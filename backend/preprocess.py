"""Normalisasi teks Bahasa Indonesia untuk TF-IDF.

Fungsi yang sama dipakai untuk dokumen DAN pertanyaan, jadi hasilnya selalu konsisten.
Stemmer: memakai Sastrawi bila terpasang (disarankan), kalau tidak memakai stemmer sederhana.
"""
import re
from functools import lru_cache

from .facets import canonicalize

try:  # pip install Sastrawi
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    _SASTRAWI = StemmerFactory().create_stemmer()
except Exception:
    _SASTRAWI = None

STOPWORDS = frozenset("""
apa apakah bagaimana gimana cara siapa kapan dimana mana berapa mengapa kenapa
yang dan atau untuk dengan dari ke di pada adalah itu ini saya aku kami kita
bisa dapat boleh agar supaya jika bila akan sudah telah ada dalam oleh para
sebagai tersebut mau ingin tolong mohon kak min halo hai pagi siang sore malam
terima kasih apabila serta juga lagi sih dong deh ya nya
""".split())

# Padanan istilah khas kampus. Token asli tetap dipertahankan, padanannya ditambahkan.
# Tim WAJIB melengkapi ini sesuai istilah di dokumen prodi (inilah solusi "skripsi" vs "tugas akhir").
EXPANSIONS = {
    "skripsi": "tugas akhir",
    "ta": "tugas akhir",
    "krs": "kartu rencana studi",
    "khs": "kartu hasil studi",
    "cuti": "cuti akademik",
    "pa": "pembimbing akademik",
    "tu": "tata usaha",
    "password": "kata sandi",
    "matkul": "mata kuliah",
    "mk": "mata kuliah",
    "ai": "kecerdasan buatan",
    "so": "sistem operasi",
    "pbo": "pemrograman berbasis objek",
    "jarkom": "jaringan komputer",
    "yudisium": "kelulusan",
}

_SUFFIXES = ("lah", "kah", "pun", "nya", "kan", "an", "i")
_PREFIXES = ("meng", "meny", "men", "mem", "peng", "peny", "pen", "pem",
             "me", "pe", "ber", "ter", "di", "ke")


def _crude_stem(tok: str) -> str:
    if len(tok) <= 4 or any(c.isdigit() for c in tok):
        return tok
    for _ in range(2):
        for suf in _SUFFIXES:
            if tok.endswith(suf) and len(tok) - len(suf) >= 3:
                tok = tok[: -len(suf)]
                break
    for pre in _PREFIXES:
        if tok.startswith(pre) and len(tok) - len(pre) >= 3:
            return tok[len(pre):]
    return tok


@lru_cache(maxsize=50_000)
def stem(tok: str) -> str:
    if len(tok) <= 3 or any(c.isdigit() for c in tok):
        return tok
    return _SASTRAWI.stem(tok) if _SASTRAWI else _crude_stem(tok)


def normalize(text: str) -> str:
    """lowercase -> buang tanda baca -> tambah padanan istilah -> buang stopword -> stemming."""
    tokens = []
    for tok in re.sub(r"[^a-z0-9]+", " ", canonicalize(text)).split():
        tokens.append(tok)
        tokens.extend(EXPANSIONS.get(tok, "").split())
    return " ".join(stem(t) for t in tokens if t not in STOPWORDS)
