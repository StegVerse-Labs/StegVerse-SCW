#!/usr/bin/env python3
"""
validate_manifest.py
Validates autopatch_manifest.json for structural correctness.
"""

import json
import pathlib
import sys

MANIFEST_PATH = pathlib.Path("autopatch_manifest.json")


def error(msg: str):
    print(f"[ERROR] {msg}")
    sys.exit(1)


def validate_rule(rule):
    required_fields = ["target_repo", "files"]
    for field in required_fields:
        if field not in rule:
            error(f"Rule missing required field: '{field}'")

    # validate files list
    if not isinstance(rule["files"], list):
        error("Field 'files' must be a list")

    for file_entry in rule["files"]:
        if not isinstance(file_entry, dict):
            error("File entry must be a dict")

        if "source" not in file_entry or "target" not in file_entry:
            error("File entry missing 'source' or 'target'")

        if not isinstance(file_entry["source"], str):
            error("File 'source' must be a string")
        if not isinstance(file_entry["target"], str):
            error("File 'target' must be a string")


def main():
    print("=== AutoPatch Manifest Validator ===")

    if not MANIFEST_PATH.exists():
        error("autopatch_manifest.json not found at repo root")

    try:
        manifest = json.loads(MANIFEST_PATH.read_text())
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in manifest: {e}")

    # root fields
    if "version" not in manifest:
        error("Manifest missing 'version' field")

    if "rules" not in manifest:
        error("Manifest missing 'rules' list")

    if not isinstance(manifest["rules"], list):
        error("'rules' must be a list")

    # validate rules
    for idx, rule in enumerate(manifest["rules"]):
        if not isinstance(rule, dict):
            error(f"Rule #{idx} must be an object")
        validate_rule(rule)

    print("Manifest valid!")
    print("Validation complete.")


if __name__ == "__main__":
    main()
