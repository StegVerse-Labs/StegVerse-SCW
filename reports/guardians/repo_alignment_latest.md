# StegVerse Repo Alignment Report

- Run: 2025-12-04T07:46:58Z
- RID: `19921521467`

## Summary
- Total repos: **4**
- Pass: **0**
- Fail: **4**

## Per-repo results

### ❌ StegVerse-Labs/TVC

**Required files:**
- ✅ `.github/workflows/autopatch.yml` — present
- ✅ `.github/workflows/workflows-status-badges.yml` — present
- ✅ `data/stegtvc_config.json` — present
- ✅ `app/resolver.py` — present
- ❌ `.github/stegtvc_client.py` — missing

**Required workflows:**
- ✅ `.github/workflows/autopatch.yml` — present
- ❌ `.github/workflows/guardian_omni_guardian.yml` — missing
- ❌ `.github/workflows/guardian_worker_readmes.yml` — missing

**Optional:** workflow_dispatch present in all workflows.

**Optional secrets check:** ok
- ❌ missing secret name `PAT_WORKFLOW`
- ❌ missing secret name `GH_STEGVERSE_PAT`

### ❌ StegVerse-Labs/hybrid-collab-bridge

**Required files:**
- ✅ `.github/workflows/autopatch.yml` — present
- ✅ `.github/workflows/workflows-status-badges.yml` — present
- ✅ `data/stegtvc_config.json` — present
- ✅ `app/resolver.py` — present
- ✅ `.github/stegtvc_client.py` — present

**Required workflows:**
- ✅ `.github/workflows/autopatch.yml` — present
- ❌ `.github/workflows/guardian_omni_guardian.yml` — missing
- ❌ `.github/workflows/guardian_worker_readmes.yml` — missing

**Optional:** workflow_dispatch missing in:
- ⚠️ `.github/workflows/ci.yml`

**Optional secrets check:** ok
- ✅ all required secret names present

### ❌ StegVerse-Labs/TV

**Required files:**
- ✅ `.github/workflows/autopatch.yml` — present
- ✅ `.github/workflows/workflows-status-badges.yml` — present
- ✅ `data/stegtvc_config.json` — present
- ✅ `app/resolver.py` — present
- ❌ `.github/stegtvc_client.py` — missing

**Required workflows:**
- ✅ `.github/workflows/autopatch.yml` — present
- ❌ `.github/workflows/guardian_omni_guardian.yml` — missing
- ❌ `.github/workflows/guardian_worker_readmes.yml` — missing

**Optional:** workflow_dispatch missing in:
- ⚠️ `.github/workflows/forward-to-bridge.yml`
- ⚠️ `.github/workflows/tv_apply_reusable.yml`
- ⚠️ `.github/workflows/tv_auto_heal.yml`
- ⚠️ `.github/workflows/tv_self_heal_on_push.yml`
- ⚠️ `.github/workflows/tv_verify_reusable.yml`

**Optional secrets check:** ok
- ❌ missing secret name `PAT_WORKFLOW`
- ❌ missing secret name `GH_STEGVERSE_PAT`

### ❌ StegVerse-Labs/StegVerse-SCW

**Required files:**
- ✅ `.github/workflows/autopatch.yml` — present
- ✅ `.github/workflows/workflows-status-badges.yml` — present
- ✅ `data/stegtvc_config.json` — present
- ✅ `app/resolver.py` — present
- ❌ `.github/stegtvc_client.py` — missing

**Required workflows:**
- ✅ `.github/workflows/autopatch.yml` — present
- ❌ `.github/workflows/guardian_omni_guardian.yml` — missing
- ❌ `.github/workflows/guardian_worker_readmes.yml` — missing

**Optional:** workflow_dispatch missing in:
- ⚠️ `.github/workflows/autopatch_dryrun.yml`
- ⚠️ `.github/workflows/ci.yml`
- ⚠️ `.github/workflows/ci_governance.yml`
- ⚠️ `.github/workflows/docs-suite-on-complete.yml`
- ⚠️ `.github/workflows/forward-to-bridge.yml`
- ⚠️ `.github/workflows/setup-common-python.yml`
- ⚠️ `.github/workflows/taskops-export-weekly.yml`
- ⚠️ `.github/workflows/taskops-first-run-update.yml`
- ⚠️ `.github/workflows/yaml_corrector.yml`
- ⚠️ `.github/workflows/yaml_corrector_v2.yml`

**Optional secrets check:** ok
- ✅ all required secret names present
