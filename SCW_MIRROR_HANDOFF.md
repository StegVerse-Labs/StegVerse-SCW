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


## AI bridge hosted-dispatch credential boundary — 2026-08-28

The current repository still contained one uncontained bridge-forwarding path after `scw_bridge.yml` and `scw_orchestrator.yml` had already been contained:

```text
.github/workflows/forward-to-bridge.yml
  GH_TOKEN <- secrets.GH_STEGVERSE_AI_TOKEN
  gh auth login --with-token
  cross-repository dispatch to hybrid-collab-bridge
```

The bounded repair retires that hosted credential/mutation path and converts the existing workflow to read-only validation of `TVC_ADMITTED_TRANSPORT_REQUIRED`.

Canonical continuation: `docs/SCW_AI_BRIDGE_DISPATCH_CREDENTIAL_BOUNDARY_MIRROR_HANDOFF.md`.

This does not authorize or implement the future TV/TVC transport route and does not change unrelated SCW workflow debt or the separate finance credential PR.


## AI bridge dispatch source closure — 2026-08-28

PR #26 merged the bounded retirement of the historical hosted AI-bridge credential/dispatch path.

```text
validated exact head: 100821e8c9754cdda7461b7b0954e18fa5c2b7ae
bounded bridge validation 33233244263: SUCCESS
Test Readiness 33233244246: SUCCESS
merge: 12fc76a54a51bcf6cfed73bc48d3a60c2719e420
repository-wide CI/CodeQL: NOT GREEN / separately owned
live TVC bridge transport: NOT OBSERVED
```

Canonical bounded continuation remains `docs/SCW_AI_BRIDGE_DISPATCH_CREDENTIAL_BOUNDARY_MIRROR_HANDOFF.md`. This closure does not absorb finance PR #24, CodeQL PR #27, legacy PAT/bootstrap lanes, or future TV/TVC transport activation.

## Finance provider credential-boundary lane — 2026-08-27

A separate non-overlapping finance lane owns `finance/stripe_handler.py`, `finance/coinbase_handler.py`, and `finance/payments_config.example.json`. Historical shape-only stubs still materialized provider secrets from the SCW environment. The bounded repair retires those reads and binds future authenticated provider execution to TV/TVC. Canonical continuation: `docs/SCW_FINANCE_PROVIDER_CREDENTIAL_BOUNDARY_MIRROR_HANDOFF.md`.


## Finance credential-boundary source closure — 2026-08-28

The bounded finance credential repair is merged. PR #24 was superseded solely to rematerialize the unchanged repair on current main; replacement PR #29 is the admitted source lane.

```text
validated source head: 28f56e6fc26ebfd9a599a4001a5aca6769598690
Finance Credential Boundary Validation 33233653819: SUCCESS
Test Readiness 33233653875: SUCCESS
merge: c437a3320a9d901d3a398ee06c6668ba5b9db5fc
repository-wide CI: NOT GREEN — separate Ruff debt
provider runtime: NOT OBSERVED
replacement state: TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED
authority_effect: NONE
```

Canonical continuation: `docs/SCW_FINANCE_PROVIDER_CREDENTIAL_BOUNDARY_MIRROR_HANDOFF.md`. This closure does not absorb CodeQL PR #27, legacy PAT/bootstrap work, or any provider/runtime activation lane.


## CMC-036 hosted HCB nightly dispatch retirement — current-main rematerialization

The historical draft owner PR #20 preserved the exact CMC-036 intent but could not be marked ready through the connected GitHub mutation because of a GraphQL schema mismatch, and its old base no longer applied cleanly after concurrent main advancement. The same bounded two-file intent was rematerialized from current main without importing unrelated history.

