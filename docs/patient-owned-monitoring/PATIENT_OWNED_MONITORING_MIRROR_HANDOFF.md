# Patient-Owned Monitoring Mirror Handoff

_Last updated: 2026-08-02T17:47:00-05:00_

## Canonical authority

- Goal ID: `POM-001`
- Active goal: build, secure, validate, and activate a patient-owned continuous health-evidence system.
- Originating goal: create patient-owned devices and home-test tooling that preserve detailed raw evidence and validate every derived measurement against a reliable simultaneous reference.
- Security rule: applicable federal requirements are the minimum floor, never the target ceiling.
- Repository/branch: `StegVerse-Labs/StegVerse-SCW` / `main`
- Canonical documentation: `docs/patient-owned-monitoring/`
- Implementation: `tools/patient_owned_monitoring/`
- Tests: `tests/patient_owned_monitoring/`
- Hardware lane: `hardware/patient_owned_monitoring/`
- Security profile: `security/patient_owned_monitoring/security_profile.json`
- Task registry: `docs/patient-owned-monitoring/TASK_REGISTRY.json`
- Session inventory: `docs/patient-owned-monitoring/SESSION_EXECUTION_INVENTORY.md`
- This is the only canonical POM handoff. Do not create a competing handoff, security profile, risk register, task registry, or validation workflow.

## Active claims

- `POM-SW-001` — `CLAIMED_FOR_VALIDATION`; owner `repository-native-ci`; release when the latest main workflow, jobs, logs, security receipts, dependency-review result, pipeline receipt, and artifact are inspected, or observed failure/blockage is durably recorded.
- `POM-SEC-ACT-001` — `BLOCKED`; owner `security-assurance-lane`; release after threat/risk records, encryption and key tests, firmware/device integrity, access/override tests, recovery tests, incident exercise, independent review, and all declared activation evidence are verified.
- `POM-HW-001` — `BLOCKED`; owner `hardware-bench-lane`; release after components exist and the first bench capture is committed.
- `POM-VAL-REAL-001` — `BLOCKED`; owner `paired-reference-validation-lane`; release after synchronized raw and reliable reference evidence is committed.

## Governing invariants

- Preserve raw signals before summaries.
- Keep measured, reference-measured, calculated, estimated, experimentally inferred, personal-trend validated, and reference-validated values distinct.
- Unknown remains null; measured zero remains zero.
- Preserve timestamps, clock correction, source hashes, algorithm/model versions, hardware/firmware versions, calibration IDs, partitions, security decisions, and quality decisions.
- Calibration, development, validation, and challenge data remain isolated.
- Missing required security evidence fails validation; missing activation evidence blocks activation.
- Security exceptions require an owner, approver, compensating control, and expiration; indefinite exceptions are prohibited.
- Algorithmic image boundaries remain proposals until reviewed coordinates are supplied.
- Synthetic fixtures never represent physical or laboratory validation.
- Patient export and local evidence capture must not depend on continued cloud, clinic, or account availability.

## Authoritative specifications and controls

- `SYSTEM_ARCHITECTURE.md`
- `VALIDATION_PROTOCOL.md`
- `DATA_SCHEMA.md`
- `HARDWARE_BOM.md`
- `PAP_EVIDENCE_MODULE.md`
- `CBC_WORKSTATION.md`
- `SECURITY_BASELINE.md` — commit `9e704d8e87bd445d758ffda78c41882a8918b58b`
- `security/patient_owned_monitoring/security_profile.json` — commit `3e6e636ef90f0a8d4c97e1e803b9180612d719d2`
- `security/THREAT_MODEL.md` — commit `b7d86cc9c79eb4f8e9165b3dcd6ea7727a0c2ea6`
- `security/RISK_REGISTER.json` — commit `c06985da69d82e10094bef68e17db00f6d37dcc3`

The baseline aligns engineering controls with the HHS HIPAA Security Rule and risk-analysis concepts, NIST SP 800-53 Rev. 5, NIST CSF 2.0, and CISA Secure by Design. This does not claim certification, legal applicability, federal approval, authorization to operate, or FDA clearance.

## Implemented software

1. `reference_pairing.py`
2. `schema_validate.py`
3. `clock_sync.py`
4. `signal_window.py`
5. `hemodynamic_features.py`
6. `pap_report.py`
7. `hematocrit_image.py`
8. `simulated_acquisition.py`
9. `waveform_features.py`
10. `stream_align.py`
11. `collapse_detector.py`
12. `sample_manifest.py`
13. `strip_reader.py`
14. `pap_event_correlation.py`
15. `run_synthetic_pipeline.py`
16. `evaluate_collapse_events.py`
17. `image_calibration.py`
18. `hematocrit_boundaries.py`
19. `validate_security_profile.py`
20. `security_gate.py`

