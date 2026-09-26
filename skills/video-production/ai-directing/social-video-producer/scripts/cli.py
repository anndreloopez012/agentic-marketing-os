#!/usr/bin/env python3
"""
cli.py
CLI unificada de la suite 'social-video-producer'.
Permite ejecutar pipelines de producción completos o por etapas:
1. 'plan': Genera el guion/storyboard técnico y analiza zonas seguras.
2. 'animate': Anima una sola imagen preservando el texto al 100% (cero distorsión).
3. 'interpolate': Transición fluida entre dos imágenes clave con Google Veo.
4. 'produce': Ejecuta la producción completa multi-escena desde un storyboard o lista de imágenes.
"""

import argparse
import json
import os
import sys
from typing import List, Optional

# Importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from veo_client import VeoClient
from text_preserver import TextPreserver
from storyboard_planner import StoryboardPlanner
from video_composer import VideoComposer

def handle_plan(args):
    planner = StoryboardPlanner(platform=args.platform)
    storyboard = planner.plan_sequence(
        image_paths=args.images,
        topic_or_brand=args.topic,
        preferred_motion=args.motion,
        has_critical_text=not args.no_text_preservation
    )
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)
    print(f"\n[CLI] Storyboard generado con éxito en: {args.output}")

def handle_animate(args):
    """
    Anima una sola imagen con Google Veo garantizando 0% distorsión en textos y logos.
    """
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(args.output)) or ".", "temp_production")
    os.makedirs(temp_dir, exist_ok=True)

    text_overlay_path = os.path.join(temp_dir, "text_overlay.png")
    clean_plate_path = os.path.join(temp_dir, "clean_background.png")
    raw_video_path = os.path.join(temp_dir, "raw_veo_animation.mp4")
    conformed_video_path = os.path.join(temp_dir, "conformed_video.mp4")

    preserver = TextPreserver(platform=args.platform)
    composer = VideoComposer(platform=args.platform)
    veo = VeoClient()

    # 1. Separar capa de texto si está activada la preservación
    target_image_for_veo = args.image
    if not args.no_text_preservation:
        print("[CLI] Modo Preservación Activo: Aislando capas de texto y logotipos...")
        preserver.auto_isolate_graphic_layer(
            args.image,
            output_overlay_path=text_overlay_path,
            output_clean_plate_path=clean_plate_path
        )
        target_image_for_veo = clean_plate_path

    # 2. Generar movimiento cinematográfico con Veo
    prompt = args.prompt or (
        f"Cinematic slow camera motion. Smooth continuous 24fps push-in. "
        f"High optical fidelity, studio lighting, no jitter, no morphing."
    )
    veo.generate_video(
        prompt=prompt,
        first_frame=target_image_for_veo,
        model=args.model,
        aspect_ratio=composer.platform_info.get("aspect_ratio", "9:16"),
        duration=args.duration,
        output_path=raw_video_path
    )

    # 3. Superponer capa de texto intacta
    current_video = raw_video_path
    if not args.no_text_preservation and os.path.exists(text_overlay_path):
        overlayed_path = os.path.join(temp_dir, "video_with_text.mp4")
        composer.overlay_lossless_plate(
            video_file=current_video,
            overlay_png=text_overlay_path,
            output_file=overlayed_path,
            animation=args.text_animation
        )
        current_video = overlayed_path

    # 4. Color grading y audio
    composer.apply_color_grading(current_video, conformed_video_path, preset_name=args.color_preset)
    composer.add_audio_and_master(conformed_video_path, args.output, bgm_file=args.bgm)

    print(f"\n[CLI] ¡Video final completado con éxito!: {args.output}")

def handle_interpolate(args):
    """
    Genera una transición fluida entre dos imágenes (first frame y last frame) con Veo.
    """
    veo = VeoClient()
    prompt = args.prompt or "Smooth, seamless cinematic camera transition interpolating between the starting frame and the final frame. Fluid motion, 24fps, high quality."
    veo.generate_video(
        prompt=prompt,
        first_frame=args.first,
        last_frame=args.last,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        duration=args.duration,
        output_path=args.output
    )
    print(f"\n[CLI] ¡Interpolación completada exitosamente en: {args.output}!")

