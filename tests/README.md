# Cultures - Test Strategy

The validation architecture (L0-L4) ensures that every country in Cultures meets minimum content standards and passes format checks. The layer model is designed to be:
- **Traceable** to ARCHITECTURE.md rules
- **Reusable** across worlds (L1a, L1b, L3 copy to Autobahn, KAIWorlds, KAILabs)
- **Extensible** for future rules (L4 can add L4b, L4c validators)

---

## Test layers

```
L0  all commits        validation stamp - proves local validators ran on this exact tree
L1a all files          encoding (UTF-8 no BOM), filenames (ASCII), em-dash, trailing newline
L1b all files          English-only prose (configurable, exception list for proper nouns)
L2  per-file typed     section structure per file type (position, piece, place, persona)
L3  within countries   link integrity (markdown links resolve, no orphaned files)
L4a per-country        culture completeness (minimum file requirements per country)
L4b per-country        audit README with status tables
L4c per-country        audit table consistency (entries match actual files)
L4d per-country        IP/plagiarism heuristics (Wikipedia patterns, date anchors)
L4e per-country        Hofstede structure + dimension alignment (README has section/scores/sources, position reflects claimed dimensions)
L4f per-country        Hofstede derived vs declared (content keywords derive 0-100 scores, compare to README declared scores)
L4g per-country        Hofstede audit table sync (README audit table matches current derived scores)
```

L0 gates everything. L1a gates L1b. L1b gates L2. L2 gates L3. L3 gates L4a. L4a gates L4b. L4b gates L4c. L4c gates L4d. L4d gates L4e. L4e gates L4f. L4f gates L4g.

**L0-L4e are hard-block jobs** (fail PR if any fails). **L4d-L4g are advisory** (warns if issues, do not block PR).

---

## Layer 0: Validation stamp

**Scope:** All commits

The `.validation-stamp` file records the tree hash of the last validated commit. CI gates on this file's presence (not its contents).

- **Purpose:** Proves that local validators ran before commit
- **Location:** `.validation-stamp` at repo root
- **Generated:** Pre-commit hook, after all L1-L4 validators pass
- **CI check:** L0-stamp-check job (hard block)

**Related files:** `.githooks/pre-commit`

---

## Layer 1a: General file format

**Scope:** All markdown files in `regions/**/*.md`

Per-file only. No cross-file reads.

- **Encoding:** UTF-8, no BOM (byte order mark). PowerShell auto-fixes via `.gitattributes` + pre-commit hook.
- **Filenames:** ASCII only (no Unicode), underscores allowed, no spaces
- **Forbidden characters:** Em-dash (U+2014) forbidden - use hyphen instead
- **Trailing newline:** All files must end with newline

**Verdict when failed:** Strip the offending bytes or replace character (specific instruction provided)

**Script:** `tests/validate_general.py`

**Example:**
```bash
python3 tests/validate_general.py regions/europe/germany/culture_german_position.md
# OK: 1 files passed general validation
```

---

## Layer 1b: English-only language policy

**Scope:** All markdown files in `regions/**/*.md`

Checks prose sections for non-English language content using `lingua` library. Proper nouns (Eigennamen) are always allowed.

- **Policy:** English-only by default
- **Configuration:** `ALLOWED_LANGUAGES=english` (env var, can extend to `english,german` later)
- **Sections checked:** Only prose sections (Owner, Projection, Action, Shadow, Tell, Shown, Offers, Withheld, Load Bearing, Apparent, Yearbook, Drives, Loses, Orders)
- **Threshold:** Minimum 15-word span to flag violation (avoids false positives on names)
- **Exception mechanism:** `tests/language_exceptions.txt` - one word/phrase per line, prevents false positives on regional proper nouns

**Verdict when failed:** Rewrite passage in English (specific section indicated)

**Script:** `tests/validate_language.py`

**Example:**
```bash
python3 tests/validate_language.py regions/europe/germany/*.md
# OK: 5 file(s) passed language policy (english)

# With violation:
# FAIL regions/africa/algeria/culture_algerian_position.md: Dutch prose in ## Drives
#   verdict: rewrite the passage in english
```

