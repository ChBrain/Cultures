# Branching

*Canonical branch-kind contract for the Cultures repo. Single source of truth
for humans and AI agents; the executable source is
[`tests/branch_scope.py`](../tests/branch_scope.py).*

## Why this exists

The repo enforces a strict branch-scope contract:

- `main` is protected - direct commits are rejected.
- Culture content (`regions/**`) is walled off from infrastructure changes so
  a refactor cannot accidentally touch culture data.
- Validators, hooks, and workflow definitions (**governance**) are walled off
  from generic tooling work so an automated contributor (or an LLM) cannot
  silently weaken the gates that protect culture content.

Every branch is classified by its name. `.githooks/pre-commit` rejects
out-of-scope commits locally; CI mirrors the same classifier. The branch
kinds and their scope rules are below.

## Pre-flight: ask the advisor

Before `git checkout -b`, ask the advisor which branch and base the work
needs - do not guess from the file types you expect to touch (a sync touches
workflow files but is a sync, not governance):

```
python tests/branch_scope.py advise --op <operation>
python tests/branch_scope.py advise --op new-country --slug <country>
python tests/branch_scope.py advise --files <path> [<path> ...]
```

- `--op` routes by *operation* - `new-country`, `new-region`, `release`,
  `sync`, `fork`, `governance`, `chore`, `fix`, `feat` - and prints the branch
  name, the required base, and the `git checkout -b` command.
- `--files` reports which lane a set of paths belongs to, and refuses a set
  that spans lanes with `SPLIT REQUIRED` plus the per-lane breakdown.

The advisor is the inverse of the classifier: the classifier rejects a wrong
branch name after the fact; the advisor hands you the right one up front.

## Branch kinds

| Kind | Pattern | PR base | Allowed paths | Hofstede check |
|---|---|---|---|---|
| `main` | exact `main` | — (not a PR head) | nothing - direct commits forbidden | n/a |
| culture (country) | `culture/<country>` | `culture/release` | `regions/<region>/<country>/**` + safe metadata | yes (±10 gap) |
| culture (region) | `culture/<region>` | `culture/release` | `regions/<region>/**` + safe metadata | yes (±10 gap) |
| culture (world) | `culture/release` | `main` | `regions/**` + safe metadata | yes (±10 gap) |
| governance | `governance/<name>` | `main` | governance paths + safe metadata | n/a |
| sync | `sync/<name>` | `culture/release` | unrestricted (snapshot of `main`) | n/a |
| fork | `fork/<name>` | `culture/release` | `regions/**` + safe metadata **only** | yes (±10 gap) |
| other | `chore/*`, `fix/*`, `feat/*`, … | `main` | everything **except** `regions/**` **and except** governance paths | n/a |

The pattern is anchored. `feat/culture-x`, `cultures/x`, and `culture/Denmark`
(uppercase) all classify as `other` and are blocked from `regions/`.

The **PR base** column is the only base each kind may target; it mirrors
`allowed_bases()` in `tests/branch_scope.py`, which the `pr-gate` workflow
enforces. Note the two directions are different lanes: `sync/<name>` carries
`main` *into* `culture/release`; carrying `culture/release` the other way,
*into* `main`, is not a sync at all - it is the release PR, whose head is
`culture/release` itself.

## Culture slug resolution

`culture/<slug>` is resolved against the on-disk `regions/` tree:

- `<slug>` = `release` -> world-level -> may touch `regions/**`.
- `<slug>` matches a region folder -> region-level -> may touch `regions/<slug>/**`.
- `<slug>` matches a country folder -> country-level -> may touch `regions/<region>/<slug>/**`.
- Otherwise: unknown slug -> reject (typo does not silently widen scope).

A `culture/germany` branch cannot touch Denmark even though both live under
`regions/europe/`. For multi-country work in one PR, use `culture/<region>` or
`culture/release`.

## Culture branch base

A `culture/<country>` or `culture/<region>` branch must be **cut from
`culture/release`**, the integration branch - never from `main`:

```
git fetch origin
git checkout -b culture/<country> origin/culture/release
```

A branch cut from `main` - or one that later merges `main` in - carries
commits that are on `main` but not yet on `culture/release`. Those commits
pollute the PR diff: the branch-scope check then flags every file `main`
changed in that gap as if the branch authored it, and contributors chase
scope violations that are really just a mis-based branch.

CI enforces this. The `cultures - Culture branch base` job fails any
`culture/*` PR whose branch contains a commit already on `main` but absent
from `culture/release`, and prints the `git rebase --onto` remedy.
`culture/release` itself is exempt - it integrates upward into `main`.

## Governance paths

Files that define or enforce repository rules. Editing any of these requires a
`governance/<name>` branch.

**Directory prefixes** (everything below is governance):

- `.githooks/**` - local pre-commit enforcement
- `.github/workflows/**` - CI enforcement

**Glob patterns** (specific paths):

