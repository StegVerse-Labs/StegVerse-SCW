#!/usr/bin/env python
"""
StegVerse Guardian Actions (Genesis v0.1)

Reads:
  reports/guardians/guardian_run_latest.json

Produces:
  reports/guardians/guardian_actions.md

Goal:
  Turn guardian scan results into a simple, human-readable
  action plan that future AI entities and humans can follow.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]  # .../StegVerse-SCW
REPORT_DIR = ROOT / "reports" / "guardians"
LATEST_JSON = REPORT_DIR / "guardian_run_latest.json"
ACTIONS_MD = REPORT_DIR / "guardian_actions.md"


def load_latest_run() -> Dict[str, Any]:
    if not LATEST_JSON.exists():
        raise SystemExit(f"Latest guardian JSON not found: {LATEST_JSON}")
    with LATEST_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def summarize_readme_refresh(task: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    details = task.get("details") or {}
    present = details.get("readme_present") or []
    missing = details.get("readme_missing") or []

    lines.append("### README Refresh")
    lines.append(f"- Status: **{task.get('status', 'unknown')}**")
    lines.append(f"- Summary: {task.get('summary', '').strip() or '(no summary)'}")
    lines.append("")

    if present:
        lines.append("Readme already present in:")
        for p in sorted(present):
            lines.append(f"- `{p}`")
        lines.append("")

    if missing:
        lines.append("Readme missing in directories (high priority for docs workers):")
        for d in sorted(missing):
            lines.append(f"- `{d}`")
        lines.append("")
        lines.append("Suggested next actions:")
        lines.append("- [ ] Create minimal README.md in each missing directory.")
        lines.append("- [ ] For key folders (e.g., `scripts/genesis`, `ledger/telemetry`), add purpose, key scripts, and how to run checks.")
        lines.append("")

    return lines


def summarize_workflow_health(task: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    details = task.get("details") or {}
    wf_files = details.get("workflow_files") or []
    count = details.get("count", len(wf_files))

    lines.append("### Workflow Health")
    lines.append(f"- Status: **{task.get('status', 'unknown')}**")
    lines.append(f"- Summary: {task.get('summary', '').strip() or '(no summary)'}")
    lines.append("")
    lines.append(f"Detected **{count}** workflow file(s):")
    for name in sorted(wf_files):
        lines.append(f"- `{name}`")
    lines.append("")

    lines.append("Suggested next actions:")
    lines.append("- [ ] Confirm each workflow is visible in GitHub Actions UI and has a trigger (`workflow_dispatch`, `schedule`, or `push`).")
    lines.append("- [ ] Mark the highest-priority workflows for 24/7 uptime (to be guarded by future AI workers).")
    lines.append("")
    return lines


def main() -> int:
    print("=== StegVerse Guardian Actions (Genesis v0.1) ===")
    data = load_latest_run()

    run_id = data.get("run_id", "unknown")
    generated_at = data.get("generated_at", "unknown")
    tasks = data.get("tasks") or []

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("# StegVerse Guardian Action Plan")
    lines.append("")
    lines.append(f"- Based on guardian run: `{run_id}`")
    lines.append(f"- Generated at: `{generated_at}`")
    lines.append("")
    lines.append("This file is the **bridge** between guardian scans and future AI workers.")
    lines.append("Guardians detect issues; this plan shows what should be done next.")
    lines.append("")

    if not tasks:
        lines.append("_No tasks found in latest guardian run._")
    else:
        # Group tasks: warnings first, then ok, then others
        warnings: List[Dict[str, Any]] = []
        oks: List[Dict[str, Any]] = []
        others: List[Dict[str, Any]] = []

        for t in tasks:
            status = (t.get("status") or "").lower()
            if status in ("warning", "error"):
                warnings.append(t)
            elif status == "ok":
                oks.append(t)
            else:
                others.append(t)

        if warnings:
            lines.append("## High-priority findings (warnings / errors)")
            lines.append("")
            for t in warnings:
                tid = t.get("id", "unknown")
                if tid == "readme_refresh":
                    lines.extend(summarize_readme_refresh(t))
                elif tid == "workflow_health":
                    lines.extend(summarize_workflow_health(t))
                else:
                    lines.append(f"### `{tid}`")
                    lines.append(f"- Status: **{t.get('status', 'unknown')}**")
                    lines.append(f"- Summary: {t.get('summary', '').strip() or '(no summary)'}")
                    lines.append("")
            lines.append("")

        if oks:
            lines.append("## Healthy guardian checks")
            lines.append("")
            for t in oks:
                lines.append(f"- `{t.get('id', 'unknown')}` — **ok** — {t.get('summary', '').strip() or '(no summary)'}")
            lines.append("")

        if others:
            lines.append("## Other guardian results")
            lines.append("")
            for t in others:
                lines.append(f"- `{t.get('id', 'unknown')}` — status: **{t.get('status', 'unknown')}** — {t.get('summary', '').strip() or '(no summary)'}")
            lines.append("")

    ACTIONS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote guardian actions plan to: {ACTIONS_MD}")
    print("=== Guardian Actions completed. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
