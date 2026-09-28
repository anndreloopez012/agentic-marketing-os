# Guía del alumno: tu marketing con IA paso a paso

Esta guía sigue el orden del curso. Cada paso dice qué pedirle a tu asistente (Claude Code, Codex/ChatGPT o claude.ai) y qué archivo te queda al terminar. Trabaja siempre dentro de tu carpeta de proyectos (por defecto `~/Documents/MarketingProjects/<tu-marca>`).

> En Claude Code puedes escribir las peticiones tal cual. En Codex puedes mencionar la skill con `$nombre-de-la-skill`. En ChatGPT o claude.ai, sube primero las skills (ver README).

## 0. Prepara tu carpeta

```bash
mkdir -p ~/Documents/MarketingProjects/mi-marca && cd ~/Documents/MarketingProjects/mi-marca
git init
```

Abre tu asistente en esa carpeta.

## Clase 1 — Diagnóstico de marca y cliente ideal

1. **Perfil de marca**
   > Crea el perfil de marca de mi empresa. Mi negocio es [describe en 2 líneas]. Mi sitio o Instagram es [enlace].

   Resultado: `marca/brand-profile.md`. Revísalo y corrige lo que no sea cierto.

2. **Diagnóstico y buyer personas**
   > Con marketing-ia-expert haz el diagnóstico de mi marca, 3 buyer personas y una matriz de mis 3 competidores principales.

3. **Competencia real** (opcional)
   > Usa social-competitor-intelligence para revisar los anuncios activos de [competidor] en la biblioteca de anuncios de Meta y resume qué ángulos repiten.

4. **Propuesta de valor**
   > Con brand-identity y copywriting-pro redacta 3 versiones de mi propuesta de valor y recomienda una.

## Clase 2 — Contenido para redes

1. **Pilares y grid**
   > Con instagram-content-suite diseña mi sistema de 3 columnas y mis pilares de contenido.
2. **Calendario**
   > Haz mi calendario de 30 días para Instagram y guárdalo en instagram/.
3. **Piezas del día**
   > Con instagram-content-suite prepara el paquete completo del día 1 del calendario.
4. **Ganchos y guiones**
   > Escribe 30 ganchos y 5 guiones de Reels de 30 segundos para mi marca.
5. **Video con IA**
   > Con google-flow-veo-director arma un Reel de 30 segundos en bloques de 10 s para Google Flow sobre [tema].
6. **Revisión antes de publicar**
   > Audita instagram/2026-10-01-mi-post/caption.md con el linter de instagram-content-suite.

## Clase 3 — Campañas, anuncios y ventas

1. **Oferta y embudo**
   > Con marketing-ia-expert define mi oferta irresistible y un embudo simple desde anuncio hasta WhatsApp.
2. **Anuncios**
   > Con paid-ads estructura una campaña de Meta Ads de 7 días con 10 anuncios y presupuesto de [monto].
3. **Mensajes de venta**
   > Escribe la secuencia de WhatsApp/DM para responder a quien escribe desde el anuncio, con manejo de objeciones.
4. **Landing page**
   > Planifica con shape y construye con frontend-design una landing para mi oferta. Luego pásale audit y polish.
5. **SEO y respuestas de IA**
   > Con seo-expert y geo-expert optimiza la landing para Google y para que ChatGPT y Perplexity la citen.

## Clase 4 — Sistema semanal

1. **Repurposing**
   > Convierte mi mejor carrusel de la semana en un Reel, 3 historias, un email y un post de LinkedIn.
2. **Reporte**
   > Te paso mis métricas de la semana [pega o adjunta]. Haz el reporte con ganadores, puntos débiles, hipótesis y qué probar la próxima semana.
3. **Biblioteca de prompts**
   > Guarda en marca/prompts.md los prompts que mejor funcionaron este mes.
4. **Memoria** (si instalaste Obsidian)
   > Registra en la memoria las decisiones de marca que tomamos hoy.

## Proyecto final

> Con marketing-ia-expert arma mi sistema de marketing de 30 días completo: diagnóstico, cliente, propuesta de valor, ideas, calendario, guiones, copies, anuncios, secuencia de mensajes, métricas y recomendaciones semanales. Guarda cada parte en su archivo.

## Buenas prácticas

- **Revisa siempre.** La IA acelera; tú decides. Corrige datos, precios y promesas.
- **No inventes pruebas.** Si no tienes testimonios o cifras, déjalo marcado y consíguelos.
- **Un cambio a la vez.** Pide ajustes concretos: "haz el titular más corto", "tono más cercano".
- **Guarda lo que funciona.** Actualiza tu perfil de marca cuando confirmes algo nuevo.
- **Claves privadas.** Tus API keys van solo en el archivo `.env`; nunca las pegues en el chat ni en tus notas.
