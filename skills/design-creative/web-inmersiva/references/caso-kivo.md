# Caso: Kivo en la landing de KINVO (2026-09-17)

Pedido: "animación dinámica que reaccione al mouse para la mascota en esta sección de la
landing, que resalte" + "otra página en el menú que explique el porqué de cada cosa, full
inmersiva, con los videos de Higgsfield necesarios". Fuente: manual de marca en PDF.

Proyecto: `core-strapi` (React 19, Vite 5, framer-motion 12, Express 5 en producción).
Notas en Obsidian: `Marcas/KINVO/Kivo`, `Kivo - Implementación web`,
`Kivo - Medios y generación` y las decisiones `Kivo - fotogramas en canvas en lugar de video`
y `Kivo - ruta publica y encabezado compartido`.

## Resultado

**Sección de la portada** (`#kivo-copilot`):

- Kivo grande y sin fondo sobre una plataforma holográfica.
- Gira la mirada hacia el cursor con inercia.
- Vigila solo cuando el cursor está quieto y en táctil sigue el scroll.
- Al tocarlo saluda y dice frases del manual, con el color del tono.
- El riel lateral y el menú suman "Kivo".

**Página `/kivo`**:

1. Portada con video en bucle.
2. "Por qué un zorro", con el ADN de la marca y un manifiesto que se revela con el scroll.
3. Anatomía fijada: Kivo se enciende pieza por pieza (pelaje, orejas, visor, medallón), cada
   una con su porqué, su color y un video de detalle.
4. Paleta con copiado de color.
5. Tres roles en acordeón.
6. Conversación de ejemplo.
7. Kivo en vivo.
8. Cierre con el lema.

## Archivos

| Archivo | Líneas |
|---|---|
| `src/components/brand/kivo/KivoInteractivo.tsx` | 446 |
| `src/components/brand/kivo/kivo-interactivo.css` | 456 |
| `src/components/brand/kivo/secuenciaDeFotogramas.ts` | 127 |
| `src/components/brand/kivo/frasesDeKivo.ts` / `kivoMedios.ts` | 23 / 35 |
| `src/components/landing/KinvoPublicHeader.tsx` | 106 |
| `src/pages/KivoPage.tsx` / `kivo-page.css` | 1166 / 1407 |
| `scripts/kivo/componer_alfa.py` / `preparar_medios.py` / `qa-kivo.mjs` | 180 / 286 / 283 |

Además cambiaron `HomeLanding.tsx`, `home-landing.css`, `App.tsx`,
`ProtectedLandingRoute.tsx` y `server.mjs`.

## Medios

- Referencia: el render oficial 1024×1024 (del repo; el mismo que trae el PDF).
- Mirada: 2 clips 1080p de 5 s (uno por lado) + recortes → 49 fotogramas (24 por lado +
  centro), muestreados por cambio visible.
- Saludo: clip 1080p de 5 s con `start_image` = `end_image` + recorte → 61 fotogramas a 12 fps.
- Encendido: imagen "apagada" (edición del render) → clip 1080p de 8 s hasta el render
  → 65 fotogramas opacos. Tiempos medidos: pelaje 0.109, orejas 0.451, visor 0.539,
  medallón 0.829.
- Portada: imagen 16:9 → clip 1080p de 8 s → bucle de ida y vuelta de 16 s (1.6 MB) y
  versión ligera de 960 px.
- 4 detalles y 3 roles: imagen base → clip 720p de 5 s → bucle con fundido.
- Costo: 529.5 créditos. Crudos en `Documents/KINVO/kivo-medios-crudos/`.

## Números

- 61 fps con el bucle activo; chunk de `/kivo` de 8.6 KB JS + 5.1 KB CSS (gzip).
- La portada baja 2.3 MB (escritorio) o 1 MB (móvil) de mirada; el saludo, solo con intención.
- Build de producción: `/kivo` 200, video 206, precache sin medios.
- QA: cero errores de consola, cero medios fallidos, encabezado correcto de 320 a 1280 px,
  ancla a 78 px.

## Lo que se corrigió durante la verificación

1. Encabezado roto en teléfonos (ya lo estaba antes): el selector de tema no se puede
   achicar por la regla de 48 px; "Ver planes" sale bajo 400 px y el avatar de Kivo bajo
   360 px.
2. Título de la sección de 5 líneas → `step-3` y 16ch.
3. La pista de texto chocaba con la plataforma.
4. Kivo no llegaba al giro completo hacia la derecha → escala por lado.
5. Rectángulo detrás del título "KIVO" → sombra en el contenedor.
6. Borde del escenario fijado a medias → marco de monitor.
7. Menú oscuro sobre la portada en tema claro → `color` en el encabezado.
8. Ancla que viajaba 1.5 s → `behavior: 'instant'`.
9. Bucles con salto en el último cuadro → fundido contado en fotogramas.

## Git

Tres ramas, cada una funcional por sí sola:

1. `feat/kivo-animado-landing`: medios de la portada, scripts, componente y sección, con el
   botón original (la ruta todavía no existe).
2. `feat/pagina-kivo`: página, ruta, encabezado compartido, servidor y botón a `/kivo`.
3. `feat/kivo-qa`: script de QA.

Las tres se integraron con `--no-ff` en `dev` y `main` avanzó en fast-forward, sin
atribución de herramientas.
