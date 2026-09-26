#!/usr/bin/env python3
"""Portable paths for the Obsidian memory system.

The vault is discovered from this file, so moving the complete vault does not
require editing scripts. Machine-specific project locations live in config.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


BIN_ROOT = Path(__file__).resolve().parent
SYSTEM_ROOT = BIN_ROOT.parent

def _expand(value: str) -> Path:
    return Path(os.path.expandvars(value)).expanduser().resolve()

def load_settings() -> dict:
    path = CONFIG_ROOT / "settings.json"
    if not path.exists():
        path = CONFIG_ROOT / "settings.example.json"
        if not path.exists():
            return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

CONFIG_ROOT = SYSTEM_ROOT / "config"
SETTINGS = load_settings()

def _resolve_vault() -> Path:
    if "OBSIDIAN_VAULT_ROOT" in os.environ:
        return _expand(os.environ["OBSIDIAN_VAULT_ROOT"])
    if "vault_root" in SETTINGS and SETTINGS["vault_root"]:
        return _expand(SETTINGS["vault_root"])
    if (SYSTEM_ROOT.parent / "Memoria").exists():
        return SYSTEM_ROOT.parent
    return _expand("~/Documents/Obsidian Vault")

VAULT_ROOT = _resolve_vault()
MEMORIA_ROOT = VAULT_ROOT / "Memoria"
DATA_ROOT = SYSTEM_ROOT / "data"
GRAPH_ROOT = SYSTEM_ROOT / "graph"
LOG_ROOT = SYSTEM_ROOT / "logs"
INSTALL_ROOT = SYSTEM_ROOT / "install"
PROJECT_GRAPHS_ROOT = SYSTEM_ROOT / "project-graphs"
PROJECTS_ROOTS = [
    _expand(item)
    for item in SETTINGS.get("projects_roots", ["~/Documents/PROYECTOS"])
]
PROJECTS_ROOT = next((path for path in PROJECTS_ROOTS if path.exists()), PROJECTS_ROOTS[0])
CODEX_ROOT = _expand(SETTINGS.get("codex_root", "~/.codex"))
CLAUDE_ROOT = _expand(SETTINGS.get("claude_root", "~/.claude"))
ANTIGRAVITY_ROOT = _expand(SETTINGS.get("antigravity_root", "~/.gemini/antigravity"))
ANTIGRAVITY_SKILLS = _expand(SETTINGS.get("antigravity_skills", "~/.gemini/config/skills"))
GRAPHIFY_BIN = _expand(SETTINGS.get("graphify_bin", "~/.local/bin/graphify"))


def portable_project_path(path: Path) -> str:
    """Store project paths without baking the current username into snapshots."""
    for index, root in enumerate(PROJECTS_ROOTS):
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            continue
        token = "$PROJECTS_ROOT" if index == 0 else f"$PROJECTS_ROOT_{root.name.upper()}"
        return f"{token}/{relative}"
    return str(path)
