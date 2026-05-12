"""Unit tests for tests/validate_language.py.

Pins the Phase-1 contract:
- data/language_policy.yaml is the single source of truth
- README `**Language(s):**` must parse and must resolve against the registry
- the gather CLIs return useful output without a lingua dependency

Also includes a live cross-check across every existing country README, so
schema drift (a stub region added without a README registry entry, a
typo in `**Language(s):**`, etc.) fails CI immediately rather than
manifesting as a silent english-only fallback on the next culture PR.

Run: python3 -m unittest tests.test_validate_language
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

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


class TestLoadPolicy(unittest.TestCase):
    """The policy file's shape is part of the public contract."""

    def test_loads_repo_policy(self):
        policy = load_policy(POLICY_PATH)
        self.assertIn("languages", policy)
        self.assertIn("prose_sections", policy)
        self.assertIn("min_span_words", policy)
        self.assertIsInstance(policy["languages"], list)
        self.assertIsInstance(policy["prose_sections"], set)
        self.assertIsInstance(policy["min_span_words"], int)
        self.assertGreater(len(policy["languages"]), 0)
        self.assertGreater(len(policy["prose_sections"]), 0)
        self.assertGreaterEqual(policy["min_span_words"], 1)

    def test_languages_includes_english(self):
        """English is the lingua franca of the repo; if it goes missing
        the validator can't classify any infrastructure file."""
        policy = load_policy(POLICY_PATH)
        self.assertIn("english", policy["languages"])

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "nope.yaml"
            with self.assertRaises(ValueError):
                load_policy(missing)

    def test_empty_languages_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "p.yaml"
            p.write_text(
                "languages: []\nprose_sections: [foo]\nmin_span_words: 15\n"
            )
            with self.assertRaises(ValueError):
                load_policy(p)

    def test_empty_prose_sections_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "p.yaml"
            p.write_text(
                "languages: [english]\nprose_sections: []\nmin_span_words: 15\n"
            )
            with self.assertRaises(ValueError):
                load_policy(p)

    def test_negative_min_span_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "p.yaml"
            p.write_text(
                "languages: [english]\nprose_sections: [foo]\nmin_span_words: 0\n"
            )
            with self.assertRaises(ValueError):
                load_policy(p)


class TestParseReadmeLanguages(unittest.TestCase):
    def test_single_language(self):
        self.assertEqual(
            parse_readme_languages("**Language(s):** German"),
            ["german"],
        )

    def test_strips_parenthetical(self):
        """`German (Hochdeutsch)` -> `german`. The parenthetical is for
        humans; the slug is what counts."""
        self.assertEqual(
            parse_readme_languages("**Language(s):** German (Hochdeutsch)"),
            ["german"],
        )

    def test_multiple_languages(self):
        self.assertEqual(
            parse_readme_languages("**Language(s):** English, German"),
            ["english", "german"],
        )

    def test_case_insensitive(self):
        self.assertEqual(
            parse_readme_languages("**Language(s):** ENGLISH"),
            ["english"],
        )

    def test_missing_line_returns_empty(self):
        self.assertEqual(parse_readme_languages("# Some heading\n\nbody"), [])

    def test_full_readme_context(self):
        """Realistic shape: line embedded in a longer README."""
        readme = (
            "# Germany - Culture Content\n"
            "\n"
            "**Language(s):** German (Hochdeutsch)\n"
            "\n"
            "Some content here.\n"
        )
        self.assertEqual(parse_readme_languages(readme), ["german"])


class TestReadmeRegistryCrossCheck(unittest.TestCase):
    """Live audit across the real regions/ tree.

    Catches drift in two directions:
    - a country README typos a language slug
    - someone adds a language to a README without adding it to the YAML
    """

    def test_every_country_readme_in_registry(self):
        policy = load_policy(POLICY_PATH)
        violations = _readme_registry_violations(policy)
        self.assertEqual(
            violations,
            [],
            "Every country README with a `**Language(s):**` line must "
            "name only languages registered in data/language_policy.yaml. "
            f"Violations:\n" + "\n".join(f"  - {v.error}" for v in violations),
        )


