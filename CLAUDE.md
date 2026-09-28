# Agentic Marketing OS — Claude Code

@AGENTS.md

## Notas para Claude Code

- Las skills se instalan en `~/.claude/skills` (con `./scripts/install.sh`) o como plugins del marketplace `agentic-marketing-os` (en ese caso se invocan con prefijo, por ejemplo `/marketing:copywriting-pro`).
- Si una skill trae scripts, ejecútalos desde la carpeta de la skill; no copies su código al proyecto salvo que el usuario lo pida.
- Para ver o probar páginas web usa el navegador disponible en la sesión o la skill `agent-browser`.
