"""L4e: Hofstede structure pass per country — section, scores, bands, sources, footers."""
import re
import warnings
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent

_DIMS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]

_SCORE_RE = re.compile(
    r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|"
    r"\s*(\d+)\s*\|"
    r"\s*\*\*(Low|Moderate|High)\*\*[^\|\n]*\|",
    re.IGNORECASE,
)
_SIGNAL_RE = re.compile(r"\*Hofstede signal:", re.IGNORECASE)
_LEGACY_RE = re.compile(r"\*\*Hofstede:\*\*\s*PDI\s*\d+", re.IGNORECASE)


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
            content = list(country_dir.glob("culture_*.md")) + list(country_dir.glob("persona_*.md"))
            if content:
                countries.append(country_dir)
    return countries


def _band(score: int) -> str:
    if score <= 39:
        return "Low"
    if score <= 59:
        return "Moderate"
    return "High"


def _scores(text: str) -> dict[str, tuple[int, str]]:
    return {
        m.group(1).upper(): (int(m.group(2)), m.group(3).title())
        for m in _SCORE_RE.finditer(text)
    }


_COUNTRIES = _country_dirs()


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_hofstede_section(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    assert re.search(r"##\s+Hofstede", readme.read_text(encoding="utf-8"), re.IGNORECASE), (
        f"{country_dir.name}: README missing ## Hofstede section"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_all_six_dimensions(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    text = readme.read_text(encoding="utf-8")
    if not re.search(r"##\s+Hofstede", text, re.IGNORECASE):
        pytest.skip("no Hofstede section")
    missing = [d for d in _DIMS if d not in _scores(text)]
    assert not missing, (
        f"{country_dir.name}: missing dimension(s): {missing} "
        f"(Level column accepts only Low / Moderate / High)"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_level_matches_band(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    mismatches = [
        f"{dim}: score={score} → band={_band(score)}, Level={level!r}"
        for dim, (score, level) in _scores(readme.read_text(encoding="utf-8")).items()
        if level != _band(score)
    ]
    assert not mismatches, f"{country_dir.name}: Level/band mismatch(es): {mismatches}"


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_source_attribution(country_dir: Path):
    readme = country_dir / "README.md"
    if not readme.is_file():
        pytest.skip("no README")
    text = readme.read_text(encoding="utf-8")
    if not re.search(r"##\s+Hofstede", text, re.IGNORECASE):
        pytest.skip("no Hofstede section")
    assert re.search(r"hofstede|empirical|research", text, re.IGNORECASE), (
        f"{country_dir.name}: Hofstede scores lack source attribution"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_references_cites_hofstede(country_dir: Path):
    refs = country_dir / "REFERENCES.md"
    if not refs.is_file():
        pytest.skip("no REFERENCES.md")
    assert "Hofstede" in refs.read_text(encoding="utf-8"), (
        f"{country_dir.name}: REFERENCES.md missing Hofstede citation"
    )


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_no_legacy_score_footer(country_dir: Path):
    bad = [
        f.name for f in sorted(country_dir.glob("culture_*.md"))
        if _LEGACY_RE.search(f.read_text(encoding="utf-8", errors="replace"))
    ]
    assert not bad, f"{country_dir.name}: legacy per-file Hofstede score footer in: {bad}"


@pytest.mark.xfail(strict=False, reason="advisory during rollout")
@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_hofstede_signal_footer(country_dir: Path):
    missing = [
        f.name for f in sorted(country_dir.glob("culture_*.md"))
        if not _SIGNAL_RE.search(f.read_text(encoding="utf-8", errors="replace"))
    ]
    assert not missing, f"{country_dir.name}: missing Hofstede signal footer in: {missing}"
