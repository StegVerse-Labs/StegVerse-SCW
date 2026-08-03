from datetime import datetime, timezone

from scripts.stability_gate_task_controller import validate_registry

NOW = datetime(2026, 8, 3, 3, 32, tzinfo=timezone.utc)


def task(**overrides):
    value = {
        "task_id": "SG-TEST-001",
        "originating_goal": "test",
        "destination": "example",
        "claim_state": "CLAIMED_FOR_VALIDATION",
        "claimant": "test-lane",
        "role": "validation",
        "claim_created_at": "2026-08-03T03:00:00Z",
        "claim_expires_at": "2026-08-04T03:00:00Z",
        "release_condition": "receipt exists",
        "collision_boundaries": ["repo:main:example"],
        "completion_state": "IMPLEMENTED_BUT_UNVALIDATED",
        "validation_state": "PENDING",
        "integration_state": "INSTALLED",
        "archival_dependency": False,
        "evidence_location": "artifact",
        "next_executable_action": "inspect artifact",
    }
    value.update(overrides)
    return value


def test_valid_registry_has_no_findings():
    assert validate_registry({"tasks": [task()]}, NOW) == []


def test_stale_active_claim_requires_review():
    findings = validate_registry(
        {"tasks": [task(claim_expires_at="2026-08-03T03:31:00Z")]}, NOW
    )
    assert findings[0]["code"] == "STALE_CLAIM"


def test_duplicate_active_collision_fails():
    findings = validate_registry(
        {
            "tasks": [
                task(),
                task(task_id="SG-TEST-002"),
            ]
        },
        NOW,
    )
    assert any(finding["code"] == "ACTIVE_COLLISION" for finding in findings)


def test_unassigned_open_task_fails():
    findings = validate_registry({"tasks": [task(claimant="")]}, NOW)
    assert any(finding["code"] == "UNASSIGNED_TASK" for finding in findings)
