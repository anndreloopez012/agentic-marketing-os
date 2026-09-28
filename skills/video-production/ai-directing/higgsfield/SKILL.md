---
name: higgsfield
description: Use when the user wants to generate AI video with Higgsfield — character-consistent video clips, cinematic camera movements, style transfer, actor locking, scene chaining, or building video campaigns with continuity. Includes workflow for single shots, multi-shot sequences, and full campaign production. Also use when the user says "generar video con Higgsfield", "hacer un reel", "video con personaje consistente", "cámara cinematográfica", or "campaña de video IA".
metadata:
  short-description: AI video generation with Higgsfield — character lock, cinematic motion, and campaign continuity.
---

# Higgsfield Skill

Higgsfield es una plataforma de generación de video IA especializada en **character consistency** (actor locking) y **movimientos de cámara cinematográficos**. Permite crear clips de video de alta calidad que mantienen identidad de personaje entre tomas — ideal para campañas, reels, narrativas y contenido de marca.

## Contexto obligatorio antes de generar

1. Consulta la memoria de continuidad de video antes de cualquier generación:
   - Lee `./marca/image_generation_memory.json` en el proyecto actual (créalo si no existe) — contiene el style bible activo.
   - Si existe `./marca/style-bible.md` o `./marca/brand-profile.md`, léelos para respetar la identidad visual de la marca.
   - Si el alumno usa la memoria de Obsidian, revisa `Memoria/Herramientas/Higgsfield - Panel.md` en su vault para campañas activas y personajes registrados.
2. Si el usuario menciona "el mismo personaje", "continuar la campaña", "siguiente escena" o "mismo estilo", reutiliza los anchors del memory file sin reinventar.
3. Después de cada sesión de generación, actualiza el memory file con los resultados.

## Capacidades principales de Higgsfield

### 1. Character Lock (Actor Consistency)
- Sube una imagen de referencia del personaje → Higgsfield lo bloquea para todas las tomas de esa sesión.
- Funciona con personas reales, personajes estilizados, y avatares.
- Para campañas: usa siempre la misma imagen de referencia de actor.

### 2. Movimientos de cámara cinematográficos
Disponibles como parámetros en el prompt:

| Movimiento | Descripción | Uso ideal |
|---|---|---|
| `dolly in` | Cámara avanza hacia el sujeto | Revelar emoción, énfasis |
| `dolly out` | Cámara retrocede | Reveal de entorno, distanciamiento |
| `orbit left/right` | Cámara gira alrededor del sujeto | Mostrar producto o personaje |
| `crane up/down` | Cámara sube/baja | Transición de escena, grandiosidad |
| `push in` | Zoom dramático hacia el sujeto | Clímax emocional |
| `pull back` | Zoom out dramático | Reveal, contexto |
| `tracking shot` | Cámara sigue al sujeto en movimiento | Acción, dinámica |
| `aerial/drone` | Vista aérea descendente | Establishing shots |
| `static` | Sin movimiento de cámara | Diálogo, estabilidad |
| `handheld` | Movimiento ligero orgánico | Autenticidad, documental |

### 3. Estilos de video disponibles
- `cinematic` — iluminación de película, profundidad de campo
- `documentary` — naturalista, light handheld
- `commercial` — limpio, alto contraste, marca
- `social media` — aspect ratio 9:16, energía rápida
- `music video` — ritmo visual, efectos, cortes creativos
- `fashion film` — estética editorial, slow motion
- `product showcase` — macro, studio lighting, fondo neutro

### 4. Parámetros de control
- **Aspect ratio:** 16:9 (widescreen), 9:16 (vertical/reels), 1:1 (square)
- **Duración:** depende del modelo; Seedance 2.5 acepta de 4 a 30 s (consultar con `models_explore`)
- **Motion intensity:** low / medium / high
- **Seed:** para reproducibilidad exacta (registra siempre el seed usado)

---

## Workflow completo de producción

### Shot único
1. Define personaje y sube imagen de referencia (si hay actor lock).
2. Escribe el prompt siguiendo la estructura (ver abajo).
3. Selecciona movimiento de cámara, estilo y aspect ratio.
4. Genera → valida → itera ajustando un parámetro a la vez.
5. Registra: seed, prompt final, movimiento, estilo, output path.

### Multi-shot / Secuencia
1. Define el story arc: cuántas escenas, qué progresa entre ellas.
2. Fija el personaje en todas las tomas (misma imagen de referencia).
3. Genera cada shot con el workflow de shot único.
4. Valida continuidad visual entre clips antes de exportar.
5. Usa transiciones naturales: el final de cada clip debe conectar con el inicio del siguiente.

### Campaña completa
1. Crea un **Style Bible** (ver references/style-bible-template.md).
2. Registra: personaje, paleta, tipografía, tono emocional, movimientos permitidos.
3. Produce en lotes: agrupa shots por escena, no por fecha.
4. Mantén el memory file actualizado después de cada sesión.
5. Para variantes A/B: cambia UN solo parámetro por variante.

---

## Generar desde Claude con el conector MCP

Probado en una campaña real con mascota animada (~530 créditos). El CLI puede decir
`Not authenticated`, pero las herramientas del conector funcionan.

1. **Saldo y costo**: `balance`; `get_cost: true` en `generate_video` / `generate_image`
   (no funciona dentro de un lote). Referencia: Seedance 2.5 1080p 5 s = 45, 8 s = 72,
   720p 5 s = 32.5; Nano Banana Pro = 2; `outpaint_image` = 2; recorte de video ≈ 1.
