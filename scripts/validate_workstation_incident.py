#!/usr/bin/env python3
"""Fail-closed semantic validator for workstation incident records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INCIDENT_SCHEMA = "stegverse.workstation-incident/v1"
VALID_STATUS = {"OBSERVED", "CORRELATED", "REPRODUCED", "ROOT_CAUSED", "FIX_AVAILABLE", "FIX_VERIFIED", "SUPERSEDED", "CLOSED"}


def fail(message: str) -> None:
    raise ValueError(message)


def validate(record: dict) -> None:
    if record.get("schema") != INCIDENT_SCHEMA:
        fail("unexpected incident schema")
    if record.get("status") not in VALID_STATUS:
        fail("invalid status")
    if not str(record.get("incident_id", "")).startswith("WGI-"):
        fail("invalid incident_id")

    for key in ("classification", "observation", "root_cause", "workaround", "fix", "provenance"):
        if not isinstance(record.get(key), dict):
            fail(f"missing object: {key}")

    if record["root_cause"].get("state") not in {"UNKNOWN", "SUSPECTED", "CONFIRMED"}:
        fail("invalid root cause state")
    if record["workaround"].get("state") not in {"NONE", "PROPOSED", "OBSERVED_SUCCESS", "REPRODUCED_SUCCESS", "FAILED"}:
        fail("invalid workaround state")
    if record["fix"].get("state") not in {"UNKNOWN", "AVAILABLE_UNVERIFIED", "VERIFIED", "REGRESSED"}:
        fail("invalid fix state")

    if record["status"] == "ROOT_CAUSED" and record["root_cause"].get("state") != "CONFIRMED":
        fail("ROOT_CAUSED requires confirmed root cause")
    if record["status"] == "FIX_AVAILABLE" and record["fix"].get("state") not in {"AVAILABLE_UNVERIFIED", "VERIFIED"}:
        fail("FIX_AVAILABLE requires an available fix")
    if record["status"] == "FIX_VERIFIED" and record["fix"].get("state") != "VERIFIED":
        fail("FIX_VERIFIED requires verified fix evidence state")
    if record["workaround"].get("state") in {"OBSERVED_SUCCESS", "REPRODUCED_SUCCESS"} and record["root_cause"].get("state") == "CONFIRMED":
        # Legal, but only when root-cause evidence is independently present.
        if not record["root_cause"].get("evidence_refs"):
            fail("confirmed root cause requires independent evidence refs")

    if record["provenance"].get("confidence") not in {"LOW", "MEDIUM", "HIGH"}:
        fail("invalid provenance confidence")
    if not isinstance(record["provenance"].get("public_projection_allowed"), bool):
        fail("public_projection_allowed must be boolean")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("incident", nargs="+")
    args = parser.parse_args()
    failed = False
    for value in args.incident:
        path = Path(value)
        try:
            validate(json.loads(path.read_text(encoding="utf-8")))
            print(f"PASS {path}")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            failed = True
            print(f"FAIL {path}: {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
