#!/usr/bin/env python3
"""Validate that culture content files have the sections their khai declaration promises.

Reads the `*khai: <type>*` footer marker, looks up the canonical sections
for that type, and asserts all four are present as `## <section>` headers.

Catches the class of bug where a history file (declared `*khai: piece*`) is
written as a narrative essay with sections like "The Event" or "The
Discovery" instead of the canonical Piece structure (Place / Load Bearing /
Apparent / Yearbook). CI's khai_tests pytest jobs catch this too, but only
in CI -- this script closes the local-hook gap exposed by PR #105.

Usage:
  scripts/validate_sections.py FILE...           # CLI mode
  validate(paths)                                # importable, returns list[Issue]

Exit status:
  0 if every file passes, 1 if any fail.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tests"))

from culture_metadata import read_metadata  # noqa: E402
from findings import Issue  # noqa: E402

# khai structural type -> required `## Section` headers, in canonical order.
# Mirrors the contract in khai-cultures-create SKILL.md and the khai_tests
# pytest components (test_khai_process, test_khai_position, test_khai_piece,
# test_khai_place, test_khai_persona).
SECTIONS: dict[str, list[str]] = {
    "process":  ["## Initiated by", "## Direction", "## Lever", "## Echo"],
    "position": ["## Has", "## Orders", "## Loses", "## Drives"],
    "piece":    ["## Place", "## Load Bearing", "## Apparent", "## Yearbook"],
    "place":    ["## Shown", "## Holds", "## Offers", "## Withheld"],
    "persona":  ["## Projection", "## Action", "## Shadow", "## Tell"],
}

def validate_file(path: Path) -> list[Issue]:
    """Return list of Issue records for `path`. Empty list = OK."""
    if not path.exists():
        return [Issue(error=f"{path}: file not found")]

    text = path.read_text(encoding="utf-8", errors="replace")

    khai_type = read_metadata(text).get("khai")
    if not khai_type:
        # No declaration -> not our concern. The khai-declaration-present
        # check lives elsewhere (Lens 1 in khai-cultures-review); this
        # script only enforces sections when a declaration exists.
        return []

    if khai_type not in SECTIONS:
        return [Issue(
            error=(
                f"{path}: invalid khai declaration `{khai_type}` "
                f"(expected one of {sorted(SECTIONS)})"
            )
        )]

    missing = [s for s in SECTIONS[khai_type] if s not in text]
    if missing:
        return [Issue(
            error=(
                f"{path}: declared *khai: {khai_type}* but missing sections: "
                f"{missing}"
            )
        )]

    return []


def validate(paths: list[Path] | None = None) -> list[Issue]:
    """Orchestrator-compatible entry point. Mirrors validate_culture's signature."""
    if paths is None:
        paths = sorted((ROOT / "regions").rglob("*.md"))

    issues: list[Issue] = []
    for p in paths:
        issues.extend(validate_file(Path(p)))
    return issues


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"Usage: {argv[0]} FILE...", file=sys.stderr)
        return 2

    paths = []
    for arg in argv[1:]:
        path = Path(arg)
        if not path.is_absolute():
            path = ROOT / path
        paths.append(path)

    failed = False
    for issue in validate(paths):
        print(issue.error)
        failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
