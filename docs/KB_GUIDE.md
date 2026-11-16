# Panduan Mengisi Knowledge Base (untuk Modul 1)

## 1. FAQ terverifikasi: `data/faq.json`
Dipakai Lapisan 1 (jawaban cepat tanpa LLM). Satu entri = satu pertanyaan umum.

| Field | Wajib | Keterangan |
|---|---|---|
| `id` | ya | unik, mis. `krs-cara` |
| `question` | ya | pertanyaan utama, bahasa mahasiswa |
| `variants` | disarankan | 3-5 cara lain menanyakan hal yang sama (inilah yang menaikkan akurasi TF-IDF) |
| `answer` | ya | salin dari dokumen resmi, jangan diparafrase dari ingatan |
| `source` | ya | nama dokumen + halaman |
| `status` | ya | `verified` hanya setelah dicek orang yang berwenang; selain itu tidak dipakai |
| `verified_by`, `verified_at` | disarankan | jejak verifikasi untuk laporan |

### Data bertingkat: Departemen → Prodi → Angkatan → Mata kuliah
Untuk informasi yang berbeda per prodi/angkatan (mis. mata kuliah semester ini), beri entri dua field tambahan:
`"prodi": "Informatika"` (pilihan: Informatika, PTI, PTE, TRSE) dan `"angkatan": 2025`. Entri tanpa field itu dianggap umum.
Perilaku sistem:
- Pertanyaan yang menyebut prodi/angkatan hanya dicocokkan dengan entri yang cakupannya sama.
- Pertanyaan yang **tidak** menyebutnya padahal jawabannya berbeda-beda dijawab dengan permintaan klarifikasi.
- Angkatan yang disebut eksplisit ("angkatan 2023") tetapi tidak ada di data ditolak, bukan dijawab dengan angkatan lain.
- Nama lengkap prodi dikenali ("Pendidikan Teknik Informatika" = PTI). Singkatan lain ditambahkan di `backend/facets.py`.

Entri yang `status`-nya bukan `verified`, atau jawabannya masih `[ISI ...]`, otomatis dilewati.

## 2. Dokumen resmi: `data/dokumen/` (PDF / MD / TXT)
Dipakai Lapisan 2 (RAG). Agar retrieval bagus:
- Satu topik per bagian, beri **heading** yang jelas (`## Syarat Seminar Proposal`). Heading ikut diindeks dan ikut dikutip.
- Tulis istilah lengkap sekaligus singkatannya: "Kartu Rencana Studi (KRS)".
- Pakai satu istilah baku untuk satu konsep; tambahkan padanannya di `EXPANSIONS` (`backend/preprocess.py`).
- Hindari tabel di dalam PDF (teksnya berantakan saat diekstrak); salin ke MD bila penting.
- PDF hasil scan tidak terbaca: lakukan OCR dulu.
- Dokumen khusus satu prodi diberi header di baris paling atas:
  ```
  ---
  prodi: Informatika
  ---
  ```
  (boleh ditambah `angkatan: 2025`). Dokumen tanpa header berlaku untuk semua prodi.
- File berawalan `contoh` atau `_` tidak diindeks. Teks yang mengandung `[Isi ...]` dibuang.

## 3. Cek hasilnya
```
python -m backend.ingest          # data asli
python -m backend.ingest --demo   # data demo
```
