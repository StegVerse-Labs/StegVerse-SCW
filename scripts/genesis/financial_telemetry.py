#!/usr/bin/env python3
"""
Financial Telemetry Engine v0.1 (Genesis, dry-run)

What it does now:
- Reads financial_limits.yaml
- Reads/initializes business ledger
- Uses simple placeholders for 'current_spend'
- Calculates % of soft/hard cap
- Writes a human-readable summary report

IMPORTANT:
- No external billing APIs yet (GitHub/OpenAI/etc.).
- Values are placeholders until wired to real data sources.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
LEDGERS_ROOT = ROOT / "stegverse-ledgers"
REPORTS_DIR = ROOT / "reports" / "financial"

FIN_LIMITS_CONFIG = CONFIG_DIR / "financial_limits.yaml"


def load_yaml(path: Path) -> Dict[str, Any]:
    import yaml
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dirs():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (LEDGERS_ROOT / "business").mkdir(parents=True, exist_ok=True)


def get_business_ledger(fin_cfg: Dict[str, Any]) -> Path:
    ledgers_cfg = fin_cfg.get("ledgers", {})
    business_cfg = ledgers_cfg.get("business", {})
    filename = Path(business_cfg.get("path", "ledger.json")).name
    return LEDGERS_ROOT / "business" / filename


def compute_placeholder_spend(biz_data: Dict[str, Any]) -> float:
    """
    For now, we just scan entries and sum an 'amount' field if present.
    Later this will be replaced by real integrations or autopatch annotations.
    """
    total = 0.0
    for e in biz_data.get("entries", []):
        try:
            total += float(e.get("amount", 0.0))
        except Exception:
            continue
    return total


def write_daily_report(summary: Dict[str, Any]):
    ts = datetime.utcnow().strftime("%Y-%m-%d")
    path = REPORTS_DIR / f"daily_{ts}.md"

    lines = [
        "# StegVerse Financial Telemetry – Daily Snapshot",
        f"- Date: `{ts}`",
        f"- Generated at: `{datetime.utcnow().isoformat()}Z`",
        "",
        "## Limits",
        f"- Monthly soft cap: **${summary['soft_cap']:.2f}**",
        f"- Monthly hard cap: **${summary['hard_cap']:.2f}**",
        "",
        "## Current Spend (placeholder)",
        f"- Amount: **${summary['current_spend']:.2f}**",
        f"- % of soft cap: **{summary['soft_pct']:.1f}%**",
        f"- % of hard cap: **{summary['hard_pct']:.1f}%**",
        "",
        "## Status",
        f"- Status: **{summary['status']}**",
        f"- Notes: {summary['notes']}",
        "",
        "_Note: Values are placeholders until telemetry is wired to real billing sources._",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[financial_telemetry] Wrote report: {path}")


def main():
    print("=== StegVerse Financial Telemetry v0.1 (Genesis) ===")
    ensure_dirs()

    fin_cfg = load_yaml(FIN_LIMITS_CONFIG)
    limits = fin_cfg.get("limits", {})
    soft_cap = float(limits.get("monthly_soft_cap", 250.0))
    hard_cap = float(limits.get("monthly_hard_cap", 275.0))

    ledger_path = get_business_ledger(fin_cfg)
    biz_data = load_json(ledger_path) if ledger_path.exists() else {}

    current_spend = compute_placeholder_spend(biz_data)
    soft_pct = (current_spend / soft_cap * 100.0) if soft_cap > 0 else 0.0
    hard_pct = (current_spend / hard_cap * 100.0) if hard_cap > 0 else 0.0

    status = "OK"
    notes = "Within soft cap."
    if soft_pct >= 85.0 and soft_pct < 95.0:
        status = "WARN"
        notes = "Approaching soft cap. Consider slowing non-essential work."
    elif soft_pct >= 95.0 or hard_pct >= 90.0:
        status = "THROTTLE"
        notes = "Near or above limits. Genesis suggests throttling workloads."

    summary = {
        "soft_cap": soft_cap,
        "hard_cap": hard_cap,
        "current_spend": current_spend,
        "soft_pct": soft_pct,
        "hard_pct": hard_pct,
        "status": status,
        "notes": notes,
    }

    print(json.dumps(summary, indent=2))
    write_daily_report(summary)
    print("=== Financial Telemetry completed (no external calls). ===")


if __name__ == "__main__":
    main()
