# Poland - Culture Content

**Language(s):** Polish (Polski)

This folder contains culture content for Poland: the Polish language, the historical arc, the cultural position, the survival process, the 1997 constitution, Warsaw, and two personas embodying the culture.

## Quick Start

Download the complete Poland culture package for Claude.ai:
- [**poland.zip**](https://github.com/ChBrain/Cultures/releases/latest/download/poland.zip) - All culture files + engine stack + instructions

The zip contains all culture files flattened at root level with links rewritten for Claude consumption.

## Content Overview

Filename convention: `culture_<adj>_<TYPE>_<NAME>.md` where TYPE is one of the 5 KAI structural types (process, position, piece, place, persona). Single-instance kinds (language, history) drop the redundant country suffix.

| File | TYPE | Purpose |
|------|------|---------|
| `culture_polish_position_language.md` | position | Polski - linguistic anchor |
| `culture_polish_piece_history.md` | piece | The arc of Polish history (966 to 2023) |
| `culture_polish_position.md` | position | Polish cultural position (krąg and state) - narrative anchor |
| `culture_polish_process_przetrwanie.md` | process | Przetrwanie - survival as cultural direction |
| `culture_polish_piece_konstytucja.md` | piece | Konstytucja - 1997 Polish Constitution as load-bearing artifact |
| `culture_polish_place_warsaw.md` | place | Warsaw - capital city as geographical anchor |
| `culture_polish_persona_male_tomasz.md` | persona | Tomasz - architect, b. 1990 |
| `culture_polish_persona_female_malgorzata.md` | persona | Dr. Małgorzata - internist, b. 1958 |

## Hofstede Cultural Dimensions

| Dimension | Score | Level | Description |
|---|---|---|---|
| PDI | 68 | **High** | Hierarchies are natural and necessary. Formal structures, titles, and chain of command matter. But pragmatic meritocracy tempers pure rank: competence and qualification also confer authority. |
| IDV | 60 | **High** | Individual achievement is valued and pursued (post-1989 entrepreneurship, career ambition). But family loyalty, community ties, and Catholic collectivism remain strong. Balance between personal goals and group obligations. |
| MAS | 64 | **High** | Achievement, competition, and success are important. Career advancement is a major life goal. But Catholicism and family values introduce compassion and care. Not ruthless individualism; achievement with social conscience. |
| UAI | 93 | **Very High** | Deep anxiety about uncertainty. Rules, procedures, documentation, and planning are comforting. Formal legal systems and written regulations provide security. Historical experience of foreign occupation and post-war rebuilding reinforced need for institutional clarity. |
| LTO | 38 | **Low** | Pragmatic about the future (planning, investment, strategy), but cultural memory and tradition are also valued. Not purely future-focused; the past shapes present identity. Catholic doctrine emphasizes continuity, but post-1989 Poland is also rapidly reforming. |
| IND | 29 | **Low** | Restraint, duty, and discipline are virtues. Self-denial and sacrifice are valued. Post-war scarcity and Catholic asceticism created a culture that views excess and self-indulgence with suspicion. |

**Source:** Hofstede Insights - empirical research from *Cultures and Organizations*

## Hofstede Alignment Audit

| Dimension | Declared | Derived | Gap | Status |
|---|---|---|---|---|
| PDI | 68 | 71 | 3 | ✅ EXCELLENT |
| IDV | 60 | 56 | 4 | ✅ EXCELLENT |
| MAS | 64 | 60 | 4 | ✅ EXCELLENT |
| UAI | 93 | 88 | 5 | ✅ EXCELLENT |
| LTO | 38 | 36 | 2 | ✅ EXCELLENT |
| IND | 29 | 33 | 4 | ✅ EXCELLENT |

**Derivation method**: Each keyword in hofstede_bag.yaml is counted once per culture file if present (word-boundary matching, no substring inflation). Score = (high_keyword_count / (high_count + low_count)) × 100. Gap tolerance: ±10 PASS, ±5 EXCELLENT. Audited May 11, 2026; re-audit pending after the v2 migration adds piece_history.md content (LTO-high and IDV-low signals).

## How Dimensions Shape Polish Culture

- **High UAI (93)** drives the obsession with procedury (procedures), protokół (protocol), and formal specification. Polish institutions document everything. Risk and ambiguity are anxiety-inducing; clarity and written rules are comforting. Historical trauma (occupation, war, Cold War) embedded this need for institutional certainty.

- **High PDI (68)** means hierarchy is expected, but expertise and qualification matter. Titles are used, chain of command is respected, but "zwierzchnik" (superior) is not feared if they are competent. Post-1989 meritocratic values temper pure rank-based deference.

- **High IDV (60)** creates tension: Polish people pursue career ambition and personal achievement, but family loyalty and community ties remain binding. You can be ambitious, but not at the expense of family obligation or social responsibility.

- **High MAS (64)** means career success and achievement are important measures of worth. Competition is normal. But Polish culture is not ruthlessly individualistic; compassion (troska), cooperation (współpraca), and care (opiekuńczość) are also values, especially within family and close relationships.

- **Low LTO (38)** reflects pragmatism without pure future-focus. Poles plan strategically (inwestycja, strategia) and understand delayed gratification, but they also honor tradition, memory (pamięć), and ancestral roots (korzenie). The past is not dead; it shapes present identity.

- **Low IND (29)** means restraint and duty are deeply valued. Self-indulgence is viewed with suspicion. The Catholic emphasis on asceza (asceticism) and wyrzeczenie (self-denial) is cultural bedrock. Pleasure exists, but always with an undertone of obligation.

These dimensions inform the **[Language](culture_polish_position_language.md)** (Polski as the acoustic register with its case system and address forms), **[Position](culture_polish_position.md)** (the krąg as fallback when institutions fail), **[History](culture_polish_piece_history.md)** (the broad arc that produced today's institutions), **[Process](culture_polish_process_przetrwanie.md)** (przetrwanie as recurring cultural movement), **[Pieces](culture_polish_piece_konstytucja.md)** (Konstytucja as load-bearing artifact), **[Place](culture_polish_place_warsaw.md)** (Warsaw rebuilt from ruins), and Personas ([Tomasz](culture_polish_persona_male_tomasz.md), [Małgorzata](culture_polish_persona_female_malgorzata.md)): how individuals navigate these cultural pressures. Culture files carry standard hofstede sentinel footers linking to this README; scoring is aggregate across all files, not per-file.

## Content Audit Status

| File | TYPE | Status | Notes |
|------|------|--------|-------|
| culture_polish_position_language.md | position | ✅ Complete | Polski linguistic anchor (Has / Orders / Loses / Drives) |
| culture_polish_piece_history.md | piece | ✅ Complete | 26 Yearbook entries 966 to 2023: chrzest, Grunwald, three partitions, uprisings, Solidarność, EU accession, TK dispute |
| culture_polish_position.md | position | ✅ Complete | Hofstede dimensions: PDI 68, IDV 60, UAI 93, MAS 64, LTO 38, IND 29 |
| culture_polish_process_przetrwanie.md | process | ✅ Complete | Przetrwanie process (Initiated by / Direction / Lever / Echo) |
| culture_polish_piece_konstytucja.md | piece | ✅ Complete | 1997 Constitution as load-bearing artifact |
| culture_polish_place_warsaw.md | place | ✅ Complete | Warsaw as social anchor with offers and withheld |
| culture_polish_persona_male_tomasz.md | persona | ✅ Complete | Architekt: projection, action, position-shaped shadow (fixed narrator-told tail), tell |
| culture_polish_persona_female_malgorzata.md | persona | ✅ Complete | Lekarka: projection, action, position-shaped shadow (fixed narrator-told tail), tell |

---

*Audited May 11, 2026; v2 migration May 13, 2026*

*v0.2.0 - Kai Schlueter - Cultures - May 2026*
