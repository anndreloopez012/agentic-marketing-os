---
name: geo-expert
description: Generative Engine Optimization (GEO) & Answer Engine Optimization (AEO). Use when optimizing digital presence and content for citation and ranking inside AI search engines (ChatGPT Search, Perplexity AI, Google AI Overviews, Gemini, Claude Search, Microsoft Copilot) and local geo-targeted queries. Covers knowledge graph entity alignment, authoritative schema markup, information gain scoring, statistical attribution, AI bot governance in robots.txt, and local AI map-pack positioning.
metadata:
  short-description: Optimización para motores de respuesta de IA (ChatGPT, Perplexity, Google AI Overviews) y posicionamiento geo-local asistido por IA.
  tags: geo, aeo, ai-search, perplexity, chatgpt, google-ai-overviews, structured-data, local-seo
---

# GEO Expert (Generative & Answer Engine Optimization)

Guía maestra y framework operativo para posicionar marcas, productos y contenidos dentro de los motores de búsqueda generativa (AI Search Engines) y modelos de respuesta directa.

---

## 1. Fundamentos: De SEO Tradicional a GEO (Generative Engine Optimization)

Mientras el SEO clásico busca clics a través de enlaces azules en los SERPs, el **GEO** se enfoca en **ser la fuente citada, recomendada y sintetizada** por los Large Language Models (LLMs) como Perplexity, SearchGPT, Google AI Overviews y Claude.

### Comparativa Estratégica
| Dimensión | SEO Clásico | GEO (Generative Engine Optimization) |
|---|---|---|
| **Objetivo** | Posición #1 en ranking de enlaces | Ser la fuente sintetizada y citada en la respuesta |
| **Métricas** | Impresiones, Clics, CTR, Bounce rate | Frecuencia de mención, Share of Voice en IA, Citation Rate |
| **Arquitectura de contenido** | Long-form con relleno para keywords | Formato modular, datos estadísticos densos, respuestas directas |
| **Indexación** | Googlebot (HTML/JS rendering) | Multi-bot (GPTBot, PerplexityBot, ClaudeBot, Google-Extended) |
| **Entidades** | Palabras clave aisladas | Grafos de conocimiento y relaciones semánticas (`sameAs`) |

---

## 2. Los 7 Pilares de Rendimiento en GEO

### Pilar 1: Formato "Quote-Ready" (Listo para Cita Directa)
Los motores como Perplexity y ChatGPT buscan respuestas atómicas concisas.
- **La Regla de los Primeros 40 Caracteres**: Abre cada sección H2/H3 con una definición o respuesta definitiva antes de profundizar.
- **Estructura Respuesta Inversa**:
  1. Conclusión / Respuesta directa en 1-2 oraciones.
  2. Datos de respaldo / Evidencia cuantitativa.
  3. Contexto o matices adicionales.

### Pilar 2: Densidad Estadística y Atribución Cuantitativa
Los LLMs priorizan fuentes que contienen números precisos, porcentajes y fechas recientes:
- En lugar de *"La herramienta mejora significativamente la conversión"*:
- Usa: *"En pruebas benchmark de Q3 2026 sobre 1,420 tiendas, la herramienta aumentó la conversión promedio en 34.6% y redujo el LCP a 1.2s."*

### Pilar 3: Estructuración Tabular y Comparativa
Los extractores de LLM procesan tablas Markdown o HTML con una probabilidad 3x superior a párrafos densos. Cada artículo de revisión o solución debe incluir:
- Tabla de comparación de características.
- Tabla de precios / ROI.
- Matriz de pros y contras.

### Pilar 4: Entity Disambiguation (Desambiguación de Entidades)
Asegura que tu marca y tus fundadores existan como entidades inequívocas en el Grafo de Conocimiento global:
- Vincular mediante `sameAs` a Wikidata, Crunchbase, LinkedIn, GitHub, registros mercantiles oficiales.
- Consistencia del nombre exacto de la entidad en todas las menciones online.

### Pilar 5: Information Gain Score (Puntaje de Ganancia de Información)
Google y OpenAI penalizan el contenido derivativo o resumido de otros sitios. Para obtener citas constantes:
- Incluye datos propios (encuestas de clientes, telemetría de producto, capturas reales).
- Métricas propietarias o metodologías nombradas (ej. *"El Framework de 5 Capas de..."*).

