"""
Voiceover and temporal synchronization engine for video generation.
Calculates speech cadence, word limits per segment, and ensures voiceover
aligns precisely with Google Flow 10-second takes.
"""

import re
from typing import Dict, Tuple

WPM_STANDARDS = {
    "es": {
        "wpm": 135,
        "desc": "Español corporativo formal (articulación clara, pausas naturales)",
        "min_ratio": 2.1,
        "max_ratio": 2.6
    },
    "en": {
        "wpm": 150,
        "desc": "Corporate Business English (crisp articulation, steady cadence)",
        "min_ratio": 2.4,
        "max_ratio": 2.9
    }
}


def clean_text(text: str) -> str:
    """Removes extra whitespace and punctuation markers for word counting."""
    return re.sub(r'[^\w\s]', '', text.strip())


def count_words(text: str) -> int:
    """Counts the number of spoken words in a script string."""
    cleaned = clean_text(text)
    if not cleaned:
        return 0
    return len(cleaned.split())


def get_target_word_range(duration_seconds: float = 10.0, language: str = "es") -> Tuple[int, int]:
    """
    Returns the recommended (min_words, max_words) for a given duration in seconds.
    For standard 10s Google Flow segment in Spanish: (21, 26) words.
    """
    lang = language.lower() if language.lower() in WPM_STANDARDS else "es"
    cfg = WPM_STANDARDS[lang]
    min_words = int(round(duration_seconds * cfg["min_ratio"]))
    max_words = int(round(duration_seconds * cfg["max_ratio"]))
    return min_words, max_words


def estimate_spoken_duration(text: str, language: str = "es") -> float:
    """Estimates the spoken duration in seconds for a given text."""
    lang = language.lower() if language.lower() in WPM_STANDARDS else "es"
    wpm = WPM_STANDARDS[lang]["wpm"]
    words = count_words(text)
    return round((words / wpm) * 60, 2)


def evaluate_segment_timing(text: str, duration_seconds: float = 10.0, language: str = "es") -> Dict:
    """
    Evaluates whether a voiceover text strictly complies with the segment duration.
    Returns status: 'optimal', 'too_fast', 'too_slow', or 'empty'.
    """
    words = count_words(text)
    min_w, max_w = get_target_word_range(duration_seconds, language)
    est_duration = estimate_spoken_duration(text, language)

    if words == 0:
        return {
            "status": "empty",
            "words": 0,
            "target_range": (min_w, max_w),
            "estimated_duration": 0.0,
            "message": "El guion está vacío."
        }

    if min_w <= words <= max_w:
        status = "optimal"
        msg = f"Óptimo ({words} palabras / rango {min_w}-{max_w}). Llena exactamente los {duration_seconds}s."
    elif words < min_w:
        status = "too_slow"
        diff = min_w - words
        msg = f"Demasiado corto ({words} palabras). Faltan aprox. {diff} palabras para evitar silencios."
    else:
        status = "too_fast"
        diff = words - max_w
        msg = f"Demasiado largo ({words} palabras). Sobran aprox. {diff} palabras para evitar atropello verbal."

    return {
        "status": status,
        "words": words,
        "target_range": (min_w, max_w),
        "estimated_duration": est_duration,
        "target_duration": duration_seconds,
        "message": msg
    }
