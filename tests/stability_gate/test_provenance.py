import pytest

from engine.stability_gate.provenance import (
    DerivationClass,
    ProvenanceError,
    provenance_from_dict,
)


def complete_payload(derivation_class="CALLER_ASSERTED", evidence_refs=None):
    refs = [] if evidence_refs is None else evidence_refs
    return {
        name: {
            "derivation_class": derivation_class,
            "producer": "scw-test",
            "method": "fixture",
            "evidence_refs": refs,
        }
        for name in (
            "deliberation_capacity",
            "model_fidelity",
            "environmental_volatility",
            "action_magnitude",
        )
    }


def test_caller_asserted_provenance_can_have_no_evidence_refs():
    provenance = provenance_from_dict(complete_payload())
    assert (
        provenance.metrics["model_fidelity"].derivation_class
        is DerivationClass.CALLER_ASSERTED
    )


def test_derived_provenance_requires_evidence_refs():
    with pytest.raises(ProvenanceError):
        provenance_from_dict(complete_payload("DERIVED"))


def test_reconstructed_provenance_with_evidence_is_valid():
    provenance = provenance_from_dict(
        complete_payload("RECONSTRUCTED", ["artifacts/input/example.json"])
    )
    assert provenance.canonical_dict()["action_magnitude"]["evidence_refs"] == [
        "artifacts/input/example.json"
    ]


def test_missing_metric_provenance_is_rejected():
    payload = complete_payload()
    payload.pop("action_magnitude")
    with pytest.raises(ProvenanceError):
        provenance_from_dict(payload)
