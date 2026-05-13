# Hofstede Decisions: Denmark

**Scores:** PDI 18 · IDV 74 · UAI 23 · MAS 16 · LTO 46 · IND 70
**Generated:** 2026-05-10
**Forked from:** none -- fresh bootstrap
**Updated:**
- 2026-05-13: LTO re-baselined 35 → 46 to match Hofstede Insights empirical score; bag unchanged.
- 2026-05-13: Persona-anchor filenames updated for TYPE-as-slot rename (language_dansk → position_language, history_danmark → piece_history).

---

## Drops from previous bag

No previous bag -- fresh bootstrap.

---

## Conflict resolution

| Word | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|
| frihed | IDV-high | Freedom as personal right; dropped from UAI-low candidacy | fleksibel (already present in UAI-low) |
| lighed | PDI-low | Structural equality of standing | selvstændighed (IDV-high) |
| respekt | removed from both | Cross-bag PDI-low/MAS-low; too polysemous to anchor either; added to country denylist | medfølelse (MAS-low), dialog (PDI-low) |
| autonomi | IDV-high | Self-direction is IDV; dropped from IND-high candidacy | nydelse (IND-high) |
| pragmatisk | UAI-low | Flexibility as method | egenart (IDV-high) |
| omsorg | MAS-low | Care for others; dropped from IND-low candidacy | selvkontrol (IND-low) |
| bæredygtighed | removed from both | Too polysemous across MAS-low and LTO-high; added to country denylist | vedholdenhed (LTO-high) |
| disciplin | IND-low | Internal restraint; dropped from UAI-high candidacy | systematik (UAI-high) |
| tradition | LTO-low | Traditional anchoring is correctly LTO-low; dropped from LTO-high candidacy | forpligtelse (LTO-high) |
| ansvarlighed | IND-low | Retained here; removed from PDI-low candidate list | dialog (PDI-low) |
| glæde | IND-high | Pleasure and joy; dropped from MAS-low candidacy | hensyn (MAS-low) |
| spontan | UAI-low | Retained; replaced in IND-high by festlighed (different lemma: spontanitet) | festlighed (IND-high) |
| forpligtelse | LTO-high | Sustained commitment over time; within-country collision detected in IND-low draft | mådehold (IND-low) |
| personlig vurdering | removed | Multi-word; fragile matching; replaced by dømmekraft in IDV-high | dømmekraft (IDV-high) |
| folke- | removed | Prefix not matchable by word-boundary regex; replaced by folkevalgt in PDI-low | folkevalgt (PDI-low) |

---

## Cross-language consistency flags

No cross-language divergence detected. No sibling bags exist in this project yet. Flag for review when Dutch and German bags are produced: autonomi / autonomie / Autonomie may fire across all three cultures in IDV-high. Per-country register reasoning will be required at that point.

---

## Decision logs

### PDI high

```
Country: denmark
Dimension: PDI
Polarity: high
Declared score: 18

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: legal/bureaucratic 3 (protokol, embedsmand, anciennitet), social-cultural 4 (hierarki, autoritet, titel, rang), everyday 3 (overordnet, lydighed, underdanighed)
Persona-anchor words: none (opposing bag)
```

### PDI low

```
Country: denmark
Dimension: PDI
Polarity: low
Declared score: 18

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): direkte and dialog share communication-directness register; different enough in abstraction level to retain both
Register spread: legal/bureaucratic 2 (medbestemmelse, folkevalgt), procedural 1 (konsensus), social-cultural 4 (ligeværd, lighed, jævnbyrdighed, uformel), everyday 3 (dialog, transparens, direkte)
Persona-anchor words: ligeværd (culture_danish_position.md, culture_danish_piece_janteloven.md)
```

### IDV high

