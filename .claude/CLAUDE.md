# CLAUDE.md

*Worktree discipline for the Cultures repo. Apply every session.*

## Canonical references

- Branch-kind and scope contract: [docs/BRANCHING.md](../docs/BRANCHING.md)
- Worktree lifecycle and commands: [.worktree/WORKTREES.md](../.worktree/WORKTREES.md)
- Shared delivery chapters: [docs/LIFECYCLE.md](../docs/LIFECYCLE.md)

If these markdown files disagree with executable rules, the executable rules
(`tests/branch_scope.py` + pre-commit + CI) win.

## Claude-specific note

`EnterWorktree(name:)` can rewrite branch names (`/` -> `+`, `worktree-`
prefix), which can break branch-scope classification. Use path-based entry
after creating the real branch/worktree pair with git as documented in
[.worktree/WORKTREES.md](../.worktree/WORKTREES.md).

## Rule 1 - Subagent isolation

Any `Agent` call that may edit files is launched with `isolation: "worktree"`.
This prevents parallel agents from stomping each other and prevents an agent
from contaminating the main session's worktree. Read-only agents (`Explore`,
research-only `general-purpose`) do not need isolation.

When dispatching multiple editing agents in parallel, each gets its own
isolated worktree. Merging their outputs back is a deliberate, post-agent
step - not implicit.

## Rule 2 - Exit only after the PR lands

`ExitWorktree` is called only after the PR for the branch is opened or
merged. The worktree must outlive the first push so review feedback is
addressed on the same branch. If work is abandoned, exit explicitly with
`action: "remove"` - do not leave orphan worktrees.

## Rule 3 - Pre-commit hook is the gate

`.githooks/pre-commit` runs L0-L4 validators plus Hofstede checks on culture
branches. Never bypass with `--no-verify`. If it fails, fix the root cause;
do not retarget the branch kind to skip the validator. The full contract for
"which branch may touch what" lives in
[docs/BRANCHING.md](../docs/BRANCHING.md).

---

*v0.1.0 - KAI Worlds*
