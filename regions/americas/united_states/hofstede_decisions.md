# Hofstede Decisions: United States

**Scores:** PDI 40 - IDV 91 - UAI 46 - MAS 62 - LTO 26 - IND 68
**Generated:** 2026-05-20
**Forked from:** none - fresh bootstrap

---

## Drops from previous bag

No previous bag - fresh bootstrap.

---

## Conflict resolution

| Word | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|
| protocol | PDI-high | Protocol in American usage signals chain of command (military, diplomatic, congressional), not rule-as-system | UAI-high gets statute instead |
| federal | UAI-high | The federal regulatory frame is the institutional signal of US ambiguity reduction; not a hierarchy signal | PDI-high gets seniority instead |
| pitch | MAS-high | The pitch is the assertive competitive act in American business and politics, not the deal itself | IDV-high gets initiative |
| initiative | IDV-high | Personal initiative is self-direction; the assertive performance frame is MAS | MAS-high gets drive |
| freedom | IND-high | Freedom in the everyday register is gratification (long weekend, freedom Friday) for the IND bag | IDV-high gets liberty as the political-constitutional register |
| liberty | IDV-high | Liberty is the founding-document personal liberty register, self-direction not gratification | IND-high gets freedom in the casual sense |
| duty | IND-low | Duty as restraint is the IND signal in American Protestant-work-ethic residual; not a group obligation in the IDV sense | IDV-low gets community |
| restraint | IND-low | Restraint is the canonical IND-low anchor | MAS-low gets modesty instead |
| modesty | MAS-low | Modesty in American usage is the femininity-pole nurturing register, distinct from self-restraint | IND-low gets reserved |

---

## Cross-language consistency flags

Nigeria English bag is the only other English-language reference; checked for vocabulary overlap. Where Nigeria uses *self-rule, self-reliant, self-made,* the US bag retains *self-reliance* (the canonical Emersonian term) and adds *individual, autonomy, private, reinvention* for the higher US IDV register. Where Nigeria uses *hustle* for MAS-high, the US bag drops *hustle* to the denylist (carries Nigerian-specific connotation; "ambition / drive / pitch" are the US equivalents). Where Nigeria uses *ambiguity, risk, adaptive,* the US bag retains *ambiguity, risk, adaptable* (synonym near-match). Where Nigeria uses *long-term, perseverance, investment,* the US bag retains all three with the same meaning since they are LTO-anchor canonical terms.

---

## Decision logs

### PDI high

```
Country: united_states
Dimension: PDI
Polarity: high
Declared score: 40

Multi-word entries: none
Cross-country root flags: title, status, rank shared with Nigeria PDI-high (canonical terms; expected)
Root-proximity flags (same country): rank / status share status-position register - both retained; rank is the position in the order, status is the position in the social field
Register spread: legal/bureaucratic 3 (title, seniority, protocol), procedural 1 (supervisor), social-cultural 4 (status, rank, hierarchy, sir), everyday 2 (chairman, senator)
Persona-anchor words: Dale - none fires (HVAC tech does not run on title/protocol); Megan - none fires (ED nurse runs on first-name unit)
Note: senator chosen as American-specific because the Senate is the highest single elected office most Americans use the title for in daily speech. Sir flagged for native-speaker review - retained as Southern register and military register, common signal.
```

### PDI low

```
Country: united_states
Dimension: PDI
Polarity: low
Declared score: 40

Multi-word entries: first-name (hyphenated; the canonical American flat-hierarchy signal; no single-word equivalent in English captures it)
Cross-country root flags: peer, accessible, egalitarian shared with English-language register; standard
Root-proximity flags (same country): accessible / approachable both name openness - retained as distinct registers; accessible is institutional (you can reach them), approachable is interpersonal (they smile back); everyone / anyone share universal-inclusion register - both retained because everyone is the affirmative inclusion (everyone is invited) and anyone is the contingent inclusion (anyone can pitch)
Register spread: legal/bureaucratic 1 (egalitarian), procedural 1 (openness), social-cultural 5 (first-name, peer, accessible, approachable, meritocracy), everyday 3 (casual, everyone, anyone)
Persona-anchor words: Dale - first-name basis fires; Megan - first-name basis fires
Drops: direct (global denylist - hard rule); flat (global denylist - hard rule); informal (within-country collision with UAI.low - retained on UAI.low since informal-register is canonical UAI-low signal). Replacements: casual, everyone, anyone.
```

### IDV high

