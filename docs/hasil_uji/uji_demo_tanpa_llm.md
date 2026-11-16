# Hasil Uji Routing

- Tanggal: 2026-11-16 11:41
- Basis data: demo/ (24 FAQ, 50 chunk)
- Mode: tanpa LLM (retrieval saja)
- Ambang: FAQ=0.5, DOC=0.15, EXTRACTIVE=0.25, COVERAGE=0.6

| No | Pertanyaan | Harapan | Hasil | Skor | Status | Cuplikan jawaban |
|---|---|---|---|---|---|---|
| 1 | gimana cara isi krs | faq | faq | 1.00 | ✅ | [DATA DEMO] KRS diisi melalui portal akademik pada periode pengisian KRS yang tercantum di… |
| 2 | mau revisi krs bisa kapan | faq | faq | 1.00 | ✅ | [DATA DEMO] Perubahan KRS dilakukan pada masa revisi melalui portal akademik dan perlu per… |
| 3 | prosedur cuti kuliah gimana | faq | faq | 1.00 | ✅ | [DATA DEMO] Cuti akademik diajukan melalui portal akademik sebelum batas waktu yang diteta… |
| 4 | jam buka admin prodi kapan ya | faq | faq | 0.61 | ✅ | [DATA DEMO] Layanan administrasi prodi buka Senin sampai Jumat pukul 08.00-15.00. |
| 5 | ruang TU prodi dimana | faq | faq | 0.88 | ✅ | [DATA DEMO] Ruang tata usaha prodi berada di Gedung Demo lantai 2. |
| 6 | apa syarat ambil skripsi | faq | faq | 0.88 | ✅ | [DATA DEMO] Syarat mengambil tugas akhir mengikuti Pedoman Tugas Akhir prodi, termasuk jum… |
| 7 | siapa dosen PA saya | faq | faq | 1.00 | ✅ | [DATA DEMO] Nama dosen pembimbing akademik dapat dilihat pada menu data mahasiswa di porta… |
| 8 | cara daftar beasiswa | faq | faq | 1.00 | ✅ | [DATA DEMO] Pendaftaran beasiswa dilakukan melalui portal beasiswa fakultas pada periode y… |
| 9 | minta surat keterangan aktif kuliah | faq | faq | 1.00 | ✅ | [DATA DEMO] Surat keterangan aktif kuliah diajukan melalui portal akademik dan dapat diamb… |
| 10 | cetak transkrip nilai gimana | faq | faq | 0.76 | ✅ | [DATA DEMO] Transkrip nilai dapat diunduh dari portal akademik atau diajukan cetak resmi k… |
| 11 | lupa password portal akademik | faq | faq | 0.81 | ✅ | [DATA DEMO] Gunakan menu lupa kata sandi di halaman login portal akademik, atau hubungi ta… |
| 12 | Apa saja tahapan tugas akhir dari awal sampai sidang? | rag | rag | 0.43 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Tugas … |
| 13 | Siapa saja yang menguji sidang akhir dan bagaimana komposisi nilainya? | rag | rag | 0.34 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Tugas … |
| 14 | Berapa lama waktu revisi setelah sidang akhir dan apa yang dikumpulkan? | rag | rag | 0.43 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Tugas … |
| 15 | Apa syarat mengikuti seminar proposal? | rag | rag | 0.43 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Tugas … |
| 16 | Apa tujuan praktik kerja lapangan? | rag | rag | 0.54 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Prakti… |
| 17 | Berapa lama PKL dilaksanakan dan siapa pembimbingnya? | rag | rag | 0.30 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Prakti… |
| 18 | Bagaimana komponen penilaian mata kuliah? | rag | rag | 0.30 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Kuriku… |
| 19 | Apa aturan mata kuliah prasyarat? | rag | rag | 0.39 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Pedoman Kuriku… |
| 20 | Siapa presiden Indonesia? | refused | refused | 0.00 | ✅ | Mohon maaf, informasi tersebut belum tersedia di dokumen resmi program studi. Silakan hubu… |
| 21 | Apa itu machine learning? | refused | refused | 0.00 | ✅ | Mohon maaf, informasi tersebut belum tersedia di dokumen resmi program studi. Silakan hubu… |
| 22 | Resep nasi goreng enak | refused | refused | 0.00 | ✅ | Mohon maaf, informasi tersebut belum tersedia di dokumen resmi program studi. Silakan hubu… |
| 23 | halo | refused | refused | 0.00 | ✅ | Mohon maaf, informasi tersebut belum tersedia di dokumen resmi program studi. Silakan hubu… |
| 24 | Berapa biaya UKT semester ini? | refused | - | - | ⏭ dilewati (butuh --with-llm) |  |
| 25 | Kapan jadwal wisuda? | refused | - | - | ⏭ dilewati (butuh --with-llm) |  |
| 26 | mata kuliah informatika angkatan 2025 semester ini apa aja | faq | faq | 0.91 | ✅ | [DATA DEMO] Mata kuliah semester ini untuk Informatika angkatan 2025 (semester 3): Kecerda… |
| 27 | matkul TRSE 2026 | faq | faq | 0.78 | ✅ | [DATA DEMO] Mata kuliah semester ini untuk Teknik Rekayasa Sistem Elektronika (TRSE) angka… |
| 28 | Pendidikan Teknik Informatika angkatan 2024 mata kuliahnya apa | faq | faq | 0.71 | ✅ | [DATA DEMO] Mata kuliah semester ini untuk Pendidikan Teknik Informatika (PTI) angkatan 20… |
| 29 | mata kuliah PTE angkatan 2025 apa saja | faq | faq | 0.74 | ✅ | [DATA DEMO] Mata kuliah semester ini untuk Pendidikan Teknik Elektronika (PTE) angkatan 20… |
| 30 | mata kuliah semester ini apa saja? | clarify | clarify | 0.00 | ✅ | Pertanyaan ini jawabannya berbeda untuk tiap program studi (Informatika, PTI, PTE, TRSE) d… |
| 31 | matkul informatika semester ini apa aja | clarify | clarify | 0.00 | ✅ | Pertanyaan ini jawabannya berbeda untuk tiap angkatan (2024, 2025, 2026). Mohon sebutkan d… |
| 32 | matkul angkatan 2025 apa saja | clarify | clarify | 0.00 | ✅ | Pertanyaan ini jawabannya berbeda untuk tiap program studi (Informatika, PTI, PTE, TRSE). … |
| 33 | matkul PTI angkatan 2023 | refused | refused | 0.00 | ✅ | Data untuk angkatan 2023 belum tersedia. Angkatan yang tersedia: 2024, 2025, 2026. |
| 34 | Berapa SKS dan prasyarat Sistem Operasi untuk Informatika? | rag | rag | 0.47 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Deskripsi Mata… |
| 35 | Bagaimana penilaian mata kuliah Kecerdasan Buatan di Informatika? | rag | rag | 0.47 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Deskripsi Mata… |
| 36 | Apa topik Sistem Operasi di PTI? | rag | rag | 0.51 | ✅ | Layanan penyusun jawaban belum aktif. Kutipan dokumen yang paling relevan:  Deskripsi Mata… |
| 37 | Berapa SKS Sistem Operasi? | clarify | clarify | 0.00 | ✅ | Pertanyaan ini jawabannya berbeda untuk tiap program studi (Informatika, PTI, PTE, TRSE). … |

Akurasi routing: 35/35 = 100%  (dilewati: 2, error: 0)
