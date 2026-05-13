#!/usr/bin/env python3
"""Synchronize a country's README Hofstede sections with canonical data.

Rewrites two coupled markdown tables inside `regions/<region>/<country>/README.md`:

1. **Hofstede Cultural Dimensions** table -- declared score + band label
   per dimension. Declared scores come from `data/hofstede_scores.json`
   (empirical countries) or are kept as-authored (approximation countries
   that aren't in the JSON database). Band labels come from
   ``score_to_band()`` in ``scripts/audit_readme_bands.py`` (canonical
   0-39 Low / 40-69 Moderate / 70-100 High).

2. **Hofstede Alignment Status** table -- declared vs. derived score
   per dimension, plus gap and EXCELLENT / PASS / WARN / FAIL status.
   Derived scores are computed by the same binary-keyword formula as
   `tests/test_hofstede_derived.py` (`_derived`): for each dimension,
   sum the count of unique high-bag keywords present in the country's
   `culture_*.md` text, sum the count of unique low-bag keywords
   present, score = `int(high / (high + low) * 100)` or 50 if neither
   side appears. The formula is documented here AND mirrored in the
   test; the test pins the contract.

What it does NOT touch:
- The "How Dimensions Shape This Culture" prose section. Run
  ``scripts/audit_readme_bands.py --mismatch`` separately to surface
  prose band drift.
- The "Content Overview" / "Content Audit Status" tables, all other
  sections, and any prose surrounding the two tables.

Usage:
    scripts/update_hofstede_readme.py germany
    scripts/update_hofstede_readme.py germany --dry-run
    scripts/update_hofstede_readme.py --all              # every country
    scripts/update_hofstede_readme.py --all --dry-run

Exit status:
    0 on success (or dry-run printed the diff)
    1 on any country failure
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_HERE))

from data.hofstede_bag_loader import load_bag_for_language  # noqa: E402
from data.hofstede_keywords import detect_language  # noqa: E402
from audit_readme_bands import score_to_band  # noqa: E402  -- canonical 39/69

DIMS = ("PDI", "IDV", "UAI", "MAS", "LTO", "IND")

DIM_LABEL = {
    "PDI": "Power Distance (PDI)",
    "IDV": "Individualism (IDV)",
    "UAI": "Uncertainty Avoidance (UAI)",
    "MAS": "Masculinity (MAS)",
    "LTO": "Long-Term Orientation (LTO)",
    "IND": "Indulgence (IND)",
}

# Profile copy per (dimension, band). Kept identical to scaffold_country.py
# so output matches what a freshly scaffolded README would carry.
DIM_PROFILE = {
    "PDI": {
        "Low":      "Equality valued; hierarchy questioned",
        "Moderate": "Moderate hierarchy",
        "High":     "Hierarchy accepted",
    },
    "IDV": {
        "Low":      "Collective; group harmony",
        "Moderate": "Balanced",
        "High":     "Individual achievement",
    },
    "UAI": {
        "Low":      "Flexible; comfortable with ambiguity",
        "Moderate": "Balanced",
        "High":     "Structure and predictability",
    },
    "MAS": {
        "Low":      "Caring and cooperation",
        "Moderate": "Balanced",
        "High":     "Competitive and achievement-focused",
    },
    "LTO": {
        "Low":      "Short-term focused",
        "Moderate": "Balanced",
        "High":     "Long-term planning oriented",
    },
    "IND": {
        "Low":      "Restraint and discipline",
        "Moderate": "Balanced",
        "High":     "Indulgence and gratification",
    },
}

# Status thresholds match the L4f contract.
STATUS_EXCELLENT = 5
STATUS_PASS = 10
STATUS_WARN = 20

# Regex for declared-score rows in an existing markdown table:
#   `| <dim cell> | <score> | <anything> |`
_DECLARED_RE = re.compile(
    r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|\s*(\d+)\s*\|",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Country discovery
# ---------------------------------------------------------------------------

def find_country_dirs() -> list[Path]:
    """Return every `regions/<region>/<country>/` folder with a README."""
    regions = _ROOT / "regions"
    if not regions.is_dir():
        return []
    out: list[Path] = []
    for region in sorted(regions.iterdir()):
        if not region.is_dir() or region.name.startswith("."):
            continue
        for country in sorted(region.iterdir()):
            if not country.is_dir() or country.name.startswith("."):
                continue
            if (country / "README.md").is_file():
                out.append(country)
    return out


def resolve_country(slug: str) -> Path | None:
    """Walk regions/ and return the directory for `slug`, or None."""
    for c in find_country_dirs():
        if c.name == slug:
            return c
    return None


# ---------------------------------------------------------------------------
# Score loading & derivation
# ---------------------------------------------------------------------------

def load_declared_from_db(country_slug: str) -> dict[str, int] | None:
    """Load declared scores from `data/hofstede_scores.json` if the country
    has an empirical entry; return None for approximation countries."""
    db_path = _ROOT / "data" / "hofstede_scores.json"
    db = json.loads(db_path.read_text(encoding="utf-8"))
    entry = db.get("scores", {}).get(country_slug)
    if entry is None:
        return None
    out: dict[str, int] = {}
    for d in DIMS:
        if d in entry:
            out[d] = int(entry[d])
    return out


def parse_declared_from_readme(text: str) -> dict[str, int]:
    """Parse the first table block: dimension -> score.

    Used for approximation countries (no entry in hofstede_scores.json):
    the README itself carries the declared scores authored by hand.
    """
    seen: set[str] = set()
    out: dict[str, int] = {}
    for m in _DECLARED_RE.finditer(text):
        dim = m.group(1).upper()
        if dim in seen:
            continue
        seen.add(dim)
        out[dim] = int(m.group(2))
    return out


def derive_scores(country_dir: Path) -> dict[str, int]:
    """Binary-keyword derivation, identical to `_derived` in
    `tests/test_hofstede_derived.py`. Returns dimension -> 0-100.

    For each dimension:
      high = count of unique high-bag keywords present in the joined text
      low  = count of unique low-bag keywords present
      score = 50 if (high + low) == 0 else int(high / (high + low) * 100)
    """
    files = sorted(country_dir.glob("culture_*.md"))
    if not files:
        return {}
    all_text = "".join(f.read_text(encoding="utf-8") for f in files)
    if not all_text.strip():
        return {}
    language = detect_language(all_text)
    bag = load_bag_for_language(language, country_folder=country_dir, fallback=True)
    text_lower = all_text.lower()
    scores: dict[str, int] = {}
    for dim in DIMS:
        if dim not in bag:
            continue
        high = sum(
            1 for kw in bag[dim]["high"]
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower)
        )
        low = sum(
            1 for kw in bag[dim]["low"]
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower)
        )
        total = high + low
        scores[dim] = 50 if total == 0 else int(high / total * 100)
    return scores


# ---------------------------------------------------------------------------
# Alignment status
# ---------------------------------------------------------------------------

def compute_status(declared: int, derived: int) -> tuple[int, str]:
    """Return (gap, status_label) for one dimension.

    Status thresholds:
      gap <=  5  -> EXCELLENT
      gap <= 10  -> PASS
      gap <= 20  -> WARN
      gap >  20  -> FAIL
    """
    gap = abs(declared - derived)
    if gap <= STATUS_EXCELLENT:
        return gap, "EXCELLENT"
    if gap <= STATUS_PASS:
        return gap, "PASS"
    if gap <= STATUS_WARN:
        return gap, "WARN"
    return gap, "FAIL"


def _status_emoji(status: str) -> str:
    return {
        "EXCELLENT": "OK",
        "PASS":      "OK",
        "WARN":      "WARN",
        "FAIL":      "FAIL",
    }[status]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_dimensions_table(declared: dict[str, int]) -> str:
    """Render the 'Hofstede Cultural Dimensions' markdown table.

    Column shape (matches existing corpus):
        | Dimension | Score | Profile |

    Profile is `**<Band>** - <copy>` where band is canonical 39/69 and
    copy comes from DIM_PROFILE.
    """
    rows = [
        "| Dimension | Score | Profile |",
        "|-----------|-------|---------|",
    ]
    for dim in DIMS:
        if dim not in declared:
            continue
        score = declared[dim]
        band = score_to_band(score)
        copy = DIM_PROFILE[dim][band]
        rows.append(
            f"| {DIM_LABEL[dim]} | {score} | **{band}** - {copy} |"
        )
    return "\n".join(rows) + "\n"


def render_alignment_table(
    declared: dict[str, int],
    derived: dict[str, int],
) -> str:
    """Render the 'Hofstede Alignment Status' markdown table.

    Column shape (matches existing corpus):
        | Dimension | Declared | Derived | Gap | Status |
    """
    rows = [
        "| Dimension | Declared | Derived | Gap | Status |",
        "|-----------|----------|---------|-----|--------|",
    ]
    for dim in DIMS:
        if dim not in declared:
            continue
        d = declared[dim]
        if dim not in derived:
            rows.append(f"| {dim} | {d} | n/a | n/a | n/a (no bag for dimension) |")
            continue
        v = derived[dim]
        gap, status = compute_status(d, v)
        rows.append(f"| {dim} | {d} | {v} | {gap} | {_status_emoji(status)} {status} |")
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------------------
# README rewriting
# ---------------------------------------------------------------------------

def _replace_table_under_heading(
    text: str,
    heading_regex: str,
    new_table: str,
) -> tuple[str, bool]:
    """Replace the first markdown table that follows a matching heading.

    Returns (new_text, replaced). If `heading_regex` doesn't match,
    returns (text, False) without raising.

    The table is detected as the run of consecutive lines starting with
    '|' (after possibly a blank line) following the heading. Replacement
    preserves everything before the table and everything after.
    """
    head_re = re.compile(heading_regex, re.MULTILINE)
    m = head_re.search(text)
    if m is None:
        return text, False

    # Find the start of the table after the heading.
    after = text[m.end():]
    table_start_match = re.search(r"(\n\|)", after)
    if table_start_match is None:
        return text, False
    table_start_offset = table_start_match.start() + 1  # keep the newline before |

    # Find where the table ends: first line after `|...` runs that does not
    # start with `|`.
    rest = after[table_start_offset:]
    lines = rest.split("\n")
    table_lines: list[str] = []
    for i, line in enumerate(lines):
        if line.startswith("|"):
            table_lines.append(line)
            continue
        # First non-| line; that's the table end.
        break
    else:
        # Reached EOF inside the table.
        i = len(lines)

    table_end_offset = table_start_offset + sum(len(l) + 1 for l in table_lines)
    # Strip the trailing newline we counted with the last table line so the
    # replacement re-introduces exactly one newline boundary.
    new = (
        text[: m.end()]
        + after[:table_start_offset]
        + new_table.rstrip("\n") + "\n"
        + after[table_end_offset:]
    )
    return new, True


def update_readme(
    text: str,
    country_name: str,
    declared: dict[str, int],
    derived: dict[str, int],
) -> tuple[str, list[str]]:
    """Rewrite the two Hofstede tables. Returns (new_text, warnings).

    Warnings are non-fatal -- e.g., a heading wasn't found and the block
    was skipped. The caller can decide whether to surface or fail on them.
    """
    warnings: list[str] = []
    new_dim_table = render_dimensions_table(declared)
    new_align_table = render_alignment_table(declared, derived)

    text, ok1 = _replace_table_under_heading(
        text,
        rf"^##\s*Hofstede\s+Cultural\s+Dimensions\b.*$",
        new_dim_table,
    )
    if not ok1:
        warnings.append(
            "Hofstede Cultural Dimensions heading or table not found; skipped."
        )

    text, ok2 = _replace_table_under_heading(
        text,
        r"^##\s*Hofstede\s+Alignment\s+Status\b.*$",
        new_align_table,
    )
    if not ok2:
        warnings.append(
            "Hofstede Alignment Status heading or table not found; skipped."
        )

    return text, warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _process_country(country_dir: Path, dry_run: bool) -> tuple[bool, list[str]]:
    """Update one country's README. Returns (ok, messages)."""
    msgs: list[str] = []
    readme = country_dir / "README.md"
    text = readme.read_text(encoding="utf-8")
    country_name = country_dir.name.replace("_", " ").title()
    country_slug = country_dir.name

    declared = load_declared_from_db(country_slug)
    if declared is None:
        # Approximation country -- declared scores live in the README itself.
        declared = parse_declared_from_readme(text)
        if not declared:
            return False, [f"{country_slug}: no declared scores in DB or README"]
        msgs.append(f"{country_slug}: declared from README (approximation country)")
    else:
        msgs.append(f"{country_slug}: declared from data/hofstede_scores.json")

    try:
        derived = derive_scores(country_dir)
    except RuntimeError as exc:
        return False, [f"{country_slug}: derivation failed: {exc}"]

    new_text, warnings = update_readme(text, country_name, declared, derived)
    msgs.extend(f"{country_slug}: {w}" for w in warnings)

    if new_text == text:
        msgs.append(f"{country_slug}: no changes")
        return True, msgs

    if dry_run:
        msgs.append(f"{country_slug}: [dry-run] would update README.md")
    else:
        readme.write_text(new_text, encoding="utf-8")
        msgs.append(f"{country_slug}: README.md updated")

    return True, msgs


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="update_hofstede_readme.py",
        description=(
            "Synchronize a country's README Hofstede tables (Cultural "
            "Dimensions + Alignment Status) with canonical declared "
            "scores and the live derived calculation."
        ),
    )
    parser.add_argument(
        "country", nargs="?",
        help="Country slug (e.g. 'germany'). Required unless --all is given.",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Process every country folder under regions/.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compute and print changes but do not write the file.",
    )
    args = parser.parse_args(argv[1:])

    if args.all and args.country:
        parser.error("--all and a country argument are mutually exclusive")
    if not args.all and not args.country:
        parser.error("provide a country slug or --all")

    if args.all:
        countries = find_country_dirs()
    else:
        d = resolve_country(args.country)
        if d is None:
            print(f"ERROR: country '{args.country}' not found under regions/")
            return 1
        countries = [d]

    failures = 0
    for cd in countries:
        ok, msgs = _process_country(cd, dry_run=args.dry_run)
        for m in msgs:
            print(m)
        if not ok:
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
