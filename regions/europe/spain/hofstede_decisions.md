# Hofstede Decisions: Spain

**Scores:** PDI 57 · IDV 51 · UAI 86 · MAS 42 · LTO 48 · IND 44
**Generated:** 2026-05-12
**Forked from:** none -- fresh bootstrap
**Updated:**
- 2026-05-13: v2 migration -- TYPE-as-slot rename, persona-anchor filename refresh, derived-score tune-up.
- 2026-05-14: Bag quality remediation. Eight bag words moved out of bags because they were also in the country denylist (self-collision detected by `test_hofstede_bag_quality::test_keywords_not_in_country_denylist`), plus one cross-bag collision (`previsión` in both UAI.high and LTO.high) resolved. See "Bag quality remediation 2026-05-14" section below. All replacements verified clean against denylist + other bags. Re-derived Hofstede after the swaps: all 6 dimensions within ±5 EXCELLENT (PDI 4 / IDV 1 / UAI 3 / MAS 5 / LTO 1 / IND 4).

---

## Drops from previous bag

No previous bag -- fresh bootstrap.

---

## Conflict resolution

| Word | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|
| autonomía | IDV-high | Individual self-direction is IDV; flat structures without autonomy can exist; PDI-low describes relationships not rights | cercanía (PDI-low) |
| protocolo | UAI-high | Rule-structure is UAI's core register; protocol as procedure not as status marker | cargo (PDI-high) |
| consenso | MAS-low | Cooperative register dominates over PDI-low flat-structure reading | consulta (PDI-low) |
| solidaridad | IDV-low | Group-loyalty signal dominates over care/cooperation reading | compasión (MAS-low) |
| fiesta | LTO-low | Present-orientation anchor; culturally load-bearing in Spanish as collective present-moment ritual | goce (IND-high) |
| celebración | LTO-low | Collective ritual register dominates over gratification register | disfrute (IND-high) |
| espontaneidad | UAI-low | Ambiguity-tolerance register dominates | alegría (IND-high) |
| informalidad | UAI-low | Rule-avoidance register dominates over PDI-low flat-structure reading | horizontalidad (PDI-low) |
| flexibilidad | UAI-low | Ambiguity-tolerance register dominates over LTO-high adaptability reading | sostenibilidad (LTO-high) |
| libertad | IDV-high | Individual agency register dominates over gratification reading | vitalidad (IND-high) |

---

## Resolution pass: review-flagged items

| Word | Action | Rule-cited reason | Replacement |
|---|---|---|---|
| individuo | dropped from IDV-high | Score-band calibration: at IDV 51 the bag should not assert individual primacy; individuo reads IDV 70+ territory | personalidad |
| calidad-de-vida | dropped from MAS-low | Hyphenated compound; space-separated is standard Spanish; matcher fires on "calidad" alone; contract broken | dignidad |
| armonía | dropped from MAS-low | Cross-bag collision: armonía in Spanish prose scores IDV-low (group harmony) before MAS-low (cooperation) | generosidad |
| regla | dropped from UAI-high | Redundant with norma; same rule-cluster register; score-band 86 requires affect-register words not density of synonyms | seguridad |
| procedimiento | dropped from UAI-high | Redundant with reglamento; same procedural register cluster | garantía |
| pronto | dropped from LTO-low | Adverb reading dominates over cultural-register reading in prose; matcher fires on wrong reading | memoria |
| planificación | dropped from LTO-high | Within-country collision: planificación retained in UAI-high (planning-as-control); LTO needs investment vocabulary not control vocabulary | formación |
| moderación | dropped from IND-low | Redundant with mesura; mesura is more culturally specific and classical register | austeridad |
| gozo | dropped from IND-high | Religious register (gozo espiritual) muddies IND-high signal; matcher fires on devotional prose | juerga |

---

## Bag quality remediation 2026-05-14

These ten denylisted words were retained in the original bag draft and the resolution-pass log above documents them as bag assignments. CI test `test_hofstede_bag_quality::test_keywords_not_in_country_denylist` correctly flags this as inconsistent: a word in the country denylist cannot also live in a bag, regardless of how the Conflict resolution table reads. Plus one within-country collision (`previsión` in both UAI.high and LTO.high) caught by `test_no_within_country_collisions`. All resolved here.

