"""Verify a PR's base branch matches what its head branch is allowed to target.

Server-side enforcement of the integration flow:

  culture/<slug>                  -> culture/release  (per-country/region work)
    culture/release                 -> main             (world-level integration)
  governance/<name>                -> main             (rule changes)
  sync/<name>                      -> culture/release  (main -> culture/release sync)
  chore/*, fix/*, feat/*, other    -> main             (non-culture, non-governance)

A PR with the wrong base fails this check. This closes the path where
someone (or an LLM) PRs ``culture/germany`` directly to ``main`` and
bypasses the ``culture/release`` integration gate.

Usage:  validate_pr_base.py <head_branch> <base_branch>
Exit:   0 if base is allowed for head; 1 with explanation otherwise.

Called from .github/workflows/pr-gate.yml. Adding a new branch kind
requires extending ``allowed_bases`` here AND the corresponding kind
in tests/branch_scope.classify_branch.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from branch_scope import WORLD_SLUGS, classify_branch  # noqa: E402


def allowed_bases(head: str) -> set[str]:
    """Return the set of acceptable PR base branches for ``head``.

    Empty set means ``head`` itself is invalid (e.g. ``main``, which
    cannot be a PR head). Callers should treat ``base in allowed_bases``
    as the gate.
    """
    kind = classify_branch(head)
    if kind == "main":
        return set()
    if kind == "culture":
        slug = head[len("culture/"):]
        if slug in WORLD_SLUGS:
            # World-level integration branch (culture/release)
            # PR upward into main.
            return {"main"}
        # Country/region branches must funnel through culture/release first.
        return {"culture/release"}
    if kind == "governance":
        return {"main"}
    if kind == "sync":
        # Sync branches funnel main -> culture/release.
        return {"culture/release"}
    # ``other`` (chore/*, fix/*, feat/*, etc.) goes directly to main.
    return {"main"}


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: validate_pr_base.py <head_branch> <base_branch>", file=sys.stderr)
        return 2
    head, base = argv[1], argv[2]
    allowed = allowed_bases(head)
    if not allowed:
        print(f">>> ERROR: '{head}' is not a valid PR head branch")
        return 1
    if base in allowed:
        print(f"OK: PR base '{base}' is allowed for head '{head}'")
        return 0
    print(f">>> ERROR: PR base '{base}' not allowed for head '{head}'")
    print("")
    print(f"   Allowed bases for {head}: {sorted(allowed)}")
    print("")
    kind = classify_branch(head)
    if kind == "culture":
        slug = head[len("culture/"):]
        if slug not in WORLD_SLUGS:
            print( "   Culture work flows:")
            print( "     culture/<slug>  -> culture/release  (this PR)")
            print( "     culture/release -> main             (release PR)")
            print( "   Retarget this PR's base to 'culture/release'.")
    elif kind == "governance":
        print( "   Governance changes go directly to main. Retarget to 'main'.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
