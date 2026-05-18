# hofstede_decisions.md
## Singapore

**Scores:** PDI 74 · IDV 20 · UAI 8 · MAS 48 · LTO 72 · IND 46
**Language:** en
**Region:** asia
**Generated:** 2026-05-17
**Status:** draft
**Source:** Hofstede Insights / The Culture Factor Group. Scores confirmed 2026-05-17. IDV and LTO updated in the October 2023 large-scale replication study. IND 46 predates the 2023 update and was not revised by it.

---

## Drops from Previous Bag

No previous bag -- fresh bootstrap.

---

## Conflict Resolution Table

| Word | Bags in conflict | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|---|
| consensus | PDI_low, IDV_low, MAS_low | IDV_low | Collective decision-making is the core collectivist signal in Singapore's Confucian context | PDI_low: accountable; MAS_low: cooperation already present. consensus added to denylist after resolution to prevent re-entry. |
| protocol | PDI_high, UAI_high | PDI_high | In Singapore, protocol signals rank-formality more than anxiety-driven rule-following | UAI_high: procedure |
| compliance | PDI_high, UAI_high | UAI_high | Singapore's "Fine city" paradigm: compliance with rules is the UAI signal, not the PDI signal | PDI_high: obedience |
| formal | PDI_high, UAI_high | PDI_high | Formality in Singapore ties to title and hierarchy, not uncertainty-anxiety | UAI_high: standardized. formal added to denylist after resolution. |
| harmony | IDV_low, MAS_low | IDV_low | Confucian harmony is fundamentally a collectivist/in-group value in Singapore | MAS_low: balance. harmony added to denylist after resolution. |
| discipline | LTO_high, IND_low | LTO_high (then dropped) | Perseverance-discipline is Singapore's LTO signal. After review, dropped from LTO_high due to denylist conflict with cross-bag risk; replaced by frugality. discipline added to denylist. | IND_low: temperance |
| spontaneous | UAI_low, IND_high | UAI_low (then dropped) | Spontaneity signals ambiguity-tolerance in UAI context. Dropped after review: same-dimension polarity ambiguity across registers. Added to denylist. | IND_high: expressive |
| deference | PDI_high, IND_low | PDI_high (then dropped) | Deference to superiors is PDI-high. Dropped: same-dimension ambiguity (can read PDI-low as "appropriate deference to merit"). Added to denylist. | IND_low: moderation already present |
| merit | PDI_low, MAS_high | MAS_high | Meritocracy in Singapore is achievement-ideology, not flat-structure ideology | PDI_low: accessible. merit added to denylist. |
| pragmatic | UAI_low | Dropped | LKY governance register makes "pragmatic" primarily an LTO-high signal in Singapore English, not UAI-low. Same-dimension opposite-polarity risk per skill rule 9. Added to denylist. | UAI_low: experimental |
| sobriety | IND_low | Dropped | Standard English "sobriety" primarily means not being drunk. Singapore IND-low mapping to composed public conduct is dialect-specific without corpus evidence. Per skill rule 10. Added to denylist. | IND_low: temperance |
| self-expression | IDV_high | Dropped | Two self- compounds in one bag violates hyphenated-compound limit (max one). self-reliance retained as the stronger cultural signal. Added to denylist. | IDV_high: detachment |
| adaptable | UAI_low | Dropped | Root-proximity collision with adapt in same bag (adaptable/adapt share root). Added to denylist. | UAI_low: experimental |
| consensus | IDV_low | Dropped from IDV_low after second-pass review | consensus replaced by interdependence to keep denylist contract clean. See denylist entry. | IDV_low: interdependence |

---

## Cross-Language Consistency Flags

- **hierarchy** (SGP, PDI_high): consistent with PDI_high direction across all high-PDI cultures in project. No divergence.
- **loyalty** (SGP, IDV_low): consistent with IDV_low direction in Nigerian and Mexican bags (obligation, circle vocabulary). No divergence.
- **perseverance** (SGP, LTO_high): consistent with LTO_high direction. Polish bag uses wytrwalosc (perseverance) for the same dimension. Directional consistency confirmed.
- **tradition** (SGP, LTO_low): consistent with skill rule: tradition is LTO_low, not LTO_high. Confirmed across project.
- **restraint** (SGP, IND_low): no cross-country collision detected.
- **pragmatic** (SGP): dropped from UAI_low after review. Singapore-specific LKY governance register creates LTO_high overlap. Not placed in any bag. Added to denylist.

No blocking divergences detected.

---

## Decision Logs

---

### Country: Singapore | PDI_high | Score: 74

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: rank shares concept-family with advancement (MAS_high) -- flagged; content context disambiguates
Register spread: social-cultural 3 (hierarchy, seniority, respect), everyday 3 (rank, title, superior), legal/bureaucratic 2 (authority, command), relational 2 (obedience, patron)
Persona-anchor words: none -- no persona files exist yet
Notes: patron flagged for native-speaker check (Section 8, item 3). Singapore English register of patron may skew commercial or religious rather than hierarchical power-broker. If so, replace with deference -- wait, deference is on denylist. Replace with allegiance.

