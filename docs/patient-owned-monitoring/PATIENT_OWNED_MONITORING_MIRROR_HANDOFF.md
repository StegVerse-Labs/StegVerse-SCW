# Patient-Owned Monitoring Mirror Handoff

_Last updated: 2026-07-21_

## Repository

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-SCW`
- Documentation path: `docs/patient-owned-monitoring/`
- Implementation path: `tools/patient_owned_monitoring/`
- Test path: `tests/patient_owned_monitoring/`
- Continuation authority: this file is the source of truth for the patient-owned monitoring build until superseded by a newer committed handoff.

## Purpose

Build a patient-owned, continuously recording health evidence system that preserves raw data, correlates multiple sensors, and validates every derived metric against a known reference device worn or operated at the same time.

The system is intended to support investigation of long warning periods and brief episodes by preserving synchronized evidence rather than reducing observations to summary scores.

## Active goal

Deliver the first executable engineering baseline for:

1. Continuous wearable ECG + PPG + IMU + temperature acquisition.
2. Experimental continuous hemodynamic-change detection and cuffless blood-pressure estimation.
3. Independent overnight PAP evidence capture: oxygen, pulse, respiration, mask pressure, humidity, body position, and awakening markers.
4. Glucose ingestion from a reference CGM or meter.
5. Low-cost saliva, urine, and finger-stick test capture.
6. A staged CBC research workstation beginning with hemoglobin, hematocrit, and standardized blood-smear imaging.
7. A validation framework based on simultaneous reference-device measurements, raw-data retention, error analysis, drift analysis, and explicit acceptance criteria.

## Operating rules

- Build what can be built.
- Preserve raw signals before calculating summaries.
- Every calculated or inferred metric must identify its source signals, algorithm version, calibration state, and validation status.
- Validation must use simultaneous paired measurements against a known reference device or laboratory result.
- Unknown, unmeasured, estimated, and validated values must remain distinct.
- No black-box score may replace exportable raw data.
- Device clocks must be synchronized and clock drift measured.
- Reference measurements must be timestamped and linked to the corresponding raw-signal window.
- Calibration data must never be mixed silently with validation data.
- Personal baselines and population models must be versioned separately.

## Completed foundation

- `SYSTEM_ARCHITECTURE.md` — system boundaries, modules, and data flow.
- `VALIDATION_PROTOCOL.md` — paired-reference validation design and acceptance framework.
- `DATA_SCHEMA.md` — raw-first open data contract.
- `HARDWARE_BOM.md` — revision A0 wearable, PAP, fluid dock, and CBC components.
- `PAP_EVIDENCE_MODULE.md` — channels, synchronization, validation sessions, and acceptance gates.
- `CBC_WORKSTATION.md` — staged hematocrit, hemoglobin, smear-imaging, and cell-counting plan.
- `tools/patient_owned_monitoring/reference_pairing.py` — executable JSONL reference-pairing and validation metrics CLI.
- `tests/patient_owned_monitoring/fixtures/` — deterministic paired BP fixtures.
- `tests/patient_owned_monitoring/test_reference_pairing.py` — pairing, metric, partition, and integrity tests.

## Current executable capability

The reference-pairing CLI can:

- import `pom.reference.v1` and `pom.estimate.v1` JSON Lines records;
- pair the nearest estimate to each reference inside a defined tolerance;
- preserve calibration/development/validation/challenge partition labels;
- emit `pom.pairing.v1` records with SHA-256 integrity fields;
- calculate count, bias, MAE, RMSE, Pearson correlation, Bland–Altman limits, maximum absolute error, and average timestamp delta;
- hash source datasets and the generated validation report.

## Initial validation references

- Blood pressure: validated upper-arm cuff used during calibration and validation sessions.
- ECG and heart rate: clinical ECG or validated single-lead reference when available.
- Oxygen saturation: recording pulse oximeter used simultaneously.
- Glucose: commercial meter or CGM paired with timestamped readings.
- Hemoglobin and CBC: accredited laboratory result from the same sampling interval.
- PAP: machine SD-card export when accessible plus independent mask-pressure and oxygen capture.

## Required data labels

Every output must carry one of:

- `measured`
- `reference_measured`
- `calculated`
- `estimated`
- `experimentally_inferred`
- `validated_for_personal_trend`
- `validated_against_reference`

## Required execution order

1. Run the deterministic reference-pairing tests.
2. Add schema validation for manifests, references, estimates, pairings, features, events, and samples.
3. Build the wearable firmware recorder interface and simulated sensor source.
4. Add clock synchronization and drift-correction tooling.
5. Add signal-window extraction and quality scoring.
6. Add hemodynamic relative-change feature extraction before absolute BP modeling.
7. Build PAP-module import and nightly-report generation.
8. Build fluid-sample manifest, image calibration, and strip-reader tooling.
9. Build hematocrit image measurement and paired laboratory validation.
10. Add hardware bench receipts and real paired datasets without replacing synthetic fixtures.

## Known remaining files and modules

- `tools/patient_owned_monitoring/schema_validate.py`
- `tools/patient_owned_monitoring/clock_sync.py`
- `tools/patient_owned_monitoring/signal_window.py`
- `tools/patient_owned_monitoring/hemodynamic_features.py`
- `tools/patient_owned_monitoring/pap_report.py`
- `tools/patient_owned_monitoring/sample_manifest.py`
- `tools/patient_owned_monitoring/strip_reader.py`
- `tools/patient_owned_monitoring/hematocrit_image.py`
- firmware acquisition and append-only storage implementation;
- enclosure and wiring files;
- real reference-device and laboratory paired datasets;
- validation receipts from hardware bench runs.

Destination: `StegVerse-Labs/StegVerse-SCW`.

## Ownership

Continuation may be performed by any authorized session or automation that reads this handoff first and records changes, test evidence, calibration data, and validation receipts durably here.
