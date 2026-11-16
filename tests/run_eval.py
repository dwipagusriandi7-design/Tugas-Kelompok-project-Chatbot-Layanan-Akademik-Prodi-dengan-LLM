"""Tabel uji coba routing, dapat disimpan ke file untuk laporan.

  python tests/run_eval.py --demo                                   # data fiktif di demo/
  python tests/run_eval.py                                          # data asli di data/ (isi data/eval_questions.json)
  python tests/run_eval.py --demo --with-llm --jeda 1 --out docs/hasil_uji/uji_demo_llm.md --csv docs/hasil_uji/uji_demo_llm.csv

Tanpa --with-llm, jalur RAG dievaluasi sampai tahap retrieval (hasil 'extractive' dihitung 'rag').
Pertanyaan bertanda "needs_llm": true hanya dinilai dengan --with-llm (penolakannya terjadi di tahap LLM + validator).
Bila satu pertanyaan error (mis. Gemini sibuk), proses berlanjut dan hasil lain tetap tersimpan.
"""
import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend import config                      # noqa: E402
from backend.knowledge_base import KnowledgeBase  # noqa: E402
from backend.pipeline import respond            # noqa: E402


def with_cache(llm, model, path):
    """Simpan keluaran LLM ke file; pertanyaan yang sama (prompt identik) tidak memanggil API lagi.
    Berguna saat kuota harian kecil: uji ulang atau lanjutan setelah kuota habis tidak memboroskan permintaan."""
    store = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    stats = {"hit": 0, "miss": 0}

    def wrapped(system, user):
        key = hashlib.sha256(f"{model}\n{system}\n{user}".encode("utf-8")).hexdigest()
        if key in store:
            wrapped.last_cached = True
            stats["hit"] += 1
            return store[key]
        wrapped.last_cached = False
        out = llm(system, user)                       # bila error, tidak tersimpan dan error diteruskan
        stats["miss"] += 1
        if out is not None:
            store[key] = out
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(store, ensure_ascii=False), encoding="utf-8")   # simpan tiap panggilan
        return out

    wrapped.last_cached = False
    return wrapped, stats


def run(kb, items, llm=None, jeda=0.0):
    """Jalankan semua pertanyaan; kembalikan daftar baris hasil."""
    rows, calls = [], {"n": 0}
    _inner = llm
    if llm is not None:                                  # hitung panggilan LLM sebenarnya
        def llm(system, user):                           # noqa: F811
            calls["n"] += 1
            return _inner(system, user)
    for i, item in enumerate(items, 1):
        before = calls["n"]
        q, expected = item["q"], item["expected"]
        row = {"no": i, "q": q, "expected": expected, "got": "-", "score": None, "status": "", "answer": ""}
        if q.startswith("[ISI"):
            continue
        if item.get("needs_llm") and llm is None:
            row["status"] = "dilewati (butuh --with-llm)"
            rows.append(row); continue
        try:
            res = respond(q, kb, llm)
        except Exception as exc:                      # satu error tidak boleh menghentikan seluruh uji
            row["got"], row["status"], row["answer"] = "error", "error", type(exc).__name__
            rows.append(row)
        else:
            row["got"] = "rag" if res.route in ("rag", "extractive") else res.route
            row["score"] = res.score
            row["status"] = "OK" if row["got"] == expected else "SALAH"
            row["answer"] = res.answer
            rows.append(row)
        if jeda and calls["n"] > before and not getattr(_inner, "last_cached", False):
            time.sleep(jeda)                              # jeda hanya setelah panggilan API sungguhan (bukan dari cache)
    return rows


def summarize(rows):
    ok = sum(r["status"] == "OK" for r in rows)
    wrong = sum(r["status"] == "SALAH" for r in rows)
    skipped = sum(r["status"].startswith("dilewati") for r in rows)
    errors = sum(r["status"] == "error" for r in rows)
    return ok, ok + wrong, skipped, errors


def _icon(status):
    return {"OK": "✅", "SALAH": "❌", "error": "⚠️ error"}.get(status, "⏭ " + status)


