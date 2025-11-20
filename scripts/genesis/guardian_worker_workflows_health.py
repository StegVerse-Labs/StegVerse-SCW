#!/usr/bin/env python
"""
StegVerse Genesis Guardian Worker – Workflow Health

Scans .github/workflows for:
- YAML parse errors
- Missing "name" or "on" keys
- Basic stats (counts, etc.)

Outputs a markdown report under:
  scripts/reports/guardians/workflow_health_YYYY-MM-DD.md

This worker is intentionally conservative: it ONLY writes reports,
it does not modify any workflows.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

import yaml  # type: ignore


ROOT = Path(".")
WORKFLOW_DIR = ROOT / ".github" / "workflows"
REPORT_DIR = ROOT / "scripts" / "reports" / "guardians"


@dataclass
class WorkflowIssue:
    file: str
    kind: str
    detail: str


@dataclass
class WorkflowHealthSummary:
    files_scanned: int = 0
    parse_errors: int = 0
    missing_name: int = 0
    missing_on: int = 0
    issues: List[WorkflowIssue] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def scan_workflows() -> WorkflowHealthSummary:
    summary = WorkflowHealthSummary()
    if not WORKFLOW_DIR.exists():
        return summary

    for wf_path in sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(
        WORKFLOW_DIR.glob("*.yaml")
    ):
        summary.files_scanned += 1
        rel = wf_path.relative_to(ROOT).as_posix()

        try:
            data = _load_yaml(wf_path)
        except Exception as exc:  # noqa: BLE001
            summary.parse_errors += 1
            summary.issues.append(
                WorkflowIssue(
                    file=rel,
                    kind="parse_error",
                    detail=f"{type(exc).__name__}: {exc}",
                )
            )
            continue

        # Basic shape checks
        if "name" not in data:
            summary.missing_name += 1
            summary.issues.append(
                WorkflowIssue(
                    file=rel,
                    kind="missing_name",
                    detail='Workflow file is missing top-level "name" key.',
                )
            )

        if "on" not in data:
            summary.missing_on += 1
            summary.issues.append(
                WorkflowIssue(
                    file=rel,
                    kind="missing_on",
                    detail='Workflow file is missing top-level "on" trigger block.',
                )
            )

    return summary


def _ensure_report_dir() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _format_markdown(summary: WorkflowHealthSummary, run_id: str) -> str:
    now = _dt.datetime.utcnow().isoformat() + "Z"
    lines: List[str] = []

    lines.append("# StegVerse Workflow Health Report")
    lines.append("")
    lines.append(f"- Generated at: `{now}`")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Workflow files scanned: **{summary.files_scanned}**")
    lines.append(f"- YAML parse errors: **{summary.parse_errors}**")
    lines.append(f"- Missing `name`: **{summary.missing_name}**")
    lines.append(f"- Missing `on`: **{summary.missing_on}**")
    lines.append("")

    if summary.issues:
        lines.append("## Detected Issues")
        lines.append("")
        for issue in summary.issues:
            lines.append(
                f"- `{issue.file}` — **{issue.kind}** — {issue.detail}"
            )
        lines.append("")
    else:
        lines.append("## Detected Issues")
        lines.append("")
        lines.append("No workflow issues detected. ✅")
        lines.append("")

    # Optional: dump a small machine-readable appendix
    lines.append("## Raw Summary (debug)")
    lines.append("")
    payload = asdict(summary)
    # remove issues detail to keep it short
    payload = {
        k: v
        for k, v in payload.items()
        if k != "issues"
    }
    lines.append("```json")
    import json as _json  # local import to avoid unused in stub

    lines.append(_json.dumps(payload, indent=2, sort_keys=True))
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def write_report(summary: WorkflowHealthSummary) -> Path:
    _ensure_report_dir()
    today = _dt.datetime.utcnow().strftime("%Y-%m-%d")
    run_id = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    report_path = REPORT_DIR / f"workflow_health_{today}.md"
    latest_path = REPORT_DIR / "workflow_health_latest.md"

    md = _format_markdown(summary, run_id=run_id)
    report_path.write_text(md, encoding="utf-8")
    latest_path.write_text(md, encoding="utf-8")

    return report_path


def main() -> None:
    print("=== StegVerse Workflow Health Guardian ===")
    print(f"Scanning workflows under: {WORKFLOW_DIR}")

    summary = scan_workflows()
    report_path = write_report(summary)

    print("Workflow health summary:")
    print(f"  files_scanned  : {summary.files_scanned}")
    print(f"  parse_errors   : {summary.parse_errors}")
    print(f"  missing_name   : {summary.missing_name}")
    print(f"  missing_on     : {summary.missing_on}")
    print(f"Report written to: {report_path.as_posix()}")
    print("=== Workflow Health Guardian complete. ===")


if __name__ == "__main__":
    main()
