import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "genesis" / "guardian_repo_alignment_check.py"
SPEC = importlib.util.spec_from_file_location("guardian_repo_alignment_check", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def write_config(path: Path) -> None:
    path.write_text(
        """version: 3
targets:
  - repo: StegVerse-Labs/example
required_files:
  - required.txt
required_workflows: []
optional_checks:
  ensure_workflow_dispatch: true
""",
        encoding="utf-8",
    )


def write_repo(root: Path) -> None:
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / "required.txt").write_text("ok\n", encoding="utf-8")
    (root / ".github" / "workflows" / "check.yml").write_text(
        "on:\n  workflow_dispatch: {}\n", encoding="utf-8"
    )


def test_run_uses_exact_local_materialization_without_credentials(tmp_path, monkeypatch):
    config = tmp_path / "config.yml"
    write_config(config)
    repo = tmp_path / "materialized" / "example"
    write_repo(repo)
    manifest = tmp_path / "materialization.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": MODULE.MANIFEST_SCHEMA,
                "targets": [
                    {
                        "repo": "StegVerse-Labs/example",
                        "source_sha": "a" * 40,
                        "path": str(repo),
                        "receipt_ref": "receipt://example/a",
                        "authority": "TV/TVC",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("GITHUB_TOKEN", "must-not-be-consumed")
    out_dir = tmp_path / "out"

    payload = MODULE.run(config, manifest, out_dir)

    assert payload["summary"]["repos_pass"] == 1
    assert payload["results"][0]["source_sha"] == "a" * 40
    assert payload["results"][0]["materialization_receipt_ref"] == "receipt://example/a"
    assert (out_dir / "repo_alignment_latest.json").is_file()
    assert (out_dir / "repo_alignment_latest.md").is_file()


def test_manifest_rejects_secret_bearing_fields(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = tmp_path / "materialization.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": MODULE.MANIFEST_SCHEMA,
                "targets": [
                    {
                        "repo": "StegVerse-Labs/example",
                        "source_sha": "b" * 40,
                        "path": str(repo),
                        "receipt_ref": "receipt://example/b",
                        "authority": "TV/TVC",
                        "github_token": "forbidden",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="secret-bearing field prohibited"):
        MODULE.load_materialization_manifest(manifest)


def test_manifest_requires_all_configured_targets(tmp_path):
    config = tmp_path / "config.yml"
    write_config(config)
    manifest = tmp_path / "materialization.json"
    other_repo = tmp_path / "other"
    other_repo.mkdir()
    manifest.write_text(
        json.dumps(
            {
                "schema": MODULE.MANIFEST_SCHEMA,
                "targets": [
                    {
                        "repo": "StegVerse-Labs/other",
                        "source_sha": "c" * 40,
                        "path": str(other_repo),
                        "receipt_ref": "receipt://other/c",
                        "authority": "TV/TVC",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing configured targets"):
        MODULE.run(config, manifest, tmp_path / "out")
