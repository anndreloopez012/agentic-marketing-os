#!/usr/bin/env python3
"""Incrementally register and graph new local projects into the portable vault."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from portable_paths import (
    DATA_ROOT,
    GRAPHIFY_BIN,
    MEMORIA_ROOT,
    PROJECT_GRAPHS_ROOT,
    PROJECTS_ROOTS,
    portable_project_path,
)

REGISTRY_PATH = DATA_ROOT / "project_registry.json"
REPORT_PATH = MEMORIA_ROOT / "Reportes" / "Incorporacion automatica de proyectos.md"
SKIP_DIRS = {
    ".git", ".obsidian", "graphify-out", "node_modules", "vendor", "dist",
    "build", ".next", ".nuxt", ".cache", "coverage", "tmp", "logs",
    ".turbo", "__pycache__",
}
CONTEXT_NAMES = {
    "README", "README.md", "README.MD", "package.json", "composer.json",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "pyproject.toml",
    "requirements.txt", "Cargo.toml", "go.mod",
}
CONTEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".py", ".php", ".sql", ".yml", ".yaml", ".html", ".css", ".xml",
    ".sh", ".toml", ".go", ".rs", ".java", ".swift", ".kt", ".cs",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: object) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def graphify_python() -> str:
    if GRAPHIFY_BIN.exists():
        try:
            line = GRAPHIFY_BIN.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
            parts = shlex.split(line.removeprefix("#!").strip())
            if parts and Path(parts[0]).exists():
                return parts[0]
        except (OSError, IndexError, ValueError):
            pass
    return "python3"


def relevant_files(project: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(project, followlinks=False):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".")]
        for filename in filenames:
            path = Path(current) / filename
            lowered = filename.lower()
            if lowered.startswith(".env") and not lowered.endswith((".example", ".sample")):
                continue
            if any(token in lowered for token in ("secret", "credential", "private-key")):
                continue
            if filename in CONTEXT_NAMES or path.suffix.lower() in CONTEXT_SUFFIXES or lowered.endswith((".env.example", ".env.sample")):
                files.append(path)
    return sorted(files)


def fingerprint(project: Path) -> dict:
    digest = hashlib.sha256()
    files = relevant_files(project)
    latest_ns = project.stat().st_mtime_ns
    for path in files:
        try:
            stat = path.stat()
        except OSError:
            continue
        relative = path.relative_to(project).as_posix()
        latest_ns = max(latest_ns, stat.st_mtime_ns)
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        digest.update(f"\0{stat.st_size}\0{stat.st_mtime_ns}\n".encode())
    direct_entries = sorted(item.name for item in project.iterdir() if item.name != "graphify-out")
    for entry in direct_entries:
        digest.update(f"entry\0{entry}\n".encode("utf-8", errors="surrogateescape"))
    return {
        "digest": digest.hexdigest(),
        "file_count": len(files),
        "latest_mtime_ns": latest_ns,
        "empty": not direct_entries,
    }


def discover(roots: list[Path]) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for root in roots:
        if not root.exists():
            continue
        for project in sorted(root.iterdir()):
            if not project.is_dir() or project.is_symlink() or project.name.startswith("."):
                continue
            # The principal PROYECTOS root inventories every direct folder. Extra
            # roots remain restricted to recognizable projects to avoid noise.
            if root != roots[0] and not any((project / marker).exists() for marker in (".git", "package.json", "graphify-out", "pyproject.toml", "Cargo.toml", "go.mod")):
                continue
            key = f"{root.name}/{project.name}"
            found[key] = {
                "key": key,
                "root": root.name,
                "name": project.name,
                "path": portable_project_path(project),
                "absolute_path": str(project.resolve()),
                "fingerprint": fingerprint(project),
            }
    return found


def graph_output(graphs_root: Path, project: dict) -> Path:
    return graphs_root / project["root"] / project["name"]


def graph_complete(output: Path) -> bool:
    return all((output / name).is_file() for name in ("graph.json", "GRAPH_REPORT.md", "graph.html"))


def ensure_compatibility_link(project: Path, output: Path) -> str:
    link = project / "graphify-out"
    if link.is_symlink() and link.resolve() == output.resolve():
        return "linked"
    if link.exists() or link.is_symlink():
        return "conflict_existing_graphify_out"
    link.symlink_to(output, target_is_directory=True)
    return "linked"


def build_snapshot(project: dict, graphs_root: Path) -> tuple[str, str, str]:
    source = Path(project["absolute_path"])
    output = graph_output(graphs_root, project)
    files = relevant_files(source)
    if not files:
        return "inventory_only", "La carpeta aun no contiene archivos analizables.", "not_applicable"
    output.mkdir(parents=True, exist_ok=True)
    local_output = source / "graphify-out"
    local_output_existed = local_output.exists() or local_output.is_symlink()
    env = os.environ.copy()
    env["GRAPHIFY_OUT"] = str(output)
    env["GRAPHIFY_NO_TIPS"] = "1"
    proc = subprocess.run(
        [str(GRAPHIFY_BIN), "update", str(source)],
        cwd=str(source), env=env, capture_output=True, text=True, timeout=1800,
    )
    detail = "\n".join(part.strip() for part in (proc.stdout, proc.stderr) if part.strip())[-4000:]
    # graphify's manifest helper currently writes this one metadata file to the
    # default local graphify-out even when GRAPHIFY_OUT is overridden. Re-home
    # only the directory created by this run; never touch a pre-existing one.
    if not local_output_existed and local_output.is_dir():
        local_manifest = local_output / "manifest.json"
        if local_manifest.is_file():
            local_manifest.replace(output / "manifest.json")
        try:
            local_output.rmdir()
        except OSError:
            pass
    if proc.returncode != 0 or not graph_complete(output):
        return "failed", detail or f"Graphify termino con codigo {proc.returncode}.", "not_linked"
    (output / ".graphify_root").write_text(str(source), encoding="utf-8")
    (output / ".graphify_python").write_text(graphify_python(), encoding="utf-8")
    link_status = ensure_compatibility_link(source, output)
    return "complete", detail or "Snapshot Graphify actualizado.", link_status


def render_report(entries: dict[str, dict], events: list[dict]) -> str:
    active = [item for item in entries.values() if item.get("presence") == "active"]
    missing = [item for item in entries.values() if item.get("presence") == "missing"]
    counts: dict[str, int] = {}
    for item in active:
        status = item.get("graph_status", "memory_only")
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "# Incorporacion automatica de proyectos\n\n",
        "Esta rutina detecta carpetas nuevas, crea memoria segmentada y mantiene snapshots Graphify individuales sin copiar repositorios ni secretos al baul.\n\n",
        f"- Ultima ejecucion: `{now()}`\n",
        f"- Proyectos activos: **{len(active)}**\n",
        f"- Proyectos ausentes conservados en registro: **{len(missing)}**\n",
        f"- Snapshots completos: **{counts.get('complete', 0)}**\n",
        f"- Solo inventario: **{counts.get('inventory_only', 0)}**\n",
        f"- Memoria sin snapshot administrado: **{counts.get('memory_only', 0)}**\n",
        f"- Errores pendientes: **{counts.get('failed', 0)}**\n\n",
        "## Proyectos activos\n\n",
        "| Proyecto | Raiz | Estado | Archivos | Ultima incorporacion |\n",
        "|---|---|---|---:|---|\n",
    ]
    for item in sorted(active, key=lambda row: (row["root"], row["name"].casefold())):
        lines.append(
            f"| `{item['name']}` | `{item['root']}` | {item.get('graph_status', 'memory_only')} | "
            f"{item.get('fingerprint', {}).get('file_count', 0)} | `{item.get('last_onboarded_at') or '-'}` |\n"
        )
    lines.extend(["\n## Eventos de esta ejecucion\n"])
    if events:
        for event in events:
            lines.append(f"- `{event['action']}` · `{event['key']}` · {event.get('status', '')}\n")
    else:
        lines.append("- Sin cambios; ejecucion idempotente.\n")
    lines.extend([
        "\n## Politica de seguridad\n",
        "- Nunca se copian repositorios, dependencias, bases de datos, `.env`, llaves ni credenciales.\n",
        "- Los snapshots tecnicos usan extraccion estructural local de Graphify, sin API ni costo de tokens.\n",
        "- Los proyectos eliminados o renombrados se marcan como ausentes; no se destruye memoria manual automaticamente.\n",
        "- Los errores de un proyecto se registran sin impedir que los demas sean incorporados.\n",
    ])
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detectar e incorporar proyectos al baul")
    parser.add_argument("--root", action="append", help="Raiz alternativa para pruebas; puede repetirse")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--graphs-root", type=Path, default=PROJECT_GRAPHS_ROOT)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--onboard-all", action="store_true", help="Crear snapshot para todos, incluso al inicializar")
    parser.add_argument("--project", action="append", default=[], help="Forzar una clave raiz/proyecto especifica")
    args = parser.parse_args()

    roots = [Path(value).expanduser().resolve() for value in args.root] if args.root else list(PROJECTS_ROOTS)
    previous_data = read_json(args.registry, {"projects": {}})
    previous = previous_data.get("projects", {}) if isinstance(previous_data, dict) else {}
    current = discover(roots)
    first_run = not args.registry.exists()
    entries: dict[str, dict] = {key: dict(value) for key, value in previous.items()}
    events: list[dict] = []

    for key, project in current.items():
        old = previous.get(key)
        changed = old is not None and old.get("fingerprint", {}).get("digest") != project["fingerprint"]["digest"]
        is_new = old is None
        entry = {**(old or {}), **project, "presence": "active", "last_seen_at": now()}
        output = graph_output(args.graphs_root, project)
        already_complete = graph_complete(output)

        if first_run and not args.onboard_all:
            entry["graph_status"] = "complete" if already_complete else ("inventory_only" if project["fingerprint"]["file_count"] == 0 else "memory_only")
            entry.setdefault("last_onboarded_at", None)
        elif is_new or args.onboard_all or key in args.project or (changed and (old or {}).get("managed_snapshot")):
            try:
                status, detail, link_status = build_snapshot(project, args.graphs_root)
            except Exception as exc:
                status, detail, link_status = "failed", f"{type(exc).__name__}: {exc}", "not_linked"
            entry.update({
                "graph_status": status,
                "graph_detail": detail,
                "compatibility_link": link_status,
                # Empty projects stay managed so adding their first real file
                # automatically promotes them from inventory_only to complete.
                "managed_snapshot": True,
                "last_onboarded_at": now(),
            })
            events.append({"action": "added" if is_new else "updated", "key": key, "status": status})
        else:
            entry["graph_status"] = "complete" if already_complete else entry.get("graph_status", "memory_only")
        # Absolute paths are runtime-only. The persistent registry must travel
        # cleanly with the vault and uses the portable $PROJECTS_ROOT token.
        entry.pop("absolute_path", None)
        if isinstance(entry.get("graph_detail"), str):
            entry["graph_detail"] = entry["graph_detail"].replace(str(Path.home()), "~")
        entries[key] = entry

    for key, old in previous.items():
        if key in current:
            continue
        entry = dict(old)
        if entry.get("presence") != "missing":
            events.append({"action": "missing", "key": key, "status": "preserved"})
            entry["missing_since"] = now()
        entry["presence"] = "missing"
        entries[key] = entry

    payload = {"version": 1, "updated_at": now(), "projects": entries, "events": events[-200:]}
    write_json(args.registry, payload)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(entries, events), encoding="utf-8")
    print(f"Project onboarding: {len(current)} active; {len(events)} event(s); registry={args.registry}")
    return 0 if not any(event.get("status") == "failed" for event in events) else 2


if __name__ == "__main__":
    raise SystemExit(main())
