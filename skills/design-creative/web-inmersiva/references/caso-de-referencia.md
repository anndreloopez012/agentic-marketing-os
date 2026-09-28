# Caso de referencia: mascota interactiva en una landing SaaS

Caso real anonimizado. La marca, los nombres y las rutas se reemplazaron por genéricos; los
números y las lecciones son los originales.

Pedido: "animación dinámica que reaccione al mouse para la mascota en esta sección de la
landing, que resalte" + "otra página en el menú que explique el porqué de cada cosa, full
inmersiva, con los videos de Higgsfield necesarios". Fuente: manual de marca en PDF.

Stack: React 19, Vite 5, framer-motion 12, Express 5 en producción.

## Resultado

**Sección de la portada** (`#mascota`):

- La mascota grande y sin fondo sobre una plataforma holográfica.
- Gira la mirada hacia el cursor con inercia.
- Vigila solo cuando el cursor está quieto y en táctil sigue el scroll.
- Al tocarla saluda y dice frases del manual, con el color del tono.
- El riel lateral y el menú suman la página de la mascota.

**Página `/mascota`**:

1. Portada con video en bucle.
2. "Por qué este animal", con el ADN de la marca y un manifiesto que se revela con el scroll.
3. Anatomía fijada: la mascota se enciende pieza por pieza (pelaje, orejas, visor, medallón),
   cada una con su porqué, su color y un video de detalle.
4. Paleta con copiado de color.
5. Tres roles en acordeón.
6. Conversación de ejemplo.
7. La mascota en vivo.
8. Cierre con el lema.

## Archivos (orden de magnitud)

| Archivo | Líneas |
|---|---|
| `components/mascota/MascotaInteractiva.tsx` | ~450 |
| `components/mascota/mascota-interactiva.css` | ~450 |
| `components/mascota/secuenciaDeFotogramas.ts` | ~130 |
| `components/mascota/frases.ts` / `medios.ts` | ~25 / ~35 |
| `pages/MascotaPage.tsx` / `mascota-page.css` | ~1150 / ~1400 |
| `scripts/componer_alfa.py` / `preparar_medios.py` / `qa.mjs` | ~180 / ~290 / ~280 |

## Medios

- Referencia: el render oficial 1024×1024 del manual de marca.
- Mirada: 2 clips 1080p de 5 s (uno por lado) + recortes → 49 fotogramas (24 por lado +
  centro), muestreados por cambio visible.
- Saludo: clip 1080p de 5 s con `start_image` = `end_image` + recorte → 61 fotogramas a 12 fps.
- Encendido: imagen "apagada" (edición del render) → clip 1080p de 8 s hasta el render
  → 65 fotogramas opacos. Tiempos medidos por pieza: 0.109, 0.451, 0.539, 0.829.
- Portada: imagen 16:9 → clip 1080p de 8 s → bucle de ida y vuelta de 16 s (1.6 MB) y
  versión ligera de 960 px.
- 4 detalles y 3 roles: imagen base → clip 720p de 5 s → bucle con fundido.
- Costo total: ~530 créditos de Higgsfield. Crudos guardados fuera del repo.

## Números

- 61 fps con el bucle activo; chunk de la página de 8.6 KB JS + 5.1 KB CSS (gzip).
- La portada baja 2.3 MB (escritorio) o 1 MB (móvil) de mirada; el saludo, solo con intención.
- QA: cero errores de consola, cero medios fallidos, encabezado correcto de 320 a 1280 px.

## Lo que se corrigió durante la verificación

1. Encabezado roto en teléfonos: el selector de tema no se puede achicar por la regla de
   48 px; los botones secundarios se ocultan bajo 400 px y el avatar bajo 360 px.
2. Título de sección de 5 líneas → escala tipográfica menor y `max-width: 16ch`.
3. La pista de texto chocaba con la plataforma.
4. La mascota no llegaba al giro completo hacia un lado → escala por lado.
5. Rectángulo detrás del título → sombra en el contenedor.
6. Borde del escenario fijado a medias → marco de monitor.
7. Menú oscuro sobre la portada en tema claro → `color` explícito en el encabezado.
8. Ancla que viajaba 1.5 s → `behavior: 'instant'`.
9. Bucles con salto en el último cuadro → fundido contado en fotogramas.

## Git

Tres ramas, cada una funcional por sí sola:

1. `feat/mascota-animada-landing`: medios de la portada, scripts, componente y sección.
2. `feat/pagina-mascota`: página, ruta, encabezado compartido y botón a la página.
3. `feat/mascota-qa`: script de QA.
