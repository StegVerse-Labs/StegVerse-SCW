"""Canonical receipts for Stability Gate context failures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .policy import Decision, GatePolicy, GateResult
from .receipt import sha256_hex


@dataclass(frozen=True)
class GateFailureReceipt:
    schema: str
    node_id: str
    context: dict[str, object]
    policy: dict[str, object]
    result: dict[str, object]
    previous_hash: str
    receipt_hash: str

    def canonical_dict(self, *, include_hash: bool = True) -> dict[str, object]:
        payload = asdict(self)
        if not include_hash:
            payload.pop("receipt_hash", None)
        return payload


def _safe_context_value(value: Any) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {
            str(key): _safe_context_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_safe_context_value(item) for item in value]
    return repr(value)


def create_failure_receipt(
    *,
    node_id: str,
    command: str,
    target_repo: str | None,
    args: dict[str, Any],
    policy: GatePolicy,
    reason: str,
    previous_hash: str = "",
) -> GateFailureReceipt:
    if not isinstance(node_id, str) or not node_id.strip():
        raise ValueError("node_id must be a non-empty string")
    if previous_hash and (
        len(previous_hash) != 64
        or any(ch not in "0123456789abcdef" for ch in previous_hash.lower())
    ):
        raise ValueError("previous_hash must be an empty string or SHA-256 hex")

    result = GateResult(Decision.FAIL_CLOSED, None, reason)
    unsigned = {
        "schema": "stegverse.stability-gate.failure-receipt.v1",
        "node_id": node_id,
        "context": {
            "args": _safe_context_value(args),
            "command": command,
            "target_repo": target_repo,
        },
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
    return GateFailureReceipt(**unsigned, receipt_hash=sha256_hex(unsigned))


def verify_failure_receipt_hash(receipt: GateFailureReceipt) -> bool:
    return sha256_hex(receipt.canonical_dict(include_hash=False)) == receipt.receipt_hash
