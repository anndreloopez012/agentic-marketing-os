"""Unit tests for prompt builder."""

import unittest
from flow_veo_director.builder import VeoShotBlueprint


class TestBuilder(unittest.TestCase):

    def test_builder_generate_prompt_text(self):
        bp = VeoShotBlueprint(
            subject="A kinetic cyber fennec fox mascot with amber fur",
            action="taps his glowing cyan HUD visor, expanding a holographic financial dashboard",
            framing="medium_close_up",
            camera_movement="dolly_in",
            lens="prime_50mm",
            lighting="corporate_volumetric",
            render_style="pixar_dreamworks_3d"
        )
        prompt = bp.generate_prompt_text()
        self.assertIn("medium close-up (MCU)", prompt)
        self.assertIn("dolly-in", prompt.lower())
        self.assertIn("HUD visor", prompt)
        self.assertIn("volumetric", prompt.lower())
        self.assertIn("Pixar", prompt)

    def test_builder_format_manifest(self):
        bp = VeoShotBlueprint(
            subject="Cybersecurity engineer",
            action="analyzing firewall incident logs",
            duration_seconds=8,
            fps=24,
            voiceover_script="El tráfico malicioso fue mitigado en milisegundos."
        )
        manifest = bp.format_manifest()
        self.assertIn("GOOGLE VEO CINEMATIC SHOT SPECIFICATION", manifest)
        self.assertTrue("DURACIÓN: 8s" in manifest or "Duración: 8s" in manifest)
        self.assertIn("NEGATIVE PROMPT", manifest)


if __name__ == "__main__":
    unittest.main()
