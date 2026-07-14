# StegVerse-SCW Mirror Handoff

_Last updated: 2026-07-14_

## Repository

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-SCW`
- Continuation authority: this file is the current handoff and task source of truth for workflow recovery until superseded by a newer committed handoff.

## Current durable findings

The Ops Console snapshot supplied from 2026-01-03 reported:

- OK: 0
- No dispatch: 110
- Broken: 40
- Total workflows observed: 150

The snapshot is historical and must not be treated as the current repository count without regeneration.

The broken workflows were labeled primarily with YAML `ScannerError` or `ParserError`.

### Diagnostic distinction

- `ScannerError` and `ParserError` are workflow-file parsing failures. They occur before jobs execute and are not caused by an expired PAT.
- An expired, revoked, or under-permissioned PAT may still be a secondary runtime blocker after a workflow parses and starts.
- PAT failure evidence must come from runtime errors such as `401`, `403`, `Bad credentials`, push rejection, inaccessible resource, or failed workflow dispatch.
- `no-dispatch` is not equivalent to broken. It may indicate a valid push-, schedule-, workflow-call-, or repository-dispatch-only workflow, or a workflow whose dispatch trigger is not recognized.

## Completed work

- Established this durable handoff in commit `e4f8284accafce648f1b777e6d5d20efb2708e0a`.
- Preserved the parser-error versus PAT-error decision.
- Preserved the January 2026 Ops Console counts as historical evidence.
- Inspected `.github/workflows/workflow_preflight.yml`; its current file was structured YAML, so the January broken label no longer represented its present shape.
- Inspected `.github/workflows/setup-common-python.yml`; it was malformed YAML and attempted to express a composite action from inside the workflows directory.
- Confirmed the intended composite action already exists at `.github/actions/setup-common-python/action.yml`.
- Replaced the malformed `setup-common-python.yml` with a valid, read-only, manually dispatchable smoke-test workflow in commit `786453329b4c4c803527298cf21c96937ded579e`.
- Inspected `.github/workflows/_reusables/telemetry.yml`; blob `d2bc52a3ff4be5853fdca402a62287fbbfdc79f7` contains two concatenated reusable-workflow definitions and is not safe to call.
- Added a valid top-level reusable workflow at `.github/workflows/telemetry-reusable.yml` in commit `3e4e8654b122759d8413fedeeaea87aea32f1c97`.
- Rewired `workflow_preflight.yml` to the top-level reusable telemetry workflow, changed manual mutation defaults to false, removed swallowed validator and push failures, and made fallback output explicitly unvalidated in commit `aab8e268a819860eccecc18a2aa8d9b1535dedc6`.
- Inspected `.github/workflows/neutralize_secrets_if.yml`; current blob `976265cdefe48767ab1799926d6671195e514495` is structured and manually dispatchable, but remains a high-risk bulk mutator and has not been run.
- Upgraded `.github/workflows/workflows-sanity-check.yml` from a shallow parse loop into a recursive, read-only workflow inventory gate producing JSON and Markdown artifacts in commit `ecf7ec713de2b1846eb9af72dc14fd86a18cd4f7`.
- Inspected `scripts/patches/repair_workflow_yaml.py`; prior blob `8eef282036ce5be54d4c3052fda6b87f411ff679` used PyYAML parsing followed by full-file dumping. That could reinterpret GitHub's `on` key as boolean false, remove comments, alter quoting, and rewrite expressions.
- Replaced the repair script with a loss-minimizing engine in commit `247542dcb14883ac568309909642b6fe11a8c587`. It reports parser failures using a GitHub-aware loader and only applies line-ending, trailing-space, and final-newline normalization. It never automatically replaces tabs or structurally re-dumps YAML.
- Rebuilt `.github/workflows/repair-bad-yaml.yml` in commit `f7ab3277c73e29df8f639f07481f21b535e16638`. Apply mode now requires exactly one reviewed top-level target, default mode is report-only, reports are uploaded, and only the selected file can be staged.
- Inspected `.github/workflows/ops-console.yml`; prior blob `634697b55984d6f2e2200515a90cad53f0d23f95` could dispatch any top-level manually dispatchable workflow.
- Restricted `.github/workflows/ops-console.yml` to the reviewed control nucleus in commit `34dc85b5d0a91b13a2c84bba1154b741a2e46f16`. It records actor, ref, workflow, and reason, and dispatches targets with their safe defaults.
- No bulk stubbing, bulk mutation, PAT rotation, release, or tag has been performed.

## Active goal

Restore a trustworthy workflow control plane without destroying recoverable workflow intent.

## Required execution order

1. Inspect current repository files before mutation.
2. Classify each workflow as valid, invalid YAML, misplaced composite action, intentionally non-dispatchable, duplicate, obsolete, or operational.
3. Repair a minimal control nucleus first rather than stubbing every broken workflow.
4. Validate YAML parsing independently.
5. Run a minimal read-only workflow.
6. Test repository write permission using `GITHUB_TOKEN` where sufficient.
7. Test any PAT-dependent cross-repository or dispatch operation separately.
8. Record receipts, failures, and repaired-file inventory here or in linked durable task records.

## Initial control nucleus

- `.github/workflows/ops-console.yml` — restricted to reviewed control workflows; execution validation pending.
- `.github/workflows/workflow_preflight.yml` — repaired; execution validation pending.
- `.github/workflows/workflows-sanity-check.yml` — repaired into inventory gate; execution validation pending.
- `.github/workflows/repair-bad-yaml.yml` — rebuilt as bounded report/safe-normalization workflow; execution validation pending.
- `.github/workflows/neutralize_secrets_if.yml` — parse-structured; quarantined from execution pending inventory results and review.
- `.github/workflows/setup-common-python.yml` — repaired; execution validation pending.
- `.github/workflows/telemetry-reusable.yml` — installed; caller validation pending.

## Safety constraints

- Do not overwrite malformed workflows without preserving their prior blob or commit reference.
- Do not assume every no-dispatch workflow requires `workflow_dispatch`.
- Do not treat PAT rotation as a YAML repair.
- Prefer `GITHUB_TOKEN` for same-repository operations and least-privilege PAT access only where cross-repository operations require it.
- Preserve iPhone-friendly recovery paths and complete-file replacements.
- Do not run `neutralize_secrets_if.yml` or another bulk mutator until the read-only inventory has identified exact targets and a reviewed mutation plan exists.
- Do not rely on `.github/workflows/_reusables/telemetry.yml`; use `.github/workflows/telemetry-reusable.yml`.
- Do not restore full-document PyYAML dumping as a repair mechanism.
- Apply-mode YAML repair must name exactly one reviewed top-level workflow file.
- The Ops Console allowlist must not be expanded to bulk mutators without review and a recorded reason.

## Known remaining work

- Execute and inspect `Workflows Sanity Check`; persist its artifact summary or failure evidence.
- Execute and inspect `Validate Setup Common Python`.
- Execute and inspect `Workflow Preflight` in its default read-only mode.
- Execute and inspect `Repair Bad Workflow YAML` in default report-only mode.
- Execute and inspect the restricted `Ops Console`, initially dispatching `workflows-sanity-check.yml`.
- Decide whether to delete, archive, or convert the malformed nested `_reusables/telemetry.yml` after all callers are migrated.
- Verify the current contents and parse status of workflows historically labeled broken using the generated inventory.
- Identify duplicate workflows and naming collisions such as multiple autopatch variants.
- Run separate PAT health validation after parse-valid same-repository workflows have executed.
- Recompute Ops Console counts from current repository state.

## Installed and missing components

### Present

- Composite action: `.github/actions/setup-common-python/action.yml`
- Smoke-test workflow: `.github/workflows/setup-common-python.yml`
- Read-only inventory gate: `.github/workflows/workflows-sanity-check.yml`
- Top-level reusable telemetry workflow: `.github/workflows/telemetry-reusable.yml`
- Rewired preflight workflow: `.github/workflows/workflow_preflight.yml`
- Bounded repair engine: `scripts/patches/repair_workflow_yaml.py`
- Bounded repair workflow: `.github/workflows/repair-bad-yaml.yml`
- Reviewed control dispatcher: `.github/workflows/ops-console.yml`

### Pending verification or repair

- Execution receipts for the repaired control workflows.
- Full current workflow inventory artifact.
- Malformed nested telemetry file disposition.
- Duplicate and obsolete workflow classification.
- PAT-dependent cross-repository dispatch and write pathways.

Destination: `StegVerse-Labs/StegVerse-SCW`.

## Ownership

- Current recovery owner: StegVerse-SCW workflow recovery task.
- Continuation may be performed by any authorized session or automation that reads this file first and records mutations and validation evidence durably.

## Archival condition for originating diagnostic session

The originating diagnostic continuity gap is closed by this committed handoff. Future work no longer requires access to that conversation, provided this file remains available.
