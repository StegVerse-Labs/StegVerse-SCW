#!/usr/bin/env python3
"""
StegTVC connectivity sync (smart version)

- Clones the source repo (default: StegVerse-Labs/TVC)
- Validates that required connectivity files exist (layout validation)
- Auto-discovers their actual locations in the source repo
- Normalizes them into a standard layout in each target repo:
    config   -> data/tv_config.json
    resolver -> app/resolver.py
    client   -> .github/stegtvc_client.py
- For each target repo:
    * Searches for "anomalous" copies of these files in non-standard paths
    * Compares them to the TVC originals via SHA256
    * Classifies anomalies as:
        - duplicate (same content as TVC)
        - diverged (different content from TVC)
    * Leaves anomalies in place but red-flags them in the report
- Writes a markdown report to reports/stegtvc_connectivity_autopatch_report.md
"""

import hashlib
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / "work" / "stegtvc_connectivity"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
WORK_ROOT.mkdir(parents=True, exist_ok=True)

REPORT_PATH = REPORTS_DIR / "stegtvc_connectivity_autopatch_report.md"

# Destination layout we want in ALL target repos
DEST_LAYOUT = {
    "config": Path("data/tv_config.json"),
    "resolver": Path("app/resolver.py"),
    "client": Path(".github/stegtvc_client.py"),
}


def env_or_default(name: str, default: str) -> str:
    val = os.getenv(name)
    return val if val else default


