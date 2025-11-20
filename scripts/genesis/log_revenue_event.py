#!/usr/bin/env python3
"""
Genesis: log_revenue_event

Creates a single revenue event file under:

  ledger/events/YYYY-MM-DD/<event_id>.json

Inputs (env vars):

  STEG_AMOUNT   (float string, required)
  STEG_CURRENCY (e.g. "USD", default "USD")
  STEG_KIND     (e.g. "invoice", default "invoice")
  STEG_MEMO     (string, optional)
  STEG_SOURCE   (string, default "manual")
  STEG_STREAM   (string, default "stegcore")
  STEG_DRY_RUN  ("true"/"false", default "false")

Prints the event JSON to stdout and path where it was written.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER_EVENTS_ROOT = ROOT / "ledger" / "events"


def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v if v is not None and v != "" else default


def main() -> None:
    # Inputs
    amount_raw = env("STEG_AMOUNT", "0")
    try:
        amount = float(amount_raw)
    except ValueError:
        raise SystemExit(f"Invalid STEG_AMOUNT: {amount_raw!r}")

    currency = env("STEG_CURRENCY", "USD")
    kind = env("STEG_KIND", "invoice")
    memo = env("STEG_MEMO", "").strip() or "No memo"
    source = env("STEG_SOURCE", "manual")
    stream = env("STEG_STREAM", "stegcore")
    dry_run = env("STEG_DRY_RUN", "false").lower() == "true"

    now = datetime.now(timezone.utc)
    ts = now.isoformat().replace("+00:00", "Z")
    day = now.date().isoformat()
    event_id = str(uuid.uuid4())

    event = {
        "id": event_id,
        "ts": ts,
        "amount": amount,
        "currency": currency,
        "kind": kind,
        "memo": memo,
        "meta": {
            "created_by": "genesis.log_revenue_event",
            "schema": "stegverse.revenue.v1",
        },
        "source": source,
        "status": "expected",
        "stream": stream,
    }

    rel_dir = Path("ledger") / "events" / day
    rel_path = rel_dir / f"{event_id}.json"
    abs_dir = LEDGER_EVENTS_ROOT / day
    abs_dir.mkdir(parents=True, exist_ok=True)
    abs_path = abs_dir / f"{event_id}.json"

    print("=== StegVerse Revenue Event (Genesis) ===")
    print(json.dumps(event, indent=2))
    print()
    print(f"dry_run: {dry_run}")
    print(f"target_file: {rel_path}")

    if dry_run:
        print("[log_revenue_event] Dry run; not writing file.")
        return

    abs_path.write_text(json.dumps(event, indent=2), encoding="utf-8")
    print(f"[log_revenue_event] Wrote {abs_path}")


if __name__ == "__main__":
    main()
