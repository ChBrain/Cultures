# PERPLEXITY.md

*Operational discipline for the Cultures repo. Apply every session.*

---

## Operating model

This agent runs via GitHub MCP tools — not a local checkout or git CLI.
All file reads, writes, branches, and pull requests are executed through
the GitHub API. Worktree mechanics (`.claude/CLAUDE.md`, `docs/WORKTREES.md`)
do not apply. The discipline below is the API-equivalent contract.

---

## Rule 1 — Branch-first

Every file change lands on a dedicated branch, never directly on `main`.
Choose the branch kind before touching any file.
Follow the contract in [docs/BRANCHING.md](../docs/BRANCHING.md):

| Kind | Pattern | Use for |
|------|---------|---------|
| `culture/` | `culture/<country\|region\|staging\|release>` | Culture content in `regions/**` |
| `governance/` | `governance/<name>` | Governance paths (hooks, CI, validators, policy data) |
| `chore/` | `chore/<name>` | Tooling, scripts, documentation |
| `fix/` | `fix/<name>` | Corrections outside culture and governance |
| `feat/` | `feat/<name>` | Non-culture, non-governance features |

Culture slug must resolve against the on-disk `regions/` tree.
A typo does not silently widen scope — unknown slugs are rejected.
If a change spans two kinds, use two branches and two PRs.

---

## Rule 2 — Read before write

Before editing any file, read the current version to confirm the SHA
(required for the GitHub API update call) and to understand existing
structure. Never overwrite blindly.

---

## Rule 3 — PR before merge

All changes are proposed as pull requests. The human reviews before
merging. The agent does not self-merge unless explicitly instructed.

PR titles: `<kind>: <short imperative description>`  
PR body: what changed and why. No meta-commentary about tooling.

---

## Rule 4 — Commit message discipline

Imperative mood. Lowercase. Under 72 characters.  
No emojis. No "as an AI" language.

---

## Rule 5 — Respect the branch-scope contract

Branch name determines which paths are writable and which validators
run. Do not route culture changes through `chore/` or `fix/` to bypass
the Hofstede validator. Do not route governance changes through `chore/`
to bypass the governance-path guard.

The executable source of truth is `tests/branch_scope.py`.
This document is downstream of that file.

---

## Rule 6 — Capability scope

**Can do (via GitHub API):**
- Read any file, directory, commit, branch, tag, release
- Create branches and push file changes (single or multi-file commits)
- Open, update, and comment on pull requests
- Read and create issues

**Cannot do:**
- Run local scripts (`check_gaps.py`, `gap_status.py`, validators, etc.)
- Execute git CLI commands or worktree operations
- Access any local filesystem

---

*v0.1.0 - KAI Worlds*
