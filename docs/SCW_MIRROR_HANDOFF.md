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
- Inspected `.github/workflows/workflow_preflight.yml`; its current file is structured YAML, so the January broken label may no longer represent its present parse state.
- Inspected `.github/workflows/setup-common-python.yml`; it was malformed YAML and attempted to express a composite action from inside the workflows directory.
- Confirmed the intended composite action already exists at `.github/actions/setup-common-python/action.yml`.
- Replaced the malformed `setup-common-python.yml` with a valid, read-only, manually dispatchable smoke-test workflow in commit `786453329b4c4c803527298cf21c96937ded579e`.
- No bulk stubbing, PAT rotation, release, or tag has been performed.

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

Priority candidates:

- `.github/workflows/ops-console.yml`
- `.github/workflows/workflow_preflight.yml`
- `.github/workflows/workflows-sanity-check.yml`
- `.github/workflows/repair-bad-yaml.yml`
- `.github/workflows/neutralize_secrets_if.yml`
- `.github/workflows/setup-common-python.yml` — repaired; execution validation pending.

## Safety constraints

- Do not overwrite malformed workflows without preserving their prior blob or commit reference.
- Do not assume every no-dispatch workflow requires `workflow_dispatch`.
- Do not treat PAT rotation as a YAML repair.
- Prefer `GITHUB_TOKEN` for same-repository operations and least-privilege PAT access only where cross-repository operations require it.
- Preserve iPhone-friendly recovery paths and complete-file replacements.

## Known remaining work

- Verify the current contents and parse status of workflows historically labeled broken.
- Validate the repaired `Validate Setup Common Python` workflow through GitHub Actions.
- Inspect the reusable telemetry reference in `workflow_preflight.yml`; verify whether `.github/workflows/_reusables/telemetry.yml` is a supported reusable-workflow location and exists.
- Identify duplicate workflows and naming collisions such as multiple autopatch variants.
- Establish an automated parser report that does not mutate files.
- Repair and validate the remaining minimal control nucleus.
- Run separate PAT health validation after parse-valid workflows are available.
- Recompute Ops Console counts from current repository state.

## Installed and missing components

### Present

- Composite action: `.github/actions/setup-common-python/action.yml`
- Smoke-test workflow: `.github/workflows/setup-common-python.yml`

### Pending verification or repair

- Workflow parser/report implementation and its dependencies.
- Reusable telemetry workflow referenced by `workflow_preflight.yml`.
- PAT-dependent cross-repository dispatch and write pathways.

Destination: `StegVerse-Labs/StegVerse-SCW`.

## Ownership

- Current recovery owner: StegVerse-SCW workflow recovery task.
- Continuation may be performed by any authorized session or automation that reads this file first and records mutations and validation evidence durably.

## Archival condition for originating diagnostic session

The originating diagnostic continuity gap is closed by this committed handoff. Future work no longer requires access to that conversation, provided this file remains available.
