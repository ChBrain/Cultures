#!/usr/bin/env python3
"""Hofstede Cultural Dimensions validation for Cultures world.

Checks that each country's documentation includes:
  - Hofstede dimension scores in README
  - Position file references to Hofstede or dimensions
  - Source attribution for scores

Exit status:
  0 if every country passes, 1 otherwise.

Usage:
  tests/validate_hofstede.py            # walks regions/
  tests/validate_hofstede.py FILE...    # validates files in same country

This validator runs per-country, not per-file. It checks README and REFERENCES
together as the documentation unit for a country's Hofstede mapping.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue

# The six standard Hofstede dimensions
HOFSTEDE_DIMENSIONS = {
    "Power Distance": ["PDI", "Power Distance Index"],
    "Individualism": ["IDV", "Individualism"],
    "Uncertainty Avoidance": ["UAI", "Uncertainty Avoidance Index"],
    "Masculinity": ["MAS", "Masculinity"],
    "Long-Term Orientation": ["LTO", "Long-Term Orientation"],
    "Indulgence": ["IND", "Indulgence"],
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
            # Only include if has content files
            content_files = list(country_dir.glob("culture_*.md")) + list(country_dir.glob("persona_*.md"))
            if content_files:
                countries.append(country_dir)
    return countries


def validate_country(country_dir: Path) -> list[Issue]:
    """Validate Hofstede mapping for a single country."""
    issues = []
    
    # 1. Check README exists
    readme_path = country_dir / "README.md"
    if not readme_path.exists():
        return [Issue(
            error=f"{country_dir.name}: README.md not found",
            verdict="create README.md with Hofstede section",
        )]
    
    readme_text = readme_path.read_text(encoding="utf-8")
    
    # 2. Check README has Hofstede section
    if not re.search(r"##\s+Hofstede", readme_text, re.IGNORECASE):
        issues.append(Issue(
            error=f"{country_dir.name}: README missing Hofstede section",
            verdict="add `## Hofstede Cultural Dimensions` section to README",
        ))
    else:
        # 3. Check for dimension scores in README
        has_table = bool(re.search(r"\|\s*(Dimension|PDI|IDV|UAI|MAS|LTO|IND)", readme_text))
        
        if not has_table:
            issues.append(Issue(
                error=f"{country_dir.name}: Hofstede section has no score table",
                verdict="add table with all 6 dimensions and scores (0-100)",
            ))
        else:
            # Count how many dimensions are present in the table
            found_dimensions = set()
            for short_code in ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]:
                # Search for dimension codes in table format: | PDI | or (PDI)
                if re.search(f"\\|\\s*{short_code}\\s*\\||\\({short_code}\\)|\\b{short_code}\\b", readme_text):
                    found_dimensions.add(short_code)
            
            if len(found_dimensions) < 6:
                missing = set(["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]) - found_dimensions
                issues.append(Issue(
                    error=f"{country_dir.name}: Hofstede scores incomplete",
                    verdict=f"add scores for: {', '.join(sorted(missing))}",
                ))
        
        # 4. Check for source attribution (Hofstede, empirical, etc.)
        has_source = bool(re.search(
            r"(Hofstede|empirical|research|Hofstede Insights|hofstede-insights)",
            readme_text,
            re.IGNORECASE
        ))
        
        if not has_source:
            issues.append(Issue(
                error=f"{country_dir.name}: Hofstede scores lack source attribution",
                verdict="add source line: '**Source:** Hofstede Insights' or explain if approximation",
            ))
    
    # 5. Check REFERENCES.md for Hofstede citations (optional but recommended)
    references_path = country_dir / "REFERENCES.md"
    if references_path.exists():
        references_text = references_path.read_text(encoding="utf-8")
        if "Hofstede" not in references_text:
            issues.append(Issue(
                error=f"{country_dir.name}: REFERENCES.md missing Hofstede citation",
                verdict="add Hofstede source entry: author, book/database, URL, trust level",
            ))
    
    # 6. Check position file exists and references dimensions (optional but encouraged)
    position_files = list(country_dir.glob("culture_*_position.md"))
    if position_files:
        position_text = position_files[0].read_text(encoding="utf-8")
        # Check for any reference to Hofstede or dimensions
        has_dimension_ref = bool(re.search(
            r"(Hofstede|Power Distance|Individualism|Uncertainty Avoidance|"
            r"Masculinity|Long-Term Orientation|Indulgence|PDI|IDV|UAI|MAS|LTO|IND)",
            position_text,
            re.IGNORECASE
        ))
        
        if not has_dimension_ref:
            issues.append(Issue(
                error=f"{country_dir.name}/culture_*_position.md: No Hofstede dimension references",
                verdict="add explanation of how position embodies/reflects Hofstede dimensions",
            ))
    
    return issues


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        # Validate files' countries only
        targets = set()
        for arg in argv[1:]:
            path = Path(arg)
            if path.exists():
                # Find country folder
                for part in path.parents:
                    if (part.parent.name in ["africa", "americas", "asia", "europe", "oceania"]):
                        targets.add(part)
                        break
        countries = sorted(targets)
    else:
        countries = find_country_folders()
    
    if not countries:
        print("No countries found")
        return 0
    
    all_issues = []
    for country_dir in countries:
        issues = validate_country(country_dir)
        all_issues.extend(issues)
    
    if all_issues:
        for issue in all_issues:
            print(f"FAIL {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        
        print(f"\nHofstede validation failed: {len(all_issues)} issue(s) found")
        return 1
    
    print(f"OK: {len(countries)} countries have valid Hofstede mapping")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
