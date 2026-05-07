#!/usr/bin/env python3
"""L4c validator: Audit table consistency.

Ensures that the audit status table in each country's README.md lists exactly
the content files that exist in that country's directory - no orphans, no
missing files.

This guards against audit tables getting out of sync when files are added/removed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from findings import Issue


def find_country_folders(root: Path) -> dict[str, Path]:
    """Find all regions/REGION/COUNTRY directories that have content."""
    regions = root / "regions"
    if not regions.is_dir():
        return {}
    
    countries = {}
    for country_dir in sorted(regions.rglob("*")):
        if not country_dir.is_dir() or ".git" in country_dir.parts:
            continue
        # Check if this directory has any content files
        has_content = any(
            f.suffix == ".md" and any(
                pattern in f.name for pattern in [
                    "culture_", "persona_"
                ]
            )
            for f in country_dir.iterdir()
        )
        if has_content:
            countries[str(country_dir)] = country_dir
    
    return countries


def get_content_files(country_path: Path) -> set[str]:
    """Get all content file basenames in a country directory.
    
    Returns set of filenames like: {culture_german_position.md, persona_hanna.md, ...}
    """
    files = set()
    for f in country_path.iterdir():
        if f.suffix == ".md" and any(
            pattern in f.name for pattern in ["culture_", "persona_"]
        ):
            files.add(f.name)
    return files


def extract_audit_files(text: str) -> set[str]:
    """Extract filenames from audit status table.
    
    Returns set of filenames listed in the table.
    """
    # Find "Audit Status" or "Content Audit Status" section
    audit_match = re.search(r"##\s+(Content\s+)?Audit\s+Status\s*\n", text, re.IGNORECASE)
    if not audit_match:
        return set()
    
    # Extract table from that point onwards
    section_start = audit_match.end()
    next_section = re.search(r"\n##\s+", text[section_start:])
    section_text = text[section_start:section_start + next_section.start()] if next_section else text[section_start:]
    
    # Extract filenames from first table column
    files = set()
    lines = section_text.split("\n")
    for line in lines:
        # Skip header and separator rows
        if "File" in line or re.match(r"^\s*\|\s*-+", line):
            continue
        # Extract filename from first cell
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 1 and cells[1]:
                # Normalize: remove backticks, ensure .md extension only once
                filename = cells[1].strip('`')
                if not filename.endswith(".md"):
                    filename += ".md"
                files.add(filename)
    
    return files


def validate(changed_files: list[Path] | None = None) -> list[Issue]:
    """Validate consistency between content files and audit table entries.
    
    Args:
        changed_files: List of changed file paths (optional, for CI efficiency)
    
    Returns:
        List of Issue objects
    """
    root = Path(__file__).resolve().parent.parent
    countries = find_country_folders(root)
    
    # If changed_files provided, filter to affected countries only
    if changed_files:
        affected_countries = set()
        for f in changed_files:
            parts = f.parts
            if "regions" in parts:
                idx = parts.index("regions")
                if idx + 2 < len(parts):
                    country_path = Path(*parts[:idx+3])
                    affected_countries.add(str(country_path))
        countries = {k: v for k, v in countries.items() if k in affected_countries}
    
    issues = []
    
    for country_path_str, country_path in sorted(countries.items()):
        # Get actual content files
        actual_files = get_content_files(country_path)
        if not actual_files:
            continue  # No content files to check
        
        # Get files listed in audit table
        readme = country_path / "README.md"
        if not readme.is_file():
            continue  # L4b validator will catch this
        
        readme_text = readme.read_text(encoding="utf-8", errors="replace")
        audit_files = extract_audit_files(readme_text)
        
        if not audit_files:
            continue  # L4b validator will catch empty table
        
        # Check for orphaned files (in audit table but not on disk)
        orphaned = audit_files - actual_files
        if orphaned:
            for orphan in sorted(orphaned):
                issues.append(Issue(
                    error=f"{country_path_str}/README.md: audit table lists '{orphan}' but file not found",
                    verdict=f"Remove '{orphan}' from audit table OR create the file"
                ))
        
        # Check for missing entries (on disk but not in audit table)
        missing = actual_files - audit_files
        if missing:
            for fname in sorted(missing):
                issues.append(Issue(
                    error=f"{country_path_str}/README.md: file '{fname}' exists but not in audit table",
                    verdict=f"Add row for '{fname}' to audit table with appropriate status"
                ))
    
    return issues


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    
    # Parse argv for changed_files if provided (from orchestrator)
    changed_files = None
    if len(sys.argv) > 1:
        changed_files = [Path(f) for f in sys.argv[1:]]
    
    # In standalone mode (no args), validate all countries
    # In orchestrator mode (with args), validate only affected countries
    issues = validate(changed_files)
    
    if issues:
        for issue in issues:
            print(f"FAIL {issue.error}")
            if issue.verdict:
                print(f"  verdict: {issue.verdict}")
        print(f"\n{len(issues)} audit consistency issue(s)")
        sys.exit(1)
    
    countries = find_country_folders(root)
    if changed_files:
        # Running from orchestrator - show affected countries only
        affected = 0
        for f in changed_files:
            parts = f.parts
            if "regions" in parts:
                idx = parts.index("regions")
                if idx + 2 < len(parts):
                    affected += 1
        print(f"OK: Audit tables consistent ({affected} affected country/countries)")
    else:
        # Standalone mode - show all
        print(f"OK: Audit tables consistent ({len(countries)} countries)")
    sys.exit(0)
