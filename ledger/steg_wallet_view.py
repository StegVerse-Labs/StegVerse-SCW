#!/usr/bin/env python3
"""
StegVerse Wallet View

Entry point for:
- Loading all ledger events
- Computing current balances
- Writing a daily wallet snapshot markdown file under:
    ledger/telemetry/financial/wallet_snapshot_YYYY-MM-DD.md
"""

from __future__ import annotations
import datetime as _dt
from pathlib import Path

from ledger.steg_ledger_core import load_all_events, compute_balances, summarize_balances_md

ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_DIR = ROOT / "ledger" / "telemetry" / "financial"


def generate_snapshot() -> Path:
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

    today = _dt.datetime.utcnow().strftime("%Y-%m-%d")
    ts = _dt.datetime.utcnow().isoformat() + "Z"
    snapshot_path = TELEMETRY_DIR / f"wallet_snapshot_{today}.md"

    events = load_all_events()
    balances = compute_balances(events)
    balance_lines = summarize_balances_md(balances)

    lines = [
        "# StegVerse Wallet Snapshot",
        "",
        f"- Generated at: `{ts}`",
        "",
        "## Balances by Account (USD)",
        "",
    ]

    # If we have USD balances, show those under the primary heading
    usd_accounts = balances.get("USD", {})
    if usd_accounts:
        for acct, amt in sorted(usd_accounts.items()):
            lines.append(f"- **{acct}**: {amt:,.2f} USD")
        lines.append("")
    else:
        # Reuse the generic message if no USD yet
        if not events:
            lines.append("No ledger events recorded yet.")
            lines.append("")
        else:
            lines.append("_No USD-denominated balances yet._")
            lines.append("")

    # Also include a full multi-currency section below
    lines.append("## Full Balance Breakdown")
    lines.append("")
    lines.extend(summarize_balances_md(balances))

    snapshot_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return snapshot_path


def main() -> None:
    path = generate_snapshot()
    print(f"[steg_wallet_view] Wrote wallet snapshot to: {path}")


if __name__ == "__main__":
    main()
