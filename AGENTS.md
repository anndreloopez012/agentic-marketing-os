# Agentic Marketing OS — Reglas para agentes de IA

Estas reglas aplican a **Claude Code**, **Codex / ChatGPT** y **Gemini / Antigravity** cuando trabajan en los proyectos de marketing del alumno. Todos comparten las mismas skills, la misma carpeta de marca y la misma memoria.

## 1. Antes de empezar

1. **Contexto de marca.** Busca `./marca/brand-profile.md` (y `./marca/style-bible.md`). Si no existe y la tarea produce contenido, créalo con la plantilla de la skill `instagram-content-suite`, entrevistando al usuario con máximo 8 preguntas.
2. **Memoria (si está instalada).** Si existe el comando `memoria`, consulta `memoria contexto <proyecto>`; si hay notas en el vault de Obsidian (`Memoria/`), lee `Inicio Memoria.md` y la nota del proyecto.
3. **Grafo (opcional).** Si el proyecto tiene `graphify-out/graph.json`, pregunta al grafo antes de leer muchos archivos: `graphify query "<pregunta>"`.
4. **Git.** Ejecuta `git status --short` antes de modificar archivos y respeta los cambios del usuario.

## 2. Qué skill usar

| Necesidad | Skills |
|---|---|
| Estrategia, diagnóstico de marca, buyer persona, entregables del curso | `marketing-ia-expert`, `business-analysis`, `brand-identity` |
| Copy que vende (landing, anuncios, emails, ganchos) | `copywriting-pro`, `email-marketing`, `writing-guidelines` |
| Contenido y redes | `content-strategy`, `social-media-strategy`, `instagram-content-suite`, `social-media-design` |
| Pauta pagada | `paid-ads` |
| Clientes, propuestas y proyectos | `client-management`, `proposal-writer`, `project-management` |
| Investigación de competencia | `social-competitor-intelligence`, `web-scraping-pro`, `agent-browser` |
| SEO y aparecer en respuestas de IA | `seo-expert`, `seo`, `geo-expert` |
| Landing pages y diseño web | `shape`, `frontend-design`, `impeccable`, `ui-ux-pro-max`, `web-inmersiva`, pulidores (`polish`, `typeset`, `layout`, `colorize`, `bolder`, `quieter`, `delight`, `animate`, `adapt`, `clarify`, `distill`), calidad (`audit`, `accessibility`, `harden`, `optimize`, `critique`) |
| Imágenes con IA | `imagegen`, `higgsfield` |
| Video con IA (Veo, Flow, Kling, Higgsfield) | `google-flow-veo-director`, `video-prompt-engineering`, `video-continuity`, `social-video-producer` |
| Video programático | `hyperframes` (punto de entrada), `remotion`, `product-launch-video`, `faceless-explainer`, `website-to-video`, `embedded-captions`, `motion-graphics` |
| Voz, música y efectos | `elevenlabs` |
| Memoria del proyecto | `project-memory`, `graphify` |

Lee el `SKILL.md` real de la skill antes de actuar; no la recites de memoria.

## 3. Reglas de calidad

- **Nada inventado.** No inventes cifras, testimonios, clientes, premios ni precios. Marca supuestos como `[POR CONFIRMAR]` o `[EJEMPLO]`.
- **Entregables listos para usar.** Tablas, calendarios, guiones, copies, prompts y archivos; no consejos vagos.
- **Voz de la marca.** Respeta tono, paleta, tipografías y política de emojis del perfil de marca.
- **Secretos fuera.** Nunca escribas API keys ni datos personales de clientes en notas, commits o archivos del proyecto. Las claves viven en `.env`.
- **Entregables separados de la memoria.** El código y los archivos van en la carpeta de proyectos; el vault de Obsidian guarda solo notas.

## 4. Al terminar

1. Si se confirmó una decisión (tono, oferta, audiencia, diseño), actualiza `./marca/brand-profile.md`.
2. Si la memoria está instalada: `memoria registrar <proyecto> --tipo decision|aprendizaje|cambio|validacion --titulo "..." --texto "..."`.
3. Si el proyecto usa Graphify: `graphify update .`.
4. En proyectos con Git: trabaja en ramas `feature/...`, integra en `dev` y luego en `main`.

## 5. Sin terminal (ChatGPT web, claude.ai)

Los comandos `memoria`, `graphify`, `flow-veo` y `elevenlabs` no existen ahí: entrega el resultado directamente en la conversación y, si hay que guardar algo, dale al usuario el texto listo para pegar en su nota o archivo.
