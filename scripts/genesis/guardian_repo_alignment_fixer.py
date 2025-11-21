#!/usr/bin/env python3
"""
StegVerse Guardian Worker — Repo Alignment Fixer (ASL-2)

Behavior:
- Reads repo alignment expectations + latest alignment report.
- If any repo FAILS required file/workflow checks, attempts an auto-fix.
- Uses TVC as "source of truth" for required files, falling back to SCW copies.
- Tracks failures per repo+file so we don't retry the same broken fix endlessly.
- Writes updated alignment report after fixes.

Inputs:
- docs/governance/repo_alignment_expectations.yaml
- reports/guardians/repo_alignment_latest.json  (from alignment check)

Outputs:
- reports/guardians/repo_alignment_fix_history.json
- reports/guardians/repo_alignment_fixer_latest.json
- reports/guardians/repo_alignment_fixer_latest.md

Safety:
- Only touches target repos listed in expectations.
- Only adds/mirrors required files + required workflows.
- Never reads/prints secret values.
"""

from __future__ import annotations

import json, os, time, shutil, subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]  # .../StegVerse-SCW
CFG_PATH = ROOT / "docs/governance/repo_alignment_expectations.yaml"
ALIGN_PATH = ROOT / "reports/guardians/repo_alignment_latest.json"
HIST_PATH = ROOT / "reports/guardians/repo_alignment_fix_history.json"
OUT_DIR = ROOT / "reports/guardians"
OUT_DIR.mkdir(parents=True, exist_ok=True)

API = "https://api.github.com"
WORKDIR = ROOT / "work" / "alignment_fixer"
WORKDIR.mkdir(parents=True, exist_ok=True)

# How many times to retry the SAME missing-path fix before giving up.
MAX_RETRIES_PER_ITEM = 2

def sh(cmd: List[str], cwd: Optional[Path]=None, check: bool=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=check)

