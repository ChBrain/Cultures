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
    GOVERNANCE_DIR_PREFIXES,
    GOVERNANCE_GLOB_PATTERNS,
    SAFE_PATTERNS,
    WORLD_SLUGS,
    check_scope,
    classify_branch,
    culture_scope,
    is_governance_path,
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

    def test_governance_happy_paths(self):
        for name in [
            "governance/harden-validators",
            "governance/ci-mirror",
            "governance/x",
            "governance/a1",
            "governance/x_y-z",
        ]:
            with self.subTest(branch=name):
                self.assertEqual(classify_branch(name), "governance")

    def test_governance_near_misses_classify_as_other(self):
        """Same bypass-surface hygiene as culture: typos must NOT be
        'governance' — they fall through to 'other' which is the safer
        default (blocked from regions/ and governance paths)."""
        for name in [
            "governance",
            "governance/",
            "governance/X",
            "governance/Foo",
            " governance/x",
            "governance/x ",
            "governance-x",
            "governances/x",
            "gov/x",
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

    def test_other_allows_non_regions_non_governance(self):
        """`other` may touch anything that isn't regions/ AND isn't
        governance. Generic docs, ARCHITECTURE.md, etc. stay open."""
        ok, unsafe = check_scope("other", [
            ".github/copilot-instructions.md",  # not under .github/workflows/
            "ARCHITECTURE.md",
            "README.md",
            "scripts/audit-germany.py",  # not validate*, not setup-hooks
            "data/hofstede_bag_locks.yaml",  # SAFE_PATTERNS carve-out
        ])
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_other_blocks_governance_paths(self):
        """The tightening: chore/*, fix/*, feat/* must NOT touch governance
        paths. Previously they could silently weaken validators/hooks."""
        ok, unsafe = check_scope("other", [
            ".githooks/pre-commit",
            "tests/branch_scope.py",
            "tests/validate_general.py",
            "tests/test_branch_scope.py",
            ".github/workflows/validate.yml",
            "scripts/validate.py",
            "data/hofstede_keywords.py",
            "data/hofstede_scores.json",
            "ARCHITECTURE.md",  # this one is OK and must NOT appear in unsafe
        ])
        self.assertFalse(ok)
        self.assertIn(".githooks/pre-commit", unsafe)
        self.assertIn("tests/branch_scope.py", unsafe)
        self.assertIn("tests/validate_general.py", unsafe)
        self.assertIn("tests/test_branch_scope.py", unsafe)
        self.assertIn(".github/workflows/validate.yml", unsafe)
        self.assertIn("scripts/validate.py", unsafe)
        self.assertIn("data/hofstede_keywords.py", unsafe)
        self.assertIn("data/hofstede_scores.json", unsafe)
        self.assertNotIn("ARCHITECTURE.md", unsafe)

    def test_other_blocks_regions(self):
        ok, unsafe = check_scope("other", [
            "regions/europe/germany/culture_german_position.md",
            "scripts/audit-germany.py",
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

    def test_governance_branch_allows_governance_paths(self):
        ok, unsafe = check_scope("governance", [
            ".githooks/pre-commit",
            ".github/workflows/validate.yml",
            "tests/branch_scope.py",
            "tests/test_branch_scope.py",
            "tests/validate_culture_completeness.py",
            "scripts/validate.py",
            "data/hofstede_keywords.py",
            "data/hofstede_scores.json",
            ".validation-stamp",
        ], "governance/harden-validators")
        self.assertTrue(ok)
        self.assertEqual(unsafe, [])

    def test_governance_branch_blocks_regions(self):
        """Governance is for rules, not data. Touching culture content
        must be done via culture/<slug>."""
        ok, unsafe = check_scope("governance", [
            "tests/branch_scope.py",
            "regions/europe/germany/culture_german_position.md",
        ], "governance/x")
        self.assertFalse(ok)
        self.assertEqual(
            unsafe,
            ["regions/europe/germany/culture_german_position.md"],
        )

    def test_governance_branch_blocks_non_governance_infra(self):
        """ARCHITECTURE.md, audit scripts, etc. aren't governance —
        they belong on chore/* branches. Keeps governance PRs focused."""
        ok, unsafe = check_scope("governance", [
            "tests/branch_scope.py",
            "ARCHITECTURE.md",
            "scripts/audit-germany.py",
        ], "governance/x")
        self.assertFalse(ok)
        self.assertIn("ARCHITECTURE.md", unsafe)
        self.assertIn("scripts/audit-germany.py", unsafe)
        self.assertNotIn("tests/branch_scope.py", unsafe)

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


class TestIsGovernancePath(unittest.TestCase):
    """Pin which paths count as governance.

    Removing an entry from this list widens the bypass surface — an
    LLM could then weaken that file from a chore/* branch. Each removal
    should be a deliberate, reviewed change.
    """

    def test_subtrees(self):
        for path in [
            ".githooks/pre-commit",
            ".githooks/sub/anything.sh",
            ".github/workflows/validate.yml",
            ".github/workflows/sub/anything.yml",
        ]:
            with self.subTest(path=path):
                self.assertTrue(is_governance_path(path))

    def test_glob_files(self):
        for path in [
            "tests/branch_scope.py",
            "tests/test_branch_scope.py",
            "tests/test_hook_scope_e2e.py",
            "tests/test_hofstede_alignment.py",
            "tests/validate_general.py",
            "tests/validate_culture_completeness.py",
            "tests/validate_hofstede_derived.py",
            "tests/validate_country_bag.py",
            "tests/requirements.txt",
            "tests/language_exceptions.txt",
            "scripts/validate.py",
            "scripts/validate_general.py",
            "scripts/setup-hooks.sh",
            "scripts/setup-hooks.bat",
            "data/hofstede_denylist.yaml",
            "data/hofstede_keywords.py",
            "data/hofstede_scores.json",
            "data/hofstede_bag_loader.py",
            "data/language_policy.yaml",
        ]:
            with self.subTest(path=path):
                self.assertTrue(is_governance_path(path))

    def test_non_governance(self):
        """Things that look adjacent but must NOT be governance, because
        chore/* legitimately needs to touch them."""
        for path in [
            "ARCHITECTURE.md",
            "README.md",
            ".github/copilot-instructions.md",  # docs, not workflows/
            ".github/dependabot.yml",            # not under workflows/
            "scripts/audit-germany.py",
            "scripts/normalize-germany.py",
            "scripts/deploy_culture.py",
            "scripts/scaffold_country.py",
            "scripts/findings.py",
            "scripts/prose_review.py",
            "scripts/audit_readme_bands.py",
            "tests/PLAN.md",
            "tests/README.md",
            "tests/findings.py",                  # not test_* and not validate_*
            "data/hofstede_bag_locks.yaml",       # SAFE_PATTERNS carve-out
            "regions/europe/germany/culture_german_position.md",
        ]:
            with self.subTest(path=path):
                self.assertFalse(is_governance_path(path))

    def test_dir_prefixes_set_locked(self):
        """Adding a prefix widens what governance branches may touch and
        what other branches are blocked from — review carefully."""
        self.assertEqual(
            GOVERNANCE_DIR_PREFIXES,
            (".githooks/", ".github/workflows/"),
        )

    def test_glob_patterns_set_locked(self):
        """Same lock as DIR_PREFIXES, but for the file-level globs. Drift
        here is the highest-value bypass — if you remove a validator
        pattern, that validator becomes editable from chore/*."""
        self.assertEqual(
            GOVERNANCE_GLOB_PATTERNS,
            (
                "tests/branch_scope.py",
                "tests/test_*.py",
                "tests/validate_*.py",
                "tests/requirements.txt",
                "tests/language_exceptions.txt",
                "scripts/validate.py",
                "scripts/validate_general.py",
                "scripts/setup-hooks.sh",
                "scripts/setup-hooks.bat",
                "data/hofstede_denylist.yaml",
                "data/hofstede_keywords.py",
                "data/hofstede_scores.json",
                "data/hofstede_bag_loader.py",
                "data/language_policy.yaml",
            ),
        )


if __name__ == "__main__":
    unittest.main()
