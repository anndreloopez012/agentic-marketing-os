# ARQUITECTURA DE GOOGLE FLOW: GENERACIÓN DE VIDEOS LARGOS CONTINUOS

Los generadores de video por difusión sufren de **deriva temporal (temporal drift)** cuando se les pide generar tomas excesivamente largas de una sola pasada: los personajes mutan, la ropa cambia de color y la física colapsa.

**Google Flow** resuelve este problema mediante la **Arquitectura de Bloques Secuenciales de 10 Segundos con Puente de Keyframes (Keyframe Bridge)**.

---

## 1. La Regla de Oro de los Bloques de 10 Segundos

Cualquier video corporativo largo (20s, 30s, 40s, 60s o 90s) debe descomponerse matemáticamente en tomas contiguas de **10 segundos exactos**:

```
+---------------------------------------------------------------------------------------------------+
| VIDEO COMPLETO (30 SEGUNDOS)                                                                      |
+---------------------------------+---------------------------------+-------------------------------+
| BLOQUE 1 (00:00 - 00:10)        | BLOQUE 2 (00:10 - 00:20)        | BLOQUE 3 (00:20 - 00:30)      |
| Gancho & Presentación del Reto  | Desarrollo Técnico & Demostración| Cierre Triunfal & Call to Action|
+---------------------------------+---------------------------------+-------------------------------+
  Start: Imagen Canónica            Start: Last Frame Toma 1          Start: Last Frame Toma 2
  End: Pose Objetivo A              End: Pose Objetivo B              End: Pose Objetivo Final
```

---

## 2. El Puente de Keyframes (A-to-B Keyframe Bridge)

1. **Toma 01 (Inicio)**:
   - Se alimenta con una imagen canónica local de alta resolución del banco del personaje como **Start Keyframe**.
   - Se instruye una acción continua que debe culminar en una postura concreta en el segundo 10 (`Pose Objetivo al Segundo 10`).
2. **Toma 02 en adelante (Handoff)**:
   - El último fotograma renderizado de la Toma 01 se convierte automáticamente en el **Start Keyframe** de la Toma 02.
   - Si se planifica en preproducción antes de renderizar, se utiliza como Start Keyframe la pose coincidente del banco maestro de poses con idéntico atuendo y ángulo de cámara.
3. **Inercia de Cámara**:
   - Si la Toma 01 finaliza con un `Dolly-In a 0.8 m/s`, la Toma 02 debe absorber esa inercia o ejecutar un corte de montaje conector justificado (`Match Cut`, `Whip Pan` o `Holographic Swipe`).

---

## 3. Matriz de Componentes por Bloque de 10 Segundos

Cada bloque dentro de Google Flow debe documentar obligatoriamente 5 capas:

```text
================================================================================
TOMA [N] — BLOQUE TEMPORAL: [00:X0 - 00:Y0] (DURACIÓN: 10 SEGUNDOS)
================================================================================
1. ANCLAJES VISUALES (KEYFRAME BRIDGE & CONTINUIDAD):
   • Start Keyframe: [Ruta absoluta al archivo JPG inicial o 'Último fotograma de Toma N-1']
   • Character Anchor: [Ruta a la imagen maestra del personaje para fijar rasgos]
   • Pose Objetivo al Segundo 10: [Descripción de la postura y encuadre final]

2. PROMPT PARA GOOGLE FLOW / VEO (INGLÉS CINEMATOGRÁFICO):
   [Prompt cinematográfico continuo en inglés con sujeto, acción, cámara, luz y estilo]

3. VECTOR DE CÁMARA Y TRANSICIÓN:
   • Movimiento: [P.ej., Slow Dolly-In a 0.8 m/s, giro orbital de 15 grados]
   • Conector de Edición: [Match Cut por movimiento, swipe de interfaz o corte natural]

4. DIÁLOGO / LOCUCIÓN CALIBRADA (22-25 PALABRAS EN ESPAÑOL — CERO EMOJIS):
   "[Líneas de diálogo redactadas para durar exactamente 10 segundos]"
================================================================================
```

---

## 4. Tipos de Conectores de Montaje para Transiciones Invisibles

* **Match Cut por Movimiento (`match_cut_movement`)**:
  * La mano del personaje inicia un movimiento en la Toma 1 y culmina completando la acción en la Toma 2 desde un ángulo más cerrado.
* **Latigazo de Paneo (`whip_pan_transition`)**:
  * La cámara realiza un giro ultrarrápido al segundo 9.5 con desenfoque de movimiento; la Toma 2 inicia frenando ese mismo giro en el nuevo escenario.
* **Barrido Holográfico / Interfaz (`holographic_swipe`)**:
  * Una ventana gráfica, reporte o interfaz digital se expande cubriendo brevemente la lente al segundo 9.8, despejando la pantalla en la Toma 2.
* **Oclusión en Primer Plano (`occlusion_reveal`)**:
  * Un pilar arquitectónico, marco de puerta o cliente cruza por delante de la lente al segundo 10, sirviendo de cortina de transición natural.
* **Corte Analítico por Mirada Directa (`direct_glance_cut`)**:
  * El protagonista clava su mirada directamente a la lente en el segundo 10; el corte pasa a un plano cerrado de reacción.
