# -*- coding: utf-8 -*-
"""Paczka wydania: zip z gotowym programem.
Nazwy z polskimi literami ("Stwórz prezentację.exe") muszą mieć w zipie flagę UTF-8 - bez niej Eksplorator Windows
rozpakowuje je jako "Stw├│rz prezentacj─Ö.exe" (błąd wydań 1.0.7-1.0.9, test_u_innych.ps1 30.09).
Python zipfile ustawia tę flagę sam dla każdej nazwy spoza ASCII.
    python zip_release.py <folder programu> <plik zip>
"""
import os
import sys
import zipfile

TOP = ["Stwórz prezentację.exe", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "CZYTAJ - jak zrobić prezentację.txt",
       "DK - szablon prezentacji.pptx"]


def main(root, out):
    files = []
    for dp, _dn, fn in os.walk(os.path.join(root, "pliki programu")):
        files += [os.path.join(dp, f) for f in fn]
    files += [os.path.join(root, f) for f in TOP]
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        sys.exit("brak plików: %s" % missing[:5])
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in files:
            z.write(f, os.path.relpath(f, root).replace("\\", "/"))
    with zipfile.ZipFile(out) as z:
        bad = [i.filename for i in z.infolist() if not i.filename.isascii() and not i.flag_bits & 0x800]
    if bad:
        sys.exit("nazwy bez flagi UTF-8: %s" % bad)
    print("zip: %s (%.0f MB, %d plików, polskie nazwy z flagą UTF-8)" % (out, os.path.getsize(out) / 2 ** 20, len(files)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
