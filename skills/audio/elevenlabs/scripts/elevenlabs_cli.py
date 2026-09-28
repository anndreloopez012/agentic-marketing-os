#!/usr/bin/env python3
"""
ElevenLabs Unified Power & Natural Language CLI
Execute any ElevenLabs task using explicit commands or natural language (Spanish & English).
"""

import sys
import os
import re
import argparse
import json
import base64
import subprocess
import tempfile
import urllib.request
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def _real_key(value):
    """Ignora valores vacios o de plantilla como 'tu_clave_de_elevenlabs_aqui'."""
    if not value:
        return None
    value = value.strip().strip('"\'')
    if not value or value.startswith("tu_"):
        return None
    return value

def get_api_key(explicit_key=None):
    if explicit_key:
        return explicit_key
    for name in ("ELEVENLABS_API_KEY", "ELEVEN_API_KEY"):
        key = _real_key(os.environ.get(name))
        if key:
            return key
    
    env_path = Path.home() / ".config" / "elevenlabs" / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip('"\'')
                if line.startswith("ELEVEN_API_KEY="):
                    return line.split("=", 1)[1].strip('"\'')
    return None

def get_openrouter_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ.get("OPENROUTER_API_KEY")
    env_path = Path.home() / ".config" / "openrouter" / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip('"\'')
    return None

def get_client(api_key):
    try:
        from elevenlabs.client import ElevenLabs
        return ElevenLabs(api_key=api_key)
    except ImportError:
        print(f"{Colors.RED}Error: La librería 'elevenlabs' de Python no está instalada.{Colors.END}")
        sys.exit(1)

def play_audio(filepath):
    if sys.platform == "darwin":
        subprocess.run(["afplay", str(filepath)])
    else:
        for player in ["ffplay", "aplay", "mpv"]:
            if subprocess.run(["which", player], capture_output=True).returncode == 0:
                args = [player, str(filepath)]
                if player == "ffplay":
                    args = ["ffplay", "-nodisp", "-autoexit", str(filepath)]
                subprocess.run(args)
                return

def resolve_voice_id(client, voice_query):
    voices = client.voices.get_all().voices
    if not voice_query:
        for v in voices:
            if v.name.lower() in ["roger", "adam", "rachel", "sarah"]:
                return v.voice_id, v.name
        return voices[0].voice_id, voices[0].name
    
    for v in voices:
        if v.voice_id == voice_query:
            return v.voice_id, v.name
            
    matches = [v for v in voices if voice_query.lower() in v.name.lower()]
    if matches:
        return matches[0].voice_id, matches[0].name
        
    return voice_query, voice_query

def cmd_status(client, args=None):
    print(f"{Colors.BOLD}{Colors.CYAN}=== Estado de Cuenta ElevenLabs ==={Colors.END}")
    user = client.user.get()
    sub = user.subscription
    tier = sub.tier.capitalize()
    used = sub.character_count
    limit = sub.character_limit
    pct = (used / limit * 100) if limit > 0 else 0
    
    print(f"{Colors.BOLD}Workspace / Usuario:{Colors.END} {user.first_name} ({user.seat_type or 'admin'})")
    print(f"{Colors.BOLD}Tier de Suscripción:{Colors.END}  {Colors.GREEN}{tier}{Colors.END}")
    print(f"{Colors.BOLD}Créditos / Caracteres:{Colors.END} {used:,} / {limit:,} ({pct:.1f}% consumido)")
    print(f"{Colors.BOLD}Límite de Voces:{Colors.END}      {sub.voice_slots_used} / {sub.voice_limit}")
    print(f"{Colors.BOLD}Voces Profesionales:{Colors.END}  {sub.professional_voice_slots_used} / {sub.professional_voice_limit}")
    print(f"{Colors.BOLD}Clonación Instantánea:{Colors.END} {'✓ Habilitada' if sub.can_use_instant_voice_cloning else '✗ Deshabilitada'}")
    print(f"{Colors.BOLD}Clonación Profesional:{Colors.END} {'✓ Habilitada' if sub.can_use_professional_voice_cloning else '✗ Deshabilitada'}")
    print(f"{Colors.BOLD}Estado:{Colors.END}                {sub.status.upper()}")

