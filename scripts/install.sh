#!/usr/bin/env bash
# ==============================================================================
# Agentic Marketing OS - Instalador universal (macOS, Linux y WSL)
# Enlaza las skills a Claude Code, OpenAI Codex (CLI, app y extensión) y Gemini /
# Antigravity, prepara la memoria en Obsidian e instala los CLI de apoyo.
#
# Uso:
#   ./scripts/install.sh                         # asistente interactivo
#   ./scripts/install.sh --yes                   # todo por defecto, sin preguntas
#   ./scripts/install.sh --agents claude,codex --vault ~/Obsidian --workspace ~/Marketing
#   ./scripts/install.sh --copy                  # copia en lugar de enlazar
#   ./scripts/install.sh --uninstall             # quita los enlaces creados
#
# Para ChatGPT (web/app) y claude.ai no se instala nada aquí: usa los .zip de
# `python3 scripts/skills_tool.py package` (ver README).
# ==============================================================================

set -euo pipefail

BOLD="\033[1m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; CYAN="\033[0;36m"; NC="\033[0m"
ok()   { echo -e "  ${GREEN}✔${NC} $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $*"; }
fail() { echo -e "  ${RED}✖${NC} $*"; }
step() { echo -e "\n${BOLD}$*${NC}"; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
ENGINE_DIR="$REPO_ROOT/engine/memory"
TEMPLATES_DIR="$REPO_ROOT/templates"
TOOLS_VENV="$REPO_ROOT/.venv-tools"
NODE_TOOLS="$REPO_ROOT/.tools/node"
LOCAL_BIN="$HOME/.local/bin"

CLAUDE_SKILLS="$HOME/.claude/skills"
CODEX_SKILLS="$HOME/.agents/skills"          # ruta de usuario documentada por Codex
CODEX_LEGACY_SKILLS="$HOME/.codex/skills"    # versiones antiguas de Codex
GEMINI_SKILLS="$HOME/.gemini/config/skills"  # Google Antigravity

VAULT_PATH=""
WORKSPACE_PATH=""
AGENTS=""
MODE="link"
ASSUME_YES=false
INSTALL_TOOLS=true
CODEX_LEGACY=false
UNINSTALL=false

usage() { sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0; }

POSITIONAL=()
while [ $# -gt 0 ]; do
    case "$1" in
        --vault) VAULT_PATH="$2"; shift 2 ;;
        --workspace) WORKSPACE_PATH="$2"; shift 2 ;;
        --agents) AGENTS="$2"; shift 2 ;;
        --copy) MODE="copy"; shift ;;
        --yes|-y) ASSUME_YES=true; shift ;;
        --no-tools) INSTALL_TOOLS=false; shift ;;
        --codex-legacy) CODEX_LEGACY=true; shift ;;
        --uninstall) UNINSTALL=true; shift ;;
        -h|--help) usage ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done
# Compatibilidad con la versión anterior: install.sh <vault> <workspace>
if [ -z "$VAULT_PATH" ] && [ "${#POSITIONAL[@]}" -ge 1 ]; then VAULT_PATH="${POSITIONAL[0]}"; fi
if [ -z "$WORKSPACE_PATH" ] && [ "${#POSITIONAL[@]}" -ge 2 ]; then WORKSPACE_PATH="${POSITIONAL[1]}"; fi

expand_path() { local p="$1"; p="${p/#\~/$HOME}"; printf '%s' "$p"; }

interactive() { [ "$ASSUME_YES" = false ] && [ -t 0 ]; }

ask() {
    # ask <variable> <pregunta> <valor por defecto>
    local __var="$1" question="$2" default="$3" answer=""
    if interactive; then
        read -r -p "$(echo -e "${CYAN}${question} [${default}]: ${NC}")" answer || true
    fi
    answer="${answer:-$default}"
    printf -v "$__var" '%s' "$(expand_path "$answer")"
}

