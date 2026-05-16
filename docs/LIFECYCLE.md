# LIFECYCLE

*Shared delivery lifecycle for the Cultures repo.*

## Purpose

This file is the shared execution model for contributors and agent wrappers.
It complements, but does not replace, branch scope policy and worktree policy.

- Branch/scope contract: [BRANCHING.md](./BRANCHING.md)
- Worktree mechanics: [../.worktree/WORKTREES.md](../.worktree/WORKTREES.md)

## 1. Plan

Decide intent and branch kind before edits.

- Pick branch kind from [BRANCHING.md](./BRANCHING.md).
- Confirm allowed paths for that branch kind.
- Split cross-scope requests into separate branches and PRs.

Output: branch kind, target files, and PR route are clear.

## 2. Code

Make the smallest scoped changes that satisfy the request.

- Keep edits inside branch scope.
- Preserve existing architecture and conventions.
- Prefer one concern per branch.

Output: focused diff for the declared scope.

## 3. Build

Run build/setup steps needed for touched components.

- Use project-standard local commands.
- Capture build blockers early.

Output: changed surfaces are buildable.

## 4. Test

Run required validation/tests for touched files.

- Run targeted validators first.
- Run required gates for branch kind.
- Ensure `.validation-stamp` reflects current validated tree.

### Test strategy - Trust, but verify

- What can be tested locally shall be tested locally before commit.
- What can be tested only locally must be tested locally before push.
- What can be tested in CI shall be tested in CI, staged by branch target and release phase.

Validation ownership model:

- Local pre-commit: fast scoped checks on staged files.
- Local pre-push/manual: broader branch-scope checks when needed.
- CI PR gates: authoritative server-side rerun of required checks.
- CI release/promotion gates: staged checks tied to integration and release flow.

If a check is CI-only today but can run locally at acceptable cost, move it to local as well.

Output: checks pass for the changed scope.

## 5. Release

Package branch changes into a reviewable PR.

- Write precise PR title/body.
- Link rationale and constraints.
- Respect merge order when PRs depend on each other.

Output: PR is ready for review and policy gates.

## 6. Deploy

Apply repository-defined deploy/release steps after merge.

- Follow repo release workflow and tagging rules.
- Keep deployment changes auditable.

Output: released state matches merged intent.

## 7. Operate

Keep the system healthy during day-2 use.

- Maintain branch hygiene.
- Resolve conflicts and drift quickly.
- Keep docs and enforcement aligned.

Output: stable contributor workflow over time.

## 8. Monitor

Observe gate and runtime signals continuously.

- Watch CI/check trends.
- Detect policy drift and recurring failure patterns.
- Feed improvements back into Plan and Code stages.

Output: continuous improvement loop.

## Notes

- This lifecycle is shared guidance.
- If guidance and executable rules diverge, executable rules win.

---

*v0.1.0 - KAI Worlds*