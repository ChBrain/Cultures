# hofstede_decisions.md
## Cultures / Mexico

**Scores:** PDI 81 · IDV 30 · UAI 82 · MAS 69 · LTO 24 · IND 97
**Language:** es
**Region:** americas
**Generated:** 2026-05-16
**Status:** draft
**Bootstrap:** fresh -- no previous bag, no sibling fork

---

## Section 1: Draft Pass

All 12 bags drafted from 15-20 candidates per slot. Candidates generated from:
- Direct dimension vocabulary in Spanish
- Behavioral vocabulary enacting the dimension without naming it
- Institutionally anchored words load-bearing in Mexican cultural context
- Everyday vocabulary native speakers associate with the cultural value
- Opposing-polarity bags drafted with awareness of score band (very low scores require strong opposing-polarity words)

No persona files exist yet for Mexico. Persona-anchor scan deferred to Round 2.
No sibling bag to fork from. Spain diverges significantly (PDI 57, IDV 51, LTO 48, IND 44) and shares only language, not Hofstede profile.

---

## Section 2: Conflict Resolution Table

| Word | First fired | Second fired | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|---|---|
| autonomía | PDI-low | IDV-high | IDV-high | Skill rule: individual autonomy is IDV-high, not PDI-low. PDI-low describes flat structures, not individual assertion. | PDI-low: horizontalidad |
| familia | IDV-low | LTO-low | IDV-low | Family as collective anchor is IDV-low. LTO-low carries tradition as temporal anchor. Different register. | LTO-low: ancestro |
| libertad | PDI-low | IDV-high | IDV-high | Same reasoning as autonomía. Individual freedom is IDV-high. | PDI-low: participación |
| disciplina | LTO-high | IND-low | IND-low | Restraint and duty are IND-low. LTO-high carries sustained investment and planning. | LTO-high: previsión |
| tradición | LTO-low | IDV-low | LTO-low | Tradition is LTO-low per skill hard rule. IDV-low covered by familia, comunidad. | IDV-low: hermandad |
| solidaridad | IDV-low | MAS-low | IDV-low | Solidarity as in-group bond is IDV-low. MAS-low carries relational care. | MAS-low: acompañamiento |
| espontaneidad | UAI-low | IND-high | IND-high | Spontaneity as gratification-impulse belongs to IND-high at score 97. UAI-low carries flexibility and improvisation. | UAI-low: informalidad |
| mérito | PDI-low | IDV-high | IDV-high | Merit as individual achievement signal is IDV-high. PDI-low describes structural flatness. | PDI-low: diálogo |
| superación | IDV-high | MAS-high | MAS-high | Self-improvement as achievement and ambition is MAS-high. IDV-high has sufficient individual vocabulary. | IDV-high: trayectoria |
| poder | PDI-high | MAS-high | PDI-high | Power as authority and hierarchy is PDI. MAS-high carries achievement and performance vocabulary. | MAS-high: empuje |
| convivencia | IDV-low | IND-high | IDV-low | Convivencia as communal belonging is IDV. IND-high carries the pleasure and celebration register. | IND-high: derroche (subsequently replaced by gozo) |
| presente | LTO-low | IND-high | LTO-low | Present-focus as temporal orientation is LTO. IND-high carries pleasure and gratification vocabulary. | IND-high: gozo |
| obligación | IDV-low | IND-low | IND-low | Obligation as restraint on gratification belongs to IND-low. IDV-low has communal vocabulary. | IDV-low: red |
| iniciativa | PDI-low | IDV-high | IDV-high | Personal initiative as individual agency is IDV-high. PDI-low carries structural access vocabulary. | PDI-low: acceso |
| don | PDI-high | -- | REMOVED | Polysemy: honorific vs. common Spanish noun/verb form. Matcher cannot disambiguate. Hard FAIL per review Round 1. | PDI-high: señor |

---

## Section 3: Drops from Previous Bag

No previous bag -- fresh bootstrap.

---

## Section 4: Cross-Language Consistency Flags

