"""Provenance model for Stability Gate metric observations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Mapping


class ProvenanceError(ValueError):
    """Raised when metric provenance is incomplete or contradictory."""


class DerivationClass(str, Enum):
    CALLER_ASSERTED = "CALLER_ASSERTED"
    DERIVED = "DERIVED"
    RECONSTRUCTED = "RECONSTRUCTED"


METRIC_NAMES = (
    "deliberation_capacity",
    "model_fidelity",
    "environmental_volatility",
    "action_magnitude",
)


@dataclass(frozen=True)
class MetricProvenance:
    derivation_class: DerivationClass
    producer: str
    method: str
    evidence_refs: tuple[str, ...] = ()

    def validate(self) -> None:
        if not isinstance(self.producer, str) or not self.producer.strip():
            raise ProvenanceError("producer must be a non-empty string")
        if not isinstance(self.method, str) or not self.method.strip():
            raise ProvenanceError("method must be a non-empty string")
        if any(not isinstance(ref, str) or not ref.strip() for ref in self.evidence_refs):
            raise ProvenanceError("evidence_refs must contain non-empty strings")
        if self.derivation_class in {
            DerivationClass.DERIVED,
            DerivationClass.RECONSTRUCTED,
        } and not self.evidence_refs:
            raise ProvenanceError(
                f"{self.derivation_class.value} provenance requires evidence_refs"
            )

    def canonical_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "derivation_class": self.derivation_class.value,
            "evidence_refs": list(self.evidence_refs),
            "method": self.method,
            "producer": self.producer,
        }


@dataclass(frozen=True)
class GateProvenance:
    metrics: Mapping[str, MetricProvenance]

    def validate(self) -> None:
        missing = sorted(set(METRIC_NAMES) - set(self.metrics))
        extra = sorted(set(self.metrics) - set(METRIC_NAMES))
        if missing:
            raise ProvenanceError("missing metric provenance: " + ", ".join(missing))
        if extra:
            raise ProvenanceError("unknown metric provenance: " + ", ".join(extra))
        for name in METRIC_NAMES:
            value = self.metrics[name]
            if not isinstance(value, MetricProvenance):
                raise ProvenanceError(f"{name} provenance must be MetricProvenance")
            value.validate()

    def canonical_dict(self) -> dict[str, object]:
        self.validate()
        return {
            name: self.metrics[name].canonical_dict()
            for name in sorted(METRIC_NAMES)
        }


def provenance_from_dict(payload: object) -> GateProvenance:
    if not isinstance(payload, dict):
        raise ProvenanceError("provenance must be an object")

    metrics: dict[str, MetricProvenance] = {}
    for name, value in payload.items():
        if not isinstance(value, dict):
            raise ProvenanceError(f"{name} provenance must be an object")
        try:
            derivation_class = DerivationClass(value["derivation_class"])
            producer = value["producer"]
            method = value["method"]
            evidence_refs = tuple(value.get("evidence_refs", ()))
        except (KeyError, TypeError, ValueError) as exc:
            raise ProvenanceError(f"invalid {name} provenance: {exc}") from exc
        metrics[name] = MetricProvenance(
            derivation_class=derivation_class,
            producer=producer,
            method=method,
            evidence_refs=evidence_refs,
        )

    result = GateProvenance(metrics=metrics)
    result.validate()
    return result
