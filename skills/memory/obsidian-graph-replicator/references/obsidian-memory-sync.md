# Obsidian Memory Sync

Use this when implementing the Obsidian side of the graph.

## Vault Layout

Recommended layout:

```text
Memoria/
  Plataforma/
    Plataforma <Project> - Hub.md
    Agentes/
    Skills/
    Interacciones/
    Herramientas/
    interacciones.json
  Runbooks/
  Proyectos Git/
```

The hub should link to agents, skills, flows, and key tools using Obsidian wikilinks so Graphify can infer relationships.

## Generated Notes

Generate these files from app metadata:

- Hub note: project overview, agent count, skill count, connection modes, flow links.
- One note per agent: role, provider/engine, type, keywords, linked skills.
- One note per skill: description and linked agents that use it.
- Flow note: named reusable flows and what they chain.
- Tool notes: important integrations such as Graphify, browsers, media providers.

## Interaction Logs

For every chat, deliverable, or pipeline:

1. Create a markdown note in `Interacciones/`.
2. Include date, agent, provider/mode, kind, prompt, and clipped output.
3. Append a JSON entry to `interacciones.json`.
4. Do not store secrets, API keys, cookies, or raw credentials.

Suggested note name:

```text
YYYY-MM-DD_HHMMSS_<agent>_<slug-title>.md
```

## Refreshing Graphify

Refresh should be best-effort and nonblocking.

Options:

- Manual route: `/api/memory/sync`.
- Background refresh every N interactions.
- Environment override: `GRAPHIFY_REFRESH=/path/to/refresh_script.py`.
- Default script if available: `memoria refresh` from Agentic Marketing OS.

After code changes in the project itself, run:

```bash
graphify update .
```

For Obsidian memory refresh scripts, ensure they mirror the memory graph into the `graph.json` path consumed by the app.

## Prompt Memory Rule

Every agent or deliverable path must call graph memory first. Use the same `graph.json` shown visually. The resulting prompt section should include a strong marker so it is easy to detect duplicate insertion:

```text
MEMORIA GRAPHIFY OBLIGATORIA
Fuente consultada: /path/to/graph.json
Usa esta memoria antes de decidir o ejecutar.
```

If the graph has no match, include a minimal fallback saying the graph was consulted and no relevant nodes were found.

## Safety

- Restrict note reads to configured note roots.
- Clip note excerpts and outputs.
- Avoid writing binary media into Obsidian notes; store media in the app library and link to it if needed.
- Make refresh failures nonfatal.
