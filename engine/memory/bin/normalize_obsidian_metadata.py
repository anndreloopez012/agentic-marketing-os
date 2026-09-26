#!/usr/bin/env python3
"""Add native Obsidian properties to legacy worklog notes without rewriting content."""
from __future__ import annotations

import json
import re
from pathlib import Path

from portable_paths import MEMORIA_ROOT

BITACORA = MEMORIA_ROOT / "Bitacora"


def field(text: str, name: str) -> str:
    match = re.search(rf"(?mi)^-?\s*{re.escape(name)}:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else ""


def clean_link(value: str) -> str:
    match = re.search(r"\[\[([^]|]+)", value)
    return match.group(1).strip() if match else value.strip("` ")


def normalize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if text.startswith("---\n") or path.name == "Registro de Trabajo.md":
        return False
    project = clean_link(field(text, "Proyecto"))
    kind = field(text, "Tipo") or "registro"
    status = field(text, "Estado") or "confirmado"
    raw_date = field(text, "Fecha")
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", raw_date or path.name)
    date = date_match.group(0) if date_match else ""
    if not any((project, raw_date, field(text, "Tipo"))):
        return False
    yaml = [
        "---\n",
        f"tipo: {json.dumps(kind, ensure_ascii=False)}\n",
        f"proyecto: {json.dumps(project, ensure_ascii=False)}\n",
        f"estado: {json.dumps(status, ensure_ascii=False)}\n",
    ]
    if date:
        yaml.append(f"fecha: {date}\n")
    yaml.extend([
        "tags:\n",
        "  - \"memoria\"\n",
        "  - \"bitacora\"\n",
        "---\n\n",
    ])
    path.write_text("".join(yaml) + text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    if BITACORA.exists():
        for path in BITACORA.rglob("*.md"):
            changed += int(normalize(path))
    print(f"Obsidian metadata normalized: {changed} legacy note(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
