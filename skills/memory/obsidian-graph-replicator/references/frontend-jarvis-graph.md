# Frontend Graphify Nebula Graph

Use this when implementing the nebula graph visual in another web app. For dependency-free replication, use `assets/nebula-graph-template` first; it is standalone HTML/CSS/JS and renders with embedded demo data. The screenshot is the visual acceptance target.

## Dependency-Free Implementation

Use the bundled template when the target site should not depend on anything else:

```text
assets/nebula-graph-template/index.html
assets/nebula-graph-template/nebula-graph.css
assets/nebula-graph-template/nebula-graph.js
assets/nebula-graph-template/sample-graph.json
```

Capabilities:

- runs with only browser APIs
- renders without a server
- includes embedded demo graph generation
- optionally loads `/api/graph` or another JSON URL
- accepts direct data via `NebulaGraph.mount(el, { graph })`
- exposes `window.NebulaGraph`

## Source Parity Map

Use these existing source files only when deeper parity with the original reference app (not included) is needed:

- `static/unified.js`
  - `Unified` module: renderer lifecycle and public API.
  - `loadGraph()`: fetches `/api/graph`, computes degrees, sorts nodes and prepares layout.
  - Fibonacci sphere block: positions nodes in 3D.
  - `glow(color)`: cached radial glow sprites.
  - `drawSphere()`: draws links, node halos, cores and labels.
  - `drawRings()`: orbital arcs.
  - `drawMotes()`, `drawCore()`: background motion and visual depth.
  - Pointer/wheel handlers: rotate, hover, click, zoom and reset.
  - Agent functions after `drawAgents()`: optional chat/agent overlay.
- `static/style.css`
  - `canvas#unified`: full-screen canvas.
  - `.unified-stats`, `.unified-feed`, `.nodepanel`: optional overlays.
  - `.fx-scan`, background variables and graph view rules: dark HUD/nebula surface.
- `src/marketing_digital_ia/server.py`
  - `load_graph()`: Graphify JSON normalization.
  - `/api/graph`: visual graph data.
  - `/api/note`: note panel data.
  - `/api/activity`: optional agent/node animation events.

Port these pieces only when the standalone template is not enough for the target project.

## Primary Visual Target

Match these visible qualities before adding secondary UI:

- Full-viewport graph surface with no card frame.
- Very dark purple/black background with subtle horizontal scanlines or star specks.
- Hundreds of nodes arranged as a deep spherical/hemispherical cloud.
- Community colors: cyan, blue, violet, magenta, green, amber, and white highlights.
- Strong bloom/glow around important nodes and communities.
- Thin semi-transparent relationship lines, dense enough to show a neural mesh without turning opaque.
- Labels for important/high-degree nodes, floating over the graph in light serif or clean display text.
- Curved orbital accent arcs crossing foreground/background.
- Visible depth: small/dim nodes in the back, larger/brighter nodes in the front.
- Motion: slow autonomous rotation, slight pulse, hover brightening, and drag/zoom controls.

## HTML Structure

Use one full-screen view. Keep overlays optional and compact:

```html
<section class="view active" id="view-unified">
  <canvas id="unified"></canvas>
  <div class="fx-scan"></div>
  <div class="nodepanel" id="nodePanel">...</div>
  <div class="unified-stats">...</div>
  <div class="unified-feed">...</div>
  <div class="unified-core-label">...</div>
  <div class="unified-hint">...</div>
</section>
<div id="tooltip"></div>
```

Required elements:

- `#unified`: full-screen canvas.
- `#tooltip`: hover label.
- Optional `#nodeCount`, `#edgeCount`, `#commCount`: graph counters.
- Optional `#search`, `#searchResults`: node search.
- Optional `#nodePanel`, `#npTitle`, `#npMeta`, `#npConns`, `#npContent`: node detail.
- Optional `#feedOffice`, `#feedBrain`: agent and node activity feeds.
- Optional `#hudActive`: active agent count.

## Visual Style

Use a glowing nebula palette:

```css
:root {
  --purple:#5E3AE2;
  --purple-2:#7b5cff;
  --yellow:#F4B422;
  --green:#00AA80;
  --blue:#2CAAFF;
  --bg:#0a0713;
  --panel:#120c24;
  --text:#ECEAF6;
  --muted:#9b94c0;
}
```

