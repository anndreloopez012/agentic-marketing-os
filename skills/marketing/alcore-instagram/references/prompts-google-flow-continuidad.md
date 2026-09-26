# GUIA MAESTRA: PROMPTS PARA GOOGLE FLOW Y CONTINUIDAD DE VIDEO LARGO

Esta guía establece el protocolo técnico para generar secuencias de video largo continuo en **Google Flow** (o sistemas de video secuencial asistido por keyframes), desglosando el metraje en **bloques sincronizados de 10 segundos** con imágenes de anclaje, vectores de cámara fluidos y diálogos medidos con precisión temporal.

---

## 1. Fundamentos de Continuidad en Google Flow

Google Flow permite encadenar tomas sucesivas mediante control de keyframes (Start Frame y End Frame) y pesos de consistencia de personaje.
Para evitar que el personaje mute, cambie de ropa o dé saltos temporales bruscos:
1. **Regla de Bloques de 10 Segundos**: Todo video largo (20s, 30s, 40s o 60s) se descompone en tomas individuales de 10 segundos (`Shot 1: 00:00-00:10`, `Shot 2: 00:10-00:20`, `Shot 3: 00:20-00:30`, etc.).
2. **Puente de Keyframes (A-to-B Continuity)**:
   - Toma 1 utiliza una imagen del banco maestro local como **Start Frame**.
   - Al finalizar la Toma 1, el último fotograma (`Last Frame at 00:10`) se convierte en el **Start Frame** de la Toma 2.
   - Si no se tiene el frame renderizado previo, se especifica una imagen del banco de poses que mantenga el ángulo y la inercia del movimiento.
3. **Métrica de Locución**: A un ritmo de locución profesional corporativo (135 palabras por minuto), cada bloque de 10 segundos admite **entre 22 y 25 palabras en español**. Superar ese límite genera atropello verbal; quedarse muy por debajo crea silencios vacíos.

---

## 2. Estructura Obligatoria por Bloque de 10 Segundos

Cuando se solicite un guion para Google Flow, la skill debe estructurar cada toma bajo el siguiente estándar:

```text
================================================================================
TOMA [N] — BLOQUE TEMPORAL: [00:X0 - 00:Y0] (DURACIÓN: 10 SEGUNDOS)
================================================================================
1. ANCLAJES VISUALES (KEYFRAMES & CONTINUIDAD):
   • Start Keyframe: [Ruta absoluta al archivo JPG inicial o 'Último fotograma de Toma N-1']
   • Character Anchor: [Ruta a la imagen maestra del personaje para fijar rasgos]
   • Pose Objetivo al Segundo 10: [Descripción de la postura y encuadre final]

2. PROMPT PARA GOOGLE FLOW (INGLÉS CINEMATOGRÁFICO):
   [Prompt continuo en inglés indicando acción fluida de 10s, movimiento de cámara coordinado,
   iluminación, coherencia física con la toma anterior y estilo Pixar/DreamWorks]

3. VECTOR DE CÁMARA Y TRANSICIÓN:
   • Movimiento: [P.ej., Continuación de Dolly-In a 1.2 m/s, giro orbital de 15 grados]
   • Conector de Edición: [Match Cut por movimiento, barrido de cola, swipe de interfaz o corte natural]

4. DIÁLOGO / LOCUCIÓN EXACTA PARA ESTOS 10 SEGUNDOS (22-25 PALABRAS — CERO EMOJIS):
   "[Líneas de diálogo en español formal redactadas exactamente para completarse en 10 segundos]"
```

---

## 3. Matriz de Coherencia de Mascotas para Flow

