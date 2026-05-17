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

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from branch_scope import allowed_bases  # noqa: E402


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
