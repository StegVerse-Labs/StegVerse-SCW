#!/usr/bin/env python3
"""Generate relative hemodynamic features from synchronized beat-level ECG/PPG data."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import fmean, median

FEATURES = ("pat_ms", "ppg_amplitude", "pulse_width_ms", "heart_rate_bpm")


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numeric(rows: list[dict[str, str]], field: str) -> list[float]:
    return [float(r[field]) for r in rows if r.get(field) not in (None, "")]


def baseline(rows: list[dict[str, str]]) -> dict[str, float]:
    result = {}
    for field in FEATURES:
        values = numeric(rows, field)
        if values:
            result[field] = median(values)
    return result


def derive(rows: list[dict[str, str]], base: dict[str, float]) -> list[dict]:
    derived = []
    for row in rows:
        out = {"time_utc": row["time_utc"]}
        deltas = []
        for field in FEATURES:
            if row.get(field) in (None, "") or field not in base:
                continue
            value = float(row[field])
            delta = value - base[field]
            pct = (delta / base[field] * 100.0) if base[field] else None
            out[field] = value
            out[f"{field}_delta"] = delta
            out[f"{field}_pct"] = pct
            if pct is not None:
                deltas.append(abs(pct))
        out["relative_change_index"] = fmean(deltas) if deltas else None
        derived.append(out)
    return derived


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="beat-level CSV")
    parser.add_argument("--baseline-count", type=int, default=60)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = load(args.input)
    if not rows:
        raise SystemExit("no rows")
    base_rows = rows[: max(1, min(args.baseline_count, len(rows)))]
    base = baseline(base_rows)
    result = {
        "schema_version": "pom.hemodynamic-features.v1",
        "algorithm": {"name": "relative-hemodynamic-features", "version": "0.1.0"},
        "baseline": base,
        "baseline_sample_count": len(base_rows),
        "features": derive(rows, base),
        "output_label": "calculated",
    }
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output: args.output.write_text(encoded + "\n", encoding="utf-8")
    else: print(encoded)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
