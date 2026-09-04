import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "scripts" / "capture_workstation_incident.py"
CORRELATE = ROOT / "scripts" / "correlate_workstation_incidents.py"
PROJECT = ROOT / "scripts" / "project_workstation_incident.py"
FIXTURE = ROOT / "data" / "workstation-incidents" / "WGI-chatgpt-ios-plus-control-20260904.json"


class WorkstationIncidentTests(unittest.TestCase):
    def test_fixture_preserves_semantic_boundaries(self):
        record = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "OBSERVED")
        self.assertEqual(record["root_cause"]["state"], "UNKNOWN")
        self.assertEqual(record["workaround"]["state"], "OBSERVED_SUCCESS")
        self.assertEqual(record["fix"]["state"], "UNKNOWN")

    def test_capture_creates_local_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CAPTURE),
                    "--product",
                    "ExampleApp",
                    "--platform",
                    "iOS",
                    "--surface",
                    "composer",
                    "--category",
                    "UI",
                    "--summary",
                    "Control disappeared",
                    "--observed-behavior",
                    "No attachment control",
                    "--workaround",
                    "Restart app",
                    "--output-dir",
                    tmp,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            path = Path(proc.stdout.strip())
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(record["schema"], "stegverse.workstation-incident/v1")
            self.assertEqual(record["root_cause"]["state"], "UNKNOWN")
            self.assertFalse(record["provenance"]["public_projection_allowed"])

    def test_public_projection_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            incident = Path(tmp) / "incident.json"
            record = json.loads(FIXTURE.read_text(encoding="utf-8"))
            record["provenance"]["public_projection_allowed"] = False
            incident.write_text(json.dumps(record), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(PROJECT), str(incident), "--public"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 3)
            self.assertIn("denied", proc.stderr)

    def test_correlation_emits_candidates_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = json.loads(FIXTURE.read_text(encoding="utf-8"))
            first = Path(tmp) / "a.json"
            second = Path(tmp) / "b.json"
            first.write_text(json.dumps(base), encoding="utf-8")
            base["incident_id"] = "WGI-second"
            second.write_text(json.dumps(base), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CORRELATE),
                    "--incident-dir",
                    tmp,
                    "--threshold",
                    "0.1",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(len(result["matches"]), 1)
            self.assertGreater(result["matches"][0]["score"], 0)


if __name__ == "__main__":
    unittest.main()
