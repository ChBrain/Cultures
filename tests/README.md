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
```

L0 gates everything. L1a gates L1b. L1b gates L2. L2 gates L3. L3 gates L4a. L4a gates L4b. L4b gates L4c. L4c gates L4d. L4d gates L4e.

**All are hard-block jobs** - fail PR if any layer fails (no soft warnings).

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

## Layer 4e: Hofstede structure + dimension alignment

**Scope:** Per-country `README.md`, `REFERENCES.md`, and `culture_*_position.md` in `regions/REGION/COUNTRY/`

Two passes:

**Structure pass (FAIL):** the country must declare a Hofstede mapping.
- README has a `## Hofstede` section.
- README contains a score table with all six dimensions filled in. Rows match `| DIM | NN | **Low/High/Very High** ... |`. Header rows alone or prose mentions of dimension codes do not count.
- README has source attribution (mentions Hofstede, empirical, or research).
- `REFERENCES.md`, if present, cites Hofstede.
- `culture_*_position.md`, if present, references at least one dimension by name or code.

**Alignment pass (WARN):** given the scores parsed in the structure pass, the position file's keywords should match the expected polarity for each dimension. Skipped for a country if no scores could be extracted (otherwise the country would silently pass the alignment check it should have failed).

**Multilingual keyword framework:**

The validator automatically detects content language and applies language-specific keyword bags. Supported languages:

- **English (en):** PDI, IDV, UAI, MAS, LTO, IND keywords in English
- **German (de):** PDI, IDV, UAI, MAS, LTO, IND keywords in German

When a language is not supported, the validator issues an advisory warning with actionable instructions:
```
WARN country/culture_position.md: language 'fr' not yet supported for Hofstede alignment
  verdict: add language 'fr' keyword bags to DIMENSION_KEYWORDS_BY_LANGUAGE in validate_hofstede_alignment.py; 
           use DIMENSION_KEYWORDS_BY_LANGUAGE['en'] as template
```

To add support for a new language:
1. Add new language entry to `DIMENSION_KEYWORDS_BY_LANGUAGE` in `tests/validate_hofstede_alignment.py`
2. Map each of the six dimensions (PDI, IDV, UAI, MAS, LTO, IND) to two polarity variants: "high" and "low"
3. For each variant, provide a list of 6-10 keywords that signal that dimension-polarity combination
4. Example: German UAI-high keywords include "präzision", "direktheit", "struktur", "regel", "klarheit"

The language detection heuristic looks for language-specific markers (articles, characters, common words). See `detect_language()` in `validate_hofstede_alignment.py` for details.

**Dimension keyword mapping (English reference):**
- **PDI (Power Distance Index):** Low: equal, merit, question; High: hierarchy, authority, obey, deference
- **IDV (Individualism):** Low: collective, group, harmony; High: individual, personal, autonomy, self
- **UAI (Uncertainty Avoidance):** Low: risk, flexible, adapt; High: rules, structure, precision, control
- **MAS (Masculinity):** Low: cooperation, care, compassion; High: compete, achieve, excellence, success
- **LTO (Long-Term Orientation):** Low: tradition, immediate, present; High: long-term, planning, future, foundation
- **IND (Indulgence):** Low: restraint, discipline, control; High: enjoy, gratification, freedom, pleasure

**Verdicts:**
- Structure failure: add the missing section/rows/source/citation as indicated.
- Alignment warning: review the position file — add keywords reflecting claimed dimensions, or adjust README dimensions to match the position.
- Language not supported: add the language's keyword bags to `DIMENSION_KEYWORDS_BY_LANGUAGE` (see instructions above).

**Script:** `tests/validate_hofstede_alignment.py`

**Output:** `FAIL` for structure issues (hard-block), `WARN` for alignment issues and unsupported languages (advisory). Exit code is 1 only if a structure issue exists.

**Architecture traceability:**
> See [ARCHITECTURE.md - Hofstede Foundation](../ARCHITECTURE.md#application-in-cultures) for dimension application guidance

**Example:**
```bash
python3 tests/validate_hofstede_alignment.py regions/europe/germany/
# OK: Hofstede alignment validation passed [de]
#   (German content, all supported dimensions evaluated)

# With warning (unsupported language):
python3 tests/validate_hofstede_alignment.py regions/europe/france/
# WARN regions/europe/france/culture_french_position.md: language 'fr' not yet supported for Hofstede alignment
#   verdict: add language 'fr' keyword bags to DIMENSION_KEYWORDS_BY_LANGUAGE in validate_hofstede_alignment.py; 
#            use DIMENSION_KEYWORDS_BY_LANGUAGE['en'] as template
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
✅ PR passes
```

Each job depends on previous job. L4d and L4e are advisory (warnings only, do not block PR). All others are hard-block (fail PR if fail).

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
