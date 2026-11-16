"""Periksa (lint) knowledge base: python -m backend.ingest [--include-draft]

Indeks dibangun otomatis saat server start, jadi perintah ini hanya melaporkan isi KB
dan memperingatkan masalah (placeholder, PDF scan, FAQ belum terverifikasi).
"""
import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config
from backend.knowledge_base import KnowledgeBase


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-draft", action="store_true")
    ap.add_argument("--demo", action="store_true", help="periksa folder demo/ (data fiktif)")
    ap.add_argument("--faq", type=Path, default=config.FAQ_PATH)
    ap.add_argument("--docs", type=Path, default=config.DOCS_DIR)
    a = ap.parse_args()
    if a.demo:
        a.faq, a.docs = config.ROOT / "demo" / "faq.json", config.ROOT / "demo" / "dokumen"
    r = KnowledgeBase.load(a.faq, a.docs, a.include_draft).report
    print(f"FAQ dimuat        : {r.faq_loaded}")
    for eid, why in r.faq_skipped:
        print(f"  - dilewati {eid}: {why}")
    print(f"File diindeks     : {len(r.files_indexed)} {r.files_indexed}")
    print(f"File dilewati     : {r.files_skipped}")
    print(f"Chunk diindeks    : {r.chunks} (dibuang karena placeholder: {r.chunks_placeholder})")
    for w in r.warnings:
        print("PERINGATAN:", w)
    if r.faq_loaded == 0 and r.chunks == 0:
        print("\nKB kosong: semua pertanyaan akan ditolak. Isi data resmi dulu (lihat docs/KB_GUIDE.md).")


if __name__ == "__main__":
    main()