| Word | Was in bag | Issue | Replacement | Replacement rationale |
|---|---|---|---|---|
| autonomía | IDV.high | In country denylist (correctly: ambiguous between IDV-high and political-regional-autonomy register) | independencia | Clean IDV-high; political-and-personal independence register; fires twice in piece_history (1810 "guerras de independencia", 1808 "Guerra de la Independencia") |
| planificación | UAI.high | In country denylist (correctly: ambiguous between UAI-high control register and LTO-high investment register) | método | Clean UAI-high; methodical-procedure register; one-lemma, no compound risk |
| espontaneidad | UAI.low | In country denylist (correctly: ambiguous between UAI-low and IND-high) | naturalidad | Clean UAI-low; ease-without-rules register; no IND-high reading |
| informalidad | UAI.low | In country denylist (correctly: ambiguous between UAI-low rule-avoidance and PDI-low flat-structure) | desenfado | Clean UAI-low; casual-comfort register; no PDI reading |
| flexibilidad | UAI.low | In country denylist (correctly: ambiguous between UAI-low and LTO-high adaptability) | versatilidad | Clean UAI-low; capable-of-multiple-modes register; no LTO reading |
| previsión | LTO.high (also UAI.high -- COLLISION) | Cross-bag collision: appears in both UAI.high (anticipation-as-anxiety-control) and LTO.high (forecast-as-investment-horizon) | proyección (LTO.high; previsión stays in UAI.high) | proyección reads forward-projection without the anxiety register; LTO-high register clean |
| fiesta | LTO.low | In country denylist (correctly: ambiguous between LTO-low collective ritual and IND-high celebration) | rito | Clean LTO-low; ceremonial-traditional register; no IND-high reading |
| celebración | LTO.low | In country denylist (correctly: same ambiguity as fiesta) | ceremonia | Clean LTO-low; formal-ritual register; no IND-high reading |

All eight replacements verified clean against:
- The full country denylist (none of `independencia`, `método`, `naturalidad`, `desenfado`, `versatilidad`, `proyección`, `rito`, `ceremonia` appears in `hofstede_bag.yaml denylist:`)
- All other bag entries (no new within-country collision introduced)

Re-derivation after the swaps (manual word-boundary Unicode matching, nominative form, per the standard derivation method):

| Dim | Declared | Derived (pre-fix) | Derived (post-fix) | Gap (post-fix) | Status |
|---|---|---|---|---|---|
| PDI | 57 | 61 | 61 | 4 | EXCELLENT |
| IDV | 51 | 47 | 50 | 1 | EXCELLENT (improved by 3 from `independencia` firing in piece_history) |
| UAI | 86 | 82 | 83 | 3 | EXCELLENT |
| MAS | 42 | 47 | 47 | 5 | EXCELLENT |
| LTO | 48 | 47 | 47 | 1 | EXCELLENT |
| IND | 44 | 40 | 40 | 4 | EXCELLENT |

No content tuning needed; the swap-and-rederive cycle produced 6/6 EXCELLENT without any culture file edits beyond the language-policy anchors added in parallel commits.

---

## Cross-language consistency flags

| Word | This country | Diverges from | Per-country register reasoning |
|---|---|---|---|
| jerarquía | es PDI-high | cognate in de context (same dimension, same polarity) | No divergence; same dimension, same polarity across both cultures |
| familia | es IDV-low | no direct equivalent in nl/de/da/pl bags | Spanish familia carries group-loyalty register at higher cultural intensity than Northern European equivalent; placement justified per-country |
| honor | es LTO-low | no equivalent in loaded culture bags | Honor in Spanish register is present-facing: performed and defended now, not invested for the future; LTO-low placement correct per skill gotcha 1 (tradition is LTO-low) |
| cofradía | es IDV-low | no equivalent in loaded culture bags | Brotherhood/guild structure; deeply Spanish (Semana Santa); in-group belonging at a register no other bag word covers; culturally specific placement justified |

---

## Decision logs

### PDI high

```
Country: spain
Dimension: PDI
Polarity: high
Declared score: 57

Multi-word entries: none
Cross-country root flags: jerarquía cognate with German PDI-high context; same dimension, same polarity; no issue
Root-proximity flags: cargo/mando share command-register; retained for different institutional contexts
  cargo = role/positional authority
  mando = command/operational authority
Register spread: social-cultural 4, institutional 4, everyday 2
Persona-anchor words: cargo (persona_female_isabel, persona_male_alejandro -- institutional authority register)
```

### PDI low

```
Country: spain
Dimension: PDI
Polarity: low
Declared score: 57

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: cercanía/proximidad share closeness-register; retained for different axes
  cercanía = relational warmth, emotional accessibility
  proximidad = structural/physical closeness between ranks
Register spread: relational 4, procedural 3, everyday 3
Persona-anchor words: confianza (persona_female_isabel -- network-trust register)
```

