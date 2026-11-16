import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import config  # memuat .env lebih dulu
from .gemini_rest import GeminiRestError, generate
from .knowledge_base import KnowledgeBase
from .pipeline import LLMError, respond

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("chatbot")

app = FastAPI(title="Chatbot Layanan Akademik Prodi", version="2.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kb = KnowledgeBase.load()
log.info("KB_MODE=%s | FAQ=%d | chunk=%d", config.KB_MODE, kb.report.faq_loaded, kb.report.chunks)

API_KEY = os.getenv("GEMINI_API_KEY") or None
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
TIMEOUT = float(os.getenv("GEMINI_TIMEOUT", "60"))


def call_gemini(system: str, user: str) -> str | None:
    """Panggilan REST langsung (tanpa SDK). Aturan dipisah dari data pengguna lewat systemInstruction."""
    try:
        return generate(system, user, model=MODEL, api_key=API_KEY, timeout=TIMEOUT)
    except GeminiRestError as exc:
        raise LLMError(str(exc)) from exc


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
    route: str = ""          # faq | rag | extractive | clarify | refused (berguna untuk tabel pengujian)
    score: float = 0.0


@app.get("/api/health")
def health():
    return {"status": "ok", "kb_mode": config.KB_MODE.upper(), "gemini_configured": bool(API_KEY),
            "model": MODEL, "faq_entries": kb.report.faq_loaded, "doc_chunks": kb.report.chunks,
            "retrieval": "tfidf"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    try:
        result = respond(payload.message, kb, call_gemini if API_KEY else None)
    except LLMError as exc:
        raise HTTPException(502, f"Gagal menghubungi Gemini API: {exc}")
    return ChatResponse(answer=result.answer, sources=result.sources,
                        route=result.route, score=round(result.score, 3))
