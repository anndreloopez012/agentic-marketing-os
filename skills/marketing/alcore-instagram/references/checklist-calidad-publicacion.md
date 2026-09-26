# CHECKLIST DE CONTROL DE CALIDAD PRE-PUBLICACION (@alcore.gt)

Antes de programar o publicar cualquier pieza visual, carrusel o video en el perfil de Instagram de ALCORE, el equipo o el agente debe auditar los siguientes 7 puntos de control de calidad institucional:

---

## 1. Verificación de Columna y Anfitrión Mandatorio
- [ ] ¿La pieza corresponde a la columna correcta según el grid vertical?
  - Columna 1 (Izquierda): **KIVO** (Kinvo Suite, Express o Prensa Tech).
  - Columna 2 (Centro): **ALKI** (Educación IA, Lenguajes de Programación o Git).
  - Columna 3 (Derecha): **KIVI** (Memes Inteligentes o Datos Curiosos).
- [ ] ¿Aparece la mascota titular en la **portada destacable** (Slide 1 o thumbnail del Reel)?

---

## 2. Auditoría Estricta de Cero Emojis
- [ ] ¿El texto del copy está completamente libre de emojis?
- [ ] ¿Los slides del carrusel están completamente libres de emojis?
- [ ] ¿El guion de locución y los subtítulos del video están libres de emojis?
- [ ] ¿Se utilizaron viñetas geométricas (`•`, `▪`, `—`) y corchetes en lugar de pictogramas?
- *(Ejecutar `python3 scripts/alcore_validator.py <archivo.md>` para confirmación automática)*.

---

## 3. Calidad Visual y Proporción
- [ ] Carruseles e imágenes estáticas: Formato vertical 4:5 (1080 x 1350 px).
- [ ] Videos y Reels: Formato vertical 9:16 (1080 x 1920 px).
- [ ] Zona de recorte 1:1 segura: En la cuadrícula cuadrada del perfil, ¿el rostro de la mascota y el titular principal quedan visibles sin cortarse?

---

## 4. Legibilidad Tipográfica Suiza
- [ ] Titulares: Tipografía Inter o Plus Jakarta Sans en peso ExtraBold o Bold.
- [ ] Código fuente, precios y comandos: Tipografía JetBrains Mono.
- [ ] Contraste: Texto Pure Ice White (`#FFFFFF`) sobre fondos oscuros (Obsidian Navy `#0A0F1D` o Alcore Royal Blue `#0B47D9`), o texto oscuro sobre fondos claros.
- [ ] Tamaño mínimo de texto: Mínimo 24pt en arte final para lectura fluida en móviles.

---

## 5. Auditoría de Audio y Métrica de Google Flow (Si es Video)
- [ ] Si es video generado en Google Flow, ¿cada bloque de 10 segundos contiene entre 20 y 26 palabras en español?
- [ ] ¿El ritmo de locución es pausado, formal y comprensible sin sensación de prisa?
- [ ] ¿La música de fondo corporativa está atenuada (ducking a -18dB) durante la voz en off?

---

## 6. Copywriting y Fórmula PAS
- [ ] Badge superior presente: `[COLUMNA X — TEMA]`.
- [ ] Titular en mayúsculas sin signos de exclamación innecesarios.
- [ ] Gancho inicial directo al grano en las primeras dos líneas.
- [ ] Estructura clara: Problema -> Agitación técnica -> Solución de ALCORE.
- [ ] Llamado a la Acción (CTA) unívoco: *"Comenta la palabra [CLAVE]"* o *"Enlace en biografía"*.

---

## 7. Hashtags y Menciones Institucionales
- [ ] ¿Se incluyeron los hashtags oficiales limpios?
  `#Alcore #GuatemalaTech #CloudComputing #DevOpsLATAM #Kinvo #KinvoExpress #IngenieriaDeSoftware`
- [ ] ¿Se verificó que los enlaces a `https://alcore-gt.com/` o `https://kinvo.alcore-gt.com/` estén vigentes y funcionales?
