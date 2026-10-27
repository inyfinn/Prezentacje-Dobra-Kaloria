# -*- coding: utf-8 -*-
"""Folder prezentacji (wersja 1.3): jeden folder na prezentację, w nim Źródła (KOPIE plików), scenariusze, wyniki i _robocze.

Czyste funkcje bez okna: propozycja folderu (baza + data + tytuł), kopiowanie źródeł, rozpoznanie folderu prezentacji,
wersje scenariuszy (scenariusz.md, scenariusz-2.md…) i wyników (<nazwa>.pptx, <nazwa> v2.pptx…), zapamiętane ustawienia.
Niczego tu nie kasujemy ani nie przenosimy: pliki użytkownika są tylko kopiowane."""
import json
import os
import re
import shutil
import time

import paths
import platforma

M_BAZA = r"M:\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE"
ZRODLA = "Źródła"
MAX_TYTUL = 60
OBRAZ_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff")
PPTX_EXT = (".pptx", ".ppsx", ".potx", ".pptm")
ZAREZERWOWANE = {"CON", "PRN", "AUX", "NUL"} | {"COM%d" % i for i in range(1, 10)} | {"LPT%d" % i for i in range(1, 10)}
_SCEN = re.compile(r"^scenariusz(?:-(\d+))?\.md$", re.I)
_NAGLOWEK = re.compile(r"^\s*(?:```[A-Za-z]*\s*\n)?\s*#\s*SCENARIUSZ\s+DK\b", re.I)
_TYTUL_LINIA = re.compile(r"^\s*tytu[łl]\s*:\s*(.+?)\s*$", re.I | re.M)


# --- ustawienia zapamiętane między uruchomieniami -------------------------------------------------------------------
def plik_ustawien():
    return os.path.join(paths.USER_DIR, "ustawienia.json")


