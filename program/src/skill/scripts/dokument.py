# -*- coding: utf-8 -*-
"""dokument.py - prezentacja marki Dobra Kaloria z DOKUMENTU (docx, doc, rtf, odt, pdf, txt, md), bez LLM (13.10.2026).

Kontrakt (stały - okno programu buduje na nim):

    dokument.ROZSZERZENIA                          # (".docx", ".doc", ".rtf", ".odt", ".pdf", ".txt", ".md")
    m   = dokument.wczytaj(plik, rob)              # {"nazwa", "tytul", "bloki": [...], "ostrzezenia": [...]}
    s   = dokument.statystyka(m)                   # zakresy suwaków liczone Z DOKUMENTU
    spec = dokument.zloz(m, {"slajdy": N, "rozdzialy": R, "wyjscie": katalog, "styl": "nowy"})   # spec dla build_dk
    pok = dokument.pokrycie(m, pptx)               # {"akapity", "przeniesione", "brakuje", "tekst": "Treść: 100% ..."}

Blok modelu: {"typ": "h1|h2|h3|p|li|tabela|obraz|cytat", "t": tekst, "poziom": int, "wiersze": [[...]] (tabela),
"obraz": ścieżka (obraz)}; li ma jeszcze "num": True dla listy numerowanej.

Zasady (references/z-dokumentu.md): treści nie gubimy i nie wymyślamy (żadnych własnych tytułów, wniosków, liczb), slajd
to plakat (hasło Mindset + dopisek Lato, liczba-bohater, pas-wniosek - reguły S1-S15 z szablonuj.py), typy slajdów z
pełnego szablonu (okładka, agenda, przekładka, tabela, zrzuty, cytat, zakończenie). Suwaki: `slajdy` = liczba slajdów Z
TREŚCIĄ (okładka, agenda, przekładki i zakończenie są dodatkowe), `rozdzialy` = liczba przekładek rozdziałów.
"""
import argparse
import collections
import contextlib
import copy
import json
import os
import re
import subprocess
import sys
import zipfile

from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ROZSZERZENIA = (".docx", ".doc", ".rtf", ".odt", ".pdf", ".txt", ".md")
MAX_SLOW_DOK = 60000          # powyżej: ValueError z radą podziału
MIN_OBRAZ_DOCX, MIN_OBRAZ_PDF = 100, 200  # najkrótszy bok obrazu (px), który uznajemy za treść
OBRAZ_DEKORACJA = 3           # ten sam obraz na tylu stronach pdf = logo / ozdoba, pomijamy
OBRAZ_PAS = 0.15              # obraz w pasie góry / dołu strony pdf (tyle wysokości) i węższy niż 1/4 strony = logo, pomijamy (21.10)
PROG_NAGL = 1.35              # pdf bez pisma ozdobnego: nagłówek od tylu x pismo podstawowe (etykiety 11 pt przy 8 pt tekstu to nie nagłówki)
KAFEL_MIN = 1.4               # pdf: pismo ozdobne co najmniej tyle x podstawowe = nagłówek strony / liczba w kaflu
_KONIEC_ZD = ".!?…"


# =====================================================================================================================
# 1. WCZYTANIE
# =====================================================================================================================
def _blok(typ, t="", poziom=0, **kw):
    d = {"typ": typ, "t": t, "poziom": poziom}
    d.update(kw)
    return d


def _czysc(t):
    """Biała spacja: twarde spacje, tabulatory, znaki zerowej szerokości, podwójne spacje -> jedna spacja."""
    if not t:
        return ""
    t = t.replace("\xa0", " ").replace("​", "").replace("­", "").replace("﻿", "")
    t = t.replace(" ", " ").replace(" ", " ").replace("\v", " ").replace("\t", " ")
    return " ".join(t.split())


def _slow(t):
    return len(t.split())


def _nazwa_pliku(plik):
    return os.path.splitext(os.path.basename(plik))[0]


def wczytaj(plik, rob):
    """Plik dokumentu -> model {"nazwa", "tytul", "bloki", "ostrzezenia"}; `rob` = katalog roboczy (obrazy, kopie z Worda).
    ValueError po polsku: nieznany format, skan bez tekstu, brak Worda dla .doc / .rtf / .odt, dokument > 60 000 słów."""
    plik = os.path.abspath(plik)
    if not os.path.isfile(plik):
        raise ValueError("Nie znalazłem pliku: %s" % plik)
    ext = os.path.splitext(plik)[1].lower()
    if ext not in ROZSZERZENIA:
        raise ValueError("Ten format (%s) nie jest obsługiwany. Dla dokumentów: %s." % (ext or "bez rozszerzenia", ", ".join(ROZSZERZENIA)))
    rob = os.path.abspath(rob)
    os.makedirs(rob, exist_ok=True)
    ostrz = []
    if ext == ".docx":
        bloki = _wczytaj_docx(plik, rob, ostrz)
    elif ext in (".doc", ".rtf", ".odt"):
        bloki = _wczytaj_docx(_przez_word(plik, rob), rob, ostrz)
    elif ext == ".pdf":
        bloki = _wczytaj_pdf(plik, rob, ostrz)
    else:
        bloki = _blocks_z_tekstu(_czytaj_tekst(plik), md=(ext == ".md"), baza=os.path.dirname(plik), ostrz=ostrz)
    return _domknij(_nazwa_pliku(plik), bloki, ostrz)


def _czytaj_tekst(plik):
    raw = open(plik, "rb").read()
    for enc in ("utf-8-sig", "cp1250"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("cp1250", "replace")


def _domknij(nazwa, bloki, ostrz):
    """Porządki wspólne dla wszystkich formatów: czyszczenie, listy numerowane „z ręki”, tytuł, limit słów."""
    out = []
    for b in bloki:
        if b["typ"] in ("tabela", "obraz", "kpi", "kv"):
            out.append(b)
            continue
        b["t"] = _czysc(b["t"])
        if b["t"]:
            out.append(b)
    for b in out:   # markdown wpisany w Wordzie („## Tytuł”): hasze znikają, akapit z haszami to nagłówek
        if b["typ"] in ("h1", "h2", "h3", "p"):
            mh = re.match(r"^(#{1,6})\s+(?=\S)", b["t"])
            if mh:
                b["t"] = b["t"][mh.end():]
                if b["typ"] == "p":
                    b["typ"], b["poziom"] = "h%d" % min(3, len(mh.group(1))), min(3, len(mh.group(1)))
    out = _krotkie_na_liste(_ukryte_listy(out))
    slow = sum(_slow(b["t"]) for b in out if b["typ"] not in ("tabela", "obraz")) + \
        sum(_slow(c) for b in out if b["typ"] == "tabela" for w in b["wiersze"] for c in w)
    if slow > MAX_SLOW_DOK:
        raise ValueError("Dokument ma ok. %d słów - to za dużo na jedną prezentację (limit %d). Podziel go na części (np. po "
                         "rozdziałach) i zrób osobne prezentacje." % (slow, MAX_SLOW_DOK))
    tytul, idx = _wybierz_tytul(out, nazwa)
    if not out:
        ostrz.append("Dokument jest pusty - nie znalazłem w nim żadnego tekstu.")
    return {"nazwa": nazwa, "tytul": tytul, "tytul_idx": idx, "bloki": out, "ostrzezenia": ostrz}


def _wybierz_tytul(bloki, nazwa):
    """Tytuł dokumentu: akapit w stylu „Tytuł”; inaczej pierwszy nagłówek 1, gdy to strona tytułowa (jedyny nagłówek 1 albo za
    nim od razu kolejny nagłówek); inaczej nazwa pliku. Zwraca (tytuł, indeks bloku | None)."""
    for i, b in enumerate(bloki):
        if b.get("tytul"):
            return b["t"], i
    z_pliku = " ".join(nazwa.replace("_", " ").split()) or nazwa      # nazwa pliku jako tytuł: bez podkreślników
    h1 = [i for i, b in enumerate(bloki) if b["typ"] == "h1"]
    if not h1 or h1[0] != 0 and any(b["typ"] not in ("p",) or _slow(b["t"]) > 25 for b in bloki[:h1[0]]):
        return z_pliku, None
    i = h1[0]
    if len(h1) == 1 and any(b["typ"] in ("h2", "h3") for b in bloki[i + 1:]):
        return bloki[i]["t"], i
    nast = bloki[i + 1:i + 2]
    if len(h1) == 1 and not nast:
        return bloki[i]["t"], i
    if nast and nast[0]["typ"] in ("h1", "h2"):       # nagłówek, a zaraz po nim kolejny nagłówek = strona tytułowa
        return bloki[i]["t"], i
    return z_pliku, None


_LISTA_NUM = re.compile(r"^(\d{1,2}|[a-z])[.)]\s+(?=\S)")


def _ukryte_listy(bloki):
    """Akapity zaczynające się od „1. ”, „2) ”, „a) ” (>= 2 kolejne z rosnącym numerem) to lista numerowana wpisana z ręki."""
    out, i = [], 0
    while i < len(bloki):
        b = bloki[i]
        m = _LISTA_NUM.match(b["t"]) if b["typ"] == "p" else None
        if m:
            j, seq = i, []
            while j < len(bloki) and bloki[j]["typ"] == "p":
                mj = _LISTA_NUM.match(bloki[j]["t"])
                if not mj or (seq and not _kolejny(seq[-1], mj.group(1))):
                    break
                seq.append(mj.group(1))
                j += 1
            if len(seq) >= 2:
                for x in bloki[i:j]:
                    out.append(_blok("li", _LISTA_NUM.sub("", x["t"], 1), 0, num=True))
                i = j
                continue
        out.append(b)
        i += 1
    return out


def _krotkie_na_liste(bloki):
    """Dwa i więcej kolejnych krótkich akapitów (do 6 słów, bez kropki na końcu) to pozycje listy (etykiety, smaki, linie adresu), nie
    osobne myśli - od razu kafle zamiast pustych kart. Akapit dłuższy niż 4 słowa z liczbą z jednostką (wynik, „80% - grupa 1”) zostaje akapitem."""
    sz = _sz()

    def krotki(b):
        t = b["t"]
        return b["typ"] == "p" and 1 <= _slow(t) <= 6 and t[-1:] not in ".!?…" and (_slow(t) <= 4 or not sz.liczba_bohater((t, None))) and \
            not b.get("podtytul")
    out, i = [], 0
    while i < len(bloki):
        j = i
        while j < len(bloki) and krotki(bloki[j]):
            j += 1
        if j - i >= 2:
            out += [_blok("li", x["t"], 0, num=False) for x in bloki[i:j]]
            i = j
        else:
            out.append(bloki[i])
            i += 1
    return out


def _kolejny(a, b):
    if a.isdigit() and b.isdigit():
        return int(b) == int(a) + 1
    return len(a) == 1 and len(b) == 1 and ord(b) == ord(a) + 1


# --- docx: zipfile + lxml (bez python-docx: w paczce programu go nie ma) ----------------------------------------------
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_V = "urn:schemas-microsoft-com:vml"
_MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _xml(dane):
    """Parser OOXML bez rozwijania encji i bez sieci (dokument od obcej osoby nie może czytać plików z dysku - XXE)."""
    return etree.fromstring(dane, etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False))


def _w(t):
    return "{%s}%s" % (_W, t)


_POMIN_TEKST = {_w("del"), _w("instrText"), _w("delText"), _w("txbxContent"), "{%s}Fallback" % _MC, _w("pPr"), _w("rPr")}
_BUL = "•·▪●○■□◦‣∙"
_BUL_RE = re.compile(r"^[%s]\s*(?=\S)|^[-–—]\s+(?=\S)" % re.escape(_BUL))


def _tekst_wezla(el):
    out = []

    def rec(e):
        for c in e:
            t = c.tag
            if not isinstance(t, str) or t in _POMIN_TEKST:
                continue
            if t == _w("t"):
                out.append(c.text or "")
            elif t in (_w("tab"), _w("cr")):
                out.append(" ")
            elif t == _w("br"):
                if c.get(_w("type")) not in ("page", "column"):
                    out.append(" ")
            elif t == _w("noBreakHyphen"):
                out.append("-")
            else:
                rec(c)
    rec(el)
    return "".join(out)


def _styl_docx(z):
    """{id stylu: {"name", "based", "outline", "num", "sz", "b"}} + domyślny rozmiar pisma (pt)."""
    st, def_sz = {}, 11.0
    if "word/styles.xml" not in z.namelist():
        return st, def_sz
    root = _xml(z.read("word/styles.xml"))
    d = root.find(".//%s/%s/%s" % (_w("docDefaults"), _w("rPrDefault"), _w("rPr")))
    if d is not None and d.find(_w("sz")) is not None:
        def_sz = int(d.find(_w("sz")).get(_w("val"), "22")) / 2.0
    for s in root.findall(_w("style")):
        sid = s.get(_w("styleId"))
        nm = s.find(_w("name"))
        based = s.find(_w("basedOn"))
        ppr, rpr = s.find(_w("pPr")), s.find(_w("rPr"))
        outline = num = None
        if ppr is not None:
            ol = ppr.find(_w("outlineLvl"))
            outline = int(ol.get(_w("val"))) if ol is not None else None
            np_ = ppr.find(_w("numPr"))
            if np_ is not None and np_.find(_w("numId")) is not None:
                num = (np_.find(_w("numId")).get(_w("val")),
                       (np_.find(_w("ilvl")).get(_w("val")) if np_.find(_w("ilvl")) is not None else "0"))
        sz = int(rpr.find(_w("sz")).get(_w("val"), "0")) / 2.0 if rpr is not None and rpr.find(_w("sz")) is not None else None
        b = _jest_wl(rpr, "b") if rpr is not None else False
        st[sid] = {"name": (nm.get(_w("val")) if nm is not None else "").lower(), "based": based.get(_w("val")) if based is not None else None,
                   "outline": outline, "num": num, "sz": sz, "b": b}
    return st, def_sz


def _jest_wl(rpr, tag):
    e = rpr.find(_w(tag)) if rpr is not None else None
    return e is not None and e.get(_w("val"), "1") not in ("0", "false", "off")


_NAGL_RE = re.compile(r"^(?:heading|nagłówek|naglowek|überschrift|titre)\s*(\d)$")


def _poziom_stylu(st, sid):
    """('h', 1..3) | ('tytul', 0) | ('podtytul', 0) | ('cytat', 0) | ('toc', 0) | ('lista', num?) | None - po łańcuchu basedOn."""
    for _ in range(12):
        s = st.get(sid)
        if not s:
            return None
        nm = s["name"]
        m = _NAGL_RE.match(nm)
        if m:
            return ("h", min(3, max(1, int(m.group(1)))))
        if nm in ("title", "tytuł", "tytul"):
            return ("tytul", 0)
        if nm in ("subtitle", "podtytuł", "podtytul"):
            return ("podtytul", 0)
        if nm in ("quote", "intense quote", "block text", "cytat", "cytat intensywny") or nm.startswith("quote"):
            return ("cytat", 0)
        if nm.startswith("toc") or nm.startswith("spis treści") or nm.startswith("table of contents"):
            return ("toc", 0)
        if nm.startswith("list bullet") or nm.startswith("lista punktowana") or nm.startswith("lista z punktorami"):
            return ("lista", False)
        if nm.startswith("list number") or nm.startswith("lista numerowana"):
            return ("lista", True)
        if s["outline"] is not None and s["outline"] < 9:
            return ("h", min(3, s["outline"] + 1))
        sid = s["based"]
    return None


def _num_docx(z):
    """{numId: {ilvl: 'bullet' | 'num'}} z numbering.xml."""
    if "word/numbering.xml" not in z.namelist():
        return {}
    root = _xml(z.read("word/numbering.xml"))
    abstr = {}
    for a in root.findall(_w("abstractNum")):
        lv = {}
        for l in a.findall(_w("lvl")):
            f = l.find(_w("numFmt"))
            lv[l.get(_w("ilvl"))] = "bullet" if f is None or f.get(_w("val")) in ("bullet", "none") else "num"
        abstr[a.get(_w("abstractNumId"))] = lv
    out = {}
    for n in root.findall(_w("num")):
        a = n.find(_w("abstractNumId"))
        out[n.get(_w("numId"))] = abstr.get(a.get(_w("val")) if a is not None else None, {})
    return out


def _relacje_docx(z):
    nm = "word/_rels/document.xml.rels"
    if nm not in z.namelist():
        return {}
    root = _xml(z.read(nm))
    return {r.get("Id"): r.get("Target") for r in root if r.get("TargetMode") != "External"}


def _wczytaj_docx(plik, rob, ostrz):
    try:
        z = zipfile.ZipFile(plik)
        doc = _xml(z.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError, etree.XMLSyntaxError):
        raise ValueError("Nie mogę otworzyć tego pliku jako dokumentu Worda (.docx) - jest uszkodzony albo ma inny format. "
                         "Otwórz go w Wordzie i zapisz ponownie jako .docx.")
    st, def_sz = _styl_docx(z)
    num = _num_docx(z)
    rels = _relacje_docx(z)
    body = doc.find(_w("body"))
    ctx = {"z": z, "st": st, "def_sz": def_sz, "num": num, "rels": rels, "rob": rob, "ostrz": ostrz, "n_obr": 0,
           "toc": False, "obr_widziane": {}}
    bloki = []
    _body_docx(body, ctx, bloki)
    if ctx["toc"]:
        ostrz.append("Pominąłem spis treści z dokumentu (program robi własną agendę).")
    if doc.find(".//" + _w("txbxContent")) is not None:
        ostrz.append("W dokumencie są pola tekstowe (ramki) - ich zawartości nie przeniosłem do slajdów.")
    if "word/footnotes.xml" in z.namelist():
        fn = _xml(z.read("word/footnotes.xml"))
        ile = sum(1 for f in fn.findall(_w("footnote")) if f.get(_w("type")) is None and _tekst_wezla(f).strip())
        if ile:
            ostrz.append("Przypisy dolne (%d) nie są przenoszone na slajdy." % ile)
    return _naglowki_z_formatu(bloki, ctx)


def _body_docx(el, ctx, bloki):
    for c in el:
        t = c.tag
        if t == _w("p"):
            _akapit_docx(c, ctx, bloki)
        elif t == _w("tbl"):
            _tabela_docx(c, ctx, bloki)
        elif t == _w("sdt"):
            cont = c.find(_w("sdtContent"))
            if cont is not None:
                _body_docx(cont, ctx, bloki)


def _runy(p):
    """Runy z tekstem akapitu (bez usuniętych i bez pól tekstowych): [(tekst, pogrubiony, rozmiar|None)]."""
    out = []

    def rec(e):
        for c in e:
            t = c.tag
            if not isinstance(t, str) or t in (_w("del"), _w("txbxContent"), "{%s}Fallback" % _MC):
                continue
            if t == _w("r"):
                tx = _tekst_wezla(c)
                if tx.strip():
                    rpr = c.find(_w("rPr"))
                    sz = rpr.find(_w("sz")) if rpr is not None else None
                    out.append((tx, _jest_wl(rpr, "b"), int(sz.get(_w("val"), "0")) / 2.0 if sz is not None else None))
            else:
                rec(c)
    rec(p)
    return out


def _akapit_docx(p, ctx, bloki):
    ppr = p.find(_w("pPr"))
    sid = None
    num_id = ilvl = None
    outline = None
    if ppr is not None:
        ps = ppr.find(_w("pStyle"))
        sid = ps.get(_w("val")) if ps is not None else None
        np_ = ppr.find(_w("numPr"))
        if np_ is not None:
            ni, il = np_.find(_w("numId")), np_.find(_w("ilvl"))
            num_id = ni.get(_w("val")) if ni is not None else None
            ilvl = il.get(_w("val")) if il is not None else "0"
        ol = ppr.find(_w("outlineLvl"))
        outline = int(ol.get(_w("val"))) if ol is not None else None
        if ppr.find("%s/%s" % (_w("rPr"), _w("vanish"))) is not None:
            return
    rodzaj = _poziom_stylu(ctx["st"], sid)
    tekst = _tekst_wezla(p)
    obrazy = _obrazy_akapitu(p, ctx)  # obrazy idą po tekście akapitu (zwykle akapit zawiera tylko obraz)
    if rodzaj and rodzaj[0] == "toc":
        ctx["toc"] = True
        return
    if tekst.strip():
        runy = _runy(p)
        rozm = [r[2] for r in runy if r[2]]
        sz = max(rozm) if rozm else None
        if sz is None and sid in ctx["st"]:
            sid2, g = sid, 0
            while sid2 in ctx["st"] and g < 12:
                if ctx["st"][sid2]["sz"]:
                    sz = ctx["st"][sid2]["sz"]
                    break
                sid2, g = ctx["st"][sid2]["based"], g + 1
        wszystko_b = bool(runy) and all(r[1] for r in runy)
        if outline is not None and outline < 9 and not rodzaj:
            rodzaj = ("h", min(3, outline + 1))
        if rodzaj and rodzaj[0] == "h":
            bloki.append(_blok("h%d" % rodzaj[1], tekst, rodzaj[1], _styl=True))
        elif rodzaj and rodzaj[0] == "tytul":
            bloki.append(_blok("h1", tekst, 1, tytul=True, _styl=True))
        elif rodzaj and rodzaj[0] == "podtytul":
            bloki.append(_blok("p", tekst, 0, podtytul=True))
        elif rodzaj and rodzaj[0] == "cytat":
            bloki.append(_blok("cytat", tekst))
        else:
            lista = None
            if num_id is not None and num_id != "0":
                lista = ("num" if ctx["num"].get(num_id, {}).get(ilvl or "0") == "num" else "bullet", int(ilvl or 0))
            elif sid in ctx["st"] and _poziom_stylu(ctx["st"], sid) and _poziom_stylu(ctx["st"], sid)[0] == "lista":
                lista = ("num" if _poziom_stylu(ctx["st"], sid)[1] else "bullet", 0)
            elif sid in ctx["st"]:  # styl z numeracją (np. „Akapit z listą” przypięty do listy w stylu)
                s = ctx["st"][sid]
                if s["num"] and s["num"][0] != "0":
                    lista = ("num" if ctx["num"].get(s["num"][0], {}).get(s["num"][1]) == "num" else "bullet", int(s["num"][1]))
            if lista:
                bloki.append(_blok("li", tekst, lista[1], num=(lista[0] == "num")))
            else:
                m = _BUL_RE.match(tekst.strip())
                if m:
                    bloki.append(_blok("li", tekst.strip()[m.end():], 0, num=False))
                else:
                    bloki.append(_blok("p", tekst, 0, _b=wszystko_b, _sz=sz))
    bloki.extend(obrazy)


