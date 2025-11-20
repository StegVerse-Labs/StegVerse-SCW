from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple

ROOT = Path(__file__).resolve().parents[2]

# Where we'll write entity run reports
ENTITY_REPORTS_DIR = ROOT / "reports" / "entities"
ENTITY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _run_cmd(cmd: str) -> Tuple[int, str]:
    proc = subprocess.Popen(
        cmd,
        shell=True,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    out, _ = proc.communicate()
    return proc.returncode, out


def run_economic_snapshot() -> Dict[str, Any]:
    """
    Calls your existing Economic Snapshot workflow logic (Python module).
    """
    rc, out = _run_cmd("python -m ledger.steg_wallet_view")
    return {
        "task": "economic_snapshot",
        "return_code": rc,
        "output": out,
    }


def run_repo_hygiene() -> Dict[str, Any]:
    """
    Calls your existing repo hygiene / audit script if present.
    """
    script = ROOT / "scripts" / "repo_audit.py"
    if not script.exists():
        return {
            "task": "repo_hygiene",
            "return_code": 0,
            "output": "repo_audit.py not found; skipping hygiene.",
        }
    rc, out = _run_cmd("python scripts/repo_audit.py")
    return {
        "task": "repo_hygiene",
        "return_code": rc,
        "output": out,
    }


def _call_github_models(prompt: str, *, system: str = "") -> str:
    """
    Very small wrapper to GitHub Models chat.completions.
    Uses GH_TOKEN or GITHUB_TOKEN from the environment.
    """
    import urllib.request
    import json as _json

    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        return "No GH_TOKEN/GITHUB_TOKEN available; cannot call GitHub Models."

    payload = {
        "model": "openai/gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": system or "You are a StegVerse telemetry analyst."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 900,
        "temperature": 0.2,
    }
    data = _json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://models.github.ai/inference/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            txt = resp.read().decode("utf-8")
            parsed = _json.loads(txt)
            return parsed["choices"][0]["message"]["content"]
    except Exception as e:
        return f"GitHub Models call failed: {e!r}"


def run_status_digest() -> Dict[str, Any]:
    """
    Reads wallet telemetry + ledger integrity reports (if present),
    synthesizes a short status digest via GitHub Models.
    """
    pieces = []

    # Financial telemetry
    fin_dir = ROOT / "ledger" / "telemetry" / "financial"
    if fin_dir.exists():
        latest = sorted(fin_dir.glob("wallet_snapshot_*.md"))[-1:]  # last one
        for p in latest:
            pieces.append(f"# Wallet Snapshot ({p.name})\n" + p.read_text(encoding="utf-8"))

    # Ledger integrity (if present)
    integ_dir = ROOT / "ledger" / "telemetry" / "integrity"
    if integ_dir.exists():
        latest = sorted(integ_dir.glob("ledger_integrity_*.md"))[-1:]
        for p in latest:
            pieces.append(f"# Ledger Integrity ({p.name})\n" + p.read_text(encoding="utf-8"))

    if not pieces:
        text = "No financial or integrity telemetry files found; nothing to summarize."
        ai_summary = text
    else:
        joined = "\n\n---\n\n".join(pieces)
        prompt = (
            "You are StegVerse-AI-001. Summarize the current economic and integrity "
            "state of StegVerse using the following telemetry:\n\n"
            f"{joined}\n\n"
            "Respond with:\n"
            "1) One-paragraph summary\n"
            "2) Bullet list of risks\n"
            "3) Bullet list of suggested next actions for StegVerse AI entities."
        )
        ai_summary = _call_github_models(prompt)

    return {
        "task": "status_digest",
        "return_code": 0,
        "output": ai_summary,
    }


def run_task(task_id: str) -> Dict[str, Any]:
    """
    Main router entry point.
    """
    if task_id == "economic_snapshot":
        return run_economic_snapshot()
    if task_id == "repo_hygiene":
        return run_repo_hygiene()
    if task_id == "status_digest":
        return run_status_digest()
    return {
        "task": task_id,
        "return_code": 0,
        "output": f"No handler defined for task {task_id!r}; skipping.",
    }
