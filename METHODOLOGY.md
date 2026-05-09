# Hofstede Implementation Methodology

*How to build and validate cultures against Hofstede's 6-dimension model.*

## Overview

The Cultures project builds content that maps to Hofstede's cultural dimensions using a **keyword-density validation model**. This document outlines the proven workflow for achieving validated scores within the CI hard gate (±10 tolerance per dimension).

**Key Discovery:** Less is more. Aggressive trimming and keyword purity improve scores more than volume.

---

## Scoring Unit: The Culture, Not The File

Scoring is **aggregate across all culture files for a country**, not per-file. The country `README.md` declares the six dimension scores; the surrounding `culture_*.md` files (position, language, piece, place, process, personas) collectively carry the keywords that derive those scores.

- **Validating layer:** `tests/validate_hofstede_derived.py` (L4f) — sums keyword counts across every `culture_*.md` file in the country, derives 0-100 per dimension, compares to README declared, reports gap/status.
- **Structure layer:** `tests/validate_hofstede_alignment.py` (L4e) — checks the README has the section, score table, and source. It does **not** score per-file content.
- **Footer contract:** every culture file ends with a `*Hofstede signal: ...*` line pointing at the README. Per-file score lines are forbidden — they imply per-file scoring and trigger false alignment failures.

**Practical consequence:** if a dimension is under-represented, you can add keywords to the most natural carrier (e.g. UAI-high → the piece on legal/constitutional structure; IND-high → the process on leisure/celebration) rather than forcing every dimension into the position file.

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

### 3. File Structure Matters

**High-Impact Files (Dense with Target Keywords):**
- **Position** (~50 lines): Defines core cultural operating principles; ultra-dense with target dimension keywords only
- **Language** (~30 lines): Communication values; focus on 1-2 dimensions max

**Nuance Files (Supporting Detail):**
- **Piece** (~30 lines): Load-bearing cultural object (historical, metaphorical)
- **Process** (~30 lines): One core cultural practice or ritual
- **Place** (~35 lines): Geographic/infrastructure signals

**Ultra-Minimal Files:**
- **Personas** (18 lines each): Concrete embodiments of cultural values; compression is critical

### 4. Language-Specific Keywords Enable Accuracy

- Without Danish keyword bags, content was scored as English → inaccurate dimension mapping
- ~300+ verified terms per language minimum, organized by all 6 dimensions
- Language detection: ≥3 marker threshold or match existing language count
- Example markers (Danish): æ/ø/å characters, "den", "det", "er", "jeg", "har"

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

**Piece File (~30 lines):**
- Load-bearing cultural object or historical concept
- Target 1 primary dimension, mention 1 secondary
- Compress: Essence + brief origin + cultural implications only
- Example: Janteloven (Danish equality principle)

**Language File (~30 lines):**
- Communication style and values
- Target 1-2 dimensions
- Structure: Has/Orders/Loses format (like position, shorter)
- Example: Dansk (Danish language values)

**Process File (~30 lines):**
- One core cultural practice (ritual, tradition, social process)
- Target 1-2 dimensions
- Narrative: Origin → How it works → What it means
- Example: Hygge (Danish coziness practice)

**Place File (~35 lines):**
- Geographic or infrastructure signals of cultural values
- Multiple subtle dimension indicators
- Structure: Shown/Holds/Offers/Withheld sections
- Example: København (Copenhagen as cultural mirror)

### Phase 4: Personas (Ultra-Minimal, 18 Lines)

**Purpose:** Embody cultural values through concrete human examples.

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

**Example (Danish):**

```markdown
## Projection
Lars is a [man] from [Danmark].
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

**Step 4: Compression Phase (If All Pass)**
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

---

## Reference Models

### Germany (100% Pass Baseline)

**Files:** 7 content files (~216 lines total)
**Structure:**
- Position: Hierarchy/autonomy tension
- Language: Hochdeutsch communication style
- Process: Erinnern (Memory/Historical reckoning)
- Piece: Grundgesetz (Constitutional foundation)
- Place: Berlin (Divided history as cultural mirror)
- Personas: Brigitte (Lawyer, autonomous judgment), Christian (Developer, practical autonomy)

**Validation Scores:**
- PDI: 25 vs 35 declared (+10 PASS)
- IDV: 60 vs 67 (+7 PASS)
- UAI: 57 vs 65 (+8 PASS)
- MAS: 66 vs 66 (0 EXCELLENT)
- LTO: 81 vs 83 (+2 EXCELLENT)
- IND: 33 vs 40 (+7 PASS)

**Pattern:** Lean, focused files with zero ambiguity.

### Denmark (Recent Case Study)

**Files:** 7 content files (~240 lines final)
**Structure:**
- Position: Autonomy-restraint paradox (individual freedom + restraint from imposing)
- Language: Dansk personal voice and democratic communication
- Process: Hygge (present-moment togetherness with discipline)
- Piece: Janteloven (Law of Jante - equality through restraint)
- Place: København (Infrastructure reflecting individual autonomy)
- Personas: Lars (Engineer, direct judgment), Sofie (Architect, respecting others' autonomy)

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

### 2. Research & Keywords

- [ ] Gather ~50-100 keywords per dimension in target language
- [ ] Identify language markers for detection (unique characters, common words)
- [ ] Verify keywords against 2-3 existing content examples

### 3. Position File Sprint

- [ ] Write position.md (~50 lines, ultra-dense, target dimensions only)
- [ ] Validate: Run initial test, check if target dimensions appear
- [ ] Trim: Remove all ambiguous/competing keywords

### 4. Supporting Files

- [ ] Write piece.md (cultural object/concept, ~30 lines)
- [ ] Write language.md (communication values, ~30 lines)
- [ ] Write process.md (cultural practice, ~30 lines)
- [ ] Write place.md (geographic/infrastructure signals, ~35 lines)
- [ ] Validate: Run test after each file added

### 5. Personas Sprint

- [ ] Create 2 personas (~18 lines each)
- [ ] Ultra-compress: Remove all explanations, keep narrative only
- [ ] Validate: Confirm all 6 dimensions still present

### 6. Final Optimization

- [ ] Run full validation: target 4+ dimensions in tolerance (±10)
- [ ] Gap analysis: Fix FAIL/WARN dimensions with targeted keywords
- [ ] Aggressive trim: Remove competing keywords across all files
- [ ] Final validation: 5-6 dimensions should be in tolerance

### 7. Documentation

- [ ] Update country README with Hofstede reference table
- [ ] Document authenticity tradeoffs (if any dimensions don't match target exactly)
- [ ] List keyword sources/references

---

## Validation Command

```bash
cd c:\Code\Cultures

# Full validation
python tests/validate_hofstede_derived.py 2>&1

# Single culture check
python tests/validate_hofstede_derived.py 2>&1 | Select-String -Pattern "^<culture>:" -Context 0,10
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

---

## Version History

- **v0.1.0** - Initial methodology from Denmark case study (May 2026)
  - Discovered less-is-more principle
  - Documented 5-phase implementation workflow
  - Created troubleshooting matrix
  - Established 18-line persona format

---

*Last updated: May 8, 2026*