**respeto** (Mexico, PDI-high): Spanish cognate in common cultural use in Spain but Spain has no PDI bag in project files. No collision. Mexican register specifically load-bearing through social hierarchy of greeting and patron relationship. Retained.

**compadrazgo** (Mexico, PDI-high): No cognate in any existing project bag. Institutionally anchored, Mexican-specific. Clear.

**patrón** (Mexico, PDI-high): No collision with existing bags. Spanish word carrying specifically Mexican labor-hierarchy register. Clear.

**familia** (Mexico, IDV-low): Conceptual overlap with Spanish position file which carries familia as first order of loyalty. Spain has no IDV bag. Register distinction: Mexican familia is gravitational and cosmic; Spanish familia is relational and protective. Documented, retained.

**fiesta** (Mexico, IND-high): No collision with existing bags. Appears in Spanish cultural usage but not as a bag word. Mexican register carries fiesta as primary evidence of indulgence at score 97. Retained.

**aguante** (Mexico, IND-low): No cognate in any existing bag. Mexican-specific register: endurance as cultural virtue under pressure. Culturally marked. Clear.

No cross-language divergence requiring resolution.

---

## Section 5: Final Bags

### PDI-HIGH
jerarquía
respeto
patrón
autoridad
mando
compadrazgo
cargo
señor
obediencia
antigüedad

### PDI-LOW
horizontalidad
participación
diálogo
consenso
colega
acuerdo
acceso
voz
apertura
criterio

### IDV-LOW
familia
comunidad
lealtad
nosotros
pertenencia
grupo
vínculo
compromiso
red
hermandad

### IDV-HIGH
individuo
autonomía
trayectoria
independencia
elección
iniciativa
privacidad
camino
identidad
voluntad

### UAI-HIGH
norma
protocolo
procedimiento
certeza
orden
estructura
formalidad
trámite
reglamento
documento

### UAI-LOW
improvisación
flexibilidad
informalidad
riesgo
intuición
adaptación
inventiva
soltura
tanteo
ingenio

### MAS-HIGH
éxito
ambición
logro
competencia
triunfo
rendimiento
reconocimiento
ascenso
empuje
esfuerzo

### MAS-LOW
cuidado
cooperación
modestia
apoyo
comprensión
armonía
bienestar
empatía
generosidad
acompañamiento

### LTO-LOW
tradición
presente
herencia
costumbre
ancestro
memoria
origen
raíz
rito
legado

### LTO-HIGH
planificación
inversión
futuro
continuidad
proyecto
estrategia
previsión
acumulación
horizonte
formación

### IND-HIGH
fiesta
alegría
disfrute
placer
música
baile
comida
humor
sabor
gozo

### IND-LOW
sacrificio
deber
contención
sobriedad
aguante
silencio
recato
moderación
renuncia
templanza

---

## Section 5b: Country Denylist

autonomía -- moved to IDV-high; PDI-low collision
libertad -- moved to IDV-high; PDI-low collision
mérito -- moved to IDV-high; PDI-low collision
poder -- moved to PDI-high; MAS-high collision
disciplina -- moved to IND-low; LTO-high collision
solidaridad -- moved to IDV-low; MAS-low collision
celebración -- moved to IND-high; LTO-low collision resolved by ancestro
espontaneidad -- moved to IND-high; UAI-low collision resolved by informalidad
convivencia -- moved to IDV-low; IND-high collision resolved by gozo
presente -- retained LTO-low; IND-high collision resolved by gozo
obligación -- moved to IND-low; IDV-low collision resolved by red
superación -- moved to MAS-high; IDV-high collision resolved by trayectoria
don -- polysemy disqualifier: honorific vs. common Spanish noun/verb; replaced by señor in PDI-high
iniciativa -- within-country collision PDI-low/IDV-high; retained IDV-high, replaced PDI-low with acceso

---

## Section 6: Per-Word Justification

