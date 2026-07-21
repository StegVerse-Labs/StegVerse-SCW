#!/usr/bin/env python3
"""Validate patient-owned-monitoring JSON or JSONL records using stdlib only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

REQUIRED: dict[str, tuple[str, ...]] = {
    "pom.session.v1": ("session_id", "device_id", "device_type", "start_time_utc"),
    "pom.signal-frame.v1": ("session_id", "stream_id", "sequence", "sample_rate_hz", "sample_count", "unit"),
    "pom.event.v1": ("event_id", "session_id", "event_type", "start_time_utc", "timestamp_source"),
    "pom.reference.v1": ("reference_id", "reference_type", "measurement_time_utc", "values"),
    "pom.pairing.v1": ("pairing_id", "reference_id", "source_session_ids", "window_start_utc", "window_end_utc", "dataset_partition"),
    "pom.feature.v1": ("feature_id", "session_id", "feature_name", "start_time_utc", "end_time_utc", "value", "unit", "output_label", "algorithm"),
    "pom.estimate.v1": ("estimate_id", "estimate_type", "time_utc", "value", "unit", "output_label", "validation_class", "model"),
    "pom.sample.v1": ("sample_id", "sample_type", "collection_start_utc", "collection_end_utc"),
    "pom.cbc-comparison.v1": ("comparison_id", "sample_id", "home_results", "laboratory_reference_id", "analysis_version"),
}

ALLOWED_LABELS = {
    "measured", "reference_measured", "calculated", "estimated",
    "experimentally_inferred", "validated_for_personal_trend", "validated_against_reference",
}


def load_records(path: Path) -> Iterable[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        for line_no, line in enumerate(text.splitlines(), 1):
            if line.strip():
                record = json.loads(line)
                record["__line__"] = line_no
                yield record
    else:
        value = json.loads(text)
        if isinstance(value, list):
            yield from value
        else:
            yield value


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema = record.get("schema_version")
    if schema not in REQUIRED:
        return [f"unsupported schema_version: {schema!r}"]
    for key in REQUIRED[schema]:
        if key not in record or record[key] is None:
            errors.append(f"missing required field: {key}")
    if "output_label" in record and record["output_label"] not in ALLOWED_LABELS:
        errors.append(f"invalid output_label: {record['output_label']!r}")
    if schema == "pom.reference.v1" and not isinstance(record.get("values"), list):
        errors.append("values must be a list")
    if schema == "pom.signal-frame.v1":
        if record.get("sample_rate_hz", 0) <= 0:
            errors.append("sample_rate_hz must be positive")
        if record.get("sample_count", 0) < 0:
            errors.append("sample_count must be nonnegative")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    failures = 0
    for path in args.paths:
        for index, record in enumerate(load_records(path), 1):
            line = record.pop("__line__", None)
            errors = validate(record)
            if errors:
                failures += 1
                where = f"line {line}" if line else f"record {index}"
                print(f"{path}:{where}: " + "; ".join(errors))
    if failures:
        print(f"INVALID records={failures}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