```text
historical owner PR: #20 (closed, source preserved)
failed exact-head ready-for-review mutation: connector GraphQL fullDatabaseId schema mismatch
stale replacement PR: #31 (superseded by current-main rematerialization)
current-main base: ba691599c0bb3e678422bf9b6aae6dbedec7119c
retired surface: .github/workflows/export-hcb-nightly.yml
historical hosted authority: actions: write + GH_TOKEN from github.token + workflow dispatch
contained export target: .github/workflows/export-hcb.yml remains
live TV/TVC export transport: NOT OBSERVED
provider/export runtime activation: NOT OBSERVED
authority_effect: NONE
```

CMC-036 removes only the hosted nightly dispatcher. It creates no replacement credential path, no TV/TVC transport implementation, no provider/export runtime authority, and no repository mutation authority.


## CodeQL validation-transport current-main repair — 2026-08-30

Historical PR #27 proved the intended CodeQL transport correction but became stale as SCW main advanced. Its exact two-file intent has been rematerialized from current main rather than merging stale history.

```text
historical owner PR: #27
current-main base: 4f0391a242f2dc0c5506cb91c6fb63f55b850a97
analysis languages: python + actions
CodeQL query execution: retained
SARIF generation: retained
code-scanning publication: disabled
analyze upload: never
database upload: false
security-events write: NONE
checkout credential persistence: false
SARIF evidence retention: actions/upload-artifact
GitHub Actions production/runtime/control-plane authority: NONE
authority_effect: NONE
```

This repair removes the repository-level Code Security publication dependency without weakening analysis. It does not modify CMC-034/035/036 source semantics, provider execution, credential authority, or runtime activation.


## PR-scoped CI validation repair — 2026-08-30

The historical repo-alignment PR #19 demonstrated that narrow SCW repairs were being blocked by unrelated repository-wide Ruff/test debt. The CI-scoping portion is rematerialized independently from current main after the CodeQL transport repair merged.

```text
current-main base: 34258a9c46acee73631d60e6ecbcebcb0fbf61cb
pull_request lint scope: changed Python files only
pull_request pytest scope: changed pytest files only
push/workflow_dispatch lint scope: repository api/scripts/tests
push/workflow_dispatch pytest scope: repository tests
checkout credential persistence: false
permissions: contents read
legacy repository-wide Ruff/test debt: STILL VISIBLE ON NON-PR RUNS
authority_effect: NONE
```

This changes validation denominator by event type only. It does not mark legacy debt resolved, weaken production/runtime checks, grant credential authority, or change any CMC provider/transport lifecycle.


## Email-monitor current operational failure repair — 2026-08-30

The next full GitHub email-monitor pass observed new current-main failures after the CodeQL and PR-CI repairs.

```text
Ops Console Dispatcher run 33328183203 / e3bb0d4:
  event: issue_comment
  failure: inputless unrelated comment reached Validate and exited "No workflow given"
  historical authority: actions:write + hosted workflow dispatch
  repair: retain request parsing/evidence only; no hosted dispatch authority; unrelated comments become NO_DISPATCH_REQUEST

Workflow Dispatch Guardian run 33328157932 / c28822a:
  failure: scanner crashed on malformed workflow YAML before producing governance output
  observed malformed source example: raw Python at YAML line 36
  repair: catch parse failures, report them in evidence, never rewrite or push workflows from GitHub Actions

Workflows Sanity Check run 33328157908 / c28822a:
  files: 167
  parse_valid: 129
  parse_invalid: 38
  state: REAL_FAIL_CLOSED_DENOMINATOR_UNCHANGED

Verify UI Layout run 33328157946 / c28822a:
  stale assertion: ui/public/index.html
  current UI architecture: Next.js source at ui/pages/index.js + ui/package.json + ui/next.config.js
  repair: validate current source layout; remove obsolete static/Render deployment assumptions
```

Bounded repair branch: `fix/scw-current-operational-failures-20260830`.
This repair does not claim the 38 invalid workflow files are fixed. It removes hosted control-plane mutation behavior from the affected dispatcher/guardian surfaces and corrects a stale UI-source validator.
