# -*- coding: utf-8 -*-
"""oko.py - "oko programu": ocena wyrenderowanego slajdu z samego obrazu (PNG), bez LLM i bez PowerPointa.

    import oko
    w = oko.ocen("s12.png", slajd=None)   # slajd = slownik slajdu ze specu (type, rows) albo None
    # -> {"miary": {...}, "usterki": [{"kod", "opis", "waga"}]}
    oko.ocen_katalog("katalog_png", spec=None)   # {nr: wynik} dla s01.png, s02.png, ...
    oko.opis(12, usterka)                        # "Slajd 12: ..."

    python oko.py KATALOG_PNG [spec.json]        # tabela do recznego sprawdzenia

Jak patrzy: obraz pomniejszony do ok. 480-530 px szerokosci, piksele w 4 klasach (biel / krem kart / zielen marki /
reszta = tresc), potem ciecie XY po bialych przerwach daje bloki; blok w kremie albo zieleni to "karta". Mierzy:
pusty dol, puste i nierowne karty, tresc przy krawedzi, zageszczenie, zbyt malo tresci. Wspolrzedne w ulamkach
szerokosci / wysokosci slajdu (0-1). Fałszywy alarm kosztuje przebudowe slajdu, wiec progi sa ostrozne.

Kody: PUSTY_DOL, KARTA_PUSTA, KARTY_NIEROWNE, PRZY_KRAWEDZI, GESTO, MALO_TRESCI, PLYWAJACA_TRESC. Waga: 1 = tylko do wiadomosci
(lista "Sprawdz najpierw"), 2 = usterka widoczna (warto przebudowac slajd), 3 = pewna usterka. Zielone tlo (okladka,
przekladka, zakonczenie), kremowe tlo calego slajdu i typy slajdow z TYPY_LUZNE (albo wiersz "quote") nie dostaja
PUSTY_DOL / MALO_TRESCI / PLYWAJACA_TRESC. Granica narzedzia: oko mierzy geometrie zrzutu; tego, czy karta ma
haslo, czy sam akapit, nie widzi - to mierzy samoocena specu (szablonuj.ocena). Wymaga numpy (jest w paczce programu) i PIL; nie rusza dysku poza czytaniem PNG.
"""
import glob
import json
import os
import re
import sys

import numpy as np
from PIL import Image

