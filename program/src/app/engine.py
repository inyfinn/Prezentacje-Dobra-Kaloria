# -*- coding: utf-8 -*-
"""Silnik programu "Stwórz prezentację": folder produktu -> gotowy PPTX.

Owija skill /prezentacje (szybka.py: inwentarz i grafiki; build_dk.py: nowy styl; build_deck.py: stary styl;
verify.ps1: kontrola tekstu w PowerPoint). Deterministyczny - żadnych pytań: czego automat nie wie, wpisuje jako
podpowiedź w [nawiasach] i zgłasza w "uwagi". Ten sam silnik obsługuje okno (gui.py) i wiersz poleceń dla AI (cli.py).

Wejście (normalize_folder / tryb_wejscia): folder produktu, plik .pptx (obca = konwersja; już w stylu marki = DOPRACOWANIE: sam
przegląd, plik użytkownika nietknięty) albo dokument (.docx, .pdf, .txt...).
"""
import base64
import glob
import hashlib
import io
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback

import paths
import folder_prez
import platforma

paths.ensure_user_dirs()
os.environ.setdefault("DK_GUARD_CACHE", os.path.join(paths.USER_DIR, "wygenerowane.json"))
os.environ.setdefault("DK_CACHE_DIR", os.path.join(paths.USER_DIR, "cache"))
sys.path.insert(0, paths.SKILL_SCRIPTS)
import szybka  # noqa: E402
import build_dk  # noqa: E402
import build_deck  # noqa: E402
import guard  # noqa: E402
import make_template  # noqa: E402  - katalog typów slajdów szablonu
import pptx_convert  # noqa: E402  - konwersja gotowej prezentacji (.pptx) na styl DK
import polecenia  # noqa: E402  - polecenia dla AI: jedno źródło tekstów (agent z plikami i czat bez plików)
import polecenia_dok  # noqa: E402  - punkty polecenia dla celu "dokument" (zapas, gdy skill nie ma ich w POLECENIA)
try:  # prezentacja z dokumentu (docx, doc, rtf, odt, pdf, txt, md): moduł skilla; starszy skill go nie ma
    import dokument  # noqa: E402
except ImportError:
    dokument = None
import wizki  # noqa: E402  - biblioteka wizualizacji produktów (packshoty do slajdów portfolio)
szybka.OCR_PS = os.path.join(paths.SKILL_SCRIPTS, "ocr_win.ps1")  # paczki bez smaku w nazwie: napis z opakowania
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

CREATE_NO_WINDOW = 0x08000000
_COM_ERR = re.compile(r"RPC_E_|0x8001|0x800706|COMException|Exception calling|Wyj.tek podczas wywo.ywania|CallRejected", re.I)


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
# Slajdy z szablonu (numer slajdu w szablonie, grupa, nazwa; nazwy jak w assets\katalog-szablonu.json - pilnuje tego
# test_prompty.py). Pominięte: instrukcje (1-2) i typy, które program buduje z danych folderu (okładka 3, zalety 31,
# karta smaku 33, linia 34, wartości 35, kafle 36, film 49, koniec 64).
EXTRA = [(4, "naglowki", "Okładka: paczka na granicy zieleni"), (5, "naglowki", "Okładka: biały tytuł na zieleni"),
         (6, "naglowki", "Okładka klasyczna 50/50"), (7, "naglowki", "Okładka bez produktu 50/50"),
         (8, "naglowki", "Okładka bez produktu na zieleni"), (9, "naglowki", "Okładka bez produktu, jasna"),
         (10, "naglowki", "Agenda"), (11, "naglowki", "Przerywnik rozdziału, ciemny"),
         (12, "naglowki", "Przerywnik rozdziału z numerem"), (65, "naglowki", "Zakończenie z podziękowaniem"),
         (13, "opis", "Wstęp z akapitem"), (15, "opis", "Tekst długi w dwóch kolumnach"),
         (16, "opis", "Akapit w karcie"), (17, "opis", "Punkty"), (18, "opis", "Punkty ze zdjęciem"),
         (19, "opis", "Kroki / proces"), (21, "opis", "Porównanie: dziś i propozycja"),
         (59, "opis", "Dwie karty: dobra i zła wiadomość"), (61, "opis", "Akapit w karcie z wyróżnieniem"),
         (22, "opis", "Tekst i zdjęcie"), (23, "opis", "Zdjęcie i tekst"),
         (24, "cechy", "Tekst i produkt"), (25, "cechy", "Zalety z ikonami i zdjęciem"),
         (30, "cechy", "Anatomia produktu"), (32, "cechy", "Siatka cech z ikonami"),
         (44, "cechy", "Argumenty dla handlu"), (56, "cechy", "Okazje spożycia"),
         (42, "szczegoly", "Tabela"), (43, "szczegoly", "Oś czasu"), (45, "szczegoly", "Logistyka"),
         (54, "szczegoly", "Cena i marża"), (55, "szczegoly", "Porównanie z konkurencją"),
         (47, "szczegoly", "Osoba kontaktowa"), (58, "szczegoly", "Następne kroki"),
         (62, "dane", "Trzy fakty w kartach"), (37, "dane", "Liczba-bohater"), (38, "dane", "Wskaźniki (KPI)"), (39, "dane", "Wykres słupkowy"),
         (40, "dane", "Dwie grupy wyników"), (41, "dane", "A kontra B"), (52, "dane", "Wykres pierścieniowy"),
         (53, "dane", "Wykres kolumnowy"),
         (48, "multimedia", "Film na cały slajd"), (50, "multimedia", "Film z tekstem"),
         (26, "multimedia", "Zdjęcie na cały slajd z podpisem"), (27, "multimedia", "Zdjęcie na cały slajd"),
         (28, "multimedia", "Galeria 3 zdjęć"), (29, "multimedia", "Galeria 6 zdjęć"),
         (51, "multimedia", "Przed i po"), (46, "multimedia", "Karty ze zdjęciem"), (57, "multimedia", "Social media"),
         (63, "multimedia", "Zrzuty w całości i wniosek"),
         (20, "cytaty", "Cytat / opinia"), (60, "cytaty", "Cytat i wniosek"), (14, "cytaty", "Jedno zdanie – teza")]
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


# Konwersja gotowej prezentacji, cel "Rozwiń / dokończ": puste slajdy z szablonu, które można dołożyć. Tylko typy
# bez produktów, zdjęć i wykresów z przykładowymi słupkami - w cudzej prezentacji wyglądałyby jak prawdziwe dane.
PPTX_DODATKI = [10, 11, 13, 15, 17, 19, 21, 42, 43, 58, 38, 40, 41, 20, 14, 65]


def catalog_pptx():
    by = {int(x["id"][1:]): x for x in catalog_extra()}
    return [dict(by[i], grupa="dodatki") for i in PPTX_DODATKI if i in by]


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
ZAJETY_MNOZNIK = 1.5   # po tylu estymatach tekst postępu zmienia się na ZAJETY_TEKST
ZAJETY_TEKST = "Komputer jest zajęty - to potrwa dłużej"
MAX_SCIEZKA_PPT = 225   # PowerPoint (COM) nie otwiera plików ani nie zapisuje zrzutów przy ścieżce > 259 znaków; zapas na nazwy
# Wagi kroków paska postępu (pomiar 13.10 na obciążonym komputerze, dokument 17 slajdów = 49 s: czytanie i składanie ok. 1 s, budowa ok. 0 s,
# zrzuty 27 s, kontrola tekstu 19 s, reszta 1 s): prawie cały czas to PowerPoint, więc pasek nie może skakać do 50% na samym początku.
PPTX_WEIGHTS = {"folder": 5, "grafiki": 1, "slajdy": 7, "budowa": 7, "qa": 74, "zapis": 6}
DOPR_WEIGHTS = {"folder": 8, "grafiki": 0, "slajdy": 0, "budowa": 0, "qa": 82, "zapis": 10}   # dopracowanie: bez budowy slajdów
# Szacunek czasu z liczby slajdów: stały narzut PowerPointa (start, zrzuty, kontrola) + czas na slajd. Pomiary 13.10 (komputer obciążony,
# PowerPoint dzielony z innymi): dokument 5 / 7 / 15 / 17 slajdów = 24 / 31 / 25 / 49 s; dopracowanie 7 / 43 slajdy = 53 / 66 s.
CZAS_DOPR = (25.0, 0.7)       # (stały, na slajd): zrzuty i kontrola kopii, bez budowy
CZAS_PPTX = (20.0, 1.0)       # konwersja (na slajd wyniku): składanie + budowa + zrzuty + kontrola; pomiar 45 slajdów = 57 s bez przebudowy układu, z jedną ok. 90 s


def powerpoint_available():
    """Windows: czy jest PowerPoint (zrzuty i kontrola tekstu przez COM). macOS: zawsze False - budowa idzie bez nich."""
    return platforma.powerpoint_dostepny()


def _log_file(text):
    try:
        with open(os.path.join(paths.LOG_DIR, "ostatni.log"), "a", encoding="utf8") as f:
            f.write(time.strftime("%H:%M:%S ") + text + "\n")
    except OSError:
        pass


PPTX_EXT = (".pptx", ".ppsx", ".potx", ".pptm")
DOK_EXT_ZAPAS = (".docx", ".doc", ".rtf", ".odt", ".pdf", ".txt", ".md")   # lista z kontraktu dokument.ROZSZERZENIA
KOMUNIKAT_PROGRAM = "To folder programu. Upuść folder produktu albo plik z prezentacją lub dokumentem."
KOMUNIKAT_TYP = ("Tego typu pliku nie umiem przeczytać. Upuść folder produktu, prezentację (.pptx) albo dokument "
                 "(.docx, .doc, .rtf, .odt, .pdf, .txt, .md).")
KOMUNIKAT_BEZ_PRZEGLADU = ("Ta wersja programu nie umie jeszcze sprawdzać prezentacji, które są już w stylu marki. "
                           "Zaktualizuj program.")
KOMUNIKAT_BEZ_DOKUMENTOW = ("Ta wersja programu nie czyta jeszcze dokumentów (.docx, .pdf, .txt…). Zaktualizuj program "
                            "albo upuść folder produktu lub prezentację (.pptx).")


def dok_ext():
    """Rozszerzenia dokumentów, które program umie zamienić na prezentację (puste, gdy skill nie ma modułu `dokument`)."""
    return tuple(getattr(dokument, "ROZSZERZENIA", DOK_EXT_ZAPAS)) if dokument is not None else ()


def _w_folderze_programu(path):
    """Folder programu (paths.ROOT, czyli wierzch razem z WORK) i wszystko w nim: tam leżą szablony i pliki programu, nie materiały użytkownika."""
    r = os.path.normcase(os.path.abspath(paths.ROOT))
    p = os.path.normcase(os.path.abspath(path))
    return p == r or p.startswith(r + os.sep)


def _ma_karty(folder):
    return bool(_Glob.glob(os.path.join(glob.escape(folder), "Karta wprowadzenia*.xls*")))


_POWOD_DOPR = {
    "szablon_dk": "To szablon z podpowiedziami w nawiasach - sprawdzam go i przygotowuję polecenie; treść wpisz sam albo zleć AI.",
    "wynik_programu": "To prezentacja zrobiona już przez ten program (nowy styl Dobra Kaloria) - nie przerabiam slajdów, "
                      "sprawdzam je i przygotowuję polecenie do dopracowania.",
    "styl_dk": "Ta prezentacja jest już w stylu Dobra Kaloria - nie przerabiam slajdów, sprawdzam je i przygotowuję polecenie "
               "do dopracowania.",
}
RODZAJ_NAZWA = {"szablon_dk": "szablon Dobra Kaloria", "wynik_programu": "wynik tego programu",
                "styl_dk": "prezentacja już w stylu marki", "obca": "prezentacja w obcym stylu"}


def _rozpoznaj_zapas(plik):
    """Zapas, gdy skill nie ma pptx_convert.rozpoznaj: po nazwie pliku (szablon DK, wynik programu)."""
    n = os.path.basename(plik).lower()
    if n.startswith("dk - szablon"):
        rodzaj = "szablon_dk"
    elif re.search(r" - (nowy styl|stary styl|dopracowana)", n):
        rodzaj = "wynik_programu"
    else:
        return {"rodzaj": "obca", "tryb": "konwersja", "konwertowac": True, "spec": None, "podpowiedzi": 0, "powod": ""}
    return {"rodzaj": rodzaj, "tryb": "dopracowanie", "konwertowac": False, "spec": None, "podpowiedzi": 0,
            "powod": _POWOD_DOPR[rodzaj]}


def _uzupelnij_rozpoznanie(r):
    """Kontrakt pptx_convert.rozpoznaj: {"rodzaj", "tryb": konwersja | dopracowanie, "powod", "konwertowac", "spec", "podpowiedzi"}.
    Starszy skill nie zwraca "tryb" (wynika z "konwertowac"), a powód w dawnym brzmieniu („nie ma czego konwertować”) jest odmową -
    zamieniamy go na zdanie informacyjne, bo plik w stylu marki dopracowujemy, nie odrzucamy."""
    r = dict(r)
    if r.get("tryb") not in ("konwersja", "dopracowanie"):
        r["tryb"] = "konwersja" if r.get("konwertowac") else "dopracowanie"
    r["konwertowac"] = r["tryb"] == "konwersja"
    r.setdefault("spec", None)
    r.setdefault("podpowiedzi", 0)
    if r["tryb"] == "dopracowanie" and (not r.get("powod") or "nie ma czego konwertować" in r["powod"]):
        r["powod"] = _POWOD_DOPR.get(r.get("rodzaj"), _POWOD_DOPR["styl_dk"])
    return r


def _rozpoznaj(plik):
    """Co to za prezentacja: pptx_convert.rozpoznaj(plik) -> {"rodzaj": obca | styl_dk | szablon_dk | wynik_programu,
    "tryb": konwersja | dopracowanie, "powod", "konwertowac", "spec", "podpowiedzi"}. Błąd rozpoznania nie blokuje (wtedy zapas
    po nazwie pliku)."""
    f = getattr(pptx_convert, "rozpoznaj", None)
    if f is not None:
        try:
            r = f(plik)
            if isinstance(r, dict) and ("konwertowac" in r or "tryb" in r):
                return _uzupelnij_rozpoznanie(r)
        except Exception:
            _log_file(traceback.format_exc())
    return _uzupelnij_rozpoznanie(_rozpoznaj_zapas(plik))


def _do_czytania(folder):
    """Pliki w folderze (bez podfolderów), z których da się zrobić prezentację: dokumenty i prezentacje do konwersji.
    Zwraca (lista, gotowe): gotowe = prezentacje już w stylu marki (szablon, wynik programu...; tryb dopracowania) - bierzemy
    je dopiero wtedy, gdy w folderze nie ma nic innego do przeczytania."""
    wyn, pom = [], []
    try:
        nazwy = sorted(os.listdir(folder), key=str.lower)
    except OSError:
        return [], []
    for n in nazwy:
        p = os.path.join(folder, n)
        if n.startswith(("~$", ".")) or not os.path.isfile(p):
            continue
        e = os.path.splitext(n)[1].lower()
        if e in PPTX_EXT:
            (wyn if _rozpoznaj(p).get("tryb") != "dopracowanie" else pom).append(p)
        elif e in dok_ext() or (dokument is None and e in DOK_EXT_ZAPAS):
            wyn.append(p)
    return wyn, pom


def normalize_folder(path):
    """Co upuszczono: zwraca ścieżkę folderu produktu albo pliku (prezentacja .pptx / dokument), albo zgłasza ValueError
    z jednym zdaniem „co zrobić”. Zasady (v14, po złym wyniku z folderu programu i szablonu):
    - folder programu i jego podfoldery nigdy nie są materiałem (wyjątek: PLIK prezentacji z folderu programu, np. szablon -
      to tryb dopracowania);
    - plik z folderu produktu (są w nim „Karta wprowadzenia…”) = folder produktu (jak dotąd);
    - folder bez kart: gdy leży w nim DOKŁADNIE jeden plik do przeczytania (dokument albo prezentacja do konwersji) -
      bierzemy ten plik; gdy są tylko prezentacje już w stylu marki, a jest jedna - też ją; inaczej komunikat;
    - plik innego typu niż prezentacja i dokument: komunikat z listą obsługiwanych."""
    path = (path or "").strip().strip('"')
    if not path:
        raise ValueError("Nie wskazano pliku ani folderu.")
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise ValueError("Nie znalazłem: %s" % path)
    if _w_folderze_programu(path) and not (os.path.isfile(path) and os.path.splitext(path)[1].lower() in PPTX_EXT):
        raise ValueError(KOMUNIKAT_PROGRAM)
    if os.path.isfile(path):
        e = os.path.splitext(path)[1].lower()
        if e in PPTX_EXT:  # gotowa prezentacja: tryb konwersji, ścieżką jest plik
            return path
        if e == ".ppt":
            raise ValueError("To stary format .ppt. Otwórz plik w PowerPoint i zapisz jako .pptx, potem upuść go tutaj.")
        if _ma_karty(os.path.dirname(path)):  # plik z folderu produktu = folder produktu
            return os.path.dirname(path)
        if e in DOK_EXT_ZAPAS or e in dok_ext():
            if dokument is None:
                raise ValueError(KOMUNIKAT_BEZ_DOKUMENTOW)
            return path
        raise ValueError(KOMUNIKAT_TYP)
    if os.path.basename(path).lower() == "_robocze":
        path = os.path.dirname(path)
        if _w_folderze_programu(path):
            raise ValueError(KOMUNIKAT_PROGRAM)
    if _ma_karty(path):
        return path
    if folder_prez.czy_folder_prezentacji(path):   # folder z Źródłami / scenariuszem (1.3): program otwiera go w całości
        return path
    wyn, pom = _do_czytania(path)
    if len(wyn) == 1:
        return wyn[0]
    if not wyn and len(pom) == 1:
        return pom[0]
    if not wyn and not pom:
        raise ValueError("W tym folderze nie ma kart wprowadzenia (plików 'Karta wprowadzenia_....xlsx') ani prezentacji "
                         "czy dokumentu do przeczytania. Upuść folder produktu albo plik z prezentacją lub dokumentem.")
    raise ValueError("W tym folderze jest kilka plików do przeczytania (%d). Upuść ten, z którego mam zrobić prezentację, "
                     "albo folder produktu z kartami wprowadzenia." % (len(wyn) or len(pom)))


def tryb_wejscia(sciezka):
    """'pptx' | 'dokument' | 'folder' | 'scenariusz' | 'pakiet' dla ścieżki zwróconej przez normalize_folder.
    scenariusz = folder prezentacji (1.3) z gotowym scenariuszem, pakiet = folder prezentacji ze Źródłami, bez scenariusza."""
    if os.path.isfile(sciezka):
        return "pptx" if sciezka.lower().endswith(PPTX_EXT) else "dokument"
    if folder_prez.czy_folder_prezentacji(sciezka) and not _ma_karty(sciezka):
        return "scenariusz" if folder_prez.najnowszy_scenariusz(sciezka)[0] else "pakiet"
    return "folder"


def _czy_dopracowanie(sciezka, opts=None):
    """Plik .pptx już w stylu marki (szablon DK, wynik programu, prezentacja z szablonu) = tryb dopracowania; wyjątek: opts["mimo_to"]
    (CLI --mimo-to) każe konwertować go jak obcą."""
    return bool(os.path.isfile(sciezka) and sciezka.lower().endswith(PPTX_EXT) and not (opts or {}).get("mimo_to")
                and _rozpoznaj(sciezka).get("tryb") == "dopracowanie")


# --- 1. analiza folderu -------------------------------------------------------------------------------------------
def analyze(path, mimo_to=False):
    """Analiza tego, co upuszczono: folder produktu, prezentacja .pptx do konwersji, prezentacja już w stylu DK (tryb
    dopracowania: tylko przegląd) albo dokument. mimo_to: konwertuj mimo to prezentację rozpoznaną jako gotową w stylu DK
    (tylko CLI --mimo-to; okno tego nie oferuje)."""
    folder = normalize_folder(path)
    t = tryb_wejscia(folder)
    if t == "pptx":
        try:
            rozp = _rozpoznaj(folder)
            if rozp["tryb"] == "dopracowanie" and not mimo_to:
                return analyze_dopracowanie(folder, rozp)
            return analyze_pptx(folder, mimo_to=mimo_to)
        except ValueError:
            raise
        except PermissionError:
            raise ValueError("Plik jest otwarty albo zablokowany przez inny program. Zamknij go (np. w PowerPoint) i upuść jeszcze raz.")
        except Exception:
            _log_file(traceback.format_exc())
            raise ValueError("Nie mogę otworzyć tej prezentacji (plik jest uszkodzony albo chroniony hasłem). Zapisz ją jeszcze raz "
                             "w PowerPoint jako .pptx i upuść ponownie.")
    if t == "dokument":
        return analyze_dokument(folder)
    if t in ("scenariusz", "pakiet"):
        return analyze_folder_prez(folder)
    cards = _Glob.glob(os.path.join(glob.escape(folder), "Karta wprowadzenia*.xls*"))
    if not cards:
        raise ValueError("W tym folderze nie ma kart wprowadzenia (plików 'Karta wprowadzenia_....xlsx') - "
                         "to nie wygląda na folder produktu. Upuść folder produktu albo plik z prezentacją lub dokumentem.")
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


