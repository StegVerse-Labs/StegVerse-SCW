# SCW AI Bridge Dispatch Credential Boundary Mirror Handoff

## Finding

Historical `.github/workflows/forward-to-bridge.yml` materialized the organization secret `GH_STEGVERSE_AI_TOKEN` in a GitHub-hosted runner, authenticated GitHub CLI with it, and performed a cross-repository dispatch to the Hybrid Collaboration Bridge.

That conflicts with the StegVerse authority model:

```text
credential authority: TV/TVC ONLY
GitHub Actions role: VALIDATION_TRANSPORT_ONLY
cross-repository command/control authority: NONE
consumer secret materialization: PROHIBITED
```

## Bounded repair

The existing workflow file is retained but converted to validation-only behavior:

```text
secret interpolation: RETIRED
GH_TOKEN materialization: RETIRED
gh auth login: RETIRED
cross-repository API dispatch: RETIRED
checkout credential persistence: FALSE
workflow permissions: contents: read
replacement state: TVC_ADMITTED_TRANSPORT_REQUIRED
authority_effect: NONE
```

The README instruction to provision `GH_STEGVERSE_AI_TOKEN` is also retired.

## Canonical continuation

A future bridge-forwarding operation may occur only through an already-admitted TV/TVC transport capability that binds exact caller, target repository/service, operation, scope/fence, and secret-free receipt evidence.

The source repair does not create that route and does not prove bridge forwarding, deployment, external provider execution, or runtime activation.

## Lifecycle

```text
source repair: IMPLEMENTED_ON_BRANCH
validation: PENDING
merge: PENDING
live TVC bridge transport: NOT OBSERVED
```


## Exact bounded validation — 2026-08-28

```text
PR: #26
validated head: 13e223d4dcd259cd05ab2e21c371baaef93f55b6
StegVerse AI Bridge Forwarding - Validation Only 33231776023: SUCCESS
```

The exact bridge boundary now proves:

```text
GH_STEGVERSE_AI_TOKEN interpolation: RETIRED
GH_TOKEN bridge materialization: RETIRED
gh auth login: RETIRED
cross-repository bridge API dispatch: RETIRED
workflow permissions: contents read
checkout credential persistence: false
replacement state: TVC_ADMITTED_TRANSPORT_REQUIRED
GitHub Actions role: VALIDATION_TRANSPORT_ONLY
authority_effect: NONE
```

Repository-wide checks remain separately red and are not attributed to this bridge repair:

```text
Test Readiness 33231776014: FAILURE
  pre-existing invalid JSON placeholders:
    ledger/events/2025-11-20/ind_events.json
    scripts/entities/registry.json
  repair owner: PR #25

CI 33231776021: FAILURE
  repository-wide Ruff debt: 516 errors
  not introduced by this bridge patch

CodeQL 33231776039: IN_PROGRESS at this evidence write
```

Lifecycle:

```text
source repair: IMPLEMENTED
bounded bridge validation: VALIDATED
repository-wide validation: NOT GREEN
merge: NOT MERGED / BLOCKED BY SEPARATE REPOSITORY GATES
live TVC bridge transport: NOT OBSERVED
```

## Current-base rematerialization — 2026-08-28

```text
new base main: 03196636f0a21b3c7744872d5c106b2cc6529763
prior PR head: 54eaee35a12a681aaa591d8d38faf515c938757f
rematerialization: SAME_BOUNDED_FOUR_FILE_REPAIR
fresh exact-head validation: PENDING
merge: PENDING
live TVC bridge transport: NOT OBSERVED
```

PR #25 is now merged on the base and the two legacy JSON placeholders are no longer a Test Readiness blocker. Repository-wide Ruff/CodeQL debt remains separately owned and is not absorbed into CMC-034.


## Merged source closure — 2026-08-28

The bounded repair was rematerialized on current main after PR #25 and validated at the exact source head before merge.

```text
PR: #26
validated exact head: 100821e8c9754cdda7461b7b0954e18fa5c2b7ae
StegVerse AI Bridge Forwarding - Validation Only 33233244263: SUCCESS
Test Readiness 33233244246: SUCCESS
CI 33233244303: FAILURE — separate repository-wide Ruff debt
CodeQL 33233244248: FAILURE — separate CodeQL lane
merge: 12fc76a54a51bcf6cfed73bc48d3a60c2719e420
```

Current lifecycle:

```text
source repair: IMPLEMENTED
bounded bridge validation: VALIDATED
source: MERGED
repository-wide validation: NOT GREEN
live TVC bridge transport: NOT OBSERVED
replacement state: TVC_ADMITTED_TRANSPORT_REQUIRED
authority_effect: NONE
```

The merge retires the hosted credential/materialization and cross-repository dispatch path only. It does not create a replacement transport capability, provider execution path, deployment, activation, or runtime authority.
