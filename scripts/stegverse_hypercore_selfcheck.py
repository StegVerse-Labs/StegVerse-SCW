#!/usr/bin/env python3
"""
StegVerse HyperCore Self-Check

This script is intentionally lightweight and safe to run from GitHub Actions.
It verifies:
- the presence of key directories/files for the HyperCore
- that the core registry can be imported
- a basic, human-readable status report

Output is printed as Markdown so it can be pasted into issues if needed.
"""

import os
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_path(rel: str) -> bool:
    return (ROOT / rel).exists()


def main() -> None:
    print("# StegVerse HyperCore Self-Check\n")

    paths = [
        "docs/STEGVERSE_HYPERCORE.md",
        "core/stegverse_core.py",
        "core/worker_registry.yaml",
        "finance/payments_config.example.json",
        "finance/stripe_handler.py",
        "finance/coinbase_handler.py",
        "compliance/compliance_rules.yaml",
        "compliance/risk_register.md",
        "ledger/steg_wallet.py",
        "ledger/steg_token.py",
        "ledger/steg_ledger.py",
    ]

    results = {}
    for rel in paths:
        exists = check_path(rel)
        results[rel] = exists
        status = "✅" if exists else "❌"
        print(f"- {status} `{rel}`")

    # Try importing the core registry
    try:
        sys.path.insert(0, str(ROOT))
        from core.stegverse_core import CORE  # type: ignore

        print("\n## Core Registry\n")
        print(f"- Modules: {len(CORE.list_modules())}")
        for m in CORE.list_modules():
            print(f"  - `{m.name}` → `{m.repo}` — {m.role}")
        print(f"- Worker classes: {len(CORE.list_worker_classes())}")
        for w in CORE.list_worker_classes():
            print(f"  - `{w.code}` — {w.description} (priority {w.default_priority})")
    except Exception as e:
        print("\n## Core Registry\n")
        print(f"- ❌ Failed to import `core.stegverse_core`: `{e}`")

    print("\n## Raw JSON\n")
    print("```json")
    print(json.dumps(results, indent=2))
    print("```")


if __name__ == "__main__":
    main()