# --- tryb pptx: konwersja gotowej prezentacji -----------------------------------------------------------------
_pcache = {}  # plik -> (mtime, model)


_ROB = None  # wymuszony katalog roboczy konwersji (CLI --robocze): źródłowy folder zostaje nietknięty


def set_robocze(path):
    global _ROB
    _ROB = os.path.abspath(path) if path else None


def _pptx_rob(plik):
    """Katalog roboczy konwersji: <folder pliku>/_robocze/<nazwa>; gdy folder jest tylko do odczytu - katalog użytkownika.
    set_robocze(...) (CLI --robocze) wymusza własny katalog."""
    if _ROB:
        os.makedirs(_ROB, exist_ok=True)
        return _ROB
    stem = os.path.splitext(os.path.basename(plik))[0]
    kat = os.path.dirname(plik)
    if os.path.basename(kat) == folder_prez.ZRODLA:   # plik ze Źródeł: _robocze leży w folderze prezentacji, nie w Źródłach
        kat = os.path.dirname(kat)
    rob = os.path.join(kat, "_robocze", stem)
    if os.path.basename(kat).lower() == "_robocze":   # plik roboczy (np. połączone źródła): katalog obok niego, nie _robocze\_robocze
        rob = os.path.join(kat, stem)
    try:
        if _w_folderze_programu(plik):   # szablon z folderu programu: program nic tam nie zapisuje (może być tylko do odczytu)
            raise OSError("folder programu")
        os.makedirs(rob, exist_ok=True)
        return rob
    except OSError:
        alt = os.path.join(paths.USER_DIR, "konwersje", stem)
        os.makedirs(alt, exist_ok=True)
        return alt


def _pptx_model(plik):
    """Model treści (extract) z cache: analiza i budowa czytają plik raz."""
    mt = os.path.getmtime(plik)
    c = _pcache.get(plik)
    if c and c[0] == mt:
        return c[1]
    rob = _pptx_rob(plik)
    os.makedirs(rob, exist_ok=True)
    model = pptx_convert.extract(plik, rob)
    _pcache[plik] = (mt, model)
    return model


def analyze_pptx(plik, mimo_to=False):
    rozp = _rozpoznaj(plik)
    model = _pptx_model(plik)
    st = pptx_convert.stats(model)
    chapters = pptx_convert.detect_chapters(model)
    # próbny układ (bez biblioteki wizualizacji - ma być szybko): ile slajdów wyniku przypada na rozdział
    spec = pptx_convert.compose(model, {"wizualizacje": False})
    n_out = {c["id"]: sum(len(spec["mapa"].get(str(n), [])) for n in c["slajdy"]) for c in chapters}
    uwagi = [{"typ": "info", "tekst": t} for t in model["uwagi"] if not t.startswith("Animacje")]
    uwagi.append({"typ": "info", "tekst": "Cały tekst zostanie przeniesiony. Na końcu sprawdzę każdy akapit i układ "
                                          "slajdów i pokażę wynik."})
    ost = rozp.get("powod") or ""
    ost = ost[ost.find("Uwaga:"):] if "Uwaga:" in ost else ""   # wątpliwość rozpoznania (obca prezentacja, ale coś niepokoi)
    if ost and rozp["tryb"] == "konwersja":
        uwagi.insert(0, {"typ": "ostrzezenie", "tekst": ost})
    if rozp["tryb"] == "dopracowanie":                           # --mimo-to
        uwagi.insert(0, {"typ": "ostrzezenie", "tekst": "Konwertuję mimo to (rozpoznano: %s)." % RODZAJ_NAZWA.get(rozp.get("rodzaj"), rozp.get("rodzaj"))})
    sekcje = [{"id": c["id"], "nazwa": c["nazwa"], "dostepna": True, "domyslnie": True, "powod": "", "grupa": "rozdzialy",
               "rodzaj": "pptx", "slajdy": n_out[c["id"]],
               "opis": ("slajd %s z oryginału" if len(c["slajdy"]) == 1 else "slajdy %s z oryginału") % pptx_convert._range(c["slajdy"])}
              for c in chapters] + catalog_pptx()
    try:
        lib = wizki.biblioteka(plik, paths.ROOT)
    except OSError:
        lib = None
    n = len(spec["slides"])
    # pomiar 13.10 (strategia, 43 slajdy): budowa ok. 25 s, zrzuty + kontrola ok. 25 s (razem ok. 60 s), każda runda "oka" ze zmianą
    # układu ok. 25 s; zakładamy jedną rundę
    est = (CZAS_PPTX[0] + CZAS_PPTX[1] * n) if powerpoint_available() else 5 + 0.3 * n
    return {"ok": True, "tryb": "pptx", "folder": os.path.dirname(plik), "plik": plik, "nazwa_pliku": os.path.basename(plik),
            "produkt": pptx_convert.produkt(model), "slajdy": st["slajdy"], "slajdy_wynik": len(spec["slides"]),
            "akapity": st["akapity"], "grafiki": st["grafiki"], "tabele": st["tabele"], "wykresy": st["wykresy"],
            "rozdzialy": [c["nazwa"] for c in chapters], "sekcje": sekcje,
            "grupy": [{"id": "rozdzialy", "nazwa": "Rozdziały", "opis": ""},
                      {"id": "dodatki", "nazwa": "Dołóż puste slajdy", "opis": "z szablonu, z podpowiedziami w [nawiasach]"}],
            "cele": [{"id": k, "nazwa": v["nazwa"], "opis": polecenia.POLECENIA.get(k, v)["opis"]}
                     for k, v in pptx_convert.CELE.items()],
            "cel_domyslny": "wiernie", "wizualizacje": {"dostepne": bool(lib), "sciezka": lib or ""},
            "presety": {"0": [], "1": [], "2": []}, "smaki": [], "karty": 0, "uwagi": uwagi,
            "domyslne": {"styl": "nowy", "dlugosc": 1, "tekst": 1}, "szacowany_czas_s": int(est),
            "powerpoint": powerpoint_available()}


# --- tryb dopracowanie: prezentacja JUŻ w stylu marki (szablon DK, wynik programu, prezentacja z szablonu) -------------------
def _przeglad(plik, rob):
    """pptx_convert.przeglad(plik, rob): przegląd gotowego pliku BEZ budowania - {"slajdy", "teksty" [(nr, [akapity])],
    "bledy_tekstu", "podpowiedzi" [(nr, tekst)], "uwagi"}."""
    f = getattr(pptx_convert, "przeglad", None)
    if f is None:
        raise ValueError(KOMUNIKAT_BEZ_PRZEGLADU)
    return f(plik, rob)


def _nazwa_prezentacji(plik):
    stem = os.path.splitext(os.path.basename(plik))[0]
    return re.sub(r" - (nowy styl|stary styl|dopracowana).*$", "", stem) or stem


def analyze_dopracowanie(plik, rozp):
    """Przegląd w oknie dla pliku w stylu marki: ile slajdów, ile podpowiedzi w [nawiasach], ile możliwych błędów tekstu i zdanie
    „co program zrobi” (rozp["powod"], informacja, nie odmowa). Bez celu, rozdziałów i suwaków: dopracowanie niczego nie buduje."""
    pr = _przeglad(plik, _pptx_rob(plik))
    n = int(pr["slajdy"])
    # liczba pól w zdaniu z rozpoznania liczy też opisy slajdów szablonu; w oknie stoi jedna liczba, z przeglądu (wiersz „Podpowiedzi…”)
    powod = re.sub(r" [(][0-9]+ pól do wypełnienia[)]", "", rozp.get("powod") or "")
    est = (CZAS_DOPR[0] + CZAS_DOPR[1] * n) if powerpoint_available() else 4   # zrzuty i kontrola kopii; bez budowy i bez „oka” z przebudową
    return {"ok": True, "tryb": "dopracowanie", "rodzaj": rozp.get("rodzaj"), "folder": os.path.dirname(plik), "plik": plik,
            "nazwa_pliku": os.path.basename(plik), "produkt": _nazwa_prezentacji(plik), "slajdy": n,
            "podpowiedzi": len(pr["podpowiedzi"]), "bledy_tekstu_liczba": len(pr["bledy_tekstu"]), "spec": rozp.get("spec"),
            "powod": powod, "uwagi": [{"typ": "info", "tekst": powod}],
            "sekcje": [], "grupy": [], "cele": [], "smaki": [], "karty": 0, "presety": {"0": [], "1": [], "2": []},
            "domyslne": {"styl": "nowy", "dlugosc": 1, "tekst": 1}, "szacowany_czas_s": int(est),
            "powerpoint": powerpoint_available()}


# --- tryb dokument: docx, doc, rtf, odt, pdf, txt, md -> prezentacja (moduł skilla `dokument`) ----------------------------
_dcache = {}  # plik -> (mtime, model)
DOK_MIN_ROZDZIALOW = 3   # od tylu rozdziałów program dokłada agendę (reguła w dokument.zloz); domyślna liczba przekładek >= tyle


def _dok_model(plik, rob=None):
    """Model treści dokumentu (dokument.wczytaj) z cache: analiza i budowa czytają plik raz. Błędy po polsku (ValueError).
    rob = własny katalog roboczy (obrazy z dokumentu); domyślnie _pptx_rob(plik)."""
    if dokument is None:
        raise ValueError(KOMUNIKAT_BEZ_DOKUMENTOW)
    mt = os.path.getmtime(plik)
    c = _dcache.get(plik)
    if c and c[0] == mt:
        return c[1]
    try:
        with open(plik, "rb"):
            pass
    except PermissionError:
        raise ValueError("Plik jest otwarty albo zablokowany przez inny program. Zamknij go (np. w Wordzie) i upuść jeszcze raz.")
    except OSError as e:
        raise ValueError("Nie mogę otworzyć pliku (%s). Sprawdź, czy istnieje i czy masz do niego dostęp." % e.strerror)
    rob = rob or _pptx_rob(plik)
    try:
        m = dokument.wczytaj(plik, rob)
    except ValueError:
        raise   # komunikaty modułu są po polsku i mówią, co zrobić (skan, za długi, brak Worda…)
    except Exception as e:
        _log_file(traceback.format_exc())
        raise ValueError("Nie udało się przeczytać dokumentu (%s). Zapisz go jeszcze raz jako .docx albo .pdf i upuść ponownie."
                         % type(e).__name__)
    st = dokument.statystyka(m)
    if not (st.get("slowa") or 0):
        raise ValueError("Ten dokument jest pusty - nie ma w nim tekstu do zamiany na slajdy. Dopisz treść i upuść go jeszcze raz.")
    _dcache[plik] = (mt, m)
    return m


def _suwaki_dokumentu(st):
    """Zakresy i wartości domyślne dwóch suwaków trybu dokument, policzone Z DOKUMENTU (statystyka). Zawsze min <= domyślnie <= max."""
    mn = max(1, int(st.get("slajdy_min") or 1))
    mx = max(mn, int(st.get("slajdy_max") or mn))
    dom = min(mx, max(mn, int(st.get("slajdy_domyslnie") or mn)))
    rmax = max(0, int(st.get("rozdzialy_max") or 0))
    if st.get("rozdzialy_domyslnie") is not None:
        rdom = int(st["rozdzialy_domyslnie"])
    elif rmax >= DOK_MIN_ROZDZIALOW:
        rdom = max(DOK_MIN_ROZDZIALOW, int(round(dom / 6.0)))   # ok. jedna przekładka na 6 slajdów, nie mniej niż agenda
    else:
        rdom = rmax
    return {"slajdy": {"min": mn, "max": mx, "domyslnie": dom},
            "rozdzialy": {"max": rmax, "domyslnie": max(0, min(rmax, rdom))}}


def _czas_dokumentu():
    """Szacunek czasu: stały + na slajd SUWAKA (okno liczy go na żywo przy przesuwaniu). Silnik dzieli slajdy, na których treść się nie mieści,
    więc w pliku jest do 1,7 razy tyle slajdów, ile na suwaku (pomiar 13.10: 3 -> 5, 5 -> 7, 9 -> 15, 11 -> 17, 79 -> 81). Pomiary czasu (komputer
    obciążony): suwak 3 / 5 / 9 / 11 / 79 = 24 / 31 / 24 / 48 / 288 s; duży dokument częściej wymaga przebudowy układu po zrzutach, stąd człon kwadratowy
    (stały + na_slajd * v + kw * v^2)."""
    pp = powerpoint_available()
    return {"stale": 18 if pp else 4, "na_slajd": 1.5 if pp else 0.5, "kw": 0.02 if pp else 0.0}


def analyze_dokument(plik):
    """Analiza dokumentu do okna: nazwa, tytuł, statystyka, zakresy dwóch suwaków (z dokumentu), ostrzeżenia."""
    m = _dok_model(plik)
    st = dokument.statystyka(m)
    sw = _suwaki_dokumentu(st)
    czas = _czas_dokumentu()
    nag = {str(k): int(v) for k, v in (st.get("naglowki") or {}).items()}
    uwagi = [{"typ": "ostrzezenie", "tekst": t} for t in (m.get("ostrzezenia") or [])]
    uwagi.append({"typ": "info", "tekst": "Na slajdach stają liczby, tabele i hasła z dokumentu; pełny tekst trafia do notatek "
                                          "prelegenta - niczego nie dopiszę i nie pominę. Na końcu sprawdzę każdy akapit i pokażę wynik."})
    v = sw["slajdy"]["domyslnie"]
    est = czas["stale"] + czas["na_slajd"] * v + czas["kw"] * v * v
    return {"ok": True, "tryb": "dokument", "folder": os.path.dirname(plik), "plik": plik, "nazwa_pliku": os.path.basename(plik),
            "produkt": m.get("tytul") or os.path.splitext(os.path.basename(plik))[0], "tytul": m.get("tytul") or "",
            "slowa": int(st.get("slowa") or 0), "akapity": int(st.get("akapity") or 0), "naglowki": nag,
            "tabele": int(st.get("tabele") or 0), "obrazy": int(st.get("obrazy") or 0),
            "suwaki": sw, "czas": czas, "uwagi": uwagi, "na_slajdach": st.get("na_slajdach") or {},
            "sekcje": [], "grupy": [], "cele": [], "presety": {"0": [], "1": [], "2": []}, "smaki": [], "karty": 0,
            "domyslne": {"styl": "nowy", "dlugosc": 1, "tekst": 1}, "szacowany_czas_s": int(est),
            "powerpoint": powerpoint_available()}


_TYPY_BLOKOW = {"h1": "nagłówek 1", "h2": "nagłówek 2", "h3": "nagłówek 3", "p": "akapit", "li": "punkt", "tabela": "tabela",
                "obraz": "obraz", "cytat": "cytat"}


def _dok_dump(model, limit=18000):
    """Tekst dokumentu blok po bloku (do polecenia dla czatu): [h1] …, [p] …, [li] …, [tabela] …, [obraz]."""
    L = []
    for b in model.get("bloki", []):
        typ = b.get("typ", "p")
        if typ == "tabela":
            t = " || ".join(" | ".join(str(c) for c in r) for r in b.get("wiersze") or [])
        elif typ == "obraz":
            t = b.get("t") or ""
        else:
            t = " ".join(str(b.get("t") or "").split())
        L.append("[%s]%s" % (typ, (" " + t) if t else ""))
    t = "\n".join(L)
    return t if len(t) <= limit else t[:limit] + "\n(dalsza część dokumentu pominięta - za długa)"


def _source_dump(model, limit=24000):
    """Tekst oryginału slajd po slajdzie (do polecenia dla czatu)."""
    L = []
    for s in model["slajdy"]:
        hb, bl = pptx_convert._body(s, model["h_cm"])
        parts = ([pptx_convert._text_of(hb)] if hb else []) + [pptx_convert._text_of(b) for b in bl]
        parts += [" | ".join(r) for tb in s["tables"] for r in tb["rows"]]
        L.append("Slajd %d: %s" % (s["n"], " || ".join(p for p in parts if p) or "(bez tekstu)"))
        if s["notes"]:
            L.append("  notatki: " + " ".join(s["notes"].split()))
    t = "\n".join(L)
    return t if len(t) <= limit else t[:limit] + "\n(dalsza część oryginału pominięta - za długa)"


# --- polecenia dla AI po konwersji gotowej prezentacji --------------------------------------------------------------
# Dwa polecenia z tych samych punktów (polecenia.py, metoda: references\dopracowanie.md): dla AGENTA Z PLIKAMI
# (ai_prompt_agent_pptx) i dla CZATU BEZ PLIKÓW (ai_prompt_pptx - dostaje tylko wklejony tekst, więc bez ścieżek,
# renderu i kontroli; widzi role tekstu, a wygląd - tylko z plansz, jeśli użytkownik je dołączy).
# Limity bloków w poleceniu dla czatu (znaki). Strategia, 43 slajdy: oryginał 9,1 tys., wynik z rolami 13 tys., reszta
# polecenia (punkty, tabela kształtów, uwagi) 8,4 tys. = 30,5 tys. Do 60 slajdów (x 1,4) mieści się z zapasem, nic nie jest
# ucinane; gdy całość przekracza LIMIT_POLECENIE, bloki dostają mniejsze limity (kolejne pary), a ucięcie jest nazwane.
LIMIT_ZRODLO = 18000
LIMIT_WYNIK = 26000
LIMITY_ZAPASOWE = ((14000, 20000), (10000, 14000), (6000, 8000))
LIMIT_POLECENIE = 60000
LIMIT_UWAG = 40        # linii "UWAGI PROGRAMU" w poleceniu (nadmiar: "…i N kolejnych")
LIMIT_BLEDOW = 60      # linii błędów tekstu w poleceniu
FORMAT_ODPOWIEDZI = (
    "FORMAT ODPOWIEDZI - trzy części, nic poza nimi (jeśli poprawiasz plik: to jest Twój raport):\n"
    "   A. BŁĘDY TEKSTU - tabela: slajd | było | jest | powód. Tylko ewidentne (punkt o błędach). Na końcu jedno zdanie:\n"
    "      „W PowerPoincie: Ctrl+H, wpisz „było”, zamień na „jest”.”\n"
    "   B. SLAJDY DO POPRAWY - tylko slajdy, które łamią zasady z punktów wyżej albo są z listy „Sprawdź najpierw”: numer | kształt treści | wzór (nazwa\n"
    "      z tabeli „kształt treści -> wzór”; gdy żaden nie pasuje: „brak”) | role tekstu, każda w osobnej linii: LICZBA: … /\n"
    "      HASŁO: … / DOPISEK: … / WNIOSEK: … / ETYKIETA: … / PUNKT: … Po złożeniu pól w tej kolejności ma wyjść dokładnie\n"
    "      tekst slajdu z oryginału (wyjątek: LICZBA powtarza liczbę z HASŁA); jeśli się nie zgadza, slajd idzie do części C.\n"
    "      Slajdów dobrych nie wypisuj.\n"
    "   C. DO DECYZJI: wątpliwe słowa, nazwy, liczby, brakujące informacje, slajdy z za dużą ilością treści.")
POKRYCIE_CZAT = (
    "Sprawdź pokrycie treści: porównaj ORYGINAŁ i WYNIK poniżej; każdą informację, której w wyniku brakuje, wpisz do "
    "części C. Jeśli widzisz „(dalsza część … pominięta)”, nie zgłaszaj braków dla tych slajdów - napisz „nie sprawdzone: "
    "slajdy N-M”.")
BEZ_PLIKOW = (
    "Jeśli nie masz pliku prezentacji ani zrzutów: nie widzisz wyglądu slajdów - oceniasz treść i role tekstu (prefiksy w "
    "nawiasach kwadratowych w bloku WYNIK). Pisma, kolorów i ikon nie oceniasz.")
BEZ_SKRYPTOW_AGENT = ("Nie masz dostępu do plików i skryptów (np. wtyczka Claude w PowerPoincie)? Pomiń KROK 0 i przejdź do "
                      "punktu „NIE MASZ DOSTĘPU…”.")
DLA_AGENTA = ("Jeśli pracujesz jako agent z dostępem do plików (Claude Cowork / Code, Codex, Gemini CLI), użyj zamiast "
              "tego polecenia „dla agenta” z programu.")
