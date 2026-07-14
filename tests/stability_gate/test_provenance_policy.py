from engine.stability_gate.provenance import provenance_from_dict
from engine.stability_gate.provenance_policy import (
    MetricAuthorityRule,
    ProvenanceDecision,
    ProvenancePolicy,
    default_dry_run_policy,
    evaluate_provenance,
)
from engine.stability_gate.provenance import DerivationClass, METRIC_NAMES


def payload(derivation_class, producer="scw", method="fixture", refs=None):
    refs = [] if refs is None else refs
    return {
        name: {
            "derivation_class": derivation_class,
            "producer": producer,
            "method": method,
            "evidence_refs": refs,
        }
        for name in METRIC_NAMES
    }


def test_caller_asserted_is_observe_only_in_dry_run():
    result = evaluate_provenance(
        provenance_from_dict(payload("CALLER_ASSERTED")),
        default_dry_run_policy(),
        dry_run=True,
    )
    assert result.decision is ProvenanceDecision.OBSERVE_ONLY
    assert not result.eligible_for_enforcement


def test_caller_asserted_fails_closed_for_enforcement():
    result = evaluate_provenance(
        provenance_from_dict(payload("CALLER_ASSERTED")),
        default_dry_run_policy(),
        dry_run=False,
    )
    assert result.decision is ProvenanceDecision.FAIL_CLOSED


def test_reconstructed_with_authorized_producer_and_method_is_eligible():
    rule = MetricAuthorityRule(
        allowed_classes=frozenset({DerivationClass.RECONSTRUCTED}),
        allowed_producers=frozenset({"authorized-engine"}),
        allowed_methods=frozenset({"canonical-v1"}),
    )
    policy = ProvenancePolicy(rules={name: rule for name in METRIC_NAMES})
    result = evaluate_provenance(
        provenance_from_dict(
            payload(
                "RECONSTRUCTED",
                producer="authorized-engine",
                method="canonical-v1",
                refs=["artifacts/input/example.json"],
            )
        ),
        policy,
        dry_run=False,
    )
    assert result.decision is ProvenanceDecision.ELIGIBLE
    assert result.eligible_for_enforcement


def test_unauthorized_producer_fails_closed():
    rule = MetricAuthorityRule(
        allowed_classes=frozenset({DerivationClass.DERIVED}),
        allowed_producers=frozenset({"authorized-engine"}),
    )
    policy = ProvenancePolicy(rules={name: rule for name in METRIC_NAMES})
    result = evaluate_provenance(
        provenance_from_dict(
            payload("DERIVED", producer="unknown", refs=["evidence.json"])
        ),
        policy,
        dry_run=False,
    )
    assert result.decision is ProvenanceDecision.FAIL_CLOSED
    assert any("not authorized" in reason for reason in result.reasons)
