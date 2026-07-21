from __future__ import annotations

import importlib.util
import math
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "tools" / "patient_owned_monitoring" / "reference_pairing.py"
SPEC = importlib.util.spec_from_file_location("reference_pairing", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

FIXTURES = Path(__file__).parent / "fixtures"


def test_pairs_nearest_estimates_within_tolerance() -> None:
    references = MODULE.load_jsonl(FIXTURES / "references.jsonl")
    estimates = MODULE.load_jsonl(FIXTURES / "estimates.jsonl")

    pairs = MODULE.pair_records(
        references,
        estimates,
        reference_name="systolic",
        estimate_type="systolic-bp",
        tolerance_seconds=30,
    )

    assert len(pairs) == 3
    assert [pair.time_delta_seconds for pair in pairs] == [5.0, 10.0, 20.0]


def test_metrics_are_deterministic() -> None:
    references = MODULE.load_jsonl(FIXTURES / "references.jsonl")
    estimates = MODULE.load_jsonl(FIXTURES / "estimates.jsonl")
    pairs = MODULE.pair_records(references, estimates, "systolic", "systolic-bp", 30)

    metrics = MODULE.compute_metrics(pairs, "systolic")

    assert metrics["count"] == 3
    assert math.isclose(metrics["bias"], -2 / 3, rel_tol=1e-9)
    assert math.isclose(metrics["mae"], 8 / 3, rel_tol=1e-9)
    assert metrics["rmse"] > metrics["mae"]
    assert metrics["correlation"] is not None
    assert metrics["bland_altman_lower"] < metrics["bias"] < metrics["bland_altman_upper"]


def test_pairing_record_carries_partition_and_hash() -> None:
    references = MODULE.load_jsonl(FIXTURES / "references.jsonl")
    estimates = MODULE.load_jsonl(FIXTURES / "estimates.jsonl")
    pair = MODULE.pair_records(references, estimates, "systolic", "systolic-bp", 30)[0]

    record = MODULE.build_pairing_record(pair, "validation")

    assert record["schema_version"] == "pom.pairing.v1"
    assert record["dataset_partition"] == "validation"
    assert record["quality_decision"] == "include"
    assert len(record["pairing_sha256"]) == 64
