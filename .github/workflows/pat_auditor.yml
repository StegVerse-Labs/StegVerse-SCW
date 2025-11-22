#!/usr/bin/env python3
"""
StegVerse PAT Auditor (Genesis v0.2)

Purpose
-------
Audit GitHub Personal Access Tokens (classic + fine-grained) used by StegVerse
workflows. Designed to run inside GitHub Actions, but also works locally.

What it does
------------
For each token:
  1. Verify token is valid and get who it belongs to.
  2. List organizations visible to that token.
  3. For a configured set of target orgs, test:
       - org visibility/membership
       - repo read access
       - repo permission level (pull/push/admin; inferred)
       - workflows read access
  4. Write machine + human reports.

Inputs (env)
------------
- PAT_NAME / PAT_TOKEN:
    Audit a single token explicitly.

OR

- Any env var whose name matches one of:
    * startswith("PAT_")  e.g., PAT_WORKFLOW_FG, PAT_WORKFLOW_CLASSIC
    * endswith("_PAT")    e.g., GH_STEGVERSE_PAT
  and is non-empty, will be audited.

Optional config:
- TARGET_ORGS: comma-separated org list to test (default: "StegVerse,StegVerse-Labs")
- SAMPLE_REPO: repo name to test in each org (default: "StegVerse-SCW")
               If absent in an org, auditor will pick the first repo it can list.
- REPORT_DIR: output folder (default: "scripts/reports/pat_audit")

Safety
------
- Read-only. No writes to any repo or workflow.
- Redacts tokens in all output.
"""

from __future__ import annotations

import json
import os
import sys
import datetime as _dt
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


GITHUB_API = "https://api.github.com"


ROOT = Path(__file__).resolve().parents[2]  # .../StegVerse-SCW
DEFAULT_REPORT_DIR = ROOT / "scripts" / "reports" / "pat_audit"


# -------------------------- helpers --------------------------

def now_utc_iso() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat()


def redact(token: str, show: int = 4) -> str:
    if not token:
        return ""
    if len(token) <= show * 2:
        return "*" * len(token)
    return token[:show] + ("*" * (len(token) - show * 2)) + token[-show:]


def env_tokens() -> Dict[str, str]:
    """
    Collect tokens to audit.
    Priority:
      1) Explicit PAT_NAME + PAT_TOKEN
      2) Any PAT_* or *_PAT env vars
    """
    explicit_name = os.getenv("PAT_NAME")
    explicit_token = os.getenv("PAT_TOKEN")

    toks: Dict[str, str] = {}

    if explicit_name and explicit_token:
        toks[explicit_name.strip()] = explicit_token.strip()
        return toks

    for k, v in os.environ.items():
        if not v or not isinstance(v, str):
            continue
        if k.startswith("PAT_") or k.endswith("_PAT"):
            toks[k] = v.strip()

    return toks


def headers_for(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "stegverse-pat-auditor",
    }


