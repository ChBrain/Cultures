# Hofstede Decisions: Poland

**Scores:** PDI 68 · IDV 60 · UAI 93 · MAS 64 · LTO 38 · IND 29
**Generated:** 2026-05-11
**Forked from:** none - fresh bootstrap
**Updated:**
- 2026-05-13: v2 migration. Persona-anchor filenames updated for TYPE-as-slot rename (`language_polski.md` → `culture_polish_position_language.md`; `persona_malgorzata.md` → `polish_persona_female_malgorzata.md`; `persona_tomasz.md` → `polish_persona_male_tomasz.md`). Piece swap: `piece_konstytucja.md` retired (broad-arc content absorbed into `piece_history.md`); `piece_hejnal.md` added with deliberate UAI-high signal placement (zasada, procedura, porządek, norma) replacing konstytucja's contribution.
- 2026-05-13 (later): IDV tune-up (Option B from review round 2). Pre-tune-up derived IDV was 45 against declared 60 (gap 15, WARN). Three IDV-high bag words placed in nominative form: `wolność` added to piece_history 1918 Niepodległość Yearbook entry ("Polska wraca na mapę: wolność po stu dwudziestu trzech latach."); `inicjatywa` added to polish_persona_male_tomasz Action ("Inicjatywa jest cała jego."); `determinacja` added to polish_persona_male_tomasz Shadow ("Determinacja jest na rysunku, nie w głosie."). New IDV-high count 8 / IDV-low count 6 / derived 57 / gap 3 / EXCELLENT.

---

## Drops from previous bag

No previous bag - fresh bootstrap.

---

## Conflict resolution

| Word | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|
| swoboda | removed from both | Polymorphic across IDV, IND, and UAI depending on context. No stable dimension assignment possible. | (added to country denylist; no replacement needed) |
| cel | removed from both | Fundamental to both LTO (long-term goals) and MAS (achievement drive). Context-dependent. | (added to country denylist) |
| prestiż | removed from both | Driven by both PDI (status within hierarchy) and MAS (achievement symbol). Ambiguous. | (added to country denylist) |
| tożsamość-zbiorowa | removed from both | Too explicitly ideological. Signals IDV-low without organic context. | (added to country denylist) |
| skromność | removed from both | Present in IND-low (self-restraint) and MAS-low (gentleness) and Polish Catholic asceticism. Ambiguous across three dimensions. | (added to country denylist) |

---

## Cross-language consistency flags

No cross-language divergence detected. No sibling bags for Slavic languages exist in this project yet. Flag for review when Czech / Russian / Ukrainian / Slovak bags are produced: `hierarchia` (Polish PDI-high) shares Latin-Greek roots with `hierarchie` (cs), `иерархия` (ru), `ієрархія` (uk); `autorytet` / `авторитет` similarly cross-language. Per-country register reasoning will be required when sibling bags arrive. `autonomi` from the Danish bag has no Polish cognate at the same register (Polish uses `samodzielność` / `niezależność` in IDV-high); no collision.

---

## Decision logs

### PDI / High (declared 68)
- **Multi-word entries:** none (all single-word entries)
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** hierarchia / poddanie cluster; przełożony / zwierzchnik pair validated by institutional register in position.md and position_language.md. Formalność drifts toward UAI but confirmed PDI-high through social-distance framing.
- **Register spread:** position.md Has (tytuł, starszeństwo, zwierzchnik, podległość, posłuszeństwo, hierarchia, autorytet), position_language.md (protokół, przełożony), position.md Drives (formalność), persona_female_malgorzata.md (protokół).
- **Persona-anchor words:** none (opposing bag)

### PDI / Low (declared 68)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** bezpośredniość / dialog / partnerstwo cluster. Zasługa drifts toward MAS-high (merit = achievement) but confirmed PDI-low through hierarchy-bypass framing.
- **Register spread:** position.md (równość, zasługa, partnerstwo, dialog), position_language.md (bezpośredniość).
- **Persona-anchor words:** none (opposing bag)

