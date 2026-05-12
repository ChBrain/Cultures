"""Unit tests for tests/validate_hofstede_reference.py.

Pins the reference-comparison contract:

  |declared - reference| <= 5            -> PASS silently
  gap > 5 + dim named in deviation       -> INFO (advisory)
  gap > 5 with no deviation section      -> FAIL

Rewritten from unittest to pytest (Loop G).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from validate_hofstede_reference import (  # noqa: E402
    HOFSTEDE_DIMENSIONS,
    REFERENCE_TOLERANCE,
    deviation_section_body,
    extract_hofstede_scores,
    is_empirical,
    justified_dimensions,
    validate_country,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_REFERENCE_GERMANY = {
    "PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
    "source": "Hofstede Insights - Empirical research",
}


def _readme_with_scores(scores: dict[str, int]) -> str:
    rows = "\n".join(f"| {dim} | {score} | high |" for dim, score in scores.items())
    return f"""# Testland - Culture Content

## Hofstede Cultural Dimensions

| Dimension | Score | Profile |
|---|---|---|
{rows}
"""


def _write_country(root: Path, name: str, readme: str, decisions: str = "") -> Path:
    country = root / "regions" / "europe" / name
    country.mkdir(parents=True)
    (country / "README.md").write_text(readme, encoding="utf-8")
    if decisions:
        (country / "hofstede_decisions.md").write_text(decisions, encoding="utf-8")
    return country


# ---------------------------------------------------------------------------
# extract_hofstede_scores
# ---------------------------------------------------------------------------

def test_extract_parses_pipe_table_rows():
    text = _readme_with_scores({"PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40})
    assert extract_hofstede_scores(text) == {
        "PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
    }


def test_extract_empty_when_no_table():
    assert extract_hofstede_scores("no scores here") == {}


# ---------------------------------------------------------------------------
# is_empirical
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source", [
    "Hofstede Insights - Empirical research",
    "EMPIRICAL data",
    "empirical (recent)",
])
def test_is_empirical_recognized(source):
    assert is_empirical(source)


@pytest.mark.parametrize("source", [
    "Approximation based on Brazil",
    "estimated",
    "",
])
def test_non_empirical_recognized(source):
    assert not is_empirical(source)


# ---------------------------------------------------------------------------
# deviation_section_body
# ---------------------------------------------------------------------------

def test_deviation_returns_body_text():
    text = (
        "# Decisions\n\n"
        "## Some other thing\n\nblah\n\n"
        "## Deviation justification\n\n"
        "### LTO\nlong-term data revised\n\n"
        "## Conflict resolution\n\nblah\n"
    )
    body = deviation_section_body(text)
    assert "### LTO" in body
    assert "revised" in body
    assert "Conflict resolution" not in body


def test_deviation_empty_when_section_missing():
    assert deviation_section_body("# foo\n\nbar") == ""


def test_deviation_case_insensitive_heading():
    body = deviation_section_body("## DEVIATION JUSTIFICATION\n\nLTO note\n")
    assert "LTO note" in body


def test_deviation_subheading_not_section():
    """### Deviation justification (three #) is not a section."""
    assert deviation_section_body("### Deviation justification\n\nLTO\n") == ""


# ---------------------------------------------------------------------------
# justified_dimensions
# ---------------------------------------------------------------------------

def test_justified_picks_dim_as_subheading():
    assert justified_dimensions("## Deviation justification\n\n### LTO\nprose\n") == {"LTO"}


def test_justified_picks_multiple_dims_inline():
    text = (
        "## Deviation justification\n\n"
        "We chose lower LTO and higher IND based on recent research.\n"
    )
    assert justified_dimensions(text) == {"LTO", "IND"}


def test_justified_word_boundary_no_false_positives():
    """Substrings like GLOBAL, ALTO, INDIA must not satisfy dim names."""
    text = "## Deviation justification\n\nSome words: GLOBAL, ALTO, INDIA\n"
    assert justified_dimensions(text) == set()


def test_justified_empty_without_section():
    assert justified_dimensions("# title\n\nLTO mentioned\n") == set()


# ---------------------------------------------------------------------------
# validate_country
# ---------------------------------------------------------------------------

@pytest.fixture
def germany(tmp_path):
    return {"root": tmp_path, "reference": {"germany": dict(_REFERENCE_GERMANY)}}


def test_validate_exact_match_passes(germany):
    country = _write_country(
        germany["root"], "germany",
        _readme_with_scores({"PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40}),
    )
    errors, info = validate_country(country, germany["reference"])
    assert errors == []
    assert info == []


def test_validate_within_tolerance_passes(germany):
    """+/-5 inclusive: PDI 30 vs ref 35 (gap 5) passes."""
    country = _write_country(
        germany["root"], "germany",
        _readme_with_scores({"PDI": 30, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40}),
    )
    errors, info = validate_country(country, germany["reference"])
    assert errors == []


def test_validate_outside_tolerance_no_justification_fails(germany):
    country = _write_country(
        germany["root"], "germany",
        _readme_with_scores({"PDI": 50, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40}),
    )
    errors, info = validate_country(country, germany["reference"])
    assert len(errors) == 1
    assert "PDI=50" in errors[0]
    assert "Empirical reference 35" in errors[0]
    assert "gap 15" in errors[0]
    assert "Deviation justification" in errors[0]


def test_validate_outside_tolerance_with_justification_passes(germany):
    decisions = (
        "# Decisions: germany\n\n"
        "## Deviation justification\n\n"
        "### PDI\nWe diverge from Hofstede here because of regional research.\n"
    )
    country = _write_country(
        germany["root"], "germany",
        _readme_with_scores({"PDI": 50, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40}),
        decisions=decisions,
    )
    errors, info = validate_country(country, germany["reference"])
    assert errors == []
    assert len(info) == 1
    assert "PDI=50" in info[0]
    assert "justified" in info[0]


def test_validate_unknown_country_skipped(germany):
    country = _write_country(germany["root"], "atlantis", _readme_with_scores({"PDI": 50}))
    errors, info = validate_country(country, germany["reference"])
    assert errors == []
    assert len(info) == 1
    assert "no Hofstede reference data" in info[0]


def test_validate_missing_readme_fails(germany):
    country = germany["root"] / "regions" / "europe" / "germany"
    country.mkdir(parents=True)
    errors, info = validate_country(country, germany["reference"])
    assert len(errors) == 1
    assert "README.md missing" in errors[0]


def test_validate_empirical_label_in_error(germany):
    country = _write_country(
        germany["root"], "germany",
        _readme_with_scores({"PDI": 90, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40}),
    )
    errors, info = validate_country(country, germany["reference"])
    assert len(errors) == 1
    assert "Empirical reference" in errors[0]


def test_validate_approximation_label_in_error(tmp_path):
    reference = {"germany": {**_REFERENCE_GERMANY, "source": "Approximation based on neighbor"}}
    country = _write_country(
        tmp_path, "germany",
        _readme_with_scores({"PDI": 90, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40}),
    )
    errors, info = validate_country(country, reference)
    assert len(errors) == 1
    assert "Approximation reference" in errors[0]


# ---------------------------------------------------------------------------
# Contract locks
# ---------------------------------------------------------------------------

def test_dimensions_locked():
    assert HOFSTEDE_DIMENSIONS == ("PDI", "IDV", "UAI", "MAS", "LTO", "IND")


def test_tolerance_locked():
    """Widening the band silently weakens the check; require a reviewed edit."""
    assert REFERENCE_TOLERANCE == 5
