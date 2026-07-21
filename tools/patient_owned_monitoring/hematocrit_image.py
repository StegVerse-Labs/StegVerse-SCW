#!/usr/bin/env python3
"""Measure packed-cell fraction from annotated capillary-tube image coordinates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def calculate(plasma_start: float, interface: float, packed_end: float) -> dict:
    total = packed_end - plasma_start
    packed = packed_end - interface
    if total <= 0:
        raise ValueError("packed_end must be greater than plasma_start")
    if packed < 0 or packed > total:
        raise ValueError("interface must fall between plasma_start and packed_end")
    fraction = packed / total
    return {
        "packed_length_px": packed,
        "total_blood_length_px": total,
        "hematocrit_fraction": fraction,
        "hematocrit_percent": fraction * 100.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Use coordinates measured along the capillary tube axis")
    parser.add_argument("--plasma-start", type=float, required=True)
    parser.add_argument("--interface", type=float, required=True, help="plasma/packed-cell boundary")
    parser.add_argument("--packed-end", type=float, required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--image-ref", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": "pom.hematocrit-image.v1",
        "sample_id": args.sample_id,
        "image_ref": args.image_ref,
        "coordinates_px": {
            "plasma_start": args.plasma_start,
            "interface": args.interface,
            "packed_end": args.packed_end,
        },
        "measurement": calculate(args.plasma_start, args.interface, args.packed_end),
        "output_label": "calculated",
        "algorithm": {"name": "axis-coordinate-hematocrit", "version": "0.1.0"},
    }
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