ZALACZNIKI = (
    "ZAŁĄCZNIKI: dołącz do tej wiadomości obrazy z folderu \"%s\" (%s). Jeśli widzisz obrazy slajdów, oceń także "
    "wygląd: czy każda karta ma hasło, czy liczby są duże, czy wniosek stoi w pasie, czy pismo jest czytelne, czy coś łamie "
    "się słowo po słowie, czy nie ma pustych kart i pustego dołu slajdu, czy ikona pasuje do treści - uwagi wpisz w części B "
    "przy numerze slajdu. Jeśli obrazów nie widzisz, oceniasz tylko treść i role tekstu.")
NAGLOWEK_BLEDOW = "Możliwe błędy w tekście oryginału"
NAGLOWEK_BLEDOW_DOK = "Możliwe błędy w tekście dokumentu"
NAGLOWEK_BLEDOW_DOPR = "Możliwe błędy w tekście prezentacji"


def _lint_opis(u):
    try:
        import lint_tekst
        return lint_tekst.opis(u)
    except Exception:
        return "Slajd %s: „%s” - możliwy błąd (%s)" % (u.get("slajd"), u.get("jest"), u.get("rodzaj"))


def _linie_bledow(bledy):
    """Linie błędów tekstu oryginału z spec["bledy_tekstu"] (lint_tekst): pewność wysoka najpierw, średnia z dopiskiem
    „do sprawdzenia”."""
    wys = [u for u in bledy or [] if u.get("pewnosc") == "wysoka"]
    sre = [u for u in bledy or [] if u.get("pewnosc") != "wysoka"]
    out = [_lint_opis(u) for u in wys] + [_lint_opis(u) + " (średnia pewność - do sprawdzenia)" for u in sre]
    return out


def _bez_linii_bledow(uwagi, bledy):
    """Uwagi bez linii z lintu (mają własny blok): nagłówek, opisy pojedynczych błędów, „…i N innych podejrzeń”."""
    opisy = {_lint_opis(u) for u in bledy or []}
    return [u for u in uwagi if u not in opisy
            and not u.startswith((NAGLOWEK_BLEDOW, NAGLOWEK_BLEDOW_DOK, NAGLOWEK_BLEDOW_DOPR, "Możliwe błędy w tekście:"))
            and not re.match(r"…i \d+ innych podejrze", u)]


def _uwagi_dla_ai(uwagi, bledy, limit=LIMIT_UWAG, gdzie="w raport.json"):
    """Uwagi do polecenia: bez linii błędów tekstu; najpierw „Sprawdź najpierw…” i „Do sprawdzenia…”, potem reszta."""
    rest = _bez_linii_bledow(uwagi, bledy)
    pierwsze = [u for u in rest if u.startswith(("Sprawdź najpierw", "Do sprawdzenia"))]
    out = pierwsze + [u for u in rest if u not in pierwsze]
    if len(out) > limit:
        out = out[:limit] + ["…i %d kolejnych %s" % (len(out) - limit, gdzie)]
    return out


def _blok_bledow(bledy, limit=LIMIT_BLEDOW):
    lin = _linie_bledow(bledy)
    if not lin:
        return [" - program nie znalazł - przeczytaj slajdy sam"]
    if len(lin) > limit:
        lin = lin[:limit] + ["…i %d kolejnych w raport.json (bledy_tekstu)" % (len(lin) - limit)]
    return [" - " + x for x in lin]


TOP_UWAG = 5   # tyle wierszy uwag widać od razu na ekranie końcowym; reszta pod „Pokaż wszystkie”


def _mn(n, jeden, kilka, wiele):
    """Polska liczba: 1 jeden, 2-4 kilka, reszta wiele."""
    return jeden if n == 1 else (kilka if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else wiele)


def _uwagi_top(uwagi, bledy=None, oko=None, wiz=None, ukryte=0, limit=TOP_UWAG):
    """Widoczne wiersze uwag na ekranie końcowym: najwyżej `limit` wpisów {"typ": "warn" | "info", "tekst"} w kolejności ważności.
    1. czego brakuje i co nie przeszło kontroli wierności (Brakuje…, Do sprawdzenia…); 2. podpowiedzi w [nawiasach]; 3. błędy tekstu:
    JEDNA linia z liczbą i dwoma przykładami; 4. „Sprawdź najpierw: slajd N…” z oka (do dwóch wierszy); 5. wstawione paczki do
    sprawdzenia; 6. slajdy ukryte. Pełna lista (`uwagi`) zostaje w poleceniach dla AI, w raport.json i w uwagi.txt."""
    uwagi = list(uwagi or [])
    wiersze = []

    def zwin(przedrostek):
        a = [u for u in uwagi if u.startswith(przedrostek)]
        if a:
            wiersze.append({"typ": "warn", "tekst": a[0] if len(a) == 1 else "%s - i %d kolejnych" % (a[0], len(a) - 1)})
    zwin("Brakuje")
    zwin("Do sprawdzenia")
    pod = [u for u in uwagi if re.match(r"Slajdy? [0-9].* (ma|mają) podpowiedzi w nawiasach", u) or u.startswith("Podpowiedzi w nawiasach kwadratowych")]
    if pod:
        wiersze.append({"typ": "warn", "tekst": pod[0]})
    if bledy:
        ks = sorted(bledy, key=lambda u: 0 if u.get("pewnosc") == "wysoka" else 1)[:2]
        przyklady = "; ".join("slajd %s „%s”%s" % (u.get("slajd"), u.get("jest"), (" -> „%s”" % u["propozycja"]) if u.get("propozycja") else "")
                              for u in ks)
        wiersze.append({"typ": "warn", "tekst": "Możliwe błędy w tekście: %d (np. %s) - program ich nie poprawia, lista pod „Pokaż wszystkie”"
                        % (len(bledy), przyklady)})
    linie = [u for u in uwagi if u.startswith("Sprawdź najpierw: slajd ")]
    reszta = sum(int(m.group(1)) for m in (re.match(r"…i (\d+) kolejnych usterek wyglądu", u) for u in uwagi) if m)
    if linie:
        wiersze.append({"typ": "warn", "tekst": linie[0]})
        if len(linie) + reszta > 1:
            wiersze.append({"typ": "warn", "tekst": "…i %d kolejnych usterek wyglądu - lista pod „Pokaż wszystkie”" % (len(linie) + reszta - 1)})
    if wiz:
        nr = sorted({int(x) for x in wiz})
        lista = ", ".join(str(n) for n in nr[:5]) + (" i %d innych" % (len(nr) - 5) if len(nr) > 5 else "")
        wiersze.append({"typ": "info", "tekst": "Wstawiłem paczki z biblioteki produktów na %s nr %s: sprawdź dobór." % (
            "slajdzie" if len(nr) == 1 else "slajdach", lista)})
    if ukryte:
        wiersze.append({"typ": "info", "tekst": "%d %s. Przed wysłaniem pliku poza firmę usuń %s albo zapisz PDF." % (
            ukryte, _mn(ukryte, "slajd jest ukryty", "slajdy są ukryte", "slajdów jest ukrytych"), "go" if ukryte == 1 else "je")})
    return wiersze[:limit]


def _zapisz_uwagi(rob, uwagi, say=None):
    """Pełna lista uwag programu w pliku <robocze>\\uwagi.txt (po jednej w wierszu): okno pokazuje tylko najważniejsze."""
    try:
        with open(os.path.join(rob, "uwagi.txt"), "w", encoding="utf8") as fh:
            fh.write("\n".join(" ".join(str(u).split()) for u in uwagi) + "\n")
    except OSError as e:
        if say:
            say("Nie zapisałem uwagi.txt (%s)." % e.strerror)


def _uwaga_okna(u, max_znakow=180):
    """Krótka wersja uwagi do listy w oknie (pełne brzmienie zostaje w poleceniach dla AI i w raport.json): None = pomiń."""
    if u.startswith("Dobór układu z pomiaru") or u.startswith("Animacje, przejścia i tła"):
        return None
    if re.match(r"Slajd \d+: dodałem wizualizacje", u):   # okno ma o tym osobny wiersz („Wstawiłem paczki z biblioteki…”)
        return None
    m = re.match(r"Ułożyłem w klocki szablonu marki .*? slajdy: ([\d, ]+)\.", u)
    if m:
        return "Ułożyłem w układy z szablonu marki %d slajdów (hasła, liczby, wnioski)." % len(re.findall(r"\d+", m.group(1)))
    m = re.match(r"Oryginał jest pisany wersalikami: ustawiłem zwykłą wielkość liter w (\d+) wierszach", u)
    if m:
        return ("Oryginał był pisany wersalikami: w %s wierszach ustawiłem zwykłą wielkość liter - sprawdź nazwy własne i skróty "
                "(lista: wielkosc-liter.txt)." % m.group(1))
    return u if len(u) <= max_znakow else u[:max_znakow].rsplit(" ", 1)[0] + " …"


OKNO_OKO = 3   # usterek wyglądu z „oka” pokazywanych osobno w oknie (reszta: jedna linia „…i N kolejnych”)


def _oko_w_oknie(rest):
    """Linie „Sprawdź najpierw: slajd N - …” z oka: w oknie najwyżej OKNO_OKO osobno + jedna linia „…i N kolejnych usterek
    wyglądu w poleceniu dla AI” (pełna lista: polecenia dla AI i raport.json)."""
    oko = [u for u in rest if u.startswith("Sprawdź najpierw: slajd ")]
    dod = [u for u in rest if re.match(r"…i \d+ kolejnych usterek wyglądu", u)]
    ile_dod = sum(int(re.match(r"…i (\d+)", u).group(1)) for u in dod)
    reszta = max(0, len(oko) - OKNO_OKO) + ile_dod
    if not reszta:
        return rest
    out, wstawiono = [], False
    for u in rest:
        if u in oko or u in dod:
            if not wstawiono:
                out += oko[:OKNO_OKO] + ["…i %d kolejnych usterek wyglądu w poleceniu dla AI" % reszta]
                wstawiono = True
            continue
        out.append(u)
    return out


def uwagi_okno(uwagi, bledy, ile=5, rodzaj="pptx"):
    """Uwagi do okna „Gotowe”: na początku blok błędów tekstu oryginału - nagłówek i najwyżej `ile` linii (pewność wysoka
    najpierw), nadmiar jako „…i N kolejnych w poleceniu dla AI”; potem reszta uwag bez linii z lintu, skrócona (_uwaga_okna)."""
    rest = _oko_w_oknie([x for x in (_uwaga_okna(u) for u in _bez_linii_bledow(uwagi, bledy)) if x])
    glowa = [u for u in rest if u.startswith(("Treść:", "Układ:"))]   # wyniki kontroli stoją zawsze na samej górze
    rest = glowa + [u for u in rest if u not in glowa]
    lin = _linie_bledow(bledy)
    if not lin:
        return rest, []
    if rodzaj == "dokument":
        naglowek = "%s: %d (program ich nie poprawia - popraw w dokumencie i zrób prezentację jeszcze raz albo zleć AI)" % (
            NAGLOWEK_BLEDOW_DOK, len(lin))
    elif rodzaj == "dopracowanie":
        naglowek = "%s: %d (program ich nie poprawia - popraw w pliku albo zleć AI)" % (NAGLOWEK_BLEDOW_DOPR, len(lin))
    else:
        naglowek = "%s: %d (program ich nie poprawia - popraw w pliku albo zleć AI)" % (NAGLOWEK_BLEDOW, len(lin))
    blok = [naglowek] + lin[:ile]
    if len(lin) > ile:
        blok.append("…i %d kolejnych w poleceniu dla AI" % (len(lin) - ile))
    return glowa + blok + rest[len(glowa):], blok


def _wynik_linie(spec, max_chars, rodzaj="pptx"):
    """Wynik konwersji slajd po slajdzie. Slajdy `uklad` z rolą tekstu w nawiasie kwadratowym ([hasło], [liczba]…),
    inne typy slajdów bez prefiksu. Powyżej max_chars: „(dalsza część wyniku pominięta - za długa)”."""
    L = []
    for i, s in enumerate(spec.get("slides", []), 1):
        skad = ("NOWY, pusty slajd z szablonu" if s.get("nowy") else
                ("z dokumentu" if rodzaj == "dokument" else "z oryginału %s" % s.get("zrodlo", "?")))
        L.append("Slajd %d (%s%s):" % (i, skad, ", ukryty" if s.get("hidden") else ""))
        role = polecenia.role_slajdu(s)
        if role:
            for r, t in role:
                L.append("  - " + polecenia.format_roli(r, t))
        else:
            seen = []
            for t in _slide_texts(s):
                if t not in seen:
                    seen.append(t)
                    L.append("  - " + t)
            if not seen:
                L.append("  - (sam obraz, bez tekstu)")
        used = sum(len(x) + 1 for x in L)
        if used > max_chars:
            L.append("(dalsza część wyniku pominięta - za długa)")
            break
    return L


def _punkty(cel, dane, pliki, rodzaj="pptx"):
    """Punkty polecenia dla AI. rodzaj "dokument": wpis POLECENIA["dokument"] ze skilla, a gdy go nie ma - zapas z polecenia_dok."""
    if rodzaj == "dokument":
        c = getattr(polecenia, "POLECENIA", {}).get("dokument")
        if c:
            return (c["polecenie_pliki"][:1] + c["polecenie"] + c["polecenie_pliki"][1:]) if pliki else list(c["polecenie"])
        return polecenia_dok.punkty(pliki)
    return polecenia.polecenie_ai(cel, dane, pliki=pliki)


def _plikow(n):
    return "%d %s" % (n, "plik" if n == 1 else ("pliki" if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else "plików"))


def ai_prompt_pptx(nazwa, plik, model, spec, uwagi, cov, qa=None, pptx=None, max_chars=None, cel="wiernie", dane=None,
                   plansze=None, rodzaj="pptx"):
    """Polecenie dla czatu (opis: _ai_prompt_pptx). Całość ma najwyżej LIMIT_POLECENIE znaków: za długą składa od nowa
    z mniejszymi limitami bloków oryginału i wyniku (ucięcie jest nazwane w tekście)."""
    t = ""
    for lz, lw in ((LIMIT_ZRODLO, max_chars or LIMIT_WYNIK),) + LIMITY_ZAPASOWE:
        t = _ai_prompt_pptx(nazwa, plik, model, spec, uwagi, cov, qa, pptx, lw, cel, dane, plansze, lz, rodzaj)
        if len(t) <= LIMIT_POLECENIE:
            break
    return t


def _ai_prompt_pptx(nazwa, plik, model, spec, uwagi, cov, qa, pptx, max_chars, cel, dane, plansze, limit_zrodlo, rodzaj="pptx"):
    """Polecenie dla CZATU BEZ PLIKÓW (Claude.ai / ChatGPT / Gemini w przeglądarce) po konwersji gotowej prezentacji.
    Czat dostaje tylko wklejony tekst: punkty wspólne (polecenia.polecenie_ai(..., pliki=False)), tabelę „kształt treści ->
    wzór”, tekst ORYGINAŁU i WYNIKU (z rolami tekstu), uwagi i błędy tekstu - bez ścieżek, renderu i kontroli, których nie
    wykona. plansze = {"folder", "pliki"}: obrazy slajdów do dołączenia (czat ocenia wtedy także wygląd)."""
    dok = rodzaj == "dokument"
    cel = cel if cel in pptx_convert.CELE else "wiernie"
    max_chars = max_chars or LIMIT_WYNIK
    bledy = (spec or {}).get("bledy_tekstu") or []
    pl = (plansze or {}).get("pliki") or []
    pokrycie = cov.get("tekst", "-").replace("Treść: ", "").rstrip(".")
    if dok:
        d = dane or {}
        L = ["To prezentacja zrobiona z dokumentu \"%s\" w stylu marki Dobra Kaloria. Program ułożył slajdy automatycznie: "
             "te same słowa, w kolejności dokumentu, w hasłach, liczbach i wnioskach z szablonu marki. Liczbę slajdów (%s) "
             "i przekładek rozdziałów (%s) ustawił człowiek suwakiem - nie zmieniaj jej. Kontrola pokrycia treści: %s. "
             "Plik wynikowy: \"%s\". Zasady i źródła stylu są w punktach poniżej - wykonaj je w tej kolejności, nie z "
             "własnego wyczucia." % (os.path.basename(plik), d.get("slajdy", "?"), d.get("rozdzialy", "?"), pokrycie, nazwa), ""]
    else:
        L = ["To konwersja prezentacji \"%s\" na styl marki Dobra Kaloria. Cel: %s. Program ułożył slajdy automatycznie: te same "
             "słowa, w hasłach, liczbach i wnioskach z szablonu marki. Kontrola pokrycia treści: %s. Plik wynikowy: \"%s\". "
             "Zasady i źródła stylu są w punktach poniżej - wykonaj je w tej kolejności, nie z własnego wyczucia." % (
                 os.path.basename(plik), pptx_convert.CELE[cel]["nazwa"].lower(), pokrycie, nazwa), ""]
    if pl:   # plansze zastępują zdanie o braku wyglądu; zdanie o agencie zostaje
        L += [ZALACZNIKI % ((plansze or {}).get("folder", ""), _plikow(len(pl))) + " " + DLA_AGENTA, ""]
    else:
        L += [BEZ_PLIKOW + " " + DLA_AGENTA, ""]
    L += ["Oryginał: %s" % os.path.basename(plik), "Wynik: %s" % (os.path.basename(pptx) if pptx else nazwa), ""]
    pts = _punkty(cel, dane, False, rodzaj)
    if dok:
        pts += [POKRYCIE_CZAT.replace("ORYGINAŁ i WYNIK", "DOKUMENT i WYNIK"), FORMAT_ODPOWIEDZI]
    else:
        pts += [POKRYCIE_CZAT,
                "Sprawdź wielkie litery nazw własnych i skrótów oraz dobór wizualizacji produktów, jeśli program je dodał "
                "(lista jest w UWAGACH PROGRAMU).", FORMAT_ODPOWIEDZI]
    L += ["CO MASZ ZROBIĆ"] + ["%d. %s" % (i, p) for i, p in enumerate(pts, 1)]
    tab = polecenia.tabela_ksztaltow()
    if tab:
        L += ["", "KSZTAŁT TREŚCI -> WZÓR Z SZABLONU", tab]
    if dok:
        L += ["", "DOKUMENT (tekst źródłowy, blok po bloku)", _dok_dump(model, limit=limit_zrodlo), "", "WYNIK (slajdy z dokumentu)"]
    else:
        L += ["", "ORYGINAŁ (tekst slajdów)", _source_dump(model, limit=limit_zrodlo), "", "WYNIK (slajdy po konwersji)"]
    L += _wynik_linie(spec or {}, max_chars, rodzaj)
    ua = _uwagi_dla_ai(uwagi, bledy, gdzie="pominięto (za dużo)")
    if ua:
        L += ["", "UWAGI PROGRAMU"] + [" - " + u for u in ua]
    if bledy:
        L += ["", "MOŻLIWE BŁĘDY W TEKŚCIE %s (program ich nie poprawia)" % ("DOKUMENTU" if dok else "ORYGINAŁU")] + _blok_bledow(bledy)
    if qa and qa.get("szczegoly"):
        L += ["", "KONTROLA TEKSTU WYKRYŁA"] + [" - " + x for x in qa["szczegoly"][:12]]
    return "\n".join(L)


