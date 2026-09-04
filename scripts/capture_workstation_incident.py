#!/usr/bin/env python3
"""Create a canonical local workstation incident record.

This utility is intentionally local-only. It creates no external issue, publication,
credential action, vendor report, or remediation authority.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "stegverse.workstation-incident/v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return value[:48] or "incident"


def build_incident(args: argparse.Namespace) -> dict:
    now = utc_now()
    incident_id = args.incident_id or f"WGI-{slug(args.product)}-{uuid.uuid4().hex[:12]}"
    tags = sorted(set(args.tag or []))
    return {
        "schema": SCHEMA,
        "incident_id": incident_id,
        "created_at": now,
        "updated_at": now,
        "status": "OBSERVED",
        "classification": {
            "vendor": args.vendor,
            "product": args.product,
            "platform": args.platform,
            "surface": args.surface,
            "category": args.category,
            "tags": tags,
        },
        "observation": {
            "summary": args.summary,
            "observed_behavior": args.observed_behavior,
            "expected_behavior": args.expected_behavior,
            "reproduction_steps": args.reproduction_step or [],
            "environment": {},
            "attachments": args.attachment or [],
        },
        "suspected_causes": [],
        "root_cause": {"state": "UNKNOWN", "statement": None, "evidence_refs": []},
        "workaround": {
            "state": "OBSERVED_SUCCESS" if args.workaround else "NONE",
            "procedure": args.workaround,
            "evidence_refs": [],
        },
        "fix": {"state": "UNKNOWN", "version": None, "statement": None, "evidence_refs": []},
        "related_incident_ids": [],
        "provenance": {
            "capture_source": args.capture_source,
            "observer": args.observer,
            "confidence": args.confidence,
            "source_refs": args.source_ref or [],
            "public_projection_allowed": args.public_projection_allowed,
            "redactions": [],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--surface", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--observed-behavior", required=True)
    parser.add_argument("--expected-behavior")
    parser.add_argument("--vendor")
    parser.add_argument("--workaround")
    parser.add_argument("--tag", action="append")
    parser.add_argument("--reproduction-step", action="append")
    parser.add_argument("--attachment", action="append")
    parser.add_argument("--source-ref", action="append")
    parser.add_argument("--capture-source", default="workstation-command:add-this-glitch")
    parser.add_argument("--observer")
    parser.add_argument("--confidence", choices=["LOW", "MEDIUM", "HIGH"], default="HIGH")
    parser.add_argument("--incident-id")
    parser.add_argument("--public-projection-allowed", action="store_true")
    parser.add_argument("--output-dir", default="data/workstation-incidents")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    incident = build_incident(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{incident['incident_id']}.json"
    if output_path.exists():
        print(f"refusing to overwrite existing incident: {output_path}", file=sys.stderr)
        return 2
    output_path.write_text(json.dumps(incident, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
