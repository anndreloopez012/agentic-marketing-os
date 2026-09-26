---
name: project-memory
description: Use this when working on local projects under /Users/macbookpro/Documents/PROYECTOS, when the user mentions Obsidian memory, project context, Core Strapi, Contraloria, USAC Editorial, RENAP, TEC InfoApp, Softplus, Store, CRM, or asks Codex to use prior project knowledge. Reads the Obsidian project memory first and refreshes it when needed.
metadata:
  short-description: Use Obsidian memory for local projects
---

# Project Memory

Use this skill before making technical decisions in the user's local projects.

## Memory Locations

- Obsidian entry point: `/Users/macbookpro/Documents/Obsidian Vault/Memoria/Proyectos Git/Inicio Memoria.md`
- Main index: `/Users/macbookpro/Documents/Obsidian Vault/Memoria/Proyectos Git/README - Memoria.md`
- Deep technical index: `/Users/macbookpro/Documents/Obsidian Vault/Memoria/Proyectos Git/Indice Tecnico Profundo.md`
- Operational context: `/Users/macbookpro/Documents/Obsidian Vault/Memoria/Proyectos Git/Contexto Operativo.md`
- Chat context clues: `/Users/macbookpro/Documents/Obsidian Vault/Memoria/Proyectos Git/Contexto de Chats.md`
- Refresh script: `/Users/macbookpro/Documents/Playground/memoria_tools/refresh_project_memory.py`
- CLI: `/opt/homebrew/bin/memoria`
- Project root: `/Users/macbookpro/Documents/PROYECTOS`

## Workflow

1. Read `Inicio Memoria.md`.
2. Read `Contexto Operativo.md` when starting a new thread or when the user asks to rely on memory.
3. Identify the relevant project note from the main index or map.
4. Read the project note before editing code, especially `Estado local`, commands, endpoints, routes, content-types, and related projects.
5. Run `git status --short` in the repo before editing. Treat local changes as user-owned unless the user explicitly says otherwise.
6. Use the deep technical index for quick lookup, then verify in source files before changing behavior.
7. If the user asks to refresh or if the project inventory seems stale, run:

```bash
python3 "/Users/macbookpro/Documents/Playground/memoria_tools/refresh_project_memory.py"
```

## CLI Shortcuts

Use the CLI for fast lookup:

```bash
memoria proyecto core-strapi
memoria buscar permisos
memoria cambios --detalle
memoria salud
memoria dependencias --proyecto contraloria-frontend
memoria rutas core-strapi
memoria refresh
memoria registrar core-strapi --tipo aprendizaje --titulo "Flujo relevante" --texto "Resumen reutilizable" --archivo src/App.tsx --validacion "npm run build"
memoria bitacora --proyecto core-strapi
```

## Memory Update Rule

When a decision is confirmed during work, add it to the relevant project note inside:

```text
<!-- memoria-manual-start -->
...
<!-- memoria-manual-end -->
```

The refresh script preserves that block.

Do not store secrets in Obsidian. Store only variable names, non-sensitive local commands, architecture notes, and confirmed decisions.

## Continuous Capture Rule

After effective work, capture reusable context with `memoria registrar` when any of these happened:

- a page, flow, service, endpoint, permission model, content-type, deployment step, or relation was understood;
- a bug was fixed and the root cause is reusable;
- a decision was confirmed;
- a validation command or runbook step was proven;
- a frontend/backend relationship was confirmed.

Do not register noisy logs, speculative guesses, secrets, tokens, full conversations, or temporary dead ends. Keep entries concise and useful for a future thread.
