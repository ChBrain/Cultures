#!/usr/bin/env python3
"""Hofstede dimension alignment validation.

Checks that a culture's Position file actually reflects the Hofstede dimensions
documented in the README. This prevents declaring one dimensional profile while
writing a position that contradicts it.

The validator reads Hofstede scores from README, extracts expected keywords/concepts
for each dimension, and verifies the position file contains matching language.

Exit status:
  0 if alignment is good, 1 if mismatches found.

Usage:
  tests/validate_hofstede_alignment.py            # all countries
  tests/validate_hofstede_alignment.py FILE...    # specific files
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue


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


def find_country_folders() -> list[Path]:
    """Find all country folders with content."""
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
            if list(country_dir.glob("culture_*_position.md")):
                countries.append(country_dir)
    return countries


def extract_hofstede_scores(readme_text: str) -> dict[str, tuple[int, str]]:
    """Extract Hofstede scores and their descriptions from README.
    
    Returns: {dimension: (score, description)}
    """
    scores = {}
    
    # Pattern: "| PDI | 35 | **Low** - ..."
    pattern = r"\|\s*(PDI|IDV|UAI|MAS|LTO|IND)\s*\|\s*(\d+)\s*\|\s*\*\*(Low|High|Very High)[^\|]*\|"
    
    for match in re.finditer(pattern, readme_text, re.IGNORECASE):
        dim = match.group(1).upper()
        score = int(match.group(2))
        level = match.group(3).upper()
        scores[dim] = (score, level)
    
    return scores


def get_expected_keywords(scores: dict[str, tuple[int, str]]) -> dict[str, set[str]]:
    """Get expected keywords for each dimension based on its score level."""
    expected = {}
    
    for dim, (score, level) in scores.items():
        if dim not in DIMENSION_KEYWORDS:
            continue
        
        keywords = DIMENSION_KEYWORDS[dim].copy()
        
        # Determine if this dimension is "high" or "low"
        # Special cases: PDI/UAI/MAS are named intuitively (high = the named trait)
        # IDV: high = individualism, low = collectivism
        # LTO: high = long-term, low = short-term
        # IND: high = indulgence, low = restraint
        
        if "Low" in level or "low" in level:
            # Use the "low" keywords for this dimension
            expected[dim] = set(keywords.get("low", []))
        else:
            # Use the "high" keywords
            expected[dim] = set(keywords.get("high", []))
    
    return expected


def check_alignment(position_text: str, expected: dict[str, set[str]]) -> dict[str, int]:
    """Count keyword matches for each dimension in position text."""
    matches = {}
    position_lower = position_text.lower()
    
    for dim, keywords in expected.items():
        count = 0
        for keyword in keywords:
            # Use word boundary matching to avoid partial matches
            if re.search(rf"\b{re.escape(keyword)}\b", position_lower):
                count += 1
        matches[dim] = count
    
    return matches


def validate_country(country_dir: Path) -> list[Issue]:
    """Validate Hofstede alignment for a single country."""
    issues = []
    
    readme_path = country_dir / "README.md"
    if not readme_path.exists():
        return []
    
    position_files = list(country_dir.glob("culture_*_position.md"))
    if not position_files:
        return []
    
    readme_text = readme_path.read_text(encoding="utf-8")
    position_text = position_files[0].read_text(encoding="utf-8")
    
    # Extract claimed Hofstede scores
    scores = extract_hofstede_scores(readme_text)
    if not scores:
        return []  # No Hofstede section to validate against
    
    # Get expected keywords
    expected = get_expected_keywords(scores)
    
    # Check alignment
    matches = check_alignment(position_text, expected)
    
    # Report findings
    for dim in sorted(matches.keys()):
        count = matches[dim]
        score, level = scores[dim]
        
        if count == 0:
            # No keywords found for this dimension
            issues.append(Issue(
                error=f"{country_dir.name}/culture_*_position.md: no alignment with {dim} ({level})",
                verdict=f"position does not reflect {level} {dim} - add keywords or revise README claim",
            ))
        elif count == 1:
            # Only one keyword - weak alignment
            issues.append(Issue(
                error=f"{country_dir.name}/culture_*_position.md: weak alignment with {dim} ({level})",
                verdict=f"only 1 keyword match for {dim} - strengthen position to reflect dimension",
            ))
    
    return issues


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        # Validate specific files' countries
        targets = set()
        for arg in argv[1:]:
            path = Path(arg)
            if path.exists():
                for part in path.parents:
                    if part.parent.name in ["africa", "americas", "asia", "europe", "oceania"]:
                        targets.add(part)
                        break
        countries = sorted(targets)
    else:
        countries = find_country_folders()
    
    all_issues = []
    for country_dir in countries:
        issues = validate_country(country_dir)
        all_issues.extend(issues)
    
    if all_issues:
        for issue in all_issues:
            print(f"WARN {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        print(f"\nHofstede alignment: {len(all_issues)} potential mismatch(es) found")
        return 1
    
    print(f"OK: {len(countries)} countries have positions aligned with Hofstede dimensions")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
