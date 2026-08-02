#!/usr/bin/env python3
"""Evaluate detected collapse-candidate events against timestamped reference events.

The evaluator is deterministic and transparent.  It reports event-level sensitivity,
false positives, false-positive rate per monitored hour, onset delay, duration overlap,
and time coverage.  Inputs are JSON or JSONL arrays containing start/end timestamps.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def parse_time(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def load_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("JSON input must contain an array")
        return data
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def normalize(records: Iterable[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        start_value = record.get("start_time_utc") or record.get("start")
        end_value = record.get("end_time_utc") or record.get("end")
        if not start_value or not end_value:
            raise ValueError(f"{label}[{index}] requires start_time_utc and end_time_utc")
        start = parse_time(str(start_value))
        end = parse_time(str(end_value))
        if end <= start:
            raise ValueError(f"{label}[{index}] end must be after start")
        normalized.append({"index": index, "start": start, "end": end, "raw": record})
    normalized.sort(key=lambda item: (item["start"], item["end"]))
    return normalized


def overlap_seconds(left: dict[str, Any], right: dict[str, Any]) -> float:
    return max(0.0, min(left["end"], right["end"]) - max(left["start"], right["start"]))


def union_duration(intervals: Iterable[tuple[float, float]]) -> float:
    ordered = sorted(intervals)
    if not ordered:
        return 0.0
    total = 0.0
    current_start, current_end = ordered[0]
    for start, end in ordered[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    return total + current_end - current_start


def evaluate(
    reference_records: Iterable[dict[str, Any]],
    detected_records: Iterable[dict[str, Any]],
    monitoring_start_utc: str | None = None,
    monitoring_end_utc: str | None = None,
    onset_tolerance_seconds: float = 30.0,
) -> dict[str, Any]:
    references = normalize(reference_records, "reference")
    detections = normalize(detected_records, "detected")

    matches: list[dict[str, Any]] = []
    used_detections: set[int] = set()
    for reference in references:
        candidates = []
        for detection in detections:
            if detection["index"] in used_detections:
                continue
            overlap = overlap_seconds(reference, detection)
            onset_distance = abs(detection["start"] - reference["start"])
            if overlap > 0 or onset_distance <= onset_tolerance_seconds:
                candidates.append((overlap, -onset_distance, detection))
        if not candidates:
            continue
        _, _, detection = max(candidates, key=lambda item: (item[0], item[1]))
        used_detections.add(detection["index"])
        overlap = overlap_seconds(reference, detection)
        reference_duration = reference["end"] - reference["start"]
        matches.append(
            {
                "reference_index": reference["index"],
                "detected_index": detection["index"],
                "onset_delay_seconds": detection["start"] - reference["start"],
                "overlap_seconds": overlap,
                "reference_overlap_fraction": overlap / reference_duration,
            }
        )

    true_positives = len(matches)
    false_negatives = len(references) - true_positives
    false_positives = len(detections) - len(used_detections)
    sensitivity = true_positives / len(references) if references else None

    all_intervals = [(item["start"], item["end"]) for item in references + detections]
    if monitoring_start_utc is not None and monitoring_end_utc is not None:
        monitoring_start = parse_time(monitoring_start_utc)
        monitoring_end = parse_time(monitoring_end_utc)
    elif all_intervals:
        monitoring_start = min(start for start, _ in all_intervals)
        monitoring_end = max(end for _, end in all_intervals)
    else:
        monitoring_start = monitoring_end = 0.0
    if monitoring_end < monitoring_start:
        raise ValueError("monitoring_end_utc must not precede monitoring_start_utc")

    monitored_seconds = monitoring_end - monitoring_start
    monitored_hours = monitored_seconds / 3600.0
    false_positive_rate_per_hour = false_positives / monitored_hours if monitored_hours > 0 else None
    covered_seconds = union_duration(
        (max(start, monitoring_start), min(end, monitoring_end))
        for start, end in all_intervals
        if end > monitoring_start and start < monitoring_end
    )
    coverage_fraction = covered_seconds / monitored_seconds if monitored_seconds > 0 else None

    delays = [match["onset_delay_seconds"] for match in matches]
    absolute_delays = [abs(value) for value in delays]
    overlap_fractions = [match["reference_overlap_fraction"] for match in matches]

    return {
        "schema_version": "pom.collapse-event-evaluation.v1",
        "status": "COMPLETE",
        "counts": {
            "reference_events": len(references),
            "detected_events": len(detections),
            "true_positives": true_positives,
            "false_negatives": false_negatives,
            "false_positives": false_positives,
        },
        "metrics": {
            "sensitivity": sensitivity,
            "false_positive_rate_per_monitored_hour": false_positive_rate_per_hour,
            "mean_onset_delay_seconds": sum(delays) / len(delays) if delays else None,
            "mean_absolute_onset_delay_seconds": sum(absolute_delays) / len(absolute_delays) if absolute_delays else None,
            "maximum_absolute_onset_delay_seconds": max(absolute_delays) if absolute_delays else None,
            "mean_reference_overlap_fraction": sum(overlap_fractions) / len(overlap_fractions) if overlap_fractions else None,
            "coverage_fraction": coverage_fraction,
            "monitored_seconds": monitored_seconds,
        },
        "configuration": {"onset_tolerance_seconds": onset_tolerance_seconds},
        "matches": matches,
        "unmatched_reference_indices": sorted(set(range(len(references))) - {m["reference_index"] for m in matches}),
        "unmatched_detected_indices": sorted(set(range(len(detections))) - used_detections),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("references")
    parser.add_argument("detections")
    parser.add_argument("output")
    parser.add_argument("--monitoring-start")
    parser.add_argument("--monitoring-end")
    parser.add_argument("--onset-tolerance-seconds", type=float, default=30.0)
    args = parser.parse_args()

    report = evaluate(
        load_records(args.references),
        load_records(args.detections),
        args.monitoring_start,
        args.monitoring_end,
        args.onset_tolerance_seconds,
    )
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": args.output, **report["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
