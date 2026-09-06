# HCB Weekly Export Containment Mirror Handoff

Updated: 2026-09-06
Repository: `StegVerse-Labs/StegVerse-SCW`
Parent authority: `SCW_MIRROR_HANDOFF.md` + `docs/SCW_SECURITY_MIRROR_HANDOFF.md`
Canonical security task: issue `#22`
Branch: `contain/export-hcb-weekly`

## Purpose

Contain the surviving `.github/workflows/export-hcb-weekly.yml` hosted cross-repository export surface without recreating a scheduler, credential path, or mutation owner.

## Preflight finding

Before this repair, the weekly workflow:

```text
triggered on a Monday schedule plus workflow_dispatch
held contents: write and pull-requests: write
validated a local HCB payload
invoked ./.github/workflows/export-hcb.yml as a reusable workflow
used secrets: inherit
requested push_strategy: direct
dry_run: false
```

The target `export-hcb.yml` is already contained and exposes only `workflow_dispatch`, so the weekly reusable-workflow call is also structurally stale. The historical semantics conflict with the current security boundary that GitHub Actions is validation/evidence transport only and TV/TVC is the sole credential authority.

No open PR was found owning this exact weekly-export containment.

## Repair

The existing path is retained in place.

New behavior:

```text
trigger: workflow_dispatch only
scheduled execution: removed
permissions.contents: read
pull-requests write: removed
secrets inheritance: removed
reusable export call: removed
non-dry-run export request: removed
cross-repository mutation: NONE
publication/release/tag authority: NONE
```

The remaining manual workflow fails closed with an explicit explanation that any future HCB export requires separately admitted TV/TVC source-read and mutation authority with exact source/target refs and secret-free receipts.

## README completeness predicate

The proposed change materially removes historical weekly scheduling and mutation semantics, so README impact was evaluated before functional mutation.

Explicit determination: `NO_README_CHANGE_REQUIRED`.

Evidence:
- root `README.md` already states the repository-wide invariant that GitHub Actions is validation/evidence transport only and must not hold cross-repository command or mutation authority;
- root `README.md` does not advertise, document, or promise a weekly HCB export capability;
- this repair enforces that already-documented global boundary and creates no new capability, prerequisite, interface, authority, dependency, or production behavior.

Therefore changing README text would add duplicate policy rather than complete missing capability documentation.

## Authority boundary

```text
credential authority: TV/TVC ONLY
GitHub Actions production/runtime/control-plane authority: NONE
weekly HCB scheduled execution: NONE
cross-repository mutation authority: NONE
publication/tag/release authority: NONE
source merge implies export execution: false
hosted validation implies export execution: false
```

## Validation boundary

PR/CI success may prove syntax and source containment only. It does not prove an HCB export, private-source materialization, TV/TVC activation, publication, release, sovereign runtime execution, or production activation.

## Remaining machine work

1. Open and validate the bounded containment PR.
2. Merge only if exact-head validation and current-main collision checks pass.
3. Keep both `export-hcb-weekly.yml` and `export-hcb.yml` contained until separately admitted TV/TVC export predicates exist.
4. Reconcile stale parent-handoff wording that still expects the retired nightly dispatcher or hosted weekly real-export behavior.

## User work

NONE currently required.

## Completion boundary

Source containment can be complete after validated merge. No post-merge hosted run is required to prove that a real export occurred because real export remains intentionally prohibited; future export execution requires separately admitted authority and authentic evidence.
