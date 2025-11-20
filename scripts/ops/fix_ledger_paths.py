#!/usr/bin/env python3
"""
Self-healing rule:
Normalize all ledger event files into ledger/events/YYYY-MM-DD/.
Fix incorrectly placed *.json or *.jsonl event files.
Detect stray event files and relocate them safely.
"""

import json
from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledger"
EVENTS = LEDGER / "events"
EVENTS.mkdir(parents=True, exist_ok=True)

def extract_date_from_event(path: Path) -> str:
    """
    Returns YYYY-MM-DD safely based on event timestamp inside file.
    Falls back to today's date if file unreadable.
    """
    try:
        data = json.loads(path.read_text())
        ts = data.get("ts") or data.get("timestamp")
        if ts:
            dt = datetime.fromisoformat(ts.replace("Z",""))
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # fallback
    return datetime.utcnow().strftime("%Y-%m-%d")

def main():
    moved = []

    # 1. Search for ANY stray event files outside the proper structure
    for ext in ("*.json", "*.jsonl"):
        for f in LEDGER.rglob(ext):
            if "events/" in str(f.parent):
                continue  # already in correct structure

            # Determine correct folder
            date_folder = extract_date_from_event(f)
            target_dir = EVENTS / date_folder
            target_dir.mkdir(parents=True, exist_ok=True)

            # Move file
            new_path = target_dir / f.name
            shutil.move(str(f), str(new_path))
            moved.append((str(f), str(new_path)))

    # 2. Write report
    report_path = ROOT / "scripts" / "reports" / "fix_ledger_paths.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w") as r:
        r.write("# Ledger Path Normalization Report\n\n")
        if not moved:
            r.write("No stray event files found.\n")
        else:
            r.write("Moved files:\n")
            for old, new in moved:
                r.write(f"- `{old}` → `{new}`\n")

if __name__ == "__main__":
    main()
