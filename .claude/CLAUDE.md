# CLAUDE.md

*Worktree discipline for the Cultures repo. Apply every session.*

## Rule 1 - Worktree-first

The main checkout at `c:\Code\Cultures` tracks `main` and stays clean. Any
non-trivial change runs in a worktree under `.claude/worktrees/<kind>/<slug>/`.
"Non-trivial" means any file edit beyond reading. Reads, greps, and
explorations may stay in the main checkout.

Each worktree directory pairs 1:1 with a branch of the same name. Both
names come from the table in Rule 2.

## Rule 2 - Branch kind chosen before entering

The pre-commit hook classifies the branch from its name and rejects
out-of-scope commits (see `tests/branch_scope.py` and
`.github/copilot-instructions.md` > Branch Scope Guards). Pick from the
change's primary target, not from convenience.

| Primary target of the change | Branch / worktree slug |
|---|---|
| `regions/<region>/<country>/` (one country) | `culture/<country>` |
| `regions/<region>/` (across one region) | `culture/<region>` |
| `regions/**` (cross-region / world) | `culture/staging` or `culture/release` |
| Validators, hooks, workflows, branch_scope, validator data | `governance/<name>` |
| Tooling, scripts, docs outside the governance set | `chore/<name>` |
| Correction outside culture and governance | `fix/<name>` |
| Non-culture, non-governance feature | `feat/<name>` |

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
do not retarget the branch kind to skip the validator.

---

*v0.1.0 - KAI Worlds*
