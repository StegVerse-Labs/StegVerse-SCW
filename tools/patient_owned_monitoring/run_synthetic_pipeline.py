#!/usr/bin/env python3
"""Run the deterministic patient-owned monitoring software pipeline end to end."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from simulated_acquisition import generate, sha
from waveform_features import extract


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(output_dir: Path, duration: int, rate: int, heart_rate: float, seed: int) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    acquisition_path = output_dir / "synthetic_acquisition.jsonl"
    beats_path = output_dir / "beats.jsonl"
    summary_path = output_dir / "pipeline_receipt.json"

    session_id, rows = generate(duration, rate, heart_rate, seed)
    with acquisition_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            record = {"schema_version": "pom.synthetic-sample.v1", **row}
            record["record_sha256"] = sha(record)
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")

    beats = extract(rows)
    with beats_path.open("w", encoding="utf-8") as handle:
        for beat in beats:
            handle.write(json.dumps({"schema_version": "pom.beat.v1", **beat}, separators=(",", ":")) + "\n")

    valid_pat = [beat["pulse_arrival_time_ms"] for beat in beats if beat["pulse_arrival_time_ms"] >= 0]
    valid_hr = [beat["heart_rate_bpm"] for beat in beats if beat["heart_rate_bpm"] is not None]
    receipt = {
        "schema_version": "pom.pipeline-receipt.v1",
        "session_id": session_id,
        "inputs": {
            "duration_seconds": duration,
            "sample_rate_hz": rate,
            "heart_rate_bpm": heart_rate,
            "seed": seed,
        },
        "outputs": {
            "sample_count": len(rows),
            "beat_count": len(beats),
            "median_heart_rate_bpm": sorted(valid_hr)[len(valid_hr) // 2] if valid_hr else None,
            "median_pulse_arrival_time_ms": sorted(valid_pat)[len(valid_pat) // 2] if valid_pat else None,
            "acquisition_path": acquisition_path.name,
            "beats_path": beats_path.name,
        },
        "integrity": {
            "acquisition_sha256": file_sha256(acquisition_path),
            "beats_sha256": file_sha256(beats_path),
        },
        "status": "COMPLETE" if beats else "FAILED",
        "next_executable_task": "PAIR_WITH_REFERENCE_DEVICE" if beats else "REVIEW_WAVEFORM_EXTRACTION",
    }
    receipt["receipt_sha256"] = sha(receipt)
    summary_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--rate", type=int, default=100)
    parser.add_argument("--heart-rate", type=float, default=72.0)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    receipt = run(Path(args.output_dir), args.duration, args.rate, args.heart_rate, args.seed)
    print(json.dumps(receipt, separators=(",", ":")))
    if receipt["status"] != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
