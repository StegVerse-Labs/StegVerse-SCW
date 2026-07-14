#!/usr/bin/env python3
"""Safely inspect or normalize GitHub Actions workflow YAML.

This tool deliberately avoids parsing and re-dumping complete workflow files.
A full YAML round-trip can reinterpret the GitHub key ``on`` as a boolean and
can destroy comments, quoting, and expression formatting.

Safe mutations are limited to:
- CRLF/CR line-ending normalization
- trailing whitespace removal
- final newline insertion

Tabs are reported but never rewritten automatically because replacing them can
change block-scalar or indentation semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

OUTDIR = Path("self_healing_out")
REPORT_MD = OUTDIR / "YAML_REPAIR_REPORT.md"
REPORT_JSON = OUTDIR / "YAML_REPAIR_REPORT.json"
CHANGED_FLAG = OUTDIR / "YAML_REPAIR_CHANGED"


class GitHubActionsLoader(yaml.SafeLoader):
    """YAML loader that treats ``on``/``off``/``yes``/``no`` as strings."""


for first_char, resolvers in list(GitHubActionsLoader.yaml_implicit_resolvers.items()):
    GitHubActionsLoader.yaml_implicit_resolvers[first_char] = [
        resolver
        for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:bool"
    ]

GitHubActionsLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    yaml.resolver.Resolver.yaml_implicit_resolvers["t"][0][1],
    list("tTfF"),
)


def normalized_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip(" ") for line in text.split("\n"))
    if not text.endswith("\n"):
        text += "\n"
    return text


def inspect_file(path: Path, apply: bool) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="strict")
    candidate = normalized_text(raw)
    safe_change = candidate != raw
    tab_lines = [i for i, line in enumerate(raw.splitlines(), start=1) if "\t" in line]

    parse_error = None
    document_type = None
    top_level_keys: list[str] = []
    try:
        data = yaml.load(candidate, Loader=GitHubActionsLoader)
        document_type = type(data).__name__
        if isinstance(data, dict):
            top_level_keys = [str(key) for key in data.keys()]
    except Exception as exc:  # report exact parser failure; never guess a repair
        parse_error = f"{type(exc).__name__}: {exc}"

    changed = False
    if apply and safe_change:
        path.write_text(candidate, encoding="utf-8")
        changed = True

    return {
        "path": path.as_posix(),
        "parse_valid": parse_error is None,
        "parse_error": parse_error,
        "document_type": document_type,
        "top_level_keys": top_level_keys,
        "has_name": "name" in top_level_keys,
        "has_on": "on" in top_level_keys,
        "has_jobs": "jobs" in top_level_keys,
        "tab_lines": tab_lines,
        "safe_normalization_available": safe_change,
        "changed": changed,
    }


def select_files(directory: Path, requested_file: str | None) -> list[Path]:
    if requested_file:
        if Path(requested_file).name != requested_file:
            raise ValueError("--file must be a top-level workflow filename")
        if not requested_file.endswith((".yml", ".yaml")):
            raise ValueError("--file must end in .yml or .yaml")
        target = directory / requested_file
        if not target.is_file():
            raise FileNotFoundError(target)
        return [target]
    return sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml"))


def write_reports(results: list[dict[str, Any]], apply: bool) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "files": len(results),
        "parse_valid": sum(1 for r in results if r["parse_valid"]),
        "parse_invalid": sum(1 for r in results if not r["parse_valid"]),
        "safe_normalization_available": sum(
            1 for r in results if r["safe_normalization_available"]
        ),
        "changed": sum(1 for r in results if r["changed"]),
        "apply": apply,
    }
    REPORT_JSON.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Workflow YAML Repair Report",
        "",
        f"- Mode: **{'apply safe normalization' if apply else 'report only'}**",
        f"- Files inspected: **{summary['files']}**",
        f"- Parse-valid: **{summary['parse_valid']}**",
        f"- Parse-invalid: **{summary['parse_invalid']}**",
        f"- Files changed: **{summary['changed']}**",
        "",
        "| File | Parse | Safe normalization | Tabs | Changed |",
        "|---|:---:|:---:|:---:|:---:|",
    ]
    for result in results:
        lines.append(
            "| `{}` | {} | {} | {} | {} |".format(
                result["path"],
                "valid" if result["parse_valid"] else "invalid",
                "yes" if result["safe_normalization_available"] else "no",
                ", ".join(map(str, result["tab_lines"])) or "—",
                "yes" if result["changed"] else "no",
            )
        )
        if result["parse_error"]:
            lines.append(f"\n> `{result['path']}`: {result['parse_error']}\n")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if summary["changed"]:
        CHANGED_FLAG.write_text("changed\n", encoding="utf-8")
    elif CHANGED_FLAG.exists():
        CHANGED_FLAG.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".github/workflows")
    parser.add_argument("--file", help="Inspect exactly one top-level workflow filename")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply only safe text normalization; never structurally rewrite YAML",
    )
    args = parser.parse_args()

    directory = Path(args.dir)
    if not directory.is_dir():
        parser.error(f"workflow directory not found: {directory}")

    try:
        files = select_files(directory, args.file)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))

    results = [inspect_file(path, args.apply) for path in files]
    write_reports(results, args.apply)

    invalid = sum(1 for result in results if not result["parse_valid"])
    print(REPORT_MD.as_posix())
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
