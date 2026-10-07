# -*- coding: utf-8 -*-
"""
pptx_convert.py - konwersja GOTOWEJ prezentacji (.pptx) na styl Dobra Kaloria, bez utraty treści (06-07.10.2026).

    python pptx_convert.py <plik.pptx> [--cel wiernie|rozwin|skroc] [--sekcje r01,r02] [--slajdy N]
                           [--bez-wizualizacji] [--wyjscie katalog] [--robocze katalog] [--bez-qa]

Kroki, każdy używany osobno przez program "Stwórz prezentację" (engine.py):
  extract(pptx, rob)        -> model treści: per slajd teksty (rozmiar, kolor, pozycja; także z grup i SmartArt),
                               tabele, wykresy, obrazy (rob\\img\\sNN_id.ext), hiperłącza, notatki, sekcje
  compose(model, opts)      -> spec dla build_dk.py (theme shop). ZASADA 1:1 (user 07.10): slajd N = slajd N, te same
                               teksty i kolejność, układ z POZYCJI na starym slajdzie (typ `uklad`: wiersze, kolumny-karty,
                               osobne etykiety jako `tag` / `meta`, hasła w ramkach, obrazy w całości). Slajd dzielimy
                               dopiero, gdy tekst nie mieści się pismem 13 pt - i mówimy o tym w uwagach.
                               Cele (CELE): wiernie | rozwin | skroc - baza jest zawsze ta sama, różni się polecenie
                               dla AI; rozdziały wyłączone w `sekcje` zostają w pliku jako slajdy UKRYTE.
                               POJEMNIK Z SZABLONU (user 07.10, lekcje A42-A43): tekst zostaje 1:1, a typ pojemnika
                               (karta, równe karty, kafle, punkty, cytat, karta-artykuł, obrazy + podpis) dobiera się
                               do kształtu treści regułami R0-R12 (references/konwersja-pptx.md pkt 2a); Mindset tylko
                               tytuł i hasła do ok. 12 słów, reszta Lato; tło zawsze białe, krem tylko w kartach.
                               Polecenie dla AI po konwersji: CELE[cel]["polecenie"] (jedno źródło dla programu, CLI
                               i dokumentów; wczytanie skilla i design systemu ds-dobra-kaloria jest w nim wprost).
                               Test bez PowerPointa: python -m pytest test_konwersja.py (-k tabela = regresja 4 plików).
  coverage(src, out, mapa)  -> kontrola 100% akapitów źródła w wyniku (tokeny)
  wiernosc(model, out, mapa)-> kontrola układu: osobne napisy osobno, kolejność góra-dół, liczby, slajdów tyle samo
Zasada nr 1: zero utraty treści. Literówek źródła nie poprawiamy - po to jest chat AI z gotowego polecenia.
Wielkość liter zmieniamy tylko tam, gdzie źródło wyświetla wersaliki (zmiany: <rob>\\wielkosc-liter.txt).
"""
import argparse
import collections
import hashlib
import json
import os
import re
import statistics
import sys
import zipfile

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_dk  # noqa: E402
from build_deck import cm  # noqa: E402

EMU_CM = 360000
NS_DGM = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
NS_P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
SKIP_PH = (PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.DATE)
TITLE_PH = (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE, PP_PLACEHOLDER.VERTICAL_TITLE)
BODY_PH = (PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT, PP_PLACEHOLDER.VERTICAL_BODY, PP_PLACEHOLDER.VERTICAL_OBJECT)
DEFAULT_PT = 18.0          # rozmiar, gdy źródło go nie podaje (dziedziczy z układu)
MAX_IMG_PX = 2400          # większe obrazy zmniejszamy (rozmiar pliku), proporcje bez zmian


