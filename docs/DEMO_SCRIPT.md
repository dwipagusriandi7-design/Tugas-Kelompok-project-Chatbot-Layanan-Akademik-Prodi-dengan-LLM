# Skenario Demo

Siapkan mode demo (data fiktif):
```powershell
$env:KB_MODE="demo"
python -m uvicorn backend.main:app --reload
python -m http.server 5500 --directory frontend    # terminal kedua
```
Cek `http://127.0.0.1:8000/api/health`: `kb_mode` harus `DEMO`, `faq_entries` 24, `doc_chunks` 48.

Data demo: 4 prodi (Informatika, PTI, PTE, TRSE) × angkatan 2024/2025/2026 (semester 5/3/1), dengan daftar mata kuliah
semester ini, ditambah pedoman tugas akhir, PKL, kurikulum, dan deskripsi mata kuliah per prodi. Semua fiktif.

| # | Ketik di chat | Jalur | Yang ditunjukkan |
|---|---|---|---|
| 1 | `gimana cara isi krs` | `faq` | Pertanyaan umum dijawab cepat tanpa LLM |
| 2 | `mau cuti semester nih` | `faq` | Bahasa sehari-hari tetap cocok |
| 3 | `mata kuliah informatika angkatan 2025 semester ini apa aja` | `faq` | Jawaban dipilih sesuai prodi dan angkatan |
| 4 | `mata kuliah semester ini apa saja?` | `clarify` | Pertanyaan ambigu: sistem meminta prodi dan angkatan |
| 5 | `matkul PTI angkatan 2023` | `refused` | Angkatan yang tidak ada di data tidak dijawab dengan data angkatan lain |
| 6 | `Berapa SKS dan prasyarat Sistem Operasi untuk Informatika?` | `rag` | Pertanyaan kompleks dijawab dari dokumen prodi yang tepat |
| 7 | `Berapa SKS Sistem Operasi?` | `clarify` | Jawaban beda tiap prodi (Informatika 3 SKS, PTI 2 SKS pada data demo) |
| 8 | `Siapa presiden Indonesia?` | `refused` | Pengetahuan umum ditolak, LLM tidak dipanggil |

Catatan:
- Tanpa API key, #6 menampilkan kutipan dokumen apa adanya (`extractive`). Dengan key, jawaban disusun Gemini dan memuat rujukan `[S1]`.
- Tambahan bila memakai API key: `Berapa biaya UKT semester ini?` dan `Kapan jadwal wisuda?`. Retrieval menemukan kata mirip,
  jadi penolakan bergantung pada LLM yang membalas `TIDAK_DITEMUKAN` dan validator. Ini bukti pagar berlapis bekerja.
- Jalankan `python tests/run_eval.py --demo --out docs/hasil_uji/uji_demo.md` untuk menyimpan tabel 37 pertanyaan uji sebagai lampiran laporan (tambahkan `--with-llm --jeda 1` bila memakai Gemini).
