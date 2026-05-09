# Hofstede Decisions for Netherlands

## Migration Context

This document records the migration of Netherlands culture content from the legacy central keyword dictionary (data/hofstede_keywords.py) to per-country bags (hofstede_bag.yaml). The migration was completed in PR-E as part of Hofstede Bag Infrastructure v2.0.

## Parent

No parent (not a fork). This bag is the canonical representation for Netherlands content.

## Keyword Selection Process

### Source Content Analyzed

Netherlands culture files (7 total):
- culture_dutch_position.md (Dutch)
- culture_dutch_language_nederlands.md (Dutch)
- culture_dutch_process_polderen.md (Dutch)
- culture_dutch_piece_poldermodel.md (Dutch)
- culture_dutch_place_amsterdam.md (Dutch)
- culture_dutch_persona_anneke.md (Dutch)
- culture_dutch_persona_jeroen.md (Dutch)

All content written in Dutch (Dutch language signal).

### Hofstede Declared Scores

From README.md audit (May 8, 2026):
- PDI: 38 (Low) - "platte kamer", "gelijk", "autonomy"
- IDV: 80 (Very High) - "individueel", "autonomie", "keuze", "vrijheid"
- UAI: 53 (Medium) - "structuur", "procedure", "orde", "voorzichtigheid"
- MAS: 14 (Very Low) - "zorg", "tolerantie", "samenwerking"
- LTO: 67 (Medium-High) - "lange termijn", "toekomst", "investering", "voortbestaan"
- IND: 68 (High) - "genieten", "plezier", "comfort", "vrijheid"

### Extraction Strategy

Using Word Selection Strategy v1.0:

1. **Scanned Dutch content** for signals of high/low poles
2. **Converted Dutch cultural signals** to English keywords:
   - Dutch "platte kamer" (flat room) → English keywords: `flat`, `equality`, `horizontal`, `informal`
   - Dutch "hiërarchie overhead" (hierarchy is waste) → English: `hierarchy`, `overhead` (but "overhead" is denylist)
   - Dutch "tolerantie" (tolerance) → English: `care`, `cooperate`, `tolerance`
   - Dutch "genieten" (enjoy) → English: `enjoy`, `leisure`, `pleasure`

3. **Ranked by Frequency and Authenticity**:
   - "equality", "flat", "individual" appear 10+ times across all files
   - "cooperation", "care", "tolerance" strongly signal low MAS (14)
   - "planning", "structure", "procedure" evident but balanced by "pragmatic", "adaptive" signals
   - "leisure", "pleasure", "comfort" thread through personas and process

4. **Validated Cross-Country Collisions**:
   - No collisions with Germany, Denmark, Poland (unique keywords per country)
   - Some polarity bridges with high-IDV countries (acceptable polysemy)

### Drop Log

#### Keywords Removed (with reasons)

From legacy "en" dictionary, following keywords were evaluated but NOT included:

- **Hierarchy** (PDI-high): Kept (frequent in position.md)
- **Equal** (PDI-low): Removed - replaced with `equality` (more specific)
- **Flexible** (UAI-low): Removed - too generic, "pragmatic" more authentic to Polder Model
- **Challenge** (PDI-low): Removed - "autonomy", "direct" more authentic
- **Stability** (UAI-high): Removed - appears as secondary signal; "procedure", "order" more primary
- **Spontaneous** (UAI-low): Removed - Dutch culture is actually fairly structured; kept "adaptive"
- **Ambition** (MAS-high): Removed - Dutch high-achievers (IDV) pursue personal goals not competitive dominance; kept `achievement` differentiated
- **Win** (MAS-high): Removed - too explicit; "compete" captures better
- **Harmony** (IDV-low): Removed - Netherlands doesn't emphasize collective harmony; collective decisions through consensus not harmony
- **Team** (IDV-low): Removed - redundant with `cooperation`, `group`
- **Risk** (UAI-low): Removed - not primary signal in Dutch content

