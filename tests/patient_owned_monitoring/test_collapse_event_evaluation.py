import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).parents[2] / "tools" / "patient_owned_monitoring" / "evaluate_collapse_events.py"
spec = importlib.util.spec_from_file_location("collapse_eval", path)
collapse_eval = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(collapse_eval)


class CollapseEventEvaluationTests(unittest.TestCase):
    def test_metrics(self):
        refs = [
            {"start_time_utc": "2026-08-02T12:00:10+00:00", "end_time_utc": "2026-08-02T12:00:30+00:00"},
            {"start_time_utc": "2026-08-02T12:01:00+00:00", "end_time_utc": "2026-08-02T12:01:20+00:00"},
        ]
        detections = [
            {"start_time_utc": "2026-08-02T12:00:12+00:00", "end_time_utc": "2026-08-02T12:00:28+00:00"},
            {"start_time_utc": "2026-08-02T12:01:04+00:00", "end_time_utc": "2026-08-02T12:01:18+00:00"},
            {"start_time_utc": "2026-08-02T12:01:40+00:00", "end_time_utc": "2026-08-02T12:01:50+00:00"},
        ]
        report = collapse_eval.evaluate(
            refs,
            detections,
            "2026-08-02T12:00:00+00:00",
            "2026-08-02T12:02:00+00:00",
            10,
        )
        self.assertEqual(report["counts"]["true_positives"], 2)
        self.assertEqual(report["counts"]["false_positives"], 1)
        self.assertEqual(report["metrics"]["sensitivity"], 1.0)
        self.assertAlmostEqual(report["metrics"]["mean_onset_delay_seconds"], 3.0)
        self.assertAlmostEqual(report["metrics"]["false_positive_rate_per_monitored_hour"], 30.0)

    def test_unknown_sensitivity_for_no_references(self):
        report = collapse_eval.evaluate([], [])
        self.assertIsNone(report["metrics"]["sensitivity"])
        self.assertEqual(report["status"], "COMPLETE")

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            collapse_eval.evaluate([
                {"start_time_utc": "2026-08-02T12:00:10+00:00", "end_time_utc": "2026-08-02T12:00:10+00:00"}
            ], [])


if __name__ == "__main__":
    unittest.main()
