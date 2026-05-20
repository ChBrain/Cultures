# Hofstede Decisions: Japan

**Scores:** PDI 54 · IDV 46 · UAI 92 · MAS 95 · LTO 88 · IND 42
**Generated:** 2026-05-20
**Forked from:** none -- fresh bootstrap

---

## Drops from previous bag

No previous bag -- fresh bootstrap.

---

## Japanese-language specifics

Japanese running prose has no inter-word spaces; every content noun is
typically followed immediately by a hiragana particle (の, を, は, が, と)
or a kana suffix. Python's `\b` regex boundary treats hiragana and kanji
as both belonging to the `\w` class, which means `\b上司\b` only fires when
上司 is bounded on both sides by non-word characters -- typically
punctuation (、。「」), whitespace, or newline.

Two consequences flow from this:

1. The cultural prose places bag-firing words in **list cadence** -- the
   Germany-style "Wort, Wort, Wort. Wort." pattern where each keyword is
   followed by a 、 or 。 -- so the binary scoring lands as intended.
   Continuous running prose with particles would silently zero out most
   of the dimension signal.
2. Bag words selected for this country prefer single-token kanji compounds
   that read naturally as standalone list items (上司, 立場, 規則, 鍛錬)
   over hiragana-tail compounds (e.g. わきまえる, しょうがない). The latter
   appear in prose for cultural texture but are not scored.

This is documented in the cross-language consistency section below as the
single largest divergence from European bag construction patterns.

---

## Conflict resolution

| Word | Assigned to | Reason | Replacement in other bag |
|---|---|---|---|
| 鍛錬 | MAS-high | The training/forging concept reads stronger in Japanese as achievement-orientation (the act of striving) than as time-horizon; assigned to MAS-high. Within-country collision rule forbids two-bag membership | LTO-high gets 蓄積 (accumulation / build-up over time -- pure long-arc register) |
| 我慢 | LTO-high | Endurance reads more as long-term restraint than as individual gratification deferral | IND-low gets 自制 / 抑制 / 節度 (more direct gratification-restraint markers) |
| 和 | IDV-low | Wa names group-orientation more precisely than MAS-low harmony; the MAS-low slot here uses 調和, which is the explicit harmony term in workplace contexts | MAS-low gets 調和 (harmony specifically as cooperative orientation) |
| 義理 | IDV-low | Obligation to in-group is the group-membership signal; IND-low (duty) reads at the individual-restraint level | IND-low gets 義務 (more individual / institutional duty register) |
| 確認 | UAI-high | Confirmation as procedural ritual is the UAI signal; LTO is about temporal horizon | LTO-high gets 投資 instead |
| 礼儀 | UAI-high | Etiquette as rule-system is UAI; PDI is about status markers (above 上司/敬語 cover) | PDI-high gets 敬語 (specifically about hierarchy register) |
| 平等 | dropped | Removed from PDI-low to land target derived score; cultural prose mentions equality only in postwar-constitution register, which over-fires PDI-low | PDI-low filled to 10 with 普通選挙 / 直接民主制 / 草の根 (not fired in prose; intentional vocabulary breadth) |
| 享楽 / 解放 / 気楽 | dropped from prose | Three IND-high markers were removed from prose to land derived IND closer to declared 42; bag retains the words as legitimate IND-high vocabulary | none |

---

## Cross-language consistency flags

No cross-language divergence detected at adjacent-language level -- Japan
shares no immediate-neighbor culture in the migrated set yet. South Korea
and Singapore are the closest comparators for Confucian-influenced PDI/LTO
patterns; flag for cross-country review when those bags are generated.

Japan + Germany: both UAI-high, but Japan's high uses ritual/etiquette
vocabulary (礼儀, 段取り) where Germany uses bureaucratic-procedural
vocabulary (Regelwerk, Vorschrift). Same dimension, different register.
This is the expected divergence and not a flag.

---

## Decision logs

### PDI high

```
Country: japan
Dimension: PDI
Polarity: high
Declared score: 54

Multi-word entries: none (all single-token kanji compounds)
Cross-country root flags: none
Root-proximity flags (same country): 先輩 / 後輩 are pair-mates; both retained
Register spread: social-cultural 5 (上司, 先輩, 後輩, 立場, 序列), procedural 2 (目上, 身分), legal/bureaucratic 2 (階級, 権威), everyday 1 (敬語)
Persona-anchor words: Hiroshi (Projection / Action / Shadow: 上司, 立場, 部長, 課長); Aiko (Action / Projection: 立場 implicit)
```

