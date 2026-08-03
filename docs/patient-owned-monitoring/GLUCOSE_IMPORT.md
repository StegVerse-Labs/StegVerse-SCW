# Governed Glucose Import Contract

## Purpose

Import patient-owned glucose-meter and continuous-glucose-monitor records without discarding source units, timestamps, device identity, provenance, or dataset partition boundaries.

## Canonical implementation

- Importer: `tools/patient_owned_monitoring/glucose_import.py`
- Tests: `tests/patient_owned_monitoring/test_glucose_import.py`
- Output serialization: JSON Lines
- Record schema: `pom.glucose.v1`

## Required source fields

Every source row must provide:

- a timezone-aware measurement timestamp;
- a finite, non-negative glucose value;
- a supported unit: `mg/dL` or `mmol/L`.

CSV, JSON, JSONL, and NDJSON inputs are accepted. Field names may be mapped through command-line options.

## Required record fields

Each imported record preserves:

- original timestamp including its supplied offset;
- source type: `glucose-meter` or `cgm`;
- manufacturer, model, and device identifier when available;
- original value and unit;
- normalized value in `mg/dL`;
- output label: `measured` or `reference-measured`;
- isolated dataset partition: `calibration`, `development`, `validation`, or `challenge`;
- source path, source SHA-256, and source row index;
- importer name and version;
- per-record SHA-256.

## Integrity rules

- Unknown values remain absent or null; they are never converted to zero.
- A measured value of zero remains zero.
- Naive timestamps without a UTC offset are rejected.
- Unsupported units and partitions are rejected.
- Original values and units are never overwritten by normalized values.
- Synthetic and imported records may not be represented as clinical or laboratory validation without a separate simultaneous reference record and pairing decision.
- Calibration, development, validation, and challenge records may not be silently mixed.

## Normalization

`mmol/L` values are converted to `mg/dL` using the explicit factor `18.0182`. The original value and unit remain in every output record.

## Validation state

The importer and deterministic tests are installed. They remain `IMPLEMENTED_BUT_UNVALIDATED` until repository-native CI execution, job logs, and artifact evidence are inspected.