```
Country: united_states
Dimension: IDV
Polarity: high
Declared score: 91

Multi-word entries: self-reliance (hyphenated; the canonical Emersonian term; no single-word equivalent), self-made (hyphenated; canonical American self-made-man / self-made-woman register)
Cross-country root flags: individual, personal, independent, autonomy shared with English canonical IDV-high - standard
Root-proximity flags (same country): self-reliance / self-made / self share self-root - three retained because each anchors a distinct facet (reliance is the verb of dependency-refusal, made is the verb of self-construction, self is the noun)
Register spread: legal/bureaucratic 1 (liberty), procedural 1 (initiative), social-cultural 6 (individual, self-reliance, personal, independent, autonomy, reinvention), everyday 2 (private, self)
Persona-anchor words: Dale - self-reliance, initiative fire (his one-truck business is the canonical case); Megan - personal, autonomy fire (her three-twelves shift schedule is structured around personal autonomy from married life)
```

### IDV low

```
Country: united_states
Dimension: IDV
Polarity: low
Declared score: 91

Multi-word entries: we-feeling (hyphenated; closed compound for collective sentiment; no single-word equivalent)
Cross-country root flags: community, collective, solidarity standard English IDV-low
Root-proximity flags (same country): communal / community share the same root - both retained because communal is the adjective register (communal table, communal effort) and community is the noun (the community decides)
Register spread: legal/bureaucratic 0, procedural 0, social-cultural 8 (community, collective, solidarity, kinship, belonging, togetherness, communal, tribe), everyday 2 (we-feeling, clan)
Persona-anchor words: none fires in personas (both Dale and Megan are operating in low-IDV-low register, as expected for a high-IDV country)
Note: tribe flagged as politically loaded in 2020s US discourse - retained because the IDV-low register is exactly what it signals in the bag context (tight in-group identity); decisions about the cultural prose's use of the word are independent of the bag.
```

### UAI high

```
Country: united_states
Dimension: UAI
Polarity: high
Declared score: 46

Multi-word entries: none
Cross-country root flags: regulation, procedure, standard, compliance shared with English UAI-high - standard
Root-proximity flags (same country): regulation / statute - retained because regulation is the executive rule, statute is the legislative rule, different institutional referents
Register spread: legal/bureaucratic 5 (regulation, procedure, compliance, statute, federal), procedural 3 (standard, inspection, documented), social-cultural 1 (certified), everyday 1 (precise)
Persona-anchor words: Dale (certification on his HVAC license fires); Megan (procedure in hospital protocols fires); History file (federal, statute fire); Interstate file (federal, procedure, standard fire)
Note: federal is unusual for UAI-high (typically PDI signal); in American discourse federal-as-uniform-standard is the regulatory ambiguity-reduction signal, not a hierarchy signal. Decision documented above. Retained.
```

### UAI low

```
Country: united_states
Dimension: UAI
Polarity: low
Declared score: 46

Multi-word entries: none
Cross-country root flags: flexible, tolerance, ambiguity, risk, informal shared with English UAI-low - standard
Root-proximity flags (same country): flexible / adaptable share flexibility-register - both retained because flexible is the static attribute and adaptable is the dynamic attribute
Register spread: legal/bureaucratic 1 (tolerance), procedural 2 (flexible, adaptable), social-cultural 4 (ambiguity, risk, workaround, experiment), everyday 3 (improvise, informal, loose)
Persona-anchor words: Dale (workaround fires on the patch-vs-replacement decision); Megan (informal, flexible fire in the unit running on improvisation between protocols)
```

### MAS high

```
Country: united_states
Dimension: MAS
Polarity: high
Declared score: 62

Multi-word entries: none
Cross-country root flags: winning, competitive, ambition, achievement, success shared with English MAS-high - standard
Root-proximity flags (same country): winning / pitch / top distinct registers - winning is the outcome, pitch is the act, top is the position
Register spread: legal/bureaucratic 0, procedural 1 (performance), social-cultural 5 (winning, competitive, ambition, achievement, success), everyday 4 (top, aggressive, dominant, pitch)
Persona-anchor words: Position file (pitch, winning, ambition, top fire); Process file (pitch, competitive, achievement, ambition, success fire); Pitching is the dimension-anchor process
Note: pitch is in MAS-high rather than UAI-low (which could plausibly hold it as improvisation) because in American business culture the pitch is the canonical assertive act of personal success-pursuit, not the canonical risk-tolerance act.
Drops: drive (global denylist). Replacement: top.
```

### MAS low

