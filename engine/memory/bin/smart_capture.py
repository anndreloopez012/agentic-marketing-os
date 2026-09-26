#!/usr/bin/env python3
"""Deterministic, safe inbox classification for reusable project context."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from portable_paths import DATA_ROOT, MEMORIA_ROOT

INDEX = DATA_ROOT / "memoria_index.json"
REGISTRY = DATA_ROOT / "capture_registry.json"
CAPTURES = MEMORIA_ROOT / "Bandeja de Entrada" / "Capturas"
TYPE_RULES = {
    "decision": ("decidimos", "decision", "acordamos", "se eligio"),
    "incidente": ("incidente", "caida", "produccion", "degradacion"),
    "bugfix": ("bug", "error", "fallo", "corregido", "fix"),
    "arquitectura": ("arquitectura", "servicio", "dependencia", "flujo", "endpoint"),
    "runbook": ("pasos", "procedimiento", "ejecutar", "comando", "despliegue"),
    "tarea": ("pendiente", "hacer", "falta", "todo", "proximo"),
    "referencia": ("referencia", "documentacion", "url", "enlace"),
}
SECRET_PATTERNS = (
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)\b(password|passwd|token|secret|api[_-]?key)\s*[:=]\s*\S+",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
    r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
    r"(?i)\b[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@",
)


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9áéíóúñü]+", "-", value.lower()).strip("-")
    return value[:72] or "captura"


def classify(text: str) -> str:
    low = text.casefold()
    scores = {kind: sum(term in low for term in terms) for kind, terms in TYPE_RULES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "aprendizaje"


def infer_project(text: str, projects: list[dict], explicit: str | None) -> tuple[str | None, str]:
    if explicit:
        matches = [p["name"] for p in projects if p["name"].casefold() == explicit.casefold()]
        if not matches:
            raise SystemExit(f"Proyecto no encontrado: {explicit}")
        return matches[0], "alta"
    low = text.casefold()
    matches = sorted((p["name"] for p in projects if p["name"].casefold() in low), key=len, reverse=True)
    return (matches[0], "media") if matches else (None, "baja")


def render_index(records: dict) -> str:
    lines = ["# Indice de Capturas\n\n", "Contenido clasificado automaticamente. Revisar las capturas de confianza baja antes de moverlas.\n\n", "| Fecha | Tipo | Proyecto | Confianza | Nota |\n|---|---|---|---|---|\n"]
    for item in sorted(records.values(), key=lambda x: x["created_at"], reverse=True):
        project = item.get("project") or "Por clasificar"
        lines.append(f"| `{item['created_at']}` | {item['type']} | {project} | {item['confidence']} | [[{Path(item['note']).stem}]] |\n")
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capturar y clasificar contexto en la bandeja")
    parser.add_argument("--texto", required=True)
    parser.add_argument("--titulo")
    parser.add_argument("--proyecto")
    parser.add_argument("--tipo", choices=["auto", "aprendizaje", *TYPE_RULES], default="auto")
    args = parser.parse_args()
    text = " ".join(args.texto.split())
    if any(re.search(pattern, text) for pattern in SECRET_PATTERNS):
        raise SystemExit("Captura rechazada: el texto parece contener un secreto. Guardalo en un gestor seguro, no en Obsidian.")
    digest = hashlib.sha256(text.casefold().encode()).hexdigest()
    records = load(REGISTRY, {})
    if digest in records:
        print(f"Captura duplicada: {records[digest]['note']}")
        return 0
    index = load(INDEX, {})
    project, confidence = infer_project(text, index.get("projects", []), args.proyecto)
    kind = classify(text) if args.tipo == "auto" else args.tipo
    now = dt.datetime.now().astimezone()
    title = args.titulo or " ".join(text.split()[:10])
    note = CAPTURES / f"{now.date().isoformat()} - {kind} - {slug(title)}.md"
    counter = 2
    while note.exists():
        note = CAPTURES / f"{now.date().isoformat()} - {kind} - {slug(title)}-{counter}.md"
        counter += 1
    destination = {
        "decision": "Memoria/Decisiones",
        "incidente": "Memoria/Incidentes",
        "runbook": "Memoria/Runbooks",
        "arquitectura": "Memoria/Arquitectura",
        "tarea": "Memoria/Bitacora",
    }.get(kind, "Memoria/Bitacora")
    CAPTURES.mkdir(parents=True, exist_ok=True)
    body = [
        "---\n", f'tipo: "captura-{kind}"\n', f'proyecto: {json.dumps(project or "por-clasificar", ensure_ascii=False)}\n',
        'estado: "por-revisar"\n', f'clasificacion: "{kind}"\n', f'confianza: "{confidence}"\n',
        f"fecha: {now.date().isoformat()}\n", "generado: true\n", 'tags:\n  - "memoria"\n  - "captura"\n', "---\n\n",
        f"# {title}\n\n", f"- Clasificacion inferida: **{kind}**\n", f"- Confianza: **{confidence}**\n",
        f"- Proyecto: {'[[../../Proyectos Git/' + project + '|' + project + ']]' if project else 'Por clasificar'}\n",
        f"- Destino recomendado: `{destination}`\n\n", "## Contenido\n", text, "\n\n",
        "## Revision\n- [ ] Confirmar proyecto y clasificacion.\n- [ ] Convertir en registro estable con `memoria registrar` cuando corresponda.\n",
    ]
    note.write_text("".join(body), encoding="utf-8")
    records[digest] = {"created_at": now.isoformat(timespec="seconds"), "type": kind, "project": project, "confidence": confidence, "note": str(note.relative_to(MEMORIA_ROOT))}
    REGISTRY.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    write_index = CAPTURES / "Indice de Capturas.md"
    write_index.write_text(render_index(records), encoding="utf-8")
    print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
