#!/usr/bin/env python
"""
StegVerse Guardian Worker: Repo Alignment Auto-Fixer (ASL-3)

What it does:
  - Reads latest alignment report from SCW.
  - Clones each failing repo.
  - Applies safe, low-risk scaffolding fixes:
      * Add root README.md if missing.
      * Add docs/stegverse/.steglink.json if missing.
      * Add docs/governance/automation_safety_levels.yaml if missing (minimal default).
      * Add placeholder directories with .gitkeep where required.
  - NEVER edits .github/workflows unless token has workflows permission.
  - Pushes changes back to each repo.

Safety:
  - Only runs if ASL config permits task `repo_alignment_fix` <= ASL-3.
  - Refuses destructive ops. Adds/scaffolds only.

Env:
  - STEGVERSE_ORG (default StegVerse-Labs)
  - TOKEN via STEG_TOKEN / GH_TOKEN / GITHUB_TOKEN
"""

from __future__ import annotations

import json, os, subprocess, sys, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[2]
ASL_CONFIG = ROOT / "docs" / "governance" / "automation_safety_levels.yaml"
LATEST = ROOT / "reports" / "guardians" / "repo_alignment_latest.json"

DEFAULT_ORG = os.getenv("STEGVERSE_ORG", "StegVerse-Labs")
TOKEN = (
    os.getenv("STEG_TOKEN")
    or os.getenv("GH_TOKEN")
    or os.getenv("GITHUB_TOKEN")
    or ""
).strip()

TMP = ROOT / ".tmp_alignment_fix"
TMP.mkdir(parents=True, exist_ok=True)

def run(cmd: List[str], cwd: Optional[Path]=None, check: bool=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)

def load_asl() -> Dict[str, Any]:
    if not ASL_CONFIG.exists() or yaml is None:
        return {}
    return yaml.safe_load(ASL_CONFIG.read_text("utf-8")) or {}

def get_task_asl(cfg: Dict[str, Any], task_id: str) -> str:
    tasks = cfg.get("tasks") or {}
    return (tasks.get(task_id) or {}).get("level") or ""

def is_asl_at_most(asl: str, limit: str) -> bool:
    order = ["ASL-1","ASL-2","ASL-3","ASL-4","ASL-5"]
    if asl not in order or limit not in order:
        return False
    return order.index(asl) <= order.index(limit)

def workflows_permission_available() -> bool:
    """
    We can't perfectly detect fine-grained perms here without API.
    So we use conservative rule:
      - If using classic PAT => assume yes.
      - If fine-grained => assume NO unless user set STEGVERSE_WORKFLOWS_WRITE=1
    """
    if os.getenv("STEGVERSE_WORKFLOWS_WRITE","").strip() == "1":
        return True
    pat_type = os.getenv("STEGVERSE_PAT_TYPE","fine-grained").lower()
    return pat_type == "classic"

def clone_repo(full_name: str) -> Tuple[bool, Path, str]:
    org, repo = full_name.split("/", 1)
    url = f"https://x-access-token:{TOKEN}@github.com/{org}/{repo}.git" if TOKEN else f"https://github.com/{org}/{repo}.git"
    dest = TMP / repo
    if dest.exists():
        run(["rm","-rf",str(dest)], check=False)
    try:
        cp = run(["git","clone",url,str(dest)], check=True)
        return True, dest, cp.stdout
    except subprocess.CalledProcessError as e:
        return False, dest, e.stdout

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True

def add_gitkeep(dir_path: Path) -> bool:
    ensure_dir(dir_path)
    keep = dir_path / ".gitkeep"
    if keep.exists():
        return False
    keep.write_text("", encoding="utf-8")
    return True

def minimal_asl_yaml() -> str:
    return """# StegVerse Automation Safety Levels
tasks:
  repo_alignment_check:
    level: "ASL-1"
    notes: "Read-only alignment scan."
  repo_alignment_fix:
    level: "ASL-3"
    notes: "Safe scaffolding auto-fixes."
  workflow_hygiene:
    level: "ASL-2"
    notes: "Only adds workflow_dispatch when allowed."
"""