def cmd_voices(client, args=None):
    search = getattr(args, "search", None) if args else None
    category = getattr(args, "category", None) if args else None
    voices = client.voices.get_all().voices
    if search:
        voices = [v for v in voices if search.lower() in v.name.lower() or (v.labels and any(search.lower() in str(val).lower() for val in v.labels.values()))]
    if category:
        voices = [v for v in voices if v.category == category]

    print(f"{Colors.BOLD}{Colors.CYAN}Voces Disponibles ({len(voices)}):{Colors.END}\n")
    for v in voices:
        labels_str = ", ".join(f"{k}: {val}" for k, val in (v.labels or {}).items())
        cat_color = Colors.GREEN if v.category == "cloned" else Colors.BLUE
        print(f"• {Colors.BOLD}{v.name}{Colors.END}  {cat_color}[{v.category}]{Colors.END}")
        print(f"  ID: {Colors.YELLOW}{v.voice_id}{Colors.END}")
        if labels_str:
            print(f"  Detalles: {Colors.DIM}{labels_str}{Colors.END}")
        if v.description:
            print(f"  Descripción: {Colors.DIM}{v.description}{Colors.END}")
        print()

def cmd_models(client, args=None):
    models = client.models.get_all()
    print(f"{Colors.BOLD}{Colors.CYAN}Modelos Disponibles ({len(models)}):{Colors.END}\n")
    for m in models:
        can_tts = getattr(m, 'can_do_text_to_speech', False)
        can_sts = getattr(m, 'can_do_voice_conversion', False)
        langs = getattr(m, 'languages', [])
        print(f"• {Colors.BOLD}{m.name}{Colors.END} ({Colors.YELLOW}{m.model_id}{Colors.END})")
        print(f"  TTS: {'✓' if can_tts else '✗'} | STS: {'✓' if can_sts else '✗'} | Idiomas: {len(langs) if langs else 0}")
        if m.description:
            print(f"  {Colors.DIM}{m.description}{Colors.END}")
        print()

def run_tts(client, text, voice=None, output_path=None, model="eleven_multilingual_v2",
            stability=0.5, similarity=0.75, style=0.0, boost=True, timestamps=False, play=False):
    voice_id, voice_name = resolve_voice_id(client, voice)
    output_path = output_path or "elevenlabs_tts.mp3"
    
    print(f"{Colors.CYAN}🎙️ Sintetizando voz con '{Colors.BOLD}{voice_name}{Colors.END}{Colors.CYAN}' ({model})...{Colors.END}")
    
    from elevenlabs import VoiceSettings
    voice_settings = VoiceSettings(
        stability=stability,
        similarity_boost=similarity,
        style=style,
        use_speaker_boost=boost
    )

    if timestamps:
        result = client.text_to_speech.convert_with_timestamps(
            voice_id=voice_id,
            text=text,
            model_id=model,
            voice_settings=voice_settings
        )
        audio_bytes = base64.b64decode(result.audio_base64)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        ts_path = Path(output_path).with_suffix(".timestamps.json")
        alignment_data = {
            "characters": result.alignment.characters if result.alignment else [],
            "character_start_times_seconds": result.alignment.character_start_times_seconds if result.alignment else [],
            "character_end_times_seconds": result.alignment.character_end_times_seconds if result.alignment else []
        }
        with open(ts_path, "w", encoding="utf-8") as f:
            json.dump(alignment_data, f, indent=2)
        print(f"{Colors.GREEN}✓ Subtítulos / Timestamps guardados en: {ts_path}{Colors.END}")
    else:
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=model,
            voice_settings=voice_settings
        )
        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

    print(f"{Colors.GREEN}✓ Audio guardado en: {output_path}{Colors.END}")
    if play:
        print(f"{Colors.BLUE}🔊 Reproduciendo...{Colors.END}")
        play_audio(output_path)
    return output_path

def cmd_tts(client, args):
    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    if not text:
        print(f"{Colors.RED}Error: Debes proporcionar un texto.{Colors.END}")
        sys.exit(1)
    run_tts(client, text, voice=args.voice, output_path=args.output, model=args.model,
            stability=args.stability, similarity=args.similarity, style=args.style,
            boost=args.boost, timestamps=args.timestamps, play=args.play)

def cmd_speak(client, args):
    text = args.text
    if getattr(args, 'file', None):
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    if not text:
        print(f"{Colors.RED}Error: Debes proporcionar un texto.{Colors.END}")
        sys.exit(1)
    out = args.output or tempfile.mktemp(suffix=".mp3", prefix="el_speak_")
    run_tts(client, text, voice=args.voice, output_path=out, model=args.model,
            stability=args.stability, similarity=args.similarity, style=args.style,
            boost=args.boost, timestamps=args.timestamps, play=True)

