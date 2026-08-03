#!/usr/bin/env python3
"""Validate Stability Gate task ownership and emit a continuation receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_STATES = {
    "UNCLAIMED",
    "CLAIMED_FOR_IMPLEMENTATION",
    "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION",
    "MACHINE_OWNED",
    "BLOCKED",
    "COMPLETE",
    "SUPERSEDED",
    "MERGED_INTO_CANONICAL_WORKSTREAM",
    "RETRY",
    "REVIEW_REQUIRED",
    "FAILED",
}
ACTIVE_STATES = {
    "CLAIMED_FOR_IMPLEMENTATION",
    "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION",
    "MACHINE_OWNED",
}
REQUIRED_FIELDS = {
    "task_id",
    "originating_goal",
    "destination",
    "claim_state",
    "claimant",
    "role",
    "claim_created_at",
    "release_condition",
    "collision_boundaries",
    "completion_state",
    "validation_state",
    "integration_state",
    "archival_dependency",
    "evidence_location",
    "next_executable_action",
}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def validate_registry(registry: dict[str, object], now: datetime) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    tasks = registry.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return [{"severity": "FAILED", "code": "NO_TASKS", "detail": "tasks must be a non-empty array"}]

    seen_ids: set[str] = set()
    seen_collisions: dict[str, str] = {}

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            findings.append({"severity": "FAILED", "code": "INVALID_TASK", "detail": f"tasks[{index}] must be an object"})
            continue

        missing = sorted(REQUIRED_FIELDS - set(task))
        if missing:
            findings.append({"severity": "FAILED", "code": "MISSING_FIELDS", "task_id": task.get("task_id"), "detail": missing})
            continue

        task_id = str(task["task_id"])
        if task_id in seen_ids:
            findings.append({"severity": "FAILED", "code": "DUPLICATE_TASK_ID", "task_id": task_id})
        seen_ids.add(task_id)

        state = task["claim_state"]
        if state not in ALLOWED_STATES:
            findings.append({"severity": "FAILED", "code": "INVALID_STATE", "task_id": task_id, "detail": state})

        claimant = task["claimant"]
        if state not in {"COMPLETE", "SUPERSEDED", "MERGED_INTO_CANONICAL_WORKSTREAM"} and (
            not isinstance(claimant, str) or not claimant.strip()
        ):
            findings.append({"severity": "FAILED", "code": "UNASSIGNED_TASK", "task_id": task_id})

        release_condition = task["release_condition"]
        if not isinstance(release_condition, str) or not release_condition.strip():
            findings.append({"severity": "FAILED", "code": "NO_RELEASE_CONDITION", "task_id": task_id})

        next_action = task["next_executable_action"]
        if state not in {"COMPLETE", "SUPERSEDED", "MERGED_INTO_CANONICAL_WORKSTREAM"} and (
            not isinstance(next_action, str) or not next_action.strip()
        ):
            findings.append({"severity": "FAILED", "code": "NO_NEXT_ACTION", "task_id": task_id})

        expires = parse_time(task.get("claim_expires_at"))
        if state in ACTIVE_STATES and expires is not None and expires <= now:
            findings.append({"severity": "REVIEW_REQUIRED", "code": "STALE_CLAIM", "task_id": task_id, "detail": task.get("claim_expires_at")})

        boundaries = task["collision_boundaries"]
        if not isinstance(boundaries, list) or not boundaries:
            findings.append({"severity": "FAILED", "code": "NO_COLLISION_BOUNDARY", "task_id": task_id})
        else:
            for boundary in boundaries:
                if not isinstance(boundary, str) or not boundary.strip():
                    findings.append({"severity": "FAILED", "code": "INVALID_COLLISION_BOUNDARY", "task_id": task_id})
                    continue
                prior = seen_collisions.get(boundary)
                if prior and prior != task_id and state in ACTIVE_STATES:
                    findings.append({"severity": "FAILED", "code": "ACTIVE_COLLISION", "task_id": task_id, "detail": {"boundary": boundary, "other_task": prior}})
                elif state in ACTIVE_STATES:
                    seen_collisions[boundary] = task_id

    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/stability-gate-tasks.json")
    parser.add_argument("--output", default="artifacts/reports/stability_gate/STABILITY_GATE_TASK_RECEIPT.json")
    parser.add_argument("--now", default=None, help="ISO-8601 UTC time for deterministic tests")
    args = parser.parse_args()

    registry_path = Path(args.registry)
    output_path = Path(args.output)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    assert now is not None

    findings = validate_registry(registry, now)
    severities = {finding["severity"] for finding in findings}
    if "FAILED" in severities:
        status = "FAILED"
    elif "REVIEW_REQUIRED" in severities:
        status = "REVIEW_REQUIRED"
    else:
        status = "COMPLETE"

    tasks = registry["tasks"]
    counts: dict[str, int] = {}
    for task in tasks:
        counts[task["claim_state"]] = counts.get(task["claim_state"], 0) + 1

    unsigned = {
        "schema": "stegverse.stability-gate.task-receipt.v1",
        "goal_id": registry.get("goal_id"),
        "owner_repository": registry.get("owner_repository"),
        "branch": registry.get("branch"),
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "registry_path": str(registry_path),
        "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        "status": status,
        "task_count": len(tasks),
        "claim_state_counts": counts,
        "findings": findings,
        "next_executable_tasks": [
            {"task_id": task["task_id"], "claim_state": task["claim_state"], "next_executable_action": task["next_executable_action"]}
            for task in tasks
            if task["claim_state"] not in {"COMPLETE", "SUPERSEDED", "MERGED_INTO_CANONICAL_WORKSTREAM"}
        ],
    }
    receipt = {**unsigned, "receipt_hash": hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if status == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
