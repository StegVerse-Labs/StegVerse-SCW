# Patient-Owned Monitoring Mirror Handoff

_Last updated: 2026-08-02T19:32:00-05:00_

## Canonical authority

- Goal ID: `POM-001`
- Active goal: build, secure, validate, and activate a patient-owned continuous health-evidence system.
- Originating goal: create patient-owned devices and home-test tooling that preserve detailed raw evidence and validate every derived measurement against a reliable simultaneous reference.
- Security rule: applicable federal requirements are the minimum floor, never the target ceiling.
- Repository/branch: `StegVerse-Labs/StegVerse-SCW` / `main`
- Documentation: `docs/patient-owned-monitoring/`
- Implementation: `tools/patient_owned_monitoring/`
- Tests: `tests/patient_owned_monitoring/`
- Hardware lane: `hardware/patient_owned_monitoring/`
- Security profile: `security/patient_owned_monitoring/security_profile.json`
- Task registry: `docs/patient-owned-monitoring/TASK_REGISTRY.json`
- Session inventory: `docs/patient-owned-monitoring/SESSION_EXECUTION_INVENTORY.md`
- This is the only canonical POM handoff. Do not create a competing handoff, security profile, risk register, glucose importer, task registry, or validation workflow.

## Active claims

- `POM-SW-001` — `CLAIMED_FOR_VALIDATION`; owner `repository-native-ci`; release when latest-main workflow, jobs, logs, security receipts, dependency-review result, pipeline receipt, and artifact are inspected, or observed failure/blockage is durably recorded.
- `POM-SEC-ACT-001` — `BLOCKED`; owner `security-assurance-lane`; release after encryption/key, firmware/device integrity, access/override, recovery, incident, independent-review, and all declared activation evidence are verified.
- `POM-HW-001` — `BLOCKED`; owner `hardware-bench-lane`; release after components exist and the first bench capture is committed.
- `POM-VAL-REAL-001` — `BLOCKED`; owner `paired-reference-validation-lane`; release after synchronized raw and reliable reference evidence is committed.

## Governing invariants

- Preserve raw signals before summaries.
- Keep measured, reference-measured, calculated, estimated, experimentally inferred, personal-trend validated, and reference-validated values distinct.
- Unknown remains null; measured zero remains zero.
- Preserve timestamps, source hashes, clock corrections, algorithm/model versions, hardware/firmware versions, calibration IDs, partitions, security decisions, and quality decisions.
- Calibration, development, validation, and challenge data remain isolated.
- Missing required security evidence fails validation; missing activation evidence blocks activation.
- Security exceptions require an owner, approver, compensating control, and expiration.
- Synthetic or imported records never represent physical, clinical, or laboratory validation without a separate simultaneous reference and pairing decision.
- Patient export and local evidence capture must not depend on continued cloud, clinic, or account availability.

## Authoritative specifications and controls

- `SYSTEM_ARCHITECTURE.md`
- `VALIDATION_PROTOCOL.md`
- `DATA_SCHEMA.md`
- `HARDWARE_BOM.md`
- `PAP_EVIDENCE_MODULE.md`
- `CBC_WORKSTATION.md`
- `GLUCOSE_IMPORT.md` — governed meter/CGM import contract; commit `11ec5d4eea2b8df8dca1c23fba43ecd30fb88946`
- `SECURITY_BASELINE.md`
- `security/patient_owned_monitoring/security_profile.json`
- `security/THREAT_MODEL.md`
- `security/RISK_REGISTER.json`

The security baseline aligns engineering controls with HHS HIPAA Security Rule and risk-analysis concepts, NIST SP 800-53 Rev. 5, NIST CSF 2.0, and CISA Secure by Design. This does not claim certification, legal applicability, federal approval, authorization to operate, or FDA clearance.

## Implemented software

The canonical implementation includes reference pairing, schema validation, clock correction, signal quality, hemodynamic features, PAP reporting and correlation, simulated acquisition, ECG/PPG extraction, stream alignment, event detection and evaluation, fluid-sample manifests, strip reading, image calibration, reviewed hematocrit processing, synthetic end-to-end receipts, security-profile validation, risk/secret scanning, and governed glucose import.

### Glucose import

- Implementation: `tools/patient_owned_monitoring/glucose_import.py`
- Commit: `2e50f2fcd0ce9c47adc0d63454073ba56392e54d`
- Tests: `tests/patient_owned_monitoring/test_glucose_import.py`
- Test commit: `a83b509e0e43288280d9b45a59be0fc93c3fc05f`
- Contract: `docs/patient-owned-monitoring/GLUCOSE_IMPORT.md`

