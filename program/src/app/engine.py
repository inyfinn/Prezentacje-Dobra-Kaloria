# -*- coding: utf-8 -*-
"""Silnik programu "Stwórz prezentację": folder produktu -> gotowy PPTX.

Owija skill /prezentacje (szybka.py: inwentarz i grafiki; build_dk.py: nowy styl; build_deck.py: stary styl;
verify.ps1: kontrola tekstu w PowerPoint). Deterministyczny - żadnych pytań: czego automat nie wie, wpisuje jako
podpowiedź w [nawiasach] i zgłasza w "uwagi". Ten sam silnik obsługuje okno (gui.py) i wiersz poleceń dla AI (cli.py).
"""
import base64
import glob
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback

import paths

paths.ensure_user_dirs()
os.environ.setdefault("DK_GUARD_CACHE", os.path.join(paths.USER_DIR, "wygenerowane.json"))
os.environ.setdefault("DK_CACHE_DIR", os.path.join(paths.USER_DIR, "cache"))
sys.path.insert(0, paths.SKILL_SCRIPTS)
import szybka  # noqa: E402
import build_dk  # noqa: E402
import build_deck  # noqa: E402
import guard  # noqa: E402
import make_template  # noqa: E402  - katalog typów slajdów szablonu
szybka.OCR_PS = os.path.join(paths.SKILL_SCRIPTS, "ocr_win.ps1")  # paczki bez smaku w nazwie: napis z opakowania
from PIL import Image  # noqa: E402

CREATE_NO_WINDOW = 0x08000000


class _Glob:  # glob bez plików tymczasowych Office (~$Karta...xlsx) - openpyxl by się na nich wywrócił
    @staticmethod
    def glob(p):
        return [f for f in glob.glob(p) if not os.path.basename(f).startswith("~$")]


szybka.glob = _Glob


class Cancelled(Exception):
    pass


# --- sekcje prezentacji (id, nazwa, opis) - kolejność = kolejność slajdów -------------------------------------
SECTIONS = [
    ("okladka", "Okładka", "Logo, nazwa produktu i cała linia smaków"),
    ("smaki", "Linia smaków", "Karta każdego smaku obok siebie z gramaturą"),
    ("wyroznia", "Co wyróżnia produkt", "Claimy z kart wprowadzenia z ikonami"),
    ("sklad", "Dobry skład", "Oświadczenia wspólne dla wszystkich smaków"),
    ("wartosci", "Wartości odżywcze", "Tabela z karty wprowadzenia (100 g i opakowanie)"),
    ("karty_smakow", "Karta każdego smaku", "Osobny slajd: nazwa, opis, twarde dane, EAN"),
    ("copy", "Tekst z copy", "Akapity z pliku copy (docx) w kartach"),
    ("badanie", "Wyniki badania", "Liczby znalezione w copy; brakujące jako [00%] do uzupełnienia"),
    ("film", "Film / podcast", "Claim i miniatura filmu z YouTube (wpisz link)"),
    ("koniec", "Zakończenie", "Logo, #zawszedobra, kontakt"),
]
LENGTH_PRESETS = {  # suwak "Długość": które sekcje domyślnie włączone
    0: ["okladka", "smaki", "wyroznia", "sklad", "koniec"],
    1: ["okladka", "smaki", "wyroznia", "sklad", "copy", "badanie", "koniec"],
    2: ["okladka", "smaki", "wyroznia", "sklad", "wartosci", "karty_smakow", "copy", "badanie", "film", "koniec"],
}
# Grupy slajdów (kolejność = kolejność w oknie i w prezentacji). Nazwy od usera 30.09.
GROUPS = [("naglowki", "Nagłówki", "okładki, agenda, przerywniki, zakończenie"),
          ("opis", "Opis", "tekst, punkty, akapity, zdjęcie z opisem"),
          ("cechy", "Cechy", "zalety, claimy, argumenty dla handlu"),
          ("szczegoly", "Szczegóły", "smaki, wartości, logistyka, ceny, tabele"),
          ("dane", "Dane", "liczby, wyniki badań, wykresy"),
          ("multimedia", "Multimedia", "filmy, zdjęcia, galerie, social media"),
          ("cytaty", "Cytaty", "opinie i jedno zdanie-teza")]
AUTO_GROUP = {"okladka": "naglowki", "koniec": "naglowki", "copy": "opis", "wyroznia": "cechy", "sklad": "cechy",
              "smaki": "szczegoly", "karty_smakow": "szczegoly", "wartosci": "szczegoly", "badanie": "dane",
              "film": "multimedia"}
# Slajdy z szablonu (numer slajdu w szablonie, grupa, nazwa). Pominięte: instrukcje (1-2) i typy, które program
# buduje z danych folderu (okładka 3, zalety 31, karta smaku 33, linia 34, wartości 35, kafle 36, film 49, koniec 59).
EXTRA = [(4, "naglowki", "Okładka: paczka na granicy zieleni"), (5, "naglowki", "Okładka: biały tytuł na zieleni"),
         (6, "naglowki", "Okładka klasyczna 50/50"), (7, "naglowki", "Okładka bez produktu 50/50"),
         (8, "naglowki", "Okładka bez produktu na zieleni"), (9, "naglowki", "Okładka bez produktu, jasna"),
         (10, "naglowki", "Agenda"), (11, "naglowki", "Przerywnik rozdziału, ciemny"),
         (12, "naglowki", "Przerywnik rozdziału z numerem"), (60, "naglowki", "Zakończenie z podziękowaniem"),
         (13, "opis", "Wstęp z akapitem"), (15, "opis", "Tekst długi w dwóch kolumnach"),
         (16, "opis", "Akapit w karcie"), (17, "opis", "Punkty"), (18, "opis", "Punkty ze zdjęciem"),
         (19, "opis", "Kroki / proces"), (21, "opis", "Porównanie: dziś i propozycja"),
         (22, "opis", "Tekst i zdjęcie"), (23, "opis", "Zdjęcie i tekst"),
         (24, "cechy", "Tekst i produkt"), (25, "cechy", "Zalety z ikonami i zdjęciem"),
         (30, "cechy", "Anatomia produktu"), (32, "cechy", "Siatka cech z ikonami"),
         (44, "cechy", "Argumenty dla handlu"), (56, "cechy", "Okazje spożycia"),
         (42, "szczegoly", "Tabela"), (43, "szczegoly", "Oś czasu"), (45, "szczegoly", "Logistyka"),
         (54, "szczegoly", "Cena i marża"), (55, "szczegoly", "Porównanie z konkurencją"),
         (47, "szczegoly", "Osoba kontaktowa"), (58, "szczegoly", "Następne kroki"),
         (37, "dane", "Liczba-bohater"), (38, "dane", "Wskaźniki (KPI)"), (39, "dane", "Wykres słupkowy"),
         (40, "dane", "Dwie grupy wyników"), (41, "dane", "A kontra B"), (52, "dane", "Wykres pierścieniowy"),
         (53, "dane", "Wykres kolumnowy"),
         (48, "multimedia", "Film na cały slajd"), (50, "multimedia", "Film z tekstem"),
         (26, "multimedia", "Zdjęcie na cały slajd z podpisem"), (27, "multimedia", "Zdjęcie na cały slajd"),
         (28, "multimedia", "Galeria 3 zdjęć"), (29, "multimedia", "Galeria 6 zdjęć"),
         (51, "multimedia", "Przed i po"), (46, "multimedia", "Karty ze zdjęciem"), (57, "multimedia", "Social media"),
         (20, "cytaty", "Cytat / opinia"), (14, "cytaty", "Jedno zdanie – teza")]
