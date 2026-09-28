#!/usr/bin/env python3
"""Herramienta de mantenimiento del catalogo de skills de Agentic Marketing OS.

Solo usa la libreria estandar de Python 3.9+.

Subcomandos:
  list         Lista las skills (nombre, categoria, ruta). --paths imprime solo rutas.
  validate     Valida frontmatter, nombres unicos y ausencia de datos personales.
  openai-yaml  Crea agents/openai.yaml (Codex / ChatGPT) en las skills que no lo tienen.
  package      Genera dist/ con un .zip por skill (subir a ChatGPT o claude.ai),
               un zip con todo y un paquete de conocimiento para Proyectos de ChatGPT.
  marketplace  Regenera .claude-plugin/marketplace.json (plugins de Claude Code).
  catalog      Regenera docs/CATALOGO.md con todas las skills.

Ejemplos:
  python3 scripts/skills_tool.py validate
  python3 scripts/skills_tool.py package
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
DIST_ROOT = REPO_ROOT / "dist"

# Claves de frontmatter del estandar abierto Agent Skills (agentskills.io).
STANDARD_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# Claves que Claude Code entiende ademas del estandar. Se conservan en el repo y se
# quitan solo en los zips para ChatGPT / claude.ai.
CLAUDE_CODE_KEYS = {"user-invocable", "argument-hint", "disable-model-invocation", "model", "version", "when_to_use"}

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_SHORT_DESCRIPTION = 64
ZIP_WARN_BYTES = 25 * 1024 * 1024

# Patrones que nunca deben publicarse en un repo para alumnos.
PRIVACY_PATTERNS = [
    (re.compile(r"/(?:Users|home)/(?!tu_usuario|tu-usuario|usuario|user|runner|you|<)[A-Za-z0-9._-]+/"), "ruta absoluta de un usuario"),
    (re.compile(r"\b(?!(?:user|usuario|tu[._-]?correo|you|example|ejemplo)@)[A-Za-z0-9._%+-]+@(?:gmail|hotmail|outlook|yahoo|icloud)\.com"), "correo personal"),
    (re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}"), "posible API key de OpenAI"),
    (re.compile(r"\bsk_[a-f0-9]{32,}"), "posible API key de ElevenLabs"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"), "posible API key de Google"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), "posible token de GitHub"),
]
TEXT_SUFFIXES = {".md", ".txt", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".yaml", ".yml", ".sh", ".html", ".css", ".toml"}
IGNORED_PARTS = {"node_modules", "__pycache__", ".git", "dist", ".venv", ".venv-tools"}

# Plugins de Claude Code: nombre -> (descripcion, carpetas que contienen <skill>/SKILL.md)
PLUGIN_GROUPS = {
    "marketing": ("Estrategia, copywriting, pauta, email, contenido, Instagram y gestión de clientes.", ["skills/marketing"]),
    "seo-geo": ("SEO técnico y local, y GEO para aparecer en ChatGPT, Perplexity y Google AI Overviews.", ["skills/seo-geo"]),
    "research": ("Scraping web e inteligencia competitiva en redes sociales.", ["skills/research-intelligence"]),
    "design": ("Diseño web y UI/UX, sistemas de diseño, redes sociales, imágenes con IA y pulido visual.", ["skills/design-creative", "skills/design-creative/visual-polishers"]),
    "video-audio": ("Video programático (Remotion, HyperFrames), dirección con IA (Veo, Flow, Higgsfield) y audio (ElevenLabs).", [
        "skills/video-production/ai-directing",
        "skills/video-production/hyperframes",
        "skills/video-production/remotion",
        "skills/video-production/video-workflows",
        "skills/audio",
    ]),
    "browser": ("Navegador autónomo para agentes: capturas, formularios, QA y auditorías.", ["skills/browser-automation", "skills/browser-automation/agent-browser/specialized"]),
    "memory": ("Memoria continua con Obsidian y grafos de conocimiento con Graphify.", ["skills/memory"]),
}


@dataclass
class Skill:
    path: Path
    frontmatter: dict
    raw_frontmatter: str
    body: str

    @property
    def name(self) -> str:
        return str(self.frontmatter.get("name", "")).strip()

    @property
    def description(self) -> str:
        return str(self.frontmatter.get("description", "")).strip()

    @property
    def category(self) -> str:
        return self.path.relative_to(SKILLS_ROOT).parts[0]

    @property
    def rel(self) -> str:
        return self.path.relative_to(REPO_ROOT).as_posix()


# ---------------------------------------------------------------------------
# Lectura de frontmatter (subconjunto YAML suficiente para SKILL.md)
# ---------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not match:
        return "", text
    return match.group(1), match.group(2)


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        return inner.replace('\\"', '"') if value[0] == '"' else inner.replace("''", "'")
    return value


def parse_frontmatter(raw: str) -> dict:
    """Parsea claves de primer nivel, bloques | y >, y mapas anidados de un nivel."""
    data: dict = {}
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, rest = match.group(1), match.group(2)
        index += 1
        block: list[str] = []
        while index < len(lines) and (lines[index].startswith((" ", "\t")) or not lines[index].strip()):
            block.append(lines[index])
            index += 1
        if rest.strip() in {"|", ">", "|-", ">-", "|+", ">+"}:
            texts = [item.strip() for item in block]
            joiner = "\n" if rest.strip().startswith("|") else " "
            data[key] = joiner.join(t for t in texts if t).strip()
        elif rest.strip():
            value = rest
            # descripcion en varias lineas sin indicador de bloque
            continuation = [item.strip() for item in block if item.strip()]
            if continuation and not any(re.match(r"^[A-Za-z0-9_-]+:\s", c) for c in continuation):
                value = " ".join([rest.strip(), *continuation])
            data[key] = _unquote(value)
        else:
            nested: dict = {}
            for item in block:
                sub = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", item)
                if sub:
                    nested[sub.group(1)] = _unquote(sub.group(2))
            data[key] = nested
    return data


def load_skill(skill_md: Path) -> Skill:
    text = skill_md.read_text(encoding="utf-8")
    raw, body = split_frontmatter(text)
    return Skill(path=skill_md.parent, frontmatter=parse_frontmatter(raw), raw_frontmatter=raw, body=body)


def discover() -> list[Skill]:
    found = []
    for skill_md in sorted(SKILLS_ROOT.rglob("SKILL.md")):
        if any(part in IGNORED_PARTS for part in skill_md.parts):
            continue
        found.append(load_skill(skill_md))
    return found


def nested_skill_dirs(skill: Skill) -> set[Path]:
    """Subcarpetas de una skill que son skills independientes (se empaquetan aparte)."""
    return {md.parent for md in skill.path.rglob("SKILL.md") if md.parent != skill.path}


def skill_files(skill: Skill) -> list[Path]:
    nested = nested_skill_dirs(skill)
    files = []
    for path in sorted(skill.path.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.parts) or path.name == ".DS_Store":
            continue
        if any(parent in nested for parent in path.parents):
            continue
        files.append(path)
    return files


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def cmd_validate(args: argparse.Namespace) -> int:
    skills = discover()
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, str] = {}

    for skill in skills:
        where = skill.rel
        if not skill.raw_frontmatter:
            errors.append(f"{where}: SKILL.md sin frontmatter YAML")
            continue
        name, description = skill.name, skill.description
        if not name:
            errors.append(f"{where}: falta 'name'")
        elif not NAME_PATTERN.match(name) or len(name) > MAX_NAME:
            errors.append(f"{where}: 'name' invalido ({name}); usa minusculas y guiones, maximo {MAX_NAME}")
        elif name != skill.path.name:
            errors.append(f"{where}: 'name' ({name}) debe coincidir con la carpeta ({skill.path.name})")
        if name in seen:
            errors.append(f"{where}: nombre duplicado, ya usado en {seen[name]}")
        seen[name] = where
        if not description:
            errors.append(f"{where}: falta 'description'")
        elif len(description) > MAX_DESCRIPTION:
            errors.append(f"{where}: 'description' tiene {len(description)} caracteres (max {MAX_DESCRIPTION})")
        unknown = set(skill.frontmatter) - STANDARD_KEYS - CLAUDE_CODE_KEYS
        if unknown:
            warnings.append(f"{where}: claves no estandar {sorted(unknown)}")
        if not (skill.path / "agents" / "openai.yaml").exists():
            warnings.append(f"{where}: falta agents/openai.yaml (ejecuta: skills_tool.py openai-yaml)")

    scan_roots = [SKILLS_ROOT, REPO_ROOT / "engine", REPO_ROOT / "templates", REPO_ROOT / "scripts"]
    scan_files = [REPO_ROOT / name for name in ("README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md")]
    for root in scan_roots:
        scan_files.extend(p for p in root.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES)
    ignored_config = REPO_ROOT / "engine" / "memory" / "config" / "settings.json"
    for path in scan_files:
        if path == ignored_config or path == Path(__file__).resolve():
            continue
        if any(part in IGNORED_PARTS for part in path.parts) or not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern, label in PRIVACY_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(REPO_ROOT)}:{line}: {label}: {match.group(0)[:60]}")

    extra = [p.strip().lower() for p in (args.deny or []) if p.strip()]
    deny_file = REPO_ROOT / ".privacy-denylist"
    if deny_file.exists():
        extra += [line.strip().lower() for line in deny_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    if extra:
        for path in scan_files:
            if not path.exists() or any(part in IGNORED_PARTS for part in path.parts) or path == deny_file:
                continue
            low = path.read_text(encoding="utf-8", errors="ignore").lower()
            for term in extra:
                if re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", low):
                    errors.append(f"{path.relative_to(REPO_ROOT)}: contiene termino privado '{term}'")

    for line in warnings if args.verbose else []:
        print(f"[AVISO] {line}")
    for line in errors:
        print(f"[ERROR] {line}")
    print(f"\n{len(skills)} skills revisadas: {len(errors)} errores, {len(warnings)} avisos.")
    return 1 if errors else 0


# ---------------------------------------------------------------------------
# openai-yaml
# ---------------------------------------------------------------------------

def display_name(name: str) -> str:
    special = {"seo": "SEO", "geo": "GEO", "ui": "UI", "ux": "UX", "ai": "AI", "ia": "IA", "css": "CSS", "cli": "CLI", "gen": "Gen"}
    return " ".join(special.get(part, part.capitalize()) for part in name.split("-"))


def short_description(skill: Skill, limit: int = MAX_SHORT_DESCRIPTION) -> str:
    metadata = skill.frontmatter.get("metadata") or {}
    text = metadata.get("short-description") if isinstance(metadata, dict) else None
    if not text:
        text = re.split(r"(?<=[.!?])\s", skill.description, maxsplit=1)[0]
        text = re.sub(r"^(Use (?:this skill )?(?:when|for|to)\s|Usa(?:r)? (?:esta skill )?(?:cuando|para)\s)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\(v?\d+(\.\d+)*\)\s*$", "", text.strip())
    if len(text) > limit:
        text = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:—-") + "…"
    return text[:1].upper() + text[1:]


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def cmd_openai_yaml(args: argparse.Namespace) -> int:
    created = 0
    for skill in discover():
        target = skill.path / "agents" / "openai.yaml"
        legacy = skill.path / "agents" / "openai.yml"
        if legacy.exists() and not target.exists():
            legacy.rename(target)
        if target.exists() and not args.force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "interface:\n"
            f"  display_name: {yaml_quote(display_name(skill.name))}\n"
            f"  short_description: {yaml_quote(short_description(skill))}\n"
            f"  default_prompt: {yaml_quote(f'Usa ${skill.name} para ayudarme con esta tarea.')}\n"
            "policy:\n"
            "  allow_implicit_invocation: true\n",
            encoding="utf-8",
        )
        created += 1
    print(f"agents/openai.yaml creados o actualizados: {created}")
    return 0


# ---------------------------------------------------------------------------
# package
# ---------------------------------------------------------------------------

def portable_frontmatter(skill: Skill) -> str:
    """Frontmatter solo con claves estandar (lo que aceptan ChatGPT y claude.ai)."""
    metadata = dict(skill.frontmatter.get("metadata") or {}) if isinstance(skill.frontmatter.get("metadata"), dict) else {}
    if "version" in skill.frontmatter and "version" not in metadata:
        metadata["version"] = str(skill.frontmatter["version"])
    lines = ["---", f"name: {skill.name}", f"description: {yaml_quote(skill.description)}"]
    for key in ("license", "compatibility", "allowed-tools"):
        if key in skill.frontmatter and isinstance(skill.frontmatter[key], str):
            lines.append(f"{key}: {yaml_quote(skill.frontmatter[key])}")
    if metadata:
        lines.append("metadata:")
        lines.extend(f"  {key}: {yaml_quote(str(value))}" for key, value in metadata.items())
    lines.append("---")
    return "\n".join(lines) + "\n"


def write_skill_zip(skill: Skill, zip_path: Path) -> int:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in skill_files(skill):
            arcname = f"{skill.name}/{path.relative_to(skill.path).as_posix()}"
            if path == skill.path / "SKILL.md":
                bundle.writestr(arcname, portable_frontmatter(skill) + skill.body.lstrip("\n"))
            else:
                bundle.write(path, arcname)
    return zip_path.stat().st_size


def build_chatgpt_project_pack(skills: list[Skill], out_dir: Path) -> None:
    """Archivos de conocimiento para Proyectos de ChatGPT (planes sin Skills)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[Skill]] = {}
    for skill in skills:
        groups.setdefault(skill.category, []).append(skill)
    index_lines = []
    for category, items in sorted(groups.items()):
        parts = [f"# Agentic Marketing OS — {category}\n",
                 "Cada sección es una skill. Aplica la sección cuya descripción coincida con la petición.\n"]
        for skill in items:
            parts.append(f"\n\n---\n\n## Skill: {skill.name}\n\n**Cuándo usarla:** {skill.description}\n\n{skill.body.strip()}\n")
        (out_dir / f"{category}.md").write_text("".join(parts), encoding="utf-8")
        index_lines.append(f"- `{category}.md`: " + ", ".join(s.name for s in items))
    (out_dir / "INSTRUCCIONES-DEL-PROYECTO.md").write_text(
        "# Instrucciones para el Proyecto de ChatGPT\n\n"
        "Copia el bloque de abajo en **Instrucciones** del Proyecto y sube como archivos los `.md` de las\n"
        "categorías que vayas a usar (marketing y seo-geo son el mínimo recomendado).\n\n"
        "```text\n"
        "Eres mi equipo de marketing con IA (Agentic Marketing OS). Los archivos del proyecto contienen\n"
        "skills: cada sección '## Skill: <nombre>' dice cuándo usarla y cómo trabajar.\n"
        "1. Antes de responder, identifica la skill que corresponde y sigue su proceso y formato.\n"
        "2. Si existe mi perfil de marca (brand-profile.md) en los archivos, úsalo siempre; si no, créalo\n"
        "   entrevistándome con máximo 8 preguntas (plantilla de la skill instagram-content-suite).\n"
        "3. No inventes cifras, testimonios ni datos de mi negocio; marca supuestos como [POR CONFIRMAR].\n"
        "4. Las skills mencionan comandos de terminal (memoria, graphify, flow-veo, elevenlabs): aquí no\n"
        "   existen; entrega el resultado directamente en la conversación.\n"
        "5. Entrega siempre algo listo para usar: tablas, calendarios, guiones, copies, prompts.\n"
        "```\n\n## Archivos disponibles\n\n" + "\n".join(index_lines) + "\n",
        encoding="utf-8",
    )


