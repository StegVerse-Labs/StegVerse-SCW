"""Deterministic replay and chain verification for Stability Gate receipts."""

from __future__ import annotations

from .model import GateInput
from .policy import Decision, GatePolicy, evaluate
from .receipt import GateReceipt, verify_receipt_hash


def replay(receipt: GateReceipt) -> bool:
    if not verify_receipt_hash(receipt):
        return False

    gate_input = GateInput(**receipt.gate_input)
    policy = GatePolicy(**receipt.policy)
    result = evaluate(gate_input, policy, now=gate_input.observed_at)

    stored = receipt.result
    return (
        result.decision.value == stored.get("decision")
        and result.reason == stored.get("reason")
        and result.score == stored.get("score")
    )


def verify_chain(receipts: list[GateReceipt]) -> bool:
    previous = ""
    for receipt in receipts:
        if receipt.previous_hash != previous:
            return False
        if not replay(receipt):
            return False
        previous = receipt.receipt_hash
    return True
