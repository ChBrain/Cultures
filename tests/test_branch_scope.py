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
    advise_operation,
    allowed_bases,
    base_remedy,
    check_scope,
    classify_branch,
    culture_scope,
    diagnose_scope_failure,
    is_governance_path,
    lane_of_path,
    lanes_for_files,
    misbased_commits,
    render_files_advice,
    render_misbased_branch,
    render_operation_advice,
    render_scope_failure,
    valid_operations,
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
        "tests/culture_metadata.py",
        "tests/conftest.py",
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
        "scripts/migrate_footer_to_frontmatter.py",
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


# ---------------------------------------------------------------------------
# diagnose_scope_failure
# ---------------------------------------------------------------------------

def _fake_history(file_commits: dict[str, list[str]], on_main: set[str]):
    """Build (commits_for_file, is_on_main) callbacks from in-memory data."""
    return (
        lambda path: file_commits.get(path, []),
        lambda sha: sha in on_main,
    )


def test_diagnose_all_inherited_from_main():
    """Every flagged file traces only to commits already on main."""
    commits_for_file, is_on_main = _fake_history(
        {
            "tests/validate_language.py": ["c1"],
            ".githooks/pre-commit": ["c1", "c2"],
        },
        on_main={"c1", "c2"},
    )
    inherited, genuine = diagnose_scope_failure(
        ["tests/validate_language.py", ".githooks/pre-commit"],
        commits_for_file=commits_for_file,
        is_on_main=is_on_main,
    )
    assert inherited == ["tests/validate_language.py", ".githooks/pre-commit"]
    assert genuine == []


def test_diagnose_all_genuine():
    """Flagged files trace to commits the branch authored (not on main)."""
    commits_for_file, is_on_main = _fake_history(
        {"tests/validate_language.py": ["branchC"]},
        on_main={"c1"},
    )
    inherited, genuine = diagnose_scope_failure(
        ["tests/validate_language.py"],
        commits_for_file=commits_for_file,
        is_on_main=is_on_main,
    )
    assert inherited == []
    assert genuine == ["tests/validate_language.py"]


def test_diagnose_mixed():
    """A file touched by both an on-main and a branch commit is genuine."""
    commits_for_file, is_on_main = _fake_history(
        {
            "data/countries.json": ["c1"],
            "tests/test_x.py": ["c1", "branchC"],
        },
        on_main={"c1"},
    )
    inherited, genuine = diagnose_scope_failure(
        ["data/countries.json", "tests/test_x.py"],
        commits_for_file=commits_for_file,
        is_on_main=is_on_main,
    )
    assert inherited == ["data/countries.json"]
    assert genuine == ["tests/test_x.py"]


def test_diagnose_no_commits_is_genuine():
    """A flagged file whose history cannot be resolved is never excused."""
    commits_for_file, is_on_main = _fake_history({}, on_main={"c1"})
    inherited, genuine = diagnose_scope_failure(
        ["mystery.py"],
        commits_for_file=commits_for_file,
        is_on_main=is_on_main,
    )
    assert inherited == []
    assert genuine == ["mystery.py"]


def test_diagnose_empty():
    commits_for_file, is_on_main = _fake_history({}, on_main=set())
    assert diagnose_scope_failure(
        [], commits_for_file=commits_for_file, is_on_main=is_on_main,
    ) == ([], [])


# ---------------------------------------------------------------------------
# render_scope_failure
# ---------------------------------------------------------------------------

def test_render_inherited_only_names_cause_and_forbids_edits():
    msg = render_scope_failure(
        "culture/mexico", "culture/release",
        inherited=["tests/validate_language.py", ".githooks/pre-commit"],
        genuine=[],
        base_behind_main=14,
    )
    assert "2 file(s) outside its scope" in msg
    assert "carries main's history" in msg
    # The whole point: steer the LLM away from editing the validator.
    assert "Do NOT" in msg
    assert "git rebase origin/culture/release" in msg
    # base is stale -> the sync step is present.
    assert "sync 'main' -> 'culture/release'" in msg
    assert "14 commit(s) behind" in msg


def test_render_inherited_only_no_sync_step_when_base_fresh():
    msg = render_scope_failure(
        "culture/mexico", "culture/release",
        inherited=["data/countries.json"],
        genuine=[],
        base_behind_main=0,
    )
    assert "sync 'main'" not in msg
    assert "git fetch origin" in msg
    assert "git rebase origin/culture/release" in msg


