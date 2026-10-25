from tools.patient_owned_monitoring.simulated_acquisition import generate
from tools.patient_owned_monitoring.waveform_features import extract
from tools.patient_owned_monitoring.collapse_detector import detect


def test_simulated_acquisition_count():
    session, rows = generate(duration_s=2, sample_rate=50, heart_rate=60, seed=1)
    assert session
    assert len(rows) == 100
    assert rows[0]["sequence"] == 0
    assert rows[-1]["sequence"] == 99


def test_waveform_extraction_from_generated_rows():
    _, rows = generate(duration_s=8, sample_rate=100, heart_rate=60, seed=2)
    csv_rows = [{k: str(v) for k, v in r.items()} for r in rows]
    beats = extract(csv_rows)
    assert len(beats) >= 5
    pats = [b["pulse_arrival_time_ms"] for b in beats if b["pulse_arrival_time_ms"] >= 0]
    assert pats


def test_sustained_collapse_candidate():
    rows = [
        {"time_utc": f"2026-07-21T12:00:{i:02d}+00:00", "relative_change_index": str(3.0 if 2 <= i <= 8 else 0.5)}
        for i in range(12)
    ]
    events = detect(rows, threshold=2.5, min_seconds=5)
    assert len(events) == 1
    assert events[0]["duration_seconds"] >= 5