def cmd_package(args: argparse.Namespace) -> int:
    skills = discover()
    skills_dir = DIST_ROOT / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for old in skills_dir.glob("*.zip"):
        old.unlink()
    total = 0
    for skill in skills:
        size = write_skill_zip(skill, skills_dir / f"{skill.name}.zip")
        total += size
        flag = "  <- grande, puede exceder el limite de subida" if size > ZIP_WARN_BYTES else ""
        if args.verbose or flag:
            print(f"{skill.name}.zip  {size / 1024:.0f} KB{flag}")
    all_zip = DIST_ROOT / "agentic-marketing-os-skills.zip"
    with zipfile.ZipFile(all_zip, "w", zipfile.ZIP_STORED) as bundle:
        for path in sorted(skills_dir.glob("*.zip")):
            bundle.write(path, f"skills/{path.name}")
    build_chatgpt_project_pack(skills, DIST_ROOT / "chatgpt-proyecto")
    print(f"{len(skills)} skills empaquetadas en {skills_dir.relative_to(REPO_ROOT)} ({total / 1024 / 1024:.1f} MB)")
    print(f"Paquete completo: {all_zip.relative_to(REPO_ROOT)}")
    print(f"Proyecto de ChatGPT: {(DIST_ROOT / 'chatgpt-proyecto').relative_to(REPO_ROOT)}")
    return 0


