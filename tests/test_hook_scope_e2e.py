"""End-to-end tests for the pre-commit hook scope guards.

Spins up a throwaway git repo, symlinks the real hook + branch_scope
module into it, stages synthetic files on different branch names, and
asserts the hook accepts/rejects as the contract requires.

This catches regressions where the *enforcement* breaks even if
classify_branch still classifies correctly (e.g. someone moves the
scope-check call below validation, or forgets to plumb the result
through).

Run: python3 -m unittest tests.test_hook_scope_e2e
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / ".githooks" / "pre-commit"
BRANCH_SCOPE_PATH = REPO_ROOT / "tests" / "branch_scope.py"
BAG_VALIDATOR_PATH = REPO_ROOT / "tests" / "validate_country_bag.py"
DENYLIST_PATH = REPO_ROOT / "data" / "hofstede_denylist.yaml"


def _minimal_valid_bag(country: str = "testland", language: str = "nl") -> str:
    """Synthesize a complete valid bag YAML for E2E test fixtures.

    The bag-validation pre-commit step rejects any bag that fails the
    schema/quality checks. Tests staging a bag must use a complete
    structure or stage something that the bag-pattern filter doesn't match.
    """
    def block(prefix):
        return "\n".join(f"      - {prefix}{i}" for i in range(1, 11))
    return f"""country: {country}
language: {language}
parent: null
hofstede_scores:
  PDI: 50
  IDV: 50
  UAI: 50
  MAS: 50
  LTO: 50
  IND: 50
