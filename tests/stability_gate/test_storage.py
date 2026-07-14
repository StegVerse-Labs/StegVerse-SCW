import json

from engine.stability_gate.model import GateInput
from engine.stability_gate.policy import GatePolicy, evaluate
from engine.stability_gate.provenance import provenance_from_dict
from engine.stability_gate.receipt import create_receipt
from engine.stability_gate.storage import write_receipt

NOW = 2_000_000_000


def make_provenance():
    return provenance_from_dict({
        name: {
            "derivation_class": "CALLER_ASSERTED",
            "producer": "scw-test",
            "method": "fixture",
            "evidence_refs": [],
        }
        for name in (
            "deliberation_capacity",
            "model_fidelity",
            "environmental_volatility",
            "action_magnitude",
        )
    })


def make_receipt():
    gate_input = GateInput(
        deliberation_capacity=1.0,
        model_fidelity=1.0,
        environmental_volatility=1.0,
        action_magnitude=1.0,
        observed_at=NOW,
        source="test:storage",
    )
    policy = GatePolicy()
    result = evaluate(gate_input, policy, now=NOW)
    return create_receipt(
        node_id="scw-test-node",
        gate_input=gate_input,
        provenance=make_provenance(),
        policy=policy,
        result=result,
    )


def test_write_receipt_is_idempotent(tmp_path):
    receipt = make_receipt()
    first = write_receipt(receipt, receipt_dir=tmp_path)
    second = write_receipt(receipt, receipt_dir=tmp_path)
    assert first == second
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["receipt_hash"] == receipt.receipt_hash
    assert payload["schema"] == "stegverse.stability-gate.receipt.v2"
