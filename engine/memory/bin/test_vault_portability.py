#!/usr/bin/env python3
"""Validate that the memory system survives moving the complete vault."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from portable_paths import BIN_ROOT, DATA_ROOT, GRAPH_ROOT, MEMORIA_ROOT, VAULT_ROOT

REPORT = MEMORIA_ROOT / "Reportes" / "Prueba de Portabilidad.md"
MANIFEST = DATA_ROOT / "portability_manifest.json"
CRITICAL = (
    ".obsidian/app.json", ".obsidian/core-plugins.json", ".obsidian/workspace.json",
    ".memoria-system/config/settings.json", ".memoria-system/graph/graph.json",
    ".memoria-system/bin/portable_paths.py", ".memoria-system/bin/refresh_graphify_memory.py",
    "Memoria/Centro de Operaciones.md", "Memoria/Bases/Proyectos.base",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Probar portabilidad del baul")
    parser.add_argument("--full-copy", action="store_true", help="Copiar los 400+ MB del baul a una ruta temporal")
    args = parser.parse_args()
    try:
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        previous = {}
    checks: list[tuple[str, bool, str]] = []
    files = {}
    for relative in CRITICAL:
        path = VAULT_ROOT / relative
        ok = path.is_file()
        checks.append((f"Existe {relative}", ok, "archivo critico"))
        if ok:
            files[relative] = digest(path)
    for path in BIN_ROOT.glob("*.py"):
        try:
            py_compile.compile(str(path), doraise=True)
            checks.append((f"Compila {path.name}", True, "Python"))
        except py_compile.PyCompileError as exc:
            checks.append((f"Compila {path.name}", False, str(exc)))
    plugin_lock = read_plugin_lock = None
    try:
        read_plugin_lock = json.loads((VAULT_ROOT / ".memoria-system/config/obsidian_plugins.lock.json").read_text(encoding="utf-8"))
    except Exception:
        read_plugin_lock = {"plugins": {}}
    for plugin, meta in read_plugin_lock.get("plugins", {}).items():
        main = VAULT_ROOT / ".obsidian" / "plugins" / plugin / "main.js"
        actual = digest(main) if main.is_file() else "missing"
        checks.append((f"Plugin portable {plugin}", actual == meta.get("sha256_main"), f"version fijada {meta.get('release')}"))
    try:
        graph = json.loads((GRAPH_ROOT / "graph.json").read_text(encoding="utf-8"))
        checks.append(("Grafo JSON legible", bool(graph.get("nodes")), f"{len(graph.get('nodes', []))} nodos"))
    except Exception as exc:
        checks.append(("Grafo JSON legible", False, str(exc)))
    external_links = []
    for path in VAULT_ROOT.rglob("*"):
        if path.is_symlink():
            try:
                path.resolve().relative_to(VAULT_ROOT)
            except (ValueError, OSError):
                external_links.append(str(path.relative_to(VAULT_ROOT)))
    checks.append(("Sin symlinks externos", not external_links, ", ".join(external_links[:10]) or "todos internos"))
    critical_absolute = []
    for relative in CRITICAL:
        path = VAULT_ROOT / relative
        if path.is_file() and "/Users/" in path.read_text(encoding="utf-8", errors="ignore"):
            critical_absolute.append(relative)
    checks.append(("Sin rutas /Users en archivos criticos", not critical_absolute, ", ".join(critical_absolute) or "portable"))

    copy_result = "No solicitada; usar `memoria portabilidad --full-copy`."
    if args.full_copy:
        with tempfile.TemporaryDirectory(prefix="obsidian-vault-portability-") as temp:
            target = Path(temp) / "Vault Copiado"
            shutil.copytree(VAULT_ROOT, target, symlinks=True, ignore=shutil.ignore_patterns("logs", "backups", "__pycache__", ".DS_Store"))
            code = (
                "import sys; "
                f"sys.path.insert(0, {str(target / '.memoria-system/bin')!r}); "
                "import portable_paths; print(portable_paths.VAULT_ROOT)"
            )
            proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
            resolved = proc.stdout.strip()
            ok = proc.returncode == 0 and Path(resolved).resolve() == target.resolve()
            checks.append(("Descubrimiento desde copia aislada", ok, resolved or proc.stderr.strip()))
            copied_hashes = {relative: digest(target / relative) for relative in files if (target / relative).is_file()}
            hashes_ok = copied_hashes == files
            checks.append(("Hashes criticos preservados", hashes_ok, f"{len(copied_hashes)}/{len(files)}"))
            copy_result = f"Copia completa temporal validada y eliminada: {len(copied_hashes)} hashes criticos."

    passed = all(ok for _, ok, _ in checks)
    last_full_copy_at = dt.datetime.now().astimezone().isoformat(timespec="seconds") if args.full_copy and passed else previous.get("last_full_copy_at")
    payload = {"version": 1, "status": "portable" if passed else "requiere-atencion", "full_copy": args.full_copy, "last_full_copy_at": last_full_copy_at, "critical_hashes": files, "checks": [{"name": name, "ok": ok, "detail": detail} for name, ok, detail in checks]}
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "---\ntipo: reporte-portabilidad\nestado: " + payload["status"] + "\ngenerado: true\ntags:\n  - memoria\n  - portabilidad\n---\n\n",
        "# Prueba de Portabilidad\n\n", f"- Resultado: **{payload['status']}**\n", f"- Ultima simulacion completa exitosa: `{last_full_copy_at or 'pendiente'}`\n", f"- {copy_result}\n\n", "## Comprobaciones\n\n",
        "| Resultado | Comprobacion | Detalle |\n|---|---|---|\n",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {'OK' if ok else 'FALLO'} | {name} | {detail} |\n")
    lines.extend(["\n## Migracion\n", "1. Copiar la carpeta completa del Vault.\n", "2. Abrirla en Obsidian.\n", "3. Ejecutar `.memoria-system/install/bootstrap-macos.sh`.\n", "4. Ajustar `.memoria-system/config/settings.json` si los repos viven en otra ubicacion.\n"])
    REPORT.write_text("".join(lines), encoding="utf-8")
    print(f"Portabilidad: {payload['status']}; full_copy={args.full_copy}; report={REPORT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
