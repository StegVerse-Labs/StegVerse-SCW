"""
Coinbase Commerce handler stub for StegVerse.

Like stripe_handler, this is a shape-only module for now.

Eventually it will:
- validate Coinbase webhooks
- write events into Continuity and StegLedger
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class CoinbaseConfig:
    enabled: bool
    api_key: Optional[str]
    webhook_secret: Optional[str]


def load_config() -> CoinbaseConfig:
    return CoinbaseConfig(
        enabled=os.getenv("STE G_COINBASE_ENABLED", "false").lower() == "true",
        api_key=os.getenv("COINBASE_COMMERCE_API_KEY"),
        webhook_secret=os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET"),
    )


def record_event(event_id: str, event_type: str, payload: dict) -> None:
    """
    Placeholder for Coinbase Commerce events.
    """
    print(f"[Coinbase] Event: {event_id} ({event_type}) - payload keys={list(payload.keys())}")
