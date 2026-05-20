# Nigeria
## KAI HACKS AI - Culture Package

Region: Africa
**Language(s):** English, Yoruba, Igbo, Hausa
Language: English (Nigerian English / Naija Pidgin) primary; Yoruba lingua-known mother-tongue sub-position; Igbo and Hausa NLP-routed mother-tongue sub-positions (skip the lingua span check per Stage 2c)
Version: v0.2.2
Date: 2026-05-20

---

## Content Overview

| # | File | Kind | Purpose |
|---|---|---|---|
| 1 | [culture_nigerian_position_language.md](culture_nigerian_position_language.md) | language | Nigerian English and Naija Pidgin as the shared acoustic layer |
| 2 | [culture_nigerian_position_language_yoruba.md](culture_nigerian_position_language_yoruba.md) | language (sub) | Yoruba: tone, Èyin/o register, òwe, the aworan metaphor |
| 3 | [culture_nigerian_position_language_igbo.md](culture_nigerian_position_language_igbo.md) | language (sub) | Igbo: aha-first naming, nke a / nke ahụ distinction, kin-precision |
| 4 | [culture_nigerian_position_language_hausa.md](culture_nigerian_position_language_hausa.md) | language (sub) | Hausa: northern lingua franca, Sannu/Yaya kake density, Ajami / Boko script history |
| 5 | [culture_nigerian_piece_history.md](culture_nigerian_piece_history.md) | piece | Nok to Tinubu; the Republic as permanent negotiation |
| 6 | [culture_nigerian_position.md](culture_nigerian_position.md) | position | Nigerian cultural position - state role, narrative anchor |
| 7 | [culture_nigerian_process_oga.md](culture_nigerian_process_oga.md) | process | Oga: patron-client as operating system |
| 8 | [culture_nigerian_piece_jollof.md](culture_nigerian_piece_jollof.md) | piece | Jollof rice as cultural proof of occasion |
| 9 | [culture_nigerian_place_lagos.md](culture_nigerian_place_lagos.md) | place | Lagos: the city that runs before the state catches up |
| 10 | [nigerian_persona_male_emeka.md](nigerian_persona_male_emeka.md) | persona (Igbo) | Emeka, contractor, born 1971; built the circle; cannot see the room without one. Prose in Igbo. |
| 11 | [nigerian_persona_female_funke.md](nigerian_persona_female_funke.md) | persona (Yoruba) | Funke, lawyer, born 1989; holds both legs; cannot see the junior who was never handed the call path. Prose in Yoruba. |
| 12 | [nigerian_persona_female_hauwa.md](nigerian_persona_female_hauwa.md) | persona (Hausa) | Hauwa, Islamiyya headmistress in Sokoto, born 1968; runs the fadar Sarki circle; cannot see the room where the Sultan's writ does not reach. Prose in Hausa. |

---

## Audit Status

| File | Type | Status |
|---|---|---|
| [culture_nigerian_position_language.md](culture_nigerian_position_language.md) | Language (en) | v0.2.0 |
| [culture_nigerian_position_language_yoruba.md](culture_nigerian_position_language_yoruba.md) | Language (yo) | v0.2.0 |
| [culture_nigerian_position_language_igbo.md](culture_nigerian_position_language_igbo.md) | Language (ig, NLP) | v0.2.0 |
| [culture_nigerian_position_language_hausa.md](culture_nigerian_position_language_hausa.md) | Language (ha, NLP) | v0.2.0 |
| [culture_nigerian_piece_history.md](culture_nigerian_piece_history.md) | History | v0.2.0 |
| [culture_nigerian_position.md](culture_nigerian_position.md) | Position | v0.2.0 |
| [culture_nigerian_process_oga.md](culture_nigerian_process_oga.md) | Process | v0.2.0 |
| [culture_nigerian_piece_jollof.md](culture_nigerian_piece_jollof.md) | Piece | v0.2.0 |
| [culture_nigerian_place_lagos.md](culture_nigerian_place_lagos.md) | Place | v0.2.0 |
| [nigerian_persona_male_emeka.md](nigerian_persona_male_emeka.md) | Persona (male, Igbo) | v0.2.0 |
| [nigerian_persona_female_funke.md](nigerian_persona_female_funke.md) | Persona (female, Yoruba) | v0.2.0 |
| [nigerian_persona_female_hauwa.md](nigerian_persona_female_hauwa.md) | Persona (female, Hausa) | v0.2.0 |

---

## Persona Notes

