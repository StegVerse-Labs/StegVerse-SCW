#!/usr/bin/env python3
"""Import timestamped glucose meter or CGM records with provenance and unit preservation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable

PARTITIONS = {"calibration", "development", "validation", "challenge"}
SOURCE_TYPES = {"glucose-meter", "cgm"}
OUTPUT_LABELS = {"measured", "reference-measured"}
MMOL_TO_MGDL = 18.0182


def source_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_time(value: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("measurement timestamp is required")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("measurement timestamp must include a UTC offset or Z")
    return parsed.isoformat()


def normalize_unit(value: object, unit: str) -> tuple[float, float, str]:
    reading = float(value)
    if not math.isfinite(reading) or reading < 0:
        raise ValueError("glucose value must be finite and non-negative")
    canonical = unit.strip().lower().replace(" ", "")
    if canonical in {"mg/dl", "mgdl"}:
        return reading, reading, "mg/dL"
    if canonical in {"mmol/l", "mmoll"}:
        return reading, reading * MMOL_TO_MGDL, "mmol/L"
    raise ValueError(f"unsupported glucose unit: {unit}")


def load_rows(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix in {".jsonl", ".ndjson"}:
        rows = []
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {number} must contain a JSON object")
                rows.append(value)
        return rows
    if suffix == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            value = value.get("records")
        if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
            raise ValueError("JSON input must be an array of objects or {'records': [...]}")
        return value
    raise ValueError("input must be CSV, JSON, JSONL, or NDJSON")


def import_records(
    rows: Iterable[dict],
    *,
    source_path: Path,
    source_type: str,
    partition: str,
    output_label: str,
    manufacturer: str,
    model: str,
    device_id: str,
    timestamp_field: str = "timestamp",
    value_field: str = "value",
    unit_field: str = "unit",
) -> list[dict]:
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"source_type must be one of {sorted(SOURCE_TYPES)}")
    if partition not in PARTITIONS:
        raise ValueError(f"partition must be one of {sorted(PARTITIONS)}")
    if output_label not in OUTPUT_LABELS:
        raise ValueError(f"output_label must be one of {sorted(OUTPUT_LABELS)}")
    digest = source_sha256(source_path)
    imported = []
    for index, row in enumerate(rows):
        if timestamp_field not in row or value_field not in row or unit_field not in row:
            raise ValueError(f"row {index} lacks timestamp, value, or unit")
        original_value, mg_dl, original_unit = normalize_unit(row[value_field], str(row[unit_field]))
        record = {
            "schema_version": "pom.glucose.v1",
            "glucose_id": str(uuid.uuid4()),
            "measurement_time_utc": parse_time(str(row[timestamp_field])),
            "source_type": source_type,
            "device": {
                "manufacturer": manufacturer,
                "model": model,
                "device_id": device_id,
            },
            "original": {"value": original_value, "unit": original_unit},
            "normalized": {"value": round(mg_dl, 6), "unit": "mg/dL"},
            "output_label": output_label,
            "dataset_partition": partition,
            "provenance": {
                "source_path": str(source_path),
                "source_sha256": digest,
                "source_row_index": index,
                "importer": {"name": "pom-glucose-import", "version": "1.0.0"},
            },
            "quality_flags": [],
        }
        canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        record["record_sha256"] = hashlib.sha256(canonical).hexdigest()
        imported.append(record)
    return imported


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--source-type", choices=sorted(SOURCE_TYPES), required=True)
    parser.add_argument("--partition", choices=sorted(PARTITIONS), required=True)
    parser.add_argument("--output-label", choices=sorted(OUTPUT_LABELS), default="measured")
    parser.add_argument("--manufacturer", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--device-id", default="")
    parser.add_argument("--timestamp-field", default="timestamp")
    parser.add_argument("--value-field", default="value")
    parser.add_argument("--unit-field", default="unit")
    args = parser.parse_args()

    source = Path(args.input)
    records = import_records(
        load_rows(source),
        source_path=source,
        source_type=args.source_type,
        partition=args.partition,
        output_label=args.output_label,
        manufacturer=args.manufacturer,
        model=args.model,
        device_id=args.device_id,
        timestamp_field=args.timestamp_field,
        value_field=args.value_field,
        unit_field=args.unit_field,
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    print(json.dumps({"status": "COMPLETE", "records": len(records), "output": str(destination)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
