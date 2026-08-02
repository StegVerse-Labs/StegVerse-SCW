from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools" / "patient_owned_monitoring"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from run_synthetic_pipeline import run
from waveform_features import load


class EndToEndPipelineTests(unittest.TestCase):
    def test_pipeline_produces_hashed_receipt_and_beats(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            receipt = run(output, duration=30, rate=100, heart_rate=72.0, seed=7)
            self.assertEqual(receipt["status"], "COMPLETE")
            self.assertEqual(receipt["outputs"]["sample_count"], 3000)
            self.assertGreater(receipt["outputs"]["beat_count"], 20)
            self.assertEqual(len(receipt["receipt_sha256"]), 64)
            self.assertEqual(len(receipt["integrity"]["acquisition_sha256"]), 64)
            self.assertEqual(len(receipt["integrity"]["beats_sha256"]), 64)
            acquisition = load(output / "synthetic_acquisition.jsonl")
            self.assertEqual(len(acquisition), 3000)
            stored = json.loads((output / "pipeline_receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["receipt_sha256"], receipt["receipt_sha256"])


if __name__ == "__main__":
    unittest.main()
