# Trampas conocidas

Cada una costó tiempo en un proyecto real. Van con su síntoma, para reconocerlas rápido.

## Generación (Higgsfield)

| Síntoma | Causa | Solución |
|---|---|---|
| El lote de video vuelve con "Preset … was recommended" | El servidor sugiere una plantilla | Repetir con `declined_preset_id` |
| 429 `rate_limit_reached` | Plan plus: 6 trabajos simultáneos | Lotes de 6 y esperar con `jobs_wait` |
| `Not authenticated` en el CLI | El CLI no tiene sesión | Usar el conector MCP |
| El recorte de fondo "no tiene transparencia" | El recorte de video entrega H.264 con el sujeto sobre negro | Reconstruir el alfa con `componer_alfa.py` usando el clip original |
| La ampliación a 16:9 se ve recargada | `outpaint_image` inventa el fondo | Generar la imagen de nuevo con referencia |
| El clip "no se mueve" en la primera mitad | Los modelos arrancan lento | Muestreo por cambio visible (`medios.py muestreo`) |
| Salto entre el fotograma 0 y el 1 | El modelo asienta la imagen de inicio | No es un corte; usa el 0 como reposo compartido |
| El conector desaparece a mitad de sesión | Desconexión del servidor MCP | Descargar cada resultado apenas termina |

## Procesamiento

| Síntoma | Causa | Solución |
|---|---|---|
| Todos los fotogramas con alfa salen vacíos | `Image.fromarray()` es de solo lectura y `floodfill` no hace nada sin avisar | `.copy()` antes de rellenar |
| Aparece una mancha de fondo entre brazo y cuerpo | Se rellenaron todos los huecos de la máscara | Rellenar solo huecos pequeños (unos 260 px a 720 px de lado) |
| Motas sueltas alrededor del personaje | Ruido del recorte | Quitar componentes pequeños (unos 350 px a 720 px) |
| Halo oscuro en tema claro | Color del borde contaminado con el fondo | Restar el fondo estimado en la franja del borde |
| ffmpeg no escribe WebP | Homebrew compila ffmpeg sin libwebp | `cwebp` |
| El bucle salta en el último cuadro | Fundido calculado en segundos | Contarlo en fotogramas (`medios.py bucle`) |
| El bucle de la portada "hace zoom hacia atrás" | Fundido sobre un clip con movimiento de cámara | `--ida-y-vuelta` |
| Un `grep` sobre `$(ls …)` no encuentra nada | `ls` tiene alias con iconos | Usar `find` o `command ls` |

## Front

| Síntoma | Causa | Solución |
|---|---|---|
| El personaje se ve translúcido al moverse | Mezcla con ambos fotogramas a media opacidad | Actual opaco + siguiente encima con la fracción |
| El personaje no gira del todo hacia un lado | Escala simétrica y personaje fuera del centro | Escalar cada lado con su espacio |
| Tirones al mover el mouse | Medir el rect en cada evento o cada cuadro | Rect en caché, invalidado por scroll/resize |
| Rectángulo oscuro detrás del título con degradado | `drop-shadow` sobre texto con `background-clip: text` | Sombra en el contenedor |
| El menú no cambia de color con las variables | `button { color: inherit }` hereda el valor ya calculado | Fijar `color` en el encabezado |
| Al llegar con `#ancla` la página "viaja" 1.5 s | `html { scroll-behavior: smooth }` | `behavior: 'instant'` |
| No se puede achicar un botón en móvil | Regla global de 48 px táctiles | Retirar elementos redundantes del encabezado |
| La ruta nueva redirige a `/` en producción | El servidor redirige lo desconocido | Registrar el segmento |
| El borde de la escena fijada se nota a medias | Máscaras que no alcanzan o que borran detalles | Enmarcarla como monitor |
| `whileInView` nunca dispara | El hijo está recortado por `overflow: hidden` | Disparador en el contenedor |
| El video no arranca en iOS | Falta `muted` como propiedad | `video.muted = video.defaultMuted = true` antes de `play()` |
| La pista de texto choca con la plataforma | La elipse sobresale del escenario | Margen superior en la pista |
| El lint marca `setState` en el efecto | React Hooks v7 (reglas del compilador) | Inicializador perezoso, `useSyncExternalStore` o `setState` dentro de callbacks |

## QA y entorno

| Síntoma | Causa | Solución |
|---|---|---|
| Capturas negras y animaciones "rotas" | Panel del navegador integrado oculto | Playwright con `channel: 'chrome'` |
| Captura "oscura" que sale clara | Playwright usa tema claro por defecto | `colorScheme` explícito |
| `tsc` "limpio" que no corrió | macOS sin `timeout` | Revisar código de salida y total de errores |
| `tsc -p tsconfig.json` no encuentra nada | `"files": []` con referencias | Usar `tsconfig.app.json` |
| Ancla medida lejos del destino | Se midió durante el scroll animado | Esperar o usar `instant` |
| El timing de recursos no lista los medios | Buffer de Resource Timing lleno (250) en desarrollo | Escuchar `response` en Playwright |
| Aparece una carpeta nueva sin versionar | Otro proceso escribió en el repo | Revisar autoría y fecha; no subirla sin confirmar |
