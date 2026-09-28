---
name: elevenlabs
description: >-
  Use ElevenLabs for high-quality text-to-speech (TTS), audio isolation, sound effects,
  speech-to-text (Scribe transcription), voice cloning, music generation, and multi-voice
  dialogues. Use when asked to generate voiceovers, audio narration, sound effects, clone voices,
  transcribe recordings, clean audio background noise, or interact with ElevenLabs tools and API.
---

# ElevenLabs Power Guide & Integration

This skill provides comprehensive instructions, best practices, CLI commands, and code patterns to leverage 100% of ElevenLabs capabilities across Antigravity, Codex, and Claude Code.

---

## 1. Uso en Lenguaje Natural (Natural Language First)

Tanto en la terminal con la CLI (`elevenlabs` o `el`) como al conversar con los agentes (Antigravity, Codex o Claude Code), puedes pedir cualquier acción directamente en lenguaje natural:

```bash
# Hablar / reproducir en vivo en tus parlantes:
el "di hola bienvenidos a mi tienda con voz de Sarah"
el "reproduce con voz de Roger: la reunión es a las 3"

# Generar efectos de sonido:
el "efecto de sonido de un trueno con lluvia de 4 segundos"
el "haz un sonido de una puerta crujiendo"

# Crear fondos o pistas musicales:
el "música lofi relajante para programar"

# Consultas y estado:
el "cuántos créditos me quedan"
el "muestra las voces disponibles"

# Limpieza y transcripción de archivos:
el "limpia el audio podcast_ruidoso.mp3"
el "transcribe la llamada reunion.m4a"
```

---

## 2. Quick CLI Access (`elevenlabs` / `el`)

El CLI viene incluido en esta skill: `scripts/elevenlabs_cli.py`. El instalador de Agentic Marketing OS lo deja disponible como `elevenlabs` y `el`. Sin instalador:

```bash
python3 -m pip install --user elevenlabs   # o dentro de un entorno virtual
export ELEVENLABS_API_KEY=...              # o guárdala en ~/.config/elevenlabs/.env
python3 <skill-dir>/scripts/elevenlabs_cli.py status
```

En ChatGPT o claude.ai (sin terminal) usa la API o la web de ElevenLabs con los mismos parámetros de voz y modelo descritos abajo.

```bash
# List available voices (search by name, accent, gender) (search by name, accent, gender)
elevenlabs voices -s "spanish"
elevenlabs voices -s "Roger"

# Text-to-Speech (TTS)
elevenlabs tts "Hola, bienvenidos a este nuevo episodio." -o salida.mp3 -v "Roger"

# TTS with timestamps (creates salida.mp3 and salida.timestamps.json for subtitles)
elevenlabs tts "Texto sincronizado" -o video_sub.mp3 --timestamps

# Instant playback through your speakers (great for testing)
elevenlabs speak "Audio de prueba reproducido en vivo."

# Sound Effects (SFX)
elevenlabs sfx "cinematic sci-fi laser blast with deep bass" -d 2.5 -o laser.mp3

# Audio Isolation (Removes background noise, room echo, hum)
elevenlabs isolate podcast_noisy.wav -o podcast_clean.mp3

# Scribe Transcription (Speech-to-Text with high precision)
elevenlabs transcribe interview.mp3 --diarize --timestamps -o transcript.txt

# Instant Voice Cloning (from audio samples)
elevenlabs clone "Voz Corporativa" muestra1.mp3 muestra2.mp3 -d "Locutor corporativo"

# AI Music Generation
elevenlabs music "ambient chillhop lofi beat for coding" -o background.mp3
```

---

## 3. Models Guide: Choosing the Right Model

| Model ID | Primary Use Case | Latency | Quality / Emotion | Languages |
| :--- | :--- | :--- | :--- | :--- |
| `eleven_multilingual_v2` | **Narración, emoción, podcasts, audiolibros** | Media (~300ms) | ★★★★★ (Máxima expresividad) | 29+ idiomas (incl. ES) |
| `eleven_turbo_v2_5` | **Videos rápidos, e-learning, streaming** | Baja (~150ms) | ★★★★☆ (Excelente consistencia) | 32+ idiomas |
| `eleven_flash_v2_5` | **Agentes conversacionales en vivo, bots** | Ultra-baja (~75ms) | ★★★☆☆ (Económico en créditos) | 32+ idiomas |
| `eleven_text_to_sound_v2` | **Efectos de sonido, impactos, ambientes** | Rápida | Alta fidelidad acústica | Text prompts |
| `scribe_v1` / `scribe_v2` | **Transcripción de audio (STT)** | Batch | Estado del arte con diarización | 99+ idiomas |

