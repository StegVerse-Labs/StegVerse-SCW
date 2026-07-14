"""Canonical, chained receipts for Stability Gate decisions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from .model import GateInput
from .policy import GatePolicy, GateResult
from .provenance import GateProvenance


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class GateReceipt:
    schema: str
    node_id: str
    gate_input: dict[str, object]
    provenance: dict[str, object]
    policy: dict[str, object]
    result: dict[str, object]
    previous_hash: str
    receipt_hash: str

    def canonical_dict(self, *, include_hash: bool = True) -> dict[str, object]:
        payload = asdict(self)
        if not include_hash:
            payload.pop("receipt_hash", None)
        return payload


def create_receipt(
    *,
    node_id: str,
    gate_input: GateInput,
    provenance: GateProvenance,
    policy: GatePolicy,
    result: GateResult,
    previous_hash: str = "",
) -> GateReceipt:
    if not isinstance(node_id, str) or not node_id.strip():
        raise ValueError("node_id must be a non-empty string")
    if previous_hash and (
        len(previous_hash) != 64
        or any(ch not in "0123456789abcdef" for ch in previous_hash.lower())
    ):
        raise ValueError("previous_hash must be an empty string or SHA-256 hex")

    unsigned = {
        "schema": "stegverse.stability-gate.receipt.v2",
        "node_id": node_id,
        "gate_input": gate_input.canonical_dict(),
        "provenance": provenance.canonical_dict(),
        "policy": {
            "allow_threshold": policy.allow_threshold,
            "delay_threshold": policy.delay_threshold,
            "max_age_seconds": policy.max_age_seconds,
        },
        "result": {
            "decision": result.decision.value,
            "reason": result.reason,
            "score": result.score,
        },
        "previous_hash": previous_hash,
    }
    return GateReceipt(**unsigned, receipt_hash=sha256_hex(unsigned))


def verify_receipt_hash(receipt: GateReceipt) -> bool:
    return sha256_hex(receipt.canonical_dict(include_hash=False)) == receipt.receipt_hash
