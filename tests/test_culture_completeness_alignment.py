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

When the cross-check fires
-------------------------
The alignment check fires on **pull_request events whose base is
``culture/release``**. That's the integration branch where culture
content and registry must both live in sync. Main lags by design --
``data/countries.json`` records a culture the moment it lands in
culture/release (release-gating-action's chore PR), but the culture
itself only reaches main via the next ``culture/release -> main``
promotion. So main is *chronically* "registry ahead, regions/ behind"
in the window between the chore PR landing and the next promotion.

In-cycle skip
-------------
Even on culture/release-base PRs, three PR types are *inherently*
mid-cycle and would always fail the cross-check by design:

- ``chore/release-gating-*`` -- workflow-opened registry PR.
- ``sync/*`` -- main->culture/release pull-through.
- ``culture/<slug>`` -- introduces a fresh culture whose chore PR
  fires only after merge.

The cross-check fires on every other PR type into culture/release and
catches the steady-state Mexico-gap drift. On main-base PRs the
release-gating-gate workflow (``release-gating-gate.yml``) is the
load-bearing pre-promotion check; this cross-check would only
duplicate it imperfectly.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))

from culture_completeness import complete_countries  # noqa: E402

_COUNTRIES_JSON = _ROOT / "data" / "countries.json"


def _should_skip() -> tuple[bool, str]:
    """True when the cross-check is not load-bearing for this run.

    Reads ``GITHUB_HEAD_REF`` and ``GITHUB_BASE_REF`` -- set by GitHub
    Actions on pull_request events; absent on push / local runs.

    Skip conditions (any one suffices):
    - PR base is not ``culture/release`` (main-base PRs: registry is
      chronically ahead of regions/; release-gating-gate handles the
      real check).
    - PR head is ``chore/release-gating-*``, ``sync/*``, or
      ``culture/<slug>`` (the three in-cycle PR types).
    - No PR context (push / local): treat as a free pass; the next PR
      will re-check.
    """
    head = os.environ.get("GITHUB_HEAD_REF", "")
    base = os.environ.get("GITHUB_BASE_REF", "")
    if not head and not base:
        return True, "no PR context (push / local): cross-check is a PR-time gate"
    if base != "culture/release":
        return True, f"base={base!r} is not culture/release: cross-check is for the integration branch"
    if head.startswith("chore/release-gating-"):
        return True, "chore/release-gating-* PR: registry entry being filed mid-cycle"
    if head.startswith("sync/"):
        return True, "sync/* PR: main->culture/release pull-through is mid-cycle by design"
    if head.startswith("culture/"):
        return True, "culture/<slug> PR: fresh-build culture's registry chore PR fires after merge"
    return False, ""


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

    Skipped on chore/release-gating-* PRs: the registry entry being added
    points at a culture whose folder is on culture/release, not on main yet.
    """
    skip, reason = _should_skip()
    if skip:
        pytest.skip(reason)
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

    Skipped on sync/* PRs: the culture on culture/release that the sync's
    diff exposes isn't in the registry on main yet -- the chore PR carrying
    its registration is pending in parallel.
    """
    skip, reason = _should_skip()
    if skip:
        pytest.skip(reason)
    registered = _registry_slugs()
    complete = _complete_slugs()
    missing = sorted(complete - registered)
    assert not missing, (
        "Folder passes is_complete_culture() but not in data/countries.json:\n"
        + "\n".join(f"  {s}" for s in missing)
        + "\n\nAdd a registry entry (release-gating.yml normally does this "
        "automatically on culture/release push)."
    )
