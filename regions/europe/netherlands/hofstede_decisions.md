# hofstede_decisions.md
## Netherlands | nl | v0.1.0 | 2026-05-11

---

## Section 1: Scores and calibration

| Dimension | Score | Band | Dominant polarity |
|---|---|---|---|
| PDI | 38 | Low (31-50) | LOW: flat, egalitarian, consultative |
| IDV | 80 | High (66-80) | HIGH: individual, self-direction, contract |
| MAS | 14 | Very low (0-30) | LOW: cooperation, modesty, care |
| UAI | 53 | Moderate (51-65) | Moderate HIGH: some structure preference |
| LTO | 67 | High (66-80) | HIGH: future, pragmatism, perseverance |
| IND | 68 | High (66-80) | HIGH: enjoyment, gratification, positivity |

UAI at 53 is genuinely moderate. Both bags drafted at reduced intensity. No compulsion-words used.

Bootstrap: fresh. No previous bag. No sibling fork (no existing Dutch-language bag in project).

---

## Section 2: Conflict resolution table

| Word | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|
| autonomie | IDV_high | Individual assertion vs. authority is IDV not PDI; PDI-low is flat structures not individual rights | inspraak in PDI_low |
| consensus | PDI_low | Flat decision mode is PDI register (polder model); care-cooperation in MAS is distinct | mededogen in MAS_low |
| gelijkheid | PDI_low | Equality of standing (no rank) is PDI; equality as care/fairness is MAS | inclusief in MAS_low |
| pragmatisch | LTO_high | Dutch pragmatism is future-adaptation per Hofstede's own NL description; not comfort-with-chaos | experiment in UAI_low |
| spontaan | IND_high | Enjoyment/impulse register dominates for NL IND 68; flexibility register secondary | spontaniteit in UAI_low |
| vrijheid | IDV_high | Loosely-knit social framework is IDV; gratification freedom is secondary | levensvreugde in IND_high |
| solidariteit | MAS_low | Care/cooperation register; standing-with is MAS not IDV | ingroep in IDV_low |
| samenwerking | MAS_low | Care-over-competition is MAS; flat-collaboration already covered by collegialiteit in PDI_low | collegialiteit in PDI_low |
| informeel | PDI_low | First placement; flat culture marker | spontaniteit in UAI_low |

---

## Section 3: Drops from previous bag

No previous bag. Fresh bootstrap.

Fix applied post-review (Geert Hofstede review, 2026-05-11):
normatiefheid -- dropped -- cultural register concern: word does not appear in Dutch cultural prose; replaced by behoudend

---

## Section 4: Cross-language consistency flags

- directheid (NL PDI_low): no Danish or German equivalent in PDI_low bags. No collision.
- medezeggenschap (NL PDI_low): German co-determination rights are PDI_low signal but no German word in existing bag. No collision. Flag for German bag drafting.
- discipline (NL IND_low): German position file uses Disziplin heavily. NL register: restraint-of-pleasure. DE register: likely structural self-control, potentially UAI or MAS coded. Flag for German bag drafting session -- cross-country register reasoning required.
- gezelligheid (NL IND_high): Danish hygge covers adjacent territory but is a separate country, separate file. No bag collision. Conceptual proximity documented.
- precisie (NL UAI_high): German Praezision would also be UAI_high. Same direction, no collision.
- prestatie (NL MAS_high): German Leistung would also be MAS_high. Same direction, no collision.

No divergent cross-language calls detected against existing bags.

---

## Section 5: Final bags (confirmed)

PDI_low: gelijkwaardig, toegankelijk, informeel, directheid, collegialiteit, overleg, medezeggenschap, inspraak, participatie, consensus

PDI_high: hiërarchie, gezag, autoriteit, ondergeschiktheid, gehoorzaamheid, protocol, formaliteit, eerbied, titulering, distantie

IDV_high: zelfredzaamheid, zelfstandigheid, individueel, privacy, initiatief, verantwoordelijkheid, onafhankelijkheid, merite, contract, autonomie

IDV_low: collectief, loyaliteit, saamhorigheid, solidariteit, clan, gemeenschap, ingroep, trouw, afhankelijkheid, harmonie

MAS_low: zorg, bescheidenheid, samenwerking, welzijn, empathie, mededogen, kwetsbaar, naasten, inclusief, sociaal