# --- PROGI (strojone na rendrach: dobre 43 slajdy, zle 2 x 43, 3 inne prezentacje, szablon marki; patrz wyniki.md) ---
PUSTY_DOL = 0.30            # pusty pas pod najnizsza trescia, ulamek wysokosci slajdu (powyzej = usterka)
PUSTY_DOL_LEKKI = 0.40      # do tylu waga 1, powyzej 2
PUSTY_DOL_CIEZKI = 0.55     # powyzej waga 3
KARTA_PUSTA = 0.50          # ulamek wysokosci karty pod ostatnim wierszem tresci
KARTA_PUSTA_CIEZKA = 0.75   # waga 3
KARTA_PELNA = 0.35          # "wypelniona" sasiadka: pusta ponizej tego
KARTA_GORA = 0.35           # pusta karta ma tekst przy gorze (pierwszy wiersz wyzej niz tyle); wysrodkowana ikona = ok
ROWNY_RZAD = 0.04           # karty w jednym rzedzie: gora i dol rozne o mniej niz tyle (ulamek wysokosci)
KARTY_NIEROWNE = 2.5        # stosunek wysokosci tresci najwyzszej do najnizszej karty w rzedzie
KARTY_NIEROWNE_CIEZKIE = 4.0
KRAWEDZ = 0.02              # tresc blizej niz tyle od krawedzi (ulamek) = usterka
GESTO = 0.935               # tekst / karta schodzi nizej niz tu (ulamek wysokosci): brak swiatla u dolu
OBRAZ_KOLOROW = 150         # blok o tylu roznych kolorach (4 bity na kanal) to zdjecie / packshot, nie tekst
PLYWA_GORA = 0.18           # PLYWAJACA_TRESC: pusty pas miedzy tytulem a trescia (ulamek wysokosci) co najmniej tyle,
PLYWA_DOL = 0.18            # pusty pas pod trescia co najmniej tyle (dobre: gora <= 0.10, odrzucone 0.19-0.28),
PLYWA_WYS = 0.50            # a sama tresc (od pierwszego bloku do najnizszego) niska: najwyzej tyle wysokosci slajdu
MALO_TRESCI = 0.50          # pole bboxu tresci pod tytulem / pole tresci (slajdy z kartami): dobre >= 0.62, zle <= 0.48
POLE_GORA = 0.25            # pole tresci zaczyna sie tu (pod tytulem), ulamek wysokosci
POLE_DOL = 0.935            # i konczy tu (nad numerem strony)
STOPKA_Y = 0.86             # stopka zrodla: blok nizej niz tu, nizszy niz STOPKA_H i krotszy niz STOPKA_W
STOPKA_H = 0.03
STOPKA_W = 0.90
STOPKA_PRZERWA = 0.025      # stopka jest oddzielona od tresci pasem tej wysokosci (ulamek)
ZIELONE_TLO = 0.38          # udzial zieleni na obwodzie slajdu => okladka / przekladka / zakonczenie
MASKA_LOGO = (0.86, 0.0, 1.0, 0.16)       # x0, y0, x1, y1 (ulamki) - logo w prawym gornym rogu
MASKA_NUMER = (0.90, 0.93, 1.0, 1.0)      # numer strony
SZEROKOSC = 480             # docelowa szerokosc analizy (px); mniejsze obrazy zostaja jak sa
# typy slajdow ze specu, ktorych wolno nie wypelniac (jedno haslo / okladka / przekladka / zakonczenie)
TYPY_LUZNE = {"cover", "cover_text", "section", "end", "contact", "statement", "quote", "hero_stat", "full_image",
              "video", "lead", "media"}

KODY = ("PUSTY_DOL", "KARTA_PUSTA", "KARTY_NIEROWNE", "PRZY_KRAWEDZI", "GESTO", "MALO_TRESCI", "PLYWAJACA_TRESC")


def _r(x):
    return round(float(x), 3)


def _pusty():
    return {"miary": {}, "usterki": []}


def _bez_tresci(m, dol):
    m.update({"tresc_bbox": None, "dol_pusty": dol, "wypelnienie": 0.0, "karty": [], "przy_krawedzi": False,
              "luzny": True, "pas_gora": None, "wys_tresci": None})
    return m, []


# --- obraz -> klasy pikseli ---------------------------------------------------------------------------------------
def _wczytaj(sciezka):
    try:
        im = Image.open(sciezka)
        im.load()
        im = im.convert("RGB")
        if im.width < 40 or im.height < 40:
            return None
        f = max(1, int(round(im.width / float(SZEROKOSC))))
        if f > 1:
            im = im.reduce(f)
        return np.asarray(im).astype(np.int16)
    except Exception:
        return None


