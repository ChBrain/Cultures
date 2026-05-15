# WORKTREES.md

*Canonical local worktree workflow for the Cultures repo.*

## Scope

This file defines **how** to run local worktrees.

- Branch policy (kinds, allowed paths, scope enforcement) lives in
  [docs/BRANCHING.md](../docs/BRANCHING.md).
- Worktree mechanics (create, enter, split, retire) live here.

If these documents disagree, branch policy from
[docs/BRANCHING.md](../docs/BRANCHING.md) and executable enforcement in
[`tests/branch_scope.py`](../tests/branch_scope.py) win.

## Worktree-first rule

Use the main checkout (`c:/Code/Cultures`) as a clean control plane.
Any non-trivial edit should happen in a dedicated worktree.

Recommended path pattern:

`.worktree/worktrees/<kind>/<slug>/`

Where `<kind>/<slug>` is the real branch name (for example
`culture/netherlands` or `governance/language-policy-french-enable`).

## Pick branch kind first

Before creating a worktree, choose branch kind from
[docs/BRANCHING.md](../docs/BRANCHING.md).

If a request spans multiple branch kinds, split work into multiple
worktrees and multiple PRs.

## Create a worktree

Use real branch names (do not rewrite `/` into `+`):

```bash
git fetch origin
git worktree add -b <kind>/<slug> .worktree/worktrees/<kind>/<slug> origin/main
```

Examples:

```bash
git worktree add -b culture/poland .worktree/worktrees/culture/poland origin/main
git worktree add -b governance/language-policy .worktree/worktrees/governance/language-policy origin/main
git worktree add -b chore/docs-worktrees .worktree/worktrees/chore/docs-worktrees origin/main
```

## Re-enter an existing worktree

```bash
git worktree list
```

Then enter by path in your tool/editor.

## Lifecycle

Keep worktrees alive through first push and review iteration.
Remove them after merge or explicit abandonment.

```bash
git worktree remove .worktree/worktrees/<kind>/<slug>
git branch -d <kind>/<slug>
```

Use `-D` only when branch history is intentionally disposable.

## Parallel work

For concurrent tasks, give each task its own branch + worktree pair.
Do not edit multiple tasks in one worktree.

## Quick checklist

1. Pick branch kind from [docs/BRANCHING.md](../docs/BRANCHING.md).
2. Create worktree from `origin/main`.
3. Make edits only within that task scope.
4. Commit and push.
5. Open PR with matching branch kind.
6. Remove worktree after PR lands (or on explicit abandon).

---

*v0.1.0 - KAI Worlds*
