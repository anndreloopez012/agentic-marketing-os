#!/usr/bin/env bash
# ==============================================================================
# Agentic Marketing OS - Universal Zero-to-Hero Installer
# Compatible with: Claude Code, OpenAI Codex, Google Antigravity
# Platforms: macOS, Linux, WSL
# ==============================================================================

set -e

# Visual formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
ENGINE_DIR="$REPO_ROOT/engine/memory"
TEMPLATES_DIR="$REPO_ROOT/templates"

clear 2>/dev/null || true
echo -e "${CYAN}${BOLD}"
echo "======================================================================"
echo "    🚀 AGENTIC MARKETING OS - INSTALADOR UNIVERSAL DE HABILIDADES     "
echo "  Marketing • Copywriting • Diseño • SEO/GEO • Video • Memoria Vault  "
echo "======================================================================"
echo -e "${NC}"

echo -e "${BLUE}ℹ️ Este asistente configurará tus herramientas de IA (Claude Code, Codex, Antigravity),${NC}"
echo -e "${BLUE}  sincronizará tu Obsidian Vault con Graphify y enlazará todas las habilidades.${NC}\n"

# ------------------------------------------------------------------------------
# 1. Comprobación de Requisitos Previos del Sistema
# ------------------------------------------------------------------------------
echo -e "${BOLD}[1/6] Verificando dependencias del sistema...${NC}"

# Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado. Instálalo antes de continuar (ej. brew install python3 o apt install python3).${NC}"
    exit 1
else
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "  ${GREEN}✔ Python 3 detectado:${NC} v$PY_VER"
fi

# Node.js y npm
if ! command -v node &>/dev/null; then
    echo -e "${RED}❌ Node.js no está instalado. Instálalo (v18 o v20+ recomendada).${NC}"
    exit 1
else
    NODE_VER=$(node -v)
    echo -e "  ${GREEN}✔ Node.js detectado:${NC} $NODE_VER"
fi

# FFmpeg (para renderizado de Remotion y HyperFrames)
if ! command -v ffmpeg &>/dev/null; then
    echo -e "  ${YELLOW}⚠️ FFmpeg no encontrado en PATH. Es requerido para renderizar videos con Remotion y HyperFrames.${NC}"
    echo -e "     En macOS: ${CYAN}brew install ffmpeg${NC}"
    echo -e "     En Ubuntu/Debian: ${CYAN}sudo apt install ffmpeg${NC}"
else
    echo -e "  ${GREEN}✔ FFmpeg detectado:${NC} $(ffmpeg -version 2>/dev/null | head -n 1 | awk '{print $3}')"
fi

# Gestor de paquetes Python (uv o pipx)
HAS_UV=false
HAS_PIPX=false
if command -v uv &>/dev/null; then
    HAS_UV=true
    echo -e "  ${GREEN}✔ uv detectado:${NC} $(uv --version)"
elif command -v pipx &>/dev/null; then
    HAS_PIPX=true
    echo -e "  ${GREEN}✔ pipx detectado:${NC} $(pipx --version)"
else
    echo -e "  ${YELLOW}ℹ️ No se detectó uv ni pipx. Intentaremos instalar pipx con python3 -m pip...${NC}"
    python3 -m pip install --user pipx 2>/dev/null || true
    if command -v pipx &>/dev/null; then
        HAS_PIPX=true
        pipx ensurepath 2>/dev/null || true
    fi
fi

# ------------------------------------------------------------------------------
# 2. Configuración Interactiva de Rutas del Alumno
# ------------------------------------------------------------------------------
echo -e "\n${BOLD}[2/6] Configuración de tu entorno de trabajo...${NC}"

# Pregunta: Ubicación del Obsidian Vault
DEFAULT_VAULT="$HOME/Documents/Obsidian Vault"
if [ -n "$1" ]; then
    VAULT_PATH="$1"
else
    read -p "$(echo -e "${CYAN}📁 ¿Dónde está la carpeta de tu Obsidian Vault? [Por defecto: ${DEFAULT_VAULT}]: ${NC}")" USER_VAULT_INPUT
    VAULT_PATH="${USER_VAULT_INPUT:-$DEFAULT_VAULT}"
fi

# Expandir tilde si existe
VAULT_PATH="${VAULT_PATH/#\~/$HOME}"
echo -e "  ${GREEN}✔ Obsidian Vault configurado en:${NC} $VAULT_PATH"

# Pregunta: Ubicación donde guardará proyectos y entregables de marketing
DEFAULT_WORKSPACE="$HOME/Documents/MarketingProjects"
if [ -n "$2" ]; then
    WORKSPACE_PATH="$2"
else
    read -p "$(echo -e "${CYAN}💼 ¿Dónde deseas guardar tus proyectos y entregables de marketing? [Por defecto: ${DEFAULT_WORKSPACE}]: ${NC}")" USER_WORKSPACE_INPUT
    WORKSPACE_PATH="${USER_WORKSPACE_INPUT:-$DEFAULT_WORKSPACE}"
