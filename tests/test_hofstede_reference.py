"""Cultures Hofstede reference validation.

For each country with a README, compare declared scores against
data/hofstede_scores.json. Tolerance: +-5 per dimension.

A gap > 5 requires a ## Deviation justification section in
hofstede_decisions.md explicitly naming the dimension. Without it: FAIL.

No imports from validate_hofstede_reference.py -- logic is self-contained.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REFERENCE_PATH = ROOT / "data" / "hofstede_scores.json"

DIMENSIONS = ("PDI", "IDV", "UAI", "MAS", "LTO", "IND")
TOLERANCE = 5

_SCORE_RE = re.compile(
    r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|\s*(\d+)\s*\|",
    re.IGNORECASE,
)
_DEVIATION_H2 = re.compile(
    r"^##\s*Deviation\s+justification\b",
    re.IGNORECASE | re.MULTILINE,
)


def _load_reference() -> dict:
    if not REFERENCE_PATH.is_file():
        return {}
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8")).get("scores", {})


def _country_dirs() -> list[Path]:
    regions = ROOT / "regions"
    out = []
    for region in sorted(regions.iterdir()):
        if not region.is_dir() or region.name.startswith("."):
            continue
        for country in sorted(region.iterdir()):
            if not country.is_dir() or country.name.startswith("."):
                continue
            if (country / "README.md").is_file():
                out.append(country)
    return out


def _parse_scores(readme: str) -> dict[str, int]:
    return {m.group(1).upper(): int(m.group(2)) for m in _SCORE_RE.finditer(readme)}


def _justified_dims(decisions_text: str) -> set[str]:
    m = _DEVIATION_H2.search(decisions_text)
    if not m:
        return set()
    tail = decisions_text[m.end():]
    nxt = re.search(r"^##\s", tail, re.MULTILINE)
    body = tail[: nxt.start()] if nxt else tail
    return {dim for dim in DIMENSIONS if re.search(rf"\b{dim}\b", body)}


_REFERENCE = _load_reference()
_COUNTRIES = _country_dirs()


@pytest.mark.parametrize("country_dir", _COUNTRIES, ids=[c.name for c in _COUNTRIES])
def test_declared_scores_match_reference(country_dir: Path):
    ref = _REFERENCE.get(country_dir.name)
    if ref is None:
        pytest.skip(f"no reference data for {country_dir.name}")

    declared = _parse_scores((country_dir / "README.md").read_text(encoding="utf-8"))
    assert declared, f"{country_dir.name}: no Hofstede scores found in README.md"

    decisions_path = country_dir / "hofstede_decisions.md"
    decisions_text = (
        decisions_path.read_text(encoding="utf-8") if decisions_path.is_file() else ""
    )
    justified = _justified_dims(decisions_text)
    source_kind = "Empirical" if "empirical" in ref.get("source", "").lower() else "Approximation"

    failures = []
    for dim in DIMENSIONS:
        if dim not in declared or dim not in ref:
            continue
        gap = abs(declared[dim] - ref[dim])
        if gap <= TOLERANCE or dim in justified:
            continue
        failures.append(
            f"  {dim}={declared[dim]} vs {source_kind} reference {ref[dim]} "
            f"(gap {gap} > {TOLERANCE}) -- update score or add "
            f"## Deviation justification in hofstede_decisions.md naming {dim}"
        )

    assert not failures, (
        f"{country_dir.name}: score deviation(s) without justification:\n"
        + "\n".join(failures)
    )
