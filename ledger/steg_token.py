"""
StegToken (skeleton)

Internal utility token for:
- compensating AI workers
- gating access to certain modules
- representing "credit" inside StegVerse

This is NOT a blockchain token yet; it is an internal ledger entry.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass
class TokenBalance:
    owner_id: str
    amount: float = 0.0


class StegTokenLedger:
    def __init__(self) -> None:
        self._balances: Dict[str, TokenBalance] = {}

    def get_balance(self, owner_id: str) -> float:
        bal = self._balances.get(owner_id)
        return bal.amount if bal else 0.0

    def _get_or_create(self, owner_id: str) -> TokenBalance:
        if owner_id not in self._balances:
            self._balances[owner_id] = TokenBalance(owner_id=owner_id, amount=0.0)
        return self._balances[owner_id]

    def mint(self, owner_id: str, amount: float, reason: str = "") -> None:
        bal = self._get_or_create(owner_id)
        bal.amount += amount
        print(f"[StegToken] Mint {amount} to {owner_id} – reason={reason}")

    def burn(self, owner_id: str, amount: float, reason: str = "") -> None:
        bal = self._get_or_create(owner_id)
        bal.amount = max(0.0, bal.amount - amount)
        print(f"[StegToken] Burn {amount} from {owner_id} – reason={reason}")


LEDGER = StegTokenLedger()
