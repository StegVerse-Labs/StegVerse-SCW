import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / "tools" / "patient_owned_monitoring" / "hematocrit_boundaries.py"
spec = importlib.util.spec_from_file_location("hematocrit_boundaries", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class HematocritBoundaryTests(unittest.TestCase):
    def test_proposal_preserves_review_requirement(self):
        profile = []
        profile.extend([[8, 8, 8]] * 2)
        profile.extend([[120, 35, 30]] * 8)
        profile.extend([[210, 205, 150]] * 10)
        reviewed = {
            "tube_start_index": 2,
            "packed_cell_plasma_boundary_index": 10,
            "profile_end_index": 19,
        }
        result = mod.analyze({"profile": profile, "reviewed_coordinates": reviewed})
        proposal = result["proposal"]
        self.assertTrue(result["review_required"])
        self.assertEqual(result["effective_coordinates"], reviewed)
        self.assertEqual(proposal["packed_cell_plasma_boundary_index"], 10)
        self.assertAlmostEqual(proposal["proposed_hematocrit_fraction"], 8 / 18)
        self.assertEqual(result["output_label"], "experimentally_inferred")

    def test_unreviewed_proposal_never_becomes_effective(self):
        profile = [[100, 30, 25]] * 6 + [[220, 215, 160]] * 6
        result = mod.analyze({"profile": profile})
        self.assertIsNone(result["reviewed_coordinates"])
        self.assertIsNone(result["effective_coordinates"])
        self.assertTrue(result["review_required"])

    def test_short_profile_rejected(self):
        with self.assertRaises(ValueError):
            mod.analyze({"profile": [[1, 2, 3]] * 5})


if __name__ == "__main__":
    unittest.main()