def _obrazy_akapitu(p, ctx):
    """Obrazy osadzone w akapicie (DrawingML `a:blip`, VML `v:imagedata`) -> bloki `obraz` (pliki w <rob>\\obrazy)."""
    out = []
    ids = []
    for e in p.iter():
        if not isinstance(e.tag, str):
            continue
        if e.tag == "{%s}blip" % _A and e.get("{%s}embed" % _R):
            ids.append(e.get("{%s}embed" % _R))
        elif e.tag == "{%s}imagedata" % _V and e.get("{%s}id" % _R):
            ids.append(e.get("{%s}id" % _R))
    for rid in ids:
        tgt = ctx["rels"].get(rid)
        if not tgt:
            continue
        nm = tgt.lstrip("/") if tgt.startswith("/") else "word/" + tgt
        nm = os.path.normpath(nm).replace("\\", "/")
        if nm not in ctx["z"].namelist():
            continue
        if nm in ctx["obr_widziane"]:
            sciezka = ctx["obr_widziane"][nm]
        else:
            sciezka = _zapisz_obraz(ctx["z"].read(nm), os.path.splitext(nm)[1], ctx, MIN_OBRAZ_DOCX)
            ctx["obr_widziane"][nm] = sciezka
        if sciezka:
            out.append(_blok("obraz", "", 0, obraz=sciezka))
    return out


def _zapisz_obraz(dane, ext, ctx, min_bok):
    """Bajty obrazu -> plik PNG / JPG w <rob>\\obrazy; None, gdy za mały albo nieczytelny (emf / wmf bez obsługi)."""
    from PIL import Image
    import io
    try:
        im = Image.open(io.BytesIO(dane))
        im.load()
    except Exception:
        ctx["ostrz"].append("Pominąłem obraz w formacie %s (nie umiem go odczytać)." % (ext or "?"))
        return None
    if min(im.size) < min_bok:
        return None
    katalog = os.path.join(ctx["rob"], "obrazy")
    os.makedirs(katalog, exist_ok=True)
    ctx["n_obr"] += 1
    sc = os.path.join(katalog, "obraz_%02d.png" % ctx["n_obr"])
    if im.mode not in ("RGB", "RGBA", "L", "LA", "P"):
        im = im.convert("RGB")
    im.save(sc)
    return sc


def _tabela_docx(tbl, ctx, bloki):
    wiersze = []
    for tr in tbl.findall(_w("tr")):
        kom = []
        for tc in tr.findall(_w("tc")):
            tcpr = tc.find(_w("tcPr"))
            span = 1
            vm = False
            if tcpr is not None:
                gs = tcpr.find(_w("gridSpan"))
                span = int(gs.get(_w("val"), "1")) if gs is not None else 1
                v = tcpr.find(_w("vMerge"))
                vm = v is not None and v.get(_w("val")) in (None, "continue")
            tx = _czysc(" ".join(_tekst_wezla(p) for p in tc.iter(_w("p"))))
            kom.append("" if vm else tx)
            kom.extend([""] * (span - 1))
        wiersze.append(kom)
    _dodaj_tabele(wiersze, bloki)


def _dodaj_tabele(wiersze, bloki):
    """Tabela -> blok `tabela`; jedna kolumna albo jeden wiersz to w praktyce tekst (ramka, okienko) - zwykłe akapity."""
    wiersze = [[_czysc(c) for c in w] for w in wiersze]
    wiersze = [w for w in wiersze if any(w)]
    if not wiersze:
        return
    n = max(len(w) for w in wiersze)
    wiersze = [w + [""] * (n - len(w)) for w in wiersze]
    puste = [j for j in range(n) if not any(w[j] for w in wiersze)]
    wiersze = [[c for j, c in enumerate(w) if j not in puste] for w in wiersze]
    n = len(wiersze[0]) if wiersze else 0
    if n <= 1 or len(wiersze) == 1:
        for w in wiersze:
            for c in w:
                if c:
                    bloki.append(_blok("p", c, 0))
        return
    bloki.append(_blok("tabela", "", 0, wiersze=wiersze))


def _naglowki_z_formatu(bloki, ctx):
    """Dokument bez stylów nagłówków (np. „Copy do …”): krótki akapit, całość pogrubiona albo większe pismo, bez kropki na końcu =
    nagłówek. Poziomy wg rozmiaru pisma (największy = 1). Znaczniki robocze `_b`, `_sz`, `_styl` znikają."""
    maja = any(b.get("_styl") for b in bloki)
    if not maja:
        akap = [b for b in bloki if b["typ"] == "p" and "_sz" in b]
        zl = collections.Counter()
        for b in akap:
            zl[round(b.get("_sz") or ctx["def_sz"], 1)] += _slow(b["t"])
        baza = zl.most_common(1)[0][0] if zl else ctx["def_sz"]
        kand = []
        for i, b in enumerate(bloki):
            if b["typ"] != "p" or b.get("podtytul"):
                continue
            t = b["t"].strip()
            sz = b.get("_sz") or baza
            sl = _slow(t)
            if not (1 <= sl <= 12) or t[-1:] in ".!?;,…" and not t.endswith(":") or not any(c.isalpha() for c in t):
                continue
            caps = t.upper() == t and sum(c.isalpha() for c in t) >= 4
            if b.get("_b") or sz >= baza * 1.2 or (caps and sl <= 8):
                kand.append((i, sz))
        if kand and len(kand) < 0.5 * max(1, len(akap)):  # same nagłówki w dokumencie to nie nagłówki
            rozm = sorted({round(sz / baza, 1) for _i, sz in kand}, reverse=True)[:3]
            for i, sz in kand:
                r = round(sz / baza, 1)
                poziom = (rozm.index(r) + 1) if r in rozm else 3
                if len(rozm) == 1 and not (sz >= baza * 1.2):
                    poziom = 1
                bloki[i]["typ"] = "h%d" % poziom
                bloki[i]["poziom"] = poziom
    for b in bloki:
        for k in ("_b", "_sz", "_styl"):
            b.pop(k, None)
        if b["typ"].startswith("h") and b["t"].endswith(":"):
            b["t"] = b["t"][:-1].rstrip()
    return bloki


# --- doc / rtf / odt (i pdf bez bibliotek): Word przez COM, własna instancja ----------------------------------------------
_PS_WORD = r"""param([string]$In, [string]$Out)
$ErrorActionPreference = 'Stop'
$przed = @(Get-Process winword -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
$w = $null; $d = $null; $moj = $false
try {
    $w = New-Object -ComObject Word.Application
    $po = @(Get-Process winword -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $nowe = @($po | Where-Object { $przed -notcontains $_ })
    $moj = ($nowe.Count -gt 0)
    if ($moj) { try { Set-Content -LiteralPath ($Out + '.pid') -Value $nowe[0] } catch {} }
    try { $w.Visible = $false; $w.DisplayAlerts = 0; $w.AutomationSecurity = 3 } catch {}
    $d = $w.Documents.Open($In, $false, $true)
    $d.SaveAs2($Out, 16)
    Write-Output 'OK'
} finally {
    if ($d -ne $null) { try { $d.Close() } catch {} }
    if ($w -ne $null -and $moj) { try { $w.Quit() } catch {} }
}
"""


def _przez_word(plik, rob):
    """Plik doc / rtf / odt / pdf -> kopia .docx w katalogu roboczym (Word w OSOBNEJ instancji, bez okna; Word użytkownika zostaje
    nietknięty). Brak Worda albo błąd = ValueError po polsku."""
    wyj = os.path.join(rob, _nazwa_pliku(plik) + " (z Worda).docx")
    if sys.platform != "win32":    # Word przez COM jest tylko na Windows
        raise ValueError("Plików %s program nie czyta na Macu. Otwórz plik w jakimkolwiek edytorze, zapisz jako .docx (albo .txt, "
                         "albo PDF) i spróbuj ponownie." % os.path.splitext(plik)[1].lower())
    ps1 = os.path.join(rob, "_word.ps1")
    with open(ps1, "w", encoding="utf-8-sig") as f:
        f.write(_PS_WORD)
    ext = os.path.splitext(plik)[1].lower()
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1, plik, wyj],
                           capture_output=True, timeout=60 if ext == ".pdf" else 150)     # bez dekodowania wyjścia (strona kodowa konsoli bywa dowolna)
    except (OSError, subprocess.TimeoutExpired):
        r = None
        _zabij_word(wyj + ".pid")      # tylko NASZA instancja Worda (jej numer zapisał skrypt); Word użytkownika zostaje
    if r is None or r.returncode != 0 or not os.path.isfile(wyj):
        if ext == ".pdf":
            raise ValueError("Nie umiem przeczytać tego PDF-a: program nie ma biblioteki do PDF, a Word nie otworzył pliku. "
                             "Otwórz PDF w Wordzie, zapisz jako .docx i spróbuj ponownie.")
        raise ValueError("Pliki %s czyta program przez Microsoft Word, a Word nie odpowiedział na tym komputerze. Otwórz plik "
                         "w jakimkolwiek edytorze, zapisz jako .docx (albo .txt) i spróbuj ponownie." % ext)
    return wyj


def _zabij_word(pidfile):
    try:
        pid = int(open(pidfile, encoding="utf-8-sig").read().strip())
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, timeout=20)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass


# --- pdf: PyMuPDF (fitz) -> pypdf (sam tekst) -> Word -------------------------------------------------------------------------
def _wczytaj_pdf(plik, rob, ostrz):
    try:
        import fitz  # PyMuPDF
    except ImportError:
        fitz = None
    if fitz is not None:
        return _pdf_fitz(plik, rob, ostrz, fitz)
    try:
        import pypdf
    except ImportError:
        pypdf = None
    if pypdf is not None:
        return _pdf_pypdf(plik, ostrz, pypdf)
    ostrz.append("Program nie ma biblioteki do czytania PDF - użyłem Worda (nagłówki i tabele mogą być mniej dokładne).")
    return _wczytaj_docx(_przez_word(plik, rob), rob, ostrz)


def _brak_tekstu():
    return ValueError("To skan bez tekstu - program nie czyta obrazów (nie robi OCR). Zapisz dokument z tekstem (np. z Worda: "
                      "Zapisz jako PDF) albo przepisz treść do pliku .docx lub .txt.")


_NUMER_STR = re.compile(r"^\s*(?:strona|str\.?|page|s\.)?\s*\d{1,4}(?:\s*(?:/|z|of|\|)\s*\d{1,4})?\s*$", re.I)


def _norm_stopka(t):
    return re.sub(r"\d+", "#", " ".join(t.split()).lower())


def _pdf_pypdf(plik, ostrz, pypdf):
    try:
        r = pypdf.PdfReader(plik)
        strony = [(p.extract_text() or "") for p in r.pages]
    except Exception:
        raise ValueError("Nie mogę otworzyć tego PDF-a (jest uszkodzony albo zabezpieczony hasłem).")
    if sum(len(s.strip()) for s in strony) < 20:
        raise _brak_tekstu()
    licz = collections.Counter()
    for s in strony:
        licz.update({_norm_stopka(l) for l in s.splitlines() if l.strip()})
    prog = max(2, int(0.5 * len(strony) + 0.5))
    wyn = []
    for s in strony:
        wyn.append(_akapity_z_linii([l for l in s.splitlines()
                                     if not (len(strony) >= 3 and licz[_norm_stopka(l)] >= prog and _slow(l) <= 12) and
                                     not _NUMER_STR.match(l)]))
    ostrz.append("PDF czytany prostą metodą (sam tekst): nagłówki i tabele rozpoznałem z kształtu tekstu, mogą być mniej dokładne.")
    return _blocks_z_tekstu("\n\n".join(wyn), md=False, baza=None, ostrz=ostrz)


def _akapity_z_linii(linie):
    """Linie tekstu z PDF -> tekst z pustymi liniami między akapitami: linia zawinięta (długa, bez kropki na końcu) łączy się z następną."""
    mx = max([len(l.strip()) for l in linie] or [0])
    out, cur = [], []
    for l in linie:
        l = l.strip()
        if not l:
            continue
        if cur and (len(cur[-1]) < 0.8 * mx or (cur[-1][-1:] in ".!?" and len(cur[-1]) < 0.93 * mx) or
                    _BUL_RE.match(l) or _LISTA_NUM.match(l)):
            out.append(" ".join(cur))
            cur = []
        cur.append(l)
    if cur:
        out.append(" ".join(cur))
    return "\n\n".join(out)


def _rodzina(font):
    """Rodzina pisma ze spanu pdf: „Lato-Bold” -> „lato”; pismo ozdobne wbudowane jako Type3 („Type3 (8 0 R)”) zostaje osobną rodziną."""
    return re.split(r"[-,]", font.lower(), 1)[0].strip()


def _ozdobne(l, ctx):
    """Linia pismem innym niż podstawowe (Mindset w raportach DK) - nagłówek, etykieta albo liczba w kaflu."""
    return ctx["f"] is not None and l["f"] != ctx["f"]


def _srodek_w(r, l):
    cx, cy = (l["x0"] + l["x1"]) / 2.0, (l["y0"] + l["y1"]) / 2.0
    return r.x0 <= cx <= r.x1 and r.y0 <= cy <= r.y1


def _pdf_fitz(plik, rob, ostrz, fitz):
    """PDF -> bloki. Pojemniki z wypełnień (karty, kafle, tabele z separatorami wierszy, metki) wyznaczają strukturę; pismo ozdobne
    (druga rodzina pisma) = nagłówki i etykiety; obraz w pasie góry / dołu strony = logo (pomijany); strona 1 z największym
    pismem = okładka (tytuł, etykieta, podtytuł, meta). PDF bez wypełnień i bez drugiego pisma czyta się jak dawniej (rozmiar pisma)."""
    try:
        pdf = fitz.open(plik)
    except Exception:
        raise ValueError("Nie mogę otworzyć tego PDF-a (jest uszkodzony albo zabezpieczony hasłem).")
    if pdf.needs_pass:
        raise ValueError("Ten PDF jest zabezpieczony hasłem - zapisz go bez hasła i spróbuj ponownie.")
    strony, znaki, obr_licz = [], 0, collections.Counter()
    for page in pdf:
        W, H = page.rect.width, page.rect.height
        lin = []
        for blk in page.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk["lines"]:
                sp = [s for s in ln["spans"] if s["text"].strip()]
                if not sp:
                    continue
                zn = sum(len(s["text"].strip()) for s in sp)
                glowny = max(sp, key=lambda s: len(s["text"].strip()))
                lin.append({"t": "".join(s["text"] for s in ln["spans"]), "n": zn, "f": _rodzina(glowny["font"]),
                            "sz": round(sum(s["size"] * len(s["text"].strip()) for s in sp) / max(1, zn), 1),
                            "b": all((s["flags"] & 16) or "bold" in s["font"].lower() for s in sp),
                            "x0": ln["bbox"][0], "x1": ln["bbox"][2], "y0": ln["bbox"][1], "y1": ln["bbox"][3]})
                znaki += zn
        boxes, seps, dots = [], [], []
        try:
            rys = page.get_drawings()
        except Exception:
            rys = []
        for d in rys:
            r = d.get("rect")
            if not d.get("fill") or r is None or (r.width >= 0.8 * W and r.height >= 0.8 * H):
                continue             # tło strony
            if r.height <= 2.5 and r.width >= 20:
                seps.append(r)              # linia pod komórką tabeli
            elif r.width <= 8 and r.height <= 8:
                dots.append(r)              # kropka punktora
            elif r.width >= 30 and r.height >= 10:
                boxes.append((r, tuple(round(c * 255) for c in d["fill"][:3])))   # karta, kafel, tabela, metka (+ kolor)
        obrazy = []
        for info in page.get_image_info(xrefs=True):
            xr = info.get("xref") or 0
            bb = info["bbox"]
            if not xr or min(info.get("width", 0), info.get("height", 0)) < MIN_OBRAZ_PDF:
                continue
            if (bb[1] < OBRAZ_PAS * H or bb[3] > (1 - OBRAZ_PAS) * H) and (bb[2] - bb[0]) < 0.25 * W:
                continue                    # logo / ozdoba w pasie nagłówka albo stopki strony
            obr_licz[xr] += 1
            obrazy.append((bb[1], xr))
        strony.append({"W": W, "H": H, "lin": lin, "boxes": boxes, "seps": seps, "dots": dots, "obrazy": obrazy})
    if znaki < 20:
        raise _brak_tekstu()
    # stopki i nagłówki stron: ten sam tekst (cyfry = #) w pasie 8% góry / dołu na >= połowie stron
    pas = collections.Counter()
    for s in strony:
        pas.update({_norm_stopka(l["t"]) for l in s["lin"] if l["y0"] < 0.08 * s["H"] or l["y1"] > 0.92 * s["H"]})
    prog = max(2, int(0.5 * len(strony) + 0.5))
    stopki = {k for k, v in pas.items() if len(strony) >= 3 and v >= prog}
    # pismo podstawowe (mediana po znakach), rodzina podstawowa i czy jest drugie pismo (ozdobne)
    zl, fam = collections.Counter(), collections.Counter()
    for s in strony:
        for l in s["lin"]:
            zl[round(l["sz"] * 2) / 2.0] += l["n"]
            fam[l["f"]] += l["n"]
    baza = zl.most_common(1)[0][0] if zl else 11.0
    f_baza = fam.most_common(1)[0][0] if fam else ""
    ozdobne = sum(v for k, v in fam.items() if k != f_baza) >= 0.02 * max(1, sum(fam.values()))
    ctx = {"baza": baza, "f": f_baza if ozdobne else None, "wiel": sorted({s for s in zl if s >= baza * PROG_NAGL}, reverse=True),
           "max": max(zl) if zl else baza, "pdf": pdf, "rob": rob, "ostrz": ostrz, "fitz": fitz, "obr_licz": obr_licz, "nr_obr": 0}
    bloki = []
    for pi, s in enumerate(strony):
        lin = [l for l in s["lin"] if not ((l["y0"] < 0.08 * s["H"] or l["y1"] > 0.92 * s["H"]) and
                                           (_norm_stopka(l["t"]) in stopki or _NUMER_STR.match(l["t"])))]
        if pi == 0 and _pdf_okladka(s, lin, ctx, bloki):
            continue
        _pdf_strona(s, lin, ctx, bloki)
    return _scal_strony(bloki)


