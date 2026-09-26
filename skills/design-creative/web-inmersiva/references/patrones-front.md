# Patrones de front

Los ejemplos son React + framer-motion (así se hizo Kivo), pero la lógica es la misma en
vanilla o Astro + GSAP (así se hizo Nimbo+). Código completo de referencia en
`core-strapi/src/components/brand/kivo/KivoInteractivo.tsx` y `src/pages/KivoPage.tsx`.

## Contenido
1. Cargar secuencias
2. Personaje que sigue al puntero
3. Pintar con mezcla
4. Escenario visual
5. Sección fijada por scroll
6. Videos
7. Portada
8. Navegación, rutas y servidor
9. Reglas de lint (React Hooks v7)

## 1. Cargar secuencias

`assets/secuenciaDeFotogramas.ts`:

```ts
const mirada = cargarSecuencia(rutasDeSecuencia('/brand/x/mirada/alta', 49), {
  prioridad: [24],            // el fotograma de reposo primero
  concurrencia: 4,
  alAvanzar: (listos, total) => { /* pintar si no hay bucle; encadenar otra carga */ },
});
mirada.cercano(indice);       // el pedido o el vecino cargado más cercano
mirada.destruir();            // aborta y libera los ImageBitmap
```

- Orden por **bisección**: extremos, centro, cuartos… La secuencia se puede usar desde las
  primeras respuestas y se va afinando.
- **Calidad** según el lienzo: `clientWidth × min(devicePixelRatio, 2) > 560` → `alta`.
- Arranca la carga con un `IntersectionObserver` de margen amplio (unos 900 px), no al montar.
- Si el componente se desmonta, `destruir()`.

## 2. Personaje que sigue al puntero

Un único bucle `requestAnimationFrame` que **solo corre mientras el escenario se ve** (segundo
observador sin margen) y con la pestaña visible (`visibilitychange`).

```ts
// Por cuadro: primero leer, después escribir.
if (estado.rectSucio) { estado.rect = escena.getBoundingClientRect(); estado.rectSucio = false; }
const libre = tactil || ahora - estado.ultimoPuntero > 2800;

if (!libre) {
  const centroX = rect.left + rect.width / 2;
  const distancia = punteroX - centroX;
  // El personaje casi nunca está centrado: cada lado se escala con su espacio,
  // así llegar a cualquier borde es giro completo.
  const alcance = distancia > 0 ? innerWidth - centroX : centroX;
  const escala = Math.max(200, Math.min(alcance * 0.9, innerWidth * 0.36));
  objetivo = limitar(distancia / escala, -1, 1);
} else if (tactil) {
  // En táctil la mirada acompaña al scroll.
  objetivo = limitar(-((rect.top + rect.height / 2) / innerHeight - 0.5) * 1.7, -1, 1);
} else {
  // Vigilancia: barrido lento con pausa en los extremos.
  const s = Math.sin(t * 0.42);
  objetivo = Math.sign(s) * Math.abs(s) ** 0.55 * 0.72;
}

const k = 1 - Math.exp(-dt * 5.5);          // inercia independiente de los fps
giro += (objetivo - giro) * k;
escena.style.setProperty('--giro', giro.toFixed(3));
pintar(mirada, centro + giro * centro);      // índice fraccional
```

- `pointermove` en `window` (pasivo) solo guarda coordenadas; se ignora `pointerType === 'touch'`.
- `scroll` y `resize` solo marcan `rectSucio`. Medir en cada `pointermove` mientras se escriben
  estilos provoca layout forzado; medir en cada cuadro fue el cuello de botella de Nimbo+.
- **Reacción al clic**: modo `volviendo` (la cabeza regresa rápido al centro, k con 14) →
  `reaccion` (reproducir por tiempo, p. ej. 12 fps) → `mirada`. Funciona sin saltos porque
  todos los clips parten y terminan en el fotograma central.
- **Carga por intención**: la reacción se descarga con `pointerenter`, `focus` o el primer
  clic. Si la tocan mientras carga, se guarda la hora del pedido y se reproduce al terminar
  (con un margen de unos 3 s).
- **Estado para QA**: `data-fotograma="mirada:24"`, `data-modo`, `data-estado`
  (`siguiendo` / `vigilando` / `saludando`), `data-listos`, `data-listo`.
- **Textos que cambian muy seguido** (grados, estado): escribe con `textContent` por ref,
  limitado a unas 7 veces por segundo. React solo re-renderiza cuando cambia la frase.
- **Movimiento reducido**: sin bucle; se pinta el reposo cuando llega el fotograma y el clic
  solo cambia la frase.
