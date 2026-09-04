#!/usr/bin/env python3
"""StegVerse Guardian Worker — Repo Alignment Check (ASL-1).

The checker is deliberately credential-free. It never contacts GitHub and never
accepts PAT/GITHUB_TOKEN style credentials. Repository source must already be
materialized by an admitted source-read capability and described by a
secret-free manifest that binds each target to an exact source SHA and receipt
reference.

This program only evaluates those local snapshots and writes reports. It grants
no source-read, mutation, publication, release, runtime, or credential authority.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CFG = ROOT / "docs" / "governance" / "repo_alignment_expectations.yaml"
DEFAULT_OUT = ROOT / "reports" / "guardians"
MANIFEST_SCHEMA = "stegverse.scw.repo-alignment-materialization/v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_MANIFEST_KEYS = {
    "token",
    "secret",
    "credential",
    "password",
    "pat",
    "github_token",
    "gh_token",
}


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing config: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("config must be a mapping")
    return data


def _reject_secret_fields(value: Any, where: str = "manifest") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_MANIFEST_KEYS or normalized.endswith("_token"):
                raise ValueError(f"secret-bearing field prohibited at {where}.{key}")
            _reject_secret_fields(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_secret_fields(child, f"{where}[{index}]")


def load_materialization_manifest(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"missing materialization manifest: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"materialization manifest schema must be {MANIFEST_SCHEMA}")
    _reject_secret_fields(data)

    entries = data.get("targets")
    if not isinstance(entries, list) or not entries:
        raise ValueError("materialization manifest targets must be a non-empty list")

    by_repo: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("materialization target must be an object")
        repo = entry.get("repo")
        source_sha = entry.get("source_sha")
        source_root = entry.get("path")
        receipt_ref = entry.get("receipt_ref")
        authority = entry.get("authority")
        if not isinstance(repo, str) or "/" not in repo:
            raise ValueError("materialization target repo must be owner/name")
        if repo in by_repo:
            raise ValueError(f"duplicate materialization target: {repo}")
        if not isinstance(source_sha, str) or not SHA_RE.fullmatch(source_sha):
            raise ValueError(f"{repo}: source_sha must be a lowercase 40-hex commit")
        if not isinstance(source_root, str) or not source_root.strip():
            raise ValueError(f"{repo}: path is required")
        if not isinstance(receipt_ref, str) or not receipt_ref.strip():
            raise ValueError(f"{repo}: receipt_ref is required")
        if authority != "TV/TVC":
            raise ValueError(f"{repo}: authority must be TV/TVC")

        root = Path(source_root)
        if not root.is_absolute():
            root = (path.parent / root).resolve()
        else:
            root = root.resolve()
        if not root.is_dir():
            raise ValueError(f"{repo}: materialized path does not exist: {root}")

        normalized = dict(entry)
        normalized["resolved_path"] = str(root)
        by_repo[repo] = normalized
    return by_repo


def list_workflows(repo_root: Path) -> Tuple[List[str], str]:
    workflow_root = repo_root / ".github" / "workflows"
    if not workflow_root.exists():
        return [], "missing"
    if not workflow_root.is_dir():
        return [], "not_directory"
    paths = [
        str(path.relative_to(repo_root)).replace(os.sep, "/")
        for path in workflow_root.iterdir()
        if path.is_file()
    ]
    return sorted(paths), "ok"


def has_workflow_dispatch(path: Path) -> bool:
    try:
        return "workflow_dispatch" in path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False


def evaluate_repo(
    full_repo: str,
    materialized: Dict[str, Any],
    required_files: List[str],
    required_workflows: List[str],
    ensure_dispatch: bool,
) -> Dict[str, Any]:
    repo_root = Path(materialized["resolved_path"])
    entry: Dict[str, Any] = {
        "repo": full_repo,
        "source_sha": materialized["source_sha"],
        "materialization_receipt_ref": materialized["receipt_ref"],
        "status": "unknown",
        "required_files": {},
        "required_workflows": {},
        "optional": {},
        "notes": [],
    }

    files_ok = True
    for relative in required_files:
        present = (repo_root / relative).is_file()
        entry["required_files"][relative] = {
            "ok": present,
            "msg": "present" if present else "missing",
        }
        files_ok = files_ok and present

    workflow_paths, workflow_state = list_workflows(repo_root)
    workflows_ok = workflow_state == "ok"
    if workflow_state != "ok":
        entry["notes"].append(f"workflow_list:{workflow_state}")
    workflow_set = set(workflow_paths)
    for relative in required_workflows:
        present = relative in workflow_set
        entry["required_workflows"][relative] = {
            "ok": present,
            "msg": "present" if present else "missing",
        }
        workflows_ok = workflows_ok and present

    if ensure_dispatch and workflow_state == "ok":
        missing_dispatch = [
            relative
            for relative in workflow_paths
            if not has_workflow_dispatch(repo_root / relative)
        ]
        entry["optional"]["workflow_dispatch_missing_in"] = missing_dispatch

    entry["status"] = "pass" if files_ok and workflows_ok else "fail"
    return entry


def render_markdown(payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# StegVerse Repo Alignment Report",
        "",
        f"- Run: {summary['ts_utc']}",
        f"- RID: `{summary['rid']}`",
        "- Input mode: credential-free exact materialized snapshots",
        "",
        "## Summary",
        f"- Total repos: **{summary['repos_total']}**",
        f"- Pass: **{summary['repos_pass']}**",
        f"- Fail: **{summary['repos_fail']}**",
        "",
        "## Per-repo results",
        "",
    ]
    for result in payload["results"]:
        badge = "✅" if result["status"] == "pass" else "❌"
        lines.extend(
            [
                f"### {badge} {result['repo']}",
                "",
                f"- Source SHA: `{result['source_sha']}`",
                f"- Materialization receipt: `{result['materialization_receipt_ref']}`",
                "",
                "**Required files:**",
            ]
        )
        for relative, state in result["required_files"].items():
            marker = "✅" if state["ok"] else "❌"
            lines.append(f"- {marker} `{relative}` — {state['msg']}")
        lines.extend(["", "**Required workflows:**"])
        if result["required_workflows"]:
            for relative, state in result["required_workflows"].items():
                marker = "✅" if state["ok"] else "❌"
                lines.append(f"- {marker} `{relative}` — {state['msg']}")
        else:
            lines.append("- none declared")
        lines.append("")
        optional = result.get("optional") or {}
        if "workflow_dispatch_missing_in" in optional:
            missing = optional["workflow_dispatch_missing_in"]
            if missing:
                lines.append("**Optional:** workflow_dispatch missing in:")
                lines.extend(f"- ⚠️ `{relative}`" for relative in missing)
            else:
                lines.append("**Optional:** workflow_dispatch present in all workflows.")
            lines.append("")
        if result["notes"]:
            lines.append("**Notes:**")
            lines.extend(f"- {note}" for note in result["notes"])
            lines.append("")
    return "\n".join(lines)


def run(config_path: Path, manifest_path: Path, out_dir: Path) -> Dict[str, Any]:
    config = load_yaml(config_path)
    materialized = load_materialization_manifest(manifest_path)
    targets = config.get("targets") or []
    required_files = config.get("required_files") or []
    required_workflows = config.get("required_workflows") or []
    ensure_dispatch = bool((config.get("optional_checks") or {}).get("ensure_workflow_dispatch"))

    configured_repos = [target.get("repo") for target in targets if isinstance(target, dict)]
    missing = [repo for repo in configured_repos if repo not in materialized]
    extra = [repo for repo in materialized if repo not in configured_repos]
    if missing:
        raise ValueError(f"materialization manifest missing configured targets: {', '.join(missing)}")
    if extra:
        raise ValueError(f"materialization manifest contains undeclared targets: {', '.join(extra)}")

    results = [
        evaluate_repo(
            repo,
            materialized[repo],
            required_files,
            required_workflows,
            ensure_dispatch,
        )
        for repo in configured_repos
    ]
    summary = {
        "repos_total": len(results),
        "repos_pass": sum(result["status"] == "pass" for result in results),
        "repos_fail": sum(result["status"] == "fail" for result in results),
        "repos_error": 0,
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rid": os.getenv("STEGVERSE_EXECUTION_ID", "local"),
        "materialization_manifest_schema": MANIFEST_SCHEMA,
    }
    payload = {"summary": summary, "results": results}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "repo_alignment_latest.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "repo_alignment_latest.md").write_text(
        render_markdown(payload) + "\n", encoding="utf-8"
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CFG)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = run(args.config, args.manifest, args.out_dir)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"BLOCKED_DEPENDENCY: {exc}")
        return 2
    print(json.dumps(payload["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
