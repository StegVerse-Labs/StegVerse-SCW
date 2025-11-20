#!/usr/bin/env python
"""
StegVerse Guardian Runner (Genesis)

Reads guardian_registry.yaml, executes all enabled tasks in
priority order, and writes:

  - reports/guardians/guardian_run_<run_id>.md
  - reports/guardians/guardian_run_latest.json

This is the orchestration layer for "guardian" style AI entities.
"""

from __future__ import annotations

import json
import os
import sys
import datetime as _dt
from pathlib import Path
from typing import Any, Dict, List

import yaml  # Requires PyYAML (already used elsewhere in SCW)


# ---------------------------------------------------------------------------
# Paths & helpers
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]  # .../StegVerse-SCW
REGISTRY_PATH = ROOT / "scripts" / "genesis" / "guardian_registry.yaml"
REPORT_DIR = ROOT / "reports" / "guardians"


def _now_iso() -> str:
    return _dt.datetime.utcnow().isoformat() + "Z"


def _get_run_id() -> str:
    # Prefer the GitHub run ID if present so reports correlate with Actions
    rid = os.getenv("GITHUB_RUN_ID")
    if rid:
        return rid
    # Fallback: timestamp-based ID
    return _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")


# ---------------------------------------------------------------------------
# Task implementations (lightweight for Genesis v0.1)
# ---------------------------------------------------------------------------

def task_workflow_health(root: Path) -> Dict[str, Any]:
    """
    Scan .github/workflows for obvious issues:
      - Count workflows
      - List workflow files
      - Flag if the directory is missing
    """
    workflows_dir = root / ".github" / "workflows"
    result: Dict[str, Any] = {
        "id": "workflow_health",
        "status": "ok",
        "summary": "",
        "details": {},
    }

    if not workflows_dir.exists():
        result["status"] = "warning"
        result["summary"] = "No .github/workflows directory found."
        result["details"] = {}
        return result

    yml_files = list(workflows_dir.glob("*.yml"))
    yaml_files = list(workflows_dir.glob("*.yaml"))
    all_files = sorted(set(yml_files + yaml_files))

    result["details"]["workflow_files"] = [p.name for p in all_files]
    result["details"]["count"] = len(all_files)

    if not all_files:
        result["status"] = "warning"
        result["summary"] = "Workflows directory exists but contains no *.yml / *.yaml files."
    else:
        result["summary"] = f"Found {len(all_files)} workflow file(s)."

    return result


def task_readme_refresh(root: Path) -> Dict[str, Any]:
    """
    Scan a shallow set of directories for missing/weak README.md files.
    This is *analysis only* for now – actual AI README rewrites will
    come in a later phase.
    """
    result: Dict[str, Any] = {
        "id": "readme_refresh",
        "status": "ok",
        "summary": "",
        "details": {},
    }

    # Target a small, important set of top-level dirs for Genesis v0.1
    candidate_dirs = [
        root,
        root / "scripts",
        root / "scripts" / "genesis",
        root / "ledger",
        root / "ledger" / "telemetry",
        root / "reports",
    ]

    missing: List[str] = []
    present: List[str] = []

    for d in candidate_dirs:
        if not d.exists() or not d.is_dir():
            continue
        readme = d / "README.md"
        if readme.exists():
            present.append(str(readme.relative_to(root)))
        else:
            missing.append(str(d.relative_to(root)))

    result["details"]["readme_present"] = present
    result["details"]["readme_missing"] = missing

    if missing:
        result["status"] = "warning"
        result["summary"] = f"{len(missing)} directory(ies) are missing README.md files."
    else:
        result["summary"] = "All monitored directories have README.md files."

    return result


# Placeholder tasks for future expansion
def task_placeholder(task_id: str) -> Dict[str, Any]:
    return {
        "id": task_id,
        "status": "skipped",
        "summary": "Task is defined in registry but not implemented yet (placeholder).",
        "details": {},
    }


# Map registry IDs -> implementation functions
TASK_IMPLS = {
    "workflow_health": task_workflow_health,
    "readme_refresh": task_readme_refresh,
    # "dependency_doctor": <future>,
    # "site_readme_refresh": <future>,
}


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

def load_registry(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Guardian registry not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if "tasks" not in data or not isinstance(data["tasks"], list):
        raise SystemExit("guardian_registry.yaml is missing a 'tasks' list.")

    return data


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def write_reports(
    run_id: str,
    generated_at: str,
    registry: Dict[str, Any],
    task_results: List[Dict[str, Any]],
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Markdown report
    md_path = REPORT_DIR / f"guardian_run_{run_id}.md"
    latest_json_path = REPORT_DIR / "guardian_run_latest.json"

    lines: List[str] = []
    lines.append("# StegVerse Guardian Run Report")
    lines.append("")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append(f"- Generated at: `{generated_at}`")
    lines.append("")
    lines.append("## Tasks")
    lines.append("")

    for r in task_results:
        tid = r.get("id", "unknown")
        status = r.get("status", "unknown")
        summary = r.get("summary", "").strip() or "(no summary)"

        lines.append(f"### `{tid}`")
        lines.append(f"- Status: **{status}**")
        lines.append(f"- Summary: {summary}")
        details = r.get("details") or {}
        if details:
            lines.append("")
            lines.append("<details><summary>Details</summary>")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(details, indent=2, sort_keys=True))
            lines.append("```")
            lines.append("</details>")
        lines.append("")

    with md_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # JSON summary (for future automation / guardian_actions)
    payload = {
        "run_id": run_id,
        "generated_at": generated_at,
        "registry": registry,
        "tasks": task_results,
    }
    with latest_json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main(argv: List[str] | None = None) -> int:
    print("=== StegVerse Guardian Runner (Genesis v0.1) ===")
    print(f"ROOT: {ROOT}")
    print(f"Registry: {REGISTRY_PATH}")

    registry = load_registry(REGISTRY_PATH)
    tasks_cfg = registry.get("tasks", [])

    # Filter to enabled tasks and sort by priority (desc)
    enabled_tasks = [
        t for t in tasks_cfg
        if t.get("enabled", False)
    ]
    enabled_tasks.sort(key=lambda t: int(t.get("priority", 0)), reverse=True)

    print("Enabled guardian tasks (in priority order):")
    for t in enabled_tasks:
        print(f"  - {t['id']} (priority={t.get('priority')})")

    run_id = _get_run_id()
    generated_at = _now_iso()

    results: List[Dict[str, Any]] = []

    for task in enabled_tasks:
        tid = task.get("id")
        print(f"--- Running guardian task: {tid} ---")

        impl = TASK_IMPLS.get(tid)
        if impl is None:
            res = task_placeholder(tid)
        else:
            res = impl(ROOT)

        results.append(res)

    write_reports(run_id, generated_at, registry, results)

    print(f"Guardian report written to: {REPORT_DIR}/guardian_run_{run_id}.md")
    print(f"Latest JSON summary updated: {REPORT_DIR}/guardian_run_latest.json")
    print("=== Guardian Runner completed. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
