"""Tests for tests/validate_language.py.

Pins the Phase-1+2 contract:
- data/language_policy.yaml is the single source of truth
- README `**Language(s):**` must parse and must resolve against the registry
- the gather CLIs return useful output without a lingua dependency
- per-culture exception files merge over the global one
- blockquotes are skipped before language detection
- --explain returns structured diagnostic output

Includes a live cross-check across every existing country README so
schema drift (a stub region added without a README registry entry, a
typo in `**Language(s):**`, etc.) fails CI immediately rather than
manifesting as a silent english-only fallback on the next culture PR.

Run: python3 -m pytest tests/test_validate_language.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import validate_language  # noqa: E402
from validate_language import (  # noqa: E402
    POLICY_PATH,
    _clean,
    _country_dir_for,
    _culture_exceptions_for,
    _parse_exceptions,
    _readme_registry_violations,
    _resolve_allowed_languages,
    explain,
    load_policy,
    parse_readme_languages,
)


# ---------------------------------------------------------------------
# load_policy
# ---------------------------------------------------------------------

class TestLoadPolicy:
    """The policy file's shape is part of the public contract."""

    def test_loads_repo_policy(self):
        policy = load_policy(POLICY_PATH)
        assert "languages" in policy
        assert "prose_sections" in policy
        assert "min_span_words" in policy
        assert isinstance(policy["languages"], list)
        assert isinstance(policy["prose_sections"], set)
        assert isinstance(policy["min_span_words"], int)
        assert len(policy["languages"]) > 0
        assert len(policy["prose_sections"]) > 0
        assert policy["min_span_words"] >= 1

    def test_languages_includes_english(self):
        """English is the lingua franca of the repo; if it goes missing
        the validator can't classify any infrastructure file."""
        policy = load_policy(POLICY_PATH)
        assert "english" in policy["languages"]

    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "nope.yaml"
        with pytest.raises(ValueError):
            load_policy(missing)

    def test_empty_languages_raises(self, tmp_path):
        p = tmp_path / "p.yaml"
        p.write_text(
            "languages: []\nprose_sections: [foo]\nmin_span_words: 15\n"
        )
        with pytest.raises(ValueError):
            load_policy(p)

    def test_empty_prose_sections_raises(self, tmp_path):
        p = tmp_path / "p.yaml"
        p.write_text(
            "languages: [english]\nprose_sections: []\nmin_span_words: 15\n"
        )
        with pytest.raises(ValueError):
            load_policy(p)

    def test_negative_min_span_raises(self, tmp_path):
        p = tmp_path / "p.yaml"
        p.write_text(
            "languages: [english]\nprose_sections: [foo]\nmin_span_words: 0\n"
        )
        with pytest.raises(ValueError):
            load_policy(p)


# ---------------------------------------------------------------------
# parse_readme_languages
# ---------------------------------------------------------------------

class TestParseReadmeLanguages:
    def test_single_language(self):
        assert parse_readme_languages("**Language(s):** German") == ["german"]

    def test_strips_parenthetical(self):
        """`German (Hochdeutsch)` -> `german`. The parenthetical is for
        humans; the slug is what counts."""
        assert parse_readme_languages(
            "**Language(s):** German (Hochdeutsch)"
        ) == ["german"]

    def test_multiple_languages(self):
        assert parse_readme_languages(
            "**Language(s):** English, German"
        ) == ["english", "german"]

    def test_case_insensitive(self):
        assert parse_readme_languages("**Language(s):** ENGLISH") == ["english"]

    def test_missing_line_returns_empty(self):
        assert parse_readme_languages("# Some heading\n\nbody") == []

    def test_full_readme_context(self):
        """Realistic shape: line embedded in a longer README."""
        readme = (
            "# Germany - Culture Content\n"
            "\n"
            "**Language(s):** German (Hochdeutsch)\n"
            "\n"
            "Some content here.\n"
        )
        assert parse_readme_languages(readme) == ["german"]


# ---------------------------------------------------------------------
# README registry live cross-check
# ---------------------------------------------------------------------

class TestReadmeRegistryCrossCheck:
    """Live audit across the real regions/ tree.

    Catches drift in two directions:
    - a country README typos a language slug
    - someone adds a language to a README without adding it to the YAML
    """

    def test_every_country_readme_in_registry(self):
        policy = load_policy(POLICY_PATH)
        violations = _readme_registry_violations(policy)
        assert violations == [], (
            "Every country README with a `**Language(s):**` line must "
            "name only languages registered in data/language_policy.yaml. "
            "Violations:\n"
            + "\n".join(f"  - {v.error}" for v in violations)
        )


# ---------------------------------------------------------------------
# _resolve_allowed_languages
# ---------------------------------------------------------------------

