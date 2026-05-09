---
name: khai-create-hofstede-bag
description: Use this skill to generate Hofstede keyword bags for a single country culture. Triggers on "generate a bag", "keyword bag for", "Hofstede bag", "bag for [country]", "bootstrap [country]", or any request to produce the 10-word scoring vocabulary for a culture's Hofstede dimension slots. The skill takes a country, its declared Hofstede scores, and any existing bags as input. It produces all 12 bags (6 dimensions x 2 polarities) with per-word justification, conflict resolution, drop enumeration, and cross-language consistency flags. Use this skill before writing any culture files — the bag is the spec the files are written to embody.
compatibility: Designed for Claude.ai and Claude Code. No scripts or external tools required -- pure language task.
metadata:
  author: KAI HACKS AI
  version: "0.9.1"
  project: Cultures
---

# khai-create-hofstede-bag

Generate defensible Hofstede keyword bags for a single country culture. Always produces all 12 slots in one session.

## Required inputs

Before starting, you need:

- **Country name** (e.g. `Ireland`, `Netherlands`, `Poland`)
- **Region** (e.g. `europe`, `africa`, `asia`, `americas`, `oceania`) -- used to construct the output path `regions/<region>/<country>/`
- **Target language** for the bag (e.g. `nl` for Netherlands, `en` for Ireland, `de` for Germany). The bag's keywords MUST be written in this language. The language of the bag is the language of the country's `culture_*.md` content files. A Dutch culture file scored against an English bag yields zero matches.
- **Declared Hofstede scores**: PDI, IDV, UAI, MAS, LTO, IND
- **Existing bags** for this country, if redrafting
- **Sibling country bag** if this country shares a language with an existing culture -- fork from the sibling whose Hofstede scores AND cultural register most closely match
- **Culture content files** if available, for persona-anchor scanning

If any required input is missing, refuse to start and request it.

**Per-country, not per-language.** Bags belong to a country culture, not to a language. Netherlands and Belgium each get their own bag even though both use Dutch. Ireland gets its own English bag distinct from any UK or US English bag. Hofstede scores are per-country; bags follow. When a country shares a language with an existing sibling, fork from the sibling whose Hofstede scores AND cultural register most closely match the target -- not just the geographic neighbor or the language match. Document the fork choice with reasoning.

**Inherited-word re-check.** When forking from a sibling, re-run the full per-keyword rule check on every inherited word. Sibling bags may contain words that were recommended informally and never received a hard-rule pass. Treat every inherited word as a new candidate until it passes all criteria.

## What the bag is

A bag is exactly 10 words in the target language for this country. Each word signals the target polarity of the target dimension. Scoring is binary: a word either appears in the culture files or it does not. Each word that appears scores 10 points toward that dimension slot. The bag is the contract the culture files are written to fulfill.

## Dimension polarity reference

| Dimension | HIGH signals | LOW signals |
|---|---|---|
| **PDI** | hierarchy, deference, status, formal authority, rank | flat structure, equality of standing, informal relations, merit over rank -- NOT individual rights or autonomy (those are IDV-high) |
| **IDV** | personal autonomy, self-direction, individual choice, independence | group loyalty, collective harmony, in-group, shared identity |
| **UAI** | rules, structure, precision, planning, predictability, order | flexibility, improvisation, ambiguity tolerance, risk, spontaneity |
| **MAS** | competition, achievement, assertion, winning, ambition | cooperation, care, modesty, relationship, compassion |
| **LTO** | future planning, continuity, sustained investment, perseverance | present-focus, immediate result, traditional anchoring -- **tradition is LTO-low, not LTO-high** |
| **IND** | enjoyment, freedom, gratification, pleasure | restraint, discipline, duty, obligation, self-control |

## Score-band calibration

| Score band | Bag character |
|---|---|
| 0-30 (very low) | Strong opposing-polarity words, no hedging |
| 31-50 (low / moderate-low) | Mostly polarity words, some everyday register |
| 51-65 (moderate to moderate-high) | Process-words, structure as method, no extremes |
| 66-80 (high) | Balanced: clear polarity plus everyday register |
| 81-100 (very high) | Compulsion-words, strong polarity, include extreme-register vocabulary. A bag at 93 reads differently from a bag at 65 -- the distance is real. |

Score near 50: both bags still require exactly 10 words each. Medium-ness expresses itself through matched content coverage, not reduced bag size. Do not split to 5+5.

## Generation procedure

### Step 1: Calibrate all 12 slots

For each of the 6 dimensions, note polarity and score band. Identify dominant bag (country sits here) and opposing bag (country does not display this polarity). Both must be drafted. For opposing bags, use sibling country bags for the same polarity as cross-reference. State this in the decision log.

### Step 2: Scan for persona anchors

If culture content files exist, scan persona and position files for distinctive descriptors. Words used as persona anchors are bag-mandatory candidates unless they violate a hard rule.

### Step 3: Draft all 12 bags simultaneously

15-20 candidates per slot. Include:

