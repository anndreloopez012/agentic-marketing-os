---
name: social-competitor-intelligence
description: Cross-platform social media competitor spying, ad intelligence, and social listening across Meta (Instagram, Facebook Ads Library), TikTok (Creative Center), YouTube, LinkedIn, and X (Twitter). Use when analyzing rival brand campaigns, discovering winning hooks and formats, reverse-engineering active ads, identifying market gaps from customer complaints, and building competitive intelligence matrices.
metadata:
  short-description: Espionaje ético e inteligencia competitiva en redes sociales y bibliotecas de anuncios.
  tags: competitor-analysis, meta-ads-library, tiktok-creative-center, social-listening, hooks, competitive-matrix
---

# Social Competitor Intelligence

Framework operativo para investigar, auditar y desarmar la estrategia de marketing y contenido de la competencia en todas las redes sociales principales.

---

## 1. Cuándo Utilizar esta Habilidad

Activa esta habilidad cuando el usuario o alumno necesite:
- **Espiar los anuncios activos de cualquier rival** para ver qué creativos y copies les están funcionando.
- **Identificar los ganchos (hooks) y formatos con mayor engagement** en Instagram Reels, TikTok o YouTube Shorts.
- **Descubrir quejas y puntos de dolor insatisfechos** en los comentarios de la competencia para usarlos como ventaja en el copy propio.
- **Auditar la frecuencia, estética y pilares de contenido** de marcas líderes en un nicho.
- **Construir una Matriz de Inteligencia Competitiva** antes de redactar una propuesta o lanzar una campaña.

---

## 2. Metodología por Plataforma

### A. Meta: Instagram & Facebook Ads Library
La **Biblioteca de Anuncios de Meta** es pública y obligatoria para cualquier análisis de pauta:
- **URL Base**: `https://www.facebook.com/ads/library/`
- **Fórmula del Ganador (The Longevity Rule)**:
  - Anuncio activo por **< 7 días**: Prueba creativa / Experimento.
  - Anuncio activo por **> 30 a 90 días**: **Anuncio ganador (Winning Ad)**. Si siguen pagando por él mes tras mes, es porque tiene un ROAS positivo comprobado.
- **Puntos a Auditar en Anuncios**:
  1. *Hook de los primeros 3 segundos* en video (¿texto en pantalla, pregunta polarizante, demostración rápida?).
  2. *Formato visual*: ¿UGC (User Generated Content), estático limpio, carrusel comparativo o video cinematográfico?
  3. *Llamado a la Acción (CTA)*: ¿Lleva a WhatsApp, landing page directa, VSL o descarga de lead magnet?

### B. TikTok & TikTok Creative Center
- **Herramienta Clave**: TikTok Creative Center (`ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en`).
- **Análisis de la Retención (Retention Curve)**:
  - *Segundo 0 a 3*: Gancho visual disruptivo (cambio de ángulo, acción rápida, sonido en tendencia).
  - *Segundo 3 a 15*: Presentación del problema sin rodeos (*"Si eres freelance y sufres con esto..."*).
  - *Segundo 15 a 45*: Demostración de la solución / Prueba social.
  - *Segundo 45 a 60*: CTA claro con urgencia.

### C. YouTube & YouTube Shorts
- **Auditoría de Canal Competidor**:
  1. Ordenar videos por **"Más populares"** (Most Popular) para identificar los dolores nucleares del nicho.
  2. Analizar miniaturas ganadoras: contraste alto, emociones faciales marcadas, texto de máximo 3-4 palabras.
  3. Extraer la estructura de títulos: Fórmulas de curiosidad, advertencia o listas de recursos.

### D. LinkedIn (B2B Competitor Intelligence)
- Auditar perfiles de fundadores vs página de empresa:
  - *Ganchos de texto*: Primeras dos líneas antes del botón "ver más" (contrarian statement, historia personal).
  - *Carruseles en PDF*: Número de diapositivas (óptimo: 8-12 páginas), tamaño de fuente grande y 1 idea clave por slide.

### E. X (Twitter / Threads)
- Búsqueda de menciones con palabras de dolor: `"[nombre competidor]" + "falla" OR "malo" OR "esperando" OR "soporte"`.
- Los reclamos públicos son la mayor mina de oro para el copy de tu cliente (*"A diferencia de otros que tardan 48 horas..."*).

---

## 3. La Matriz de Inteligencia Competitiva

Al concluir la investigación, el agente debe generar un informe estructurado siguiendo la plantilla en `templates/competitor_matrix_template.md`:

```markdown
# Matriz Competitiva: [Nicho / Marca]

| Competidor | Propuesta Central | Formatos Dominantes | Ganchos Ganadores | Debilidad Detectada |
|---|---|---|---|---|
| Rival A | Software de gestión simple | Reels UGC + Meta Ads activos > 60d | "¿Sigues usando Excel para...?" | Soporte lento según comentarios |
| Rival B | Agencia boutique | Carruseles educativos LinkedIn | "La verdad que nadie te dice sobre..." | Precios altos no transparentes |
```

---

## 4. Combinación con Agent-Browser y Web Scraping

1. Usa `agent-browser` para navegar a la Biblioteca de Anuncios de Meta o perfiles públicos.
2. Usa `web-scraping-pro` para extraer transcripciones de video o textos de blogs competidores.
3. Alimenta la información a `copywriting-pro` para crear ángulos de contra-ataque superiores.
