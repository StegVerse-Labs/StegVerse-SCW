#!/usr/bin/env python3
"""
StegVerse Ledger Core v0.1

- Append-only JSONL event log
- Simple balance computation per (account, currency)
- Designed to be safe for Git-based workflows:
  - Small, line-oriented events
  - Tolerant of partial writes / bad lines
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
LEDGER_DIR = ROOT / "ledger" / "events"
LEDGER_FILE = LEDGER_DIR / "events.jsonl"


@dataclass
class LedgerEvent:
    ts: str               # ISO timestamp (UTC)
    kind: str             # "spend", "revenue", "transfer", "meta"
    account: str          # logical account name, e.g. "Rigel/Personal", "StegVerse/Cloud"
    amount: float         # positive numbers only; sign is implied by kind
    currency: str = "USD"
    source: str = ""      # e.g. "GitHub/SCW", "OpenAI/ChatGPT"
    meta: Dict[str, Any] = field(default_factory=dict)


def _ensure_dir() -> None:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)


def record_event(
    ts: str,
    kind: str,
    account: str,
    amount: float,
    currency: str = "USD",
    source: str = "",
    meta: Dict[str, Any] | None = None,
    ledger_path: Path | None = None,
) -> None:
    """
    Append a single ledger event as a JSON line.

    NOTE: amount should always be positive; direction is implied by `kind`:
      - "spend"    => funds leave `account`
      - "revenue"  => funds enter `account`
      - "transfer" => requires meta["to_account"], moves between accounts
    """
    if ledger_path is None:
        ledger_path = LEDGER_FILE

    _ensure_dir()
    event = LedgerEvent(
        ts=ts,
        kind=kind,
        account=account,
        amount=float(amount),
        currency=currency,
        source=source,
        meta=meta or {},
    )
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), sort_keys=True) + "\n")


def load_events(ledger_path: Path | None = None) -> List[LedgerEvent]:
    """Load all events from the JSONL file, skipping any bad lines."""
    if ledger_path is None:
        ledger_path = LEDGER_FILE

    if not ledger_path.exists():
        return []

    events: List[LedgerEvent] = []
    with ledger_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                events.append(LedgerEvent(**raw))
            except Exception:
                # Corrupt line? Skip but keep the rest.
                continue
    return events


def compute_balances(events: Iterable[LedgerEvent]) -> Dict[Tuple[str, str], float]:
    """
    Compute balances per (account, currency).

    Rules:
      - "revenue"  => +amount
      - "spend"    => -amount
      - "transfer" => -amount from event.account, +amount to meta["to_account"]
      - others     => ignored for balance math
    """
    balances: Dict[Tuple[str, str], float] = {}

    def add(account: str, currency: str, delta: float) -> None:
        key = (account, currency)
        balances[key] = balances.get(key, 0.0) + delta

    for ev in events:
        if ev.kind == "revenue":
            add(ev.account, ev.currency, ev.amount)
        elif ev.kind == "spend":
            add(ev.account, ev.currency, -ev.amount)
        elif ev.kind == "transfer":
            to_acct = ev.meta.get("to_account")
            if to_acct:
                add(ev.account, ev.currency, -ev.amount)
                add(to_acct, ev.currency, ev.amount)
        else:
            # "meta" or unknown types do not affect balances
            continue

    return balances
