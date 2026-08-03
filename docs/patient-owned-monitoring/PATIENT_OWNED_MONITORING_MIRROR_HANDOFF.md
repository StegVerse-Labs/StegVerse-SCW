# Patient-Owned Monitoring Mirror Handoff

_Last updated: 2026-08-02T22:09:00-05:00_

## Canonical authority

- Goal ID: `POM-001`
- Active goal: build, secure, validate, and activate a patient-owned continuous health-evidence system.
- Originating goal: create patient-owned devices and home-test tooling that preserve detailed raw evidence and validate every derived measurement against a reliable simultaneous reference.
- Security rule: applicable federal requirements are the minimum floor, never the target ceiling.
- Repository/branch: `StegVerse-Labs/StegVerse-SCW` / `main`
- Documentation: `docs/patient-owned-monitoring/`
- Software: `tools/patient_owned_monitoring/`
- Tests: `tests/patient_owned_monitoring/`
- Hardware: `hardware/patient_owned_monitoring/`
- Security profile: `security/patient_owned_monitoring/security_profile.json`
- Task registry: `docs/patient-owned-monitoring/TASK_REGISTRY.json`
- Session inventory: `docs/patient-owned-monitoring/SESSION_EXECUTION_INVENTORY.md`
- This is the sole canonical POM handoff. Do not create competing handoffs, security profiles, risk registers, action-provenance records, hardware-interface sets, bench receipt schemas, task registries, importers, or validation workflows.

## Active claims

- `POM-SW-001` — `CLAIMED_FOR_VALIDATION`; owner `repository-native-ci`; release after direct inspection of the latest-main workflow, jobs, logs, security receipts, action provenance, dependency review when applicable, pipeline receipt, and artifact, or after observed failure/blockage is durably recorded.
- `POM-SEC-ACT-001` — `BLOCKED`; owner `security-assurance-lane`; release after cryptography/key, firmware/device integrity, access/override, recovery, incident, independent-review, and all declared activation evidence are verified.
- `POM-HW-001` — `BLOCKED`; owner `hardware-bench-lane`; release after source schematic, firmware build, enclosure artifacts, measured power/thermal evidence, completed bench receipt, and simultaneous reference capture are committed.
- `POM-VAL-REAL-001` — `BLOCKED`; owner `paired-reference-validation-lane`; release after synchronized raw and reliable reference evidence is committed.

## Governing invariants

- Preserve raw signals before summaries.
- Keep measured, reference-measured, calculated, estimated, experimentally inferred, personal-trend validated, and reference-validated values distinct.
- Unknown remains null; measured zero remains zero.
- Preserve timestamps, source hashes, clock corrections, algorithm/model versions, hardware/firmware versions, calibration IDs, partitions, security decisions, and quality decisions.
- Calibration, development, validation, and challenge data remain isolated.
- Missing required security evidence fails validation; missing activation evidence blocks activation.
- Security exceptions require owner, approver, compensating control, and expiration.
- Every third-party action is pinned to a reviewed immutable commit SHA; floating tags are prohibited.
- Unsigned firmware, failed verification, rollback, replay, sequence gaps, unavailable sensors, and evidence loss cannot be silently accepted.
- Synthetic, imported, or interface-only artifacts never represent physical, clinical, or laboratory validation.
- Patient export and local evidence capture must not depend on cloud, clinic, or account availability.

## Authoritative specifications and controls

- `SYSTEM_ARCHITECTURE.md`
- `VALIDATION_PROTOCOL.md`
- `DATA_SCHEMA.md`
- `HARDWARE_BOM.md`
- `PAP_EVIDENCE_MODULE.md`
- `CBC_WORKSTATION.md`
- `GLUCOSE_IMPORT.md`
- `SECURITY_BASELINE.md`
- `security/patient_owned_monitoring/security_profile.json`
- `security/THREAT_MODEL.md`
- `security/RISK_REGISTER.json`
- `security/ACTION_PROVENANCE.json`
- `hardware/patient_owned_monitoring/FIRMWARE_SECURITY_INTERFACE.md`
- `hardware/patient_owned_monitoring/WIRING_INTERFACES.md`
- `hardware/patient_owned_monitoring/POWER_THERMAL_ENCLOSURE.md`
- `hardware/patient_owned_monitoring/BENCH_RECEIPT_TEMPLATE.json`

The security baseline aligns engineering controls with HHS HIPAA Security Rule and risk-analysis concepts, NIST SP 800-53 Rev. 5, NIST CSF 2.0, and CISA Secure by Design. This is not a claim of certification, legal applicability, authorization to operate, federal approval, or FDA clearance.

## Implemented software and automation

