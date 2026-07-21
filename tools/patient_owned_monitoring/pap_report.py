#!/usr/bin/env python3
"""Generate a raw-linked nightly PAP evidence report from synchronized CSV channels."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from statistics import fmean


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def values(rows: list[dict[str, str]], field: str) -> list[float]:
    return [float(r[field]) for r in rows if r.get(field) not in (None, "")]


def summary(rows: list[dict[str, str]], field: str) -> dict:
    data = values(rows, field)
    return {} if not data else {"count": len(data), "min": min(data), "max": max(data), "mean": fmean(data)}


def threshold_events(rows: list[dict[str, str]], field: str, predicate, event_type: str) -> list[dict]:
    events = []
    active = None
    for row in rows:
        value = row.get(field)
        hit = value not in (None, "") and predicate(float(value))
        if hit and active is None:
            active = {"event_type": event_type, "start_time_utc": row["time_utc"], "minimum": float(value)}
        elif hit and active is not None:
            active["minimum"] = min(active["minimum"], float(value))
        elif not hit and active is not None:
            active["end_time_utc"] = row["time_utc"]
            events.append(active)
            active = None
    if active is not None:
        active["end_time_utc"] = rows[-1]["time_utc"]
        events.append(active)
    return events


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="synchronized nightly CSV")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = load(args.input)
    if not rows:
        raise SystemExit("no rows")
    awakenings = [r for r in rows if str(r.get("awakening_marker", "")).lower() in {"1", "true", "yes"}]
    report = {
        "schema_version": "pom.pap-nightly-report.v1",
        "start_time_utc": rows[0]["time_utc"],
        "end_time_utc": rows[-1]["time_utc"],
        "source": {"path": str(args.input), "sha256": sha256(args.input)},
        "summaries": {
            "spo2_pct": summary(rows, "spo2_pct"),
            "pulse_bpm": summary(rows, "pulse_bpm"),
            "mask_pressure_cmh2o": summary(rows, "mask_pressure_cmh2o"),
            "mask_humidity_rh": summary(rows, "mask_humidity_rh"),
            "room_humidity_rh": summary(rows, "room_humidity_rh"),
            "respiration_bpm": summary(rows, "respiration_bpm"),
        },
        "events": threshold_events(rows, "spo2_pct", lambda x: x < 90.0, "spo2-below-90")
                  + threshold_events(rows, "mask_humidity_rh", lambda x: x < 35.0, "mask-humidity-below-35"),
        "awakening_markers": [r["time_utc"] for r in awakenings],
        "raw_rows": len(rows),
        "output_label": "calculated",
    }
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output: args.output.write_text(encoded + "\n", encoding="utf-8")
    else: print(encoded)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
