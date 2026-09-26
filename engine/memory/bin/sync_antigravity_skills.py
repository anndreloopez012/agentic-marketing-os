#!/usr/bin/env python3
"""Sincroniza y enlaza todas las skills de Claude y Codex hacia Google Antigravity (~/.gemini/config/skills)."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from portable_paths import ANTIGRAVITY_SKILLS, CLAUDE_ROOT, CODEX_ROOT


def discover_available_skills() -> dict[str, Path]:
    """Descubre todas las carpetas de skills disponibles en Claude y Codex."""
    sources = [
        ("Claude", CLAUDE_ROOT / "skills"),
        ("Codex", CODEX_ROOT / "skills"),
        ("Codex System", CODEX_ROOT / "skills" / ".system"),
    ]

    discovered: dict[str, Path] = {}

    for ai_name, root in sources:
        if not root.exists():
            continue
        for item in root.iterdir():
            if item.name.startswith("."):
                continue
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                skill_name = item.name
                if skill_name not in discovered:
                    resolved = item.resolve() if item.is_symlink() else item
                    discovered[skill_name] = resolved

    return discovered


def sync_skills(dry_run: bool = False, verbose: bool = False) -> tuple[int, int, int]:
    """Enlaza todas las skills descubiertas hacia el directorio de Antigravity."""
    target_dir = ANTIGRAVITY_SKILLS
    target_dir.mkdir(parents=True, exist_ok=True)

    available = discover_available_skills()
    existing_count = 0
    newly_linked_count = 0
    skipped_count = 0

    for name, source_path in sorted(available.items()):
        dest = target_dir / name

        if dest.exists() or dest.is_symlink():
            if dest.is_symlink():
                try:
                    target_resolved = dest.resolve(strict=True)
                    if not (dest / "SKILL.md").exists():
                        if not dry_run:
                            dest.unlink()
                            os.symlink(str(source_path), str(dest))
                            newly_linked_count += 1
                            if verbose:
                                print(f"[REPARADO] {name} -> {source_path}")
                        continue
                    else:
                        existing_count += 1
                        if verbose:
                            print(f"[EXISTE] {name} -> {target_resolved}")
                        continue
                except (OSError, FileNotFoundError):
                    if not dry_run:
                        dest.unlink(missing_ok=True)
                        os.symlink(str(source_path), str(dest))
                        newly_linked_count += 1
                        if verbose:
                            print(f"[REPARADO] {name} -> {source_path}")
                    continue
            else:
                existing_count += 1
                if verbose:
                    print(f"[LOCAL] {name} (directorio local)")
                continue

        if dry_run:
            newly_linked_count += 1
            if verbose:
                print(f"[DRY-RUN ENLACE] {name} -> {source_path}")
        else:
            try:
                os.symlink(str(source_path), str(dest))
                newly_linked_count += 1
                if verbose:
                    print(f"[ENLAZADO] {name} -> {source_path}")
            except Exception as exc:
                print(f"[ERROR] No se pudo enlazar {name}: {exc}", file=sys.stderr)
                skipped_count += 1

    return newly_linked_count, existing_count, skipped_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincronizar skills hacia Google Antigravity")
    parser.add_argument("--dry-run", action="store_true", help="Simular cambios sin enlazar archivos")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar detalle de cada skill")
    args = parser.parse_args()

    newly_linked, existing, skipped = sync_skills(dry_run=args.dry_run, verbose=args.verbose)

    total_active = len([p for p in ANTIGRAVITY_SKILLS.iterdir() if (p / "SKILL.md").exists()]) if ANTIGRAVITY_SKILLS.exists() else 0

    print("=== Sincronización de Skills para Antigravity ===")
    print(f"Directorio destino : {ANTIGRAVITY_SKILLS}")
    print(f"Nuevas enlazadas   : {newly_linked}")
    print(f"Previamente activas: {existing}")
    if skipped:
        print(f"Con errores/omitidas: {skipped}")
    print(f"Total skills activas en Antigravity: {total_active}")


if __name__ == "__main__":
    main()
