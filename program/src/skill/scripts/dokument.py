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
        if b["typ"] in ("tabela", "obraz"):
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


def _pdf_fitz(plik, rob, ostrz, fitz):
    try:
        pdf = fitz.open(plik)
    except Exception:
        raise ValueError("Nie mogę otworzyć tego PDF-a (jest uszkodzony albo zabezpieczony hasłem).")
    if pdf.needs_pass:
        raise ValueError("Ten PDF jest zabezpieczony hasłem - zapisz go bez hasła i spróbuj ponownie.")
    strony = []  # na stronę: lista elementów (y0, rodzaj, dane) w kolejności czytania
    znaki = 0
    obr_licz = collections.Counter()
    for pn, page in enumerate(pdf):
        h = page.rect.height
        el = []
        tabele = []
        try:
            for tb in page.find_tables().tables:
                dane = tb.extract()
                if dane and len(dane) >= 2 and max(len(w) for w in dane) >= 2:
                    tabele.append((fitz.Rect(tb.bbox), dane))
        except Exception:
            pass
        for blk in page.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            bb = fitz.Rect(blk["bbox"])
            if any(bb.intersects(tr) and (bb & tr).get_area() > 0.5 * bb.get_area() for tr, _d in tabele):
                continue
            lin = []
            for ln in blk["lines"]:
                sp = [s for s in ln["spans"] if s["text"].strip()]
                if not sp:
                    continue
                tx = "".join(s["text"] for s in ln["spans"])
                zn = sum(len(s["text"].strip()) for s in sp)
                sz = sum(s["size"] * len(s["text"].strip()) for s in sp) / max(1, zn)
                bold = all((s["flags"] & 16) or "bold" in s["font"].lower() for s in sp)
                lin.append({"t": tx, "sz": round(sz, 1), "b": bold, "x0": ln["bbox"][0], "x1": ln["bbox"][2],
                            "y0": ln["bbox"][1], "y1": ln["bbox"][3], "n": zn})
                znaki += zn
            if lin:
                el.append((bb.y0, "tekst", {"lin": lin, "bb": bb}))
        for tr, dane in tabele:
            el.append((tr.y0, "tabela", dane))
        for info in page.get_image_info(xrefs=True):
            xr = info.get("xref") or 0
            if xr and min(info.get("width", 0), info.get("height", 0)) >= MIN_OBRAZ_PDF:
                obr_licz[xr] += 1
                el.append((info["bbox"][1], "obraz", xr))
        # kolejność: bloki tekstu zostają w kolejności strumienia, tabele i obrazy wchodzą według położenia
        tekst = [e for e in el if e[1] == "tekst"]
        reszta = sorted((e for e in el if e[1] != "tekst"), key=lambda e: e[0])
        for e in reszta:
            i = next((k for k, t in enumerate(tekst) if t[0] > e[0] + 1), len(tekst))
            tekst.insert(i, e)
        strony.append((h, tekst))
    if znaki < 20:
        raise _brak_tekstu()
    # stopki i nagłówki stron: ten sam tekst (cyfry = #) w pasie 8% góry / dołu na >= połowie stron
    pas = collections.Counter()
    for h, el in strony:
        wid = set()
        for y0, rodz, d in el:
            if rodz == "tekst":
                for l in d["lin"]:
                    if l["y0"] < 0.08 * h or l["y1"] > 0.92 * h:
                        wid.add(_norm_stopka(l["t"]))
        pas.update(wid)
    prog = max(2, int(0.5 * len(strony) + 0.5))
    stopki = {k for k, v in pas.items() if len(strony) >= 3 and v >= prog}
    # rozmiar pisma podstawowego (mediana po znakach)
    zl = collections.Counter()
    for _h, el in strony:
        for _y, rodz, d in el:
            if rodz == "tekst":
                for l in d["lin"]:
                    zl[round(l["sz"] * 2) / 2.0] += l["n"]
    baza = zl.most_common(1)[0][0] if zl else 11.0
    wiel = sorted({s for s in zl if s >= baza * 1.15}, reverse=True)
    bloki = []
    for pi, (h, el) in enumerate(strony):
        for y0, rodz, d in el:
            if rodz == "tabela":
                _dodaj_tabele(d, bloki)
            elif rodz == "obraz":
                if obr_licz[d] >= OBRAZ_DEKORACJA:
                    continue
                sc = _pdf_obraz(pdf, d, rob, ostrz, fitz, len([b for b in bloki if b["typ"] == "obraz"]) + 1)
                if sc:
                    bloki.append(_blok("obraz", "", 0, obraz=sc))
            else:
                lin = [l for l in d["lin"]
                       if not ((l["y0"] < 0.08 * h or l["y1"] > 0.92 * h) and (_norm_stopka(l["t"]) in stopki or _NUMER_STR.match(l["t"])))]
                _pdf_blok(lin, baza, wiel, bloki)
    return _scal_strony(bloki)


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


def _pdf_blok(lin, baza, wiel, bloki):
    """Linie jednego bloku PDF -> nagłówek / lista / akapity (łamanie z dzieleniem wyrazów sklejone)."""
    if not lin:
        return
    # sam punktor w osobnej linii (Word: „•” + tabulator) dołącza się do następnej linii
    l2, i = [], 0
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
    # podział na akapity wewnątrz bloku: przerwa pionowa, zmiana pisma, nowy punkt listy albo krótka linia kończąca zdanie
    grupy, cur = [], [lin[0]]
    for a, b in zip(lin, lin[1:]):
        przerwa = b["y0"] - a["y1"] > 0.6 * a["sz"]
        zmiana = abs(a["sz"] - b["sz"]) > 0.6 or a["b"] != b["b"]
        koniec = a["t"].rstrip()[-1:] in _KONIEC_ZD and a["x1"] < 0.85 * max(l["x1"] for l in lin) and b["t"].lstrip()[:1].isupper()
        punkt = bool(_BUL_RE.match(b["t"].strip())) or bool(_LISTA_NUM.match(b["t"].strip()))
        if przerwa or zmiana or koniec or punkt:
            grupy.append(cur)
            cur = []
        cur.append(b)
    grupy.append(cur)
    for g in grupy:
        t = _skleja_linie([l["t"] for l in g])
        sz = max(l["sz"] for l in g)
        sl = _slow(t)
        if wiel and sz >= baza * 1.15 and sl <= 16:
            poziom = min(3, 1 + min(range(len(wiel)), key=lambda i: abs(wiel[i] - round(sz * 2) / 2.0)))
            bloki.append(_blok("h%d" % poziom, t, poziom, _pdf_h=True))
        elif all(l["b"] for l in g) and sl <= 10 and t[-1:] not in ".,;!?…":
            bloki.append(_blok("h3", t, 3, _pdf_h=True))
        else:
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
    """(tytuł, podtytuł | None, zbiór indeksów bloków zużytych na okładce)."""
    zuz = set()
    i = m.get("tytul_idx")
    pod = None
    if i is not None:
        zuz.add(i)
        b = m["bloki"][i + 1] if i + 1 < len(m["bloki"]) else None
        if b and b["typ"] == "p" and (_slow(b["t"]) <= PODTYTUL_SLOW if len(m["tytul"]) <= COVER_DLUGI else len(b["t"]) <= 68) and \
                (b.get("podtytul") or any(x["typ"] in ("h1", "h2", "h3") for x in m["bloki"][i + 2:i + 3])):
            pod = b["t"]
            zuz.add(i + 1)
    return m["tytul"], pod, zuz


