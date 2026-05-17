"""Metadata-format guard for the footer -> YAML-frontmatter migration.

Keeps a dirty (partial) migration safe. Per country, over every
``culture_*.md`` file:

  A. No file carries BOTH a YAML frontmatter block and a trailing
     metadata footer -- that ambiguity is rejected outright.
  B. Frontmatter is all-or-nothing within a country: once any
     ``culture_*.md`` is frontmatter, every one must be. A country
     migrates as a unit; a half-converted country fails here.

Legacy footer/none variation inside an unmigrated country is left alone
-- this guard governs only the footer -> frontmatter transition, not
pre-existing v1 shape.

Run: python -m pytest tests/test_metadata_format.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

from culture_metadata import format_of, strip_metadata  # noqa: E402


def _country_dirs() -> list[Path]:
    """Every regions/<region>/<country>/ folder that holds culture_*.md files."""
    regions = _ROOT / "regions"
    if not regions.is_dir():
        return []
    return sorted(
        country
        for region in sorted(regions.iterdir()) if region.is_dir()
        for country in sorted(region.iterdir())
        if country.is_dir() and any(country.glob("culture_*.md"))
    )


_COUNTRIES = _country_dirs()


def _has_both_blocks(text: str) -> bool:
    """True if ``text`` carries a frontmatter block AND a trailing footer."""
    if format_of(text) != "frontmatter":
        return False
    return format_of(strip_metadata(text)) == "footer"


@pytest.mark.parametrize("country", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_no_double_metadata(country: Path):
    """Rule A: no file carries both a frontmatter block and a footer."""
    bad = [
        f.name for f in sorted(country.glob("culture_*.md"))
        if _has_both_blocks(f.read_text(encoding="utf-8", errors="replace"))
    ]
    assert not bad, (
        f"{country.name}: these files carry BOTH frontmatter and a trailing "
        f"footer -- delete the footer, keep the frontmatter: {bad}"
    )


@pytest.mark.parametrize("country", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_frontmatter_is_all_or_nothing(country: Path):
    """Rule B: a country migrates to frontmatter as a unit, never half-and-half."""
    frontmatter: list[str] = []
    other: list[str] = []
    for f in sorted(country.glob("culture_*.md")):
        fmt = format_of(f.read_text(encoding="utf-8", errors="replace"))
        (frontmatter if fmt == "frontmatter" else other).append(f.name)
    if frontmatter and other:
        pytest.fail(
            f"{country.name}: metadata format is mixed -- a country migrates "
            f"to frontmatter as a unit.\n"
            f"  frontmatter: {frontmatter}\n"
            f"  not yet converted: {other}"
        )
