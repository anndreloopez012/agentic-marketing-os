---
name: obsidian-graph-replicator
description: "Replicate the Obsidian/Graphify nebula graph design in any web app without depending on marketing-digital-ia, Graphify, Obsidian, npm, CDNs, or a backend. Use the bundled self-contained vanilla HTML/CSS/JS template in assets/nebula-graph-template, or adapt marketing-digital-ia/static/unified.js and static/style.css for deeper parity, to reproduce the screenshot-style full-screen dark graph with 3D spherical nodes, glow, dense links, labels, and orbital arcs. Also covers optional live graph.json, note lookup, prompt memory, and agent overlays."
---

# Obsidian Graph Replicator

Use this skill to replicate the screenshot-style graph design in another web app without requiring the original project. The skill now carries a self-contained vanilla template that runs with embedded sample data. Use the original `marketing-digital-ia` code only as a parity reference or when the target app needs the exact production behavior.

## Portable First

Default to the bundled portable template when the user wants the design in another site:

- `assets/nebula-graph-template/index.html`
- `assets/nebula-graph-template/nebula-graph.css`
- `assets/nebula-graph-template/nebula-graph.js`
- `assets/nebula-graph-template/sample-graph.json`
- `scripts/install_nebula_graph.py`

This template has no external dependencies: no npm, no CDN, no framework, no Graphify runtime, no Obsidian runtime, and no backend requirement. It renders demo data immediately and can optionally load `/api/graph` or any Graphify-like JSON.

Install it with:

```bash
python3 /Users/macbookpro/.codex/skills/obsidian-graph-replicator/scripts/install_nebula_graph.py /path/to/target-web-root
```

Read `references/portable-template.md` before using or modifying the bundled template.

## Source Code First

When exact parity with `marketing-digital-ia` is needed, inspect and adapt the existing code:

- `/Users/macbookpro/Documents/PROYECTOS/marketing-digital-ia/static/unified.js`: graph renderer, Fibonacci sphere, glow cache, links, labels, orbital rings, camera interaction, optional agent animation.
- `/Users/macbookpro/Documents/PROYECTOS/marketing-digital-ia/static/style.css`: full-screen graph layout, canvas sizing, overlays, scan/vignette effects, node panel and optional feed styles.
- `/Users/macbookpro/Documents/PROYECTOS/marketing-digital-ia/src/marketing_digital_ia/server.py`: `load_graph()`, `/api/graph`, `/api/note`, `/api/activity`, `/api/health`, graph memory hooks.
- `/Users/macbookpro/Documents/PROYECTOS/marketing-digital-ia/src/marketing_digital_ia/memory_sync.py`: optional Obsidian note generation and Graphify refresh flow.

Use this path for deep integration, not as a hard dependency for simple replication.

## Core Workflow

1. Inspect the target project stack and constraints.
   - If a local graph exists, query it first: `graphify query "<what should be replicated?>"`.
   - Identify the backend entry point, static frontend directory, agent/job model, and where user/project memory should live.
   - Decide whether the target needs the portable template only, or the full source-code parity path.

2. Install the portable graph template unless the target already has an equivalent renderer.
   - Run `scripts/install_nebula_graph.py`.
   - Keep the template files together unless integrating into an existing asset pipeline.
   - Verify `index.html` works with embedded sample data before wiring real data.

3. Add the graph data layer when live data is required.
   - Build or refresh `graphify-out/graph.json` from the desired corpus.
   - For Obsidian memory, prefer a vault folder such as `~/Documents/<Project>-Vault/Memoria`.
   - Support env overrides for portability: `GRAPH_JSON`, `NOTE_ROOTS`, `PORT`, and project-specific vault env vars.
   - Read `references/architecture.md` for the end-to-end system map.

