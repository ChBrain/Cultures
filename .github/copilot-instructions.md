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

## Branch naming

- `culture/<country>` - per-country culture work (e.g., `culture/denmark`)
- `culture/<region>` - per-region culture work (e.g., `culture/europe`)
- `culture/staging`, `culture/release` - integration points for batched culture releases
- `governance/<name>` - changes to the rules themselves: hooks, CI workflows, validators, branch-scope module, validator data sources
- `feat/<name>` - non-culture, non-governance feature work
- `fix/<name>` - corrections outside culture and governance
- `chore/<name>` - non-culture, non-governance tooling / docs

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

## Branch Scope Guards

The pre-commit hook classifies every branch and enforces the matching scope:

| Branch kind | Pattern | May modify | Hofstede check |
|---|---|---|---|
| `main` | exact name `main` | nothing — direct commits forbidden | n/a |
| culture (country) | `culture/<country>` | `regions/<region>/<country>/**` + safe metadata | yes (±10 gap) |
| culture (region) | `culture/<region>` | `regions/<region>/**` + safe metadata | yes (±10 gap) |
| culture (world) | `culture/staging`, `culture/release` | `regions/**` + safe metadata | yes (±10 gap) |
| governance | `governance/<name>` | governance paths + safe metadata | n/a |
| other | anything else (`chore/*`, `fix/*`, `feat/*`, …) | anything **except** `regions/**` **and except** governance paths | n/a |

### Data vs. governance

Culture data lives under `regions/<region>/<country>/`. **Governance** — the code and data that defines and enforces repository rules — lives in fixed paths and is walled off from non-governance branches so a generic `chore/refactor` cannot silently weaken the gates that protect culture content.

Governance paths (single source of truth: `tests/branch_scope.py` `GOVERNANCE_DIR_PREFIXES` + `GOVERNANCE_GLOB_PATTERNS`):

- `.githooks/**` — local pre-commit enforcement
- `.github/workflows/**` — CI enforcement
- `tests/branch_scope.py` — the rules themselves
- `tests/test_*.py` — tests that pin the rules
- `tests/validate_*.py` — every validator script
- `tests/requirements.txt`, `tests/language_exceptions.txt` — validator config
- `scripts/validate.py`, `scripts/validate_general.py` — orchestrator + helper
- `scripts/setup-hooks.sh`, `scripts/setup-hooks.bat` — hook installation
- `scripts/audit_readme_bands.py` — canonical Hofstede band contract
- `scripts/update_hofstede_readme.py` — deterministic README Hofstede-tables updater
- `data/hofstede_denylist.yaml`, `data/hofstede_keywords.py` — validator inputs
- `data/hofstede_scores.json` — Hofstede Insights reference dataset
- `data/hofstede_bag_loader.py` — bag-validation infrastructure
- `data/language_policy.yaml` — per-language policy data
- `data/phrase_denylist.txt` — plagiarism phrase denylist

### Culture slug resolution

Culture branches use forward-slash naming, and the slug after the slash is resolved against the on-disk `regions/` tree. The slug must match either a known country folder (`regions/<region>/<slug>/`), a known region folder (`regions/<slug>/`), or one of the world-level integration names (`staging`, `release`). A typo or unknown slug fails fast instead of silently widening scope. Near-misses like `feat/culture-x`, `cultures/x`, and `culture/Denmark` (uppercase) are all classified as `other` and blocked from `regions/`.

Per-country protection means a `culture/germany` branch cannot touch Denmark even though both live under `regions/europe/`. If you need to span multiple countries in a single PR, use `culture/<region>` (e.g. `culture/europe`) or the world-level `culture/staging`.

### Safe metadata

Files allowed on culture **and** governance branches alongside their primary scope:
- `.validation-stamp` - proof of local validation
- `.bump-type` - version intent declaration
- `.gitignore`, `.editorconfig` - repository config
- `data/hofstede_bag_locks.yaml` - bag-lock index (carved out for bag migration PRs)
- `data/v2_migrated_countries.txt` - per-country v2 opt-in (carved out for v2 migration PRs)

### Splitting work across scopes

If your work spans two scopes, split it into separate branches/PRs — each PR can merge independently:
1. Culture content: `git checkout -b culture/<country>`
2. Validator/hook/workflow changes: `git checkout -b governance/<name>`
3. General tooling/docs: `git checkout -b chore/<name>`

Hook rejection messages:
```
>>> ERROR: Culture branch out of scope (allowed: regions/<region>/<country>/**)
>>> ERROR: Unknown culture slug
>>> ERROR: Governance branch out of scope
>>> ERROR: Non-culture/non-governance branch out of scope
```
Use `git reset` and move the offending files to the right branch kind.

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

## L0-stamp-check Gate

GitHub Actions **L0-stamp-check** verifies that `.validation-stamp` exists in your commit. This proof that you ran local validation before pushing - it prevents accidental commits from bypassing checks.

If you see "L0-stamp-check FAILED":
- Your `.validation-stamp` is missing
- This means local validators didn't run or didn't pass
- Recovery: `git reset HEAD~1`, fix issues, commit again

## Validators run at each stage

| Stage | Tool | When | Includes Hofstede? |
|-------|------|------|---|
| Local pre-commit | `.githooks/pre-commit` | Before every `git commit` on **culture/*** | YES |
| Local pre-commit | `.githooks/pre-commit` | Before every `git commit` on **chore/*, fix/*** | NO |
| L0-stamp-check | CI job | Every PR, every push to main | - |
| L1-L4 validation | CI jobs (chained) | Every PR, when L0 passes | Base validation only |
| L1-L7 validation | CI jobs (chained) | PR to **culture/staging**, when L0 passes | Includes Hofstede (L5-L7) |

## Validation Chain

**Culture Branch Path (culture/<name> → culture/staging → main):**
- Local: L1-L4 + **Hofstede** (pre-commit hook enforces alignment)
- CI on culture/staging: L1-L7 full validation + L0-stamp-check
- CI on main (from staging): verify scope stayed in regions/, no scope creep

**Infrastructure Branch Path (chore/*, fix/*, feat/* non-culture → main):**
- Local: L1-L4 only, no Hofstede (pre-commit hook skips)
- CI on main: L1-L4 validation + L0-stamp-check
- Hofstede not required (infrastructure/metadata don't carry cultural dimensions)

## Protection

- ✅ Pre-commit hook prevents main commits locally
- ✅ Pre-commit hook prevents culture-branch scope creep (non-regions/ changes)
- ✅ L0-stamp-check prevents commits without proof of local validation
- ✅ GitHub branch protection requires PR + passing checks before merge
- ✅ All commits to main must pass full CI validation

---

*v0.2.0 - KAI Worlds*