- La figura es un `<button>` con etiqueta accesible; el globo de frases, `aria-live="polite"`.

## 3. Pintar con mezcla

```ts
const base = Math.floor(posicion), mezcla = posicion - base;
ctx.clearRect(0, 0, w, h);                       // solo si la secuencia tiene alfa
ctx.globalAlpha = 1;
ctx.drawImage(secuencia.cercano(base), 0, 0, w, h);
if (mezcla > 0.02) {
  ctx.globalAlpha = mezcla;                      // el siguiente ENCIMA, parcial
  ctx.drawImage(secuencia.cercano(base + 1), 0, 0, w, h);
  ctx.globalAlpha = 1;
}
```

Pintar los dos a media opacidad deja el interior translúcido (alfa total 0.75 a mitad de
camino). Evita repintar si no cambió nada: compara una clave con la posición redondeada, los
fotogramas cargados y el ancho del lienzo.

Lienzo: `width = height = round(clientWidth × min(dpr, 2))`, ajustado con `ResizeObserver`.
**No pongas `filter: drop-shadow` sobre un lienzo que cambia cada cuadro**: se recalcula el
desenfoque en cada repintado. Las sombras y los brillos van en capas estáticas.

## 4. Escenario visual

Capas, de atrás hacia adelante, movidas por variables CSS que escribe el bucle:

- **Halo**: gradientes radiales con el color del personaje y el de la telemetría, desenfoque
  fijo, desplazado al revés que la mirada (`translate3d(calc(var(--giro) * -28px), …)`).
- **Plataforma**: un cuadrado con `rotateX(76deg)` es una elipse a los pies. Anillos con
  `repeating-conic-gradient` y máscara radial; uno gira despacio y otro "respira".
- **Esquinas de visor**: ocho `linear-gradient` en un solo elemento; el escenario se lee como
  un instrumento.
- **Partículas**: pocas (unas 8), con posiciones y retrasos fijos (nada de `Math.random` al
  renderizar).
- **Figura**: `rotateY(calc(var(--giro) * 7deg))` para dar volumen sobre el giro de la cabeza.
- **Globo**: zona con **altura reservada** (las frases cambian de largo y el escenario no debe
  saltar) y un color por tono: guía (cian), alerta (ámbar), éxito (verde).
- **Póster**: el fotograma central como `<img>` hasta que el lienzo pinta; luego se funde.
- Deja espacio bajo el escenario: la plataforma sobresale y se come la pista de texto.
- Tema claro: el globo y las etiquetas usan superficie blanca y sombra suave.
- En móvil, el escenario va **antes** que el texto: es lo que engancha al llegar.

## 5. Sección fijada por scroll

```tsx
<section ref={seccion} style={{ height: '520vh' }}>
  <div style={{ position: 'sticky', top: 0, height: '100svh' }}>…</div>
</section>
```

```ts
const { scrollYProgress } = useScroll({ target: seccion, offset: ['start start', 'end end'] });
// Tramos iguales por capítulo aunque cada evento ocurra a su ritmo en el video:
const CORTES = [0.02, t.orejas - 0.06, t.visor - 0.02, t.medallon - 0.05, 1];
function mapear(v) {
  if (v < 0.08) return { avance: (v / 0.08) * CORTES[0], capitulo: -1 };
  if (v >= 0.94) return { avance: 1, capitulo: 3 };
  const tramo = ((v - 0.08) / 0.86) * 4, c = Math.min(3, Math.floor(tramo));
  return { avance: CORTES[c] + (CORTES[c + 1] - CORTES[c]) * (tramo - c), capitulo: c };
}
useMotionValueEvent(scrollYProgress, 'change', (v) => {
  const { avance, capitulo } = mapear(v);
  pintar(avance);                                   // directo al lienzo
  setCapitulo((a) => (a === capitulo ? a : capitulo)); // estado solo si cambia
});
```

- Los tiempos (`t.*`) salen de `scripts/medios.py tiempos` y viven en el módulo generado.
- **Enmarca el escenario** (borde redondeado, esquinas, etiqueta "Secuencia de encendido",
  contador `03 / 04`). Fundir los bordes con máscaras borra lo que toca el borde.
- **Puntos** sobre el personaje en % del encuadre: el activo late; los ya vistos quedan
  atenuados.
- Ficha del capítulo con `AnimatePresence mode="wait"`: número, nombre con icono, qué es,
  **por qué**, color de marca y un video corto de detalle.
- Progreso con chips numerados (`aria-current="step"`).
- **Sin pin** en teléfono (≤900 px o `pointer: coarse`) y con movimiento reducido: imagen
  estática con los puntos numerados y las fichas en lista.
