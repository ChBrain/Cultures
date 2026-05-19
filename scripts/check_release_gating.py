#!/usr/bin/env python3
"""Release gating check -- country registry completeness.

Before a culture is promoted `culture/release -> main`, the release gating
data on `main` must be complete for it. This check covers the country
registry: every country in the release set must have a complete, valid
entry in `data/countries.json`.

It catches the drift class where a culture is developed and promoted but
never registered -- see issue #257 (the Mexico gap). It is the logic the
release-gating blocking gate runs; the workflow that invokes it on the
`culture/release -> main` promotion is a separate, later piece.

Every failure prints as a work order -- rule, entity, problem, fix, lane --
so it can be acted on without guessing (the audit-message contract).

Usage:
    python scripts/check_release_gating.py <country-id> [<country-id> ...]
    python scripts/check_release_gating.py --all

Exit 0 = gating data complete for every checked country.
Exit 1 = one or more gaps.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COUNTRIES = REPO_ROOT / "data" / "countries.json"

REGIONS = {"africa", "americas", "asia", "europe", "oceania"}
# Top-level fields every registry entry must carry with a real value.
REQUIRED_FIELDS = ("id", "name", "region", "asset", "anchor", "language", "name_source")
PLACEHOLDERS = {"", "TODO", "TBD", "todo", "tbd"}


def load_registry() -> dict[str, dict]:
    """data/countries.json as an id -> entry map."""
    data = json.loads(COUNTRIES.read_text(encoding="utf-8"))
    return {c["id"]: c for c in data.get("countries", []) if "id" in c}


def _work_order(rule: str, entity: str, problem: str, fix: str, lane: str) -> str:
    return (
        f"release-gating FAIL [{rule}]\n"
        f"  entity:  {entity}\n"
        f"  problem: {problem}\n"
        f"  fix:     {fix}\n"
        f"  lane:    {lane}\n"
        f"  ref:     data/countries.json -- see issue #257"
    )


def _is_placeholder(v: object) -> bool:
    return v is None or (isinstance(v, str) and v.strip() in PLACEHOLDERS)


def check_anchor(slug: str, anchor: object) -> list[str]:
    """Work orders for an entry's `anchor`; empty list = valid."""
    if not isinstance(anchor, dict) or "type" not in anchor:
        return [_work_order(
            "anchor-valid", f"countries.json entry '{slug}', field 'anchor'",
            f"not a valid anchor object (got {anchor!r})",
            'set anchor to {"type": "region", "iso": "XX"} or '
            '{"type": "marker", "coords": [lat, lng]}',
            "chore (data/countries.json)",
        )]
    kind = anchor["type"]
    if kind == "region":
        iso = anchor.get("iso")
        if not (isinstance(iso, str) and len(iso) == 2 and iso.isupper()):
            return [_work_order(
                "anchor-valid", f"countries.json entry '{slug}', anchor.iso",
                f"region anchor needs a 2-letter uppercase ISO code (got {iso!r})",
                "set anchor.iso to the ISO 3166-1 alpha-2 code",
                "chore (data/countries.json)",
            )]
    elif kind == "marker":
        coords = anchor.get("coords")
        if not (isinstance(coords, list) and len(coords) == 2
                and all(isinstance(n, (int, float)) for n in coords)):
            return [_work_order(
                "anchor-valid", f"countries.json entry '{slug}', anchor.coords",
                f"marker anchor needs coords [lat, lng] (got {coords!r})",
                "set anchor.coords to a [lat, lng] number pair",
                "chore (data/countries.json)",
            )]
    else:
        return [_work_order(
            "anchor-valid", f"countries.json entry '{slug}', anchor.type",
            f"unknown anchor type {kind!r}",
            "anchor.type must be 'region' or 'marker'",
            "chore (data/countries.json)",
        )]
    return []


def check_country(slug: str, registry: dict[str, dict]) -> list[str]:
    """Work orders for one country; empty list = gating data complete."""
    entry = registry.get(slug)
    if entry is None:
        return [_work_order(
            "registry-presence", f"country '{slug}'",
            "not in data/countries.json -- a promoted culture must be registered first",
            f"add a complete '{slug}' entry to data/countries.json",
            "chore (data/countries.json)",
        )]

    problems: list[str] = []
    for field in REQUIRED_FIELDS:
        if field == "anchor":
            continue  # structural, validated by check_anchor
        if _is_placeholder(entry.get(field)):
            problems.append(_work_order(
                "registry-completeness",
                f"countries.json entry '{slug}', field '{field}'",
                f"missing or placeholder (value={entry.get(field)!r})",
                f"set '{field}' to its real value",
                "chore (data/countries.json)",
            ))
    region = entry.get("region")
    if not _is_placeholder(region) and region not in REGIONS:
        problems.append(_work_order(
            "registry-completeness", f"countries.json entry '{slug}', field 'region'",
            f"region {region!r} is not one of {sorted(REGIONS)}",
            "set 'region' to the country's regions/ parent folder",
            "chore (data/countries.json)",
        ))
    problems.extend(check_anchor(slug, entry.get("anchor")))
    return problems


def check_registry_uniqueness() -> list[str]:
    """Registry-wide: every culture is registered exactly once.

    Reads the raw countries.json list (not load_registry's dict, which
    silently collapses duplicate ids). `id` collapses entries; `asset`
    collides downloads. `iso` is intentionally NOT checked unique --
    subdivisions will deliberately share a parent country's iso.
    """
    raw = json.loads(COUNTRIES.read_text(encoding="utf-8")).get("countries", [])
    problems: list[str] = []
    for field in ("id", "asset"):
        values = [c.get(field) for c in raw if c.get(field) is not None]
        for dup in sorted({v for v in values if values.count(v) > 1}):
            problems.append(_work_order(
                "registry-uniqueness",
                f"data/countries.json, {field}={dup!r}",
                f"{field} {dup!r} is used by more than one culture -- "
                "a culture must be registered exactly once",
                f"remove the duplicate entry, or correct its {field}",
                "chore (data/countries.json)",
            ))
    return problems


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="check_release_gating.py",
        description="Verify release gating data (country registry) is complete.",
    )
    parser.add_argument("countries", nargs="*", help="country ids to check")
    parser.add_argument("--all", action="store_true",
                        help="check every country registered in countries.json")
    args = parser.parse_args(argv[1:])

    registry = load_registry()
    if args.all:
        slugs = sorted(registry)
    elif args.countries:
        slugs = args.countries
    else:
        parser.error("provide one or more country ids, or --all")

    # Registry-wide uniqueness runs regardless of the slugs in scope --
    # a duplicate anywhere is a release-blocking problem.
    orders: list[str] = check_registry_uniqueness()
    for slug in slugs:
        orders.extend(check_country(slug, registry))

    if orders:
        for o in orders:
            sys.stderr.write(o + "\n\n")
        sys.stderr.write(
            f"release-gating: {len(orders)} gap(s) across {len(slugs)} country(ies).\n"
        )
        return 1
    print(f"release-gating: registry gating data complete for {len(slugs)} country(ies).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
