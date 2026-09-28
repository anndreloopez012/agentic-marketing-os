#!/usr/bin/env python3
"""Linter de calidad para contenido de Instagram.

Revisa un archivo de caption, carrusel o guion de video contra el perfil de marca:
  1. Emojis segun la politica del perfil (permitidos | moderados | prohibidos).
  2. Locucion de bloques de 10 s (20-26 palabras por "Dialogo: ...").
  3. Rutas de imagenes locales referenciadas que no existen.
  4. Hashtags de marca y presencia de un CTA.
  5. Titulares de portada de mas de 6 palabras.

Uso:
  python3 content_validator.py <archivo.md> [--perfil ./marca/brand-profile.md]
  python3 content_validator.py --test
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000027BF"
    "]+"
)

DIALOG_PATTERN = re.compile(r"Di[aá]logo[^:\n]*:\s*[\"“]([^\"”]+)[\"”]", re.IGNORECASE)
IMAGE_PATTERN = re.compile(r"(?<![\w/])((?:\.{1,2}/|~/|/)[^\s`'\"()\]]+\.(?:jpe?g|png|webp))", re.IGNORECASE)
TITLE_PATTERN = re.compile(r"Titular[^:\n]*:\s*\[?([^\]\n]+)\]?", re.IGNORECASE)
CTA_HINTS = ("cta", "enlace", "link", "escr", "comenta", "reserva", "agenda", "compra", "whatsapp", "dm", "bio")
MODERATE_EMOJI_LIMIT = 3


def load_profile(path: Path | None) -> dict:
    profile = {"emojis": "moderados", "hashtags": []}
    if not path or not path.exists():
        return profile
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^-\s*emojis:\s*\[?([a-záéíóú]+)", text, re.IGNORECASE | re.MULTILINE)
    if match:
        profile["emojis"] = match.group(1).lower()
    section = re.search(r"##\s*\d*\.?\s*Hashtags(.*?)(?:\n## |\Z)", text, re.IGNORECASE | re.DOTALL)
    if section:
        profile["hashtags"] = [tag for tag in re.findall(r"#[\wÁÉÍÓÚáéíóúñÑ]+", section.group(1))]
    return profile


def validate(text: str, profile: dict, base_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    emojis = EMOJI_PATTERN.findall(text)
    policy = profile.get("emojis", "moderados")
    if policy.startswith("prohib") and emojis:
        errors.append(f"Emojis prohibidos por el perfil: {' '.join(emojis)}")
    elif policy.startswith("moder") and len(emojis) > MODERATE_EMOJI_LIMIT:
        warnings.append(f"{len(emojis)} emojis; el perfil pide uso moderado (<= {MODERATE_EMOJI_LIMIT}).")

    for index, dialog in enumerate(DIALOG_PATTERN.findall(text), 1):
        words = len(dialog.split())
        if not 20 <= words <= 26:
            errors.append(f"Bloque {index}: {words} palabras de locucion (esperado 20-26 por 10 s): \"{dialog[:50]}...\"")

    for raw in IMAGE_PATTERN.findall(text):
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        if not candidate.exists():
            warnings.append(f"Imagen referenciada no encontrada: {raw}")

    for title in TITLE_PATTERN.findall(text):
        clean = title.strip().strip("[]")
        is_placeholder = "MÁX" in clean.upper() or "MAX." in clean.upper()
        if clean and not is_placeholder and len(clean.split()) > 6:
            warnings.append(f"Titular de mas de 6 palabras: \"{clean}\"")

    hashtags = profile.get("hashtags") or []
    if hashtags and not any(tag.lower() in text.lower() for tag in hashtags):
        warnings.append("No aparece ningun hashtag del perfil de marca.")
    if not any(hint in text.lower() for hint in CTA_HINTS):
        warnings.append("No se detecta un llamado a la accion (CTA).")

    return errors, warnings


def run_test() -> int:
    sample = (
        "Titular: CUIDA TU BICI EN 1 HORA\n"
        "Dialogo: \"Si tu cadena suena asi cada manana, no es mala suerte. Es falta de mantenimiento, "
        "y se arregla en menos de una hora.\"\n"
        "Agenda tu revision desde el enlace de la bio. #TallerEjemplo\n"
    )
    errors, warnings = validate(sample, {"emojis": "prohibidos", "hashtags": ["#TallerEjemplo"]}, Path.cwd())
    print("Errores:", errors or "ninguno")
    print("Advertencias:", warnings or "ninguna")
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Linter de calidad para contenido de Instagram")
    parser.add_argument("archivo", nargs="?", help="Archivo .md o .txt a revisar")
    parser.add_argument("--perfil", help="Ruta al brand-profile.md", default=None)
    parser.add_argument("--test", action="store_true", help="Ejecuta una prueba de humo")
    args = parser.parse_args()

    if args.test:
        return run_test()
    if not args.archivo:
        parser.print_help()
        return 1

    target = Path(args.archivo)
    if not target.exists():
        print(f"Error: no existe {target}")
        return 1

    profile_path = Path(args.perfil) if args.perfil else None
    if profile_path is None:
        for candidate in (Path("marca/brand-profile.md"), Path("brand-profile.md")):
            if candidate.exists():
                profile_path = candidate
                break

    profile = load_profile(profile_path)
    errors, warnings = validate(target.read_text(encoding="utf-8"), profile, target.parent)

    print("=" * 60)
    print(f"AUDITORIA DE CALIDAD: {target.name}")
    print(f"Perfil: {profile_path or 'no encontrado (reglas por defecto)'}")
    print("=" * 60)
    print(f"Estado: {'APROBADO' if not errors else 'RECHAZADO'}")
    for line in errors:
        print(f"  [ERROR] {line}")
    for line in warnings:
        print(f"  [AVISO] {line}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
