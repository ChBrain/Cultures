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
from culture_metadata import read_metadata
from validate_language import load_policy, POLICY_PATH

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


# NLP-only languages (Igbo, Hausa, Pidgin, ...) have no keyword bag and
# the LLM-judged signal isn't a keyword signal. A culture_*.md file whose
# frontmatter declares one of these languages is skipped from the keyword
# aggregation -- the lingua-known files in the same country still
# aggregate, so the country's derived score is computed from the bag
# language alone, not diluted by content the validator can't score.
#
# Resolved once at import time: the policy is governance-tracked, so
# missing-config means the test suite has bigger problems than NLP
# routing. Empty list (default policy + no NLP languages) keeps the
# original behaviour for every existing file.
try:
    _POLICY_HF = load_policy(POLICY_PATH)
    _NLP_LANGUAGES = set(_POLICY_HF.get("nlp_languages") or [])
    _ISO_MAP = _POLICY_HF.get("iso_map") or {}
except Exception:
    _NLP_LANGUAGES = set()
    _ISO_MAP = {}


def _is_nlp_language_file(file_path: Path) -> bool:
    """True if ``file_path``'s frontmatter declares an NLP-only language."""
    if not _NLP_LANGUAGES:
        return False
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    try:
        meta = read_metadata(text)
    except Exception:
        return False
    if not isinstance(meta, dict):
        return False
    raw = meta.get("language")
    if raw is None:
        return False
    iso = str(raw).strip().lower()
    name = _ISO_MAP.get(iso)
    return name in _NLP_LANGUAGES


def _scored_culture_files(country_dir: Path) -> list[Path]:
    """Culture files contributing to the country's keyword aggregation.

    Filters NLP-only-language files (Igbo, Hausa, Pidgin, ...): they have
    no keyword bag and the NLP check from culture-review.yml is the gate
    for their content, not a keyword count here.
    """
    return [
        f for f in country_dir.glob("culture_*.md")
        if not _is_nlp_language_file(f)
    ]


def _declared(country_id: str) -> dict[str, int]:
    """Declared Hofstede scores for a country from the single home."""
    entry = _SCORES.get(country_id, {})
    return {dim: entry[dim] for dim in _DIMS if isinstance(entry.get(dim), int)}


def _derived(country_dir: Path, language: str) -> dict[str, int | None]:
    """Derived score per dimension from culture-file keyword density.

    A dimension maps to ``None`` when the content has zero keyword hits
    for it (high + low == 0): the score is unverifiable, not 50. Folding
    no-signal into a mid-range default let a dimension the content never
    expresses pass the ±tolerance gate whenever its declared score sat
    near 50. The caller treats ``None`` as a gate failure.
    """
    keywords = load_bag_for_language(language, country_folder=country_dir, fallback=True)
    all_text = "".join(
        f.read_text(encoding="utf-8", errors="replace").lower()
        for f in _scored_culture_files(country_dir)
    )
    scores: dict[str, int | None] = {}
    for dim in _DIMS:
        if dim not in keywords:
            continue
        high = sum(1 for kw in keywords[dim]["high"] if re.search(r"\b" + re.escape(kw) + r"\b", all_text))
        low = sum(1 for kw in keywords[dim]["low"] if re.search(r"\b" + re.escape(kw) + r"\b", all_text))
        total = high + low
        scores[dim] = None if total == 0 else int(high / total * 100)
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
        for f in _scored_culture_files(country_dir)
    )
    language = detect_language(all_text)
    derived = _derived(country_dir, language)

    failures = []
    for dim in _DIMS:
        if dim not in declared or dim not in derived:
            continue
        if derived[dim] is None:
            detail = (
                f"{dim}: declared={declared[dim]}, derived=<no signal> "
                f"-- the culture content carries no {dim} keyword, so the "
                f"declared score cannot be verified"
            )
        else:
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
        f"{country_dir.name}: dimension(s) failed the derived-score gate "
        f"-- this PR changes the country's culture files, so every Hofstede "
        f"dimension must be expressed in the content and derive within "
        f"±{_TOLERANCE} of declared:\n"
        + "\n".join(f"  {f}" for f in failures)
    )


