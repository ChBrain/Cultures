# Cultures branching — introduce `test/*` and `data/*` as TDD-parallel kinds

*Migration plan. Stepwise rollout of two new branch kinds. Each phase is one
small PR; pause for review between phases.*

## Changes on `main` since planning started (reviewed 2026-05-17)

`origin/main` advanced ~80 commits. Relevant deltas, and how the plan absorbs them:

- **`docs/LIFECYCLE.md` is NEW** (PR #202). It documents the exact `plan → code → build → test → release → deploy → operate → monitor` lifecycle this plan's rationale rests on, and a local-vs-CI "validation matrix". It *defers branch-kind choice to BRANCHING.md* — so adding `test/*`/`data/*` needs no LIFECYCLE.md edit. **This strengthens the plan**: LIFECYCLE.md names "Test" as a first-class stage, yet BRANCHING.md still has no `test/*` kind to carry test-stage work. The gap is now explicit and documented.
- **`culture/staging` is GONE** (PR #199, "align branch contract to culture/release only"). `WORLD_SLUGS = frozenset({"release"})`. Culture pipeline is now two-tier: `culture/<country>` → `culture/release` → `main`. The `test/*` two-tier design still mirrors culture — no change.
- **`tests/conftest.py` is NEW and now governance** (locked into `GOVERNANCE_GLOB_PATTERNS`). It stays governance through both rollouts.
- **`.worktree/WORKTREES.md`, `.worktree/.gitignore` are NEW governance paths.** `docs/WORKTREES.md` is now a compatibility redirect. Worktree mechanics moved out of `.claude/CLAUDE.md` into `.worktree/WORKTREES.md`.
- **New validators/tests** (auto-covered by glob, but the explicit lists below are refreshed): `scripts/validate_culture.py`, `scripts/validate_name_register.py`, `tests/validate_hofstede_derived.py`, `tests/validate_hofstede_reference.py`, `tests/test_name_register.py`.
- **New data** under a subdirectory: `data/countries.json`, `data/names/name_register.json`, `data/names/name_register.schema.json`. The `data/*` dir-prefix design covers `data/names/` automatically — this *validates* the prefix approach.
- **Four per-AI contributor-guidance files exist** — `.claude/CLAUDE.md`, `.gemini/GEMINI.md`, `.github/copilot-instructions.md`, `.perplexity/PERPLEXITY.md`. Three are DRY (no kind enumeration; they link to BRANCHING.md). **`.perplexity/PERPLEXITY.md` is the exception**: its Rule 1 has a branch-kind table that (a) enumerates kinds, so it needs `test/*`/`data/*` added, and (b) is *already stale* — it still lists `culture/staging`, removed by PR #199. Phase D survives, scoped to this one file.
- **`engine/` directory is NEW** (`engine/claude/`, `engine/copilot/`, `engine/gemini/`). These are *end-user runtime instructions shipped inside culture zips* (persona operation), NOT contributor guidance — and `git grep` confirms they contain no branching references. Out of scope for this plan.
- **The footer → YAML-frontmatter migration landed** (Phases 1–2, 2026-05-17):
  culture-file metadata moved out of a trailing footer into a leading
  frontmatter block. It added `tests/culture_metadata.py`,
  `tests/test_culture_metadata.py`, `tests/test_metadata_format.py`,
  `tests/test_migrate_footer.py`, and `scripts/migrate_footer_to_frontmatter.py`.
  It does **not** touch the branch-kind structure, so this plan is unaffected —
  and the new files fall out of the classification *rule* cleanly
  (`culture_metadata` + the new `test_*` files → `test/*`; the one-shot
  migration script → `other`). The explicit `test/*` snapshot below is
  correspondingly more stale — as already noted, regenerate it from a fresh
  glob at Phase B2 / C2.

## Context

Observation: the branching strategy is sometimes confusing the agents. Working with the user, we converged on a structural cause: the contract collapses **three orthogonal categories of work** into a single `governance/*` bucket.

**The matrix (user's framing):**

```
                     │  Content                     │  Test
─────────────────────┼──────────────────────────────┼──────────────────────────────
Solution (single)    │  culture/*  (regions/**,     │  test/*  ← NEW kind
                     │   slug-narrowed)             │   (validators + tests of
                     │                              │    culture content)
─────────────────────┼──────────────────────────────┼──────────────────────────────
Solution (shared)    │  data/*  ← NEW kind          │  (covered by test/*; tests
                     │   (data/**, cross-culture    │   of shared data live in
                     │   reference + policy data)   │   the same place as tests
                     │                              │   of single-culture content)
─────────────────────┼──────────────────────────────┼──────────────────────────────
Delivery             │  governance/*                │  governance/*  (delivery-test
                     │  (gates, classifier,         │   is tightly coupled to
                     │   orchestrators, contract    │   delivery-content; no value
                     │   doc)                       │   in separating)
```

Today, three of these five cells are collapsed into `governance/*`. A TDD workflow has to ride `governance/*` to add a validator and then `culture/*` for the content; a data update has to ride `governance/*` even though it's not a gate change.

**Governance is about gates between lifecycle phases, not about tests** (user framing; the lifecycle itself is now documented in [docs/LIFECYCLE.md](../LIFECYCLE.md)). The lifecycle: `plan → code → build → test → release → deploy → operate → monitor`. Governance owns the **checkpoints between phases**. Gates may *use* tests as their check, and the same test may run on both sides of a gate (e.g., a culture-content test run by both the pre-commit hook and CI). So:

- A **test file is classified by what it tests**, not by whether a gate happens to run it.
- `test_branch_scope.py` tests the classifier (a gate component) → `governance/*`.
- `test_plagiarism.py` tests culture content → `test/*`, even though CI's PR-gate also runs it.
- The matrix captures the 4 cells we need today (culture, data, test, governance); future lifecycle phases (build, release, deploy, operate, monitor) can carve out their own kinds without disturbing this contract.

**TDD-aligned pipelines (the target):**

```
                          ┌─ test/<slug>    → test/release    → main   (lands first if
Requirement ─ split into ─┤                                              new test coverage
                          └─ culture/<slug> → culture/release → main    is needed)

Data update (Hofstede release, new denylist entries, etc.):
                            data/<slug>     → main            (one-tier, direct)
```

**Pairing rule (per user) is conditional, not 1:1:**

> Before opening a `culture/<slug>` PR, ask:
> Q1. **How can this be tested?** (design question)
> Q2. **Do the necessary test cases already exist in `main`?**
>   - **Yes** → no `test/*` PR needed; proceed with `culture/<slug>` directly.
>   - **No** → open `test/<slug>` first, land through `test/release` → `main`, then `culture/<slug>`.

Pairing is by **shared slug convention** (`test/germany-personas-v2` pairs with `culture/germany-personas-v2`) but not enforced 1:1.

## The path-allocation matrix (snapshot 2026-05-16)

Verified by globbing [tests/](../../tests/), [scripts/](../../scripts/), [data/](../../data/) on disk. **The file set churns** — new validators and data files land regularly. What's stable is the **classification rule**; the explicit lists below are a snapshot and MUST be regenerated from a fresh glob at implementation time (Phase B2 / C2). The rule:

- `regions/**` → `culture/*`
- `data/**` (everything, any depth) → `data/*`
- gates + tests-of-gates + orchestrators (explicit list) → `governance/*`
- everything else under `tests/**` and the content validator/audit scripts → `test/*`
- the remainder (ad-hoc scripts, generators, top-level docs) → `other`

### `culture/*` — Solution-Content-Single (unchanged)

- `regions/**` (scope-narrowed by slug per [tests/branch_scope.py](../../tests/branch_scope.py))
- + existing `SAFE_PATTERNS` (incl. `data/hofstede_bag_locks.yaml`, `data/v2_migrated_countries.txt` — these are per-country opt-ins that ride with culture PRs and **stay carved-out as SAFE on culture/* branches**; see "data/ exceptions" below)

### `data/*` — Solution-Content-Shared (NEW)

Shared reference data, policy data, fixtures used across all cultures. **The whole `data/` folder at any depth, including the `.py` files in it** (they're code that loads/defines the data — moves with the data, not with the gates). Snapshot of `data/`:

- `data/hofstede_scores.json` — Hofstede Insights reference dataset
- `data/hofstede_keywords.py` — keyword sets (Python module of constants)
- `data/hofstede_denylist.yaml` — denied terms
- `data/hofstede_bag_loader.py` — bag-loading utility
- `data/language_policy.yaml` — language policy
- `data/phrase_denylist.txt` — plagiarism denylist
- `data/countries.json` — country registry (NEW since planning)
- `data/names/name_register.json`, `data/names/name_register.schema.json` — name register + schema in a subdirectory (NEW; confirms the dir-prefix design covers nested paths)
- + safe metadata

**`data/` exceptions** — files already carved into `SAFE_PATTERNS` for culture/* stay there (they ride with per-country PRs by design, not with shared-data PRs):

- `data/hofstede_bag_locks.yaml` — per-country bag locks
- `data/v2_migrated_countries.txt` — per-country v2 opt-in

### `test/*` — Solution-Test (NEW)

Tests and validators that verify **culture content** (or shared data). This is the `tests/*` suite LIFECYCLE.md calls "Cultures repo tests" — distinct from the external `khai_tests.*` suite. Snapshot (regenerate at impl time — `tests/test_*.py` and `tests/validate_*.py` minus the gate exceptions, plus the content validator/audit scripts):

- `tests/validate_country_bag.py`, `tests/validate_language.py`
- `tests/validate_hofstede_derived.py`, `tests/validate_hofstede_reference.py` (NEW since planning)
- `tests/test_audit_consistency.py`, `test_audit_readme.py`, `test_audit_readme_bands.py`
- `tests/test_completeness.py`, `test_history_arc.py`
- `tests/test_hofstede_bag_completeness.py`, `test_hofstede_bag_fork.py`, `test_hofstede_bag_loader.py`, `test_hofstede_bag_quality.py`, `test_hofstede_bag_shape.py`
- `tests/test_hofstede_derived.py`, `test_hofstede_reference.py`, `test_hofstede_structure.py`
- `tests/test_language.py`, `test_validate_language.py`
- `tests/test_links.py`, `test_plagiarism.py`, `test_sections.py`
- `tests/test_update_hofstede_readme.py`
- `tests/test_name_register.py` (NEW since planning)
- `tests/findings.py` (validator-runtime library — duplicate of `scripts/findings.py`; see "Deferred cleanup")
- `tests/requirements.txt`, `tests/language_exceptions.txt`
- `scripts/validate_history_arc.py`, `scripts/validate_sections.py`
- `scripts/validate_culture.py`, `scripts/validate_name_register.py` (NEW since planning)
- `scripts/audit_readme_bands.py` — confirmed test/* per user ("test in disguise")
- `scripts/prose_review.py`
- `scripts/findings.py` (validator-runtime library; duplicate)
- + safe metadata

### `governance/*` — Delivery (Content + Test) (narrowed)

Only the **gates and their tests**:

- `.githooks/**` — the hook itself
- `.github/workflows/**` — CI gates
- `tests/branch_scope.py` — classifier engine
- `tests/conftest.py` — pytest config; explicitly locked into governance since planning started
- `tests/test_branch_scope.py` — tests of the classifier
- `tests/test_hook_scope_e2e.py` — tests of the hook end-to-end
- `tests/validate_pr_base.py`, `tests/validate_pr_scope.py` — PR-routing gates
- `tests/test_validate_pr_base.py`, `tests/test_validate_pr_base_cli.py` — tests of PR-routing gates
- `scripts/validate.py`, `scripts/validate_general.py` — orchestrators (the pipes)
- `scripts/setup-hooks.sh`, `scripts/setup-hooks.bat` — hook installers
- `docs/BRANCHING.md` — the contract document
- `.worktree/WORKTREES.md`, `.worktree/.gitignore` — worktree governance policy (NEW governance paths since planning)

### `other` (`chore/*`, `fix/*`, `feat/*`) — content tooling, ad-hoc scripts

- `scripts/scaffold_country.py` — content generator (reads Hofstede, emits per-country READMEs)
- `scripts/deploy_culture.py` — release-tooling that moves `culture_*.md` files into target folders
- `scripts/audit-germany.py`, `scripts/normalize-germany.py` — one-shot scripts (likely legacy)
- `scripts/update_hofstede_readme.py` — README updater (generative, not a gate; moves out of governance)
- Anything else not under `regions/**`, `data/**`, `tests/**` (non-gate), `scripts/validate_*.py` (non-orchestrator), or governance paths

### `sync/*` — unchanged

Pointer-at-`main` branches that PR into `culture/release`.

### Resolved from earlier open questions

- `data/hofstede_bag_loader.py` → `data/*` (whole `data/` folder is one kind).
- `scripts/audit_readme_bands.py` → `test/*` (user confirmed).
- `scripts/scaffold_country.py` → `other` (content generator, not validator).
- `scripts/deploy_culture.py` → `other` (release-tooling). Currently NOT in governance, so no classifier change for this file.
- `scripts/findings.py`, `tests/findings.py` → `test/*` (validator-runtime library; duplication flagged as deferred cleanup).
- `scripts/update_hofstede_readme.py` → `other` (generative tooling; moves OUT of current governance list).

## Approach: stepwise, two new-kind rollouts in sequence

`data/*` ships first because it's the cleaner, smaller cut (single directory, no test repartitioning). `test/*` follows because it validates the same pattern with bigger surface area. Each rollout is two small governance/* PRs (PR-base routing, then classifier+hook+doc). Three of the four agent-facing docs need no follow-up — they were made DRY upstream and defer to `docs/BRANCHING.md`. The fourth (`.perplexity/PERPLEXITY.md`) still enumerates kinds and gets its own small `chore/*` PR (Phase D).

---

### Phase A — Lock the matrix (no code) — RESOLVED

User-resolved during planning:

1. **Matrix and path-allocation lists above** — agreed.
2. **`data/<slug>` → `main` directly** (one-tier; no `data/release`) — agreed. *Forward-looking note: data target may live outside git one day (DB or similar); one-tier keeps the door open.*
3. **`test/<slug>` → `test/release` → `main`** (two-tier, mirrors culture) — agreed.
4. **`data/*` covers the whole `data/` folder including `.py` files** (e.g., `hofstede_bag_loader.py`, `hofstede_keywords.py`) — agreed for now. *Acknowledged "semi dirty": `.py` files in `data/` could arguably be scripts; revisit later if it causes friction.*
5. **Gate-test files stay `governance/*`** (`test_branch_scope.py`, `test_hook_scope_e2e.py`, `test_validate_pr_base*.py`) — agreed. The rule: a test belongs with what it tests; if it tests a gate, it's governance; if it tests content, it's `test/*`. The same test may run on both sides of a gate (e.g., pre-commit + CI) and that doesn't move its kind.

---

### Phase 0 — Place the plan doc in the repo (chore/*) — THIS PR

Branch: `chore/branching-plan-doc`

Creates this file (`docs/migration/branching-kinds-test-data.md`). After this lands, all
subsequent phases reference and update this repo copy as the source of truth.

Verification: branch classifies as `other`; `docs/migration/*` is in-scope for `chore/*`.

---

### Phase B — Introduce `data/*` kind (first; smallest cut)

#### B1 — PR-base routing for `data/*` (governance/*)

Branch: `governance/branching-data-pr-routing`

Adds the route `data/<slug>` → `main` to `tests/validate_pr_base.py`. Forward-compatible: adds a new allowed route, rejects nothing existing.

Files:
- `tests/validate_pr_base.py`
- `tests/test_validate_pr_base.py`, `test_validate_pr_base_cli.py` — new route cases

Verification: `pytest tests/test_validate_pr_base.py tests/test_validate_pr_base_cli.py` green.

#### B2 — Classifier + hook + BRANCHING.md (one governance/* PR)

Branch: `governance/branching-data-kind`

Bundled because BRANCHING.md is governance and must agree with the classifier; the hook is governance and surfaces classifier output. Splitting them would ship inconsistent intermediates.

**`tests/branch_scope.py`:**
- Add `DATA_BRANCH_PATTERN = re.compile(r"^data/[a-z0-9][a-z0-9_.-]*$")`.
- Add `classify_branch` case returning `"data"`.
- Add `DATA_ALLOWED_DIR_PREFIXES = ("data/",)`.
- Add `check_scope` branch for `branch_kind == "data"`: file must start with `data/` OR be in `SAFE_PATTERNS`. Note: `data/hofstede_bag_locks.yaml` and `data/v2_migrated_countries.txt` stay carved into `SAFE_PATTERNS` (allowed on culture/* too) — `data/*` branches simply also allow them.
- **REMOVE from `GOVERNANCE_GLOB_PATTERNS`:** `data/hofstede_denylist.yaml`, `data/hofstede_keywords.py`, `data/hofstede_scores.json`, `data/hofstede_bag_loader.py`, `data/language_policy.yaml`, `data/phrase_denylist.txt`. Also remove `scripts/update_hofstede_readme.py` (moves to `other`).

**`tests/test_branch_scope.py`:**
- `classify_branch` cases for `data/*` (valid + near-misses fall to `other`).
- `check_scope` cases: `data/<slug>` may touch all `data/**` files; rejected on `regions/**`, governance paths, tests/.
- Cross-kind rejection: `chore/*` and `governance/*` no longer allowed to touch data files (other than what was already SAFE).
- Locked-set test for `DATA_ALLOWED_DIR_PREFIXES`.
- Updated locked-set test for the narrowed `GOVERNANCE_GLOB_PATTERNS`.

**`.githooks/pre-commit`:**
- Add `data`-branch error arm mirroring the others.
- Add `data/<slug>` (and fix the existing `feat/<name>` omission) to the "Create a feature branch first" message.

**`docs/BRANCHING.md`:**
- Add `data/<slug>` row to the kinds table with a **"PRs into"** column (also grounded in `validate_pr_base.py` after B1).
- Add a brief "What's data?" subsection — shared reference/policy data, not single-culture content.
- Fix the "four kinds" wording opportunistically (we're already touching the file).

Verification:
- `pytest tests/test_branch_scope.py tests/test_hook_scope_e2e.py` green.
- Manual hook smoke test on a `data/smoke-test` worktree: staging `data/hofstede_keywords.py` passes; staging `regions/europe/germany/*.md` rejects with the new data-branch error.
- Existing culture/* branches still pass scope check (carve-outs for bag_locks.yaml and v2_migrated_countries.txt preserved).

---

### Phase C — Introduce `test/*` kind (second; bigger cut)

#### C1 — PR-base routing for `test/*` and `test/release` (governance/*)

Branch: `governance/branching-test-pr-routing`

Adds routes:
- `test/<slug>` (slug ≠ "release") → `test/release`
- `test/release` → `main`

Same forward-compatibility property as B1.

Files: same shape as B1.

#### C2 — Classifier + hook + BRANCHING.md (one governance/* PR)

Branch: `governance/branching-test-kind`

**`tests/branch_scope.py`:**
- Add `TEST_BRANCH_PATTERN = re.compile(r"^test/[a-z0-9][a-z0-9_.-]*$")`.
- Add `TEST_WORLD_SLUGS = frozenset({"release"})` (two-tier pipeline; no `test/staging` for now).
- Add `classify_branch` case returning `"test"`.
- Add explicit `TEST_ALLOWED_GLOB_PATTERNS` listing every path from the `test/*` matrix section above (regenerate from a fresh glob — the file set has grown since planning).
- Because of overlap between "gate files" (governance) and "test files for culture" (test/*) in the same `tests/` directory, the implementation needs **explicit listing** of the governance entries in `tests/`: `branch_scope.py`, `conftest.py`, `test_branch_scope.py`, `test_hook_scope_e2e.py`, `validate_pr_base.py`, `validate_pr_scope.py`, `test_validate_pr_base.py`, `test_validate_pr_base_cli.py`. Order: governance-check runs first; if a file matches a governance pattern, classify governance; otherwise check test/* patterns.
- Add `check_scope` branch for `branch_kind == "test"`: file must match `TEST_ALLOWED_GLOB_PATTERNS` OR be in `SAFE_PATTERNS`.
- **REMOVE/REPLACE in `GOVERNANCE_GLOB_PATTERNS`:** broad `tests/test_*.py` and `tests/validate_*.py` go away; replaced by the explicit gate entries plus `tests/validate_pr_base.py`, `tests/validate_pr_scope.py`. Remove `tests/requirements.txt`, `tests/language_exceptions.txt`, `scripts/validate_*.py` (except orchestrators), `scripts/audit_readme_bands.py`.

**`tests/test_branch_scope.py`:**
- `classify_branch` cases for `test/*` (valid + near-misses).
- `check_scope` cases for each `test/*` path; rejection of culture/data/governance paths from `test/*` branches.
- Critical: a parity test asserting every path in the matrix is reachable from exactly one of `culture/*` / `test/*` / `data/*` / `governance/*` / `other` (no path classifiable as two kinds; no gap).
- Locked-set test for `TEST_ALLOWED_GLOB_PATTERNS`.

**`.githooks/pre-commit`:**
- Add `test`-branch error arm.
- Add `test/<slug>` to the "Create a feature branch first" message.

**`docs/BRANCHING.md`:**
- Add `test/<slug>` and `test/release` rows to the kinds table with PRs-into column.
- Add the TDD pairing section (Q1/Q2 decision flow).
- Add the matrix diagram at the top of the doc as the canonical agent-facing decision aid.
- Worked examples per kind: `culture/germany-personas-v2`, `test/persona-tradition-required`, `data/hofstede-2025-refresh`, `governance/harden-hook`, `chore/update-readme`, `sync/release-from-main-2026-05-13`.

Verification:
- `pytest tests/test_branch_scope.py tests/test_hook_scope_e2e.py` green.
- Manual hook smoke test on `test/smoke-test`: staging `tests/test_plagiarism.py` passes; staging `tests/branch_scope.py` rejects (still governance).

---

### Phase D — DRY-ify `.perplexity/PERPLEXITY.md` (chore/*)

Branch: `chore/branching-perplexity-dry`

Three of the four contributor-guidance files are already DRY and need no change for the new kinds:

- **`.claude/CLAUDE.md`** — "Canonical references" section points at `docs/BRANCHING.md`. No kind list.
- **`.gemini/GEMINI.md`** — "Authoritative references ... do not restate them, link to them." No kind list.
- **`.github/copilot-instructions.md`** — "Do not duplicate branch-kind rules in this file." No kind list.

**`.perplexity/PERPLEXITY.md` is the outlier.** Its Rule 1 carries a literal branch-kind table (`culture/`, `governance/`, `chore/`, `fix/`, `feat/`) that already disagrees with the contract — it lists `culture/staging`, removed by PR #199. Fix it the same way the repo DRY'd the other three:

- Replace the enumeration table with a pointer to `docs/BRANCHING.md` (matching the GEMINI.md / copilot pattern). Keep Rule 1's intent ("branch-first, choose kind before editing, split cross-kind work") — drop only the table.
- This simultaneously fixes the live `culture/staging` staleness and makes the file future-proof: `test/*`, `data/*`, and any later kind need no further PERPLEXITY.md edit.

`.perplexity/` is `other` scope → `chore/*` is the correct branch kind (PERPLEXITY.md is not governance, not regions/, not data/).

**Sequencing:** independent of B/C — a pointer to BRANCHING.md is correct regardless of BRANCHING.md's current content. Can run first (it fixes a live staleness bug) or last (after C2, for a coherent single sweep). Recommend running it **first**, right after Phase 0, so the staleness bug doesn't linger.

Optional polish (fold into the C2 governance PR, not here): add a `test/` and `data/` example to the worktree-create example block in `.worktree/WORKTREES.md`.

Verification: pre-commit hook passes on `chore/*`; grep the four contributor files afterward to confirm none still enumerate a kind set.

---

## Deferred (not in this plan)

- **`scripts/findings.py` and `tests/findings.py` are identical.** Confirmed by reading both. Pick one canonical location (probably `tests/findings.py` since it's validator-runtime) and delete the other; update imports. Separate chore/* — but note both copies land in `test/*` after C2, so a single `test/*` PR can do the dedup. Sequence after C2.
- Whether `.claude/CLAUDE.md` and `.github/copilot-instructions.md` should themselves become governance (closes a soft-gate-weakening hole — they're agent-instruction surfaces editable on `chore/*` today).
- Hard CI-enforced TDD ordering ("`culture/<slug>` cannot merge unless `test/<slug>` is in main"). User's rule is conditional, so soft enforcement is right starting point.
- Whether `chore`/`fix`/`feat` should collapse (identical at the contract level today).
- Terminology normalization ("kind" everywhere; retire "scope" for branch classification).
- Reducing duplication between BRANCHING.md prose lists and `branch_scope.py` constants (have the doc reference the code rather than re-list).

## Critical files

- `tests/branch_scope.py` — classifier + locked sets (**governance**)
- `tests/test_branch_scope.py` — contract pinning (**governance**)
- `tests/validate_pr_base.py` — PR routing (**governance**)
- `tests/test_validate_pr_base.py`, `test_validate_pr_base_cli.py` — routing tests (**governance**)
- `.githooks/pre-commit` — error messages (**governance**)
- `docs/BRANCHING.md` — canonical contract (**governance**)
- `.worktree/WORKTREES.md` — worktree workflow + examples (**governance**; optional C2 polish)
- `.perplexity/PERPLEXITY.md` — Perplexity contributor doc, enumerates kinds (`other`; `chore/*` — Phase D)
- `.claude/CLAUDE.md`, `.gemini/GEMINI.md`, `.github/copilot-instructions.md` — already DRY (defer to BRANCHING.md; **no edits needed**)

## Order summary

1. **Phase A** — Matrix lock-in (RESOLVED; no code changes).
2. **Phase 0** — `chore/branching-plan-doc` (places this plan at `docs/migration/branching-kinds-test-data.md`).
3. **Phase D** — `chore/branching-perplexity-dry` (DRY-ify `.perplexity/PERPLEXITY.md`; runs early — fixes a live `culture/staging` staleness bug).
4. **Phase B1** — `governance/branching-data-pr-routing` (forward-compatible).
5. **Phase B2** — `governance/branching-data-kind` (classifier + hook + doc for `data/*`).
6. **Phase C1** — `governance/branching-test-pr-routing` (forward-compatible).
7. **Phase C2** — `governance/branching-test-kind` (classifier + hook + doc for `test/*`; optional WORKTREES.md examples).

Pause for review after each. Each is independently reversible (revert one PR at a time). Phase D is order-independent — listed early because it fixes existing staleness, but it can move.
