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

### Software validation claim

- Task: `POM-SW-001`
- Role: `CLAIMED_FOR_VALIDATION`
- Claimant: repository-native CI
- Created: `2026-08-02T16:28:00-05:00`
- Release condition: the latest `main` validation workflow passes and its job logs and receipt artifact are inspected; otherwise update the claim to `BLOCKED` or `FAILED` with the observed evidence.
- Exact surface: `.github/workflows/patient-owned-monitoring-validation.yml`

### Physical construction and paired-reference claims

- `POM-HW-001`: `BLOCKED`; owner `hardware-bench-lane`; release condition is availability of components and the first committed bench capture.
- `POM-VAL-REAL-001`: `BLOCKED`; owner `paired-reference-validation-lane`; release condition is a synchronized physical or fluid-test dataset with reliable reference measurements.

No other active implementation claim was found. Unclaimed software tasks are enumerated in `TASK_REGISTRY.json`.

## Governing requirements

- Build what can be built; preserve engineering paths rather than replacing them with generic text warnings.
- Preserve raw signals before summaries.
- Validate each measurement for its stated purpose against a reliable device or laboratory result operating on the same interval.
- Keep measured, reference-measured, calculated, estimated, experimentally inferred, personal-trend validated, and reference-validated values distinct.
- Preserve original timestamps, clock correction, algorithm versions, hardware and firmware versions, calibration IDs, source hashes, and quality decisions.
- Keep calibration, development, validation, and challenge partitions isolated.
- Zero is a measured value; unknown or untracked values never become zero.
- PAP evidence must remain independently collectable when clinic exports are unavailable.

## Authoritative architecture and specifications

- `SYSTEM_ARCHITECTURE.md`
- `VALIDATION_PROTOCOL.md`
- `DATA_SCHEMA.md`
- `HARDWARE_BOM.md`
- `PAP_EVIDENCE_MODULE.md`
- `CBC_WORKSTATION.md`

## Implemented software

- `reference_pairing.py` — reference pairing and bias, MAE, RMSE, correlation, Bland–Altman, timing, and integrity reporting.
- `schema_validate.py` — core evidence-record validation.
- `clock_sync.py` — clock-drift fitting and correction with residuals.
- `signal_window.py` — time-window extraction and coverage, clipping, flatline, and motion scoring.
- `hemodynamic_features.py` — personal-baseline PAT, PPG amplitude, pulse-width, and heart-rate changes.
- `pap_report.py` — nightly PAP evidence summary and threshold intervals.
- `hematocrit_image.py` — reviewed-coordinate hematocrit calculation.
- `simulated_acquisition.py` — deterministic synthetic ECG, PPG, motion, temperature, contact pressure, append-only records, and per-record hashes.
- `waveform_features.py` — ECG/PPG extraction from CSV or recorder JSONL; commit `1024d6136edbab245e0fc28cf107777e73573563` repaired the recorder/extractor format mismatch.
- `stream_align.py` — cross-stream alignment and timing-quality reporting.
- `collapse_detector.py` — sustained personal-baseline hemodynamic candidate events.
- `sample_manifest.py` — hashed append-only fluid and capillary-sample records.
- `strip_reader.py` — fixed-light calibrated RGB interpretation.
- `pap_event_correlation.py` — event-centered PAP evidence windows.
- `run_synthetic_pipeline.py` — deterministic acquisition-to-beat-extraction pipeline with hashed receipt; commit `63a22d723cdd4efe4a23229544a3607a71d781fd`.

## Tests and repository automation

- Deterministic BP fixtures.
- `test_reference_pairing.py`.
- `test_processing_pipeline.py`.
- `test_acquisition_and_detection.py`.
- `test_end_to_end_pipeline.py`; commit `8d28c7b759f921304c1394d703abb50ab7dbdae7`.
- `.github/workflows/patient-owned-monitoring-validation.yml`; commit `6da51bcdd2902181f2c025fcf3b9dc9255b20651`.

The workflow compiles the modules, runs all deterministic unit tests, executes the synthetic pipeline, validates the receipt, and uploads the complete evidence directory for 90 days. Installation is verified by the commit. Workflow success is **not** yet claimed: no status check was present when commit `6da51bc` was inspected.

## Task and consolidation records