- Words that directly name the concept
- Words that enact the concept without naming it (behavioral vocabulary)
- Institutionally anchored words that have become culturally load-bearing
- Everyday vocabulary native speakers associate with the cultural value
- For opposing bags: vocabulary from sibling countries that display the polarity

### Step 4: Conflict resolution pass

For every word appearing in two draft bags: assign to one, replace in the other. Log every resolution.

### Step 5: Filter each bag

Apply in order. Eliminate any word that fails any criterion:

1. **Unambiguous polarity**: signals this polarity only, not both
2. **PDI-low / IDV-high guardrail**: words implying individual standing against collective or authority are IDV-high, not PDI-low. PDI-low describes flat structures and equal relationships, not individual assertion.
3. **No within-country collision**: does not appear in any other dimension's bag for this country
4. **No cross-country opposing-polarity collision (same root, same dimension)**: flag for review and resolution -- not automatic discard, but must be documented.
5. **Cross-country conceptual collision (same root, different dimension)**: flag and document per-country register reasoning. The same root in two countries scoring different dimensions means the validator assigns the same cultural concept to different dimensions across countries -- document why the registers genuinely differ.
6. **Root-proximity flag (same country)**: record in decision log when a word shares a root with a keyword in another dimension's bag for the same country.
7. **Conceptual overlap check**: ask whether this word scores a cultural concept that another bag already scores with different vocabulary. Flag; drop if a less-overlapping replacement exists.
8. **Same-dimension opposite-polarity disqualifier**: if a word has plausible readings for both high and low on the same dimension, the word is bag-disqualifying. This is categorically different from cross-dimension dual readings -- a word signaling two different dimensions can be placed in one with documentation. Same-dimension ambiguity means the matcher fires for the wrong polarity in some content. No contextual argument overrides this. If unsure, require native-speaker corpus evidence before placing.
9. **Dialect-specific polarity placements need corpus gating**: when a word's placement depends on a dialect-specific reading that diverges from the standard-language reading, etymological reasoning alone is insufficient. Require contemporary corpus evidence that the dialect reading dominates in cultural prose. If no corpus evidence available, treat as unsafe and use a standard-reading word instead.
10. **Cross-register sibling scan**: when flagging a word for cross-dimension adjacency, scan the full bag for words in the same register or concept-cluster and apply the same flag. Do not terminate with a flag on one word and silence on a register-sibling in the same bag.
11. **Lemma form**: use the base/dictionary form. Lemma swaps are not no-ops -- `care` and `caring` hit different content. Log them.
12. **Common-word denylist (hard rule, no exceptions)**:
   - Pronouns: `we`, `I`, `wij`, `ik`, `ich`, `vi`, `jeg`, and equivalents
   - Articles, prepositions, conjunctions
   - Deictics: `now`, `here`, `nu`, `da`, `jetzt`, and equivalents
   - Top-200 frequency words for the language
   - Polysemous high-frequency words in English: `flat`, `open`, `own`, `shared`, `drive`, `past`, `support`, `together`
   - No contextual override. The matcher does not see context.

### Step 6: Rank and select 10

Rank by cultural specificity. Prefer words that:

- Are uniquely associated with this country's expression of the dimension
- Would not appear in a generic text about the dimension
- Would be recognized by a native speaker as culturally marked

**Register diversity check.** Group by register: legal/bureaucratic, procedural, social-cultural, everyday. If any group is empty or any group holds more than 5 words, rebalance.

**Hyphenated compound limit.** Maximum one hyphenated compound per bag. Two `self-` compounds is redundancy. Flag all multi-word entries in the decision log with justification that no single-word equivalent exists.

Select exactly 10. If fewer than 10 survive, flag the shortfall.

## Output structure

Produce all sections below. Do not terminate until all are present.

### Section 1: Draft pass

All 12 draft bags.

### Section 2: Conflict resolution table

Every word that fired in two draft bags:
```
word -- assigned to [bag] -- reason -- replacement in other bag
```

### Section 3: Drops from previous bag

**Mandatory when redrafting or forking.** For every word in the previous bag not in the new bag:
```
word -- dropped -- rule-cited reason
```

Valid reasons:
- "Common-word denylist violation"
- "Cross-country opposing-polarity collision with [country] [dimension]"
- "Cross-bag conflict -- moved to [other dimension]"
- "Within-country collision with [other bag]"
- "Lemma swap -- replaced by [new lemma form]"
- "Polysemy concern -- replaced by [less ambiguous word]"
- "Redundant with [other word in same bag]"
- "Cultural register concern -- flagged for native check"

If no words dropped: "No drops from previous bag."
If fresh bootstrap: "No previous bag -- fresh bootstrap."
If forking from sibling: "Forked from [sibling]; divergences below." Then log every divergence.

If you cannot articulate a rule-cited reason, restore the word.

### Section 4: Cross-language consistency flags

For every word in the final bags, check all other countries' bags for the same dimension. List only divergent calls:
```
word (this country, this dimension, this polarity) diverges from cognate in [other country, other dimension/polarity] -- per-country register reasoning
```
Same-direction calls do not need listing. If no divergent calls: "No cross-language divergence detected."

### Section 5: Final bags