def ai_prompt_agent_pptx(nazwa, plik, pptx, rob, spec, uwagi, cel="wiernie", dane=None, rodzaj="pptx"):
    """Polecenie dla AGENTA Z PLIKAMI (Claude Code / Cowork, Codex, Gemini CLI, Cursor): krok 0, zadanie, punkty
    (polecenia.polecenie_ai(..., pliki=True)), tabela „kształt treści -> wzór”, błędy tekstu, uwagi. Każdy element w nowej
    linii, punkty numerowane. Agent czyta skill i pliki sam, więc nie dostaje tekstu slajdów."""
    dok = rodzaj == "dokument"
    cel = cel if cel in pptx_convert.CELE else "wiernie"
    bledy = (spec or {}).get("bledy_tekstu") or []
    d = dane or {}
    zadanie = (("Dopracuj prezentację \"%s\" (zrobiona z dokumentu \"%s\"). To wersja z automatu: układ, hasła i liczby są "
                "wstępnie zrobione, Ty robisz z niej prezentację gotową do pokazania; liczbę slajdów (%s) i przekładek "
                "rozdziałów (%s) ustawił człowiek suwakiem. Pracuj na autopilocie według \"%s\" (sekcja 3b) i "
                "references\\dopracowanie.md - krok po kroku, do bramek, bez pytań o zgodę na kolejne kroki.")
               % (pptx, plik, d.get("slajdy", "?"), d.get("rozdzialy", "?"), paths.AGENTS_MD)) if dok else (
        "Dopracuj prezentację \"%s\" (konwersja z \"%s\", cel: %s). To wersja z automatu: układ, hasła i liczby są wstępnie "
        "zrobione, Ty robisz z niej prezentację gotową do pokazania. Pracuj na autopilocie według \"%s\" (sekcja 3b) i "
        "references\\dopracowanie.md - krok po kroku, do bramek, bez pytań o zgodę na kolejne kroki." % (
            pptx, plik, pptx_convert.CELE[cel]["nazwa"].lower(), paths.AGENTS_MD))
    L = [BEZ_SKRYPTOW_AGENT, krok0(), zadanie,
         "Pliki robocze (spec układu spec_program.json - w poleceniach nazywany spec_konwersja.json, to ten sam plik; "
         "decyzje-szablon.json, raport.json): \"%s\"." % rob,
         "CO MASZ ZROBIĆ"]
    L += ["%d. %s" % (i, p) for i, p in enumerate(_punkty(cel, dane, True, rodzaj), 1)]
    tab = polecenia.tabela_ksztaltow()
    if tab:
        L += ["KSZTAŁT TREŚCI -> WZÓR Z SZABLONU", tab]
    L += ["MOŻLIWE BŁĘDY W TEKŚCIE %s (program ich nie poprawia)" % ("DOKUMENTU" if dok else "ORYGINAŁU")] + _blok_bledow(bledy)
    ua = _uwagi_dla_ai(uwagi, bledy)
    if ua:
        L += ["UWAGI PROGRAMU"] + [" - " + u for u in ua]
    return "\n".join(L)


BEZ_PLIKOW_DOPR = ("Jeśli nie masz pliku prezentacji ani zrzutów: nie widzisz wyglądu slajdów - oceniasz treść (blok TEKST "
                   "PREZENTACJI). Pisma, kolorów i ikon nie oceniasz.")


def _teksty_dump(teksty, limit=18000):
    """Tekst prezentacji slajd po slajdzie (z pptx_convert.przeglad) do polecenia dla czatu."""
    L = []
    for nr, ps in teksty or []:
        t = " || ".join(" ".join(str(p).split()) for p in ps if str(p).strip())
        L.append("Slajd %s: %s" % (nr, t or "(bez tekstu)"))
    t = "\n".join(L)
    return t if len(t) <= limit else t[:limit] + "\n(dalsza część tekstu pominięta - za długa)"


def _nazwa_kopii(plik):
    """Kopia, którą poprawia agent: „<nazwa> - dopracowana.pptx” obok oryginału; istniejącego pliku nigdy nie nadpisuje
    („… - dopracowana 2.pptx”, 3…). Zwraca pełną ścieżkę."""
    stem = re.sub(r" - dopracowana( [0-9]+)?$", "", os.path.splitext(os.path.basename(plik))[0])
    kat = os.path.dirname(plik)
    p, n = os.path.join(kat, stem + " - dopracowana.pptx"), 1
    while os.path.exists(p):
        n += 1
        p = os.path.join(kat, "%s - dopracowana %d.pptx" % (stem, n))
    return p


def ai_prompt_dopracowanie(plik, rozp, pr, uwagi, bledy, qa=None, plansze=None):
    """Polecenie dla CZATU BEZ PLIKÓW po przeglądzie pliku w stylu marki: wklejony tekst slajdów, uwagi i błędy tekstu, plansze
    do dołączenia (czat ocenia wtedy też wygląd). Najwyżej LIMIT_POLECENIE znaków (za długie: mniejszy limit bloku tekstu)."""
    t = ""
    for lz in (LIMIT_ZRODLO,) + tuple(z for z, _w in LIMITY_ZAPASOWE):
        t = _ai_prompt_dopracowanie(plik, rozp, pr, uwagi, bledy, qa, plansze, lz)
        if len(t) <= LIMIT_POLECENIE:
            break
    return t


def _ai_prompt_dopracowanie(plik, rozp, pr, uwagi, bledy, qa, plansze, limit_zrodlo):
    pl = (plansze or {}).get("pliki") or []
    L = ["Prezentacja \"%s\" jest już w stylu marki Dobra Kaloria (%s). Program niczego w niej nie zmienił ani nie przebudował: "
         "sprawdził ją i podaje listę uwag poniżej. Twoje zadanie to DOPRACOWANIE, nie przebudowa. Zasady i źródła stylu są "
         "w punktach poniżej - wykonaj je w tej kolejności, nie z własnego wyczucia." % (
             os.path.basename(plik), RODZAJ_NAZWA.get(rozp.get("rodzaj"), "prezentacja w stylu marki")), ""]
    if pl:
        L += [ZALACZNIKI % ((plansze or {}).get("folder", ""), _plikow(len(pl))) + " " + DLA_AGENTA, ""]
    else:
        L += [BEZ_PLIKOW_DOPR + " " + DLA_AGENTA, ""]
    L += ["Plik: %s" % os.path.basename(plik), ""]
    pts = polecenia_dok.punkty_dopracowanie(False) + [polecenia_dok.FORMAT_DOPRACOWANIE]
    L += ["CO MASZ ZROBIĆ"] + ["%d. %s" % (i, p) for i, p in enumerate(pts, 1)]
    tab = polecenia.tabela_ksztaltow()
    if tab:
        L += ["", "KSZTAŁT TREŚCI -> WZÓR Z SZABLONU", tab]
    L += ["", "TEKST PREZENTACJI (slajd po slajdzie)", _teksty_dump((pr or {}).get("teksty"), limit_zrodlo)]
    ua = _uwagi_dla_ai(uwagi, bledy, gdzie="pominięto (za dużo)")
    if ua:
        L += ["", "UWAGI PROGRAMU"] + [" - " + u for u in ua]
    if bledy:
        L += ["", "MOŻLIWE BŁĘDY W TEKŚCIE ORYGINAŁU (program ich nie poprawia)"] + _blok_bledow(bledy)
    if qa and qa.get("szczegoly"):
        L += ["", "KONTROLA TEKSTU WYKRYŁA"] + [" - " + x for x in qa["szczegoly"][:12]]
    return "\n".join(L)


def ai_prompt_agent_dopracowanie(plik, kopia, rob, rozp, uwagi, bledy):
    """Polecenie dla AGENTA Z PLIKAMI po przeglądzie pliku w stylu marki: krok 0, zadanie, punkty (polecenia_dok.punkty_dopracowanie:
    ze specem - pracuj na specu, bez speca - na kopii „… - dopracowana.pptx” w ramach istniejących kształtów i motywu), tabela
    „kształt treści -> wzór”, błędy tekstu, uwagi. Agent czyta skill i pliki sam, więc nie dostaje tekstu slajdów."""
    zadanie = ("Dopracuj prezentację \"%s\" (%s). Jest już w stylu marki Dobra Kaloria: program niczego w niej nie zmienił ani nie "
               "przebudował, tylko ją sprawdził (listy niżej). Pracuj na autopilocie według \"%s\" (sekcja 3b) i "
               "references\\dopracowanie.md - krok po kroku, do bramek, bez pytań o zgodę na kolejne kroki." % (
                   plik, RODZAJ_NAZWA.get(rozp.get("rodzaj"), "prezentacja w stylu marki"), paths.AGENTS_MD))
    L = [BEZ_SKRYPTOW_AGENT, krok0(), zadanie,
         "Pliki robocze (kopia do renderu w podfolderze „kopia”, zrzuty w „qa”, plansze w „plansze”, raport.json): \"%s\"." % rob,
         "CO MASZ ZROBIĆ"]
    L += ["%d. %s" % (i, p) for i, p in enumerate(polecenia_dok.punkty_dopracowanie(True, rozp.get("spec"), plik, kopia), 1)]
    tab = polecenia.tabela_ksztaltow()
    if tab:
        L += ["KSZTAŁT TREŚCI -> WZÓR Z SZABLONU", tab]
    L += ["MOŻLIWE BŁĘDY W TEKŚCIE ORYGINAŁU (program ich nie poprawia)"] + _blok_bledow(bledy)
    ua = _uwagi_dla_ai(uwagi, bledy)
    if ua:
        L += ["UWAGI PROGRAMU"] + [" - " + u for u in ua]
    return "\n".join(L)


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
        back = [x for x in extra if x == "t65"]
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


def krok0():
    r"""KROK 0 w poleceniach dla AI: najpierw sprawdź, czy agent ma skill /prezentacje, a jeśli nie - zainstaluj go
    z folderu WORK programu (zainstaluj-skill.cmd albo kopia folderu skill-prezentacje), potem wczytaj ze skilla SKILL.md
    (sekcja 1b), references\dopracowanie.md (metoda dopracowania wyniku), references\katalog-szablonu.md (tabela
    „kształt treści -> slajd szablonu”) i references\lekcje.md (konwersja: też konwersja-pptx.md pkt 2a i 2b), potem
    identyfikację wizualną Dobra Kaloria (skill ds-dobra-kaloria; zapasowo folder skill-ds-dobra-kaloria obok
    programu). User 07.10: polecenie ma być zakorzenione w skillu i design systemie, nie w pamięci modelu."""
    root = paths.WORK_DIR      # zainstaluj-skill.cmd i kopie skilli leżą w WORK (stary układ: obok programu)
    return ("KROK 0: Sprawdź, czy masz skill /prezentacje: plik %USERPROFILE%\\.claude\\skills\\prezentacje\\SKILL.md "
            "(Claude Code; Codex: %USERPROFILE%\\.codex\\skills\\prezentacje, Gemini: %USERPROFILE%\\.gemini\\skills\\prezentacje, "
            "Cursor: %USERPROFILE%\\.cursor\\skills\\prezentacje). Jeśli go nie ma albo jest starszy niż program (brakuje "
            "w nim pliku references\\dopracowanie.md), zainstaluj - poprzednia wersja zostanie przeniesiona obok, nic nie "
            "jest kasowane: uruchom \"" +
            os.path.join(root, "zainstaluj-skill.cmd") + "\" "
            "(opcjonalnie -Cel \"<katalog skilli Twojego agenta>\") albo skopiuj folder \"" +
            os.path.join(root, "skill-prezentacje") + "\" w to miejsce. "
            "Potem wczytaj ze skilla: SKILL.md (sekcja 1b), references\\dopracowanie.md (metoda dopracowania wyniku; w razie "
            "sprzeczności z innym dokumentem wygrywa ten plik), references\\katalog-szablonu.md (tabela „kształt treści -> "
            "slajd szablonu”) i references\\lekcje.md; przy konwersji gotowej prezentacji dodatkowo "
            "references\\konwersja-pptx.md (pkt 2a i 2b). "
            "KROK 0b: wczytaj identyfikację wizualną Dobra Kaloria: %USERPROFILE%\\.claude\\skills\\ds-dobra-kaloria\\"
            "IDENTYFIKACJA-WIZUALNA.md (i DESIGN-SYSTEM-DOBRA-KALORIA.md pkt 5.4 „Prezentacje PPTX”); jeśli nie ma, "
            "szukaj folderu \"" + os.path.join(root, "skill-ds-dobra-kaloria") + "\"; jeśli i tego nie ma, trzymaj się "
            "skrótu: wzorzec = sklep dobrakaloria.pl, tło białe, kremowe tylko karty, hasła w Mindset, Lato tylko jako krótki "
            "dopisek, zieleń marki ze slotu motywu, dużo światła, mało obrysów. Bez tych dwóch źródeł nie zmieniaj wyglądu.")


# E (13.10): prezentacja z folderu produktu też poprawia ewidentne błędy tekstu - ale tylko w tekstach opisowych
BLEDY_TEKSTU_ZADANIE = ("5) ewidentne błędy tekstu (sklejone słowa, literówki, interpunkcja) wypisz jako „było -> jest”; "
                        "poprawiasz je tylko w tekstach opisowych. Oświadczeń, nazw prawnych, liczb i danych z kart "
                        "wprowadzenia nie zmieniasz - wątpliwości do decyzji")


def ai_prompt(pptx, folder, uwagi):
    lines = [krok0(),
             "Popraw prezentację \"%s\" utworzoną automatycznie z folderu \"%s\"." % (pptx, folder),
             "Najpierw przeczytaj instrukcję: \"%s\" (jak działa program i jak sprawdzić wynik)." % paths.AGENTS_MD,
             "Zadania: 1) uzupełnij teksty w [nawiasach] danymi z folderu (copy, karty wprowadzenia, badanie); "
             "2) każda liczba ma mieć źródło; 3) nie zmieniaj układu, kolorów ani czcionek; "
             "4) na końcu uruchom kontrolę opisaną w instrukcji i pokaż mi zrzuty slajdów; " + BLEDY_TEKSTU_ZADANIE +
             "; 6) sieroty i spójniki na końcu linii usuwa kontrola z instrukcji - doprowadź ją do „Tekst - problemy: 0”."]
    if uwagi:
        lines.append("Uwagi z programu:")
        lines += [" - " + u for u in uwagi]
    return "\n".join(lines)


# klucz: (nazwa, adres w przeglądarce, nazwa aplikacji w menu Start albo None)
AI_CHATS = {"claude": ("Claude", "https://claude.ai/new", "Claude"),
            "chatgpt": ("ChatGPT", "https://chatgpt.com/", "ChatGPT"),
            "gemini": ("Gemini", "https://gemini.google.com/app", None)}


def find_app(name):
    """Windows: AppID aplikacji z menu Start o dokładnie tej nazwie (np. Claude). macOS: ścieżka do <Nazwa>.app. Albo None."""
    return platforma.znajdz_aplikacje(name)
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
        L += ["PLIKI NA KOMPUTERZE", krok0(),
              "Plik prezentacji: %s" % pptx,
              "Folder produktu (karty, copy, grafiki): %s" % folder,
              "Instrukcja programu: %s" % paths.AGENTS_MD,
              "Program w wersji dla AI: %s" % paths.CLI_EXE,
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
         "6. Nie zmieniaj kolejności slajdów, nie dodawaj nowych.",
         "7. " + BLEDY_TEKSTU_ZADANIE[3:] + ".", "", "SLAJDY W PREZENTACJI"]
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


def _zbuduj_plik(spec, uwagi, say):
    """Budowa PPTX ze specu (build_dk / klasyczny). Zwraca ścieżkę pliku (może różnić się od spec["output"], gdy
    ten był otwarty albo zmieniony ręcznie - wtedy wpis w uwagach)."""
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
    return pptx


def _ps_z_biciem(emit, krok, opis, od, do, szacunek_s, script, *args):
    """`_ps` z „biciem serca”: co sekundę zgłasza postęp w przedziale (od, do) kroku, żeby długi render albo kontrola w PowerPoint nie
    wyglądały na zawieszenie (i żeby po przekroczeniu estymaty mógł się pojawić tekst „komputer jest zajęty”). Bez anulowania w środku:
    PowerShell i PowerPoint dokańczają swoją pracę (kolejne uruchomienie nie wejdzie im w drogę)."""
    return _z_postepem(lambda: _ps(script, *args), lambda k, o, fr: emit(k, o, od + (do - od) * fr), lambda: None, krok, opis, szacunek_s)


def _render_i_kontrola(pptx, rob, opts, uwagi, emit, say, zakres=(0.0, 1.0), sufiks="", osadzaj=True):
    """Osadzenie czcionek, zrzuty (PNG) i kontrola tekstu w PowerPoint. Zwraca (qa, miniatury); qa["png"] = katalog zrzutów
    (None, gdy zrzutów nie zrobiono). zakres = (od, do) części paska kroku "qa" dla tego przebiegu. osadzaj=False (dopracowanie,
    kopia pliku użytkownika): render_app.ps1 -NoEmbed - PowerPoint otwiera plik tylko do odczytu i niczego nie zapisuje."""
    def f(x):
        return zakres[0] + (zakres[1] - zakres[0]) * x
    qa = {"problemy": None, "szczegoly": [], "wykonano": False, "png": None}
    thumbs = []
    if powerpoint_available() and not opts.get("bez_qa"):
        name = os.path.splitext(os.path.basename(pptx))[0]
        png = os.path.join(rob, "qa", name)
        if len(png) > MAX_SCIEZKA_PPT:
            skrot = hashlib.sha1(png.encode("utf8")).hexdigest()[:10]
            png = os.path.join(rob, "qa", skrot)
            if len(png) > MAX_SCIEZKA_PPT:
                png = os.path.join(paths.USER_DIR, "qa", skrot)
            say("Długa ścieżka folderu - zrzuty slajdów zapisuję w: " + png)
        emit("qa", ("Osadzam czcionki i robię zrzuty slajdów" if osadzaj else "Robię zrzuty slajdów") + sufiks, f(0.15))
        for old in glob.glob(os.path.join(png, "s*.png")):  # stare zrzuty (własne pliki) - inaczej dłuższa poprzednia
            os.remove(old)                                    # wersja zostawiłaby nadmiarowe miniatury
        flagi = [] if osadzaj else ["-NoEmbed"]
        opis_r = ("Osadzam czcionki i robię zrzuty slajdów" if osadzaj else "Robię zrzuty slajdów") + sufiks
        r = _ps_z_biciem(emit, "qa", opis_r, f(0.15), f(0.55), 40, paths.RENDER_PS, "-Src", pptx, "-Out", png, *flagi)
        if not glob.glob(os.path.join(png, "s*.png")):  # PowerPoint zajety: jedna powtorka po chwili
            time.sleep(5)
            r = _ps_z_biciem(emit, "qa", opis_r, f(0.15), f(0.55), 40, paths.RENDER_PS, "-Src", pptx, "-Out", png, *flagi)
        say(r.strip()[-300:])
        if osadzaj:
            guard.record(pptx)  # PowerPoint zapisał plik od nowa - odśwież sumę (inaczej następna budowa uzna go za ręczny)
        emit("qa", "Sprawdzam tekst (sieroty, kolizje, krawędzie)" + sufiks, f(0.6))
        opis_v = "Sprawdzam tekst (sieroty, kolizje, krawędzie)" + sufiks
        rep = _ps_z_biciem(emit, "qa", opis_v, f(0.6), f(0.88), 40, paths.VERIFY_PS, "-Src", pptx)
        if _COM_ERR.search(rep):
            time.sleep(5)
            rep = _ps_z_biciem(emit, "qa", opis_v, f(0.6), f(0.88), 40, paths.VERIFY_PS, "-Src", pptx)
        m = re.search(r"Tekst - problemy:\s*(\d+)", rep)
        zajety = bool(_COM_ERR.search(rep)) or not glob.glob(os.path.join(png, "s*.png"))
        qa["wykonano"] = bool(m) and not zajety
        if zajety:
            uwagi.append("PowerPoint nie oddał zrzutów slajdów (był zajęty albo folder ma bardzo długą ścieżkę), więc kontrola "
                         "tekstu się nie wykonała. Zamknij okna dialogowe PowerPointa i stwórz prezentację jeszcze raz.")
        qa["problemy"] = int(m.group(1)) if m else None
        qa["szczegoly"] = [l.strip() for l in rep.splitlines() if re.match(r"\s{3}s\d+ ", l)]
        qa["png"] = png
        emit("qa", "Przygotowuję podgląd" + sufiks, f(0.9))
        thumbs = _thumbs(png)
    elif opts.get("bez_qa"):
        say("Pominięto PowerPoint (--bez-qa): bez osadzania czcionek i kontroli tekstu.")
    else:
        if platforma.mac():
            say("macOS: program nie robi podglądu slajdów - pomijam osadzanie czcionek i kontrolę tekstu.")
            uwagi.append("Nie sprawdzono w PowerPoint: na Macu program nie robi podglądu slajdów. Otwórz plik i przejrzyj slajdy.")
        else:
            say("PowerPoint niedostępny - pomijam osadzanie czcionek i kontrolę tekstu.")
            uwagi.append("Nie sprawdzono w PowerPoint (brak PowerPointa na tym komputerze).")
    return qa, thumbs


def _build_and_qa(spec, rob, opts, uwagi, emit, finish_step, check, say, qa_zakres=(0.0, 1.0), finish_qa=True):
    """Budowa PPTX (build_dk / klasyczny) + osadzenie czcionek, zrzuty i kontrola tekstu w PowerPoint.
    Zwraca (ścieżka pliku, wynik kontroli, miniatury). Dopisuje do uwagi. finish_qa=False: krok "qa" kończy wywołujący
    (po pętli "oka", która dokłada do niego własne przebiegi)."""
    emit("budowa", "Buduję prezentację (%d slajdów)" % len(spec["slides"]), 0.1)
    pptx = _zbuduj_plik(spec, uwagi, say)
    finish_step("budowa")
    check()
    qa, thumbs = _render_i_kontrola(pptx, rob, opts, uwagi, emit, say, qa_zakres)
    if finish_qa:
        finish_step("qa")
    return pptx, qa, thumbs


