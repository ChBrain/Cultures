# Cultures - Copilot Instructions

## Git workflow (MANDATORY)

**Before any file edit:**
1. Run `git branch --show-current` to confirm the current branch
2. If on `main`, STOP - create a feature branch first
3. Only commit changes when on a feature branch
4. Never commit or push directly to `main`

## Setup (First Time)

Enable local validation by configuring git hooks:

**On macOS/Linux:**
```bash
scripts/setup-hooks.sh
git config core.hooksPath .githooks
```

**On Windows (PowerShell):**
```powershell
.\scripts\setup-hooks.bat
git config core.hooksPath .githooks
```

This installs `.githooks/pre-commit` which validates every commit locally before it reaches GitHub.

## Branches

**See [docs/BRANCHING.md](../docs/BRANCHING.md) for the complete branch-kind contract.**

**See [.worktree/WORKTREES.md](../.worktree/WORKTREES.md) for the canonical worktree workflow.**

**See [docs/LIFECYCLE.md](../docs/LIFECYCLE.md) for the shared chapter flow (plan, code, build, test, release, deploy, operate, monitor).**

That document is the single source of truth for all branch types, allowed paths, scope rules, and governance enforcement. It is mirrored from the executable classifier in [`tests/branch_scope.py`](../tests/branch_scope.py).

Do not duplicate branch-kind rules in this file. When in doubt, follow [`docs/BRANCHING.md`](../docs/BRANCHING.md) and the executable checks in [`tests/branch_scope.py`](../tests/branch_scope.py).

**Before `git checkout -b`, run the advisor.** `python tests/branch_scope.py advise --op <operation>` routes by operation (not file type) and prints the branch name, required base, and create command. `python tests/branch_scope.py advise --files <paths>` reports a change that must be split across branches. See [`docs/BRANCHING.md`](../docs/BRANCHING.md) "Pre-flight: ask the advisor".

## Cultures v2 Schema

Every country has **8 canonical kinds**, mapped to the **5 KAI structural types**. The mapping is enforced by validators that read a footer declaration on every content file.

### The 8 kinds

| File pattern | Cultures kind | KAI structural type |
|---|---|---|
| `culture_<adj>_language_<slug>.md` | Language | position |
| `culture_<adj>_history_<slug>.md` | History | piece |
| `culture_<adj>_position.md` | Position | position |
| `culture_<adj>_process_<slug>.md` | Process | process |
| `culture_<adj>_piece_<slug>.md` | Piece | piece |
| `culture_<adj>_place_<slug>.md` | Place | place |
| `culture_<adj>_male_<name>.md` | Male persona | persona |
| `culture_<adj>_female_<name>.md` | Female persona | persona |

`<adj>` is the cultural adjective (e.g. `german`, `dutch`). `<slug>` is a short kebab-/snake-case identifier; `<name>` is a given name.

### khai declaration footer

Every `culture_*.md` ends with a single-line marker declaring its KAI structural type:

```
*khai: <type>*
```

where `<type>` is exactly one of: `process`, `position`, `piece`, `place`, `persona`.

The filename token and the footer must agree. Examples:

| Filename | khai footer |
|---|---|
| `culture_german_language_german.md` | `*khai: position*` |
| `culture_german_history_grundgesetz.md` | `*khai: piece*` |
| `culture_german_position.md` | `*khai: position*` |
| `culture_german_process_einkaufen.md` | `*khai: process*` |
| `culture_german_piece_bauhaus.md` | `*khai: piece*` |
| `culture_german_place_brandenburg_gate.md` | `*khai: place*` |
| `culture_german_male_christian.md` | `*khai: persona*` |
| `culture_german_female_brigitte.md` | `*khai: persona*` |

Validators read both surfaces and reject any mismatch. The footer drives KAIHACKS `khai-tests` v0.1.6 component detection; the filename drives the Cultures-side completeness check (`tests/test_completeness.py`).

### Full footer (v2)

The khai line is one of three italicized footer lines every `culture_*.md` carries in v2-migrated countries. The full block, separator above:

```
---
*hofstede: aggregate in [README.md](README.md).*
*khai: <type>*
*<YYYY-MM-DD> | KAI HACKS AI | v<X.Y.Z> | CC-BY-NC-4.0*
```

