#!/usr/bin/env python3
"""
StegVerse Financial Daily Rollup (Genesis v0.1)

Collects:
- Latest wallet snapshot from ledger/telemetry/financial/
- Latest financial telemetry report from scripts/reports/financial/
- Latest ledger integrity report from scripts/reports/ledger/

Writes a consolidated dashboard to:
- scripts/reports/financial/daily_rollup_YYYY-MM-DD.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List


ROOT = Path(__file__).resolve().parents[2]

WALLET_DIR = ROOT / "ledger" / "telemetry" / "financial"
FIN_REPORT_DIR = ROOT / "scripts" / "reports" / "financial"
LEDGER_REPORT_DIR = ROOT / "scripts" / "reports" / "ledger"


@dataclass
class WalletSnapshot:
  path: Path
  generated_at: str
  body: str


def latest_by_prefix(folder: Path, prefix: str) -> Optional[Path]:
    if not folder.exists():
        return None
    candidates = sorted(
        [p for p in folder.glob(f"{prefix}*") if p.is_file()],
        key=lambda p: p.name,
    )
    return candidates[-1] if candidates else None


def load_wallet() -> Optional[WalletSnapshot]:
    p = latest_by_prefix(WALLET_DIR, "wallet_snapshot_")
    if not p:
        return None
    text = p.read_text(encoding="utf-8")
    m = re.search(r"Generated at:\s*`([^`]+)`", text)
    ts = m.group(1) if m else "unknown"
    return WalletSnapshot(path=p, generated_at=ts, body=text)


def load_latest_file(folder: Path, prefix: str) -> Optional[Path]:
    return latest_by_prefix(folder, prefix)


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    FIN_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = FIN_REPORT_DIR / f"daily_rollup_{today}.md"

    wallet = load_wallet()
    fin_report = load_latest_file(FIN_REPORT_DIR, "daily_")
    ledger_report = load_latest_file(LEDGER_REPORT_DIR, "ledger_integrity_")

    lines: List[str] = []
    lines.append("# StegVerse Daily Financial Rollup")
    lines.append("")
    lines.append(f"- Generated at: `{now}`")
    lines.append("")

    # Wallet
    lines.append("## Wallet Snapshot")
    if wallet:
        lines.append(f"- Source: `{wallet.path.relative_to(ROOT)}`")
        lines.append(f"- Snapshot time: `{wallet.generated_at}`")
    else:
        lines.append("- No wallet snapshot found.")
    lines.append("")

    # Link-style pointers (paths)
    lines.append("## Component Reports")
    if wallet:
        lines.append(
            f"- Wallet snapshot: `{wallet.path.relative_to(ROOT)}`"
        )
    if fin_report:
        lines.append(
            f"- Financial telemetry: `{fin_report.relative_to(ROOT)}`"
        )
    if ledger_report:
        lines.append(
            f"- Ledger integrity: `{ledger_report.relative_to(ROOT)}`"
        )
    if not any([wallet, fin_report, ledger_report]):
        lines.append("- No component reports available yet.")
    lines.append("")

    lines.append("## Notes")
    lines.append("- This is a lightweight index for all Genesis financial views.")
    lines.append("- Future versions may inline summaries / KPIs here.")
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"Wrote daily rollup to {out.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