**Future enhancement:**
- Per-country language support: `ALLOWED_LANGUAGES=english,german` for regions with multilingual heritage
- Regional exception files: `language_exceptions_<region>.txt`

**Related files:**
- `tests/language_exceptions.txt` - Eigennamen exceptions
- `tests/requirements.txt` - lists `lingua-language-detector>=2.0.2`

---

## Layer 2: Section structure

**Scope:** All markdown files in `regions/**/*.md`, per file type

Per-file only. No cross-file reads. Enforces required sections per file type.

| File type | Basename pattern | Required sections (in order) |
|-----------|------------------|------------------------------|
| position | `culture_*_position.md` | Owner, Has, Orders, Loses, Drives |
| piece | `culture_*_piece_*.md` | Owner, Place, Load Bearing, Apparent, Yearbook |
| place | `culture_*_place_*.md` | Owner, Shown, Holds, Offers, Withheld |
| persona | `persona_*.md` | Owner, Projection, Action, Shadow, Tell |

**Rules:**
- All required sections must be present
- Sections must appear in the order listed
- Extra sections allowed after required ones
- Sections are case-insensitive for detection but must be formatted as `## Section Name`

**Gender position linking (personas only):**
- Every persona's `## Projection` section must begin with gender and culture position links
- Pattern: `[Name] is a [man/woman]([gender link]) from [Country]([culture link]).`
- Gender links point to universal engine positions: `[man](../../../engine/position_male.md)` or `[woman](../../../engine/position_female.md)`
- Culture links point to local culture position: `[Country](culture_[culture]_position.md)`
- These links establish the persona's intersection of universal gender and specific cultural context
- Example:
  ```
  ## Projection
  Thomas is a [man](../../../engine/position_male.md)
  from [Germany](culture_german_position.md).
  [Additional projection content...]
  ```

**Verdict when failed:** Add missing section in correct position, or add gender/culture links to Projection (specific instruction provided)

**Script:** `tests/validate_sections.py`

**Example:**
```bash
python3 tests/validate_sections.py regions/europe/germany/persona_hanna.md regions/europe/germany/persona_thomas.md
# OK: 2 files passed section validation

# With violation (missing section):
# FAIL regions/europe/germany/persona_unknown.md
#   - missing required section: ## Shadow
#   verdict: add section in order: Owner, Projection, Action, Shadow, Tell

# With violation (missing gender link):
# FAIL regions/europe/germany/persona_old.md
#   - persona Projection missing gender position link
#   verdict: Add [man](../../../engine/position_male.md) or [woman](../../../engine/position_female.md) as first line of Projection
```

---

## Layer 3: Link integrity

**Scope:** All markdown files in `regions/**/*.md`

Checks that all markdown links `[text](target.md)` resolve to existing files. Detects orphaned files.

- **General purpose:** No region-specific rules - reusable across all worlds
- **Link pattern:** Markdown syntax `[text](file.md)` in prose
- **Resolution strategies:** Relative to source file, with support for cross-level links
  1. Local links (same directory): `[text](filename.md)`
  2. Relative paths: `[text](../../../africa/algeria/piece.md)` from `regions/europe/germany/`
  3. Cross-level links: `[text](../../../engine/position_male.md)` from any persona in `regions/REGION/COUNTRY/`
  4. Repository-root paths: Fallback via ARCHITECTURE.md anchor detection
- **Orphaned files:** Detected by full scan (no internal links pointing to it, regions-only)

**Verdict when failed:** Fix broken link target, or delete orphaned file (specific instruction provided)

**Script:** `tests/validate_links.py` (reusable - can copy to Autobahn, KAIWorlds, KAILabs)

**Example:**
```bash
# On Germany personas with gender links (CI mode):
python3 tests/validate_links.py regions/europe/germany/persona_hanna.md regions/europe/germany/persona_thomas.md
# OK: Link validation passed

# On single country:
python3 tests/validate_links.py regions/europe/germany/
# OK: Link validation passed

# Full scan (development mode):
python3 tests/validate_links.py
# OK: 0 broken links
# INFO: 247 orphaned files (expected - internal linking TBD)
```

**Related:** No external files required - pure link resolution

---