### PDI-HIGH
jerarquía -- PDI-high -- the word for hierarchy itself, load-bearing in every institutional and family context in Mexico
respeto -- PDI-high -- respect as the social lubricant of vertical relationships, expected before any transaction
patrón -- PDI-high -- the employer-protector figure carrying the full authority structure of Mexican labor culture
autoridad -- PDI-high -- authority as institutional and personal fact, not questioned, navigated
mando -- PDI-high -- command as a natural feature of the room, whoever holds it holds it without explanation
compadrazgo -- PDI-high -- ritual kinship network formalizing loyalty and obligation across social strata, uniquely Mexican load-bearing term
cargo -- PDI-high -- the title that arrives before the person, placement word in every formal register
señor -- PDI-high -- honorific marking seniority and respect in the social hierarchy, unambiguous placement signal
obediencia -- PDI-high -- obedience as the expected response to authority, not submission but right order
antigüedad -- PDI-high -- seniority as legitimate claim to authority, institutionalized in labor law and social custom

### PDI-LOW
horizontalidad -- PDI-low -- flatness of structure, used in contemporary Mexican organizational discourse for non-hierarchical design
participación -- PDI-low -- participation as equal standing in a process, democratic register
diálogo -- PDI-low -- dialogue as the mechanism of equal exchange, used in political and social reform contexts
consenso -- PDI-low -- consensus as a decision mode not requiring a superior to decide
colega -- PDI-low -- colleague as peer, the word that signals flat register between equals
acuerdo -- PDI-low -- agreement reached between equals rather than handed down from above
acceso -- PDI-low -- structural access to the process regardless of rank, flat-structure signal
voz -- PDI-low -- voice as the right to speak and be heard regardless of rank
apertura -- PDI-low -- openness as structural availability, the flat room that receives input from any direction
criterio -- PDI-low -- personal judgment exercised independently of rank

### IDV-LOW
familia -- IDV-low -- the primary collective unit, gravitational not relational, you do not leave it and it does not release you
comunidad -- IDV-low -- community as the collective that precedes and outlasts the individual
lealtad -- IDV-low -- loyalty as the currency of collective belonging, owed before it is earned
nosotros -- IDV-low -- we as the operative subject, the group that acts and decides
pertenencia -- IDV-low -- belonging as the condition of full personhood, not optional
grupo -- IDV-low -- the group as the unit of action and identity
vínculo -- IDV-low -- the bond that ties person to person, collective to collective
compromiso -- IDV-low -- commitment as the obligation that makes belonging real
red -- IDV-low -- the network of relationships that precedes and enables every action
hermandad -- IDV-low -- brotherhood as the register of tight collective solidarity, goes beyond colega into mutual claim

### IDV-HIGH
individuo -- IDV-high -- the individual as a distinct agent, used in contexts where personal standing is asserted
autonomía -- IDV-high -- personal autonomy as the right and capacity to act from one's own center
trayectoria -- IDV-high -- personal trajectory as the individual's story of achievement and movement
independencia -- IDV-high -- independence as the state of not being determined by others
elección -- IDV-high -- personal choice as the expression of individual will
iniciativa -- IDV-high -- personal initiative taken without waiting for collective permission
privacidad -- IDV-high -- privacy as the individual's protected interior space
camino -- IDV-high -- the personal path, the individual's direction distinct from the group's
identidad -- IDV-high -- personal identity as distinct from collective membership
voluntad -- IDV-high -- will as the individual's capacity to direct themselves

### UAI-HIGH
norma -- UAI-high -- the rule that structures behavior and reduces uncertainty
protocolo -- UAI-high -- protocol as the prescribed sequence that makes outcomes predictable
procedimiento -- UAI-high -- procedure as the formal path through any institutional process
certeza -- UAI-high -- certainty as the valued state, the goal that planning and rules pursue
orden -- UAI-high -- order as the condition that structure produces and uncertainty destroys
estructura -- UAI-high -- structure as the framework that holds everything in predictable relation
formalidad -- UAI-high -- formality as the register that signals the rules are in operation
trámite -- UAI-high -- the bureaucratic procedure, uniquely Mexican load-bearing word for the formal process that must be followed
reglamento -- UAI-high -- the rulebook, the written document that makes the rules visible and binding
documento -- UAI-high -- the document as the physical proof that the procedure was followed

