#!/usr/bin/env python3
"""
Genesis Worker Kernel v0.1

This is a lightweight, dry-run worker engine:
- Reads lanes + workers from config/genesis_core.yaml
- Prints what would run, in priority order
- Does NOT call external APIs or bill anything yet
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
GENESIS_CONFIG = CONFIG_DIR / "genesis_core.yaml"
REPORTS_DIR = ROOT / "reports" / "genesis"


def load_yaml(path: Path):
    import yaml
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@dataclass
class WorkerPlan:
    lane_id: str
    lane_priority: float
    worker_name: str
    enabled: bool


def build_worker_plan(genesis_cfg: Dict) -> List[WorkerPlan]:
    lanes = genesis_cfg.get("lanes", {})
    plan: List[WorkerPlan] = []

    for lane_name, lane_cfg in lanes.items():
        if not lane_cfg.get("enabled", True):
            continue
        priority = float(lane_cfg.get("priority", 0.5))
        workers = lane_cfg.get("workers", [])
        for w in workers:
            plan.append(
                WorkerPlan(
                    lane_id=lane_name,
                    lane_priority=priority,
                    worker_name=w,
                    enabled=True,
                )
            )

    # higher priority first, then sort by worker name
    plan.sort(key=lambda w: (-w.lane_priority, w.worker_name))
    return plan


def write_plan_report(plan: List[WorkerPlan]):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = REPORTS_DIR / f"worker_plan_{ts}.md"

    lines = [
        "# Genesis Worker Plan (Dry-Run)",
        f"- Run: `{datetime.utcnow().isoformat()}Z`",
        "",
        "## Planned Workers (highest priority first)",
        "",
    ]
    for p in plan:
        lines.append(
            f"- Lane `{p.lane_id}` (priority {p.lane_priority}) → worker `{p.worker_name}`"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[worker_kernel] Wrote worker plan report: {path}")


def main():
    print("=== StegVerse Genesis Worker Kernel v0.1 ===")
    cfg = load_yaml(GENESIS_CONFIG)

    plan = build_worker_plan(cfg)
    print(json.dumps(
        [
            {
                "lane": p.lane_id,
                "priority": p.lane_priority,
                "worker": p.worker_name,
            }
            for p in plan
        ],
        indent=2,
    ))
    write_plan_report(plan)
    print("=== Worker Kernel completed (dry-run; no workers actually executed). ===")


if __name__ == "__main__":
    main()
