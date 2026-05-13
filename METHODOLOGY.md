# Hofstede Implementation Methodology

*How to build and validate cultures against Hofstede's 6-dimension model.*

## Overview

The Cultures project builds content that maps to Hofstede's cultural dimensions using a **keyword-density validation model**. This document outlines the proven workflow for achieving validated scores within the CI hard gate (±10 tolerance per dimension).

**Key Discovery:** Less is more. Aggressive trimming and keyword purity improve scores more than volume.

### v2 schema awareness

The Hofstede keyword-density method is independent of the file schema -- the validator sums keyword occurrences across all `culture_*.md` files in a country, regardless of how those files are partitioned. The schema that frames *which* files exist, however, has moved from v1 (6 kinds) to v2 (8 kinds). This methodology references both:

- **v2 schema** (8 kinds: language, history, position, process, piece, place, male, female) -- for countries listed in `data/v2_migrated_countries.txt`
- **v1 schema** (6 kinds: language, position, process, piece, place, personas) -- for countries not yet migrated; valid until the migration PR lands

See [`ARCHITECTURE.md`](ARCHITECTURE.md) > Cultures v2 Schema for the full structural contract, including the `*khai: <type>*` declaration footer and the 3-line v2 footer block that every `culture_*.md` carries in v2-migrated countries. The keyword-density rules in this document apply identically to both layouts; the file enumeration shifts but the per-file authoring discipline stays the same.

---

## Scoring Unit: The Culture, Not The File

Scoring is **aggregate across all culture files for a country**, not per-file. The country `README.md` declares the six dimension scores; the surrounding `culture_*.md` files collectively carry the keywords that derive those scores.

In **v2-migrated countries**, the contributing files are: language, history, position, process, piece, place, male, female (8 kinds). In **v1 (legacy) countries**, the contributing files are: language, position, process, piece, place, personas (6 kinds; persona files split into male/female on migration).

