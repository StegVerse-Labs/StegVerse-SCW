#!/usr/bin/env python3
"""Record an explicit, append-only correlation decision for two workstation incidents."""

from __future__ import annotations

import argparse
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "stegverse.workstation-incident-correlation-decision/v1"


def load_incident(path: Path) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("schema") != "stegverse.workstation-incident/v1":
        raise ValueError(f"unexpected incident schema: {path}")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left")
    parser.add_argument("right")
    parser.add_argument("--score", type=float, required=True)
    parser.add_argument(
        "--decision",
        choices=["RELATED", "NOT_RELATED", "UNRESOLVED"],
        required=True,
    )
    parser.add_argument(
        "--relationship",
        choices=[
            "SAME_PRESENTATION",
            "SAME_COMPONENT",
            "SAME_ROOT_CAUSE",
            "POSSIBLY_RELATED",
            "NONE",
            "UNKNOWN",
        ],
        default="UNKNOWN",
    )
    parser.add_argument("--reason", required=True)
    parser.add_argument("--actor-type", choices=["USER", "SME", "SYSTEM"], required=True)
    parser.add_argument("--actor-id", required=True)
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument(
        "--output-dir",
        default="data/workstation-incident-correlation-decisions",
    )
    args = parser.parse_args()

    if not 0 <= args.score <= 1:
        parser.error("--score must be between 0 and 1")

    left = load_incident(Path(args.left))
    right = load_incident(Path(args.right))
    if left["incident_id"] == right["incident_id"]:
        parser.error("cannot correlate an incident with itself")
    if args.relationship == "SAME_ROOT_CAUSE":
        if args.decision != "RELATED":
            parser.error("SAME_ROOT_CAUSE requires decision RELATED")
        if not args.evidence_ref:
            parser.error("SAME_ROOT_CAUSE requires at least one --evidence-ref")

    now = datetime.now(timezone.utc)
    decision_id = f"WGCD-{now:%Y%m%dT%H%M%SZ}-{secrets.token_hex(4)}"
    record = {
        "schema": SCHEMA,
        "decision_id": decision_id,
        "left_incident_id": left["incident_id"],
        "right_incident_id": right["incident_id"],
        "candidate_score": args.score,
        "decision": args.decision,
        "relationship": args.relationship,
        "reason": args.reason,
        "decided_at": now.isoformat().replace("+00:00", "Z"),
        "actor": {
            "type": args.actor_type,
            "id": args.actor_id,
        },
        "evidence_refs": sorted(set(args.evidence_ref)),
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{decision_id}.json"
    output_path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
