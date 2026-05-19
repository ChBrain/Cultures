"""L4b: Per-country README must have a non-empty Content Audit Status table."""
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


def _audit_rows(text: str) -> list[str] | None:
    m = _SECTION_RE.search(text)
    if not m:
        return None
    start = m.end()
    nxt = re.search(r"\n##\s+", text[start:])
    section = text[start: start + nxt.start()] if nxt else text[start:]
    rows = []
    for line in section.split("\n"):
        if _HEADER_RE.search(line) or _SEP_RE.match(line):
            continue
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 1 and cells[1]:
                rows.append(_cell_filename(cells[1]))
    return rows


_COUNTRIES = _country_dirs()


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_readme_exists(country_dir: Path):
    assert (country_dir / "README.md").is_file(), f"{country_dir.name}: README.md not found"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_audit_section_present(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    rows = _audit_rows(readme.read_text(encoding="utf-8", errors="replace"))
    assert rows is not None, (
        f"{country_dir.name}/README.md: no '## Content Audit Status' section"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_audit_table_not_empty(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    rows = _audit_rows(readme.read_text(encoding="utf-8", errors="replace"))
    if rows is None:
        pytest.skip("no audit section")
    assert rows, f"{country_dir.name}/README.md: Audit Status table is empty"


def test_cell_filename_accepts_link_or_plain():
    assert _cell_filename("culture_x.md") == "culture_x.md"
    assert _cell_filename("`culture_x.md`") == "culture_x.md"
    assert _cell_filename("[culture_x.md](culture_x.md)") == "culture_x.md"
    assert _cell_filename("[`culture_x.md`](./culture_x.md)") == "culture_x.md"
