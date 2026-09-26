#!/usr/bin/env python3
"""
storyboard_planner.py
Planificador cinematográfico y narrativo para videos de alto impacto en redes sociales.
Convierte una o múltiples imágenes en una estructura secuencial con gancho (Hook),
desarrollo de valor (Core) y llamada a la acción (CTA), respetando zonas seguras y
asignando movimientos de cámara controlados para Google Veo.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, List, Optional
from PIL import Image

class StoryboardPlanner:
    """Planificador de guiones y secuencias para video marketing."""

    def __init__(self, platform: str = "tiktok"):
        self.platform = platform
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        self.platforms_cfg = self._load_json(os.path.join(self.config_dir, "platforms.json")).get("platforms", {})
        self.motion_cfg = self._load_json(os.path.join(self.config_dir, "motion_presets.json"))
        
        self.platform_info = self.platforms_cfg.get(platform, self.platforms_cfg.get("tiktok", {}))
        self.motion_presets = self.motion_cfg.get("motion_presets", {})
        self.negative_prompts = self.motion_cfg.get("negative_prompts", [""])[0]

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def plan_sequence(
        self,
        image_paths: List[str],
        topic_or_brand: str = "Brand Promotion",
        voiceover_script: Optional[List[str]] = None,
        preferred_motion: Optional[str] = None,
        has_critical_text: bool = True
    ) -> Dict[str, Any]:
        """
        Crea un plan de producción (storyboard) completo optimizado para retención viral.
        
        Args:
            image_paths: Lista de rutas a las imágenes de entrada.
            topic_or_brand: Descripción del producto, campaña o tema.
            voiceover_script: Lista de textos para locución por escena (opcional).
            preferred_motion: Preset de movimiento preferido (opcional).
            has_critical_text: Si es True, activa el modo de preservación de capas de texto.
        """
        if not image_paths:
            raise ValueError("Se requiere al menos una imagen para planificar el storyboard.")

        num_images = len(image_paths)
        scenes: List[Dict[str, Any]] = []

        # Secuencia inteligente de movimientos de cámara para dinamismo
        motion_sequence = [
            "subtle_dolly_in",    # Escena 1: Hook frontal de impacto
            "cinematic_orbit",    # Escena 2: Giro tridimensional
            "horizontal_truck",   # Escena 3: Parallax lateral
            "pedestal_reveal",    # Escena 4: Revelación vertical
            "ambient_light_sweep" # Escena 5 / Final: Cierre elegante estático con luz
        ]

        # Transiciones profesionales disponibles en ffmpeg xfade
        transition_sequence = ["fade", "wipeleft", "slideup", "circlecrop", "dissolve"]

        current_timestamp = 0.0

        for i, img_path in enumerate(image_paths):
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"No existe el archivo de imagen: {img_path}")

            with Image.open(img_path) as im:
                img_w, img_h = im.size

            # Determinar rol de la escena
            if i == 0:
                scene_role = "HOOK (Primeros 2 segundos para capturar atención)"
                motion_key = preferred_motion or "subtle_dolly_in"
                duration = 4
            elif i == num_images - 1 and num_images > 1:
                scene_role = "CTA (Cierre con llamado a la acción y logotipo)"
                motion_key = "ambient_light_sweep"
                duration = 4
            else:
                scene_role = f"VALUE PUNCH {i} (Beneficio o detalle visual)"
                motion_key = motion_sequence[i % len(motion_sequence)]
                duration = 4

            preset_info = self.motion_presets.get(motion_key, self.motion_presets.get("subtle_dolly_in", {}))
            prompt_fragment = preset_info.get("prompt_fragment", "")

            # Construir prompt cinematográfico completo para Veo
            cinematic_prompt = (
                f"{topic_or_brand}. {prompt_fragment} "
                f"Commercial high-end production quality, 8k textures, crisp lighting. "
                f"Avoid: {self.negative_prompts}"
            )

            # Transición hacia la siguiente escena
            transition = transition_sequence[i % len(transition_sequence)] if i < num_images - 1 else "none"
            trans_duration = 0.5 if transition != "none" else 0.0

            scene_script = voiceover_script[i] if voiceover_script and i < len(voiceover_script) else ""

            scene_entry = {
                "scene_index": i + 1,
                "role": scene_role,
                "source_image": img_path,
                "dimensions": {"width": img_w, "height": img_h},
                "duration_seconds": duration,
                "start_time_seconds": round(current_timestamp, 2),
                "end_time_seconds": round(current_timestamp + duration, 2),
                "motion_preset": motion_key,
                "prompt_veo": cinematic_prompt,
                "text_mode": "preserve_lossless_overlay" if has_critical_text else "native_veo_render",
                "transition_to_next": transition,
                "transition_duration": trans_duration,
                "voiceover_text": scene_script,
                "sfx_cue": "whoosh" if transition != "none" else "none"
            }
            scenes.append(scene_entry)
            current_timestamp += (duration - trans_duration)

        total_duration = round(current_timestamp, 2)

        storyboard = {
            "project_name": f"Video_{topic_or_brand.replace(' ', '_')[:25]}",
            "platform": self.platform,
            "platform_specs": self.platform_info,
            "total_scenes": num_images,
            "estimated_duration_seconds": total_duration,
            "safe_zones_active": True,
            "color_grading_preset": "commercial_punch",
            "audio_strategy": {
                "background_music": True,
                "auto_ducking": bool(voiceover_script),
                "ducking_attenuation_db": -14.0,
                "target_lufs": self.platform_info.get("target_audio_lufs", -14.0)
            },
            "scenes": scenes
        }

        return storyboard

def main():
    parser = argparse.ArgumentParser(description="Generador de Storyboards para video marketing")
    parser.add_argument("--images", nargs="+", required=True, help="Lista de imágenes ordenadas para el video")
    parser.add_argument("--platform", default="tiktok", choices=["tiktok", "instagram_reels", "youtube_shorts", "instagram_feed_square", "linkedin_feed", "youtube_landscape"], help="Plataforma social")
    parser.add_argument("--topic", default="Campaña corporativa", help="Tema o marca")
    parser.add_argument("--motion", choices=["subtle_dolly_in", "cinematic_orbit", "pedestal_reveal", "horizontal_truck", "ambient_light_sweep", "floating_macro"], help="Preset de movimiento forzado")
    parser.add_argument("--preserve-text", action="store_true", default=True, help="Activar preservación estricta de textos")
    parser.add_argument("--output-json", default="storyboard.json", help="Ruta de salida del JSON de planificación")
    args = parser.parse_args()

    planner = StoryboardPlanner(platform=args.platform)
    storyboard = planner.plan_sequence(
        image_paths=args.images,
        topic_or_brand=args.topic,
        preferred_motion=args.motion,
        has_critical_text=args.preserve_text
    )

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)

    print(f"\n[StoryboardPlanner] ¡Planificación completada con éxito!")
    print(f"                     Plataforma: {args.platform}")
    print(f"                     Escenas planificadas: {storyboard['total_scenes']}")
    print(f"                     Duración estimada: {storyboard['estimated_duration_seconds']}s")
    print(f"                     Archivo guardado en: {args.output_json}")

if __name__ == "__main__":
    main()
