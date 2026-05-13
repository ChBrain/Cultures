"""Unit tests for data/hofstede_bag_loader.py.

Pin every branch of the loader's behaviour:
- Per-country bag found and parses cleanly -> return it.
- Bag absent, country not locked -> fall back to legacy.
- Bag absent, country LOCKED -> RuntimeError (loud).
- Bag malformed YAML, country not locked -> stderr warning + legacy fallback.
- Bag malformed, country LOCKED -> RuntimeError (loud).
- Bag schema invalid -> BagLoadError surfaces as RuntimeError under lock,
  warning + fallback otherwise.
- Both `hofstede_bag.yaml` and `hofstede_bag_<lang>.yaml` present ->
  language-specific wins, warning emitted.
- `fallback=False` and no bag -> ValueError.

Run: python -m pytest tests/test_hofstede_bag_loader.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data import hofstede_bag_loader as loader  # noqa: E402


VALID_BAG_YAML = """\
country: testland
language: nl
parent: null
hofstede_scores:
  PDI: 38
  IDV: 80
  UAI: 53
  MAS: 14
  LTO: 67
  IND: 68
bags:
  PDI:
    high: [a, b, c, d, e, f, g, h, i, j]
    low:  [k, l, m, n, o, p, q, r, s, t]
  IDV:
    high: [a1, b1, c1, d1, e1, f1, g1, h1, i1, j1]
    low:  [k1, l1, m1, n1, o1, p1, q1, r1, s1, t1]
  UAI:
    high: [a2, b2, c2, d2, e2, f2, g2, h2, i2, j2]
    low:  [k2, l2, m2, n2, o2, p2, q2, r2, s2, t2]
  MAS:
    high: [a3, b3, c3, d3, e3, f3, g3, h3, i3, j3]
    low:  [k3, l3, m3, n3, o3, p3, q3, r3, s3, t3]
  LTO:
    high: [a4, b4, c4, d4, e4, f4, g4, h4, i4, j4]
    low:  [k4, l4, m4, n4, o4, p4, q4, r4, s4, t4]
  IND:
    high: [a5, b5, c5, d5, e5, f5, g5, h5, i5, j5]
    low:  [k5, l5, m5, n5, o5, p5, q5, r5, s5, t5]
