---
name: instagram-content-suite
description: Suite de producción de contenido para Instagram de cualquier marca. Parte de un perfil de marca editable (paleta, tipografías, tono, pilares, mascotas o voceros) y genera paquetes diarios completos, carruseles 4:5 con portada destacable, prompts de video para Google Veo (toma única 5-8s) y Google Flow (bloques continuos de 10s con keyframes y diálogo medido), historias destacadas, calendario de 30 días y un linter de calidad. Usar cuando el usuario pida contenido de Instagram, Reels, carruseles, calendario editorial, grid de 3 columnas, destacadas o prompts Veo/Flow para su marca.
metadata:
  short-description: Producción de Instagram para cualquier marca (carruseles, Reels Veo/Flow, calendario)
  version: 3.0.0
---

# Instagram Content Suite

Convierte al agente en el equipo de contenido de Instagram de **la marca del usuario**: estratega, redactor, director de arte y productor de video con IA. Todo sale del **perfil de marca**; la skill no trae ninguna marca precargada.

## Paso 0 — Cargar o crear el perfil de marca (obligatorio)

1. Buscar un perfil existente, en este orden:
   - `./marca/brand-profile.md` en el proyecto actual.
   - `./brand-profile.md`.
   - Cualquier ruta que el usuario indique.
2. Si no existe, copiar [templates/brand-profile-template.md](templates/brand-profile-template.md) a `./marca/brand-profile.md` y completarlo **entrevistando al usuario** (máximo 8 preguntas, agrupadas). Si el usuario da una URL de su sitio o su @ de Instagram, extraer de ahí lo que se pueda y preguntar solo lo que falte.
3. Nunca inventar datos duros de la marca (precios, métricas, premios, clientes). Si faltan, dejar `[POR CONFIRMAR]`.

Todo lo que produce esta skill respeta el perfil: paleta, tipografías, tono, política de emojis, pilares, voceros/mascotas, hashtags y CTA.

## Comandos rápidos

| Comando / intención | Qué entrega | Referencia |
| :--- | :--- | :--- |
| `/perfil` | Crea o actualiza el perfil de marca | `templates/brand-profile-template.md` |
| `/grid` | Diseña el sistema de 3 columnas del feed (pilares + anfitriones) | `references/sistema-de-columnas.md` |
| `/calendario` | Plan de 30 días con fechas, columna, formato y tema | `references/calendario-30-dias.md` |
| `/dia [n]` | Paquete diario completo: portada, carrusel o guion, caption y prompts | `references/protocolo-entrega-por-bloques.md` |
| `/carrusel` | Carrusel de 5-7 láminas 4:5 con portada destacable | `references/carruseles-y-portadas.md` |
| `/veo` | Prompt de toma única 5-8s para Google Veo (o Kling, Runway, Luma) | `references/prompts-google-veo.md` |
| `/flow [segundos]` | Video largo en bloques de 10s con keyframes y diálogo medido | `references/prompts-google-flow-continuidad.md` |
| `/destacadas` | Portadas y guion de las historias destacadas | `references/historias-destacadas.md` |
| `/style-bible` | Biblia visual para personajes 3D o fotografía consistente | `references/style-bible-plantilla.md` |
| `/auditar [archivo]` | Linter de calidad antes de publicar | `scripts/content_validator.py` |

Los comandos son atajos de intención dentro de un mensaje (por ejemplo "calendario para octubre" o "/carrusel sobre precios"); si el usuario no los usa, inferir la intención y seguir el mismo flujo.

## Reglas de producción

1. **Una pieza, un objetivo.** Cada publicación declara su objetivo (alcance, guardado, conversación o conversión) y su CTA único.
2. **Portada destacable.** La lámina 1 o miniatura del Reel funciona sola en la cuadrícula del perfil: titular de máximo 6 palabras, sujeto centrado, zona segura para el recorte.
3. **Formatos.** Carrusel e imagen: 1080x1350 (4:5). Reel e historia: 1080x1920 (9:16). Texto mínimo 24 pt en arte final.
4. **Copy.** Gancho en las dos primeras líneas, desarrollo con PAS o AIDA (ver skill `copywriting-pro`), CTA claro y hashtags del perfil (3-8, mezcla de marca, nicho y local).
5. **Emojis.** Seguir la política del perfil (`permitidos`, `moderados` o `prohibidos`). Si están prohibidos, usar viñetas tipográficas (`•`, `▪`, `—`) y etiquetas (`[GUÍA]`, `[CASO]`).
6. **Video con IA.** Prompts de cámara en inglés; locución y textos en el idioma del perfil. Métrica de locución: 20-26 palabras por cada 10 s.
7. **Consistencia visual.** Si la marca tiene mascota o vocero, usar siempre la misma imagen ancla (ruta en el perfil) y los rasgos fijos de la style bible.
8. **Honestidad.** Nada de testimonios, cifras o logos de clientes inventados. Marcar como `[EJEMPLO]` cualquier dato ilustrativo.

## Formato de entrega

Entregar siempre en bloques independientes y numerados según [references/protocolo-entrega-por-bloques.md](references/protocolo-entrega-por-bloques.md). Si hay acceso a disco, guardar cada paquete en `./instagram/AAAA-MM-DD-slug/` con `caption.md`, `carrusel.md` y `prompts-video.md`, y ejecutar el linter.

En entornos sin terminal (ChatGPT o claude.ai), entregar los bloques en la respuesta y aplicar manualmente el checklist de [references/checklist-calidad.md](references/checklist-calidad.md).

## Linter de calidad

```bash
python3 scripts/content_validator.py ./instagram/2026-10-01-slug/caption.md --perfil ./marca/brand-profile.md
python3 scripts/content_validator.py --test
```

Revisa emojis según la política, palabras por bloque de Flow, rutas de imágenes ancla, hashtags de marca, CTA y titulares de portada demasiado largos.

## Skills complementarias

- `copywriting-pro` para ganchos y captions, `content-strategy` para pilares, `social-media-strategy` para crecimiento.
- `social-media-design` e `imagegen` para artes; `video-prompt-engineering`, `google-flow-veo-director` y `video-continuity` para video.
- `social-competitor-intelligence` para investigar qué funciona en el nicho antes de planificar el mes.
