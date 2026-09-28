"""
Vocabulary and Cinema Grammar for Google Flow & Veo.
Contains standard camera movements, shot framings, lighting profiles, optics,
audio directives, and transition connectors.
"""

from typing import Dict, List

CAMERA_MOVEMENTS: Dict[str, Dict[str, str]] = {
    "dolly_in": {
        "en": "slow smooth dolly-in towards subject at 0.8 m/s",
        "desc": "Acercamiento físico de cámara que intensifica emoción, tensión o concentración.",
        "category": "axial"
    },
    "dolly_out": {
        "en": "measured slow dolly-out revealing surrounding environment",
        "desc": "Alejamiento físico de cámara para desvelar escala, soledad o contexto espacial.",
        "category": "axial"
    },
    "dolly_zoom": {
        "en": "dramatic vertigo dolly-zoom (push in while zooming out)",
        "desc": "Efecto Vértigo. Distorsiona la perspectiva del fondo manteniendo el tamaño del sujeto.",
        "category": "optical_mechanical"
    },
    "pan_horizontal": {
        "en": "steady horizontal pan from left to right at controlled angular speed",
        "desc": "Giro sobre el eje del trípode para explorar el escenario de izquierda a derecha.",
        "category": "rotational"
    },
    "whip_pan": {
        "en": "rapid whip-pan with natural motion blur",
        "desc": "Giro ultrarrápido con desenfoque de movimiento; actúa como conector de corte dinámico.",
        "category": "transition"
    },
    "tilt_up": {
        "en": "vertical tilt-up rising from details to wide perspective",
        "desc": "Inclinación vertical hacia arriba para mostrar altura, tecnología monumental o cielos.",
        "category": "rotational"
    },
    "tilt_down": {
        "en": "deliberate tilt-down descending toward subject interaction",
        "desc": "Inclinación vertical hacia abajo enfocando hacia el dispositivo o superficie de trabajo.",
        "category": "rotational"
    },
    "truck": {
        "en": "lateral tracking truck shot moving parallel to subject",
        "desc": "Desplazamiento horizontal paralelo al sujeto mientras camina o interactúa.",
        "category": "lateral"
    },
    "pedestal": {
        "en": "smooth mechanical pedestal rise along vertical axis",
        "desc": "Elevación física vertical en línea recta manteniendo el horizonte nivelado.",
        "category": "vertical"
    },
    "crane_down": {
        "en": "sweeping crane shot swooping down from ceiling to medium close-up",
        "desc": "Movimiento amplio y fluido de grúa descendiendo desde las alturas.",
        "category": "crane"
    },
    "orbit_arc": {
        "en": "graceful 180-degree orbital arc shot circulating subject",
        "desc": "Giro orbital en semicírculo alrededor del sujeto, ideal para tomas de presentación heroica.",
        "category": "orbital"
    },
    "aerial_drone": {
        "en": "cinematic high-altitude drone shot gliding forward over architecture",
        "desc": "Toma aérea continua con perspectiva amplia sobre infraestructura o campus corporativo.",
        "category": "aerial"
    },
    "birds_eye": {
        "en": "top-down 90-degree bird's-eye view looking straight down",
        "desc": "Plano cenital perpendicular mostrando esquemas, terminales o flujos desde arriba.",
        "category": "aerial"
    },
    "handheld_drift": {
        "en": "subtle floating handheld camera drift with realistic organic balance",
        "desc": "Sensación de cámara en mano estabilizada (estilo Steadicam) con respiración sutil.",
        "category": "stabilized"
    },
    "static_lock": {
        "en": "locked-off static tripod shot with zero camera drift",
        "desc": "Cámara completamente inmóvil para máxima estabilidad en demostraciones y datos duros.",
        "category": "static"
    }
}

SHOT_FRAMINGS: Dict[str, Dict[str, str]] = {
    "extreme_wide_shot": {
        "en": "extreme wide establishing shot (EWS)",
        "desc": "Plano general extremo para ubicar la escala colosal de un centro de datos o ciudad."
    },
    "wide_shot": {
        "en": "wide shot (WS) showing full environment and subject context",
        "desc": "Plano general con sujeto completo y amplio margen del entorno tecnológico."
    },
    "full_shot": {
        "en": "full shot (FS) framing character from head to toe",
        "desc": "Plano entero que muestra postura corporal, vestuario y calzado técnico completo."
    },
    "medium_shot": {
        "en": "medium shot (MS) framed from waist up",
        "desc": "Plano medio de cintura arriba; equilibrio entre expresión del personaje y entorno."
    },
    "medium_close_up": {
        "en": "medium close-up (MCU) framing from chest to head",
        "desc": "Plano medio corto (pecho a cabeza); estándar de oro para locución, autoridad y confianza."
    },
    "close_up": {
        "en": "cinematic close-up (CU) focusing on facial expression and headgear",
        "desc": "Primer plano centrado en visor, ojos y reacciones micro-expresivas."
    },
    "extreme_close_up": {
        "en": "macro extreme close-up (ECU) revealing micro-details",
        "desc": "Plano detalle extremo sobre componentes biónicos, circuitos integrados o pantallas táctiles."
    },
    "over_the_shoulder": {
        "en": "over-the-shoulder (OTS) shot looking at workspace interface",
        "desc": "Plano sobre el hombro del personaje mirando hacia pantallas u hologramas."
    },
    "low_angle_hero": {
        "en": "low-angle hero shot looking upward",
        "desc": "Contrapicado que otorga liderazgo, resiliencia, estatura heroica y autoridad corporativa."
    },
    "high_angle_analytic": {
        "en": "high-angle analytic perspective looking downward",
        "desc": "Picado que transmite supervisión analítica, control de métricas y evaluación objetiva."
    },
    "dutch_angle_alert": {
        "en": "canted Dutch angle shot with 12-degree camera tilt",
        "desc": "Plano holandés inclinado; expresa alerta crítica de ciberseguridad o anomalía en tiempo real."
    }
}

