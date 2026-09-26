---
name: video-continuity
description: Use when the user needs to maintain visual continuity across multiple AI video clips — character consistency, style bible enforcement, scene chaining, color grading consistency, or building multi-shot sequences that feel like one coherent piece. Also use when planning a video campaign that spans multiple sessions or when the user says "mismo estilo", "siguiente escena", "continuar campaña", or "que se vea todo igual".
metadata:
  short-description: Maintain character, style, and visual continuity across multi-shot AI video campaigns.
---

# Video Continuity Skill

Garantiza que múltiples clips generados en distintas sesiones se vean como parte de una misma pieza coherente.

## Por qué la continuidad es difícil en video IA

Los modelos de video IA no tienen memoria entre sesiones. Cada generación es independiente. La continuidad debe ser **ingeniería deliberada**, no suerte.

Los tres pilares de continuidad son:
1. **Anchor de personaje** — misma imagen de referencia, siempre.
2. **Style Bible** — documento que define exactamente cómo se ve todo.
3. **Seed management** — registrar y reusar seeds que funcionaron.

---

## Style Bible: estructura mínima

Antes de generar el primer clip de una campaña, crea un Style Bible. Guárdalo en:
`~/Documents/Playground/memoria_tools/image_generation_memory.json` bajo `video_sessions > style_bible`.

```json
{
  "campaign_name": "nombre-campaña",
  "brand": "marca o proyecto",
  "character": {
    "description": "Mujer 30s, cabello oscuro, ropa business casual",
    "reference_image": "output/refs/character-main.jpg",
    "invariants": ["cabello oscuro siempre recogido", "nunca usa accesorios dorados"]
  },
  "visual_palette": {
    "primary": "#1A1A2E",
    "accent": "#E94560",
    "neutrals": "blancos cálidos, beige",
    "avoid": "verde, colores neón"
  },
  "lighting": "golden hour lateral, siempre cálido, nunca luz fría",
  "camera_movement": "dolly in o push in — nunca handheld ni movimientos bruscos",
  "aspect_ratio": "9:16",
  "style_keywords": ["cinematic", "warm", "aspirational", "premium"],
  "negative_keywords": ["harsh lighting", "cold tones", "handheld shakiness"],
  "working_seeds": [42187, 99341, 55820]
}
```

---

## Flujo de continuidad entre sesiones

### Inicio de sesión
1. Leer `image_generation_memory.json` → localizar `video_sessions` activas.
2. Abrir el Style Bible de la campaña activa.
3. Identificar: ¿qué shots ya existen? ¿qué falta generar?
4. Verificar que tienes la imagen de referencia de personaje disponible.

### Durante la sesión
1. Usar SIEMPRE la misma imagen de referencia de personaje.
2. Mantener los `style_keywords` en todos los prompts.
3. Empezar cada prompt con la misma base y solo cambiar acción/entorno.
4. Anotar el seed de cada clip que quede bien.

### Al cerrar la sesión
1. Actualizar `working_seeds` con los nuevos seeds exitosos.
2. Actualizar el Style Bible si se descubrió algo nuevo.
3. Documentar qué shots quedaron listos y cuáles faltan.
4. Registrar outputs en `output/video/[campaña]/shot-XXX.mp4`.

---

## Técnicas de encadenamiento de escenas

### Continuidad visual entre clips
El final de clip N debe conectar con el inicio de clip N+1:

```
Clip 1: personaje camina hacia cámara → termina en close-up de cara
Clip 2: inicia con close-up de cara → personaje mira hacia la derecha
Clip 3: inicia con lo que está a la derecha (entorno/objeto)
```

### Movimientos de cámara complementarios
Evita repetir el mismo movimiento en clips consecutivos — crea ritmo alternando:
```
Shot 1: dolly in (acercamiento) 
Shot 2: static (pausa/énfasis)
Shot 3: pull back (reveal/contexto)
```

### Paleta de color consistente
Describe la paleta en cada prompt aunque el estilo ya lo defina:
```
"...warm amber tones, consistent with previous shots, no cool light sources"
```

---

## Checklist pre-generación

Antes de generar cualquier clip de una campaña existente:
- [ ] Leí el Style Bible completo.
- [ ] Tengo la imagen de referencia de personaje correcta.
- [ ] El prompt incluye los `style_keywords` del Style Bible.
- [ ] El movimiento de cámara es consistente con el tono de la campaña.
- [ ] El aspect ratio es el correcto.
- [ ] Voy a anotar el seed si el resultado es bueno.

---

## Solución de problemas de continuidad

| Problema | Causa probable | Solución |
|---|---|---|
| El personaje cambia de cara entre shots | Imagen de referencia diferente o no cargada | Usar siempre la misma imagen de referencia |
| El color se ve diferente entre clips | Descripción de iluminación inconsistente | Fijar exactamente el mismo texto de iluminación |
| El estilo cambia entre sesiones | Style Bible no consultado | Leer memoria antes de cada sesión |
| Los clips no conectan bien | Transiciones no planificadas | Planificar el story arc completo antes de generar |
| Seed no reproduce el resultado | Otros parámetros cambiaron | El seed es determinista solo si TODO lo demás es igual |

---

## Gestión de outputs

Estructura de carpetas recomendada:
```
output/
  video/
    [nombre-campaña]/
      refs/          ← imágenes de referencia de personajes
      raw/           ← clips crudos de Higgsfield
      approved/      ← clips aprobados para edición
      final/         ← versión final editada
      seeds.json     ← registro de seeds exitosos
```

`seeds.json`:
```json
{
  "shots": [
    {
      "shot_id": "shot-001",
      "scene": "apertura",
      "seed": 42187,
      "prompt_hash": "abc123",
      "approved": true,
      "notes": "movimiento de cabeza natural, luz perfecta"
    }
  ]
}
```
