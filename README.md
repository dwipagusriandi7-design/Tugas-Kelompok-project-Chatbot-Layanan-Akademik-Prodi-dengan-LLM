# Chatbot Layanan Akademik Prodi Teknik Informatika

Chatbot berbasis Google Gemini API dengan pendekatan Retrieval-Augmented Generation (RAG).
Backend FastAPI, frontend HTML/CSS/JavaScript, dan pencarian dokumen lokal menggunakan TF-IDF.

## Persyaratan
- Python 3.10+
- Git
- API key Gemini dari Google AI Studio

## Instalasi Windows (PowerShell)
```powershell
git clone https://github.com/USERNAME/chatbot-akademik-prodi.git
cd chatbot-akademik-prodi

py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item .env.example .env
notepad .env
```
Isi `GEMINI_API_KEY` pada `.env`. Jangan pernah mengunggah `.env` ke GitHub.

## Menambahkan dokumen akademik
Letakkan dokumen resmi berformat PDF, TXT, atau MD di:
`backend/data/dokumen/`

Kemudian jalankan:
```powershell
python backend/ingest.py
```
Perintah tersebut memotong dokumen, membangun matriks TF-IDF, lalu menyimpan indeks ke `backend/data/tfidf_index.joblib`. Jalankan ulang setiap kali dokumen berubah. Dokumen contoh hanya placeholder. Ganti dengan informasi resmi prodi sebelum digunakan.

## Menjalankan backend
```powershell
uvicorn backend.main:app --reload
```
API berjalan di `http://127.0.0.1:8000`.
Dokumentasi API: `http://127.0.0.1:8000/docs`.

## Menjalankan frontend
Buka terminal kedua:
```powershell
py -m http.server 5500 --directory frontend
```
Buka `http://127.0.0.1:5500`.

## Membuat repository GitHub
Buat repository kosong bernama `chatbot-akademik-prodi`, lalu:
```powershell
git init
git add .
git commit -m "Initial chatbot akademik dengan Gemini dan RAG"
git branch -M main
git remote add origin https://github.com/USERNAME/chatbot-akademik-prodi.git
git push -u origin main
```
Ganti `USERNAME` dengan username GitHub Anda.

## Catatan keamanan dan kualitas
- API key hanya disimpan di `.env`.
- Jangan masukkan data pribadi mahasiswa atau data akademik terbatas ke Knowledge Base publik.
- Batasi akses dokumen dan endpoint ingest untuk penggunaan produksi.
- Jawaban chatbot perlu diverifikasi dan dokumen harus selalu diperbarui.
- Data contoh dalam `backend/data/dokumen` bukan kebijakan resmi kampus.
- Pencarian TF-IDF mencocokkan kata dan frasa, sehingga istilah yang berbeda tetapi bermakna sama mungkin tidak ditemukan.