fi

WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"
mkdir -p "$WORKSPACE_PATH"
echo -e "  ${GREEN}✔ Directorio de proyectos configurado en:${NC} $WORKSPACE_PATH"

# Pregunta: ¿Qué agentes de IA usa el usuario?
echo -e "\n${CYAN}🤖 ¿Qué asistentes de IA utilizas en esta máquina?${NC}"
echo "  1) Todos (Claude Code, OpenAI Codex y Google Antigravity) [Recomendado]"
echo "  2) Claude Code únicamente"
echo "  3) OpenAI Codex únicamente"
echo "  4) Google Antigravity únicamente"
read -p "$(echo -e "${CYAN}Selecciona una opción [1-4, por defecto: 1]: ${NC}")" AGENT_OPT
AGENT_OPT="${AGENT_OPT:-1}"

# ------------------------------------------------------------------------------
# 3. Inicialización del Baúl de Obsidian (Estructura de Memoria Continua)
# ------------------------------------------------------------------------------
echo -e "\n${BOLD}[3/6] Inicializando sistema de memoria en tu Obsidian Vault...${NC}"
mkdir -p "$VAULT_PATH/Memoria" \
         "$VAULT_PATH/Memoria/Bitacora" \
         "$VAULT_PATH/Memoria/Graphify" \
         "$VAULT_PATH/Memoria/Proyectos Git" \
         "$VAULT_PATH/Memoria/Decisiones" \
         "$VAULT_PATH/Memoria/Skills"

# Copiar notas maestras iniciales si no existen
if [ ! -f "$VAULT_PATH/Memoria/Inicio Memoria.md" ]; then
    cp "$TEMPLATES_DIR/vault/Memoria/Inicio Memoria.md" "$VAULT_PATH/Memoria/"
    echo -e "  ${GREEN}✔ Creada nota maestra:${NC} $VAULT_PATH/Memoria/Inicio Memoria.md"
fi

if [ ! -f "$VAULT_PATH/Memoria/Contexto Operativo.md" ]; then
    cp "$TEMPLATES_DIR/vault/Memoria/Contexto Operativo.md" "$VAULT_PATH/Memoria/"
    echo -e "  ${GREEN}✔ Creada nota maestra:${NC} $VAULT_PATH/Memoria/Contexto Operativo.md"
fi

if [ ! -f "$VAULT_PATH/Memoria/Bitacora/Registro de Trabajo.md" ]; then
    cp "$TEMPLATES_DIR/vault/Memoria/Bitacora/Registro de Trabajo.md" "$VAULT_PATH/Memoria/Bitacora/"
    echo -e "  ${GREEN}✔ Creado registro de bitácora:${NC} $VAULT_PATH/Memoria/Bitacora/Registro de Trabajo.md"
fi

# Configurar settings.json para el motor memoria
mkdir -p "$ENGINE_DIR/config"
cat <<EOF > "$ENGINE_DIR/config/settings.json"
{
  "vault_root": "$VAULT_PATH",
  "projects_roots": [
    "$WORKSPACE_PATH",
    "$REPO_ROOT"
  ],
  "graph_compatibility_roots": {
    "MarketingProjects": "$WORKSPACE_PATH",
    "AgenticMarketingOS": "$REPO_ROOT"
  },
  "codex_root": "$HOME/.codex",
  "claude_root": "$HOME/.claude",
  "antigravity_root": "$HOME/.gemini/antigravity",
  "antigravity_skills": "$HOME/.gemini/config/skills",
  "graphify_bin": "$HOME/.local/bin/graphify",
  "project_family_overrides": {},
  "vitaminado": {
    "inactive_days": 180,
    "summary_daily": true,
    "summary_weekly": true,
    "smart_capture": true,
    "portability_full_copy_on_demand": true
  }
}
EOF
echo -e "  ${GREEN}✔ Configuración de rutas guardada en:${NC} $ENGINE_DIR/config/settings.json"

# Enlazar CLI memoria a ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sfn "$ENGINE_DIR/bin/memoria" "$HOME/.local/bin/memoria"
chmod +x "$ENGINE_DIR/bin/memoria"
echo -e "  ${GREEN}✔ Comando 'memoria' instalado en:${NC} $HOME/.local/bin/memoria"

# ------------------------------------------------------------------------------
# 4. Instalación de Herramientas CLI (Graphify, Agent-Browser, HyperFrames)
# ------------------------------------------------------------------------------
echo -e "\n${BOLD}[4/6] Verificando e instalando herramientas CLI globales...${NC}"

# Graphify
if ! command -v graphify &>/dev/null; then
    echo -e "  ${CYAN}📦 Instalando Graphifyy (Motor AST de Grafo de Conocimiento)...${NC}"
    if [ "$HAS_UV" = true ]; then
        uv tool install graphifyy || true
    elif [ "$HAS_PIPX" = true ]; then
        pipx install graphifyy || true
    else
        python3 -m pip install --user graphifyy || true
    fi