## Layer 4a: Culture completeness

**Scope:** Per-country folders in `regions/REGION/COUNTRY/`

Validates that each country has minimum required files per ARCHITECTURE.md.

| Requirement | Count | Enforced |
|-------------|-------|----------|
| Position files | exactly 1 | Yes - error if 0 or >1 |
| Piece files | at least 1 | Yes - error if 0 |
| Place files | at least 1 | Yes - error if 0 |
| Persona files | at least 2 | Yes - error if <2 (note: gender diversity + position intersection) |
| Gender links in personas | per persona | Yes - error if missing from Projection |
| Culture links in personas | per persona | Yes - error if missing from Projection |

**Detection:**
- Position: `culture_*_position.md` (exactly 1 per country)
- Piece: `culture_*_piece_*.md` (at least 1 per country)
- Place: `culture_*_place_*.md` (at least 1 per country)
- Persona: `persona_*.md` (at least 2 per country)

**Verdict when failed:** Create exactly 1 file, or add missing piece/place/persona (specific instruction provided)

**Architecture traceability:**
> See [ARCHITECTURE.md - Minimum per Country](../ARCHITECTURE.md#minimum-per-country) for rationale

**Scripts:**
- `tests/validate_culture_completeness.py` - L4a completeness enforcer

**Example:**
```bash
python3 tests/validate_culture_completeness.py regions/europe/germany/
# OK: Culture completeness validation passed

# With violation (incomplete country):
python3 tests/validate_culture_completeness.py regions/africa/algeria/
# FAIL: Pieces required but not found (0/1)
#   verdict: Create exactly 1 file: culture_algerian_piece_*.md in regions/africa/algeria/
```

---

## Layer 4b: Audit README with status tables

**Scope:** Per-country folders in `regions/REGION/COUNTRY/`

Validates that each country folder contains README.md with a Content Audit Status table documenting all content files.

**Requirements:**
- `README.md` exists in country folder
- File contains `## Content Audit Status` section (case-insensitive header)
- Section includes a markdown table with columns: `File`, `Status`, `Audit Notes`
- Table has at least one entry
- All entries match actual content files in the folder

**Verdict when failed:** Create/update README.md with Content Audit Status table (template provided)

**Architecture traceability:**
> See [ARCHITECTURE.md - Hofstede Foundation](../ARCHITECTURE.md#hofstede-foundation) for audit documentation requirements

**Script:** `tests/validate_audit_readme.py`

**Example:**
```bash
python3 tests/validate_audit_readme.py regions/europe/germany/
# OK: Audit README validation passed

# With violation (missing status table):
python3 tests/validate_audit_readme.py regions/africa/algeria/
# FAIL regions/africa/algeria/README.md: Missing Content Audit Status table
#   verdict: Add Content Audit Status section with table entries for all content files
```

---

## Layer 4c: Audit table consistency

**Scope:** Per-country folders in `regions/REGION/COUNTRY/`

Validates that the Content Audit Status table in README.md matches actual content files. Detects orphaned files (in folder but not listed in audit table) and missing entries (listed in table but file doesn't exist).

**Requirements:**
- All files listed in audit table exist in folder
- All content files in folder are listed in audit table
- No orphans (files with no audit entry)
- No stale entries (audit entries for missing files)

**Verdict when failed:** Update README.md audit table to match actual files, or move/delete orphaned files

**Script:** `tests/validate_audit_consistency.py`

**Example:**
```bash
python3 tests/validate_audit_consistency.py regions/europe/germany/
# OK: Audit consistency validation passed

# With violation (orphaned file):
python3 tests/validate_audit_consistency.py regions/africa/algeria/
# FAIL regions/africa/algeria/: Orphaned file culture_algerian_piece_old.md not in README audit table
#   verdict: Add entry to audit table in README.md, or delete the file
```

---

## Layer 4d: IP/plagiarism heuristics

**Scope:** Per-country content files in `regions/REGION/COUNTRY/`

Detects heuristic patterns that suggest accidental close-paraphrase copying or Wikipedia-style plagiarism. This is an **advisory layer** (warnings only, not hard-block).

**Patterns detected:**
1. **Wikipedia-style construction:** Multiple instances of `[word] is a [noun] [in/located in/situated in/found in] [place]`
   - Example: "Berlin is a city in Germany. The museum is a building in the city."
   - Threshold: 2+ instances flags warning

2. **Date-anchored constructions:** Multiple instances of `The [noun] [verb] [in/on date]`
   - Example: "The war ended in 1945. The city was rebuilt in 1946."
   - Threshold: 3+ instances flags warning

3. **REFERENCES.md plagiarism protocol:** Validates that `REFERENCES.md` documents sourcing approach
   - Must include section on plagiarism detection/paraphrase protocol
   - Required if content was adapted from other sources

**Verdict when failed (warnings only):** Advisory - review sourcing and update REFERENCES.md if content was adapted

**Script:** `tests/validate_plagiarism.py`

**Output:** WARN prefix (advisory, not hard-block)

**Example:**
```bash
python3 tests/validate_plagiarism.py regions/europe/germany/
# OK: Plagiarism heuristics passed (no warnings)

# With warning (advisory):
python3 tests/validate_plagiarism.py regions/africa/algeria/
# WARN regions/africa/algeria/culture_algerian_position.md: Wikipedia-style pattern detected (2 instances)
#   verdict: review sourcing - if content was adapted, update REFERENCES.md with plagiarism protocol
```

---

## Layer 4e: Hofstede structure + footer sentinel

**Scope:** Per-country `README.md`, `REFERENCES.md`, and all `culture_*.md` files in `regions/REGION/COUNTRY/`

Structure-only. Per-file dimension scoring lives in **L4f**, which scores aggregate keyword density across the whole culture (see ARCHITECTURE.md > "Scoring is Aggregate, Not Per-File").

**Structure pass (FAIL, hard-block):** the country must declare a Hofstede mapping.
- README has a `## Hofstede` section.
- README contains a score table with all six dimensions filled in. Rows match `| DIM | NN | **Low/Moderate/High** ... |`. Header rows alone or prose mentions of dimension codes do not count.
- **Band + mismatch check.** The Level column is a closed enum: `Low`, `Moderate`, `High`. `Medium`, `Very High`, `Very Low`, `Medium-High` and other variants are intentionally not matched and surface as "scores incomplete" failures. On top of that, the Level cell must equal `score_to_band(score)`:
  - 0-39 → Low
  - 40-59 → Moderate
  - 60-100 → High

  A Level cell that disagrees with its score is a hard FAIL with the verdict `set Level to {band} (score {score} sits in the {band} band, 0-39 Low / 40-59 Moderate / 60-100 High)`. The canonical case: NL UAI 53 with Level `High` is rejected because 53 sits in the Moderate band.
- **Classifier prose** like `Very Low` / `Very High` is not a band -- it belongs in the Description column of the Detailed Profile table and is not parsed by L4e. The audit script `scripts/audit_readme_bands.py` (diagnostic, run separately) reports every band mismatch across all country READMEs -- both the score-table Level cell (the same contract L4e enforces) and bold-with-colon prose leads of the form `**<Band> <DIM>:**`, e.g. `**Low PDI + High IDV:**` (How Dimensions section) or `**Moderate UAI (target 53):**` (Target Keyword Distribution section). For each prose `<Band> <DIM>` pair the declared band is compared to the table score's `score_to_band` value; `Medium` is normalized to `Moderate` for the equivalence check but is still surfaced in the `declared` column so the non-canonical word stays visible. Output schema: `country | source | dimension | score | declared | expected | needs_change`, with `source` being `table` or `prose:L<line>`. The table-row count holds at zero on main; prose-row drift is tracked separately and cleaned up per country migration. The audit's parsing contract is pinned by `tests/test_audit_readme_bands.py`. Graduating the prose check into L4e (so CI gates on it) is a deferred follow-up once the prose row count also reaches zero.
- README has source attribution (mentions Hofstede, empirical, or research).
- `REFERENCES.md`, if present, cites Hofstede.

**Footer sentinel pass (WARN, advisory):** every `culture_*.md` file in the country should:
- Carry the Hofstede signal footer line: `*Hofstede signal: this file contributes to the culture's aggregate score. Declared dimensions live in [README.md](README.md).*`
- Not carry a legacy per-file score footer (`**Hofstede:** PDI ... · IDV ... · ...`). These imply per-file scoring and are forbidden under the aggregate-scoring contract.

The sentinel pass is advisory during rollout (started May 2026, DK/DE/NL first). It will graduate to FAIL once all completed countries are migrated.

**Verdicts:**
- Structure failure: add the missing section/rows/source/citation as indicated.
- Missing sentinel: add the Hofstede signal line above the version footer.
- Legacy score footer present: remove the `**Hofstede:** PDI ...` line.

**Script:** `tests/validate_hofstede_alignment.py`

**Output:** `FAIL` for structure issues (hard-block), `WARN` for footer-sentinel issues (advisory). Exit code is 1 only if a structure issue exists.

**Architecture traceability:**
> See [ARCHITECTURE.md - Hofstede Foundation](../ARCHITECTURE.md#scoring-is-aggregate-not-per-file) for the aggregate-scoring contract and footer requirements.

**Example:**
```bash
python3 tests/validate_hofstede_alignment.py regions/europe/germany/
# OK: 1 countries pass Hofstede structure + footer

# With sentinel warning (advisory, during rollout):
python3 tests/validate_hofstede_alignment.py regions/europe/france/
# WARN france/culture_french_position.md: missing Hofstede signal footer
#   verdict: add line above version footer: `*Hofstede signal: this file contributes to the culture's aggregate score. Declared dimensions live in [README.md](README.md).*`
```

---

## Layer 4f: Hofstede derived vs declared scores

**Scope:** Per-country `README.md` and all `culture_*_*.md` files in `regions/REGION/COUNTRY/`

Validates that **declared Hofstede scores in README match the actual content embodied in all culture files**. This is an **advisory layer** (warnings only, not hard-block).

**Model:** Content is the source of truth. The validator:
1. Scans all `culture_*.md` files per country (position, piece, place, persona, language files)
2. Counts high/low keywords for each Hofstede dimension using language-specific keyword bags
3. Derives 0-100 scores per dimension based on keyword distribution
4. Compares derived scores to declared scores in README
5. Flags gaps as WARN (±10 to ±20) or advisory (> ±20)

**Tolerance thresholds:**
- **Excellent:** Gap ≤ ±5 (content and declared are well-aligned)
- **Pass:** Gap ≤ ±10 (acceptable - minor misalignment tolerated)
- **Warn:** Gap ≤ ±20 (advisory - review content or declared score)
- **Fail (advisory):** Gap > ±20 (significant mismatch - investigate)

**Two decision paths when gaps exist:**

**Option A - Update README:**
If the content authentically embodies a dimension at a high/low level, update README declared score to match derived score. Example: if German content emphasizes precision/rules (UAI-high), derived UAI=100, then change README UAI from 65 → 100.

**Option B - Rewrite content:**
If README declared scores represent the desired target cultural profile, rewrite content to add/reduce keywords matching the declared dimension-polarity. Example: if Germany should be UAI=65 (moderate uncertainty aversion), reduce precision/rule keywords and add risk-taking/flexibility language.

**Multilingual keyword bags (same as L4e):**
- **English (en):** all 6 dimensions
- **German (de):** all 6 dimensions
- Add new languages to `tests/validate_hofstede_derived.py` by extending `DIMENSION_KEYWORDS_BY_LANGUAGE`

**Output format:** Gap report per country/dimension with status (excellent/pass/warn/fail).

**Verdict:** If gap > ±10, investigate. If gap > ±20, strongly consider content revision or README correction.

**Script:** `tests/validate_hofstede_derived.py`

**Output:** Exit code 1 if any gap > ±10 (advisory warnings), exit code 0 if all gaps ≤ ±10

**Example:**
```bash
python3 tests/validate_hofstede_derived.py
# === Hofstede Derived Score Report ===
# 
# germany:
#   Dim | Declared | Derived | Gap | Status
#   ----|----------|---------|-----|--------
#   PDI  |       35 |     100 |  65 | ✗ fail
#   UAI  |       65 |     100 |  35 | ✗ fail
#   IDV  |       67 |      50 |  17 | ~ warn
#   LTO  |       83 |     100 |  17 | ~ warn
#   MAS  |       66 |      75 |   9 | ✓ pass
#   IND  |       40 |      33 |   7 | ✓ pass
#
# verdict (options):
# A - Update README: PDI→100, UAI→100, IDV→50, LTO→100 (match content)
# B - Rewrite content: reduce PDI/UAI to ~65, increase IDV to ~67
```

---

---

## Layer 4g: Hofstede audit table sync

**Scope:** Per-country `README.md` "Hofstede Alignment Status" audit table

Validates that **audit tables in country READMEs stay synchronized with current Hofstede derived scores**. This ensures README documentation remains accurate when content changes. This is an **advisory layer** (warnings only, not hard-block).

**Model:** The audit table is a snapshot of the validation result. When content keywords change:
1. Validator runs `validate_hofstede_derived.py` internally to get current scores
2. Extracts the audit table from README (table format: `| Dimension | Declared | Derived | Gap | Status |`)
3. Compares audit table's "Derived" column to current derived scores
4. Flags mismatches to alert developer that README needs updating

**Typical scenario:**
- Developer adds keywords to a piece/process/persona
- Hofstede scores shift slightly (e.g., MAS 16 → 18)
- Validator detects drift and warns: "README audit table shows MAS=16 (Derived), but content now derives MAS=18"
- Developer re-runs validator and updates README audit table with new scores

**Tolerance:**
- **Synchronized:** Audit table Derived column matches current content-derived scores exactly
- **Stale:** Any dimension drifts due to content changes (even 1 point is flagged)

**Verdict when stale:**
1. Run: `python tests/validate_hofstede_derived.py` to get current scores
2. Update README audit table with new Derived values
3. Re-commit

**Script:** `tests/validate_hofstede_readme_audit.py`

**Output:** `[OK]` for synchronized tables, `[STALE]` for mismatched, exit code 0 (advisory). Provides specific guidance on which dimensions drifted and how many points.

**Example:**
```bash
python3 tests/validate_hofstede_readme_audit.py
# [OK] germany: Hofstede audit table synchronized
# [OK] denmark: Hofstede audit table synchronized
# [STALE] france: Hofstede audit table stale
#   → README audit table shows MAS=70 (Derived), current content derives MAS=72 (drift 2 points)
#   → Update README audit table: change Derived from 70 to 72, Gap from 4 to 2, Status from PASS to EXCELLENT
```

---

## Validation chain (CI jobs)

```
setup (compute changed files)
  ↓
L0-stamp-check (validation stamp exists)
  ↓
L1-general (encoding, filenames, em-dash, newline)
  ↓
L1b-language (English-only prose)
  ↓
L2-sections (section structure per file type)
  ↓
L3-links (link integrity, no orphaned files)
  ↓
L4a-completeness (minimum files per country)
  ↓
L4b-audit-readme (README with status tables)
  ↓
L4c-audit-consistency (audit table matches files)
  ↓
L4d-plagiarism (heuristic patterns - advisory)
  ↓
L4e-hofstede-alignment (dimension keywords - advisory)
  ↓
L4f-hofstede-derived (derived vs declared scores - advisory)
  ↓
L4g-hofstede-readme-audit (audit table sync - advisory)
  ↓
✅ PR passes
```

L0-L4e are hard-block (fail PR if fail). L4d-L4g are advisory (warn if issues, do not block PR).

---

## Local validation chain (pre-commit hook)

Runs before commit to give developers full feedback:

```python
validators = [
    validate_general.py,        # L1a
    validate_language.py,       # L1b (requires: lingua)
    validate_sections.py,       # L2
    validate_links.py,          # L3
    validate_culture.py,        # L4
]
```

If any validator fails, commit is rejected. Developer sees:
1. Which layer failed
2. Which file(s) have issues
3. Specific verdict (how to fix)

Stamp is written only if all validators pass.

**Setup:**
```bash
git config core.hooksPath .githooks
./scripts/setup-hooks.sh    # Linux/Mac
# or
./scripts/setup-hooks.bat   # Windows
```

---

## File locations

| Script | Layer | File type scope | Status |
|--------|-------|-----------------|--------|
| `tests/validate_general.py` | L1a | all files | ✅ Complete |
| `tests/validate_language.py` | L1b | all files | ✅ Complete |
| `tests/validate_sections.py` | L2 | typed files | ✅ Complete |
| `tests/validate_links.py` | L3 | all files | ✅ Complete (reusable) |
| `tests/validate_culture_completeness.py` | L4a | per-country | ✅ Complete |
| `tests/validate_audit_readme.py` | L4b | per-country | ✅ Complete |
| `tests/validate_audit_consistency.py` | L4c | per-country | ✅ Complete |
| `tests/validate_plagiarism.py` | L4d | per-country | ✅ Complete (advisory) |
| `tests/validate_hofstede_alignment.py` | L4e | per-country | ✅ Complete (advisory) |
| `tests/validate_hofstede_derived.py` | L4f | per-country | ✅ Complete (advisory) |
| `tests/validate_hofstede_readme_audit.py` | L4g | per-country | ✅ Complete (advisory) |
| `tests/validate_culture.py` | L4 orchestrator | orchestrator | ✅ Complete |
| `tests/findings.py` | shared | data structure | ✅ Complete |
| `tests/language_exceptions.txt` | L1b | exceptions | ✅ Complete (template) |
| `tests/requirements.txt` | dependencies | env setup | ✅ Complete |

---

## Reusability across worlds

**Copy to Autobahn, KAIWorlds, KAILabs without changes:**
- ✅ `validate_general.py` (L1a)
- ✅ `validate_language.py` (L1b) - with `lingua-language-detector` installed
- ✅ `validate_links.py` (L3)
- ✅ `findings.py` (shared types)

**Customize per world:**
- `validate_sections.py` (L2) - adjust section maps per architecture

**Cultures-specific only:**
- `validate_culture_completeness.py` (L4a - country structure)
- `validate_audit_readme.py` (L4b - audit documentation)
- `validate_audit_consistency.py` (L4c - audit table consistency)
- `validate_plagiarism.py` (L4d - IP safety for content-heavy worlds)
- `validate_hofstede_alignment.py` (L4e - Hofstede framework specific to Cultures)
- `validate_culture.py` (L4 orchestrator)

---

## Gender position framework (Engine-level)

**Overview:** Every persona embodies the intersection of a universal gender position and a specific cultural position. This framework operates at the engine level (above all cultures) and is enforced by L2 (section structure) and L3 (link integrity).

**Universal gender positions** (in `engine/`):
- `position_male.md` - The body read as a claim before it speaks; assumption of agency conferred not requested
- `position_female.md` - The body read as an invitation before it speaks; expectation of accommodation assumed not negotiated

These are NOT culture-specific. They apply universally and establish the baseline gender dynamic independent of cultural context.

**Linking pattern (mandatory for all personas):**

Every persona's `## Projection` section begins with gender and culture links:

```markdown
## Projection
[Name] is a [man/woman]([gender link]) from [Country]([culture link]).
[Additional projection content...]
```

Example (Thomas, Germany):
```markdown
## Projection
Thomas is a [man](../../../engine/position_male.md)
from [Germany](culture_german_position.md).
Clipboard. Steel-toed boots.
[rest of projection...]
```

Example (Hanna, Germany):
```markdown
## Projection
Hanna is a [woman](../../../engine/position_female.md)
from [Germany](culture_german_position.md).
Stands at the front of the room.
[rest of projection...]
```

**Why this matters:**
- Gender + culture intersection reveals how universal positions materialize in specific cultural contexts
- Thomas (male/German) carries the claim of agency within German hierarchy/precision culture
- Hanna (female/German) carries the accommodation expectation within German hierarchy/precision culture
- Same gender, different culture = different manifestation; same culture, different gender = different manifestation

**Validation enforcement:**
- **L2 (validate_sections.py):** Checks that personas have both gender and culture links in Projection
  - If missing: `verdict: Add [man/woman](../../../engine/position_male.md / position_female.md) as first line of Projection`
- **L3 (validate_links.py):** Checks that links resolve correctly across the `regions/REGION/COUNTRY/` → `engine/` path
  - Cross-level path: `../../../engine/position_male.md` from `regions/europe/germany/persona_thomas.md`
  - Culture path: `culture_german_position.md` (local reference)

**Requirements for new personas:**
- All new personas must include gender links (mandatory)
- Existing personas should be updated on next edit (no retroactive bulk update)
- Scaffolding templates must generate gender link pattern by default

**Baseline (Germany - Production Ready):**
- ✅ persona_thomas.md: Has gender + culture links
- ✅ persona_hanna.md: Has gender + culture links
- ✅ L2 validation: Both pass
- ✅ L3 validation: All links resolve correctly
- ✅ Full E2E: All 9 layers pass (L0-L4e)

---

## Testing locally

**Unit tests (parser/contract pins):**
```bash
pip install -r tests/requirements.txt   # one-time: pytest, lingua, PyYAML
python3 -m pytest tests/                # 136 tests across 9 suites
```

`pytest` discovers both unittest-style suites (`test_hofstede_alignment.py`, `test_audit_readme_bands.py`, `test_branch_scope.py`, `test_hook_scope_e2e.py`) and pytest-style suites (`test_hofstede_bag_*.py`) in the same run -- no separate harness needed. Run a single suite with `python3 -m pytest tests/test_audit_readme_bands.py`. These pin parser regexes, band/score contracts, branch-scope policy, and the bag-loader behavior; they do not read `regions/` content.

**Full validation on changed files (CI simulation):**
```bash
python3 tests/validate_general.py regions/europe/germany/*.md
python3 tests/validate_language.py regions/europe/germany/*.md
python3 tests/validate_sections.py regions/europe/germany/*.md
python3 tests/validate_links.py regions/europe/germany/*.md
python3 tests/validate_culture_completeness.py regions/europe/germany/*.md
python3 tests/validate_audit_readme.py regions/europe/germany/*.md
python3 tests/validate_audit_consistency.py regions/europe/germany/*.md
python3 tests/validate_plagiarism.py regions/europe/germany/*.md
python3 tests/validate_hofstede_alignment.py regions/europe/germany/*.md
```

**Using the orchestrator (L4 only):**
```bash
python3 tests/validate_culture.py regions/europe/germany/*.md
```

**Full scan (all countries):**
```bash
python3 tests/validate_general.py
python3 tests/validate_language.py
python3 tests/validate_sections.py
python3 tests/validate_links.py
python3 tests/validate_culture_completeness.py
python3 tests/validate_audit_readme.py
python3 tests/validate_audit_consistency.py
python3 tests/validate_plagiarism.py
python3 tests/validate_hofstede_alignment.py
```

**Pre-commit hook locally:**
```bash
python3 .githooks/pre-commit
```

**With custom language settings:**
```bash
ALLOWED_LANGUAGES=english,german python3 tests/validate_language.py
```

---

## Baselines

**Germany (7 files: 1 position, 1 piece, 1 place, 2 personas + gender links, README, REFERENCES):**
- L1a: ✅ UTF-8, ASCII filenames, no em-dash, trailing newline
- L1b: ✅ English-only prose
- L2: ✅ Section structure per file type + gender position links in both personas
- L3: ✅ Link integrity (no broken/orphaned files, cross-level links resolve: `../../../engine/position_*.md`)
- L4a: ✅ Completeness (1 position, 1 piece, 1 place, 2 personas with gender/culture links)
- L4b: ✅ README with Hofstede audit table
- L4c: ✅ Audit table consistency
- L4d: ✅ No plagiarism heuristics warnings
- L4e: ✅ Strong Hofstede alignment (all 6 dimensions reflected in position)

**Full scan (31 countries):**
- L1a-L3: Germany ✅ pass; 30 others vary (incomplete content)
- L4a: 5 countries complete, 26 incomplete (content work in progress)
- L4b-L4e: Germany ✅ fully compliant; others incomplete until scaffolded

---

## Related documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - specification that validators enforce
- [.githooks/pre-commit](.githooks/pre-commit) - local validation gate
- [.github/workflows/validate.yml](.github/workflows/validate.yml) - CI job definitions