The canonical software includes reference pairing, schema validation, clock correction, signal quality, hemodynamic features, PAP reporting/correlation, simulated acquisition, ECG/PPG extraction, stream alignment, event detection/evaluation, fluid-sample manifests, strip reading, image calibration, reviewed hematocrit processing, glucose import, synthetic receipts, security-profile validation, risk/secret scanning, and immutable action provenance.

The sole workflow is `.github/workflows/patient-owned-monitoring-validation.yml`. It compiles modules, validates security records, scans credential patterns, performs pull-request dependency review, runs deterministic tests, executes the synthetic pipeline, validates receipts, and uploads evidence. Its third-party actions are pinned to immutable commits recorded in `security/ACTION_PROVENANCE.json`.

Workflow success is not claimed until the run, jobs, logs, and artifact are directly inspected.

## Hardware interface implementation

`POM-HW-IFACE-001` is `COMPLETE` as an interface and acceptance-contract task:

- `FIRMWARE_SECURITY_INTERFACE.md`; commit `3ba219c6672b3e763cc3af4af2187e0b4596cb4e`
- `WIRING_INTERFACES.md`; commit `a1ccf7ff3b65a28700e5bc8434e5bd85914cb4b3`
- `POWER_THERMAL_ENCLOSURE.md`; commit `646e1c4f23f4405014c331d7c1c47d8597f88cb9`
- `BENCH_RECEIPT_TEMPLATE.json`; commit `b0e5d5e2dcc7523015fd8818bebf9c5550a1ded4`

These contracts require signed firmware, verified boot, anti-rollback, non-exportable identity, key separation, authenticated encrypted evidence, explicit replay/sequence handling, governed debug authorization, brownout recovery, offline export, patient isolation, documented bus and fault behavior, measured runtime and temperature, enclosure evidence, and a hashed bench receipt.

They do not prove a physical device, firmware implementation, electrical safety, thermal safety, or body-worn operation. Those remain blocked under `POM-HW-001`.

## Current task state

- `POM-PIPE-001`: `COMPLETE`, pending CI evidence.
- `POM-CI-001`: `CLAIMED`.
- `POM-ACTION-PIN-001`: `COMPLETE`, pending hosted execution evidence.
- `POM-HW-IFACE-001`: `COMPLETE`, physical implementation pending in hardware lane.
- `POM-SEC-PROFILE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-SEC-RISK-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-EVENT-EVAL-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-IMAGE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-CBC-IMG-001`: `IMPLEMENTED_BUT_UNVALIDATED`.
- `POM-GLUCOSE-001`: `IMPLEMENTED_BUT_UNVALIDATED`.

Exact evidence and release conditions are authoritative in `TASK_REGISTRY.json`, hardware-interface update commit `806540f132e2ab3cafdfc0ce583cb0e7928a84f0`.

## Exact next execution order

1. Inspect the latest main workflow run, jobs, logs, security receipts, action provenance, dependency-review result when applicable, pipeline receipt, and artifact. Commit reconciliation under `docs/patient-owned-monitoring/receipts/` and release, fail, or durably block `POM-SW-001`.
2. In `hardware/patient_owned_monitoring/`, commit source schematic/netlist, connector pinout, firmware source/build manifest, signed-image metadata, enclosure CAD/drawings, measured power/thermal data, and a completed hashed bench receipt.
3. Produce cryptography/key-lifecycle, access/override, replay/sequence, restore/offline, incident-response, and independent-review receipts.
4. Import governed real simultaneous glucose records and commit pairing decisions without mixing dataset partitions.
5. Commit synchronized cuff, ECG, pulse-oximeter, PAP, hemoglobin, hematocrit, and CBC references.
6. Run isolated calibration, development, validation, and challenge evaluations before any personal model or diagnostic activation.

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
- No unique project, security, or hardware-interface requirement remains only in this conversation.
- Physical, real-reference, and production-security work can continue from durable claims without chat history.
- Archive remains blocked only by this session's distinct responsibility to reconcile `POM-SW-001` from directly inspected workflow evidence.

## Percentages and denominator

Required deliverables: 48 — 15 specifications/security/hardware records, 21 software modules, and 12 tests/automation/coordination records. Developed: 48/48. Validation layers: 16 — static presence, profile consistency, risk-register consistency, secret scan, syntax, unit tests, deterministic pipeline, hosted workflow, logs, artifact, cryptography/key evidence, firmware/device evidence, power/thermal/mechanical bench evidence, recovery/incident evidence, real paired-device evidence, laboratory pairing. Verified: 1/16. Integration chains: 10; contract/software-integrated: 9/10; physical/reference activation remains blocked. Goal activation: 50%.

## Archive condition

Archive after `POM-SW-001` is released, failed, or durably blocked from directly inspected workflow evidence and the registry/handoff are updated. No other unresolved task requires information unique to this chat.
