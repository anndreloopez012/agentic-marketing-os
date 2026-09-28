#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import html
import os
import re
import shutil
import shlex
import subprocess
import sys
from urllib.parse import quote
from collections import Counter, defaultdict
from pathlib import Path

from portable_paths import DATA_ROOT, GRAPHIFY_BIN, GRAPH_ROOT, MEMORIA_ROOT, VAULT_ROOT

try:
    import graphify  # noqa: F401
except ModuleNotFoundError:
    if GRAPHIFY_BIN.exists():
        first_line = GRAPHIFY_BIN.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
        shebang = shlex.split(first_line.removeprefix("#!").strip())
        interpreter = shebang[0] if shebang else ""
        if interpreter and Path(interpreter).exists() and Path(interpreter).absolute() != Path(sys.executable).absolute():
            os.execv(interpreter, [interpreter, str(Path(__file__).resolve()), *sys.argv[1:]])
    raise SystemExit("Graphify no esta instalado. Ejecuta .memoria-system/install/bootstrap-macos.sh")

import networkx as nx

from graphify.analyze import god_nodes, surprising_connections
from graphify.build import build_from_json
from graphify.cluster import cluster, cohesion_score
from graphify.export import to_html, to_json
from graphify.report import generate

INDEX_PATH = DATA_ROOT / "memoria_index.json"
GRAPH_OUT = GRAPH_ROOT
VAULT_GRAPHIFY = MEMORIA_ROOT / "Graphify"
EXCLUDED_DIRS = {"Graphify", ".obsidian", ".git", ".memoria-system"}

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def slug(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip()
    return re.sub(r"[-\s]+", "-", cleaned).strip("-").lower() or "sin-nombre"


def safe_name(text: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|#^[\]]', "", text.replace("\n", " ")).strip()
    cleaned = re.sub(r"\.(md|mdx|qmd|markdown)$", "", cleaned, flags=re.IGNORECASE)
    return cleaned or "unnamed"


def title_from_text(path: Path, text: str) -> str:
    match = H1_RE.search(text)
    if match:
        return match.group(1).strip()
    return path.stem


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def list_note_files() -> list[Path]:
    notes: list[Path] = []
    for path in MEMORIA_ROOT.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        notes.append(path)
    return sorted(notes)


def build_aliases(notes: list[Path]) -> dict[str, list[Path]]:
    aliases: dict[str, list[Path]] = defaultdict(list)
    for note in notes:
        rel_memoria = note.relative_to(MEMORIA_ROOT)
        rel_vault = note.relative_to(VAULT_ROOT)
        stem = note.stem
        aliases[stem.casefold()].append(note)
        aliases[str(rel_memoria.with_suffix("")).casefold()].append(note)
        aliases[str(rel_vault.with_suffix("")).casefold()].append(note)
    return aliases


def parse_wikilinks(text: str) -> list[str]:
    links: list[str] = []
    for match in WIKILINK_RE.findall(text):
        target = match.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            links.append(target)
    return links


def resolve_link(source: Path, target: str, aliases: dict[str, list[Path]]) -> Path | None:
    raw = target.replace("\\", "/").strip()
    if "/" in raw or raw.startswith("."):
        candidate = (source.parent / raw).with_suffix(".md").resolve()
        if candidate.exists():
            return candidate
        candidate = (VAULT_ROOT / raw).with_suffix(".md").resolve()
        if candidate.exists():
            return candidate
        candidate = (MEMORIA_ROOT / raw).with_suffix(".md").resolve()
        if candidate.exists():
            return candidate

    matches = aliases.get(raw.casefold(), [])
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    source_parts = set(source.relative_to(MEMORIA_ROOT).parts)
    same_branch = [item for item in matches if source_parts & set(item.relative_to(MEMORIA_ROOT).parts)]
    return same_branch[0] if same_branch else matches[0]


def note_node_id(note: Path) -> str:
    return f"note::{note.relative_to(MEMORIA_ROOT).as_posix()}"


def concept_node_id(kind: str, value: str) -> str:
    return f"{kind}::{slug(value)}"


def relative_obsidian_ref(path: Path, base_dir: Path) -> str:
    return os.path.relpath(path.with_suffix(""), base_dir).replace("\\", "/")


def obsidian_note_link(path: Path, base_dir: Path, label: str) -> str:
    """Use a Markdown link when # would be parsed as an Obsidian heading."""
    reference = relative_obsidian_ref(path, base_dir)
    if "#" in reference:
        href = quote(f"{reference}.md", safe="/.-_~")
        return f"[{label}](<{href}>)"
    return f"[[{reference}|{label}]]"


def community_label(graph, members: list[str]) -> str:
    folder_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    note_labels: list[str] = []
    for node_id in members:
        data = graph.nodes[node_id]
        label = data.get("label", node_id)
        if label.startswith("Familia: "):
            family_counts[label.replace("Familia: ", "", 1)] += 1
        source_file = data.get("source_file", "")
        if source_file:
            parts = Path(source_file).parts
            if len(parts) >= 2:
                folder_counts[parts[1]] += 1
        if data.get("type") != "concept":
            note_labels.append(label)

    if family_counts:
        return f"{family_counts.most_common(1)[0][0]} Workspace"
    if folder_counts:
        return f"{folder_counts.most_common(1)[0][0]} Notes"
    if note_labels:
        return " + ".join(note_labels[:2])
    return "Community"


def unique_community_labels(base_labels: dict[int, str]) -> dict[int, str]:
    counts: Counter[str] = Counter(base_labels.values())
    seen: Counter[str] = Counter()
    result: dict[int, str] = {}
    for cid, label in base_labels.items():
        if counts[label] == 1:
            result[cid] = label
            continue
        seen[label] += 1
        result[cid] = f"{label} #{seen[label]}"
    return result


def create_community_hub_notes(graph, communities: dict[int, list[str]], labels: dict[int, str], output_dir: Path) -> None:
    node_community = {node: cid for cid, members in communities.items() for node in members}
    for cid, members in communities.items():
        label = labels[cid]
        filename = output_dir / f"_COMMUNITY_{safe_name(label)}.md"
        lines = [f"# {label}", "", "## Notas"]
        note_members = [node for node in members if graph.nodes[node].get("type") != "concept"]
        for node_id in sorted(note_members, key=lambda item: graph.nodes[item].get("label", item)):
            source_file = graph.nodes[node_id].get("source_file")
            if not source_file:
                continue
            note_path = VAULT_ROOT / source_file
            label_text = graph.nodes[node_id].get("label", node_id)
            lines.append(f"- {obsidian_note_link(note_path, output_dir, label_text)}")

        linked_communities: Counter[int] = Counter()
        for node_id in members:
            for neighbor in graph.neighbors(node_id):
                other = node_community.get(neighbor)
                if other is not None and other != cid:
                    linked_communities[other] += 1

        if linked_communities:
            lines.extend(["", "## Conexiones"])
            for other_cid, edge_count in linked_communities.most_common(8):
                other_label = labels[other_cid]
                lines.append(f"- [[_COMMUNITY_{safe_name(other_label)}|{other_label}]]: {edge_count} enlace(s)")

        filename.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_dashboard(
    report_path: Path,
    canvas_path: Path,
    html_path: Path,
    graph_path: Path,
    labels: dict[int, str],
    communities: dict[int, list[str]],
) -> None:
    lines = [
        "# Graphify - Panel",
        "",
        "Panel operativo del grafo local de memoria.",
        "",
        "## Artefactos",
        f"- [[{report_path.stem}|Reporte Graphify]]",
        f"- [[{canvas_path.stem}|Canvas Graphify]]",
        f"- [Vista HTML Graphify]({html_path.name})",
        "- [[../Runbooks/Graphify - Sistema portable|Sistema portable y migracion]]",
        "",
        "## Navegacion por capas",
        "- [[../Proyectos/Indice de Proyectos Segmentados|Proyectos por familia y secciones]]",
        "- [[../Reportes/Cobertura PROYECTOS en Obsidian y Graphify|Cobertura proyecto por proyecto]]",
        "- [[../Arquitectura/Indice Corporativo|Arquitectura corporativa]]",
        "- [[../Proyectos Git/Indice Tecnico Profundo|Indice tecnico profundo]]",
        "- [[../Runbooks/Indice de Skills Codex|Runbooks y skills de Codex]]",
        "- [[../Skills/Codex Skills|Skills Codex]] y [[../Skills/Claude Skills|Skills Claude]]",
        "- [[../Cursos/MARKETING IA/00 - Nucleo Marketing IA|Cursos - Marketing IA]]",
        "- [[../Bitacora/Registro de Trabajo|Bitacora]]",
        "- [[../Herramientas/Agentes IA - Indice|Herramientas y agentes IA]]",
        "",
        "## Comunidades",
    ]
    prominent = sorted(communities.items(), key=lambda item: len(item[1]), reverse=True)
    eligible = []
    for cid, members in prominent:
        note_members = sum(1 for node in members if not str(node).startswith(("family::", "role::", "state::", "stack::")))
        if note_members >= 3:
            eligible.append((cid, members, note_members))
    for cid, members, note_members in eligible[:30]:
        label = labels[cid]
        lines.append(f"- [[_COMMUNITY_{safe_name(label)}|{label}]]: {note_members} nota(s)")
    hidden = len(communities) - min(30, len(eligible))
    if hidden:
        lines.append(f"- Comunidades secundarias ocultas en este panel: {hidden}")
    lines.extend([
        "",
        "## Uso en terminal",
        "```bash",
        "graphify query \"Que proyectos conectan backend y frontend\" --graph \"$OBSIDIAN_VAULT/.memoria-system/graph/graph.json\"",
        "graphify path \"Inicio Memoria\" \"Contexto Operativo\" --graph \"$OBSIDIAN_VAULT/.memoria-system/graph/graph.json\"",
        "graphify explain \"Contexto Operativo\" --graph \"$OBSIDIAN_VAULT/.memoria-system/graph/graph.json\"",
        "```",
    ])
    (VAULT_GRAPHIFY / "Graphify - Panel.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_obsidian_graph_canvas(graph, output_path: Path, node_filenames: dict[str, str]) -> None:
    """Write an Obsidian-native Canvas that visually behaves like a graph.

    File nodes remain directly openable in Obsidian. Concept nodes supply the
    dense hubs that make project, stack, skill, and family relationships visible.
    The deterministic force layout keeps the same organic composition on refresh.
    """
    undirected = graph.to_undirected()
    components = sorted(
        (set(members) for members in nx.connected_components(undirected) if len(members) > 1),
        key=lambda members: (-len(members), min(map(str, members))),
    )

    # Obsidian Canvas has no live physics engine. Build a deterministic packed
    # force layout instead: one dense central sphere, one secondary lobe, and
    # the remaining connected communities as small surrounding satellites.
    # Isolated notes stay in graph.json but are intentionally omitted here,
    # because they have no relation to draw and otherwise form an artificial ring.
    positions: dict[str, tuple[float, float]] = {}
    component_indexes: dict[str, int] = {}
    golden_angle = math.pi * (3 - math.sqrt(5))
    for component_index, members in enumerate(components):
        if component_index == 0:
            budget = 600
            center_x, center_y = -0.16, 0.10
            component_radius = 1.0
        elif component_index == 1:
            budget = 100
            center_x, center_y = 0.92, -0.72
            component_radius = 0.31
        else:
            selected = sorted(members, key=str)
            satellite_index = component_index - 2
            angle = -math.pi / 2 + satellite_index * golden_angle
            ring = 1.12 + 0.09 * (satellite_index // 9)
            center_x = math.cos(angle) * ring * 1.08
            center_y = math.sin(angle) * ring * 0.92
            component_radius = 0.10 + min(0.13, math.sqrt(len(members)) * 0.025)

        if component_index <= 1:
            ranked = sorted(members, key=lambda node: (-undirected.degree(node), str(node)))
            concept_nodes = [node for node in ranked if graph.nodes[node].get("type") == "concept"]
            selected_set = set(concept_nodes[:budget])
            for node_id in ranked:
                if len(selected_set) >= budget:
                    break
                selected_set.add(node_id)
            selected = sorted(selected_set, key=lambda node: (-undirected.degree(node), str(node)))

        for node_id in selected:
            component_indexes[node_id] = component_index

        if component_index == 0:
            # Pack the largest community into a broad, irregular nebula. Hubs
            # remain near the core, while the warped edge avoids a perfect disc.
            count = len(selected)
            for rank, node_id in enumerate(selected):
                radius = math.sqrt((rank + 0.45) / count)
                base_angle = rank * golden_angle
                boundary_warp = 0.94 + 0.07 * math.sin(base_angle * 3.0 + 0.8) + 0.035 * math.sin(base_angle * 7.0)
                angle = base_angle + 0.12 * math.sin((rank + 1) * 12.9898)
                positions[node_id] = (
                    center_x + math.cos(angle) * radius * boundary_warp * component_radius,
                    center_y + math.sin(angle) * radius * boundary_warp * component_radius * 0.94,
                )
            continue

        subgraph = undirected.subgraph(selected)
        local = nx.spring_layout(
            subgraph,
            seed=42 + component_index,
            iterations=125 if component_index <= 1 else 70,
            k=(1.55 / math.sqrt(max(len(selected), 2))) if component_index <= 1 else None,
            scale=1.0,
            center=(0.0, 0.0),
        )
        max_radius = max(math.hypot(float(point[0]), float(point[1])) for point in local.values()) or 1.0
        for node_id, point in local.items():
            positions[node_id] = (
                center_x + float(point[0]) / max_radius * component_radius,
                center_y + float(point[1]) / max_radius * component_radius * 0.94,
            )

    canvas_nodes: list[dict] = []
    node_canvas_ids: dict[str, str] = {}
    for index, node_id in enumerate(sorted(positions, key=str)):
        data = graph.nodes[node_id]
        degree = graph.degree(node_id)
        diameter = round(5 + min(29, math.log2(degree + 1) * 3.8))
        if data.get("type") == "concept":
            diameter += 3

        x, y = positions[node_id]
        canvas_id = f"graphify-node-{index}"
        node_canvas_ids[node_id] = canvas_id
        kind = str(node_id).split("::", 1)[0]
        component_index = component_indexes[node_id]
        if component_index == 1:
            color = "3"
        elif component_index >= 2:
            color = ("3", "3", "2", "3", "1")[(component_index - 2) % 5]
        elif data.get("type") == "note":
            color = "1"
        elif kind in {"ai", "skill-category", "skill-name"}:
            color = "3"
        else:
            color = "2"

        common = {
            "id": canvas_id,
            "x": round(x * 620 - diameter / 2),
            "y": round(y * 580 - diameter / 2),
            "width": diameter,
            "height": diameter,
            "color": color,
        }
        if data.get("type") == "note" and node_id in node_filenames:
            canvas_nodes.append(
                {
                    **common,
                    "type": "text",
                    "text": f"[[{node_filenames[node_id]}|{data.get('label', node_id)}]]",
                }
            )
        else:
            canvas_nodes.append(
                {
                    **common,
                    "type": "text",
                    "text": str(data.get("label", node_id)),
                }
            )

    canvas_edges: list[dict] = []
    ordered_edges = sorted(graph.edges(data=True), key=lambda item: (str(item[0]), str(item[1]), str(item[2].get("relation", ""))))
    for index, (source, target, _data) in enumerate(ordered_edges):
        if source == target or source not in node_canvas_ids or target not in node_canvas_ids:
            continue
        canvas_edges.append(
            {
                "id": f"graphify-edge-{index}",
                "fromNode": node_canvas_ids[source],
                "toNode": node_canvas_ids[target],
                "fromEnd": "none",
                "toEnd": "none",
                "color": "#7899C2",
            }
        )

    geometry = {
        node["id"]: {
            "cx": node["x"] + node["width"] / 2,
            "cy": node["y"] + node["height"] / 2,
            "radius": node["width"] / 2,
            "color": node["color"],
            "label": str(node.get("text", "")),
        }
        for node in canvas_nodes
    }
    padding = 70
    min_x = min(node["x"] for node in canvas_nodes) - padding
    min_y = min(node["y"] for node in canvas_nodes) - padding
    max_x = max(node["x"] + node["width"] for node in canvas_nodes) + padding
    max_y = max(node["y"] + node["height"] for node in canvas_nodes) + padding
    svg_width = round(max_x - min_x)
    svg_height = round(max_y - min_y)
    palette = {"1": "#47a4fa", "2": "#53d5e8", "3": "#ffbc42"}

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="{min_x} {min_y} {svg_width} {svg_height}">',
        "<defs>",
        '<radialGradient id="bg" cx="48%" cy="48%" r="72%"><stop offset="0" stop-color="#0a1a25"/><stop offset="1" stop-color="#050d14"/></radialGradient>',
        '<filter id="hub-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        "</defs>",
        f'<rect x="{min_x}" y="{min_y}" width="{svg_width}" height="{svg_height}" fill="url(#bg)"/>',
        '<g fill="none" stroke="#91aacc" stroke-width="1.25" stroke-opacity="0.28">',
    ]
    for edge in canvas_edges:
        source = geometry[edge["fromNode"]]
        target = geometry[edge["toNode"]]
        svg_lines.append(
            f'<line x1="{source["cx"]:.1f}" y1="{source["cy"]:.1f}" x2="{target["cx"]:.1f}" y2="{target["cy"]:.1f}"/>'
        )
    svg_lines.append("</g>")
    for node in canvas_nodes:
        item = geometry[node["id"]]
        raw_label = item["label"]
        label = raw_label.split("|", 1)[-1].removesuffix("]] ").removesuffix("]]") if raw_label.startswith("[[") else raw_label
        glow = ' filter="url(#hub-glow)"' if item["radius"] >= 18 else ""
        svg_lines.append(
            f'<circle cx="{item["cx"]:.1f}" cy="{item["cy"]:.1f}" r="{item["radius"]:.1f}" fill="{palette[item["color"]]}"{glow}><title>{html.escape(label)}</title></circle>'
        )
    svg_lines.append("</svg>")

    svg_path = output_path.with_suffix(".svg")
    svg_path.write_text("\n".join(svg_lines) + "\n", encoding="utf-8")
    svg_vault_path = svg_path.relative_to(VAULT_ROOT).as_posix()
    output_path.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "id": "graphify-render",
                        "type": "file",
                        "file": svg_vault_path,
                        "x": 0,
                        "y": 0,
                        "width": svg_width,
                        "height": svg_height,
                    }
                ],
                "edges": [],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> None:
    GRAPH_OUT.mkdir(parents=True, exist_ok=True)
    (GRAPH_OUT / ".graphify_root").write_text(str(MEMORIA_ROOT), encoding="utf-8")
    (GRAPH_OUT / ".graphify_python").write_text(sys.executable, encoding="utf-8")
    VAULT_GRAPHIFY.mkdir(parents=True, exist_ok=True)
    for stale in VAULT_GRAPHIFY.glob("_COMMUNITY_*.md"):
        stale.unlink(missing_ok=True)
    for stale_name in ("Graphify - Panel.md", "Graphify - Memoria.canvas", "Graphify - Memoria.svg", "Reporte Graphify.md", "Graphify - Memoria.html", "Graphify - Arbol.html"):
        (VAULT_GRAPHIFY / stale_name).unlink(missing_ok=True)

    notes = list_note_files()
    aliases = build_aliases(notes)

    nodes: list[dict] = []
    edges: list[dict] = []
    note_ids: dict[Path, str] = {}
    note_titles: dict[Path, str] = {}
    total_words = 0

    for note in notes:
        text = read_text(note)
        title = title_from_text(note, text)
        total_words += word_count(text)
        node_id = note_node_id(note)
        note_ids[note] = node_id
        note_titles[note] = title
        nodes.append(
            {
                "id": node_id,
                "label": title,
                "file_type": "document",
                "source_file": note.relative_to(VAULT_ROOT).as_posix(),
                "type": "note",
            }
        )

    for note in notes:
        source_id = note_ids[note]
        text = read_text(note)
        for raw_target in parse_wikilinks(text):
            resolved = resolve_link(note, raw_target, aliases)
            if resolved and resolved in note_ids:
                edges.append(
                    {
                        "source": source_id,
                        "target": note_ids[resolved],
                        "relation": "references",
                        "confidence": "EXTRACTED",
                        "source_file": note.relative_to(VAULT_ROOT).as_posix(),
                    }
                )

    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    concept_nodes: dict[str, dict] = {}

    def ensure_concept(kind: str, value: str, label_prefix: str) -> str:
        node_id = concept_node_id(kind, value)
        if node_id not in concept_nodes:
            concept_nodes[node_id] = {
                "id": node_id,
                "label": f"{label_prefix}: {value}",
                "file_type": "concept",
                "source_file": "",
                "type": "concept",
            }
        return node_id

    for project in index_data.get("projects", []):
        project_note = MEMORIA_ROOT / "Proyectos Git" / f"{project['name']}.md"
        project_id = note_ids.get(project_note)
        if not project_id:
            continue

        family_id = ensure_concept("family", project.get("family", "Otros"), "Familia")
        role_id = ensure_concept("role", project.get("role", "app"), "Rol")
        state_label = "Con cambios locales" if project.get("dirty") else "Sin cambios locales"
        state_id = ensure_concept("state", state_label, "Estado")

        edges.extend(
            [
                {
                    "source": project_id,
                    "target": family_id,
                    "relation": "belongs_to_family",
                    "confidence": "EXTRACTED",
                    "source_file": project_note.relative_to(VAULT_ROOT).as_posix(),
                },
                {
                    "source": project_id,
                    "target": role_id,
                    "relation": "has_role",
                    "confidence": "EXTRACTED",
                    "source_file": project_note.relative_to(VAULT_ROOT).as_posix(),
                },
                {
                    "source": project_id,
                    "target": state_id,
                    "relation": "has_status",
                    "confidence": "EXTRACTED",
                    "source_file": project_note.relative_to(VAULT_ROOT).as_posix(),
                },
            ]
        )

        for signal in project.get("signals", [])[:8]:
            stack_id = ensure_concept("stack", signal, "Stack")
            edges.append(
                {
                    "source": project_id,
                    "target": stack_id,
                    "relation": "uses_stack",
                    "confidence": "EXTRACTED",
                    "source_file": project_note.relative_to(VAULT_ROOT).as_posix(),
                }
            )

    for asset in index_data.get("multimedia_assets", []):
        note_name = asset.get("note_name") or f"{safe_name(asset.get('owner', 'General'))} - {safe_name(asset.get('name', 'activo'))}"
        asset_note = MEMORIA_ROOT / "Multimedia" / "Activos" / f"{note_name}.md"
        asset_id = note_ids.get(asset_note)
        if not asset_id:
            continue

        kind_id = ensure_concept("asset-kind", asset.get("kind", "desconocido"), "Tipo de activo")
        owner_id = ensure_concept("asset-owner", f"{asset.get('owner_type', 'biblioteca')}: {asset.get('owner', 'General')}", "Propietario multimedia")
        ext_id = ensure_concept("asset-extension", asset.get("extension", "sin-extension"), "Extension")
        for target_id, relation in (
            (kind_id, "has_asset_kind"),
            (owner_id, "belongs_to_asset_owner"),
            (ext_id, "has_asset_extension"),
        ):
            edges.append(
                {
                    "source": asset_id,
                    "target": target_id,
                    "relation": relation,
                    "confidence": "EXTRACTED",
                    "source_file": asset_note.relative_to(VAULT_ROOT).as_posix(),
                }
            )

    for skill in index_data.get("ai_skills", []):
        note_name = skill.get("note_name") or f"{safe_name(skill.get('ai', 'IA'))} - {safe_name(skill.get('name', 'skill'))}"
        skill_note = MEMORIA_ROOT / "Skills" / f"{note_name}.md"
        skill_id = note_ids.get(skill_note)
        if not skill_id:
            continue

        ai_id = ensure_concept("ai", skill.get("ai", "desconocida"), "IA")
        category_id = ensure_concept("skill-category", skill.get("category", "General"), "Categoria skill")
        skill_name_id = ensure_concept("skill-name", skill.get("name", "skill"), "Skill")
        for target_id, relation in (
            (ai_id, "available_in_ai"),
            (category_id, "has_skill_category"),
            (skill_name_id, "implements_skill"),
        ):
            edges.append(
                {
                    "source": skill_id,
                    "target": target_id,
                    "relation": relation,
                    "confidence": "EXTRACTED",
                    "source_file": skill_note.relative_to(VAULT_ROOT).as_posix(),
                }
            )

    nodes.extend(concept_nodes.values())

    extraction = {"nodes": nodes, "edges": edges}
    graph = build_from_json(extraction)
    communities = cluster(graph, exclude_hubs_percentile=95)
    labels = unique_community_labels({cid: community_label(graph, members) for cid, members in communities.items()})
    cohesion_scores = {cid: round(cohesion_score(graph, members), 3) for cid, members in communities.items()}
    report_text = generate(
        graph,
        communities,
        cohesion_scores,
        labels,
        god_nodes(graph, top_n=10),
        surprising_connections(graph, communities, top_n=8),
        {"total_files": len(notes), "total_words": total_words},
        {"input": 0, "output": 0},
        "Memoria Obsidian",
        suggested_questions=[
            {
                "question": "Que notas conectan varias familias de proyectos?",
                "why": "La mezcla de wikilinks y metadatos de familia ayuda a detectar notas puente.",
            },
            {
                "question": "Que runbooks o decisiones afectan mas proyectos?",
                "why": "Las comunidades y nodos mas conectados dejan ver documentos operativos con mayor alcance.",
            },
            {
                "question": "Que proyectos tienen cambios locales y contexto relacionado?",
                "why": "Los estados locales del indice se combinan con la memoria navegable del vault.",
            },
        ],
        built_at_commit=None,
    )

    graph_json_path = GRAPH_OUT / "graph.json"
    report_path = GRAPH_OUT / "GRAPH_REPORT.md"
    html_path = GRAPH_OUT / "graph.html"
    tree_path = GRAPH_OUT / "GRAPH_TREE.html"

    to_json(graph, communities, str(graph_json_path), force=True, community_labels=labels)
    report_path.write_text(report_text, encoding="utf-8")
    to_html(graph, communities, str(html_path), community_labels=labels, node_limit=500)

    subprocess.run(
        [
            str(GRAPHIFY_BIN),
            "tree",
            "--graph",
            str(graph_json_path),
            "--output",
            str(tree_path),
            "--label",
            "Memoria Obsidian",
        ],
        check=True,
    )

    canvas_map = {}
    for note, node_id in note_ids.items():
        canvas_map[node_id] = note.relative_to(VAULT_ROOT).with_suffix("").as_posix()

    canvas_path = VAULT_GRAPHIFY / "Graphify - Memoria.canvas"
    export_obsidian_graph_canvas(graph, canvas_path, canvas_map)

    create_community_hub_notes(graph, communities, labels, VAULT_GRAPHIFY)

    vault_report = VAULT_GRAPHIFY / "Reporte Graphify.md"
    vault_html = VAULT_GRAPHIFY / "Graphify - Memoria.html"
    vault_tree = VAULT_GRAPHIFY / "Graphify - Arbol.html"
    shutil.copy2(report_path, vault_report)
    shutil.copy2(html_path, vault_html)
    shutil.copy2(tree_path, vault_tree)

    build_dashboard(vault_report, canvas_path, vault_html, graph_json_path, labels, communities)

    print(f"Graphify memory graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"Portable graph output: {GRAPH_OUT}")
    print(f"Obsidian output: {VAULT_GRAPHIFY}")


if __name__ == "__main__":
    main()
