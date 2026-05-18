"""Tests for scripts/check_release_gating.py -- the release gating check."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_release_gating import (  # noqa: E402
    check_anchor, check_country, load_registry,
)

_GOOD = {
    "id": "germany",
    "name": "Germany",
    "region": "europe",
    "asset": "cultures-europe-germany.zip",
    "anchor": {"type": "region", "iso": "DE"},
    "language": "de",
    "name_source": "DESTATIS_DE_2023",
}


class TestRealRegistry:
    """The check must pass against the live countries.json."""

    def test_every_registered_country_is_complete(self):
        reg = load_registry()
        assert reg, "countries.json registry is empty"
        for slug in reg:
            orders = check_country(slug, reg)
            assert orders == [], (
                f"{slug}: registry entry incomplete:\n" + "\n".join(orders)
            )


class TestCheckCountry:
    def test_unregistered_country_fails(self):
        orders = check_country("atlantis", {})
        assert len(orders) == 1
        assert "registry-presence" in orders[0]
        assert "not in data/countries.json" in orders[0]

    def test_complete_entry_passes(self):
        assert check_country("germany", {"germany": _GOOD}) == []

    def test_placeholder_field_fails(self):
        bad = {**_GOOD, "name_source": "TODO"}
        orders = check_country("germany", {"germany": bad})
        assert any("registry-completeness" in o and "name_source" in o for o in orders)

    def test_missing_field_fails(self):
        bad = {k: v for k, v in _GOOD.items() if k != "asset"}
        orders = check_country("germany", {"germany": bad})
        assert any("'asset'" in o for o in orders)

    def test_bad_region_fails(self):
        bad = {**_GOOD, "region": "atlantis"}
        orders = check_country("germany", {"germany": bad})
        assert any("region" in o for o in orders)


class TestCheckAnchor:
    def test_region_anchor_ok(self):
        assert check_anchor("x", {"type": "region", "iso": "DE"}) == []

    def test_marker_anchor_ok(self):
        assert check_anchor("x", {"type": "marker", "coords": [41.9, 12.45]}) == []

    def test_region_anchor_lowercase_iso_fails(self):
        assert check_anchor("x", {"type": "region", "iso": "de"})

    def test_region_anchor_missing_iso_fails(self):
        assert check_anchor("x", {"type": "region"})

    def test_marker_anchor_bad_coords_fails(self):
        assert check_anchor("x", {"type": "marker", "coords": [1]})
        assert check_anchor("x", {"type": "marker"})

    def test_unknown_anchor_type_fails(self):
        assert check_anchor("x", {"type": "blob"})

    def test_non_dict_anchor_fails(self):
        assert check_anchor("x", "DE")

    def test_work_order_carries_all_parts(self):
        order = check_anchor("x", {"type": "blob"})[0]
        for label in ("entity:", "problem:", "fix:", "lane:", "ref:"):
            assert label in order, f"work order missing '{label}':\n{order}"
