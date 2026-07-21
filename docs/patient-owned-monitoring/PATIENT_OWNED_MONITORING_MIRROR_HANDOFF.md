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

The system supports investigation of long warning periods and brief episodes by preserving synchronized evidence rather than reducing observations to summary scores.

## Active goal

Deliver an executable engineering baseline for:

1. Continuous wearable ECG + PPG + IMU + temperature acquisition.
2. Experimental continuous hemodynamic-change detection and cuffless blood-pressure estimation.
3. Independent overnight PAP evidence capture: oxygen, pulse, respiration, mask pressure, humidity, body position, and awakening markers.
4. Glucose ingestion from a reference CGM or meter.
5. Low-cost saliva, urine, and finger-stick test capture.
6. A staged CBC research workstation beginning with hemoglobin, hematocrit, and standardized blood-smear imaging.
7. Validation through simultaneous reference-device measurements, raw-data retention, error analysis, drift analysis, and explicit acceptance criteria.

## Operating rules

- Build what can be built.
- Preserve raw signals before calculating summaries.
- Every calculated or inferred metric identifies source signals, algorithm version, calibration state, and validation status.
- Validation uses simultaneous paired measurements against a known reference device or laboratory result.
- Unknown, unmeasured, estimated, and validated values remain distinct.
- No black-box score replaces exportable raw data.
- Device clocks are synchronized and clock drift is measured.
- Reference measurements are timestamped and linked to the corresponding raw-signal window.
- Calibration data is never mixed silently with validation data.
- Personal baselines and population models are versioned separately.

## Completed foundation

- `SYSTEM_ARCHITECTURE.md` — system boundaries, modules, and data flow.
- `VALIDATION_PROTOCOL.md` — paired-reference validation design and acceptance framework.
- `DATA_SCHEMA.md` — raw-first open data contract.
- `HARDWARE_BOM.md` — revision A0 wearable, PAP, fluid dock, and CBC components.
- `PAP_EVIDENCE_MODULE.md` — channels, synchronization, validation sessions, and acceptance gates.
- `CBC_WORKSTATION.md` — staged hematocrit, hemoglobin, smear-imaging, and cell-counting plan.
- `reference_pairing.py` — paired reference/estimate validation and metrics.
- `schema_validate.py` — schema and field validation for core POM records.
- `clock_sync.py` — linear drift fitting, residual reporting, and timestamp correction.
- `signal_window.py` — timestamp-window extraction with coverage, flatline, clipping, and motion quality scoring.
- `hemodynamic_features.py` — personal-baseline PAT, PPG amplitude, pulse-width, and heart-rate relative-change features.
- `pap_report.py` — nightly raw-linked summaries and threshold event extraction.
- `hematocrit_image.py` — axis-coordinate packed-cell fraction measurement.
- deterministic BP fixtures and automated reference-pairing tests.
- `test_processing_pipeline.py` — unit tests for schema validation, clock fitting, hematocrit, and hemodynamic features.

## Current executable capability

The module can now:

- validate core JSON and JSONL evidence records;
- fit a clock model from simultaneous timing anchors and preserve residual error;
- extract bounded signal windows from CSV streams;
- score coverage, flatline, clipping, and motion quality;
- create transparent relative hemodynamic features against a personal baseline;
- pair estimates with reference readings and calculate bias, MAE, RMSE, Pearson correlation, Bland–Altman limits, maximum error, and timing offset;
- produce independent nightly PAP summaries linked to source hashes;
- identify oxygen-below-90 and low-mask-humidity intervals from synchronized PAP evidence;
- calculate hematocrit from explicit capillary-image coordinates;
- preserve calibration/development/validation/challenge partitions.

## Initial validation references

- Blood pressure: validated upper-arm cuff during calibration and validation sessions.
- ECG and heart rate: clinical ECG or validated single-lead reference when available.
- Oxygen saturation: recording pulse oximeter worn simultaneously.
- Glucose: commercial meter or CGM paired with timestamped readings.
- Hemoglobin and CBC: accredited laboratory result from the same sampling interval.
- PAP: machine SD-card export when accessible plus independent mask-pressure and oxygen capture.

## Required data labels

Every output carries one of:

- `measured`
- `reference_measured`
- `calculated`
- `estimated`
- `experimentally_inferred`
- `validated_for_personal_trend`
- `validated_against_reference`

## Required execution order

1. Run all deterministic unit tests in a checked-out repository and record the receipt.
2. Add simulated wearable acquisition and append-only recorder output.
3. Add beat detection and ECG-to-PPG pulse-arrival-time extraction from raw waveforms.
4. Add cross-stream resampling and alignment-quality reports.
5. Add personal hemodynamic-collapse event detection using validated relative features.
6. Add fluid-sample manifests, fixed-light image calibration, and strip-reader tooling.
7. Add semi-automatic capillary boundary detection while retaining reviewed coordinates.
8. Add nightly PAP event correlation around awakenings and mouth-opening markers.
9. Add hardware enclosure, wiring, and bench-test receipts.
10. Add real simultaneous reference-device and laboratory datasets without replacing synthetic fixtures.

## Known remaining files and modules

- simulated acquisition and append-only storage implementation;
- raw ECG/PPG beat and pulse-arrival-time extraction;
- cross-stream resampling/alignment tooling;
- hemodynamic-collapse detector and evaluation harness;
- `sample_manifest.py`;
- fixed-light image calibration and `strip_reader.py`;
- automatic hematocrit boundary proposal;
- PAP event-correlation report;
- firmware, enclosure, and wiring files;
- real paired datasets and hardware validation receipts.

Destination: `StegVerse-Labs/StegVerse-SCW`.

## Ownership

Continuation may be performed by any authorized session or automation that reads this handoff first and records changes, test evidence, calibration data, and validation receipts durably here.
