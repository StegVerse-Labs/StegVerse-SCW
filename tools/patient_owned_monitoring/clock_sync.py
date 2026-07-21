#!/usr/bin/env python3
"""Fit and apply linear clock correction from synchronization anchors."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean
from typing import Iterable


def parse_utc(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def format_utc(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class ClockModel:
    slope_seconds_per_tick: float
    intercept_seconds: float
    residual_rmse_ms: float
    anchor_count: int

    def correct(self, monotonic_tick: int | float) -> float:
        return self.intercept_seconds + self.slope_seconds_per_tick * float(monotonic_tick)


def fit_clock(anchors: Iterable[dict]) -> ClockModel:
    rows = [(float(a["monotonic_tick"]), parse_utc(a["reference_time_utc"])) for a in anchors]
    if len(rows) < 2:
        raise ValueError("at least two clock anchors are required")
    xs, ys = zip(*rows)
    x_bar, y_bar = fmean(xs), fmean(ys)
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0:
        raise ValueError("clock anchors must contain distinct monotonic ticks")
    slope = sum((x - x_bar) * (y - y_bar) for x, y in rows) / denominator
    intercept = y_bar - slope * x_bar
    residuals = [y - (intercept + slope * x) for x, y in rows]
    rmse_ms = (fmean(r * r for r in residuals) ** 0.5) * 1000.0
    return ClockModel(slope, intercept, rmse_ms, len(rows))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("anchors", type=Path, help="JSON array of monotonic/reference time anchors")
    parser.add_argument("--ticks", type=Path, help="optional JSONL records containing monotonic_tick")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    anchors = json.loads(args.anchors.read_text(encoding="utf-8"))
    model = fit_clock(anchors)
    report = {
        "schema_version": "pom.clock-model.v1",
        "slope_seconds_per_tick": model.slope_seconds_per_tick,
        "intercept_seconds": model.intercept_seconds,
        "residual_rmse_ms": model.residual_rmse_ms,
        "anchor_count": model.anchor_count,
    }
    if args.ticks:
        corrected = []
        for line in args.ticks.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            record["wall_time_corrected_utc"] = format_utc(model.correct(record["monotonic_tick"]))
            corrected.append(record)
        report["corrected_records"] = corrected
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
