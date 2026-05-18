"""Consistency gate -- REFERENCES.md Hofstede table vs scores.json / bags / READMEs.

The "Hofstede Dimension Scores" table in the repository-root REFERENCES.md
is the canonical, human-reviewable record of every developed culture's six
Hofstede scores. This test asserts that every other place those scores are
stored agrees with the table:

  - data/hofstede_scores.json                   (central registry)
  - regions/<region>/<slug>/hofstede_bag.yaml   ('hofstede_scores' block)
  - regions/<region>/<slug>/README.md           (declared score table)

A drift like the one this gate was built for -- hofstede_scores.json still
carrying Nigeria's old West-Africa-cluster values (77/20/54) after the
country profile moved to 80/30/55 -- now fails CI instead of sitting latent.

If REFERENCES.md carries no Hofstede table yet, the test skips, so it can
land independently of the PR that introduces the table.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent

_DIMS = ["PDI", "IDV", "UAI", "MAS", "LTO", "IND"]

# A REFERENCES.md table data row: a country name followed by six integers.
# The header row ("Country | PDI | ...") and separator ("---|---") carry no
# digit cells / no leading letter, so neither matches.
_ROW_RE = re.compile(
    r"^\|\s*([A-Za-z][A-Za-z .'-]*?)\s*\|" + r"\s*(\d+)\s*\|" * 6,
    re.MULTILINE,
)

# A country README declared-score cell: | ... PDI ... | 38 |
_README_SCORE_RE = re.compile(
    r"\|[^|\n]*\b(PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|\s*(\d+)\s*\|",
    re.IGNORECASE,
)


def _reference_table() -> dict[str, dict[str, int]]:
    """Parse the `## Hofstede Dimension Scores` table from root REFERENCES.md.

    Returns ``{slug: {DIM: score}}``; an empty dict if the section is absent.
    Parsing is scoped to that section so an unrelated table elsewhere in the
    file can never be mistaken for the score table.
    """
    refs = _ROOT / "REFERENCES.md"
    if not refs.is_file():
        return {}
    section = re.search(
        r"^##\s+Hofstede Dimension Scores\s*$(.*?)(?=^##\s|\Z)",
        refs.read_text(encoding="utf-8"),
        re.MULTILINE | re.DOTALL,
    )
    if not section:
        return {}
    table: dict[str, dict[str, int]] = {}
    for row in _ROW_RE.finditer(section.group(1)):
        slug = row.group(1).strip().lower()
        table[slug] = {dim: int(row.group(i + 2)) for i, dim in enumerate(_DIMS)}
    return table


def _country_dir(slug: str) -> Path | None:
    hits = list(_ROOT.glob(f"regions/*/{slug}/hofstede_bag.yaml"))
    return hits[0].parent if hits else None


_TABLE = _reference_table()
_COUNTRIES = sorted(_TABLE) or [None]


@pytest.mark.parametrize("slug", _COUNTRIES)
def test_scores_consistent_with_references(slug):
    if slug is None:
        pytest.skip("no Hofstede Dimension Scores table in REFERENCES.md yet")

    expected = _TABLE[slug]

    # 1. data/hofstede_scores.json
    scores = json.loads(
        (_ROOT / "data" / "hofstede_scores.json").read_text(encoding="utf-8")
    )["scores"]
    assert slug in scores, f"{slug}: missing from data/hofstede_scores.json"
    js = {d: scores[slug].get(d) for d in _DIMS}
    assert js == expected, (
        f"{slug}: data/hofstede_scores.json {js} != REFERENCES.md {expected}"
    )

    cdir = _country_dir(slug)
    assert cdir is not None, f"{slug}: no regions/*/{slug}/hofstede_bag.yaml"

    # 2. the country's hofstede_bag.yaml
    bag = yaml.safe_load(
        (cdir / "hofstede_bag.yaml").read_text(encoding="utf-8")
    ).get("hofstede_scores", {})
    bag6 = {d: bag.get(d) for d in _DIMS}
    assert bag6 == expected, (
        f"{slug}: {cdir.name}/hofstede_bag.yaml {bag6} != REFERENCES.md {expected}"
    )

    # 3. the country's README declared scores
    readme = cdir / "README.md"
    assert readme.is_file(), f"{slug}: no README.md"
    declared = {
        m.group(1).upper(): int(m.group(2))
        for m in _README_SCORE_RE.finditer(readme.read_text(encoding="utf-8"))
    }
    rd6 = {d: declared.get(d) for d in _DIMS}
    assert rd6 == expected, (
        f"{slug}: {cdir.name}/README.md declared {rd6} != REFERENCES.md {expected}"
    )