def _wagi_tabeli(head, rows):
    """Względne szerokości kolumn tabeli (jak w `table`: pierwsze 40 znaków najdłuższej komórki, potęga 0,7)."""
    out = []
    for j in range(len(head)):
        dl = max([len(head[j])] + [len(r[j]) for r in rows if j < len(r)])
        out.append(round(max(8, min(dl, 40)) ** 0.7, 2))
    return out


def _tabela_tekstowa(w):
    """Tabela z długimi komórkami (zawijałyby się poza wiersz): slajd `table` ma stałą wysokość wiersza i jedną linię pisma 13 pt."""
    n = len(w[0])
    wagi = _wagi_tabeli(w[0], w[1:])
    razem = sum(wagi)
    for j in range(n):
        znaki = max(4.0, (28.5 * wagi[j] / razem - 1.0) * 3.5)       # tyle znaków mieści się w kolumnie w jednej linii
        if any(len(r[j]) > znaki for r in w if j < len(r)):
            return True
    return False


def _tabela_na_akapity(w):
    """Tabela tekstowa -> akapity: dwie kolumny = „etykieta – wartość” na wiersz; więcej = akapit na kolumnę („nagłówek – komórki”; komórka bez
    kropki na końcu dostaje ją, żeby granice komórek były granicami zdań - hasło i dopisek tną po zdaniach)."""
    n = len(w[0])
    if n == 2:
        return [("%s – %s" % (r[0], r[1])) if r[0] and r[1] else (r[0] or r[1]) for r in w if r[0] or r[1]]
    out = []
    for j in range(n):
        kom = [r[j] for r in w[1:] if j < len(r) and r[j]]
        tx = " ".join(c if c[-1] in ".!?…:;)" else c + "." for c in kom[:-1]) + (" " if len(kom) > 1 else "") + (kom[-1] if kom else "")
        out.append(("%s – %s" % (w[0][j], tx)) if w[0][j] and tx else (w[0][j] or tx))
    return [x for x in out if x]


def _drzewo(m, uw=None):
    """Sekcje dokumentu w kolejności: {"naglowek", "poziom", "rodzic", "idx", "atomy": [...]}. Pierwsza sekcja (bez nagłówka) to treść
    przed pierwszym nagłówkiem. Atomy: p (zdania), li (pozycje), tab, obr (obrazy z podpisem), cyt."""
    _t, _p, zuz = _okladka(m)
    bl = m["bloki"]
    sek = [{"naglowek": None, "poziom": 0, "rodzic": None, "idx": None, "atomy": []}]
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
            sek.append({"naglowek": b["t"], "poziom": lv, "rodzic": stos[-1][1] if stos else None, "idx": i, "atomy": []})
            stos.append((lv, b["t"]))
        elif typ == "p":
            cur["atomy"].append({"k": "p", "zd": _zdania(b["t"]), "b": [i]})
        elif typ == "li":
            if cur["atomy"] and cur["atomy"][-1]["k"] == "li":
                cur["atomy"][-1]["poz"].append(b["t"])
                cur["atomy"][-1]["b"].append(i)
            else:
                cur["atomy"].append({"k": "li", "poz": [b["t"]], "b": [i], "num": bool(b.get("num"))})
        elif typ == "tabela":
            if _tabela_tekstowa(b["wiersze"]):
                if uw is not None:
                    uw.append("Tabela z długimi komórkami (%d x %d) nie zmieściłaby się w wierszach tabeli - przepisałem ją jako karty z tekstem "
                              "(nagłówek - treść)." % (len(b["wiersze"]), len(b["wiersze"][0])))
                for t in _tabela_na_akapity(b["wiersze"]):
                    cur["atomy"].append({"k": "p", "zd": _zdania(t), "b": [i]})
            else:
                cur["atomy"].append({"k": "tab", "wiersze": b["wiersze"], "b": [i]})
        elif typ == "cytat":
            cur["atomy"].append({"k": "cyt", "t": b["t"], "b": [i]})
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
    return 0