- Escenas oscuras en ambos temas: fuerza los tokens oscuros dentro de la sección.

## 6. Videos

```tsx
function VideoEnBucle({ nombre, reducido }) {
  const ref = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const video = ref.current; if (!video) return;
    video.muted = true; video.defaultMuted = true;   // Safari lo exige para reproducir solo
    if (reducido) return;
    const io = new IntersectionObserver(([e]) => (e.isIntersecting ? video.play().catch(() => {}) : video.pause()), { threshold: 0.15 });
    io.observe(video);
    return () => { io.disconnect(); video.pause(); };
  }, [reducido, nombre]);
  return <video ref={ref} src={`${BASE}/${nombre}.mp4`} poster={`${BASE}/${nombre}.webp`} muted loop playsInline preload="metadata" aria-hidden="true" tabIndex={-1} />;
}
```

- Con movimiento reducido no hay reproducción automática; queda el póster.
- **Galería de roles en acordeón**: `flex: 1` y `flex-grow: 2.3` al señalado (solo con puntero
  que no sea táctil). En teléfono, tarjetas apiladas con altura mínima.
- **Conversación que se escribe sola**: `useInView(..., { once: true })` y los `setState`
  dentro de `setTimeout` (nunca síncronos en el efecto). Con movimiento reducido se muestra
  completa desde el inicio.

## 7. Portada

- **Video corrido a un lado**: el contenedor del video va con `left: 20%; width: 100%` y un
  velo con gradiente desde la izquierda. El personaje queda a dos tercios y el título respira.
  En teléfono, video centrado y velo desde abajo más denso.
- Clip con acercamiento de cámara → bucle **de ida y vuelta** (un fundido mostraría el salto
  del zoom).
- **Título con degradado**: `background-clip: text` en cada letra y la **sombra en el
  contenedor** (`filter: drop-shadow` sobre el texto recortado pinta un rectángulo oscuro).
- Letras que suben con máscara `overflow: hidden`: el disparador (`whileInView`) va en el
  contenedor, no en cada letra, porque un hijo desplazado fuera de su máscara nunca interseca.
- Parallax suave con `useScroll` + `useTransform` (escala del fondo, subida y desvanecido del
  texto), desactivado con movimiento reducido.
- Manifiesto que se revela palabra por palabra: un componente por palabra con
  `useTransform(progreso, [i/n, (i+1)/n], [0.14, 1])`.

## 8. Navegación, rutas y servidor

- **Encabezado compartido** entre la portada y la página nueva: mismo menú; la opción de la
  página nueva lleva avatar y queda activa (`aria-current="page"`).
- Desde la página nueva, las secciones de la portada van como `/#seccion`. En la portada:
  ```ts
  document.getElementById(destino)?.scrollIntoView({ behavior: 'instant', block: 'start' });
  ```
  `'auto'` respeta el `scroll-behavior: smooth` del `html` y recorre toda la portada
  animando. Agrega una corrección a los ~800 ms (fuentes y secciones fijadas terminan de medir
  después), solo si la persona no se movió.
- **Color del menú sobre una portada oscura en tema claro**: si los botones heredan
  (`button { color: inherit }`), el valor llega ya calculado desde el contenedor raíz; fija
  `color` en el propio encabezado mientras no esté condensado.
- **Encabezado en teléfono**: si hay tamaños mínimos táctiles globales (48 px), no achiques
  botones; retira lo que ya existe como botón grande en la página y agrega `flex-shrink: 0`
  al logo. Pruébalo de 320 a 1280 px.
- **Ruta**: carga diferida; guardia que solo exige "landing activa" (la página es de la
  marca, no de un módulo); agrégala a las rutas que pintan sin esperar la configuración
  global si la portada lo hace.
- **Servidor de producción**: registra el segmento si el servidor redirige lo desconocido
  (los tenants con CMS público lo mandaban a `/`). Caché de un día para los videos de marca.
  `express.static` ya responde rangos (`206`), que Safari necesita para el video.
- **PWA**: revisa que el precache (`injectManifest`) no incluya los medios; si su patrón
  admite `webp` o `mp4`, exclúyelos.

## 9. Reglas de lint (React Hooks v7)

- Nada de `setState` síncrono dentro de un efecto: inicializador perezoso
  (`useState(esTactil)`) o `useSyncExternalStore` para `matchMedia`.
- No leer `ref.current` al renderizar; las funciones que el efecto crea se exponen con refs
  (`activarRef.current = () => …`) y se llaman desde manejadores.
- `react-refresh/only-export-components`: los datos compartidos van en su propio archivo
  (frases, conteos), no exportados junto al componente.
