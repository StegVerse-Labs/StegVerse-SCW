"""Deterministic policy evaluation for the local Stability Gate."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import GateInput, GateInputError


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DELAY = "DELAY"
    BLOCK = "BLOCK"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True)
class GatePolicy:
    allow_threshold: float = 1.0
    delay_threshold: float = 0.7
    max_age_seconds: int = 300

    def validate(self) -> None:
        if self.allow_threshold <= 0:
            raise ValueError("allow_threshold must be positive")
        if self.delay_threshold < 0:
            raise ValueError("delay_threshold must be non-negative")
        if self.delay_threshold >= self.allow_threshold:
            raise ValueError("delay_threshold must be below allow_threshold")
        if self.max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be positive")


@dataclass(frozen=True)
class GateResult:
    decision: Decision
    score: float | None
    reason: str


def compute_score(gate_input: GateInput) -> float:
    denominator = (
        gate_input.environmental_volatility * gate_input.action_magnitude
    )
    if denominator == 0:
        return float("inf")
    return (
        gate_input.deliberation_capacity * gate_input.model_fidelity
    ) / denominator


def evaluate(
    gate_input: GateInput,
    policy: GatePolicy | None = None,
    *,
    now: int | None = None,
) -> GateResult:
    active_policy = policy or GatePolicy()
    try:
        active_policy.validate()
        gate_input.validate(
            now=now,
            max_age_seconds=active_policy.max_age_seconds,
        )
    except (GateInputError, ValueError) as exc:
        return GateResult(Decision.FAIL_CLOSED, None, str(exc))

    score = compute_score(gate_input)
    if score >= active_policy.allow_threshold:
        return GateResult(Decision.ALLOW, score, "score meets allow threshold")
    if score >= active_policy.delay_threshold:
        return GateResult(Decision.DELAY, score, "score requires more deliberation")
    return GateResult(Decision.BLOCK, score, "score is below delay threshold")
