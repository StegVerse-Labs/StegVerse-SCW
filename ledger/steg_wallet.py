"""
StegWallet (skeleton)

Goal:
- Provide a unified interface for balances:
  - fiat summary (via Stripe)
  - crypto summary (via Coinbase/external wallets)
  - StegToken balance (internal ledger)

In v1 this is a simple in-memory model; later it will be backed by a datastore.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class WalletSnapshot:
    fiat_usd: float = 0.0
    crypto_usd_equiv: float = 0.0
    steg_tokens: float = 0.0


@dataclass
class Wallet:
    owner_id: str
    balances: WalletSnapshot = field(default_factory=WalletSnapshot)

    def total_usd_equiv(self, steg_token_price_usd: float = 1.0) -> float:
        return (
            self.balances.fiat_usd
            + self.balances.crypto_usd_equiv
            + self.balances.steg_tokens * steg_token_price_usd
        )


class WalletRegistry:
    """
    Simple in-memory registry. Later this should sit behind a datastore.
    """

    def __init__(self) -> None:
        self._wallets: Dict[str, Wallet] = {}

    def get_or_create(self, owner_id: str) -> Wallet:
        if owner_id not in self._wallets:
            self._wallets[owner_id] = Wallet(owner_id=owner_id)
        return self._wallets[owner_id]


REGISTRY = WalletRegistry()
