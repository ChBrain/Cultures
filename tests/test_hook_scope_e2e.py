"""End-to-end tests for the pre-commit hook scope guards — pytest version.

Spins up a throwaway git repo, wires in the real hook + branch_scope module,
stages synthetic files on different branch names, and asserts the hook
accepts/rejects as the contract requires.

Rewritten from unittest to pytest (Loop F). Logic unchanged from the original.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / ".githooks" / "pre-commit"
BRANCH_SCOPE_PATH = REPO_ROOT / "tests" / "branch_scope.py"
BAG_VALIDATOR_PATH = REPO_ROOT / "tests" / "validate_country_bag.py"
DENYLIST_PATH = REPO_ROOT / "data" / "hofstede_denylist.yaml"


def _minimal_valid_bag(country: str = "testland", language: str = "nl") -> str:
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
    return _run(sys.executable, str(repo / ".githooks" / "pre-commit"), cwd=repo)


@pytest.fixture
def repo(tmp_path):
    return _make_repo(tmp_path)


# ---------------------------------------------------------------------------
# Hook enforcement tests
# ---------------------------------------------------------------------------

def test_main_blocks_any_commit(repo):
    _stage(repo, "tests/foo.py")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Direct commits to main are forbidden" in result.stdout


def test_culture_branch_allows_regions(repo):
    _checkout(repo, "culture/netherlands")
    _stage(repo, "regions/europe/netherlands/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 0
    assert (repo / ".validation-stamp").exists()


def test_culture_branch_allows_safe_metadata(repo):
    _checkout(repo, "culture/x")
    _stage(repo, ".gitignore", "*.bak\n")
    _stage(repo, "regions/europe/x/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 0


def test_culture_branch_allows_lock_index_alongside_bag(repo):
    _checkout(repo, "culture/netherlands")
    _stage(repo, "regions/europe/netherlands/hofstede_bag.yaml",
           _minimal_valid_bag(country="netherlands", language="nl"))
    _stage(repo, "data/hofstede_bag_locks.yaml", "locks: {}\n")
    result = _run_hook(repo)
    assert result.returncode == 0


def test_culture_branch_blocks_malformed_bag(repo):
    _checkout(repo, "culture/netherlands")
    _stage(repo, "regions/europe/netherlands/hofstede_bag.yaml",
           "country: netherlands\nlanguage: nl\n")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "BAG VALIDATION FAILED" in result.stdout
    assert "missing required field" in result.stdout


def test_culture_branch_blocks_infra_changes(repo):
    _checkout(repo, "culture/netherlands")
    _stage(repo, "tests/foo.py")
    _stage(repo, ".github/copilot-instructions.md", "# tampered\n")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Culture branch out of scope" in result.stdout
    assert "regions/europe/netherlands/" in result.stdout
    assert "tests/foo.py" in result.stdout
    assert ".github/copilot-instructions.md" in result.stdout


def test_country_branch_blocks_other_country(repo):
    _checkout(repo, "culture/netherlands")
    _stage(repo, "regions/europe/denmark/culture_danish_position.md")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Culture branch out of scope" in result.stdout
    assert "regions/europe/netherlands/" in result.stdout
    assert "regions/europe/denmark/culture_danish_position.md" in result.stdout


def test_country_branch_blocks_other_region(repo):
    _checkout(repo, "culture/netherlands")
    _stage(repo, "regions/asia/japan/culture_japanese_position.md")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Culture branch out of scope" in result.stdout


def test_region_branch_allows_multi_country(repo):
    _checkout(repo, "culture/europe")
    _stage(repo, "regions/europe/germany/foo.txt")
    _stage(repo, "regions/europe/denmark/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 0


def test_region_branch_blocks_other_region(repo):
    _checkout(repo, "culture/europe")
    _stage(repo, "regions/asia/japan/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Culture branch out of scope" in result.stdout
    assert "regions/europe/" in result.stdout


def test_world_branch_allows_anything_in_regions(repo):
    _checkout(repo, "culture/release")
    _stage(repo, "regions/europe/germany/foo.txt")
    _stage(repo, "regions/asia/japan/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 0


def test_release_branch_allows_anything_in_regions(repo):
    _checkout(repo, "culture/release")
    _stage(repo, "regions/europe/germany/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 0


def test_unknown_culture_slug_rejected(repo):
    _checkout(repo, "culture/atlantis")
    _stage(repo, "regions/europe/germany/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Unknown culture slug" in result.stdout
    assert "culture/atlantis" in result.stdout


def test_other_branch_allows_non_governance_infra(repo):
    _checkout(repo, "chore/x")
    _stage(repo, "tests/foo.py")
    _stage(repo, "ARCHITECTURE.md")
    _stage(repo, ".github/copilot-instructions.md")
    result = _run_hook(repo)
    assert result.returncode == 0


def test_other_branch_blocks_governance_paths(repo):
    _checkout(repo, "chore/sneaky")
    _stage(repo, ".github/workflows/validate.yml", "name: x\n")
    _stage(repo, "data/hofstede_scores.json", "{}\n")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "out of scope" in result.stdout
    assert ".github/workflows/validate.yml" in result.stdout
    assert "data/hofstede_scores.json" in result.stdout
    assert "governance/<name>" in result.stdout


def test_other_branch_blocks_regions(repo):
    _checkout(repo, "chore/x")
    _stage(repo, "regions/europe/germany/culture_german_position.md")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "out of scope" in result.stdout
    assert "regions/europe/germany/culture_german_position.md" in result.stdout


def test_other_branch_blocks_mixed_diff(repo):
    _checkout(repo, "fix/x")
    _stage(repo, "tests/foo.py")
    _stage(repo, "regions/europe/x/foo.md")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "regions/europe/x/foo.md" in result.stdout


def test_slash_form_classified_as_other(repo):
    """feat/culture/netherlands (slash form) must be rejected for regions/ edits."""
    _checkout(repo, "feat/culture/netherlands")
    _stage(repo, "regions/europe/netherlands/foo.md")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "out of scope" in result.stdout
    assert "regions/europe/netherlands/foo.md" in result.stdout


def test_typo_plural_classified_as_other(repo):
    _checkout(repo, "feat/cultures-netherlands")
    _stage(repo, "regions/europe/netherlands/foo.md")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "out of scope" in result.stdout


def test_governance_branch_allows_governance_paths(repo):
    _checkout(repo, "governance/harden-validators")
    _stage(repo, ".github/workflows/validate.yml", "name: x\n")
    _stage(repo, "data/hofstede_scores.json", "{}\n")
    result = _run_hook(repo)
    assert result.returncode == 0


def test_governance_branch_blocks_regions(repo):
    _checkout(repo, "governance/x")
    _stage(repo, ".github/workflows/validate.yml", "name: x\n")
    _stage(repo, "regions/europe/germany/foo.txt")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Governance branch out of scope" in result.stdout
    assert "regions/europe/germany/foo.txt" in result.stdout


def test_governance_branch_blocks_non_governance_infra(repo):
    _checkout(repo, "governance/x")
    _stage(repo, ".github/workflows/validate.yml", "name: x\n")
    _stage(repo, "ARCHITECTURE.md", "# arch\n")
    result = _run_hook(repo)
    assert result.returncode == 1
    assert "Governance branch out of scope" in result.stdout
    assert "ARCHITECTURE.md" in result.stdout
