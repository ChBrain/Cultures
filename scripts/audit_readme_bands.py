#!/usr/bin/env python3
"""Audit Hofstede band labels in country README scores tables.

For every `regions/<region>/<country>/README.md`, locate Hofstede score table
rows and compare the declared Level cell against the band computed from the
score. Reports mismatches that L4e (`validate_hofstede_alignment.py`) will
reject once the band+mismatch contract is enforced.

Band contract (Level column, machine-validated):
  0-39   -> Low
  40-59  -> Moderate
  60-100 -> High

Output is one TSV row per dimension found, with a `needs_change` flag:

  country | dimension | score | declared_level | computed_band | needs_change

`needs_change` is `yes` when `declared_level.title() != computed_band`.

Exit status:
  0 if no mismatches.
  1 if any mismatch found.

Usage:
  scripts/audit_readme_bands.py             # all countries, report all rows
  scripts/audit_readme_bands.py --mismatch  # only print rows that need change
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HOFSTEDE_DIMENSIONS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]

REGIONS = ("africa", "americas", "asia", "europe", "oceania")

ROW_PATTERN = re.compile(
    r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|"
    r"\s*(\d+)\s*\|"
    r"\s*\*\*([A-Za-z][A-Za-z \-]*?)\*\*[^|\n]*\|",
    re.IGNORECASE,
)


def score_to_band(score: int) -> str:
    if score <= 39:
        return "Low"
    if score <= 59:
        return "Moderate"
    return "High"


def find_country_readmes() -> list[Path]:
    regions_dir = ROOT / "regions"
    if not regions_dir.is_dir():
        return []
    readmes: list[Path] = []
    for region in sorted(regions_dir.iterdir()):
        if not region.is_dir() or region.name.startswith("."):
            continue
        for country in sorted(region.iterdir()):
            if not country.is_dir() or country.name.startswith("."):
                continue
            readme = country / "README.md"
            if readme.exists():
                readmes.append(readme)
    return readmes


def audit_readme(readme: Path) -> list[tuple[str, str, int, str, str, bool]]:
    """Return (country, dim, score, declared_level, computed_band, needs_change) per row."""
    text = readme.read_text(encoding="utf-8")
    country = readme.parent.name
    rows: list[tuple[str, str, int, str, str, bool]] = []
    seen: set[tuple[str, int]] = set()
    for match in ROW_PATTERN.finditer(text):
        dim = match.group(1).upper()
        score = int(match.group(2))
        declared_raw = match.group(3).strip()
        declared = declared_raw.split()[0].title() if declared_raw else ""
        key = (dim, score)
        if key in seen:
            continue
        seen.add(key)
        band = score_to_band(score)
        needs_change = declared != band
        rows.append((country, dim, score, declared, band, needs_change))
    return rows


def main(argv: list[str]) -> int:
    only_mismatch = "--mismatch" in argv[1:]
    readmes = find_country_readmes()
    if not readmes:
        print("No country READMEs found.", file=sys.stderr)
        return 0

    print("country\tdimension\tscore\tdeclared_level\tcomputed_band\tneeds_change")
    total = 0
    mismatches = 0
    for readme in readmes:
        for country, dim, score, declared, band, needs_change in audit_readme(readme):
            total += 1
            if needs_change:
                mismatches += 1
            if only_mismatch and not needs_change:
                continue
            print(
                f"{country}\t{dim}\t{score}\t{declared}\t{band}\t"
                f"{'yes' if needs_change else 'no'}"
            )

    print(
        f"\nAudited {len(readmes)} README(s), {total} dimension row(s); "
        f"{mismatches} mismatch(es).",
        file=sys.stderr,
    )
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
