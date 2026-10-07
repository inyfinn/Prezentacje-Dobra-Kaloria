# -*- coding: utf-8 -*-
"""
wizki.py - wizualizacje produktów (gotowe packshoty) z biblioteki marki do slajdów portfolio (07.10.2026).

    python wizki.py "<nazwa linii albo smaku>" [--kategoria kulki] [--biblioteka <ścieżka>] [--ile 3] [--zloz wynik.png]
    python wizki.py --lista [--kategoria batony]        # linie i smaki, które są w bibliotece

Biblioteka:  ...\\- POLSKA\\01 - PRODUKTY\\- DK\\<kategoria>\\<SMAK — [ linia ]>\\<wersja>\\4 - WIZKI\\*FRONT-S*.png
(także podfolder INTERNET-PREZENTACJE-RGB). Nigdy: ARCHIWUM, PROJEKT, DRUK.

Po co: user 07.10 przy prezentacji strategii - na slajdach „Kulki” i „Batony” „brakuje wrzuconych tam wizualizacji.
jak wiesz, gdzie one są, to możesz je spróbować wrzucić”. Automat konwersji (pptx_convert) woła dla_kolumn() i wstawia
grafikę tylko wtedy, gdy KAŻDA kolumna slajdu ma pewne dopasowanie; każdy wybór trafia do uwag, żeby dało się go
sprawdzić. Zła paczka na slajdzie jest gorsza niż jej brak.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ALIASY_PLIK = os.path.join(HERE, "..", "assets", "linie-aliasy.json")
STALE = (r"M:\- POLSKA\01 - PRODUKTY\- DK", r"D:\Marketing\- POLSKA\01 - PRODUKTY\- DK")
ZBIORCZE = ("KAR", "MINI", "DOY6", "DISPLAY", "BOX", "MIX")  # wersje zbiorcze: bierzemy dopiero, gdy nie ma sztuki
CIEN = (59, 42, 32)


def _n(t):
    """Nazwa do porównań: małe litery, bez polskich znaków i wszystkiego poza literami i cyframi."""
    t = unicodedata.normalize("NFKD", (t or "").lower().replace("ł", "l"))
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in t if not unicodedata.combining(c)))


def biblioteka(*sciezki):
    """Katalog '01 - PRODUKTY\\- DK': zmienna DK_PRODUKTY, potem przodkowie podanych ścieżek (plik prezentacji, folder
    programu), potem stałe lokalizacje. None, gdy nie ma (np. dysk G: działu sprzedaży)."""
    env = os.environ.get("DK_PRODUKTY")
    if env:  # jawne wskazanie wygrywa; wartość, która nie jest katalogiem (np. "brak"), wyłącza bibliotekę (testy)
        return env if os.path.isdir(env) else None
    for s in sciezki:
        d = os.path.abspath(s) if s else ""
        while d and os.path.dirname(d) != d:
            c = os.path.join(d, "01 - PRODUKTY", "- DK")
            if os.path.isdir(c):
                return c
            d = os.path.dirname(d)
    return next((p for p in STALE if os.path.isdir(p)), None)


def indeks(lib):
    """[{kategoria, smak, linia, sciezka}] - dwa poziomy katalogów, bez archiwum, miksów i kategorii testowej."""
    out = []
    for kat in sorted(os.listdir(lib)):
        kp = os.path.join(lib, kat)
        if not os.path.isdir(kp) or "TEST" in kat.upper():
            continue
        for prod in sorted(os.listdir(kp)):
            pp = os.path.join(kp, prod)
            if not os.path.isdir(pp) or "ARCHIWUM" in prod.upper() or prod.startswith(("_", "—", "-")):
                continue
            m = re.match(r"^(.*?)\s*[—–-]\s*\[\s*(.*?)\s*\]\s*$", prod)
            out.append({"kategoria": re.sub(r"^[\d\s-]+", "", kat), "smak": (m.group(1) if m else prod).strip(),
                        "linia": m.group(2).strip() if m else "", "sciezka": pp})
    return out


def kategoria_z(tekst, idx):
    """Kategoria wymieniona w tekście (np. tytuł slajdu „Batony”) albo None. Porównanie po pierwszych 4 literach."""
    toks = [_n(w) for w in re.split(r"\W+", tekst or "") if len(w) >= 4]
    for kat in sorted({p["kategoria"] for p in idx}):
        k = _n(kat)
        if any(t[:4] == k[:4] for t in toks):
            return kat
    return None


def _aliasy():
    try:
        return json.load(open(ALIASY_PLIK, encoding="utf8"))
    except Exception:
        return {}


def dopasuj(nazwa, idx, kategoria=None):
    """Nazwa z nagłówka kolumny -> (produkty, opis dopasowania) albo ([], powód). Kolejność: słownik aliasów, linia
    dokładnie, linia po wspólnym początku (>= 6 liter), smak dokładnie. Kilka różnych linii naraz = brak (niepewne)."""
    n = _n(nazwa)
    if len(n) < 4:
        return [], "za krótka nazwa"
    pool = [p for p in idx if not kategoria or p["kategoria"] == kategoria]
    al = _aliasy()
    for key in ([_n(kategoria)] if kategoria else []) + ["*"]:
        a = (al.get(key) or {}).get(n)
        if a:
            got = [p for p in pool if (a.get("linia") and _n(p["linia"]) == _n(a["linia"])) or
                   _n(p["smak"]) in [_n(s) for s in a.get("smaki", [])]]
            if got:
                return got, "słownik: %s = %s" % (nazwa.strip(), a.get("linia") or ", ".join(a.get("smaki", [])))

    def linie(test):
        return sorted({(p["kategoria"], p["linia"]) for p in pool if p["linia"] and test(_n(p["linia"]))})

    def pref(a, b):
        k = 0
        while k < min(len(a), len(b)) and a[k] == b[k]:
            k += 1
        return k

    # pewne: nazwa linii dokładnie; albo nazwa ucięta / odmieniona końcówką (>= 8 wspólnych liter od początku, jedno
    # słowo jest początkiem drugiego) - ale tylko w znanej kategorii i tylko gdy pasuje jedna linia
    for jak, test in (("linia", lambda l: l == n),
                      ("linia (ta sama nazwa bez końcówki)",
                       lambda l: bool(kategoria) and pref(l, n) >= 8 and pref(l, n) == min(len(l), len(n)))):
        ls = linie(test)
        if len(ls) == 1:
            return [p for p in pool if (p["kategoria"], p["linia"]) == ls[0]], "%s %s" % (jak, ls[0][1])
        if len(ls) > 1:
            return [], "kandydat: kilka linii pasuje (%s)" % ", ".join("%s / %s" % x for x in ls)
    sm = [p for p in pool if _n(p["smak"]) == n]
    if len(sm) == 1:
        return sm, "smak " + sm[0]["smak"]
    ls = linie(lambda l: pref(l, n) >= 6)  # podobna nazwa to tylko podpowiedź do raportu, nigdy automat
    if ls:
        return [], "kandydat: podobna nazwa linii (%s)" % ", ".join("%s / %s" % x for x in ls)
    return [], "brak w bibliotece"


def _data(nazwa):
    m = re.search(r"(\d{1,2})[. ](\d{1,2})[. ](\d{4})", nazwa)
    if m:
        return (int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.search(r"(\d{4})[-_.](\d{1,2})[-_.](\d{1,2})", nazwa)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0, 0, 0)


def packshot(produkt):
    """Najlepszy gotowy packshot produktu: (ścieżka, ranga) albo (None, 9). Ranga: 0 = wprost pojedyncza sztuka,
    1 = nie wiadomo, 2 = wersja zbiorcza (karton, mini, 6x). W randze wygrywa najnowsza data w nazwie wersji;
    plik *FRONT-S*.png przed *FRONT*.png; bez tyłów i ujęć en face."""
    best = None
    for ver in os.listdir(produkt):
        vp = os.path.join(produkt, ver)
        w = os.path.join(vp, "4 - WIZKI")
        if "ARCHIWUM" in ver.upper() or not os.path.isdir(w):
            continue
        files = []
        for root in [w] + [os.path.join(w, d) for d in os.listdir(w) if os.path.isdir(os.path.join(w, d))
                           and "CMYK" not in d.upper() and "DRUK" not in d.upper()]:
            for f in os.listdir(root):
                u = f.upper()
                if u.endswith(".PNG") and "FRONT" in u and not any(x in u for x in ("TYŁ", "TYL", "ENFACE", "BACK")):
                    files.append((0 if "FRONT-S" in u else 1, 1 if "DEMO" in u else 0, len(f), os.path.join(root, f)))
        if not files:
            continue
        u = ver.upper().lstrip()
        zb = u.startswith(ZBIORCZE) or "6X" in u
        # 0 = wprost pojedyncza sztuka (BAT, BATON, DOY, gramatura w nazwie), 1 = nie wiadomo, 2 = wersja zbiorcza
        rank = 2 if zb else 0 if (u.startswith(("BAT", "DOY")) or re.search(r"\d{2,3}\s?G\b", u)) else 1
        key = (rank, tuple(-x for x in _data(ver)), sorted(files)[0])
        if best is None or key < best[0]:
            best = (key, sorted(files)[0][3], rank)
    return (best[1], best[2]) if best else (None, 9)


def _trim(path):
    """Obraz przycięty do alfy; None, gdy nie ma przezroczystości (biały prostokąt na slajdzie wygląda źle)."""
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A")
    if a.getextrema()[0] >= 250:
        return None
    return im.crop(a.getbbox())


def _cien(im, blur=16, dy=20, op=0.32):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, CIEN + (0,))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * op)))
    out.alpha_composite(sh, (pad, pad + dy))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad))
    return out


def zloz(pliki, wyjscie, max_px=1000):
    """2-3 paczki w jedną grafikę z miękkim cieniem: stojące obok siebie, leżące (batony) jedna nad drugą.
    Paczki o innym formacie niż pierwsza (leżąca wśród stojących) odpadają - mieszanka wygląda źle.
    Zwraca listę plików, które weszły do grafiki ([] = żaden plik nie ma przezroczystego tła)."""
    para = [(p, im) for p, im in ((p, _trim(p)) for p in pliki) if im is not None]
    if not para:
        return []
    lezace = para[0][1].width / para[0][1].height > 1.6
    para = [(p, im) for p, im in para if (im.width / im.height > 1.6) == lezace]
    ims = [im for _p, im in para]
    if lezace:
        wd, rots, dx, step = 1250, [-3, 2, -2], [0, 70, 20], 0.80
        ims = [im.resize((wd, int(im.height * wd / im.width)), Image.LANCZOS).rotate(rots[i % 3], expand=True,
                                                                                    resample=Image.BICUBIC)
               for i, im in enumerate(ims)]
        cv = Image.new("RGBA", (wd + 400, int(sum(im.height * step for im in ims[:-1]) + ims[-1].height) + 200))
        y = 40
        for i, im in enumerate(ims):
            cv.alpha_composite(_cien(im), (60 + dx[i % 3], y))
            y += int(im.height * step)
    else:
        ht = 900
        rots = {1: [0], 2: [-5, 5]}.get(len(ims), [-7, 0, 7])
        front = 1 if len(ims) == 3 else None
        ims = [im.resize((int(im.width * h / im.height), h), Image.LANCZOS).rotate(rots[i % len(rots)], expand=True,
                                                                                  resample=Image.BICUBIC)
               for i, im in enumerate(ims) for h in [int(ht * (1.0 if i == front else 0.93))]]
        ov = 0.22 if len(ims) == 3 else 0.10
        steps = [int(im.width * (1 - ov)) for im in ims]
        cv = Image.new("RGBA", (sum(steps[:-1]) + ims[-1].width + 200, max(im.height for im in ims) + 200))
        xs = [40 + sum(steps[:i]) for i in range(len(ims))]
        for i in [k for k in range(len(ims)) if k != front] + ([front] if front is not None else []):
            cv.alpha_composite(_cien(ims[i]), (xs[i], 40 + (cv.height - 200 - ims[i].height) // 2))
    cv = cv.crop(cv.getchannel("A").getbbox())
    cv.thumbnail((max_px, max_px), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(wyjscie)), exist_ok=True)
    cv.save(wyjscie, optimize=True)
    return [p for p, _im in para]


def dla_nazwy(nazwa, idx, kategoria, out_dir, ile=3):
    """Grafika dla jednej nazwy linii / smaku: {image, opis, produkty} albo {image: None, opis: powód}."""
    prods, jak = dopasuj(nazwa, idx, kategoria)
    kand = []
    for p in prods:
        f, rank = packshot(p["sciezka"])
        if f:
            kand.append((rank, p["smak"], f))
    if not kand:
        return {"image": None, "opis": jak if not prods else jak + ", ale bez gotowego packshotu (FRONT-S)"}
    best = min(r for r, _s, _f in kand)  # jedna ranga w grafice: same pojedyncze sztuki albo same kartony, bez mieszania
    wyb = [(s, f) for r, s, f in kand if r == best][:ile]
    name = "kol_%s_%s.png" % (_n(nazwa)[:24], hashlib.sha1("|".join(f for _, f in wyb).encode("utf8")).hexdigest()[:8])
    out = os.path.join(out_dir, name)
    lista = os.path.splitext(out)[0] + ".txt"  # które pliki naprawdę weszły do grafiki (po odsianiu innych formatów)
    if os.path.isfile(out) and os.path.isfile(lista):
        uzyte = [x for x in open(lista, encoding="utf8").read().splitlines() if x]
    else:
        uzyte = zloz([f for _, f in wyb], out)
        if not uzyte:
            return {"image": None, "opis": jak + ", ale packshoty nie mają przezroczystego tła"}
        with open(lista, "w", encoding="utf8") as fh:
            fh.write("\n".join(uzyte))
    wyb = [(s, f) for s, f in wyb if f in uzyte]
    return {"image": out, "opis": "%s (%s)" % (jak, ", ".join(s.capitalize() for s, _ in wyb)),
            "produkty": [s for s, _ in wyb], "pliki": [f for _, f in wyb]}


def dla_kolumn(nazwy, kontekst, lib, out_dir, ile=3):
    """Dla nagłówków kolumn jednego slajdu: lista wyników dla_nazwy (ta sama kolejność). kontekst = tytuł slajdu
    (z niego kategoria, np. „Batony”)."""
    idx = indeks(lib)
    kat = kategoria_z(kontekst, idx)
    return [dla_nazwy(n, idx, kat, out_dir, ile) for n in nazwy]


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Wizualizacje produktów Dobra Kaloria z biblioteki 01 - PRODUKTY\\- DK.")
    ap.add_argument("nazwa", nargs="?", default="")
    ap.add_argument("--kategoria", default="", help="np. kulki, batony (zawęża szukanie)")
    ap.add_argument("--biblioteka", default="", help="ścieżka do '01 - PRODUKTY\\- DK' (domyślnie szukam sam)")
    ap.add_argument("--ile", type=int, default=3)
    ap.add_argument("--zloz", default="", help="zapisz złożoną grafikę do tego pliku PNG")
    ap.add_argument("--lista", action="store_true", help="wypisz linie i smaki z biblioteki")
    a = ap.parse_args(argv)
    lib = a.biblioteka or biblioteka(os.getcwd(), HERE)
    if not lib:
        print("Nie znalazłem biblioteki '01 - PRODUKTY\\- DK'. Podaj --biblioteka albo ustaw DK_PRODUKTY.")
        return 2
    idx = indeks(lib)
    kat = kategoria_z(a.kategoria, idx) if a.kategoria else None
    if a.lista or not a.nazwa:
        for k in sorted({p["kategoria"] for p in idx}):
            if kat and k != kat:
                continue
            print(k)
            for ln in sorted({p["linia"] for p in idx if p["kategoria"] == k}):
                print("  [%s] %s" % (ln or "bez linii", ", ".join(p["smak"] for p in idx if p["kategoria"] == k and p["linia"] == ln)))
        return 0
    prods, jak = dopasuj(a.nazwa, idx, kat)
    print("Biblioteka:", lib)
    print("Dopasowanie:", jak)
    files = []
    kand = []
    for p in prods:
        f, rank = packshot(p["sciezka"])
        print("  %s / %s [%s] %s -> %s" % (p["kategoria"], p["smak"], p["linia"],
                                         {0: "sztuka", 1: "?", 2: "zbiorcze"}.get(rank, "-"), f or "BRAK packshotu"))
        if f:
            kand.append((rank, f))
    if kand:
        best = min(r for r, _f in kand)
        files = [f for r, f in kand if r == best][:a.ile]
    if a.zloz and files:
        print("Złożono %s z: %s" % (a.zloz, ", ".join(os.path.basename(f) for f in zloz(files, a.zloz))))
    return 0 if prods else 1


if __name__ == "__main__":
    sys.exit(main())
