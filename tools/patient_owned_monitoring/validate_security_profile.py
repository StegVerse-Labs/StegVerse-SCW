#!/usr/bin/env python3
"""Fail-closed validator for the patient-owned monitoring security profile."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "profile_id",
    "status",
    "policy",
    "references",
    "required_control_families",
    "activation_evidence",
    "exception_contract",
    "validation_semantics",
}

REQUIRED_FAMILIES = {
    "governance",
    "data_protection",
    "identity_access",
    "device_integrity",
    "evidence_integrity",
    "audit_detection",
    "availability_recovery",
    "software_supply_chain",
    "incident_response",
}

REQUIRED_REFERENCES = {
    "HHS_HIPAA_SECURITY_RULE",
    "HHS_RISK_ANALYSIS_GUIDANCE",
    "NIST_SP_800_53_REV5_CURRENT_PATCH",
    "NIST_CSF_2_0",
    "CISA_SECURE_BY_DESIGN",
}

REQUIRED_EXCEPTION_FIELDS = {
    "exception_id",
    "control",
    "rationale",
    "compensating_controls",
    "owner",
    "approved_by",
    "created_at",
    "expires_at",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(profile))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")

    if profile.get("schema_version") != "pom.security-profile.v1":
        errors.append("schema_version must be pom.security-profile.v1")
    if profile.get("status") != "MANDATORY":
        errors.append("status must be MANDATORY")

    policy = profile.get("policy")
    if not isinstance(policy, str) or "minimum floor" not in policy.lower():
        errors.append("policy must state that federal requirements are the minimum floor")

    references = profile.get("references")
    if not isinstance(references, list):
        errors.append("references must be an array")
    else:
        absent = sorted(REQUIRED_REFERENCES - set(references))
        if absent:
            errors.append(f"missing baseline references: {', '.join(absent)}")

    families = profile.get("required_control_families")
    if not isinstance(families, dict):
        errors.append("required_control_families must be an object")
    else:
        absent = sorted(REQUIRED_FAMILIES - set(families))
        if absent:
            errors.append(f"missing control families: {', '.join(absent)}")
        for name, controls in families.items():
            if not isinstance(controls, list) or not controls:
                errors.append(f"control family {name} must contain at least one control")
            elif len(controls) != len(set(controls)):
                errors.append(f"control family {name} contains duplicate controls")

    evidence = profile.get("activation_evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("activation_evidence must contain required receipts")
    elif len(evidence) != len(set(evidence)):
        errors.append("activation_evidence contains duplicates")

    exception = profile.get("exception_contract")
    if not isinstance(exception, dict):
        errors.append("exception_contract must be an object")
    else:
        fields = exception.get("required_fields")
        if not isinstance(fields, list):
            errors.append("exception_contract.required_fields must be an array")
        else:
            absent = sorted(REQUIRED_EXCEPTION_FIELDS - set(fields))
            if absent:
                errors.append(f"missing exception fields: {', '.join(absent)}")
        if exception.get("indefinite_exceptions_allowed") is not False:
            errors.append("indefinite security exceptions must be prohibited")
        if exception.get("missing_exception_evidence") != "FAIL":
            errors.append("missing exception evidence must fail")

    semantics = profile.get("validation_semantics")
    if not isinstance(semantics, dict):
        errors.append("validation_semantics must be an object")
    else:
        expected = {
            "missing_required_control": "FAIL",
            "missing_activation_evidence": "BLOCKED",
            "unknown_value": None,
            "zero_means_measured_zero": True,
            "unreviewed_security_claim": "NOT_VALIDATED",
        }
        for key, value in expected.items():
            if semantics.get(key) != value:
                errors.append(f"validation_semantics.{key} must equal {value!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument("--receipt")
    args = parser.parse_args()

    path = Path(args.profile)
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAILED", "errors": [str(exc)]}, indent=2))
        return 2

    errors = validate(profile)
    result = {
        "schema_version": "pom.security-profile-validation.v1",
        "profile": str(path),
        "profile_sha256": _sha256(path),
        "profile_id": profile.get("profile_id"),
        "status": "COMPLETE" if not errors else "FAILED",
        "errors": errors,
        "required_control_family_count": len(REQUIRED_FAMILIES),
        "declared_activation_evidence_count": len(profile.get("activation_evidence", []))
        if isinstance(profile.get("activation_evidence"), list)
        else 0,
        "activation_state": "BLOCKED_PENDING_EVIDENCE" if not errors else "NOT_ELIGIBLE",
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        receipt = Path(args.receipt)
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
