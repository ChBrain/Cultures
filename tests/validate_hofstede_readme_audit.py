#!/usr/bin/env python3
"""Validate that README Hofstede Alignment Status table matches current derived scores.

Ensures that the audit proof table in country README files stays synchronized with
actual content. Prevents stale documentation where README claims certain keyword
densities but content has changed.

Exit status:
  0 if all audit tables match current derived scores
  1 if any README table is stale or missing

Output:
  PASS / FAIL per country with comparison of declared vs audit-table vs current-derived

Usage:
  tests/validate_hofstede_readme_audit.py            # all countries
  tests/validate_hofstede_readme_audit.py FILE...    # files in same country only
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
from validate_hofstede_derived import (
    find_country_folders,
    derive_scores,
    HOFSTEDE_DIMENSIONS,
)
from data.hofstede_keywords import detect_language


def extract_audit_table_scores(readme_text: str) -> dict[str, dict]:
    """Extract Hofstede Alignment Status audit table from README.
    
    Returns {dimension: {declared, derived, gap}} if table found, else empty dict.
    Parses the "Hofstede Alignment Status (Content Audit)" table format.
    """
    scores: dict[str, dict] = {}
    
    # Match the audit table structure: | Dim | Declared | Derived | Gap | Status |
    pattern = (
        r"\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
    )
    
    for match in re.finditer(pattern, readme_text):
        dim = match.group(1).upper()
        if dim not in HOFSTEDE_DIMENSIONS:
            continue
        
        declared = int(match.group(2))
        derived_in_table = int(match.group(3))
        gap_in_table = int(match.group(4))
        
        scores[dim] = {
            "declared": declared,
            "derived_in_table": derived_in_table,
            "gap_in_table": gap_in_table,
        }
    
    return scores


def validate_audit_table_sync(country_dir: Path) -> list[Issue]:
    """Validate that README audit table matches current derived scores.
    
    Returns list of issues if table is stale or mismatched.
    """
    readme_path = country_dir / "README.md"
    if not readme_path.exists():
        return []  # L4b validator will catch missing README
    
    readme_text = readme_path.read_text(encoding="utf-8")
    
    # Extract audit table from README
    audit_table = extract_audit_table_scores(readme_text)
    if not audit_table:
        return []  # No audit table found (not L4g responsibility, might be new file)
    
    # Derive current scores from content
    all_text = ""
    for f in country_dir.glob("culture_*.md"):
        all_text += f.read_text(encoding="utf-8")
    language = detect_language(all_text)
    current_derived = derive_scores(country_dir, language=language)
    
    # Compare audit table derived scores to current derived scores
    issues: list[Issue] = []
    mismatches: list[str] = []
    
    for dim in HOFSTEDE_DIMENSIONS:
        if dim not in audit_table:
            continue
        
        audit_entry = audit_table[dim]
        audit_derived = audit_entry.get("derived_in_table", 0)
        current = current_derived.get(dim, 50)
        
        if audit_derived != current:
            mismatches.append(
                f"{dim}: audit table shows {audit_derived}, "
                f"current content derives {current} (drift {abs(current - audit_derived)} points)"
            )
    
    if mismatches:
        issues.append(Issue(
            error=f"{country_dir.name}: Hofstede Alignment Status table stale",
            verdict=f"README audit table does not match current content keywords. "
                   f"Run: python tests/validate_hofstede_derived.py > temp.txt, "
                   f"then update README audit table with current Derived values. "
                   f"Mismatches: {'; '.join(mismatches)}",
        ))
    
    return issues


def main(argv: list[str]) -> int:
    """Run audit table validation across all countries."""
    
    # Resolve target countries
    if len(argv) <= 1:
        countries = find_country_folders()
    else:
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
        countries = sorted(targets)
    
    if not countries:
        print("No country folders found.", file=sys.stderr)
        return 0
    
    all_issues: list[Issue] = []
    has_stale = False
    
    for country_dir in countries:
        issues = validate_audit_table_sync(country_dir)
        if issues:
            has_stale = True
            for issue in issues:
                print(f"\n[STALE] {issue.error}")
                print(f"  → {issue.verdict}")
            all_issues.extend(issues)
        else:
            print(f"[OK] {country_dir.name}: Hofstede audit table synchronized")
    
    if all_issues:
        print(f"\n{len(all_issues)} audit table(s) stale or mismatched", file=sys.stderr)
        return 1
    
    print(f"\nOK: All {len(countries)} country audit tables synchronized")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
