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

The broken workflows were labeled primarily with YAML `ScannerError` or `ParserError`.

### Diagnostic distinction

- `ScannerError` and `ParserError` are workflow-file parsing failures. They occur before jobs execute and are not caused by an expired PAT.
- An expired, revoked, or under-permissioned PAT may still be a secondary runtime blocker after a workflow parses and starts.
- PAT failure evidence must come from runtime errors such as `401`, `403`, `Bad credentials`, push rejection, inaccessible resource, or failed workflow dispatch.
- `no-dispatch` is not equivalent to broken. It may indicate a valid push-, schedule-, workflow-call-, or repository-dispatch-only workflow, or a workflow whose dispatch trigger is not recognized.

## Completed work

- Established this durable handoff.
- Preserved the parser-error versus PAT-error decision.
- Preserved the January 2026 Ops Console counts.
- Recorded that no bulk rescue, stub replacement, PAT rotation, release, tag, or workflow repair was previously verified as completed.

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
- `.github/workflows/setup-common-python.yml`

## Safety constraints

- Do not overwrite malformed workflows without preserving their original content or commit reference.
- Do not assume every no-dispatch workflow requires `workflow_dispatch`.
- Do not treat PAT rotation as a YAML repair.
- Prefer `GITHUB_TOKEN` for same-repository operations and least-privilege PAT access only where cross-repository operations require it.
- Preserve iPhone-friendly recovery paths and complete-file replacements.

## Known remaining work

- Verify the current contents and parse status of the 40 workflows previously labeled broken.
- Determine whether `setup-common-python.yml` is a misplaced composite action.
- Identify duplicate workflows and naming collisions such as multiple autopatch variants.
- Establish an automated parser report that does not mutate files.
- Repair and validate the minimal control nucleus.
- Run separate PAT health validation after parse-valid workflows are available.
- Recompute Ops Console counts from current repository state.

## Ownership

- Current recovery owner: StegVerse-SCW workflow recovery task.
- Continuation may be performed by any authorized session or automation that reads this file first and records mutations and validation evidence durably.

## Archival condition for originating diagnostic session

The originating diagnostic continuity gap is closed by this committed handoff. Future work no longer requires access to that conversation, provided this file remains available.
