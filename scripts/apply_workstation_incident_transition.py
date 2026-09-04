#!/usr/bin/env python3
"""Apply a validated local incident status transition and emit an append-only receipt."""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from validate_workstation_incident import validate

ALLOWED = {
    "OBSERVED": {"CORRELATED", "REPRODUCED", "CLOSED"},
    "CORRELATED": {"REPRODUCED", "ROOT_CAUSED", "CLOSED"},
    "REPRODUCED": {"ROOT_CAUSED", "FIX_AVAILABLE", "CLOSED"},
    "ROOT_CAUSED": {"FIX_AVAILABLE", "CLOSED"},
    "FIX_AVAILABLE": {"FIX_VERIFIED", "REPRODUCED", "CLOSED"},
    "FIX_VERIFIED": {"REPRODUCED", "SUPERSEDED", "CLOSED"},
    "SUPERSEDED": {"CLOSED"},
    "CLOSED": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def transition_id() -> str:
    return f"WGIT-{uuid.uuid4().hex}"


def apply_transition(
    record: dict,
    to_status: str,
    actor: str,
    reason: str,
    evidence_refs: list[str],
) -> tuple[dict, dict]:
    validate(record)
    from_status = record["status"]
    if to_status not in ALLOWED.get(from_status, set()):
        raise ValueError(f"transition not allowed: {from_status} -> {to_status}")
    if to_status in {"ROOT_CAUSED", "FIX_AVAILABLE", "FIX_VERIFIED"} and not evidence_refs:
        raise ValueError(f"{to_status} requires transition evidence refs")

    updated = json.loads(json.dumps(record))
    now = utc_now()
    updated["status"] = to_status
    updated["updated_at"] = now

    if to_status == "ROOT_CAUSED" and updated["root_cause"]["state"] != "CONFIRMED":
        raise ValueError("ROOT_CAUSED requires root_cause.state CONFIRMED")
    if to_status == "FIX_AVAILABLE" and updated["fix"]["state"] not in {
        "AVAILABLE_UNVERIFIED",
        "VERIFIED",
    }:
        raise ValueError("FIX_AVAILABLE requires an available fix state")
    if to_status == "FIX_VERIFIED" and updated["fix"]["state"] != "VERIFIED":
        raise ValueError("FIX_VERIFIED requires fix.state VERIFIED")

    transition = {
        "schema": "stegverse.workstation-incident-transition/v1",
        "transition_id": transition_id(),
        "incident_id": updated["incident_id"],
        "timestamp": now,
        "from_status": from_status,
        "to_status": to_status,
        "actor": actor,
        "reason": reason,
        "evidence_refs": evidence_refs,
        "authority_effect": False,
        "publication_effect": False,
    }
    validate(updated)
    return updated, transition


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("incident")
    parser.add_argument("--to", required=True, choices=sorted(ALLOWED))
    parser.add_argument("--actor", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument(
        "--transition-dir",
        default="data/workstation-incident-transitions",
    )
    args = parser.parse_args()

    incident_path = Path(args.incident)
    record = json.loads(incident_path.read_text(encoding="utf-8"))
    updated, transition = apply_transition(
        record,
        args.to,
        args.actor,
        args.reason,
        args.evidence_ref,
    )

    transition_dir = Path(args.transition_dir)
    transition_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = transition_dir / f"{transition['transition_id']}.json"
    if receipt_path.exists():
        raise SystemExit(f"refusing to overwrite transition receipt: {receipt_path}")
    receipt_path.write_text(
        json.dumps(transition, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    incident_path.write_text(
        json.dumps(updated, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