MAS_high: ambitie, prestatie, competitie, winnaar, assertiviteit, doelgericht, resultaat, carrière, dominantie, prestatiegerichtheid

UAI_high: structuur, regels, planning, procedure, precisie, beleid, systematisch, kader, voorbereiding, overzicht

UAI_low: flexibel, experiment, aanpassen, tolerantie, risico, improvisatie, ruimte, onzekerheid, testen, spontaniteit

LTO_high: toekomst, volharding, investering, pragmatisch, duurzaam, doorzetten, leren, ontwikkeling, langetermijn, continuïteit

LTO_low: traditie, kortetermijn, gewoonten, resultaat, snel, verleden, stabiliteit, onmiddellijk, bewezen, behoudend

IND_high: genieten, plezier, ontspanning, geluk, levensvreugde, humor, spontaan, vriendschap, gezelligheid, optimisme

IND_low: beheersing, discipline, plicht, matigheid, terughoudendheid, zelfbeheersing, verplichting, ernst, soberheid, onthechting

---

## Section 5b: Country denylist

Words considered, rejected, excluded from all Netherlands bags:

autonomie -- cross-bag collision, moved to IDV_high
consensus -- cross-bag collision, moved to PDI_low
gelijkheid -- cross-bag collision, moved to PDI_low
pragmatisch -- cross-bag collision, moved to LTO_high
spontaan -- cross-bag collision, moved to IND_high
vrijheid -- cross-bag collision, moved to IDV_high
solidariteit -- cross-bag collision, moved to MAS_low
samenwerking -- cross-bag collision, moved to MAS_low
wij -- pronoun, denylist class
nu -- deictic, denylist class
open -- polysemous high-frequency, denylist class
zelf -- pronoun class
norm -- same-dimension opposite-polarity risk (UAI_high and UAI_low readings both plausible)
rang -- weak cultural load in Dutch prose
relatie -- polysemous high-frequency
vermijden -- dimension mismatch (UAI not LTO)
sparen -- register too narrow (financial only)
meten -- cross-dimension ambiguity, unsafe for scoring
instrument -- cross-dimension ambiguity, unsafe for scoring
afstand -- polysemous (physical vs. power distance)
dimensie -- too technical for cultural prose
vergelijken -- no clean dimension signal
modelleren -- too technical
informeel -- within-country collision with PDI_low (first placement)
zekerheid -- cross-dimension risk with UAI_high
normatiefheid -- cultural register concern; word absent from Dutch cultural prose; replaced by behoudend

---

## Section 6: Per-word justification

**PDI_low**
gelijkwaardig -- PDI-low: equal standing -- core Dutch egalitarian value, no inherent rank between persons
toegankelijk -- PDI-low: accessible -- superiors on first name basis; management reachable
informeel -- PDI-low: informal -- first-name culture, no protocol distance
directheid -- PDI-low: directness -- Dutch directness is PDI-low behavioral signature
collegialiteit -- PDI-low: collegiality -- peer relationship as default, not hierarchical
overleg -- PDI-low: consultation -- employees expect to be consulted before decisions
medezeggenschap -- PDI-low: co-determination -- institutionalized participation right; load-bearing Dutch concept
inspraak -- PDI-low: voice/input -- the right to speak up; structurally embedded in Dutch workplace culture
participatie -- PDI-low: participation -- flat decision-making requires active participation
consensus -- PDI-low: consensus -- Dutch polder model; decision by agreement not by rank

**PDI_high**
hiërarchie -- PDI-high: hierarchy -- direct signal of vertical power ordering
gezag -- PDI-high: authority -- legitimate power as positional
autoriteit -- PDI-high: formal authority -- institutional rank-based power
ondergeschiktheid -- PDI-high: subordination -- acceptance of lower position
gehoorzaamheid -- PDI-high: obedience -- compliance with rank
protocol -- PDI-high: protocol -- formal procedures governing interaction by rank
formaliteit -- PDI-high: formality -- distance-maintaining behavior
eerbied -- PDI-high: deference -- respect as positional not earned
titulering -- PDI-high: titling -- use of formal titles as distance marker
distantie -- PDI-high: distance -- emotional and social distance between ranks

