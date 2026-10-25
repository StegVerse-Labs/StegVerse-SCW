import json
import tempfile
import unittest
from pathlib import Path

from tools.patient_owned_monitoring.security_gate import build_receipt, scan_secrets, validate_risk_register


class SecurityGateTests(unittest.TestCase):
    def valid_register(self):
        return {
            "risk_policy": {
                "federal_floor_only": True,
                "critical_open_risks_block_activation": True,
                "high_open_risks_require_owner_and_release_condition": True,
                "exceptions_must_expire": True,
                "unknown_risk_state": None,
                "zero_means_measured_zero": True,
            },
            "risks": [{
                "risk_id": "R-1",
                "severity": "critical",
                "state": "BLOCKED_PENDING_EVIDENCE",
                "owner": "security-assurance-lane",
                "controls": ["encrypted-storage"],
                "evidence_required": ["encryption-test"],
                "release_condition": "Evidence is committed and verified",
            }],
            "exceptions": [],
        }

    def test_valid_register_passes(self):
        self.assertEqual(validate_risk_register(self.valid_register()), [])

    def test_indefinite_exception_fails(self):
        register = self.valid_register()
        register["exceptions"] = [{
            "exception_id": "E-1",
            "owner": "owner",
            "approved_by": "approver",
            "expires_at": "never",
            "compensating_control": "isolation",
        }]
        errors = validate_risk_register(register)
        self.assertTrue(any("cannot be indefinite" in error for error in errors))

    def test_secret_scan_detects_token(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            token = "ghp_" + "A" * 36
            (root / "bad.txt").write_text(token + "\n", encoding="utf-8")
            findings = scan_secrets(root)
            self.assertEqual(findings[0]["kind"], "github_token")

    def test_receipt_is_hashed_and_activation_remains_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            register_path = root / "risk.json"
            register_path.write_text(json.dumps(self.valid_register()), encoding="utf-8")
            receipt = build_receipt(register_path, root)
            self.assertEqual(receipt["status"], "COMPLETE")
            self.assertEqual(receipt["activation_state"], "BLOCKED_PENDING_EVIDENCE")
            self.assertEqual(len(receipt["receipt_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
