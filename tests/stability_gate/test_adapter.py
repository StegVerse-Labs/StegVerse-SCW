import json
from pathlib import Path

from engine.stability_gate.adapter import evaluate_context_dry_run
from engine.stability_gate.failure_receipt import (
    GateFailureReceipt,
    verify_failure_receipt_hash,
)
from engine.stability_gate.policy import Decision
from engine.stability_gate.receipt import verify_receipt_hash

FIXTURES = Path(__file__).parent / "fixtures"
NOW = 2_000_000_000


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def caller_asserted_provenance():
    return {
        name: {
            "derivation_class": "CALLER_ASSERTED",
            "producer": "fixture-runner",
            "method": "fixture",
            "evidence_refs": [],
        }
        for name in (
            "deliberation_capacity",
            "model_fidelity",
            "environmental_volatility",
            "action_magnitude",
        )
    }


def test_decision_fixtures():
    for filename in ("allow.json", "delay.json", "block.json", "fail_closed.json"):
        fixture = load_fixture(filename)
        result, receipt = evaluate_context_dry_run(
            command="autopatch",
            target_repo="StegVerse-Labs/example",
            args={
                "stability_gate": fixture["stability_gate"],
                "stability_gate_provenance": caller_asserted_provenance(),
            },
            node_id="scw-test-node",
            observed_at=NOW,
        )
        assert result.decision.value == fixture["expected_decision"]
        assert receipt is not None
        if result.decision is Decision.FAIL_CLOSED:
            assert isinstance(receipt, GateFailureReceipt)
            assert verify_failure_receipt_hash(receipt)
        else:
            assert verify_receipt_hash(receipt)
            assert receipt.provenance["model_fidelity"]["producer"] == "fixture-runner"


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


def test_missing_provenance_fails_closed_with_receipt():
    fixture = load_fixture("allow.json")
    result, receipt = evaluate_context_dry_run(
        command="autopatch",
        target_repo="StegVerse-Labs/example",
        args={"stability_gate": fixture["stability_gate"]},
        node_id="scw-test-node",
        observed_at=NOW,
    )
    assert result.decision is Decision.FAIL_CLOSED
    assert isinstance(receipt, GateFailureReceipt)
    assert "stability_gate_provenance" in receipt.result["reason"]
