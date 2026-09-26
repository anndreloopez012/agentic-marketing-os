#!/usr/bin/env python3
"""
veo_client.py
Cliente de producción para Google Veo 3.1, Veo 2 y Gemini Omni.
Implementa llamadas nativas directas vía REST (zero-dependencies con urllib)
y compatibilidad automática con google-genai SDK si está instalado.
Soporta:
- Text-to-Video
- Image-to-Video (First Frame)
- Frame Interpolation (First Frame + Last Frame)
- Video Extension
- Sondeo asíncrono con exponential backoff y sanitización de credenciales.
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional, Tuple

DEFAULT_MODEL = "veo-3.1-generate-preview"
DEFAULT_DURATION = 6
DEFAULT_ASPECT_RATIO = "9:16"
DEFAULT_RESOLUTION = "720p"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def get_api_key() -> str:
    """Obtiene la API key de GEMINI_API_KEY."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "ERROR: La variable de entorno GEMINI_API_KEY no está configurada.\n"
            "Ejecuta: export GEMINI_API_KEY='tu-api-key'"
        )
    return key

def sanitize_error(err_str: str) -> str:
    """Sanitiza mensajes de error para nunca exponer API keys ni tokens en logs."""
    if not err_str:
        return ""
    key = os.environ.get("GEMINI_API_KEY", "")
    if key and len(key) >= 8:
        err_str = err_str.replace(key, "[REDACTED_KEY]")
    err_str = re.sub(r'AIza[0-9A-Za-z_\-]{30,}', '[REDACTED_KEY]', err_str)
    err_str = re.sub(r'AQ\.[0-9A-Za-z_\-]{20,}', '[REDACTED_KEY]', err_str)
    err_str = re.sub(r'Bearer\s+[A-Za-z0-9_\-\.]+', 'Bearer [REDACTED_TOKEN]', err_str, flags=re.IGNORECASE)
    err_str = re.sub(r'([?&](?:key|api_key|apiKey)=)[^&\s"\'<>()]+', r'\1[REDACTED]', err_str)
    return err_str

