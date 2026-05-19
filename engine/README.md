# Culture Engine

The culture engine is the scaffold every culture runs on. A deployment is
one culture zip (the culture content for a single country) plus this engine
layer: the shared positions, the stack, the process scaffold, and one set of
deployment instructions.

## Deployments

Pick the deployment that matches the assistant you will run the culture on:

- [Claude](claude/README.md) - upload the culture zip as a project and paste
  `claude/instructions.md` into the instructions field.
- [Gemini](gemini/instructions.md) - the Gemini instruction set.
- [Copilot](copilot/instructions.md) - the Copilot instruction set.

Each deployment carries its own `instructions.md`. The instructions are
exact: paste them as-is, do not edit or summarize them.

## Shared scaffold

These files ship with every deployment:

- [stack.md](stack.md) - the project stack.
- [position_female.md](position_female.md) / [position_male.md](position_male.md) - the gender positions a persona can hold.
- [process_world_is_spinning.md](process_world_is_spinning.md) - the shared process scaffold.

A culture's own files - persona, place, piece, position, process, history -
live under `regions/<region>/<country>/` and reference this engine layer.

---

*v0.1.0 - KAI Cultures*
