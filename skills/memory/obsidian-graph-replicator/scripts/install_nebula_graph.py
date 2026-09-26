#!/usr/bin/env python3
"""Install the self-contained Graphify Nebula template into any web project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy the portable Graphify Nebula graph template.")
    parser.add_argument("target", help="Target directory where the template folder should be created.")
    parser.add_argument("--name", default="graphify-nebula", help="Output folder name inside target.")
    parser.add_argument("--force", action="store_true", help="Replace the output folder if it already exists.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    source = skill_dir / "assets" / "nebula-graph-template"
    target_root = Path(args.target).expanduser().resolve()
    destination = target_root / args.name

    if not source.is_dir():
      raise SystemExit(f"Template not found: {source}")
    target_root.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not args.force:
            raise SystemExit(f"Destination exists: {destination}. Use --force to replace it.")
        shutil.rmtree(destination)

    shutil.copytree(source, destination)
    print(f"Installed Graphify Nebula template: {destination}")
    print(f"Open: {destination / 'index.html'}")
    print("Connect data by setting data-graph-src on .nebula-shell or by calling NebulaGraph.mount(el, {src: '/api/graph'}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
