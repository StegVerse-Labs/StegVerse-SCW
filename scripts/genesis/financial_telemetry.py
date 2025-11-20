#!/usr/bin/env python3
"""
StegVerse Genesis - Financial Telemetry v0.3 (BIG)

- Reads soft/hard caps and current spend from environment (with safe defaults)
- Computes percentages and simple status
- Writes TWO artifacts:

  1) Markdown ledger entry:
     ledger/telemetry/financial/daily_YYYY-MM-DD.md

  2) JSON mirror for machine use:
     ledger/telemetry/financial/daily_YYYY-MM-DD.json

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


def write_markdown(summary: dict, ts_iso: str, day: str, base: Path) -> Path:
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
    md_path = base / f"daily_{day}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path


def write_json(summary: dict, ts_iso: str, day: str, base: Path) -> Path:
    payload = dict(summary)
    payload["generated_at"] = ts_iso
    json_path = base / f"daily_{day}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return json_path


def main() -> None:
    LEDGER_ROOT.mkdir(parents=True, exist_ok=True)

    cfg = load_config()
    summary = evaluate_status(cfg)

    now = datetime.datetime.utcnow()
    day = now.strftime("%Y-%m-%d")
    ts_iso = now.isoformat() + "Z"

    md_path = write_markdown(summary, ts_iso, day, LEDGER_ROOT)
    json_path = write_json(summary, ts_iso, day, LEDGER_ROOT)

    print("=== StegVerse Financial Telemetry v0.3 (Genesis) ===")
    print(json.dumps(summary, indent=2))
    print(f"[financial_telemetry] Wrote markdown: {md_path}")
    print(f"[financial_telemetry] Wrote json:     {json_path}")
    print("=== Financial Telemetry completed ===")


if __name__ == "__main__":
    main()
