#!/usr/bin/env python3
"""Human-friendly `add this glitch` command surface for local incident capture.

This is a workstation command adapter only. It delegates to the canonical local
capture utility and does not publish, report to vendors, mutate external repos,
or claim a fix.
"""

from __future__ import annotations

import argparse
from types import SimpleNamespace

from capture_workstation_incident import build_incident


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary")
    parser.add_argument("--product", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--surface", required=True)
    parser.add_argument("--category", default="glitch")
    parser.add_argument("--observed-behavior")
    parser.add_argument("--expected-behavior")
    parser.add_argument("--vendor")
    parser.add_argument("--workaround")
    parser.add_argument("--tag", action="append")
    parser.add_argument("--source-ref", action="append")
    parser.add_argument("--observer")
    parser.add_argument("--public-projection-allowed", action="store_true")
    return parser.parse_args()


def main() -> int:
    import json
    from pathlib import Path

    args = parse_args()
    incident_args = SimpleNamespace(
        product=args.product,
        platform=args.platform,
        surface=args.surface,
        category=args.category,
        summary=args.summary,
        observed_behavior=args.observed_behavior or args.summary,
        expected_behavior=args.expected_behavior,
        vendor=args.vendor,
        workaround=args.workaround,
        tag=args.tag,
        reproduction_step=None,
        attachment=None,
        source_ref=args.source_ref,
        capture_source="workstation-command:add-this-glitch",
        observer=args.observer,
        confidence="HIGH",
        incident_id=None,
        public_projection_allowed=args.public_projection_allowed,
    )
    incident = build_incident(incident_args)
    output_dir = Path("data/workstation-incidents")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{incident['incident_id']}.json"
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing incident: {path}")
    path.write_text(json.dumps(incident, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
