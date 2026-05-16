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
out-of-scope commits locally; CI mirrors the same classifier. The four kinds
and their scope rules are below.

## Branch kinds

| Kind | Pattern | Allowed paths | Hofstede check |
|---|---|---|---|
| `main` | exact `main` | nothing - direct commits forbidden | n/a |
| culture (country) | `culture/<country>` | `regions/<region>/<country>/**` + safe metadata | yes (±10 gap) |
| culture (region) | `culture/<region>` | `regions/<region>/**` + safe metadata | yes (±10 gap) |
| culture (world) | `culture/release` | `regions/**` + safe metadata | yes (±10 gap) |
| governance | `governance/<name>` | governance paths + safe metadata | n/a |
| sync | `sync/<name>` | unrestricted (snapshot of `main`) | n/a |
| other | `chore/*`, `fix/*`, `feat/*`, … | everything **except** `regions/**` **and except** governance paths | n/a |

The pattern is anchored. `feat/culture-x`, `cultures/x`, and `culture/Denmark`
(uppercase) all classify as `other` and are blocked from `regions/`.

## Culture slug resolution

`culture/<slug>` is resolved against the on-disk `regions/` tree:

- `<slug>` = `release` -> world-level -> may touch `regions/**`.
- `<slug>` matches a region folder -> region-level -> may touch `regions/<slug>/**`.
- `<slug>` matches a country folder -> country-level -> may touch `regions/<region>/<slug>/**`.
- Otherwise: unknown slug -> reject (typo does not silently widen scope).

A `culture/germany` branch cannot touch Denmark even though both live under
`regions/europe/`. For multi-country work in one PR, use `culture/<region>` or
`culture/release`.

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
