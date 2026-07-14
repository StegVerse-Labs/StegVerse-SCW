"""Local deterministic Stability Gate for SCW execution-time evaluation."""

from .model import GateInput, GateInputError
from .policy import Decision, GatePolicy, GateResult, evaluate
from .provenance import (
    DerivationClass,
    GateProvenance,
    MetricProvenance,
    ProvenanceError,
    provenance_from_dict,
)

__all__ = [
    "Decision",
    "DerivationClass",
    "GateInput",
    "GateInputError",
    "GatePolicy",
    "GateProvenance",
    "GateResult",
    "MetricProvenance",
    "ProvenanceError",
    "evaluate",
    "provenance_from_dict",
]
