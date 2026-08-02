# Patient-Owned Monitoring Mirror Handoff

_Last updated: 2026-08-02T16:28:00-05:00_

## Canonical authority

- Goal ID: `POM-001`
- Active goal: build, validate, and activate a patient-owned continuous health-evidence system.
- Originating session goal: create devices and home-test tooling that preserve detailed raw evidence and validate every derived measurement against a reliable simultaneous reference.
- Organization/repository: `StegVerse-Labs/StegVerse-SCW`
- Branch: `main`
- Documentation: `docs/patient-owned-monitoring/`
- Implementation: `tools/patient_owned_monitoring/`
- Tests: `tests/patient_owned_monitoring/`
- Claims and machine state: `docs/patient-owned-monitoring/TASK_REGISTRY.json`
- Session inventory: `docs/patient-owned-monitoring/SESSION_EXECUTION_INVENTORY.md`
- Canonical owner: this repository workstream; no competing handoff or duplicate validation workflow is authorized.

## Active claims

- `POM-SW-001`: `CLAIMED_FOR_VALIDATION`; owner `repository-native-ci`; release condition is an inspected latest-main workflow run, job logs, and receipt artifact, or a durable FAILED/BLOCKED record from observed evidence.
- `POM-HW-001`: `BLOCKED`; owner `hardware-bench-lane`; release condition is component availability and the first committed bench capture.
- `POM-VAL-REAL-001`: `BLOCKED`; owner `paired-reference-validation-lane`; release condition is a synchronized physical or fluid-test dataset with reliable reference measurements.

No competing implementation claim was found. Remaining software tasks are enumerated in `TASK_REGISTRY.json`.

## Governing requirements

- Build what can be built and preserve executable engineering paths.
- Preserve raw signals before summaries.
- Validate each measurement for its stated purpose against a reliable simultaneous device or laboratory result.
- Keep measured, reference-measured, calculated, estimated, experimentally inferred, personal-trend validated, and reference-validated values distinct.
- Preserve original timestamps, clock correction, algorithm versions, hardware and firmware versions, calibration IDs, source hashes, and quality decisions.
- Keep calibration, development, validation, and challenge partitions isolated.
- Zero is a measured value; unknown or untracked values never become zero.
- PAP evidence must remain independently collectable when clinic exports are unavailable.
- Algorithmic image boundaries are proposals only; reviewed coordinates remain the only effective coordinates.

## Authoritative specifications

- `SYSTEM_ARCHITECTURE.md`
- `VALIDATION_PROTOCOL.md`
- `DATA_SCHEMA.md`
- `HARDWARE_BOM.md`
- `PAP_EVIDENCE_MODULE.md`
- `CBC_WORKSTATION.md`

## Implemented software

- `reference_pairing.py` — simultaneous reference pairing and error metrics.
- `schema_validate.py` — core evidence-record validation.
- `clock_sync.py` — clock-drift fitting and timestamp correction.
- `signal_window.py` — bounded extraction and signal-quality metrics.
- `hemodynamic_features.py` — transparent relative hemodynamic features.
- `pap_report.py` — nightly PAP evidence summaries and threshold intervals.
- `hematocrit_image.py` — reviewed-coordinate hematocrit calculation.
- `simulated_acquisition.py` — deterministic synthetic ECG, PPG, motion, temperature, contact pressure, append-only records, and hashes.
- `waveform_features.py` — ECG/PPG extraction from CSV or recorder JSONL; commit `1024d6136edbab245e0fc28cf107777e73573563` repaired the format mismatch.
- `stream_align.py` — cross-stream alignment and timing-quality reporting.
- `collapse_detector.py` — sustained personal-baseline candidate events.
- `sample_manifest.py` — hashed append-only fluid and capillary-sample records.
- `strip_reader.py` — calibrated RGB interpretation.
- `pap_event_correlation.py` — event-centered PAP evidence windows.
- `run_synthetic_pipeline.py` — deterministic acquisition-to-beat-extraction pipeline with hashed receipt; commit `63a22d723cdd4efe4a23229544a3607a71d781fd`.
- `evaluate_collapse_events.py` — event sensitivity, false-positive rate, onset delay, overlap, and coverage; commit `d084ea539b6f80cb436e327a541fd97757aa6793`.
- `image_calibration.py` — fixed-light calibration, corrected sample-region RGB, fit RMSE, source hashing, and fail-closed geometry checks; commit `fb18f5da1fc7d7f8b932b299bea72ccc43027f0c`.
- `hematocrit_boundaries.py` — transparent red-dominance gradient proposals from a profile or image region, source hashing, confidence evidence, and mandatory operator review; commit `83cf15497c3c56a7ef3e66580eacd9ae3acea830`.

## Tests and automation