def run_cmd(cmd: List[str], cwd: Path | None = None) -> None:
    print(f"[cmd] {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )


def clone_repo(full_name: str, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    url = f"https://github.com/{full_name}.git"
    run_cmd(["git", "clone", "--depth", "1", url, str(dest)])


def discover_source_layout(source_dir: Path) -> Dict[str, Path]:
    """
    Auto-discover where the connectivity files actually live in TVC.
    Returns a mapping of logical key -> relative source path.
    Raises RuntimeError if required pieces are missing.
    """
    # Candidates for each logical piece
    candidates: Dict[str, List[Path]] = {
        "config": [
            Path("stegtv_config.json"),
            Path("data/tv_config.json"),
            Path("config/stegtv_config.json"),
        ],
        "resolver": [
            Path("resolver.py"),
            Path("app/resolver.py"),
            Path("src/resolver.py"),
        ],
        # Client is optional; we’ll sync it if present
        "client": [
            Path("stegtvc_resolver.py"),
            Path("stegtvc_client.py"),
            Path("app/stegtvc_client.py"),
            Path(".github/stegtvc_client.py"),
        ],
    }

    found: Dict[str, Path] = {}
    missing_required: List[str] = []

    for key, rel_list in candidates.items():
        for rel in rel_list:
            if (source_dir / rel).exists():
                found[key] = rel
                break

        # config + resolver are required; client is optional
        if key in ("config", "resolver") and key not in found:
            missing_required.append(key)

    if missing_required:
        details = []
        for key in missing_required:
            patterns = ", ".join(str(p) for p in candidates[key])
            details.append(f"- {key}: tried {patterns}")
        detail_text = "\n".join(details)
        raise RuntimeError(
            "Source layout validation failed.\n"
            "Could not find required StegTVC connectivity files in source repo.\n"
            f"{detail_text}"
        )

    print("[layout] Discovered source layout:")
    for k, v in found.items():
        print(f"  - {k}: {v}")

    return found


def ensure_dest_dirs(repo_dir: Path) -> None:
    """Ensure the parent directories for the DEST_LAYOUT targets exist."""
    for rel in DEST_LAYOUT.values():
        parent = (repo_dir / rel).parent
        parent.mkdir(parents=True, exist_ok=True)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_if_changed(src: Path, dest: Path) -> bool:
    """
    Copy src -> dest if contents differ. Returns True if changed.
    """
    if not src.exists():
        return False
    before = dest.read_bytes() if dest.exists() else None
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    after = dest.read_bytes()
    return before != after


def find_anomalies(
    repo_dir: Path,
    logical_key: str,
    canonical_rel: Path,
) -> List[Path]:
    """
    Look for files that look like this logical piece but are NOT
    at the canonical path. We scan by name patterns.
    """
    patterns: Dict[str, List[str]] = {
        "config": ["**/stegtv_config.json", "**/tv_config.json"],
        "resolver": ["**/resolver.py"],
        "client": ["**/stegtvc_*.py"],
    }
    results: List[Path] = []
    for pattern in patterns.get(logical_key, []):
        for p in repo_dir.glob(pattern):
            rel = p.relative_to(repo_dir)
            if rel != canonical_rel:
                results.append(rel)
    return sorted(set(results))


def sync_repo(
    source_dir: Path,
    source_layout: Dict[str, Path],
    source_hashes: Dict[str, str],
    target_full_name: str,
    work_root: Path,
) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    Clone target repo, sync connectivity files into standard layout,
    detect anomalies, commit + push if changed.

    Returns:
      (status, message, anomalies)
      status in: "updated", "no_changes", "error"
      anomalies: list of dicts describing odd files
    """
    safe_name = target_full_name.replace("/", "_").replace(".", "_")
    local_dir = work_root / safe_name

    try:
        clone_repo(target_full_name, local_dir)
    except Exception as e:
        return "error", f"clone failed: {e}", []

    ensure_dest_dirs(local_dir)

    changed_any = False
    anomalies: List[Dict[str, Any]] = []

    # For each logical piece, copy canonical from TVC
    for key in ("config", "resolver", "client"):
        if key not in source_layout:
            continue  # client may be missing
        src = source_dir / source_layout[key]
        dest = local_dir / DEST_LAYOUT[key]
        if copy_if_changed(src, dest):
            changed_any = True

        # Scan for anomalies in this repo for this key
        weird_paths = find_anomalies(local_dir, key, DEST_LAYOUT[key])
        for rel in weird_paths:
            full = local_dir / rel
            status = "unknown"
            same = False
            if full.exists():
                try:
                    h = file_hash(full)
                    if key in source_hashes and h == source_hashes[key]:
                        status = "duplicate"
                        same = True
                    else:
                        status = "diverged"
                except Exception as e:
                    status = f"hash_error: {e}"
            anomalies.append(
                {
                    "logical": key,
                    "path": str(rel),
                    "status": status,
                    "same_as_tvc": same,
                }
            )

    if not changed_any:
        status = "no_changes"
        msg = "Already up to date."
    else:
        # Commit + push
        try:
            run_cmd(["git", "add", "data", "app", ".github"], cwd=local_dir)
            run_cmd(
                ["git", "commit", "-m", "Autopatch: sync StegTVC connectivity files"],
                cwd=local_dir,
            )
            run_cmd(["git", "push", "origin", "HEAD"], cwd=local_dir)
            status = "updated"
            msg = "Updated & pushed."
        except Exception as e:
            status = "error"
            msg = f"commit/push failed: {e}"

    return status, msg, anomalies


def main() -> None:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise SystemExit("ERROR: GITHUB_TOKEN / GH_TOKEN is not set.")

    source_repo = env_or_default("SOURCE_REPO", "StegVerse-Labs/TVC")
    raw_targets = env_or_default(
        "TARGET_REPOS",
        "StegVerse-Labs/TVC,StegVerse-Labs/hybrid-collab-bridge,"
        "StegVerse-Labs/TV,StegVerse-Labs/StegVerse-SCW",
    )
    task_label = env_or_default("TASK_LABEL", "manual")

    targets = [
        t.strip() for t in raw_targets.replace("\n", ",").split(",") if t.strip()
    ]

    print(f"[info] Source repo : {source_repo}")
    print(f"[info] Target repos: {targets}")
    print(f"[info] Task label  : {task_label}")

    # 1. Clone source & discover layout
    source_dir = WORK_ROOT / "source_TVC"

    print(f"[step] Cloning source repo {source_repo} ...")
    clone_repo(source_repo, source_dir)

    print("[step] Discovering source layout...")
    source_layout = discover_source_layout(source_dir)

    # Pre-compute hashes of TVC files for anomaly comparison
    source_hashes: Dict[str, str] = {}
    for key, rel in source_layout.items():
        full = source_dir / rel
        if full.exists():
            source_hashes[key] = file_hash(full)

    # 2. Process targets
    summary = {
        "total": len(targets),
        "updated": 0,
        "no_changes": 0,
        "error": 0,
    }
    per_repo: List[Dict[str, Any]] = []

    for repo in targets:
        print(f"[step] Processing target repo: {repo}")
        status, msg, anomalies = sync_repo(
            source_dir, source_layout, source_hashes, repo, WORK_ROOT
        )
        if status in summary:
            summary[status] += 1
        else:
            summary["error"] += 1

        per_repo.append(
            {
                "repo": repo,
                "status": status,
                "message": msg,
                "anomalies": anomalies,
            }
        )

    # 3. Write report
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    run_id = os.getenv("GITHUB_RUN_ID", "local")

    lines: List[str] = []
    lines.append("# StegTVC Connectivity Autopatch Report")
    lines.append("")
    lines.append(f"- Run: {now}")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append(f"- Task: `{task_label}`")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total repos: **{summary['total']}**")
    lines.append(f"- Updated: **{summary['updated']}**")
    lines.append(f"- No changes: **{summary['no_changes']}**")
    lines.append(f"- Errors: **{summary['error']}**")
    lines.append("")
    lines.append("## Per-repo results")

    for item in per_repo:
        repo = item["repo"]
        status = item["status"]
        msg = item["message"]
        anomalies = item.get("anomalies") or []

        icon = "✅" if status == "updated" else "ℹ️" if status == "no_changes" else "⚠️"
        lines.append(f"- {icon} `{repo}` — {status} — {msg}")

        if anomalies:
            lines.append(f"  - Anomalies ({len(anomalies)}):")
            for a in anomalies:
                logical = a["logical"]
                path = a["path"]
                st = a["status"]
                same = " (same as TVC)" if a.get("same_as_tvc") else ""
                lines.append(f"    - `{logical}` at `{path}` — {st}{same}")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[report] Wrote {REPORT_PATH}")

    # Exit non-zero if there were errors
    if summary["error"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
