#!/usr/bin/env python3
"""
StegVerse Guardian Runner v1

- Loads guardian_manifest.json
- Runs guardian tasks in priority order:
  1) workflow_health
  2) readme_refresh

Writes a consolidated report into reports/guardians/.
Designed to be called from a GitHub Actions job using PAT_WORKFLOW/GH_STEGVERSE_PAT.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]  # scripts/entities -> scripts -> ROOT
MANIFEST_PATH = ROOT / "scripts" / "entities" / "guardian_manifest.json"


def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Guardian manifest not found at {MANIFEST_PATH}")
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _call_task(module_name: str, func_name: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Import and run a task function, returning a structured dict.

    module_name: e.g. 'workflow_health'
    func_name:   e.g. 'run'
    """
    from importlib import import_module

    mod_path = f"scripts.entities.tasks.{module_name}"
    mod = import_module(mod_path)
    fn = getattr(mod, func_name)

    return fn(manifest=manifest)


def main() -> None:
    manifest = load_manifest()
    reports_dir = ROOT / manifest.get("reports_dir", "reports/guardians")
    reports_dir.mkdir(parents=True, exist_ok=True)

    priorities = manifest.get("task_priorities", {})
    # Known tasks in this runner
    known_tasks = ["workflow_health", "readme_refresh"]

    # Sort tasks by priority (default big number if not present)
    ordered_tasks = sorted(
        known_tasks,
        key=lambda t: priorities.get(t, 999),
    )

    run_id = os.getenv("GITHUB_RUN_ID", "local")
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    overall: Dict[str, Any] = {
        "run_id": run_id,
        "timestamp_utc": ts,
        "tasks": [],
    }

    print("=== StegVerse Guardian Runner ===")
    print(f"Run ID: {run_id}")
    print(f"Tasks in priority order: {ordered_tasks}")

    for task_id in ordered_tasks:
        print(f"\n--- Running guardian task: {task_id} ---")
        try:
            if task_id == "workflow_health":
                result = _call_task("workflow_health", "run", manifest)
            elif task_id == "readme_refresh":
                result = _call_task("readme_refresh", "run", manifest)
            else:
                result = {
                    "task": task_id,
                    "status": "skipped",
                    "reason": "unknown_task"
                }
        except Exception as e:
            result = {
                "task": task_id,
                "status": "error",
                "error": str(e),
            }

        overall["tasks"].append(result)

    # Write JSON + Markdown summaries
    json_path = reports_dir / "guardian_run_latest.json"
    json_path.write_text(json.dumps(overall, indent=2), encoding="utf-8")

    md_path = reports_dir / f"guardian_run_{run_id}.md"
    lines: List[str] = [
        "# StegVerse Guardian Run",
        f"- Run ID: `{run_id}`",
        f"- Time (UTC): `{ts}`",
        "",
        "## Tasks",
    ]
    for t in overall["tasks"]:
        status = t.get("status", "unknown")
        name = t.get("task", "unknown")
        lines.append(f"- **{name}** — `{status}`")
        if "summary" in t:
            lines.append(f"  - {t['summary']}")
        if "error" in t:
            lines.append(f"  - Error: `{t['error']}`")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nGuardian report written to: {md_path}")


if __name__ == "__main__":
    main()
