"""Coinbase Commerce compatibility stub for StegVerse SCW.

Credential-bearing Coinbase Commerce authentication/webhook verification belongs
inside an admitted TV/TVC provider-operation boundary. This consumer stub does
not read or retain provider credentials.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

TVC_ROUTE_REQUIRED = "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED"


@dataclass(frozen=True)
class CoinbaseConfig:
    enabled: bool
    api_key: Optional[str]
    webhook_secret: Optional[str]
    credential_authority: str = "TV/TVC"
    provider_route_state: str = TVC_ROUTE_REQUIRED


def load_config() -> CoinbaseConfig:
    """Return a credential-neutral, fail-closed compatibility configuration."""
    return CoinbaseConfig(enabled=False, api_key=None, webhook_secret=None)


def record_event(event_id: str, event_type: str, payload: dict) -> None:
    """Record only non-secret event-shape evidence."""
    print(f"[Coinbase] Event: {event_id} ({event_type}) - payload keys={list(payload.keys())}")
