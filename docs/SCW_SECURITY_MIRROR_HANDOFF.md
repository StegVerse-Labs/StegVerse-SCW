# SCW Security Mirror Handoff

Status: ACTIVE — CREDENTIAL AUTHORITY MIGRATION / HISTORICAL PROVENANCE AUDIT

Established: 2026-08-19
Canonical repository: `StegVerse-Labs/StegVerse-SCW`
Parent operational handoff: `SCW_MIRROR_HANDOFF.md`
Canonical task: issue `#22`
Audit evidence: `StegVerse-Labs/footprint-auditor/evidence/findings/2026-08-19-pat-backed-autopatch-authority-containment.json`

## Governing boundary

- Credential authority is TV/TVC only.
- No NON-TV/TVC secret or token may be introduced or restored.
- GitHub Actions may validate or transport evidence but may not become production/runtime/control-plane authority.
- Missing authority fails closed before source materialization or mutation.
- Historical workflow existence, syntax validity, prior success, or a generated report does not prove admitted authority.

## Containment completed

The following legacy workflows were changed in place to read-only, manual, fail-closed placeholders. Scheduled execution and direct mutation behavior were removed where present:

- `.github/workflows/autopatch.yml`
- `.github/workflows/auto_patch.yml`
- `.github/workflows/stegverse-multi-autopatch.yml`
- `.github/workflows/stegtvc_connectivity_autopatch.yml`
- `.github/workflows/alignment_check.yml`
- `.github/workflows/alignment_fixer.yml`
- `.github/workflows/guardian_repo_alignment.yml`
- `.github/workflows/guardian_repo_alignment_check.yml`
- `.github/workflows/guardian_repo_alignment_fixer.yml`
- `.github/workflows/guardian_workflows.yml`
- `.github/workflows/guardian_worker_workflows.yml`
- `.github/workflows/guardian_worker_READMEs.yml`
- `.github/workflows/entities_runner.yml`
- `.github/workflows/revenue_event_manual.yml`
- `.github/workflows/stegtvc_connectivity_sync.yml`
- `.github/workflows/pat_auditor.yml`
- `.github/workflows/pat_secrets_guardian.yml`
- `.github/workflows/multi-autopatch.yml`

These paths previously included one or more of:

- PAT-family credential interpolation;
- PAT fallback between multiple secret names;
- derived `GITHUB_TOKEN`, `GH_TOKEN`, or `STEG_TOKEN` values;
- global `x-access-token` Git URL rewriting;
- `contents`, `actions`, `workflows`, or `issues` write authority;
- scheduled mutation;
- cross-repository source access/synchronization;
- direct `git push`;
- workflow self-modification;
- generated entity/memory/documentation/ledger state committed from GitHub-hosted execution.

Containment is not historical remediation and does not erase prior executions.

## Replacement architecture

### Private source read

Existing TVC capability:

`StegVerse-Labs/TVC/docs/PRIVATE_SOURCE_READ_MIRROR_HANDOFF.md`

Capability id: `tvc.private-source-read.v1`.

It provides exact-ref/exact-SHA, ephemeral, read-only source materialization under TV/TVC authority and explicitly prohibits `GITHUB_TOKEN`, `GH_TOKEN`, PAT, provider-token, or user-token substitution.

Current activation state: NOT ACTIVATED. Source implementation exists, but actual TV/TVC credential/grant execution and materialization evidence remain required.

### Mutation / repair / publication

No generic replacement mutation authority is inferred from the private-source-read capability. Any replacement for auto-fix, workflow mutation, report publication, entity state, README generation, revenue ledger writes, or cross-repository sync requires a separately admitted mutation capability binding:

- exact caller;
- exact source state;
- exact target repository/ref;
- bounded operation;
- actor/application/token provenance;
- decision and expiry;
- resulting commit/receipt;
- no secret persistence or export.

## Historical audit requirements

For every consequential historical execution of the contained workflows, reconstruct where evidence exists:

1. triggering actor/application;
2. credential/application identity or token hash;
3. source workflow commit;
4. external action/dependency versions actually executed;
5. target repositories and refs;
6. files/refs mutated;
7. resulting commits/PRs/issues/releases;
8. repository visibility at the event time;
9. whether authority was expected, unexplained, third-party, or unauthorized.

Organization audit-log evidence remains required to close historical actor/token/visibility gaps.

## Completion gate

This lane is not complete until:

- TVC private-source-read is actually activated and produces secret-free materialization receipts for required private-source consumers;
- required mutation paths are reintroduced only through explicit TV/TVC-admitted authority, or retired permanently;
- no live SCW workflow consumes a NON-TV/TVC credential for mutation;
- historical execution provenance is reconciled as far as retained GitHub/audit evidence permits;
- unresolved gaps remain explicit in the footprint-auditor exception ledger.

Do not repair a contained workflow by restoring its old token/PAT behavior.
