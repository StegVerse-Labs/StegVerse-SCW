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
- restored ASL-1 execution by pointing `.github/workflows/alignment_check.yml` at the existing canonical `scripts/genesis/guardian_repo_alignment_check.py` implementation and its declared `docs/governance/repo_alignment_expectations.yaml` configuration
- aligned the repaired ASL-1 workflow with the existing token fallback contract and added fetch/rebase-before-push protection for report publication

## Latest Repair

```text
Event: repository repair
Repository: StegVerse-Labs/StegVerse-SCW
Branch: main
Workflow: StegVerse Guardian Worker – Repo Alignment Check
Commit: ff99291108fe3ad48d2f6f35d7093de435f8de98
Failure class repaired: stale workflow reference to absent scripts/genesis/repo_alignment_check.py and absent scripts/genesis/repo_alignment_manifest.json
Canonical implementation identified: scripts/genesis/guardian_repo_alignment_check.py
Canonical configuration identified: docs/governance/repo_alignment_expectations.yaml
Repair behavior: the existing workflow now runs the existing ASL-1 implementation, preserves PAT_WORKFLOW/GH_STEGVERSE_PAT fallback, and safely rebases before publishing changed reports
Authority effect: none; no new workflow, external repository mutation, release, tag, merge, deployment, or authority expansion was introduced
Verification: static path/config verification complete; next scheduled or explicitly authorized workflow run must confirm execution, source-repository readability, report generation, and safe publication
```

## Latest Failure Handling

```text
Event: GitHub Actions failure notification
Repository: StegVerse-Labs/StegVerse-SCW
Branch: main
Workflow: StegTV Connectivity Autopatch
Job: stegtvc-connectivity
Run: 29188787382
Commit: f1b160304924ef9ae80a7061e5d9109c09c3bb1d
Failure class: recurring external repository authentication failure
Observed cause: scripts/stegtvc_connectivity_autopatch.py invoked `gh repo clone StegVerse-Labs/TVC`; GitHub CLI returned HTTP 401 Bad credentials before any target repository mutation occurred
Evidence: checkout, token resolution, Python setup, and dependency installation succeeded; the first source-repository clone failed, a local report was written, and the commit step was skipped
Repair status: blocked; changing token scope, substituting credentials, or authorizing cross-repository mutation is outside the current handoff
Authority effect: none; no external repository was modified, no report commit was pushed, and no deployment, release, tag, merge, or authority expansion occurred
Next task: establish an explicitly authorized read-only credential/preflight contract for `StegVerse-Labs/TVC`; do not retry mutation-capable synchronization until that boundary is verified
```

```text
Event: GitHub Actions failure notification
Repository: StegVerse-Labs/StegVerse-SCW
Branch: main
Workflow: StegVerse Guardian Worker – Repo Alignment Check
Job: alignment_check
Run: 29188553744
Commit: 7611f5158c73a4db5704abf6fc8d78927fe872c0
Failure class: recurring missing local declared script
Observed cause: the workflow invoked `scripts/genesis/repo_alignment_check.py --manifest scripts/genesis/repo_alignment_manifest.json --write-latest`; the script path is absent and Python exited with Errno 2 before alignment evaluation or report publication
Evidence: checkout, token resolution, Python setup, and dependency installation succeeded; the first failing step was the declared ASL-1 script invocation
Repair status: repaired by commit ff99291108fe3ad48d2f6f35d7093de435f8de98 using the existing canonical ASL-1 implementation and configuration
Authority effect: none; no new workflow or authority surface was introduced
Next task: verify the repaired workflow through the next scheduled or explicitly authorized run
```

## Prior Failure Handling

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
Repair status: repaired by commit ff99291108fe3ad48d2f6f35d7093de435f8de98
Authority effect: none; no workflow was added and no external repository was modified
Next task: verify the repaired workflow through execution
```

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

Verify the repaired ASL-1 workflow through execution. Separately resolve the StegTVC source-read credential boundary before any cross-repository synchronization attempt. Then continue the previously declared verification sequence for `taskops-nightly` and `export-hcb-nightly`.

## Known Remaining Work

Destination: `StegVerse-Labs/StegVerse-SCW`

- verify the repaired ASL-1 workflow runs the canonical implementation and writes the declared reports
- verify ASL-1 can read each configured target with explicitly authorized credentials
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


## JSON placeholder readiness repair — 2026-08-28

Repository-wide Test Readiness identified two syntactically invalid legacy JSON placeholders unrelated to the active finance credential lane:

```text
ledger/events/2025-11-20/ind_events.json
  prior bytes: "$ 0.00\n"
  reader found in current source: NONE
  repair: preserve exact value as JSON string "$ 0.00"

scripts/entities/registry.json
  prior bytes: blank line
  active entity registry reader path: ROOT/entities/registry.json
  scripts/entities/registry.json reader found in current source: NONE
  repair: normalize unused placeholder to empty JSON object {}
```

This is repository-readiness hygiene only. It does not create or change ledger balances, entity definitions, credential authority, finance provider execution, or runtime authority.
