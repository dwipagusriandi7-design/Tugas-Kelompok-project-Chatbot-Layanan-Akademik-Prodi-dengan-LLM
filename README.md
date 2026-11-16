# Chatbot Layanan Akademik Prodi

Chatbot hybrid dengan dua lapisan. Backend FastAPI, frontend HTML/CSS/JavaScript, Google Gemini API.

```
Pertanyaan -> [Facets]    deteksi prodi/angkatan: ambigu -> minta klarifikasi, tidak tersedia -> ditolak
           -> [Lapisan 1] FAQ terverifikasi (TF-IDF + cosine, threshold + cakupan kata) -> jawaban langsung, LLM tidak dipanggil
           -> [Guard]     retrieval dokumen di bawah threshold -> pesan "informasi tidak ditemukan", LLM tidak dipanggil
           -> [Lapisan 2] RAG terbatas: LLM merangkum HANYA dari kutipan berlabel [S1], [S2]...
           -> [Validator] jawaban tanpa rujukan sah / "TIDAK_DITEMUKAN" ditolak
```
LLM bukan rule-based, tetapi dijalankan dalam pagar rule-based (router, guard, validator) di `backend/pipeline.py`.

## Peta repository
```
chatbot-akademik/
├── README.md              <- mulai dari sini
├── requirements.txt       dependensi Python
├── .env.example           contoh konfigurasi (salin ke .env, JANGAN upload .env)
├── .gitignore
│
├── backend/               KODE server (tidak berisi data)
│   ├── main.py            API FastAPI + pemanggilan Gemini
│   ├── pipeline.py        router, guard, prompt terbatas, validator   (inti Modul 3)
│   ├── gemini_rest.py     pemanggil Gemini lewat REST (retry, timeout)
│   ├── knowledge_base.py  memuat FAQ + dokumen, chunking, indeks TF-IDF
│   ├── preprocess.py      stopword, stemming, padanan istilah
│   ├── facets.py          pengenal prodi dan angkatan (data bertingkat)
│   ├── config.py          threshold dan pengaturan
│   └── ingest.py          pemeriksa isi knowledge base
│
├── frontend/              antarmuka chat (HTML, CSS, JS)
│
├── data/                  KNOWLEDGE BASE ASLI prodi (isi oleh Modul 1)
│   ├── faq.json
│   ├── dokumen/           dokumen resmi PDF/MD/TXT
│   └── eval_questions.json
│
├── demo/                  KNOWLEDGE BASE DUMMY (fiktif, untuk demo & uji)
│   ├── faq.json
│   ├── dokumen/
│   └── eval_questions.json
│
├── tests/
│   ├── test_pipeline.py   uji pagar LLM tanpa API key
│   └── run_eval.py        tabel uji coba routing
│
└── docs/
    ├── KB_GUIDE.md        cara mengisi knowledge base
    ├── DEMO_SCRIPT.md     skenario demo
    ├── PERUBAHAN.md       daftar perubahan dari versi awal + deskripsi Pull Request
    └── GITHUB.md          panduan upload + checklist
```

### Apa yang di-upload ke GitHub?
| Item | Upload? | Catatan |
|---|---|---|
| `README.md`, `requirements.txt`, `.gitignore`, `.env.example` | Ya | |
| `backend/`, `frontend/`, `tests/`, `docs/` | Ya | |
| `demo/` | Ya | data fiktif, setiap jawaban bertanda `[DATA DEMO]` |
| `data/` | Ya, bila boleh publik | pastikan tidak ada data pribadi atau dokumen terbatas |
| **`.env`** | **JANGAN** | berisi API key |
| `.venv/`, `__pycache__/`, `*.joblib` | **JANGAN** | sudah diabaikan `.gitignore` |

Detail dan perintah git: `docs/GITHUB.md`.

## Pembagian modul
| Modul | Fokus | File utama | Penanggung jawab |
|---|---|---|---|
| 1. Dataset & Knowledge Base | Pengumpulan dan pembersihan data | `data/`, `knowledge_base.py`, `preprocess.py` | [nama] |
| 2. Mesin TF-IDF | Pencocokan FAQ, threshold | `knowledge_base.py`, `config.py` | [nama] |
| 3. Integrasi LLM & RAG | Prompt terbatas, guard, validator | `pipeline.py`, `main.py` | [nama] |
| 4. Backend & Antarmuka | API dan tampilan chat | `main.py`, `frontend/` | [nama] |

