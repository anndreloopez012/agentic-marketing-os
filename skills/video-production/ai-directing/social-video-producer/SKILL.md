---
name: social-video-producer
description: "Suite de producción cinematográfica para crear videos de alto impacto para redes sociales (TikTok, Instagram Reels/Stories/Feed, YouTube Shorts, LinkedIn, X/Twitter) a partir de imágenes usando Google Veo (Veo 3.1, Veo 2, Gemini Omni) y ffmpeg. Garantiza 0% de distorsión en textos, tipografías y logotipos mediante arquitectura de doble capa (clean plate + lossless overlay), cumple zonas seguras (safe zones), estructura guiones con gancho viral (hook 0-2s) y aplica postproducción con transiciones, gradación de color, audio ducking y subtítulos modernos."
metadata:
  short-description: Producción de video profesional para redes sociales desde imágenes con Google Veo
---

# Social Video Producer (Google Veo & Post-Production Suite)

Esta skill convierte imágenes (fotos de producto, artes gráficos publicitarios, diapositivas de marca, banners o carruseles) en **videos dinámicos, fluidos y de nivel comercial para cualquier red social**, asegurando que **los textos, precios, logotipos y copys nunca se deformen ni alucinen**.

---

## 1. Reglas Maestras de Producción Empresarial

### Regla 1: Cero Distorsión de Textos y Logos (Arquitectura de Doble Capa)
Los modelos generativos de video (Veo, Sora, etc.) alteran y "derriten" las letras y vectores pequeños debido a la difusión latente.
Para garantizar **calidad 100% empresarial sin errores ni divagaciones**:
1. **Aislar la capa gráfica**: El script `text_preserver.py` extrae los textos y logotipos en una placa PNG transparente de 32 bits en su resolución nativa intacta.
2. **Generar el fondo limpio (Clean Plate)**: Se genera una versión del fondo donde las áreas de texto se suavizan/rellenan para que Google Veo anime el fondo con movimientos de cámara naturales (dolly, órbita, parallax, barrido de luz) sin duplicar letras.
3. **Recomposición Lossless**: `video_composer.py` superpone el texto original nítido sobre el video renderizado con entradas cinéticas elegantes (`fade_in`, `slide_in_bottom`, `pop_in` o `static_lock`).

### Regla 2: Cumplimiento Estricto de Safe Zones (Zonas Seguras)
En redes móviles (TikTok, Reels, Shorts), la interfaz del sistema (iconos de me gusta, comentarios, título, sonido) cubre zonas críticas de la pantalla:
- **TikTok / Reels (9:16 - 1080x1920)**:
  - Margen superior reservado: **160px a 180px** (no colocar títulos arriba del todo).
  - Margen inferior reservado: **340px a 380px** (reservado para pie de foto y audio).
  - Margen derecho reservado: **120px a 140px** (botones de interacción).
  - Todo el contenido clave, rostros y llamadas a la acción deben concentrarse en el centro vertical.
- **YouTube Shorts (9:16)**: Margen inferior reservado de **280px**.
- **Instagram Feed (4:5 o 1:1)**: Centrado con márgenes de seguridad de **60px**.

### Regla 3: Estructura de Retención Viral (3 Actos)
- **Acto 1: The Hook (0 a 2.5s)**: Movimiento de cámara rápido o empuje frontal (`subtle_dolly_in`), cambio visual inmediato para evitar el scroll.
- **Acto 2: The Core / Value (2.5s a 8s+)**: Tomas de ángulo cambiante (`cinematic_orbit` o `horizontal_truck`), mostrando beneficios o ángulos del producto.
- **Acto 3: The Payoff / CTA (Final)**: Estabilidad visual (`ambient_light_sweep` o `static_lock`), llamada a la acción clara y logotipo de la empresa.

---

## 2. Herramientas y Scripts Disponibles

Todos los scripts se ubican en:
`/Users/macbookpro/.gemini/config/skills/social-video-producer/scripts/`

### 1. `cli.py` (Orquestador Central)
Punto de entrada unificado para ejecutar cualquier tarea de video.

```bash
# Animar 1 imagen individual garantizando 0% distorsión de texto:
python3 /Users/macbookpro/.gemini/config/skills/social-video-producer/scripts/cli.py animate \
  --image "/ruta/a/promo.png" \
  --platform tiktok \
  --duration 6 \
  --text-animation fade_in \
  --color-preset commercial_punch \
  --output "video_tiktok.mp4"

# Interpolar transición fluida entre dos imágenes (inicio -> fin):
python3 /Users/macbookpro/.gemini/config/skills/social-video-producer/scripts/cli.py interpolate \
  --first "/ruta/a/inicio.png" \
  --last "/ruta/a/final.png" \
  --platform instagram_reels \
  --duration 6 \
  --output "transicion.mp4"

# Planificar un video completo desde varias imágenes (storyboard):
python3 /Users/macbookpro/.gemini/config/skills/social-video-producer/scripts/cli.py plan \
  --images slide1.png slide2.png slide3.png \
  --platform reels \
  --topic "Lanzamiento Nueva Colección" \
  --output "storyboard.json"

# Producir el video multi-escena final desde el storyboard:
python3 /Users/macbookpro/.gemini/config/skills/social-video-producer/scripts/cli.py produce \
  --storyboard "storyboard.json" \
  --transition fade \
  --bgm "audio/musica_fondo.mp3" \
  --output "anuncio_completo.mp4"
```