def gh_get(token: str, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    return requests.get(f"{GITHUB_API}{path}", headers=headers_for(token), params=params or {})


def summarize_response(r: requests.Response) -> Dict[str, Any]:
    """
    Safely summarize GitHub API responses.

    Handles:
      - JSON objects (dict)
      - JSON lists
      - Non-JSON responses
    """
    ct = r.headers.get("content-type", "")

    summary: Dict[str, Any] = {
        "status_code": r.status_code,
        "type": None,
        "message": None,
        "size": None,
        "url": r.url,
    }

    if "application/json" not in ct:
        summary["type"] = "non-json"
        try:
            summary["message"] = r.text[:200]
        except Exception:
            pass
        return summary

    try:
        j = r.json()

        if isinstance(j, dict):
            summary["type"] = "object"
            summary["message"] = j.get("message")
            summary["size"] = len(j)

        elif isinstance(j, list):
            summary["type"] = "list"
            summary["size"] = len(j)
            if j:
                summary["message"] = str(j[0])[:200]

        else:
            summary["type"] = type(j).__name__

    except Exception as e:
        summary["type"] = "json-parse-error"
        summary["message"] = str(e)

    return summary


def safe_json(r: requests.Response) -> Any:
    try:
        return r.json()
    except Exception:
        return None


# -------------------------- models --------------------------

@dataclass
class RepoCheck:
    org: str
    repo: str
    ok_repo_read: bool
    permissions: Dict[str, bool]
    ok_workflows_read: bool
    notes: str = ""


@dataclass
class OrgCheck:
    org: str
    ok_visible: bool
    ok_member_or_public: bool
    repo_check: Optional[RepoCheck]
    notes: str = ""


@dataclass
class TokenAudit:
    name: str
    redacted: str
    ok_user: bool
    user_login: Optional[str]
    user_id: Optional[int]
    visible_orgs: List[str]
    target_orgs: List[OrgCheck]
    rate_limit: Optional[Dict[str, Any]]
    errors: List[str]


# -------------------------- audit logic --------------------------

def audit_user(token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    r = gh_get(token, "/user")
    if r.status_code != 200:
        return False, None, f"/user failed: {summarize_response(r)}"
    return True, safe_json(r), None


def list_orgs_visible(token: str) -> Tuple[List[str], Optional[str]]:
    r = gh_get(token, "/user/orgs", params={"per_page": 200})
    if r.status_code != 200:
        return [], f"/user/orgs failed: {summarize_response(r)}"
    data = safe_json(r) or []
    orgs = [o.get("login") for o in data if isinstance(o, dict) and o.get("login")]
    return orgs, None


def check_org_visibility(token: str, org: str, visible_orgs: List[str]) -> OrgCheck:
    # If org is in visible orgs list, we consider it visible.
    ok_visible = org in visible_orgs

    # If org not visible, could still be public-only access. We'll do a GET org.
    r_org = gh_get(token, f"/orgs/{org}")
    ok_org_get = r_org.status_code == 200

    ok_member_or_public = ok_visible or ok_org_get

    notes = ""
    if not ok_member_or_public:
        notes = f"Org not visible and /orgs/{org} not accessible: {summarize_response(r_org)}"

    # Repo check will be filled separately
    return OrgCheck(
        org=org,
        ok_visible=ok_visible,
        ok_member_or_public=ok_member_or_public,
        repo_check=None,
        notes=notes
    )


def pick_sample_repo(token: str, org: str, sample_repo_env: str) -> Tuple[Optional[str], Optional[str]]:
    # Prefer explicit SAMPLE_REPO
    if sample_repo_env:
        # verify it exists & is readable
        r = gh_get(token, f"/repos/{org}/{sample_repo_env}")
        if r.status_code == 200:
            return sample_repo_env, None

    # else list first repo we can see
    r = gh_get(token, f"/orgs/{org}/repos", params={"per_page": 1})
    if r.status_code != 200:
        return None, f"Cannot list repos in {org}: {summarize_response(r)}"
    data = safe_json(r) or []
    if not data:
        return None, f"No repos visible in {org} for this token."
    first = data[0]
    if isinstance(first, dict) and first.get("name"):
        return first["name"], None
    return None, f"Unexpected repo list shape for {org}."


def check_repo_and_workflows(token: str, org: str, repo: str) -> RepoCheck:
    notes = ""

    # Repo read / permissions inference
    r_repo = gh_get(token, f"/repos/{org}/{repo}")
    ok_repo_read = r_repo.status_code == 200
    perms = {"pull": False, "push": False, "admin": False, "maintain": False, "triage": False}

    if ok_repo_read:
        j = safe_json(r_repo) or {}
        p = j.get("permissions") if isinstance(j, dict) else None
        if isinstance(p, dict):
            for k in perms:
                if k in p:
                    perms[k] = bool(p.get(k))
        else:
            notes += "Repo permissions not included in response (common for FG PATs). "
    else:
        notes += f"Repo GET failed: {summarize_response(r_repo)} "

    # Workflows read
    r_wf = gh_get(token, f"/repos/{org}/{repo}/actions/workflows", params={"per_page": 1})
    ok_workflows_read = r_wf.status_code == 200
    if not ok_workflows_read:
        notes += f"Workflows read failed: {summarize_response(r_wf)} "

    return RepoCheck(
        org=org,
        repo=repo,
        ok_repo_read=ok_repo_read,
        permissions=perms,
        ok_workflows_read=ok_workflows_read,
        notes=notes.strip()
    )


def read_rate_limit(token: str) -> Optional[Dict[str, Any]]:
    r = gh_get(token, "/rate_limit")
    if r.status_code != 200:
        return None
    return safe_json(r)


def audit_token(name: str, token: str, target_orgs: List[str], sample_repo_env: str) -> TokenAudit:
    errors: List[str] = []

    ok_user, user_data, err = audit_user(token)
    if err:
        errors.append(err)

    user_login = user_data.get("login") if ok_user and isinstance(user_data, dict) else None
    user_id = user_data.get("id") if ok_user and isinstance(user_data, dict) else None

    visible_orgs, err_orgs = list_orgs_visible(token)
    if err_orgs:
        errors.append(err_orgs)

    org_checks: List[OrgCheck] = []
    for org in target_orgs:
        oc = check_org_visibility(token, org, visible_orgs)

        # only attempt repo checks if we can see org at all
        if oc.ok_member_or_public:
            repo_name, err_repo_pick = pick_sample_repo(token, org, sample_repo_env)
            if err_repo_pick:
                oc.notes = (oc.notes + " " + err_repo_pick).strip()
            if repo_name:
                oc.repo_check = check_repo_and_workflows(token, org, repo_name)
        org_checks.append(oc)

    rl = read_rate_limit(token)

    return TokenAudit(
        name=name,
        redacted=redact(token),
        ok_user=ok_user,
        user_login=user_login,
        user_id=user_id,
        visible_orgs=visible_orgs,
        target_orgs=org_checks,
        rate_limit=rl,
        errors=errors
    )


# -------------------------- reporting --------------------------

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_json(report_dir: Path, audit: TokenAudit) -> Path:
    ensure_dir(report_dir)
    out = report_dir / f"pat_audit_{audit.name}_latest.json"
    out.write_text(json.dumps(asdict(audit), indent=2), encoding="utf-8")
    return out


def write_md(report_dir: Path, audit: TokenAudit) -> Path:
    ensure_dir(report_dir)
    out = report_dir / f"pat_audit_{audit.name}_latest.md"

    lines: List[str] = []
    lines.append(f"# StegVerse PAT Audit — `{audit.name}`")
    lines.append("")
    lines.append(f"- Generated: `{now_utc_iso()}`")
    lines.append(f"- Token: `{audit.redacted}`")
    lines.append(f"- Valid user: `{audit.ok_user}`")
    if audit.user_login:
        lines.append(f"- User: `{audit.user_login}` (id `{audit.user_id}`)")
    lines.append("")

    lines.append("## Visible Orgs")
    if audit.visible_orgs:
        for o in audit.visible_orgs:
            lines.append(f"- ✅ `{o}`")
    else:
        lines.append("- (none visible)")
    lines.append("")

    lines.append("## Target Org Checks")
    for oc in audit.target_orgs:
        lines.append(f"### `{oc.org}`")
        lines.append(f"- Visible in /user/orgs: `{oc.ok_visible}`")
        lines.append(f"- Accessible via /orgs/{oc.org}: `{oc.ok_member_or_public}`")
        if oc.repo_check:
            rc = oc.repo_check
            lines.append(f"- Sample repo: `{rc.repo}`")
            lines.append(f"  - Repo read: `{rc.ok_repo_read}`")
            lines.append(f"  - Workflows read: `{rc.ok_workflows_read}`")
            lines.append("  - Permissions (inferred):")
            for k, v in rc.permissions.items():
                sym = "✅" if v else "❌"
                lines.append(f"    - {sym} `{k}`")
            if rc.notes:
                lines.append(f"  - Notes: {rc.notes}")
        if oc.notes:
            lines.append(f"- Notes: {oc.notes}")
        lines.append("")

    if audit.errors:
        lines.append("## Errors")
        for e in audit.errors:
            lines.append(f"- ❌ {e}")
        lines.append("")

    if audit.rate_limit:
        lines.append("## Rate Limit (raw)")
        lines.append("```json")
        lines.append(json.dumps(audit.rate_limit, indent=2)[:4000])
        lines.append("```")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# -------------------------- main --------------------------

def main() -> int:
    tokens = env_tokens()
    if not tokens:
        print("No PATs found in env. Provide PAT_NAME+PAT_TOKEN or PAT_* / *_PAT vars.")
        return 1

    target_orgs = [o.strip() for o in os.getenv("TARGET_ORGS", "StegVerse,StegVerse-Labs").split(",") if o.strip()]
    sample_repo_env = os.getenv("SAMPLE_REPO", "StegVerse-SCW").strip()
    report_dir = Path(os.getenv("REPORT_DIR", str(DEFAULT_REPORT_DIR)))

    print("=== StegVerse PAT Auditor (Genesis v0.2) ===")
    print(f"Tokens detected: {list(tokens.keys())}")
    print(f"Target orgs: {target_orgs}")
    print(f"Sample repo preference: {sample_repo_env}")
    print(f"Report dir: {report_dir}")
    print("")

    all_audits: Dict[str, Any] = {}

    for name, tok in tokens.items():
        print(f"--- Auditing {name} ({redact(tok)}) ---")
        audit = audit_token(name, tok, target_orgs, sample_repo_env)

        jpath = write_json(report_dir, audit)
        mpath = write_md(report_dir, audit)

        all_audits[name] = asdict(audit)
        print(f"✅ Wrote JSON: {jpath}")
        print(f"✅ Wrote MD:   {mpath}")
        print("")

    # write rollup
    rollup_json = report_dir / "pat_audit_rollup_latest.json"
    rollup_md = report_dir / "pat_audit_rollup_latest.md"

    rollup_json.write_text(json.dumps(all_audits, indent=2), encoding="utf-8")

    md_lines = ["# StegVerse PAT Audit — Rollup", f"- Generated: `{now_utc_iso()}`", ""]
    for name, ad in all_audits.items():
        md_lines.append(f"## `{name}`")
        md_lines.append(f"- Token: `{ad.get('redacted')}`")
        md_lines.append(f"- Valid user: `{ad.get('ok_user')}`")
        md_lines.append(f"- User: `{ad.get('user_login')}`")
        md_lines.append(f"- Visible orgs: {', '.join(ad.get('visible_orgs') or []) or '(none)'}")
        for oc in ad.get("target_orgs", []):
            md_lines.append(f"  - Org `{oc['org']}` accessible: `{oc['ok_member_or_public']}`")
            rc = oc.get("repo_check")
            if rc:
                md_lines.append(f"    - Repo `{rc['repo']}` read: `{rc['ok_repo_read']}`, workflows read: `{rc['ok_workflows_read']}`")
                perms = rc.get("permissions") or {}
                md_lines.append(f"    - Perms: " + ", ".join([f"{k}={v}" for k, v in perms.items()]))
        if ad.get("errors"):
            md_lines.append("  - Errors:")
            for e in ad["errors"]:
                md_lines.append(f"    - ❌ {e}")
        md_lines.append("")

    rollup_md.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"✅ Wrote rollup JSON: {rollup_json}")
    print(f"✅ Wrote rollup MD:   {rollup_md}")
    print("=== PAT audit complete. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
