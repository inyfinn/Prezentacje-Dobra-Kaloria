# -*- coding: utf-8 -*-
"""scenariusz.py - prezentacja marki Dobra Kaloria ze SCENARIUSZA Markdown (27.10.2026). Czyste funkcje, bez okna.

AI (czat albo agent) pisze scenariusz według wzoru (`assets/scenariusz-wzor.md`), program buduje z niego PPTX 1:1: jeden nagłówek
`##` = DOKŁADNIE jeden slajd treści (bez przepakowywania i dzielenia jak w dokument.py), plus okładka (z `tytuł:` i `podtytuł:`)
i zakończenie. `## Rozdział: X` = przekładka. Hasło (`##`) jest tytułem slajdu (Mindset), pod nim dopisek (Lato), punkty,
liczba-bohater, tabela, obrazy albo cytat.

    import scenariusz
    scenariusz.MARKER                                 # "# SCENARIUSZ DK"
    scenariusz.wzor()                                 # treść scenariusz-wzor.md
    md   = scenariusz.wyciagnij(wklejka)              # scenariusz z odpowiedzi czatu (bez płotków ```), None gdy brak markera
    wyn  = scenariusz.sprawdz(md, folder=None, limit=None)   # {"ok","slajdy","rozdzialy","tytul","uwagi","bledy"}
    spec = scenariusz.zloz(md, {"wyjscie": k, "folder": baza_obrazow, "nazwa": "plik", "limit": N})   # spec dla build_dk.build
    scenariusz.model(md, folder)                      # model w formacie dokument.py (dla dokument.pokrycie(m, pptx, spec["mapa_blokow"]))
    scenariusz.polecenie_przygotowania(zrodla, obrazy, slajdy, tytul, folder)   # polecenie dla czatu: źródła -> scenariusz
    scenariusz.polecenie_poprawki(md, uwagi, plansze, slajdy, folder)           # polecenie dla czatu: popraw scenariusz po budowie
    scenariusz.polecenie_agenta(folder)                                          # POLECENIE.md dla Claude Code / agenta

`sprawdz`: błędy = nie da się zbudować (zloz rzuca wtedy ValueError po polsku), uwagi = da się, ale warto poprawić.
Układ slajdu: klocki z dokument.py (`_wiersze_lista`, `_slajd_cytatu`...) i build_dk (`uklad`, `table`, `pics`, `statement`).
"""
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
WZOR_PLIK = os.path.join(HERE, "..", "assets", "scenariusz-wzor.md")

MARKER = "# SCENARIUSZ DK"
HASLO_SLOW = 10          # hasło dłuższe: uwaga (zalecane do 8)
DOPISEK_SLOW = 30        # dopisek dłuższy: uwaga (zalecany do 25)
PUNKTY_ZALECANE = 4      # więcej punktów: uwaga
PUNKTY_MAX = 8           # tyle punktów mieści jeden slajd (dokument.LISTA_MAX); więcej: błąd
LICZBY_MAX = 4           # liczb-bohaterów obok siebie
OBRAZY_MAX = 6           # obrazów na slajdzie (build_dk `pics`)
TABELA_WIERSZE, TABELA_KOLUMNY = 8, 6   # wiersze danych i kolumny tabeli na jednym slajdzie (dokument.TABELA_*)
SLAJDOW_MAX = 80
COVER_DLUGI = 44         # tytuł dłuższy: okładka z jednym zdaniem na środku (dokument.COVER_DLUGI)
PODTYTUL_SLOW = 25       # dłuższy podtytuł nie mieści się na okładce w całości (dokument skraca go i zostawia całość w notatkach)
ZRODLA_ZNAKI = 35000     # tyle znaków tekstu źródeł w poleceniu dla czatu
SOURCE_ZNAKI = 110       # dopisek przy tabeli (stopka slajdu, jedna linia)


def _dok():
    import dokument
    return dokument


def _slow(t):
    return len(t.split())