def run_sfx(client, prompt, output_path=None, duration=None, prompt_influence=0.3, play=False):
    output_path = output_path or "elevenlabs_sfx.mp3"
    print(f"{Colors.CYAN}🔊 Generando efecto de sonido para: '{prompt}'...{Colors.END}")
    audio_stream = client.text_to_sound_effects.convert(
        text=prompt,
        duration_seconds=duration,
        prompt_influence=prompt_influence
    )
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
    print(f"{Colors.GREEN}✓ Efecto de sonido guardado en: {output_path}{Colors.END}")
    if play:
        print(f"{Colors.BLUE}🔊 Reproduciendo...{Colors.END}")
        play_audio(output_path)
    return output_path

def cmd_sfx(client, args):
    run_sfx(client, args.prompt, output_path=args.output, duration=args.duration,
            prompt_influence=args.prompt_influence, play=args.play)

def run_isolate(client, input_file, output_path=None, play=False):
    if not os.path.exists(input_file):
        print(f"{Colors.RED}Error: El archivo '{input_file}' no existe.{Colors.END}")
        sys.exit(1)
    output_path = output_path or f"isolated_{Path(input_file).name}"
    print(f"{Colors.CYAN}🧹 Aislando voz y eliminando ruido en '{input_file}'...{Colors.END}")
    with open(input_file, "rb") as f:
        audio_stream = client.audio_isolation.convert(audio=f)
        with open(output_path, "wb") as out:
            for chunk in audio_stream:
                out.write(chunk)
    print(f"{Colors.GREEN}✓ Audio limpio guardado en: {output_path}{Colors.END}")
    if play:
        play_audio(output_path)
    return output_path

def cmd_isolate(client, args):
    run_isolate(client, args.file, output_path=args.output, play=args.play)

def run_transcribe(client, input_file, output_path=None, model="scribe_v1", diarize=False, timestamps=False):
    if not os.path.exists(input_file):
        print(f"{Colors.RED}Error: El archivo '{input_file}' no existe.{Colors.END}")
        sys.exit(1)
    print(f"{Colors.CYAN}📝 Transcribiendo '{input_file}' ({model})...{Colors.END}")
    with open(input_file, "rb") as f:
        response = client.speech_to_text.convert(
            file=f,
            model_id=model,
            diarize=diarize,
            timestamps_granularity="word" if timestamps else "none"
        )
    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            out.write(response.text)
        print(f"{Colors.GREEN}✓ Transcripción guardada en: {output_path}{Colors.END}")
    else:
        print(f"\n{Colors.BOLD}{Colors.GREEN}=== Transcripción ==={Colors.END}")
        print(response.text)
        print(f"{Colors.BOLD}{Colors.GREEN}======================{Colors.END}\n")
    return response.text

def cmd_transcribe(client, args):
    run_transcribe(client, args.file, output_path=args.output, model=args.model,
                   diarize=args.diarize, timestamps=args.timestamps)

def run_music(client, prompt, output_path=None, play=False):
    output_path = output_path or "elevenlabs_music.mp3"
    print(f"{Colors.CYAN}🎵 Componiendo música para: '{prompt}'...{Colors.END}")
    music_stream = client.music.compose(prompt=prompt)
    with open(output_path, "wb") as f:
        for chunk in music_stream:
            f.write(chunk)
    print(f"{Colors.GREEN}✓ Pista musical guardada en: {output_path}{Colors.END}")
    if play:
        print(f"{Colors.BLUE}🔊 Reproduciendo...{Colors.END}")
        play_audio(output_path)
    return output_path

def cmd_music(client, args):
    run_music(client, args.prompt, output_path=args.output, play=args.play)

def cmd_clone(client, args):
    sample_files = [open(fpath, "rb") for fpath in args.samples if os.path.exists(fpath)]
    if not sample_files:
        print(f"{Colors.RED}Error: Muestras de audio no encontradas.{Colors.END}")
        sys.exit(1)
    print(f"{Colors.CYAN}🧬 Clonando voz '{args.name}'...{Colors.END}")
    voice = client.voices.add(
        name=args.name,
        description=args.description or f"Voz clonada para {args.name}",
        files=sample_files
    )
    for f in sample_files:
        f.close()
    print(f"{Colors.GREEN}✓ Voz clonada creada exitosamente: {voice.name} (ID: {voice.voice_id}){Colors.END}")

