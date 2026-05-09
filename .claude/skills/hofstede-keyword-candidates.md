# Hofstede Keyword Candidates

**Skill for generating Hofstede dimension keyword candidates for per-country bags.**

## Purpose

When creating a per-country Hofstede bag (YAML file with 10 keywords per dimension/polarity), this skill provides a structured workflow to:

1. Analyze country cultural content (positions, pieces, places, personas)
2. Extract candidate keywords that reflect high/low poles of each dimension
3. Validate candidates against constraints (uniqueness, denylist, formatting)
4. Generate or refine bag YAML entries

## Input

- **Country folder**: `regions/<region>/<country>/` containing:
  - `culture_*_position.md` - Cultural position statement
  - `culture_*_piece_*.md` - Historical/cultural pieces
  - `culture_*_place_*.md` - Place descriptions
  - `persona_*.md` - Character personas
  
- **Hofstede scores** (reference or from README.md audit):
  - PDI, IDV, UAI, MAS, LTO, IND (0-100 scale)

- **Optional**:
  - Existing bag YAML (to refine/augment)
  - Declared Hofstede scores in README.md
  - Previous bag drop logs (decisions.md)

## Word Selection Strategy v1.0

The following strategy selects keywords that authentically represent Hofstede dimensions:

### High/Low Pole Definitions

Each dimension has cultural anchors:

| Dimension | High Pole | Low Pole |
|-----------|-----------|----------|
| **PDI** (Power Distance) | Hierarchy, deference to authority, clear status | Equality, informality, merit-based access |
| **IDV** (Individualism) | Personal achievement, autonomy, self-reliance | Group harmony, loyalty, community belonging |
| **UAI** (Uncertainty Avoidance) | Rules, structure, planning, control of risk | Flexibility, improvisation, comfort with ambiguity |
| **MAS** (Masculinity) | Competition, achievement, assertiveness, winning | Cooperation, caring, modesty, quality of life |
| **LTO** (Long-Term Orientation) | Persistence, planning, respect for tradition | Short-term satisfaction, prompt rewards |
| **IND** (Indulgence) | Gratification of desires, fun, leisure | Self-restraint, duty, delayed gratification |

### Extraction Process

**Step 1: Scan for signals in cultural content**

Read all culture files (position, pieces, places, personas) and mark phrases/concepts that signal each pole:

- High-pole signals: "hierarchy," "respect authority," "structured planning," "collective loyalty," "long-suffering endurance," "restrained duty"
- Low-pole signals: "informal decision-making," "individual choice," "adaptive quick-change," "personal ambition," "enjoying pleasures," "questioning norms"

**Step 2: Convert signals to candidate keywords**

For each signal, extract 1-3 candidate keywords:

- Signal: "respect for hierarchy" → Keywords: `hierarchy`, `deference`
- Signal: "structured planning" → Keywords: `structure`, `protocol`, `planning`
- Signal: "individual achievement drives society" → Keywords: `achievement`, `competition`

**Step 3: Apply constraints**

For each dimension, filter candidates to 10 keywords per pole:

1. **Uniqueness**: No keyword appears twice in same country (any dimension/polarity)
2. **Denylist**: Exclude common words (a, the, is, and, etc.) and dimension-neutral nouns
3. **Formatting**: Lowercase, single words or hyphenated compounds (no spaces, no punctuation)
4. **Authenticity**: Prioritize keywords that:
   - Appear multiple times in country content (weighted signal)
   - Are culturally specific (not generic)
   - Connect to historical/social narratives in country folder
   - Match Hofstede theory (avoid polysemy across countries)

**Step 4: Rank by relevance**

Order final 10 candidates by:

1. Frequency in country content (higher = higher rank)
2. Alignment to cultural narrative (thematic coherence)
3. Hofstede theory fit (avoid cross-cultural misalignment)

Select top 10 for high pole, top 10 for low pole.

**Step 5: Validate cross-country collisions**

Check against existing bags in other countries:

