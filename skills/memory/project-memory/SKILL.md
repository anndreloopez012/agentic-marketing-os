---
name: project-memory
description: Use the student's Obsidian memory vault as long-term context for their marketing and web projects. Use when starting work on a project, when the user mentions Obsidian, memoria, bitácora, project context, previous decisions, "what did we do last time", or asks to record a decision or learning. Reads the vault first, checks git state, and records confirmed decisions with the `memoria` CLI.
metadata:
  short-description: Use the Obsidian memory vault for project context
---

# Project Memory

Use this skill before making decisions in the user's projects, and after finishing work to leave context for the next session (for any agent: Claude, Codex/ChatGPT or Gemini).

## Where memory lives

The installer (`scripts/install.sh` in Agentic Marketing OS) writes the paths to `engine/memory/config/settings.json`. Resolve them in this order:

1. `$OBSIDIAN_VAULT_ROOT` environment variable, if set.
2. `vault_root` in `engine/memory/config/settings.json`.
3. Default: `~/Documents/Obsidian Vault`.

Inside the vault:

- `Memoria/Inicio Memoria.md` — entry point.
- `Memoria/Contexto Operativo.md` — active projects and priorities.
- `Memoria/Proyectos Git/<proyecto>.md` — one note per project.
- `Memoria/Bitacora/` — chronological log.
- `Memoria/Decisiones/` — confirmed decisions.
- `Memoria/Graphify/<proyecto>/` — exported knowledge graphs.

Deliverables live in the projects folder chosen at install time (`projects_roots` in settings), never inside the vault.

## Workflow

1. Read `Inicio Memoria.md`, then `Contexto Operativo.md` when starting a new thread.
2. Find the project note (`memoria proyecto <nombre>` or the index) and read it before editing.
3. Run `git status --short` in the project. Treat local changes as the user's.
4. If the project has `graphify-out/graph.json`, ask the graph before reading lots of files: `graphify query "<pregunta>"`.
5. Verify in the real files before changing behavior; memory is a hint, not the source of truth.

## CLI shortcuts

```bash
memoria contexto <proyecto>
memoria proyecto <proyecto>
memoria buscar "<texto>"
memoria cambios --detalle
memoria salud
memoria refresh
memoria registrar <proyecto> --tipo decision --titulo "Tono de voz aprobado" --texto "Cercano, sin tecnicismos, tuteo." --archivo marca/brand-profile.md
memoria bitacora --proyecto <proyecto>
```

If the `memoria` CLI is not installed (for example in ChatGPT or claude.ai without a terminal), write the same information as a short Markdown note and ask the user to save it in `Memoria/Bitacora/`.

## Memory update rule

When a decision is confirmed, add it to the project note inside:

```text
<!-- memoria-manual-start -->
...
<!-- memoria-manual-end -->
```

The refresh script preserves that block.

## What to record (and what not)

Record: approved brand decisions, campaign results, audiences that worked, validated prompts, fixed bugs with a reusable cause, deployment steps that worked.

Never record: passwords, API keys, tokens, client personal data, full conversations, noisy logs or guesses.
