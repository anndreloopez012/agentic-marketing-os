---
name: web-scraping-pro
description: Autonomous and programmatic web scraping, content harvesting, and clean structured data extraction for marketing research, competitor pricing, SEO audits, lead intelligence, and LLM feeding. Covers static HTTP extraction (BeautifulSoup, Cheerio), dynamic browser scraping (Playwright, Agent-Browser, CDP), clean Markdown conversion, sitemap crawling, anti-detection stealth practices, and structured JSON output.
metadata:
  short-description: Extracción avanzada de datos web, scraping de catálogos, artículos a Markdown y rastreo de competidores.
  tags: web-scraping, data-extraction, playwright, markdown, pricing, sitemap, lead-generation
---

# Web Scraping Pro

Framework y directivas maestras para extracción automatizada, estructuración y saneamiento de datos web orientados a inteligencia de mercado, auditorías SEO y espionaje de competidores.

---

## 1. Cuándo Utilizar esta Habilidad

Usa esta habilidad siempre que necesites:
- Extraer catálogos completos de productos, listas de precios y variantes de la competencia.
- Convertir páginas web, blogs y documentación en Markdown limpio sin menús, anuncios ni código residual para alimentar LLMs.
- Rastrear sitemaps XML (`sitemap.xml`) para mapear la arquitectura completa del sitio de un rival.
- Extraer opiniones, testimonios y reseñas de clientes (Trustpilot, Google Maps, Amazon, Shopify).
- Recolectar datos de contacto públicos (emails, teléfonos, enlaces de redes sociales) para prospección B2B.
- Monitorear cambios de precios y stock en tiendas de e-commerce.

---

## 2. Los 3 Métodos de Extracción según la Arquitectura Web

| Método | Casos de Uso | Velocidad | Herramientas |
|---|---|---|---|
| **A. Estático (HTTP / HTML)** | Páginas server-rendered (SSR), blogs de WordPress, documentación, sitemaps. | Ultra rápida (< 1s) | Python `urllib`, `requests`, `BeautifulSoup4`, Node `cheerio`. |
| **B. Dinámico / SPA** | Sitios en React, Vue, Angular, con scroll infinito, renderizado del lado del cliente o shadow DOM. | Moderada (2-5s) | `agent-browser`, Playwright, Puppeteer, Chrome DevTools Protocol (CDP). |
| **C. APIs Ocultas / Red** | Cuando el sitio carga datos mediante peticiones `fetch`/`xhr` a endpoints JSON internos. | Instantánea | Inspección de red (Network tab) y llamada directa al endpoint JSON. |

---

## 3. Protocolo de Extracción a Markdown Limpio (Clean Markdown)

Cuando se extrae un artículo o página web para investigación o análisis con IA, **nunca** guardes el HTML crudo. Convierte a Markdown semántico:

1. **Eliminar elementos de ruido**:
   - `<nav>`, `<header>`, `<footer>`, `<aside>`, `.sidebar`, `.ads`, `.cookie-banner`, `<script>`, `<style>`.
2. **Preservar estructura de valor**:
   - `<h1>` a `<h6>` (jerarquía de encabezados).
   - `<table>` (tablas de precios y comparativas intactas).
   - `<ul>` / `<ol>` (listas de características y viñetas).
   - Metadatos: Título, Autor, Fecha de publicación, URL canónica, Meta descripción.

---

## 4. Scripts Utilitarios Incluidos

### A. Extractor de URL a Markdown (`scripts/scrape_to_markdown.py`)
Convierte cualquier URL pública en un archivo Markdown limpio con metadatos estructurados en formato YAML frontmatter:

```bash
python3 skills/research-intelligence/web-scraping-pro/scripts/scrape_to_markdown.py "https://ejemplo.com/articulo" -o articulo.md
```

### B. Rastreador de Sitemap XML (`scripts/crawl_sitemap.py`)
Descarga e indexa todas las URLs de un competidor a partir de su sitemap:

```bash
python3 skills/research-intelligence/web-scraping-pro/scripts/crawl_sitemap.py "https://competidor.com/sitemap.xml" -o urls_competidor.txt
```

---

## 5. Buenas Prácticas de Evasión de Bloqueos y Respeto Web

1. **Rotación de User-Agents Modernos**: Utilizar cadenas de navegadores reales (Chrome en macOS/Windows) y evitar identificadores genéricos de bots (`python-requests`, `curl`).
2. **Encabezados HTTP Mínimos**:
   ```python
   headers = {
       "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
       "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   }
   ```
3. **Pausas Humanas (Throttling)**: Agregar retardos aleatorios entre 1.5s y 4s entre peticiones consecutivas para no sobrecargar el servidor del competidor.
4. **Respeto a Políticas y Datos Personales**: Extraer únicamente datos públicos con fines legítimos de benchmarking competitivo y análisis de mercado.

---

## 6. Integración con Agent-Browser

Para sitios protegidos por Cloudflare, botones que requieren interacción previa o inicios de sesión, combina este skill con `agent-browser`:
```bash
# Abrir y esperar carga completa de JavaScript
agent-browser open "https://competidor.com/catalogo"
agent-browser wait --load
# Extraer el DOM accesible o capturar texto
agent-browser snapshot -c
```
