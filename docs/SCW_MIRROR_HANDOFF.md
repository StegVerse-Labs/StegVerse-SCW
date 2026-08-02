# StegVerse-SCW Mirror Handoff

_Last updated: 2026-08-02_

## Goal authority

- Goal ID: `SCW-WORKFLOW-CONTROL-PLANE-RECOVERY-001`
- Organization: `StegVerse-Labs`
- Repository: `StegVerse-Labs/StegVerse-SCW`
- Branch: `main`
- Active goal: restore a trustworthy, observable workflow control plane without destroying recoverable workflow intent.
- Continuation authority: this file plus live repository state and committed evidence.

## Historical incident

The 2026-01-03 Ops Console snapshot reported 150 workflows: 0 OK, 110 no-dispatch, and 40 broken. That snapshot is historical and must not be treated as current state until regenerated.

`ScannerError` and `ParserError` are parse-stage failures and are not caused by an expired PAT. PAT validity remains a separate runtime question and requires direct `401`, `403`, `Bad credentials`, push, resource-access, or dispatch evidence.

## Authoritative implementation inventory

The governed required-component denominator is defined in `config/workflow-recovery-required.json`.

### Implemented

1. `.github/actions/setup-common-python/action.yml` — canonical composite action.
2. `.github/workflows/setup-common-python.yml` — read-only smoke test; repaired in `786453329b4c4c803527298cf21c96937ded579e`.
3. `.github/workflows/telemetry-reusable.yml` — top-level reusable telemetry; installed in `3e4e8654b122759d8413fedeeaea87aea32f1c97`.
4. `.github/workflows/workflow_preflight.yml` — safe defaults and corrected telemetry caller; repaired in `aab8e268a819860eccecc18a2aa8d9b1535dedc6`.
5. `.github/workflows/workflows-sanity-check.yml` — recursive read-only inventory gate; upgraded in `ecf7ec713de2b1846eb9af72dc14fd86a18cd4f7`.
6. `scripts/patches/repair_workflow_yaml.py` — bounded loss-minimizing repair engine; replaced in `247542dcb14883ac568309909642b6fe11a8c587`.
7. `.github/workflows/repair-bad-yaml.yml` — one-target, report-first repair workflow; rebuilt in `f7ab3277c73e29df8f639f07481f21b535e16638`.
8. `.github/workflows/ops-console.yml` — reviewed allowlisted dispatcher; restricted in `34dc85b5d0a91b13a2c84bba1154b741a2e46f16`.
9. `config/workflow-recovery-required.json` — governed inventory and release conditions; installed in `ff6d7a09b483e010db4d068ad7619a60b8e2a955`.
10. `scripts/workflow_recovery_controller.py` — deterministic read-only state controller; installed in `d651e1a16f2c1aa78d82665430ec17b1f5c1f125`.
11. `.github/workflows/workflow-recovery-controller.yml` — push, schedule, and manual automation producing inspectable receipts and failing closed; installed in `9a4fd146f374ab52e02f90ce8fab1c6f573cb423`.
12. `docs/SCW_MIRROR_HANDOFF.md` — durable continuation authority.

### Quarantined or superseded

- `.github/workflows/_reusables/telemetry.yml` — blob `d2bc52a3ff4be5853fdca402a62287fbbfdc79f7` contains concatenated workflow definitions and must not be called.
- `.github/workflows/neutralize_secrets_if.yml` — parse-structured but a high-risk repository-wide mutator; do not execute until inventory evidence names exact targets and a reviewed mutation boundary exists.
- Prior repair script blob `8eef282036ce5be54d4c3052fda6b87f411ff679` — superseded because full-document PyYAML dumping could alter GitHub workflow semantics.

## Automation contract

Owner: `StegVerse-Labs/StegVerse-SCW`.

Trigger:

- changes to workflow recovery files on `main`;
- daily schedule at `05:17 UTC`;
- manual dispatch.

Deterministic inputs:

- repository tree;
- `config/workflow-recovery-required.json`.

Outputs:

- `self_healing_out/workflow-recovery/WORKFLOW_RECOVERY_RECEIPT.json`;
- `self_healing_out/workflow-recovery/WORKFLOW_RECOVERY_RECEIPT.md`;
- uploaded artifact `workflow-recovery-receipt-<run_id>`;
- job summary and non-zero fail-closed result when incomplete.

