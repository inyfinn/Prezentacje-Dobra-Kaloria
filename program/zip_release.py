# -*- coding: utf-8 -*-
"""Paczka wydania: zip z gotowym programem.
Układ zipa = układ folderu programu od 1.3: na wierzchu Prezentacje.exe i paczka dla AI, reszta w WORK ("WORK/pliki programu" itd.).
Nazwy z polskimi literami ("Stwórz prezentację.exe", "DK - paczka ...") muszą mieć w zipie flagę UTF-8 - bez niej Eksplorator Windows
rozpakowuje je jako "Stw├│rz prezentacj─Ö.exe" (błąd wydań 1.0.7-1.0.9, test_u_innych.ps1 30.09).
Python zipfile ustawia tę flagę sam dla każdej nazwy spoza ASCII.
    python zip_release.py <folder programu> <plik zip> [--stary]
--stary: wydanie PRZEJŚCIOWE w starym układzie (Stwórz prezentację.exe, pliki programu i skille na wierzchu zipa; plik startowy to ten sam
nowy Prezentacje.exe pod starą nazwą). Tylko takie wydanie zaktualizuje programy do 1.2.x (ich skrypt aktualizacji zna wyłącznie stary
układ); nowy układ wchodzi wtedy przez świeżą instalację albo kolejne wydanie, które stara instalacja przyjmuje już w miejscu.
"""
import os
import sys
import zipfile

TOP = ["Prezentacje.exe", "DK - paczka prezentacji dla AI.zip"]
WORK_PLIKI = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", "GROK.md", "PROMPT BEZ PROGRAMU.md", "zainstaluj-skill.ps1", "zainstaluj-skill.cmd"]
DIRS = ["pliki programu", "skill-prezentacje", "skill-ds-dobra-kaloria"]  # 06-07.10: kopie skilli dla agentów AI; od 1.3 w WORK
WORK = "WORK"
STARY_START = "Stwórz prezentację.exe"


def main(root, out, stary=False):
    """Wpisy (plik na dysku, nazwa w zipie). Nowy układ: nazwa = ścieżka względem `root`. Stary: WORK/ zdjęte z nazw, a plik startowy
    wchodzi pod nazwą "Stwórz prezentację.exe"."""
    wpisy = []
    for d in DIRS:
        for dp, _dn, fn in os.walk(os.path.join(root, WORK, d)):
            wpisy += [(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), os.path.join(root, WORK)).replace("\\", "/") if stary
                       else os.path.relpath(os.path.join(dp, f), root).replace("\\", "/")) for f in fn]
    wpisy += [(os.path.join(root, WORK, f), f if stary else WORK + "/" + f) for f in WORK_PLIKI]
    wpisy += [(os.path.join(root, f), STARY_START if (stary and f == "Prezentacje.exe") else f) for f in TOP]
    files = [p for p, _ in wpisy]
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        sys.exit("brak plików: %s" % missing[:5])
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p, nazwa in wpisy:
            z.write(p, nazwa)
    with zipfile.ZipFile(out) as z:
        bad = [i.filename for i in z.infolist() if not i.filename.isascii() and not i.flag_bits & 0x800]
    if bad:
        sys.exit("nazwy bez flagi UTF-8: %s" % bad)
    print("zip: %s (%.0f MB, %d plików, polskie nazwy z flagą UTF-8)" % (out, os.path.getsize(out) / 2 ** 20, len(files)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--stary" in sys.argv[3:])
