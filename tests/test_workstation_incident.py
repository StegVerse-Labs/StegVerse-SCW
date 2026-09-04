import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "scripts" / "capture_workstation_incident.py"
CORRELATE = ROOT / "scripts" / "correlate_workstation_incidents.py"
CORRELATION_DECISION = ROOT / "scripts" / "accept_workstation_incident_correlation.py"
PROJECT = ROOT / "scripts" / "project_workstation_incident.py"
TRANSITION = ROOT / "scripts" / "apply_workstation_incident_transition.py"
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

    def test_correlation_decision_is_append_only_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            second = Path(tmp) / "second.json"
            base = json.loads(FIXTURE.read_text(encoding="utf-8"))
            first.write_text(json.dumps(base), encoding="utf-8")
            base["incident_id"] = "WGI-second"
            second.write_text(json.dumps(base), encoding="utf-8")
            output_dir = Path(tmp) / "decisions"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CORRELATION_DECISION),
                    str(first),
                    str(second),
                    "--score",
                    "0.8",
                    "--decision",
                    "RELATED",
                    "--relationship",
                    "SAME_PRESENTATION",
                    "--reason",
                    "same user-visible symptom",
                    "--actor-type",
                    "SYSTEM",
                    "--actor-id",
                    "test",
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            decision_path = Path(proc.stdout.strip())
            decision = json.loads(decision_path.read_text(encoding="utf-8"))
            self.assertEqual(decision["decision"], "RELATED")
            self.assertEqual(decision["relationship"], "SAME_PRESENTATION")
            self.assertEqual(decision["evidence_refs"], [])
            self.assertEqual(
                json.loads(first.read_text(encoding="utf-8"))["status"],
                "OBSERVED",
            )

    def test_same_root_cause_correlation_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            second = Path(tmp) / "second.json"
            base = json.loads(FIXTURE.read_text(encoding="utf-8"))
            first.write_text(json.dumps(base), encoding="utf-8")
            base["incident_id"] = "WGI-second"
            second.write_text(json.dumps(base), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CORRELATION_DECISION),
                    str(first),
                    str(second),
                    "--score",
                    "0.9",
                    "--decision",
                    "RELATED",
                    "--relationship",
                    "SAME_ROOT_CAUSE",
                    "--reason",
                    "candidate root cause match",
                    "--actor-type",
                    "SME",
                    "--actor-id",
                    "test",
                    "--output-dir",
                    str(Path(tmp) / "decisions"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)

    def test_transition_emits_receipt_and_updates_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            incident = Path(tmp) / "incident.json"
            transition_dir = Path(tmp) / "transitions"
            incident.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(TRANSITION),
                    str(incident),
                    "--to",
                    "CORRELATED",
                    "--actor",
                    "test",
                    "--reason",
                    "candidate match accepted for review",
                    "--transition-dir",
                    str(transition_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            receipt_path = Path(proc.stdout.strip())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            updated = json.loads(incident.read_text(encoding="utf-8"))
            self.assertEqual(receipt["from_status"], "OBSERVED")
            self.assertEqual(receipt["to_status"], "CORRELATED")
            self.assertFalse(receipt["authority_effect"])
            self.assertEqual(updated["status"], "CORRELATED")

    def test_strong_transition_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            incident = Path(tmp) / "incident.json"
            record = json.loads(FIXTURE.read_text(encoding="utf-8"))
            record["status"] = "REPRODUCED"
            record["root_cause"]["state"] = "CONFIRMED"
            record["root_cause"]["evidence_refs"] = ["evidence:root-cause"]
            incident.write_text(json.dumps(record), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(TRANSITION),
                    str(incident),
                    "--to",
                    "ROOT_CAUSED",
                    "--actor",
                    "test",
                    "--reason",
                    "root cause review",
                    "--transition-dir",
                    str(Path(tmp) / "transitions"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