Status vocabulary: `COMPLETE`, `BLOCKED`, `RETRY`, `REVIEW_REQUIRED`, `FAILED`.

The controller detects missing required components, invalid YAML, nested workflow files, duplicate exact content, dispatch posture, and the next executable task. It is read-only and prevents duplicate concurrent execution by workflow concurrency.

## Validation state

### Proven

- Repository mutations were accepted on `main` by the connected GitHub authority.
- Required automation files exist at their committed destinations.
- Repository permission snapshot reports administrative, maintain, push, pull, and triage authority.

### Not yet proven

- No hosted workflow run, job log, or artifact receipt has yet been directly inspected for the controller or repaired nucleus.
- The connected commit-status endpoint returned no status records for commit `9a4fd146f374ab52e02f90ce8fab1c6f573cb423`; this is absence of evidence, not success or failure.
- Current repository-wide parse counts remain unknown until a controller or sanity-check artifact is inspected.
- Same-repository `GITHUB_TOKEN` execution has not been proven.
- PAT-dependent cross-repository dispatch or write authority has not been tested.

## Exact next tasks

1. Inspect the first `Workflow Recovery Controller` run, jobs, logs, and `workflow-recovery-receipt-*` artifact at `.github/workflows/workflow-recovery-controller.yml`.
2. Correct `scripts/workflow_recovery_controller.py` or its workflow if the hosted receipt reports `FAILED`.
3. Use the receipt’s `next_task` field to repair the first invalid workflow through `.github/workflows/repair-bad-yaml.yml` in report-only mode.
4. Inspect hosted runs for `.github/workflows/workflows-sanity-check.yml`, `.github/workflows/setup-common-python.yml`, and `.github/workflows/workflow_preflight.yml` with mutation inputs disabled.
5. After same-repository execution succeeds, install a least-privilege PAT health-check workflow that performs no mutation and records only authorization class and HTTP result.
6. Recompute and publish the current Ops Console state from controller evidence.
7. Remove or relocate `.github/workflows/_reusables/telemetry.yml` only after repository search proves no remaining callers.
8. Classify duplicate and obsolete workflow families, beginning with autopatch variants, using the controller receipt.

## Blockers and release conditions

- Hosted validation blocker: release when a directly inspected run has jobs, logs, and an uploaded controller receipt.
- PAT validation blocker: release only after parse-valid same-repository workflows execute successfully.
- Nested telemetry removal blocker: release when repository search finds no caller of `_reusables/telemetry.yml`.
- Bulk mutator quarantine: release only when an inventory receipt names exact targets and a reviewed one-target or bounded mutation plan exists.

There are no unspecified external tasks. Hosted observation is owned by `.github/workflows/workflow-recovery-controller.yml`; repair selection is owned by `scripts/workflow_recovery_controller.py`; bounded correction is owned by `.github/workflows/repair-bad-yaml.yml`; PAT validation remains a named future repository-native workflow task after its release condition is met.

## Cross-repository posture

No canonical change from this recovery task currently requires propagation to `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `admissibility-wiki`, `stegguardian-wiki`, or `master-records`. Propagation is not claimed. A future release record may require publication after the SCW control plane is validated and tagged.

## Completion accounting

Required deliverables for the current recovery goal: 16.

- Implemented production files/contracts: 12.
- Hosted validation receipt sets: 0 of 4 required.
- PAT health-check automation: missing, intentionally blocked by same-repository validation.
- Current-state Ops Console publication: missing.
- Nested malformed telemetry disposition: incomplete.
- Duplicate/obsolete workflow classification: incomplete.

Task completion: 12/16 = 75%.
Developed-file completion: 12/13 currently unblocked required files = 92%.
Validation completion: 0/4 receipt sets = 0%.
Integration completion: 1/3 internal integration boundaries = 33% (controller installed; hosted evidence and PAT lane incomplete).
Goal activation: 7/16 weighted activation conditions = 44%.

## Archive condition

Do not archive while hosted receipts, current-state classification, PAT-lane implementation, malformed telemetry disposition, or duplicate-family classification remain unresolved. Continuation must begin from this file and the latest controller receipt.
