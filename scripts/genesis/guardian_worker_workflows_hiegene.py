#!/usr/bin/env python
"""
StegVerse Guardian Worker: Workflow Hygiene (ASL-2)

Goals:
  - Respect Automation Safety Levels (ASL) config.
  - Keep GitHub Actions workflows "human-friendly":
      * Ensure each workflow has a `workflow_dispatch` trigger so you always
        have a "Run workflow" button available from the UI.
  - Operate only on `.github/workflows/*.yml*` inside StegVerse-SCW.

Reads:
  - docs/governance/automation_safety_levels.yaml
  - reports/guardians/guardian_run_latest.json (optional; not required)

Writes:
  - Updates .github/workflows/*.yml* in place (only if ASL allows).

Safety:
  - Only runs if task `workflow_hygiene` is ASL-2 or lower.
  - Never touches code outside `.github/workflows`.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml  # Used only to confirm file is valid YAML; we modify as text.
except Exception:
    yaml = None


ROOT = Path(__file__).resolve().parents[2]  # .../StegVerse-SCW
ASL_CONFIG = ROOT / "docs" / "governance" / "automation_safety_levels.yaml"
LATEST_JSON = ROOT / "reports" / "guardians" / "guardian_run_latest.json"
WF_DIR = ROOT / ".github" / "workflows"


# ---------------- ASL helpers ----------------

def load_asl_config() -> Dict[str, Any]:
    if not ASL_CONFIG.exists():
        print(f"[ASL] Config not found at {ASL_CONFIG}; refusing to change workflows.")
        return {}
    if yaml is None:
        print("[ASL] PyYAML not available; refusing to change workflows.")
        return {}
    with ASL_CONFIG.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_task_asl(cfg: Dict[str, Any], task_id: str) -> str:
    tasks = (cfg.get("tasks") or {})
    t = tasks.get(task_id) or {}
    return t.get("level") or ""


def is_asl_at_most(asl: str, limit: str) -> bool:
    order = ["ASL-1", "ASL-2", "ASL-3", "ASL-4", "ASL-5"]
    if asl not in order or limit not in order:
        return False
    return order.index(asl) <= order.index(limit)


# ---------------- Utility helpers ----------------

def load_latest_run() -> Dict[str, Any]:
    if not LATEST_JSON.exists():
        print("[Guardians] No latest guardian run file; proceeding with generic hygiene.")
        return {}
    try:
        with LATEST_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Guardians] Could not parse latest guardian JSON: {e}")
        return {}


def list_workflow_files() -> List[Path]:
    if not WF_DIR.exists():
        print(f"[WF] No workflows directory at {WF_DIR}")
        return []
    files: List[Path] = []
    for p in sorted(WF_DIR.glob("*.yml")) + sorted(WF_DIR.glob("*.yaml")):
        if p.is_file():
            files.append(p)
    return files


def has_workflow_dispatch(txt: str) -> bool:
    # Very simple check: any line that mentions workflow_dispatch:
    return bool(re.search(r'^\s*workflow_dispatch\s*:', txt, flags=re.M))


def ensure_workflow_dispatch(txt: str) -> Tuple[str, bool]:
    """
    Make sure there is a `workflow_dispatch` trigger under `on:`.
    Returns (new_text, changed?).
    """
    if has_workflow_dispatch(txt):
        return txt, False

    # Look for a plain 'on:' line
    pattern_plain_on = re.compile(r'^on:\s*$', flags=re.M)
    m_plain = pattern_plain_on.search(txt)
    if m_plain:
        insert_at = m_plain.end()
        snippet = "\n  workflow_dispatch: {}\n"
        return txt[:insert_at] + snippet + txt[insert_at:], True

    # Look for 'on:' followed by newline (e.g., 'on:\n  push: ...')
    pattern_on_block = re.compile(r'on:\s*\n', flags=re.M)
    m_block = pattern_on_block.search(txt)
    if m_block:
        insert_at = m_block.end()
        snippet = "  workflow_dispatch: {}\n"
        return txt[:insert_at] + snippet + txt[insert_at:], True

    # If no 'on:' at all, prepend a minimal block
    snippet = "on:\n  workflow_dispatch: {}\n\n"
    return snippet + txt, True


def validate_yaml(text: str, path: Path) -> bool:
    """
    Try to parse the resulting YAML to avoid writing broken workflows.
    If PyYAML is unavailable, we skip validation but still proceed.
    """
    if yaml is None:
        return True
    try:
        yaml.safe_load(text)
        return True
    except Exception as e:
        print(f"[YAML] WARNING: validation failed for {path}: {e}")
        return False


# ---------------- Main worker logic ----------------

def main() -> int:
    print("=== StegVerse Guardian Worker: Workflow Hygiene (ASL-2) ===")

    # 1) ASL check
    asl_cfg = load_asl_config()
    task_id = "workflow_hygiene"
    task_asl = get_task_asl(asl_cfg, task_id)

    if not task_asl:
        print(f"[ASL] No ASL level configured for task '{task_id}'.")
        print("[ASL] Refusing to change workflows (safe mode).")
        return 0

    print(f"[ASL] Task '{task_id}' is configured as {task_asl}")
    if not is_asl_at_most(task_asl, "ASL-2"):
        print("[ASL] This task is above ASL-2; refusing to change workflows.")
        return 0

    # 2) Load guardian run (optional, mainly for future refinements)
    run_data = load_latest_run()
    _ = run_data  # placeholder; we can later restrict which workflows to touch

    # 3) Process workflow files
    workflows = list_workflow_files()
    if not workflows:
        print("[WF] No workflow files found; nothing to do.")
        return 0

    changed = 0
    skipped_invalid = 0

    for wf in workflows:
        text = wf.read_text(encoding="utf-8", errors="ignore")

        new_text, did_change = ensure_workflow_dispatch(text)
        if not did_change:
            print(f"- {wf.name}: already has workflow_dispatch; OK.")
            continue

        # Validate YAML before writing
        if not validate_yaml(new_text, wf):
            print(f"  ❌ Skipping write for {wf.name} (YAML invalid after edit).")
            skipped_invalid += 1
            continue

        wf.write_text(new_text, encoding="utf-8")
        changed += 1
        print(f"  ✅ Added workflow_dispatch to {wf.name}")

    print("")
    print("Summary:")
    print(f"- Workflows scanned: {len(workflows)}")
    print(f"- Updated (added workflow_dispatch): {changed}")
    print(f"- Skipped (post-edit YAML invalid): {skipped_invalid}")
    print("=== Workflow Hygiene worker complete. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
