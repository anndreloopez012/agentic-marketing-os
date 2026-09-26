# Protocolo Multi-Agente: Agentic Marketing OS (Codex, Antigravity y Claude Code)

Este repositorio y entorno de desarrollo opera bajo un protocolo de colaboración multi-agente donde **OpenAI Codex**, **Google Antigravity** y **Anthropic Claude Code** comparten la misma base de conocimiento, herramientas y memoria continua sincronizada con **Obsidian** y **Graphify**.

---

## 1. Regla Mandatoria de Inicio: Consumir Memoria Antes de Asumir o Modificar
Siempre que el usuario solicite crear una campaña, diseñar una interfaz, optimizar SEO/GEO, producir un video o modificar código:

1. **Consultar la Memoria del Proyecto**:
   - Usar la CLI local:
     ```bash
     memoria contexto <nombre-proyecto>
     memoria proyecto <nombre-proyecto>
     ```
   - O consultar las notas en el Obsidian Vault:
     - `Memoria/Inicio Memoria.md`
     - `Memoria/Contexto Operativo.md`
     - `Memoria/Proyectos Git/<nombre-proyecto>.md`

2. **Consultar Graphify para Arquitectura y Flujos**:
   - Si el proyecto cuenta con `graphify-out/graph.json`:
     ```bash
     graphify query "<pregunta sobre arquitectura, dependencias o flujos>"
     graphify path "<ComponenteA>" "<ComponenteB>"
     graphify explain "<ModuloOConcepto>"
     ```

3. **Inspección Previa de Git**:
   - Ejecutar `git status --short` antes de modificar o crear archivos. Respetar cambios locales sin confirmar del usuario.

---

## 2. Catálogo de Habilidades y Directivas por Dominio

### A. Marketing Estratégico y Copywriting
- **Copywriting**: Utilizar la habilidad `copywriting-pro` con fórmulas probadas (AIDA, PAS, BAB, StoryBrand). Todo copy debe enfocarse en conversión, claridad y dolor del cliente.
- **Estrategia y Calendarios**: Usar `content-strategy` y `social-media-strategy` para planificar pilares, clusters de contenido y tácticas multicanal.
- **Pauta Publicitaria**: Usar `paid-ads` para estructurar campañas de Meta Ads, Google Ads y TikTok Ads, calculando ROAS y ángulos de prueba.
- **Identidad de Marca**: Usar `brand-identity` para guías de estilo, tono de voz, propuestas de valor y manuales de marca.

### B. SEO y GEO (Generative Engine Optimization)
- **SEO Clásico y Técnico**: Usar `seo-expert` y `seo` para Core Web Vitals, metadatos, sitemaps XML y checklists técnicos.
- **GEO / AEO (Optimización para IA)**: Usar `geo-expert` para estructurar contenido en formato "quote-ready" para ChatGPT Search, Perplexity AI y Google AI Overviews.
- Implementar siempre esquemas JSON-LD ricos (`Organization`, `FAQPage`, `LocalBusiness`, `sameAs`).

### C. Diseño Frontend, UI/UX y Arte Visual
- **Diseño de Interfaces**: Usar `frontend-design`, `impeccable` y `ui-ux-pro-max` para interfaces modernas con jerarquía visual impecable, evitando estéticas genéricas de IA.
- **Micro-habilidades de Pulido**: Aplicar `polish`, `typeset`, `layout`, `delight`, `animate`, `colorize`, `bolder` o `quieter` según la dirección artística deseada.
- **Generación de Imágenes**: Usar `imagegen` con descriptores de iluminación, lente, composición y estilo.

### D. Producción y Edición de Video (Remotion & HyperFrames)
- **Remotion**: Cuando se trabaje con video programático en React, consultar `remotion` y sus reglas en `rules/` (timing, audio visualization, subtitles, silence detection, 3D).
- **HyperFrames**: Para composiciones ultrarrápidas y deterministas en HTML/CSS, utilizar `hyperframes-core` y workflows especializados (`product-launch-video`, `faceless-explainer`, `talking-head-recut`, `general-video`).
- **Dirección Cinematográfica de IA**: Utilizar `google-flow-veo-director`, `video-prompt-engineering` y `video-continuity` para secuencias consistentes.
- **Audio y Voz**: Utilizar `elevenlabs` para locuciones profesionales, efectos de sonido y limpieza de audio.

### E. Inspección y Automatización Web
- **Agent-Browser**: Usar `agent-browser` para navegar sitios web en vivo, extraer datos del DOM, capturar pantallas, auditar accesibilidad con axe-core y verificar formularios.

---

## 3. Regla Mandatoria de Sincronización y Cierre de Cambios
Al concluir cualquier tarea, entrega o sprint en un proyecto:

1. **Actualizar el Grafo de Conocimiento**:
   ```bash
   graphify update .
   ```
2. **Exportar hacia el Obsidian Vault**:
   ```bash
   graphify export obsidian --dir "$VAULT_ROOT/Memoria/Graphify/<nombre-proyecto>"
   ```
3. **Refrescar Índices de Memoria**:
   ```bash
   memoria refresh
   ```
4. **Registrar Decisiones o Aprendizajes**:
   ```bash
   memoria registrar <nombre-proyecto> --tipo [aprendizaje|decision|cambio|validacion] --titulo "<Título>" --texto "<Resumen técnico claro y conciso>"
   ```
5. **Estrategia de Ramas Git**:
   - Crear ramas de funcionalidad (`feature/...`).
   - Integrar en `dev`.
   - Sincronizar y confirmar en `main`.
