#!/usr/bin/env python3
"""Correlate local workstation incidents without mutating or publishing them."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def tokens(value: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", value.lower()) if len(t) > 2}


def fingerprint(incident: dict) -> set[str]:
    c = incident.get("classification", {})
    o = incident.get("observation", {})
    fields = [
        c.get("vendor") or "",
        c.get("product") or "",
        c.get("platform") or "",
        c.get("surface") or "",
        c.get("category") or "",
        " ".join(c.get("tags") or []),
        o.get("summary") or "",
        o.get("observed_behavior") or "",
    ]
    return tokens(" ".join(fields))


def similarity(a: set[str], b: set[str]) -> float:
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def load_incidents(directory: Path) -> list[dict]:
    incidents = []
    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            record = json.load(handle)
        if record.get("schema") == "stegverse.workstation-incident/v1":
            incidents.append(record)
    return incidents


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--incident-dir", default="data/workstation-incidents")
    parser.add_argument("--threshold", type=float, default=0.35)
    args = parser.parse_args()

    incidents = load_incidents(Path(args.incident_dir))
    rows = []
    for index, left in enumerate(incidents):
        left_fp = fingerprint(left)
        for right in incidents[index + 1 :]:
            score = similarity(left_fp, fingerprint(right))
            if score >= args.threshold:
                rows.append({
                    "left": left["incident_id"],
                    "right": right["incident_id"],
                    "score": round(score, 4),
                })
    print(json.dumps({"schema": "stegverse.workstation-incident-correlation/v1", "matches": rows}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
