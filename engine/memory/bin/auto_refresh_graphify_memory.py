#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from portable_paths import BIN_ROOT, DATA_ROOT, LOG_ROOT, MEMORIA_ROOT, PROJECTS_ROOTS

REFRESH_SCRIPT = BIN_ROOT / "refresh_graphify_memory.py"
STATE_PATH = DATA_ROOT / ".graphify_auto_refresh_state.json"
LOCK_PATH = DATA_ROOT / ".graphify_auto_refresh.lock"
LOG_PATH = LOG_ROOT / "graphify_auto_refresh.log"

SKIP_DIRS = {
    ".git",
    ".obsidian",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".cache",
    "coverage",
    "tmp",
    "logs",
    ".turbo",
    "Graphify",
    "__pycache__",
}

RELEVANT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".php",
    ".sql",
    ".yml",
    ".yaml",
    ".html",
    ".css",
    ".xml",
    ".sh",
    ".toml",
    ".env.example",
    ".example",
}

MIN_SECONDS_BETWEEN_REFRESH = 300


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def read_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"[{timestamp}] {message}\n")


def should_include_file(path: Path) -> bool:
    if path.name.startswith(".") and path.suffix.lower() not in {".env.example", ".example"}:
        return False
    if path.name in {"package-lock.json", "package.json", "README.md", "README", "Dockerfile", "docker-compose.yml", "docker-compose.yaml"}:
        return True
    suffix = path.suffix.lower()
    if suffix in RELEVANT_SUFFIXES:
        return True
    return path.name.lower().endswith((".env.example", ".example"))


def scan_tree(root: Path, exclude_graphify: bool = False) -> dict:
    latest_mtime = 0.0
    file_count = 0
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if exclude_graphify and Path(current_root).name == "Graphify":
            dirnames[:] = []
            continue
        for filename in filenames:
            path = Path(current_root) / filename
            if exclude_graphify and "Graphify" in path.parts:
                continue
            if not should_include_file(path):
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            file_count += 1
            if stat.st_mtime > latest_mtime:
                latest_mtime = stat.st_mtime
    return {
        "root": str(root),
        "file_count": file_count,
        "latest_mtime": latest_mtime,
        # Detect empty additions, renames and folder swaps even when no relevant
        # file count or timestamp changes.
        "direct_projects": sorted(
            item.name for item in root.iterdir()
            if item.is_dir() and not item.is_symlink() and not item.name.startswith(".") and item.name not in SKIP_DIRS
        ),
    }


def build_signature() -> dict:
    vault = scan_tree(MEMORIA_ROOT, exclude_graphify=True)
    projects = [scan_tree(root, exclude_graphify=False) for root in PROJECTS_ROOTS if root.exists()]
    return {
        "vault": vault,
        "projects": projects,
    }


def signatures_equal(a: dict | None, b: dict | None) -> bool:
    return a == b


def lock_is_active() -> bool:
    if not LOCK_PATH.exists():
        return False
    try:
        data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        pid = int(data.get("pid", 0))
    except Exception:
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock() -> None:
    LOCK_PATH.write_text(json.dumps({"pid": os.getpid(), "started_at": iso_now()}), encoding="utf-8")


def release_lock() -> None:
    LOCK_PATH.unlink(missing_ok=True)


def last_refresh_recent(last_refresh_at: str | None) -> bool:
    if not last_refresh_at:
        return False
    try:
        last_dt = datetime.fromisoformat(last_refresh_at)
    except ValueError:
        return False
    return (utc_now() - last_dt).total_seconds() < MIN_SECONDS_BETWEEN_REFRESH


def run_refresh() -> int:
    env = os.environ.copy()
    env["PATH"] = f"{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    proc = subprocess.run(
        [sys.executable, str(REFRESH_SCRIPT)],
        cwd=str(MEMORIA_ROOT.parent),
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.stdout.strip():
        log(proc.stdout.strip())
    if proc.stderr.strip():
        log(proc.stderr.strip())
    return proc.returncode


def main() -> int:
    if lock_is_active():
        log("refresh skipped: another run is still active")
        return 0

    acquire_lock()
    try:
        state = read_state()
        signature_before = build_signature()
        last_refresh_at = state.get("last_refresh_at")
        last_signature = state.get("last_signature")
        reasons: list[str] = []

        if not last_refresh_at:
            reasons.append("first_run")
        else:
            try:
                last_date = datetime.fromisoformat(last_refresh_at).date()
            except ValueError:
                last_date = None
            if last_date != datetime.now().date():
                reasons.append("daily_refresh")

        if not signatures_equal(signature_before, last_signature):
            reasons.append("source_changed")

        if not reasons:
            state["last_checked_at"] = iso_now()
            write_state(state)
            log("no refresh needed")
            return 0

        if last_refresh_recent(last_refresh_at):
            state["last_checked_at"] = iso_now()
            write_state(state)
            log(f"refresh skipped: recent run within debounce window; reasons={','.join(reasons)}")
            return 0

        log(f"refresh starting; reasons={','.join(reasons)}")
        code = run_refresh()
        signature_after = build_signature()

        state.update(
            {
                "last_checked_at": iso_now(),
                "last_refresh_at": iso_now(),
                "last_signature": signature_after,
                "last_refresh_exit_code": code,
                "last_refresh_reasons": reasons,
            }
        )
        write_state(state)

        if code == 0:
            log("refresh completed successfully")
            return 0

        log(f"refresh failed with exit code {code}")
        return code
    finally:
        release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
