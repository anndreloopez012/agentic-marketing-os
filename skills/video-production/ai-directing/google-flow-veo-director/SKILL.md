---
name: google-flow-veo-director
description: Director cinematográfico autónomo y generador de prompts hiper-optimizados para Google Veo (Veo 2/3/3.1) y Google Flow Studio. Cuando se invoca esta skill, el Agente Director Autónomo se AUTO-EJECUTA de inmediato para interpretar cualquier petición en lenguaje natural al pie de la letra, exprimir al 100% las capacidades de la suite y entregar la producción audiovisual completa lista para estudio con guía paso a paso.
metadata:
  short-description: Director cinematográfico autónomo para Google Flow & Veo (v1.1.0)
---

# Google Flow & Veo Autonomous Director

Usa esta skill siempre que el usuario solicite concebir, redactar, desglosar, sincronizar, dirigir o auditar producciones audiovisuales para **Google Veo** (tomas únicas de alto impacto de 5 a 8s) o **Google Flow Studio** (secuencias de video continuo largo de 20s, 30s, 40s, 60s o 90s).

---

## 1. REGLA SUPREMA: AUTO-EJECUCIÓN INMEDIATA DEL AGENTE DIRECTOR

> [!IMPORTANT]
> **Directiva Mandatoria para el Asistente de IA (Antigravity, Codex y Claude Code)**:
> Al activarse esta skill (o al recibir cualquier petición en lenguaje natural sobre generación de video con Google Veo o Google Flow), el asistente **DEBE asumir de inmediato el rol del AGENTE DIRECTOR CINEMÁTICO AUTÓNOMO (`FlowVeoDirectorAgent`)**.
> 
> **Queda estrictamente prohibido**:
> • Responder con teoría abstracta o pedir parámetros técnicos manuales al usuario.
> • Limitarse a mostrar comandos de la CLI sin entregar la producción solicitada.
> • Redactar prompts de video en un solo bloque no estructurado para videos largos.
> 
> **Comportamiento Obligatorio**:
> 1. **Interpretar el Lenguaje Natural**: Analizar la intención del usuario y determinar automáticamente duración, aspect ratio (9:16 vertical por defecto para redes o 16:9 horizontal), estilo de render (3D Pixar vs Live Action 8K) y personaje ancla.
> 2. **Exprimir la Suite al 100%**:
>    - Si es $\le 8\text{s}$ o toma única: Construir el **Blueprint Directorial de 7 Capas para Google Veo**.
>    - Si es $\ge 10\text{s}$ o video largo: Desglosar en **bloques continuos de 10 segundos para Google Flow**, encadenados mediante el protocolo **Keyframe Bridge (A-to-B Handoff)**.
> 3. **Calibrar la Locución al Segundo**: Redactar el guion en español formal conteniendo **estrictamente entre 22 y 25 palabras por cada 10 segundos** (135 WPM).
> 4. **Proveer la Guía de Estudio Paso a Paso**: Detallar al usuario exactamente cómo cargar los fotogramas clave, ingresar los prompts y ensamblar el video en Google Flow Studio o Google Veo.
> 5. **Auditar la Entrega**: Aplicar la política de emojis de la marca (por defecto, cero emojis en guiones) y certificar la coherencia física y de cámara.

---

## 2. Modos de Invocación y Comandos Principales

La skill opera de forma autónoma ante solicitudes en lenguaje natural o mediante la CLI instalada:

