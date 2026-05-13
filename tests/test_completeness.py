"""L4a: Per-country file set check with v2 opt-in.

Countries listed in ``data/v2_migrated_countries.txt`` are validated against
the **v2 schema**:
- 8 canonical kinds required (language, history, position, process, piece,
  place, male, female)
- Every ``culture_*.md`` file must carry a ``*khai: <type>*`` footer matching
  one of the 5 KAI structural types (process, position, piece, place, persona)

Countries **not** on that list run under the **legacy v1 rules** (1 position,
>=1 piece, >=1 place, >=2 personas with mixed gender via Projection links).

The list is the per-country opt-in marker. A migration PR (culture/<country>)
adds the country to the list in the same commit that renames files and adds
khai declaration footers. Once every developed country is on the list,
stage 4 deprecates the opt-in mechanism and the validator becomes
unconditionally v2.
"""
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Legacy v1 helpers
# ---------------------------------------------------------------------------

_MALE_RE = re.compile(r"\]\s*\(\s*[^)]*position_male\.md\s*\)")
_FEMALE_RE = re.compile(r"\]\s*\(\s*[^)]*position_female\.md\s*\)")
_PROJECTION_RE = re.compile(r"^## Projection\s*$(.+?)^## ", re.MULTILINE | re.DOTALL)

# ---------------------------------------------------------------------------
# v2 helpers
# ---------------------------------------------------------------------------

# Matches the footer marker convention from KAIHACKS khai-tests v0.1.6:
#     *khai: persona*
# (lowercase prefix, italicized, one of the 5 KAI structural types as value)
_KHAI_DECLARATION_RE = re.compile(r"^\*khai:\s*(\w+)\s*\*\s*$", re.MULTILINE)
_VALID_KHAI_TYPES = frozenset({"process", "position", "piece", "place", "persona"})


def _v2_migrated() -> set[str]:
    """Country folder names that have opted into v2-strict validation.

    Reads ``data/v2_migrated_countries.txt``: one slug per line, blank
    lines and ``#`` comments ignored. Missing file -> empty set (no
    country is v2-strict; everyone runs legacy rules).
    """
    path = _ROOT / "data" / "v2_migrated_countries.txt"
    if not path.is_file():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line)
    return out


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


_COUNTRIES = _country_dirs()
_V2 = _v2_migrated()


def _is_v2(country_dir: Path) -> bool:
    return country_dir.name in _V2


def _files(country_dir: Path) -> dict[str, list[Path]]:
    """Legacy v1 file buckets, used by the legacy checks."""
    md = list(country_dir.glob("*.md"))
    return {
        "positions": [f for f in md if "_position.md" in f.name],
        "pieces":    [f for f in md if "_piece_" in f.name],
        "places":    [f for f in md if "_place_" in f.name],
        "personas":  [f for f in md if f.name.startswith("persona_") or "_persona_" in f.name],
    }


def _v2_files(country_dir: Path) -> dict[str, list[Path]]:
    """v2 file buckets, used by the strict v2 checks.

    Detection is by filename token: ``culture_<adj>_<kind>_<slug>.md``.
    Slug match is by ``_<kind>_`` infix (or trailing ``_position.md`` for
    the slug-less position file).
    """
    md = list(country_dir.glob("culture_*.md"))
    return {
        "language": [f for f in md if "_language_" in f.name],
        "history":  [f for f in md if "_history_" in f.name],
        "position": [f for f in md if "_position.md" in f.name],
        "process":  [f for f in md if "_process_" in f.name],
        "piece":    [f for f in md if "_piece_" in f.name],
        "place":    [f for f in md if "_place_" in f.name],
        "male":     [f for f in md if "_male_" in f.name],
        "female":   [f for f in md if "_female_" in f.name],
    }


def _gender(persona: Path) -> tuple[bool, bool]:
    """Legacy gender detection via Projection link to engine position file."""
    text = persona.read_text(encoding="utf-8", errors="replace")
    m = _PROJECTION_RE.search(text)
    if not m:
        return False, False
    proj = m.group(1)
    return bool(_MALE_RE.search(proj)), bool(_FEMALE_RE.search(proj))


