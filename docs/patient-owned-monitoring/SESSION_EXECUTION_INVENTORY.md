# Patient-Owned Monitoring Session Execution Inventory

_Last reconciled: 2026-08-02T22:09:00-05:00_

Canonical continuation: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`

## Goal inventory

| ID | Originating goal | Exact destination | Owner / claim | Completion | Validation | Integration | Archival dependency | Evidence | Next executable action |
|---|---|---|---|---|---|---|---|---|---|
| POM-001 | Build a patient-owned continuous evidence system | `docs/patient-owned-monitoring/`, `tools/patient_owned_monitoring/`, `tests/patient_owned_monitoring/`, `hardware/patient_owned_monitoring/` on `main` | Canonical repository workstream | Partially implemented | CI and physical validation pending | Software and hardware contracts share canonical evidence rules | Reconcile CI claim; retain durable physical lanes | Canonical handoff, registry, Git history | Inspect latest validation workflow |
| POM-SEC-001 | Treat applicable federal security requirements as the minimum floor and exceed them | Security baseline/profile, threat/risk records, immutable action provenance, firmware-security interface, existing CI workflow | CI validation claim; production activation in security-assurance lane | Policy and executable repository gates installed; operational controls incomplete | CI, cryptographic, firmware, recovery, incident, and independent-review evidence pending | Integrated into software and hardware contracts | Evidence-based release of `POM-SW-001` and `POM-SEC-ACT-001` | Security records and task registry | Inspect CI; implement and test operational controls |
| POM-BP-001 | Continuous hemodynamic sensing and BP-change validation | `hemodynamic_features.py`, `collapse_detector.py`, `reference_pairing.py`, `evaluate_collapse_events.py` | Software implemented; real validation BLOCKED | Relative features and evaluator implemented | Cuff data absent | Integrated in software chain | Physical paired dataset | Source and tests | Import paired cuff data after capture |
| POM-WEAR-001 | One wearable combining ECG, PPG, motion, temperature, and raw evidence | `HARDWARE_BOM.md`, `simulated_acquisition.py`, `hardware/patient_owned_monitoring/` | Interface work complete; physical build BLOCKED under `POM-HW-001` | Firmware-security, wiring, power/thermal, enclosure, and receipt contracts installed; physical device absent | No schematic, firmware build, CAD, measured power/thermal, or bench result | Hardware acceptance path now integrated with security and evidence rules | Completed bench receipt and simultaneous reference capture | Commits `3ba219c6`, `a1ccf7ff`, `646e1c4f`, `b0e5d5e2`, registry | Hardware lane commits source artifacts and executes bench protocol |
| POM-PAP-001 | Independent PAP evidence without clinic-gated portal access | `PAP_EVIDENCE_MODULE.md`, `pap_report.py`, `pap_event_correlation.py`; hardware interface applies to PAP recorder | Canonical workstream; physical capture BLOCKED | Reporting implemented | Structured-input and overnight capture pending | Shared timestamps, hashes, and hardware security contract | Real overnight capture | PAP files and hardware contracts | Add deterministic fixtures and physical capture |
| POM-GLU-001 | Ingest glucose meter or CGM evidence | `GLUCOSE_IMPORT.md`, `glucose_import.py`, `test_glucose_import.py` | Canonical workstream; CI validation under `POM-SW-001` | Implemented but unvalidated | CI and real paired data pending | Integrated into shared provenance and partition rules | CI receipt and simultaneous reference dataset | Glucose commits and registry | Execute CI and import governed paired records |
| POM-FLUID-001 | Low-cost saliva, urine, and finger-stick testing | `sample_manifest.py`, `strip_reader.py`, `image_calibration.py` | Canonical workstream | Software implemented | CI and physical calibration pending | Integrated in software | Fixed-light physical receipt | Sources and tests | Capture physical calibration evidence |
| POM-CBC-001 | Begin home CBC workstation | `CBC_WORKSTATION.md`, `hematocrit_image.py`, `hematocrit_boundaries.py` | Canonical workstream; laboratory lane BLOCKED | Hematocrit software implemented; broader CBC incomplete | Laboratory pairing absent | Partial | Physical samples and laboratory references | Specification, sources, tests | Commit paired comparison evidence |
| POM-VAL-001 | Validate every metric against reliable simultaneous references | `VALIDATION_PROTOCOL.md`, workflow, `data/`, `receipts/`, bench receipt template | CI CLAIMED; physical validation BLOCKED | Framework and templates implemented | Workflow unobserved; physical validation absent | Software and hardware evidence routes integrated | CI evidence plus real references | Workflow, task registry, bench template | Inspect CI; then execute hardware/reference lanes |
| POM-CONT-001 | Prevent duplicate sessions and preserve continuation | `TASK_REGISTRY.json`, handoff, this inventory | Canonical repository | Implemented | Static inspection complete | Integrated | Evidence-based claim release | Registry and handoff | Reconcile CI claim |

## Hardware interface transfer

The following canonical hardware contracts now exist:

- `hardware/patient_owned_monitoring/FIRMWARE_SECURITY_INTERFACE.md`
- `hardware/patient_owned_monitoring/WIRING_INTERFACES.md`
- `hardware/patient_owned_monitoring/POWER_THERMAL_ENCLOSURE.md`
- `hardware/patient_owned_monitoring/BENCH_RECEIPT_TEMPLATE.json`

They require signed firmware, verified boot, anti-rollback, non-exportable device identity, key separation, authenticated encrypted evidence, replay and sequence detection, governed debug access, brownout recovery, offline export, patient isolation, explicit bus and fault behavior, measured runtime and temperature, enclosure test artifacts, and an evidence-complete bench receipt. These are implementation and acceptance contracts, not proof of physical conformance.

## Session-specific requirements transferred

1. Buildable engineering steps take precedence over generic warning text.
2. Every inferred measurement requires simultaneous reliable-reference validation for its declared use.
3. Raw data remains available; summaries cannot replace evidence.
4. Long warning periods and brief collapses require continuous capture.
5. Calibration, development, validation, and challenge partitions remain isolated.
6. Zero is measured; unknown remains null.
7. PAP evidence remains independently collectable.
8. CBC begins with capillary hemoglobin/hematocrit and smear imaging, then paired laboratory expansion.
9. Applicable federal security requirements are the minimum floor; stronger fail-closed controls and inspectable evidence are mandatory.

## Convergence decision

All session implementation is merged into `StegVerse-Labs/StegVerse-SCW`. No second handoff, security profile, risk register, action-provenance record, hardware interface set, bench receipt schema, task registry, glucose importer, or POM validation workflow is authorized. Physical construction, production security assurance, and real-reference validation remain separate durable lanes in `TASK_REGISTRY.json`.

## Archive dependency

All nine session goals are durably transferred. Archive remains blocked only by the active software-validation claim: inspect the repository workflow and receipts, or durably record its failure/blockage. Hardware, real-reference, and production-security work can continue entirely from repository records without undocumented chat context.