### IDV high

```
Country: spain
Dimension: IDV
Polarity: high
Declared score: 51

Multi-word entries: none
Cross-country root flags: independencia (post 2026-05-14 swap from autonomía) is a Romance cognate (it indipendenza, fr indépendance); same dimension, same polarity expected when sibling Romance bags arrive; no divergence
Root-proximity flags: criterio/decisión share judgment-register; retained
  criterio = standard of judgment
  decisión = act of deciding
Register spread: social-cultural 4, everyday 4, professional 2
Persona-anchor words: iniciativa (persona_male_alejandro -- interpreter-initiative register); trayectoria (persona_female_isabel and persona_male_alejandro -- career-path register); voluntad / criterio / responsabilidad (both personas -- post-v2 tuning additions); independencia (piece_history Yearbook 1808 + 1810 -- national-and-personal independence register)
Score-band note: individuo dropped; at IDV 51 the bag reads individual agency within social context, not individual primacy
Bag-quality 2026-05-14 note: autonomía replaced by independencia (autonomía was in country denylist); the swap improved derived IDV by 3 points (47 -> 50) because independencia has stronger firing in piece_history Yearbook
```

### IDV low

```
Country: spain
Dimension: IDV
Polarity: low
Declared score: 51

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: cofradía/clan/grupo overlap in collective-register; retained for register diversity
  cofradía = culturally specific (Semana Santa, guild), institutionally anchored
  clan = structural collective
  grupo = everyday collective
Register spread: social-cultural 4, everyday 4, institutionally anchored 2
Persona-anchor words: familia (position file -- first loyalty register); red (place_madrid and position -- network register)
```

### UAI high

```
Country: spain
Dimension: UAI
Polarity: high
Declared score: 86

Multi-word entries: none
Cross-country root flags: norma and reglamento share regulatory-register with German UAI-high; same polarity; no divergence
Root-proximity flags: norma/reglamento/orden share regulatory-cluster; retained at maximum 3 after dropping regla and procedimiento
Score-band note: score 86 requires affect-register words alongside structural words
  seguridad and garantía added to carry the emotional need behind the rules
  burocracia retained as lived-experience word at everyday register
Register spread: legal/bureaucratic 3, procedural 2, affect/security 3, everyday 2
Persona-anchor words: burocracia (position_language and position files -- obstacle register); garantía (position -- relationship-as-guarantee register)
Bag-quality 2026-05-14 note: planificación replaced by método (planificación was in country denylist); previsión retained here as anxiety-anticipation register (resolves the cross-bag collision with LTO-high, which now uses proyección)
```

### UAI low

```
Country: spain
Dimension: UAI
Polarity: low
Declared score: 86

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: improvisación/naturalidad share spontaneity-cluster; retained
  improvisación = structural improvisation, method
  naturalidad = behavioral ease-without-rules
apertura register note: confirmed UAI-low in Spanish cultural prose (apertura democrática, apertura al cambio); not generic positivity word
Register spread: behavioral 4, attitudinal 4, everyday 2
Persona-anchor words: none
Bag-quality 2026-05-14 note: three denylisted UAI-low words swapped -- espontaneidad → naturalidad, informalidad → desenfado, flexibilidad → versatilidad. Low count was already appropriate for UAI=86 declared; swaps preserve the low count without firing new content.
```

### MAS high

```
Country: spain
Dimension: MAS
Polarity: high
Declared score: 42

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: logro/resultado/rendimiento share achievement-cluster; retained for register diversity
  logro = achievement as outcome
  resultado = result as deliverable
  rendimiento = performance as process
Register spread: competitive 4, achievement 4, social 2
Persona-anchor words: none (opposing bag; MAS 42 is feminine)
```

### MAS low

```
Country: spain
Dimension: MAS
Polarity: low
Declared score: 42

Multi-word entries: none (calidad-de-vida dropped; hyphenated compound breaks matcher)
Cross-country root flags: none
Root-proximity flags: empatía/compasión/humanidad share care-register; distributed
  empatía = relational care
  compasión = affective care
  humanidad = ethical care
armonía drop note: moved to IDV-low denylist; Spanish armonía scores group harmony (IDV) before cooperation (MAS)
dignidad placement: quality-of-life as human dignity; unambiguous MAS-low; no IDV reading
Register spread: social-cultural 5, relational 3, ethical 2
Persona-anchor words: hospitalidad (position file -- obligación voluntaria register); dignidad (position file)
```

### LTO high

