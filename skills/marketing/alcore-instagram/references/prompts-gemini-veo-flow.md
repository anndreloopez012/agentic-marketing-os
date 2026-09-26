# GUIA MAESTRA: PROMPTS PARA GEMINI VEO Y FLOW (ALCORE INSTAGRAM)

Esta guía establece el protocolo técnico para construir prompts de video generativo para **Gemini Veo**, **Flow**, **Luma Dream Machine**, **Runway Gen-3** y **Higgsfield**, manteniendo consistencia total de las 3 mascotas corporativas.

---

## 1. Estructura Sintáctica del Prompt para Modelos de Video

Los modelos de video de frontera interpretan con mayor precisión los prompts redactados en inglés técnico estructurado bajo la siguiente fórmula:

```
[Subject & Character Bible] + [Starting Pose & Environment] + [Precise Action & Dynamics] + [Cinematic Camera Movement] + [Lighting & Atmosphere] + [Render Style & Quality Parameters]
```

### Reglas Clave:
1. **Evitar movimientos caóticos**: Los modelos de video generan aberraciones cuando se les pide acciones demasiado complejas en una sola toma. Se debe solicitar una sola acción fluida (un saludo, caminar dos pasos, señalar una pantalla, teclear, elevar una tableta).
2. **Duración y FPS**: Especificar siempre `Duration: 5-8s`, `24fps` o `60fps`.
3. **Relación de aspecto**: `9:16` para Reels / Stories de Instagram.
4. **Referencia de imagen (Image-to-Video)**: Indicar siempre la ruta del asset local como imagen inicial (`first frame` o `character reference`).

---

## 2. Bloques de Personaje por Mascota

### KIVO (Columna 1 — Kinvo & Prensa Tech)
```text
Subject: Kivo, the official cybernetic fox mascot of KINVO. Vibrant Solar Amber orange and cream fur, oversized bionic ears with electric cyan neon circuit traces, glowing cyan digital HUD monocle over left eye displaying telemetry waves, sleek cyber collar with metallic cyan 'K' medallion, high-tech white and titanium cyber boots. Highly expressive, energetic, agile posture.
```

### ALKI (Columna 2 — Educación IA, Lenguajes y Git)
```text
Subject: Alki, the official architect moose mascot of ALCORE. Tall stylish anthropomorphic moose wearing a tailored navy blue blazer, charcoal gray turtleneck sweater, tailored trousers and dark brown leather dress shoes. Striking geometric carbon-fiber and polished titanium antlers, black designer glasses, warm intelligent amber eyes. Senior, authoritative, calm and visionary posture.
```

### KIVI (Columna 3 — Memes y Datos Curiosos)
```text
Subject: Kivi, the official mecha chameleon mascot of Kinvo Express. Bionic robotic chameleon with brushed titanium mechanical joints, emerald green and dark violet armor panels, glowing purple neon circuit channels along his mechanical spine, independent 360-degree turret eyes with cybernetic lens diaphragms, prehensile segmented tail curled in an iconic 'K' shape with glowing purple neon tubes, holding a sleek touchscreen POS retail tablet.
```

---

## 3. Catálogo de Movimientos de Cámara Recomendados
- **Slow Cinematic Dolly In**: La cámara avanza lentamente hacia el rostro o la pantalla de la mascota para enfatizar el titular.
- **Subtle 45-Degree Orbit**: La cámara gira 45 grados alrededor de la mascota mostrando el volumen tridimensional y los detalles de su espalda/cola.
- **Low-Angle Hero Tracking**: Ángulo contrapicado que sigue a la mascota mientras camina hacia el espectador con paso firme.
- **Pedestal Up / Crane Reveal**: La cámara asciende desde la base de la estación de trabajo revelando el holograma o pantalla completa.

---

## 4. Ejemplos Listos para Usar por Columna

### Ejemplo Columna 1 (Kivo explicando el módulo POS de Kinvo):
```text
[GEMINI VEO / FLOW PROMPT]
Aspect Ratio: 9:16 | Duration: 6s | FPS: 24fps
Prompt: A cinematic 3D animation clip of Kivo, the cybernetic fox mascot of KINVO with orange fur, bionic cyan ears and glowing left HUD eye visor. Kivo stands in a sleek minimalist glass cloud server room. He smiles cordially at the camera and gestures with his cybernetic right paw towards a floating translucent cyan holographic POS billing terminal displaying real-time transaction graphs. Camera executes a smooth slow dolly-in from medium shot to close-up. Volumetric studio rim lighting with subtle cyan and amber highlights, ray-traced reflections on floor. Pixar DreamWorks feature film quality, ultra-detailed textures.
Image Reference Path: /Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVO/01_kivo_frontal_full.jpg
```

### Ejemplo Columna 2 (Alki explicando Git Hooks):
```text
[GEMINI VEO / FLOW PROMPT]
Aspect Ratio: 9:16 | Duration: 6s | FPS: 24fps
Prompt: A cinematic 3D animation clip of Alki, the sophisticated moose software architect wearing a tailored navy blazer and black glasses with geometric titanium antlers. Alki stands in an architectural blueprint studio with deep royal blue ambient light. He holds a digital stylus and taps a floating floating code block in JetBrains Mono showing a pre-commit hook script, nodding with senior approval. Smooth 30-degree orbital camera pan. Warm studio key light, crisp white accents, Pixar 3D animated film render quality.
Image Reference Path: /Users/macbookpro/Documents/ALCORE/MASCOTAS/ALKI/01_alki_frontal_full.jpg
```

### Ejemplo Columna 3 (Kivi en meme de cobro rápido SAT FEL):
```text
[GEMINI VEO / FLOW PROMPT]
Aspect Ratio: 9:16 | Duration: 6s | FPS: 24fps
Prompt: A comedic dynamic 3D clip of Kivi, the mecha chameleon of Kinvo Express with brushed titanium joints, emerald and purple armor, and 'K'-shaped glowing neon tail. In a boutique retail store counter, Kivi rapidly whips his flexible pink cyber tongue to catch a floating printed invoice ticket in mid-air, while his two 360-degree eyes look in different directions comically before looking at the camera with a triumphant grin and raising his POS tablet with green checkmarks. Dynamic snappy camera punch-in. Bright commercial lighting, Pixar DreamWorks comedic character animation.
Image Reference Path: /Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/08_kivi_tongue_fel.jpg
```
