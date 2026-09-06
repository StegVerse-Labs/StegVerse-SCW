# Trigger Backup Validation Boundary Mirror Handoff

Updated: 2026-09-05
Repository: `StegVerse-Labs/StegVerse-SCW`
Parent authority: `SCW_MIRROR_HANDOFF.md` + `docs/SCW_SECURITY_MIRROR_HANDOFF.md`
Canonical security task: issue `#22`
Branch: `contain/backup-triggers-validation-only`

## Purpose

Contain the remaining hosted credential and cross-repository mutation behavior in `.github/workflows/backup_triggers.yml` while preserving useful trigger-folder packaging as validation/evidence output.

## Preflight finding

The live workflow on `main` still:

```text
read BACKUP_PAT from repository secrets
authenticated to StegVerse/StegVerse-Trigger-Backups
checked out that external repository with BACKUP_PAT
configured a bot identity
committed mirrored trigger state
pulled/rebased and pushed to the external repository
```

This is incompatible with the current StegVerse rule that TV/TVC is the sole credential authority and GitHub Actions is validation/evidence transport only.

No existing PR was found that owns this exact backup-trigger containment.

## Authority boundary

```text
credential/secret/token authority: TV/TVC ONLY
GitHub Actions runtime/production/control-plane authority: NONE
GitHub Actions role here: validation/evidence transport only
external repository mutation authority: NONE
external backup publication authority: NONE
artifact retention implies external backup: false
artifact retention implies sovereign runtime activation: false
```

## Repair

The existing workflow is retained rather than replaced.

New behavior:

```text
triggers: push + schedule + workflow_dispatch retained
permissions.contents: read
checkout persist-credentials: false
BACKUP_PAT: removed
external API authentication: removed
external repository checkout: removed
bot identity: removed
git commit/pull/push: removed
trigger-folder tarball: retained
secret-free evidence manifest: added
output retention: actions/upload-artifact@v4
artifact name: trigger-backup-evidence
external publication: NONE
```

The evidence manifest records source repository, exact source SHA, workflow run ID, event, timestamp, `authority_effect=NONE_VALIDATION_EVIDENCE_ONLY`, `external_repository_mutation=false`, and `publication=false`.

## README completeness predicate

This repair materially changes credential prerequisites, cross-repository mutation authority, output handling, publication semantics, and failure behavior. `README.md` is therefore required in the same change set.

The README now documents trigger backup as validation/evidence retention only; it explicitly states that no `BACKUP_PAT` is consumed, no external repository is authenticated or mutated, and durable replication requires a separately admitted TV/TVC-backed transport/mutation capability.

README completeness: `SATISFIED_IN_BRANCH`.

## Validation boundary

Hosted CI/workflow validation may prove syntax and evidence-output behavior only. It does not prove an external backup was published, sovereign runtime execution occurred, TV/TVC transport is activated, or any repository mutation authority exists.

## Remaining machine work

1. Open and validate the bounded containment PR.
2. Merge only if exact-head validation and current-main collision checks pass.
3. After merge, observe one genuine trigger-backup validation-only execution.
4. Inspect the retained `trigger-backup-evidence` artifact and manifest.
5. Keep durable cross-repository replication behind a separately admitted TV/TVC transport/mutation capability.
6. Reconcile stale root-handoff wording that still describes backup as a destination-availability/push workflow.

## User work

NONE currently required.

## Completion boundary

Source containment can be complete after validated merge. Operational validation-only proof requires one observed execution of the merged workflow and artifact inspection. No result from this lane constitutes external backup publication, sovereign runtime activation, or mutation authority.
