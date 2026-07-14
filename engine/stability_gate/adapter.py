"""SCW integration adapter for dry-run Stability Gate evaluation."""

from __future__ import annotations

from dataclasses import asdict
from time import time
from typing import Any

from .model import GateInput
from .policy import GatePolicy, GateResult, evaluate
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
    """Build a gate input only from explicit runtime measurements.

    No inferred defaults are used for D, M, E, or A. Missing values are
    intentionally rejected so dry-run evidence exposes unresolved schemas.
    """

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


def evaluate_context_dry_run(
    *,
    command: str,
    target_repo: str | None,
    args: dict[str, Any],
    node_id: str,
    previous_hash: str = "",
    observed_at: int | None = None,
    policy: GatePolicy | None = None,
) -> tuple[GateResult, GateReceipt | None]:
    active_policy = policy or GatePolicy()
    try:
        gate_input = gate_input_from_context(
            command=command,
            target_repo=target_repo,
            args=args,
            observed_at=observed_at,
        )
    except (GateContextError, TypeError, ValueError) as exc:
        from .policy import Decision

        return GateResult(Decision.FAIL_CLOSED, None, str(exc)), None

    result = evaluate(gate_input, active_policy, now=gate_input.observed_at)
    receipt = create_receipt(
        node_id=node_id,
        gate_input=gate_input,
        policy=active_policy,
        result=result,
        previous_hash=previous_hash,
    )
    return result, receipt
