"""Cross-check: data/countries.json (the website-map registry) and the
complete-cultures set (zips + PDFs) stay in lockstep.

The release-gating workflow opens a chore PR adding a country's registry
entry the moment its content lands in culture/release, so under normal
flow the two sets agree. This test catches drift -- a country added to
the registry whose folder doesn't yet pass the completeness bar, or a
country promoted to culture/release that nobody registered.

The historical case is the Mexico gap that motivated issue #257: content
shipped but no registry entry, so available.json (the website map's data
source) didn't know about it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))

from culture_completeness import complete_countries  # noqa: E402

_COUNTRIES_JSON = _ROOT / "data" / "countries.json"


def _registry_slugs() -> set[str]:
    """Country slugs in data/countries.json, normalised to underscores
    (the registry uses '-', the regions/ folders use '_')."""
    if not _COUNTRIES_JSON.is_file():
        return set()
    entries = json.loads(_COUNTRIES_JSON.read_text(encoding="utf-8")).get("countries", [])
    return {c["id"].replace("-", "_") for c in entries if "id" in c}


def _complete_slugs() -> set[str]:
    return {country.name for _region, country in complete_countries()}


def test_every_registered_country_is_complete():
    """Every entry in data/countries.json must satisfy is_complete_culture().

    A registered country whose folder isn't yet complete means available.json
    will advertise a download that doesn't exist -- the website map shows a
    culture with no zip behind it.
    """
    registered = _registry_slugs()
    complete = _complete_slugs()
    not_complete = sorted(registered - complete)
    assert not not_complete, (
        "Registered in data/countries.json but folder fails is_complete_culture():\n"
        + "\n".join(f"  {s}" for s in not_complete)
        + "\n\nEither finish the culture's content (position + 2 personas + place + "
        "piece + README) or remove the registry entry."
    )


def test_every_complete_country_is_registered():
    """Every culture passing is_complete_culture() must be in data/countries.json.

    A complete country that isn't registered ships in zips/PDFs but the website
    map doesn't know about it -- the Mexico gap (#257) in its original form.
    The release-gating workflow normally catches this by opening a chore PR
    on culture/release push; the test guards the steady state.
    """
    registered = _registry_slugs()
    complete = _complete_slugs()
    missing = sorted(complete - registered)
    assert not missing, (
        "Folder passes is_complete_culture() but not in data/countries.json:\n"
        + "\n".join(f"  {s}" for s in missing)
        + "\n\nAdd a registry entry (release-gating.yml normally does this "
        "automatically on culture/release push)."
    )
