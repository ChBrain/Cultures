"""Verify a PR's diff stays within its head branch's allowed file scope.

Server-side mirror of ``tests/branch_scope.check_scope``. Closes two
bypass paths the local pre-commit hook cannot cover:

- ``git commit --no-verify`` (skips the hook)
- GitHub Web UI edits (never invoke the hook)

If the local hook ran correctly, this check is a no-op. If anything
slipped past it, the PR fails here before it can merge.

Usage:  validate_pr_scope.py <head_branch> <base_ref>
        ``base_ref`` is a git ref like 'origin/main' or
        'origin/culture/release' (the PR's base).
Exit:   0 if every changed file is within head's allowed scope; 1 otherwise.

Called from .github/workflows/pr-gate.yml.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from branch_scope import (  # noqa: E402
    SAFE_PATTERNS,
    check_scope,
    classify_branch,
    culture_scope,
)


def diff_paths(base_ref: str) -> list[str]:
    """Return the set of paths changed between ``base_ref`` and HEAD.

    ``--diff-filter=ACMRT`` excludes deletions; a path that no longer
    exists in HEAD can't be scope-checked and is irrelevant for our
    "are you touching forbidden files" question.

    ``base_ref...HEAD`` (three-dot) uses the merge base, which is what
    GitHub's PR diff shows; we match it so failures point at the same
    file list the reviewer sees.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRT", f"{base_ref}...HEAD"],
        capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: validate_pr_scope.py <head_branch> <base_ref>", file=sys.stderr)
        return 2
    head, base_ref = argv[1], argv[2]
    kind = classify_branch(head)
    paths = diff_paths(base_ref)

    ok, unsafe = check_scope(kind, paths, head)
    if ok:
        print(f"OK: all {len(paths)} changed files within {kind} scope for {head}")
        return 0

    print(f">>> ERROR: PR diff exceeds branch scope for {head} (kind={kind})")
    print("")
    print(f"Unsafe files ({len(unsafe)}):")
    for f in unsafe:
        print(f"  x {f}")
    print("")
    if kind == "culture":
        prefix = culture_scope(head)
        if prefix is None:
            print(f"   Culture slug '{head}' doesn't resolve to a country/region/world.")
            print( "   Rename the branch or split the work; see branch_scope.culture_scope.")
        else:
            print(f"   Allowed: {prefix}** + " + ", ".join(sorted(SAFE_PATTERNS)))
    elif kind == "governance":
        print( "   Allowed: governance paths only (GOVERNANCE_DIR_PREFIXES +")
        print( "            GOVERNANCE_GLOB_PATTERNS in tests/branch_scope.py)")
        print( "   Non-governance file? Move it to a chore/* branch in a separate PR.")
    else:
        print( "   Allowed: anything except regions/** and governance paths.")
        print( "   regions/** change? Use culture/<slug>.")
        print( "   Governance change? Use governance/<name>.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
