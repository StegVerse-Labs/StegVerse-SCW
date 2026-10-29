"""AutoPatch runner must never remove or rewrite manifest entries (StegVerse-org/.github#166)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[1] / "scripts" / "autopatch_runner.py"

MANIFEST = """version: 1
patches:
  - id: already-there
    path: keep/exists.txt
    mode: ensure
  - id: blocked-one
    path: keep/blocked.txt
    mode: ensure
    requires_files: [no/such/file]
  - id: errored-one
    mode: ensure
  - just-a-bare-string
"""


def _run(tmp: Path, *extra: str):
    return subprocess.run(
        [sys.executable, "scripts/autopatch_runner.py", "--manifest", ".github/autopatch/patches.yml", *extra],
        cwd=tmp, capture_output=True, text=True,
    )


def _tree(tmp: Path, manifest: str) -> None:
    (tmp / "scripts").mkdir()
    shutil.copy(RUNNER, tmp / "scripts" / "autopatch_runner.py")
    (tmp / ".github" / "autopatch").mkdir(parents=True)
    (tmp / ".github" / "autopatch" / "patches.yml").write_text(manifest, encoding="utf-8")
    (tmp / "keep").mkdir()
    (tmp / "keep" / "exists.txt").write_text("x", encoding="utf-8")


def test_prune_and_defer_never_remove_entries(tmp_path):
    _tree(tmp_path, MANIFEST)
    before = (tmp_path / ".github/autopatch/patches.yml").read_bytes()
    r = _run(tmp_path, "--prune-success", "--defer-file", ".github/autopatch/patches_deferred.yml")
    assert r.returncode == 0, r.stderr
    assert (tmp_path / ".github/autopatch/patches.yml").read_bytes() == before
    rep = json.loads((tmp_path / "self_healing_out/AUTOPATCH_REPORT.json").read_text())
    assert rep["manifest_rewritten"] is False
    assert len(rep["items"]) == 4
    assert all(i["retained"] for i in rep["items"])
    assert rep["summary"]["noop"] == 1 and rep["summary"]["blocked"] == 1 and rep["summary"]["error"] == 2
    deferred = (tmp_path / ".github/autopatch/patches_deferred.yml").read_text()
    assert "blocked-one" in deferred and "errored-one" in deferred
    # a second run adds no duplicates
    _run(tmp_path, "--prune-success", "--defer-file", ".github/autopatch/patches_deferred.yml")
    assert (tmp_path / ".github/autopatch/patches_deferred.yml").read_text() == deferred


def test_invalid_manifest_is_reported_and_left_unchanged(tmp_path):
    bad = "patches:\n  - bare\n    - id: x\n  path: y\n"
    _tree(tmp_path, bad)
    r = _run(tmp_path, "--prune-success")
    assert r.returncode == 0, r.stderr
    assert (tmp_path / ".github/autopatch/patches.yml").read_text() == bad
    rep = json.loads((tmp_path / "self_healing_out/AUTOPATCH_REPORT.json").read_text())
    assert rep["invalid_manifest"]
    assert rep["manifest_rewritten"] is False
