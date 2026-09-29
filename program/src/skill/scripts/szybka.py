# -*- coding: utf-8 -*-
"""
szybka.py - od folderu produktu do sprawdzonej prezentacji jednym poleceniem (28.09.2026).

    python szybka.py "<folder produktu>" [--claimy "a;b;c;d"] [--style C] [--tylko inwentarz|grafiki|szkic]
                                         [--robocze <katalog>] [--wyjscie <katalog>]

Kroki (każdy zapisuje wynik w <folder>\\_robocze, kolejne uruchomienie korzysta z cache):
  1. INWENTARZ  karty wprowadzenia (xlsx) -> nazwa, smaki, EAN, gramatura, % owoców, claimy, wartości odżywcze;
                copy (docx); packshoty z Wizualizacje\\; elementy z Elementy\\ przypisane do smaków
                -> inwentarz.json + mapa_grafik.json + podglad_grafik.png  (SPRAWDŹ OBRAZEM mapę!)
  2. GRAFIKI    wycięcie tła automatycznie wg rodzaju (alfa -> trim, czarne -> cutout_dark, białe -> cutout,
                TIF -> tif), zmniejszenie; cache: pomija pliki już przetworzone
  3. SZKIC      spec_B.json / spec_C.json ze standardową historią (okładka z 3 paczkami, claimy z ikonami,
                linia smaków, skład, karta każdego smaku, koniec). Istniejących specy NIE nadpisuje (-> szkic_*.json)
  4. BUDOWA+QA  build_dk.py, render.ps1 -EmbedFonts, verify.ps1 (kolizje), plansze podglądu
Na końcu wypisuje listę "DO DECYZJI" (dane badania z copy, niepewne dopasowania grafik, braki).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import unicodedata

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prep_images  # noqa: E402

NUT_NAMES = ["wartość energetyczna", "tłuszcz", "w tym kwasy tłuszczowe nasycone", "węglowodany", "w tym cukry",
             "błonnik", "białko", "sól", "potas"]
IMG_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def tokens(t):
    return [w for w in slug(t).split("_") if len(w) >= 3]


def stem(w):
    return w[:4]


# --- 1. inwentarz ------------------------------------------------------------------------------------
def read_card(path):
    import openpyxl
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    lab, nut = {}, []
    for row in ws.iter_rows(values_only=True):
        a, b = (row[0] if len(row) > 0 else None), (row[1] if len(row) > 1 else None)
        if a and b is not None:
            lab[str(a).strip().rstrip(":").strip().lower()] = b
        if b and str(b).strip().lower() in NUT_NAMES and len(row) > 3 and row[2]:
            nut.append([str(b).strip(), str(row[2]).strip(), str(row[3] or "").strip()])

    def get(*keys):
        for k in keys:
            for kk, v in lab.items():
                if kk.startswith(k):
                    return v
        return None

    legal = str(get("nazwa prawna") or "")
    fruit = re.search(r"Zawarto\w+ owoc\w+\s*(\d+\s*%)", legal)
    claims = [clean_claim(c) for c in str(get("oświadczenie żywieniowe") or "").splitlines() if c.strip()]
    claims = [c for c in claims if c]
    firm = str(get("podmiot odpowiedzialny") or "")
    return {
        "plik": os.path.basename(path), "nazwa_handlowa": str(get("nazwa handlowa") or ""),
        "ean": str(get("gtin") or "").strip(), "masa": str(get("masa netto") or "").strip(),
        "nazwa_prawna": legal.split(".")[0].strip(), "owoce": fruit.group(1).replace(" ", "") if fruit else "",
        "claimy_front": claims, "wartosci": nut, "polska_firma_rodzinna": "rodzinna" in firm.lower(),
    }


def clean_claim(c):
    """Claim z karty: bez znaków sterujących (np. \\x01 zamiast '0' w '0 % dodatku cukru'), '% dodatku' -> '0% dodatku',
    WERSALIKI -> zwykłe litery (Mindset i tak wersalikuje), '0 %' -> '0%'."""
    c = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", c).replace("\xa0", " ").strip(" -\u2022\t")
    c = re.sub(r"\s+", " ", c)
    c = re.sub(r"^\s*%", "0%", c)
    c = re.sub(r"(\d)\s+%", r"\1%", c)
    if c.isupper():
        c = c.lower()
    return c


def clean_claim(c):
    """Claim z karty: bez znaków sterujących (\\x01 zamiast '0' w '0 % dodatku cukru'), '% dodatku' -> '0% dodatku',
    WERSALIKI -> zwykłe litery (Mindset i tak wersalikuje), '0 %' -> '0%'."""
    c = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", c).replace("\xa0", " ").strip(" -•\t")
    c = re.sub(r"\s+", " ", c)
    c = re.sub(r"^\s*%", "0%", c)
    c = re.sub(r"(\d)\s+%", r"\1%", c)
    if c.isupper():
        c = c.lower()
    return c


def card_flavors(files):
    """Smak z nazwy pliku karty: 'Karta wprowadzenia_<produkt> <SMAK> 65 g 6300861 — data.xlsx'."""
    full = {}
    for f in files:
        base = os.path.basename(f)
        m = re.match(r"Karta wprowadzenia[_ ](.+?)\s+\d+\s*g\b", base, re.I)
        full[f] = (m.group(1) if m else os.path.splitext(base)[0]).split()
    names = list(full.values())
    pre = []
    if len(names) > 1:
        for ws in zip(*names):
            if len(set(w.lower() for w in ws)) == 1:
                pre.append(ws[0])
            else:
                break
    out = {}
    for f, ws in full.items():
        rest = ws[len(pre):] if pre else [w for w in ws if w.isupper()] or ws[-1:]
        fl = " ".join(rest).lower()
        prod = " ".join(pre) if pre else " ".join(ws[:len(ws) - len(rest)])
        out[f] = (prod, fl[:1].upper() + fl[1:])
    return out


def read_copy(folder):
    paras = []
    for f in glob.glob(os.path.join(folder, "*.docx")):
        import zipfile
        x = zipfile.ZipFile(f).read("word/document.xml").decode("utf8")
        for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
            t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip()
            if t:
                paras.append(t)
    return paras


def match_flavor(name, flavors):
    """Najlepszy smak dla nazwy pliku (wspólne tokeny po 4 pierwszych literach)."""
    tk = {stem(w) for w in tokens(name)}
    best, score = None, 0
    for fl in flavors:
        sc = len(tk & {stem(w) for w in tokens(fl)})
        if sc > score:
            best, score = fl, sc
    return best


def inventory(folder, rob):
    cards = sorted(glob.glob(os.path.join(folder, "Karta wprowadzenia*.xls*")))
    fl_of = card_flavors(cards)
    skus = []
    product = ""
    for c in cards:
        prod, fl = fl_of[c]
        product = product or prod
        d = read_card(c)
        d["smak"] = fl
        skus.append(d)
    flavors = [s["smak"] for s in skus]
    product_words = tokens(product)[:1]  # np. "kulki"
    # packshoty
    packs = sorted(f for f in glob.glob(os.path.join(folder, "Wizualizacje", "*")) if f.lower().endswith(IMG_EXT))
    mapa = {"packshoty": {}, "elementy": {fl: [] for fl in flavors}, "produkt": [], "pominiete": [],
            "niepewne": []}
    used = set()
    for f in packs:
        fl = match_flavor(os.path.basename(f), flavors)
        if fl and fl not in mapa["packshoty"]:
            mapa["packshoty"][fl] = f
            used.add(f)
    rest = [f for f in packs if f not in used]
    for fl in flavors:  # brak nazwy smaku w pliku -> kolorem: przypisz po kolejności i oznacz do sprawdzenia
        if fl not in mapa["packshoty"] and rest:
            mapa["packshoty"][fl] = rest.pop(0)
            mapa["niepewne"].append("packshot %s -> %s (dopasowanie po kolejności, sprawdź na podglądzie)"
                                    % (fl, os.path.basename(mapa["packshoty"][fl])))
    # elementy
    for f in sorted(glob.glob(os.path.join(folder, "Elementy", "*"))):
        if not f.lower().endswith(IMG_EXT):
            continue
        if os.path.getsize(f) > 40 * 1024 * 1024:
            mapa["pominiete"].append("%s (za duży - duże ilustracje nie pasują jako drobne elementy)" % os.path.basename(f))
            continue
        base = os.path.basename(f)
        if product_words and any(stem(w) == stem(product_words[0]) for w in tokens(base)):
            mapa["produkt"].append(f)
            continue
        fl = match_flavor(base, flavors)
        if fl:
            mapa["elementy"][fl].append(f)
        else:
            mapa["pominiete"].append("%s (nie pasuje do żadnego smaku)" % base)
    inv = {"folder": folder, "produkt": product[:1].upper() + product[1:], "smaki": skus, "copy": read_copy(folder),
           "badania": [os.path.basename(f) for f in glob.glob(os.path.join(folder, "*.xls*"))
                       if not os.path.basename(f).lower().startswith("karta")]}
    json.dump(inv, open(os.path.join(rob, "inwentarz.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    mp = os.path.join(rob, "mapa_grafik.json")
    if os.path.exists(mp):  # mapa już była - zachowaj ręczne poprawki (np. zamienione packshoty)
        old = json.load(open(mp, encoding="utf8"))
        if old.get("recznie"):
            mapa = old
            mapa["niepewne"] = []
    mapa.setdefault("recznie", False)
    json.dump(mapa, open(mp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    preview(mapa, os.path.join(rob, "podglad_grafik.png"))
    return inv, mapa


def preview(mapa, out):
    rows = [("PACKSHOT " + k, [v]) for k, v in mapa["packshoty"].items()]
    rows += [("ELEMENTY " + k, v[:8]) for k, v in mapa["elementy"].items()]
    rows += [("PRODUKT", mapa["produkt"][:8])]
    cell = 150
    im = Image.new("RGB", (220 + 8 * cell, len(rows) * (cell + 10)), (250, 246, 239))
    d = ImageDraw.Draw(im)
    for r, (label, files) in enumerate(rows):
        y = r * (cell + 10)
        d.text((8, y + cell // 2), label[:30], fill="black")
        for c, f in enumerate(files):
            d.text((220 + c * cell, y + cell - 4), os.path.basename(f)[:24], fill=(90, 90, 90))
            try:
                t = Image.open(f)
                t.thumbnail((cell - 8, cell - 8))
                t = t.convert("RGBA")
                im.paste(t, (220 + c * cell, y + 4), t)
            except Exception as e:  # noqa: BLE001
                d.text((220 + c * cell, y + 20), "blad: %s" % e, fill="red")
    im.save(out)


# --- 2. grafiki ---------------------------------------------------------------------------------------
def prep(src, dst, max_side):
    """Rodzaj tła rozpoznany z narożników; cache - pomija, gdy wynik nowszy od źródła."""
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    if src.lower().endswith((".tif", ".tiff")):
        prep_images.tif(src, dst, max_side=max_side)
        return dst
    im = Image.open(src).convert("RGBA")
    W, H = im.size
    corners = [im.getpixel(p) for p in [(2, 2), (W - 3, 2), (2, H - 3), (W - 3, H - 3)]]
    if all(c[3] < 20 for c in corners):
        bb = im.split()[-1].point(lambda a: 255 if a > 16 else 0).getbbox()
        im = im.crop(bb)
        im.thumbnail((max_side, max_side))
        im.save(dst)
    elif all(max(c[:3]) < 40 for c in corners):
        prep_images.cutout_dark(src, dst, max_side=max_side)
    else:
        prep_images.cutout(src, dst)
        t = Image.open(dst)
        t.thumbnail((max_side, max_side))
        t.save(dst)
    return dst


def diversify(files, n):
    """Po trochu z każdego rodzaju (pierwsze słowo nazwy + 'ugryz'/'lisc' itp.): mango, marakuja, liść, kulka cała,
    kulka nadgryziona... zamiast n plików tego samego rodzaju."""
    groups = {}
    for f in files:
        tk = tokens(re.sub(r"[\s_]*\(?\d+\)?$", "", os.path.splitext(os.path.basename(f))[0]))
        groups.setdefault(" ".join(tk[-2:]) if len(tk) > 1 else "".join(tk), []).append(f)
    out, i = [], 0
    while len(out) < min(n, len(files)):
        for g in groups.values():
            if i < len(g) and len(out) < n:
                out.append(g[i])
        i += 1
    return out


def prep_all(mapa, rob):
    el = os.path.join(rob, "el")
    os.makedirs(el, exist_ok=True)
    out = {"pack": {}, "props": {}, "produkt": []}
    for fl, f in mapa["packshoty"].items():
        out["pack"][fl] = prep(f, os.path.join(rob, "pack_%s.png" % slug(fl)), 1400)
    for fl, files in mapa["elementy"].items():
        out["props"][fl] = [prep(f, os.path.join(el, "p_%s.png" % slug(os.path.splitext(os.path.basename(f))[0])), 520)
                            for f in diversify(files, 10)]
    for f in diversify(mapa["produkt"], 8):
        out["produkt"].append(prep(f, os.path.join(el, "k_%s.png" % slug(os.path.splitext(os.path.basename(f))[0])), 700))
    return out


# --- 3. szkic -----------------------------------------------------------------------------------------
def tint_deep(pack):
    im = Image.open(pack).convert("RGBA")
    im.thumbnail((200, 200))
    px = [p for p in (im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()) if p[3] > 200]
    r, g, b = [sum(c[i] for c in px) / len(px) for i in range(3)]
    tint = "%02X%02X%02X" % tuple(int(255 - (255 - v) * 0.12) for v in (r, g, b))

    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    k = 1.0
    while True:  # przyciemniaj kolor smaku, aż tekst na tle smaku ma >= 4.5:1
        deep = "%02X%02X%02X" % tuple(int(v * k) for v in (r, g, b))
        if (lum(tint) + 0.05) / (lum(deep) + 0.05) >= 4.5 or k < 0.2:
            return tint, deep
        k -= 0.05


def icon_for(claim):
    c = claim.lower()
    for key, ic in [("cukr", "candy-off"), ("błonnik", "wheat"), ("potas", "leaf"), ("białk", "dumbbell"),
                    ("kreatyn", "dumbbell"), ("owoc", "apple"), ("rodzinn", "hand-heart"), ("naturaln", "sprout"),
                    ("mięk", "smile-plus"), ("smak", "citrus"), ("kwaś", "sparkles"), ("słod", "sparkles")]:
        if key in c:
            return ic
    return "badge-check"


def cap(t):
    return t[:1].upper() + t[1:]


def draft(inv, g, claims, theme, out_dir=None, suffix=""):
    skus = inv["smaki"]
    fl = [s["smak"] for s in skus]
    packs = [g["pack"].get(f) for f in fl]
    have = [p for p in packs if p]
    trio = [have[0], have[1], have[2]] if len(have) >= 3 else (have[0] if have else None)
    prod = g["produkt"]
    mix = []
    for i in range(6):  # elementy okładki: po jednym z każdego smaku + kulki produktu
        pool = [g["props"].get(f, []) for f in fl] + [prod]
        src = pool[i % len(pool)]
        if src:
            mix.append(src[(i // len(pool)) % len(src)])

    def props_for(f):
        own = g["props"].get(f, [])[:4]
        return (own + prod[:2] + own[4:6])[:6]
    claims = claims or sorted({c for s in skus for c in s["claimy_front"]}, key=len)[:4]
    claim_items = [{"icon": icon_for(c), "title": cap(c), "text": ""} for c in claims]
    source = "Wg kart wprowadzenia."
    grid = []
    common = set.intersection(*[set(map(str.lower, s["claimy_front"])) for s in skus]) if skus else set()
    for c in sorted(common):
        grid.append({"icon": icon_for(c), "title": cap(c), "text": ""})
    fruits = sorted({s["owoce"] for s in skus if s["owoce"]})
    if fruits:
        grid.append({"icon": "apple", "title": "%s owoców" % "-".join(fruits), "text": "w składzie"})
    if all(s["polska_firma_rodzinna"] for s in skus):
        grid.append({"icon": "hand-heart", "title": "Polska firma rodzinna", "text": ""})
    slides = [{"type": "cover", "variant": 2 if theme == "fresh" else 1, "kicker": "Nowość", "title": inv["produkt"],
               "subtitle": ". ".join(cap(c) for c in claims[:2]) + ".", "image": trio, "props": mix,
               "flavors": [{"name": f} for f in fl]}]
    if theme == "shop":
        slides.append({"type": "icon_list", "kicker": "Produkt", "title": "Co wyróżnia " + inv["produkt"].lower(),
                       "pack": trio, "props": mix[:5], "items": claim_items[:4]})
    else:
        slides.append({"type": "product_hero", "kicker": "Produkt", "title": "Co wyróżnia produkt", "image": trio,
                       "props": mix[:4], "items": claim_items[:4]})
    if len(skus) > 1:
        slides.append({"type": "line", "kicker": "Portfolio", "title": "%d smaki" % len(skus) if len(skus) < 5 else "Linia",
                       "items": [{"key": slug(s["smak"]), "name": s["smak"], "meta": s["masa"], "ean": s["ean"],
                                  "image": g["pack"].get(s["smak"]), "props": props_for(s["smak"])[:3],
                                  "title": "%s %s - %s" % (inv["produkt"], s["smak"].lower(), s["masa"]),
                                  "text": "%s owoców · EAN %s" % (s["owoce"], s["ean"])} for s in skus]})
    if grid:
        slides.append({"type": "icon_grid", "kicker": "Skład", "title": "Dobry skład", "items": grid[:6],
                       "source": source})
    for i, s in enumerate(skus):
        p = g["pack"].get(s["smak"])
        tint, deep = tint_deep(p) if p else ("F7E6DE", "A3302A")
        slides.append({"type": "flavor", "key": slug(s["smak"]), "kicker": "Smak %d/%d" % (i + 1, len(skus)),
                       "name": s["smak"], "text": s["nazwa_prawna"] + ".",
                       "facts": [{"value": s["owoce"] or "-", "label": "owoców w składzie"},
                                 {"value": "0%" if any("cukr" in c.lower() for c in s["claimy_front"]) else "-",
                                  "label": "dodatku cukru"}, {"value": s["masa"], "label": "opakowanie"}],
                       "ean": s["ean"], "tint": tint, "deep": deep, "image": p, "props": props_for(s["smak"]),
                       "rot": [-4, 4, -3, 3][i % 4], "morph": i > 0})
    slides.append({"type": "end", "contact": "halo@dobrakaloria.pl  ·  dobrakaloria.pl"})
    label = {"fresh": "B (odświeżona)", "shop": "nowy styl"}[theme]  # 29.09: nazwy "nowy styl" / "stary styl"
    return {"output": os.path.join(out_dir or inv["folder"], "%s - %s%s.pptx" % (inv["produkt"], label, suffix)),
            "theme": theme,
            "slides": slides}


# --- 4. budowa + QA ------------------------------------------------------------------------------------
def build_and_qa(spec_path, rob):
    r = subprocess.run([sys.executable, os.path.join(HERE, "build_dk.py"), spec_path], capture_output=True,
                       text=True, encoding="utf8", errors="replace")
    print(r.stdout.strip() or r.stderr.strip()[-2000:])
    m = re.search(r"OK (.+\.pptx) \d+ slajdow", r.stdout)
    if not m:
        return None
    pptx = m.group(1)
    name = os.path.splitext(os.path.basename(pptx))[0]
    png = os.path.join(rob, "qa", name)
    ps = lambda script, *a: subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",  # noqa: E731
                                            os.path.join(HERE, script), *a], capture_output=True, text=True,
                                           encoding="utf8", errors="replace").stdout
    ps("render.ps1", "-Src", pptx, "-Out", png, "-EmbedFonts")
    rep = ps("verify.ps1", "-Src", pptx)
    print("\n".join(l for l in rep.splitlines() if re.search(r"Tekst - problemy|TEKST|GRAFIKA|PRZEPE|krawedzi", l)))
    sheet = os.path.join(rob, "qa", name + ".png")
    subprocess.run([sys.executable, os.path.join(HERE, "contact_sheet.py"), png, sheet, "2"], capture_output=True)
    print("PLANSZA:", sheet)
    return pptx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--claimy", default="", help="claimy od usera oddzielone średnikiem")
    ap.add_argument("--style", default="C")  # 29.09: B nie robimy (user)
    ap.add_argument("--tylko", choices=["inwentarz", "grafiki", "szkic"])
    ap.add_argument("--robocze")
    ap.add_argument("--wyjscie", help="katalog na PPTX (domyślnie folder produktu)")
    a = ap.parse_args()
    rob = a.robocze or os.path.join(a.folder, "_robocze")
    os.makedirs(rob, exist_ok=True)
    inv, mapa = inventory(a.folder, rob)
    print("INWENTARZ: produkt '%s', smaki: %s, copy: %d akapitów, badania: %s" % (
        inv["produkt"], ", ".join(s["smak"] for s in inv["smaki"]), len(inv["copy"]), inv["badania"] or "brak"))
    print("PODGLĄD GRAFIK (sprawdź obrazem!):", os.path.join(rob, "podglad_grafik.png"))
    if a.tylko == "inwentarz":
        return
    g = prep_all(mapa, rob)
    if a.tylko == "grafiki":
        return
    claims = [c.strip() for c in a.claimy.split(";") if c.strip()]
    todo = list(mapa["niepewne"]) + ["pominięto: " + p for p in mapa["pominiete"]]
    if inv["copy"]:
        todo.append("copy ma %d akapitów - wstaw jego treść (np. wyniki badania: slajd section + segments/hero_stat)"
                    % len(inv["copy"]))
    if not claims:
        todo.append("brak claimów od usera - użyto oświadczeń z kart; dopytaj o claimy produktowe")
    for fl in mapa["elementy"]:
        if not mapa["elementy"][fl]:
            todo.append("smak %s nie ma własnych elementów - dodaj z biblioteki marki (owoce/liście)" % fl)
    for st in a.style.split(","):
        theme = {"B": "fresh", "C": "shop"}[st.strip()]
        path = os.path.join(rob, "spec_%s.json" % st.strip())
        suffix = ""
        if os.path.exists(path):  # dopracowany spec już jest - nie ruszamy go ani jego PPTX
            path, suffix = os.path.join(rob, "szkic_%s.json" % st.strip()), " (szkic)"
        spec = draft(inv, g, claims, theme, a.wyjscie, suffix)
        json.dump(spec, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=1)
        print("SPEC:", path)
        if a.tylko != "szkic":
            build_and_qa(path, rob)
    print("\nDO DECYZJI / UZUPEŁNIENIA:")
    for t in todo:
        print(" -", t)


if __name__ == "__main__":
    main()
