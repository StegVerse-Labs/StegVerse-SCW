# SCW Telemetry Caller Migration Receipt

Date: 2026-07-14
Repository: `StegVerse-Labs/StegVerse-SCW`

## Completed

Commit `849eb4f7295f5f1d88a7da4d1795ce136b502b34` migrated `.github/workflows/rebuild-kit.yml` from the malformed nested reusable workflow reference:

`./.github/workflows/_reusables/telemetry.yml`

to the declared top-level reusable workflow:

`./.github/workflows/telemetry-reusable.yml`

The rebuild workflow remains read-only and uploads its reconstruction bundle plus telemetry artifacts.

## Remaining caller blocker

`.github/workflows/one_button_supercheck.yml` still references nested workflow files from step-level `uses` entries, including `_reusables/telemetry.yml` and `_reusables/upload-sweep.yml`. Reusable workflows cannot be invoked as steps. The workflow also contains broad mutation behavior and must not be dispatched or activated by a trigger until it is reviewed and replaced or decomposed.

Preserved source blob for review: `88b2d75b8c11fd3428783dc14b9a192041ea4a63`.

## Required continuation

1. Keep `one_button_supercheck.yml` out of the trusted control nucleus.
2. Inventory every mutation and external call in that workflow.
3. Replace invalid step-level reusable-workflow calls with valid actions or job-level reusable callers.
4. Default all mutation controls to disabled and remove automatic push activation before execution validation.
5. After all callers have migrated, decide whether to delete or archive `.github/workflows/_reusables/telemetry.yml`.

## Authority effect

No workflow was executed. No release, tag, deployment, PAT change, cross-repository mutation, or bulk repair occurred.
