# -*- coding: utf-8 -*-
"""Plansza startowa pliku "Stwórz prezentację.exe" (launcher.cs): zieleń marki, logo, nazwa, "Uruchamiam…"
-> WORK\\src\\ui\\img\\powitanie.png (560x330; launcher czyta ją z "pliki programu\\app\\ui\\img")."""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "src", "skill", "assets")
W, H = 560, 330
im = Image.new("RGB", (W, H), (15, 118, 62))  # 0F763E
logo = Image.open(os.path.join(A, "logo_white_box.png")).convert("RGBA")
lw = 190
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
im.paste(logo, ((W - lw) // 2, 34), logo)
d = ImageDraw.Draw(im)
f1 = ImageFont.truetype(os.path.join(A, "fonts", "Mindset.otf"), 34)
f2 = ImageFont.truetype(os.path.join(A, "fonts", "Lato-Regular.ttf"), 17)
t1 = "STWÓRZ PREZENTACJĘ"  # "Uruchamiam…", kółko i pasek rysuje na żywo launcher.cs (1.1.2)
d.text(((W - d.textlength(t1, font=f1)) / 2, 188), t1, font=f1, fill=(255, 255, 255))
out = os.path.join(HERE, "src", "ui", "img", "powitanie.png")
im.save(out)
print("OK", out)
