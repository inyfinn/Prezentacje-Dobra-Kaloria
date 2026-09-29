# -*- coding: utf-8 -*-
"""Ikona programu z logo marki (zielony kafel z białym napisem) -> WORK\\src\\ikona.ico (kilka rozmiarów)."""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "src", "skill", "assets", "logo_green_box.png")
im = Image.open(src).convert("RGBA")
bbox = im.getbbox()
im = im.crop(bbox)
w, h = im.size
side = int(max(w, h) * 1.08)
canvas = Image.new("RGBA", (side, side), (15, 118, 62, 255))  # zieleń marki 0F763E jako tło kafla
canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
# zaokrąglone rogi kafla
mask = Image.new("L", (side, side), 0)
from PIL import ImageDraw  # noqa: E402
ImageDraw.Draw(mask).rounded_rectangle([0, 0, side - 1, side - 1], radius=side // 6, fill=255)
canvas.putalpha(mask)
out = os.path.join(HERE, "src", "ikona.ico")
canvas.save(out, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("OK", out, os.path.getsize(out), "B")