**IDV_high**
zelfredzaamheid -- IDV-high: self-reliance -- individual takes care of self not in-group
zelfstandigheid -- IDV-high: independence -- operating without group support
individueel -- IDV-high: individual -- self-image defined as I not We
privacy -- IDV-high: privacy -- personal sphere protected from group
initiatief -- IDV-high: initiative -- individual acts without waiting for group
verantwoordelijkheid -- IDV-high: responsibility -- personal accountability not collective
onafhankelijkheid -- IDV-high: independence (personal) -- freedom from group claims
merite -- IDV-high: merit -- hiring/promotion on individual performance
contract -- IDV-high: contract -- employer-employee as mutual agreement not loyalty bond
autonomie -- IDV-high: autonomy -- individual self-direction as value; persona anchor

**IDV_low**
collectief -- IDV-low: collective -- group as primary unit
loyaliteit -- IDV-low: loyalty -- obligation to in-group
saamhorigheid -- IDV-low: togetherness -- belonging to a defined group
solidariteit -- IDV-low: solidarity -- standing with the group
clan -- IDV-low: clan -- tight kinship group as identity carrier
gemeenschap -- IDV-low: community -- group defines the individual
ingroep -- IDV-low: in-group -- bounded group with clear membership
trouw -- IDV-low: faithfulness -- loyalty as ongoing obligation
afhankelijkheid -- IDV-low: dependence -- reliance on group for identity and support
harmonie -- IDV-low: harmony -- group peace as value over individual assertion

**MAS_low**
zorg -- MAS-low: care -- caring for the weak as social value
bescheidenheid -- MAS-low: modesty -- not standing out; quality over competition
samenwerking -- MAS-low: cooperation -- working together over competing
welzijn -- MAS-low: wellbeing -- quality of life as success metric
empathie -- MAS-low: empathy -- understanding others as social value
mededogen -- MAS-low: compassion -- active care for others
kwetsbaar -- MAS-low: vulnerable -- acknowledging weakness is acceptable; score 14 justifies inclusion
naasten -- MAS-low: loved ones -- care directed at proximate others
inclusief -- MAS-low: inclusive -- no one excluded from care
sociaal -- MAS-low: social -- socially oriented behavior as valued trait; persona anchor (Gert Jan)

**MAS_high**
ambitie -- MAS-high: ambition -- individual drive for more
prestatie -- MAS-high: achievement -- success defined by performance
competitie -- MAS-high: competition -- winner/loser framing
winnaar -- MAS-high: winner -- being best in field as goal
assertiviteit -- MAS-high: assertiveness -- pushing forward as valued
doelgericht -- MAS-high: goal-oriented -- results over relationships
resultaat -- MAS-high: result -- outcome as measure of worth (cross-dimension note: also in LTO_low; see decision log)
carrière -- MAS-high: career -- upward trajectory as life goal
dominantie -- MAS-high: dominance -- being on top as valued state
prestatiegerichtheid -- MAS-high: achievement-orientation -- systemic focus on performance outcomes; closed compound, not hyphenated

**UAI_high**
structuur -- UAI-high: structure -- preference for organized frameworks
regels -- UAI-high: rules -- rules as comfort against uncertainty
planning -- UAI-high: planning -- preparing for future reduces uncertainty
procedure -- UAI-high: procedure -- defined process reduces ambiguity
precisie -- UAI-high: precision -- exactness as response to uncertainty; persona anchor (Geert)
beleid -- UAI-high: policy -- structured framework for decisions
systematisch -- UAI-high: systematic -- methodical approach as preference
kader -- UAI-high: framework -- bounding context reduces open-endedness
voorbereiding -- UAI-high: preparation -- reducing surprise through advance work
overzicht -- UAI-high: overview -- having the full picture before acting

**UAI_low**
flexibel -- UAI-low: flexible -- adapts when situation changes
experiment -- UAI-low: experiment -- trying new approaches without fear
aanpassen -- UAI-low: adapt -- changing course is comfortable
tolerantie -- UAI-low: tolerance -- deviance and difference accepted
risico -- UAI-low: risk -- uncertainty not inherently threatening
improvisatie -- UAI-low: improvisation -- working without complete plan
ruimte -- UAI-low: room/space -- leaving things open is acceptable
onzekerheid -- UAI-low: uncertainty -- comfortable with not knowing
testen -- UAI-low: testing -- empirical trial-and-error approach
spontaniteit -- UAI-low: spontaneity -- unplanned action as comfortable; native-speaker check flagged (root proximity with spontaan in IND_high)

