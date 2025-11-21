#!/usr/bin/env python
"""
StegVerse Guardian Worker: Repo Alignment Check (ASL-1)

What it does:
  - Discovers repos in the StegVerse org (or uses explicit list if provided).
  - Clones each repo shallowly.
  - Checks for cross-repo alignment scaffolding:
      * docs/governance/automation_safety_levels.yaml
      * .github/workflows/* having workflow_dispatch (reported only)
      * README.md existence at repo root
      * SCW link metadata file: docs/stegverse/.steglink.json (or .steglink.yaml)
      * Standard folders (optional): docs/, scripts/, .github/workflows/
  - Writes a JSON + Markdown report into reports/guardians/

Safety:
  - ASL-1: read-only on target repos (no writes).
  - Writes reports only in StegVerse-SCW.

Env:
  - STEGVERSE_ORG (default: StegVerse-Labs)
  - STEGVERSE_REPOS (optional comma list override)
  - GH_TOKEN / GITHUB_TOKEN / STEG_TOKEN for GitHub API + clone auth
"""

from __future__ import annotations

import json, os, re, sys, textwrap, subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "guardians"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_ORG = os.getenv("STEGVERSE_ORG", "StegVerse-Labs")
REPO_OVERRIDE = os.getenv("STEGVERSE_REPOS", "").strip()

TOKEN = (
    os.getenv("STEG_TOKEN")
    or os.getenv("GH_TOKEN")
    or os.getenv("GITHUB_TOKEN")
    or ""
).strip()

@dataclass
class RepoResult:
    name: str
    url: str
    pass_ok: bool
    checks: Dict[str, bool]
    notes: List[str]

def run(cmd: List[str], cwd: Optional[Path]=None, check: bool=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)

def gh_api(path: str) -> dict:
    """
    Minimal GitHub REST call using curl (keeps deps light).
    """
    if not TOKEN:
        raise RuntimeError("No GH token in env (STEG_TOKEN/GH_TOKEN/GITHUB_TOKEN).")

    url = f"https://api.github.com{path}"
    cmd = ["curl", "-sS", "-H", f"Authorization: token {TOKEN}", "-H", "Accept: application/vnd.github+json", url]
    cp = run(cmd, check=True)
    try:
        return json.loads(cp.stdout)
    except Exception as e:
        raise RuntimeError(f"GitHub API parse failed on {url}: {e}\n{cp.stdout}")

def discover_repos(org: str) -> List[str]:
    """
    Discover up to 100 repos in org (paging if needed).
    """
    repos: List[str] = []
    page = 1
    while True:
        data = gh_api(f"/orgs/{org}/repos?per_page=100&page={page}")
        if not isinstance(data, list) or not data:
            break
        for r in data:
            name = r.get("name")
            if name:
                repos.append(f"{org}/{name}")
        page += 1
        if page > 10:
            break
    return sorted(set(repos))

def clone_repo(full_name: str, workdir: Path) -> Tuple[bool, str]:
    """
    Shallow clone. Returns (ok, log).
    """
    org, repo = full_name.split("/", 1)
    url = f"https://x-access-token:{TOKEN}@github.com/{org}/{repo}.git" if TOKEN else f"https://github.com/{org}/{repo}.git"
    dest = workdir / repo

    if dest.exists():
        run(["rm", "-rf", str(dest)], check=False)

    try:
        cp = run(["git", "clone", "--depth", "1", url, str(dest)], cwd=workdir, check=True)
        return True, cp.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stdout

def file_exists(repo_root: Path, rel: str) -> bool:
    return (repo_root / rel).exists()

def has_workflow_dispatch_in_any(repo_root: Path) -> bool:
    wf_dir = repo_root / ".github" / "workflows"
    if not wf_dir.exists():
        return False
    for p in wf_dir.glob("*.yml"):
        txt = p.read_text("utf-8", errors="ignore")
        if re.search(r"^\s*workflow_dispatch\s*:", txt, flags=re.M):
            return True
    for p in wf_dir.glob("*.yaml"):
        txt = p.read_text("utf-8", errors="ignore")
        if re.search(r"^\s*workflow_dispatch\s*:", txt, flags=re.M):
            return True
    return False

