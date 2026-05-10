# Hofstede Decisions: Germany

**Scores:** PDI 35 · IDV 67 · UAI 65 · MAS 66 · LTO 83 · IND 40
**Generated:** 2026-05-10
**Forked from:** none -- fresh bootstrap

---

## Drops from previous bag

No previous bag -- fresh bootstrap.

---

## Conflict resolution

| Word | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|
| eigenverantwortung | IDV-high | Personal responsibility is self-direction, not flat-structure signaling | PDI-low gets mitsprache |
| leistung | MAS-high | Achievement/performance is the MAS signal; IDV is about self-direction not output | IDV-high gets eigenleistung |
| solidarität | IDV-low | Solidarity names in-group loyalty more precisely than care/cooperation | MAS-low gets rücksichtnahme |
| fürsorge | MAS-low | Care for others is femininity signal; IDV-low is about group belonging | IDV-low: fürsorge removed, replaced by kollektivgeist |
| pragmatismus | LTO-high | German pragmatismus is forward-looking adaptation, not ambiguity tolerance | UAI-low gets anpassungsfähigkeit |
| spontaneität | UAI-low | Spontaneity signals ambiguity tolerance more directly than short-termism | LTO-low gets sofortigkeit |
| pflicht | IND-low | Duty as restraint is the IND signal; IDV is self-direction not obligation | IDV-high gets selbstständigkeit |
| bescheidenheit | IND-low | Modesty as self-restraint fits IND-low; cannot serve MAS-low simultaneously | MAS-low gets gemeinwohl; bescheidenheit to denylist |
| freiheit | IDV-high | Freedom as self-determination is IDV; IND-high gratification-freedom is secondary register | IND-high gets unbeschwertheit |
| kontinuität | UAI-high | Continuity signals predictability and order more than future investment | LTO-high gets weitsicht |
| wohlbefinden | MAS-low | Wellbeing as quality of life is the MAS-low signal | IND-high drops wohlbefinden; to denylist |

---

## Cross-language consistency flags

No cross-language divergence detected. Netherlands bag pending -- cross-country check to be run after NL bag is generated. German and Dutch share register proximity in UAI-high and LTO-high dimensions; flag for that review pass.

---

## Decision logs

### PDI high

```
Country: germany
Dimension: PDI
Polarity: high
Declared score: 35

Multi-word entries: none
Cross-country root flags: none (Netherlands bag pending)
Root-proximity flags (same country): none
Register spread: legal/bureaucratic 3 (weisungsbefugnis, dienstwege, protokoll), procedural 2 (unterordnung, gehorsam), social-cultural 3 (autorität, hierarchie, statusdenken), everyday 2 (vorgesetzter, statussymbol)
Persona-anchor words: no PDI-high firing in delivered personas. Christian carries status-seeking shadow (ehrgeiz); Brigitte carries professional expertise but not hierarchical deference. PDI-low frames both personas.
```

### PDI low

```
Country: germany
Dimension: PDI
Polarity: low
Declared score: 35

Multi-word entries: flachhierarchie (closed compound; no single-word equivalent captures flat-structure concept), direktkommunikation (closed compound; institutionally named in Hofstede Insights description of Germany -- justified)
Cross-country root flags: none (Netherlands bag pending)
Root-proximity flags (same country): mitbestimmung / mitsprache share mit- prefix -- both retained; institutional referents are distinct (co-determination law vs. right to voice)
Persona-anchor words: Christian and Brigitte both carry eigeninitiative and eigenverantwortung (developer autonomy, lawyer decision-making). Light but present across both personas.

```
Country: germany
Dimension: IDV
Polarity: high
Declared score: 67

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): eigenverantwortung / eigeninitiative / eigenleistung share eigen- prefix -- all retained; each anchors a distinct behavioral register (responsibility, initiative, output)
Register spread: legal/bureaucratic 2 (vertragsfreiheit, selbstbestimmung), procedural 1 (eigeninitiative), social-cultural 4 (selbstverwirklichung, unabhängigkeit, privatsphäre, freiheit), everyday 3 (eigenverantwortung, eigenleistung, selbstständigkeit)
Persona-anchor words: none
```

### IDV low

```
Country: germany
Dimension: IDV
Polarity: low
Declared score: 67

Multi-word entries: wir-gefühl (hyphenated compound; no single-word equivalent for the collective-feeling concept -- justified as one allowed hyphenated compound), gruppenidentität (closed compound; standard German)
Cross-country root flags: none
Root-proximity flags (same country): none
Persona-anchor words: no IDV-low firing in delivered personas. Both personas emphasize individual autonomy and decision-making; no collective-loyalty framing detected. This is architecturally correct for Germany's high IDV score. (Round 1 review: within-country collision with MAS-low). Replaced by kollektivgeist -- collective spirit, unambiguously IDV-low, no collision with any other bag.
```

### UAI high

```
Country: germany
Dimension: UAI
Polarity: high
Declared score: 65

