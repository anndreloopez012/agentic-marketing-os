#!/usr/bin/env python3
"""
Herramientas para convertir clips generados en medios de una web inmersiva.

Requiere: python3 con numpy y Pillow, ffmpeg/ffprobe y cwebp (ffmpeg de Homebrew
no trae libwebp, por eso los WebP se escriben con cwebp).

Subcomandos:
  hoja            hoja de contacto con marcas de tiempo (revisar antes de procesar)
  curva           movimiento por fotograma y acumulado (cortes, arranques lentos)
  muestreo        índices repartidos por cambio visible, no por tiempo
  secuencia       fotogramas opacos a WebP en varias calidades
  secuencia-alfa  fotogramas con alfa reconstruido (original + recortado sobre negro)
  tiempos         momento en que cada región del encuadre se enciende
  bucle           video en bucle: fundido contado en fotogramas o ida y vuelta
  poster          primer fotograma como WebP

Ejemplos:
  medios.py hoja clip.mp4 --salida hoja.jpg
  medios.py muestreo mirada-der-sin-fondo.mp4 --cantidad 24
  medios.py secuencia-alfa mirada.mp4 mirada-sin-fondo.mp4 public/mascota/mirada \
      --indices 0,5,9,14 --calidades alta:900:80,ligera:460:78
  medios.py secuencia encendido.mp4 public/mascota/encendido --paso 3 \
      --calidades alta:960:72,ligera:560:70
  medios.py tiempos encendido.mp4 --regiones regiones.json
  medios.py bucle detalle.mp4 detalle-web.mp4 --ancho 640 --alto 640
  medios.py bucle portada.mp4 portada-web.mp4 --ancho 1920 --alto 1080 --ida-y-vuelta
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))


def correr(cmd):
    subprocess.run(cmd, check=True)


def info(ruta):
    salida = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
         '-show_entries', 'stream=width,height,nb_read_frames,r_frame_rate:format=duration',
         '-of', 'json', ruta],
        check=True, stdout=subprocess.PIPE, text=True,
    ).stdout
    datos = json.loads(salida)
    flujo = datos['streams'][0]
    numerador, denominador = flujo['r_frame_rate'].split('/')
    return {
        'ancho': int(flujo['width']),
        'alto': int(flujo['height']),
        'cuadros': int(flujo['nb_read_frames']),
        'fps': float(numerador) / float(denominador),
        'duracion': float(datos['format']['duration']),
    }


def leer_gris(ruta, lado=160):
    crudo = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', ruta, '-vf', f'scale={lado}:{lado}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
        check=True, stdout=subprocess.PIPE,
    ).stdout
    return np.frombuffer(crudo, dtype=np.uint8).reshape(-1, lado, lado).astype(np.float32)


def pasos_de_movimiento(ruta):
    cuadros = leer_gris(ruta)
    pasos = [0.0] + [float(np.abs(cuadros[i] - cuadros[i - 1]).mean()) for i in range(1, len(cuadros))]
    return np.array(pasos)


def calidades(texto):
    """'alta:900:80,ligera:460:78' → [('alta', 900, 80), ...]"""
    resultado = []
    for parte in texto.split(','):
        nombre, lado, calidad = parte.split(':')
        resultado.append((nombre, int(lado), int(calidad)))
    return resultado


def a_webp(tareas):
    def una(tarea):
        origen, destino, lado, calidad = tarea
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        correr(['cwebp', '-quiet', '-mt', '-m', '6', '-q', str(calidad), '-alpha_q', '90',
                '-resize', str(lado), '0', origen, '-o', destino])
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        list(pool.map(una, tareas))


def escribir_calidades(pngs, salida, lista_calidades):
    total = len(pngs)
    digitos = max(2, len(str(total - 1)))
    tareas = []
    for nombre, lado, calidad in lista_calidades:
        destino = os.path.join(salida, nombre)
        if os.path.isdir(destino):
            shutil.rmtree(destino)
        os.makedirs(destino, exist_ok=True)
        for indice, png in enumerate(pngs):
            tareas.append((png, os.path.join(destino, f'{indice:0{digitos}d}.webp'), lado, calidad))
    a_webp(tareas)
    return total


# ------------------------------------------------------------------ comandos

def cmd_hoja(args):
    datos = info(args.video)
    with tempfile.TemporaryDirectory() as tmp:
        correr(['ffmpeg', '-v', 'error', '-y', '-i', args.video,
                '-vf', f'fps={args.fps},scale={args.ancho}:-2', os.path.join(tmp, '%03d.jpg')])
        archivos = sorted(os.listdir(tmp))
        imagenes = [Image.open(os.path.join(tmp, nombre)).convert('RGB') for nombre in archivos]
    if not imagenes:
        sys.exit('El video no tiene fotogramas')
    ancho, alto = imagenes[0].size
    columnas = min(args.columnas, len(imagenes))
    filas = (len(imagenes) + columnas - 1) // columnas
    hoja = Image.new('RGB', (ancho * columnas, alto * filas), (0, 0, 0))
    dibujo = ImageDraw.Draw(hoja)
    for indice, imagen in enumerate(imagenes):
        x, y = (indice % columnas) * ancho, (indice // columnas) * alto
        hoja.paste(imagen, (x, y))
        dibujo.text((x + 4, y + 4), f'{indice / args.fps:.1f}s', fill=(255, 255, 0))
    hoja.save(args.salida, quality=85)
    print(json.dumps({'hoja': args.salida, 'muestras': len(imagenes), **datos}))


def cmd_curva(args):
    pasos = pasos_de_movimiento(args.video)
    acumulado = np.cumsum(pasos)
    tipico = float(np.median(pasos[1:])) if len(pasos) > 1 else 0.0
    for indice, paso in enumerate(pasos):
        marca = '  <- posible corte' if tipico and paso > tipico * 4 and paso > 2 else ''
        print(f'{indice:4d}  paso={paso:6.2f}  acumulado={acumulado[indice]:8.1f}  {"#" * int(paso * 10)}{marca}')
    print(json.dumps({'cuadros': len(pasos), 'paso_mediano': round(tipico, 3), 'total': round(float(acumulado[-1]), 2)}))


def cmd_muestreo(args):
    acumulado = np.cumsum(pasos_de_movimiento(args.video))
    objetivos = np.linspace(0, acumulado[-1], args.cantidad + 1)[1:]
    indices, anterior = [], args.desde
    for objetivo in objetivos:
        indice = int(np.searchsorted(acumulado, objetivo))
        indice = min(max(indice, anterior + 1), len(acumulado) - 1)
        indices.append(indice)
        anterior = indice
    print(json.dumps({'indices': indices}))


def cmd_secuencia(args):
    lista = calidades(args.calidades)
    lado_max = max(lado for _, lado, _ in lista)
    with tempfile.TemporaryDirectory() as tmp:
        correr(['ffmpeg', '-v', 'error', '-y', '-i', args.video,
                '-vf', f"select='not(mod(n\\,{args.paso}))',scale={lado_max}:-2:flags=lanczos",
                '-vsync', '0', os.path.join(tmp, '%04d.png')])
        pngs = sorted(os.path.join(tmp, nombre) for nombre in os.listdir(tmp))
        total = escribir_calidades(pngs, args.salida, lista)
    print(json.dumps({'salida': args.salida, 'total': total, 'paso': args.paso}))


def cmd_secuencia_alfa(args):
    lista = calidades(args.calidades)
    lado_max = max(lado for _, lado, _ in lista)
    with tempfile.TemporaryDirectory() as tmp:
        correr([sys.executable, os.path.join(AQUI, 'componer_alfa.py'), args.original, args.recortado,
                tmp, '--lado', str(lado_max), '--fotogramas', args.indices])
        pngs = sorted(os.path.join(tmp, nombre) for nombre in os.listdir(tmp) if nombre.endswith('.png'))
        total = escribir_calidades(pngs, args.salida, lista)
    print(json.dumps({'salida': args.salida, 'total': total}))


def cmd_tiempos(args):
    """regiones.json: {"nombre": {"caja": [x0, y0, x1, y1], "metrica": "calidez|cian|brillo"}}
    con la caja en 0..1 sobre el encuadre."""
    regiones = json.load(open(args.regiones, encoding='utf-8'))
    lado = 200
    crudo = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', args.video, '-vf', f'scale={lado}:{lado}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
        check=True, stdout=subprocess.PIPE,
    ).stdout
    cuadros = np.frombuffer(crudo, dtype=np.uint8).reshape(-1, lado, lado, 3).astype(np.float32)
    resultado = {}
    for nombre, region in regiones.items():
        x0, y0, x1, y1 = [int(round(valor * lado)) for valor in region['caja']]
        zona = cuadros[:, y0:y1, x0:x1]
        metrica = region.get('metrica', 'brillo')
        if metrica == 'calidez':
            curva = (zona[..., 0] - zona[..., 2]).mean(axis=(1, 2))
        elif metrica == 'cian':
            curva = (zona[..., 1] + zona[..., 2] - zona[..., 0]).mean(axis=(1, 2))
        else:
            curva = zona.mean(axis=(1, 2, 3))
        curva = curva - curva[: max(1, len(curva) // 20)].mean()
        tope = float(curva.max())
        inicio = int(np.argmax(curva >= tope * 0.5)) if tope > 0 else 0
        resultado[nombre] = {
            'inicio': round(inicio / len(curva), 3),
            'pico': round(int(np.argmax(curva)) / len(curva), 3),
        }
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


def codificar(entrada, salida, filtro, crf):
    correr(['ffmpeg', '-v', 'error', '-y', '-i', entrada, '-filter_complex', filtro, '-map', '[v]',
            '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-pix_fmt', 'yuv420p',
            '-profile:v', 'high', '-movflags', '+faststart', salida])


def cmd_bucle(args):
    total = int(round(info(args.entrada)['duracion'] * args.fps))
    escala = f'fps={args.fps},scale={args.ancho}:{args.alto}:flags=lanczos'
    if args.ida_y_vuelta:
        # Adelante y atrás sin repetir los extremos: para clips con movimiento de cámara.
        filtro = (
            f'[0:v]{escala},split[f][r];'
            f'[r]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[rv];'
            f'[f][rv]concat=n=2:v=1:a=0,trim=end_frame={2 * total - 2},format=yuv420p[v]'
        )
    else:
        # Los primeros N fotogramas se funden sobre la cola. Contado en fotogramas:
        # en segundos el fundido acababa uno antes y el bucle saltaba.
        n = args.fundido
        filtro = (
            f'[0:v]{escala},split[a][b];'
            f'[a]trim=start_frame={n}:end_frame={total},setpts=PTS-STARTPTS[cuerpo];'
            f'[b]trim=end_frame={n},setpts=PTS-STARTPTS,format=yuva420p,'
            f'fade=t=in:s=0:n={n}:alpha=1,setpts=PTS+{total - 2 * n}/({args.fps}*TB)[cabeza];'
            f'[cuerpo][cabeza]overlay=eof_action=pass:repeatlast=0,trim=end_frame={total - n},format=yuv420p[v]'
        )
    codificar(args.entrada, args.salida, filtro, args.crf)
    cuadros = leer_gris(args.salida, 96)
    costura = float(np.abs(cuadros[-1] - cuadros[0]).mean())
    pasos = [float(np.abs(cuadros[i] - cuadros[i - 1]).mean()) for i in range(1, len(cuadros))]
    print(json.dumps({
        'salida': args.salida,
        'cuadros': len(cuadros),
        'costura': round(costura, 2),
        'paso_tipico': round(float(np.mean(pasos)), 2),
        'paso_maximo': round(float(np.max(pasos)), 2),
    }))


def cmd_poster(args):
    with tempfile.TemporaryDirectory() as tmp:
        png = os.path.join(tmp, 'p.png')
        correr(['ffmpeg', '-v', 'error', '-y', '-i', args.video, '-frames:v', '1', png])
        correr(['cwebp', '-quiet', '-m', '6', '-q', str(args.calidad), '-resize', str(args.ancho), '0', png, '-o', args.salida])
    print(json.dumps({'poster': args.salida}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('hoja')
    p.add_argument('video')
    p.add_argument('--salida', default='hoja.jpg')
    p.add_argument('--fps', type=float, default=2)
    p.add_argument('--ancho', type=int, default=240)
    p.add_argument('--columnas', type=int, default=6)
    p.set_defaults(func=cmd_hoja)

    p = sub.add_parser('curva')
    p.add_argument('video')
    p.set_defaults(func=cmd_curva)

    p = sub.add_parser('muestreo')
    p.add_argument('video', help='mejor el clip sin fondo: el fondo solo aporta ruido')
    p.add_argument('--cantidad', type=int, required=True)
    p.add_argument('--desde', type=int, default=0, help='índice que ya se usó como inicio')
    p.set_defaults(func=cmd_muestreo)

    p = sub.add_parser('secuencia')
    p.add_argument('video')
    p.add_argument('salida')
    p.add_argument('--paso', type=int, default=2)
    p.add_argument('--calidades', default='alta:960:72,ligera:560:70')
    p.set_defaults(func=cmd_secuencia)

    p = sub.add_parser('secuencia-alfa')
    p.add_argument('original')
    p.add_argument('recortado')
    p.add_argument('salida')
    p.add_argument('--indices', required=True, help='índices separados por coma, en orden de salida')
    p.add_argument('--calidades', default='alta:900:80,ligera:460:78')
    p.set_defaults(func=cmd_secuencia_alfa)

    p = sub.add_parser('tiempos')
    p.add_argument('video')
    p.add_argument('--regiones', required=True)
    p.set_defaults(func=cmd_tiempos)

    p = sub.add_parser('bucle')
    p.add_argument('entrada')
    p.add_argument('salida')
    p.add_argument('--ancho', type=int, required=True)
    p.add_argument('--alto', type=int, required=True)
    p.add_argument('--fps', type=int, default=24)
    p.add_argument('--fundido', type=int, default=20, help='fotogramas de fundido')
    p.add_argument('--ida-y-vuelta', action='store_true')
    p.add_argument('--crf', type=int, default=26)
    p.set_defaults(func=cmd_bucle)

    p = sub.add_parser('poster')
    p.add_argument('video')
    p.add_argument('salida')
    p.add_argument('--ancho', type=int, default=1600)
    p.add_argument('--calidad', type=int, default=78)
    p.set_defaults(func=cmd_poster)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
