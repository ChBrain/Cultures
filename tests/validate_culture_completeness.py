#!/usr/bin/env python3
"""L4a validator: Culture-specific completeness (per-country minimum file set).

Checks that each country folder has the minimum required files per ARCHITECTURE.md:
- Exactly 1 position file
- At least 1 piece file
- At least 1 place file
- At least 2 persona files
"""
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict

from findings import Issue


def find_country_folders() -> dict[str, list[Path]]:
    """Find all country folders under regions/ and their files.
    
    Returns:
        Dict mapping country path (e.g., "regions/europe/germany") 
        to list of its markdown files.
    """
    regions = Path("regions")
    if not regions.exists():
        return {}
    
    countries = defaultdict(list)
    
    # Find all .md files and group by country folder
    for md_file in sorted(regions.glob("**/*.md")):
        # Country folder is 2 levels up from the file (regions/REGION/COUNTRY/file.md)
        if md_file.parent.parent.parent == regions:
            country_path = str(md_file.parent)
            countries[country_path].append(md_file)
    
    return dict(countries)


def validate_country(country_path: str, files: list[Path]) -> list[Issue]:
    """Validate a single country's file completeness.
    
    Args:
        country_path: Path to country folder (e.g., "regions/europe/germany")
        files: All markdown files in that country
        
    Returns:
        List of Issue objects (errors if requirements not met).
    """
    issues = []
    
    # Categorize files by type
    positions = [f for f in files if "_position.md" in f.name]
    pieces = [f for f in files if "_piece_" in f.name]
    places = [f for f in files if "_place_" in f.name]
    personas = [f for f in files if f.name.startswith("persona_")]
    
    # Check position count (exactly 1)
    if len(positions) == 0:
        issues.append(Issue(
            error=f"{country_path}: Missing position file",
            verdict="Create exactly 1 file: culture_<adj>_position.md"
        ))
    elif len(positions) > 1:
        issues.append(Issue(
            error=f"{country_path}: Too many position files ({len(positions)})",
            verdict="Only 1 position file allowed per country"
        ))
    
    # Check piece count (at least 1)
    if len(pieces) == 0:
        issues.append(Issue(
            error=f"{country_path}: Missing piece file(s)",
            verdict="Create at least 1 file: culture_<adj>_piece_<descriptor>.md"
        ))
    
    # Check place count (at least 1)
    if len(places) == 0:
        issues.append(Issue(
            error=f"{country_path}: Missing place file(s)",
            verdict="Create at least 1 file: culture_<adj>_place_<descriptor>.md"
        ))
    
    # Check persona count (at least 2)
    if len(personas) < 2:
        issues.append(Issue(
            error=f"{country_path}: Too few personas ({len(personas)})",
            verdict="Create at least 2 persona files: persona_<name>.md (minimum: 1 male, 1 female)"
        ))
    
    return issues


def validate(changed_files: list[Path] | None = None) -> list[Issue]:
    """Validate culture completeness for all countries.
    
    Args:
        changed_files: If provided, only check countries that contain changed files.
                      Otherwise check all countries.
    
    Returns:
        List of Issue objects (errors if any country fails completeness check).
    """
    issues = []
    
    countries = find_country_folders()
    if not countries:
        return issues
    
    # If checking specific files, find which countries they belong to
    countries_to_check = set(countries.keys())
    if changed_files:
        changed_set = set(changed_files)
        countries_to_check = {
            country for country, files in countries.items()
            if any(f in changed_set for f in files)
        }
    
    # Validate each country
    for country_path in sorted(countries_to_check):
        country_issues = validate_country(country_path, countries[country_path])
        issues.extend(country_issues)
    
    return issues


def main(argv: list[str]) -> int:
    """Entry point. Args are file paths (optional)."""
    changed_files = None
    if len(argv) > 1:
        changed_files = [Path(f) for f in argv[1:]]
    
    issues = validate(changed_files)
    
    if not issues:
        print(f"OK: Culture completeness validation passed")
        return 0
    
    # Print issues
    for issue in issues:
        print(f"FAIL {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")
    
    print(f"\n{len(issues)} completeness issues found")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