Alur kerja tim: satu branch per modul (`modul-1-kb`, `modul-2-tfidf`, ...), digabung ke `main` lewat pull request.

## Persyaratan
- Python 3.10+
- Git
- API key Gemini dari Google AI Studio (opsional untuk mencoba mode demo)

## Instalasi (Windows PowerShell)
```powershell
git clone https://github.com/USERNAME/chatbot-akademik-prodi.git
cd chatbot-akademik-prodi

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Copy-Item .env.example .env
notepad .env
```
Isi `GEMINI_API_KEY` pada `.env`. Jangan pernah mengunggah `.env` ke GitHub.

## Menjalankan
**Mode demo** (data fiktif, langsung bisa dicoba):
```powershell
$env:KB_MODE="demo"
python -m uvicorn backend.main:app --reload
```
**Mode asli** (data resmi di `data/`): jalankan tanpa baris `KB_MODE`.

Server: `http://127.0.0.1:8000`, dokumentasi API: `http://127.0.0.1:8000/docs`, status: `/api/health`
(menampilkan `kb_mode`, jumlah FAQ dan chunk). Respons `/api/chat` memuat `route` (faq / rag / extractive / clarify / refused) dan `score`.
Tanpa `GEMINI_API_KEY`, FAQ tetap berfungsi dan jalur RAG menampilkan kutipan dokumen.

Frontend, di terminal kedua:
```powershell
python -m http.server 5500 --directory frontend
```
Buka `http://127.0.0.1:5500`. Skenario demonstrasi: `docs/DEMO_SCRIPT.md`.

## Mengisi knowledge base asli
Baca `docs/KB_GUIDE.md`. Ringkasnya: FAQ terverifikasi di `data/faq.json`, dokumen resmi di `data/dokumen/`.
Indeks dibangun otomatis saat server start (tidak ada file indeks yang perlu di-commit). Cek isi KB:
```powershell
python -m backend.ingest
```

## Pengujian
```powershell
python -m pytest tests -q                  # uji pagar Modul 3 (tanpa API key)
python tests/run_eval.py --demo            # tabel uji routing dengan data demo
python tests/run_eval.py                   # data asli: isi data/eval_questions.json
python tests/run_eval.py --demo --with-llm # termasuk panggilan Gemini (butuh API key)
```
Menyimpan hasil untuk laporan (Markdown dan CSV, UTF-8; folder dibuat otomatis):
```powershell
python tests/run_eval.py --demo --with-llm --jeda 1 --out docs/hasil_uji/uji_demo_llm.md --csv docs/hasil_uji/uji_demo_llm.csv
python tests/run_eval.py --demo --out docs/hasil_uji/uji_demo_tanpa_llm.md   # tanpa API key
```
`--jeda 1` memberi jeda 1 detik antar panggilan Gemini agar tidak kena batas kuota. Bila satu pertanyaan error,
proses tetap lanjut dan hasil lainnya tetap tersimpan. File `.md` memuat tanggal, model, ambang, tabel, dan cuplikan jawaban;
file `.csv` bisa dibuka di Excel.
Threshold (`FAQ_THRESHOLD`, `DOC_THRESHOLD`, `EXTRACTIVE_THRESHOLD`, `FAQ_MIN_COVERAGE`) adalah nilai awal.
Kalibrasi dengan data prodi asli sebelum dilaporkan sebagai hasil akhir.

## Catatan keamanan dan kualitas
- API key hanya disimpan di `.env`.
- Jangan masukkan data pribadi mahasiswa atau data akademik terbatas ke knowledge base publik.
- Data di `demo/` dan `data/dokumen/CONTOH_*` bukan kebijakan resmi kampus.
- Pertanyaan yang kata-katanya mirip dokumen tetapi jawabannya tidak ada (mis. biaya UKT saat dokumen hanya membahas
  semester) hanya bisa ditolak di tahap LLM + validator. Uji dengan `--with-llm`.
- TF-IDF mencocokkan kata. Istilah berbeda yang bermakna sama harus ditambahkan ke `EXPANSIONS` di `backend/preprocess.py`.
- Jawaban chatbot perlu diverifikasi dan dokumen harus selalu diperbarui.
