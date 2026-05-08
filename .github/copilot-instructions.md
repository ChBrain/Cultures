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

- `feat/<name>` - new culture, new content, rebalancing
- `fix/<name>` - corrections to existing content
- `chore/<name>` - infrastructure, validation, documentation

## Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feat/my-change
   ```

2. **Make changes** to culture files in `regions/<region>/<country>/`

3. **Commit locally** - Pre-commit hook automatically:
   - ✓ Strips UTF-8 BOM from PowerShell files
   - ✓ Prevents direct commits to `main`
   - ✓ Runs L1-L4 validators (general format, language policy, sections, links, completeness)
   - ✓ Writes `.validation-stamp` (git tree hash) on success
   - ✗ Rejects commits if validation fails

   ```bash
   git add regions/europe/country/culture_*.md
   git commit -m "feat: rewrite country culture with Hofstede alignment"
   ```

4. **Push to remote**
   ```bash
   git push -u origin feat/my-change
   ```

5. **Open PR** - GitHub CI runs full validation (L0-L4f):
   - L0: Verifies `.validation-stamp` exists (proof local validation passed)
   - L1-L4: Re-runs all validators in CI
   - All checks must pass before merge

6. **Merge to main** - Only via PR (branch protection enforced)

## L0-stamp-check Gate

GitHub Actions **L0-stamp-check** verifies that `.validation-stamp` exists in your commit. This proof that you ran local validation before pushing - it prevents accidental commits from bypassing checks.

If you see "L0-stamp-check FAILED":
- Your `.validation-stamp` is missing
- This means local validators didn't run or didn't pass
- Recovery: `git reset HEAD~1`, fix issues, commit again

## Validators run at each stage

| Stage | Tool | When |
|-------|------|------|
| Local pre-commit | `.githooks/pre-commit` | Before every `git commit` |
| L0-stamp-check | CI job | Every PR, every push to main |
| L1-L4f validation | CI jobs (chained) | Every PR (if L0 passes) |

## Protection

- ✅ Pre-commit hook prevents main commits locally
- ✅ L0-stamp-check prevents commits without proof of local validation
- ✅ GitHub branch protection requires PR + passing checks before merge
- ✅ All commits to main must pass full CI validation

---

*v0.1.0 - KAI Worlds*
