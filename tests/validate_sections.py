#!/usr/bin/env python3
"""L2 validation: per-file-type section structure.

Checks that each file type has its required sections in order:
  - position: Owner, Has, Orders, Loses, Drives
  - piece: Owner, Place, Load Bearing, Apparent, Yearbook
  - place: Owner, Shown, Holds, Offers, Withheld
  - persona: Owner, Projection, Action, Shadow, Tell

Exit status:
  0 if every file passes, 1 otherwise.

Usage:
  tests/validate_sections.py            # walks regions/
  tests/validate_sections.py FILE...    # validates only the given files
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from findings import Issue

# Section requirements per file type
SECTION_REQUIREMENTS = {
    "position": ["Owner", "Has", "Orders", "Loses", "Drives"],
    "piece": ["Owner", "Place", "Load Bearing", "Apparent", "Yearbook"],
    "place": ["Owner", "Shown", "Holds", "Offers", "Withheld"],
    "persona": ["Owner", "Projection", "Action", "Shadow", "Tell"],
}


def get_file_type(path: Path) -> str | None:
    """Determine file type from basename pattern."""
    name = path.name
    if name.startswith("culture_") and "_position.md" in name:
        return "position"
    elif name.startswith("culture_") and "_piece_" in name:
        return "piece"
    elif name.startswith("culture_") and "_place_" in name:
        return "place"
    elif name.startswith("persona_"):
        return "persona"
    return None


def extract_sections(text: str) -> list[str]:
    """Extract all section headings (##) from the file."""
    pattern = r"^## (.+?)$"
    return [m.group(1) for m in re.finditer(pattern, text, re.MULTILINE)]


def validate(path: Path) -> list[Issue]:
    """Validate file structure."""
    issues: list[Issue] = []

    file_type = get_file_type(path)
    if not file_type:
        # Not a typed file; skip validation
        return issues

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [Issue(error=f"Could not read file: {exc}", verdict=None)]

    sections = extract_sections(text)
    required = SECTION_REQUIREMENTS[file_type]

    # Check each required section exists
    for req in required:
        if req not in sections:
            issues.append(Issue(
                error=f"{file_type} missing required section: ## {req}",
                verdict=f"Add section ## {req}",
            ))

    # Check section order (first N required sections should appear in order)
    found_indices = []
    for req in required:
        if req in sections:
            found_indices.append(sections.index(req))

    if found_indices and found_indices != sorted(found_indices):
        issues.append(Issue(
            error=f"{file_type} sections are out of order",
            verdict=f"Reorder sections: {', '.join(required)}",
        ))

    return issues


def find_md_files(root: Path) -> list[Path]:
    """Find all culture files in regions/."""
    regions = root / "regions"
    if not regions.is_dir():
        return []
    return sorted(p for p in regions.rglob("*.md") if ".git" not in p.parts)


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    targets = [Path(a) for a in argv[1:]] if len(argv) > 1 else find_md_files(root)

    failed = 0
    for path in targets:
        # Skip files that don't have a type
        if not get_file_type(path):
            continue

        issues = validate(path)
        if issues:
            failed += 1
            print(f"FAIL {path}")
            for issue in issues:
                print(f"  - {issue.error}")
                if issue.verdict:
                    print(f"    verdict: {issue.verdict}")

    typed_files = [p for p in targets if get_file_type(p)]
    if typed_files:
        if failed:
            print(f"\n{failed}/{len(typed_files)} files failed section validation")
            return 1
        print(f"OK: {len(typed_files)} files passed section validation")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
