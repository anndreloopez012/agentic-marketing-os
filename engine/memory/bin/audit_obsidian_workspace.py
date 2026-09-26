#!/usr/bin/env python3
"""Generate a concise, portable health report for the operational vault."""
from __future__ import annotations

import json
import re
from pathlib import Path

from portable_paths import MEMORIA_ROOT, VAULT_ROOT

REPORT = MEMORIA_ROOT / "Reportes" / "Salud del espacio de trabajo Obsidian.md"
REQUIRED_CONFIG = (
    "app.json", "appearance.json", "backlink.json", "bookmarks.json",
    "core-plugins.json", "daily-notes.json", "graph.json", "templates.json",
    "types.json", "workspace.json",
)
REQUIRED_PROPERTIES = ("tipo", "proyecto", "familia", "rol", "raiz", "estado", "actualizado")
REQUIRED_COMMUNITY_PLUGINS = ("dataview", "omnisearch")


def frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError:
        return {}
    result: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line or line.startswith((" ", "-")):
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def main() -> int:
    notes = list(MEMORIA_ROOT.rglob("*.md"))
    with_metadata = 0
    project_homes: list[Path] = []
    incomplete: list[str] = []
    oversized: list[str] = []
    sensitive_names: list[str] = []
    for path in notes:
        text = path.read_text(encoding="utf-8", errors="ignore")
        props = frontmatter(text)
        with_metadata += int(bool(props))
        if path.name == "00 - Inicio.md" and "Proyectos" in path.parts:
            project_homes.append(path)
            missing = [key for key in REQUIRED_PROPERTIES if key not in props]
            if missing:
                incomplete.append(f"{path.relative_to(VAULT_ROOT)}: {', '.join(missing)}")
        if " - Segmentos" not in str(path) and "Graphify" not in path.parts and path.stat().st_size > 100_000:
            oversized.append(str(path.relative_to(VAULT_ROOT)))
    for path in VAULT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        lower = path.name.lower()
        if (
            lower == ".env"
            or lower.startswith(".env.")
            or lower.startswith(".env_")
            or lower.endswith((".pem", ".key", ".p12", ".pfx"))
            or lower.startswith(("id_rsa", "id_ed25519"))
        ):
            sensitive_names.append(str(path.relative_to(VAULT_ROOT)))

    config = VAULT_ROOT / ".obsidian"
    missing_config = [name for name in REQUIRED_CONFIG if not (config / name).is_file()]
    invalid_json: list[str] = []
    for name in REQUIRED_CONFIG:
        path = config / name
        if not path.exists():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            invalid_json.append(name)
    plugin_findings: list[str] = []
    try:
        enabled = json.loads((config / "community-plugins.json").read_text(encoding="utf-8"))
    except Exception:
        enabled = []
        plugin_findings.append("community-plugins.json faltante o invalido")
    for plugin in REQUIRED_COMMUNITY_PLUGINS:
        root = config / "plugins" / plugin
        if plugin not in enabled or not all((root / name).is_file() for name in ("manifest.json", "main.js")):
            plugin_findings.append(f"Plugin incompleto o deshabilitado: {plugin}")

    status = "saludable" if not any((incomplete, oversized, sensitive_names, missing_config, invalid_json, plugin_findings)) else "requiere-atencion"
    lines = [
        "---\n",
        "tipo: reporte-salud-obsidian\n",
        f"estado: {status}\n",
        "generado: true\n",
        "tags:\n  - memoria\n  - obsidian\n  - salud\n",
        "---\n\n",
        "# Salud del espacio de trabajo Obsidian\n\n",
        f"- Notas visibles: **{len(notes)}**\n",
        f"- Notas con propiedades: **{with_metadata}**\n",
        f"- Proyectos modulares: **{len(project_homes)}**\n",
        f"- Proyectos con propiedades incompletas: **{len(incomplete)}**\n",
        f"- Notas grandes sin segmentar: **{len(oversized)}**\n",
        f"- Configuraciones faltantes o invalidas: **{len(missing_config) + len(invalid_json)}**\n",
        f"- Archivos sensibles por nombre: **{len(sensitive_names)}**\n\n",
        f"- Problemas de plugins requeridos: **{len(plugin_findings)}**\n\n",
        "## Acciones\n",
    ]
    findings = (
        [("Propiedades", item) for item in incomplete]
        + [("Tamaño", item) for item in oversized]
        + [("Configuración faltante", item) for item in missing_config]
        + [("JSON inválido", item) for item in invalid_json]
        + [("Sensible", item) for item in sensitive_names]
        + [("Plugin", item) for item in plugin_findings]
    )
    if findings:
        lines.extend(f"- **{kind}:** `{item}`\n" for kind, item in findings[:100])
    else:
        lines.append("- Sin hallazgos críticos en la configuración operativa.\n")
    lines.extend([
        "\n## Accesos\n",
        "- [[../Centro de Operaciones|Centro de Operaciones]]\n",
        "- [[Cobertura PROYECTOS en Obsidian y Graphify|Cobertura]]\n",
        "- [[Incorporacion automatica de proyectos|Incorporación automática]]\n",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("".join(lines), encoding="utf-8")
    print(f"Obsidian workspace audit: {status}; report={REPORT}")
    return 0 if status == "saludable" else 1


if __name__ == "__main__":
    raise SystemExit(main())
