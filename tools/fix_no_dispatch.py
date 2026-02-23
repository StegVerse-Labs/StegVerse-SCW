#!/usr/bin/env python3
"""
Fix missing workflow_dispatch in .github/workflows/*.yml|*.yaml (SCW repo).

- Reads YAML safely (best effort).
- Ensures `on: workflow_dispatch:` exists.
- Writes patchlog JSONL + summary JSON for auditability.

Usage:
  python tools/fix_no_dispatch.py --root . --apply
  python tools/fix_no_dispatch.py --root .          (dry run)

Outputs:
  reports/guardians/patchlogs/no_dispatch_patchlog.jsonl
  reports/guardians/patchlogs/no_dispatch_summary.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_yaml(path: Path) -> Tuple[bool, Any, str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as e:
        return False, None, f"read_error: {e}"
    try:
        data = yaml.safe_load(raw)
        return True, data, ""
    except Exception as e:
        return False, None, f"yaml_parse_error: {e}"


def dump_yaml(data: Any) -> str:
    # Preserve reasonably readable output; this may reformat YAML.
    return yaml.safe_dump(data, sort_keys=False)


def normalize_on(on_val: Any) -> Dict[str, Any]:
    """
    Normalize the `on` section into a mapping.
    - If `on` is a string like "push" => {"push": {}}
    - If it's a list => {event: {}}
    - If it's a dict => itself
    """
    if on_val is None:
        return {}
    if isinstance(on_val, str):
        return {on_val: {}}
    if isinstance(on_val, list):
        out: Dict[str, Any] = {}
        for e in on_val:
            if isinstance(e, str):
                out[e] = {}
        return out
    if isinstance(on_val, dict):
        return dict(on_val)
    return {}


def ensure_workflow_dispatch(doc: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Returns (changed, note).
    """
    if not isinstance(doc, dict):
        return False, "not_a_mapping"

    on_map = normalize_on(doc.get("on"))
    if "workflow_dispatch" in on_map:
        return False, "already_has_workflow_dispatch"

    on_map["workflow_dispatch"] = {}
    doc["on"] = on_map
    return True, "added_workflow_dispatch"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true", help="Write changes to disk.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    workflows_dir = root / ".github" / "workflows"
    out_dir = root / "reports" / "guardians" / "patchlogs"
    out_dir.mkdir(parents=True, exist_ok=True)

    patchlog_path = out_dir / "no_dispatch_patchlog.jsonl"
    summary_path = out_dir / "no_dispatch_summary.json"

    run_at = now_utc()
    records: List[Dict[str, Any]] = []

    if not workflows_dir.exists():
        summary = {
            "generated_at_utc": run_at,
            "status": "warning",
            "reason": "missing_workflows_dir",
            "workflows_dir": str(workflows_dir),
            "apply": bool(args.apply),
            "changed": 0,
            "scanned": 0,
        }
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return 3

    workflow_files = sorted(list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml")))
    changed = 0
    scanned = 0
    parse_errors = 0

    for wf in workflow_files:
        scanned += 1
        ok, doc, err = load_yaml(wf)
        if not ok:
            parse_errors += 1
            records.append({
                "ts_utc": run_at,
                "file": str(wf.relative_to(root)).replace("\\", "/"),
                "action": "skip",
                "reason": err,
            })
            continue

        chg, note = ensure_workflow_dispatch(doc)
        if chg:
            changed += 1
            if args.apply:
                wf.write_text(dump_yaml(doc), encoding="utf-8")
            records.append({
                "ts_utc": run_at,
                "file": str(wf.relative_to(root)).replace("\\", "/"),
                "action": "modify" if args.apply else "plan",
                "reason": note,
            })
        else:
            records.append({
                "ts_utc": run_at,
                "file": str(wf.relative_to(root)).replace("\\", "/"),
                "action": "noop",
                "reason": note,
            })

    with patchlog_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    summary = {
        "generated_at_utc": run_at,
        "status": "ok" if parse_errors == 0 else "warning",
        "apply": bool(args.apply),
        "scanned": scanned,
        "changed": changed,
        "parse_errors": parse_errors,
        "patchlog": str(patchlog_path.relative_to(root)).replace("\\", "/"),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Non-zero exit if parse errors exist (so SCW can surface it)
    return 0 if parse_errors == 0 else 4


if __name__ == "__main__":
    raise SystemExit(main())
