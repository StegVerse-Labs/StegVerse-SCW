# Patient-Owned Monitoring Session Execution Inventory

_Last reconciled: 2026-08-02T17:47:00-05:00_

Canonical continuation: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`

## Goal inventory

| ID | Originating goal | Exact destination | Owner / claim | Completion | Validation | Integration | Archival dependency | Evidence | Next executable action |
|---|---|---|---|---|---|---|---|---|---|
| POM-001 | Build a patient-owned continuous evidence system | `docs/patient-owned-monitoring/`, `tools/patient_owned_monitoring/`, `tests/patient_owned_monitoring/` on `main` | Canonical repository workstream | Partially implemented | CI pending | Software modules share open evidence records | CI evidence; durable hardware and validation ownership | Canonical handoff and Git history | Inspect latest validation workflow |
| POM-SEC-001 | Treat applicable federal security requirements as the minimum floor and exceed them | `SECURITY_BASELINE.md`, `security_profile.json`, `security/THREAT_MODEL.md`, `security/RISK_REGISTER.json`, security validators, existing CI workflow | CI validation claim; production activation assigned to security-assurance lane | Policy, profile, threat model, risk register, secret gate, tests, and dependency-review gate installed | CI run, logs, receipts, and operational evidence pending | Integrated into the sole POM workflow | Reconcile CI claim; operational evidence remains in durable blocked lane | Commits `9e704d8e`, `3e6e636e`, `b7d86cc9`, `c06985da`, `ca272f72`, `06d9561a`, `4d588f74`, `aef5db49` | Inspect workflow; then complete cryptography, firmware, recovery, incident, and independent-review evidence |
| POM-BP-001 | Continuous hemodynamic sensing and BP-change validation | `hemodynamic_features.py`, `collapse_detector.py`, `reference_pairing.py`, `evaluate_collapse_events.py` | Software implemented; real validation BLOCKED | Relative features and evaluator implemented; absolute personal model incomplete | Synthetic tests committed; cuff data absent | Integrated in software evidence chain | Physical paired dataset | Source and tests | Import paired cuff data after capture |
| POM-WEAR-001 | One wearable combining ECG, PPG, movement, temperature, and detailed raw data | `HARDWARE_BOM.md`, `simulated_acquisition.py`, future `hardware/patient_owned_monitoring/` | Hardware-bench lane BLOCKED | Interface and simulation implemented; recorder absent | Software CI and bench validation pending | Software format integrated | Components and bench evidence | BOM, acquisition source, registry | Install firmware interface and wiring files |
| POM-PAP-001 | Independent PAP evidence without clinic-gated portal access | `PAP_EVIDENCE_MODULE.md`, `pap_report.py`, `pap_event_correlation.py` | Canonical workstream | Reporting implemented | Structured-input validation and overnight capture pending | Shared timestamps and hashes | Real capture | PAP files | Add deterministic correlation fixtures and real overnight evidence |
| POM-GLU-001 | Ingest glucose meter or CGM evidence | `DATA_SCHEMA.md`, future `glucose_import.py` | UNCLAIMED | Schema only | None | Not integrated | Importer and paired records | Registry | Implement importer |
| POM-FLUID-001 | Low-cost saliva, urine, and finger-stick testing | `sample_manifest.py`, `strip_reader.py`, `image_calibration.py` | Canonical workstream | Software chain implemented | CI and physical calibration pending | Integrated in software | Physical fixed-light receipt | Sources and tests | Capture physical calibration evidence |
| POM-CBC-001 | Begin home CBC workstation with capillary blood | `CBC_WORKSTATION.md`, `hematocrit_image.py`, `hematocrit_boundaries.py` | Canonical workstream; lab validation BLOCKED | Hematocrit and reviewed proposals implemented; broader CBC incomplete | Laboratory pairing absent | Partial | Physical samples and lab references | Specification, source, tests | Add paired comparison and laboratory data |
| POM-VAL-001 | Validate every metric against reliable simultaneous reference | `VALIDATION_PROTOCOL.md`, `reference_pairing.py`, workflow, future `data/` and `receipts/` | CI CLAIMED; physical validation BLOCKED | Software framework implemented | Workflow unobserved; physical validation absent | Framework integrated | CI plus real references | Workflow and registry | Inspect run/jobs/logs/artifacts |
| POM-CONT-001 | Prevent duplicate sessions and preserve continuation | `TASK_REGISTRY.json`, handoff, this inventory | Canonical repository | Implemented | Static inspection complete | Integrated | Evidence-based claim release | Registry and handoff | Reconcile CI claim |

## Security implementation transferred

The above-federal requirement now has durable policy and executable controls:

- `docs/patient-owned-monitoring/SECURITY_BASELINE.md`
- `security/patient_owned_monitoring/security_profile.json`
- `docs/patient-owned-monitoring/security/THREAT_MODEL.md`
- `docs/patient-owned-monitoring/security/RISK_REGISTER.json`
- `tools/patient_owned_monitoring/validate_security_profile.py`
- `tools/patient_owned_monitoring/security_gate.py`
- `tests/patient_owned_monitoring/test_security_profile.py`
- `tests/patient_owned_monitoring/test_security_gate.py`
- `.github/workflows/patient-owned-monitoring-validation.yml`

The gate validates risk ownership, release conditions, required evidence, exception expiry, federal-floor semantics, and null/zero semantics; scans repository text for credential patterns; and runs dependency review on pull requests. It produces a hashed security receipt and keeps production activation blocked until operational evidence is present.

## Session-specific requirements transferred

1. Buildable engineering steps take precedence over generic warning text.
2. Every inferred measurement requires simultaneous reference validation for its declared use.
3. Raw data remains available; summaries cannot replace evidence.
4. Long warning periods and brief collapses require continuous capture.
5. Calibration, development, validation, and challenge partitions remain isolated.
6. Zero is measured; unknown remains null.
7. PAP evidence remains independently collectable.
8. CBC begins with capillary hemoglobin/hematocrit and smear imaging, then paired laboratory expansion.
9. Applicable federal security requirements are the minimum floor; stronger fail-closed controls and inspectable evidence are mandatory.

## Convergence decision

All session implementation is merged into `StegVerse-Labs/StegVerse-SCW`. No second handoff, security profile, risk register, task registry, or POM validation workflow is authorized. Physical construction, production security assurance, and real-reference validation are separate durable lanes in `TASK_REGISTRY.json`.

## Archive dependency

All nine session goals are durably transferred. Archive remains blocked only by the active software-validation claim: inspect the repository workflow and receipts, or durably record its failure/blockage. Hardware, real-reference, and production-security evidence no longer depend on undocumented chat context.
