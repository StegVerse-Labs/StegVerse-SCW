#!/usr/bin/env python3
"""Folded groups keep their push path filters (python tools/tasks/selection_selftest.py).

A group whose original filter does not match the event's changed files records NOT_SELECTED
(a run, never a skipped job); a group whose filter matches runs its steps.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("run_catalog", ROOT / "tools/tasks/run_catalog.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
CATALOG = json.loads((ROOT / "tools/tasks/task_catalog.json").read_text(encoding="utf-8"))
GROUPS = {g["id"]: g for g in CATALOG["groups"]}


def cell(event, files, gid):
    return [c for c in rc.matrix(event, files)["include"] if c["group"] == gid][0]["selected"]


class GlobTests(unittest.TestCase):
    def test_star_stops_at_slash_and_double_star_does_not(self):
        self.assertTrue(rc.glob_regex("data/*.json").match("data/a.json"))
        self.assertFalse(rc.glob_regex("data/*.json").match("data/x/a.json"))
        self.assertTrue(rc.glob_regex("data/**").match("data/x/y/a.json"))
        self.assertTrue(rc.glob_regex("**/a.json").match("a.json"))

    def test_later_negation_removes_an_earlier_match(self):
        self.assertFalse(rc.path_matches(["docs/**", "!docs/skip.md"], "docs/skip.md"))

    def test_paths_ignore_runs_unless_every_file_is_ignored(self):
        filt = {"paths_ignore": ["docs/**"]}
        self.assertFalse(rc.filter_selects(filt, ["docs/a.md"]))
        self.assertTrue(rc.filter_selects(filt, ["docs/a.md", "src/a.py"]))

    def test_unknown_changed_files_select_everything(self):
        self.assertTrue(rc.filter_selects({"paths": ["only/this"]}, None))


class GroupSelectionTests(unittest.TestCase):
    def test_hcb_group_runs_only_when_its_original_paths_change(self):
        gid = "hcb-pipeline.smoke"
        self.assertEqual(cell("push", ["README.md"], gid), "false")
        self.assertEqual(cell("push", ["hybrid-collab-bridge/api/app/main.py"], gid), "true")
        self.assertEqual(cell("push", [f"tools/tasks/steps/{gid}/01-x.sh"], gid), "true")
        self.assertEqual(cell("push", None, gid), "true")

    def test_groups_without_a_pull_request_filter_always_run_on_pull_requests(self):
        for gid, group in GROUPS.items():
            filters = group.get("path_filters") or {}
            if "pull_request" in group["events"] and "pull_request" not in filters:
                self.assertEqual(cell("pull_request", ["README.md"], gid), "true", gid)

    def test_every_filtered_group_is_selected_by_each_of_its_own_literal_paths(self):
        for gid, group in GROUPS.items():
            for event, filt in (group.get("path_filters") or {}).items():
                for pattern in filt.get("paths", []):
                    if pattern.startswith("!") or any(ch in pattern for ch in "*?+["):
                        continue
                    self.assertEqual(cell(event, [pattern], gid), "true", (gid, event, pattern))

    def test_filters_match_the_folded_originals(self):
        try:
            import yaml
        except ImportError:
            return
        for gid, group in GROUPS.items():
            wf = Path((group.get("source") or {}).get("workflow", "")).name
            original = ROOT / "tools/tasks/folded" / wf
            if not wf or not original.is_file():
                continue
            doc = yaml.safe_load(original.read_text(encoding="utf-8"))
            on = doc.get(True, doc.get("on")) or {}
            for event in group["events"]:
                cfg = on.get(event) if isinstance(on, dict) else None
                has = bool(isinstance(cfg, dict) and (cfg.get("paths") or cfg.get("paths-ignore")))
                self.assertEqual(has, event in (group.get("path_filters") or {}), (gid, event))


if __name__ == "__main__":
    unittest.main()
