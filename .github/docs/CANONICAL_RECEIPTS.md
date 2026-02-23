# Canonical Receipts (StegDB)

SCW is the command plane. StegDB is the truth plane.

When SCW runs audits or applies fixes, the canonical receipts live in StegDB:

## Latest global receipt
- `StegDB/meta/guardian/GUARDIAN_GLOBAL_LATEST.md`
- `StegDB/meta/guardian/guardian_global_latest.json`

## Why this matters
- SCW runs can be re-run, logs can be noisy.
- StegDB keeps the canonical time-series audit trail.

## SCW rule
Every major workflow should append links to the StegDB receipts in the job summary.

See: `.github/workflows/_reusables/append-stegdb-receipts.yml`
