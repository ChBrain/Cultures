#!/usr/bin/env python3
"""L4b validator: Audit README completeness.

Each country with content files must have a README.md in the country directory
containing an "Audit Status" section with a properly-formatted table listing
all content files and their audit status.

This ensures per-country transparency: audit status lives where content lives.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from findings import Issue


def find_country_folders(root: Path) -> dict[str, Path]:
    """Find all regions/REGION/COUNTRY directories that have content.
    
    Returns dict: {country_path_str: Path}
    """
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


def extract_audit_table(text: str) -> list[str] | None:
    """Extract audit status table rows from README.
    
    Looks for "Audit Status" or "Content Audit Status" section and extracts table rows.
    Returns list of file names from table (or None if no table found).
    """
    # Find "Audit Status" or "Content Audit Status" section
    audit_match = re.search(r"##\s+(Content\s+)?Audit\s+Status\s*\n", text, re.IGNORECASE)
    if not audit_match:
        return None
    
    # Extract table from that point onwards until next section or end
    section_start = audit_match.end()
    next_section = re.search(r"\n##\s+", text[section_start:])
    section_text = text[section_start:section_start + next_section.start()] if next_section else text[section_start:]
    
    # Extract table rows (lines with | separators)
    # Format: | File | Type | Verified | Status | Notes |
    # Skip header and separator lines
    lines = section_text.split("\n")
    rows = []
    for i, line in enumerate(lines):
        # Skip header row (has "File | Type")
        if "File" in line and "Type" in line:
            continue
        # Skip separator row (has dashes)
        if re.match(r"^\s*\|\s*-+", line):
            continue
        # Capture data rows
        if line.strip().startswith("|") and line.strip().endswith("|"):
            # Extract first cell (filename)
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 1 and cells[1]:  # cells[0] is empty, cells[1] is first cell
                # Normalize: remove backticks, ensure .md extension only once
                filename = cells[1].strip('`')
                if not filename.endswith(".md"):
                    filename += ".md"
                rows.append(filename)
    
    return rows if rows else None


def validate(changed_files: list[Path] | None = None) -> list[Issue]:
    """Validate per-country README audit status tables.
    
    Args:
        changed_files: List of changed file paths (optional, for CI efficiency)
                      If provided, only validates countries containing changed files
    
    Returns:
        List of Issue objects
    """
    root = Path(__file__).resolve().parent.parent
    countries = find_country_folders(root)
    
    # If changed_files provided, filter to affected countries only
    if changed_files:
        affected_countries = set()
        for f in changed_files:
            # Determine country from file path
            parts = f.parts
            if "regions" in parts:
                idx = parts.index("regions")
                if idx + 2 < len(parts):
                    country_path = Path(*parts[:idx+3])
                    affected_countries.add(str(country_path))
        countries = {k: v for k, v in countries.items() if k in affected_countries}
    
    issues = []
    
    for country_path_str, country_path in sorted(countries.items()):
        # Check for README.md
        readme = country_path / "README.md"
        if not readme.is_file():
            issues.append(Issue(
                error=f"{country_path_str}: README.md not found",
                verdict=f"Create {readme.name} with 'Audit Status' section and table"
            ))
            continue
        
        # Check README has audit section
        readme_text = readme.read_text(encoding="utf-8", errors="replace")
        audit_rows = extract_audit_table(readme_text)
        
        if audit_rows is None:
            issues.append(Issue(
                error=f"{country_path_str}/README.md: no 'Content Audit Status' section found",
                verdict="Add '## Content Audit Status' section with table listing all content files"
            ))
            continue
        
        # Check audit table is not empty
        if not audit_rows:
            issues.append(Issue(
                error=f"{country_path_str}/README.md: 'Audit Status' table is empty",
                verdict="Add table rows with: | filename | type | verified | status | notes |"
            ))
            continue
    
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
        print(f"\n{len(issues)} audit README issue(s)")
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
        print(f"OK: {affected} affected country/countries have audit README status tables")
    else:
        # Standalone mode - show all
        print(f"OK: {len(countries)} countries have audit README status tables")
    sys.exit(0)