4. Add backend contracts only when the target needs live graph, note, activity, or memory routes.
   - Expose `/api/graph`, `/api/note`, `/api/activity`, `/api/health`, and optionally `/api/memory/sync`.
   - Normalize Graphify JSON into `{nodes, links}` with stable fields: `id`, `label`, `community`, `group`, `file`, `source`, `target`, `relation`.
   - Add graph memory retrieval before every agent answer or deliverable.
   - Read `references/backend-contract.md` before editing backend code.

5. Add Obsidian memory sync only when persistent project memory is required.
   - Generate hub notes, agent notes, skill notes, and interaction logs with wikilinks.
   - Refresh Graphify best-effort after important changes or on a manual sync route.
   - Read `references/obsidian-memory-sync.md` before implementing vault writes.

6. Add or integrate the screenshot-style Graphify nebula graph.
   - Use a full-screen canvas for the graph, not a card preview.
   - For independence, start from `assets/nebula-graph-template`.
   - For exact production parity, adapt the `Unified` module in `static/unified.js` and graph-related CSS blocks in `static/style.css`.
   - Match the screenshot first: dark starfield, dense 3D node sphere, bloom/glow nodes, many fine edges, large project labels, and orbital accent arcs.
   - Render nodes on a Fibonacci sphere or force-directed 3D projection, color by community, size by degree, and label important/high-degree nodes.
   - Add stats/search/panels only as overlays when the target web needs them; do not let panels dominate the graph.
   - Read `references/frontend-jarvis-graph.md` before implementing frontend.

6. Wire activity to graph animation when the target app has agents or chat.
   - Poll `/api/activity`.
   - Map activity events to graph nodes with `node_id`.
   - Optionally call `updateUnifiedAgents(activity)` and `animateAgentCollect(agentId, nodeId)` when relevant events arrive.

8. Validate.
   - Run project syntax/build tests.
   - Run `graphify update .` after code changes when the project uses Graphify.
   - Browser-test `/api/graph`, node search, node panel note loading, activity feed, and robot movement.

## Implementation Rules

- The visual design must be reproducible from the bundled template without the original repo or backend.
- When live data exists, the same `graph.json` should power both the visual graph and prompt memory. Do not maintain separate graph sources.
- Treat `marketing-digital-ia` source code as canonical only for exact parity; the portable template is canonical for dependency-free replication.
- Agents must consult graph memory before answering, generating prompts, or creating deliverables when the target app includes agents.
- Keep note access safe: resolve files only under configured note roots.
- Do not expose secrets in graph, notes, or frontend config.
- Keep graph UI as the actual first-screen experience: full-bleed canvas, dark immersive background, glowing graph, no marketing hero page.
- When the user references the screenshot, prioritize visual fidelity over dashboards, cards, panels, or chat controls.
- Use canvas 2D for this design unless the target project already uses Three.js; the original implementation is canvas-based.
- Prefer progressive enhancement: the app should still answer if the graph is missing, but it should mark the missing graph clearly.

## Reference Routing

- `references/architecture.md`: read for overall flow and file responsibilities.
- `references/backend-contract.md`: read before adding backend endpoints or graph memory injection.
- `references/frontend-jarvis-graph.md`: read before recreating the visual design.
- `references/obsidian-memory-sync.md`: read before writing vault notes, interaction logs, or refresh hooks.
- `references/portable-template.md`: read before using the bundled dependency-free template.

## Minimal Acceptance Checklist

- The bundled template can be copied into a blank folder and opened with demo data.
- The template uses no external dependencies or network calls unless a data source is configured.
- Optional `/api/health` reports whether graph JSON exists.
- Optional `/api/graph` returns non-empty `nodes` and `links` when `graph.json` exists.
- Optional `/api/note?file=...` loads note text only from allowed roots.
- Optional chat/job paths call graph memory before provider execution.
- Frontend first screen visually matches the screenshot: dark nebula, 3D graph cloud, glow nodes, dense edges, labels, and orbital arcs.
- Optional search opens a node detail panel with note content and related nodes.
- Optional agent activity creates visible feed entries and robot-to-node animations.
- Graphify refresh/update is documented and can be run manually.
