#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

GITHUB_API = "https://api.github.com"


@dataclass
class RepoStatus:
    ok: bool
    missing_files: List[str]
    missing_workflows: List[str]
    notes: List[str]


@dataclass
class RepoScan:
    scan_fingerprint: str
    requirements_hash: str
    kit_version: str
    skipped_deep_scan: bool


@dataclass
class RepoRow:
    repo: str
    private: bool
    archived: bool
    default_branch: str
    head_sha: str
    classification: Dict[str, Any]
    requirements: Dict[str, Any]
    status: RepoStatus
    scan: RepoScan


def _http_get_json(url: str, token: Optional[str] = None) -> Any:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "stegverse-scw-constitutional-audit")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _file_exists(repo_full: str, path: str, token: Optional[str]) -> bool:
    # For public repos, unauthenticated is fine.
    url = f"{GITHUB_API}/repos/{repo_full}/contents/{path}"
    try:
        _http_get_json(url, token)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def _list_org_repos(org: str, token: Optional[str]) -> List[Dict[str, Any]]:
    repos: List[Dict[str, Any]] = []
    page = 1
    while True:
        url = f"{GITHUB_API}/orgs/{org}/repos?per_page=100&page={page}&type=public"
        batch = _http_get_json(url, token)
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def _get_head_sha(repo_full: str, branch: str, token: Optional[str]) -> str:
    url = f"{GITHUB_API}/repos/{repo_full}/commits/{branch}"
    j = _http_get_json(url, token)
    return j.get("sha", "")


def _has_any_signal(repo_full: str, signals: Dict[str, Any], token: Optional[str]) -> Tuple[bool, List[str]]:
    hits: List[str] = []
    for p in signals.get("paths_any", []):
        if _file_exists(repo_full, p, token):
            hits.append(p)
    for f in signals.get("filenames_any", []):
        # Try docs/ first, then root. Cheap best-effort.
        if _file_exists(repo_full, f"docs/{f}", token) or _file_exists(repo_full, f, token):
            hits.append(f)
    return (len(hits) > 0), hits


def _classify(repo_name: str, signal_hits: List[str]) -> Dict[str, Any]:
    lname = repo_name.lower()

    # Deterministic rule: if signals indicate policy/schema/verification surfaces, flag as constitutional-candidate.
    constitutional_candidate = any(
        h.startswith("schemas/") or h.startswith("docs/governance/") or "resolver" in h or "tv_manifest" in h or "roles_templates" in h
        for h in signal_hits
    )

    # Minimal purpose inference (you’ll override later in StegDB repo_index.json).
    if lname in {"stegseed", "stegid", "governance", "tv", "tvc"}:
        purpose = lname
        tier = "constitutional-required"
    elif lname in {"stegdb", "stegverse-scw", "scw", "stegbrain", "stegcore"}:
        purpose = lname
        tier = "constitutional-recommended"
    elif constitutional_candidate:
        purpose = "constitutional-candidate"
        tier = "constitutional-recommended"
    else:
        purpose = "standard"
        tier = "standard"

    return {
        "purpose_guess": purpose,
        "tier_guess": tier,
        "constitutional_candidate": constitutional_candidate,
        "signal_hits": signal_hits
    }


