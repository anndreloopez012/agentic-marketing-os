"""Unit tests for timing and speech cadence."""

import unittest
from flow_veo_director.timing import (
    count_words,
    get_target_word_range,
    estimate_spoken_duration,
    evaluate_segment_timing
)


class TestTiming(unittest.TestCase):

    def test_count_words(self):
        text = "Hola mundo corporativo en la nube de alta fidelidad."
        self.assertEqual(count_words(text), 9)
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("   Palabra   con   espacios   "), 3)

    def test_target_word_range(self):
        min_w, max_w = get_target_word_range(10.0, "es")
        self.assertEqual(min_w, 21)
        self.assertEqual(max_w, 26)

    def test_evaluate_segment_timing_optimal(self):
        # 23 words in Spanish
        text = (
            "La optimización en tiempo real de tu base de datos garantiza latencia mínima "
            "y máxima rentabilidad financiera para todas tus sucursales en producción."
        )
        self.assertEqual(count_words(text), 23)
        res = evaluate_segment_timing(text, 10.0, "es")
        self.assertEqual(res["status"], "optimal")

    def test_evaluate_segment_timing_too_fast(self):
        # Over 26 words
        text = (
            "Uno dos tres cuatro cinco seis siete ocho nueve diez "
            "once doce trece catorce quince dieciséis diecisiete dieciocho diecinueve veinte "
            "veintiuno veintidós veintitrés veinticuatro veinticinco veintiséis veintisiete veintiocho."
        )
        res = evaluate_segment_timing(text, 10.0, "es")
        self.assertEqual(res["status"], "too_fast")

    def test_evaluate_segment_timing_too_slow(self):
        text = "Hola a todos."
        res = evaluate_segment_timing(text, 10.0, "es")
        self.assertEqual(res["status"], "too_slow")


if __name__ == "__main__":
    unittest.main()
