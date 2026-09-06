# ASL-1 Materialized Input Repair Mirror Handoff

## Scope

Repository: `StegVerse-Labs/StegVerse-SCW`

Parent handoffs:
- `SCW_MIRROR_HANDOFF.md`
- `docs/SCW_SECURITY_MIRROR_HANDOFF.md`

Canonical security task: issue `#22`
Source repair PR: `#41`
Branch: `repair/asl1-materialized-input`

This bounded repair removes credential acquisition and provider reads from the ASL-1 repository alignment checker. It does not reactivate the contained hosted workflow and does not grant source-read, mutation, report-publication, runtime, release, or credential authority.

## Finding

Current `main` intentionally contains `.github/workflows/alignment_check.yml` because the historical lane used PAT fallbacks, global Git credential rewriting, and direct report pushes. The canonical checker on `main` also directly resolves `PAT_WORKFLOW`, `GH_STEGVERSE_PAT`, or `GITHUB_TOKEN`, calls GitHub APIs, and inspects repository secret names.

That implementation is incompatible with issue #22 and with the current TV/TVC-only credential boundary.

## Repair

Changed surfaces:

```text
README.md
scripts/genesis/guardian_repo_alignment_check.py
docs/governance/repo_alignment_expectations.yaml
tests/test_guardian_repo_alignment_check.py
docs/ASL1_MATERIALIZED_INPUT_CONTRACT.json
docs/ASL1_MATERIALIZED_INPUT_CONTRACT.md
docs/ASL1_MATERIALIZED_INPUT_MIRROR_HANDOFF.md
docs/ASL1_MATERIALIZED_INPUT_STATUS.json
```

New checker contract:

```text
source acquisition: OUTSIDE CHECKER / PRE-MATERIALIZED ONLY
credential inputs: PROHIBITED
network/provider calls: NONE
input: secret-free exact-source materialization manifest
required per target: repo + exact 40-hex source SHA + local path + receipt reference + authority=TV/TVC
alignment evaluation: LOCAL / CREDENTIAL-FREE
report generation: LOCAL ONLY
report publication: NONE
mutation authority: NONE
```

Manifest schema identifier:

`stegverse.scw.repo-alignment-materialization/v1`

The checker fails closed when a configured target is absent, an undeclared target is supplied, an exact SHA is malformed, authority is not `TV/TVC`, a local materialized path is absent, or a secret/token/credential field is present.

The legacy optional checks for `PAT_WORKFLOW` and `GH_STEGVERSE_PAT` secret names are removed from the alignment policy.

## README completeness predicate

This repair materially changes ASL-1 prerequisites, credential semantics, checker input, failure behavior, and authority boundaries. The repository README is therefore part of the required change set rather than optional documentation.

`README.md` now states that:
- the checker is credential-free and must not resolve PAT/GitHub/provider credentials;
- target repositories must already be materialized through an admitted TV/TVC exact-source path;
- the manifest must be secret-free and exact-SHA/receipt bound;
- report generation is local evaluation only;
- materialization, report publication, repository mutation, release, deployment, runtime, and production authority remain separate governed capabilities;
- `.github/workflows/alignment_check.yml` remains contained until the required predicates are actually satisfied.

README completeness state: `SATISFIED_IN_PR_41`.

## TVC dependency

Existing capability: `StegVerse-Labs/TVC` / `tvc.private-source-read.v1`.

Current observed TVC state:

```text
source implementation: VALIDATED + MERGED
credential/grant activation: NOT OBSERVED
live private materialization: NOT OBSERVED
resident exact-source admission: NOT OBSERVED
```

SCW ASL-1 has been recorded as a bounded noncurrent/backlog consumer relationship of the existing TVC private-source-read lane without changing TVC credential semantics or interrupting the currently admitted progression.

Therefore this repair deliberately does not reactivate `.github/workflows/alignment_check.yml`. A future admitted execution owner must supply exact materialized snapshots and secret-free receipt references through TV/TVC authority. GitHub Actions may transport/validate evidence but may not become the source-read or production control plane.

## Coordination / authority state

```text
canonical work intent authority: StegVerse Canonical Work Coordination System
Master Records authority: observed events / custody / reconstructable evidence only
WorkerCoordinator authority: execution claim/fence ownership
Interlock/InTr authority: task admission / governed state transitions
SCW repair owner: issue #22 + PR #41
new competing canonical task identity created by this repair: NO
source/CI implies runtime activation: NO
```

No separate WorkerCoordinator or canonical Task Registry claim for this exact branch was observed during the 2026-09-05 preflight. PR #41 remains the bounded source owner; absence of a central task record is not treated as execution admission or completion evidence.

## Validation

Focused source tests cover:
- exact local materialized snapshot evaluation while `GITHUB_TOKEN` is present but unused;
- rejection of secret-bearing manifest fields;
- fail-closed rejection when configured targets are not supplied.

Historical PR-head validation before the latest README/handoff reconciliation showed:

```text
Test Readiness: SUCCESS
CodeQL - Validation Transport Only: SUCCESS
StegVerse AI Bridge Forwarding - Validation Only: SUCCESS
CI: FAILURE — one Ruff import-order defect in tests/test_guardian_repo_alignment_check.py
```

That exact Ruff defect has been corrected. Fresh validation for the current PR #41 head is required and must be evaluated as source/test evidence only. It does not prove TVC activation or operational ASL-1 execution.

## Remaining machine work

```text
1. Require fresh PR #41 current-head source/test validation to complete successfully.
2. If source validation is green, advance PR #41 through the repository's admitted source-integration controls without claiming runtime activation.
3. Keep the existing hosted alignment workflow contained.
4. After actual TVC materialization activation, bind exact target snapshots to this checker and execute credential-free validation.
5. Reintroduce durable report publication only through a separately admitted bounded mutation/publication capability, if publication remains required.
```

## User work

NONE currently required.

## Completion boundary

Source repair can be complete before runtime activation. ASL-1 operational proof remains incomplete until admitted exact-source materialization, credential-free checker execution, declared report generation, and any separately required safe publication are actually observed.