### A. KIVO (Columna 1 — Kinvo & Prensa Tech)
- **Ruta Maestra de Personaje**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVO/01_kivo_frontal_full.jpg`
- **Puntos Críticos de Continuidad**:
  - Visor HUD siempre sobre el ojo izquierdo (nunca en el derecho).
  - Circuito cian pulsando dentro de las orejas.
  - Collar K centrado en el pecho.
- **Transición Típica**: Kivo toca el visor HUD -> La interfaz se expande -> Match cut hacia el detalle de la pantalla en la siguiente toma.

### B. ALKI (Columna 2 — Educación IA, Lenguajes y Git)
- **Ruta Maestra de Personaje**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/ALKI/01_alki_frontal_full.jpg`
- **Puntos Críticos de Continuidad**:
  - Pelaje suave azul cielo y blanco ártico con trazas luminiscentes cian (#00C4FF).
  - Visor AR rectangular de realidad aumentada cian que cubre ambos ojos con telemetría.
  - Sudadera con capucha (hoodie) azul marino oscuro con cordones verde lima y logotipo de nube ALCORE.
  - Zapatillas high-top con iluminación cian reactiva.
- **Transición Típica**: Alki toca su visor AR o desliza su garra sobre la tableta transparente ALCORE -> La interfaz holográfica cian se expande hacia el código en la toma siguiente.

### C. KIVI (Columna 3 — Memes y Datos Curiosos)
- **Ruta Maestra de Personaje**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/05_kivi_back_view.jpg` y `01_kivi_frontal_full.jpg`
- **Puntos Críticos de Continuidad**:
  - Cola prensil segmentada siempre con el lazo interior en forma de 'K' mayúscula y neón púrpura activo.
  - Juntas mecánicas de titanio visibles en rodillas y codos.
  - Ojos independientes 360° con anillo de lente fotográfico.
- **Transición Típica**: Giro rápido de cabeza de Kivi con mirada a cámara -> Whip pan cómico o golpe de ticket con lengua -> Inicio de la siguiente toma.

---

## 4. Ejemplo Práctico: Secuencia de 30 Segundos (3 Bloques de 10s) con Kivi

### TOMA 01 — BLOQUE TEMPORAL: 00:00 - 00:10 (DURACIÓN: 10 SEGUNDOS)
- **Start Keyframe**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/07_kivi_counter_scanner.jpg`
- **Character Anchor**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/05_kivi_back_view.jpg`
- **Pose Objetivo al Segundo 10**: Kivi detrás del mostrador, baja el escáner láser y levanta una ceja mirando a cámara.
- **Prompt para Google Flow**:
  ```text
  Continuous 10-second shot. Kivi, the mecha chameleon of Kinvo Express with purple and teal armor, stands behind a modern retail store counter. He is rapidly scanning product barcodes with a handheld red laser scanner. At second 6, he stops scanning, turns his independent chameleon eyes toward the camera, and raises an inquisitive eyebrow. Smooth slow camera dolly-in from medium shot to waist-level close-up. Warm retail lighting with subtle purple neon glow on his spine. Consistent Pixar DreamWorks 3D mecha character animation.
  ```
- **Vector de Cámara**: Slow Dolly-In frontal suave a 0.8 m/s.
- **Conector de Edición**: Corte por mirada directa a cámara en el segundo 10.
- **Diálogo Sincronizado (00:00 - 00:10 | 24 palabras)**:
  "Cobrar en mostrador debería tomar menos de cinco segundos. Pero si tu sistema se congela a fin de mes, el problema no es tu internet."

---

### TOMA 02 — BLOQUE TEMPORAL: 00:10 - 00:20 (DURACIÓN: 10 SEGUNDOS)
- **Start Keyframe**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/01_kivi_frontal_full.jpg`
- **Character Anchor**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/05_kivi_back_view.jpg`
- **Pose Objetivo al Segundo 10**: Kivi muestra la pantalla de su tableta POS con un check verde gigante de "SAT FEL Certificado".
- **Prompt para Google Flow**:
  ```text
  Continuous 10-second shot connecting seamlessly from previous take. Kivi holds up his sleek glowing touchscreen POS tablet toward the camera. His mechanical fingers tap the screen twice, causing a bright green holographic SAT FEL invoice certificate to project outward with floating cryptographic checkmarks. His curled 'K' tail wiggles happily behind him, glowing purple. Camera holds steady in medium shot with gentle floating handheld drift. Commercial boutique lighting, crisp reflections on tablet glass, identical mecha shaders.
  ```
- **Vector de Cámara**: Plano medio fijo con sutil deriva flotante cinematográfica.
- **Conector de Edición**: El holograma del check verde cubre brevemente el encuadre al segundo 20.
- **Diálogo Sincronizado (00:10 - 00:20 | 23 palabras)**:
  "Es tu software. Kinvo Express sincroniza cada cobro con el SAT al instante, incluso si se cae la red local en plena quincena."

---

### TOMA 03 — BLOQUE TEMPORAL: 00:20 - 00:30 (DURACIÓN: 10 SEGUNDOS)
- **Start Keyframe**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/10_kivi_celebration.jpg`
- **Character Anchor**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/05_kivi_back_view.jpg`
- **Pose Objetivo al Segundo 10**: Salto de victoria elevando la tableta, guiño de ojo y congelado con logotipo de Kinvo Express.
- **Prompt para Google Flow**:
  ```text
  Continuous 10-second concluding shot. Emerging from the glowing holographic checkmark, Kivi jumps into an energetic triumphant celebration pose, lifting the tablet high above his head while his mechanical 'K' tail swings with electric purple light. Celebratory digital confetti sparkles fall gently. Kivi winks directly at the camera with a playful smile. Camera pulls back smoothly into a wide hero shot. Volumetric celebration lighting, high polish 3D feature animation render.
  ```
- **Vector de Cámara**: Slow Dolly-Out de plano medio a plano entero heroico.
- **Conector de Edición**: Remate y fade a tarjeta final institucional.
- **Diálogo Sincronizado (00:20 - 00:30 | 22 palabras)**:
  "Caja cuadrada, clientes atendidos y cero multas fiscales. Deja de pelear con tu punto de venta. Pide tu demo hoy mismo."
