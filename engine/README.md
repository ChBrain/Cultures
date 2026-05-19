# Culture Engine

The culture engine is the scaffold every culture runs on. A deployment pairs
a culture (the content for one country) with this engine layer and one set of
provider instructions. Each provider needs its own targeted package -- the
deployments differ for technical reasons -- so downloads are per provider.

## Deployments

Pick the deployment that matches the tool you will run the culture on. Each
folder's README explains its provider and links the same download. The
per-provider zips are stubs for now; the targeted packages land with the
release pipeline.

1. [Claude.ai Project](claude/README.md) - download: _targeted zip (stub)_
2. [Copilot Project](copilot/README.md) - download: _targeted zip (stub)_
3. [Gemini Gem](gemini/README.md) - download: _targeted zip (stub)_
4. [Google NotebookLM](notebooklm/README.md) - download: _targeted zip (stub)_
5. [Perplexity Space](perplexity/README.md) - download: _targeted zip (stub)_

Each deployment folder carries its own `README.md` and an `instructions.md`.
The instructions are exact: paste them as-is, do not edit or summarize them.

## Naked engine

The naked engine is this layer with no target provider attached: the bare
scaffold a culture runs on, without deployment instructions. Use it directly
when you are not targeting one of the deployments above.

It is these files, shipped with every deployment:

- [stack.md](stack.md) - the project stack.
- [position_female.md](position_female.md) / [position_male.md](position_male.md) - the gender positions a persona can hold.
- [process_world_is_spinning.md](process_world_is_spinning.md) - the shared process scaffold.

A culture's own files - persona, place, piece, position, process, history -
live under `regions/<region>/<country>/` and reference this engine layer.

---

*v0.2.0 - KAI Cultures*