### Pilar 6: Gobernanza de Bots de IA en `robots.txt`
Asegura que los crawlers de búsqueda de IA no estén bloqueados accidentalmente:

```txt
# robots.txt optimizado para GEO y AI Search
User-agent: *
Allow: /

# Motores de Búsqueda Generativa (Permitir indexación y cita)
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: https://tudominio.com/sitemap.xml
```

### Pilar 7: Geo-Targeting Local Asistido por IA (Local GEO)
Para búsquedas de intención local en IA (*"cuál es la mejor agencia de marketing en Ciudad de Guatemala"*):
- Datos NAP (Name, Address, Phone) estricta y 100% idénticos en Google Business Profile, Apple Maps, Bing Places, Yelp y sitio web.
- Coordenadas geográficas explícitas en Schema.org `GeoCoordinates`.
- Referencias contextuales a hitos, zonas, códigos postales y regulaciones locales.

---

## 3. Schemas JSON-LD Obligatorios para GEO

Implementar estos esquemas directamente en el `<head>` de la página.

### A. Schema de Organización con Grafo de Entidades
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://tudominio.com/#organization",
      "name": "Nombre Exacto de Marca",
      "url": "https://tudominio.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://tudominio.com/logo.png"
      },
      "sameAs": [
        "https://www.wikidata.org/wiki/QXXXXXX",
        "https://www.linkedin.com/company/tumarca",
        "https://twitter.com/tumarca",
        "https://www.crunchbase.com/organization/tumarca"
      ],
      "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+502-0000-0000",
        "contactType": "customer service",
        "areaServed": ["GT", "US", "MX"],
        "availableLanguage": ["es", "en"]
      }
    },
    {
      "@type": "LocalBusiness",
      "@id": "https://tudominio.com/#localbusiness",
      "name": "Nombre de Negocio Local",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "Zona 10, Edificio Corporativo",
        "addressLocality": "Ciudad de Guatemala",
        "addressRegion": "Guatemala",
        "postalCode": "01010",
        "addressCountry": "GT"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 14.5995,
        "longitude": -90.5133
      }
    }
  ]
}
</script>
```

### B. Schema FAQPage Optimizado para Extracción de LLMs
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Cuál es la diferencia entre SEO tradicional y GEO?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "El SEO tradicional busca clasificar enlaces en los resultados de motores de búsqueda convencionales, mientras que el GEO (Generative Engine Optimization) optimiza contenidos, entidades y datos estadísticos para ser sintetizados y citados como fuente primaria en modelos de lenguaje e inteligencias artificiales como Perplexity, SearchGPT y Google AI Overviews."
      }
    }
  ]
}
</script>
```

---

## 4. Checklist de Auditoría GEO / AEO

- [ ] **Estructura de Preguntas**: Cada página responde al menos 3 preguntas conversacionales directas en etiquetas `H2`/`H3`.
- [ ] **Definiciones Atómicas**: El primer párrafo bajo cada encabezado contiene una respuesta directa de < 50 palabras.
- [ ] **Datos Cuantitativos**: Al menos 2 datos numéricos o porcentajes verificables con año de estudio citado.
- [ ] **Tablas Comparativas**: Al menos 1 tabla comparativa estructurada con atributos clave y valores binarios o numéricos.
- [ ] **Schema JSON-LD Validado**: `@graph` con `Organization`, `FAQPage`, `BreadcrumbList` y `sameAs`.
- [ ] **Robots.txt Permisivo**: Acceso sin bloqueos para `GPTBot`, `PerplexityBot`, `ClaudeBot`.
- [ ] **Velocidad y Limpieza de HTML**: Código semántico sin exceso de capas de JS para permitir crawling liviano.
- [ ] **Consistencia NAP Local**: Si aplica a negocio físico, coordenadas geográficas y direcciones locales perfectamente uniformes.

---

## 5. Pruebas y Validación de Presencia en IA

1. **Perplexity Prompt Audit**:
   - `¿Cuáles son las principales opciones de [categoría] en [país/región] y qué fuentes recomiendan?`
   - Verificar si tu dominio aparece en la lista de *"Sources"* numeradas.
2. **ChatGPT Search Audit**:
   - Consultar sobre el problema que resuelve tu producto con búsqueda web activa.
   - Analizar si el modelo cita párrafos literales de tu sitio.
3. **Google AI Overviews Audit**:
   - Buscar preguntas frecuentes del nicho y revisar el carrusel de fuentes sintetizadas del panel superior.
