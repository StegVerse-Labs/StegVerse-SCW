"""
StegLedger (skeleton)

Append-only log of key economic events:
- payments
- grants
- AI wages
- refunds
- token mints/burns

In v1: in-memory + print/JSON emission.
Later: persisted to a DB or Continuity-compatible store.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import time
import json


@dataclass
class LedgerEvent:
    ts: float
    event_type: str
    actor_id: str
    amount_usd_equiv: float
    metadata: Dict[str, Any]


class StegLedger:
    def __init__(self) -> None:
        self._events: List[LedgerEvent] = []

    def record(self, event_type: str, actor_id: str, amount_usd_equiv: float, **metadata: Any) -> LedgerEvent:
        ev = LedgerEvent(
            ts=time.time(),
            event_type=event_type,
            actor_id=actor_id,
            amount_usd_equiv=amount_usd_equiv,
            metadata=metadata,
        )
        self._events.append(ev)
        print("[StegLedger]", json.dumps(ev.__dict__, default=str))
        return ev

    def all_events(self) -> List[LedgerEvent]:
        return list(self._events)


LEDGER = StegLedger()
