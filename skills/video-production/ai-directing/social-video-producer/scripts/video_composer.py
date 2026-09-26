#!/usr/bin/env python3
"""
video_composer.py
Motor de postproducción profesional basado en ffmpeg.
Ensambla secuencias de video, aplica transiciones cinematográficas (xfade),
superpone capas gráficas de alta resolución sin distorsión, mezcla audio
con ducking inteligente y normalización a -14 LUFS, aplica gradación de color
y quema subtítulos animados para redes sociales.
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Any, List, Optional

class VideoComposer:
    """Compositor de video para acabados profesionales de estudio."""

    def __init__(self, platform: str = "tiktok"):
        self.platform = platform
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        self.platforms_cfg = self._load_json(os.path.join(self.config_dir, "platforms.json")).get("platforms", {})
        self.luts_cfg = self._load_json(os.path.join(self.config_dir, "color_luts.json")).get("color_presets", {})
        self.platform_info = self.platforms_cfg.get(platform, self.platforms_cfg.get("tiktok", {}))

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_video_duration(self, video_path: str) -> float:
        """Obtiene la duración exacta de un video usando ffprobe."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())

    def conform_aspect_ratio(
        self,
        input_file: str,
        output_file: str,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        fps: int = 30
    ) -> str:
        """
        Adapta cualquier video o imagen a la resolución exacta de la plataforma
        utilizando fondo difuminado (blurred pillarbox/letterbox) sin deformar el contenido.
        """
        tw = target_width or self.platform_info.get("width", 1080)
        th = target_height or self.platform_info.get("height", 1920)

        # Filtro de escalado proporcional con fondo desenfocado
        filtergraph = (
            f"[0:v]scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},boxblur=25:5[bg];"
            f"[0:v]scale={tw}:{th}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[outv]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", input_file,
            "-filter_complex", filtergraph,
            "-map", "[outv]",
            "-r", str(fps),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_file
        ]
        print(f"[VideoComposer] Adaptando relación de aspecto a {tw}x{th}...")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file

    def overlay_lossless_plate(
        self,
        video_file: str,
        overlay_png: str,
        output_file: str,
        animation: str = "fade_in",
        start_time: float = 0.5,
        fade_duration: float = 0.6
    ) -> str:
        """
        Superpone una capa PNG transparente de texto/logos con animación fluida
        garantizando cero distorsión sobre el video de fondo.
        """
        if animation == "fade_in":
            filtergraph = (
                f"[1:v]format=rgba,fade=t=in:st={start_time}:d={fade_duration}:alpha=1[ov];"
                f"[0:v][ov]overlay=0:0:enable='gte(t,{start_time})'[outv]"
            )
        elif animation == "slide_in_bottom":
            filtergraph = (
                f"[1:v]format=rgba[ov];"
                f"[0:v][ov]overlay=0:'if(lt(t,{start_time}),H,max(0,H-(H*(t-{start_time})/{fade_duration})))':enable='gte(t,{start_time})'[outv]"
            )
        else: # static_lock
            filtergraph = "[0:v][1:v]overlay=0:0[outv]"

        cmd = [
            "ffmpeg", "-y",
            "-i", video_file,
            "-i", overlay_png,
            "-filter_complex", filtergraph,
            "-map", "[outv]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_file
        ]
        print(f"[VideoComposer] Superponiendo capa tipográfica lossless con animación '{animation}'...")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file

    def concatenate_with_transitions(
        self,
        video_files: List[str],
        output_file: str,
        transition: str = "fade",
        transition_duration: float = 0.5
    ) -> str:
        """
        Une múltiples clips de video aplicando transiciones cinematográficas xfade.
        """
        if not video_files:
            raise ValueError("Se requiere al menos un archivo de video.")
        if len(video_files) == 1:
            # Solo un clip, copiar directamente
            subprocess.run(["ffmpeg", "-y", "-i", video_files[0], "-c", "copy", output_file], check=True, capture_output=True)
            return output_file

        durations = [self.get_video_duration(v) for v in video_files]
        inputs = []
        for v in video_files:
            inputs.extend(["-i", v])

        # Construir grafo xfade secuencial
        filter_parts = []
        last_out = "0:v"
        current_offset = durations[0] - transition_duration

        for i in range(1, len(video_files)):
            next_in = f"{i}:v"
            out_label = f"v_trans_{i}"
            part = (
                f"[{last_out}][{next_in}]xfade="
                f"transition={transition}:duration={transition_duration}:offset={current_offset:.2f}[{out_label}]"
            )
            filter_parts.append(part)
            last_out = out_label
            if i < len(video_files) - 1:
                current_offset += durations[i] - transition_duration

        filter_complex_str = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex_str,
            "-map", f"[{last_out}]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_file
        ]
        print(f"[VideoComposer] Concatenando {len(video_files)} clips con transición '{transition}'...")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file

    def apply_color_grading(
        self,
        video_file: str,
        output_file: str,
        preset_name: str = "commercial_punch"
    ) -> str:
        """Aplica gradación de color profesional para pantallas móviles."""
        preset = self.luts_cfg.get(preset_name, self.luts_cfg.get("commercial_punch", {}))
        filter_str = preset.get("ffmpeg_filter", "null")

        if filter_str == "null":
            subprocess.run(["ffmpeg", "-y", "-i", video_file, "-c", "copy", output_file], check=True, capture_output=True)
            return output_file

        cmd = [
            "ffmpeg", "-y",
            "-i", video_file,
            "-vf", filter_str,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_file
        ]
        print(f"[VideoComposer] Aplicando gradación de color '{preset_name}'...")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file

    def add_audio_and_master(
        self,
        video_file: str,
        output_file: str,
        bgm_file: Optional[str] = None,
        voiceover_file: Optional[str] = None,
        bgm_volume: float = 0.25,
        fade_out_seconds: float = 1.5
    ) -> str:
        """
        Mezcla música de fondo, voz con ducking y normalización a -14 LUFS para redes sociales.
        """
        vid_duration = self.get_video_duration(video_file)

        if not bgm_file and not voiceover_file:
            # Si no hay audio, generar un track estéreo silencioso para que la plataforma lo acepte
            cmd = [
                "ffmpeg", "-y",
                "-i", video_file,
                "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=44100",
                "-t", str(vid_duration),
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_file
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_file

        fade_start = max(0.0, vid_duration - fade_out_seconds)

        if bgm_file and voiceover_file:
            # Ducking de música cuando la voz habla
            filtergraph = (
                f"[1:a]volume={bgm_volume},afade=t=out:st={fade_start}:d={fade_out_seconds}[bgm];"
                f"[2:a]volume=1.0[vox];"
                f"[bgm][vox]sidechaincompress=threshold=0.1:ratio=4:attack=20:release=300[ducked_bgm];"
                f"[ducked_bgm][vox]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=11:TP=-1.5[outa]"
            )
            cmd = [
                "ffmpeg", "-y",
                "-i", video_file,
                "-stream_loop", "-1", "-i", bgm_file,
                "-i", voiceover_file,
                "-filter_complex", filtergraph,
                "-map", "0:v",
                "-map", "[outa]",
                "-t", str(vid_duration),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                output_file
            ]
        elif bgm_file:
            # Solo música de fondo
            filtergraph = (
                f"[1:a]volume={bgm_volume},afade=t=out:st={fade_start}:d={fade_out_seconds},"
                f"loudnorm=I=-14:LRA=11:TP=-1.5[outa]"
            )
            cmd = [
                "ffmpeg", "-y",
                "-i", video_file,
                "-stream_loop", "-1", "-i", bgm_file,
                "-filter_complex", filtergraph,
                "-map", "0:v",
                "-map", "[outa]",
                "-t", str(vid_duration),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                output_file
            ]
        else:
            # Solo voz
            filtergraph = "[1:a]volume=1.0,loudnorm=I=-14:LRA=11:TP=-1.5[outa]"
            cmd = [
                "ffmpeg", "-y",
                "-i", video_file,
                "-i", voiceover_file,
                "-filter_complex", filtergraph,
                "-map", "0:v",
                "-map", "[outa]",
                "-t", str(vid_duration),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                output_file
            ]

        print(f"[VideoComposer] Masterizando audio (BGM, Ducking, Loudnorm a -14 LUFS)...")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file

    def burn_subtitles(
        self,
        video_file: str,
        subtitles_file: str,
        output_file: str
    ) -> str:
        """Quema subtítulos modernos ASS/SRT sobre el video respetando safe zones."""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_file,
            "-vf", f"subtitles={subtitles_file}",
            "-c:v", "libx264",
            "-c:a", "copy",
            output_file
        ]
        print(f"[VideoComposer] Quemando subtítulos desde {subtitles_file}...")
        subprocess.run(cmd, check=True, capture_output=True)
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Compositor de video para redes sociales")
    parser.add_argument("--videos", nargs="+", required=True, help="Videos de entrada a procesar o unir")
    parser.add_argument("--platform", default="tiktok", help="Plataforma de destino")
    parser.add_argument("--transition", default="fade", help="Tipo de transición xfade")
    parser.add_argument("--overlay", help="Capa PNG con texto o logo")
    parser.add_argument("--bgm", help="Archivo de audio para música de fondo")
    parser.add_argument("--voiceover", help="Archivo de audio para locución")
    parser.add_argument("--color-preset", default="commercial_punch", help="Preset de gradación de color")
    parser.add_argument("--subtitles", help="Archivo de subtítulos .ass o .srt")
    parser.add_argument("--output", default="final_social_video.mp4", help="Video renderizado final")
    args = parser.parse_args()

    composer = VideoComposer(platform=args.platform)

    # 1. Unir videos si hay más de uno
    intermediate_1 = "temp_joined.mp4"
    if len(args.videos) > 1:
        composer.concatenate_with_transitions(args.videos, intermediate_1, transition=args.transition)
    else:
        intermediate_1 = args.videos[0]

    current_stage = intermediate_1

    # 2. Superponer texto/branding si se especifica
    if args.overlay:
        intermediate_2 = "temp_overlayed.mp4"
        composer.overlay_lossless_plate(current_stage, args.overlay, intermediate_2)
        current_stage = intermediate_2

    # 3. Gradación de color
    if args.color_preset and args.color_preset != "none":
        intermediate_3 = "temp_colored.mp4"
        composer.apply_color_grading(current_stage, intermediate_3, preset_name=args.color_preset)
        current_stage = intermediate_3

    # 4. Audio mastering
    intermediate_4 = "temp_audio.mp4"
    composer.add_audio_and_master(current_stage, intermediate_4, bgm_file=args.bgm, voiceover_file=args.voiceover)
    current_stage = intermediate_4

    # 5. Subtítulos si existen
    if args.subtitles:
        composer.burn_subtitles(current_stage, args.subtitles, args.output)
    else:
        # Copiar al output final
        subprocess.run(["ffmpeg", "-y", "-i", current_stage, "-c", "copy", args.output], check=True, capture_output=True)

    # Limpiar temporales
    for temp in ["temp_joined.mp4", "temp_overlayed.mp4", "temp_colored.mp4", "temp_audio.mp4"]:
        if os.path.exists(temp) and temp != args.output:
            try:
                os.remove(temp)
            except Exception:
                pass

    print(f"\n[VideoComposer] ¡Video final generado con éxito en: {args.output}!")

if __name__ == "__main__":
    main()
