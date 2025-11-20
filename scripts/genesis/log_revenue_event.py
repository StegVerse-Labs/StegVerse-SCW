#!/usr/bin/env python3
"""
Genesis: Log a single revenue event into the ledger.

This is intentionally simple and append-only. It does NOT move real money.
It just records an event line in JSONL so the ledger + snapshots can reason
about revenue streams over time.
"""

import argparse
import datetime as _dt
import json
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

# Auto-discover repo root by walking upward until .git or ledger/ is found
def find_repo_root(start: Path) -> Path:
    p = start
    for _ in range(10):
        if (p / ".git").exists() or (p / "ledger").exists():
            return p
        p = p.parent
    raise RuntimeError("Could not locate repository root")

ROOT = find_repo_root(Path(__file__).resolve())
EVENTS_DIR = ROOT / "ledger" / "events"
EVENTS_FILE = EVENTS_DIR / "revenue_events.jsonl"


def parse_amount(raw: str) -> float:
    try:
        return float(Decimal(raw))
    except (InvalidOperation, ValueError) as e:
        raise SystemExit(f"Invalid amount '{raw}': {e}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--amount", required=True, help="Amount in currency units (e.g. 25.00)")
    ap.add_argument("--currency", default="USD", help="Currency code, default USD")
    ap.add_argument(
        "--kind",
        default="invoice",
        help="Event kind: invoice|subscription|donation|grant|other",
    )
    ap.add_argument(
        "--stream",
        default="core",
        help="Revenue stream label (e.g. stegcore, consulting, grants)",
    )
    ap.add_argument(
        "--status",
        default="expected",
        help="Status: expected|pending|settled|failed|refunded",
    )
    ap.add_argument(
        "--source",
        default="manual",
        help="Origin of this event (manual|stripe|coinbase|internal|other)",
    )
    ap.add_argument(
        "--memo",
        default="",
        help="Free-form note, e.g. 'Pilot customer X subscription, month 1'",
    )
    args = ap.parse_args()

    amount = parse_amount(args.amount)

    EVENTS_DIR.mkdir(parents=True, exist_ok=True)

    ts = _dt.datetime.utcnow().isoformat() + "Z"
    event = {
        "id": str(uuid.uuid4()),
        "ts": ts,
        "kind": args.kind,
        "stream": args.stream,
        "source": args.source,
        "status": args.status,
        "amount": amount,
        "currency": args.currency.upper(),
        "memo": args.memo,
        "meta": {
            "schema": "stegverse.revenue.v1",
            "created_by": "genesis.log_revenue_event",
        },
    }

    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")

    print("=== StegVerse Revenue Event ===")
    print(json.dumps(event, indent=2, sort_keys=True))
    print(f"Wrote to: {EVENTS_FILE}")


if __name__ == "__main__":
    main()