Multi-word entries: regelwerk (closed compound; single token in German)
Cross-country root flags: none
Root-proximity flags (same country): regelwerk / vorschrift both name rule-systems -- retained; regelwerk is the body of rules as system, vorschrift is the individual prescription; distinct institutional referents
Register spread: legal/bureaucratic 3 (regelwerk, vorschrift, ordnung), procedural 4 (planung, struktur, systematik, genauigkeit), social-cultural 2 (gründlichkeit, verlässlichkeit), everyday 1 (präzision)
Persona-anchor words: Christian (developer): struktur, gründlichkeit, systematik, genauigkeit (4 of 10 fires). Brigitte (lawyer): präzision, gründlichkeit, verlässlichkeit, systematik (4 of 10 fires). Both personas carry strong UAI-high signals through procedural/precision emphasis.
```

### UAI low

```
Country: germany
Dimension: UAI
Polarity: low
Declared score: 65

Multi-word entries: experimentierfreude (closed compound; no single-word equivalent for enjoyment-of-experimentation), risikobereitschaft (closed compound; standard German for risk-willingness), anpassungsfähigkeit (closed compound; replaces pragmatismus which was resolved to LTO-high)
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: legal/bureaucratic 0, procedural 2 (anpassungsfähigkeit, wendigkeit), social-cultural 3 (experimentierfreude, risikobereitschaft, ungezwungenheit), everyday 5 (flexibilität, improvisation, spontaneität, offenheit, gelassenheit)
Persona-anchor words: Christian (developer): experimentierfreude, flexibilität, wendigkeit (3 of 10 fires). Brigitte (lawyer): anpassungsfähigkeit, wendigkeit, offenheit (3 of 10 fires). Light presence architecturally appropriate for tension with UAI-high cultural layer.
Note: ungezwungenheit flagged for native-speaker register check -- verify active use in cultural prose.
```

### MAS high

```
Country: germany
Dimension: MAS
Polarity: high
Declared score: 66

Multi-word entries: leistungsbereitschaft (closed compound; no single word captures disposition toward performance), leistungsgesellschaft (closed compound; institutionally load-bearing meta-concept -- justified), zielorientierung (closed compound; no single-word equivalent), durchsetzungsvermögen (closed compound; assertiveness has no single-word German equivalent -- justified)
Cross-country root flags: none
Root-proximity flags (same country): leistung / leistungsbereitschaft / leistungsgesellschaft share leistung- root -- three retained; leistungsträger dropped as redundant
Register spread: legal/bureaucratic 0, procedural 2 (zielorientierung, durchsetzungsvermögen), social-cultural 4 (karriere, erfolg, ehrgeiz, leistungsgesellschaft), everyday 4 (leistung, leistungsbereitschaft, wettbewerb, konkurrenz)
Persona-anchor words: Christian (developer): leistung, leistungsbereitschaft, karriere, erfolg, ehrgeiz, wettbewerb, konkurrenz, zielorientierung, durchsetzungsvermögen (9 of 10 bag words fire). Exceptionally strong MAS-high anchor -- Christian is the architectural MAS-high pole persona.
Note: four closed compounds in this bag. Rule applies to hyphenated compounds only. All four are natural single-token German words. No violation. leistungsgesellschaft flagged for native-speaker register check -- politically loaded in contemporary discourse.
```

### MAS low

```
Country: germany
Dimension: MAS
Polarity: low
Declared score: 66

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): fürsorge appears in IDV-low (resolved) -- assigned to MAS-low; not in IDV-low final bag
Register spread: legal/bureaucratic 0, procedural 0, social-cultural 6 (kooperation, lebensqualität, mitgefühl, harmonie, menschlichkeit, gemeinwohl), everyday 4 (rücksichtnahme, ausgewogenheit, sanftmut, fürsorge)
Persona-anchor words: Brigitte (lawyer): kooperation, rücksichtnahme, lebensqualität, harmonie, sanftmut, fürsorge, menschlichkeit, gemeinwohl (8 of 10 bag words fire). Strong MAS-low anchor -- Brigitte is the architectural MAS-low pole persona. Christian carries zero MAS-low words (correct polarity separation).
```

### LTO high

```
Country: germany
Dimension: LTO
Polarity: high
Declared score: 83