# ==========================================
#  NATURAL LANGUAGE ROUTER & PARSER
# ==========================================
def parse_natural_language_heuristic(prompt):
    text_clean = prompt.strip()
    lower = text_clean.lower()
    
    # 1. Status / Credits
    if any(k in lower for k in ["credito", "crédito", "cuanto queda", "cuánto queda", "saldo", "cuantos caracteres", "cuántos caracteres", "mi cuenta", "estado de cuenta", "status"]):
        return {"action": "status"}
        
    # 2. Voices list
    if any(k in lower for k in ["lista de voces", "que voces", "qué voces", "voces disponibles", "mostrar voces", "ver voces", "list voices"]):
        return {"action": "voices"}
        
    # 3. Models list
    if any(k in lower for k in ["que modelos", "qué modelos", "modelos disponibles", "lista de modelos", "list models"]):
        return {"action": "models"}
        
    # 4. Audio Isolation
    m_iso = re.search(r"(?:limpia|aisla|aísla|remueve ruido|quitar ruido|quita ruido|limpiar|isolate)\s+(?:el\s+audio\s+)?(?:de\s+)?([^\s]+\.(?:mp3|wav|m4a|aac|ogg|flac))", text_clean, re.I)
    if m_iso:
        return {"action": "isolate", "file": m_iso.group(1)}
        
    # 5. Transcription
    m_tra = re.search(r"(?:transcribe|transcribir|pasa a texto|pasar a texto|stt)\s+(?:el\s+audio\s+)?(?:de\s+)?([^\s]+\.(?:mp3|wav|m4a|aac|ogg|flac))", text_clean, re.I)
    if m_tra:
        return {"action": "transcribe", "file": m_tra.group(1)}
        
    # 6. Sound Effects (SFX)
    m_sfx = re.search(r"(?:efecto de sonido|sonido de|haz un sonido de|crea un sonido de|ruido de|sfx|sound effect)\s*(?:de\s+|para\s+)?(.*)", text_clean, re.I)
    if m_sfx:
        sfx_prompt = m_sfx.group(1).strip()
        dur_match = re.search(r"(?:de\s+)?(\d+(?:\.\d+)?)\s*(?:segundos?|s\b)", sfx_prompt, re.I)
        dur = float(dur_match.group(1)) if dur_match else None
        if dur_match:
            sfx_prompt = sfx_prompt.replace(dur_match.group(0), "").strip()
        play = any(k in lower for k in ["reproduce", "escucha", "play", "oir", "oír"])
        return {"action": "sfx", "prompt": sfx_prompt or "ambient sound", "duration": dur, "play": play}
        
    # 7. Music Generation
    m_mus = re.search(r"(?:musica|música|cancion|canción|pista musical|beat|soundtrack)\s*(?:de\s+|para\s+)?(.*)", text_clean, re.I)
    if m_mus:
        mus_prompt = m_mus.group(1).strip()
        play = any(k in lower for k in ["reproduce", "escucha", "play", "oir", "oír"])
        return {"action": "music", "prompt": mus_prompt or "cinematic background music", "play": play}

    # 8. Voice extraction: "con voz de X" / "usando la voz de X"
    voice = None
    m_v = re.search(r"(?:con voz(?: de)?|usando la voz de|con la voz de)\s+([a-zA-Z0-9_-]+)", text_clean, re.I)
    if m_v:
        voice = m_v.group(1)
        text_clean = text_clean[:m_v.start()] + text_clean[m_v.end():]
        text_clean = text_clean.strip()

    # 9. Check if file generation requested: "genera un audio / guarda un audio / crea una locución"
    if any(k in lower for k in ["genera un audio", "crea un audio", "guarda un audio", "haz una locucion", "haz una locución", "guárdalo en", "guardalo en"]):
        m_t = re.search(r"(?:genera|crea|haz|guarda)\s+(?:un\s+audio|una\s+locución|una\s+locucion|un\s+archivo)?\s*(?:que\s+diga|diciendo|con el texto)?\s*[:\"'\s]*(.*?)(?:[\"']|$)", text_clean, re.I)
        speech_text = m_t.group(1).strip() if m_t else text_clean
        out_match = re.search(r"(?:en|como)\s+([a-zA-Z0-9_-]+\.mp3)", text_clean, re.I)
        out_file = out_match.group(1) if out_match else "locucion.mp3"
        return {"action": "tts", "text": speech_text, "voice": voice, "output": out_file}

    # 10. Default speak (live playback): "di ...", "habla ...", "reproduce ...", "say ..."
    m_spk = re.search(r"^(?:di|habla|reproduce|say|speak|dile que|pronuncia)\s*[:\"'\s]*(.*?)(?:[\"']|$)", text_clean, re.I)
    if m_spk:
        speech_text = m_spk.group(1).strip()
        return {"action": "speak", "text": speech_text, "voice": voice}

    # Fallback to speak the text
    return {"action": "speak", "text": text_clean, "voice": voice}

