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
    elif name.startswith("culture_") and "_persona_" in name:
        return "persona"
    elif name.startswith("culture_") and "_language_" in name:
        return "language"
    elif name.startswith("culture_") and "_process_" in name:
        return "process"
    elif name.startswith("persona_"):
        return "persona"
    return None


def extract_sections(text: str) -> list[str]:
    """Extract all section headings (##) from the file."""
    pattern = r"^## (.+?)$"
    return [m.group(1) for m in re.finditer(pattern, text, re.MULTILINE)]


def validate_owner_shape(text: str, path: Path) -> list[Issue]:
    """Enforce the canonical Owner block.

    Required form, exactly two list items in order:
        ## Owner
        - Project: Cultures
        - Culture: <Country>      (files under regions/)
        - Scope: Universal        (files under engine/)

    No bold, no link decoration, no extra lines, no suffixes.
    """
    issues: list[Issue] = []

    m = re.search(r"^## Owner\s*$\n((?:[^\n]*\n?){0,6})", text, re.MULTILINE)
    if not m:
        return issues

    body = m.group(1)
    list_lines = []
    for raw in body.split("\n"):
        line = raw.rstrip()
        if not line:
            if list_lines:
                break
            continue
        if not line.startswith("- "):
            break
        list_lines.append(line)

    is_engine = any(part == "engine" for part in path.parts)
    expected_tier = "Scope" if is_engine else "Culture"

    if len(list_lines) != 2:
        issues.append(Issue(
            error=f"Owner block must be exactly two list items; found {len(list_lines)}",
            verdict=(
                "Owner is exactly two lines:\n"
                "  - Project: Cultures\n"
                f"  - {expected_tier}: <value>"
            ),
        ))
        return issues

    if list_lines[0] != "- Project: Cultures":
        issues.append(Issue(
            error=f"Owner first line must be '- Project: Cultures'; got {list_lines[0]!r}",
            verdict="Replace with: - Project: Cultures (no bold, no suffix)",
        ))

    second = list_lines[1]
    tier_match = re.match(r"^- (Culture|Scope): (.+?)\s*$", second)
    if not tier_match:
        issues.append(Issue(
            error=f"Owner second line must be '- {expected_tier}: <value>'; got {second!r}",
            verdict=f"Replace with: - {expected_tier}: <value> (no bold, no link)",
        ))
        return issues

    tier_kind = tier_match.group(1)
    tier_value = tier_match.group(2).strip()

    if tier_kind != expected_tier:
        location = "engine/" if is_engine else "regions/"
        issues.append(Issue(
            error=f"Owner second tier must be '{expected_tier}' for files in {location}; got '{tier_kind}'",
            verdict=f"Use: - {expected_tier}: <value>",
        ))
    elif expected_tier == "Scope" and tier_value != "Universal":
        issues.append(Issue(
            error=f"Engine Owner Scope must be 'Universal'; got {tier_value!r}",
            verdict="Use: - Scope: Universal",
        ))
    elif expected_tier == "Culture" and not tier_value:
        issues.append(Issue(
            error="Owner Culture value is empty",
            verdict="Use: - Culture: <Country>",
        ))

    return issues


def validate_persona_gender_links(text: str) -> list[Issue]:
    """Validate that persona Projection contains gender position links.
    
    Link validation is language-agnostic: check only the link targets (in parentheses),
    not the link text (in brackets). This supports any language for the link text.
    
    Requires:
    - Link to position_male.md (any path format, any link text)
    - Link to position_female.md (any path format, any link text)
    - Link to culture_*_position.md (any path format, any link text)
    """
    issues: list[Issue] = []
    
    # Find Projection section
    projection_match = re.search(r"^## Projection$(.+?)^##", text, re.MULTILINE | re.DOTALL)
    if not projection_match:
        issues.append(Issue(
            error="persona missing ## Projection section",
            verdict="Add section ## Projection with gender and culture position links",
        ))
        return issues
    
    projection_text = projection_match.group(1)
    
    # Check for gender links: look ONLY at link targets in (), ignore link text in []
    # Pattern: any text in [] followed by link to position_male.md or position_female.md
    has_male_link = bool(re.search(r"\]\s*\(\s*[^)]*position_male\.md\s*\)", projection_text))
    has_female_link = bool(re.search(r"\]\s*\(\s*[^)]*position_female\.md\s*\)", projection_text))
    
    if not (has_male_link or has_female_link):
        issues.append(Issue(
            error="persona Projection missing gender position link",
            verdict="Add link to position_male.md or position_female.md (e.g., [Name](engine/position_male.md))",
        ))
    
    # Check for culture link: any link to culture_*_position.md
    has_culture_link = bool(re.search(r"\]\s*\(\s*[^)]*culture_[^)]*_position\.md\s*\)", projection_text))
    
    if not has_culture_link:
        issues.append(Issue(
            error="persona Projection missing culture position link",
            verdict="Add link to culture_*_position.md (e.g., [Country](culture_german_position.md))",
        ))
    
    return issues


def validate(path: Path) -> list[Issue]:
    """Validate file structure."""
    issues: list[Issue] = []

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [Issue(error=f"Could not read file: {exc}", verdict=None)]

    # Owner-shape check applies to any file with an ## Owner section,
    # independent of file type (catches language/process/engine too).
    if "## Owner" in text:
        issues.extend(validate_owner_shape(text, path))

    file_type = get_file_type(path)
    if not file_type:
        # Not a typed file; skip the rest (section set, persona links).
        return issues

    sections = extract_sections(text)
    required = SECTION_REQUIREMENTS.get(file_type)

    if required:
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

    # Persona-specific: validate gender position links in Projection
    if file_type == "persona":
        gender_issues = validate_persona_gender_links(text)
        issues.extend(gender_issues)

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
