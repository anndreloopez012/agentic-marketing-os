---
name: seo-expert
description: Use when the user needs SEO work — technical SEO audits, on-page optimization, keyword research, content SEO, local SEO, link building strategy, Core Web Vitals, structured data/schema, sitemap/robots.txt, SEO for Next.js/React/Strapi, or interpreting Google Search Console and Analytics data. Also use when the user says "posicionamiento", "aparecer en Google", "optimizar para buscadores", "SEO técnico", "palabras clave", or "mejorar el ranking".
metadata:
  short-description: SEO técnico, on-page, local y de contenido — auditorías, keywords y optimización completa.
---

# SEO Expert

Cobertura completa de SEO: técnico, on-page, off-page, local, de contenido y para frameworks modernos (Next.js, React, Strapi).

---

## 1. SEO Técnico

### Core Web Vitals (CWV)
| Métrica | Meta | Cómo optimizar |
|---|---|---|
| **LCP** (Largest Contentful Paint) | < 2.5s | Optimizar imágenes, preload hero, CDN, SSR |
| **INP** (Interaction to Next Paint) | < 200ms | Reducir JS en main thread, code splitting |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Dimensiones explícitas en imágenes/ads, font-display |

### Checklist técnico
- [ ] HTTPS en todo el sitio
- [ ] Sitemap XML en `/sitemap.xml` y declarado en robots.txt
- [ ] `robots.txt` correcto — no bloquear recursos CSS/JS
- [ ] Canonical tags en páginas con contenido duplicado
- [ ] Hreflang para sitios multiidioma
- [ ] URLs limpias y descriptivas (sin parámetros innecesarios)
- [ ] Paginación correcta (`rel="next"` / `rel="prev"` o `?page=N`)
- [ ] Redirects 301 correctos (no cadenas de redirects)
- [ ] Sin errores 404 no manejados
- [ ] Velocidad de carga < 3s en móvil
- [ ] Mobile-first indexing — el sitio funciona perfecto en móvil
- [ ] Structured data (Schema.org) implementado
- [ ] Open Graph y Twitter Cards para social sharing

### SEO para Next.js / React
```jsx
// Next.js 13+ App Router — metadata estática
export const metadata = {
  title: 'Título de página | Marca',
  description: 'Descripción de 150-160 chars con keyword principal',
  keywords: ['keyword1', 'keyword2'],
  openGraph: {
    title: 'Título OG',
    description: 'Descripción OG',
    images: [{ url: '/og-image.jpg', width: 1200, height: 630 }],
  },
  robots: { index: true, follow: true },
  alternates: { canonical: 'https://tudominio.com/esta-pagina' },
}

// Metadata dinámica
export async function generateMetadata({ params }) {
  const data = await fetch(`/api/producto/${params.slug}`)
  return {
    title: `${data.nombre} | Tienda`,
    description: data.descripcion.slice(0, 160),
  }
}
```

```jsx
// Structured Data (JSON-LD) en Next.js
export default function ProductoPage({ producto }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: producto.nombre,
    description: producto.descripcion,
    image: producto.imagen,
    offers: {
      '@type': 'Offer',
      price: producto.precio,
      priceCurrency: 'GTQ',
      availability: 'https://schema.org/InStock',
    },
  }
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      {/* ... */}
    </>
  )
}
```

---

## 2. Investigación de Keywords

### Framework de clasificación
| Tipo | Intent | Ejemplo | Prioridad |
|---|---|---|---|
| **Transaccional** | Comprar ahora | "comprar software CRM Guatemala" | Alta — convierte |
| **Comercial** | Comparar opciones | "mejor CRM para pymes Guatemala" | Alta — near-convert |
| **Informacional** | Aprender | "qué es un CRM" | Media — tráfico |
| **Navegacional** | Buscar marca | "NombreDeTuMarca CRM" | Baja — ya te conocen |

### Proceso de investigación
1. **Seed keywords**: 5-10 términos base del negocio.
2. **Expansión**: usar Google Autocomplete, "People also ask", Google Trends.
3. **Análisis**: volumen de búsqueda, dificultad (KD), intent.
4. **Priorización**: alta intención + baja competencia = ganar primero.
5. **Mapeo**: una keyword principal por página + 2-3 secundarias.

### Métricas clave
- **Volumen mensual**: mínimo 100/mes para mercados pequeños (Guatemala/LATAM)
- **KD (Keyword Difficulty)**: empezar con KD < 30 si el sitio es nuevo
- **CPC**: indica valor comercial — mayor CPC = keyword más valiosa para el negocio

---

## 3. On-Page SEO

