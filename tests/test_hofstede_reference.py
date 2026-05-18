"""Culture-docs Hofstede-free gate.

New architecture (issue #257): a country's deployable docs carry no
*reproduced* Hofstede analytical content. README.md / REFERENCES.md may
*cite* Hofstede as a source -- they must not reproduce the dimension
scores.

This gate is hard and PR-scoped. For every country a PR touches, that
country's README.md and REFERENCES.md must contain no Hofstede score
table. There is no exception list: a touched country must be in the new
architecture. Untouched countries are not evaluated here -- they migrate
the day they are next touched.

Replaces the former "README declared scores must match
hofstede_scores.json" check -- that was the old architecture, where the
README carried the score table.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# A Hofstede score-table row: a dimension-keyword cell followed by a
# number cell -- i.e. a reproduced score. A plain-text mention of
# "Hofstede" (a citation) does not match this and is allowed.
_SCORE_ROW = re.compile(
    r"\|[^|\n]*\b(?:PDI|IDV|UAI|MAS|LTO|IND)\b[^|\n]*\|\s*\d+\s*\|",
    re.IGNORECASE,
)

_DEPLOYABLE_DOCS = ("README.md", "REFERENCES.md")


def _pr_touched_countries() -> list[str]:
    """Country slugs whose regions/ files changed in this PR.

    PR_CHANGED_FILES is set by the setup job in validate.yml on PR events.
    Absent (push events, local runs) -> no countries: the gate is a no-op,
    because the PR is where it enforces.

    A sync/* PR is exempt: it mechanically funnels main's HEAD into
    culture/release (see tests/branch_scope.py), so it is integration, not
    a culture edit. The gate enforces on culture-development PRs and on the
    culture/release -> main promotion, not on syncs.
    """
    if os.environ.get("GITHUB_HEAD_REF", "").startswith("sync/"):
        return []
    changed = os.environ.get("PR_CHANGED_FILES", "").strip()
    if not changed:
        return []
    slugs = set()
    for path in changed.split():
        parts = path.split("/")
        if path.startswith("regions/") and len(parts) >= 4:
            slugs.add(parts[2])
    return sorted(slugs)


_COUNTRIES = _pr_touched_countries()


@pytest.mark.parametrize("country", _COUNTRIES or [None])
def test_touched_country_docs_are_hofstede_free(country):
    if country is None:
        pytest.skip(
            "no PR-touched country -- the docs-Hofstede-free gate enforces "
            "at the PR boundary"
        )

    hits = list((ROOT / "regions").glob(f"*/{country}"))
    if not hits:
        pytest.skip(f"{country}: no regions/*/{country}/ folder")
    cdir = hits[0]

    offenders: list[str] = []
    for doc in _DEPLOYABLE_DOCS:
        path = cdir / doc
        if not path.is_file():
            continue
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if _SCORE_ROW.search(line):
                offenders.append(f"{cdir.name}/{doc}:{lineno}")

    assert not offenders, (
        "release-gate FAIL [docs-hofstede-free]\n"
        f"  entity:  {country} -- " + ", ".join(offenders) + "\n"
        "  problem: a touched country's deployable docs still reproduce Hofstede\n"
        "           dimension scores (a score table). The new architecture does\n"
        "           not allow analytical content in shipped docs.\n"
        "  fix:     remove the Hofstede score table(s) from README.md /\n"
        "           REFERENCES.md. Citing Hofstede as a source is fine;\n"
        "           reproducing the dimension scores is not.\n"
        f"  lane:    culture (regions/*/{country}/)\n"
        "  ref:     issue #257 -- 'cite, don't reproduce'"
    )