**LTO_high**
toekomst -- LTO-high: future -- future-orientation as planning horizon
volharding -- LTO-high: perseverance -- sustained effort over time
investering -- LTO-high: investment -- committing resources for future return
pragmatisch -- LTO-high: pragmatic -- truth depends on situation not absolute; NL cultural marker
duurzaam -- LTO-high: sustainable -- long-term thinking embedded in the word
doorzetten -- LTO-high: persist -- continuing despite difficulty
leren -- LTO-high: learning -- adaptation through knowledge accumulation
ontwikkeling -- LTO-high: development -- gradual improvement over time
langetermijn -- LTO-high: long-term -- explicit temporal orientation; closed compound (one per bag)
continuïteit -- LTO-high: continuity -- sustaining what works across time

**LTO_low**
traditie -- LTO-low: tradition -- time-honoured norms as anchor
kortetermijn -- LTO-low: short-term -- immediate horizon as orientation; closed compound (one per bag)
gewoonten -- LTO-low: habits/customs -- established patterns as truth
resultaat -- LTO-low: result -- quick outcome as goal; cross-dimension flag: also in MAS_high; distinct registers retained in both bags
snel -- LTO-low: fast -- speed as value not patience
verleden -- LTO-low: past -- past as reference point
stabiliteit -- LTO-low: stability -- existing state as preferred
onmiddellijk -- LTO-low: immediately -- now as the relevant timeframe
bewezen -- LTO-low: proven -- established methods over new approaches
behoudend -- LTO-low: conservative/tradition-bound -- everyday register; culturally marked NL usage; replaces normatiefheid per Geert Hofstede review 2026-05-11

**IND_high**
genieten -- IND-high: enjoyment -- free gratification of natural drives
plezier -- IND-high: pleasure -- positive experience as valued
ontspanning -- IND-high: relaxation -- leisure time as legitimate
geluk -- IND-high: happiness -- positive emotional state as life goal
levensvreugde -- IND-high: joie de vivre -- enjoyment of life as value; Dutch cultural marker; closed compound (one per bag)
humor -- IND-high: humor -- lightness and laughter as social value
spontaan -- IND-high: spontaneous -- acting on impulse as positive
vriendschap -- IND-high: friendship -- chosen relationships for enjoyment
gezelligheid -- IND-high: conviviality -- Dutch cultural marker for enjoyable togetherness; native-speaker check flagged (social vs. individual gratification coding)
optimisme -- IND-high: optimism -- positive attitude toward life

**IND_low**
beheersing -- IND-low: control -- controlling impulses
discipline -- IND-low: discipline -- self-restraint as duty; native-speaker check: confirm NL register is pleasure-restraint not rule-following
plicht -- IND-low: duty -- obligation over desire
matigheid -- IND-low: moderation -- limiting gratification
terughoudendheid -- IND-low: restraint -- holding back
zelfbeheersing -- IND-low: self-control -- mastering own impulses; closed compound (one per bag)
verplichting -- IND-low: obligation -- duty-bound behavior
ernst -- IND-low: seriousness -- gratification secondary to duty
soberheid -- IND-low: sobriety -- plain unindulgent living
onthechting -- IND-low: detachment -- releasing desire; native-speaker check: confirm frequency in Dutch cultural prose

---

## Section 7: Decision logs

**PDI_low | Netherlands | PDI 38 | Low band**
Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: directheid / direct -- not in other bags, clear
Register spread: social-cultural 4, procedural 3, everyday 3
Persona-anchor words: none (afstand dropped: polysemous)

**PDI_high | Netherlands | PDI 38 | Opposing**
Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: none
Register spread: legal/bureaucratic 3, procedural 3, social-cultural 4

**IDV_high | Netherlands | IDV 80 | High band**
Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: zelfstandigheid / zelfredzaamheid -- same zelf- root; kept: zelfstandigheid is operating independently, zelfredzaamheid is self-sufficiency; distinct
Register spread: legal/bureaucratic 2, procedural 2, social-cultural 4, everyday 2
Persona-anchor words: autonomie (from position files)

**IDV_low | Netherlands | IDV 80 | Opposing**
Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: saamhorigheid / solidariteit -- adjacent concepts; kept: saamhorigheid is belonging, solidariteit is standing-with; distinct register
Register spread: social-cultural 6, everyday 4

