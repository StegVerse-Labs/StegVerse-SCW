# StegVerse SCW Mirror Handoff

## Status

This file is the active handoff and task source of truth for `StegVerse-Labs/StegVerse-SCW` until superseded.

## Current goal

Repair the local repository alignment check path while preserving credential, token, and cross-repo boundaries.

## Current failure classes

```text
StegVerse Guardian Worker Repo Alignment Check -> missing scripts/genesis/repo_alignment_check.py.
Legacy PR #18 -> superseded by a fresh branch because it became stale and triggered broad policy checks.
```

## Repair boundary

This repair may add a local non-mutating checker and handoff only. It does not change secrets, grant PAT scope, force-push, delete reports, or create cross-repo mutation authority.

## Remaining files or modules to install

```text
scripts/genesis/repo_alignment_check.py -> StegVerse-Labs/StegVerse-SCW
workflow push-hardening patch -> StegVerse-Labs/StegVerse-SCW after workflow paths are confirmed
credential access repair -> StegVerse-Labs/StegVerse-SCW and StegVerse-Labs/TVC after explicit authorization
Repo Operations Center status surface -> StegVerse-Labs/Site
Publisher status artifact -> GCAT-BCAT-Engine/Publisher
Admissibility note -> StegVerse-Labs/admissibility-wiki
Guardian operator boundary note -> StegVerse-002/stegguardian-wiki
```

## Archive posture

This handoff records the current SCW repair source of truth so the complete thread can be archived without additional context.
