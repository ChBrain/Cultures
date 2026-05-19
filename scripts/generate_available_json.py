#!/usr/bin/env python3
"""Generate the Cultures download manifest (available.json).

Producer side of the Cultures <-> KAIHACKS download contract. Regenerates
the manifest wholesale from data/countries.json -- the single source of
truth -- projecting each registered culture to the contract shape
(kaihacks.ai/cultures/public_html/assets/data/available.schema.json).

available.json is never hand-extended: a country added to countries.json
is picked up by the next regeneration; a changed country is reflected;
regeneration is idempotent.

The release-delivery workflow runs this and opens an idempotent PR against
ChBrain/KAIHACKS.

Usage:
    python scripts/generate_available_json.py --release <tag> [--out PATH]

Without --out, the manifest is printed to stdout.

Exit 0 = manifest generated; 1 = a producer-side invariant is violated.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COUNTRIES = REPO_ROOT / "data" / "countries.json"

SCHEMA_VERSION = 1
DOWNLOAD_BASE = "https://github.com/ChBrain/Cultures/releases/latest/download/"
REGIONS = {"africa", "americas", "asia", "europe", "oceania"}

# culture.id must match the contract pattern; the registry uses '_' in
# multi-word slugs, the manifest uses '-'.
_ID_RE = re.compile(r"^[a-z0-9-]+$")


def _culture_entry(c: dict) -> dict:
    """Project a countries.json entry onto a contract `culture` object."""
    return {
        "id": c["id"].replace("_", "-"),
        "name": c["name"],
        "region": c["region"],
        "asset": c["asset"],
        "anchor": c["anchor"],
        "parent": c.get("parent"),
    }


def build_manifest(release: str) -> dict:
    """Build the full manifest dict from data/countries.json."""
    registry = json.loads(COUNTRIES.read_text(encoding="utf-8"))
    cultures = [_culture_entry(c) for c in registry.get("countries", [])]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "release": release,
        "downloadBase": DOWNLOAD_BASE,
        "cultures": cultures,
    }


def check_manifest(manifest: dict) -> list[str]:
    """Producer-side invariants. Returns a list of problems; empty = OK."""
    problems: list[str] = []
    ids = [c["id"] for c in manifest["cultures"]]
    for cid in ids:
        if not _ID_RE.match(cid):
            problems.append(f"culture id {cid!r} violates ^[a-z0-9-]+$")
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        problems.append(f"duplicate culture id(s): {dupes}")
    for c in manifest["cultures"]:
        if c["region"] not in REGIONS:
            problems.append(f"{c['id']}: region {c['region']!r} not in {sorted(REGIONS)}")
        anchor = c.get("anchor")
        if not isinstance(anchor, dict) or anchor.get("type") not in ("region", "marker"):
            problems.append(f"{c['id']}: invalid anchor {anchor!r}")
        elif anchor["type"] == "region":
            iso = anchor.get("iso")
            if not (isinstance(iso, str) and re.fullmatch(r"[A-Z]{2}", iso)):
                problems.append(f"{c['id']}: region anchor iso {iso!r} is not [A-Z]{{2}}")
    return problems


def dumps(manifest: dict) -> str:
    """Serialize in the contract file's style: 2-space indent, each region
    anchor object kept on one line."""
    text = json.dumps(manifest, indent=2, ensure_ascii=False)
    text = re.sub(
        r'\{\n\s*"type": ("[^"]+"),\n\s*"iso": ("[^"]+")\n\s*\}',
        r'{ "type": \1, "iso": \2 }',
        text,
    )
    return text + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="generate_available_json.py")
    parser.add_argument("--release", required=True,
                        help="Cultures release tag this manifest is generated from")
    parser.add_argument("--out", help="output path; stdout if omitted")
    args = parser.parse_args(argv[1:])

    manifest = build_manifest(args.release)
    problems = check_manifest(manifest)
    if problems:
        for p in problems:
            sys.stderr.write(f"ERROR: {p}\n")
        return 1

    out = dumps(manifest)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"wrote {len(manifest['cultures'])} cultures to {args.out}")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
