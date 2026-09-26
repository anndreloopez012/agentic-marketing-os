---
name: web-inmersiva
description: Build immersive, eye-catching web pages around an animated brand mascot, character or product using AI-generated media (Higgsfield) — a mascot that follows the cursor with its gaze and reacts to clicks, scroll-driven storytelling with pinned sections where the subject lights up piece by piece, cinematic looping hero videos, role galleries, plus real-Chrome QA. Use it whenever the user wants an "immersive" page or landing section, scrollytelling, something that reacts to the mouse, a mascot or character animated on a website, a page that explains a mascot or product piece by piece, or Higgsfield media inside a web page — even if they never say "immersive". Also to turn generated clips into transparent WebP frame sequences. Spanish triggers include "página inmersiva", "full inmersiva", "que reaccione al mouse", "anima la mascota", "que resalte nuestra mascota", "explica el porqué de cada cosa". Not for final video files (hyperframes/remotion) or media without a page (higgsfield-generate).
---

# Web inmersiva con personajes y medios generados

Receta probada en dos proyectos reales: la web de SoftPlus GT (Nimbo+, hyperlapse por scroll,
Astro + GSAP) y Kivo de KINVO (React + Vite + framer-motion: mascota que sigue el cursor y una
página que la explica pieza por pieza). Aquí está lo que funcionó, **por qué**, y las trampas
que solo aparecieron al ejecutar. El caso completo está en
[references/caso-kivo.md](references/caso-kivo.md).

## Principios

1. **Toca solo la página pedida.** Las capturas del usuario marcan el lugar exacto. Si un
   componente se usa en otras pantallas (chat, asistente, CMS), crea uno nuevo en vez de
   modificarlo: la petición es sobre esta página, no sobre las demás.
2. **El contenido sale de la fuente de la marca.** Lee el manual o brief antes de escribir.
   Si una pieza del personaje no tiene significado oficial, no le inventes uno. Lo que es
   guía interna (checklists, "qué no decir") no se publica.
3. **La interacción se hace con fotogramas, no con video reproducido.** Un `<video>` no se
   adelanta fotograma a fotograma de forma fiable en Safari/iOS, y los videos con alfa no son
   portables (WebM con alfa falla en Safari, HEVC con alfa en Chrome). Una secuencia WebP con
   alfa pintada en `<canvas>` funciona en todos y permite que el puntero o el scroll decidan
   el fotograma.
4. **El movimiento siempre tiene alternativa**: movimiento reducido, pantallas táctiles,
   pestaña oculta y conexiones lentas tienen su versión (estática, lista o ligera).
5. **Verifica ejecutando en Chrome real.** Leer el código engaña: en estos proyectos varios
   "bugs" eran de la medición, y varios aciertos aparentes no habían corrido.

## Flujo

### 1. Contexto (antes de gastar un crédito)

- Ubica la sección o ruta exacta y lee su CSS: tokens, tema claro/oscuro, cómo se aíslan
  los estilos, movimiento reducido. Lee también el encabezado, el router y el servidor de
  producción: una ruta pública nueva suele necesitar registrarse allí.
- Busca reglas globales que te van a pelear: `html { scroll-behavior: smooth }`, tamaños
  mínimos táctiles, `button { color: inherit }` y el precache del service worker.
- Extrae la referencia oficial del personaje. De un PDF sin poppler: `pypdf` →
  `page.images` → `im.data`.
- Escribe el **guion de medios**: qué ve la persona, qué controla (puntero, scroll, clic) y
  qué medio necesita cada momento. Tabla de decisión y presupuesto en
  [references/guion-de-medios.md](references/guion-de-medios.md).

### 2. Generar medios con Higgsfield

Detalle, parámetros y plantillas de prompt en
[references/higgsfield-para-web.md](references/higgsfield-para-web.md). Lo esencial:

- Sube la referencia una vez y reutiliza su id. Genera primero las **imágenes base** (valen
  2 créditos) para validar identidad y encuadre, y después anímalas con `start_image`.
- Para lo que controla el usuario: cámara fija, **un solo movimiento continuo**, y **todos
  los clips parten del mismo fotograma**. Así "izquierda al revés + centro + derecha" empalma
  sin costura. Para reacciones que regresan a la pose, usa `start_image` = `end_image`.
- Para secuencias por scroll, pide los eventos en orden ("primero…, luego…, al final…") y
  después **mide** cuándo ocurre cada uno.
- Consulta el costo antes (`get_cost`), lanza en lotes de hasta 6 trabajos y descarga cada
  resultado en cuanto termina. Guarda los crudos fuera del repo junto con sus ids.

### 3. Revisar y procesar

Scripts incluidos (Python con numpy + Pillow, ffmpeg y cwebp):

- `scripts/medios.py hoja clip.mp4 --salida hoja.jpg` — hoja de contacto con tiempos.
  **Mira siempre los clips antes de procesarlos.**
- `scripts/medios.py curva clip.mp4` — movimiento por fotograma: detecta cortes, arranques
  lentos y tramos quietos.
- `scripts/medios.py muestreo clip-sin-fondo.mp4 --cantidad 24` — índices repartidos por
  **cambio visible**, no por tiempo. Los generadores arrancan lento, y con muestreo por tiempo
  el cursor recorre media pantalla sin que el personaje se mueva.
- `scripts/medios.py secuencia-alfa original.mp4 recortado.mp4 salida/ --indices 0,4,9`
  — reconstruye el alfa (con `scripts/componer_alfa.py`) y escribe WebP en dos calidades.
  Hace falta porque el recorte de fondo de video de Higgsfield entrega H.264 **sin alfa**,
  con el sujeto sobre negro puro.