OPTICS_AND_LENSES: Dict[str, str] = {
    "anamorphic_35mm": "shot on 35mm anamorphic prime lens, subtle edge compression, cinematic horizontal oval bokeh",
    "prime_50mm": "shot on 50mm f/1.4 prime lens, natural human eye perspective, sharp subject isolation, buttery background blur",
    "macro_85mm": "shot on 85mm macro lens, ultra-shallow depth of field, hyper-crisp optical micro-contrast",
    "wide_24mm": "shot on 24mm cinema prime lens, expansive environmental field of view with zero barrel distortion",
    "deep_focus": "panavision deep focus cinema lens, f/11 aperture, crisp clarity from foreground to background horizon"
}

LIGHTING_PROFILES: Dict[str, Dict[str, str]] = {
    "corporate_volumetric": {
        "en": "volumetric atmospheric studio lighting, gentle god rays cutting through clean air, deep obsidian navy shadows, hyper cyan ambient fill",
        "desc": "Iluminación corporativa prémium con rayos de luz visibles y acentos cian y azul marino."
    },
    "high_tech_cleanroom": {
        "en": "pristine high-key corporate cleanroom illumination, soft 5600K daylight balanced softboxes, minimal shadows, ray-traced glass reflections",
        "desc": "Luz diurna fría y homogénea sin sombras duras, ideal para laboratorios de I+D y nube."
    },
    "chiaroscuro_security": {
        "en": "dramatic low-key chiaroscuro lighting, sharp directional rim light slicing subject silhouette, intense neon amber alert glow",
        "desc": "Alto contraste dramático para ciberseguridad, respuesta ante incidentes y análisis de riesgos."
    },
    "golden_hour_executive": {
        "en": "warm executive golden-hour sunlight pouring through floor-to-ceiling glass windows, warm amber rim light, soft contrast",
        "desc": "Luz dorada cálida que entra por ventanales corporativos; transmite éxito comercial y madurez."
    },
    "cyberpunk_datacenter": {
        "en": "deep midnight server room lighting, alternating pulse of emerald green status LEDs and electric purple fiber optic trails",
        "desc": "Iluminación de centro de datos con cables de fibra óptica y destellos esmeralda."
    }
}

RENDER_STYLES: Dict[str, str] = {
    "pixar_dreamworks_3d": "3D animated feature film render quality, Pixar and DreamWorks character aesthetic, tactile physically-based shaders, subsurface scattering on fur and skin, zero AI artifacts, photorealistic material textures",
    "cinematic_live_action": "photorealistic 8K cinematic live action, Arri Alexa Mini LF camera sensor, natural skin pores, realistic cloth weave, optical motion blur, Academy Color Encoding System (ACES) color grade",
    "stylized_tech_scifi": "hyper-stylized high-end 3D corporate science-fiction render, polished brushed titanium surfaces, glowing emissive interface glyphs, Octane Render style, pristine clarity",
    "hybrid_motion_graphics": "seamless blend of high-polish 3D character and floating vector HUD infographics, crisp typography in JetBrains Mono and Inter, clean motion lines"
}

TRANSITION_CONNECTORS: Dict[str, Dict[str, str]] = {
    "match_cut_movement": {
        "en": "seamless match cut aligned with the continuation of arm gesture",
        "desc": "Corte sobre movimiento; la inercia del cuerpo de la toma anterior continúa idéntica en la siguiente."
    },
    "whip_pan_transition": {
        "en": "fast whip-pan motion blur handoff into new angle",
        "desc": "El latigazo de cámara de la toma previa se empareja con la entrada de la nueva."
    },
    "holographic_swipe": {
        "en": "holographic UI window expands outwards briefly wiping the camera frame",
        "desc": "Una ventana holográfica o interfaz cubre el objetivo para revelar el siguiente plano."
    },
    "occlusion_reveal": {
        "en": "foreground pillar slides past the lens revealing the next camera position",
        "desc": "Un elemento en primer plano cruza la pantalla ocultando el punto de corte."
    },
    "direct_glance_cut": {
        "en": "subject locks direct gaze into camera at second 10, cutting cleanly to next perspective",
        "desc": "Corte limpio por mirada directa a cámara en el último segundo del bloque."
    }
}

NATIVE_AUDIO_DIRECTIVES: Dict[str, str] = {
    "clean_corporate": "crisp professional studio acoustics, gentle ambient room tone, soft keyboard clicks in the distance, subtle warm synthesizer pad",
    "cyber_security": "tense low-frequency sub-bass hum, crisp mechanical relay clicks, subtle digital telemetry pinging, zero audio distortion",
    "retail_speed": "lively modern boutique room acoustics, crisp laser barcode scanner beep, smooth receipt paper glide, confident upbeat pace",
    "cloud_infrastructure": "steady low-noise server fan drone in deep background, smooth robotic servo whirr, crisp holographic chime at key moment"
}
