# Cultures repo structure: refactor plan

Status: draft (design captured, not yet executed).
Trigger: PR #103 friction over `.github/copilot-instructions.md` ownership, plus a growing pattern of file-by-file additions to `GOVERNANCE_GLOB_PATTERNS`.

## Why

- `branch_scope.py` carries a 14-entry glob list (`GOVERNANCE_GLOB_PATTERNS`) plus a `SAFE_PATTERNS` carve-out because top-level folders mix concerns. The type system can't be expressed in folder prefixes alone, so it leaks into a per-file table.
- **Live evidence of the friction (as of plan revision):**
  - **PR #103** (`governance/language-onboarding-flow`) had to be split. The validator + tests stay on #103; `.github/copilot-instructions.md` moved to **PR #110** (`chore/language-policy-docs`). The #110 body says verbatim: *"Split from that PR because `.github/copilot-instructions.md` is not a governance path."*
  - **Commit `0cbfe82`** (during the #101 Phase 1 merge) had to first register `data/language_policy.yaml` in `GOVERNANCE_GLOB_PATTERNS` before the governance PR could legitimately add the file. The commit message: *"CI on the parent PR flagged both branch-scope checks failing because data/language_policy.yaml wasn't in GOVERNANCE_GLOB_PATTERNS."* This is the same friction one level deeper — the glob list grows by hand, one file per governance feature.
- **Gap surfaced during review (PR #109):** `engine/` is currently unprotected. A `chore/*` branch can edit `engine/claude/instructions.md` (and any other engine file) because `engine/` is neither under `regions/` nor in any governance pattern. See "Engine currently unprotected" below.
- Goal: realign the source tree so **folder = concern = branch kind**, retire the glob list, and give every future case like #103 and #109 a principled answer.

## Genre (carry to other repos)

Cultures is a **content pack with deployment manifests**, not a standard `src/tst/doc` application. The contract that generalizes:

1. **Source tree is author-organized; artifact is flat-or-remapped.** Folder hierarchy does not survive the build. Filename schema (e.g., `culture_<adjective>_<kind>_<slug>.md`) does the namespacing work that folders do in standard projects.
2. **Multiple artifacts from one source via manifests.** Each manifest is a curated selection (world, region, DACH, NATO, ...). Filenames must be globally unique across any possible selection, not just per-zip.
3. **Validation-driven authoring.** Reference data defines the standard; validators check content against it; tightening the standard forces content rework (data &rarr; tests fail &rarr; regions must change).
4. **Author-locality co-location.** Shipped content and its co-located non-shipped meta live together in the author's working folder. Build filters at composition.
5. **Branch ownership is folder-grain; build filtering is filename-grain.** Two orthogonal axes that have been conflated in the current `branch_scope.py`.

## Cultures-specific overlays

- Author concern = a country.
- **Language-locality invariant**: country folder = native-language `culture_*.md` + English bridge files (`README.md`, `REFERENCES.md`). This is why co-location wins over standard `src/tst/` separation &mdash; the country folder is a language island, and validation fixtures (`hofstede_bag.yaml`, `hofstede_decisions.md`) live inside it because pulling them out would fragment the island without benefit (flat-deploy doesn't care where they live in source).
- Filename schema: `culture_<adjective>_<kind>_<slug>.md` where `<kind>` &isin; {persona, position, piece, place, process, language}.
- Engine layer: cross-cultural primitives (no `culture_` prefix, e.g. `position_male.md`, `process_world_is_spinning.md`) + per-agent runtime config (`engine/{claude,copilot,gemini}/`, including `engine/claude/instructions.md` and similar).
- Reference data: Hofstede scores, denylists, language policy.
- Deployment manifests: world, region, alliance groupings (DACH, NATO, ...). Not in repo yet.

## Two orthogonal axes (formalized)

| Axis | Grain | Determines |
|---|---|---|
| Branch-ownership | folder prefix | who can edit (PR-time gate) |
| Ships-to-deploy | filename pattern, modulated by manifest | what reaches the LLM (build-time filter) |

These look similar; they are not the same. Past confusion in `branch_scope.py` traces to treating them as one.

## Engine currently unprotected (gap)

Under current `branch_scope.py`:
- `regions/**` &rarr; restricted to `culture/*` branches.
- Governance paths (workflow, hooks, validators, data registry) &rarr; restricted to `governance/*` branches.
- **Everything else, including `engine/**`** &rarr; fall through to "other"; editable from any `chore/*` / `fix/*` / `feat/*` / `claude/*` branch.

PR #109 (`chore/claude-instructions`) is editing `engine/claude/instructions.md` &mdash; the agent runtime config &mdash; under this fall-through. The current rules don't prevent a non-engine PR from rewriting Claude's instructions, Copilot's instructions, the position/process primitives, or any per-agent runtime file. The same is true for `manifests/` (when introduced) and any other product-side directory.

This gap exists because the original branch_scope.py was scoped to protect `regions/` (culture content) and the gates that check it, leaving `engine/` and any new product directory as a default-allow zone. The fix is folder-grain: add `engine/*` as a recognized kind owning `engine/**`, and make all non-listed product directories default-deny for unrelated kinds.

## Recent related work on main (since plan was first drafted)

| Merge | What it did | Effect on this plan |
|---|---|---|
| **#101** Phase 1 language policy YAML | Added `data/language_policy.yaml`; registered it in `GOVERNANCE_GLOB_PATTERNS` via commit `0cbfe82` | Live instance of the file-by-file glob friction. Strengthens the case for folder-grain. |
| **#102** Loop E | Rewrote five `validate_*.py` standalone scripts as parametrized `test_*.py` pytest files | `tests/` is now mostly pytest; the remaining `validate_*.py` files are CLI tools, not test files. Migration step 3 must reflect this. |
| **#108** Loop F | Converted `test_branch_scope.py` and `test_hook_scope_e2e.py` from unittest to pytest (146 tests) | "Lock tests" in this plan now means pytest fixtures + `@pytest.mark.parametrize`, not unittest TestCase. |
| **#98** L4g audit mode | Validators enter audit mode when `data/hofstede_scores.json` changes | Partially implements the data &rarr; regions coupling that this plan named `standard/*`. See open question 2. |

## Current layout (what we have)

```
.github/                 mixed: workflows (delivery), CODEOWNERS (delivery), copilot-instructions.md (steering)
.githooks/               delivery
data/                    delivery (Hofstede reference, language policy, denylists) -- misnamed; not product data
engine/                  product, ships  [currently unprotected -- see "Engine currently unprotected"]
  claude/ copilot/ gemini/
  position_*.md, process_*.md, stack.md
regions/                 product, ships (filtered)
  <region>/<country>/
    culture_*.md           ships
    README.md, REFERENCES.md  ships (English bridges)
    hofstede_bag.yaml      co-located meta, doesn't ship
    hofstede_decisions.md  co-located meta, doesn't ship
scripts/                 mixed: setup-hooks + validate.py (delivery), scaffold_country.py + audit-* + normalize-* + prose_review.py (authoring tooling)
tests/                   mostly pytest after #102, #108:
                           test_*.py: parametrized validators + harness + branch_scope test
                           validate_*.py: remaining CLI tools (validate_language.py, validate_pr_*.py, etc.)
                           branch_scope.py: gate logic
                           language_exceptions.txt, requirements.txt: fixtures + config
docs/migration/          product-meta docs
check_gaps.py, compare_positions.py, gap_status.py, show_scores.py    loose maintainer tools at root
README.md, ARCHITECTURE.md, METHODOLOGY.md, REFERENCES.md, LICENSE    product-meta docs
.bump-type, .validation-stamp, .pr-body.md, .gitignore, .gitattributes    delivery state + git config
```

The mixed folders (`scripts/`, `tests/`, `.github/`) are the source of the glob list. The unprotected `engine/` is the gap.

## Target layout

```
engine/         cross-cultural primitives + per-agent runtime config  [PROTECTED under engine/*]
  claude/
  copilot/
  gemini/
  position_*.md, process_*.md, stack.md
manifests/      deployment selectors (world, region, DACH, NATO, ...)  [NEW; PROTECTED under engine/*]
regions/        author-organized country content (language islands)    [PROTECTED under culture/*]
  <region>/
    <country>/
      culture_*.md            ships
      README.md, REFERENCES.md  ships (English bridges)
      hofstede_bag.yaml       co-located meta, doesn't ship
      hofstede_decisions.md   co-located meta, doesn't ship
tools/          authoring helpers (scaffold, audit, normalize, prose_review, analysis)
                [consolidates current scripts/ authoring half + root .py]
validation/     validators, gates, fixtures, branch_scope
                [consolidates current tests/ + data/ + scripts/ delivery half]
docs/           README, ARCHITECTURE, METHODOLOGY, REFERENCES, migration notes
.github/        forced-path infrastructure (CI workflows, CODEOWNERS, copilot-instructions.md as mirror)
.githooks/      forced-path git hooks
```

## Branch-kind type system

| Branch kind | Owns prefix(es) |
|---|---|
| `culture/*` | `regions/**` |
| `engine/*` *(new)* | `engine/**`, `manifests/**` |
| `governance/*` | `validation/**`, `tools/**`, `docs/**`, `.github/**`, `.githooks/**`, root infra files |
| `standard/*` *(new, optional &mdash; see open Q2)* | `validation/data/**` + `regions/**/hofstede_*.{yaml,md}` &mdash; for reference-driven coupled realignments |
| `main` | nothing (no-commits gate, separate) |

Five prefix rules. No glob list.

## What this does to PR #103

`.github/copilot-instructions.md` is editing-time tooling that steers Copilot when authors edit the repo. It doesn't ship.

Under the new layout it becomes the **forced-path mirror** of an authored file under `engine/copilot/` (the canonical source-of-truth). Maintained in lockstep by `engine/*` PRs &mdash; or by `governance/*` PRs if the file stays classified as delivery-side steering rather than product-side runtime config. Either way, the carve-out ("docs, not workflows/") disappears and the file's authorship is principled, and PR #103 + PR #110 collapse back into one PR.

The decision between `engine/copilot/` (product) and `validation/steering/copilot/` (delivery) depends on whether the file's text is the same content Copilot uses at runtime in deployed scaffolds, or whether it's only used at editing time. To verify: read `engine/copilot/*` and compare with `.github/copilot-instructions.md`.

## Migration steps

Each step is a single `governance/*` PR. Order matters; CI must stay green between steps.

1. **Decide open questions** (see below) before any moves.
2. **Hotfix: add `engine/*` as a branch kind owning `engine/**`** *(optional; can run before or as part of the larger restructure)*. Closes PR #109's gap immediately. 20-line change to `branch_scope.py` plus pytest fixtures asserting the new prefix.
3. **Add new branch kinds** (`engine/*` if not hotfixed in step 2, optionally `standard/*`) to `branch_scope.py` as recognized prefixes with empty allowed-paths. Lock tests assert.
4. **Move `tests/` &rarr; `validation/`.** Update CI workflow paths, hook paths, all imports. Single PR. Note: most contents are pytest after #102/#108; preserve `tests/` &rarr; `validation/` import paths via package layout.
5. **Move `data/` &rarr; `validation/data/`** (or `validation/reference/`). Update imports in validators. Single PR.
6. **Split `scripts/`**: delivery half (`setup-hooks.*`, `validate.py`, `validate_general.py`) &rarr; `validation/`; authoring half (`scaffold_country.py`, `deploy_culture.py`, `prose_review.py`, `audit-germany.py`, `normalize-germany.py`, `audit_readme_bands.py`, `findings.py`) &rarr; `tools/`. Single PR.
7. **Move root analysis tools** (`check_gaps.py`, `compare_positions.py`, `gap_status.py`, `show_scores.py`) &rarr; `tools/`. Single PR.
8. **Introduce `manifests/`** as an empty top-level with a placeholder README. First manifest landed in a follow-up `engine/*` (or `manifests/*`) PR.
9. **Reclassify `.github/copilot-instructions.md`** as a generated/mirrored file with source-of-truth under `engine/copilot/` (or `validation/steering/copilot/`, pending the verification above). Add a CI step to verify mirror is in sync.
10. **Retire `branch_scope.py` glob list.** Replace with prefix-only rules. Update all `test_branch_scope.py` pytest fixtures + parametrize assertions.
11. **Update `ARCHITECTURE.md`** to document the new layout and the two-axis model.

Order constraints: 3 before 4-7; 4-7 before 10; 10 before any new branch kind PR can usefully exercise the new rules. Step 2 (hotfix) is independent and can land at any time.

## Open questions to resolve before migration

1. **Manifests location**: `manifests/` at root (first-class), or `engine/manifests/` (engine-internal)?
2. **`standard/*` branch kind vs L4g audit mode**: PR #98 already implements audit mode when `data/hofstede_scores.json` changes (at the validator level). Does `standard/*` (PR-name-level labeling) add value over L4g, or is it redundant? Options:
   - Adopt `standard/*` as PR-time label; keep L4g as validator-level fallback. Most explicit.
   - Drop `standard/*`; rely on L4g and culture/* follow-ups. Less ceremony.
   - Generalize L4g's pattern: any data file with a registered downstream impact triggers audit mode for the affected paths.
3. **`validation/data/` naming**: `data/`, `reference/`, `fixtures/`, or `standard/`? The name should signal "reference inputs to validators, not product data".
4. **`copilot-instructions.md` true classification**: engine (runtime) or delivery-side steering (editing-time)? Verify against `engine/copilot/*`.
5. **Country-folder English bridge files** (`README.md`, `REFERENCES.md`): any special treatment needed in `branch_scope.py`, or does folder-grain ownership of `regions/<country>/**` cover them cleanly?
6. **In-flight PRs**: at time of writing, open PRs are #100 (culture/spain), #103-#107 (culture/* + governance/*), #109 (chore/claude-instructions on engine/), #110 (chore/language-policy-docs split). Restructure timing should land most of these first; #109 and #110 specifically exercise the gaps this plan closes.
7. **Engine hotfix timing**: do step 2 (engine/* as a branch kind) as a separate ahead-of-restructure PR to close PR #109's gap now, or fold into the larger restructure? Doing it ahead means PR #109 may need rebasing; doing it later means engine/ stays open-edit until the restructure lands.

## Risk and trigger

- **Risk**: every in-flight PR rebases against moved paths. CI workflow YAML and hooks reference `tests/`, `data/`, `scripts/` &mdash; must update in lockstep with each move PR. `git log --follow` works but history is path-confused for weeks.
- **Trigger**: pick a quiet moment with few in-flight PRs. Migration can happen incrementally (one PR per step above) over a week, not as a big-bang. The engine/* hotfix (step 2) can run independently before the moments are quiet enough for the bigger moves.

## What this gives you

- Folder-grain branch ownership: 5 prefix rules instead of a glob table.
- `.github/copilot-instructions.md` and similar forced-path mirrors get a principled home; PR #103 + #110 stop needing to split.
- `engine/` is protected; PR #109's gap closes.
- The genre contract (above) is reusable in KAIHACKS and future content-pack repos.
- Validation reference data (`data/`) is named accurately as delivery-side, not product.
- Authoring tools (`scaffold_country.py`, etc.) get a home that matches their role.
- The two-axis model (branch-ownership vs ships-to-deploy) is documented and won't be re-conflated.

---

Session: https://claude.ai/code/session_01WLXjruMPTCScGpY348YuF1
