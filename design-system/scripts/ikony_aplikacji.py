# -*- coding: utf-8 -*-
"""Ikony aplikacji Dobra Kaloria (wariant A, wybór usera 30.09.2026): zielony „liść” z logo - zaokrąglone narożniki
lewy górny i prawy dolny, pozostałe ostre - i białe litery Mindset.
    python ikony_aplikacji.py   ->  assets/icons/<id>.ico (16-256 px), <id>-256.png, <id>-1024.png

Małe rozmiary rysowane osobno (nie zmniejszane z 256), żeby litery zostały ostre w 16 i 32 px."""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
FONT = os.path.join(BASE, "assets", "fonts", "Mindset.otf")
OUT = os.path.join(BASE, "assets", "icons")
GREEN, WHITE = (15, 118, 62, 255), (255, 255, 255, 255)
APPS = {"prezentacje": "PR", "photo-resizer": "RE", "dam": "DAM", "packaging-checker": "PC"}
SIZES = [256, 128, 64, 48, 40, 32, 24, 20, 16]


def leaf(px, radius=0.24):
    s = px * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(s * radius)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=GREEN)
    d.rectangle([s - 1 - r, 0, s - 1, r], fill=GREEN)      # prawy górny ostry
    d.rectangle([0, s - 1 - r, r, s - 1], fill=GREEN)      # lewy dolny ostry
    return im


def icon(letters, px):
    im = leaf(px)
    s = px * 4
    d = ImageDraw.Draw(im)
    width = 0.80 if len(letters) > 2 else 0.74             # w małych rozmiarach litery możliwie duże
    if px <= 24:
        width += 0.06
    size = int(s * 0.62)
    while size > 8:
        f = ImageFont.truetype(FONT, size)
        l, t, r, b = d.textbbox((0, 0), letters, font=f)
        if r - l <= s * width and b - t <= s * 0.52:
            break
        size -= 2
    d.text(((s - (r - l)) / 2 - l, (s - (b - t)) / 2 - t), letters, font=f, fill=WHITE)
    return im.resize((px, px), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for app, letters in APPS.items():
        frames = [icon(letters, px) for px in SIZES]
        frames[0].save(os.path.join(OUT, "%s.ico" % app), sizes=[(p, p) for p in SIZES], append_images=frames[1:])
        frames[0].save(os.path.join(OUT, "%s-256.png" % app))
        icon(letters, 1024).save(os.path.join(OUT, "%s-1024.png" % app))
        print("ok", app, letters)


if __name__ == "__main__":
    main()
