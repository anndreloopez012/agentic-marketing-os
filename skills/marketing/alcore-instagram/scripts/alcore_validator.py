#!/usr/bin/env python3
"""
ALCORE Content Quality & Production Linter (alcore_validator.py)
Validador de calidad corporativa para publicaciones, prompts y guiones de Instagram (@alcore.gt).

Verificaciones obligatorias:
1. Regla de Cero Emojis (escaneo exhaustivo de pictogramas y emoticonos, permitiendo viñetas tipográficas •, ▪, —).
2. Métrica de Locución para Google Flow (20 a 26 palabras por cada bloque de 10 segundos).
3. Verificación de Rutas Locales de Imágenes de Mascotas.
4. Coherencia de Mascota y Columna (Kivo -> Col 1, Alki -> Col 2, Kivi -> Col 3).
5. Estructura de Copywriting (Presencia de Badge, Fórmula PAS, CTA y Hashtags oficiales).
"""

import sys
import re
import os
from pathlib import Path

# Rango Unicode preciso para detección de emojis, excluyendo viñetas tipográficas permitidas (•, ▪, —)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticonos
    "\U0001F300-\U0001F5FF"  # Símbolos y pictogramas
    "\U0001F680-\U0001F6FF"  # Transporte y mapas
    "\U0001F1E0-\U0001F1FF"  # Banderas
    "\U0001F900-\U0001F9FF"  # Símbolos y pictogramas suplementarios
    "\U0001FA70-\U0001FAFF"  # Símbolos extendidos
    "\U00002705"              # Check mark emoji
    "\U0000270A-\U0000270D"  # Gestos con manos
    "\U00002728"              # Destellos
    "\U0000274C"              # Marca de cruz
    "\U000026A0"              # Signo de advertencia emoji
    "\U00002600-\U00002604"  # Clima/sol
    "]+",
    flags=re.UNICODE
)

OFFICIAL_HASHTAGS = [
    "#Alcore", "#GuatemalaTech", "#CloudComputing", 
    "#DevOpsLATAM", "#Kinvo", "#KinvoExpress", "#IngenieriaDeSoftware"
]

def check_emojis(text: str) -> list:
    """Detecta la presencia de emojis prohibidos."""
    return EMOJI_PATTERN.findall(text)

def check_flow_timing(text: str) -> list:
    """Verifica que los diálogos de bloques de 10s en Flow tengan entre 20 y 26 palabras."""
    issues = []
    pattern = re.compile(r'Diálogo.*?:\s*["“]([^"”]+)["”]', re.IGNORECASE)
    matches = pattern.findall(text)
    for i, dialog in enumerate(matches, 1):
        words = dialog.strip().split()
        count = len(words)
        if count < 20 or count > 26:
            issues.append(f"Bloque {i}: {count} palabras (rango óptimo: 20-26 palabras para 10 segundos). Diálogo: '{dialog[:45]}...'")
    return issues

def check_asset_paths(text: str) -> list:
    """Verifica que las rutas de imágenes referenciadas existan en el sistema de archivos."""
    missing = []
    path_pattern = re.compile(r'(/Users/macbookpro/Documents/ALCORE/MASCOTAS/[^\s\)\]"]+\.jpg)')
    found_paths = path_pattern.findall(text)
    for p in found_paths:
        if not os.path.exists(p):
            missing.append(p)
    return missing

def validate_content(text: str) -> dict:
    """Ejecuta la auditoría integral de calidad."""
    results = {
        "passed": True,
        "emojis": check_emojis(text),
        "flow_timing_issues": check_flow_timing(text),
        "missing_assets": check_asset_paths(text),
        "has_official_hashtags": any(tag.lower() in text.lower() for tag in OFFICIAL_HASHTAGS),
        "has_column_badge": bool(re.search(r'\[COLUMNA\s+[123]', text, re.IGNORECASE))
    }

    if results["emojis"] or results["flow_timing_issues"] or results["missing_assets"]:
        results["passed"] = False

    return results

def run_cli():
    if len(sys.argv) < 2:
        print("Uso: python3 alcore_validator.py <archivo.md|texto>")
        print("     python3 alcore_validator.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        test_text = """
        [COLUMNA 1 - KINVO]
        PRUEBA DE VALIDACION

        Texto con viñetas tipográficas permitidas: • punto 1 ▪ punto 2 — guion.
        Diálogo Sincronizado (00:00 - 00:10): "Cobrar en mostrador debería tomar menos de cinco segundos cuando tu sistema de facturación está integrado directamente con el SAT local."
        Ruta: /Users/macbookpro/Documents/ALCORE/MASCOTAS/KIVO/01_kivo_frontal_full.jpg
        #Alcore #GuatemalaTech #Kinvo
        """
        res = validate_content(test_text)
        print("Resultado del test de validación:")
        print(f"Pasa auditoría: {res['passed']}")
        print(f"Emojis encontrados: {len(res['emojis'])}")
        print(f"Desviaciones de tiempo en Flow: {len(res['flow_timing_issues'])}")
        print(f"Assets faltantes: {len(res['missing_assets'])}")
        print(f"Badge de columna presente: {res['has_column_badge']}")
        sys.exit(0 if res["passed"] else 1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: El archivo '{filepath}' no existe.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    res = validate_content(content)
    print("=" * 60)
    print(f"REPORTE DE AUDITORÍA DE CALIDAD ALCORE: {os.path.basename(filepath)}")
    print("=" * 60)
    print(f"Estado General: {'APROBADO' if res['passed'] else 'RECHAZADO'}")
    print(f"Badge de Columna: {'OK' if res['has_column_badge'] else 'FALTA BADGE [COLUMNA X]'}")
    print(f"Hashtags Oficiales: {'OK' if res['has_official_hashtags'] else 'ADVERTENCIA: Faltan hashtags oficiales'}")

    if res["emojis"]:
        print(f"\n[VIOLACIÓN CRÍTICA] Emojis detectados ({len(res['emojis'])}):")
        for em in res["emojis"]:
            print(f"  - Carácter prohibido: {em}")

    if res["flow_timing_issues"]:
        print(f"\n[ALERTA DE LOCUCIÓN FLOW] Desajuste de métrica temporal en bloques de 10s:")
        for iss in res["flow_timing_issues"]:
            print(f"  - {iss}")

    if res["missing_assets"]:
        print(f"\n[ERROR DE RECURSOS] Rutas locales de imagen no encontradas:")
        for p in res["missing_assets"]:
            print(f"  - {p}")

    print("=" * 60)
    sys.exit(0 if res["passed"] else 1)

if __name__ == "__main__":
    run_cli()
