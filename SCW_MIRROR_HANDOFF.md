# SCW Mirror Handoff

This file is the current handoff and task source of truth for `StegVerse-Labs/StegVerse-SCW`.

## Current Goal

Restore stable repository operations without adding workflows.

## Completed Repairs

- restored `scripts/autodocs_probe_pr_safe.py` from `.github/autopatch/docs-prsafe-status.patch.yml`
- preserved `taskops-nightly` as the existing declared task surface
- made `.github/workflows/stegverse-multi-autopatch.yml` concurrency-safe for report publication
- added fetch/rebase-before-push handling for `reports/stegverse_multi_autopatch_report.md`
- serialized `.github/workflows/stegtvc_connectivity_autopatch.yml`
- made connectivity report publication empty-diff safe and fetch/rebase-before-push safe
- removed silent dependency-install success from the connectivity workflow
- aligned `docs/governance/repo_alignment_expectations.yaml` with `scripts/stegtvc_connectivity_manifest.json`
- removed undeclared cross-repo workflow filename assumptions from ASL-1 enforcement
- preflighted `.github/workflows/backup_triggers.yml` so an absent or inaccessible backup destination records a clean skip instead of failing the repository
- added rebase-before-push handling to the trigger backup publication step
- repaired `.github/workflows/export-hcb-nightly.yml` so the scheduled profile dispatches the existing `export-hcb.yml` workflow instead of attempting to call a workflow that does not declare `workflow_call`

## Latest Failure Handling

```text
Event: GitHub Actions failure notification
Repository: StegVerse-Labs/StegVerse-SCW
Branch: main
Workflow: .github/workflows/export-hcb-nightly.yml
Run: 29141761848
Commit: 2ea9fcdcddbc63cae6a1f8c2d4ace0c792c5a88d
Failure class: workflow configuration / no jobs were run
Observed cause: export-hcb-nightly attempted to invoke ./.github/workflows/export-hcb.yml as a reusable workflow, but export-hcb.yml exposes workflow_dispatch only and does not declare workflow_call
Repair commit: 56a6f3e260474897358a0192d2473daf8b86bdf4
Repair behavior: the existing nightly workflow now uses the repository-scoped GITHUB_TOKEN with actions:write to dispatch the existing export-hcb.yml workflow in dry-run mode
Authority effect: none; no external repository write, release, tag, merge, deployment, or non-dry-run export was authorized
Verification: pending the next scheduled or explicitly authorized workflow execution
```

## Current Priority

Verify that `export-hcb-nightly` creates a job and successfully dispatches the dry-run `export-hcb.yml` workflow. Then inspect the dispatched dry-run result before declaring the export path repaired.

## Known Remaining Work

Destination: `StegVerse-Labs/StegVerse-SCW`

- verify `taskops-nightly` passes after restoring the AutoDocs probe
- verify multi-repo autopatch report publication passes after concurrency repair
- verify StegTV connectivity execution and report publication pass after workflow hardening
- verify ASL-1 alignment uses the canonical StegTVC file contract
- verify backup workflow records a clean skip when destination access is absent
- verify `export-hcb-nightly` produces a job and dispatches the dry-run export workflow
- inspect the dispatched `export-hcb.yml` dry-run for local dependency, token, or payload-validation failures
- inspect repository-wide CodeQL and validation cascade separately from operational workflow repairs

## Build Rule

Prefer existing declared scripts and task surfaces. Keep commit steps safe when no files changed or when `main` advances during execution. Optional external destinations must be preflighted and may not convert unavailable authority into a repository failure. Do not claim downstream completion without evidence.

## Next Integration Candidate

Publish verified SCW status through existing Site and Publisher paths after local checks are green.
