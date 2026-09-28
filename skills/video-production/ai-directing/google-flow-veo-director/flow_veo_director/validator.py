"""
Quality linter and structural validator for Google Flow and Veo scripts.
Verifies camera kinematics, word count timing windows, character anchor paths,
and corporate quality rules (such as zero-emoji discipline).
"""

import re
from typing import Dict, List, Any
from flow_veo_director.timing import evaluate_segment_timing, count_words
from flow_veo_director.vocabulary import CAMERA_MOVEMENTS, SHOT_FRAMINGS

# Regex to detect Unicode Emojis
EMOJI_PATTERN = re.compile(
    r"[\U0001F600-\U0001F64F"  # emoticons
    r"\U0001F300-\U0001F5FF"  # symbols & pictographs
    r"\U0001F680-\U0001F6FF"  # transport & map
    r"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    r"\U00002702-\U000027B0"
    r"\U000024C2-\U0001F251"
    r"\U0001F900-\U0001F9FF"  # supplemental symbols
    r"\U0001FA70-\U0001FAFF"
    r"]+", flags=re.UNICODE
)


class ScriptValidator:
    """Validates markdown scripts and prompt sequences for Google Flow & Veo."""

    @staticmethod
    def check_emojis(text: str) -> List[str]:
        """Detects presence of forbidden emojis in corporate text."""
        emojis_found = EMOJI_PATTERN.findall(text)
        if emojis_found:
            return [f"Se detectaron {len(emojis_found)} emojis en el texto: {' '.join(emojis_found)}. Regla corporativa estricta: CERO EMOJIS."]
        return []

    @staticmethod
    def audit_prompt_string(prompt: str) -> Dict[str, Any]:
        """Audits an English cinematic prompt against best-practice keywords."""
        issues = []
        score = 100

        # Check for camera movement mention
        found_camera = any(cam in prompt.lower() for cam in ["dolly", "pan", "tilt", "truck", "pedestal", "crane", "orbit", "static", "tracking"])
        if not found_camera:
            issues.append("El prompt carece de una directiva clara de movimiento de cámara (dolly, pan, orbit, etc.).")
            score -= 20

        # Check for lighting mention
        found_light = any(l in prompt.lower() for l in ["lighting", "light", "god rays", "rim light", "volumetric", "chiaroscuro", "glow", "softbox"])
        if not found_light:
            issues.append("El prompt no especifica perfil de iluminación ni volumetría.")
            score -= 15

        # Check for render style or optics
        found_render = any(r in prompt.lower() for r in ["render", "3d", "8k", "lens", "shading", "subsurface", "octane", "photorealistic", "pixar", "dreamworks"])
        if not found_render:
            issues.append("El prompt no define calidad de render o lente óptica (35mm, 50mm, 3D feature animation).")
            score -= 15

        return {
            "score": max(0, score),
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    @staticmethod
    def audit_markdown_file(file_path: str) -> Dict[str, Any]:
        """Parses a markdown script file and checks all structural guidelines."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"status": "error", "message": f"No se pudo leer el archivo: {str(e)}"}

        emoji_errors = ScriptValidator.check_emojis(content)
        
        # Detect 10s blocks
        shot_matches = list(re.finditer(r"(TOMA\s+\d+|Shot\s+\d+).*?(?=(TOMA\s+\d+|Shot\s+\d+|$))", content, re.DOTALL | re.IGNORECASE))
        
        block_audits = []
        for match in shot_matches:
            shot_text = match.group(0)
            
            # Find dialogue
            dialogue_match = re.search(r'(?:DIÁLOGO|LOCUCIÓN|Voiceover).*?["“]([^"”]+)["”]', shot_text, re.IGNORECASE | re.DOTALL)
            dialogue = dialogue_match.group(1).strip() if dialogue_match else ""
            
            timing_info = evaluate_segment_timing(dialogue, 10.0, "es") if dialogue else None
            
            block_audits.append({
                "block_header": match.group(1),
                "has_dialogue": bool(dialogue),
                "dialogue_words": count_words(dialogue) if dialogue else 0,
                "timing_status": timing_info["status"] if timing_info else "missing",
                "timing_message": timing_info["message"] if timing_info else "No se encontró bloque de diálogo entre comillas."
            })

        return {
            "file_path": file_path,
            "total_shots_found": len(shot_matches),
            "emoji_errors": emoji_errors,
            "blocks": block_audits,
            "passed": len(emoji_errors) == 0 and all(b["timing_status"] == "optimal" for b in block_audits if b["has_dialogue"])
        }
