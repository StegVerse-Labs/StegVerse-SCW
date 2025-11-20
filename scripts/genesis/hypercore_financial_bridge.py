#!/usr/bin/env python3
"""
StegVerse Genesis - HyperCore Financial Bridge v0.1

- Reads the *latest* financial telemetry JSON from:
    ledger/telemetry/financial/daily_YYYY-MM-DD.json

- Injects or updates a 'Financial Snapshot' block inside:
    docs/STEGVERSE_HYPERCORE.md

  using markers:

    <!-- BEGIN FINANCIAL_SNAPSHOT -->
    ...
    <!-- END FINANCIAL_SNAPSHOT -->

- If anything is missing, exits quietly (no crash).
"""

import json
import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
LEDGER_DIR = ROOT / "ledger" / "telemetry" / "financial"
HYPERCORE_DOC = ROOT / "docs" / "STEGVERSE_HYPERCORE.md"


def find_latest_financial_json() -> Optional[Path]:
    if not LEDGER_DIR.exists():
        return None
    candidates = sorted(LEDGER_DIR.glob("daily_*.json"))
    return candidates[-1] if candidates else None


def load_summary(p: Path) -> Optional[dict]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def render_block(summary: dict, rel_path: str) -> str:
    return f"""<!-- BEGIN FINANCIAL_SNAPSHOT -->
## Financial Snapshot (auto-linked)

- Status: **{summary.get('status', 'UNKNOWN')}**
- Current spend: `${summary.get('current_spend', 0):.2f}`
- Soft cap: `${summary.get('soft_cap', 0):.2f}` ({summary.get('soft_pct', 0):.2f}%)
- Hard cap: `${summary.get('hard_cap', 0):.2f}` ({summary.get('hard_pct', 0):.2f}%)
- Notes: {summary.get('notes', '—')}
- Source: `{rel_path}`

<!-- END FINANCIAL_SNAPSHOT -->
""".rstrip() + "\n"


def patch_hypercore_doc(block: str) -> None:
    if not HYPERCORE_DOC.exists():
        # No doc yet; create a minimal one containing just the block
        HYPERCORE_DOC.parent.mkdir(parents=True, exist_ok=True)
        HYPERCORE_DOC.write_text("# StegVerse HyperCore\n\n" + block, encoding="utf-8")
        return

    txt = HYPERCORE_DOC.read_text(encoding="utf-8")

    pattern = r"<!-- BEGIN FINANCIAL_SNAPSHOT -->(?:.|\n)*?<!-- END FINANCIAL_SNAPSHOT -->"
    if re.search(pattern, txt, flags=re.MULTILINE):
        new_txt = re.sub(pattern, block.strip(), txt, flags=re.MULTILINE)
    else:
        # Append at the end with a separator
        if not txt.endswith("\n"):
            txt += "\n"
        new_txt = txt + "\n" + block

    HYPERCORE_DOC.write_text(new_txt, encoding="utf-8")


def main() -> None:
    latest = find_latest_financial_json()
    if not latest:
        print("[hypercore_financial_bridge] No financial JSON found; skipping.")
        return

    summary = load_summary(latest)
    if not summary:
        print("[hypercore_financial_bridge] Could not parse financial JSON; skipping.")
        return

    rel_path = str(latest.relative_to(ROOT))
    block = render_block(summary, rel_path)
    patch_hypercore_doc(block)

    print(f"[hypercore_financial_bridge] Updated HyperCore doc with {rel_path}")


if __name__ == "__main__":
    main()
