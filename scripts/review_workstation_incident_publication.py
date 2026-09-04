#!/usr/bin/env python3
"""Fail-closed publication/redaction preflight for workstation incident records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SENSITIVE_ENVIRONMENT_KEYS = {
    "account_id",
    "email",
    "hostname",
    "ip",
    "ip_address",
    "location",
    "phone",
    "serial",
    "serial_number",
    "ssid",
    "user_id",
    "username",
}


def review(record: dict) -> dict:
    blockers: list[str] = []
    provenance = record.get("provenance", {})
    if not provenance.get("public_projection_allowed", False):
        blockers.append("PUBLIC_PROJECTION_NOT_AUTHORIZED")

    environment = record.get("observation", {}).get("environment", {})
    redactions = set(provenance.get("redactions") or [])
    for key, value in environment.items():
        if key.lower() in SENSITIVE_ENVIRONMENT_KEYS and value not in (None, ""):
            marker = f"observation.environment.{key}"
            if marker not in redactions:
                blockers.append(f"UNREDACTED_SENSITIVE_FIELD:{marker}")

    observer = provenance.get("observer")
    if observer not in (None, "") and "provenance.observer" not in redactions:
        blockers.append("UNREDACTED_SENSITIVE_FIELD:provenance.observer")

    return {
        "schema": "stegverse.workstation-incident-publication-review/v1",
        "incident_id": record.get("incident_id"),
        "decision": "PASS" if not blockers else "DENY",
        "blockers": sorted(set(blockers)),
        "authority_effect": False,
        "publication_effect": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("incident")
    args = parser.parse_args()

    path = Path(args.incident)
    record = json.loads(path.read_text(encoding="utf-8"))
    result = review(record)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["decision"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
