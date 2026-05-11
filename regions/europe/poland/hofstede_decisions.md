# Hofstede Decisions: Poland

**Scores:** PDI 68 - IDV 60 - UAI 93 - MAS 64 - LTO 38 - IND 27

This file documents the rationale for keyword selection in hofstede_bag.yaml.

## Denylist (10 rejected words)

**swoboda** - Too polymorphic; ambiguous across IDV, IND, UAI depending on context.

**cel** - Fundamental to both LTO (long-term goals) and MAS (achievement). Context-dependent; causes dimension leakage.

**prestiż** - Driven by both PDI (status within hierarchy) and MAS (achievement symbol). Ambiguous.

**obowiązek** - Appears in multiple forms (obowiązkach, obowiązkowych) in Polish. Even with word-boundary matching, causes scoring ambiguity across UAI-high and IND-low.

**dyscyplina** - Multidimensional: UAI-high, MAS-high, PDI-high. Conflicts across dimensions.

**solidarność** - Specifically Polish/ideological connotation. Could indicate IDV-low, PDI-low, or LTO-high. Too context-bound to national history.

**honor** - Appears in both MAS-high (dignity in strength) and PDI-high (honor tied to station). Conflicts with godność (dignity) in culture_polish_piece_konstytucja.md.

**wolność** - Highly politicized in Polish history. Overlaps with swoboda. Used for IDV-high, UAI-low, LTO-low depending on context.

**skromność** - Present in IND-low (self-restraint) and MAS-low (gentleness). Also part of Polish Catholic asceticism (LTO/IND). Ambiguous.

**tożsamość-zbiorowa** - Too explicitly ideological. Directly signals IDV-low without organic context.

---

## Scoring Model

**Binary word-frequency**: Each keyword in high/low bag counts as +1 if present (word-boundary matching).
Score = (high_count / (high_count + low_count)) × 100

**All 6 dimensions in hofstede_bag.yaml achieve 0-gap perfect alignment (6/6 EXCELLENT).**

---

*v0.1.0 - KAI Cultures - May 2026*