# ---------------------------------------------------------------------------
# marketplace
# ---------------------------------------------------------------------------

def cmd_marketplace(args: argparse.Namespace) -> int:
    skills = discover()
    plugins = []
    covered: set[str] = set()
    for plugin_name, (description, folders) in PLUGIN_GROUPS.items():
        folder_paths = [REPO_ROOT / folder for folder in folders]
        members = sorted(s.name for s in skills if s.path.parent in folder_paths)
        covered.update(members)
        plugins.append({
            "name": plugin_name,
            "source": "./",
            "description": f"{description} ({len(members)} skills)",
            "version": args.version,
            "category": "marketing",
            "skills": [f"./{folder}/" for folder in folders],
        })
    missing = sorted({s.name for s in skills} - covered)
    if missing:
        print(f"[ERROR] Skills fuera de cualquier plugin: {missing}")
        return 1
    manifest = {
        "name": "agentic-marketing-os",
        "owner": {"name": "Agentic Marketing OS"},
        "metadata": {
            "description": "Skills de marketing, SEO/GEO, diseño, video y memoria para trabajar el marketing de tu empresa con IA.",
            "version": args.version,
        },
        "plugins": plugins,
    }
    target = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{target.relative_to(REPO_ROOT)}: {len(plugins)} plugins, {len(covered)} skills")
    return 0


