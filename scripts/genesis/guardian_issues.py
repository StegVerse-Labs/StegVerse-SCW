#!/usr/bin/env python
"""
StegVerse Guardian Issues (Genesis v0.2)

Reads:
  - reports/guardians/guardian_run_latest.json

Maintains:
  - reports/guardians/guardian_issues_index.json

Creates/updates GitHub issues for guardian findings, using stable "keys"
so we don't open duplicates on each run.

Current scope:
  - Missing README.md directories (readme_refresh)
  - Workflow health warnings (workflow_health)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests  # installed by guardians workflow


ROOT = Path(__file__).resolve().parents[2]  # .../StegVerse-SCW
REPORT_DIR = ROOT / "reports" / "guardians"
LATEST_JSON = REPORT_DIR / "guardian_run_latest.json"
ISSUE_INDEX_JSON = REPORT_DIR / "guardian_issues_index.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_latest_run() -> Dict[str, Any]:
    if not LATEST_JSON.exists():
        raise SystemExit(f"Latest guardian JSON not found: {LATEST_JSON}")
    with LATEST_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_issue_index() -> Dict[str, Any]:
    if not ISSUE_INDEX_JSON.exists():
        return {"version": 1, "issues": {}}
    with ISSUE_INDEX_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f) or {}
    if "issues" not in data:
        data["issues"] = {}
    return data


def save_issue_index(idx: Dict[str, Any]) -> None:
    ISSUE_INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    with ISSUE_INDEX_JSON.open("w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, sort_keys=True)


def get_repo_and_token() -> (str, str, str):
    repo_full = os.getenv("GITHUB_REPOSITORY")
    if not repo_full:
        raise SystemExit("GITHUB_REPOSITORY is not set in environment.")
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN (or GH_TOKEN) is not set; needed to create issues.")

    owner, name = repo_full.split("/", 1)
    return owner, name, token


def gh_api(
    method: str,
    path: str,
    token: str,
    json_body: Optional[Dict[str, Any]] = None,
) -> requests.Response:
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.request(method, url, headers=headers, json=json_body, timeout=20)
    if resp.status_code >= 400:
        raise RuntimeError(f"GitHub API {method} {path} failed: {resp.status_code} {resp.text}")
    return resp


def ensure_issue(
    *,
    key: str,
    title: str,
    body: str,
    labels: List[str],
    idx: Dict[str, Any],
    owner: str,
    repo: str,
    token: str,
) -> Dict[str, Any]:
    """
    Ensure there is a single GitHub issue associated with this logical "key".
    - If not present in index -> create new issue and record it.
    - If present -> update body (and reopen if closed).
    """
    issues_idx = idx.setdefault("issues", {})
    existing = issues_idx.get(key)

    if existing:
        issue_number = existing.get("number")
        if not issue_number:
            existing = None

    if existing:
        # Fetch issue state
        path = f"/repos/{owner}/{repo}/issues/{issue_number}"
        resp = gh_api("GET", path, token)
        data = resp.json()
        state = data.get("state", "open")

        patch_body = {"body": body}
        if state == "closed":
            patch_body["state"] = "open"

        gh_api("PATCH", path, token, patch_body)
        issues_idx[key]["last_updated_body_len"] = len(body)
        issues_idx[key]["state"] = "open"
        print(f"Updated guardian issue #{issue_number} for key={key}")
        return idx

    # Create new issue
    path = f"/repos/{owner}/{repo}/issues"
    payload = {
        "title": title,
        "body": body,
        "labels": labels,
    }
    resp = gh_api("POST", path, token, payload)
    data = resp.json()
    issue_number = data.get("number")

    issues_idx[key] = {
        "number": issue_number,
        "state": "open",
        "title": title,
        "labels": labels,
    }
    print(f"Created new guardian issue #{issue_number} for key={key}")
    return idx


# ---------------------------------------------------------------------------
# Issue generators for specific guardian tasks
# ---------------------------------------------------------------------------

def build_readme_missing_issue(run_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    From the readme_refresh task, construct a single issue if there are
    missing README directories.
    """
    for task in run_data.get("tasks", []):
        if task.get("id") == "readme_refresh":
            status = (task.get("status") or "").lower()
            details = task.get("details") or {}
            missing = details.get("readme_missing") or []
            if not missing:
                return None

            summary = task.get("summary", "").strip()
            run_id = run_data.get("run_id", "unknown")
            generated_at = run_data.get("generated_at", "unknown")

            lines: List[str] = []
            lines.append("Guardian task `readme_refresh` detected directories missing `README.md`.")
            lines.append("")
            lines.append(f"- Guardian run ID: `{run_id}`")
            lines.append(f"- Generated at: `{generated_at}`")
            lines.append(f"- Guardian status: **{status}**")
            if summary:
                lines.append(f"- Guardian summary: {summary}")
            lines.append("")
            lines.append("## Directories missing README.md")
            lines.append("")
            for d in sorted(missing):
                lines.append(f"- [ ] `{d}`")
            lines.append("")
            lines.append("## Suggested actions")
            lines.append("")
            lines.append("- For each directory, create a `README.md` that includes:")
            lines.append("  - Purpose of the folder")
            lines.append("  - Key files / scripts")
            lines.append("  - How to run or use them (if applicable)")
            lines.append("")
            lines.append("_This issue is managed by StegVerse guardians; editing the list above is safe._")

            return {
                "key": "readme_refresh_missing",
                "title": "[Guardian] Missing README.md in key directories",
                "body": "\n".join(lines),
                "labels": ["guardian", "documentation"],
            }
    return None


