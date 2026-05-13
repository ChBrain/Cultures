#!/usr/bin/env python3
"""Audit Hofstede band labels in country READMEs.

Catches two kinds of drift:

1. Score table -- Level cell vs. score_to_band(score). The same contract
   L4e (`tests/validate_hofstede_alignment.py`) enforces.

2. Prose mentions -- any bold-with-colon lead of the form `**...:**`
   that contains one or more `<Band> <DIM>` pairs. Examples:
     `**Low PDI + High IDV:**`       (How Dimensions section)
     `**High UAI:**`
     `**Moderate UAI (target 53):**` (Target Keyword Distribution)
   Each pair's declared band must agree with `score_to_band(score)`
   for that dimension's table score. Catches the "Low IND" / "Medium
   UAI" prose drift that survived the table-only audit (and motivated
   PR #74). "Medium" is normalized to "Moderate" for band-equivalence
   (the canonical L4e form), but is still shown in the `declared`
   column so the non-canonical word is visible.

Band contract (canonical Hofstede bands):
  0-39    -> Low
  40-69   -> Moderate
  70-100  -> High

Output is one TSV row per finding, with a `needs_change` flag:

  country | source | dimension | score | declared | expected | needs_change

`source` is `table` for score-table rows, `prose:L<line>` for prose
mentions (line of the containing bold-with-colon block).

Exit status:
  0 if no mismatches.
  1 if any mismatch found.

Usage:
  scripts/audit_readme_bands.py             # all countries, all rows
  scripts/audit_readme_bands.py --mismatch  # only rows that need change
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HOFSTEDE_DIMENSIONS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]

REGIONS = ("africa", "americas", "asia", "europe", "oceania")

# Score-table row: `| <dim cell> | <score> | **<Level>**[ ...] |`
TABLE_PATTERN = re.compile(
    r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|"
    r"\s*(\d+)\s*\|"
    r"\s*\*\*([A-Za-z][A-Za-z \-]*?)\*\*[^|\n]*\|",
    re.IGNORECASE,
)

# Prose lead: a bold blob ending in `:**`, single line, no `*` inside.
PROSE_BLOCK_PATTERN = re.compile(r"\*\*\s*([^*\n]+?)\s*:\s*\*\*")

# Band-dimension pair inside a prose lead (case-insensitive).
BAND_DIM_PATTERN = re.compile(
    r"\b(Low|Moderate|Medium|High)\s+(PDI|IDV|UAI|MAS|LTO|IND)\b",
    re.IGNORECASE,
)

# 'Medium' is an accepted prose alias for 'Moderate' (canonical L4e form).
BAND_ALIAS = {"medium": "moderate"}


Row = tuple[str, str, str, int, str, str, bool]
# (country, source, dim, score, declared, expected, needs_change)


def score_to_band(score: int) -> str:
    """Map a 0-100 Hofstede score to its canonical band.

    Canonical Hofstede band contract:
        0-39    -> Low
        40-69   -> Moderate
        70-100  -> High

    Kept in sync with the band thresholds in
    ``scripts/scaffold_country.py``.
    """
    if score <= 39:
        return "Low"
    if score <= 69:
        return "Moderate"
    return "High"


def normalize_band(word: str) -> str:
    w = word.strip().lower()
    return BAND_ALIAS.get(w, w).title()


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def find_country_readmes() -> list[Path]:
    regions_dir = ROOT / "regions"
    if not regions_dir.is_dir():
        return []
    readmes: list[Path] = []
    for region in sorted(regions_dir.iterdir()):
        if not region.is_dir() or region.name.startswith("."):
            continue
        for country in sorted(region.iterdir()):
            if not country.is_dir() or country.name.startswith("."):
                continue
            readme = country / "README.md"
            if readme.exists():
                readmes.append(readme)
    return readmes


def audit_table(country: str, text: str) -> tuple[list[Row], dict[str, int]]:
    """Audit score-table rows. Returns (rows, dim_to_score)."""
    rows: list[Row] = []
    scores: dict[str, int] = {}
    seen: set[tuple[str, int]] = set()
    for match in TABLE_PATTERN.finditer(text):
        dim = match.group(1).upper()
        score = int(match.group(2))
        declared_raw = match.group(3).strip()
        declared_first = declared_raw.split()[0].title() if declared_raw else ""
        key = (dim, score)
        if key in seen:
            continue
        seen.add(key)
        scores[dim] = score
        expected = score_to_band(score)
        needs_change = normalize_band(declared_first) != expected
        rows.append(
            (country, "table", dim, score, declared_first, expected, needs_change)
        )
    return rows, scores


def audit_prose(country: str, text: str, scores: dict[str, int]) -> list[Row]:
    """Audit prose band-dim mentions against the table scores."""
    rows: list[Row] = []
    seen: set[tuple[int, str, str]] = set()
    for block in PROSE_BLOCK_PATTERN.finditer(text):
        block_text = block.group(1)
        line = line_of(text, block.start())
        for match in BAND_DIM_PATTERN.finditer(block_text):
            declared_raw = match.group(1)
            dim = match.group(2).upper()
            if dim not in scores:
                continue
            declared_title = declared_raw.title()
            key = (line, dim, declared_title)
            if key in seen:
                continue
            seen.add(key)
            score = scores[dim]
            expected = score_to_band(score)
            needs_change = normalize_band(declared_raw) != expected
            rows.append(
                (
                    country,
                    f"prose:L{line}",
                    dim,
                    score,
                    declared_title,
                    expected,
                    needs_change,
                )
            )
    return rows


def audit_readme(readme: Path) -> list[Row]:
    text = readme.read_text(encoding="utf-8")
    country = readme.parent.name
    table_rows, scores = audit_table(country, text)
    prose_rows = audit_prose(country, text, scores)
    return table_rows + prose_rows


def main(argv: list[str]) -> int:
    only_mismatch = "--mismatch" in argv[1:]
    readmes = find_country_readmes()
    if not readmes:
        print("No country READMEs found.", file=sys.stderr)
        return 0

    print("country\tsource\tdimension\tscore\tdeclared\texpected\tneeds_change")
    total = 0
    mismatches = 0
    for readme in readmes:
        for row in audit_readme(readme):
            country, source, dim, score, declared, expected, needs_change = row
            total += 1
            if needs_change:
                mismatches += 1
            if only_mismatch and not needs_change:
                continue
            print(
                f"{country}\t{source}\t{dim}\t{score}\t{declared}\t{expected}\t"
                f"{'yes' if needs_change else 'no'}"
            )

    print(
        f"\nAudited {len(readmes)} README(s), {total} band mention(s); "
        f"{mismatches} mismatch(es).",
        file=sys.stderr,
    )
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
