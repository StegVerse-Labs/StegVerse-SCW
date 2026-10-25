import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "tools" / "patient_owned_monitoring"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_schema_validator_accepts_reference():
    module = load("schema_validate")
    record = {
        "schema_version": "pom.reference.v1",
        "reference_id": "r1",
        "reference_type": "bp-cuff",
        "measurement_time_utc": "2026-07-21T10:00:00Z",
        "values": [{"name": "systolic", "value": 120, "unit": "mmHg"}],
    }
    assert module.validate(record) == []


def test_clock_fit_and_correction():
    module = load("clock_sync")
    anchors = [
        {"monotonic_tick": 0, "reference_time_utc": "2026-07-21T10:00:00Z"},
        {"monotonic_tick": 1_000_000, "reference_time_utc": "2026-07-21T10:00:01Z"},
        {"monotonic_tick": 2_000_000, "reference_time_utc": "2026-07-21T10:00:02Z"},
    ]
    model = module.fit_clock(anchors)
    assert abs(model.slope_seconds_per_tick - 0.000001) < 1e-12
    assert model.residual_rmse_ms < 0.001


def test_hematocrit_coordinate_calculation():
    module = load("hematocrit_image")
    result = module.calculate(0, 55, 100)
    assert result["hematocrit_percent"] == 45.0


def test_hemodynamic_baseline_and_relative_change():
    module = load("hemodynamic_features")
    rows = [
        {"time_utc": "2026-07-21T10:00:00Z", "pat_ms": "200", "ppg_amplitude": "1", "pulse_width_ms": "300", "heart_rate_bpm": "70"},
        {"time_utc": "2026-07-21T10:00:01Z", "pat_ms": "180", "ppg_amplitude": "0.8", "pulse_width_ms": "270", "heart_rate_bpm": "77"},
    ]
    base = module.baseline(rows[:1])
    derived = module.derive(rows, base)
    assert derived[0]["relative_change_index"] == 0
    assert round(derived[1]["pat_ms_pct"], 6) == -10.0
    assert round(derived[1]["ppg_amplitude_pct"], 6) == -20.0