---

## 4. Voice Settings Tuning (Ajuste Fino de Parámetros)

Para sacarle el máximo provecho a la voz según el objetivo:

* **Stability (0.0 a 1.0)**:
  * `0.30 - 0.45`: **Voz dramática, expresiva y emocional**. Ideal para audiolibros de ficción, narración de historias, doblaje de personajes.
  * `0.50 - 0.65`: **Conversacional equilibrado** (Recomendado por defecto). Ideal para podcasts, tutoriales y videos explicativos.
  * `0.70 - 0.85`: **Ultra-consistente y sobrio**. Ideal para noticias, cursos formales, avisos corporativos y discursos técnicos.
* **Similarity Boost (0.0 a 1.0)**:
  * `0.75 - 0.85`: Fidelidad alta a la voz original sin introducir distorsiones ni artefactos.
  * `> 0.90`: Usar solo si la muestra de audio original es prístina (sin ningún ruido de fondo).
* **Style Exaggeration (0.0 a 1.0)**:
  * `0.00`: Neutro / Natural.
  * `0.10 - 0.25`: Énfasis en el estilo dramático de la voz.
* **Speaker Boost**:
  * Siempre mantener en `True` para maximizar presencia y claridad vocal.

---

## 5. MCP Server Tools (Model Context Protocol)

El servidor MCP `@mindstone/mcp-server-elevenlabs` está instalado y configurado en:
- Antigravity: `~/.gemini/config/mcp_config.json`
- Claude Code: `~/.claude/mcp_config.json`
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Codex: `~/.codex/config.toml`

Herramientas disponibles directamente para los agentes:
- `generate_speech`: Texto a voz directo con soporte de semillas (`seed`) y pronunciación.
- `generate_speech_with_timestamps`: Genera audio + archivo `.srt` sincronizado palabra por palabra.
- `generate_sound_effect`: Genera FX acústicos de hasta 22 segundos.
- `isolate_audio`: Limpieza y supresión de ruido en audios > 4.6s.
- `transcribe_audio`: Transcripción de audio con separación de hablantes (`diarize`).
- `speech_to_speech`: Conversión de tono y voz entre dos archivos de audio.
- `text_to_dialogue`: Guiones multi-personaje con diferentes voces por línea.
- `clone_voice`: Creación de clones instantáneos.
- `design_voice` & `create_voice_from_preview`: Diseño sintético de voces nuevas desde cero.
- `create_dubbing` & `get_dubbing`: Doblaje automático multilingüe de videos y pistas de audio.
- `generate_music`: Creación de composiciones musicales completas.

---

## 6. Python Code Patterns

```python
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

client = ElevenLabs()  # Lee ELEVENLABS_API_KEY automáticamente

# 1. Generar audio simple
audio = client.text_to_speech.convert(
    voice_id="CwhRBWXzGAHq8TQ4Fs17",  # Roger
    text="Hola, esto es una narración generada con ElevenLabs.",
    model_id="eleven_multilingual_v2",
    voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.1, use_speaker_boost=True)
)
with open("output.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

# 2. Generar audio con timestamps para subtítulos
result = client.text_to_speech.convert_with_timestamps(
    voice_id="CwhRBWXzGAHq8TQ4Fs17",
    text="Este audio tiene marcas de tiempo precisas.",
    model_id="eleven_multilingual_v2"
)

# 3. Efectos de sonido
sfx = client.text_to_sound_effects.convert(
    text="Thunder strike with heavy rain in the forest",
    duration_seconds=3.0
)

# 4. Transcripción con Scribe
with open("audio.mp3", "rb") as f:
    transcript = client.speech_to_text.convert(file=f, model_id="scribe_v1", diarize=True)
    print(transcript.text)
```

---

## 7. Integración con Video (HyperFrames / Remotion)

Cuando generes videos con `hyperframes` o `remotion`:
1. Genera la locución con `elevenlabs tts "..." --timestamps -o audio.mp3`.
2. Utiliza `audio.timestamps.json` para alinear cortes de cámara, textos cinéticos y animaciones con los frames exactos del habla.
3. Agrega efectos de sonido ambientales con `elevenlabs sfx "..." -o whoosh.mp3`.
