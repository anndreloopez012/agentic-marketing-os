---
name: video-prompt-engineering
description: Use when the user needs to write, optimize, or debug prompts for AI video platforms (Higgsfield, Runway, Pika, Kling, Sora, Luma). Includes prompt structure, negative prompts, camera language, lighting descriptors, motion control, and iterative refinement. Also use when a video prompt isn't working as expected or needs to be adapted between platforms.
metadata:
  short-description: Craft and optimize prompts for AI video generation across platforms.
---

# Video Prompt Engineering

Guía completa para escribir prompts efectivos en plataformas de video IA.

## Anatomía de un prompt de video

```
[SUJETO + APARIENCIA] + [ACCIÓN/MOVIMIENTO] + [ENTORNO/ESCENARIO] + 
[ILUMINACIÓN] + [MOVIMIENTO DE CÁMARA] + [ESTILO VISUAL] + [MOOD/EMOCIÓN]
```

Todos los componentes son opcionales pero el orden importa. Coloca lo más importante al inicio — los modelos de video IA dan más peso a los primeros tokens.

---

## Componentes detallados

### Sujeto
- Sé específico en apariencia: edad aproximada, ropa, expresión, postura.
- Evita pronombres ambiguos: no "she" sino "a woman in her 30s".
- Para consistencia: incluye detalles únicos que anclen la identidad visual.

```
✅ "A tall man in his 40s, dark suit, confident posture, slight smile"
❌ "A man"
```

### Acción / Movimiento
- Usa verbos de acción precisos: `walks slowly`, `turns toward camera`, `picks up`, `gestures`.
- Describe el ritmo: `slowly`, `briskly`, `suddenly`, `gracefully`.
- Para escenas estáticas: `stands still`, `holds position`, `breathes naturally`.

### Entorno
- Especifica: interior/exterior, época, lugar geográfico, condiciones climáticas.
- Agrega detalles de fondo que anclen el mood sin competir con el sujeto.

```
✅ "modern minimalist office, floor-to-ceiling windows, city skyline in background"
❌ "office"
```

### Iluminación
| Tipo | Descripción | Mood |
|---|---|---|
| `golden hour light` | Cálido, lateral | Emocional, aspiracional |
| `studio lighting` | Limpio, controlado | Profesional, producto |
| `natural daylight` | Suave, difuso | Autenticidad |
| `neon glow` | Colorido, contrastado | Urbano, nocturno |
| `dramatic side lighting` | Alto contraste | Tensión, drama |
| `soft box` | Uniforme, sin sombras duras | Comercial, belleza |
| `backlit / silhouette` | Sujeto oscuro, fondo brillante | Misterio, silueta |
| `candle/firelight` | Cálido, orgánico, parpadeante | Íntimo |

### Movimiento de cámara
(Ver higgsfield skill para lista completa)

Los más universales:
- `static shot` — no hay movimiento, máxima estabilidad
- `slow push in` — acercamiento gradual, tensión suave
- `wide establishing shot` — muestra el entorno completo
- `close-up` — foco emocional en el sujeto

### Estilo visual
```
cinematic | documentary | commercial | editorial | music video | 
social media | animation | noir | vintage | hyperrealistic | 
watercolor motion | sketch animation | low poly | vaporwave
```

### Mood / Emoción
Agrega 2-3 palabras que describan la emoción objetivo:
```
warm and hopeful | dark and mysterious | energetic and bold |
calm and introspective | luxurious and aspirational | playful and vibrant
```

---

## Diferencias por plataforma

| Plataforma | Fortaleza | Prompt style |
|---|---|---|
| **Higgsfield** | Character lock, cinematografía | Descriptivo, cámara explícita |
| **Runway Gen-3** | Calidad fotorrealista, edición | Técnico, referencia de imagen |
| **Pika** | Rápido, versátil | Corto y directo |
| **Kling** | Movimiento físico realista | Acciones físicas detalladas |
| **Luma Dream Machine** | Transiciones fluidas | Temporal + espacial |
| **Sora** | Comprensión de mundo | Narrativo, storytelling |

### Adaptación entre plataformas
Para adaptar un prompt de Higgsfield a Runway:
1. Mantén sujeto + acción + entorno + iluminación.
2. Elimina el movimiento de cámara explícito (Runway lo infiere o lo controlas diferente).
3. Agrega referencia de imagen si tienes.
4. Reduce longitud del prompt en un 30%.

---

## Negative prompts (cuándo y cómo)

Plataformas que los soportan: Runway, algunas versiones de Pika.
Higgsfield: no tiene campo de negative prompt — incorpora las restricciones en el prompt positivo.

**Para prompt positivo (Higgsfield y plataformas sin negative):**
```
"...smooth motion, consistent lighting, sharp focus, no flickering, 
no distortion, natural movement"
```

**Negative prompts universales:**
```
blurry, deformed hands, extra fingers, flickering, artifacts, 
low quality, watermark, text overlay, overexposed, underexposed,
jumpcuts, inconsistent lighting, bad anatomy
```

---

## Iteración sistemática

Cuando el resultado no es el esperado, cambia UN solo elemento por iteración:

1. **Problema de sujeto** → modifica descripción del personaje o acción.
2. **Problema de movimiento** → cambia el movimiento de cámara.
3. **Problema de calidad** → agrega modificadores de calidad al final.
4. **Problema de estilo** → cambia el estilo visual.
5. **Problema de mood** → cambia los adjetivos emocionales.

Registra qué cambió y el resultado — esto construye tu biblioteca de prompts que funciona.

---

## Biblioteca de prompts de referencia

### Producto / E-commerce
```
A [product name] sits on [surface], [background], 
studio lighting with soft shadows, [orbit/dolly] movement, 
commercial style, premium and minimal, sharp focus
```

### Personaje aspiracional
```
A [descripción persona] [acción] in [lugar], 
golden hour light, slow push in, cinematic, 
[emoción objetivo], 4K quality, film grain
```

### Establishing shot de marca
```
Wide shot of [location that represents brand], 
[time of day] light, aerial pull back, 
[brand style], establishing atmosphere
```

### Testimonial / Social proof
```
A [demographic] speaks directly to camera with a warm smile, 
modern interior background, natural daylight, static shot, 
documentary style, authentic and relatable
```

### Reels de producto
```
[Product] appears in frame from [direction], 
[background color/texture], studio lighting, 
orbit [left/right], commercial, aspect ratio 9:16, 
bold and attention-grabbing
```
