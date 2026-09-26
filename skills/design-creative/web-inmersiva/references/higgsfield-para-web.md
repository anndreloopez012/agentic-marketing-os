# Higgsfield para medios de una web

Cómo usar Higgsfield cuando el destino es una página interactiva. Para el catálogo general de
modelos, ver la skill `higgsfield-generate`; para la biblia de estilo y la memoria de campañas,
`higgsfield`.

## Acceso

- El **CLI `higgsfield`** puede estar sin sesión (`Not authenticated`). El **conector MCP de
  Higgsfield** funciona igual: `balance`, `models_explore`, `media_upload` + `media_confirm`,
  `generate_image(_batch)`, `generate_video(_batch)`, `jobs_wait`, `remove_background`,
  `outpaint_image`.
- El conector se puede desconectar a mitad de la sesión: descarga cada resultado en cuanto
  termina (`curl -s -o archivo URL`).

## Subir la referencia

1. `media_upload` con `filename` y `content_type` → devuelve `upload_url` y `media_id`.
2. `curl -X PUT -H "Content-Type: image/jpeg" --data-binary @archivo 'upload_url'` → 200.
3. `media_confirm` con `type: image` y el `media_id`.

Reutiliza ese `media_id` en todas las generaciones.

## Parámetros que funcionaron

- **Imagen base** (identidad y encuadre): `nano_banana_pro`, rol `image_references`
  (el servidor corrige `image` y avisa), `aspect_ratio` 1:1 o 16:9. Entrega 2048 o 2752 px.
- **Video desde imagen**: `seedance_2_5`, `mode: 'omni_reference'`, `start_image` (y
  `end_image` si debe terminar en una pose), `resolution` 720p o 1080p, `duration` 4-30,
  `generate_audio: false`, `aspect_ratio` igual al de la imagen. El `start_image` puede ser el
  id de un trabajo de imagen anterior.
- Seedance 2.5 a 1:1 1080p entrega **1440×1440, HEVC 10 bits, 24 fps**; a 720p, 960×960 H.264.
  Una imagen base 16:9 puede reencuadrarse sola (la portada de Kivo quedó centrada).
- **Recorte de fondo**: `remove_background` con `media_type: video` y el id del trabajo.
  Devuelve **H.264 sin alfa, con el sujeto sobre negro puro**. Conserva el original: el alfa se
  reconstruye comparando ambos (`scripts/componer_alfa.py`).
- **Ampliación** (`outpaint_image`): entrega el doble de la resolución anunciada, pero inventa
  fondos recargados. Para una escena limpia es mejor generar la imagen de nuevo con referencia.

## Lotes y límites

- `generate_*_batch` admite 1-12 pedidos, pero el plan plus corre **6 trabajos a la vez**:
  el séptimo devuelve 429 `rate_limit_reached`. Espera con `jobs_wait` (máximo 15 s por
  llamada) y lanza el resto cuando haya cupo.
- Un pedido de video puede volver con **"Preset X was recommended instead of submitting a
  job"**: repítelo con `declined_preset_id` igual al id sugerido.
- Consulta el costo con `get_cost: true` (no funciona dentro de un lote).

## Plantillas de prompt

Abre siempre con la identidad y enumera las piezas del personaje. Ejemplo:

> Keep the character exactly as in the reference image: same face, same cyan holographic visor
> over one eye, same indigo collar with the round glowing K medallion, same white gloves and
> boots with cyan accents, same amber fur, same huge ears with glowing cyan circuits, same
> proportions and 3D animated style.

Cierra con: *No readable text, no letters except the K on his medallion.*

**Giro hacia un lado** (repetir con el otro lado; ambos con el mismo `start_image`):

> Static locked-off tripod camera: the camera never moves, no zoom, no pan. The character keeps
> exactly the same standing pose: body, arms, hands, legs, feet and tail stay perfectly still.
> Only his head and eyes move: he slowly and smoothly turns his head to look toward the right
> side of the frame (the viewer's right), in one single continuous turn at a constant slow
> speed, ending in a three-quarter view. No blinking, no talking, no extra gestures. Same
> background and lighting throughout.

Resultado real: arranca lento y en la segunda mitad también gira el torso. Se ve natural; el
muestreo por cambio visible corrige el ritmo.

**Reacción que vuelve a la pose** (`start_image` = `end_image`):

> Static locked-off tripod camera. The character starts in exactly this pose, lifts one hand
> and waves hello at the viewer twice with a warm, confident smile, then lowers the hand and
> returns to exactly the same starting pose. Feet stay planted. Same background and lighting.

**Encendido pieza por pieza** (`start_image` = versión apagada, `end_image` = render oficial):

> Static locked-off camera, no camera movement at all. The character starts powered down in the
> dark with his eyes closed. He powers on in sequence: first a warm amber light sweeps up
> across his fur, then the circuit lines inside his ears light up from base to tip, then his
> visor boots up with data while he opens his eyes, and finally the medallion ignites with a
> bright pulse. He ends in exactly the same pose. The character never leaves his spot.

Seedance respetó el orden. La versión apagada se hizo editando el render con Nano Banana Pro:
mismo encuadre, piezas apagadas, escena más oscura, ojos cerrados.

**Detalle en bucle** (desde una imagen base de primer plano, 720p):

> Static camera. [qué se anima: luz que recorre el pelaje, orejas que giran escuchando,
> visor con datos, medallón que late]. Calm, continuous, loopable motion.

**Rol en escena** (imagen base 16:9, personaje a un lado y panel holográfico al otro):

> Very slow push-in. [acción del rol]. Continuous motion.

## Revisión obligatoria

Antes de procesar, mira cada clip con `scripts/medios.py hoja` y `curva`. Se buscan:
cortes (pasos que multiplican el típico), cámara que se movió pese al prompt, cambios de
identidad y el tramo útil. En los clips desde imagen, el paso entre el fotograma 0 y el 1 suele
ser mayor (el modelo "asienta" la imagen): no es un corte.

## Registrar

Después de cada sesión, actualiza el panel `Herramientas/Higgsfield - Panel.md` del vault y
`image_generation_memory.json` (último trabajo y secuencia con nombre), y guarda los ids en
`trabajos-higgsfield.tsv` junto a los crudos.
