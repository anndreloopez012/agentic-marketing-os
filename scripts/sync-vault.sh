#!/usr/bin/env bash
# ==============================================================================
# Agentic Marketing OS - Vault & Knowledge Graph Synchronization Script
# ==============================================================================

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
NC="\033[0m"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETTINGS_FILE="$REPO_ROOT/engine/memory/config/settings.json"

if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Configuración no encontrada. Ejecuta ./scripts/install.sh primero."
    exit 1
fi

VAULT_ROOT=$(python3 -c "import json; print(json.load(open('$SETTINGS_FILE')).get('vault_root', ''))" 2>/dev/null)
PROJECT_DIR="${1:-$(pwd)}"
PROJECT_NAME="$(basename "$PROJECT_DIR")"

echo -e "${CYAN}${BOLD}🔄 Sincronizando proyecto '${PROJECT_NAME}' con Obsidian y Graphify...${NC}"

# 1. Actualizar grafo AST
echo -e "${BLUE}[1/3] Actualizando grafo de conocimiento con Graphify...${NC}"
cd "$PROJECT_DIR"
if [ -d "graphify-out" ]; then
    graphify update . || graphify .
else
    graphify .
fi

# 2. Exportar grafo hacia Obsidian
if [ -n "$VAULT_ROOT" ] && [ -d "$VAULT_ROOT/Memoria" ]; then
    EXPORT_DIR="$VAULT_ROOT/Memoria/Graphify/$PROJECT_NAME"
    echo -e "${BLUE}[2/3] Exportando grafo hacia Obsidian (${EXPORT_DIR})...${NC}"
    mkdir -p "$EXPORT_DIR"
    graphify export obsidian --dir "$EXPORT_DIR" || true
else
    echo "No se encontró el directorio Memoria en el Vault ($VAULT_ROOT)."
fi

# 3. Refrescar índices del sistema de memoria
echo -e "${BLUE}[3/3] Refrescando índices y memoria global...${NC}"
memoria refresh || true

echo -e "${GREEN}${BOLD}✔ Sincronización completada exitosamente.${NC}\n"
