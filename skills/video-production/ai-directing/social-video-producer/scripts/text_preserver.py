#!/usr/bin/env python3
"""
text_preserver.py
Motor de preservación y composición de textos y logos sin distorsión (Zero AI Hallucination).
Separa las capas tipográficas y de branding de la imagen original, genera un clean plate
para que Google Veo anime el fondo sin interferencias, y recompone el texto original intacto
en alta resolución mediante ffmpeg con efectos cinéticos (fade, slide, pop, static lock).
"""

import argparse
import json
import os
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageFilter, ImageOps, ImageDraw
import numpy as np

class TextPreserver:
    """Aislador y compositor de capas de texto/branding."""

    def __init__(self, platform: str = "tiktok"):
        self.platform = platform
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        self.platforms_cfg = self._load_json(os.path.join(self.config_dir, "platforms.json")).get("platforms", {})
        self.platform_info = self.platforms_cfg.get(platform, self.platforms_cfg.get("tiktok", {}))

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def inspect_safe_zones(self, image_path: str) -> Dict[str, Any]:
        """
        Analiza las dimensiones de la imagen y determina si los elementos
        deben ser ajustados a las zonas seguras de la plataforma.
        """
        with Image.open(image_path) as img:
            w, h = img.size
        
        safe = self.platform_info.get("safe_zones", {})
        top_margin = safe.get("top_margin_px", 160)
        bottom_margin = safe.get("bottom_margin_px", 380)
        left_margin = safe.get("left_margin_px", 60)
        right_margin = safe.get("right_margin_px", 140)

        safe_rect = {
            "x1": left_margin,
            "y1": top_margin,
            "x2": w - right_margin,
            "y2": h - bottom_margin,
            "safe_width": (w - right_margin) - left_margin,
            "safe_height": (h - bottom_margin) - top_margin
        }

        return {
            "image_size": (w, h),
            "platform": self.platform,
            "safe_zone": safe_rect
        }

    def extract_text_layer_by_boxes(
        self,
        image_path: str,
        boxes: List[Tuple[int, int, int, int]],
        output_overlay_path: str = "text_overlay.png",
        output_clean_plate_path: str = "clean_background.png"
    ) -> Tuple[str, str]:
        """
        Extrae regiones delimitadas por cajas [ymin, xmin, ymax, xmax] (coordenadas relativas 0-1000 o píxeles)
        generando:
        1. Una placa alpha PNG transparente de 32 bits con el texto original nítido.
        2. Un clean plate con las zonas de texto rellenadas/suavizadas para animación con Veo.
        """
        with Image.open(image_path).convert("RGBA") as img:
            w, h = img.size
            
            # Crear imagen overlay completamente transparente
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            
            # Crear máscara binaria de las áreas de texto
            mask = Image.new("L", (w, h), 0)
            draw_mask = ImageDraw.Draw(mask)

            for box in boxes:
                y1, x1, y2, x2 = box
                # Si las coordenadas son relativas (0 a 1000 o 0.0 a 1.0)
                if max(y1, x1, y2, x2) <= 1.0:
                    px1 = int(x1 * w)
                    py1 = int(y1 * h)
                    px2 = int(x2 * w)
                    py2 = int(y2 * h)
                elif max(y1, x1, y2, x2) <= 1000:
                    px1 = int((x1 / 1000.0) * w)
                    py1 = int((y1 / 1000.0) * h)
                    px2 = int((x2 / 1000.0) * w)
                    py2 = int((y2 / 1000.0) * h)
                else:
                    px1, py1, px2, py2 = int(x1), int(y1), int(x2), int(y2)

                # Asegurar límites dentro de la imagen
                px1 = max(0, min(px1, w - 1))
                py1 = max(0, min(py1, h - 1))
                px2 = max(0, min(px2, w))
                py2 = max(0, min(py2, h))

                # Copiar píxeles originales exactos al overlay
                crop_region = img.crop((px1, py1, px2, py2))
                overlay.paste(crop_region, (px1, py1))
                
                # Pintar rectángulo en la máscara
                draw_mask.rectangle([px1, py1, px2, py2], fill=255)

            # Guardar capa de texto intacta
            os.makedirs(os.path.dirname(os.path.abspath(output_overlay_path)), exist_ok=True)
            overlay.save(output_overlay_path, "PNG")

            # Crear clean plate: Expandir máscara y rellenar con desenfoque de fondo inteligente
            expanded_mask = mask.filter(ImageFilter.MaxFilter(9))
            blurred_bg = img.filter(ImageFilter.GaussianBlur(15))
            clean_plate = Image.composite(blurred_bg, img, expanded_mask)
            
            clean_plate_rgb = clean_plate.convert("RGB")
            os.makedirs(os.path.dirname(os.path.abspath(output_clean_plate_path)), exist_ok=True)
            clean_plate_rgb.save(output_clean_plate_path, "PNG")

            print(f"[TextPreserver] Capa de texto vectorial/original extraída en: {output_overlay_path}")
            print(f"[TextPreserver] Fondo limpio para animación Veo guardado en: {output_clean_plate_path}")

            return output_overlay_path, output_clean_plate_path

    def auto_isolate_graphic_layer(
        self,
        image_path: str,
        output_overlay_path: str = "text_overlay.png",
        output_clean_plate_path: str = "clean_background.png",
        text_threshold: int = 40
    ) -> Tuple[str, str]:
        """
        Modo de aislamiento inteligente automático cuando no se especifican cajas manuales.
        Detecta zonas de alto contraste y bordes nítidos típicos de tipografía y logos.
        """
        with Image.open(image_path).convert("RGBA") as img:
            w, h = img.size
            gray = img.convert("L")
            
            # Detección de bordes y gradientes
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edges_np = np.array(edges)
            
            # Zonas con alta densidad de bordes (característico de texto y vectores)
            binary_mask = (edges_np > text_threshold).astype(np.uint8) * 255
            mask_img = Image.fromarray(binary_mask).filter(ImageFilter.MaxFilter(5))
            
            # Extraer capa overlay
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            overlay.paste(img, (0, 0), mask_img)
            
            os.makedirs(os.path.dirname(os.path.abspath(output_overlay_path)), exist_ok=True)
            overlay.save(output_overlay_path, "PNG")

            # Inpaint sutil en clean plate
            dilated = mask_img.filter(ImageFilter.MaxFilter(9))
            blurred_bg = img.filter(ImageFilter.GaussianBlur(12))
            clean_plate = Image.composite(blurred_bg, img, dilated).convert("RGB")
            
            os.makedirs(os.path.dirname(os.path.abspath(output_clean_plate_path)), exist_ok=True)
            clean_plate.save(output_clean_plate_path, "PNG")

            return output_overlay_path, output_clean_plate_path

    def generate_ffmpeg_overlay_filter(
        self,
        animation_style: str = "fade_in",
        start_time: float = 0.5,
        fade_duration: float = 0.8,
        total_duration: float = 6.0
    ) -> str:
        """
        Construye el filtro complejo ffmpeg para superponer la capa de texto
        sobre el video generado por Veo con movimiento fluido.
        """
        if animation_style == "fade_in":
            # Transparencia gradual suave
            filtergraph = (
                f"[1:v]format=rgba,colorchannelmixer=aa=0[ov_zero];"
                f"[1:v]format=rgba,fade=t=in:st={start_time}:d={fade_duration}:alpha=1[ov_faded];"
                f"[0:v][ov_faded]overlay=0:0:enable='gte(t,{start_time})'"
            )
            return filtergraph

        elif animation_style == "slide_in_bottom":
            # Entrada cinética desde abajo hacia su posición exacta
            filtergraph = (
                f"[1:v]format=rgba[ov];"
                f"[0:v][ov]overlay=0:'if(lt(t,{start_time}),H,max(0,H-(H*(t-{start_time})/{fade_duration})))':enable='gte(t,{start_time})'"
            )
            return filtergraph

        elif animation_style == "pop_in":
            # Entrada con ligero rebote o fade rápido
            filtergraph = (
                f"[1:v]format=rgba,fade=t=in:st={start_time}:d=0.3:alpha=1[ov_pop];"
                f"[0:v][ov_pop]overlay=0:0:enable='gte(t,{start_time})'"
            )
            return filtergraph

        else: # static_lock
            # Texto estático fijado con 100% de nitidez sobre el video móvil
            return "[0:v][1:v]overlay=0:0"