### UAI-LOW
improvisación -- UAI-low -- improvisation as the capacity to act without a predetermined plan
flexibilidad -- UAI-low -- flexibility as the valued ability to adapt to changing conditions
informalidad -- UAI-low -- informality as the register that operates outside the formal structure
riesgo -- UAI-low -- risk as something accepted or embraced rather than avoided
intuición -- UAI-low -- intuition as a trusted guide in the absence of rules
adaptación -- UAI-low -- adaptation as the response to ambiguity rather than resistance to it
inventiva -- UAI-low -- inventiveness as the creative capacity that operates without a manual
soltura -- UAI-low -- ease and looseness in moving through situations without needing a fixed frame
tanteo -- UAI-low -- trial and error as a legitimate method, feeling one's way through uncertainty
ingenio -- UAI-low -- ingenuity as the capacity to find solutions outside prescribed paths

### MAS-HIGH
éxito -- MAS-high -- success as the publicly valued outcome of ambition and effort
ambición -- MAS-high -- ambition as the drive that organizes individual effort toward achievement
logro -- MAS-high -- achievement as the concrete result that demonstrates competence
competencia -- MAS-high -- competition as the context in which achievement is tested
triunfo -- MAS-high -- triumph as the register of winning, stronger than éxito, carries the body
rendimiento -- MAS-high -- performance as the measurable output that justifies position
reconocimiento -- MAS-high -- recognition as the social confirmation that achievement has been witnessed
ascenso -- MAS-high -- advancement as the upward movement that ambition produces
empuje -- MAS-high -- drive and push as the energy that produces results, specifically Mexican register
esfuerzo -- MAS-high -- effort as the visible expenditure of energy toward a goal, socially valued

### MAS-LOW
cuidado -- MAS-low -- care as the orientation toward the other's wellbeing
cooperación -- MAS-low -- cooperation as the preferred mode of working together
modestia -- MAS-low -- modesty as the social virtue of not asserting superiority
apoyo -- MAS-low -- support as the relational act of holding someone else up
comprensión -- MAS-low -- understanding as the empathic orientation toward another's situation
armonía -- MAS-low -- harmony as the valued state of relational peace
bienestar -- MAS-low -- wellbeing as the goal that organizes care and cooperation
empatía -- MAS-low -- empathy as the capacity to feel with the other
generosidad -- MAS-low -- generosity as the social virtue of giving without calculation
acompañamiento -- MAS-low -- accompaniment as the act of being present with someone through their experience, specifically Mexican pastoral and social register

### LTO-LOW
tradición -- LTO-low -- tradition as the anchor in the past that organizes the present; LTO-low per skill hard rule
presente -- LTO-low -- the present moment as the primary temporal register
herencia -- LTO-low -- inheritance as what the past hands to the present, not what the present builds for the future
costumbre -- LTO-low -- custom as the habitual practice that connects present to past
ancestro -- LTO-low -- the ancestor as a living presence in the current moment, not a historical abstraction
memoria -- LTO-low -- memory as the faculty that keeps the past present
origen -- LTO-low -- origin as the point of identity, where things come from determines what they are
raíz -- LTO-low -- root as the metaphor for connection to origin and tradition
rito -- LTO-low -- rite as the repeated practice that keeps tradition alive in the present
legado -- LTO-low -- legacy as what the past leaves in the present, received rather than built

### LTO-HIGH
planificación -- LTO-high -- planning as the forward-oriented activity that organizes action toward future outcomes
inversión -- LTO-high -- investment as the commitment of resources now for future return
futuro -- LTO-high -- the future as the temporal orientation that organizes present decisions
continuidad -- LTO-high -- continuity as the value of sustained effort across time
proyecto -- LTO-high -- project as the organized forward-looking endeavor
estrategia -- LTO-high -- strategy as the long-term thinking that precedes action
previsión -- LTO-high -- foresight as the capacity to anticipate and prepare
acumulación -- LTO-high -- accumulation as the patient building up of resources over time
horizonte -- LTO-high -- horizon as the metaphor for the long-term view
formación -- LTO-high -- formation and education as investment in the future self

