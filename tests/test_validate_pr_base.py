"""Unit tests for the PR base routing contract (branch_scope.allowed_bases).

Pins the allowed_bases() routing layer:
  culture/<country|region>          -> {"culture/release"}
    culture/release                   -> {"main"}
  governance/<name>                 -> {"main"}
  sync/<name>                       -> {"culture/release"}
  chore/*, fix/*, feat/*, other     -> {"main"}
  main                              -> set()  (invalid head)

DRY note: branch pattern validity (e.g. what makes a slug valid) is
exhaustively covered in test_branch_scope.py. These tests cover one
representative per routing path plus dot-slug variants (allowed since
PR #114).

Run: python -m pytest tests/test_validate_pr_base.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from branch_scope import allowed_bases, base_remedy  # noqa: E402


# ---------------------------------------------------------------------------
# culture/<country|region> -> culture/release
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("head", [
    "culture/germany",       # country
    "culture/europe",        # region
    "culture/rollout-v1.2",  # dots -- version slugs allowed since PR #114
])
def test_culture_non_world_routes_to_release(head):
    assert allowed_bases(head) == {"culture/release"}


# ---------------------------------------------------------------------------
# culture world slugs -> main
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("head", ["culture/release"])
def test_culture_world_slug_routes_to_main(head):
    assert allowed_bases(head) == {"main"}


# ---------------------------------------------------------------------------
# governance -> main
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("head", [
    "governance/harden-validators",
    "governance/foo-v0.1.5",  # dots
])
def test_governance_routes_to_main(head):
    assert allowed_bases(head) == {"main"}


# ---------------------------------------------------------------------------
# sync -> culture/release
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("head", [
    "sync/release-from-main",
    "sync/release-from-main-2026-05-13",
    "sync/foo.bar_v1",
])
def test_sync_routes_to_release(head):
    assert allowed_bases(head) == {"culture/release"}


# ---------------------------------------------------------------------------
# other -> main
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("head", [
    "chore/refactor",
    "fix/typo",
    "feat/new-thing",
    "random-branch",
])
def test_other_routes_to_main(head):
    assert allowed_bases(head) == {"main"}


# ---------------------------------------------------------------------------
# invalid head
# ---------------------------------------------------------------------------

def test_main_is_invalid_head():
    assert allowed_bases("main") == set()


# ---------------------------------------------------------------------------
# validate.yml trigger must not drift from the allowed-base set
# ---------------------------------------------------------------------------

def test_validate_yml_runs_for_exactly_the_allowed_bases():
    """validate.yml triggers on a fixed branch set; allowed_bases() routes
    PRs to a base set. If the two drift, a PR can target a base the base
    check accepts while validate.yml never runs for it -- the #290 class
    (a PR with zero content validation)."""
    text = (HERE.parent / ".github" / "workflows" / "validate.yml").read_text(
        encoding="utf-8"
    )
    m = re.search(r"pull_request:\s*\n\s*branches:\s*\[([^\]]*)\]", text)
    assert m, "validate.yml: could not find the pull_request branches trigger"
    triggers = {b.strip() for b in m.group(1).split(",") if b.strip()}
    routed: set[str] = set()
    for head in ("culture/germany", "culture/release", "governance/x",
                 "sync/x", "fork/x", "chore/x"):
        routed |= allowed_bases(head)
    assert triggers == routed, (
        f"validate.yml triggers on {sorted(triggers)} but allowed_bases() "
        f"routes PRs to {sorted(routed)} -- they must match, or a PR can "
        f"target a base where validate.yml never runs."
    )


# ---------------------------------------------------------------------------
# base_remedy names the engine-stacking sequencing trap
# ---------------------------------------------------------------------------

def test_base_remedy_flags_culture_stacked_on_feature_branch():
    """A culture branch based on a non-integration branch (e.g. stacked on
    an engine PR because its content links that engine's files) gets the
    sequencing guidance, not just 'retarget to culture/release'."""
    msg = base_remedy("culture/germany", "engine/language-process-ladder")
    assert msg is not None
    assert "sequencing dependency" in msg
    assert "engine -> main -> sync" in msg


def test_base_remedy_culture_into_release_is_clean():
    assert base_remedy("culture/germany", "culture/release") is None