```
Country: united_states
Dimension: MAS
Polarity: low
Declared score: 62

Multi-word entries: none
Cross-country root flags: care, cooperation, modesty, nurture, compassion, harmony shared with English MAS-low - standard
Root-proximity flags (same country): none
Register spread: legal/bureaucratic 0, procedural 1 (cooperation), social-cultural 7 (care, modesty, nurture, compassion, harmony, empathy, reconciliation), everyday 2 (gentle, kindness)
Persona-anchor words: Megan (care fires - the ED nurse is care-coded); Position file (modesty fires - quiet competence section)
Note: modesty is typed as MAS-low not IND-low to preserve the femininity-pole register; restraint and reserved cover the IND-low self-control register.
```

### LTO high

```
Country: united_states
Dimension: LTO
Polarity: high
Declared score: 26

Multi-word entries: long-term (hyphenated; the canonical English LTO-high term; no single-word equivalent)
Cross-country root flags: long-term, perseverance, investment, patience, thrift, future shared with English LTO-high - standard
Root-proximity flags (same country): foresight / accumulated / prudence - distinct registers retained
Register spread: legal/bureaucratic 1 (investment), procedural 2 (long-term, sustained), social-cultural 5 (perseverance, patience, thrift, accumulated, foresight), everyday 2 (legacy, prudence)
Persona-anchor words: none fires significantly (US is low-LTO, expected behavior)
Note: LTO-high words appear sparingly in US culture prose by design; the country is on the present-and-near-term end and the bag reflects that.
```

### LTO low

```
Country: united_states
Dimension: LTO
Polarity: low
Declared score: 26

Multi-word entries: none
Cross-country root flags: immediate, present, instant, quick, fast, today shared with English LTO-low - standard
Root-proximity flags (same country): immediate / instant / current share immediacy register - three retained for register distinction (immediate is the formal register, instant is the demand register, current is the present-tense state)
Register spread: legal/bureaucratic 0, procedural 1 (immediate), social-cultural 3 (overnight, momentary, daily), everyday 6 (current, present, instant, quick, fast, today)
Persona-anchor words: Dale (daily route fires); Megan (immediate, fast, current fire on the ED shift); Process file (immediate fires)
Drops: now (global denylist - hard rule, deictic). Replacement: current.
```

### IND high

```
Country: united_states
Dimension: IND
Polarity: high
Declared score: 68

Multi-word entries: none
Cross-country root flags: enjoyment, leisure, fun, pleasure, vacation, optimism, happiness shared with English IND-high - standard
Root-proximity flags (same country): freedom / vacation distinct registers (freedom is the constitutional-flavored gratification register; vacation is the schedule-coded gratification register)
Register spread: legal/bureaucratic 0, procedural 0, social-cultural 6 (enjoyment, leisure, indulgence, optimism, freedom, happiness), everyday 4 (fun, pleasure, vacation, weekend)
Persona-anchor words: Position file (indulgence, freedom, optimism, happiness fire); History file (vacation fires on July 4 entry); Place file (no fires); Personas (none fires - both personas are working-register)
```

### IND low

```
Country: united_states
Dimension: IND
Polarity: low
Declared score: 68

Multi-word entries: self-control (hyphenated; the canonical English IND-low compound)
Cross-country root flags: restraint, duty, discipline, sober, moderation, sacrifice, austerity, frugal shared with English IND-low - standard
Root-proximity flags (same country): restraint / reserved / self-control share self-restraint register - three retained for distinct registers (restraint is the act, reserved is the disposition, self-control is the practice)
Register spread: legal/bureaucratic 0, procedural 1 (self-control), social-cultural 5 (restraint, duty, sacrifice, austerity, moderation), everyday 4 (discipline, sober, reserved, frugal)
Persona-anchor words: Position file (duty, restraint, reserved fire light); Personas (none fires significantly)
Note: IND-low fires sparingly in US prose by design; the country is on the indulgent end and the bag reflects that.
```

---

## Native-speaker checks needed

- [ ] sir - retained as Southern and military register; verify it does not read as obsolete in northern/coastal American usage
- [ ] hustle - placed on denylist (Nigerian-specific connotation); verify the US bag's *drive, ambition, pitch* fully cover the register
- [ ] tribe - flagged as politically loaded in contemporary US discourse; bag use is for the IDV-low signal only, prose use is independent
- [ ] federal - unusual placement in UAI-high (not PDI-high); verify the institutional-ambiguity-reduction reading holds for native speakers
- [ ] pitch - verify the bag use (MAS-high) is the dominant register and not blocked by sports-only association (baseball pitcher) in casual American usage
