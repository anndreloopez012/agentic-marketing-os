#!/usr/bin/env node
/**
 * Plantilla de QA para páginas inmersivas, en Chrome real.
 *
 * Copia este archivo al proyecto (p. ej. scripts/<pieza>/qa.mjs), ajusta la
 * sección VERIFICACIONES PROPIAS y córrelo con el front levantado:
 *
 *   PLAYWRIGHT_MODULE=/ruta/a/node_modules/playwright/index.mjs \
 *   BASE=http://localhost:8080 RUTAS=/,/mascota node qa.mjs --capturas /tmp/qa
 *
 * Por qué así:
 * - channel 'chrome': el navegador integrado del editor deja el documento oculto
 *   y ni IntersectionObserver ni requestAnimationFrame corren.
 * - Se baja por pasos: los saltos instantáneos no disparan los observadores.
 * - colorScheme explícito: Playwright usa tema claro por defecto.
 * - El estado de las animaciones se lee de atributos data-* que expone el
 *   componente (fotograma, modo, cargados), no de capturas.
 *
 * Sale con código 1 si falla alguna verificación.
 */
import fs from 'node:fs';
import path from 'node:path';

const BASE = process.env.BASE || 'http://localhost:8080';
const RUTAS = (process.env.RUTAS || '/').split(',').map((ruta) => ruta.trim()).filter(Boolean);
const ANCHOS = (process.env.ANCHOS || '320,360,375,390,414,430,768,1024,1280').split(',').map(Number);
const posicion = process.argv.indexOf('--capturas');
const CAPTURAS = posicion > -1 ? path.resolve(process.argv[posicion + 1]) : null;
if (CAPTURAS) fs.mkdirSync(CAPTURAS, { recursive: true });

