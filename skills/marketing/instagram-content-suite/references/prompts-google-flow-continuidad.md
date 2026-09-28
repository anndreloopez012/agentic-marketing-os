# Google Flow: Video Largo en Bloques de 10 Segundos

Protocolo para Reels de 20 a 60 s con continuidad de personaje, vestuario y cámara en Google Flow (o cualquier herramienta de video por keyframes: Kling, Runway, Higgsfield).

## 1. Fundamentos
1. **Bloques de 10 s.** Todo video largo se divide en tomas de 10 s: `00:00-00:10`, `00:10-00:20`, ...
2. **Puente de keyframes.** La toma 1 parte de la imagen ancla. El último fotograma de cada toma es el Start Frame de la siguiente. Si no se tiene, usar una pose del banco que conserve ángulo y dirección del movimiento.
3. **Métrica de locución.** A ritmo natural (~130-150 palabras por minuto) caben **20-26 palabras por bloque**. Menos deja silencios; más atropella.
4. **Rasgos fijos.** Copiar literalmente la descripción del sujeto de la style bible en cada toma.

## 2. Estructura obligatoria por bloque

```text
================================================================================
TOMA [N] — BLOQUE [00:X0 - 00:Y0] (10 s)
================================================================================
1. ANCLAJES VISUALES
   • Start Keyframe: [ruta o "Último fotograma de la toma N-1"]
   • Character Anchor: [imagen canónica]
   • Pose objetivo al segundo 10: [...]
2. PROMPT PARA GOOGLE FLOW (inglés)
   [Continuous 10-second shot ...]
3. CÁMARA Y TRANSICIÓN
   • Movimiento: [...]
   • Conector de edición: [...]
4. LOCUCIÓN EXACTA (20-26 palabras)
   Diálogo: "[...]"
```

## 3. Arco recomendado
- **30 s (3 bloques)**: gancho + problema → solución en acción → resultado + CTA.
- **60 s (6 bloques)**: gancho → problema → agitación → solución → prueba → CTA.

## 4. Ejemplo genérico — 30 s, tienda de bicicletas con mascota

### TOMA 01 — 00:00-00:10
- Start Keyframe: `./marca/mascotas/rueda/01_frontal.jpg`
- Character Anchor: `./marca/mascotas/rueda/01_frontal.jpg`
- Pose objetivo: la mascota mira una bicicleta con la cadena rota y levanta una ceja a cámara.
- Prompt:
  ```text
  Continuous 10-second shot. Rueda, a friendly 3D animated hedgehog mechanic in a green workshop apron,
  kneels next to a city bike with a broken chain in a bright bicycle workshop. At second 6 he looks up
  at the camera and raises one eyebrow. Slow dolly-in from medium shot to waist-level close-up.
  Warm workshop lighting with soft green rim light. Consistent 3D feature-animation style.
  ```
- Cámara: dolly-in lento. Conector: corte por mirada a cámara.
- Diálogo (23 palabras): "Si tu cadena suena así cada mañana, no es mala suerte. Es falta de mantenimiento, y se arregla en menos de una hora."

### TOMA 02 — 00:10-00:20
- Start Keyframe: último fotograma de la toma 01.
- Pose objetivo: la mascota sostiene la cadena nueva, brillante, frente a cámara.
- Diálogo (22 palabras): "Revisamos cadena, frenos y cambios mientras esperas un café. Te decimos qué necesita tu bici y qué no, sin letra pequeña."

### TOMA 03 — 00:20-00:30
- Pose objetivo: la mascota sale pedaleando; plano abierto con espacio para la tarjeta final.
- Diálogo (21 palabras): "Tu bici lista hoy mismo. Agenda tu revisión desde el enlace de la biografía y pedalea tranquilo toda la semana."

(Los prompts de las tomas 02 y 03 siguen la misma forma que la 01.)

## 5. Errores comunes
- Cambiar la descripción del personaje entre tomas → el personaje muta.
- Pedir dos acciones grandes en 10 s → movimientos incoherentes.
- Olvidar la dirección del movimiento en el corte → saltos de eje.
- Escribir la locución antes de contar palabras → audio que no cabe.
