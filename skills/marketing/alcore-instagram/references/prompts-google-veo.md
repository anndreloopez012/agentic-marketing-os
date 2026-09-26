# GUIA TECNICA: PROMPTS PARA GOOGLE VEO (ALCORE INSTAGRAM)

Esta guía define el protocolo de generación de prompts para **Google Veo** (y modelos afines de toma única como Luma Dream Machine, Runway Gen-3 Alpha o Kling AI), orientados a clips autocontenidos de alto impacto para Reels de Instagram.

---

## 1. Naturaleza de Google Veo
Google Veo está optimizado para generar tomas cinemáticas de alta fidelidad con resolución nativa de hasta 1080p/4K y comprensión avanzada de lenguaje cinematográfico.
- **Rango de Duración**: Clips de 5 a 8 segundos (toma única).
- **Relación de Aspecto**: 9:16 (1080x1920 px para Reels y Stories) o 1:1 (Feed).
- **Enfoque Narrativo**: Apertura de gancho, demostración de autoridad o cierre de impacto.

---

## 2. Estructura Obligatoria del Prompt para Google Veo

```text
[GOOGLE VEO PROMPT]
Aspect Ratio: 9:16 | Duration: [5-8s] | FPS: 24fps
Character Seed: [Nombre de la Mascota], [descripción canónica física, atuendo institucional y rasgos biónicos].
Environment: [Escenario corporativo / nube / mostrador con iluminación volumétrica].
Action: [Acción única y fluida en 5 a 8 segundos: p.ej., saludo formal, escaneo de terminal, señalización de pantalla].
Camera: [Movimiento de cámara: Slow Dolly-In, 30-degree orbital pan, Crane down to medium shot].
Lighting & Atmosphere: Volumetric studio lighting, deep navy and cyan ambient fill, crisp rim light on edges, ray-traced reflections.
Render Style: 3D animated feature film quality, Pixar and DreamWorks character aesthetic, subsurface scattering on fur/skin, tactile materials, zero artifacts.
Image Reference (Start Frame): [Ruta absoluta al archivo JPG local de la mascota]

GUION DE LOCUCIÓN (VOICEOVER EN ESPAÑOL - CERO EMOJIS):
"[Texto conciso de 15 a 20 segundos calculado para locución institucional]"
```

---

## 3. Catálogo de Rutas para Start Frame en Google Veo
- **Kivo (Columna 1)**:
  - Saludo / Onboarding: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVO/10_kivo_onboarding_guide.jpg`
  - Alerta de Datos: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVO/07_kivo_centinela_alert.jpg`
  - Frontal Neutral: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVO/01_kivo_frontal_full.jpg`
- **Alki (Columna 2)**:
  - Maestro / Mentor: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/ALKI/01_alki_frontal_full.jpg`
  - Análisis en Laboratorio: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/ALKI/07_alki_workstation_top.jpg`
  - Autoridad Contrapicado: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/ALKI/08_alki_hero_lowangle.jpg`
- **Kivi (Columna 3)**:
  - Cobro POS / Terminal: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/01_kivi_frontal_full.jpg`
  - Acción Lengua SAT FEL: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/08_kivi_tongue_fel.jpg`
  - Memes / Ojos 360°: `/Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVI/03_kivi_threequarter_right.jpg` o `09_kivi_supervisor_eyes.jpg`
