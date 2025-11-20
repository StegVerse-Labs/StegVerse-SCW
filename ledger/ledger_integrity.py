#!/usr/bin/env python3
"""
StegVerse Ledger Integrity Guardian (Genesis v0.1)

- Scans ledger/events/ for JSON event files
- Validates structure & fields
- Detects:
    * JSON parse errors
    * duplicate event IDs
    * negative / non-numeric amounts
    * future-dated timestamps
- Computes simple balances by currency + stream
- Emits a human-readable report in:
    scripts/reports/ledger/ledger_integrity_YYYY-MM-DD.md

This is read-only: it does not modify events, only reports.
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Repo root is one level up from this file (ledger/)
ROOT = Path(__file__).resolve().parents[1]
EVENT_ROOT = ROOT / "ledger" / "events"
REPORT_DIR = ROOT / "scripts" / "reports" / "ledger"


def iter_event_files() -> List[Path]:
    if not EVENT_ROOT.exists():
        return []
    return sorted(EVENT_ROOT.rglob("*.json"))


def load_json(path: Path) -> Tuple[Any, str]:
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        return data, ""
    except Exception as e:
        return None, f"JSON error: {e}"


def ensure_list(obj: Any) -> List[Dict[str, Any]]:
    # We support either a single dict or a list of dicts
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        return [obj]
    return []


def is_number(x: Any) -> bool:
    try:
        v = float(x)
        return not math.isnan(v) and not math.isinf(v)
    except Exception:
        return False


def parse_ts(ts: Any) -> Tuple[datetime, str]:
    if not isinstance(ts, str):
        return None, "ts not a string"
    try:
        # Accept ISO8601 with or without trailing Z
        if ts.endswith("Z"):
            ts = ts[:-1]
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt, ""
    except Exception as e:
        return None, f"bad ts: {e}"


def analyze_events() -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    files = iter_event_files()

    summary = {
        "files_scanned": 0,
        "events_scanned": 0,
        "files_with_errors": 0,
        "events_with_errors": 0,
        "duplicate_ids": 0,
        "future_events": 0,
        "negative_amounts": 0,
    }

    errors: List[str] = []
    balances: Dict[str, float] = {}                # currency -> amount
    balances_by_stream: Dict[str, Dict[str, float]] = {}  # stream -> currency -> amount
    seen_ids: set[str] = set()

    for path in files:
        summary["files_scanned"] += 1
        data, jerr = load_json(path)
        if jerr:
            summary["files_with_errors"] += 1
            errors.append(f"- `{path}` → {jerr}")
            continue

        events = ensure_list(data)
        if not events:
            continue

        for ev in events:
            summary["events_scanned"] += 1

            # Basic shape
            eid = ev.get("id")
            ts = ev.get("ts")
            amt = ev.get("amount")
            cur = ev.get("currency", "USD")
            stream = ev.get("stream", "unknown")
            kind = ev.get("kind", "unknown")

            # ID checks
            if not isinstance(eid, str) or not eid:
                summary["events_with_errors"] += 1
                errors.append(f"- `{path}` → missing/invalid id for event: {ev!r}")
            elif eid in seen_ids:
                summary["events_with_errors"] += 1
                summary["duplicate_ids"] += 1
                errors.append(f"- `{path}` → duplicate id `{eid}`")
            else:
                seen_ids.add(eid)

            # Amount checks
            if not is_number(amt):
                summary["events_with_errors"] += 1
                errors.append(f"- `{path}` → non-numeric amount for id `{eid}`: {amt!r}")
                continue  # can't use this event for balances

            amt_f = float(amt)
            if amt_f < 0:
                summary["negative_amounts"] += 1

            # Timestamp checks
            ts_dt, ts_err = parse_ts(ts)
            if ts_err:
                summary["events_with_errors"] += 1
                errors.append(f"- `{path}` → {ts_err} for id `{eid}`")
            else:
                if ts_dt > now:
                    summary["future_events"] += 1
                    errors.append(
                        f"- `{path}` → future-dated event `{eid}` at {ts_dt.isoformat()}"
                    )

            # Accumulate balances
            balances[cur] = balances.get(cur, 0.0) + amt_f
            if stream not in balances_by_stream:
                balances_by_stream[stream] = {}
            balances_by_stream[stream][cur] = (
                balances_by_stream[stream].get(cur, 0.0) + amt_f
            )

    return {
        "summary": summary,
        "errors": errors,
        "balances": balances,
        "balances_by_stream": balances_by_stream,
        "generated_at": now.isoformat(),
    }


def write_report(result: Dict[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = REPORT_DIR / f"ledger_integrity_{today}.md"

    s = result["summary"]
    lines: List[str] = []

    lines.append("# StegVerse Ledger Integrity Report")
    lines.append("")
    lines.append(f"- Generated at: `{result['generated_at']}`")
    lines.append(f"- Event root: `ledger/events/`")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Files scanned: **{s['files_scanned']}**")
    lines.append(f"- Events scanned: **{s['events_scanned']}**")
    lines.append(f"- Files with errors: **{s['files_with_errors']}**")
    lines.append(f"- Events with errors: **{s['events_with_errors']}**")
    lines.append(f"- Duplicate IDs: **{s['duplicate_ids']}**")
    lines.append(f"- Future-dated events: **{s['future_events']}**")
    lines.append(f"- Negative amounts: **{s['negative_amounts']}**")
    lines.append("")

    lines.append("## Balances by Currency")
    if result["balances"]:
        for cur, amt in sorted(result["balances"].items()):
            lines.append(f"- **{cur}**: `{amt:.2f}`")
    else:
        lines.append("- No valid events yet.")
    lines.append("")

    lines.append("## Balances by Stream")
    if result["balances_by_stream"]:
        for stream, sub in sorted(result["balances_by_stream"].items()):
            lines.append(f"- **{stream}**")
            for cur, amt in sorted(sub.items()):
                lines.append(f"  - {cur}: `{amt:.2f}`")
    else:
        lines.append("- No stream breakdown available.")
    lines.append("")

    lines.append("## Detected Issues")
    if result["errors"]:
        lines.extend(result["errors"])
    else:
        lines.append("- No integrity issues detected 🎉")
    lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    result = analyze_events()
    report_path = write_report(result)
    # Print JSON-ish summary for the Actions log
    print(
        json.dumps(
            {
                "report": str(report_path),
                "summary": result["summary"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
