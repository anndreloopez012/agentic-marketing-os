# Prompts para Google Veo (toma única 5-8 s)

Sirve también para Kling, Runway, Luma, Sora o Higgsfield: modelos de clip único.

## 1. Cuándo usarlo
- Gancho de apertura de un Reel (primeros 3 segundos).
- Demostración visual corta del producto.
- Cierre de impacto con el anfitrión mirando a cámara.

## 2. Estructura obligatoria

```text
[GOOGLE VEO PROMPT]
Aspect Ratio: 9:16 | Duration: 5-8s | FPS: 24
Subject: [sujeto con rasgos fijos]
Environment: [escenario]
Action: [UNA acción continua]
Camera: [movimiento]
Lighting & Atmosphere: [luces con HEX de marca]
Render Style: [estilo del perfil]
Negative: no text artifacts, no morphing, no extra limbs, no flicker
Image Reference (Start Frame): [ruta a la imagen ancla]

LOCUCIÓN (15-20 palabras si el clip se usa solo; si es parte de un Reel, ver Flow):
"[texto]"
```

## 3. Reglas
- Una sola acción por clip. Dos acciones = morphing y cortes raros.
- El movimiento de cámara se nombra en términos de cine (dolly-in, orbit, crane, tracking, handheld).
- Describir el sujeto siempre con las mismas palabras (copiar de la style bible).
- Si hay imagen de referencia, el prompt describe el movimiento, no vuelve a describir cada rasgo.
- Pedir 2-4 variaciones y elegir; no corregir con prompts larguísimos.

## 4. Ejemplo genérico

```text
[GOOGLE VEO PROMPT]
Aspect Ratio: 9:16 | Duration: 6s | FPS: 24
Subject: a barista in a mustard apron with rolled sleeves, short curly hair
Environment: small specialty coffee bar, warm morning light, espresso machine in focus
Action: she pours latte art in one continuous motion and slides the cup toward camera
Camera: slow dolly-in from medium shot to close-up on the cup
Lighting & Atmosphere: warm key light from window, soft teal fill (#2A9D8F), gentle steam
Render Style: photoreal commercial, shallow depth of field
Negative: no text, no extra hands, no flicker
```