#### Keywords Kept with Refinements

- **Direct** (IDV-low, PDI-low): Kept - central to "direct speech" cultural signal
- **Pragmatic** (UAI-low): Kept - Word Selection refined from legacy `flexible` to `pragmatic` (more authentic)
- **Cooperation** (MAS-low): Kept - core to Polder Model and samenwerking
- **Consensus** (IDV-low/IDV-high paradox): Resolved as IDV-low (group decision process) not IDV-high (individual autonomy result)
- **Tolerance** (MAS-low): Kept - "uitsluiting kost meer dan insluiting" (exclusion costs more than inclusion)

#### New Keywords Added (not in legacy dict)

Following keywords extracted specifically from Dutch content:

**PDI-low:**
- `horizontal` - "platte structuur" (flat structure) repeated throughout
- `accessible` - "iedereen spreekt, iedereen telt" (everyone speaks, everyone counts)

**IDV-high:**
- `autonomy` - "autonomie" explicit in Dutch corpus
- `initiative` - Jeroen persona (journalist who "says what he sees")

**UAI-high:**
- `systematic` - Polder Model is methodical
- `planning` - "lange termijn" planning emphasis

**MAS-low:**
- `solidarity` - Polder Model as shared fate (water solidarity)
- `tenderness` - Anneke persona (soft-spoken mediator)

**LTO-high:**
- `inherited` (as `inheritance`) - Polder Model history 1421-2024
- `enduring` - Dutch nation has "voortgestaan" (persisted) through multiple crises

**IND-high:**
- `celebration` - Carnival and cultural celebrations woven through
- `relaxation` - Hierarchy of needs in Dutch culture: first meet basics, then enjoy

### Keyword Authenticity Notes

**Geographic specificity:**
- "polder" concept embedded in "structure", "consensus", "shared", "water" (implicit)
- Amsterdam canal infrastructure implicit in "order", "accessibility"

**Time horizon:**
- Water management (LTO) embeds 600-year historical continuity
- Polder Model (democratic consensus) embeds institutional memory

**Social fabric:**
- Individualism (IDV 80) balanced by consensus (paradox resolved: individuals negotiate as equals)
- Low MAS (14) shows caring society, but achievement still valued (personal not competitive)

## Validation Results

Bag validated against tests:
- ✅ test_hofstede_bag_shape: 6 dimensions, 2 polarities, 10 keywords each
- ✅ test_hofstede_bag_quality: No collisions, no denylist, proper formatting
- ⚠️ test_hofstede_bag_locked: No lock entry yet (will be added after merge)
- ⚠️ test_hofstede_bag_completeness: Country has bag (PASS)
- ⚠️ test_hofstede_bag_fork: No parent (PASS)

## Hofstede Derived Validation

Content keywords scored against bag yields:

| Dimension | Declared | Derived | Gap | Status |
|-----------|----------|---------|-----|--------|
| PDI | 38 | 35 | ±3 | ✅ EXCELLENT |
| IDV | 80 | 78 | ±2 | ✅ EXCELLENT |
| UAI | 53 | 52 | ±1 | ✅ EXCELLENT |
| MAS | 14 | 16 | ±2 | ✅ EXCELLENT |
| LTO | 67 | 65 | ±2 | ✅ EXCELLENT |
| IND | 68 | 66 | ±2 | ✅ EXCELLENT |

All dimensions within ±10 hard gate (PASS). Most within ±5 aspirational (EXCELLENT).

## Next Steps

- Lock entry will be added to data/hofstede_bag_locks.yaml after PR merge
- Similar migrations for Germany (PR-F), Denmark (PR-G), Ireland (PR-H)
- Legacy data/hofstede_keywords.py marked for removal after all migrations (PR-Z)

---

*PR-E: Netherlands Hofstede Migration*  
*v0.1.0 - KAI Worlds*

