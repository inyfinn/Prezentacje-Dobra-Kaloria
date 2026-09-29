# -*- coding: utf-8 -*-
"""
Ikony liniowe (Lucide, licencja ISC) -> PNG z przezroczystym tłem w kolorach motywów.

    python make_icons.py            # renderuje wszystkie assets/icons/svg/*.svg
    python make_icons.py nazwa ...  # tylko wybrane

Nowa ikona: pobierz SVG z https://unpkg.com/lucide-static@1.48.0/icons/<nazwa>.svg do assets/icons/svg/
(nazwy: https://lucide.dev/icons). Styl jak w sklepie dobrakaloria.pl: cienka zielona kreska, zaokrąglone końce.
Wynik: assets/icons/<kolor>/<nazwa>.png (256 px). Kolory: zieleń fresh, zieleń shop, biel (na zieleni).
"""
import glob
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(ROOT, "assets", "icons", "svg")
COLORS = {"006400": "#006400", "0F763E": "#0F763E", "FFFFFF": "#FFFFFF", "AD8767": "#AD8767"}
SIZE = 256


def main(names=None):
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
    main(sys.argv[1:] or None)
