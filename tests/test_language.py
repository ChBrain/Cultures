"""Cultures language policy -- static checks.

Tests the Cultures-specific layer:
  - data/language_policy.yaml is present and well-formed
  - every country README declares a language slug that is in the registry
  - per-culture exception files (language_exceptions.txt), if present, are valid

Per-file language detection (requires lingua) is handled by the
khai-language CI job via khai_tests.test_khai_language.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
POLICY_PATH = ROOT / "data" / "language_policy.yaml"

sys.path.insert(0, str(HERE))
import validate_language  # noqa: E402

_LANG_LINE_RE = re.compile(r"^\*\*Language\(s\):\*\*\s*(.+)$", re.MULTILINE)


def _load_policy() -> dict:
    raw = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8")) or {}
    return {
        "languages": [s.lower() for s in (raw.get("languages") or [])],
        "prose_sections": {s.lower() for s in (raw.get("prose_sections") or [])},
        "min_span_words": raw.get("min_span_words", 3),
    }


def _country_dirs() -> list[Path]:
    regions = ROOT / "regions"
    out = []
    for region in sorted(regions.iterdir()):
        if not region.is_dir() or region.name.startswith("."):
            continue
        for country in sorted(region.iterdir()):
            if not country.is_dir() or country.name.startswith("."):
                continue
            if (country / "README.md").is_file():
                out.append(country)
    return out


_COUNTRIES = _country_dirs()


# ---------------------------------------------------------------------------
# Policy structure
# ---------------------------------------------------------------------------

def test_policy_file_exists():
    assert POLICY_PATH.is_file(), "data/language_policy.yaml missing"


def test_policy_has_languages():
    assert _load_policy()["languages"], "languages list is empty"


def test_policy_has_prose_sections():
    assert _load_policy()["prose_sections"], "prose_sections list is empty"


def test_policy_min_span_words_positive():
    min_words = _load_policy()["min_span_words"]
    assert isinstance(min_words, int) and min_words >= 1, (
        f"min_span_words must be a positive integer, got {min_words!r}"
    )


# ---------------------------------------------------------------------------
# README language declarations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_readme_declares_language(country_dir: Path):
    readme = (country_dir / "README.md").read_text(encoding="utf-8")
    assert _LANG_LINE_RE.search(readme), (
        f"{country_dir.name}/README.md has no **Language(s):** line"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_readme_language_in_registry(country_dir: Path):
    policy = _load_policy()
    readme = (country_dir / "README.md").read_text(encoding="utf-8")
    m = _LANG_LINE_RE.search(readme)
    if not m:
        pytest.skip("no Language(s) line -- covered by test_readme_declares_language")
    declared = [
        chunk.split("(")[0].strip().lower()
        for chunk in m.group(1).split(",")
        if chunk.split("(")[0].strip()
    ]
    unknown = [lang for lang in declared if lang not in policy["languages"]]
    assert not unknown, (
        f"{country_dir.name}/README.md declares unknown language(s): {unknown}\n"
        f"  registered: {policy['languages']}"
    )


# ---------------------------------------------------------------------------
# Per-culture exception files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_culture_exception_file_valid(country_dir: Path):
    exc_file = country_dir / "language_exceptions.txt"
    if not exc_file.is_file():
        pytest.skip("no per-culture exception file")
    lines = exc_file.read_text(encoding="utf-8").splitlines()
    entries = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
    assert entries, (
        f"{country_dir.name}/language_exceptions.txt exists but contains no entries "
        f"(add at least one word, or delete the file)"
    )


# ---------------------------------------------------------------------
# Country language unlock gate
# ---------------------------------------------------------------------
# data/countries.json is the data home for a country's language; this gate
# blocks culture work on a country whose language is not unlocked (its ISO
# code maps, via iso_map, onto a registered lingua name).

_VL_POLICY = validate_language.load_policy()
_COUNTRY_IDS = sorted(
    c["id"] for c in validate_language.load_countries() if c.get("id")
)


def test_iso_map_present():
    assert _VL_POLICY["iso_map"], (
        "data/language_policy.yaml: `iso_map` is empty -- no country "
        "language can be unlocked"
    )


def test_iso_map_values_registered():
    registry = set(_VL_POLICY["languages"])
    unregistered = {
        iso: name for iso, name in _VL_POLICY["iso_map"].items()
        if name not in registry
    }
    assert not unregistered, (
        f"iso_map values not in `languages`: {unregistered}"
    )


@pytest.mark.parametrize("country_id", _COUNTRY_IDS)
def test_country_language_unlocked(country_id: str):
    issues = validate_language.country_language_unlocked_violations(
        _VL_POLICY, {country_id}
    )
    assert not issues, "\n".join(i.error for i in issues)


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_readme_language_matches_registry(country_dir: Path):
    """A README's declared language must match data/countries.json.

    Cross-checks the hand-written `**Language(s):**` line against the
    country's ISO code resolved through iso_map -- catches drift between
    the data home and the human-readable declaration.
    """
    entry = next(
        (c for c in validate_language.load_countries()
         if c.get("id") == country_dir.name),
        None,
    )
    if entry is None:
        pytest.skip("country not in data/countries.json")
    iso = str(entry.get("language") or "").strip().lower()
    expected = _VL_POLICY["iso_map"].get(iso)
    if expected is None:
        pytest.skip("language not unlocked -- caught by test_country_language_unlocked")
    declared = validate_language.parse_readme_languages(
        (country_dir / "README.md").read_text(encoding="utf-8")
    )
    if not declared:
        pytest.skip("no Language(s) line -- caught by test_readme_declares_language")
    assert expected in declared, (
        f"{country_dir.name}/README.md declares {declared}, but "
        f"data/countries.json says language={iso!r} ({expected!r})"
    )
