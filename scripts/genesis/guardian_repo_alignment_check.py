#!/usr/bin/env python3
"""
StegVerse Guardian Worker — Repo Alignment Check (ASL-1)

Scans target repos and reports ✅/❌ for:
  - required files (connectivity & sharing)
  - required workflows
  - optional checks (workflow_dispatch present, secret names exist)

Writes:
  reports/guardians/repo_alignment_latest.json
  reports/guardians/repo_alignment_latest.md

Notes:
- Secret VALUES are never read (impossible + unsafe). If PAT lacks permission
  to list secret names, we mark secrets status as "unknown" rather than fail.
"""

from __future__ import annotations
import json, os, sys, time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / "docs" / "governance" / "repo_alignment_expectations.yaml"
OUT_DIR = ROOT / "reports" / "guardians"
OUT_DIR.mkdir(parents=True, exist_ok=True)

API = "https://api.github.com"

def load_cfg() -> Dict[str, Any]:
    if not CFG_PATH.exists():
        raise SystemExit(f"Missing config at {CFG_PATH}")
    return yaml.safe_load(CFG_PATH.read_text(encoding="utf-8")) or {}

def gh_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "StegVerse-Repo-Alignment-Check"
    }

def api_get(url: str, token: str) -> requests.Response:
    return requests.get(url, headers=gh_headers(token), timeout=30)

def file_exists(owner: str, repo: str, path: str, token: str) -> Tuple[bool, str]:
    url = f"{API}/repos/{owner}/{repo}/contents/{path}"
    r = api_get(url, token)
    if r.status_code == 200:
        return True, "present"
    if r.status_code == 404:
        return False, "missing"
    return False, f"error:{r.status_code}"

def list_workflows(owner: str, repo: str, token: str) -> Tuple[List[str], str]:
    url = f"{API}/repos/{owner}/{repo}/contents/.github/workflows"
    r = api_get(url, token)
    if r.status_code != 200:
        return [], f"error:{r.status_code}"
    items = r.json()
    paths = []
    for it in items if isinstance(items, list) else []:
        if it.get("type") == "file":
            paths.append(f".github/workflows/{it.get('name')}")
    return paths, "ok"

def fetch_file_text(owner: str, repo: str, path: str, token: str) -> Tuple[str, str]:
    url = f"{API}/repos/{owner}/{repo}/contents/{path}"
    r = api_get(url, token)
    if r.status_code != 200:
        return "", f"error:{r.status_code}"
    data = r.json()
    download_url = data.get("download_url")
    if not download_url:
        return "", "no_download_url"
    raw = requests.get(download_url, timeout=30)
    if raw.status_code != 200:
        return "", f"raw_error:{raw.status_code}"
    return raw.text, "ok"

def has_workflow_dispatch(yaml_text: str) -> bool:
    # text-level check is enough
    return "workflow_dispatch" in yaml_text

def list_secret_names(owner: str, repo: str, token: str) -> Tuple[List[str], str]:
    # Requires repo admin + actions:read for secrets listing.
    url = f"{API}/repos/{owner}/{repo}/actions/secrets"
    r = api_get(url, token)
    if r.status_code == 200:
        names = [s.get("name") for s in (r.json().get("secrets") or [])]
        return names, "ok"
    # if not permitted, mark unknown
    return [], f"unknown:{r.status_code}"