- `scripts/medios.py secuencia clip.mp4 salida/ --paso 3` — fotogramas opacos para escenas
  con fondo (secuencias por scroll).
- `scripts/medios.py tiempos clip.mp4 --regiones regiones.json` — en qué momento se enciende
  cada región del encuadre.
- `scripts/medios.py bucle entrada.mp4 salida.mp4 --ancho 1280 --alto 720` — bucle con
  fundido **contado en fotogramas**. Con `--ida-y-vuelta` sirve para clips con movimiento de
  cámara, donde un fundido dejaría ver el salto.
- `scripts/medios.py poster video.mp4 poster.webp --ancho 1600`.

Genera un módulo con los conteos que lee el front (por ejemplo `medios.ts`) desde el mismo
proceso: copiarlos a mano se desincroniza en la siguiente regeneración.

### 4. Construir el front

Patrones con código en [references/patrones-front.md](references/patrones-front.md):

- `assets/secuenciaDeFotogramas.ts`: carga por bisección (la secuencia sirve desde las
  primeras peticiones), `createImageBitmap` fuera del hilo principal y vecino más cercano
  mientras llega el resto.
- **Personaje que sigue al puntero**: un solo `requestAnimationFrame` activo solo en vista;
  escala del giro por el espacio de cada lado; inercia exponencial independiente de los fps;
  vigilancia autónoma cuando el cursor está quieto; en táctil, la mirada sigue al scroll.
  La segunda secuencia (la reacción) se descarga con intención: hover, foco o clic.
- **Mezcla de fotogramas**: pinta el fotograma actual opaco y el siguiente encima con la
  fracción como opacidad. Si pintas ambos a media opacidad, el personaje se vuelve translúcido.
- **Sección fijada por scroll**: reparte el recorrido en tramos iguales por capítulo, aunque
  en el video cada evento ocurra a su propio ritmo. Enmarca el escenario como un "monitor" en
  vez de fundir sus bordes: las máscaras borran detalles que tocan el borde (orejas, pies).
- **Videos**: silenciados por propiedad (`muted` y `defaultMuted`) y reproducidos solo en
  vista. En la portada, un video corrido a un lado deja espacio al título.
- **Navegación**: encabezado compartido entre páginas; `scrollIntoView({ behavior: 'instant' })`
  al llegar con ancla; ruta protegida solo por "landing activa"; segmento registrado en el
  servidor.

### 5. QA en Chrome real

Checklist y plantilla en [references/qa.md](references/qa.md) y `assets/qa-inmersiva.mjs`.
Usa Playwright con `channel: 'chrome'`: el navegador integrado del editor deja el documento
oculto, y así no corren ni `IntersectionObserver` ni el bucle de animación. Expón el estado en
atributos `data-*` (fotograma, modo, cargados) y compruébalo con el puntero todavía en
movimiento. Prueba escritorio, teléfono táctil, movimiento reducido, tema claro, anchos de
320 a 1280 px para el encabezado, anclas al volver a otra página y el build servido por el
servidor real (videos con `206 Partial Content`).

### 6. Entregar

- Una rama por modificación, y **cada rama tiene que funcionar sola**: si la ruta nueva llega
  en la segunda rama, la primera no puede enlazarla. Integra con `--no-ff` en `dev` y mueve
  `main` en fast-forward. Los commits van sin atribución de herramientas.
- Registra lo aprendido: bitácora de Obsidian y grafo, activos en la biblioteca multimedia
  del vault y resultados en el panel y la memoria de Higgsfield.

## Trampas que ya costaron tiempo

Lista completa y explicada en [references/trampas.md](references/trampas.md). Las más caras:

- `Image.fromarray()` de Pillow devuelve una imagen de solo lectura y `ImageDraw.floodfill`
  no hace nada sin avisar: usa `.copy()`.
- Rellenar todos los huecos de la máscara vuelve opaco el fondo encerrado entre brazo y cola:
  rellena solo los chicos.
- El batch de Higgsfield responde "preset recommendation" hasta que repites con
  `declined_preset_id`.
- macOS no trae `timeout`: `timeout 300 npx tsc | grep` parece limpio sin haber corrido.
  Confirma el total de errores.
- En Playwright el tema por defecto es claro: pide el esquema de color explícito.
- `drop-shadow` sobre texto con `background-clip: text` pinta un rectángulo: pon la sombra en
  el contenedor.

## Referencias

| Archivo | Cuándo leerlo |
|---|---|
| [references/guion-de-medios.md](references/guion-de-medios.md) | Al planear qué generar y cuánto cuesta |
| [references/higgsfield-para-web.md](references/higgsfield-para-web.md) | Antes de lanzar trabajos en Higgsfield |
| [references/patrones-front.md](references/patrones-front.md) | Al escribir el componente, la sección fijada o la navegación |
| [references/qa.md](references/qa.md) | Antes de dar algo por terminado |
| [references/trampas.md](references/trampas.md) | Cuando algo "no hace nada" o se ve raro |
| [references/caso-kivo.md](references/caso-kivo.md) | Para ver un resultado completo con archivos y números |

Skills relacionadas: `higgsfield-generate` (catálogo de modelos), `higgsfield` (biblia de
estilo y memoria de campañas), `frontend-design` e `impeccable` (dirección visual), y
`hyperframes` si el entregable final es un video y no una página.
