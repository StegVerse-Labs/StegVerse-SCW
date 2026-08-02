#!/usr/bin/env python3
"""Fail-closed security gate for the patient-owned monitoring workstream."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

ALLOWED_STATES = {
    "COMPLETE",
    "BLOCKED_PENDING_EVIDENCE",
    "MITIGATION_IMPLEMENTED_PENDING_VALIDATION",
    "MITIGATION_IMPLEMENTED_PENDING_REAL_VALIDATION",
    "FAILED",
    "REVIEW_REQUIRED",
}
SEVERITIES = {"low", "moderate", "high", "critical"}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
    ),
}
TEXT_SUFFIXES = {
    ".py", ".json", ".jsonl", ".md", ".txt", ".csv", ".yml", ".yaml",
    ".toml", ".ini", ".cfg", ".sh", ".js", ".ts", ".tsx", ".jsx",
}
IGNORED_PARTS = {".git", ".venv", "venv", "node_modules", "artifacts", "dist", "build"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_risk_register(register: dict) -> list[str]:
    errors: list[str] = []
    policy = register.get("risk_policy")
    if not isinstance(policy, dict):
        return ["risk_policy must be an object"]
    required_true = (
        "federal_floor_only",
        "critical_open_risks_block_activation",
        "high_open_risks_require_owner_and_release_condition",
        "exceptions_must_expire",
        "zero_means_measured_zero",
    )
    for key in required_true:
        if policy.get(key) is not True:
            errors.append(f"risk_policy.{key} must be true")
    if policy.get("unknown_risk_state", "missing") is not None:
        errors.append("risk_policy.unknown_risk_state must be null")

    risks = register.get("risks")
    if not isinstance(risks, list) or not risks:
        errors.append("risks must be a non-empty array")
        return errors
    seen: set[str] = set()
    for index, risk in enumerate(risks):
        prefix = f"risks[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{prefix} must be an object")
            continue
        risk_id = risk.get("risk_id")
        if not isinstance(risk_id, str) or not risk_id:
            errors.append(f"{prefix}.risk_id is required")
        elif risk_id in seen:
            errors.append(f"duplicate risk_id: {risk_id}")
        else:
            seen.add(risk_id)
        severity = risk.get("severity")
        if severity not in SEVERITIES:
            errors.append(f"{prefix}.severity must be one of {sorted(SEVERITIES)}")
        if risk.get("state") not in ALLOWED_STATES:
            errors.append(f"{prefix}.state is not an allowed state")
        for field in ("owner", "release_condition"):
            if not isinstance(risk.get(field), str) or not risk[field].strip():
                errors.append(f"{prefix}.{field} is required")
        for field in ("controls", "evidence_required"):
            if not isinstance(risk.get(field), list) or not risk[field]:
                errors.append(f"{prefix}.{field} must be a non-empty array")
        if severity == "critical" and risk.get("state") != "COMPLETE":
            if not risk.get("release_condition"):
                errors.append(f"{prefix} critical open risk lacks release condition")

    exceptions = register.get("exceptions")
    if not isinstance(exceptions, list):
        errors.append("exceptions must be an array")
    else:
        for index, exception in enumerate(exceptions):
            prefix = f"exceptions[{index}]"
            if not isinstance(exception, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in ("exception_id", "owner", "approved_by", "expires_at", "compensating_control"):
                if not isinstance(exception.get(field), str) or not exception[field].strip():
                    errors.append(f"{prefix}.{field} is required")
            if str(exception.get("expires_at", "")).lower() in {"never", "none", "indefinite"}:
                errors.append(f"{prefix}.expires_at cannot be indefinite")
    return errors


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"Dockerfile", "Makefile"}:
            yield path


def scan_secrets(root: Path) -> list[dict]:
    findings: list[dict] = []
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "security-gate-allow-example" in line:
                continue
            for kind, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    findings.append({"path": str(path), "line": line_no, "kind": kind})
    return findings


def build_receipt(register_path: Path, root: Path) -> dict:
    register = load_json(register_path)
    risk_errors = validate_risk_register(register)
    secret_findings = scan_secrets(root)
    status = "COMPLETE" if not risk_errors and not secret_findings else "FAILED"
    receipt = {
        "schema_version": "pom.security-gate-receipt.v1",
        "status": status,
        "risk_register": {
            "path": str(register_path),
            "sha256": sha256_file(register_path),
            "risk_count": len(register.get("risks", [])),
            "validation_errors": risk_errors,
        },
        "secret_scan": {
            "root": str(root),
            "files_scanned": sum(1 for _ in iter_text_files(root)),
            "finding_count": len(secret_findings),
            "findings": secret_findings,
        },
        "activation_state": "BLOCKED_PENDING_EVIDENCE",
        "next_task": "Inspect CI result and complete operational activation evidence",
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--risk-register", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    receipt = build_receipt(Path(args.risk_register), Path(args.root))
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        destination = Path(args.receipt)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if receipt["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
