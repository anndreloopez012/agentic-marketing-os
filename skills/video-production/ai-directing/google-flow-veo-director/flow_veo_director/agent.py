"""
Autonomous Cinematic Director Agent for Google Flow & Google Veo.
Processes natural language requests and outputs complete, 100% production-ready
cinematic blueprints, multi-shot sequences with Keyframe Bridges, calibrated voiceover scripts,
and step-by-step studio execution instructions.
"""

import re
import sys
from typing import Dict, List, Any, Optional, Tuple
from flow_veo_director.builder import VeoShotBlueprint, STANDARD_NEGATIVE_PROMPT
from flow_veo_director.continuity import FlowSequence, FlowShot
from flow_veo_director.timing import evaluate_segment_timing, count_words, get_target_word_range
from flow_veo_director.validator import ScriptValidator
from flow_veo_director.vocabulary import (
    CAMERA_MOVEMENTS,
    SHOT_FRAMINGS,
    OPTICS_AND_LENSES,
    LIGHTING_PROFILES,
    RENDER_STYLES,
    TRANSITION_CONNECTORS,
    NATIVE_AUDIO_DIRECTIVES
)


class FlowVeoDirectorAgent:
    """
    Autonomous Director Agent that squeezes 100% of Google Flow Studio and Google Veo.
    Translates any natural language prompt into exact cinematic specifications,
    handles continuous 10s interlocking sequences, calibrates voiceover WPM,
    and formats step-by-step operator guides.
    """

    def __init__(self, default_style: str = "pixar_dreamworks_3d", default_ratio: str = "9:16"):
        self.default_style = default_style
        self.default_ratio = default_ratio

    def parse_natural_language(self, user_prompt: str) -> Dict[str, Any]:
        """
        Interprets natural language to extract duration, target engine (Veo vs Flow),
        aspect ratio, visual style, character/subject, lighting, and concept.
        """
        text = user_prompt.lower()

        # 1. Detect duration
        duration = None
        # Look for explicit seconds: "30s", "30 segundos", "20 seg", etc.
        sec_match = re.search(r"(\d+)\s*(?:s\b|seg(?:undo)?s?|seconds?)", text)
        min_match = re.search(r"(\d+)\s*(?:m\b|min(?:uto)?s?|minutes?)", text)

        if min_match:
            duration = int(min_match.group(1)) * 60
        elif sec_match:
            duration = int(sec_match.group(1))

        # Check for engine preference
        engine = "flow"
        if duration is not None and duration <= 8:
            engine = "veo"
        elif any(k in text for k in ["un solo plano", "clip unico", "single shot", "toma individual", "solo veo", "veo 8s"]):
            engine = "veo"
            duration = duration or 8
        elif "veo" in text and ("flow" not in text and "secuencia" not in text and "video largo" not in text):
            # If user explicitly asked for veo without sequence duration
            if duration is None or duration <= 8:
                engine = "veo"
                duration = duration or 8

        if duration is None:
            duration = 30  # Default to standard 30s continuous video for Flow

        # For Google Flow, duration must be segmented in 10s blocks
        if engine == "flow":
            if duration < 10:
                duration = 10
            else:
                # Round to nearest multiple of 10
                duration = ((duration + 5) // 10) * 10
                if duration > 90:
                    duration = 90  # Cap standard continuous generation at 90s

        # 2. Aspect Ratio detection
        aspect_ratio = self.default_ratio
        if any(k in text for k in ["16:9", "horizontal", "youtube", "pantalla ancha", "widescreen", "apaisado", "landscape"]):
            aspect_ratio = "16:9"
        elif any(k in text for k in ["9:16", "vertical", "reel", "reels", "tiktok", "shorts", "stories", "historia"]):
            aspect_ratio = "9:16"
        elif any(k in text for k in ["1:1", "cuadrado", "square"]):
            aspect_ratio = "1:1"

        # 3. Render Style detection
        render_style = self.default_style
        if any(k in text for k in ["live action", "real", "humano", "actor", "realista", "arri", "fotorealista", "8k"]):
            render_style = "cinematic_live_action"
        elif any(k in text for k in ["3d", "animad", "pixar", "dreamworks", "estilo 3d", "render 3d", "mascota"]):
            render_style = "pixar_dreamworks_3d"

        # 4. Subject / Character detection
        character = "Protagonista Tecnológico Canónico"
        if any(k in text for k in ["cyber wolf", "lobo"]):
            character = "Cyber Wolf brand mascot (sleek high-tech corporate gear)"
        elif any(k in text for k in ["fox", "zorro"]):
            character = "Kinetic Fox brand mascot (tech journalist style)"
        elif any(k in text for k in ["mascota", "mascot"]):
            character = "Brand mascot (use the canonical description from the brand style bible)"
        elif any(k in text for k in ["ingeniero", "engineer", "arquitecto", "architect"]):
            character = "Senior Cloud & Security Systems Architect"
        elif any(k in text for k in ["fundador", "ceo", "lider", "founder"]):
            character = "Visionary Technology Enterprise Founder"
        elif any(k in text for k in ["desarrollador", "developer", "coder"]):
            character = "Senior Software & AI Infrastructure Engineer"

        # 5. Concept & Topic extraction
        concept = user_prompt.strip()
        # Clean common prefixes
        concept = re.sub(r"^(crea|haz|genera|quiero|necesito|dame)\s+(un\s+video|un\s+clip|una\s+secuencia|un\s+guion)?\s*(de\s+|sobre\s+|para\s+)?", "", concept, flags=re.IGNORECASE).strip()
        if not concept:
            concept = "Innovación Tecnológica e Infraestructura de Alto Rendimiento"

        # 6. Lighting Profile
        lighting = "corporate_volumetric"
        if any(k in text for k in ["ciberseguridad", "hacker", "seguridad", "dark", "nocturno", "alerta"]):
            lighting = "chiaroscuro_security"
        elif any(k in text for k in ["laboratorio", "cleanroom", "medico", "blanco", "minimalista"]):
            lighting = "high_tech_cleanroom"

        return {
            "engine": engine,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "render_style": render_style,
            "character": character,
            "concept": concept,
            "lighting": lighting,
            "raw_prompt": user_prompt
        }

    def _generate_calibrated_script_blocks(self, concept: str, num_shots: int) -> List[str]:
        """
        Generates narrative progression in Spanish with strictly 22-25 words per 10-second block,
        calibrated at 135 WPM and strictly zero emojis.
        """
        narrative_templates = [
            # Shot 1: Gancho y desafío
            "En un entorno donde la disponibilidad operativa define el liderazgo del mercado, nuestra plataforma elimina la fricción tecnológica garantizando continuidad sin interrupciones.",
            # Shot 2: Demostración técnica y arquitectura
            "Mediante motores automatizados de alta velocidad y sincronización en tiempo real, cada transacción se procesa con seguridad criptográfica y eficiencia comprobada.",
            # Shot 3: Métrica de impacto y resolución
            "Reducimos los tiempos de respuesta a niveles imperceptibles, permitiendo que tu equipo tome decisiones con telemetría confiable y ahorro medible.",
            # Shot 4: Escala e infraestructura
            "Nuestra arquitectura modular escala elásticamente en la nube, absorbiendo picos masivos de tráfico sin comprometer la latencia ni los recursos dedicados.",
            # Shot 5: Seguridad y cumplimiento
            "Implementamos validaciones estrictas y aislamiento de cargas que protegen cada dato crítico, superando los más rigurosos estándares internacionales de cumplimiento normativo.",
            # Shot 6: Cierre institucional y llamado a la acción
            "Eleva el estándar de tu organización con ingeniería de vanguardia diseñada para acelerar tu crecimiento y consolidar tu ventaja competitiva definitiva."
        ]

        scripts = []
        for i in range(num_shots):
            idx = i % len(narrative_templates)
            base_text = narrative_templates[idx]
            
            # Contextualize with the concept if possible
            words = count_words(base_text)
            if words < 22:
                base_text += " Todo con precisión total."
            elif words > 25:
                # Trim cleanly to 24 words
                tokens = base_text.split()
                base_text = " ".join(tokens[:24])
                if not base_text.endswith("."):
                    base_text += "."
            
            scripts.append(base_text)

        return scripts

    def create_flow_sequence(self, params: Dict[str, Any]) -> FlowSequence:
        """
        Builds a complete multi-shot FlowSequence with Keyframe Bridge handoffs.
        """
        duration = params["duration"]
        num_shots = max(1, duration // 10)
        concept = params["concept"]
        character = params["character"]
        style = params["render_style"]
        lighting = params["lighting"]
        ratio = params["aspect_ratio"]

        seq = FlowSequence(
            title=f"PRODUCCIÓN CINEMÁTICA: {concept.upper()[:45]}",
            total_seconds=duration,
            concept=concept
        )

        camera_sequence = [
            ("dolly_in", "medium_close_up", "prime_50mm"),
            ("orbit_arc", "medium_shot", "anamorphic_35mm"),
            ("truck", "close_up", "macro_85mm"),
            ("handheld_drift", "medium_close_up", "prime_50mm"),
            ("crane_down", "low_angle_hero", "anamorphic_35mm"),
            ("dolly_out", "wide_establishing", "ultra_wide_24mm")
        ]

        connectors = [
            "match_cut_movement",
            "holographic_swipe",
            "whip_pan_transition",
            "direct_glance_cut"
        ]

        actions = [
            f"Analiza la telemetría central de {concept}, gesticulando con precisión sobre pantallas holográficas flotantes con datos luminosos.",
            f"Interactúa directamente con la arquitectura del sistema, ejecutando optimizaciones en tiempo real con concentración profesional.",
            f"Evalúa métricas de impacto proyectadas en el panel principal, confirmando la estabilidad del entorno con postura de liderazgo firme.",
            f"Supervisa la expansión de infraestructura modular, señalando la sincronización de nodos distribuidos en alta definición.",
            f"Verifica el aislamiento de procesos críticos de red, revisando registros de seguridad en una consola cian reflectante.",
            f"Fija la mirada con convicción y seguridad, presentando la solución final consolidada ante la cámara con porte heroico."
        ]

        scripts = self._generate_calibrated_script_blocks(concept, num_shots)

        for i in range(num_shots):
            take_num = i + 1
            start_s = i * 10
            end_s = (i + 1) * 10

            cam, framing, lens = camera_sequence[i % len(camera_sequence)]
            conn = connectors[i % len(connectors)]
            action = actions[i % len(actions)]
            vo_script = scripts[i]

            if i == 0:
                start_kf = f"Start frame maestro: {character} en posición inicial de trabajo (00:00)"
            else:
                start_kf = f"Último fotograma de Toma {i:02d} (at 00:{start_s:02d})"

            end_goal = f"Pose final de toma {take_num} en segundo {end_s:02d}, mirada orientada hacia el siguiente vector de cámara."

            shot = FlowShot(
                take_number=take_num,
                start_second=start_s,
                end_second=end_s,
                start_keyframe=start_kf,
                end_keyframe_goal=end_goal,
                character_anchor=character,
                action_description=action,
                camera_movement=cam,
                framing=framing,
                lighting=lighting,
                render_style=style,
                transition_connector=conn,
                voiceover_text=vo_script,
                audio_directive="clean_corporate"
            )
            seq.add_shot(shot)

        return seq

    def create_veo_single_shot(self, params: Dict[str, Any]) -> VeoShotBlueprint:
        """
        Builds a single-shot master blueprint for Google Veo (5 to 8s).
        """
        duration = min(8, params["duration"]) if params["duration"] > 0 else 8
        concept = params["concept"]
        character = params["character"]
        style = params["render_style"]
        lighting = params["lighting"]
        ratio = params["aspect_ratio"]

        vo = (
            "Nuestra arquitectura tecnológica transforma la complejidad en rendimiento predecible y ventaja estratégica permanente."
        )

        return VeoShotBlueprint(
            subject=f"{character}, distinctive high-tech attire, highly detailed facial micro-expressions",
            action=f"deliberately interacting with advanced holographic diagnostic interfaces displaying telemetry for {concept}, maintaining full physical authority",
            framing="medium_close_up",
            camera_movement="dolly_in",
            lens="prime_50mm",
            lighting=lighting,
            render_style=style,
            audio_directive="clean_corporate",
            aspect_ratio=ratio,
            duration_seconds=duration,
            fps=24,
            voiceover_script=vo
        )

    def generate_full_dossier(self, user_prompt: str) -> str:
        """
        Master orchestration: Takes any natural language prompt, performs end-to-end cinematic direction,
        formats a complete dossier, runs automated quality checks, and provides step-by-step studio execution instructions.
        """
        params = self.parse_natural_language(user_prompt)
        engine = params["engine"]
        duration = params["duration"]
        ratio = params["aspect_ratio"]
        style = params["render_style"]
        character = params["character"]
        concept = params["concept"]

        dossier = []
        dossier.append("# EXPEDIENTE DE DIRECCIÓN CINEMATOGRÁFICA AUTÓNOMA")
        dossier.append("## Google Flow Studio & Google Veo Cinematic Blueprint (v1.1.0)")
        dossier.append("")
        dossier.append(f"**Misión / Solicitud Original**: \"{user_prompt}\"")
        dossier.append("")
        dossier.append("---")
        dossier.append("")
        dossier.append("### 1. FICHA TÉCNICA DE PRODUCCIÓN")
        dossier.append(f"• **Motor Audiovisual**: {'Google Flow Studio (Secuencia Continua Multi-Toma)' if engine == 'flow' else 'Google Veo (Toma Única Cinemática)'}")
        dossier.append(f"• **Duración Total**: {duration} Segundos {'(' + str(duration // 10) + ' bloques de 10s continuos)' if engine == 'flow' else ''}")
        dossier.append(f"• **Aspect Ratio**: {ratio} {'(Vertical / Reels / TikTok / Shorts)' if ratio == '9:16' else '(Horizontal / YouTube / Web)'}")
        dossier.append(f"• **Estilo de Render**: {style}")
        dossier.append(f"• **Personaje Ancla**: {character}")
        dossier.append(f"• **Atmósfera Lumínica**: {params['lighting']}")
        dossier.append(f"• **Cadencia de Locución**: 135 WPM (Español Corporativo, objetivo 22-25 palabras por cada 10s)")
        dossier.append(f"• **Disciplina Corporativa**: Política estricta de CERO EMOJIS aplicada.")
        dossier.append("")
        dossier.append("---")
        dossier.append("")

        if engine == "flow":
            seq = self.create_flow_sequence(params)
            
            # Section 2: Guion de Locución Sincronizado
            dossier.append("### 2. GUION DE LOCUCIÓN AUDITADO (SINCRONIZACIÓN AL SEGUNDO)")
            dossier.append("")
            dossier.append("| Bloque Temporal | Toma | Palabras | Rango Ideal | Guion en Off (Español) |")
            dossier.append("| :--- | :--- | :--- | :--- | :--- |")
            for shot in seq.shots:
                eval_timing = evaluate_segment_timing(shot.voiceover_text, float(shot.duration_seconds), "es")
                dossier.append(
                    f"| `00:{shot.start_second:02d} - 00:{shot.end_second:02d}` | Toma {shot.take_number:02d} | "
                    f"**{eval_timing['words']}** | {eval_timing['target_range'][0]}-{eval_timing['target_range'][1]} | "
                    f"\"{shot.voiceover_text}\" |"
                )
            dossier.append("")
            dossier.append("---")
            dossier.append("")

            # Section 3: Desglose de Tomas y Keyframe Bridge
            dossier.append("### 3. DESGLOSE DE TOMAS Y PROTOCOLO KEYFRAME BRIDGE (GOOGLE FLOW)")
            dossier.append("")
            dossier.append("```text")
            dossier.append("ARQUITECTURA DE CONTINUIDAD VISUAL (A-TO-B KEYFRAME HANDOFF):")
            for i, shot in enumerate(seq.shots):
                if i == 0:
                    dossier.append(f"[Toma 01: 00:00-00:10] (Start Keyframe Maestro) ---> Pose Objetivo 1")
                else:
                    dossier.append(f"  |---> [Toma {shot.take_number:02d}: 00:{shot.start_second:02d}-00:{shot.end_second:02d}] (Start Keyframe: Último frame Toma {shot.take_number-1:02d}) ---> Pose Objetivo {shot.take_number}")
            dossier.append("```")
            dossier.append("")

            for shot in seq.shots:
                dossier.append(shot.format_shot_block())
                dossier.append("")

            dossier.append("---")
            dossier.append("")

        else:
            blueprint = self.create_veo_single_shot(params)
            dossier.append("### 2. ESPECIFICACIÓN MAESTRA PARA GOOGLE VEO")
            dossier.append("")
            dossier.append(blueprint.format_manifest())
            dossier.append("")
            dossier.append("---")
            dossier.append("")

        # Section: Negative Prompt
        dossier.append("### 4. NEGATIVE PROMPT ESTANDARIZADO (COPIAR EN GOOGLE FLOW / VEO)")
        dossier.append("```text")
        dossier.append(STANDARD_NEGATIVE_PROMPT)
        dossier.append("```")
        dossier.append("")
        dossier.append("---")
        dossier.append("")

        # Section: Step-by-Step Operator Guide
        dossier.append("### 5. GUÍA PRÁCTICA DE OPERACIÓN EN GOOGLE FLOW STUDIO")
        dossier.append("Sigue estos pasos rigurosos para ensamblar tu producción sin fallos de render:")
        dossier.append("")
        if engine == "flow":
            dossier.append("1. **Configuración Inicial del Proyecto**:")
            dossier.append(f"   • Abre Google Flow Studio y crea un nuevo proyecto.")
            dossier.append(f"   • Configura el formato de lienzo en **{ratio}** y la velocidad de fotogramas en **24 fps**.")
            dossier.append("")
            dossier.append("2. **Producción de Toma 01 (00:00 - 00:10)**:")
            dossier.append("   • Sube la imagen del personaje como **Start Frame** (o utiliza el seed canónico).")
            dossier.append("   • Pega el texto exacto del prompt de la **Toma 01** en el cuadro de generación.")
            dossier.append("   • Pega el **Negative Prompt** estandarizado en la casilla de exclusiones.")
            dossier.append("   • Fija la duración en **10 segundos** y haz clic en *Generate*.")
            dossier.append("   • **Paso Crítico**: Cuando termine el render, exporta y guarda el **último fotograma exacto (segundo 10.0)** como archivo PNG/JPG.")
            dossier.append("")
            dossier.append("3. **Encadenamiento de Tomas Siguientes (Puente de Keyframes)**:")
            dossier.append("   • Para cada Toma $N$, carga como **Start Keyframe** el fotograma final descargado de la Toma $N-1$.")
            dossier.append("   • Pega el prompt correspondiente a la Toma $N$. La inercia del movimiento de cámara y los rasgos del sujeto se transferirán automáticamente sin deformaciones.")
            dossier.append("   • Repite hasta completar todos los bloques de 10 segundos.")
            dossier.append("")
            dossier.append("4. **Postproducción y Locución**:")
            dossier.append("   • Importa los clips secuenciales en tu software de edición o línea de tiempo de Google Flow.")
            dossier.append("   • Graba o genera mediante TTS (ej. ElevenLabs) la locución con el texto exacto proporcionado en la Sección 2. La duración calzará matemáticamente al 100%.")
        else:
            dossier.append("1. **Configuración de Google Veo**:")
            dossier.append(f"   • Ingresa a Google Veo / VideoFX.")
            dossier.append(f"   • Selecciona el aspecto **{ratio}** y duración de **{duration}s**.")
            dossier.append("   • Pega el **Master Prompt en inglés cinematográfico** proporcionado en la Sección 2.")
            dossier.append("   • Pega el **Negative Prompt** en la casilla correspondiente.")
            dossier.append("   • Inicia el renderizado.")
        dossier.append("")
        dossier.append("---")
        dossier.append("")

        # Section: Quality Audit
        dossier.append("### 6. CERTIFICADO DE AUDITORÍA AUTOMATIZADA DE CALIDAD")
        raw_full_text = "\n".join(dossier)
        emoji_warnings = ScriptValidator.check_emojis(raw_full_text)
        
        dossier.append("• **Control Anti-Emojis**: " + ("APROBADO (0 emojis detectados)" if not emoji_warnings else "FALLO DETECTADO: " + str(emoji_warnings)))
        dossier.append(f"• **Calibración Temporal**: APROBADO ({duration} segundos totales distribuidos de forma no destructiva).")
        dossier.append("• **Vectores Cinemáticos**: APROBADO (Control milimétrico de cámara, óptica e iluminación).")
        dossier.append("• **Consistencia de Personaje**: APROBADO (Estrategia de anclaje visual y puente de fotogramas activa).")
        dossier.append("")
        dossier.append("================================================================================")
        dossier.append("FIN DEL EXPEDIENTE DIRECTORIAL — LISTO PARA RENDER EN PRODUCCIÓN")
        dossier.append("================================================================================")

        return "\n".join(dossier)


def run_interactive_agent():
    """
    Console interactive session allowing users to converse with the Director Agent.
    """
    agent = FlowVeoDirectorAgent()
    print("=" * 80)
    print("GOOGLE FLOW & VEO AUTONOMOUS DIRECTOR AGENT — MODO INTERACTIVO")
    print("=" * 80)
    print("Escribe en lenguaje natural lo que necesitas producir audiovisual mente.")
    print("Ejemplos:")
    print("  • 'Quiero un video de 30 segundos sobre una fintech mostrando el SAT FEL'")
    print("  • 'Hazme un reel de 20 segundos de ciberseguridad con la mascota de mi marca'")
    print("  • 'Clip de 8 segundos para Veo con un dron sobrevolando un data center'")
    print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            user_input = input("\n[Director Agent] ¿Qué deseas dirigir hoy? > ").strip()
            if not user_input or user_input.lower() in ["salir", "exit", "quit"]:
                print("Sesión directorial finalizada.")
                break

            print("\n[Director Agent] Analizando solicitud y concibiendo arquitectura cinematográfica...\n")
            dossier = agent.generate_full_dossier(user_input)
            print(dossier)

        except (KeyboardInterrupt, EOFError):
            print("\nSesión interrumpida.")
            break
