# Cultures: gate-tightening migration plan

**Persistent plan, versioned at `docs/migration/cultures-gate-tightening.md`.**
Iterated across working sessions. Each phase below is a separate `chore/<name>`
PR off `main` (or `culture/<name>` for in-`regions/` work).

**How to use this doc.** Read top-to-bottom for context. Update via PR
when a phase ships, a decision is resolved, or an open question is
answered. The update log at the bottom is append-only. GitHub issues
(#69 closed, #77 active) carry the in-flight implementation details;
this doc carries the architecture, resolved decisions, sequencing
rationale, and phases that don't yet have issues.

**Status snapshot (2026-05-11, post-Phase 6 landing).**
- Phase 6 essentially complete: 6c (#71), audit script (#73), 6b data
  fixes (#74), prose-audit extension (#75) all on `main`.
- Outstanding: 6a (cross-repo Skill update in `ChBrain/KAIHACKS`), one
  Poland prose line (`**Medium IDV**` → `**High IDV**`), and the NL
  decisions.md drift Phase 4 is designed to clean up.
- Next concrete action: pick from Phase 1 (close PR #67's bypass route),
  Phase 4 (decisions generator → cleans NL drift mechanically), or the
  Poland one-liner.

---

## Guiding model

- **Branch shapes.**
  - `culture/<name>` — single-country branch; touches exactly one
    `regions/<region>/<country>/` folder. This is where authors work.
  - `culture/release` — long-lived collector; accumulates multiple
    countries between promotions. Does not reset.
  - `chore/fix/feat` — non-regions work, lands directly on `main`.
- **Two gate boundaries.**
  - `culture/<name> → culture/release` is the **per-country review
    surface**. One country's bag + decisions + content must be coherent
    here. This is where native-speaker / domain review happens and where
    L4f, Bx, no-bag-yet-absent, and decisions consistency are hard-blocks.
  - `culture/release → main` is the **release smoke test**. Cross-country
    and full-set checks (lock SHAs match every bag, every present bag
    still passes shape/quality, no regression). Per-country gates do not
    need to rerun if 2a was clean.
- **Everything in a country folder is culture work.** Bag YAML, decisions
  log, README, REFERENCES, and `culture_*.md` all flow through the
  culture stream. Bag PRs are not split into a separate lane.
- **Source-of-truth split for the decisions log.**
  `hofstede_bag.yaml` is the machine-readable contract.
  `hofstede_decisions.md` is human narrative — except Sections 5 (final
  bags) and 5b (denylist), which are generated from the YAML at commit
  time. See Phase 4.

---

## Move #1 — sketch (Phase 1 CI changes)

Phase 1 makes **two** edits to `.github/workflows/validate.yml`. Both fall
under "branch-shape enforcement" — direction (which target a head branch
may PR to) and scope (what one PR may touch). Together they close the
gap that allowed PR #67 to merge `culture/netherlands-hofstede-bag`
straight to `main`, bypassing culture/release.

### 1A — Direction enforcement (extend `branch-scope-mirror`)

The existing `branch-scope-mirror` job classifies the head branch and
checks file scope. It does not check the PR's target. PR #67 (head
`culture/netherlands-hofstede-bag`, base `main`) passed this gate
because all files were under `regions/`.

Add a target-ref assertion before the existing scope check:

```python
# In .github/workflows/validate.yml > branch-scope-mirror inline script
HEAD = os.environ["HEAD_REF"]   # github.head_ref
BASE = os.environ["BASE_REF"]   # github.base_ref

if kind == "culture":
    if HEAD == "culture/release":
        # Promotion. culture/release may only target main.
        if BASE != "main":
            print(f"ERROR: culture/release may only target main, "
                  f"not {BASE}")
            sys.exit(1)
    else:
        # Per-country culture/<name>. Must enter the review surface.
        if BASE != "culture/release":
            print(f"ERROR: {HEAD} (culture branch) must target "
                  f"culture/release, not {BASE}. Open the PR against "
                  f"culture/release instead.")
            sys.exit(1)
elif kind == "other":
    if BASE == "culture/release":
        print(f"ERROR: non-culture branch {HEAD} may not target "
              f"culture/release. Open against main instead.")
        sys.exit(1)
# kind == "main" is already caught by the existing branch-kind check.
```

The existing scope check (regions/** + SAFE_PATTERNS for kind=culture,
no regions/** for kind=other) runs after the direction check; both must
pass.

`branch_scope.py` itself does not change — the direction rules are about
PR shape, not about a branch's own file scope.

### 1B — Per-country count at culture/release (new `single-culture-scope` job)

New job that fires on PRs targeting culture/release. Asserts the diff
touches exactly one country folder. Catches multi-country drift at the
review surface.

```yaml
single-culture-scope:
  name: Culture release - per-country scope
  if: >-
    github.event_name == 'pull_request' &&
    github.base_ref == 'culture/release'
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Check PR scope
      env:
        BASE_REF: ${{ github.base_ref }}
      run: |
        set -e
        git diff --name-only --diff-filter=ACMRT \
          "origin/${BASE_REF}...HEAD" > /tmp/files.txt
        python3 - <<'PY'
        import sys
        sys.path.insert(0, "tests")
        from branch_scope import SAFE_PATTERNS

        with open("/tmp/files.txt") as f:
            files = [l.strip() for l in f if l.strip()]

        countries: set[str] = set()
        out_of_scope: list[str] = []
        for f in files:
            if f in SAFE_PATTERNS:
                continue
            if f.startswith("regions/"):
                parts = f.split("/")
                if len(parts) >= 3:
                    countries.add(f"{parts[1]}/{parts[2]}")
                    continue
            out_of_scope.append(f)

        errors: list[str] = []
        if out_of_scope:
            errors.append("Files outside regions/<region>/<country>/ and "
                          "SAFE_PATTERNS:")
            errors.extend(f"  - {f}" for f in out_of_scope)
        if len(countries) > 1:
            errors.append(f"PR touches {len(countries)} countries; "
                          "culture/<name> → culture/release accepts "
                          "exactly one:")
            errors.extend(f"  - {c}" for c in sorted(countries))

        if errors:
            print("ERROR: per-country scope violation")
            for line in errors:
                print(line)
            sys.exit(1)

        print(f"OK: scope clean — {len(countries)} country, "
              f"{len(files)} file(s)")
        PY
```

Unit-test in `tests/test_culture_release_scope.py`: single-country
accept, two-country reject, infra-only accept, mixed-with-infra
accept, out-of-regions reject.

---

## Phase plan

### Phase 0 — Persist this plan ✅

This document. Lives in `/tmp/` for the session. Promote to
`docs/migration/` or similar only when the work is far enough along that
codification helps.

### Phase 1 — Branch-shape enforcement at culture/release

**Goal.** Mechanically enforce two rules at once: (a) culture/<name>
branches can only enter via culture/release, not main directly; (b) a
culture/release entry PR touches exactly one country folder.

**Why both in one phase.** They're the same family of check (PR shape)
and they reinforce each other. (a) alone lets a culture/<name> branch
land at culture/release with a multi-country diff. (b) alone lets a
culture/<name> branch skip culture/release entirely — this is what PR
#67 did (head `culture/netherlands-hofstede-bag`, base `main`; passed
existing `branch-scope-mirror` because all files were under
`regions/`). Both gates are needed.

**Changes (two edits to `.github/workflows/validate.yml`).**
- **1A — direction enforcement.** Extend the existing
  `branch-scope-mirror` job's inline Python with target-ref
  assertions:
  - kind=culture, head != culture/release → must target culture/release
  - kind=culture, head == culture/release → must target main
  - kind=other → must not target culture/release
- **1B — single-country scope.** Add new `single-culture-scope` job
  (sketched above) that fires on PRs targeting culture/release.

**Tests.**
- Extend `tests/test_branch_scope.py` (or add `test_pr_direction.py`)
  with the direction matrix: culture/X → culture/release ok,
  culture/X → main reject, culture/release → main ok, culture/release
  → culture/release reject, chore/X → main ok, chore/X →
  culture/release reject.
- Add `tests/test_culture_release_scope.py` with the single-country
  count cases (single accept, two reject, infra-only accept,
  mixed-with-infra accept, out-of-regions reject).
- No changes to `branch_scope.py` itself — both edits live in
  `validate.yml` because they're about PR shape, not branch file
  scope.

**Why first.** Smallest move, biggest structural payoff. Closes the PR
#67 bypass and makes Phases 2–4 reason about "a culture PR" as "one
country entering via culture/release" without caveat.

**Risk.** Low-medium. Job is additive but **1A will break in-flight
PRs that target the wrong base** (PR #67's shape). Two mitigations:
- Open culture/release if it doesn't exist before this phase lands
  (one-time setup).
- Before merging 1A, scan open culture/* PRs targeting main; rebase
  them onto culture/release manually so they aren't stranded by the
  new check.

**Rollout signal.** First culture/<name> → culture/release PR goes
green on both checks. A deliberate test PR shaped like #67
(culture/<name> → main) is red with the direction-enforcement
verdict. A two-country PR into culture/release is red with the
scope verdict.

### Phase 2 — Per-country entry gate + release smoke test

Split into 2a and 2b matching the two gate boundaries.

#### 2a — Per-country entry gate (`culture/<name> → culture/release`)

**Goal.** A country cannot enter culture/release with broken coherence.
Today L4f is documented as advisory and not enforced; this phase removes
the advisory escape hatch at the per-country boundary.

**Changes.**
- In `validate.yml`, mark the existing L0–L4 ladder jobs as required when
  `github.base_ref == 'culture/release'`. They already run; this just
  removes the "advisory" framing in `tests/README.md` and pairs with
  branch-protection rules on culture/release.
- Add `tests/validate_country_bag.py` + Bx (PR #68's validator) as
  hard-required at the same boundary.
- Add the Phase-4 YAML-decisions consistency check at the same boundary.
- Assert `.no-bag-yet` is absent in the touched country folder.
- Document the per-country gate set in `tests/README.md` under a new
  "Per-country entry gate" heading.

**Why this comes second.** This is the gate the Copilot got past on PR
#67. Phase 1 makes the diff legible (one country); Phase 2a puts teeth in
"derived ≈ declared" at the per-country boundary so culture/release stays
coherent as it accumulates.

**Risk.** Medium. In-flight PRs that depend on the advisory framing will
start failing. Mitigate by landing 2a only after the next country PR is
content-complete, so we don't strand work.

**Rollout signal.** First `culture/netherlands → culture/release` PR
that holds red until the seven `culture_dutch_*.md` rewrites bring
derived ≈ declared. Anneke/Jeroen rewrites for NL are the proving ground.

#### 2b — Release smoke test (`culture/release → main`)

**Goal.** Catch cross-country and full-set issues that per-country gates
can't see.

**Changes.**
- New `release-smoke` job in `validate.yml`, fires only on
  `culture/release → main` PRs. Runs:
  - `test_hofstede_bag_locked` — lock file SHAs match every present bag
  - `test_hofstede_bag_shape` + `test_hofstede_bag_quality` over every
    bag in the repo (not just the touched ones)
  - `test_hofstede_bag_completeness` — every non-exempt country has a
    bag (re-runs after each promotion to surface coverage drift)
  - Re-run of 2a's per-country gates against any country whose files
    have been edited directly on culture/release since the last
    promotion (paranoia mode; cheap)
- No L4f rerun if 2a was clean and culture/release wasn't edited
  directly between PRs.

**Why this is also second.** Smoke tests are mostly redundant when 2a
holds, but they catch the specific case where someone edits country
files directly on culture/release between accumulating PRs.

**Risk.** Low. Mostly re-runs of existing tests; new check is the
"directly edited on culture/release" detection.

### Phase 3 — Coupling smell on culture/release PRs

**Goal.** Surface bag-without-content (and content-without-bag) drift as
a visible signal earlier than the promotion gate.

**Changes.**
- New advisory job `bag-content-coupling` in `validate.yml`, fires on PRs
  into culture/release.
- Logic: for each `regions/<region>/<country>/` touched in the diff,
  flag if `hofstede_bag.yaml` is in the diff but no `culture_*.md` is
  (or vice versa). Output is a check-run comment, not a hard fail.
- Exception: PRs touching only `hofstede_bag.yaml` +
  `hofstede_decisions.md` + `hofstede_bag_locks.yaml` (the "bag bootstrap"
  shape) get a special note: "bag landed without content; promotion will
  fail L4f until culture_*.md rewrites land".

**Why third.** Phase 2 catches the cheat at promotion; Phase 3 makes the
cheat visible while there's still room to fix it.

**Risk.** Low. Advisory only. The bootstrap shape is explicitly tolerated
inside culture/release.

**Rollout signal.** PR similar in shape to #67 gets the "bag landed
without content" advisory and either the content rewrite follows or the
PR is closed.

### Phase 4 — Canonical decisions log (generator + hooks + CI + DK/DE/NL migration)

**Goal.** One canonical structure for `hofstede_decisions.md`. Three
machine-managed blocks (Section 1 band-range table, Section 5 final
bags, Section 5b country denylist) generated from `hofstede_bag.yaml`
with HTML-marker delimiters. Everything else (Sections 2/3/4/6/7/8) is
human-authored. Drift becomes structurally impossible — pre-commit hook
regenerates on every bag commit, CI re-checks on every PR, and the
contract is documented + tested.

**Choice B confirmed (2026-05-11): canonical scope.** All four migrated
countries (DK / DE / NL / future PL) converge on the same section
structure. DK/DE gain the three generated blocks; NL's drift is cleaned
by re-running the generator. No format heterogeneity in the repo.

**Canonical section structure.**

| # | Section | Required? | Audience | Source |
|---|---|---|---|---|
| Header | country, scores summary, generated date | yes | both | hand-edited |
| 1 | Scores and calibration (band-range table) | yes | both | **generated** (band column, range labels) |
| 2 | Conflict resolution table | recommended | human | human prose |
| 3 | Drops from previous bag | recommended | human | human prose (or "N/A: fresh bootstrap") |
| 4 | Cross-language consistency flags | recommended | human | human prose |
| 5 | Final bags (confirmed) | yes | both | **generated** from YAML `bags:` |
| 5b | Country denylist | yes | both | **generated** from YAML `denylist:` |
| 6 | Per-word justification | optional | human | human prose (or "See Section 7") |
| 7 | Decision logs (per-dimension) | yes | human | human prose |
| 8 | Native-speaker check items | recommended | human | human prose (or empty bullet list) |

The three machine-managed blocks (1, 5, 5b) are wrapped in HTML markers
so the generator knows what region to replace:

```markdown
<!-- BEGIN GENERATED: section-5 -->
...generated content...
<!-- END GENERATED: section-5 -->
```

Edits inside the markers are clobbered on the next `--write`; edits
outside are preserved.

**Sub-phase breakdown (5 PRs).**

#### 4a — Generator + tests (chore PR)

- New `scripts/generate_decisions_sections.py` with two modes:
  - `--check <country-folder>` — exits 1 if the existing markdown
    doesn't match what the generator would emit for the three managed
    blocks. Used by CI.
  - `--write <country-folder>` — rewrites the three blocks in place.
    Used by the pre-commit hook and by authors.
- New `tests/test_generate_decisions_sections.py` — unit tests
  pinning: header parsing, marker detection, idempotent --write,
  --check failure modes, three-block output schema.
- Doesn't touch `regions/` — chore branch, lands first.

#### 4b — Pre-commit hook integration (chore PR)

- Extend `.githooks/pre-commit` so on culture branches, if
  `hofstede_bag.yaml` is staged AND a sibling `hofstede_decisions.md`
  exists, run `--write` and re-stage the decisions file. Drift becomes
  impossible at commit time.
- New `tests/test_hook_decisions_regen.py` adds E2E coverage in the
  pattern of `tests/test_hook_scope_e2e.py`.

#### 4c — CI validator (chore PR)

- Wire `--check` into the existing bag-integrity workflow job, or add
  a new `decisions-consistency` job. Fires on every PR that touches
  `regions/<country>/hofstede_bag.yaml` or `hofstede_decisions.md`.
- Soft-warn at first (does not block merge) so DK/DE/NL can soak
  through their migration PRs.

#### 4d — Country migrations (three culture PRs, one per country)

Each one is `culture/<country>-decisions-canonical`, single-country
diff, touches only `regions/<region>/<country>/hofstede_decisions.md`.

- **Denmark** — insert the three generated blocks (Section 1, 5, 5b).
  Rename existing sections to canonical numbering ("Drops from
  previous bag" → "Section 3: Drops from previous bag", etc.). Add
  empty Section 6 with "See Section 7 for justification".
- **Germany** — same shape as Denmark.
- **Netherlands** — re-run generator on existing markers (drift fix
  for Sections 1, 5, 5b). Section 6 stays as-is (NL has per-word
  justification authored). Section 7 line 335 (resultaat → kortzichtig
  collision resolution) hand-edited as a one-off.

#### 4e — Flip CI from warn to hard-block (chore PR)

Last PR. Promotes the `--check` failure from advisory to merge-blocking.
Lands only when 4d's three migrations are on main and `--check` is
green across the repo.

**Sequencing.**

```
4a (chore) ──► 4b (chore) ──► 4c (chore, soft warn) ──► 4d × 3 (culture) ──► 4e (chore, hard block)
```

4a → 4b → 4c can run sequentially as small chore PRs. 4d's three
migrations can run in parallel (different culture branches, different
files). 4e gates on all three migrations being green.

**Risk.**

Medium. The biggest risk is the migration PRs (4d) — DK and DE
decisions logs grow new sections and gain canonical section numbering.
Each migration PR is ~80 lines of structural insertion + heading
renames. Reviewable by hand. NL is the easiest of the three
(re-running the generator on already-marked sections, plus the one
Section 7 hand-edit).

**Audience preserved.** Human authors still own Sections 2, 3, 4, 6,
7, 8 — the narrative content. Sections 1 / 5 / 5b become read-only
mirrors of the YAML, regenerated at every commit. No drift possible.

**Why this scope.** User direction (2026-05-11): "it should be one
structure, well guarded with hooks and CI and everything". Choice B
(canonical across DK/DE/NL) over Choice A (NL-only) or Choice C (drop
generated sections, narrative-only). Trade-off: bigger one-time
migration cost in exchange for a single canonical shape and zero
drift afterward.

**Rollout signal.** A culture PR edits `hofstede_bag.yaml`, the
pre-commit hook regenerates Sections 1/5/5b, CI `--check` is green,
no further hand-editing of the generated blocks needed.

### Phase 6 — Band vocabulary (Low / Moderate / High) ✅ SHIPPED (modulo 6a + Poland prose line)

**Shipped 2026-05-11.** Phase 6 landed on `main` via four PRs:

| PR | Layer | Commit |
|---|---|---|
| #71 | L4e validator: regex `(Low\|Moderate\|High)` closed-bold + `score_to_band` + mismatch check + 12 tests | b0a7cf6 / merge c2dca10 |
| #73 | `scripts/audit_readme_bands.py` (table audit) | 89941c3 / merge d46e494 |
| #74 | Data fixes: DE IND 40 Low→Moderate, NL UAI 53 High→Moderate (on `culture/...` branch) | 0fac086 / merge 0c6e0fa |
| #75 | Audit extension: prose `**<Band> <DIM>:**` pairs with Medium→Moderate normalization | ace2713 / merge e931396 |

Post-landing state:
- L4e passes for all four migrated countries (Denmark, Germany,
  Netherlands, Poland).
- 84 tests green in the L4e + bag suites + branch-scope tests.
- Audit script reports **1 prose mismatch on main**:
  `poland prose:L54 IDV 60 Medium expected High` — Poland's
  `**High PDI + Medium IDV:**` line uses non-canonical "Medium" AND
  wrong band ("Moderate" should be "High" since IDV 60 sits in
  High band, 60-100).

**Sequencing lesson (worth keeping).** My original plan ordered
6a → 6b (audit-fix) → 6c (validator), but 6b alone would have
cascade-failed L4e because the old regex didn't accept "Moderate".
The team reorganized to:
6c (validator, chore branch, touches no `regions/`)
→ audit script split out as its own chore PR (#73)
→ data fixes on a `culture/...` branch (#74, allowed to touch
  `regions/`)
→ prose-audit extension (#75) — caught a class of drift the
  table-only audit missed.

This sequencing avoided the chore-touching-regions branch-scope
problem entirely. Lesson for future phases: when a Phase needs to
edit both `tests/`/`scripts/` AND `regions/<country>/*.md`, split
the chore work and the culture data fixes into separate PRs with
the matching branch kind. Combined PRs would require either a
branch-kind exemption or a multi-country culture branch (both
worse than the split).

---

#### Phase 6 — Remaining work

##### 6a — Skill update (cross-repo, still owing)

Status: not yet started. Cross-repo work in `ChBrain/KAIHACKS` /
`khai-cultures-review` SKILL.md. See original 6a spec below.

##### 6d — Poland prose line (small follow-up)

Status: ready to ship. One-line edit on a `culture/poland-...` branch:
`regions/europe/poland/README.md:54` from
`**High PDI + Medium IDV:**` to `**High PDI + High IDV:**`. Brings
the audit script to 0 mismatches on main.

##### NL decisions.md drift (Phase 4 territory, not 6)

`regions/europe/netherlands/hofstede_decisions.md` on main carries
three flavors of drift that Phase 4 (generator) is designed to
clean up systematically:
- Section 1 band ranges: `Low (31-50)` and `Moderate (51-65)` are
  wrong under the new contract (Low is 0-39, Moderate is 40-59).
- Section 5 LTO_low still lists `resultaat`; YAML correctly has
  `kortzichtig`.
- Section 5b denylist still lists `autonomie / consensus /
  gelijkheid / pragmatisch / spontaan / vrijheid / solidariteit /
  samenwerking / informeel` as denylist entries — all live in
  resolved bags; YAML denylist correctly omits them.

These three are exactly what Phase 4's generator (Section 5/5b
from YAML at commit time + Section 1 band-range table) would fix
mechanically. Section 1's band ranges are a new third
generator-managed block worth folding into Phase 4's scope.

---

#### Phase 6 — Original spec (kept for reference)

**Promoted to next concrete action** (2026-05-11). Independent of the
bag/content coupling phases; small mechanical scope; catches a class of
semantic error CI currently misses; unblocks PR #67's NL UAI-53 issue.

**Goal.** Replace today's `Low / High / Very High` with `Low / Moderate /
High` as the validated Level vocabulary, separate the band label from
the qualitative classifier, and add a band-matches-score check that
catches the semantic error currently invisible to CI (NL UAI 53 marked
"High").

**Vocabulary contract.**

| Score range | Band (validated, Level column) | Classifier (free prose, Description column) |
|---|---|---|
| 0-19  | Low | Very Low |
| 20-39 | Low | Low |
| 40-59 | Moderate | Moderate (no sub-classifier — score number carries the nuance) |
| 60-79 | High | High |
| 80-100 | High | Very High |

The Level column is machine-validated as one of {Low, Moderate, High}
and must equal `score_to_band(score)`. The Description column carries
any classifier the author chooses, including "Very Low" / "Very High";
the validator does not parse Description prose.

**Three sub-phases, sequenced 6a → 6b → 6c.** Each is a separate PR.

#### 6a — Skill update (`ChBrain/KAIHACKS`)

**Repo.** `ChBrain/KAIHACKS` (cross-repo; not this repo).

**Changes.** Edit `khai-cultures-review` SKILL.md:
- Replace the current `0-39 Low / 40-59 Medium / 60-100 High` band
  table with `0-39 Low / 40-59 Moderate / 60-100 High`.
- Add the classifier convention table (Very Low / Low / Moderate /
  High / Very High) with a clear note: classifier is description-only
  prose, not validated, and the Level column must be the band.
- Add a worked example (NL UAI 53 → Level=Moderate, Description="…
  near-middle …") to lock in the pattern.
- Bump SKILL.md version; coordinate with whoever cuts the
  `khai-tests-v0.X.X` release that this Cultures repo's CI consumes.

**Why first.** Copilot must start emitting the new vocabulary before
the validator starts rejecting the old one, otherwise every culture PR
goes red until Copilot is re-pulled.

**Rollout signal.** A new culture review run by Copilot produces a
README with `Moderate` for a 40-59 score and the classifier convention
in the description.

#### 6b — README audit script + audit-fix PR (this repo)

**Repo.** `ChBrain/Cultures` (this repo).

**Changes.**
- New `scripts/audit_readme_bands.py`. For every
  `regions/<region>/<country>/README.md`, find Hofstede table rows,
  compute `score_to_band(score)`, and report mismatches. Output format:
  `country | dimension | score | declared_level | computed_band |
  needs_change`.
- Run the script; bundle the mismatches into one PR on
  `chore/band-vocabulary-audit-fix` that edits the affected README
  Level cells. Each cell edit is mechanical (Low/High → Moderate, or
  Very High → High, or 40-59 mis-labelled → Moderate).
- Known cost across migrated countries: Denmark 0, Germany 1 (IND 40),
  Netherlands 2 (IDV 80, UAI 53), Poland 0. ~194 non-bagged READMEs
  pending audit-script output.
- Land 6b after 6a is shipped + Copilot pulled the new SKILL.md.

**Why second.** The audit must run before the validator change; the
audit fix must land before the validator change. Otherwise the
validator change cascade-fails every legacy README.

**Rollout signal.** Audit script reports 0 mismatches across the repo.

#### 6c — Validator change (this repo)

**Repo.** `ChBrain/Cultures` (this repo).

**Changes.** Edit `tests/validate_hofstede_alignment.py` (L4e):

1. Regex at line 99 changes from
   `\*\*(Low|High|Very High)[^\|\n]*\|` to
   `\*\*(Low|Moderate|High)[^\|\n]*\|`.
2. New `score_to_band(score)` function plus a mismatch check in
   `check_structure` (or a sibling check). When
   `extract_hofstede_scores` yields `(dim, score, level)`, assert
   `level.title() == score_to_band(score)`. Raise an `Issue` on
   mismatch with verdict
   `"set Level to {band} (score {score} sits in the {band} band, 0-39
   Low / 40-59 Moderate / 60-100 High)"`.
3. Update tests in `tests/` that exercise L4e to cover: Moderate
   accepted at 50; mismatch rejected (Level=High at score 53);
   `Very High` rejected in Level column; classifier prose tolerated in
   Description column.
4. Update the regex docstring at line 88 of the file to drop the
   "Very High" allowance and add the band-mismatch behaviour.

**Why third.** Load-bearing change. The enum swap alone is cosmetic;
the mismatch check is what catches the semantic error. Land only after
6a + 6b are done so CI doesn't break on day one.

**Why this is the load-bearing change.** Without the mismatch check,
the enum swap trades one set of accepted strings for another. The
Copilot self-analysis quoted earlier ("PDI 100 derived vs 38 declared")
is one shape of the cheat; "Level=High at score 53" is another, and
the mismatch check is the only mechanism that closes it.

**Rollout signal.** First culture PR where Level reads `Moderate` for
a 40-59 score, Description carries the classifier prose, and L4e
passes. NL UAI 53 going `Moderate` is the canonical test. Then: a
deliberate test PR that puts `High` at score 53 and confirms L4e
rejects it with the verdict line.

**Risk across 6a–6c.** Medium. The cross-repo handoff is the main one;
the rest is mechanical. Sequencing 6a → 6b → 6c prevents cascade
failure during the cutover.

### Phase 5 — Migrate in-flight work

**Goal.** Bring PRs #67, #68, and the `claude/netherlands-hofstede-bags-vS7RV`
branch onto the new contract.

**Changes.**
- PR #68: blocked on the e2e fix already commented; once that's in, it
  lands and the new Bx validator is available to Phase 2.
- PR #67: under the new contract, this is a culture/release PR that
  isn't ready to promote. Two paths:
  - (a) Keep it open on culture/release; do the seven `culture_dutch_*.md`
    rewrites in the same branch so derived ≈ declared, then promote.
  - (b) Close PR #67; reopen as a culture/release PR with bag + decisions
    + content in one shot.
  - Either way, Section 5/5b drift in decisions.md must be fixed.
- `claude/netherlands-hofstede-bags-vS7RV`: rename to something matching
  the convention (e.g. `culture/netherlands` if not already taken, else
  open a culture/release PR from it). Same content rewrite required for
  promotion.

**Why last.** Phases 1–4 must be the safety net before retroactively
migrating in-flight PRs onto the contract, otherwise we ask the author
to satisfy a contract that isn't enforced yet.

---

## Sequencing

```
                ┌── Phase 6a (Skill) ─► Phase 6b (audit) ─► Phase 6c (validator) ─┐
                │                                                                 │
Phase 0 ────────┤                                                                 ├──► Phase 5
                │                                                                 │
                └── Phase 1 ─► Phase 2a / 2b / 3 / 4 (parallel) ──────────────────┘
```

**Phase 6 runs first as the priority track** (small, mechanical, catches a
real bug). 6a is cross-repo and gates 6b and 6c. 6c only lands once 6a is
shipped and 6b has zeroed out legacy README mismatches.

In parallel, **Phase 1 starts the workflow-gates track**. It unlocks
Phases 2a/2b/3/4 to run in parallel.

**Phase 5** (migrate in-flight PRs onto the new contract) starts once
both tracks have at least one phase landed — minimum: Phase 6c on main
so vocabulary is enforced, plus Phase 1 on main so single-culture scope
is enforced. The rest of 5 follows as the other phases land.

## Resolved decisions

- **Stream model:** `culture/<name>` is single-country; `culture/release`
  is a long-lived multi-country collector; review happens at
  `culture/<name> → culture/release`. (User, 2026-05-11.)
- **Gate boundaries:** per-country gates fire at `culture/<name> →
  culture/release`; release smoke test fires at `culture/release →
  main`. (User, 2026-05-11.)
- **Decisions log audience:** markdown stays primary for human-authored
  sections (1, 2, 3, 4, 6, 7, 8). Sections 5 and 5b are generated from
  YAML — primary audience for those two is the same machine pipeline
  that reads the YAML. (User-led framing, generator chosen, 2026-05-11.)

## Open questions

- **Bx vs `validate_country_bag.py` overlap.** PR #68 adds
  `validate_hofstede_bag_denylist.py` (Bx) which overlaps with the
  existing `validate_country_bag.py` (denylist coherence, collisions,
  word counts). Do we keep both, fold one into the other, or split
  responsibilities? Resolve before Phase 2a wires both into the per-
  country gate.
- **branch-protection on culture/release.** Phase 2a relies on
  branch-protection rules to make the existing L4 jobs required. Need to
  confirm we can set those on culture/release without manual ops each
  promotion cycle.
- **Migration order in Phase 5.** Land Phase 1 → Phase 4 → Phase 2a so
  that by the time the per-country gate hardens, decisions logs are
  already drift-proof. Or land 2a first to apply pressure? Decide before
  Phase 5 starts.

## Update log

- 2026-05-11: Phase 0 — initial plan persisted.
- 2026-05-11: Refined stream model (culture/<name> single, culture/release
  collector); split Phase 2 into 2a (per-country entry) and 2b (release
  smoke test); Phase 4 switched from parser to generator; resolved
  decisions section added.
- 2026-05-11: Added Phase 6 (Band vocabulary Low/Moderate/High). Corrected
  validator location to `validate_hofstede_alignment.py` (L4e). Added
  score-to-band mismatch check as the load-bearing change. Flagged
  cross-repo Skill coordination for `khai-cultures-review`. Sized
  migration cost: DK 0, DE 1 (IND 40), NL 2 (IDV 80, UAI 53), PL 0,
  ~194 non-bagged countries pending audit.
- 2026-05-11: Phase 6 promoted to next concrete action. Split into 6a
  (Skill update, cross-repo), 6b (README audit + fix PR), 6c (validator
  regex + mismatch check). Sequenced 6a → 6b → 6c. Sequencing diagram
  redrawn with Phase 6 as the priority track parallel to Phase 1's
  workflow-gates track. Phase 5 now requires at least Phase 6c + Phase 1
  on main before starting.
- 2026-05-11: Phase 1 expanded to cover direction enforcement (1A) AND
  single-country scope (1B). 1A extends `branch-scope-mirror` to reject
  culture/<name> → main and chore → culture/release. Motivated by PR
  #67 (head culture/netherlands-hofstede-bag, base main) bypassing the
  intended culture/release review surface — passed CI because the
  existing mirror only checks head-branch file scope, not target.
  Direction matrix added to test plan. Risk note: 1A will break
  in-flight PRs with PR #67-shape; mitigate by pre-rebase before
  merge.
- 2026-05-11: Phase 6 shipped on main via PRs #71 (validator), #73
  (audit script), #74 (data fixes on culture branch), #75 (prose-audit
  extension). Outstanding: 6a (cross-repo Skill update), Poland prose
  line (one-line `Medium IDV` → `High IDV` on a culture/poland-* PR).
  Sequencing lesson captured: split chore-script + culture-data-fix
  worked cleanly because the chore branch never touched `regions/` and
  the culture branch was single-country (no branch-scope conflict).
  NL decisions.md still carries the three drifts Phase 4 will clean up
  mechanically (Section 1 band ranges, Section 5 LTO_low resultaat,
  Section 5b denylist with moved-words).
- 2026-05-11: PR #76 hardened Phase 6 — 189-line test suite pinning the
  audit script's parsing contract (table, prose, normalize_band,
  score_to_band, Poland Medium-IDV-vs-High-band case) and
  `tests/README.md` sync. Tests-only, no drift surface change. Phase 4
  Choice A/B/C still open.
- 2026-05-11: Phase 4 scope surfaced a format-spread finding (DK/DE
  decisions logs have no Section 5/5b/1, NL does). Three options open:
  A narrow (NL-only generator + drift fix), B canonical (migrate
  DK/DE/NL to a single shape with generator-managed blocks), C slim
  (drop Section 5/5b/1 from NL, converge on DK/DE narrative-only
  shape — no generator needed). User-direction pending.
- 2026-05-11: Phase 4 direction confirmed — Choice B (canonical
  structure) with full enforcement scope ("hooks and CI and
  everything"). Plan refined to 5 sub-phases: 4a generator + tests
  (chore), 4b pre-commit hook integration (chore), 4c CI validator
  (chore, soft-warn), 4d × 3 country migrations (DK/DE/NL culture
  branches), 4e flip CI to hard-block (chore). Issue #77 opened
  carrying the full plan, acceptance criteria, sequencing, and
  coordination notes (mirrors #69 shape for Phase 6).
- 2026-05-11: PR #78 — small docs-only PR adding the
  `python3 -m pytest tests/` invocation guide to `tests/README.md`
  ("Testing locally" section, 8 lines). No regions/, no code, no
  contract change.
- 2026-05-11: Issue #69 audited. Closed-as-completed by ChBrain
  earlier; clarification comment added explaining the two
  out-of-scope outstanding items so future readers aren't confused.
  6a (cross-repo SKILL.md in KAIHACKS) is intentionally a separate
  PR by design. Poland prose drift (`Medium IDV` → `High IDV` in
  `regions/europe/poland/README.md:54`) was surfaced by #75 after
  #69 was opened; will be handled during the next Poland culture
  cycle, not pulled into a tracker now. Net: every in-repo Phase 6
  gate is on `main` and enforced.
