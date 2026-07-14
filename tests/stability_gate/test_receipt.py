from dataclasses import replace

from engine.stability_gate.model import GateInput
from engine.stability_gate.policy import GatePolicy, evaluate
from engine.stability_gate.provenance import provenance_from_dict
from engine.stability_gate.receipt import create_receipt, verify_receipt_hash
from engine.stability_gate.replay import replay, verify_chain

NOW = 2_000_000_000


def make_input():
    return GateInput(
        deliberation_capacity=1.0,
        model_fidelity=1.0,
        environmental_volatility=1.0,
        action_magnitude=1.0,
        observed_at=NOW,
        source="test",
    )


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


def make_receipt(previous_hash=""):
    gate_input = make_input()
    policy = GatePolicy()
    result = evaluate(gate_input, policy, now=NOW)
    return create_receipt(
        node_id="scw-test-node",
        gate_input=gate_input,
        provenance=make_provenance(),
        policy=policy,
        result=result,
        previous_hash=previous_hash,
    )


def test_receipt_hash_and_replay():
    receipt = make_receipt()
    assert verify_receipt_hash(receipt)
    assert replay(receipt)


def test_tampering_breaks_verification():
    receipt = make_receipt()
    tampered = replace(receipt, result={**receipt.result, "decision": "BLOCK"})
    assert not verify_receipt_hash(tampered)
    assert not replay(tampered)


def test_provenance_tampering_breaks_verification():
    receipt = make_receipt()
    tampered = replace(receipt, provenance={})
    assert not verify_receipt_hash(tampered)
    assert not replay(tampered)


def test_chain_verifies_from_genesis():
    first = make_receipt()
    second = make_receipt(first.receipt_hash)
    assert verify_chain([first, second])


def test_chain_rejects_wrong_parent():
    first = make_receipt()
    second = make_receipt("0" * 64)
    assert not verify_chain([first, second])
