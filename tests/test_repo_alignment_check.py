from __future__ import annotations

import importlib.util
from pathlib import Path


def test_repo_alignment_checker_main_passes() -> None:
    path = Path("scripts/genesis/repo_alignment_check.py")
    spec = importlib.util.spec_from_file_location("repo_alignment_check", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.main() == 0
    report = Path("reports/genesis/repo_alignment_check.json")
    assert report.exists()
