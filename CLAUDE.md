# Protocolo para Claude Code: Agentic Marketing OS

Este archivo instruye a **Claude Code** para operar en perfecta sincronía con **OpenAI Codex** y **Google Antigravity** sobre los proyectos de marketing, video, diseño y memoria continua del usuario.

---

## 1. Reglas Primarias de Comportamiento

1. **Revisar Memoria en Obsidian Antes de Empezar**:
   - Ejecuta `memoria contexto <proyecto>` o revisa notas en el Obsidian Vault configurado (`$VAULT_ROOT/Memoria`).
   - Si existe `graphify-out/graph.json`, utiliza `graphify query "<pregunta>"` para entender la arquitectura antes de leer código redundante.

2. **Inspección Previa en Git**:
   - Ejecuta `git status --short` antes de modificar o crear archivos.

3. **Uso de Habilidades Disponibles**:
   - **Marketing & Copy**: `copywriting-pro`, `content-strategy`, `email-marketing`, `paid-ads`, `social-media-strategy`, `brand-identity`, `client-management`.
   - **SEO & GEO**: `seo-expert`, `seo`, `geo-expert` (Optimización para Perplexity, ChatGPT Search y Google AI Overviews).
   - **Diseño & UI**: `frontend-design`, `impeccable`, `ui-ux-pro-max`, `design-system-builder`, `tailwind-css-patterns`, `shadcn`. Micro-pulido con `polish`, `typeset`, `delight`, `animate`.
   - **Video & Audio**: Remotion (`remotion` con reglas en `rules/`), HyperFrames (`hyperframes-core`, `product-launch-video`, etc.), `google-flow-veo-director`, `elevenlabs`.
   - **Navegación Web**: `agent-browser` para interactuar con páginas, tomar capturas y verificar resultados.
   - **Scraping e Inteligencia de Competidores**: `web-scraping-pro` (extracción a Markdown, precios, sitemaps) y `social-competitor-intelligence` (espionaje en Meta Ad Library, TikTok Creative Center, YouTube y LinkedIn).

4. **Regla de Cierre y Sincronización**:
   - Al finalizar, ejecuta:
     ```bash
     graphify update .
     graphify export obsidian --dir "$VAULT_ROOT/Memoria/Graphify/<proyecto>"
     memoria refresh
     memoria registrar <proyecto> --tipo [aprendizaje|decision|cambio] --titulo "..." --texto "..."
     ```
   - Trabaja por ramas (`feature/...` -> `dev` -> `main`).
