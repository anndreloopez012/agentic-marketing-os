(function () {
  "use strict";

  const PALETTE = ["#33e8ff", "#34a7ff", "#8c62ff", "#ff4ed2", "#19e1a7", "#ffc247", "#ffffff"];
  const GOLDEN = Math.PI * (3 - Math.sqrt(5));

  function seededRandom(seed) {
    let s = seed >>> 0;
    return function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
  }

  function createSampleGraph(count = 260) {
    const rand = seededRandom(42);
    const groups = ["Command Center", "Projects", "Skills", "Runbooks", "Marketing", "Backend", "Frontend", "Memory"];
    const nodes = [];
    const links = [];
    const anchors = [
      "Indice de Skills", "Campana Lanzamiento", "Calendario Instagram", "tienda-online",
      "landing-page", "Mi Marca", "Runbooks", "Graphify", "Brand Book"
    ];

    for (let i = 0; i < count; i += 1) {
      const group = i % groups.length;
      nodes.push({
        id: "node-" + i,
        label: anchors[i] || groups[group] + " " + String(i + 1).padStart(2, "0"),
        community: group,
        group: groups[group]
      });
    }

    for (let i = 0; i < count; i += 1) {
      const local = (i + 1 + Math.floor(rand() * 8)) % count;
      links.push({ source: "node-" + i, target: "node-" + local, relation: "related" });
      if (i % 2 === 0) links.push({ source: "node-" + i, target: "node-" + Math.floor(rand() * count), relation: "mentions" });
      if (i % 3 === 0) links.push({ source: "node-" + i, target: "node-" + Math.floor(rand() * count), relation: "cross-link" });
      if (i % 5 === 0) links.push({ source: "node-" + i, target: "node-" + ((i + 37) % count), relation: "bridge" });
    }
    return { nodes, links };
  }

  function normalizeGraph(input) {
    const data = input && typeof input === "object" ? input : createSampleGraph();
    const rawNodes = Array.isArray(data.nodes) ? data.nodes : [];
    const rawLinks = Array.isArray(data.links) ? data.links : Array.isArray(data.edges) ? data.edges : [];

    const nodes = rawNodes.map((n, i) => {
      const id = String(n.id || n.key || n.name || n.label || "node-" + i);
      return {
        id,
        label: String(n.label || n.name || n.title || id),
        community: Number.isFinite(Number(n.community)) ? Number(n.community) : Number.isFinite(Number(n.group)) ? Number(n.group) : i % PALETTE.length,
        group: String(n.group || n.community_label || n.type || "Group " + ((i % PALETTE.length) + 1)),
        file: n.file || n.source_file || "",
        raw: n
      };
    });

    const nodeIds = new Set(nodes.map(n => n.id));
    const links = rawLinks.map((l) => {
      const source = typeof l.source === "object" ? l.source.id : l.source;
      const target = typeof l.target === "object" ? l.target.id : l.target;
      return {
        source: String(source || ""),
        target: String(target || ""),
        relation: String(l.relation || l.type || l.label || "related")
      };
    }).filter(l => nodeIds.has(l.source) && nodeIds.has(l.target) && l.source !== l.target);

    return { nodes, links };
  }

  function mount(root, options = {}) {
    const host = typeof root === "string" ? document.querySelector(root) : root;
    if (!host) throw new Error("NebulaGraph mount target not found");

    const canvas = host.querySelector("canvas") || document.createElement("canvas");
    if (!canvas.parentNode) host.appendChild(canvas);
    const ctx = canvas.getContext("2d");
    const tip = host.querySelector("#graphTooltip");
    const nodePanel = host.querySelector("#nodePanel");
    const nodeTitle = host.querySelector("#nodeTitle");
    const nodeCommunity = host.querySelector("#nodeCommunity");
    const nodeMeta = host.querySelector("#nodeMeta");
    const nodeLinks = host.querySelector("#nodeLinks");
    const search = host.querySelector("#graphSearch");
    const searchResults = host.querySelector("#searchResults");

    const state = {
      graph: normalizeGraph(options.graph || window.NEBULA_GRAPH_DATA || createSampleGraph()),
      nodeMap: new Map(),
      degree: new Map(),
      adjacency: new Map(),
      labels: new Set(),
      hover: null,
      selected: null,
      width: 0,
      height: 0,
      dpr: 1,
      radius: 1,
      rotX: -0.34,
      rotY: 0.18,
      zoom: 1,
      dragging: false,
      lastX: 0,
      lastY: 0,
      tick: 0,
      stars: [],
      glowCache: new Map()
    };

    function colorFor(node) {
      return PALETTE[Math.abs(Number(node.community) || 0) % PALETTE.length];
    }

    function updateMetrics() {
      const communities = new Set(state.graph.nodes.map(n => n.community));
      setText("nodeCount", state.graph.nodes.length);
      setText("edgeCount", state.graph.links.length);
      setText("communityCount", communities.size);
    }

    function setText(id, value) {
      const el = host.querySelector("#" + id);
      if (el) el.textContent = value;
    }

    function prepareGraph(graph) {
      state.graph = normalizeGraph(graph);
      state.nodeMap = new Map(state.graph.nodes.map(n => [n.id, n]));
      state.degree = new Map();
      state.adjacency = new Map();

      for (const n of state.graph.nodes) {
        state.degree.set(n.id, 0);
        state.adjacency.set(n.id, new Set());
      }
      for (const l of state.graph.links) {
        state.degree.set(l.source, (state.degree.get(l.source) || 0) + 1);
        state.degree.set(l.target, (state.degree.get(l.target) || 0) + 1);
        state.adjacency.get(l.source)?.add(l.target);
        state.adjacency.get(l.target)?.add(l.source);
      }

      const ordered = [...state.graph.nodes].sort((a, b) => {
        const c = Number(a.community) - Number(b.community);
        return c || (state.degree.get(b.id) || 0) - (state.degree.get(a.id) || 0);
      });
      const max = Math.max(1, ordered.length - 1);
      ordered.forEach((n, i) => {
        const y = 1 - (i / max) * 2;
        const rad = Math.sqrt(Math.max(0, 1 - y * y));
        const th = GOLDEN * i;
        const cluster = 0.82 + ((Number(n.community) || 0) % 5) * 0.035;
        n.bx = Math.cos(th) * rad * cluster;
        n.by = y * 0.78;
        n.bz = Math.sin(th) * rad * cluster;
      });

      const top = [...state.graph.nodes]
        .sort((a, b) => (state.degree.get(b.id) || 0) - (state.degree.get(a.id) || 0))
        .slice(0, Math.min(34, Math.ceil(state.graph.nodes.length * 0.12)));
      state.labels = new Set(top.map(n => n.id));
      updateMetrics();
      renderSearch("");
    }

    function resize() {
      state.dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
      state.width = Math.max(1, host.clientWidth || window.innerWidth);
      state.height = Math.max(1, host.clientHeight || window.innerHeight);
      canvas.width = Math.floor(state.width * state.dpr);
      canvas.height = Math.floor(state.height * state.dpr);
      canvas.style.width = state.width + "px";
      canvas.style.height = state.height + "px";
      ctx.setTransform(state.dpr, 0, 0, state.dpr, 0, 0);
      state.radius = Math.min(state.width, state.height) * 0.48 * state.zoom;
      buildStars();
    }

    function buildStars() {
      const rand = seededRandom(84);
      const total = Math.max(70, Math.floor((state.width * state.height) / 16000));
      state.stars = Array.from({ length: total }, () => ({
        x: rand() * state.width,
        y: rand() * state.height,
        r: .35 + rand() * 1.25,
        a: .16 + rand() * .48
      }));
    }

    function glow(color) {
      if (state.glowCache.has(color)) return state.glowCache.get(color);
      const size = 180;
      const c = document.createElement("canvas");
      c.width = size;
      c.height = size;
      const g = c.getContext("2d");
      const grd = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
      grd.addColorStop(0, "rgba(255,255,255,.95)");
      grd.addColorStop(.12, color);
      grd.addColorStop(.44, hexToRgba(color, .24));
      grd.addColorStop(1, "rgba(0,0,0,0)");
      g.fillStyle = grd;
      g.fillRect(0, 0, size, size);
      state.glowCache.set(color, c);
      return c;
    }

    function hexToRgba(hex, alpha) {
      const clean = hex.replace("#", "");
      const n = parseInt(clean.length === 3 ? clean.split("").map(ch => ch + ch).join("") : clean, 16);
      return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${alpha})`;
    }

    function project(n) {
      const cy = Math.cos(state.rotY), sy = Math.sin(state.rotY);
      const cx = Math.cos(state.rotX), sx = Math.sin(state.rotX);
      let x = n.bx, y = n.by, z = n.bz;
      const x1 = x * cy - z * sy;
      const z1 = x * sy + z * cy;
      const y1 = y * cx - z1 * sx;
      const z2 = y * sx + z1 * cx;
      const focal = state.radius * 2.55;
      const scale = focal / (focal - z2 * state.radius);
      const centerX = state.width * 0.5;
      const centerY = state.height * 0.54;
      return {
        x: centerX + x1 * state.radius * scale,
        y: centerY + y1 * state.radius * scale,
        z: z2,
        s: scale
      };
    }

    function drawBackground() {
      ctx.clearRect(0, 0, state.width, state.height);
      const bg = ctx.createRadialGradient(state.width * .5, state.height * .58, 20, state.width * .5, state.height * .55, Math.max(state.width, state.height) * .72);
      bg.addColorStop(0, "rgba(42, 25, 92, .38)");
      bg.addColorStop(.42, "rgba(12, 8, 30, .96)");
      bg.addColorStop(1, "rgba(5, 3, 12, 1)");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, state.width, state.height);

      for (const s of state.stars) {
        ctx.globalAlpha = s.a * (0.7 + Math.sin(state.tick * .02 + s.x) * .25);
        ctx.fillStyle = "#bdb5ff";
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

    function drawRings() {
      const cx = state.width * .5;
      const cy = state.height * .55;
      const w = state.radius * 2.25;
      const h = state.radius * .55;
      for (let i = 0; i < 3; i += 1) {
        ctx.save();
        ctx.translate(cx, cy + i * 18);
        ctx.rotate(-0.18 + i * .22 + Math.sin(state.tick * .006 + i) * .025);
        ctx.lineWidth = 1.5 + i * .45;
        ctx.strokeStyle = i === 1 ? "rgba(51,232,255,.18)" : "rgba(255,194,71,.28)";
        ctx.beginPath();
        ctx.ellipse(0, 0, w * (.48 + i * .09), h * (.42 + i * .08), 0, Math.PI * 1.05, Math.PI * 1.9);
        ctx.stroke();
        ctx.restore();
      }
    }

    function drawGraph() {
      const projected = new Map();
      const nodesByDepth = [...state.graph.nodes].map(n => {
        const p = project(n);
        projected.set(n.id, p);
        return { n, p };
      }).sort((a, b) => a.p.z - b.p.z);

      for (const l of state.graph.links) {
        const a = projected.get(l.source);
        const b = projected.get(l.target);
        if (!a || !b) continue;
        const source = state.nodeMap.get(l.source);
        const target = state.nodeMap.get(l.target);
        const front = Math.max(a.z, b.z);
        const isHot = state.hover && (state.hover.id === l.source || state.hover.id === l.target);
        const alpha = isHot ? .34 : Math.max(.026, Math.min(.12, .05 + front * .035));
        ctx.strokeStyle = hexToRgba(colorFor(source || target), alpha);
        ctx.lineWidth = isHot ? 1.15 : .55;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }

      for (const item of nodesByDepth) {
        const n = item.n;
        const p = item.p;
        const degree = state.degree.get(n.id) || 1;
        const color = colorFor(n);
        const front = Math.max(0, p.z + 1) / 2;
        const hot = state.hover && (state.hover.id === n.id || state.adjacency.get(state.hover.id)?.has(n.id));
        const selected = state.selected && state.selected.id === n.id;
        const core = (2.1 + Math.min(8, Math.sqrt(degree) * 1.3)) * p.s;
        const pulse = selected ? 1 + Math.sin(state.tick * .1) * .16 : 1;
        const halo = core * (hot || selected ? 7.5 : 5.4) * pulse;

        ctx.globalAlpha = .24 + front * .58;
        ctx.drawImage(glow(color), p.x - halo, p.y - halo, halo * 2, halo * 2);
        ctx.globalAlpha = 1;

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, core * pulse, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,.88)";
        ctx.beginPath();
        ctx.arc(p.x - core * .24, p.y - core * .24, Math.max(1, core * .34), 0, Math.PI * 2);
        ctx.fill();

        n.sx = p.x;
        n.sy = p.y;
        n.screenR = Math.max(8, halo * .24);
        n.depth = p.z;
      }

      drawLabels(nodesByDepth);
    }

    function drawLabels(nodesByDepth) {
      ctx.font = "600 15px Georgia, serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      for (const { n, p } of nodesByDepth) {
        const visible = state.labels.has(n.id) || (state.hover && state.hover.id === n.id) || (state.selected && state.selected.id === n.id);
        if (!visible || p.z < -.72) continue;
        const label = n.label.length > 32 ? n.label.slice(0, 31) + "..." : n.label;
        ctx.lineWidth = 5;
        ctx.strokeStyle = "rgba(7,5,17,.78)";
        ctx.strokeText(label, p.x, p.y - (n.screenR || 14) - 12);
        ctx.fillStyle = "rgba(244,238,255,.9)";
        ctx.fillText(label, p.x, p.y - (n.screenR || 14) - 12);
      }
    }

    function draw() {
      state.tick += 1;
      if (!state.dragging) state.rotY += 0.0018;
      drawBackground();
      drawRings();
      drawGraph();
      requestAnimationFrame(draw);
    }

    function pickNode(x, y) {
      let best = null;
      let bestD = Infinity;
      for (const n of state.graph.nodes) {
        if (typeof n.sx !== "number") continue;
        const dx = n.sx - x;
        const dy = n.sy - y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < (n.screenR || 10) && d < bestD) {
          best = n;
          bestD = d;
        }
      }
      return best;
    }

    function pointerPos(event) {
      const rect = canvas.getBoundingClientRect();
      return { x: event.clientX - rect.left, y: event.clientY - rect.top };
    }

    function showTooltip(node, event) {
      if (!tip || !node) {
        if (tip) tip.style.display = "none";
        return;
      }
      tip.textContent = node.label + " - " + (node.group || "Graph node");
      tip.style.display = "block";
      tip.style.left = Math.min(window.innerWidth - 300, event.clientX + 14) + "px";
      tip.style.top = Math.min(window.innerHeight - 60, event.clientY + 14) + "px";
    }

    function openNode(node) {
      state.selected = node;
      if (!nodePanel || !node) return;
      nodePanel.classList.add("open");
      if (nodeTitle) nodeTitle.textContent = node.label;
      if (nodeCommunity) nodeCommunity.textContent = node.group || "Graph node";
      if (nodeMeta) nodeMeta.textContent = `${state.degree.get(node.id) || 0} links` + (node.file ? ` - ${node.file}` : "");
      if (nodeLinks) {
        const related = [...(state.adjacency.get(node.id) || [])].slice(0, 10)
          .map(id => state.nodeMap.get(id))
          .filter(Boolean);
        nodeLinks.innerHTML = related.length
          ? related.map(n => `<span>${escapeHtml(n.label)}</span>`).join("")
          : "<span>No visible links</span>";
      }
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
    }

    function renderSearch(query) {
      if (!searchResults) return;
      const q = String(query || "").trim().toLowerCase();
      if (!q) {
        searchResults.classList.remove("open");
        searchResults.innerHTML = "";
        return;
      }
      const matches = state.graph.nodes
        .filter(n => n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q) || String(n.group).toLowerCase().includes(q))
        .sort((a, b) => (state.degree.get(b.id) || 0) - (state.degree.get(a.id) || 0))
        .slice(0, 8);
      searchResults.innerHTML = matches.map(n => `<button type="button" data-node="${escapeHtml(n.id)}">${escapeHtml(n.label)}</button>`).join("");
      searchResults.classList.toggle("open", matches.length > 0);
    }

    canvas.addEventListener("pointerdown", (event) => {
      state.dragging = true;
      state.lastX = event.clientX;
      state.lastY = event.clientY;
      canvas.setPointerCapture(event.pointerId);
    });
    canvas.addEventListener("pointerup", () => { state.dragging = false; });
    canvas.addEventListener("pointercancel", () => { state.dragging = false; });
    canvas.addEventListener("pointermove", (event) => {
      const pos = pointerPos(event);
      if (state.dragging) {
        state.rotY += (event.clientX - state.lastX) * 0.006;
        state.rotX += (event.clientY - state.lastY) * 0.004;
        state.rotX = Math.max(-1.1, Math.min(.7, state.rotX));
        state.lastX = event.clientX;
        state.lastY = event.clientY;
      }
      state.hover = pickNode(pos.x, pos.y);
      showTooltip(state.hover, event);
    });
    canvas.addEventListener("mouseleave", () => {
      state.hover = null;
      if (tip) tip.style.display = "none";
    });
    canvas.addEventListener("click", (event) => {
      const pos = pointerPos(event);
      const node = pickNode(pos.x, pos.y);
      if (node) openNode(node);
    });
    canvas.addEventListener("dblclick", () => {
      state.rotX = -0.34;
      state.rotY = 0.18;
      state.zoom = 1;
      resize();
    });
    canvas.addEventListener("wheel", (event) => {
      event.preventDefault();
      state.zoom = Math.max(.55, Math.min(1.75, state.zoom + (event.deltaY < 0 ? .07 : -.07)));
      resize();
    }, { passive: false });

    host.querySelector("#closeNodePanel")?.addEventListener("click", () => nodePanel?.classList.remove("open"));
    search?.addEventListener("input", () => renderSearch(search.value));
    searchResults?.addEventListener("click", (event) => {
      const btn = event.target.closest("button[data-node]");
      if (!btn) return;
      const node = state.nodeMap.get(btn.dataset.node);
      if (node) openNode(node);
    });

    async function loadFromSource() {
      const src = options.src || host.dataset.graphSrc || new URLSearchParams(location.search).get("graph");
      if (!src) return;
      try {
        const response = await fetch(src, { cache: "no-store" });
        if (!response.ok) throw new Error("HTTP " + response.status);
        prepareGraph(await response.json());
      } catch (err) {
        console.warn("NebulaGraph: using embedded sample graph because data source failed:", err);
      }
    }

    prepareGraph(state.graph);
    resize();
    window.addEventListener("resize", resize);
    loadFromSource();
    requestAnimationFrame(draw);

    return {
      setGraph: prepareGraph,
      resize,
      destroy() {
        window.removeEventListener("resize", resize);
      }
    };
  }

  window.NebulaGraph = { mount, normalizeGraph, createSampleGraph };

  document.addEventListener("DOMContentLoaded", function () {
    const shell = document.querySelector(".nebula-shell");
    if (shell && !window.__NEBULA_GRAPH_AUTO_MOUNTED__) {
      window.__NEBULA_GRAPH_AUTO_MOUNTED__ = true;
      window.nebulaGraph = mount(shell);
    }
  });
}());
