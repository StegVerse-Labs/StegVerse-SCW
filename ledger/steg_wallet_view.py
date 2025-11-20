#!/usr/bin/env python3
"""
StegVerse Wallet View v0.1

Reads the append-only events ledger and prints balances per account/currency.
Also writes a markdown snapshot under:

  ledger/telemetry/financial/wallet_snapshot_YYYY-MM-DD.md
"""

import datetime
from pathlib import Path

from .steg_ledger_core import load_events, compute_balances, ROOT

SNAP_DIR = ROOT / "ledger" / "telemetry" / "financial"


def write_snapshot() -> Path:
    events = load_events()
    balances = compute_balances(events)

    SNAP_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    ts_iso = datetime.datetime.utcnow().isoformat() + "Z"
    out_path = SNAP_DIR / f"wallet_snapshot_{today}.md"

    lines = [
        "# StegVerse Wallet Snapshot",
        "",
        f"- Generated at: `{ts_iso}`",
        "",
        "## Balances by Account (USD)",
    ]

    if not balances:
        lines.append("")
        lines.append("_No ledger events recorded yet._")
    else:
        lines.append("")
        lines.append("| Account | Currency | Balance |")
        lines.append("|---------|----------|---------|")
        for (account, currency), amount in sorted(balances.items()):
            lines.append(f"| `{account}` | {currency} | ${amount:,.2f} |")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    path = write_snapshot()
    print(f"[wallet_view] Wrote snapshot: {path}")


if __name__ == "__main__":
    main()
