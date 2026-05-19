"""Tests for scripts/generate_available_json.py -- the download manifest generator."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from generate_available_json import build_manifest, check_manifest, dumps  # noqa: E402


def _manifest(cultures: list[dict]) -> dict:
    return {
        "schemaVersion": 1,
        "release": "v1",
        "downloadBase": "https://example/",
        "cultures": cultures,
    }


def _culture(**over) -> dict:
    base = {
        "id": "x", "name": "X", "region": "europe", "asset": "a.zip",
        "anchor": {"type": "region", "iso": "DE"}, "parent": None,
    }
    base.update(over)
    return base


class TestBuildManifest:
    def test_top_level_shape(self):
        m = build_manifest("v1.2.3")
        assert m["schemaVersion"] == 1
        assert m["release"] == "v1.2.3"
        assert m["downloadBase"].startswith("https://") and m["downloadBase"].endswith("/")
        assert isinstance(m["cultures"], list) and m["cultures"]

    def test_culture_entry_shape(self):
        for c in build_manifest("v1")["cultures"]:
            assert set(c) == {"id", "name", "region", "asset", "anchor", "parent"}
            assert re.match(r"^[a-z0-9-]+$", c["id"]), c["id"]
            assert c["anchor"]["type"] in ("region", "marker")

    def test_live_registry_is_clean(self):
        """The real data/countries.json must project to a problem-free manifest."""
        assert check_manifest(build_manifest("v1")) == []


class TestCheckManifest:
    def test_bad_id_flagged(self):
        bad = _manifest([_culture(id="South_Africa")])
        assert any("violates" in p for p in check_manifest(bad))

    def test_duplicate_id_flagged(self):
        m = _manifest([_culture(id="x"), _culture(id="x")])
        assert any("duplicate" in p for p in check_manifest(m))

    def test_bad_region_flagged(self):
        m = _manifest([_culture(region="atlantis")])
        assert any("region" in p for p in check_manifest(m))

    def test_bad_iso_flagged(self):
        m = _manifest([_culture(anchor={"type": "region", "iso": "de"})])
        assert any("iso" in p for p in check_manifest(m))

    def test_clean_manifest_no_problems(self):
        assert check_manifest(_manifest([_culture()])) == []


class TestDumps:
    def test_region_anchor_on_one_line(self):
        assert '{ "type": "region", "iso": "DE" }' in dumps(_manifest([_culture()]))

    def test_round_trips_to_valid_json(self):
        m = build_manifest("v1")
        assert json.loads(dumps(m)) == m

    def test_trailing_newline(self):
        assert dumps(_manifest([_culture()])).endswith("\n")
