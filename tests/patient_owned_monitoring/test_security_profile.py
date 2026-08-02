import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "patient_owned_monitoring"))

from validate_security_profile import validate


class SecurityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile_path = ROOT / "security" / "patient_owned_monitoring" / "security_profile.json"
        cls.profile = json.loads(cls.profile_path.read_text(encoding="utf-8"))

    def test_canonical_profile_passes(self):
        self.assertEqual(validate(self.profile), [])

    def test_missing_family_fails(self):
        altered = copy.deepcopy(self.profile)
        del altered["required_control_families"]["device_integrity"]
        errors = validate(altered)
        self.assertTrue(any("device_integrity" in error for error in errors))

    def test_indefinite_exception_fails(self):
        altered = copy.deepcopy(self.profile)
        altered["exception_contract"]["indefinite_exceptions_allowed"] = True
        errors = validate(altered)
        self.assertTrue(any("indefinite security exceptions" in error for error in errors))

    def test_unknown_remains_null(self):
        altered = copy.deepcopy(self.profile)
        altered["validation_semantics"]["unknown_value"] = 0
        errors = validate(altered)
        self.assertTrue(any("unknown_value" in error for error in errors))

    def test_missing_federal_floor_statement_fails(self):
        altered = copy.deepcopy(self.profile)
        altered["policy"] = "Apply reasonable security controls."
        errors = validate(altered)
        self.assertTrue(any("minimum floor" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