def parse_with_openrouter(prompt):
    openrouter_key = get_openrouter_key()
    if not openrouter_key:
        return None

    system_prompt = (
        "You are an ElevenLabs natural language intent parser. "
        "Extract the user's intent into a JSON object with these allowed actions: "
        "'speak' (live voice playback), 'tts' (save voice to file), 'sfx' (sound effect), "
        "'music' (music track), 'isolate' (audio cleaning), 'transcribe' (STT), "
        "'status' (account info), 'voices' (voice list).\n"
        "Return ONLY valid JSON matching this schema:\n"
        '{"action": "speak|tts|sfx|music|isolate|transcribe|status|voices", '
        '"text": "string or null", "prompt": "string or null", "voice": "string or null", '
        '"file": "string or null", "output": "string or null", "duration": float or null, "play": bool}'
    )

    req_data = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(req_data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            content = res_json["choices"][0]["message"]["content"].strip()
            # Clean markdown fences if any
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
    except Exception:
        return None

def execute_nl_intent(client, intent):
    action = intent.get("action", "speak")
    print(f"{Colors.DIM}✨ Intención detectada: {action.upper()}{Colors.END}")

    if action == "status":
        cmd_status(client)
    elif action == "voices":
        cmd_voices(client)
    elif action == "models":
        cmd_models(client)
    elif action == "speak":
        text = intent.get("text") or intent.get("prompt")
        voice = intent.get("voice")
        temp_out = tempfile.mktemp(suffix=".mp3", prefix="el_nl_")
        run_tts(client, text, voice=voice, output_path=temp_out, play=True)
    elif action == "tts":
        text = intent.get("text") or intent.get("prompt")
        voice = intent.get("voice")
        output_path = intent.get("output") or "locucion.mp3"
        play = intent.get("play", False)
        run_tts(client, text, voice=voice, output_path=output_path, play=play)
    elif action == "sfx":
        prompt = intent.get("prompt") or intent.get("text")
        output_path = intent.get("output") or "efecto.mp3"
        dur = intent.get("duration")
        play = intent.get("play", True)
        run_sfx(client, prompt, output_path=output_path, duration=dur, play=play)
    elif action == "music":
        prompt = intent.get("prompt") or intent.get("text")
        output_path = intent.get("output") or "musica.mp3"
        play = intent.get("play", True)
        run_music(client, prompt, output_path=output_path, play=play)
    elif action == "isolate":
        file_path = intent.get("file")
        output_path = intent.get("output")
        play = intent.get("play", False)
        run_isolate(client, file_path, output_path=output_path, play=play)
    elif action == "transcribe":
        file_path = intent.get("file")
        output_path = intent.get("output")
        run_transcribe(client, file_path, output_path=output_path)

def main():
    KNOWN_COMMANDS = {
        "status", "account", "whoami", "voices", "models", "tts", "generate",
        "speak", "sfx", "sound-effect", "isolate", "transcribe", "stt", "clone", "music", "help"
    }

    # If first argument is not a known subcommand and not a flag, treat the whole command line as natural language
    if len(sys.argv) > 1 and sys.argv[1] not in KNOWN_COMMANDS and not sys.argv[1].startswith("-"):
        nl_prompt = " ".join(sys.argv[1:])
        api_key = get_api_key()
        if not api_key:
            print(f"{Colors.RED}Error: No se encontró ELEVENLABS_API_KEY.{Colors.END}")
            sys.exit(1)
        client = get_client(api_key)
        
        # 1. Try fast local heuristics
        intent = parse_natural_language_heuristic(nl_prompt)
        
        # 2. If intent is just fallback speak but prompt was clearly conversational or long, try OpenRouter
        if intent.get("action") == "speak" and len(nl_prompt.split()) > 6 and not any(k in nl_prompt.lower() for k in ["di", "habla", "reproduce"]):
            ai_intent = parse_with_openrouter(nl_prompt)
            if ai_intent:
                intent = ai_intent
                
        execute_nl_intent(client, intent)
        return

    # Standard Argparse CLI
    parser = argparse.ArgumentParser(
        description="ElevenLabs Unified CLI - Voz, Efectos de Sonido, Música y Audio con IA",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--api-key", help="Clave API de ElevenLabs")
    subparsers = parser.add_subparsers(dest="command")

    p_status = subparsers.add_parser("status", aliases=["account", "whoami"], help="Consulta créditos y estado")
    p_voices = subparsers.add_parser("voices", help="Lista las voces")
    p_voices.add_argument("-s", "--search")
    p_voices.add_argument("-c", "--category")
    p_models = subparsers.add_parser("models", help="Lista los modelos")

    p_tts = subparsers.add_parser("tts", aliases=["generate"], help="Texto a voz")
    p_tts.add_argument("text", nargs="?")
    p_tts.add_argument("-f", "--file")
    p_tts.add_argument("-v", "--voice")
    p_tts.add_argument("-o", "--output")
    p_tts.add_argument("-m", "--model", default="eleven_multilingual_v2")
    p_tts.add_argument("--stability", type=float, default=0.5)
    p_tts.add_argument("--similarity", type=float, default=0.75)
    p_tts.add_argument("--style", type=float, default=0.0)
    p_tts.add_argument("--no-boost", dest="boost", action="store_false")
    p_tts.add_argument("--timestamps", action="store_true")
    p_tts.add_argument("-p", "--play", action="store_true")

    p_speak = subparsers.add_parser("speak", help="Habla inmediatamente por los altavoces de la Mac")
    p_speak.add_argument("text", nargs="?")
    p_speak.add_argument("-f", "--file")
    p_speak.add_argument("-v", "--voice")
    p_speak.add_argument("-o", "--output")
    p_speak.add_argument("-m", "--model", default="eleven_multilingual_v2")
    p_speak.add_argument("--stability", type=float, default=0.5)
    p_speak.add_argument("--similarity", type=float, default=0.75)
    p_speak.add_argument("--style", type=float, default=0.0)
    p_speak.add_argument("--no-boost", dest="boost", action="store_false")
    p_speak.add_argument("--timestamps", action="store_true")

    p_sfx = subparsers.add_parser("sfx", aliases=["sound-effect"], help="Genera efectos de sonido")
    p_sfx.add_argument("prompt")
    p_sfx.add_argument("-o", "--output")
    p_sfx.add_argument("-d", "--duration", type=float, default=None)
    p_sfx.add_argument("--prompt-influence", type=float, default=0.3)
    p_sfx.add_argument("-p", "--play", action="store_true")

    p_isolate = subparsers.add_parser("isolate", help="Limpia ruido de fondo de un audio")
    p_isolate.add_argument("file")
    p_isolate.add_argument("-o", "--output")
    p_isolate.add_argument("-p", "--play", action="store_true")

    p_transcribe = subparsers.add_parser("transcribe", aliases=["stt"], help="Transcribe audio a texto")
    p_transcribe.add_argument("file")
    p_transcribe.add_argument("-o", "--output")
    p_transcribe.add_argument("-m", "--model", default="scribe_v1")
    p_transcribe.add_argument("--diarize", action="store_true")
    p_transcribe.add_argument("--timestamps", action="store_true")

    p_clone = subparsers.add_parser("clone", help="Clona una voz")
    p_clone.add_argument("name")
    p_clone.add_argument("samples", nargs="+")
    p_clone.add_argument("-d", "--description")

    p_music = subparsers.add_parser("music", help="Genera música")
    p_music.add_argument("prompt")
    p_music.add_argument("-o", "--output")
    p_music.add_argument("-p", "--play", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    api_key = get_api_key(args.api_key)
    if not api_key:
        print(f"{Colors.RED}Error: No se encontró ELEVENLABS_API_KEY.{Colors.END}")
        sys.exit(1)

    client = get_client(api_key)
    if args.command in ["status", "account", "whoami"]:
        cmd_status(client, args)
    elif args.command == "voices":
        cmd_voices(client, args)
    elif args.command == "models":
        cmd_models(client, args)
    elif args.command in ["tts", "generate"]:
        cmd_tts(client, args)
    elif args.command == "speak":
        cmd_speak(client, args)
    elif args.command in ["sfx", "sound-effect"]:
        cmd_sfx(client, args)
    elif args.command == "isolate":
        cmd_isolate(client, args)
    elif args.command in ["transcribe", "stt"]:
        cmd_transcribe(client, args)
    elif args.command == "clone":
        cmd_clone(client, args)
    elif args.command == "music":
        cmd_music(client, args)

if __name__ == "__main__":
    main()
