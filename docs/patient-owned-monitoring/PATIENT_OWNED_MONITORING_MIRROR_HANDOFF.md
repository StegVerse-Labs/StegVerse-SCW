# Patient-Owned Monitoring Mirror Handoff

_Last updated: 2026-07-21_

## Repository

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-SCW`
- Documentation: `docs/patient-owned-monitoring/`
- Implementation: `tools/patient_owned_monitoring/`
- Tests: `tests/patient_owned_monitoring/`
- Continuation authority: this file is the source of truth until superseded by a newer committed handoff.

## Purpose

Build a patient-owned, continuously recording health-evidence system that preserves synchronized raw data and validates derived metrics against known reference devices or laboratory results collected at the same time.

## Operating rules

- Build what can be built.
- Preserve raw signals before summaries.
- Keep measured, reference-measured, calculated, estimated, experimentally inferred, personal-trend validated, and reference-validated values distinct.
- Preserve original timestamps and measured clock correction.
- Never mix calibration and validation partitions silently.
- Retain algorithm, hardware, firmware, calibration, source hashes, and quality decisions with every output.

## Completed architecture and specifications

- `SYSTEM_ARCHITECTURE.md`
- `VALIDATION_PROTOCOL.md`
- `DATA_SCHEMA.md`
- `HARDWARE_BOM.md`
- `PAP_EVIDENCE_MODULE.md`
- `CBC_WORKSTATION.md`

## Completed executable modules

- `reference_pairing.py` — simultaneous reference pairing and bias, MAE, RMSE, correlation, Bland-Altman, timing, and integrity reporting.
- `schema_validate.py` — core evidence-record validation.
- `clock_sync.py` — clock-drift fitting and correction with residuals.
- `signal_window.py` — time-window extraction and coverage, clipping, flatline, and motion scoring.
- `hemodynamic_features.py` — personal-baseline PAT, PPG amplitude, pulse-width, and heart-rate changes.
- `pap_report.py` — nightly PAP evidence summary and threshold intervals.
- `hematocrit_image.py` — reviewed-coordinate hematocrit calculation.
- `simulated_acquisition.py` — synchronized synthetic ECG, PPG, motion, temperature, contact-pressure, append-only records, and per-record hashes.
- `waveform_features.py` — transparent ECG peak, PPG foot, heart-rate, and pulse-arrival-time extraction.
- `stream_align.py` — cross-stream common-grid alignment and timing-quality report.
- `collapse_detector.py` — sustained personal-baseline hemodynamic-change candidate events.
- `sample_manifest.py` — hashed append-only saliva, urine, capillary-blood, smear, and microhematocrit records.
- `strip_reader.py` — fixed-light calibrated RGB strip-pad interpretation.
- `pap_event_correlation.py` — awakening or mouth-opening windows correlated with oxygen, pulse, mask pressure, humidity, respiration, and jaw-position evidence.

## Completed tests and fixtures

- deterministic paired blood-pressure fixtures;
- `test_reference_pairing.py`;
- `test_processing_pipeline.py`;
- `test_acquisition_and_detection.py`.

The tests are committed but still require execution in a checked-out repository. No execution receipt is claimed yet.

## Current executable capability

The project can generate raw synthetic wearable evidence, preserve it append-only, validate records, fit clock drift, align streams, extract ECG/PPG beat timing, calculate relative hemodynamic features, detect sustained candidate events, pair outputs with simultaneous references, generate PAP nightly and event-centered reports, create fluid-sample manifests, interpret calibrated strip colors, and calculate reviewed-coordinate hematocrit.

## Required next execution order

1. Run the full deterministic test suite and commit the receipt.
2. Add an end-to-end synthetic pipeline command that chains acquisition through event detection and reference validation.
3. Add evaluation metrics for collapse-event sensitivity, false-positive rate, onset delay, and coverage.
4. Add semi-automatic hematocrit boundary proposals while retaining operator-reviewed coordinates.
5. Add fixed-light image geometry and calibration-card processing for strip images.
6. Add firmware interfaces matching the append-only recorder contract.
7. Add enclosure drawings, wiring maps, power-budget measurements, and bench receipts.
8. Import real simultaneous cuff, ECG, pulse-oximeter, PAP, glucose, hemoglobin, hematocrit, and CBC references without replacing synthetic fixtures.
9. Train and validate personal BP-change and collapse models using isolated calibration, development, validation, and challenge partitions.

## Remaining physical validation

- actual sensors and recorder hardware;
- firmware and device drivers;
- enclosure and charging system;
- simultaneous reference-device datasets;
- laboratory-paired CBC datasets;
- hardware clock, battery, thermal, dropout, contact, motion, and continuous-wear receipts.

Destination: `StegVerse-Labs/StegVerse-SCW`.

## Ownership

Continuation may be performed by any authorized session or automation that reads this handoff first and records code, tests, calibration data, paired datasets, and validation receipts durably here.
