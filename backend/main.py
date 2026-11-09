from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
from .retrieval import load_index, search

load_dotenv()
app = FastAPI(title="Chatbot Layanan Akademik Prodi", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tfidf_index = load_index()
gemini = (
    genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options=types.HttpOptions(
            timeout=30_000,
            # Local development may inherit an unusable loopback proxy.
            client_args={"trust_env": False},
            async_client_args={"trust_env": False},
        ),
    )
    if os.getenv("GEMINI_API_KEY")
    else None
)
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []

@app.get("/api/health")
def health():
    return {"status": "ok", "gemini_configured": gemini is not None,
            "documents": len(tfidf_index["documents"]) if tfidf_index else 0,
            "retrieval": "tfidf"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    if gemini is None:
        raise HTTPException(503, "GEMINI_API_KEY belum diatur pada file .env.")
    matches = search(tfidf_index, payload.message, limit=4)
    context = "\n\n".join(document for document, _ in matches)
    sources = list(dict.fromkeys(
        str(metadata.get("source", "Dokumen akademik")) for _, metadata in matches
    ))
    if not context:
        context = "Belum ada dokumen akademik yang dimasukkan ke Knowledge Base."
    prompt = f"""
Anda adalah Chatbot Layanan Akademik Program Studi Teknik Informatika.
Jawab dalam Bahasa Indonesia yang sopan, jelas, dan ringkas.
Gunakan konteks dokumen sebagai sumber utama. Jangan mengarang jadwal,
nama dosen, kebijakan, biaya, atau tanggal. Jika informasi tidak tersedia
di konteks, katakan bahwa informasi belum tersedia dan sarankan mahasiswa
menghubungi admin program studi. Bedakan informasi resmi dari saran umum.

KONTEKS DOKUMEN:
{context}

PERTANYAAN MAHASISWA:
{payload.message}
"""
    try:
        response = gemini.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=700),
        )
        answer = response.text or "Maaf, belum ada jawaban yang dapat diberikan."
        return ChatResponse(answer=answer, sources=sources)
    except Exception as exc:
        raise HTTPException(502, f"Gagal menghubungi Gemini API: {type(exc).__name__}")