### 2. `veo_client.py` (Motor Google Veo)
Conecta directamente con la API de Google Veo sin requerir dependencias externas.
- **Modelos soportados**:
  - `veo-3.1-generate-preview` (Máxima calidad cinematográfica, resolución hasta 4K, 24fps).
  - `veo-3.1-fast-generate-preview` (Iteración ultra-rápida).
  - `veo-2.0-generate-001` (Estabilidad comprobada).
- **Manejo de variables**: Requiere `export GEMINI_API_KEY="tu-api-key"`.

### 3. `text_preserver.py` (Protector Tipográfico)
Extrae capas vectoriales y genera máscaras alpha para recomposición `ffmpeg`.

### 4. `video_composer.py` (Postproducción & Mastering)
Ensambla cortes, transiciones `xfade`, audio ducking (baja música cuando hay voz), normalización a `-14 LUFS` y gradación de color.

---

## 3. Guía de Prompts de Cinematografía para Google Veo

Para evitar deformaciones o comportamientos extraños, **los prompts para Veo deben escribirse siempre en inglés** y seguir la siguiente fórmula probada:

`[Sujeto y Acción Principal] + [Movimiento de Cámara Específico] + [Iluminación & Lente] + [Restricciones Anti-Distorsión]`

### Presets Recomendados:
1. **Dolly In Frontal (Para productos o personas)**:
   > *"Smooth, slow cinematic dolly in push camera motion. The camera glides forward gently toward the product. High optical stability, shallow depth of field, 50mm lens, studio key lighting, sharp focus on subject, continuous unbroken motion, no jitter, no warping, 24fps."*
2. **Órbita 3D (Para empaques, arquitectura o moda)**:
   > *"Smooth, continuous 15-degree slow orbital arc camera movement panning around the subject. Consistent framing, clean horizon line, soft ambient reflections, perfectly stable motion, cinematic warm lighting, 24fps."*
3. **Barrido de Luz Estático (Para imágenes con mucho texto o diagramas)**:
   > *"Static camera angle with zero camera translation. Rich dynamic lighting sweep passing across the subject: warm volumetric golden-hour ray moving softly across the scene. Subtle ambient particles in air, no morphing, no distortion, 24fps."*
4. **Pedestal Vertical (Para interfaces de app o envases altos)**:
   > *"Graceful vertical pedestal up camera movement rising steadily from bottom to top. Revealing the upper details smoothly. Fluid crane-like stabilization, commercial clean lighting, steady vertical velocity, 24fps."*

---

## 4. Presets de Red Social y Aspect Ratios

| Plataforma | Aspect Ratio | Resolución | FPS | Enfoque Principal |
| :--- | :--- | :--- | :--- | :--- |
| **TikTok** | `9:16` | 1080x1920 | 30 | Hook en 1.5s, márgenes libres a la derecha y abajo |
| **Instagram Reels** | `9:16` | 1080x1920 | 30 | Alta nitidez, colores vibrantes, margen superior 180px |
| **Instagram Stories**| `9:16` | 1080x1920 | 30 | Ritmo rápido (5s a 15s), llamada a la acción clara |
| **Instagram Feed** | `4:5` | 1080x1350 | 30 | Máximo espacio visual en feed sin cortes |
| **Feed Cuadrado** | `1:1` | 1080x1080 | 30 | Versatilidad total para Meta Ads y LinkedIn |
| **YouTube Shorts** | `9:16` | 1080x1920 | 30 | Audio a 48kHz, margen inferior seguro de 280px |
| **YouTube / Web** | `16:9` | 1920x1080 / 4K | 30 | Formato horizontal panorámico corporativo |

---

## 5. Protocolo de Ejecución Paso a Paso para el Agente

Cuando el usuario solicite crear un video a partir de una o varias imágenes:

1. **Inspeccionar los archivos de entrada**:
   - Comprobar existencia y dimensiones de las imágenes.
   - Preguntar o detectar la red social objetivo (por defecto `tiktok` o `instagram_reels` si no se especifica).
   - Identificar si las imágenes contienen textos publicitarios, logotipos o precios para activar el modo de preservación de capas.
2. **Generar la Planificación (Storyboard)**:
   - Si son varias imágenes, ejecutar `storyboard_planner.py` o `cli.py plan` para establecer el orden lógico, duraciones y transiciones.
3. **Procesar y Animar con Veo**:
   - Aplicar el aislamiento de textos si hay elementos tipográficos.
   - Llamar a `veo_client.py` con el modelo `veo-3.1-generate-preview` (o `veo-2.0-generate-001`).
4. **Postproducción y Composición**:
   - Re-ensamblar la capa tipográfica con `video_composer.py`.
   - Incorporar música de fondo (BGM) o audio si el usuario lo proporciona.
   - Aplicar gradación de color (`commercial_punch` para e-commerce/lifestyle o `tech_clean` para B2B).
5. **Entregar y Confirmar**:
   - Reportar la ruta del archivo `.mp4` final generado.
   - Confirmar resolución, duración y compatibilidad con la red social indicada.
