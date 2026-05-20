"""The completeness rule -- which cultures are "ready to ship".

One filter, multiple consumers. Anything that asks "is this culture
deployable?" reads from here:

  scripts/build_zips.py   -- which countries get a zip
  scripts/build_pdfs.py   -- which countries get a PDF
  tests/test_culture_completeness_alignment.py -- cross-check that
      data/countries.json (the website map's registry) and the
      complete-cultures set stay in lockstep

The rule itself: a country folder is *complete* when it carries a
position file, at least two personas (accepting all naming forms across
the persona-rename rollout), a place file, a piece file, and a README.
That is exactly what the deployment artifacts need to resolve.

Untested skeleton countries -- a region folder with a stub README but no
content -- fall out. As each one finishes its v0.2.0 fix pass, it
crosses the bar and joins the shipped set automatically.
"""
from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_REGIONS = _ROOT / "regions"


def is_complete_culture(country: Path) -> bool:
    """A country folder ready to ship: position + 2 personas + place + piece + README.

    Persona detection accepts every naming form that ships during the
    rename rollout (#302): the legacy ``persona_<name>.md``, the v2
    ``culture_<adj>_persona_<gender>_<name>.md``, and the post-rename
    ``<adj>_persona_<gender>_<name>.md``. The shipped artifact downstream
    handles the union; the completeness rule does too.
    """
    if not country.is_dir():
        return False
    personas = [
        p for p in country.glob("*.md")
        if "_persona_" in p.name or p.name.startswith("persona_")
    ]
    return (
        any(country.glob("culture_*_position.md"))
        and len(personas) >= 2
        and any(country.glob("culture_*_place_*.md"))
        and any(country.glob("culture_*_piece_*.md"))
        and (country / "README.md").is_file()
    )


def complete_countries() -> list[tuple[str, Path]]:
    """(region_name, country_dir) for every complete culture, sorted.

    Ordered: regions alphabetically, countries within each region
    alphabetically. Hidden folders (``.xyz``) skipped.
    """
    out: list[tuple[str, Path]] = []
    if not _REGIONS.is_dir():
        return out
    for region in sorted(p for p in _REGIONS.iterdir() if p.is_dir() and not p.name.startswith(".")):
        for country in sorted(p for p in region.iterdir() if p.is_dir() and not p.name.startswith(".")):
            if is_complete_culture(country):
                out.append((region.name, country))
    return out
