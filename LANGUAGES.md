# LANGUAGES.md

*Language strategy and tracking for the Cultures project.*

## Strategy

Language is the primary gate for country "Unlocks." A culture is considered unlocked when it has a valid keyword bag in its primary language (facilitated by the `lingua` library or markers) allowing the aggregate Hofstede signal to be derived and validated.

## Pre-flight: check language enablement before starting a culture

**Before opening a `culture/<country>` branch, verify the country's primary language is already registered in `data/language_policy.yaml`.**

The check:

```bash
grep -c "^  - <language-slug>$" data/language_policy.yaml
# 1 means enabled; 0 means run the governance PR below first
```

If the language is NOT registered:

1. Open `governance/add-<language>-language` -> main.
   - Adds the slug to `data/language_policy.yaml` under `languages:`.
   - Verify `khai_tests/plugin.py` already maps the slug to a `lingua.Language` enum value (currently supported: catalan, danish, dutch, english, french, german, italian, japanese, norwegian, polish, portuguese, spanish, swedish). If your target language is outside that set, see section 7 (Workarounds).
2. Merge that PR.
3. Sync main -> culture/release via `sync/<name>` so the integration target has the new entry.
4. Only then open `culture/<country>` for the migration.

**Why it matters:** the static check `tests/test_language.py::test_readme_language_in_registry` asserts every country README's `**Language(s):**` slug appears in the policy. Skipping the pre-flight means the per-file lingua test passes (lingua itself supports the language) but the static registry test fails late in the CI cycle. The CI gate `language-preflight` (validate.yml) runs this same assertion as an always-on, fast pre-flight so the missing-language case surfaces in ~30s on every PR instead of after the components chain.

**Incident reference:** the Spain v2 migration (PR #166, 2026-05-14) skipped this check. Discovery happened after every other validator had passed; emergency PRs #167 + #168 unblocked the release at the cost of two extra round-trips.

## 1. Enabled Languages

The following languages are currently registered in `data/language_policy.yaml`:

- **English (en)**: Global fallback.
- **German (de)**: Tier 3 unlocked.
- **Danish (da)**: Tier 3 unlocked.
- **Dutch (nl)**: Tier 3 unlocked.
- **Polish (pl)**: Tier 3 unlocked.
- **Spanish (es)**: Tier 3 unlocked.

## 2. Implementation Tiers

To allow for parallel development, cultures move through three tiers of implementation:

| Tier | Name | Prose | Logic/Keywords | Status |
|---|---|---|---|---|
| 1 | **Locked** | None | None | No content. |
| 2 | **Soft Unlock** | English | English or Native | "Half-implemented" (Fallback). |
| 3 | **Hard Unlock** | Native | Native | Fully migrated. |

## 3. Unlocked Cultures (Tier 3)

Cultures with full v2 content and passing keyword-density validation:

- **Germany** (de)
- **Denmark** (da)
- **Netherlands** (nl)
- **Poland** (pl)
- **Spain** (es)
- **United Kingdom** (en - baseline)

## 4. Fallback Cultures (Tier 2)

Cultures currently utilizing English as a fallback for prose while maintaining regional logic:

- **Dominican Republic** (en prose / native logic pending)

## 5. Locked Cultures (Tier 1)

Approximately **190+ countries** are currently locked. The primary bottleneck is the lack of language-specific keyword bags (`hofstede_bag.yaml`) and mapping in the detection engine.

## 6. Enablement Roadmap (Macro-Language Priority)

To unlock the maximum number of regions with the fewest architectural changes, the following languages are prioritized for bag creation:

1. ~~**Spanish (es)**: Unlocks the majority of the Americas and Spain.~~ Done in PR #167.
2. **French (fr)**: Unlocks **France**, **Belgium**, **Switzerland**, and significant portions of **West/Central Africa**.
3. **Arabic (ar)**: Unlocks the **Middle East** and **North Africa** (MENA).
4. **Portuguese (pt)**: Unlocks **Brazil**, **Portugal**, **Angola**, and **Mozambique**.
5. **Mandarin (zh)**: Unlocks the primary population anchor in **Asia**.

## 7. Workarounds for Lingua Limitations

The `lingua` library supports ~75 languages. For cultures using languages outside this scope (e.g., specific African indigenous languages or Pacific dialects), the following workarounds apply:

- **Detection Markers**: Using unique character sets (e.g., `æ/ø/å` for Danish) or high-frequency functional words to trigger detection via `tests/validate_language.py`.
- **Manual Exceptions**: Adding specific proper nouns or markers to `regions/<region>/<country>/language_exceptions.txt`.
- **Hybrid Prose**: Maintaining position and persona files in English while using native-language keywords for scoring purposes, as allowed by `METHODOLOGY.md`.

## 8. Upstream Tracking (lingua)

The project relies on `pemistahl/lingua-py` for automated detection. To ensure the roadmap remains viable:

- **Periodic Audit**: Quarterly check of the Lingua supported languages list.
- **Extension Trigger**: If a prioritized roadmap language (e.g., Arabic or Mandarin) is added upstream, update `tests/validate_language.py` and `data/language_policy.yaml` to enable native detection.
- **Stagnation Pivot**: If `lingua` development stalls and a high-priority region remains "Locked," the project will shift to Phase 5 "Detection Markers" (regex-based triggers for high-frequency function words) as the primary detection logic for those regions.

### Current Constraints

As of May 2026, `lingua` supports 75 languages. Major gaps for this project include several high-density African and Oceanic indigenous languages.

---
*2026-05-14 | KAI HACKS AI | v0.2.1 | CC-BY-NC-4.0*
