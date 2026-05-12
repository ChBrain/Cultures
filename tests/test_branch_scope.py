"""Unit tests for tests/branch_scope.py.

The classification + scope contract is enforced by the pre-commit hook
and (planned) by a CI job. These tests pin the rules so a future hook
edit that loosens them fails CI before it can land.

Run: python3 -m unittest tests.test_branch_scope
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from branch_scope import (  # noqa: E402
    SAFE_PATTERNS,
    WORLD_SLUGS,
    check_scope,
    classify_branch,
    culture_scope,
)


class TestClassifyBranch(unittest.TestCase):
    def test_main(self):
        self.assertEqual(classify_branch("main"), "main")

    def test_culture_happy_paths(self):
        for name in [
            "culture/netherlands",
            "culture/denmark",
            "culture/germany",
            "culture/x",
            "culture/x_y-z",
            "culture/burkina_faso",
            "culture/staging",
            "culture/a1",
        ]:
            with self.subTest(branch=name):
                self.assertEqual(classify_branch(name), "culture")

    def test_near_misses_classify_as_other(self):
        """The bypass surface — every one of these must NOT be 'culture'."""
        for name in [
            "feat/culture-netherlands",
            "feat/culture-denmark",
            "culture/Culture-denmark",
            "culture-netherlands",
            "cultures/netherlands",
            "culture",
            "culture/",
            "culture/X",
            "culture/STAGING",
            " culture/denmark",
            "culture/denmark ",
            "culture/denmark.md",
        ]:
            with self.subTest(branch=name):
                self.assertEqual(classify_branch(name), "other")

    def test_other_prefixes(self):
        for name in [
            "chore/x",
            "fix/x",
            "feat/foo",
            "feat/culture-old",
            "claude/review-foo",
            "release/v1",
            "develop",
        ]:
            with self.subTest(branch=name):
                self.assertEqual(classify_branch(name), "other")


class TestCultureScope(unittest.TestCase):
    """Slug resolution against the real regions/ tree.

    These tests depend on actual regions/europe/{germany,denmark,...}
    directories existing in this repo. If those move, update the
    expected prefixes here.
    """

    def test_country_slug_resolves_to_country_subtree(self):
        self.assertEqual(
            culture_scope("culture/germany"),
            "regions/europe/germany/",
        )
        self.assertEqual(
            culture_scope("culture/denmark"),
            "regions/europe/denmark/",
        )
        self.assertEqual(
            culture_scope("culture/netherlands"),
            "regions/europe/netherlands/",
        )
        self.assertEqual(
            culture_scope("culture/poland"),
            "regions/europe/poland/",
        )

    def test_region_slug_resolves_to_region_subtree(self):
        for region in ["europe", "africa", "americas", "asia", "oceania"]:
            with self.subTest(region=region):
                self.assertEqual(
                    culture_scope(f"culture/{region}"),
                    f"regions/{region}/",
                )

    def test_world_slugs_resolve_to_regions_root(self):
        self.assertEqual(culture_scope("culture/staging"), "regions/")
        self.assertEqual(culture_scope("culture/release"), "regions/")

    def test_unknown_slug_returns_none(self):
        for name in [
            "culture/atlantis",
            "culture/mars",
            "culture/europe_west",
            "culture/germany_extra",
        ]:
            with self.subTest(branch=name):
                self.assertIsNone(culture_scope(name))

    def test_non_culture_branch_returns_none(self):
        for name in ["main", "chore/x", "feat/foo", "culture/X"]:
            with self.subTest(branch=name):
                self.assertIsNone(culture_scope(name))


class TestCheckScope(unittest.TestCase):
    def test_country_branch_allows_own_country(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/europe/germany/README.md",
            "regions/europe/germany/hofstede_bag.yaml",
            ".validation-stamp",
            ".gitignore",
            ".bump-type",
            ".editorconfig",
            "data/hofstede_bag_locks.yaml",
        ], "culture/germany")
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_country_branch_blocks_other_country(self):
        """A culture/germany branch must not be able to edit Denmark."""
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/europe/denmark/culture_danish_position.md",
        ], "culture/germany")
        self.assertFalse(ok)
        self.assertEqual(
            unsafe,
            ["regions/europe/denmark/culture_danish_position.md"],
        )

    def test_country_branch_blocks_other_region(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/asia/japan/culture_japanese_position.md",
        ], "culture/germany")
        self.assertFalse(ok)
        self.assertIn(
            "regions/asia/japan/culture_japanese_position.md",
            unsafe,
        )

    def test_region_branch_allows_any_country_in_region(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/europe/denmark/culture_danish_position.md",
            "regions/europe/netherlands/culture_dutch_position.md",
        ], "culture/europe")
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_region_branch_blocks_other_region(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/asia/japan/culture_japanese_position.md",
        ], "culture/europe")
        self.assertFalse(ok)
        self.assertEqual(
            unsafe,
            ["regions/asia/japan/culture_japanese_position.md"],
        )

    def test_world_branch_allows_anything_in_regions(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/asia/japan/culture_japanese_position.md",
            "regions/africa/kenya/culture_kenyan_position.md",
        ], "culture/staging")
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_release_branch_allows_anything_in_regions(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/asia/japan/culture_japanese_position.md",
        ], "culture/release")
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_culture_allows_lock_index_alongside_bag(self):
        """Migration PRs update the lock index in the same commit as the
        new bag YAML. Strategy v2 explicit carve-out — must hold even
        under the tightest (country-level) scope."""
        ok, unsafe = check_scope("culture", [
            "regions/europe/netherlands/hofstede_bag.yaml",
            "regions/europe/netherlands/hofstede_decisions.md",
            "data/hofstede_bag_locks.yaml",
        ], "culture/netherlands")
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_culture_blocks_non_regions(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            ".githooks/pre-commit",
            "tests/validate_general.py",
            "ARCHITECTURE.md",
        ], "culture/germany")
        self.assertFalse(ok)
        self.assertIn(".githooks/pre-commit", unsafe)
        self.assertIn("tests/validate_general.py", unsafe)
        self.assertIn("ARCHITECTURE.md", unsafe)
        self.assertNotIn(
            "regions/europe/germany/culture_german_position.md", unsafe,
        )

    def test_unknown_culture_slug_blocks_everything(self):
        """A culture branch whose slug doesn't resolve must not silently
        widen scope to regions/**. Every non-safe file is unsafe."""
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            ".validation-stamp",
        ], "culture/atlantis")
        self.assertFalse(ok)
        self.assertEqual(
            unsafe,
            ["regions/europe/germany/culture_german_position.md"],
        )

    def test_missing_branch_name_blocks_everything(self):
        """Caller that doesn't pass branch_name on a 'culture' kind gets
        a blanket rejection instead of silent widening."""
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
        ])
        self.assertFalse(ok)
        self.assertEqual(
            unsafe,
            ["regions/europe/germany/culture_german_position.md"],
        )

    def test_other_allows_non_regions(self):
        ok, unsafe = check_scope("other", [
            ".githooks/pre-commit",
            "tests/branch_scope.py",
            ".github/copilot-instructions.md",
            "ARCHITECTURE.md",
            "data/hofstede_keywords.py",
        ])
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_other_blocks_regions(self):
        ok, unsafe = check_scope("other", [
            "regions/europe/germany/culture_german_position.md",
            "tests/validate_general.py",
        ])
        self.assertFalse(ok)
        self.assertEqual(
            unsafe,
            ["regions/europe/germany/culture_german_position.md"],
        )

    def test_other_blocks_regions_metadata_too(self):
        """A README.md inside regions/ is still culture territory on an
        infra branch — SAFE_PATTERNS does not bypass the regions/ rule."""
        ok, unsafe = check_scope("other", [
            "regions/europe/germany/README.md",
        ])
        self.assertFalse(ok)
        self.assertEqual(unsafe, ["regions/europe/germany/README.md"])

    def test_safe_patterns_only_match_at_root(self):
        """`subdir/.gitignore` is not in SAFE_PATTERNS (exact-string match),
        so a culture branch must NOT silently allow it outside regions/."""
        ok, unsafe = check_scope(
            "culture", ["subdir/.gitignore"], "culture/germany",
        )
        self.assertFalse(ok)
        self.assertEqual(unsafe, ["subdir/.gitignore"])

    def test_main_is_noop(self):
        """`main` is gated by the no-commits-on-main rule, not by scope.
        check_scope('main', ...) must not falsely flag scope violations."""
        ok, unsafe = check_scope("main", [
            "regions/europe/germany/culture_german_position.md",
            ".githooks/pre-commit",
        ])
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_safe_patterns_set_locked(self):
        """Pin the safe-pattern set. Any change here is a contract change
        and should be a deliberate, reviewed edit — not a drive-by addition.
        """
        self.assertEqual(
            SAFE_PATTERNS,
            frozenset({
                ".validation-stamp",
                ".bump-type",
                ".gitignore",
                ".editorconfig",
                "data/hofstede_bag_locks.yaml",
            }),
        )

    def test_world_slugs_set_locked(self):
        """Pin the world-level slug set. These are the only culture
        branches that may touch any country — adding to this set widens
        scope and should be a reviewed change."""
        self.assertEqual(WORLD_SLUGS, frozenset({"staging", "release"}))


if __name__ == "__main__":
    unittest.main()
