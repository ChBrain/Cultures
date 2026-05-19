"""L4f: Derived Hofstede scores vs declared — keyword scoring across all culture files."""
import json
import os
import re
import sys
import warnings
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_ROOT))

from data.hofstede_keywords import detect_language
from data.hofstede_bag_loader import load_bag_for_language

_DIMS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]

# The derived score must land within ±5 of the declared score. On a PR that
# changes a country's culture files this is enforced as a hard failure for
# the changed countries (see _STRICT below); elsewhere -- push, local,
# full-corpus runs -- it stays advisory (a warning), so a latent gap in an
# untouched country never blocks unrelated work.
_TOLERANCE = 5

# Declared scores come from data/hofstede_scores.json -- the single home for
# Hofstede data. A migrated country's README no longer carries a score table
# (test_hofstede_reference enforces that), so the README is not a usable
# source. Reading the canonical scores keyed by country id means migrated
# countries are checked, not skipped: the ±5 gate applies everywhere.
_SCORES_PATH = _ROOT / "data" / "hofstede_scores.json"
_SCORES: dict[str, dict] = json.loads(
    _SCORES_PATH.read_text(encoding="utf-8")
).get("scores", {})


def _country_dirs() -> list[Path]:
    regions = _ROOT / "regions"
    if not regions.is_dir():
        return []
    countries = []
    for region_dir in sorted(regions.iterdir()):
        if not region_dir.is_dir() or region_dir.name.startswith("."):
            continue
        for country_dir in sorted(region_dir.iterdir()):
            if not country_dir.is_dir() or country_dir.name.startswith("."):
                continue
            if list(country_dir.glob("culture_*.md")):
                countries.append(country_dir)
    return countries


def _declared(country_id: str) -> dict[str, int]:
    """Declared Hofstede scores for a country from the single home."""
    entry = _SCORES.get(country_id, {})
    return {dim: entry[dim] for dim in _DIMS if isinstance(entry.get(dim), int)}


def _derived(country_dir: Path, language: str) -> dict[str, int]:
    keywords = load_bag_for_language(language, country_folder=country_dir, fallback=True)
    all_text = "".join(
        f.read_text(encoding="utf-8", errors="replace").lower()
        for f in country_dir.glob("culture_*.md")
    )
    scores: dict[str, int] = {}
    for dim in _DIMS:
        if dim not in keywords:
            continue
        high = sum(1 for kw in keywords[dim]["high"] if re.search(r"\b" + re.escape(kw) + r"\b", all_text))
        low = sum(1 for kw in keywords[dim]["low"] if re.search(r"\b" + re.escape(kw) + r"\b", all_text))
        total = high + low
        scores[dim] = 50 if total == 0 else int(high / total * 100)
    return scores


_COUNTRIES = _country_dirs()

# Narrow to PR-changed countries when CI is running on a PR. Env vars are
# set by the L4f job in .github/workflows/validate.yml; absent on push events
# or local runs, which keeps the full corpus in scope. A Denmark-only
# deviation shouldn't fail a Germany PR's CI.
_pr_changed = os.environ.get("PR_CHANGED_FILES", "").strip()
_pr_data_changed = os.environ.get("PR_DATA_CHANGED", "").strip().lower() == "true"
if _pr_changed and not _pr_data_changed:
    _pr_slugs = {
        p.split("/")[2]
        for p in _pr_changed.split()
        if p.startswith("regions/") and len(p.split("/")) >= 4
    }
    _COUNTRIES = [d for d in _COUNTRIES if d.name in _pr_slugs]

# Strict (hard-fail) mode: a regions/ PR scoped to specific changed countries
# -- exactly the case where _COUNTRIES was narrowed just above. Those
# countries are "in flight" and must meet ±_TOLERANCE. Push / local /
# data-change runs stay advisory (warn only): a strict ±5 gate must never
# retroactively fail the whole corpus, only the countries a PR is touching.
_STRICT = bool(_pr_changed) and not _pr_data_changed


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_derived_within_tolerance(country_dir: Path):
    declared = _declared(country_dir.name)
    if not declared:
        pytest.skip("no declared scores in data/hofstede_scores.json")

    all_text = "".join(
        f.read_text(encoding="utf-8", errors="replace")
        for f in country_dir.glob("culture_*.md")
    )
    language = detect_language(all_text)
    derived = _derived(country_dir, language)

    failures = []
    for dim in _DIMS:
        if dim not in declared or dim not in derived:
            continue
        gap = abs(declared[dim] - derived[dim])
        if gap <= _TOLERANCE:
            continue
        detail = (
            f"{dim}: declared={declared[dim]}, derived={derived[dim]}, "
            f"gap={gap} > ±{_TOLERANCE}"
        )
        if _STRICT:
            failures.append(detail)
        else:
            warnings.warn(f"{country_dir.name}: {detail} [WARN]", stacklevel=2)

    assert not failures, (
        f"{country_dir.name}: dimension(s) outside ±{_TOLERANCE} tolerance "
        f"-- this PR changes the country's culture files, so the derived "
        f"Hofstede scores must land within ±{_TOLERANCE} of declared:\n"
        + "\n".join(f"  {f}" for f in failures)
    )