# ---------------------------------------------------------------------------
# NLP-language skip (Nigeria mother-tongue arc -- Stage 2c)
# ---------------------------------------------------------------------------

class TestNlpLanguageSkip:
    """A culture file whose frontmatter declares an NLP-only language
    (Igbo, Hausa, Pidgin, ...) is excluded from the keyword aggregation:
    no bag exists for the language, and the LLM-judged signal isn't a
    keyword signal. The country's derived score is computed from the
    lingua-known files alone."""

    def _make_country(self, tmp_path: Path) -> Path:
        country = tmp_path / "regions" / "africa" / "testland"
        country.mkdir(parents=True)
        (country / "README.md").write_text("# Testland\n**Language(s):** English\n")
        return country

    def test_nlp_file_detected(self, tmp_path):
        """The detector recognises a `language: ig` frontmatter file."""
        if not _NLP_LANGUAGES:
            pytest.skip("policy did not load nlp_languages")
        country = self._make_country(tmp_path)
        f = country / "culture_x_position_language_igbo.md"
        f.write_text(
            "---\nkhai: position\nlanguage: ig\n---\n# body\n",
            encoding="utf-8",
        )
        assert _is_nlp_language_file(f) is True

    def test_lingua_file_not_flagged(self, tmp_path):
        country = self._make_country(tmp_path)
        f = country / "culture_x_position_language.md"
        f.write_text(
            "---\nkhai: position\nlanguage: en\n---\n# body\n",
            encoding="utf-8",
        )
        assert _is_nlp_language_file(f) is False

    def test_absent_language_field_not_flagged(self, tmp_path):
        """Back-compat: a file with no `language:` field is not NLP."""
        country = self._make_country(tmp_path)
        f = country / "culture_x_position.md"
        f.write_text(
            "---\nkhai: position\n---\n# body\n",
            encoding="utf-8",
        )
        assert _is_nlp_language_file(f) is False

    def test_scored_files_omits_nlp(self, tmp_path):
        """A country with one english file and one Igbo file has the
        Igbo file dropped from the aggregation set."""
        if not _NLP_LANGUAGES:
            pytest.skip("policy did not load nlp_languages")
        country = self._make_country(tmp_path)
        en = country / "culture_x_position_language.md"
        en.write_text(
            "---\nkhai: position\nlanguage: en\n---\n# english body\n",
            encoding="utf-8",
        )
        ig = country / "culture_x_position_language_igbo.md"
        ig.write_text(
            "---\nkhai: position\nlanguage: ig\n---\n# igbo body\n",
            encoding="utf-8",
        )
        scored = set(_scored_culture_files(country))
        assert scored == {en}, (
            f"NLP-language file must be excluded from aggregation; got {scored}"
        )

    def test_country_score_unchanged_when_nlp_added(self, tmp_path):
        """The whole point of the skip: adding an NLP file must not
        change the set the keyword aggregator sees."""
        if not _NLP_LANGUAGES:
            pytest.skip("policy did not load nlp_languages")
        country = self._make_country(tmp_path)
        en = country / "culture_x_position_language.md"
        en.write_text(
            "---\nkhai: position\nlanguage: en\n---\n# english body\n",
            encoding="utf-8",
        )
        scored_without = set(_scored_culture_files(country))

        ig = country / "culture_x_position_language_igbo.md"
        ig.write_text(
            "---\nkhai: position\nlanguage: ig\n---\n# igbo body\n",
            encoding="utf-8",
        )
        scored_with = set(_scored_culture_files(country))
        assert scored_without == scored_with, (
            "Adding an NLP-language file must not change the scored set; "
            f"without={scored_without} with={scored_with}"
        )
