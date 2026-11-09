"""Bangun indeks TF-IDF dari dokumen .txt, .md, dan .pdf."""
from pathlib import Path

from pypdf import PdfReader

if __package__:
    from .retrieval import build_index, save_index
else:
    from retrieval import build_index, save_index

BASE = Path(__file__).resolve().parent
DOCS = BASE / "data" / "dokumen"
DOCS.mkdir(parents=True, exist_ok=True)

def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="ignore")

def chunks(text: str, size: int = 900, overlap: int = 120):
    text = " ".join(text.split())
    start = 0
    while start < len(text):
        yield text[start:start + size]
        start += size - overlap

def main():
    documents, metadatas = [], []
    for path in DOCS.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md", ".pdf"}:
            content = read_file(path)
            for index, chunk in enumerate(chunks(content)):
                if chunk.strip():
                    documents.append(chunk)
                    metadatas.append({"source": path.name, "chunk": index})
    if not documents:
        print("Belum ada dokumen. Tambahkan file PDF/TXT/MD ke backend/data/dokumen.")
        return
    index = build_index(documents, metadatas)
    save_index(index, BASE / "data" / "tfidf_index.joblib")
    print(f"Berhasil membangun indeks TF-IDF dari {len(documents)} potongan dokumen.")

if __name__ == "__main__":
    main()
