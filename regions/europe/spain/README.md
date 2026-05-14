# Spain - Culture Content

**Language(s):** Spanish (Español)

This folder contains culture content for Spain: the Spanish language, the historical arc, the cultural position, the negotiation process, the Conquista as defining piece, Madrid, and two personas embodying the culture.

## Quick Start

Download the complete Spain culture package for Claude.ai:
- [**spain.zip**](https://github.com/ChBrain/Cultures/releases/latest/download/spain.zip) - All culture files + engine stack + instructions

The zip contains all culture files flattened at root level with links rewritten for Claude consumption.

## Content Overview

Filename convention: `culture_<adj>_<TYPE>_<NAME>.md` where TYPE is one of the 5 KAI structural types (process, position, piece, place, persona). Single-instance kinds (language, history) drop the redundant country/variety suffix.

| File | TYPE | Purpose |
|------|------|---------|
| `culture_spanish_position_language.md` | position | Castellano - linguistic anchor |
| `culture_spanish_piece_history.md` | piece | The arc of Spanish history (218 BC to 2024) |
| `culture_spanish_position.md` | position | Spanish cultural position - narrative anchor |
| `culture_spanish_process_negociar.md` | process | Negociar - negotiating as cultural process |
| `culture_spanish_piece_conquista.md` | piece | La Conquista - the discrete colonial encounter still active in the culture |
| `culture_spanish_place_madrid.md` | place | Madrid - capital city as geographical anchor |
| `culture_spanish_persona_male_alejandro.md` | persona | Alejandro - traductor e intérprete, b. 1978 |
| `culture_spanish_persona_female_isabel.md` | persona | Isabel - diplomática, b. 1955 |

## Hofstede Cultural Dimensions

| Dimension | Score | Level | Description |
|---|---|---|---|
| PDI | 57 | **Moderate** | Hierarchy respected but not absolute. Cargo carries authority, but the superior who fails to care for his people loses command without losing title. Position is relation before it is structure. |
| IDV | 51 | **Moderate** | Balance between personal initiative and group obligation. Trayectoria and criterio matter, but familia, comunidad and red are the first orders of loyalty. Identity is held with others, not against them. |
| UAI | 86 | **High** | Very High in the classifier sense (86 sits inside the 80-100 band). Strong need for norms, structure, planning. Bureaucracy is dense; institutional documents are long; the affect-level need for seguridad and garantía sits beneath the regulatory layer. |
| MAS | 42 | **Moderate** | Cooperation and dignidad sit alongside ambición. Career and reconocimiento matter, but hospitalidad, cuidado and conciliación are equally valued. Achievement with social conscience, not ruthless individualism. |
| LTO | 48 | **Moderate** | Mix of present-orientation (tradición, honor, orgullo, memoria, rito, ceremonia) with strategic future-investment (inversión, desarrollo, formación, proyección). Spanish culture honours tradition while developing toward Europe. |
| IND | 44 | **Moderate** | Gratification balanced with social duty. Disfrute, placer, ocio, alegría, juerga and diversión are real cultural registers, but contención, deber, decoro, discreción and mesura carry equal weight, especially in older registers. |

**Source:** Hofstede Insights - empirical research from *Cultures and Organizations*

## Hofstede Alignment Audit

| Dimension | Declared | Derived | Gap | Status |
|---|---|---|---|---|
| PDI | 57 | 61 | 4 | ✅ EXCELLENT |
| IDV | 51 | 50 | 1 | ✅ EXCELLENT |
| UAI | 86 | 83 | 3 | ✅ EXCELLENT |
| MAS | 42 | 47 | 5 | ✅ EXCELLENT |
| LTO | 48 | 47 | 1 | ✅ EXCELLENT |
| IND | 44 | 40 | 4 | ✅ EXCELLENT |

**Derivation method**: Each keyword in hofstede_bag.yaml is counted once per culture file if present (word-boundary matching against the bag word in nominative form; no substring inflation). Score = (high_keyword_count / (high_count + low_count)) × 100. Gap tolerance: ±10 PASS, ±5 EXCELLENT. Re-derived May 14, 2026 against the post-bag-fix content (8 bag swaps: autonomía → independencia, planificación → método, espontaneidad → naturalidad, informalidad → desenfado, flexibilidad → versatilidad, previsión-collision → proyección in LTO-high, fiesta → rito, celebración → ceremonia). All 6 dimensions within ±5 EXCELLENT band. CI L4f will confirm.

## How Dimensions Shape Spanish Culture

- **Moderate PDI (57)** sits between Northern European flatness and Latin American steepness. Cargo and jerarquía carry weight, but the superior is accountable to los suyos. Accessibility of the boss is not weakness; it is proof he is at the front. Igualdad and proximidad are post-1978 values that have become habit on the street and at the table.

- **Moderate IDV (51)** holds tension. Spanish people pursue personal trayectoria, criterio, voluntad and responsabilidad, but familia, grupo, comunidad and vínculo are the first orders of loyalty. The red is what activates when the institution fails. Identity is held with others, not against them.

- **High UAI (86)** drives the density of norma, reglamento, orden, estructura, burocracia and the affect-layer of seguridad and garantía. Spanish institutions document everything, and beneath the documentation is the older anxiety: that without certeza, the relation cannot hold. Historical trauma (Civil War, dictatorship, transition) embedded this need for institutional certainty.

- **Moderate MAS (42)** means achievement matters but is held in balance with cooperation. Competencia, logro, ambición and reconocimiento are real registers, but dignidad, cuidado, compasión, conciliación, empatía and hospitalidad sit equally on the cultural ledger. Spain values reaching the top, but the manner of getting there matters as much as the position.

- **Moderate LTO (48)** carries a paradox. Tradición, honor, orgullo, memoria, legado, costumbre, rito and ceremonia are present-anchoring forces with deep cultural weight, but inversión, desarrollo, futuro, paciencia, formación and proyección are equally real in the post-1986 European era. The past is honoured and the future is invested in, simultaneously.

- **Moderate IND (44)** balances disfrute, placer, ocio, alegría, juerga and diversión with contención, deber, sacrificio, decoro, sobriedad and discreción. Gratification is real and cultural (the late dinner, the long mesa, the terraza in October), but it sits inside a frame of obligation to los suyos and decorum in public.

These dimensions inform the **[Language](culture_spanish_position_language.md)** (Castellano as the acoustic register that places relation before subject), **[History](culture_spanish_piece_history.md)** (the broad arc from Roman conquest through Al-Ándalus, the Reconquista, the imperial cycle, the Civil War, Franco, the transition, EU entry, and the unresolved territorial question), **[Position](culture_spanish_position.md)** (the dual loyalty to jerarquía and to los suyos), **[Process](culture_spanish_process_negociar.md)** (negociar as the recurring cultural movement where the relation outweighs the term), **[Piece](culture_spanish_piece_conquista.md)** (La Conquista as the discrete formative encounter still active in the culture), **[Place](culture_spanish_place_madrid.md)** (Madrid as kilómetro cero), and Personas ([Alejandro](culture_spanish_persona_male_alejandro.md), [Isabel](culture_spanish_persona_female_isabel.md)): how individuals navigate these cultural pressures. Culture files carry standard hofstede sentinel footers linking to this README; scoring is aggregate across all files, not per-file.

## Content Audit Status

| File | TYPE | Status | Notes |
|------|------|--------|-------|
| culture_spanish_position_language.md | position | ✅ Complete | Castellano linguistic anchor (Has / Orders / Loses / Drives) |
| culture_spanish_piece_history.md | piece | ✅ Complete | 21 Yearbook entries 218 BC to 2024: Roman conquest, Al-Ándalus, Reconquista, 1492, Quijote, 1808, 1898, Civil War, Franco, transition, EU, 15-M, Catalan referendum, amnesty law |
| culture_spanish_position.md | position | ✅ Complete | Hofstede dimensions: PDI 57, IDV 51, UAI 86, MAS 42, LTO 48, IND 44 |
| culture_spanish_process_negociar.md | process | ✅ Complete | Negociar process (Initiated by / Direction / Lever / Echo) |
| culture_spanish_piece_conquista.md | piece | ✅ Complete | La Conquista with 12 Yearbook entries 711 to 2021 |
| culture_spanish_place_madrid.md | place | ✅ Complete | Madrid as social anchor with Shown / Holds / Offers / Withheld |
| culture_spanish_persona_male_alejandro.md | persona | ✅ Complete | Traductor e intérprete: projection, action, position-shaped shadow, tell |
| culture_spanish_persona_female_isabel.md | persona | ✅ Complete | Diplomática: projection, action, position-shaped shadow, tell |

---

*Audited May 14, 2026 (re-derived after L4-bag-quality fix; all 6 dimensions ±5 EXCELLENT)*

*v0.2.1 - Kai Schlueter - Cultures - May 2026*
