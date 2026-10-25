from __future__ import annotations

import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[2] / "tools" / "patient_owned_monitoring" / "image_calibration.py"
SPEC = importlib.util.spec_from_file_location("image_calibration", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ImageCalibrationTests(unittest.TestCase):
    def test_affine_calibration_recovers_reference_scale(self):
        pixels = [
            [[10, 20, 30], [10, 20, 30], [50, 60, 70], [50, 60, 70]],
            [[10, 20, 30], [10, 20, 30], [50, 60, 70], [50, 60, 70]],
            [[30, 40, 50], [30, 40, 50], [30, 40, 50], [30, 40, 50]],
        ]
        document = {
            "pixels": pixels,
            "calibration_patches": [
                {"patch_id": "dark", "region": [0, 0, 2, 2], "reference_rgb": [20, 40, 60]},
                {"patch_id": "light", "region": [2, 0, 4, 2], "reference_rgb": [100, 120, 140]},
            ],
            "sample_regions": [{"sample_id": "pad-1", "region": [0, 2, 4, 3]}],
        }
        result = MODULE.calibrate_document(document)
        corrected = result["samples"][0]["corrected_rgb"]
        self.assertEqual(tuple(round(value, 6) for value in corrected), (60.0, 80.0, 100.0))
        self.assertEqual(result["quality"]["patch_count"], 2)
        self.assertAlmostEqual(result["quality"]["maximum_channel_fit_rmse"], 0.0)

    def test_region_validation_rejects_empty_region(self):
        with self.assertRaises(ValueError):
            MODULE.mean_region([[[1, 2, 3]]], [0, 0, 0, 1])

    def test_unknown_is_not_replaced_by_zero(self):
        result = MODULE.calibrate_document({
            "pixels": [[[10, 10, 10], [20, 20, 20]]],
            "calibration_patches": [
                {"patch_id": "a", "region": [0, 0, 1, 1], "reference_rgb": [20, 20, 20]},
                {"patch_id": "b", "region": [1, 0, 2, 1], "reference_rgb": [40, 40, 40]},
            ],
        })
        self.assertEqual(result["samples"], [])


if __name__ == "__main__":
    unittest.main()
