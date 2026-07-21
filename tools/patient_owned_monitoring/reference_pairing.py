#!/usr/bin/env python3
"""Pair POM estimates with reference measurements and compute validation metrics.

Inputs are JSON Lines files following docs/patient-owned-monitoring/DATA_SCHEMA.md.
The tool never mutates source records and emits pairing records plus a metrics report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def parse_time(value: str) -> datetime:
    value = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def canonical_sha256(record: dict[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return records


def extract_reference_value(record: dict[str, Any], name: str) -> float | None:
    for value in record.get("values", []):
        if value.get("name") == name and value.get("value") is not None:
            return float(value["value"])
    return None


@dataclass(frozen=True)
class Pair:
    reference: dict[str, Any]
    estimate: dict[str, Any]
    time_delta_seconds: float


def pair_records(
    references: Iterable[dict[str, Any]],
    estimates: Iterable[dict[str, Any]],
    reference_name: str,
    estimate_type: str,
    tolerance_seconds: float,
) -> list[Pair]:
    candidates = [e for e in estimates if e.get("estimate_type") == estimate_type]
    output: list[Pair] = []

    for reference in references:
        if extract_reference_value(reference, reference_name) is None:
            continue
        reference_time = parse_time(reference["measurement_time_utc"])
        best: tuple[float, dict[str, Any]] | None = None
        for estimate in candidates:
            estimate_time = parse_time(estimate["time_utc"])
            delta = abs((estimate_time - reference_time).total_seconds())
            if delta <= tolerance_seconds and (best is None or delta < best[0]):
                best = (delta, estimate)
        if best is not None:
            output.append(Pair(reference=reference, estimate=best[1], time_delta_seconds=best[0]))
    return output


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom = math.sqrt(sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys))
    return numerator / denom if denom else None


def compute_metrics(pairs: list[Pair], reference_name: str) -> dict[str, Any]:
    refs = [float(extract_reference_value(pair.reference, reference_name)) for pair in pairs]
    estimates = [float(pair.estimate["value"]) for pair in pairs]
    errors = [estimate - reference for estimate, reference in zip(estimates, refs)]

    if not errors:
        return {
            "count": 0,
            "bias": None,
            "mae": None,
            "rmse": None,
            "correlation": None,
            "bland_altman_lower": None,
            "bland_altman_upper": None,
        }

    bias = statistics.fmean(errors)
    standard_deviation = statistics.stdev(errors) if len(errors) > 1 else 0.0
    return {
        "count": len(errors),
        "bias": bias,
        "mae": statistics.fmean(abs(error) for error in errors),
        "rmse": math.sqrt(statistics.fmean(error**2 for error in errors)),
        "correlation": pearson(refs, estimates),
        "bland_altman_lower": bias - 1.96 * standard_deviation,
        "bland_altman_upper": bias + 1.96 * standard_deviation,
        "max_absolute_error": max(abs(error) for error in errors),
        "mean_pairing_delta_seconds": statistics.fmean(pair.time_delta_seconds for pair in pairs),
    }


def build_pairing_record(pair: Pair, partition: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": "pom.pairing.v1",
        "pairing_id": str(uuid.uuid4()),
        "reference_id": pair.reference["reference_id"],
        "source_session_ids": [pair.estimate.get("session_id", "unknown")],
        "window_start_utc": pair.estimate["time_utc"],
        "window_end_utc": pair.reference["measurement_time_utc"],
        "pairing_method": "nearest-estimate-within-tolerance",
        "dataset_partition": partition,
        "quality_decision": "include",
        "quality_reasons": [],
        "operator": "reference_pairing.py",
        "time_delta_seconds": pair.time_delta_seconds,
    }
    record["pairing_sha256"] = canonical_sha256(record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--estimates", type=Path, required=True)
    parser.add_argument("--reference-name", required=True)
    parser.add_argument("--estimate-type", required=True)
    parser.add_argument("--tolerance-seconds", type=float, default=60.0)
    parser.add_argument("--partition", choices=["calibration", "development", "validation", "challenge"], default="validation")
    parser.add_argument("--pairings-out", type=Path, required=True)
    parser.add_argument("--metrics-out", type=Path, required=True)
    args = parser.parse_args()

    try:
        references = load_jsonl(args.references)
        estimates = load_jsonl(args.estimates)
        pairs = pair_records(
            references,
            estimates,
            args.reference_name,
            args.estimate_type,
            args.tolerance_seconds,
        )
        pairings = [build_pairing_record(pair, args.partition) for pair in pairs]
        args.pairings_out.parent.mkdir(parents=True, exist_ok=True)
        with args.pairings_out.open("w", encoding="utf-8") as handle:
            for record in pairings:
                handle.write(json.dumps(record, sort_keys=True) + "\n")

        metrics = {
            "schema_version": "pom.validation-report.v1",
            "reference_name": args.reference_name,
            "estimate_type": args.estimate_type,
            "partition": args.partition,
            "tolerance_seconds": args.tolerance_seconds,
            "metrics": compute_metrics(pairs, args.reference_name),
            "source_hashes": {
                "references_sha256": hashlib.sha256(args.references.read_bytes()).hexdigest(),
                "estimates_sha256": hashlib.sha256(args.estimates.read_bytes()).hexdigest(),
            },
        }
        metrics["report_sha256"] = canonical_sha256(metrics)
        args.metrics_out.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
