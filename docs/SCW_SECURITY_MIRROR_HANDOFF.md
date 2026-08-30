# SCW Security Mirror Handoff

Status: ACTIVE — CREDENTIAL AUTHORITY MIGRATION / HISTORICAL PROVENANCE AUDIT

Established: 2026-08-19  
Last reconciled: 2026-08-19  
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

Twenty-two legacy `StegVerse-Labs/StegVerse-SCW` workflow paths plus the related `StegVerse-Labs/hybrid-collab-bridge` autopatch path are now contained/retired in place (23 total paths in the audit finding). Scheduled execution and direct mutation behavior were removed where present.

Contained/retired StegVerse-SCW paths:

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
- `.github/workflows/export-hcb.yml`
- `.github/workflows/propagate-commit-template.yml`
- `.github/workflows/propagate-readme-badges.yml`
- `.github/workflows/propagate-commit-template-v1_1.yml`

Related contained path:

- `StegVerse-Labs/hybrid-collab-bridge/.github/workflows/autopatch.yml`

These paths previously included one or more of:

- PAT/bot credential interpolation or fallback;
- derived `GITHUB_TOKEN`, `GH_TOKEN`, or `STEG_TOKEN` values;
- bearer `x-access-token` Git URLs;
- `contents`, `actions`, `workflows`, `pull-requests`, `issues`, or OIDC write authority;
- scheduled mutation;
- arbitrary/cross-repository source access, repository creation, synchronization, branch mutation, tagging, or release attempts;
- direct `git push` or PR creation;
- workflow self-modification or propagation of hosted write-authority workflows;
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

No generic replacement mutation authority is inferred from the private-source-read capability. Any replacement for auto-fix, workflow mutation, report publication, entity state, README generation, revenue ledger writes, cross-repository sync, HCB export, template propagation, repository creation, tagging, or release requires a separately admitted mutation capability binding:

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


## Invalid hosted-mutation workflow retirement batch 1 — 2026-08-30

Seven additional parse-invalid legacy workflow surfaces were found to violate the current SCW security boundary even before considering their YAML syntax. They are retired rather than repaired into executable form:

```text
.github/workflows/autopatch-ops.yml
.github/workflows/autopatch-readme-quickcontrols.yml
.github/workflows/autopatch-reindex.yml
.github/workflows/autopatch-repotree-and-supercheck.yml
.github/workflows/autopatch-wire-quick-controls.yml
.github/workflows/self_repair_autopatch.yml
.github/workflows/universal_fixit.yml
```

Observed prohibited patterns included hosted `contents/actions/workflows/pull-requests/checks: write`, direct `git push`, `github.token` / `GITHUB_TOKEN`-backed dispatch or PR creation, workflow self-modification, and broad source normalization from a hosted runner.

No current indexed source reference to these workflow filenames was observed before retirement. No replacement mutation capability is introduced. Any future automated repair must use separately admitted exact-scope TV/TVC authority or remain proposal/evidence-only.

`autopatch_dryrun.yml` is intentionally not included because its current semantics are read-only PR validation/artifact generation and should be repaired separately if its YAML can be made valid without authority expansion.

The previous parse-invalid denominator was 38 at Workflows Sanity Check run `33327664669`. A fresh post-merge sanity run is required before recording a new denominator.