```
Country: spain
Dimension: LTO
Polarity: high
Declared score: 48

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: inversión/ahorro share savings-register; retained
  inversión = active future investment
  ahorro = restraint for future benefit
planificación drop note: within-country collision with UAI-high; planning-as-control belongs to UAI; LTO needs investment vocabulary
formación replacement: development investment over time; unambiguous LTO-high; no UAI reading
Register spread: economic 4, developmental 3, temporal 3
Persona-anchor words: none
Bag-quality 2026-05-14 note: previsión replaced by proyección (resolves the cross-bag collision with UAI-high which retains previsión as anxiety-anticipation register). proyección reads forward-projection without anxiety; clean LTO-high.
```

### LTO low

```
Country: spain
Dimension: LTO
Polarity: low
Declared score: 48

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: orgullo/honor share reputational-register; retained
  honor = historically anchored, performed in present, defended now
  orgullo = present-affective pride, immediate
tradición placement: LTO-low confirmed per skill gotcha 1 (tradition is LTO-low, not LTO-high)
pronto drop note: adverb reading dominates in cultural prose; replaced by memoria
memoria placement: past-anchoring without future investment; tradition-facing; LTO-low register
Register spread: social-cultural 5, historical 3, everyday 2
Persona-anchor words: honor (piece file -- Conquista register); tradición (position file)
Bag-quality 2026-05-14 note: two denylisted LTO-low words swapped -- fiesta → rito, celebración → ceremonia. The ritual register is preserved (both rito and ceremonia carry collective-traditional weight); the denylist hit is cleared.
```

### IND high

```
Country: spain
Dimension: IND
Polarity: high
Declared score: 44

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: disfrute/goce/placer share enjoyment-register; retained for register diversity
  disfrute = active enjoyment, process
  goce = savored pleasure, state
  placer = sensory pleasure
gozo drop note: religious register (gozo espiritual) muddies IND-high signal; juerga replaces at colloquial high-affect register
juerga placement: colloquial, high affect, authentically Spanish IND-high; no other dimension reading
Register spread: sensory 3, social 3, colloquial 2, everyday 2
Persona-anchor words: none
```

### IND low

```
Country: spain
Dimension: IND
Polarity: low
Declared score: 44

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: contención/templanza/mesura share restraint-register; distributed
  contención = active restraint, effort
  templanza = measured moderation, virtue
  mesura = classical restraint, dignity of manner
moderación drop note: redundant with mesura; mesura is more culturally specific; austeridad replaces at economic-moral register
Register spread: social-cultural 4, moral 3, classical 2, economic 1
Persona-anchor words: decoro (position file -- dignidad register); deber (process file -- obligación register)
```

---

## Native-speaker checks needed

- [ ] calidad-de-vida: dropped in favor of dignidad; confirm dignidad carries quality-of-life register in MAS-low context, not only human-rights register
- [ ] cofradía: confirm word is recognized outside Andalucía/Semana Santa as general in-group/brotherhood signal in everyday Spanish
- [ ] honor: confirm contemporary register is active, not primarily archaic/literary; if thin, replace with reputación
- [ ] mesura: confirm active in contemporary Spanish prose, not only classical register; if archaic, replace with contención (already in bag) and find new IND-low word
- [ ] juerga: confirm register is culturally marked IND-high without being too colloquial for cultural file prose
- [ ] apertura: confirm UAI-low reading dominates in cultural prose over generic positivity reading
- [ ] obediencia: confirm PDI-high reading (deference to persons) dominates over UAI-high reading (compliance with rules) in Spanish organizational prose
- [ ] rito vs ceremonia (post 2026-05-14): confirm both are recognized as LTO-low traditional-ritual register in contemporary Spanish, not interchangeable noise; if interchangeable, drop one and find a different LTO-low word
- [ ] desenfado: confirm UAI-low reading (casual ease) is the dominant register in Spanish prose, not specifically literary
- [ ] versatilidad: confirm UAI-low reading (capable-of-multiple-modes) over a broader read; if too broad, replace with adaptabilidad (denylisted? no -- adaptación is the existing bag word but versatilidad is sufficiently distinct)
- [ ] método: confirm UAI-high reading dominates in Spanish cultural prose; if it reads as neutral-procedural without affect, the score-band-86 register may need a more affect-laden replacement (e.g., minuciosidad)
- [ ] independencia: confirm IDV-high reading dominates over the political-territorial reading in Spanish prose (the 2017 Catalan referendum context could activate the political register); if the political reading dominates in given files, the IDV signal may need rebalancing
