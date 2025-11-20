"""
Guardian Task: readme_refresh

Phase 1:
- Scans configured repos/readme_targets from guardian_manifest
- Fetches current README content via `gh api`
- Produces a "refresh plan" report (what should be clarified/added), but does NOT edit files yet.

Later:
- You can wire in GitHub Models / StegTVC to propose new README content
- And either open PRs or apply changes automatically.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]


def _run(cmd: str, env: Dict[str, str]) -> str:
    proc = subprocess.run(
        cmd,
        shell=True,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc.stdout


def _fetch_file(repo: str, path: str, env: Dict[str, str]) -> str:
    # Use gh api to fetch a file's contents (raw)
    cmd = f'gh api repos/{repo}/contents/{path} --jq ".content"'
    out = _run(cmd, env).strip()
    if not out or out.startswith("Not Found"):
        return ""
    # content is base64; decode via Python
    import base64
    try:
        return base64.b64decode(out).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def run(*, manifest: Dict[str, Any]) -> Dict[str, Any]:
    gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    env = os.environ.copy()
    if gh_token:
        env["GH_TOKEN"] = gh_token

    readme_targets: Dict[str, List[str]] = manifest.get("readme_targets", {})
    results: List[Dict[str, Any]] = []

    for repo, paths in sorted(readme_targets.items()):
        for path in paths:
            content = _fetch_file(repo, path, env)
            if not content:
                results.append({
                    "repo": repo,
                    "path": path,
                    "status": "missing_or_inaccessible",
                })
                continue

            # Very simple heuristic: check for key sections
            needed_sections = ["Quick Start", "For Developers", "For AI Entities", "Troubleshooting"]
            missing_sections = [s for s in needed_sections if s.lower() not in content.lower()]

            status = "ok" if not missing_sections else "needs_improvement"

            results.append({
                "repo": repo,
                "path": path,
                "status": status,
                "missing_sections": missing_sections,
            })

    # Summarize
    total = len(results)
    needs = sum(1 for r in results if r["status"] == "needs_improvement")
    missing = sum(1 for r in results if r["status"] == "missing_or_inaccessible")

    summary = (
        f"{total} README targets scanned — "
        f"{needs} need improvements, {missing} missing/inaccessible."
    )

    reports_dir = ROOT / manifest.get("reports_dir", "reports/guardians")
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    report_path = reports_dir / f"readme_refresh_{ts.replace(':','-')}.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("=== readme_refresh ===")
    print(summary)

    return {
        "task": "readme_refresh",
        "status": "ok",
        "summary": summary,
        "targets": total,
        "needs_improvement": needs,
        "missing": missing,
    }
