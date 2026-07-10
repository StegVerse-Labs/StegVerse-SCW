# SCW Mirror Handoff

This file is the current handoff and task source of truth for `StegVerse-Labs/StegVerse-SCW`.

## Current Goal

Restore stable repository operations without adding workflows.

## Completed Repairs

- restored `scripts/autodocs_probe_pr_safe.py` from `.github/autopatch/docs-prsafe-status.patch.yml`
- preserved `taskops-nightly` as the existing declared task surface
- made `.github/workflows/stegverse-multi-autopatch.yml` concurrency-safe for report publication
- added fetch/rebase-before-push handling for `reports/stegverse_multi_autopatch_report.md`
- serialized `.github/workflows/stegtvc_connectivity_autopatch.yml`
- made connectivity report publication empty-diff safe and fetch/rebase-before-push safe
- removed silent dependency-install success from the connectivity workflow
- aligned `docs/governance/repo_alignment_expectations.yaml` with `scripts/stegtvc_connectivity_manifest.json`
- removed undeclared cross-repo workflow filename assumptions from ASL-1 enforcement
- preflighted `.github/workflows/backup_triggers.yml` so an absent or inaccessible backup destination records a clean skip instead of failing the repository
- added rebase-before-push handling to the trigger backup publication step

## Current Priority

Inspect `export-hcb-nightly` and identify whether its failure is a missing local dependency, destination-reference drift, or report-publication race.

## Known Remaining Work

Destination: `StegVerse-Labs/StegVerse-SCW`

- verify `taskops-nightly` passes after restoring the AutoDocs probe
- verify multi-repo autopatch report publication passes after concurrency repair
- verify StegTV connectivity execution and report publication pass after workflow hardening
- verify ASL-1 alignment uses the canonical StegTVC file contract
- verify backup workflow records a clean skip when destination access is absent
- inspect and repair `export-hcb-nightly`
- inspect repository-wide CodeQL and validation cascade separately from operational workflow repairs

## Build Rule

Prefer existing declared scripts and task surfaces. Keep commit steps safe when no files changed or when `main` advances during execution. Optional external destinations must be preflighted and may not convert unavailable authority into a repository failure. Do not claim downstream completion without evidence.

## Next Integration Candidate

Publish verified SCW status through existing Site and Publisher paths after local checks are green.
