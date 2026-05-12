"""L4a: Per-country minimum file set (position, piece, place, personas, gender mix)."""
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent

_MALE_RE = re.compile(r"\]\s*\(\s*[^)]*position_male\.md\s*\)")
_FEMALE_RE = re.compile(r"\]\s*\(\s*[^)]*position_female\.md\s*\)")
_PROJECTION_RE = re.compile(r"^## Projection\s*$(.+?)^## ", re.MULTILINE | re.DOTALL)


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
            if list(country_dir.glob("culture_*.md")) + list(country_dir.glob("persona_*.md")):
                countries.append(country_dir)
    return countries


def _files(country_dir: Path) -> dict[str, list[Path]]:
    md = list(country_dir.glob("*.md"))
    return {
        "positions": [f for f in md if "_position.md" in f.name],
        "pieces":    [f for f in md if "_piece_" in f.name],
        "places":    [f for f in md if "_place_" in f.name],
        "personas":  [f for f in md if f.name.startswith("persona_") or "_persona_" in f.name],
    }


def _gender(persona: Path) -> tuple[bool, bool]:
    text = persona.read_text(encoding="utf-8", errors="replace")
    m = _PROJECTION_RE.search(text)
    if not m:
        return False, False
    proj = m.group(1)
    return bool(_MALE_RE.search(proj)), bool(_FEMALE_RE.search(proj))


_COUNTRIES = _country_dirs()


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_exactly_one_position(country_dir: Path):
    n = len(_files(country_dir)["positions"])
    assert n == 1, f"{country_dir.name}: expected 1 position file, found {n}"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_at_least_one_piece(country_dir: Path):
    assert _files(country_dir)["pieces"], f"{country_dir.name}: no piece file"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_at_least_one_place(country_dir: Path):
    assert _files(country_dir)["places"], f"{country_dir.name}: no place file"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_at_least_two_personas(country_dir: Path):
    n = len(_files(country_dir)["personas"])
    assert n >= 2, f"{country_dir.name}: need ≥2 personas, found {n}"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_male_persona_present(country_dir: Path):
    personas = _files(country_dir)["personas"]
    if not personas:
        pytest.skip("no personas")
    assert any(_gender(p)[0] for p in personas), (
        f"{country_dir.name}: no persona links position_male.md in ## Projection"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_female_persona_present(country_dir: Path):
    personas = _files(country_dir)["personas"]
    if not personas:
        pytest.skip("no personas")
    assert any(_gender(p)[1] for p in personas), (
        f"{country_dir.name}: no persona links position_female.md in ## Projection"
    )
