"""Pengenal cakupan pertanyaan: program studi dan angkatan (aturan murni, tanpa LLM).

Data bertingkat: Departemen -> Prodi -> Angkatan -> Mata kuliah semester ini.
Entri FAQ/dokumen boleh diberi `prodi` dan/atau `angkatan`. Pertanyaan yang menyebut prodi/angkatan hanya
akan dicocokkan dengan entri yang cakupannya sama (atau entri umum tanpa cakupan).
"""
import re
from dataclasses import dataclass

# Urutan penting: nama panjang diperiksa dulu agar "Pendidikan Teknik Informatika" tidak terbaca "Informatika".
PRODI_PATTERNS = [
    ("PTI", r"pendidikan teknik informatika|\bpti\b"),
    ("PTE", r"pendidikan teknik elektronika|\bpte\b"),
    ("TRSE", r"teknik rekayasa sistem elektronika|\btrse\b"),
    ("Informatika", r"\binformatika\b"),
]
PRODI_ORDER = ["Informatika", "PTI", "PTE", "TRSE"]
_YEAR = re.compile(r"\b(20[2-3]\d)\b")
_ANGKATAN_EKSPLISIT = re.compile(r"\bangk(?:atan|\.)?\s*(?:tahun\s*)?(20[2-3]\d)\b")


@dataclass(frozen=True)
class Facets:
    prodi: frozenset = frozenset()
    angkatan: frozenset = frozenset()
    angkatan_eksplisit: frozenset = frozenset()   # tahun yang didahului kata 'angkatan'


def detect(text: str) -> Facets:
    t, found = text.lower(), set()
    for name, pattern in PRODI_PATTERNS:
        if re.search(pattern, t):
            found.add(name)
            t = re.sub(pattern, " ", t)          # hapus agar tidak terbaca ganda
    return Facets(frozenset(found), frozenset(int(y) for y in _YEAR.findall(text)),
                  frozenset(int(y) for y in _ANGKATAN_EKSPLISIT.findall(text.lower())))


def canonical_prodi(value) -> str | None:
    found = detect(str(value)).prodi
    return next(iter(found)) if len(found) == 1 else None


def allows(prodi, angkatan, f: Facets) -> bool:
    """Entri bercakupan (prodi, angkatan) boleh dipakai untuk pertanyaan dengan facets f."""
    if f.prodi and prodi and prodi not in f.prodi:
        return False
    if f.angkatan and angkatan and angkatan not in f.angkatan:
        return False
    return True


def canonicalize(text: str) -> str:
    """Seragamkan nama prodi (nama lengkap -> singkatan baku) agar pencocokan TF-IDF konsisten."""
    t = text.lower()
    for name, pattern in PRODI_PATTERNS:
        t = re.sub(pattern, f" {name.lower()} ", t)
    return t