# ---------------------------------------------------------------------------
# catalog
# ---------------------------------------------------------------------------

CATEGORY_TITLES = {
    "marketing": "Marketing, copywriting y gestión",
    "seo-geo": "SEO y GEO (búsqueda con IA)",
    "research-intelligence": "Investigación y competencia",
    "design-creative": "Diseño web, UI/UX e imágenes",
    "video-production": "Video con IA y video programático",
    "audio": "Audio y voz",
    "browser-automation": "Navegador autónomo",
    "memory": "Memoria y grafos de conocimiento",
}


def cmd_catalog(args: argparse.Namespace) -> int:
    skills = discover()
    plugin_of = {}
    for plugin_name, (_, folders) in PLUGIN_GROUPS.items():
        for skill in skills:
            if skill.path.parent in [REPO_ROOT / f for f in folders]:
                plugin_of[skill.name] = plugin_name
    lines = [
        "# Catálogo de skills",
        "",
        f"{len(skills)} skills. Archivo generado con `python3 scripts/skills_tool.py catalog`; no editar a mano.",
        "",
        "En Claude Code con plugins se invocan como `/<plugin>:<skill>`; con el instalador, como `/<skill>`.",
        "En Codex se mencionan con `$<skill>`. En todos los agentes también se activan solas según la petición.",
        "",
    ]
    for category in CATEGORY_TITLES:
        items = [s for s in skills if s.category == category]
        if not items:
            continue
        lines += [f"## {CATEGORY_TITLES[category]}", "", "| Skill | Plugin | Para qué sirve |", "|---|---|---|"]
        for skill in items:
            summary = short_description(skill, 140).replace("|", "/")
            lines.append(f"| [`{skill.name}`](../{skill.rel}/SKILL.md) | `{plugin_of.get(skill.name, '-')}` | {summary} |")
        lines.append("")
    target = REPO_ROOT / "docs" / "CATALOGO.md"
    target.parent.mkdir(exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"{target.relative_to(REPO_ROOT)}: {len(skills)} skills")
    return 0


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> int:
    for skill in discover():
        if args.paths:
            print(skill.path)
        else:
            print(f"{skill.name:34} {skill.category:22} {skill.rel}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p_list = sub.add_parser("list", help="Lista las skills")
    p_list.add_argument("--paths", action="store_true", help="Imprime solo rutas absolutas")
    p_val = sub.add_parser("validate", help="Valida el catalogo")
    p_val.add_argument("--verbose", "-v", action="store_true", help="Muestra tambien los avisos")
    p_val.add_argument("--deny", action="append", help="Termino privado adicional a buscar (repetible)")
    p_yaml = sub.add_parser("openai-yaml", help="Genera agents/openai.yaml faltantes")
    p_yaml.add_argument("--force", action="store_true", help="Sobrescribe los existentes")
    p_pkg = sub.add_parser("package", help="Genera zips para ChatGPT / claude.ai")
    p_pkg.add_argument("--verbose", "-v", action="store_true")
    p_mkt = sub.add_parser("marketplace", help="Regenera .claude-plugin/marketplace.json")
    p_mkt.add_argument("--version", default="2.0.0")
    sub.add_parser("catalog", help="Regenera docs/CATALOGO.md")
    args = parser.parse_args()
    handlers = {"list": cmd_list, "validate": cmd_validate, "openai-yaml": cmd_openai_yaml, "package": cmd_package, "marketplace": cmd_marketplace, "catalog": cmd_catalog}
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
