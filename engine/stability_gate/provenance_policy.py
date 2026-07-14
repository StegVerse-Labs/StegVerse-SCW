"""Policy evaluation for Stability Gate metric provenance."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from .provenance import DerivationClass, GateProvenance, METRIC_NAMES


class ProvenanceDecision(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    ELIGIBLE = "ELIGIBLE"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True)
class MetricAuthorityRule:
    allowed_classes: frozenset[DerivationClass]
    allowed_producers: frozenset[str] = frozenset()
    allowed_methods: frozenset[str] = frozenset()
    require_evidence_refs: bool = True

    def validate(self) -> None:
        if not self.allowed_classes:
            raise ValueError("allowed_classes must not be empty")
        if any(not value.strip() for value in self.allowed_producers):
            raise ValueError("allowed_producers must contain non-empty strings")
        if any(not value.strip() for value in self.allowed_methods):
            raise ValueError("allowed_methods must contain non-empty strings")


@dataclass(frozen=True)
class ProvenancePolicy:
    rules: Mapping[str, MetricAuthorityRule]
    allow_caller_asserted_in_dry_run: bool = True

    def validate(self) -> None:
        missing = sorted(set(METRIC_NAMES) - set(self.rules))
        extra = sorted(set(self.rules) - set(METRIC_NAMES))
        if missing:
            raise ValueError("missing provenance rules: " + ", ".join(missing))
        if extra:
            raise ValueError("unknown provenance rules: " + ", ".join(extra))
        for name in METRIC_NAMES:
            rule = self.rules[name]
            if not isinstance(rule, MetricAuthorityRule):
                raise ValueError(f"{name} rule must be MetricAuthorityRule")
            rule.validate()


@dataclass(frozen=True)
class ProvenancePolicyResult:
    decision: ProvenanceDecision
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def eligible_for_enforcement(self) -> bool:
        return self.decision is ProvenanceDecision.ELIGIBLE


def evaluate_provenance(
    provenance: GateProvenance,
    policy: ProvenancePolicy,
    *,
    dry_run: bool,
) -> ProvenancePolicyResult:
    try:
        provenance.validate()
        policy.validate()
    except ValueError as exc:
        return ProvenancePolicyResult(ProvenanceDecision.FAIL_CLOSED, (str(exc),))

    reasons: list[str] = []
    observe_only = False

    for name in METRIC_NAMES:
        metric = provenance.metrics[name]
        rule = policy.rules[name]

        if metric.derivation_class is DerivationClass.CALLER_ASSERTED:
            if dry_run and policy.allow_caller_asserted_in_dry_run:
                observe_only = True
                reasons.append(f"{name}: caller asserted")
                continue
            reasons.append(f"{name}: caller asserted is not enforcement eligible")
            return ProvenancePolicyResult(
                ProvenanceDecision.FAIL_CLOSED,
                tuple(reasons),
            )

        if metric.derivation_class not in rule.allowed_classes:
            reasons.append(
                f"{name}: derivation class {metric.derivation_class.value} not allowed"
            )
        if rule.allowed_producers and metric.producer not in rule.allowed_producers:
            reasons.append(f"{name}: producer {metric.producer!r} not authorized")
        if rule.allowed_methods and metric.method not in rule.allowed_methods:
            reasons.append(f"{name}: method {metric.method!r} not authorized")
        if rule.require_evidence_refs and not metric.evidence_refs:
            reasons.append(f"{name}: evidence references required")

    if reasons and not observe_only:
        return ProvenancePolicyResult(ProvenanceDecision.FAIL_CLOSED, tuple(reasons))
    if reasons:
        return ProvenancePolicyResult(ProvenanceDecision.OBSERVE_ONLY, tuple(reasons))
    return ProvenancePolicyResult(ProvenanceDecision.ELIGIBLE, ())


def default_dry_run_policy() -> ProvenancePolicy:
    rule = MetricAuthorityRule(
        allowed_classes=frozenset(
            {DerivationClass.DERIVED, DerivationClass.RECONSTRUCTED}
        ),
        require_evidence_refs=True,
    )
    return ProvenancePolicy(rules={name: rule for name in METRIC_NAMES})
