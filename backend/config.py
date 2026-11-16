"""Konfigurasi terpusat. Semua nilai bisa diubah lewat environment variable atau file .env."""
import os
from pathlib import Path

try:  # .env harus terbaca SEBELUM nilai di bawah dibaca
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent

# Mode knowledge base: "real" = folder data/ (data resmi prodi), "demo" = folder demo/ (data FIKTIF)
KB_MODE = os.getenv("KB_MODE", "real").strip().lower()
KB_DIR = ROOT / ("demo" if KB_MODE == "demo" else "data")
FAQ_PATH = KB_DIR / "faq.json"
DOCS_DIR = KB_DIR / "dokumen"

# Ambang batas awal. WAJIB dikalibrasi dengan data prodi asli memakai tests/run_eval.py.
FAQ_THRESHOLD = float(os.getenv("FAQ_THRESHOLD", "0.50"))  # >= ini: jawab langsung dari FAQ, LLM tidak dipanggil
DOC_THRESHOLD = float(os.getenv("DOC_THRESHOLD", "0.15"))  # < ini: tolak, LLM tidak dipanggil
# Tanpa LLM tidak ada lapis pengaman kedua, jadi kutipan hanya ditampilkan bila retrieval cukup yakin
EXTRACTIVE_THRESHOLD = float(os.getenv("EXTRACTIVE_THRESHOLD", "0.20"))
# Minimal porsi kata penting pertanyaan yang harus ada di pertanyaan FAQ (cegah salah cocok berskor tinggi)
FAQ_MIN_COVERAGE = float(os.getenv("FAQ_MIN_COVERAGE", "0.60"))
TOP_K = int(os.getenv("TOP_K", "4"))
CHUNK_MAX_CHARS = int(os.getenv("CHUNK_MAX_CHARS", "900"))

# FAQ berstatus "draft" hanya dipakai bila diaktifkan.
INCLUDE_DRAFT = os.getenv("INCLUDE_DRAFT_KB", "0") == "1"

NOT_FOUND_MESSAGE = (
    "Mohon maaf, informasi tersebut belum tersedia di dokumen resmi program studi. "
    "Silakan hubungi admin program studi untuk kepastian."
)
