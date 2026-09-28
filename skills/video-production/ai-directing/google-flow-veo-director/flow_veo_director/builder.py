"""
Prompt Builder for Google Veo and Google Flow.
Constructs layered, director-grade cinematic blueprints combining optics,
camera motion vectors, physical action, volumetric illumination, shaders,
and native audio directives.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from flow_veo_director.vocabulary import (
    CAMERA_MOVEMENTS,
    SHOT_FRAMINGS,
    OPTICS_AND_LENSES,
    LIGHTING_PROFILES,
    RENDER_STYLES,
    NATIVE_AUDIO_DIRECTIVES
)

STANDARD_NEGATIVE_PROMPT = (
    "blurry, morphing artifacts, extra limbs, deformed fingers, plastic artificial skin, "
    "low resolution, jittery camera, distorted typography, flickering lighting, disjointed motion, "
    "unstable geometry, amateur color grading, washed out shadows"
)


@dataclass
class VeoShotBlueprint:
    """Represents the complete configuration of a single cinematic shot."""
    subject: str
    action: str
    framing: str = "medium_close_up"
    camera_movement: str = "dolly_in"
    lens: str = "prime_50mm"
    lighting: str = "corporate_volumetric"
    render_style: str = "pixar_dreamworks_3d"
    audio_directive: Optional[str] = "clean_corporate"
    aspect_ratio: str = "9:16"
    duration_seconds: int = 8
    fps: int = 24
    character_anchor_path: Optional[str] = None
    voiceover_script: Optional[str] = None
    custom_details: List[str] = field(default_factory=list)

    def generate_prompt_text(self) -> str:
        """
        Assembles the rigorous 7-layer directorial prompt in cinematographic English.
        """
        # 1. Framing
        framing_info = SHOT_FRAMINGS.get(self.framing, {}).get("en", self.framing)
        
        # 2. Optics
        lens_info = OPTICS_AND_LENSES.get(self.lens, self.lens)
        
        # 3. Camera motion
        camera_info = CAMERA_MOVEMENTS.get(self.camera_movement, {}).get("en", self.camera_movement)
        
        # 4. Lighting
        lighting_info = LIGHTING_PROFILES.get(self.lighting, {}).get("en", self.lighting)
        
        # 5. Render
        render_info = RENDER_STYLES.get(self.render_style, self.render_style)
        
        # 6. Audio
        audio_info = ""
        if self.audio_directive:
            audio_text = NATIVE_AUDIO_DIRECTIVES.get(self.audio_directive, self.audio_directive)
            audio_info = f" Native audio: {audio_text}."

        custom_str = ""
        if self.custom_details:
            custom_str = " " + " ".join(self.custom_details)

        prompt = (
            f"{framing_info}, {lens_info}. {camera_info.capitalize()}. "
            f"{self.subject}. {self.action}.{custom_str} "
            f"{lighting_info.capitalize()}. {render_info}.{audio_info}"
        )
        return prompt.strip()

    def format_manifest(self) -> str:
        """Generates the standardized Markdown manifest for production."""
        prompt_text = self.generate_prompt_text()
        char_anchor = self.character_anchor_path or "[None / Generated from text]"
        vo_script = self.voiceover_script or "[No voiceover specified]"

        manifest = [
            "```text",
            "================================================================================",
            f"GOOGLE VEO CINEMATIC SHOT SPECIFICATION (DURACIÓN: {self.duration_seconds}s | {self.fps}fps)",
            "================================================================================",
            f"Aspect Ratio: {self.aspect_ratio} | Duration: {self.duration_seconds}s | FPS: {self.fps}fps",
            f"Character Seed / Anchor: {char_anchor}",
            f"Framing & Optics: {self.framing} ({self.lens})",
            f"Camera Movement Vector: {self.camera_movement}",
            f"Lighting Atmosphere: {self.lighting}",
            f"Render Aesthetics: {self.render_style}",
            "",
            "[VEO MASTER PROMPT (ENGLISH CINEMATOGRAPHY)]:",
            prompt_text,
            "",
            "[NEGATIVE PROMPT]:",
            STANDARD_NEGATIVE_PROMPT,
            "",
            "[VOICEOVER / GUION DE LOCUCIÓN]:",
            f'"{vo_script}"',
            "================================================================================",
            "```"
        ]
        return "\n".join(manifest)
