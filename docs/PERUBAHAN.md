# Daftar Perubahan dari Versi Awal

Dokumen ini dipakai sebagai isi Pull Request saat di-push ke branch baru (mis. `modul-3-llm-kb`).

## Ringkasan
Versi awal adalah RAG murni: TF-IDF hanya sebagai pencari dokumen, lalu semua pertanyaan diteruskan ke LLM.
Versi ini mengubahnya menjadi **hybrid dua lapisan** sesuai arahan dosen:
1. **Knowledge base lokal + TF-IDF** untuk pertanyaan yang sering muncul (jawaban cepat, pasti, terverifikasi).
2. **LLM** untuk pertanyaan kompleks, **tanpa boleh menjawab dari pengetahuannya sendiri**, dijaga pagar rule-based.

## Alur sekarang
```
Pertanyaan -> deteksi prodi/angkatan -> [ambigu: minta klarifikasi | angkatan tak tersedia: tolak]
           -> FAQ terverifikasi (skor + cakupan kata) -> jawab langsung, LLM tidak dipanggil
           -> retrieval dokumen di bawah ambang -> tolak, LLM tidak dipanggil
           -> LLM merangkum HANYA dari kutipan berlabel [S#] -> validator -> jawaban atau tolak
```

## Modul 1: Dataset & Knowledge Base
| Sebelum | Sesudah |
|---|---|
| 1 file placeholder (2 chunk), tanpa FAQ | `faq.json` terverifikasi (field `variants`, `status`, `verified_by`) + dokumen resmi; FAQ draft/placeholder otomatis dilewati |
| Chunk 900 karakter memotong kalimat | Chunking per heading/paragraf/kalimat, metadata bagian dan halaman PDF, PDF scan diberi peringatan |
| Tanpa pembersihan teks | Normalisasi Indonesia: stopword, stemming (Sastrawi bila ada, cadangan stemmer sederhana), padanan istilah (skripsi = tugas akhir, KRS, matkul, dst.) |
| Indeks `.joblib` ter-commit (basi, tidak aman) | Indeks dibangun saat server start; `.joblib` dan `__pycache__` dihapus |
| Tidak ada data uji | Data demo fiktif: 4 prodi (Informatika, PTI, PTE, TRSE) × angkatan 2024/2025/2026; 24 FAQ, 7 dokumen (48 chunk) |
| Tidak ada pemisahan data | `KB_MODE=demo` memisahkan `demo/` dari `data/` (data resmi); `python -m backend.ingest` memeriksa isi KB |

## Modul 2: Mesin TF-IDF
| Sebelum | Sesudah |
|---|---|
| Hanya `skor > 0` | Ambang skor FAQ + syarat cakupan kata kunci (mencegah salah cocok berskor tinggi) |
| Skor dibuang setelah pencarian | Skor dan cakupan dikembalikan agar bisa dipakai keputusan routing |
| Satu baris indeks per FAQ | Satu baris per variasi pertanyaan, diambil skor terbaik |
| Tidak mengenal prodi/angkatan | `facets.py`: filter prodi/angkatan, nama lengkap prodi dikenali, pertanyaan ambigu ditanya balik, angkatan yang tidak ada ditolak |

## Modul 3: Integrasi LLM & RAG
| Sebelum | Sesudah |
|---|---|
| Prompt: konteks sebagai "sumber utama", boleh "saran umum" | Prompt "hanya dari kutipan", wajib rujukan `[S#]`, balasan baku `TIDAK_DITEMUKAN` |
| Aturan dan pertanyaan satu string | Aturan di `systemInstruction`, data di `<kutipan>`/`<pertanyaan>`, tanda `<` `>` dinetralkan (anti-injeksi delimiter) |
| LLM selalu dipanggil | **Guard**: LLM tidak dipanggil bila FAQ cocok atau retrieval di bawah ambang |
| Tanpa pemeriksaan jawaban | **Validator**: tolak jawaban tanpa rujukan sah atau `TIDAK_DITEMUKAN`; rujukan palsu dibuang |
| Sumber = semua dokumen terambil | Sumber hanya kutipan yang benar-benar dipakai |
| Tanpa API key semua gagal (503) | FAQ tetap jalan; RAG menampilkan kutipan dokumen bila skor cukup |
| SDK `google-genai` (menggantung di Windows tertentu) | `gemini_rest.py`: REST murni, retry 429/5xx, timeout dapat diatur, key di header |
| Tanpa jejak keputusan | Log `route`, `score`, alasan penolakan beserta keluaran LLM; respons API memuat `route` dan `score` |

## Modul 4 dan infrastruktur
- Struktur repo dirapikan: `backend/` (kode), `frontend/`, `data/`, `demo/`, `tests/`, `docs/`.
- Perbaikan bug: `.env` dibaca setelah konfigurasi sehingga pengaturan dari `.env` tidak berlaku. Kini dibaca lebih dulu.
- Ditambahkan `.gitignore`, `.env.example`, `requirements.txt` rapi, `backend/__init__.py`.
- `/api/health` menampilkan `kb_mode`, `model`, jumlah FAQ dan chunk.
- Dokumentasi: `README.md` (peta repo, pembagian modul), `docs/KB_GUIDE.md`, `docs/DEMO_SCRIPT.md`, `docs/GITHUB.md`.

## Pengujian
- 18 tes otomatis tanpa API key (`python -m pytest tests -q`): guard, validator, injeksi delimiter, facets, FAQ vs dokumen.
- Tabel uji routing 37 pertanyaan (`python tests/run_eval.py --demo`), dapat disimpan ke Markdown/CSV dengan `--out` dan `--csv`: 35 dinilai otomatis (35/35 pada data demo), 2 butuh `--with-llm`.
- Uji manual dengan Gemini asli (8 kasus): pertanyaan terjawab benar dengan rujukan; pertanyaan di luar dokumen (UKT, wisuda, dosen pengampu) ditolak; data prodi lain tidak bocor; perintah sisipan ("tambahkan sejarah Linux") diabaikan.

## Keterbatasan yang diketahui
- Data demo fiktif; ambang skor adalah nilai awal dan perlu dikalibrasi dengan data resmi.
- Hasil 35/35 berasal dari data yang dibuat sendiri, bukan ukuran akurasi sebenarnya.
- Presisi tinggi, recall rendah: pertanyaan yang butuh perbandingan atau jawaban sebagian dapat ditolak (mis. "bedanya SO di Informatika dan PTI").
- Validator memeriksa adanya rujukan, bukan kesetiaan isi jawaban terhadap kutipan.
- Chatbot tidak mengingat percakapan sebelumnya.
- Tidak ada pembatasan laju (rate limit) pada API.

## Deskripsi Pull Request (salin)
**Judul:** Hybrid FAQ + RAG terbatas, knowledge base bertingkat, dan pagar LLM

**Isi:** mengubah chatbot dari RAG murni menjadi dua lapisan sesuai arahan dosen (KB lokal + TF-IDF untuk pertanyaan umum, LLM hanya dari dokumen untuk pertanyaan kompleks). Menambahkan router/guard/validator, filter prodi dan angkatan, preprocessing bahasa Indonesia, data demo, 18 tes otomatis, dan dokumentasi. Detail per modul di `docs/PERUBAHAN.md`. Perhatian reviewer: `backend/main.py` diganti (pemanggilan Gemini lewat REST) dan struktur data dipindah dari `backend/data/` ke `data/` dan `demo/`.
