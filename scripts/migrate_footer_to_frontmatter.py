#!/usr/bin/env python3
"""Convert a culture markdown file's trailing footer to YAML frontmatter.

One-shot, idempotent, reusable. Phase 2 of the metadata migration runs it
over the v2-migrated countries; later it runs per-country as each country
migrates. ``read_metadata`` parses the legacy footer, ``strip_metadata``
removes it, and the metadata is re-emitted as a leading ``---`` block in
the locked schema key order.

A file already in frontmatter -- or carrying no metadata at all -- is left
untouched, so re-running over a half-migrated tree is safe.

Usage:
  migrate_footer_to_frontmatter.py PATH [PATH ...]    convert in place
  migrate_footer_to_frontmatter.py --check PATH ...   report only; exit 1
                                                      if any file would change
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tests"))

import yaml  # noqa: E402
from culture_metadata import format_of, read_metadata, strip_metadata  # noqa: E402

# Frontmatter key order -- the locked schema. Keys absent from a file's
# metadata are simply skipped (e.g. `type` is not on every file, `sources`
# is hand-authored later).
_SCHEMA_ORDER = ("khai", "type", "hofstede", "license", "sources", "stamp")


def _normalise(meta: dict) -> dict:
    """Re-key parsed footer metadata into the locked frontmatter schema.

    The footer's free-text hofstede pointer ("aggregate in README.md") is
    collapsed to the controlled token ``aggregate`` so scripts can branch
    on the value instead of parsing prose.
    """
    out: dict = {}
    for key in _SCHEMA_ORDER:
        if key not in meta:
            continue
        value = meta[key]
        if key == "hofstede" and isinstance(value, str) and "aggregate" in value.lower():
            value = "aggregate"
        out[key] = value
    return out


def to_frontmatter(text: str) -> str | None:
    """Return ``text`` rewritten with a frontmatter block, or None.

    None means no conversion is due -- the file is already frontmatter, or
    carries no footer to migrate.
    """
    if format_of(text) != "footer":
        return None
    meta = _normalise(read_metadata(text))
    body = strip_metadata(text)
    block = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).rstrip("\n")
    return f"---\n{block}\n---\n{body}"


def main(argv: list[str]) -> int:
    args = argv[1:]
    check = "--check" in args
    paths = [Path(a) for a in args if a != "--check"]
    if not paths:
        print("Usage: migrate_footer_to_frontmatter.py [--check] PATH ...",
              file=sys.stderr)
        return 2

    changed: list[Path] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        new = to_frontmatter(text)
        if new is None or new == text:
            continue
        changed.append(path)
        if check:
            print(f"would convert: {path}")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"converted: {path}")

    verb = "would change" if check else "converted"
    print(f"{len(changed)} file(s) {verb}.")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
