"""
Guardian Task: workflow_health

Checks the recent health of critical workflows across StegVerse repos.

- Uses `gh` CLI (expects GH_TOKEN/GITHUB_TOKEN already configured in the workflow)
- Reads `critical_workflows` from guardian_manifest.json
- Writes a per-task summary dict back to guardian_runner
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]  # tasks -> entities -> scripts -> ROOT


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


def run(*, manifest: Dict[str, Any]) -> Dict[str, Any]:
    gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    env = os.environ.copy()
    if gh_token:
        env["GH_TOKEN"] = gh_token

    critical = manifest.get("critical_workflows", {})
    repos: List[str] = sorted(critical.keys())

    results: List[Dict[str, Any]] = []

    for repo in repos:
        workflows = critical.get(repo, [])
        for wf_name in workflows:
            # Use gh to list last few runs of this workflow by name
            cmd = (
                f'gh run list --repo "{repo}" '
                f'--workflow "{wf_name}" '
                f'--limit 1 --json databaseId,status,conclusion,createdAt,updatedAt'
            )
            out = _run(cmd, env)
            try:
                data = json.loads(out)
            except Exception:
                # gh prints errors as plain text; not JSON
                results.append({
                    "repo": repo,
                    "workflow": wf_name,
                    "status": "error",
                    "raw_output": out.strip(),
                })
                continue

            if not data:
                results.append({
                    "repo": repo,
                    "workflow": wf_name,
                    "status": "no_runs",
                })
                continue

            last = data[0]
            status = last.get("status")
            conclusion = last.get("conclusion")
            updated_at = last.get("updatedAt")

            if conclusion == "success":
                health = "healthy"
            elif conclusion in ("failure", "cancelled", "timed_out", "stale"):
                health = "failing"
            else:
                health = f"status:{status}, conclusion:{conclusion}"

            results.append({
                "repo": repo,
                "workflow": wf_name,
                "status": health,
                "last_status": status,
                "last_conclusion": conclusion,
                "last_updated": updated_at,
            })

    # Summarize
    total = len(results)
    failing = sum(1 for r in results if r["status"] == "failing")
    healthy = sum(1 for r in results if r["status"] == "healthy")
    no_runs = sum(1 for r in results if r["status"] == "no_runs")
    errors = sum(1 for r in results if r["status"] == "error")

    summary = (
        f"{total} workflow(s) checked — "
        f"{healthy} healthy, {failing} failing, "
        f"{no_runs} with no runs, {errors} errors."
    )

    # Write a detailed report file for this task
    reports_dir = ROOT / manifest.get("reports_dir", "reports/guardians")
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    report_path = reports_dir / f"workflow_health_{ts.replace(':','-')}.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("=== workflow_health ===")
    print(summary)

    return {
        "task": "workflow_health",
        "status": "ok",
        "summary": summary,
        "checked": total,
        "healthy": healthy,
        "failing": failing,
        "no_runs": no_runs,
        "errors": errors,
    }