### IND-HIGH
fiesta -- IND-high -- the party as the primary institution of gratification and communal pleasure; load-bearing at score 97
alegría -- IND-high -- joy as a legitimate and pursued state, not incidental
disfrute -- IND-high -- enjoyment as an active practice, the noun form of disfrutar
placer -- IND-high -- pleasure as a recognized good, not suspect
música -- IND-high -- music as the sonic environment of gratification, present at every occasion
baile -- IND-high -- dance as the bodily expression of indulgence, inseparable from celebration
comida -- IND-high -- food as pleasure and abundance, not sustenance
humor -- IND-high -- humor as the social lubricant and the pleasure of the moment
sabor -- IND-high -- flavor as the sensory register of pleasure, carries the body and the culture simultaneously
gozo -- IND-high -- joy as fullness and delight, stronger register than alegría, carries spiritual and physical pleasure together

### IND-LOW
sacrificio -- IND-low -- sacrifice as the valued act of giving up gratification for a higher claim
deber -- IND-low -- duty as the obligation that limits personal gratification
contención -- IND-low -- containment of impulse as a social and moral virtue
sobriedad -- IND-low -- sobriety as restraint in the face of available pleasure
aguante -- IND-low -- endurance as the Mexican-specific virtue of bearing difficulty without complaint; load-bearing cultural word
silencio -- IND-low -- silence as the restraint of expression, what is not said or shown
recato -- IND-low -- modesty and restraint in personal conduct, especially in public register
moderación -- IND-low -- moderation as the deliberate limiting of indulgence
renuncia -- IND-low -- renunciation as the active giving up of what could be taken
templanza -- IND-low -- temperance as the classical virtue of restraint over desire

---

## Section 7: Decision Logs

**Country:** Mexico
**Dimension:** PDI
**Polarity:** HIGH
**Declared score:** 81

Multi-word entries: none
Cross-country root flags: respeto -- conceptual cognate with Spain's cultural usage; no Spain PDI bag in project. Retained.
Root-proximity flags: cargo appears in IDV-low candidate list conceptually for other countries; here assigned PDI-high for title-placement register. Logged.
Register spread: legal/bureaucratic 2 (autoridad, cargo), procedural 1 (mando), social-cultural 5 (respeto, patrón, compadrazgo, señor, antigüedad), everyday 2 (jerarquía, obediencia)
Persona-anchor words: none (no persona files yet)
NOTE: señor replaces don following Round 1 review. Polysemy blocker on don resolved.

---

**Country:** Mexico
**Dimension:** PDI
**Polarity:** LOW
**Declared score:** 81

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: acceso could fire in UAI-low (access as flexibility). Assigned PDI-low: access as structural equality, not procedural flexibility. Logged.
Register spread: legal/bureaucratic 1 (participación), procedural 2 (acuerdo, consenso), social-cultural 4 (diálogo, apertura, voz, criterio), everyday 3 (horizontalidad, colega, acceso)
Persona-anchor words: none
NOTE: acceso replaces iniciativa following Round 1 review. Within-country collision with IDV-high resolved.

---

**Country:** Mexico
**Dimension:** IDV
**Polarity:** LOW
**Declared score:** 30

Multi-word entries: none
Cross-country root flags: familia -- conceptual overlap with Spain position file. Register distinction: Mexican familia is gravitational and cosmic; Spanish familia is relational and protective. Documented in Section 4. Retained.
Root-proximity flags: vínculo proximity to MAS-low (relational vocabulary). Assigned IDV-low: bond as collective structure, not care. Logged.
Register spread: legal/bureaucratic 0, procedural 1 (compromiso), social-cultural 6 (familia, comunidad, lealtad, pertenencia, hermandad, red), everyday 3 (nosotros, grupo, vínculo)
Persona-anchor words: none
FLAG: nosotros -- borderline pronoun. Native-speaker confirmation required before status moves from draft to reviewed. Does nosotros function as culturally marked identity vocabulary in Mexican prose rather than firing as a grammatical pronoun?

