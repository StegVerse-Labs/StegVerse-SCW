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
- removed the stale `scripts/taskops_autodocs_link.py` invocation from `taskops-nightly`; the script does not exist anywhere in the repository and the existing AutoDocs probe is the declared refresh surface

## Latest Failure Handling

```text
Event: GitHub Actions failure notification
Repository: StegVerse-Labs/StegVerse-SCW
Branch: main
Workflow: StegTV Connectivity Autopatch
Job: stegtvc-connectivity
Run: 29148766401
Commit: abcfdd5fdc875eca8bdb71fbbae462ebe6de57fe
Failure class: external repository authentication failure
Observed cause: scripts/stegtvc_connectivity_autopatch.py invoked `gh repo clone StegVerse-Labs/TVC`; GitHub CLI returned HTTP 401 Bad credentials before any target repository mutation occurred
Evidence: checkout, token-resolution, Python setup, and dependency installation succeeded; the first source-repository clone failed and the report was written locally before the job exited
Repair status: blocked; changing credential scope, substituting authority, or mutating external repositories is not authorized by this handoff
Authority effect: none; no external repository was modified, no report commit was pushed, and no deployment, release, tag, merge, or authority expansion occurred
Next task: verify the configured PAT or replace the cross-repository mutation design with an explicitly authorized read-only/preflight contract before retrying
```

```text
Event: GitHub Actions failure notification
Repository: StegVerse-Labs/StegVerse-SCW
Branch: main
Workflow: StegVerse Guardian Worker – Repo Alignment Check
Job: alignment_check
Run: 29148507073
Commit: 715ce6b948f0283833f5cdd40d1a271a73977f19
Failure class: missing local declared script
Observed cause: .github/workflows/alignment_check.yml invokes scripts/genesis/repo_alignment_check.py, but that path is absent from the current repository; the job exited before alignment evaluation or report publication
Evidence: checkout, PAT resolution, Python setup, and dependency installation succeeded; Python returned Errno 2 for the declared script path
Repair status: blocked; no canonical replacement implementation or explicitly declared source path is present in the current handoff
Authority effect: none; no report was changed, no issue was created, no external repository was modified, and no deployment, release, tag, or merge occurred
Next task: identify or restore the canonical ASL-1 implementation and manifest as an existing declared repository surface, then verify locally before re-enabling report publication
```

## Prior Failure Handling

```text
Event: GitHub Actions failure notification
Repository: StegVerse-Labs/StegVerse-SCW
Branch: main
Workflow: taskops-nightly
Job: refresh
Run: 29143978376
Commit: 8c4da5f13427321d1250323f1dd527b366eb6e82
Failure class: missing local script / stale workflow reference
Observed cause: scripts/autodocs_probe_pr_safe.py completed and updated AutoDocs outputs, then the job attempted to execute scripts/taskops_autodocs_link.py, which is absent from the repository and has no current repository reference implementation
Repair commit: 79f4455f81e321a028e899dea71b3b2a9051aa29
Repair behavior: taskops-nightly now runs the existing AutoDocs probe and continues to the existing commit and CI-dashboard refresh steps without calling the nonexistent linker
Authority effect: none; no workflow was added, no external repository was modified, and no deployment, release, tag, merge, or cross-repository authority was exercised
Verification: static workflow verification complete; next scheduled run required to verify execution and publication behavior
```

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

Restore or locate the canonical ASL-1 alignment implementation without inventing a new authority surface. Separately resolve the StegTVC source-read credential boundary before any cross-repository synchronization attempt. Then continue the previously declared verification sequence for `taskops-nightly` and `export-hcb-nightly`.

## Known Remaining Work

Destination: `StegVerse-Labs/StegVerse-SCW`

- restore or locate the canonical `scripts/genesis/repo_alignment_check.py` implementation and matching manifest
- verify ASL-1 locally before allowing report publication
- verify the StegTVC source repository can be read with explicitly authorized credentials
- ensure unavailable cross-repository authority produces a bounded preflight result rather than an attempted mutation
- verify `taskops-nightly` passes and safely publishes AutoDocs/CI-dashboard updates
- verify multi-repo autopatch report publication passes after concurrency repair
- verify StegTV connectivity execution and report publication pass after credential and authority preflight
- verify backup workflow records a clean skip when destination access is absent
- verify `export-hcb-nightly` produces a job and dispatches the dry-run export workflow
- inspect the dispatched `export-hcb.yml` dry-run for local dependency, token, or payload-validation failures
- inspect repository-wide CodeQL and validation cascade separately from operational workflow repairs

## Build Rule

Prefer existing declared scripts and task surfaces. Keep commit steps safe when no files changed or when `main` advances during execution. Optional external destinations must be preflighted and may not convert unavailable authority into a repository failure. Do not claim downstream completion without evidence.

## Next Integration Candidate

Publish verified SCW status through existing Site and Publisher paths after local checks are green.
