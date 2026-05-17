"""Tests for scripts/validate_history_arc.py + audit on actual culture history files.

Two layers:
- unit tests on synthetic content (does the parser count entries / spans correctly?)
- audit tests across all real culture_*_history_*.md files (do the files in
  the repo respect the methodology?)

CI invokes this file in the L4h-history-arc job in validate.yml. The local
hook calls scripts/validate_history_arc.py directly via scripts/validate.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import validate_history_arc as vha  # noqa: E402


# ---------------------------------------------------------------------------
# Unit tests on synthetic content
# ---------------------------------------------------------------------------

def _make_file(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "culture_test_history_testcountry.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_parse_yearbook_counts_simple_entries(tmp_path):
    body = (
        "# History: Test\n\n"
        "## Yearbook\n"
        "1500: One.\n"
        "1600: Two.\n"
        "1700: Three.\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = _make_file(tmp_path, body)
    years = vha._parse_yearbook(p.read_text())
    assert years == [1500, 1600, 1700]


def test_parse_yearbook_handles_german_era_markers(tmp_path):
    body = (
        "# History: Test\n\n"
        "## Yearbook\n"
        "9 n. Chr.: After-Christ entry.\n"
        "57 v. Chr.: Before-Christ entry.\n"
        "476: Plain.\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = _make_file(tmp_path, body)
    years = vha._parse_yearbook(p.read_text())
    assert years == [9, -57, 476], f"expected [9, -57, 476], got {years}"


def test_parse_yearbook_handles_year_ranges(tmp_path):
    body = (
        "# History: Test\n\n"
        "## Yearbook\n"
        "1940-1945: Occupation period.\n"
        "1795-1813: Batavian period.\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = _make_file(tmp_path, body)
    years = vha._parse_yearbook(p.read_text())
    # Range entries use the first year.
    assert years == [1940, 1795]


def test_parse_yearbook_returns_empty_when_no_yearbook_header(tmp_path):
    body = (
        "# History: Test\n\n"
        "## Place\n"
        "Somewhere.\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = _make_file(tmp_path, body)
    assert vha._parse_yearbook(p.read_text()) == []


def test_validate_file_fails_with_too_few_entries(tmp_path):
    yearbook_lines = "\n".join(f"{1900 + i}: Entry {i}." for i in range(5))
    body = (
        "# History: Test\n\n"
        "## Yearbook\n"
        f"{yearbook_lines}\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = _make_file(tmp_path, body)
    issues = vha.validate_file(p)
    assert any("at least 12" in i.error for i in issues), (
        f"expected 'at least 12' message; got: {[i.error for i in issues]}"
    )


def test_validate_file_fails_with_narrow_span(tmp_path):
    # 12 entries but all within 2 centuries (1900-2024).
    yearbook_lines = "\n".join(f"{1900 + 10 * i}: Entry {i}." for i in range(12))
    body = (
        "# History: Test\n\n"
        "## Yearbook\n"
        f"{yearbook_lines}\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = _make_file(tmp_path, body)
    issues = vha.validate_file(p)
    assert any("centuries" in i.error for i in issues), (
        f"expected 'centuries' message; got: {[i.error for i in issues]}"
    )


def test_validate_file_passes_with_arc(tmp_path):
    # 12 entries spanning 9 AD to 2014 -- the German broad-arc shape.
    yearbook_lines = "\n".join([
        "9 n. Chr.: Varusschlacht.",
        "800: Karl der Große.",
        "1517: Luther in Wittenberg.",
        "1648: Westfälischer Frieden.",
        "1685: Bach geboren.",
        "1810: Beethoven 5.",
        "1919: Weimar.",
        "1949: Grundgesetz.",
        "1954: Wunder von Bern.",
        "1989: Mauerfall.",
        "1990: Wiedervereinigung.",
        "2014: Vierter Stern.",
    ])
    body = (
        "# History: Test\n\n"
        "## Yearbook\n"
        f"{yearbook_lines}\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = _make_file(tmp_path, body)
    # Rename to match the history filename pattern.
    target = tmp_path / "culture_german_history_germany.md"
    target.write_text(body, encoding="utf-8")
    issues = vha.validate_file(target)
    assert issues == [], f"expected no issues; got: {[i.error for i in issues]}"


def test_validate_file_skips_non_history_files(tmp_path):
    body = (
        "# Piece: Something\n\n"
        "## Yearbook\n"
        "1900: One.\n"
        "\n---\n"
        "*khai: piece*\n"
    )
    p = tmp_path / "culture_german_piece_autobahn.md"
    p.write_text(body, encoding="utf-8")
    issues = vha.validate_file(p)
    # Not a history file -> skipped, no issues.
    assert issues == []


def test_validate_file_flags_wrong_khai_declaration(tmp_path):
    body = (
        "# History: Test\n\n"
        "## Yearbook\n"
        "1900: One.\n"
        "\n---\n"
        "*khai: persona*\n"  # wrong declaration for a history file
    )
    p = tmp_path / "culture_test_history_test.md"
    p.write_text(body, encoding="utf-8")
    issues = vha.validate_file(p)
    assert any("must declare khai: piece" in i.error for i in issues), (
        f"expected wrong-declaration message; got: {[i.error for i in issues]}"
    )


# ---------------------------------------------------------------------------
# Audit on actual repo files
# ---------------------------------------------------------------------------

def _all_history_files() -> list[Path]:
    return sorted((ROOT / "regions").rglob("culture_*_history_*.md"))


HISTORY_FILES = _all_history_files()


@pytest.mark.parametrize(
    "history_file",
    HISTORY_FILES,
    ids=[str(p.relative_to(ROOT)) for p in HISTORY_FILES] if HISTORY_FILES else ["(none)"],
)
def test_history_files_pass_arc_methodology(history_file):
    """Every culture_*_history_*.md in the repo must respect the
    defining-moments-arc methodology (khai-cultures-create v0.1.1+):
    12+ Yearbook entries, spanning 5+ centuries, declared *khai: piece*.
    """
    if not HISTORY_FILES:
        pytest.skip("no history files found in regions/**")
    issues = vha.validate_file(history_file)
    assert not issues, "\n".join(i.error for i in issues)