def main():
    parser = argparse.ArgumentParser(description="Aislador y preservador de textos para video marketing")
    parser.add_argument("--image", required=True, help="Ruta a la imagen con texto/logos")
    parser.add_argument("--platform", default="tiktok", choices=["tiktok", "instagram_reels", "youtube_shorts", "instagram_feed_square", "linkedin_feed"], help="Plataforma de destino")
    parser.add_argument("--boxes", help="JSON con cajas de texto [[ymin, xmin, ymax, xmax], ...]")
    parser.add_argument("--output-overlay", default="text_overlay.png", help="Archivo PNG con texto transparente")
    parser.add_argument("--output-clean-plate", default="clean_background.png", help="Archivo PNG con fondo limpio para Veo")
    parser.add_argument("--animation", default="fade_in", choices=["fade_in", "slide_in_bottom", "pop_in", "static_lock"], help="Estilo de animación de entrada del texto")
    args = parser.parse_args()

    preserver = TextPreserver(platform=args.platform)
    
    # Reportar zonas seguras
    safe_info = preserver.inspect_safe_zones(args.image)
    print(f"\n[TextPreserver] Inspección de Safe Zones para {args.platform}:")
    print(f"                Dimensiones imagen: {safe_info['image_size']}")
    print(f"                Zona segura útil: {safe_info['safe_zone']}")

    if args.boxes:
        boxes_list = json.loads(args.boxes)
        preserver.extract_text_layer_by_boxes(
            args.image,
            boxes_list,
            output_overlay_path=args.output_overlay,
            output_clean_plate_path=args.output_clean_plate
        )
    else:
        preserver.auto_isolate_graphic_layer(
            args.image,
            output_overlay_path=args.output_overlay,
            output_clean_plate_path=args.output_clean_plate
        )

    filt = preserver.generate_ffmpeg_overlay_filter(animation_style=args.animation)
    print(f"[TextPreserver] Filtro ffmpeg generado para animación '{args.animation}':\n{filt}")

if __name__ == "__main__":
    main()