**MAS_low | Netherlands | MAS 14 | Very low band**
Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: empathie / mededogen -- care-register siblings; kept: empathie is understanding, mededogen is active compassion; distinct
Register spread: social-cultural 6, everyday 4
Persona-anchor words: sociaal (Gert Jan files)

**MAS_high | Netherlands | MAS 14 | Opposing**
Multi-word entries: prestatiegerichtheid (closed compound, not hyphenated -- allowed)
Cross-country root flags: prestatie / Leistung (German MAS_high probable): same direction, no collision
Root-proximity flags: prestatie / prestatiegerichtheid -- root proximity; kept: one is the act, one is the orientation
Register spread: procedural 3, social-cultural 4, everyday 3

**UAI_high | Netherlands | UAI 53 | Moderate**
Multi-word entries: none
Cross-country root flags: precisie / Praezision (German UAI_high probable): same direction, no collision
Root-proximity flags: none
Register spread: legal/bureaucratic 2, procedural 5, social-cultural 2, everyday 1
Persona-anchor words: precisie (Geert persona: specifiek, duidelijk cluster)

**UAI_low | Netherlands | UAI 53 | Opposing moderate**
Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: spontaniteit (UAI_low) / spontaan (IND_high) -- root proximity; native-speaker check required: confirm these read as distinct concepts in Dutch cultural prose; if not, replace spontaniteit with nonchalance
Register spread: procedural 3, social-cultural 3, everyday 4

**LTO_high | Netherlands | LTO 67 | High band**
Multi-word entries: langetermijn (closed compound -- one per bag)
Cross-country root flags: none
Root-proximity flags: volharding / doorzetten -- perseverance cluster; kept: volharding is the quality, doorzetten is the action; distinct
Register spread: procedural 3, social-cultural 3, everyday 4

**LTO_low | Netherlands | LTO 67 | Opposing**
Multi-word entries: kortetermijn (closed compound -- one per bag)
Cross-country root flags: none
Root-proximity flags: gewoonten / traditie -- habit cluster; kept: gewoonten is behavioral habit, traditie is cultural inheritance; distinct register
Cross-dimension flag: resultaat fires in MAS_high too; NL is MAS_low and LTO_high so opposing bags carry it; distinct registers (achievement vs. quick-result); retained in both with documentation
Post-review change: normatiefheid replaced by behoudend (Geert Hofstede review, 2026-05-11)
Register spread: social-cultural 4, procedural 2, everyday 4

**IND_high | Netherlands | IND 68 | High band**
Multi-word entries: levensvreugde (closed compound -- one per bag)
Cross-country root flags: none
Root-proximity flags: geluk / optimisme -- positive-affect cluster; kept: geluk is happiness as state, optimisme is positive orientation; distinct
Register spread: social-cultural 5, everyday 5
Native-speaker check: gezelligheid -- confirm IND_high coding (individual vs. social gratification)

**IND_low | Netherlands | IND 68 | Opposing**
Multi-word entries: zelfbeheersing (closed compound -- one per bag)
Cross-country root flags: discipline / Disziplin (German): NL register is restraint-of-pleasure; DE register likely UAI or MAS coded; flag for German bag drafting
Root-proximity flags: beheersing / zelfbeheersing -- root proximity; kept: beheersing is control (general), zelfbeheersing is self-control (specific); distinct; logged
Register spread: social-cultural 4, procedural 3, everyday 3

---

## Section 8: Native-speaker check items

- spontaniteit (UAI_low): root proximity with spontaan (IND_high); confirm these read as distinct in Dutch cultural prose; if not, replace with nonchalance
- gezelligheid (IND_high): primarily social concept; confirm it scores individual gratification in Dutch content or reassign
- discipline (IND_low): confirm Dutch register is pleasure-restraint not rule-following (which would be UAI_high)
- onthechting (IND_low): philosophical register; confirm frequency in Dutch cultural prose
- prestatiegerichtheid (MAS_high): closed compound; confirm natural usage frequency in Dutch prose

---

*hofstede_decisions.md - netherlands - v0.1.0*
*Reviewed: Geert Hofstede, Gert Jan Hofstede -- Nyhavn session, 2026-05-11*
*KAI HACKS AI / Cultures*
