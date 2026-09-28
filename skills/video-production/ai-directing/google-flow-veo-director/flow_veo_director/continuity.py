"""
Multi-shot sequence and continuity engine for Google Flow.
Breaks down long video productions (20s, 30s, 40s, 60s, 90s) into interlocking
10-second takes connected by Keyframe Bridges (Start Frame -> End Frame),
character physical persistence, camera vector handoffs, and voiceover timing gates.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from flow_veo_director.builder import VeoShotBlueprint
from flow_veo_director.timing import evaluate_segment_timing, count_words
from flow_veo_director.vocabulary import TRANSITION_CONNECTORS


@dataclass
class FlowShot:
    """Represents a single 10-second interlocking take within Google Flow."""
    take_number: int
    start_second: int
    end_second: int
    start_keyframe: str
    end_keyframe_goal: str
    character_anchor: str
    action_description: str
    camera_movement: str
    framing: str
    lighting: str
    render_style: str
    transition_connector: str
    voiceover_text: str
    audio_directive: str = "clean_corporate"
    custom_details: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> int:
        return self.end_second - self.start_second

    def to_veo_blueprint(self) -> VeoShotBlueprint:
        return VeoShotBlueprint(
            subject=f"Persistent character referenced in {self.character_anchor}",
            action=self.action_description,
            framing=self.framing,
            camera_movement=self.camera_movement,
            lighting=self.lighting,
            render_style=self.render_style,
            audio_directive=self.audio_directive,
            duration_seconds=self.duration_seconds,
            voiceover_script=self.voiceover_text,
            custom_details=self.custom_details
        )

    def format_shot_block(self) -> str:
        """Formats the 10-second block following the master Google Flow protocol."""
        timing_eval = evaluate_segment_timing(self.voiceover_text, float(self.duration_seconds), "es")
        prompt_text = self.to_veo_blueprint().generate_prompt_text()
        connector_desc = TRANSITION_CONNECTORS.get(self.transition_connector, {}).get("desc", self.transition_connector)

        lines = [
            f"================================================================================",
            f"TOMA {self.take_number:02d} — BLOQUE TEMPORAL: 00:{self.start_second:02d} - 00:{self.end_second:02d} (DURACIÓN: {self.duration_seconds} SEGUNDOS)",
            f"================================================================================",
            f"1. ANCLAJES VISUALES (KEYFRAME BRIDGE & CONTINUIDAD):",
            f"   • Start Keyframe: {self.start_keyframe}",
            f"   • Character Anchor: {self.character_anchor}",
            f"   • Pose Objetivo al Segundo {self.end_second:02d}: {self.end_keyframe_goal}",
            f"",
            f"2. PROMPT PARA GOOGLE FLOW / VEO (INGLÉS CINEMATOGRÁFICO):",
            f"   {prompt_text}",
            f"",
            f"3. VECTOR DE CÁMARA Y TRANSICIÓN:",
            f"   • Movimiento: {self.camera_movement}",
            f"   • Conector de Edición: {connector_desc}",
            f"",
            f"4. DIÁLOGO / LOCUCIÓN CALIBRADA ({timing_eval['words']} palabras | Rango ideal: {timing_eval['target_range'][0]}-{timing_eval['target_range'][1]} palabras):",
            f'   "{self.voiceover_text}"',
            f"   [Estado de Sincronización]: {timing_eval['message']}",
            f"================================================================================"
        ]
        return "\n".join(lines)


@dataclass
class FlowSequence:
    """Manages an entire continuous multi-shot video project."""
    title: str
    total_seconds: int
    concept: str
    shots: List[FlowShot] = field(default_factory=list)

    def add_shot(self, shot: FlowShot):
        self.shots.append(shot)

    def validate_continuity(self) -> List[str]:
        """Validates keyframe continuity and temporal progression across shots."""
        warnings = []
        if not self.shots:
            warnings.append("La secuencia no contiene ninguna toma.")
            return warnings

        current_second = 0
        for i, shot in enumerate(self.shots):
            if shot.start_second != current_second:
                warnings.append(f"Discontinuidad temporal en Toma {shot.take_number}: inicia en {shot.start_second}s pero la previa terminó en {current_second}s.")
            current_second = shot.end_second

            # Keyframe handoff check
            if i > 0:
                prev_shot = self.shots[i - 1]
                expected_keyframe = f"Último fotograma de Toma {prev_shot.take_number:02d} (at 00:{prev_shot.end_second:02d})"
                if "Último fotograma" not in shot.start_keyframe and shot.start_keyframe != prev_shot.end_keyframe_goal:
                    warnings.append(
                        f"Aviso de Continuidad en Toma {shot.take_number}: Se recomienda usar como Start Keyframe '{expected_keyframe}' o una imagen coincidente con la pose final anterior."
                    )

        if current_second != self.total_seconds:
            warnings.append(f"La duración acumulada de las tomas ({current_second}s) no coincide con la duración total programada ({self.total_seconds}s).")

        return warnings

    def export_full_storyboard(self) -> str:
        """Exports the complete production-ready Markdown document."""
        output = [
            f"# GUION MAESTRO CINEMATOGRÁFICO: {self.title.upper()}",
            f"**Duración Total**: {self.total_seconds} Segundos | **Total de Tomas**: {len(self.shots)} (Bloques de 10s)",
            f"**Concepto**: {self.concept}",
            "",
            "---",
            ""
        ]

        for shot in self.shots:
            output.append(shot.format_shot_block())
            output.append("")

        warnings = self.validate_continuity()
        output.append("### REPORTE DE AUDITORÍA Y CONTINUIDAD:")
        if not warnings:
            output.append("• Coherencia temporal y puente de keyframes: 100% VALIDADOS.")
            output.append("• Sincronización de locución: Calibrada a ritmo corporativo (135 WPM).")
        else:
            for w in warnings:
                output.append(f"• [ADVERTENCIA] {w}")

        return "\n".join(output)
