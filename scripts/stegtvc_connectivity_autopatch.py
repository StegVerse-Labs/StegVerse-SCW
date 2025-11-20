#!/usr/bin/env python3
"""
StegTVC Connectivity Autopatch
- Uses StegVerse-Labs/TVC as the source of truth for connectivity files.
- Copies connectivity files into target StegVerse-Labs repos.
- Commits and pushes changes when needed.
- Writes a markdown report into reports/stegtvc_connectivity_autopatch_report.md in StegVerse-SCW.
"""

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
REPORTS = ROOT / "reports"
WORK.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)


def run(cmd, cwd=None, check=True) -> subprocess.CompletedProcess:
    """Run a command and echo it; raise on failure if check=True."""
    print("+", " ".join(cmd))
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(cmd)}")
    return result


def safe_name(repo: str) -> str:
    return repo.replace("/", "__").replace(".", "_")


def load_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Manifest not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_report(task: str, summary: Dict[str, Any], items: list) -> None:
    """Write a markdown report to reports/stegtvc_connectivity_autopatch_report.md"""
    report_path = REPORTS / "stegtvc_connectivity_autopatch_report.md"
    lines = []
    lines.append("# StegTVC Connectivity Autopatch Report")
    lines.append("")
    lines.append(f"- Run: {os.getenv('GITHUB_RUN_ID', 'local')}")
    lines.append(f"- Task: `{task}`")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total repos: **{summary['total_repos']}**")
    lines.append(f"- Updated: **{summary['updated']}**")
    lines.append(f"- No changes: **{summary['no_changes']}**")
    lines.append(f"- Clone failed: **{summary['clone_failed']}**")
    lines.append(f"- Errors: **{summary['error']}**")
    lines.append("")
    lines.append("## Per-repo results")
    for item in items:
        icon = "ℹ️"
        if item["status"] == "updated":
            icon = "✅"
        elif item["status"] in ("clone_failed", "error"):
            icon = "⚠️"
        lines.append(f"- {icon} `{item['repo']}` — {item['status']} — {item['message']}")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote connectivity report to {report_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to StegTVC connectivity manifest JSON")
    ap.add_argument("--task", default="manual", help="Optional task label for the report")
    args = ap.parse_args()

    manifest_path = ROOT / args.manifest
    manifest = load_manifest(manifest_path)

    source_repo = manifest.get("source_repo")
    source_paths: Dict[str, str] = manifest.get("source_paths") or {}
    targets: List[Dict[str, Any]] = manifest.get("targets") or []

    if not source_repo:
        raise SystemExit("Manifest is missing 'source_repo'.")
    if not source_paths:
        raise SystemExit("Manifest is missing 'source_paths'.")
    if not targets:
        raise SystemExit("Manifest has no 'targets'.")

    report_items = []
    summary = {
        "total_repos": len(targets),
        "updated": 0,
        "no_changes": 0,
        "clone_failed": 0,
        "error": 0,
    }

    # ------------------------------------------------------------------
    # Clone source-of-truth repo (TVC)
    # ------------------------------------------------------------------
    src_safe = safe_name(source_repo)
    src_dir = WORK / f"src_{src_safe}"
    ensure_clean_dir(src_dir)

    try:
        print(f"Cloning source repo: {source_repo} -> {src_dir}")
        run(["gh", "repo", "clone", source_repo, str(src_dir), "--", "--depth", "1"], cwd=WORK)
    except Exception as e:
        summary["error"] = len(targets)
        msg = f"ERROR: Failed to clone source repo {source_repo}: {e}"
        print(msg)
        for t in targets:
            report_items.append({
                "repo": t.get("repo"),
                "status": "error",
                "message": msg,
            })
        write_report(args.task, summary, report_items)
        raise SystemExit(1)

    # Verify required source files exist
    for src_rel in source_paths.keys():
        p = src_dir / src_rel
        if not p.exists():
            raise SystemExit(f"Source file missing in {source_repo}: {src_rel}")

    # ------------------------------------------------------------------
    # Process each target repo
    # ------------------------------------------------------------------
    for target in targets:
        repo = target.get("repo")
        if not repo:
            continue
        print(f"=== Processing target repo: {repo} ===")

        safe = safe_name(repo)
        dest_dir = WORK / safe
        ensure_clean_dir(dest_dir)

        # Clone target
        try:
            run(["gh", "repo", "clone", repo, str(dest_dir), "--", "--depth", "1"], cwd=WORK)
        except Exception as e:
            msg = f"Clone failed: {e}"
            print(msg)
            summary["clone_failed"] += 1
            report_items.append({
                "repo": repo,
                "status": "clone_failed",
                "message": msg,
            })
            continue

        # Copy files
        try:
            for src_rel, dest_rel in source_paths.items():
                src_file = src_dir / src_rel
                dest_file = dest_dir / dest_rel
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                print(f"Copying {src_file} -> {dest_file}")
                shutil.copy2(src_file, dest_file)
        except Exception as e:
            msg = f"Copy error: {e}"
            print(msg)
            summary["error"] += 1
            report_items.append({
                "repo": repo,
                "status": "error",
                "message": msg,
            })
            continue

        # Check for changes
        status = run(["git", "status", "--porcelain"], cwd=dest_dir, check=False)
        if status.stdout.strip():
            try:
                run(["git", "config", "user.name", "StegVerse-Autopatch"], cwd=dest_dir)
                run(["git", "config", "user.email", "autopatch@stegverse.local"], cwd=dest_dir)
                run(["git", "add", "."], cwd=dest_dir)
                run(["git", "commit", "-m", "Autopatch: sync StegTVC connectivity files"], cwd=dest_dir)
                run(["git", "push", "origin", "HEAD"], cwd=dest_dir)
                summary["updated"] += 1
                report_items.append({
                    "repo": repo,
                    "status": "updated",
                    "message": "Updated & pushed connectivity files.",
                })
            except Exception as e:
                msg = f"Commit/push error: {e}"
                print(msg)
                summary["error"] += 1
                report_items.append({
                    "repo": repo,
                    "status": "error",
                    "message": msg,
                })
        else:
            summary["no_changes"] += 1
            report_items.append({
                "repo": repo,
                "status": "no_changes",
                "message": "Already up to date.",
            })

    write_report(args.task, summary, report_items)


if __name__ == "__main__":
    main()
