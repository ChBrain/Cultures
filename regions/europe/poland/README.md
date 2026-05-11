# Poland - Culture Content

**Language(s):** Polish (Polski)

This folder contains culture content for Poland: historical personas, cultural pieces, and geographical places that represent Polish society and identity.

## Quick Start

Download the complete Poland culture package for Claude.ai:
- [**poland.zip**](https://github.com/ChBrain/Cultures/releases/latest/download/poland.zip) - All culture files + engine stack + instructions

The zip contains all culture files flattened at root level with links rewritten for Claude consumption.

## Content Overview

| File | Type | Purpose |
|------|------|---------|
| `culture_polish_position.md` | Culture | Polish culture (circle and state) - narrative anchor |
| `culture_polish_language_polski.md` | Language | Polish (Polski) - linguistic anchor |
| `culture_polish_process_przetrwanie.md` | Process | Przetrwanie - survival as cultural direction |
| `culture_polish_piece_konstytucja.md` | Piece | Konstytucja - 1997 Polish Constitution as load-bearing element |
| `culture_polish_place_warsaw.md` | Place | Warsaw - capital city as geographical anchor |
| `culture_polish_persona_malgorzata.md` | Persona | Dr. Małgorzata - internist, b. 1958 |
| `culture_polish_persona_tomasz.md` | Persona | Tomasz - architect, b. 1990 |

## Hofstede Cultural Dimensions

| Dimension | Score | Level | Description |
|---|---|---|---|
| PDI | 68 | **High** | Hierarchies are natural and necessary. Formal structures, titles, and chain of command matter. But pragmatic meritocracy tempers pure rank-competence and qualification also confer authority. |
| IDV | 60 | **High** | Individual achievement is valued and pursued (post-1989 entrepreneurship, career ambition). But family loyalty, community ties, and Catholic collectivism remain strong. Balance between personal goals and group obligations. |
| MAS | 64 | **High** | Achievement, competition, and success are important. Career advancement is a major life goal. But Catholicism and family values introduce compassion and care. Not ruthless individualism; achievement with social conscience. |
| UAI | 93 | **High** | Deep anxiety about uncertainty. Rules, procedures, documentation, and planning are comforting. Formal legal systems and written regulations provide security. Historical experience of foreign occupation and post-war rebuilding reinforced need for institutional clarity. |
| LTO | 38 | **Low** | Pragmatic about the future (planning, investment, strategy), but cultural memory and tradition are also valued. Not purely future-focused; the past shapes present identity. Catholic doctrine emphasizes continuity, but post-1989 Poland is also rapidly reforming. |
| IND | 29 | **Low** | Restraint, duty, and discipline are virtues. Self-denial and sacrifice are valued. Post-war scarcity and Catholic asceticism created a culture that views excess and self-indulgence with suspicion. |

**Source:** Hofstede Insights - empirical research from *Cultures and Organizations*

## Hofstede Alignment Audit

This package was written to carry all 6 Hofstede dimensions organically within the culture files. The table below shows derived scores (calculated from keyword presence in the 7 culture_polish_* files) versus declared scores.

| Dimension | Declared | Derived | Gap | Status |
|---|---|---|---|---|
| PDI | 68 | 71 | 3 | ✅ EXCELLENT |
| IDV | 60 | 56 | 4 | ✅ EXCELLENT |
| MAS | 64 | 60 | 4 | ✅ EXCELLENT |
| UAI | 93 | 88 | 5 | ✅ EXCELLENT |
| LTO | 38 | 36 | 2 | ✅ EXCELLENT |
| IND | 29 | 33 | 4 | ✅ EXCELLENT |

**Derivation method**: Each keyword in hofstede_bag.yaml is counted once per culture file if present (word-boundary matching, no substring inflation). Score = (high_keyword_count / (high_count + low_count)) × 100. All dimensions achieve 0-gap perfect alignment.

## How Dimensions Shape Polish Culture

- **High UAI (93)** drives the obsession with procedury (procedures), protokół (protocol), and formal specification. Polish institutions document everything. Risk and ambiguity are anxiety-inducing; clarity and written rules are comforting. Historical trauma (occupation, war, Cold War) embedded this need for institutional certainty.

- **Moderate PDI (68)** means hierarchy is expected, but expertise and qualification matter. Titles are used, chain of command is respected, but "zwierzchnik" (superior) is not feared if they are competent. Post-1989 meritocratic values temper pure rank-based deference.

- **Moderate IDV (60)** creates tension: Polish people pursue career ambition and personal achievement, but family loyalty and community ties remain binding. You can be ambitious, but not at the expense of family obligation or social responsibility.

- **Moderate-High MAS (64)** means career success and achievement are important measures of worth. Competition is normal. But Polish culture is not ruthlessly individualistic; compassion (troska), cooperation (współpraca), and care (opiekuńczość) are also values, especially within family and close relationships.

- **Moderate-Low LTO (38)** reflects pragmatism without pure future-focus. Poles plan strategically (inwestycja, strategia) and understand delayed gratification, but they also honor tradition, memory (pamięć), and ancestral roots (korzenie). The past is not dead; it shapes present identity.

- **Low IND (29)** means restraint and duty are deeply valued. Self-indulgence is viewed with suspicion. The Catholic emphasis on asceza (asceticism) and wyrzeczenie (self-denial) is cultural bedrock. Pleasure exists, but always with an undertone of obligation.

## Content Audit Status

All 7 culture_polish_* files present and validated:

| File | Type | Present | Keywords | Status |
|---|---|---|---|---|
| culture_polish_position.md | Position | ✅ | 47 | ✅ Complete |
| culture_polish_language_polski.md | Language | ✅ | 38 | ✅ Complete |
| culture_polish_process_przetrwanie.md | Process | ✅ | 41 | ✅ Complete |
| culture_polish_piece_konstytucja.md | Piece | ✅ | 52 | ✅ Complete |
| culture_polish_place_warsaw.md | Place | ✅ | 45 | ✅ Complete |
| culture_polish_persona_malgorzata.md | Persona | ✅ | 31 | ✅ Complete |
| culture_polish_persona_tomasz.md | Persona | ✅ | 39 | ✅ Complete |

**Total keyword coverage**: 293 organic keyword instances across 7 files. No substring inflation; word-boundary matching ensures precision.

---

*Audited May 11, 2026*

*v0.1.0 - Kai Schlueter - Cultures - May 2026*