POLICY_TWO_LANG = {
    "languages": ["english", "german"],
    "prose_sections": {"shown"},
    "min_span_words": 15,
}


class TestResolveAllowedLanguages:
    def test_readme_is_always_english(self, tmp_path):
        country = tmp_path / "regions" / "europe" / "germany"
        country.mkdir(parents=True)
        readme = country / "README.md"
        readme.write_text("**Language(s):** German\n")
        assert _resolve_allowed_languages(readme, POLICY_TWO_LANG) == {"english"}

    def test_culture_file_inherits_readme(self, tmp_path):
        country = tmp_path / "regions" / "europe" / "germany"
        country.mkdir(parents=True)
        (country / "README.md").write_text("**Language(s):** German\n")
        culture = country / "culture_german_position.md"
        culture.write_text("# Position\n")
        assert _resolve_allowed_languages(culture, POLICY_TWO_LANG) == {"german"}

    def test_missing_readme_falls_back_to_english(self, tmp_path):
        country = tmp_path / "regions" / "europe" / "stub"
        country.mkdir(parents=True)
        culture = country / "culture_x_position.md"
        culture.write_text("# Position\n")
        assert _resolve_allowed_languages(culture, POLICY_TWO_LANG) == {"english"}

    def test_unknown_slug_in_readme_falls_back_to_english(self, tmp_path):
        """Unknown slugs are flagged separately by the cross-check; the
        resolved set falls back to english so the file isn't orphaned."""
        country = tmp_path / "regions" / "europe" / "germany"
        country.mkdir(parents=True)
        (country / "README.md").write_text("**Language(s):** Germansh\n")
        culture = country / "culture_german_position.md"
        culture.write_text("# Position\n")
        assert _resolve_allowed_languages(culture, POLICY_TWO_LANG) == {"english"}


# ---------------------------------------------------------------------
# Lingua slug coverage
# ---------------------------------------------------------------------

class TestLinguaSlugCoverage:
    """Every language in the policy registry must have a lingua mapping.

    Without this test, adding a language to data/language_policy.yaml
    without adding the corresponding `lingua.Language` entry would
    silently exclude that language from detection -- the validator
    would still pass files but would never flag them.

    Skipped when lingua isn't installed so the test suite still runs
    cleanly in environments without the NLP dep.
    """

    def test_every_registry_slug_maps_to_lingua(self):
        lang_map = validate_language._lingua_language_map()
        if lang_map is None:
            pytest.skip("lingua not installed")
        policy = load_policy(POLICY_PATH)
        missing = [s for s in policy["languages"] if s not in lang_map]
        assert missing == [], (
            "These language slugs are in data/language_policy.yaml but "
            "have no lingua.Language mapping in validate_language.py: "
            f"{missing}. Add them to _lingua_language_map()."
        )


# ---------------------------------------------------------------------
# Blockquote skipping
# ---------------------------------------------------------------------

class TestBlockquoteSkipping:
    """Lines starting with `>` are stripped before detection so cited
    source material can stay in its original language."""

    def test_blockquote_lines_removed(self):
        text = (
            "regular english prose here\n"
            "> foreign language quote goes here\n"
            "> more of the same quote\n"
            "more english prose\n"
        )
        cleaned = _clean(text)
        assert "foreign" not in cleaned
        assert "quote" not in cleaned
        assert "regular english" in cleaned
        assert "more english" in cleaned

    def test_blockquote_with_indent(self):
        """Indented `> ...` (markdown-legal under list items) is also
        stripped. The regex anchors on optional leading whitespace."""
        text = "  > indented quote in another language\nregular prose\n"
        cleaned = _clean(text)
        assert "indented" not in cleaned
        assert "regular prose" in cleaned

    def test_non_blockquote_preserved(self):
        """A `>` mid-line (e.g. comparison operator in a snippet) is
        not a blockquote and must not be stripped."""
        text = "this > that does not start with a > char\n"
        cleaned = _clean(text)
        assert "this" in cleaned
        assert "does not start" in cleaned


# ---------------------------------------------------------------------
# Per-culture exception overlay
# ---------------------------------------------------------------------

@pytest.fixture
def clear_culture_cache():
    """Clear the per-country exceptions cache around each test.

    The validator caches per-country exception files for process lifetime;
    tests that rebuild different tmp_path trees each run need a clean
    slate so a stale entry from a prior test doesn't leak in.
    """
    validate_language._culture_exception_cache.clear()
    yield
    validate_language._culture_exception_cache.clear()


def _make_country(root: Path, region: str, country: str) -> Path:
    p = root / "regions" / region / country
    p.mkdir(parents=True)
    return p


