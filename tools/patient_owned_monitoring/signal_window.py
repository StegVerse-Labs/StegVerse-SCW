#!/usr/bin/env python3
"""Extract timestamped signal windows and compute transparent quality scores."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from statistics import fmean, pstdev


def ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def quality(rows: list[dict[str, str]], value_field: str, expected_rate_hz: float | None) -> dict:
    values = [float(r[value_field]) for r in rows if r.get(value_field) not in (None, "")]
    timestamps = [ts(r["time_utc"]) for r in rows]
    duration = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0.0
    expected = max(1, round(duration * expected_rate_hz) + 1) if expected_rate_hz else len(rows)
    coverage = min(1.0, len(rows) / expected) if expected else 0.0
    flatline = len(values) > 2 and pstdev(values) == 0
    clipping = sum(1 for r in rows if str(r.get("clipped", "")).lower() in {"1", "true", "yes"})
    motion = fmean(float(r.get("motion", 0) or 0) for r in rows) if rows else 0.0
    score = max(0.0, coverage - (0.35 if flatline else 0.0) - min(0.35, clipping / max(1, len(rows))) - min(0.30, motion))
    flags = []
    if coverage < 0.9: flags.append("low-coverage")
    if flatline: flags.append("flatline")
    if clipping: flags.append("clipping")
    if motion > 0.4: flags.append("high-motion")
    return {"score": round(score, 6), "coverage": round(coverage, 6), "flags": flags, "sample_count": len(rows)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--value-field", default="value")
    parser.add_argument("--expected-rate-hz", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    start, end = ts(args.start), ts(args.end)
    rows = [r for r in load_csv(args.input) if start <= ts(r["time_utc"]) <= end]
    result = {"schema_version": "pom.signal-window.v1", "start_time_utc": args.start, "end_time_utc": args.end,
              "rows": rows, "quality": quality(rows, args.value_field, args.expected_rate_hz)}
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output: args.output.write_text(encoded + "\n", encoding="utf-8")
    else: print(encoded)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