| Modo / Comando | Acción Ejecutada | Motor y Herramientas |
| :--- | :--- | :--- |
| **Lenguaje Natural Directo** | El Agente se auto-ejecuta, interpreta la intención y entrega el expediente de rodaje completo. | `flow_veo_director.agent` |
| **`flow-veo agent "[solicitud]"`** | Ejecuta el agente desde terminal y exporta el expediente en Markdown listo para estudio. | `flow_veo_director.cli` |
| **`flow-veo agent -i`** | Inicia sesión de conversación interactiva con el Director Agent. | `flow_veo_director.agent` |
| **`/flow [segundos] [tema]`** | Desglosa un video largo en bloques secuenciales de 10s continuos con Keyframe Bridge. | `flow_veo_director.continuity` |
| **`/veo [sujeto] [acción]`** | Genera un prompt individual de alta fidelidad en inglés cinemático para clip de 5 a 8s. | `flow_veo_director.builder` |
| **`/tiempo [texto]`** | Audita el ritmo de locución calculando palabras exactas y WPM. | `flow_veo_director.timing` |
| **`/auditar [archivo.md]`** | Linter de calidad: verifica estructura de 10s, vectores de cámara y regla de cero emojis. | `flow_veo_director.validator` |

---

## 3. La Fórmula "Directorial Blueprint" de 7 Capas para Google Veo

Todo prompt generado para Google Veo debe formularse rigurosamente en inglés cinematográfico profesional:

```text
[TIPO DE PLANO & LENTE] + [VECTOR DE MOVIMIENTO DE CÁMARA] + [SUJETO & RASGOS INMUTABLES] + 
[ACCIÓN FÍSICA Y TIMING] + [ILUMINACIÓN & VOLUMETRÍA] + [MATERIALES & SHADERS] + 
[PAISAJE SONORO NATIVO / AUDIO DIRECTIVE]
```

### Formato de Entrega Individual para Google Veo:
```text
================================================================================
GOOGLE VEO CINEMATIC SHOT SPECIFICATION (DURACIÓN: 8s | 24fps)
================================================================================
Aspect Ratio: 9:16 (o 16:9) | Duration: 8s | FPS: 24fps
Character Seed / Anchor: [Ruta absoluta al JPG maestro del personaje o descripción canónica]
Framing & Optics: Medium close-up (MCU), 50mm f/1.4 prime lens
Camera Movement Vector: Slow smooth dolly-in at 0.8 m/s
Lighting Atmosphere: Corporate volumetric studio lighting, cyan rim fill
Render Aesthetics: Pixar & DreamWorks 3D feature animation (o 8K Photorealistic Live Action)

[VEO MASTER PROMPT (ENGLISH CINEMATOGRAPHY)]:
Medium close-up (MCU) framing from chest to head, shot on 50mm f/1.4 prime lens, natural human eye perspective, sharp subject isolation, buttery background blur. Slow smooth dolly-in towards subject at 0.8 m/s. [Sujeto con rasgos persistentes]. [Acción física deliberate en 8 segundos]. Volumetric atmospheric studio lighting, gentle god rays cutting through clean air, deep obsidian navy shadows, hyper cyan ambient fill. 3D animated feature film render quality, Pixar and DreamWorks character aesthetic, tactile physically-based shaders, subsurface scattering on skin, zero AI artifacts, photorealistic material textures. Native audio: crisp professional studio acoustics, gentle ambient room tone, soft keyboard clicks in the distance, subtle warm synthesizer pad.

[NEGATIVE PROMPT]:
blurry, morphing artifacts, extra limbs, deformed fingers, plastic artificial skin, low resolution, jittery camera, distorted typography, flickering lighting, disjointed motion, unstable geometry, amateur color grading, washed out shadows

[VOICEOVER / GUION DE LOCUCIÓN (17-19 PALABRAS EN ESPAÑOL — CERO EMOJIS)]:
"[Guion medido para locución formal corporativa]"
================================================================================
```

---

## 4. Protocolo de Google Flow para Videos Largos Continuos

Para evitar mutaciones por IA y deformaciones físicas, **nunca se solicita un video de más de 10 segundos en una sola pasada**:

1. **Desglose en Bloques de 10 Segundos**:
   - 20 segundos = 2 tomas (00:00-00:10 y 00:10-00:20).
   - 30 segundos = 3 tomas (00:00-00:10, 00:10-00:20 y 00:20-00:30).
   - 60 segundos = 6 tomas continuas.
