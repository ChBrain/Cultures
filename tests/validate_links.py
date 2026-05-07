#!/usr/bin/env python3
"""L3 validator: Link integrity (general, reusable across worlds).

This validator checks that all markdown links resolve to existing files
and detects orphaned files (exist but are never referenced).

Works for any world structure. Scans from regions/ directory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from findings import Issue


def find_all_markdown_files() -> list[Path]:
    """Find all markdown files in regions/ directory."""
    regions = Path("regions")
    if not regions.exists():
        return []
    return sorted(regions.glob("**/*.md"))


def extract_links(text: str) -> list[str]:
    """Extract markdown link targets: [text](target.md).
    
    Returns list of target paths (just the filename for relative links).
    """
    # Match [text](path.md) pattern
    pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
    matches = re.findall(pattern, text)
    return [target for _, target in matches]


def resolve_link(link: str, from_file: Path) -> Path | None:
    """Resolve a link relative to the source file's directory.
    
    Args:
        link: Link target (e.g., "culture_german_place_berlin.md")
        from_file: The file containing the link
        
    Returns:
        Resolved path if link exists, or None if resolution fails.
    """
    # If link is just a filename, resolve relative to source file's directory
    if "/" not in link and "\\" not in link:
        resolved = from_file.parent / link
        if resolved.exists():
            return resolved
        return None
    
    # If link contains path, try as-is
    resolved = Path(link)
    if resolved.exists():
        return resolved
    
    # Try relative to source file's directory
    resolved = from_file.parent / link
    if resolved.exists():
        return resolved
    
    return None


def validate(changed_files: list[Path] | None = None) -> list[Issue]:
    """Validate link integrity across all markdown files.
    
    Args:
        changed_files: If provided, only check links in these files.
                      Otherwise check all files in regions/.
    
    Returns:
        List of Issue objects (errors = broken links, orphaned files).
    """
    issues = []
    
    # Get all markdown files
    all_files = set(find_all_markdown_files())
    if not all_files:
        return issues
    
    # If checking specific files, validate their links
    files_to_check = set(changed_files) if changed_files else all_files
    referenced_files = set()
    
    for file in files_to_check:
        if not file.exists():
            continue
        
        try:
            text = file.read_text(encoding="utf-8")
        except Exception as e:
            issues.append(Issue(error=f"{file}: Could not read file: {e}", verdict="check file encoding"))
            continue
        
        links = extract_links(text)
        for link in links:
            resolved = resolve_link(link, file)
            if resolved is None:
                issues.append(Issue(
                    error=f"{file}: Link target not found: {link}",
                    verdict=f"verify file exists: regions/.../.../{link}"
                ))
            else:
                # Track all referenced files (normalize to same path format as all_files)
                referenced_files.add(resolved)
    
    # If we checked all files, also detect orphaned files
    if not changed_files:
        orphaned = all_files - referenced_files
        for file in orphaned:
            issues.append(Issue(
                error=f"{file}: Orphaned file (never referenced)",
                verdict=f"either delete the file or add a reference to it"
            ))
    
    return issues


def main(argv: list[str]) -> int:
    """Entry point. Args are file paths (optional)."""
    changed_files = None
    if len(argv) > 1:
        changed_files = [Path(f) for f in argv[1:]]
    
    issues = validate(changed_files)
    
    if not issues:
        print(f"OK: Link validation passed")
        return 0
    
    # Print issues
    for issue in issues:
        print(f"FAIL {issue.error}")
        if issue.verdict:
            print(f"  verdict: {issue.verdict}")
    
    print(f"\n{len(issues)} link issues found")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
