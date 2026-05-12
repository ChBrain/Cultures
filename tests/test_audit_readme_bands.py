"""Unit tests for scripts/audit_readme_bands.py.

Pins the band parsing contract that #71/#73 introduced and #75 extended:

  - Score table: Level cell vs. score_to_band(score) (closed enum
    Low/Moderate/High; non-band tokens silently skipped).
  - Prose: bold-with-colon leads like `**Low PDI + High IDV:**` or
    `**Moderate UAI (target 53):**` -- each <Band> <DIM> pair must
    agree with the table score's band. `Medium` is normalized to
    `Moderate` for the equivalence check but is still surfaced in the
    `declared` column so the non-canonical word is visible.

Canonical Hofstede band contract (this PR aligns the audit to it):
  0-39    -> Low
  40-69   -> Moderate
  70-100  -> High

Run: python3 -m unittest tests.test_audit_readme_bands
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))

import audit_readme_bands as audit  # noqa: E402


TABLE_SIX = (
    "| Dimension | Score | Level |\n"
    "|-----------|-------|-------|\n"
    "| PDI | 35 | **Low** |\n"
    "| IDV | 67 | **Moderate** |\n"
    "| UAI | 53 | **Moderate** |\n"
    "| MAS | 66 | **Moderate** |\n"
    "| LTO | 83 | **High** |\n"
    "| IND | 40 | **Moderate** |\n"
)

SCORES = {"PDI": 35, "IDV": 67, "UAI": 53, "MAS": 66, "LTO": 83, "IND": 40}


class TestScoreToBand(unittest.TestCase):
    def test_band_boundaries(self):
        self.assertEqual(audit.score_to_band(0), "Low")
        self.assertEqual(audit.score_to_band(39), "Low")
        self.assertEqual(audit.score_to_band(40), "Moderate")
        self.assertEqual(audit.score_to_band(69), "Moderate")
        self.assertEqual(audit.score_to_band(70), "High")
        self.assertEqual(audit.score_to_band(100), "High")


class TestNormalizeBand(unittest.TestCase):
    def test_canonical_passes_through(self):
        self.assertEqual(audit.normalize_band("Low"), "Low")
        self.assertEqual(audit.normalize_band("Moderate"), "Moderate")
        self.assertEqual(audit.normalize_band("High"), "High")

    def test_medium_aliased_to_moderate(self):
        self.assertEqual(audit.normalize_band("Medium"), "Moderate")
        self.assertEqual(audit.normalize_band("medium"), "Moderate")
        self.assertEqual(audit.normalize_band("MEDIUM"), "Moderate")


class TestAuditTable(unittest.TestCase):
    def test_extracts_all_six_dimensions(self):
        rows, scores = audit.audit_table("test", TABLE_SIX)
        self.assertEqual(scores, SCORES)
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertFalse(row[6], msg=f"unexpected mismatch: {row}")

    def test_flags_mismatched_level(self):
        text = TABLE_SIX.replace(
            "| UAI | 53 | **Moderate** |",
            "| UAI | 53 | **High** |",
        )
        rows, _ = audit.audit_table("test", text)
        mismatches = [r for r in rows if r[6]]
        self.assertEqual(len(mismatches), 1)
        _, source, dim, score, declared, expected, _ = mismatches[0]
        self.assertEqual(source, "table")
        self.assertEqual(dim, "UAI")
        self.assertEqual(score, 53)
        self.assertEqual(declared, "High")
        self.assertEqual(expected, "Moderate")

    def test_handles_inline_classifier_in_level_cell(self):
        # `**Moderate** - description` style. Score 67 sits in the
        # Moderate band (40-69) under the canonical contract.
        text = (
            "| Power Distance (PDI) | 35 | **Low** - Equality valued |\n"
            "| Individualism (IDV) | 67 | **Moderate** - Balanced autonomy |\n"
            "| Uncertainty Avoidance (UAI) | 65 | **Moderate** - Some rules |\n"
            "| Masculinity (MAS) | 66 | **Moderate** - Balanced |\n"
            "| Long-Term Orientation (LTO) | 83 | **High** - Long planning |\n"
            "| Indulgence (IND) | 40 | **Moderate** - Restrained pole |\n"
        )
        rows, scores = audit.audit_table("test", text)
        self.assertEqual(len(rows), 6)
        self.assertEqual(scores["PDI"], 35)
        self.assertEqual(scores["IND"], 40)
        for row in rows:
            self.assertFalse(row[6], msg=f"unexpected mismatch: {row}")

    def test_dedupes_duplicate_dim_score(self):
        # Same DIM and SCORE appearing twice (e.g. Detailed Profile
        # restatement) should not double-count.
        text = TABLE_SIX + (
            "| Power Distance (PDI) | 35 | **Low** - description |\n"
        )
        rows, _ = audit.audit_table("test", text)
        pdi_rows = [r for r in rows if r[2] == "PDI"]
        self.assertEqual(len(pdi_rows), 1)


class TestAuditProse(unittest.TestCase):
    def test_finds_combined_band_dim_pair(self):
        # Use scores in unambiguous bands so the matched declared bands
        # agree: PDI=35 -> Low, IDV=83 -> High.
        scores = {**SCORES, "PDI": 35, "IDV": 83}
        text = "- **Low PDI + High IDV:** Equality and autonomy.\n"
        rows = audit.audit_prose("test", text, scores)
        self.assertEqual(len(rows), 2)
        dims = {r[2] for r in rows}
        self.assertEqual(dims, {"PDI", "IDV"})
        for row in rows:
            self.assertFalse(row[6], msg=f"unexpected mismatch: {row}")

    def test_finds_keyword_distribution_target_form(self):
        text = '- **Moderate UAI (target 53):** "structuur", "regels".\n'
        rows = audit.audit_prose("test", text, SCORES)
        self.assertEqual(len(rows), 1)
        _, source, dim, _, declared, expected, needs_change = rows[0]
        self.assertTrue(source.startswith("prose:L"))
        self.assertEqual(dim, "UAI")
        self.assertEqual(declared, "Moderate")
        self.assertEqual(expected, "Moderate")
        self.assertFalse(needs_change)

    def test_medium_normalized_no_mismatch(self):
        # UAI=53 in SCORES. "Medium UAI" normalizes to Moderate; band agrees.
        text = "- **Medium UAI:** balanced tolerance.\n"
        rows = audit.audit_prose("test", text, SCORES)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], "Medium")     # declared printed as-is
        self.assertEqual(rows[0][5], "Moderate")   # canonical expected
        self.assertFalse(rows[0][6])               # not a mismatch

    def test_medium_with_high_band_is_mismatch(self):
        # Drift class: prose says "Medium IDV" but the table score sits in
        # the High band (>=70 under the canonical 39/69 contract). Use
        # PDI=78 (High) so the same-bullet companion stays clean and the
        # IDV mismatch isolates.
        scores = {**SCORES, "PDI": 78, "IDV": 72}
        text = "- **High PDI + Medium IDV:** Hierarchy is real but earned.\n"
        rows = audit.audit_prose("test", text, scores)
        idv_row = next(r for r in rows if r[2] == "IDV")
        self.assertEqual(idv_row[4], "Medium")
        self.assertEqual(idv_row[5], "High")
        self.assertTrue(idv_row[6])
        # PDI 78 sits in High band; same-bullet companion is clean.
        pdi_row = next(r for r in rows if r[2] == "PDI")
        self.assertFalse(pdi_row[6])

    def test_skips_bold_with_no_band_dim(self):
        text = "- **Source:** Hofstede Insights.\n- **Note:** see also...\n"
        rows = audit.audit_prose("test", text, SCORES)
        self.assertEqual(rows, [])

    def test_skips_prose_dim_absent_from_scores(self):
        # Country with only PDI in its table; prose MAS mention silent.
        text = "- **High MAS:** competitive.\n"
        rows = audit.audit_prose("test", text, {"PDI": 35})
        self.assertEqual(rows, [])

    def test_table_profile_cell_not_scanned_as_prose(self):
        # `**Low** - prose |` ends with `**` not `:**`; prose pass skips it.
        text = "| PDI | 35 | **Low** - Equality valued |\n"
        rows = audit.audit_prose("test", text, SCORES)
        self.assertEqual(rows, [])

    def test_line_number_reported(self):
        # Use a score that puts the declared band on the right band under
        # the canonical 39/69 contract: IDV=83 -> High.
        scores = {**SCORES, "IDV": 83}
        text = (
            "intro line one\n"
            "intro line two\n"
            "- **High IDV:** something\n"
        )
        rows = audit.audit_prose("test", text, scores)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "prose:L3")


if __name__ == "__main__":
    unittest.main()