def render(rows, header_lines, with_answer=False):
    ok, total, skipped, errors = summarize(rows)
    cols = "| No | Pertanyaan | Harapan | Hasil | Skor | Status |" + (" Cuplikan jawaban |" if with_answer else "")
    sep = "|---|---|---|---|---|---|" + ("---|" if with_answer else "")
    lines = [*header_lines, "", cols, sep]
    for r in rows:
        score = "-" if r["score"] is None else f"{r['score']:.2f}"
        line = f"| {r['no']} | {r['q']} | {r['expected']} | {r['got']} | {score} | {_icon(r['status'])} |"
        if with_answer:
            snippet = r["answer"].replace("\n", " ").replace("|", "/")
            line += f" {snippet[:90]}{'…' if len(snippet) > 90 else ''} |"
        lines.append(line)
    pct = 100 * ok / total if total else 0
    lines += ["", f"Akurasi routing: {ok}/{total} = {pct:.0f}%  (dilewati: {skipped}, error: {errors})"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Tabel uji coba routing chatbot")
    ap.add_argument("--demo", action="store_true", help="pakai data fiktif di demo/")
    ap.add_argument("--questions", type=Path)
    ap.add_argument("--with-llm", action="store_true", help="sertakan panggilan Gemini (butuh API key)")
    ap.add_argument("--jeda", type=float, default=0.0, help="jeda detik setelah tiap panggilan LLM (mis. 7 untuk batas 10 permintaan/menit)")
    ap.add_argument("--cache", type=Path, help="file cache keluaran LLM (mis. .cache/llm.json) agar uji ulang tidak memakai kuota lagi")
    ap.add_argument("--out", type=Path, help="simpan tabel sebagai Markdown (UTF-8), mis. docs/hasil_uji/uji_demo.md")
    ap.add_argument("--csv", type=Path, help="simpan juga sebagai CSV (untuk Excel)")
    a = ap.parse_args()

    base = ROOT / ("demo" if (a.demo or config.KB_MODE == "demo") else "data")
    kb = KnowledgeBase.load(base / "faq.json", base / "dokumen")
    qfile = a.questions or base / "eval_questions.json"
    llm, model = None, "-"
    if a.with_llm:
        from backend.main import MODEL, call_gemini
        llm, model = call_gemini, MODEL
        if a.cache:
            llm, stats = with_cache(llm, model, a.cache)

    items = json.loads(qfile.read_text(encoding="utf-8"))
    rows = run(kb, items, llm, a.jeda)
    if not rows:
        print("Belum ada pertanyaan uji. Isi", qfile); return

    header = [
        "# Hasil Uji Routing", "",
        f"- Tanggal: {datetime.now():%Y-%m-%d %H:%M}",
        f"- Basis data: {base.name}/ ({len(kb.faq_entries)} FAQ, {kb.report.chunks} chunk)",
        f"- Mode: {'dengan LLM, model ' + model if llm else 'tanpa LLM (retrieval saja)'}",
        f"- Ambang: FAQ={config.FAQ_THRESHOLD}, DOC={config.DOC_THRESHOLD}, "
        f"EXTRACTIVE={config.EXTRACTIVE_THRESHOLD}, COVERAGE={config.FAQ_MIN_COVERAGE}",
    ]
    print(render(rows, header[2:]))                      # layar: ringkas, tanpa judul dan cuplikan

    if a.with_llm and a.cache:
        print(f"\nCache LLM: {stats['hit']} dari cache, {stats['miss']} panggilan API baru")
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(render(rows, header, with_answer=True) + "\n", encoding="utf-8")
        print(f"\nTersimpan: {a.out}")
    if a.csv:
        a.csv.parent.mkdir(parents=True, exist_ok=True)
        with a.csv.open("w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig agar terbaca benar di Excel
            w = csv.writer(f)
            w.writerow(["no", "pertanyaan", "harapan", "hasil", "skor", "status", "jawaban"])
            for r in rows:
                w.writerow([r["no"], r["q"], r["expected"], r["got"],
                            "" if r["score"] is None else round(r["score"], 3), r["status"], r["answer"]])
        print(f"Tersimpan: {a.csv}")


if __name__ == "__main__":
    main()
