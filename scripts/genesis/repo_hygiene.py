#!/usr/bin/env python3
"""
StegVerse Repo Hygiene (Genesis v0.1)

What this script does (read-only to the codebase, writes a report):

- Walks the repo tree and:
  * Counts files by type.
  * Computes SHA256 hashes to find potential duplicate files.
  * Attempts to parse Python / YAML / JSON(/JSONL) files and records parse errors.
- Detects a domain-specific check for StegVerse ledger:
  * If there are ledger event files BUT the latest wallet snapshot still says
    "No ledger events recorded yet.", it flags that as a mismatch.

Output:
- Markdown report at: scripts/reports/hygiene/repo_hygiene_YYYY-MM-DD.md
"""

import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = ROOT / "scripts" / "reports" / "hygiene"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

EXCLUDED_DIRS = {
    ".git",
    ".github/workflows/cache",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    "self_healing_out",
    ".venv",
}

TEXT_EXTS = {".py", ".yml", ".yaml", ".json", ".jsonl", ".md", ".txt"}
PY_EXTS = {".py"}
YAML_EXTS = {".yml", ".yaml"}
JSON_EXTS = {".json", ".jsonl"}


def is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    return any(p in EXCLUDED_DIRS for p in parts)


def iter_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if is_excluded(p):
            continue
        files.append(p)
    return files


def sha256_of(path: Path, max_bytes: int = 5 * 1024 * 1024) -> str:
    """Hash file content (truncating very large files for performance)."""
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            total += len(chunk)
            h.update(chunk)
            if total >= max_bytes:
                # Tag truncated hashes so they don't get false-merged with small files.
                h.update(b"__TRUNCATED__")
                break
    return h.hexdigest()


def try_parse_text_file(path: Path) -> Tuple[bool, str]:
    """
    Try to parse well-known formats; return (ok, message).
    Does NOT raise, always returns something.
    """
    suffix = path.suffix.lower()
    try:
        data = path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"read_error: {e}"

    # Python: just try compile
    if suffix in PY_EXTS:
        try:
            compile(data, str(path), "exec")
            return True, "ok: python syntax"
        except Exception as e:
            return False, f"python_syntax_error: {e}"

    # YAML: best-effort parse if PyYAML is available, otherwise treat as text
    if suffix in YAML_EXTS:
        try:
            import yaml  # type: ignore

            yaml.safe_load(data)
            return True, "ok: yaml parse"
        except Exception as e:
            return False, f"yaml_error: {e}"

    # JSON / JSONL
    if suffix == ".json":
        try:
            json.loads(data)
            return True, "ok: json parse"
        except Exception as e:
            return False, f"json_error: {e}"

    if suffix == ".jsonl":
        try:
            for i, line in enumerate(data.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue
                json.loads(line)
            return True, "ok: jsonl parse"
        except Exception as e:
            return False, f"jsonl_error (line {i}): {e}"

    # Markdown / text: assume OK
    if suffix in {".md", ".txt"}:
        return True, "ok: text"

    return True, "ok: unvalidated"


def ledger_status() -> Dict[str, object]:
    """
    Domain-specific check for StegVerse ledger.

    - Looks for any JSON/JSONL files under `ledger/events`.
    - Looks for latest wallet snapshot markdown under `ledger/telemetry/financial`.
    - If events exist but snapshot still says "No ledger events recorded yet.",
      flag as a inconsistency.
    """
    ledger_dir = ROOT / "ledger"
    events_dir = ledger_dir / "events"
    telemetry_dir = ledger_dir / "telemetry" / "financial"

    has_events = False
    latest_snapshot_path: Path | None = None
    latest_snapshot_ts: datetime.datetime | None = None
    snapshot_says_empty = False

    # Any event files?
    if events_dir.exists():
        for p in events_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".json", ".jsonl"}:
                has_events = True
                break

    # Latest snapshot
    if telemetry_dir.exists():
        for p in telemetry_dir.glob("wallet_snapshot_*.md"):
            if not p.is_file():
                continue
            # sort by mtime
            mtime = datetime.datetime.utcfromtimestamp(p.stat().st_mtime)
            if latest_snapshot_ts is None or mtime > latest_snapshot_ts:
                latest_snapshot_ts = mtime
                latest_snapshot_path = p

    if latest_snapshot_path:
        txt = latest_snapshot_path.read_text(encoding="utf-8", errors="ignore")
        if "No ledger events recorded yet." in txt:
            snapshot_says_empty = True

    status = {
        "has_events": has_events,
        "latest_snapshot": str(latest_snapshot_path) if latest_snapshot_path else None,
        "snapshot_says_empty": snapshot_says_empty,
        "issue": None,
    }

    if has_events and latest_snapshot_path and snapshot_says_empty:
        status["issue"] = (
            "Ledger events exist under `ledger/events`, but the latest "
            "wallet snapshot still shows 'No ledger events recorded yet.'."
        )

    return status


