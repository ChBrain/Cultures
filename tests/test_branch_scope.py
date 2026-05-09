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
sys.path.insert(0, str(HERE))

from branch_scope import (  # noqa: E402
    SAFE_PATTERNS,
    check_scope,
    classify_branch,
)


class TestClassifyBranch(unittest.TestCase):
    def test_main(self):
        self.assertEqual(classify_branch("main"), "main")

    def test_culture_happy_paths(self):
        for name in [
            "feat/culture-netherlands",
            "feat/culture-denmark",
            "feat/culture-germany",
            "feat/culture-x",
            "feat/culture-x_y-z",
            "feat/culture-burkina_faso",
            "feat/culture-a1",
        ]:
            with self.subTest(branch=name):
                self.assertEqual(classify_branch(name), "culture")

    def test_near_misses_classify_as_other(self):
        """The bypass surface — every one of these must NOT be 'culture'."""
        for name in [
            "feat/culture/netherlands",  # slash form (the original PR #27 doc bug)
            "feat/cultures-x",           # typo plural
            "feat/culture",              # missing name
            "feat/culture-",             # missing name char
            "feat/Culture-x",            # uppercase
            "feat/culture-X",            # uppercase in name
            "feat/CULTURE-x",            # all caps prefix
            " feat/culture-x",           # leading whitespace
            "feat/culture-x ",           # trailing whitespace
            "feat/culture-x.y",          # disallowed punctuation
        ]:
            with self.subTest(branch=name):
                self.assertEqual(classify_branch(name), "other")

    def test_other_prefixes(self):
        for name in [
            "chore/x",
            "fix/x",
            "feat/foo",
            "claude/review-foo",
            "release/v1",
            "develop",
        ]:
            with self.subTest(branch=name):
                self.assertEqual(classify_branch(name), "other")


class TestCheckScope(unittest.TestCase):
    def test_culture_allows_regions_and_safe(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            "regions/europe/germany/README.md",
            ".validation-stamp",
            ".gitignore",
            ".bump-type",
            ".editorconfig",
        ])
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_culture_blocks_non_regions(self):
        ok, unsafe = check_scope("culture", [
            "regions/europe/germany/culture_german_position.md",
            ".githooks/pre-commit",
            "tests/validate_general.py",
            "ARCHITECTURE.md",
        ])
        self.assertFalse(ok)
        self.assertIn(".githooks/pre-commit", unsafe)
        self.assertIn("tests/validate_general.py", unsafe)
        self.assertIn("ARCHITECTURE.md", unsafe)
        self.assertNotIn(
            "regions/europe/germany/culture_german_position.md", unsafe,
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
        ok, unsafe = check_scope("culture", ["subdir/.gitignore"])
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
        and should be a deliberate, reviewed edit — not a drive-by addition."""
        self.assertEqual(
            SAFE_PATTERNS,
            frozenset({
                ".validation-stamp",
                ".bump-type",
                ".gitignore",
                ".editorconfig",
            }),
        )


if __name__ == "__main__":
    unittest.main()