# =====================================================================================================
# 1. EXTRACT
# =====================================================================================================
def otworz(pptx, rob):
    """Presentation(); .ppsx / .potx / .pptm mają te same części, inny typ treści - czytamy kopię z poprawionym typem."""
    if os.path.splitext(pptx)[1].lower() == ".ppt":
        raise ValueError("To stary format .ppt. Otwórz plik w PowerPoint i zapisz jako .pptx.")
    try:
        return Presentation(pptx)
    except ValueError:
        pass
    os.makedirs(rob, exist_ok=True)
    kopia = os.path.join(rob, "_zrodlo.pptx")
    main = b"application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
    olds = [b"application/vnd.openxmlformats-officedocument.presentationml.slideshow.main+xml",
            b"application/vnd.openxmlformats-officedocument.presentationml.template.main+xml",
            b"application/vnd.ms-powerpoint.presentation.macroEnabled.main+xml",
            b"application/vnd.ms-powerpoint.slideshow.macroEnabled.main+xml",
            b"application/vnd.ms-powerpoint.template.macroEnabled.main+xml"]
    with zipfile.ZipFile(pptx) as zi, zipfile.ZipFile(kopia, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            data = zi.read(it.filename)
            if it.filename == "[Content_Types].xml":
                for o in olds:
                    data = data.replace(o, main)
            zo.writestr(it, data)
    return Presentation(kopia)


def _scale_of(sh):
    """fontScale z normAutofit (PowerPoint zmniejszył tekst, żeby się zmieścił) -> mnożnik rozmiaru."""
    try:
        v = sh._element.xpath(".//a:bodyPr/a:normAutofit/@fontScale")
        return float(v[0]) / 100000.0 if v else 1.0
    except Exception:
        return 1.0


def _pt_of(par, scale, lst_pt):
    sizes = collections.Counter()
    for r in par.runs:
        if r.font.size and r.text.strip():
            sizes[r.font.size.pt] += len(r.text)
    pt = sizes.most_common(1)[0][0] if sizes else None
    if pt is None and par.font.size:
        pt = par.font.size.pt
    if pt is None:
        pt = lst_pt
    return round(pt * scale, 1) if pt else None


def _url_of(par):
    """Adres hiperłącza, jeśli obejmuje większość akapitu."""
    tot = sum(len(r.text) for r in par.runs) or 1
    for r in par.runs:
        try:
            a = r.hyperlink.address
        except Exception:
            a = None
        if a and len(r.text) >= 0.6 * tot:
            return a
    return None


def _links_of(par):
    out = []
    for r in par.runs:
        try:
            a = r.hyperlink.address
        except Exception:
            a = None
        if a:
            out.append((r.text.strip(), a))
    return out


def _is_li(p, body_ph):
    pPr = p._p.pPr
    if pPr is not None:
        if pPr.find(qn("a:buNone")) is not None:
            return False
        if pPr.find(qn("a:buChar")) is not None or pPr.find(qn("a:buAutoNum")) is not None:
            return True
    return p.level > 0 or body_ph


CAPS_FONTS = ("mindset", "bebas")  # czcionki bez małych liter: slajd pokazuje wersaliki niezależnie od zapisu w pliku


def _styl(par, scale=1.0):
    """(wiersze akapitu tak, jak je widać - podział na a:br, cechy całego akapitu). Wiersz: t, runs [(tekst, kolor)],
    pt (rozmiar przeważający w wierszu albo None). Akapit: kols = udziały kolorów (None = dziedziczony),
    b = pogrubienie, caps = wyświetlany wersalikami, al = wyrównanie."""
    def new():
        return {"t": "", "runs": [], "sz": collections.Counter(), "eu": False}
    lines, cur, tot = [], new(), collections.Counter()
    n = bold = caps = 0
    for el in par._p:
        if el.tag == qn("a:br"):
            lines.append(cur)
            cur = new()
            continue
        if el.tag not in (qn("a:r"), qn("a:fld")):
            continue
        t = "".join(x.text or "" for x in el.iter(qn("a:t")))
        k = len(t.strip())
        rPr, c = el.find(qn("a:rPr")), None
        if rPr is not None:
            sf = rPr.find(qn("a:solidFill"))
            if sf is not None and len(sf):
                c = sf[0].get("val")
            lat = rPr.find(qn("a:latin"))
            bold += k if rPr.get("b") == "1" else 0
            if rPr.get("cap") == "all" or (lat is not None and (lat.get("typeface") or "").lower().startswith(CAPS_FONTS)):
                caps += k
            if rPr.get("sz") and k:
                cur["sz"][int(rPr.get("sz"))] += k
        cur["t"] += t
        cur["runs"].append((t, c))
        if k:  # 10.10 (runda 4): wiersz konczacy sie hiperlaczem konczy zdanie (s41: „…udaru” + wiersz „Dla segmentu…”)
            cur["eu"] = rPr is not None and rPr.find(qn("a:hlinkClick")) is not None
        tot[c] += k
        n += k
    lines.append(cur)
    s = sum(tot.values()) or 1
    a = par.alignment
    al = None if a is None else ("c" if "CENTER" in str(a) else "r" if "RIGHT" in str(a) else "l")
    return ([{"t": ln["t"], "runs": ln["runs"], "eu": ln["eu"],
              "pt": round(ln["sz"].most_common(1)[0][0] / 100.0 * scale, 1) if ln["sz"] else None} for ln in lines],
            {"kols": {c: v / s for c, v in tot.items() if v}, "b": n > 0 and bold > 0.6 * n,
             "caps": n > 0 and caps > 0.6 * n, "al": al})


def _text_block(sh, geo, ph):
    scale = _scale_of(sh)
    try:
        lst = sh._element.xpath(".//a:lstStyle/a:lvl1pPr/a:defRPr/@sz")
        lst_pt = float(lst[0]) / 100.0 if lst else None
    except Exception:
        lst_pt = None
    pars = [p for p in sh.text_frame.paragraphs]
    body_ph = ph in BODY_PH and len([p for p in pars if p.text.strip()]) >= 2
    out, links, odstep = [], [], False
    for p in pars:
        t = p.text
        if not t.strip():
            odstep = bool(out)  # pusty akapit między myślami: autor oddzielił je odstępem
            continue
        pt = _pt_of(p, scale, lst_pt) or (44.0 if ph in TITLE_PH else None)  # tytuł bez rozmiaru dziedziczy duży z układu
        linie, st = _styl(p, scale)
        out.append({"t": t, "pt": pt, "li": _is_li(p, body_ph), "url": _url_of(p), "odstep": odstep, "linie": linie,
                    **st})
        odstep = False
        links += _links_of(p)
    if not out:
        return None, links
    return dict(kind="text", ph=ph, paras=out, **geo), links


def _diagram_texts(sh, slide):
    """Teksty SmartArt (węzły diagramu) - python-pptx ich nie udostępnia."""
    try:
        el = next(sh._element.iter("{%s}relIds" % NS_DGM), None)
        if el is None:
            return []
        part = slide.part.related_part(el.get(qn("r:dm")))
        xml = etree.fromstring(part.blob)
        out = []
        for pt in xml.iter("{%s}pt" % NS_DGM):
            if pt.get("type", "node") in ("node", "asst"):
                t = "".join(x.text or "" for x in pt.iter(qn("a:t"))).strip()
                if t:
                    out.append(t)
        return out
    except Exception:
        return []


def _chart(sh, geo, uwagi, n):
    try:
        ch = sh.chart
        plot = ch.plots[0]
        cats = [str(c) for c in plot.categories]
        ser = []
        for s in plot.series:
            ser.append({"name": str(s.name or ""), "values": [None if v is None else float(v) for v in s.values]})
        if len(ch.plots) > 1:
            uwagi.append("Slajd %d: wykres złożony - przeniesiono tylko pierwszy układ serii." % n)
        title = ""
        if ch.has_title and ch.chart_title.has_text_frame:
            title = ch.chart_title.text_frame.text.strip()
        return dict(kind="chart", typ=str(ch.chart_type), cats=cats, series=ser, title=title, **geo)
    except Exception as e:
        uwagi.append("Slajd %d: nie udało się odczytać wykresu (%s) - sprawdź go ręcznie." % (n, e))
        return None


def _wypelnienie_obrazem(sh, slide):
    """Obraz wstawiony jako WYPEŁNIENIE kształtu (a:blipFill w p:spPr): tak zapisują zdjęcia Canva i Google Slides, tak
    wygląda też zdjęcie przycięte do kształtu. python-pptx nie widzi go jako obrazu, więc do 07.10.2026 takie zdjęcia
    ginęły bez śladu. Zwraca {blob, ext, px, crop} albo None."""
    el = sh._element
    if el.tag != qn("p:sp"):
        return None
    spPr = el.find(qn("p:spPr"))
    bf = spPr.find(qn("a:blipFill")) if spPr is not None else None
    blip = bf.find(qn("a:blip")) if bf is not None else None
    rid = blip.get(qn("r:embed")) if blip is not None else None
    if not rid:
        return None
    try:
        part = slide.part.related_part(rid)
        im = part.image
        src = bf.find(qn("a:srcRect"))
        crop = [min(0.9, max(0.0, int(src.get(k, 0)) / 100000.0)) for k in ("l", "t", "r", "b")] if src is not None \
            else [0.0] * 4
        try:
            px = im.size
        except Exception:
            px = None
        return dict(blob=part.blob, ext=im.ext.lower(), px=px, crop=crop)
    except Exception:
        return None


def _sceny(good, img_dir, n):
    """Obrazy nachodzące na siebie (kolaż, paczka z owocami) -> jedna grafika złożona dokładnie w ich układzie
    (kolejność warstw i obrót jak na slajdzie). Dzięki temu kolaż zostaje kolażem, a nie rozsypuje się na osobne
    obrazki. Pozostałe obrazy bez zmian."""
    grp = list(range(len(good)))

    def find(i):
        while grp[i] != i:
            i = grp[i]
        return i
    for i, a in enumerate(good):
        for j in range(i):
            b = good[j]
            ox = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
            oy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            if ox > 0 and oy > 0 and ox * oy >= 0.12 * min(a["w"] * a["h"], b["w"] * b["h"]):
                grp[find(i)] = find(j)
    sets = collections.defaultdict(list)
    for i in range(len(good)):
        sets[find(i)].append(i)
    out, k = [], 0
    for root in sorted(sets, key=lambda r: min(sets[r])):
        idx = sets[root]
        if len(idx) == 1:
            out.append(good[idx[0]])
            continue
        ims = [good[i] for i in idx]
        x0, y0 = min(i["x"] for i in ims), min(i["y"] for i in ims)
        x1, y1 = max(i["x"] + i["w"] for i in ims), max(i["y"] + i["h"] for i in ims)
        ppc = min(70.0, 1800.0 / max(x1 - x0, y1 - y0, 0.1))
        try:
            cv = Image.new("RGBA", (max(1, int((x1 - x0) * ppc)), max(1, int((y1 - y0) * ppc))), (0, 0, 0, 0))
            for im in ims:  # kolejność na liście = kolejność warstw na slajdzie
                src = Image.open(im["path"]).convert("RGBA").resize(
                    (max(1, int(im["w"] * ppc)), max(1, int(im["h"] * ppc))), Image.LANCZOS)
                if abs(im.get("rot") or 0) > 0.5:
                    src = src.rotate(-im["rot"], expand=True, resample=Image.BICUBIC)
                cx, cy = (im["x"] + im["w"] / 2 - x0) * ppc, (im["y"] + im["h"] / 2 - y0) * ppc
                layer = Image.new("RGBA", cv.size, (0, 0, 0, 0))  # warstwa: obrócony obraz może wystawać poza kadr
                layer.paste(src, (int(cx - src.width / 2), int(cy - src.height / 2)))
                cv = Image.alpha_composite(cv, layer)
            k += 1
            path = os.path.join(img_dir, "s%02d_kolaz%d.png" % (n, k))
            cv.save(path)
            out.append(dict(path=path, x=x0, y=y0, w=x1 - x0, h=y1 - y0, px=cv.size, rot=0, kolaz=len(ims)))
        except Exception:
            out += ims  # nie udało się złożyć: obrazy zostają osobno, nic nie ginie
    return out


def _walk(shapes, tf, slide, n, acc, uwagi):
    """tf = (a, b, sx, sy): współrzędna dziecka grupy -> współrzędna na slajdzie (x = a + x_dziecka * sx)."""
    for sh in shapes:
        l, t = sh.left or 0, sh.top or 0
        w, h = sh.width or 0, sh.height or 0
        x, y = tf[0] + l * tf[2], tf[1] + t * tf[3]
        gw, gh = w * tf[2], h * tf[3]
        geo = dict(x=x / EMU_CM, y=y / EMU_CM, w=gw / EMU_CM, h=gh / EMU_CM, id=sh.shape_id, name=sh.name)
        st = sh.shape_type
        ph = None
        if sh.is_placeholder:
            try:
                ph = sh.placeholder_format.type
            except Exception:
                ph = None
            if ph in SKIP_PH:
                continue
        if st == MSO_SHAPE_TYPE.GROUP:
            xf = sh._element.grpSpPr.find(qn("a:xfrm"))
            co, ce = xf.find(qn("a:chOff")), xf.find(qn("a:chExt"))
            cx, cy = (int(ce.get("cx")) or 1), (int(ce.get("cy")) or 1)
            sx, sy = gw / cx, gh / cy
            _walk(sh.shapes, (x - int(co.get("x")) * sx, y - int(co.get("y")) * sy, sx, sy), slide, n, acc, uwagi)
            continue
        if getattr(sh, "has_table", False) and sh.has_table:
            rows = []
            for r in sh.table.rows:
                rows.append([" ".join(c.text.split()) if not c.is_spanned else "" for c in r.cells])
            acc["tables"].append(dict(kind="table", rows=rows, **geo))
            continue
        if getattr(sh, "has_chart", False) and sh.has_chart:
            c = _chart(sh, geo, uwagi, n)
            if c:
                acc["charts"].append(c)
            continue
        if st == MSO_SHAPE_TYPE.PICTURE or (sh.is_placeholder and hasattr(sh, "image") and ph == PP_PLACEHOLDER.PICTURE):
            try:
                im = sh.image
                blob, ext = im.blob, im.ext.lower()
                try:
                    px = im.size
                except Exception:
                    px = None
                crop = [getattr(sh, a, 0.0) or 0.0 for a in ("crop_left", "crop_top", "crop_right", "crop_bottom")]
            except Exception:
                uwagi.append("Slajd %d: nie udało się odczytać obrazu '%s'." % (n, sh.name))
                continue
            try:
                link = sh.click_action.hyperlink.address
            except Exception:
                link = None
            if link:
                acc["links"].append(("", link))
            acc["pics"].append(dict(kind="pic", blob=blob, ext=ext, px=px, crop=crop, sha=hashlib.sha1(blob).hexdigest(),
                                    rot=getattr(sh, "rotation", 0) or 0, **geo))
            continue
        fill = _wypelnienie_obrazem(sh, slide)
        if fill:  # zdjęcie jako wypełnienie kształtu; kształt może mieć też tekst, więc idziemy dalej
            acc["pics"].append(dict(kind="pic", sha=hashlib.sha1(fill["blob"]).hexdigest(),
                                    rot=getattr(sh, "rotation", 0) or 0, **fill, **geo))
        if st in (MSO_SHAPE_TYPE.MEDIA, MSO_SHAPE_TYPE.WEB_VIDEO):
            uwagi.append("Slajd %d: film / dźwięk '%s' nie jest przenoszony - dodaj go ręcznie." % (n, sh.name))
            continue
        if st in (MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT, MSO_SHAPE_TYPE.LINKED_OLE_OBJECT):
            uwagi.append("Slajd %d: obiekt osadzony '%s' (np. Excel) nie jest przenoszony." % (n, sh.name))
            continue
        if sh._element.tag == qn("p:graphicFrame") and next(sh._element.iter("{%s}relIds" % NS_DGM), None) is not None:
            txts = _diagram_texts(sh, slide)
            if txts:
                acc["texts"].append(dict(kind="text", ph=None, paras=[{"t": t, "pt": None, "li": True, "url": None}
                                                                      for t in txts], **geo))
            continue
        if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
            blk, links = _text_block(sh, geo, ph)
            if blk:
                acc["texts"].append(blk)
            acc["links"] += links
            try:
                lk = sh.click_action.hyperlink.address
                if lk:
                    acc["links"].append(("", lk))
            except Exception:
                pass


def _sections(prs):
    """Sekcje PowerPointa: [(nazwa, [numer slajdu 1..N])] albo []."""
    ids = [int(s.get("id")) for s in prs.slides._sldIdLst]
    out = []
    try:
        for ext in prs.part._element.iter(qn("p:ext")):
            if ext.get("uri") == "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}":
                for sec in ext.iter("{%s}section" % NS_P14):
                    nums = [ids.index(int(i.get("id"))) + 1 for i in sec.iter("{%s}sldId" % NS_P14)
                            if int(i.get("id")) in ids]
                    out.append((sec.get("name") or "", nums))
    except Exception:
        return []
    return [(n, s) for n, s in out if s]


def extract(pptx, rob):
    """Model treści prezentacji. Obrazy: rob\\img\\sNN_id.ext (bez logo i ozdobników)."""
    pptx = os.path.abspath(pptx)
    prs = otworz(pptx, rob)
    wc, hc = prs.slide_width / EMU_CM, prs.slide_height / EMU_CM
    uwagi, slides = [], []
    shas = collections.defaultdict(set)
    poz = collections.defaultdict(collections.Counter)  # obraz -> ile razy stoi w tym samym miejscu
    obok = 0

    def poza(e):  # element w całości poza kadrem slajdu
        return e["x"] >= wc - 0.05 or e["y"] >= hc - 0.05 or e["x"] + e["w"] <= 0.05 or e["y"] + e["h"] <= 0.05
    for n, sl in enumerate(prs.slides, 1):
        acc = {"texts": [], "tables": [], "charts": [], "pics": [], "links": []}
        _walk(sl.shapes, (0, 0, 1, 1), sl, n, acc, uwagi)
        notes = ""
        if sl.has_notes_slide and sl.notes_slide.notes_text_frame is not None:
            notes = sl.notes_slide.notes_text_frame.text.strip()
        out = [b for b in acc["texts"] if poza(b)]
        if out:  # tekst obok slajdu (notatki autora, opisy szablonu) nie jest częścią slajdu, ale nie ginie: do notatek
            acc["texts"] = [b for b in acc["texts"] if not poza(b)]
            extra = "\n".join(" ".join(p["t"].split()) for b in out for p in b["paras"])
            notes = (notes + "\n\n" if notes else "") + "[Obok slajdu w oryginale]\n" + extra
            obok += 1
        acc["pics"] = [p for p in acc["pics"] if not poza(p)]
        for p in acc["pics"]:
            shas[p["sha"]].add(n)
            poz[p["sha"]][(round(p["x"]), round(p["y"]), round(p["w"]))] += 1
        slides.append({"n": n, "uklad": sl.slide_layout.name, "hidden": sl._element.get("show") == "0", "notes": notes,
                       **acc})
    # obrazy: logo / ozdobniki / tła odpadają, reszta trafia na dysk
    img_dir = os.path.join(rob, "img")
    kept = skipped = 0
    for s in slides:
        good = []
        for p in s["pics"]:
            area = (p["w"] * p["h"]) / (wc * hc)
            mx = max(p["px"]) if p["px"] else 0
            why = None
            k = len(shas[p["sha"]])
            if k >= 3 and poz[p["sha"]].most_common(1)[0][1] >= max(3, 0.6 * k):
                why = "stały element na %d slajdach (logo, belka)" % k
            elif k >= 5 and area <= 0.03:  # drobny ozdobnik; większy obraz powtarzany w różnych miejscach to treść
                why = "drobny ozdobnik na %d slajdach" % k
            elif p["px"] and mx <= 160:
                why = "mały ozdobnik"
            elif area >= 0.85 and s["texts"]:
                why = "tło slajdu"
            elif p["ext"] not in ("png", "jpg", "jpeg", "gif", "bmp", "tif", "tiff", "webp") or not p["px"]:
                uwagi.append("Slajd %d: grafika wektorowa / nieobsługiwana (%s) nie została przeniesiona." % (s["n"], p["ext"]))
                why = "format"
            if why:
                skipped += 1
                continue
            os.makedirs(img_dir, exist_ok=True)
            path = os.path.join(img_dir, "s%02d_%d.%s" % (s["n"], p["id"], "jpg" if p["ext"] == "jpeg" else p["ext"]))
            _save_img(p, path)
            good.append(dict(path=path, x=p["x"], y=p["y"], w=p["w"], h=p["h"], px=p["px"], rot=p.get("rot") or 0))
            kept += 1
        s["obrazy"] = _sceny(good, img_dir, s["n"])
        del s["pics"]
    if obok:
        uwagi.append("Tekst leżący obok slajdu (poza kadrem) na %d slajdach trafił do notatek prelegenta." % obok)
    if skipped:
        uwagi.append("Pominięto %d obrazów powtarzających się na slajdach (logo, ozdobniki) albo mniejszych niż 160 px." % skipped)
    akapity = sum(len(m) + len(n) for m, n in _slide_paras(prs))
    return {"plik": pptx, "nazwa": os.path.splitext(os.path.basename(pptx))[0], "w_cm": wc, "h_cm": hc, "slajdy": slides,
            "akapity": akapity,
            "sekcje_zrodla": _sections(prs), "uwagi": uwagi, "rob": rob,
            "stat": {"slajdy": len(slides), "grafiki": kept, "pominiete_grafiki": skipped,
                     "tabele": sum(len(s["tables"]) for s in slides), "wykresy": sum(len(s["charts"]) for s in slides)}}


def _save_img(p, path):
    """Zapis obrazu z uwzględnieniem kadrowania ze slajdu i zmniejszeniem zbyt dużych."""
    import io
    im = Image.open(io.BytesIO(p["blob"]))
    l, t, r, b = p["crop"]
    if any(v > 0.005 for v in p["crop"]):
        W, H = im.size
        im = im.crop((int(l * W), int(t * H), int(W - r * W), int(H - b * H)))
    if max(im.size) > MAX_IMG_PX:
        im.thumbnail((MAX_IMG_PX, MAX_IMG_PX))
    elif not any(v > 0.005 for v in p["crop"]):
        with open(path, "wb") as f:  # bez zmian - oryginalne bajty
            f.write(p["blob"])
        return
    if path.lower().endswith((".jpg", ".jpeg")) and im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    im.save(path)


# =====================================================================================================
# 2. COMPOSE
# =====================================================================================================
_TERM = re.compile(r"[.!?…:;]$")
_MARK = re.compile(r"^\s*(?:[•·▪■◦●‣*]\s*|[–—-]\s+|[–—](?=\S)|\d{1,2}[.)]\s+)")
_DATE = re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b|\b(?:19|20)\d\d\b")
_SRC = re.compile(r"^(źródło|zrodlo|source|za:|dane:)\b", re.I)
_URL = re.compile(r"^https?://\S+$", re.I)
_KPI = re.compile(r"^\s*([~≈>]?\d[\d  .,]*\d|\d)\s*(%|mln|mld|tys\.?|zł|kg|g|x|×)?\s+(.+)$", re.I)


def _clean(t):
    return re.sub(r"\s+", " ", t.replace(" ", " ")).strip()


def _split_vt(text, flags=False, eu=()):
    """Akapit z łamaniami wiersza (\\v): zawinięcie w środku zdania skleja, po kropce i wielkiej literze zaczyna nowy akapit.
    flags=True: lista (tekst, po_pustej_linii, konczy_sie_laczem) - pusta linia to twardy podział akapitu.
    eu = dla każdego wiersza: czy kończy się hiperłączem (10.10: taki wiersz kończy zdanie jak kropka)."""
    out, cur, blank, hard, ends, cur_eu = [], "", False, [], [], False
    for k, ln in enumerate(re.split(r"[\v\n\r]", text)):
        e = bool(eu[k]) if k < len(eu) else False
        ln = _clean(ln)
        if not ln:
            if cur:
                out.append(cur)
                hard.append(blank)
                ends.append(cur_eu)
                cur, blank, cur_eu = "", False, False
            blank = True
            continue
        if cur and (_TERM.search(cur) or cur_eu) and not ln[0].islower():
            out.append(cur)
            hard.append(blank)
            ends.append(cur_eu)
            cur, blank, cur_eu = ln, False, e
        else:
            cur = (cur + " " + ln).strip()
            cur_eu = e
    if cur:
        out.append(cur)
        hard.append(blank)
        ends.append(cur_eu)
    return list(zip(out, hard, ends)) if flags else out


def _med(xs):
    xs = [x for x in xs if x]
    return statistics.median(xs) if xs else DEFAULT_PT


def _order(blocks, h_cm):
    """Kolejność czytania: wiersze (top w granicach ~4% wysokości), w wierszu od lewej."""
    tol, rows = 0.04 * h_cm, []
    for b in sorted(blocks, key=lambda b: (b["y"], b["x"])):
        if rows and abs(b["y"] - rows[-1][0]) <= tol:
            rows[-1][1].append(b)
        else:
            rows.append([b["y"], [b]])
    return [b for _y, r in rows for b in sorted(r, key=lambda b: b["x"])]


def _items(blocks, sklej=True, luzno=False):
    """Bloki tekstu -> pozycje (akapity po rozbiciu \\v), z rozmiarem, znacznikiem listy i numerem pola tekstowego.
    luzno: pole ze zdaniami dużym pismem (08.10) - autor łamie Enterem wycentrowane wiersze różnej długości, więc
    sklejamy bez miary długości ostatniego wiersza (nie przez pustą linię autora)."""
    out = []
    for bi, b in enumerate(blocks):
        vis = [[len(_clean(x)) for x in re.split(r"[\v\n\r]", p["t"]) if x.strip()] for p in b["paras"]]
        ml = max([k for v in vis for k in v] or [0])  # najdłuższy widoczny wiersz pola
        for p, v in zip(b["paras"], vis):
            li = p["li"]
            eu = [ln.get("eu") for ln in p.get("linie") or []]
            for pi, (part, hard, eu_end) in enumerate(_split_vt(p["t"], True, eu)):
                m = _MARK.match(part)
                num = False
                if m and len(part) > m.end() and re.match(r"\s*\d", m.group(0)):
                    li2, num = False, True  # "1. Zrób X": numer zostaje w tekście
                elif m and len(part) > m.end():
                    part, li2 = part[m.end():].strip(), True
                else:
                    li2 = li
                if part:
                    out.append({"t": part, "pt": p["pt"] or DEFAULT_PT, "li": li2, "url": p["url"], "bi": id(b),
                                "x": b["x"], "y": b["y"], "w": b["w"], "hb": hard, "num": num,
                                "ll": v[-1] if v else 0, "ml": ml, "od": bool(p.get("odstep")) and pi == 0,
                                "luzno": luzno, "eu": eu_end})
    return _merge_wraps(out) if sklej else out


def _merge_wraps(items):
    """Autorzy łamią zdania Enterem w środku zdania. Gdy pole tekstu wygląda na prozę (akapity średnio >= 30 znaków),
    akapit bez kropki na końcu skleja się z następnym; krótkie pozycje (listy haseł) zostają osobno."""
    by = collections.defaultdict(list)
    for it in items:
        by[it["bi"]].append(len(it["t"]))
    prose = {bi for bi, ls in by.items() if len(ls) >= 2 and sum(ls) / len(ls) >= 30}
    out = []
    for it in items:
        p = out[-1] if out else None
        if p and it["bi"] in prose and p["bi"] == it["bi"] and not p["li"] and not it["li"] and len(p["t"]) >= 20 \
                and not it.get("num") \
                and not _TERM.search(p["t"]) and not p.get("eu") and abs(p["pt"] - it["pt"]) < 0.5 and not it.get("hb") \
                and not (it.get("luzno") and it.get("od")) \
                and (p.get("ll", 0) >= 0.7 * p.get("ml", 0) or it.get("luzno")):
            p["t"] += ("\x1f" if it.get("luzno") else " ") + it["t"]  # \x1f: miejsce sklejenia (wielkosc liter wg wierszy)
            p["ll"] = it.get("ll", 0)
            p["eu"] = it.get("eu")
        else:
            out.append(dict(it))
    return out


def _header(blocks, h_cm):
    """Nagłówek slajdu: tekst w tytułowym placeholderze albo najwyższy tekst w górnym pasie; None, gdy go nie ma."""
    for b in blocks:
        if b["ph"] in TITLE_PH:
            return b
    band = [b for b in blocks if b["y"] + b["h"] <= 0.22 * h_cm and sum(len(p["t"]) for p in b["paras"]) <= 90]
    if band and len(blocks) > len(band):
        return sorted(band, key=lambda b: (b["y"], -max((p["pt"] or 0) for p in b["paras"])))[0]
    return None


def _body(sl, h_cm):
    """(nagłówek, pozostałe bloki tekstu w kolejności czytania). Nagłówek musi się mieścić w kickerze - dłuższy
    jest zwykłym tekstem slajdu (nic się nie gubi)."""
    hdr = _header(sl["texts"], h_cm)
    if hdr is not None and not _kick_ok(_text_of(hdr)):
        hdr = None
    rest = [b for b in sl["texts"] if b is not hdr]
    return hdr, _order(rest, h_cm)


def _text_of(b):
    return " ".join(_clean(t) for p in b["paras"] for t in _split_vt(p["t"]))


def _words(blocks):
    return sum(len(_text_of(b).split()) for b in blocks)


def is_section(sl, h_cm, first):
    """Slajd-przerywnik: jedno krótkie hasło (<= 6 słów) dużą czcionką (>= 54 pt), bez grafik, tabel i wykresów."""
    if first or sl["tables"] or sl["charts"] or sl["obrazy"]:
        return None
    hdr, rest = _body(sl, h_cm)
    if len(rest) != 1:
        return None
    b = rest[0]
    if _words(rest) > 6 or max((p["pt"] or DEFAULT_PT) for p in b["paras"]) < 54:
        return None
    return _text_of(b)


def _chap_name(t):
    """Nazwa rozdziału z hasła przerywnika: WERSALIKI -> zwykłe litery, ale skróty (GLP-1, NPD) zostają."""
    t = _clean(t)
    return t[:1] + t[1:].lower() if t.isupper() and (" " in t or len(t) > 8) else t


def detect_chapters(model):
    """Rozdziały: sekcje PowerPointa (gdy są) albo przerywniki. [{id, nazwa, slajdy[n...], numer}]"""
    sl, hc = model["slajdy"], model["h_cm"]
    chapters = []
    if len(model["sekcje_zrodla"]) > 1:
        seen = set()
        for i, (name, nums) in enumerate(model["sekcje_zrodla"], 1):
            chapters.append({"id": "r%02d" % i, "nazwa": name.strip() or "Rozdział %d" % i, "slajdy": list(nums), "numer": i})
            seen |= set(nums)
        rest = [s["n"] for s in sl if s["n"] not in seen]  # slajdy poza sekcjami - do poprzedniego rozdziału
        if rest:
            chapters[0]["slajdy"] = sorted(chapters[0]["slajdy"] + rest)
        return chapters
    cur = {"nazwa": "Początek", "slajdy": [], "numer": None}
    chapters.append(cur)
    k = 0
    for s in sl:
        t = is_section(s, hc, s["n"] == 1)
        if t:
            k += 1
            cur = {"nazwa": _chap_name(t), "slajdy": [], "numer": k}
            chapters.append(cur)
        cur["slajdy"].append(s["n"])
    chapters = [c for c in chapters if c["slajdy"]]
    for i, c in enumerate(chapters, 1):
        c["id"] = "r%02d" % i
    return chapters


# --- miary dopasowania do typów DK (te same funkcje, co w budowie) ------------------------------------------
def _title_fits(t):
    sz = build_dk.title_size(t, 40, 26, cm(26))
    return len(build_dk.display_lines(t, sz, cm(26))) * sz <= 84 and len(t) <= 110


def _kick_ok(t):
    """Kicker: jedna linia 14 pt bold WERSALIKAMI z rozstrzałem 1,5 pt w polu 20 cm."""
    return build_dk.bd.text_w_emu(t.upper(), 14, "Lato Bold") + len(t) * 1.5 * 12700 <= cm(19.5)


def _stmt_size(t):
    """Największy rozmiar (pt), przy którym hasło ma <= ~7,6 cm wysokości; 0 = nie mieści się nawet przy 34 pt."""
    for sz in range(60, 33, -2):
        if len(build_dk.display_lines(t, sz, cm(26))) * sz <= 215:
            return sz
    return 0


def _stmt(kicker, text, source=None):
    sp = {"type": "statement", "kicker": kicker, "text": text, "max_pt": _stmt_size(text) or 34}
    if source:
        sp["note"] = source
    return sp


def _lead_fits(t):
    return len(build_dk.lines_for(t, 26, cm(24))) <= 6


def _article_fits(paras):
    tw = build_dk.W - 2 * build_dk.MX - cm(1.2) - cm(6.4)
    for size in (16, 15, 14, 13):
        th = sum(len(build_dk.lines_for(p, size, tw)) for p in paras) * size * 1.45 * 12700 + (len(paras) - 1) * cm(0.5)
        if th <= build_dk.CB - build_dk.CT - cm(2.4):
            return True
    return False


def _one_line(t, size=20):
    return len(build_dk.lines_for(t, size, build_dk.W - 2 * build_dk.MX - cm(2), "bold")) == 1


def _pick_title(items, allow_single=False):
    """(pozycja-tytuł, reszta): tytuł to krótki pierwszy akapit wyraźnie wyróżniony - większy od reszty, pytanie /
    dwukropek albo bardzo krótki przed długim tekstem."""
    if not items or (len(items) < 2 and not allow_single):
        return None, items
    a, rest = items[0], items[1:]
    t = a["t"]
    if a["li"] or len(t) > 70 or t.endswith((".", ";", ",", "…")) or _URL.match(t):
        return None, items
    mx = max([i["pt"] for i in rest] or [0])
    longer = bool(rest) and len(rest[0]["t"]) >= 2.5 * len(t)
    if (not rest and a["pt"] >= 30) or (rest and (a["pt"] > 1.12 * mx or t.endswith(("?", ":")) or
                                                  (len(t) <= 40 and longer and a["pt"] >= 0.95 * mx))):
        if _title_fits(t):
            return a, rest
    return None, items


def _is_head(it, med):
    return (not it["li"] and len(it["t"]) <= 60 and not it["t"].endswith((".", ";", ",")) and
            (it["pt"] >= 1.25 * med or it["t"].endswith(":")))


def _blocks_of(items):
    """Pozycje -> bloki dla typu flow: li / h / url / p (krótkie wiersze tego samego pola tekstowego -> jeden akapit z łamaniami)."""
    med = _med([i["pt"] for i in items])
    out, i = [], 0
    while i < len(items):
        it = items[i]
        if it["li"]:
            out.append({"k": "li", "t": it["t"], **({"url": it["url"]} if it["url"] else {})})
        elif _URL.match(it["t"]) or it["url"]:
            out.append({"k": "url", "t": it["t"], "url": it["url"] or it["t"]})
        elif _is_head(it, med) and i + 1 < len(items):
            out.append({"k": "h", "t": it["t"]})
        else:
            lines = [it["t"]]
            while (i + 1 < len(items) and items[i + 1]["bi"] == it["bi"] and not items[i + 1]["li"] and
                   not items[i + 1]["url"] and len(items[i + 1]["t"]) <= 48 and len(lines[-1]) <= 48 and
                   not _is_head(items[i + 1], med)):
                i += 1
                lines.append(items[i]["t"])
            out.append({"k": "p", "t": "\n".join(lines)})
        i += 1
    return out


def _split_sentences(t):
    parts = re.split(r"(?<=[.!?…])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ0-9„\"(])", t)
    if len(parts) == 1:
        w = t.split()
        parts = [" ".join(w[:len(w) // 2]), " ".join(w[len(w) // 2:])]
    return parts


def _chunk(blocks, w, h, min_size=15):
    """Dzieli bloki na grupy, z których każda mieści się w (w x h) przy rozmiarze >= min_size. Nic nie ucina."""
    sizes = tuple(s for s in build_dk.FLOW_SIZES if s >= min_size)
    work, chunks, cur = list(blocks), [], []
    while work:
        b = work.pop(0)
        if build_dk.flow_layout(cur + [b], w, h, sizes):
            cur.append(b)
            continue
        if cur:
            work.insert(0, b)
            if cur[-1]["k"] == "h" and len(cur) > 1:  # nagłówek nie zostaje sam na końcu slajdu
                work.insert(0, cur.pop())
            chunks.append(cur)
            cur = []
            continue
        parts = _split_sentences(b["t"].replace("\n", " ") if b["k"] != "p" else b["t"])
        if len(parts) < 2:  # pojedyncze słowo-gigant: zostaje (i tak mieści się po zmniejszeniu pisma)
            cur.append(b)
            continue
        half = len(parts) // 2 or 1
        work.insert(0, {**b, "t": " ".join(parts[half:])})
        work.insert(0, {**b, "t": " ".join(parts[:half])})
    if cur:
        chunks.append(cur)
    return chunks


def _suffix(spec, k, n):
    if n > 1:
        key = "title" if spec.get("title") else "kicker"
        if spec.get(key):
            spec[key] = "%s (%d/%d)" % (spec[key], k, n)
    return spec


def _head(hdr, t):
    """(kicker, title) dla typu z miejscem na tytuł: nagłówek slajdu -> kicker, tytuł z treści -> title."""
    if t:
        return (hdr if hdr and _kick_ok(hdr) else None), t
    if hdr and _title_fits(hdr):
        return None, hdr
    return (hdr if hdr and _kick_ok(hdr) else None), None


def _flow_specs(hdr, title, blocks, imgs=None, kicker_extra=None):
    """Typ flow (albo flow + obrazy) z dzieleniem na kolejne slajdy, gdy tekst się nie mieści."""
    kicker, title = _head(hdr, title)
    pre = []
    if hdr and not kicker and title != hdr:  # nagłówek zbyt długi na kicker i na tytuł - leci jako pierwszy podtytuł
        pre = [{"k": "h", "t": hdr}]
    blocks = pre + blocks
    y0 = build_dk.CT if title else cm(3.6)
    tw = cm(16.6) if imgs else cm(24)
    chunks = _chunk(blocks, tw, build_dk.CB - y0 - cm(0.6))
    specs = []
    for k, ch in enumerate(chunks, 1):
        s = {"type": "flow", "kicker": kicker, "title": title, "blocks": ch}
        if imgs and k == 1:
            s["images"] = imgs
        specs.append(_suffix(s, k, len(chunks)))
    return specs


def _bullets_spec(hdr, t, intro, li_items):
    kicker, title = _head(hdr, t["t"] if t else None)
    if intro and not t:
        it = " ".join(i["t"] for i in intro)
        if _title_fits(it):
            kicker, title = (hdr if hdr and _kick_ok(hdr) else None), it
    return {"type": "bullets", "kicker": kicker, "title": title, "items": [{"title": i["t"]} for i in li_items]}


def _text_specs(items, hdr, imgs=None, allow_single=False):
    """Pozycje tekstu jednego slajdu źródła -> lista slajdów DK. Wybór typu wg kształtu treści."""
    items = [i for i in items if i["t"]]
    if not items:
        if hdr:
            return [_stmt(None, hdr)] if _stmt_size(hdr) else _flow_specs(None, None, [{"k": "p", "t": hdr}])
        return []
    src = [i for i in items if _SRC.match(i["t"]) and len(i["t"]) <= 140]
    source = " · ".join(i["t"] for i in src) or None
    items = [i for i in items if i not in src]
    t, rest = _pick_title(items, allow_single=allow_single)
    n_li = sum(1 for i in rest if i["li"])
    total = sum(len(i["t"]) for i in rest)
    has_url = any(i["url"] or _URL.match(i["t"]) for i in rest)  # adresy zostają w zwykłym tekście (flow), z hiperłączem
    specs = None
    if not rest and t:
        specs = [_stmt(hdr if hdr and _kick_ok(hdr) else None, t["t"], source)] if _stmt_size(t["t"]) else None
    # kpis: 2-4 krótkie frazy zaczynające się od liczby
    if specs is None and 2 <= len(rest) <= 4 and not n_li and all(len(i["t"]) <= 90 and _KPI.match(i["t"]) for i in rest) \
            and not imgs:
        ks = []
        for i in rest:
            m = _KPI.match(i["t"])
            ks.append({"value": (m.group(1) + (m.group(2) or "")).replace(" ", "").strip(), "label": m.group(3)})
        if all(len(k["value"]) <= 9 for k in ks):
            kicker, title = _head(hdr, t["t"] if t else None)
            specs = [{"type": "kpis", "kicker": kicker, "title": title, "items": ks}]
    if specs is None and not imgs:
        # statement: krótki tekst bez tytułu
        if not t and not n_li and not has_url and len(rest) <= 3 and total <= 220 and \
                _stmt_size("\n".join(i["t"] for i in rest)):
            specs = [_stmt(hdr if hdr and _kick_ok(hdr) else None, "\n".join(i["t"] for i in rest), source)]
        # lead: tytuł + 1-3 krótkie zdania
        elif t and not n_li and not has_url and len(rest) <= 3 and total <= 240 and \
                _lead_fits(" ".join(i["t"] for i in rest)):
            kicker, title = _head(hdr, t["t"])
            specs = [{"type": "lead", "kicker": kicker, "title": title, "lead": " ".join(i["t"] for i in rest)}]
    if specs is None and not imgs:
        # lista: bullets (3-6 krótkich pozycji) albo flow
        intro = []
        for i in rest:
            if i["li"]:
                break
            intro.append(i)
        li_items = [i for i in rest if i["li"]]
        if li_items and len(intro) + len(li_items) == len(rest) and 2 <= len(li_items) <= 6 and \
                all(len(i["t"]) <= 66 and _one_line(i["t"]) for i in li_items) and (not t or not intro) and \
                (not intro or _title_fits(" ".join(i["t"] for i in intro))):
            specs = [_bullets_spec(hdr, t, intro, li_items)]
        elif not li_items and not has_url and not any(i.get("num") for i in rest) and 3 <= len(rest) <= 6 and \
                all(len(i["t"]) <= 66 and _one_line(i["t"]) for i in rest):
            specs = [_bullets_spec(hdr, t, [], rest)]
        # artykuł: 1-3 długie akapity pod tytułem
        elif not li_items and not has_url and rest and len(rest) <= 5 and sum(len(i["t"]) for i in rest) / len(rest) >= 40 and sum(len(i["t"]) for i in rest) >= 150 and \
                _head(hdr, t["t"] if t else None)[1] and _article_fits([i["t"] for i in rest]):
            kicker, title = _head(hdr, t["t"] if t else None)
            specs = [{"type": "article", "kicker": kicker, "title": title, "paragraphs": [i["t"] for i in rest]}]
    if specs is None:
        specs = _flow_specs(hdr, t["t"] if t else None, _blocks_of(rest), imgs=imgs)
    if source and specs and not (specs[-1]["type"] == "statement" and specs[-1].get("note")):
        _put_source(specs, source)
    return specs


def _put_source(specs, source):
    """Linia 'Źródło: ...' -> stopka slajdu (statement: podpis pod hasłem). Bardzo długie źródło dostaje własny blok."""
    last = specs[-1]
    if last["type"] == "statement":
        last["note"] = source
    elif len(source) <= 130:
        last["source"] = (last["source"] + " · " if last.get("source") else "") + source
    else:
        last["source"] = source[:127] + "..."
        specs += _flow_specs(None, None, [{"k": "small", "t": source}])


# --- kolumny ----------------------------------------------------------------------------------------------
def _columns(blocks, w_cm):
    """Bloki w 2-4 kolumnach (klastry po nakładaniu się w poziomie) albo None."""
    if len(blocks) < 2 or any(b["w"] > 0.58 * w_cm for b in blocks):
        return None
    cl = []
    for b in sorted(blocks, key=lambda b: b["x"]):
        for c in cl:
            ov = min(c["x1"], b["x"] + b["w"]) - max(c["x0"], b["x"])
            if ov > 0.3 * min(b["w"], c["x1"] - c["x0"]):
                c["bs"].append(b)
                c["x0"], c["x1"] = min(c["x0"], b["x"]), max(c["x1"], b["x"] + b["w"])
                break
        else:
            cl.append({"x0": b["x"], "x1": b["x"] + b["w"], "bs": [b]})
    return cl if 2 <= len(cl) <= 8 else None


def _col_spec(c):
    """Klaster bloków -> kolumna {title, blocks}. Nagłówek: górne, wyraźnie większe i krótkie pole tekstu."""
    bs = sorted(c["bs"], key=lambda b: b["y"])
    its = _items(bs)
    title = None
    if len(bs) >= 2 and its:
        first = _items(bs[:1])
        rest_pt = max([i["pt"] for i in _items(bs[1:])] or [0])
        txt = " ".join(i["t"] for i in first)
        if len(txt) <= 60 and not any(i["li"] for i in first) and max(i["pt"] for i in first) >= 1.2 * rest_pt:
            title, its = txt, _items(bs[1:])
    return {"title": title, "blocks": _blocks_of(its)}


def _cols_specs(cols, hdr, t):
    """Kolumny -> text_cols (albo flow, gdy się nie mieszczą nawet po zmniejszeniu pisma)."""
    kicker, title = _head(hdr, t)
    if len(cols) <= 4 and build_dk.text_cols_layout(cols, bool(title))["size"]:
        return [{"type": "text_cols", "kicker": kicker, "title": title, "columns": cols}]
    bl = []  # za dużo kolumn / tekstu na jeden slajd: kolejno nagłówek + treść każdej kolumny, z podziałem na slajdy
    for c in cols:
        bl += ([{"k": "h", "t": c["title"]}] if c["title"] else []) + c["blocks"]
    return _flow_specs(hdr, t, bl)


def _headgroups(items):
    """Powtarzający się układ 'nagłówek + treść' w pionie (2-4 grupy) -> kolumny albo None."""
    med = _med([i["pt"] for i in items])
    heads = [k for k, i in enumerate(items) if not i["li"] and len(i["t"]) <= 60 and i["pt"] >= 1.25 * med
             and not i["t"].endswith((".", ";", ","))]
    if not (2 <= len(heads) <= 4) or heads[0] != 0:
        return None
    cols = []
    for a, b in zip(heads, heads[1:] + [len(items)]):
        body = items[a + 1:b]
        if not body:
            return None
        cols.append({"title": items[a]["t"], "blocks": _blocks_of(body)})
    return cols


# --- obrazy -----------------------------------------------------------------------------------------------
def _captions(imgs, blocks):
    """(podpisy {nr obrazu: tekst}, wspólny podpis, bloki bez podpisów). Podpis = drobny tekst tuż pod obrazem."""
    caps, note, left = {}, [], []
    for b in blocks:
        text = _text_of(b)
        small = max((p["pt"] or DEFAULT_PT) for p in b["paras"]) <= 24
        near = []
        for k, im in enumerate(imgs):
            bottom = im["y"] + im["h"]
            ov = min(im["x"] + im["w"], b["x"] + b["w"]) - max(im["x"], b["x"])
            if small and len(text) <= 160 and bottom - 0.8 <= b["y"] <= bottom + 2.5 and ov >= 0.25 * min(im["w"], b["w"]):
                near.append(k)
        if len(near) == 1:
            caps[near[0]] = (caps.get(near[0], "") + " " + text).strip()
        elif len(near) > 1:
            note.append(text)
        else:
            left.append(b)
    return caps, " ".join(note), left


def _pics_specs(hdr, title, imgs, caps, note, source=None, kicker_only=False):
    kicker, title = (hdr if hdr and _kick_ok(hdr) else None, None) if kicker_only else _head(hdr, title)
    out = []
    for i in range(0, len(imgs), 6):
        chunk = imgs[i:i + 6]
        items = [{"image": im["path"], "caption": caps.get(i + j, "")} for j, im in enumerate(chunk)]
        s = {"type": "pics", "kicker": kicker, "title": title, "items": items}
        if note and i + 6 >= len(imgs):
            s["note"] = note
        if source and i + 6 >= len(imgs):
            s["source"] = source
        out.append(s)
    n = len(out)
    return [_suffix(s, k, n) for k, s in enumerate(out, 1)]


def _image_specs(sl, hdr, blocks, h_cm):
    imgs = sorted(sl["obrazy"], key=lambda i: (round(i["y"] / 3), i["x"]))
    caps, note, left = _captions(imgs, blocks)
    items = _items(left)
    src = [i for i in items if _SRC.match(i["t"]) and len(i["t"]) <= 130]
    source = " · ".join(i["t"] for i in src) or None
    items = [i for i in items if i not in src]
    t, rest = _pick_title(items, allow_single=True)
    if rest and not t and len(imgs) >= 2 and len(rest) == 1 and not rest[0]["li"] and len(rest[0]["t"]) <= 160 \
            and rest[0]["pt"] < 30:
        note, rest = (rest[0]["t"] + (" " + note if note else "")).strip(), []
    out = []
    if rest:
        flow_w = cm(16.6)
        bl = _blocks_of(rest)
        beside = (len(imgs) == 1 or (len(imgs) == 2 and sum(len(i["t"]) for i in rest) > 250)) and \
            len(_chunk(bl, flow_w, build_dk.CB - build_dk.CT - cm(0.6))) == 1
        if beside:
            ims = [{"image": im["path"], "caption": caps.get(k, "")} for k, im in enumerate(imgs)]
            return _text_specs(items + src, hdr, imgs=ims, allow_single=True)
        out += _text_specs(items, hdr)
        out += _pics_specs(hdr, None, imgs, caps, note, source, kicker_only=bool(out))
        return out
    return _pics_specs(hdr, t["t"] if t else None, imgs, caps, note, source)


# --- tabele i wykresy -------------------------------------------------------------------------------------
def _table_specs(tb, hdr, title_item):
    rows = [r for r in tb["rows"] if any(c.strip() for c in r)]
    if not rows:
        return []
    head, body = rows[0], rows[1:]
    ncol = len(head)
    ok = 2 <= ncol <= 6 and body
    widths = []
    if ok:
        widths = [max(12, min(60, max(len(r[c]) if c < len(r) else 0 for r in rows))) for c in range(ncol)]
        tw = build_dk.W - 2 * build_dk.MX
        colw = [tw * w / sum(widths) - cm(1) for w in widths]
        ok = min(colw) >= cm(1.8) and all(len(build_dk.lines_for(cell, 13, colw[c])) <= 2
                                           for r in rows for c, cell in enumerate(r[:ncol]))
    kicker, title = _head(hdr, title_item)
    if not ok:  # tabela nietypowa: wiersz = punkt z nazwami kolumn
        bl = [{"k": "li", "t": "; ".join("%s: %s" % (h, v) if h else v for h, v in zip(head, r) if v.strip())
               if body else r[0]} for r in (body or [head])]
        return _flow_specs(hdr, title_item, bl)
    specs, per = [], 9
    for i in range(0, len(body), per):
        specs.append({"type": "table", "kicker": kicker, "title": title, "head": head,
                      "rows": [r + [""] * (ncol - len(r)) for r in body[i:i + per]],
                      "widths": widths})
    n = len(specs)
    return [_suffix(s, k, n) for k, s in enumerate(specs, 1)]


def _num(v):
    return 0.0 if v is None else v


def _chart_spec(ch, hdr, title_item):
    kicker, title = _head(hdr, title_item or ch["title"] or None)
    dec = 0
    for s in ch["series"]:
        for v in s["values"]:
            if v is not None and abs(v - round(v)) > 1e-9:
                dec = max(dec, 2 if abs(v * 10 - round(v * 10)) > 1e-6 else 1)
    fmt = "0" if dec == 0 else "0." + "0" * dec
    return {"type": "columns", "kicker": kicker, "title": title, "categories": ch["cats"],
            "series": [{"name": s["name"] or "Seria %d" % (i + 1), "values": [_num(v) for v in s["values"]]}
                       for i, s in enumerate(ch["series"])], "number_format": fmt}


# --- jeden slajd źródła -> slajdy DK ----------------------------------------------------------------------
def _cover_spec(sl, hdr, items, hc):
    """Okładka: największe pole tekstu = tytuł; data -> meta; reszta -> podtytuł."""
    if items:
        top = max(items, key=lambda i: i["pt"])
        tit = [i for i in items if i["bi"] == top["bi"]]
        title = " ".join(i["t"] for i in tit)
    else:
        tit, title = [], hdr
    others = [i["t"] for i in items if i not in tit]
    meta = [o for o in others if _DATE.search(o) and len(o) <= 40]
    sub = [o for o in others if o not in meta]
    w1, w3 = cm(12.3), build_dk.W - 2 * build_dk.MX
    sz1 = build_dk.title_size(title, 58, 36, w1)
    sz3 = build_dk.title_size(title, 84, 44, w3)
    if len(build_dk.display_lines(title, sz1, w1)) * sz1 <= 215:
        variant = 1
    elif len(build_dk.display_lines(title, sz3, w3)) * sz3 <= 150:
        variant = 3  # długi tytuł: pas z logo u góry i tytuł na całą szerokość
    else:
        return None
    spec = {"type": "cover_text", "variant": variant, "title": title}
    if hdr and items:
        spec["kicker"] = hdr
    if sub:
        spec["subtitle"] = "\n".join(sub)
    if meta:
        spec["meta"] = " · ".join(meta)
    out = [spec]
    if sl["obrazy"]:
        out += _image_specs(dict(sl, texts=[]), None, [], hc)
    return out


def _convert(sl, model, first, last, chap_no):
    hc, wc = model["h_cm"], model["w_cm"]
    hdr_b, blocks = _body(sl, hc)
    hdr = _text_of(hdr_b) if hdr_b else None
    items = _items(blocks)
    plain = not sl["tables"] and not sl["charts"]
    if first and plain and sl["texts"]:  # okładka: tytuł to największy tekst (także z placeholdera tytułu)
        cov = _cover_spec(sl, None, _items(_order(sl["texts"], hc)), hc)
        if cov:
            return cov
        hdr, blocks, items = None, _order(sl["texts"], hc), _items(_order(sl["texts"], hc))  # tytuł za długi na okładkę
    if last and plain and not sl["obrazy"] and not hdr and items and items[0]["t"].startswith("#") and \
            len(items[0]["t"]) <= 40:
        spec = {"type": "end", "hashtag": items[0]["t"]}
        if len(items) > 1:
            spec["contact"] = "  ·  ".join(i["t"] for i in items[1:])
        return [spec]
    sec = is_section(sl, hc, first)
    if sec and last:
        return [{"type": "end", "variant": "light", "title": _clean(sec), **({"subtitle": hdr} if hdr else {})}]
    if sec:
        spec = {"type": "section", "variant": "dark", "number": "%02d" % (chap_no or 1), "title": _clean(sec)}
        if hdr:
            spec["subtitle"] = hdr
        return [spec]
    if sl["tables"] or sl["charts"]:
        t, rest = _pick_title([i for i in items if not _SRC.match(i["t"])], allow_single=True)
        out = []
        for tb in sl["tables"]:
            out += _table_specs(tb, hdr, t["t"] if t else None)
        for ch in sl["charts"]:
            out.append(_chart_spec(ch, hdr, t["t"] if t else None))
        left = [i for i in items if i is not t]
        return out + (_text_specs(left, None) if left else [])
    if sl["obrazy"]:
        return _image_specs(sl, hdr, blocks, hc)
    # tekst: kolumny (pola obok siebie) -> grupy "nagłówek + treść" -> typy ogólne
    t0, _r = _pick_title(items)
    tb = next((b for b in blocks if t0 and id(b) == t0["bi"]), None)
    cb, tcol = blocks, None
    if tb is not None and len(_items([tb])) == 1 and all(tb["y"] + tb["h"] <= b["y"] + 0.6 for b in blocks if b is not tb):
        cb, tcol = [b for b in blocks if b is not tb], t0["t"]  # tytuł nad kolumnami (np. "KULKI" nad trzema smakami)
    cl = _columns(cb, wc)
    if cl:
        cols = [_col_spec(c) for c in sorted(cl, key=lambda c: c["x0"])]
        return _cols_specs(cols, hdr, tcol)
    if len(items) >= 4:
        g = _headgroups(items)
        if g:
            return _cols_specs(g, hdr, None)
    return _text_specs(items, hdr)


# =====================================================================================================
# 2a. UKŁAD 1:1 (07.10.2026): wiersze i kolumny z pozycji na starym slajdzie
# =====================================================================================================
# User 07.10: „Nie trzymałeś się tekstów w slajdzie i kolejności… Staraj się trzymać układu ze starej prezentacji”,
# „Segment 1 i 3… musi być osobno”. Automat niczego nie odgaduje: przenosi to, co stało na slajdzie, w te same miejsca
# (typ `uklad` z build_dk). Gdy nie umie odczytać układu - zwykłe wiersze w kolejności oryginału; dzieli slajd dopiero
# wtedy, gdy tekst nie mieści się pismem 13 pt.
CELE = {
    "wiernie": {
        "nazwa": "Zachowaj układ", "sufiks": "",
        "opis": "Ten sam slajd w nowym wyglądzie. Te same teksty, kolejność i układ.",
        "polecenie": [
            # Polecenie dla agenta, który nic nie wie o projekcie (user 07.10: instrukcje mają być ZAKORZENIONE w skillu
            # i w design systemie, nie w pamięci modelu). Zmiana tutaj = program (engine.ai_prompt_pptx), wiersz poleceń
            # i dokumenty (konwersja-pptx.md pkt 0 i 2a) dostają ją po build.ps1.
            "ZANIM COKOLWIEK POPRAWISZ, wczytaj dwa źródła (bez nich nie zmieniaj wyglądu): (1) skill /prezentacje: "
            "%USERPROFILE%\\.claude\\skills\\prezentacje\\SKILL.md (sekcja 1b) oraz references\\konwersja-pptx.md "
            "(pkt 1 i 2a) i references\\lekcje.md (A27-A44, sekcja D); gdy skilla nie ma, zainstaluj go z folderu programu "
            "(zainstaluj-skill.cmd albo kopia folderu skill-prezentacje). (2) identyfikacja wizualna Dobra Kaloria: "
            "%USERPROFILE%\\.claude\\skills\\ds-dobra-kaloria\\IDENTYFIKACJA-WIZUALNA.md (i DESIGN-SYSTEM-DOBRA-KALORIA.md "
            "pkt 5.4 „Prezentacje PPTX”); gdy nie ma, szukaj folderu skill-ds-dobra-kaloria obok programu. Skrót: wzorzec "
            "= sklep dobrakaloria.pl: tło slajdu białe, kremowe są tylko karty, Mindset tylko w tytule i hasłach do ok. "
            "12 słów, cała reszta Lato, zieleń marki ze slotu motywu (DS: #007936), czerwień tylko jako akcent słów "
            "z oryginału, dużo światła, mało obrysów.",
            "To konwersja 1:1 (lekcje A33): slajd N wyniku = slajd N oryginału - te same słowa, ta sama kolejność "
            "góra-dół, ten sam układ (kolumny zostają kolumnami, osobne etykiety osobno, obrazy w całości, kolory słów "
            "z oryginału). Wypisz slajdy, które się rozjechały.",
            "ZAKAZ PRZEBUDOWY: żadnych nowych slajdów, agendy, przekładek, tytułów-wniosków, łączenia ani dzielenia "
            "slajdów, przestawiania, dopisywania ani skracania tekstu, wyjmowania liczb ze zdań do kafli, zamiany zdań "
            "na hasła. Nie wymyślaj liczb ani faktów. Oczywiste literówki popraw i wypisz osobno (było -> jest); "
            "niejasne zostaw i zgłoś do decyzji.",
            "Zmienia się TYLKO pojemnik wizualny, dobrany do kształtu treści z naszego szablonu (konwersja-pptx.md "
            "pkt 2a, reguły R0-R12): stos haseł = karta albo kafle; 2-4 krótkie myśli = równe karty obok siebie "
            "(„Dobra wiadomość – …” / „Zła wiadomość – …” = nagłówek karty w kolorze + reszta); krótka lista = kafle "
            "albo punkty z kropką marki, pozycje osobno; cytat z autorem = cytat (kursywa Lato, autor pogrubiony, "
            "nawias zostaje); akapit albo zdanie >= 13 słów = karta-artykuł w Lato; zdjęcie + podpis = obrazy w całości "
            "+ podpis Mindset pod nimi; etykiety CT / TA / Insight = osobny wiersz do lewej; gdy karty się nie mieszczą "
            "= zwykłe wiersze, nie nowy slajd. Żadnego gołego akapitu Mindset na całą szerokość, żadnego kremowego tła "
            "całego slajdu.",
            "Interpunkcja z oryginału zostaje znak w znak (nawiasy, myślniki, kropki, cudzysłowy); w pliku pokrycie.json "
            "klucz „znaki” wypisuje każdy zdjęty znak - ma być pusty. Kontrole „Treść: 100%” i „Układ: … usterki” też "
            "muszą być czyste.",
            "BRAMKA ODDANIA (gdy masz dostęp do plików): render oryginału i wyniku (scripts\\render.ps1), plansze par "
            "stary | nowy (scripts\\pary_slajdow.py) obejrzane co do jednej - ten sam slajd, te same słowa, pojemnik "
            "z szablonu na każdym slajdzie; scripts\\verify.ps1 „Tekst - problemy: 0” bez wyjątku COM; python -m pytest "
            "scripts\\test_konwersja.py. Bez obejrzanych plansz nie mów, że gotowe. Poprawki wpisuj do "
            "spec_konwersja.json (typ uklad) i buduj build_dk.py, nie ręcznie w PowerPoincie.",
        ]},
    "rozwin": {
        "nazwa": "Rozwiń / dokończ", "sufiks": " - rozwinięta",
        "opis": "Slajdy z oryginału zostają. Program dołoży puste slajdy z podpowiedziami w [nawiasach]. Treść dopisze "
                "AI albo Ty; sam program niczego nie napisze.",
        "polecenie": [
            "Prezentacja ma zostać dokończona i rozwinięta. Slajdy z oryginału zostają bez zmian: te same teksty, "
            "kolejność i układ. Niczego z nich nie zabieraj.",
            "Uzupełnij slajdy oznaczone w notatkach „NOWY” (teksty w [nawiasach kwadratowych]) treścią, która wynika "
            "z prezentacji: agenda z tytułów rozdziałów, podsumowanie z wniosków, następne kroki z ustaleń.",
            "Zaproponuj brakujące slajdy. Dla każdego podaj: po którym slajdzie ma stać, typ slajdu z szablonu "
            "(np. Punkty, Tabela, Następne kroki) i gotowy tekst. Każdy oznacz słowem NOWY.",
            "Nowe liczby i fakty tylko z materiałów, które dostałeś. Czego w nich nie ma, zostaw w [nawiasach] jako "
            "„do uzupełnienia”. Niczego nie wymyślaj.",
            "Na końcu lista: co dopisałeś, na którym slajdzie i skąd wziąłeś treść.",
        ]},
    "skroc": {
        "nazwa": "Skróć", "sufiks": " - skrót",
        "opis": "Nic nie znika: rozdziały, które wyłączysz, zostają w pliku jako slajdy ukryte. Dalszy skrót zrobi AI "
                "z gotowego polecenia.",
        "polecenie": [
            "Prezentacja ma być krótsza: do pokazu ma zostać około %(cel_slajdy)s slajdów (teraz widocznych jest "
            "%(widoczne)s z %(wszystkie)s).",
            "Niczego nie kasuj. Slajd, który nie wchodzi do pokazu, UKRYJ (prawy klik na miniaturze > Ukryj slajd) - "
            "zostaje w pliku na swoim miejscu.",
            "Gdy chcesz podać treść slajdu krócej albo połączyć dwa sąsiednie slajdy o tym samym temacie: zrób NOWY "
            "slajd z krótszą treścią, a oryginały ukryj tuż za nim. Pełny tekst oryginału wklej też do notatek nowego slajdu.",
            "Nie zmieniaj liczb, nazw ani sensu. Nie dopisuj treści, której nie ma w źródle.",
            "Na końcu lista „Co ukryte i gdzie jest oryginał”: numer slajdu oryginału, powód, numer nowego slajdu "
            "(jeśli powstał).",
        ]},
}
SKROTY = {"GUS", "TA", "IG", "UE", "USA", "UK", "AI", "KPI", "ROI", "SKU", "EAN", "VAT", "IT", "PR", "HR", "NCEŻ", "CEO",
          "ESG", "PLN", "EUR", "USD", "FMCG", "NPD", "CT", "MCT", "DK", "GLP", "II", "III", "IV", "VI", "XL", "XXL", "OK",
          "WHO", "NIK", "NFZ", "EFSA", "FDA", "BCG", "PWC", "ZUS", "PKB", "CBOS", "OECD", "ONZ", "GIS", "IŻŻ", "AAKG",
          "BIO", "VEGE", "B2B", "B2C", "DNA", "UV", "SPF", "IO", "PCOS", "UGC", "SEO", "CPC", "CTR", "CPM", "ROAS", "FB",
          "YT", "POS", "POSM", "CRM", "NPS", "FAQ", "PDF", "QR", "ECO", "VIP", "TOP", "LOL"}
# krótkie zwykłe słowa, które autorzy wpisują WERSALIKAMI w wierszu z małymi literami - to nie są skróty
_ZWYKLE = {"ORAZ", "ALE", "LUB", "DLA", "NIE", "TAK", "CZY", "JAK", "JEST", "SĄ", "CO", "DO", "NA", "OD", "PO", "ZA", "ZE",
           "TO", "TEŻ", "BEZ", "POD", "NAD", "PRZY", "ABY", "ŻE", "BY", "WE", "KU", "SIĘ", "TEN", "TE", "TYM", "ICH", "JEJ",
           "JEGO", "NAS", "NAM", "MA", "MY", "WY", "ON", "ONA", "ALBO", "WIĘC", "GDY", "BO", "NIŻ", "AŻ", "JUŻ", "ZŁA", "ZŁY",
           "NOWA", "NOWY", "NOWE", "DUŻY", "MAŁY", "CEL", "CELE", "PLAN", "ROK", "LAT", "LATA", "RAZ", "TU", "TAM"}
_JEDN = {"MLN", "MLD", "TYS", "ZŁ", "KG", "ML", "KCAL", "CM", "MM", "KM", "SZT", "NP", "TJ", "TZW", "WG", "DR", "NR", "PKT",
         "PROC", "DKG", "GODZ", "MIN", "M.IN", "LAT", "ROK", "OK"}
_SAMOGL = set("aąeęioóuy")
_SKR_KROPKA = ("np.", "tj.", "tzw.", "ok.", "min.", "godz.", "tys.", "mln.", "mld.", "wg.", "ul.", "str.", "r.", "m.in.")
_OBOK = ".,:;!?()„”\"'–—-/+&"
BUL = "\u2022\u00a0"  # punkt listy w bloku kolumny (kropka + twarda spacja)
MIN_PT, MIN_PT_KOL = 13, 12   # najmniejsze pismo tekstu w wierszu / w karcie kolumny; niżej dzielimy slajd


# --- wielkość liter (tylko pola, które źródło WYŚWIETLA wersalikami) ------------------------------------------
def _slowo(w, chron, mieszany=False):
    """Słowo zapisane WERSALIKAMI -> małe litery, poza skrótami (bez samogłosek, z cyfrą, z listy SKROTY) i słowami
    chronionymi (w tym pliku stoją gdzieś w środku wiersza z wielkiej litery - nazwy własne). mieszany = wiersz ma
    też małe litery: wtedy krótkie słowo WERSALIKAMI (do 4 liter) to prawie zawsze skrót (WHO, FDA, NIK) i zostaje,
    chyba że jest zwykłym spójnikiem albo przyimkiem."""
    m = re.match(r"^(\W*)(.*?)(\W*)$", w, re.S)
    pre, core, post = m.groups()
    n_alpha = sum(1 for c in core if c.isalpha())
    if n_alpha < 2 or not core.isupper():
        return w
    if core in _JEDN:  # jednostki i skróty pisane zawsze małymi: mln, zł, kg, np.
        return pre + core.lower() + post
    if any(c.isdigit() for c in core) or core in SKROTY or not (_SAMOGL & set(core.lower())):
        return w
    if mieszany and n_alpha <= 4 and core not in _ZWYKLE:
        return w
    cap = core[0] + core[1:].lower()
    return pre + (cap if cap in chron else core.lower()) + post


def _zdaniowo(lines, chron, maly=()):
    """Wiersze jednego pola w zapisie zdaniowym: początek pola i zdania wielką literą, wiersz-kontynuacja małą
    (chyba że to nazwa własna: następne słowo też z wielkiej litery, cudzysłów przed słowem, słowo chronione).
    maly = słowa, które w tym pliku stoją też małą literą: wielka litera w środku zdania („Za dobra luksusowe”,
    „Chcą się”) to wersalikowy zapis autora, nie nazwa własna - idzie małą (08.10)."""
    out, nowe = [], True

    def caps(x):  # słowo WERSALIKAMI z co najmniej dwiema literami (nie „B6”, nie „X”)
        return x.isupper() and sum(1 for c in x if c.isalpha()) >= 2

    for ln in lines:
        src, toks, po_kropce = ln.split(" "), [], False
        mieszany = any(c.islower() for c in ln)
        for k, w in enumerate(src):
            s = _slowo(w, chron, mieszany)
            core = w.strip(_OBOK)
            if len(core) == 1 and core.isupper() and core.lower() in "aiouwz" and k and not po_kropce:
                # pojedyncza litera (spójnik, przyimek): mała w ciągu WERSALIKÓW albo gdy dalej idzie małe słowo
                # („dzień I temat” -> „i”); „Gen Z”, „X I Y” i litera po kropce zostają
                prev, nxt = src[k - 1].strip(_OBOK), (src[k + 1].strip(_OBOK) if k + 1 < len(src) else "")
                if not mieszany or caps(prev) or caps(nxt) or \
                        (core in "AIOUW" and nxt[:1].islower() and prev[-1:].islower()):
                    s = w.replace(core, core.lower(), 1)
            if po_kropce and s != w and s[:1].islower():
                s = s[:1].upper() + s[1:]
            c2 = s.strip(_OBOK)
            if k and not po_kropce and not src[k - 1].endswith(":") and len(c2) >= 2 and c2[0].isupper() and \
                    c2[1:].islower() and c2.lower() in maly:
                s = s.replace(c2, c2[0].lower() + c2[1:], 1)
            toks.append(s)
            po_kropce = bool(re.search(r"[.!?…]$", s)) and s.lower() not in _SKR_KROPKA and \
                (len(s) >= 4 or any(c.isdigit() for c in s))
        ln2 = re.sub(r"(\d)\s+R\.", r"\1 r.", " ".join(toks))
        m = re.search(r"[^\W\d_]", ln2)
        if m:
            i = m.start()
            w0 = re.match(r"[\w-]+", ln2[i:]).group(0)
            nast = re.findall(r"[^\W\d_][\w-]*", ln2[i + len(w0):])
            if nowe or re.match(r"^[^:]{2,40}:\s+\S", ln2):  # „Etykieta: wartość” to zawsze osobna myśl
                nowe = True
            if nowe:
                if not any(c.isdigit() for c in ln2[:i]):  # „2 kierunki poszukiwań” zostaje
                    ln2 = ln2[:i] + ln2[i].upper() + ln2[i + 1:]
            elif ln2[i].isupper() and (len(w0) == 1 or w0[1:].islower()) and w0 not in chron and \
                    not re.search(r"[„\"“«]", ln2[:i]) and not (nast and nast[0][:1].isupper()):
                ln2 = ln2[:i] + ln2[i].lower() + ln2[i + 1:]
        out.append(ln2)
        nowe = bool(re.search(r"([.!?…:][\"”»)]*|\d)\s*$", ln2))  # po kropce, dwukropku albo liczbie zaczyna się nowa myśl
    return out


def _chronione(model):
    """Słowa, które w tym pliku stoją w środku wiersza z wielkiej litery (Byron, Polaków, Gen): zostają wielką."""
    out = set()
    for s in model["slajdy"]:
        for b in s["texts"]:
            for p in b["paras"]:
                for ln in re.split(r"[\v\n\r]", p["t"]):
                    ws = ln.split()
                    for k in range(1, len(ws)):
                        c = ws[k].strip(_OBOK)
                        # 10.10: słowo po kropce / dwukropku to początek zdania (s26 „Ale”), nie nazwa własna
                        if len(c) >= 3 and c[0].isupper() and c[1:].islower() and \
                                not re.search(r"[.!?…:][\"”»)]*$", ws[k - 1]):
                            out.add(c)
    return out


def _maly(model):
    """Słowa (>= 2 litery), które w tym pliku stoją gdzieś pisane małymi literami."""
    out = set()
    for s in model["slajdy"]:
        for b in s["texts"]:
            for p in b["paras"]:
                for w in p["t"].split():
                    c = w.strip(_OBOK)
                    if len(c) >= 2 and c.islower():
                        out.add(c)
    return out


def _lit(ctx, n, b, lines):
    """Zapis zdaniowy, jeśli pole jest wyświetlane wersalikami; zmiany trafiają do dziennika „było -> jest”."""
    if b is None or not any(p.get("caps") for p in b["paras"]):
        return list(lines)
    # wielka litera w środku zdania -> mała tylko w polu w całości wersalikowym (w polu z akapitami Lato „Dla segmentu…”
    # po łączu zaczyna nowe zdanie)
    new = _zdaniowo(lines, ctx["chron"], ctx.get("maly", ()) if all(p.get("caps") for p in b["paras"]) else ())
    for a, c in zip(lines, new):
        if a != c:
            ctx["litery"].append((n, a, c))
    return new


# --- wiersze pola tekstu ----------------------------------------------------------------------------------------
def _czerwony(c):
    try:
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    except Exception:
        return False
    return r >= 190 and g <= 95 and b <= 95


def _flagi(runs, glowny):
    """Kolor każdego słowa wiersza: 'a' czerwień (akcent), 'i' inny niż przeważający w pliku, '-' zwykły.
    Kolor dziedziczony (None) traktujemy jak zwykły."""
    chars = []
    for t, c in runs or []:
        chars += ["a" if (c and _czerwony(c)) else "-" if (c is None or c == glowny) else "i"] * len(t)
    raw = "".join(t for t, _c in runs or [])
    return [chars[m.start()] for m in re.finditer(r"\S+", raw)]


def _wiersze(b):
    """Pole tekstu -> wiersze tak, jak je złamał autor (akapity i miękkie łamania). 'pusty' = przed wierszem była
    pusta linia (autor oddzielił myśl)."""
    out, pusty = [], False
    for p in b["paras"]:
        pusty = pusty or bool(p.get("odstep"))
        linie = p.get("linie") or [{"t": t, "runs": [(t, None)]} for t in re.split(r"[\v\n\r]", p["t"])]
        for ln in linie:
            t = _clean(ln["t"])
            if not t:
                pusty = True
                continue
            out.append({"t": t, "pt": ln.get("pt") or p["pt"] or DEFAULT_PT, "li": p["li"], "url": p["url"],
                        "runs": ln.get("runs"), "b": p.get("b"), "al": p.get("al"), "pusty": pusty and bool(out),
                        "eu": ln.get("eu")})
            pusty = False
    return out[b.get("_od", 0):]


def _tryb(b, skala):
    """Jak przenieść pole tekstu:
    'proza'   - długi tekst (akapity po kilka wierszy): zdania sklejamy i układamy na nowo, pismo Lato;
    'hasla'   - duże pismo (>= 28 pt), krótko: hasła nagłówkowe, łamania autora zostają;
    'wiersze' - małe pismo, krótko (opisy w kolumnach, podpisy, listy): Lato, akapity autora zostają osobnymi wierszami."""
    ws = _wiersze(b)
    if not ws:
        return "pusty"
    pt = max(w["pt"] for w in ws) * skala
    total = sum(len(w["t"]) for w in ws)
    if total >= 180 and sum(1 for w in ws if len(w["t"]) >= 40) * 2 >= len(ws):
        return "proza"
    if pt >= 28 and not any(w["li"] for w in ws):
        # 08.10: zdanie to nie hasło - pole dużego pisma, w którym połowa słów stoi w zdaniach, idzie Lato (R-ZD)
        return "proza" if _udzial_zdan(ws) >= 0.5 else "hasla"
    return "proza" if len(ws) == 1 and total > 90 else "wiersze"


_KONIEC = re.compile(r"[.!…][\"”»)]*$")


def _grupy_wierszy(ws):
    """Wiersze pola -> grupy (jedno źródło progu dla _tryb i _hasla_grupy): podział na pustej linii, po kropce,
    przy zmianie rozmiaru pisma (> 15%) i na granicy listy z myślnikami. Każdy wiersz dostaje 'mark'."""
    groups, cur = [], []
    for w in ws:
        mark = bool(_MARK.match(w["t"])) and not re.match(r"\s*\d", w["t"])
        if cur and (w["pusty"] or mark != cur[-1]["mark"] or abs(w["pt"] - cur[-1]["pt"]) > 0.15 * cur[-1]["pt"] or
                    (not mark and re.search(r"[.!?…][\"”»)]*$", cur[-1]["t"])) or
                    (not mark and cur[-1].get("eu") and w["t"][:1].isupper())):  # wiersz kończy łącze, następny od wielkiej
            groups.append(cur)
            cur = []
        cur.append(dict(w, mark=mark))
    if cur:
        groups.append(cur)
    return groups


def _zdanie_grupa(g):
    """Grupa wierszy to ZDANIE (nie hasło): >= 13 słów albo >= 8 słów zakończone [.!…] (znak '?' nie liczy się -
    pytania bywają hasłami)."""
    n = sum(len(w["t"].split()) for w in g)
    return n >= 13 or (n >= 8 and bool(_KONIEC.search(g[-1]["t"])))


def _udzial_zdan(ws):
    """Jaka część słów pola stoi w grupach-zdaniach (0..1)."""
    tot = sum(len(w["t"].split()) for w in ws)
    zd = sum(sum(len(w["t"].split()) for w in g) for g in _grupy_wierszy(ws) if _zdanie_grupa(g))
    return zd / tot if tot else 0.0


def _bez_sierot(lines):
    """Typografia PL (twarda reguła usera z 29.09): ostatni wiersz nie może być jednym słowem. Gdy autor sam złamał
    wiersz przed pojedynczym słowem („grup na zabiegi / kosmetyczne”), słowo wraca do poprzedniego wiersza."""
    out = []
    for ln in lines:
        if out and len(ln.split()) == 1 and len(out[-1].split()) >= 2 and not _TERM.search(out[-1]):
            out[-1] += " " + ln
        else:
            out.append(ln)
    return out


def _dziel_po_kropce(lines):
    """Grupy wierszy: nowa grupa po wierszu zakończonym kropką (osobna myśl, np. „…czekolady.” | „CT: 35-55”)."""
    out, cur = [], []
    for ln in lines:
        cur.append(ln)
        if re.search(r"[.!?…][\"”»)]*$", ln):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def _flagi_pola(b, ctx):
    """Kolor każdego słowa pola (jak _flagi), po zdjęciu znaczników listy - w kolejności słów, jaką mają pozycje
    z _items (kolejność słów się nie zmienia przy sklejaniu i dzieleniu akapitów)."""
    out = []
    for w in _wiersze(b):
        f = _flagi(w["runs"], ctx["glowny"])
        t = w["t"]
        if _MARK.match(t) and not re.match(r"\s*\d", t):
            t = _MARK.sub("", t).strip()
        k = len(t.split())
        out += f[len(f) - k:] if len(f) >= k else ["-"] * k
    return "".join(out)


def _kolor_fl(fl, row, lato=False):
    """Kolor słów wiersza z flag ('a' czerwień, 'i' inny kolor, '-' zwykły). Cały wiersz czerwony -> akcent;
    mieszane -> `wyr` słowo po słowie. Cały w innym kolorze: Mindset -> zieleń marki, Lato (akapit) -> bez zmiany,
    bo to kolor bazowy pola, nie wyróżnienie. Flagi zostają w wierszu (`_fl`) dla reguł pojemników."""
    if not fl:
        return row
    if lato:  # kolor bazowy pola (najczęstszy poza czerwienią) to nie wyróżnienie, tylko zwykły tekst akapitu
        cnt = collections.Counter(c for c in fl if c != "a")
        base = cnt.most_common(1)[0][0] if cnt else "-"
        if base != "-":
            fl = fl.replace(base, "-")
    row["_fl"] = fl
    fs = set(fl)
    if fs == {"-"}:
        return row
    if fs == {"a"}:
        row["color"] = "accent"
    elif fs == {"i"}:
        if not lato:
            row["color"] = "brand"
    else:
        row["wyr"] = fl
    return row


def _proza_bloki(b, ctx, n):
    """Pole prozy -> [(rodzaj, tekst, flagi)]: 'b' podtytuł, 'p' akapit, 'li' punkt, 'small' link albo źródło.
    flagi = kolor każdego słowa tekstu (string) albo None, gdy nie da się ich przypisać."""
    ws = _wiersze(b)
    tryb = _tryb(b, ctx["skala"])
    duze = bool(ws) and max(w["pt"] for w in ws) * ctx["skala"] >= 28
    luzno = tryb == "proza" and duze and _udzial_zdan(ws) >= 0.5
    out = []
    for bl in _blocks_of(_items([b], sklej=tryb == "proza", luzno=luzno)):
        k = {"h": "b", "li": "li", "url": "small"}.get(bl["k"], "p")
        if k == "p" and _SRC.match(bl["t"]) and len(bl["t"]) <= 130:
            k = "small"
        segs = [t.split("\x1f") for t in bl["t"].split("\n")]  # wiersze autora sklejone w akapit (luzno)
        lit = _lit(ctx, n, b, [x for ss in segs for x in ss])  # wielkosc liter liczona wg wierszy autora
        lines, c = [], 0
        for ss in segs:
            line = lit[c]
            for x in lit[c + 1:c + len(ss)]:
                line += " " + x
            c += len(ss)
            lines.append(line)
        for grp in (_dziel_po_kropce(lines) if k == "p" and len(lines) > 1 else [lines]):
            out.append((k, "\n".join(_bez_sierot(grp))))
    fl = _flagi_pola(b, ctx)
    if sum(len(t.split()) for _k, t in out) != len(fl):
        if any(c != "-" for c in fl):
            ctx["uwagi"].append("Slajd %d: kolory słów w akapicie nie przeniesione (liczba słów się nie zgadza)." % n)
        return [(k, t, None) for k, t in out]
    res, c = [], 0
    for k, t in out:
        m = len(t.split())
        res.append((k, t, fl[c:c + m]))
        c += m
    return res


def _pozycje_listy(raw, maks_slow):
    """R3: lista krótkich pozycji - >= 3 wiersze po <= maks_slow słów, żaden nie kończy się [.!?;:]. Wiersz zaczynający
    się od „oraz / lub / albo” to dalszy ciąg poprzedniej pozycji. Zwraca pozycje albo None."""
    it = []
    for t in raw:
        if it and re.match(r"(?i)^(oraz|lub|albo)\b", t):
            it[-1] += " " + t
        else:
            it.append(t)
    if len(it) >= 3 and all(len(t.split()) <= maks_slow and not re.search(r"[.!?;:][\"”»)]*$", t) for t in it):
        return it
    return None


def _hasla_grupy(b, ctx, n, kolumna=False):
    """Pole haseł -> grupy wierszy [{lines, flagi, pt, al, mark, lista}]: podział na pustej linii, po kropce, przy
    zmianie rozmiaru pisma i na granicy listy z myślnikami. flagi = kolor każdego słowa ('a', 'i', '-').
    lista (R3): po wzięciu 1. wiersza na tytuł (b['_od']) albo w kolumnie pod nagłówkiem (kolumna=True) krótkie
    pozycje zostają osobnymi pozycjami (bez sklejania sierot)."""
    out = []
    for g in _grupy_wierszy(_wiersze(b)):
        raw = [_MARK.sub("", w["t"]).strip() if w["mark"] else w["t"] for w in g]
        flagi = []
        for w, t in zip(g, raw):
            f = _flagi(w["runs"], ctx["glowny"])
            k = len(t.split())
            flagi += f[len(f) - k:] if len(f) >= k else ["-"] * k  # znacznik listy zabiera słowa z początku
        lista = False
        poz = None if g[0]["mark"] else _pozycje_listy(raw, 6 if b.get("_od") == 1 else 4) \
            if (b.get("_od") == 1 or kolumna) else None
        if g[0]["mark"]:
            lines = [x for t in raw for x in _lit(ctx, n, b, [t])]  # każdy punkt listy zaczyna się wielką literą
        elif poz:
            lines, lista = [x for t in poz for x in _lit(ctx, n, b, [t])], True
        else:
            lines = _bez_sierot(_lit(ctx, n, b, raw))
        znaki = [(_MARK.match(w["t"]).group(0).strip() if w["mark"] else "") for w in g]  # markery wpisane przez autora
        out.append({"lines": lines, "flagi": "".join(flagi), "pt": max(w["pt"] for w in g), "al": g[0]["al"],
                    "mark": g[0]["mark"], "lista": lista, "znaki": znaki})
    return out


def _kolor(g, row, baza="lead"):
    """Kolor grupy haseł jak w źródle: cała czerwona -> akcent; cała w innym kolorze -> zieleń marki (h);
    pojedyncze słowa wyróżnione -> znaczniki `wyr` (słowo po słowie)."""
    fl = set(g["flagi"])
    if fl == {"a"}:
        row["color"] = "accent"
    elif fl == {"i"}:
        if baza == "lead" and row["k"] == "lead":
            row["k"] = "h"
        else:
            row["color"] = "brand"
    elif fl - {"-"}:
        row["wyr"] = g["flagi"]
    return row


def _wyrownanie(b, al, wc):
    if al:
        return "c" if al == "c" else "l"
    if b.get("ph") is None:  # zwykle pole tekstu bez ustawionego wyrownania = do lewej
        return "l"
    return "c" if abs((b["x"] + b["w"] / 2) - wc / 2) <= 0.06 * wc and b["w"] <= 0.85 * wc else "l"


def _wiersze_pola(b, ctx, n):
    """Samodzielne pole tekstu -> wiersze slajdu `uklad` (w kolejności źródła)."""
    sk, rows = ctx["skala"], []
    ws = _wiersze(b)
    ptp = max([w["pt"] for w in ws] or [0]) * sk
    pole = {"_pole": id(b), "_duze": ptp >= 28}  # metadane dla _pojemniki (usuwane przed zapisem specu)
    if _tryb(b, sk) != "hasla":
        for k, t, fl in _proza_bloki(b, ctx, n):
            row = {"k": "p", "t": t, "li": True} if k == "li" else {"k": k, "t": t}
            if k != "small":
                _kolor_fl(fl, row, lato=True)
            rows.append(dict(row, _pt=ptp, **pole))
        return rows
    for g in _hasla_grupy(b, ctx, n):
        if g["mark"] or g["lista"]:
            # 10.10 (runda 4): wiodący myślnik listy to marker (jak punktor) - kafle go nie mają; kafle zawsze w zieleni
            # marki (kolor wypełnienia to pojemnik, nie treść); zdjęty marker wpisuje się w pokrycie jako `markery`
            kaf = list(g["lines"])
            if 2 <= len(kaf) <= 8 and all(len(t) <= 36 for t in kaf):
                ch = {"k": "chips", "items": kaf, "per_row": 2 if len(kaf) in (2, 4) else 3}
                rows.append(dict(ch, **pole))
            else:
                rows += [dict({"k": "b" if g["lista"] else "p", "t": t, "li": True}, _lista=True, **pole)
                         for t in g["lines"]]
            continue
        pt = g["pt"] * sk
        t = "\n".join(g["lines"])
        if len(g["lines"]) == 1 and len(t.split()) <= 4 and pt >= 60:
            row = {"k": "big", "t": t}
        else:
            row = {"k": "lead", "t": t}
            pw = int(max(24, min(60, round(pt))))
            if len(t.split()) > 4:  # hasło dłuższe niż 4 słowa: pismo do 36 pt (R0) - nie wielkie hasło na cały slajd
                pw = min(pw, 36)
            if abs(pw - 36) >= 5:
                row["pt"] = pw
        _kolor(g, row)
        row["_fl"] = g["flagi"]
        if _wyrownanie(b, g["al"], ctx["wc"]) != "c":
            row["align"] = "l"
        rows.append(dict(row, _pt=pt, **pole))
    return rows


# --- pasma i kolumny --------------------------------------------------------------------------------------------
def _pasma(els):
    """Elementy (pola tekstu i obrazy) w pasma poziome: element dochodzi do pasma, gdy zachodzi na nie w pionie
    co najmniej 35% wysokości niższego z nich."""
    bands = []
    for e in sorted(els, key=lambda e: (round(e["y"], 1), e["x"])):
        if bands:
            b = bands[-1]
            ov = min(b["y1"], e["y"] + e["h"]) - max(b["y0"], e["y"])
            if ov > 0 and ov >= 0.35 * min(e["h"], b["y1"] - b["y0"]):
                b["els"].append(e)
                b["y1"] = max(b["y1"], e["y"] + e["h"])
                continue
        bands.append({"y0": e["y"], "y1": e["y"] + e["h"], "els": [e]})
    return bands


def _klastry(els):
    cl = []
    for e in sorted(els, key=lambda e: e["x"]):
        for c in cl:
            ov = min(c["x1"], e["x"] + e["w"]) - max(c["x0"], e["x"])
            if ov > 0.3 * min(e["w"], c["x1"] - c["x0"]):
                c["els"].append(e)
                c["x0"], c["x1"] = min(c["x0"], e["x"]), max(c["x1"], e["x"] + e["w"])
                break
        else:
            cl.append({"x0": e["x"], "x1": e["x"] + e["w"], "els": [e]})
    return cl


def _pasuje(band, cl):
    """Czy pasmo leży w tych samych kolumnach: każdy element zachodzi wyraźnie na dokładnie jedną kolumnę
    (>= 60% szerokości węższego z pary) i nie wchodzi na sąsiednią (>= 25%). Zwraca [(element, nr kolumny)] albo None."""
    pary = []
    for e in band["els"]:
        ovs = [(min(c["x1"], e["x"] + e["w"]) - max(c["x0"], e["x"])) / max(min(e["w"], c["x1"] - c["x0"]), 0.1)
               for c in cl]
        hit = [k for k, o in enumerate(ovs) if o >= 0.6]
        if len(hit) != 1 or any(o >= 0.25 for k, o in enumerate(ovs) if k != hit[0]):
            return None
        pary.append((e, hit[0]))
    return pary


def _jedna_linia(b):
    ws = _wiersze(b)
    return ws[0]["t"] if len(ws) == 1 else None


def _haslo(b, sk):
    """Krótkie hasło do ramki: 1-3 wiersze, razem do 34 znaków, bez kropki na końcu, duże pismo."""
    ws = _wiersze(b)
    t = " ".join(w["t"] for w in ws)
    return bool(ws) and len(ws) <= 3 and len(t) <= 34 and not t.endswith((".", ",", ";", ":")) and \
        max(w["pt"] for w in ws) * sk >= 26 and not any(w["li"] for w in ws)


def _etykieta(e, pt_max):
    if e["typ"] != "t":
        return False
    t = _jedna_linia(e["b"])
    pt = max((p["pt"] or DEFAULT_PT) for p in e["b"]["paras"])
    return bool(t) and len(t) <= 28 and pt <= 0.6 * pt_max


def _kolumny(grp, cl, ctx, n, caps_of):
    """Grupa pasm o wspólnych kolumnach -> wiersz `cols`: bloki każdej kolumny w kolejności góra-dół; końcowe pasma
    samych krótkich etykiet zostają OSOBNYMI elementami (ostatnie = metka `meta`, przedostatnie = znacznik `tag`)."""
    sk = ctx["skala"]
    tx = [e for b in grp for e in b["els"] if e["typ"] == "t"]
    pt_max = max([max((p["pt"] or DEFAULT_PT) for p in e["b"]["paras"]) for e in tx] or [DEFAULT_PT])
    lab = []
    while len(grp) - len(lab) > 1 and len(lab) < 2 and all(_etykieta(e, pt_max) for e in grp[-1 - len(lab)]["els"]):
        lab.append(grp[-1 - len(lab)])
    lab_ids = {id(e): ("meta" if k == 0 else "tag") for k, b in enumerate(lab) for e in b["els"]}
    items = []
    for c in sorted(cl, key=lambda c: c["x0"]):
        els = sorted(c["els"], key=lambda e: (e["y"], e["x"]))
        it = {"blocks": []}
        body = [e for e in els if id(e) not in lab_ids]
        for k, e in enumerate(body):
            if e["typ"] == "i":
                it["blocks"].append({"k": "img", "image": e["im"]["path"],
                                     "h": round(max(2.5, min(9.5, e["h"] * ctx["sk_y"] * 0.92)), 1), "round": True})
                if caps_of.get(id(e["im"])):
                    it["blocks"].append({"k": "small", "t": caps_of[id(e["im"])], "color": "ink", "pt": 16})  # podpis kolorem tekstu, >= 14 pt
                continue
            b = e["b"]
            one = _jedna_linia(b)
            rest_pt = max([max((p["pt"] or DEFAULT_PT) for p in x["b"]["paras"]) for x in body[k + 1:] if x["typ"] == "t"]
                          or [0])
            my_pt = max((p["pt"] or DEFAULT_PT) for p in b["paras"])
            if k == 0 and one and len(one) <= 40 and len(body) > 1 and my_pt >= rest_pt and \
                    not one.endswith((".", ",", ";")):
                it["blocks"].append({"k": "h", "t": _lit(ctx, n, b, [one])[0]})
                continue
            if _tryb(b, sk) != "hasla":
                for kk, t, fl in _proza_bloki(b, ctx, n):
                    blk = {"k": "p", "t": BUL + t} if kk == "li" else {"k": kk, "t": t}
                    if kk != "small" and fl and "a" in fl:  # wyroznienie czerwienia zostaje takze w kolumnie
                        _kolor_fl(("-" + fl) if kk == "li" else fl, blk, lato=True)
                    it["blocks"].append(blk)
            else:
                pod_h = any(x["k"] == "h" for x in it["blocks"])  # R3b: lista pod naglowkiem kolumny
                for g in _hasla_grupy(b, ctx, n, kolumna=pod_h):
                    if g["lista"]:
                        it["blocks"].append({"k": "p", "t": "\n".join(BUL + t for t in g["lines"])})
                        continue
                    blk = {"k": "lead", "t": "\n".join((BUL + t) if g["mark"] else t for t in g["lines"])}
                    it["blocks"].append(blk if g["mark"] else _kolor(g, blk, baza="kol"))
        for e in els:
            if id(e) in lab_ids:
                key = lab_ids[id(e)]
                t = _lit(ctx, n, e["b"], [_jedna_linia(e["b"])])[0]
                it[key] = (it[key] + " · " + t) if it.get(key) else t
        items.append(it)
    row = {"k": "cols", "items": items}
    if any(bl["k"] == "img" for it in items for bl in it["blocks"]):
        row["card"] = False
        mean = sum(c["x1"] - c["x0"] for c in cl) / len(cl)
        for it, c in zip(items, sorted(cl, key=lambda c: c["x0"])):
            it["w"] = round(max(0.6, min(1.6, (c["x1"] - c["x0"]) / mean)), 2)
    return row


def _wlasny_naglowek(blocks, imgs, ctx):
    """Nagłówek samego slajdu (pod belką): samotne, jednowierszowe pole-etykieta (do 4 słów i 32 znaków) nad całą
    resztą treści, np. „Kulki”, „Dane wejściowe”. Pełne zdanie zostaje treścią. Zwraca (pole, tekst) albo (None, None)."""
    if len(blocks) + len(imgs) < 2 or not blocks:
        return None, None
    b = min(blocks, key=lambda b: (b["y"], b["x"]))
    rest = [x for x in blocks if x is not b]
    if any(x["y"] < b["y"] + b["h"] - 0.3 for x in rest + list(imgs)):
        return None, None
    ws = _wiersze(b)
    if len(ws) != 1:
        return None, None
    t = ws[0]["t"]
    rest_pt = max([w["pt"] for x in rest for w in _wiersze(x)] or [0])
    rest_len = sum(len(_text_of(x)) for x in rest)
    if len(t) <= 32 and len(t.split()) <= 4 and not t.endswith((".", ",", ";")) and ws[0]["pt"] >= 0.9 * rest_pt and \
            _title_fits(t) and (rest_len >= 1.5 * len(t) or imgs or len(rest) >= 2):
        return b, t
    return None, None


def _pierwszy_wiersz_tytulem(blocks, ctx):
    """Pole haseł, którego pierwszy wiersz jest pytaniem albo kończy się dwukropkiem: ten wiersz zostaje tytułem,
    reszta pola idzie dalej (np. „Co jest celem naszego spotkania?” + lista)."""
    if not blocks:
        return None, None
    b = min(blocks, key=lambda b: (b["y"], b["x"]))
    ws = _wiersze(b)
    if len(ws) >= 2 and _tryb(b, ctx["skala"]) == "hasla" and ws[0]["t"].endswith(("?", ":")) and \
            len(ws[0]["t"]) <= 70 and _title_fits(ws[0]["t"]) and all(x["y"] >= b["y"] - 0.3 for x in blocks):
        b["_od"] = 1
        return b, ws[0]["t"]
    return None, None


def _stosy(imgs):
    """Obrazy ustawione jeden pod drugim w tej samej kolumnie -> grupy (w nowym stylu stoją obok siebie, w kolejności
    góra-dół = lewa-prawa). Zwraca listę grup obrazów."""
    groups = []
    for im in sorted(imgs, key=lambda i: (i["y"], i["x"])):
        for g in groups:
            last = g[-1]
            ov = min(last["x"] + last["w"], im["x"] + im["w"]) - max(last["x"], im["x"])
            if ov >= 0.6 * min(last["w"], im["w"]) and -0.5 <= im["y"] - (last["y"] + last["h"]) <= 1.5:
                g.append(im)
                break
        else:
            groups.append([im])
    return groups


def _uklad_wiersze(sl, blocks, ctx):
    """Pola tekstu i obrazy slajdu -> wiersze `uklad` w kolejności góra-dół. Zwraca (wiersze, niepewny)."""
    n, sk, wc = sl["n"], ctx["skala"], ctx["wc"]
    imgs = list(sl["obrazy"])
    caps, note, left = _captions(imgs, blocks) if imgs else ({}, "", list(blocks))
    cap_blocks = [b for b in blocks if not any(b is x for x in left)]
    caps_of, wn_of, wnioski = {}, {}, []  # wnioski (R10a): podpis-wniosek pod obrazami -> wiersz `sub`, nie drobny druk
    for k, t in caps.items():
        src = next((b for b in cap_blocks if _clean(_text_of(b)) and _clean(_text_of(b)) in t), None)
        caps_of[id(imgs[k])] = _lit(ctx, n, src, [t])[0]
        # jeden podpis na cały slajd = wniosek; seria podpisów (po jednym pod każdym obrazem) to zwykłe podpisy
        kol = _wniosek(src, ctx) if src is not None and len(caps) + bool(note) == 1 and \
            not _SRC.match(caps_of[id(imgs[k])]) else None
        if kol:
            wn_of[id(imgs[k])] = kol
    if note and not _SRC.match(note) and not caps:
        src_n = next((b for b in cap_blocks if _clean(_text_of(b)) and _clean(_text_of(b)) in note and
                      not any(_clean(_text_of(b)) in t for t in caps.values())), None)
        kol = _wniosek(src_n, ctx) if src_n is not None else None
        if kol:
            wnioski.append((_lit(ctx, n, src_n, [note])[0], kol))
            note = ""
    els = [dict(typ="t", b=b, x=b["x"], y=b["y"], w=max(b["w"], 0.1), h=max(b["h"], 0.1)) for b in left
           if _wiersze(b)]
    stosy = _stosy(imgs)
    if len(stosy) != 1:
        stosy = [[im] for im in imgs]
    for g in stosy:
        if len(g) == 1:
            im = g[0]
            els.append(dict(typ="i", im=im, ims=[im], x=im["x"], y=im["y"], w=max(im["w"], 0.1), h=max(im["h"], 0.1)))
        else:  # stos obrazów: jeden wiersz na całą szerokość (obok siebie), tekst z boku idzie pod spód
            y0, y1 = min(i["y"] for i in g), max(i["y"] + i["h"] for i in g)
            els.append(dict(typ="i", im=g[0], ims=g, x=0.0, y=y0, w=wc, h=y1 - y0))
    bands = _pasma(els)
    k = 0
    while k < len(bands) - 1:  # obraz stojący tuż nad kolumną następnego pasma należy do tej kolumny
        a, nx = bands[k], bands[k + 1]
        if len(a["els"]) == 1 and a["els"][0]["typ"] == "i" and len(a["els"][0]["ims"]) == 1 and len(nx["els"]) >= 2:
            cl = _klastry(nx["els"])
            if 2 <= len(cl) <= 4 and _pasuje(a, cl):
                nx["els"].insert(0, a["els"][0])
                nx["y0"] = a["y0"]
                del bands[k]
                k = max(k - 1, 0)
                continue
        k += 1
    rows, niepewny, i = [], False, 0

    def pics(es):
        ims = [im for e in sorted(es, key=lambda e: (e["y"], e["x"])) for im in e["ims"]]
        if len(es) > 1:  # obok siebie: rzedami (gora-dol), w rzedzie od lewej
            ims = sorted(ims, key=lambda i: (round(i["y"] / 3), i["x"]))
        row = {"k": "pics", "min_h": 4.0}
        if len(ims) >= 4:
            big = max(ims, key=lambda i: i["w"] * i["h"])
            rest = [i for i in ims if i is not big]
            if big["x"] <= min(i["x"] for i in rest) and big["w"] * big["h"] >= 1.5 * max(i["w"] * i["h"] for i in rest):
                ims = [big] + rest  # duzy zrzut z lewej, reszta w siatce 2 x n z prawej - jak w oryginale
                row["layout"] = "1+siatka"
        row["items"] = []
        for im in ims:
            cap = caps_of.get(id(im), "")
            if cap and id(im) in wn_of:  # R10a: podpis-wniosek pod obrazem idzie pod wszystkie obrazy, Mindsetem
                row.setdefault("_wn", []).append((cap, wn_of[id(im)]))
                cap = ""
            row["items"].append({"image": im["path"], "caption": cap,
                                 "box": [round(im["x"], 1), round(im["y"], 1), round(im["w"], 1), round(im["h"], 1)]})
        wys = max(e["h"] for e in es) * ctx["sk_y"] * 0.9  # wysokosc rzedu jak w oryginale (w skali nowego slajdu)
        row["h"] = round(max(4.0, min(8.5, wys)), 1)
        row["_poj"] = len(ims) == 1 or (len(es) == 1 and len(es[0]["ims"]) > 1)
        mw = max(im["w"] for im in ims)
        if not row.get("layout") and min(im["w"] for im in ims) < 0.6 * mw:
            row["ws"] = [round(max(0.25, im["w"] / mw), 2) for im in ims]
        return row

    def pojedynczo(es):
        out, ims = [], []
        for e in sorted(es, key=lambda e: (e["y"], e["x"])):
            if e["typ"] == "i":
                ims.append(e)
                continue
            if ims:
                out.append(pics(ims))
                ims = []
            out += _wiersze_pola(e["b"], ctx, n)
        return out + ([pics(ims)] if ims else [])

    def haslo_t(e):
        t = " ".join(_lit(ctx, n, e["b"], [w["t"] for w in _wiersze(e["b"])]))
        return t[:1].upper() + t[1:]

    while i < len(bands):
        es = bands[i]["els"]
        if len(es) == 1 or all(e["typ"] == "i" for e in es):
            rows += pojedynczo(es) if len(es) == 1 else [pics(es)]
            i += 1
            continue
        cl = _klastry(es)
        same_hasla = all(e["typ"] == "t" and _haslo(e["b"], sk) for e in es)
        if len(cl) == 1 or len(cl) > 4:
            if len(cl) > 4 and same_hasla:
                rows.append({"k": "chips", "per_row": min(len(es), 4),
                             "items": [haslo_t(e) for e in sorted(es, key=lambda e: e["x"])]})
            else:
                niepewny = niepewny or len(cl) > 4
                rows += pojedynczo(es)
            i += 1
            continue
        nxt = bands[i + 1] if i + 1 < len(bands) else None
        ciag = nxt is not None and _pasuje(nxt, cl) and \
            not all(e["typ"] == "t" and _haslo(e["b"], sk) for e in nxt["els"])
        if same_hasla and all(len(c["els"]) == 1 for c in cl) and not ciag:
            # krótkie hasła w rzędach (np. 3 + 2) -> hasła w ramkach, w kolejności rzędów
            items, j = [], i
            while j < len(bands) and (j == i or len(bands[j]["els"]) >= 2) and \
                    all(e["typ"] == "t" and _haslo(e["b"], sk) for e in bands[j]["els"]):
                items += [haslo_t(e) for e in sorted(bands[j]["els"], key=lambda e: e["x"])]
                j += 1
            rows.append({"k": "chips", "items": items, "per_row": len(es)})
            i = j
            continue
        grp, j = [bands[i]], i + 1
        while j < len(bands):
            pary = _pasuje(bands[j], cl)
            if not pary:
                break
            for e, kk in pary:
                cl[kk]["els"].append(e)
                cl[kk]["x0"], cl[kk]["x1"] = min(cl[kk]["x0"], e["x"]), max(cl[kk]["x1"], e["x"] + e["w"])
            grp.append(bands[j])
            j += 1
        rows.append(_kolumny(grp, cl, ctx, n, caps_of))
        i = j
    if note:
        rows.append({"k": "small", "t": note})
    out = []
    for r in rows:  # sąsiednie wiersze samych obrazów -> jeden wiersz (obok siebie), najwyżej 4 obrazy
        razem = out and r["k"] == "pics" and out[-1]["k"] == "pics" and not r.get("layout") and not out[-1].get("layout")
        if razem and len(r["items"]) == 1 and len(out[-1]["items"]) <= 3 and r.get("_poj") and out[-1].get("_poj"):
            out[-1]["items"] += r["items"]
            out[-1]["_wn"] = out[-1].get("_wn", []) + r.get("_wn", [])
        else:
            out.append(r)
    res = []
    for r in out:  # R10a: wniosek pod obrazami Mindsetem (zielony / czerwony), tuz pod swoim wierszem obrazow
        res.append(r)
        res += [{"k": "sub", "t": t, "color": kol} for t, kol in r.pop("_wn", [])]
    res += [{"k": "sub", "t": t, "color": kol} for t, kol in wnioski]  # wspolny podpis (note) jak dotad na koncu
    return res, niepewny


def _wniosek(b, ctx):
    """R10a: podpis, którego pole źródła ma pismo >= 24 pt (po skali), jest w całości w kolorze albo źródło wyświetla go
    wersalikami (jak hasła, nie jak drobny podpis), to wniosek pod obrazami. Zwraca kolor wiersza ('accent' gdy cały
    czerwony, inaczej 'brand') albo None."""
    ws = _wiersze(b)
    if not ws:
        return None
    fl = [x for w in ws for x in _flagi(w["runs"], ctx["glowny"])]
    cale = bool(fl) and "-" not in fl
    if max(w["pt"] for w in ws) * ctx["skala"] >= 24 or cale or any(p.get("caps") for p in b["paras"]):
        return "accent" if fl and set(fl) == {"a"} else "brand"
    return None


# --- pojemniki z szablonu (08.10) -------------------------------------------------------------------------------
# User 07.10: „Nie korzystałeś z naszego szablonu. Brzydkie. Po slajdzie 5 dramat.” Automat dobiera POJEMNIK z szablonu
# do KSZTAŁTU treści (tekst, kolejność, liczby i kolory słów zostają): hasło -> karta (s14), zdania -> karta-artykuł
# (s16), 2-4 krótkie myśli -> karty obok siebie (s21), cytat -> s20, krótka lista -> punkty / kafle (s17, s36).
# Wiersze z _wiersze_pola niosą metadane `_pole`, `_pt`, `_duze`, `_fl` (usuwane przed zapisem specu).
_MIND = ("lead", "h", "big", "sub")
_CZESC = re.compile(r"^(?:pod|oraz|i|a|ale|lub|albo|czyli|bo)\b", re.I)
_CYT_NAW = re.compile(r"^(?P<q>.+?)\s*\((?P<a>[^()]{3,60})\)[.!]?$", re.S)
_CYT_CUD = re.compile(r"[„\"“]([^„”\"“]+)[”\"“]")
_PREFIKS = re.compile(r"^(\S+(?:\s\S+){0,3})\s([–—-])\s(.+)$", re.S)
_ETYKIETA = re.compile(r"^(?:CT|TA|Insight)\s*:", re.I)


def _w(r):
    return len((r.get("t") or "").split())


def _tekst(r):
    """Wiersz tekstu, który może wejść do karty (nie lista-punkty, nie etykieta, nie źródło)."""
    return r["k"] in _MIND + ("p", "b") and "_pole" in r and not r.get("_lista") and not r.get("_et")


def _lato(r):
    return r["k"] in ("p", "b")


def _rodzaj(r):
    return None if r is None else ("karta" if r.get("kont") else r["k"])


def _tk(t):
    """Łamania autora w środku zdania (żaden wiersz poza ostatnim nie kończy się kropką) -> spacje."""
    ls = t.split("\n")
    return " ".join(ls) if len(ls) > 1 and not any(_TERM.search(x) for x in ls[:-1]) else t


def _blok(r, k=None, align="l"):
    """Wiersz -> blok karty. big / sub nie mają odpowiedników w kartach: big -> h, sub -> lead (kolor marki)."""
    k = k or {"big": "h", "sub": "lead"}.get(r["k"], r["k"])
    b = {"k": k, "t": (BUL if r.get("li") else "") + _tk(r["t"]), "align": align}
    col = r.get("color") or ("brand" if r["k"] in ("h", "sub", "big") and k in ("p", "b", "lead") else None)
    if col:
        b["color"] = col
    if r.get("wyr"):
        b["wyr"] = ("-" + r["wyr"]) if r.get("li") else r["wyr"]
    return b


def _karta(items, pad, min_h, valign="m"):
    return {"k": "cols", "items": items, "card": True, "kont": True, "pad": pad, "min_h": min_h, "valign": valign}


def _wiersz_cytat(r, q, a):
    row = {"k": "quote", "t": q, "author": a, "_pole": r["_pole"]}
    fl, nq = r.get("_fl"), len(q.split())
    if fl and len(fl) == len(r["t"].split()) and nq <= len(fl):
        _kolor_fl(fl[:nq], row, lato=True)
    if r.get("color") == "accent" and not row.get("color") and not row.get("wyr"):
        row["color"] = "accent"
    return row


def _cytaty(rows):
    """R4: cytat z autorem - (a) wiersz kończy się nawiasem z >= 2 słowami z wielkiej litery („… (Byron Sharp)”)
    albo (b) fragment w „…” z >= 2 słowami, a następny wiersz tego pola to krótki podpis (<= 6 słów, bez kropki)."""
    out, i = [], 0
    while i < len(rows):
        r = rows[i]
        if not _tekst(r) or r.get("li"):
            out.append(r)
            i += 1
            continue
        t = " ".join(r["t"].split())
        m = _CYT_NAW.match(t)
        if m and sum(1 for x in m.group("a").split() if x[:1].isupper()) >= 2:
            # 09.10 (runda 3): nawiasy i kropka końcowa zostają przy autorze („(Byron Sharp, Ehrenberg-Bass).”)
            out.append(_wiersz_cytat(r, m.group("q").strip(), t[m.end("q"):].strip()))
            i += 1
            continue
        nx = rows[i + 1] if i + 1 < len(rows) else None
        if nx is not None and _tekst(nx) and not nx.get("li") and nx["_pole"] == r["_pole"] and \
                any(len(x.split()) >= 2 for x in _CYT_CUD.findall(t)) and _w(nx) <= 6 and len(nx["t"]) <= 40 and \
                not re.search(r"[.!?:]\s*$", nx["t"]):
            out.append(_wiersz_cytat(r, t, " ".join(nx["t"].split())))
            i += 2
            continue
        out.append(r)
        i += 1
    return out


def _etykiety(rows):
    """R8: etykieta grupy docelowej / insightu (CT:, TA:, Insight:) zostaje gołym wierszem h, do lewej."""
    return [dict(r, k="h", align="l", _et=True) if _tekst(r) and _ETYKIETA.match(r["t"]) else r for r in rows]


def _r6_ok(u):
    if not 2 <= len(u) <= 4:
        return False
    ws = [_w(r) for r in u]
    if max(ws) > 22 or max(ws) > 2.5 * min(ws):
        return False
    pts = [r.get("_pt") or 0 for r in u]
    if min(pts) and max(pts) > 1.15 * min(pts):
        return False
    return not any(r["t"].lstrip().startswith(("=", "+")) or _CZESC.match(r["t"].lstrip()) or
                   r["t"].rstrip().endswith(":") for r in u)


def _karty6(u):
    """R6: 2-4 równe karty obok siebie (s21 szablonu). R6a: każda myśl „Prefiks – reszta” (różne prefiksy) ->
    nagłówek karty (zieleń / czerwień jak w źródle) + reszta pod nim."""
    pre = [_PREFIKS.match(" ".join(r["t"].split())) for r in u]
    items = []
    if all(pre) and len({m.group(1).lower() for m in pre}) == len(u):
        for r, m in zip(u, pre):
            np_, fl = len(m.group(1).split()), r.get("_fl")
            ok = bool(fl) and len(fl) == len(r["t"].split())
            # 09.10 (runda 3): myślnik z oryginału zostaje na końcu nagłówka („Dobra wiadomość –”) - tekst znak w znak
            ph = {"k": "h", "t": m.group(1) + " " + m.group(2), "one_line": True}
            if ok and set(fl[:np_]) == {"a"}:
                ph["color"] = "accent"
            rest = {"k": "lead", "t": m.group(3).strip()}
            if ok:
                _kolor({"flagi": fl[np_ + 1:]}, rest, baza="kol")
            items.append({"blocks": [ph, rest]})
    else:
        # zdanie z kropką (>= 8 słów) to nie hasło: jedna taka myśl w parze / trójce = wszystkie karty Lato (K5, spójność)
        lato = any(_lato(r) or (_w(r) >= 8 and _KONIEC.search(r["t"].rstrip())) for r in u)
        for r in u:
            blk = _blok(r, k="p" if lato else None)
            if lato and r["k"] in ("h", "sub", "big") and "color" not in r:
                blk.pop("color", None)  # kolor bazowy pola w akapicie Lato nie jest wyróżnieniem (jak w _kolor_fl)
            items.append({"blocks": [blk]})
    return _karta(items, 1.2 if len(items) <= 2 else 0.6, 0, "t")  # trzy-cztery wąskie karty: pad 0,6 (tekst na szerokość karty)


def _stos(karta):
    """Wariant układu: karty z jednej karty-rzędu jedna pod drugą (każda na całą szerokość)."""
    return [dict(karta, items=[it]) for it in karta["items"]]


def _r6(run):
    """Szuka w ciągu wierszy dużego pisma 2-4 jednostek-kart: jednostka = pole (gdy >= 2 pola po 1 wierszu) albo
    wiersz (gdy to jedno pole z 2-4 wierszami); gdy mieszane - tylko wiersze jedynego pola wielowierszowego.
    Zwraca (od, do, karta) albo None."""
    i = 0
    while i < len(run):
        if not run[i].get("_duze") or run[i].get("li"):
            i += 1
            continue
        j = i
        while j < len(run) and run[j].get("_duze") and not run[j].get("li"):
            j += 1
        sl = run[i:j]
        poles = list(dict.fromkeys(r["_pole"] for r in sl))
        cnt = collections.Counter(r["_pole"] for r in sl)
        a, b = i, j
        if not (len(poles) == 1 or (len(poles) >= 2 and all(c == 1 for c in cnt.values()))):
            multi = [p for p in poles if cnt[p] > 1]
            idx = [k for k, r in enumerate(sl) if multi and r["_pole"] == multi[0]]
            if len(multi) != 1 or idx[-1] - idx[0] + 1 != len(idx):
                i = j
                continue
            a, b = i + idx[0], i + idx[-1] + 1
        if _r6_ok(run[a:b]):
            return a, b, _karty6(run[a:b])
        i = j
    return None


def _karta5(run):
    """R5: 1-4 wiersze haseł w jednej kremowej karcie, wyśrodkowane (s14 szablonu w karcie). Pismo bloku zachowuje
    proporcje źródła (mediana = rozmiar bazowy), w granicach 0,8-1,35."""
    pts = [r.get("_pt") or 36 for r in run]
    med = statistics.median(pts)
    blocks = []
    for r, pt in zip(run, pts):
        b = _blok(r, align=r.get("align", "c"))
        base = build_dk.UK_COL[b["k"]][1]
        b["pt"] = int(round(base * min(1.35, max(0.8, pt / med))))
        blocks.append(b)
    return _karta([{"blocks": blocks}], 1.6, 4.5)


def _naglowek_r7(r):
    return (r["k"] in _MIND + ("b",) and _w(r) <= 6) or r["t"].rstrip().endswith(":")


def _grupy_r7(run):
    """R7b: samotny wiersz-nagłówek (Mindset <= 6 słów albo zakończony ':') zaczyna nową grupę = nową kartę."""
    groups, cur = [], []
    for i, r in enumerate(run):
        if cur and i < len(run) - 1 and _naglowek_r7(r) and any(not _naglowek_r7(x) for x in cur):
            groups.append(cur)
            cur = []
        cur.append(r)
    if cur:
        groups.append(cur)
    return groups


def _karta7(g):
    """R7: akapity w kremowej karcie na całą szerokość (s16 szablonu); nagłówek grupy jako blok h."""
    blocks = []
    for i, r in enumerate(g):
        blocks.append(_blok(r, k="h" if (i == 0 and len(g) > 1 and _naglowek_r7(r)) else None))
    return _karta([{"blocks": blocks}], 1.0, 0)  # 10.10: pad 1,0 (było 1,6) - duży tekst (s41) dostaje miejsce


def _r7_ok(g):
    if all(r.get("li") for r in g):  # sama lista punktów zostaje punktami z kropką marki (s17)
        return False
    return any(r.get("_duze") for r in g) or sum(_w(r) for r in g) >= 20 or len(g) >= 2


def _komentarz(r):
    """Wiersz-wniosek po kartach: Mindset, ale nie większy niż tekst kart (08.10: „odwrócona hierarchia”)."""
    return dict(r, pt=22, max_pt=24, po_kartach=True)


def _run(run, pk, nk, alt=False):
    """Ciąg kolejnych wierszy tekstu (przerwany obrazami, kafelkami, kolumnami, cytatem) -> wiersze i karty.
    pk / nk = rodzaj wiersza przed / po ciągu ('karta', 'chips', 'pics', 'cols', ...).
    alt = wariant układu: karty z R6 jedna pod drugą, a grupy z R7b obok siebie (wybiera lepszy _uklad)."""
    if not run:
        return []
    if len(run) == 1 and run[0]["k"] in _MIND and (_w(run[0]) <= 12 or run[0]["t"].rstrip().endswith(":")) and \
            (nk in ("chips", "pics", "cols", "karta") or pk in ("karta", "pics")):
        return [_komentarz(run[0]) if pk == "karta" else run[0]]  # R9 (wstęp przed pojemnikiem) i R10b (wniosek po kartach)
    r6 = _r6(run)
    if r6:
        a, b, karta = r6
        return _run(run[:a], pk, "karta", alt) + (_stos(karta) if alt else [karta]) + _run(run[b:], "karta", nk, alt)
    if all(r["k"] in _MIND for r in run):
        return [_karta5(run)] if len(run) <= 4 else list(run)
    out = []
    if len(run) >= 2 and run[-1]["k"] in _MIND and _w(run[-1]) <= 12 and not run[-1]["t"].rstrip().endswith(":"):
        body, tail = run[:-1], [_komentarz(run[-1])]  # R10b: wniosek Mindsetem po akapitach
    else:
        body, tail = run, []
    grupy = _grupy_r7(body)
    if alt and 2 <= len(grupy) <= 3 and all(_r7_ok(g) for g in grupy):  # kilka kart-artykułów obok siebie
        karty = [_karta7(g) for g in grupy]
        return [dict(karty[0], items=[k["items"][0] for k in karty], pad=1.2, valign="t")] + tail  # góry kart równo
    for g in grupy:
        out += [_karta7(g)] if _r7_ok(g) else list(g)
    return out + tail


def _pojemniki(rows, alt=False):
    """Wiersze slajdu `uklad` -> te same teksty w pojemnikach z szablonu (reguły R4-R10 z references/konwersja-pptx.md).
    Zwraca NOWĄ listę; wiersze wejściowe się nie zmieniają (fallback w _uklad zostaje ze starymi)."""
    rows = _etykiety(_cytaty(list(rows)))
    out, run = [], []

    def zrzut(nxt):
        nonlocal run
        if run:
            out.extend(_run(run, _rodzaj(out[-1]) if out else None, _rodzaj(nxt), alt))
            run = []

    for r in rows:
        if _tekst(r):
            run.append(r)
        else:
            zrzut(r)
            out.append(r)
    zrzut(None)
    if len(out) > 1:  # karta obok innych wierszy / drugiej karty: bez wymuszonej wysokości, mniejsze marginesy
        po_karcie = False
        for i, r in enumerate(out):
            if r.get("kont"):
                r["min_h"] = 0
                r["pad"] = min(r["pad"], 1.0)
                r["bgap"] = 0.3
                po_karcie = True
            elif i and out[i - 1].get("kont") and r["k"] != "pics":
                out[i] = dict(r, gap=0.9)
            if po_karcie and not r.get("kont") and r["k"] in ("p", "b") and not r.get("li"):
                out[i] = dict(out[i], pt=17, max_pt=26, po_kartach=True)  # komentarz pod kartami: pismo jak w kartach
            if po_karcie and r.get("_et"):
                out[i] = dict(out[i], pt=28)  # etykieta CT / TA pod kartami: nie przytłacza tekstu kart
            if r["k"] == "pics" and any(x.get("kont") for x in out):
                r["h"] = min(r.get("h", 8.5), 6.2)
    return out


def _czysc(sp):
    """Usuwa znaczniki robocze (klucze zaczynające się od '_') z wierszy, kolumn i bloków specu."""
    for r in sp.get("rows", []):
        for k in [k for k in r if k.startswith("_")]:
            del r[k]
        for it in r.get("items", []) if r.get("k") == "cols" else []:
            for bl in it.get("blocks", []):
                for k in [k for k in bl if k.startswith("_")]:
                    del bl[k]


def _min_pt(sp):
    """(mieści się?, najmniejsze pismo wiersza, najmniejsze pismo w kolumnie) dla slajdu `uklad`."""
    ms, _f = build_dk.uklad_layout(sp)
    if ms is None:
        return False, 0, 0
    row, col = [99], [99]
    for m, r in zip(ms, sp["rows"]):
        if m["kind"] in ("text", "quote") and r["k"] != "small":
            row.append(m["pt"])
        elif m["kind"] == "cols":
            for (parts, _iw), it in zip(m["cols"], m["items"]):
                for (kind, _y, _h, d), bl in zip(parts, it.get("blocks", [])):
                    if kind == "txt" and bl["k"] != "small":
                        col.append(d["pt"])
    return True, min(row), min(col)


def _miesci(sp):
    ok, r, c = _min_pt(sp)
    return ok and r >= MIN_PT and c >= MIN_PT_KOL


def _ocena(sp):
    """(najmniejsze pismo tekstu w pt, kara) układu z kartami; kara = 4 za wąską kolumnę Lato (akapit >= 8 słów z >= 2
    liniami po jednym słowie: „samej / zarówno / dobrze”, albo średnio < 1,9 słowa w linii). (-1, 0) = nie mieści się.
    Służy do wyboru między układem a jego wariantem."""
    ms, _f = build_dk.uklad_layout(sp)
    if ms is None:
        return -1, 0
    pts, kara = [99], 0
    for m, r in zip(ms, sp["rows"]):
        if m["kind"] == "cols":
            if m.get("rwane") and len(m["cols"]) >= 3:  # 10.10: trzy-cztery wąskie karty z „rwanym” Lato (s18, s21, s40)
                kara = max(kara, 8)
            for (parts, _iw), it in zip(m["cols"], m["items"]):
                for (kind, _y, _h, d), bl in zip(parts, it.get("blocks", [])):
                    if kind == "txt" and bl["k"] != "small":
                        pts.append(d["pt"])
                        nw = len(bl["t"].split())
                        jedno = sum(1 for ln in d["lines"] if len(ln.split()) == 1)  # linie z jednym słowem
                        if d["font"] == "body" and nw >= 8 and (jedno >= 2 or nw / max(1, len(d["lines"])) < 1.9):
                            kara = max(kara, 4)
        elif m["kind"] in ("text", "quote") and r["k"] != "small":
            pts.append(m["pt"])
    return min(pts), kara


def _zwez(sp):
    """Wąskie kolumny Lato (słowa pojedynczo w linii, patrz _ocena): zmniejszamy górną granicę pisma, aż kara znika
    (jeśli pismo nie spadnie poniżej 15 pt). Zwraca slajd (ten sam albo z niższym max_f)."""
    if _ocena(sp)[1] == 0:
        return sp
    for mf in (1.4, 1.3, 1.2, 1.1, 1.0, 0.9):
        s2 = dict(sp, max_f=mf)
        pt, kara = _ocena(s2)
        if kara == 0 and pt >= 15:
            return s2
    return sp


def _wartosc(sp):
    pt, kara = _ocena(sp)
    return pt - kara


def _proste(rows):
    """Układ awaryjny: to samo w zwykłych wierszach, w kolejności czytania (kolumna po kolumnie, od lewej)."""
    out = []
    for r in rows:
        if r["k"] != "cols":
            out.append(r)
            continue
        for it in r["items"]:
            for bl in it.get("blocks", []):
                if bl["k"] == "img":
                    out.append({"k": "pics", "items": [{"image": bl["image"], "caption": ""}]})
                else:
                    out.append({"k": {"h": "sub", "lead": "p"}.get(bl["k"], bl["k"]), "t": bl["t"],
                                **({"align": "l"} if bl["k"] == "h" else {})})
            for key in ("tag", "meta"):
                if it.get(key):
                    out.append({"k": "small", "t": it[key]})
    return out


def _podziel(sp):
    """Ostatni szczebel: wiersze na kolejne slajdy „(1/2)”, tak żeby każdy mieścił się pismem >= 13 pt."""
    rows, parts, cur = list(sp["rows"]), [], []
    while rows:
        r = rows.pop(0)
        if _miesci(dict(sp, rows=cur + [r])):
            cur.append(r)
            continue
        if cur:
            parts.append(cur)
            cur = []
            rows.insert(0, r)
            continue
        ps = _split_sentences(r["t"]) if r.get("t") and r["k"] in ("p", "b", "lead", "h", "sub") else []
        if len(ps) < 2:
            cur.append(r)  # pojedynczy wiersz-gigant: zostaje (build_dk zmniejszy pismo poniżej progu)
            parts.append(cur)
            cur = []
            continue
        half = len(ps) // 2 or 1
        rows.insert(0, dict(r, t=" ".join(ps[half:])))
        rows.insert(0, dict(r, t=" ".join(ps[:half])))
    if cur:
        parts.append(cur)
    out = [dict(sp, rows=p) for p in parts]
    return [_suffix(s, k, len(out)) for k, s in enumerate(out, 1)]


def _wizualizacje(sp, sl, ctx):
    """Slajd portfolio: nad nagłówkiem KAŻDEJ kolumny grafika z paczkami linii - tylko gdy wszystkie kolumny mają
    dokładne dopasowanie w bibliotece, a tekst po dodaniu grafik nadal trzyma próg czytelności (12 pt w kartach)
    i nie maleje o więcej niż jedną czwartą."""
    if not ctx.get("lib") or sl["obrazy"]:
        return
    for r in sp["rows"]:
        if r["k"] != "cols" or len(r["items"]) < 2 or r.get("kont"):  # karty-pojemniki nie dostają packshotów
            continue
        heads = [next((bl["t"] for bl in it["blocks"] if bl["k"] == "h"), None) for it in r["items"]]
        if not all(heads):
            continue
        import wizki
        if ctx.get("idx") is None:
            ctx["idx"] = wizki.indeks(ctx["lib"])
        kat = wizki.kategoria_z("%s %s" % (sp.get("title") or "", sp.get("kicker") or ""), ctx["idx"])
        res = [wizki.dla_nazwy(h, ctx["idx"], kat, os.path.join(ctx["rob"], "wiz")) for h in heads]
        opis = "; ".join("%s - %s" % (h, x["opis"]) for h, x in zip(heads, res))
        got = [x for x in res if x["image"]]
        if not got:
            if any("kandydat" in x["opis"] for x in res):
                ctx["uwagi"].append("Slajd %d: wizualizacji nie wstawiłem. Możliwe dopasowania: %s." % (sl["n"], opis))
            continue
        if len(got) < len(heads):
            ctx["uwagi"].append("Slajd %d: wizualizacji nie wstawiłem, bo nie każda kolumna ma dokładne dopasowanie "
                                "w bibliotece: %s." % (sl["n"], opis))
            continue
        f0 = build_dk.uklad_fit(sp)
        for hh in (3.7, 3.0, 2.5):
            for it, x in zip(r["items"], res):
                it["blocks"] = [bl for bl in it["blocks"] if not bl.get("_wiz")]
                it["blocks"].insert(0, {"k": "img", "image": x["image"], "h": hh, "_wiz": True,
                                        "name": ("Wizualizacja: " + ", ".join(os.path.basename(p) for p in x["pliki"]))[:240]})
            f1 = build_dk.uklad_fit(sp)
            if f0 and f1 and f1 >= 0.75 * f0 - 1e-9 and _miesci(sp):
                r["grow"] = True
                ctx["wiz"].append({"slajd": sl["n"], "kolumny": [{"nazwa": h, "opis": x["opis"], "pliki": x["pliki"]}
                                                                  for h, x in zip(heads, res)]})
                ctx["uwagi"].append("Slajd %d: dodałem wizualizacje z biblioteki produktów - %s. Sprawdź dobór." % (
                    sl["n"], "; ".join("%s: %s" % (h, x["opis"]) for h, x in zip(heads, res))))
                break
        else:
            for it in r["items"]:
                it["blocks"] = [bl for bl in it["blocks"] if not bl.get("_wiz")]
            ctx["uwagi"].append("Slajd %d: wizualizacje są w bibliotece (%s), ale tekst zrobiłby się przez nie za mały - "
                                "nie wstawiłem." % (sl["n"], opis))


def _szer(t, pt):
    return build_dk.bd.text_w_emu(t, pt, build_dk.FONT_REF["display"][1])


def _dopasuj_hasla(sp):
    """Hasła z łamaniami autora: rozmiar pisma taki, żeby najdłuższy wiersz mieścił się w szerokości slajdu (inaczej
    builder złamałby go drugi raz, w innym miejscu niż autor). Zwraca największy współczynnik powiększenia, przy
    którym żaden taki wiersz się nie łamie."""
    wmax = cm(27.5) * 0.97
    fmax = 9.0
    for r in sp["rows"]:
        if r["k"] not in ("lead", "h", "big", "sub") or not r.get("t"):
            continue
        lines = [ln for ln in r["t"].splitlines() if len(ln) <= 48]
        if not lines:
            continue  # jedno długie zdanie bez łamań autora: łamie się samo
        pt = r.get("pt", build_dk.UK_KIND[r["k"]][1])
        need = max(_szer(ln, pt) for ln in lines)
        if need > wmax:
            pt = max(22, int(pt * wmax / need))
            r["pt"] = pt
            need = max(_szer(ln, pt) for ln in lines)
        fmax = min(fmax, wmax / max(need, 1))
    return fmax


def _odstep(a, b):
    """Odległość między dwoma prostokątami (0 = stykają się albo nachodzą)."""
    dx = max(0.0, a["x"] - (b["x"] + b["w"]), b["x"] - (a["x"] + a["w"]))
    dy = max(0.0, a["y"] - (b["y"] + b["h"]), b["y"] - (a["y"] + a["h"]))
    return (dx * dx + dy * dy) ** 0.5


def _siatka(sl, blocks, ctx):
    """Układ awaryjny slajdu-kolażu (dużo obrazów i krótkich podpisów w dowolnych miejscach): obrazy w jednym albo
    dwóch rzędach, w kolejności czytania; każdy krótki tekst jako podpis NAJBLIŻSZEGO obrazu (kontekst zostaje);
    długie teksty jako zwykłe wiersze nad obrazami."""
    n, hc = sl["n"], max(i["y"] + i["h"] for i in sl["obrazy"])
    imgs = sorted(sl["obrazy"], key=lambda i: (round((i["y"] + i["h"] / 2) / (0.4 * hc)), i["x"]))
    caps, rows = collections.defaultdict(list), []
    for b in sorted(blocks, key=lambda b: (b["y"], b["x"])):
        ws = _wiersze(b)
        if not ws:
            continue
        t = " ".join(_lit(ctx, n, b, [w["t"] for w in ws]))
        if len(t) <= 140:
            caps[min(range(len(imgs)), key=lambda k: _odstep(b, imgs[k]))].append(t)
        else:
            rows += _wiersze_pola(b, ctx, n)
    per = len(imgs) if len(imgs) <= 4 else (len(imgs) + 1) // 2
    for a in range(0, len(imgs), per):
        rows.append({"k": "pics", "min_h": 3.6, "h": 6.0,
                     "items": [{"image": im["path"], "caption": " · ".join(caps.get(a + j, []))}
                               for j, im in enumerate(imgs[a:a + per])]})
    return rows


def _uklad(sl, model, ctx):
    """Jeden slajd źródła -> lista slajdów `uklad` (zwykle jeden). Drabina: układ z pozycji -> siatka obrazów z
    podpisami (slajd-kolaż) -> proste wiersze -> podział na kolejne slajdy."""
    hc = model["h_cm"]
    hdr_b, blocks = _body(sl, hc)
    hdr = _lit(ctx, sl["n"], hdr_b, [_text_of(hdr_b)])[0] if hdr_b is not None else None
    for b in blocks:
        b.pop("_od", None)
    own_b, own = _wlasny_naglowek(blocks, sl["obrazy"], ctx)
    if own_b is not None:
        blocks = [b for b in blocks if b is not own_b]
    else:
        own_b, own = _pierwszy_wiersz_tytulem(blocks, ctx)
    if own:
        own = _lit(ctx, sl["n"], own_b, [own])[0]
    rows, niepewny = _uklad_wiersze(sl, blocks, ctx)

    def zloz(rs):
        """Slajd `uklad` z wierszy: tytuł / kicker, tło papierowe (krem tylko jako karta), pismo, wizualizacje."""
        rs = list(rs)
        sp = {"type": "uklad", "rows": rs}
        if own:
            sp["title"] = own
            if hdr and _kick_ok(hdr):
                sp["kicker"] = hdr
            elif hdr:
                rs.insert(0, {"k": "small", "t": hdr})
        elif hdr:
            sp["title" if _title_fits(hdr) else "kicker"] = hdr
        kinds = [r["k"] for r in rs]
        karty = [r for r in rs if r.get("kont")]
        chars = sum(len(r.get("t", "")) for r in rs) + \
            sum(len(bl.get("t", "")) for r in karty for it in r["items"] for bl in it["blocks"])
        fmax = _dopasuj_hasla(sp)
        if rs and ("pics" not in kinds or karty) and (chars <= 260 or karty) and \
                all(r["k"] != "cols" or r.get("kont") for r in rs):
            # karty-pojemniki: pismo rośnie do wypełnienia karty (granica pisma w karcie: build_dk.KONT_PT)
            sp["max_f"] = max(1.0, min(1.6 if karty else 1.25, int(fmax * 20) / 20.0))
        if kinds == ["cols"] and not rs[0].get("kont"):
            rs[0]["grow"] = True
        if 2 <= len(rs) <= 4 and all(r["k"] in ("b", "p") and r.get("li") for r in rs):  # s02: krótka lista - środek slajdu
            sp["valign"], sp["max_f"] = "m", 1.3
            for r in rs:
                r.setdefault("gap", 0.9)
        _wizualizacje(sp, sl, ctx)
        return sp

    nowe = _pojemniki(rows)
    sp = _zwez(zloz(nowe))
    alt = _pojemniki(rows, True)
    if json.dumps(alt, ensure_ascii=False, default=str) != json.dumps(nowe, ensure_ascii=False, default=str):
        sp2 = _zwez(zloz(alt))  # wariant: karty jedna pod drugą <-> obok siebie; wygrywa większe pismo / szersze linie
        o1 = _wartosc(sp)
        if o1 < 20 and _wartosc(sp2) > o1 + 0.5:  # podstawowy układ ma pismo >= 20 pt i szerokie linie: zostaje
            nowe, sp = alt, sp2
    if any(r.get("kont") or r["k"] == "quote" for r in nowe) and not _miesci(sp):
        # R12: karty nie mieszczą się - zostają stare wiersze (bez kart), slajd do sprawdzenia
        ctx["sprawdz"].append(sl["n"])
        ctx["uwagi"].append("Slajd %d: karty nie mieszczą się czytelnym pismem - zostawiłem zwykłe wiersze." % sl["n"])
        sp = zloz(rows)
    else:
        rows = nowe
    if niepewny:
        ctx["sprawdz"].append(sl["n"])
    if _miesci(sp):
        return [sp]
    if len(sl["obrazy"]) >= 3:  # slajd-kolaż: zanim cokolwiek podzielimy - obrazy w siatce z podpisami
        siatka = dict(sp, rows=_siatka(sl, blocks, ctx))
        siatka.pop("bg", None)
        siatka.pop("max_f", None)
        if _miesci(siatka):
            ctx["sprawdz"].append(sl["n"])
            ctx["uwagi"].append("Slajd %d: obrazy i podpisy stały w dowolnych miejscach - ułożyłem obrazy w rzędach, "
                                "a każdy podpis dałem przy najbliższym obrazie. Sprawdź, czy podpisy trafiły do swoich "
                                "obrazów." % sl["n"])
            return [siatka]
    simple = dict(sp, rows=_proste(rows))
    simple.pop("bg", None)
    if any(r["k"] == "cols" for r in rows) and _miesci(simple):
        ctx["sprawdz"].append(sl["n"])
        ctx["uwagi"].append("Slajd %d: kolumny nie mieszczą się czytelnym pismem - ułożyłem treść w wierszach, w "
                            "kolejności oryginału." % sl["n"])
        return [simple]
    parts = _podziel(simple if any(r["k"] == "cols" for r in rows) else sp)
    ctx["sprawdz"].append(sl["n"])
    if len(parts) > 1:
        ctx["uwagi"].append("Slajd %d: tekst nie mieści się na jednym slajdzie pismem %d pt - podzielony na %d części."
                            % (sl["n"], MIN_PT, len(parts)))
    return parts


def _specjalny(sl, model, first, last):
    """Slajdy, które w stylu DK mają własny typ: okładka, zakończenie, przerywnik (belka jako `label`, bez dopisanego
    numeru). None = zwykły slajd treści."""
    hc = model["h_cm"]
    if sl["tables"] or sl["charts"]:
        return None
    if first and sl["texts"] and not sl["obrazy"]:
        cov = _cover_spec(sl, None, _items(_order(sl["texts"], hc)), hc)
        if cov and cov[0].get("subtitle"):
            # podtytuł okładki ma 4 cm: tekst układamy na nowo i dobieramy pismo (20 / 16 / 14 pt); gdy nadal się nie
            # mieści, pierwszy slajd idzie jak zwykły slajd treści - niczego nie ucinamy
            sub = " ".join(cov[0]["subtitle"].split())
            w = build_dk.W - (build_dk.W / 2 + cm(2.2)) - build_dk.MX
            ok = next((pt for pt in (20, 16, 14)
                       if len(build_dk.lines_for(sub, pt, w)) * pt * 1.4 * 12700 <= cm(4)), None)
            cov = None if ok is None else [dict(cov[0], subtitle=sub, **({"subtitle_pt": ok} if ok != 20 else {}))] + cov[1:]
        if cov:
            return cov
    hdr_b, blocks = _body(sl, hc)
    hdr = _text_of(hdr_b) if hdr_b else None
    items = _items(blocks)
    male = all(i["w"] * i["h"] <= 0.12 * model["w_cm"] * hc for i in sl["obrazy"])  # samo logo to nie treść
    if last and male and not hdr and items and items[0]["t"].startswith("#") and len(items[0]["t"]) <= 40:
        spec = {"type": "end", "hashtag": items[0]["t"], "valign": "m"}  # blok logo + hasztag na środku slajdu
        if len(items) > 1:
            spec["contact"] = "  ·  ".join(i["t"] for i in items[1:])
        return [spec]
    sec = is_section(sl, hc, first)
    if sec and last:
        return [{"type": "end", "variant": "light", "title": _clean(sec), **({"subtitle": hdr} if hdr else {})}]
    if sec:
        return [{"type": "section", "variant": "dark", "number": "", "title": _clean(sec),
                 **({"label": hdr} if hdr else {})}]
    return None


def _slajd(s, model, ctx, first, last):
    """Jeden slajd źródła -> slajdy DK: typ własny (okładka, przerywnik, zakończenie), tabela / wykres starą ścieżką,
    cała reszta typem `uklad` z pozycji na starym slajdzie."""
    sp = _specjalny(s, model, first, last)
    if sp:
        for one in sp:  # data / autor na okładce to nie drobny druk (oryginał: duża, zielona)
            if one.get("type") == "cover_text" and one.get("meta"):
                one["meta_big"] = True
        if any(p.get("caps") for b in s["texts"] for p in b["paras"]):
            for one in sp:  # drobny tekst okładki / przerywnika idzie Lato: zwykła wielkość liter jak wszędzie
                for key in ("subtitle", "meta", "contact"):
                    if one.get(key):
                        old = one[key].split("\n")
                        new = _zdaniowo(old, ctx["chron"])
                        ctx["litery"] += [(s["n"], a, b) for a, b in zip(old, new) if a != b]
                        one[key] = "\n".join(new)
        return sp
    if s["tables"] or s["charts"]:
        return _convert(s, model, first, last, None)
    if not s["texts"] and not s["obrazy"]:
        return []
    return _uklad(s, model, ctx)


def polecenie_ai(cel, dane=None):
    """Punkty polecenia dla AI dla wybranego celu (jedno źródło dla programu, wiersza poleceń i dokumentów)."""
    dane = dane or {}
    return [p % dane if "%(" in p else p for p in CELE[cel if cel in CELE else "wiernie"]["polecenie"]]


def wstaw_dodatki(spec, extra):
    """Cel „Rozwiń / dokończ”: puste slajdy z szablonu (z podpowiedziami w [nawiasach]) wstawione PRZED zakończeniem
    oryginału; w notatkach „NOWY”. Poprawia mapę slajdów źródła. Zwraca numery (od 1) nowych slajdów."""
    if not extra:
        return []
    sl = spec["slides"]
    pos = len(sl) - 1 if sl and sl[-1].get("type") == "end" else len(sl)
    for e in extra:
        e["nowy"] = True
        e["notes"] = "NOWY slajd z szablonu (nie było go w oryginale). Uzupełnij teksty w [nawiasach kwadratowych]."
    sl[pos:pos] = extra
    for k, idx in spec["mapa"].items():
        spec["mapa"][k] = [i + len(extra) if i >= pos else i for i in idx]
    return list(range(pos + 1, pos + 1 + len(extra)))


def compose(model, opts=None):
    """Model -> spec dla build_dk.py. opts: cel (wiernie | rozwin | skroc), sekcje (id rozdziałów widocznych w pokazie;
    pozostałe zostają w pliku jako slajdy UKRYTE - nic nie znika), wizualizacje (domyślnie tak, gdy jest biblioteka),
    biblioteka (ścieżka do '01 - PRODUKTY\\- DK'), wyjscie."""
    opts = opts or {}
    cel = opts.get("cel") if opts.get("cel") in CELE else "wiernie"
    sl = model["slajdy"]
    chapters = detect_chapters(model)
    chosen = opts.get("sekcje")
    ukryj, uwagi = set(), list(model["uwagi"])
    if chosen is not None and any(c["id"] in chosen for c in chapters):
        for c in chapters:
            if c["id"] not in chosen:
                ukryj |= set(c["slajdy"])
                uwagi.append("Rozdział „%s” (slajdy %s) jest wyłączony: jego slajdy zostały w pliku jako ukryte." % (
                    c["nazwa"], _range(c["slajdy"])))
    first_of = {c["slajdy"][0]: c for c in chapters}
    n_last = sl[-1]["n"] if sl else 0
    kol = collections.Counter()
    for s in sl:
        for b in s["texts"]:
            for p in b["paras"]:
                for c, v in (p.get("kols") or {}).items():
                    kol[c] += v * len(p["t"])
    lib = None
    if opts.get("wizualizacje", True):
        import wizki
        lib = opts.get("biblioteka") or wizki.biblioteka(model["plik"], HERE)
    sk = (build_dk.H / EMU_CM) / model["h_cm"]
    ctx = {"skala": sk, "sk_y": sk, "wc": model["w_cm"], "glowny": kol.most_common(1)[0][0] if kol else None,
           "chron": _chronione(model), "maly": _maly(model), "litery": [], "uwagi": uwagi, "sprawdz": [], "wiz": [], "lib": lib, "idx": None,
           "rob": model["rob"]}
    slides, mapa = [], {}
    for s in sl:
        try:
            specs = _slajd(s, model, ctx, s["n"] == 1, s["n"] == n_last)
        except Exception as e:  # nigdy nie gubimy slajdu po cichu: awaryjnie cały tekst w wierszach, w kolejności źródła
            ctx["sprawdz"].append(s["n"])
            uwagi.append("Slajd %d: nietypowy układ (%s: %s) - treść ułożona w zwykłych wierszach, w kolejności oryginału."
                         % (s["n"], type(e).__name__, e))
            rows = [{"k": "p", "t": i["t"]} for i in _items(_order(s["texts"], model["h_cm"]))]
            if s["obrazy"]:
                rows.append({"k": "pics", "items": [{"image": im["path"], "caption": ""} for im in s["obrazy"]]})
            specs = _podziel({"type": "uklad", "rows": rows})
        if not specs:
            specs = [{"type": "uklad", "rows": []}]
            if not s["notes"]:
                specs[0]["notes"] = "W oryginale ten slajd nie miał treści do przeniesienia (sam układ graficzny)."
            uwagi.append("Slajd %d: w oryginale bez treści (sam układ graficzny) - zostaje pusty slajd na tym samym "
                         "miejscu." % s["n"])
        if len(specs) > 1 and s["n"] not in ctx["sprawdz"]:
            ctx["sprawdz"].append(s["n"])
            uwagi.append("Slajd %d: w nowym stylu zajmuje %d slajdy (tabela, wykres albo okładka z obrazami)."
                         % (s["n"], len(specs)))
        for k, sp in enumerate(specs):
            sp["zrodlo"] = s["n"]
            if k == 0 and s["notes"]:
                sp["notes"] = s["notes"]
            if s["hidden"] or s["n"] in ukryj:
                sp["hidden"] = True
        if s["n"] in first_of and len(chapters) > 1:
            specs[0]["section"] = first_of[s["n"]]["nazwa"]
        _links(s, specs)
        mapa[str(s["n"])] = list(range(len(slides), len(slides) + len(specs)))
        slides += specs
    for sp in slides:  # znaczniki robocze (_poj, _wiz, _pole, _fl ...) nie trafiają do specu
        _czysc(sp)
    st = model["stat"]
    if st["grafiki"]:
        uwagi.append("Grafiki: przeniesiono %d (całe, bez przycinania). Tekst na zrzutach ekranu zostaje obrazem - "
                     "nie jest przepisywany automatycznie." % st["grafiki"])
    if ctx["litery"]:
        log = os.path.join(model["rob"], "wielkosc-liter.txt")
        try:
            with open(log, "w", encoding="utf8") as f:
                f.write("Wielkość liter zmieniona automatycznie (oryginał jest pisany wersalikami). było -> jest\n\n")
                for n, a, b in ctx["litery"]:
                    f.write("slajd %d: %s  ->  %s\n" % (n, a, b))
        except OSError:
            log = None
        ex = "; ".join("„%s” -> „%s”" % (a, b) for _n, a, b in ctx["litery"][:2])
        uwagi.append("Oryginał jest pisany wersalikami: ustawiłem zwykłą wielkość liter w %d wierszach (np. %s). Sprawdź "
                     "nazwy własne i skróty%s." % (len(ctx["litery"]), ex,
                                                  " - pełna lista: " + os.path.basename(log) if log else ""))
    sprawdz = sorted(set(ctx["sprawdz"]))
    if sprawdz:
        uwagi.append("Sprawdź najpierw slajdy oryginału nr %s - mają nietypowy układ albo dużo tekstu."
                     % ", ".join(str(n) for n in sprawdz))
    n_ukr = sum(1 for sp in slides if sp.get("hidden"))
    if n_ukr:
        uwagi.append("Slajdy ukryte: %d (zostają w pliku, nie widać ich w pokazie; usunięto 0). Przed wysłaniem pliku "
                     "poza firmę usuń je w PowerPoincie albo zapisz PDF." % n_ukr)
    uwagi.append("Animacje, przejścia i tła slajdów z oryginału nie są przenoszone - to kwestia stylu, nie treści.")
    out_dir = opts.get("wyjscie") or os.path.dirname(model["plik"])
    if opts.get("styl") == "stary":
        uwagi.append("Stary styl jest niedostępny dla konwersji gotowej prezentacji - zbudowano w nowym stylu.")
    return {"theme": "shop", "sections": len(chapters) > 1, "slides": slides, "mapa": mapa, "uwagi": uwagi, "cel": cel,
            "sprawdz": sprawdz, "wizualizacje": ctx["wiz"], "litery": len(ctx["litery"]),
            "biblioteka": lib,
            "output": os.path.join(out_dir, "%s - nowy styl%s.pptx" % (model["nazwa"], CELE[cel]["sufiks"]))}


def _range(nums):
    nums = sorted(nums)
    return "%d-%d" % (nums[0], nums[-1]) if len(nums) > 1 else str(nums[0])


def _widoczny(sp):
    """Cały widoczny tekst slajdu wyniku jednym napisem (do szukania fragmentu z hiperłączem)."""
    out = [sp.get(k) or "" for k in ("kicker", "title", "subtitle", "label", "meta")]
    for r in sp.get("rows", []):
        out += [r.get("t") or "", r.get("author") or ""]
        if r["k"] == "chips":
            out += list(r.get("items") or [])
        elif r["k"] == "cols":
            for it in r.get("items") or []:
                out += [bl.get("t") or "" for bl in it.get("blocks", [])]
    return " ".join(" ".join(x.replace(" ", " ").split()) for x in out if isinstance(x, str)).lower()


def _links(s, specs):
    """Hiperłącza oryginału (08.10: żadnego dopisanego napisu „Link: …” na slajdzie). Adres widoczny w tekście wyniku:
    nic. Hiperłącze na słowach („Byron Sharp”, zdanie o słodzikach): zostaje na tych samych słowach (spec `links`, builder
    kładzie je na przebiegu tekstu). Reszta (kliknięcie w obraz, tekst, którego nie ma w wyniku): adres w notatkach."""
    shown = json.dumps(specs, ensure_ascii=False)
    done, miss = set(), []
    for t, u in s["links"]:
        if not u or u in shown or u in done:
            continue
        w = " ".join((t or "").replace(" ", " ").split())
        sp = next((x for x in specs if w and w.lower() in _widoczny(x)), None)
        if sp is not None:
            sp.setdefault("links", []).append({"t": w, "url": u})
            done.add(u)
        else:
            miss.append(u)
    miss = [u for u in dict.fromkeys(miss) if u not in done]
    if miss and specs:
        old = specs[0].get("notes")
        specs[0]["notes"] = ((old + "\n\n") if old else "") + "[Hiperłącza z oryginału] " + "  ".join(miss)


# =====================================================================================================
# 3. COVERAGE
# =====================================================================================================
def _norm(t):
    t = t.lower().replace(" ", " ").replace("\u000b", " ").replace("\v", " ")
    t = re.sub(r"[–—−‑]", "-", t)
    t = re.sub(r"[„”“”»«]", '"', t)
    return t


def _tokens(t):
    return re.findall(r"\w+", _norm(t), re.U)


def _xml_paras(root, skip_ph=True):
    """Akapity (a:p) z XML slajdu / notatek - niezależnie od modelu: łapie też grupy, tabele i pola."""
    out = []
    for p in root.iter(qn("a:p")):
        if skip_ph:
            sp = next((a for a in p.iterancestors() if a.tag in (qn("p:sp"),)), None)
            if sp is not None:
                ph = sp.find(".//" + qn("p:ph"))
                if ph is not None and ph.get("type") in ("sldNum", "ftr", "dt"):
                    continue
        txt = []
        for el in p:
            if el.tag in (qn("a:r"), qn("a:fld")):
                txt.append("".join(x.text or "" for x in el.iter(qn("a:t"))))
            elif el.tag == qn("a:br"):
                txt.append(" ")
        t = " ".join("".join(txt).split())
        if len(t) >= 3 and _tokens(t):
            out.append(t)
    return out


def _slide_paras(prs):
    res = []
    for sl in prs.slides:
        main = _xml_paras(sl._element)
        notes = _xml_paras(sl.notes_slide._element) if sl.has_notes_slide else []
        res.append((main, notes))
    return res


def coverage(src_pptx, out_pptx, mapa=None, skip=(), rob=None):
    """Czy każdy akapit źródła (>= 3 znaki) jest w wyniku? Test na tokenach: >= 95% tokenów akapitu musi się znaleźć
    na slajdach wyniku (albo w ich notatkach). mapa {nr slajdu źródła: [indeksy slajdów wyniku]} zawęża szukanie do
    slajdów, na które trafił dany slajd źródła; bez niej - okno 3 kolejnych slajdów wyniku. skip: slajdy źródła
    świadomie pominięte (wyłączone rozdziały)."""
    sp = otworz(src_pptx, rob or os.path.dirname(os.path.abspath(out_pptx)))
    op = Presentation(out_pptx)
    src, out = _slide_paras(sp), _slide_paras(op)
    out_cnt = []
    for main, notes in out:
        c = collections.Counter()
        for p in main + notes:
            c.update(_tokens(p))
        out_cnt.append(c)
    total = ok = 0
    missing = []
    skip = set(skip)
    for n, (main, notes) in enumerate(src, 1):
        if n in skip:
            continue
        if mapa is not None and str(n) in mapa:
            idx = mapa[str(n)]
            wins = [sum((out_cnt[i] for i in idx), collections.Counter())] if idx else []
        else:
            wins = [sum(out_cnt[i:i + w], collections.Counter()) for w in (1, 2, 3) for i in range(len(out_cnt))]
        for p in main + notes:
            tk = collections.Counter(_tokens(p))
            need = sum(tk.values())
            total += 1
            best = max((sum(min(v, w[t]) for t, v in tk.items()) / need for w in wins), default=0.0)
            if best >= 0.95:
                ok += 1
            else:
                missing.append({"slajd": n, "tekst": p[:160], "zgodnosc": round(best, 2)})
    chs = _chart_data(sp), _chart_data(op)
    ch_ok = sum(1 for c in chs[0] if c in chs[1])
    pct = 100.0 * ok / total if total else 100.0
    return {"akapity": total, "przeniesione": ok, "brakuje": missing, "procent": round(pct, 1),
            "wykresy": {"zrodlo": len(chs[0]), "przeniesione": ch_ok},
            "tekst": ("Treść: 100%% akapitów (%d/%d) przeniesionych" % (ok, total)) if ok == total else
                     ("Treść: %.1f%% akapitów (%d/%d) przeniesionych, brakuje %d" % (pct, ok, total, total - ok))}


def _chart_data(prs):
    out = []
    for sl in prs.slides:
        for sh in sl.shapes:
            if getattr(sh, "has_chart", False) and sh.has_chart:
                try:
                    pl = sh.chart.plots[0]
                    out.append((tuple(str(c) for c in pl.categories),
                                tuple(tuple(0.0 if v is None else round(float(v), 6) for v in s.values) for s in pl.series)))
                except Exception:
                    pass
    return out


def stats(model):
    """Liczby do ekranu 'Znalazłem w prezentacji' (akapity liczone tak samo jak w kontroli pokrycia)."""
    return {"slajdy": len(model["slajdy"]), "akapity": model["akapity"], "grafiki": model["stat"]["grafiki"],
            "tabele": model["stat"]["tabele"], "wykresy": model["stat"]["wykresy"]}


def produkt(model):
    """Nazwa prezentacji: tytuł okładki (jeśli krótki) albo nazwa pliku."""
    s = model["slajdy"][0] if model["slajdy"] else None
    if s and s["texts"]:
        big = max(s["texts"], key=lambda b: max((p["pt"] or 0) for p in b["paras"]))
        t = _clean(_text_of(big))
        if 2 <= len(t) <= 60:
            return t
    return model["nazwa"].replace("_", " ")


# =====================================================================================================
# 3a. WIERNOŚĆ UKŁADU (07.10.2026)
# =====================================================================================================
# Kontrola pokrycia liczy słowa na całych slajdach, więc „Segment 1 & 3” wklejone w zdanie nadal daje 100% - tak
# przeszła wersja, którą user odrzucił. Tu sprawdzamy to, na co on patrzy: czy osobne napisy są osobno, czy to, co
# stało wyżej, nadal jest wyżej, i czy wszystkie liczby są na swoim slajdzie.
def _nk(t):
    return " ".join(_tokens(t))


def _pola_wyniku(slide):
    """[(tekst znormalizowany, top, left)] pól tekstu slajdu wyniku - także w grupach i komórkach tabel."""
    out = []

    def walk(shapes):
        for sh in shapes:
            if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                walk(sh.shapes)
            elif getattr(sh, "has_table", False) and sh.has_table:
                for r in sh.table.rows:
                    for c in r.cells:
                        out.append((_nk(c.text), sh.top or 0, sh.left or 0))
            elif getattr(sh, "has_text_frame", False) and sh.has_text_frame and sh.text_frame.text.strip():
                out.append((_nk(sh.text_frame.text), sh.top or 0, sh.left or 0))
    walk(slide.shapes)
    return [o for o in out if o[0]]


def _liczby(root):
    """Liczby z tekstu slajdu (bez numeru strony, stopki i daty z symboli zastępczych)."""
    out = []
    for p in root.iter(qn("a:p")):
        sp = next((a for a in p.iterancestors() if a.tag == qn("p:sp")), None)
        if sp is not None:
            ph = sp.find(".//" + qn("p:ph"))
            if ph is not None and ph.get("type") in ("sldNum", "ftr", "dt"):
                continue
        t = "".join(x.text or "" for x in p.iter(qn("a:t")))
        out += re.findall(r"\d+(?:[.,]\d+)*", t)
    return out


def _interp(t):
    """Znaki interpunkcji i symbole akapitu (bez liter, cyfr i spacji): kropki, nawiasy, myślniki, cudzysłowy..."""
    return collections.Counter(re.findall(r"[^\w\s]", _norm(t).replace("…", "..."), re.U))


def wiernosc(model, out_pptx, mapa, nowe=0):
    """Czy wynik trzyma układ źródła. Zwraca {etykiety: [ok, wszystkie], kolejnosc: [naruszenia], liczby: [ok, wszystkie],
    slajdy: [źródło, wynik], usterki: [opisy z numerem slajdu], tekst: jedno zdanie do raportu}.
    etykiety - każde krótkie, jednowierszowe pole źródła (do 40 znaków) ma w wyniku WŁASNE pole o tym samym tekście;
    kolejnosc - pole, które w źródle stało nad innym w tej samej kolumnie, w wyniku też jest nad nim;
    liczby - każda liczba ze slajdu źródła jest na slajdach, które z niego powstały (także akapity 1-2-znakowe)."""
    op = Presentation(out_pptx)
    outs = [_pola_wyniku(s) for s in op.slides]
    onum = []
    for s in op.slides:
        c = collections.Counter(_liczby(s._element))
        if s.has_notes_slide:
            c.update(_liczby(s.notes_slide._element))
        onum.append(c)
    sp = otworz(model["plik"], model["rob"])
    snum = [collections.Counter(_liczby(s._element)) for s in sp.slides]
    zr_par, wy_par = _slide_paras(sp), _slide_paras(op)
    et_ok = et_all = li_ok = li_all = 0
    usterki, kolej, znaki, markery = [], [], [], []
    for s in model["slajdy"]:
        idx = mapa.get(str(s["n"]))
        if not idx:
            continue
        # znaki interpunkcji (nawiasy, myślniki, kropki): informacja, nie usterka - zdjęty punktor listy to nie brak słowa
        zr, mk = collections.Counter(), collections.Counter()
        for p_ in zr_par[s["n"] - 1][0]:
            m_ = _MARK.match(p_)
            if m_ and len(p_) > m_.end() and not re.match(r"\s*\d", m_.group(0)):
                mk += _interp(m_.group(0))  # 10.10: wiodący punktor / myślnik listy to marker, nie treść
                p_ = p_[m_.end():]
            zr += _interp(p_)
        wy = collections.Counter()
        for i in idx:
            for p_ in wy_par[i][0] + wy_par[i][1]:
                wy += _interp(p_)
        brak = zr - wy
        if brak:
            znaki.append({"slajd": s["n"], "brak": "".join(c * k for c, k in sorted(brak.items()))})
        if mk:
            markery.append({"slajd": s["n"], "marker": "".join(c * k for c, k in sorted(mk.items()))})
        pola = [(t, top, left, i) for i in idx for t, top, left in outs[i]]
        teksty = {t for t, _a, _b, _c in pola}
        # liczby
        have = sum((onum[i] for i in idx), collections.Counter())
        for num, cnt in snum[s["n"] - 1].items():
            li_all += cnt
            got = min(cnt, have[num])
            li_ok += got
            if got < cnt:
                usterki.append("slajd %d: brakuje liczby „%s”" % (s["n"], num))
        if s["tables"] or s["charts"]:
            continue
        # etykiety osobno
        for b in s["texts"]:
            one = _jedna_linia(b)
            if one and len(one) <= 40 and _nk(one):
                et_all += 1
                if _nk(one) in teksty:
                    et_ok += 1
                else:
                    usterki.append("slajd %d: napis „%s” nie jest osobnym elementem" % (s["n"], one))

        # kolejność góra-dół w kolumnie
        def gdzie(b):
            tk = collections.Counter(_tokens(_text_of(b)))
            need = sum(tk.values())
            best = None
            for t, top, _left, i in pola:
                c = collections.Counter(t.split())
                hit = sum(min(v, c[w]) for w, v in tk.items())
                if need and hit / need >= 0.6 and (best is None or hit > best[0]):
                    best = (hit, i, top)
            return best
        loc = [(b, gdzie(b)) for b in s["texts"]]
        for a, la in loc:
            for b, lb in loc:
                if a is b or la is None or lb is None:
                    continue
                ov = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
                if a["y"] + a["h"] <= b["y"] + 0.3 and ov >= 0.5 * min(a["w"], b["w"]):
                    if (la[1], la[2]) > (lb[1], lb[2] + 72000):  # ten sam slajd: A niżej niż B (tolerancja 2 mm)
                        kolej.append("slajd %d: „%s” jest pod „%s”, a w oryginale było nad" % (
                            s["n"], _text_of(a)[:40], _text_of(b)[:40]))
    n_src, n_out = len(model["slajdy"]), len(op.slides) - nowe
    if n_src != n_out:
        usterki.append("liczba slajdów: oryginał %d, wynik %d" % (n_src, n_out))
    usterki += kolej
    return {"etykiety": [et_ok, et_all], "kolejnosc": kolej, "liczby": [li_ok, li_all], "slajdy": [n_src, n_out],
            "usterki": usterki, "znaki": znaki, "markery": markery,
            "tekst": "Układ: osobne napisy %d z %d, kolejność góra-dół %s, liczby %d z %d, interpunkcja %s, %s" % (
                et_ok, et_all, "bez zmian" if not kolej else "zmieniona w %d miejscach" % len(kolej), li_ok, li_all,
                "bez różnic" if not znaki else "zdjęta na %d slajdach (lista w pokrycie.json: znaki)" % len(znaki),
                ("slajdów tyle samo (%d)" % n_src) if n_src == n_out else
                ("slajdów w oryginale %d, w wyniku %d" % (n_src, n_out)))}


# =====================================================================================================
# 4. CLI
# =====================================================================================================
def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # wynik kontroli z PowerPointa bywa w innym kodowaniu
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Konwersja gotowej prezentacji .pptx na styl Dobra Kaloria (bez utraty treści).")
    ap.add_argument("plik")
    ap.add_argument("--cel", choices=sorted(CELE), default="wiernie",
                    help="wiernie = ten sam slajd w nowym wyglądzie (domyślnie); rozwin = baza do dokończenia; "
                         "skroc = baza do skrócenia (wyłączone rozdziały zostają jako slajdy ukryte)")
    ap.add_argument("--sekcje", default="", help="id rozdziałów widocznych w pokazie (r01,r02...); pozostałe UKRYTE")
    ap.add_argument("--slajdy", type=int, default=0, help="cel skroc: ile slajdów ma zostać w pokazie (do polecenia dla AI)")
    ap.add_argument("--bez-wizualizacji", action="store_true", help="nie dokładaj packshotów z biblioteki produktów")
    ap.add_argument("--wyjscie", default="", help="katalog na PPTX (domyślnie obok źródła)")
    ap.add_argument("--robocze", default="", help="katalog roboczy (domyślnie <folder>\\_robocze\\<nazwa>)")
    ap.add_argument("--styl", choices=["nowy", "stary"], default="nowy")
    ap.add_argument("--bez-qa", action="store_true", help="bez PowerPointa (zrzuty, kontrola tekstu)")
    a = ap.parse_args(argv)
    plik = os.path.abspath(a.plik)
    stem = os.path.splitext(os.path.basename(plik))[0]
    rob = os.path.abspath(a.robocze) if a.robocze else os.path.join(os.path.dirname(plik), "_robocze", stem)
    os.makedirs(rob, exist_ok=True)
    model = extract(plik, rob)
    st = stats(model)
    print("Prezentacja: %s | %d slajdów, %d akapitów, %d grafik, %d tabel, %d wykresów" % (
        produkt(model), st["slajdy"], st["akapity"], st["grafiki"], st["tabele"], st["wykresy"]))
    sekcje = [x.strip() for x in a.sekcje.split(",") if x.strip()] or None
    spec = compose(model, {"styl": a.styl, "cel": a.cel, "sekcje": sekcje, "wizualizacje": not a.bez_wizualizacji,
                           "wyjscie": os.path.abspath(a.wyjscie) if a.wyjscie else None})
    os.makedirs(os.path.dirname(spec["output"]), exist_ok=True)
    spec_path = os.path.join(rob, "spec_konwersja.json")
    json.dump(spec, open(spec_path, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    import szybka
    if a.bez_qa:
        build_dk.build(spec, spec["output"])
        pptx = build_dk.build.last_out
    else:
        pptx = szybka.build_and_qa(spec_path, rob)
    cov = coverage(plik, pptx, spec["mapa"], rob=rob)
    wier = wiernosc(model, pptx, spec["mapa"])
    json.dump(dict(cov, wiernosc=wier), open(os.path.join(rob, "pokrycie.json"), "w", encoding="utf8"),
              ensure_ascii=False, indent=1)
    print("Cel: %s" % CELE[spec["cel"]]["nazwa"])
    print(cov["tekst"])
    for m in cov["brakuje"][:30]:
        print("  BRAK s%d (%.0f%%): %s" % (m["slajd"], 100 * m["zgodnosc"], m["tekst"]))
    print(wier["tekst"])
    for u in wier["usterki"][:30]:
        print("  USTERKA:", u)
    if wier.get("znaki"):  # informacja: znaki interpunkcji ze źródła, których nie ma w wyniku (np. punktor listy zastąpiony kropką)
        print("Znaki interpunkcji zdjęte (informacja): " + "; ".join("s%d: %s" % (z["slajd"], z["brak"]) for z in wier["znaki"][:40]))
    for u in spec["uwagi"]:
        print(" -", u)
    if a.cel != "wiernie":
        wid = sum(1 for s in spec["slides"] if not s.get("hidden"))
        print("\nPOLECENIE DLA AI (%s):" % CELE[a.cel]["nazwa"])
        for i, p in enumerate(polecenie_ai(a.cel, {"cel_slajdy": a.slajdy or "?", "widoczne": wid,
                                                   "wszystkie": len(spec["slides"])}), 1):
            print(" %d. %s" % (i, p))
    print("PPTX:", pptx)
    return 0 if not cov["brakuje"] and not wier["usterki"] else 1


if __name__ == "__main__":
    sys.exit(main())
