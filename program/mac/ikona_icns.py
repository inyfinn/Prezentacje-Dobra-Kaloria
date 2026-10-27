# -*- coding: utf-8 -*-
"""Ikona programu dla macOS: src/ikona.ico (kilka rozmiarów, największy 256 px) -> ikona.icns.
    python ikona_icns.py <ikona.ico> <ikona.icns>
Pillow sam zapisuje komplet rozmiarów .icns (16-512 px, zwykłe i @2x) z największego obrazu."""
import sys

from PIL import Image


def main(ico, icns):
    im = Image.open(ico)
    rozmiary = im.info.get("sizes") or {im.size}
    im.size = max(rozmiary)          # ICO trzyma kilka obrazów - bierzemy największy
    im = im.convert("RGBA")
    im.save(icns)
    print("OK %s (%dx%d) -> %s" % (ico, im.width, im.height, icns))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
