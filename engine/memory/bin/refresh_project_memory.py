#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from portable_paths import (
    ANTIGRAVITY_SKILLS,
    CLAUDE_ROOT,
    CODEX_ROOT,
    DATA_ROOT,
    MEMORIA_ROOT as CORP_ROOT,
    PROJECT_GRAPHS_ROOT,
    PROJECTS_ROOTS,
    SETTINGS,
    SYSTEM_ROOT,
    VAULT_ROOT,
    portable_project_path,
)

TOOL_ROOT = Path(__file__).resolve().parent
MEMORY_ROOT = CORP_ROOT / "Proyectos Git"
SEGMENTED_PROJECTS_ROOT = CORP_ROOT / "Proyectos"
INDEX_PATH = DATA_ROOT / "memoria_index.json"
INTEGRATION_IMPORT_ROOT = SYSTEM_ROOT / "imports" / "project-integrations"

MANUAL_START = "<!-- memoria-manual-start -->"
MANUAL_END = "<!-- memoria-manual-end -->"
OLD_MANUAL_START = "<!-- codex-manual-start -->"
OLD_MANUAL_END = "<!-- codex-manual-end -->"

SKIP_DIRS = {
    ".git",
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
    "__pycache__",
}

SECTION_DIRS = {
    "arquitectura": CORP_ROOT / "Arquitectura",
    "runbooks": CORP_ROOT / "Runbooks",
    "decisiones": CORP_ROOT / "Decisiones",
    "incidentes": CORP_ROOT / "Incidentes",
    "ambientes": CORP_ROOT / "Ambientes",
    "clientes": CORP_ROOT / "Clientes Dominios",
    "checklists": CORP_ROOT / "Checklists",
    "convenciones": CORP_ROOT / "Convenciones",
    "reportes": CORP_ROOT / "Reportes",
    "bitacora": CORP_ROOT / "Bitacora",
    "templates": CORP_ROOT / "Templates",
    "multimedia": CORP_ROOT / "Multimedia",
    "skills": CORP_ROOT / "Skills",
}

MULTIMEDIA_ROOT = CORP_ROOT / "Multimedia"
MULTIMEDIA_LIBRARY = MULTIMEDIA_ROOT / "Biblioteca"
MULTIMEDIA_GENERATED = MULTIMEDIA_ROOT / "Activos"

MULTIMEDIA_EXTENSIONS = {
    ".ai": "diseno",
    ".aiff": "audio",
    ".avi": "video",
    ".csv": "datos",
    ".doc": "documento",
    ".docx": "documento",
    ".eps": "logo/vector",
    ".fig": "diseno",
    ".gif": "imagen",
    ".heic": "imagen",
    ".jpeg": "imagen",
    ".jpg": "imagen",
    ".json": "datos",
    ".key": "presentacion",
    ".m4a": "audio",
    ".mov": "video",
    ".mp3": "audio",
    ".mp4": "video",
    ".otf": "fuente",
    ".pdf": "documento",
    ".png": "imagen",
    ".ppt": "presentacion",
    ".pptx": "presentacion",
    ".psd": "diseno",
    ".svg": "logo/vector",
    ".ttf": "fuente",
    ".wav": "audio",
    ".webm": "video",
    ".webp": "imagen",
    ".xls": "hoja",
    ".xlsx": "hoja",
    ".zip": "paquete",
}

SKILL_SOURCES = {
    "Codex": CODEX_ROOT / "skills",
    "Claude": CLAUDE_ROOT / "skills",
    "Antigravity": ANTIGRAVITY_SKILLS,
}
SKILLS_ROOT = CORP_ROOT / "Skills"
SKILL_CATEGORY_KEYWORDS = {
    "Ciberseguridad y auditoría": ("security", "vulnerability", "vulnerabilidad", "pentest", "pen-test", "cve", "owasp", "threat"),
    "Marketing y contenido": ("marketing", "copy", "content", "seo", "ads", "social", "email", "brand", "proposal", "client"),
    "Diseno y frontend": ("frontend", "design", "ui", "ux", "accessibility", "tailwind", "shadcn", "react", "layout", "color", "polish"),
    "Video e imagen": ("image", "video", "remotion", "higgsfield", "visual", "animate", "photo"),
    "Datos y analitica": ("analytics", "data", "audit", "accounting", "financial", "spreadsheet", "reporting"),
    "Automatizacion e integraciones": ("n8n", "workflow", "automation", "webhook", "linear", "gmail", "calendar"),
    "Backend e infraestructura": ("node", "express", "postgres", "supabase", "stripe", "cloudflare", "vercel", "docker", "haproxy", "strapi"),
    "Memoria y documentacion": ("memory", "obsidian", "graph", "doc", "writing", "skill", "plugin"),
    "Debugging y calidad": ("debug", "test", "vitest", "security", "harden", "audit", "optimize"),
}

SKILL_ROUTER_RULES = [
    {
        "intent": "Marca, marketing, contenido o ventas",
        "triggers": "branding, marca, logo, propuesta de valor, copy, anuncios, SEO, redes, email, propuesta comercial",
        "skills": ["brand-identity", "marketing-ia-expert", "copywriting-pro", "content-strategy", "paid-ads", "seo-expert", "social-media-strategy", "social-media-design", "email-marketing", "proposal-writer"],
    },
    {
        "intent": "Frontend, UI, UX y accesibilidad",
        "triggers": "interfaz, pantalla, componente, diseño web, accesibilidad, responsive, Tailwind, shadcn, React",
        "skills": ["frontend-design", "ui-ux-pro-max", "accessibility", "tailwind-css-patterns", "shadcn", "vercel-react-best-practices", "web-design-guidelines"],
    },
    {
        "intent": "Automatizaciones, n8n e integraciones",
        "triggers": "workflow, automatizacion, webhook, n8n, AI Agent tool, expresiones, nodos, validacion n8n",
        "skills": ["n8n-workflow-patterns", "n8n-node-configuration", "n8n-expression-syntax", "n8n-validation-expert", "n8n-code-javascript", "n8n-code-python", "n8n-code-tool", "n8n-mcp-tools-expert"],
    },
    {
        "intent": "Video, imagen y continuidad visual",
        "triggers": "imagen, editar imagen, video, Remotion, Higgsfield, campaña visual, continuidad, prompt de video",
        "skills": ["imagegen", "higgsfield", "remotion-best-practices", "video-continuity", "video-prompt-engineering"],
    },
    {
        "intent": "Backend, infraestructura y despliegue",
        "triggers": "Node.js, Express, Strapi, Supabase, Stripe, Cloudflare, Vercel, Docker, HAProxy, PostgreSQL",
        "skills": ["nodejs-best-practices", "nodejs-backend-patterns", "nodejs-express-server", "strapi-workspace-expert", "supabase", "stripe-best-practices", "cloudflare-dns", "deploy-to-vercel", "haproxy-lab-ops"],
    },
    {
        "intent": "Memoria, documentos y graphify",
        "triggers": "Obsidian, memoria, Graphify, contexto previo, documento, redaccion, runbook, skill nueva",
        "skills": ["project-memory", "doc", "writing-guidelines", "skill-creator", "skill-installer", "obsidian-graph-replicator"],
    },
    {
        "intent": "Auditoria, contabilidad, datos y reportes",
        "triggers": "auditoria, contabilidad, ERP, conciliacion, impuestos, reporte financiero, analitica",
        "skills": ["accounting-audit-expert", "accounting-systems-engineer", "audit-data-analytics", "financial-reporting", "tax-compliance-gt"],
    },
    {
        "intent": "Debugging y verificacion",
        "triggers": "bug dificil, error intermitente, test, Vitest, performance, optimizar",
        "skills": ["debugging-code", "debug-mode", "vitest", "vercel-optimize"],
    },
    {
        "intent": "Ciberseguridad y auditoría de vulnerabilidades",
        "triggers": "seguridad, vulnerabilidad, auditoria de seguridad, security audit, pentest, pen-test, cve, injection, owasp, auth bypass",
        "skills": ["security-audit"],
    },
]


def sh(args: list[str], cwd: Path | None = None, timeout: int = 15) -> str:
    try:
        return subprocess.check_output(args, cwd=cwd, stderr=subprocess.DEVNULL, text=True, timeout=timeout).strip()
    except Exception:
        return ""


def read_text(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(errors="ignore")[:limit]
    except Exception:
        return ""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sync_project_integrations() -> list[dict]:
    """Mirror small Obsidian/Graphify integration sources that live in repos."""
    manifest: list[dict] = []
    skipped_dirs = SKIP_DIRS | {"graphify-out", ".obsidian"}
    for root in PROJECTS_ROOTS:
        if not root.exists():
            continue
        for current, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in skipped_dirs and not d.startswith(".")]
            current_path = Path(current)
            for filename in filenames:
                source = current_path / filename
                relative = source.relative_to(root)
                lowered = relative.as_posix().lower()
                if "obsidian" not in lowered and "graphify" not in lowered:
                    continue
                if source.is_symlink() or source.stat().st_size > 5_000_000:
                    continue
                if filename.startswith(".env") or any(token in lowered for token in ("secret", "credential", "token")):
                    continue
                mirror = INTEGRATION_IMPORT_ROOT / root.name / relative
                mirror.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, mirror)
                manifest.append({
                    "source": portable_project_path(source),
                    "mirror": mirror.relative_to(SYSTEM_ROOT).as_posix(),
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "bytes": source.stat().st_size,
                })
    write(INTEGRATION_IMPORT_ROOT / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


def md_cell(value: object) -> str:
    return str(value or "").replace("|", "/").replace("\n", " ")


def preserve_manual(path: Path) -> str:
    text = read_text(path)
    if MANUAL_START in text and MANUAL_END in text:
        return text.split(MANUAL_START, 1)[1].split(MANUAL_END, 1)[0].strip("\n")
    if OLD_MANUAL_START in text and OLD_MANUAL_END in text:
        return text.split(OLD_MANUAL_START, 1)[1].split(OLD_MANUAL_END, 1)[0].strip("\n")
    marker = "## Contexto de chat / decisiones"
    if marker in text:
        tail = text.split(marker, 1)[1]
        next_marker = "\n## "
        if next_marker in tail:
            tail = tail.split(next_marker, 1)[0]
        cleaned = tail.strip()
        if cleaned and "Pendiente de alimentar" not in cleaned:
            return cleaned
    return "- Agregar aqui decisiones confirmadas y contexto humano que no debe borrarse."


def package_info(repo: Path) -> tuple[dict, dict, dict, list[str]]:
    package_path = repo / "package.json"
    if not package_path.exists():
        return {}, {}, {}, []
    try:
        package = json.loads(package_path.read_text(errors="ignore"))
    except Exception:
        return {}, {}, {}, []

    scripts = package.get("scripts") or {}
    deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies"):
        deps.update(package.get(key) or {})

    checks = {
        "React": ["react"],
        "Vite": ["vite"],
        "Next.js": ["next"],
        "Vue": ["vue"],
        "Angular": ["@angular/core"],
        "NestJS": ["@nestjs/core"],
        "Express": ["express"],
        "Fastify": ["fastify"],
        "Strapi": ["@strapi/strapi"],
        "Prisma": ["prisma", "@prisma/client"],
        "TypeORM": ["typeorm"],
        "Sequelize": ["sequelize"],
        "Tailwind": ["tailwindcss"],
        "MUI": ["@mui/material"],
        "Ant Design": ["antd"],
        "PostgreSQL": ["pg"],
        "MySQL": ["mysql2", "mysql"],
        "SQL Server": ["mssql"],
        "MongoDB": ["mongoose", "mongodb"],
        "JWT": ["jsonwebtoken", "@nestjs/jwt"],
        "Axios": ["axios"],
        "Capacitor": ["@capacitor/core"],
        "PWA": ["vite-plugin-pwa"],
    }
    signals = [label for label, keys in checks.items() if any(key in deps for key in keys)]
    return package, scripts, deps, signals


def family(name: str) -> str:
    override = (SETTINGS.get("project_family_overrides") or {}).get(name)
    if override:
        return str(override)
    mapping = [
        ("contraloria", "Contraloria"),
        ("core-signature", "Core Signature"),
        ("core-strapi", "Core Signature"),
        ("usac-editorial", "USAC Editorial"),
        ("renap", "RENAP"),
        ("tec-infoapp", "TEC InfoApp"),
        ("crm", "CRM / Ventas"),
        ("softplus", "Softplus"),
        ("saas-alcore", "SaaS Alcore"),
        ("store", "Store"),
    ]
    for key, label in mapping:
        if key in name:
            return label
    return "Otros"


def project_role(name: str, signals: list[str]) -> str:
    if "frontend" in name or "static" in name:
        return "frontend"
    if "backend" in name or "api" in name:
        return "backend/api"
    if "balanceador" in name:
        return "infra/balanceador"
    if "Strapi" in signals:
        return "cms/backend"
    return "app"


def env_keys(repo: Path) -> list[str]:
    keys: list[str] = []
    patterns = [".env.example", ".env.*.example", "env.example"]
    for pattern in patterns:
        for path in repo.glob(pattern):
            for line in read_text(path, 50_000).splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key = line.split("=", 1)[0].strip()
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key) and key not in keys:
                    keys.append(key)
    return keys