def main() -> None:
    now = datetime.datetime.utcnow()
    today = now.date().isoformat()

    files = iter_files(ROOT)

    stats_by_ext: Dict[str, int] = {}
    duplicates_by_hash: Dict[str, List[Path]] = {}
    parse_errors: List[Dict[str, str]] = []
    oversized: List[Path] = []

    for p in files:
        ext = p.suffix.lower() or "<no_ext>"
        stats_by_ext[ext] = stats_by_ext.get(ext, 0) + 1

        try:
            h = sha256_of(p)
            duplicates_by_hash.setdefault(h, []).append(p)
        except Exception:
            # If we can't hash a file, just skip; it's likely special.
            oversized.append(p)
            continue

        # Parse only "reasonable" text files (< 1MB)
        if ext in TEXT_EXTS and p.stat().st_size <= 1 * 1024 * 1024:
            ok, msg = try_parse_text_file(p)
            if not ok:
                parse_errors.append(
                    {
                        "path": str(p.relative_to(ROOT)),
                        "message": msg,
                    }
                )

    # Build duplicate sets
    duplicate_groups: List[List[Path]] = [
        paths for paths in duplicates_by_hash.values() if len(paths) > 1
    ]

    # Sort duplicate groups by size descending
    duplicate_groups.sort(key=len, reverse=True)

    ledger_info = ledger_status()

    # ---------- Build report ----------
    report_lines: List[str] = []
    report_lines.append("# StegVerse Repo Hygiene Report")
    report_lines.append("")
    report_lines.append(f"- Generated at: `{now.isoformat()}Z`")
    report_lines.append(f"- Root: `{ROOT.name}`")
    report_lines.append("")
    report_lines.append("## Summary")
    report_lines.append(f"- Total files scanned: **{len(files)}**")
    report_lines.append(
        f"- File types: **{len(stats_by_ext)}** (by extension, including `<no_ext>`)"
    )
    report_lines.append(f"- Duplicate groups (same hash): **{len(duplicate_groups)}**")
    report_lines.append(f"- Files with parse errors: **{len(parse_errors)}**")
    report_lines.append("")

    # Stats by ext
    report_lines.append("## Files by extension")
    for ext, count in sorted(stats_by_ext.items(), key=lambda kv: (-kv[1], kv[0])):
        report_lines.append(f"- `{ext}`: **{count}**")
    report_lines.append("")

    # Duplicate details
    report_lines.append("## Potential duplicate files")
    if not duplicate_groups:
        report_lines.append("- None detected.")
    else:
        report_lines.append(
            "> Groups below share the same SHA256 hash. "
            "The first path is the suggested canonical file; others are candidates "
            "for Attic + forwarding stubs."
        )
        report_lines.append("")
        for i, group in enumerate(duplicate_groups, start=1):
            # Pick the shortest path as canonical suggestion
            canonical = min(group, key=lambda p: len(str(p)))
            report_lines.append(f"### Group {i}")
            report_lines.append(f"- Canonical: `{canonical.relative_to(ROOT)}`")
            report_lines.append("- Duplicates:")
            for p in group:
                if p == canonical:
                    continue
                rel = p.relative_to(ROOT)
                attic_path = Path("attic") / rel
                stub_path = rel  # where a forwarding stub could remain
                report_lines.append(
                    f"  - `{rel}` → _candidate_: move to `{attic_path}` and leave "
                    f"a forwarding stub at `{stub_path}`"
                )
            report_lines.append("")
    report_lines.append("")

    # Parse errors
    report_lines.append("## Parse / validation issues")
    if not parse_errors:
        report_lines.append("- None detected for Python / YAML / JSON(/L) files.")
    else:
        for err in parse_errors:
            report_lines.append(f"- `{err['path']}` — {err['message']}")
    report_lines.append("")

    # Ledger-specific health
    report_lines.append("## Ledger & Wallet Telemetry Health Check")
    report_lines.append(f"- Events present under `ledger/events`: **{ledger_info['has_events']}**")
    report_lines.append(
        f"- Latest wallet snapshot: `{ledger_info['latest_snapshot']}`"
    )
    report_lines.append(
        f"- Snapshot says 'No ledger events recorded yet.': "
        f"**{ledger_info['snapshot_says_empty']}**"
    )
    if ledger_info.get("issue"):
        report_lines.append("")
        report_lines.append("### Detected issue")
        report_lines.append(f"- ⚠️ {ledger_info['issue']}")
        report_lines.append("")
        report_lines.append(
            "Suggested future self-heal:\n"
            "- Recompute wallet balances from `ledger/events/*` and "
            "regenerate the latest snapshot so it reflects actual revenue/expense events."
        )
    else:
        report_lines.append("")
        report_lines.append("- ✅ Ledger telemetry appears internally consistent.")
    report_lines.append("")

    # Future actions
    report_lines.append("## Future Attic & Forwarding Automation (Design Sketch)")
    report_lines.append(
        "- This report is **read-only** for now; it does not move or modify any source files."
    )
    report_lines.append(
        "- In a future phase, a `repo_attic_worker` can:\n"
        "  1. Read this report.\n"
        "  2. Move marked duplicates into an `attic/` folder, preserving history.\n"
        "  3. Create forwarding stubs that explain where the canonical file lives.\n"
        "  4. Open autopatch PRs across StegVerse repos referencing the canonical locations."
    )
    report_lines.append("")

    # ---------- Write report ----------
    out_path = REPORT_DIR / f"repo_hygiene_{today}.md"
    out_path.write_text("\n".join(report_lines), encoding="utf-8")

    # Also emit a tiny JSON summary to stdout for logs
    summary = {
        "files": len(files),
        "duplicate_groups": len(duplicate_groups),
        "parse_errors": len(parse_errors),
        "ledger_issue": bool(ledger_info.get("issue")),
        "report": str(out_path.relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
