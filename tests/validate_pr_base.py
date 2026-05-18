"""CLI: verify a PR's base branch matches what its head is allowed to target.

Server-side enforcement of the integration flow. The routing matrix and the
remedy text are the single source of truth in ``tests/branch_scope.py``
(``allowed_bases`` / ``base_remedy``); this file is the thin CLI that
pr-gate.yml's base-branch-check job runs. On failure it prints the
prescriptive remedy and mirrors it to the GitHub Actions step summary so the
fix is visible in the PR's Checks UI without opening raw logs.

Usage:  validate_pr_base.py <head_branch> <base_branch>
Exit:   0 if base is allowed for head;
        1 with a prescriptive remedy otherwise;
        2 on bad arguments.

Called from .github/workflows/pr-gate.yml.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from branch_scope import base_remedy  # noqa: E402


def _write_step_summary(text: str) -> None:
    """Append the remedy to the GitHub Actions step summary, if running in CI."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("### pr-gate: allowed base for head\n\n```\n" + text + "\n```\n")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: validate_pr_base.py <head_branch> <base_branch>", file=sys.stderr)
        return 2
    head, base = argv[1], argv[2]
    remedy = base_remedy(head, base)
    if remedy is None:
        print(f"OK: PR base '{base}' is allowed for head '{head}'")
        return 0
    print(remedy)
    _write_step_summary(remedy)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
