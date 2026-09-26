---
name: alcore-instagram
description: Suite empresarial de producción de contenido para el Instagram de ALCORE (@alcore.gt). Incluye generador de video separado para Google Veo (single-take 5-8s) y Google Flow (secuencias continuas de 10s con keyframes y diálogo medido), carruseles 4:5, portadas destacables de mascotas, calendario de 30 días, linter de calidad y control de las 3 columnas fijas (Kivo, Alki, Kivi). Norma estricta de cero emojis.
metadata:
  short-description: Suite de producción y video para Instagram de ALCORE (v2.0.0)
---

# ALCORE Instagram Enterprise Content & Video Production Suite (@alcore.gt)

Usa esta skill para planificar, redactar, estructurar y auditar todo el contenido publicado en el perfil de Instagram de **ALCORE Technologies Solutions** (`@alcore.gt`), garantizando una estética 3D cinematográfica estilo Pixar/DreamWorks, continuidad visual en videos y rigurosa disciplina corporativa.

---

## 1. Modos de Invocación y Comandos Rápidos

La skill responde de forma modular según lo que solicite el usuario:

| Comando / Intención | Acción Ejecutada | Archivos de Apoyo |
| :--- | :--- | :--- |
| **`/dia [columna o número]`** | Genera el paquete diario completo (Veo, Flow continuo, Carrusel 4:5 y Copy). | `references/calendario-editorial-30-dias.md` |
| **`/flow [segundos]`** | Desglosa un video largo en bloques continuos de 10s con keyframes, vector de cámara y diálogos de 20-26 palabras. | `references/prompts-google-flow-continuidad.md` |
| **`/veo`** | Genera prompt autocontenido de alta fidelidad para clip de 5 a 8s con Google Veo. | `references/prompts-google-veo.md` |
| **`/carrusel`** | Diseña carrusel de 5 a 7 slides en proporción 4:5 con portada destacable obligatoria con la mascota. | `references/plantillas-carruseles-portadas.md` |
| **`/calendario`** | Muestra el plan editorial del mes con fechas, temas, columnas y assets asignados. | `references/calendario-editorial-30-dias.md` |
| **`/auditar [archivo]`** | Ejecuta el linter automático de calidad para verificar cero emojis, timing de Flow y assets locales. | `scripts/alcore_validator.py` |

---

## 2. Reglas No Negociables de Marca

- **Empresa**: ALCORE Technologies Solutions (`https://alcore-gt.com/`).
- **Lema Institucional**: *"El Núcleo Tecnológico que Impulsa y Protege tu Negocio"*.
- **Posicionamiento**: Infraestructura Cloud de alto rendimiento con hasta 60% de ahorro vs AWS/Azure, desarrollo a medida en TypeScript/Python, software SaaS propio (Kinvo y Kinvo Express) y soporte humano directo 24/7 de ingenieros. 99.9% de uptime real.
- **Arquetipos**: El Sabio (60% - datos duros, benchmarks, rigor) + El Protector (40% - seguridad perimetral, resiliencia y soberanía operativa).
- **Prohibición Estricta de Emojis**: Ninguna publicación, biografía, titular, carrusel, prompt o guion de video debe contener emojis. Se utiliza diseño editorial suizo, etiquetas vectoriales (`[PRENSA]`, `[MASTERCLASS]`, `[LABS]`), viñetas geométricas (`•`, `▪`, `—`) y tipografía limpia.
- **Paleta Cromática Oficial**:
  - `Alcore Royal Blue`: `#0B47D9` (Color primario institucional, fondos educativos y CTAs)
  - `Hyper Cyan`: `#00C4FF` (Flujo cloud, gradientes, destellos y acentos)
  - `Emerald Cyber`: `#10B981` (99.9% uptime, ciberseguridad, checks de éxito y Kivi)
  - `Solar Amber`: `#F59E0B` (Color insignia de Kivo y cintillos de alerta técnica)
  - `Obsidian Navy`: `#0A0F1D` (Fondo nocturno, terminales y prensa)
  - `Pure Ice White`: `#FFFFFF` (Fondos claros y textos de alto contraste)
  - `Slate Tech`: `#64748B` (Textos secundarios y microcopias)
- **Tipografías**:
  - Títulos: Plus Jakarta Sans / Inter (ExtraBold / Bold)
  - Cuerpo: Inter (Regular / Medium)
  - Código, Precios y Métricas: JetBrains Mono

---

## 3. Las 3 Columnas Verticales del Feed

```
+---------------------------+---------------------------+---------------------------+
|    COLUMNA 1 (IZQUIERDA)  |     COLUMNA 2 (CENTRO)    |    COLUMNA 3 (DERECHA)    |
|           KIVO            |           ALKI            |           KIVI            |
|   Kinvo Suite, Express    |  Educación IA, Lenguajes  |   Memes Inteligentes y    |
|      y Prensa Tech        |          y Git            |      Datos Curiosos       |
+---------------------------+---------------------------+---------------------------+
```

