# Patient-Owned Monitoring Session Execution Inventory

_Last reconciled: 2026-08-02T19:32:00-05:00_

Canonical continuation: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`

## Goal inventory

| ID | Originating goal | Exact destination | Owner / claim | Completion | Validation | Integration | Archival dependency | Evidence | Next executable action |
|---|---|---|---|---|---|---|---|---|---|
| POM-001 | Build a patient-owned continuous evidence system | `docs/patient-owned-monitoring/`, `tools/patient_owned_monitoring/`, `tests/patient_owned_monitoring/` on `main` | Canonical repository workstream | Partially implemented | CI pending | Software modules share open evidence records | CI evidence; durable hardware and validation ownership | Canonical handoff and Git history | Inspect latest validation workflow |
| POM-SEC-001 | Treat applicable federal security requirements as the minimum floor and exceed them | `SECURITY_BASELINE.md`, `security_profile.json`, `security/THREAT_MODEL.md`, `security/RISK_REGISTER.json`, security validators, existing CI workflow | CI validation claim; production activation assigned to security-assurance lane | Policy, profile, threat model, risk register, secret gate, tests, and dependency-review gate installed | CI run, logs, receipts, and operational evidence pending | Integrated into sole POM workflow | Reconcile CI claim; operational evidence remains in durable blocked lane | Security commits and `TASK_REGISTRY.json` | Inspect workflow; complete cryptography, firmware, recovery, incident, and independent-review evidence |
| POM-BP-001 | Continuous hemodynamic sensing and BP-change validation | `hemodynamic_features.py`, `collapse_detector.py`, `reference_pairing.py`, `evaluate_collapse_events.py` | Software implemented; real validation BLOCKED | Relative features and evaluator implemented; absolute personal model incomplete | Synthetic tests committed; cuff data absent | Integrated in software evidence chain | Physical paired dataset | Source and tests | Import paired cuff data after capture |
| POM-WEAR-001 | One wearable combining ECG, PPG, movement, temperature, and detailed raw data | `HARDWARE_BOM.md`, `simulated_acquisition.py`, future `hardware/patient_owned_monitoring/` | Hardware-bench lane BLOCKED | Interface and simulation implemented; recorder absent | Software CI and bench validation pending | Software format integrated | Components and bench evidence | BOM, acquisition source, registry | Install firmware interface and wiring files |
| POM-PAP-001 | Independent PAP evidence without clinic-gated portal access | `PAP_EVIDENCE_MODULE.md`, `pap_report.py`, `pap_event_correlation.py` | Canonical workstream | Reporting implemented | Structured-input validation and overnight capture pending | Shared timestamps and hashes | Real capture | PAP files | Add deterministic correlation fixtures and real overnight evidence |
| POM-GLU-001 | Ingest glucose meter or CGM evidence | `GLUCOSE_IMPORT.md`, `glucose_import.py`, `test_glucose_import.py` | Canonical repository workstream; CI validation under `POM-SW-001` | Importer, contract, provenance, unit normalization, partition isolation, and tests installed | CI and real paired glucose evidence pending | Integrated into shared record/hash conventions | CI receipt and simultaneous meter/CGM reference dataset | Commits `2e50f2fc`, `a83b509e`, `11ec5d4e`; task registry | Execute CI; import governed paired records without mixing partitions |
| POM-FLUID-001 | Low-cost saliva, urine, and finger-stick testing | `sample_manifest.py`, `strip_reader.py`, `image_calibration.py` | Canonical workstream | Software chain implemented | CI and physical calibration pending | Integrated in software | Physical fixed-light receipt | Sources and tests | Capture physical calibration evidence |
| POM-CBC-001 | Begin home CBC workstation with capillary blood | `CBC_WORKSTATION.md`, `hematocrit_image.py`, `hematocrit_boundaries.py` | Canonical workstream; lab validation BLOCKED | Hematocrit and reviewed proposals implemented; broader CBC incomplete | Laboratory pairing absent | Partial | Physical samples and lab references | Specification, source, tests | Add paired comparison and laboratory data |
| POM-VAL-001 | Validate every metric against reliable simultaneous reference | `VALIDATION_PROTOCOL.md`, `reference_pairing.py`, workflow, future `data/` and `receipts/` | CI CLAIMED; physical validation BLOCKED | Software framework implemented | Workflow unobserved; physical validation absent | Framework integrated | CI plus real references | Workflow and registry | Inspect run/jobs/logs/artifacts |
| POM-CONT-001 | Prevent duplicate sessions and preserve continuation | `TASK_REGISTRY.json`, handoff, this inventory | Canonical repository | Implemented | Static inspection complete | Integrated | Evidence-based claim release | Registry and handoff | Reconcile CI claim |

## Security implementation transferred

The above-federal requirement has durable policy and executable controls in `SECURITY_BASELINE.md`, the mandatory security profile, threat model, risk register, profile validator, security gate, deterministic tests, and the sole POM validation workflow. The gate validates ownership, release conditions, evidence, exception expiry, federal-floor semantics, null/zero semantics, credential patterns, and pull-request dependency changes. Production activation remains blocked until operational evidence exists.

## Glucose implementation transferred

`POM-GLU-001` is no longer schema-only or unclaimed. The importer accepts CSV, JSON, JSONL, and NDJSON; rejects naive timestamps, invalid values, unsupported units, and invalid partitions; preserves original units; normalizes to `mg/dL`; records source hashes and row indexes; distinguishes `measured` from `reference-measured`; and preserves calibration, development, validation, and challenge isolation. Synthetic or imported records do not become clinical validation without a separate simultaneous reference and pairing decision.

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

All session implementation is merged into `StegVerse-Labs/StegVerse-SCW`. No second handoff, security profile, risk register, task registry, glucose importer, or POM validation workflow is authorized. Physical construction, production security assurance, and real-reference validation remain separate durable lanes in `TASK_REGISTRY.json`.

## Archive dependency

All nine session goals are durably transferred. Archive remains blocked only by the active software-validation claim: inspect the repository workflow and receipts, or durably record its failure/blockage. Hardware, real-reference, and production-security evidence no longer depend on undocumented chat context.