- deterministic paired blood-pressure fixtures;
- `test_reference_pairing.py`;
- `test_processing_pipeline.py`;
- `test_acquisition_and_detection.py`;
- `test_end_to_end_pipeline.py`;
- `test_collapse_event_evaluation.py`; commit `ee9bf5f47510d2756ce4a71f1465d140ddee90d2`;
- `test_image_calibration.py`; commit `46c599bef1ac65d47a6ab40eafbbd912498c14f5`;
- `test_hematocrit_boundaries.py`; commit `7e015cb493014aafdec979112559e573aa0eec9f`;
- `.github/workflows/patient-owned-monitoring-validation.yml`; commit `6da51bcdd2902181f2c025fcf3b9dc9255b20651`.

The workflow compiles modules, runs deterministic tests, executes the synthetic pipeline, validates the receipt, and uploads evidence for 90 days. Workflow success is not claimed because no run, job log, or artifact has yet been directly inspected.

## Task and consolidation records

- `TASK_REGISTRY.json`; latest update commit `d3721385492674d9e786c40af1dd104697d3b572`.
- `SESSION_EXECUTION_INVENTORY.md`; commit `db864abbaad6ec65e40d61d3bb58d3b7a02392e5`.

All unique session requirements remain transferred into this canonical workstream. The historical discussion of MaxAlert, white-cross tablets, ephedrine, and ma-huang created no repository implementation obligation.

## Current classifications

- Architecture/specifications: `COMPLETE` as design artifacts; physical conformance unvalidated.
- Software processing modules: `IMPLEMENTED_BUT_PARTIALLY_UNVALIDATED`.
- Synthetic pipeline: `IMPLEMENTED_BUT_UNVALIDATED_BY_CI`.
- Collapse-event evaluator: `IMPLEMENTED_BUT_UNVALIDATED_BY_CI`.
- Fixed-light image calibration: `IMPLEMENTED_BUT_UNVALIDATED_BY_CI`.
- Hematocrit boundary proposals: `IMPLEMENTED_BUT_UNVALIDATED_BY_CI`; proposals never become effective without reviewed coordinates.
- Repository-native CI: `CLAIMED_FOR_VALIDATION`.
- Physical wearable/PAP recorder: `BLOCKED` by hardware-bench release condition.
- Real device and laboratory pairing: `BLOCKED` by synchronized dataset release condition.
- Site, Publisher, wiki, release, and deployment propagation: `NOT_REQUIRED` until validated evidence or a release candidate exists.

## Exact next execution order

1. Inspect the run, jobs, logs, and artifact produced by `.github/workflows/patient-owned-monitoring-validation.yml`; reconcile `POM-SW-001` and commit a receipt under `docs/patient-owned-monitoring/receipts/`.
2. Implement `tools/patient_owned_monitoring/glucose_import.py` for timestamped meter and CGM records with provenance, units, and partition labels.
3. Create firmware interfaces, wiring maps, enclosure files, and bench receipt templates under `hardware/patient_owned_monitoring/`.
4. Commit real synchronized datasets under governed data/custody locations without replacing synthetic fixtures.
5. Run isolated calibration, development, validation, and challenge evaluations before activating personal BP-change or collapse models.

## Validation commands

```bash
python -m compileall -q tools/patient_owned_monitoring tests/patient_owned_monitoring
python -m unittest discover -s tests/patient_owned_monitoring -p 'test_*.py' -v
python tools/patient_owned_monitoring/run_synthetic_pipeline.py artifacts/patient-owned-monitoring --duration 60 --rate 100 --heart-rate 72 --seed 7
```

## Cross-repository dependencies and propagation

No external repository currently owns this capability. `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `admissibility-wiki`, `stegguardian-wiki`, and `master-records` receive no propagation claim until a validated evidence release or explicit contract exists. Local canonical authority prevents premature duplication.

## Machine-owned continuation

The validation workflow is the active machine-owned task. It has deterministic inputs, persists artifacts, fails when tests or receipt checks fail, and records repository/run metadata. Absence of observed evidence is not success.

## Session consolidation

- Primary and adjacent goals inventoried: `8`.
- Durably transferred or completed: `8`.
- MERGED INTO: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`.
- No unique design requirement remains only in this chat.
- Archive remains blocked only until the active software-validation claim is reconciled from directly inspected workflow evidence or durably converted to a blocked state with that evidence.

## Percentages and denominator

Required deliverables denominator: 31 canonical deliverables — 6 specifications, 18 software modules, 7 tests/automation/coordination records. Developed: 31/31. Validation denominator: 10 layers — static presence, syntax, unit tests, end-to-end deterministic execution, workflow, logs, artifact, physical bench, real paired-device, laboratory pairing. Verified: 1/10. Integration denominator: 8 capability chains. Integrated in software: 6/8; hardware and real-reference chains remain blocked. Goal activation is 54% because boundary proposal and operator-review controls are installed but CI, physical acquisition, and real paired validation are not established.

## Archive condition

Archive after `POM-SW-001` is released, failed, or blocked from directly inspected workflow evidence and the registry/handoff are updated. Physical and real-reference work may continue repository-natively from their durable blocked claims; this chat need not retain their details after software-claim reconciliation.
