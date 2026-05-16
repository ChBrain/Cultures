"""Unit tests for tests/branch_scope.py - pins classify/scope/governance contracts.

Rewritten from unittest to pytest (Loop F). Logic unchanged from the original.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
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

# ---------------------------------------------------------------------------
# classify_branch
# ---------------------------------------------------------------------------

def test_classify_main():
    assert classify_branch("main") == "main"


@pytest.mark.parametrize("branch", [
    "culture/netherlands",
    "culture/denmark",
    "culture/germany",
    "culture/x",
    "culture/x_y-z",
    "culture/burkina_faso",
    "culture/a1",
    "culture/rollout-v1.2",
    "culture/fix-v0.1.5",
])
def test_classify_culture(branch):
    assert classify_branch(branch) == "culture"


@pytest.mark.parametrize("branch", [
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
])
def test_classify_culture_near_misses_are_other(branch):
    """The bypass surface - every one of these must NOT be 'culture'."""
    assert classify_branch(branch) == "other"


@pytest.mark.parametrize("branch", [
    "chore/x",
    "fix/x",
    "feat/foo",
    "feat/culture-old",
    "claude/review-foo",
    "release/v1",
    "develop",
])
def test_classify_other_prefixes(branch):
    assert classify_branch(branch) == "other"


@pytest.mark.parametrize("branch", [
    "governance/harden-validators",
    "governance/ci-mirror",
    "governance/x",
    "governance/a1",
    "governance/x_y-z",
    "governance/ci-pin-khai-tests-v0.1.5",
    "governance/bump-v2.0.0",
])
def test_classify_governance(branch):
    assert classify_branch(branch) == "governance"


@pytest.mark.parametrize("branch", [
    "governance",
    "governance/",
    "governance/X",
    "governance/Foo",
    " governance/x",
    "governance/x ",
    "governance-x",
    "governances/x",
    "gov/x",
])
def test_classify_governance_near_misses_are_other(branch):
    """Typos must NOT be 'governance' - fall through to 'other' (safer default)."""
    assert classify_branch(branch) == "other"


@pytest.mark.parametrize("branch", [
    "sync/release-from-main",
    "sync/release-from-main-2026-05-13",
    "sync/x",
    "sync/foo.bar_v1",
])
def test_classify_sync(branch):
    assert classify_branch(branch) == "sync"


@pytest.mark.parametrize("branch", [
    "sync",
    "sync/",
    "sync/X",
    "sync/Foo",
    " sync/x",
    "sync/x ",
    "sync-x",
    "syncs/x",
])
def test_classify_sync_near_misses_are_other(branch):
    """Typos must NOT be 'sync' - fall through to 'other' (safer default)."""
    assert classify_branch(branch) == "other"


# ---------------------------------------------------------------------------
# culture_scope
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("branch,expected", [
    ("culture/germany",     "regions/europe/germany/"),
    ("culture/denmark",     "regions/europe/denmark/"),
    ("culture/netherlands", "regions/europe/netherlands/"),
    ("culture/poland",      "regions/europe/poland/"),
])
def test_culture_scope_country(branch, expected):
    assert culture_scope(branch) == expected


@pytest.mark.parametrize("region", ["europe", "africa", "americas", "asia", "oceania"])
def test_culture_scope_region(region):
    assert culture_scope(f"culture/{region}") == f"regions/{region}/"


def test_culture_scope_world_release():
    assert culture_scope("culture/release") == "regions/"


@pytest.mark.parametrize("branch", [
    "culture/atlantis",
    "culture/mars",
    "culture/europe_west",
    "culture/germany_extra",
])
def test_culture_scope_unknown_slug_is_none(branch):
    assert culture_scope(branch) is None


@pytest.mark.parametrize("branch", ["main", "chore/x", "feat/foo", "culture/X"])
def test_culture_scope_non_culture_is_none(branch):
    assert culture_scope(branch) is None


def test_culture_scope_dot_slug_resolves_to_none():
    """A dot-containing slug like 'denmark.md' is syntactically valid but not
    a real country/region, so scope resolves to None and blocks everything."""
    assert culture_scope("culture/denmark.md") is None


# ---------------------------------------------------------------------------
# check_scope - culture branches
# ---------------------------------------------------------------------------

def test_check_scope_culture_own_country():
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
    assert ok
    assert unsafe == []


def test_check_scope_culture_blocks_other_country():
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
        "regions/europe/denmark/culture_danish_position.md",
    ], "culture/germany")
    assert not ok
    assert unsafe == ["regions/europe/denmark/culture_danish_position.md"]


def test_check_scope_culture_blocks_other_region():
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
        "regions/asia/japan/culture_japanese_position.md",
    ], "culture/germany")
    assert not ok
    assert "regions/asia/japan/culture_japanese_position.md" in unsafe


def test_check_scope_region_allows_own_region():
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
        "regions/europe/denmark/culture_danish_position.md",
        "regions/europe/netherlands/culture_dutch_position.md",
    ], "culture/europe")
    assert ok
    assert unsafe == []


def test_check_scope_region_blocks_other_region():
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
        "regions/asia/japan/culture_japanese_position.md",
    ], "culture/europe")
    assert not ok
    assert unsafe == ["regions/asia/japan/culture_japanese_position.md"]


def test_check_scope_world_release_allows_all():
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
        "regions/asia/japan/culture_japanese_position.md",
    ], "culture/release")
    assert ok
    assert unsafe == []


def test_check_scope_culture_allows_lock_index():
    """Migration PRs update lock index in same commit as bag YAML."""
    ok, unsafe = check_scope("culture", [
        "regions/europe/netherlands/hofstede_bag.yaml",
        "regions/europe/netherlands/hofstede_decisions.md",
        "data/hofstede_bag_locks.yaml",
    ], "culture/netherlands")
    assert ok
    assert unsafe == []


def test_check_scope_culture_allows_v2_list():
    """Migration PRs add the country to data/v2_migrated_countries.txt in the
    same commit that renames persona_* -> male_*/female_* and adds the
    khai declaration footers. Carved out via SAFE_PATTERNS."""
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_male_christian.md",
        "regions/europe/germany/culture_german_female_brigitte.md",
        "regions/europe/germany/culture_german_history_grundgesetz.md",
        "data/v2_migrated_countries.txt",
    ], "culture/germany")
    assert ok
    assert unsafe == []


def test_check_scope_culture_blocks_non_regions():
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
        ".githooks/pre-commit",
        "tests/validate_general.py",
        "ARCHITECTURE.md",
    ], "culture/germany")
    assert not ok
    assert ".githooks/pre-commit" in unsafe
    assert "tests/validate_general.py" in unsafe
    assert "ARCHITECTURE.md" in unsafe
    assert "regions/europe/germany/culture_german_position.md" not in unsafe


def test_check_scope_unknown_slug_blocks_everything():
    """Unknown slug must not silently widen scope to regions/**."""
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
        ".validation-stamp",
    ], "culture/atlantis")
    assert not ok
    assert unsafe == ["regions/europe/germany/culture_german_position.md"]


def test_check_scope_missing_branch_name_blocks_everything():
    ok, unsafe = check_scope("culture", [
        "regions/europe/germany/culture_german_position.md",
    ])
    assert not ok
    assert unsafe == ["regions/europe/germany/culture_german_position.md"]


# ---------------------------------------------------------------------------
# check_scope - other branches
# ---------------------------------------------------------------------------

def test_check_scope_other_allows_non_governance():
    ok, unsafe = check_scope("other", [
        ".github/copilot-instructions.md",
        "ARCHITECTURE.md",
        "README.md",
        "scripts/audit-germany.py",
        "data/hofstede_bag_locks.yaml",
        "data/v2_migrated_countries.txt",
    ])
    assert ok
    assert unsafe == []


def test_check_scope_other_blocks_governance_paths():
    ok, unsafe = check_scope("other", [
        ".githooks/pre-commit",
        "tests/branch_scope.py",
        "tests/validate_general.py",
        "tests/test_branch_scope.py",
        ".github/workflows/validate.yml",
        "scripts/validate.py",
        "scripts/validate_sections.py",
        "scripts/validate_history_arc.py",
        "scripts/audit_readme_bands.py",
        "scripts/update_hofstede_readme.py",
        "data/hofstede_keywords.py",
        "data/hofstede_scores.json",
        "ARCHITECTURE.md",
    ])
    assert not ok
    assert ".githooks/pre-commit" in unsafe
    assert "tests/branch_scope.py" in unsafe
    assert "tests/validate_general.py" in unsafe
    assert "tests/test_branch_scope.py" in unsafe
    assert ".github/workflows/validate.yml" in unsafe
    assert "scripts/validate.py" in unsafe
    assert "scripts/validate_sections.py" in unsafe
    assert "scripts/validate_history_arc.py" in unsafe
    assert "scripts/audit_readme_bands.py" in unsafe
    assert "scripts/update_hofstede_readme.py" in unsafe
    assert "data/hofstede_keywords.py" in unsafe
    assert "data/hofstede_scores.json" in unsafe
    assert "ARCHITECTURE.md" not in unsafe


def test_check_scope_other_blocks_regions():
    ok, unsafe = check_scope("other", [
        "regions/europe/germany/culture_german_position.md",
        "scripts/audit-germany.py",
    ])
    assert not ok
    assert unsafe == ["regions/europe/germany/culture_german_position.md"]


def test_check_scope_other_blocks_regions_metadata():
    """README inside regions/ is still culture territory on an infra branch."""
    ok, unsafe = check_scope("other", ["regions/europe/germany/README.md"])
    assert not ok
    assert unsafe == ["regions/europe/germany/README.md"]


def test_check_scope_safe_patterns_only_at_root():
    """`subdir/.gitignore` is not in SAFE_PATTERNS (exact-string match)."""
    ok, unsafe = check_scope("culture", ["subdir/.gitignore"], "culture/germany")
    assert not ok
    assert unsafe == ["subdir/.gitignore"]


def test_check_scope_main_is_noop():
    ok, unsafe = check_scope("main", [
        "regions/europe/germany/culture_german_position.md",
        ".githooks/pre-commit",
    ])
    assert ok
    assert unsafe == []


# ---------------------------------------------------------------------------
# check_scope - sync branches (main -> culture/release funnel)
# ---------------------------------------------------------------------------

def test_check_scope_sync_allows_any_path():
    """Sync branches mirror main's content; no path restriction applies."""
    ok, unsafe = check_scope("sync", [
        "regions/europe/germany/culture_german_position.md",
        ".githooks/pre-commit",
        ".github/workflows/validate.yml",
        "tests/branch_scope.py",
        "docs/BRANCHING.md",
        "scripts/validate.py",
    ])
    assert ok
    assert unsafe == []


# ---------------------------------------------------------------------------
# check_scope - governance branches
# ---------------------------------------------------------------------------

def test_check_scope_governance_allows_governance_paths():
    ok, unsafe = check_scope("governance", [
        ".githooks/pre-commit",
        ".github/workflows/validate.yml",
        "tests/branch_scope.py",
        "tests/test_branch_scope.py",
        "tests/validate_culture_completeness.py",
        "scripts/validate.py",
        "scripts/validate_sections.py",
        "scripts/validate_history_arc.py",
        "scripts/audit_readme_bands.py",
        "scripts/update_hofstede_readme.py",
        "data/hofstede_keywords.py",
        "data/hofstede_scores.json",
        ".validation-stamp",
        "data/v2_migrated_countries.txt",
    ], "governance/harden-validators")
    assert ok
    assert unsafe == []


def test_check_scope_governance_blocks_regions():
    ok, unsafe = check_scope("governance", [
        "tests/branch_scope.py",
        "regions/europe/germany/culture_german_position.md",
    ], "governance/x")
    assert not ok
    assert unsafe == ["regions/europe/germany/culture_german_position.md"]


def test_check_scope_governance_blocks_non_governance_infra():
    ok, unsafe = check_scope("governance", [
        "tests/branch_scope.py",
        "ARCHITECTURE.md",
        "scripts/audit-germany.py",
    ], "governance/x")
    assert not ok
    assert "ARCHITECTURE.md" in unsafe
    assert "scripts/audit-germany.py" in unsafe
    assert "tests/branch_scope.py" not in unsafe


# ---------------------------------------------------------------------------
# Locked sets - any change here is a contract change
# ---------------------------------------------------------------------------

def test_safe_patterns_set_locked():
    assert SAFE_PATTERNS == frozenset({
        ".validation-stamp",
        ".bump-type",
        ".gitignore",
        ".editorconfig",
        "data/hofstede_bag_locks.yaml",
        "data/v2_migrated_countries.txt",
    })


def test_world_slugs_set_locked():
    assert WORLD_SLUGS == frozenset({"release"})


# ---------------------------------------------------------------------------
# is_governance_path
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    ".githooks/pre-commit",
    ".githooks/sub/anything.sh",
    ".github/workflows/validate.yml",
    ".github/workflows/sub/anything.yml",
])
def test_is_governance_path_subtrees(path):
    assert is_governance_path(path)


@pytest.mark.parametrize("path", [
    "tests/branch_scope.py",
    "tests/test_branch_scope.py",
    "tests/test_hook_scope_e2e.py",
    "tests/test_hofstede_alignment.py",
    "tests/test_history_arc.py",
    "tests/validate_general.py",
    "tests/validate_culture_completeness.py",
    "tests/validate_hofstede_derived.py",
    "tests/validate_country_bag.py",
    "tests/requirements.txt",
    "tests/language_exceptions.txt",
    "scripts/validate.py",
    "scripts/validate_general.py",
    "scripts/validate_sections.py",
    "scripts/validate_history_arc.py",
    "scripts/setup-hooks.sh",
    "scripts/setup-hooks.bat",
    "scripts/audit_readme_bands.py",
    "scripts/update_hofstede_readme.py",
    "data/hofstede_denylist.yaml",
    "data/hofstede_keywords.py",
    "data/hofstede_scores.json",
    "data/hofstede_bag_loader.py",
    "data/language_policy.yaml",
    "data/phrase_denylist.txt",
])
def test_is_governance_path_glob_files(path):
    assert is_governance_path(path)


@pytest.mark.parametrize("path", [
    "ARCHITECTURE.md",
    "README.md",
    ".github/copilot-instructions.md",
    ".github/dependabot.yml",
    "scripts/audit-germany.py",
    "scripts/normalize-germany.py",
    "scripts/deploy_culture.py",
    "scripts/scaffold_country.py",
    "scripts/findings.py",
    "scripts/prose_review.py",
    "tests/PLAN.md",
    "tests/README.md",
    "tests/findings.py",
    "data/hofstede_bag_locks.yaml",
    "data/v2_migrated_countries.txt",
    "regions/europe/germany/culture_german_position.md",
])
def test_is_governance_path_non_governance(path):
    assert not is_governance_path(path)


def test_governance_dir_prefixes_locked():
    assert GOVERNANCE_DIR_PREFIXES == (".githooks/", ".github/workflows/")


def test_governance_glob_patterns_locked():
    assert GOVERNANCE_GLOB_PATTERNS == (
        "tests/branch_scope.py",
        "tests/test_*.py",
        "tests/validate_*.py",
        "tests/requirements.txt",
        "tests/language_exceptions.txt",
        "scripts/validate.py",
        "scripts/validate_*.py",
        "scripts/setup-hooks.sh",
        "scripts/setup-hooks.bat",
        "scripts/audit_readme_bands.py",
        "scripts/update_hofstede_readme.py",
        "data/hofstede_denylist.yaml",
        "data/hofstede_keywords.py",
        "data/hofstede_scores.json",
        "data/hofstede_bag_loader.py",
        "data/language_policy.yaml",
        "data/phrase_denylist.txt",
        "docs/BRANCHING.md",
        ".worktree/WORKTREES.md",
        ".worktree/.gitignore",
    )
