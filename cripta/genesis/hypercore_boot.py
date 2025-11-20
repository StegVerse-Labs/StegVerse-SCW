#!/usr/bin/env python3
"""
HyperCore Genesis Boot – v0.1

Safe, dry-run initializer for:
- Genesis lane config
- Dual ledger structure (personal + business)
- Basic reports folders
- Health summary

NO external network calls, NO billing APIs, NO crypto ops.
"""

import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
REPORTS_DIR = ROOT / "reports" / "genesis"
LEDGERS_ROOT = ROOT / "stegverse-ledgers"

GENESIS_CONFIG = CONFIG_DIR / "genesis_core.yaml"
FIN_LIMITS_CONFIG = CONFIG_DIR / "financial_limits.yaml"


def load_yaml(path: Path):
    import yaml  # installed by workflow
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ensure_dirs():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (LEDGERS_ROOT / "personal").mkdir(parents=True, exist_ok=True)
    (LEDGERS_ROOT / "business").mkdir(parents=True, exist_ok=True)


def ensure_ledger(path: Path, kind: str):
    """
    Initialize basic ledger file if missing.
    For personal: kept simple & private (you can encrypt later).
    For business: standard JSON ledger.
    """
    if path.exists():
        return False

    if kind == "personal":
        data = {
            "version": 1,
            "kind": "personal",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "entries": [],
            "notes": "Genesis v0.1 personal ledger initialized (no sensitive data stored yet).",
        }
    else:
        data = {
            "version": 1,
            "kind": "business",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "entries": [],
            "notes": "Genesis v0.1 business ledger initialized.",
        }

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True


def write_boot_report(summary: dict):
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    report_path = REPORTS_DIR / f"genesis_boot_{ts}.md"

    lines = [
        "# HyperCore Genesis Boot Report",
        f"- Run: `{datetime.utcnow().isoformat()}Z`",
        "",
        "## Status",
    ]
    for k, v in summary.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[hypercore_boot] Wrote report: {report_path}")


def main():
    print("=== StegVerse HyperCore Genesis Boot v0.1 ===")

    ensure_dirs()

    genesis_cfg = load_yaml(GENESIS_CONFIG)
    fin_cfg = load_yaml(FIN_LIMITS_CONFIG)

    lanes = genesis_cfg.get("lanes", {})
    defaults = genesis_cfg.get("defaults", {})
    ledgers_cfg = fin_cfg.get("ledgers", {})

    summary = {
        "lanes_defined": len(lanes),
        "dry_run": str(defaults.get("dry_run", True)),
        "personal_ledger_initialized": "no",
        "business_ledger_initialized": "no",
        "soft_cap": str(fin_cfg.get("limits", {}).get("monthly_soft_cap", "unknown")),
        "hard_cap": str(fin_cfg.get("limits", {}).get("monthly_hard_cap", "unknown")),
    }

    # Ledgers
    personal_cfg = ledgers_cfg.get("personal", {})
    business_cfg = ledgers_cfg.get("business", {})

    # Personal
    if personal_cfg.get("enabled"):
        p_path = LEDGERS_ROOT / "personal" / Path(personal_cfg.get("path", "")).name
        if ensure_ledger(p_path, "personal"):
            summary["personal_ledger_initialized"] = f"created: {p_path}"
        else:
            summary["personal_ledger_initialized"] = f"exists: {p_path}"

    # Business
    if business_cfg.get("enabled"):
        b_path = LEDGERS_ROOT / "business" / Path(business_cfg.get("path", "")).name
        if ensure_ledger(b_path, "business"):
            summary["business_ledger_initialized"] = f"created: {b_path}"
        else:
            summary["business_ledger_initialized"] = f"exists: {b_path}"

    print(json.dumps(summary, indent=2))
    write_boot_report(summary)
    print("=== HyperCore Genesis Boot completed (dry-run safe). ===")


if __name__ == "__main__":
    main()
