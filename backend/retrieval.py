"""Pencarian potongan dokumen dengan TF-IDF dan cosine similarity."""

from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


INDEX_PATH = Path(__file__).resolve().parent / "data" / "tfidf_index.joblib"


def build_index(documents: list[str], metadatas: list[dict]) -> dict:
    """Bangun indeks TF-IDF dari dokumen yang sudah dipotong."""
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform(documents)
    return {"vectorizer": vectorizer, "matrix": matrix,
            "documents": documents, "metadatas": metadatas}


def save_index(index: dict, destination: Path = INDEX_PATH) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    joblib.dump(index, temporary)
    temporary.replace(destination)


def load_index(source: Path = INDEX_PATH) -> dict | None:
    if not source.is_file():
        return None
    return joblib.load(source)


def search(index: dict | None, query: str, limit: int = 4) -> list[tuple[str, dict]]:
    """Kembalikan potongan paling relevan; abaikan skor nol/tanpa kecocokan."""
    if not index or not query.strip():
        return []

    query_vector = index["vectorizer"].transform([query])
    scores = cosine_similarity(query_vector, index["matrix"]).ravel()
    ranked = scores.argsort()[::-1]
    matches = []
    for position in ranked:
        if scores[position] <= 0:
            break
        matches.append((index["documents"][position], index["metadatas"][position]))
        if len(matches) >= limit:
            break
    return matches
