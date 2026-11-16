# Panduan Upload ke GitHub

## Checklist sebelum commit pertama
- [ ] `data/faq.json` dan `data/dokumen/` berisi data resmi yang **boleh dipublikasikan** (atau dibiarkan template)
- [ ] Tidak ada data pribadi mahasiswa/dosen di `data/`
- [ ] `.env` TIDAK ikut ter-commit (cek perintah di bawah)
- [ ] `python -m pytest tests -q` lulus
- [ ] `USERNAME` pada README sudah diganti
- [ ] Kolom "Penanggung jawab" pada README sudah diisi

## Perintah
```powershell
git init
git status                                   # pastikan .env, .venv, __pycache__ TIDAK muncul
git add .
git ls-files | Select-String "\.env$"        # harus kosong; .env.example boleh
git commit -m "Chatbot akademik: hybrid FAQ + RAG terbatas"
git branch -M main
git remote add origin https://github.com/USERNAME/chatbot-akademik-prodi.git
git push -u origin main
```

## Kerja kelompok
```powershell
git checkout -b modul-3-llm       # satu branch per modul
git add backend/pipeline.py backend/main.py
git commit -m "Modul 3: guard dan validator"
git push -u origin modul-3-llm    # lalu buat Pull Request di GitHub
```
Hindari dua orang mengedit file yang sama sekaligus (terutama `main.py` dan `knowledge_base.py`). Bagi file sesuai tabel pembagian modul di README.

## Jika API key terlanjur ter-upload
Menghapus file saja tidak cukup karena key masih ada di riwayat commit. Langkah yang benar:
1. **Cabut dan buat ulang key** di Google AI Studio (lakukan ini lebih dulu).
2. Baru bersihkan riwayat git bila perlu.