**Emeka** (male, born 1971, Onitsha/Lagos, Igbo): Contractor. Built through the circle. Lived through SAP and the Abacha years. Oha na Eze runs as his default governance model. His position tips toward Igbo merit-permeable circle logic: achievement earns standing, the circle is built as well as inherited. Persona written in Igbo (`language: ig`).

**Funke** (female, born 1989, Ibadan/Lagos, Yoruba): Lawyer. Built in Lagos. She works with both the formal channel and the circle channel in the same move. Her shadow is that this dual access has always been available to her, so she cannot see the junior who was never handed the call path. Persona written in Yoruba (`language: yo`).

**Hauwa** (female, born 1968, Wamakko/Sokoto, Hausa-Fulani): Headmistress of an Islamiyya girls' school. Built inside the fadar Sarki domain - the Sultan's writ, the malam network, the older-women's circle that reaches into the palace through marriage and school ties. Her shadow is that this circle has worked her entire life, so she cannot see the procedural room in Lagos or Abuja where the call she would make has no listener. Persona written in Hausa (`language: ha`).

The three personas together cover the three major Nigerian ethnic positions (Yoruba, Igbo, Hausa-Fulani) without resolving the aggregate into any one of them.

---

## Language Architecture

The mother-tongue arc lands here. Every persona is written in their mother tongue. Bilingual is done through the ladder concept - one language is always winning. The `language:` frontmatter field declares the persona's primary tongue; the 4-channel language-process ladder (`engine/process_<channel>_<width>.md`) carries the second language as the working language at work.

- `language: en` - the shared Nigerian English file, the position, the place, the process, the history, the two pieces. Lingua span check runs.
- `language: yo` - Funke's persona and the Yoruba sub-position. Lingua span check runs (Yoruba is a lingua-known language as of Stage 2c).
- `language: ig` - Emeka's persona and the Igbo sub-position. NLP-routed: lingua does not know Igbo, so the validator skips the deterministic span check and the NLP language_faithful check runs from `culture-review.yml`.
- `language: ha` - Hauwa's persona and the Hausa sub-position. NLP-routed, same path as Igbo.

NLP-language files are excluded from the Hofstede keyword aggregator (Stage 2c), so the country's six declared dimensions are computed from the English files alone. Adding the three sub-positions and the rewrites does not move the aggregate.

---

## Language Notes

Nigerian English is the shared declared language of this package. Naija Pidgin surfaces in specific files as the register that carries what formal English cannot. Three load-bearing Pidgin anchors live in the English layer:

- **No wahala**: in the [language file](culture_nigerian_position_language.md). Social contract running as acceptance. Not agreement.
- **E go better**: in the position file Drives section. Forward motion. The circle extends.
- **E don do**: in the language file. Present-tense closure. The moment is complete.

Three load-bearing mother-tongue anchors now live in their own sub-position files:

- **Yoruba** - ohun (tone), Èyin/o (respect register), òwe (proverb), aworan (image/picture as metaphor for speech).
- **Igbo** - aha (name as identity), nke a / nke ahụ (this / that distinction), kin-precision (nwanne m, dee m, ada m).
- **Hausa** - Sannu / Yaya kake (greeting density), In sha Allahu / Alhamdulillahi / Mashallah (Allah-woven speech), Ajami / Boko (the two scripts).

None of them translates itself.

---

## Build Notes

The position file carries the Nigerian aggregate across all three major groups. The three sub-position language files carry the ethnic specificity of language without resolving the aggregate into one group's logic. The three personas carry the lived facet of each ethnic position. The place file (Lagos) holds the three groups in proximity and names in its Withheld section what Lagos cannot contain: the north, the Delta, the 500 languages running beneath.

Hauwa is anchored in Sokoto, not Lagos, on purpose. Two personas in Lagos and a third also in Lagos would have made the package a Lagos package. Sokoto puts the northern register on its own ground - the fadar Sarki, the Islamiyya school, the malam circle, the Ajami script - where it is not a minority among the Yoruba-Igbo Lagos crowd but the default.

The oga process carries both the functional and dysfunctional registers simultaneously. The Lever section holds the patron-client logic and the accountability-deflection logic without resolving either. Both are real. Both are Nigerian.

Jollof is the piece. The party rice is the proof that the occasion is real. Hauwa's jollof is northern - with masara and stronger spice - and that the dish even reaches Sokoto under the same name is the point.

---

*2026-05-20 | KAI HACKS AI | v0.2.2 | CC-BY-NC-4.0*