- ⚠️ **Warn** if keyword appears as opposite pole in another country (polysemy)
- ✅ **Accept** if keyword appears in same pole (cross-cultural strength signal)

### Example: Poland (High Context Scenario)

Content signals for **UAI (Uncertainty Avoidance)**:

- `culture_polish_position.md`: "Martial law, Soviet structures, orderly procedures, CPN hierarchy"
- `culture_polish_piece_uprising.md`: "Underground networks, careful planning, Solidarność protocols"
- `personas`: "Wariness of chaos, respect for institutions"

**High-UAI candidates**: `structure`, `protocol`, `hierarchy`, `order`, `martial`, `plan`, `careful`, `formal`, `institution`, `control`

**Low-UAI candidates**: (harder to find in Polish context, search for counterpoints)
- "Reform-minded," "creative resistance," "questioning authority" → `improvise`, `adapt`, `challenge`, `flexibility`, `reform`

**Final UAI bag** (after filtering for top 10 each):
- High: `structure`, `protocol`, `hierarchy`, `order`, `institution`, `martial`, `formal`, `discipline`, `plan`, `control`
- Low: `improvise`, `adapt`, `challenge`, `flexibility`, `reform`, `question`, `elastic`, `pragmatic`, `informal`, `creativity`

## Output

**Hofstede bag YAML file**: `regions/<region>/<country>/hofstede_bag.yaml` or `hofstede_bag_<lang>.yaml`

```yaml
country: <country_name>
language: <language_code>  # e.g., "en", "pl", "de"
parent: null               # or "regions/region/parent_country" if fork

hofstede_scores:
  PDI: <0-100>
  IDV: <0-100>
  UAI: <0-100>
  MAS: <0-100>
  LTO: <0-100>
  IND: <0-100>

bags:
  PDI: { high: [word1, word2, ...], low: [...] }  # exactly 10 each
  IDV: { high: [...], low: [...] }
  UAI: { high: [...], low: [...] }
  MAS: { high: [...], low: [...] }
  LTO: { high: [...], low: [...] }
  IND: { high: [...], low: [...] }
```

**Decisions document** (if fork): `regions/<region>/<country>/hofstede_decisions.md`

```markdown
# Hofstede Decisions for <Country>

## Parent: <path/to/parent> (if applicable)

## Drop Log

### Dropped Keywords (with reasons)

- `keyword1`: Removed because [reason - e.g., "too generic," "collides with other country," "not in content"]
- `keyword2`: Moved from high to low because [reason]

## Fork Divergences

If this bag diverges from parent:
- Changed PDI-high from `obey` to `deference`: More authentic to context
- Added new IND-high `celebration`: Local festivals emphasize enjoyment

---
v0.1.0 - KAI Worlds
```

## Workflow Integration

This skill is invoked in two scenarios:

1. **Creation**: Building a brand-new bag for a country
   - Input: Country content files + Hofstede scores (from README or research)
   - Output: YAML bag + decisions.md

2. **Refinement**: Updating existing bag (e.g., after content changes)
   - Input: Existing bag + updated content
   - Output: Refined YAML + drop log explaining changes

## Constraints & Safety

- **Exactly 10 keywords per polarity**: No more, no fewer (enforced by test_hofstede_bag_shape.py)
- **No within-country collisions**: Each keyword unique within country (enforced by test_hofstede_bag_quality.py)
- **No cross-country opposing collisions**: Warned if keyword appears as opposite pole elsewhere (test_hofstede_bag_quality.py)
- **Locked bags**: Once a bag is locked (SHA256 in data/hofstede_bag_locks.yaml), changes must be tracked in decisions.md
- **Fork discipline**: If bag has parent, divergences must be documented

## Related Files

- Data: `data/hofstede_bag_loader.py` — Bag loading with fallback
- Data: `data/hofstede_bag_locks.yaml` — SHA256 lock index (created in PR-D)
- Tests: `tests/test_hofstede_bag_*.py` — Validation test suite
- Validator: `tests/validate_hofstede_derived.py` — Content keyword scoring

## Version

v0.1.0 - KAI Worlds
