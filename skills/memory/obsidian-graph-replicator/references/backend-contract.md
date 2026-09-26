# Backend Contract

Use this when adding the graph to a Python/Node/Ruby/etc backend. The original project uses Python `http.server`, but the contract is framework independent.

## Configuration

Support these environment variables or equivalents:

```text
GRAPH_JSON=/absolute/path/to/graphify-out/graph.json
NOTE_ROOTS=/absolute/vault/Memoria:/absolute/project/docs
PORT=8800
```

On Windows, accept `;` as a separator for `NOTE_ROOTS` when practical.

## Graph Loading

Normalize Graphify data once and cache by file mtime:

```python
def load_graph():
    raw = json.load(open(GRAPH_JSON, encoding="utf-8"))
    nodes = [{
        "id": n.get("id"),
        "label": n.get("label", ""),
        "community": n.get("community", 0),
        "group": n.get("community_name", ""),
        "file": n.get("source_file", ""),
    } for n in raw.get("nodes", [])]
    links = [{
        "source": e.get("source"),
        "target": e.get("target"),
        "relation": e.get("relation", ""),
    } for e in raw.get("links", raw.get("edges", []))]
    return {"nodes": nodes, "links": links}
```

## Required Routes

- `GET /api/graph`: return normalized graph.
- `GET /api/note?file=<relative>`: resolve and return note content.
- `GET /api/activity`: return job/tool events and active agents.
- `GET /api/health`: include `graph: true|false`.
- `GET /api/memory/sync` optional: regenerate Obsidian docs and refresh Graphify.

## Safe Note Resolution

Never trust the `file` query directly. Normalize the path, join it under each allowed root, and only return the file if its real path starts with one of the real allowed roots. Also support lookup by basename because Graphify `source_file` may be relative.

## Graph Memory Retrieval

Use the same graph that powers `/api/graph`.

1. Build search terms from user prompt, upstream result, agent name, role, keywords, and skills.
2. Score nodes by label/group/file/id.
3. Pick the top nodes plus directly related neighbors.
4. Resolve note excerpts from `file`.
5. Build a text block with:
   - marker: `MEMORIA GRAPHIFY OBLIGATORIA`
   - source path
   - relevant nodes
   - useful relations
   - Obsidian excerpts
   - rule for missing data

Attach this block before provider execution. If the graph is missing, still add a small marker saying the graph was consulted but unavailable.

## Activity Events

To drive robot animations, events need `agent`, `state`, `label`, `node_id`, and `target_short`.

When graph context is selected for a job, emit synthetic events such as:

```json
{"tool": "Graphify", "state": "reading", "label": "consulting Graphify/Obsidian memory", "agent": "orchestrator", "node_id": "note::topic.md"}
```

The frontend uses these to pulse nodes and send robots to exact locations.

## Validation

- `curl /api/health` shows graph availability.
- `curl /api/graph` returns expected counts.
- `curl /api/note?file=<known-file>` returns content and rejects traversal.
- A job records graph context before LLM/provider execution.
