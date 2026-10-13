# -*- coding: utf-8 -*-
"""Miniatury slajdów szablonu dla okna programu (WORK\\src\\ui\\img\\typy\\tNN.png, 240 x 135, RGB).

Okno pokazuje je przy dodatkowych slajdach z szablonu (engine.EXTRA / catalog_extra: "img/typy/tNN.png"). Po zmianie
numeracji szablonu (13.10.2026: slajdy 59-63 doszły, 60 = "Cytat i wniosek", 64 = zakończenie, 65 = zakończenie
z podziękowaniem) trzeba odświeżyć t59-t63 i t65 (t60 miał miniaturę starego zakończenia z podziękowaniem).

    python miniatury_typow.py <katalog z renderami szablonu: s01.png...s65.png> [--nry 59,60,61,62,63,65] [--cel <katalog>]

Rendery: scripts\\render.ps1 -Src "DK - szablon prezentacji - pełen.pptx" -Out <katalog>. Nadpisuje tylko wskazane tNN.png
(własne pliki programu); bez --nry robi wszystkie numery z engine.EXTRA, które mają render.
"""
import argparse
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CEL = os.path.join(os.path.dirname(HERE), "src", "ui", "img", "typy")

ap = argparse.ArgumentParser()
ap.add_argument("rendery")
ap.add_argument("--nry", default="")
ap.add_argument("--cel", default=CEL)
a = ap.parse_args()
if a.nry:
    nry = [int(x) for x in a.nry.split(",") if x.strip()]
else:
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src", "app"))
    import engine
    nry = [n for n, _g, _t in engine.EXTRA]
os.makedirs(a.cel, exist_ok=True)
zrobione = []
for n in nry:
    src = os.path.join(a.rendery, "s%02d.png" % n)
    if not os.path.isfile(src):
        print("brak renderu slajdu %d: %s" % (n, src))
        continue
    with Image.open(src) as im:
        im.convert("RGB").resize((240, 135), Image.LANCZOS).save(os.path.join(a.cel, "t%02d.png" % n), optimize=True)
    zrobione.append(n)
print("OK: %s -> %s" % (", ".join("t%02d" % n for n in zrobione), a.cel))
