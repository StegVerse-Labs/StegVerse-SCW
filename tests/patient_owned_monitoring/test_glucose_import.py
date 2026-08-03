import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[2] / "tools" / "patient_owned_monitoring" / "glucose_import.py"
spec = importlib.util.spec_from_file_location("glucose_import", MODULE)
glucose_import = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(glucose_import)


class GlucoseImportTests(unittest.TestCase):
    def make_source(self, content: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "readings.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_imports_and_normalizes_meter_records(self):
        source = self.make_source(
            "timestamp,value,unit\n"
            "2026-08-02T12:00:00-05:00,100,mg/dL\n"
            "2026-08-02T12:05:00-05:00,5.5,mmol/L\n"
        )
        rows = glucose_import.load_rows(source)
        records = glucose_import.import_records(
            rows,
            source_path=source,
            source_type="glucose-meter",
            partition="validation",
            output_label="reference-measured",
            manufacturer="Example",
            model="Meter",
            device_id="meter-1",
        )
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["normalized"], {"value": 100.0, "unit": "mg/dL"})
        self.assertAlmostEqual(records[1]["normalized"]["value"], 99.1001, places=4)
        self.assertEqual(records[1]["original"], {"value": 5.5, "unit": "mmol/L"})
        self.assertEqual(records[0]["dataset_partition"], "validation")
        self.assertEqual(records[0]["output_label"], "reference-measured")
        self.assertEqual(len(records[0]["record_sha256"]), 64)
        self.assertEqual(records[0]["provenance"]["source_sha256"], records[1]["provenance"]["source_sha256"])

    def test_zero_is_preserved_as_measured_zero(self):
        source = self.make_source("timestamp,value,unit\n2026-08-02T12:00:00Z,0,mg/dL\n")
        record = glucose_import.import_records(
            glucose_import.load_rows(source),
            source_path=source,
            source_type="cgm",
            partition="challenge",
            output_label="measured",
            manufacturer="",
            model="",
            device_id="",
        )[0]
        self.assertEqual(record["original"]["value"], 0.0)
        self.assertEqual(record["normalized"]["value"], 0.0)

    def test_rejects_timestamp_without_timezone(self):
        source = self.make_source("timestamp,value,unit\n2026-08-02T12:00:00,90,mg/dL\n")
        with self.assertRaises(ValueError):
            glucose_import.import_records(
                glucose_import.load_rows(source),
                source_path=source,
                source_type="glucose-meter",
                partition="calibration",
                output_label="measured",
                manufacturer="",
                model="",
                device_id="",
            )

    def test_rejects_unknown_units_and_partitions(self):
        source = self.make_source("timestamp,value,unit\n2026-08-02T12:00:00Z,90,unknown\n")
        with self.assertRaises(ValueError):
            glucose_import.import_records(
                glucose_import.load_rows(source),
                source_path=source,
                source_type="glucose-meter",
                partition="development",
                output_label="measured",
                manufacturer="",
                model="",
                device_id="",
            )
        with self.assertRaises(ValueError):
            glucose_import.import_records(
                [],
                source_path=source,
                source_type="glucose-meter",
                partition="production",
                output_label="measured",
                manufacturer="",
                model="",
                device_id="",
            )

    def test_json_object_requires_records_array(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "readings.json"
        path.write_text(json.dumps({"not_records": []}), encoding="utf-8")
        with self.assertRaises(ValueError):
            glucose_import.load_rows(path)


if __name__ == "__main__":
    unittest.main()