2. **Subir la referencia una vez**: `media_upload` → `curl -X PUT` al `upload_url` →
   `media_confirm`. Reutilizar el `media_id` en todo.
3. **Imágenes base primero** con `nano_banana_pro` (rol `image_references`) para validar
   identidad y encuadre antes de gastar en video.
4. **Video desde imagen**: `seedance_2_5` con `mode: 'omni_reference'` y `start_image`
   (y `end_image` para terminar en una pose). El valor puede ser el id de un trabajo anterior.
5. **Lotes**: `generate_video_batch` / `generate_image_batch` y esperar con `jobs_wait`.
   - Plan plus: **máximo 6 trabajos a la vez** (el séptimo da 429).
   - Si vuelve "Preset … was recommended", repetir con `declined_preset_id`.
6. **Descargar en cuanto termina** cada trabajo: el conector puede desconectarse.
7. **Recorte de fondo** (`remove_background`, video): entrega H.264 **sin alfa**, con el
   sujeto sobre negro. Guardar también el original para reconstruir la transparencia.

Lo que funcionó para identidad: abrir el prompt con "Keep the character exactly as in the
reference image" y enumerar sus piezas; cerrar con "No readable text". Para animaciones que
controla una persona (mirada que sigue al cursor, encendido por scroll): cámara fija, un solo
movimiento continuo y todos los clips partiendo del mismo fotograma.

**Si los medios van a una página web** (mascota interactiva, historia por scroll, portada
con video), seguir la skill `web-inmersiva`: guion de medios, plantillas de prompt, scripts
para fotogramas con alfa y bucles, y QA en Chrome real.

---

## Estructura de prompt para Higgsfield

```
[SUJETO] [ACCIÓN] [ENTORNO] [ILUMINACIÓN] [MOVIMIENTO DE CÁMARA] [ESTILO] [MOOD]
```

### Ejemplo básico:
```
A young woman in a white linen dress walks through a sunlit coffee shop,
warm morning light, dolly in, cinematic, warm and intimate
```

### Ejemplo de producto:
```
A sleek black smartphone on a marble surface rotates slowly,
studio lighting with soft shadows, orbit right, commercial style, premium and minimal
```

### Ejemplo de campaña de marca:
```
A confident entrepreneur in a modern office looks directly at camera,
golden hour light through large windows, push in, cinematic, empowering and aspirational
```

### Modificadores de calidad (agrega al final):
- `sharp focus, high detail, 4K quality`
- `professional cinematography, film grain`
- `smooth motion, no artifacts`
- `consistent lighting throughout`

### Palabras a evitar (degradan calidad):
- `cartoon, anime, painting` (a menos que sea el estilo deseado)
- `blurry, low quality, deformed`
- Descripciones contradictorias de iluminación

---

## Integración con imagen

Antes de video, considera el pipeline completo:
1. **Imagegen skill** → genera imagen de referencia del personaje o escena.
2. **Higgsfield** → anima esa imagen o úsala como anchor de actor.
3. Esto garantiza máxima coherencia visual entre imagen y video.

---

## Memory y continuidad

Después de cada sesión, actualiza estos archivos:

**`./marca/image_generation_memory.json`** — agrega:
```json
{
  "video_sessions": [
    {
      "date": "YYYY-MM-DD",
      "platform": "higgsfield",
      "campaign": "nombre-de-campaña",
      "character_reference": "ruta/a/imagen.jpg",
      "style_bible": { ... },
      "shots": [
        {
          "scene": 1,
          "prompt": "...",
          "camera": "dolly in",
          "style": "cinematic",
          "seed": 12345,
          "output": "output/video/shot-001.mp4"
        }
      ]
    }
  ]
}
```

**Obsidian:** actualiza `Memoria/Herramientas/Higgsfield - Panel.md` en tu vault de Obsidian (si usas la memoria) con:
- Campaña activa, personajes registrados, seeds usados, resultados clave.
- Créditos antes y después, y dónde quedaron los crudos con los ids de cada trabajo
  (por ejemplo `trabajos-higgsfield.tsv` junto a los archivos).

---

## Limitaciones a tener en cuenta

- El CLI `higgsfield` puede no tener sesión; el conector MCP de Higgsfield sí permite generar desde Claude (ver arriba).
- El actor lock funciona mejor con imágenes de frente, buena iluminación, fondo limpio.
- Seedance 2.5 puede generar audio (`generate_audio`, activo por defecto); para medios de una web se apaga porque los videos van silenciados.
- Los clips de 8s consumen más créditos que los de 4s.
- Para máxima consistencia entre shots, usa el mismo seed cuando sea posible.
- Prompts muy largos (>100 palabras) pueden reducir la coherencia.

---

## Comandos de referencia

Cuando el usuario pide usar Higgsfield, el flujo de Claude es:
1. Leer memoria de continuidad.
2. Construir el prompt usando la estructura correcta.
3. Sugerir movimiento de cámara adecuado al objetivo.
4. Entregar: prompt listo para pegar en Higgsfield + parámetros recomendados + notas de continuidad.
5. Después de confirmación del usuario, actualizar memory file.

Si el conector MCP de Higgsfield está disponible, Claude genera directamente (ver "Generar desde Claude con el conector MCP"). Si no lo está, entrega prompts listos y parámetros optimizados para que el usuario los ejecute en la web.
