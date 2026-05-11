"""Unit tests for tests/validate_hofstede_alignment.py (L4e).

Pins the band+mismatch contract introduced in Phase 6c:

  - Level column is a closed enum: `Low`, `Moderate`, `High`.
  - Level must equal `score_to_band(score)`:
        0-39   -> Low
        40-59  -> Moderate
        60-100 -> High
  - Classifier prose like `Very Low` / `Very High` belongs in the
    Description column and is not parsed by L4e.

Run: python3 -m unittest tests.test_hofstede_alignment
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from validate_hofstede_alignment import (  # noqa: E402
    check_structure,
    extract_hofstede_scores,
    score_to_band,
)


HEADER_AND_SOURCE = (
    "## Hofstede Cultural Dimensions\n\n"
    "| Dimension | Score | Level |\n"
    "|-----------|-------|-------|\n"
)
FOOTER_SOURCE = "\n**Source:** Hofstede Insights\n"


def _readme(rows: list[str]) -> str:
    return HEADER_AND_SOURCE + "\n".join(rows) + "\n" + FOOTER_SOURCE


def _all_six_rows(uai_score: int = 50, uai_level: str = "Moderate") -> list[str]:
    """Six dimension rows; UAI is the one under test."""
    return [
        "| PDI | 35 | **Low** |",
        "| IDV | 67 | **High** |",
        f"| UAI | {uai_score} | **{uai_level}** |",
        "| MAS | 66 | **High** |",
        "| LTO | 83 | **High** |",
        "| IND | 40 | **Moderate** |",
    ]


class TestScoreToBand(unittest.TestCase):
    def test_low_band_inclusive(self):
        self.assertEqual(score_to_band(0), "Low")
        self.assertEqual(score_to_band(39), "Low")

    def test_moderate_band_inclusive(self):
        self.assertEqual(score_to_band(40), "Moderate")
        self.assertEqual(score_to_band(50), "Moderate")
        self.assertEqual(score_to_band(59), "Moderate")

    def test_high_band_inclusive(self):
        self.assertEqual(score_to_band(60), "High")
        self.assertEqual(score_to_band(100), "High")


class TestExtractHofstedeScores(unittest.TestCase):
    def test_extracts_moderate_band(self):
        text = _readme(_all_six_rows(uai_score=50, uai_level="Moderate"))
        scores = extract_hofstede_scores(text)
        self.assertEqual(scores["UAI"], (50, "Moderate"))

    def test_does_not_match_very_high_in_level_column(self):
        rows = _all_six_rows()
        rows.append("| EXTRA | 85 | **Very High** |")
        text = _readme(rows)
        scores = extract_hofstede_scores(text)
        self.assertNotIn("EXTRA", scores)

    def test_does_not_match_medium_in_level_column(self):
        rows = _all_six_rows()
        rows[2] = "| UAI | 53 | **Medium** |"
        text = _readme(rows)
        scores = extract_hofstede_scores(text)
        self.assertNotIn("UAI", scores)

    def test_ignores_description_only_row(self):
        text = _readme([
            "| PDI | 35 | **Low** |",
            "| IDV | 67 | **High** |",
            "| UAI | 53 | **Moderate** |",
            "| MAS | 66 | **High** |",
            "| LTO | 83 | **High** |",
            "| IND | 40 | **Moderate** |",
            "| Uncertainty Avoidance (UAI) | 53 | Balanced; comfort with structure but prepared for ambiguity |",
        ])
        scores = extract_hofstede_scores(text)
        self.assertEqual(scores["UAI"], (53, "Moderate"))


class TestCheckStructureBands(unittest.TestCase):
    def _run(self, rows: list[str]):
        text = _readme(rows)
        scores = extract_hofstede_scores(text)
        with tempfile.TemporaryDirectory() as tmp:
            country_dir = Path(tmp)
            return check_structure("test", country_dir, text, scores)

    def test_moderate_accepted_at_50(self):
        rows = _all_six_rows(uai_score=50, uai_level="Moderate")
        issues = self._run(rows)
        self.assertEqual(issues, [])

    def test_high_at_53_is_mismatch(self):
        rows = _all_six_rows(uai_score=53, uai_level="High")
        issues = self._run(rows)
        mismatch = [i for i in issues if "UAI" in i.error and "disagrees" in i.error]
        self.assertEqual(len(mismatch), 1, msg=f"got: {[i.error for i in issues]}")
        self.assertIn("Moderate", mismatch[0].verdict)
        self.assertIn("53", mismatch[0].error)

    def test_very_high_rejected_via_missing_dimension(self):
        rows = _all_six_rows()
        rows[1] = "| IDV | 67 | **Very High** |"
        issues = self._run(rows)
        incomplete = [i for i in issues if "incomplete" in i.error]
        self.assertEqual(len(incomplete), 1)
        self.assertIn("IDV", incomplete[0].verdict)
        self.assertIn("Low/Moderate/High", incomplete[0].verdict)

    def test_classifier_prose_in_description_ignored(self):
        text = _readme([
            "| PDI | 35 | **Low** |",
            "| IDV | 67 | **High** |",
            "| UAI | 53 | **Moderate** |",
            "| MAS | 66 | **High** |",
            "| LTO | 83 | **High** |",
            "| IND | 40 | **Moderate** |",
        ])
        text += (
            "\n**Detailed Profile:**\n\n"
            "| Dimension | Score | Description |\n"
            "|-----------|-------|-------------|\n"
            "| Power Distance (PDI) | 35 | Very Low equality gap; hierarchy must be justified |\n"
            "| Individualism (IDV) | 67 | Very High autonomy and individual rights prioritized |\n"
        )
        scores = extract_hofstede_scores(text)
        with tempfile.TemporaryDirectory() as tmp:
            country_dir = Path(tmp)
            issues = check_structure("test", country_dir, text, scores)
        self.assertEqual(issues, [], msg=f"got: {[i.error for i in issues]}")

    def test_band_with_inline_classifier_in_level_cell(self):
        # `**Low** - Equality valued` style, used by Germany / Poland.
        rows = [
            "| Power Distance (PDI) | 35 | **Low** - Equality valued; hierarchy questioned |",
            "| Individualism (IDV) | 67 | **High** - Individual achievement and autonomy prioritized |",
            "| Uncertainty Avoidance (UAI) | 65 | **High** - Rules, structure, and planning preferred |",
            "| Masculinity (MAS) | 66 | **High** - Competitiveness, achievement valued |",
            "| Long-Term Orientation (LTO) | 83 | **High** - Long-term planning and adaptation emphasized |",
            "| Indulgence (IND) | 40 | **Moderate** - Restrained pole; gratification regulated by social norms |",
        ]
        issues = self._run(rows)
        self.assertEqual(issues, [], msg=f"got: {[i.error for i in issues]}")


if __name__ == "__main__":
    unittest.main()
