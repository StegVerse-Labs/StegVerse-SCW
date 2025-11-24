#!/usr/bin/env python
"""
StegVerse Guardian Worker: PAT Secrets Check (ASL-1)

Goal:
  - Check that expected PAT secrets are present in environment.
  - Write report to reports/pat_audit/pat_secrets_latest.md + .json

How it works:
  - EXPECTED_PATS env var contains names of secrets (space or newline separated)
  - This guardian DOES NOT reveal token values, only missing/present.

Safety:
  - Read-only local check.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "pat_audit"

@dataclass
class SecretCheck:
    name: str
    present: bool

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def parse_expected() -> List[str]:
    raw = os.environ.get("EXPECTED_PATS", "").strip()
    if not raw:
        return []
    # split on any whitespace
    return [x.strip() for x in raw.split() if x.strip()]

def main() -> int:
    expected = parse_expected()
    if not expected:
        print("No EXPECTED_PATS env set. Nothing to check.")
        return 0

    checks: List[SecretCheck] = []
    missing = 0
    for name in expected:
        present = bool(os.environ.get(name, "").strip())
        checks.append(SecretCheck(name=name, present=present))
        if not present:
            missing += 1

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "pat_secrets_latest.json"
    md_path = REPORT_DIR / "pat_secrets_latest.md"

    payload = {
        "generated_at": now_utc_iso(),
        "expected_count": len(expected),
        "missing_count": missing,
        "checks": [asdict(c) for c in checks],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    lines.append("# StegVerse PAT Secrets Guardian Report")
    lines.append("")
    lines.append(f"- Generated at (UTC): `{now_utc_iso()}`")
    lines.append(f"- Expected secrets: `{len(expected)}`")
    lines.append(f"- Missing secrets: `{missing}`")
    lines.append("")
    for c in checks:
        mark = "✅" if c.present else "❌"
        lines.append(f"- {mark} `{c.name}`")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Report written: {md_path}")
    print(f"JSON written: {json_path}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