_TPL = None


def _template():
    """Slajdy szablonu {numer: slajd} (z make_template - to samo źródło co plik szablonu)."""
    global _TPL
    if _TPL is None:
        _TPL = {i + 1: s for i, s in enumerate(make_template.spec("shop")["slides"])}
    return _TPL


def _short(label, n=110):
    t = label.split(":", 1)[1] if ":" in label[:60] else label
    t = re.sub(r"\s*\(wzór z [^)]*\)", "", t).strip()
    t = t.split(". ")[0].rstrip(".")
    t = t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"
    return t[:1].upper() + t[1:]


def catalog_extra():
    tpl = _template()
    return [{"id": "t%02d" % i, "grupa": g, "nazwa": n, "opis": _short(tpl[i]["label_slide"]), "rodzaj": "szablon",
             "miniatura": "img/typy/t%02d.png" % i, "slajdy": 1, "dostepna": True, "domyslnie": False, "powod": ""}
            for i, g, n in EXTRA]


def template_slides(ids, produkt, flavors, packs, props, claim=""):
    """Wybrane slajdy szablonu z podpowiedziami w [nawiasach]; obrazy przykładowe zamienione na grafiki produktu,
    [Nazwa produktu] i [Smak N] - na dane z folderu. Reszta nawiasów zostaje do uzupełnienia."""
    import copy as _copy
    demo = os.path.join(paths.SKILL_DIR, "assets", "demo")
    cnt = {"pack": 0, "p": 0}

    def img(path):
        base = os.path.basename(path)
        kind = "pack" if base.startswith("pack_") else "p"
        pool = packs if kind == "pack" else props
        if pool:
            cnt[kind] += 1
            return pool[(cnt[kind] - 1) % len(pool)]
        return os.path.join(demo, base)

    def walk(x):
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        if isinstance(x, str):
            if x.lower().endswith(".png") and os.sep + "demo" + os.sep in x:
                return img(x)
            x = x.replace("[Nazwa produktu]", produkt).replace("[Nowość]", "Nowość")
            if claim:
                x = x.replace("[Jedno zdanie: główny claim z karty wprowadzenia]", claim)
            for n, f in enumerate(flavors[:3], 1):
                x = x.replace("[Smak %d]" % n, f)
        return x

    tpl = _template()
    out = []
    for sid in ids:
        s = _copy.deepcopy(tpl[int(sid[1:])])
        for k in ("section", "label_slide", "hidden"):
            s.pop(k, None)
        out.append(walk(s))
    return out


STEPS = [("folder", "Czytam folder", 5), ("grafiki", "Przygotowuję grafiki", 40), ("slajdy", "Układam slajdy", 5),
         ("budowa", "Buduję prezentację", 20), ("qa", "Sprawdzam w PowerPoint", 25), ("zapis", "Zapisuję", 5)]
_cache = {}  # folder -> (inv, mapa)


def powerpoint_available():
    try:
        import winreg
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"PowerPoint.Application\CurVer"))
        return True
    except OSError:
        return False


def _log_file(text):
    try:
        with open(os.path.join(paths.LOG_DIR, "ostatni.log"), "a", encoding="utf8") as f:
            f.write(time.strftime("%H:%M:%S ") + text + "\n")
    except OSError:
        pass


def normalize_folder(path):
    """Upuszczony może być folder ALBO dowolny plik z niego - bierzemy folder."""
    path = (path or "").strip().strip('"')
    if not path:
        raise ValueError("Nie wskazano folderu.")
    if os.path.isfile(path):
        path = os.path.dirname(path)
    if not os.path.isdir(path):
        raise ValueError("Folder nie istnieje: %s" % path)
    if os.path.basename(path).lower() == "_robocze":
        path = os.path.dirname(path)
    return os.path.abspath(path)


