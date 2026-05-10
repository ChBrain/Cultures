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
- `culture/staging` - integration point for batched culture releases
- `feat/<name>` - other feature work (direct to main)
- `fix/<name>` - corrections to existing content
- `chore/<name>` - infrastructure, validation, documentation

## Branch Scope Guards

The pre-commit hook classifies every branch and enforces the matching scope:

| Branch kind | Pattern | May modify | Hofstede check |
|---|---|---|---|
| `main` | exact name `main` | nothing — direct commits forbidden | n/a |
| culture | regex `^culture/[a-z0-9][a-z0-9_-]*$` | `regions/**` + safe metadata files | yes (±10 gap) |
| other | anything else (`chore/*`, `fix/*`, `feat/*`, …) | anything **except** `regions/**` | no |

Culture branches use forward-slash naming: `culture/denmark`, `culture/staging`, etc. This anchors scope validation: `feat/culture-x`, `cultures/x`, and typos are all classified as `other` and blocked from `regions/`.

Safe metadata files allowed on culture branches alongside `regions/**`:
- `.validation-stamp` - proof of local validation
- `.bump-type` - version intent declaration
- `.gitignore`, `.editorconfig` - repository config

If your work spans both scopes, split it into two branches and open two PRs:
1. Push culture work: `git push origin culture/<country>`
2. Create a separate branch: `git checkout -b chore/<name>`
3. Make infrastructure changes there
4. Both PRs can merge independently

Hook rejection messages:
```
>>> ERROR: Culture branch can only modify regions/
>>> ERROR: Non-culture branch cannot modify regions/
```
Use `git reset` and split your changes.

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
