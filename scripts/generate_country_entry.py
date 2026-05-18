#!/usr/bin/env python3
"""Generate data/countries.json skeleton entries for new cultures.

Part of the Release Gating Engine (issue #257). When a culture enters
`culture/release`, the release-gating action calls this so the registry
gating data is in place before the promotion to `main`.

Derivable fields are filled from the repo; curated fields are written as
`TODO` so the gating check (`scripts/check_release_gating.py`) fails until
a human completes them -- that completion is the release audit.

  derived:  id, region, name (title-cased), language (from hofstede_bag.yaml),
            asset (cultures-<region>-<id>.zip)
  TODO:     anchor.iso (ISO 3166-1 alpha-2, or switch anchor to a marker),
            name_source

Idempotent: a slug already registered is left untouched.

Usage:
    python scripts/generate_country_entry.py <slug> [<slug> ...]

Exit 0 = registry written or already complete.
Exit 1 = a slug has no regions/<region>/<slug>/ folder.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COUNTRIES = REPO_ROOT / "data" / "countries.json"
REGIONS = REPO_ROOT / "regions"

TODO = "TODO"


def _find_region(slug: str) -> str | None:
    """The regions/ parent folder of `slug`, or None if no folder exists."""
    for d in sorted(REGIONS.glob(f"*/{slug}")):
        if d.is_dir():
            return d.parent.name
    return None


def _language(region: str, slug: str) -> str:
    """The country's language from its hofstede_bag.yaml, else TODO."""
    bag = REGIONS / region / slug / "hofstede_bag.yaml"
    if bag.is_file():
        data = yaml.safe_load(bag.read_text(encoding="utf-8")) or {}
        lang = data.get("language")
        if isinstance(lang, str) and lang.strip():
            return lang
    return TODO


def skeleton_entry(slug: str) -> dict:
    """Build a skeleton registry entry for `slug`.

    Raises ValueError if no regions/<region>/<slug>/ folder exists.
    """
    region = _find_region(slug)
    if region is None:
        raise ValueError(f"no regions/<region>/{slug}/ folder for '{slug}'")
    return {
        "id": slug,
        "name": slug.replace("_", " ").title(),
        "region": region,
        "asset": f"cultures-{region}-{slug}.zip",
        "anchor": {"type": "region", "iso": TODO},
        "language": _language(region, slug),
        "name_source": TODO,
    }


def _dump_registry(data: dict) -> str:
    """Serialize the registry, keeping each anchor object on one line to
    match the established countries.json style."""
    text = json.dumps(data, indent=2, ensure_ascii=False)
    text = re.sub(
        r'\{\n\s*"type": ("[^"]+"),\n\s*"iso": ("[^"]+")\n\s*\}',
        r'{ "type": \1, "iso": \2 }',
        text,
    )
    return text + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="generate_country_entry.py",
        description="Add skeleton registry entries to data/countries.json.",
    )
    parser.add_argument("slugs", nargs="+", help="country ids to register")
    args = parser.parse_args(argv[1:])

    data = json.loads(COUNTRIES.read_text(encoding="utf-8"))
    entries = data.setdefault("countries", [])
    registered = {c.get("id") for c in entries}

    added: list[str] = []
    for slug in args.slugs:
        if slug in registered:
            print(f"{slug}: already registered -- left untouched.")
            continue
        try:
            entries.append(skeleton_entry(slug))
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        added.append(slug)

    if not added:
        print("countries.json: no new entries.")
        return 0

    COUNTRIES.write_text(_dump_registry(data), encoding="utf-8")
    print(f"countries.json: added skeleton entr{'y' if len(added) == 1 else 'ies'} "
          f"for {', '.join(added)} -- complete the TODO fields (anchor.iso, name_source).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
