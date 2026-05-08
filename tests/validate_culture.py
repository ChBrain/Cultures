#!/usr/bin/env python3
"""L4 validator: Culture-specific rules (Cultures orchestrator).

Calls child validators that enforce Cultures-specific requirements.

Child validators:
- L4a: validate_culture_completeness.py - per-country minimum file set
- L4b: validate_audit_readme.py - per-country README with audit status table
- L4c: validate_audit_consistency.py - audit table matches actual files
- L4d: validate_plagiarism.py - IP/plagiarism heuristics
- L4e: validate_hofstede_alignment.py - position reflects Hofstede dimensions
- L4f: validate_hofstede_derived.py - content keywords vs declared scores (advisory)
- L4g: validate_hofstede_readme_audit.py - audit table sync (advisory)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from findings import Issue


def run_child_validator(script: str, changed_files: list[Path] | None = None) -> list[Issue]:
    """Run a child validator script and parse its output.
    
    Args:
        script: Path to validator script (e.g., "tests/validate_culture_completeness.py")
        changed_files: Optional list of files to check (passed as args to script)
        
    Returns:
        List of Issue objects from the validator output.
    """
    issues = []
    
    cmd = [sys.executable, script]
    if changed_files:
        cmd.extend(str(f) for f in changed_files)
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    # Parse output - each FAIL line starts an issue
    lines = result.stdout.strip().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("FAIL "):
            error = line[5:]  # Remove "FAIL " prefix
            verdict = None
            # Check next line for verdict
            if i + 1 < len(lines) and lines[i + 1].startswith("  verdict: "):
                verdict = lines[i + 1][11:]  # Remove "  verdict: " prefix
                i += 2
            else:
                i += 1
            issues.append(Issue(error=error, verdict=verdict))
        else:
            i += 1
    
    return issues


def validate(changed_files: list[Path] | None = None) -> list[Issue]:
    """Validate all Cultures-specific rules via child validators.
    
    Args:
        changed_files: If provided, only check files/countries affected by changes.
                      Otherwise check all.
    
    Returns:
        List of all Issue objects from all child validators.
    """
    issues = []
    
    # L4a: Completeness (minimum files per country)
    completeness_issues = run_child_validator("tests/validate_culture_completeness.py", changed_files)
    issues.extend(completeness_issues)
    
    # L4b: README audit table presence
    readme_issues = run_child_validator("tests/validate_audit_readme.py", changed_files)
    issues.extend(readme_issues)
    
    # L4c: Audit table consistency
    consistency_issues = run_child_validator("tests/validate_audit_consistency.py", changed_files)
    issues.extend(consistency_issues)
    
    # L4d: IP/plagiarism heuristics (warnings only)
    plagiarism_issues = run_child_validator("tests/validate_plagiarism.py", changed_files)
    issues.extend(plagiarism_issues)
    
    # L4e: Hofstede dimension alignment
    hofstede_align_issues = run_child_validator("tests/validate_hofstede_alignment.py", changed_files)
    issues.extend(hofstede_align_issues)
    
    # L4g: Hofstede audit table sync (advisory)
    audit_table_issues = run_child_validator("tests/validate_hofstede_readme_audit.py", changed_files)
    issues.extend(audit_table_issues)
    
    return issues


def main(argv: list[str]) -> int:
    """Entry point. Args are file paths (optional)."""
    changed_files = None
    if len(argv) > 1:
        changed_files = [Path(f) for f in argv[1:]]
    
    issues = validate(changed_files)
    
    if not issues:
        print(f"OK: Culture validation passed")
        return 0
    
    # Print issues
    for issue in issues:
        print(f"FAIL {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")
    
    print(f"\n{len(issues)} culture validation issues found")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
