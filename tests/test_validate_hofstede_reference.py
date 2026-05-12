"""Unit tests for tests/validate_hofstede_reference.py.

Pins the reference-comparison contract:

  |declared - reference| <= 5            -> PASS silently
  gap > 5 + dim named in deviation       -> INFO (advisory)
  gap > 5 with no deviation section      -> FAIL

Run: python3 -m unittest tests.test_validate_hofstede_reference
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

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


_REFERENCE_GERMANY = {
    "PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
    "source": "Hofstede Insights - Empirical research",
}


def _readme_with_scores(scores: dict[str, int]) -> str:
    """Render the score table the way real README.md files do."""
    rows = "\n".join(
        f"| {dim} | {score} | high |" for dim, score in scores.items()
    )
    return f"""# Testland - Culture Content

## Hofstede Cultural Dimensions

| Dimension | Score | Profile |
|---|---|---|
{rows}
"""


def _write_country(
    root: Path, name: str, readme: str, decisions: str = "",
) -> Path:
    """Build a minimal country dir on disk for validate_country() to read."""
    country = root / "regions" / "europe" / name
    country.mkdir(parents=True)
    (country / "README.md").write_text(readme, encoding="utf-8")
    if decisions:
        (country / "hofstede_decisions.md").write_text(decisions, encoding="utf-8")
    return country


class TestExtractScores(unittest.TestCase):
    def test_parses_pipe_table_rows(self):
        text = _readme_with_scores({
            "PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
        })
        scores = extract_hofstede_scores(text)
        self.assertEqual(
            scores,
            {"PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40},
        )

    def test_empty_when_no_table(self):
        self.assertEqual(extract_hofstede_scores("no scores here"), {})


class TestSourceClassification(unittest.TestCase):
    def test_empirical_recognized(self):
        for s in [
            "Hofstede Insights - Empirical research",
            "EMPIRICAL data",
            "empirical (recent)",
        ]:
            with self.subTest(source=s):
                self.assertTrue(is_empirical(s))

    def test_non_empirical_recognized(self):
        for s in [
            "Approximation based on Brazil",
            "estimated",
            "",
        ]:
            with self.subTest(source=s):
                self.assertFalse(is_empirical(s))


class TestDeviationSection(unittest.TestCase):
    """The justification heuristic is the only fuzzy bit; pin it carefully."""

    def test_returns_body_text(self):
        text = (
            "# Decisions\n\n"
            "## Some other thing\n\nblah\n\n"
            "## Deviation justification\n\n"
            "### LTO\nlong-term data revised\n\n"
            "## Conflict resolution\n\nblah\n"
        )
        body = deviation_section_body(text)
        self.assertIn("### LTO", body)
        self.assertIn("revised", body)
        self.assertNotIn("Conflict resolution", body)

    def test_empty_when_section_missing(self):
        self.assertEqual(deviation_section_body("# foo\n\nbar"), "")

    def test_case_insensitive_heading(self):
        body = deviation_section_body("## DEVIATION JUSTIFICATION\n\nLTO note\n")
        self.assertIn("LTO note", body)

    def test_subheading_count_does_not_create_false_positives(self):
        """A ``### Deviation justification`` (three #'s) is NOT a section."""
        self.assertEqual(
            deviation_section_body("### Deviation justification\n\nLTO\n"),
            "",
        )


class TestJustifiedDimensions(unittest.TestCase):
    def test_picks_dim_mentioned_as_subheading(self):
        text = "## Deviation justification\n\n### LTO\nprose\n"
        self.assertEqual(justified_dimensions(text), {"LTO"})

    def test_picks_multiple_dims_inline(self):
        text = (
            "## Deviation justification\n\n"
            "We chose lower LTO and higher IND based on recent research.\n"
        )
        self.assertEqual(justified_dimensions(text), {"LTO", "IND"})

    def test_word_boundary_no_false_positives(self):
        """Substring matches like 'GLOBAL' must not satisfy LTO."""
        text = "## Deviation justification\n\nSome words: GLOBAL, ALTO, INDIA\n"
        self.assertEqual(justified_dimensions(text), set())

    def test_returns_empty_without_section(self):
        self.assertEqual(justified_dimensions("# title\n\nLTO mentioned\n"), set())