All 12 bags. One word per line. No numbering, no decoration.

### Section 6: Per-word justification

One line per word: `word -- dimension signal -- why this word in this country`
One clause. For the hard reviewer.

### Section 7: Decision logs (per bag)

```
Country: [country]
Dimension: [dimension]
Polarity: [polarity]
Declared score: [score]

Multi-word entries: [none | list each with matching consequence note]
Cross-country root flags: [none | list]
Root-proximity flags (same country): [none | list]
Register spread: legal/bureaucratic N, procedural N, social-cultural N, everyday N
Persona-anchor words: [none | list with source file]
```

### Section 8: Native-speaker check items

Flag any word where:
- Register is uncertain for this specific country
- Compound form may not match natural usage
- Political or cultural connotations may have shifted since 2020
- Word is from a regional variety that may differ from the canonical language form

## Quality rules

- **Exactly 10 words per bag.** Not 9, not 11.
- **12 bags total.** No skipping the opposing-polarity bag.
- **Lemma form always.** `langfristig` not `langfristige`. `restraint` not `restrained`.
- **No proper nouns** unless the proper noun has become a common cultural verb or adjective. Flag borderline cases.
- **No English borrowings** unless genuinely in cultural use in this specific country.
- **Silent drops are unsafe.** Every word from the previous bag must appear in the new bag or in the drop log. No exceptions. This is the LLM-changes-the-rules vector.
- **Drop reasoning must be rule-compliant.** Not "generic" alone -- follow with the specific rule it violates.
- **Rebalance mode**: if culture files exist, scan for words functioning as defining descriptors in persona and position files. Those words are bag-mandatory candidates unless they violate a hard rule.
- **No em-dashes in output.** Use colons or line breaks.

## Gotchas

1. `tradition` is LTO-low, not LTO-high.
2. Common-word denylist violations to watch in any language: deictics, pronouns, high-frequency everyday words, and polysemous words where the cultural reading is real but the matcher fires on all readings indiscriminately.
3. Lemma swaps are not no-ops. Two different forms of the same word hit different content.
4. Polysemy alone disqualifies. A word with 4 unrelated common meanings cannot anchor a cultural signal.
5. Hyphenated compounds: max one per bag.
6. Words with politically loaded connotations in contemporary usage need native-speaker register checks before placement.
7. Institutionally anchored words are valid when culturally load-bearing. Flag in decision log.
8. Score-band calibration matters. Do not draft a very-high score like a moderate score.
9. Per-country, not per-language. Fork sibling bags explicitly and log every divergence.

## Refusal conditions

Do not terminate if any of the following are unresolved:

- Fewer than 12 bags drafted
- Any bag has fewer or more than 10 words
- A common-word denylist violation persists in the final output
- **Bag keywords are not in the target language for the country (the language of its `culture_*.md` files). A Dutch country with English keywords scores zero matches against Dutch content. This rule overrides every "the cultural concept is universal" argument -- the matcher does exact-word string comparison.**
- Silent drops from previous bag without drop-log entries
- A cross-country opposing-polarity collision is unresolved
- The country shares a language with a sibling and you did not fork explicitly
- The drop log section is absent when a previous bag exists

## Output files

When file creation is available, write two files into the country's folder under `regions/`. Use the **lowercase country slug** (no spaces, no diacritics) for the country folder:

**Single-language country** (one bag file):
```
regions/<region>/<country>/hofstede_bag.yaml
regions/<region>/<country>/hofstede_decisions.md
```

**Multilingual country** (one bag file per language; e.g. Belgium with `nl` and `fr`, Switzerland with `de`/`fr`/`it`/`rm`):
```
regions/<region>/<country>/hofstede_bag_<lang>.yaml
regions/<region>/<country>/hofstede_bag_<other_lang>.yaml
regions/<region>/<country>/hofstede_decisions.md
```

The country folder names the country; the bag file does not need the country name in it. The language suffix is used only when the country has more than one language bag.

If the `regions/<region>/<country>/` folder does not exist yet (the country has no culture content), create the folder and the bag/decisions files within it. The bag is the spec the culture files will be written to embody, so the bag may precede the content files.

Bag changes land on `feat/culture-<country>` branches per the branch-scope guard. Update `data/hofstede_bag_locks.yaml` in the same commit as the bag YAML; that file is in `SAFE_PATTERNS` for culture branches specifically so the lock entry can ride alongside the bag.

Load [assets/hofstede_bag_template.yaml](assets/hofstede_bag_template.yaml) and fill in the 12 bags. Load [assets/hofstede_decisions_template.md](assets/hofstede_decisions_template.md) and fill in all sections.

If file creation is not available, the session output is the deliverable. The human packages the files from the session output.

## After the bags

The bags are ready for human review. A hard reviewer may challenge any word. The decision log is the defense. If a word is replaced, the log records the swap and reason.

Once approved, the bags are the scoring contract. Culture files are written to carry these words naturally -- not as forced insertions, but as organic vocabulary that the dimension would generate.

---

*SKILL.md - khai-create-hofstede-bag*
*v0.9.1 - KAI HACKS AI / Cultures*
