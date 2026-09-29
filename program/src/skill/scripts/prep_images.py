# -*- coding: utf-8 -*-
"""
Przygotowanie grafik do prezentacji.

  python prep_images.py cutout WEJ.png WYJ.png [--tol 18]
      Usuwa biale/jednolite tlo zalewaniem od krawedzi (packshot na bialym tle
      -> przezroczysty PNG). Wnetrze opakowania zostaje nietkniete, nawet jesli
      jest biale, bo zalewanie idzie tylko od brzegow.

  python prep_images.py trim WEJ.png WYJ.png [--pad 12]
      Przycina przezroczyste marginesy (packshot z duzym pustym polem).

  python prep_images.py cutout_dark WEJ.png WYJ.png
      Produkt na CZARNYM tle (sesja zdjęciowa) -> PNG z alfą (np. prawdziwe kulki z kreatyną).

  python prep_images.py tif WEJ.tif WYJ.png
      Drukarski TIF CMYK+alfa (z biblioteki marki) -> PNG RGBA, przyciety i zmniejszony do 1400 px.

  python prep_images.py xlsx PLIK.xlsx KATALOG
      Wyciaga obrazy osadzone w Excelu razem z kotwica (arkusz, kolumna, wiersz),
      zeby dalo sie je dopasowac do naglowkow (np. warianty opakowan J/L/R/S).
"""
import os
import re
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFilter


def cutout(src, dst, tol=18):
    im = Image.open(src).convert("RGBA")
    W, H = im.size
    rgb = im.convert("RGB")
    mask = Image.new("L", (W, H), 0)
    # zalewanie od kazdego piksela brzegu, ktory jest jasny
    work = rgb.copy()
    marker = (255, 0, 255)
    for x, y in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2)]:
        px = work.getpixel((x, y))
        if px != marker and min(px) > 200:
            ImageDraw.floodfill(work, (x, y), marker, thresh=tol * 3)
    px = work.load()
    mp = mask.load()
    for y in range(H):
        for x in range(W):
            if px[x, y] == marker:
                mp[x, y] = 255
    alpha = Image.eval(mask, lambda v: 255 - v).filter(ImageFilter.GaussianBlur(0.8))
    im.putalpha(alpha)
    bb = alpha.point(lambda a: 255 if a > 20 else 0).getbbox()
    if bb:
        im = im.crop(bb)
    im.save(dst)
    print("cutout", dst, im.size)


def tif(src, dst, max_side=1400):
    """Drukarski TIF (CMYK + alfa, czesto 100+ MB) -> PNG RGBA do prezentacji.
    PIL nie czyta takich plikow - uzywamy tifffile (+imagecodecs). Konwersja CMYK->RGB bez profilu ICC
    (przyblizenie wystarczajace do rekwizytow); kolory sprawdz na podgladzie."""
    import numpy as np
    import tifffile
    a = tifffile.imread(src)
    t = tifffile.TiffFile(src)
    photometric = int(t.pages[0].photometric)
    if a.ndim == 3 and photometric == 5:  # SEPARATED = CMYK
        c, m, y, k = [a[..., i].astype(np.float32) / 255 for i in range(4)]
        alpha = a[..., 4].astype(np.float32) / 255 if a.shape[2] > 4 else np.ones_like(c)
        # alfa skojarzona (premultiplied): odwracamy mnozenie na farbie
        safe = np.where(alpha > 0, alpha, 1)
        c, m, y, k = [np.clip(ch / safe, 0, 1) for ch in (c, m, y, k)]
        rgb = np.stack([(1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k)], -1)
        out = np.concatenate([rgb, alpha[..., None]], -1)
        im = Image.fromarray((out * 255).astype(np.uint8), "RGBA")
    else:
        im = Image.fromarray(a)
    im = im.convert("RGBA")
    bb = im.split()[-1].point(lambda v: 255 if v > 20 else 0).getbbox()
    if bb:
        im = im.crop(bb)
    im.thumbnail((max_side, max_side))
    im.save(dst)
    print("tif", dst, im.size)


def cutout_dark(src, dst, thr=34, max_side=700):
    """Zdjęcie na czarnym tle (np. kulki z sesji) -> PNG z alfą. Tło = ciemne piksele połączone z krawędzią
    (zalewanie), więc ciemne miejsca wewnątrz produktu zostają. Miękka krawędź: rozmycie maski + zmniejszenie."""
    import numpy as np
    from scipy import ndimage
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    dark = a.max(axis=2) < thr
    lab, _ = ndimage.label(dark)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    bg = ndimage.binary_opening(bg, iterations=2)
    alpha = Image.fromarray(((~bg) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    bb = alpha.point(lambda v: 255 if v > 20 else 0).getbbox()
    if bb:
        out = out.crop(bb)
    out.thumbnail((max_side, max_side))
    out.save(dst)
    print("cutout_dark", dst, out.size)


def trim(src, dst, pad=12):
    im = Image.open(src).convert("RGBA")
    bb = im.split()[-1].point(lambda a: 255 if a > 20 else 0).getbbox()
    if bb:
        bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad))
        im = im.crop(bb)
    im.save(dst)
    print("trim", dst, im.size)


def xlsx_images(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    z = zipfile.ZipFile(path)
    names = z.namelist()
    wb_rels = z.read("xl/_rels/workbook.xml.rels").decode("utf8")
    wb = z.read("xl/workbook.xml").decode("utf8")
    sheets = {rid: name for name, rid in re.findall(r'<sheet[^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb)}
    sheet_files = {re.sub(r"^/?(xl/)?", "xl/", t): sheets.get(i) for i, t in re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', wb_rels)}
    for sf, sname in sheet_files.items():
        rels = sf.replace("worksheets/", "worksheets/_rels/") + ".rels"
        if rels not in names:
            continue
        for dt in re.findall(r'Target="([^"]*drawing\d+\.xml)"', z.read(rels).decode("utf8")):
            dpath = os.path.normpath(os.path.join(os.path.dirname(sf), dt)).replace("\\", "/")
            drels = dpath.replace("drawings/", "drawings/_rels/") + ".rels"
            rmap = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', z.read(drels).decode("utf8")))
            d = z.read(dpath).decode("utf8")
            for i, (col, coff, row, rid) in enumerate(re.findall(
                    r"<xdr:from><xdr:col>(\d+)</xdr:col><xdr:colOff>(-?\d+)</xdr:colOff><xdr:row>(\d+)</xdr:row>.*?r:embed=\"(rId\d+)\"", d, re.S)):
                media = os.path.normpath(os.path.join(os.path.dirname(dpath), rmap[rid])).replace("\\", "/")
                ext = os.path.splitext(media)[1]
                out = os.path.join(outdir, "%s_%02d_col%s_off%s_row%s%s" % (re.sub(r"\W+", "_", sname or "arkusz"), i + 1, col, coff, row, ext))
                with open(out, "wb") as f:
                    f.write(z.read(media))
                print(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    args = sys.argv[2:]
    opt = {}
    if "--tol" in args:
        opt["tol"] = int(args[args.index("--tol") + 1])
    if "--pad" in args:
        opt["pad"] = int(args[args.index("--pad") + 1])
    pos = [a for a in args if not a.startswith("--") and not a.isdigit()]
    {"cutout": cutout, "cutout_dark": cutout_dark, "trim": trim, "tif": tif}.get(cmd, lambda *a, **k: xlsx_images(*a))(*pos[:2], **opt) if cmd != "xlsx" else xlsx_images(*pos[:2])
