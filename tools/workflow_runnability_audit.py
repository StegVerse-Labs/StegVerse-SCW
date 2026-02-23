#!/usr/bin/env python3
"""
SCW: Workflow Runnability Audit (API-aware)

Goal:
- Explain why a workflow may NOT show the "Run workflow" button
  OR why it is "broken" / ScannerError / not runnable.
- Provide a machine-readable report StegDB can canonize.

Outputs:
- reports/guardians/workflow_runnability_latest.json
- reports/guardians/workflow_runnability_latest.md  (human summary)

What we detect (best-effort):
- YAML parseability
- has workflow_dispatch
- workflow files present
- referenced secrets/vars (e.g., secrets.FOO)
- API: repo default branch, actions enabled (where accessible),
  workflows list/state (where accessible)
- API: repo permission for current actor (where accessible)
- GITHUB_TOKEN permission limits are respected: we never assume access.

Usage:
  python tools/workflow_runnability_audit.py --repo-root .
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
import urllib.error

import yaml


SECRET_REF_RE = re.compile(r"secrets\.([A-Za-z0-9_]+)")
VAR_REF_RE = re.compile(r"vars\.([A-Za-z0-9_]+)")
ENV_REF_RE = re.compile(r"\${{\s*env\.([A-Za-z0-9_]+)\s*}}")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def safe_load_yaml(text: str) -> Tuple[bool, Any, str]:
    try:
        return True, yaml.safe_load(text), ""
    except Exception as e:
        return False, None, str(e)


def normalize_on(on_val: Any) -> Dict[str, Any]:
    if on_val is None:
        return {}
    if isinstance(on_val, str):
        return {on_val: {}}
    if isinstance(on_val, list):
        out: Dict[str, Any] = {}
        for e in on_val:
            if isinstance(e, str):
                out[e] = {}
        return out
    if isinstance(on_val, dict):
        return dict(on_val)
    return {}


def extract_refs(raw: str) -> Dict[str, List[str]]:
    secrets = sorted(set(SECRET_REF_RE.findall(raw)))
    vars_ = sorted(set(VAR_REF_RE.findall(raw)))
    envs = sorted(set(ENV_REF_RE.findall(raw)))
    return {"secrets": secrets, "vars": vars_, "env": envs}


def gh_api(url: str, token: Optional[str]) -> Any:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "stegverse-scw-audit")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def gh_api_try(url: str, token: Optional[str]) -> Tuple[bool, Any, str]:
    try:
        return True, gh_api(url, token), ""
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return False, None, f"HTTP {e.code}: {body[:300]}"
    except Exception as e:
        return False, None, str(e)


def infer_owner_repo() -> Tuple[Optional[str], Optional[str]]:
    repo = os.getenv("GITHUB_REPOSITORY")  # owner/name
    if not repo or "/" not in repo:
        return None, None
    owner, name = repo.split("/", 1)
    return owner, name


@dataclass
class WorkflowFinding:
    path: str
    yaml_ok: bool
    yaml_error: str
    has_workflow_dispatch: bool
    on_events: List[str]
    referenced_secrets: List[str]
    referenced_vars: List[str]
    referenced_env: List[str]


def scan_workflows(repo_root: Path) -> Tuple[List[WorkflowFinding], Dict[str, Any]]:
    wf_dir = repo_root / ".github" / "workflows"
    meta: Dict[str, Any] = {
        "workflows_dir_exists": wf_dir.exists(),
        "workflow_file_count": 0,
        "workflow_files": [],
    }
    findings: List[WorkflowFinding] = []
    if not wf_dir.exists():
        return findings, meta

    files = sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")))
    meta["workflow_file_count"] = len(files)
    meta["workflow_files"] = [str(p.relative_to(repo_root)).replace("\\", "/") for p in files]

    for p in files:
        raw = read_text(p)
        refs = extract_refs(raw)
        ok, doc, err = safe_load_yaml(raw)
        on_events: List[str] = []
        has_dispatch = False
        if ok and isinstance(doc, dict):
            on_map = normalize_on(doc.get("on"))
            on_events = sorted(list(on_map.keys()))
            has_dispatch = "workflow_dispatch" in on_map

        findings.append(
            WorkflowFinding(
                path=str(p.relative_to(repo_root)).replace("\\", "/"),
                yaml_ok=ok,
                yaml_error=err if not ok else "",
                has_workflow_dispatch=has_dispatch,
                on_events=on_events,
                referenced_secrets=refs["secrets"],
                referenced_vars=refs["vars"],
                referenced_env=refs["env"],
            )
        )
    return findings, meta


def build_markdown_summary(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# SCW Workflow Runnability Audit\n\n")
    lines.append(f"- Generated at (UTC): `{payload['generated_at_utc']}`\n")
    lines.append(f"- Repo: `{payload.get('repo', '?')}`\n")
    lines.append(f"- Default branch: `{payload.get('repo_api', {}).get('default_branch', '?')}`\n\n")

    api = payload.get("repo_api", {})
    if api.get("note"):
        lines.append(f"> API note: {api['note']}\n\n")

    lines.append("## Workflows\n\n")
    lines.append("| Workflow | YAML | Dispatch | Events | Notes |\n")
    lines.append("|---|:---:|:---:|---|---|\n")

    for w in payload.get("workflows", []):
        yaml_ok = "✅" if w["yaml_ok"] else "❌"
        disp = "✅" if w["has_workflow_dispatch"] else "➖"
        events = ", ".join(w.get("on_events", []))[:80]
        note = ""
        if not w["yaml_ok"]:
            note = (w.get("yaml_error") or "")[:80]
        elif not w["has_workflow_dispatch"]:
            note = "missing workflow_dispatch"
        lines.append(f"| `{w['path']}` | {yaml_ok} | {disp} | {events} | {note} |\n")

    lines.append("\n## Referenced Secrets / Vars (union)\n\n")
    lines.append(f"- secrets: `{', '.join(payload.get('refs_union', {}).get('secrets', [])) or '(none)'}`\n")
    lines.append(f"- vars: `{', '.join(payload.get('refs_union', {}).get('vars', [])) or '(none)'}`\n")
    lines.append(f"- env: `{', '.join(payload.get('refs_union', {}).get('env', [])) or '(none)'}`\n\n")

    lines.append("## API Signals (best-effort)\n\n")
    lines.append("```json\n")
    lines.append(json.dumps(payload.get("api_signals", {}), indent=2, sort_keys=True))
    lines.append("\n```\n")
    return "".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_dir = repo_root / "reports" / "guardians"
    out_dir.mkdir(parents=True, exist_ok=True)

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_STEGVERSE_AI_TOKEN")
    owner, name = infer_owner_repo()

    generated_at = now_utc()

    wf_findings, wf_meta = scan_workflows(repo_root)

    # Union of referenced secrets/vars/env across all workflow files
    union = {"secrets": set(), "vars": set(), "env": set()}
    for w in wf_findings:
        union["secrets"].update(w.referenced_secrets)
        union["vars"].update(w.referenced_vars)
        union["env"].update(w.referenced_env)

    refs_union = {
        "secrets": sorted(union["secrets"]),
        "vars": sorted(union["vars"]),
        "env": sorted(union["env"]),
    }

    repo_api: Dict[str, Any] = {}
    api_signals: Dict[str, Any] = {
        "github_repository": os.getenv("GITHUB_REPOSITORY"),
        "actor": os.getenv("GITHUB_ACTOR"),
        "token_present": bool(token),
    }

    # Best-effort API queries (won't fail the run if blocked)
    if owner and name:
        ok, data, err = gh_api_try(f"https://api.github.com/repos/{owner}/{name}", token)
        if ok:
            repo_api = {
                "full_name": data.get("full_name"),
                "private": data.get("private"),
                "default_branch": data.get("default_branch"),
                "archived": data.get("archived"),
                "disabled": data.get("disabled"),
                "visibility": data.get("visibility"),
            }
            api_signals["repo"] = repo_api
        else:
            repo_api = {"note": f"Repo API unavailable: {err}"}
            api_signals["repo_error"] = err

        # Workflows API (detect state, helpful for ScannerError-type issues)
        ok2, data2, err2 = gh_api_try(f"https://api.github.com/repos/{owner}/{name}/actions/workflows?per_page=100", token)
        if ok2:
            api_signals["actions_workflows_count"] = len(data2.get("workflows", []))
            # map path->state if possible (some entries include "path")
            wf_states = []
            for wf in data2.get("workflows", []):
                wf_states.append({
                    "name": wf.get("name"),
                    "state": wf.get("state"),
                    "path": wf.get("path"),
                })
            api_signals["actions_workflows"] = wf_states
        else:
            api_signals["actions_workflows_error"] = err2

        # Repo Actions permissions endpoint (may be blocked for GITHUB_TOKEN)
        ok3, data3, err3 = gh_api_try(f"https://api.github.com/repos/{owner}/{name}/actions/permissions", token)
        if ok3:
            api_signals["actions_permissions"] = data3
        else:
            api_signals["actions_permissions_note"] = f"Not accessible: {err3}"

        # GITHUB_TOKEN default permission setting (may be blocked)
        ok4, data4, err4 = gh_api_try(f"https://api.github.com/repos/{owner}/{name}/actions/permissions/workflow", token)
        if ok4:
            api_signals["actions_workflow_token_permissions"] = data4
        else:
            api_signals["actions_workflow_token_permissions_note"] = f"Not accessible: {err4}"

    payload: Dict[str, Any] = {
        "generated_at_utc": generated_at,
        "repo": os.getenv("GITHUB_REPOSITORY", repo_root.name),
        "workflows_meta": wf_meta,
        "workflows": [
            {
                "path": w.path,
                "yaml_ok": w.yaml_ok,
                "yaml_error": w.yaml_error,
                "has_workflow_dispatch": w.has_workflow_dispatch,
                "on_events": w.on_events,
                "referenced_secrets": w.referenced_secrets,
                "referenced_vars": w.referenced_vars,
                "referenced_env": w.referenced_env,
            }
            for w in wf_findings
        ],
        "refs_union": refs_union,
        "repo_api": repo_api,
        "api_signals": api_signals,
    }

    (out_dir / "workflow_runnability_latest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (out_dir / "workflow_runnability_latest.md").write_text(
        build_markdown_summary(payload),
        encoding="utf-8",
    )

    # Exit code policy:
    # - If workflows dir missing: warning but ok
    # - If any YAML parse error: nonzero (so it is loud)
    yaml_errors = [w for w in wf_findings if not w.yaml_ok]
    return 0 if not yaml_errors else 4


if __name__ == "__main__":
    raise SystemExit(main())
