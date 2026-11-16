"""Knowledge base lokal: FAQ terverifikasi + dokumen resmi (chunking sadar-heading).

Indeks dibangun saat server start (korpus kecil), jadi tidak ada file pickle yang basi/tidak aman.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import config
from .facets import Facets, PRODI_ORDER, allows, canonical_prodi
from .preprocess import normalize

log = logging.getLogger(__name__)

HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
PLACEHOLDER = re.compile(r"\[\s*(isi|ganti|todo)[^\]]*\]", re.I)
SKIP_PREFIXES = ("contoh", "_")          # file berawalan ini tidak diindeks (template/contoh)
SUPPORTED = {".md", ".txt", ".pdf"}


@dataclass
class Hit:
    text: str
    source: str
    score: float
    section: str | None = None
    page: int | None = None
    faq_id: str | None = None
    coverage: float = 1.0      # porsi kata pertanyaan yang ditemukan di baris FAQ terbaik
    prodi: str | None = None   # cakupan entri (None = umum)
    angkatan: int | None = None

    @property
    def label(self) -> str:
        label = self.source
        if self.section:
            label += f" › {self.section}"
        if self.page:
            label += f" (hlm. {self.page})"
        return label


@dataclass
class Report:
    faq_loaded: int = 0
    faq_skipped: list = field(default_factory=list)      # (id, alasan)
    files_indexed: list = field(default_factory=list)
    files_skipped: list = field(default_factory=list)
    chunks: int = 0
    chunks_placeholder: int = 0
    warnings: list = field(default_factory=list)


class Index:
    def __init__(self, texts: list[str], metas: list[dict]):
        self.texts, self.metas = texts, metas
        self.tokensets = [set(normalize(t).split()) for t in texts]
        self.vectorizer = TfidfVectorizer(
            preprocessor=normalize, tokenizer=str.split, token_pattern=None,
            lowercase=False, ngram_range=(1, 2), sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(texts)

    def scores(self, query: str):
        return cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()


def _make_index(texts, metas):
    if not texts:
        return None
    try:
        return Index(texts, metas)
    except ValueError:  # kosakata kosong setelah normalisasi
        return None


# ---------- chunking ----------

def _split_long(block: str, max_chars: int) -> list[str]:
    out, cur = [], ""
    for sent in re.split(r"(?<=[.!?;])\s+", block):
        while len(sent) > max_chars:                       # kalimat super panjang: potong di spasi
            cut = sent.rfind(" ", 0, max_chars) or max_chars
            out.append(sent[:cut].strip()); sent = sent[cut:].strip()
        if cur and len(cur) + 1 + len(sent) > max_chars:
            out.append(cur); cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        out.append(cur)
    return out


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Potong per paragraf/kalimat (tidak memotong di tengah kata), lalu gabung sampai max_chars."""
    pieces = []
    for block in re.split(r"\n\s*\n", text):
        block = re.sub(r"\s+", " ", block).strip()
        if block:
            pieces.extend([block] if len(block) <= max_chars else _split_long(block, max_chars))
    out, cur = [], ""
    for piece in pieces:
        if cur and len(cur) + 1 + len(piece) > max_chars:
            out.append(cur); cur = piece
        else:
            cur = f"{cur} {piece}".strip()
    if cur:
        out.append(cur)
    return out


def _md_sections(text: str):
    stack, lines, sections = [], [], []

    def flush():
        body = "\n".join(lines).strip()
        if body:
            sections.append((" › ".join(t for _, t in stack) or None, body))
        lines.clear()

    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
        else:
            lines.append(line)
    flush()
    return sections


FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def _front_matter(text: str):
    m = FRONT.match(text)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip().lower()] = v.strip()
        text = text[m.end():]
    return meta, text


def _scope(meta: dict, where: str, report: Report):
    prodi = canonical_prodi(meta["prodi"]) if meta.get("prodi") else None
    if meta.get("prodi") and not prodi:
        report.warnings.append(f"{where}: prodi '{meta['prodi']}' tidak dikenali (pakai Informatika/PTI/PTE/TRSE)")
    angkatan = None
    if meta.get("angkatan"):
        try:
            angkatan = int(meta["angkatan"])
        except ValueError:
            report.warnings.append(f"{where}: angkatan '{meta['angkatan']}' bukan angka")
    return prodi, angkatan