---

**Country:** Mexico
**Dimension:** IDV
**Polarity:** HIGH
**Declared score:** 30

Multi-word entries: none
Cross-country root flags: autonomía -- Spain position file carries autonomía conceptually but not as bag word. Retained.
Root-proximity flags: iniciativa proximity to former PDI-low slot. Resolution documented in conflict table. iniciativa retained here as personal agency vocabulary.
Register spread: legal/bureaucratic 0, procedural 1 (elección), social-cultural 4 (identidad, trayectoria, camino, voluntad), everyday 5 (individuo, autonomía, independencia, iniciativa, privacidad)
Persona-anchor words: none

---

**Country:** Mexico
**Dimension:** UAI
**Polarity:** HIGH
**Declared score:** 82

Multi-word entries: none
Cross-country root flags: norma, protocolo, procedimiento -- conceptual parallels with German and Polish cultural usage; no project bags for those countries' UAI dimension. No collision.
Root-proximity flags: orden proximity to PDI-high structurally. Assigned UAI-high: order as reduction of uncertainty, not as command hierarchy. Logged.
Register spread: legal/bureaucratic 4 (norma, reglamento, documento, formalidad), procedural 3 (protocolo, procedimiento, trámite), social-cultural 1 (certeza), everyday 2 (orden, estructura)
Persona-anchor words: none
FLAG: trámite -- highly load-bearing for UAI-high. Native-speaker check: does trámite carry neutral procedural meaning or primarily negative connotation in contemporary Mexican usage? If primarily negative, it scores uncertainty avoidance but through frustration register which may skew.

---

**Country:** Mexico
**Dimension:** UAI
**Polarity:** LOW
**Declared score:** 82

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: flexibilidad proximity to IDV-high conceptually. Assigned UAI-low: adaptive response to ambiguity, not individual autonomy. Logged.
Register spread: legal/bureaucratic 0, procedural 2 (adaptación, flexibilidad), social-cultural 3 (improvisación, inventiva, ingenio), everyday 5 (informalidad, riesgo, intuición, soltura, tanteo)
Persona-anchor words: none

---

**Country:** Mexico
**Dimension:** MAS
**Polarity:** HIGH
**Declared score:** 69

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: rendimiento proximity to UAI-high (procedural output). Assigned MAS-high: performance as achievement measure, not procedural compliance. Logged.
Register spread: legal/bureaucratic 0, procedural 2 (rendimiento, competencia), social-cultural 5 (éxito, ambición, triunfo, reconocimiento, ascenso), everyday 3 (logro, empuje, esfuerzo)
Persona-anchor words: none
FLAG: empuje -- Mexican-specific register for drive and initiative as energy. Verify empuje reads as culturally marked in Mexico rather than as a generic Spanish word. Native-speaker check required.

---

**Country:** Mexico
**Dimension:** MAS
**Polarity:** LOW
**Declared score:** 69

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: apoyo proximity to IDV-low (collective support). Assigned MAS-low: relational care, not collective belonging. Logged.
Register spread: legal/bureaucratic 0, procedural 1 (cooperación), social-cultural 6 (cuidado, comprensión, armonía, empatía, generosidad, acompañamiento), everyday 3 (modestia, apoyo, bienestar)
Persona-anchor words: none
FLAG: acompañamiento -- Mexican pastoral and social register claim. Verify this word functions in secular cultural prose as naturally as in religious or therapeutic contexts.

---

**Country:** Mexico
**Dimension:** LTO
**Polarity:** LOW
**Declared score:** 24

Multi-word entries: none
Cross-country root flags: tradición -- skill hard rule: tradition is LTO-low explicitly. Confirmed. memoria -- no collision in existing bags.
Root-proximity flags: legado proximity to IDV-low (heritage as collective). Assigned LTO-low: legacy as temporal, what the past leaves in the present. Logged.
Register spread: legal/bureaucratic 0, procedural 0, social-cultural 7 (tradición, herencia, costumbre, ancestro, memoria, rito, legado), everyday 3 (presente, origen, raíz)
Persona-anchor words: none
OBSERVATION: 0 legal/bureaucratic and 0 procedural is culturally correct for LTO-low. Culture files should carry these words in social-cultural and everyday prose sections.