```
Country: denmark
Dimension: IDV
Polarity: high
Declared score: 74

Multi-word entries: none. personlig vurdering was a candidate but replaced by dømmekraft (single-word; no fragile multi-word matching risk).
Cross-country root flags: autonomi -- may appear in NL and DE bags when produced; flag for cross-country review at that point
Root-proximity flags (same country): selvbestemmelse and selvstændighed share selv- root; retained because they signal meaningfully different aspects (constitutional right vs. behavioral capacity)
Register spread: legal 2 (meningsfrihed, ytringsfrihed), social-cultural 4 (autonomi, selvbestemmelse, selvstændighed, egenart), everyday 4 (frihed, initiativ, integritet, dømmekraft)
Persona-anchor words: autonomi (culture_danish_position.md, culture_danish_position_language.md, persona files), selvbestemmelse (culture_danish_position_language.md, culture_danish_place_copenhagen.md)

NOTE -- autonomi appears in no other bag for this country. IDV-high is its only valid placement.
```

### IDV low

```
Country: denmark
Dimension: IDV
Polarity: low
Declared score: 74

Multi-word entries: vi-følelse -- compound; no single-word equivalent without losing the "we" component. Retained.
Cross-country root flags: solidaritet -- appears as Polish Solidarnosc piece title; different register. Danish "solidaritet" is an abstract political noun; not the same cultural load as the Polish proper-noun movement. No collision.
Root-proximity flags (same country): fællesskab and fællesånd share fælles- root. Retained: fællesskab = community as social unit; fællesånd = communal spirit as motivating force. Sufficient conceptual separation.
Register spread: social-cultural 6 (fællesskab, samhørighed, vi-følelse, tilhørsforhold, harmoni, fællesånd), everyday 4 (loyalitet, gruppeidentitet, solidaritet, sammenhold)
Persona-anchor words: none (opposing bag)
```

### UAI high

```
Country: denmark
Dimension: UAI
Polarity: high
Declared score: 23

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: legal 2 (regulering, standardisering), procedural 4 (procedure, systematik, planlægning, forudsigelighed), social-cultural 2 (orden, struktur), everyday 2 (regler, præcision)
Persona-anchor words: none (opposing bag)
```

### UAI low

```
Country: denmark
Dimension: UAI
Polarity: low
Declared score: 23

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): spontan (UAI-low) and spontanitet (IND-high) -- different lemma forms, different dimensions. Root-proximity pair: spontan = methodological openness to unplanned situations (UAI-low); spontanitet = pleasurable spontaneity (IND-high). Matcher fires on different strings. Documented in both UAI-low and IND-high decision logs per Skill Rule 11.
Register spread: social-cultural 3 (uhøjtidelighed, tolerance, afslappet), procedural 3 (fleksibel, pragmatisk, tilpasningsevne), everyday 4 (improvisere, spontan, åbenhed, eksperimentere)
Persona-anchor words: fleksibel (culture_danish_position_language.md), pragmatisk (culture_danish_position_language.md)
```

### MAS high

```
Country: denmark
Dimension: MAS
Polarity: high
Declared score: 16

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: social-cultural 3 (konkurrence, selvhævdelse, dominans), everyday 5 (ambition, sejr, karriere, stræben, succes), procedural 2 (præstation, resultat)
Persona-anchor words: none (opposing bag)
```

### MAS low

```
Country: denmark
Dimension: MAS
Polarity: low
Declared score: 16

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): velvære (MAS-low) and velværd (IND-high) -- near-synonyms in adjacent bags. Critical distinction: velvære = relational wellbeing and care for others; velværd = personal gratification and quality of life. Native-speaker check required before approving.
Register spread: social-cultural 5 (omsorg, nærvær, medfølelse, hensyn, mægling), institutional 1 (ligestilling), everyday 4 (samarbejde, ydmyghed, balance, velvære)
Persona-anchor words: omsorg (culture_danish_process_hygge.md), nærvær (culture_danish_process_hygge.md)
```

### LTO high

```
Country: denmark
Dimension: LTO
Polarity: high
Declared score: 46

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): forpligtelse (LTO-high) -- same word was candidate for IND-low but replaced there with mådehold. No collision in final bags.
Register spread: financial 2 (investering, opsparing), temporal 3 (langsigtet, fremtid, generationer), behavioral 3 (vedholdenhed, tålmodighed, kontinuitet), strategic 2 (forpligtelse, strategi)
Persona-anchor words: forpligtelse (culture_danish_piece_history.md), vedholdenhed (culture_danish_piece_history.md), langsigtet (culture_danish_piece_history.md, culture_danish_position.md), generationer (culture_danish_piece_history.md, culture_danish_piece_janteloven.md yearbook), tålmodighed (culture_danish_position.md), arv (culture_danish_position.md)
```