def ustawienia():
    try:
        with open(plik_ustawien(), encoding="utf8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def zapisz_ustawienie(klucz, wartosc):
    """Dopisuje jeden klucz do ustawienia.json (reszta zostaje). Błąd zapisu nie przerywa pracy: zwraca False."""
    d = ustawienia()
    d[klucz] = wartosc
    p = plik_ustawien()
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p + ".tmp", "w", encoding="utf8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(p + ".tmp", p)
        return True
    except OSError:
        return False


# --- baza i nazwa folderu --------------------------------------------------------------------------------------------
def baza_m():
    """Folder prezentacji firmy na dysku M:. DK_PREZ_BAZA podmienia go (testy, inny dysk). Na Macu nie ma dysku M: - pusta baza,
    więc domyślnie wybierane są Dokumenty."""
    return os.environ.get("DK_PREZ_BAZA") or ("" if platforma.mac() else M_BAZA)


def zapisywalny(d):
    return bool(d) and os.path.isdir(d) and os.access(d, os.W_OK)


def dokumenty_baza():
    return os.path.join(os.path.expanduser("~"), "Documents", "Prezentacje Dobra Kaloria")


def baza_domyslna():
    """(baza, m_dostepny): ostatnio użyta (jeśli nadal istnieje) -> M:\\…\\PREZENTACJE -> Dokumenty\\Prezentacje Dobra Kaloria."""
    m = zapisywalny(baza_m())
    ost = ustawienia().get("baza_prezentacji")
    if isinstance(ost, str) and zapisywalny(ost):
        return ost, m
    return (baza_m() if m else dokumenty_baza()), m


def oczysc_tytul(t, limit=MAX_TYTUL):
    """Tytuł nadaje się na nazwę folderu i pliku w Windows: bez <>:"/\\|?*, bez kropki i spacji na końcu, do `limit` znaków
    (cięcie na granicy słowa, gdy zostaje sensowna długość)."""
    t = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", str(t or ""))
    t = " ".join(t.split()).strip(" .")
    litery = [c for c in t if c.isalpha()]
    if len(litery) > 3 and all(c.isupper() for c in litery):   # tytuł z PDF wersalikami: w nazwie folderu zwykła wielkość liter
        t = t[:1] + t[1:].lower()
    if len(t) > limit:
        c = t[:limit]
        if t[limit] != " " and " " in c and c.rfind(" ") >= limit // 2:
            c = c[:c.rfind(" ")]
        t = c.rstrip(" .-,;:")
    if t.upper() in ZAREZERWOWANE:
        t += "_"
    return t or "Prezentacja"


def nazwa_folderu(tytul, data=None):
    return "%s - %s" % (data or time.strftime("%Y-%m-%d"), oczysc_tytul(tytul))


def unikalna_sciezka(baza, nazwa, ext=""):
    """baza\\nazwa<ext>; gdy zajęta: „nazwa (2)<ext>”, „nazwa (3)<ext>”… Nigdy nie nadpisuje istniejącego."""
    p = os.path.join(baza, nazwa + ext)
    n = 2
    while os.path.exists(p):
        p = os.path.join(baza, "%s (%d)%s" % (nazwa, n, ext))
        n += 1
    return p


# --- pliki wejściowe ----------------------------------------------------------------------------------------------------
def typ_pliku(p, dok_ext=()):
    e = os.path.splitext(p)[1].lower()
    if e in PPTX_EXT:
        return "pptx"
    if e in OBRAZ_EXT:
        return "obraz"
    if e in dok_ext:
        return "dokument"
    return "inny"


def rozmiar_tekst(n):
    for jedn, dz in (("GB", 1 << 30), ("MB", 1 << 20), ("KB", 1 << 10)):
        if n >= dz:
            return ("%.1f %s" % (n / dz, jedn)).replace(".", ",")
    return "%d B" % n


def opis_pliku(p, dok_ext=()):
    try:
        r = os.path.getsize(p)
    except OSError:
        r = 0
    return {"nazwa": os.path.basename(p), "typ": typ_pliku(p, dok_ext), "rozmiar": r, "rozmiar_tekst": rozmiar_tekst(r), "sciezka": p}


def kopiuj_zrodla(pliki, folder):
    """Kopia (shutil.copy2, nigdy move) plików do <folder>\\Źródła. Kolizja nazw: „nazwa (2).ext”. Plik, który już leży w Źródłach
    tego folderu, jest pomijany. Zwraca listę ścieżek kopii; brak pliku źródłowego -> FileNotFoundError."""
    cel = os.path.join(folder, ZRODLA)
    os.makedirs(cel, exist_ok=True)
    wynik = []
    for p in pliki:
        if os.path.normcase(os.path.abspath(os.path.dirname(p))) == os.path.normcase(os.path.abspath(cel)):
            wynik.append(p)
            continue
        if not os.path.isfile(p):
            raise FileNotFoundError(p)
        nazwa, ext = os.path.splitext(os.path.basename(p))
        wynik_p = unikalna_sciezka(cel, nazwa, ext)
        shutil.copy2(p, wynik_p)
        wynik.append(wynik_p)
    return wynik


def utworz_folder(baza, nazwa, pliki):
    """Tworzy <baza>\\<nazwa> (zajęta nazwa -> „ (2)”), kopiuje pliki do Źródła. Zwraca (folder, [kopie])."""
    os.makedirs(baza, exist_ok=True)
    folder = unikalna_sciezka(baza, nazwa)
    os.makedirs(folder)
    return folder, kopiuj_zrodla(pliki, folder)


# --- rozpoznanie folderu prezentacji i scenariusze ---------------------------------------------------------------------
def scenariusze(folder):
    """[(numer wersji, ścieżka)] rosnąco: scenariusz.md = 1, scenariusz-2.md = 2…"""
    try:
        nazwy = os.listdir(folder)
    except OSError:
        return []
    wyn = []
    for n in nazwy:
        m = _SCEN.match(n)
        if m and os.path.isfile(os.path.join(folder, n)):
            wyn.append((int(m.group(1)) if m.group(1) else 1, os.path.join(folder, n)))
    return sorted(wyn)


def czy_folder_prezentacji(folder):
    return bool(folder) and os.path.isdir(folder) and (os.path.isdir(os.path.join(folder, ZRODLA)) or bool(scenariusze(folder)))


def najnowszy_scenariusz(folder):
    """(ścieżka, numer wersji) najwyższego numeru albo (None, 0)."""
    s = scenariusze(folder)
    return (s[-1][1], s[-1][0]) if s else (None, 0)


def nowa_wersja_scenariusza(folder, md):
    """Zapisuje md jako kolejną wersję (pierwsza: scenariusz.md; potem scenariusz-2.md…). Zwraca (ścieżka, numer)."""
    nr = najnowszy_scenariusz(folder)[1] + 1
    p = os.path.join(folder, "scenariusz.md" if nr == 1 else "scenariusz-%d.md" % nr)
    with open(p, "x", encoding="utf8", newline="\n") as f:   # "x": nigdy nie nadpisuje istniejącej wersji
        f.write(md.rstrip() + "\n")
    return p, nr


def nazwa_wyniku(folder, nazwa):
    """<folder>\\<nazwa>.pptx; gdy zajęta: „<nazwa> v2.pptx”, „v3”… (poprzednie wersje zostają)."""
    nazwa = oczysc_tytul(nazwa, 120)
    p = os.path.join(folder, nazwa + ".pptx")
    n = 2
    while os.path.exists(p):
        p = os.path.join(folder, "%s v%d.pptx" % (nazwa, n))
        n += 1
    return p


def tytul_scenariusza(md, zapas=""):
    """Linia „tytuł: …” scenariusza; brak -> `zapas`."""
    m = _TYTUL_LINIA.search(md or "")
    return m.group(1).strip() if m else zapas


def tytul_z_folderu(folder):
    """Nazwa folderu bez przedrostka daty „RRRR-MM-DD - ”."""
    n = os.path.basename(os.path.abspath(folder))
    return re.sub(r"^\d{4}-\d{2}-\d{2}\s*-\s*", "", n) or n


def pliki_zrodel(folder):
    """Pliki w <folder>\\Źródła (bez podfolderów, bez ukrytych i ~$), alfabetycznie."""
    d = os.path.join(folder, ZRODLA)
    try:
        nazwy = sorted(os.listdir(d), key=str.lower)
    except OSError:
        return []
    return [os.path.join(d, n) for n in nazwy if not n.startswith(("~$", ".")) and os.path.isfile(os.path.join(d, n))]


def wyglada_na_scenariusz(tekst):
    """Czysty filtr schowka: po białych znakach (i ewentualnym ```markdown) zaczyna się od „# SCENARIUSZ DK”."""
    return bool(tekst) and bool(_NAGLOWEK.match(tekst))