let chromium;
try {
  ({ chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright'));
} catch {
  console.error('Falta Playwright: define PLAYWRIGHT_MODULE con la ruta a playwright/index.mjs.');
  process.exit(2);
}

const espera = (ms) => new Promise((resolver) => setTimeout(resolver, ms));
const fallos = [];
function verificar(condicion, mensaje, detalle) {
  console.log(`${condicion ? '  ok ' : ' FALLA'} ${mensaje}${detalle === undefined ? '' : ` → ${JSON.stringify(detalle)}`}`);
  if (!condicion) fallos.push(mensaje);
}

const navegador = await chromium.launch({ channel: process.env.CHANNEL || 'chrome', headless: true });

async function abrir(ruta, viewport, opciones = {}) {
  const contexto = await navegador.newContext({
    viewport,
    deviceScaleFactor: opciones.dpr || 1,
    isMobile: Boolean(opciones.tactil),
    hasTouch: Boolean(opciones.tactil),
    reducedMotion: opciones.reducido ? 'reduce' : 'no-preference',
    colorScheme: opciones.claro ? 'light' : 'dark',
  });
  const pagina = await contexto.newPage();
  const errores = [];
  const recursosFallidos = [];
  pagina.on('console', (mensaje) => mensaje.type() === 'error' && errores.push(mensaje.text().slice(0, 200)));
  pagina.on('pageerror', (error) => errores.push(`pageerror ${error.message.slice(0, 200)}`));
  pagina.on('response', (respuesta) => {
    const url = respuesta.url();
    if (url.startsWith(BASE) && respuesta.status() >= 400) recursosFallidos.push(`${respuesta.status()} ${url}`);
  });
  await pagina.goto(BASE + ruta, { waitUntil: 'domcontentloaded' });
  await espera(1200);
  return { contexto, pagina, errores, recursosFallidos };
}

async function recorrer(pagina, paso = 300) {
  const alto = await pagina.evaluate(() => document.documentElement.scrollHeight);
  const fuera = new Set();
  for (let y = 0; y < alto; y += paso) {
    await pagina.evaluate((valor) => window.scrollTo({ top: valor, behavior: 'instant' }), y);
    await espera(60);
    const nuevos = await pagina.evaluate(() =>
      [...document.querySelectorAll('body *')]
        .filter((elemento) => {
          const caja = elemento.getBoundingClientRect();
          const estilo = getComputedStyle(elemento);
          return caja.width > 0 && (caja.right > window.innerWidth + 1 || caja.left < -1) && estilo.position !== 'fixed';
        })
        .slice(0, 5)
        .map((elemento) => `${elemento.tagName.toLowerCase()}.${String(elemento.className).slice(0, 40)}`)
    );
    nuevos.forEach((nombre) => fuera.add(nombre));
  }
  return [...fuera];
}

for (const ruta of RUTAS) {
  console.log(`\n${ruta} · escritorio oscuro`);
  {
    const { contexto, pagina, errores, recursosFallidos } = await abrir(ruta, { width: 1512, height: 900 }, { dpr: 2 });
    if (CAPTURAS) await pagina.screenshot({ path: path.join(CAPTURAS, `${ruta.replace(/\W+/g, '_') || 'inicio'}-escritorio.png`) });
    await recorrer(pagina);

    // ---------------------------------------------------- VERIFICACIONES PROPIAS
    // Ejemplo para un personaje que sigue al puntero y expone data-fotograma:
    //
    // const escena = await pagina.locator('.mi-escena').boundingBox();
    // await pagina.mouse.move(10, escena.y + escena.height * 0.3, { steps: 8 });
    // await espera(1500);
    // const izquierda = await pagina.evaluate(() => document.querySelector('.mi-escena').dataset.fotograma);
    // verificar(Number(izquierda) <= 3, 'mira a la izquierda', izquierda);
    //
    // Para una sección fijada: bajar a fracciones del recorrido y leer data-capitulo.
    // ------------------------------------------------------------------------------

    verificar(errores.length === 0, 'sin errores de consola', errores);
    verificar(recursosFallidos.length === 0, 'sin recursos fallidos', recursosFallidos);
    await contexto.close();
  }

  console.log(`${ruta} · teléfono táctil`);
  {
    const { contexto, pagina, errores } = await abrir(ruta, { width: 390, height: 844 }, { dpr: 3, tactil: true });
    const fuera = await recorrer(pagina, 400);
    if (CAPTURAS) await pagina.screenshot({ path: path.join(CAPTURAS, `${ruta.replace(/\W+/g, '_') || 'inicio'}-telefono.png`) });
    verificar((await pagina.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)) === 0, 'sin desborde del documento');
    verificar(fuera.length === 0, 'ningún elemento se sale de la pantalla', fuera);
    verificar(errores.length === 0, 'sin errores de consola', errores);
    await contexto.close();
  }

  console.log(`${ruta} · tema claro y movimiento reducido`);
  {
    const { contexto, errores } = await abrir(ruta, { width: 1280, height: 860 }, { claro: true, reducido: true });
    verificar(errores.length === 0, 'sin errores de consola', errores);
    await contexto.close();
  }

  console.log(`${ruta} · encabezado en ${ANCHOS.length} anchos`);
  for (const ancho of ANCHOS) {
    const { contexto, pagina } = await abrir(ruta, { width: ancho, height: 800 }, { tactil: ancho < 768 });
    const derecha = await pagina.evaluate(() => {
      const encabezado = document.querySelector('header');
      if (!encabezado) return 0;
      const visibles = [...encabezado.querySelectorAll('*')].filter(
        (elemento) => getComputedStyle(elemento).display !== 'none' && elemento.getBoundingClientRect().width > 0
      );
      return Math.round(Math.max(0, ...visibles.map((elemento) => elemento.getBoundingClientRect().right)));
    });
    verificar(derecha <= ancho, `el encabezado cabe en ${ancho} px`, derecha);
    await contexto.close();
  }
}

await navegador.close();
console.log(fallos.length ? `\n${fallos.length} verificación(es) fallaron.` : '\nTodas las verificaciones pasaron.');
process.exit(fallos.length ? 1 : 0);