class TestValidateCountry(unittest.TestCase):
    """End-to-end on a temp country dir; pins the gate behavior."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.reference = {"germany": dict(_REFERENCE_GERMANY)}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_exact_match_passes(self):
        country = _write_country(
            self.root, "germany",
            _readme_with_scores({
                "PDI": 35, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
            }),
        )
        errors, info = validate_country(country, self.reference)
        self.assertEqual(errors, [])
        self.assertEqual(info, [])

    def test_within_tolerance_passes(self):
        """+/-5 inclusive: PDI 30 vs ref 35 (gap 5) passes."""
        country = _write_country(
            self.root, "germany",
            _readme_with_scores({
                "PDI": 30, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
            }),
        )
        errors, info = validate_country(country, self.reference)
        self.assertEqual(errors, [], errors)

    def test_outside_tolerance_no_justification_fails(self):
        country = _write_country(
            self.root, "germany",
            _readme_with_scores({
                "PDI": 50, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
            }),
        )
        errors, info = validate_country(country, self.reference)
        self.assertEqual(len(errors), 1)
        self.assertIn("PDI=50", errors[0])
        self.assertIn("Empirical reference 35", errors[0])
        self.assertIn("gap 15", errors[0])
        self.assertIn("Deviation justification", errors[0])

    def test_outside_tolerance_with_justification_passes(self):
        decisions = (
            "# Decisions: germany\n\n"
            "## Deviation justification\n\n"
            "### PDI\nWe diverge from Hofstede here because of regional research.\n"
        )
        country = _write_country(
            self.root, "germany",
            _readme_with_scores({
                "PDI": 50, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
            }),
            decisions=decisions,
        )
        errors, info = validate_country(country, self.reference)
        self.assertEqual(errors, [])
        self.assertEqual(len(info), 1)
        self.assertIn("PDI=50", info[0])
        self.assertIn("justified", info[0])

    def test_unknown_country_skipped(self):
        country = _write_country(self.root, "atlantis", _readme_with_scores({"PDI": 50}))
        errors, info = validate_country(country, self.reference)
        self.assertEqual(errors, [])
        self.assertEqual(len(info), 1)
        self.assertIn("no Hofstede reference data", info[0])

    def test_missing_readme_fails(self):
        country = self.root / "regions" / "europe" / "germany"
        country.mkdir(parents=True)
        errors, info = validate_country(country, self.reference)
        self.assertEqual(len(errors), 1)
        self.assertIn("README.md missing", errors[0])

    def test_empirical_label_appears_in_error(self):
        country = _write_country(
            self.root, "germany",
            _readme_with_scores({
                "PDI": 90, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
            }),
        )
        errors, info = validate_country(country, self.reference)
        self.assertEqual(len(errors), 1)
        self.assertIn("Empirical reference", errors[0])

    def test_approximation_label_appears_in_error(self):
        reference = {
            "germany": {
                **_REFERENCE_GERMANY,
                "source": "Approximation based on neighbor",
            }
        }
        country = _write_country(
            self.root, "germany",
            _readme_with_scores({
                "PDI": 90, "IDV": 67, "UAI": 65, "MAS": 66, "LTO": 83, "IND": 40,
            }),
        )
        errors, info = validate_country(country, reference)
        self.assertEqual(len(errors), 1)
        self.assertIn("Approximation reference", errors[0])


class TestContractLocks(unittest.TestCase):
    """Pin the public contract — changing these should be deliberate."""

    def test_dimensions_locked(self):
        self.assertEqual(
            HOFSTEDE_DIMENSIONS,
            ("PDI", "IDV", "UAI", "MAS", "LTO", "IND"),
        )

    def test_tolerance_locked(self):
        """Widening the band silently weakens the check; require a
        reviewed edit."""
        self.assertEqual(REFERENCE_TOLERANCE, 5)


if __name__ == "__main__":
    unittest.main()