- **Validating layer:** `tests/validate_hofstede_derived.py` (L4f) — sums keyword counts across every `culture_*.md` file in the country, derives 0-100 per dimension, compares to README declared, reports gap/status.
- **Structure layer:** `tests/validate_hofstede_alignment.py` (L4e) — checks the README has the section, score table, and source. It does **not** score per-file content.
- **Footer contract:** every culture file in a v2-migrated country ends with a 3-line italicized footer block (see [`ARCHITECTURE.md`](ARCHITECTURE.md) > Footer for the spec):
  - `*hofstede: aggregate in [README.md](README.md).*` — aggregate-score sentinel. The legacy `*Hofstede signal: this file contributes...*` form is accepted during the v2 rollout (per PR #130); canonical is the shorter `hofstede:` form.
  - `*khai: <type>*` — KAI structural type declaration (one of `process`, `position`, `piece`, `place`, `persona`).
  - `*<YYYY-MM-DD> | KAI HACKS AI | v<X.Y.Z> | CC-BY-NC-4.0*` — IP safeguard line; license authoritative in the repo `LICENSE` file.

  Per-file Hofstede score lines (e.g. `**Hofstede:** PDI 35 · IDV 67 ...`) are forbidden — they imply per-file scoring and trigger false alignment failures.

**Practical consequence:** if a dimension is under-represented, you can add keywords to the most natural carrier (e.g. UAI-high → the piece on legal/constitutional structure; IND-high → the process on leisure/celebration) rather than forcing every dimension into the position file. In v2, the natural carriers expand: history can absorb dimensions that emerged from a founding moment (LTO from a constitution), language can absorb formality dimensions (PDI / UAI from address forms), male/female personas can carry MAS / IND.

---

## Core Principles

### 1. Keyword Purity > Volume

- **Validator uses exact word matching** (case-sensitive, no fuzzy matching)
- One ambiguous keyword can shift a dimension by 5-10 points
- Remove all ambiguous words; replace with unambiguous alternatives
- Example: "respekt" appears in both PDI-high and PDI-low → avoid; use "autonomi" or "omsorg" instead

### 2. Distribution > Content Volume

| Reference | Total Lines | Personas | Format | Result |
|-----------|------------|----------|--------|--------|
| Germany   | 216        | 18 lines | Ultra-minimal | 6/6 EXCELLENT (100% pass) |
| Denmark   | 373 (start)| 60 lines | Bloated | 2/5 PASS (40% pass) |
| Denmark   | 240 (final)| 18 lines | Ultra-minimal | 6/6 EXCELLENT (100% pass) |

**Insight:** Trimming Denmark personas from 60 to 18 lines improved validation to 100% pass and boosted IDV and LTO.

### 3. Band Contract

Canonical Hofstede bands (pinned by `scripts/audit_readme_bands.py` + `tests/test_audit_readme_bands.py`):

| Score range | Band |
|---|---|
| 0-39 | Low |
| 40-69 | Moderate |
| 70-100 | High |

"Medium" is an accepted prose alias for "Moderate" (audit normalizes for equivalence but surfaces the non-canonical word as `declared`). When authoring a country's README, the band label in each row must agree with `score_to_band(score)`. Prose like `**Low PDI + High IDV:**` in the "How Dimensions Shape This Culture" paragraph is audited the same way.

### 4. File Structure Matters

**High-Impact Files (Dense with Target Keywords):**
- **Position** (~50 lines): Defines core cultural operating principles; ultra-dense with target dimension keywords only
- **Language** (~30 lines): Communication values; focus on 1-2 dimensions max

**Nuance Files (Supporting Detail):**
- **History** (~30 lines, v2): Pivotal moment where one or two dimensions emerged or were tested -- a founding document, war, or settlement
- **Piece** (~30 lines): Load-bearing cultural artifact or concept (in v2: distinct from history)
- **Process** (~30 lines): One core cultural practice or ritual
- **Place** (~35 lines): Geographic/infrastructure signals

**Ultra-Minimal Files:**
- **Male / Female personas** (18 lines each, v2): Concrete embodiments of cultural values, gender encoded in filename
- **Personas** (18 lines each, v1): Same compression rules; gender encoded only in `## Projection` link

### 5. Language-Specific Keywords Enable Accuracy

- Without Danish keyword bags, content was scored as English → inaccurate dimension mapping
- ~300+ verified terms per language minimum, organized by all 6 dimensions
- Language detection: ≥3 marker threshold or match existing language count
- Example markers (Danish): æ/ø/å characters, "den", "det", "er", "jeg", "har"

### 6. khai declaration footer (v2)

Every `culture_*.md` in a v2-migrated country carries a `*khai: <type>*` footer where `<type>` is one of `process`, `position`, `piece`, `place`, `persona`. The filename token and the footer must agree:

| Filename | khai footer |
|---|---|
| `culture_<adj>_language_*.md` | `*khai: position*` |
| `culture_<adj>_history_*.md` | `*khai: piece*` |
| `culture_<adj>_position.md` | `*khai: position*` |
| `culture_<adj>_process_*.md` | `*khai: process*` |
| `culture_<adj>_piece_*.md` | `*khai: piece*` |
| `culture_<adj>_place_*.md` | `*khai: place*` |
| `culture_<adj>_male_*.md` | `*khai: persona*` |
| `culture_<adj>_female_*.md` | `*khai: persona*` |

KAIHACKS `khai-tests` v0.1.6 reads the footer to apply the right structural contract (section order, fields, links); the Cultures-side completeness check reads the filename token. A mismatch is a hard fail.

---

## Implementation Phases

### Phase 1: Position File (Core Architecture)

**Purpose:** Establish the primary dimension targets through unambiguous keywords.

**Structure:**
```markdown
# Position: <Culture>

## Has
[Positive keyword section - only target dimensions]

## Orders
[Prescriptive principles - what should happen]

## Loses
[Negative section - what should NOT happen]
```

**Guidelines:**
- Consolidate all primary keywords for target dimensions here
- Move ambiguous keywords OUT of other files into position only
- Avoid: filler words, cross-dimension keywords, explanatory phrases
- Target: 50 lines max, zero ambiguity
- In v2: end the file with the 3-line footer (`*hofstede:`, `*khai: position*`, IP line)

**Example (Danish):**
- Target PDI 18 (very low hierarchy) → fill position with "lighed", "demokratisk", "autonomi", "ligeværd"
- Remove all PDI-high words ("hierarki", "ledelse", "autoritet")

### Phase 2: Language-Specific Keyword Bags

**Purpose:** Enable accurate scoring in target language.

**Process:**
1. Identify all 6 dimensions in target language
2. Create ~50 keywords per dimension (300+ total)
3. Verify against content to ensure density is achievable
4. Test language detection markers

**Example (Danish Keywords):**

| Dimension | High Keywords | Low Keywords |
|-----------|---------------|--------------|
| PDI | hierarki, status, ledelse | lighed, demokratisk, ligeværd |
| IDV | individuelt, personlig, autonomi | gruppe, fællesskab, samarbejde |
| UAI | regel, struktur, orden, sikkerhed | fleksibel, pragmatisk, improvisere |
| MAS | præstation, succes, konkurrence | omsorg, empati, medmenneskelig |
| LTO | fremtid, plan, investering | nu, øjebliklet, spontan |
| IND | nyde, nydelse, frihed, hygge | disciplin, selvkontrol, pligt |

### Phase 3: Supporting Files (1-2 Dimensions Each)

**History File (~30 lines, v2 only):**
- Pivotal historical moment where dimensions emerged or were tested
- Target 1-2 dimensions (commonly LTO + one other)
- Compress: When + What happened + Why it still matters
- Example: Grundgesetz (Germany's 1949 constitution; LTO-high through deliberate constitutional design)
- khai footer: `*khai: piece*` (history maps to the KAI piece structural type)

**Piece File (~30 lines):**
- Cultural artifact, work, or concept (in v2: artifact / concept only; pivotal moments belong in history)
- Target 1 primary dimension, mention 1 secondary
- Compress: Essence + brief origin + cultural implications only
- Example: Janteloven (Danish equality principle)
- khai footer: `*khai: piece*`

**Language File (~30 lines):**
- Communication style and values
- Target 1-2 dimensions
- Structure: Has/Orders/Loses format (like position, shorter)
- Example: Dansk (Danish language values)
- khai footer: `*khai: position*` (language maps to the KAI position structural type)

**Process File (~30 lines):**
- One core cultural practice (ritual, tradition, social process)
- Target 1-2 dimensions
- Narrative: Origin → How it works → What it means
- Example: Hygge (Danish coziness practice)
- khai footer: `*khai: process*`

**Place File (~35 lines):**
- Geographic or infrastructure signals of cultural values
- Multiple subtle dimension indicators
- Structure: Shown/Holds/Offers/Withheld sections
- Example: København (Copenhagen as cultural mirror)
- khai footer: `*khai: place*`

### Phase 4: Personas (Male / Female, Ultra-Minimal, 18 Lines)

**Purpose:** Embody cultural values through concrete human examples. In v2 each country has at least one male persona file and at least one female persona file, with gender encoded in the filename.

**Naming:**
- v2: `culture_<adj>_male_<name>.md` for male personas, `culture_<adj>_female_<name>.md` for female personas
- v1 (legacy): `culture_<adj>_persona_<name>.md` (gender visible only inside the Projection link)

**khai footer:** `*khai: persona*` for both male and female files.

**Structure (18 lines total):**
```markdown
## Projection (2 lines)
<Name> is a <gender> from <Culture>.
<One core cultural concept>.

## Action (2 lines)
<Concrete scenario showing cultural value in practice>.
<How they handle it differently than other cultures>.

## Shadow (1 line)
<Their blind spot or unexamined assumption>.

## Tell (1 line)
<Essence - what makes them distinctly from this culture>.
```

**Compression Rules:**
- Remove all titles, explanations, meta-phrases
- Each concept = 1-2 words, not sentences
- One narrative element per section, not multiple examples
- Mirror reference model's ultra-minimal style

**Example (Danish, v2 filename `culture_danish_male_lars.md`):**

```markdown
## Projection
Lars is a [man](../../../engine/position_male.md) from [Danmark](culture_danish_position.md).
Egen bedømmelse altid først. Autonomi er hans værktøj.

## Action
I mødet siger han straks hvad han ser. Gruppen hører eller hører ikke. 
Han accepterer det uden at påtvinge.

## Shadow
Han tror han er neutral. Han har stærk mening og glemmer at andre 
har samme ret.

## Tell
Del først, lyt efter. Autonomi gennem respekt for begge.
```

### Phase 5: Validation & Iteration

**Step 1: Initial Validation**
```bash
python tests/validate_hofstede_derived.py 2>&1 | Select-String -Pattern "^<culture>:" -Context 0,10
```

**Step 2: Gap Analysis**
- Identify FAIL (>±20), WARN (±10-20), PASS (±10), EXCELLENT (±5)
- Prioritize: Fix FAIL first, then WARN, then PASS

**Step 3: Targeted Fixes**
- Only add/remove keywords in target dimension's files
- Never cross-pollinate dimensions (keep IDV keywords OUT of UAI files)
- Revalidate after each major change

**Step 4: Band Audit**
- Run `python3 scripts/audit_readme_bands.py --mismatch` to flag any README band labels that disagree with the score's canonical band (0-39 Low, 40-69 Moderate, 70-100 High)
- Or run `python3 scripts/update_hofstede_readme.py <country>` to deterministically rewrite the README's Hofstede tables with canonical bands and current derived scores
- Fix mismatches in the score table cell and in any prose mentions

**Step 5: Compression Phase (If All Pass)**
- Once all 6 dimensions pass, aggressively trim files
- Remove filler words, explanatory phrases, redundant keywords
- Revalidate: Trimming often improves scores by removing competing keywords

---

## Troubleshooting Matrix

| Problem | Root Cause | Diagnostic | Solution |
|---------|-----------|-----------|----------|
| Dimension at 50 | Equal high/low keywords | File balance is 50-50 split | Move all ambiguous words OUT; consolidate in position file only |
| Dimension stuck below target | Competing dimension keywords | Count keywords from other dimensions | Remove filler keywords; use only unambiguous target terms |
| Dimension overcorrected (opposite extreme) | Added excessive opposite keywords | Previous version had opposite extreme | Find middle ground: 60-40 split, not 100-0 |
| UAI at 100 (max uncertainty avoidance) | Entirely missing UAI-low keywords | No fleksibel, pragmatisk, improvisere | Add UAI-low keywords; balance with some order/structure |
| IDV stuck below authentic target | MAS-low keywords (omsorg, empati) competing | Keywords overlap as filler | Remove omsorg/empati from IDV files; use only autonomi/personlig |
| IND at 100 (max indulgence) | Excessive IND-high keywords | Files full of frihed, nydelse, hygge | Restore IND-low (disciplin, selvkontrol); find 50-50 balance |
| MAS stuck at 33 (high masculinity) | Removed all MAS-high but missing MAS-low | No omsorg, empati, medmenneskelig | Add explicit MAS-low keywords; distribute across multiple files |
| All dimensions pass but at boundary | Keyword distribution fragile | Scores at ±10 limits | Aggressive trim: remove competing keywords → often improves to ±5 |
| Band audit flags a row | README label disagrees with `score_to_band(score)` | `audit_readme_bands.py --mismatch` | Fix the table cell and any prose mention; bands are 0-39 / 40-69 / 70-100. Or run `update_hofstede_readme.py <country>` for a deterministic rewrite. |
| khai footer / filename mismatch (v2) | Filename token disagrees with footer type | `tests/test_completeness.py` flags it | Fix the `*khai: <type>*` line; persona files take `persona`, history takes `piece`, language takes `position` |

---

## Reference Models

Both reference models are currently authored in v1 layout (7 files each: position, language, piece, place, process, 2 personas). The keyword-density scores below are content-derived and do not depend on schema layout; once Germany and Denmark complete their v2 migration PRs, they will have 8 files each (history split out from piece; personas split into male and female) with the same dimensional content distributed across the new layout.

### Germany (100% Pass Baseline)

**Files (v1):** 7 content files (~216 lines total)
**Structure:**
- Position: Hierarchy/autonomy tension
- Language: Hochdeutsch communication style
- Process: Erinnern (Memory/Historical reckoning)
- Piece: Grundgesetz (Constitutional foundation) -- *in v2 this becomes history; an authentic artifact piece is authored alongside*
- Place: Berlin (Divided history as cultural mirror)
- Personas: Brigitte (Lawyer, autonomous judgment), Christian (Developer, practical autonomy) -- *in v2 these become `culture_german_female_brigitte.md` and `culture_german_male_christian.md`*

**Validation Scores:**
- PDI: 25 vs 35 declared (+10 PASS)
- IDV: 60 vs 67 (+7 PASS)
- UAI: 57 vs 65 (+8 PASS)
- MAS: 66 vs 66 (0 EXCELLENT)
- LTO: 81 vs 83 (+2 EXCELLENT)
- IND: 33 vs 40 (+7 PASS)

**Pattern:** Lean, focused files with zero ambiguity.

### Denmark (Recent Case Study)

**Files (v1):** 7 content files (~240 lines final)
**Structure:**
- Position: Autonomy-restraint paradox (individual freedom + restraint from imposing)
- Language: Dansk personal voice and democratic communication
- Process: Hygge (present-moment togetherness with discipline)
- Piece: Janteloven (Law of Jante - equality through restraint) -- *Janteloven is an artifact concept, stays in piece in v2; a separate history file covers the foundational moment*
- Place: København (Infrastructure reflecting individual autonomy)
- Personas: Lars (Engineer, direct judgment), Sofie (Architect, respecting others' autonomy) -- *in v2 these become `culture_danish_male_lars.md` and `culture_danish_female_sofie.md`*

**Validation Scores (Final):**
- PDI: 28 vs 18 (+10 PASS)
- IDV: 71 vs 74 (+3 EXCELLENT)
- UAI: 33 vs 23 (+10 PASS)
- MAS: 20 vs 16 (+4 EXCELLENT)
- LTO: 40 vs 35 (+5 EXCELLENT)
- IND: 71 vs 70 (+1 EXCELLENT)

**Journey:** Started 373 lines, 2/5 pass → Ended 240 lines, 6/6 pass. Key: Aggressive trimming removed competing keywords.

---

## Next Culture Workflow

### 1. Pre-Implementation

- [ ] Choose target culture with declared Hofstede scores
- [ ] Find reference culture with similar profile (if available)
- [ ] Identify core cultural paradox or tension (like Denmark's autonomy-restraint)
- [ ] Decide v1 or v2 layout (v2 recommended for all new countries; v1 only for incremental work on countries that have not yet migrated)

### 2. Research & Keywords

- [ ] Gather ~50-100 keywords per dimension in target language
- [ ] Identify language markers for detection (unique characters, common words)
- [ ] Verify keywords against 2-3 existing content examples

### 3. Position File Sprint

- [ ] Write position.md (~50 lines, ultra-dense, target dimensions only)
- [ ] In v2: add the 3-line footer (`*hofstede:`, `*khai: position*`, IP line)
- [ ] Validate: Run initial test, check if target dimensions appear
- [ ] Trim: Remove all ambiguous/competing keywords

### 4. Supporting Files

- [ ] Write piece.md (cultural artifact/concept, ~30 lines; khai: piece)
- [ ] In v2: Write history.md (pivotal moment, ~30 lines; khai: piece)
- [ ] Write language.md (communication values, ~30 lines; khai: position)
- [ ] Write process.md (cultural practice, ~30 lines; khai: process)
- [ ] Write place.md (geographic/infrastructure signals, ~35 lines; khai: place)
- [ ] Validate: Run test after each file added

### 5. Personas Sprint

- [ ] In v2: Create 1 male persona (`culture_<adj>_male_<name>.md`, ~18 lines, khai: persona) and 1 female persona (`culture_<adj>_female_<name>.md`, ~18 lines, khai: persona)
- [ ] In v1: Create 2 personas (`culture_<adj>_persona_<name>.md`, ~18 lines each), at least one linking `position_male.md` and at least one linking `position_female.md` via Projection
- [ ] Ultra-compress: Remove all explanations, keep narrative only
- [ ] Validate: Confirm all 6 dimensions still present

### 6. Final Optimization

- [ ] Run full validation: target 4+ dimensions in tolerance (±10)
- [ ] Gap analysis: Fix FAIL/WARN dimensions with targeted keywords
- [ ] Aggressive trim: Remove competing keywords across all files
- [ ] Run `python3 scripts/update_hofstede_readme.py <country>` to sync the README's two Hofstede tables (declared/derived/gap/status under canonical bands)
- [ ] Final validation: 5-6 dimensions should be in tolerance

### 7. Documentation

- [ ] Update country README via `scripts/update_hofstede_readme.py` (deterministic) or by hand if approximation country
- [ ] Document authenticity tradeoffs (if any dimensions don't match target exactly)
- [ ] List keyword sources/references
- [ ] In v2: Add the country slug to `data/v2_migrated_countries.txt` in the same commit as the file renames and the 3-line v2 footer adoption

---

## Validation Command

```bash
cd c:\Code\Cultures

# Full validation
python tests/validate_hofstede_derived.py 2>&1

# Single culture check
python tests/validate_hofstede_derived.py 2>&1 | Select-String -Pattern "^<culture>:" -Context 0,10

# Band audit (canonical 0-39 / 40-69 / 70-100)
python3 scripts/audit_readme_bands.py --mismatch

# Deterministic README sync (rewrites Hofstede tables in country README)
python3 scripts/update_hofstede_readme.py <country>
python3 scripts/update_hofstede_readme.py <country> --dry-run
```

---

## FAQ

**Q: Why does aggressively trimming improve scores?**
A: The validator is literal. Filler words and competing keywords reduce precision. Removing them concentrates the signal in target dimensions.

**Q: Can I force all 6 dimensions to target?**
A: Rarely. Authentic cultures have natural tensions (like Denmark's autonomy-restraint paradox). Target ±5 excellent where possible; ±10 pass is the hard gate.

**Q: What if I only pass 4 dimensions?**
A: That's acceptable for initial merge. Document why 2 dimensions don't match (cultural authenticity tradeoff). Plan Phase 2 optimization.

**Q: How many languages can one culture support?**
A: Theoretically unlimited. But implementation starts with primary language. Add secondary languages after primary passes validation.

**Q: Does word order matter?**
A: No. Validator counts keyword occurrences, not position. Density (keyword count / total words) is what matters.

**Q: Do I need to migrate to v2 to author a new country?**
A: New countries should be authored in v2 directly (8 kinds, khai footers, 3-line v2 footer, country slug added to `data/v2_migrated_countries.txt`). The v2-strict L4a validator runs only against listed countries, so an unmigrated country authored in v2 still passes; listing it activates the strict checks. v1 layout is only meaningful for countries that already exist in v1 and have not yet been touched.

**Q: Where does the piece-vs-history split sit?**
A: A piece is an artifact, work, or concept (a constitution, a film, a movement, an idea). A history is a dated pivotal moment with a yearbook of events. In v1, both lived in `piece_*`. In v2, history gets its own file so pieces can stay focused on the artifact's load-bearing quality without mixing in dated context.

---

## Version History

- **v0.2.0** - v2 schema awareness (May 2026)
  - Added v2 schema callout (8 kinds, khai footer, per-country opt-in)
  - Added Band Contract principle (canonical 0-39 / 40-69 / 70-100)
  - Added khai declaration footer principle with filename-token agreement table
  - Phase 3 expanded to cover History as its own kind (v2 only)
  - Phase 4 split into Male / Female persona authoring with v2 filename guidance
  - Reference models annotated with v2 migration notes (file content unchanged)
  - Next Culture Workflow updated with v2 steps (khai footers, v2 list opt-in)
  - Added Band audit step to validation phase
  - Footer contract bullet updated to the 3-line v2 footer (Option C): `*hofstede:` sentinel, `*khai:` declaration, IP safeguard line
  - Validation Command block + Next Culture Workflow reference `scripts/update_hofstede_readme.py` for deterministic README sync
- **v0.1.0** - Initial methodology from Denmark case study (May 2026)
  - Discovered less-is-more principle
  - Documented 5-phase implementation workflow
  - Created troubleshooting matrix
  - Established 18-line persona format

---

*Last updated: May 13, 2026*