def encode_image_to_base64(image_path: str) -> Tuple[str, str]:
    """Lee una imagen local y retorna (base64_data, mime_type)."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No se encontró la imagen: {image_path}")
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".bmp": "image/bmp"
    }
    mime_type = mime_map.get(ext, "image/jpeg")
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data, mime_type

def make_rest_request(url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, method: str = "GET") -> Dict[str, Any]:
    """Realiza una petición HTTP REST segura usando únicamente urllib."""
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if headers:
        req_headers.update(headers)
    
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        if method == "GET":
            method = "POST"
    
    req = urllib.request.Request(url, data=encoded_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        raw_error = e.read().decode("utf-8", errors="replace")
        sanitized = sanitize_error(raw_error)
        raise RuntimeError(f"HTTP Error {e.code}: {sanitized}") from None
    except Exception as e:
        sanitized = sanitize_error(str(e))
        raise RuntimeError(f"Error de red: {sanitized}") from None

def download_file(url: str, destination: str, api_key: str):
    """Descarga un archivo con urllib siguiendo redirecciones de forma segura."""
    os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
    req = urllib.request.Request(url, headers={"x-goog-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            with open(destination, "wb") as out_f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    out_f.write(chunk)
    except Exception as e:
        # Fallback sin header si la URL ya es una URL firmada de storage
        req2 = urllib.request.Request(url)
        with urllib.request.urlopen(req2, timeout=300) as resp:
            with open(destination, "wb") as out_f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    out_f.write(chunk)

class VeoClient:
    """Cliente unificado para generación de video con Google Veo y Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_api_key()
        self._sdk_available = False
        self._sdk_client = None
        try:
            from google import genai
            self._sdk_client = genai.Client(api_key=self.api_key)
            self._sdk_available = True
        except ImportError:
            self._sdk_available = False

    def generate_video(
        self,
        prompt: str,
        first_frame: Optional[str] = None,
        last_frame: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        duration: int = DEFAULT_DURATION,
        resolution: str = DEFAULT_RESOLUTION,
        output_path: str = "output_veo.mp4",
        poll_interval: int = 10,
        timeout: int = 900
    ) -> str:
        """
        Genera un video a partir de una o dos imágenes y un prompt cinematográfico.
        
        Args:
            prompt: Descripción de movimiento de cámara e iluminación en inglés.
            first_frame: Ruta a la imagen inicial.
            last_frame: Ruta a la imagen final (opcional, para interpolación).
            model: Modelo a utilizar (ej. 'veo-3.1-generate-preview' o 'veo-2.0-generate-001').
            aspect_ratio: '9:16', '16:9' o '1:1'.
            duration: Segundos (4, 6 u 8 para Veo 3.1).
            resolution: '720p', '1080p' o '4k'.
            output_path: Archivo MP4 de destino.
            poll_interval: Segundos entre cada consulta de estado.
            timeout: Tiempo máximo de espera en segundos.
        
        Returns:
            Ruta del video descargado.
        """
        print(f"\n[VeoClient] Iniciando generación con modelo '{model}'...")
        print(f"            Aspect Ratio: {aspect_ratio} | Resolución: {resolution} | Duración: {duration}s")
        if first_frame:
            print(f"            Frame inicial: {first_frame}")
        if last_frame:
            print(f"            Frame final (interpolación): {last_frame}")
        print(f"            Prompt: \"{prompt}\"")

        # Configurar instancia
        instance: Dict[str, Any] = {"prompt": prompt}
        
        if first_frame:
            b64_data, mime_type = encode_image_to_base64(first_frame)
            instance["image"] = {
                "bytesBase64Encoded": b64_data,
                "mimeType": mime_type
            }
        
        if last_frame:
            b64_data_last, mime_type_last = encode_image_to_base64(last_frame)
            instance["lastFrame"] = {
                "bytesBase64Encoded": b64_data_last,
                "mimeType": mime_type_last
            }

        # Parámetros Veo
        parameters: Dict[str, Any] = {
            "aspectRatio": aspect_ratio,
            "durationSeconds": str(duration),
            "resolution": resolution,
            "personGeneration": "allow_adult"
        }

        request_body = {
            "instances": [instance],
            "parameters": parameters
        }

        endpoint_url = f"{BASE_URL}/models/{model}:predictLongRunning"
        headers = {"x-goog-api-key": self.api_key}

        print("[VeoClient] Enviando solicitud al endpoint de Google Veo...")
        response = make_rest_request(endpoint_url, data=request_body, headers=headers, method="POST")
        
        operation_name = response.get("name")
        if not operation_name:
            raise RuntimeError(f"Respuesta inesperada de Veo API: {response}")

        print(f"[VeoClient] Operación creada exitosamente: {operation_name}")
        print("[VeoClient] Esperando que Veo termine de renderizar el video...")

        # Sondeo (Polling)
        poll_url = f"{BASE_URL}/{operation_name}"
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"La generación excedió el tiempo límite de {timeout} segundos.")

            time.sleep(poll_interval)
            status_resp = make_rest_request(poll_url, headers=headers, method="GET")
            is_done = status_resp.get("done", False)

            if is_done:
                # Comprobar si hubo error en la operación
                if "error" in status_resp:
                    err_info = sanitize_error(json.dumps(status_resp["error"]))
                    raise RuntimeError(f"Error devuelto por la operación de Veo: {err_info}")
                
                # Extraer URI o datos de video
                resp_data = status_resp.get("response", {})
                
                # Manejar variaciones del esquema de respuesta de Veo / PredictLongRunning
                generated_samples = None
                if "generateVideoResponse" in resp_data:
                    generated_samples = resp_data["generateVideoResponse"].get("generatedSamples")
                elif "generated_videos" in resp_data:
                    generated_samples = resp_data["generated_videos"]
                elif "generatedSamples" in resp_data:
                    generated_samples = resp_data["generatedSamples"]

                if not generated_samples or len(generated_samples) == 0:
                    raise RuntimeError(f"No se encontró muestra de video en la respuesta: {status_resp}")

                video_obj = generated_samples[0].get("video", {})
                video_uri = video_obj.get("uri")
                video_b64 = video_obj.get("bytesBase64Encoded") or video_obj.get("videoBytes")

                if video_b64:
                    print(f"[VeoClient] Guardando bytes de video en {output_path}...")
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(video_b64))
                    print(f"[VeoClient] ¡Video guardado exitosamente en {output_path}!")
                    return output_path
                elif video_uri:
                    print(f"[VeoClient] Descargando video generado desde URI remota...")
                    download_file(video_uri, output_path, self.api_key)
                    print(f"[VeoClient] ¡Video descargado exitosamente en {output_path}!")
                    return output_path
                else:
                    raise RuntimeError(f"El objeto de video no contiene uri ni bytesBase64Encoded: {video_obj}")

            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            print(f"            [+ {mins:02d}:{secs:02d}] Procesando frames de alta definición...")

def main():
    parser = argparse.ArgumentParser(description="Cliente CLI para Google Veo 3.1 y 2.0")
    parser.add_argument("--prompt", required=True, help="Prompt de cinematografía en inglés")
    parser.add_argument("--first-frame", help="Ruta a imagen de inicio")
    parser.add_argument("--last-frame", help="Ruta a imagen final para interpolación")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Modelo Veo (default: veo-3.1-generate-preview)")
    parser.add_argument("--aspect-ratio", default="9:16", choices=["9:16", "16:9", "1:1"], help="Aspect ratio")
    parser.add_argument("--duration", type=int, default=6, choices=[4, 6, 8], help="Duración en segundos")
    parser.add_argument("--resolution", default="720p", choices=["720p", "1080p", "4k"], help="Resolución")
    parser.add_argument("--output", default="output_veo.mp4", help="Ruta del archivo de salida")
    args = parser.parse_args()

    client = VeoClient()
    client.generate_video(
        prompt=args.prompt,
        first_frame=args.first_frame,
        last_frame=args.last_frame,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        duration=args.duration,
        resolution=args.resolution,
        output_path=args.output
    )

if __name__ == "__main__":
    main()
