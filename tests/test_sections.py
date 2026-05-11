"""Cultures-specific section and owner rules.

Covers what khai component tests do NOT check:
  - Owner block format (Project: Cultures + Culture/Scope)
  - Required sections appear in canonical order
  - Persona Projection contains gender and culture position links
"""
import re
import pytest
from pathlib import Path

_SECTION_ORDER: dict[str, list[str]] = {
    "position": ["Owner", "Has", "Orders", "Loses", "Drives"],
    "piece":    ["Owner", "Place", "Load Bearing", "Apparent", "Yearbook"],
    "place":    ["Owner", "Shown", "Holds", "Offers", "Withheld"],
    "persona":  ["Owner", "Projection", "Action", "Shadow", "Tell"],
}

_COMPONENT_TYPES = {"process", "position", "piece", "place", "persona"}


def _component_type(path: Path) -> str | None:
    parts = path.stem.lower().split("_")
    for ctype in _COMPONENT_TYPES:
        if ctype in parts:
            return ctype
    return None


def _extract_sections(text: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r"^## (.+?)$", text, re.MULTILINE)]


def _owner_items(text: str) -> list[str]:
    m = re.search(r"^## Owner\s*$\n((?:[^\n]*\n?){0,6})", text, re.MULTILINE)
    if not m:
        return []
    items = []
    for raw in m.group(1).split("\n"):
        line = raw.rstrip()
        if not line:
            if items:
                break
            continue
        if not line.startswith("- "):
            break
        items.append(line)
    return items


def test_owner_shape(md_file: Path):
    ctype = _component_type(md_file)
    if ctype is None:
        pytest.skip(f"not a component file: {md_file.name}")
    text = md_file.read_text(encoding="utf-8", errors="replace")
    if "## Owner" not in text:
        pytest.skip("no ## Owner section (caught by khai owner tests)")
    items = _owner_items(text)
    assert len(items) == 2, (
        f"{md_file.name}: Owner block must have exactly 2 items; got {len(items)}"
    )
    assert items[0] == "- Project: Cultures", (
        f"{md_file.name}: Owner first item must be '- Project: Cultures'; got {items[0]!r}"
    )
    is_engine = "engine" in md_file.parts
    expected_tier = "Scope" if is_engine else "Culture"
    assert re.match(rf"^- {expected_tier}: .+$", items[1]), (
        f"{md_file.name}: Owner second item must match '- {expected_tier}: <value>'; got {items[1]!r}"
    )
    if is_engine:
        assert items[1] == "- Scope: Universal", (
            f"{md_file.name}: engine Owner Scope must be 'Universal'; got {items[1]!r}"
        )


def test_section_order(md_file: Path):
    ctype = _component_type(md_file)
    if ctype not in _SECTION_ORDER:
        pytest.skip(f"no ordering rule for: {md_file.name}")
    text = md_file.read_text(encoding="utf-8", errors="replace")
    sections = _extract_sections(text)
    required = _SECTION_ORDER[ctype]
    found = [s for s in sections if s in required]
    expected = [s for s in required if s in found]
    assert found == expected, (
        f"{md_file.name}: sections out of order. "
        f"Found: {found}. Expected order: {required}"
    )


def test_persona_projection_links(md_file: Path):
    if _component_type(md_file) != "persona":
        pytest.skip(f"not a persona file: {md_file.name}")
    text = md_file.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^## Projection$(.+?)^##", text, re.MULTILINE | re.DOTALL)
    if not m:
        pytest.skip("no ## Projection section (caught by khai-persona)")
    proj = m.group(1)
    has_gender = bool(re.search(r"\]\s*\(\s*[^)]*position_(male|female)\.md\s*\)", proj))
    assert has_gender, (
        f"{md_file.name}: Projection missing link to position_male.md or position_female.md"
    )
    has_culture_pos = bool(re.search(r"\]\s*\(\s*[^)]*culture_[^)]*_position\.md\s*\)", proj))
    assert has_culture_pos, (
        f"{md_file.name}: Projection missing link to culture_*_position.md"
    )
