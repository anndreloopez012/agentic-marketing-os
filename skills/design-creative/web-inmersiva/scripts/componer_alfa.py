#!/usr/bin/env python3
"""
Recupera el canal alfa de Kivo a partir de dos videos alineados:

  original   el clip tal como salio del generador (Kivo sobre su fondo)
  recortado  el mismo clip con el fondo quitado, pero entregado SIN alfa:
             el recortador compone a Kivo sobre negro puro (= alfa * color)

Con los dos se reconstruye un RGBA limpio:
  1. mascara  = pixeles del recortado con brillo; se rellenan los huecos
     (nariz, pupilas, suelas) para que el interior quede opaco.
  2. borde    = cociente de brillo recortado / original en una franja de pocos
     pixeles alrededor de la mascara: da la transicion suave del pelaje.
  3. color    = el del original (10 bits, mejor que el recortado de 8), con el
     fondo restado en el borde para que no quede un halo oscuro en tema claro.

Uso:
  componer_alfa.py ORIGINAL RECORTADO SALIDA --lado 720 --fotogramas 0,3,5,...

Escribe SALIDA/NN.png (RGBA). La conversion a WebP la hace preparar_medios.sh.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def leer_video(ruta, lado):
    cmd = [
        'ffmpeg', '-v', 'error', '-i', ruta,
        '-vf', f'scale={lado}:{lado}:flags=lanczos',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-',
    ]
    crudo = subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout
    return np.frombuffer(crudo, dtype=np.uint8).reshape(-1, lado, lado, 3)


def filtro(mascara, filtro_pil):
    imagen = Image.fromarray((mascara * 255).astype(np.uint8), 'L')
    return np.asarray(imagen.filter(filtro_pil)) > 127


def dilatar(mascara, radio):
    return filtro(mascara, ImageFilter.MaxFilter(2 * radio + 1)) if radio > 0 else mascara


def erosionar(mascara, radio):
    return filtro(mascara, ImageFilter.MinFilter(2 * radio + 1)) if radio > 0 else mascara


def componentes(mascara, limite=600):
    """Componentes conexas (4-vecinos) con el relleno de PIL: [(area, mascara)]."""
    # .copy(): una imagen creada desde numpy es de solo lectura y floodfill
    # la ignoraria sin avisar.
    trabajo = Image.fromarray(np.where(mascara, 255, 0).astype(np.uint8), 'L').copy()
    ancho = mascara.shape[1]
    resultado = []
    for _ in range(limite):
        plano = np.asarray(trabajo)
        pendientes = np.flatnonzero(plano == 255)
        if pendientes.size == 0:
            break
        fila, columna = divmod(int(pendientes[0]), ancho)
        ImageDraw.floodfill(trabajo, (columna, fila), 100, thresh=0)
        plano = np.asarray(trabajo)
        componente = plano == 100
        resultado.append((int(componente.sum()), componente))
        trabajo = Image.fromarray(np.where(componente, 50, plano).astype(np.uint8), 'L').copy()
    return resultado


def quitar_motas(mascara, area_minima):
    """Deja solo las piezas grandes: el recortador suelta motas sueltas en el fondo."""
    limpia = np.zeros_like(mascara)
    for area, componente in componentes(mascara):
        if area >= area_minima:
            limpia |= componente
    return limpia


def rellenar_huecos_pequenos(mascara, area_maxima):
    """Rellena solo huecos chicos (pupilas, nariz). Un hueco grande es fondo
    real encerrado entre brazo, cuerpo y cola, y tiene que quedar transparente."""
    alto, ancho = mascara.shape
    lienzo = Image.new('L', (ancho + 2, alto + 2), 0)
    lienzo.paste(Image.fromarray((mascara * 255).astype(np.uint8), 'L'), (1, 1))
    ImageDraw.floodfill(lienzo, (0, 0), 128, thresh=0)
    exterior = np.asarray(lienzo)[1:-1, 1:-1] == 128
    huecos = ~exterior & ~mascara
    rellena = mascara.copy()
    for area, componente in componentes(huecos):
        if area <= area_maxima:
            rellena |= componente
    return rellena


def desenfoque_caja(arreglo, radio):
    """Desenfoque de caja separable con sumas acumuladas (sin scipy)."""
    salida = arreglo.astype(np.float64)
    for eje in (0, 1):
        relleno = [(0, 0)] * salida.ndim
        relleno[eje] = (radio + 1, radio)
        acumulado = np.cumsum(np.pad(salida, relleno, mode='edge'), axis=eje)
        n = salida.shape[eje]
        alto = np.take(acumulado, np.arange(2 * radio + 1, 2 * radio + 1 + n), axis=eje)
        bajo = np.take(acumulado, np.arange(0, n), axis=eje)
        salida = (alto - bajo) / (2 * radio + 1)
    return salida


def componer(original, recortado):
    o = original.astype(np.float64) / 255.0
    r = recortado.astype(np.float64) / 255.0
    brillo_r = r.max(axis=2)
    brillo_o = o.max(axis=2)

    lado = brillo_r.shape[0]
    escala = (lado / 720.0) ** 2
    mascara = quitar_motas(brillo_r > 0.07, area_minima=int(350 * escala))
    mascara = rellenar_huecos_pequenos(mascara, area_maxima=int(260 * escala))
    nucleo = erosionar(mascara, 1)
    franja = dilatar(mascara, 2) & ~nucleo

    cociente = np.clip(brillo_r / np.maximum(brillo_o, 0.03), 0.0, 1.0)
    cociente[cociente < 0.08] = 0.0

    alfa = np.where(nucleo, 1.0, np.where(franja, cociente, 0.0))
    # Suaviza un pixel el escalon entre nucleo y franja.
    alfa = np.clip(desenfoque_caja(alfa, 1) * 0.5 + alfa * 0.5, 0.0, 1.0)
    alfa[alfa < 0.04] = 0.0

    # Fondo estimado bajo Kivo: promedio del fondo visible alrededor.
    peso = (~dilatar(mascara, 4)).astype(np.float64)
    suma = desenfoque_caja(o * peso[..., None], 36)
    norma = desenfoque_caja(peso, 36)[..., None]
    fondo = suma / np.maximum(norma, 1e-4)

    a = alfa[..., None]
    color = np.where(
        a >= 0.999,
        o,
        np.clip((o - (1.0 - a) * fondo) / np.maximum(a, 0.05), 0.0, 1.0),
    )
    rgba = np.dstack([color, alfa])
    return (rgba * 255.0 + 0.5).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('original')
    parser.add_argument('recortado')
    parser.add_argument('salida')
    parser.add_argument('--lado', type=int, default=720)
    parser.add_argument('--fotogramas', required=True, help='indices separados por coma')
    args = parser.parse_args()

    indices = [int(valor) for valor in args.fotogramas.split(',') if valor.strip()]
    os.makedirs(args.salida, exist_ok=True)

    originales = leer_video(args.original, args.lado)
    recortados = leer_video(args.recortado, args.lado)
    total = min(len(originales), len(recortados))

    digitos = max(2, len(str(len(indices) - 1)))
    for posicion, indice in enumerate(indices):
        if indice >= total:
            sys.exit(f'fotograma {indice} fuera de rango ({total})')
        rgba = componer(originales[indice], recortados[indice])
        destino = os.path.join(args.salida, f'{posicion:0{digitos}d}.png')
        Image.fromarray(rgba, 'RGBA').save(destino, compress_level=1)

    print(json.dumps({'salida': args.salida, 'fotogramas': len(indices), 'lado': args.lado}))


if __name__ == '__main__':
    main()
