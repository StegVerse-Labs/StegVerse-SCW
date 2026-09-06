# ASL-1 Materialized Input Repair Mirror Handoff

## Scope

Repository: `StegVerse-Labs/StegVerse-SCW`

Parent handoffs:
- `SCW_MIRROR_HANDOFF.md`
- `docs/SCW_SECURITY_MIRROR_HANDOFF.md`

Canonical security task: issue `#22`
Source repair PR: `#41`
Source repair merge: `224c6c662e010b9ef49397cf59224476452548a1`
Validated PR head: `0ab3b4b4ac3e15933d194d868b3f8476d154561e`

This bounded repair removes credential acquisition, provider reads, and the undeclared PyYAML prerequisite from the ASL-1 repository-alignment checker. It does not reactivate the contained hosted workflow and does not grant source-read, mutation, report-publication, runtime, release, credential, WorkerCoordinator, or InTr authority.

## Finding

Historical ASL-1 source directly resolved `PAT_WORKFLOW`, `GH_STEGVERSE_PAT`, or `GITHUB_TOKEN`, called GitHub APIs, inspected repository secret names, and was paired with a hosted workflow that performed credential rewriting and direct report pushes. Current security policy contains that hosted workflow and requires TV/TVC-only source materialization.

PR #41 validation also exposed that the rewritten checker still imported `yaml` even though neither the root/API development dependency chain nor the focused CI install declared PyYAML. Adding PyYAML solely to satisfy the checker would have introduced an unnecessary third-party prerequisite.

## Integrated repair

Merged surfaces:

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

Integrated checker contract:

```text
source acquisition: OUTSIDE CHECKER / PRE-MATERIALIZED ONLY
credential inputs: PROHIBITED
network/provider calls: NONE
third-party parser dependency: NONE
policy path: docs/governance/repo_alignment_expectations.yaml
policy bytes: JSON serialization (valid YAML)
policy parser: Python stdlib json
input: secret-free exact-source materialization manifest
required per target: repo + exact 40-hex source SHA + local path + receipt reference + authority=TV/TVC
alignment evaluation: LOCAL / CREDENTIAL-FREE
report generation: LOCAL ONLY
report publication: NONE
mutation authority: NONE
```

Manifest schema identifier:

`stegverse.scw.repo-alignment-materialization/v1`

The checker fails closed when a configured target is absent, an undeclared target is supplied, an exact SHA is malformed, authority is not `TV/TVC`, a local materialized path is absent, a secret/token/credential field is present, or policy bytes are invalid JSON.

The canonical policy retains its historical `.yaml` path to preserve existing SCW references. JSON is valid YAML, so YAML-capable legacy readers remain compatible while the ASL-1 checker itself is Python-stdlib-only.

## README completeness predicate

The source repair materially changed ASL-1 prerequisites, credential semantics, checker input, failure behavior, authority boundaries, and parser/dependency semantics. README update was therefore mandatory and was included in PR #41 before merge.

`README.md` now states that:
- the checker is credential-free and does not resolve PAT/GitHub/provider credentials;
- the checker is stdlib-only and does not require PyYAML;
- the canonical `.yaml` policy path contains JSON serialization, preserving YAML compatibility while enabling stdlib parsing;
- target repositories must already be materialized through an admitted TV/TVC exact-source path;
- the manifest must be secret-free and exact-SHA/receipt bound;
- report generation is local evaluation only;
- materialization, report publication, repository mutation, release, deployment, runtime, and production authority remain separate governed capabilities;
- `.github/workflows/alignment_check.yml` remains contained until required runtime predicates are actually satisfied.

README completeness state: `SATISFIED_IN_PR_41`.

## Exact source validation and integration evidence

Exact validated PR head:

`0ab3b4b4ac3e15933d194d868b3f8476d154561e`

Observed validation:

```text
CI 34002152391: SUCCESS
  changed Python lint: PASS
  focused pytest: PASS
Test Readiness 34002152430: SUCCESS
StegVerse AI Bridge Forwarding - Validation Only 34002152399: SUCCESS
CodeQL - Validation Transport Only 34002152388: SUCCESS
```

Current-main collision check before merge:

```text
main advancement from PR merge base: 3 commits
changed main-only files: 3 generated financial/ledger report files
ASL-1 overlap: NONE
review objections: NONE
unresolved review threads: NONE
```

Source integration:

```text
PR #41: MERGED
merge commit: 224c6c662e010b9ef49397cf59224476452548a1
source repair state: COMPLETE_MERGED
runtime activation effect: NONE
```

Hosted validation proves source/test behavior only. It does not prove TVC activation, private-source materialization, operational ASL-1 execution, report publication, or production activation.

## TVC dependency

Existing capability: `StegVerse-Labs/TVC` / `tvc.private-source-read.v1`.

Current observed TVC state:

```text
source implementation: VALIDATED + MERGED
credential/grant activation: NOT OBSERVED
live private materialization: NOT OBSERVED
resident exact-source admission: NOT OBSERVED
current admitted private-source progression: exact StegCore PR #146
SCW ASL-1 status: NONCURRENT/BACKLOG CONSUMER
```

SCW ASL-1 is a bounded noncurrent/backlog consumer of the existing TVC private-source-read lane. It may not interrupt or masquerade as the current StegCore PR #146 progression. When SCW becomes the admitted target, TVC must bind a fresh exact-source grant to then-current SCW target coordinates and retain secret-free evidence.

Therefore `.github/workflows/alignment_check.yml` remains contained. A future admitted execution owner must supply exact materialized snapshots and secret-free receipt references through TV/TVC authority. GitHub Actions may transport or validate evidence but may not become source-read or production control-plane authority.

## Coordination / authority state

```text
canonical work intent authority: StegVerse Canonical Work Coordination System
Master Records authority: observed events / custody / reconstructable evidence only
WorkerCoordinator authority: execution claim/fence ownership
Interlock/InTr authority: task admission / governed state transitions
SCW source repair owner: issue #22 + PR #41
source repair state: COMPLETE_MERGED
new competing canonical task identity created: NO
source/merge/CI implies runtime activation: NO
```

No separate WorkerCoordinator or canonical Task Registry claim for this exact source-repair branch was observed during preflight. PR #41 was used as the existing bounded source owner rather than fabricating duplicate task identity.

## Remaining machine work

```text
1. Keep the existing hosted alignment workflow contained.
2. Do not compete with TVC's current exact StegCore PR #146 private-source progression.
3. When TVC actually activates private-source materialization and SCW becomes the admitted consumer, bind then-current exact target snapshots to this checker and execute credential-free ASL-1 validation.
4. Retain the generated alignment reports as execution evidence.
5. Reintroduce durable report publication only through a separately admitted bounded mutation/publication capability, if publication remains required.
6. Reconcile operational evidence through canonical Task Registry / Master Records / WorkerCoordinator / InTr surfaces without inferring completion from source merge.
```

## User work

NONE currently required.

## Completion accounting

```text
bounded source repair: 100% COMPLETE_MERGED
README completeness: SATISFIED
source validation: PASS
contained workflow reactivation: NO
TVC private-source activation for SCW: NOT OBSERVED
operational exact-source ASL-1 execution: NOT OBSERVED
durable report publication: NOT OBSERVED / separately governed if required
runtime/production activation effect: NONE
```

## Completion boundary

The bounded source repair is complete. ASL-1 operational proof remains incomplete until admitted exact-source materialization, credential-free checker execution against those exact snapshots, declared report generation, and any separately required safe publication are actually observed.
