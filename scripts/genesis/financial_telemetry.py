#!/usr/bin/env python3
"""
StegVerse Genesis - Financial Telemetry v0.2

- Reads soft/hard caps and current spend from environment (with safe defaults)
- Computes percentages and simple status
- Writes a daily markdown report into:

    ledger/telemetry/financial/daily_YYYY-MM-DD.md

- Prints a JSON summary to stdout for quick inspection in Actions logs.
"""

import datetime
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER_ROOT = ROOT / "ledger" / "telemetry" / "financial"


def load_config() -> dict:
    """Load telemetry config from environment with safe defaults."""
    soft_cap = float(os.getenv("STEG_SOFT_CAP", "250"))
    hard_cap = float(os.getenv("STEG_HARD_CAP", "275"))
    current_spend = float(os.getenv("STEG_CURRENT_SPEND", "0"))

    # Guard against weird values
    soft_cap = max(0.0, soft_cap)
    hard_cap = max(soft_cap, hard_cap)  # hard cap should never be below soft cap
    current_spend = max(0.0, current_spend)

    return {
        "soft_cap": soft_cap,
        "hard_cap": hard_cap,
        "current_spend": current_spend,
    }


def evaluate_status(cfg: dict) -> dict:
    soft_cap = cfg["soft_cap"]
    hard_cap = cfg["hard_cap"]
    current = cfg["current_spend"]

    soft_pct = (current / soft_cap * 100.0) if soft_cap > 0 else 0.0
    hard_pct = (current / hard_cap * 100.0) if hard_cap > 0 else 0.0

    if current <= soft_cap:
        status = "OK"
        notes = "Within soft cap."
    elif current <= hard_cap:
        status = "WARN"
        notes = "Between soft and hard cap."
    else:
        status = "ALERT"
        notes = "Over hard cap."

    return {
        "soft_cap": soft_cap,
        "hard_cap": hard_cap,
        "current_spend": current,
        "soft_pct": round(soft_pct, 2),
        "hard_pct": round(hard_pct, 2),
        "status": status,
        "notes": notes,
    }


def write_daily_markdown(summary: dict) -> Path:
    LEDGER_ROOT.mkdir(parents=True, exist_ok=True)

    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    ts_iso = datetime.datetime.utcnow().isoformat() + "Z"

    fname = f"daily_{today}.md"
    out_path = LEDGER_ROOT / fname

    lines = [
        "# StegVerse Financial Telemetry",
        "",
        f"- Generated at: `{ts_iso}`",
        "",
        "## Caps",
        f"- Soft cap: `${summary['soft_cap']:.2f}`",
        f"- Hard cap: `${summary['hard_cap']:.2f}`",
        "",
        "## Current Spend",
        f"- Amount: `${summary['current_spend']:.2f}`",
        f"- % of soft cap: `{summary['soft_pct']:.2f}%`",
        f"- % of hard cap: `{summary['hard_pct']:.2f}%`",
        "",
        "## Status",
        f"- State: **{summary['status']}**",
        f"- Notes: {summary['notes']}",
    ]

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    cfg = load_config()
    summary = evaluate_status(cfg)
    out_path = write_daily_markdown(summary)

    print("=== StegVerse Financial Telemetry v0.2 (Genesis) ===")
    print(json.dumps(summary, indent=2))
    print(f"[financial_telemetry] Wrote report: {out_path}")
    print("=== Financial Telemetry completed ===")


if __name__ == "__main__":
    main()