### LTO low

```
Country: denmark
Dimension: LTO
Polarity: low
Declared score: 46

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): tradition, sædvane, skik -- all three in same bag, same concept cluster. Cross-register sibling scan applied: tradition = the abstract value; sædvane = established custom practice; skik = social custom and norm. Sufficient register separation to retain all three. LTO-low bag; traditional anchoring is the correct signal; three words at different abstraction levels is appropriate.
Register spread: abstract 3 (tradition, nutid, fortid), everyday 5 (sædvane, arv, aktuel, erfaring, skik), behavioral 2 (umiddelbar, øjeblikkelig)
Persona-anchor words: tradition (culture_danish_piece_janteloven.md), sædvane (culture_danish_place_copenhagen.md), nutid (culture_danish_piece_history.md), erfaring (culture_danish_piece_history.md), umiddelbar (culture_danish_process_hygge.md), øjeblikkelig (culture_danish_process_hygge.md)

NOTE -- tradition appears in the country denylist as unsafe for LTO-high. Its placement here in LTO-low is correct per the polarity reference table.
NOTE -- LTO re-baselined from 35 to 46 (2026-05-13) to match Hofstede Insights' empirical Danish LTO score. Bag composition unchanged; v2 content tuning (history file + hygge present-moment markers) calibrates derived score to match new declared.
```

### IND high

```
Country: denmark
Dimension: IND
Polarity: high
Declared score: 70

Multi-word entries: none
Cross-country root flags: hygge -- institutionally anchored proper noun turned common cultural term. Culturally load-bearing. Retained. Note: may appear in NL or DE files by cultural borrowing; matcher fires on Danish content only, so no cross-country collision risk.
Root-proximity flags (same country): spontan (UAI-low) / spontanitet (IND-high) -- different lemmas; different dimensions. Registered.
Register spread: social-cultural 3 (hygge, festlighed, fryd), everyday 5 (nydelse, glæde, tilfredsstillelse, fornøjelse, velværd), behavioral 2 (lyst, spontanitet)
Persona-anchor words: nydelse (culture_danish_process_hygge.md), fryd (culture_danish_process_hygge.md), hygge (process file title and body)
```

### IND low

```
Country: denmark
Dimension: IND
Polarity: low
Declared score: 70

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: behavioral 5 (selvkontrol, tilbageholdenhed, besindighed, beherskelse, afdæmpet), ethical 3 (pligt, ansvarlighed, nøjsomhed), everyday 2 (disciplin, mådehold)
Persona-anchor words: selvkontrol (culture_danish_process_hygge.md)

NOTE -- forpligtelse was a candidate here but was detected as a within-country collision with LTO-high. Replaced by mådehold. Forpligtelse placed in LTO-high.
NOTE -- disciplin appears in the country denylist as unsafe for UAI-high. Its placement here in IND-low is its only valid placement in this country's bags.
NOTE -- ansvarlighed was removed from PDI-low candidacy and resolved to IND-low. No collision.
```

---

## Native-speaker checks needed

- [ ] velvære (MAS-low) vs. velværd (IND-high) -- near-synonyms placed in different bags; confirm register distinction holds in contemporary Danish cultural prose; if interchangeable, drop velværd to denylist and find IND-high replacement
- [ ] vi-følelse (IDV-low) -- compound; confirm currency in contemporary Danish versus samhørighed for the same semantic slot
- [ ] uhøjtidelighed (UAI-low) -- confirm this reads as everyday UAI-low marker rather than ironic or literary usage
- [ ] øjeblikkelig (LTO-low) -- confirm this is read as temporal immediacy and not as instantaneous in a neutral or technical sense that would produce false positives
- [ ] forpligtelse (LTO-high) -- confirm it reads as sustained long-term commitment rather than immediate duty in Danish cultural prose; if the duty reading dominates, replace with udholdenhed
