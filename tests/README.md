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
L4  per-country        culture completeness (minimum file requirements per country)
```

L0 gates everything. L1a gates L1b. L1b gates L2. L2 gates L3. L3 gates L4.

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

**Verdict when failed:** Add missing section in correct position, or reorder existing sections (specific instruction provided)

**Script:** `tests/validate_sections.py`

**Example:**
```bash
python3 tests/validate_sections.py regions/europe/germany/persona_hanna.md
# OK: 1 files passed section validation

# With violation:
# FAIL regions/europe/germany/persona_thomas.md
#   - missing required section: ## Shadow
#   verdict: add section in order: Owner, Projection, Action, Shadow, Tell
```

---

## Layer 3: Link integrity

**Scope:** All markdown files in `regions/**/*.md`

Checks that all markdown links `[text](target.md)` resolve to existing files. Detects orphaned files.

- **General purpose:** No region-specific rules - reusable across all worlds
- **Link pattern:** Markdown syntax `[text](file.md)` in prose
- **Resolution:** Relative to source file directory (e.g., link from `regions/europe/germany/persona_hanna.md` to `../../../africa/algeria/piece.md` resolves correctly)
- **Orphaned files:** Detected by full scan (no internal links pointing to it)

**Verdict when failed:** Fix broken link target, or delete orphaned file (specific instruction provided)

**Script:** `tests/validate_links.py` (reusable - can copy to Autobahn, KAIWorlds, KAILabs)

**Example:**
```bash
# On Germany files only (CI mode):
python3 tests/validate_links.py regions/europe/germany/culture_german_position.md
# OK: Link validation passed

# Full scan (development mode):
python3 tests/validate_links.py
# OK: 0 broken links
# INFO: 247 orphaned files (expected - internal linking TBD)
```

**Related:** No external files required - pure link resolution

---

## Layer 4: Culture completeness

**Scope:** Per-country folders in `regions/REGION/COUNTRY/`

Validates that each country has minimum required files per ARCHITECTURE.md.

| Requirement | Count | Enforced |
|-------------|-------|----------|
| Position files | exactly 1 | Yes - error if 0 or >1 |
| Piece files | at least 1 | Yes - error if 0 |
| Place files | at least 1 | Yes - error if 0 |
| Persona files | at least 2 | Yes - error if <2 (note: gender diversity expected) |

**Detection:**
- Position: `culture_*_position.md` (exactly 1 per country)
- Piece: `culture_*_piece_*.md` (at least 1 per country)
- Place: `culture_*_place_*.md` (at least 1 per country)
- Persona: `persona_*.md` (at least 2 per country)

**Verdict when failed:** Create exactly 1 file, or add missing piece/place/persona (specific instruction provided)

**Architecture traceability:**
> See [ARCHITECTURE.md - Minimum per Country](../ARCHITECTURE.md#minimum-per-country) for rationale

**Scripts:**
- `tests/validate_culture.py` - L4 orchestrator (calls L4a completeness)
- `tests/validate_culture_completeness.py` - L4a completeness enforcer

**Reusability:** L4 is Cultures-specific (country structure). Not copied to other worlds.

**Example:**
```bash
python3 tests/validate_culture.py regions/europe/germany/
# OK: Culture completeness validation passed

# With violation (incomplete country):
python3 tests/validate_culture.py regions/africa/algeria/
# FAIL: Pieces required but not found (0/1)
#   verdict: Create exactly 1 file: culture_algerian_piece_*.md in regions/africa/algeria/
```

**Future extension:**
- L4b: Gender validation (2+ personas should represent gender diversity)
- L4c: Relationship checks (place/piece/persona internal links)

---

## Validation chain (CI jobs)

```
setup (compute changed files)
  ↓
L0-stamp-check (validation stamp exists)
  ↓
L1a-general (encoding, filenames, em-dash, newline)
  ↓
L1b-language (English-only prose)
  ↓
L2-sections (section structure per file type)
  ↓
L3-links (link integrity, no orphaned files)
  ↓
L4-culture (culture completeness per country)
  ↓
✅ PR passes
```

Each job depends on previous job. All are hard-block (fail PR if fail).

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
| `tests/validate_culture.py` | L4 orchestrator | orchestrator | ✅ Complete |
| `tests/validate_culture_completeness.py` | L4a | per-country | ✅ Complete |
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
- `validate_culture.py` + `validate_culture_completeness.py` (L4 country logic)

---

## Testing locally

**Full validation on changed files (CI simulation):**
```bash
python3 tests/validate_general.py regions/europe/germany/*.md
python3 tests/validate_language.py regions/europe/germany/*.md
python3 tests/validate_sections.py regions/europe/germany/*.md
python3 tests/validate_links.py regions/europe/germany/*.md
python3 tests/validate_culture.py regions/europe/germany/*.md
```

**Full scan (all countries):**
```bash
python3 tests/validate_general.py
python3 tests/validate_language.py
python3 tests/validate_sections.py
python3 tests/validate_links.py
python3 tests/validate_culture.py
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

**Germany (5 files):**
- L1a: 4/5 fail (BOM) → auto-fixed by pre-commit hook
- L1b: ✅ 5/5 pass English-only
- L2: ✅ 5/5 pass structure
- L3: ✅ 5/5 pass links
- L4: ✅ Pass completeness

**Full scan (31 countries):**
- L3: 0 broken links, ~247 orphaned files (expected - internal linking TBD)
- L4: 5 countries complete, 26 incomplete (content work in progress)

---

## Related documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - specification that validators enforce
- [.githooks/pre-commit](.githooks/pre-commit) - local validation gate
- [.github/workflows/validate.yml](.github/workflows/validate.yml) - CI job definitions
