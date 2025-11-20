#!/usr/bin/env python3
"""
fix_ledger_paths.py

StegVerse-SCW ledger self-healing helper.

Goals:
- Ensure we use the canonical per-event layout:
    ledger/events/YYYY-MM-DD/<event_id>.json
- Migrate any stray / legacy files:
    - scripts/ledger/events/*.jsonl  (old JSONL log)
    - scripts/ledger/events/*.json   (misplaced JSON events)
    - ledger/events/revenue_events.jsonl  (old single-file log)

Notes:
- Safe to run repeatedly (idempotent).
- Never deletes source files; it copies / moves + leaves the original
  and prints a warning so we can clean up later.
"""

import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
LEDGER_ROOT = ROOT / "ledger"
CANON_EVENTS = LEDGER_ROOT / "events"

# Legacy locations we want to scan
LEGACY_PATHS = [
    ROOT / "scripts" / "ledger" / "events",
    LEDGER_ROOT / "events",  # for old jsonl in root
]

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def parse_ts(ts: str) -> str:
    """
    Return date string YYYY-MM-DD from a timestamp.
    Falls back to 'unknown' if parsing fails.
    """
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.date().isoformat()
    except Exception:
        return "unknown"

def migrate_jsonl_file(src: Path) -> int:
    """
    Read a JSONL file and emit one canonical JSON file per event.
    Returns number of events migrated.
    """
    if not src.exists():
        return 0

    print(f"[fix_ledger_paths] Migrating JSONL events from {src}")
    count = 0
    with src.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except Exception as e:
                print(f"[fix_ledger_paths]  ! Skipping bad line: {e}")
                continue

            event_id = str(event.get("id") or f"event_{count}")
            ts = str(event.get("ts") or "")
            day = parse_ts(ts)
            target_dir = CANON_EVENTS / day
            ensure_dir(target_dir)
            target = target_dir / f"{event_id}.json"

            # Do not overwrite existing files
            if target.exists():
                print(f"[fix_ledger_paths]  - {target} already exists, skipping")
                continue

            target.write_text(json.dumps(event, indent=2), encoding="utf-8")
            print(f"[fix_ledger_paths]  + wrote {target}")
            count += 1

    print(f"[fix_ledger_paths] Migrated {count} events from {src}")
    return count

def migrate_loose_json(src_dir: Path) -> int:
    """
    Migrate any loose *.json event files from a legacy directory into
    the canonical layout, inferring day from ts if possible.
    """
    if not src_dir.exists():
        return 0

    print(f"[fix_ledger_paths] Scanning loose JSON events in {src_dir}")
    count = 0
    for p in src_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[fix_ledger_paths]  ! Skipping {p}: {e}")
            continue

        event_id = str(data.get("id") or p.stem)
        ts = str(data.get("ts") or "")
        day = parse_ts(ts)
        target_dir = CANON_EVENTS / day
        ensure_dir(target_dir)
        target = target_dir / f"{event_id}.json"

        if target.exists():
            print(f"[fix_ledger_paths]  - {target} already exists, skipping")
            continue

        target.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"[fix_ledger_paths]  + wrote {target}")
        count += 1

    print(f"[fix_ledger_paths] Migrated {count} loose JSON events from {src_dir}")
    return count

def main() -> None:
    ensure_dir(CANON_EVENTS)

    total = 0

    # 1) JSONL logs
    jsonl_candidates = [
        ROOT / "scripts" / "ledger" / "events" / "revenue_events.jsonl",
        LEDGER_ROOT / "events" / "revenue_events.jsonl",
    ]
    for p in jsonl_candidates:
        total += migrate_jsonl_file(p)

    # 2) Loose JSON files in legacy dirs
    for legacy_root in LEGACY_PATHS:
        total += migrate_loose_json(legacy_root)

    if total == 0:
        print("[fix_ledger_paths] No legacy ledger events found. Nothing to migrate.")
    else:
        print(f"[fix_ledger_paths] Completed migration of {total} events.")

if __name__ == "__main__":
    main()
