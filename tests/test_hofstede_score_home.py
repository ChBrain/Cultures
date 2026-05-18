"""Single-home gate for Hofstede dimension scores.

`data/hofstede_scores.json` is the single source of truth for Hofstede
cultural-dimension scores. This test asserts that no other in-repo copy has
drifted from it.

  - Every `regions/*/*/hofstede_bag.yaml` that still carries a
    `hofstede_scores` block must have that block equal to the home entry
    for its country.

A bag whose score block has been removed (single-home migration, done one
country at a time) is skipped here: the home becomes its only score source,
and the README score table stays covered by `tests/test_hofstede_reference.py`.
Once every bag has dropped the block, this test has nothing left to check
and can be retired.

Also sanity-checks the source catalog, `data/hofstede_sources.yaml`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parent.parent
_HOME = _ROOT / "data" / "hofstede_scores.json"
_CATALOG = _ROOT / "data" / "hofstede_sources.yaml"

_DIMS = ("PDI", "IDV", "UAI", "MAS", "LTO", "IND")


def _home_scores() -> dict[str, dict]:
    return json.loads(_HOME.read_text(encoding="utf-8"))["scores"]


def _bags_with_score_block() -> list[Path]:
    out: list[Path] = []
    for bag in sorted(_ROOT.glob("regions/*/*/hofstede_bag.yaml")):
        data = yaml.safe_load(bag.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict) and "hofstede_scores" in data:
            out.append(bag)
    return out


_BAGS = _bags_with_score_block()


@pytest.mark.parametrize(
    "bag_path",
    _BAGS or [None],
    ids=[b.parent.name for b in _BAGS] or ["none"],
)
def test_bag_score_block_matches_home(bag_path):
    if bag_path is None:
        pytest.skip(
            "no hofstede_bag.yaml carries a hofstede_scores block "
            "(single-home migration complete)"
        )

    country = bag_path.parent.name
    home = _home_scores()
    assert country in home, (
        f"{country}: bag carries a hofstede_scores block but the country has "
        f"no entry in {_HOME.name}"
    )

    bag_block = yaml.safe_load(bag_path.read_text(encoding="utf-8"))["hofstede_scores"]
    bag_six = {d: bag_block.get(d) for d in _DIMS}
    home_six = {d: home[country].get(d) for d in _DIMS}
    assert bag_six == home_six, (
        f"{country}: hofstede_bag.yaml score block {bag_six} has drifted from "
        f"the home {_HOME.name} {home_six}. The home is the single source of "
        f"truth - correct the bag, or migrate the country (drop the block)."
    )


def test_source_catalog_well_formed():
    if not _CATALOG.is_file():
        pytest.skip(
            "data/hofstede_sources.yaml not present yet "
            "(added in a companion chore PR)"
        )
    catalog = yaml.safe_load(_CATALOG.read_text(encoding="utf-8"))
    assert isinstance(catalog, dict) and isinstance(catalog.get("sources"), dict), (
        f"{_CATALOG.name}: must have a top-level 'sources' mapping"
    )
    valid_kinds = {"empirical", "cluster", "estimate"}
    for sid, meta in catalog["sources"].items():
        assert isinstance(meta.get("priority"), int), (
            f"{sid}: 'priority' must be an integer"
        )
        assert meta.get("kind") in valid_kinds, (
            f"{sid}: 'kind' must be one of {sorted(valid_kinds)}"
        )
        for field in ("label", "rights_holder", "usage"):
            assert meta.get(field), f"{sid}: missing required field '{field}'"