def docker_files(repo: Path) -> list[str]:
    files: list[str] = []
    for pattern in ("Dockerfile", "Dockerfile.*", "docker-compose.yml", "docker-compose.yaml", "docker-compose-*.yml", "docker-compose-*.yaml"):
        files.extend(path.name for path in repo.glob(pattern) if path.is_file())
    return sorted(set(files))


def docker_ports(repo: Path) -> list[str]:
    ports: list[str] = []
    for name in docker_files(repo):
        text = read_text(repo / name, 80_000)
        for match in re.finditer(r"(?m)^\s*-\s*[\"']?(\d{2,5}:\d{2,5})", text):
            item = f"{name}: {match.group(1)}"
            if item not in ports:
                ports.append(item)
    return ports[:30]


def first_summary(repo: Path) -> str:
    for name in ("README.md", "README.MD", "Readme.md", "readme.md", "README"):
        path = repo / name
        if path.exists():
            text = read_text(path, 8_000)
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("#"):
                    return line.lstrip("#").strip()
            for line in text.splitlines():
                line = line.strip()
                if len(line) > 25 and not line.startswith(("[!", "<", "```")):
                    return line[:220]
    return ""


def git_files(repo: Path) -> list[str]:
    out = sh(["git", "ls-files"], cwd=repo)
    if out:
        return out.splitlines()
    files: list[str] = []
    for root, dirs, names in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in names:
            full = Path(root) / name
            files.append(str(full.relative_to(repo)))
    return files


def main_dirs(repo: Path) -> list[str]:
    return sorted(
        p.name
        for p in repo.iterdir()
        if p.is_dir() and p.name not in SKIP_DIRS and not p.name.startswith(".")
    )[:24]


def top_extensions(files: list[str]) -> str:
    counter = Counter()
    for file in files:
        if any(part in file for part in ("node_modules/", "vendor/", "dist/", "build/")):
            continue
        suffix = Path(file).suffix.lower() or "[sin extension]"
        counter[suffix] += 1
    return ", ".join(f"{ext}({count})" for ext, count in counter.most_common(10))


def frontend_routes(repo: Path, files: list[str]) -> list[str]:
    candidates = []
    for file in files:
        if not file.startswith("src/"):
            continue
        if not file.endswith((".tsx", ".jsx", ".ts", ".js")):
            continue
        if any(part in file for part in ("/pages/", "/routes/", "App.tsx", "App.jsx", "router")):
            text = read_text(repo / file, 100_000)
            for match in re.finditer(r"""path\s*[:=]\s*["'`]([^"'`]+)["'`]""", text):
                candidates.append(f"{match.group(1)} ({file})")
            for match in re.finditer(r"""<Route[^>]+path=["'`]([^"'`]+)["'`]""", text):
                candidates.append(f"{match.group(1)} ({file})")
    return sorted(set(candidates))[:80]


def endpoints(repo: Path, files: list[str]) -> list[str]:
    found = []
    pattern = re.compile(r"""["'`]((?:https?://[^"'`\s]+|/api/[^"'`\s)]+|api/[^"'`\s)]+))["'`]""")
    for file in files:
        if not file.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")):
            continue
        if not (file.startswith("src/") or file.startswith("server") or file.startswith("config/")):
            continue
        text = read_text(repo / file, 160_000)
        for match in pattern.finditer(text):
            value = match.group(1)
            if len(value) < 160:
                found.append(f"{value} ({file})")
    return sorted(set(found))[:120]


def services_and_pages(files: list[str]) -> tuple[list[str], list[str], list[str]]:
    services = [f for f in files if f.startswith("src/services/") and f.endswith((".ts", ".tsx", ".js", ".jsx"))]
    pages = [f for f in files if ("/pages/" in f or f.startswith("src/pages/")) and f.endswith((".ts", ".tsx", ".js", ".jsx"))]
    components = [f for f in files if f.startswith("src/components/") and f.endswith((".ts", ".tsx", ".js", ".jsx"))]
    return services[:120], pages[:160], components[:120]


def strapi_content_types(repo: Path) -> list[str]:
    items = []
    for schema in repo.glob("src/api/*/content-types/*/schema.json"):
        try:
            data = json.loads(schema.read_text(errors="ignore"))
        except Exception:
            data = {}
        singular = data.get("info", {}).get("singularName") or schema.parent.name
        plural = data.get("info", {}).get("pluralName") or schema.parents[2].name
        attrs = data.get("attributes") or {}
        attr_names = ", ".join(sorted(attrs.keys())[:24])
        items.append(f"{plural} / {singular}: {attr_names} ({schema.relative_to(repo)})")
    return sorted(items)[:160]


def config_files(files: list[str]) -> list[str]:
    interesting = []
    names = (
        "vite.config",
        "next.config",
        "angular.json",
        "nest-cli.json",
        "tsconfig",
        "tailwind.config",
        "eslint.config",
        "server.mjs",
        "capacitor.config",
        "wrangler",
    )
    for file in files:
        if file in ("package.json", "composer.json", "Dockerfile") or file.startswith("config/") or any(Path(file).name.startswith(n) for n in names):
            interesting.append(file)
    return sorted(set(interesting))[:80]


def collect_projects() -> tuple[list[dict], list[str]]:
    projects: list[dict] = []
    nongit_other: list[str] = []
    used_names: set[str] = set()
    for root_index, root in enumerate(PROJECTS_ROOTS):
        if not root.exists():
            continue
        for path in sorted(root.iterdir()):
            if not path.is_dir() or path.name.startswith("."):
                if root_index == 0:
                    nongit_other.append(path.name)
                continue
            is_git = (path / ".git").exists()
            has_package = (path / "package.json").exists()
            has_graph = (path / "graphify-out").exists()
            if root_index > 0 and not (is_git or has_package or has_graph):
                continue
            memory_name = path.name
            if memory_name in used_names:
                memory_name = f"{path.name} - {root.name}"
            used_names.add(memory_name)
            package, scripts, deps, signals = package_info(path)
            files = git_files(path) if is_git or has_package else [
                str(item.relative_to(path))
                for item in path.rglob("*")
                if item.is_file() and not any(part in SKIP_DIRS for part in item.parts)
            ][:5000]
            dirty = sh(["git", "status", "--short"], cwd=path) if is_git else ""
            branch = sh(["git", "branch", "--show-current"], cwd=path) if is_git else ""
            remote = sh(["git", "remote", "get-url", "origin"], cwd=path) if is_git else ""
            last = sh(["git", "log", "-1", "--format=%h %ad %s", "--date=short"], cwd=path) if is_git else ""
            services, pages, components = services_and_pages(files)
            projects.append(
                {
                    "name": memory_name,
                    "folder_name": path.name,
                    "source_root": root.name,
                    "path": portable_project_path(path),
                    "is_git": is_git,
                    "inventory_only": not is_git and not has_package,
                    "family": family(path.name),
                    "role": project_role(path.name, signals),
                    "branch": branch,
                    "remote": remote,
                    "last": last,
                    "dirty": dirty.splitlines(),
                    "summary": first_summary(path),
                    "scripts": scripts,
                    "deps": deps,
                    "signals": signals,
                    "env_keys": env_keys(path),
                    "docker": docker_files(path),
                    "ports": docker_ports(path),
                    "dirs": main_dirs(path),
                    "top_ext": top_extensions(files),
                    "services": services,
                    "pages": pages,
                    "components": components,
                    "routes": frontend_routes(path, files),
                    "endpoints": endpoints(path, files),
                    "content_types": strapi_content_types(path),
                    "configs": config_files(files),
                }
            )
    return projects, nongit_other


def render_list(items: list[str], empty: str = "Por confirmar.", limit: int | None = None) -> str:
    if not items:
        return f"- {empty}\n"
    chosen = items[:limit] if limit else items
    return "".join(f"- `{item}`\n" for item in chosen)


def note_safe(value: str) -> str:
    return re.sub(r'[\\/*?:"<>|#^[\]]', "-", value).strip().strip(".") or "Sin nombre"


def segmented_rel(project: dict) -> Path:
    return Path(note_safe(project["family"])) / note_safe(project["name"])


def metadata(project: dict, tipo: str, seccion: str = "") -> str:
    """Stable properties for native Obsidian Bases, search and filtering."""
    def value(item: object) -> str:
        return json.dumps(str(item), ensure_ascii=False)

    tags = ["memoria", "proyecto", f"familia/{note_safe(project['family']).lower().replace(' ', '-')}"]
    lines = [
        "---\n",
        f"tipo: {value(tipo)}\n",
        f"proyecto: {value(project['name'])}\n",
        f"familia: {value(project['family'])}\n",
        f"rol: {value(project['role'])}\n",
        f"raiz: {value(project.get('source_root', 'PROYECTOS'))}\n",
        "estado: \"activo\"\n",
        "generado: true\n",
        f"actualizado: {dt.date.today().isoformat()}\n",
    ]
    if seccion:
        lines.append(f"seccion: {value(seccion)}\n")
    lines.append("tags:\n")
    lines.extend(f"  - {value(tag)}\n" for tag in tags)
    lines.append("---\n\n")
    return "".join(lines)


def project_graph_status(project: dict) -> dict:
    graph_dir = PROJECT_GRAPHS_ROOT / project.get("source_root", "PROYECTOS") / project.get("folder_name", project["name"])
    return {
        "dir": graph_dir,
        "snapshot": graph_dir.is_dir(),
        "json": (graph_dir / "graph.json").is_file(),
        "report": (graph_dir / "GRAPH_REPORT.md").is_file(),
        "html": (graph_dir / "graph.html").is_file(),
        "manifest": (graph_dir / "manifest.json").is_file(),
    }


