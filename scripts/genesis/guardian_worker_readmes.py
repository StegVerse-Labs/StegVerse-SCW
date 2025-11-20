#!/usr/bin/env python
"""
StegVerse Guardian Worker: README Generator (Genesis v0.4, ASL-aware)

Reads:
  - reports/guardians/guardian_run_latest.json
  - docs/governance/automation_safety_levels.yaml

Behavior:
  - Looks for the 'readme_refresh' task in the latest guardian run.
  - Reads its assigned Automation Safety Level (ASL) from the governance config.
  - If ASL-1: allowed to auto-generate missing README.md files.
  - If higher than ASL-1: worker refuses to write, logs that it's blocked.

For ASL-1:
  - If README.md is missing in a folder:
      * Inspect file names in that folder.
      * Call GitHub Models (via GITHUB_TOKEN) to generate a starter README.
      * Save README.md with an auto-generated banner.

Safety:
  - Never overwrites an existing README.md.
  - Caps the number of README files created per run.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests

try:
    import yaml  # We already use PyYAML in SCW
except Exception:
    yaml = None


ROOT = Path(__file__).resolve().parents[2]  # .../StegVerse-SCW
REPORT_DIR = ROOT / "reports" / "guardians"
LATEST_JSON = REPORT_DIR / "guardian_run_latest.json"
ASL_CONFIG = ROOT / "docs" / "governance" / "automation_safety_levels.yaml"


# ---------------- ASL helpers ----------------

def load_asl_config() -> Dict[str, Any]:
    if not ASL_CONFIG.exists():
        print(f"[ASL] Config not found at {ASL_CONFIG}; defaulting to safe mode (no writes).")
        return {}
    if yaml is None:
        print("[ASL] PyYAML not available; defaulting to safe mode (no writes).")
        return {}
    with ASL_CONFIG.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_task_asl(cfg: Dict[str, Any], task_id: str) -> str:
    tasks = (cfg.get("tasks") or {})
    t = tasks.get(task_id) or {}
    return t.get("level") or ""


def is_asl_at_most(asl: str, limit: str) -> bool:
    order = ["ASL-1", "ASL-2", "ASL-3", "ASL-4", "ASL-5"]
    if asl not in order or limit not in order:
        return False
    return order.index(asl) <= order.index(limit)


# ---------------- Core helpers ----------------

def load_latest_run() -> Dict[str, Any]:
    if not LATEST_JSON.exists():
        raise SystemExit(f"Latest guardian JSON not found: {LATEST_JSON}")
    with LATEST_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or ""
    if not token:
        raise SystemExit("GITHUB_TOKEN / GH_TOKEN is required for GitHub Models.")
    return token


def call_github_model(system_prompt: str, user_prompt: str, token: str) -> str:
    url = "https://models.github.ai/inference/chat/completions"
    payload = {
        "model": "openai/gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 700,
        "temperature": 0.25,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    if resp.status_code >= 400:
        raise RuntimeError(
            f"GitHub Models error {resp.status_code}: {resp.text[:300]}"
        )
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps(data, indent=2)


def list_folder_contents(folder: Path) -> List[str]:
    if not folder.exists():
        return []
    names: List[str] = []
    for p in sorted(folder.iterdir()):
        if p.name.startswith("."):
            continue
        if p.is_dir():
            names.append(p.name + "/")
        else:
            names.append(p.name)
    return names


def build_user_prompt(rel_path: str, files: List[str]) -> str:
    lines: List[str] = []
    lines.append(
        "You are StegVerse Docs AI. Generate a short, practical README.md "
        "for this folder inside the StegVerse-SCW repository."
    )
    lines.append("")
    lines.append(f"Folder path (relative to repo root): `{rel_path}`")
    lines.append("")
    if files:
        lines.append("Entries currently in this folder:")
        for name in files:
            lines.append(f"- {name}")
        lines.append("")
    else:
        lines.append("The folder is currently empty (no files detected).")
        lines.append("")
    lines.append("README requirements:")
    lines.append("- Start with an H1 header matching the folder purpose.")
    lines.append("- Include sections: Overview, Key files/responsibilities, How this fits into StegVerse, Notes/TODO.")
    lines.append("- Do NOT invent specific APIs or behavior that you cannot infer.")
    lines.append("- It's OK to add TODO bullets where details are unknown.")
    lines.append("")
    lines.append(
        "Return only valid Markdown, no surrounding explanations. "
        "Keep it concise and focused on helping a human (Rigel or another "
        "developer/AI worker) understand and extend this folder."
    )
    return "\n".join(lines)


def main() -> int:
    print("=== StegVerse Guardian Worker: README Generator (ASL-aware) ===")

    # 1) Load ASL config and verify that this task is allowed to write
    asl_cfg = load_asl_config()
    task_id = "readme_refresh"
    task_asl = get_task_asl(asl_cfg, task_id)

    if not task_asl:
        print(f"[ASL] No ASL level configured for task '{task_id}'.")
        print("[ASL] Refusing to auto-write READMEs (safe mode).")
        return 0

    print(f"[ASL] Task '{task_id}' is configured as {task_asl}")
    if not is_asl_at_most(task_asl, "ASL-1"):
        print("[ASL] This task is not ASL-1 or lower; refusing to write.")
        print("[ASL] You can still generate proposals by adding another worker later.")
        return 0

    # 2) Load guardian latest run
    run_data = load_latest_run()
    token = get_github_token()

    tasks = run_data.get("tasks") or []
    readme_task = None
    for t in tasks:
        if t.get("id") == task_id:
            readme_task = t
            break

    if not readme_task:
        print("No `readme_refresh` task found in latest guardian run. Nothing to do.")
        return 0

    details = readme_task.get("details") or {}
    missing_dirs = details.get("readme_missing") or []
    if not missing_dirs:
        print("Guardian reports no missing README directories. Nothing to do.")
        return 0

    system_prompt = (
        "You are an internal StegVerse documentation assistant. "
        "You help organize and document the StegVerse-SCW repository. "
        "You are careful, conservative, and do not fabricate precise behavior "
        "when you cannot see the code; instead, you add TODO notes."
    )

    created = 0
    skipped_existing = 0
    skipped_missing_folder = 0

    for rel in sorted(set(missing_dirs)):
        folder = ROOT / rel
        readme_path = folder / "README.md"

        if not folder.exists():
            print(f"- Skipping `{rel}` (folder does not exist on disk).")
            skipped_missing_folder += 1
            continue

        if readme_path.exists():
            print(f"- Skipping `{rel}` (README.md already exists).")
            skipped_existing += 1
            continue

        # Safety: cap number of creations per run
        if created >= 12:
            print("Reached generation limit (12 README files). Stopping.")
            break

        print(f"- Generating README.md for `{rel}` ...")
        files = list_folder_contents(folder)
        user_prompt = build_user_prompt(rel, files)

        try:
            content = call_github_model(system_prompt, user_prompt, token)
        except Exception as e:
            print(f"  ❌ GitHub Models call failed for `{rel}`: {e}")
            continue

        banner = (
            "<!-- AUTO-GENERATED by StegVerse Guardian Worker (ASL-1).\n"
            "     Edit freely; this file is meant as a starting point.\n"
            "     Regenerate via Guardians if needed. -->\n\n"
        )
        final_md = banner + content.strip() + "\n"

        folder.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(final_md, encoding="utf-8")
        created += 1
        print(f"  ✅ Wrote {readme_path.relative_to(ROOT)}")

    print("")
    print("Summary:")
    print(f"- New README files created: {created}")
    print(f"- Skipped (already had README): {skipped_existing}")
    print(f"- Skipped (folder not present): {skipped_missing_folder}")
    print("=== Guardian Worker finished. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