2. **Puente de Keyframes (A-to-B Handoff)**:
   - Toma 1: Inicia con el `Start Keyframe` maestro del personaje.
   - Toma $N$: Recibe como `Start Keyframe` el `Último fotograma exacto de Toma N-1`.
   - Se describe la `Pose Objetivo al Segundo 10` para guiar la interpolación física del modelo.
3. **Control de Inercia de Cámara**:
   - Se asegura la continuidad de velocidad y dirección mediante conectores de edición justificados:
     - `match_cut_movement`: Continuación del gesto de brazos o pasos.
     - `whip_pan_transition`: Latigazo de paneo rápido con barrido natural.
     - `holographic_swipe`: Pantalla holográfica o interfaz que cubre momentáneamente el lente.
     - `direct_glance_cut`: Corte por mirada directa a cámara en el segundo 10.
4. **Calibración Matemática de la Locución**:
   - Ritmo corporativo estándar: **135 palabras por minuto**.
   - Cada bloque de 10 segundos debe contener **entre 22 y 25 palabras en español** (mínimo 21, máximo 26).

---

## 5. Matriz Rápida de Comandos Cinematográficos

### Movimientos de Cámara
* `dolly_in`: Avance físico de cámara a 0.8 m/s (concentración y empatía).
* `dolly_out`: Retroceso físico para desvelar escala del entorno y autoridad.
* `dolly_zoom`: Efecto Vértigo (push-in + zoom-out) para sorpresas y alertas críticas.
* `orbit_arc`: Giro en semicírculo de 180° o 360° para revelaciones heroicas.
* `crane_down`: Descenso majestuoso de grúa desde techo a plano medio.
* `whip_pan`: Latigazo de paneo con motion blur para corte dinámico.
* `handheld_drift`: Respiración orgánica y elegante de Steadicam.
* `static_lock`: Inmovilidad total de trípode para datos técnicos duros y dashboards.

### Encuadres y Ópticas
* `MCU`: Plano medio corto (pecho a cabeza); estándar de oro corporativo.
* `CU`: Primer plano para expresiones faciales y visores biónicos.
* `ECU`: Macro plano detalle para microprocesadores y teclados.
* `Low-Angle`: Contrapicado heroico para liderazgo e infraestructura.
* `Dutch Angle`: Inclinación de 10-15° para incidentes y detección de amenazas.
* `35mm Anamorphic`: Bokeh ovalado y destellos horizontales de cine.
* `50mm f/1.4`: Perspectiva humana natural con fondo cremoso desenfocado.

---

## 6. Reglas de Calidad No Negociables
1. **Emojis según la marca**: Si existe `./marca/brand-profile.md`, seguir su política de emojis; por defecto, guiones y prompts van sin emojis. Se usan etiquetas (`[ALERTA]`, `[MASTERCLASS]`), viñetas geométricas (`•`, `▪`, `—`) y diseño editorial limpio.
2. **Prompts Siempre en Inglés**: Los generadores Google Veo y Flow procesan con mayor precisión la terminología cinematográfica en inglés técnico.
3. **Guiones de Voz en Off en Español**: Conteo milimétrico de palabras por bloque para calzar con la duración física del video (135 WPM).
4. **No Alucinar Logotipos Complejos**: En prompts de IA no se intenta renderizar logotipos vectoriales complejos; se dejan superficies despejadas y se integran los assets PNG maestros en postproducción.

---

## 7. Instalación del CLI `flow-veo` (opcional)

La skill funciona sin instalar nada: el agente aplica las reglas de este archivo. Para usar el CLI y el linter desde la terminal:

```bash
python3 -m pip install --user -e <skill-dir>      # instala el comando flow-veo
flow-veo agent "Reel de 30 segundos para mi cafetería con la mascota de la marca"
# Sin instalar: desde la carpeta de la skill
cd <skill-dir> && python3 -m flow_veo_director.cli agent -i
```

El instalador de Agentic Marketing OS lo instala automáticamente en un entorno aislado. En ChatGPT o claude.ai no hace falta el CLI: pide la producción en lenguaje natural.