### Columna 1 (Izquierda) — KIVO (The Kinetic Fox / Centinela de Datos)
- **Mascota**: Zorro/gato fénec cibernético, pelaje Solar Amber, collar K, orejas biónicas con neón cian, visor HUD en ojo izquierdo.
- **Territorio**:
  - Desglose y demostración de módulos de **KINVO Suite** (CRM, POS, Finanzas, Nómina, Marcaje QR, Copiloto IA).
  - Bondades de **KINVO EXPRESS** (cobro <5s en mostrador, SAT FEL automático, caja cuadrada).
  - Noticias y prensa de tecnología: ciberseguridad, cloud y actualizaciones de software.
- **Banco de Assets**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVO/` (10 imágenes).

### Columna 2 (Centro) — ALKI (The Architect Moose / Alce de Software)
- **Mascota**: Alce elegante en traje sastre azul marino, cuello de tortuga carbón, astas poligonales de fibra de carbono/titanio y gafas negras de ingeniería.
- **Territorio**:
  - Cómo aplicar Inteligencia Artificial en desarrollo y empresas reales (RAG, agentes, automatizaciones).
  - Lenguajes de programación modernos (TypeScript, Python, Go, Node.js) y arquitectura limpia.
  - Buenas prácticas de **Git** (trunk-based development, git hooks, resolución de conflictos y CI/CD).
- **Banco de Assets**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/ALKI/` (10 imágenes).

### Columna 3 (Derecha) — KIVI (The Tech Chameleon Mecha)
- **Mascota**: Camaleón mecha biónico con juntas de titanio, placas violeta/esmeralda, espina dorsal con neón púrpura, cola prensil en 'K', ojos 360° y tableta POS táctil.
- **Territorio**:
  - Memes inteligentes de programación, devops, finanzas corporativas y situaciones reales de comerciantes en punto de venta retail.
  - Datos curiosos de la historia de la tecnología, anécdotas de empresas y retail moderno.
- **Banco de Assets**: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/` (20 imágenes).

---

## 4. Motores de Video: Veo vs. Flow Continuo

### Motor A: Google Veo (Toma Única Cinemática de 5 a 8s)
- **Objetivo**: Gancho de apertura y clips cortos de alto impacto visual.
- **Formato**:
  ```text
  [GOOGLE VEO PROMPT]
  Aspect Ratio: 9:16 | Duration: 5-8s | FPS: 24fps
  Prompt: [Prompt cinematográfico continuo en inglés con sujeto, acción, cámara, iluminación y render 3D Pixar/DreamWorks]
  Character Seed Image: [Ruta absoluta al archivo JPG local de la mascota]

  Guion de Locución (Voiceover en Español - Cero Emojis | 15-20s):
  "[Texto conciso en español calculado para locución profesional]"
  ```

### Motor B: Google Flow (Continuidad Secuencial en Bloques de 10 Segundos)
- **Objetivo**: Videos largos y continuos (20s, 30s, 40s, 60s) manteniendo continuidad física, vestuario idéntico y cámara emparejada.
- **Para CADA bloque de 10 segundos**:
  1. `Start Keyframe`: Ruta absoluta a la imagen de anclaje inicial.
  2. `Character Anchor`: Imagen canónica de la mascota para fijar rasgos.
  3. `Pose Objetivo al Segundo 10`: Posición final del plano.
  4. `Prompt para Google Flow`: En inglés cinematográfico coordinando acción y trayectoria de cámara.
  5. `Diálogo Sincronizado`: Exactamente entre **20 y 26 palabras en español** para durar los 10 segundos en voz en off.
  6. `Conector de Continuidad`: Indicación técnica de montaje (Match Cut, corte por movimiento, swipe de interfaz).

---

## 5. Carruseles (4:5 — 1080x1350 px) y Portadas Destacadas

- **Slide 1 (Portada Destacable con Mascota)**:
  - Imagen sugerida del banco local con la mascota titular en plano medio.
  - Badge superior: `[COLUMNA X — TEMÁTICA]`.
  - Titular principal en mayúsculas (máximo 6 palabras).
  - Subtítulo de gancho.
- **Slides 2 a N-1**: Desarrollo conceptual, código en JetBrains Mono, diagramas o memes.
- **Slide Final**: Resumen ejecutivo en 3 viñetas geométricas (`▪`) y CTA unívoco.

---

## 6. Copywriting Oficial del Post (Cero Emojis)
- Badge y Titular.
- Gancho inicial directo.
- Argumentación técnica bajo fórmula PAS (Problema - Agitación - Solución).
- Llamado a la acción (CTA) directo.
- Hashtags limpios de marca: `#Alcore #GuatemalaTech #CloudComputing #DevOpsLATAM #Kinvo #KinvoExpress #IngenieriaDeSoftware`.

---

## 7. Herramientas y Recursos Vinculados
- Script de Validación: `python3 scripts/alcore_validator.py <archivo.md>`
- Style Bible 3D: `references/style-bible-3d.md`
- Calendario 30 Días: `references/calendario-editorial-30-dias.md`
- Checklist de Calidad: `references/checklist-calidad-publicacion.md`
- Banco de Mascotas Completo: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/`
- Portadas WhatsApp y Telegram: `/Users/macbookpro/Documents/ALCORE/PORTADAS/`
