#!/usr/bin/env python3
"""
StegVerse Multi-Repo Autopatch Runner

- Uses a JSON manifest to decide:
    * which repos to touch
    * which files to sync into each repo
- For each repo:
    * git clone --depth 1 https://github.com/<repo>.git
    * copy canonical files from StegVerse-SCW into that repo
    * commit + push if anything changed
- Writes a summary markdown report to:
    reports/stegverse_multi_autopatch_report.md

The workflow sets up:
- PAT-based git URL rewriting
- GITHUB_TOKEN / GH_TOKEN / STEG_TOKEN (classic PAT)
so no tokens are hard-coded here.
"""

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / "work" / "multi_autopatch"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def safe_name(repo):
    """Turn 'StegVerse-Labs/TV' into 'StegVerse-Labs__TV' etc."""
    return repo.replace("/", "__").replace(".", "_")


def run(cmd, cwd=None, check=True, capture_output=False):
    """Run a shell command with logging."""
    print(f"[cmd] {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        capture_output=capture_output,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {cmd}")
    return result


def clone_repo(repo):
    """Clone a repo into WORK_ROOT/<safe_name> (fresh each run)."""
    dest = WORK_ROOT / safe_name(repo)
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{repo}.git"
    run(f"git clone --depth 1 {url} {dest}")
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="JSON manifest listing repos + files")
    ap.add_argument("--task", default="manual", help="Optional label for this run")
    args = ap.parse_args()

    # Fresh work area each run
    if WORK_ROOT.exists():
        shutil.rmtree(WORK_ROOT)
    WORK_ROOT.mkdir(parents=True, exist_ok=True)

    manifest_path = ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    default_files = manifest.get("default_files") or []
    targets = manifest.get("targets") or []

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    task = args.task

    summary = {
        "total": len(targets),
        "updated": 0,
        "no_changes": 0,
        "clone_failed": 0,
        "error": 0,
    }
    per_repo = []

    for t in targets:
        repo = t.get("repo")
        if not repo:
            summary["error"] += 1
            per_repo.append(
                {"repo": "<missing>", "status": "error", "message": "No repo specified in manifest"}
            )
            continue

        files = t.get("files") or default_files
        if not files:
            summary["error"] += 1
            per_repo.append(
                {
                    "repo": repo,
                    "status": "error",
                    "message": "No files configured (manifest.default_files is empty)",
                }
            )
            continue

        try:
            repo_dir = clone_repo(repo)
        except Exception as e:
            summary["clone_failed"] += 1
            per_repo.append(
                {"repo": repo, "status": "clone_failed", "message": f"clone failed: {e}"}
            )
            continue

        changed_any = False
        try:
            # Copy / sync files
            for entry in files:
                if isinstance(entry, dict):
                    src_rel = entry.get("from")
                    dst_rel = entry.get("to") or src_rel
                else:
                    # simple string -> same path in target
                    src_rel = dst_rel = entry

                if not src_rel:
                    continue

                src_path = ROOT / src_rel
                if not src_path.exists():
                    raise FileNotFoundError(f"Source file not found: {src_rel}")

                dst_path = repo_dir / dst_rel
                dst_path.parent.mkdir(parents=True, exist_ok=True)

                src_text = src_path.read_text(encoding="utf-8")
                if dst_path.exists():
                    dst_text = dst_path.read_text(encoding="utf-8")
                    if dst_text == src_text:
                        # Already identical; nothing to do for this file
                        continue

                dst_path.write_text(src_text, encoding="utf-8")
                changed_any = True

            status = "no_changes"
            message = "Already up to date."

            if changed_any:
                st = run(
                    "git status --porcelain",
                    cwd=repo_dir,
                    check=False,
                    capture_output=True,
                )
                if st.stdout.strip():
                    run(
                        'git config user.name "StegVerse Autopatch Bot"',
                        cwd=repo_dir,
                    )
                    run(
                        'git config user.email "autopatch-bot@users.noreply.github.com"',
                        cwd=repo_dir,
                    )
                    run("git add .", cwd=repo_dir)
                    run(
                        'git commit -m "Autopatch: sync shared StegVerse workflows"',
                        cwd=repo_dir,
                    )
                    run("git push origin HEAD", cwd=repo_dir)
                    status = "updated"
                    message = "Updated & pushed."
                else:
                    status = "no_changes"
                    message = "Files identical after copy; nothing to commit."

            if status == "updated":
                summary["updated"] += 1
            elif status == "no_changes":
                summary["no_changes"] += 1

            per_repo.append({"repo": repo, "status": status, "message": message})

        except Exception as e:
            summary["error"] += 1
            per_repo.append(
                {"repo": repo, "status": "error", "message": f"exception: {e}"}
            )

    # Build markdown report
    lines = [
        "# StegVerse Multi-Repo Autopatch Report",
        "",
        f"- Run: {ts}",
        f"- Run ID: `{run_id}`",
        f"- Task: `{task}`",
        "",
        "## Summary",
        f"- Total repos: **{summary['total']}**",
        f"- Updated: **{summary['updated']}**",
        f"- No changes: **{summary['no_changes']}**",
        f"- Clone failed: **{summary['clone_failed']}**",
        f"- Errors: **{summary['error']}**",
        "",
        "## Per-repo results",
    ]

    for r in per_repo:
        emoji = {
            "updated": "✅",
            "no_changes": "ℹ️",
            "clone_failed": "❌",
            "error": "⚠️",
        }.get(r["status"], "•")
        lines.append(
            f"- {emoji} `{r['repo']}` — {r['status']} — {r['message']}"
        )

    report_path = REPORTS_DIR / "stegverse_multi_autopatch_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Also print JSON summary to logs for quick glance
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
