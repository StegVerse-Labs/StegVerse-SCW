# SCW Mirror Handoff

This file is the current handoff and task source of truth for `StegVerse-Labs/StegVerse-SCW`.

## Current Goal

Restore stable repository operations without adding workflows.

## Current Priority

Install `scripts/autodocs_probe_pr_safe.py` from the checked-in declaration at `.github/autopatch/docs-prsafe-status.patch.yml` so `taskops-nightly` can run its declared AutoDocs task.

## Known Remaining Work

- inspect StegTV connectivity execution failure
- inspect multi-repo report commit failure
- inspect ASL-1 alignment failure
- inspect backup repository checkout failure
- inspect export-hcb-nightly failure

## Build Rule

Prefer existing declared scripts and task surfaces. Keep commit steps safe when no files changed. Do not claim downstream completion without evidence.

## Next Integration Candidate

Publish verified SCW status through existing Site and Publisher paths after local checks are green.
