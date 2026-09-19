# One-Button Supercheck Read-Only Replacement Receipt

Date: 2026-07-14
Repository: `StegVerse-Labs/StegVerse-SCW`

## Prior state preserved

The previous `.github/workflows/one_button_supercheck.yml` blob was:

`88b2d75b8c11fd3428783dc14b9a192041ea4a63`

That workflow mixed diagnostics, YAML mutation, repository edits, auto-triage, PR creation, direct pushes, inline script scaffolding, and invalid step-level reusable-workflow calls. It also allowed a push-triggered execution path and broad write permissions.

## Replacement

Commit:

`2f2e7c15debb15b35950dc14eba78f08dfcadc8a`

The same workflow path now provides a bounded, manually dispatched, read-only supercheck.

### Current behavior

- `contents: read` only.
- No push trigger.
- No YAML correction or repository mutation.
- No script seeding, branch creation, PR creation, direct push, or secret-dependent action.
- Generates JSON and Markdown workflow inventory evidence.
- Classifies top-level workflows, nested workflow files, parse failures, manual dispatch support, and reusable workflow support.
- Optionally performs GET-only API checks against:
  - `/v1/ops/health`
  - `/v1/ops/env/required`
  - `/v1/ops/config/status`
- Uploads evidence as a 14-day artifact.
- Calls the canonical `.github/workflows/telemetry-reusable.yml` at job level.

## Authority effect

No workflow was executed by this change. No repository content other than the workflow and this receipt was mutated. No deployment, release, tag, PAT change, cross-repository operation, automated correction, or authority expansion occurred.

## Required validation

1. Execute `One-Button Supercheck (Read-Only)` with API checks disabled.
2. Retain and inspect the `one-button-supercheck-read-only` artifact.
3. Confirm all workflow files are classified and any parse-invalid or nested files are listed.
4. Execute again with API checks enabled only after an explicit current StegVerse-owned/admitted SCW API origin is available; do not select a third-party hosted fallback.
5. Record the workflow run URL, conclusion, artifact ID, inventory counts, and API results in the current handoff or a linked validation receipt.

## Remaining scope

- Reconcile this receipt and the control-nucleus hardening receipts into `docs/SCW_MIRROR_HANDOFF.md`.
- Use inventory evidence to decide the disposition of `.github/workflows/_reusables/telemetry.yml` and other nested workflow files.
- Do not reintroduce mutation behavior into this workflow; mutation must remain in separately reviewed, explicit workflows.
