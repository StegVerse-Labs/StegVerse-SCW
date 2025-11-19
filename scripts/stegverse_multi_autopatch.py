#!/usr/bin/env python3
"""
StegVerse multi-repo autopatch runner.

- Uses scripts/stegverse_autopatch_manifest.json as the manifest.
- Copies a set of "default_files" from the current repo (StegVerse-SCW)
  into each target repo listed in "targets".
- For each target:
    * Clones the repo into work/multi_autopatch/<safe_name>
    * Ensures parent dirs for each file exist
    * Copies the file if contents differ
    * Commits & pushes if there were changes
- Writes a markdown report to reports/stegverse_multi_autopatch_report.md
- Prints a JSON summary at the end for easy reading in CI logs.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / "work" / "multi_autopatch"
REPORTS_DIR = ROOT / "reports"
MANIFEST_PATH = ROOT / "scripts" / "stegverse_autopatch_manifest.json"

GIT_ENV = os.environ.copy()


def run_cmd(cmd: List[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a shell command and return the CompletedProcess, never raising."""
    print(f"[cmd] {' '.join(cmd)} (cwd={cwd or ROOT})")
    return subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        env=GIT_ENV,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Manifest not found: {MANIFEST_PATH}")
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Failed to parse manifest {MANIFEST_PATH}: {e}")
    if "default_files" not in data or "targets" not in data:
        raise SystemExit("Manifest must contain 'default_files' and 'targets'.")
    return data


def ensure_source_files(default_files: List[str]) -> None:
    """Fail fast if any source file is missing in StegVerse-SCW."""
    missing: List[str] = []
    for rel in default_files:
        src = ROOT / rel
        if not src.exists():
            missing.append(rel)
    if missing:
        raise SystemExit(
            "The following source files are missing in StegVerse-SCW:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )


def safe_repo_name(repo: str) -> str:
    """Turn org/repo into a filesystem-safe folder name."""
    return repo.replace("/", "__").replace(".", "_")


def clone_repo(repo: str, dest: Path) -> bool:
    """Clone a repo into dest. Returns True if success, False if clone failed."""
    if dest.exists():
        # Clean existing dir to avoid stale state
        print(f"[info] Removing existing directory {dest}")
        for p in sorted(dest.rglob("*"), reverse=True):
            if p.is_file() or p.is_symlink():
                p.unlink(missing_ok=True)
            elif p.is_dir():
                p.rmdir()
        dest.rmdir()

    dest.parent.mkdir(parents=True, exist_ok=True)

    # Prefer explicit x-access-token URL if STEG_TOKEN/GITHUB_TOKEN present
    token = os.environ.get("STEG_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"
    else:
        clone_url = f"https://github.com/{repo}.git"

    cp = run_cmd(["git", "clone", "--depth", "1", clone_url, str(dest)])
    print(cp.stdout)
    if cp.returncode != 0:
        print(f"[error] Clone failed for {repo}")
        return False
    return True


def sync_files_into_repo(
    repo: str,
    repo_dir: Path,
    default_files: List[str],
) -> str:
    """
    Copy default_files from ROOT into repo_dir.
    Returns a status string: 'updated', 'no_changes', or 'error:<msg>'
    """
    try:
        changed = False
        for rel in default_files:
            src = ROOT / rel
            dst = repo_dir / rel

            dst.parent.mkdir(parents=True, exist_ok=True)

            src_text = src.read_text(encoding="utf-8")
            if dst.exists():
                dst_text = dst.read_text(encoding="utf-8")
                if dst_text == src_text:
                    continue  # already identical

            dst.write_text(src_text, encoding="utf-8")
            changed = True
            print(f"[info] Synced {rel} into {repo}")

        if not changed:
            return "no_changes"

        # Commit & push
        cp_status = run_cmd(["git", "status", "--porcelain"], cwd=repo_dir)
        if cp_status.returncode != 0:
            return "error: git status failed"

        if not cp_status.stdout.strip():
            # nothing staged after all
            return "no_changes"

        run_cmd(["git", "add"] + default_files, cwd=repo_dir)

        msg = "Autopatch: sync shared StegVerse workflows"
        run_cmd(["git", "commit", "-m", msg], cwd=repo_dir)

        # Use current branch (usually main)
        branch_cp = run_cmd(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir
        )
        branch = branch_cp.stdout.strip() or "main"

        push_cp = run_cmd(["git", "push", "origin", branch], cwd=repo_dir)
        if push_cp.returncode != 0:
            return "error: git push failed"

        return "updated"

    except Exception as e:  # noqa: BLE001
        return f"error: {e}"


def main() -> None:
    manifest = load_manifest()
    default_files: List[str] = manifest.get("default_files", [])
    targets: List[Dict[str, Any]] = manifest.get("targets", [])

    ensure_source_files(default_files)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "stegverse_multi_autopatch_report.md"

    results: List[Dict[str, Any]] = []
    summary = {"total": 0, "updated": 0, "no_changes": 0, "clone_failed": 0, "error": 0}

    for t in targets:
        repo = t.get("repo")
        if not repo:
            continue

        summary["total"] += 1
        safe_name = safe_repo_name(repo)
        dest = WORK_ROOT / safe_name

        print(f"[info] Processing repo: {repo}")

        if not clone_repo(repo, dest):
            summary["clone_failed"] += 1
            results.append(
                {
                    "repo": repo,
                    "status": "clone_failed",
                    "message": "Failed to clone repository",
                }
            )
            continue

        status = sync_files_into_repo(repo, dest, default_files)
        if status == "updated":
            summary["updated"] += 1
        elif status == "no_changes":
            summary["no_changes"] += 1
        else:
            summary["error"] += 1

        results.append({"repo": repo, "status": status})

    # Write markdown report
    lines: List[str] = []
    lines.append("# StegVerse Multi-Repo Autopatch Report")
    lines.append("")
    lines.append(f"- Run: {os.environ.get('GITHUB_RUN_ID', 'local')} ")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key in ["total", "updated", "no_changes", "clone_failed", "error"]:
        lines.append(f"- **{key}**: {summary[key]}")
    lines.append("")
    lines.append("## Per-repo results")
    lines.append("")
    for r in results:
        lines.append(f"- `{r['repo']}` → **{r['status']}**")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== Multi-autopatch summary ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
