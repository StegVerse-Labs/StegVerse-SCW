# ASL-1 Materialized Input Repair Mirror Handoff

## Scope

Repository: `StegVerse-Labs/StegVerse-SCW`

Parent handoffs:
- `SCW_MIRROR_HANDOFF.md`
- `docs/SCW_SECURITY_MIRROR_HANDOFF.md`

Canonical security task: issue `#22`

This bounded repair removes credential acquisition and provider reads from the ASL-1 repository alignment checker. It does not reactivate the contained hosted workflow and does not grant source-read, mutation, report-publication, runtime, release, or credential authority.

## Finding

Current `main` intentionally contains `.github/workflows/alignment_check.yml` because the historical lane used PAT fallbacks, global Git credential rewriting, and direct report pushes. The canonical checker on `main` also directly resolves `PAT_WORKFLOW`, `GH_STEGVERSE_PAT`, or `GITHUB_TOKEN`, calls GitHub APIs, and inspects repository secret names.

That implementation is incompatible with issue #22 and with the current TV/TVC-only credential boundary.

## Repair

Branch: `repair/asl1-materialized-input`

Changed surfaces:

```text
scripts/genesis/guardian_repo_alignment_check.py
docs/governance/repo_alignment_expectations.yaml
tests/test_guardian_repo_alignment_check.py
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

## TVC dependency

Existing capability: `StegVerse-Labs/TVC` / `tvc.private-source-read.v1`.

Current observed TVC state at repair creation:

```text
source implementation: VALIDATED + MERGED
credential/grant activation: NOT OBSERVED
live private materialization: NOT OBSERVED
resident exact-source admission: NOT OBSERVED
```

Therefore this repair deliberately does not reactivate `.github/workflows/alignment_check.yml`. A future admitted execution owner must supply exact materialized snapshots and secret-free receipt references through TV/TVC authority. GitHub Actions may transport/validate evidence but may not become the source-read or production control plane.

## Validation

Focused source tests are added for:
- exact local materialized snapshot evaluation while `GITHUB_TOKEN` is present but unused;
- rejection of secret-bearing manifest fields;
- fail-closed rejection when configured targets are not supplied.

Hosted CI evidence is pending after PR creation. Hosted validation, if successful, proves source/test behavior only; it is not TVC activation or operational ASL-1 execution.

## Remaining machine work

```text
1. Open the repair PR and obtain source/test validation.
2. Keep the existing hosted alignment workflow contained.
3. Register/reconcile SCW as a bounded noncurrent consumer of tvc.private-source-read.v1 only if canonical TVC ownership permits it without interrupting the current admitted progression.
4. After actual TVC materialization activation, bind exact target snapshots to this checker and execute credential-free validation.
5. Reintroduce durable report publication only through a separately admitted bounded mutation/publication capability, if publication remains required.
```

## User work

NONE currently required.

## Completion boundary

Source repair can be complete before runtime activation. ASL-1 operational proof remains incomplete until admitted exact-source materialization, credential-free checker execution, declared report generation, and any separately required safe publication are actually observed.
