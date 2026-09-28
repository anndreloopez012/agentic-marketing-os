"""
Command-Line Interface for Google Flow & Veo Cinematic Director.
Provides rapid generation of Veo prompts, Google Flow multi-shot sequences,
script timing analysis, quality validation, and the Autonomous Director Agent.
"""

import sys
import argparse
import json
from flow_veo_director.builder import VeoShotBlueprint
from flow_veo_director.continuity import FlowSequence, FlowShot
from flow_veo_director.timing import evaluate_segment_timing, count_words
from flow_veo_director.validator import ScriptValidator
from flow_veo_director.agent import FlowVeoDirectorAgent, run_interactive_agent
from flow_veo_director.vocabulary import (
    CAMERA_MOVEMENTS,
    SHOT_FRAMINGS,
    OPTICS_AND_LENSES,
    LIGHTING_PROFILES,
    RENDER_STYLES,
    TRANSITION_CONNECTORS
)


def cmd_agent(args):
    """Executes the Autonomous Director Agent in natural language or interactive mode."""
    if args.interactive or not args.prompt:
        run_interactive_agent()
        return

    prompt_text = " ".join(args.prompt) if isinstance(args.prompt, list) else args.prompt
    style = "pixar_dreamworks_3d" if args.style == "3d" else "cinematic_live_action"
    agent = FlowVeoDirectorAgent(
        default_style=style,
        default_ratio=args.ratio
    )
    dossier = agent.generate_full_dossier(prompt_text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(dossier)
        print(f"Expediente directorial exportado con éxito a: {args.output}")
    else:
        print(dossier)


def cmd_prompt(args):
    """Generates a single master prompt for Google Veo."""
    blueprint = VeoShotBlueprint(
        subject=args.subject,
        action=args.action,
        framing=args.framing,
        camera_movement=args.camera,
        lens=args.lens,
        lighting=args.lighting,
        render_style=args.render,
        audio_directive=args.audio,
        aspect_ratio=args.ratio,
        duration_seconds=args.duration,
        fps=args.fps,
        voiceover_script=args.vo
    )
    print(blueprint.format_manifest())


def cmd_sequence(args):
    """Generates an interlocking Google Flow multi-shot sequence for long videos."""
    total_seconds = args.duration
    num_shots = max(1, total_seconds // 10)
    
    seq = FlowSequence(
        title=args.title,
        total_seconds=total_seconds,
        concept=args.concept
    )

    cameras = ["dolly_in", "handheld_drift", "orbit_arc", "truck", "crane_down", "static_lock"]
    framings = ["medium_close_up", "close_up", "medium_shot", "over_the_shoulder", "low_angle_hero"]
    connectors = ["match_cut_movement", "holographic_swipe", "whip_pan_transition", "direct_glance_cut"]

    for i in range(num_shots):
        toma_num = i + 1
        start_s = i * 10
        end_s = (i + 1) * 10

        start_kf = f"Start frame image / Asset maestro" if i == 0 else f"Último fotograma de Toma {i:02d} (at 00:{start_s:02d})"
        end_goal = f"Pose final de toma {toma_num}, fijando la mirada hacia la interfaz técnica"
        cam = cameras[i % len(cameras)]
        frame = framings[i % len(framings)]
        conn = connectors[i % len(connectors)]

        # Sample voiceover calibrated to 22-25 words
        sample_vo = (
            f"En esta fase número {toma_num} de tu operación tecnológica, la arquitectura en la nube "
            f"garantiza resiliencia inmediata y protección de datos sin fricciones para tu negocio."
        )

        shot = FlowShot(
            take_number=toma_num,
            start_second=start_s,
            end_second=end_s,
            start_keyframe=start_kf,
            end_keyframe_goal=end_goal,
            character_anchor=args.character or "Corporate Lead / Tech Mascot",
            action_description=f"Action step {toma_num} of {args.concept}. Precise, deliberate gestures demonstrating high authority.",
            camera_movement=cam,
            framing=frame,
            lighting="corporate_volumetric",
            render_style="pixar_dreamworks_3d" if args.style == "3d" else "cinematic_live_action",
            transition_connector=conn,
            voiceover_text=sample_vo
        )
        seq.add_shot(shot)

    storyboard = seq.export_full_storyboard()
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(storyboard)
        print(f"Guion exportado con éxito a: {args.output}")
    else:
        print(storyboard)


def cmd_validate(args):
    """Validates a script markdown file."""
    res = ScriptValidator.audit_markdown_file(args.file)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    if not res.get("passed", False):
        sys.exit(1)


def cmd_vocab(args):
    """Displays available vocabulary commands."""
    cat = args.category.lower()
    if cat == "camera":
        print("\n=== COMANDOS DE MOVIMIENTO DE CÁMARA ===")
        for k, v in CAMERA_MOVEMENTS.items():
            print(f"• {k:<18} [{v['category']}] -> {v['desc']}")
    elif cat == "framing":
        print("\n=== ENCUADRES Y PLANOS CINEMATOGRÁFICOS ===")
        for k, v in SHOT_FRAMINGS.items():
            print(f"• {k:<22} -> {v['desc']}")
    elif cat == "lighting":
        print("\n=== PERFILES DE ILUMINACIÓN Y VOLUMETRÍA ===")
        for k, v in LIGHTING_PROFILES.items():
            print(f"• {k:<22} -> {v['desc']}")
    elif cat == "optics":
        print("\n=== LENTES Y ÓPTICAS CINEMATOGRÁFICAS ===")
        for k, v in OPTICS_AND_LENSES.items():
            print(f"• {k:<18} -> {v}")
    elif cat == "connectors":
        print("\n=== CONECTORES DE TRANSICIÓN CONTINUA ===")
        for k, v in TRANSITION_CONNECTORS.items():
            print(f"• {k:<22} -> {v['desc']}")
    else:
        print("Categorías disponibles: camera, framing, lighting, optics, connectors")


def main():
    parser = argparse.ArgumentParser(
        prog="flow-veo",
        description="Google Flow & Veo Cinematic Director CLI — Herramienta de prompts y secuencias de video largo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: agent
    p_agent = subparsers.add_parser("agent", help="Ejecuta el Agente Director Autónomo que interpreta lenguaje natural")
    p_agent.add_argument("prompt", nargs="*", help="Instrucción en lenguaje natural sobre lo que deseas producir")
    p_agent.add_argument("--interactive", "-i", action="store_true", help="Inicia sesión interactiva de dirección")
    p_agent.add_argument("--ratio", default="9:16", choices=["9:16", "16:9", "1:1"], help="Relación de aspecto")
    p_agent.add_argument("--style", default="3d", choices=["3d", "live_action"], help="Estilo visual predominante")
    p_agent.add_argument("--output", "-o", help="Archivo Markdown de salida para el expediente")
    p_agent.set_defaults(func=cmd_agent)

    # Subcommand: prompt
    p_prompt = subparsers.add_parser("prompt", help="Genera un prompt cinematográfico individual para Google Veo")
    p_prompt.add_argument("--subject", required=True, help="Sujeto principal y atributos físicos")
    p_prompt.add_argument("--action", required=True, help="Acción física principal en 5-8 segundos")
    p_prompt.add_argument("--framing", default="medium_close_up", choices=list(SHOT_FRAMINGS.keys()))
    p_prompt.add_argument("--camera", default="dolly_in", choices=list(CAMERA_MOVEMENTS.keys()))
    p_prompt.add_argument("--lens", default="prime_50mm", choices=list(OPTICS_AND_LENSES.keys()))
    p_prompt.add_argument("--lighting", default="corporate_volumetric", choices=list(LIGHTING_PROFILES.keys()))
    p_prompt.add_argument("--render", default="pixar_dreamworks_3d", choices=list(RENDER_STYLES.keys()))
    p_prompt.add_argument("--audio", default="clean_corporate")
    p_prompt.add_argument("--ratio", default="9:16")
    p_prompt.add_argument("--duration", type=int, default=8)
    p_prompt.add_argument("--fps", type=int, default=24)
    p_prompt.add_argument("--vo", help="Texto de voz en off / locución")
    p_prompt.set_defaults(func=cmd_prompt)

    # Subcommand: sequence
    p_seq = subparsers.add_parser("sequence", help="Desglosa un video largo en bloques continuos de 10s para Google Flow")
    p_seq.add_argument("--duration", type=int, default=30, help="Duración total en segundos (múltiplo de 10)")
    p_seq.add_argument("--title", required=True, help="Título del proyecto")
    p_seq.add_argument("--concept", required=True, help="Arco conceptual o tema central")
    p_seq.add_argument("--character", help="Ruta o descripción canónica del personaje")
    p_seq.add_argument("--style", default="3d", choices=["3d", "live_action"])
    p_seq.add_argument("--output", "-o", help="Archivo Markdown de salida")
    p_seq.set_defaults(func=cmd_sequence)

    # Subcommand: validate
    p_val = subparsers.add_parser("validate", help="Audita un archivo Markdown contra las reglas de Flow y Veo")
    p_val.add_argument("file", help="Ruta al archivo Markdown")
    p_val.set_defaults(func=cmd_validate)

    # Subcommand: vocab
    p_vocab = subparsers.add_parser("vocab", help="Explora el catálogo de comandos cinematográficos")
    p_vocab.add_argument("category", choices=["camera", "framing", "lighting", "optics", "connectors"])
    p_vocab.set_defaults(func=cmd_vocab)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