- `tests/branch_scope.py` - the classifier itself
- `tests/test_*.py` - tests that pin the rules
- `tests/validate_*.py` - every validator script
- `tests/requirements.txt`, `tests/language_exceptions.txt` - validator config
- `scripts/validate.py`, `scripts/validate_general.py` - orchestrator + helper
- `scripts/setup-hooks.sh`, `scripts/setup-hooks.bat` - hook installation
- `scripts/audit_readme_bands.py` - canonical Hofstede band contract
- `scripts/update_hofstede_readme.py` - deterministic README Hofstede-tables updater
- `scripts/build_zips.py` - the release zip build engine
- `data/hofstede_denylist.yaml`, `data/hofstede_keywords.py` - validator inputs
- `data/hofstede_scores.json` - Hofstede Insights reference dataset
- `data/hofstede_bag_loader.py` - bag-validation infrastructure
- `data/language_policy.yaml` - per-language policy data
- `data/phrase_denylist.txt` - plagiarism phrase denylist
- `.worktree/WORKTREES.md`, `.worktree/.gitignore` - worktree governance policy

Authoritative list: `GOVERNANCE_DIR_PREFIXES` + `GOVERNANCE_GLOB_PATTERNS` in
[`tests/branch_scope.py`](../tests/branch_scope.py). This document is
downstream of the code; if the two disagree, the code wins and the doc is the
bug.

## Sync branches

`sync/<name>` branches funnel `main`'s HEAD into `culture/release`. They exist
so `culture/release` (the integration target for `culture/<country>` PRs) can
stay current with `main` without bypassing branch protection.

A sync branch carries no new commits - the branch ref points directly at
`main`'s tip. The PR (sync/<name> -> culture/release) is reviewed and merged
through the normal flow; CI's PR-base gate allows the routing, and the
PR-scope check is permissive on sync because the content is whatever `main`
already has.

Typical naming: `sync/release-from-main-<date>`. Cadence: as needed when
`culture/release` drifts behind `main` enough that culture-PR diffs against it
include non-target content.

A `sync/<name>` branch only ever targets `culture/release`. The reverse -
landing `culture/release`'s accumulated culture content on `main` - is **not**
a sync: it is the release PR, opened with head `culture/release` and base
`main` (no intermediate branch). Filing that as `sync/* -> main` fails the
`pr-gate` base check; `python tests/branch_scope.py advise --op release`
prescribes the correct routing.

## Fork branches

`fork/<name>` is the lane for **external / contributor culture content** -
work that originates outside the maintainer's own branches (typically a
GitHub fork PR). `<name>` is the contributor handle.

It is the **narrowest write scope in the repo**: `regions/**` plus safe
metadata, and nothing else - no engine, no scripts, no validators, no
workflows, no governance data. A fork branch that touches any of those is
rejected by the scope check. The point is containment: an outside
contribution cannot reach an executable or rule-defining surface, so it
cannot weaken a gate or exfiltrate a secret through CI.

A fork PR cannot run the private `khai` jobs (a fork gets no `KAIHACKS`
secret). The workflow is therefore: **re-home** the contribution onto a
`fork/<name>` branch in this repo, where it runs the full same-repo gate
set, before it reaches `culture/release`. A `fork/<name>` branch carries
culture content, so it is held to the culture gates (Hofstede ±10 included)
and targets `culture/release`, exactly like a `culture/<country>` branch.

Before re-homing, review the diff: if it is purely `regions/**` it is inert
content; anything outside `regions/**` must be treated as untrusted code.

## Worktree operations

Branching policy and scope constraints are defined in this document.
Local worktree lifecycle and command workflow are defined in
[../.worktree/WORKTREES.md](../.worktree/WORKTREES.md).

## Safe metadata

Paths allowed on **any** branch kind alongside the branch's primary scope:

- `.validation-stamp` - proof of local validation
- `.bump-type` - version intent declaration
- `.gitignore`, `.editorconfig` - repository config
- `data/hofstede_bag_locks.yaml` - bag-lock index (carved out for bag migration PRs)
- `data/v2_migrated_countries.txt` - per-country v2 opt-in (carved out for v2 migration PRs)

Authoritative list: `SAFE_PATTERNS` in
[`tests/branch_scope.py`](../tests/branch_scope.py).

## Splitting work across scopes

If a change spans two kinds, split it into separate branches/PRs:

1. Culture content -> `culture/<country>` (or `<region>`, `release`)
2. Validator / hook / workflow changes -> `governance/<name>`
3. General tooling / docs -> `chore/<name>`
4. Bug fixes outside culture and governance -> `fix/<name>`
5. New non-culture, non-governance features -> `feat/<name>`

Never widen scope to fit everything into one branch.

## Hook rejection messages

```
>>> ERROR: Culture branch out of scope (allowed: regions/<region>/<country>/**)
>>> ERROR: Unknown culture slug
>>> ERROR: Governance branch out of scope
>>> ERROR: Non-culture/non-governance branch out of scope
```

When rejected: `git reset`, move the offending files to the correct branch
kind, recommit. Never bypass with `--no-verify`.

## Why this is gated locally and in CI

The pre-commit hook enforces classification at the developer's machine. CI
mirrors the classifier so a `--no-verify` push does not bypass the rule. Both
read from `tests/branch_scope.py`, which is itself in governance scope - so
weakening the rules requires its own `governance/*` PR with explicit
justification.

---

*v0.1.0 - KAI Worlds*