else
    echo -e "  ${GREEN}✔ Graphify ya está instalado.${NC}"
fi

# Agent-Browser (Navegador autónomo)
if ! command -v agent-browser &>/dev/null; then
    echo -e "  ${CYAN}📦 Instalando agent-browser (Automatización y visualización web)...${NC}"
    npm install -g agent-browser 2>/dev/null || sudo npm install -g agent-browser 2>/dev/null || true
else
    echo -e "  ${GREEN}✔ agent-browser ya está instalado:${NC} $(agent-browser --version 2>/dev/null || echo 'listo')"
fi

# HyperFrames (Video programmatic rendering)
if ! command -v hyperframes &>/dev/null; then
    echo -e "  ${CYAN}📦 Instalando hyperframes (Renderizado de video de alta velocidad)...${NC}"
    npm install -g hyperframes 2>/dev/null || sudo npm install -g hyperframes 2>/dev/null || true
else
    echo -e "  ${GREEN}✔ hyperframes ya está instalado:${NC} $(hyperframes --version 2>/dev/null || echo 'listo')"
fi

# ------------------------------------------------------------------------------
# 5. Enlace Universal de Habilidades a Claude Code, Codex y Antigravity
# ------------------------------------------------------------------------------
echo -e "\n${BOLD}[5/6] Enlazando catálogo de habilidades a los agentes de IA...${NC}"

TARGET_DIRS=()
case "$AGENT_OPT" in
    1)
        TARGET_DIRS+=("$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.gemini/config/skills")
        ;;
    2)
        TARGET_DIRS+=("$HOME/.claude/skills")
        ;;
    3)
        TARGET_DIRS+=("$HOME/.codex/skills")
        ;;
    4)
        TARGET_DIRS+=("$HOME/.gemini/config/skills")
        ;;
    *)
        TARGET_DIRS+=("$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.gemini/config/skills")
        ;;
esac

# Recorrer todas las carpetas con SKILL.md dentro de skills/
SKILL_COUNT=0
for skill_file in $(find "$SKILLS_DIR" -type f -name "SKILL.md"); do
    skill_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$skill_dir")"
    
    for dest_root in "${TARGET_DIRS[@]}"; do
        mkdir -p "$dest_root"
        ln -sfn "$skill_dir" "$dest_root/$skill_name"
    done
    SKILL_COUNT=$((SKILL_COUNT + 1))
done

echo -e "  ${GREEN}✔ $SKILL_COUNT habilidades sincronizadas y enlazadas con éxito.${NC}"

# Copiar reglas maestras (AGENTS.md, CLAUDE.md, GEMINI.md) al Workspace del alumno
cp "$REPO_ROOT/AGENTS.md" "$WORKSPACE_PATH/AGENTS.md" 2>/dev/null || true
cp "$REPO_ROOT/CLAUDE.md" "$WORKSPACE_PATH/CLAUDE.md" 2>/dev/null || true
cp "$REPO_ROOT/GEMINI.md" "$WORKSPACE_PATH/GEMINI.md" 2>/dev/null || true
mkdir -p "$WORKSPACE_PATH/.agents/rules"
cp "$REPO_ROOT/AGENTS.md" "$WORKSPACE_PATH/.agents/rules/AGENTS.md" 2>/dev/null || true

# Configurar plantilla de variables de entorno si no existe
if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo -e "  ${GREEN}✔ Creado archivo .env con plantilla de credenciales.${NC}"
fi

# ------------------------------------------------------------------------------
# 6. Verificación Final de Estado
# ------------------------------------------------------------------------------
echo -e "\n${BOLD}[6/6] Verificando integridad del sistema...${NC}"
chmod +x "$REPO_ROOT/scripts/doctor.sh" "$REPO_ROOT/scripts/sync-vault.sh" 2>/dev/null || true

echo -e "\n${GREEN}${BOLD}======================================================================${NC}"
echo -e "${GREEN}${BOLD}  🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!                              ${NC}"
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo -e "  • ${BOLD}Obsidian Vault:${NC} $VAULT_PATH"
echo -e "  • ${BOLD}Directorio de Entregables:${NC} $WORKSPACE_PATH"
echo -e "  • ${BOLD}Total Habilidades Activas:${NC} $SKILL_COUNT"
echo -e "  • ${BOLD}Herramientas Listas:${NC} memoria, graphify, agent-browser, hyperframes, remotion"
echo -e "\n${CYAN}💡 Siguientes pasos recomendados:${NC}"
echo -e "  1. Configura tus API keys en: ${BOLD}$REPO_ROOT/.env${NC} (ElevenLabs, OpenAI, Gemini)"
echo -e "  2. Ejecuta el diagnóstico del sistema: ${BOLD}./scripts/doctor.sh${NC}"
echo -e "  3. Abre tu Obsidian y navega a: ${BOLD}Memoria/Inicio Memoria.md${NC}"
echo -e "  4. Inicia tu asistente favorito (claude, codex o antigravity) en tu carpeta de proyectos.\n"