target_dirs() {
    local list="${AGENTS:-all}" agent
    [ "$list" = "all" ] && list="claude,codex,gemini"
    IFS=',' read -r -a chosen <<< "$list"
    for agent in "${chosen[@]}"; do
        case "$(echo "$agent" | tr '[:upper:]' '[:lower:]' | tr -d ' ')" in
            claude) echo "$CLAUDE_SKILLS" ;;
            codex|chatgpt|openai)
                echo "$CODEX_SKILLS"
                if [ "$CODEX_LEGACY" = true ]; then echo "$CODEX_LEGACY_SKILLS"; fi ;;
            gemini|antigravity) echo "$GEMINI_SKILLS" ;;
            *) warn "Agente desconocido ignorado: $agent" >&2 ;;
        esac
    done
}

points_into_repo() { case "$(readlink "$1")" in "$SKILLS_DIR"/*) return 0 ;; *) return 1 ;; esac; }

# Elimina enlaces de instalaciones anteriores que apuntan a skills que ya no existen.
prune_stale_links() {
    local dest_root="$1" link
    [ -d "$dest_root" ] || return 0
    for link in "$dest_root"/*; do
        if [ -L "$link" ] && points_into_repo "$link" && [ ! -e "$link" ]; then
            rm -f "$link"
            echo "    · enlace obsoleto eliminado: $(basename "$link")"
        fi
    done
}

# ------------------------------------------------------------------------------
# Desinstalación
# ------------------------------------------------------------------------------
if [ "$UNINSTALL" = true ]; then
    step "Quitando skills de Agentic Marketing OS..."
    for dest_root in "$CLAUDE_SKILLS" "$CODEX_SKILLS" "$CODEX_LEGACY_SKILLS" "$GEMINI_SKILLS"; do
        [ -d "$dest_root" ] || continue
        removed=0
        for link in "$dest_root"/*; do
            if [ -L "$link" ] && points_into_repo "$link"; then
                rm -f "$link"; removed=$((removed + 1))
            elif [ -f "$link/.agentic-marketing-os" ]; then
                rm -rf "$link"; removed=$((removed + 1))
            fi
        done
        ok "$dest_root: $removed skills quitadas"
    done
    for tool in memoria elevenlabs el flow-veo hyperframes agent-browser; do
        if [ -L "$LOCAL_BIN/$tool" ] || grep -qs "agentic-marketing-os wrapper" "$LOCAL_BIN/$tool"; then rm -f "$LOCAL_BIN/$tool"; fi
    done
    ok "Listo. Tus notas de Obsidian y tus proyectos no se tocaron."
    exit 0
fi

if interactive; then clear 2>/dev/null || true; fi
echo -e "${CYAN}${BOLD}"
echo "======================================================================"
echo "        AGENTIC MARKETING OS - INSTALADOR UNIVERSAL DE SKILLS         "
echo "  Marketing • Copywriting • Diseño • SEO/GEO • Video • Memoria Vault  "
echo "======================================================================"
echo -e "${NC}"

# ------------------------------------------------------------------------------
# 1. Requisitos
# ------------------------------------------------------------------------------
step "[1/6] Verificando dependencias del sistema..."
if ! command -v python3 >/dev/null 2>&1; then
    fail "Python 3 no está instalado (macOS: brew install python3 · Ubuntu/WSL: sudo apt install python3 python3-venv)."
    exit 1
fi
ok "Python $(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
if command -v node >/dev/null 2>&1; then ok "Node.js $(node -v)"; else warn "Node.js no encontrado: necesario para video (Remotion/HyperFrames) y agent-browser. Instala Node 20+."; fi
if command -v ffmpeg >/dev/null 2>&1; then ok "FFmpeg"; else warn "FFmpeg no encontrado: necesario para renderizar video (brew install ffmpeg · sudo apt install ffmpeg)."; fi
if command -v git >/dev/null 2>&1; then ok "Git"; else warn "Git no encontrado."; fi

# ------------------------------------------------------------------------------
# 2. Rutas del alumno
# ------------------------------------------------------------------------------
step "[2/6] Configuración de tu entorno de trabajo..."
[ -n "$VAULT_PATH" ] || ask VAULT_PATH "📁 ¿Dónde está (o dónde creamos) tu Obsidian Vault?" "$HOME/Documents/Obsidian Vault"
[ -n "$WORKSPACE_PATH" ] || ask WORKSPACE_PATH "💼 ¿Dónde guardarás los proyectos y entregables de marketing?" "$HOME/Documents/MarketingProjects"
VAULT_PATH="$(expand_path "$VAULT_PATH")"
WORKSPACE_PATH="$(expand_path "$WORKSPACE_PATH")"

if [ -z "$AGENTS" ]; then
    AGENTS="all"
    if interactive; then
        echo -e "\n${CYAN}🤖 ¿Qué asistentes de IA usas en esta máquina?${NC}"
        echo "  1) Todos: Claude Code, Codex (ChatGPT) y Gemini/Antigravity [Recomendado]"
        echo "  2) Claude Code"
        echo "  3) Codex (CLI, app de escritorio o extensión de VS Code con tu cuenta de ChatGPT)"
        echo "  4) Gemini / Google Antigravity"
        echo "  5) Claude Code + Codex"
        opt=""
        read -r -p "$(echo -e "${CYAN}Opción [1-5, por defecto 1]: ${NC}")" opt || true
        case "${opt:-1}" in
            2) AGENTS="claude" ;; 3) AGENTS="codex" ;; 4) AGENTS="gemini" ;; 5) AGENTS="claude,codex" ;; *) AGENTS="all" ;;
        esac
    fi
fi
mkdir -p "$WORKSPACE_PATH"
ok "Obsidian Vault: $VAULT_PATH"
ok "Proyectos: $WORKSPACE_PATH"
ok "Asistentes: $AGENTS (modo: $MODE)"

# ------------------------------------------------------------------------------
# 3. Memoria en Obsidian
# ------------------------------------------------------------------------------
step "[3/6] Preparando la memoria en tu Obsidian Vault..."
mkdir -p "$VAULT_PATH/Memoria/Bitacora" "$VAULT_PATH/Memoria/Graphify" "$VAULT_PATH/Memoria/Proyectos Git" \
         "$VAULT_PATH/Memoria/Decisiones" "$VAULT_PATH/Memoria/Skills" "$VAULT_PATH/Memoria/Marcas"
for note in "Inicio Memoria.md" "Contexto Operativo.md" "Bitacora/Registro de Trabajo.md"; do
    if [ ! -f "$VAULT_PATH/Memoria/$note" ]; then
        cp "$TEMPLATES_DIR/vault/Memoria/$note" "$VAULT_PATH/Memoria/$note"
        ok "Creada: Memoria/$note"
    fi
done

mkdir -p "$ENGINE_DIR/config"
VAULT_PATH="$VAULT_PATH" WORKSPACE_PATH="$WORKSPACE_PATH" python3 - "$ENGINE_DIR/config/settings.json" <<'PY'
import json, os, sys
home = os.path.expanduser("~")
settings = {
    "vault_root": os.environ["VAULT_PATH"],
    "projects_roots": [os.environ["WORKSPACE_PATH"]],
    "graph_compatibility_roots": {"MarketingProjects": os.environ["WORKSPACE_PATH"]},
    "codex_root": os.path.join(home, ".codex"),
    "claude_root": os.path.join(home, ".claude"),
    "antigravity_root": os.path.join(home, ".gemini", "antigravity"),
    "antigravity_skills": os.path.join(home, ".gemini", "config", "skills"),
    "graphify_bin": os.path.join(home, ".local", "bin", "graphify"),
    "project_family_overrides": {},
    "vitaminado": {"inactive_days": 180, "summary_daily": True, "summary_weekly": True,
                   "smart_capture": True, "portability_full_copy_on_demand": True},
}
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    json.dump(settings, fh, ensure_ascii=False, indent=2)
PY
ok "Rutas guardadas en engine/memory/config/settings.json"

mkdir -p "$LOCAL_BIN"
chmod +x "$ENGINE_DIR/bin/memoria" "$ENGINE_DIR/bin/multimedia" "$ENGINE_DIR/bin/skills" 2>/dev/null || true
ln -sfn "$ENGINE_DIR/bin/memoria" "$LOCAL_BIN/memoria"
ok "Comando 'memoria' disponible en $LOCAL_BIN"

# ------------------------------------------------------------------------------
# 4. Herramientas CLI
# ------------------------------------------------------------------------------
step "[4/6] Herramientas de línea de comandos..."
write_wrapper() {
    # write_wrapper <nombre> <ejecutable> [script]: carga .env del repo y ejecuta
    local name="$1" executable="$2" script="${3:-}"
    {
        echo '#!/usr/bin/env bash'
        echo '# agentic-marketing-os wrapper'
        printf 'if [ -f %q ]; then set -a; . %q; set +a; fi\n' "$REPO_ROOT/.env" "$REPO_ROOT/.env"
        if [ -n "$script" ]; then
            printf 'exec %q %q "$@"\n' "$executable" "$script"
        else
            printf 'exec %q "$@"\n' "$executable"
        fi
    } > "$LOCAL_BIN/$name"
    chmod +x "$LOCAL_BIN/$name"
}

if [ "$INSTALL_TOOLS" = true ]; then
    if [ ! -x "$TOOLS_VENV/bin/python" ]; then
        python3 -m venv "$TOOLS_VENV" >/dev/null 2>&1 || warn "No se pudo crear el entorno virtual (en Ubuntu/WSL: sudo apt install python3-venv)."
    fi
    if [ -x "$TOOLS_VENV/bin/python" ]; then
        "$TOOLS_VENV/bin/python" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
        ELEVEN_CLI="$SKILLS_DIR/audio/elevenlabs/scripts/elevenlabs_cli.py"
        if "$TOOLS_VENV/bin/python" -m pip install --quiet elevenlabs >/dev/null 2>&1; then
            write_wrapper elevenlabs "$TOOLS_VENV/bin/python" "$ELEVEN_CLI"
            write_wrapper el "$TOOLS_VENV/bin/python" "$ELEVEN_CLI"
            ok "elevenlabs / el (voz, efectos y música con IA)"
        else
            warn "No se pudo instalar la librería de ElevenLabs (revisa tu conexión)."
        fi
        FLOW_DIR="$SKILLS_DIR/video-production/ai-directing/google-flow-veo-director"
        if "$TOOLS_VENV/bin/python" -m pip install --quiet -e "$FLOW_DIR" >/dev/null 2>&1; then
            write_wrapper flow-veo "$TOOLS_VENV/bin/flow-veo"
            ok "flow-veo (director de Google Veo / Flow)"
        else
            warn "No se pudo instalar flow-veo."
        fi
    fi

    if command -v graphify >/dev/null 2>&1; then
        ok "graphify ya instalado"
    elif command -v uv >/dev/null 2>&1 && uv tool install graphifyy >/dev/null 2>&1; then
        ok "graphify (uv)"
    elif command -v pipx >/dev/null 2>&1 && pipx install graphifyy >/dev/null 2>&1; then
        ok "graphify (pipx)"
    else
        warn "graphify no instalado. Opcional: pipx install graphifyy"
    fi

    # HyperFrames y agent-browser van dentro del bundle (sin instalaciones globales).
    if command -v npm >/dev/null 2>&1; then
        mkdir -p "$NODE_TOOLS"
        for pkg in hyperframes agent-browser; do
            if npm install --prefix "$NODE_TOOLS" --no-fund --no-audit "$pkg@latest" >/dev/null 2>&1 \
                && [ -x "$NODE_TOOLS/node_modules/.bin/$pkg" ]; then
                write_wrapper "$pkg" "$NODE_TOOLS/node_modules/.bin/$pkg"
                ok "$pkg (incluido en el bundle: .tools/node)"
            else
                warn "$pkg no se pudo instalar en el bundle. Alternativa: npx $pkg"
            fi
        done
    else
        warn "npm no encontrado: instala Node.js 20+ para HyperFrames y agent-browser."
    fi
else
    warn "Herramientas omitidas (--no-tools)."
fi

# ------------------------------------------------------------------------------
# 5. Skills para cada asistente
# ------------------------------------------------------------------------------
step "[5/6] Instalando las skills en tus asistentes de IA..."
SKILL_DIRS=()
while IFS= read -r line; do
    [ -n "$line" ] && SKILL_DIRS+=("$line")
done < <(python3 "$REPO_ROOT/scripts/skills_tool.py" list --paths)

DEST_ROOTS=()
while IFS= read -r line; do
    [ -n "$line" ] && DEST_ROOTS+=("$line")
done < <(target_dirs)

for dest_root in "${DEST_ROOTS[@]}"; do
    mkdir -p "$dest_root"
    prune_stale_links "$dest_root"
    installed=0; kept=0
    for skill_dir in "${SKILL_DIRS[@]}"; do
        name="$(basename "$skill_dir")"
        dest="$dest_root/$name"
        if [ -e "$dest" ] && [ ! -L "$dest" ] && [ ! -f "$dest/.agentic-marketing-os" ]; then
            kept=$((kept + 1))
            echo "    · se conserva tu skill existente: $name"
            continue
        fi
        rm -rf "$dest"
        if [ "$MODE" = "copy" ]; then
            cp -R "$skill_dir" "$dest"
            touch "$dest/.agentic-marketing-os"
        else
            ln -s "$skill_dir" "$dest"
        fi
        installed=$((installed + 1))
    done
    if [ "$kept" -gt 0 ]; then
        ok "$dest_root: $installed skills ($kept conservadas porque ya existían)"
    else
        ok "$dest_root: $installed skills"
    fi
done

for rules in AGENTS.md CLAUDE.md GEMINI.md; do
    if [ ! -f "$WORKSPACE_PATH/$rules" ]; then
        cp "$REPO_ROOT/$rules" "$WORKSPACE_PATH/$rules"
        ok "Reglas $rules copiadas a tu carpeta de proyectos"
    fi
done
BRAND_TEMPLATE="$SKILLS_DIR/marketing/instagram-content-suite/templates/brand-profile-template.md"
if [ ! -f "$WORKSPACE_PATH/marca/brand-profile.md" ] && [ -f "$BRAND_TEMPLATE" ]; then
    mkdir -p "$WORKSPACE_PATH/marca"
    cp "$BRAND_TEMPLATE" "$WORKSPACE_PATH/marca/brand-profile.md"
    ok "Plantilla de perfil de marca en marca/brand-profile.md"
fi
if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    ok "Creado .env para tus claves de API"
fi

# ------------------------------------------------------------------------------
# 6. Final
# ------------------------------------------------------------------------------
step "[6/6] Verificación final..."
chmod +x "$REPO_ROOT/scripts/"*.sh 2>/dev/null || true
case ":$PATH:" in
    *":$LOCAL_BIN:"*) ok "$LOCAL_BIN está en tu PATH" ;;
    *) warn "Agrega esta línea a tu ~/.zshrc o ~/.bashrc y abre una terminal nueva:  export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

echo -e "\n${GREEN}${BOLD}======================================================================${NC}"
echo -e "${GREEN}${BOLD}  🎉 INSTALACIÓN COMPLETADA                                            ${NC}"
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo -e "  • Skills: ${#SKILL_DIRS[@]}"
echo -e "  • Vault: $VAULT_PATH"
echo -e "  • Proyectos: $WORKSPACE_PATH"
echo -e "\n${CYAN}Siguientes pasos:${NC}"
echo -e "  1. Pon tus claves en ${BOLD}$REPO_ROOT/.env${NC} (solo las de los servicios que uses)."
echo -e "  2. Revisa todo con: ${BOLD}./scripts/doctor.sh${NC}"
echo -e "  3. Reinicia Claude Code / Codex, ábrelo en ${BOLD}$WORKSPACE_PATH${NC} y pide: \"Crea el perfil de marca de mi empresa\"."
echo -e "  4. ¿Usas ChatGPT web o claude.ai? Ejecuta ${BOLD}python3 scripts/skills_tool.py package${NC} y sube los zips de dist/skills.\n"
