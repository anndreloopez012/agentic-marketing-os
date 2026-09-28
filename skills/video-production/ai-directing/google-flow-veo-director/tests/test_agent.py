"""Unit tests for the Autonomous Director Agent."""

import unittest
from flow_veo_director.agent import FlowVeoDirectorAgent
from flow_veo_director.validator import ScriptValidator
from flow_veo_director.timing import count_words


class TestDirectorAgent(unittest.TestCase):

    def setUp(self):
        self.agent = FlowVeoDirectorAgent()

    def test_parse_natural_language_flow_sequence(self):
        res = self.agent.parse_natural_language("Quiero un video de 30 segundos sobre una fintech mostrando el SAT FEL")
        self.assertEqual(res["engine"], "flow")
        self.assertEqual(res["duration"], 30)
        self.assertEqual(res["aspect_ratio"], "9:16")  # default

    def test_parse_natural_language_horizontal_and_live_action(self):
        res = self.agent.parse_natural_language("Video horizontal para youtube de 40s en live action con un actor ingeniero")
        self.assertEqual(res["engine"], "flow")
        self.assertEqual(res["duration"], 40)
        self.assertEqual(res["aspect_ratio"], "16:9")
        self.assertEqual(res["render_style"], "cinematic_live_action")

    def test_parse_natural_language_single_shot_veo(self):
        res = self.agent.parse_natural_language("Clip unico de 8 segundos para Veo con un lobo cibernetico")
        self.assertEqual(res["engine"], "veo")
        self.assertLessEqual(res["duration"], 8)
        self.assertIn("Cyber Wolf", res["character"])

    def test_calibrated_voiceover_word_counts(self):
        scripts = self.agent._generate_calibrated_script_blocks("Optimizacion de servidores", 3)
        self.assertEqual(len(scripts), 3)
        for s in scripts:
            wc = count_words(s)
            self.assertGreaterEqual(wc, 21, f"Script too short: {wc} words in '{s}'")
            self.assertLessEqual(wc, 26, f"Script too long: {wc} words in '{s}'")

    def test_create_flow_sequence_handoffs(self):
        params = self.agent.parse_natural_language("Video de 20s de ciberseguridad")
        seq = self.agent.create_flow_sequence(params)
        self.assertEqual(len(seq.shots), 2)
        self.assertEqual(seq.shots[0].take_number, 1)
        self.assertEqual(seq.shots[1].take_number, 2)
        self.assertIn("Último fotograma de Toma 01", seq.shots[1].start_keyframe)

    def test_generate_full_dossier_structure_and_no_emojis(self):
        prompt = "Quiero un video de 30 segundos sobre infraestructura cloud para bancos"
        dossier = self.agent.generate_full_dossier(prompt)
        
        self.assertIn("EXPEDIENTE DE DIRECCIÓN CINEMATOGRÁFICA AUTÓNOMA", dossier)
        self.assertIn("FICHA TÉCNICA DE PRODUCCIÓN", dossier)
        self.assertIn("GUION DE LOCUCIÓN AUDITADO", dossier)
        self.assertIn("KEYFRAME BRIDGE", dossier)
        self.assertIn("NEGATIVE PROMPT ESTANDARIZADO", dossier)
        self.assertIn("GUÍA PRÁCTICA DE OPERACIÓN EN GOOGLE FLOW STUDIO", dossier)
        self.assertIn("CERTIFICADO DE AUDITORÍA AUTOMATIZADA DE CALIDAD", dossier)
        
        # Verify strict zero emojis rule
        emojis = ScriptValidator.check_emojis(dossier)
        self.assertEqual(len(emojis), 0, f"Found emojis in dossier: {emojis}")


if __name__ == "__main__":
    unittest.main()
