# -*- coding: utf-8 -*-
"""Sklada PNG slajdow w jedna plansze do szybkiego przegladu: contact_sheet.py KATALOG_PNG WYJ.png [kolumny]"""
import glob, os, sys
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
fs = sorted(glob.glob(os.path.join(d, "s*.png")))
W, H = 800, 450
rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * W + (cols + 1) * 12, rows * H + (rows + 1) * 12), (60, 60, 60))
for i, f in enumerate(fs):
    t = Image.open(f).convert("RGB").resize((W, H))
    sheet.paste(t, (12 + (i % cols) * (W + 12), 12 + (i // cols) * (H + 12)))
sheet.save(out)
print(out, len(fs))
