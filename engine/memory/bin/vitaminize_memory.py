#!/usr/bin/env python3
"""Build the operational intelligence layer for the portable memory vault."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from portable_paths import DATA_ROOT, MEMORIA_ROOT, PROJECT_GRAPHS_ROOT, SETTINGS, VAULT_ROOT

INDEX_PATH = DATA_ROOT / "memoria_index.json"
REGISTRY_PATH = DATA_ROOT / "project_registry.json"
WORKLOG_PATH = DATA_ROOT / "memoria_worklog.json"
STATUS_PATH = DATA_ROOT / "operational_status.json"
REPORTS = MEMORIA_ROOT / "Reportes"
PROJECTS = MEMORIA_ROOT / "Proyectos"
ARCHITECTURE = MEMORIA_ROOT / "Arquitectura"
DEPENDENCIES_PATH = DATA_ROOT / "project_dependencies.json"


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe(value: str) -> str:
    return re.sub(r'[\\/*?:"<>|#^[\]]', "-", value).strip().strip(".") or "Sin nombre"


def iso_from_ns(value: int | float | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromtimestamp(int(value) / 1_000_000_000, tz=dt.timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


def parse_iso(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        result = dt.datetime.fromisoformat(value)
        return result if result.tzinfo else result.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def registry_entry(project: dict, registry: dict) -> dict:
    key = f"{project.get('source_root', 'PROYECTOS')}/{project.get('folder_name', project['name'])}"
    return registry.get("projects", {}).get(key, {})


def project_home(project: dict) -> Path:
    return PROJECTS / safe(project["family"]) / safe(project["name"]) / "00 - Inicio.md"


def simple_frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return {}
    raw = text.split("---\n", 2)[1]
    result = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def missing_projects(registry: dict, active_names: set[str]) -> list[dict]:
    by_name = {simple_frontmatter(path).get("proyecto"): path for path in PROJECTS.rglob("00 - Inicio.md")}
    result = []
    for entry in registry.get("projects", {}).values():
        name = entry.get("name")
        if entry.get("presence") != "missing" or not name or name in active_names:
            continue
        home = by_name.get(name)
        props = simple_frontmatter(home) if home else {}
        result.append({
            "name": name,
            "folder_name": name,
            "source_root": entry.get("root", "PROYECTOS"),
            "path": entry.get("path", "$PROJECTS_ROOT/" + name),
            "family": props.get("familia") or (home.parent.parent.name if home else "Otros"),
            "role": props.get("rol", "por-confirmar"),
            "summary": "La fuente ya no esta disponible; se conserva la memoria historica.",
            "branch": "",
            "last": "",
            "signals": [],
            "dirs": [],
            "services": [],
            "scripts": {},
            "dirty": [],
        })
    return result


def context_path(project: dict) -> Path:
    return PROJECTS / safe(project["family"]) / safe(project["name"]) / "05 - Contexto para IA.md"


def assess(project: dict, registry: dict, previous: dict, now: dt.datetime) -> dict:
    reg = registry_entry(project, registry)
    fingerprint = reg.get("fingerprint", {})
    source_time = iso_from_ns(fingerprint.get("latest_mtime_ns"))
    onboard_time = parse_iso(reg.get("last_onboarded_at"))
    graph_status = reg.get("graph_status", "memory_only")
    home = project_home(project)
    home_time = dt.datetime.fromtimestamp(home.stat().st_mtime, tz=dt.timezone.utc) if home.exists() else None
    reasons: list[str] = []
    critical: list[str] = []
    informational: list[str] = []

    if reg.get("presence") == "missing":
        critical.append("La carpeta fuente ya no esta disponible.")
    if graph_status == "failed":
        critical.append("El snapshot Graphify administrado fallo.")
    if not home.exists():
        critical.append("Falta la ficha modular del proyecto.")
    if reg.get("managed_snapshot") and source_time and (not onboard_time or source_time > onboard_time + dt.timedelta(minutes=5)):
        critical.append("El codigo es mas reciente que el snapshot Graphify administrado.")

    if fingerprint.get("empty") and reg.get("presence") != "missing":
        reasons.append("La carpeta fuente esta vacia; se conserva como inventario.")
    if project.get("dirty"):
        reasons.append(f"Hay {len(project['dirty'])} cambio(s) local(es) sin capturar como estado estable.")
    if not project.get("summary"):
        reasons.append("Falta una descripcion reutilizable desde README.")
    if project.get("is_git") and not project.get("remote"):
        reasons.append("El repositorio no tiene remoto origin detectado.")
    if source_time and now - source_time > dt.timedelta(days=int(SETTINGS.get("vitaminado", {}).get("inactive_days", 180))):
        informational.append("Sin actividad reciente; puede ser un proyecto estable o archivado.")
    if home_time and source_time and source_time > home_time + dt.timedelta(minutes=5):
        critical.append("La fuente cambio despues de la memoria visible.")

    color = "rojo" if critical else ("amarillo" if reasons else "verde")
    stale = bool(critical)
    prior = previous.get("projects", {}).get(project["name"], {}).get("semaforo")
    return {
        "proyecto": project["name"],
        "familia": project["family"],
        "rol": project["role"],
        "raiz": project.get("source_root", "PROYECTOS"),
        "semaforo": color,
        "obsoleto": stale,
        "motivos": critical + reasons,
        "informativo": informational,
        "graph_status": graph_status,
        "managed_snapshot": bool(reg.get("managed_snapshot")),
        "source_updated_at": source_time.isoformat() if source_time else None,
        "snapshot_updated_at": onboard_time.isoformat() if onboard_time else None,
        "memory_updated_at": home_time.isoformat() if home_time else None,
        "previous_semaforo": prior,
        "presence": reg.get("presence", "active"),
    }


def update_home_properties(path: Path, status: dict, today: str) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return
    end = text.find("\n---\n", 4)
    if end < 0:
        return
    front = text[4:end]
    values = {
        "estado": '"ausente"' if status.get("presence") == "missing" else '"activo"',
        "semaforo": f'"{status["semaforo"]}"',
        "obsoleto": "true" if status["obsoleto"] else "false",
        "contexto_ia": "true",
        "ultimo_contexto": today,
    }
    for key, value in values.items():
        pattern = rf"(?m)^{re.escape(key)}:.*$"
        if re.search(pattern, front):
            front = re.sub(pattern, f"{key}: {value}", front)
        else:
            front += f"\n{key}: {value}"
    path.write_text(f"---\n{front}\n---\n{text[end + 5:]}", encoding="utf-8")
    body = path.read_text(encoding="utf-8", errors="ignore")
    if "[[05 - Contexto para IA]]" not in body and "## Navegacion\n" in body:
        body = body.replace("## Navegacion\n", "## Navegacion\n- [[05 - Contexto para IA]]\n", 1)
        path.write_text(body, encoding="utf-8")


def recent_work(project_name: str, worklog: list[dict], limit: int = 6) -> list[dict]:
    return [entry for entry in worklog if entry.get("project") == project_name][-limit:]


def context_note(project: dict, status: dict, worklog: list[dict], edges: list[list], today: str) -> str:
    related = [(a, b, why) for a, b, why in edges if project["name"] in {a, b}]
    work = recent_work(project["name"], worklog)
    commands = list(project.get("scripts", {}).items())[:12]
    findings = status["motivos"] or ["Sin alertas operativas."]
    next_steps = status["motivos"][:4] or ["Mantener el contexto al cerrar trabajo significativo."]
    lines = [
        "---\n",
        'tipo: "contexto-ia"\n',
        f'proyecto: {json.dumps(project["name"], ensure_ascii=False)}\n',
        f'familia: {json.dumps(project["family"], ensure_ascii=False)}\n',
        f'rol: {json.dumps(project["role"], ensure_ascii=False)}\n',
        f'raiz: {json.dumps(project.get("source_root", "PROYECTOS"), ensure_ascii=False)}\n',
        f'estado: "{status["semaforo"]}"\n',
        f'semaforo: "{status["semaforo"]}"\n',
        f'obsoleto: {str(status["obsoleto"]).lower()}\n',
        "generado: true\n",
        f"actualizado: {today}\n",
        'fuente: "inventario-local-y-bitacora"\n',
        'tags:\n  - "memoria"\n  - "contexto-ia"\n',
        "---\n\n",
        f"# {project['name']} — Contexto para IA\n\n",
        "> [!info] Uso\n> Contexto compacto y regenerable. Verificar siempre en el codigo antes de modificar comportamiento.\n\n",
        "## Identidad\n",
        f"- Proposito: {project.get('summary') or 'Por confirmar desde README o contexto manual.'}\n",
        f"- Familia / rol: **{project['family']}** / **{project['role']}**\n",
        f"- Ruta portable: `{project['path']}`\n",
        f"- Rama / ultimo commit: `{project.get('branch') or '-'} / {project.get('last') or '-'}`\n",
        f"- Estado operativo: **{status['semaforo']}** · Graphify: `{status['graph_status']}`\n\n",
        "## Arquitectura y stack\n",
        f"- Stack: {', '.join(project.get('signals') or []) or 'Por confirmar.'}\n",
        f"- Directorios: {', '.join(f'`{x}`' for x in (project.get('dirs') or [])[:15]) or 'Por confirmar.'}\n",
        f"- Servicios: {', '.join(f'`{x}`' for x in (project.get('services') or [])[:12]) or 'No detectados.'}\n",
        f"- Persistencia: {', '.join(x for x in (project.get('signals') or []) if x in {'PostgreSQL','MySQL','SQL Server','MongoDB','Prisma','TypeORM','Sequelize','Strapi'}) or 'No detectada.'}\n\n",
        "## Comandos comprobables\n",
    ]
    lines.extend([f"- `{name}` → `{command}`\n" for name, command in commands] or ["- No se detectaron scripts en `package.json`.\n"])
    lines.extend(["\n## Relaciones\n"])
    if related:
        for source, target, reason in related[:15]:
            other = target if source == project["name"] else source
            lines.append(f"- [[../../../Proyectos Git/{other}|{other}]] — {reason} (**inferida**, confirmar en codigo).\n")
    else:
        lines.append("- Sin relaciones entre proyectos detectadas.\n")
    lines.append("\n## Decisiones y trabajo reciente\n")
    if work:
        for entry in reversed(work):
            lines.append(f"- `{entry.get('timestamp', '-')}` · **{entry.get('type', 'registro')}** · {entry.get('title', 'Sin titulo')} — {entry.get('text', '')[:260]}\n")
    else:
        lines.append("- Sin registros confirmados en la bitacora.\n")
    lines.append("\n## Alertas y riesgos\n")
    lines.extend(f"- {item}\n" for item in findings)
    lines.extend(f"- _Informativo:_ {item}\n" for item in status["informativo"])
    lines.append("\n## Proximas acciones\n")
    lines.extend(f"- [ ] {item}\n" for item in next_steps)
    lines.extend([
        "\n## Fuentes navegables\n",
        "- [[00 - Inicio|Mapa modular]]\n",
        "- [[10 - Resumen y relaciones|Resumen]]\n",
        "- [[20 - Arquitectura y stack|Arquitectura]]\n",
        "- [[30 - Operacion y entorno|Operacion]]\n",
        "- [[70 - Estado local|Estado local]]\n",
        f"- [[../../../Proyectos Git/{project['name']}|Contexto manual]]\n",
        f"- [[../../../Runbooks/{project['name']}|Runbook]]\n",
    ])
    return "".join(lines)


def render_traffic_light(statuses: list[dict], timestamp: str) -> str:
    counts = Counter(item["semaforo"] for item in statuses)
    lines = [
        "---\ntipo: reporte-semaforo\nestado: activo\ngenerado: true\ntags:\n  - memoria\n  - salud\n---\n\n",
        "# Semaforo de Proyectos\n\n",
        f"Actualizado: `{timestamp}`\n\n",
        f"> [!success] Verdes: **{counts['verde']}**\n",
        f"> [!warning] Amarillos: **{counts['amarillo']}**\n",
        f"> [!danger] Rojos: **{counts['rojo']}**\n\n",
        "## Reglas\n",
        "- **Rojo:** fuente ausente, Graphify administrado fallido, memoria faltante o fuente mas reciente que su salida administrada.\n",
        "- **Amarillo:** carpeta vacia, cambios locales, descripcion faltante o remoto no configurado.\n",
        "- **Verde:** no se detectaron condiciones anteriores. La inactividad antigua se muestra como informacion, no como fallo.\n\n",
        "## Estado por proyecto\n\n",
        "| Estado | Proyecto | Familia | Graphify | Motivo principal |\n|---|---|---|---|---|\n",
    ]
    icons = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}
    for item in sorted(statuses, key=lambda x: ({"rojo": 0, "amarillo": 1, "verde": 2}[x["semaforo"]], x["proyecto"].casefold())):
        reason = (item["motivos"] or item["informativo"] or ["Sin alertas"])[0]
        lines.append(f"| {icons[item['semaforo']]} {item['semaforo']} | [[../Proyectos/{safe(item['familia'])}/{safe(item['proyecto'])}/05 - Contexto para IA|{item['proyecto']}]] | {item['familia']} | `{item['graph_status']}` | {reason} |\n")
    return "".join(lines)


def render_staleness(statuses: list[dict], timestamp: str) -> str:
    stale = [item for item in statuses if item["obsoleto"]]
    inactive = [item for item in statuses if item["informativo"]]
    lines = [
        "---\ntipo: reporte-obsolescencia\nestado: activo\ngenerado: true\ntags:\n  - memoria\n  - obsolescencia\n---\n\n",
        "# Obsolescencia de Proyectos\n\n",
        f"Actualizado: `{timestamp}`\n\n",
        f"- Desactualizados por evidencia: **{len(stale)}**\n",
        f"- Sin actividad reciente, solo informativo: **{len(inactive)}**\n\n",
        "## Requieren actualizacion\n",
    ]
    if stale:
        for item in stale:
            lines.append(f"- [[../Proyectos/{safe(item['familia'])}/{safe(item['proyecto'])}/05 - Contexto para IA|{item['proyecto']}]]: {'; '.join(item['motivos'])}\n")
    else:
        lines.append("- Ningun proyecto tiene evidencia de memoria o snapshot atrasado.\n")
    lines.append("\n## Inactividad no bloqueante\n")
    if inactive:
        lines.extend(f"- **{item['proyecto']}**: {'; '.join(item['informativo'])}\n" for item in inactive)
    else:
        lines.append("- Sin proyectos por encima del umbral configurado.\n")
    return "".join(lines)


def worklog_date(entry: dict) -> dt.date | None:
    try:
        return dt.datetime.strptime(entry.get("timestamp", "")[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def summary_note(period: str, day: dt.date, worklog: list[dict], statuses: list[dict], transitions: list[dict]) -> tuple[Path, str]:
    if period == "diario":
        start = end = day
        label = day.isoformat()
        folder = REPORTS / "Resumen Diario"
        title = f"Resumen Diario {label}"
    else:
        start = day - dt.timedelta(days=day.weekday())
        end = start + dt.timedelta(days=6)
        year, week, _ = day.isocalendar()
        label = f"{year}-W{week:02d}"
        folder = REPORTS / "Resumen Semanal"
        title = f"Resumen Semanal {label}"
    entries = [item for item in worklog if (date := worklog_date(item)) and start <= date <= end]
    projects = sorted({item.get("project", "") for item in entries if item.get("project")})
    alerts = [item for item in statuses if item["semaforo"] in {"rojo", "amarillo"}]
    lines = [
        "---\n",
        f'tipo: "resumen-{period}"\n',
        'estado: "generado"\n',
        "generado: true\n",
        f"fecha: {day.isoformat()}\n",
        f'periodo: "{label}"\n',
        'tags:\n  - "memoria"\n  - "resumen"\n',
        "---\n\n",
        f"# {title}\n\n",
        f"- Periodo: `{start}` a `{end}`\n",
        f"- Registros confirmados: **{len(entries)}**\n",
        f"- Proyectos con trabajo registrado: **{len(projects)}**\n",
        f"- Alertas operativas actuales: **{len(alerts)}**\n\n",
        "## Proyectos afectados\n",
    ]
    lines.extend(f"- [[Memoria/Proyectos Git/{name}|{name}]]\n" for name in projects) if projects else lines.append("- Sin trabajo confirmado en el periodo.\n")
    lines.append("\n## Trabajo y decisiones\n")
    if entries:
        for entry in entries[-60:]:
            lines.append(f"- `{entry.get('timestamp')}` · **{entry.get('project')}** · {entry.get('type')} · {entry.get('title')}\n")
    else:
        lines.append("- Sin registros.\n")
    lines.append("\n## Cambios de semaforo\n")
    relevant_transitions = [item for item in transitions if item.get("anterior")]
    if relevant_transitions:
        lines.extend(f"- **{item['proyecto']}**: `{item['anterior']}` → `{item['actual']}`\n" for item in relevant_transitions)
    else:
        lines.append("- Sin cambios de estado detectados en esta ejecucion.\n")
    lines.append("\n## Alertas actuales\n")
    if alerts:
        for item in alerts[:50]:
            lines.append(f"- **{item['semaforo']} · {item['proyecto']}**: {(item['motivos'] or ['Revisar contexto'])[0]}\n")
    else:
        lines.append("- Sin alertas.\n")
    lines.extend(["\n## Pendientes\n", "- [ ] Revisar los proyectos rojos.\n", "- [ ] Capturar decisiones o validaciones que aun no esten en la bitacora.\n"])
    return folder / f"{label}.md", "".join(lines)


def dependency_records(edges: list[list]) -> list[dict]:
    overrides = read_json(VAULT_ROOT / ".memoria-system" / "config" / "dependency_overrides.json", {"confirmed": [], "ignored": []})
    ignored = {(item.get("source"), item.get("target")) for item in overrides.get("ignored", [])}
    records: dict[tuple[str, str, str], dict] = {}
    for source, target, reason in edges:
        if (source, target) in ignored:
            continue
        key = (source, target, reason)
        records[key] = {
            "source": source, "target": target, "kind": "inferred",
            "confidence": "high" if "endpoint" in reason else "low",
            "evidence": reason, "origin": "inventory",
        }
    for item in overrides.get("confirmed", []):
        source, target = item.get("source"), item.get("target")
        if not source or not target or source == target:
            continue
        reason = item.get("evidence") or "confirmada manualmente"
        records[(source, target, reason)] = {
            "source": source, "target": target, "kind": "confirmed",
            "confidence": "high", "evidence": reason, "origin": "config/dependency_overrides.json",
        }
    return sorted(records.values(), key=lambda item: (item["source"], item["target"], item["kind"]))


def corporate_dependencies(projects: list[dict], records: list[dict], timestamp: str) -> str:
    lookup = {p["name"]: p for p in projects}
    lines = [
        "---\ntipo: mapa-dependencias\nestado: activo\ngenerado: true\ntags:\n  - memoria\n  - arquitectura\n  - dependencias\n---\n\n",
        "# Mapa Corporativo de Dependencias\n\n",
        f"Actualizado: `{timestamp}`. Las relaciones se etiquetan como **inferidas** hasta confirmarse en codigo o mediante `memoria registrar`.\n\n",
        "## Mapa\n\n```mermaid\ngraph LR\n",
    ]
    for record in records:
        source, target, reason = record["source"], record["target"], record["evidence"]
        sid = "p_" + hashlib.sha1(source.encode()).hexdigest()[:10]
        tid = "p_" + hashlib.sha1(target.encode()).hexdigest()[:10]
        label = str(reason).replace('"', "'").replace("|", "/").replace("\n", " ")
        lines.append(f'  {sid}["{source}"] -->|"{label}"| {tid}["{target}"]\n')
    if not records:
        lines.append('  none["Sin relaciones detectadas"]\n')
    lines.extend(["```\n\n", "## Relaciones consultables\n\n", "| Origen | Destino | Tipo | Evidencia | Confianza |\n|---|---|---|---|---|\n"])
    for record in records:
        source, target, reason = record["source"], record["target"], record["evidence"]
        confidence = record["confidence"]
        sf = safe(lookup.get(source, {}).get("family", "Otros"))
        tf = safe(lookup.get(target, {}).get("family", "Otros"))
        lines.append(f"| [[../Proyectos/{sf}/{safe(source)}/05 - Contexto para IA|{source}]] | [[../Proyectos/{tf}/{safe(target)}/05 - Contexto para IA|{target}]] | {record['kind']} | {reason} | {confidence} |\n")
    lines.extend(["\n## Regla de uso\n", "- Confirmar siempre en codigo/configuracion antes de cambiar despliegues.\n", "- Registrar relaciones comprobadas con `memoria registrar <proyecto> --tipo arquitectura ...`.\n"])
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generar inteligencia operativa del baul")
    parser.parse_args()
    index = read_json(INDEX_PATH, {})
    registry = read_json(REGISTRY_PATH, {"projects": {}})
    worklog = read_json(WORKLOG_PATH, [])
    previous = read_json(STATUS_PATH, {"projects": {}})
    projects = index.get("projects", [])
    retained_projects = missing_projects(registry, {project["name"] for project in projects})
    operational_projects = projects + retained_projects
    edges = index.get("dependency_edges", [])
    dependency_data = dependency_records(edges)
    now = dt.datetime.now(dt.timezone.utc)
    local_now = dt.datetime.now().astimezone()
    today = local_now.date().isoformat()
    timestamp = local_now.isoformat(timespec="seconds")
    statuses = [assess(project, registry, previous, now) for project in operational_projects]
    status_by_name = {item["proyecto"]: item for item in statuses}
    transitions = [
        {"proyecto": item["proyecto"], "anterior": item["previous_semaforo"], "actual": item["semaforo"]}
        for item in statuses if item["previous_semaforo"] != item["semaforo"]
    ]

    for project in operational_projects:
        status = status_by_name[project["name"]]
        write(context_path(project), context_note(project, status, worklog, edges, today))
        update_home_properties(project_home(project), status, today)

    write(REPORTS / "Semaforo de Proyectos.md", render_traffic_light(statuses, timestamp))
    write(REPORTS / "Obsolescencia de Proyectos.md", render_staleness(statuses, timestamp))
    for period in ("diario", "semanal"):
        path, content = summary_note(period, local_now.date(), worklog, statuses, transitions)
        write(path, content)
        write(REPORTS / ("Resumen Diario.md" if period == "diario" else "Resumen Semanal.md"), content)
    write(ARCHITECTURE / "Mapa Corporativo de Dependencias.md", corporate_dependencies(projects, dependency_data, timestamp))
    DEPENDENCIES_PATH.write_text(json.dumps({"version": 1, "updated_at": timestamp, "dependencies": dependency_data}, ensure_ascii=False, indent=2), encoding="utf-8")

    capture_index = MEMORIA_ROOT / "Bandeja de Entrada" / "Capturas" / "Indice de Capturas.md"
    if not capture_index.exists():
        write(capture_index, "# Indice de Capturas\n\nSin capturas inteligentes pendientes.\n")

    payload = {
        "version": 1,
        "updated_at": timestamp,
        "rules": {
            "inactive_days": int(SETTINGS.get("vitaminado", {}).get("inactive_days", 180)),
            "red": "fuente ausente, fallo Graphify, memoria faltante o salida administrada obsoleta",
            "yellow": "carpeta vacia, cambios locales, descripcion faltante o remoto ausente",
        },
        "summary": dict(Counter(item["semaforo"] for item in statuses)),
        "transitions": transitions,
        "projects": status_by_name,
    }
    STATUS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Vitaminado 2: {len(operational_projects)} contextos; semaforo={payload['summary']}; transiciones={len(transitions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
