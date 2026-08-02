#!/usr/bin/env python3
"""Extract transparent ECG R peaks, PPG feet, heart rate, and pulse-arrival time.

Inputs may be CSV or append-only JSON Lines produced by simulated or physical
recorders. The parser preserves the raw record order and rejects unsupported
record shapes instead of silently coercing them.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def load(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if source.suffix.lower() in {".jsonl", ".ndjson"}:
        rows: list[dict[str, Any]] = []
        with source.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError(f"line {line_number}: expected JSON object")
                rows.append(record)
        return rows
    with source.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def timestamp_seconds(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def local_max(values: list[float], index: int, width: int = 2) -> bool:
    return all(
        values[index] >= values[other]
        for other in range(max(0, index - width), min(len(values), index + width + 1))
    )


def extract(
    rows: Iterable[dict[str, Any]],
    ecg_key: str = "ecg_mv",
    ppg_key: str = "ppg_ir",
    time_key: str = "time_utc",
) -> list[dict[str, Any]]:
    materialized = list(rows)
    if len(materialized) < 5:
        return []
    required = {ecg_key, ppg_key, time_key}
    for index, row in enumerate(materialized):
        missing = required.difference(row)
        if missing:
            raise ValueError(f"row {index}: missing fields {sorted(missing)}")

    times = [timestamp_seconds(str(row[time_key])) for row in materialized]
    ecg = [float(row[ecg_key]) for row in materialized]
    ppg = [float(row[ppg_key]) for row in materialized]
    sample_period = statistics.median(
        later - earlier for earlier, later in zip(times, times[1:]) if later > earlier
    )
    if sample_period <= 0:
        raise ValueError("timestamps must increase")

    ecg_baseline = statistics.median(ecg)
    threshold = ecg_baseline + 0.45 * (max(ecg) - ecg_baseline)
    refractory_samples = max(1, int(round(0.25 / sample_period)))
    candidates = [
        index
        for index in range(2, len(ecg) - 2)
        if ecg[index] >= threshold and local_max(ecg, index)
    ]
    r_peaks: list[int] = []
    for candidate in candidates:
        if not r_peaks or candidate - r_peaks[-1] >= refractory_samples:
            r_peaks.append(candidate)
        elif ecg[candidate] > ecg[r_peaks[-1]]:
            r_peaks[-1] = candidate

    beats: list[dict[str, Any]] = []
    maximum_search_samples = max(2, int(round(1.2 / sample_period)))
    for beat_number, r_index in enumerate(r_peaks):
        next_r = r_peaks[beat_number + 1] if beat_number + 1 < len(r_peaks) else len(ppg)
        end = min(next_r, r_index + maximum_search_samples, len(ppg))
        if end <= r_index + 2:
            continue
        segment = ppg[r_index:end]
        foot_index = r_index + min(range(len(segment)), key=segment.__getitem__)
        pat_ms = (times[foot_index] - times[r_index]) * 1000.0
        rr_seconds = times[r_index] - times[r_peaks[beat_number - 1]] if beat_number else None
        beats.append(
            {
                "r_index": r_index,
                "ppg_foot_index": foot_index,
                "r_time_utc": materialized[r_index][time_key],
                "ppg_foot_time_utc": materialized[foot_index][time_key],
                "pulse_arrival_time_ms": pat_ms,
                "heart_rate_bpm": 60.0 / rr_seconds if rr_seconds and rr_seconds > 0 else None,
            }
        )
    return beats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", help="CSV or JSONL acquisition records")
    parser.add_argument("output_jsonl")
    args = parser.parse_args()
    beats = extract(load(args.input_path))
    with open(args.output_jsonl, "w", encoding="utf-8") as handle:
        for beat in beats:
            handle.write(json.dumps({"schema_version": "pom.beat.v1", **beat}, separators=(",", ":")) + "\n")
    print(json.dumps({"beats": len(beats), "output": args.output_jsonl}))


if __name__ == "__main__":
    main()