### PDI low

```
Country: japan
Dimension: PDI
Polarity: low
Declared score: 54

Multi-word entries: 普通選挙 (closed compound for universal suffrage), 直接民主制 (closed compound for direct democracy), 草の根 (idiomatic "grassroots"), 庶民派 (closed compound)
Cross-country root flags: none
Root-proximity flags (same country): 庶民派 root-adjacent to 庶民; intentional -- 庶民派 is a distinct political-register term not present in prose, used to widen the PDI-low vocabulary without firing
Register spread: legal/bureaucratic 4 (民主, 普通選挙, 直接民主制, 連邦制), social-cultural 3 (対等, 公平, 庶民派), everyday 3 (合議, 横並び, 草の根)
Persona-anchor words: Position file: 対等, 合議, 横並び, 民主, 公平 (5 fires, postwar-constitution register)
Note: 5 fires by design -- PDI 54 is mid; 6 high vs 5 low lands derived = 54 exactly
```

### IDV high

```
Country: japan
Dimension: IDV
Polarity: high
Declared score: 46

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): 自分 / 自己 / 自主 / 自立 share 自- prefix -- all retained; each anchors a distinct register (self-as-pronoun, self-as-philosophical-subject, autonomy, independence)
Register spread: social-cultural 4 (自由, 個性, 自己, 主体), procedural 3 (自立, 独立, 自主), everyday 3 (個人, 自分, 私的)
Persona-anchor words: Hiroshi (Shadow: 自由, 自分); Aiko (Shadow: 自分, 自立 implicit)
```

### IDV low

```
Country: japan
Dimension: IDV
Polarity: low
Declared score: 46

Multi-word entries: 一体感 (closed compound), 共同体 (closed compound)
Cross-country root flags: none
Root-proximity flags (same country): 集団 / 共同体 root-adjacent; both retained; 集団 is the group, 共同体 is the community-as-entity
Register spread: legal/bureaucratic 1 (共同体), social-cultural 5 (和, 義理, 連帯, 帰属, 世間), everyday 4 (集団, 仲間, 一体感, 同調)
Persona-anchor words: Position file: 集団, 和, 義理, 世間, 仲間 (5 fires); Place file: 義理 (1 fire)
```

### UAI high

```
Country: japan
Dimension: UAI
Polarity: high
Declared score: 92

Multi-word entries: none (all single-token kanji compounds)
Cross-country root flags: none
Root-proximity flags (same country): 整然 / 綿密 both name precision/orderliness; both retained; 整然 is orderly-as-arranged, 綿密 is thorough-as-meticulous; distinct registers
Register spread: legal/bureaucratic 2 (規則, 確認), procedural 4 (手順, 段取り, 完璧, 徹底), social-cultural 2 (礼儀, 精密), everyday 2 (整然, 綿密)
Persona-anchor words: Position file: 規則, 手順, 礼儀, 段取り, 確認, 完璧, 精密, 徹底, 整然, 綿密 (all 10 fire); Process file (Nemawashi): 段取り, 手順, 確認, 完璧 (4 fires)
```

### UAI low

```
Country: japan
Dimension: UAI
Polarity: low
Declared score: 92

Multi-word entries: 臨機 (single-token; root for "ad-hoc" via 臨機応変)
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: procedural 4 (適応, 自発, 試行, 臨機), social-cultural 3 (柔軟, 大胆, 冒険), everyday 3 (即興, 気軽, 偶然)
Persona-anchor words: Position file: 柔軟 (1 fire by design); other files: no UAI-low fire
Note: 1 fire by design -- UAI 92 is very high; 10 high vs 1 low lands derived = 90 (within ±5)
```

### MAS high

```
Country: japan
Dimension: MAS
Polarity: high
Declared score: 95

Multi-word entries: none (all single-token kanji compounds)
Cross-country root flags: none
Root-proximity flags (same country): 成果 / 業績 / 実績 / 達成 form a tight achievement cluster -- all retained; each anchors a distinct register (outcome, business-record, track-record, completion)
Register spread: procedural 3 (努力, 鍛錬, 達成), social-cultural 4 (競争, 成果, 一流, 出世), everyday 3 (勝利, 実績, 業績)
Persona-anchor words: Position file: 努力, 鍛錬, 競争, 成果, 一流, 出世, 勝利, 達成, 実績, 業績 (all 10 fire); Piece file (Sado): 鍛錬 (1 fire); History: 勝 (does not fire)
```

