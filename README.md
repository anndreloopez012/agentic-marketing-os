# Agentic Marketing OS

### Tu equipo de marketing con IA: estrategia, copy, redes, pauta, SEO/GEO, diseño web, video y memoria

**Funciona con:** Claude Code · claude.ai · Codex (con tu cuenta de ChatGPT) · ChatGPT · Gemini / Antigravity

[![Licencia](https://img.shields.io/badge/licencia-MIT-green.svg)](./LICENSE)
[![Skills](https://img.shields.io/badge/skills-89-blue.svg)](./docs/CATALOGO.md)
[![Estándar](https://img.shields.io/badge/formato-Agent%20Skills-8A2BE2.svg)](https://agentskills.io)

---

## Qué es

Un paquete de **skills** (instrucciones expertas que el asistente carga solo cuando las necesita) para trabajar el marketing de tu empresa con IA de principio a fin:

- Diagnóstico de marca, cliente ideal, propuesta de valor y oferta.
- Copy que vende: landing pages, anuncios, emails, ganchos, WhatsApp.
- Contenido para redes: pilares, calendario de 30 días, carruseles, Reels con Google Veo y Flow.
- Campañas en Meta, Google, TikTok y LinkedIn Ads.
- SEO y **GEO** (que ChatGPT, Perplexity y Google AI Overviews citen tu marca).
- Landing pages con diseño profesional y revisión de calidad.
- Video programático (HyperFrames, Remotion), voz y música con ElevenLabs.
- Investigación de competencia y memoria de tus proyectos en Obsidian.

Todas las skills siguen el estándar abierto **Agent Skills** (`SKILL.md`): las mismas carpetas sirven para Claude y para ChatGPT/Codex. Ninguna trae datos de una empresa en particular; cada skill trabaja con **tu** perfil de marca.

- 📚 [Catálogo completo de skills](./docs/CATALOGO.md)
- 🎓 [Guía del alumno paso a paso](./docs/GUIA-ALUMNO.md)

---

## Instalación: elige tu herramienta

| Usas… | Método | Tiempo |
|---|---|---|
| **Claude Code** (terminal, app de escritorio o VS Code) | [A. Plugins](#a-claude-code-con-plugins-lo-más-fácil) o [B. Instalador](#b-instalador-completo-claude-code--codex--gemini) | 2 min |
| **Codex** (CLI, app o extensión; entras con tu cuenta de ChatGPT) | [B. Instalador](#b-instalador-completo-claude-code--codex--gemini) | 5 min |
| **ChatGPT** en la web o app | [C. Subir skills a ChatGPT](#c-chatgpt-web-o-app) | 5 min |
| **claude.ai** en la web o app | [D. Subir skills a claude.ai](#d-claudeai-web-o-app) | 5 min |
| **Windows** sin WSL | [E. Windows](#e-windows) | 5 min |

### A. Claude Code con plugins (lo más fácil)

Dentro de Claude Code:

```text
/plugin marketplace add anndreloopez012/agentic-marketing-os
/plugin install marketing@agentic-marketing-os
```

Instala los grupos que necesites (cada uno es independiente):

| Plugin | Incluye |
|---|---|
| `marketing` | estrategia, copy, pauta, email, contenido, Instagram, clientes y propuestas |
| `seo-geo` | SEO técnico/local y GEO |
| `research` | scraping e inteligencia de competencia |
| `design` | landing pages, UI/UX, imágenes con IA y pulido visual |
| `video-audio` | Veo/Flow, Higgsfield, HyperFrames, Remotion y ElevenLabs |
| `browser` | navegador autónomo para capturas y QA |
| `memory` | memoria con Obsidian y Graphify |

Con plugins, las skills se invocan con prefijo (`/marketing:copywriting-pro`), aunque también se activan solas según lo que pidas. Para actualizar: `/plugin marketplace update agentic-marketing-os`.

### B. Instalador completo (Claude Code + Codex + Gemini)

Instala las skills en todos tus asistentes, crea la memoria en Obsidian y deja listos los comandos `memoria`, `elevenlabs`, `flow-veo`, `graphify`, `agent-browser` y `hyperframes`. HyperFrames, agent-browser, ElevenLabs y flow-veo quedan **dentro del bundle** (`.tools/` y `.venv-tools/` en la carpeta del repo), sin instalaciones globales. Funciona en macOS, Linux y Windows con WSL.

**Requisitos:** Git y Python 3.10+. Para video: Node.js 20+ y FFmpeg.

```bash
# macOS
brew install git python node ffmpeg
# Ubuntu / Debian / WSL
sudo apt update && sudo apt install -y git python3 python3-venv nodejs npm ffmpeg
```

```bash
cd ~/Documents
git clone https://github.com/anndreloopez012/agentic-marketing-os.git
cd agentic-marketing-os
./scripts/install.sh
```

El instalador pregunta tres cosas: dónde está tu vault de Obsidian (si no tienes, lo crea), dónde guardarás tus proyectos y qué asistentes usas.

| Asistente | Dónde quedan las skills |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex (CLI, app, extensión) | `~/.agents/skills/` |
| Gemini / Antigravity | `~/.gemini/config/skills/` |

Opciones útiles:

```bash
./scripts/install.sh --yes                       # sin preguntas, todo por defecto
./scripts/install.sh --agents claude,codex       # solo esos asistentes
./scripts/install.sh --copy                      # copia en vez de enlazar
./scripts/install.sh --codex-legacy              # además en ~/.codex/skills (versiones antiguas de Codex)
./scripts/install.sh --uninstall                 # quita todo lo instalado
./scripts/doctor.sh                              # diagnóstico
```

Las skills quedan **enlazadas** al repositorio: para actualizarlas basta con `git pull`. Si ya tenías una skill con el mismo nombre, el instalador la respeta.

Después, agrega tus claves en `.env` (solo las de los servicios que uses):

| Variable | Para qué | Dónde se obtiene |
|---|---|---|
| `ELEVENLABS_API_KEY` | voz, efectos y música | [elevenlabs.io](https://elevenlabs.io/app/developers/api-keys) |
| `OPENAI_API_KEY` | generación de imágenes (`imagegen`) | [platform.openai.com](https://platform.openai.com/api-keys) |
| `GEMINI_API_KEY` | video con Veo por API | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| `VERCEL_TOKEN` | publicar landing pages | [vercel.com](https://vercel.com/account/tokens) |

Reinicia Claude Code o Codex. En Codex puedes mencionar una skill con `$copywriting-pro`.

### C. ChatGPT web o app

**Con Skills en ChatGPT** (planes que tienen Skills habilitadas):

1. Descarga los zips desde [Releases](https://github.com/anndreloopez012/agentic-marketing-os/releases) (`agentic-marketing-os-skills.zip` trae todos) o genéralos tú con `python3 scripts/skills_tool.py package` (quedan en `dist/skills/`).
2. En ChatGPT abre **Skills → Crear → Subir desde tu computadora** y sube el zip de cada skill que quieras. Empieza por `marketing-ia-expert`, `instagram-content-suite`, `copywriting-pro`, `content-strategy`, `paid-ads`, `seo-expert` y `geo-expert`.
3. Úsalas pidiendo la tarea o mencionándolas con `@nombre-de-la-skill`.

**Sin Skills** (cualquier plan con Proyectos):

1. Descarga `chatgpt-proyecto.zip` de Releases o genera `dist/chatgpt-proyecto/` con el comando anterior.
2. Crea un **Proyecto** en ChatGPT, pega el texto de `INSTRUCCIONES-DEL-PROYECTO.md` en sus instrucciones y sube como archivos `marketing.md` y `seo-geo.md` (y las demás categorías que necesites).
3. Sube también tu `brand-profile.md` cuando lo tengas.

### D. claude.ai web o app

1. Activa **Ajustes → Capacidades → Skills** (requiere la ejecución de código activada).
2. Sube los zips de `dist/skills/` (o de Releases) uno por uno.
3. Crea un Proyecto para tu marca y sube ahí tu `brand-profile.md`.

### E. Windows

Lo recomendado es instalar [WSL](https://learn.microsoft.com/windows/wsl/install) y usar el método B. Si prefieres Windows nativo (solo skills, sin memoria ni CLIs):

```powershell
git clone https://github.com/anndreloopez012/agentic-marketing-os.git
cd agentic-marketing-os
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

---

## Primeros pasos

1. Abre tu asistente dentro de tu carpeta de proyectos (por ejemplo `~/Documents/MarketingProjects/mi-marca`).
2. Pide: **"Crea el perfil de marca de mi empresa"**. Queda en `marca/brand-profile.md` y todas las skills lo usan desde ahí.
3. Sigue la [Guía del alumno](./docs/GUIA-ALUMNO.md): diagnóstico → contenido → campañas → sistema semanal → proyecto final.

Ejemplos:

> Con marketing-ia-expert haz el diagnóstico de mi marca y 3 buyer personas.
>
> Haz mi calendario de Instagram de 30 días con 3 columnas.
>
> Arma un Reel de 30 segundos en bloques de 10 s para Google Flow sobre mi oferta.
>
> Estructura una campaña de Meta Ads de 7 días con 10 anuncios.
>
> Crea una landing para mi oferta y optimízala para Google y para ChatGPT.

---

## Skills destacadas

| Skill | Qué hace |
|---|---|
| `marketing-ia-expert` | Método del curso: diagnóstico, personas, oferta, embudo, campañas y reportes con estándares de entrega. |
| `instagram-content-suite` | Perfil de marca, grid de 3 columnas, calendario de 30 días, carruseles, Reels Veo/Flow, destacadas y linter. |
| `copywriting-pro` | Copy de respuesta directa con AIDA, PAS, BAB y StoryBrand. |
| `paid-ads` | Estructura, audiencias, creatividades y métricas para Meta, Google, TikTok y LinkedIn Ads. |
| `geo-expert` / `seo-expert` | Posicionamiento en Google y en motores de respuesta de IA. |
| `google-flow-veo-director` | Director de video con IA: prompts de 7 capas y secuencias con continuidad (incluye el CLI `flow-veo`). |
| `social-competitor-intelligence` | Qué anuncios y contenidos le funcionan a tu competencia. |
| `frontend-design` + `impeccable` + `audit` | Landing pages con diseño profesional y control de calidad. |
| `elevenlabs` | Locuciones, efectos y música (incluye el CLI `elevenlabs` / `el`). |

Lista completa con enlaces: [docs/CATALOGO.md](./docs/CATALOGO.md).

---

## Memoria con Obsidian (opcional)

El instalador crea en tu vault:

```
Tu-Vault/Memoria/
├── Inicio Memoria.md       ← punto de entrada para los agentes
├── Contexto Operativo.md   ← proyectos activos y prioridades
├── Bitacora/               ← registro cronológico (memoria registrar)
├── Proyectos Git/          ← una nota por proyecto
├── Decisiones/             ← decisiones confirmadas
├── Marcas/                 ← notas de marca
├── Graphify/               ← grafos exportados
└── Skills/                 ← inventario de skills
```

Tus entregables (landing pages, videos, campañas) viven en tu carpeta de proyectos; el vault solo guarda notas.

```bash
memoria contexto mi-marca
memoria registrar mi-marca --tipo decision --titulo "Tono de voz" --texto "Cercano, sin tecnicismos"
memoria refresh
./scripts/sync-vault.sh ~/Documents/MarketingProjects/mi-marca   # grafo + exportación a Obsidian
```

---

## Estructura del repositorio

```
agentic-marketing-os/
├── skills/                     ← 89 skills por categoría (formato Agent Skills)
│   └── <categoría>/<skill>/
│       ├── SKILL.md            ← instrucciones (Claude, Codex, ChatGPT, Gemini)
│       ├── agents/openai.yaml  ← metadatos para Codex / ChatGPT
│       └── references/ scripts/ templates/ assets/
├── .claude-plugin/             ← marketplace de plugins para Claude Code
├── engine/memory/              ← CLI `memoria` y motor de Obsidian + Graphify
├── templates/vault/            ← notas iniciales del vault
├── scripts/                    ← install.sh, install.ps1, doctor.sh, sync-vault.sh, skills_tool.py
├── docs/                       ← catálogo y guía del alumno
└── AGENTS.md · CLAUDE.md · GEMINI.md  ← reglas compartidas para los agentes
```

---

## Para instructores: mantenimiento

```bash
python3 scripts/skills_tool.py validate -v     # frontmatter, nombres, datos personales o claves
python3 scripts/skills_tool.py openai-yaml     # metadatos de Codex/ChatGPT para skills nuevas
python3 scripts/skills_tool.py marketplace     # regenera .claude-plugin/marketplace.json
python3 scripts/skills_tool.py catalog         # regenera docs/CATALOGO.md
python3 scripts/skills_tool.py package         # zips para ChatGPT / claude.ai en dist/
```

- Para agregar una skill: crea `skills/<categoría>/<nombre>/SKILL.md` con `name` igual al nombre de la carpeta y una `description` que diga cuándo usarla; luego ejecuta los comandos de arriba.
- Al crear un tag `vX.Y.Z`, GitHub Actions publica los zips en Releases. Cada push valida el catálogo y hace una instalación de prueba.
- Crea un archivo local `.privacy-denylist` (no se sube) con nombres de tu empresa o clientes, uno por línea: `validate` falla si alguno aparece en el repositorio.

---

## Licencia y créditos

Distribuido bajo licencia **MIT** ([LICENSE](./LICENSE)). Algunas skills incluyen su propia licencia en su carpeta.

Reconocimiento a los proyectos abiertos integrados: [Remotion](https://remotion.dev), HyperFrames, Agent-Browser, Graphify, ElevenLabs, Tailwind CSS, shadcn/ui e Impeccable. Las técnicas de copywriting se basan en los clásicos de respuesta directa (Eugene Schwartz, John Caples, Claude Hopkins, Gary Halbert, Dan Kennedy) y en StoryBrand de Donald Miller.