denylist: []
bags:
  PDI:
    high:
{block('a')}
    low:
{block('b')}
  IDV:
    high:
{block('c')}
    low:
{block('d')}
  UAI:
    high:
{block('e')}
    low:
{block('f')}
  MAS:
    high:
{block('g')}
    low:
{block('h')}
  LTO:
    high:
{block('i')}
    low:
{block('j')}
  IND:
    high:
{block('k')}
    low:
{block('l')}
"""


def _run(*args: str, cwd: Path, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(args),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=check,
    )


def _make_repo(tmp_path: Path) -> Path:
    """Create a minimal repo with the real hook + branch_scope wired in."""
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / ".githooks").mkdir()
    (repo / "tests").mkdir()
    (repo / "data").mkdir()
    shutil.copy2(HOOK_PATH, repo / ".githooks" / "pre-commit")
    shutil.copy2(BRANCH_SCOPE_PATH, repo / "tests" / "branch_scope.py")
    if BAG_VALIDATOR_PATH.exists():
        shutil.copy2(BAG_VALIDATOR_PATH, repo / "tests" / "validate_country_bag.py")
    if DENYLIST_PATH.exists():
        shutil.copy2(DENYLIST_PATH, repo / "data" / "hofstede_denylist.yaml")
    os.chmod(repo / ".githooks" / "pre-commit", 0o755)

    # Seed a minimal regions/ topology so culture/<slug> resolution works.
    # branch_scope.culture_scope walks regions/ to map slugs to allowed
    # path prefixes; without these stubs every culture branch would fail
    # with "Unknown culture slug" before reaching the scope check.
    for country in ("netherlands", "denmark", "germany", "x"):
        (repo / "regions" / "europe" / country).mkdir(parents=True)
        (repo / "regions" / "europe" / country / ".gitkeep").write_text("")
    (repo / "regions" / "asia" / "japan").mkdir(parents=True)
    (repo / "regions" / "asia" / "japan" / ".gitkeep").write_text("")

    _run("git", "init", "-q", "-b", "main", cwd=repo, check=True)
    _run("git", "config", "user.email", "test@test.invalid", cwd=repo, check=True)
    _run("git", "config", "user.name", "test", cwd=repo, check=True)
    _run("git", "config", "commit.gpgsign", "false", cwd=repo, check=True)
    _run("git", "config", "tag.gpgSign", "false", cwd=repo, check=True)
    _run("git", "add", "-A", cwd=repo, check=True)
    _run("git", "commit", "-q", "-m", "init", cwd=repo, check=True)
    return repo


def _stage(repo: Path, rel: str, content: str = "x\n") -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    _run("git", "add", "--", rel, cwd=repo, check=True)


def _checkout(repo: Path, branch: str) -> None:
    _run("git", "checkout", "-q", "-b", branch, cwd=repo, check=True)


def _run_hook(repo: Path) -> subprocess.CompletedProcess:
    """Invoke the hook the same way git would: from the repo root."""
    return _run(
        sys.executable, str(repo / ".githooks" / "pre-commit"),
        cwd=repo,
    )


class TestHookScopeEnforcement(unittest.TestCase):
    """Each test gets its own fresh repo via setUp / tearDown."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = _make_repo(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_main_blocks_any_commit(self):
        """Hook init left us on `main`; any staged change must be rejected."""
        _stage(self.repo, "tests/foo.py")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Direct commits to main are forbidden", result.stdout)

    def test_culture_branch_allows_regions(self):
        _checkout(self.repo, "culture/netherlands")
        _stage(self.repo, "regions/europe/netherlands/foo.txt")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue((self.repo / ".validation-stamp").exists())

    def test_culture_branch_allows_safe_metadata(self):
        _checkout(self.repo, "culture/x")
        _stage(self.repo, ".gitignore", "*.bak\n")
        _stage(self.repo, "regions/europe/x/foo.txt")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_culture_branch_allows_lock_index_alongside_bag(self):
        _checkout(self.repo, "culture/netherlands")
        _stage(
            self.repo,
            "regions/europe/netherlands/hofstede_bag.yaml",
            _minimal_valid_bag(country="netherlands", language="nl"),
        )
        _stage(self.repo, "data/hofstede_bag_locks.yaml", "locks: {}\n")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_culture_branch_blocks_malformed_bag(self):
        _checkout(self.repo, "culture/netherlands")
        _stage(
            self.repo,
            "regions/europe/netherlands/hofstede_bag.yaml",
            "country: netherlands\nlanguage: nl\n",
        )
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("BAG VALIDATION FAILED", result.stdout)
        self.assertIn("missing required field", result.stdout)

    def test_culture_branch_blocks_infra_changes(self):
        _checkout(self.repo, "culture/netherlands")
        _stage(self.repo, "tests/foo.py")
        _stage(self.repo, ".github/copilot-instructions.md", "# tampered\n")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Culture branch out of scope", result.stdout)
        self.assertIn("regions/europe/netherlands/", result.stdout)
        self.assertIn("tests/foo.py", result.stdout)
        self.assertIn(".github/copilot-instructions.md", result.stdout)

    def test_country_branch_blocks_other_country(self):
        """culture/netherlands must not be able to edit Denmark — even
        though Denmark is the same region. Per-country protection."""
        _checkout(self.repo, "culture/netherlands")
        _stage(self.repo, "regions/europe/denmark/culture_danish_position.md")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Culture branch out of scope", result.stdout)
        self.assertIn("regions/europe/netherlands/", result.stdout)
        self.assertIn(
            "regions/europe/denmark/culture_danish_position.md",
            result.stdout,
        )

    def test_country_branch_blocks_other_region(self):
        """culture/netherlands must not be able to edit Japan (different region)."""
        _checkout(self.repo, "culture/netherlands")
        _stage(self.repo, "regions/asia/japan/culture_japanese_position.md")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Culture branch out of scope", result.stdout)

    def test_region_branch_allows_multi_country(self):
        """culture/europe is a region-level scope and may touch any
        country within europe in a single commit."""
        _checkout(self.repo, "culture/europe")
        _stage(self.repo, "regions/europe/germany/foo.txt")
        _stage(self.repo, "regions/europe/denmark/foo.txt")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_region_branch_blocks_other_region(self):
        _checkout(self.repo, "culture/europe")
        _stage(self.repo, "regions/asia/japan/foo.txt")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Culture branch out of scope", result.stdout)
        self.assertIn("regions/europe/", result.stdout)

    def test_world_branch_allows_anything_in_regions(self):
        """culture/staging is the integration target — by design it may
        touch any country/region in a single commit."""
        _checkout(self.repo, "culture/staging")
        _stage(self.repo, "regions/europe/germany/foo.txt")
        _stage(self.repo, "regions/asia/japan/foo.txt")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_release_branch_allows_anything_in_regions(self):
        _checkout(self.repo, "culture/release")
        _stage(self.repo, "regions/europe/germany/foo.txt")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_unknown_culture_slug_rejected(self):
        """culture/<slug> where slug isn't a country, region, or world
        target must be rejected outright — not silently widened to all
        of regions/."""
        _checkout(self.repo, "culture/atlantis")
        _stage(self.repo, "regions/europe/germany/foo.txt")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Unknown culture slug", result.stdout)
        self.assertIn("culture/atlantis", result.stdout)

    def test_other_branch_allows_infra(self):
        _checkout(self.repo, "chore/x")
        _stage(self.repo, "tests/foo.py")
        _stage(self.repo, ".github/workflows/foo.yml")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_other_branch_blocks_regions(self):
        """The symmetric guard added in this PR. Without it, a chore/*
        branch could silently rewrite culture content."""
        _checkout(self.repo, "chore/x")
        _stage(self.repo, "regions/europe/germany/culture_german_position.md")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Non-culture branch cannot modify regions/", result.stdout)
        self.assertIn(
            "regions/europe/germany/culture_german_position.md", result.stdout,
        )

    def test_other_branch_blocks_mixed_diff(self):
        """A chore branch staging both infra AND regions/ is still rejected
        (the regions/ change is what makes it unsafe)."""
        _checkout(self.repo, "fix/x")
        _stage(self.repo, "tests/foo.py")
        _stage(self.repo, "regions/europe/x/foo.md")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("regions/europe/x/foo.md", result.stdout)

    def test_slash_form_classified_as_other(self):
        """Worked example in the original doc was `feat/culture/netherlands`
        (slash). That bypassed the unanchored startswith() check. With the
        anchored regex it classifies as `other`, so a regions/ change on
        the slash form is now correctly rejected."""
        _checkout(self.repo, "feat/culture/netherlands")
        _stage(self.repo, "regions/europe/netherlands/foo.md")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Non-culture branch cannot modify regions/", result.stdout)

    def test_typo_plural_classified_as_other(self):
        _checkout(self.repo, "feat/cultures-netherlands")
        _stage(self.repo, "regions/europe/netherlands/foo.md")
        result = _run_hook(self.repo)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Non-culture branch cannot modify regions/", result.stdout)


if __name__ == "__main__":
    unittest.main()
