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

import os
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


def _write_step_summary(text: str) -> None:
    """Append the failure report to the GitHub Actions step summary, if in CI."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("### pr-gate: diff within branch scope\n\n```\n" + text + "\n```\n")


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

    lines = [
        f">>> ERROR: PR diff exceeds branch scope for {head} (kind={kind})",
        "",
        f"Unsafe files ({len(unsafe)}):",
    ]
    lines += [f"  x {f}" for f in unsafe]
    lines.append("")
    if kind == "culture":
        prefixes = culture_scope(head)
        if prefixes is None:
            lines += [
                f"   Culture slug '{head}' doesn't resolve to a country/region/"
                "world/engine.",
                "   Rename the branch or split the work; see branch_scope.culture_scope.",
            ]
        else:
            allowed = " + ".join(f"{p}**" for p in prefixes)
            lines.append(f"   Allowed: {allowed} + " + ", ".join(sorted(SAFE_PATTERNS)))
    elif kind == "governance":
        lines += [
            "   Allowed: governance paths only (GOVERNANCE_DIR_PREFIXES +",
            "            GOVERNANCE_GLOB_PATTERNS in tests/branch_scope.py)",
            "   Non-governance file? Move it to a chore/* branch in a separate PR.",
        ]
    else:
        lines += [
            "   Allowed: anything except regions/** and governance paths.",
            "   regions/** change? Use culture/<slug>.",
            "   Governance change? Use governance/<name>.",
        ]
    lines += [
        "",
        "   Route by operation: python tests/branch_scope.py advise --op <operation>",
        "   or check files directly: python tests/branch_scope.py advise --files <path>...",
    ]
    report = "\n".join(lines)
    print(report)
    _write_step_summary(report)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
