#!/usr/bin/env python3
"""Hofstede validation: structure + dimension alignment.

Two passes per country:

1. Structure (FAIL, hard-block): README has a `## Hofstede` section, a
   score table with all six dimensions filled in (PDI, IDV, UAI, MAS, LTO,
   IND), a source line, and REFERENCES.md cites Hofstede. If the country
   has a culture position file, it should reference the dimensions.

2. Alignment (WARN, advisory): given the scores from the README, the
   position file's keywords should match the expected polarity for each
   dimension.

Alignment depends on structure: if scores cannot be extracted from the
README, the alignment pass is skipped for that country (otherwise it would
silently pass with no findings).

The alignment keyword bag is English. Per the language policy, position
files are written in the culture's native language, so alignment warnings
on non-English content are expected and currently informational only —
hence advisory. Multilingual keyword bags are a future project.

Both passes share the same `extract_hofstede_scores` parser, so dimension
presence in the structure pass and score extraction in the alignment pass
agree on what counts as a valid score row.

Exit status:
  0 if every country passes the structure pass (alignment warnings ignored
    for the exit code).
  1 if any country has a structure issue.

Usage:
  tests/validate_hofstede_alignment.py            # all countries
  tests/validate_hofstede_alignment.py FILE...    # files in same country only
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue


HOFSTEDE_DIMENSIONS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]

# Keyword sets for each dimension's high vs low variants
DIMENSION_KEYWORDS = {
    "PDI": {
        "high": ["hierarchy", "status", "rank", "formal", "respect", "authority", "leader", "obey"],
        "low": ["equal", "equality", "merit", "question", "challenge", "flat", "egalitarian", "democratic"],
    },
    "IDV": {
        "high": ["individual", "autonomy", "personal", "achievement", "self", "unique", "independent"],
        "low": ["group", "collective", "harmony", "loyalty", "team", "community", "belonging", "together"],
    },
    "UAI": {
        "high": ["rule", "structure", "plan", "clarity", "precise", "predict", "stability", "order", "protocol"],
        "low": ["flexible", "adapt", "improvise", "ambiguous", "risk", "spontaneous", "comfort uncertainty"],
    },
    "MAS": {
        "high": ["achieve", "compete", "win", "success", "ambitious", "assert", "power", "strength"],
        "low": ["care", "cooperate", "relationship", "quality life", "modest", "compassion", "community"],
    },
    "LTO": {
        "high": ["long-term", "future", "plan", "save", "invest", "adapt", "persever", "tradition respect"],
        "low": ["immediate", "present", "quick", "instant", "result", "tradition", "past", "heritage"],
    },
    "IND": {
        "high": ["enjoy", "gratif", "pleasure", "freedom", "indulge", "relax"],
        "low": ["restrain", "discipline", "moderate", "self-control", "duty", "obligation"],
    },
}

POSITION_DIMENSION_REF = re.compile(
    r"hofstede|power distance|individualism|uncertainty avoidance|"
    r"masculinity|long-term orientation|indulgence|"
    r"\b(?:PDI|IDV|UAI|MAS|LTO|IND)\b",
    re.IGNORECASE,
)


def find_country_folders() -> list[Path]:
    """Find all country folders that contain culture content."""
    root = Path(__file__).resolve().parent.parent
    regions = root / "regions"
    if not regions.is_dir():
        return []

    countries = []
    for region_dir in sorted(regions.iterdir()):
        if not region_dir.is_dir() or region_dir.name.startswith("."):
            continue
        for country_dir in sorted(region_dir.iterdir()):
            if not country_dir.is_dir() or country_dir.name.startswith("."):
                continue
            content_files = (
                list(country_dir.glob("culture_*.md"))
                + list(country_dir.glob("persona_*.md"))
            )
            if content_files:
                countries.append(country_dir)
    return countries


def extract_hofstede_scores(readme_text: str) -> dict[str, tuple[int, str]]:
    """Extract Hofstede scores from README.

    Matches table rows of either form:
      `| PDI | 35 | **Low** ... |`
      `| Power Distance (PDI) | 35 | **Low** ... |`

    The first cell must contain the dimension code as a whole word; the
    second must be a bare integer; the third must open with `**Low`,
    `**High`, or `**Very High` (further qualifiers like `**Low-Moderate**`
    are accepted and read as the leading level). Header rows, prose
    mentions, score ranges, and missing bold markers are intentionally not
    counted: structure and alignment must agree on the same notion of a
    "valid score row".

    Returns: {dimension: (score, level)}
    """
    scores: dict[str, tuple[int, str]] = {}
    pattern = (
        r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|"
        r"\s*(\d+)\s*\|"
        r"\s*\*\*(Low|High|Very High)[^\|\n]*\|"
    )
    for match in re.finditer(pattern, readme_text, re.IGNORECASE):
        dim = match.group(1).upper()
        score = int(match.group(2))
        level = match.group(3).upper()
        scores[dim] = (score, level)
    return scores


def check_structure(
    country_name: str,
    country_dir: Path,
    readme_text: str,
    scores: dict[str, tuple[int, str]],
) -> list[Issue]:
    """Structure pass: README section, score completeness, sources, citations."""
    issues: list[Issue] = []

    if not re.search(r"##\s+Hofstede", readme_text, re.IGNORECASE):
        issues.append(Issue(
            error=f"{country_name}: README missing Hofstede section",
            verdict="add `## Hofstede Cultural Dimensions` section to README",
        ))
        return issues

    missing = [d for d in HOFSTEDE_DIMENSIONS if d not in scores]
    if missing:
        issues.append(Issue(
            error=f"{country_name}: Hofstede scores incomplete",
            verdict=(
                f"add table rows `| DIM | NN | **Low/High/Very High** ... |` "
                f"for: {', '.join(missing)}"
            ),
        ))

    if not re.search(r"hofstede|empirical|research", readme_text, re.IGNORECASE):
        issues.append(Issue(
            error=f"{country_name}: Hofstede scores lack source attribution",
            verdict="add source line: '**Source:** Hofstede Insights' or explain if approximation",
        ))

    references_path = country_dir / "REFERENCES.md"
    if references_path.exists():
        if "Hofstede" not in references_path.read_text(encoding="utf-8"):
            issues.append(Issue(
                error=f"{country_name}: REFERENCES.md missing Hofstede citation",
                verdict="add Hofstede source entry: author, book/database, URL, trust level",
            ))

    position_files = list(country_dir.glob("culture_*_position.md"))
    if position_files:
        position_text = position_files[0].read_text(encoding="utf-8")
        if not POSITION_DIMENSION_REF.search(position_text):
            issues.append(Issue(
                error=f"{country_name}/{position_files[0].name}: no Hofstede dimension references",
                verdict="add explanation of how position embodies/reflects Hofstede dimensions",
            ))

    return issues


def get_expected_keywords(scores: dict[str, tuple[int, str]]) -> dict[str, set[str]]:
    """Get expected keywords for each dimension based on its score level."""
    expected: dict[str, set[str]] = {}
    for dim, (_score, level) in scores.items():
        if dim not in DIMENSION_KEYWORDS:
            continue
        polarity = "low" if "LOW" in level else "high"
        expected[dim] = set(DIMENSION_KEYWORDS[dim].get(polarity, []))
    return expected


def check_alignment(position_text: str, expected: dict[str, set[str]]) -> dict[str, int]:
    """Count keyword matches per dimension in position text."""
    matches: dict[str, int] = {}
    position_lower = position_text.lower()
    for dim, keywords in expected.items():
        count = 0
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", position_lower):
                count += 1
        matches[dim] = count
    return matches


def validate_country(country_dir: Path) -> tuple[list[Issue], list[Issue]]:
    """Run structure pass then alignment pass.

    Returns (structure_issues, alignment_issues). Alignment is skipped if
    scores cannot be extracted or no position file exists.
    """
    readme_path = country_dir / "README.md"
    if not readme_path.exists():
        structure_issues = [Issue(
            error=f"{country_dir.name}: README.md not found",
            verdict="create README.md with Hofstede section",
        )]
        return structure_issues, []

    readme_text = readme_path.read_text(encoding="utf-8")
    scores = extract_hofstede_scores(readme_text)

    structure_issues = check_structure(
        country_dir.name, country_dir, readme_text, scores,
    )

    if not scores:
        return structure_issues, []

    position_files = list(country_dir.glob("culture_*_position.md"))
    if not position_files:
        return structure_issues, []

    position_text = position_files[0].read_text(encoding="utf-8")
    expected = get_expected_keywords(scores)
    matches = check_alignment(position_text, expected)

    alignment_issues: list[Issue] = []
    for dim in sorted(matches.keys()):
        count = matches[dim]
        _score, level = scores[dim]
        if count == 0:
            alignment_issues.append(Issue(
                error=f"{country_dir.name}/{position_files[0].name}: no alignment with {dim} ({level})",
                verdict=f"position does not reflect {level} {dim} - add keywords or revise README claim",
            ))
        elif count == 1:
            alignment_issues.append(Issue(
                error=f"{country_dir.name}/{position_files[0].name}: weak alignment with {dim} ({level})",
                verdict=f"only 1 keyword match for {dim} - strengthen position to reflect dimension",
            ))

    return structure_issues, alignment_issues


def _resolve_targets(argv: list[str]) -> list[Path]:
    if len(argv) <= 1:
        return find_country_folders()
    targets: set[Path] = set()
    regions = {"africa", "americas", "asia", "europe", "oceania"}
    for arg in argv[1:]:
        path = Path(arg)
        if not path.exists():
            continue
        for part in path.parents:
            if part.parent.name in regions:
                targets.add(part)
                break
    return sorted(targets)


def main(argv: list[str]) -> int:
    countries = _resolve_targets(argv)
    if not countries:
        print("No countries found")
        return 0

    all_structure: list[Issue] = []
    all_alignment: list[Issue] = []
    for country_dir in countries:
        structure_issues, alignment_issues = validate_country(country_dir)
        all_structure.extend(structure_issues)
        all_alignment.extend(alignment_issues)

    for issue in all_structure:
        print(f"FAIL {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")
    for issue in all_alignment:
        print(f"WARN {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")

    total = len(all_structure) + len(all_alignment)
    if total:
        print(
            f"\nHofstede: {len(all_structure)} structure issue(s), "
            f"{len(all_alignment)} alignment warning(s) across {len(countries)} country(ies)"
        )
        return 1 if all_structure else 0

    print(f"OK: {len(countries)} countries pass Hofstede structure + alignment")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