def test_render_genuine_only_points_at_governance_branch():
    msg = render_scope_failure(
        "culture/germany", "culture/release",
        inherited=[],
        genuine=["tests/branch_scope.py"],
        base_behind_main=0,
    )
    assert "genuine scope violations" in msg
    assert "governance/*" in msg
    assert "carries main's history" not in msg


def test_render_mixed_lists_both_and_orders_rebase_first():
    msg = render_scope_failure(
        "culture/mexico", "culture/release",
        inherited=["data/countries.json"],
        genuine=["tests/test_x.py"],
        base_behind_main=3,
    )
    assert "carries main's history" in msg
    assert "genuine scope violations" in msg
    assert "data/countries.json" in msg
    assert "tests/test_x.py" in msg
    # Rebase step precedes the genuine-violation step.
    assert msg.index("git rebase") < msg.index("revert the genuine")


# ---------------------------------------------------------------------------
# misbased_commits
# ---------------------------------------------------------------------------

def test_misbased_commits_flags_on_main_only():
    commits = [
        ("aaa1111", "feat: tune mexico package"),   # branch's own work
        ("bbb2222", "Merge pull request #209"),      # main's lead
        ("ccc3333", "fix: stabilize mexico spans"),  # branch's own work
        ("ddd4444", "chore: seed name register"),    # main's lead
    ]
    offending = misbased_commits(
        commits, is_on_main=lambda sha: sha in {"bbb2222", "ddd4444"},
    )
    assert offending == [
        ("bbb2222", "Merge pull request #209"),
        ("ddd4444", "chore: seed name register"),
    ]


def test_misbased_commits_clean_branch_returns_empty():
    """A branch cut from culture/release has no commit on main yet."""
    commits = [("aaa1111", "feat: x"), ("ccc3333", "fix: y")]
    assert misbased_commits(commits, is_on_main=lambda sha: False) == []


def test_misbased_commits_empty():
    assert misbased_commits([], is_on_main=lambda sha: True) == []


# ---------------------------------------------------------------------------
# render_misbased_branch
# ---------------------------------------------------------------------------

def test_render_misbased_branch_names_cause_and_remedy():
    msg = render_misbased_branch(
        "culture/mexico",
        [("bbb2222", "Merge pull request #209"),
         ("ddd4444", "chore: seed name register")],
    )
    assert "wrong base" in msg
    assert "2 commit(s)" in msg
    assert "bbb2222" in msg and "ddd4444" in msg
    # Steer away from the wrong fix; give the exact rebase remedy.
    assert "do not edit validators" in msg.lower()
    assert "git rebase --onto origin/culture/release origin/main culture/mexico" in msg


def test_render_misbased_branch_respects_base_ref():
    msg = render_misbased_branch(
        "culture/europe", [("eee5555", "x")], base_ref="culture/release",
    )
    assert "culture/release" in msg


# ---------------------------------------------------------------------------
# advise_operation - operation -> prescribed branch
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("operation,kind,base", [
    ("new-country", "culture", "culture/release"),
    ("new-region", "culture", "culture/release"),
    ("release", "culture", "main"),
    ("sync", "sync", "culture/release"),
    ("governance", "governance", "main"),
    ("chore", "other", "main"),
    ("fix", "other", "main"),
    ("feat", "other", "main"),
])
def test_advise_operation_kind_and_base(operation, kind, base):
    advice = advise_operation(operation)
    assert advice is not None
    assert advice.kind == kind
    assert advice.base == base


def test_advise_operation_unknown_returns_none():
    assert advise_operation("sink") is None
    assert advise_operation("workflow-fix") is None


def test_valid_operations_is_the_registry():
    ops = valid_operations()
    assert set(ops) == {
        "new-country", "new-region", "release", "sync",
        "governance", "chore", "fix", "feat",
    }


def test_advise_sync_routes_to_sync_not_governance():
    """A sync touches workflow files but is a sync lane, not governance."""
    advice = advise_operation("sync")
    assert advice.kind == "sync"
    assert advice.branch.startswith("sync/")
    assert advice.base == "culture/release"
    assert advice.start == "origin/main"


def test_advise_new_country_resolves_real_slug():
    advice = advise_operation("new-country", "germany")
    assert advice.branch == "culture/germany"
    assert advice.scope.startswith("regions/europe/germany/")


def test_advise_new_country_flags_unknown_slug():
    advice = advise_operation("new-country", "atlantis")
    assert advice.branch == "culture/atlantis"
    assert "UNRESOLVED" in advice.scope