The software chain generates append-only synthetic evidence, validates schemas and clocks, extracts ECG/PPG timing, aligns streams, computes transparent relative features, detects and evaluates candidate events, pairs estimates with references, processes PAP evidence, records fluid samples, calibrates strip images, proposes review-required hematocrit boundaries, validates the mandatory security profile, validates the risk register, scans for embedded credential patterns, and emits hashed receipts.

## Tests and automation

Committed deterministic tests include reference pairing, processing pipeline, acquisition/detection, end-to-end pipeline, event evaluation, image calibration, hematocrit boundaries, security profile, and security gate tests.

The sole workflow is:

`.github/workflows/patient-owned-monitoring-validation.yml`

Latest security-gate update: commit `4d588f747e8c1c30af44ff301c26bad4d23f6c1f`.

It now:

- compiles POM modules and tests;
- validates the mandatory security profile;
- validates risk ownership, release conditions, exception expiry, null/zero semantics, and required evidence declarations;
- scans repository text for credential patterns;
- runs dependency review on pull requests and fails at moderate-or-higher newly introduced vulnerability severity;
- runs deterministic unit tests;
- executes the synthetic pipeline;
- validates all generated receipts;
- uploads security, pipeline, and workflow evidence for 90 days.

Workflow success is not claimed until the run, jobs, logs, and artifact are directly inspected.

## Security activation state

- Policy/profile: `IMPLEMENTED_BUT_UNVALIDATED_BY_CI`.
- Threat model/risk register/security gate: `IMPLEMENTED_BUT_UNVALIDATED_BY_CI`.
- Production security: `BLOCKED_PENDING_EVIDENCE`.

The machine-readable risk register currently tracks device theft, malicious updates, sensor replay/injection, privilege escalation, CI/dependency/secret compromise, outage evidence loss, and incorrect inference. Critical open risks block activation. A passing profile or CI gate proves consistency and repository hygiene only; it does not prove operational encryption, key lifecycle, firmware integrity, recovery, incident readiness, or independent assurance.

## Current task state

- `POM-PIPE-001`: `COMPLETE`, pending CI execution evidence.
- `POM-CI-001`: `CLAIMED`.
- `POM-SEC-PROFILE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-SEC-RISK-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-EVENT-EVAL-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-IMAGE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-CBC-IMG-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-GLUCOSE-001`: `UNCLAIMED`, target `tools/patient_owned_monitoring/glucose_import.py`.

Exact evidence and release conditions are authoritative in `TASK_REGISTRY.json`, latest security update commit `aef5db495adae56131aab2e1a5ee634ce82fe2d8`.

## Exact next execution order

1. Inspect the latest main workflow run, jobs, logs, security-profile receipt, security-gate receipt, dependency-review result when applicable, pipeline receipt, and artifact. Commit a reconciliation receipt under `docs/patient-owned-monitoring/receipts/` and release or block `POM-SW-001` from evidence.
2. Pin all third-party workflow actions to reviewed immutable commit SHAs and record their provenance.
3. Implement `tools/patient_owned_monitoring/glucose_import.py` with timestamp, unit, device/source, provenance, partition, and measured/reference labels.
4. Create hardware firmware interfaces, wiring maps, enclosure definitions, power/thermal budgets, and bench receipt templates, including signed firmware, verified boot, anti-rollback, hardware identity, debug control, encrypted storage, and offline recovery.
5. Produce encryption/key-lifecycle, access/override, replay/sequence, restore/offline, incident-response, and independent-review receipts.
6. Commit governed real synchronized cuff, ECG, pulse-oximeter, PAP, glucose, hemoglobin, hematocrit, and CBC references without replacing synthetic fixtures.
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

Required deliverables: 40 — 9 specifications/security records, 20 software modules, and 11 tests/automation/coordination records. Developed: 40/40. Validation layers: 15 — static presence, profile consistency, risk-register consistency, secret scan, syntax, unit tests, deterministic pipeline, hosted workflow, logs, artifact, cryptography/key evidence, firmware/device evidence, recovery/incident evidence, real paired-device evidence, laboratory pairing. Verified: 1/15. Integration chains: 9; software-integrated: 7/9. Goal activation: 44% because stronger security evidence increases the activation denominator.

## Archive condition

Archive after `POM-SW-001` is released, failed, or durably blocked from directly inspected workflow evidence and the registry/handoff are updated. No other unresolved task requires information unique to this chat.
