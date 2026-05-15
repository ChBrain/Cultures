# Cultures kind schema: split `piece` into `history` + `piece`, split `persona` into `male` + `female`

Status: **EXECUTED (2026-05-14, v0.5.0)**. All three stages of this plan shipped. KAIHACKS stage 1 in [PR #183](https://github.com/ChBrain/KAIHACKS/pull/183) (khai-tests-v0.1.6, later v0.1.7). Cultures stage 2 (governance) shipped via Cultures PRs #156 (stamp shape), #157 (L2 sections + L4h history-arc), #159 (L4a trailing-form kind tokens), #161 (stamp encoding), #163 (validate.yml push triggers removed). Cultures stage 3 (per-culture migration) shipped via Cultures PRs #104 (Germany v2), #105 (Netherlands), #155 (Denmark), #165 (Poland), #166 (Spain). Released to main as v0.5.0 via #169. This document is kept as historical record of the schema decision and stage sequencing; `data/v2_migrated_countries.txt` references it as the "full plan".

Trigger: the original `piece` kind was doing double duty as the culture's foundational historical artifact, which weakened what `piece` could mean (a true cultural piece: a work, a craft, a practice). Same conflation in `persona` (two genders share one kind, with gender encoded in the name slug). Splitting both made the schema honest.

## Naming convention

- **KAI** / **KAI HACKS AI** — the architecture / system (proper name).
- **khai** — the lowercase prefix used for the package (`khai_tests`), skills (`khai-cultures-*`), test modules (`test_khai_*.py`), and the footer declaration marker (`*khai: persona*`).
- **khai component** / **khai type** — refers to one of the 5 generic components (process, position, piece, place, persona).

Following the existing convention: brand/architecture references use uppercase "KAI"; programmatic references (markers, identifiers, file names) use lowercase "khai".

## Architectural decision

**Option A confirmed**: this is **Cultures applying the KAI HACKS AI Architecture**. The khai framework stays at 5 generic components (process, position, piece, place, persona) with their existing mnemonic structures (IDLE / HOLD / PLAY / SHOW / PAST). No new khai components are introduced.

`history`, `male`, `female`, and `language` are **Cultures-specific kinds layered on top** of khai components:

| Cultures kind | khai component structure |
|---|---|
| `language` | **position** (Has / Orders / Loses / Drives) |
| `history` | **piece** (Place / Load Bearing / Apparent / Yearbook) |
| `position` | **position** (Has / Orders / Loses / Drives) |
| `process` | **process** (Initiated by / Direction / Lever / Echo) |
| `piece` | **piece** (Place / Load Bearing / Apparent / Yearbook) |
| `place` | **place** (Shown / Holds / Offers / Withheld) |
| `male` | **persona** (Projection / Action / Shadow / Tell) |
| `female` | **persona** (Projection / Action / Shadow / Tell) |

8 Cultures kinds run on 5 khai structures. Multiple Cultures kinds share a khai structure (language and position share HOLD; history and piece share PLAY; male and female share PAST). The test framework must distinguish them without knowing about Cultures specifics.

## Detection mechanism: footer declaration

KAIHACKS PR [#183](https://github.com/ChBrain/KAIHACKS/pull/183) merged the declaration-driven `khai_tests.components._component.is_component_type`. Every khai component file declares its type via a footer marker:

```
*khai: persona*
```

This sits alongside the existing footer convention (`*Hofstede signal: ...*`, `*Type: Composite*`).

```python
_KHAI_DECLARATION_RE = re.compile(r"^\*khai:\s*(\w+)\s*\*\s*$", re.MULTILINE)

def is_component_type(path: Path, ctype: str) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = _KHAI_DECLARATION_RE.search(text)
    if m is not None:
        return m.group(1).lower() == ctype
    # Legacy filename-token fallback during migration.
    return ctype in path.stem.lower().split("_")
```

The declaration is the contract. Filename and section structure are not consulted. Cultures' specialized kind names (`language`, `history`, `male`, `female`) become transparent — the test framework doesn't know or care.

### Why this beats the alternatives

| Approach | Cost | Agnosticism | Catches structural typos? |
|---|---|---|---|
| Name-token (legacy) | 0 lines | Requires every project to name files with the khai type as a `_`-separated token | yes — name says "persona", test runs, missing sections fail |
| Filename-glob broadening (per-kind adapter) | small but recurring | Bad — test framework knows about Cultures kinds | yes, but couples khai to Cultures vocabulary |
| Pure structure detection (all 4 canonical headers present) | 1 function | Good | NO — a file missing one section silently skips (worse) |
| **Footer declaration (shipped in v0.1.6)** | 1 function in KAIHACKS + 1 footer line per content file | Good — any project opts in by adding the line | yes — declared file with broken structure FAILS loudly |

The footer declaration also fixes an existing soft bug: today, `culture_german_positon.md` (typo in filename) silently skips all position tests. Once Cultures content has the declaration, the typo'd-filename file still has the right `*khai: position*` footer and IS detected and tested.

## Strategic directive (binding)

- **All `culture/*` PRs are paused.** PRs #100 (Spain), #104 (Germany), #105 (Netherlands), #106 (Denmark v2), #107 (Poland v2) do not move forward until the schema split has landed in Cultures (stage 2 + stage 3).
- **Only work NOT affected by this change advances.**
- **KAIHACKS drives Cultures.** Test framework refactor landed first (stage 1a); skill prose updates + release landed (stage 1b); Cultures changes follow (stage 2 unblocked).

## Cultures CI currently broken (urgent)

`chbrain/Cultures` `.github/workflows/validate.yml` pins `khai-tests-v0.2.0`, which was deleted in commit `6e9b078` (the "patch-only" version reset). Every `khai-*` job in Cultures CI is failing on the wheel download (404). Bump to `khai-tests-v0.1.6` unblocks CI immediately. This is independent of the schema split and can land as a hotfix or be folded into stage 2.

## Why

- **Piece-as-history conflation.** Germany's `culture_german_piece_grundgesetz.md` holds the constitutional document — that's history, not a piece of culture. Both files would structurally follow khai's piece mnemonic; only the subject differs. Splitting the kind makes the subject explicit while reusing the khai structure.
- **Persona-as-name conflation.** `persona_brigitte` is female, `persona_christian` is male — gender implicit in the name. The engine layer makes the dual structure explicit (`engine/position_male.md`, `engine/position_female.md`) but the culture layer hides it. Lifting `male` and `female` to kind names matches engine; the name slug stays in the filename to keep human identity visible.

## The three-layer correctness model (acceptance criteria)

The schema change is complete only when **all three layers agree**:

| Layer | Surface | Owner |
|---|---|---|
| **Content** — what's in Cultures conforms to the 8-kind schema and every file carries `*khai: <type>*` footer | `regions/<country>/culture_*.md` | Cultures repo, `culture/*` branches |
| **Skills** — production produces correctly with declaration; review catches deviations | `skills/khai-cultures-create/SKILL.md` (+ templates), `skills/khai-cultures-review/SKILL.md`, `skills/khai-cultures-hofstede-bag/SKILL.md` | KAIHACKS repo, skill `v` bumps (DONE in v0.1.6) |
| **Tests** — khai-level reads declaration to detect type; Cultures-level enforces 8-kind minimum + canonical order + declaration-present audit | KAIHACKS `components/_component.py` (DONE in v0.1.6); Cultures `tests/validate_culture_completeness.py` (or pytest successor) — stage 2 work | KAIHACKS + Cultures repos |

Drift on any layer means "not done". A working acceptance test: produce a culture with `khai-cultures-create`; run `khai-cultures-review` on the output; push; observe Cultures CI green.

## Target schema

Eight files **minimum** per developed culture, canonical authoring/display order. More instances per kind allowed above the minimum.

| # | Cultures kind | Filename pattern | Slug | Footer marker | khai structure | Template |
|---|---|---|---|---|---|---|
| 1 | language | `culture_<adj>_language_<slug>.md` | required | `*khai: position*` | Has / Orders / Loses / Drives | `template_culture_language.md` |
| 2 | history | `culture_<adj>_history_<slug>.md` | required | `*khai: piece*` | Place / Load Bearing / Apparent / Yearbook | `template_culture_history.md` |
| 3 | position | `culture_<adj>_position.md` | none | `*khai: position*` | Has / Orders / Loses / Drives | `template_culture_position.md` |
| 4 | process | `culture_<adj>_process_<slug>.md` | required | `*khai: process*` | Initiated by / Direction / Lever / Echo | `template_culture_process.md` |
| 5 | piece | `culture_<adj>_piece_<slug>.md` | required | `*khai: piece*` | Place / Load Bearing / Apparent / Yearbook | `template_culture_piece.md` |
| 6 | place | `culture_<adj>_place_<slug>.md` | required | `*khai: place*` | Shown / Holds / Offers / Withheld | `template_culture_place.md` |
| 7 | male | `culture_<adj>_male_<name>.md` | required (persona's name) | `*khai: persona*` | Projection / Action / Shadow / Tell | `template_culture_persona.md` |
| 8 | female | `culture_<adj>_female_<name>.md` | required (persona's name) | `*khai: persona*` | Projection / Action / Shadow / Tell | `template_culture_persona.md` |

Order 1-8 is enforced for both creation (skills produce in this sequence) and audit (per-country README "Audit Status" table lists kinds in canonical order).

History (file 2) and piece (file 5) both share khai piece structure and the `*khai: piece*` declaration, but each has its own template because the subject focus differs (pivotal historical moment vs. currently practiced cultural piece). Male and female (files 7 and 8) share khai persona structure and the `*khai: persona*` declaration, AND share a single template (gender is a slot policy, not a subject divergence).

## Worked example: Germany

Current (7 files; no declarations):
```
culture_german_language_hochdeutsch.md
culture_german_persona_brigitte.md
culture_german_persona_christian.md
culture_german_piece_grundgesetz.md
culture_german_place_berlin.md
culture_german_position.md
culture_german_process_erinnern.md
```

Target (8 files, with declarations):
```
culture_german_language_hochdeutsch.md          (no rename; add *khai: position* footer)
culture_german_history_grundgesetz.md           (renamed from piece_grundgesetz; add *khai: piece*; template_culture_history)
culture_german_position.md                      (add *khai: position*)
culture_german_process_erinnern.md              (add *khai: process*)
culture_german_piece_<slug>.md                  (NEW true piece e.g. beethoven9; add *khai: piece*; template_culture_piece)
culture_german_place_berlin.md                  (add *khai: place*)
culture_german_male_christian.md                (renamed from persona_christian; add *khai: persona*)
culture_german_female_brigitte.md               (renamed from persona_brigitte; add *khai: persona*)
```

Net: 3 renames + 1 new file + 8 footer additions.

## Impact map

| Surface | Change | Repo | Status |
|---|---|---|---|
| `tests/khai/khai_tests/components/_component.py` | declaration-driven `is_component_type` (reads `*khai: <type>*`) with filename fallback | KAIHACKS | **shipped in v0.1.6** (PR #183) |
| `skills/khai-cultures-create/SKILL.md` v0.2.0 | 8-file schema, canonical 1-8 order, khai declaration footer requirement, build sequence rewritten | KAIHACKS | **shipped in v0.1.6** |
| `skills/khai-cultures-create/references/template_culture_history.md` | NEW — pivotal-moments-focused template, worked example Grundgesetz | KAIHACKS | **shipped in v0.1.6** |
| `skills/khai-cultures-create/references/template_culture_piece.md` v0.2.0 | refocused on current cultural piece/artifact, worked example Beethoven's Neunte Sinfonie | KAIHACKS | **shipped in v0.1.6** |
| `skills/khai-cultures-create/references/template_culture_{language,position,process,place,persona}.md` v0.2.0 | khai declaration footer added; Grundgesetz cross-refs → history; persona template adds male/female filename split + gender slot policy | KAIHACKS | **shipped in v0.1.6** |
| `skills/khai-cultures-review/SKILL.md` v0.4.0 | declaration-driven structure lens; canonical-order audit; new hard FAILs | KAIHACKS | **shipped in v0.1.6** |
| `skills/khai-cultures-hofstede-bag/SKILL.md` v0.3.0 | persona-anchor scan references both gender files; non-invocation guard | KAIHACKS | **shipped in v0.1.6** |
| `tests/khai/pyproject.toml` v0.1.6 | patch bump per the patch-only convention | KAIHACKS | **shipped in v0.1.6** |
| **KAIHACKS `khai-tests-v0.1.6` release** | declaration-driven detection wheel | KAIHACKS | **published 2026-05-12 18:45** |
| **Cultures `.github/workflows/validate.yml`** | bump `khai-tests` pin from deleted `v0.2.0` → `v0.1.6` (URGENT — CI currently broken) | Cultures | **pending** — see hotfix options |
| Cultures `validate_culture_completeness.py` (or pytest successor) | enforce 8-kind minimum, canonical 1-8 order; assert every culture file has a valid `*khai: <type>*` declaration; transition mode for old vs new schema | Cultures | pending — stage 2 |
| Cultures `tests/test_audit_*` | audit-table tests updated for split persona row + new history row in canonical order | Cultures | pending — stage 2 |
| Cultures `scripts/scaffold_country.py` | scaffold the new 8-kind layout in canonical order, with declarations | Cultures | pending — stage 2 |
| Cultures content per developed country | rename + author new piece + add `*khai: <type>*` footer to every component file | Cultures, `culture/<country>` | pending — stage 3 |
| Cultures `.github/copilot-instructions.md`, `ARCHITECTURE.md`, `METHODOLOGY.md` | document new schema + declaration convention | Cultures, `governance/*` | pending — stage 2 |

## Staged plan

### Stage 1a — KAIHACKS test framework refactor (DONE)

`_component.py` refactored to declaration-driven detection with `*khai: <type>*` footer marker; filename-token fallback retained during migration. Shipped in v0.1.6.

### Stage 1b — KAIHACKS skills + templates (DONE)

Single coordinated KAIHACKS PR [#183](https://github.com/ChBrain/KAIHACKS/pull/183) merged 2026-05-12 18:45. All three cultures skills bumped, both piece-and-history templates split, all five other templates carry khai declaration footers. `khai-tests-v0.1.6` released 27 seconds after merge by the auto-release workflow.

### Stage 2 — Cultures governance: validator + scaffold + workflow pin + docs (UNBLOCKED)

Now ready to start. One coordinated `governance/*` PR (or hotfix-first + stage 2):

1. **`.github/workflows/validate.yml`**: bump `khai-tests` pin from `v0.2.0` (deleted) → `v0.1.6`. **URGENT — Cultures CI is currently broken on this**.
2. Update `validate_culture_completeness.py` (or its pytest successor per `tests/khai/PLAN.md`) to:
   - Recognize the 8-kind schema with canonical 1-8 order enforced.
   - Assert every `culture_*.md` file has a valid `*khai: <type>*` declaration matching one of the 5 khai types.
   - Accept transition mode (old `persona_*`/`piece_*` filenames still pass when their declaration is correct).
3. Add a pytest sequence test pinning the 1-8 canonical order.
4. Update `tests/test_audit_*` for split persona row + new history row.
5. Update `scripts/scaffold_country.py` to scaffold the 8-kind layout in canonical order, with declarations.
6. Document the new schema + declaration convention in `.github/copilot-instructions.md`, `ARCHITECTURE.md`, `METHODOLOGY.md`.

### Stage 3 — Per-culture migration

After stage 2 lands and the paused culture PRs (#100, #104-#107) are addressed:

For each developed country (Germany, Denmark, Netherlands, Poland, Spain, + others with culture content):

1. `git mv culture_<adj>_piece_<slug>.md culture_<adj>_history_<slug>.md`
2. `git mv culture_<adj>_persona_<malename>.md culture_<adj>_male_<malename>.md`
3. `git mv culture_<adj>_persona_<femalename>.md culture_<adj>_female_<femalename>.md`
4. Author new `culture_<adj>_piece_<slug>.md` with true-piece content using `template_culture_piece.md`.
5. **Add `*khai: <type>*` footer to every culture_*.md file** (the substantive declarative work — 8 footer additions per country).
6. Update country `README.md` "Audit Status" table to canonical order.
7. Audit `hofstede_decisions.md` for old-filename references.

The paused in-flight PRs: close + reopen as stage-3 migration PRs.

### Stage 4 — Deprecate transition mode (one governance PR, after all migrations)

1. Remove old-schema acceptance from Cultures validators.
2. Cultures content all has declarations — KAIHACKS filename-token fallback can be deleted in a follow-up KAIHACKS PR (after auditing `worlds/` for declaration coverage).
3. Mark schema as v2.0 in `METHODOLOGY.md`.

## Three-layer agreement check (what "done" means)

1. **Content**: every developed culture has 8+ files in canonical order, each with `*khai: <type>*` footer matching the right khai structure.
2. **Skills**: `khai-cultures-create` produces the 8-file set with declarations using subject-specific templates; `khai-cultures-review` flags missing declarations or broken structure; `khai-cultures-hofstede-bag` has no stale 7-file assumptions.
3. **Tests**: Cultures pytest fails on a culture missing a kind; KAIHACKS component tests pass for declared files; canonical-order test fails on out-of-order audit tables; declaration-presence audit catches files without `*khai:` footer.

## Resolved decisions

| Question | Decision |
|---|---|
| Male/female slug | Name preserved in filename: `culture_<adj>_male_<name>.md`. |
| Order enforcement | Validated for both creation and audit. 1-8 is a contract. |
| Plurality | 8 is the minimum. More instances per kind allowed via different slugs. |
| KAI architecture impact | None. Cultures applies existing 5-component framework. |
| Detection mechanism | Footer declaration `*khai: <type>*`, with filename-token fallback during migration. |
| Marker prefix case | Lowercase `khai:` matching package/skill/module convention (case-sensitive prefix, case-insensitive type comparison). |
| Templates for piece vs history | Two distinct templates: `template_culture_piece.md` (cultural artifact, currently practiced; worked example Beethoven's Neunte Sinfonie) and `template_culture_history.md` (pivotal moment of the culture's history; worked example Grundgesetz). Both produce files declaring `*khai: piece*` because both use KAI piece structure. The split exists because the subjects need different framing and worked examples even when the structure is shared. |
| Piece content for migration | Authored fresh in stage 3 using the refocused piece template. |
| KAIHACKS branch | `claude/cultures-kind-schema-XIWZa` (merged in PR #183). |
| khai-tests release version | `v0.1.6` (patch increment per the patch-only convention from KAIHACKS commit `6e9b078`). |

## Risks

- **Three-surface drift.** Skills and tests can diverge. Mitigation: skill version notes coordinate explicitly with khai-tests release; review-skill (v0.4.0) validates the declaration as part of its lens. Stage 1 closure (this) means all three KAIHACKS surfaces match the v0.1.6 release.
- **Declaration migration of legacy KAIHACKS content (worlds/).** The filename-token fallback handles existing content during transition. Auditing `worlds/` for full declaration coverage is a follow-up task before the fallback can be removed.
- **Skill prose drift from validator.** Mitigate by referencing the same canonical 1-8 table from both skills and the Cultures validator.
- **History/piece subject overlap during authoring.** Same KAI structure can blur the kind distinction. Mitigation: separate templates with distinct worked examples (Grundgesetz vs Beethoven 9); review-skill flags same-subject coverage in both files as OBSERVATION.
- **Transition mode lifetime.** Keep a per-country migration checklist visible so transition mode doesn't silently mask half-migrations.
- **Cultures CI broken on deleted `v0.2.0` pin.** Urgent fix needed; see stage 2 step 1.

## What lands next (sequence)

1. **Stage 1a KAIHACKS test framework refactor** — done.
2. **Stage 1b KAIHACKS skills + templates + release** — done. `khai-tests-v0.1.6` published.
3. **Stage 2 Cultures governance PR** — validator + scaffold + workflow pin + docs. **Step 1 (`validate.yml` pin bump to v0.1.6) is urgent because Cultures CI is broken on the deleted v0.2.0 reference.** Can land as a separate hotfix PR or as the first commit of the larger stage 2 PR.
4. **Stage 3 per-culture migration PRs** — Germany first; closes/replaces paused #100, #104-#107.
5. **Stage 4 deprecation PR** — close transition mode in Cultures + remove filename fallback in KAIHACKS.

---

Session: https://claude.ai/code/session_01WLXjruMPTCScGpY348YuF1
