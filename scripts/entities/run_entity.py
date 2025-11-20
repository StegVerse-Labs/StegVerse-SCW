from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))  # allow 'scripts.entities.*' imports

from entities.entity_models import get_entity  # type: ignore
from entities.task_graph import default_task_graph  # type: ignore
from entities.task_router import run_task  # type: ignore
from entities.memory_store import append_memory  # type: ignore

REPORTS_DIR = ROOT / "reports" / "entities"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run a StegVerse AI entity (Phase 2).")
    ap.add_argument("--entity", required=False, default="stegverse-ai-001")
    ap.add_argument("--tasks", nargs="*", help="Override tasks for this run.")
    args = ap.parse_args(argv)

    entity_id = args.entity
    entity = get_entity(entity_id)

    if not entity.enabled:
        print(f"Entity {entity.id} is disabled; exiting.")
        return 0

    selected_tasks = args.tasks if args.tasks else entity.tasks
    graph = default_task_graph()
    ordered = graph.linear_order(selected_tasks)

    run_id = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    heading = f"Run {run_id} for {entity.id}"
    log_lines = [f"Entity: {entity.id}", f"Tasks: {', '.join(ordered)}", ""]

    results: List[Dict[str, Any]] = []

    print(f"=== Running entity {entity.id} ({entity.name}) ===")
    print(f"Tasks: {ordered}")

    for tid in ordered:
        print(f"--- Running task: {tid} ---")
        res = run_task(tid)
        results.append(res)
        rc = res.get("return_code", 0)
        out = res.get("output", "")
        print(out)
        log_lines.append(f"### Task: {tid}")
        log_lines.append(f"- return_code: {rc}")
        log_lines.append("")
        log_lines.append("```")
        log_lines.append(out.strip())
        log_lines.append("```")
        log_lines.append("")

    # Write a run report
    report_path = REPORTS_DIR / f"{entity.id}-run-{run_id}.md"
    md = [
        f"# Entity Run Report",
        f"- entity: `{entity.id}`",
        f"- name: `{entity.name}`",
        f"- role: `{entity.role}`",
        f"- run_id: `{run_id}`",
        "",
        "## Tasks",
    ]
    for r in results:
        md.append(f"- `{r['task']}` → rc={r.get('return_code', 0)}")
    md.append("")
    md.append("## Details")
    md.extend(log_lines)

    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    # Append to entity memory
    append_memory(entity, heading=heading, body="\n".join(log_lines), kind="run")

    # Overall return code: nonzero if any task had nonzero rc
    overall_rc = 0
    for r in results:
        if int(r.get("return_code", 0)) != 0:
            overall_rc = 1
    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())