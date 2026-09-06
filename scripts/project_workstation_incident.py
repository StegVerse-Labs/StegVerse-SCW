#!/usr/bin/env python3
"""Render bounded user, SME, or machine projections of a local incident.

No external publication is performed. Public projection is fail-closed unless the
incident explicitly allows it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def user_projection(record: dict) -> dict:
    return {
        "incident_id": record["incident_id"],
        "status": record["status"],
        "product": record["classification"]["product"],
        "platform": record["classification"]["platform"],
        "surface": record["classification"]["surface"],
        "summary": record["observation"]["summary"],
        "observed_behavior": record["observation"]["observed_behavior"],
        "workaround": record["workaround"],
        "fix": record["fix"],
        "root_cause_state": record["root_cause"]["state"],
    }


def sme_projection(record: dict) -> dict:
    return {
        **user_projection(record),
        "classification": record["classification"],
        "reproduction_steps": record["observation"].get("reproduction_steps", []),
        "environment": record["observation"].get("environment", {}),
        "suspected_causes": record.get("suspected_causes", []),
        "root_cause": record["root_cause"],
        "related_incident_ids": record.get("related_incident_ids", []),
        "provenance": record["provenance"],
    }


def machine_projection(record: dict) -> dict:
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("incident")
    parser.add_argument(
        "--view",
        choices=["user", "sme", "machine"],
        default="user",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="enforce public-projection authorization",
    )
    args = parser.parse_args()

    record = json.loads(Path(args.incident).read_text(encoding="utf-8"))
    allowed = record.get("provenance", {}).get("public_projection_allowed", False)
    if args.public and not allowed:
        print("public projection denied by incident provenance", file=sys.stderr)
        return 3

    if args.view == "user":
        projected = user_projection(record)
    elif args.view == "sme":
        projected = sme_projection(record)
    else:
        projected = machine_projection(record)

    print(json.dumps(projected, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