def _khai_declaration(path: Path) -> str | None:
    """Return the declared khai type (one of _VALID_KHAI_TYPES) or None.

    None means either the marker is missing or the declared value isn't one
    of the 5 valid KAI structural types -- both are v2 schema failures.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    m = _KHAI_DECLARATION_RE.search(text)
    if m is None:
        return None
    value = m.group(1).lower()
    return value if value in _VALID_KHAI_TYPES else None


# ---------------------------------------------------------------------------
# Universal checks (run on every country regardless of mode)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_exactly_one_position(country_dir: Path):
    """v1 and v2 both require exactly one position file per country."""
    n = len(_files(country_dir)["positions"])
    assert n == 1, f"{country_dir.name}: expected 1 position file, found {n}"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_at_least_one_place(country_dir: Path):
    """v1 and v2 both require at least one place file."""
    assert _files(country_dir)["places"], f"{country_dir.name}: no place file"


# ---------------------------------------------------------------------------
# Legacy v1 checks (skipped on v2-listed countries)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_legacy_at_least_one_piece(country_dir: Path):
    """Legacy: at least one piece file (which in v1 carried double duty as
    history). v2 splits this into separate piece and history checks."""
    if _is_v2(country_dir):
        pytest.skip("country is on v2 list; piece checked via v2-strict tests")
    assert _files(country_dir)["pieces"], f"{country_dir.name}: no piece file"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_legacy_at_least_two_personas(country_dir: Path):
    if _is_v2(country_dir):
        pytest.skip("country is on v2 list; persona count enforced via male+female filenames")
    n = len(_files(country_dir)["personas"])
    assert n >= 2, f"{country_dir.name}: need >=2 personas, found {n}"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_legacy_male_persona_present(country_dir: Path):
    if _is_v2(country_dir):
        pytest.skip("country is on v2 list; male persona enforced via filename")
    personas = _files(country_dir)["personas"]
    if not personas:
        pytest.skip("no personas")
    assert any(_gender(p)[0] for p in personas), (
        f"{country_dir.name}: no persona links position_male.md in ## Projection"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_legacy_female_persona_present(country_dir: Path):
    if _is_v2(country_dir):
        pytest.skip("country is on v2 list; female persona enforced via filename")
    personas = _files(country_dir)["personas"]
    if not personas:
        pytest.skip("no personas")
    assert any(_gender(p)[1] for p in personas), (
        f"{country_dir.name}: no persona links position_female.md in ## Projection"
    )


# ---------------------------------------------------------------------------
# v2-strict checks (skipped on countries not on the v2 list)
# ---------------------------------------------------------------------------

def _v2_require_kind(country_dir: Path, kind: str) -> None:
    """Helper: assert at least one file of the given v2 kind exists."""
    if not _is_v2(country_dir):
        pytest.skip("country is not on v2 list; v2-strict checks skipped")
    files = _v2_files(country_dir)[kind]
    assert files, (
        f"{country_dir.name}: v2 schema requires at least one '{kind}' file "
        f"(filename pattern: culture_<adj>_{kind}_*.md)"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_v2_language(country_dir: Path):
    _v2_require_kind(country_dir, "language")


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_v2_history(country_dir: Path):
    _v2_require_kind(country_dir, "history")


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_v2_process(country_dir: Path):
    _v2_require_kind(country_dir, "process")


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_v2_piece(country_dir: Path):
    _v2_require_kind(country_dir, "piece")


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_v2_male(country_dir: Path):
    _v2_require_kind(country_dir, "male")


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_v2_female(country_dir: Path):
    _v2_require_kind(country_dir, "female")


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_v2_khai_declarations(country_dir: Path):
    """Every culture_*.md file in a v2-listed country must carry a valid
    `*khai: <type>*` footer marker. The KAIHACKS khai-tests v0.1.6
    declaration-driven detection reads this marker to apply the right
    structural check; a missing or invalid declaration is a hard fail."""
    if not _is_v2(country_dir):
        pytest.skip("country is not on v2 list; declarations not enforced")
    md = list(country_dir.glob("culture_*.md"))
    if not md:
        pytest.skip("no culture_*.md content")
    missing = sorted(f.name for f in md if _khai_declaration(f) is None)
    assert not missing, (
        f"{country_dir.name}: v2 schema requires every culture_*.md to carry "
        f"a `*khai: <type>*` footer matching one of "
        f"{sorted(_VALID_KHAI_TYPES)}. "
        f"Files without a valid declaration: {missing}"
    )