class TestResolveAllowedLanguages(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.policy = {
            "languages": ["english", "german"],
            "prose_sections": {"shown"},
            "min_span_words": 15,
        }

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write(self, rel: str, body: str = "") -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        return p

    def test_readme_is_always_english(self):
        country = self.root / "regions" / "europe" / "germany"
        country.mkdir(parents=True)
        readme = country / "README.md"
        readme.write_text("**Language(s):** German\n")
        self.assertEqual(
            _resolve_allowed_languages(readme, self.policy),
            {"english"},
        )

    def test_culture_file_inherits_readme(self):
        country = self.root / "regions" / "europe" / "germany"
        country.mkdir(parents=True)
        (country / "README.md").write_text("**Language(s):** German\n")
        culture = country / "culture_german_position.md"
        culture.write_text("# Position\n")
        self.assertEqual(
            _resolve_allowed_languages(culture, self.policy),
            {"german"},
        )

    def test_missing_readme_falls_back_to_english(self):
        country = self.root / "regions" / "europe" / "stub"
        country.mkdir(parents=True)
        culture = country / "culture_x_position.md"
        culture.write_text("# Position\n")
        self.assertEqual(
            _resolve_allowed_languages(culture, self.policy),
            {"english"},
        )

    def test_unknown_slug_in_readme_falls_back_to_english(self):
        """Unknown slugs are flagged separately by the cross-check; the
        resolved set falls back to english so the file isn't orphaned."""
        country = self.root / "regions" / "europe" / "germany"
        country.mkdir(parents=True)
        (country / "README.md").write_text("**Language(s):** Germansh\n")
        culture = country / "culture_german_position.md"
        culture.write_text("# Position\n")
        self.assertEqual(
            _resolve_allowed_languages(culture, self.policy),
            {"english"},
        )


class TestLinguaSlugCoverage(unittest.TestCase):
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
            self.skipTest("lingua not installed")
        policy = load_policy(POLICY_PATH)
        missing = [s for s in policy["languages"] if s not in lang_map]
        self.assertEqual(
            missing,
            [],
            "These language slugs are in data/language_policy.yaml but "
            "have no lingua.Language mapping in validate_language.py: "
            f"{missing}. Add them to _lingua_language_map().",
        )


class TestBlockquoteSkipping(unittest.TestCase):
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
        self.assertNotIn("foreign", cleaned)
        self.assertNotIn("quote", cleaned)
        self.assertIn("regular english", cleaned)
        self.assertIn("more english", cleaned)

    def test_blockquote_with_indent(self):
        """Indented `> ...` (markdown-legal under list items) is also
        stripped. The regex anchors on optional leading whitespace."""
        text = "  > indented quote in another language\nregular prose\n"
        cleaned = _clean(text)
        self.assertNotIn("indented", cleaned)
        self.assertIn("regular prose", cleaned)

    def test_non_blockquote_preserved(self):
        """A `>` mid-line (e.g. comparison operator in a snippet) is
        not a blockquote and must not be stripped."""
        text = "this > that does not start with a > char\n"
        cleaned = _clean(text)
        self.assertIn("this", cleaned)
        self.assertIn("does not start", cleaned)


class TestPerCultureExceptions(unittest.TestCase):
    """The Phase 2 friction reducer: per-country exception files.

    Live in regions/<region>/<country>/language_exceptions.txt and merge
    on top of the global tests/language_exceptions.txt. Contributors add
    country-specific proper nouns in their culture/<country> PR without
    needing a governance/* change to widen the global allowlist.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        # Clear the module-level cache so each test starts fresh; the
        # validator caches by country dir for efficiency, but tests
        # rebuild different dirs each time.
        validate_language._culture_exception_cache.clear()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _country(self, region: str, country: str) -> Path:
        p = self.root / "regions" / region / country
        p.mkdir(parents=True)
        return p

    def test_returns_empty_when_no_file(self):
        country = self._country("europe", "germany")
        culture = country / "culture_german_position.md"
        culture.write_text("# placeholder\n")
        self.assertEqual(_culture_exceptions_for(culture), set())

    def test_loads_country_specific_words(self):
        country = self._country("europe", "germany")
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
        exc = _culture_exceptions_for(culture)
        self.assertEqual(
            exc,
            {"vergangenheitsbewältigung", "erinnerungskultur", "bundeskanzler"},
        )

    def test_isolation_between_countries(self):
        """Germany's exception is not Denmark's; the validator must
        scope per-country lookups."""
        germany = self._country("europe", "germany")
        denmark = self._country("europe", "denmark")
        (germany / "language_exceptions.txt").write_text("Bundeskanzler\n")
        (denmark / "language_exceptions.txt").write_text("Janteloven\n")
        de_file = germany / "culture_german_position.md"
        de_file.write_text("# x\n")
        dk_file = denmark / "culture_danish_position.md"
        dk_file.write_text("# x\n")
        self.assertEqual(_culture_exceptions_for(de_file), {"bundeskanzler"})
        self.assertEqual(_culture_exceptions_for(dk_file), {"janteloven"})

    def test_country_dir_for_culture_file(self):
        country = self._country("europe", "germany")
        culture = country / "culture_german_position.md"
        culture.write_text("# x\n")
        self.assertEqual(_country_dir_for(culture), country.resolve())

    def test_country_dir_for_non_culture_path(self):
        outside = self.root / "tests" / "foo.py"
        outside.parent.mkdir(parents=True)
        outside.write_text("")
        self.assertIsNone(_country_dir_for(outside))


class TestExplain(unittest.TestCase):
    """The --explain diagnostic. We test the structural shape rather
    than the lingua output (which is non-deterministic across versions);
    structural checks catch the integration bugs."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unreadable_file_does_not_crash(self):
        ghost = self.root / "nonexistent.md"
        lines = explain(ghost)
        self.assertTrue(any("=== " in l for l in lines))
        self.assertTrue(any("could not read" in l for l in lines))

    def test_runs_without_lingua(self):
        """When lingua is absent, explain() prints a skip note rather
        than crashing -- mirrors validate()'s graceful degradation."""
        if validate_language._lingua_language_map() is not None:
            self.skipTest("lingua installed; this test exercises absence")
        culture = self.root / "regions" / "europe" / "germany" / "culture_x_position.md"
        culture.parent.mkdir(parents=True)
        culture.write_text("## Shown\n\nbody\n")
        lines = explain(culture)
        self.assertTrue(any("lingua not installed" in l for l in lines))


class TestParseExceptions(unittest.TestCase):
    """The shared parser used by both global and per-culture files."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "exc.txt"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_missing_file_returns_empty(self):
        self.assertEqual(_parse_exceptions(self.path), set())

    def test_strips_comments_and_blanks(self):
        self.path.write_text(
            "# a comment\n"
            "Foo\n"
            "\n"
            "  Bar  \n"
            "# trailing comment\n"
        )
        self.assertEqual(_parse_exceptions(self.path), {"foo", "bar"})


if __name__ == "__main__":
    unittest.main()
