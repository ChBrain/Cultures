"""Tests for scripts/generate_country_entry.py -- the registry skeleton generator."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from generate_country_entry import skeleton_entry, _dump_registry  # noqa: E402


class TestSkeletonEntry:
    def test_developed_country(self):
        e = skeleton_entry("germany")
        assert e["id"] == "germany"
        assert e["name"] == "Germany"
        assert e["region"] == "europe"
        assert e["asset"] == "cultures-europe-germany.zip"
        assert e["anchor"] == {"type": "region", "iso": "TODO"}
        assert e["language"] == "de"  # derived from hofstede_bag.yaml
        assert e["name_source"] == "TODO"

    def test_curated_fields_left_as_todo(self):
        e = skeleton_entry("germany")
        assert e["anchor"]["iso"] == "TODO"
        assert e["name_source"] == "TODO"

    def test_multiword_slug_title_cased(self):
        multi = next(
            (d for d in sorted(REPO_ROOT.glob("regions/*/*"))
             if d.is_dir() and "_" in d.name),
            None,
        )
        if multi is None:
            pytest.skip("no multiword country folder in the repo")
        e = skeleton_entry(multi.name)
        assert e["name"] == multi.name.replace("_", " ").title()
        assert e["region"] == multi.parent.name
        assert e["asset"] == f"cultures-{multi.parent.name}-{multi.name}.zip"

    def test_no_folder_raises(self):
        with pytest.raises(ValueError, match="no regions"):
            skeleton_entry("atlantis")


class TestDumpRegistry:
    def test_anchor_collapsed_to_one_line(self):
        data = {"countries": [
            {"id": "x", "anchor": {"type": "region", "iso": "DE"}},
        ]}
        out = _dump_registry(data)
        assert '{ "type": "region", "iso": "DE" }' in out
        assert out.endswith("\n")

    def test_round_trips_valid_json(self):
        data = {"version": "2.0", "countries": [
            {"id": "x", "anchor": {"type": "region", "iso": "TODO"}},
        ]}
        assert json.loads(_dump_registry(data)) == data