def main() -> int:
    """
    Public-only audit. Produces:
      - matrix.json (machine-readable)
      - matrix.md   (human-readable summary)
    """
    org = os.environ.get("ORG", "StegVerse-Labs")
    # Optional: if StegDB becomes private later, set a token here.
    token = os.environ.get("SV_SCAN_TOKEN")  # unused for public unless you want higher rate limits

    requirements_url = os.environ.get(
        "REQUIREMENTS_URL",
        f"https://raw.githubusercontent.com/{org}/StegDB/main/registry/requirements_catalog.json"
    )

    reqs = _http_get_json(requirements_url, token=None)
    kit_version = reqs.get("kit_version", "unknown")
    required_files = reqs.get("required_files", [])
    required_workflows = reqs.get("required_workflows", [])
    signals = reqs.get("constitutional_signals", {})

    requirements_hash = _sha256_text(json.dumps(reqs, sort_keys=True))

    repos = _list_org_repos(org, token=None)

    rows: List[RepoRow] = []
    started = time.time()

    for r in repos:
        repo_full = r["full_name"]
        repo_name = r["name"]
        private = bool(r.get("private", False))
        archived = bool(r.get("archived", False))
        default_branch = r.get("default_branch", "main")

        # Public-only: skip private (should not occur in org public listing, but keep safe)
        if private:
            continue

        head_sha = _get_head_sha(repo_full, default_branch, token=None)

        # fingerprint used later for skip logic (once you persist last_scan in StegDB)
        scan_fingerprint = _sha256_text(f"{repo_full}|{default_branch}|{head_sha}|{requirements_hash}|{kit_version}")

        # Classification signals (cheap file probes)
        has_signals, hits = _has_any_signal(repo_full, signals, token=None)
        classification = _classify(repo_name, hits)

        # Requirements checks
        missing_files = [p for p in required_files if not _file_exists(repo_full, p, token=None)]
        missing_workflows = [p for p in required_workflows if not _file_exists(repo_full, p, token=None)]

        ok = (len(missing_files) == 0 and len(missing_workflows) == 0)

        notes: List[str] = []
        if archived:
            notes.append("archived=true")
        if not has_signals:
            notes.append("no_constitutional_signals_detected")

        status = RepoStatus(
            ok=ok,
            missing_files=missing_files,
            missing_workflows=missing_workflows,
            notes=notes
        )

        scan = RepoScan(
            scan_fingerprint=scan_fingerprint,
            requirements_hash=requirements_hash,
            kit_version=kit_version,
            skipped_deep_scan=False
        )

        rows.append(
            RepoRow(
                repo=repo_full,
                private=private,
                archived=archived,
                default_branch=default_branch,
                head_sha=head_sha,
                classification=classification,
                requirements={
                    "required_files": required_files,
                    "required_workflows": required_workflows
                },
                status=status,
                scan=scan
            )
        )

    # Build outputs
    matrix = {
        "schema": "repo_compliance_matrix.v1",
        "org": org,
        "mode": "public_only",
        "kit_version": kit_version,
        "requirements_url": requirements_url,
        "generated_at_unix": int(time.time()),
        "duration_s": round(time.time() - started, 2),
        "summary": {
            "total_public_repos": len(rows),
            "ok": sum(1 for x in rows if x.status.ok),
            "fail": sum(1 for x in rows if not x.status.ok),
            "constitutional_required_guess": sum(1 for x in rows if x.classification.get("tier_guess") == "constitutional-required"),
            "constitutional_recommended_guess": sum(1 for x in rows if x.classification.get("tier_guess") == "constitutional-recommended")
        },
        "repos": [
            {
                **{k: v for k, v in asdict(x).items() if k not in ("status", "scan")},
                "status": asdict(x.status),
                "scan": asdict(x.scan)
            }
            for x in rows
        ]
    }

    with open("matrix.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2)

    # Human-readable summary
    lines: List[str] = []
    lines.append(f"# Repo Compliance Matrix (Public Only) — {org}")
    lines.append("")
    lines.append(f"- Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(matrix['generated_at_unix']))}")
    lines.append(f"- Kit: `{kit_version}`")
    lines.append(f"- Total public repos: **{matrix['summary']['total_public_repos']}**")
    lines.append(f"- OK: **{matrix['summary']['ok']}** | Fail: **{matrix['summary']['fail']}**")
    lines.append("")
    lines.append("## Failing Repos (Missing kit components)")
    lines.append("")
    any_fail = False
    for x in rows:
        if x.status.ok:
            continue
        any_fail = True
        lines.append(f"- **{x.repo}**")
        if x.status.missing_workflows:
            lines.append(f"  - Missing workflows: {', '.join(x.status.missing_workflows)}")
        if x.status.missing_files:
            lines.append(f"  - Missing files: {', '.join(x.status.missing_files)}")
    if not any_fail:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Constitutional Candidates (signal-based guess)")
    lines.append("")
    for x in rows:
        if x.classification.get("constitutional_candidate"):
            hits = x.classification.get("signal_hits", [])
            lines.append(f"- **{x.repo}** — hits: {', '.join(hits) if hits else '(none)'}")

    with open("matrix.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps(matrix["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
