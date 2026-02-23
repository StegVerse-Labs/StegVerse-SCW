# StegVerse Architecture: Command Plane vs Truth Plane

StegVerse is intentionally split into two planes:

- **SCW (StegVerse Code Worker)** = **Command Plane**
  - Executes commands.
  - Runs validations and guardians.
  - Generates fixes (autopatch, README standardize, template sync).
  - Opens issues / comments / PRs to apply changes.

- **StegDB (StegVerse DataBase)** = **Truth Plane**
  - Canonical record of repo structure and file identity (paths + SHAs).
  - Global audit snapshots over time.
  - Aggregation of guardian outputs into one place.
  - Attestation / manifests for “what was seen” and “what changed”.

## Why this split exists

A system that both *acts* and *defines truth* can accidentally erase evidence.
To prevent that, we separate:
- **Action** (SCW) from **Proof** (StegDB)

SCW can say “I fixed it.”
StegDB proves: “It was broken, here’s the baseline, here’s the change, here’s the after-state.”

## Canonical Audit Artifact Contract (Truth Plane)

StegDB is responsible for maintaining a stable, machine-readable contract:

- `meta/registry.json`  
  The authoritative list of repos, their canonical flags, and metadata.

- `meta/guardian/guardian_global_latest.json`  
  Global guardian findings snapshot (across repos).

- `meta/guardian/GUARDIAN_GLOBAL_LATEST.md`  
  Human readable global guardian findings.

- `meta/guardian/per_repo/<repo>/guardian_latest.json`  
  Per-repo guardian findings snapshot (copied/ingested).

- `meta/aggregated_files.jsonl`  
  Aggregated file index across repos (paths + hashes).

- `meta/global_state.json` and/or `meta/GLOBAL_STATE.md`  
  Single “pasteable” system report.

- `meta/attest/manifest.json` (+ checksum)  
  Hash manifest over audit artifacts for tamper evidence.

## SCW output rule

Every SCW run that generates findings should publish:
1) its local results (logs/artifacts/issues),
2) and a link to the **StegDB canonical receipt**.

SCW should not be the long-term store of truth artifacts.
StegDB is the ledger.

## Practical outcomes

- SCW is allowed to be noisy (logs, experiments, PRs).
- StegDB stays stable, canonical, time-series, and auditable.
- Users always know where to look: the StegDB “receipt”.