The importer accepts CSV, JSON, JSONL, and NDJSON; requires timezone-aware timestamps; accepts `mg/dL` and `mmol/L`; preserves the original value/unit; normalizes to `mg/dL` using factor `18.0182`; records device/source metadata, source SHA-256, row index, importer version, output label, partition, and record SHA-256; rejects invalid values, units, timestamps, source types, and partitions; and preserves measured zero.

## Tests and automation

The sole workflow is `.github/workflows/patient-owned-monitoring-validation.yml`. It compiles modules, validates the mandatory security profile and risk register, scans credential patterns, performs pull-request dependency review, runs all deterministic tests including glucose import, executes the synthetic pipeline, validates receipts, and uploads evidence for 90 days.

Workflow success is not claimed until the run, jobs, logs, and artifact are directly inspected.

## Current task state

- `POM-PIPE-001`: `COMPLETE`, pending CI execution evidence.
- `POM-CI-001`: `CLAIMED`.
- `POM-SEC-PROFILE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-SEC-RISK-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-EVENT-EVAL-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-IMAGE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-CBC-IMG-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-GLUCOSE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.

Exact evidence and release conditions are authoritative in `TASK_REGISTRY.json`, latest glucose-state commit `d8e3c9841fc7400817f441523058ea3945550949`.

## Exact next execution order

1. Inspect the latest main workflow run, jobs, logs, security-profile receipt, security-gate receipt, dependency-review result when applicable, pipeline receipt, and artifact. Commit reconciliation under `docs/patient-owned-monitoring/receipts/` and release or block `POM-SW-001` from evidence.
2. Pin all third-party workflow actions to reviewed immutable commit SHAs and record provenance.
3. Create hardware firmware interfaces, wiring maps, enclosure definitions, power/thermal budgets, and bench receipt templates, including signed firmware, verified boot, anti-rollback, hardware identity, debug control, encrypted storage, and offline recovery.
4. Produce encryption/key-lifecycle, access/override, replay/sequence, restore/offline, incident-response, and independent-review receipts.
5. Import governed real simultaneous glucose-meter/CGM records and commit their reference-pairing decisions without mixing calibration, development, validation, and challenge partitions.
6. Commit governed real synchronized cuff, ECG, pulse-oximeter, PAP, hemoglobin, hematocrit, and CBC references without replacing synthetic fixtures.
7. Run isolated calibration, development, validation, and challenge evaluations before any personal BP-change, collapse, or diagnostic activation.

## Validation commands

```bash
python -m compileall -q tools/patient_owned_monitoring tests/patient_owned_monitoring
python tools/patient_owned_monitoring/validate_security_profile.py security/patient_owned_monitoring/security_profile.json --receipt artifacts/patient-owned-monitoring/security_profile_validation.json
python tools/patient_owned_monitoring/security_gate.py --risk-register docs/patient-owned-monitoring/security/RISK_REGISTER.json --root . --receipt artifacts/patient-owned-monitoring/security_gate_receipt.json
python -m unittest discover -s tests/patient_owned_monitoring -p 'test_*.py' -v
python tools/patient_owned_monitoring/run_synthetic_pipeline.py artifacts/patient-owned-monitoring/pipeline --duration 60 --rate 100 --heart-rate 72 --seed 7
```

## Cross-repository propagation

No external repository currently owns this capability. No Site, Publisher, wiki, master-records, release, deployment, or publication propagation is claimed until validated evidence or an explicit integration contract exists.

## Session consolidation

- Primary and adjacent goals: `9`.
- Durably transferred or completed: `9`.
- MERGED INTO: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`.
- No unique project or security requirement remains only in this conversation.
- Physical, real-reference, and production-security work can continue from durable claims without retaining chat history.
- Archive remains blocked only by this session's distinct responsibility to reconcile `POM-SW-001` from directly inspected workflow evidence.

## Percentages and denominator

Required deliverables: 43 — 10 specifications/security records, 21 software modules, and 12 tests/automation/coordination records. Developed: 43/43. Validation layers: 15 — static presence, profile consistency, risk-register consistency, secret scan, syntax, unit tests, deterministic pipeline, hosted workflow, logs, artifact, cryptography/key evidence, firmware/device evidence, recovery/incident evidence, real paired-device evidence, laboratory pairing. Verified: 1/15. Integration chains: 9; software-integrated: 8/9. Goal activation: 47% because glucose import is integrated while hosted, physical, security-assurance, and real-reference evidence remain incomplete.

## Archive condition

Archive after `POM-SW-001` is released, failed, or durably blocked from directly inspected workflow evidence and the registry/handoff are updated. No other unresolved task requires information unique to this chat.
