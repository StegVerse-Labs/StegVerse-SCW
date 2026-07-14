#!/usr/bin/env python3
"""Run representative Stability Gate fixtures and emit deterministic evidence."""

from __future__ import annotations

import json
from pathlib import Path

from engine.stability_gate.adapter import evaluate_context_dry_run
from engine.stability_gate.storage import write_receipt

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "stability_gate" / "fixtures"
REPORT_DIR = ROOT / "artifacts" / "reports" / "stability_gate"
REPORT = REPORT_DIR / "representative-cases.json"
FIXTURE_NAMES = ("allow.json", "delay.json", "block.json", "fail_closed.json")
OBSERVED_AT = 2_000_000_000


def main() -> int:
    cases = []
    failures = []

    for name in FIXTURE_NAMES:
        fixture = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        result, receipt = evaluate_context_dry_run(
            command="fixture-validation",
            target_repo="StegVerse-Labs/StegVerse-SCW",
            args={"stability_gate": fixture["stability_gate"]},
            node_id="StegVerse-Labs/StegVerse-SCW:fixture-runner",
            observed_at=OBSERVED_AT,
        )
        expected = fixture["expected_decision"]
        passed = result.decision.value == expected
        receipt_path = None
        if receipt is not None:
            receipt_path = str(write_receipt(receipt, receipt_dir=ROOT / "artifacts" / "receipts" / "stability_gate"))

        case = {
            "fixture": name,
            "expected_decision": expected,
            "actual_decision": result.decision.value,
            "score": result.score,
            "reason": result.reason,
            "receipt_path": receipt_path,
            "passed": passed,
        }
        cases.append(case)
        if not passed:
            failures.append(name)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "stegverse.stability-gate.representative-cases.v1",
        "observed_at": OBSERVED_AT,
        "cases": cases,
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
    }
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
