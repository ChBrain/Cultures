# Hofstede Decisions: Poland

**Scores:** PDI 68 - IDV 60 - UAI 93 - MAS 64 - LTO 38 - IND 29

This file documents the rationale for keyword selection in hofstede_bag.yaml.

---

## Denylist (5 rejected words)

**swoboda** - Polymorphic across IDV, IND, and UAI depending on context. No stable dimension assignment possible.

**cel** - Fundamental to both LTO (long-term goals) and MAS (achievement drive). Context-dependent; causes dimension leakage regardless of register.

**prestiż** - Driven by both PDI (status within hierarchy) and MAS (achievement symbol). Ambiguous dimension assignment.

**tożsamość-zbiorowa** - Too explicitly ideological. Signals IDV-low without organic context; cannot appear naturally in prose without forcing interpretation.

**skromność** - Present in IND-low (self-restraint) and MAS-low (gentleness) and Polish Catholic asceticism. Ambiguous across three dimensions.

---

## Per-Bag Decision Logs

### PDI / High (declared 68)
- **Multi-word:** none (all single-word entries)
- **Root-proximity:** hierarchia/poddanie cluster; przetożony/zwierzchnik pair validated by institutional register in position.md and language_polski.md. Formalność drifts toward UAI but confirmed PDI-high through social-distance framing.
- **Register spread:** position.md (Has: tytuł, starszeństwo, zwierzchnik, podłegłość, posłuszeństwo, hierarchia, autorytet), language_polski.md (protokół, przełożony), position.md Drives (formalność).

### PDI / Low (declared 68)
- **Multi-word:** none
- **Root-proximity:** bezpośwredniość/dialog/partnerstwo cluster. Zasługa drifts toward MAS-high (merit = achievement) but confirmed PDI-low through hierarchy-bypass framing.
- **Register spread:** position.md (równość, zasługa, partnerstwo, dialog), language_polski.md (bezpośredniość).

### IDV / High (declared 60)
- **Multi-word:** własna-droga (hyphenated compound; treated as single token)
- **Root-proximity:** indywidualność/niezależność/prywatność cluster is clean. Inicjatywa drifts toward MAS-high (competition) but confirmed IDV-high through self-determination framing in tomasz Shadow.
- **Register spread:** position.md (indywidualność, niezależność), language_polski.md (prywatność), przetrwanie Echo (samorealizacja), tomasz Shadow (inicjatywa, determinacja), tomasz Tell (przedsiębiorczość).

### IDV / Low (declared 60)
- **Multi-word:** wzajemna-pomoc (hyphenated compound)
- **Root-proximity:** rodzina/przynależność/wspólnota cluster is clean. Solidarność carries Polish historical connotation but confirms IDV-low through group-bond framing in position.md.
- **Register spread:** position.md (rodzina, solidarność, zakorzenienie in przetrwanie Echo), language_polski.md (przynależność), przetrwanie Direction (wspólnota).

### UAI / High (declared 93)
- **Multi-word:** none
- **Root-proximity:** zasada/procedura/prawo/norma cluster is clean. Dyscyplina drifts toward MAS-high and PDI-high but confirmed UAI-high through uncertainty-avoidance framing in language_polski.md.
- **Register spread:** language_polski.md (dyscyplina, norma, ścisłość, porządek), piece_konstytucja.md (zasada, prawo, procedura).

### UAI / Low (declared 93)
- **Multi-word:** none
- **Root-proximity:** elastyczność/improwizacja cluster signals UAI-low clearly. Low count (1 word present) is appropriate for UAI=93.
- **Register spread:** language_polski.md (elastyczność in Has: appears only among inner-circle context).

### MAS / High (declared 64)
- **Multi-word:** none
- **Root-proximity:** kariera/sukces/ambicja cluster clean. Honor drifts toward PDI-high (status) but confirmed MAS-high through achievement-and-valor framing in warsaw Withheld.
- **Register spread:** warsaw Offers (ambicja, kariera, sukces), przetrwanie Echo (osiągnięcie), warsaw Offers (wynik), warsaw Withheld (honor).

### MAS / Low (declared 64)
- **Multi-word:** none
- **Root-proximity:** troska/empatia/współpraca/serdeczność cluster clean. Kompromis and życzliwość were present in earlier draft but removed (both too semantically proximate to IDV-low).
- **Register spread:** przetrwanie Lever (troska, empatia), warsaw Offers (współpraca, serdeczność).

### LTO / High (declared 38)
- **Multi-word:** none
- **Root-proximity:** wytrwałość/ciągłość/strategia/cierpliwość/inwestycja cluster clean. Strategia drifts toward MAS-high (competitive planning) but confirmed LTO-high through survival-horizon framing in przetrwanie.
- **Register spread:** przetrwanie Lever (wytrwałość, ciągłość, strategia, cierpliwość, inwestycja).

### LTO / Low (declared 38)
- **Multi-word:** none
- **Root-proximity:** tradycja/obyczaj/zwyczaj/ceremonia cluster clean. Wiara drifts toward IND-low (Catholic duty) but confirmed LTO-low through ancestral-continuity framing in przetrwanie Echo.
- **Register spread:** przetrwanie Direction (dziedzictwo, korzenie), przetrwanie Echo (przodkowie, zwyczaj, wiara, ceremonia, pamięć).

### IND / High (declared 29)
- **Multi-word:** none
- **Root-proximity:** przyjemność/radość/relaks cluster clean. Ekspresja drifts toward IDV-high (self-expression) but was excluded from text to preserve IND score alignment.
- **Register spread:** warsaw Offers (przyjemność), persona_malgorzata.md (radość, relaks, organic).

### IND / Low (declared 29)
- **Multi-word:** none
- **Root-proximity:** powciągliwość/wstrzemieźliwość/samokontrola cluster clean. Obowiązek drifts toward UAI-high (rule-following as duty) but confirmed IND-low through self-restraint framing in language_polski.md.
- **Register spread:** warsaw Withheld (powciągliwość, wstrzemieźliwość, samokontrola), przetrwanie Lever (wyrzeczenie), przetrwanie Echo (poświęcenie), language_polski.md (obowiązek).

---

## Native-Speaker Checks

All Polish prose in this package was reviewed against the following criteria:

- **Grammatical case agreement:** Verbs, adjectives, and prepositions require correct case on governed nouns. Scoring depends on nominative bag-word forms; genitive/accusative/instrumental forms do not match bag keywords.
- **Register:** Polish distinguishes formal (pan/pani address, titles, protocols) from informal (ty address, first names). Register signals PDI and UAI dimensions; all content maintains appropriate register per section.
- **Known corrections applied:**
  - language_polski.md: "gendera" replaced with "rodzaj gramatyczny" (non-word removed)
  - language_polski.md: incomplete sentence "Nie można wyboru" corrected to "Nie można dokonać wyboru"
  - position.md: "Relacja z zewnętrznym" corrected to "Relacja z kimś spoza kręgu" (adjective without noun)
  - position.md: missing commas added ("wiary w to, że"; "co będzie zrobione, gdy trzeba")
  - All em-dashes replaced with commas or sentence breaks per project style guide

---

*v0.1.0 - KAI Cultures - May 2026*