def _read_sections(path: Path, report: Report):
    """Hasil: (meta, daftar (section, page, body))."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader  # import malas: tidak wajib untuk MD/TXT
        out = []
        for n, page in enumerate(PdfReader(str(path)).pages, 1):
            body = (page.extract_text() or "").strip()
            if not body:
                report.warnings.append(f"{path.name} hlm. {n}: tanpa teks (kemungkinan hasil scan, perlu OCR)")
            else:
                out.append((None, n, body))
        return {}, out
    text = path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".md":
        meta, text = _front_matter(text)
        return meta, [(s, None, b) for s, b in _md_sections(text)]
    return {}, [(None, None, text)]


# ---------- knowledge base ----------

class KnowledgeBase:
    def __init__(self, faq_index, faq_entries, doc_index, doc_chunks, report):
        self.faq_index, self.faq_entries = faq_index, faq_entries
        self.doc_index, self.doc_chunks = doc_index, doc_chunks
        self.report = report

    @classmethod
    def load(cls, faq_path: Path = config.FAQ_PATH, docs_dir: Path = config.DOCS_DIR,
             include_draft: bool = config.INCLUDE_DRAFT,
             max_chars: int = config.CHUNK_MAX_CHARS) -> "KnowledgeBase":
        report = Report()
        faq_entries, faq_texts, faq_metas = [], [], []
        if Path(faq_path).is_file():
            for i, e in enumerate(json.loads(Path(faq_path).read_text(encoding="utf-8"))):
                eid = e.get("id") or f"faq-{i}"
                if not e.get("question") or not e.get("answer"):
                    report.faq_skipped.append((eid, "pertanyaan/jawaban kosong")); continue
                if PLACEHOLDER.search(e["answer"]):
                    report.faq_skipped.append((eid, "jawaban masih placeholder")); continue
                if e.get("status", "draft") != "verified" and not include_draft:
                    report.faq_skipped.append((eid, "status belum 'verified'")); continue
                e["prodi"], e["angkatan"] = _scope(e, f"FAQ {eid}", report)
                faq_entries.append(e)
                for q in [e["question"], *e.get("variants", [])]:   # satu baris indeks per variasi pertanyaan
                    faq_texts.append(q); faq_metas.append(len(faq_entries) - 1)
        else:
            report.warnings.append(f"File FAQ tidak ditemukan: {faq_path}")
        report.faq_loaded = len(faq_entries)

        doc_chunks, doc_texts = [], []
        for path in sorted(Path(docs_dir).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED:
                continue
            if path.name.lower().startswith(SKIP_PREFIXES):
                report.files_skipped.append(path.name); continue
            report.files_indexed.append(path.name)
            meta, sections = _read_sections(path, report)
            prodi, angkatan = _scope(meta, path.name, report)
            for section, page, body in sections:
                for piece in chunk_text(body, max_chars):
                    if PLACEHOLDER.search(piece):
                        report.chunks_placeholder += 1; continue
                    doc_texts.append(f"{section}\n{piece}" if section else piece)
                    doc_chunks.append({"source": path.name, "section": section, "page": page,
                                       "prodi": prodi, "angkatan": angkatan})
        report.chunks = len(doc_chunks)

        return cls(_make_index(faq_texts, faq_metas), faq_entries,
                   _make_index(doc_texts, doc_chunks), doc_chunks, report)

    def search_faq(self, query: str, facets: Facets | None = None, k: int = 3) -> list[Hit]:
        facets = facets or Facets()
        if not self.faq_index:
            return []
        q_tokens = set(normalize(query).split())
        best: dict[int, tuple[float, float]] = {}      # entri -> (skor, cakupan) dari baris terbaik
        for row, (score, entry_idx) in enumerate(zip(self.faq_index.scores(query), self.faq_index.metas)):
            e = self.faq_entries[entry_idx]
            if not allows(e["prodi"], e["angkatan"], facets):      # cakupan prodi/angkatan tidak cocok
                continue
            if score > best.get(entry_idx, (0.0, 0.0))[0]:
                cov = len(q_tokens & self.faq_index.tokensets[row]) / len(q_tokens) if q_tokens else 0.0
                best[entry_idx] = (float(score), cov)
        hits = []
        for entry_idx, (score, cov) in sorted(best.items(), key=lambda kv: -kv[1][0])[:k]:
            e = self.faq_entries[entry_idx]
            hits.append(Hit(text=e["answer"], source=e.get("source", "FAQ prodi"),
                            score=score, faq_id=e.get("id"), coverage=cov,
                            prodi=e["prodi"], angkatan=e["angkatan"]))
        return hits

    def search_docs(self, query: str, k: int = config.TOP_K, facets: Facets | None = None) -> list[Hit]:
        facets = facets or Facets()
        if not self.doc_index:
            return []
        scores = self.doc_index.scores(query)
        hits = []
        for pos in scores.argsort()[::-1]:
            if scores[pos] <= 0 or len(hits) >= k:
                break
            m = self.doc_index.metas[pos]
            if not allows(m["prodi"], m["angkatan"], facets):
                continue
            hits.append(Hit(text=self._text(pos), source=m["source"], score=float(scores[pos]),
                            section=m["section"], page=m["page"], prodi=m["prodi"], angkatan=m["angkatan"]))
        return hits

    def facet_options(self) -> tuple[list[str], list[int]]:
        """Prodi dan angkatan yang benar-benar ada di data (untuk pesan klarifikasi)."""
        prodi = {e["prodi"] for e in self.faq_entries if e["prodi"]} | {m["prodi"] for m in self.doc_chunks if m["prodi"]}
        angkatan = {e["angkatan"] for e in self.faq_entries if e["angkatan"]}
        return [p for p in PRODI_ORDER if p in prodi], sorted(angkatan)

    def _text(self, pos: int) -> str:
        return self.doc_index.texts[pos]
