"""Culture-set traceability gates (ChBrain/Cultures#301, rules R4-R6).

Each fact has one home file; the package docs and the persona link graph
must reference the real culture set, not a drifted one.

  R5  REFERENCES.md per-file sections map 1:1 to the content files.
  R6  README.md per-file table rows map 1:1 to the content files.
  R4  a country's persona files together link every sibling component.

All three are xfail(strict=False) during rollout: the corpus carries
pre-existing drift (Germany's REFERENCES.md has a ghost section -- a
piece_grundgesetz that is not in the set -- and two missing ones; its
personas reach 2 of 6 siblings). Each country flips to xpass as it is
brought true; when the corpus is clean the xfail marks come off and
these become hard gates -- the same rollout pattern as the band-relabel
xfails in test_hofstede_structure.
"""
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_MD_RE = re.compile(r"\b([a-z][a-z0-9_]+\.md)\b")
_DOC_FILES = {"README.md", "REFERENCES.md"}


def _is_content(name: str) -> bool:
    """A culture-package content file: a culture component or a persona,
    whatever its current naming. Not a doc file, not a hofstede artifact."""
    return (
        name.endswith(".md")
        and name not in _DOC_FILES
        and not name.startswith("hofstede_")
    )


def _is_persona(name: str) -> bool:
    return (
        "_persona_" in name
        or "_male_" in name
        or "_female_" in name
        or name.startswith("persona_")
    )


def _country_dirs() -> list[Path]:
    regions = _ROOT / "regions"
    if not regions.is_dir():
        return []
    out = []
    for region in sorted(regions.iterdir()):
        if not region.is_dir() or region.name.startswith("."):
            continue
        for country in sorted(region.iterdir()):
            if country.is_dir() and not country.name.startswith("."):
                if any(_is_content(p.name) for p in country.glob("*.md")):
                    out.append(country)
    return out


_COUNTRIES = _country_dirs()
_IDS = [c.name for c in _COUNTRIES]


def _content_files(country: Path) -> set[str]:
    return {p.name for p in country.glob("*.md") if _is_content(p.name)}


def _cited_md(text: str, keep) -> set[str]:
    """Content-file names mentioned on lines for which keep(line) is true."""
    cited = set()
    for line in text.splitlines():
        if keep(line):
            cited.update(m for m in _MD_RE.findall(line) if _is_content(m))
    return cited


@pytest.mark.xfail(strict=False, reason="R5 rollout: REFERENCES.md drift is "
                   "corrected per-country; flips to xpass when true")
@pytest.mark.parametrize("country", _COUNTRIES, ids=_IDS)
def test_references_traces_culture_set(country: Path):
    """R5: every `### <file>` section in REFERENCES.md maps 1:1 to a real
    content file -- no ghost sections, no files without a section."""
    refs = country / "REFERENCES.md"
    if not refs.is_file():
        pytest.skip("no REFERENCES.md")
    cited = _cited_md(
        refs.read_text(encoding="utf-8", errors="replace"),
        lambda ln: ln.startswith("### "),
    )
    if not cited:
        pytest.skip("REFERENCES.md has no per-file sections")
    actual = _content_files(country)
    ghost = sorted(cited - actual)
    missing = sorted(actual - cited)
    assert not ghost and not missing, (
        f"{country.name}/REFERENCES.md out of sync with the culture set -- "
        f"ghost sections: {ghost}; files with no section: {missing}"
    )


@pytest.mark.xfail(strict=False, reason="R6 rollout: README.md per-file rows "
                   "are corrected per-country; flips to xpass when true")
@pytest.mark.parametrize("country", _COUNTRIES, ids=_IDS)
def test_readme_rows_match_files(country: Path):
    """R6: every content file named in a README table row is real, and every
    real content file appears in a README row."""
    readme = country / "README.md"
    if not readme.is_file():
        pytest.skip("no README.md")
    cited = _cited_md(
        readme.read_text(encoding="utf-8", errors="replace"),
        lambda ln: ln.lstrip().startswith("|"),
    )
    if not cited:
        pytest.skip("README.md has no per-file table rows")
    actual = _content_files(country)
    ghost = sorted(cited - actual)
    missing = sorted(actual - cited)
    assert not ghost and not missing, (
        f"{country.name}/README.md per-file rows out of sync -- "
        f"ghost rows: {ghost}; files with no row: {missing}"
    )


@pytest.mark.xfail(strict=False, reason="R4 rollout: persona link coverage is "
                   "completed per-country; flips to xpass when true")
@pytest.mark.parametrize("country", _COUNTRIES, ids=_IDS)
def test_persona_links_cover_siblings(country: Path):
    """R4: a persona lives in its culture -- across a country's persona
    files, the links must reach every sibling culture component."""
    content = _content_files(country)
    personas = {n for n in content if _is_persona(n)}
    siblings = content - personas
    if not personas or not siblings:
        pytest.skip("no personas or no sibling components")
    linked = set()
    for pf in personas:
        text = (country / pf).read_text(encoding="utf-8", errors="replace")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            linked.add(Path(target.strip()).name)
    uncovered = sorted(siblings - linked)
    assert not uncovered, (
        f"{country.name}: persona files reach "
        f"{len(siblings) - len(uncovered)}/{len(siblings)} sibling "
        f"components; unlinked: {uncovered}"
    )