- `TASK_REGISTRY.json`; commit `56ae32861d94485d827f2009fa7728c89752f531`.
- `SESSION_EXECUTION_INVENTORY.md`; commit `db864abbaad6ec65e40d61d3bb58d3b7a02392e5`.

All unique session requirements are now transferred into this canonical workstream. The discussion of historical “white cross”/MaxAlert products and modern ephedrine or ma-huang comparisons created no repository implementation obligation.

## Current classifications

- Architecture/specifications: `COMPLETE` as design artifacts; physical conformance unvalidated.
- Software processing modules: `IMPLEMENTED_BUT_PARTIALLY_UNVALIDATED`.
- Synthetic end-to-end pipeline: `IMPLEMENTED_BUT_UNVALIDATED_BY_CI`.
- Repository-native CI: `CLAIMED_FOR_VALIDATION`.
- Physical wearable/PAP recorder: `BLOCKED` by hardware-bench release condition.
- Real cuff, ECG, pulse-oximeter, PAP, glucose, hemoglobin, hematocrit, and CBC pairing: `BLOCKED` by synchronized dataset release condition.
- Publication, Site, Publisher, wiki, release, and deployment propagation: `NOT_REQUIRED` until validated evidence or a release candidate exists.

## Exact next execution order

1. Inspect the run, jobs, logs, and artifact produced by `.github/workflows/patient-owned-monitoring-validation.yml`; update `POM-SW-001` and commit a receipt under `docs/patient-owned-monitoring/receipts/`.
2. Implement `tools/patient_owned_monitoring/evaluate_collapse_events.py` with sensitivity, false-positive rate, onset delay, and coverage metrics.
3. Implement `tools/patient_owned_monitoring/image_calibration.py` for calibration-card geometry and corrected strip-pad sampling.
4. Implement `tools/patient_owned_monitoring/hematocrit_boundaries.py` for semi-automatic boundary proposals while retaining reviewed coordinates.
5. Implement a timestamped glucose meter/CGM importer under `tools/patient_owned_monitoring/`.
6. Create firmware interfaces, wiring maps, enclosure files, and bench receipt templates under `hardware/patient_owned_monitoring/`.
7. Commit real synchronized datasets under governed data/custody locations without replacing synthetic fixtures.
8. Run isolated calibration, development, validation, and challenge evaluations before activating personal BP-change or collapse models.

## Validation commands

```bash
python -m compileall -q tools/patient_owned_monitoring tests/patient_owned_monitoring
python -m unittest discover -s tests/patient_owned_monitoring -p 'test_*.py' -v
python tools/patient_owned_monitoring/run_synthetic_pipeline.py artifacts/patient-owned-monitoring --duration 60 --rate 100 --heart-rate 72 --seed 7
```

## Cross-repository dependencies and propagation

No external repository currently owns this capability. `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `admissibility-wiki`, `stegguardian-wiki`, and `master-records` receive no propagation claim at this stage. Propagation becomes required only after a validated evidence release or explicit contract is committed; until then, local canonical authority avoids duplicated or premature publication.

## Machine-owned continuation

The validation workflow is the current machine-owned task. It has deterministic inputs, persists artifacts, fails when tests or receipt checks fail, and records repository/run metadata. Claim state must be reconciled from observed workflow evidence; absence of evidence is not success.

## Session consolidation

- Primary and adjacent session goals inventoried: `8`.
- Durably transferred or completed: `8`.
- MERGED INTO: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`.
- This session has no remaining unique design requirement outside the repository.
- Archive remains blocked only until the active software-validation claim is reconciled from workflow evidence or durably converted to a blocked state with that evidence.

## Percentages and denominator

Required deliverables denominator: 25 canonical deliverables — 6 specifications, 15 software modules, 4 automation/coordination records. Developed: 25/25. Validation denominator: 10 layers — static presence, syntax, unit tests, end-to-end deterministic execution, workflow, logs, artifact, physical bench, real paired-device, laboratory pairing. Verified: 1/10 (committed file presence only). Integration denominator: 8 capability chains. Integrated in software: 6/8; hardware and real-reference chains remain blocked. Goal activation is 48% because software is installed but CI, physical acquisition, and real paired validation are not established.

## Archive condition

Archive after `POM-SW-001` is released, failed, or blocked from directly inspected workflow evidence and the registry/handoff are updated. Physical and real-reference work may continue repository-natively from their durable blocked claims; this chat need not retain their details after software-claim reconciliation.
