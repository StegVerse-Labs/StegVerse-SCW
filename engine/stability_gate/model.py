"""Validated input model for the local Stability Gate."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from time import time


class GateInputError(ValueError):
    """Raised when gate inputs cannot support an admissibility decision."""


@dataclass(frozen=True)
class GateInput:
    deliberation_capacity: float
    model_fidelity: float
    environmental_volatility: float
    action_magnitude: float
    observed_at: int
    source: str

    def validate(self, *, now: int | None = None, max_age_seconds: int = 300) -> None:
        current = int(time()) if now is None else int(now)
        values = {
            "deliberation_capacity": self.deliberation_capacity,
            "model_fidelity": self.model_fidelity,
            "environmental_volatility": self.environmental_volatility,
            "action_magnitude": self.action_magnitude,
        }

        for name, value in values.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise GateInputError(f"{name} must be numeric")
            if not isfinite(float(value)):
                raise GateInputError(f"{name} must be finite")

        if self.deliberation_capacity < 0:
            raise GateInputError("deliberation_capacity must be non-negative")
        if not 0 <= self.model_fidelity <= 1:
            raise GateInputError("model_fidelity must be within [0, 1]")
        if self.environmental_volatility < 0:
            raise GateInputError("environmental_volatility must be non-negative")
        if self.action_magnitude <= 0:
            raise GateInputError("action_magnitude must be greater than zero")
        if not isinstance(self.observed_at, int) or isinstance(self.observed_at, bool):
            raise GateInputError("observed_at must be an integer epoch timestamp")
        if self.observed_at > current:
            raise GateInputError("observed_at cannot be in the future")
        if current - self.observed_at > max_age_seconds:
            raise GateInputError("gate input is stale")
        if not isinstance(self.source, str) or not self.source.strip():
            raise GateInputError("source must be a non-empty string")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "action_magnitude": float(self.action_magnitude),
            "deliberation_capacity": float(self.deliberation_capacity),
            "environmental_volatility": float(self.environmental_volatility),
            "model_fidelity": float(self.model_fidelity),
            "observed_at": self.observed_at,
            "source": self.source,
        }