def _jednostki(atomy):
    """Atomy tekstu (p, li) -> jednostki myśli: zdanie (p) albo porcja listy po <= LISTA_PORCJA pozycji (li)."""
    u = []
    for ai, a in enumerate(atomy):
        if a["k"] == "p":
            for z in a["zd"]:
                u.append({"k": "p", "id": ai, "t": [z], "w": _slow(z), "b": a["b"]})
        else:
            poz = a["poz"]
            n = len(poz)
            porcje = max(1, -(-n // LISTA_PORCJA))
            for j in range(porcje):
                sl = poz[j * n // porcje:(j + 1) * n // porcje]
                u.append({"k": "li", "id": ai, "t": sl, "w": sum(_slow(x) for x in sl), "b": a["b"], "num": a.get("num"), "n": len(sl)})
    return u


def _fragmenty(units):
    """Jednostki jednego slajdu -> fragmenty (kolejne zdania tego samego akapitu = jeden fragment, porcje tej samej listy = jeden)."""
    out = []
    for u in units:
        if out and out[-1]["id"] == u["id"] and out[-1]["k"] == u["k"]:
            out[-1]["t"] = out[-1]["t"] + u["t"]
            out[-1]["w"] += u["w"]
        else:
            out.append({"k": u["k"], "id": u["id"], "t": list(u["t"]), "w": u["w"], "b": u["b"], "num": u.get("num")})
    return out


def _grupa_ok(frs):
    """Czy tak zmieszane fragmenty (k: p / li, w: słowa, n: pozycje listy) da się ułożyć na jednym slajdzie (zgodnie z `_wiersze_frag`)?
    Najwyżej CAP_FRAG kart, lista najwyżej LISTA_MAX punktów; zdanie wprowadzające przed listą do 60 słów (jedna karta)."""
    if len(frs) > CAP_FRAG or any(f["k"] == "li" and f.get("n", 0) > LISTA_MAX for f in frs):
        return False
    k = "".join("p" if f["k"] == "p" else "l" for f in frs)
    if k == "pl" and frs[0]["w"] > 60:
        return False
    return True


def _pakuj(units):
    """Najgęstszy podział jednostek na slajdy (limit słów, zgodne rodzaje fragmentów, najwyżej CAP_FRAG kart): lista list indeksów."""
    grupy, cur, w, frs = [], [], 0, []
    for i, u in enumerate(units):
        if frs and frs[-1]["id"] == u["id"] and frs[-1]["k"] == u["k"]:
            nowe = [dict(f) for f in frs]
            nowe[-1]["w"] += u["w"]
            nowe[-1]["n"] = nowe[-1].get("n", 0) + u.get("n", 0)
        else:
            nowe = [dict(f) for f in frs] + [{"k": u["k"], "id": u["id"], "w": u["w"], "n": u.get("n", 0)}]
        if cur and (w + u["w"] > CAP_SLOW or not _grupa_ok(nowe)):
            grupy.append(cur)
            cur, w = [], 0
            nowe = [{"k": u["k"], "id": u["id"], "w": u["w"], "n": u.get("n", 0)}]
        cur.append(i)
        w += u["w"]
        frs = nowe
    if cur:
        grupy.append(cur)
    return grupy


def _ile_slajdow_tabeli(wiersze):
    kol = len(wiersze[0])
    w = max(0, len(wiersze) - 1)
    return max(1, -(-w // TABELA_WIERSZE)) * max(1, -(-(kol - 1) // (TABELA_KOLUMNY - 1)) if kol > TABELA_KOLUMNY else 1)


def _elementy(sek):
    """Sekcje -> elementy do rozdzielenia na slajdy: {"sek": i, "k": "tekst"|"tab"|"obr"|"cyt", ...}; tekst: jednostki + k_min / k_max."""
    el = []
    for si, s in enumerate(sek):
        run = []

        def zrzut():
            if run:
                u = _jednostki(run)
                el.append({"sek": si, "k": "tekst", "atomy": list(run), "u": u, "w": sum(x["w"] for x in u),
                           "kmin": len(_pakuj(u)), "kmax": len(u)})
                run.clear()
        for a in s["atomy"]:
            if a["k"] in ("p", "li"):
                run.append(a)
            else:
                zrzut()
                el.append({"sek": si, "k": a["k"], "atom": a})
        zrzut()
    return el


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


def _wybierz_rozdzialy(sek, n):
    """n sekcji, od których zaczynają się rozdziały: najwyższe poziomem, przy równym poziomie najdłuższe; wynik w kolejności dokumentu."""
    kand = _kandydaci_rozdzialow(sek)
    n = max(0, min(n, len(kand), MAX_ROZDZIALOW))
    if not n:
        return []
    wyb = sorted(kand, key=lambda i: (sek[i]["poziom"], -_slowa_poddrzewa(sek, i), i))[:n]
    return sorted(wyb)


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
# 3. STATYSTYKA
# =====================================================================================================================
def _zakres(el):
    fix = sum(_ile_slajdow_tabeli(e["atom"]["wiersze"]) if e["k"] == "tab" else 1 for e in el if e["k"] != "tekst")
    kmin = sum(e["kmin"] for e in el if e["k"] == "tekst")
    kmax = sum(e["kmax"] for e in el if e["k"] == "tekst")
    wt = sum(e["w"] for e in el if e["k"] == "tekst")
    mn = fix + kmin
    mx = max(mn, min(MAX_SLAJDOW, fix + kmax))
    my = sum(len(e["u"]) for e in el if e["k"] == "tekst")
    cel = max(wt / float(SLOW_NA_SLAJD), my / MYSLI_NA_SLAJD)
    dom = fix + (min(kmax, max(kmin, int(round(cel)))) if kmax else 0)
    return fix, mn, mx, max(mn, min(mx, dom)), wt


def statystyka(m):
    """Zakresy suwaków liczone Z DOKUMENTU (bez pomiaru układu - natychmiast). `slajdy_*` = slajdy Z TREŚCIĄ (okładka, agenda, przekładki
    i zakończenie dochodzą). min = najgęściej, jak się da bez łamania progów pisma (najwyżej %d słów i %d kart na slajd, sekcje się nie
    łączą); max = jedna myśl (zdanie) na slajd, najwyżej %d; domyślnie 1 slajd na ok. %d słów treści (2-3 karty hasło + dopisek na slajd;
    nie rzadziej niż 1 slajd na %d zdań), w granicach min-max - luźniej niż min, ale nie jedna karta na slajd. `rozdzialy_max` = ile nagłówków może być przekładką (najwyżej %d; 0, gdy
    dokument nie ma nagłówków - tytułów nie wymyślamy); `rozdzialy_domyslnie` = liczba nagłówków najwyższego poziomu (2-8) albo 0.""" % (
        CAP_SLOW, CAP_FRAG, MAX_SLAJDOW, SLOW_NA_SLAJD, int(MYSLI_NA_SLAJD), MAX_ROZDZIALOW)
    sek = _drzewo(m)
    el = _elementy(sek)
    fix, mn, mx, dom, wt = _zakres(el)
    nag = {1: 0, 2: 0, 3: 0}
    for i, b in enumerate(m["bloki"]):
        if b["typ"] in ("h1", "h2", "h3") and i != m.get("tytul_idx"):
            nag[int(b["typ"][1])] += 1
    slowa = sum(_slow(b["t"]) for b in m["bloki"] if b["typ"] not in ("tabela", "obraz")) + \
        sum(_slow(c) for b in m["bloki"] if b["typ"] == "tabela" for w in b["wiersze"] for c in w)
    kand = _kandydaci_rozdzialow(sek)
    return {"slowa": slowa, "akapity": sum(1 for b in m["bloki"] if b["typ"] in ("p", "li", "cytat")), "naglowki": nag,
            "tabele": sum(1 for b in m["bloki"] if b["typ"] == "tabela"), "obrazy": sum(1 for b in m["bloki"] if b["typ"] == "obraz"),
            "slajdy_min": mn, "slajdy_max": mx, "slajdy_domyslnie": dom,
            "rozdzialy_max": min(MAX_ROZDZIALOW, len(kand)), "rozdzialy_domyslnie": _rozdzialy_domyslnie(sek, dom),
            "slajdy_stale": fix}


# =====================================================================================================================
# 4. ZŁOŻENIE: rozdzielenie slajdów, układy z szablonu
# =====================================================================================================================
def _przydziel(runs, n_tekst):
    """Ile slajdów dostaje każdy ciąg tekstu: proporcjonalnie do słów, w granicach [kmin, kmax]; suma = n_tekst, gdy się da."""
    sk = [r["kmin"] for r in runs]
    if n_tekst <= sum(sk):
        return sk
    if n_tekst >= sum(r["kmax"] for r in runs):
        return [r["kmax"] for r in runs]
    razem = float(sum(r["w"] for r in runs)) or 1.0
    ideal = [n_tekst * r["w"] / razem for r in runs]
    k = [max(r["kmin"], min(r["kmax"], int(x))) for r, x in zip(runs, ideal)]
    while sum(k) < n_tekst:
        j = max((i for i in range(len(k)) if k[i] < runs[i]["kmax"]), key=lambda i: ideal[i] - k[i])
        k[j] += 1
    while sum(k) > n_tekst:
        j = min((i for i in range(len(k)) if k[i] > runs[i]["kmin"]), key=lambda i: ideal[i] - k[i])
        k[j] -= 1
    return k


def _koncowki(units):
    """Dla każdego początku grupy i: dozwolone końce [(j, słowa)] (grupa units[i:j] mieści się w limicie słów i ma zgodne fragmenty)."""
    n, out = len(units), []
    for i in range(n):
        frs, w, res = [], 0, []
        for j in range(i, n):
            u = units[j]
            if frs and frs[-1]["id"] == u["id"] and frs[-1]["k"] == u["k"]:
                frs[-1]["w"] += u["w"]
                frs[-1]["n"] = frs[-1].get("n", 0) + u.get("n", 0)
            else:
                frs.append({"k": u["k"], "id": u["id"], "w": u["w"], "n": u.get("n", 0)})
            w += u["w"]
            if j > i and (w > CAP_SLOW or not _grupa_ok(frs)):
                break
            res.append((j + 1, w))
        out.append(res)
    return out


def _podziel_jednostki(units, k):
    """Dokładnie k kolejnych grup jednostek o zbliżonej liczbie słów (programowanie dynamiczne): każda grupa jest dozwolona (limit słów,
    zgodne fragmenty), cięcie w środku akapitu kosztuje. Gdy k jest mniejsze niż najgęstszy podział - podział najgęstszy."""
    n = len(units)
    k = max(1, min(k, n))
    razem = sum(u["w"] for u in units)
    cel = razem / float(k)
    kara = 0.5 * cel * cel
    gran = _koncowki(units)
    inf = float("inf")
    f = [[inf] * (n + 1) for _ in range(k + 1)]
    wstecz = [[0] * (n + 1) for _ in range(k + 1)]
    f[0][0] = 0.0
    for g in range(1, k + 1):
        for i in range(n):
            if f[g - 1][i] == inf:
                continue
            for j, w in gran[i]:
                c = f[g - 1][i] + (w - cel) ** 2
                if j < n and units[j - 1]["id"] == units[j]["id"] and units[j - 1]["k"] == units[j]["k"]:
                    c += kara
                if c < f[g][j]:
                    f[g][j], wstecz[g][j] = c, i
    if f[k][n] == inf:
        return _pakuj(units)
    out, j = [], n
    for g in range(k, 0, -1):
        i = wstecz[g][j]
        out.append(list(range(i, j)))
        j = i
    return out[::-1]


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
def _tekst_frag(fr):
    return " ".join(fr["t"])


def _karta_p(sz, tekst):
    return sz.k_karta(sz.blok("p", (tekst, None), align="l"))


def _karta_li(sz, poz):
    return sz.k_karta(*[{"k": "li", "t": x, "icon": "check"} for x in poz])


def _wiersze_frag(ctx, frags):
    """Fragmenty slajdu -> (wiersze, gotowy). gotowy = układ ułożony ręcznie (bez reguł szablonuj.stosuj). None = tak się nie da
    (za dużo kart albo zmieszane rodzaje) - slajd zostanie podzielony."""
    sz = ctx.sz
    n = len(frags)
    if n > CAP_FRAG:
        return None
    rodz = [f["k"] for f in frags]
    if n == 1:
        return _wiersze_p(ctx, frags[0]["t"]) if rodz[0] == "p" else _wiersze_lista(ctx, frags[0])
    if all(k == "p" for k in rodz):      # kilka akapitów: rząd równych kart (hasło + dopisek)
        return [sz.k_cols([_karta_p(sz, " ".join(f["t"])) for f in frags], pad=1.0)], False
    if n == 2 and rodz == ["p", "li"] and sum(_slow(x) for x in frags[0]["t"]) <= 60:
        zd = frags[0]["t"]       # zdanie wprowadzające + lista: jedna karta (hasło, dopisek, punkty)
        h, r = sz.haslo_cut((zd[0], None))
        blocks = [sz.blok("lead", h, color="ink")]
        reszta = ([r[0]] if r else []) + zd[1:]
        if reszta:
            blocks.append(sz.blok("p", (" ".join(reszta), None), max_pt=18))
        blocks += [{"k": "li", "t": x, "icon": "check"} for x in frags[1]["t"]]
        return [sz.k_cols([sz.k_karta(*blocks)], pad=1.0)], True
    if n == 2 and rodz == ["li", "p"] and sum(_slow(x) for x in frags[1]["t"]) <= 25:
        w = _wiersze_lista(ctx, frags[0])    # lista, a pod nią krótki komentarz = pas
        if w is not None:
            rows, gotowy = w
            return rows + [sz.k_band((" ".join(frags[1]["t"]), None), "brand")], gotowy
    # inne mieszanki: rząd kart, każda z hasłem i dopiskiem (akapit) albo z punktami (lista) - ręcznie, bez reguł S1-S15
    return [sz.k_cols([_karta_reczna(sz, f) for f in frags], pad=1.0, rwane_ok=True)], True


def _hero_i_haslo(sz, h, liczba):
    """(hero, hasło) dla zdania z liczbą-bohaterem. K2 (13.10): liczba znika z hasła tylko wtedy, gdy po jej zdjęciu zostaje domknięta fraza
    (`szablonuj.bez_liczby`: „o 7,8%” przechodzi do hero, „80% - grupa 1 jak powyżej” -> „Grupa 1 jak powyżej”); inaczej hasło zostaje
    z liczbą, a hero się powtarza."""
    r = sz.bez_liczby(h, liczba, zdejmij=True)
    if r:
        return {"k": "hero", "t": r[2], "zast": True}, sz.blok("lead", (r[0], r[1]), color="ink")
    return {"k": "hero", "t": liczba}, sz.blok("lead", h, color="ink")


def _karta_reczna(sz, fr):
    """Fragment -> karta: akapit = (liczba-bohater) + hasło z pierwszego zdania + dopisek; lista = punkty z ikoną."""
    if fr["k"] == "li":
        return _karta_li(sz, fr["t"])
    zd = fr["t"]
    h, r = sz.haslo_cut((zd[0], None))
    liczba = sz.liczba_bohater(h)
    bl = list(_hero_i_haslo(sz, h, liczba)) if liczba and liczba in h[0] else [sz.blok("lead", h, color="ink")]
    reszta = ([r[0]] if r else []) + zd[1:]
    if reszta:
        bl.append(sz.blok("p", (" ".join(reszta), None), max_pt=18))
    return sz.k_karta(*bl)


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


def _tytul_z_hasla(ctx, frags):
    """Pierwsze zdanie slajdu (fragment akapitu) -> (tytuł = jego hasło, fragmenty bez tego hasła) albo None. Słowa źródła, tylko przeniesione:
    reszta pierwszego zdania zostaje na początku fragmentu jako dopisek. Nie dla hasła z liczbą-bohaterem (zostaje kartą z liczbą), numeru
    pozycji / składnika (liczba i mała litera), uciętej zapowiedzi listy („:”), hasła dłuższego niż HASLO_TYTUL_SLOW słów, ani gdy na slajdzie zostałoby mniej niż RESZTA_MIN_SLOW słów."""
    f0 = frags[0]
    if f0["k"] != "p":
        return None
    sz = ctx.sz
    z0 = f0["t"][0]
    h, r = sz.haslo_cut((z0, None))
    tyt = h[0].strip().rstrip(",;-–—").strip()      # urwany przecinek / myślnik na końcu hasła nie należy do tytułu
    if not tyt or sz.nslow(h) > HASLO_TYTUL_SLOW or len(tyt) > HASLO_TYTUL_ZNAKI or _ilosc(tyt) or sz.liczba_bohater(h) or             (r is not None and ":" in tyt):
        return None             # liczba-bohater w haśle: fakt zostaje kartą; „:” w uciętym haśle = zapowiedź listy, której ciąg jest w reszcie zdania
    reszta = ([r[0]] if r else []) + list(f0["t"][1:])
    nowe = ([dict(f0, t=reszta, w=sum(_slow(x) for x in reszta))] if reszta else []) + list(frags[1:])
    if sum(f["w"] for f in nowe) < RESZTA_MIN_SLOW:
        return None
    return tyt, nowe


def _zbuduj_tekst(ctx, frags, tytul, kicker, nazwa=None):
    """Fragmenty jednego slajdu -> (slajd, decyzje, rekord) albo None, gdy się nie mieści. `nazwa` (nazwa sekcji dłuższej niż DLUGA_SEKCJA
    slajdy): tytuł slajdu = hasło z jego pierwszego zdania, nazwa sekcji nad nim; gdy się nie da - zwykły tytuł `tytul`."""
    if nazwa:
        th = _tytul_z_hasla(ctx, frags)
        w = _wiersze_frag(ctx, th[1]) if th else None
        if w is not None:
            rows, gotowy = w
            sp = {"type": "uklad", "title": th[0], "kicker": _etykieta_sekcji(nazwa), "rows": rows, "valign": "t", "zrodlo": ctx.nowy_nr()}
            wyn = _wybierz_uklad(ctx, sp, gotowy)
            if wyn is not None:
                ctx.wlasne.add(id(wyn[0]))
                return wyn
            ctx.nr -= 1
        z0 = frags[0]["t"][0] if frags else ""
        if len(frags) == 1 and frags[0]["k"] == "p" and len(frags[0]["t"]) == 1 and _slow(z0) <= STATEMENT_SLOW and                 not ctx.sz.liczba_bohater((z0, None)):
            sp = {"type": "statement", "bg": "card", "text": z0, "title": z0, "kicker": _etykieta_sekcji(nazwa), "max_pt": 54,
                  "zrodlo": ctx.nowy_nr()}
            ctx.wlasne.add(id(sp))
            return sp, [], None
    w = _wiersze_frag(ctx, frags)
    if w is None:
        return None
    rows, gotowy = w
    sp = {"type": "uklad", "title": tytul, "rows": rows, "valign": "t", "zrodlo": ctx.nowy_nr()}
    if kicker:
        sp["kicker"] = kicker
    wyn = _wybierz_uklad(ctx, sp, gotowy)
    if wyn is None:
        ctx.nr -= 1
    return wyn


def _polowa(frags):
    """Fragmenty -> dwie połowy o zbliżonej liczbie słów (cięcie między fragmentami, a przy jednym fragmencie - między zdaniami)."""
    if len(frags) >= 2:
        cum, c = [], 0
        for f in frags:
            c += f["w"]
            cum.append(c)
        i = min(range(len(frags) - 1), key=lambda j: abs(cum[j] - cum[-1] / 2.0))
        return frags[:i + 1], frags[i + 1:]
    f = frags[0]
    t = f["t"]
    if len(t) < 2:
        return None
    cum, c = [], 0
    for x in t:
        c += _slow(x)
        cum.append(c)
    i = min(range(len(t) - 1), key=lambda j: abs(cum[j] - cum[-1] / 2.0))
    a, b = dict(f, t=t[:i + 1], w=cum[i]), dict(f, t=t[i + 1:], w=cum[-1] - cum[i])
    return [a], [b]


def _slajdy_tekstu(ctx, frags, tytul_fn, kicker, nazwa=None):
    """Fragmenty -> lista (slajd, decyzje, rekord, bloki); gdy slajd się nie mieści, dzieli go (wynik ma wtedy więcej slajdów)."""
    wyn = _zbuduj_tekst(ctx, frags, tytul_fn(), kicker, nazwa)
    bl = sorted({i for f in frags for i in f["b"]})
    if wyn is not None:
        return [(wyn[0], wyn[1], wyn[2], bl)]
    pol = _polowa(frags) if sum(len(f["t"]) for f in frags) > 1 or len(frags) > 1 else None
    if pol is None:
        # jedna myśl, która się nie mieści: tekst do czytania (flow, pismo 20-13 pt)
        t = _tekst_frag(frags[0])
        sp = {"type": "flow", "title": tytul_fn(), "blocks": [{"k": "li" if frags[0]["k"] == "li" else "p", "t": x}
                                                             for x in (frags[0]["t"] if frags[0]["k"] == "li" else [t])]}
        if kicker:
            sp["kicker"] = kicker
        ctx.uwagi.append("Slajd z jednym bardzo długim fragmentem tekstu (%d słów) zostaje tekstem do czytania, bez haseł: „%s…”" % (
            _slow(t), t[:60]))
        return [(sp, [], None, bl)]
    return _slajdy_tekstu(ctx, pol[0], tytul_fn, kicker, nazwa) + _slajdy_tekstu(ctx, pol[1], tytul_fn, kicker, nazwa)


# --- tabele, cytaty, obrazy ----------------------------------------------------------------------------------------------------
def _slajdy_tabeli(ctx, tab):
    """Tabela -> slajdy `table` (t42): do 6 kolumn i 8 wierszy na slajd; dłuższa dzieli się na kolejne slajdy z powtórzonym
    nagłówkiem (przy > 6 kolumnach pierwsza kolumna powtarza się w każdej części)."""
    w = tab["wiersze"]
    head, dane = w[0], w[1:]
    ncol = len(head)
    if ncol > TABELA_KOLUMNY:
        reszta, grupy = list(range(1, ncol)), []
        while reszta:
            grupy.append([0] + reszta[:TABELA_KOLUMNY - 1])
            reszta = reszta[TABELA_KOLUMNY - 1:]
        ctx.uwagi.append("Tabela ma %d kolumn - podzieliłem ją na %d slajdy (pierwsza kolumna powtarza się)." % (ncol, len(grupy)))
    else:
        grupy = [list(range(ncol))]
    out = []
    for g in grupy:
        for a in range(0, max(1, len(dane)), TABELA_WIERSZE):
            chunk = dane[a:a + TABELA_WIERSZE]
            wagi = _wagi_tabeli([head[j] for j in g], [[r[j] for j in g] for r in chunk])
            out.append({"type": "table", "head": [head[j] for j in g], "rows": [[r[j] for j in g] for r in chunk], "widths": wagi,
                        "zrodlo": ctx.nowy_nr()})
    if len(out) > len(grupy):
        ctx.uwagi.append("Tabela ma %d wierszy - podzieliłem ją na %d slajdów (nagłówek się powtarza)." % (len(dane), len(out)))
    return out


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
def _slajd_okladki(m, podtytul):
    """Okładka bez produktu 50/50 (t07). Wszystkie warianty `cover_text` źle znoszą tytuł dłuższy niż ~45 znaków (pismo nie schodzi poniżej
    36 pt w wąskim polu, tytuł wychodzi poza kadr), dlatego długi tytuł dostaje okładkę z jednym zdaniem na środku (`statement`, t14, kremowe
    tło, logo u dołu), a podtytuł tylko gdy ma najwyżej 68 znaków (jedna linia; inaczej akapit zostaje w treści - `_okladka`)."""
    if len(m["tytul"]) > COVER_DLUGI:
        sp = {"type": "statement", "bg": "card", "text": m["tytul"], "max_pt": 54}
        if podtytul:
            sp["note"] = podtytul
        return sp
    sp = {"type": "cover_text", "variant": 1, "title": m["tytul"]}
    if podtytul:
        sp["subtitle"] = podtytul
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


def _zloz(m, ustawienia=None):
    """Model -> spec dla build_dk (typy slajdów z szablonu + `uklad` z klockami S1-S15). Ustawienia: `slajdy` (slajdy Z TREŚCIĄ,
    domyślnie z `statystyka`; poza zakresem = najbliższa dozwolona wartość), `rozdzialy` (przekładki; 0 = bez), `wyjscie`, `styl`.
    Klucze specu poza slajdami: output, uwagi, mapa_blokow {nr slajdu: [indeksy bloków modelu]}, bledy_tekstu, szablon (decyzje
    z polem `wzor`), warianty (kandydaci układu, jak w konwersji), ustawienia (co wyszło)."""
    ust = ustawienia or {}
    ctx = _Ctx()
    ctx.bd.T = dict(ctx.bd.THEMES["shop"])
    if ust.get("styl") not in (None, "nowy"):
        ctx.uwagi.append("Z dokumentu powstaje tylko nowy styl (sklep) - zbudowałem w nowym stylu.")
    sek = _drzewo(m, ctx.uwagi)
    el = _elementy(sek)
    fix, mn, mx, dom, _wt = _zakres(el)
    zad_slajdy = ust.get("slajdy")
    N = max(mn, min(mx, int(zad_slajdy if zad_slajdy else dom)))
    if zad_slajdy and int(zad_slajdy) != N:
        ctx.uwagi.append("Dokument pozwala na %d-%d slajdów z treścią - zamiast %s ustawiłem %d." % (mn, mx, zad_slajdy, N))
    zad_roz = ust.get("rozdzialy")
    R = _rozdzialy_domyslnie(sek, dom) if zad_roz is None else int(zad_roz)
    rozdz = _wybierz_rozdzialy(sek, R)
    if zad_roz is not None and len(rozdz) != int(zad_roz):
        ctx.uwagi.append("Dokument ma %d nagłówków, które mogą być rozdziałami (najwyżej %d) - zamiast %s ustawiłem %d." % (
            len(_kandydaci_rozdzialow(sek)), MAX_ROZDZIALOW, zad_roz, len(rozdz)))
    runs = [e for e in el if e["k"] == "tekst"]
    for e, k in zip(runs, _przydziel(runs, N - fix) if runs else []):
        e["k_zad"] = k
    _tyt, podtytul, _zuz = _okladka(m)
    kand_roz = _kandydaci_rozdzialow(sek)
    out = []     # {"slajd", "bloki", "dec", "rek", "sek"}
    for si, s in enumerate(sek):
        elems = [e for e in el if e["sek"] == si]
        czesci = []
        n_sl = sum(e["k_zad"] if e["k"] == "tekst" else (_ile_slajdow_tabeli(e["atom"]["wiersze"]) if e["k"] == "tab" else 1) for e in elems)
        dluga = n_sl > DLUGA_SEKCJA
        for e in elems:
            if e["k"] == "tekst":
                units = e["u"]
                for g in _podziel_jednostki(units, e["k_zad"]):
                    fr = _fragmenty([units[i] for i in g])
                    kick = s["rodzic"] if s["naglowek"] else None
                    miara = (s["naglowek"] or m["tytul"]) + " (2)"
                    # sekcja na > 2 slajdy: nazwa nad tytułem, tytuł = hasło slajdu (pierwszy slajd sekcji z nagłówkiem zostaje z nagłówkiem)
                    nazwa = (s["naglowek"] or m["tytul"]) if dluga and (czesci or not s["naglowek"]) else None
                    czesci += [("tekst",) + x for x in _slajdy_tekstu(ctx, fr, lambda t=miara: t, kick, nazwa)]
            elif e["k"] == "tab":
                czesci += [("tab", sl, [], None, e["atom"]["b"]) for sl in _slajdy_tabeli(ctx, e["atom"])]
            elif e["k"] == "cyt":
                a = e["atom"]
                czesci.append(("cyt", _slajd_cytatu(ctx, a["t"]), [], None, a["b"]))
            elif e["k"] == "obr":
                a = e["atom"]
                sp = {"type": "pics", "items": [{"image": it["obraz"], "caption": it["podpis"]} for it in a["items"]],
                      "zrodlo": ctx.nowy_nr()}
                if a.get("nota"):    # zapowiedź z dwukropkiem przed obrazem + podpis pod nim = jeden podpis (kolejność zostaje)
                    sp["items"][0]["caption"] = (a["nota"] + " " + sp["items"][0]["caption"]).strip()
                czesci.append(("obr", sp, [], None, a["b"]))
        for n, (rodzaj, sl, dec, rek, bl) in enumerate(czesci):
            baza = s["naglowek"] or m["tytul"]
            wl = id(sl) in ctx.wlasne          # tytuł z hasła i nazwa sekcji nad nim są już ustawione
            etykieta = sl.get("kicker") if wl else None
            if rek:
                _tytul_w_kandydatach(rek, sl)  # (wybrany kandydat to ten sam obiekt co `sl`: czyści też jego etykietę)
            if wl:
                if etykieta:
                    sl["kicker"] = etykieta
            else:
                sl.pop("kicker", None)
                if s["naglowek"] and s["rodzic"] and len(s["rodzic"]) > KICKER_MAX:
                    baza = "%s - %s" % (s["rodzic"], baza)       # etykieta nad tytułem jest jednoliniowa; za długą dopisujemy do tytułu
                sl["title"] = baza if n == 0 else "%s (%d)" % (baza, n + 1)
                if s["naglowek"] and s["rodzic"] and len(s["rodzic"]) <= KICKER_MAX:
                    sl["kicker"] = s["rodzic"]
            if rek:
                _tytul_w_kandydatach(rek, sl, tak=True)
            bb = list(bl)
            if n == 0 and s["idx"] is not None:
                bb = [s["idx"]] + bb
            out.append({"slajd": sl, "bloki": bb, "dec": dec, "rek": rek, "sek": si, "rodzaj": rodzaj})
    n_hasla = sum(1 for r in out if id(r["slajd"]) in ctx.wlasne)
    if n_hasla:
        ctx.uwagi.append("Sekcje dłuższe niż %d slajdy nie mają numerków „(3)”: %d slajdów ma tytuł z pierwszego zdania (hasło ze słów dokumentu) albo samo "
                         "zdanie na środku, a nazwa sekcji stoi nad nim." % (DLUGA_SEKCJA, n_hasla))
    # --- ramka
    nazwy_roz = {i: sek[i]["naglowek"] for i in rozdz}
    slides, mapa, decyzje, rekordy = [], {}, [], []

    def dodaj(sl, bloki, dec=(), wz=None):
        slides.append(sl)
        nr = len(slides)
        mapa[nr] = sorted(set(bloki))
        for d in dec:
            decyzje.append(dict(d, slajd=nr))
        if wz:
            decyzje.append(dict(wz, slajd=nr))
    ok_bl = [i for i in (m.get("tytul_idx"),) if i is not None] + ([m["tytul_idx"] + 1] if podtytul and m.get("tytul_idx") is not None else [])
    okl = _slajd_okladki(m, podtytul)
    dodaj(okl, ok_bl, wz=_dec(ctx, "okladka", "t14" if okl["type"] == "statement" else "t07", "okładka %s (tytuł dokumentu%s)" % (
        "z jednym zdaniem na środku (długi tytuł)" if okl["type"] == "statement" else "bez produktu", 
        " i podtytuł z pierwszego akapitu" if podtytul else "")))
    agenda = len(rozdz) >= 3
    if agenda and max(len(nazwy_roz[i]) for i in rozdz) > AGENDA_MAX[0 if len(rozdz) <= 4 else 1]:
        agenda = False
        ctx.uwagi.append("Agendy nie dodałem: nazwy rozdziałów są za długie na jedną linię punktu agendy (przekładki zostają).")
    if agenda:
        dodaj({"type": "agenda", "title": "Agenda", "items": [nazwy_roz[i] for i in rozdz]}, [sek[i]["idx"] for i in rozdz],
              wz=_dec(ctx, "agenda", "t10", "agenda z %d rozdziałów" % len(rozdz)))
    wstawione, ile_roz = set(), 0
    sekcje_pptx = len(rozdz) >= 2
    for rec in out:
        si = rec["sek"]
        for ri in rozdz:   # przekładka stoi przed pierwszym slajdem rozdziału (jego własnym albo podsekcji)
            if ri not in wstawione and (ri == si or (ri < si and _w_poddrzewie(sek, ri, si))):
                wstawione.add(ri)
                ile_roz += 1
                dodaj({"type": "section", "variant": "dark", "number": "%02d" % ile_roz, "title": sek[ri]["naglowek"],
                       "section": sek[ri]["naglowek"]}, [sek[ri]["idx"]],
                      wz=_dec(ctx, "przekladka", "t11", "przekładka rozdziału %d: „%s”" % (ile_roz, sek[ri]["naglowek"])))
        sl = rec["slajd"]
        wz = None
        if sl["type"] == "table":
            wz = _dec(ctx, "tabela", "t42", "tabela %dx%d" % (len(sl["rows"]) + 1, len(sl["head"])))
        elif sl["type"] == "statement":
            wz = _dec(ctx, "teza-zielona", "t14", "jedno zdanie na środku slajdu (sekcja dłuższa niż %d slajdy)" % DLUGA_SEKCJA)
        elif sl["type"] == "pics":
            n = len(sl["items"])
            wz = _dec(ctx, "zrzuty", "t26" if n == 1 else ("t63" if n == 2 else "t28"), "%d obraz(y) w całości z podpisem" % n)
        elif sl["type"] == "uklad" and sl["rows"] and sl["rows"][0]["k"] == "quote":
            wz = _dec(ctx, "cytat", "t20", "cytat")
        elif sl["type"] == "flow":
            wz = _dec(ctx, "akapit-do-czytania", "t15", "bardzo długi fragment jako tekst do czytania")
        decs = list(rec["dec"])
        if sl["type"] == "uklad" and not decs and sl["rows"] and sl["rows"][0]["k"] == "cols":
            it = sl["rows"][0]["items"]
            if len(it) == 1 and it[0].get("fill") == "brand":
                decs = [_dec(ctx, "teza-zielona", "t14", "jedna teza: zielona karta z hasłem")]
            elif len(it) == 1 and any(b["k"] == "hero" for b in it[0]["blocks"]):
                decs = [_dec(ctx, "fakt-z-liczba", "t37", "jeden fakt z liczbą-bohaterem")]
            elif any(b["k"] == "li" for x in it for b in x["blocks"]):
                decs = [_dec(ctx, "lista-z-ikona", "t17", "punkty z ikoną")]
        if rec["rek"]:
            rekordy.append(rec["rek"])
        dodaj(sl, rec["bloki"], decs, wz)
    dodaj({"type": "end", "variant": "brand", "hashtag": "#zawszedobra"}, [], wz=_dec(ctx, "zakonczenie", "t64", "zakończenie"))
    bez_hasla = [i for i, sl in enumerate(slides, 1) if "AKAPIT_BEZ_HASLA" in ctx.kody.get(sl.get("zrodlo"), ())]
    if bez_hasla:
        ctx.uwagi.append("Slajdy %s: dłuższy akapit zostaje bez hasła (zdanie ma ponad 24 słowa i nie ma przecinka ani spójnika, na którym da się "
                         "je podzielić) - to jedyny dopuszczalny akapit Lato bez hasła; do decyzji autora." % ", ".join(str(i) for i in bez_hasla[:12]))
    n_tresc = len(out)
    if n_tresc != N:
        if n_tresc > N:
            ctx.uwagi.append("Slajdów z treścią wyszło %d zamiast %d: tyle potrzeba, żeby pismo nie spadło poniżej progów (hasło od 16 pt, "
                             "dopisek od 13 pt) i żeby żaden fragment nie został obcięty." % (n_tresc, N))
        else:
            ctx.uwagi.append("Slajdów z treścią wyszło %d zamiast %d: dokument nie ma więcej osobnych myśli." % (n_tresc, N))
    puste = [sek[i]["naglowek"] for i in range(len(sek)) if sek[i]["naglowek"] and i not in kand_roz and
             not sek[i]["atomy"] and not any(sek[j]["atomy"] for j in range(i + 1, len(sek)) if _w_poddrzewie(sek, i, j))]
    if puste:
        ctx.uwagi.append("Nagłówki bez żadnej treści pod spodem pominąłem (nie ma co pokazać): %s." % "; ".join("„%s”" % x for x in puste[:8]))
    if any(not sek[r["sek"]]["naglowek"] for r in out):
        ctx.uwagi.append("Część dokumentu nie ma nagłówków (tytułów nie wymyślam): jej slajdy mają tytuł dokumentu z numerem - w Wordzie dodaj "
                         "nagłówki, a tytuły slajdów będą zgodne z treścią.")
    ramka = len(slides) - n_tresc
    ctx.uwagi.append("Razem w pliku: %d slajdów (%d z treścią + okładka%s%s i zakończenie)." % (
        len(slides), n_tresc, ", agenda" if agenda else "", (", %d przekładki" % len(rozdz)) if rozdz else ""))
    # --- błędy tekstu (lint): tekst źródła każdego slajdu
    bledy = _lint(m, mapa, ctx.uwagi)
    for w in m.get("ostrzezenia", []):
        ctx.uwagi.append(w)
    spec = {"theme": "shop", "sections": sekcje_pptx, "slides": slides, "mapa_blokow": mapa, "uwagi": ctx.uwagi, "cel": "dokument",
            "szablon": decyzje, "bledy_tekstu": bledy, "warianty": {"wersja": 1, "slajdy": rekordy}, "warianty_plik": "warianty-szablon.json",
            "nazwa": m["nazwa"], "tytul": m["tytul"],
            "ustawienia": {"slajdy": n_tresc, "rozdzialy": len(rozdz), "razem": len(slides), "ramka": ramka},
            "output": _nazwa_wyniku(m, ust.get("wyjscie"))}
    return spec


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
        return [" ".join(w) for w in b["wiersze"]]
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


def _akapity_pptx(pptx):
    """Slajdy pptx -> [Counter tokenów slajdu] (cały tekst: tytuły, pola, tabele, grupy; bez numerów stron)."""
    from pptx import Presentation
    from pptx.oxml.ns import qn
    prs = Presentation(pptx)
    out = []
    for sl in prs.slides:
        c = collections.Counter()
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
    """Czy każdy akapit dokumentu (>= 95% jego słów) stoi na slajdach pptx? Szuka po kolei, od slajdu, na którym skończył poprzedni akapit,
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
    return {"akapity": n, "przeniesione": ok, "brakuje": brak, "procent": round(pct, 1),
            "tekst": ("Treść: 100%% akapitów (%d/%d) przeniesionych" % (ok, n)) if ok == n else
                     ("Treść: %.1f%% akapitów (%d/%d) przeniesionych, brakuje %d" % (pct, ok, n, n - ok))}


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