def _klasy(a):
    """0 = biel, 1 = krem kart (FDF8EC), 2 = zielen marki (0F763E), 3 = reszta (tekst, zdjecia, akcenty)."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    jasny = (r >= 240) & (g >= 236) & (b >= 226)
    k = np.full(r.shape, 3, np.uint8)
    k[jasny & (b >= 247)] = 0
    k[jasny & (b < 247)] = 1
    zielen = (np.abs(r - 15) <= 32) & (np.abs(g - 118) <= 32) & (np.abs(b - 62) <= 32)
    k[zielen & ~jasny] = 2
    return k


# --- ciecie XY na bloki -------------------------------------------------------------------------------------------
def _przerwy(profil, minimum):
    """Przedzialy [a, b) kolejnych True w profilu (zajete), rozdzielone przerwami >= minimum."""
    idx = np.flatnonzero(profil)
    if not len(idx):
        return []
    out, a, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p - 1 >= minimum:
            out.append((a, p + 1))
            a = i
        p = i
    out.append((a, p + 1))
    return out


def _bloki(zaj, gx, gy):
    """Rekurencyjne ciecie XY maski zajetosci po bialych przerwach (gx: min. szerokosc pionowej, gy: poziomej)."""
    wyn = []
    stos = [(0, 0, zaj.shape[1], zaj.shape[0], 0)]
    while stos:
        x0, y0, x1, y1, d = stos.pop()
        sub = zaj[y0:y1, x0:x1]
        ys = _przerwy(sub.any(1), gy)
        if not ys:
            continue
        if len(ys) > 1:
            for a, b in ys:
                stos.append((x0, y0 + a, x1, y0 + b, d + 1))
            continue
        ya, yb = ys[0]
        sub = zaj[y0 + ya:y0 + yb, x0:x1]
        xs = _przerwy(sub.any(0), gx)
        if len(xs) > 1 and d < 12:
            for a, b in xs:
                stos.append((x0 + a, y0 + ya, x0 + b, y0 + yb, d + 1))
            continue
        xa, xb = xs[0]
        wyn.append((x0 + xa, y0 + ya, x0 + xb, y0 + yb))
    return wyn


def _maska(shape, m):
    H, W = shape
    return int(m[0] * W), int(m[1] * H), int(np.ceil(m[2] * W)), int(np.ceil(m[3] * H))


# --- pomiar -------------------------------------------------------------------------------------------------------
def _tlo(k):
    """Klasa tla slajdu wg obwodu: 'biale' / 'kremowe' / 'zielone' / 'inne'."""
    ob = np.concatenate([k[0], k[-1], k[:, 0], k[:, -1]])
    zi = float((ob == 2).mean())
    if zi >= ZIELONE_TLO or float((k == 2).mean()) >= 0.6:
        return "zielone"
    if float((ob == 0).mean()) >= 0.5:
        return "biale"
    if float((ob == 1).mean()) >= 0.5:
        return "kremowe"
    return "inne"


def _karta(k, bl):
    """Blok -> karta albo None. Karta = prostokat w kremie albo zieleni marki, nie wiekszy niz panel na caly slajd."""
    H, W = k.shape
    x0, y0, x1, y1 = bl
    w, h = x1 - x0, y1 - y0
    if w < 0.08 * W or h < 0.055 * H:
        return None
    if w >= 0.96 * W or h >= 0.96 * H:
        return None  # tlo / panel na caly slajd
    sub = k[y0:y1, x0:x1]
    kr, zi = float((sub == 1).mean()), float((sub == 2).mean())
    if max(kr, zi) < 0.45:
        return None
    return "krem" if kr >= zi else "zielen"


def _wypelnienie_karty(k, bl, rodzaj):
    """(pierwszy, ostatni) wiersz tresci karty w ulamku jej wysokosci. Tresc = piksel inny niz wypelnienie karty."""
    x0, y0, x1, y1 = bl
    H, W = k.shape
    mx, my = max(2, int(0.012 * W)), max(2, int(0.012 * H))
    sub = k[y0 + my:y1 - my, x0 + mx:x1 - mx]
    if not sub.size:
        return None, None
    wyp = 1 if rodzaj == "krem" else 2
    tr = (sub != wyp).sum(1) >= 2
    idx = np.flatnonzero(tr)
    if not len(idx):
        return None, None
    h = float(y1 - y0)
    return (idx[0] + my) / h, (idx[-1] + 1 + my) / h


def _obraz(a, b):
    """Blok to zdjecie / packshot: duzo roznych kolorow (tekst i plaskie wypelnienia maja ich kilkadziesiat)."""
    x0, y0, x1, y1 = b
    sub = (a[y0:y1, x0:x1] >> 4).reshape(-1, 3)
    return len(np.unique(sub[:, 0] * 256 + sub[:, 1] * 16 + sub[:, 2])) > OBRAZ_KOLOROW


def _analiza(a, slajd=None):
    k = _klasy(a)
    H, W = k.shape
    tlo = _tlo(k)
    slajd = slajd if isinstance(slajd, dict) else {}
    typ = slajd.get("type") or ""
    wiersze = slajd.get("rows") if isinstance(slajd.get("rows"), list) else []
    luzny = typ in TYPY_LUZNE or any(isinstance(r, dict) and r.get("k") == "quote" for r in wiersze) or tlo == "kremowe"
    m = {"tlo": tlo}
    if tlo in ("zielone", "inne"):
        m["pominiety"] = "tlo_" + tlo
        return _bez_tresci(m, 0.0)
    zaj = k != 0
    if tlo == "kremowe":
        zaj = k != 1
    for ma in (MASKA_LOGO, MASKA_NUMER):
        x0, y0, x1, y1 = _maska(k.shape, ma)
        zaj[y0:y1, x0:x1] = False
    bl = _bloki(zaj, max(3, int(0.016 * W)), max(2, int(0.008 * H)))
    if not bl:
        return _bez_tresci(m, 1.0)
    # panele na caly slajd (tlo, zdjecie, polowa slajdu) nie sa trescia do mierzenia. Stopka zrodla: maly blok bez
    # wypelnienia, nisko po lewej, oddzielony od reszty tresci pasem >= STOPKA_PRZERWA (kolejne linie stopki tez)
    tresc, panele = [], []
    for b in sorted(bl, key=lambda b: (b[1], b[0])):
        x0, y0, x1, y1 = b
        sub = k[y0:y1, x0:x1]
        if (x1 - x0) >= 0.96 * W or (y1 - y0) >= 0.96 * H:
            panele.append(b)
        elif (y0 >= STOPKA_Y * H and (y1 - y0) <= STOPKA_H * H and (x1 / W) <= STOPKA_W
              and y0 - max([t[3] for t in tresc if t[0] < x1 and t[2] > x0] or [0]) >= STOPKA_PRZERWA * H
              and float(((sub == 1) | (sub == 2)).mean()) < 0.4):
            continue
        else:
            tresc.append(b)
    m["panel"] = bool(panele)
    if not tresc:
        return _bez_tresci(m, 0.0 if panele else 1.0)
    X0 = min(b[0] for b in tresc)
    Y0 = min(b[1] for b in tresc)
    X1 = max(b[2] for b in tresc)
    Y1 = max(b[3] for b in tresc)
    txt = [b for b in tresc if not _obraz(a, b)]
    m["dol_tekstu"] = _r(max(b[3] for b in txt) / H) if txt else 0.0
    m["tresc_bbox"] = [_r(X0 / W), _r(Y0 / H), _r(X1 / W), _r(Y1 / H)]
    m["dol_pusty"] = _r(1 - Y1 / H)
    # karty
    karty = []
    for b in tresc:
        rodz = _karta(k, b) if tlo == "biale" else None
        if not rodz:
            continue
        p, o = _wypelnienie_karty(k, b, rodz)
        if o is None:
            p, o = 0.0, 0.0  # karta zupelnie bez tresci: pusta w calosci
        h = float(b[3] - b[1])
        karty.append({"x0": _r(b[0] / W), "y0": _r(b[1] / H), "x1": _r(b[2] / W), "y1": _r(b[3] / H), "rodzaj": rodz,
                      "pusta": _r(1 - o), "gora": _r(p), "wys_tresci": _r((o - p) * h / H)})
    m["karty"] = karty
    # pole tresci w pionie
    y_a, y_b = int(POLE_GORA * H), int(POLE_DOL * H)
    wiersze_z = np.zeros(H, bool)
    for b in tresc:
        wiersze_z[b[1]:b[3]] = True
    pole = wiersze_z[y_a:y_b]
    m["gestosc"] = _r(pole.mean())
    # wypelnienie = pole bboxu tresci pod tytulem / pole tresci
    pod = [b for b in tresc if b[3] > y_a]
    if pod:
        bx0, bx1 = min(b[0] for b in pod), max(b[2] for b in pod)
        by0, by1 = max(y_a, min(b[1] for b in pod)), max(b[3] for b in pod)
        m["wypelnienie"] = _r(float((bx1 - bx0) * max(0, by1 - by0)) / float((0.90 * W) * (y_b - y_a)))
    else:
        m["wypelnienie"] = 0.0
    # pas miedzy tytulem a trescia i wysokosc samej tresci (tytul = blok(i) z gory slajdu, nad 0.30 wysokosci)
    tyt = [b for b in tresc if b[1] < 0.20 * H and b[3] <= 0.30 * H]
    cialo = [b for b in tresc if all(b is not t for t in tyt)]
    if tyt and cialo:
        gora = min(b[1] for b in cialo)
        m["pas_gora"] = _r(max(0.0, (gora - max(b[3] for b in tyt)) / H))
        m["wys_tresci"] = _r((Y1 - gora) / H)
    else:
        m["pas_gora"], m["wys_tresci"] = None, None
    # krawedzie: bloki nie bedace panelem na caly slajd
    blizej = 1.0
    for b in tresc:
        x0, y0, x1, y1 = b
        blizej = min(blizej, x0 / W, y0 / H, 1 - x1 / W, 1 - y1 / H)
    m["przy_krawedzi"] = bool(blizej < KRAWEDZ)
    m["odstep_od_krawedzi"] = _r(blizej)
    m["luzny"] = bool(luzny or panele)
    return m, tresc


def _usterki(m):
    u = []
    if m.get("pominiety"):
        return u
    luzny = m.get("luzny", False)
    karty = m.get("karty", [])
    dol = m.get("dol_pusty", 0.0)
    if not luzny and dol > PUSTY_DOL:
        u.append({"kod": "PUSTY_DOL", "opis": "%d%% wysokości slajdu pod treścią jest puste" % round(dol * 100),
                  "waga": 3 if dol > PUSTY_DOL_CIEZKI else (2 if dol > PUSTY_DOL_LEKKI else 1)})
    # rzedy kart: pokrywanie sie w pionie
    rzedy = []
    for c in sorted(karty, key=lambda c: c["y0"]):
        for r in rzedy:
            if abs(c["y0"] - r[0]["y0"]) <= ROWNY_RZAD and abs(c["y1"] - r[0]["y1"]) <= ROWNY_RZAD:
                r.append(c)
                break
        else:
            rzedy.append([c])
    puste = []
    for r in rzedy:
        if len(r) >= 2 and any(c["pusta"] < KARTA_PELNA for c in r):
            puste += [c["pusta"] for c in r if c["pusta"] > KARTA_PUSTA and c["gora"] < KARTA_GORA]
    if puste:
        pu = max(puste)
        u.append({"kod": "KARTA_PUSTA",
                  "opis": "karta ma %d%% wysokości pusta pod tekstem, a obok stoi wypełniona" % round(pu * 100),
                  "waga": 3 if pu > KARTA_PUSTA_CIEZKA else 2})
    else:
        for r in rzedy:
            if len(r) < 2:
                continue
            wy = [c["wys_tresci"] for c in r if c["wys_tresci"] > 0]
            if len(wy) >= 2 and max(wy) / min(wy) > KARTY_NIEROWNE:
                u.append({"kod": "KARTY_NIEROWNE",
                          "opis": ("w jednym rzędzie treść jednej karty jest %.1f raza wyższa niż drugiej" % (max(wy) / min(wy))).replace(".", ","),
                          "waga": 3 if max(wy) / min(wy) > KARTY_NIEROWNE_CIEZKIE else 2})
                break
    if m.get("przy_krawedzi"):
        d = m.get("odstep_od_krawedzi", 0)
        u.append({"kod": "PRZY_KRAWEDZI",
                  "opis": ("treść dotyka krawędzi slajdu (może być ucięta)" if d <= 0.004
                           else ("treść jest %.1f%% od krawędzi slajdu" % (d * 100)).replace(".", ",")),
                  "waga": 3 if d <= 0.004 else 2})
    if not m.get("panel") and m.get("tlo") == "biale" and m.get("dol_tekstu", 0) > GESTO:
        u.append({"kod": "GESTO",
                  "opis": "tekst schodzi na %d%% wysokości slajdu, zostaje %d%% światła u dołu" % (
                      round(m["dol_tekstu"] * 100), round((1 - m["dol_tekstu"]) * 100)),
                  "waga": 1})
    pg = m.get("pas_gora")
    if not luzny and karty and pg is not None and pg >= PLYWA_GORA and dol >= PLYWA_DOL and m["wys_tresci"] <= PLYWA_WYS:
        u.append({"kod": "PLYWAJACA_TRESC",
                  "opis": "treść pływa: %d%% wysokości pusto pod tytułem i %d%% pod treścią, sama treść zajmuje %d%%" % (
                      round(pg * 100), round(dol * 100), round(m["wys_tresci"] * 100)),
                  "waga": 2})
    elif not luzny and karty and m.get("wypelnienie", 1) < MALO_TRESCI:
        u.append({"kod": "MALO_TRESCI", "opis": "treść zajmuje tylko %d%% pola treści" % round(m["wypelnienie"] * 100),
                  "waga": 2 if m["wypelnienie"] < 0.25 else 1})
    return u


def ocen(png_path, slajd=None):
    """Miary i usterki jednego slajdu. Brak / uszkodzony plik = wynik pusty, bez wyjatku."""
    try:
        a = _wczytaj(png_path)
        if a is None:
            return _pusty()
        m, _ = _analiza(a, slajd)
        u = _usterki(m)
        return {"miary": m, "usterki": u}
    except Exception:
        return _pusty()


def _slajdy_ze_specu(spec):
    if spec is None:
        return []
    if isinstance(spec, str):
        try:
            with open(spec, encoding="utf-8") as f:
                spec = json.load(f)
        except Exception:
            return []
    if isinstance(spec, dict):
        spec = spec.get("slides") or []
    return list(spec) if isinstance(spec, list) else []


def ocen_katalog(png_dir, spec=None):
    """{nr_slajdu: wynik ocen()} dla s01.png, s02.png, ... (spec: sciezka json / slownik z 'slides' / lista)."""
    sl = _slajdy_ze_specu(spec)
    wyn = {}
    for f in sorted(glob.glob(os.path.join(png_dir, "s*.png"))):
        mm = re.match(r"s(\d+)\.png$", os.path.basename(f), re.I)
        if not mm:
            continue
        nr = int(mm.group(1))
        wyn[nr] = ocen(f, sl[nr - 1] if 0 < nr <= len(sl) and isinstance(sl[nr - 1], dict) else None)
    return wyn


def opis(nr, usterka):
    return "Slajd %s: %s" % (nr, usterka["opis"])


def _tabela(png_dir, spec=None):
    wyn = ocen_katalog(png_dir, spec)
    for nr, w in wyn.items():
        m = w["miary"]
        kody = ",".join("%s/%d" % (u["kod"], u["waga"]) for u in w["usterki"]) or "-"
        if not m:
            ms = "(pusty wynik)"
        elif m.get("pominiety"):
            ms = "pominiety: " + m["pominiety"]
        else:
            ms = "dol=%.2f wyp=%.2f gest=%.2f karty=%d kraw=%.3f bbox=%s" % (
                m.get("dol_pusty", 0), m.get("wypelnienie", 0), m.get("gestosc", 0), len(m.get("karty", [])),
                m.get("odstep_od_krawedzi", 0), m.get("tresc_bbox"))
        print("s%02d | %-34s | %s" % (nr, kody, ms))
    return wyn


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    _tabela(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
