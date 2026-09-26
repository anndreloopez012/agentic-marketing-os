# Guion de medios: qué generar y cuánto cuesta

Antes de generar, escribe una tabla con cada momento de la página: qué ve la persona, qué
controla y qué medio lo resuelve. Un medio mal elegido cuesta créditos y, peor, una
interacción que no se siente viva.

## Técnica según quién manda

| Quién manda | Ejemplo | Técnica | Medio |
|---|---|---|---|
| El **puntero** | Personaje que mira al cursor | Secuencia con alfa en canvas, índice = posición del puntero | 2 clips que parten del mismo fotograma (uno hacia cada lado) + recortes de fondo |
| Un **clic** | Saludo, celebración, alerta | Secuencia con alfa reproducida por tiempo y vuelta al estado base | Clip con `start_image` = `end_image` + recorte |
| El **scroll** | Personaje o producto que se enciende pieza por pieza, hyperlapse | Sección fijada + secuencia opaca en canvas, índice = avance del scroll | Clip con eventos en orden (con `start_image` y `end_image`), o varios clips encadenados |
| **Nadie** (ambiente) | Portada de cine, detalles, roles | `<video>` en bucle silenciado, solo en vista | Clip con cámara fija (bucle con fundido) o con movimiento (ida y vuelta) |
| Nada se mueve | Póster, fallback, avatar | Imagen WebP | Fotograma extraído o imagen base |

Reglas que salieron de la práctica:

- **Todo lo interactivo parte del mismo fotograma**, normalmente el render oficial: así las
  secuencias empalman entre sí (la mirada vuelve al centro y ahí empieza el saludo).
- **Un solo movimiento por clip interactivo.** Si el clip hace dos cosas, el puntero no puede
  controlarlas por separado.
- **Fondo recortado para lo que flota sobre la página** (funciona en tema claro y oscuro).
  **Fondo propio para escenas** (portada, anatomía): se tratan como escenas oscuras en ambos
  temas y se enmarcan.
- Si el encuadre queda muy justo (orejas o pies tocando el borde), no se pueden fundir los
  bordes con máscaras: enmarca la escena como un monitor.

## Presupuesto (Higgsfield, plan plus, septiembre de 2026)

| Pieza | Costo |
|---|---|
| Seedance 2.5 · 1080p · 5 s | 45 |
| Seedance 2.5 · 1080p · 8 s | 72 |
| Seedance 2.5 · 720p · 5 s | 32.5 |
| Nano Banana Pro (imagen) | 2 |
| Ampliación (outpaint) | 2 |
| Recorte de fondo de video | ≈ 1 |

Referencia: la mascota interactiva más una página completa (13 clips, 10 imágenes y 3 recortes)
costó 529.5 créditos. Usa 1080p para lo que se ve grande y controla el usuario, y 720p para
los detalles y roles, que se ven en tarjetas.

## Pesos que funcionaron

| Secuencia | Fotogramas | Alta | Ligera |
|---|---|---|---|
| Mirada (con alfa, 900/460 px) | 49 | 2.3 MB | 980 KB |
| Reacción (con alfa, 12 fps) | 61 | 3.1 MB | 1.2 MB |
| Scroll (opaca, 960/560 px) | 65 | 1.7 MB | 924 KB |

- La secuencia principal se carga al acercarse a la sección; la reacción, solo con intención
  (hover, foco o clic).
- La mezcla entre fotogramas vecinos permite usar menos fotogramas sin que se note el paso.
- Los píxeles transparentes casi no pesan en WebP con alfa: no hace falta recortar el lienzo.

## Estructura de archivos sugerida

```
public/brand/<personaje>/
  mirada/{alta,ligera}/NN.webp
  saludo/{alta,ligera}/NN.webp
  encendido/{alta,ligera}/NN.webp
  video/<nombre>.mp4 + <nombre>.webp (póster)
scripts/<personaje>/preparar_medios.py   ← regenera todo y escribe medios.ts
src/components/brand/<personaje>/medios.ts  ← generado: conteos y tiempos
```

Los crudos no van al repo: guárdalos junto al material de marca, con un `LEEME.md` y los ids
de los trabajos.
