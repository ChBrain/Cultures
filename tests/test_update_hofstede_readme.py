"""Unit tests for scripts/update_hofstede_readme.py.

Pins the contract:
- Status thresholds (EXCELLENT / PASS / WARN / FAIL)
- Band labels in the Cultural Dimensions table match canonical 39/69
- Alignment table format (declared / derived / gap / status)
- update_readme replaces only the two targeted tables; surrounding
  prose and other sections stay intact
- parse_declared_from_readme handles the existing corpus format
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))

import update_hofstede_readme as upd  # noqa: E402


# ---------------------------------------------------------------------------
# compute_status -- pin the EXCELLENT / PASS / WARN / FAIL thresholds
# ---------------------------------------------------------------------------

class TestComputeStatus:
    def test_excellent_zero_gap(self):
        assert upd.compute_status(50, 50) == (0, "EXCELLENT")

    @pytest.mark.parametrize("declared,derived,expected_gap", [
        (50, 55, 5),
        (50, 45, 5),
        (35, 30, 5),
    ])
    def test_excellent_upper_boundary(self, declared, derived, expected_gap):
        gap, status = upd.compute_status(declared, derived)
        assert gap == expected_gap
        assert status == "EXCELLENT"

    @pytest.mark.parametrize("declared,derived,expected_gap", [
        (50, 56, 6),
        (50, 60, 10),
        (50, 44, 6),
        (50, 40, 10),
    ])
    def test_pass_band(self, declared, derived, expected_gap):
        gap, status = upd.compute_status(declared, derived)
        assert gap == expected_gap
        assert status == "PASS"

    @pytest.mark.parametrize("declared,derived,expected_gap", [
        (50, 61, 11),
        (50, 70, 20),
        (50, 30, 20),
    ])
    def test_warn_band(self, declared, derived, expected_gap):
        gap, status = upd.compute_status(declared, derived)
        assert gap == expected_gap
        assert status == "WARN"

    @pytest.mark.parametrize("declared,derived,expected_gap", [
        (50, 71, 21),
        (0, 100, 100),
        (100, 0, 100),
    ])
    def test_fail_band(self, declared, derived, expected_gap):
        gap, status = upd.compute_status(declared, derived)
        assert gap == expected_gap
        assert status == "FAIL"


# ---------------------------------------------------------------------------
# parse_declared_from_readme -- parses existing corpus markdown
# ---------------------------------------------------------------------------

class TestParseDeclared:
    def test_basic_table(self):
        text = (
            "| Dimension | Score | Profile |\n"
            "|-----------|-------|---------|\n"
            "| Power Distance (PDI) | 35 | **Low** - blah |\n"
            "| Individualism (IDV) | 67 | **Moderate** - blah |\n"
        )
        assert upd.parse_declared_from_readme(text) == {"PDI": 35, "IDV": 67}

    def test_six_dimensions(self):
        text = (
            "| PDI | 35 | **Low** |\n"
            "| IDV | 67 | **Moderate** |\n"
            "| UAI | 65 | **Moderate** |\n"
            "| MAS | 66 | **Moderate** |\n"
            "| LTO | 83 | **High** |\n"
            "| IND | 40 | **Moderate** |\n"
        )
        assert upd.parse_declared_from_readme(text) == {
            "PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
        }

    def test_dedupes_same_dimension(self):
        """If a dim appears twice (e.g. summary + detail tables), keep first."""
        text = (
            "| PDI | 35 | **Low** |\n"
            "| PDI | 99 | **High** |\n"  # second mention; should be ignored
        )
        assert upd.parse_declared_from_readme(text) == {"PDI": 35}

    def test_empty_text(self):
        assert upd.parse_declared_from_readme("") == {}


# ---------------------------------------------------------------------------
# render_dimensions_table -- uses canonical bands
# ---------------------------------------------------------------------------

class TestRenderDimensionsTable:
    def test_germany_canonical_bands(self):
        """Germany's declared scores under canonical 39/69 thresholds:
        35 -> Low, 67 -> Moderate, 65 -> Moderate, 66 -> Moderate,
        83 -> High, 40 -> Moderate.
        """
        out = upd.render_dimensions_table({
            "PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
        })
        assert "| Power Distance (PDI) | 35 | **Low**" in out
        assert "| Individualism (IDV) | 67 | **Moderate**" in out
        assert "| Uncertainty Avoidance (UAI) | 65 | **Moderate**" in out
        assert "| Masculinity (MAS) | 66 | **Moderate**" in out
        assert "| Long-Term Orientation (LTO) | 83 | **High**" in out
        assert "| Indulgence (IND) | 40 | **Moderate**" in out

    def test_band_boundaries(self):
        """39 -> Low; 40 -> Moderate; 69 -> Moderate; 70 -> High."""
        out = upd.render_dimensions_table({
            "PDI": 39, "IDV": 40, "UAI": 69, "MAS": 70,
        })
        assert "| Power Distance (PDI) | 39 | **Low**" in out
        assert "| Individualism (IDV) | 40 | **Moderate**" in out
        assert "| Uncertainty Avoidance (UAI) | 69 | **Moderate**" in out
        assert "| Masculinity (MAS) | 70 | **High**" in out

    def test_partial_dimensions(self):
        out = upd.render_dimensions_table({"PDI": 35})
        assert "Power Distance (PDI)" in out
        assert "Individualism (IDV)" not in out

    def test_header_present(self):
        out = upd.render_dimensions_table({"PDI": 35})
        assert "| Dimension | Score | Profile |" in out
        assert "|-----------|-------|---------|" in out


# ---------------------------------------------------------------------------
# render_alignment_table
# ---------------------------------------------------------------------------

class TestRenderAlignmentTable:
    def test_status_per_dimension(self):
        declared = {"PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40}
        derived  = {"PDI": 33, "IDV": 75, "UAI": 66, "MAS": 60, "LTO": 87, "IND": 33}
        out = upd.render_alignment_table(declared, derived)
        assert "| PDI | 35 | 33 | 2 | OK EXCELLENT |" in out
        assert "| IDV | 67 | 75 | 8 | OK PASS |" in out
        assert "| UAI | 65 | 66 | 1 | OK EXCELLENT |" in out
        assert "| MAS | 66 | 60 | 6 | OK PASS |" in out
        assert "| LTO | 83 | 87 | 4 | OK EXCELLENT |" in out
        assert "| IND | 40 | 33 | 7 | OK PASS |" in out

    def test_warn_and_fail_surface(self):
        declared = {"PDI": 50, "IDV": 50}
        derived  = {"PDI": 65, "IDV": 90}
        out = upd.render_alignment_table(declared, derived)
        assert "WARN WARN" in out  # 50 vs 65 -> gap 15 -> WARN
        assert "FAIL FAIL" in out  # 50 vs 90 -> gap 40 -> FAIL

    def test_missing_derived_marks_na(self):
        declared = {"PDI": 35}
        derived: dict[str, int] = {}
        out = upd.render_alignment_table(declared, derived)
        assert "| PDI | 35 | n/a | n/a |" in out

    def test_header_present(self):
        out = upd.render_alignment_table({"PDI": 35}, {"PDI": 35})
        assert "| Dimension | Declared | Derived | Gap | Status |" in out
        assert "|-----------|----------|---------|-----|--------|" in out


# ---------------------------------------------------------------------------
# update_readme -- replaces only the targeted tables
# ---------------------------------------------------------------------------

_README_FIXTURE = (
    "# Germany - Culture Content\n"
    "\n"
    "Some intro prose stays intact.\n"
    "\n"
    "## Hofstede Cultural Dimensions - Germany\n"
    "\n"
    "Germany's cultural profile:\n"
    "\n"
    "| Dimension | Score | Profile |\n"
    "|-----------|-------|---------|\n"
    "| PDI | 35 | **Low** - old copy |\n"
    "| IDV | 67 | **High** - DRIFTED |\n"
    "\n"
    "**Source:** Hofstede et al. (2010).\n"
    "\n"
    "## Hofstede Alignment Status (Content Audit)\n"
    "\n"
    "Pre-table prose.\n"
    "\n"
    "| Dimension | Declared | Derived | Gap | Status |\n"
    "|-----------|----------|---------|-----|--------|\n"
    "| PDI | 35 | 30 | 5 | OLD EXCELLENT |\n"
    "\n"
    "Post-table prose stays.\n"
    "\n"
    "## Some Other Section\n"
    "\n"
    "Untouched section.\n"
)


class TestUpdateReadme:
    def test_replaces_both_tables(self):
        declared = {"PDI": 35, "IDV": 67}
        derived = {"PDI": 33, "IDV": 75}
        new_text, warnings = upd.update_readme(
            _README_FIXTURE, "Germany", declared, derived,
        )
        assert warnings == []
        # IDV=67 under canonical 39/69 is Moderate, not High
        assert "**High** - DRIFTED" not in new_text
        assert "| Individualism (IDV) | 67 | **Moderate**" in new_text
        # Alignment table updated with new derived value
        assert "| PDI | 35 | 33 | 2 | OK EXCELLENT |" in new_text
        # OLD EXCELLENT label removed (was wrong format)
        assert "OLD EXCELLENT" not in new_text

    def test_preserves_surrounding_prose(self):
        new_text, _ = upd.update_readme(
            _README_FIXTURE, "Germany",
            {"PDI": 35}, {"PDI": 35},
        )
        assert "Some intro prose stays intact." in new_text
        assert "**Source:** Hofstede et al. (2010)." in new_text
        assert "Pre-table prose." in new_text
        assert "Post-table prose stays." in new_text

    def test_preserves_other_sections(self):
        new_text, _ = upd.update_readme(
            _README_FIXTURE, "Germany",
            {"PDI": 35}, {"PDI": 35},
        )
        assert "## Some Other Section" in new_text
        assert "Untouched section." in new_text

    def test_missing_sections_emit_warnings(self):
        text = "# No Hofstede sections at all\n\nJust some content.\n"
        new_text, warnings = upd.update_readme(
            text, "X", {"PDI": 35}, {"PDI": 30},
        )
        assert new_text == text
        assert len(warnings) == 2  # both sections missing
        assert any("Cultural Dimensions" in w for w in warnings)
        assert any("Alignment Status" in w for w in warnings)

    def test_alignment_only_when_dimensions_missing(self):
        text = (
            "## Hofstede Alignment Status\n"
            "\n"
            "| Dimension | Declared | Derived | Gap | Status |\n"
            "|-----------|----------|---------|-----|--------|\n"
            "| PDI | 35 | 30 | 5 | OLD |\n"
        )
        new_text, warnings = upd.update_readme(
            text, "X", {"PDI": 35}, {"PDI": 33},
        )
        # Alignment table updated
        assert "| PDI | 35 | 33 | 2 | OK EXCELLENT |" in new_text
        # Cultural Dimensions heading missing -> one warning
        assert len(warnings) == 1
        assert "Cultural Dimensions" in warnings[0]
