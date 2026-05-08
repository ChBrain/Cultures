# Cultures

*198 cultural positions. Each one already running. Each one holding what it holds.*

---

*For the person who arrived in a room and did not know which contract was in force.*

---

## What this is

A library built from the operating logic of 198 cultures across 5 regions.

Each culture has a position - what it holds, what it orders, what it loses when pressed. Each position has a place: the capital city or the defining location where the position does its daily work. Each position has a piece: the load-bearing historical moment, document, or symbol without which the position's logic would not have its current shape.

Hundreds of personas. People doing ordinary work carrying a cultural position they did not choose and mostly do not name. Each acting from it anyway.

---

## How to use

**Step 1 - Install the engine** (once per project)

Download the engine zip for your platform and upload all files to your AI project.

The engine defines how the world runs. It must be present before adding any cultures.

| Platform | Download |
|----------|----------|
| Claude.ai | [engine-claude.zip](https://github.com/ChBrain/Cultures/releases/latest/download/engine_claude.zip) |
| Microsoft Copilot | [engine-copilot.zip](https://github.com/ChBrain/Cultures/releases/latest/download/engine_copilot.zip) |
| Google Gemini | [engine-gemini.zip](https://github.com/ChBrain/Cultures/releases/latest/download/engine_gemini.zip) |

**Step 2 - Add the cultures you need**

Download one or more region packs and upload their files to the same project:

| Region | Cultures | Download | PDF |
|--------|----------|----------|-----|
| Africa | 53 | [cultures-africa.zip](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-africa.zip) | [cultures-africa.pdf](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-africa.pdf) |
| Americas | 35 | [cultures-americas.zip](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-americas.zip) | [cultures-americas.pdf](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-americas.pdf) |
| Asia | 49 | [cultures-asia.zip](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-asia.zip) | [cultures-asia.pdf](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-asia.pdf) |
| Europe | 48 | [cultures-europe.zip](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-europe.zip) | [cultures-europe.pdf](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-europe.pdf) |
| Oceania | 13 | [cultures-oceania.zip](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-oceania.zip) | [cultures-oceania.pdf](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-oceania.pdf) |
| All regions | 198 | [cultures-full.zip](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-full.zip) | [cultures-full.pdf](https://github.com/ChBrain/Cultures/releases/latest/download/cultures-full.pdf) |

You can install multiple region packs into the same project. The world runs with whatever cultures are present.

**Step 3 - Start**

Open a conversation in your AI project. Bring what you have.

---

## Structure

```
engine/
  claude/     instructions for Claude.ai
  copilot/    instructions for Microsoft Copilot
  gemini/     instructions for Google Gemini
  stack.md    shared architecture
  process_world_is_spinning.md
regions/
  europe/     48 cultures
  africa/     53 cultures
  americas/   35 cultures
  asia/       49 cultures
  oceania/    13 cultures
```

Each country folder: position + piece + place + personas.

---

*CC BY-NC 4.0 - KAI Worlds - 2026*
