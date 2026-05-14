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

That document is the single source of truth for all branch types, allowed paths, scope rules, and governance enforcement. It is mirrored from the executable classifier in [`tests/branch_scope.py`](../tests/branch_scope.py).

Quick reference:
- `culture/<country>` - culture content (scope-locked to that country)
- `culture/<region>` - cross-country culture work
- `culture/staging`, `culture/release` - all culture content (regions/**)
- `governance/<name>` - validators, hooks, workflows
- `chore/<name>`, `fix/<name>`, `feat/<name>` - general tooling (not regions/**, not governance)

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

### Culture Work (culture/<country> or culture/<region>)

1. **Create culture branch**
   ```bash
   git checkout -b culture/netherlands
   ```

2. **Make changes only to culture files** in `regions/<region>/<country>/`

3. **Commit locally** - Pre-commit hook automatically:
   - ✓ Strips UTF-8 BOM from PowerShell files
   - ✓ Prevents direct commits to `main`
   - ✓ **Blocks commits with non-regions/ changes** (culture-only guard)
   - ✓ Runs L1-L4 validators (general format, language policy, sections, links, completeness)
   - ✓ **Runs Hofstede validation** (dimension alignment ±10 tolerance)
   - ✓ Writes `.validation-stamp` (git tree hash) on success
   - ✗ Rejects commits if validation fails

   ```bash
   git add regions/europe/netherlands/culture_*.md
   git commit -m "feat: add Netherlands culture with Hofstede alignment"
   ```

4. **Push to remote**
   ```bash
   git push -u origin culture/netherlands
   ```

5. **Open PR to `culture/staging`** - Culture content gets staged for review
   - GitHub CI runs full validation (L0-L4f)
   - Culture reviewers can batch-test before main merge
   - All checks must pass

6. **Merge to `culture/staging`** - Queues for release

7. **Release cycle** - When ready to deploy:
   - Create PR from `culture/staging` → `main`
   - Merge to `main`
   - Create GitHub release tag (v0.X.Y)
   - Workflow deploys

### Infrastructure Work (chore/*, fix/*)

1. **Create non-culture branch**
   ```bash
   git checkout -b chore/validation-script
   ```

2. **Make changes to scripts, tooling, documentation** (anywhere outside regions/)

3. **Commit locally** - Pre-commit hook validates as before
   - ✓ Strips UTF-8 BOM from PowerShell files
   - ✓ Prevents direct commits to `main`
   - ✓ **Blocks commits that touch `regions/`** (non-culture branches stay outside culture content)
   - ✓ Runs L1-L4 validators only (no Hofstede)
   - ✓ Writes `.validation-stamp`
   - ✗ Rejects commits if validation fails

4. **Open PR directly to `main`** - Infrastructure PRs bypass staging
   - Approved and merged independently
   - Does not block culture releases

## Validation stamp gate

GitHub Actions **cultures - Validation stamp gate** verifies that `.validation-stamp` exists in your commit. This proof that you ran local validation before pushing - it prevents accidental commits from bypassing checks.

If you see "cultures - Validation stamp gate FAILED":
- Your `.validation-stamp` is missing
- This means local validators didn't run or didn't pass
- Recovery: `git reset HEAD~1`, fix issues, commit again

## Validators run at each stage

| Stage | Tool | When | Includes Hofstede? |
|-------|------|------|---|
| Local pre-commit | `.githooks/pre-commit` | Before every `git commit` on **culture/*** | YES |
| Local pre-commit | `.githooks/pre-commit` | Before every `git commit` on **chore/*, fix/*** | NO |
| cultures - Validation stamp gate | CI job | Every PR, every push to main | - |
| L1-L4 validation | CI jobs (chained) | Every PR, when L0 passes | Base validation only |
| L1-L7 validation | CI jobs (chained) | PR to **culture/staging**, when L0 passes | Includes Hofstede (L5-L7) |

## Validation Chain

**Culture Branch Path (culture/<name> → culture/staging → main):**
- Local: L1-L4 + **Hofstede** (pre-commit hook enforces alignment)
- CI on culture/staging: L1-L7 full validation + cultures - Validation stamp gate
- CI on main (from staging): verify scope stayed in regions/, no scope creep

**Infrastructure Branch Path (chore/*, fix/*, feat/* non-culture → main):**
- Local: L1-L4 only, no Hofstede (pre-commit hook skips)
- CI on main: L1-L4 validation + cultures - Validation stamp gate
- Hofstede not required (infrastructure/metadata don't carry cultural dimensions)

## Protection

- ✅ Pre-commit hook prevents main commits locally
- ✅ Pre-commit hook prevents culture-branch scope creep (non-regions/ changes)
- ✅ cultures - Validation stamp gate prevents commits without proof of local validation
- ✅ GitHub branch protection requires PR + passing checks before merge
- ✅ All commits to main must pass full CI validation

---

*v0.2.0 - KAI Worlds*
