# Patient-Owned Monitoring Session Execution Inventory

_Last reconciled: 2026-08-02T16:28:00-05:00_

Canonical continuation: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`

## Goal inventory

| ID | Originating goal | Exact destination | Owner / claim | Completion | Validation | Integration | Archival dependency | Evidence | Next executable action |
|---|---|---|---|---|---|---|---|---|---|
| POM-001 | Build a patient-owned continuous evidence system | `docs/patient-owned-monitoring/`, `tools/patient_owned_monitoring/`, `tests/patient_owned_monitoring/` on `main` | Canonical repository workstream | Partially implemented | CI pending | Software modules share open records | CI evidence and hardware ownership must be durable | Canonical handoff and Git history | Inspect validation workflow run |
| POM-SEC-001 | Treat applicable federal security requirements as the minimum floor and exceed them | `SECURITY_BASELINE.md`, `security/patient_owned_monitoring/security_profile.json`, `validate_security_profile.py`, CI security gate | Canonical repository workstream; CI validation claim | Implemented but operational evidence incomplete | Profile tests and workflow run pending | Integrated into the only POM validation workflow | CI receipt plus production security evidence | Inspect CI; create threat model and risk register |
| POM-BP-001 | Continuous hemodynamic sensing and BP-change validation | `hemodynamic_features.py`, `collapse_detector.py`, `reference_pairing.py`, `evaluate_collapse_events.py` | Software implemented; real validation BLOCKED under POM-VAL-REAL-001 | Relative features and evaluator implemented; absolute personal model incomplete | Synthetic tests committed; real cuff data absent | Integrated in software evidence chain | Physical paired dataset | Source files; task registry | Import paired cuff data after hardware capture |
| POM-WEAR-001 | One wearable combining ECG, PPG, movement, temperature, and detailed raw data | `HARDWARE_BOM.md`, `simulated_acquisition.py`; future `hardware/patient_owned_monitoring/` | Hardware bench lane BLOCKED | Interface and simulation implemented; physical recorder absent | Software validation pending; bench validation absent | Software format integrated | Components and bench capture | BOM, acquisition code, task registry | Produce firmware interface and wiring files |
| POM-PAP-001 | Independent PAP evidence without clinic-gated portal access | `PAP_EVIDENCE_MODULE.md`, `pap_report.py`, `pap_event_correlation.py` | Canonical repository workstream | Software reporting implemented | Structured-input validation pending | Integrated with shared timestamps and hashes | Real overnight capture | PAP files and handoff | Add fixture and deterministic event-correlation tests |
| POM-GLU-001 | Ingest glucose meter or CGM evidence | `DATA_SCHEMA.md`; future `tools/patient_owned_monitoring/glucose_import.py` | UNCLAIMED | Schema only | None | Not integrated | Importer and paired records | Data schema; task registry | Implement generic timestamped meter/CGM importer |
| POM-FLUID-001 | Low-cost saliva, urine, and finger-stick testing | `sample_manifest.py`, `strip_reader.py`, `image_calibration.py` | Canonical repository workstream | Manifest, calibration, and RGB lookup implemented | CI pending; physical calibration absent | Software chain integrated | Fixed-light physical calibration receipt | Source files and tests | Capture physical calibration-card evidence |
| POM-CBC-001 | Begin home CBC workstation with capillary blood | `CBC_WORKSTATION.md`, `hematocrit_image.py`, `hematocrit_boundaries.py` | Canonical repository workstream; physical validation BLOCKED | Hematocrit calculation and reviewed boundary proposals implemented; broader CBC incomplete | Laboratory pairing absent | Partial | Physical samples and laboratory references | CBC specification, source, tests | Add paired comparison tooling and lab datasets |
| POM-VAL-001 | Validate every metric against a reliable simultaneous reference | `VALIDATION_PROTOCOL.md`, `reference_pairing.py`, CI workflow, future `data/` and `receipts/` | CI CLAIMED; physical validation BLOCKED | Software framework implemented | Workflow not yet observed; physical validation absent | Framework integrated | Workflow run plus real references | Workflow and task registry | Inspect CI run/jobs/logs/artifact |
| POM-CONT-001 | Prevent duplicate sessions and preserve continuation | `TASK_REGISTRY.json`, canonical handoff, this inventory | Canonical repository | Implemented | Static inspection complete | Integrated into handoff | Release or block active claims from evidence | Registry, handoff, inventory commits | Reconcile CI claim |

## Session-specific requirements transferred

1. Buildable engineering steps take precedence over generic warning text.
2. Every inferred measurement must be validated for its stated purpose through simultaneous reliable references.
3. Raw data must remain available; summary scores cannot become the sole evidence.
4. Long warning periods and brief collapses both require continuous capture.
5. Calibration, development, validation, and challenge datasets remain isolated.
6. Zero is a measured value; unknown or untracked values cannot be converted to zero.
7. PAP evidence must remain independently collectable when clinic data is gated.
8. CBC work begins with capillary sampling, hemoglobin/hematocrit, and smear imaging, then expands through paired laboratory validation.
9. Applicable federal security requirements are the minimum floor; production activation requires stronger, fail-closed controls and directly inspectable evidence.

## Security requirement transfer

The new security requirement is installed at:

- `docs/patient-owned-monitoring/SECURITY_BASELINE.md`
- `security/patient_owned_monitoring/security_profile.json`
- `tools/patient_owned_monitoring/validate_security_profile.py`
- `tests/patient_owned_monitoring/test_security_profile.py`
- `.github/workflows/patient-owned-monitoring-validation.yml`

The profile requires governance, encryption, identity/access, device integrity, evidence integrity, audit/detection, availability/recovery, software supply-chain, and incident-response controls. Security exceptions must be time-bounded and include compensating controls. Missing control evidence fails; missing activation evidence blocks activation.

## Convergence and duplicate-control decision

All patient-owned monitoring implementation from this session is merged into the canonical `StegVerse-Labs/StegVerse-SCW` workstream. No second repository, handoff, CI workflow, security profile, or task registry should be created for the same capability. Physical construction and real paired validation are distinct lanes recorded in `TASK_REGISTRY.json`.

## Non-project discussion

The historical discussion of 1990s “white cross” or MaxAlert products and modern ephedrine/ma-huang comparisons did not create a StegVerse implementation obligation.

## Archive dependency

All nine session goals are durably transferred. Archive remains blocked by the active software-validation claim: the repository workflow must produce inspectable run evidence or be durably marked FAILED/BLOCKED. Physical, real-reference, and production-security activation work is durably assigned and does not require retaining undocumented chat history.
