"""L4c: Audit table must list exactly the content files on disk — no orphans, no gaps."""
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent

_SECTION_RE = re.compile(r"##\s+(Content\s+)?Audit\s+Status\s*\n", re.IGNORECASE)
_HEADER_RE = re.compile(r"File.*Type", re.IGNORECASE)
_SEP_RE = re.compile(r"^\s*\|\s*-+")
_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _cell_filename(cell: str) -> str:
    """Filename from an audit-table File cell.

    The cell may be a bare name, a backticked name, or a markdown link
    ``[name](target)`` -- links give the reader navigation. The link
    target is the file path; everything reduces to the basename.
    """
    cell = cell.strip()
    m = _LINK_RE.search(cell)
    if m:
        cell = m.group(1).split("#", 1)[0]
    return Path(cell.strip().strip("`").strip()).name


def _country_dirs() -> list[Path]:
    regions = _ROOT / "regions"
    if not regions.is_dir():
        return []
    countries = []
    for region_dir in sorted(regions.iterdir()):
        if not region_dir.is_dir() or region_dir.name.startswith("."):
            continue
        for country_dir in sorted(region_dir.iterdir()):
            if not country_dir.is_dir() or country_dir.name.startswith("."):
                continue
            if not (country_dir / "README.md").is_file():
                continue
            has_content = any(
                f.suffix == ".md" and any(p in f.name for p in ("culture_", "persona_"))
                for f in country_dir.iterdir()
            )
            if has_content:
                countries.append(country_dir)
    return countries


def _content_files(country_dir: Path) -> set[str]:
    return {
        f.name for f in country_dir.iterdir()
        if f.suffix == ".md" and any(p in f.name for p in ("culture_", "persona_"))
    }


def _audit_files(text: str) -> set[str]:
    m = _SECTION_RE.search(text)
    if not m:
        return set()
    start = m.end()
    nxt = re.search(r"\n##\s+", text[start:])
    section = text[start: start + nxt.start()] if nxt else text[start:]
    files: set[str] = set()
    for line in section.split("\n"):
        if _HEADER_RE.search(line) or _SEP_RE.match(line):
            continue
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 1 and cells[1]:
                name = _cell_filename(cells[1])
                if not name.endswith(".md"):
                    name += ".md"
                files.add(name)
    return files


_COUNTRIES = _country_dirs()


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_no_orphaned_audit_entries(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    listed = _audit_files(readme.read_text(encoding="utf-8", errors="replace"))
    if not listed:
        pytest.skip("no audit table")
    orphans = sorted(listed - _content_files(country_dir))
    assert not orphans, (
        f"{country_dir.name}/README.md: audit table lists files not on disk: {orphans}"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_no_missing_audit_entries(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    listed = _audit_files(readme.read_text(encoding="utf-8", errors="replace"))
    if not listed:
        pytest.skip("no audit table")
    missing = sorted(_content_files(country_dir) - listed)
    assert not missing, (
        f"{country_dir.name}/README.md: files on disk missing from audit table: {missing}"
    )


def test_audit_files_parses_linked_cells():
    table = (
        "## Content Audit Status\n\n"
        "| File | TYPE | Status |\n"
        "|------|------|--------|\n"
        "| [culture_x_position.md](culture_x_position.md) | position | ok |\n"
        "| `culture_x_place_y.md` | place | ok |\n"
    )
    assert _audit_files(table) == {
        "culture_x_position.md", "culture_x_place_y.md",
    }
