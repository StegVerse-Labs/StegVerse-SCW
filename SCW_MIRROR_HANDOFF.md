# SCW Mirror Handoff

This file is the current handoff and task source of truth for `StegVerse-Labs/StegVerse-SCW`.

## Current Goal

Restore stable repository operations without adding workflows.

## Completed Repairs

- restored `scripts/autodocs_probe_pr_safe.py` from `.github/autopatch/docs-prsafe-status.patch.yml`
- preserved `taskops-nightly` as the existing declared task surface
- made `.github/workflows/stegverse-multi-autopatch.yml` concurrency-safe for report publication
- added fetch/rebase-before-push handling for `reports/stegverse_multi_autopatch_report.md`

## Current Priority

Inspect the StegTV connectivity execution failure and determine whether it is a local script defect, destination-reference drift, or token-scope boundary.

## Known Remaining Work

Destination: `StegVerse-Labs/StegVerse-SCW`

- verify `taskops-nightly` passes after restoring the AutoDocs probe
- verify multi-repo autopatch report publication passes after concurrency repair
- inspect StegTV connectivity execution failure
- inspect ASL-1 alignment failure
- inspect backup repository checkout failure
- inspect `export-hcb-nightly` failure

## Build Rule

Prefer existing declared scripts and task surfaces. Keep commit steps safe when no files changed or when `main` advances during execution. Do not claim downstream completion without evidence.

## Next Integration Candidate

Publish verified SCW status through existing Site and Publisher paths after local checks are green.