def render_project_segments(project: dict, all_projects: list[dict]) -> dict[str, str]:
    shards: dict[str, str] = {}

    def sharded_section(title: str, items: list[str], prefix: str, chunk_size: int, empty: str) -> str:
        if len(items) <= chunk_size:
            return f"## {title}\n" + render_list(items, empty)
        lines = [f"## {title}\n", f"{len(items)} elementos divididos para lectura incremental:\n"]
        for index in range(0, len(items), chunk_size):
            number = index // chunk_size + 1
            note_name = f"{prefix} {number:02d}"
            chunk = items[index:index + chunk_size]
            shards[f"{note_name}.md"] = metadata(project, "contexto-proyecto", note_name.lower().replace(" ", "-")) + f"# {project['name']} — {title} {number:02d}\n\n" + render_list(chunk, empty)
            lines.append(f"- [[{note_name}]] ({len(chunk)} elementos)\n")
        return "".join(lines)

    related = [
        other["name"] for other in all_projects
        if other["name"] != project["name"] and other["family"] == project["family"]
    ]
    graph = project_graph_status(project)
    home = [metadata(project, "proyecto", "inicio"), f"# {project['name']} — Inicio\n\n"]
    home.extend([
        "Mapa de contenido segmentado. Esta carpeta se regenera desde el inventario tecnico y no contiene secretos.\n\n",
        "## Navegacion\n",
        "- [[05 - Contexto para IA]]\n",
        "- [[10 - Resumen y relaciones]]\n",
        "- [[20 - Arquitectura y stack]]\n",
        "- [[30 - Operacion y entorno]]\n",
        "- [[40 - Interfaz y componentes]]\n",
        "- [[50 - Servicios y APIs]]\n",
        "- [[60 - Datos y modelos]]\n",
        "- [[70 - Estado local]]\n",
        "- [[80 - Cobertura Obsidian y Graphify]]\n",
        f"- [[../../../Proyectos Git/{project['name']}|Contexto manual y compatibilidad]]\n",
        f"- [[../../../Runbooks/{project['name']}|Runbook]]\n",
    ])

    summary = [metadata(project, "contexto-proyecto", "resumen"), f"# {project['name']} — Resumen y relaciones\n\n"]
    summary.extend([
        f"- Familia: {project['family']}\n",
        f"- Rol: {project['role']}\n",
        f"- Raiz: `{project.get('source_root', 'PROYECTOS')}`\n",
        f"- Ruta portable: `{project['path']}`\n",
        f"- Descripcion: {project['summary'] or 'Por completar.'}\n",
        f"- Git: {'si' if project['is_git'] else 'no detectado'}\n",
        f"- Remoto: `{project['remote'] or 'sin remoto origin detectado'}`\n",
        "\n## Proyectos relacionados\n",
    ])
    summary.extend([f"- [[../../{note_safe(project['family'])}/{note_safe(name)}/00 - Inicio|{name}]]\n" for name in related] or ["- Por confirmar.\n"])

    architecture = [metadata(project, "contexto-proyecto", "arquitectura"), f"# {project['name']} — Arquitectura y stack\n\n"]
    architecture.append("## Stack detectado\n" + render_list(project["signals"], "Por confirmar."))
    architecture.append("\n## Estructura principal\n" + render_list(project["dirs"]))
    architecture.append("\n## Configuracion\n" + render_list(project["configs"]))
    architecture.append(f"\n## Tipos de archivo\n- {project['top_ext'] or 'Por confirmar'}\n")

    operation = [metadata(project, "contexto-proyecto", "operacion"), f"# {project['name']} — Operacion y entorno\n\n", "## Comandos\n"]
    if project["scripts"]:
        operation.extend(f"- `{key}`: `{value}`\n" for key, value in project["scripts"].items())
    else:
        operation.append("- No se detectaron scripts en `package.json`.\n")
    operation.append("\n## Docker\n" + render_list(project["docker"], "No detectado."))
    operation.append("\n## Puertos\n" + render_list(project["ports"], "No detectados."))
    operation.append("\n## Variables esperadas (solo nombres)\n" + render_list(project["env_keys"], "No detectadas.", 120))

    interface = [metadata(project, "contexto-proyecto", "interfaz"), f"# {project['name']} — Interfaz y componentes\n\n"]
    interface.append(sharded_section("Paginas y vistas", project["pages"], "41 - Paginas", 50, "No detectadas."))
    interface.append("\n" + sharded_section("Componentes", project["components"], "42 - Componentes", 50, "No detectados."))
    interface.append("\n" + sharded_section("Rutas frontend", project["routes"], "43 - Rutas frontend", 50, "No detectadas."))

    services = [metadata(project, "contexto-proyecto", "servicios-api"), f"# {project['name']} — Servicios y APIs\n\n"]
    services.append(sharded_section("Servicios", project["services"], "51 - Servicios", 50, "No detectados."))
    services.append("\n" + sharded_section("Endpoints y URLs", project["endpoints"], "52 - Endpoints", 40, "No detectados."))

    data = [metadata(project, "contexto-proyecto", "datos-modelos"), f"# {project['name']} — Datos y modelos\n\n"]
    data.append(sharded_section("Strapi content-types", project["content_types"], "61 - Content types", 12, "No detectados."))
    data.append("\n## Dependencias de persistencia detectadas\n")
    persistence = [s for s in project["signals"] if s in {"PostgreSQL", "MySQL", "SQL Server", "MongoDB", "Prisma", "TypeORM", "Sequelize", "Strapi"}]
    data.append(render_list(persistence, "No detectadas."))

    state = [metadata(project, "contexto-proyecto", "estado-local"), f"# {project['name']} — Estado local\n\n"]
    state.extend([
        f"- Rama: `{project['branch'] or 'sin rama detectada'}`\n",
        f"- Ultimo commit: `{project['last'] or 'sin commits detectados'}`\n",
        f"- Cambios locales: {len(project['dirty'])}\n",
    ])
    if project["dirty"]:
        state.append("\n```text\n" + "\n".join(project["dirty"][:120]) + "\n```\n")
    state.append("\nAntes de editar, volver a ejecutar `git status --short`; este estado es solo una captura.\n")

    coverage = [metadata(project, "contexto-proyecto", "cobertura"), f"# {project['name']} — Cobertura Obsidian y Graphify\n\n"]
    coverage.extend([
        "## Memoria visible\n",
        "- Nota principal: si\n",
        "- Runbook: si\n",
        "- Carpeta segmentada: si\n",
        f"- Inventario solamente: {'si' if project.get('inventory_only') else 'no'}\n",
        "\n## Snapshot Graphify individual\n",
        f"- Existe: {'si' if graph['snapshot'] else 'no'}\n",
        f"- `graph.json`: {'si' if graph['json'] else 'no'}\n",
        f"- `GRAPH_REPORT.md`: {'si' if graph['report'] else 'no'}\n",
        f"- `graph.html`: {'si' if graph['html'] else 'no'}\n",
        f"- `manifest.json`: {'si' if graph['manifest'] else 'no'}\n",
        "\nTodos los proyectos forman parte del grafo maestro aunque no tengan snapshot Graphify individual.\n",
    ])
    result = {
        "00 - Inicio.md": "".join(home),
        "10 - Resumen y relaciones.md": "".join(summary),
        "20 - Arquitectura y stack.md": "".join(architecture),
        "30 - Operacion y entorno.md": "".join(operation),
        "40 - Interfaz y componentes.md": "".join(interface),
        "50 - Servicios y APIs.md": "".join(services),
        "60 - Datos y modelos.md": "".join(data),
        "70 - Estado local.md": "".join(state),
        "80 - Cobertura Obsidian y Graphify.md": "".join(coverage),
    }
    result.update(shards)
    return result


def render_coverage_matrix(projects: list[dict]) -> str:
    selected = [p for p in projects if p.get("source_root") == "PROYECTOS"]
    lines = ["# Cobertura PROYECTOS en Obsidian y Graphify\n\n"]
    lines.append(f"Cobertura de memoria: **{len(selected)}/{len(selected)}** carpetas directas de `PROYECTOS`.\n\n")
    graph_count = sum(project_graph_status(p)["snapshot"] for p in selected)
    lines.append(f"Snapshots Graphify individuales existentes: **{graph_count}/{len(selected)}**. Los demas proyectos siguen incluidos en el grafo maestro por el inventario tecnico.\n\n")
    lines.append("| Proyecto | Memoria | Segmentos | Runbook | Snapshot | JSON | Reporte | HTML |\n")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|\n")
    for p in selected:
        g = project_graph_status(p)
        link = f"../Proyectos/{note_safe(p['family'])}/{note_safe(p['name'])}/00 - Inicio"
        yn = lambda value: "si" if value else "no"
        lines.append(f"| [[{link}|{p['name']}]] | si | si | si | {yn(g['snapshot'])} | {yn(g['json'])} | {yn(g['report'])} | {yn(g['html'])} |\n")
    lines.extend([
        "\n## Interpretacion\n",
        "- `Memoria` confirma que existe una representacion navegable y portable en el baul.\n",
        "- `Snapshot` confirma que Graphify se ejecuto individualmente sobre ese proyecto.\n",
        "- No se copian repositorios, dependencias ni secretos; estos deben restaurarse con Git u otro respaldo.\n",
    ])
    return "".join(lines)


def render_project_moc(project: dict) -> str:
    """Keep legacy project links stable while directing readers to small notes."""
    manual = preserve_manual(MEMORY_ROOT / f"{project['name']}.md")
    segmented = segmented_rel(project)
    lines = [metadata(project, "proyecto-moc", "compatibilidad"), f"# {project['name']}\n\n"]
    lines.extend([
        "## Navegacion modular\n",
        f"- [[../Proyectos/{segmented.as_posix()}/00 - Inicio|Abrir memoria segmentada]]\n",
        f"- [[../Runbooks/{project['name']}|Runbook operativo]]\n",
        "- [[Contexto de Chats|Contexto historico compartido]]\n",
        "\n## Identidad rapida\n",
        f"- Familia: {project['family']}\n",
        f"- Rol: {project['role']}\n",
        f"- Ruta portable: `{project['path']}`\n",
        f"- Stack: {', '.join(project['signals']) or 'Por confirmar'}\n",
        "\n## Contexto manual preservado\n",
        f"{MANUAL_START}\n{manual}\n{MANUAL_END}\n",
        "\nLa informacion detectada automaticamente se divide por tema en la carpeta modular para que cada nota sea pequena y facil de procesar.\n",
    ])
    return "".join(lines)


def render_project(project: dict, all_projects: list[dict]) -> str:
    manual = preserve_manual(MEMORY_ROOT / f"{project['name']}.md")
    related = [
        other["name"]
        for other in all_projects
        if other["name"] != project["name"] and other["family"] == project["family"]
    ]
    segmented = segmented_rel(project)
    lines = [f"# {project['name']}\n\n"]
    lines.append(f"> [!tip] Memoria segmentada\n> Abrir [[../Proyectos/{segmented.as_posix()}/00 - Inicio|indice modular del proyecto]].\n\n")
    lines.append("## Resumen\n")
    lines.append(f"- Familia: [[Mapa de Proyectos#{project['family']}|{project['family']}]]\n")
    lines.append(f"- Rol probable: {project['role']}\n")
    lines.append(f"- Ruta local: `{project['path']}`\n")
    lines.append(f"- Git: {'si' if project['is_git'] else 'no detectado en esta carpeta'}\n")
    lines.append(f"- Remoto: `{project['remote'] or 'sin remoto origin detectado'}`\n")
    lines.append(f"- Rama actual: `{project['branch'] or 'sin rama detectada'}`\n")
    lines.append(f"- Ultimo commit: `{project['last'] or 'sin commits detectados'}`\n")
    lines.append(f"- Descripcion detectada: {project['summary'] or 'Por completar.'}\n")
    lines.append(f"- Stack detectado: {', '.join(project['signals']) or 'Por confirmar'}\n")
    lines.append(f"- Tipos de archivo principales: {project['top_ext'] or 'Por confirmar'}\n")

    lines.append("\n## Estado local\n")
    if project["dirty"]:
        lines.append(f"Hay {len(project['dirty'])} cambio(s) local(es). No revertir ni pisar sin revisar.\n\n")
        lines.append("```text\n" + "\n".join(project["dirty"][:60]) + "\n```\n")
    else:
        lines.append("Sin cambios locales al momento del barrido.\n")

    lines.append("\n## Comandos detectados\n")
    if project["scripts"]:
        for key, value in project["scripts"].items():
            lines.append(f"- `{key}`: `{value}`\n")
    else:
        lines.append("- No se detectaron scripts en `package.json`.\n")

    lines.append("\n## Docker, puertos y entorno\n")
    lines.append("- Archivos Docker/Compose: " + (", ".join(f"`{x}`" for x in project["docker"]) if project["docker"] else "No detectados") + "\n")
    lines.append("- Puertos detectados: " + (", ".join(f"`{x}`" for x in project["ports"]) if project["ports"] else "No detectados") + "\n")
    lines.append("- Variables esperadas desde ejemplos: " + (", ".join(f"`{x}`" for x in project["env_keys"][:100]) if project["env_keys"] else "No detectadas") + "\n")

    lines.append("\n## Archivos de configuracion\n")
    lines.append(render_list(project["configs"]))

    lines.append("\n## Estructura principal\n")
    lines.append(render_list(project["dirs"]))

    lines.append("\n## Servicios frontend / cliente\n")
    lines.append(render_list(project["services"], "No detectados.", 80))

    lines.append("\n## Paginas / vistas\n")
    lines.append(render_list(project["pages"], "No detectadas.", 100))

    lines.append("\n## Rutas frontend detectadas\n")
    lines.append(render_list(project["routes"], "No detectadas.", 80))

    lines.append("\n## Endpoints y URLs detectadas\n")
    lines.append(render_list(project["endpoints"], "No detectados.", 100))

    lines.append("\n## Strapi content-types detectados\n")
    lines.append(render_list(project["content_types"], "No detectados.", 120))

    lines.append("\n## Componentes principales\n")
    lines.append(render_list(project["components"], "No detectados.", 80))

    lines.append("\n## Relaciones probables\n")
    if related:
        for name in related:
            lines.append(f"- [[{name}]]\n")
    else:
        lines.append("- Por confirmar.\n")

    lines.append("\n## Contexto de chat / decisiones\n")
    lines.append(f"{MANUAL_START}\n{manual}\n{MANUAL_END}\n")

    lines.append("\n## Notas operativas\n")
    lines.append("- Antes de modificar, revisar `git status --short`.\n")
    lines.append("- Si se trabaja con variables de entorno, usar ejemplos y no guardar secretos en Obsidian.\n")
    lines.append("- Si una duda toca endpoints o permisos, cruzar esta nota con [[Contexto de Chats]].\n")
    return "".join(lines)


