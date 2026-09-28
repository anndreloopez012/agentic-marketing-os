# Manual de Referencia Técnica: Protocolo del Agente Director Autónomo

> **Documento**: `references/06_protocolo_agente_director_autonomo.md`  
> **Sistema**: Google Flow & Veo Cinematic Director Suite  
> **Versión**: 1.1.0  
> **Audiencia**: Agentes de IA (Antigravity, Codex, Claude) y Directores Audiovisuales

---

## 1. Arquitectura y Filosofía del Agente

El **Agente Director Autónomo** (`FlowVeoDirectorAgent`) fue concebido para eliminar por completo la fricción entre la concepción de una idea en lenguaje natural y la ejecución rigurosa y matemática requerida por los modelos generativos de video de última generación (**Google Veo 2 / 3 / 3.1** y **Google Flow Studio**).

### El Problema de la Brecha de Producción:
* **Entrada Humana Natural**: *"Quiero un video de 30 segundos sobre una fintech mostrando el SAT FEL y retail POS"*.
* **Limitación Clásica de IA**: Respuestas genéricas con prompts vagos ("A cinematic video of fintech"), solicitud de parámetros tediosos al usuario, o prompts largos que provocan deformaciones de extremidades y mutación de rostros en el modelo.
* **Solución del Agente Director**: Auto-ejecución inmediata que desglosa el requerimiento en un **expediente cinematográfico completo de grado industrial**, con calibración temporal de 10s, puente de fotogramas clave, guion con conteo de palabras auditado y guía de estudio paso a paso.

---

## 2. Heurísticas de Interpretación de Lenguaje Natural

El motor de análisis en `flow_veo_director.agent` procesa las peticiones del usuario mediante una jerarquía determinista:

| Dimensión | Patrones Detectados en Lenguaje Natural | Decisión Directorial / Valor por Defecto |
| :--- | :--- | :--- |
| **Motor Objetivo** | Menciones de *"clip"*, *"toma única"*, *"veo"*, duración $\le 8\text{s}$. | **Google Veo** (Master Blueprint individual de 5 a 8s). |
| | Menciones de *"secuencia"*, *"video largo"*, *"flow"*, duración $\ge 10\text{s}$. | **Google Flow Studio** (Secuencia en bloques de 10s continuos). |
| **Duración** | Regex `(\d+)\s*(s\|seg\|min)`. Multiplica minutos por 60. | Si no especifica: **30 segundos** (3 tomas de 10s) para Flow, **8 segundos** para Veo. Redondeo automático a múltiplos de 10s para Flow. |
| **Aspect Ratio** | *"reel"*, *"tiktok"*, *"shorts"*, *"vertical"*, *"9:16"*. | `9:16` (Estándar vertical para consumo móvil). |
| | *"horizontal"*, *"youtube"*, *"web"*, *"corporativo"*, *"16:9"*. | `16:9` (Estándar cinemático horizontal). |
| | *"cuadrado"*, *"feed"*, *"1:1"*. | `1:1` (Estándar Instagram Feed). |
| **Estilo Visual** | *"live action"*, *"real"*, *"humano"*, *"actor"*, *"8k"*, *"arri"*. | `cinematic_live_action` (Cámara Arri Alexa Mini LF 8K). |
| | *"3d"*, *"animado"*, *"pixar"*, *"dreamworks"*, *"mascota"*. | `pixar_dreamworks_3d` (Shaders táctiles, SSS, iluminación Pixar). |
| **Personaje** | Mascota de marca, lobo, zorro, ingeniero, fundador, etc. | Asigna prompt canónico inmutable para fijar el rostro en todas las tomas. |
| **Iluminación** | Ciberseguridad, banca, retail, cleanroom, nocturno. | Mapea a `corporate_volumetric`, `chiaroscuro_security` o `high_tech_cleanroom`. |

---

## 3. Protocolo de Continuidad para Google Flow Studio (Keyframe Bridge)

Para garantizar cero deriva temporal (cero mutaciones corporales o de vestuario), el agente implementa el protocolo de **Puente de Fotogramas Clave**:

```text
[Start Frame Maestro]
        │
        ▼
   ┌─────────┐
   │ TOMA 01 │  (00:00 - 00:10)
   └────┬────┘
        │
        ├─ Exportar último fotograma exacto (segundo 10.0)
        ▼
   ┌─────────┐
   │ TOMA 02 │  (00:10 - 00:20) [Start Frame = Último Frame Toma 01]
   └────┬────┘
        │
        ├─ Exportar último fotograma exacto (segundo 20.0)
        ▼
   ┌─────────┐
   │ TOMA 03 │  (00:20 - 00:30) [Start Frame = Último Frame Toma 02]
   └─────────┘
```

### Inercia y Conectores de Movimiento de Cámara:
* **Toma 1 a Toma 2**: Si la Toma 1 finaliza con un `dolly_in` a $0.8\text{ m/s}$, la Toma 2 recibe la inercia con un `orbit_arc` fluido o aplica un conector `match_cut_movement` (continuidad del gesto del sujeto).
* **Toma 2 a Toma 3**: Aplica `whip_pan_transition` o `holographic_swipe` para realizar el cambio de encuadre hacia plano cerrado o gran angular de cierre sin saltos visuales incómodos.

---

## 4. Calibración Matemática de la Locución (WPM)

La cadencia de locución es una de las variables más críticas: si el locutor habla demasiado rápido, el mensaje se vuelve incomprensible; si habla demasiado lento, se generan silencios muertos en el video.

* **Estándar Corporativo en Español**: 135 Palabras Por Minuto (WPM), equivalente a **2.25 palabras por segundo**.
* **Ventana por Bloque de 10 Segundos**:
  * Óptimo: **22 a 25 palabras**.
  * Rango Aceptable de Seguridad: **21 a 26 palabras**.
  * Fuera de rango: El motor del agente recalibra y ajusta automáticamente la redacción antes de entregarla.

---

## 5. Uso Programático en Python

Los desarrolladores y otros agentes pueden instanciar y consumir el motor directamente en código:

```python
from flow_veo_director.agent import FlowVeoDirectorAgent

# Inicializar agente
agent = FlowVeoDirectorAgent(default_style="pixar_dreamworks_3d", default_ratio="9:16")

# Generar expediente completo desde lenguaje natural
dossier_markdown = agent.generate_full_dossier(
    "Quiero un video de 30 segundos sobre una fintech mostrando el SAT FEL y retail POS"
)

# Guardar o enviar al usuario
with open("expediente_produccion.md", "w", encoding="utf-8") as f:
    f.write(dossier_markdown)
```