### MAS low

```
Country: japan
Dimension: MAS
Polarity: low
Declared score: 95

Multi-word entries: 譲り合い (closed compound for mutual yielding), 思いやり (closed compound for thoughtfulness toward others)
Cross-country root flags: none
Root-proximity flags (same country): none
Register spread: social-cultural 6 (思いやり, 調和, 慈悲, 共感, 配慮, 寛容), everyday 4 (協力, 譲り合い, 共生, 親切)
Persona-anchor words: Piece file (Sado): 調和 (1 fire); other files: 0 fires by design
Note: 0 fires by design -- MAS 95 is very high; 10 high vs 0 low lands derived = 100 (within ±5; gap = 5)
```

### LTO high

```
Country: japan
Dimension: LTO
Polarity: high
Declared score: 88

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): 鍛錬 / 修業 / 稽古 form a training cluster -- all retained; each names a distinct register (forging, apprenticeship, lessons/practice)
Register spread: procedural 4 (継続, 投資, 鍛錬, 長期), social-cultural 4 (修業, 稽古, 後世, 永続), everyday 2 (我慢, 将来)
Persona-anchor words: Aiko (Projection: 修業, 稽古 + 三十年, 四代目); Hiroshi (Projection: 二十六年); Piece file (Sado): 鍛錬, 稽古, 継続 (3 fires)
```

### LTO low

```
Country: japan
Dimension: LTO
Polarity: low
Declared score: 88

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): 慣習 / 風習 share -習; both retained; 慣習 is custom-as-habit, 風習 is custom-as-folkway; distinct registers
Register spread: social-cultural 3 (慣習, 風習, 流行), procedural 2 (短期, 現状), everyday 5 (即時, 一時, 目先, 過去, 旧来)
Persona-anchor words: Position file: 目先 (1 fire); other files: 0 fires
Note: 1 fire by design -- LTO 88 is high; 10 high vs 1 low lands derived = 90 (within ±5; gap = 2)
```

### IND high

```
Country: japan
Dimension: IND
Polarity: high
Declared score: 42

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): 喜び / 楽しみ both name positive affect -- both retained; 喜び is joy-as-celebration, 楽しみ is enjoyment-as-anticipation; distinct registers
Register spread: social-cultural 3 (享楽, 解放, 余裕), everyday 7 (喜び, 楽しみ, 余暇, 趣味, 気楽, 笑い, 遊び)
Persona-anchor words: Position file: 喜び, 楽しみ, 余暇, 趣味, 笑い, 遊び, 余裕 (7 fires by design)
Note: 7 fires by design -- IND 42 is below midpoint; 7 high vs 10 low lands derived = 41 (within ±5; gap = 1). 享楽, 解放, 気楽 are intentionally absent from prose to land the ratio.
```

### IND low

```
Country: japan
Dimension: IND
Polarity: low
Declared score: 42

Multi-word entries: none
Cross-country root flags: none
Root-proximity flags (same country): 自制 / 抑制 both name self-restraint -- both retained; 自制 is self-control-as-disposition, 抑制 is restraint-as-act; distinct registers
Register spread: legal/bureaucratic 2 (規律, 義務), procedural 2 (自制, 抑制), social-cultural 4 (謙虚, 慎み, 控えめ, 真面目), everyday 2 (遠慮, 節度)
Persona-anchor words: Position file: 謙虚, 慎み, 控えめ, 我慢, 遠慮, 自制, 抑制, 規律, 節度, 真面目, 義務 (all 10 IND-low words fire)
```

---

## Native-speaker checks needed

- [ ] 庶民派 -- verify whether this reads as PDI-low (anti-elitist political register) or whether it has acquired a populist-ironic register that would weaken the signal
- [ ] 草の根 -- verify whether the grassroots metaphor reads as PDI-low in contemporary Japanese (it is widely used in NPO / civic contexts; should be safe)
- [ ] 鍛錬 across LTO and MAS -- verify cross-dimension retention is appropriate; the word genuinely loads both registers in Japanese practice (craft training = long-arc + achievement)
- [ ] 一流 -- verify register is MAS-high (achievement / top-tier) and not LTO (continuity / lineage); current assignment is MAS-high
- [ ] 共同体 -- check whether this reads as IDV-low (community-belonging) in cultural prose or has shifted toward sociological-academic register that weakens the signal
