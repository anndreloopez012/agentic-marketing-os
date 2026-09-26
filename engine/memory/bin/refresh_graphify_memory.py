#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from portable_paths import BIN_ROOT

ONBOARD = BIN_ROOT / "onboard_projects.py"
REFRESH = BIN_ROOT / "refresh_project_memory.py"
NORMALIZE = BIN_ROOT / "normalize_obsidian_metadata.py"
SEGMENT = BIN_ROOT / "segment_large_notes.py"
AUDIT = BIN_ROOT / "audit_obsidian_workspace.py"
VITAMINIZE = BIN_ROOT / "vitaminize_memory.py"
PORTABILITY = BIN_ROOT / "test_vault_portability.py"
DEEP = BIN_ROOT / "deep_documentation.py"
RELATIONS = BIN_ROOT / "relation_review.py"
INTEGRATIONS = BIN_ROOT / "integration_hub.py"
TEMPORAL = BIN_ROOT / "temporal_graph.py"
BUILD = BIN_ROOT / "build_graphify_memory.py"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> int:
    # A project-specific Graphify failure is recorded but must not prevent the
    # rest of the memory and the master graph from refreshing.
    subprocess.run([sys.executable, str(ONBOARD)], check=False)
    run([sys.executable, str(REFRESH)])
    run([sys.executable, str(NORMALIZE)])
    run([sys.executable, str(SEGMENT)])
    run([sys.executable, str(VITAMINIZE)])
    run([sys.executable, str(DEEP)])
    run([sys.executable, str(RELATIONS), "build"])
    run([sys.executable, str(INTEGRATIONS)])
    subprocess.run([sys.executable, str(PORTABILITY)], check=False)
    subprocess.run([sys.executable, str(AUDIT)], check=False)
    run([sys.executable, str(BUILD)])
    run([sys.executable, str(TEMPORAL)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