---

### Country: Singapore | PDI_low | Score: 74 (opposing bag)

Multi-word entries: bottom-up -- one hyphenated compound; no single-word equivalent captures upward-initiative meaning. Retained.
Cross-country root flags: none
Root-proximity flags: none
Register spread: organizational 4 (flat, horizontal, collaborative, bottom-up), social-cultural 3 (equal, peer, informal), procedural 2 (accessible, accountable), everyday 1 (voice)
Persona-anchor words: none

---

### Country: Singapore | IDV_low | Score: 20

Multi-word entries: in-group -- one hyphenated compound; no single-word equivalent captures in-group/out-group structural distinction. Retained.
Cross-country root flags: loyalty -- Nigerian bag uses same word for IDV_low. Consistent direction, no conflict.
Root-proximity flags: obligation shares concept-territory with duty (IND_low) -- flagged. Both retained: obligation is the collectivist binding mechanism (IDV signal); duty is individual self-restraint (IND signal). Context distinguishes.
Register spread: social-cultural 5 (loyalty, kinship, community, belonging, solidarity), structural 2 (in-group, interdependence), relational 2 (obligation, collective), everyday 1 (filial)
Persona-anchor words: none
Notes: filial flagged for native-speaker check (Section 8, item 5). If content files use only the compound "filial piety," single-word match will miss. Monitor.
Notes: consensus dropped from this bag after second pass (denylist contract). Replaced by interdependence. interdependence signals mutual dependence within the group -- IDV_low polarity confirmed.

---

### Country: Singapore | IDV_high | Score: 20 (opposing bag)

Multi-word entries: self-reliance -- one self- compound retained after self-expression dropped. Limit satisfied.
Cross-country root flags: none
Root-proximity flags: autonomy / independence share conceptual territory -- both IDV_high, same bag. Retained: autonomy is structural (freedom from institutional constraint), independence is relational (freedom from group claim). Distinct enough.
Register spread: philosophical 3 (autonomy, independence, freedom), social-cultural 3 (individual, personal, privacy), behavioral 2 (assertion, initiative), psychological 2 (self-reliance, detachment)
Persona-anchor words: none
Notes: opposing bag at score 20 uses generic English IDV_high vocabulary. This is correct for an opposing bag at this extreme score band. Content files will naturally carry IDV_low vocabulary; the opposing bag words will appear only in contrast or in shadow sections.

---

### Country: Singapore | UAI_low | Score: 8

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: flexible / agile share register -- both UAI_low, same bag. Retained: flexible is general behavioral vocabulary, agile is contemporary organizational vocabulary. Distinct registers.
Register spread: organizational 3 (agile, flexible, experimental), behavioral 3 (improvise, opportunistic, adapt), conceptual 2 (ambiguity, tolerance), everyday 2 (risk, fluid)
Persona-anchor words: none
Notes: pragmatic dropped. LKY governance register in Singapore English maps pragmatic primarily to LTO_high (long-term instrumental thinking), not UAI_low (ambiguity tolerance). Same-dimension opposite-polarity risk per skill rule 9. Replaced by experimental.
Notes: adapt and adaptable root collision resolved: adaptable dropped (denylist), adapt retained.

---

### Country: Singapore | UAI_high | Score: 8 (opposing bag)

Multi-word entries: none
Cross-country root flags: rules -- consistent UAI_high across all high-UAI cultures in project
Root-proximity flags: structure / systematic share root concept -- both UAI_high, same bag. Retained: structure is environmental, systematic is behavioral.
Register spread: legal/bureaucratic 3 (rules, regulation, compliance), procedural 3 (procedure, standardized, systematic), organizational 2 (structure, controlled), psychological 2 (certainty, predictable)
Persona-anchor words: none

---

### Country: Singapore | MAS_low | Score: 48

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: care / compassion / nurture share concept cluster -- all MAS_low, same bag. Retained with register-distinction reasoning: care is systemic (policy/civic), compassion is relational, nurture is developmental.
Register spread: policy/civic 3 (welfare, wellbeing, care), relational 4 (relationship, compassion, nurture, cooperation), personal 2 (modesty, balance), organizational 1 (quality)
Persona-anchor words: none

---

### Country: Singapore | MAS_high | Score: 48 (opposing bag)

Multi-word entries: none
Cross-country root flags: achievement, competition, success -- all consistent MAS_high across project bags
Root-proximity flags: status / advancement share career-register -- both MAS_high, same bag. Retained: status is positional (social recognition), advancement is directional (upward movement).
Register spread: educational 2 (achievement, performance), competitive 3 (competition, winning, ambition), professional 3 (success, advancement, excellence), behavioral 2 (assertive, status)
Persona-anchor words: none
Notes: kiasu culture anchors achievement, winning, competition, status directly. These words should appear organically in Singapore culture content without forcing.