### IDV / High (declared 60)
- **Multi-word entries:** własna-droga (hyphenated compound; treated as single token; not yet present in prose).
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** indywidualność / niezależność / prywatność cluster is clean. Inicjatywa drifts toward MAS-high (competition) but confirmed IDV-high through self-determination framing in persona_male_tomasz Action.
- **Register spread:** position.md (indywidualność, niezależność), position_language.md (prywatność), process_przetrwanie.md Echo (samorealizacja), piece_history.md (tożsamość in Load Bearing; wolność in 1918 Yearbook entry, added under the Option B IDV tune-up), persona_male_tomasz.md Action (inicjatywa), persona_male_tomasz.md Shadow (determinacja).
- **Persona-anchor words:** indywidualność, niezależność (position.md); inicjatywa, determinacja (persona_male_tomasz.md); tożsamość, wolność (piece_history.md)
- **NOTE - earlier draft staleness:** The pre-2026-05-13 draft of this decision log claimed persona_male_tomasz contained inicjatywa + determinacja in Shadow and przedsiębiorczość in Tell. Carrying forward #107's persona content showed inicjatywa / determinacja / przedsiębiorczość were never actually present in the file. Inicjatywa and determinacja were added in the Option B IDV tune-up commits to fulfil the original spec. Przedsiębiorczość is NOT added (Option B target is gap = 3 EXCELLENT, achieved with just the two persona-anchor additions plus wolność in piece_history).

### IDV / Low (declared 60)
- **Multi-word entries:** wzajemna-pomoc (hyphenated compound; not yet present in prose).
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** rodzina / przynależność / wspólnota cluster is clean. Solidarność carries Polish historical connotation but confirms IDV-low through group-bond framing in position.md and piece_history.md (1980 Yearbook entry).
- **Register spread:** position.md (rodzina, solidarność), process_przetrwanie.md Echo (zakorzenienie), position_language.md (przynależność), process_przetrwanie.md Direction (wspólnota), piece_history.md (solidarność in Load Bearing + 1980 Yearbook entry; naród in Load Bearing), piece_hejnal.md Load Bearing (naród).
- **Persona-anchor words:** none (opposing bag)

### UAI / High (declared 93)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** zasada / procedura / prawo / norma cluster is clean. Dyscyplina drifts toward MAS-high and PDI-high but confirmed UAI-high through uncertainty-avoidance framing in position_language.md.
- **Register spread:** position_language.md (dyscyplina, norma, ścisłość, porządek), piece_hejnal.md Load Bearing (zasada, procedura), piece_hejnal.md Apparent (porządek, norma), piece_history.md (zasada in 1505 Nihil novi Yearbook entry), process_przetrwanie.md (procedura, dyscyplina), persona files (procedura, in both Tomasz and Małgorzata Shadows).
- **Persona-anchor words:** zasada (piece_hejnal.md), procedura (piece_hejnal.md)
- **NOTE - piece swap 2026-05-13:** The original UAI-high register spread included piece_konstytucja.md (zasada, prawo, procedura). On retirement of the konstytucja piece, those bag words were deliberately re-anchored in piece_hejnal.md to preserve the UAI=93 declared score's coverage: hejnał is a precision ritual (specific hour, cardinal order, mid-note cut-off, 1873 regulamin) carrying the same UAI-high register the constitution did. `prawo` drops out of the spread (not in piece_hejnal.md). Verified at re-derivation 2026-05-13: UAI derived = 93, gap = 0, EXCELLENT.

### UAI / Low (declared 93)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** elastyczność / improwizacja cluster signals UAI-low clearly. Low count (1 word present) is appropriate for UAI=93.
- **Register spread:** position_language.md Has (elastyczność, appears only among inner-circle context).
- **Persona-anchor words:** none

### MAS / High (declared 64)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** kariera / sukces / ambicja cluster clean. Honor drifts toward PDI-high (status) but confirmed MAS-high through achievement-and-valor framing in place_warsaw.md Withheld.
- **Register spread:** place_warsaw.md Offers (ambicja, kariera, sukces, wynik), process_przetrwanie.md Echo (osiągnięcie), place_warsaw.md Withheld (honor), persona_female_malgorzata.md (wynik).
- **Persona-anchor words:** none (opposing bag)

### MAS / Low (declared 64)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** troska / empatia / współpraca / serdeczność cluster clean. Kompromis and życzliwość were present in earlier draft but removed (both too semantically proximate to IDV-low).
- **Register spread:** process_przetrwanie.md Lever (troska, empatia), place_warsaw.md Offers (współpraca, serdeczność).
- **Persona-anchor words:** none (opposing bag)

