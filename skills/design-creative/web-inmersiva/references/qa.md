# QA de una página inmersiva

No se da nada por terminado sin ejecutarlo en un navegador que pinte de verdad y sin medir lo
que la persona vería. Plantilla: `assets/qa-inmersiva.mjs` (cópiala al proyecto y agrega las
verificaciones propias).

## Entorno

- **Chrome real con Playwright**: `chromium.launch({ channel: 'chrome' })`. El navegador
  integrado del editor deja el documento oculto (`visibilityState === 'hidden'`): no corren
  `IntersectionObserver` ni `requestAnimationFrame`, las capturas salen negras y todo parece
  roto sin estarlo. Los binarios que descarga Playwright no siempre coinciden con su versión;
  el canal `chrome` sí.
- Si el proyecto no tiene Playwright, apunta a una instalación existente con
  `PLAYWRIGHT_MODULE=/ruta/node_modules/playwright/index.mjs`.
- **Pide el esquema de color explícito** (`colorScheme: 'dark'`): el valor por defecto es
  claro. Con `next-themes`, además `localStorage.setItem('theme', 'light')` en un
  `addInitScript` para forzar el claro.
- **Baja por pasos** (`scrollTo` de 200-300 px con pausas cortas): los saltos grandes no
  disparan los observadores.
- Con `html { scroll-behavior: smooth }`, usa `scrollTo({ behavior: 'instant' })` en las
  pruebas o mide después de que termine la animación: a los 1.5 s puede seguir en camino.

## Qué verificar

| Área | Verificación |
|---|---|
| Carga | La secuencia llega completa (`data-listos`) y ningún medio responde ≥ 400 |
| Puntero | Cursor a la izquierda → fotograma ≤ 3; a la derecha → ≥ total − 4; al centro → reposo ± 3 |
| Inactividad | Unos 3.8 s sin mover el cursor → `data-estado="vigilando"` |
| Reacción | Tras el clic cambia la frase y `data-modo` pasa por la reacción y vuelve |
| Táctil | Tras un scroll de ~260 px cambia el fotograma |
| Movimiento reducido | El fotograma no cambia con el cursor; los videos no arrancan; las listas reemplazan al pin |
| Scroll fijado | A 3 %, 20 %, 42 %, 63 % y 85 % del recorrido: capítulos −1, 0, 1, 2, 3 |
| Interacciones | Copiar al portapapeles (con permisos `clipboard-read`/`clipboard-write`), acordeón, conversación completa |
| Navegación | El menú lleva a la página nueva; desde ella, `/#seccion` llega con la sección a la altura de `scroll-margin-top` (± 12 px) |
| Encabezado | De 320 a 1280 px: el borde derecho ≤ ancho − 4 y el logo nunca se aplasta |
| Desborde | `scrollWidth − innerWidth === 0` y ningún elemento (no fijo) sale de la pantalla |
| Consola | Sin errores ni `pageerror` |
| Fluidez | Un rAF de 1 s con el bucle activo cuenta unos 60 cuadros |

Lee el estado **con el mouse todavía en movimiento** cuando importa la transición, y guarda
capturas en los momentos clave (media reacción, cada capítulo).

## Producción

1. Compila (`npm run build`) y revisa que el precache del service worker no incluya los medios.
2. Levanta el servidor real (por ejemplo `server.mjs`) con sus variables de entorno.
3. Comprueba:
   - `curl` a la ruta nueva → 200 con el HTML de la app.
   - `curl -H "Range: bytes=0-1023"` a un video → `206 Partial Content`, `Accept-Ranges` y
     `Cache-Control`.
   - Los fotogramas → 200 con su caché.
4. Corre el mismo QA contra el build.

## Tipos y lint

- Revisa que el chequeo de tipos **corra de verdad**: en macOS no hay `timeout`, y
  `timeout 300 npx tsc … | grep archivo` termina en "command not found" sin que nada lo note.
  Guarda la salida en un archivo, cuenta los errores totales y filtra por los archivos tocados
  (si el proyecto arrastra errores previos, compara contra ese total).
- Un `tsconfig.json` con `"files": []` y solo referencias no revisa nada: usa el de la app
  (`tsconfig.app.json`).
- `npx eslint` sobre los archivos nuevos.

## Cuando algo "no se ve"

1. ¿El documento está oculto? (`document.visibilityState`)
2. ¿El observador mira un elemento recortado por un ancestro con `overflow: hidden`?
3. ¿La captura está en el tema que crees?
4. ¿El selector mide lo que crees? Un `innerText` con `text-transform: uppercase` devuelve
   mayúsculas.
5. ¿Una regla de mayor especificidad pisa la tuya? En DevTools (CDP):
   `CSS.getMatchedStylesForNode`.