def check_repo(full_name: str, repo_root: Path) -> RepoResult:
    checks: Dict[str, bool] = {}
    notes: List[str] = []
    org, repo = full_name.split("/", 1)

    # Core alignment signals
    checks["has_root_readme"] = file_exists(repo_root, "README.md")
    checks["has_asl_config"] = file_exists(repo_root, "docs/governance/automation_safety_levels.yaml")
    checks["has_steglink"] = (
        file_exists(repo_root, "docs/stegverse/.steglink.json")
        or file_exists(repo_root, "docs/stegverse/.steglink.yaml")
        or file_exists(repo_root, "docs/stegverse/.steglink.yml")
    )
    checks["has_docs_dir"] = file_exists(repo_root, "docs")
    checks["has_scripts_dir"] = file_exists(repo_root, "scripts")
    checks["has_workflows_dir"] = file_exists(repo_root, ".github/workflows")
    checks["has_any_workflow_dispatch"] = has_workflow_dispatch_in_any(repo_root)

    # Evaluate pass
    required = ["has_root_readme", "has_steglink"]
    pass_ok = all(checks.get(k, False) for k in required)

    if not checks["has_any_workflow_dispatch"]:
        notes.append("No workflow_dispatch found in any workflow (reporting only).")
    if not checks["has_asl_config"]:
        notes.append("Missing docs/governance/automation_safety_levels.yaml (fixer can add).")
    if not checks["has_steglink"]:
        notes.append("Missing docs/stegverse/.steglink.(json|yaml) (fixer can add).")

    return RepoResult(
        name=full_name,
        url=f"https://github.com/{org}/{repo}",
        pass_ok=pass_ok,
        checks=checks,
        notes=notes,
    )

def main() -> int:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rid = str(int(datetime.now().timestamp()))

    # Decide repo list
    if REPO_OVERRIDE:
        repos = [r.strip() for r in REPO_OVERRIDE.split(",") if r.strip()]
    else:
        repos = discover_repos(DEFAULT_ORG)

    workdir = ROOT / ".tmp_alignment"
    workdir.mkdir(parents=True, exist_ok=True)

    results: List[RepoResult] = []
    scanned = 0
    for full in repos:
        scanned += 1
        ok, log = clone_repo(full, workdir)
        if not ok:
            results.append(RepoResult(
                name=full,
                url=f"https://github.com/{full}",
                pass_ok=False,
                checks={"clone_ok": False},
                notes=[f"Clone failed. Log:\n{log.strip()}"]
            ))
            continue
        repo_root = workdir / full.split("/", 1)[1]
        res = check_repo(full, repo_root)
        res.checks["clone_ok"] = True
        results.append(res)

    # Summary counts
    repos_total = len(results)
    repos_pass = sum(1 for r in results if r.pass_ok)
    repos_fail = repos_total - repos_pass

    out_json = {
        "repos_total": repos_total,
        "repos_pass": repos_pass,
        "repos_fail": repos_fail,
        "repos_error": 0,
        "ts_utc": ts,
        "rid": rid,
        "org": DEFAULT_ORG,
        "repos": [
            {
                "name": r.name,
                "url": r.url,
                "pass": r.pass_ok,
                "checks": r.checks,
                "notes": r.notes,
            }
            for r in results
        ],
    }

    json_path = REPORT_DIR / "repo_alignment_latest.json"
    md_path = REPORT_DIR / "repo_alignment_latest.md"
    json_path.write_text(json.dumps(out_json, indent=2), encoding="utf-8")

    # Markdown
    lines = []
    lines.append(f"# StegVerse Repo Alignment Report")
    lines.append("")
    lines.append(f"- Generated: `{ts}`")
    lines.append(f"- Org: `{DEFAULT_ORG}`")
    lines.append(f"- Repos scanned: **{repos_total}**")
    lines.append(f"- Pass: **{repos_pass}**")
    lines.append(f"- Fail: **{repos_fail}**")
    lines.append("")
    for r in results:
        status = "✅ PASS" if r.pass_ok else "❌ FAIL"
        lines.append(f"## {status} — {r.name}")
        lines.append(f"- URL: {r.url}")
        for k, v in r.checks.items():
            lines.append(f"  - `{k}`: {'✅' if v else '❌'}")
        if r.notes:
            lines.append("  - Notes:")
            for n in r.notes:
                lines.append(f"    - {n}")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "repos_total": repos_total,
        "repos_pass": repos_pass,
        "repos_fail": repos_fail,
        "repos_error": 0,
        "ts_utc": ts,
        "rid": rid
    }, indent=2))
    print(f"\nReport written:\n- {md_path}\n- {json_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