# --- 1. analiza folderu -------------------------------------------------------------------------------------------
def analyze(path):
    folder = normalize_folder(path)
    cards = _Glob.glob(os.path.join(folder, "Karta wprowadzenia*.xls*"))
    if not cards:
        raise ValueError("W tym folderze nie ma kart wprowadzenia (plików 'Karta wprowadzenia_....xlsx') - "
                         "to nie wygląda na folder produktu.")
    rob = os.path.join(folder, "_robocze")
    os.makedirs(rob, exist_ok=True)
    inv, mapa = szybka.inventory(folder, rob)
    _cache[folder] = (inv, mapa)
    skus = inv["smaki"]
    smaki = [{"nazwa": s["smak"], "masa": s["masa"], "ean": s["ean"], "packshot": bool(mapa["packshoty"].get(s["smak"])),
              "elementy": len(mapa["elementy"].get(s["smak"], []))} for s in skus]
    n_el = sum(len(v) for v in mapa["elementy"].values()) + len(mapa["produkt"])
    uwagi = []
    for s in smaki:
        if not s["packshot"]:
            uwagi.append({"typ": "ostrzezenie", "tekst": "Smak %s nie ma packshotu w folderze Wizualizacje - na slajdach "
                                                      "będzie miejsce do podmiany." % s["nazwa"]})
        elif s["elementy"] == 0:
            uwagi.append({"typ": "info", "tekst": "Smak %s nie ma własnych elementów (owoce) w folderze Elementy."
                          % s["nazwa"]})
    for t in mapa.get("niepewne", []):
        uwagi.append({"typ": "info", "tekst": t})
    if mapa.get("ocr"):
        uwagi.append({"typ": "info", "tekst": "Paczki dopasowane po napisie na opakowaniu (nazwy plików nie mają smaku)."})
    for t in mapa.get("pominiete", [])[:3]:
        uwagi.append({"typ": "info", "tekst": "Pominięto: " + t})
    common = _common_claims(skus)
    prose, _src, copy_stats = split_copy(inv["copy"])
    prose = [p for _, ps in chunk_copy(prose) for p in ps]  # same nagłówki bez treści to nie akapity
    wiz = os.path.join(folder, "Wizualizacje")
    packs_all = sorted(f for f in _Glob.glob(os.path.join(wiz, "*")) if f.lower().endswith(szybka.IMG_EXT))
    packshoty_pliki = [{"plik": os.path.basename(f), "miniatura": _thumb_file(f)} for f in packs_all]
    for s in smaki:
        p = mapa["packshoty"].get(s["nazwa"])
        s["packshot_plik"] = os.path.basename(p) if p else None
        s["miniatura"] = next((x["miniatura"] for x in packshoty_pliki if x["plik"] == s["packshot_plik"]), None)
    avail = {
        "okladka": True, "koniec": True,
        "smaki": len(skus) > 1,
        "wyroznia": any(s["claimy_front"] for s in skus),
        "sklad": bool(common or any(s["owoce"] for s in skus)),
        "wartosci": any(s["wartosci"] for s in skus),
        "karty_smakow": len(skus) >= 1,
        "copy": len(prose) > 0,
        "badanie": bool(inv["badania"]) or len(copy_stats) >= 2,
        "film": True,
    }
    default = set(LENGTH_PRESETS[1])
    powody = {}
    if inv["copy"] and not prose:
        powody["copy"] = "w pliku są same liczby z badania, trafią do „Wyniki badania”"
    n_copy = len(chunk_copy(split_copy(inv["copy"])[0]))
    slajdy = {"karty_smakow": len(skus), "copy": n_copy, "badanie": 2}
    sekcje = [{"id": i, "nazwa": n, "opis": o, "dostepna": avail[i], "domyslnie": avail[i] and i in default,
               "powod": powody.get(i, ""), "grupa": AUTO_GROUP[i], "rodzaj": "auto", "slajdy": slajdy.get(i, 1)}
              for i, n, o in SECTIONS] + catalog_extra()
    n_img = len(mapa["packshoty"]) + min(n_el, 10 * max(1, len(skus)) + 8)
    est = 8 + 0.7 * n_img + (18 if powerpoint_available() else 0)
    return {"ok": True, "folder": folder, "produkt": inv["produkt"], "smaki": smaki, "karty": len(cards),
            "copy_akapity": len(prose), "copy_pliki": [t["plik"] for t in inv.get("teksty", [])],
            "copy_wszystkie": len(inv["copy"]), "copy_liczby": len(copy_stats), "badania": inv["badania"], "packshoty_pliki": packshoty_pliki,
            "grafiki": {"packshoty": len(mapa["packshoty"]), "elementy": n_el, "pominiete": len(mapa.get("pominiete", []))},
            "uwagi": uwagi, "sekcje": sekcje, "grupy": [{"id": g, "nazwa": n, "opis": d} for g, n, d in GROUPS],
            "presety": {str(k): v for k, v in LENGTH_PRESETS.items()}, "domyslne": {"styl": "nowy", "dlugosc": 1, "tekst": 1},
            "szacowany_czas_s": int(est), "powerpoint": powerpoint_available()}


# --- pomocnicze: treść --------------------------------------------------------------------------------------------
def _common_claims(skus):
    if not skus:
        return []
    common = set.intersection(*[set(map(str.lower, s["claimy_front"])) for s in skus])
    return sorted(common, key=len)


def parse_claims(text):
    """Claimy od usera: linia = 'Tytuł' albo 'Tytuł – opis' / 'Tytuł: opis' (średnik też rozdziela)."""
    out = []
    for line in re.split(r"[\n;]", text or ""):
        line = line.strip(" -•")
        if not line:
            continue
        m = re.match(r"(.+?)\s*(?:[:–—]|\s-\s)\s*(.+)", line)
        out.append((szybka.cap(m.group(1).strip()), m.group(2).strip()) if m else (szybka.cap(line), ""))
    return out[:6]


def find_stats(paras):
    """Liczby procentowe z copy: etykieta = nagłówek nad nimi (krótka linia / z ':') albo początek zdania,
    notatka = fragment po liczbie. Automat nie rozumie treści - w uwagach każemy sprawdzić."""
    out, seen, header = [], set(), ""
    for p in paras:
        p = re.sub(r"\s+", " ", p.replace("\xa0", " ")).strip()
        if not p:
            continue
        if not re.search(r"\d{1,3}\s*%", p):
            if len(p) < 80 and (p.endswith(":") or not p.endswith((".", "!", "?"))):
                header = re.sub(r"\s*-\s*nag[łl]ówek\s*$", "", p.rstrip(":").strip(), flags=re.I)
            continue
        for m in re.finditer(r"(\d{1,3})\s*%", p):
            before = p[:m.start()].strip(" -–—:,;")
            after = re.split(r"[.;]", p[m.end():].strip(" -–—:,;"))[0]
            label = before if len(before.split()) >= 3 else header
            if label and len(label) > 50:
                label = " ".join(label.split()[-6:])
            label = szybka.cap(label) if label else ""
            note = " ".join(after.split()[:12])
            if not label and not note:
                continue
            key = (m.group(1), (label + note).lower())
            if key in seen:
                continue
            seen.add(key)
            out.append({"value": m.group(1) + "%", "label": label or szybka.cap(note), "note": note if label else ""})
    return out


def split_copy(paras):
    """Copy -> (akapity prozy, zdanie o źródle badania, liczby). Linie z procentami i informacja o badaniu
    nie są 'tekstem o produkcie' - idą na slajd z wynikami i do stopki źródła."""
    src = [p for p in paras if re.search(r"badani\w*\s+(wykona|przeprowadz|zrealizow)", p, re.I)]
    src_line = ""
    if src:
        src_line = szybka.cap(re.sub(r"^.*?na dole\s*[-–—:]\s*", "", src[0]).strip().rstrip("."))
    prose = [p for p in paras if p not in src and not re.search(r"\d{1,3}\s*%", p)]
    return prose, src_line, find_stats(paras)


def _thumb_file(path, size=160):
    try:
        im = Image.open(path)
        im.thumbnail((size, size))
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        buf = io.BytesIO()
        bg.convert("RGB").save(buf, "JPEG", quality=80)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return None


def _legal(s):
    t = s["nazwa_prawna"]
    return t if len(t) <= 80 else t.split(",")[0]


