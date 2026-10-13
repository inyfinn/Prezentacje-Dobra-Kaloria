# -*- coding: utf-8 -*-
"""
Ikony liniowe (Lucide, licencja ISC) -> PNG z przezroczystym tłem w kolorach motywów.

    python make_icons.py            # renderuje wszystkie assets/icons/svg/*.svg
    python make_icons.py nazwa ...  # tylko wybrane

Nowa ikona: pobierz SVG z https://unpkg.com/lucide-static@1.48.0/icons/<nazwa>.svg do assets/icons/svg/
(nazwy: https://lucide.dev/icons). Styl jak w sklepie dobrakaloria.pl: cienka zielona kreska, zaokrąglone końce.
Wynik: assets/icons/<kolor>/<nazwa>.png (256 px). Kolory: zieleń fresh, zieleń shop, biel (na zieleni).

Ikony marki „W stylu DK” (odręczny obrys, 1000 szt., te same nazwy co Lucide) - jedno źródło, kolor robi build_dk.icon() w locie:

    python make_icons.py --dk <folder z PNG 512 px zestawu>   # -> assets/icons/dk/<nazwa>.png (256 px, RGBA, jeden kolor)
    # + trzy ikony pochodne, bo zestaw ich nie ma: check (z check-line bez linii), trending-up (trending-down odbity w pionie)
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(ROOT, "assets", "icons", "svg")
COLORS = {"006400": "#006400", "0F763E": "#0F763E", "FFFFFF": "#FFFFFF", "AD8767": "#AD8767"}
SIZE = 256


DK_DIR = os.path.join(ROOT, "assets", "icons", "dk")
DK_RGB = (15, 118, 62)  # #0F763E - kolor zestawu; icon() podmienia RGB, alfa zostaje


def dk_z_folderu(src):
    """PNG 512 px zestawu DK -> assets/icons/dk/<nazwa>.png: 256 px (LANCZOS), RGB ujednolicone, alfa bez zmian."""
    from PIL import Image
    os.makedirs(DK_DIR, exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(src, "*.png"))):
        a = Image.open(f).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS).getchannel("A")
        out = Image.new("RGBA", (SIZE, SIZE), DK_RGB + (0,))
        out.putalpha(a)
        out.save(os.path.join(DK_DIR, os.path.basename(f)), optimize=True)
        n += 1
    # zestaw nie ma samego „ptaszka” (check): wycinamy go z check-line (bez linii pod spodem), na środek płótna
    f = os.path.join(DK_DIR, "check-line.png")
    if os.path.exists(f):
        al = Image.open(f).getchannel("A")
        al.paste(0, (0, int(SIZE * 0.7), SIZE, SIZE))
        bb = al.getbbox()
        c = Image.new("L", (SIZE, SIZE), 0)
        c.paste(al.crop(bb), ((SIZE - (bb[2] - bb[0])) // 2, (SIZE - (bb[3] - bb[1])) // 2))
        out = Image.new("RGBA", (SIZE, SIZE), DK_RGB + (0,))
        out.putalpha(c)
        out.save(os.path.join(DK_DIR, "check.png"), optimize=True)
        n += 1
    # trending-up = trending-down odbity w pionie (zestaw ma tylko spadek)
    f = os.path.join(DK_DIR, "trending-down.png")
    if os.path.exists(f):
        Image.open(f).transpose(Image.FLIP_TOP_BOTTOM).save(os.path.join(DK_DIR, "trending-up.png"), optimize=True)
        n += 1
    print("OK", n, "ikon DK ->", DK_DIR)


def main(names=None):
    from playwright.sync_api import sync_playwright
    files = sorted(glob.glob(os.path.join(SVG_DIR, "*.svg")))
    if names:
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in names]
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": SIZE, "height": SIZE})
        for hexc, css in COLORS.items():
            out_dir = os.path.join(ROOT, "assets", "icons", hexc)
            os.makedirs(out_dir, exist_ok=True)
            for f in files:
                svg = open(f, encoding="utf8").read()
                svg = svg.replace('width="24"', 'width="%d"' % SIZE).replace('height="24"', 'height="%d"' % SIZE)
                svg = svg.replace('stroke-width="2"', 'stroke-width="1.6"')  # cieniej, jak ikony w sklepie
                page.set_content('<html><body style="margin:0;background:transparent;color:%s">%s</body></html>'
                                 % (css, svg))
                out = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0] + ".png")
                page.locator("svg").screenshot(path=out, omit_background=True)
        b.close()
    print("OK", len(files), "ikon x", len(COLORS), "kolory")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--dk"]:
        dk_z_folderu(sys.argv[2])
    else:
        main(sys.argv[1:] or None)
