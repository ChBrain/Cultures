"""Cultures-specific section and owner rules.

Covers what khai component tests do NOT check:
  - Owner block format (Project: Cultures + Culture/Scope)
  - Required sections appear in canonical order
  - Persona Projection contains gender and culture position links
  - Persona `type` value, one-line Title, stamp.date quoting (PR-scoped)
  - Persona Projection language-ladder completeness (PR-scoped)

Cultures layers specialized kind names on top of KAI's 5 generic
component structures. The alias map below resolves Cultures-specific
filename tokens to their KAI structural type so v2 schema files
(history -> piece structure, male/female -> persona structure, language
-> position structure) get the same section-order validation that
their KAI structural cousins get.
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

# Cultures-specific kind tokens (in filenames) -> KAI structural type.
# Each entry on the left can appear in a filename; the right is the KAI
# component whose section-order contract applies. KAI types map to
# themselves (process / position / piece / place / persona); Cultures-
# specific kinds (language / history / male / female) map to the KAI
# structure they reuse.
_CULTURES_KIND_TO_KHAI: dict[str, str] = {
    # KAI components (self-mapping)
    "process":  "process",
    "position": "position",
    "piece":    "piece",
    "place":    "place",
    "persona":  "persona",
    # Cultures-specific kinds layered on KAI structures
    "language": "position",   # culture_<adj>_language_<slug>.md uses HOLD (Has/Orders/Loses/Drives)
    "history":  "piece",      # culture_<adj>_history_<slug>.md uses PLAY (Place/Load Bearing/Apparent/Yearbook)
    "male":     "persona",    # culture_<adj>_male_<name>.md uses PAST (Projection/Action/Shadow/Tell)
    "female":   "persona",    # culture_<adj>_female_<name>.md uses PAST
}


def _component_type(path: Path) -> str | None:
    """Resolve a Cultures filename to its KAI structural component type.

    Splits the filename stem on underscore and returns the KAI type for
    the first token that matches a known Cultures kind. Returns None for
    files that don't carry any recognized kind token (README, REFERENCES,
    hofstede_decisions, etc.) -- those skip the section-order checks.
    """
    parts = path.stem.lower().split("_")
    for token in parts:
        if token in _CULTURES_KIND_TO_KHAI:
            return _CULTURES_KIND_TO_KHAI[token]
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


# --- Frontmatter and ladder rules (PR-scoped via --khai-files) -------------
#
# Enforced per-PR, not repo-wide: these iterate the files in --khai-files
# (the changed culture files for the PR) rather than the global md_file
# fixture. Repo-wide enforcement would retroactively fail the countries
# migrated before these rules existed; PR scoping challenges each country
# when its own migration PR runs. Mirrors test_no_orphans in test_links.py.

_LADDER_CHANNELS = ("speaking", "hearing", "writing", "reading")
_VALID_PERSONA_TYPES = frozenset({"composite"})


def _frontmatter(text: str) -> str | None:
    """Return the raw YAML frontmatter block, or None if the file has none."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else None


def _khai_files(pytestconfig) -> list[Path]:
    """The .md files passed via --khai-files, as resolved paths."""
    try:
        raw = pytestconfig.getoption("--khai-files") or ""
    except ValueError:
        raw = ""
    root = Path(pytestconfig.rootdir)
    return [(root / part).resolve() for part in raw.split() if part.endswith(".md")]


def test_persona_type(pytestconfig):
    """Persona `type` is lowercase and in the allowed set (`composite`)."""
    files = _khai_files(pytestconfig)
    if not files:
        pytest.skip("--khai-files not provided; PR-scoped check")
    failures: list[str] = []
    for f in files:
        if not f.exists() or _component_type(f) != "persona":
            continue
        fm = _frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        if fm is None:
            continue
        m = re.search(r"^type:[ \t]*(\S+)[ \t]*$", fm, re.MULTILINE)
        if not m:
            failures.append(f"{f.name}: persona frontmatter missing 'type:'")
            continue
        value = m.group(1)
        if value != value.lower():
            failures.append(f"{f.name}: type must be lowercase; got {value!r}")
        elif value not in _VALID_PERSONA_TYPES:
            failures.append(
                f"{f.name}: type must be one of "
                f"{sorted(_VALID_PERSONA_TYPES)}; got {value!r}"
            )
    assert not failures, "persona type:\n  " + "\n  ".join(failures)


def test_persona_title_one_line(pytestconfig):
    """Persona Title is a single line: `## Title: <role>`."""
    files = _khai_files(pytestconfig)
    if not files:
        pytest.skip("--khai-files not provided; PR-scoped check")
    failures: list[str] = []
    for f in files:
        if not f.exists() or _component_type(f) != "persona":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^## Title\b", text, re.MULTILINE):
            continue
        if re.search(r"^## Title[ \t]*$", text, re.MULTILINE):
            failures.append(
                f"{f.name}: Title must be one line '## Title: <role>', "
                f"not '## Title' with the role on the next line"
            )
        elif not re.search(r"^## Title: \S.*$", text, re.MULTILINE):
            failures.append(f"{f.name}: Title must match '## Title: <role>'")
    assert not failures, "persona Title:\n  " + "\n  ".join(failures)


def test_stamp_date_quoted(pytestconfig):
    """stamp.date is a quoted ISO string: `date: 'YYYY-MM-DD'`."""
    files = _khai_files(pytestconfig)
    if not files:
        pytest.skip("--khai-files not provided; PR-scoped check")
    failures: list[str] = []
    for f in files:
        if not f.exists() or _component_type(f) is None:
            continue
        fm = _frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        if fm is None:
            continue
        m = re.search(r"^[ \t]*date:[ \t]*(.+?)[ \t]*$", fm, re.MULTILINE)
        if not m:
            continue
        if not re.fullmatch(r"'\d{4}-\d{2}-\d{2}'", m.group(1)):
            failures.append(
                f"{f.name}: stamp.date must be a quoted ISO date "
                f"'YYYY-MM-DD'; got {m.group(1)!r}"
            )
    assert not failures, "stamp.date:\n  " + "\n  ".join(failures)


def test_persona_projection_ladder(pytestconfig):
    """If a persona's Projection adopts the language ladder, it covers all
    four channels. Skip-tolerant per file: a persona with no ladder links is
    not yet migrated and is not failed."""
    files = _khai_files(pytestconfig)
    if not files:
        pytest.skip("--khai-files not provided; PR-scoped check")
    failures: list[str] = []
    for f in files:
        if not f.exists() or _component_type(f) != "persona":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^## Projection$(.+?)^##", text, re.MULTILINE | re.DOTALL)
        if not m:
            continue
        proj = m.group(1)
        found = {
            ch for ch in _LADDER_CHANNELS
            if re.search(rf"process_{ch}_[a-z_]+\.md", proj)
        }
        if not found:
            continue  # ladder not adopted yet
        missing = [ch for ch in _LADDER_CHANNELS if ch not in found]
        if missing:
            failures.append(
                f"{f.name}: Projection uses the language ladder but is "
                f"missing channel(s) {missing}; a persona that adopts the "
                f"ladder covers all four {list(_LADDER_CHANNELS)}"
            )
    assert not failures, "Projection ladder:\n  " + "\n  ".join(failures)
