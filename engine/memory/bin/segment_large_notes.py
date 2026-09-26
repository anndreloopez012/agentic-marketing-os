#!/usr/bin/env python3
"""Turn oversized Markdown notes into portable MOCs plus bounded parts."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

from portable_paths import DATA_ROOT, MEMORIA_ROOT, SYSTEM_ROOT


MAX_BYTES = 100_000
MAX_LINES = 1_000
TARGET_LINES = 300
MARKER = "<!-- segmentado-automaticamente -->"
ORIGINALS_ROOT = SYSTEM_ROOT / "imports" / "large-notes-originals"
MANIFEST_PATH = DATA_ROOT / "large_notes_segments.json"


def should_skip(path: Path) -> bool:
    return (
        "Graphify" in path.parts
        or "Skills" in path.parts
        or "Proyectos" in path.parts
        or any(part.endswith(" - Segmentos") for part in path.parts)
    )


def bounded_chunks(lines: list[str]) -> list[list[str]]:
    chunks: list[list[str]] = []
    start = 0
    while start < len(lines):
        end = min(start + TARGET_LINES, len(lines))
        fence_open = sum(1 for line in lines[start:end] if line.lstrip().startswith("```")) % 2 == 1
        while fence_open and end < len(lines):
            if lines[end].lstrip().startswith("```"):
                fence_open = False
            end += 1
        chunks.append(lines[start:end])
        start = end
    return chunks


def table_header(lines: list[str]) -> list[str]:
    for index in range(len(lines) - 1):
        if lines[index].lstrip().startswith("|") and re.match(r"^\s*\|?[\s|:-]+\|\s*$", lines[index + 1]):
            return [lines[index], lines[index + 1]]
    return []


def segment(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines(keepends=True)
    relative = path.relative_to(MEMORIA_ROOT)
    original = ORIGINALS_ROOT / relative
    original.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, original)

    output_dir = path.parent / f"{path.stem} - Segmentos"
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("Parte *.md"):
        stale.unlink(missing_ok=True)

    header = table_header(lines)
    chunks = bounded_chunks(lines)
    links: list[str] = []
    for number, chunk in enumerate(chunks, 1):
        name = f"Parte {number:03d}"
        links.append(f"- [[{output_dir.name}/{name}|{name}]] · {len(chunk)} lineas\n")
        body = list(chunk)
        if number > 1 and header and body and body[0].lstrip().startswith("|"):
            body = header + body
        title = f"# {path.stem} — {name}\n\n"
        back = f"[[../{path.stem}|Volver al indice]]\n\n"
        (output_dir / f"{name}.md").write_text(title + back + "".join(body), encoding="utf-8")

    moc = [
        f"# {path.stem}\n\n",
        f"{MARKER}\n",
        "Esta nota se dividio automaticamente para que Obsidian, Graphify y las IA puedan procesarla por partes.\n\n",
        f"- Tamano original: {len(text.encode('utf-8')):,} bytes\n",
        f"- Lineas originales: {len(lines):,}\n",
        f"- Partes: {len(chunks)}\n",
        "- Original exacto preservado dentro de `.memoria-system/imports/large-notes-originals/`.\n\n",
        "## Partes\n",
        *links,
    ]
    path.write_text("".join(moc), encoding="utf-8")
    return {
        "note": relative.as_posix(),
        "original": original.relative_to(SYSTEM_ROOT).as_posix(),
        "bytes": len(text.encode("utf-8")),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "lines": len(lines),
        "parts": len(chunks),
    }


def main() -> int:
    previous: dict[str, dict] = {}
    if MANIFEST_PATH.exists():
        try:
            previous = {item["note"]: item for item in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))}
        except (OSError, json.JSONDecodeError, KeyError):
            previous = {}
    results = dict(previous)
    for path in MEMORIA_ROOT.rglob("*.md"):
        if should_skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if MARKER in text:
            continue
        if path.stat().st_size > MAX_BYTES or text.count("\n") + 1 > MAX_LINES:
            item = segment(path)
            results[item["note"]] = item
    MANIFEST_PATH.write_text(json.dumps(sorted(results.values(), key=lambda item: item["note"]), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Large notes segmented: {len(results)} tracked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
