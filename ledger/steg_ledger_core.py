#!/usr/bin/env python3
"""
StegVerse Ledger Core

Responsibilities:
- Discover and load ledger event files under ledger/events/**
- Tolerate a few different formats:
  * Single JSON object
  * JSON array of objects
  * JSON-lines (.jsonl) one event per line
- Compute balances per (currency, account/stream)
- Provide helpers to generate wallet snapshots

Current assumptions (Genesis v0.1):
- Default account is taken from:
    event["account"] if present
    else event["stream"] if present
    else "stegcore"
- Positive amounts increase the balance (no debits modeled yet).
"""

from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
LEDGER_ROOT = ROOT / "ledger"
EVENTS_ROOT = LEDGER_ROOT / "events"


@dataclass
class LedgerEvent:
    id: str
    ts: str
    amount: float
    currency: str
    account: str
    raw: Dict[str, Any]


def _iter_event_files() -> Iterable[Path]:
    """
    Yield all candidate event files under ledger/events.
    Looks for both .json and .jsonl files.
    """
    if not EVENTS_ROOT.exists():
        return
    for ext in (".json", ".jsonl"):
        for path in EVENTS_ROOT.rglob(f"*{ext}"):
            if path.is_file():
                yield path


def _load_json_any(path: Path) -> Any:
    """
    Try to load JSON from a file that may be:
    - standard JSON (object or array)
    - JSON-lines (.jsonl): one JSON object per line
    """
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return []

    # Try standard JSON first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Fallback: JSON-lines (one event per line)
    items: List[Any] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            # best-effort; skip bad lines
            continue
    return items


def _normalize_raw_events(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize arbitrary parsed JSON into a flat list of dict events.
    Supported patterns:
    - dict  -> single event
    - list  -> list of events
    - dict with 'events' key -> use value
    """
    if isinstance(data, dict):
        # If dict has "events", treat that as the list
        if "events" in data and isinstance(data["events"], list):
            return [e for e in data["events"] if isinstance(e, dict)]
        # Otherwise treat the dict itself as a single event
        return [data]
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    return []


def _normalize_event(raw: Dict[str, Any]) -> Optional[LedgerEvent]:
    """
    Convert a raw dict into a LedgerEvent, if possible.
    Returns None for unusable events.
    """
    try:
        ev_id = str(raw.get("id") or raw.get("event_id") or "")
        ts = str(raw.get("ts") or raw.get("timestamp") or "")
        amount = float(raw.get("amount", 0.0))
        currency = str(raw.get("currency") or "USD").upper().strip() or "USD"

        # Account routing:
        account = (
            str(raw.get("account"))
            or str(raw.get("stream"))
            or "stegcore"
        )

        if not ts:
            # We still accept it, but it's a bit malformed; keep ts empty
            ts = ""

        return LedgerEvent(
            id=ev_id,
            ts=ts,
            amount=amount,
            currency=currency,
            account=account,
            raw=raw,
        )
    except Exception:
        return None


def load_all_events() -> List[LedgerEvent]:
    """
    Load and normalize all events from ledger/events/**.
    Skips files with unreadable JSON.
    """
    events: List[LedgerEvent] = []
    for path in _iter_event_files():
        try:
            parsed = _load_json_any(path)
            raw_events = _normalize_raw_events(parsed)
            for raw in raw_events:
                ev = _normalize_event(raw)
                if ev is not None:
                    events.append(ev)
        except Exception:
            # Hygiene workers will flag parse issues separately
            continue
    return events


def compute_balances(events: Iterable[LedgerEvent]) -> Dict[str, Dict[str, float]]:
    """
    Compute balances grouped by currency, then by account.

    Returns structure:
    {
      "USD": {
         "stegcore": 10.01,
         "account2": 5.00
      },
      "EUR": { ... }
    }
    """
    balances: Dict[str, Dict[str, float]] = {}
    for ev in events:
        cur = ev.currency
        acct = ev.account or "stegcore"
        balances.setdefault(cur, {}).setdefault(acct, 0.0)
        balances[cur][acct] += ev.amount
    return balances


def summarize_balances_md(balances: Dict[str, Dict[str, float]]) -> List[str]:
    """
    Produce human-readable markdown lines for balances.
    """
    lines: List[str] = []
    if not balances:
        lines.append("No ledger events recorded yet.")
        return lines

    for currency, accounts in sorted(balances.items()):
        lines.append(f"### Balances in {currency}")
        if not accounts:
            lines.append("")
            lines.append("_No accounts for this currency yet._")
            lines.append("")
            continue
        lines.append("")
        for acct, amt in sorted(accounts.items()):
            lines.append(f"- **{acct}**: {amt:,.2f} {currency}")
        lines.append("")

    return lines