def main():
    token = os.getenv("PAT_WORKFLOW") or os.getenv("GH_STEGVERSE_PAT") or os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ No token available. Set PAT_WORKFLOW or GH_STEGVERSE_PAT.")
        return 1

    cfg = load_cfg()
    targets = cfg.get("targets") or []
    required_files = cfg.get("required_files") or []
    required_wfs = cfg.get("required_workflows") or []
    opts = cfg.get("optional_checks") or {}

    results = []
    summary = {
        "repos_total": len(targets),
        "repos_pass": 0,
        "repos_fail": 0,
        "repos_error": 0,
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rid": os.getenv("GITHUB_RUN_ID", "local"),
    }

    for t in targets:
        full = t["repo"]
        owner, repo = full.split("/", 1)

        repo_entry = {
            "repo": full,
            "status": "unknown",
            "required_files": {},
            "required_workflows": {},
            "optional": {},
            "notes": []
        }

        # ---- required files
        file_ok = True
        for f in required_files:
            ok, msg = file_exists(owner, repo, f, token)
            repo_entry["required_files"][f] = {"ok": ok, "msg": msg}
            if not ok:
                file_ok = False

        # ---- required workflows (by file path existence)
        wf_ok = True
        wf_paths, wf_msg = list_workflows(owner, repo, token)
        if wf_msg != "ok":
            wf_ok = False
            repo_entry["notes"].append(f"workflow_list:{wf_msg}")
        wf_set = set(wf_paths)
        for w in required_wfs:
            ok = w in wf_set
            repo_entry["required_workflows"][w] = {"ok": ok, "msg": "present" if ok else "missing"}
            if not ok:
                wf_ok = False

        # ---- optional: ensure workflow_dispatch
        if opts.get("ensure_workflow_dispatch"):
            dispatch_fail = []
            for w in wf_paths:
                text, tmsg = fetch_file_text(owner, repo, w, token)
                if tmsg == "ok" and text:
                    if not has_workflow_dispatch(text):
                        dispatch_fail.append(w)
            repo_entry["optional"]["workflow_dispatch_missing_in"] = dispatch_fail

        # ---- optional: secrets presence (names only)
        check_names = opts.get("check_repo_secrets_names") or []
        if check_names:
            names, smsg = list_secret_names(owner, repo, token)
            if smsg.startswith("unknown"):
                repo_entry["optional"]["secrets_status"] = smsg
                repo_entry["optional"]["secrets_missing"] = []
            else:
                missing = [n for n in check_names if n not in names]
                repo_entry["optional"]["secrets_status"] = "ok"
                repo_entry["optional"]["secrets_missing"] = missing

        # ---- status decision
        if file_ok and wf_ok:
            repo_entry["status"] = "pass"
            summary["repos_pass"] += 1
        else:
            repo_entry["status"] = "fail"
            summary["repos_fail"] += 1

        results.append(repo_entry)

    # write JSON
    out_json = OUT_DIR / "repo_alignment_latest.json"
    payload = {"summary": summary, "results": results}
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # write MD
    lines = [
        "# StegVerse Repo Alignment Report",
        "",
        f"- Run: {summary['ts_utc']}",
        f"- RID: `{summary['rid']}`",
        "",
        "## Summary",
        f"- Total repos: **{summary['repos_total']}**",
        f"- Pass: **{summary['repos_pass']}**",
        f"- Fail: **{summary['repos_fail']}**",
        "",
        "## Per-repo results",
        ""
    ]

    for r in results:
        badge = "✅" if r["status"] == "pass" else "❌"
        lines.append(f"### {badge} {r['repo']}")
        lines.append("")
        lines.append("**Required files:**")
        for f, st in r["required_files"].items():
            fb = "✅" if st["ok"] else "❌"
            lines.append(f"- {fb} `{f}` — {st['msg']}")
        lines.append("")
        lines.append("**Required workflows:**")
        for w, st in r["required_workflows"].items():
            wb = "✅" if st["ok"] else "❌"
            lines.append(f"- {wb} `{w}` — {st['msg']}")
        lines.append("")

        opt = r.get("optional") or {}
        if "workflow_dispatch_missing_in" in opt:
            miss = opt["workflow_dispatch_missing_in"]
            if miss:
                lines.append("**Optional:** workflow_dispatch missing in:")
                for m in miss:
                    lines.append(f"- ⚠️ `{m}`")
            else:
                lines.append("**Optional:** workflow_dispatch present in all workflows.")
            lines.append("")

        if "secrets_status" in opt:
            lines.append(f"**Optional secrets check:** {opt['secrets_status']}")
            if opt.get("secrets_missing"):
                for n in opt["secrets_missing"]:
                    lines.append(f"- ❌ missing secret name `{n}`")
            elif opt["secrets_status"] == "ok":
                lines.append("- ✅ all required secret names present")
            lines.append("")

        if r["notes"]:
            lines.append("**Notes:**")
            for n in r["notes"]:
                lines.append(f"- {n}")
            lines.append("")

    out_md = OUT_DIR / "repo_alignment_latest.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