### Estructura de página optimizada
```
H1 — Keyword principal (1 sola vez por página)
  H2 — Subtema 1 (keyword secundaria)
    H3 — Detalle
  H2 — Subtema 2
    H3 — Detalle
```

### Title tag
- 50-60 caracteres
- Keyword principal al inicio
- Marca al final
- Formato: `Keyword Principal | Nombre de Marca`

### Meta description
- 150-160 caracteres
- Incluye keyword principal naturalmente
- Termina con CTA: "Descúbrelo aquí →" o "Solicita tu demo gratis"
- No se usa para ranking directo pero impacta CTR

### Optimización de imágenes
- Nombre de archivo descriptivo: `software-crm-guatemala.webp`
- Alt text: descriptivo y natural, incluye keyword cuando aplique
- Formato: WebP (mejor compresión que JPG/PNG)
- Lazy loading para imágenes fuera del viewport inicial
- Preload para la imagen hero (LCP)

### Densidad de keywords
- No forzar: 1-2% de densidad máxima
- Usar variaciones semánticas (LSI keywords)
- Distribuir naturalmente en: H1, primeros 100 palabras, H2/H3, último párrafo

---

## 4. SEO Local (Guatemala / LATAM)

### Google Business Profile
- Verificar y completar al 100%: nombre, dirección, teléfono, horario, categorías
- Agregar fotos reales del negocio (mínimo 10)
- Responder TODAS las reseñas (positivas y negativas)
- Posts regulares (mínimo 1 por semana)
- Preguntas y respuestas: añadir las más comunes

### NAP Consistency
**Name, Address, Phone** — deben ser IDÉNTICOS en:
- Sitio web (footer)
- Google Business Profile
- Directorios locales
- Redes sociales
- Cualquier mención online

### Keywords locales
- Incluir ciudad/país en keywords: "software CRM Guatemala"
- Crear páginas de servicio por zona si aplica
- Markup de LocalBusiness en Schema.org

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Nombre del Negocio",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Calle X",
    "addressLocality": "Ciudad de Guatemala",
    "addressCountry": "GT"
  },
  "telephone": "+502-XXXX-XXXX",
  "url": "https://tudominio.com",
  "openingHours": "Mo-Fr 08:00-17:00"
}
```

---

## 5. SEO de Contenido

### Fórmula de artículo SEO
1. **Keyword en título** (H1) — exacta o muy cercana
2. **Intro de 100 palabras** — responde la pregunta directamente (para featured snippets)
3. **Cuerpo estructurado** con H2/H3
4. **Contenido completo** — cubre el tema más profundo que la competencia
5. **FAQ al final** — captura "People Also Ask"
6. **CTA** — siguiente paso claro

### Estrategia de pillar + cluster
```
Pillar Page: "Guía completa de CRM para empresas"
  └── Cluster: "Cómo implementar un CRM paso a paso"
  └── Cluster: "Los 5 mejores CRM para pymes en Guatemala"
  └── Cluster: "CRM vs ERP: ¿cuál necesita tu empresa?"
  └── Cluster: "Cómo migrar de Excel a un CRM"
```

### Internal linking
- Cada artículo debe tener 3-5 internal links relevantes
- Los links deben tener anchor text descriptivo (no "click aquí")
- Enlazar desde páginas con más autoridad a las que quieres rankear

---

## 6. Auditoría SEO rápida

Cuando el usuario pide una auditoría, evalúa en este orden:
1. **Rastreabilidad**: robots.txt, sitemap, indexación en Google (`site:dominio.com`)
2. **Técnico**: HTTPS, velocidad, mobile-friendliness, CWV
3. **On-page**: titles, metas, estructura H1-H6, ALT tags
4. **Contenido**: calidad, profundidad, keyword targeting
5. **Links**: internal linking, backlinks tóxicos, autoridad de dominio
6. **Local**: GBP, NAP consistency (si aplica)

Entrega el reporte en tabla con: Problema | Impacto (Alto/Medio/Bajo) | Acción correctiva | Prioridad

---

## 7. Interpretación de Search Console

### Métricas principales
- **Impresiones**: cuántas veces aparece en resultados
- **Clics**: cuántas veces dan click
- **CTR**: clics/impresiones — bajo CTR = mejorar title/meta
- **Posición promedio**: posición 1-10 = primera página

### Alertas a revisar
- Páginas con muchas impresiones y bajo CTR → mejorar title y meta
- Páginas en posición 8-15 → contenido más profundo = salto a top 5
- Errores de indexación → corregir inmediatamente
- Caídas bruscas de tráfico → penalización o cambio de algoritmo
