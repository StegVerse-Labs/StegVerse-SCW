# StegVerse SCW Mirror Handoff

## Status

This file is the active handoff and task source of truth for `StegVerse-Labs/StegVerse-SCW` until superseded.

## Current goal

Repair repository-operations failures surfaced by the GitHub error monitor while preserving token and cross-repo boundaries.

## Current failure classes

```text
Ledger Integrity Check -> report committed but push rejected non-fast-forward.
StegTV Connectivity Autopatch -> cross-repo clone of StegVerse-Labs/TVC failed with bad credentials.
StegVerse Multi-Repo Autopatch -> report committed but push rejected non-fast-forward.
StegVerse Guardian Worker Repo Alignment Check -> missing scripts/genesis/repo_alignment_check.py.
```

## Repair boundary

This repair path may add missing local shims and documentation. It does not change secrets, grant PAT scope, force-push, delete reports, or create cross-repo mutation authority.

## Required next actions

```text
1. Add a safe local repo-alignment checker at scripts/genesis/repo_alignment_check.py.
2. Add pull/rebase-before-push hardening to report-writing workflows once workflow file paths are confirmed.
3. Refresh or scope GH_TOKEN/PAT for StegVerse-Labs/TVC only after explicit credential authorization.
```

## Remaining files or modules to install

```text
scripts/genesis/repo_alignment_check.py -> StegVerse-Labs/StegVerse-SCW
workflow push-hardening patch -> StegVerse-Labs/StegVerse-SCW once workflow paths are confirmed
credential access repair -> StegVerse-Labs/StegVerse-SCW and StegVerse-Labs/TVC after explicit authorization
Repo Operations Center status surface -> StegVerse-Labs/Site
Publisher status artifact -> GCAT-BCAT-Engine/Publisher
Admissibility note -> StegVerse-Labs/admissibility-wiki
Guardian operator boundary note -> StegVerse-002/stegguardian-wiki
```

## Archive posture

This handoff records the current SCW repair source of truth so the complete thread can be archived without additional context.
