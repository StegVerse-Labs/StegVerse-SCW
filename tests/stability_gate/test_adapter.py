import json
from pathlib import Path

from engine.stability_gate.adapter import evaluate_context_dry_run
from engine.stability_gate.failure_receipt import (
    GateFailureReceipt,
    verify_failure_receipt_hash,
)
from engine.stability_gate.policy import Decision

FIXTURES = Path(__file__).parent / "fixtures"
NOW = 2_000_000_000


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_decision_fixtures():
    for filename in ("allow.json", "delay.json", "block.json", "fail_closed.json"):
        fixture = load_fixture(filename)
        result, receipt = evaluate_context_dry_run(
            command="autopatch",
            target_repo="StegVerse-Labs/example",
            args={"stability_gate": fixture["stability_gate"]},
            node_id="scw-test-node",
            observed_at=NOW,
        )
        assert result.decision.value == fixture["expected_decision"]
        assert receipt is not None
        if result.decision is Decision.FAIL_CLOSED:
            assert isinstance(receipt, GateFailureReceipt)
            assert verify_failure_receipt_hash(receipt)


def test_missing_metrics_fail_closed_with_receipt():
    result, receipt = evaluate_context_dry_run(
        command="autopatch",
        target_repo="StegVerse-Labs/example",
        args={},
        node_id="scw-test-node",
        observed_at=NOW,
    )
    assert result.decision is Decision.FAIL_CLOSED
    assert isinstance(receipt, GateFailureReceipt)
    assert verify_failure_receipt_hash(receipt)
    assert receipt.context["command"] == "autopatch"
    assert receipt.context["target_repo"] == "StegVerse-Labs/example"
