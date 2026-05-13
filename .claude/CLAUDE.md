# CLAUDE.md

*Worktree discipline for the Cultures repo. Apply every session.*

## Rule 1 - Worktree-first

The main checkout at `c:\Code\Cultures` tracks `main` and stays clean. Any
non-trivial change runs in a worktree under `.claude/worktrees/<kind>/<slug>/`.
"Non-trivial" means any file edit beyond reading. Reads, greps, and
explorations may stay in the main checkout.

Each worktree directory pairs 1:1 with a branch of the same name.

## Rule 2 - Branch kind chosen before entering

Pick the branch kind from the change's primary target, using
[docs/BRANCHING.md](../docs/BRANCHING.md) as the contract:

- `culture/<country>` or `culture/<region>` for culture content
- `governance/<name>` for validators, hooks, workflows, branch_scope
- `chore/<name>` for tooling, scripts, docs
- `fix/<name>` for corrections outside culture and governance
- `feat/<name>` for non-culture, non-governance features

If a request spans two kinds, split it into two worktrees + two PRs. Never
widen scope to fit everything into one branch.

Refuse to start work without picking a kind. The branch name is a precommit
contract, not a label.

## Rule 3 - Creating and entering the worktree

`EnterWorktree(name:)` rewrites the branch name (`/` to `+`, `worktree-`
prefix) which breaks the pre-commit classifier. To get the branch and path
the hook expects, create the worktree with `git worktree add` first, then
enter by path:

```
git worktree add -b <kind>/<slug> .claude/worktrees/<kind>/<slug> origin/main
```

then

```
EnterWorktree(path: ".claude/worktrees/<kind>/<slug>")
```

If a worktree for the branch already exists, skip the `git worktree add`
step and only call `EnterWorktree(path:)`.

## Rule 4 - Subagent isolation

Any `Agent` call that may edit files is launched with `isolation: "worktree"`.
This prevents parallel agents from stomping each other and prevents an agent
from contaminating the main session's worktree. Read-only agents (`Explore`,
research-only `general-purpose`) do not need isolation.

When dispatching multiple editing agents in parallel, each gets its own
isolated worktree. Merging their outputs back is a deliberate, post-agent
step - not implicit.

## Rule 5 - Exit only after the PR lands

`ExitWorktree` is called only after the PR for the branch is opened or
merged. The worktree must outlive the first push so review feedback is
addressed on the same branch. If work is abandoned, exit explicitly with
`action: "remove"` - do not leave orphan worktrees.

## Rule 6 - Pre-commit hook is the gate

`.githooks/pre-commit` runs L0-L4 validators plus Hofstede checks on culture
branches. Never bypass with `--no-verify`. If it fails, fix the root cause;
do not retarget the branch kind to skip the validator. The full contract for
"which branch may touch what" lives in
[docs/BRANCHING.md](../docs/BRANCHING.md).

---

*v0.1.0 - KAI Worlds*
