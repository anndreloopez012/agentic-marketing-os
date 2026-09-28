# Architecture Pattern

This skill replicates a production graph system (an Obsidian + Graphify memory viewer) as a portable pattern.

## Layers

1. Corpus and memory
   - Obsidian vault contains durable notes, runbooks, agent docs, skill docs, and interaction logs.
   - Graphify builds `graphify-out/graph.json` from the corpus.
   - The graph may also be mirrored from another memory graph path.

2. Backend
   - Loads `GRAPH_JSON`.
   - Resolves note files from `NOTE_ROOTS`.
   - Exposes graph, note, activity, memory sync, and health endpoints.
   - Injects graph context into agent prompts before any execution.

3. Frontend
   - Loads `/api/graph`.
   - Renders a full-screen canvas graph sphere.
   - Polls `/api/activity` and animates agent robots to nodes.
   - Opens node panels using `/api/note`.

4. Agent execution
   - User prompt enters a job.
   - Job queries graph memory.
   - Enhanced prompt includes a required marker such as `MEMORIA GRAPHIFY OBLIGATORIA`.
   - Provider execution happens only after memory is attached.
   - Output and interactions can be logged back to Obsidian.

## Portable File Map

Use analogous files in the target project:

```text
backend/
  graph_config.py or server.py       # GRAPH_JSON, NOTE_ROOTS, load_graph
  memory_sync.py                     # optional Obsidian note generation/logging
  routes.py or server.py             # /api/graph, /api/note, /api/activity
frontend/
  index.html                         # canvas shell and panels
  graph.css                          # visual system and responsive layout
  unified.js                         # canvas renderer, search, panels, agent animation
graphify-out/
  graph.json                         # source of truth for UI and agent memory
```

## Required Runtime Data Shapes

Backend `/api/graph` should return:

```json
{
  "nodes": [
    {"id": "note::x.md", "label": "Topic", "community": 1, "group": "Community Name", "file": "x.md"}
  ],
  "links": [
    {"source": "note::x.md", "target": "note::y.md", "relation": "mentions"}
  ]
}
```

Backend `/api/activity` should return:

```json
{
  "events": [
    {"agent": "orchestrator", "state": "reading", "label": "consulting memory", "node_id": "note::x.md", "target_short": "Topic"}
  ],
  "active_agents": {
    "orchestrator": {"state": "reading", "label": "consulting memory", "target": "Topic"}
  },
  "working": true
}
```

## Replication Sequence

1. Create or locate the memory corpus.
2. Run Graphify and confirm `graphify-out/graph.json`.
3. Implement backend graph normalization.
4. Implement note resolution safely.
5. Implement graph memory retrieval and prompt injection.
6. Implement activity events with `node_id`.
7. Add canvas graph UI.
8. Wire polling to robot/node animations.
9. Validate in browser and with graph queries.
