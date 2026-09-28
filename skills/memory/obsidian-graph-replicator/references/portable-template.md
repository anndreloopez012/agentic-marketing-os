# Portable Template

Use this reference when the user wants the graph design to work in another site without depending on the original reference app, a build system, a backend, or external packages.

## Included Files

The skill bundles a self-contained template at:

```text
assets/nebula-graph-template/
  index.html
  nebula-graph.css
  nebula-graph.js
  sample-graph.json
```

It uses only browser APIs:

- Canvas 2D
- pointer events
- `fetch` only when an optional graph source is configured
- no npm packages
- no CDN
- no framework
- no backend required for the demo state

## Install

Copy the template with the bundled script:

```bash
python3 <skill-dir>/scripts/install_nebula_graph.py /path/to/target-web-root
```

This creates:

```text
/path/to/target-web-root/graphify-nebula/
```

Open `graphify-nebula/index.html` directly or serve it from the target site.

## Connect Real Data

The renderer works with these graph shapes:

```json
{"nodes":[{"id":"a","label":"A","community":0}],"links":[{"source":"a","target":"b"}]}
```

or:

```json
{"nodes":[...],"edges":[{"source":"a","target":"b"}]}
```

Use one of these integration methods:

```html
<main class="nebula-shell" data-graph-src="/api/graph">
```

or:

```js
NebulaGraph.mount(document.querySelector(".nebula-shell"), { src: "/api/graph" });
```

or pass data directly:

```js
NebulaGraph.mount(document.querySelector(".nebula-shell"), { graph: myGraph });
```

## Porting Rules

- Keep `nebula-graph.js` independent unless the target app needs a framework wrapper.
- Preserve the canvas first-screen layout.
- Preserve glow nodes, dense translucent edges, high-degree labels, and orbital arcs.
- Hide or remove the optional panel if the target site needs a pure visual background.
- Do not require Graphify, Obsidian, Python, or a server for the visual demo.
- Add backend only when the target site needs live `graph.json`, note lookup, or activity events.

## Validation

Before delivery:

- open the generated `index.html`
- confirm the graph renders with the embedded sample data
- confirm drag, wheel zoom, double-click reset, hover tooltip, search, and node panel work
- if connected to `/api/graph`, confirm node/link counts match the returned JSON
