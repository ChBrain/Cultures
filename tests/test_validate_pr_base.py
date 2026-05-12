"""Unit tests for tests/validate_pr_base.py.

Pins the integration flow:

  culture/<country|region>          -> culture/release
  culture/release, culture/staging  -> main
  governance/<name>                 -> main
  chore/*, fix/*, feat/*, other     -> main

Any change to allowed_bases here is a contract change; the matching
edit to .github/workflows/pr-gate.yml or branch_scope.classify_branch
should land in the same PR.

Run: python3 -m unittest tests.test_validate_pr_base
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from validate_pr_base import allowed_bases  # noqa: E402


class TestAllowedBases(unittest.TestCase):
    def test_culture_country_only_to_release(self):
        for head in [
            "culture/germany",
            "culture/denmark",
            "culture/netherlands",
            "culture/burkina_faso",
        ]:
            with self.subTest(head=head):
                self.assertEqual(allowed_bases(head), {"culture/release"})

    def test_culture_region_only_to_release(self):
        for head in [
            "culture/europe",
            "culture/asia",
            "culture/africa",
            "culture/americas",
            "culture/oceania",
        ]:
            with self.subTest(head=head):
                self.assertEqual(allowed_bases(head), {"culture/release"})

    def test_culture_world_slugs_to_main(self):
        """culture/release and culture/staging are the integration
        targets — they PR upward into main, not back into themselves."""
        self.assertEqual(allowed_bases("culture/release"), {"main"})
        self.assertEqual(allowed_bases("culture/staging"), {"main"})

    def test_governance_to_main(self):
        for head in [
            "governance/ci-pr-gate",
            "governance/harden-validators",
            "governance/x",
        ]:
            with self.subTest(head=head):
                self.assertEqual(allowed_bases(head), {"main"})

    def test_other_kinds_to_main(self):
        for head in [
            "chore/refactor",
            "fix/typo",
            "feat/new-thing",
            "claude/review-foo",
            "random-branch",
        ]:
            with self.subTest(head=head):
                self.assertEqual(allowed_bases(head), {"main"})

    def test_main_is_not_a_valid_head(self):
        """A PR with head=main has nowhere legitimate to go; empty set
        signals the head itself is invalid."""
        self.assertEqual(allowed_bases("main"), set())


class TestValidatePrBaseCli(unittest.TestCase):
    """Smoke-test the CLI wrapper. The interesting logic is allowed_bases;
    these tests just verify the CLI plumbs args and exit codes correctly."""

    def _run(self, head: str, base: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HERE / "validate_pr_base.py"), head, base],
            capture_output=True, text=True, check=False,
        )

    def test_allowed_pair_exits_zero(self):
        result = self._run("culture/germany", "culture/release")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_disallowed_pair_exits_one(self):
        result = self._run("culture/germany", "main")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not allowed", result.stdout)
        self.assertIn("culture/release", result.stdout)

    def test_main_as_head_exits_one(self):
        result = self._run("main", "main")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a valid PR head", result.stdout)

    def test_missing_args_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(HERE / "validate_pr_base.py")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
