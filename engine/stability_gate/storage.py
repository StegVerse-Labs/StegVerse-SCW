"""Filesystem persistence for Stability Gate receipts."""

from __future__ import annotations

import json
from pathlib import Path

from .receipt import GateReceipt, canonical_json


DEFAULT_RECEIPT_DIR = Path("artifacts/receipts/stability_gate")


def write_receipt(
    receipt: GateReceipt,
    *,
    receipt_dir: Path = DEFAULT_RECEIPT_DIR,
) -> Path:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    path = receipt_dir / f"{receipt.receipt_hash}.json"
    payload = receipt.canonical_dict()
    serialized = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"

    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if canonical_json(json.loads(existing)) != canonical_json(payload):
            raise RuntimeError(f"receipt hash collision or conflicting artifact: {path}")
        return path

    path.write_text(serialized, encoding="utf-8")
    return path
