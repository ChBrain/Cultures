#!/usr/bin/env python3
"""Validate that history files document a broad arc of defining moments.

Per khai-cultures-create skill v0.1.1+: a history file is the culture's
**defining moments across its full arc** -- not a single pivotal event.
A Yearbook with 8 entries narrowly clustered on one event is a piece
file (File 5), not a history file (File 2).

This script enforces the methodology:
- File matches `culture_*_history_*.md`
- File declares `*khai: piece*`
- Yearbook section is present
- Yearbook contains MIN_ENTRIES dated entries
- Date range spans MIN_CENTURY_SPAN centuries (broad arc)

Catches the class of bug where a history file ships as a single-event
essay (e.g. the original Beeldenstorm-only Netherlands history; the
original event-named Grundgesetz Germany history). Companion to the
section-parity validator (scripts/validate_sections.py).

Usage:
  scripts/validate_history_arc.py FILE...        # CLI mode
  validate(paths)                                # importable, returns list[Issue]

Exit status:
  0 if every file passes, 1 if any fail. Non-history files are skipped.
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

MIN_ENTRIES = 12
MIN_CENTURY_SPAN = 5

YEARBOOK_HEADER_RE = re.compile(r"^##\s+Yearbook\s*$", re.MULTILINE | re.IGNORECASE)

# Dated Yearbook entry. Year can be:
#   1949:
#   9 n. Chr.:                 (German AD)
#   57 v. Chr.:                (German BC)
#   9 AD:  /  9 n.Chr.:        (other AD variants)
#   57 BC: / 57 v.Chr.:        (other BC variants)
#   1940-1945:                 (range; uses first year)
#   1795-1813:
# Captures the first year. Era marker optional.
DATE_LINE_RE = re.compile(
    r"^"
    r"(?P<year>\d{1,4})"
    r"(?:\s*(?P<era>v\.?\s*Chr\.?|n\.?\s*Chr\.?|BC|AD))?"
    r"(?:-(?P<end_year>\d{1,4}))?"
    r"\s*:",
    re.MULTILINE | re.IGNORECASE,
)


def _is_history_file(path: Path) -> bool:
    """True if the filename matches the culture history convention."""
    name = path.name
    return (
        name.startswith("culture_")
        and "_history_" in name
        and name.endswith(".md")
    )


def _normalise_year(year_str: str, era: str | None) -> int:
    """Convert (year_str, era) to a signed year integer.

    BC / v. Chr. -> negative. AD / n. Chr. / no marker -> positive.
    """
    n = int(year_str)
    if era:
        era_low = era.lower().replace(" ", "")
        if "v." in era_low or "vc" in era_low or era_low == "bc":
            return -n
    return n


def _parse_yearbook(text: str) -> list[int]:
    """Return list of first-years of dated entries in the Yearbook section.

    Returns empty list if no Yearbook header is found.
    """
    header_match = YEARBOOK_HEADER_RE.search(text)
    if not header_match:
        return []

    rest = text[header_match.end():]
    # Yearbook ends at the next `## ` header or at the metadata footer rule.
    next_header = re.search(r"^##\s", rest, re.MULTILINE)
    next_footer = re.search(r"^---\s*$", rest, re.MULTILINE)
    cutoffs = [m.start() for m in (next_header, next_footer) if m]
    end = min(cutoffs) if cutoffs else len(rest)

    section = rest[:end]
    years: list[int] = []
    for m in DATE_LINE_RE.finditer(section):
        years.append(_normalise_year(m.group("year"), m.group("era")))
    return years


def validate_file(path: Path) -> list[Issue]:
    """Return Issue records for one history file. Non-history files return [].

    Three checks:
      1. *khai: piece* declaration present (history files share piece structure)
      2. Yearbook has >= MIN_ENTRIES dated entries
      3. Yearbook date range spans >= MIN_CENTURY_SPAN centuries (broad arc)
    """
    if not _is_history_file(path):
        return []
    if not path.exists():
        return [Issue(error=f"{path}: file not found")]

    text = path.read_text(encoding="utf-8", errors="replace")
    issues: list[Issue] = []

    # Check 1: khai declaration
    khai = read_metadata(text).get("khai")
    if not khai:
        issues.append(Issue(
            error=f"{path.name}: missing khai declaration (expected khai: piece)"
        ))
    elif khai != "piece":
        issues.append(Issue(
            error=(
                f"{path.name}: declared khai: {khai} but history "
                f"files must declare khai: piece (share piece structure)"
            )
        ))

    # Check 2 + 3: Yearbook entries and span
    years = _parse_yearbook(text)
    if len(years) < MIN_ENTRIES:
        issues.append(Issue(
            error=(
                f"{path.name}: Yearbook has {len(years)} dated entries; "
                f"history files must have at least {MIN_ENTRIES} "
                f"(defining-moments arc, not single event). "
                f"See khai-cultures-create skill v0.1.1+ File 2."
            )
        ))
    elif years:
        span = max(years) - min(years)
        # Centuries: ceil(span / 100). A span of 100 covers 2 centuries
        # if the years straddle a century boundary; conservatively count
        # the maximum centuries any pair could touch.
        centuries = (span // 100) + 1
        if centuries < MIN_CENTURY_SPAN:
            issues.append(Issue(
                error=(
                    f"{path.name}: Yearbook spans {span} years "
                    f"({centuries} centuries), but history files must span "
                    f"at least {MIN_CENTURY_SPAN} centuries (broad arc, "
                    f"not narrow event). "
                    f"Earliest entry: {min(years)}; latest: {max(years)}."
                )
            ))

    return issues


def validate(paths: list[Path] | None = None) -> list[Issue]:
    """Orchestrator-compatible entry point. Mirrors validate_culture's signature."""
    if paths is None:
        paths = sorted((ROOT / "regions").rglob("culture_*_history_*.md"))

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