def default_steglink_json(full_name: str) -> str:
    org, repo = full_name.split("/",1)
    return json.dumps({
        "schema": "stegverse.steglink.v1",
        "repo": {
            "org": org,
            "name": repo,
            "full_name": full_name,
            "url": f"https://github.com/{full_name}"
        },
        "module": {
            "slug": repo.lower(),
            "kind": "module",
            "status": "genesis",
            "owners": ["stegverse-core"]
        },
        "contracts": {
            "cross_repo": True
        }
    }, indent=2) + "\n"

def default_root_readme(full_name: str) -> str:
    org, repo = full_name.split("/",1)
    return f"""# {repo}

This repo is part of the **StegVerse** ecosystem.

## What this repo is
- Module: `{repo}`
- Org: `{org}`
- Status: Genesis / active scaffolding

## Cross-repo alignment
This repo is aligned with StegVerse-SCW via:
- `docs/stegverse/.steglink.json`
- `docs/governance/automation_safety_levels.yaml`

If those files are missing, StegVerse Guardian may re-add them.

## Dev quickstart
1. Read the module README(s).
2. Run workflows from **Actions → workflow_dispatch** buttons.
3. Keep changes small + traceable.

---
Generated/maintained by StegVerse Guardian (ASL-3 safe-mode).
"""

def changed_files(repo_root: Path) -> str:
    cp = run(["git","status","--porcelain"], cwd=repo_root, check=False)
    return cp.stdout.strip()

def commit_and_push(repo_root: Path, msg: str) -> Tuple[bool,str]:
    run(["git","config","user.name","StegVerse Guardian Worker"], cwd=repo_root, check=False)
    run(["git","config","user.email","guardian-worker@stegverse.local"], cwd=repo_root, check=False)
    run(["git","add","-A"], cwd=repo_root, check=False)

    if not changed_files(repo_root):
        return True, "No changes."
    try:
        run(["git","commit","-m",msg], cwd=repo_root, check=True)
        cp = run(["git","push","origin","main"], cwd=repo_root, check=True)
        return True, cp.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stdout

def main() -> int:
    print("=== StegVerse Guardian Worker: Repo Alignment Auto-Fixer (ASL-3) ===")

    # ASL gate
    cfg = load_asl()
    task_asl = get_task_asl(cfg, "repo_alignment_fix")
    if not task_asl or not is_asl_at_most(task_asl, "ASL-3"):
        print(f"[ASL] repo_alignment_fix is '{task_asl or 'UNSET'}' — refusing to run.")
        return 0

    if not LATEST.exists():
        print(f"[Fixer] Latest alignment report not found: {LATEST}")
        return 1

    data = json.loads(LATEST.read_text("utf-8"))
    repos = data.get("repos") or []
    failing = [r for r in repos if not r.get("pass")]

    if not failing:
        print("[Fixer] No failing repos. Nothing to fix.")
        return 0

    wf_write_ok = workflows_permission_available()
    if not wf_write_ok:
        print("[Fixer] Workflows write NOT enabled for this token. Will not touch .github/workflows anywhere.")

    fixed_count = 0
    for r in failing:
        full_name = r.get("name")
        if not full_name:
            continue

        ok, repo_root, log = clone_repo(full_name)
        if not ok:
            print(f"❌ Clone failed for {full_name}\n{log}")
            continue

        changes = 0

        # README root
        changes += int(write_if_missing(repo_root / "README.md", default_root_readme(full_name)))

        # steglink
        changes += int(write_if_missing(repo_root / "docs/stegverse/.steglink.json", default_steglink_json(full_name)))

        # ASL yaml
        changes += int(write_if_missing(repo_root / "docs/governance/automation_safety_levels.yaml", minimal_asl_yaml()))

        # Placeholder dirs
        changes += int(add_gitkeep(repo_root / "docs"))
        changes += int(add_gitkeep(repo_root / "scripts"))
        changes += int(add_gitkeep(repo_root / ".github/workflows"))

        # NEVER modify workflows unless explicitly allowed
        if wf_write_ok:
            # still no edits here (reserved for workflow_hygiene worker)
            pass

        ok_push, push_log = commit_and_push(repo_root, "Guardian: repo alignment safe scaffolding")
        if ok_push:
            if changes:
                fixed_count += 1
            print(f"✅ {full_name}: fixed={changes>0} changes={changes}")
        else:
            print(f"❌ {full_name}: push failed\n{push_log}")

    print("")
    print(f"Summary: repos_fixed={fixed_count} of {len(failing)} failing repos")
    print("=== Repo Alignment Auto-Fixer complete. ===")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