def chunk_copy(paras, max_chars=650):
    """Akapity copy -> slajdy (tytuł, [akapity]). Krótka linia bez kropki = nagłówek następnego slajdu."""
    slides, cur, title = [], [], None
    for p in paras:
        p = re.sub(r"\s*-\s*nag[łl]ówek\s*$", "", p.strip(), flags=re.I)
        if len(p) < 70 and not p.rstrip().endswith((".", "!", "?")) and not cur:
            title = p.rstrip(":")
            continue
        if cur and sum(map(len, cur)) + len(p) > max_chars:
            slides.append((title, cur))
            cur, title = [], None
        cur.append(p)
    if cur:
        slides.append((title, cur))
    return slides[:4]


def _num_claim(text):
    m = re.match(r"^\s*(\d+\s*%|\d+\s*(?:g|mg|kcal))\s+(.+)$", text, re.I)
    return (m.group(1).replace(" ", ""), m.group(2)) if m else None


# --- 2. układ slajdów ---------------------------------------------------------------------------------------------
def compose(inv, g, o):
    skus = inv["smaki"]
    fl = [s["smak"] for s in skus]
    produkt = inv["produkt"]
    styl = o.get("styl", "nowy")
    tekst = int(o.get("tekst", 1))
    sek = set(o.get("sekcje") or LENGTH_PRESETS[int(o.get("dlugosc", 1))]) | {"koniec"}  # okładka do wyłączenia (30.09)
    extra = [x for x in (o.get("sekcje") or []) if re.fullmatch(r"t\d\d", str(x))]
    extra.sort(key=lambda x: [i for i, (n, _g, _t) in enumerate(EXTRA) if "t%02d" % n == x][0])
    uwagi = []
    have = [g["pack"].get(f) for f in fl if g["pack"].get(f)]
    trio = have[:3] if len(have) >= 3 else (have[0] if have else None)
    prod = g["produkt"]
    pool = [g["props"].get(f, []) for f in fl] + [prod]
    mix = []
    for i in range(6):
        src = pool[i % len(pool)]
        if src:
            mix.append(src[(i // len(pool)) % len(src)])
    fruit_mix = [m for m in mix if m not in prod] or mix

    def props_for(f):
        own = g["props"].get(f, [])[:4]
        return (own + prod[:2] + own[4:6])[:6]

    claims = parse_claims(o.get("claimy")) or \
        [(szybka.cap(c), "") for c in sorted({c for s in skus for c in s["claimy_front"]}, key=len)[:4]]
    grid = [(szybka.cap(c), "") for c in _common_claims(skus)]
    fruits = sorted({s["owoce"] for s in skus if s["owoce"]})
    if fruits:
        grid.append(("%s owoców" % "-".join(fruits), "w składzie"))
    polska = bool(skus) and all(s["polska_firma_rodzinna"] for s in skus)
    if polska:
        grid.append(("Polska firma rodzinna", "Kubara"))
    prose, src_copy, stats = split_copy(inv["copy"])
    copy_slides = chunk_copy(prose) if "copy" in sek else []
    if tekst == 0:
        copy_slides = copy_slides[:1]
    stats = stats[:4]
    src_badanie = ("Badanie: " + src_copy) if src_copy else (
        ("Badanie: " + os.path.splitext(inv["badania"][0])[0].replace("_", " ")) if inv["badania"]
        else "[Źródło: kto, kiedy, próba]")
    n_smaki = {2: "Dwa smaki", 3: "Trzy smaki", 4: "Cztery smaki"}.get(len(skus), "Linia smaków")
    trio_dicts = [{"path": p, "shadow_color": "3B2A20", "name": "!!pack_%d" % i} for i, p in enumerate(have[:3])]
    packs_any = have[:1] and [{"path": have[0], "shadow_color": "3B2A20", "name": "!!pack"}]
    sl = []

    if styl == "nowy":
        cover = {"type": "cover", "variant": 4, "kicker": "Nowość", "title": produkt, "image": trio, "props": mix[:4]}
        if tekst == 2 and claims:
            cover["subtitle"] = ". ".join(t for t, _ in claims[:2]) + "."
        if "okladka" in sek:
            sl.append(cover)
        tpl = dict(zip(extra, template_slides(extra, produkt, fl, have, mix, claim=(claims[0][0] + ".") if claims else "")))
        front = [x for x in extra if x in ("t04", "t05", "t06", "t07", "t08", "t09", "t10")]  # okładki i agenda na początek
        back = [x for x in extra if x == "t60"]
        sl += [tpl[x] for x in front]
        if "smaki" in sek and len(skus) > 1:
            items = []
            for s in skus:
                it = {"key": szybka.slug(s["smak"]), "name": s["smak"], "meta": s["masa"],
                      "title": "%s %s" % (produkt, s["smak"].lower()), "image": g["pack"].get(s["smak"]),
                      "props": props_for(s["smak"])[:3], "tint": "card"}
                if tekst == 2:
                    it["text"] = ("%s owoców · " % s["owoce"] if s["owoce"] else "") + "EAN " + s["ean"]
                items.append(it)
            sl.append({"type": "line", "title": n_smaki + " na start", "items": items})
        if "wyroznia" in sek and claims:
            sl.append({"type": "icon_list", "title": "Co wyróżnia " + produkt.lower(), "pack": trio, "props": mix[:3],
                       "items": [{"icon": szybka.icon_for(t), "title": t,
                                  "text": (d or ("[Jedno zdanie: co to daje klientowi]" if tekst == 2 else "")) if tekst >= 1 else ""}
                                 for t, d in claims[:4]]})
        if "sklad" in sek and grid:
            g4 = [x for x in grid if x[0].lower() not in {t.lower() for t, _ in claims}][:4]
            if len(g4) < 3:  # bez własnych claimów "skład" miałby 1-2 kafle - lepiej pełny zestaw z kart
                g4 = grid[:4]
                if not parse_claims(o.get("claimy")):
                    uwagi.append("'Dobry skład' powtarza oświadczenia z kart - wpisz własne claimy (pole 'Claimy'), "
                                 "żeby slajd 'Co wyróżnia' mówił o czymś innym.")
            sl.append({"type": "tiles", "title": "Dobry skład", "items": [
                {"title": t, "text": (d or "[krótkie rozwinięcie]") if tekst == 2 else "",
                 "image": fruit_mix[i % len(fruit_mix)] if fruit_mix else None,
                 "rot": [-10, 0, 12, -6][i % 4]} for i, (t, d) in enumerate(g4)]})
        if "wartosci" in sek and any(s["wartosci"] for s in skus):
            s0 = next(s for s in skus if s["wartosci"])
            note = "Wartości dla smaku %s." % s0["smak"] if len(skus) > 1 else ""
            sl.append({"type": "nutrition", "title": "Wartości odżywcze", "image": g["pack"].get(s0["smak"]),
                       "props": props_for(s0["smak"])[:4], "head": ["Wartość odżywcza", "100 g", s0["masa"] or "porcja"],
                       "rows": [r[:3] for r in s0["wartosci"]][:9], "note": note or None})
        if "karty_smakow" in sek:
            for i, s in enumerate(skus):
                p = g["pack"].get(s["smak"])
                tint, deep = szybka.tint_deep(p) if p else ("F7E6DE", "A3302A")
                sl.append({"type": "flavor", "key": szybka.slug(s["smak"]), "kicker": "Smak %d/%d" % (i + 1, len(skus)),
                           "name": s["smak"], "text": _legal(s) + "." if tekst >= 1 else "",
                           "facts": [{"value": s["owoce"] or "-", "label": "owoców w składzie"},
                                     {"value": "0%" if any("cukr" in c.lower() for c in s["claimy_front"]) else "-",
                                      "label": "dodatku cukru"}, {"value": s["masa"], "label": "opakowanie"}],
                           "ean": s["ean"], "tint": tint, "deep": deep, "image": p, "props": props_for(s["smak"]),
                           "rot": [-4, 4, -3, 3][i % 4], "morph": i > 0})
        for i, (title, paras) in enumerate(copy_slides):
            sl.append({"type": "article", "title": title or ("O produkcie" if i == 0 else "O produkcie (cd.)"),
                       "paragraphs": paras, "props": (fruit_mix + prod)[:4]})
        if "badanie" in sek:
            sl.append({"type": "section", "variant": "dark", "number": "Badanie", "title": "Co mówią konsumenci",
                       "subtitle": src_badanie if inv["badania"] else "", "image": have[-1] if have else None,
                       "props": mix[:4]})
            if len(stats) >= 2:
                sl.append({"type": "kpis", "kicker": "Badanie konsumenckie", "title": "Wyniki badania",
                           "items": [{"value": s["value"], "label": s["label"],
                                      "note": s.get("note", "") if tekst >= 1 else ""} for s in stats],
                           "highlight": 0, "source": src_badanie})
                uwagi.append("Liczby z badania wzięte automatycznie z copy - sprawdź opisy przy procentach.")
            else:
                sl.append({"type": "hero_stat", "kicker": "Badanie konsumenckie", "title": "[Tytuł: wniosek z badania]",
                           "value": "[00%]", "label": "[Czego dotyczy liczba i w jakiej grupie]", "image": have[0] if have else None,
                           "props": mix[:4], "items": [{"value": "[00%]", "label": "[liczba pomocnicza]"}],
                           "source": src_badanie})
                uwagi.append("Slajd 'Wyniki badania' ma podpowiedzi w [nawiasach] - wpisz liczby z badania.")
        if "film" in sek and o.get("film"):
            t, d = claims[0] if claims else (produkt, "")
            sl.append({"type": "media", "title": "Zobacz film o produkcie", "claim_image": (prod + fruit_mix)[0] if (prod + fruit_mix) else None,
                       "claim_title": t, "text": d or "[1-2 zdania: dlaczego ten produkt jest ważny dla odbiorcy]",
                       "media_title": "Zapraszamy do obejrzenia filmu", "link": o["film"].strip()})
        sl += [tpl[x] for x in extra if x not in front and x not in back]
        sl.append({"type": "end", "contact": "halo@dobrakaloria.pl  ·  dobrakaloria.pl"})
        sl += [tpl[x] for x in back]
        if extra:
            uwagi.append("Slajdy z szablonu (%d) mają podpowiedzi w [nawiasach] - uzupełnij je albo użyj przycisku "
                         "Claude / ChatGPT / Gemini." % len(extra))
        theme, label = "shop", "nowy styl"
    else:  # stary styl (klasyczny DK_WZÓR, build_deck)
        cover = {"type": "cover", "kicker": "Nowość", "title": produkt, "images": trio_dicts or packs_any or []}
        if len(fl) > 1:
            cover["subtitle"] = [", ".join(fl[:2]), ", ".join(fl[2:])] if len(fl) > 2 else [", ".join(fl)]
        if "okladka" in sek:
            sl.append(cover)
        if extra:
            uwagi.append("Slajdy z szablonu są tylko w nowym stylu - pominięto %d." % len(extra))
        if "smaki" in sek and len(skus) > 1:
            sl.append({"type": "skus", "title": n_smaki + " na start", "items": [
                {"name": s["smak"], "meta": s["masa"], "ean": s["ean"] if tekst == 2 else None,
                 "path": g["pack"].get(s["smak"]), "shadow_color": "3B2A20"} for s in skus]})
        if "wyroznia" in sek and claims:
            sl.append({"type": "product", "title": "Co wyróżnia " + produkt.lower(),
                       "bullets": [t + (" – " + d if d and tekst == 2 else "") for t, d in claims[:5]],
                       "images": trio_dicts or packs_any or [],
                       "props": [{"path": mix[0], "w": 2.0, "anchor": "bl", "dx": -0.4, "dy": -0.6, "rot": -12}] if mix else [],
                       "callouts": [{"kind": "polska", "x": 4.6, "y": 15.4, "w": 6.8}] if polska else []})
        if "sklad" in sek and grid:
            nums = [_num_claim(t) for t, _ in grid]
            items = [{"value": v, "label": lab} for n in nums if n for v, lab in [n]]
            if len(items) >= 2:
                sl.append({"type": "stats", "title": "Dobry skład", "items": items[:4],
                           "source": "Wg kart wprowadzenia (wartości wspólne dla wszystkich smaków)."})
            else:
                sl.append({"type": "bullets", "title": "Dobry skład", "bullets": [t for t, _ in grid[:6]]})
        if "wartosci" in sek:
            uwagi.append("Stary styl nie ma tabeli wartości odżywczych - sekcja pominięta (jest w nowym stylu).")
        if "karty_smakow" in sek:
            anchors = [("l", -0.3, -12), ("tr", -0.6, 20), ("bl", 0.8, 8), ("r", 0.3, -10), ("b", 0.0, 25)]
            for s in skus:
                b = [_legal(s)] if tekst >= 1 else []
                b += [x for x in ("%s owoców" % s["owoce"] if s["owoce"] else None,
                                  "0% dodatku cukru" if any("cukr" in c.lower() for c in s["claimy_front"]) else None,
                                  "%s, EAN %s" % (s["masa"], s["ean"])) if x]
                p = g["pack"].get(s["smak"])
                sl.append({"type": "product", "title": "Smak: " + s["smak"].lower(), "text_w": 14.5, "bullets": b,
                           "images": [{"path": p, "shadow_color": "3B2A20", "name": "!!pack_" + szybka.slug(s["smak"])}] if p else [],
                           "props": [{"path": q, "w": 2.3, "anchor": a, "dx": dx, "rot": r}
                                     for q, (a, dx, r) in zip(props_for(s["smak"])[:5], anchors)]})
        for i, (title, paras) in enumerate(copy_slides):
            sl.append({"type": "article", "title": title or ("O produkcie" if i == 0 else "O produkcie (cd.)"),
                       "paragraphs": paras, "props": (fruit_mix + prod)[:4]})
        if "badanie" in sek:
            if len(stats) >= 2:
                sl.append({"type": "stats", "title": "Świetne wyniki badania konsumenckiego",
                           "items": [{"value": s["value"], "label": s["label"], "note": s.get("note", "")} for s in stats[:4]],
                           "source": src_badanie})
                uwagi.append("Liczby z badania wzięte automatycznie z copy - sprawdź opisy przy procentach.")
            else:
                sl.append({"type": "stats", "title": "Wyniki badania konsumenckiego", "lead": "[Tytuł: wniosek z badania]",
                           "items": [{"value": "[00%]", "label": "[grupa / czego dotyczy]"},
                                     {"value": "[00%]", "label": "[grupa / czego dotyczy]"}], "source": src_badanie})
                uwagi.append("Slajd 'Wyniki badania' ma podpowiedzi w [nawiasach] - wpisz liczby z badania.")
        if "film" in sek and o.get("film"):
            t, d = claims[0] if claims else (produkt, "")
            sl.append({"type": "media", "title": "Zobacz film o produkcie", "claim_image": (prod + fruit_mix)[0] if (prod + fruit_mix) else None,
                       "claim_title": t, "text": d or "[1-2 zdania: dlaczego ten produkt jest ważny dla odbiorcy]",
                       "media_title": "Zapraszamy do obejrzenia filmu", "link": o["film"].strip()})
        sl.append({"type": "end"})
        theme, label = "classic", "stary styl"
    out_dir = o.get("wyjscie") or inv["folder"]
    return {"theme": theme, "slides": sl, "output": os.path.join(out_dir, "%s - %s.pptx" % (produkt, label)),
            "uwagi": uwagi}


def _apply_packshots(folder, rob, mapa, mapping, say):
    """Ręczne przypisanie packshotów do smaków (okno: klik w miniaturę; CLI: --packshoty). Zapisuje mapę jako
    'recznie' (kolejne uruchomienia ją szanują) i usuwa nieaktualny cache pack_<smak>.png (własny plik programu)."""
    wiz = os.path.join(folder, "Wizualizacje")
    changed = False
    for smak, plik in (mapping or {}).items():
        if not plik:
            continue
        src = os.path.join(wiz, os.path.basename(plik))
        if not os.path.exists(src):
            say("Packshot nie istnieje, pomijam: " + plik)
            continue
        if os.path.normcase(mapa["packshoty"].get(smak, "")) != os.path.normcase(src):
            mapa["packshoty"][smak] = src
            changed = True
            stale = os.path.join(rob, "pack_%s.png" % szybka.slug(smak))
            if os.path.exists(stale):
                os.remove(stale)
            say("Packshot %s -> %s" % (smak, plik))
    if changed:
        mapa["recznie"] = True
        mapa["niepewne"] = []
        json.dump(mapa, open(os.path.join(rob, "mapa_grafik.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)


# --- 3. budowa ----------------------------------------------------------------------------------------------------
def _build_classic(spec, out):
    deck = build_deck.Deck()
    for sl in spec["slides"]:
        n0 = len(deck.prs.slides)
        build_deck.BUILDERS[sl["type"]](deck, sl)
        if sl.get("morph") is True and len(deck.prs.slides) > n0:
            build_deck.add_morph(deck.prs.slides[n0])
    return deck.finish(out)


def _ps(script, *args, timeout=900):
    q = lambda s: "'" + s.replace("'", "''") + "'"  # noqa: E731
    cmd = "[Console]::OutputEncoding=[Text.Encoding]::UTF8; & %s %s" % (
        q(script), " ".join(a if a.startswith("-") else q(a) for a in args))
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                       capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=timeout)
    return (r.stdout + r.stderr).decode("utf-8", "replace")


def _thumbs(png_dir, width=480):
    out = []
    for f in sorted(glob.glob(os.path.join(png_dir, "s*.png"))):
        im = Image.open(f).convert("RGB")
        im.thumbnail((width, width))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82)
        out.append("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii"))
    return out


def ai_prompt(pptx, folder, uwagi):
    lines = ["Popraw prezentację \"%s\" utworzoną automatycznie z folderu \"%s\"." % (pptx, folder),
             "Najpierw przeczytaj instrukcję: \"%s\" (jak działa program i jak sprawdzić wynik)." % paths.AGENTS_MD,
             "Zadania: 1) uzupełnij teksty w [nawiasach] danymi z folderu (copy, karty wprowadzenia, badanie); "
             "2) każda liczba ma mieć źródło; 3) nie zmieniaj układu, kolorów ani czcionek; "
             "4) na końcu uruchom kontrolę opisaną w instrukcji i pokaż mi zrzuty slajdów."]
    if uwagi:
        lines.append("Uwagi z programu:")
        lines += [" - " + u for u in uwagi]
    return "\n".join(lines)


# klucz: (nazwa, adres w przeglądarce, nazwa aplikacji w menu Start albo None)
AI_CHATS = {"claude": ("Claude", "https://claude.ai/new", "Claude"),
            "chatgpt": ("ChatGPT", "https://chatgpt.com/", "ChatGPT"),
            "gemini": ("Gemini", "https://gemini.google.com/app", None)}


def find_app(name):
    """AppID aplikacji z menu Start o dokładnie tej nazwie (np. Claude) albo None."""
    if not name or not re.fullmatch(r"[A-Za-z0-9 ]+", name):
        return None
    try:
        cmd = "(Get-StartApps | Where-Object { $_.Name -eq '%s' } | Select-Object -First 1).AppID" % name
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
                           capture_output=True, text=True, timeout=15, creationflags=0x08000000)
        app = (r.stdout or "").strip().splitlines()
        return app[0].strip() if app and app[0].strip() else None
    except Exception:
        return None
_NOT_TEXT = re.compile(r"\.(png|jpe?g|tiff?|gif|webp|svg|mp4|pptx|xlsx|docx)$|^[A-Za-z]:[\\/]|^https?://|^[0-9A-Fa-f]{6}$|^[a-z0-9_-]+$", re.I)
_SKIP_KEYS = {"type", "theme", "image", "images", "icon", "icons", "video", "thumb", "poster", "output", "layout",
              "variant", "color", "bg", "props", "pack", "scene"}


def _slide_texts(node):
    """Wszystkie teksty slajdu ze specu (bez ścieżek, nazw plików, kolorów i nazw technicznych)."""
    out = []
    if isinstance(node, str):
        t = " ".join(node.split())
        if t and not (_NOT_TEXT.search(t) and " " not in t):
            out.append(t)
    elif isinstance(node, dict):
        for k, v in node.items():
            if k not in _SKIP_KEYS:
                out += _slide_texts(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            out += _slide_texts(v)
    return out


def ai_prompt_chat(nazwa, inv, spec, uwagi, qa=None, max_copy=7000, pptx=None, folder=None):
    """Polecenie dla zwykłego czatu (Claude / ChatGPT / Gemini): cała treść jest w środku, czat nie potrzebuje
    dostępu do dysku. Użytkownik tylko wkleja."""
    smaki = ", ".join(s.get("smak", "") for s in inv.get("smaki", []) if s.get("smak"))
    L = ["Pomóż mi dokończyć prezentację handlową produktu marki Dobra Kaloria.",
         "Program przygotował wersję roboczą pliku \"%s\". Poniżej masz całą jej treść i materiały źródłowe." % nazwa,
         ""]
    if pptx and folder:
        L += ["PLIKI NA KOMPUTERZE",
              "Plik prezentacji: %s" % pptx,
              "Folder produktu (karty, copy, grafiki): %s" % folder,
              "Instrukcja programu: %s" % paths.AGENTS_MD,
              "Program w wersji dla AI: %s" % os.path.join(paths.ROOT, "pliki programu", "stworz-cli.exe"),
              "Jeśli masz dostęp do plików (Claude w trybie Cowork albo Code): przeczytaj instrukcję, otwórz folder "
              "i popraw prezentację bezpośrednio w pliku. Jeśli nie masz dostępu do plików: odpowiedz samymi "
              "tekstami według punktów poniżej.", ""]
    L += ["PRODUKT: %s" % inv.get("produkt", ""), "SMAKI: %s" % (smaki or "brak danych"), "",
         "CO MASZ ZROBIĆ",
         "1. Dla każdego slajdu podaj gotowe teksty do wklejenia. Tekst w [nawiasach kwadratowych] to miejsce do "
         "uzupełnienia: zastąp je treścią z materiałów poniżej.",
         "2. Odpowiedz listą: numer slajdu, nazwa pola (tytuł, opis, punkt), gotowy tekst. Bez wstępu i bez komentarza.",
         "3. Liczby i fakty bierz tylko z materiałów poniżej. Czego w nich nie ma, oznacz jako BRAK DANYCH. Niczego nie wymyślaj.",
         "4. Pisz krótko: tytuł do 8 słów, opis do 2 zdań, punkt do 10 słów. Tytuł ma być wnioskiem, nie etykietą.",
         "5. Język polski. Nie kończ wiersza na „a, i, o, u, w, z”. Bez wykrzykników i bez języka reklamowego.",
         "6. Nie zmieniaj kolejności slajdów, nie dodawaj nowych.", "", "SLAJDY W PREZENTACJI"]
    for i, s in enumerate(spec.get("slides", []), 1):
        L.append("Slajd %d (%s):" % (i, s.get("type", "")))
        seen = []
        for t in _slide_texts(s):
            if t not in seen:
                seen.append(t)
                L.append("  - " + t)
        if not seen:
            L.append("  - (sam obraz, bez tekstu)")
    copy = [" ".join(str(p).split()) for p in (inv.get("copy") or []) if str(p).strip()]
    L += ["", "MATERIAŁ ŹRÓDŁOWY: COPY"]
    if copy:
        used = 0
        for p in copy:
            if used + len(p) > max_copy:
                L.append("(dalsza część copy pominięta - za długa)")
                break
            L.append(p)
            used += len(p)
    else:
        L.append("(w folderze nie było pliku z copy)")
    fakty = []
    for s in inv.get("smaki", []):
        def txt(v):
            return ", ".join(str(x) for x in v) if isinstance(v, (list, tuple)) else str(v)
        bits = ["%s: %s" % (n, txt(s[k])) for k, n in (("nazwa_handlowa", "nazwa"), ("masa", "masa"), ("ean", "EAN"),
                                                       ("owoce", "owoce"), ("claimy_front", "oświadczenia na opakowaniu"))
                if s.get(k)]
        fakty.append("Smak %s - %s" % (s.get("smak", "?"), "; ".join(bits)))
        rows = [r for r in (s.get("wartosci") or []) if isinstance(r, (list, tuple)) and len(r) >= 2]
        if rows:
            fakty.append("  wartości odżywcze (w 100 g%s): %s" % (
                " / w porcji" if len(rows[0]) > 2 else "",
                "; ".join("%s %s" % (r[0], " / ".join(str(x) for x in r[1:])) for r in rows)))
    if fakty:
        L += ["", "MATERIAŁ ŹRÓDŁOWY: KARTY WPROWADZENIA"] + fakty
    if inv.get("badania"):
        L += ["", "BADANIE: %s (liczby z badania są już na slajdach powyżej)" % ", ".join(inv["badania"])]
    if uwagi:
        L += ["", "UWAGI PROGRAMU (braki do uzupełnienia)"] + [" - " + u for u in uwagi]
    if qa and qa.get("szczegoly"):
        L += ["", "KONTROLA TEKSTU WYKRYŁA"] + [" - " + x for x in qa["szczegoly"][:12]]
    return "\n".join(L)


def build(folder, opts, progress=None, log=None, cancel=None):
    """Główna praca. progress(krok_id, opis, procent, eta_s); log(tekst); cancel = threading.Event."""
    t0 = time.time()
    folder = normalize_folder(folder)
    opts = dict(opts or {})
    est_total = float(opts.get("szacowany_czas_s") or 40)
    done_w = 0

    def emit(step, opis, frac):
        nonlocal done_w
        w = dict((s, wt) for s, _, wt in STEPS)[step]
        pct = min(99, int(done_w + w * max(0.0, min(1.0, frac))))
        el = time.time() - t0
        eta = max(1, int(el / pct * (100 - pct))) if pct >= 8 else max(1, int(est_total - el))
        if progress:
            progress(step, opis, pct, eta)
        _log_file("%3d%% %s" % (pct, opis))

    def finish_step(step):
        nonlocal done_w
        done_w += dict((s, wt) for s, _, wt in STEPS)[step]

    def check():
        if cancel is not None and cancel.is_set():
            raise Cancelled()

    def say(t):
        _log_file(t)
        if log:
            log(t)

    rob = os.path.join(folder, "_robocze")
    os.makedirs(rob, exist_ok=True)
    # 1. inwentarz (z cache po analizie)
    emit("folder", "Czytam folder", 0)
    if folder in _cache:
        inv, mapa = _cache[folder]
    else:
        inv, mapa = szybka.inventory(folder, rob)
    say("Produkt: %s, smaki: %s" % (inv["produkt"], ", ".join(s["smak"] for s in inv["smaki"])))
    if opts.get("packshoty"):
        _apply_packshots(folder, rob, mapa, opts["packshoty"], say)
    finish_step("folder")
    check()
    # 2. grafiki (jak szybka.prep_all, ale z postępem i przerwaniem)
    el_dir = os.path.join(rob, "el")
    os.makedirs(el_dir, exist_ok=True)
    jobs = []
    for fl, f in mapa["packshoty"].items():
        jobs.append(("pack", fl, f, os.path.join(rob, "pack_%s.png" % szybka.slug(fl)), 1400))
    for fl, files in mapa["elementy"].items():
        for f in szybka.diversify(files, 10):
            jobs.append(("props", fl, f, os.path.join(el_dir, "p_%s.png" % szybka.slug(os.path.splitext(os.path.basename(f))[0])), 520))
    for f in szybka.diversify(mapa["produkt"], 8):
        jobs.append(("produkt", None, f, os.path.join(el_dir, "k_%s.png" % szybka.slug(os.path.splitext(os.path.basename(f))[0])), 700))
    g = {"pack": {}, "props": {fl: [] for fl in mapa["elementy"]}, "produkt": []}
    for i, (kind, fl, src, dst, side) in enumerate(jobs):
        emit("grafiki", "Przygotowuję grafiki (%d/%d)" % (i + 1, len(jobs)), i / max(1, len(jobs)))
        check()
        try:
            res = szybka.prep(src, dst, side)
        except Exception as e:  # jedna zła grafika nie zatrzymuje całości
            say("Pominięto grafikę %s: %s" % (os.path.basename(src), e))
            continue
        if kind == "pack":
            g["pack"][fl] = res
        elif kind == "props":
            g["props"][fl].append(res)
        else:
            g["produkt"].append(res)
    finish_step("grafiki")
    # 3. układ
    emit("slajdy", "Układam slajdy", 0.3)
    spec = compose(inv, g, opts)
    uwagi = list(spec.pop("uwagi", []))
    json.dump(spec, open(os.path.join(rob, "spec_program.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("slajdy")
    check()
    # 4. budowa
    emit("budowa", "Buduję prezentację (%d slajdów)" % len(spec["slides"]), 0.1)
    out = spec["output"]
    if spec["theme"] == "classic":
        pptx = _build_classic(spec, out)
    else:
        build_dk.build(spec, out)
        pptx = build_dk.build.last_out
    if os.path.abspath(pptx) != os.path.abspath(out):
        uwagi.append("Plik '%s' był otwarty albo zmieniony ręcznie - zapisano jako '%s'."
                     % (os.path.basename(out), os.path.basename(pptx)))
    say("Zapisano: " + pptx)
    finish_step("budowa")
    check()
    # 5. QA w PowerPoint (czcionki, zrzuty, kontrola tekstu)
    qa = {"problemy": None, "szczegoly": [], "wykonano": False}
    thumbs = []
    if powerpoint_available() and not opts.get("bez_qa"):
        name = os.path.splitext(os.path.basename(pptx))[0]
        png = os.path.join(rob, "qa", name)
        emit("qa", "Osadzam czcionki i robię zrzuty slajdów", 0.15)
        for old in glob.glob(os.path.join(png, "s*.png")):  # stare zrzuty (własne pliki) - inaczej dłuższa poprzednia
            os.remove(old)                                    # wersja zostawiłaby nadmiarowe miniatury
        r = _ps(paths.RENDER_PS, "-Src", pptx, "-Out", png)
        say(r.strip()[-300:])
        guard.record(pptx)  # PowerPoint zapisał plik od nowa - odśwież sumę (inaczej następna budowa uzna go za ręczny)
        emit("qa", "Sprawdzam tekst (sieroty, kolizje, krawędzie)", 0.6)
        rep = _ps(paths.VERIFY_PS, "-Src", pptx)
        m = re.search(r"Tekst - problemy:\s*(\d+)", rep)
        qa["wykonano"] = bool(m)
        qa["problemy"] = int(m.group(1)) if m else None
        qa["szczegoly"] = [l.strip() for l in rep.splitlines() if re.match(r"\s{3}s\d+ ", l)]
        emit("qa", "Przygotowuję podgląd", 0.9)
        thumbs = _thumbs(png)
    elif opts.get("bez_qa"):
        say("Pominięto PowerPoint (--bez-qa): bez osadzania czcionek i kontroli tekstu.")
    else:
        say("PowerPoint niedostępny - pomijam osadzanie czcionek i kontrolę tekstu.")
        uwagi.append("Nie sprawdzono w PowerPoint (brak PowerPointa na tym komputerze).")
    finish_step("qa")
    emit("zapis", "Zapisuję raport", 0.5)
    result = {"ok": True, "pptx": pptx, "nazwa": os.path.basename(pptx), "folder": folder, "slajdy": len(spec["slides"]),
              "czas_s": int(time.time() - t0), "miniatury": thumbs, "qa": qa, "uwagi": uwagi,
              "prompt_ai": ai_prompt_chat(os.path.basename(pptx), inv, spec, uwagi, qa, pptx=pptx, folder=folder),
              "prompt_agent": ai_prompt(pptx, folder, uwagi), "styl": opts.get("styl", "nowy")}
    json.dump({k: v for k, v in result.items() if k != "miniatury"},
              open(os.path.join(rob, "raport.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("zapis")
    if progress:
        progress("zapis", "Gotowe", 100, 0)
    return result


def safe_build(*a, **kw):
    try:
        return build(*a, **kw)
    except Cancelled:
        return {"ok": False, "blad": "Przerwano.", "przerwano": True}
    except Exception as e:
        _log_file(traceback.format_exc())
        return {"ok": False, "blad": "%s: %s" % (type(e).__name__, e), "traceback": traceback.format_exc()}