---

**Country:** Mexico
**Dimension:** LTO
**Polarity:** HIGH
**Declared score:** 24

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: proyecto proximity to IDV-high (personal project). Assigned LTO-high: organized forward-looking endeavor, not personal trajectory. Logged.
Register spread: legal/bureaucratic 1 (inversión), procedural 3 (planificación, estrategia, previsión), social-cultural 3 (continuidad, horizonte, formación), everyday 3 (futuro, proyecto, acumulación)
Persona-anchor words: none

---

**Country:** Mexico
**Dimension:** IND
**Polarity:** HIGH
**Declared score:** 97

Multi-word entries: none
Cross-country root flags: fiesta -- no collision in existing bags. Load-bearing at score 97.
Root-proximity flags: alegría proximity to MAS-low (wellbeing, armonía register). Assigned IND-high: joy as gratification-state, not relational harmony. Logged.
Register spread: legal/bureaucratic 0, procedural 0, social-cultural 5 (fiesta, música, baile, humor, gozo), everyday 5 (alegría, disfrute, placer, comida, sabor)
Persona-anchor words: none
NOTE: Score 97 is the highest IND score in the project. Extreme-register vocabulary is appropriate and required by skill calibration table. Fiesta is the institutional anchor. Gozo carries spiritual-physical register that distinguishes Mexican indulgence from mere hedonic pleasure.
FLAG: gozo -- carries both secular pleasure and spiritual joy. Native-speaker check: does gozo appear naturally in everyday cultural prose or primarily in literary and religious contexts?

---

**Country:** Mexico
**Dimension:** IND
**Polarity:** LOW
**Declared score:** 97

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags: deber proximity to LTO-high (obligation as investment). Assigned IND-low: duty as restraint on gratification, not future orientation. Logged. sacrificio proximity to LTO-low culturally. Assigned IND-low: sacrifice as active renunciation of pleasure, not temporal anchoring. Logged.
Register spread: legal/bureaucratic 0, procedural 1 (contención), social-cultural 6 (sacrificio, sobriedad, aguante, recato, renuncia, templanza), everyday 3 (deber, silencio, moderación)
Persona-anchor words: none
NOTE: aguante is the most culturally specific word in this bag. It carries the Mexican register of dignified endurance under pressure with no direct equivalent in other project bags.
FLAG: recato -- carries modesty and restraint with a specifically feminine historical register in Mexican usage. Native-speaker check: does recato apply equally across genders in contemporary Mexican cultural prose or does it carry a marked feminine connotation that would skew scoring?

---

## Section 8: Native-Speaker Check Items

Before status moves from draft to reviewed, the following words require native-speaker confirmation:

1. nosotros (IDV-low): does nosotros function as culturally marked identity vocabulary in Mexican prose or does it fire too broadly as a grammatical pronoun?
2. trámite (UAI-high): does trámite carry neutral procedural meaning or primarily negative connotation in contemporary Mexican usage?
3. aguante (IND-low): does aguante function naturally in written cultural prose or primarily in colloquial speech?
4. recato (IND-low): does recato apply equally across genders in contemporary Mexican cultural prose or carry a marked feminine connotation?
5. empuje (MAS-high): does empuje read as culturally marked in Mexico or as generic Spanish?
6. gozo (IND-high): does gozo appear naturally in everyday cultural prose or primarily in literary and religious contexts?
7. acompañamiento (MAS-low): does acompañamiento function in secular cultural prose as naturally as in religious or therapeutic contexts?
8. señor (PDI-high): does señor carry the honorific placement register unambiguously in contemporary Mexican formal prose without competing readings?

---

*hofstede_decisions.md -- Mexico*
*KAI HACKS AI -- v0.1.0*
*2026-05-16*
