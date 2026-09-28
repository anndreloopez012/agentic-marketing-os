#!/usr/bin/env bash
# ==============================================================================
# Agentic Marketing OS - Health & Diagnostic Doctor
# ==============================================================================

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETTINGS_FILE="$REPO_ROOT/engine/memory/config/settings.json"

echo -e "${CYAN}${BOLD}"
echo "======================================================================"
echo "          🩺 AGENTIC MARKETING OS - DIAGNÓSTICO DEL SISTEMA          "
echo "======================================================================"
echo -e "${NC}"

ERRORS=0
WARNINGS=0

# 1. Comprobación de Comandos Base
echo -e "${BOLD}1. Binarios y Entorno de Ejecución:${NC}"

check_cmd() {
    local name="$1"
    local required="$2"
    local install_hint="$3"
    
    if command -v "$name" &>/dev/null; then
        local ver
        ver=$("$name" --version 2>/dev/null | head -n 1 || echo "instalado")
        echo -e "  [${GREEN}OK${NC}] $name (${CYAN}$ver${NC})"
    else
        if [ "$required" = "true" ]; then
            echo -e "  [${RED}FAIL${NC}] $name no encontrado en PATH. $install_hint"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "  [${YELLOW}WARN${NC}] $name no encontrado (opcional). $install_hint"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
}

check_cmd "git" "true" "Instala git desde xcode-select --install o tu gestor de paquetes."
check_cmd "python3" "true" "Instala Python 3.10+ (brew install python3)."
check_cmd "node" "false" "Necesario para video y agent-browser: instala Node.js 20+ (brew install node o nvm)."
check_cmd "ffmpeg" "false" "Requerido para Remotion y HyperFrames (brew install ffmpeg)."
check_cmd "memoria" "false" "Ejecuta ./scripts/install.sh para enlazar el CLI de memoria."
check_cmd "graphify" "false" "Instala con: pipx install graphifyy o uv tool install graphifyy."
check_cmd "agent-browser" "false" "Instala con: npm install -g agent-browser."
check_cmd "hyperframes" "false" "Instala con: npm install -g hyperframes."
check_cmd "elevenlabs" "false" "Ejecuta ./scripts/install.sh (instala el CLI de ElevenLabs)."
check_cmd "flow-veo" "false" "Ejecuta ./scripts/install.sh (instala el director de Veo/Flow)."

# 2. Comprobación de Configuración de Obsidian y Espacio de Trabajo
echo -e "\n${BOLD}2. Memoria Continua y Obsidian Vault:${NC}"
VAULT_ROOT=$(PYTHONPATH="$REPO_ROOT/engine/memory/bin" python3 -c "from portable_paths import VAULT_ROOT; print(str(VAULT_ROOT))" 2>/dev/null || echo "")

if [ -n "$VAULT_ROOT" ] && [ -d "$VAULT_ROOT" ]; then
    echo -e "  [${GREEN}OK${NC}] Obsidian Vault detectado en: ${CYAN}$VAULT_ROOT${NC}"
    
    if [ -d "$VAULT_ROOT/Memoria" ]; then
        echo -e "  [${GREEN}OK${NC}] Carpeta Memoria/ presente en el Vault."
    else
        echo -e "  [${YELLOW}WARN${NC}] No se encontró '$VAULT_ROOT/Memoria'. Ejecuta ./scripts/install.sh para inicializarla."
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if [ -f "$VAULT_ROOT/Memoria/Inicio Memoria.md" ]; then
        echo -e "  [${GREEN}OK${NC}] Nota maestra 'Inicio Memoria.md' vinculada correctamente."
    fi
else
    echo -e "  [${YELLOW}WARN${NC}] Obsidian Vault no configurado o no encontrado en: $VAULT_ROOT"
    echo -e "         Ejecuta ./scripts/install.sh para ingresar la ruta de tu Vault."
    WARNINGS=$((WARNINGS + 1))
fi

# 3. Comprobación de Enlace de Habilidades en Agentes
echo -e "\n${BOLD}3. Enlace de Habilidades por Asistente de IA:${NC}"

count_skills() {
    local dir="$1"
    local label="$2"
    if [ -d "$dir" ]; then
        local count
        count=$(find -L "$dir" -mindepth 2 -maxdepth 2 -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  [${GREEN}OK${NC}] $label: ${CYAN}$count${NC} habilidades detectadas en $dir"
    else
        echo -e "  [${YELLOW}INFO${NC}] $label: directorio no configurado ($dir)"
    fi
}

count_skills "$HOME/.claude/skills" "Claude Code"
count_skills "$HOME/.agents/skills" "OpenAI Codex / ChatGPT"
count_skills "$HOME/.gemini/config/skills" "Google Antigravity"

# Catálogo del repositorio
if python3 "$REPO_ROOT/scripts/skills_tool.py" validate >/dev/null 2>&1; then
    echo -e "  [${GREEN}OK${NC}] Catálogo de skills válido ($(python3 "$REPO_ROOT/scripts/skills_tool.py" list --paths | wc -l | tr -d ' ') skills)"
else
    echo -e "  [${RED}FAIL${NC}] El catálogo tiene errores: python3 scripts/skills_tool.py validate"
    ERRORS=$((ERRORS + 1))
fi

# 4. Comprobación de Credenciales de API (Opcionales para IA Externa)
echo -e "\n${BOLD}4. Variables de Entorno y Claves de API:${NC}"
ENV_FILE="$REPO_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    check_api_key() {
        local key="$1"
        local service="$2"
        if grep -q "^${key}=.\+" "$ENV_FILE" && ! grep -q "^${key}=tu_.*_aqui" "$ENV_FILE"; then
            echo -e "  [${GREEN}OK${NC}] $service ($key configurada)"
        else
            echo -e "  [${YELLOW}INFO${NC}] $service ($key pendiente de configurar en .env)"
        fi
    }
    
    check_api_key "ELEVENLABS_API_KEY" "ElevenLabs (Audio, Voz y Efectos)"
    check_api_key "OPENAI_API_KEY" "OpenAI (ImageGen / DALL-E / GPT-4o)"
    check_api_key "GEMINI_API_KEY" "Google Gemini (Multimodal / Veo)"
else
    echo -e "  [${YELLOW}WARN${NC}] No se encontró archivo .env. Copia .env.example a .env para configurar tus API keys."
    WARNINGS=$((WARNINGS + 1))
fi

# Resumen
echo -e "\n${BOLD}======================================================================${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✔ SISTEMA 100% OPERATIVO: Todo está perfectamente configurado.${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}✔ SISTEMA LISTO CON ${WARNINGS} ADVERTENCIA(S) MENORES: Revisa los puntos amarillos arriba.${NC}"
else
    echo -e "${RED}${BOLD}✖ SE DETECTARON ${ERRORS} ERROR(ES) CRÍTICOS: Resuelve los fallos en rojo antes de continuar.${NC}"
fi
echo -e "${BOLD}======================================================================${NC}\n"