Multi-word entries: langfristigkeit (closed compound; the dimension concept itself in German), zukunftsorientierung (closed compound; no single-word equivalent), rücklagenbildung (dropped -- too finance-register specific)
Cross-country root flags: none
Root-proximity flags (same country): weitblick / weitsicht share sehen-root -- both retained; weitblick is the capacity for foresight, weitsicht is the strategic horizon application; register distinct
Register spread: legal/bureaucratic 0, procedural 3 (investition, langfristigkeit, zukunftsorientierung), social-cultural 4 (nachhaltigkeit, beharrlichkeit, geduld, ausdauer), everyday 3 (weitblick, sparsamkeit, weitsicht)
Persona-anchor words: no LTO-high persona firing in Christian or Brigitte. Position file carries strong LTO-high signal (nachhaltigkeit, beharrlichkeit, langfristigkeit, geduld, ausdauer, zukunftsorientierung). Personas inherit this frame at cultural foundation level; no persona-specific polarity needed.
```

### LTO low

```
Country: germany
Dimension: LTO
Polarity: low
Declared score: 83

Multi-word entries: gegenwartsorientierung (closed compound; no single-word equivalent)
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: legal/bureaucratic 0, procedural 1 (gegenwartsorientierung), social-cultural 4 (tradition, brauchtum, konvention, überlieferung), everyday 5 (kurzfristigkeit, sofortigkeit, gewohnheit, althergebracht, kurzfristdenken)
Persona-anchor words: Position carries strong LTO-low signal via Loses/Drives sections (Widerstand gegen sofortigkeit, Beharrlichkeit statt Hastigkeit). Personas inherit frame. No LTO-low-specific persona firing (correct -- personas layer MAS polarity, not LTO).
Note: statusquo removed (Round 1 review: spelling ambiguity -- Status quo is standard two-word German; single-token form unsafe). Replaced by kurzfristdenken -- short-term thinking, unambiguous LTO-low signal, single token. Althergebracht -- verify active use in cultural prose vs. archaic register.
```

### IND high

```
Country: germany
Dimension: IND
Polarity: high
Declared score: 40

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: legal/bureaucratic 0, procedural 0, social-cultural 4 (lebensfreude, vergnügen, hedonismus, geselligkeit), everyday 6 (genuss, freizeit, entspannung, unbeschwertheit, spaß, ausgelassenheit)
Persona-anchor words: no IND-high persona firing in Christian or Brigitte. Position file acknowledges entspannung and lebensfreude but frames them as compartmentalized (work/private boundary). Personas carry pure IND-low signals (correct for IND 40 low score).
```

### IND low

```
Country: germany
Dimension: IND
Polarity: low
Declared score: 40

Multi-word entries: pflichtbewusstsein (closed compound; institutionally load-bearing), pflichterfüllung (closed compound; distinct from pflichtbewusstsein -- disposition vs. act), verantwortungsgefühl (closed compound; no single-word equivalent), selbstkontrolle (closed compound; standard German single-token word)
Cross-country root flags: none
Root-proximity flags (same country): pflichtbewusstsein / pflichterfüllung share pflicht- root -- both retained; distinct registers (consciousness of duty vs. execution of duty). verbindlichkeit root-adjacent to UAI-high (obligation/bindingness overlaps with rule-following) -- primary register assigned to IND-low as duty/commitment; flagged for native-speaker check.
Register spread: legal/bureaucratic 1 (verbindlichkeit), procedural 2 (selbstdisziplin, selbstkontrolle), social-cultural 4 (pflichtbewusstsein, pflichterfüllung, verantwortungsgefühl, ernsthaftigkeit), everyday 3 (zurückhaltung, disziplin, mäßigung)
Persona-anchor words: Brigitte (lawyer): zurückhaltung, disziplin, selbstkontrolle, mäßigung, verbindlichkeit, verantwortungsgefühl, pflichterfüllung (7 of 10 bag words fire). Strong IND-low anchor. Christian (developer): zero IND-low words -- reflects competitive achievement focus, not restraint-based personality. Position carries overwhelming IND-low signal (9 of 10 bag words fire) -- foundational cultural layer all personas inherit.
```

---

## Native-speaker checks needed

- [ ] augenhöhe -- idiom in standard use but may be shifting toward corporate cliché; check whether it still reads as genuine cultural signal or has become HR-speak
- [ ] leistungsgesellschaft -- politically loaded in contemporary German discourse (critique of neoliberalism); check whether it signals MAS-high authentically or has acquired ironic register
- [ ] althergebracht -- verify natural cultural prose register vs. archaic
- [ ] ungezwungenheit -- verify active use in cultural prose; not bureaucratic-register paradox
- [ ] verbindlichkeit -- confirm primary register is duty/obligation and not contract/reliability reading that would pull toward UAI-high
