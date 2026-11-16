"""Pemanggil Gemini lewat REST murni (stdlib). Tanpa SDK, jadi mengikuti pengaturan proxy/sistem Windows
seperti PowerShell/browser. Dipakai sebagai pengganti google-genai bila SDK menggantung."""
import json
import logging
import re
import time
import urllib.error
import urllib.request

log = logging.getLogger(__name__)
BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiRestError(Exception):
    pass


def _retry_delay(exc, detail: str, default: float = 15.0, cap: float = 65.0) -> float:
    """Baca jeda yang diminta Google (header Retry-After atau retryDelay di badan error), dibatasi cap."""
    hdr = exc.headers.get("Retry-After") if exc.headers else None
    if hdr and hdr.replace(".", "", 1).isdigit():
        return min(float(hdr) + 1, cap)
    m = re.search(r'"retryDelay"\s*:\s*"(\d+(?:\.\d+)?)s"', detail)
    return min(float(m.group(1)) + 1, cap) if m else default


def generate(system: str, user: str, *, model: str, api_key: str, timeout: float = 60,
             temperature: float = 0.1, max_tokens: int = 1024, retries: int = 2, base_url: str = BASE) -> str | None:
    """Kembalikan teks jawaban, atau None bila kandidat kosong (mis. diblokir)."""
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/{model}:generateContent", data=body, method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key})   # key di header, bukan di URL

    last = "tidak diketahui"
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            log.info("Gemini modelVersion=%s (diminta: %s)", data.get("modelVersion"), model)   # model yang benar-benar melayani
            parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
            return text or None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "ignore")[:2000]
            last = f"HTTP {exc.code}"
            log.warning("Gemini %s (percobaan %d/%d): %s", exc.code, attempt + 1, retries + 1, detail[:200])
            if exc.code not in (429, 500, 502, 503, 504):
                raise GeminiRestError(last) from exc          # 400/401/403/404: percuma diulang
            if exc.code == 429:
                if "perday" in detail.lower().replace("_", "").replace(" ", ""):
                    raise GeminiRestError("429 kuota HARIAN habis (RPD): ulangi besok, ganti model, atau aktifkan billing") from exc
                wait = _retry_delay(exc, detail)               # kuota per menit: tunggu sesuai arahan Google
                if attempt < retries:
                    log.warning("Gemini 429: menunggu %.0f detik sesuai retryDelay", wait)
                    time.sleep(wait)
                    continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = type(exc).__name__
            log.warning("Gemini jaringan/timeout (percobaan %d/%d): %s", attempt + 1, retries + 1, exc)
        if attempt < retries:
            time.sleep(2 * (attempt + 1))
    raise GeminiRestError(last)
