#!/usr/bin/env python3
"""Consulta acotada al grafo de memoria (Graphify) del alumno.

Busca el grafo en este orden:
  1. $MARKETING_GRAPH
  2. <vault>/.memoria-system/graph/graph.json (vault de settings.json u $OBSIDIAN_VAULT_ROOT)
  3. ./graphify-out/graph.json en la carpeta actual
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys


def candidate_graphs():
    env = os.environ.get("MARKETING_GRAPH")
    if env:
        yield pathlib.Path(env).expanduser()
    vault = os.environ.get("OBSIDIAN_VAULT_ROOT")
    if not vault:
        here = pathlib.Path(__file__).resolve()
        for parent in here.parents:
            settings = parent / "engine" / "memory" / "config" / "settings.json"
            if settings.exists():
                try:
                    vault = json.loads(settings.read_text(encoding="utf-8")).get("vault_root")
                except (OSError, json.JSONDecodeError):
                    vault = None
                break
    if vault:
        yield pathlib.Path(vault).expanduser() / ".memoria-system" / "graph" / "graph.json"
    yield pathlib.Path.cwd() / "graphify-out" / "graph.json"


def main() -> int:
    question = " ".join(sys.argv[1:]).strip() or "Marketing IA"
    graph = next((path for path in candidate_graphs() if path.exists()), None)
    if graph is None:
        print("No se encontro un graph.json. Ejecuta `graphify .` en tu proyecto o `memoria refresh`.")
        return 1
    graphify = shutil.which("graphify")
    if not graphify:
        print("No se encontro el CLI graphify. Instalalo con: pipx install graphifyy")
        return 1
    return subprocess.run([graphify, "query", question, "--graph", str(graph), "--budget", "2500"], check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