"""

# Sentinel legacy dict; tests check identity against this to assert fallback.
SENTINEL_LEGACY = {
    "nl": {
        "PDI": {"high": ["legacy_nl_pdi_high"], "low": ["legacy_nl_pdi_low"]},
        "IDV": {"high": [], "low": []},
        "UAI": {"high": [], "low": []},
        "MAS": {"high": [], "low": []},
        "LTO": {"high": [], "low": []},
        "IND": {"high": [], "low": []},
    },
    "en": {
        "PDI": {"high": ["legacy_en"], "low": []},
        "IDV": {"high": [], "low": []},
        "UAI": {"high": [], "low": []},
        "MAS": {"high": [], "low": []},
        "LTO": {"high": [], "low": []},
        "IND": {"high": [], "low": []},
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def loader_env(tmp_path, monkeypatch):
    """Isolated repo root with a testland country folder and patched loader."""
    repo = tmp_path
    (repo / "regions" / "europe" / "testland").mkdir(parents=True)
    (repo / "data").mkdir()
    monkeypatch.setattr(loader, "_REPO_ROOT", repo)
    monkeypatch.setattr(loader, "_LOCKS_FILE", repo / "data" / "hofstede_bag_locks.yaml")
    monkeypatch.setattr(loader, "DIMENSION_KEYWORDS_BY_LANGUAGE", SENTINEL_LEGACY)
    return repo


@pytest.fixture
def country_folder(loader_env):
    return loader_env / "regions" / "europe" / "testland"


# ---------------------------------------------------------------------------
# Helpers (plain functions -- take paths, no self)
# ---------------------------------------------------------------------------

def write_bag(folder: Path, *, language: str | None = None, content: str = VALID_BAG_YAML):
    name = f"hofstede_bag_{language}.yaml" if language else "hofstede_bag.yaml"
    (folder / name).write_text(content, encoding="utf-8")


def write_lock(
    env: Path,
    country_path: str = "regions/europe/testland/hofstede_bag.yaml",
):
    loader._LOCKS_FILE.write_text(
        f"locks:\n  {country_path}: dummy_sha\n", encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

def test_loads_generic_bag(country_folder):
    write_bag(country_folder)
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag["PDI"]["high"][0] == "a"
    assert bag != SENTINEL_LEGACY["nl"]


def test_loads_language_specific_bag(country_folder):
    write_bag(country_folder, language="nl")
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag["PDI"]["high"][0] == "a"


def test_lang_specific_wins_over_generic_with_warning(country_folder, capsys):
    write_bag(country_folder)
    write_bag(country_folder, language="nl")
    loader.load_bag_for_language("nl", country_folder=country_folder)
    err = capsys.readouterr().err
    assert "both" in err
    assert "hofstede_bag_nl.yaml" in err


# ---------------------------------------------------------------------------
# Fallback -- unlocked country
# ---------------------------------------------------------------------------

def test_no_bag_unlocked_falls_back_silently(country_folder, capsys):
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["nl"]
    assert capsys.readouterr().err == ""


def test_no_bag_unknown_language_falls_back_to_english(country_folder):
    bag = loader.load_bag_for_language("xx", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["en"]


def test_no_bag_fallback_false_raises(country_folder):
    with pytest.raises(ValueError):
        loader.load_bag_for_language("nl", country_folder=country_folder, fallback=False)


# ---------------------------------------------------------------------------
# Malformed bag -- unlocked (warn + fallback, never silent)
# ---------------------------------------------------------------------------

def test_yaml_parse_error_warns_and_falls_back(country_folder, capsys):
    write_bag(country_folder, content=":\n: malformed: : :\n")
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["nl"]
    assert "WARNING" in capsys.readouterr().err


def test_missing_bags_key_warns_and_falls_back(country_folder, capsys):
    write_bag(country_folder, content="country: testland\nlanguage: nl\n")
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["nl"]
    assert "missing top-level" in capsys.readouterr().err


def test_schema_invalid_warns_and_falls_back(country_folder, capsys):
    write_bag(country_folder, content=(
        "bags:\n"
        "  PDI:\n"
        "    high: not_a_list\n"
        "    low: []\n"
    ))
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["nl"]
    assert "WARNING" in capsys.readouterr().err


def test_missing_dimension_warns_and_falls_back(country_folder, capsys):
    broken = VALID_BAG_YAML.replace(
        "  IND:\n"
        "    high: [a5, b5, c5, d5, e5, f5, g5, h5, i5, j5]\n"
        "    low:  [k5, l5, m5, n5, o5, p5, q5, r5, s5, t5]\n",
        "",
    )
    write_bag(country_folder, content=broken)
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["nl"]
    assert "missing dimension" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Locked country -- fails loud
# ---------------------------------------------------------------------------

def test_locked_with_missing_bag_raises(loader_env, country_folder):
    write_lock(loader_env)
    with pytest.raises(RuntimeError, match="(?i)missing"):
        loader.load_bag_for_language("nl", country_folder=country_folder)


def test_locked_with_malformed_yaml_raises(loader_env, country_folder):
    write_lock(loader_env)
    write_bag(country_folder, content=":\n: malformed: : :\n")
    with pytest.raises(RuntimeError, match="(?i)malformed"):
        loader.load_bag_for_language("nl", country_folder=country_folder)


def test_locked_with_schema_violation_raises(loader_env, country_folder):
    write_lock(loader_env)
    write_bag(country_folder, content="bags: not_a_dict\n")
    with pytest.raises(RuntimeError, match="(?i)malformed"):
        loader.load_bag_for_language("nl", country_folder=country_folder)


def test_locked_with_valid_bag_loads_normally(loader_env, country_folder):
    write_lock(loader_env)
    write_bag(country_folder)
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag["PDI"]["high"][0] == "a"


def test_unrelated_lock_entries_do_not_affect_unlocked_country(loader_env, country_folder):
    """Lock entries for other countries must not affect this country."""
    loader._LOCKS_FILE.write_text(
        "locks:\n"
        "  regions/europe/somewhere_else/hofstede_bag.yaml: deadbeef\n",
        encoding="utf-8",
    )
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["nl"]


# ---------------------------------------------------------------------------
# load_bag_for_country_file (file-path entry point)
# ---------------------------------------------------------------------------

def test_load_by_file_finds_country_folder(loader_env, country_folder):
    write_bag(country_folder)
    culture_md = country_folder / "culture_test_position.md"
    culture_md.write_text("# test\n")
    bag = loader.load_bag_for_country_file(culture_md, "nl")
    assert bag["PDI"]["high"][0] == "a"


def test_load_by_file_outside_regions_falls_back(loader_env):
    random_path = loader_env / "data" / "hofstede_keywords.py"
    random_path.write_text("# placeholder\n")
    bag = loader.load_bag_for_country_file(random_path, "nl")
    assert bag == SENTINEL_LEGACY["nl"]


# ---------------------------------------------------------------------------
# Lock index edge cases
# ---------------------------------------------------------------------------

def test_no_lock_file_treated_as_empty(country_folder):
    write_bag(country_folder)
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag["PDI"]["high"][0] == "a"


def test_malformed_lock_file_warns_and_treats_as_empty(loader_env, country_folder, capsys):
    loader._LOCKS_FILE.write_text(":\n: : :\n", encoding="utf-8")
    bag = loader.load_bag_for_language("nl", country_folder=country_folder)
    assert bag == SENTINEL_LEGACY["nl"]
    assert "hofstede_bag_locks.yaml" in capsys.readouterr().err