class TestPerCultureExceptions:
    """The Phase 2 friction reducer: per-country exception files.

    Live in regions/<region>/<country>/language_exceptions.txt and merge
    on top of the global tests/language_exceptions.txt. Contributors add
    country-specific proper nouns in their culture/<country> PR without
    needing a governance/* change to widen the global allowlist.
    """

    def test_returns_empty_when_no_file(self, tmp_path, clear_culture_cache):
        country = _make_country(tmp_path, "europe", "germany")
        culture = country / "culture_german_position.md"
        culture.write_text("# placeholder\n")
        assert _culture_exceptions_for(culture) == set()

    def test_loads_country_specific_words(self, tmp_path, clear_culture_cache):
        country = _make_country(tmp_path, "europe", "germany")
        (country / "language_exceptions.txt").write_text(
            "# German proper nouns specific to this culture\n"
            "Vergangenheitsbewältigung\n"
            "Erinnerungskultur\n"
            "\n"
            "# blank lines and comments are skipped\n"
            "Bundeskanzler\n"
        )
        culture = country / "culture_german_position.md"
        culture.write_text("# placeholder\n")
        assert _culture_exceptions_for(culture) == {
            "vergangenheitsbewältigung",
            "erinnerungskultur",
            "bundeskanzler",
        }

    def test_isolation_between_countries(self, tmp_path, clear_culture_cache):
        """Germany's exception is not Denmark's; the validator must
        scope per-country lookups."""
        germany = _make_country(tmp_path, "europe", "germany")
        denmark = _make_country(tmp_path, "europe", "denmark")
        (germany / "language_exceptions.txt").write_text("Bundeskanzler\n")
        (denmark / "language_exceptions.txt").write_text("Janteloven\n")
        de_file = germany / "culture_german_position.md"
        de_file.write_text("# x\n")
        dk_file = denmark / "culture_danish_position.md"
        dk_file.write_text("# x\n")
        assert _culture_exceptions_for(de_file) == {"bundeskanzler"}
        assert _culture_exceptions_for(dk_file) == {"janteloven"}

    def test_country_dir_for_culture_file(self, tmp_path):
        country = _make_country(tmp_path, "europe", "germany")
        culture = country / "culture_german_position.md"
        culture.write_text("# x\n")
        assert _country_dir_for(culture) == country.resolve()

    def test_country_dir_for_non_culture_path(self, tmp_path):
        outside = tmp_path / "tests" / "foo.py"
        outside.parent.mkdir(parents=True)
        outside.write_text("")
        assert _country_dir_for(outside) is None

    def test_country_dir_for_unknown_region_resolves(self, tmp_path):
        """Topology comes from the path shape, not a hardcoded region
        list, so an unfamiliar continent under regions/ still resolves
        (the same on-disk convention branch_scope.py uses)."""
        country = _make_country(tmp_path, "antarctica", "research_station")
        culture = country / "culture_x.md"
        culture.write_text("# x\n")
        assert _country_dir_for(culture) == country.resolve()


# ---------------------------------------------------------------------
# explain
# ---------------------------------------------------------------------

class TestExplain:
    """The --explain diagnostic. We test the structural shape rather
    than the lingua output (which is non-deterministic across versions);
    structural checks catch the integration bugs."""

    def test_unreadable_file_does_not_crash(self, tmp_path):
        ghost = tmp_path / "nonexistent.md"
        lines = explain(ghost)
        assert any("=== " in l for l in lines)
        assert any("could not read" in l for l in lines)

    def test_runs_without_lingua(self, tmp_path):
        """When lingua is absent, explain() prints a skip note rather
        than crashing -- mirrors validate()'s graceful degradation."""
        if validate_language._lingua_language_map() is not None:
            pytest.skip("lingua installed; this test exercises absence")
        culture = tmp_path / "regions" / "europe" / "germany" / "culture_x_position.md"
        culture.parent.mkdir(parents=True)
        culture.write_text("## Shown\n\nbody\n")
        lines = explain(culture)
        assert any("lingua not installed" in l for l in lines)


# ---------------------------------------------------------------------
# _parse_exceptions
# ---------------------------------------------------------------------

class TestParseExceptions:
    """The shared parser used by both global and per-culture files."""

    def test_missing_file_returns_empty(self, tmp_path):
        assert _parse_exceptions(tmp_path / "exc.txt") == set()

    def test_strips_comments_and_blanks(self, tmp_path):
        path = tmp_path / "exc.txt"
        path.write_text(
            "# a comment\n"
            "Foo\n"
            "\n"
            "  Bar  \n"
            "# trailing comment\n"
        )
        assert _parse_exceptions(path) == {"foo", "bar"}
