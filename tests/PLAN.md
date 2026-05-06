# Validation plan

Sequencing for the test/validation work in Cultures, learning from Autobahn's revised setup. Strictly testing/validation. Architecture is owned by the human author and is not on this plan; PRs that depend on architecture wait for it.

## Status at the start of this branch

- `scripts/findings.py` - shared `Issue(error, verdict)` record
- `scripts/validate_general.py` - L1: filename rules, UTF-8/no-BOM, no U+FFFD, no em-dash, no `\uXXXX` literals, trailing newline
- `.github/workflows/validate.yml` - single job, runs L1 on changed `regions/**/*.md`

`ARCHITECTURE.md` was drafted on this branch as a separate strand of work; it is not part of the validation plan and not authored by the validation work.

## PR1 - L1 parity with Autobahn

Pure structure plus one new rule.

- Move `scripts/findings.py` -> `tests/findings.py`
- Move `scripts/validate_general.py` -> `tests/validate_general.py`
- Add mojibake byte check (`b"\xc3\x83" in raw`) to `validate_general.py`
- Update `validate.yml` to call `tests/validate_general.py`

Why first: zero design decisions; matches the destination Autobahn already proved. Gets validation off `scripts/` before anything else accretes there.

## PR2 - Workflow shape

Restructure `validate.yml` from one job into the `setup -> L1` pattern.

- `setup` job computes changed files once, exposes them as job outputs
- `L1` job consumes outputs, runs `tests/validate_general.py`
- explicit `no-changes` job replaces the inline `if:` skip

Why second, before L0: adding L0 / L2 / ... later becomes mechanical (`needs: setup` plus a new job). Doing the shape now means later PRs only add jobs, never restructure.

## PR3 - L0 validation stamp gate

First PR that changes contributor experience. Adds the `.validation-stamp` mechanism Autobahn introduced.

- `.githooks/pre-commit` writes `.validation-stamp` = `git mktree` of the content tree (excluding the stamp file)
- `scripts/setup-hooks.sh` (+ `.bat`) so contributors can install
- New `L0-stamp-check` job in `validate.yml`, gating L1
- Install step documented in PR body and commit message

Why third: earns its keep only once there is something worth running locally. With L1 alone the value is small but real - catches forgotten local runs. Slots cleanly into the PR2 shape.

## Held until architecture is settled

These move only after the corresponding contract is written into `ARCHITECTURE.md`. The validation work does not author architecture.

- **PR4+ - per-type L2 validators.** One PR per file type whose section contract is fixed. Likely order follows the architecture: position, place, piece, persona, process. Each PR adds one `tests/validate_<type>.py` and an `L2` job (or sub-step) in the workflow.
- **PR(later) - L3+ graph validators.** Cross-file consistency: piece `Place` link resolves to a sibling, place `Holds` lists existing siblings, persona position link resolves, minimum-per-country counts (1 position, 1 piece, 1 place, 2 personas with mixed-gender reading). Triggers once the architecture fixes the cross-file rules and the persona mixed-gender reading.
- **PR(later) - language validation.** Cultures equivalent of Autobahn's `validate_language.py`, with a `tests/language_exceptions.txt`. Triggers once the architecture defines what counts as language bleed in Cultures.

## Not on this plan

- `tests/README.md` - the layer-model document. Architecture-adjacent; not authored by the validation work.
- `tests/requirements.txt` - added only when a validator pulls in a Python dependency. None do today.

## Sequencing diagram

```text
PR0 (this branch) -> main
                     |
                     +-> PR1 folder + mojibake
                     |   |
                     |   +-> PR2 workflow shape
                     |       |
                     |       +-> PR3 L0 stamp gate
                     |
                     +-> (architecture work, separate hand)
                         |
                         +-> PR4+ L2 per type -> PR(later) L3+ graph
                                              -> PR(later) language
```
