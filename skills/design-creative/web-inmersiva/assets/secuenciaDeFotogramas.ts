/**
 * Carga progresiva de una secuencia de fotogramas para pintarla en <canvas>.
 *
 * Se usa en lugar de adelantar un <video> porque Safari/iOS no adelanta video
 * de forma fiable fotograma a fotograma, y porque los fotogramas WebP conservan
 * el canal alfa (Kivo va recortado sobre el fondo de la página).
 *
 * El orden de carga es por bisección: extremos, centro, cuartos... Así la
 * secuencia es usable desde las primeras peticiones (con saltos) y se va
 * afinando mientras llegan las demás.
 */

export type Fotograma = ImageBitmap | HTMLImageElement;

export interface SecuenciaDeFotogramas {
  readonly total: number;
  /** Cuántos fotogramas ya están decodificados. */
  listos: () => number;
  /** El fotograma pedido o, si todavía no llegó, el cargado más cercano. */
  cercano: (indice: number) => Fotograma | null;
  destruir: () => void;
}

interface OpcionesDeCarga {
  concurrencia?: number;
  /** Índices que deben llegar antes que el resto (p. ej. el fotograma central). */
  prioridad?: number[];
  alAvanzar?: (listos: number, total: number) => void;
}

export function ordenPorBiseccion(total: number, prioridad: number[] = []): number[] {
  const orden: number[] = [];
  const visto = new Set<number>();
  const agregar = (indice: number) => {
    if (indice < 0 || indice >= total || visto.has(indice)) return;
    visto.add(indice);
    orden.push(indice);
  };

  prioridad.forEach(agregar);
  agregar(0);
  agregar(total - 1);

  let paso = total - 1;
  while (paso > 1) {
    paso = Math.ceil(paso / 2);
    for (let indice = 0; indice < total; indice += paso) agregar(indice);
  }
  for (let indice = 0; indice < total; indice += 1) agregar(indice);

  return orden;
}

async function decodificar(ruta: string, senal: AbortSignal): Promise<Fotograma> {
  if (typeof createImageBitmap === 'function') {
    const respuesta = await fetch(ruta, { signal: senal });
    if (!respuesta.ok) throw new Error(`${respuesta.status} ${ruta}`);
    return createImageBitmap(await respuesta.blob());
  }

  const imagen = new Image();
  imagen.decoding = 'async';
  imagen.src = ruta;
  await imagen.decode();
  return imagen;
}

export function cargarSecuencia(rutas: string[], opciones: OpcionesDeCarga = {}): SecuenciaDeFotogramas {
  const total = rutas.length;
  const fotogramas: (Fotograma | null)[] = new Array(total).fill(null);
  const controlador = new AbortController();
  const pendientes = ordenPorBiseccion(total, opciones.prioridad);
  let listos = 0;
  let destruida = false;

  const trabajador = async () => {
    while (!destruida && pendientes.length > 0) {
      const indice = pendientes.shift() as number;
      try {
        const fotograma = await decodificar(rutas[indice], controlador.signal);
        if (destruida) {
          if ('close' in fotograma) fotograma.close();
          return;
        }
        fotogramas[indice] = fotograma;
        listos += 1;
        opciones.alAvanzar?.(listos, total);
      } catch {
        // Un fotograma perdido no rompe la secuencia: `cercano` lo cubre con el vecino.
        if (destruida) return;
      }
    }
  };

  const hilos = Math.max(1, Math.min(opciones.concurrencia ?? 4, total));
  for (let hilo = 0; hilo < hilos; hilo += 1) void trabajador();

  return {
    total,
    listos: () => listos,
    cercano: (indice) => {
      const base = Math.max(0, Math.min(total - 1, Math.round(indice)));
      if (fotogramas[base]) return fotogramas[base];
      for (let distancia = 1; distancia < total; distancia += 1) {
        const antes = fotogramas[base - distancia];
        if (antes) return antes;
        const despues = fotogramas[base + distancia];
        if (despues) return despues;
      }
      return null;
    },
    destruir: () => {
      destruida = true;
      controlador.abort();
      fotogramas.forEach((fotograma) => {
        if (fotograma && 'close' in fotograma) fotograma.close();
      });
      fotogramas.fill(null);
    },
  };
}

/** Rutas `carpeta/00.webp … carpeta/NN.webp`. */
export function rutasDeSecuencia(carpeta: string, total: number): string[] {
  const digitos = String(total - 1).length < 2 ? 2 : String(total - 1).length;
  return Array.from({ length: total }, (_, indice) => `${carpeta}/${String(indice).padStart(digitos, '0')}.webp`);
}
