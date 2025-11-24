#!/usr/bin/env python
"""
StegVerse PAT Auditor (ASL-1)

What it does:
  - Discovers PATs from environment.
  - Verifies each PAT can authenticate.
  - Probes repo read/write access in up to two orgs.
  - Detects workflow-write capability (common pain point).
  - Writes markdown + json report to reports/pat_audit/.

How to pass PATs:
  For each token define:
    <KEY>_NAME = human label (string)
    <KEY>_PAT  = token value (secret)

  Example:
    PAT_WORKFLOW_FG_NAME="PAT_WORKFLOW_FG"
    PAT_WORKFLOW_FG_PAT="<secret>"

Safety:
  - Read-only GitHub API calls only.
  - No mutations.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "pat_audit"


# ---------------- Models ----------------

@dataclass
class ProbeResult:
    ok: bool
    status: int
    message: Optional[str] = None
    url: Optional[str] = None
    detail: Optional[Any] = None


@dataclass
class PatAudit:
    label: str
    token_present: bool
    auth_ok: bool
    auth_login: Optional[str]
    auth_type: Optional[str]
    auth_scopes: List[str]

    org_primary: str
    org_secondary: str

    primary_repo_sample: Optional[str]
    secondary_repo_sample: Optional[str]

    can_list_primary_repos: bool
    can_list_secondary_repos: bool

    can_push_primary_sample: bool
    can_push_secondary_sample: bool

    can_write_workflows_primary: bool
    can_write_workflows_secondary: bool

    errors: List[str]


# ---------------- GitHub helpers ----------------

def gh_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "StegVerse-PAT-Auditor",
    }


def summarize_response(r: requests.Response) -> ProbeResult:
    """
    Robust summary that handles JSON object / list / plain text.
    """
    msg = None
    detail = None
    try:
        ct = r.headers.get("content-type", "")
        if "application/json" in ct:
            j = r.json()
            detail = j
            if isinstance(j, dict):
                msg = j.get("message")
            elif isinstance(j, list):
                # list responses don't have "message"
                msg = None
        else:
            detail = r.text[:500]
    except Exception:
        detail = r.text[:500] if hasattr(r, "text") else None

    return ProbeResult(
        ok=r.status_code < 400,
        status=r.status_code,
        message=msg,
        url=r.url,
        detail=detail,
    )


def gh_get(token: str, url: str) -> ProbeResult:
    r = requests.get(url, headers=gh_headers(token), timeout=20)
    return summarize_response(r)


def gh_post(token: str, url: str, json_body: Any) -> ProbeResult:
    r = requests.post(url, headers=gh_headers(token), json=json_body, timeout=20)
    return summarize_response(r)


def whoami(token: str) -> Tuple[bool, Optional[str], Optional[str], List[str], Optional[str]]:
    r = requests.get("https://api.github.com/user", headers=gh_headers(token), timeout=20)
    scopes_hdr = r.headers.get("x-oauth-scopes", "") or ""
    scopes = [s.strip() for s in scopes_hdr.split(",") if s.strip()]

    if r.status_code >= 400:
        pr = summarize_response(r)
        return False, None, None, scopes, pr.message or "auth failed"

    data = r.json()
    login = data.get("login")
    typ = data.get("type")
    return True, login, typ, scopes, None


def list_repos_in_org(token: str, org: str) -> Tuple[bool, Optional[str], int, Optional[str]]:
    url = f"https://api.github.com/orgs/{org}/repos?per_page=1&type=all"
    pr = gh_get(token, url)
    if not pr.ok:
        return False, None, pr.status, pr.message

    sample_name = None
    if isinstance(pr.detail, list) and pr.detail:
        sample_name = pr.detail[0].get("name")
    return True, sample_name, pr.status, None


def probe_push(token: str, org: str, repo: str) -> bool:
    """
    Push-probe WITHOUT writing:
      we check permission via repo endpoint + permissions block.
    """
    url = f"https://api.github.com/repos/{org}/{repo}"
    pr = gh_get(token, url)
    if not pr.ok or not isinstance(pr.detail, dict):
        return False
    perms = pr.detail.get("permissions") or {}
    return bool(perms.get("push"))


def probe_workflow_write(token: str, org: str, repo: str) -> bool:
    """
    Checks whether token appears to have workflow write capability.
    We infer this from permissions + token scopes.

    Note: GitHub does not expose workflow permission directly.
    So:
      - push on repo AND
      - scopes include 'workflow' OR classic full-repo scope
    """
    auth_ok, _, _, scopes, _ = whoami(token)
    if not auth_ok:
        return False

    can_push = probe_push(token, org, repo)
    if not can_push:
        return False

    scope_set = set(scopes)
    if "workflow" in scope_set:
        return True
    if "repo" in scope_set or "public_repo" in scope_set:
        # classic broad scopes usually allow workflow updates *if org allows*
        return True
    return False


# ---------------- PAT discovery ----------------

def discover_pats_from_env() -> List[Tuple[str, str]]:
    """
    Finds env pairs <KEY>_NAME and <KEY>_PAT.
    Returns list of (label, token).
    """
    env = dict(os.environ)
    labels_tokens: List[Tuple[str, str]] = []

    # Find all *_PAT keys
    pat_keys = [k for k in env.keys() if k.endswith("_PAT")]
    for pat_key in sorted(pat_keys):
        base = pat_key[:-4]
        name_key = base + "_NAME"
        label = env.get(name_key, base)
        token = env.get(pat_key, "")
        if token.strip():
            labels_tokens.append((label, token.strip()))

    return labels_tokens


# ---------------- Reporting ----------------

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_reports(audits: List[PatAudit], org_primary: str, org_secondary: str) -> Tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    json_path = REPORT_DIR / f"pat_audit_{ts}.json"
    md_path = REPORT_DIR / f"pat_audit_{ts}.md"

    # JSON
    json_data = {
        "generated_at": now_utc_iso(),
        "org_primary": org_primary,
        "org_secondary": org_secondary,
        "pat_count": len(audits),
        "audits": [asdict(a) for a in audits],
    }
    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

    # Markdown
    lines = []
    lines.append("# StegVerse PAT Audit Report")
    lines.append("")
    lines.append(f"- Generated at (UTC): `{now_utc_iso()}`")
    lines.append(f"- Primary org: `{org_primary}`")
    lines.append(f"- Secondary org: `{org_secondary}`")
    lines.append(f"- PATs audited: `{len(audits)}`")
    lines.append("")

    for a in audits:
        status = "✅ PASS" if (a.auth_ok and (a.can_list_primary_repos or a.can_list_secondary_repos)) else "❌ FAIL"
        lines.append(f"## {a.label} — {status}")
        lines.append("")
        lines.append(f"- Token present: `{a.token_present}`")
        lines.append(f"- Auth OK: `{a.auth_ok}`")
        if a.auth_login:
            lines.append(f"- Auth login: `{a.auth_login}` ({a.auth_type})")
        lines.append(f"- Scopes: `{', '.join(a.auth_scopes) or 'none reported'}`")
        lines.append("")
        lines.append(f"### Org Access")
        lines.append(f"- Can list repos in `{org_primary}`: `{a.can_list_primary_repos}`")
        lines.append(f"- Sample repo: `{a.primary_repo_sample or 'n/a'}`")
        lines.append(f"- Can push sample: `{a.can_push_primary_sample}`")
        lines.append(f"- Can write workflows (inferred): `{a.can_write_workflows_primary}`")
        lines.append("")
        lines.append(f"- Can list repos in `{org_secondary}`: `{a.can_list_secondary_repos}`")
        lines.append(f"- Sample repo: `{a.secondary_repo_sample or 'n/a'}`")
        lines.append(f"- Can push sample: `{a.can_push_secondary_sample}`")
        lines.append(f"- Can write workflows (inferred): `{a.can_write_workflows_secondary}`")
        lines.append("")
        if a.errors:
            lines.append("### Errors / Notes")
            for e in a.errors:
                lines.append(f"- {e}")
            lines.append("")
        lines.append("---")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


# ---------------- Main ----------------

def audit_one(label: str, token: str, org_primary: str, org_secondary: str) -> PatAudit:
    errors: List[str] = []

    token_present = bool(token.strip())

    auth_ok, login, typ, scopes, auth_err = whoami(token)
    if not auth_ok and auth_err:
        errors.append(f"Auth failed: {auth_err}")

    # Primary org
    can_list_primary, prim_sample, prim_status, prim_err = list_repos_in_org(token, org_primary)
    if not can_list_primary:
        errors.append(f"Cannot list repos in {org_primary}: {prim_err or prim_status}")

    can_push_primary = probe_push(token, org_primary, prim_sample) if prim_sample else False
    can_write_wf_primary = probe_workflow_write(token, org_primary, prim_sample) if prim_sample else False

    # Secondary org
    can_list_secondary, sec_sample, sec_status, sec_err = list_repos_in_org(token, org_secondary)
    if not can_list_secondary:
        errors.append(f"Cannot list repos in {org_secondary}: {sec_err or sec_status}")

    can_push_secondary = probe_push(token, org_secondary, sec_sample) if sec_sample else False
    can_write_wf_secondary = probe_workflow_write(token, org_secondary, sec_sample) if sec_sample else False

    return PatAudit(
        label=label,
        token_present=token_present,
        auth_ok=auth_ok,
        auth_login=login,
        auth_type=typ,
        auth_scopes=scopes,

        org_primary=org_primary,
        org_secondary=org_secondary,

        primary_repo_sample=prim_sample,
        secondary_repo_sample=sec_sample,

        can_list_primary_repos=can_list_primary,
        can_list_secondary_repos=can_list_secondary,

        can_push_primary_sample=can_push_primary,
        can_push_secondary_sample=can_push_secondary,

        can_write_workflows_primary=can_write_wf_primary,
        can_write_workflows_secondary=can_write_wf_secondary,

        errors=errors,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--org-primary", default="StegVerse")
    ap.add_argument("--org-secondary", default="StegVerse-Labs")
    ap.add_argument("--strict", default="false")
    args = ap.parse_args()

    org_primary = args.org_primary
    org_secondary = args.org_secondary
    strict = (args.strict or "false").lower() == "true"

    pats = discover_pats_from_env()
    if not pats:
        print("No PATs found in env. Provide <KEY>_NAME + <KEY>_PAT pairs.")
        print("Example: PAT_WORKFLOW_FG_NAME / PAT_WORKFLOW_FG_PAT")
        return 1

    audits: List[PatAudit] = []
    any_fail = False

    for label, token in pats:
        print(f"\n--- Auditing {label} ---")
        a = audit_one(label, token, org_primary, org_secondary)
        audits.append(a)

        passed = a.auth_ok and (a.can_list_primary_repos or a.can_list_secondary_repos)
        any_fail = any_fail or (not passed)

        print(f"Auth OK: {a.auth_ok} | {org_primary} list: {a.can_list_primary_repos} | {org_secondary} list: {a.can_list_secondary_repos}")

    md_path, json_path = write_reports(audits, org_primary, org_secondary)

    print("\nReport written:")
    print(f"- {md_path}")
    print(f"- {json_path}")

    if strict and any_fail:
        print("\nSTRICT mode enabled: failing job due to PAT failures.")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
