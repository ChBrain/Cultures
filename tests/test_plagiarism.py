"""Cultures-specific plagiarism structural checks.

Two surfaces:
- Phrase denylist hygiene: data/phrase_denylist.txt exists and is well-formed.
  The actual per-file phrase matching runs in khai-plagiarism (KAIHACKS
  test_khai_plagiarism.py). These tests only verify the list itself is valid.
- REFERENCES.md presence: every country directory must document its sources.

Independence: no imports from validate_plagiarism.py.
"""
from __future__ import annotations

from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

_DENYLIST_PATH = ROOT / "data" / "phrase_denylist.txt"


def _load_phrases() -> list[str]:
    if not _DENYLIST_PATH.is_file():
        return []
    return [
        line.strip().lower()
        for line in _DENYLIST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _country_dirs() -> list[Path]:
    regions = ROOT / "regions"
    if not regions.is_dir():
        return []
    return sorted(
        country
        for region in regions.iterdir()
        if region.is_dir() and not region.name.startswith(".")
        for country in region.iterdir()
        if country.is_dir() and not country.name.startswith(".")
        and (country / "README.md").is_file()
    )


_COUNTRIES = _country_dirs()


# ---------------------------------------------------------------------------
# Phrase denylist structural checks
# ---------------------------------------------------------------------------

def test_phrase_denylist_exists():
    """data/phrase_denylist.txt must exist to activate khai-plagiarism opt-in."""
    assert _DENYLIST_PATH.is_file(), (
        "data/phrase_denylist.txt missing -- "
        "create it (even empty) to activate the phrase detection opt-in"
    )


def test_phrase_denylist_min_word_count():
    """All active phrases must be 7+ words to avoid false positives on common language."""
    phrases = _load_phrases()
    if not phrases:
        pytest.skip("no active phrases in denylist")
    short = [p for p in phrases if len(p.split()) < 7]
    assert not short, (
        "phrases shorter than 7 words fire too broadly -- rephrase or remove:\n"
        + "\n".join(f"  '{p}'  ({len(p.split())} words)" for p in short)
    )


def test_phrase_denylist_no_duplicates():
    """Duplicate phrases waste match time and indicate copy-paste errors."""
    phrases = _load_phrases()
    if not phrases:
        pytest.skip("no active phrases in denylist")
    seen: set[str] = set()
    dupes = []
    for p in phrases:
        if p in seen:
            dupes.append(p)
        seen.add(p)
    assert not dupes, (
        "duplicate phrases in denylist:\n"
        + "\n".join(f"  '{p}'" for p in dupes)
    )


# ---------------------------------------------------------------------------
# Per-country REFERENCES.md structural check
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[d.name for d in _COUNTRIES])
def test_references_md_exists(country_dir: Path):
    """Every country with a README must document its sources in REFERENCES.md."""
    ref = country_dir / "REFERENCES.md"
    assert ref.is_file(), (
        f"{country_dir.name}/REFERENCES.md missing -- "
        f"create it with the source registry and paraphrase notes"
    )