---

### Country: Singapore | LTO_high | Score: 72

Multi-word entries: none
Cross-country root flags: perseverance -- consistent with Polish LTO_high direction (wytrwalosc)
Root-proximity flags: planning / foresight share forward-orientation -- both LTO_high, same bag. Retained: planning is operational, foresight is strategic.
Register spread: civic/policy 3 (planning, sustainability, prudence), behavioral 3 (perseverance, patience, frugality), economic 2 (investment, thrift), conceptual 2 (continuity, foresight)
Persona-anchor words: none
Notes: discipline dropped from this bag after conflict resolution (LTO_high / IND_low collision) and added to denylist. Replaced by frugality. Frugality signals LTO_high through Confucian and CPF-savings register in Singapore.

---

### Country: Singapore | LTO_low | Score: 72 (opposing bag)

Multi-word entries: none
Cross-country root flags: tradition -- per skill rule: tradition is LTO_low, not LTO_high. Confirmed.
Root-proximity flags: convention / established / custom / norm share tradition-register -- four words in same bag. Flagged. Decision: retain all four. They signal distinct aspects: convention is social practice, established is institutional, custom is behavioral, norm is descriptive standard. Register diversity acceptable at this score band for an opposing bag.
Register spread: cultural 4 (tradition, custom, ceremonial, heritage), behavioral 3 (norm, convention, established), temporal 2 (immediate, present), evaluative 1 (quick)
Persona-anchor words: none

---

### Country: Singapore | IND_low | Score: 46

Multi-word entries: self-control -- one self- compound; no single-word equivalent. Retained.
Cross-country root flags: none
Root-proximity flags: restraint / moderation / temperance share temperance-cluster -- three words in same bag. Flagged. Decision: retain. Restraint is the governing concept; moderation is behavioral expression; temperance is register-specific (Confucian/civic self-governance). Distinct enough with register-distinction reasoning.
Root-proximity flags: obligation shares concept-territory with obligation in IDV_low. Both bags carry obligation. Flagged: same word in two bags. COLLISION. Final state: obligation replaced by gravity. Reason: obligation appeared in both IDV_low and IND_low (duplicate across bags). gravity signals composed public self-presentation; not on denylist; not in any other bag.
Register spread: civic/public 3 (restraint, decorum, propriety), behavioral 3 (self-control, measured, composed), conceptual 2 (duty, gravity), personal 2 (moderation, temperance)
Persona-anchor words: none
Notes: Final state is stable: gravity remains in IND_low after resolving the IDV_low collision and denylist constraints.

---

### Country: Singapore | IND_high | Score: 46 (opposing bag)

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: enjoyment / pleasure / fun / leisure share hedonic cluster -- four words in same bag. Flagged. Decision: retain. At score 46 the opposing bag needs clear polarity coverage. Register-distinct: enjoyment is general, pleasure is sensory, fun is social/casual, leisure is temporal.
Register spread: lifestyle 4 (enjoyment, leisure, pleasure, fun), celebratory 3 (festive, celebration, expressive), psychological 2 (gratification, desire), commercial 1 (entertainment)
Persona-anchor words: none

---

## Native-Speaker Check Items

1. **patron (PDI_high):** Does "patron" in Singapore English primarily read as hierarchical power-broker or as commercial/religious patron? If the latter dominates, replace with allegiance.

2. **filial (IDV_low):** Does Singapore cultural prose use "filial" as standalone adjective, or always in the compound "filial piety"? If always compound, single-word match will miss. Consider swapping to piety if content authors confirm they will use "filial piety" throughout.

3. **experimental (UAI_low):** Singapore's governance discourse may not use "experimental" as a cultural self-descriptor. Does it appear naturally in Singapore cultural prose (startup culture, regulatory sandboxes) or does it read as imposed vocabulary?

4. **frugality (LTO_high):** "Frugality" and "thrift" are near-synonyms in the same bag. Both are LTO_high. Verify that both will appear distinctly in content files. If content files only use one, drop the other.

5. **gravity (IND_low):** "Gravity" in the sense of seriousness of manner is a somewhat formal register. Verify it appears naturally in Singapore cultural prose describing composed public conduct. Alternative: composure (verify no root collision -- composed is in the same bag; composure and composed share root). If gravity reads as forced, use reserve instead.

6. **four near-synonyms in LTO_low (tradition, convention, heritage, established):** Verify all four appear as natural vocabulary in Singapore content files and are not redundant with each other.

---

*hofstede_decisions.md -- Singapore*
*KAI HACKS AI*
*2026-05-17*
