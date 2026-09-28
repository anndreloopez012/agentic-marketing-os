"""Unit tests for script validator and emoji checker."""

import unittest
from flow_veo_director.validator import ScriptValidator


class TestValidator(unittest.TestCase):

    def test_emoji_detection(self):
        clean_text = "Este es un texto corporativo sin emojis y con rigor técnico."
        self.assertEqual(len(ScriptValidator.check_emojis(clean_text)), 0)

        emoji_text = "Este texto tiene un cohete 🚀 y fuego 🔥."
        self.assertGreater(len(ScriptValidator.check_emojis(emoji_text)), 0)

    def test_prompt_auditor(self):
        good_prompt = (
            "Medium close-up shot, 50mm lens. Slow smooth dolly-in towards subject. "
            "A senior cloud architect analyzes server logs. Volumetric studio lighting with cyan fill. "
            "Pixar and DreamWorks 3D feature animation render."
        )
        res = ScriptValidator.audit_prompt_string(good_prompt)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["score"], 100)

        bad_prompt = "A cat sitting on a chair."
        res_bad = ScriptValidator.audit_prompt_string(bad_prompt)
        self.assertFalse(res_bad["is_valid"])
        self.assertLess(res_bad["score"], 100)


if __name__ == "__main__":
    unittest.main()