Layout rules:

- Canvas fills the viewport under the header.
- If panels are present, make them glassy, compact, and clearly secondary.
- Do not split the graph into dashboard cards.
- If a right feed exists, reserve its width in the graph center calculation so the sphere is not hidden behind the feed.
- Node panel, if present, overlays one side and loads note content on demand.
- Use scanlines and subtle vignette as overlays, not decorative blobs.

## Canvas Algorithm

1. Fetch `/api/graph`.
2. Compute degree for each node.
3. Sort by community, then degree.
4. Place nodes on a Fibonacci sphere or force-directed 3D sphere. Fibonacci sphere is deterministic and close to the screenshot:

```js
const GOLDEN = Math.PI * (3 - Math.sqrt(5));
ordered.forEach((n, i) => {
  const y = 1 - (i / (N - 1)) * 2;
  const rad = Math.sqrt(Math.max(0, 1 - y * y));
  const th = GOLDEN * i;
  n.bx = Math.cos(th) * rad;
  n.by = y;
  n.bz = Math.sin(th) * rad;
});
```

5. Rotate by `rotY` and `rotX`.
6. Perspective project with focal length around `R * 2.6`.
7. Sort by projected depth.
8. Draw back links first, then front links with higher alpha.
9. Draw glow halos, then node cores, then labels.
10. Color nodes by `community % palette.length`.
11. Size nodes by degree and depth.
12. Highlight neighbors on hover/selection.

## Drawing Rules

- Use additive-looking glow with layered circles: large low-alpha halo, medium color halo, small white core.
- Cap edge alpha so dense meshes stay readable: usually `0.025` to `0.12`.
- Use edge color from source/target community with low alpha.
- Label only high-degree or selected/hovered nodes; too many labels creates noise.
- Use label shadows/glow so text remains readable over edges.
- Draw 2-4 orbital arcs with `quadraticCurveTo` or projected 3D rings; keep them thin and amber/cyan.
- Keep animation subtle: slow rotation, pulsing selected nodes, occasional shimmer particles.

## Optional Agent Robots

Only add robots when the target web also has chat/agent activity. They are not required to replicate the screenshot. Represent each agent as an object with:

```js
{ agent, ang, active:false, state:"idle", target:null, mission:null, x:0, y:0 }
```

Place agents on an orbit around the sphere. Draw small holographic robots with:

- glow halo in agent color
- animated eyes
- anti-grav disc
- chest emoji
- keyboard when working
- travel trail
- collection beam/particles when reading a node

Expose two global functions:

```js
window.updateUnifiedAgents = function(activity) { ... }
window.animateAgentCollect = function(agentId, nodeId) { ... }
```

`animateAgentCollect()` should pulse the node and create a mission:

```js
ag.mission = { nodeId, phase: "out", t: 0, dur: 48, collectDur: 42 };
```

Mission phases:

- `out`: robot travels from orbit to node using a quadratic Bezier curve.
- `collect`: robot stays near node, node pulses, particles stream to robot.
- `back`: robot returns to orbit and shows a small report pill.

## Interaction

- Drag canvas to rotate sphere.
- Wheel to zoom.
- Double click to reset camera.
- Hover node to show tooltip.
- Click node to open detail panel.
- Search result opens and focuses a node.
- Click robot opens or preselects that agent in the chat UI.

## Polling Hook

Every 2 seconds:

1. Fetch `/api/activity`.
2. Update feed lists.
3. Call `updateUnifiedAgents(activity)`.
4. For new events with `node_id`, call `Unified.activate(node_id)` and `animateAgentCollect(event.agent, event.node_id)`.

## Browser QA

Before considering the graph finished:

- Verify the canvas is nonblank on desktop and mobile widths.
- Compare against the screenshot target: dark nebula, 3D spherical graph, multicolor glow, dense translucent links, labels, and orbital arcs.
- Verify counts match `/api/graph`.
- Verify hover tooltip, zoom, drag, and double-click reset.
- If optional panels exist, verify search, node panel, and note loading.
- If optional agents exist, trigger a synthetic activity event and verify robot travel.
