# TaskOps Nightly Validation Boundary Mirror Handoff

Updated: 2026-09-05
Repository: `StegVerse-Labs/StegVerse-SCW`
Parent authority: `SCW_MIRROR_HANDOFF.md` + `docs/SCW_SECURITY_MIRROR_HANDOFF.md`
Canonical security task: issue `#22`
Branch: `contain/taskops-nightly-validation-only`

## Purpose

Contain the remaining hosted mutation behavior in `.github/workflows/taskops-nightly.yml` while preserving useful scheduled/manual AutoDocs validation and evidence generation.

## Preflight finding

The live workflow on `main` still had:

```text
schedule + workflow_dispatch
permissions.contents: write
actions/checkout with default credential persistence
ad-hoc PyYAML install
local AutoDocs generation
bot git identity configuration
direct commits to README.md and .github/docs/
direct git push to main
call to absent scripts/readme_ci_dashboard.py with `|| true`
second direct commit/push to main
```

No existing open or historical PR was found that owns this exact `taskops-nightly` containment. Historical TaskOps PR #6 is unrelated to this authority repair.

`export-hcb-nightly.yml`, which older root-handoff prose still lists for verification, is already absent from current `main` and is treated as superseded/retired rather than recreated.

## Authority boundary

```text
credential/secret/token authority: TV/TVC ONLY
GitHub Actions runtime/production/control-plane authority: NONE
GitHub Actions role here: validation/evidence transport only
repository mutation authority from taskops-nightly: NONE
publication authority from taskops-nightly: NONE
artifact existence implies publication: false
artifact existence implies runtime activation: false
```

## Repair

The existing workflow is retained, not replaced with a new workflow.

New behavior:

```text
trigger: schedule + workflow_dispatch retained
permissions.contents: read
checkout persist-credentials: false
AutoDocs probe: retained
PyYAML install: retained solely as existing validation dependency of autodocs_probe_pr_safe.py
README/.github/docs changes: local checkout only
proposed delta: taskops-proposed.patch
output retention: actions/upload-artifact@v4
bot git identity: removed
git commit: removed
git push: removed
absent readme_ci_dashboard.py invocation: removed
durable publication: NONE
```

The retained artifact includes:
- `taskops-proposed.patch`
- `.github/docs/PR_SAFE_STATUS.md`
- generated checkout `README.md`

These are proposed/evidence outputs only.

## README completeness predicate

This repair materially changes scheduled workflow mutation authority, publication semantics, output handling, and failure behavior. `README.md` is therefore required in the same change set.

README now states that TaskOps nightly is validation/evidence-only, uses read-only contents permissions, does not persist checkout credentials, does not configure a bot identity, does not commit/push to `main`, retires the missing dashboard-script call, and requires separately admitted mutation/publication authority for durable application.

README completeness: `SATISFIED_IN_BRANCH`.

## Validation boundary

Hosted workflow/CI success after this source change may validate syntax and proposed-output behavior. It does not prove sovereign runtime execution, TV/TVC credential activation, publication, or production activation.

A post-merge scheduled/manual TaskOps run may establish that the validation-only workflow executes and retains its artifact, but that run still grants no repository mutation authority.

## Remaining machine work

1. Open and validate the bounded containment PR.
2. Merge only if exact-head validation and current-main collision checks pass.
3. After merge, observe one real TaskOps validation-only execution and inspect the retained artifact.
4. Keep durable application of generated documentation behind a separately admitted mutation/publication path.
5. Reconcile stale root-handoff references that describe TaskOps as directly publishing or `export-hcb-nightly` as still present.

## User work

NONE currently required.

## Completion boundary

Source containment can be complete after validated merge. Operational validation-only proof requires one observed execution of the merged workflow. No result from this lane constitutes runtime or publication activation.
