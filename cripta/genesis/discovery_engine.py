#!/usr/bin/env python3
"""
Genesis Discovery Engine v0.1

Safe mapper that:
- Walks the repo
- Notes expected vs. missing key files
- Notes duplicate or suspiciously named connectivity files
- Writes a markdown report for human review

Does NOT move, rename, or delete any files (read-only).
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports" / "genesis"


EXPECTED_CONNECTIVITY_FILES = [
    "data/tv_config.json",
    "app/resolver.py",
    ".github/stegtvc_client.py",
]


def scan_repo() -> Dict[str, List[str]]:
    found = []
    for dirpath, _, filenames in os.walk(ROOT):
        for fname in filenames:
            rel = Path(dirpath).joinpath(fname).relative_to(ROOT)
            found.append(rel.as_posix())

    return {"all_files": found}


def classify_connectivity(found: List[str]) -> Dict[str, List[str]]:
    present = []
    missing = []
    suspects = []

    for path in EXPECTED_CONNECTIVITY_FILES:
        if path in found:
            present.append(path)
        else:
            missing.append(path)

    # Heuristic: connectivity-like files
    for f in found:
        lf = f.lower()
        if any(k in lf for k in ["stegtv", "stegtvc", "tv_config", "resolver", "connectivity"]):
            if f not in present:
                suspects.append(f)

    return {
        "present": present,
        "missing": missing,
        "suspects": suspects,
    }


def write_discovery_report(index: Dict[str, List[str]], connectivity_info: Dict[str, List[str]]):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = REPORTS_DIR / f"discovery_{ts}.md"

    lines = [
        "# Genesis Discovery Report",
        f"- Run: `{datetime.utcnow().isoformat()}Z`",
        "",
        "## Connectivity Summary",
        "",
        "### Present (expected files found)",
    ]
    if connectivity_info["present"]:
        for p in connectivity_info["present"]:
            lines.append(f"- `{p}`")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("### Missing (expected files not found)")
    if connectivity_info["missing"]:
        for m in connectivity_info["missing"]:
            lines.append(f"- `{m}`")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("### Suspect Files (possibly misplaced/duplicate connectivity files)")
    if connectivity_info["suspects"]:
        for s in connectivity_info["suspects"]:
            lines.append(f"- `{s}`")
    else:
        lines.append("- (none)")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[discovery_engine] Wrote discovery report: {path}")


def main():
    print("=== StegVerse Genesis Discovery Engine v0.1 ===")
    index = scan_repo()
    connectivity_info = classify_connectivity(index["all_files"])
    write_discovery_report(index, connectivity_info)
    print("=== Discovery scan complete (read-only). ===")


if __name__ == "__main__":
    main()
