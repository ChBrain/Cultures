"""Verify .validation-stamp equals the tree hash of HEAD (excluding stamp).

Tightens the existing L0-stamp-check (which only verifies the file is
present). The stamp's value is the git tree-hash that the pre-commit
hook computes after stripping the stamp itself from the index. If the
contents of the tree change but the stamp is not refreshed, the values
diverge and this check catches it.

What this closes:
- GitHub Web UI commits (didn't re-run local hook -> stamp stale)
- ``git commit --no-verify`` (skipped the hook -> stamp stale)
- A copied/replayed stamp from a different tree

What this does NOT close:
- A contributor who runs the local hook on a permissive variant of
  branch_scope.py: the stamp will be valid, but the diff would still
  fail validate_pr_scope or branch-scope-check. Tree-hash equality is
  one layer in the stack, not the whole stack.

Usage:  validate_pr_stamp.py
        Run from the repo root with HEAD pointing at the PR head.
Exit:   0 if stamp matches tree hash; 1 with explanation otherwise.

Called from .github/workflows/pr-gate.yml.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _run_git(*args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True, env=env,
    )
    return result.stdout.strip()


def _compute_tree_hash_excluding_stamp() -> str:
    """Compute the tree hash of HEAD minus .validation-stamp.

    The pre-commit hook computes this same value before writing the
    stamp file. We use a temporary index so the running repo is never
    mutated -- safe to call from a CI job that has other steps after.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_index = str(Path(tmpdir) / "index")
        env = {**os.environ, "GIT_INDEX_FILE": tmp_index}
        _run_git("read-tree", "HEAD", env=env)
        # ignore-unmatch: if there's no .validation-stamp committed (which
        # is itself a check failure handled by the caller), don't error here.
        subprocess.run(
            ["git", "rm", "--cached", "--ignore-unmatch", ".validation-stamp"],
            env=env, capture_output=True, check=False,
        )
        return _run_git("write-tree", env=env)


def main(argv: list[str]) -> int:
    stamp_path = Path(".validation-stamp")
    if not stamp_path.is_file():
        print(">>> ERROR: .validation-stamp missing from HEAD")
        print("")
        print( "   The pre-commit hook writes this file on every successful")
        print( "   local commit. Its absence means local validation did not")
        print( "   run (or the commit was made via the GitHub Web UI).")
        print("")
        print( "   Recovery:")
        print( "     1. Install the hook locally: scripts/setup-hooks.sh")
        print( "     2. Re-run validation: git commit --amend -m '<msg>'")
        print( "     3. Force-push the branch.")
        return 1

    recorded = stamp_path.read_text(encoding="utf-8").strip()
    computed = _compute_tree_hash_excluding_stamp()

    if recorded == computed:
        print(f"OK: .validation-stamp matches tree hash ({computed[:12]})")
        return 0

    print(">>> ERROR: .validation-stamp does not match current tree hash")
    print("")
    print(f"   Recorded in .validation-stamp: {recorded}")
    print(f"   Computed from HEAD's tree:     {computed}")
    print("")
    print( "   The tree changed after the stamp was written. Common causes:")
    print( "     - GitHub Web UI edit on top of a hook-signed commit")
    print( "     - 'git commit --no-verify' that skipped the hook")
    print( "     - Stamp manually edited or copied from a different tree")
    print("")
    print( "   Fix: re-run local validation to refresh the stamp.")
    print( "     git config core.hooksPath .githooks")
    print( "     git add -A && git commit --amend -m '<original message>'")
    print( "     git push --force-with-lease")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