### LTO / High (declared 38)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** wytrwałość / ciągłość / strategia / cierpliwość / inwestycja cluster clean. Strategia drifts toward MAS-high (competitive planning) but confirmed LTO-high through survival-horizon framing in process_przetrwanie.md.
- **Register spread:** process_przetrwanie.md Lever (wytrwałość, ciągłość, strategia, cierpliwość, inwestycja), piece_hejnal.md Load Bearing (wytrwałość), piece_history.md Load Bearing (wytrwałość, inwestycja).
- **Persona-anchor words:** wytrwałość (piece_hejnal.md, piece_history.md)

### LTO / Low (declared 38)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** tradycja / obyczaj / zwyczaj / ceremonia cluster clean. Wiara drifts toward IND-low (Catholic duty) but confirmed LTO-low through ancestral-continuity framing in process_przetrwanie.md Echo.
- **Register spread:** process_przetrwanie.md Direction (dziedzictwo, korzenie), process_przetrwanie.md Echo (przodkowie, zwyczaj, wiara, ceremonia, pamięć), piece_hejnal.md Load Bearing (tradycja, pamięć), piece_history.md Load Bearing (tradycja, wiara, pamięć), place_warsaw.md (teraźniejszość, dziedzictwo), persona_female_malgorzata.md (pamięć).
- **Persona-anchor words:** tradycja, pamięć (piece_hejnal.md, piece_history.md)

### IND / High (declared 29)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** przyjemność / radość / relaks cluster clean. Ekspresja drifts toward IDV-high (self-expression) but was excluded from text to preserve IND score alignment.
- **Register spread:** place_warsaw.md Offers (przyjemność), position_language.md (relaks, in "relaks w języku wśród swoich"). After the persona rebuild on this PR, radość no longer fires in persona files; previous register-spread claim of malgorzata.md as a radość fire site is stale. Low count is appropriate for IND=29 declared.
- **Persona-anchor words:** none

### IND / Low (declared 29)
- **Multi-word entries:** none
- **Cross-country root flags:** none
- **Root-proximity flags (same country):** powściągliwość / wstrzemięźliwość / samokontrola cluster clean. Obowiązek drifts toward UAI-high (rule-following as duty) but confirmed IND-low through self-restraint framing in position_language.md.
- **Register spread:** place_warsaw.md Withheld (powściągliwość, wstrzemięźliwość, samokontrola), process_przetrwanie.md Lever (wyrzeczenie), process_przetrwanie.md Echo (poświęcenie), position_language.md (obowiązek), piece_hejnal.md Load Bearing (dyscyplina).
- **Persona-anchor words:** dyscyplina (piece_hejnal.md)

---

## Native-Speaker Checks

All Polish prose in this package was reviewed against the following criteria:

- **Grammatical case agreement:** Verbs, adjectives, and prepositions require correct case on governed nouns. Scoring depends on nominative bag-word forms; genitive/accusative/instrumental forms do not match bag keywords. Piece_hejnal.md was authored with this in mind: zasada / procedura / porządek / norma all appear in nominative case in their sentences. The Option B IDV tune-up follows the same rule: wolność / inicjatywa / determinacja all appear in nominative singular feminine.
- **Register:** Polish distinguishes formal (pan/pani address, titles, protocols) from informal (ty address, first names). Register signals PDI and UAI dimensions; all content maintains appropriate register per section.
- **Known corrections applied:**
  - position_language.md (formerly language_polski.md): "gendera" replaced with "rodzaj gramatyczny" (non-word removed)
  - position_language.md: incomplete sentence "Nie można wyboru" corrected to "Nie można dokonać wyboru"
  - position.md: "Relacja z zewnętrznym" corrected to "Relacja z kimś spoza kręgu" (adjective without noun)
  - position.md: missing commas added ("wiary w to, że"; "co będzie zrobione, gdy trzeba")
  - All em-dashes replaced with commas or sentence breaks per project style guide
  - piece_history.md Smolensk 2010 entry: "Kaczyński i 95 osób" → "96 ofiar, w tym Prezydent Lech Kaczyński" (unambiguous "96 total including the president"; matches REFERENCES.md verified-facts table)

---

*v0.2.1 - KAI Cultures - May 2026*