def _pdf_okladka(s, lin, ctx, bloki):
    """Strona tytułowa (<= 90 słów, największe pismo dokumentu >= 1,6 x podstawowe) -> h1 (tytuł, `tytul`, `kicker` = etykieta nad nim),
    akapit `podtytul`, blok `kv` `meta` (kafle AUTOR / STAN NA / ZAKRES, data nad tytułem). True = strona zużyta."""
    if not lin or sum(_slow(l["t"]) for l in lin) > 90 or ctx["max"] < 1.6 * ctx["baza"]:
        return False
    duze = sorted((l for l in lin if l["sz"] >= ctx["max"] - 0.5), key=lambda l: (l["y0"], l["x0"]))
    if not duze:
        return False
    y_t0, y_t1 = duze[0]["y0"], duze[-1]["y1"]
    if any(l["sz"] >= KAFEL_MIN * ctx["baza"] and l not in duze and not (l["y1"] <= y_t0 + 1 and _slow(l["t"]) <= 6) for l in lin):
        return False            # inny nagłówek pod tytułem: to pierwsza strona treści, nie okładka
    meta, w_kaflach = [], set()
    for r, _col in sorted(s["boxes"], key=lambda rc: (round(rc[0].y0 / 4), rc[0].x0)):
        w = sorted((l for l in lin if _srodek_w(r, l)), key=lambda l: (l["y0"], l["x0"]))
        if not w or any(id(l) in w_kaflach for l in w):
            continue
        w_kaflach.update(id(l) for l in w)
        meta.append([w[0]["t"].strip(), _skleja_linie([l["t"] for l in w[1:]])])
    reszta = sorted((l for l in lin if id(l) not in w_kaflach and l not in duze), key=lambda l: (l["y0"], l["x0"]))
    nad = [l for l in reszta if l["y1"] <= y_t0 + 1]
    kicker = ""
    if nad and _slow(nad[-1]["t"]) <= 6 and y_t0 - nad[-1]["y1"] < 3 * ctx["baza"]:
        kicker = nad.pop()["t"].strip()
    for l in nad:
        if _slow(l["t"]) <= 6:
            meta.append(["", l["t"].strip()])
    pod = [l for l in reszta if l["y0"] >= y_t1 - 1]
    podt = []
    for l in pod:
        if podt and l["y0"] - podt[-1]["y1"] > 0.8 * l["sz"]:
            break
        podt.append(l)
    bloki.append(_blok("h1", _skleja_linie([l["t"] for l in duze]), 1, tytul=True, kicker=_czysc(kicker)))
    if podt:
        bloki.append(_blok("p", _skleja_linie([l["t"] for l in podt]), 0, podtytul=True))
    for l in pod[len(podt):]:
        bloki.append(_blok("p", l["t"], 0))
    pary = [[_czysc(a), _czysc(b)] for a, b in meta if _czysc(a) or _czysc(b)]
    if pary:
        bloki.append(_blok("kv", "", 0, pary=pary, meta=True))
    return True


def _pdf_strona(s, lin, ctx, bloki):
    """Jedna strona: drzewo pojemników (wypełnienia), linie i separatory przypisane do najmniejszego pojemnika, kropki = punkty."""
    baza = ctx["baza"]
    kont = []
    for r, col in sorted(s["boxes"], key=lambda rc: -(rc[0].width * rc[0].height)):
        w = [l for l in lin if _srodek_w(r, l)]
        if r.height <= 2.6 * baza and len(w) <= 1 and r.width < 0.2 * s["W"]:
            for l in w:
                l["tag"] = True             # metka (status, termin, „KRYTYCZNE”): linia zostaje, nie jest nagłówkiem strony
            continue
        kont.append({"r": r, "col": col, "kids": [], "lin": [], "rodzic": None, "seps": []})
    for i, k in enumerate(kont):
        rodz = [p for p in kont[:i] if p["r"].contains(k["r"])]
        if rodz:
            k["rodzic"] = min(rodz, key=lambda p: p["r"].width * p["r"].height)
            k["rodzic"]["kids"].append(k)
    # biały prostokąt wprost na stronie (tło części strony, nie karta): jego dzieci idą na stronę
    kont = [k for k in kont if not (k["rodzic"] is None and k["col"] == (255, 255, 255) and not any(k["r"].contains(sp) for sp in s["seps"]))]
    for k in kont:
        if k["rodzic"] is not None and k["rodzic"] not in kont:
            k["rodzic"] = None
    root = {"r": None, "kids": [k for k in kont if k["rodzic"] is None], "lin": [], "seps": [], "rodzic": None}
    for l in lin:
        c = root
        while True:
            nx = next((k for k in c["kids"] if _srodek_w(k["r"], l)), None)
            if nx is None:
                break
            c = nx
        c["lin"].append(l)
    for sp in s["seps"]:
        c, cur = None, root
        while True:
            nx = next((k for k in cur["kids"] if k["r"].contains(sp)), None)
            if nx is None:
                break
            cur = c = nx
        if c is not None:
            c["seps"].append(sp)
    for d in s["dots"]:
        cy = (d.y0 + d.y1) / 2.0
        for l in lin:
            if l["y0"] <= cy <= l["y1"] and d.x1 <= l["x0"] + 1 and l["x0"] - d.x1 < 2.5 * baza:
                l["kropka"] = True
                break
    _pdf_kont(root, s, ctx, bloki, 0, sorted(s["obrazy"]))


def _pdf_kolumny(k, lin):
    """Linie bez pojemników w 2-4 kolumnach (FAQ w dwóch szpaltach, trzy decyzje obok siebie) -> lista kolumn albo None. Granica kolumny
    = x, którego nie przecina żadna linia, z >= 2 liniami po każdej stronie."""
    if len(lin) < 4:
        return None
    gran = []
    for b in sorted({round(l["x0"]) for l in lin})[1:]:
        if any(l["x0"] < b - 3 and l["x1"] > b + 3 for l in lin):
            continue
        if sum(1 for l in lin if l["x0"] >= b - 3) >= 2 and sum(1 for l in lin if l["x1"] <= b + 3) >= 2:
            gran.append(b)
    if not gran or len(gran) > 3:
        return None
    kol = [[] for _ in range(len(gran) + 1)]
    for l in lin:
        kol[sum(1 for b in gran if l["x0"] >= b - 3)].append(l)
    kol = [sorted(c, key=lambda l: (l["y0"], l["x0"])) for c in kol if c]
    return kol if len(kol) >= 2 else None


def _pdf_kont(k, s, ctx, bloki, gleb, obrazy=()):
    """Pojemnik (gleb 0 = strona): zawartość w kolejności czytania. Rząd >= 3 równych kafli = kpi / kv; pojemnik z separatorami = tabela;
    reszta = pojemniki zagnieżdżone i linie tekstu (pierwsza linia ozdobna pojemnika = jego nagłówek)."""
    lin = k["lin"]
    if not k["kids"] and not obrazy:
        kol = _pdf_kolumny(k, lin)
        if kol:
            for czesc in kol:
                _pdf_linie(czesc, ctx, bloki, gleb, True)
            return
    items = [(c["r"].y0, c["r"].x0, "k", c) for c in k["kids"]] + [(l["y0"], l["x0"], "l", l) for l in lin] + \
        [(y, 0.0, "o", xr) for y, xr in obrazy]
    items.sort(key=lambda it: (round(it[0] / 4.0), it[1]))
    run, pierwsza, i = [], True, 0
    while i < len(items):
        y, _x, rodz, ob = items[i]
        if rodz == "l":
            run.append(ob)
            i += 1
            continue
        if run:
            _pdf_linie(run, ctx, bloki, gleb, pierwsza)
            run, pierwsza = [], False
        if rodz == "o":
            if ctx["obr_licz"][ob] < OBRAZ_DEKORACJA:
                ctx["nr_obr"] += 1
                sc = _pdf_obraz(ctx["pdf"], ob, ctx["rob"], ctx["ostrz"], ctx["fitz"], ctx["nr_obr"])
                if sc:
                    bloki.append(_blok("obraz", "", 0, obraz=sc))
            i += 1
            continue
        rzad, j = [ob], i + 1
        while j < len(items) and items[j][2] == "k" and abs(items[j][0] - y) <= 4:
            rzad.append(items[j][3])
            j += 1
        if len(rzad) >= 3 and _pdf_kafle(rzad, ctx, bloki):
            i = j
            continue
        for c in sorted(rzad, key=lambda c: c["r"].x0):
            if c["seps"] and _pdf_tabela(c, ctx, bloki):
                continue
            _pdf_kont(c, s, ctx, bloki, gleb + 1)
        i = j
    if run:
        _pdf_linie(run, ctx, bloki, gleb, pierwsza)


def _pdf_kafle(rzad, ctx, bloki):
    """Rząd >= 3 równych kafli: liczba / słowo ozdobnym pismem + opis -> blok `kpi`; krótka etykieta + wartość -> blok `kv`."""
    szer = [c["r"].width for c in rzad]
    if max(szer) > 1.3 * min(szer) or any(c["kids"] or c["seps"] or not c["lin"] or len(c["lin"]) > 6 for c in rzad):
        return False
    items = []
    for c in sorted(rzad, key=lambda c: c["r"].x0):
        w = sorted(c["lin"], key=lambda l: (l["y0"], l["x0"]))
        items.append((w[0], _skleja_linie([l["t"] for l in w[1:]])))
    if all(_ozdobne(l, ctx) and l["sz"] >= KAFEL_MIN * ctx["baza"] for l, _t in items):
        bloki.append(_blok("kpi", "", 0, items=[{"value": _czysc(l["t"]), "label": _czysc(t)} for l, t in items]))
    elif all(_slow(l["t"]) <= 4 and t for l, t in items):
        bloki.append(_blok("kv", "", 0, pary=[[_czysc(l["t"]), _czysc(t)] for l, t in items]))
    else:
        return False
    return True


def _pdf_tabela(c, ctx, bloki):
    """Pojemnik z liniami pod komórkami: kolumny z segmentów pierwszej linii, wiersze z kolejnych; komórka = linie w polu. Nagłówek =
    pierwszy wiersz w całości ozdobny (bez drugiego pisma: pogrubiony), gdy drugi wiersz zaczyna się zwykłym pismem. Dwie kolumny
    bez nagłówka z ozdobną pierwszą komórką w każdym wierszu = `kv` (etykieta: wartość). False = to nie tabela."""
    ys = sorted({round(sp.y0) for sp in c["seps"]})
    kols = []
    for a, b in sorted((sp.x0, sp.x1) for sp in c["seps"] if round(sp.y0) == ys[0]):
        if kols and a < kols[-1][1] - 2:          # segmenty komórek stykają się końcami; scalamy tylko nachodzące
            kols[-1] = (kols[-1][0], max(kols[-1][1], b))
        else:
            kols.append((a, b))
    if len(kols) < 2:
        return False
    gran = [c["r"].y0] + [y + 0.5 for y in ys] + [c["r"].y1]
    kom = [[[] for _ in kols] for _ in range(len(gran) - 1)]
    for l in sorted(c["lin"], key=lambda l: (l["y0"], l["x0"])):
        cy, cx = (l["y0"] + l["y1"]) / 2.0, (l["x0"] + l["x1"]) / 2.0
        ri = next((i for i in range(len(gran) - 1) if gran[i] <= cy < gran[i + 1]), None)
        if ri is None:
            continue
        ci = next((j for j, (a, b) in enumerate(kols) if a - 2 <= cx <= b + 2), None)
        if ci is None:
            ci = min(range(len(kols)), key=lambda j: abs((kols[j][0] + kols[j][1]) / 2.0 - cx))
        if ci == 0 and l.get("tag") and len(kols) == 2:
            ci = 1                                   # metka (zielona pigułka) to wartość, nie etykieta
        kom[ri][ci].append(l)

    def ozd(cell):
        z = [l for l in cell if not l.get("tag")]
        return bool(z) and all((_ozdobne(l, ctx) if ctx["f"] else l["b"]) for l in z)

    def etyk(cell):   # etykieta pary: pismo ozdobne albo pogrubione WERSALIKI do 4 słów („JĘZYK”, „DANE”)
        z = [l for l in cell if not l.get("tag")]
        return bool(z) and all(_ozdobne(l, ctx) or (l["b"] and l["t"].strip().isupper() and _slow(l["t"]) <= 4) for l in z)
    pary = [([_skleja_linie([l["t"] for l in cell]) for cell in row], [ozd(cell) for cell in row], etyk(row[0])) for row in kom]
    pary = [p for p in pary if any(p[0])]
    if len(pary) < 2:
        return False
    wiersze, oz, et = [p[0] for p in pary], [p[1] for p in pary], [p[2] for p in pary]
    naglowek = all(oz[0]) and not oz[1][0]
    if len(kols) == 2 and not naglowek and all(et):
        bloki.append(_blok("kv", "", 0, pary=[[_czysc(a), _czysc(b)] for a, b in wiersze]))
        return True
    _dodaj_tabele(wiersze, bloki)
    return True


def _pdf_obraz(pdf, xref, rob, ostrz, fitz, nr):
    try:
        pix = fitz.Pixmap(pdf, xref)
        if pix.n - pix.alpha >= 4:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        katalog = os.path.join(rob, "obrazy")
        os.makedirs(katalog, exist_ok=True)
        sc = os.path.join(katalog, "pdf_obraz_%02d.png" % nr)
        pix.save(sc)
        return sc
    except Exception:
        ostrz.append("Pominąłem obraz z PDF (nie umiem go odczytać).")
        return None


def _pdf_linie(lin, ctx, bloki, gleb=0, pierwsza=False):
    """Linie tekstu jednego pojemnika -> nagłówek / lista / akapity. Ozdobne pismo = nagłówek (h1 = największe na stronie; h2 = duże albo
    pierwsza linia karty; h3 = reszta); metka = h3; kropka przed linią = punkt; pogrubione pytanie „…?” = h3 (FAQ)."""
    if not lin:
        return
    baza, wiel = ctx["baza"], ctx["wiel"]
    lin = sorted(lin, key=lambda l: (round(l["y0"] / 2.0), l["x0"]))
    l2, i = [], 0     # sam punktor w osobnej linii (Word: „•” + tabulator) dołącza się do następnej linii
    while i < len(lin):
        if lin[i]["t"].strip() and set(lin[i]["t"].strip()) <= set(_BUL + "-–—") and i + 1 < len(lin):
            nx = dict(lin[i + 1])
            nx["t"] = "• " + nx["t"].lstrip()
            l2.append(nx)
            i += 2
            continue
        l2.append(lin[i])
        i += 1
    lin = l2
    grupy, cur = [], [lin[0]]
    for a, b in zip(lin, lin[1:]):
        przerwa = b["y0"] - a["y1"] > 0.6 * a["sz"]
        zmiana = abs(a["sz"] - b["sz"]) > 0.6 or a["b"] != b["b"] or a["f"] != b["f"] or a.get("tag") != b.get("tag")
        koniec = a["t"].rstrip()[-1:] in _KONIEC_ZD and a["x1"] < 0.85 * max(l["x1"] for l in lin) and b["t"].lstrip()[:1].isupper()
        punkt = bool(_BUL_RE.match(b["t"].strip())) or bool(_LISTA_NUM.match(b["t"].strip())) or b.get("kropka")
        if przerwa or zmiana or koniec or punkt:
            grupy.append(cur)
            cur = []
        cur.append(b)
    grupy.append(cur)
    for gi, g in enumerate(grupy):
        t = _skleja_linie([l["t"] for l in g])
        sz = max(l["sz"] for l in g)
        sl = _slow(t)
        tag = any(l.get("tag") for l in g)
        if g[0].get("kropka"):
            bloki.append(_blok("li", _BUL_RE.sub("", t.strip(), 1), 0, num=False))
            continue
        if all(_ozdobne(l, ctx) for l in g) and sl <= 16:
            if gleb == 0 and sz >= ctx["max"] - 0.5 and ctx["max"] >= 1.6 * baza:
                poz = 1
            elif sz >= KAFEL_MIN * baza and gleb == 0:
                poz = 2                                   # nagłówek strony = rozdział
            elif pierwsza and gi == 0 and gleb >= 1:
                bloki.append(_blok("h3", t, 3))           # nagłówek karty = podrozdział (bez sklejania z nagłówkiem strony)
                continue
            else:
                poz = 3
            bloki.append(_blok("h%d" % poz, t, poz, _pdf_h=True, pytanie=(poz == 3 and t.rstrip().endswith("?"))))
            continue
        if tag and sl <= 3:
            bloki.append(_blok("h3", t, 3))
            continue
        if ctx["f"] is None and wiel and sz >= baza * PROG_NAGL and sl <= 16:
            poziom = min(3, 1 + min(range(len(wiel)), key=lambda i: abs(wiel[i] - round(sz * 2) / 2.0)))
            bloki.append(_blok("h%d" % poziom, t, poziom, _pdf_h=True))
            continue
        if all(l["b"] for l in g) and sl <= 12 and t.rstrip().endswith("?"):
            bloki.append(_blok("h3", t, 3, pytanie=True))
            continue
        if all(l["b"] for l in g) and sl <= 10 and t[-1:] not in ".,;!?…" and not tag and                 g[0]["x0"] <= min(l["x0"] for l in lin) + 2 * baza:         # pogrubiona linia od lewej krawędzi (nie „wersja 2.7.5” z prawej)
            bloki.append(_blok("h3", t, 3, _pdf_h=True))
            continue
        m = _BUL_RE.match(t.strip())
        if m:
            bloki.append(_blok("li", t.strip()[m.end():], 0, num=False))
        else:
            bloki.append(_blok("p", t, 0))


def _skleja_linie(linie):
    out = ""
    for l in linie:
        l = l.strip()
        if not out:
            out = l
        elif re.search(r"[A-Za-ząćęłńóśźż]-$", out) and l[:1].islower():
            out = out[:-1] + l      # dzielenie wyrazu na końcu linii
        else:
            out += " " + l
    return out


def _scal_strony(bloki):
    """Akapit przerwany końcem strony / kolumny: poprzedni nie kończy się kropką, następny zaczyna małą literą -> jeden akapit;
    sąsiednie wiersze nagłówka tego samego poziomu -> jeden nagłówek."""
    out = []
    for b in bloki:
        p = out[-1] if out else None
        if p and b["typ"] == "p" and p["typ"] == "p" and p["t"][-1:] not in _KONIEC_ZD + ":;" and b["t"][:1].islower():
            p["t"] += " " + b["t"]
            continue
        if p and b["typ"] == p["typ"] and b["typ"] in ("h1", "h2", "h3") and p.get("_pdf_h") and b.get("_pdf_h") and \
                p["t"][-1:] not in _KONIEC_ZD:
            p["t"] += " " + b["t"]
            continue
        out.append(b)
    for b in out:
        b.pop("_pdf_h", None)
    return out


# --- txt / md ----------------------------------------------------------------------------------------------------------------
_MD_NAGL = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_MD_LISTA = re.compile(r"^\s*(?:[-*+•·▪●○■◦‣∙–—])\s+(.*)$")
_MD_NUM = re.compile(r"^\s*(\d{1,3})[.)]\s+(.*)$")
_MD_OBRAZ = re.compile(r"^!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)\s*$")
_NAGL_NUM = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(?=\S)")


def _md_inline(t):
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"(\*\*|__)(.+?)\1", r"\2", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", t)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    return t