def handle_produce(args):
    """
    Ejecuta una producción completa de múltiples escenas a partir de un storyboard JSON.
    """
    if not os.path.exists(args.storyboard):
        raise FileNotFoundError(f"No se encontró el storyboard: {args.storyboard}")

    with open(args.storyboard, "r", encoding="utf-8") as f:
        sb = json.load(f)

    platform = sb.get("platform", "tiktok")
    scenes = sb.get("scenes", [])
    if not scenes:
        raise ValueError("El storyboard no contiene escenas.")

    composer = VideoComposer(platform=platform)
    veo = VeoClient()
    preserver = TextPreserver(platform=platform)

    temp_dir = os.path.join(os.path.dirname(os.path.abspath(args.output)) or ".", "temp_multi_scene")
    os.makedirs(temp_dir, exist_ok=True)

    generated_scene_videos = []

    for sc in scenes:
        idx = sc.get("scene_index", 1)
        print(f"\n--- [CLI] Produciendo Escena {idx}/{len(scenes)}: {sc.get('role')} ---")
        src_img = sc.get("source_image")
        prompt = sc.get("prompt_veo")
        dur = sc.get("duration_seconds", 4)
        text_mode = sc.get("text_mode", "preserve_lossless_overlay")

        scene_raw_vid = os.path.join(temp_dir, f"scene_{idx}_raw.mp4")
        scene_final_vid = os.path.join(temp_dir, f"scene_{idx}_final.mp4")

        target_img = src_img
        overlay_path = os.path.join(temp_dir, f"scene_{idx}_overlay.png")
        clean_bg_path = os.path.join(temp_dir, f"scene_{idx}_clean.png")

        if text_mode == "preserve_lossless_overlay":
            preserver.auto_isolate_graphic_layer(
                src_img,
                output_overlay_path=overlay_path,
                output_clean_plate_path=clean_bg_path
            )
            target_img = clean_bg_path

        # Generar con Veo
        veo.generate_video(
            prompt=prompt,
            first_frame=target_img,
            model=args.model or "veo-3.1-generate-preview",
            aspect_ratio=composer.platform_info.get("aspect_ratio", "9:16"),
            duration=dur,
            output_path=scene_raw_vid
        )

        # Componer texto si aplica
        if text_mode == "preserve_lossless_overlay" and os.path.exists(overlay_path):
            composer.overlay_lossless_plate(scene_raw_vid, overlay_path, scene_final_vid, animation="fade_in")
        else:
            scene_final_vid = scene_raw_vid

        generated_scene_videos.append(scene_final_vid)

    # Concatenar escenas con transiciones
    joined_video = os.path.join(temp_dir, "joined_video.mp4")
    composer.concatenate_with_transitions(generated_scene_videos, joined_video, transition=args.transition)

    # Color grading
    colored_video = os.path.join(temp_dir, "colored_video.mp4")
    composer.apply_color_grading(joined_video, colored_video, preset_name=sb.get("color_grading_preset", "commercial_punch"))

    # Audio master
    composer.add_audio_and_master(colored_video, args.output, bgm_file=args.bgm)

    print(f"\n========================================================")
    print(f"[CLI] ¡PRODUCCIÓN MULTI-ESCENA COMPLETADA CON ÉXITO!")
    print(f"      Video maestro guardado en: {args.output}")
    print(f"========================================================")

def main():
    parser = argparse.ArgumentParser(description="CLI de producción de video social con Google Veo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: plan
    p_plan = subparsers.add_parser("plan", help="Generar storyboard y plan de retención")
    p_plan.add_argument("--images", nargs="+", required=True, help="Imágenes de entrada")
    p_plan.add_argument("--platform", default="tiktok", help="Plataforma de destino")
    p_plan.add_argument("--topic", default="Promoción de producto", help="Tema o campaña")
    p_plan.add_argument("--motion", help="Preset de movimiento forzado")
    p_plan.add_argument("--no-text-preservation", action="store_true", help="Desactivar preservación de texto")
    p_plan.add_argument("--output", default="storyboard.json", help="Ruta de salida JSON")
    p_plan.set_defaults(func=handle_plan)

    # Subcomando: animate
    p_anim = subparsers.add_parser("animate", help="Animar una imagen preservando texto")
    p_anim.add_argument("--image", required=True, help="Imagen a animar")
    p_anim.add_argument("--platform", default="tiktok", help="Plataforma de destino")
    p_anim.add_argument("--prompt", help="Prompt de cinematografía en inglés")
    p_anim.add_argument("--model", default="veo-3.1-generate-preview", help="Modelo Veo")
    p_anim.add_argument("--duration", type=int, default=6, choices=[4, 6, 8], help="Duración")
    p_anim.add_argument("--no-text-preservation", action="store_true", help="Desactivar aislamiento de texto")
    p_anim.add_argument("--text-animation", default="fade_in", choices=["fade_in", "slide_in_bottom", "pop_in", "static_lock"], help="Animación de texto")
    p_anim.add_argument("--color-preset", default="commercial_punch", help="Preset de color")
    p_anim.add_argument("--bgm", help="Música de fondo opcional")
    p_anim.add_argument("--output", default="animated_video.mp4", help="Video de salida")
    p_anim.set_defaults(func=handle_animate)

    # Subcomando: interpolate
    p_inter = subparsers.add_parser("interpolate", help="Interpolar entre dos imágenes")
    p_inter.add_argument("--first", required=True, help="Imagen de inicio")
    p_inter.add_argument("--last", required=True, help="Imagen final")
    p_inter.add_argument("--prompt", help="Prompt de transición")
    p_inter.add_argument("--model", default="veo-3.1-generate-preview", help="Modelo Veo")
    p_inter.add_argument("--aspect-ratio", default="9:16", help="Aspect ratio")
    p_inter.add_argument("--duration", type=int, default=6, choices=[4, 6, 8], help="Duración")
    p_inter.add_argument("--output", default="interpolated_video.mp4", help="Video de salida")
    p_inter.set_defaults(func=handle_interpolate)

    # Subcomando: produce
    p_prod = subparsers.add_parser("produce", help="Producción completa multi-escena")
    p_prod.add_argument("--storyboard", required=True, help="Ruta al JSON de storyboard")
    p_prod.add_argument("--model", default="veo-3.1-generate-preview", help="Modelo Veo")
    p_prod.add_argument("--transition", default="fade", help="Transición xfade")
    p_prod.add_argument("--bgm", help="Música de fondo")
    p_prod.add_argument("--output", default="final_production.mp4", help="Video final")
    p_prod.set_defaults(func=handle_produce)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
