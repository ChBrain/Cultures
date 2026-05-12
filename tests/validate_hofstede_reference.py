#!/usr/bin/env python3
"""Compare declared Hofstede scores against the Hofstede Insights reference.

Scope: each culture's ``README.md`` declares Hofstede scores;
``data/hofstede_scores.json`` holds the canonical Hofstede Insights values.
This validator catches drift between the two and forces a deliberate
justification when they diverge.

Rule per dimension:
  |declared - reference| <= 5            -> PASS silently.
  |declared - reference| > 5 + justified -> INFO (advisory log).
  |declared - reference| > 5, no jus.    -> FAIL.

A dimension is "justified" when ``hofstede_decisions.md`` contains a
``## Deviation justification`` section whose body names the dimension
(``PDI``, ``IDV``, ``UAI``, ``MAS``, ``LTO``, ``IND``) — typically as a
``### LTO`` sub-heading with prose underneath, but any whole-word
mention inside the section counts.

Source-type behavior:
  - source contains "Empirical research":      empirical Hofstede Insights data
  - source contains "approximation"/other:     approximation, less authoritative
  Both go through the same gate; the source string only colors the error.

What this closes:
  An LLM generating plausible-looking scores in the 0-100 range (e.g.
  PDI=72 for Denmark when the real reference is 18). Range/structure
  checks miss this; reference-comparison catches it.

Usage:
  tests/validate_hofstede_reference.py              # all countries
  tests/validate_hofstede_reference.py FILE...      # only countries owning FILE(s)

Exit:
  0 if every checked country matches within +/-5 OR carries justification
    for each deviating dimension.
  1 if any dimension deviates without justification.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

# Inlined rather than imported from validate_hofstede_derived because that
# module imports heavy NLP deps (lingua) we don't need here, and CI hops
# this validator on PRs that haven't installed them. The regex parser is
# small enough that duplication beats the import overhead.
_README_SCORE_PATTERN = re.compile(
    r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|\s*(\d+)\s*\|",
    re.IGNORECASE,
)


def extract_hofstede_scores(readme_text: str) -> dict[str, int]:
    """Pull `{dim: score}` from any pipe-table rows in README.md.

    Same shape as validate_hofstede_derived.extract_hofstede_scores; if
    that one changes (e.g. accepts a new table format), this must follow.
    """
    return {
        m.group(1).upper(): int(m.group(2))
        for m in _README_SCORE_PATTERN.finditer(readme_text)
    }


HOFSTEDE_DIMENSIONS = ("PDI", "IDV", "UAI", "MAS", "LTO", "IND")
REFERENCE_TOLERANCE = 5
REFERENCE_PATH = ROOT / "data" / "hofstede_scores.json"

# Regions list mirrors the on-disk regions/ layout. Kept hardcoded rather
# than scanned so an empty regions/ doesn't silently widen target inference.
_REGIONS = frozenset({"africa", "americas", "asia", "europe", "oceania"})

# Match the `## Deviation justification` heading exactly at column 0.
# Case-insensitive so casing tweaks don't accidentally pass the check.
_DEVIATION_HEADING = re.compile(
    r"^##\s*Deviation\s+justification\b",
    re.IGNORECASE | re.MULTILINE,
)


def load_reference() -> dict[str, dict]:
    """Return ``{country_slug: {PDI..., source}}`` or {} if reference missing.

    Missing reference -> validator returns success but warns. We don't
    block contributors when the data we'd compare against doesn't exist.
    """
    if not REFERENCE_PATH.is_file():
        return {}
    payload = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
    return payload.get("scores", {})


def is_empirical(source: str) -> bool:
    """Hofstede Insights labels its survey data as 'Empirical research'."""
    return "empirical" in source.lower()


def deviation_section_body(decisions_text: str) -> str:
    """Return the body text of the ``## Deviation justification`` section.

    Spans from the heading to the next ``##``-level heading or EOF.
    Empty string if no such section exists.
    """
    m = _DEVIATION_HEADING.search(decisions_text)
    if not m:
        return ""
    tail = decisions_text[m.end():]
    next_h2 = re.search(r"^##\s", tail, re.MULTILINE)
    return tail[: next_h2.start()] if next_h2 else tail


def justified_dimensions(decisions_text: str) -> set[str]:
    """Set of dimension names mentioned in the deviation-justification body.

    Whole-word match: ``LTO`` matches ``### LTO`` and ``the LTO score`` but
    not ``GLOBAL``. Empty if no deviation section exists.
    """
    body = deviation_section_body(decisions_text)
    if not body:
        return set()
    return {dim for dim in HOFSTEDE_DIMENSIONS if re.search(rf"\b{dim}\b", body)}


def validate_country(
    country_dir: Path,
    reference: dict[str, dict],
) -> tuple[list[str], list[str]]:
    """Validate one country's declared vs reference scores.

    Returns ``(errors, info_messages)``. Caller aggregates and prints.
    """
    country = country_dir.name
    errors: list[str] = []
    info: list[str] = []

    ref = reference.get(country)
    if ref is None:
        info.append(f"{country}: no Hofstede reference data; skipping comparison.")
        return errors, info

    source = ref.get("source", "")
    readme = country_dir / "README.md"
    if not readme.is_file():
        errors.append(f"{country}: README.md missing; cannot validate reference scores.")
        return errors, info
    declared = extract_hofstede_scores(readme.read_text(encoding="utf-8"))
    if not declared:
        errors.append(f"{country}: no Hofstede scores found in README.md")
        return errors, info

    decisions_path = country_dir / "hofstede_decisions.md"
    decisions_text = (
        decisions_path.read_text(encoding="utf-8") if decisions_path.is_file() else ""
    )
    justified = justified_dimensions(decisions_text)
    source_kind = "Empirical" if is_empirical(source) else "Approximation"

    for dim in HOFSTEDE_DIMENSIONS:
        if dim not in declared or dim not in ref:
            continue
        decl = declared[dim]
        refv = ref[dim]
        gap = abs(decl - refv)
        if gap <= REFERENCE_TOLERANCE:
            continue
        if dim in justified:
            info.append(
                f"{country}: {dim}={decl} vs {source_kind.lower()} reference {refv} "
                f"(gap {gap}) -- justified."
            )
            continue
        errors.append(
            f"{country}: {dim}={decl} deviates from {source_kind} reference {refv} "
            f"(gap {gap} > {REFERENCE_TOLERANCE}). "
            f"Update README to within +/-{REFERENCE_TOLERANCE} of {refv}, "
            f"or add a '## Deviation justification' section in "
            f"hofstede_decisions.md naming {dim}."
        )
    return errors, info


def _country_dirs_for_files(file_args: list[str]) -> list[Path]:
    """Map file path args to their owning country directories.

    Resolves each arg's nearest ancestor whose grandparent name is a known
    region. Deduplicates so passing multiple files from one country only
    validates that country once.
    """
    by_name: dict[str, Path] = {}
    for arg in file_args:
        p = Path(arg).resolve()
        for parent in p.parents:
            if parent.parent.name in _REGIONS:
                by_name[parent.name] = parent
                break
    return sorted(by_name.values(), key=lambda d: d.name)


def _all_country_dirs() -> list[Path]:
    regions_dir = ROOT / "regions"
    if not regions_dir.is_dir():
        return []
    out: list[Path] = []
    for region in sorted(regions_dir.iterdir()):
        if not region.is_dir() or region.name not in _REGIONS:
            continue
        for country in sorted(region.iterdir()):
            if country.is_dir() and not country.name.startswith("."):
                out.append(country)
    return out


def main(argv: list[str]) -> int:
    reference = load_reference()
    if not reference:
        print(f"WARN: {REFERENCE_PATH} missing or empty; skipping reference checks.")
        return 0

    countries = (
        _country_dirs_for_files(argv[1:]) if len(argv) > 1 else _all_country_dirs()
    )
    if not countries:
        print("No countries to check.")
        return 0

    all_errors: list[str] = []
    all_info: list[str] = []
    for country_dir in countries:
        errors, info = validate_country(country_dir, reference)
        all_errors.extend(errors)
        all_info.extend(info)

    for line in all_info:
        print(f"INFO {line}")
    for err in all_errors:
        print(f"FAIL {err}")

    print(
        f"\nHofstede reference check: {len(countries)} country(ies) checked; "
        f"{len(all_errors)} deviation(s) without justification."
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
