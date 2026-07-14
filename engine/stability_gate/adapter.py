"""SCW integration adapter for dry-run Stability Gate evaluation."""

from __future__ import annotations

from time import time
from typing import Any

from .failure_receipt import GateFailureReceipt, create_failure_receipt
from .model import GateInput
from .policy import Decision, GatePolicy, GateResult, evaluate
from .provenance import GateProvenance, ProvenanceError, provenance_from_dict
from .provenance_policy import (
    ProvenancePolicyResult,
    default_dry_run_policy,
    evaluate_provenance,
)
from .receipt import GateReceipt, create_receipt


class GateContextError(ValueError):
    """Raised when SCW context cannot produce authoritative gate inputs."""


def gate_input_from_context(
    *,
    command: str,
    target_repo: str | None,
    args: dict[str, Any],
    observed_at: int | None = None,
) -> GateInput:
    """Build a gate input only from explicit runtime measurements."""

    metrics = args.get("stability_gate")
    if not isinstance(metrics, dict):
        raise GateContextError("args.stability_gate must be an object")

    required = {
        "deliberation_capacity",
        "model_fidelity",
        "environmental_volatility",
        "action_magnitude",
    }
    missing = sorted(required - set(metrics))
    if missing:
        raise GateContextError(
            "missing stability_gate metrics: " + ", ".join(missing)
        )

    source = metrics.get("source") or f"scw:{command}:{target_repo or 'none'}"
    return GateInput(
        deliberation_capacity=metrics["deliberation_capacity"],
        model_fidelity=metrics["model_fidelity"],
        environmental_volatility=metrics["environmental_volatility"],
        action_magnitude=metrics["action_magnitude"],
        observed_at=int(time()) if observed_at is None else observed_at,
        source=source,
    )


def provenance_from_context(args: dict[str, Any]) -> GateProvenance:
    payload = args.get("stability_gate_provenance")
    if payload is None:
        raise GateContextError("args.stability_gate_provenance must be an object")
    try:
        return provenance_from_dict(payload)
    except ProvenanceError as exc:
        raise GateContextError(str(exc)) from exc


def assess_context_provenance(args: dict[str, Any]) -> ProvenancePolicyResult:
    provenance = provenance_from_context(args)
    return evaluate_provenance(
        provenance,
        default_dry_run_policy(),
        dry_run=True,
    )


def evaluate_context_dry_run(
    *,
    command: str,
    target_repo: str | None,
    args: dict[str, Any],
    node_id: str,
    previous_hash: str = "",
    observed_at: int | None = None,
    policy: GatePolicy | None = None,
) -> tuple[GateResult, GateReceipt | GateFailureReceipt]:
    active_policy = policy or GatePolicy()
    try:
        gate_input = gate_input_from_context(
            command=command,
            target_repo=target_repo,
            args=args,
            observed_at=observed_at,
        )
        provenance = provenance_from_context(args)
    except (GateContextError, TypeError, ValueError) as exc:
        result = GateResult(Decision.FAIL_CLOSED, None, str(exc))
        receipt = create_failure_receipt(
            node_id=node_id,
            command=command,
            target_repo=target_repo,
            args=args,
            policy=active_policy,
            reason=result.reason,
            previous_hash=previous_hash,
        )
        return result, receipt

    result = evaluate(gate_input, active_policy, now=gate_input.observed_at)
    receipt = create_receipt(
        node_id=node_id,
        gate_input=gate_input,
        provenance=provenance,
        policy=active_policy,
        result=result,
        previous_hash=previous_hash,
    )
    return result, receipt
