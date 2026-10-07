# -*- coding: utf-8 -*-
"""Plansze porównawcze konwersji 1:1: stary slajd N (lewa) | nowy slajd N (prawa), 3 pary na planszę.
User porównuje prezentacje dokładnie tak - dwa okna obok siebie - więc to jest bramka oddania konwersji (lekcje A33).

    python pary_slajdow.py <png oryginału> <png wyniku> <katalog wyjściowy>

Wejście: katalogi z render.ps1 (s01.png, s02.png, ...). Różna liczba slajdów = błąd konwersji (wypisuje ostrzeżenie).
"""
import os
import sys

from PIL import Image, ImageDraw


def main(old, new, out, per=3, wt=800, ht=450):
    os.makedirs(out, exist_ok=True)
    count = lambda d: len([f for f in os.listdir(d) if f.startswith("s") and f.endswith(".png")])
    n_old, n_new = count(old), count(new)
    if n_old != n_new:
        print("UWAGA: oryginał ma %d slajdów, wynik %d - konwersja ma być 1:1" % (n_old, n_new))
    n = max(n_old, n_new)
    for a in range(1, n + 1, per):
        sheet = Image.new("RGB", (wt * 2 + 12, (ht + 10) * per), (60, 60, 60))
        d = ImageDraw.Draw(sheet)
        for r, i in enumerate(range(a, min(a + per, n + 1))):
            for c, folder in enumerate((old, new)):
                p = os.path.join(folder, "s%02d.png" % i)
                if os.path.isfile(p):
                    sheet.paste(Image.open(p).convert("RGB").resize((wt, ht), Image.LANCZOS), (c * (wt + 12), r * (ht + 10)))
            d.text((4, r * (ht + 10) + 2), "%02d" % i, fill=(255, 0, 0))
        sheet.save(os.path.join(out, "para_%02d-%02d.png" % (a, min(a + per - 1, n))))
    print("OK %d par -> %s" % (n, out))


if __name__ == "__main__":
    main(*sys.argv[1:4])