def render_readme(projects: list[dict], nongit_other: list[str]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["# Memoria - Proyectos Git\n\n"]
    lines.append(f"Actualizado: {now} America/Guatemala\n\n")
    lines.append("Base de memoria local para trabajar con las raices configuradas en `.memoria-system/config/settings.json`.\n\n")
    lines.append("## Entrada rapida\n")
    lines.append("- [[Inicio Memoria]]\n")
    lines.append("- [[Mapa de Proyectos]]\n")
    lines.append("- [[Indice Tecnico Profundo]]\n")
    lines.append("- [[Contexto Operativo]]\n")
    lines.append("- [[Contexto de Chats]]\n")
    lines.append("- [[Pendientes de Memoria]]\n\n")
    lines.append("- [[../Reportes/Cobertura PROYECTOS en Obsidian y Graphify|Matriz de cobertura PROYECTOS]]\n")
    lines.append("- [[../Proyectos/Indice de Proyectos Segmentados|Indice de proyectos segmentados]]\n\n")
    lines.append("## Corporativo\n")
    lines.append("- [[../Arquitectura/Indice Corporativo|Indice Corporativo]]\n")
    lines.append("- [[../Arquitectura/Mapa de Dependencias|Mapa de Dependencias]]\n")
    lines.append("- [[../Ambientes/Inventario de Ambientes|Inventario de Ambientes]]\n")
    lines.append("- [[../Reportes/Reporte de Salud|Reporte de Salud]]\n")
    lines.append("- [[../Bitacora/Registro de Trabajo|Registro de Trabajo]]\n")
    lines.append("- [[../Multimedia/Multimedia|Multimedia]]\n")
    lines.append("- [[../Skills/Skills|Skills]]\n")
    lines.append("- [[../Convenciones/Convenciones de Desarrollo|Convenciones de Desarrollo]]\n")
    lines.append("- [[../Checklists/Checklist de Despliegue|Checklist de Despliegue]]\n\n")
    lines.append("## Plantillas\n")
    lines.append("- [[../Templates/Decision Tecnica|Decision Tecnica]]\n")
    lines.append("- [[../Templates/Bugfix|Bugfix]]\n")
    lines.append("- [[../Templates/Despliegue|Despliegue]]\n")
    lines.append("- [[../Templates/Modulo Arquitectura|Modulo / Arquitectura]]\n")
    lines.append("- [[../Templates/Incidente|Incidente]]\n")
    lines.append("- [[../Templates/Ambiente|Ambiente]]\n")
    lines.append("- [[../Templates/Runbook|Runbook]]\n\n")
    lines.append("- [[../Templates/Activo Multimedia|Activo Multimedia]]\n\n")
    lines.append("## Repositorios y carpetas de app\n")
    lines.append("| Proyecto | Familia | Rol | Stack detectado | Rama | Cambios locales | Nota |\n")
    lines.append("|---|---|---|---|---|---:|---|\n")
    for project in projects:
        lines.append(
            f"| {md_cell(project['name'])} | {md_cell(project['family'])} | {md_cell(project['role'])} | "
            f"{md_cell(', '.join(project['signals']) or 'Por confirmar')} | {md_cell(project['branch'])} | "
            f"{len(project['dirty'])} | [[{project['name']}]] |\n"
        )
    if nongit_other:
        lines.append("\n## Elementos no Git / no app detectados\n")
        for name in nongit_other:
            lines.append(f"- `{name}`\n")
    return "".join(lines)


def render_map(projects: list[dict]) -> str:
    by_family: dict[str, list[dict]] = defaultdict(list)
    for project in projects:
        by_family[project["family"]].append(project)
    lines = ["# Mapa de Proyectos\n\n"]
    lines.append("Agrupacion practica para navegar soluciones relacionadas.\n")
    for fam in sorted(by_family):
        lines.append(f"\n## {fam}\n")
        for project in sorted(by_family[fam], key=lambda p: p["name"]):
            lines.append(f"- [[{project['name']}]] - {project['role']}; stack: {', '.join(project['signals']) or 'por confirmar'}\n")
    return "".join(lines)


def render_deep_index(projects: list[dict]) -> str:
    lines = ["# Indice Tecnico Profundo\n\n"]
    lines.append("Vista compacta para encontrar rapido servicios, rutas, content-types y endpoints por proyecto.\n")
    for project in projects:
        lines.append(f"\n## {project['name']}\n")
        lines.append(f"- Nota: [[{project['name']}]]\n")
        lines.append(f"- Ruta local: `{project['path']}`\n")
        lines.append(f"- Stack: {', '.join(project['signals']) or 'por confirmar'}\n")
        if project["services"]:
            lines.append("- Servicios destacados: " + ", ".join(f"`{x}`" for x in project["services"][:18]) + "\n")
        if project["pages"]:
            lines.append("- Vistas destacadas: " + ", ".join(f"`{x}`" for x in project["pages"][:18]) + "\n")
        if project["content_types"]:
            lines.append("- Content-types: " + ", ".join(f"`{x.split(':', 1)[0]}`" for x in project["content_types"][:24]) + "\n")
        if project["endpoints"]:
            lines.append("- Endpoints/URLs: " + ", ".join(f"`{x.split(' (', 1)[0]}`" for x in project["endpoints"][:24]) + "\n")
    return "".join(lines)


def render_start_here(projects: list[dict]) -> str:
    dirty = [p for p in projects if p["dirty"]]
    lines = ["# Inicio Memoria\n\n"]
    lines.append("Leer esta nota primero cuando el usuario pida trabajar con proyectos locales configurados en `.memoria-system/config/settings.json`.\n\n")
    lines.append("## Procedimiento operativo\n")
    lines.append("1. Identificar el repo por nombre o por familia en [[Mapa de Proyectos]].\n")
    lines.append("2. Abrir la nota del proyecto y revisar `Estado local`, comandos, rutas, endpoints y relaciones.\n")
    lines.append("3. Ejecutar `git status --short` en el repo antes de editar.\n")
    lines.append("4. Si hay cambios locales, asumir que son del usuario y trabajar con ellos sin revertirlos.\n")
    lines.append("5. Cruzar dudas historicas con [[Contexto de Chats]].\n")
    lines.append("6. Despues de resolver algo importante, agregar una decision confirmada en la seccion manual de la nota del proyecto.\n\n")
    lines.append("## Comando de refresco\n")
    lines.append("```bash\nmemoria refresh-grafo\n```\n\n")
    lines.append("Los proyectos nuevos se detectan automaticamente cada 10 minutos, incluso si la carpeta esta vacia. Ver [[../Reportes/Incorporacion automatica de proyectos|estado de incorporacion]].\n\n")
    lines.append("## Proyectos con cambios locales al ultimo barrido\n")
    if dirty:
        for project in dirty:
            lines.append(f"- [[{project['name']}]]: {len(project['dirty'])} cambio(s)\n")
    else:
        lines.append("- Ninguno.\n")
    lines.append("\n## Archivos clave\n")
    lines.append("- [[README - Memoria]]\n")
    lines.append("- [[Indice Tecnico Profundo]]\n")
    lines.append("- [[Contexto Operativo]]\n")
    lines.append("- [[Contexto de Chats]]\n")
    lines.append("- [[Pendientes de Memoria]]\n")
    lines.append("- [[../Runbooks/Graphify - Sistema portable|Sistema portable Obsidian + Graphify]]\n")
    lines.append("- [[../Arquitectura/Indice Corporativo|Indice Corporativo]]\n")
    lines.append("- [[../Reportes/Reporte de Salud|Reporte de Salud]]\n")
    lines.append("- [[../Reportes/Incorporacion automatica de proyectos|Incorporacion automatica]]\n")
    lines.append("- [[../Ambientes/Inventario de Ambientes|Inventario de Ambientes]]\n")
    lines.append("- [[../Multimedia/Multimedia|Multimedia]]\n")
    lines.append("- [[../Skills/Skills|Skills]]\n")
    lines.append("\n## Plantillas para alimentar memoria\n")
    lines.append("- [[../Templates/Decision Tecnica|Decision Tecnica]]\n")
    lines.append("- [[../Templates/Bugfix|Bugfix]]\n")
    lines.append("- [[../Templates/Despliegue|Despliegue]]\n")
    lines.append("- [[../Templates/Modulo Arquitectura|Modulo / Arquitectura]]\n")
    lines.append("- [[../Templates/Incidente|Incidente]]\n")
    lines.append("- [[../Templates/Ambiente|Ambiente]]\n")
    lines.append("- [[../Templates/Runbook|Runbook]]\n")
    lines.append("- [[../Templates/Activo Multimedia|Activo Multimedia]]\n")
    return "".join(lines)


def render_pending(projects: list[dict]) -> str:
    lines = ["# Pendientes de Memoria\n\n"]
    lines.append("- Completar decisiones humanas verificadas por proyecto dentro del bloque manual de cada nota.\n")
    lines.append("- Confirmar relaciones exactas frontend/backend, puertos y dominios de despliegue cuando se levante cada stack.\n")
    lines.append("- Documentar credenciales de desarrollo solo si son no sensibles; nunca guardar secretos reales.\n")
    for project in projects:
        if not project["summary"]:
            lines.append(f"- Agregar descripcion funcional de [[{project['name']}]].\n")
        if not project["is_git"]:
            lines.append(f"- Confirmar si [[{project['name']}]] debe inicializar Git o pertenece a otro repo.\n")
    return "".join(lines)


def render_operational_context(projects: list[dict]) -> str:
    dirty = [p for p in projects if p["dirty"]]
    lines = ["# Contexto Operativo\n\n"]
    lines.append("Esta nota define como debe usarse esta memoria en conversaciones nuevas y durante trabajo tecnico sobre los proyectos locales.\n\n")
    lines.append("## Objetivo\n")
    lines.append("- Usar Obsidian como memoria navegable para todas las raices de proyectos configuradas.\n")
    lines.append("- Dar contexto rapido antes de responder dudas, modificar codigo, levantar servicios o revisar errores.\n")
    lines.append("- Mantener el grafo mental limpio, con nombres neutrales y sin etiquetas del asistente en titulos visibles.\n")
    lines.append("- Guardar decisiones, arquitectura, comandos y relaciones entre proyectos sin almacenar secretos.\n\n")
    lines.append("- Mantener una biblioteca multimedia navegable para documentos, logos, imagenes, audios, videos, fuentes y referencias reutilizables.\n\n")
    lines.append("- Mantener un inventario de [[../Skills/Skills|Skills]] separado por IA para elegir capacidades instaladas segun la tarea.\n\n")
    lines.append("## Como usar en un chat nuevo\n")
    lines.append("- Pedir: `usa la memoria de proyectos` o `usa project-memory`.\n")
    lines.append("- El asistente debe leer primero [[Inicio Memoria]], luego [[README - Memoria]], [[Mapa de Proyectos]] y la nota del proyecto relacionado.\n")
    lines.append("- Si el proyecto no es claro, buscar por familia: Contraloria, Core Signature, USAC Editorial, RENAP, TEC InfoApp, Store, Softplus, CRM o SaaS Alcore.\n")
    lines.append("- Para dudas historicas, cruzar con [[Contexto de Chats]], pero confirmar siempre en archivos locales antes de cambiar comportamiento.\n\n")
    lines.append("## Reglas operativas confirmadas\n")
    lines.append("- Antes de editar un repo, ejecutar `git status --short`.\n")
    lines.append("- Los cambios locales se consideran del usuario; no revertirlos ni pisarlos sin instruccion explicita.\n")
    lines.append("- El bloque manual de cada nota se preserva entre refrescos usando marcadores `memoria-manual-start` y `memoria-manual-end`.\n")
    lines.append("- No guardar secretos ni valores reales de `.env`; solo nombres de variables, comandos locales y metadatos tecnicos.\n")
    lines.append("- El sistema de refresco vive en `.memoria-system/` dentro del baul y se excluye del grafo visible para evitar ruido y ciclos.\n")
    lines.append("- Las notas visibles deben evitar nombres con la marca del asistente; usar nombres como `Memoria`, `Inicio Memoria` y `Contexto de Chats`.\n\n")
    lines.append("## Captura continua durante el trabajo\n")
    lines.append("- Cuando se resuelva algo efectivo, registrar el aprendizaje con `memoria registrar`.\n")
    lines.append("- Registrar cambios de arquitectura, decisiones, bugfixes, validaciones, rutas importantes, paginas entendidas y relaciones frontend/backend confirmadas.\n")
    lines.append("- Registrar solo contexto reutilizable; no guardar ruido, logs largos ni conversaciones completas.\n")
    lines.append("- Cada registro crea una nota en [[../Bitacora/Registro de Trabajo|Registro de Trabajo]] y agrega un enlace en la nota del proyecto.\n\n")
    lines.append("## Multimedia\n")
    lines.append("- Guardar activos en [[../Multimedia/Multimedia|Multimedia]] usando la estructura `Biblioteca/Proyectos`, `Biblioteca/Marcas` o `Biblioteca/General`.\n")
    lines.append("- Los activos soportados generan notas en `Multimedia/Activos` para que Graphify y las IA puedan encontrarlos por marca, proyecto, tipo y archivo.\n")
    lines.append("- Despues de agregar logos, audios, documentos o referencias visuales, correr el refresco completo para actualizar el grafo.\n\n")
    lines.append("## Skills\n")
    lines.append("- Consultar [[../Skills/Skills|Skills]] cuando el usuario pida usar capacidades disponibles o cuando la tarea pueda beneficiarse de una skill especializada.\n")
    lines.append("- Las skills se separan por [[../Skills/Codex Skills|Codex]], [[../Skills/Claude Skills|Claude]] y [[../Skills/Antigravity Skills|Antigravity]], con comparativa en [[../Skills/Comparativa Skills por IA|Comparativa Skills por IA]].\n")
    lines.append("- Si una skill aplica a la solicitud, leer su `SKILL.md` real antes de actuar.\n\n")
    lines.append("## Mantenimiento\n")
    lines.append("- Refrescar con:\n\n")
    lines.append("```bash\nmemoria refresh\n```\n\n")
    lines.append("- Registrar aprendizaje:\n\n")
    lines.append("```bash\nmemoria registrar core-strapi --tipo aprendizaje --titulo 'Flujo de permisos' --texto 'Resumen reutilizable...' --archivo src/App.tsx --validacion 'npm run build'\n```\n\n")
    lines.append("- Hay una automatizacion semanal activa los lunes a las 8:00 para refrescar la memoria y reportar cambios.\n")
    lines.append("- Si el grafo muestra nodos viejos, recargar el vault o cerrar y abrir Obsidian para limpiar cache visual.\n\n")
    lines.append("## Estado conocido del ultimo barrido\n")
    if dirty:
        for project in dirty:
            lines.append(f"- [[{project['name']}]] tiene {len(project['dirty'])} cambio(s) local(es).\n")
    else:
        lines.append("- No se detectaron cambios locales.\n")
    lines.append("\n## Alcance actual\n")
    lines.append("- La memoria cubre carpetas directas de la raiz principal y repos Git, apps o grafos en las raices adicionales configuradas.\n")
    lines.append("- Incluye indices de stack, comandos, Docker, puertos, variables de ejemplo, rutas, endpoints, servicios, vistas, componentes y content-types cuando se detectan.\n")
    lines.append("- El contexto de chats se guarda como pistas cortas filtradas; no reemplaza la verificacion en codigo.\n")
    return "".join(lines)


def dependency_edges(projects: list[dict]) -> list[tuple[str, str, str]]:
    by_name = {p["name"]: p for p in projects}
    edges: set[tuple[str, str, str]] = set()
    for project in projects:
        name = project["name"]
        fam = project["family"]
        if project["role"] == "frontend":
            for other in projects:
                if other["name"] == name or other["family"] != fam:
                    continue
                if other["role"] in {"backend/api", "cms/backend"}:
                    edges.add((name, other["name"], "familia frontend-backend"))
        if "balanceador" in name:
            for other in projects:
                if other["name"] != name and other["family"] == fam:
                    edges.add((name, other["name"], "infra"))

        endpoint_blob = "\n".join(project["endpoints"]).lower()
        for other_name in by_name:
            if other_name == name:
                continue
            tokens = {other_name.lower(), other_name.lower().replace("-", "_"), other_name.lower().replace("-", "")}
            if any(token and token in endpoint_blob for token in tokens):
                edges.add((name, other_name, "referencia en endpoints"))
    return sorted(edges)


def render_dependency_map(projects: list[dict]) -> str:
    lines = ["# Mapa de Dependencias\n\n"]
    lines.append("Relaciones inferidas entre proyectos. Confirmar en codigo y configuracion antes de usarlas para despliegue.\n\n")
    edges = dependency_edges(projects)
    lines.append("## Diagrama\n\n")
    lines.append("```mermaid\ngraph LR\n")
    if edges:
        for source, target, reason in edges:
            s = source.replace("-", "_").replace("/", "_")
            t = target.replace("-", "_").replace("/", "_")
            lines.append(f'  {s}["{source}"] -->|"{reason}"| {t}["{target}"]\n')
    else:
        lines.append('  SinRelaciones["Sin relaciones inferidas"]\n')
    lines.append("```\n\n")
    lines.append("## Tabla\n")
    lines.append("| Origen | Destino | Motivo |\n|---|---|---|\n")
    for source, target, reason in edges:
        lines.append(f"| [[{source}]] | [[{target}]] | {reason} |\n")
    if not edges:
        lines.append("| - | - | No se infirieron relaciones |\n")
    return "".join(lines)


def health_findings(projects: list[dict]) -> list[tuple[str, str, str, str]]:
    findings: list[tuple[str, str, str, str]] = []
    for project in projects:
        name = project["name"]
        if project["dirty"]:
            findings.append(("Atencion", name, "Cambios locales", f"{len(project['dirty'])} cambio(s) local(es)."))
        if project["is_git"] and not project["remote"]:
            findings.append(("Medio", name, "Remoto faltante", "No se detecto remoto origin."))
        if project["is_git"] and not project["branch"]:
            findings.append(("Medio", name, "Rama faltante", "No se detecto rama activa."))
        if not project["summary"]:
            findings.append(("Bajo", name, "Descripcion faltante", "No se detecto descripcion desde README."))
        if project["deps"] and not project["scripts"].get("build"):
            findings.append(("Medio", name, "Build no documentado", "No hay script `build` en package.json."))
        if project["deps"] and not (project["scripts"].get("test") or project["scripts"].get("test:app")):
            findings.append(("Bajo", name, "Tests no documentados", "No hay script de test claro."))
        if "Strapi" in project["signals"] and not project["env_keys"]:
            findings.append(("Medio", name, "Entorno no documentado", "Proyecto Strapi sin variables en .env.example detectadas."))
        if not project["is_git"]:
            findings.append(("Medio", name, "Sin Git directo", "Carpeta de app sin `.git` directo. Confirmar si es copia o subproyecto."))
    return findings


def render_health_report(projects: list[dict]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    findings = health_findings(projects)
    lines = ["# Reporte de Salud\n\n"]
    lines.append(f"Actualizado: {now} America/Guatemala\n\n")
    lines.append("## Resumen\n")
    lines.append(f"- Proyectos inventariados: {len(projects)}\n")
    lines.append(f"- Hallazgos: {len(findings)}\n")
    lines.append(f"- Con cambios locales: {sum(1 for p in projects if p['dirty'])}\n")
    lines.append(f"- Sin Git directo: {sum(1 for p in projects if not p['is_git'])}\n\n")
    lines.append("## Hallazgos\n")
    lines.append("| Severidad | Proyecto | Categoria | Detalle |\n|---|---|---|---|\n")
    for severity, project, category, detail in findings:
        lines.append(f"| {severity} | [[{project}]] | {category} | {detail} |\n")
    if not findings:
        lines.append("| - | - | - | Sin hallazgos |\n")
    return "".join(lines)


def render_environment_inventory(projects: list[dict]) -> str:
    lines = ["# Inventario de Ambientes\n\n"]
    lines.append("Inventario no sensible de variables, puertos y archivos de entorno detectados.\n\n")
    lines.append("| Proyecto | Puertos | Variables de ejemplo | Docker |\n|---|---|---|---|\n")
    for project in projects:
        ports = ", ".join(f"`{x}`" for x in project["ports"]) or "No detectados"
        envs = ", ".join(f"`{x}`" for x in project["env_keys"][:30]) or "No detectadas"
        docker = ", ".join(f"`{x}`" for x in project["docker"]) or "No detectado"
        lines.append(f"| [[{project['name']}]] | {ports} | {envs} | {docker} |\n")
    lines.append("\n## Regla\n")
    lines.append("- No guardar valores reales de secretos. Solo nombres de variables, puertos, comandos y rutas no sensibles.\n")
    return "".join(lines)


def infer_asset_owner(path: Path, projects: list[dict]) -> tuple[str, str]:
    rel = path.relative_to(MULTIMEDIA_LIBRARY)
    parts = rel.parts
    project_names = {p["name"].casefold(): p["name"] for p in projects}
    if len(parts) >= 2:
        folder = parts[0]
        if folder.casefold() in project_names:
            return "proyecto", project_names[folder.casefold()]
        if folder.casefold() in {"marcas", "marca", "clientes", "cliente"} and len(parts) >= 3:
            return "marca", parts[1]
        if folder.casefold() in {"proyectos", "proyecto"} and len(parts) >= 3:
            return "proyecto", parts[1]
    return "biblioteca", parts[0] if len(parts) > 1 else "General"


def collect_multimedia_assets(projects: list[dict]) -> list[dict]:
    MULTIMEDIA_LIBRARY.mkdir(parents=True, exist_ok=True)
    MULTIMEDIA_GENERATED.mkdir(parents=True, exist_ok=True)
    assets: list[dict] = []
    for path in sorted(MULTIMEDIA_LIBRARY.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in MULTIMEDIA_EXTENSIONS:
            continue
        owner_type, owner = infer_asset_owner(path, projects)
        rel = path.relative_to(MULTIMEDIA_ROOT)
        stat = path.stat()
        asset = {
            "name": path.stem,
            "filename": path.name,
            "path": str(path),
            "relative_path": rel.as_posix(),
            "kind": MULTIMEDIA_EXTENSIONS[path.suffix.lower()],
            "extension": path.suffix.lower(),
            "owner_type": owner_type,
            "owner": owner,
            "size_bytes": stat.st_size,
            "modified": dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        }
        asset["note_name"] = asset_note_name(asset)
        assets.append(asset)
    return assets


def asset_note_name(asset: dict) -> str:
    owner = re.sub(r"[^\w\s-]", "", asset["owner"], flags=re.UNICODE).strip() or "General"
    stem = re.sub(r"[^\w\s-]", "", asset["name"], flags=re.UNICODE).strip() or "activo"
    return f"{owner} - {stem}"


def render_asset_note(asset: dict) -> str:
    path = Path(asset["path"])
    embed = path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp3", ".wav", ".m4a", ".mp4", ".mov", ".webm", ".pdf"}
    link_prefix = "!" if embed else ""
    owner_link = f"[[{asset['owner']}]]" if asset["owner_type"] in {"proyecto", "marca"} else asset["owner"]
    lines = [
        "---\n",
        "tipo: activo-multimedia\n",
        f"asset_kind: {asset['kind']}\n",
        f"owner_type: {asset['owner_type']}\n",
        f"owner: {asset['owner']}\n",
        f"extension: {asset['extension']}\n",
        "estado: disponible\n",
        "tags:\n",
        "  - multimedia\n",
        f"  - {asset['kind'].replace('/', '-')}\n",
        "---\n\n",
        f"# {asset['name']}\n\n",
        "## Archivo\n",
        f"- Archivo: `{asset['filename']}`\n",
        f"- Ruta en vault: `{asset['relative_path']}`\n",
        f"- Tipo: {asset['kind']}\n",
        f"- Extension: `{asset['extension']}`\n",
        f"- Tamano: {asset['size_bytes']} bytes\n",
        f"- Modificado: {asset['modified']}\n",
        f"- Relacion: {owner_link}\n\n",
        "## Vista / enlace\n",
        f"- {link_prefix}[[../{asset['relative_path']}|{asset['filename']}]]\n\n",
        "## Uso recomendado\n",
        "- Definir uso: logo, audio, referencia visual, documento comercial, fuente, video, entregable, mockup o material de pauta.\n",
        "- Confirmar derechos de uso antes de publicar externamente.\n",
        "- No guardar secretos, credenciales ni documentos sensibles sin una politica explicita.\n",
    ]
    return "".join(lines)


def render_multimedia_index(assets: list[dict]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    by_owner: dict[str, list[dict]] = defaultdict(list)
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for asset in assets:
        by_owner[f"{asset['owner_type']}:{asset['owner']}"].append(asset)
        by_kind[asset["kind"]].append(asset)

    lines = ["# Multimedia\n\n"]
    lines.append("Biblioteca operativa de documentos, imagenes, logos, audios, videos y fuentes para proyectos, marcas y marketing.\n\n")
    lines.append(f"Actualizado: {now} America/Guatemala\n\n")
    lines.append("## Como guardar activos\n")
    lines.append("- Proyectos: `Multimedia/Biblioteca/Proyectos/<nombre-proyecto>/<tipo>/archivo.ext`\n")
    lines.append("- Marcas/clientes: `Multimedia/Biblioteca/Marcas/<nombre-marca>/<tipo>/archivo.ext`\n")
    lines.append("- General: `Multimedia/Biblioteca/General/<tipo>/archivo.ext`\n")
    lines.append("- Despues de agregar archivos, correr `memoria refresh-grafo`.\n\n")
    lines.append("## Uso por IA y Graphify\n")
    lines.append("- Cada archivo soportado genera una nota en [[Activos]] con ruta, tipo y relacion.\n")
    lines.append("- Las notas son legibles por Graphify y quedan enlazadas a proyectos o marcas cuando la ruta lo permite.\n")
    lines.append("- Para buscar desde terminal: `multimedia buscar logo`.\n\n")
    lines.append("## Resumen\n")
    lines.append(f"- Activos detectados: {len(assets)}\n")
    for kind, items in sorted(by_kind.items()):
        lines.append(f"- {kind}: {len(items)}\n")

    lines.append("\n## Por propietario\n")
    if by_owner:
        for owner_key, items in sorted(by_owner.items()):
            owner_type, owner = owner_key.split(":", 1)
            lines.append(f"\n### {owner} ({owner_type})\n")
            for asset in sorted(items, key=lambda item: (item["kind"], item["filename"])):
                lines.append(f"- [[Activos/{asset['note_name']}|{asset['filename']}]] - {asset['kind']}\n")
    else:
        lines.append("- Sin activos detectados todavia.\n")

    lines.append("\n## Plantillas\n")
    lines.append("- [[../Templates/Activo Multimedia|Activo Multimedia]]\n")
    return "".join(lines)


def render_multimedia_runbook() -> str:
    return """# Runbook - Multimedia

## Objetivo
Mantener una biblioteca reusable de activos para proyectos, marcas, campanas y piezas de marketing, disponible para Obsidian, IA y Graphify.

## Estructura
- `Multimedia/Biblioteca/Proyectos/<proyecto>/<tipo>/archivo.ext`
- `Multimedia/Biblioteca/Marcas/<marca>/<tipo>/archivo.ext`
- `Multimedia/Biblioteca/General/<tipo>/archivo.ext`

## Tipos recomendados
- `logos`
- `imagenes`
- `audios`
- `videos`
- `documentos`
- `presentaciones`
- `fuentes`
- `referencias`
- `entregables`

## Flujo
1. Guardar el archivo en la carpeta correcta.
2. Usar nombres descriptivos, sin secretos ni datos sensibles.
3. Correr el refresco:

```bash
memoria refresh-grafo
```

4. Buscar desde Graphify u Obsidian:

```bash
graphify query "que logos tenemos para Campuslands"
multimedia buscar logo
```

## Reglas
- No guardar credenciales, llaves privadas, tokens ni dumps sensibles.
- Confirmar derechos de uso antes de publicar activos de terceros.
- Si un activo define identidad de marca, enlazarlo desde la nota de marca o proyecto.
"""


def render_asset_template() -> str:
    return """---
tipo: activo-multimedia
asset_kind: imagen / logo-vector / audio / video / documento / fuente / presentacion / diseno
owner_type: proyecto / marca / biblioteca
owner: nombre
estado: disponible / revisar / archivado
tags:
  - multimedia
---

# Nombre del activo

## Archivo
- Archivo:
- Ruta en vault:
- Tipo:
- Formato:
- Version:
- Fuente/origen:

## Uso
- Uso principal:
- Puede usarse en:
- No usar en:
- Derechos/licencia:

## Relacionado
- Proyecto:
- Marca/cliente:
- Campana:
"""


def clean_frontmatter_value(value: str) -> str:
    value = value.strip().strip('"').strip("'")
    return value


def parse_skill_frontmatter(path: Path) -> dict:
    text = read_text(path, 80_000)
    meta: dict[str, str] = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            lines = text[3:end].strip().splitlines()
            idx = 0
            while idx < len(lines):
                line = lines[idx]
                if ":" not in line or line.startswith((" ", "\t", "-")):
                    idx += 1
                    continue
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if value in {">", ">-", "|", "|-"}:
                    idx += 1
                    parts: list[str] = []
                    while idx < len(lines) and (lines[idx].startswith((" ", "\t")) or not lines[idx].strip()):
                        parts.append(lines[idx].strip())
                        idx += 1
                    meta[key] = clean_frontmatter_value(" ".join(part for part in parts if part))
                    continue
                meta[key] = clean_frontmatter_value(value)
                idx += 1
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line.lstrip("#").strip()
            break
    return {
        "name": meta.get("name") or path.parent.name,
        "description": meta.get("description") or meta.get("short-description") or "",
        "title": title,
    }


def skill_category(name: str, description: str) -> str:
    haystack = f"{name} {description}".lower()
    if "security" in name or any(token in haystack for token in ("security-audit", "vulnerability review", "pentest", "pen-test", "vulnerabilidad")):
        return "Ciberseguridad y auditoría"
    if name.startswith("n8n"):
        return "Automatizacion e integraciones"
    if any(token in haystack for token in ("remotion", "higgsfield", "imagegen", "video", "image generation")):
        return "Video e imagen"
    if any(token in haystack for token in ("stripe", "cloudflare", "vercel", "nodejs", "postgres", "supabase", "docker", "haproxy", "strapi")):
        return "Backend e infraestructura"
    for category, keywords in SKILL_CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category
    return "General"


def skill_note_name(ai_name: str, skill_name: str) -> str:
    cleaned = re.sub(r"[^\w\s.-]", "", skill_name, flags=re.UNICODE).strip()
    cleaned = re.sub(r"\s+", "-", cleaned)
    return f"{ai_name} - {cleaned or 'skill'}"


def collect_ai_skills() -> list[dict]:
    rows: list[dict] = []
    for ai_name, root in SKILL_SOURCES.items():
        grouped: dict[str, dict] = {}
        try:
            skill_paths = list(root.rglob("SKILL.md", recurse_symlinks=True))
        except TypeError:
            skill_paths = [Path(dp) / "SKILL.md" for dp, _, fns in os.walk(root, followlinks=True) if "SKILL.md" in fns]
        for path in sorted(skill_paths):
            parsed = parse_skill_frontmatter(path)
            name = parsed["name"]
            key = name.casefold()
            rel_path = path.relative_to(root).as_posix()
            if key not in grouped:
                grouped[key] = {
                    "ai": ai_name,
                    "name": name,
                    "title": parsed["title"],
                    "description": parsed["description"],
                    "category": skill_category(name, parsed["description"]),
                    "paths": [],
                    "primary_path": str(path),
                    "relative_paths": [],
                    "note_name": skill_note_name(ai_name, name),
                }
            grouped[key]["paths"].append(str(path))
            grouped[key]["relative_paths"].append(rel_path)
            if len(rel_path.split("/")) < len(Path(grouped[key]["primary_path"]).relative_to(root).parts):
                grouped[key]["primary_path"] = str(path)
            if parsed["description"] and not grouped[key]["description"]:
                grouped[key]["description"] = parsed["description"]
        rows.extend(grouped.values())
    return sorted(rows, key=lambda item: (item["ai"], item["category"], item["name"].casefold()))


def skills_by_ai(skills: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for skill in skills:
        grouped[skill["ai"]].append(skill)
    return grouped


def skill_availability(skills: list[dict]) -> dict[str, set[str]]:
    available: dict[str, set[str]] = defaultdict(set)
    for skill in skills:
        available[skill["name"]].add(skill["ai"])
    return available


def render_skills_index(skills: list[dict]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    grouped = skills_by_ai(skills)
    by_category: dict[str, list[dict]] = defaultdict(list)
    for skill in skills:
        by_category[skill["category"]].append(skill)
    lines = ["# Skills\n\n"]
    lines.append("Inventario operativo de skills instaladas por IA para decidir que capacidad usar en cada interaccion.\n\n")
    lines.append(f"Actualizado: {now} America/Guatemala\n\n")
    lines.append("## Paneles\n")
    lines.append("- [[Codex Skills]]\n")
    lines.append("- [[Claude Skills]]\n")
    lines.append("- [[Antigravity Skills]]\n")
    lines.append("- [[Comparativa Skills por IA]]\n")
    lines.append("- [[Skills Router]]\n\n")
    lines.append("## Resumen\n")
    lines.append(f"- Total instalaciones consolidadas: {len(skills)}\n")
    for ai_name in sorted(grouped):
        lines.append(f"- {ai_name}: {len(grouped[ai_name])} skill(s)\n")
    lines.append("\n## Uso operativo\n")
    lines.append("- Antes de pedir una capacidad especial, consultar este panel o buscar con Graphify.\n")
    lines.append("- Si una tarea coincide con una skill disponible para la IA activa, usar esa skill antes de razonamiento generico.\n")
    lines.append("- Si una skill existe solo en otra IA, usar esta nota para decidir si conviene mover, sincronizar o delegar.\n\n")
    lines.append("## Recomendacion rapida\n")
    lines.append("```bash\n")
    lines.append("skills recomendar 'crear campaña con landing y anuncios'\n")
    lines.append("```\n\n")
    lines.append("## Categorias\n")
    for category in sorted(by_category):
        lines.append(f"\n### {category}\n")
        seen: set[str] = set()
        for skill in sorted(by_category[category], key=lambda item: item["name"].casefold()):
            if skill["name"] in seen:
                continue
            seen.add(skill["name"])
            ais = ", ".join(sorted(skill_availability(skills)[skill["name"]]))
            lines.append(f"- `{skill['name']}` - {ais}\n")
    return "".join(lines)


def render_skills_router(skills: list[dict]) -> str:
    availability = skill_availability(skills)
    lines = ["# Skills Router\n\n"]
    lines.append("Reglas operativas para elegir skills segun la intencion del usuario y la IA activa.\n\n")
    lines.append("## Regla principal\n")
    lines.append("1. Interpretar la solicitud del usuario.\n")
    lines.append("2. Buscar skills candidatas en este router, en [[Skills]] o con la CLI.\n")
    lines.append("3. Si la skill existe para la IA activa, leer su `SKILL.md` real antes de actuar.\n")
    lines.append("4. Si existe solo en otra IA, usar la comparativa para decidir si se sincroniza, delega o se trabaja con alternativa local.\n\n")
    lines.append("## CLI\n")
    lines.append("```bash\n")
    lines.append("skills recomendar 'necesito un workflow n8n con webhook y validacion'\n")
    lines.append("skills buscar marketing --ia Codex\n")
    lines.append("skills comparar brand-identity\n")
    lines.append("```\n\n")
    lines.append("## Rutas por intencion\n")
    for rule in SKILL_ROUTER_RULES:
        lines.append(f"\n### {rule['intent']}\n")
        lines.append(f"- Disparadores: {rule['triggers']}\n")
        lines.append("- Skills candidatas:\n")
        for skill_name in rule["skills"]:
            ais = sorted(availability.get(skill_name, set()))
            ai_label = ", ".join(ais) if ais else "no detectada"
            lines.append(f"  - `{skill_name}` - {ai_label}\n")
    return "".join(lines)


def render_ai_skills(ai_name: str, skills: list[dict]) -> str:
    rows = [skill for skill in skills if skill["ai"] == ai_name]
    by_category: dict[str, list[dict]] = defaultdict(list)
    for skill in rows:
        by_category[skill["category"]].append(skill)
    lines = [f"# {ai_name} Skills\n\n"]
    lines.append(f"Skills disponibles para {ai_name} desde `{SKILL_SOURCES[ai_name]}`.\n\n")
    lines.append(f"- Total: {len(rows)}\n")
    lines.append("- Indice general: [[Skills]]\n")
    lines.append("- Comparativa: [[Comparativa Skills por IA]]\n\n")
    for category in sorted(by_category):
        lines.append(f"## {category}\n")
        for skill in sorted(by_category[category], key=lambda item: item["name"].casefold()):
            lines.append(f"- [[{skill['note_name']}|{skill['name']}]]")
            if skill["description"]:
                lines.append(f": {skill['description'][:220]}")
            lines.append("\n")
        lines.append("\n")
    return "".join(lines)


def render_skills_comparison(skills: list[dict]) -> str:
    availability = skill_availability(skills)
    by_name: dict[str, list[dict]] = defaultdict(list)
    for skill in skills:
        by_name[skill["name"]].append(skill)
    lines = ["# Comparativa Skills por IA\n\n"]
    lines.append("Vista para saber que IA tiene cada skill instalada.\n\n")
    lines.append("| Skill | Codex | Claude | Antigravity | Categoria | Descripcion |\n")
    lines.append("|---|---:|---:|---:|---|---|\n")
    for name in sorted(by_name, key=str.casefold):
        first = sorted(by_name[name], key=lambda item: item["ai"])[0]
        codex = "si" if "Codex" in availability[name] else "no"
        claude = "si" if "Claude" in availability[name] else "no"
        antigravity = "si" if "Antigravity" in availability[name] else "no"
        lines.append(
            f"| `{md_cell(name)}` | {codex} | {claude} | {antigravity} | {md_cell(first['category'])} | {md_cell(first.get('description', '')[:180])} |\n"
        )
    return "".join(lines)


def render_skill_note(skill: dict, availability: dict[str, set[str]]) -> str:
    other_ais = sorted(availability[skill["name"]] - {skill["ai"]})
    lines = [
        "---\n",
        "tipo: skill\n",
        f"ia: {skill['ai']}\n",
        f"skill: {skill['name']}\n",
        f"categoria: {skill['category']}\n",
        "estado: instalada\n",
        "tags:\n",
        "  - skills\n",
        f"  - {skill['ai'].lower()}\n",
        "---\n\n",
        f"# {skill['name']}\n\n",
        f"- IA: [[{skill['ai']} Skills]]\n",
        f"- Categoria: {skill['category']}\n",
        f"- Ruta principal: `{skill['primary_path']}`\n",
    ]
    if other_ais:
        lines.append("- Tambien disponible en: " + ", ".join(f"[[{ai} Skills]]" for ai in other_ais) + "\n")
    if skill["description"]:
        lines.append(f"- Descripcion: {skill['description']}\n")
    lines.append("\n## Instalaciones detectadas\n")
    for path in skill["paths"]:
        lines.append(f"- `{path}`\n")
    lines.append("\n## Uso\n")
    lines.append("- Usar cuando la solicitud del usuario coincida con la descripcion o categoria de esta skill.\n")
    lines.append("- Leer primero el `SKILL.md` real antes de aplicar instrucciones especificas.\n")
    return "".join(lines)


def render_conventions() -> str:
    return """# Convenciones de Desarrollo

## Reglas de trabajo
- Revisar estado local antes de editar.
- No revertir cambios locales sin instruccion explicita.
- Preferir patrones existentes del repo antes de crear abstracciones nuevas.
- Verificar con comandos reales del proyecto: build, lint, test o prueba manual segun aplique.
- Documentar decisiones confirmadas en la nota del proyecto o en una nota de Decision.

## Memoria
- Mantener titulos neutrales para conservar limpio el grafo.
- Guardar contexto operativo, no conversaciones completas.
- No guardar secretos.
- Mantener el script de refresco fuera del vault.
"""


def render_deploy_checklist() -> str:
    return """# Checklist de Despliegue

## Antes
- Confirmar proyecto y ambiente.
- Revisar `git status --short`.
- Confirmar rama y ultimo commit.
- Revisar variables requeridas sin exponer secretos.
- Ejecutar build/lint/test disponible.

## Durante
- Registrar comando usado.
- Validar logs.
- Validar endpoint o pantalla principal.
- Revisar errores de consola o backend.

## Despues
- Registrar resultado.
- Registrar rollback disponible.
- Actualizar decision o incidente si aplica.
"""


def render_client_domains() -> str:
    return """# Clientes y Dominios

Registrar aqui dominios, tenants, clientes, ambientes y relaciones comerciales no sensibles.

## Regla
- No guardar credenciales ni tokens.
- Si un dominio apunta a un proyecto, enlazar la nota del proyecto.
"""


def render_corporate_index() -> str:
    return """# Indice Corporativo

## Operacion
- [[../Proyectos Git/Inicio Memoria|Inicio Memoria]]
- [[../Proyectos Git/Contexto Operativo|Contexto Operativo]]
- [[../Reportes/Reporte de Salud|Reporte de Salud]]
- [[../Reportes/Validacion Sistema de Memoria|Validacion Sistema de Memoria]]
- [[../Bitacora/Registro de Trabajo|Registro de Trabajo]]
- [[../Ambientes/Inventario de Ambientes|Inventario de Ambientes]]
- [[../Multimedia/Multimedia|Multimedia]]
- [[../Skills/Skills|Skills]]

## Arquitectura
- [[Mapa de Dependencias]]
- [[../Proyectos Git/Mapa de Proyectos|Mapa de Proyectos]]
- [[../Proyectos Git/Indice Tecnico Profundo|Indice Tecnico Profundo]]

## Gobierno tecnico
- [[../Convenciones/Convenciones de Desarrollo|Convenciones de Desarrollo]]
- [[../Checklists/Checklist de Despliegue|Checklist de Despliegue]]
- [[../Clientes Dominios/Clientes y Dominios|Clientes y Dominios]]

## Registros
- [[../Decisiones/Registro de Decisiones|Registro de Decisiones]]
- [[../Incidentes/Registro de Incidentes|Registro de Incidentes]]
"""


def render_decision_register() -> str:
    return """# Registro de Decisiones

Usar una nota por decision cuando sea importante para arquitectura, negocio, despliegue o mantenimiento.

## Pendientes
- Crear decisiones confirmadas usando la plantilla [[../Templates/Decision Tecnica|Decision Tecnica]].
"""


def render_incident_register() -> str:
    return """# Registro de Incidentes

Usar una nota por incidente cuando haya fallos de build, despliegue, datos, permisos o disponibilidad.

## Pendientes
- Registrar incidentes relevantes usando la plantilla [[../Templates/Bugfix|Bugfix]] o una nota especifica de incidente.
"""


def ensure_worklog_register() -> None:
    path = SECTION_DIRS["bitacora"] / "Registro de Trabajo.md"
    if not path.exists():
        write(
            path,
            "# Registro de Trabajo\n\n"
            "Bitacora de aprendizajes, cambios efectivos, decisiones y validaciones capturadas durante el trabajo.\n\n"
            "## Entradas\n",
        )


def render_runbook(project: dict) -> str:
    dev = project["scripts"].get("dev") or project["scripts"].get("start") or ""
    build = project["scripts"].get("build") or ""
    test = project["scripts"].get("test") or project["scripts"].get("test:app") or ""
    lint = project["scripts"].get("lint") or ""
    lines = [metadata(project, "runbook", "operacion"), f"# Runbook - {project['name']}\n\n"]
    lines.append(f"- Proyecto: [[{project['name']}]]\n")
    lines.append(f"- Ruta: `{project['path']}`\n")
    lines.append(f"- Rol: {project['role']}\n")
    lines.append(f"- Stack: {', '.join(project['signals']) or 'Por confirmar'}\n\n")
    lines.append("## Antes de trabajar\n")
    lines.append("```bash\n")
    lines.append(f"cd '{project['path']}'\n")
    lines.append("git status --short\n")
    lines.append("```\n\n")
    lines.append("## Levantar local\n")
    if dev:
        lines.append("```bash\n")
        lines.append(f"cd '{project['path']}'\n")
        lines.append(f"npm run {'dev' if project['scripts'].get('dev') else 'start'}\n")
        lines.append("```\n")
    else:
        lines.append("- No hay comando local claro detectado. Revisar nota del proyecto.\n")
    if project["docker"]:
        lines.append("\n## Docker\n")
        lines.append("```bash\n")
        lines.append(f"cd '{project['path']}'\n")
        compose = next((x for x in project["docker"] if x.startswith("docker-compose")), "")
        if compose:
            lines.append(f"docker compose -f {compose} up -d\n")
        else:
            lines.append("docker build .\n")
        lines.append("```\n")
    lines.append("\n## Validacion\n")
    if lint:
        lines.append(f"- Lint: `npm run lint`\n")
    if test:
        lines.append(f"- Tests: `npm run {'test' if project['scripts'].get('test') else 'test:app'}`\n")
    if build:
        lines.append("- Build: `npm run build`\n")
    if not any([lint, test, build]):
        lines.append("- No se detectaron comandos de validacion. Confirmar manualmente.\n")
    lines.append("\n## Entorno no sensible\n")
    lines.append("- Puertos: " + (", ".join(f"`{x}`" for x in project["ports"]) if project["ports"] else "No detectados") + "\n")
    lines.append("- Variables: " + (", ".join(f"`{x}`" for x in project["env_keys"][:80]) if project["env_keys"] else "No detectadas") + "\n")
    lines.append("\n## Rollback\n")
    lines.append("- Confirmar commit previo y estrategia antes de produccion.\n")
    lines.append("- No ejecutar reset destructivo sin instruccion explicita.\n")
    return "".join(lines)


def render_chat_context(projects: list[dict]) -> str:
    names = [p["name"] for p in projects]
    index = CODEX_ROOT / "session_index.jsonl"
    rows = []
    if index.exists():
        for line in read_text(index, 2_000_000).splitlines():
            try:
                item = json.loads(line)
            except Exception:
                continue
            title = item.get("thread_name", "") or ""
            low = title.lower()
            hits: set[str] = set()
            for name in names:
                if name.lower() in low or name.lower().replace("-", " ") in low:
                    hits.add(name)
            if any(word in low for word in ("strapi", "cms", "shop", "purchase", "gps", "scanner", "tenant", "permiso", "landing", "bodega", "sucursal", "orden", "mail", "page builder")):
                if "core-strapi" in names:
                    hits.add("core-strapi")
            if any(word in low for word in ("contraloria", "menú", "menu")):
                if "contraloria-frontend" in names:
                    hits.add("contraloria-frontend")
            if hits:
                rows.append((item.get("updated_at", "")[:10], title, sorted(hits)))
    seen = set()
    unique = []
    for row in rows:
        key = (row[1], tuple(row[2]))
        if key not in seen:
            seen.add(key)
            unique.append(row)

    lines = ["# Contexto de Chats\n\n"]
    lines.append("Resumen acotado de sesiones locales detectadas. Sirve como pista, no como verdad final.\n\n")
    lines.append("| Fecha indice | Tema de sesion | Proyectos relacionados inferidos |\n")
    lines.append("|---|---|---|\n")
    for date, title, hits in unique[:160]:
        links = ", ".join(f"[[{hit}]]" for hit in hits)
        lines.append(f"| {md_cell(date)} | {md_cell(title)} | {links} |\n")
    if not unique:
        lines.append("| - | No se detectaron sesiones relacionadas por titulo | - |\n")
    lines.append("\n## Uso\n")
    lines.append("- Si una duda coincide con un tema de sesion, abrir la nota del proyecto y buscar en archivos locales antes de asumir.\n")
    lines.append("- Para memoria duradera, mover decisiones confirmadas a la nota del repo correspondiente.\n")
    snippets = archived_chat_snippets(projects)
    lines.append("\n## Menciones acotadas en sesiones archivadas\n")
    lines.append("Fragmentos cortos filtrados desde sesiones archivadas. No incluyen salidas de comandos completas.\n\n")
    lines.append("| Fecha archivo | Proyecto | Rol | Fragmento |\n")
    lines.append("|---|---|---|---|\n")
    if snippets:
        for date, project, role, snippet in snippets[:180]:
            lines.append(f"| {md_cell(date)} | [[{md_cell(project)}]] | {md_cell(role)} | {md_cell(snippet)} |\n")
    else:
        lines.append("| - | - | - | No se detectaron menciones utiles. |\n")
    return "".join(lines)


def archived_chat_snippets(projects: list[dict]) -> list[tuple[str, str, str, str]]:
    names = [p["name"] for p in projects]
    aliases: dict[str, list[str]] = {}
    for name in names:
        base = name.lower()
        aliases[name] = sorted({base, base.replace("-", " ")})
    thematic = {
        "core-strapi": ["strapi", "cms", "shop", "purchase", "gps", "scanner", "tenant", "bodega", "sucursal", "page builder"],
        "contraloria-frontend": ["contraloria", "menú", "menu", "mega menu", "niveles"],
        "softplus": ["softplus"],
    }

    rows: list[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    archive_dir = CODEX_ROOT / "archived_sessions"
    if not archive_dir.exists():
        return rows

    archive_files = sorted(archive_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:24]
    for path in archive_files:
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
        file_date = date_match.group(1) if date_match else ""
        line_count = 0
        try:
            handle = path.open(errors="ignore")
        except Exception:
            continue
        with handle:
            for line in handle:
                line_count += 1
                if line_count > 2500:
                    break
                if len(line) > 120_000:
                    continue
                try:
                    item = json.loads(line)
                except Exception:
                    continue
                payload = item.get("payload") or {}
                if payload.get("type") != "message":
                    continue
                role = payload.get("role", "")
                if role not in {"user", "assistant"}:
                    continue
                parts = []
                for content in payload.get("content") or []:
                    if isinstance(content, dict):
                        text = content.get("text") or ""
                        if text:
                            parts.append(text)
                text = "\n".join(parts).strip()
                if not text or text.startswith("<") or len(text) > 20_000:
                    continue
                low = text.lower()
                hit_projects: set[str] = set()
                for name, terms in aliases.items():
                    if any(term in low for term in terms):
                        hit_projects.add(name)
                for name, terms in thematic.items():
                    if name in names and any(term in low for term in terms):
                        hit_projects.add(name)
                if not hit_projects:
                    continue
                cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
                cleaned = re.sub(r"/Users/macbookpro/\.codex/\S+", "[ruta local]", cleaned)
                cleaned = cleaned.replace("Codex", "asistente").replace("codex", "asistente")
                cleaned = cleaned.replace("SKILL.md", "archivo de skill").replace("openai.yaml", "metadata")
                cleaned = re.sub(r"\s+", " ", cleaned)
                cleaned = cleaned.replace("```", "")
                if len(cleaned) > 260:
                    cleaned = cleaned[:257] + "..."
                for project in sorted(hit_projects):
                    key = (project, role, cleaned)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append((file_date, project, role, cleaned))
                    if len(rows) >= 220:
                        return rows
    return rows


def main() -> None:
    projects, nongit_other = collect_projects()
    integration_imports = sync_project_integrations()
    assets = collect_multimedia_assets(projects)
    skills = collect_ai_skills()
    availability = skill_availability(skills)
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
    SEGMENTED_PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
    for directory in SECTION_DIRS.values():
        directory.mkdir(parents=True, exist_ok=True)
    for directory in (
        MULTIMEDIA_LIBRARY / "Proyectos",
        MULTIMEDIA_LIBRARY / "Marcas",
        MULTIMEDIA_LIBRARY / "General",
        MULTIMEDIA_GENERATED,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    for stale in MULTIMEDIA_GENERATED.glob("*.md"):
        stale.unlink(missing_ok=True)
    for stale in SECTION_DIRS["skills"].glob("*.md"):
        stale.unlink(missing_ok=True)
    write(MEMORY_ROOT / "README - Memoria.md", render_readme(projects, nongit_other))
    write(MEMORY_ROOT / "Inicio Memoria.md", render_start_here(projects))
    write(MEMORY_ROOT / "Mapa de Proyectos.md", render_map(projects))
    write(MEMORY_ROOT / "Indice Tecnico Profundo.md", render_deep_index(projects))
    write(MEMORY_ROOT / "Contexto Operativo.md", render_operational_context(projects))
    write(MEMORY_ROOT / "Contexto de Chats.md", render_chat_context(projects))
    write(MEMORY_ROOT / "Pendientes de Memoria.md", render_pending(projects))
    write(SECTION_DIRS["arquitectura"] / "Indice Corporativo.md", render_corporate_index())
    write(SECTION_DIRS["arquitectura"] / "Mapa de Dependencias.md", render_dependency_map(projects))
    write(SECTION_DIRS["ambientes"] / "Inventario de Ambientes.md", render_environment_inventory(projects))
    write(SECTION_DIRS["reportes"] / "Reporte de Salud.md", render_health_report(projects))
    write(SECTION_DIRS["reportes"] / "Cobertura PROYECTOS en Obsidian y Graphify.md", render_coverage_matrix(projects))
    write(SECTION_DIRS["convenciones"] / "Convenciones de Desarrollo.md", render_conventions())
    write(SECTION_DIRS["checklists"] / "Checklist de Despliegue.md", render_deploy_checklist())
    write(SECTION_DIRS["clientes"] / "Clientes y Dominios.md", render_client_domains())
    write(SECTION_DIRS["decisiones"] / "Registro de Decisiones.md", render_decision_register())
    write(SECTION_DIRS["incidentes"] / "Registro de Incidentes.md", render_incident_register())
    write(SECTION_DIRS["multimedia"] / "Multimedia.md", render_multimedia_index(assets))
    write(SECTION_DIRS["runbooks"] / "Multimedia.md", render_multimedia_runbook())
    write(SECTION_DIRS["templates"] / "Activo Multimedia.md", render_asset_template())
    for asset in assets:
        write(MULTIMEDIA_GENERATED / f"{asset['note_name']}.md", render_asset_note(asset))
    write(SECTION_DIRS["skills"] / "Skills.md", render_skills_index(skills))
    write(SECTION_DIRS["skills"] / "Codex Skills.md", render_ai_skills("Codex", skills))
    write(SECTION_DIRS["skills"] / "Claude Skills.md", render_ai_skills("Claude", skills))
    write(SECTION_DIRS["skills"] / "Antigravity Skills.md", render_ai_skills("Antigravity", skills))
    write(SECTION_DIRS["skills"] / "Comparativa Skills por IA.md", render_skills_comparison(skills))
    write(SECTION_DIRS["skills"] / "Skills Router.md", render_skills_router(skills))
    for skill in skills:
        write(SECTION_DIRS["skills"] / f"{skill['note_name']}.md", render_skill_note(skill, availability))
    ensure_worklog_register()
    for project in projects:
        project_dir = SEGMENTED_PROJECTS_ROOT / segmented_rel(project)
        if project_dir.exists():
            for stale in project_dir.glob("*.md"):
                stale.unlink(missing_ok=True)
        for filename, content in render_project_segments(project, projects).items():
            write(project_dir / filename, content)
        write(MEMORY_ROOT / f"{project['name']}.md", render_project_moc(project))
        write(SECTION_DIRS["runbooks"] / f"{project['name']}.md", render_runbook(project))
    segmented_index = ["# Indice de Proyectos Segmentados\n\n", "Navegacion modular por familia y proyecto.\n"]
    by_family: dict[str, list[dict]] = defaultdict(list)
    for project in projects:
        by_family[project["family"]].append(project)
    for family_name in sorted(by_family):
        segmented_index.append(f"\n## {family_name}\n")
        for project in sorted(by_family[family_name], key=lambda item: item["name"]):
            segmented_index.append(f"- [[{segmented_rel(project).as_posix()}/00 - Inicio|{project['name']}]]\n")
    write(SEGMENTED_PROJECTS_ROOT / "Indice de Proyectos Segmentados.md", "".join(segmented_index))
    index = {
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "projects_roots": ["$PROJECTS_ROOT", "$PROJECTS_ROOT_PLAYGROUND"],
        "vault_root": "$VAULT_ROOT/Memoria",
        "projects": projects,
        "multimedia_assets": assets,
        "ai_skills": skills,
        "health_findings": health_findings(projects),
        "dependency_edges": dependency_edges(projects),
        "nongit_other": nongit_other,
        "project_integration_imports": integration_imports,
    }
    write(INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2))
    print(f"Updated {len(projects) * 2 + len(assets) + len(skills) + 24} notes in {CORP_ROOT}")


if __name__ == "__main__":
    main()