def build_workflow_health_issue(run_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    From the workflow_health task, open a tracking issue if there are warnings.
    """
    for task in run_data.get("tasks", []):
        if task.get("id") == "workflow_health":
            status = (task.get("status") or "").lower()
            if status == "ok":
                return None  # no issue needed when healthy

            details = task.get("details") or {}
            workflow_files = details.get("workflow_files") or []
            count = details.get("count", len(workflow_files))
            summary = task.get("summary", "").strip()
            run_id = run_data.get("run_id", "unknown")
            generated_at = run_data.get("generated_at", "unknown")

            lines: List[str] = []
            lines.append("Guardian task `workflow_health` reported warnings about GitHub workflows.")
            lines.append("")
            lines.append(f"- Guardian run ID: `{run_id}`")
            lines.append(f"- Generated at: `{generated_at}`")
            lines.append(f"- Guardian status: **{status}**")
            if summary:
                lines.append(f"- Guardian summary: {summary}")
            lines.append("")
            lines.append(f"Detected **{count}** workflow file(s):")
            lines.append("")
            for name in sorted(workflow_files):
                lines.append(f"- `{name}`")
            lines.append("")
            lines.append("## Suggested actions")
            lines.append("")
            lines.append("- [ ] Confirm each workflow has at least one trigger (`workflow_dispatch`, `schedule`, or `push`).")
            lines.append("- [ ] Mark high-priority workflows that should be guarded for uptime.")
            lines.append("- [ ] Retire or archive workflows that are obsolete or unused.")
            lines.append("")
            lines.append("_This issue is managed by StegVerse guardians; it may be updated automatically._")

            return {
                "key": "workflow_health_warning",
                "title": "[Guardian] Workflow health warnings",
                "body": "\n".join(lines),
                "labels": ["guardian", "workflows"],
            }
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== StegVerse Guardian Issues (Genesis v0.2) ===")

    run_data = load_latest_run()
    issue_index = load_issue_index()
    owner, repo, token = get_repo_and_token()

    # Collect desired issues from current guardian run
    issue_specs: List[Dict[str, Any]] = []

    readme_issue = build_readme_missing_issue(run_data)
    if readme_issue:
        issue_specs.append(readme_issue)

    wf_issue = build_workflow_health_issue(run_data)
    if wf_issue:
        issue_specs.append(wf_issue)

    if not issue_specs:
        print("No guardian issues to create/update based on latest run.")
        save_issue_index(issue_index)
        return 0

    for spec in issue_specs:
        issue_index = ensure_issue(
            key=spec["key"],
            title=spec["title"],
            body=spec["body"],
            labels=spec["labels"],
            idx=issue_index,
            owner=owner,
            repo=repo,
            token=token,
        )

    save_issue_index(issue_index)
    print("Guardian issue index updated.")
    print("=== Guardian Issues completed. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
