import os
from groq import Groq
import httpx

API_KEY = os.getenv("GROQ_API_KEY")
# Proveer http_client explícito para evitar que el SDK construya uno con kwargs incompatibles
_http_client = httpx.Client(timeout=30.0)
client = Groq(api_key=API_KEY, http_client=_http_client) if API_KEY else None

class GroqClientError(Exception):
    pass

def _ensure_client():
    if not API_KEY:
        raise GroqClientError("GROQ_API_KEY no configurada")
    if client is None:
        raise GroqClientError("Cliente de Groq no inicializado")

def ask_groq(prompt: str) -> str:
    _ensure_client()
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        choice = response.choices[0]
        # Soportar tanto acceso por atributo como por dict si varía la lib
        msg = getattr(choice, "message", None)
        if msg is not None:
            content = getattr(msg, "content", None)
            if content is not None:
                return content
            # fallback si message es dict-like
            try:
                return msg["content"]
            except Exception:
                pass
        # Fallback directo si estructura es diferente
        try:
            return choice["message"]["content"]
        except Exception:
            raise GroqClientError("Formato de respuesta de Groq no reconocido")
    except Exception as e:
        raise GroqClientError(f"Error consultando Groq: {e}") from e
