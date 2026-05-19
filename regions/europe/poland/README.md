# Poland - Culture Content

[**Download poland.zip**](https://github.com/ChBrain/Cultures/releases/latest/download/poland.zip) - all culture files plus the engine stack and instructions, flattened for a single upload.

**Language(s):** Polish (Polski)

## Culture Map

Poland has two personas, [Tomasz](culture_polish_persona_male_tomasz.md) and [Małgorzata](culture_polish_persona_female_malgorzata.md). Each persona carries a gender from the [culture engine](../../../engine/), speaks [Polski](culture_polish_position_language.md), and holds the [Polish cultural position](culture_polish_position.md).

The cultural position has a primary [place](culture_polish_place_warsaw.md), holds a primary [piece](culture_polish_piece_hejnal.md), runs a primary [process](culture_polish_process_przetrwanie.md), and moves through its [history](culture_polish_piece_history.md).

## Content Overview

Filename convention: `culture_<adj>_<TYPE>_<NAME>.md` where TYPE is one of the 5 KAI structural types (process, position, piece, place, persona). Single-instance kinds (language, history) drop the redundant country suffix.

| File | TYPE | Purpose |
|------|------|---------|
| `culture_polish_position_language.md` | position | Polski - linguistic anchor |
| `culture_polish_piece_history.md` | piece | The arc of Polish history (966 to 2023) |
| `culture_polish_position.md` | position | Polish cultural position (krąg and state) - narrative anchor |
| `culture_polish_process_przetrwanie.md` | process | Przetrwanie - survival as cultural direction |
| `culture_polish_piece_hejnal.md` | piece | Hejnał Mariacki - hourly trumpet call from the tower of Bazylika Mariacka, Kraków; broadcast nationally at noon |
| `culture_polish_place_warsaw.md` | place | Warsaw - capital city as geographical anchor |
| `culture_polish_persona_male_tomasz.md` | persona | Tomasz - architect, b. 1990 |
| `culture_polish_persona_female_malgorzata.md` | persona | Dr. Małgorzata - internist, b. 1958 |

## Cultural Anchors

Polish culture in this package is organized around a few anchors. Hierarchies and titles are visible from the first meeting, and yet expertise (zasługa) tempers pure rank. Individual ambition coexists with family loyalty and Catholic collectivism: post-1989 career drive sits next to obligations that do not negotiate. Polish institutions document everything; risk and ambiguity are uncomfortable, clarity and written rules are comforting. The cultural arc honors tradition, memory (pamięć), and ancestral roots (korzenie) while also planning strategically (inwestycja, strategia). Restraint and duty are virtues; self-indulgence is viewed with suspicion.

These anchors inform the **[Language](culture_polish_position_language.md)** (Polski as the acoustic register with its case system and address forms), **[Position](culture_polish_position.md)** (the krąg as fallback when institutions fail), **[History](culture_polish_piece_history.md)** (the broad arc that produced today's institutions), **[Process](culture_polish_process_przetrwanie.md)** (przetrwanie as recurring cultural movement), **[Pieces](culture_polish_piece_hejnal.md)** (Hejnał Mariacki as the daily ritual that holds a wound through repetition), **[Place](culture_polish_place_warsaw.md)** (Warsaw rebuilt from ruins), and Personas ([Tomasz](culture_polish_persona_male_tomasz.md), [Małgorzata](culture_polish_persona_female_malgorzata.md)): how individuals navigate these cultural pressures. Hofstede dimension scores for Poland are maintained centrally in `data/hofstede_scores.json` (issue #257: cite, don't reproduce); this deployable README cites Hofstede as a source without restating the score table.

## Content Audit Status

| File | TYPE | Status | Notes |
|------|------|--------|-------|
| culture_polish_position_language.md | position | ✅ Complete | Polski linguistic anchor (Has / Orders / Loses / Drives) |
| culture_polish_piece_history.md | piece | ✅ Complete | 26 Yearbook entries 966 to 2023: chrzest, Grunwald, three partitions, uprisings, 1918 niepodległość, Solidarność, EU accession, TK dispute |
| culture_polish_position.md | position | ✅ Complete | Krąg-based cultural position with hierarchy, competence-tempered authority, written law read with context |
| culture_polish_process_przetrwanie.md | process | ✅ Complete | Przetrwanie process (Initiated by / Direction / Lever / Echo) |
| culture_polish_piece_hejnal.md | piece | ✅ Complete | Hejnał Mariacki: hourly trumpet call, Tatar-arrow mid-note cut-off since 1241, broadcast on Polskie Radio Jedynka at noon since 1927 (18 Yearbook entries) |
| culture_polish_place_warsaw.md | place | ✅ Complete | Warsaw as social anchor with offers and withheld |
| culture_polish_persona_male_tomasz.md | persona | ✅ Complete | Architekt b. 1990: PAST with projection linking all culture files + 4-channel language ladder; shadow as blind spot (krąg ma granice; mieszkaniec za 40 lat nierealny); tell is a physical body action |
| culture_polish_persona_female_malgorzata.md | persona | ✅ Complete | Lekarka internistka b. 1958: PAST with projection linking all culture files + 4-channel language ladder; shadow as blind spot (protokół nie zastępuje kręgu); tell is a physical body action |

---

*Audited May 19, 2026 (v0.2.0 fix pass: PAST personas tightened, projections link all culture files + 4-channel language ladder, REFERENCES rebuilt 1:1, hejnał Yearbook expanded, score tables removed per #257)*

*v0.2.0 - Kai Schlueter - Cultures - May 2026*
