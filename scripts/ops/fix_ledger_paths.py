#!/usr/bin/env python3
"""
Fix & normalize StegVerse ledger event paths.

- Patches log_revenue_event.py so it writes to `ledger/events/...`
  instead of `scripts/ledger/events/...`.
- Migrates any existing revenue event files from the old path
  to the new canonical location.
- Writes a small JSON report under scripts/reports/ledger/.
"""

from pathlib import Path
import json
import shutil
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]

OLD_EVENTS_DIR = ROOT / "scripts" / "ledger" / "events"
NEW_EVENTS_DIR = ROOT / "ledger" / "events"

LOG_REVENUE_SCRIPT = ROOT / "scripts" / "genesis" / "log_revenue_event.py"
REPORT_DIR = ROOT / "scripts" / "reports" / "ledger"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def patch_log_revenue_script():
    """
    Rewrite any hard-coded 'scripts/ledger/events' path in
    log_revenue_event.py to 'ledger/events'.
    """
    if not LOG_REVENUE_SCRIPT.exists():
        return {"patched": False, "reason": "script_missing"}

    text = LOG_REVENUE_SCRIPT.read_text(encoding="utf-8")
    new_text = text.replace("scripts/ledger/events", "ledger/events")

    if new_text == text:
        return {"patched": False, "reason": "already_correct"}

    LOG_REVENUE_SCRIPT.write_text(new_text, encoding="utf-8")
    return {"patched": True, "reason": "path_rewritten"}


def migrate_legacy_events():
    """
    Move any event files from scripts/ledger/events -> ledger/events.
    If a file with the same name already exists at the new location,
    we leave the old one in place and record a warning.
    """
    moved = []
    skipped = []

    if not OLD_EVENTS_DIR.exists():
        return {"moved": moved, "skipped": skipped, "old_dir_exists": False}

    NEW_EVENTS_DIR.mkdir(parents=True, exist_ok=True)

    for p in OLD_EVENTS_DIR.glob("*.jsonl"):
        target = NEW_EVENTS_DIR / p.name
        if target.exists():
            skipped.append({
                "file": str(p.relative_to(ROOT)),
                "reason": "target_exists",
                "target": str(target.relative_to(ROOT)),
            })
            continue

        shutil.move(str(p), str(target))
        moved.append({
            "from": str(p.relative_to(ROOT)),
            "to": str(target.relative_to(ROOT)),
        })

    # If directory is now empty, we can leave it or remove it; for now keep it.
    return {
        "moved": moved,
        "skipped": skipped,
        "old_dir_exists": True,
    }


def main():
    patch_result = patch_log_revenue_script()
    migrate_result = migrate_legacy_events()

    report = {
        "ts": dt.datetime.utcnow().isoformat() + "Z",
        "patch_result": patch_result,
        "migrate_result": migrate_result,
    }

    out = REPORT_DIR / "fix_ledger_paths_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== fix_ledger_paths ===")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
