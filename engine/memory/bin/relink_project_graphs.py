#!/usr/bin/env python3
"""Restore compatibility links from project folders to vault-owned graphs."""
from __future__ import annotations

import os
import shlex
from pathlib import Path

from portable_paths import GRAPHIFY_BIN, PROJECT_GRAPHS_ROOT, SETTINGS


def expand(value: str) -> Path:
    return Path(os.path.expandvars(value)).expanduser().resolve()


def main() -> int:
    roots = SETTINGS.get(
        "graph_compatibility_roots",
        {"MarketingProjects": "~/Documents/MarketingProjects"},
    )
    linked = 0
    skipped = 0
    for marker in PROJECT_GRAPHS_ROOT.rglob(".graphify_root"):
        target = marker.parent
        relative = target.relative_to(PROJECT_GRAPHS_ROOT)
        if len(relative.parts) < 2:
            continue
        root_name, *project_parts = relative.parts
        configured_root = roots.get(root_name)
        if not configured_root:
            skipped += 1
            continue
        project_dir = expand(configured_root).joinpath(*project_parts)
        if not project_dir.exists():
            skipped += 1
            continue
        marker.write_text(str(project_dir), encoding="utf-8")
        python_marker = target / ".graphify_python"
        if GRAPHIFY_BIN.exists():
            first_line = GRAPHIFY_BIN.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
            shebang = shlex.split(first_line.removeprefix("#!").strip())
            if shebang:
                python_marker.write_text(shebang[0], encoding="utf-8")
        link = project_dir / "graphify-out"
        if link.is_symlink() and link.resolve() == target.resolve():
            continue
        if link.exists() or link.is_symlink():
            skipped += 1
            continue
        link.symlink_to(target, target_is_directory=True)
        linked += 1
    print(f"Graphify links restored: {linked}; skipped safely: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