# --- plansze dla czatu (J) -----------------------------------------------------------------------------------------
def zrob_plansze(png_dir, out_dir, per=6, szer=1920):
    """Plansze z gotowych zrzutów slajdów (s01.png…): po `per` slajdów (2 kolumny), numer slajdu w rogu, szerokość ok.
    `szer` px: czat bez plików ocenia z nich WYGLĄD. Pliki wynik_01-06.png, wynik_07-12.png… w out_dir; poprzednie
    wynik_*.png (własne pliki programu) są zastępowane. Zwraca listę ścieżek (pusta, gdy brak zrzutów)."""
    pliki = sorted(f for f in glob.glob(os.path.join(png_dir, "s*.png")) if re.search(r"s\d+\.png$", f, re.I))
    if not pliki:
        return []
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, "wynik_*.png")):
        os.remove(old)
    gap = 12
    cw = (szer - 3 * gap) // 2
    ch = cw * 9 // 16
    try:
        font = ImageFont.truetype("arialbd.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    out = []
    for a in range(0, len(pliki), per):
        grupa = pliki[a:a + per]
        nry = [int(re.search(r"s(\d+)\.png$", f, re.I).group(1)) for f in grupa]
        rzedy = (len(grupa) + 1) // 2
        sheet = Image.new("RGB", (szer, rzedy * ch + (rzedy + 1) * gap), (58, 58, 58))
        d = ImageDraw.Draw(sheet)
        for i, (f, nr) in enumerate(zip(grupa, nry)):
            x, y = gap + (i % 2) * (cw + gap), gap + (i // 2) * (ch + gap)
            with Image.open(f) as im:
                sheet.paste(im.convert("RGB").resize((cw, ch), Image.LANCZOS), (x, y))
            tw = d.textlength(str(nr), font=font)
            d.rounded_rectangle([x, y, x + tw + 24, y + 42], radius=8, fill=(0, 121, 54))
            d.text((x + 12, y + 4), str(nr), fill=(255, 255, 255), font=font)
        path = os.path.join(out_dir, "wynik_%02d-%02d.png" % (nry[0], nry[-1]))
        sheet.save(path, optimize=True)
        out.append(path)
    return out


# --- "oko programu" (I): po renderze program ocenia zrzuty i zmienia układ slajdów z usterkami -------------------------
# kontrola PowerPointa (verify.ps1) -> kody usterek wyglądu; (fragment linii, kod, waga)
_VERIFY_KODY = (("TEKST NA GRAFICE", "KOLIZJA", 3), ("GRAFIKA NA LOGO", "KOLIZJA", 3), ("PRZEPELNIENIE", "PRZEPELNIENIE", 3),
                ("SIEROTA", "SIEROTA", 2), ("ZAWIESZKA", "ZAWIESZKA", 2), ("MYSLNIK", "ZAWIESZKA", 2),
                ("krawedzi", "PRZY_KRAWEDZI", 2))
OKO_MIN_WAGA = 2        # do pętli przebudowy idą usterki o wadze >= 2; waga 1 trafia tylko do „Sprawdź najpierw”
OKO_RUNDY = 2
OKO_LIMIT_S = 240       # gdy pierwsza budowa + kontrola trwała dłużej - tylko 1 runda
OKO_LINII = 10          # najwyżej tyle linii „Sprawdź najpierw: slajd N - …” z oka w uwagach


def usterki_verify(qa):
    """qa["szczegoly"] (linie verify.ps1: "s12 ZAWIESZKA na koncu linii: …") -> {nr: [{kod, opis, waga, zrodlo}]}."""
    out = {}
    for l in (qa or {}).get("szczegoly") or []:
        m = re.match(r"s(\d+)\s+(.*)", l)
        if not m:
            continue
        for frag, kod, waga in _VERIFY_KODY:
            if frag in m.group(2):
                out.setdefault(int(m.group(1)), []).append({"kod": kod, "opis": m.group(2), "waga": waga, "zrodlo": "verify"})
                break
    return out


def ocena_slajdow(qa, spec, oko_mod=None):
    """{nr: [usterki {kod, opis, waga, zrodlo}]} z kontroli PowerPointa (verify) i z oka (oko.ocen_katalog na zrzutach
    qa["png"], ze specem - oko pomija wtedy okładki, przekładki, cytaty). Wszystkie wagi; do pętli liczą się >= OKO_MIN_WAGA."""
    wyn = usterki_verify(qa)
    png = (qa or {}).get("png")
    if oko_mod is not None and png:
        for nr, w in oko_mod.ocen_katalog(png, spec).items():
            for u in w.get("usterki", []):
                wyn.setdefault(nr, []).append({"kod": u["kod"], "opis": u["opis"], "waga": u.get("waga", 1), "zrodlo": "oko"})
    return wyn


def _miara(us):
    """Im mniejsza, tym lepszy slajd: (liczba usterek wagi >= 2, ich suma wag). Waga 1 nie liczy się do porównania."""
    ciezkie = [u for u in us or [] if u["waga"] >= OKO_MIN_WAGA]
    return (len(ciezkie), sum(u["waga"] for u in ciezkie))


def _pismo_hasel(sl):
    """Najmniejsze pismo haseł (lead, big) slajdu `uklad` w pt według układu build_dk; None = nie dotyczy / nie da się policzyć."""
    try:
        if not isinstance(sl, dict) or sl.get("type") != "uklad":
            return None
        ms, _f = build_dk.uklad_layout(sl)
        if ms is None:
            return None
        pts = []
        for m, r in zip(ms, sl["rows"]):
            if m["kind"] in ("text", "quote") and r["k"] in ("lead", "big"):
                pts.append(m["pt"])
            elif m["kind"] == "cols":
                for (parts, _iw), it in zip(m["cols"], m["items"]):
                    for (kind, _y, _h, d), bl in zip(parts, it.get("blocks", [])):
                        if kind == "txt" and bl["k"] in ("lead", "big"):
                            pts.append(d["pt"])
        return min(pts) if pts else None
    except Exception:
        return None


def petla_oka(spec, wynik, zbuduj, ocen, popraw, spec_path, rundy=OKO_RUNDY, say=None, emit=None, pismo=None):
    """Pętla: ocena zrzutów -> `popraw` (inny wariant układu slajdów z usterkami) -> budowa + render + ocena ponownie ->
    dla każdego zmienionego slajdu ZOSTAJE LEPSZA wersja (nigdy gorsza; remis = poprzednia) -> najwyżej `rundy` rund.
    Slajd, którego wariant nie poprawił wyniku, nie jest próbowany drugi raz.

    spec: słownik specu (z "slides"); wynik: (pptx, qa, miniatury) po pierwszej budowie;
    zbuduj(spec, runda, faza) -> (pptx, qa, miniatury): budowa + render + kontrola (faza 1 = próba, 2 = odbudowa po cofnięciu);
    ocen(wynik, spec) -> {nr: [usterki {kod, opis, waga}]}; popraw(spec_path, {nr: [kody]}) -> [nr zmienionych]
    (pptx_convert.popraw_po_renderze: czyta i zapisuje spec_path); emit(runda, rundy, tekst); pismo(slajd) -> najmniejsze
    pismo haseł w pt albo None: nowy wariant, w którym pismo haseł spadło, jest cofany nawet przy mniejszej liczbie usterek.
    Zwraca {spec, wynik, ocena, zmienione, odrzucone, rundy}."""
    say = say or (lambda t: None)
    emit = emit or (lambda *a: None)
    pismo = pismo or (lambda sl: None)
    ocena = ocen(wynik, spec)
    zmienione, odrzucone, proby, wykonane = [], [], set(), 0
    for r in range(1, rundy + 1):
        kody = {nr: list(dict.fromkeys(u["kod"] for u in us if u["waga"] >= OKO_MIN_WAGA)) for nr, us in ocena.items()
                if nr not in proby and any(u["waga"] >= OKO_MIN_WAGA for u in us)}
        if not kody:
            break
        emit(r, rundy, "start")
        kopia = copy.deepcopy(spec)
        try:
            with open(spec_path, "w", encoding="utf8") as fh:
                json.dump(spec, fh, ensure_ascii=False, indent=1)
            zm = list(popraw(spec_path, kody) or [])
            with open(spec_path, encoding="utf8") as fh:
                nowy = json.load(fh)
        except Exception as e:
            say("Oko: zmiana układu się nie powiodła (%s: %s) - zostaje poprzedni." % (type(e).__name__, e))
            break
        if len(nowy.get("slides", [])) != len(kopia["slides"]):
            say("Oko: zmiana układu zmieniła liczbę slajdów - odrzucona (konwersja ma być 1:1).")
            break
        zm = [nr for nr in zm if isinstance(nr, int) and 1 <= nr <= len(kopia["slides"])
              and nowy["slides"][nr - 1] != kopia["slides"][nr - 1]]
        if not zm:
            say("Oko: brak innego wariantu układu dla slajdów z usterkami (%s)." % ", ".join(str(n) for n in sorted(kody)))
            break
        proby |= set(zm)
        wynik2 = zbuduj(nowy, r, 1)
        ocena2 = ocen(wynik2, nowy)
        wykonane += 1
        if (wynik2[1] or {}).get("wykonano", True):
            def spadlo(nr):   # pismo haseł nowego wariantu mniejsze niż poprzedniego
                a, b = pismo(kopia["slides"][nr - 1]), pismo(nowy["slides"][nr - 1])
                return a is not None and b is not None and b < a
            gorsze = [nr for nr in zm if _miara(ocena2.get(nr)) >= _miara(ocena.get(nr)) or spadlo(nr)]
        else:   # PowerPoint nie oddał zrzutów: nowego układu nie da się ocenić - wracamy do poprzedniego
            gorsze = list(zm)
            say("Oko: po zmianie układu PowerPoint nie oddał zrzutów - cofam zmianę.")
        if gorsze:  # wracamy do poprzedniego układu tych slajdów i budujemy plik jeszcze raz (zapis nadpisał poprzedni)
            for nr in gorsze:
                nowy["slides"][nr - 1] = kopia["slides"][nr - 1]
            wynik2 = zbuduj(nowy, r, 2)
            ocena2 = ocen(wynik2, nowy)
        zmienione += [nr for nr in zm if nr not in gorsze]
        odrzucone += gorsze
        say("Oko, runda %d: próbowano slajdy %s; zostawiono nowy układ: %s; cofnięto: %s." % (
            r, ", ".join(str(n) for n in sorted(zm)), ", ".join(str(n) for n in sorted(set(zm) - set(gorsze))) or "-",
            ", ".join(str(n) for n in sorted(gorsze)) or "-"))
        spec, wynik, ocena = nowy, wynik2, ocena2
    return {"spec": spec, "wynik": wynik, "ocena": ocena, "zmienione": sorted(set(zmienione)),
            "odrzucone": sorted(set(odrzucone)), "rundy": wykonane}


def _oko_dla_pptx(spec, wynik, rob, opts, emit, say, t_pierwszy_s):
    """Wpięcie pętli w konwersję: moduł oko i pptx_convert.popraw_po_renderze są opcjonalne - brak modułu, funkcji albo
    wyjątek = pętla pominięta (wpis w logu), konwersja kończy się jak bez niej. Zwraca wynik petla_oka albo None."""
    try:
        import oko
        popraw = pptx_convert.popraw_po_renderze
    except Exception as e:
        say("Oko programu niedostępne (%s: %s) - pomijam poprawianie układu po zrzutach." % (type(e).__name__, e))
        return None
    rundy = 1 if t_pierwszy_s > OKO_LIMIT_S else OKO_RUNDY
    if rundy < OKO_RUNDY:
        say("Budowa i kontrola trwały %d s - robię tylko 1 rundę poprawiania układu." % t_pierwszy_s)

    def zbuduj(sp, r, faza):
        lo = 0.5 + 0.25 * (r - 1) + (0.125 if faza == 2 else 0.0)
        suf = " (runda %d z %d%s)" % (r, rundy, ", wracam do lepszej wersji" if faza == 2 else "")
        emit("qa", "Buduję poprawiony układ" + suf, lo)
        u = []
        pptx = _zbuduj_plik(sp, u, say)
        qa, th = _render_i_kontrola(pptx, rob, opts, u, emit, say, (lo, lo + 0.125), suf)
        return pptx, qa, th

    def emit_r(r, n, faza):
        emit("qa", "Oglądam zrzuty i poprawiam układ (runda %d z %d)" % (r, n), 0.5 + 0.25 * (r - 1))

    try:
        return petla_oka(spec, wynik, zbuduj, lambda w, sp: ocena_slajdow(w[1], sp, oko), popraw,
                         os.path.join(rob, "spec_oko.json"), rundy, say, emit_r, pismo=_pismo_hasel)
    except Exception as e:  # pętla nigdy nie psuje konwersji; stan sprzed wyjątku jest w pliku, który właśnie zbudowano
        _log_file(traceback.format_exc())
        say("Oko: pętla przerwana (%s: %s) - zostaje ostatnio zbudowany plik." % (type(e).__name__, e))
        return None


def _oko_dla_dokumentu(spec, wynik, rob, opts, emit, say, t_pierwszy_s):
    """Pętla poprawek dokumentu: `dokument.petla_poprawek` (po renderze ocena zrzutów i kontroli tekstu, inny wariant układu slajdów
    z usterkami, ponowna budowa; nowy układ zostaje tylko gdy ma MNIEJ usterek niż przed) - to samo co `petla_oka` w konwersji, ale
    na specu z `dokument.zloz` (warianty układu siedzą w spec["warianty"]). Brak funkcji w skillu albo wyjątek = None (wpis w logu),
    wynik jak z petla_oka: {spec, wynik: (pptx, qa, miniatury), ocena, zmienione, odrzucone, rundy}."""
    petla = getattr(dokument, "petla_poprawek", None)
    pomiar_f = getattr(dokument, "usterki_po_renderze", None)
    if petla is None or pomiar_f is None:
        say("Pętla poprawek dokumentu niedostępna w skillu - pomijam poprawianie układu po zrzutach.")
        return None
    try:
        import oko as oko_mod
    except Exception:  # bez oka tylko kontrola tekstu z PowerPointa
        oko_mod = None
    rundy = 1 if t_pierwszy_s > OKO_LIMIT_S else OKO_RUNDY
    if rundy < OKO_RUNDY:
        say("Budowa i kontrola trwały %d s - robię tylko 1 rundę poprawiania układu." % t_pierwszy_s)
    st = {"pptx": wynik[0], "qa": wynik[1], "thumbs": wynik[2], "do_renderu": False, "buduj": 0}
    spec.setdefault("uwagi", [])

    def pomiar():
        if st["do_renderu"]:
            lo = 0.5 + 0.1 * min(st["buduj"], 4)
            suf = " (przebudowa %d)" % st["buduj"]
            st["qa"], st["thumbs"] = _render_i_kontrola(st["pptx"], rob, opts, [], emit, say, (lo, lo + 0.1), suf)
            st["do_renderu"] = False
        qa = st["qa"]
        if not (qa.get("wykonano") and qa.get("png")):   # PowerPoint nie oddał zrzutów: nie ma czego oceniać
            return {}, ""
        v = "\n".join("   " + x for x in (qa.get("szczegoly") or []))   # linie verify.ps1 w postaci, jakiej oczekuje usterki_po_renderze
        return pomiar_f(qa["png"], spec, v), v

    def buduj():
        st["buduj"] += 1
        emit("qa", "Buduję poprawiony układ (przebudowa %d)" % st["buduj"], 0.5 + 0.1 * min(st["buduj"], 4))
        st["pptx"] = _zbuduj_plik(spec, [], say)
        st["do_renderu"] = True

    emit("qa", "Oglądam zrzuty i poprawiam układ", 0.5)
    try:
        _wyn, poprawione = petla(spec, pomiar, buduj, rundy)
        ocena = ocena_slajdow(st["qa"], spec, oko_mod)
    except Exception as e:  # pętla nigdy nie psuje wyniku; stan sprzed wyjątku jest w ostatnio zbudowanym pliku
        _log_file(traceback.format_exc())
        say("Pętla poprawek dokumentu przerwana (%s: %s) - zostaje ostatnio zbudowany plik." % (type(e).__name__, e))
        return None
    return {"spec": spec, "wynik": (st["pptx"], st["qa"], st["thumbs"]), "ocena": ocena, "zmienione": sorted(set(poprawione)),
            "odrzucone": [], "rundy": st["buduj"]}


def build(folder, opts, progress=None, log=None, cancel=None):
    """Główna praca. progress(krok_id, opis, procent, eta_s); log(tekst); cancel = threading.Event."""
    t0 = time.time()
    opts = dict(opts or {})
    # opts["scenariusz"] (CLI --scenariusz): budowa z TEGO pliku, folder = folder prezentacji (bez rozpoznawania wejścia)
    folder = os.path.abspath(folder) if opts.get("scenariusz") else normalize_folder(folder)
    est_total = float(opts.get("szacowany_czas_s") or 40)
    done_w = 0
    weights = dict((s, wt) for s, _, wt in STEPS)
    dopr = _czy_dopracowanie(folder, opts)
    tryb = "scenariusz" if opts.get("scenariusz") else tryb_wejscia(folder)
    if tryb == "scenariusz" and opts.get("bez_ai"):   # folder ma scenariusz, ale człowiek chce budowy wprost z dokumentów
        tryb = "pakiet"
    if os.path.isfile(folder) or tryb in ("scenariusz", "pakiet"):
        weights.update(DOPR_WEIGHTS if dopr else PPTX_WEIGHTS)

    def emit(step, opis, frac):
        nonlocal done_w
        w = weights[step]
        pct = min(99, int(done_w + w * max(0.0, min(1.0, frac))))
        el = time.time() - t0
        lin = int(el / pct * (100 - pct)) if pct >= 8 else 0   # ekstrapolacja z dotychczasowego postępu
        eta = max(1, int(max(lin, est_total - el)))             # nigdy mniej, niż zostało do szacunku (przy dobrym szacunku pasek nie „przyspiesza”)
        if el > ZAJETY_MNOZNIK * est_total:   # trwa dłużej niż szacunek: tekst mówi, co się dzieje, zamiast stać
            opis = ZAJETY_TEKST
        if progress:
            progress(step, opis, pct, eta)
        _log_file("%3d%% %s" % (pct, opis))

    def finish_step(step):
        nonlocal done_w
        done_w += weights[step]

    def check():
        if cancel is not None and cancel.is_set():
            raise Cancelled()

    def say(t):
        _log_file(t)
        if log:
            log(t)

    if tryb == "scenariusz":    # folder prezentacji (1.3): budowa 1:1 z najnowszego scenariusza
        return _build_scenariusz(folder, opts, t0, emit, finish_step, check, say, progress)
    if tryb == "pakiet":        # folder prezentacji bez scenariusza: Źródła bez AI (dokument albo kilka dokumentów)
        return _build_pakiet(folder, opts, t0, emit, finish_step, check, say, progress)
    if os.path.isfile(folder):  # gotowa prezentacja (konwersja bez utraty treści) albo dokument
        if tryb == "dokument":
            return _build_dokument(folder, opts, t0, emit, finish_step, check, say, progress)
        if dopr:   # plik już w stylu marki: niczego nie budujemy ani nie zmieniamy
            return _build_dopracowanie(folder, opts, t0, emit, finish_step, check, say, progress)
        return _build_pptx(folder, opts, t0, emit, finish_step, check, say, progress)
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
    os.makedirs(os.path.dirname(spec["output"]), exist_ok=True)   # --wyjscie na jeszcze nieistniejący katalog (jak przy konwersji)
    uwagi = list(spec.pop("uwagi", []))
    json.dump(spec, open(os.path.join(rob, "spec_program.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("slajdy")
    check()
    # 4-5. budowa i kontrola w PowerPoint (wspólne z trybem pptx)
    pptx, qa, thumbs = _build_and_qa(spec, rob, opts, uwagi, emit, finish_step, check, say)
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


def _jakosc(spec, rob, opts, uwagi, emit, finish_step, check, say, spec_json, dok=False):
    """Wspólne dla konwersji i dokumentu: budowa + zrzuty + kontrola tekstu w PowerPoint + pętla „oka” (ocena zrzutów, inny
    wariant układu slajdów z usterkami, ponowna budowa). dok=True: pętla poprawek dokumentu (dokument.petla_poprawek).
    Kończy krok „qa”. Zwraca dict(pptx, qa, thumbs, spec, oko, oko_linie)."""
    oko_on = opts.get("oko", True) is not False
    t_qa = time.time()
    pptx, qa, thumbs = _build_and_qa(spec, rob, opts, uwagi, emit, finish_step, check, say,
                                     qa_zakres=(0.0, 0.5 if oko_on else 1.0), finish_qa=False)
    t_pierwszy = int(time.time() - t_qa)
    oko = {"uruchomione": False, "rundy": 0, "zmienione": [], "odrzucone": [], "pozostale": {}, "czas_s": 0, "pierwsza_budowa_s": t_pierwszy}
    oko_linie = []
    if oko_on and qa.get("wykonano") and qa.get("png"):
        t_oko = time.time()
        w = (_oko_dla_dokumentu if dok else _oko_dla_pptx)(spec, (pptx, qa, thumbs), rob, opts, emit, say, t_pierwszy)
        if w:
            spec, (pptx, qa, thumbs) = w["spec"], w["wynik"]
            json.dump(spec, open(spec_json, "w", encoding="utf8"), ensure_ascii=False, indent=1)
            wygladu = sorted(((nr, u) for nr, us in w["ocena"].items() for u in us if u.get("zrodlo") == "oko"),
                             key=lambda x: (-x[1]["waga"], x[0]))   # usterki wyglądu (oko); tekstowe kontroli PowerPointa są w "Tekst na slajdach"
            oko.update(uruchomione=True, rundy=w["rundy"], zmienione=w["zmienione"], odrzucone=w["odrzucone"],
                       pozostale=[{"slajd": nr, "kod": u["kod"], "waga": u["waga"], "opis": u["opis"]} for nr, u in wygladu])
            if w["zmienione"]:
                oko_linie.append("Po obejrzeniu zrzutów poprawiłem układ slajdów: %s" % ", ".join(str(n) for n in w["zmienione"]))
            oko_linie += ["Sprawdź najpierw: slajd %d - %s" % (nr, u["opis"]) for nr, u in wygladu[:OKO_LINII]]
            if len(wygladu) > OKO_LINII:
                oko_linie.append("…i %d kolejnych usterek wyglądu w raport.json (oko)" % (len(wygladu) - OKO_LINII))
        oko["czas_s"] = int(time.time() - t_oko)
    finish_step("qa")
    if oko["uruchomione"] and not qa.get("wykonano"):
        uwagi.append("PowerPoint nie oddał zrzutów po poprawce układu (był zajęty), więc kontrola tekstu po niej się nie "
                     "wykonała. Zamknij okna dialogowe PowerPointa i stwórz prezentację jeszcze raz.")
    return {"pptx": pptx, "qa": qa, "thumbs": thumbs, "spec": spec, "oko": oko, "oko_linie": oko_linie}


def _plansze_wyniku(pptx, qa, say, folder=None):
    """Plansze dla czatu (J): obrazy z ostatniego renderu, w podfolderze „plansze” obok prezentacji (otwiera go „Pokaż folder”);
    `folder` wskazuje inne miejsce (dopracowanie: katalog roboczy, nie folder użytkownika)."""
    plansze, folder_wl = [], folder
    folder = None
    if qa.get("png") and qa.get("wykonano"):
        try:
            folder = folder_wl or os.path.join(os.path.dirname(pptx), "plansze")
            plansze = zrob_plansze(qa["png"], folder)
        except Exception as e:
            plansze = []
            say("Plansze dla czatu się nie zrobiły (%s: %s)." % (type(e).__name__, e))
        if not plansze:
            folder = None
    return plansze, folder


def _uwaga_podpowiedzi(pptx, rob, zrodlo=""):
    """Uwaga dla ekranu „Gotowe”, liczona z GOTOWEGO pliku: „Slajdy 43, 44 mają podpowiedzi w nawiasach - uzupełnij je albo usuń”
    (pptx_convert.przeglad: pola tekstu w [nawiasach] na slajdach pliku). Podpowiedzi, które stały już w tekście oryginału (`zrodlo`,
    np. przypisy [1]), nie liczą się. None = nic do zgłoszenia albo przegląd się nie udał (wpis w logu)."""
    f = getattr(pptx_convert, "przeglad", None)
    if f is None:
        return None
    try:
        pr = f(pptx, rob)
    except Exception:
        _log_file(traceback.format_exc())
        return None
    zr = " ".join((zrodlo or "").split())
    nry = sorted({nr for nr, t in (pr.get("podpowiedzi") or []) if " ".join(str(t).split()) not in zr})
    if not nry:
        return None
    lista = ", ".join(str(n) for n in nry[:8]) + (" i %d innych" % (len(nry) - 8) if len(nry) > 8 else "")
    if len(nry) == 1:
        return "Slajd %s ma podpowiedzi w nawiasach - uzupełnij je albo usuń" % lista
    return "Slajdy %s mają podpowiedzi w nawiasach - uzupełnij je albo usuń" % lista


def _wyjscie_krotkie(spec, uwagi, say):
    """PowerPoint (COM) nie otwiera pliku o ścieżce > 259 znaków: zrzuty i kontrola tekstu by się nie wykonały. Za długą nazwę skracamy
    w tym samym folderze; gdy sam folder jest za długi - plik idzie do katalogu użytkownika (w uwagach jest informacja gdzie)."""
    out = spec["output"]
    if len(out) <= MAX_SCIEZKA_PPT:
        return
    kat, nazwa = os.path.split(out)
    stem, ext = os.path.splitext(nazwa)
    ile = MAX_SCIEZKA_PPT - len(kat) - 1 - len(ext)
    m = re.search(r" - (nowy styl|stary styl|prezentacja).*$", stem)   # końcówka z nazwy wyniku („ - nowy styl - rozwinięta”) zostaje cała
    ogon, glowa = (m.group(0), stem[:m.start()]) if m else ("", stem)
    if ile - len(ogon) >= 15:
        nowy = os.path.join(kat, glowa[:ile - len(ogon)].rstrip(" -") + ogon + ext)
        uwagi.append("Nazwa pliku była za długa dla PowerPointa - zapisałem prezentację jako „%s”." % os.path.basename(nowy))
    else:
        nowy = os.path.join(paths.USER_DIR, "wyniki", stem[:60].rstrip(" -") + ext)
        uwagi.append("Folder ma bardzo długą ścieżkę (PowerPoint takich plików nie otwiera) - zapisałem prezentację w: %s" % nowy)
    say("Ścieżka wyniku za długa (%d znaków) - zapis w: %s" % (len(out), nowy))
    spec["output"] = nowy


def _build_pptx(plik, opts, t0, emit, finish_step, check, say, progress):
    """Konwersja gotowej prezentacji: extract -> compose (układ 1:1 z pozycji na starym slajdzie, klocki szablonu) -> build_dk
    -> kontrola w PowerPoint -> "oko" (ocena zrzutów, inny wariant układu slajdów z usterkami, ponowna budowa) -> pokrycie
    treści i wierność układu -> plansze dla czatu.
    opts["cel"]: wiernie | rozwin | skroc (pptx_convert.CELE). opts["sekcje"]: id rozdziałów widocznych w pokazie
    (r01...; pozostałe ZOSTAJĄ w pliku jako slajdy ukryte - nic nie znika) oraz, przy celu "rozwin", id pustych slajdów
    z szablonu (t10...), które program wstawia przed zakończeniem. opts["wizualizacje"]: False wyłącza packshoty.
    opts["oko"]: False wyłącza pętlę poprawiania układu po zrzutach (CLI --bez-oka)."""
    rob = _pptx_rob(plik)
    cel = opts.get("cel") if opts.get("cel") in pptx_convert.CELE else "wiernie"
    emit("folder", "Czytam prezentację", 0)
    model = _pptx_model(plik)
    say("Prezentacja: %s, slajdów: %d, akapitów: %d" % (os.path.basename(plik), len(model["slajdy"]), model["akapity"]))
    finish_step("folder")
    check()
    emit("grafiki", "Przygotowuję grafiki (%d)" % model["stat"]["grafiki"], 0.5)
    finish_step("grafiki")
    check()
    emit("slajdy", "Układam slajdy", 0.3)
    wybrane = opts.get("sekcje")
    rozdz = [x for x in wybrane if not re.fullmatch(r"t\d+", x)] if wybrane is not None else None
    dod = [x for x in (wybrane or []) if re.fullmatch(r"t\d+", x)] if cel == "rozwin" else []
    spec = pptx_convert.compose(model, {"cel": cel, "sekcje": rozdz, "styl": opts.get("styl"),
                                        "wyjscie": opts.get("wyjscie"), "wizualizacje": opts.get("wizualizacje", True)})
    uwagi = list(spec.pop("uwagi"))
    nowe = pptx_convert.wstaw_dodatki(spec, template_slides(dod, "[Nazwa produktu]", [], [], [])) if dod else []
    if nowe:
        uwagi.insert(0, "Dołożyłem puste slajdy z szablonu: %d (nr %s, przed zakończeniem). Uzupełnij teksty "
                        "w [nawiasach] - sam program niczego nie dopisuje." % (len(nowe), ", ".join(str(n) for n in nowe)))
    _wyjscie_krotkie(spec, uwagi, say)
    os.makedirs(os.path.dirname(spec["output"]), exist_ok=True)
    spec_json = os.path.join(rob, "spec_program.json")
    json.dump(spec, open(spec_json, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("slajdy")
    check()
    j = _jakosc(spec, rob, opts, uwagi, emit, finish_step, check, say, spec_json)
    pptx, qa, thumbs, spec, oko, oko_linie = j["pptx"], j["qa"], j["thumbs"], j["spec"], j["oko"], j["oko_linie"]
    emit("zapis", "Sprawdzam, czy nic nie zginęło", 0.3)
    poprawki = spec.get("poprawki") or None
    cov = pptx_convert.coverage(plik, pptx, spec["mapa"], rob=rob, poprawki=poprawki)
    wier = pptx_convert.wiernosc(model, pptx, spec["mapa"], nowe=len(nowe), poprawki=poprawki,
                                 zdjete=pptx_convert.zdjete_znaki(spec))
    say(cov["tekst"])
    say(wier["tekst"])
    for m in cov["brakuje"][:10]:
        uwagi.append("Brakuje (slajd %d oryginału): %s" % (m["slajdy"] if "slajdy" in m else m["slajd"], m["tekst"]))
    for u in wier["usterki"][:10]:
        uwagi.append("Do sprawdzenia - " + u)
    pod = _uwaga_podpowiedzi(pptx, rob, _source_dump(model, limit=10 ** 9))
    if pod:   # jedno zdanie z numerami slajdów zastępuje ogólne „Dołożyłem puste slajdy…”: mówi, które slajdy zostały z podpowiedziami
        uwagi[:] = [u for u in uwagi if not u.startswith("Dołożyłem puste slajdy z szablonu")]
        uwagi.insert(0, pod)
    uwagi[0:0] = oko_linie
    uwagi.insert(0, wier["tekst"])
    uwagi.insert(0, cov["tekst"])
    plansze, plansze_folder = _plansze_wyniku(pptx, qa, say)
    wszystkie = len(spec["slides"])
    ukryte = sum(1 for x in spec["slides"] if x.get("hidden"))
    try:
        cel_slajdy = int(opts.get("cel_slajdy") or 0)
    except (TypeError, ValueError):
        cel_slajdy = 0
    dane = {"cel_slajdy": cel_slajdy or max(3, int(round(0.6 * (wszystkie - ukryte)))), "widoczne": wszystkie - ukryte,
            "wszystkie": wszystkie}
    emit("zapis", "Zapisuję raport", 0.6)
    bledy = spec.get("bledy_tekstu") or []
    uwagi_wyniku, bledy_okno = uwagi_okno(uwagi, bledy)
    _zapisz_uwagi(rob, uwagi, say)
    result = {"ok": True, "tryb": "pptx", "uwagi_top": _uwagi_top(uwagi_wyniku, bledy, oko, [w.get("slajd") for w in spec.get("wizualizacje", [])
                                                                                           if isinstance(w, dict) and w.get("slajd")], ukryte), "pptx": pptx, "nazwa": os.path.basename(pptx), "folder": os.path.dirname(plik),
              "plik": plik, "slajdy": wszystkie, "ukryte": ukryte, "nowe": nowe, "cel": cel,
              "cel_nazwa": pptx_convert.CELE[cel]["nazwa"], "cel_slajdy": dane["cel_slajdy"] if cel == "skroc" else None,
              "czas_s": int(time.time() - t0), "miniatury": thumbs, "qa": qa,
              "uwagi": uwagi_wyniku, "uwagi_pelne": uwagi, "bledy_okno": bledy_okno, "bledy_tekstu": bledy, "oko": oko,
              "pokrycie": cov, "wiernosc": wier, "sprawdz": spec.get("sprawdz", []),
              "wizualizacje": spec.get("wizualizacje", []), "styl": "nowy",
              "plansze": plansze, "plansze_folder": plansze_folder,
              "prompt_ai": ai_prompt_pptx(os.path.basename(pptx), plik, model, spec, uwagi, cov, qa, pptx, cel=cel, dane=dane,
                                          plansze={"folder": plansze_folder, "pliki": plansze}),
              "prompt_agent": ai_prompt_agent_pptx(os.path.basename(pptx), plik, pptx, rob, spec, uwagi, cel=cel, dane=dane),
              "raport": os.path.join(rob, "raport.json")}
    json.dump({k: v for k, v in result.items() if k != "miniatury"},
              open(result["raport"], "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("zapis")
    if progress:
        progress("zapis", "Gotowe", 100, 0)
    return result


def _z_postepem(praca, emit, check, krok, opis, szacunek_s):
    """Wykonuje praca() w wątku, a w tym czasie co sekundę zgłasza postęp (długi krok bez wiadomości wygląda jak zawieszenie) i
    sprawdza anulowanie (check() może rzucić Cancelled: wątek dokańcza w tle, jego wynik jest wyrzucany). Wyjątek z praca()
    leci dalej bez zmian."""
    wynik = {}

    def run():
        try:
            wynik["v"] = praca()
        except BaseException as e:  # noqa: BLE001 - przekazujemy dalej w wątku wywołującego
            wynik["e"] = e
    t = threading.Thread(target=run, daemon=True)
    t.start()
    t0 = time.time()
    while t.is_alive():
        t.join(1.0)
        emit(krok, opis, min(0.95, (time.time() - t0) / max(float(szacunek_s), 1.0)))
        check()
    if "e" in wynik:
        raise wynik["e"]
    return wynik["v"]


def _w_zakresie(v, lo, hi, dom):
    try:
        v = int(v)
    except (TypeError, ValueError):
        v = dom
    return max(lo, min(hi, v))


def _build_dokument(plik, opts, t0, emit, finish_step, check, say, progress):
    """Prezentacja z dokumentu: dokument.wczytaj -> dokument.zloz (liczba slajdów i rozdziałów z dwóch suwaków) -> build_dk ->
    kontrola w PowerPoint -> „oko” -> dokument.pokrycie (wiersz „Treść”) -> plansze. Ta sama ścieżka jakości co konwersja.
    opts["slajdy"], opts["rozdzialy"]: wartości suwaków (poza zakresem z dokumentu są przycinane); opts["oko"]: False wyłącza pętlę."""
    rob = _pptx_rob(plik)
    emit("folder", "Czytam dokument", 0)
    model = _dok_model(plik)
    st = dokument.statystyka(model)
    sw = _suwaki_dokumentu(st)
    say("Dokument: %s, słów: %d, akapitów: %d, nagłówków: %d" % (
        os.path.basename(plik), st.get("slowa", 0), st.get("akapity", 0), sum((st.get("naglowki") or {}).values())))
    finish_step("folder")
    check()
    emit("grafiki", "Przygotowuję obrazy (%d)" % (st.get("obrazy") or 0), 0.5)
    finish_step("grafiki")
    check()
    emit("slajdy", "Układam slajdy", 0.3)
    n_sl = _w_zakresie(opts.get("slajdy"), sw["slajdy"]["min"], sw["slajdy"]["max"], sw["slajdy"]["domyslnie"])
    n_rz = _w_zakresie(opts.get("rozdzialy"), 0, sw["rozdzialy"]["max"], sw["rozdzialy"]["domyslnie"])
    # składanie slajdów liczy układy z pomiaru (pomiar 13.10: ok. 1,5 s na slajd) - w tle, żeby pasek postępu się nie zatrzymał
    spec = _z_postepem(lambda: dokument.zloz(model, {"slajdy": n_sl, "rozdzialy": n_rz, "wyjscie": opts.get("wyjscie"), "styl": "nowy"}),
                       emit, check, "slajdy", "Układam slajdy", 1.6 * n_sl)
    uwagi = list(opts.get("uwagi_wstep") or []) + list(spec.get("uwagi", []))
    spec["uwagi"] = []   # dokument.popraw_po_renderze dopisuje tu wpis o zmianie układu; własną linię z oka składa silnik
    if opts.get("wyjscie_plik"):   # folder prezentacji (1.3): wynik z numerem wersji w folderze prezentacji
        spec["output"] = opts["wyjscie_plik"]
    n_tresc = int((spec.get("ustawienia") or {}).get("slajdy") or 0)
    if n_tresc > n_sl + 2:   # dokument.zloz nie zawęża liczby slajdów poniżej progów pisma - człowiek ma o tym wiedzieć
        uwagi.append("Suwak: %d slajdów, w pliku jest ich %d z treścią - bez AI program niczego nie skraca, tylko dzieli slajdy, na "
                     "których treść nie mieści się czytelnie. Krótszą prezentację da »Przygotuj z AI« (czat sam skraca treść)." % (n_sl, n_tresc))
    _wyjscie_krotkie(spec, uwagi, say)
    os.makedirs(os.path.dirname(spec["output"]), exist_ok=True)
    spec_json = os.path.join(rob, "spec_program.json")
    json.dump(spec, open(spec_json, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("slajdy")
    check()
    j = _jakosc(spec, rob, opts, uwagi, emit, finish_step, check, say, spec_json, dok=True)
    pptx, qa, thumbs, spec, oko, oko_linie = j["pptx"], j["qa"], j["thumbs"], j["spec"], j["oko"], j["oko_linie"]
    spec.pop("uwagi", None)
    emit("zapis", "Sprawdzam, czy nic nie zginęło", 0.3)
    cov = dokument.pokrycie(model, pptx)
    say(cov.get("tekst", ""))
    for m in (cov.get("brakuje") or [])[:10]:
        uwagi.append("Brakuje: %s" % (m if isinstance(m, str) else (m.get("tekst") or str(m))))
    uwagi[0:0] = oko_linie
    uwagi.insert(0, cov.get("tekst", ""))
    plansze, plansze_folder = _plansze_wyniku(pptx, qa, say)
    wszystkie = len(spec["slides"])
    if wszystkie != n_sl:
        say("Liczba slajdów treści w pliku: %d (suwak: %d) - program podzielił slajdy, na których treść nie mieściła się czytelnie."
            % (wszystkie, n_sl))
    dane = {"slajdy": n_sl, "rozdzialy": n_rz, "cel_slajdy": n_sl, "widoczne": wszystkie, "wszystkie": wszystkie}
    emit("zapis", "Zapisuję raport", 0.6)
    bledy = spec.get("bledy_tekstu") or []
    uwagi_wyniku, bledy_okno = uwagi_okno(uwagi, bledy, rodzaj="dokument")
    _zapisz_uwagi(rob, uwagi, say)
    result = {"ok": True, "tryb": "dokument", "uwagi_top": _uwagi_top(uwagi_wyniku, bledy, oko), "pptx": pptx, "nazwa": os.path.basename(pptx),
              "folder": opts.get("folder_prezentacji") or os.path.dirname(plik),
              "plik": plik, "slajdy": wszystkie, "ukryte": 0, "nowe": [], "cel": "dokument", "cel_nazwa": "Dokument",
              "suwaki": {"slajdy": n_sl, "rozdzialy": n_rz},
              "czas_s": int(time.time() - t0), "miniatury": thumbs, "qa": qa,
              "uwagi": uwagi_wyniku, "uwagi_pelne": uwagi, "bledy_okno": bledy_okno, "bledy_tekstu": bledy, "oko": oko,
              "pokrycie": cov, "wiernosc": {"usterki": [], "tekst": ""}, "sprawdz": [], "wizualizacje": [], "styl": "nowy",
              "plansze": plansze, "plansze_folder": plansze_folder,
              "prompt_ai": ai_prompt_pptx(os.path.basename(pptx), plik, model, spec, uwagi, cov, qa, pptx, cel="wiernie", dane=dane,
                                          plansze={"folder": plansze_folder, "pliki": plansze}, rodzaj="dokument"),
              "prompt_agent": ai_prompt_agent_pptx(os.path.basename(pptx), plik, pptx, rob, spec, uwagi, cel="wiernie", dane=dane,
                                                   rodzaj="dokument"),
              "raport": os.path.join(rob, "raport.json")}
    json.dump({k: v for k, v in result.items() if k != "miniatury"},
              open(result["raport"], "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("zapis")
    if progress:
        progress("zapis", "Gotowe", 100, 0)
    return result


def _sha256(plik):
    h = hashlib.sha256()
    with open(plik, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def _oko_przeglad(qa, say):
    """„Oko” na zrzutach kopii w trybie dopracowania: tylko OCENA (lista „Sprawdź najpierw: slajd N - …”), bez zmiany układu i bez
    ponownej budowy - program nie przebudowuje prezentacji, która jest już w stylu marki. Zwraca (oko, linie uwag)."""
    oko = {"uruchomione": False, "rundy": 0, "zmienione": [], "odrzucone": [], "pozostale": [], "czas_s": 0}
    if not (qa.get("wykonano") and qa.get("png")):
        return oko, []
    t = time.time()
    try:
        import oko as oko_mod
        ocena = ocena_slajdow(qa, None, oko_mod)
    except Exception as e:  # brak modułu oka nie psuje przeglądu
        _log_file(traceback.format_exc())
        say("Oko programu niedostępne (%s: %s) - pomijam ocenę wyglądu zrzutów." % (type(e).__name__, e))
        return oko, []
    wygladu = sorted(((nr, u) for nr, us in ocena.items() for u in us if u.get("zrodlo") == "oko"),
                     key=lambda x: (-x[1]["waga"], x[0]))
    oko.update(uruchomione=True, czas_s=int(time.time() - t),
               pozostale=[{"slajd": nr, "kod": u["kod"], "waga": u["waga"], "opis": u["opis"]} for nr, u in wygladu])
    linie = ["Sprawdź najpierw: slajd %d - %s" % (nr, u["opis"]) for nr, u in wygladu[:OKO_LINII]]
    if len(wygladu) > OKO_LINII:
        linie.append("…i %d kolejnych usterek wyglądu w raport.json (oko)" % (len(wygladu) - OKO_LINII))
    return oko, linie


def _build_dopracowanie(plik, opts, t0, emit, finish_step, check, say, progress):
    """Dopracowanie pliku JUŻ w stylu marki (szablon DK, wynik programu, prezentacja z szablonu): NIE buduje slajdów i NIE zmienia
    pliku użytkownika. Kroki: przegląd (pptx_convert.przeglad: podpowiedzi w [nawiasach], błędy tekstu) -> zrzuty i kontrola
    PowerPointa na KOPII w katalogu roboczym (bez osadzania czcionek) -> „oko” (sama ocena) -> plansze -> dwa polecenia dla AI.
    Wynik: res["pptx"] = plik użytkownika; res["plik_bez_zmian"] = suma SHA-256 sprzed i po jest ta sama."""
    rob = _pptx_rob(plik)
    rozp = _rozpoznaj(plik)
    try:
        suma0 = _sha256(plik)
    except PermissionError:
        raise ValueError("Plik jest otwarty albo zablokowany przez inny program. Zamknij go (np. w PowerPoint) i spróbuj jeszcze raz.")
    emit("folder", "Czytam prezentację", 0)
    pr = _przeglad(plik, rob)
    bledy = list(pr.get("bledy_tekstu") or [])
    podp = list(pr.get("podpowiedzi") or [])
    say("Prezentacja: %s, slajdów: %d, podpowiedzi w [nawiasach]: %d, możliwe błędy tekstu: %d" % (
        os.path.basename(plik), pr["slajdy"], len(podp), len(bledy)))
    finish_step("folder")
    check()
    kopia = os.path.join(rob, "kopia", os.path.basename(plik))   # render i kontrola idą na kopii; PowerPoint nie dotyka pliku użytkownika
    if len(kopia) > MAX_SCIEZKA_PPT:   # za długa ścieżka: PowerPoint nie otworzy kopii (zrzuty i kontrola by się nie wykonały)
        kopia = os.path.join(rob, "kopia", "kopia.pptx")
        if len(kopia) > MAX_SCIEZKA_PPT:
            kopia = os.path.join(paths.USER_DIR, "kopia", hashlib.sha1(kopia.encode("utf8")).hexdigest()[:10] + ".pptx")
        say("Długa ścieżka folderu - kopię do sprawdzenia zapisuję w: " + kopia)
    os.makedirs(os.path.dirname(kopia), exist_ok=True)
    shutil.copy2(plik, kopia)
    uwagi_pp = []
    qa, thumbs = _render_i_kontrola(kopia, rob, opts, uwagi_pp, emit, say, (0.0, 0.7), osadzaj=False)
    uwagi_pp = [u.replace("stwórz prezentację jeszcze raz", "sprawdź prezentację jeszcze raz") for u in uwagi_pp]
    check()
    emit("qa", "Oglądam zrzuty slajdów", 0.75)
    oko, oko_linie = _oko_przeglad(qa, say)
    emit("qa", "Przygotowuję plansze", 0.9)
    plansze, plansze_folder = _plansze_wyniku(kopia, qa, say, os.path.join(rob, "plansze"))
    finish_step("qa")
    check()
    emit("zapis", "Zapisuję raport", 0.3)
    uwagi = oko_linie + _bez_linii_bledow(pr.get("uwagi") or [], bledy) + uwagi_pp
    bez_zmian = _sha256(plik) == suma0
    if not bez_zmian:
        uwagi.insert(0, "Plik zmienił się w trakcie sprawdzania (ktoś zapisał go w PowerPoint) - zrzuty mogą być nieaktualne. "
                        "Sprawdź prezentację jeszcze raz.")
    nazwa_kopii = _nazwa_kopii(plik)
    uwagi_wyniku, bledy_okno = uwagi_okno(uwagi, bledy, rodzaj="dopracowanie")
    _zapisz_uwagi(rob, uwagi, say)
    result = {"ok": True, "tryb": "dopracowanie", "uwagi_top": _uwagi_top(uwagi_wyniku, bledy, oko), "rodzaj": rozp.get("rodzaj"), "pptx": plik, "nazwa": os.path.basename(plik),
              "folder": os.path.dirname(plik), "folder_pokaz": plansze_folder or rob, "plik": plik,
              "kopia_przegladu": kopia, "slajdy": pr["slajdy"], "ukryte": 0, "nowe": [], "cel": "dopracowanie",
              "cel_nazwa": "Dopracowanie", "podpowiedzi": len(podp), "spec": rozp.get("spec"), "plik_bez_zmian": bez_zmian,
              "czas_s": int(time.time() - t0), "miniatury": thumbs, "qa": qa,
              "uwagi": uwagi_wyniku, "uwagi_pelne": uwagi, "bledy_okno": bledy_okno, "bledy_tekstu": bledy, "oko": oko,
              "pokrycie": {}, "wiernosc": {"usterki": [], "tekst": ""}, "sprawdz": [], "wizualizacje": [], "styl": "nowy",
              "plansze": plansze, "plansze_folder": plansze_folder,
              "prompt_ai": ai_prompt_dopracowanie(plik, rozp, pr, uwagi, bledy, qa, {"folder": plansze_folder, "pliki": plansze}),
              "prompt_agent": ai_prompt_agent_dopracowanie(plik, nazwa_kopii, rob, rozp, uwagi, bledy),
              "raport": os.path.join(rob, "raport.json")}
    with open(result["raport"], "w", encoding="utf8") as fh:
        json.dump({k: v for k, v in result.items() if k != "miniatury"}, fh, ensure_ascii=False, indent=1, default=str)
    finish_step("zapis")
    if progress:
        progress("zapis", "Gotowe", 100, 0)
    return result


# --- folder prezentacji (1.3): wiele plików, propozycja folderu, scenariusz od AI -------------------------------------------
KOMUNIKAT_BEZ_SCENARIUSZA = "Ta wersja programu nie umie jeszcze pracować ze scenariuszem. Zaktualizuj program."
KOMUNIKAT_ZRZUTY_BEZ_AI = ("Zrzuty i zdjęcia czyta czat - użyj »Przygotuj z AI«. Bez AI program zbuduje prezentację z dokumentów "
                           "(.docx, .pdf, .txt…) albo przełoży gotową prezentację (.pptx).")
AI_Q_PARAM = {}   # klucz czatu -> nazwa parametru adresu (np. {"chatgpt": "q"}): wstępnie wpisane polecenie. NIESPRAWDZONE - puste, włączyć po teście
AI_Q_MAX = 1500   # parametr ?q= tylko dla krótkiego polecenia (adres ma limit długości)
POLECENIE_CLAUDE_CODE = "Przeczytaj POLECENIE.md i wykonaj"
SLAJDY_BEZ_DOKUMENTU = {"min": 3, "max": 30, "domyslnie": 8}   # suwak, gdy w folderze nie ma dokumentu (same zrzuty): czat wybiera treść


def scenariusz_modul():
    """Moduł skilla `scenariusz` (importowany dopiero tu: starszy skill go nie ma, a program ma nadal działać)."""
    try:
        import scenariusz
    except ImportError:
        raise ValueError(KOMUNIKAT_BEZ_SCENARIUSZA)
    return scenariusz


def _czytaj_scenariusz(plik):
    with open(plik, encoding="utf-8-sig") as f:
        return f.read()


def _rob_analizy(plik):
    """Jeden wspólny katalog roboczy do SAMEJ analizy plików, które jeszcze nie leżą w folderze prezentacji (obrazy z dokumentów
    nadpisują się nawzajem - analiza ich nie używa): nic obok pliku użytkownika i bez rosnącej liczby katalogów."""
    return os.path.join(paths.USER_DIR, "cache", "analiza-zrodel")


def _suwaki_pakietu(lista):
    """Suwaki z listy `_suwaki_dokumentu` (po jednym na dokument): jeden dokument = jego suwaki; kilka = sumy (dokumenty łączą się w jedną
    prezentację); bez dokumentów (same zrzuty) = zakres stały. Wartości w budowie i tak są przycinane do zakresu połączonego dokumentu."""
    if not lista:
        return {"slajdy": dict(SLAJDY_BEZ_DOKUMENTU), "rozdzialy": {"max": 0, "domyslnie": 0}}
    if len(lista) == 1:
        return lista[0]
    mx_sl = getattr(dokument, "MAX_SLAJDOW", 80)
    mn = min(sum(s["slajdy"]["min"] for s in lista), mx_sl)
    mx = max(mn, min(sum(s["slajdy"]["max"] for s in lista), mx_sl))
    dom = max(mn, min(mx, sum(s["slajdy"]["domyslnie"] for s in lista)))
    rmax = min(8, sum(s["rozdzialy"]["max"] for s in lista))
    rdom = max(0, min(rmax, sum(s["rozdzialy"]["domyslnie"] for s in lista)))
    return {"slajdy": {"min": mn, "max": mx, "domyslnie": dom}, "rozdzialy": {"max": rmax, "domyslnie": rdom}}


def _pola_wspolne(res):
    """Klucze, których ekran opcji oczekuje od każdej analizy (jak w analyze_dokument), puste dla trybów folderu prezentacji."""
    res.update({"sekcje": [], "grupy": [], "cele": [], "smaki": [], "karty": 0, "presety": {"0": [], "1": [], "2": []},
                "domyslne": {"styl": "nowy", "dlugosc": 1, "tekst": 1}, "powerpoint": powerpoint_available()})
    return res


def _czas_slajdow(n):
    c = _czas_dokumentu()
    return int(c["stale"] + c["na_slajd"] * n + c["kw"] * n * n)


def analyze_many(sciezki):
    """Analiza tego, co upuszczono lub wybrano: LISTA ścieżek (plików albo folderów).
    - jeden folder produktu / jedna prezentacja .pptx / plik z folderu produktu / folder z jednym dokumentem-do-przeczytania lub pptx:
      wynik jak `analyze` (dodany klucz "tryb": folder | pptx | dopracowanie | dokument...);
    - jeden folder prezentacji (ma Źródła\\ albo scenariusz*.md): "tryb": "scenariusz" (jest scenariusz) albo "pakiet", "istnieje": True;
    - inne pliki (jeden lub wiele: dokumenty, obrazy, zrzuty, pptx): "tryb": "pakiet", "istnieje": False + propozycja folderu prezentacji
      (baza, nazwa_folderu, folder, m_dostepny). Folder powstaje dopiero w `create_folder` (okno), analiza niczego nie tworzy obok plików."""
    lista, widziane = [], set()
    for p in sciezki or []:
        p = str(p or "").strip().strip('"')
        if p:
            p = os.path.abspath(p)
            if os.path.normcase(p) not in widziane:
                widziane.add(os.path.normcase(p))
                lista.append(p)
    if not lista:
        raise ValueError("Nie wskazano pliku ani folderu.")
    for p in lista:
        if not os.path.exists(p):
            raise ValueError("Nie znalazłem: %s" % p)
    uwagi = []
    if len(lista) == 1:
        p = lista[0]
        if os.path.isdir(p):
            n = normalize_folder(p)   # komunikat po polsku dla folderu programu / pustego / z wieloma plikami
            if os.path.isdir(n) or n.lower().endswith(PPTX_EXT):
                return _z_trybem(analyze(n))
            lista = [n]   # folder z jednym dokumentem = ten dokument
        elif p.lower().endswith(PPTX_EXT) or _ma_karty(os.path.dirname(p)):
            return _z_trybem(analyze(p))
    else:
        for p in [x for x in lista if os.path.isdir(x)]:
            lista.remove(p)
            uwagi.append("Pominąłem folder „%s” - przeciągnij pliki, a nie foldery." % os.path.basename(p))
        if not lista:
            raise ValueError("Przeciągnij pliki (dokumenty, zrzuty ekranu, zdjęcia, prezentacje) albo jeden folder.")
    return analyze_pakiet(lista, uwagi)


def _z_trybem(res):
    res.setdefault("tryb", "folder")
    return res


def analyze_pakiet(lista, uwagi=None):
    """Pliki do nowej prezentacji (jeszcze bez folderu): lista plików, tytuł, suwaki i propozycja folderu."""
    uwagi = list(uwagi or [])
    dok = dok_ext()
    pliki = [folder_prez.opis_pliku(p, dok) for p in lista]
    modele, suwaki, slowa = [], [], 0
    for x in pliki:
        if x["typ"] != "dokument":
            continue
        try:
            m = _dok_model(x["sciezka"], _rob_analizy(x["sciezka"]))
        except ValueError as e:   # skan, pusty plik, za długi: czat może go przeczytać z załącznika, więc nie blokujemy
            x["problem"] = str(e)
            uwagi.append("%s: %s" % (x["nazwa"], e))
            continue
        st = dokument.statystyka(m)
        modele.append(m)
        suwaki.append(_suwaki_dokumentu(st))
        slowa += int(st.get("slowa") or 0)
    for x in pliki:
        if x["typ"] == "inny":
            uwagi.append("„%s” trafi do folderu ze źródłami, ale program nie umie go przeczytać - dołącz go w czacie." % x["nazwa"])
    tytul = (modele[0].get("tytul") if modele else "") or os.path.splitext(pliki[0]["nazwa"])[0]
    tytul = " ".join(str(tytul).replace("_", " ").split())
    baza, m_ok = folder_prez.baza_domyslna()
    if not m_ok and baza == folder_prez.dokumenty_baza() and not platforma.mac():   # na Macu nie ma dysku M: - nie ma o czym ostrzegać
        uwagi.append("Dysk M: z folderem prezentacji firmy jest teraz niedostępny - proponuję folder w Dokumentach.")
    folder = folder_prez.unikalna_sciezka(baza, folder_prez.nazwa_folderu(tytul))
    sw = _suwaki_pakietu(suwaki)
    est = _czas_slajdow(sw["slajdy"]["domyslnie"])
    return _pola_wspolne({
        "ok": True, "tryb": "pakiet", "istnieje": False, "pliki": pliki, "tytul": tytul, "produkt": tytul, "baza": baza,
        "nazwa_folderu": os.path.basename(folder), "folder": folder, "m_dostepny": m_ok, "uwagi": uwagi,
        "slowa": slowa, "suwaki": sw, "czas": _czas_dokumentu(),
        "szacowany_czas_s": est})


def analyze_folder_prez(folder):
    """Folder prezentacji (ma Źródła\\ albo scenariusz*.md): pliki ze Źródeł, najnowszy scenariusz (z kontrolą), poprzednie wyniki."""
    folder = os.path.abspath(folder)
    pliki = [folder_prez.opis_pliku(p, dok_ext()) for p in folder_prez.pliki_zrodel(folder)]
    sc, nr = folder_prez.najnowszy_scenariusz(folder)
    try:
        wyniki = sorted((n for n in os.listdir(folder) if n.lower().endswith(".pptx") and not n.startswith("~$")),
                        key=lambda n: -os.path.getmtime(os.path.join(folder, n)))
    except OSError:
        wyniki = []
    uwagi = []
    res = {"ok": True, "istnieje": True, "folder": folder, "nazwa_folderu": os.path.basename(folder), "baza": os.path.dirname(folder),
           "m_dostepny": folder_prez.zapisywalny(folder_prez.baza_m()), "pliki": pliki, "wyniki": wyniki, "uwagi": uwagi,
           "tytul": folder_prez.tytul_z_folderu(folder), "produkt": folder_prez.tytul_z_folderu(folder), "czas": _czas_dokumentu()}
    if sc:
        md = _czytaj_scenariusz(sc)
        k = scenariusz_modul().sprawdz(md, folder, None)
        res.update(tryb="scenariusz", scenariusz=sc, scenariusz_nazwa=os.path.basename(sc), scenariusz_wersja=nr,
                   tytul=k.get("tytul") or res["tytul"], produkt=k.get("tytul") or res["produkt"], slajdy=k["slajdy"],
                   rozdzialy=k["rozdzialy"], scenariusz_ok=k["ok"], scenariusz_bledy=k["bledy"], scenariusz_uwagi=k["uwagi"],
                   szacowany_czas_s=_czas_slajdow(k["slajdy"]))
        uwagi += ["Scenariusz: " + b for b in k["bledy"]]
        res["suwaki"] = {"slajdy": {"min": 1, "max": max(k["slajdy"], 1), "domyslnie": max(k["slajdy"], 1)}, "rozdzialy": {"max": 0, "domyslnie": 0}}
    else:
        suwaki = []
        for x in pliki:
            if x["typ"] == "dokument":
                try:
                    suwaki.append(_suwaki_dokumentu(dokument.statystyka(_dok_model(x["sciezka"]))))
                except ValueError as e:
                    x["problem"] = str(e)
                    uwagi.append("%s: %s" % (x["nazwa"], e))
        sw = _suwaki_pakietu(suwaki)
        res.update(tryb="pakiet", suwaki=sw, szacowany_czas_s=_czas_slajdow(sw["slajdy"]["domyslnie"]))
    return _pola_wspolne(res)


# --- źródła w folderze prezentacji -> tekst dla AI i dla budowy bez AI --------------------------------------------------
def _model_na_md(model, przesuniecie=0, kopiuj_obraz=None, bez_tytulu=False, obraz_tekst="[obraz w dokumencie]"):
    """Model dokumentu (bloki) -> Markdown: nagłówki #, listy, tabele GFM, cytaty. przesuniecie = o ile poziomów nagłówki schodzą niżej
    (max ###). kopiuj_obraz(ścieżka) -> ścieżka względna w .md albo None (obraz pomijany); bez niego obraz to linia `obraz_tekst`."""
    L, poprzedni_li = [], False
    pomin = model.get("tytul_idx") if bez_tytulu else None
    for i, b in enumerate(model.get("bloki", [])):
        if i == pomin:
            continue
        typ = b.get("typ", "p")
        t = " ".join(str(b.get("t") or "").split())
        if typ in ("h1", "h2", "h3"):
            wiersz = "%s %s" % ("#" * min(3, int(typ[1]) + przesuniecie), t)
        elif typ == "li":
            wiersz = ("1. " if b.get("num") else "- ") + t
        elif typ == "cytat":
            wiersz = "> " + t
        elif typ == "tabela":
            w = b.get("wiersze") or []
            if not w:
                continue
            kol = max(len(r) for r in w)
            tab = ["| " + " | ".join(" ".join(str(c).replace("|", "/").split()) for c in list(r) + [""] * (kol - len(r))) + " |" for r in w]
            tab.insert(1, "|" + "---|" * kol)
            wiersz = "\n".join(tab)
        elif typ == "obraz":
            rel = kopiuj_obraz(b.get("obraz")) if kopiuj_obraz else obraz_tekst
            if not rel:
                continue
            wiersz = "![](%s)" % rel if kopiuj_obraz else rel
        else:
            wiersz = t
        if not wiersz.strip():
            continue
        L.append((("\n" if typ == "li" and poprzedni_li else "\n\n") if L else "") + wiersz)
        poprzedni_li = typ == "li"
    return "".join(L)


def zrodla_folderu(folder):
    """Co jest w <folder>\\Źródła dla AI: {"dokumenty": [{"plik", "tekst"}], "do_zalaczenia": [nazwy], "uwagi": [str]}.
    "suwaki" = zakresy suwaka slajdów po jednym na dokument. Dokumenty i prezentacje -> tekst (Markdown). Obrazy, zrzuty, PDF-y (oryginał ma rysunki), pliki nieczytelne i inne typy
    -> `do_zalaczenia` (użytkownik przeciąga je do czatu)."""
    dok, wyn, zalacz, uwagi, suwaki = dok_ext(), [], [], [], []
    for p in folder_prez.pliki_zrodel(folder):
        nazwa, typ = os.path.basename(p), folder_prez.typ_pliku(p, dok)
        if typ == "dokument":
            try:
                m = _dok_model(p)
                wyn.append({"plik": nazwa, "tekst": _model_na_md(m)})
                suwaki.append(_suwaki_dokumentu(dokument.statystyka(m)))
                if p.lower().endswith(".pdf"):
                    zalacz.append(nazwa)
            except ValueError as e:
                uwagi.append("%s: %s" % (nazwa, e))
                zalacz.append(nazwa)
        elif typ == "pptx":
            try:
                wyn.append({"plik": nazwa, "tekst": _source_dump(_pptx_model(p), limit=10 ** 6)})
            except Exception as e:   # uszkodzona / chroniona prezentacja: czat dostanie ją jako załącznik
                _log_file(traceback.format_exc())
                uwagi.append("Nie przeczytałem prezentacji „%s” (%s) - dołącz ją w czacie." % (nazwa, type(e).__name__))
                zalacz.append(nazwa)
        else:
            zalacz.append(nazwa)
    return {"dokumenty": wyn, "do_zalaczenia": zalacz, "uwagi": uwagi, "suwaki": suwaki}


def polecenie_przygotowania_ai(folder, slajdy=None):
    """Polecenie dla czatu: źródła z folderu -> scenariusz. Zwraca {"tekst", "do_zalaczenia", "uwagi", "katalog" (Źródła), "slajdy"}."""
    S = scenariusz_modul()
    z = zrodla_folderu(folder)
    try:
        n = int(slajdy or 0)
    except (TypeError, ValueError):
        n = 0
    if n <= 0:
        n = _suwaki_pakietu(z["suwaki"])["slajdy"]["domyslnie"]
    tekst = S.polecenie_przygotowania(z["dokumenty"], z["do_zalaczenia"], n, folder_prez.tytul_z_folderu(folder), folder)
    return {"tekst": tekst, "do_zalaczenia": z["do_zalaczenia"], "uwagi": z["uwagi"], "katalog": os.path.join(folder, folder_prez.ZRODLA),
            "slajdy": n}


def polecenie_poprawki_ai(folder, slajdy=None):
    """Polecenie dla czatu: popraw najnowszy scenariusz po budowie (uwagi i plansze z ostatniego raportu). None, gdy nie ma scenariusza."""
    S = scenariusz_modul()
    sc, _nr = folder_prez.najnowszy_scenariusz(folder)
    if not sc:
        return None
    md = _czytaj_scenariusz(sc)
    raport = {}
    try:
        with open(os.path.join(folder, "_robocze", "raport.json"), encoding="utf8") as f:
            raport = json.load(f)
    except (OSError, ValueError):
        pass
    uwagi = _uwagi_dla_ai(raport.get("uwagi_pelne") or raport.get("uwagi") or [], raport.get("bledy_tekstu") or [])
    plansze_folder = raport.get("plansze_folder") or os.path.join(folder, "plansze")
    plansze = [os.path.basename(p) for p in raport.get("plansze") or [] if os.path.isfile(p)]
    try:
        n = int(slajdy or 0) or S.sprawdz(md, folder, None)["slajdy"]
    except (TypeError, ValueError):
        n = S.sprawdz(md, folder, None)["slajdy"]
    tekst = S.polecenie_poprawki(md, uwagi, plansze, n, plansze_folder if plansze else "")
    return {"tekst": tekst, "do_zalaczenia": plansze, "uwagi": [], "katalog": plansze_folder if plansze else os.path.dirname(sc),
            "slajdy": n}


def zapisz_polecenie(folder):
    """POLECENIE.md w folderze prezentacji (dla Claude Code i innych agentów z plikami). Błąd zapisu nie przerywa pracy: zwraca ścieżkę albo None."""
    try:
        tekst = scenariusz_modul().polecenie_agenta(folder)
        p = os.path.join(folder, "POLECENIE.md")
        with open(p, "w", encoding="utf8", newline="\n") as f:
            f.write(tekst.rstrip() + "\n")
        return p
    except (ValueError, OSError):
        _log_file(traceback.format_exc())
        return None


def zapisz_scenariusz(folder, tekst, limit=None):
    """Odpowiedź czatu (cała wklejka) -> walidacja -> nowa wersja scenariusza w folderze prezentacji.
    {"ok", "plik", "wersja", "slajdy", "uwagi", "blad"}; przy błędach scenariusza nic nie zapisuje."""
    S = scenariusz_modul()
    md = S.wyciagnij(tekst)
    if md is None:
        return {"ok": False, "plik": None, "wersja": 0, "slajdy": 0, "uwagi": [],
                "blad": "To nie wygląda na scenariusz - brakuje linii „# SCENARIUSZ DK”. Wklej całą odpowiedź czatu."}
    k = S.sprawdz(md, folder, limit)
    if not k["ok"]:
        return {"ok": False, "plik": None, "wersja": 0, "slajdy": k["slajdy"], "uwagi": k["uwagi"],
                "blad": "Scenariusza nie da się zbudować: " + " ".join(k["bledy"][:3]) + " Popraw odpowiedź w czacie i wklej ją jeszcze raz."}
    try:
        lim = int(limit or 0)
    except (TypeError, ValueError):
        lim = 0
    if lim and k["slajdy"] > lim:   # suwak ma działać w programie, nie tylko w poleceniu: nic nie ucinamy po cichu
        return {"ok": False, "plik": None, "wersja": 0, "slajdy": k["slajdy"], "uwagi": k["uwagi"],
                "blad": "Scenariusz ma %d slajdów, a ustawiłeś najwyżej %d. Napisz w czacie: „Skróć scenariusz do %d slajdów, zostaw "
                        "najważniejsze, ten sam format.” i wklej nową odpowiedź (albo przesuń suwak)." % (k["slajdy"], lim, lim)}
    plik, nr = folder_prez.nowa_wersja_scenariusza(folder, md)
    return {"ok": True, "plik": plik, "wersja": nr, "slajdy": k["slajdy"], "rozdzialy": k["rozdzialy"], "tytul": k["tytul"],
            "uwagi": k["uwagi"], "blad": "", "szacowany_czas_s": _czas_slajdow(k["slajdy"])}


# --- czaty AI -----------------------------------------------------------------------------------------------------------
def ai_cele():
    """[{"id", "nazwa", "dostepny"}]: Claude, ChatGPT, Gemini oraz (gdy `claude` jest w PATH) Claude Code. Każdy ma też "ostatni"
    (True dla zapamiętanego wyboru; bez zapamiętanego - dla pierwszego)."""
    cele = [{"id": k, "nazwa": v[0], "dostepny": True} for k, v in AI_CHATS.items()]
    if claude_protokol():   # aplikacja Claude Desktop: sesja Cowork z dostępem do folderu prezentacji
        cele.insert(1, {"id": "claude_cowork", "nazwa": "Claude Cowork (z folderem)", "dostepny": True})
    if platforma.znajdz_claude() or claude_protokol():
        cele.append({"id": "claude_code", "nazwa": "Claude Code", "dostepny": True})
    ost = folder_prez.ustawienia().get("ostatni_ai")
    ost = ost if ost in {c["id"] for c in cele} else cele[0]["id"]
    for c in cele:
        c["ostatni"] = c["id"] == ost
    return cele


def adres_czatu(ktory, url, tekst):
    """Adres czatu; z wpisanym poleceniem tylko dla czatu z AI_Q_PARAM i krótkiego polecenia (domyślnie: pusty słownik = nigdy)."""
    par = AI_Q_PARAM.get(ktory)
    if par and tekst and len(tekst) <= AI_Q_MAX:
        import urllib.parse
        return "%s?%s=%s" % (url, par, urllib.parse.quote(tekst))
    return url


def claude_protokol():
    """True, gdy system zna schemat claude:// (Windows: wpis w rejestrze; macOS: jest Claude.app) - zainstalowana aplikacja Claude Desktop."""
    return platforma.schemat_claude()


def adres_claude(rodzaj, polecenie, folder=None):
    """Link aplikacji Claude Desktop: rodzaj "chat" | "cowork" | "code". Polecenie jest wpisywane w nowej rozmowie (użytkownik
    wysyła je sam), folder wymaga zgody użytkownika w aplikacji. Format według dokumentacji Anthropic (30.06.2026, przekazane
    przez GPT 27.10.2026; niesprawdzone na tym komputerze - w razie błędu polecenie zostaje w schowku)."""
    import urllib.parse
    q = urllib.parse.quote(polecenie or "", safe="")
    if rodzaj == "chat":
        return "claude://claude.ai/new?q=" + q
    return "claude://%s/new?q=%s&folder=%s" % (rodzaj, q, urllib.parse.quote(folder or "", safe=""))


def uruchom_claude_code(folder, polecenie=POLECENIE_CLAUDE_CODE):
    """Nowe okno terminala w folderze prezentacji z `claude` i krótkim poleceniem (Windows: wt albo konsola, macOS: Terminal.app przez
    osascript - szczegóły w platforma.py). False, gdy `claude` nie jest zainstalowany."""
    return platforma.uruchom_claude_code(folder, polecenie)


# --- budowa: folder prezentacji ---------------------------------------------------------------------------------------
def _polacz_zrodla(folder, pliki, tytul):
    """Kilka dokumentów ze Źródeł -> jeden plik Markdown <folder>\\_robocze\\zrodla-polaczone.md (kolejność nazw plików): tytuł
    prezentacji, każdy dokument jako rozdział (##), jego nagłówki poziom niżej. Obrazy kopiowane do _robocze\\obrazy-zrodel."""
    rob = os.path.join(folder, "_robocze")
    os.makedirs(rob, exist_ok=True)
    obr_dir, n = os.path.join(rob, "obrazy-zrodel"), [0]

    def kopiuj(src):
        if not src or not os.path.isfile(src):
            return None
        os.makedirs(obr_dir, exist_ok=True)
        n[0] += 1
        nazwa = "z%02d_%s" % (n[0], re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(src)))
        shutil.copy2(src, os.path.join(obr_dir, nazwa))
        return "obrazy-zrodel/" + nazwa

    czesci = ["# " + tytul]
    for p in pliki:
        m = _dok_model(p)
        czesci.append("## %s\n\n%s" % (m.get("tytul") or os.path.splitext(os.path.basename(p))[0], _model_na_md(m, 2, kopiuj, True)))
    plik = os.path.join(rob, "zrodla-polaczone.md")
    with open(plik, "w", encoding="utf8", newline="\n") as f:
        f.write("\n\n".join(czesci) + "\n")
    return plik


def _build_pakiet(folder, opts, t0, emit, finish_step, check, say, progress):
    """Folder prezentacji bez scenariusza, budowa BEZ AI: jeden dokument ze Źródeł = jak `_build_dokument`; kilka = połączone w
    kolejności nazw w jeden dokument. Zrzuty, zdjęcia i prezentacje bez AI są pomijane (czyta je czat). Wynik i _robocze: w folderze prezentacji."""
    if dokument is None:
        raise ValueError(KOMUNIKAT_BEZ_DOKUMENTOW)
    dok = dok_ext()
    zrodla = folder_prez.pliki_zrodel(folder)
    dokumenty = [p for p in zrodla if folder_prez.typ_pliku(p, dok) == "dokument"]
    if not dokumenty:
        raise ValueError(KOMUNIKAT_ZRZUTY_BEZ_AI)
    pominiete = [os.path.basename(p) for p in zrodla if p not in dokumenty]
    wstep = []
    if pominiete:
        wstep.append("Bez AI program nie czyta tych plików: %s - czyta je czat (»Przygotuj z AI«)." % ", ".join(pominiete[:6]) +
                     (" i %d innych" % (len(pominiete) - 6) if len(pominiete) > 6 else ""))
    tytul = folder_prez.tytul_z_folderu(folder)
    if len(dokumenty) == 1:
        plik = dokumenty[0]
    else:
        plik = _polacz_zrodla(folder, dokumenty, tytul)
        wstep.insert(0, "Połączyłem %d dokumentów w kolejności nazw plików; każdy jest teraz rozdziałem prezentacji." % len(dokumenty))
    opts = dict(opts, wyjscie=folder, wyjscie_plik=folder_prez.nazwa_wyniku(folder, tytul), folder_prezentacji=folder, uwagi_wstep=wstep)
    wynik = _build_dokument(plik, opts, t0, emit, finish_step, check, say, progress)
    wynik.update(wejscie="pakiet", zrodla=[os.path.basename(p) for p in zrodla], folder=folder)
    zapisz_polecenie(folder)
    return wynik


def _build_scenariusz(folder, opts, t0, emit, finish_step, check, say, progress):
    """Budowa 1:1 z najnowszego scenariusza w folderze prezentacji (albo z pliku opts["scenariusz"]): `##` = jeden slajd. Dalej ta sama
    ścieżka jakości co dokument: zrzuty, kontrola tekstu w PowerPoint, „oko”, pokrycie treści, plansze. Wynik: <nazwa>.pptx, <nazwa> v2.pptx…
    w folderze prezentacji (poprzednie zostają), _robocze obok."""
    S = scenariusz_modul()
    if dokument is None:
        raise ValueError(KOMUNIKAT_BEZ_DOKUMENTOW)
    rob = os.path.join(folder, "_robocze")
    os.makedirs(rob, exist_ok=True)
    wsk = opts.get("scenariusz")   # okno podaje True („z najnowszego”), CLI - ścieżkę pliku
    sc, nr = (wsk, 0) if isinstance(wsk, str) and wsk else folder_prez.najnowszy_scenariusz(folder)
    if not sc or not os.path.isfile(sc):
        raise ValueError("W folderze nie ma scenariusza (scenariusz.md). Wklej odpowiedź czatu albo zbuduj prezentację bez AI.")
    emit("folder", "Czytam scenariusz", 0)
    md = _czytaj_scenariusz(sc)
    try:
        limit = int(opts.get("slajdy") or 0) or None
    except (TypeError, ValueError):
        limit = None
    k = S.sprawdz(md, folder, limit)
    if not k["ok"]:
        raise ValueError("Scenariusza nie da się zbudować: " + " ".join(k["bledy"][:3]))
    say("Scenariusz: %s, slajdów z treścią: %d, przekładek: %d" % (os.path.basename(sc), k["slajdy"], k["rozdzialy"]))
    stem = folder_prez.oczysc_tytul(k["tytul"] or folder_prez.tytul_z_folderu(folder), 100)
    finish_step("folder")
    check()
    emit("grafiki", "Przygotowuję obrazy", 0.5)
    finish_step("grafiki")
    check()
    emit("slajdy", "Układam slajdy", 0.3)
    spec = _z_postepem(lambda: S.zloz(md, {"wyjscie": folder, "folder": folder, "nazwa": stem, "limit": limit}),
                       emit, check, "slajdy", "Układam slajdy", 1.6 * k["slajdy"])
    spec["output"] = folder_prez.nazwa_wyniku(folder, stem)
    uwagi = list(spec.get("uwagi", []))
    spec["uwagi"] = []   # dokument.popraw_po_renderze dopisuje tu wpis o zmianie układu; własną linię z oka składa silnik
    _wyjscie_krotkie(spec, uwagi, say)
    os.makedirs(os.path.dirname(spec["output"]), exist_ok=True)
    spec_json = os.path.join(rob, "spec_program.json")
    json.dump(spec, open(spec_json, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    finish_step("slajdy")
    check()
    j = _jakosc(spec, rob, opts, uwagi, emit, finish_step, check, say, spec_json, dok=True)
    pptx, qa, thumbs, spec, oko, oko_linie = j["pptx"], j["qa"], j["thumbs"], j["spec"], j["oko"], j["oko_linie"]
    spec.pop("uwagi", None)
    emit("zapis", "Sprawdzam, czy nic nie zginęło", 0.3)
    cov = dokument.pokrycie(S.model(md, folder), pptx, spec.get("mapa_blokow"))
    say(cov.get("tekst", ""))
    for m in (cov.get("brakuje") or [])[:10]:
        uwagi.append("Brakuje: %s" % (m if isinstance(m, str) else (m.get("tekst") or str(m))))
    uwagi[0:0] = oko_linie
    uwagi.insert(0, cov.get("tekst", ""))
    plansze, plansze_folder = _plansze_wyniku(pptx, qa, say)
    emit("zapis", "Zapisuję raport", 0.6)
    wszystkie = len(spec["slides"])
    bledy = spec.get("bledy_tekstu") or []
    uwagi_wyniku, bledy_okno = uwagi_okno(uwagi, bledy, rodzaj="dokument")
    _zapisz_uwagi(rob, uwagi, say)
    result = {"ok": True, "tryb": "scenariusz", "uwagi_top": _uwagi_top(uwagi_wyniku, bledy, oko), "pptx": pptx,
              "nazwa": os.path.basename(pptx), "folder": folder, "plik": sc, "scenariusz": sc,
              "scenariusz_wersja": nr or folder_prez.najnowszy_scenariusz(folder)[1], "slajdy": wszystkie, "ukryte": 0, "nowe": [],
              "cel": "scenariusz", "cel_nazwa": "Scenariusz", "suwaki": {"slajdy": k["slajdy"], "rozdzialy": k["rozdzialy"]},
              "czas_s": int(time.time() - t0), "miniatury": thumbs, "qa": qa, "uwagi": uwagi_wyniku, "uwagi_pelne": uwagi,
              "bledy_okno": bledy_okno, "bledy_tekstu": bledy, "oko": oko, "pokrycie": cov, "wiernosc": {"usterki": [], "tekst": ""},
              "sprawdz": [], "wizualizacje": [], "styl": "nowy", "plansze": plansze, "plansze_folder": plansze_folder,
              "raport": os.path.join(rob, "raport.json")}
    result["prompt_ai"] = S.polecenie_poprawki(md, _uwagi_dla_ai(uwagi, bledy), [os.path.basename(p) for p in plansze],
                                               limit or k["slajdy"], plansze_folder or "")
    result["prompt_agent"] = S.polecenie_agenta(folder)
    json.dump({kk: v for kk, v in result.items() if kk != "miniatury"}, open(result["raport"], "w", encoding="utf8"),
              ensure_ascii=False, indent=1)
    zapisz_polecenie(folder)
    finish_step("zapis")
    if progress:
        progress("zapis", "Gotowe", 100, 0)
    return result


# Komunikat w oknie nie może mieć surowego wyjątku: nazwy klasy, „WinError”, „Errno”, śladu stosu ani podwójnych ukośników
# (repr ścieżki w tekście wyjątku). Nasze własne komunikaty (ValueError po polsku) przechodzą bez zmian, reszta dostaje zdanie
# domyślne; szczegóły techniczne zostają w logu programu i w „Pokaż szczegóły”.
_SUROWY = re.compile(r"WinError|Traceback|Errno|Error\b|Exception|\\\\|File \"|0x[0-9A-Fa-f]{4,}|<[^>]+object at")
BLAD_TWORZENIA = ("Nie udało się stworzyć prezentacji. Spróbuj jeszcze raz; jeśli to się powtórzy, szczegóły są pod "
                  "„Pokaż szczegóły”.")
BLAD_PLIKU = ("Nie udało się przeczytać tego pliku ani folderu. Sprawdź, czy istnieje i czy masz do niego dostęp, "
              "i spróbuj jeszcze raz.")


def komunikat_bledu(e, domyslny=BLAD_PLIKU):
    """Tekst błędu dla człowieka: własny komunikat programu (ValueError po polsku bez śladów surowego wyjątku) albo `domyslny`."""
    t = " ".join(str(e).split())
    if isinstance(e, ValueError) and t and not _SUROWY.search(t):
        return t
    return domyslny


def safe_build(*a, **kw):
    try:
        return build(*a, **kw)
    except Cancelled:
        return {"ok": False, "blad": "Przerwano.", "przerwano": True}
    except Exception as e:
        tb = traceback.format_exc()
        _log_file(tb)
        return {"ok": False, "blad": komunikat_bledu(e, BLAD_TWORZENIA), "traceback": tb}