def test_render_operation_advice_gives_create_command():
    advice = advise_operation("new-country", "germany")
    out = render_operation_advice(advice)
    assert "git checkout -b culture/germany origin/culture/release" in out
    assert "Base:      culture/release" in out


def test_render_operation_advice_release_has_no_create_command():
    out = render_operation_advice(advise_operation("release"))
    assert "do not create it" in out
    assert "git checkout -b" not in out


# ---------------------------------------------------------------------------
# lane_of_path / lanes_for_files - files -> branch lane
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path,lane,kind", [
    ("regions/europe/germany/culture_german_position.md", "culture/germany", "culture"),
    ("regions/africa/nigeria/README.md", "culture/nigeria", "culture"),
    (".github/workflows/validate.yml", "governance/<name>", "governance"),
    ("tests/validate_language.py", "governance/<name>", "governance"),
    ("tests/branch_scope.py", "governance/<name>", "governance"),
    (".validation-stamp", "(safe metadata)", "safe"),
    ("data/hofstede_bag_locks.yaml", "(safe metadata)", "safe"),
    (".github/copilot-instructions.md", "chore/<name>", "other"),
    ("ARCHITECTURE.md", "chore/<name>", "other"),
    ("data/countries.json", "chore/<name>", "other"),
])
def test_lane_of_path(path, lane, kind):
    assert lane_of_path(path) == (lane, kind)


def test_lanes_for_files_single_lane():
    lanes = lanes_for_files([
        "regions/europe/germany/culture_german_position.md",
        "regions/europe/germany/README.md",
    ])
    assert lanes == {"culture/germany": [
        "regions/europe/germany/culture_german_position.md",
        "regions/europe/germany/README.md",
    ]}


def test_lanes_for_files_split_detects_mexico_bundle():
    """The PR #213 shape: culture content + validators + workflow + data."""
    lanes = lanes_for_files([
        "regions/americas/mexico/README.md",
        "tests/validate_language.py",
        ".github/workflows/validate.yml",
        "data/countries.json",
        ".validation-stamp",
    ])
    non_safe = {k for k in lanes if k != "(safe metadata)"}
    assert non_safe == {"culture/mexico", "governance/<name>", "chore/<name>"}
    out = render_files_advice(lanes)
    assert "SPLIT REQUIRED" in out
    assert "3 branch lanes" in out


def test_render_files_advice_single_lane():
    out = render_files_advice(lanes_for_files([
        "regions/europe/denmark/culture_danish_position.md",
    ]))
    assert "one lane: culture/denmark" in out
    assert "base: culture/release" in out


def test_render_files_advice_safe_only():
    out = render_files_advice(lanes_for_files([".validation-stamp"]))
    assert "safe metadata" in out.lower()


# ---------------------------------------------------------------------------
# base_remedy - prescriptive PR base routing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("head,base", [
    ("culture/germany", "culture/release"),
    ("culture/release", "main"),
    ("governance/harden-validators", "main"),
    ("sync/release-from-main-2026-05-17", "culture/release"),
    ("chore/tidy", "main"),
])
def test_base_remedy_none_for_valid_pair(head, base):
    assert base_remedy(head, base) is None


def test_base_remedy_matches_allowed_bases():
    """base_remedy returns None exactly when the pair is in allowed_bases."""
    heads = ["culture/germany", "culture/release", "governance/x",
             "sync/x", "chore/x", "main"]
    for head in heads:
        for base in ("main", "culture/release"):
            in_contract = base in allowed_bases(head)
            assert (base_remedy(head, base) is None) == in_contract


def test_base_remedy_sync_into_main_points_at_release_pr():
    """The PR #223 trap: a sync/* head aimed at main is told to use a release PR."""
    msg = base_remedy("sync/main-from-culture-release-2026-05-17", "main")
    assert msg is not None
    assert "not allowed" in msg
    assert "release PR" in msg
    assert "base 'main'" in msg
    assert "culture/release" in msg


def test_base_remedy_country_into_main_points_at_release():
    msg = base_remedy("culture/germany", "main")
    assert msg is not None
    assert "not allowed" in msg
    assert "culture/release" in msg


def test_base_remedy_release_wrong_base_points_at_main():
    msg = base_remedy("culture/release", "culture/release")
    assert msg is not None
    assert "Retarget" in msg
    assert "main" in msg


def test_base_remedy_main_is_not_a_valid_head():
    msg = base_remedy("main", "main")
    assert msg is not None
    assert "not a valid PR head" in msg
