#!/usr/bin/env python3
"""
Obsidian Vault Auto-Sync & GitHub Backup Engine
Monitors the vault for additions/modifications and pushes segmented, clean commits.
"""

import datetime
import os
import subprocess
import sys

VAULT_DIR = "/Users/macbookpro/Documents/Obsidian Vault"
LOG_FILE = os.path.join(VAULT_DIR, ".memoria-system", "logs", "git_backup.log")


def log(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def run_cmd(args, timeout=120) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            cwd=VAULT_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout expired"
    except Exception as e:
        return -1, "", str(e)


def sync_vault():
    os.chdir(VAULT_DIR)

    # 1. Check git status
    code, out, err = run_cmd(["git", "status", "--porcelain"])
    if code != 0:
        log(f"Error checking git status: {err}")
        return False

    if not out:
        # Nothing changed
        return True

    # 2. Stage changes
    code, out_add, err_add = run_cmd(["git", "add", "-A"])
    if code != 0:
        log(f"Error running git add: {err_add}")
        return False

    # 3. Analyze staged changes for commit message
    code, diff_stat, _ = run_cmd(["git", "diff", "--cached", "--name-status"])
    if not diff_stat:
        return True

    lines = [l for l in diff_stat.split("\n") if l.strip()]
    count = len(lines)

    # Sample top modified files
    samples = []
    for l in lines[:5]:
        parts = l.split("\t", 1)
        if len(parts) == 2:
            status, path = parts
            samples.append(f"{status}: {os.path.basename(path)}")

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample_text = ", ".join(samples)
    if count > 5:
        sample_text += f", +{count - 5} más"

    commit_title = f"sync(auto): {count} nodo(s) actualizado(s) [{now_str}]"
    commit_body = f"Archivos sincronizados ({count}):\n" + "\n".join(f"- {l}" for l in lines[:25])
    if count > 25:
        commit_body += f"\n- ... y {count - 25} archivo(s) adicional(es)"

    full_commit_msg = f"{commit_title}\n\n{commit_body}"

    # 4. Commit
    code, c_out, c_err = run_cmd(["git", "commit", "-m", full_commit_msg])
    if code != 0:
        log(f"Git commit warning: {c_err}")
        return False

    log(f"Commit realizado: {commit_title} ({sample_text})")

    # 5. Push to GitHub
    code, p_out, p_err = run_cmd(["git", "push", "origin", "main"], timeout=180)
    if code != 0:
        log(f"Advertencia al subir a GitHub (se reintentará en el próximo ciclo): {p_err}")
        return False

    log(f"Sincronización remota exitosa hacia origin/main ({count} nodos respaldados)")
    return True


if __name__ == "__main__":
    success = sync_vault()
    sys.exit(0 if success else 1)