# =====================================================================================================================
# 1. WZÓR I WYCIĄGANIE Z WKLEJKI
# =====================================================================================================================
def wzor():
    """Treść `assets/scenariusz-wzor.md` (przykład 6 slajdów treści i 2 przekładek: pokazuje każdy element)."""
    with open(WZOR_PLIK, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


# Szkielet pokazuje WYŁĄCZNIE format: nawiasy <…> to miejsca na treść z materiałów. Nie zawiera żadnej treści, którą dałoby się przepisać
# (27.10.2026: czat przepisał do prezentacji przykład „Baton Przykład” z poprzedniego polecenia zamiast materiałów użytkownika).
SZKIELET = (
    "# SCENARIUSZ DK\n"
    "tytuł: <tytuł z materiałów>\n"
    "podtytuł: <jedno zdanie z materiałów, opcjonalnie>\n"
    "\n"
    "## Rozdział: <nazwa rozdziału>\n"
    "\n"
    "## <hasło slajdu>\n"
    "<jedno zdanie dopisku>\n"
    "\n"
    "## <hasło slajdu>\n"
    "- <punkt>\n"
    "- <punkt>\n"
    "\n"
    "## <hasło slajdu>\n"
    "**<liczba z materiałów>** <krótki opis liczby>\n"
    "\n"
    "## <hasło slajdu>\n"
    "| <kolumna> | <kolumna> |\n"
    "|---|---|\n"
    "| <komórka> | <komórka> |\n"
    "\n"
    "## <hasło slajdu>\n"
    "![<podpis>](Źródła/<nazwa pliku z listy>)\n"
    "\n"
    "## <hasło slajdu>\n"
    "> <cytat z materiałów> — <autor>\n")
SZKIELET_OPIS = ("SZKIELET (to tylko FORMAT, nie przykład: nawiasy <…> zastąp treścią Z MATERIAŁÓW; nie przepisuj żadnego słowa z tego szkieletu, "
                 "a nawiasów <…> nie zostawiaj):")
_ZNAKI_AWARYJNE = ("baton przykład", "baton-przyklad", "anna przykładowa")    # gdy nie da się przeczytać wzoru
_RX_PUSTE = re.compile(r"<\s*(?:tytuł|podtytuł|nazwa rozdziału|hasło|jedno zdanie|punkt|liczba|krótki opis|kolumna|komórka|podpis|nazwa pliku|cytat|autor)"
                       r"[^>\n]*>", re.I)
BLAD_PRZYKLAD = "Czat przepisał przykład zamiast Twoich materiałów – poproś go o scenariusz z plików w folderze Źródła."
BLAD_SZKIELET = "Czat zostawił puste miejsca ze szkieletu zamiast treści z Twoich materiałów – poproś go o scenariusz z plików w folderze Źródła."


def znaki_przykladu():
    """Nazwy własne z `wzor()` (małe litery): tytuł (cały i część przed pierwszą półpauzą), nazwy plików obrazów bez rozszerzenia, autor cytatu.
    Brane z aktualnego wzoru, więc po jego zmianie wykrywanie przepisanego przykładu idzie za nim. Krótsze niż 6 znaków pomijam."""
    try:
        w = wzor()
    except OSError:
        return _ZNAKI_AWARYJNE
    z = set()
    m = re.search(r"^\s*tytu[łl]\s*:\s*(.+)$", w, re.I | re.M)
    if m:
        t = m.group(1).strip()
        z |= {t, re.split(r"\s[–—-]\s", t)[0]}
    z |= {os.path.splitext(os.path.basename(urllib.parse.unquote(p)))[0] for p in re.findall(r"!\[[^\]]*\]\(\s*<?([^)>]+?)>?\s*\)", w)}
    z |= set(re.findall(r"^>.*\s[—–-]\s+([^,\n]+)", w, re.M))
    z = {x.strip().lower() for x in z}
    return tuple(sorted(x for x in z if len(x) >= 6)) or _ZNAKI_AWARYJNE

_RX_MARKER = re.compile(r"^\s*#\s*SCENARIUSZ\s+DK\s*$", re.I)
_RX_PLOTEK = re.compile(r"^\s*```")


def wyciagnij(tekst):
    """Scenariusz z dowolnej wklejki (np. cała odpowiedź czatu): od OSTATNIEJ linii `# SCENARIUSZ DK` (czat bywa, że powtarza wzór
    z polecenia) do końca albo do pierwszego płotka ``` po niej. None, gdy w tekście nie ma markera."""
    linie = (tekst or "").replace("\r\n", "\n").replace("\r", "\n").replace("﻿", "").split("\n")
    idx = [i for i, l in enumerate(linie) if _RX_MARKER.match(l)]
    if not idx:
        return None
    reszta = linie[idx[-1]:]
    for i, l in enumerate(reszta[1:], 1):
        if _RX_PLOTEK.match(l):
            reszta = reszta[:i]
            break
    reszta[0] = MARKER
    return "\n".join(l.rstrip() for l in reszta).strip() + "\n"


# =====================================================================================================================
# 2. PARSER: scenariusz -> model (format dokument.py) + slajdy
# =====================================================================================================================
_RX_H2 = re.compile(r"^##(?!#)\s*(.*)$")
_RX_ROZ = re.compile(r"^rozdzia[łl]\s*:\s*(.*)$", re.I)
_RX_POLE = re.compile(r"^\**\s*(podtytu[łl]|tytu[łl])\s*:\s*\**\s*(.*)$", re.I)
_RX_LI = re.compile(r"^[-*+•]\s+(.*)$")
_RX_NUM = re.compile(r"^\d{1,3}[.)]\s+(.*)$")
_RX_OBR = re.compile(r"^!\[(?P<p>[^\]]*)\]\(\s*<?(?P<s>[^)>]+?)>?\s*(?:\"[^\"]*\")?\)$")
_RX_LICZBA = re.compile(r"^\*\*(?P<l>[^*]{1,16})\*\*\s*(?P<o>.*)$")
_RX_AUTOR = re.compile(r"^(?P<q>.+?)\s+[—–-]\s+(?P<a>[^—–]{2,80})$")


def _czysc(t):
    """Markdown w linii -> zwykły tekst, polska typografia (cudzysłowy „”, półpauza, wielokropek)."""
    t = _dok()._md_inline(t)
    t = re.sub(r'"([^"\n]+)"', "„\\1”", t)
    t = re.sub(r"\s-\s", " – ", t).replace("...", "…")
    return " ".join(t.split())


def _tabela(linie):
    w = []
    for l in linie:
        kom = [c.strip() for c in l.strip().strip("|").split("|")]
        if any(kom) and all(re.fullmatch(r":?-{2,}:?", c) for c in kom if c):
            continue                                  # wiersz ---|---
        w.append([_czysc(c) for c in kom])
    n = max([len(r) for r in w] or [0])
    return [r + [""] * (n - len(r)) for r in w]


def _cytat(t):
    """„cytat — autor” -> (cytat, autor); bez autora autor = ''."""
    t = _czysc(t)
    m = _RX_AUTOR.match(t)
    q, a = (m.group("q"), m.group("a").strip()) if m else (t, "")
    return q.strip("„” \"").strip(), a


def _elementy(linie):
    """Linie pod nagłówkiem `##` -> elementy w kolejności: dop (akapit), li (lista), liczba, tab, obr, cyt."""
    out, par = [], []

    def akapit():
        if par:
            out.append({"k": "dop", "t": _czysc(" ".join(par))})
            par.clear()

    i = 0
    while i < len(linie):
        surowa = linie[i]
        s = surowa.strip()
        i += 1
        if not s or s.startswith("```") or (s.startswith("<!--") and s.endswith("-->")):
            if not s:
                akapit()
            continue
        if s.startswith("|"):
            akapit()
            tab = [s]
            while i < len(linie) and linie[i].strip().startswith("|"):
                tab.append(linie[i].strip())
                i += 1
            out.append({"k": "tab", "wiersze": _tabela(tab)})
            continue
        if s.startswith(">"):
            akapit()
            q = [s.lstrip(">").strip()]
            while i < len(linie) and linie[i].strip().startswith(">"):
                q.append(linie[i].strip().lstrip(">").strip())
                i += 1
            out.append({"k": "cyt", "t": " ".join(x for x in q if x)})
            continue
        mo = _RX_OBR.match(s)
        if mo:
            akapit()
            out.append({"k": "obr", "podpis": _czysc(mo.group("p")), "src": mo.group("s").strip()})
            continue
        ml, mn = _RX_LI.match(s), _RX_NUM.match(s)
        if ml or mn:
            akapit()
            num = bool(mn and not ml)
            poz = _czysc((ml or mn).group(1))
            if out and out[-1]["k"] == "li" and out[-1]["num"] == num:
                out[-1]["poz"].append(poz)
            else:
                out.append({"k": "li", "poz": [poz], "num": num})
            continue
        mc = _RX_LICZBA.match(s)
        if mc and any(c.isdigit() for c in mc.group("l")):
            akapit()
            out.append({"k": "liczba", "l": _czysc(mc.group("l")), "o": _czysc(mc.group("o"))})
            continue
        if out and out[-1]["k"] == "li" and not par and surowa[:1] in (" ", "\t"):
            out[-1]["poz"][-1] += " " + _czysc(s)                    # zawinięty punkt listy
            continue
        par.append(re.sub(r"^#{3,6}\s+", "", s))
    akapit()
    return out


def _tabela_dluga(w):
    """Czy któraś komórka tabeli jest dłuższa niż jedna linia pisma w `table` (stały wiersz, 13 pt)? Szerokość kolumny jak w
    `dokument._wagi_tabeli` (jak w `build_dk.s_table`): tyle znaków mieści się w jednej linii."""
    wagi = _dok()._wagi_tabeli(w[0], w[1:])
    razem = sum(wagi)
    return any(len(r[j]) > max(4.0, (28.5 * wagi[j] / razem - 1.0) * 3.5) for j in range(len(w[0])) for r in w if j < len(r))


def _sciezka_obrazu(src, folder):
    """Ścieżka obrazu ze scenariusza -> bezwzględna (względne liczone od `folder`; %20 z linków też działa)."""
    kand = [src] + ([urllib.parse.unquote(src)] if "%" in src else [])
    pelne = [os.path.abspath(k if os.path.isabs(k) else os.path.join(folder or "", k)) for k in kand]
    return next((p for p in pelne if os.path.isfile(p)), pelne[0])


def model(md, folder=None):
    """Scenariusz -> model w formacie dokument.py {"nazwa", "tytul", "tytul_idx", "bloki", "ostrzezenia"} + "podtytul" i "slajdy"
    (po jednym wpisie na każdy `##`: {"typ": "tresc" | "rozdzial", "haslo", "b": [indeksy bloków], "el": [elementy]}).
    Bloki: h1 (tytuł, nazwa rozdziału), p (podtytuł, dopisek, liczba z opisem, podpis obrazu), h2 (hasło), li, tabela, obraz, cytat.
    Dzięki temu `dokument.pokrycie(model, pptx, spec["mapa_blokow"])` sprawdza, czy cały tekst scenariusza stoi w pliku."""
    d = _dok()
    tekst = wyciagnij(md)
    if tekst is None:
        raise ValueError("To nie wygląda na scenariusz – brakuje pierwszej linii „%s” — scenariusz musi się od niej zaczynać." % MARKER)
    pola, naglowki, cur = {}, [], None
    for l in tekst.split("\n")[1:]:
        s = l.strip()
        mh = _RX_H2.match(s)
        if mh:
            cur = {"haslo": mh.group(1), "linie": []}
            naglowki.append(cur)
        elif cur is not None:
            cur["linie"].append(l)
        else:
            mp = _RX_POLE.match(s)
            if mp:
                pola["pod" if mp.group(1).lower().startswith("pod") else "tyt"] = _czysc(mp.group(2))
    bloki = []

    def dodaj(typ, t="", poziom=0, **kw):
        bloki.append(d._blok(typ, t, poziom, **kw))
        return len(bloki) - 1

    tytul, podtytul = pola.get("tyt", ""), pola.get("pod", "")
    tytul_idx = dodaj("h1", tytul, 1) if tytul else None
    pod_idx = dodaj("p", podtytul, 0, podtytul=True) if tytul and podtytul else None
    slajdy = []
    for n in naglowki:
        mr = _RX_ROZ.match(_czysc(n["haslo"]))
        if mr:
            nazwa = _czysc(mr.group(1))
            s = {"typ": "rozdzial", "haslo": nazwa, "b": [dodaj("h1", nazwa, 1)] if nazwa else [], "el": _elementy(n["linie"])}
            slajdy.append(s)
            continue
        haslo = _czysc(n["haslo"])
        s = {"typ": "tresc", "haslo": haslo, "b": [dodaj("h2", haslo, 2)] if haslo else [], "el": _elementy(n["linie"])}
        for e in s["el"]:
            if e["k"] == "dop":
                e["b"] = [dodaj("p", e["t"])]
            elif e["k"] == "li":
                e["b"] = [dodaj("li", x, 0, num=e["num"]) for x in e["poz"]]
            elif e["k"] == "liczba":
                e["b"] = [dodaj("p", (e["l"] + " " + e["o"]).strip())]
            elif e["k"] == "tab":
                e["b"] = [dodaj("tabela", "", 0, wiersze=e["wiersze"])]
            elif e["k"] == "cyt":
                e["b"] = [dodaj("cytat", _czysc(e["t"]))]
            elif e["k"] == "obr":
                e["plik"] = _sciezka_obrazu(e["src"], folder)
                e["b"] = [dodaj("obraz", "", 0, obraz=e["plik"])] + ([dodaj("p", e["podpis"])] if e["podpis"] else [])
            s["b"] += e["b"]
        slajdy.append(s)
    nazwa = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", tytul).strip(" .")[:80] or "prezentacja"
    return {"nazwa": nazwa, "tytul": tytul, "podtytul": podtytul, "tytul_idx": tytul_idx, "pod_idx": pod_idx, "bloki": bloki,
            "ostrzezenia": [], "slajdy": slajdy}


# =====================================================================================================================
# 3. LINT
# =====================================================================================================================
def sprawdz(md, folder=None, limit=None, przyklad_ok=False):
    """Kontrola scenariusza przed budową -> {"ok", "slajdy" (z treścią), "rozdzialy", "tytul", "uwagi", "bledy"}. Błąd = nie da się
    zbudować slajdu 1:1; uwaga = da się, ale warto poprawić (hasło dłuższe niż 10 słów, dopisek ponad 30, więcej niż 4 punkty,
    samo hasło, za dużo slajdów względem `limit`). `folder` = baza ścieżek obrazów (`Źródła/x.jpg`); bez niego brak pliku obrazu
    sprawdzamy tylko dla ścieżek bezwzględnych. Błąd „Czat przepisał przykład…”: scenariusz zawiera nazwy ze starego wzoru (Baton Przykład,
    baton-przyklad.jpg; lista z `znaki_przykladu()`, czyli z aktualnego wzoru) albo puste miejsca ze szkieletu (<hasło slajdu>); `przyklad_ok=True`
    wyłącza to wykrywanie (testy z wzorem). Każdy błąd to „jedno zdanie — szczegóły”: okno pokazuje samo zdanie, resztę zwija."""
    wyn = {"ok": False, "slajdy": 0, "rozdzialy": 0, "tytul": "", "uwagi": [], "bledy": []}
    try:
        m = model(md, folder)
    except ValueError as e:
        wyn["bledy"].append(str(e))
        return wyn
    bl, uw = wyn["bledy"], wyn["uwagi"]
    tresc = [s for s in m["slajdy"] if s["typ"] == "tresc"]
    roz = [s for s in m["slajdy"] if s["typ"] == "rozdzial"]
    wyn.update(slajdy=len(tresc), rozdzialy=len(roz), tytul=m["tytul"])
    if not m["tytul"]:
        bl.append("W scenariuszu brakuje tytułu prezentacji — pod linią „%s” dodaj wiersz „tytuł: …”." % MARKER)
    if not tresc:
        bl.append("W scenariuszu nie ma żadnego slajdu — każdy slajd zaczyna się od linii „## Hasło slajdu”.")
    if len(m["slajdy"]) > SLAJDOW_MAX:
        bl.append("Scenariusz ma za dużo slajdów — ma %d, a program buduje najwyżej %d. Podziel go na dwie prezentacje." % (len(m["slajdy"]), SLAJDOW_MAX))
    if _slow(m["podtytul"]) > PODTYTUL_SLOW:
        uw.append("Podtytuł ma %d słów - na okładce mieści się jedna, najwyżej dwie linie (do %d słów). Skróć go." % (_slow(m["podtytul"]), PODTYTUL_SLOW))
    if len(m["tytul"]) > COVER_DLUGI:
        uw.append("Tytuł prezentacji ma %d znaków - krótszy (do %d) dostanie ładniejszą okładkę." % (len(m["tytul"]), COVER_DLUGI))
    for nr, s in enumerate(m["slajdy"], 1):
        if s["typ"] == "rozdzial":
            if not s["haslo"]:
                bl.append("Przekładka nr %d nie ma nazwy — wpisz ją po „## Rozdział:”." % nr)
            if s["el"]:
                bl.append("Pod przekładką „%s” stoi tekst — przekładka pokazuje tylko nazwę rozdziału. Przenieś ten tekst na osobny slajd (##)." % s["haslo"])
            nast = m["slajdy"][nr] if nr < len(m["slajdy"]) else None
            if nast is None or nast["typ"] == "rozdzial":
                uw.append("Rozdział „%s” nie ma po sobie żadnego slajdu z treścią." % s["haslo"])
            continue
        _slajd(s, nr, folder, bl, uw)
    if limit and len(tresc) > int(limit):
        uw.append("Scenariusz ma %d slajdów z treścią, a limit to %d. Poproś o skrócenie albo zostaw, jak jest." % (len(tresc), int(limit)))
    if not przyklad_ok:
        low = md.lower()
        if any(z in low for z in znaki_przykladu()):
            bl.insert(0, BLAD_PRZYKLAD)
        elif _RX_PUSTE.search(md):
            bl.insert(0, BLAD_SZKIELET)
    wyn["ok"] = not bl
    return wyn


def blad_krotko(bledy):
    """Lista błędów z `sprawdz` -> JEDNO krótkie zdanie dla człowieka: pierwszy błąd bez części po „ — ” (szczegóły zostają w liście błędów)."""
    zd = str((bledy or [""])[0]).split(" — ", 1)[0].strip()
    return (zd if zd[-1:] in ".!?" else zd + ".") if zd else "Z tego scenariusza nie da się zbudować slajdów."


def _slajd(s, nr, folder, bl, uw):
    """Kontrola jednego slajdu treści (bledy i uwagi dopisywane do list)."""
    nazwa = "Slajd „%s”" % s["haslo"] if s["haslo"] else "Slajd nr %d" % nr
    if not s["haslo"]:
        bl.append("%s nie ma hasła — nagłówek ## jest pusty, a hasło to tytuł slajdu." % nazwa)
    elif _slow(s["haslo"]) > HASLO_SLOW:
        uw.append("%s: hasło ma %d słów (zalecane do 8) - krótsze lepiej wygląda." % (nazwa, _slow(s["haslo"])))
    el = s["el"]
    if not el:
        uw.append("%s ma samo hasło, bez dopisku - stanie jako jedno zdanie na środku slajdu." % nazwa)
        return
    rodz = [e["k"] for e in el]
    dop = [e for e in el if e["k"] == "dop"]
    if len(dop) > 1:
        uw.append("%s: ma %d osobne akapity - dopisek ma być jednym krótkim zdaniem." % (nazwa, len(dop)))
    slow_dop = sum(_slow(e["t"]) for e in dop)
    if slow_dop > DOPISEK_SLOW:
        uw.append("%s: dopisek ma %d słów (zalecany do 25) - skróć go." % (nazwa, slow_dop))
    for e in el:
        if e["k"] == "li":
            if len(e["poz"]) > PUNKTY_MAX:
                bl.append("%s ma za dużo punktów (%d) — na jednym slajdzie mieści się najwyżej %d. Skróć listę albo przenieś część na inny slajd (##)." % (
                    nazwa, len(e["poz"]), PUNKTY_MAX))
            elif len(e["poz"]) > PUNKTY_ZALECANE:
                uw.append("%s: ma %d punktów (zalecane do %d) - mniej punktów czyta się lepiej." % (nazwa, len(e["poz"]), PUNKTY_ZALECANE))
        elif e["k"] == "tab":
            w = e["wiersze"]
            if len(w) < 2:
                bl.append("%s: tabela jest pusta — potrzebny nagłówek i co najmniej jeden wiersz z danymi." % nazwa)
            elif len(w) - 1 > TABELA_WIERSZE or len(w[0]) > TABELA_KOLUMNY:
                bl.append("%s: tabela jest za duża — ma %d wierszy i %d kolumn, a na slajdzie mieści się najwyżej %d wierszy i %d kolumn. Skróć ją albo "
                          "podziel na dwa slajdy (##)." % (nazwa, len(w) - 1, len(w[0]), TABELA_WIERSZE, TABELA_KOLUMNY))
            elif _tabela_dluga(w):
                uw.append("%s: w tabeli są komórki dłuższe niż jedna linia - skróć je, bo tabela ma jedną linię pisma w wierszu." % nazwa)
        elif e["k"] == "obr":
            if folder or os.path.isabs(e["src"]):
                if not os.path.isfile(_sciezka_obrazu(e["src"], folder)):
                    bl.append("%s: obrazu „%s” nie ma w Twoich plikach — użyj nazwy dokładnie tak, jak jest w folderze Źródła." % (nazwa, e["src"]))
    if rodz.count("tab") > 1:
        bl.append("%s ma %d tabele — na jednym slajdzie może stać jedna." % (nazwa, rodz.count("tab")))
    if "tab" in rodz and [k for k in rodz if k not in ("tab", "dop")]:
        bl.append("%s: tabela stoi razem z innymi elementami — zajmuje cały slajd i nie może stać z punktami, liczbą, obrazem ani cytatem. "
                  "Przenieś je na osobny slajd (##)." % nazwa)
    elif "tab" in rodz and dop and len(" ".join(e["t"] for e in dop)) > SOURCE_ZNAKI:
        bl.append("%s: dopisek przy tabeli jest za długi — ma %d znaków, a przy tabeli mieści się jedna krótka linia (do %d znaków)." % (
            nazwa, len(" ".join(e["t"] for e in dop)), SOURCE_ZNAKI))
    if rodz.count("liczba") > LICZBY_MAX:
        bl.append("%s ma za dużo liczb-bohaterów (%d) — na slajdzie mieści się najwyżej %d." % (nazwa, rodz.count("liczba"), LICZBY_MAX))
    if rodz.count("obr") > OBRAZY_MAX:
        bl.append("%s ma za dużo obrazów (%d) — na slajdzie mieści się najwyżej %d." % (nazwa, rodz.count("obr"), OBRAZY_MAX))
    if rodz.count("cyt") > 1:
        bl.append("%s ma %d cytaty — na slajdzie może stać jeden." % (nazwa, rodz.count("cyt")))


# =====================================================================================================================
# 4. SKŁADANIE: scenariusz -> spec dla build_dk (ten sam kształt co dokument.zloz)
# =====================================================================================================================
def _karta_liczby(sz, e, duza=False):
    """Liczba-bohater: hero (Mindset, do 60 pt) + opis. duza: liczba stoi sama na slajdzie (pismo największe, jakie karta znosi)."""
    bl = [{"k": "hero", "t": e["l"], **({"pt": 60} if duza else {})}]
    if e["o"]:
        bl.append(sz.blok("lead", (e["o"], None), color="ink", **({"pt": 36} if duza else {})) if _slow(e["o"]) <= 8
                  else sz.blok("p", (e["o"], None), **({"pt": 26} if duza else {"max_pt": 18})))
    return sz.k_karta(*bl)


def _wiersze(ctx, el):
    """Elementy slajdu -> (wiersze `uklad`, gotowy). gotowy=False tylko dla samej listy (reguły S4/S14 szablonuj ułożą kafle)."""
    d, sz = _dok(), ctx.sz
    rows, gotowy, i = [], True, 0
    while i < len(el):
        e, k = el[i], el[i]["k"]
        if k == "liczba":
            j = i
            while j < len(el) and el[j]["k"] == "liczba":
                j += 1
            karty = [_karta_liczby(sz, x) for x in el[i:j]]
            rows.append(sz.k_cols(karty, pad=1.3 if len(karty) == 1 else 1.1, rwane_ok=True,
                                  **({"valign": "m", "min_h": 7.5} if len(karty) == 1 and len(el) == 1 else {})))
            i = j
            continue
        if k == "obr":
            j = i
            while j < len(el) and el[j]["k"] == "obr":
                j += 1
            rows.append({"k": "pics", "items": [{"image": x["plik"], "caption": x["podpis"]} for x in el[i:j]]})
            i = j
            continue
        if k == "dop":
            nast = el[i + 1] if i + 1 < len(el) else None
            if nast and nast["k"] == "li":                      # dopisek + punkty = jedna karta
                bl = [sz.blok("p", (e["t"], None), pt=24)] + [{"k": "li", "t": x, "icon": "check", "pt": 22} for x in nast["poz"]]
                rows.append(sz.k_cols([sz.k_karta(*bl)], pad=1.2, valign="m"))
                i += 2
                continue
            rows.append(sz.k_band((e["t"], None), "brand") if rows else
                        sz.k_cols([sz.k_karta(sz.blok("p", (e["t"], None), align="l", pt=26))], pad=1.3, valign="m"))
        elif k == "li":
            w, g = d._wiersze_lista(ctx, {"k": "li", "t": e["poz"], "num": e["num"]})
            rows += w
            gotowy = gotowy and g
        elif k == "cyt":
            q, a = _cytat(e["t"])
            rows.append({"k": "quote", "t": q, "author": a})
        i += 1
    return rows, gotowy


def _min_h(ctx, sp, udzial):
    """Wysokość karty (cm) jako ułamek pola treści pod tytułem tego slajdu: krótka treść wypełnia slajd, nie zostawia pustego dołu."""
    bd = ctx.bd
    return round(udzial * (bd.CB - bd.uklad_top(sp)) / bd.cm(1), 1)


def _kand(nazwa, sl, wyp):
    """Kandydat układu (format `szablonuj.zapis_wariantow`) dla slajdu, którego `szablonuj.ocena` nie liczy (statement, hero_stat, table):
    punkty i wypełnienie szacowane, nie z pomiaru renderu."""
    return {"nazwa": nazwa, "opcje": {}, "punkty": 110.0, "miary": {"wypelnienie": round(wyp, 3), "gestosc": 0.0}, "usterki": [],
            "dopuszczony": True, "slajd": sl}


def _kand_uklad(ctx, nazwa, sp):
    """Kandydat z miary układu (`szablonuj.rozloz` + `ocena`) albo None, gdy treść się nie mieści albo pismo spada poniżej progów."""
    sl = ctx.sz.rozloz(dict(sp), ctx.bd)
    oc = ctx.sz.ocena(sl, ctx.bd)
    if {u["kod"] for u in oc["usterki"]} & _dok()._ZLE:
        return None
    return {"nazwa": nazwa, "opcje": {}, "punkty": oc["punkty"], "miary": oc["miary"], "usterki": oc["usterki"], "dopuszczony": True, "slajd": sl}


def _wynik(nr, kand, wz):
    """Lista kandydatów -> (slajd wybranego = pierwszego, decyzje, rekord wariantów | None, wz) albo None, gdy żaden się nie mieści."""
    kand = [k for k in kand if k]
    if not kand:
        return None
    return kand[0]["slajd"], [], ({"zrodlo": nr, "czesc": 0, "wybrany": 0, "kandydaci": kand} if len(kand) > 1 else None), wz


def _wypelnij(ctx, sl, udzial=0.7):
    """Slajd `uklad` z jednym rzędem kart-pojemników (kafle, kroki, karta z punktami): karty rosną do `udzial` pola treści, a treść stoi w nich
    na środku - krótka lista nie zostawia pustego dołu. Zmiana zostaje tylko, gdy slajd nadal się mieści; wynik zmierzony na nowo."""
    rows = sl.get("rows") or []
    if sl.get("type") != "uklad" or len(rows) != 1 or rows[0].get("k") != "cols" or not rows[0].get("kont") or not rows[0].get("card", True) \
            or any(b["k"] == "img" for it in rows[0]["items"] for b in it["blocks"]):
        return False
    cel = _min_h(ctx, sl, udzial)
    if (rows[0].get("min_h") or 0) >= cel:
        return False
    stare = (rows[0].get("min_h"), rows[0].get("valign"))
    rows[0]["min_h"], rows[0]["valign"] = cel, "m"
    if ctx.bd.uklad_layout(sl)[0] is None:
        rows[0]["min_h"], rows[0]["valign"] = stare
        return False
    return True


def _statement(ctx, nr, haslo, dop):
    """Hasło (Mindset, duże) i dopisek (Lato) na środku slajdu `statement` (t14) albo None, gdy nie zmieszczą się nad logo."""
    bd = ctx.bd
    w = bd.cm(26)
    size = bd.title_size(haslo, 54, 34, w)
    ls = bd.display_lines(haslo, size, w)
    th = len(ls) * size * 12700
    dol = (bd.H - th) / 2 - bd.cm(0.4) + th + bd.cm(0.8) + len(bd.lines_for(dop, 20, w)) * 20 * 1.35 * 12700
    if len(ls) > 3 or dol > bd.H - bd.cm(3.2):
        return None
    return {"type": "statement", "bg": "card", "text": haslo, "title": haslo, "note": dop, "max_pt": 54, "zrodlo": nr}


def _warianty_dopisku(ctx, nr, haslo, t):
    """Samo hasło i dopisek: statement (hasło duże, dopisek pod nim) / karta z dopiskiem Lato / zielona karta z tezą (do 16 słów)."""
    sz = ctx.sz
    kand = []
    st = _statement(ctx, nr, haslo, t)
    if st:
        kand.append(_kand("hasło i dopisek na środku slajdu", st, 0.45))
    sp = {"type": "uklad", "title": haslo, "valign": "t", "zrodlo": nr,
          "rows": [sz.k_cols([sz.k_karta(sz.blok("p", (t, None), align="l", pt=26))], pad=1.3, valign="m")]}
    sp["rows"][0]["min_h"] = _min_h(ctx, sp, 0.75)
    kand.append(_kand_uklad(ctx, "dopisek w dużej karcie", sp))
    if sz.nslow((t, None)) <= 16:
        sp = {"type": "uklad", "title": haslo, "valign": "t", "zrodlo": nr,
              "rows": [sz.k_cols([sz.k_karta(sz.blok("lead", (t, None), align="c"), fill="brand", align="c")], pad=1.6, valign="m")]}
        sp["rows"][0]["min_h"] = _min_h(ctx, sp, 0.75)
        kand.append(_kand_uklad(ctx, "dopisek jako teza na zielonej karcie", sp))
    return _wynik(nr, kand, ("teza-zielona", "t14", "hasło i dopisek na środku slajdu") if st else
                  ("haslowanie", "t61", "hasło i dopisek w dużej karcie"))


def _warianty_liczb(ctx, nr, haslo, el):
    """Same liczby-bohaterowie: karty z dużą liczbą na wysokość pola (t37 / t38); jedna liczba ma jeszcze wariant `hero_stat` (t37)."""
    sz, bd = ctx.sz, ctx.bd
    n = len(el)
    sp = {"type": "uklad", "title": haslo, "valign": "t", "zrodlo": nr,
          "rows": [sz.k_cols([_karta_liczby(sz, e, duza=n == 1) for e in el], pad=1.3 if n == 1 else 1.1, rwane_ok=True, valign="m")]}
    sp["rows"][0]["min_h"] = _min_h(ctx, sp, 0.75)
    kand = [_kand_uklad(ctx, "liczba-bohater w karcie", sp)]
    e = el[0]
    hs = {"type": "hero_stat", "title": haslo, "value": e["l"], "label": e["o"], "zrodlo": nr}
    if n == 1 and e["o"] and len(e["l"]) <= 5 and bd.title_bottom(hs) <= bd.cm(3.9) and len(bd.lines_for(e["o"], 22, bd.cm(15))) <= 4:
        kand.append(_kand("liczba-bohater na całą wysokość (hero_stat)", hs, 0.5))
    return _wynik(nr, kand, ("fakt-z-liczba", "t37", "liczba-bohater") if n == 1 else
                  ("fakt-z-liczba", "t38", "%d liczby-bohaterowie obok siebie" % n))


def _wypelnienie_tabeli(bd, n_wierszy):
    """Jak `build_dk.s_table`: wysokość bloku tabeli / pole treści (K4: krótka tabela dostaje wiersze do 1,9 cm i stoi na środku pola)."""
    pole = bd.CB - bd.CT
    rh = min(bd.cm(1.3), (bd.H - bd.cm(7)) / n_wierszy)
    if n_wierszy <= 7 and rh * n_wierszy < 0.65 * pole:
        rh = min(bd.cm(1.9), 0.65 * pole / n_wierszy)
    return rh * n_wierszy / pole


def _warianty_tabeli(ctx, nr, haslo, w, dop):
    """Tabela (t42). Krótka tabela (do 3 wierszy danych) zostawia pusto nad i pod sobą - `build_dk.s_table` nie ma większych wierszy - więc jej
    wariantem jest zapis „karta na wiersz”: każdy wiersz tabeli = karta z parami etykieta (nagłówek kolumny) - wartość."""
    sz = ctx.sz
    sp = {"type": "table", "title": haslo, "head": w[0], "rows": w[1:], "widths": _dok()._wagi_tabeli(w[0], w[1:]), "zrodlo": nr}
    if dop:       # tabela zajmuje cały slajd: dopisek stoi w stopce (drobne pismo, jedna linia)
        sp["source"] = dop
        ctx.uwagi.append("Slajd „%s”: dopisek przy tabeli stoi w stopce slajdu drobnym pismem (krótka tabela może dostać go w pasie pod kartami)." % haslo)
    kand = [_kand("tabela", sp, _wypelnienie_tabeli(ctx.bd, len(w)))]
    if 2 <= len(w) <= 4 and 2 <= len(w[0]) <= 4 and all(w[0]) and all(all(r) for r in w[1:]):
        karty = [sz.k_karta(*[{"k": "kv", "label": w[0][j], "t": r[j]} for j in range(len(w[0]))]) for r in w[1:]]
        sp2 = {"type": "uklad", "title": haslo, "valign": "t", "zrodlo": nr, "rows": [sz.k_cols(karty, pad=1.1, rwane_ok=True, valign="m")]}
        if dop:       # w karcie-wierszu dopisek nie musi być drobny: stoi w pasie pod kartami
            sp2["rows"].append(sz.k_band((dop, None), "brand"))
        sp2["rows"][0]["min_h"] = _min_h(ctx, sp2, 0.55 if dop else 0.7)
        kand.append(_kand_uklad(ctx, "karta na wiersz tabeli", sp2))
    return _wynik(nr, kand, ("tabela", "t42", "tabela %dx%d" % (len(w), len(w[0]))))


def _slajd_tresci(ctx, s):
    """Slajd `##` -> (slajd, decyzje, rekord wariantów | None, decyzja szablonu). Zawsze JEDEN slajd. Krótka treść wypełnia slajd (statement,
    duża karta, hero_stat); rekord wariantów to kandydaci dla pętli „oka” (`szablonuj.inny_wariant`)."""
    d = _dok()
    el, haslo = s["el"], s["haslo"]
    rodz = [e["k"] for e in el]
    dop = [e["t"] for e in el if e["k"] == "dop"]
    nr = ctx.nowy_nr()
    if "tab" in rodz:
        w = next(e["wiersze"] for e in el if e["k"] == "tab")
        return _warianty_tabeli(ctx, nr, haslo, w, " ".join(dop))
    if "obr" in rodz and set(rodz) <= {"obr", "dop"} and len(dop) <= 1:
        it = [{"image": e["plik"], "caption": e["podpis"]} for e in el if e["k"] == "obr"]
        sp = {"type": "pics", "title": haslo, "items": it, "zrodlo": nr}
        if dop:
            sp["note"] = dop[0]
        return sp, [], None, ("zrzuty", "t26" if len(it) == 1 else ("t63" if len(it) == 2 else "t28"), "%d obraz(y) w całości z podpisem" % len(it))
    if not el:
        sp = {"type": "statement", "bg": "card", "text": haslo, "title": haslo, "max_pt": 54, "zrodlo": nr}
        return sp, [], None, ("teza-zielona", "t14", "samo hasło na środku slajdu")
    wyn = (_warianty_dopisku(ctx, nr, haslo, dop[0]) if rodz == ["dop"] else
           _warianty_liczb(ctx, nr, haslo, el) if set(rodz) == {"liczba"} else None)
    if wyn:
        return wyn
    rows, gotowy = _wiersze(ctx, el)
    sp = {"type": "uklad", "title": haslo, "rows": rows, "valign": "m" if rodz == ["cyt"] else "t", "zrodlo": nr}
    if gotowy:
        _wypelnij(ctx, sp)                                   # jedna karta wypełnia pole treści zamiast zostawiać pusty dół
    wyn = d._wybierz_uklad(ctx, sp, gotowy)
    if wyn is not None:
        if not gotowy:                                       # kafle / kroki z reguł szablonu: ta sama zasada, dla wybranego i dla kandydatów
            for sl in [wyn[0]] + [k["slajd"] for k in (wyn[2] or {}).get("kandydaci", [])]:
                _wypelnij(ctx, sl)
            for k in (wyn[2] or {}).get("kandydaci", []):
                oc = ctx.sz.ocena(k["slajd"], ctx.bd)
                k.update(punkty=oc["punkty"], miary=oc["miary"], usterki=oc["usterki"])
        wz = ("cytat", "t20", "cytat") if rodz == ["cyt"] else (
            ("fakt-z-liczba", "t37", "liczba-bohater") if "liczba" in rodz else (
                ("lista-z-ikona", "t17", "punkty z ikoną") if "li" in rodz else ("teza-zielona", "t14", "hasło i dopisek")))
        return wyn[0], wyn[1], wyn[2], wz
    if set(rodz) <= {"dop", "li"}:            # sam tekst, który się nie mieści: tekst do czytania (flow) - nadal jeden slajd
        bl = [{"k": "li", "t": x} if e["k"] == "li" else {"k": "p", "t": e["t"]} for e in el for x in (e["poz"] if e["k"] == "li" else [None])]
        ctx.uwagi.append("Slajd „%s” ma za dużo tekstu na plakat - stoi jako tekst do czytania, bez haseł. Skróć dopisek albo punkty." % haslo)
        return {"type": "flow", "title": haslo, "blocks": bl}, [], None, ("akapit-do-czytania", "t15", "tekst do czytania")
    raise ValueError("Slajd „%s” ma za dużo treści — nie mieści się na jednym slajdzie. Skróć jego treść albo przenieś część na inny slajd (##)." % haslo)


def zloz(md, ustawienia=None):
    """Scenariusz -> spec dla build_dk (kształt jak `dokument.zloz`: theme, sections, slides, mapa_blokow, uwagi, cel="scenariusz", szablon,
    bledy_tekstu, warianty, warianty_plik, nazwa, tytul, ustawienia, output). Ustawienia: `wyjscie` (folder wyniku), `folder` (baza
    ścieżek obrazów), `nazwa` (nazwa pliku wyniku bez .pptx; domyślnie z tytułu), `limit` (uwaga, gdy slajdów z treścią jest więcej).
    ValueError po polsku, gdy `sprawdz` zgłasza błędy albo slajd nie mieści się na jednym slajdzie."""
    ust = ustawienia or {}
    folder = ust.get("folder")
    kontrola = sprawdz(md, folder, ust.get("limit"), bool(ust.get("przyklad_ok")))
    if not kontrola["ok"]:
        raise ValueError("Scenariusza nie da się zbudować:\n- " + "\n- ".join(kontrola["bledy"]))
    import build_dk
    d = _dok()
    with d._pomiar_ukladu(build_dk):
        return _zloz(md, ust, kontrola)


def _zloz(md, ust, kontrola):
    d = _dok()
    m = model(md, ust.get("folder"))
    ctx = d._Ctx()
    ctx.bd.T = dict(ctx.bd.THEMES["shop"])
    ctx.uwagi.extend(kontrola["uwagi"])
    slides, mapa, decyzje, rekordy = [], {}, [], []

    def dodaj(sl, bloki, dec=(), wz=None):
        slides.append(sl)
        nr = len(slides)
        mapa[nr] = sorted(set(bloki))
        for x in dec:
            decyzje.append(dict(x, slajd=nr))
        if wz:
            decyzje.append(dict(d._dec(ctx, wz[0], wz[1], wz[2]), slajd=nr))
        return nr

    ok = {"tytul": m["tytul"], "podtytul": m["podtytul"] or None, "kicker": "", "meta": ""}
    okl = d._slajd_okladki(m, ok)
    if okl["type"] == "cover_text" and ok["podtytul"] and _slow(ok["podtytul"]) <= PODTYTUL_SLOW:
        okl["subtitle"] = ok["podtytul"]                     # 1:1: pełny podtytuł autora (dokument.py skraca go do frazy)
    okl["notes"] = "\n".join(x for x in (m["tytul"], m["podtytul"]) if x)
    dodaj(okl, [i for i in (m["tytul_idx"], m["pod_idx"]) if i is not None],
          wz=("okladka", "t14" if okl["type"] == "statement" else "t09", "okładka %s" % ("z jednym zdaniem na środku (długi tytuł)" if okl["type"] == "statement" else "bez produktu")))
    n_roz = n_tresc = 0
    for s in m["slajdy"]:
        if s["typ"] == "rozdzial":
            n_roz += 1
            dodaj({"type": "section", "variant": "dark", "number": "%02d" % n_roz, "title": s["haslo"], "section": s["haslo"]}, s["b"],
                  wz=("przekladka", "t11", "przekładka rozdziału %d: „%s”" % (n_roz, s["haslo"])))
            continue
        n_tresc += 1
        sl, dec, rek, wz = _slajd_tresci(ctx, s)
        if rek:
            rekordy.append(rek)
        dodaj(sl, s["b"], dec, wz)
    dodaj({"type": "end", "variant": "brand", "hashtag": "#zawszedobra"}, [], wz=("zakonczenie", "t64", "zakończenie"))
    ctx.uwagi.append("Razem w pliku: %d slajdów (%d z treścią + okładka%s i zakończenie)." % (
        len(slides), n_tresc, (", %d przekładki" % n_roz) if n_roz else ""))
    nazwa = ust.get("nazwa") or m["nazwa"]
    # lint tekstu: tekst każdego slajdu z modelu (jak dokument._lint; program błędów NIE poprawia)
    bledy = d._lint(m, mapa, ctx.uwagi)
    return {"theme": "shop", "sections": n_roz >= 2, "slides": slides, "mapa_blokow": mapa, "uwagi": ctx.uwagi, "cel": "scenariusz",
            "szablon": decyzje, "bledy_tekstu": bledy, "warianty": {"wersja": 1, "slajdy": rekordy}, "warianty_plik": "warianty-szablon.json",
            "nazwa": nazwa, "tytul": m["tytul"],
            "ustawienia": {"slajdy": n_tresc, "rozdzialy": n_roz, "razem": len(slides), "ramka": len(slides) - n_tresc},
            "output": os.path.join(ust.get("wyjscie") or os.getcwd(), nazwa + ".pptx")}


# =====================================================================================================================
# 5. POLECENIA DLA AI (czat i agent z plikami)
# =====================================================================================================================
FORMAT = (
    "FORMAT SCENARIUSZA (program zbuduje z niego slajdy jeden do jednego):\n"
    "- Pierwsza linia: # SCENARIUSZ DK. Pod nią: „tytuł: …” (wymagany, najlepiej do 8 słów) i „podtytuł: …” (opcjonalny, jedno zdanie).\n"
    "- Każdy nagłówek ## to DOKŁADNIE jeden slajd i nic ponad to: program niczego nie dzieli ani nie łączy. Okładkę i zakończenie dodaje "
    "program - nie pisz ich.\n"
    "- „## Rozdział: Nazwa” to przekładka (slajd z samą nazwą rozdziału); nic pod nią nie piszesz.\n"
    "- Tekst nagłówka ## to HASŁO slajdu: jego tytuł, do 8 słów, jedna myśl, bez kropki na końcu.\n"
    "- Pod hasłem dajesz treść slajdu, najczęściej samo jedno zdanie dopisku (do 25 słów). Do wyboru:\n"
    "  * dopisek: zwykła linia tekstu;\n"
    "  * punkty (najwyżej 4, każdy krótki): linie zaczynające się od „- ”;\n"
    "  * liczba-bohater: „**42%** krótki opis liczby” (do 4 takich linii na slajd);\n"
    "  * tabela: wiersze „| a | b |” z linią „|---|---|” pod nagłówkiem (najwyżej 8 wierszy i 6 kolumn); tabela zajmuje cały slajd, "
    "więc oprócz niej dajesz najwyżej krótką linię dopisku;\n"
    "  * obraz: „![podpis](Źródła/nazwa-pliku.jpg)” (do 6 na slajd; tylko pliki z podanej listy, nazwa dokładnie jak na liście);\n"
    "  * cytat: „> treść cytatu — Autor”.\n"
    "- Pisz po polsku, z polską typografią: cudzysłowy „…”, półpauza –. Bez emoji.")


_RX_SCEN = re.compile(r"^scenariusz(?:-(\d+))?\.md$", re.I)


def _kolejny_scenariusz(folder):
    """(ścieżka KOLEJNEGO pliku scenariusza, ścieżka najnowszego istniejącego albo None). Numeracja jak w programie: scenariusz.md = wersja 1,
    potem scenariusz-2.md, scenariusz-3.md… Agent zapisuje wynik jako kolejny plik i nigdy nie nadpisuje poprzedniego."""
    nr, ostatni = 0, None
    try:
        for n in os.listdir(folder):
            m = _RX_SCEN.match(n)
            if m and os.path.isfile(os.path.join(folder, n)) and int(m.group(1) or 1) > nr:
                nr, ostatni = int(m.group(1) or 1), os.path.join(folder, n)
    except OSError:
        pass
    return os.path.join(folder, "scenariusz.md" if nr == 0 else "scenariusz-%d.md" % (nr + 1)), ostatni


def _oddaj_czat(poprawiony=False, dodatek=""):
    """Końcowy blok każdego polecenia dla czatu: jednoznacznie, CO oddać (sam scenariusz w jednym bloku kodu, bez komentarzy)."""
    return ("CO MASZ ODDAĆ\nOdpowiedz WYŁĄCZNIE pełnym%s scenariuszem w jednym bloku kodu (```markdown), od linii # SCENARIUSZ DK; bez komentarzy "
            "przed blokiem i po nim%s." % (", poprawionym" if poprawiony else "", ", bez opisu zmian" if poprawiony else "")) + dodatek


def _oddaj_agent(plik, dodatek=""):
    """Końcowy blok każdego polecenia dla agenta z plikami (Cowork / Code): kolejny plik w folderze i jedno zdanie na koniec."""
    return ("## CO MASZ ODDAĆ\nZapisz CAŁY scenariusz (od linii # SCENARIUSZ DK, bez bloku kodu wokół) jako kolejny plik %s w folderze prezentacji "
            "(scenariusz-N.md; nie nadpisuj poprzednich wersji) i napisz jedno zdanie: „Gotowe – wróć do programu Stwórz prezentację.”" % plik) + dodatek


def _limit_slajdow(slajdy):
    try:
        n = int(slajdy or 0)
    except (TypeError, ValueError):
        n = 0
    return ("Najwyżej %d slajdów z treścią (okładka, zakończenie i przekładki się nie liczą). " % n) if n > 0 else ""


def _blok_kodu(tekst):
    return "```markdown\n" + tekst.strip("\n") + "\n```"


def _przytnij_zrodla(zrodla, folder):
    """Teksty dokumentów -> jeden tekst (łącznie ok. ZRODLA_ZNAKI znaków, po równo na dokument); przycięty dostaje dopisek, że reszta
    jest w pliku w folderze."""
    out, zostalo = [], ZRODLA_ZNAKI
    for i, z in enumerate(zrodla or []):
        tx = (z.get("tekst") or "").strip()
        udzial = max(0, zostalo) // (len(zrodla) - i)
        czesc = tx
        if len(tx) > udzial:
            czesc = tx[:udzial].rsplit(None, 1)[0] if udzial and " " in tx[:udzial] else tx[:udzial]
        zostalo -= len(czesc)
        gdzie = (" w folderze %s" % os.path.join(folder, "Źródła")) if folder else " w folderze ze źródłami"
        dopisek = "" if len(czesc) == len(tx) else "\n[…tekst przycięty: pokazuję %d z %d znaków; reszta jest w pliku „%s”%s]" % (
            len(czesc), len(tx), z.get("plik", ""), gdzie)
        out.append("=== PLIK: %s ===\n%s%s" % (z.get("plik", ""), czesc, dopisek))
    return "\n\n".join(out)


def polecenie_przygotowania(zrodla, obrazy, slajdy, tytul="", folder=""):
    """Polecenie dla czatu (bez dostępu do plików): materiały źródłowe -> scenariusz prezentacji marki Dobra Kaloria.
    zrodla = [{"plik", "tekst"}] (tekst dokumentów, łącznie przycięty do ok. 35 000 znaków), obrazy = nazwy plików do przeciągnięcia
    do czatu, slajdy = limit slajdów z treścią, tytul = tytuł prezentacji (puste: czat proponuje), folder = folder prezentacji."""
    cz = [
        "ROLA\nJesteś redaktorem prezentacji marki Dobra Kaloria (zdrowe przekąski, sklep dobrakaloria.pl). Z materiałów poniżej "
        "przygotuj SCENARIUSZ prezentacji w formacie programu „Stwórz prezentację”, który zbuduje z niego slajdy 1:1.",
        "CEL\n" + (("Prezentacja „%s”. " % tytul) if tytul else "Zaproponuj krótki tytuł prezentacji na podstawie materiałów. ") +
        "Najwyżej %d slajdów z treścią (okładka, zakończenie i przekładki rozdziałów się nie liczą); raczej mniej: lepiej kilka mocnych "
        "slajdów niż dużo słabych. Dobierz tylko to, co w materiałach naprawdę ważne." % int(slajdy),
        "ZASADY TREŚCI\n"
        "1. Niczego nie wymyślasz. Liczby, nazwy, daty, składniki, certyfikaty, cytaty i fakty bierzesz WYŁĄCZNIE z materiałów; "
        "czego tam nie ma, pomijasz. Liczby i nazwy przepisujesz dokładnie.\n"
        "2. Slajd to plakat, nie kartka: hasło (tytuł slajdu, do 8 słów, jedna myśl) i krótki dopisek (do 25 słów). Nie wklejaj akapitów.\n"
        "3. Kolejność myśli jak w materiałach. Powtórzeń i ogólników („wysoka jakość”, „innowacyjne rozwiązanie”) unikaj.\n"
        "4. Tabelę, liczbę-bohatera i cytat użyj tylko wtedy, gdy materiały je mają.\n"
        "5. Szkielet poniżej pokazuje sam FORMAT. Nie przepisuj z niego żadnych słów i nie zostawiaj nawiasów <…>.",
        FORMAT,
        SZKIELET_OPIS + "\n" + _blok_kodu(SZKIELET),
        "MATERIAŁY (tekst dokumentów)\n" + (_przytnij_zrodla(zrodla, folder) or "(brak dokumentów tekstowych - treść jest w załączonych obrazach)"),
    ]
    if obrazy:
        cz.append("OBRAZY I ZRZUTY (przeciągnij do tego czatu)\n" + "\n".join("- %s" % o for o in obrazy) + "\n"
                  "Odczytaj z nich treść (tekst, liczby, tabele) i użyj jej tak samo jak tekstu dokumentów. Obraz wstaw na slajd "
                  "(![podpis](Źródła/nazwa-pliku)) tylko wtedy, gdy ma tam stać jako zdjęcie lub zrzut; nazwa dokładnie jak na liście. "
                  "Gdy zrzut zawiera dane, zapisz je jako tabelę albo liczbę-bohatera.")
    cz.append(_oddaj_czat(False, " Nie pytaj o nic, zrób scenariusz z tego, co masz." + (
        " Jeśli nie widzisz załączonych obrazów, odpowiedz jednym zdaniem: „Nie widzę obrazów - przeciągnij je do czatu i wyślij "
        "polecenie jeszcze raz.”" if obrazy else "")))
    return "\n\n".join(cz)


OCENA_PLANSZY = (
    "Dla KAŻDEJ planszy i KAŻDEGO slajdu na niej oceń po kolei: czy hasło jest krótkie i mieści się w jednej-dwóch liniach, czy dopisek lub "
    "punkty nie są ścianą tekstu, czy slajd nie ma dużej pustej przestrzeni, czy tabela, liczba-bohater i obrazy są czytelne, czy rodzaj "
    "treści pasuje do tego, co jest na slajdzie. Ocen nie wypisuj: widać je tylko w poprawkach scenariusza.")


def _lista_problemow(uwagi, problemy):
    """Dwie listy do polecenia poprawki: „PROBLEMY NA SLAJDACH” (z kontroli PowerPointa, po ludzku, z numerem slajdu) i „UWAGI PROGRAMU”."""
    cz = []
    if problemy:
        cz.append("PROBLEMY NA SLAJDACH (kontrola w PowerPoint; napraw każdy: skróć tekst albo zmień rodzaj treści)\n" +
                  "\n".join("- %s" % u for u in problemy))
    cz.append("UWAGI PROGRAMU\n" + ("\n".join("- %s" % u for u in uwagi) if uwagi else "(brak uwag - oceń same plansze)"))
    return cz


def polecenie_poprawki(md, uwagi, plansze, slajdy, folder="", problemy=None):
    """Polecenie dla czatu: popraw scenariusz po budowie. md = obecny scenariusz, uwagi = uwagi programu, plansze = nazwy plików PNG
    (zrzuty slajdów) do przeciągnięcia do czatu, slajdy = limit slajdów z treścią, problemy = problemy z kontroli PowerPointa
    po ludzku („Slajd 7: tekst … nie mieści się w polu”)."""
    cz = [
        "ROLA\nJesteś redaktorem prezentacji marki Dobra Kaloria. Program „Stwórz prezentację” zbudował slajdy z poniższego scenariusza. "
        "Popraw scenariusz tak, żeby prezentacja wyglądała i brzmiała lepiej.",
        "CO ROBISZ\n"
        "1. Obejrzyj załączone plansze (zrzuty slajdów), listę problemów i uwagi programu.\n"
        "2. " + OCENA_PLANSZY + "\n"
        "3. Popraw w scenariuszu to, co widać na planszach i co jest na liście problemów: za długie hasła i dopiski, slajdy z pustym miejscem "
        "albo zbyt gęste, tabele z długimi komórkami, źle dobrany rodzaj treści (np. punkty zamiast liczby-bohatera).\n"
        "4. Nie zmieniaj faktów: liczby, nazwy i cytaty zostają jak w scenariuszu. Niczego nie dopisujesz od siebie.\n"
        "5. Najwyżej %d slajdów z treścią (okładka, zakończenie i przekładki się nie liczą). Jeden nagłówek ## = jeden slajd." % int(slajdy),
        FORMAT,
        "OBECNY SCENARIUSZ\n" + _blok_kodu(md),
    ] + _lista_problemow(uwagi, problemy)
    if plansze:
        cz.append("PLANSZE (przeciągnij do tego czatu)\n" + "\n".join("- %s" % p for p in plansze) +
                  ("\nPliki leżą w folderze: %s" % folder if folder else ""))
    cz.append(_oddaj_czat(True, (" Jeśli nie widzisz załączonych plansz, odpowiedz jednym zdaniem: „Nie widzę plansz - przeciągnij obrazy z folderu do czatu "
                                 "i wyślij polecenie jeszcze raz.”" if plansze else "")))
    return "\n\n".join(cz)


def polecenie_poprawki_agenta(folder, scenariusz, zapisz_jako, uwagi, plansze, slajdy, plansze_folder="", problemy=None):
    """Treść POLECENIE-POPRAWKA.md dla agenta z plikami (Claude Cowork / Code): przeczytaj scenariusz i plansze, popraw, zapisz jako kolejny
    plik scenariusz-N.md (`zapisz_jako`, pełna ścieżka) i napisz „Gotowe, wróć do programu”. Prezentację buduje program, nie agent."""
    cz = [
        "# Polecenie: popraw scenariusz prezentacji Dobra Kaloria po obejrzeniu slajdów",
        "Folder prezentacji: %s\nObecny scenariusz: %s\nPlansze (zrzuty slajdów, PNG): %s\nZapisz poprawiony scenariusz jako NOWY plik: %s" % (
            folder, scenariusz, plansze_folder or "(brak plansz - oceń sam scenariusz)", zapisz_jako),
        "## Krok 1. Przeczytaj\nPrzeczytaj obecny scenariusz oraz listę problemów i uwag programu poniżej.",
    ] + _lista_problemow(uwagi, problemy)
    cz.append("## Krok 2. Obejrzyj plansze\n" + (
        "Otwórz KAŻDĄ planszę z folderu %s jako obraz (%s). " % (plansze_folder, ", ".join(plansze[:12]) + ("…" if len(plansze) > 12 else ""))
        if plansze else "Plansz nie ma - oceń scenariusz bez nich. ") + OCENA_PLANSZY)
    cz.append("## Krok 3. Popraw scenariusz\nNie zmieniaj faktów: liczby, nazwy i cytaty zostają jak w scenariuszu, niczego nie dopisujesz od siebie. "
              "Najwyżej %d slajdów z treścią (okładka, zakończenie i przekładki się nie liczą). Jeden nagłówek ## = jeden slajd.\n\n%s" % (int(slajdy), FORMAT))
    cz.append(_oddaj_agent(zapisz_jako, " Nie buduj prezentacji: zrobi to program „Stwórz prezentację” po kliknięciu użytkownika."))
    return "\n\n".join(cz)


def polecenie_naprawy(md, bledy, folder="", agent=False, slajdy=None):
    """KRÓTKIE polecenie po odrzuceniu odpowiedzi: „popraw te błędy i oddaj pełny scenariusz”. Czat ma jeszcze w rozmowie materiały i format
    z pierwszego polecenia, więc nie powtarzam ani szkieletu, ani formatu; dołączam powody (po polsku) i poprzednią odpowiedź do poprawy.
    agent=True: wersja dla agenta z plikami (Cowork / Code) w `folder`: czyta pliki ze Źródeł i zapisuje wynik jako kolejny scenariusz-N.md.
    slajdy = limit slajdów z treścią (None: bez limitu w poleceniu)."""
    bl = [str(b) for b in (bledy or [])] or ["(brak opisu)"]
    if agent:
        return polecenie_naprawy_agenta(folder, bl, _kolejny_scenariusz(folder)[0], slajdy, md)
    zly = (md or "").strip()
    if len(zly) > 20000:
        zly = zly[:20000].rsplit("\n", 1)[0] + "\n[…odpowiedź przycięta]"
    cz = [
        "POPRAWKA\nTwoja poprzednia odpowiedź nie nadaje się do zbudowania slajdów. Powody:\n" + "\n".join("- %s" % b for b in bl),
        "CO ROBISZ\n"
        "1. Popraw scenariusz tylko pod kątem powyższych powodów. Format zostaje taki sam jak w pierwszym poleceniu (# SCENARIUSZ DK, „tytuł: …”, "
        "jeden nagłówek ## = jeden slajd).\n"
        "2. Całą treść bierz WYŁĄCZNIE z materiałów, które dostałeś na początku tej rozmowy (pliki z folderu Źródła). Nie z przykładu ani ze szkieletu: "
        "nie przepisuj ich słów i nie zostawiaj nawiasów <…>.\n"
        "3. " + (_limit_slajdow(slajdy).strip() or "Liczbę slajdów zostaw jak w poprzedniej odpowiedzi.") +"\n"
        "Jeśli nie widzisz tych materiałów (to nowa rozmowa), odpowiedz jednym zdaniem: „Nie widzę materiałów - wklej pierwsze polecenie jeszcze raz.”",
    ]
    if zly:
        cz.append("TWOJA POPRZEDNIA ODPOWIEDŹ (do poprawy; jeśli powodem jest przepisany przykład, nie przepisuj jej, tylko napisz od nowa z materiałów)\n"
                  + _blok_kodu(zly))
    cz.append(_oddaj_czat(True))
    return "\n\n".join(cz)


def polecenie_naprawy_agenta(folder, bledy, zapisz_jako, slajdy=None, md=""):
    """Treść POLECENIE-POPRAWKA.md dla agenta z plikami po odrzuceniu scenariusza: przeczytaj pliki z Źródła, napraw, zapisz jako kolejny plik."""
    zly = (md or "").strip()
    cz = [
        "# Polecenie: popraw scenariusz prezentacji Dobra Kaloria (nie da się z niego zbudować slajdów)",
        "Folder prezentacji: %s\nŹródła: %s\nZapisz poprawiony scenariusz jako NOWY plik: %s" % (folder, os.path.join(folder, "Źródła"), zapisz_jako),
        "## Powody odrzucenia\n" + "\n".join("- %s" % b for b in (bledy or ["(brak opisu)"])),
        "## Krok 1. Przeczytaj materiały\nPrzeczytaj KAŻDY plik z folderu Źródła%s (obrazy i zrzuty ekranu OBEJRZYJ), zanim cokolwiek napiszesz. "
        "Cała treść slajdów ma pochodzić z tych plików: nie z przykładu, nie ze szkieletu, nie wymyślona." % _nazwy_zrodel(folder),
        "## Krok 2. Napisz scenariusz od nowa albo popraw obecny\n%sJeden nagłówek ## = jeden slajd.\n\n%s\n\n%s\n\n%s" % (
            _limit_slajdow(slajdy), FORMAT, SZKIELET_OPIS, _blok_kodu(SZKIELET)),
    ]
    if zly:
        cz.append("## Odrzucona wersja (nie przepisuj jej, jeśli powód to przepisany przykład)\n" + _blok_kodu(zly[:20000]))
    cz.append(_oddaj_agent(zapisz_jako, " Nie buduj prezentacji: zrobi to program po kliknięciu użytkownika."))
    return "\n\n".join(cz)


def _cli_agenta():
    """(polecenie, gdzie leży, jak nazwać program, kiedy go nie da się uruchomić). Windows: stworz-cli.exe w WORK\\pliki programu
    (z okna programu - pełna ścieżka z `&`, bo agent uruchamia to w PowerShellu). Mac (pakiet .app): ten sam plik wykonywalny co okno."""
    if sys.platform == "darwin" and getattr(sys, "frozen", False):
        return ('"%s"' % sys.executable, "to plik wykonywalny programu „Stwórz prezentację”, ten sam co okno; z argumentami działa jak wiersz poleceń",
                "programu", "Claude Cowork, brak programu")
    gdzie = "stworz-cli.exe leży w folderze „WORK\\pliki programu” programu „Stwórz prezentację”"
    if sys.platform == "win32" and getattr(sys, "frozen", False):     # program uruchomiony z okna: znamy prawdziwą ścieżkę
        cli = os.path.join(os.path.dirname(sys.executable), "stworz-cli.exe")
        if os.path.isfile(cli):
            return '& "%s"' % cli, gdzie, "stworz-cli.exe", "Claude Cowork, Mac, brak programu"
    return "stworz-cli.exe", gdzie, "stworz-cli.exe", "Claude Cowork, Mac, brak programu"


def _nazwy_zrodel(folder):
    """„: a.docx, b.png” (nazwy plików w <folder>\\Źródła) albo pusty tekst; polecenie dla agenta wymienia je z nazwy."""
    try:
        n = sorted(x for x in os.listdir(os.path.join(folder, "Źródła")) if os.path.isfile(os.path.join(folder, "Źródła", x)))
    except OSError:
        return ""
    return (": " + ", ".join(n)) if n else ""


def polecenie_agenta(folder):
    """Treść POLECENIE.md dla Claude Code / agenta z dostępem do plików: źródła (wymienione z nazwy) -> scenariusz w kolejnym pliku -> budowa -> plansze."""
    nowy, ostatni = _kolejny_scenariusz(folder)
    cli, gdzie, nazwa, kiedy = _cli_agenta()
    return "\n\n".join([
        "# Polecenie: prezentacja Dobra Kaloria ze scenariusza",
        "Folder prezentacji: %s\nŹródła (docx, pdf, txt, obrazy, zrzuty ekranu): %s\nScenariusz do napisania (nowy plik): %s%s" % (
            folder, os.path.join(folder, "Źródła"), nowy, ("\nPoprzedni scenariusz (zostaje bez zmian): %s" % ostatni) if ostatni else ""),
        "Pracujesz samodzielnie, aż prezentacja przejdzie kontrolę. Pytasz tylko wtedy, gdy w folderze Źródła nie ma materiałów.",
        "## Krok 1. Przeczytaj źródła\nPrzeczytaj KAŻDY plik z folderu Źródła%s. Czytasz je wszystkie PRZED napisaniem pierwszej linii scenariusza. "
        "Dokumenty czytasz jako tekst, a obrazy i zrzuty ekranu OBEJRZYJ narzędziem do odczytu obrazów (są w nich dane, których nie ma w tekście). "
        "Niczego nie wymyślasz: liczby, nazwy, daty, składniki i cytaty tylko ze źródeł. Cała treść slajdów ma pochodzić z tych plików, nie z przykładu "
        "ani ze szkieletu." % _nazwy_zrodel(folder),
        "## Krok 2. Napisz scenariusz\nZapisz %s według formatu poniżej%s. Slajd to plakat: hasło do 8 słów i dopisek do 25 słów.\n\n%s\n\n%s\n\n%s" % (
            nowy, (" (zacznij od poprzedniego scenariusza i popraw go, ale zapisz jako nowy plik)" if ostatni else ""), FORMAT, SZKIELET_OPIS,
            _blok_kodu(SZKIELET)),
        "## Krok 3. Zbuduj prezentację\n```\n%s \"%s\" --scenariusz \"%s\" --wyjscie \"%s\"\n```\n"
        "(%s.) Program najpierw sprawdza scenariusz: linie „BŁĄD” to rzeczy, "
        "które musisz poprawić w scenariuszu (potem uruchom budowę jeszcze raz), „uwagi” to wskazówki. Po budowie wypisuje ścieżkę "
        "pliku .pptx i folder z planszami PNG (zrzuty slajdów, 6 na planszę).\n\n"
        "Nie możesz uruchomić %s (np. %s)? Pomiń Kroki 3 i 4 i przejdź do CO MASZ ODDAĆ: program sam znajdzie nowy scenariusz, "
        "sprawdzi go i zbuduje prezentację." % (cli, folder, nowy, folder, gdzie, nazwa, kiedy),
        "## Krok 4. Oceń plansze\nObejrzyj KAŻDĄ planszę jako obraz. Dla każdego slajdu zapytaj: czy hasło jest krótkie i czytelne, czy dopisek "
        "mieści się bez gęstego tekstu, czy nie ma dużej pustej przestrzeni, czy tabela i obrazy są czytelne. Poprawki wpisuj do scenariusza "
        "(nie do pliku .pptx), zmieniając tylko to, co widać na planszach, i buduj ponownie. Najwyżej 3 rundy. Poprzednie wersje pliku "
        "zostają w folderze (kolejne mają dopisek „v2”, „v3”).",
        _oddaj_agent(nowy, " Jeśli zbudowałeś też prezentację (Kroki 3 i 4), dopisz krótko po polsku: ścieżkę pliku .pptx, liczbę slajdów, co zmieniłeś "
                           "po planszach i co zostało do decyzji człowieka. Nie pisz, że gotowe, jeśli nie obejrzałeś plansz po ostatniej zmianie."),
    ])