def _blocks_z_tekstu(tekst, md=False, baza=None, ostrz=None):
    """Tekst (txt / md) -> bloki. md: `#`, listy, tabele `|`, cytaty `>`, obrazy `![]()`, pogrubiony wiersz = nagłówek 3.
    txt: wiersz WERSALIKAMI, numerowany („1.2 Cele”) albo krótki wiersz bez kropki, po którym stoi dłuższy akapit = nagłówek;
    puste linie dzielą akapity; linie złamane „na sztywno” (równa długość) sklejam, linie jednozdaniowe zostają osobnymi akapitami."""
    ostrz = ostrz if ostrz is not None else []
    linie = [l.rstrip() for l in tekst.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    # bloki rozdzielone pustymi liniami
    bl, cur = [], []
    w_kodzie = False
    for l in linie:
        if md and l.strip().startswith("```"):
            w_kodzie = not w_kodzie
            continue
        if not l.strip() and not w_kodzie:
            if cur:
                bl.append(cur)
                cur = []
        else:
            cur.append(l)
    if cur:
        bl.append(cur)
    dl = [len(l.strip()) for b in bl for l in b]
    mx = max(dl) if dl else 0
    bloki = []
    for bi, b in enumerate(bl):
        nast = bl[bi + 1] if bi + 1 < len(bl) else None
        _blok_tekstu(b, bloki, md, baza, mx, nast, ostrz)
    return bloki


def _blok_tekstu(b, bloki, md, baza, mx, nast, ostrz):
    pierwsza = b[0]
    # --- markdown: tabela
    if md and all(l.strip().startswith("|") for l in b) and len(b) >= 2:
        wiersze = []
        for l in b:
            kom = [c.strip() for c in l.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in kom if c):
                continue
            wiersze.append([_md_inline(c) for c in kom])
        _dodaj_tabele(wiersze, bloki)
        return
    # --- markdown: cytat
    if md and all(l.lstrip().startswith(">") for l in b):
        bloki.append(_blok("cytat", _md_inline(" ".join(l.lstrip()[1:].strip() for l in b))))
        return
    # --- wiersze bloku jedno po drugim: nagłówki #, listy, obrazy; reszta = akapit
    akap = []

    def zrzuc_akapit():
        if not akap:
            return
        linie = list(akap)
        akap.clear()
        sztywne = len(linie) >= 3 and mx >= 50 and \
            sum(1 for l in linie[:-1] if len(l.strip()) >= 0.75 * mx) >= 0.75 * (len(linie) - 1)
        czesci = [" ".join(l.strip() for l in linie)] if (sztywne or (len(linie) == 2 and len(linie[0].strip()) >= 0.85 * mx and
                                                                       linie[0].rstrip()[-1:] not in _KONIEC_ZD)) else [l.strip() for l in linie]
        for c in czesci:
            c = _md_inline(c) if md else c
            bloki.append(_blok("p", c))
    li_cur = None
    for l in b:
        s = l.strip()
        mh = _MD_NAGL.match(s) if md else None
        mo = _MD_OBRAZ.match(s) if md else None
        ml = _MD_LISTA.match(l)
        mn = _MD_NUM.match(l)
        if mh:
            zrzuc_akapit()
            li_cur = None
            n = min(3, len(mh.group(1)))
            bloki.append(_blok("h%d" % n, _md_inline(mh.group(2)), n))
        elif mo:
            zrzuc_akapit()
            li_cur = None
            sc = mo.group(1)
            sc = sc if os.path.isabs(sc) else os.path.join(baza or "", sc)
            if os.path.isfile(sc):
                bloki.append(_blok("obraz", "", 0, obraz=os.path.abspath(sc)))
            else:
                ostrz.append("Nie znalazłem obrazu z pliku .md: %s" % mo.group(1))
        elif ml and not re.match(r"^\s*[-–—]\s*$", l):
            zrzuc_akapit()
            li_cur = _blok("li", _md_inline(ml.group(1)) if md else ml.group(1), 0, num=False)
            bloki.append(li_cur)
        elif mn and (len(b) > 1 or md):
            zrzuc_akapit()
            li_cur = _blok("li", _md_inline(mn.group(2)) if md else mn.group(2), 0, num=True)
            bloki.append(li_cur)
        elif li_cur is not None and (l.startswith("  ") or l[:1] == "\t" or s[:1].islower()):
            li_cur["t"] += " " + s          # ciąg dalszy punktu listy (zawinięty wiersz)
        else:
            li_cur = None
            akap.append(l)
    # pojedynczy wiersz bloku: pogrubiony = nagłówek 3 (md); w txt heurystyki nagłówków
    if len(akap) == 1 and len(b) == 1 and not (md and _MD_NAGL.match(b[0].strip())):
        s = akap[0].strip()
        if md:
            mb = re.fullmatch(r"(\*\*|__)(.+)\1", s)
            if mb and _slow(mb.group(2)) <= 12:
                akap.clear()
                bloki.append(_blok("h3", mb.group(2).strip().rstrip(":"), 3))
                return
        else:
            poz = _naglowek_txt(s, nast)
            if poz:
                akap.clear()
                bloki.append(_blok("h%d" % poz, s.rstrip(":").strip(), poz))
                return
    zrzuc_akapit()


def _naglowek_txt(s, nast):
    """Poziom nagłówka (1-3) dla pojedynczej linii tekstu zwykłego albo 0. WERSALIKI i numeracja 1.2.3 wystarczą; zwykły krótki
    wiersz bez kropki jest nagłówkiem, gdy za nim stoi dłuższy akapit albo lista."""
    sl = _slow(s)
    if not 1 <= sl <= 10 or s[-1:] in ".!?;,…" or sum(c.isalpha() for c in s) < 3 or _BUL_RE.match(s):
        return 0
    mn = _NAGL_NUM.match(s)
    if mn and sl <= 9 and re.match(r"[A-ZĄĆĘŁŃÓŚŹŻ]", s[mn.end():mn.end() + 1] or ""):
        return min(3, mn.group(1).count(".") + 1)
    if s.upper() == s and sum(c.isalpha() for c in s) >= 4:
        return 1
    if nast:
        f = nast[0].strip()
        if _MD_LISTA.match(nast[0]) or _MD_NUM.match(nast[0]) or _slow(f) >= max(8, int(1.5 * sl)):
            return 1
    return 0



# =====================================================================================================================
# 2. STRUKTURA DOKUMENTU: sekcje, elementy, jednostki myśli
# =====================================================================================================================
CAP_SLOW = 110          # najwięcej słów tekstu na jednym slajdzie przy najgęstszym układzie (3 karty po ~35 słów)
CAP_FRAG = 4            # tyle akapitów / list (kart) najwyżej na jednym slajdzie
SLOW_NA_SLAJD = 45      # domyślnie ok. 1 slajd na tyle słów treści: 2-3 myśli = 2-3 karty (hasło + dopisek), nie jedna karta na slajd
MYSLI_NA_SLAJD = 5.0    # ...i nie rzadziej niż jeden slajd na tyle zdań (karta = hasło + dopisek = ok. 2 zdania, slajd = 2-3 karty)
KARTA_JEDNA_DO = 26     # zdania jednego akapitu: do tylu słów jedna karta,
KARTA_DWIE_DO = 48      # do tylu dwie karty obok siebie, dalej trzy (najwyżej tyle, ile zdań)
HASLO_TYTUL_SLOW = 15   # hasło z pierwszego zdania slajdu może być jego tytułem, gdy ma najwyżej tyle słów (tytuł Mindset do 3 linii)
HASLO_TYTUL_ZNAKI = 100
STATEMENT_SLOW = 22     # jedno krótkie zdanie na slajdzie sekcji > 2 slajdy (bez hasła-tytułu): zdanie na środku (statement), nie „Sekcja (7)” z kartą
RESZTA_MIN_SLOW = 4     # po zdjęciu tytułu-hasła na slajdzie ma zostać co najmniej tyle słów (inaczej zostaje „(n)”)
DLUGA_SEKCJA = 2        # sekcja rozciągnięta na więcej slajdów nie dostaje numerków „(3)”: nazwa idzie nad tytuł, tytuł = hasło slajdu
MAX_SLAJDOW = 80
MAX_ROZDZIALOW = 8      # agenda mieści 8 punktów
TABELA_WIERSZE, TABELA_KOLUMNY = 8, 6
LISTA_PORCJA = 3        # lista dzieli się między slajdy porcjami po tyle pozycji
LISTA_MAX = 8           # najwięcej punktów listy na jednym slajdzie
PODPIS_SLOW = 15        # akapit pod obrazem do 15 słów = podpis
COVER_DLUGI = 44        # tytuł dłuższy niż tyle znaków: okładka-teza (statement) zamiast cover_text
KICKER_MAX = 52         # najdłuższa etykieta nad tytułem (jedna linia, 20 cm, 14 pt wersalikami)
AGENDA_MAX = (70, 34)   # najdłuższy punkt agendy: do 4 punktów (jedna kolumna), od 5 (dwie kolumny)
PODTYTUL_SLOW = 30      # pierwszy akapit pod tytułem do 30 słów = podtytuł okładki


def _sz():
    import szablonuj
    return szablonuj


def _zdania(t):
    """Akapit -> zdania (granice jak w szablonuj.zdania). Zdanie do 3 słów albo z dwukropkiem na końcu jest początkiem następnego
    (zapowiedź nie stoi sama), krótki ogon dopisujemy do poprzedniego zdania."""
    out, znacznik = [], ""
    for z in _sz().zdania((t, None)):
        z = (znacznik + z[0]).strip()
        znacznik = ""
        mk = re.search(r"(?:^|\s)(\d{1,2}\.)$", z)     # „… są: 1.” - numer pozycji należy do następnego zdania
        if mk and _slow(z) > 1:
            z, znacznik = z[:mk.start(1)].rstrip(), mk.group(1) + " "
        if out and ((_slow(out[-1]) <= 3 and not re.match(r"\d{1,2}\.", out[-1])) or out[-1].rstrip().endswith(":")):
            out[-1] += " " + z
        else:
            out.append(z)
    if znacznik:
        out[-1] = (out[-1] + " " + znacznik).strip()
    if len(out) >= 2 and _slow(out[-1]) <= 3 and not re.match(r"\d{1,2}\.", out[-1]):
        ost = out.pop()
        out[-1] += " " + ost
    return out or [t]


def _okladka(m):
    """Okładka z modelu: {"tytul", "podtytul" | None, "kicker" (etykieta nad tytułem), "meta" (autor, data...), "zuz" (indeksy bloków
    zużytych na okładce)}. Podtytuł = akapit `podtytul` albo krótki akapit pod tytułem przed nagłówkiem; meta = blok `kv` `meta`."""
    zuz, pod, kicker, meta = set(), None, "", ""
    i = m.get("tytul_idx")
    if i is not None:
        zuz.add(i)
        kicker = m["bloki"][i].get("kicker") or ""
        b = m["bloki"][i + 1] if i + 1 < len(m["bloki"]) else None
        if b and b["typ"] == "p" and (_slow(b["t"]) <= PODTYTUL_SLOW if len(m["tytul"]) <= COVER_DLUGI else len(b["t"]) <= 68) and                 (b.get("podtytul") or any(x["typ"] in ("h1", "h2", "h3", "kv", "kpi") for x in m["bloki"][i + 2:i + 3])):
            pod = b["t"]
            zuz.add(i + 1)
        for j in range(i + 1, min(len(m["bloki"]), i + 4)):
            b = m["bloki"][j]
            if b["typ"] == "kv" and b.get("meta"):
                pary = [p for p in b["pary"] if p[1] and _slow(p[1]) <= 6]
                if any(p[0] for p in pary):
                    pary = [p for p in pary if p[0]]        # data z nagłówka strony dubluje „STAN NA”
                meta = " · ".join(p[1] for p in pary)
                zuz.add(j)
                break
            if b["typ"] not in ("p",) or j not in zuz:
                break
    return {"tytul": m["tytul"], "podtytul": pod, "kicker": kicker, "meta": meta, "zuz": zuz}


def _wagi_tabeli(head, rows):
    """Względne szerokości kolumn tabeli (jak w `table`: pierwsze 40 znaków najdłuższej komórki, potęga 0,7)."""
    out = []
    for j in range(len(head)):
        dl = max([len(head[j])] + [len(r[j]) for r in rows if j < len(r)])
        out.append(round(max(8, min(dl, 40)) ** 0.7, 2))
    return out


def _drzewo(m, uw=None):
    """Sekcje dokumentu w kolejności: {"naglowek", "poziom", "rodzic", "idx", "atomy": [...]}. Pierwsza sekcja (bez nagłówka) to treść
    przed pierwszym nagłówkiem. Atomy: p (zdania), li (pozycje), tab, obr (obrazy z podpisem), cyt."""
    zuz = _okladka(m)["zuz"]
    bl = m["bloki"]
    sek = [{"naglowek": None, "poziom": 0, "rodzic": None, "idx": None, "atomy": [], "rodzic_idx": None, "pytanie": False}]
    stos = []
    i = 0
    while i < len(bl):
        b = bl[i]
        if i in zuz:
            i += 1
            continue
        typ = b["typ"]
        cur = sek[-1]
        if typ in ("h1", "h2", "h3"):
            lv = int(typ[1])
            while stos and stos[-1][0] >= lv:
                stos.pop()
            sek.append({"naglowek": b["t"], "poziom": lv, "rodzic": stos[-1][1] if stos else None, "idx": i, "atomy": [],
                        "rodzic_idx": stos[-1][2] if stos else None, "pytanie": bool(b.get("pytanie"))})
            stos.append((lv, b["t"], len(sek) - 1))
        elif typ == "p":
            cur["atomy"].append({"k": "p", "zd": _zdania(b["t"]), "b": [i]})
        elif typ == "li":
            if cur["atomy"] and cur["atomy"][-1]["k"] == "li":
                cur["atomy"][-1]["poz"].append(b["t"])
                cur["atomy"][-1]["b"].append(i)
            else:
                cur["atomy"].append({"k": "li", "poz": [b["t"]], "b": [i], "num": bool(b.get("num"))})
        elif typ == "tabela":
            cur["atomy"].append({"k": "tab", "wiersze": b["wiersze"], "b": [i]})
        elif typ == "cytat":
            cur["atomy"].append({"k": "cyt", "t": b["t"], "b": [i]})
        elif typ == "kpi":
            cur["atomy"].append({"k": "kpi", "items": b["items"], "b": [i]})
        elif typ == "kv":
            cur["atomy"].append({"k": "kv", "pary": b["pary"], "b": [i]})
        elif typ == "obraz":
            at = {"k": "obr", "items": [{"obraz": b["obraz"], "podpis": "", "b": [i]}], "b": [i]}
            pop = cur["atomy"][-1] if cur["atomy"] else None
            if pop and pop["k"] == "p" and len(pop["zd"]) == 1 and pop["zd"][0].rstrip().endswith(":") and _slow(pop["zd"][0]) <= 20:
                cur["atomy"].pop()
                at["nota"] = pop["zd"][0]
                at["b"] = pop["b"] + at["b"]
            nast = bl[i + 1] if i + 1 < len(bl) else None
            if nast and nast["typ"] == "p" and _slow(nast["t"]) <= PODPIS_SLOW and (i + 1) not in zuz:
                at["items"][0]["podpis"] = nast["t"]
                at["items"][0]["b"].append(i + 1)
                at["b"].append(i + 1)
                i += 1
            if cur["atomy"] and cur["atomy"][-1]["k"] == "obr" and len(cur["atomy"][-1]["items"]) < 3 and \
                    not at["items"][0]["podpis"] == "" and False:
                pass
            if cur["atomy"] and cur["atomy"][-1]["k"] == "obr" and len(cur["atomy"][-1]["items"]) < 3 and not at.get("nota"):
                cur["atomy"][-1]["items"] += at["items"]
                cur["atomy"][-1]["b"] += at["b"]
            else:
                cur["atomy"].append(at)
        i += 1
    return sek


def _slow_atomu(a):
    if a["k"] == "p":
        return sum(_slow(z) for z in a["zd"])
    if a["k"] == "li":
        return sum(_slow(x) for x in a["poz"])
    if a["k"] == "cyt":
        return _slow(a["t"])
    if a["k"] == "tab":
        return sum(_slow(c) for w in a["wiersze"] for c in w)
    if a["k"] == "kpi":
        return sum(_slow(it["value"]) + _slow(it["label"]) for it in a["items"])
    if a["k"] == "kv":
        return sum(_slow(p[0]) + _slow(p[1]) for p in a["pary"])
    return 0


def _kandydaci_rozdzialow(sek):
    """Indeksy sekcji, które mogą być rozdziałem: mają nagłówek i treść (własną albo w podsekcjach)."""
    out = []
    for i, s in enumerate(sek):
        if not s["naglowek"]:
            continue
        j = i
        tresc = bool(s["atomy"])
        while not tresc and j + 1 < len(sek) and sek[j + 1]["poziom"] > s["poziom"]:
            j += 1
            tresc = bool(sek[j]["atomy"])
        if tresc:
            out.append(i)
    return out


def _slowa_poddrzewa(sek, i):
    s = sek[i]
    w = sum(_slow_atomu(a) for a in s["atomy"])
    j = i + 1
    while j < len(sek) and sek[j]["poziom"] > s["poziom"]:
        w += sum(_slow_atomu(a) for a in sek[j]["atomy"])
        j += 1
    return w


def _rozdzialy_domyslnie(sek, slajdy_domyslnie):
    """Przekładki domyślnie tylko wtedy, gdy rozdział ma średnio >= 3 slajdy treści (inaczej przekładki zjadają prezentację)."""
    if slajdy_domyslnie < 9:
        return 0
    kand = _kandydaci_rozdzialow(sek)
    for lv in (1, 2, 3):
        ile = [i for i in kand if sek[i]["poziom"] == lv]
        if 2 <= len(ile) <= MAX_ROZDZIALOW and slajdy_domyslnie >= 3 * len(ile):
            return len(ile)
    return 0


# =====================================================================================================================
# 3. PLAN: ROZDZIAŁY, NOŚNIKI TREŚCI, BUDŻET SLAJDÓW (21.10.2026)
# =====================================================================================================================
# Slajd pokazuje NOŚNIK treści (liczby, tabela, lista jako hasła, pary etykieta: wartość, karty, FAQ, akapit jako hasło z dopiskiem);
# pełny tekst dokumentu idzie do notatek prelegenta. Suwak = liczba slajdów z treścią; nośniki wchodzą według rangi.
ROZDZIAL_MIN_SLOW = 40    # sekcja najwyższego poziomu krótsza niż tyle słów nie jest osobnym rozdziałem (dokleja się do sąsiada)
_RANGA0 = re.compile(r"decyz|wniosk|rekomend|podsumow|\bplan|nast[eę]pne kroki", re.I)   # rozdział dla zarządu: zawsze na slajdzie
PAS_MAX = 12              # pas-wniosek (zielony) do tylu słów; dłuższe zdanie idzie do notatek
ZIELONA_MAX = 10          # zielona karta z jednym hasłem do tylu słów; dłuższe = kremowa karta z hasłem i dopiskiem
SLAJD_MAX_SLOW = 60       # bramka: tyle słów najwyżej na jednym slajdzie treści
TAB_KOL, TAB_WIERSZY = 3, 6                  # tabela „Standardowo”: kolumny i wiersze na slajdzie
TAB_KOL_SZCZ, TAB_WIERSZY_SZCZ = 4, 8        # tabela „Szczegółowo”
KOMORKA_SLOW = 4          # komórka tabeli na slajdzie: do tylu słów (pierwszy człon), reszta w notatkach
KPI_MAX, LISTA_MAX_POZ, FAQ_NA_SLAJD, KARTY_MAX, KV_MAX = 4, 6, 5, 4, 8
HASLO_POZ = 12            # pozycja listy / hasło karty: pierwszy człon do tylu słów
HASLO_KROTKIE = 6         # hasło kafla: pierwsza fraza do tylu słów (reszta = dopisek Lato)
KOMORKA_FRAZA = 7         # komórka tabeli: pierwsza fraza do tylu słów; dłuższa = komórka w notatkach
DOPISEK_SLOW = 25         # dopisek pod hasłem do tylu słów (karta akapitu)
DOPISEK_KAFLA = 16        # dopisek w kaflu listy do tylu słów (reszta w notatkach)
RANGA = {"kpi": 1, "tab": 2, "lista-liczby": 2, "obr": 2, "siatka": 2, "kv": 3, "lista": 3, "kroki": 3, "karty": 3, "cyt": 3, "faq": 4, "tekst": 5}


def _slow_sek(sek, i):
    return sum(_slow_atomu(a) for a in sek[i]["atomy"])


def _rozdzialy(sek):
    """Rozdziały = sekcje najwyższego poziomu z nagłówkiem; krótsze niż ROZDZIAL_MIN_SLOW doklejają się: sam wstęp (tylko akapity) do
    następnego, inne do poprzedniego. [{"sekcje": [indeksy], "start": indeks sekcji z nagłówkiem | None}] w kolejności dokumentu."""
    kand = _kandydaci_rozdzialow(sek)
    if not kand:
        return [{"sekcje": list(range(len(sek))), "start": next((i for i in range(len(sek)) if sek[i]["naglowek"]), None)}]
    lv = min(sek[i]["poziom"] for i in kand)
    starty = [i for i in range(len(sek)) if sek[i]["naglowek"] and sek[i]["poziom"] == lv]
    gr = [list(range(0, starty[0]))] if starty[0] > 0 else []
    gr += [list(range(a, b)) for a, b in zip(starty, starty[1:] + [len(sek)])]
    out, pend = [], []
    for g in gr:
        w = sum(_slow_sek(sek, i) for i in g)
        tylko_p = all(a["k"] == "p" for i in g for a in sek[i]["atomy"])
        if w < ROZDZIAL_MIN_SLOW and (tylko_p or not out):
            pend += g
        elif w < ROZDZIAL_MIN_SLOW:
            out[-1] += g
        else:
            out.append(pend + g)
            pend = []
    if pend:
        if out and sum(_slow_sek(sek, i) for i in pend) < ROZDZIAL_MIN_SLOW:
            out[-1] += pend
        else:
            out.append(pend)
    return [{"sekcje": g, "start": next((i for i in g if sek[i]["naglowek"]), None)} for g in out]


def _nowy(k, si, ri, atomy, sek):
    b = sorted({i for a in atomy for i in a["b"]})
    return {"k": k, "sek": si, "roz": ri, "tytul": sek[si]["naglowek"], "atomy": list(atomy), "b": b, "wstep": [], "po": [],
            "ranga": RANGA[k], "extra": 0, "wybrany": 0, "pominiete": []}


def _liczby_w(poz):
    sz = _sz()
    return sum(1 for x in poz if sz.liczba_bohater((x, None)))


def _grupa_podsekcji(sek, secs, i):
    """Od sekcji secs[i]: ciąg sąsiednich podsekcji tego samego poziomu (głębszego niż rozdział) z <= 2 atomami tekstu każda."""
    s = sek[secs[i]]
    if not s["naglowek"] or not s["atomy"] or len(s["atomy"]) > 2 or any(a["k"] != "p" for a in s["atomy"]):
        return [i]
    j = i
    while j + 1 < len(secs):
        t = sek[secs[j + 1]]
        if not (t["naglowek"] and t["poziom"] == s["poziom"] and t["rodzic"] == s["rodzic"] and 1 <= len(t["atomy"]) <= 2 and
                all(a["k"] == "p" for a in t["atomy"]) and bool(t.get("pytanie")) == bool(s.get("pytanie"))):
            break
        j += 1
    return list(range(i, j + 1))


def _grupy_kv(sek):
    """Grupy >= 3 sąsiednich sekcji tego samego poziomu z blokiem `kv` o >= 2 wspólnych etykietach (karty programów), także przez
    nagłówek rozdziału między nimi („Karty programów (cd.)”). {indeks pierwszej sekcji: ([indeksy sekcji], [wspólne etykiety])}."""
    def kv(si):
        return next((a for a in sek[si]["atomy"] if a["k"] == "kv"), None)
    out, i = {}, 0
    while i < len(sek):
        s = sek[i]
        if not s["naglowek"] or kv(i) is None:
            i += 1
            continue
        idx, j = [i], i + 1
        etyk0 = {p[0] for p in kv(i)["pary"]}
        while j < len(sek):
            t = sek[j]
            if t["naglowek"] and t["poziom"] == s["poziom"] and kv(j) is not None:
                if len(etyk0 & {p[0] for p in kv(j)["pary"]}) < 2:
                    break           # inna karta (inne etykiety) kończy siatkę
                idx.append(j)
            elif t["poziom"] < s["poziom"] and all(a["k"] == "p" for a in t["atomy"]):
                pass            # nagłówek rozdziału z samym wstępem: karty ciągną się dalej
            else:
                break
            j += 1
        etyk = [p[0] for p in kv(i)["pary"]]
        wspolne = [e for e in etyk if all(any(p[0] == e for p in kv(x)["pary"]) for x in idx)]
        if len(idx) >= 3 and len(wspolne) >= 2:
            out[i] = (idx, wspolne)
            i = idx[-1] + 1
        else:
            i += 1
    return out


def _nosniki(sek, rozdz):
    """Nośniki treści w kolejności dokumentu. Akapity przed pierwszym nośnikiem sekcji = wstęp (band / notatki), po nim = komentarz."""
    out = []
    grupy = _grupy_kv(sek)
    zuzyte = set()
    for ri, r in enumerate(rozdz):
        secs = r["sekcje"]
        i = 0
        while i < len(secs):
            si = secs[i]
            s = sek[si]
            if si in zuzyte:
                i += 1
                continue
            if si in grupy:
                idx, etyk = grupy[si]
                atomy, reszta, karty = [], [], []
                for x in idx:
                    kvat = next(a for a in sek[x]["atomy"] if a["k"] == "kv")
                    karty.append((sek[x]["naglowek"], [(e, next((p[1] for p in kvat["pary"] if p[0] == e), "")) for e in etyk]))
                    atomy.append(kvat)
                    reszta += [a for a in sek[x]["atomy"] if a is not kvat]
                    zuzyte.add(x)
                n = _nowy("siatka", si, ri, atomy, sek)
                n["karty"], n["po"] = karty, reszta
                n["tytul"] = sek[s["rodzic_idx"]]["naglowek"] if s.get("rodzic_idx") is not None else s["naglowek"]
                n["b"] = sorted(set(n["b"]) | {i2 for a in reszta for i2 in a["b"]} | {sek[x]["idx"] for x in idx})
                out.append(n)
                i += 1
                continue
            idx = _grupa_podsekcji(sek, secs, i)
            if len(idx) >= 2 and s["poziom"] > sek[r["start"]]["poziom"] if r["start"] is not None else False:
                k = "faq" if s.get("pytanie") else "karty"
                atomy = [a for x in idx for a in sek[secs[x]]["atomy"]]
                n = _nowy(k, si, ri, atomy, sek)
                n["karty"] = [(sek[secs[x]]["naglowek"], " ".join(z for a in sek[secs[x]]["atomy"] for z in a["zd"])) for x in idx]
                pop = sek[secs[i - 1]] if i > 0 else None     # pusty nagłówek tuż przed grupą („Decyzje zarządu” nad 1. 2. 3.) = jej tytuł
                if pop is not None and pop["naglowek"] and not pop["atomy"] and pop["poziom"] >= sek[r["start"]]["poziom"]:
                    n["tytul"] = pop["naglowek"]
                    n["b"] = sorted(set(n["b"]) | {pop["idx"]})
                else:
                    n["tytul"] = sek[s["rodzic_idx"]]["naglowek"] if s.get("rodzic_idx") is not None else s["naglowek"]
                n["b"] = sorted(set(n["b"]) | {sek[secs[x]]["idx"] for x in idx})
                out.append(n)
                i = idx[-1] + 1
                continue
            wst, wsek = [], []
            for a in s["atomy"]:
                if a["k"] == "p" or (a["k"] == "kv" and len(a["pary"]) < 3):
                    if a["k"] == "kv":
                        a = {"k": "p", "zd": ["%s: %s" % tuple(p) if p[0] else p[1] for p in a["pary"]], "b": a["b"]}
                    (wsek[-1]["po"] if wsek else wst).append(a)
                    continue
                if a["k"] == "li":
                    k = "kroki" if a.get("num") and 2 <= len(a["poz"]) <= 5 else ("lista-liczby" if _liczby_w(a["poz"]) >= 2 else "lista")
                else:
                    k = a["k"]
                n = _nowy(k, si, ri, [a], sek)
                if k == "tab":
                    n["ksztalt"], n["kol_wart"] = _ksztalt_tabeli(a["wiersze"])
                wsek.append(n)
            if wsek:
                wsek[0]["wstep"] = wst
                out += wsek
            elif wst:
                out.append(_nowy("tekst", si, ri, wst, sek))
            i += 1
    for n in out:
        n["b"] = sorted(set(n["b"]) | {i for a in n["wstep"] + n["po"] for i in a["b"]} | ({sek[n["sek"]]["idx"]} if sek[n["sek"]]["idx"] is not None else set()))
    return out


def _jednostki_planu(nos, szcz):
    """Jednostki budżetu: slajd bazowy każdego nośnika + slajdy dodatkowe (dalsze wiersze tabeli, akapity, pary FAQ, karty)."""
    u = []
    for i, n in enumerate(nos):
        u.append((n, 0))
        if n["k"] == "tab" and n.get("ksztalt", "tab") == "tab":
            w = len(n["atomy"][0]["wiersze"]) - 1
            ex = max(0, -(-w // TAB_WIERSZY_SZCZ) - 1)
        elif n["k"] == "faq":
            ex = max(0, -(-len(n["karty"]) // FAQ_NA_SLAJD) - 1)
        elif n["k"] == "karty":
            ex = max(0, -(-len(n["karty"]) // KARTY_MAX) - 1)
        elif n["k"] == "tekst":
            ex = len(n["atomy"]) - 1
        else:
            ex = 0
        n["dod"] = [a for a in n["wstep"] + n["po"] if a["k"] == "p" and _slow_atomu(a) >= 12] if n["k"] != "tekst" else []
        n["wlasne"] = ex
        ex += len(n["dod"])
        n["extra_max"] = ex
        u += [(n, e) for e in range(1, ex + 1)]
    return u


def plan(m, N=None, sek=None):
    """Plan prezentacji: rozdziały, nośniki, zakres suwaka (min = najlepszy nośnik każdego rozdziału + nośniki rangi 0; domyślnie = nośniki
    rangi <= 3; max = wszystkie nośniki i ich dalsze części) oraz wybór N jednostek według rangi. Oznacza nośniki: `wybrany` = liczba
    slajdów, `pominiete` = nośniki, których tekst idzie do notatek tego slajdu."""
    sek = sek if sek is not None else _drzewo(m)
    rozdz = _rozdzialy(sek)
    nos = _nosniki(sek, rozdz)
    for n in nos:
        n["wybrany"], n["pominiete"] = 0, []
        roz_t = sek[rozdz[n["roz"]]["start"]]["naglowek"] if rozdz[n["roz"]]["start"] is not None else ""
        if n["k"] != "faq" and (_RANGA0.search(n["tytul"] or "") or (n["k"] != "tekst" and _RANGA0.search(roz_t or ""))):
            n["ranga"] = 0
        elif n["k"] == "tekst" and all(x["k"] == "tekst" for x in nos if x["roz"] == n["roz"]):
            n["ranga"] = 2        # rozdział z samego tekstu: jego akapity pokazują się „Standardowo”
        else:
            n["ranga"] = RANGA[n["k"]]
    for ri in range(len(rozdz)):
        w = [n for n in nos if n["roz"] == ri and n["k"] != "faq"]    # FAQ nigdy nie jest wymuszone (ranga 4)
        if w:
            best = min(w, key=lambda n: (n["ranga"], nos.index(n)))
            best["wymuszony"] = True
            if ri == len(rozdz) - 1:
                best["ranga"] = 0
    for n in nos:
        if n["ranga"] == 0:
            n["wymuszony"] = True
    units = _jednostki_planu(nos, False)
    kolej = sorted(range(len(units)), key=lambda i: (0 if (units[i][1] == 0 and units[i][0].get("wymuszony")) else 1,
                                                     units[i][0]["ranga"] if units[i][1] == 0 else 6, nos.index(units[i][0]), units[i][1]))
    mn = sum(1 for n in nos if n.get("wymuszony"))
    dom = sum(1 for n in nos if n.get("wymuszony") or n["ranga"] <= 2)
    mx = min(MAX_SLAJDOW, len(units))
    mn, dom = min(mn, mx), min(max(dom, mn), mx)
    N = dom if N is None else max(mn, min(mx, int(N)))
    for i in kolej[:N]:
        units[i][0]["wybrany"] += 1
    prev = None
    for n in nos:
        if n["wybrany"]:
            prev = n
        elif prev is not None:
            prev["pominiete"].append(n)
        else:
            nast = next((x for x in nos if x["wybrany"]), None)
            if nast is not None:
                nast["pominiete"].append(n)
    return {"sek": sek, "rozdzialy": rozdz, "nosniki": nos, "min": mn, "dom": dom, "max": mx, "N": N, "szczegolowo": N > dom,
            "na_slajdach": _udzial_na_slajdach(nos, N > dom)}


ZAWIESZKI = {"z", "w", "i", "o", "a", "u", "na", "do", "od", "po", "za", "ze", "we", "oraz", "lub", "albo", "ani", "czy", "że", "bo", "dla",
             "nie", "jak", "bez", "pod", "nad", "przez", "przy", "jako", "który", "która", "które", "których", "też", "to", "jest", "są", "się", "ich",
             "tylko", "także", "oraz", "między", "wobec", "przed", "ponad", "ok.", "np.", "tj."}


def _konc_ok(toks):
    """Tekst na slajdzie nie kończy się spójnikiem, przyimkiem ani otwartym nawiasem."""
    if not toks:
        return False
    ost = toks[-1].strip().rstrip(",;:–—-")
    calosc = "".join(toks)
    return bool(ost) and ost.lower() not in ZAWIESZKI and not ost.endswith("(") and calosc.count("(") <= calosc.count(")")


def _fraza(t, maks, nr=0, min_sl=1):
    """Pierwsza pełna fraza tekstu (do przecinka / średnika / dwukropka / myślnika / końca zdania) o najwyżej `maks` słowach; `nr` = weź
    frazę o tyle granic dalej (dłuższy człon, gdy krótszy się powtarza). None, gdy pierwsza fraza jest za długa. Fraza nie kończy się
    spójnikiem, przyimkiem ani otwartym nawiasem (granica przesuwa się na poprzednie słowo albo fraza odpada)."""
    t = " ".join(t.split())
    toks = t.split()
    if not toks:
        return None
    abbr = _sz().ABBR
    gr = [i for i in range(1, len(toks)) if toks[i - 1][-1:] in ",;:" or toks[i] in ("–", "—", "-") or
          (toks[i - 1][-1:] in ".!?…" and toks[i][:1].isupper() and len(toks[i - 1]) > 2 and toks[i - 1].lower() not in abbr)]
    gr = [g for g in gr if g >= min_sl] + [len(toks)]       # fraza nie krótsza niż min_sl słów („Oprogramowanie,” to nie fraza)
    k = min(nr, len(gr) - 1)
    out = toks[:gr[k]]
    while out and not _konc_ok(out):
        out = out[:-1]
    if not out or len(out) > (maks + 2 if len(out) == len(toks) else maks):     # cały krótki tekst wolno o 2 słowa dłuższy
        return None
    return " ".join(out).rstrip(",;:–—- ").strip()


def _czlon(t, maks):
    """Pierwszy człon tekstu do `maks` słów: pełna fraza (`_fraza`), a gdy jest za długa - pierwsze słowa bez zawieszki na końcu."""
    f = _fraza(t, maks, min_sl=3)      # fraza krótsza niż 3 słowa („Podejście:”) to nie człon
    if f is not None:
        return f
    toks = " ".join(t.split()).split()
    # bez granicy interpunkcyjnej: tnij przed ostatnim przyimkiem / spójnikiem w zasięgu („zrzuty ekranów porównywane | z projektem”)
    przed = [i for i in range(2, min(len(toks), maks + 1)) if toks[i].lower() in ZAWIESZKI]
    out = toks[:przed[-1]] if przed else toks[:maks]
    while len(out) > 2 and not _konc_ok(out):
        out.pop()
    return " ".join(out).rstrip(",;:–—- ")


def _haslo_poz(t, maks=HASLO_POZ):
    """Pozycja listy / karta -> (hasło, dopisek): hasło = pierwsza fraza do ~6 słów (`_fraza`), gdy jej nie ma - pierwszy człon
    (`szablonuj.haslo_cut`); dopisek = reszta pierwszego zdania (+ drugie), do DOPISEK_SLOW słów; None, gdy nic nie zostaje."""
    sz = _sz()
    zd = _zdania(t)
    z0 = " ".join(zd[0].split())
    h = _fraza(z0, HASLO_KROTKIE, min_sl=2)
    if h is None:
        hh, _r = sz.haslo_cut((z0, None))
        h = _czlon(hh[0], maks)
    if _slow(z0) <= HASLO_KROTKIE and _slow(h) >= _slow(z0) - 1:
        h, reszta = z0.rstrip(".").strip() if z0.count(".") == 1 and z0.endswith(".") else z0, " ".join(zd[1:2])
    else:
        hw = _slow(h)
        reszta = " ".join(z0.split()[hw:] + zd[1:2]).lstrip(",;:–—- ")
    reszta = " ".join(reszta.split())
    if reszta and _slow(reszta) > DOPISEK_KAFLA:
        reszta = _czlon(reszta, DOPISEK_KAFLA)
    return h, (reszta or None)


_DATA = re.compile(r"\b(\d{1,2}[./]\d{4}|\d{4}|stycz|lut|mar|kwie|maj|czerw|lip|sierp|wrze|paźdz|listop|grud)", re.I)
_TAKNIE = {"tak", "nie", "częściowo", "czesciowo", "✓", "✗", "x", "-"}


def _komorka(t):
    """Komórka na slajdzie: pierwsza fraza do KOMORKA_FRAZA słów albo None (brak pełnej frazy: na slajd idzie krótsze ujęcie `_czlon`,
    a kolumna z wieloma takimi komórkami znika)."""
    t = " ".join(str(t).split())
    if not t:
        return None
    if _slow(t) <= KOMORKA_SLOW:
        return t if _konc_ok(t.split()) or _slow(t) <= 1 else _czlon(t, KOMORKA_SLOW)
    return _fraza(t, KOMORKA_FRAZA, min_sl=2)


def _ksztalt_tabeli(wiersze):
    """Kształt tabeli -> pojemnik: „kpi” (kolumna liczb / krótkich wartości, <= 6 wierszy), „czas” (kolumna dat), „taknie” (kolumna
    tak / nie), „kv” (2 kolumny krótkich wartości), „tab” (>= 3 sensowne kolumny). Zwraca (kształt, numer kolumny wartości)."""
    head, rows = wiersze[0], wiersze[1:]
    n = len(head)
    if not rows or n < 2 or n > 3:
        return "tab", None          # >= 4 kolumn: tabela zostaje tabelą

    def kol(j):
        return [r[j] if j < len(r) else "" for r in rows]
    for j in range(1, n):
        c = [x for x in kol(j) if x]
        if len(rows) <= 8 and c and sum(1 for x in c if x.strip().lower().rstrip(".") in _TAKNIE) >= 0.6 * len(rows):
            return "taknie", j
    for j in range(1, n):
        c = [x for x in kol(j) if x]
        if len(rows) <= 6 and c and sum(1 for x in c if _slow(x) <= 4 and re.search(r"\d", x) and not _DATA.search(x)) >= 0.6 * len(rows):
            return "kpi", j         # kolumna liczb (nie dat)
    if n == 2 and len(rows) <= 6:
        c = [x for x in kol(1) if x]
        if c and sum(1 for x in c if _DATA.search(x)) >= 0.6 * len(rows):
            return "czas", 1
        if all(_slow(x) <= 8 for x in c):
            return "kv", 1
    return "tab", None


def _tab_skrot(wiersze, szcz, czesc=0):
    """Tabela na slajd: kolumny = pierwsza (nazwa) + druga + najkrótsze z pozostałych do TAB_KOL (TAB_KOL_SZCZ); komórka = pierwsza fraza
    do KOMORKA_FRAZA słów (`_komorka`); kolumna, w której ponad 1/3 komórek nie ma takiej frazy, znika (zostaje w notatkach); dwa wiersze
    o tej samej nazwie dostają dłuższy człon. Wiersze porcji `czesc`. Zwraca (head, rows)."""
    kol_max, wi_max = (TAB_KOL_SZCZ, TAB_WIERSZY_SZCZ) if szcz else (TAB_KOL, TAB_WIERSZY)
    head, rows = wiersze[0], wiersze[1:]
    n = len(head)
    kom = [[_komorka(r[j]) if j < len(r) else "" for j in range(n)] for r in rows]
    zle = [sum(1 for r in kom if r[j] is None) for j in range(n)]
    ok = [j for j in range(n) if j == 0 or zle[j] * 3 <= len(rows)]
    dl = [max([_slow(head[j])] + [_slow(r[j] or "") for r in kom]) for j in range(n)]
    reszta = [j for j in ok if j >= 2]
    wyb = ok if len(ok) <= kol_max else sorted([j for j in ok if j < 2] + sorted(reszta, key=lambda j: (dl[j], j))[:kol_max - len([j for j in ok if j < 2])])
    porcja = list(range(czesc * wi_max, min(len(rows), (czesc + 1) * wi_max)))
    out = [[(kom[i][j] if kom[i][j] is not None else (_czlon(rows[i][j], KOMORKA_FRAZA) if j < len(rows[i]) else "")) for j in wyb] for i in porcja]
    for a in range(len(out)):          # ta sama nazwa w dwóch wierszach: dłuższy człon
        for b in range(a):
            if out[a] and out[a][0] and out[a][0] == out[b][0]:
                for i2, k in ((porcja[a], a), (porcja[b], b)):
                    f = _fraza(rows[i2][0], HASLO_POZ, nr=1)
                    if f and f != out[k][0]:
                        out[k][0] = f
    return [head[j] for j in wyb], out


def _udzial_na_slajdach(nos, szcz):
    """Szacunek: ile słów dokumentu widać na slajdach (bez pomiaru układu) / wszystkie słowa nośników."""
    razem = pokaz = 0
    for n in nos:
        w = sum(_slow_atomu(a) for a in n["atomy"] + n["wstep"] + n["po"])
        razem += w
        if not n["wybrany"]:
            continue
        k = n["k"]
        if k == "kpi":
            pokaz += sum(_slow(it["value"]) + _slow(it["label"]) for it in n["atomy"][0]["items"][:KPI_MAX])
        elif k == "tab" and n.get("ksztalt", "tab") == "tab":
            for c in range(n["wybrany"]):
                h, r = _tab_skrot(n["atomy"][0]["wiersze"], szcz, c)
                pokaz += sum(_slow(x) for x in h) + sum(_slow(x) for row in r for x in row)
        elif k == "tab":
            pokaz += sum(min(HASLO_KROTKIE, _slow(r[0])) + min(6, _slow(r[n["kol_wart"]]) if n["kol_wart"] is not None and n["kol_wart"] < len(r) else 0)
                         for r in n["atomy"][0]["wiersze"][1:7])
        elif k == "siatka":
            pokaz += sum(_slow(h) + sum(_slow(e) + min(6, _slow(v)) for e, v in kv) for h, kv in n["karty"])
        elif k == "kv":
            pokaz += sum(_slow(p[0]) + min(6, _slow(p[1])) for p in n["atomy"][0]["pary"][:KV_MAX])
        elif k in ("lista", "lista-liczby", "kroki"):
            pokaz += sum(min(HASLO_POZ, _slow(x)) for x in n["atomy"][0]["poz"][:LISTA_MAX_POZ])
        elif k in ("faq", "karty"):
            na = FAQ_NA_SLAJD if k == "faq" else KARTY_MAX
            pokaz += sum(_slow(h) + min(HASLO_POZ, _slow(t)) for h, t in n["karty"][:na * n["wybrany"]])
        elif k == "tekst":
            pokaz += sum(min(HASLO_POZ + DOPISEK_SLOW, _slow_atomu(a)) for a in n["atomy"][:n["wybrany"]])
        else:
            pokaz += w
        if n["wstep"] or n["po"]:
            pokaz += min(PAS_MAX, 0)
    return int(round(100.0 * pokaz / razem)) if razem else 100


def _rozdzialy_domyslnie(pl):
    """Przekładki domyślnie tylko wtedy, gdy rozdział ma średnio >= 3 slajdy treści (inaczej przekładki zjadają prezentację)."""
    n = sum(1 for r in pl["rozdzialy"] if r["start"] is not None)
    return n if 2 <= n <= MAX_ROZDZIALOW and pl["dom"] >= 9 and pl["dom"] >= 3 * n else 0


def statystyka(m):
    """Zakresy suwaków liczone Z DOKUMENTU (bez pomiaru układu - natychmiast). `slajdy_*` = slajdy Z TREŚCIĄ (okładka, agenda, przekładki
    i zakończenie dochodzą): min = jeden nośnik na rozdział (+ rozdziały dla zarządu: decyzje, plan, wnioski); domyślnie = każda liczba,
    tabela, lista i para etykieta: wartość; max = także akapity, dalsze wiersze tabel i pytania FAQ. `na_slajdach` = ile procent słów
    dokumentu widać na slajdach przy min / domyślnie / max (reszta w notatkach prelegenta). `rozdzialy_max` = ile rozdziałów może
    dostać slajd tytułowy (najwyżej %d; 0 bez nagłówków)."""
    sek = _drzewo(m)
    pl = plan(m, None, sek)
    nag = {1: 0, 2: 0, 3: 0}
    for i, b in enumerate(m["bloki"]):
        if b["typ"] in ("h1", "h2", "h3") and i != m.get("tytul_idx"):
            nag[int(b["typ"][1])] += 1
    slowa = sum(_slowa_bloku(b) for b in m["bloki"])
    return {"slowa": slowa, "akapity": sum(1 for b in m["bloki"] if b["typ"] in ("p", "li", "cytat")), "naglowki": nag,
            "tabele": sum(1 for b in m["bloki"] if b["typ"] == "tabela"), "obrazy": sum(1 for b in m["bloki"] if b["typ"] == "obraz"),
            "slajdy_min": pl["min"], "slajdy_max": pl["max"], "slajdy_domyslnie": pl["dom"],
            "rozdzialy_max": min(MAX_ROZDZIALOW, sum(1 for r in pl["rozdzialy"] if r["start"] is not None)),
            "rozdzialy_domyslnie": _rozdzialy_domyslnie(pl), "slajdy_stale": 0, "nosniki": len(pl["nosniki"]),
            "na_slajdach": {"min": plan(m, pl["min"], sek)["na_slajdach"], "domyslnie": pl["na_slajdach"],
                            "max": plan(m, pl["max"], sek)["na_slajdach"]}}


statystyka.__doc__ = statystyka.__doc__ % MAX_ROZDZIALOW


def _slowa_bloku(b):
    if b["typ"] == "tabela":
        return sum(_slow(c) for w in b["wiersze"] for c in w)
    if b["typ"] == "kpi":
        return sum(_slow(it["value"]) + _slow(it["label"]) for it in b["items"])
    if b["typ"] == "kv":
        return sum(_slow(p[0]) + _slow(p[1]) for p in b["pary"])
    if b["typ"] == "obraz":
        return 0
    return _slow(b["t"])


@contextlib.contextmanager
def _pomiar_ukladu(bd):
    """Na czas `zloz` pamięć podręczna `build_dk.uklad_layout` (klucz: JSON slajdu): `rozloz`, `ocena` i kandydaci liczą te same układy
    wiele razy. Po `zloz` stara funkcja wraca (budowa pliku liczy układ za każdym razem od nowa)."""
    orig, cache = bd.uklad_layout, {}

    def pamietaj(sp):
        k = json.dumps(sp, sort_keys=True, ensure_ascii=False, default=str)
        if k not in cache:
            cache[k] = orig(sp)
        return cache[k]
    bd.uklad_layout = pamietaj
    try:
        yield
    finally:
        bd.uklad_layout = orig


class _Ctx:
    """Stan jednego `zloz`: moduły, uwagi, decyzje szablonowania, warianty (do podmiany po renderze), mapa bloków."""

    def __init__(self):
        import build_dk
        import szablonuj
        self.bd, self.sz = build_dk, szablonuj
        szablonuj.przyspiesz_pomiar(build_dk)       # pamięć podręczna pomiaru tekstu (wspólna z konwersją)
        self.uwagi, self.decyzje, self.warianty = [], [], []
        self.wlasne = set()   # id slajdów, których tytuł i etykieta ustaliły się przy składaniu (tytuł z hasła) - `_zloz` ich nie rusza
        self.nr = 0           # numer roboczy slajdu treści (pole `zrodlo`)
        self.kody = {}        # zrodlo -> kody usterek wybranego układu (szablonuj.ocena)

    def nowy_nr(self):
        self.nr += 1
        return self.nr


_ZLE = {"NIE_MIESCI_SIE", "HASLO_MALE", "DOPISEK_MALY"}


def _usterki(ctx, sl):
    oc = ctx.sz.ocena(sl, ctx.bd)
    return {u["kod"] for u in oc["usterki"]}, oc


def _wybierz_uklad(ctx, sp, gotowy=False):
    """`_wybierz_uklad0` + zapamiętanie usterek wybranego układu (do uwag dla człowieka)."""
    w = _wybierz_uklad0(ctx, sp, gotowy)
    if w is not None:
        ctx.kody[sp["zrodlo"]] = _usterki(ctx, w[0])[0]
    return w


def _wybierz_uklad0(ctx, sp, gotowy=False):
    """Slajd `uklad` z gołymi wierszami -> (slajd, decyzje, rekord kandydatów | None) albo None, gdy się nie mieści czytelnym pismem.
    Najpierw reguły S1-S15 (`szablonuj.stosuj`); gdy wynik ma usterki, wybór z kandydatów z pomiaru (`kandydaci` + `wybierz`)."""
    sz, bd = ctx.sz, ctx.bd
    nr = sp["zrodlo"]
    if not gotowy:
        sl, dec = sz.stosuj(sp, nr)
        if sl is not None:
            # kandydaci zawsze (także przy czystym układzie): po renderze `popraw_po_renderze` ma z czego wybrać inny wariant
            kand = sz.kandydaci(sp, nr, bd, lambda s: not (_usterki(ctx, s)[0] & _ZLE))
            w = sz.wybierz(kand) if kand else None
            if w is not None:
                return kand[w]["slajd"], kand[w]["decyzje"], sz.zapis_wariantow(kand, w, nr, 0)
            sl = sz.rozloz(sl, bd)
            if not (_usterki(ctx, sl)[0] & _ZLE):
                return sl, dec, None
    raw = sz.rozloz(dict(sp), bd)
    kody, _oc = _usterki(ctx, raw)
    if not (kody & _ZLE):
        return raw, [], None
    return None


def _wzor(ctx, id_):
    k = ctx.sz.katalog().get(id_)
    return dict(k) if k else None


# --- wiersze z fragmentów --------------------------------------------------------------------------------------------
def _karta_p(sz, tekst):
    return sz.k_karta(sz.blok("p", (tekst, None), align="l"))


def _karta_li(sz, poz):
    return sz.k_karta(*[{"k": "li", "t": x, "icon": "check"} for x in poz])


def _hero_i_haslo(sz, h, liczba):
    """(hero, hasło) dla zdania z liczbą-bohaterem. K2 (13.10): liczba znika z hasła tylko wtedy, gdy po jej zdjęciu zostaje domknięta fraza
    (`szablonuj.bez_liczby`: „o 7,8%” przechodzi do hero, „80% - grupa 1 jak powyżej” -> „Grupa 1 jak powyżej”); inaczej hasło zostaje
    z liczbą, a hero się powtarza."""
    r = sz.bez_liczby(h, liczba, zdejmij=True)
    if r:
        return {"k": "hero", "t": r[2], "zast": True}, sz.blok("lead", (r[0], r[1]), color="ink")
    return {"k": "hero", "t": liczba}, sz.blok("lead", h, color="ink")


def _liczby(sz, poz):
    return any(sz.liczba_bohater((x, None)) for x in poz)


def _wiersze_lista(ctx, fr):
    """Lista -> układ zależny od kształtu: 1 pozycja = myśl; 2-6 krótkich haseł = kafle z ikonami (S4); lista numerowana 2-5 pozycji =
    kroki (numer w kółku-bohaterze); 2-4 dłuższe pozycje = karty z hasłem i dopiskiem; 5-6 haseł do 14 słów = siatka kafli; reszta
    = jedna karta z punktami."""
    sz = ctx.sz
    poz = fr["t"]
    n = len(poz)
    if n == 1:
        return _wiersze_p(ctx, poz)
    maxw = max(_slow(x) for x in poz)
    if 2 <= n <= 6 and (maxw <= 4 or (maxw <= 6 and not _liczby(sz, poz))):          # krótkie pozycje (także „300 g wody”) = kafle
        return [{"k": "li", "t": x} for x in poz], False                          # S4: kafle z ikoną
    if fr.get("num") and 2 <= n <= 5 and maxw <= 30 and not _liczby(sz, poz):
        karty = []
        for i, x in enumerate(poz, 1):
            h, r = sz.haslo_cut((x, None))
            bl = [{"k": "hero", "t": str(i)}, sz.blok("lead", h, color="ink")]
            if r is not None:
                bl.append(sz.blok("p", r, max_pt=18))
            karty.append(sz.k_karta(*bl))
        return [sz.k_cols(karty, pad=1.1, rwane_ok=True)], True                  # t19: kroki
    if 2 <= n <= 4 and maxw <= 30:
        return [sz.k_cols([_karta_p(sz, x) for x in poz], pad=1.0)], False        # kolejne punkty = karty z hasłem
    if 5 <= n <= 6 and maxw <= 14 and not _liczby(sz, poz):
        ik = sz.ikony()
        wiersze, ile = [], 3
        for a in range(0, n, ile):
            karty = [sz.k_karta(sz.k_icon(sz.ikona_dla(x, ik) or "sparkles", align="c", d=1.6),
                                sz.blok("lead", sz.flow((x, None)), align="c", color="ink", pt=20), align="c") for x in poz[a:a + ile]]
            wiersze.append(sz.k_cols(karty, pad=0.8, rwane_ok=True))
        return wiersze, True
    return [sz.k_cols([_karta_li(sz, poz)], pad=1.0)], True                       # dłuższa lista: jedna karta z punktami


def _ile_kart(zd):
    """Zdania jednego akapitu -> ile kart (myśli) obok siebie: do KARTA_JEDNA_DO słów jedna karta (hasło + dopisek), do KARTA_DWIE_DO dwie,
    dalej trzy; najwyżej tyle, ile zdań. Slajd z 2-3 myślami, nie z jedną kartą i pustą połową."""
    w = sum(_slow(z) for z in zd)
    c = 1 if w < KARTA_JEDNA_DO else (2 if (w < KARTA_DWIE_DO or len(zd) == 2) else 3)
    return max(1, min(c, len(zd)))


def _na_karty(zd, c):
    """Zdania -> c kolejnych grup o zbliżonej liczbie słów (programowanie dynamiczne; zdanie się nie dzieli)."""
    n = len(zd)
    c = max(1, min(c, n))
    w = [_slow(z) for z in zd]
    cel = sum(w) / float(c)
    inf = float("inf")
    f = [[inf] * (n + 1) for _ in range(c + 1)]
    wst = [[0] * (n + 1) for _ in range(c + 1)]
    f[0][0] = 0.0
    for g in range(1, c + 1):
        for j in range(g, n + 1):
            for i in range(g - 1, j):
                if f[g - 1][i] == inf:
                    continue
                v = f[g - 1][i] + (sum(w[i:j]) - cel) ** 2
                if v < f[g][j]:
                    f[g][j], wst[g][j] = v, i
    out, j = [], n
    for g in range(c, 0, -1):
        i = wst[g][j]
        out.append(zd[i:j])
        j = i
    return out[::-1]


def _wiersze_p(ctx, zd):
    """Zdania jednego akapitu: 1 = myśl (teza, fakt z liczbą); więcej = 1-3 karty obok siebie, każda z hasłem i dopiskiem (S14) - karta to
    1-2 sąsiednie zdania (`_ile_kart`); tylko gdy zdań >= 4 i razem mało słów: hasło i punkty."""
    if len(zd) == 1:
        return _wiersze_zdanie(ctx, zd[0])
    c = _ile_kart(zd)
    if c == 1:
        if len(zd) >= 4:
            return _wiersze_dlugi(ctx, zd), True
        return [ctx.sz.k_cols([_karta_p(ctx.sz, " ".join(zd))], pad=1.0)], False
    return [ctx.sz.k_cols([_karta_p(ctx.sz, " ".join(g)) for g in _na_karty(zd, c)], pad=1.0)], False


def _wiersze_zdanie(ctx, t):
    """Jedna myśl na slajdzie: krótka teza -> zielona karta (jak s03 strategii); z liczbą-bohaterem -> karta hero + hasło + dopisek;
    dłuższe -> karta z hasłem i dopiskiem (reguły S14)."""
    sz = ctx.sz
    p = (t, None)
    liczba = sz.liczba_bohater(p)
    h, r = sz.haslo_cut(p)
    if liczba and r is not None and sz.nslow(h) <= 16 and liczba in h[0]:
        blocks = list(_hero_i_haslo(sz, h, liczba)) + [sz.blok("p", r, max_pt=18)]
        return [sz.k_cols([sz.k_karta(*blocks)], pad=1.3, valign="m", min_h=7.5)], True
    if sz.nslow(p) <= 16:
        return [sz.k_cols([sz.k_karta(sz.blok("lead", p, align="c"), fill="brand", align="c")], pad=1.6, valign="m", min_h=8.5)], True
    return [sz.k_cols([_karta_p(sz, t)], pad=1.0)], False


def _wiersze_dlugi(ctx, zd):
    """Akapit z >= 4 zdaniami: hasło (pierwsze zdanie) i kolejne zdania jako punkty z ikoną."""
    sz = ctx.sz
    h, r = sz.haslo_cut((zd[0], None))
    blocks = [sz.blok("lead", h, color="ink")]
    if r is not None:
        blocks.append(sz.blok("p", r, max_pt=18))
    blocks += [{"k": "li", "t": x, "icon": "check"} for x in zd[1:]]
    return [sz.k_cols([sz.k_karta(*blocks)], pad=1.0)]


def _etykieta_sekcji(t):
    """Nazwa sekcji jako etykieta nad tytułem (jedna linia, KICKER_MAX znaków): za długą skracam do pełnych słów i „…” (pełna nazwa stoi
    na pierwszym slajdzie sekcji jako jej tytuł)."""
    t = " ".join(t.split())
    if len(t) <= KICKER_MAX:
        return t
    out = ""
    for sl in t.split():
        if len(out) + len(sl) + 1 > KICKER_MAX - 1:
            break
        out = (out + " " + sl).strip()
    return (out or t[:KICKER_MAX - 1]).rstrip(",;:-–—") + "…"


def _ilosc(t):
    """Wiersz zaczyna się liczbą i małą literą („1 łyżeczka harissy”, „2-3 pęczki natki”): to składnik / pozycja, nie tytuł. „4 Szpaki” (nazwa) nie."""
    m = re.match(r"\d[\d,.\-–/]*\s+(\S)", t)
    return bool(m and m.group(1).islower())


_AUTOR = re.compile(r"^(?P<q>.{20,}?)\s+[-–—]\s+(?P<a>[A-ZĄĆĘŁŃÓŚŹŻ][^-–—]{2,60})$")
_AUTOR_NAW = re.compile(r"^(?P<q>.{20,}?)\s*\((?P<a>[^()]{4,80})\)\.?$")


def _slajd_cytatu(ctx, t):
    """Cytat -> `uklad` z wierszem quote (t20). Autor: „… - Imię Nazwisko” albo „… (Imię Nazwisko)” na końcu; bez autora sam cytat."""
    q, a = t, ""
    for rx in (_AUTOR_NAW, _AUTOR):
        m = rx.match(t)
        if m and sum(1 for x in m.group("a").split() if x[:1].isupper()) >= 2:
            q, a = m.group("q").strip(), t[m.end("q"):].strip(" -–—")
            if rx is _AUTOR:
                a = m.group("a").strip()
            break
    return {"type": "uklad", "rows": [{"k": "quote", "t": q, "author": a}], "valign": "m", "zrodlo": ctx.nowy_nr()}


# --- ramka: okładka, agenda, przekładki, zakończenie ------------------------------------------------------------------------------
def _slajd_okladki(m, ok):
    """Okładka raportu (t09: jasna, zielony pas z logo marki, etykieta, tytuł, podtytuł, autor i data w stopce). Tytuł dłuższy niż ~45
    znaków dostaje okładkę z jednym zdaniem na środku (`statement`, t14), bo `cover_text` nie mieści go w wąskim polu."""
    if len(m["tytul"]) > COVER_DLUGI:
        sp = {"type": "statement", "bg": "card", "text": m["tytul"], "max_pt": 54}
        if ok["podtytul"]:
            sp["note"] = ok["podtytul"]
        elif ok["meta"]:
            sp["note"] = ok["meta"]
        if ok["kicker"]:
            sp["kicker"] = ok["kicker"]
        return sp
    sp = {"type": "cover_text", "variant": 3, "title": m["tytul"]}
    if ok["podtytul"]:
        sp["subtitle"] = _fraza(ok["podtytul"], 14, min_sl=4) or _czlon(ok["podtytul"], 14)   # do ~2 linii; całość w notatkach
    if ok["kicker"]:
        sp["kicker"] = ok["kicker"]
    if ok["meta"]:
        sp["meta"] = ok["meta"]
    return sp


def _nazwa_wyniku(m, wyjscie):
    return os.path.join(wyjscie or os.getcwd(), "%s - nowy styl.pptx" % m["nazwa"])


def _dec(ctx, wzorzec, wz, opis):
    return {"slajd": 0, "wzorzec": wzorzec, "wzor": _wzor(ctx, wz) if wz else None, "opis": opis}


def zloz(m, ustawienia=None):
    """Model -> spec (patrz `_zloz`); z pamięcią podręczną pomiaru układu."""
    import build_dk
    with _pomiar_ukladu(build_dk):
        return _zloz(m, ustawienia)


def _pas(n):
    """Zdanie-wniosek do pasa pod treścią: pierwsze zdanie komentarza po nośniku, inaczej wstępu; całe do PAS_MAX słów albo jego pierwszy
    człon (`haslo_cut`), gdy ten jest <= PAS_MAX słów. Dłuższe teksty nigdy nie idą na zieleń (zostają w notatkach)."""
    sz = _sz()
    for a in n["po"] + n["wstep"]:
        if a["k"] != "p" or not a["zd"] or _slow(a["zd"][0]) < 4:
            continue
        z = a["zd"][0]
        if _slow(z) <= PAS_MAX:
            return z
        h, r = sz.haslo_cut((z, None))
        if r is not None and _slow(h[0]) <= PAS_MAX:
            return h[0].strip().rstrip(",;:–—- ")
    return None


def _karta_hasla(sz, t, hero=True):
    """Tekst -> karta: (liczba-bohater) + hasło z pierwszego członu pierwszego zdania + dopisek (reszta zdania, do DOPISEK_SLOW słów)."""
    zd = _zdania(t)
    h, r = sz.haslo_cut((zd[0], None))
    liczba = sz.liczba_bohater(h) if hero else None
    bl = list(_hero_i_haslo(sz, h, liczba)) if liczba and liczba in h[0] else [sz.blok("lead", h, color="ink")]
    reszta = ([r[0]] if r else []) + zd[1:2]
    if reszta:
        bl.append(sz.blok("p", (_czlon(" ".join(reszta), DOPISEK_SLOW), None), max_pt=18))
    return sz.k_karta(*bl)


def _slajd_z_wierszy(ctx, n, rows, gotowy, tytul, kicker, pas=True):
    """Wiersze `uklad` (+ pas-wniosek) -> (slajd, decyzje, rekord) albo None, gdy się nie mieści."""
    sz = ctx.sz
    if pas:
        z = _pas(n)
        if z:
            rows = rows + [sz.k_band((z, None), "brand")]
    sp = {"type": "uklad", "title": tytul, "rows": rows, "valign": "t", "zrodlo": ctx.nowy_nr()}
    if kicker:
        sp["kicker"] = kicker
    w = _wybierz_uklad(ctx, sp, gotowy)
    if w is None:
        ctx.nr -= 1
    return w


def _kafle_listy(sz, poz, num=False, stopien=0):
    """Pozycje listy -> wiersze kafli: hasło (pierwsza fraza do ~6 słów) + dopisek Lato; ikona ze słownika na wszystkich kaflach albo na
    żadnym (numerowana: numer-bohater). 1-4 kafle w rzędzie, 5 = 3 + 2, 6 = 3 + 3. stopien 1 = bez dopisków, 2 = najwyżej 4 kafle."""
    poz = poz[:LISTA_MAX_POZ if stopien < 2 else 4]
    pary = [_haslo_poz(x) for x in poz]
    ik = sz.ikony()
    nazwy = [sz.ikona_dla(h, ik) for h, _d in pary]
    if not num and not all(nazwy):
        nazwy = [None] * len(pary)
    karty = []
    for i, ((h, d), nazwa) in enumerate(zip(pary, nazwy), 1):
        bl = []
        if num:
            bl.append({"k": "hero", "t": str(i)})
        elif nazwa:
            bl.append(sz.k_icon(nazwa, align="l", d=1.6))
        bl.append(sz.blok("lead", (h, None), color="ink"))
        if d and stopien < 1:
            bl.append(sz.blok("p", (d, None), max_pt=18))
        karty.append(sz.k_karta(*bl))
    n = len(karty)
    rzedy = [karty] if n <= 4 else [karty[:3], karty[3:]]
    return [sz.k_cols(r, pad=0.9, rwane_ok=True) for r in rzedy]


def _wiersze_tabeli(sz, n, stopien):
    """Tabela o kształcie innym niż tabela -> wiersze `uklad`: kpi (karty liczba + nazwa), taknie (karta na każdą wartość z punktami),
    kv (kafle etykieta: wartość)."""
    wiersze = n["atomy"][0]["wiersze"]
    head, rows = wiersze[0], wiersze[1:]
    j = n["kol_wart"]
    ks = n["ksztalt"]
    if ks == "kpi":
        karty = []
        for r in rows[:6 if stopien < 2 else 4]:
            v = r[j] if j < len(r) else ""
            karty.append(sz.k_karta({"k": "hero", "t": _czlon(v, 4)}, sz.blok("lead", (_czlon(r[0], HASLO_KROTKIE), None), color="ink", align="l")))
        rzedy = [karty] if len(karty) <= 4 else [karty[:3], karty[3:]]
        return [sz.k_cols(r, pad=0.9, rwane_ok=True) for r in rzedy], True
    if ks == "taknie":
        grupy = collections.OrderedDict()
        for r in rows:
            v = (r[j] if j < len(r) else "").strip()
            grupy.setdefault(v.lower(), (v, []))[1].append(_czlon(r[0], HASLO_POZ))
        ik = {"tak": "check", "częściowo": "minus", "czesciowo": "minus", "nie": "x"}
        karty = [sz.k_karta(sz.blok("h", (v or head[j], None)), *[{"k": "li", "t": x, "icon": ik.get(kl, "check")} for x in xs])
                 for kl, (v, xs) in list(grupy.items())[:3]]
        return [sz.k_cols(karty, pad=0.9, rwane_ok=True)], True
    karty = [sz.k_karta({"k": "kv", "label": _czlon(r[0], 4), "t": _czlon(r[j] if j < len(r) else "", 6)}) for r in rows[:KV_MAX - 2 * stopien]]
    return [sz.k_cols(karty[i:i + 4], pad=0.8, rwane_ok=True) for i in range(0, len(karty), 4)], True


def _wiersze_nosnika(ctx, n, szcz, czesc, stopien):
    """Wiersze slajdu dla nośnika; `stopien` 0 = pełny, 1-2 = mniej pozycji (gdy się nie mieści). Zwraca (rows, gotowy) albo None."""
    sz = ctx.sz
    k = n["k"]
    if k == "kpi":
        it = n["atomy"][0]["items"][:max(2, KPI_MAX - stopien)]
        karty = [sz.k_karta({"k": "hero", "t": x["value"]}, sz.blok("lead", (x["label"], None), color="ink", align="l")) for x in it]
        return [sz.k_cols(karty, pad=1.0, rwane_ok=True)], True
    if k == "kv":
        pary = n["atomy"][0]["pary"][:max(3, KV_MAX - 2 * stopien)]
        karty = [sz.k_karta({"k": "kv", "label": p[0], "t": _czlon(p[1], 6)}) for p in pary]
        return [sz.k_cols(karty[i:i + 4], pad=0.8, rwane_ok=True) for i in range(0, len(karty), 4)], True
    if k == "siatka":
        karty = []
        for h, kv in n["karty"][:6 if stopien < 2 else 4]:
            bl = [sz.blok("lead", (_czlon(h, HASLO_KROTKIE), None), color="ink")] + \
                [{"k": "kv", "label": e, "t": _czlon(v, 6)} for e, v in kv[:3 if stopien < 1 else 2] if v]
            karty.append(sz.k_karta(*bl))
        rzedy = [karty] if len(karty) <= 4 else [karty[:3], karty[3:]]
        return [sz.k_cols(r, pad=0.8, rwane_ok=True) for r in rzedy], True
    if k == "tab":
        return _wiersze_tabeli(sz, n, stopien)
    if k in ("lista", "lista-liczby", "kroki"):
        a = n["atomy"][0]
        poz = a["poz"][:LISTA_MAX_POZ if stopien < 2 else 4]
        pary = [_haslo_poz(x) for x in poz]
        if k != "kroki" and all(d is None and _slow(h) <= HASLO_KROTKIE for h, d in pary):
            return [{"k": "li", "t": h} for h, _d in pary], False      # same krótkie hasła: kafle S4 z ikonami (reguły + kandydaci układu)
        return _kafle_listy(sz, poz, num=(k == "kroki"), stopien=stopien), True
    if k in ("faq", "karty"):
        na = FAQ_NA_SLAJD if k == "faq" else KARTY_MAX
        karty = n["karty"][czesc * na:(czesc + 1) * na][:max(2, na - stopien)]
        cards = []
        for i, (h, t) in enumerate(karty, 1):
            bl = ([{"k": "hero", "t": str(i)}] if k == "karty" and re.match(r"\d+[.)]\s", h or "") else []) + \
                [sz.blok("lead", (re.sub(r"^\d+[.)]\s+", "", h or ""), None), color="ink"), sz.blok("p", (_czlon(t, DOPISEK_SLOW), None), max_pt=18)]
            cards.append(sz.k_karta(*bl))
        if k == "faq" and len(cards) > 3:
            return [sz.k_cols(cards[:3], pad=0.9, rwane_ok=True), sz.k_cols(cards[3:], pad=0.9, rwane_ok=True)], True
        return [sz.k_cols(cards, pad=0.9, rwane_ok=True)], True
    if k == "tekst":
        a = n["atomy"][czesc]
        t = " ".join(a["zd"])
        if len(a["zd"]) == 1 and _slow(t) <= ZIELONA_MAX:
            return [sz.k_cols([sz.k_karta(sz.blok("lead", (t, None), align="c"), fill="brand", align="c")], pad=1.6, valign="m", min_h=8.5)], True
        karta = _karta_hasla(sz, t)
        if stopien:
            karta["blocks"] = karta["blocks"][:-1] if len(karta["blocks"]) > 1 else karta["blocks"]
        return [sz.k_cols([karta], pad=1.3, valign="m", min_h=7.5)], True
    if k == "cyt":
        return _slajd_cytatu(ctx, n["atomy"][0]["t"])["rows"], True
    return None


def _tekst_pokazany(sl):
    """Słowa widoczne na slajdzie (spec): tytuł, wiersze `uklad`, tabela, pozostałe pola tekstowe."""
    out = []

    def zb(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("t", "title", "kicker", "label", "text", "caption", "author", "note") and isinstance(v, str):
                    out.append(v)
                elif k in ("rows", "items", "blocks", "head") or isinstance(v, (list, dict)):
                    zb(v)
        elif isinstance(x, list):
            for v in x:
                zb(v) if isinstance(v, (list, dict)) else (out.append(v) if isinstance(v, str) else None)
    zb(sl)
    return " ".join(out)


def _notatki(m, n, sek):
    """Notatki prelegenta: nagłówek, cały tekst nośnika (w kolejności dokumentu) i tekst nośników pominiętych na slajdach."""
    L = []

    def dodaj(x):
        if x["tytul"]:
            L.append(x["tytul"])
        for i in x["b"]:
            L.extend(_tekst_bloku(m["bloki"][i]))
    dodaj(n)
    for p in n["pominiete"]:
        L.append("")
        dodaj(p)
    return "\n".join(L)


def _slajdy_nosnika(ctx, n, szcz, m, sek, rozdz):
    """Nośnik -> lista (slajd, bloki, decyzje, rekord): slajd bazowy + dalsze części (tabela, FAQ, akapity), gdy je wybrano."""
    sz = ctx.sz
    tytul = n["tytul"] or m["tytul"]
    r = rozdz[n["roz"]]
    roz_t = sek[r["start"]]["naglowek"] if r["start"] is not None else None
    kicker = roz_t if roz_t and roz_t != tytul and len(roz_t) <= KICKER_MAX else None
    if roz_t and roz_t != tytul and len(roz_t) > KICKER_MAX and n["tytul"]:
        tytul = "%s - %s" % (roz_t, tytul)          # etykieta nad tytułem jest jednoliniowa; za długą dopisujemy do tytułu
    out = []
    for czesc in range(n["wybrany"]):
        tyt = tytul if czesc == 0 else "%s (%d)" % (tytul, czesc + 1)
        if czesc > n.get("wlasne", 0) and n["k"] != "tekst":   # wstęp / komentarz nośnika jako osobny slajd (hasło + dopisek)
            a = n["dod"][czesc - n["wlasne"] - 1]
            rows = [sz.k_cols([_karta_hasla(sz, " ".join(a["zd"]))], pad=1.3, valign="m", min_h=7.5)]
            w = _slajd_z_wierszy(ctx, n, rows, True, tyt, kicker, pas=False)
            if w is None:
                sp = {"type": "flow", "title": tyt, "blocks": [{"k": "p", "t": " ".join(a["zd"])}], "zrodlo": ctx.nowy_nr()}
                w = (sp, [], None)
            out.append((w[0], w[1], w[2], _dec(ctx, "haslo-dopisek", "t61", "akapit jako hasło z dopiskiem")))
            continue
        if n["k"] == "tab" and n.get("ksztalt", "tab") == "tab":
            wiersze = n["atomy"][0]["wiersze"]
            head, rows = _tab_skrot(wiersze, szcz, czesc)
            if not rows:
                break
            sp = {"type": "table", "title": tyt, "head": head, "rows": rows, "widths": _wagi_tabeli(head, rows), "zrodlo": ctx.nowy_nr()}
            if kicker:
                sp["kicker"] = kicker
            out.append((sp, [], None, _dec(ctx, "tabela", "t42", "tabela %dx%d (skrót: %d kolumn, %d wierszy; reszta w notatkach)" % (
                len(wiersze) - 1, len(wiersze[0]), len(head), len(rows)))))
            continue
        if n["k"] == "tab" and n["ksztalt"] == "czas":
            rows = n["atomy"][0]["wiersze"][1:7]
            items = []
            for r in rows:
                v = r[1] if len(r) > 1 else ""
                data = _fraza(v, 5) or _czlon(v, 4)
                reszta = " ".join(v.split()[_slow(data):]).lstrip(",;:–—- ")
                items.append({"date": data, "title": _czlon(r[0], HASLO_KROTKIE), "text": _czlon(reszta, 10) if reszta else ""})
            sp = {"type": "timeline", "title": tyt, "items": items, "zrodlo": ctx.nowy_nr()}
            if kicker:
                sp["kicker"] = kicker
            out.append((sp, [], None, _dec(ctx, "os-czasu", "t43", "tabela z datami jako oś czasu")))
            continue
        if n["k"] == "obr":
            a = n["atomy"][0]
            sp = {"type": "pics", "title": tyt, "items": [{"image": it["obraz"], "caption": it["podpis"]} for it in a["items"]], "zrodlo": ctx.nowy_nr()}
            if a.get("nota"):
                sp["items"][0]["caption"] = (a["nota"] + " " + sp["items"][0]["caption"]).strip()
            out.append((sp, [], None, _dec(ctx, "zrzuty", "t26" if len(a["items"]) == 1 else "t63", "%d obraz(y) w całości" % len(a["items"]))))
            continue
        w = None
        for stopien in (0, 1, 2):
            rw = _wiersze_nosnika(ctx, n, szcz, czesc, stopien)
            if rw is None:
                break
            rows, gotowy = rw
            w = _slajd_z_wierszy(ctx, n, rows, gotowy, tyt, kicker, pas=(czesc == 0))
            if w is not None:
                break
        if w is None:   # ostateczność: tekst do czytania (sam zmniejsza pismo), nigdy dodatkowy slajd
            rw = _wiersze_nosnika(ctx, n, szcz, czesc, 2) or ([], True)
            t = _tekst_pokazany({"rows": rw[0]})
            sp = {"type": "flow", "title": tyt, "blocks": [{"k": "p", "t": t}], "zrodlo": ctx.nowy_nr()}
            if kicker:
                sp["kicker"] = kicker
            ctx.uwagi.append("Slajd „%s”: treść nie zmieściła się w układzie z szablonu - został tekst do czytania." % tyt)
            w = (sp, [], None)
        wz = {"kpi": ("fakt-z-liczba", "t62", "liczby w kartach z hasłem"), "kv": ("etykieta-wartosc", "t45", "kafle etykieta: wartość"),
              "tab": {"kpi": ("fakt-z-liczba", "t62", "tabela z liczbami jako karty liczba + nazwa"), "taknie": ("tak-nie", "t59", "tabela tak / nie jako karty z punktami"),
                      "kv": ("etykieta-wartosc", "t45", "tabela dwukolumnowa jako kafle etykieta: wartość")}.get(n.get("ksztalt")),
              "siatka": ("karty-kv", "t45", "karty z nagłówkiem i parami etykieta: wartość"), "lista": ("kafle", "t36", "kafle z hasłem i dopiskiem"),
              "lista-liczby": ("kafle", "t36", "kafle z hasłem i dopiskiem"), "kroki": ("kroki", "t19", "kroki z numerem"),
              "faq": ("pytania", "t17", "pytania z pierwszym zdaniem odpowiedzi"), "karty": ("karty", "t19", "karty z nagłówkiem i dopiskiem"),
              "tekst": ("haslo-dopisek", "t61", "akapit jako hasło z dopiskiem"), "cyt": ("cytat", "t20", "cytat")}.get(n["k"])
        out.append((w[0], w[1], w[2], _dec(ctx, *wz) if wz else None))
    return out


def _zloz(m, ustawienia=None):
    """Model -> spec dla build_dk: plan (rozdziały, nośniki, budżet = suwak `slajdy`), slajd na nośnik z pełnym tekstem w notatkach,
    ramka (okładka, agenda, przekładki = suwak `rozdzialy`, zakończenie). Twarda bramka: slajdów treści nie więcej niż ustawienie.
    Klucze specu poza slajdami: output, uwagi, mapa_blokow, bledy_tekstu, szablon, warianty, ustawienia, plan."""
    ust = ustawienia or {}
    ctx = _Ctx()
    ctx.bd.T = dict(ctx.bd.THEMES["shop"])
    if ust.get("styl") not in (None, "nowy"):
        ctx.uwagi.append("Z dokumentu powstaje tylko nowy styl (sklep) - zbudowałem w nowym stylu.")
    sek = _drzewo(m, ctx.uwagi)
    zad = ust.get("slajdy")
    pl = plan(m, int(zad) if zad else None, sek)
    N, szcz, rozdz = pl["N"], pl["szczegolowo"], pl["rozdzialy"]
    if zad and int(zad) != N:
        ctx.uwagi.append("Dokument pozwala na %d-%d slajdów z treścią - zamiast %s ustawiłem %d." % (pl["min"], pl["max"], zad, N))
    z_nagl = [i for i, r in enumerate(rozdz) if r["start"] is not None]
    zad_roz = ust.get("rozdzialy")
    R = _rozdzialy_domyslnie(pl) if zad_roz is None else int(zad_roz)
    R = max(0, min(R, len(z_nagl), MAX_ROZDZIALOW))
    wyb = sorted(sorted(z_nagl, key=lambda i: -sum(_slow_sek(sek, s) for s in rozdz[i]["sekcje"]))[:R])
    if zad_roz is not None and len(wyb) != int(zad_roz):
        ctx.uwagi.append("Dokument ma %d rozdziałów (najwyżej %d dostaje slajd tytułowy) - zamiast %s ustawiłem %d." % (
            len(z_nagl), MAX_ROZDZIALOW, zad_roz, len(wyb)))
    tresc = []
    for n in pl["nosniki"]:
        if not n["wybrany"]:
            continue
        czesci = _slajdy_nosnika(ctx, n, szcz, m, sek, rozdz)
        for ci, (sl, dec, rek, wz) in enumerate(czesci):
            sl["notes"] = _notatki(m, n, sek) if ci == 0 else "%s - ciąg dalszy (pełny tekst w notatkach poprzedniego slajdu)." % (n["tytul"] or m["tytul"])
            tresc.append({"slajd": sl, "bloki": n["b"] if ci == 0 else [], "dec": dec, "rek": rek, "wz": wz, "roz": n["roz"], "n": n})
    n_tresc = len(tresc)
    if n_tresc > N:
        raise RuntimeError("Program złożył %d slajdów treści przy ustawieniu %d - błąd planu (to nie powinno się zdarzyć)." % (n_tresc, N))
    # --- ramka
    slides, mapa, decyzje, rekordy = [], {}, [], []

    def dodaj(sl, bloki, dec=(), wz=None):
        slides.append(sl)
        nr = len(slides)
        mapa[nr] = sorted(set(bloki))
        for d in dec:
            decyzje.append(dict(d, slajd=nr))
        if wz:
            decyzje.append(dict(wz, slajd=nr))
    ok = _okladka(m)
    okl = _slajd_okladki(m, ok)
    okl["notes"] = chr(10).join(t for i in sorted(ok["zuz"]) for t in _tekst_bloku(m["bloki"][i]))
    dodaj(okl, sorted(ok["zuz"]), wz=_dec(ctx, "okladka", "t14" if okl["type"] == "statement" else "t09", "okładka %s (tytuł dokumentu%s)" % (
        "z jednym zdaniem na środku (długi tytuł)" if okl["type"] == "statement" else "bez produktu", " i podtytuł" if ok["podtytul"] else "")))
    nazwy = {i: sek[rozdz[i]["start"]]["naglowek"] for i in wyb}
    agenda = len(wyb) >= 3
    if agenda and max(len(nazwy[i]) for i in wyb) > AGENDA_MAX[0 if len(wyb) <= 4 else 1]:
        agenda = False
        ctx.uwagi.append("Spisu treści nie dodałem: nazwy rozdziałów są za długie na jedną linię punktu (slajdy tytułowe rozdziałów zostają).")
    if agenda:
        dodaj({"type": "agenda", "title": "Agenda", "items": [nazwy[i] for i in wyb]}, [sek[rozdz[i]["start"]]["idx"] for i in wyb],
              wz=_dec(ctx, "agenda", "t10", "spis treści z %d rozdziałów" % len(wyb)))
    wstawione = set()
    for rec in tresc:
        ri = rec["roz"]
        if ri in wyb and ri not in wstawione:
            wstawione.add(ri)
            dodaj({"type": "section", "variant": "dark", "number": "%02d" % len(wstawione), "title": nazwy[ri], "section": nazwy[ri]},
                  [sek[rozdz[ri]["start"]]["idx"]], wz=_dec(ctx, "przekladka", "t11", "slajd tytułowy rozdziału %d: „%s”" % (len(wstawione), nazwy[ri])))
        if rec["rek"]:
            _tytul_w_kandydatach(rec["rek"], rec["slajd"], tak=True)
            rekordy.append(rec["rek"])
        dodaj(rec["slajd"], rec["bloki"], rec["dec"], rec["wz"])
    dodaj({"type": "end", "variant": "brand", "hashtag": "#zawszedobra"}, [], wz=_dec(ctx, "zakonczenie", "t64", "zakończenie"))
    # --- bramki jakości w specu
    for i, sl in enumerate(slides, 1):
        if sl["type"] in ("cover_text", "statement", "agenda", "section", "end"):
            continue
        w = _slow(_tekst_pokazany(sl))
        if w > SLAJD_MAX_SLOW + (15 if sl["type"] == "table" else 0):
            ctx.uwagi.append("Slajd %d ma %d słów (limit %d) - sprawdź, czy nie jest za gęsty." % (i, w, SLAJD_MAX_SLOW))
        for r in (sl.get("rows", []) if sl["type"] == "uklad" else []):
            if r.get("k") == "band" and _slow(r.get("t", "")) > PAS_MAX:
                raise RuntimeError("Slajd %d: pas zielony ma %d słów (limit %d)." % (i, _slow(r["t"]), PAS_MAX))
    pomin = [n for n in pl["nosniki"] if not n["wybrany"]]
    if pomin:
        ctx.uwagi.append("W notatkach prelegenta (nie na slajdach): %s%s." % (
            "; ".join("„%s”" % (n["tytul"] or m["tytul"]) for n in pomin[:8]), " i %d innych" % (len(pomin) - 8) if len(pomin) > 8 else ""))
    tab_sk = [rec for rec in tresc if rec["slajd"]["type"] == "table" and rec["n"]["wybrany"] * (TAB_WIERSZY_SZCZ if szcz else TAB_WIERSZY) <
              len(rec["n"]["atomy"][0]["wiersze"]) - 1]
    if tab_sk:
        ctx.uwagi.append("Tabele skrócone na slajdach (pełne wiersze i kolumny w notatkach): %s." % "; ".join("„%s”" % (r["n"]["tytul"] or m["tytul"]) for r in tab_sk[:6]))
    ramka = len(slides) - n_tresc
    ctx.uwagi.append("Razem w pliku: %d slajdów (%d z treścią + okładka%s%s i zakończenie); na slajdach ok. %d%% słów dokumentu, całość w notatkach prelegenta." % (
        len(slides), n_tresc, ", spis treści" if agenda else "", (", %d slajdów tytułowych rozdziałów" % len(wyb)) if wyb else "", pl["na_slajdach"]))
    bledy = _lint(m, mapa, ctx.uwagi)
    for w in m.get("ostrzezenia", []):
        ctx.uwagi.append(w)
    return {"theme": "shop", "sections": len(wyb) >= 2, "slides": slides, "mapa_blokow": mapa, "uwagi": ctx.uwagi, "cel": "dokument",
            "szablon": decyzje, "bledy_tekstu": bledy, "warianty": {"wersja": 1, "slajdy": rekordy}, "warianty_plik": "warianty-szablon.json",
            "nazwa": m["nazwa"], "tytul": m["tytul"],
            "ustawienia": {"slajdy": n_tresc, "rozdzialy": len(wyb), "razem": len(slides), "ramka": ramka, "na_slajdach": pl["na_slajdach"],
                           "zakres": [pl["min"], pl["dom"], pl["max"]]},
            "output": _nazwa_wyniku(m, ust.get("wyjscie"))}


def _tytul_w_kandydatach(rek, sl, tak=False):
    """Kandydaci układu w rekordzie mierzono z tytułem roboczym; po ustaleniu tytułu i etykiety slajdu dostają je też (inaczej zamiana
    wariantu po renderze podmieniłaby tytuł). tak=False: tylko czyści etykietę w kandydatach; tak=True: kopiuje tytuł i etykietę ze slajdu."""
    tytul, etykieta = sl.get("title"), sl.get("kicker")     # przed pętlą: wybrany kandydat bywa tym samym obiektem co `sl`
    for k in rek["kandydaci"]:
        k["slajd"].pop("kicker", None)
        if tak:
            k["slajd"]["title"] = tytul
            if etykieta:
                k["slajd"]["kicker"] = etykieta


def _w_poddrzewie(sek, rodzic, i):
    """Czy sekcja i leży w poddrzewie sekcji `rodzic` (kolejne sekcje o większym poziomie)."""
    if i <= rodzic:
        return i == rodzic
    return all(sek[j]["poziom"] > sek[rodzic]["poziom"] for j in range(rodzic + 1, i + 1))


def _tekst_bloku(b):
    if b["typ"] == "tabela":
        return [" | ".join(c for c in w if c) for w in b["wiersze"]]
    if b["typ"] == "kpi":
        return ["%s - %s" % (it["value"], it["label"]) for it in b["items"]]
    if b["typ"] == "kv":
        return [("%s: %s" % (p[0], p[1])) if p[0] else p[1] for p in b["pary"]]
    return [b["t"]] if b["t"] else []


def _lint(m, mapa, uwagi):
    """Ostrzeżenia o ewidentnych błędach tekstu źródła (lint_tekst; program ich NIE poprawia). Zwraca listę, dopisuje uwagi."""
    try:
        import lint_tekst
    except Exception:
        return []
    try:
        slajdy = []
        for nr, idxs in mapa.items():
            tx = []
            for i in idxs:
                tx += _tekst_bloku(m["bloki"][i])
            slajdy.append((nr, tx))
        wyniki = list(lint_tekst.sprawdz(slajdy) or [])
    except Exception:
        return []
    wys = [u for u in wyniki if u.get("pewnosc") == "wysoka"]
    sre = [u for u in wyniki if u.get("pewnosc") == "srednia"]
    if wys or sre:
        uwagi.append("Możliwe błędy w tekście dokumentu: %d (program ich nie poprawia - popraw w pliku i zrób prezentację jeszcze raz)" %
                     (len(wys) + len(sre)))
        for u in wys + sre[:10]:
            try:
                uwagi.append(lint_tekst.opis(u))
            except Exception:
                pass
        if len(sre) > 10:
            uwagi.append("…i %d innych podejrzeń o średniej pewności (lista: bledy_tekstu w specu)" % (len(sre) - 10))
    return wyniki


# =====================================================================================================================
# 5. POKRYCIE: czy cała treść dokumentu jest w pliku pptx
# =====================================================================================================================
def _tokeny(t):
    t = t.lower().replace("\xa0", " ")
    t = re.sub(r"[–—−‑]", "-", t)
    return re.findall(r"\w+", t, re.U)


def _akapity_pptx(pptx, notatki=True):
    """Slajdy pptx -> [Counter tokenów slajdu] (cały tekst: tytuły, pola, tabele, grupy; bez numerów stron; z notatkami prelegenta)."""
    from pptx import Presentation
    from pptx.oxml.ns import qn
    prs = Presentation(pptx)
    out = []
    for sl in prs.slides:
        c = collections.Counter()
        if notatki and sl.has_notes_slide:
            c.update(_tokeny(sl.notes_slide.notes_text_frame.text or ""))
        for p in sl._element.iter(qn("a:p")):
            sp = next((a for a in p.iterancestors() if a.tag == qn("p:sp")), None)
            if sp is not None:
                ph = sp.find(".//" + qn("p:ph"))
                if ph is not None and ph.get("type") in ("sldNum", "ftr", "dt"):
                    continue
            t = "".join(x.text or "" for x in p.iter(qn("a:t")))
            c.update(_tokeny(t))
        out.append(c)
    return out


def _wymagane(m):
    """[(indeks bloku, typ, tekst)]: akapity do sprawdzenia. Nagłówek bez żadnej treści pod sobą nie wchodzi (nie ma czego pokazać)."""
    sek = _drzewo(m)
    puste = set()
    for i, s in enumerate(sek):
        if s["naglowek"] and s["idx"] is not None and not s["atomy"]:
            j = i + 1
            if not (j < len(sek) and sek[j]["poziom"] > s["poziom"] and _slowa_poddrzewa(sek, i)):
                puste.add(s["idx"])
    out = []
    for i, b in enumerate(m["bloki"]):
        if b["typ"] == "obraz" or i in puste:
            continue
        if b["typ"] == "tabela":
            out += [(i, "tabela", " ".join(w)) for w in b["wiersze"]]
        elif b["typ"] in ("kpi", "kv"):
            out += [(i, b["typ"], t) for t in _tekst_bloku(b)]
        elif b["t"]:
            out.append((i, b["typ"], b["t"]))
    return out


def _dopasuj(sl, tk, need, start, smax, limit=None):
    """Najlepsze okno 1..smax kolejnych slajdów (od `start`), w którym stoi >= 95% słów bloku. (zgodność 0-1, (pierwszy slajd, szerokość))."""
    best, bw = 0.0, None
    for a in range(start, len(sl)):
        for w in range(1, smax + 1):
            cnt = sum((sl[x] for x in range(a, min(len(sl), a + w))), collections.Counter())
            zg = sum(min(v, cnt[tok]) for tok, v in tk.items()) / float(need)
            if zg > best:
                best, bw = zg, (a, w)
            if zg >= 0.95:
                return best, bw
        if limit is not None and a - start >= limit:
            break
    return best, bw


def pokrycie(m, pptx, mapa=None):
    """Czy każdy akapit dokumentu (>= 95% jego słów) stoi w pliku pptx (na slajdzie albo w jego notatkach prelegenta)? Szuka po kolei, od slajdu, na którym skończył poprzedni akapit,
    w oknie kilku kolejnych slajdów (akapit może być rozcięty na tyle slajdów, ile ma zdań) - to sprawdza też kolejność; czego nie
    ma w pobliżu, szuka na całej prezentacji. `mapa` ({nr slajdu: [indeksy bloków]}) zawęża okno do slajdów, na które trafił blok.
    Zwraca {"akapity", "przeniesione", "brakuje": [...], "procent", "tekst"}."""
    sl = _akapity_pptx(pptx)
    gdzie = {}
    for nr, idxs in (mapa or {}).items():
        for i in idxs:
            gdzie.setdefault(i, []).append(int(nr) - 1)
    wym = _wymagane(m)
    ok, brak, ptr = 0, [], 0
    for i, typ, t in wym:
        tk = collections.Counter(_tokeny(t))
        need = sum(tk.values())
        if not need:
            ok += 1
            continue
        smax = max(3, len(_zdania(t)) + 1)     # blok z s zdaniami może być rozcięty na s slajdów
        if typ == "tabela":
            smax = max(smax, 40)       # tabela tekstowa idzie jako karty kolumnami, zdanie na slajd: komórki jednego wiersza są daleko od siebie
        if i in gdzie:
            best, bw = _dopasuj(sl, tk, need, max(0, min(gdzie[i]) - 1), max(smax, max(gdzie[i]) - min(gdzie[i]) + 3))
        else:
            best, bw = _dopasuj(sl, tk, need, ptr, smax, limit=8)
            if best < 0.95:
                best2, bw2 = _dopasuj(sl, tk, need, 0, smax)
                if best2 > best:
                    best, bw = best2, bw2
        if best >= 0.95:
            ok += 1
            ptr = bw[0] + (bw[1] - 1 if bw[1] <= 3 else 0)      # szerokie okno nie przesuwa wskaźnika za daleko
        else:
            brak.append({"blok": i, "typ": typ, "tekst": t[:160], "zgodnosc": round(best, 2)})
    n = len(wym)
    pct = 100.0 * ok / n if n else 100.0
    dok = collections.Counter()
    for _i, _typ, t in wym:
        dok.update(_tokeny(t))
    na_sl = sum(_akapity_pptx(pptx, notatki=False), collections.Counter())
    razem = sum(dok.values())
    na_slajdach = int(round(100.0 * sum(min(v, na_sl[k]) for k, v in dok.items()) / razem)) if razem else 100
    return {"akapity": n, "przeniesione": ok, "brakuje": brak, "procent": round(pct, 1), "na_slajdach": na_slajdach,
            "tekst": ("Treść: 100%% akapitów (%d/%d) w pliku (slajdy i notatki prelegenta); na slajdach ok. %d%% słów" % (ok, n, na_slajdach)) if ok == n else
                     ("Treść: %.1f%% akapitów (%d/%d) w pliku, brakuje %d; na slajdach ok. %d%% słów" % (pct, ok, n, n - ok, na_slajdach))}


# =====================================================================================================================
# 6. WIERSZ POLECEŃ
# =====================================================================================================================
def _buduj(spec, katalog_rob):
    import build_dk
    spec_path = os.path.join(katalog_rob, "spec_dokument.json")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    build_dk.build(spec, spec["output"])
    return getattr(build_dk.build, "last_out", spec["output"]), spec_path


_RX_VERIFY = re.compile(r"^\s+s(\d+)\s+([A-Z_]{4,})")


def usterki_po_renderze(png_dir, spec, verify_tekst=""):
    """{nr slajdu: [kody]} z dwóch kontroli po renderze: pomiar zrzutów (oko.py, usterki wagi >= 2: PUSTY_DOL, KARTA_PUSTA...) i kontrola tekstu
    z PowerPointa (verify.ps1: linie „sNN PRZEPELNIENIE / SIEROTA / ZAWIESZKA ...”)."""
    wyn = collections.defaultdict(list)
    try:
        import oko
        for nr, w in oko.ocen_katalog(png_dir, spec).items():
            wyn[nr] += [u["kod"] for u in w["usterki"] if int(u.get("waga", 2)) >= 2]
    except Exception:  # noqa: BLE001 - brak oka = tylko kontrola tekstu
        pass
    for l in (verify_tekst or "").splitlines():
        m = _RX_VERIFY.match(l)
        if m:
            wyn[int(m.group(1))].append(m.group(2))
    return {nr: sorted(set(k)) for nr, k in wyn.items() if k}


def popraw_po_renderze(spec, usterki):
    """Zamienia w specu slajdy z usterkami na następny wariant układu z listy kandydatów (`szablonuj.inny_wariant`; kandydaci siedzą w
    spec["warianty"]). Zwraca numery zmienionych slajdów; dopisuje wpis do uwag. Budowa pliku i ponowny render są po stronie wołającego."""
    import szablonuj
    zm = [nr for nr in sorted(usterki) if szablonuj.inny_wariant(spec, nr, usterki[nr], spec.get("warianty"))]
    if zm:
        spec["uwagi"].append("Po obejrzeniu zrzutów poprawiłem układ slajdów: %s (inny wariant układu z listy kandydatów)." % ", ".join(str(x) for x in zm))
    return zm


def _przywroc_wybor(spec, zrodlo, wybory):
    """Po cofnięciu zamiany slajdu wraca też wskaźnik wybranego kandydata w rekordzie wariantów."""
    for r in (spec.get("warianty") or {}).get("slajdy", []):
        if r["zrodlo"] == zrodlo and (zrodlo, r["czesc"]) in wybory:
            r["wybrany"] = wybory[(zrodlo, r["czesc"])]


def petla_poprawek(spec, pomiar, buduj, max_rund=2):
    """Pętla „oko”: pomiar() po renderze -> {nr: [kody]} (+ tekst kontroli), przy usterkach zamiana wariantu układu (`popraw_po_renderze`),
    buduj() = ponowna budowa pliku ze specu. Po przebudowie slajd zostaje z nowym wariantem tylko wtedy, gdy ma MNIEJ usterek niż przed;
    inaczej wraca stary układ i drugi raz go nie ruszamy. Zwraca (ostatni wynik pomiaru, numery slajdów z zatrzymaną poprawką)."""
    odrzucone, poprawione, stan, wybory = set(), [], None, {}
    wyn = pomiar()
    for runda in range(max_rund + 1):
        us = wyn[0]
        if stan:
            przed, migawka, zm = stan
            cofnac = [nr for nr in zm if len(us.get(nr, [])) >= przed[nr]]
            for nr in cofnac:
                spec["slides"][nr - 1] = migawka[nr]
                _przywroc_wybor(spec, migawka[nr].get("zrodlo"), wybory)
                odrzucone.add(nr)
            if cofnac:
                buduj()
                wyn = pomiar()
                us = wyn[0]
            poprawione += [nr for nr in zm if nr not in cofnac and nr not in poprawione]
            stan = None
        do = {nr: k for nr, k in us.items() if nr not in odrzucone}
        if runda == max_rund or not do:
            break
        migawka = {nr: copy.deepcopy(spec["slides"][nr - 1]) for nr in do}
        wybory = {(r["zrodlo"], r["czesc"]): r.get("wybrany") for r in (spec.get("warianty") or {}).get("slajdy", [])}
        zm = popraw_po_renderze(spec, do)
        if not zm:
            break
        buduj()
        stan = ({nr: len(do[nr]) for nr in zm}, migawka, zm)
        wyn = pomiar()
    return wyn, poprawione


def _ps(skrypt, *arg):
    """Skrypt PowerShell skilla (render.ps1 / verify.ps1) -> tekst wyjścia; błąd uruchomienia = ''."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(HERE, skrypt)] + list(arg),
                           capture_output=True, timeout=900)
        return (r.stdout or b"").decode("utf-8", "replace")
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _qa(spec, out, rob, spec_path):
    """Kontrole z PowerPointem + pętla poprawek: zrzuty (`<robocze>\\zrzuty`), pomiar zrzutów (oko.py), kontrola tekstu (verify.ps1);
    przy usterkach do 2 rund zamiany wariantu układu (`petla_poprawek`). Wypisuje wynik ostatniej kontroli."""
    if sys.platform != "win32":    # zrzuty i kontrola tekstu to PowerPoint (COM)
        print("Na Macu bez podglądu slajdów: otwórz plik i sprawdź.")
        return
    png = os.path.join(rob, "zrzuty")
    ost = {"verify": ""}

    def pomiar():
        if not _ps("render.ps1", "-Src", out, "-Out", png).strip():
            ost["verify"] = ""
            return {}, ""
        v = _ps("verify.ps1", out)
        ost["verify"] = v
        return usterki_po_renderze(png, spec, v), v

    def buduj():
        _buduj(spec, rob)

    (us, _v), poprawione = petla_poprawek(spec, pomiar, buduj)
    if not os.path.isdir(png):
        print("Zrzutów nie zrobiono (PowerPoint nie odpowiedział) - wyglądu nie sprawdzono.")
        return
    if poprawione:
        print("Pętla poprawek: zmieniłem układ slajdów %s." % ", ".join(str(x) for x in poprawione))
    ukl = {nr: k for nr, k in us.items() if any(x not in ("PRZEPELNIENIE", "SIEROTA", "ZAWIESZKA", "MYSLNIK", "KOLIZJA") for x in k)}
    print("Kontrola układu (oko): usterki wagi >= 2 na %d slajdach%s; zrzuty: %s" % (
        len(ukl), (" (" + "; ".join("%d: %s" % (nr, ",".join(k)) for nr, k in sorted(ukl.items())) + ")") if ukl else "", png))
    t = [l for l in ost["verify"].splitlines() if l.startswith("Tekst")]
    print(t[-1] if t else "Kontrola tekstu: brak wyniku (PowerPoint nie odpowiedział)")
    for l in [l for l in ost["verify"].splitlines() if _RX_VERIFY.match(l)][:12]:
        print("  " + l.strip())


def main(argv=None):
    ap = argparse.ArgumentParser(description="Prezentacja Dobra Kaloria z dokumentu (%s)" % ", ".join(ROZSZERZENIA))
    ap.add_argument("plik")
    ap.add_argument("--slajdy", type=int, help="liczba slajdów Z TREŚCIĄ (domyślnie z dokumentu)")
    ap.add_argument("--rozdzialy", type=int, help="liczba przekładek rozdziałów (0 = bez)")
    ap.add_argument("--wyjscie", help="katalog na plik pptx (domyślnie obok dokumentu)")
    ap.add_argument("--robocze", help="katalog roboczy (obrazy, spec, zrzuty)")
    ap.add_argument("--bez-qa", action="store_true", help="bez PowerPointa: tylko kontrola treści (bez zrzutów i kontroli tekstu)")
    a = ap.parse_args(argv)
    plik = os.path.abspath(a.plik)
    wyj = os.path.abspath(a.wyjscie) if a.wyjscie else os.path.dirname(plik)
    rob = os.path.abspath(a.robocze) if a.robocze else os.path.join(wyj, "_robocze", os.path.splitext(os.path.basename(plik))[0])
    os.makedirs(wyj, exist_ok=True)
    os.makedirs(rob, exist_ok=True)
    try:
        m = wczytaj(plik, rob)
    except ValueError as e:
        print("BŁĄD: %s" % e)
        return 2
    s = statystyka(m)
    print("Dokument: „%s”, %d słów, nagłówki %s, tabele %d, obrazy %d" % (m["tytul"], s["slowa"], s["naglowki"], s["tabele"], s["obrazy"]))
    print("Zakres slajdów z treścią: %d-%d (domyślnie %d), rozdziałów do %d" % (s["slajdy_min"], s["slajdy_max"], s["slajdy_domyslnie"], s["rozdzialy_max"]))
    spec = zloz(m, {"slajdy": a.slajdy, "rozdzialy": a.rozdzialy, "wyjscie": wyj, "styl": "nowy"})
    out, spec_path = _buduj(spec, rob)
    print("Zbudowano: %s (%d slajdów)" % (out, len(spec["slides"])))
    for u in spec["uwagi"]:
        print("  - " + u)
    pok = pokrycie(m, out, spec["mapa_blokow"])
    print(pok["tekst"])
    for b in pok["brakuje"][:10]:
        print("  brakuje (blok %d, %s, zgodność %.2f): %s" % (b["blok"], b["typ"], b["zgodnosc"], b["tekst"]))
    if not a.bez_qa:
        _qa(spec, out, rob, spec_path)
    else:
        print("Wyglądu i łamania tekstu nie sprawdzono w PowerPoincie (--bez-qa).")
    return 0 if not pok["brakuje"] else 1


if __name__ == "__main__":
    sys.exit(main())
