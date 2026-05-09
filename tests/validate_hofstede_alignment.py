#!/usr/bin/env python3
"""Hofstede validation: structure pass only.

Per-country structure check (FAIL, hard-block):
  - README has a `## Hofstede` section.
  - README score table contains all six dimensions (PDI, IDV, UAI, MAS, LTO, IND).
  - README has source attribution.
  - REFERENCES.md, if present, cites Hofstede.

Each `culture_*.md` file in the country should carry the Hofstede signal
footer (see ARCHITECTURE.md > Footer). This is checked as an advisory WARN
during rollout; it will graduate to a hard FAIL once all completed countries
are migrated.

Per-file dimension scoring lives in L4f (`validate_hofstede_derived.py`),
which scores aggregate keyword density across every `culture_*.md` file in
the country. L4e does not score content; it only enforces the documentation
contract. See ARCHITECTURE.md > "Scoring is Aggregate, Not Per-File".

Exit status:
  0 if every country passes the structure pass (sentinel warnings ignored
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
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from findings import Issue


HOFSTEDE_DIMENSIONS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]

# Stable sentinel for the per-file Hofstede signal footer. The leading token
# is fixed; wording after the colon may evolve. See ARCHITECTURE.md > Footer.
HOFSTEDE_SIGNAL_SENTINEL = re.compile(r"\*Hofstede signal:", re.IGNORECASE)

# Forbidden legacy footer: per-file score line implies per-file scoring.
LEGACY_SCORE_FOOTER = re.compile(
    r"\*\*Hofstede:\*\*\s*PDI\s*\d+",
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
    counted.

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

    return issues


def check_footer_sentinels(
    country_name: str,
    country_dir: Path,
) -> list[Issue]:
    """Advisory: each culture_*.md file should carry the Hofstede signal footer
    and must not carry a per-file score footer (see ARCHITECTURE.md > Footer).
    """
    issues: list[Issue] = []
    for path in sorted(country_dir.glob("culture_*.md")):
        text = path.read_text(encoding="utf-8")
        if LEGACY_SCORE_FOOTER.search(text):
            issues.append(Issue(
                error=f"{country_name}/{path.name}: legacy per-file Hofstede score footer present",
                verdict="remove `**Hofstede:** PDI ... · ...` line - scoring is aggregate, see ARCHITECTURE.md > Footer",
            ))
        if not HOFSTEDE_SIGNAL_SENTINEL.search(text):
            issues.append(Issue(
                error=f"{country_name}/{path.name}: missing Hofstede signal footer",
                verdict="add line above version footer: `*Hofstede signal: this file contributes to the culture's aggregate score. Declared dimensions live in [README.md](README.md).*`",
            ))
    return issues


def validate_country(country_dir: Path) -> tuple[list[Issue], list[Issue]]:
    """Run structure pass plus advisory footer-sentinel pass.

    Returns (structure_issues, sentinel_issues). Structure issues are
    hard-block FAIL; sentinel issues are advisory WARN during rollout.
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

    # Only check footer sentinels if README structure is intact (avoids
    # noise on countries that haven't been scaffolded yet).
    sentinel_issues: list[Issue] = []
    if not structure_issues:
        sentinel_issues = check_footer_sentinels(country_dir.name, country_dir)

    return structure_issues, sentinel_issues


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
    all_sentinel: list[Issue] = []
    for country_dir in countries:
        structure_issues, sentinel_issues = validate_country(country_dir)
        all_structure.extend(structure_issues)
        all_sentinel.extend(sentinel_issues)

    for issue in all_structure:
        print(f"FAIL {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")
    for issue in all_sentinel:
        print(f"WARN {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")

    total = len(all_structure) + len(all_sentinel)
    if total:
        print(
            f"\nHofstede: {len(all_structure)} structure issue(s), "
            f"{len(all_sentinel)} footer warning(s) across {len(countries)} country(ies)"
        )
        return 1 if all_structure else 0

    print(f"OK: {len(countries)} countries pass Hofstede structure + footer")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