def load_yaml(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

def load_json(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_json(p: Path, data: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

def gh_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "StegVerse-Repo-Alignment-Fixer"
    }

def api_get(url: str, token: str) -> requests.Response:
    return requests.get(url, headers=gh_headers(token), timeout=30)

def fetch_raw_from_repo(owner: str, repo: str, path: str, token: str) -> Tuple[str, str]:
    url = f"{API}/repos/{owner}/{repo}/contents/{path}"
    r = api_get(url, token)
    if r.status_code != 200:
        return "", f"error:{r.status_code}"
    data = r.json()
    dl = data.get("download_url")
    if not dl:
        return "", "no_download_url"
    raw = requests.get(dl, timeout=30)
    if raw.status_code != 200:
        return "", f"raw_error:{raw.status_code}"
    return raw.text, "ok"

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def write_text(p: Path, txt: str):
    ensure_dir(p.parent)
    p.write_text(txt, encoding="utf-8")

def history_key(repo_full: str, path: str) -> str:
    return f"{repo_full}::{path}"

def should_skip_item(hist: Dict[str, Any], repo_full: str, path: str) -> bool:
    key = history_key(repo_full, path)
    entry = hist.get(key) or {}
    fails = int(entry.get("fails", 0))
    return fails >= MAX_RETRIES_PER_ITEM

def mark_item(hist: Dict[str, Any], repo_full: str, path: str, ok: bool, msg: str):
    key = history_key(repo_full, path)
    entry = hist.get(key) or {"fails": 0, "last_msg": ""}
    if ok:
        entry["fails"] = 0
    else:
        entry["fails"] = int(entry.get("fails", 0)) + 1
    entry["last_msg"] = msg
    entry["last_ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    hist[key] = entry

def clone_repo(repo_full: str, dest: Path) -> Tuple[bool, str]:
    if dest.exists():
        shutil.rmtree(dest)
    try:
        sh(["gh", "repo", "clone", repo_full, str(dest), "--", "--depth", "1"])
        return True, "cloned"
    except subprocess.CalledProcessError as e:
        return False, f"clone_failed: {e.stderr.strip() or e.stdout.strip()}"

def git_commit_push(dest: Path, message: str) -> Tuple[bool, str]:
    try:
        sh(["git", "config", "user.name", "StegVerse Alignment Fixer"], cwd=dest)
        sh(["git", "config", "user.email", "alignment-fixer@stegverse.local"], cwd=dest)
        if not sh(["git", "status", "--porcelain"], cwd=dest).stdout.strip():
            return True, "no_changes"
        sh(["git", "add", "-A"], cwd=dest)
        sh(["git", "commit", "-m", message], cwd=dest)
        sh(["git", "push", "origin", "HEAD"], cwd=dest)
        return True, "pushed"
    except subprocess.CalledProcessError as e:
        return False, f"push_failed: {e.stderr.strip() or e.stdout.strip()}"

def main() -> int:
    print("=== Repo Alignment Fixer (ASL-2) ===")

    token = os.getenv("PAT_WORKFLOW") or os.getenv("GH_STEGVERSE_PAT") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ No token set. Need PAT_WORKFLOW or GH_STEGVERSE_PAT.")
        return 1

    cfg = load_yaml(CFG_PATH)
    if not cfg:
        print("❌ Missing expectations config.")
        return 1

    alignment = load_json(ALIGN_PATH)
    if not alignment:
        print("❌ Missing alignment report. Run alignment check first.")
        return 1

    targets = cfg.get("targets") or []
    required_files = cfg.get("required_files") or []
    required_workflows = cfg.get("required_workflows") or []

    hist = load_json(HIST_PATH) or {}

    tvc_repo = cfg.get("source_of_truth_repo") or "StegVerse-Labs/TVC"
    tvc_owner, tvc_name = tvc_repo.split("/", 1)

    fixer_results = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rid": os.getenv("GITHUB_RUN_ID", "local"),
        "attempted": [],
        "summary": {"repos_fixed": 0, "repos_skipped": 0, "repos_failed": 0}
    }

    align_map = {r["repo"]: r for r in (alignment.get("results") or [])}

    for t in targets:
        repo_full = t["repo"]
        ar = align_map.get(repo_full)
        if not ar or ar.get("status") != "fail":
            continue

        print(f"\n--- Fixing {repo_full} ---")

        dest = WORKDIR / repo_full.replace("/", "__")
        ok, msg = clone_repo(repo_full, dest)
        if not ok:
            fixer_results["attempted"].append({"repo": repo_full, "status": "clone_failed", "message": msg})
            fixer_results["summary"]["repos_failed"] += 1
            continue

        changed_any = False
        repo_notes = []

        # Required files
        for path in required_files:
            abs_path = dest / path
            if abs_path.exists():
                continue
            if should_skip_item(hist, repo_full, path):
                repo_notes.append(f"skip:{path}:max_retries")
                continue

            txt, st = fetch_raw_from_repo(tvc_owner, tvc_name, path, token)
            if st == "ok" and txt.strip():
                write_text(abs_path, txt)
                changed_any = True
                mark_item(hist, repo_full, path, True, "restored_from_TVC")
                repo_notes.append(f"fixed:{path}:from_TVC")
                continue

            scw_src = ROOT / path
            if scw_src.exists():
                write_text(abs_path, scw_src.read_text(encoding="utf-8"))
                changed_any = True
                mark_item(hist, repo_full, path, True, "restored_from_SCW")
                repo_notes.append(f"fixed:{path}:from_SCW")
                continue

            placeholder = f"""# AUTOGENERATED PLACEHOLDER
# Repo Alignment Fixer could not locate a canonical source for:
#   {path}
# Please replace with correct canonical file (prefer {tvc_repo}).
"""
            write_text(abs_path, placeholder)
            changed_any = True
            mark_item(hist, repo_full, path, False, "placeholder_created")
            repo_notes.append(f"fixed:{path}:placeholder")

        # Required workflows
        for wf in required_workflows:
            abs_wf = dest / wf
            if abs_wf.exists():
                continue
            if should_skip_item(hist, repo_full, wf):
                repo_notes.append(f"skip:{wf}:max_retries")
                continue

            txt, st = fetch_raw_from_repo(tvc_owner, tvc_name, wf, token)
            if st == "ok" and txt.strip():
                write_text(abs_wf, txt)
                changed_any = True
                mark_item(hist, repo_full, wf, True, "workflow_from_TVC")
                repo_notes.append(f"fixed:{wf}:from_TVC")
            else:
                placeholder = f"""name: Placeholder Workflow ({wf})

on:
  workflow_dispatch: {{}}

permissions:
  contents: read

jobs:
  placeholder:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Placeholder created by Repo Alignment Fixer. Replace with canonical workflow."
"""
                write_text(abs_wf, placeholder)
                changed_any = True
                mark_item(hist, repo_full, wf, False, "workflow_placeholder_created")
                repo_notes.append(f"fixed:{wf}:placeholder")

        if changed_any:
            ok2, msg2 = git_commit_push(dest, "Alignment Fixer: restore required StegVerse files/workflows")
            if ok2:
                fixer_results["summary"]["repos_fixed"] += 1
                fixer_results["attempted"].append({"repo": repo_full, "status": "fixed", "message": msg2, "notes": repo_notes})
            else:
                fixer_results["summary"]["repos_failed"] += 1
                fixer_results["attempted"].append({"repo": repo_full, "status": "push_failed", "message": msg2, "notes": repo_notes})
        else:
            fixer_results["summary"]["repos_skipped"] += 1
            fixer_results["attempted"].append({"repo": repo_full, "status": "nothing_to_fix", "notes": repo_notes})

    save_json(HIST_PATH, hist)

    OUT_JSON = OUT_DIR / "repo_alignment_fixer_latest.json"
    OUT_MD   = OUT_DIR / "repo_alignment_fixer_latest.md"
    save_json(OUT_JSON, fixer_results)

    md_lines = [
        "# StegVerse Repo Alignment Fixer Report",
        "",
        f"- Run: {fixer_results['ts_utc']}",
        f"- RID: `{fixer_results['rid']}`",
        "",
        "## Summary",
        *(f"- {k}: **{v}**" for k, v in fixer_results["summary"].items()),
        "",
        "## Attempts"
    ]
    for a in fixer_results["attempted"]:
        md_lines.append(f"- **{a['repo']}** — {a['status']} — {a.get('message','')}")
        for n in a.get("notes") or []:
            md_lines.append(f"  - {n}")
    write_text(OUT_MD, "\n".join(md_lines) + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
