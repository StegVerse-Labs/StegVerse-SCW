# Patient-Owned Monitoring Session Execution Inventory

_Last reconciled: 2026-08-02T16:28:00-05:00_

Canonical continuation: `StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/PATIENT_OWNED_MONITORING_MIRROR_HANDOFF.md`

## Goal inventory

| ID | Originating goal | Exact destination | Owner / claim | Completion | Validation | Integration | Archival dependency | Evidence | Next executable action |
|---|---|---|---|---|---|---|---|---|---|
| POM-001 | Build a patient-owned continuous evidence system | `docs/patient-owned-monitoring/`, `tools/patient_owned_monitoring/`, `tests/patient_owned_monitoring/` on `main` | Canonical repository workstream | Partially implemented | CI pending | Software modules share open records | CI evidence and hardware ownership must be durable | Canonical handoff and Git history | Inspect validation workflow run |
| POM-BP-001 | Continuous hemodynamic sensing and BP-change validation | `hemodynamic_features.py`, `collapse_detector.py`, `reference_pairing.py` | Software complete; real validation BLOCKED under POM-VAL-REAL-001 | Relative features implemented; absolute personal model incomplete | Synthetic tests committed; real cuff data absent | Integrated in software evidence chain | Physical paired dataset | Source files; task registry | Implement event evaluation, then import paired cuff data |
| POM-WEAR-001 | One wearable combining ECG, PPG, movement, temperature, and detailed raw data | `HARDWARE_BOM.md`, `simulated_acquisition.py`; future `hardware/patient_owned_monitoring/` | Hardware bench lane BLOCKED | Interface and simulation implemented; physical recorder absent | Software validation pending; bench validation absent | Software format integrated | Components and bench capture | BOM, acquisition code, task registry | Produce firmware interface and wiring files |
| POM-PAP-001 | Independent PAP evidence without clinic-gated portal access | `PAP_EVIDENCE_MODULE.md`, `pap_report.py`, `pap_event_correlation.py` | Canonical repository workstream | Software reporting implemented | Synthetic/structured-input validation pending | Integrated with shared timestamps and hashes | Real overnight capture | PAP files and handoff | Add fixture and deterministic event-correlation tests |
| POM-GLU-001 | Ingest glucose meter or CGM evidence | `DATA_SCHEMA.md`; future importer under `tools/patient_owned_monitoring/` | UNCLAIMED | Schema only | None | Not integrated | Importer and paired records | Data schema | Implement generic timestamped meter/CGM importer |
| POM-FLUID-001 | Low-cost saliva, urine, and finger-stick testing | `sample_manifest.py`, `strip_reader.py`; future `image_calibration.py` | Image calibration UNCLAIMED | Manifest and RGB lookup implemented | Fixed-light geometry not validated | Partially integrated | Calibration-card pipeline | Task registry | Implement image calibration geometry |
| POM-CBC-001 | Begin home CBC workstation with capillary blood | `CBC_WORKSTATION.md`, `hematocrit_image.py`; future `hematocrit_boundaries.py` | Boundary proposal UNCLAIMED; physical validation BLOCKED | Hematocrit coordinate calculation implemented; broader CBC incomplete | Laboratory pairing absent | Partial | Physical samples and laboratory references | CBC specification and task registry | Add boundary proposal and paired comparison tooling |
| POM-VAL-001 | Validate every metric against a reliable simultaneous reference | `VALIDATION_PROTOCOL.md`, `reference_pairing.py`, CI workflow, future `data/` and `receipts/` | CI CLAIMED; physical validation BLOCKED | Software framework implemented | Workflow not yet observed; physical validation absent | Framework integrated | Workflow run plus real references | Workflow and task registry | Inspect CI run/jobs/logs/artifact |
| POM-CONT-001 | Prevent duplicate sessions and preserve continuation | `TASK_REGISTRY.json`, canonical handoff, this inventory | Canonical repository | Implemented | Static inspection complete | Integrated into handoff | Release/expire active claims correctly | Commits `56ae3286`, inventory commit | Update claim after CI result |

## Session-specific requirements transferred

1. Buildable engineering steps take precedence over generic warning text.
2. Every inferred measurement must be validated for its stated purpose through simultaneous reliable references.
3. Raw data must remain available; summary scores cannot become the sole evidence.
4. Long warning periods and brief collapses both require continuous capture.
5. Calibration, development, validation, and challenge datasets remain isolated.
6. Zero is a measured value; unknown or untracked values cannot be converted to zero.
7. PAP evidence must remain independently collectable when clinic data is gated.
8. CBC work begins with capillary sampling, hemoglobin/hematocrit, and smear imaging, then expands through paired laboratory validation.

## Convergence and duplicate-control decision

All patient-owned monitoring implementation from this session is merged into the canonical `StegVerse-Labs/StegVerse-SCW` workstream. No second repository, handoff, CI workflow, or task registry should be created for the same capability. Physical construction and real paired validation are distinct lanes recorded in `TASK_REGISTRY.json`; they are not silently assigned to a chat session.

## Non-project discussion

The historical discussion of 1990s “white cross” or MaxAlert products and modern ephedrine/ma-huang comparisons did not create a StegVerse implementation obligation. No repository task is assigned from that discussion.

## Archive dependency

The unique session knowledge is durably transferred. The remaining reason not to archive immediately is the active software-validation claim: the newly installed repository workflow must produce an inspectable run or be durably marked BLOCKED with its release condition. Once that claim is updated from observed evidence, no session-only implementation authority remains.
