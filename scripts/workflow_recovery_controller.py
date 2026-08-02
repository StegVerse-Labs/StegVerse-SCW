#!/usr/bin/env python3
"""Read-only controller for SCW workflow recovery.

Produces deterministic JSON and Markdown receipts, classifies workflow files,
checks required components, detects duplicate content, and selects the next
executable task. It never mutates repository files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import yaml


class GitHubLoader(yaml.SafeLoader):
    pass


for first_char, resolvers in list(GitHubLoader.yaml_implicit_resolvers.items()):
    GitHubLoader.yaml_implicit_resolvers[first_char] = [
        item for item in resolvers if item[0] != "tag:yaml.org,2002:bool"
    ]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def inspect_yaml(path: pathlib.Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    record: dict[str, Any] = {
        "path": path.as_posix(),
        "bytes": len(text.encode("utf-8")),
        "lines": len(text.splitlines()),
        "sha256": sha256_text(text),
        "parse_valid": False,
        "workflow_dispatch": False,
        "workflow_call": False,
        "scheduled": False,
        "classification": "FAILED",
        "error": None,
    }
    try:
        data = yaml.load(text, Loader=GitHubLoader)
        if not isinstance(data, dict):
            raise ValueError("top-level YAML value is not a mapping")
        events = data.get("on", {})
        if isinstance(events, str):
            event_names = {events}
        elif isinstance(events, list):
            event_names = {str(item) for item in events}
        elif isinstance(events, dict):
            event_names = {str(item) for item in events.keys()}
        else:
            event_names = set()
        record.update(
            parse_valid=True,
            workflow_dispatch="workflow_dispatch" in event_names,
            workflow_call="workflow_call" in event_names,
            scheduled="schedule" in event_names,
            classification="COMPLETE",
        )
    except Exception as exc:  # report exact parser boundary
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def choose_next(required: list[dict[str, Any]], invalid: list[dict[str, Any]]) -> dict[str, str]:
    missing = [item for item in required if not item["exists"]]
    if missing:
        return {"status": "BLOCKED", "task": "install_missing_required_component", "target": missing[0]["path"]}
    required_invalid = [item for item in required if item.get("parse_valid") is False]
    if required_invalid:
        return {"status": "REVIEW_REQUIRED", "task": "repair_required_workflow", "target": required_invalid[0]["path"]}
    if invalid:
        return {"status": "REVIEW_REQUIRED", "task": "review_invalid_workflow", "target": invalid[0]["path"]}
    return {"status": "COMPLETE", "task": "inspect_hosted_validation_receipts", "target": ".github/workflows/workflows-sanity-check.yml"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", default="config/workflow-recovery-required.json")
    parser.add_argument("--out", default="self_healing_out/workflow-recovery")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    config = load_json(root / args.config)
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)

    workflow_root = root / ".github" / "workflows"
    workflow_paths = sorted(workflow_root.rglob("*.yml")) + sorted(workflow_root.rglob("*.yaml"))
    records = [inspect_yaml(path) for path in workflow_paths]
    by_path = {item["path"]: item for item in records}

    required: list[dict[str, Any]] = []
    for component in config["required_components"]:
        rel = component["path"]
        target = root / rel
        item: dict[str, Any] = {**component, "exists": target.is_file()}
        if target.is_file() and rel.startswith(".github/workflows/"):
            item.update(by_path.get(target.as_posix(), inspect_yaml(target)))
        required.append(item)

    hash_groups: dict[str, list[str]] = defaultdict(list)
    for item in records:
        hash_groups[item["sha256"]].append(item["path"])
    duplicates = [paths for paths in hash_groups.values() if len(paths) > 1]
    invalid = [item for item in records if not item["parse_valid"]]
    dispatchable = [item for item in records if item["workflow_dispatch"]]
    nested = [item for item in records if pathlib.Path(item["path"]).parent != workflow_root]
    next_task = choose_next(required, invalid)

    missing_required = sum(1 for item in required if not item["exists"])
    invalid_required = sum(1 for item in required if item.get("parse_valid") is False)
    if missing_required:
        overall = "BLOCKED"
    elif invalid_required or invalid:
        overall = "REVIEW_REQUIRED"
    else:
        overall = "COMPLETE"

    receipt = {
        "schema_version": "1.0",
        "goal_id": config["goal_id"],
        "owner_repository": config["owner_repository"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": overall,
        "summary": {
            "workflow_files": len(records),
            "parse_valid": len(records) - len(invalid),
            "parse_invalid": len(invalid),
            "dispatchable": len(dispatchable),
            "nested_workflow_files": len(nested),
            "duplicate_content_groups": len(duplicates),
            "required_components": len(required),
            "missing_required": missing_required,
            "invalid_required": invalid_required,
        },
        "next_task": next_task,
        "required_components": required,
        "invalid_workflows": invalid,
        "nested_workflows": nested,
        "duplicate_content_groups": duplicates,
        "workflows": records,
    }

    json_path = out / "WORKFLOW_RECOVERY_RECEIPT.json"
    md_path = out / "WORKFLOW_RECOVERY_RECEIPT.md"
    json_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Workflow Recovery Receipt",
        "",
        f"- Goal: `{receipt['goal_id']}`",
        f"- Status: **{overall}**",
        f"- Workflow files: **{len(records)}**",
        f"- Parse-valid: **{len(records) - len(invalid)}**",
        f"- Parse-invalid: **{len(invalid)}**",
        f"- Required missing: **{missing_required}**",
        f"- Required invalid: **{invalid_required}**",
        f"- Next task: `{next_task['task']}` at `{next_task['target']}`",
        "",
        "## Invalid workflows",
    ]
    lines.extend([f"- `{item['path']}` — {item['error']}" for item in invalid] or ["- None"])
    lines += ["", "## Duplicate content groups"]
    lines.extend(["- " + ", ".join(f"`{path}`" for path in group) for group in duplicates] or ["- None"])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(receipt["summary"], sort_keys=True))
    print(f"status={overall}")
    print(f"next_task={next_task['task']}::{next_task['target']}")
    return 0 if overall == "COMPLETE" else 2


if __name__ == "__main__":
    sys.exit(main())