- The **hofstede line** is the aggregate-score sentinel. Per-file Hofstede scores are forbidden; the README is the single source of truth. The legacy form `*Hofstede signal: this file contributes to the culture's aggregate score. Declared dimensions live in [README.md](README.md).*` is accepted during the v2 rollout (per PR #130); canonical is the shorter `hofstede:` form above.
- The **khai line** declares the KAI structural type (see the previous subsection for the filename ↔ footer agreement table).
- The **IP safeguard line** carries four pipe-separated fields: the last-edit date in ISO 8601, the project owner (`KAI HACKS AI`), the KAIWorlds release version at last edit, and the license shorthand. The authoritative license lives in the repo `LICENSE` file at the root.

Authoritative spec: [`ARCHITECTURE.md`](../ARCHITECTURE.md) > Footer.

### Per-country v2 opt-in

The v2-strict validator runs only against countries listed in `data/v2_migrated_countries.txt` (one slug per line, blank lines and `#` comments ignored). Countries not on the list run the legacy v1 rules and stay readable in the meantime.

A migration PR (`culture/<country>`) adds its slug to that file in the same commit that:
- renames `persona_*` to `male_*` / `female_*`
- renames `piece_*` to `history_*` where the file is actually history (a pivotal moment, not an artifact)
- adds an authentic `piece` if the old `piece_*` doubled as history
- adds the 3-line v2 footer (hofstede sentinel, khai declaration, IP safeguard line) to every `culture_*.md`
- updates the audit table in `README.md` to the canonical 8-kind order via `scripts/update_hofstede_readme.py`

`data/v2_migrated_countries.txt` is in `SAFE_PATTERNS`, so culture branches are allowed to edit it. Once every developed country is on the list, stage 4 deprecates the opt-in mechanism and the validator becomes unconditionally v2.

### Hofstede band contract

Canonical thresholds (pinned by `scripts/audit_readme_bands.py` + `tests/test_audit_readme_bands.py`):

| Score range | Band |
|---|---|
| 0-39 | Low |
| 40-69 | Moderate |
| 70-100 | High |

"Medium" is an accepted prose alias for "Moderate" (the audit normalizes for equivalence but surfaces the non-canonical word in the `declared` column). README band labels and any prose mentions like `**Low PDI + High IDV:**` must agree with each dimension's score.

### Language policy

`data/language_policy.yaml` is the single source of truth: registered languages, prose sections to check, span threshold. Each culture's `README.md` declares which registered languages it uses via `**Language(s):** <name>[, <name>...]`. Typos fail loudly (no silent english-only fallback).

**Proper-noun exceptions** are layered:

- **Global** (`tests/language_exceptions.txt`): proper nouns allowed everywhere. Governance-tracked.
- **Per-culture** (`regions/<region>/<country>/language_exceptions.txt`): country-specific. Lives with the culture content, so contributors add country-specific names alongside the culture PR; no separate `governance/*` change needed.

**Quoted source material**: wrap in markdown blockquotes (`> ...`). Blockquoted lines are stripped before detection, so faithful citations in any language pass cleanly.

**Useful CLIs:**

```bash
# What languages does this repo allow?
python3 tests/validate_language.py --list-repo-languages

# What does each country declare?
python3 tests/validate_language.py --list-country-languages

# Are all READMEs consistent with the registry?
python3 tests/validate_language.py --check-readmes-only

# Why is this specific file failing? (per-section span trace)
python3 tests/validate_language.py --explain regions/europe/germany/culture_*.md
```

**Failure messages** carry a fix ladder (cheapest first):

```
FAIL regions/europe/germany/culture_german_persona_brigitte.md:
  German span (18 words) in ## Shown: 'Die Wuerde des Menschen ist unantastbar...'
  verdict: if a quoted source, wrap as `> ...` blockquote (skipped);
           if proper nouns, add proper nouns to regions/europe/germany/language_exceptions.txt;
           otherwise rewrite in english
```

**Strategy and roadmap**: see [LANGUAGES.md](../LANGUAGES.md) for the full enablement tier model, current enabled languages, pre-flight checklist, and macro-language priority roadmap.

## Workflow

Use canonical workflow docs instead of repeating branch logic here:

- Branch kinds, allowed paths, and PR target rules: [`docs/BRANCHING.md`](../docs/BRANCHING.md)
- Worktree lifecycle and commands: [`/.worktree/WORKTREES.md`](../.worktree/WORKTREES.md)
- Shared delivery chapters: [`docs/LIFECYCLE.md`](../docs/LIFECYCLE.md)

Validation enforcement remains hook-first and CI-backed:

- Local pre-commit gate: `.githooks/pre-commit`
- Server-side PR/base and scope gate: `.github/workflows/pr-gate.yml`
- Validation chain: `.github/workflows/validate.yml`

---

*v0.2.0 - KAI Worlds*
