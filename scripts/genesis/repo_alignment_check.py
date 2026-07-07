#!/usr/bin/env python3
"""Safe repository alignment check shim for SCW guardian worker workflows.

This checker intentionally performs local, non-mutating validation only. It exists
so the workflow can fail on concrete repository-state issues instead of failing
because the expected checker path is missing.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "STEGVERSE_SCW_MIRROR_HANDOFF.md"
REPORT_DIR = ROOT / "reports" / "genesis"
REPORT = REPORT_DIR / "repo_alignment_check.json"


def main() -> int:
    errors: list[str] = []
    if not HANDOFF.exists():
        errors.append("missing_STEGVERSE_SCW_MIRROR_HANDOFF.md")
    workflows = ROOT / ".github" / "workflows"
    has_yml = any(workflows.glob("*.yml"))
    has_yaml = any(workflows.glob("*.yaml"))
    if workflows.exists() and not (has_yml or has_yaml):
        errors.append("workflows_directory_has_no_workflows")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "stegverse.scw.repo_alignment_check.v0.1",
        "repo": "StegVerse-Labs/StegVerse-SCW",
        "status": "fail" if errors else "pass",
        "errors": errors,
        "non_claims": {
            "cross_repo_mutation_authority": False,
            "credential_repair_performed": False,
            "force_push_allowed": False,
        },
    }
    report_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    REPORT.write_text(report_text, encoding="utf-8")
    if errors:
        print("SCW_REPO_ALIGNMENT_CHECK_FAIL: " + ", ".join(errors))
        return 1
    print("SCW_REPO_ALIGNMENT_CHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
