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
- `data/hofstede_denylist.yaml`, `data/hofstede_keywords.py` — validator inputs
- `data/hofstede_scores.json` — Hofstede Insights reference dataset
- `data/hofstede_bag_loader.py` — bag-validation infrastructure

### Culture slug resolution

Culture branches use forward-slash naming, and the slug after the slash is resolved against the on-disk `regions/` tree. The slug must match either a known country folder (`regions/<region>/<slug>/`), a known region folder (`regions/<slug>/`), or one of the world-level integration names (`staging`, `release`). A typo or unknown slug fails fast instead of silently widening scope. Near-misses like `feat/culture-x`, `cultures/x`, and `culture/Denmark` (uppercase) are all classified as `other` and blocked from `regions/`.

Per-country protection means a `culture/germany` branch cannot touch Denmark even though both live under `regions/europe/`. If you need to span multiple countries in a single PR, use `culture/<region>` (e.g. `culture/europe`) or the world-level `culture/staging`.

### Safe metadata

Files allowed on culture **and** governance branches alongside their primary scope:
- `.validation-stamp` - proof of local validation
- `.bump-type` - version intent declaration
- `.gitignore`, `.editorconfig` - repository config
- `data/hofstede_bag_locks.yaml` - bag-lock index (carved out for bag migration PRs)

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

*v0.1.0 - KAI Worlds*
