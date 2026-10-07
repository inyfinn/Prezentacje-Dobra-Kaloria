# -*- coding: utf-8 -*-
"""
build_dk.py - prezentacje Dobra Kaloria w nowym stylu (od 28.09.2026 zastępuje build_fresh.py).

    python build_dk.py spec.json [wyjscie.pptx]

Dwa motywy (spec "theme"):
  fresh - ciepły papier, szałwia, ciemnozielony tekst          (wersja B)
  shop  - jak dobrakaloria.pl: biel, kremowe karty, prawie czarne nagłówki, zieleń sklepu,
          etykiety w kształcie metki cenowej                    (wersja C)

Zasady (lekcje z iteracji z userem, patrz references/lekcje.md):
  * ZERO plam/bąbelków za produktem. Produkt = packshot + MAŁE elementy smaku rozsypane wokół
    (jak karty produktów w sklepie), miękki cień pod paczką.
  * Kolory tylko ze SLOTÓW MOTYWU PowerPointa (Tekst 1, Tło 2, Akcent 1-6) -> użytkownik zmienia
    kolory całej prezentacji w: Projektowanie > Warianty > Kolory. Wyjątek: kolory smaków (stałe).
  * Czcionki tylko z MOTYWU: nagłówki = Mindset (+mj-lt), treść = Lato (+mn-lt) -> Warianty > Czcionki.
  * Morph na każdym slajdzie; obiekty wspólne mają te same nazwy "!!..." (logo, tytuł, paczka).
  * Opis "do czego służy slajd" (spec "label") trafia do notatek i do etykiety POZA obszarem slajdu
    (widać ją przy edycji, w pokazie nie). Sekcje PowerPointa ze spec "section".
Po zbudowaniu: render.ps1 -EmbedFonts (osadza Lato; Mindset jest osadzony w szablonie bazowym).
"""
import json
import math
import os
import re
import sys
import uuid

from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_deck as bd  # noqa: E402
from build_deck import cm, img_ratio, place_image  # noqa: E402

A = os.path.join(bd.ROOT, "assets")
bd.FONT_FILES.update({
    "Lato": os.path.join(A, "fonts", "Lato-Regular.ttf"),
    "Lato Bold": os.path.join(A, "fonts", "Lato-Bold.ttf"),
})
W, H = bd.SLIDE_W, bd.SLIDE_H
MX = cm(2.4)          # margines boczny (więcej 'światła', 28.09)
CT = cm(5.3)          # góra obszaru treści (pod tytułem)
CB = H - cm(1.75)     # dół obszaru treści (nad stopką)
GAP = cm(0.9)         # odstęp między kartami

# --- motywy: wartości slotów -------------------------------------------------------------------
THEMES = {
    "fresh": dict(name="Dobra Kaloria - naturalny", ink="1F3A24", white="FFFFFF", brand="006400", paper="FAF6EF",
                  accent="D6232A", card="F1ECE2", sage="C9DABB", sage2="AD8767", sun="F2C94C", tag="pill"),
    "shop": dict(name="Dobra Kaloria - sklep", ink="3B2A20", white="FFFFFF", brand="0F763E", paper="FFFFFF",
                 accent="DA272D", card="FDF8EC", sage="E9F2EC", sage2="AD8767", sun="FFD42A", tag="price"),
}
T = dict(THEMES["fresh"])
# token -> (slot motywu, jasność). Jasność >0 rozjaśnia, <0 przyciemnia (lumMod/lumOff - też globalne).
SLOT = {
    "ink": (MSO_THEME_COLOR.TEXT_1, 0), "white": (MSO_THEME_COLOR.BACKGROUND_1, 0),
    "brand": (MSO_THEME_COLOR.ACCENT_1, 0), "paper": (MSO_THEME_COLOR.BACKGROUND_2, 0),
    "accent": (MSO_THEME_COLOR.ACCENT_2, 0), "card": (MSO_THEME_COLOR.ACCENT_3, 0),
    "sage": (MSO_THEME_COLOR.ACCENT_4, 0),
    "sun": (MSO_THEME_COLOR.ACCENT_6, 0),
    # beż "pod tło" (AD8767, wybór usera 28.09): tan = etykiety >=14 pt bold i podpisy >=18 pt (3:1),
    # muted = ten sam beż przyciemniony do >=4.5:1 dla drobnego tekstu
    "tan": (MSO_THEME_COLOR.ACCENT_5, 0), "muted": (MSO_THEME_COLOR.ACCENT_5, -0.30),
    "brand_soft": (MSO_THEME_COLOR.ACCENT_1, 0.55),
    "line": (MSO_THEME_COLOR.ACCENT_3, -0.10), "brand_hi": (MSO_THEME_COLOR.ACCENT_1, 0.18),
    "brand_lo": (MSO_THEME_COLOR.ACCENT_1, -0.25), "on_brand": (MSO_THEME_COLOR.BACKGROUND_1, -0.12),
}
FONT_REF = {"display": ("+mj-lt", "Mindset", False), "body": ("+mn-lt", "Lato", False),
            "bold": ("+mn-lt", "Lato Bold", True)}


def paint(color_format, token):
    """Ustawia kolor: token motywu (globalny) albo stały hex (kolory smaków)."""
    if token in SLOT:
        slot, br = SLOT[token]
        color_format.theme_color = slot
        if br:
            color_format.brightness = br
    else:
        color_format.rgb = RGBColor.from_string(token)


def hexof(token):
    """Wartość hex tokenu w bieżącym motywie (do obliczeń, np. placeholderów)."""
    return T.get(token, token) if token in T else (T["ink"] if token == "muted" else token)


def write_theme(prs, theme_name):
    """Wpisuje schemat kolorów i czcionek do motywu -> globalna zmiana w Projektowanie > Warianty."""
    t = THEMES[theme_name]
    part = prs.slide_master.part.part_related_by(RT.THEME)
    xml = part.blob.decode("utf8")
    clr = ('<a:clrScheme name="%s"><a:dk1><a:srgbClr val="%s"/></a:dk1><a:lt1><a:srgbClr val="%s"/></a:lt1>'
           '<a:dk2><a:srgbClr val="%s"/></a:dk2><a:lt2><a:srgbClr val="%s"/></a:lt2>'
           '<a:accent1><a:srgbClr val="%s"/></a:accent1><a:accent2><a:srgbClr val="%s"/></a:accent2>'
           '<a:accent3><a:srgbClr val="%s"/></a:accent3><a:accent4><a:srgbClr val="%s"/></a:accent4>'
           '<a:accent5><a:srgbClr val="%s"/></a:accent5><a:accent6><a:srgbClr val="%s"/></a:accent6>'
           '<a:hlink><a:srgbClr val="%s"/></a:hlink><a:folHlink><a:srgbClr val="%s"/></a:folHlink></a:clrScheme>'
           % (t["name"], t["ink"], t["white"], t["brand"], t["paper"], t["brand"], t["accent"], t["card"],
              t["sage"], t["sage2"], t["sun"], t["brand"], t["sage2"]))
    xml = re.sub(r"<a:clrScheme .*?</a:clrScheme>", clr, xml, flags=re.S)
    fonts = ('<a:fontScheme name="Dobra Kaloria"><a:majorFont><a:latin typeface="Mindset"/><a:ea typeface=""/>'
             '<a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Lato"/><a:ea typeface=""/>'
             '<a:cs typeface=""/></a:minorFont></a:fontScheme>')
    xml = re.sub(r"<a:fontScheme .*?</a:fontScheme>", fonts, xml, flags=re.S)
    part._blob = xml.encode("utf8")


# --- podstawowe elementy -------------------------------------------------------------------------
def named(sh, name):
    """'!!' na początku nazwy = Morph łączy obiekty o tej samej nazwie na sąsiednich slajdach."""
    sh.name = name
    return sh


def shape(s, kind, x, y, w, h, fill, radius=None, line=None, line_w=1.5, name=None):
    sh = s.shapes.add_shape(kind, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    if fill:
        sh.fill.solid()
        paint(sh.fill.fore_color, fill)
    else:
        sh.fill.background()
    if line:
        paint(sh.line.color, line)
        sh.line.width = Pt(line_w)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    tf = sh.text_frame
    tf.text = ""
    if name:
        sh.name = name
    return sh


def rect(s, x, y, w, h, fill, **kw):
    return shape(s, MSO_SHAPE.RECTANGLE, x, y, w, h, fill, **kw)


def card(s, x, y, w, h, fill="card", r=0.06, **kw):
    """Zaokrąglona karta; promień stały w cm (jak w sklepie) niezależnie od rozmiaru."""
    rr = min(0.5, cm(0.45) / max(1, min(w, h)))
    return shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, radius=rr if r is None else max(rr, 0) , **kw)


def dot(s, cx, cy, d, fill):
    return shape(s, MSO_SHAPE.OVAL, cx - d / 2, cy - d / 2, d, d, fill)


def lines_for(text, size, w, font="body"):
    """Łamanie tylko na spacjach + ochrona przed sierotą (jedno słowo w ostatniej linii)."""
    meas = FONT_REF[font][1]
    out = []
    for para in str(text).split("\n"):
        ls = bd.wrap_lines(para, size, int(w * 0.96), meas)
        if len(ls) >= 2 and len(ls[-1].split()) == 1 and len(ls[-2].split()) > 2:
            prev = ls[-2].split()
            ls[-2], ls[-1] = " ".join(prev[:-1]), prev[-1] + " " + ls[-1]
        out.extend(ls)
    return out


def txt(s, x, y, w, h, text, size, color="ink", font="body", align="l", anchor="t", line=None, spacing=None,
        caps=False, italic=False, name=None, wrap=True):
    """Pole tekstowe z czcionką i kolorem MOTYWU. text: str (łamany sam) albo lista linii."""
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(max(w, 10))), Emu(int(max(h, 10))))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    if caps:
        text = text.upper() if isinstance(text, str) else [t.upper() for t in text]
    if isinstance(text, str):
        text = lines_for(text, size, w, font) if (wrap and font != "display") else text.split("\n")
    ref, _, bold = FONT_REF[font]
    for i, ln in enumerate(text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        if line:
            p.line_spacing = Pt(line)
        r = p.add_run()
        r.text = bd.typo_nbsp(ln) if font != "display" else ln  # typografia PL (Lato ma twardą spację)
        r.font.size = Pt(size)
        r.font.name = ref
        r.font.bold = bold
        r.font.italic = italic
        paint(r.font.color, color)
        if spacing:
            r.font._rPr.set("spc", str(spacing))
    if name:
        tb.name = name
    return tb


def fit(text, max_pt, min_pt, w, font="display"):
    return bd.fit_size(text, max_pt, min_pt, int(w), FONT_REF[font][1])


def title_size(text, max_pt, min_pt, w):
    """Rozmiar tytułu: najdłuższe SŁOWO musi się zmieścić (tytuł może się łamać na spacjach). Typografia PL
    (29.09): gdy ostatnia linia byłaby jednym słowem, a da się tego uniknąć - czcionka o krok mniejsza."""
    size = fit(max(text.split(), key=len), max_pt, min_pt, w)
    floor = max(min_pt, size * 0.85)  # najwyżej ~15% mniej - większe zmniejszanie rozpycha nagłówek w 1 linię
    while size - 2 >= floor and _orphan(display_lines(text, size, w)):
        size -= 2
    return size


def _orphan(ls):
    """Sierota: ostatnia linia to jedno słowo, a poprzednia ma >=3 słowa albo to słowo jest krótkie (<=4 liter).
    "MANGO & / MARAKUJA" i "Co mówią / konsumenci" to NIE sieroty (reguła usera 29.09: krótkie słowa i spójniki)."""
    if len(ls) < 2 or len(ls[-1].split(" ")) != 1:
        return False
    return len(ls[-2].split(" ")) >= 3 or len(ls[-1].strip("?!.,")) <= 4


def display_lines(text, size, w, balance=True):
    """Łamanie nagłówka Mindset. balance: linie wyrównane długością (bez sieroty 'W / DIECIE?') - zwężamy
    szerokość, dopóki liczba linii się nie zmienia (29.09)."""
    if "\n" in text:  # łamanie ręczne ze specu ("1 g kreatyny\nw każdej kulce") - każdy kawałek osobno
        return [ln for part in text.split("\n") for ln in display_lines(part, size, w, balance)]
    ls = bd.wrap_lines(text, size, int(w), "Mindset")
    if not balance or len(ls) < 2:
        return ls
    best, ww = ls, w
    while ww > w * 0.45:
        ww *= 0.97
        t = bd.wrap_lines(text, size, int(ww), "Mindset")
        if len(t) != len(ls):
            break
        best = t
    if _orphan(best):  # sierota nie do usunięcia przeniesieniem (za szeroko) -> przedostatnia linia po słowie w linii
        best = best[:-2] + bd.typo_tokens(best[-2]) + best[-1:]
    return best


def pill_w(text, size, pad=cm(1.0), spacing=100, font="bold"):
    t = text.upper()
    return bd.text_w_emu(t, size, FONT_REF[font][1]) + len(t) * spacing / 100 * 12700 + pad


def tag(s, x, y, text, fill="brand", fg="white", size=11, h=None, dot_color=None, style=None):
    """Etykieta. Style jak na dobrakaloria.pl:
    button - żółty/kremowy prostokąt z lekko zaokrąglonymi rogami (przyciski 'ZOBACZ WIĘCEJ')
    badge  - znaczek z ostrymi końcami (NOWOŚĆ, BESTSELLER na listingu)
    price  - metka ceny ścięta tylko z lewej strony
    pill   - pigułka (motyw fresh)"""
    h = h or cm(0.85)
    style = style or ("pill" if T["tag"] == "pill" else "button")
    w = pill_w(text, size, spacing=60) + (cm(0.5) if dot_color else 0) + (cm(0.4) if style in ("badge", "price") else 0)
    if style == "badge":
        sh = shape(s, MSO_SHAPE.HEXAGON, x, y, w, h, fill)
        sh.adjustments[0] = 0.18
    elif style == "price":
        sh = shape(s, MSO_SHAPE.PENTAGON, x, y, w, h, fill)
        sh.adjustments[0] = 0.28
        sh._element.spPr.find(qn("a:xfrm")).set("flipH", "1")  # ostrze z lewej
    elif style == "button":
        sh = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, radius=min(0.5, cm(0.12) / h))
    else:
        sh = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, radius=0.5)
    tx = x + (cm(0.25) if style == "price" else 0)
    if dot_color:
        dot(s, x + cm(0.55), y + h / 2, cm(0.28), dot_color)
        tx += cm(0.35)
    txt(s, tx, y, w - (tx - x), h, text, size, color=fg, font="bold", align="c", anchor="m", caps=True, spacing=60)
    return w


def chip(s, x, y, text, on_dark=False, active=False):
    """Pigułka jak filtry na dobrakaloria.pl ('WSZYSTKIE' / 'COŚ NA SŁODKO'): pełne zaokrąglenie, Lato Bold,
    wersaliki. Na jasnym tle biała z cienką ramką, na zieleni biała bez ramki; active = zielona."""
    h = cm(0.9)
    w = pill_w(text, 11, spacing=60)
    fill = "brand" if active else "white"
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, radius=0.5,
          line=None if (on_dark or active) else "line", line_w=1)
    txt(s, x, y, w, h, text, 11, color="white" if active else "ink", font="bold", align="c", anchor="m", caps=True,
        spacing=60)
    return w


def kicker(s, x, y, text, color="tan", dot_color="accent"):
    """Etykieta nad tytułem: beż AD8767, 14 pt bold, wersaliki (fresh: z czerwoną kropką, sklep: sam tekst)."""
    return txt(s, x, y, cm(20), cm(0.7), text, 14, color=color, font="bold", caps=True, spacing=150, name="!!kicker")


def logo(s, x, y, w, kind="green_box", name="!!logo_small"):
    f = {"green_box": "logo_green_box.png", "white_box": "logo_white_box.png",
         "green_letters": "logo_green_letters.png"}[kind]
    pic = s.shapes.add_picture(os.path.join(A, f), Emu(int(x)), Emu(int(y)), Emu(int(w)))
    return named(pic, name)


def morph(slide, dur=1250):
    pns = "http://schemas.openxmlformats.org/presentationml/2006/main"
    el = etree.fromstring(
        '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:p="%s" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" '
        'xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main">'
        '<mc:Choice Requires="p159"><p:transition spd="slow" p14:dur="%d"><p159:morph option="byObject"/>'
        '</p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition>'
        '</mc:Fallback></mc:AlternateContent>' % (pns, dur))
    anchor = slide._element.find("{%s}clrMapOvr" % pns)
    if anchor is None:
        anchor = slide._element.find("{%s}cSld" % pns)
    anchor.addnext(el)


# --- obrazy: placeholder + scena produktu ----------------------------------------------------------
PH_DIR = None


def placeholder(ratio, label="ZDJĘCIE"):
    """PNG-zastępnik zdjęcia o zadanych proporcjach (w PowerPoint: prawy klik > Zmień obraz)."""
    w = 1200
    h = int(w / ratio)
    fn = os.path.join(PH_DIR, "ph_%d_%s.png" % (int(ratio * 1000), label.encode("ascii", "ignore").decode() or "x"))
    if os.path.exists(fn):
        return fn
    bg = tuple(int(hexof("card")[i:i + 2], 16) for i in (0, 2, 4))
    fg = tuple(max(0, c - 55) for c in bg)
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    s = min(w, h) // 6
    cx, cy = w // 2, h // 2 - s // 3
    d.rounded_rectangle([cx - s, cy - s * 0.7, cx + s, cy + s * 0.7], radius=s // 6, outline=fg, width=max(3, s // 18))
    d.polygon([(cx - s * 0.75, cy + s * 0.5), (cx - s * 0.2, cy - s * 0.1), (cx + s * 0.1, cy + s * 0.2),
               (cx + s * 0.35, cy), (cx + s * 0.75, cy + s * 0.5)], fill=fg)
    d.ellipse([cx + s * 0.25, cy - s * 0.45, cx + s * 0.5, cy - s * 0.2], fill=fg)
    try:
        f = ImageFont.truetype(bd.FONT_FILES["Lato Bold"], max(18, s // 4))
        tw = d.textlength(label, font=f)
        d.text((cx - tw / 2, cy + s * 0.9), label, fill=fg, font=f)
    except OSError:
        pass
    im.save(fn)
    return fn


def picture(s, path, x, y, w, h, name=None):
    """Obraz wypełniający ramkę (przycięcie 'cover', bez zniekształceń)."""
    if not path:
        path = placeholder(w / h)
    pic = s.shapes.add_picture(path, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    r_img, r_box = img_ratio(path), w / h
    if r_img > r_box:
        c = (1 - r_box / r_img) / 2
        pic.crop_left = pic.crop_right = c
    elif r_img < r_box:
        c = (1 - r_img / r_box) / 2
        pic.crop_top = pic.crop_bottom = c
    if name:
        pic.name = name
    return pic


# Małe elementy wokół paczki (jak w sklepie dobrakaloria.pl): (u, v) względem ramki paczki 0..1,
# rozmiar (dłuższy bok) jako ułamek wysokości paczki, obrót, przód(True)/za paczką(False).
SCATTER = [(-0.16, 0.30, 0.19, -16, True), (1.10, 0.16, 0.16, 24, False), (-0.10, 0.86, 0.21, 10, True),
           (1.14, 0.70, 0.20, -12, True), (0.26, 1.03, 0.14, 34, True), (0.80, 1.05, 0.16, -28, True),
           (0.62, -0.06, 0.12, 12, False), (-0.26, 0.58, 0.11, 40, False)]


def _hits(box, avoid):
    """Czy prostokąt (x0,y0,x1,y1) wchodzi w którąś strefę zakazaną (teksty, logo)."""
    return any(box[0] < a[2] and box[2] > a[0] and box[1] < a[3] and box[3] > a[1] for a in (avoid or []))


def scene_trio(s, packs, cx, cy, h, props=(), key="pack", prop_scale=1.0, avoid=None):
    """Trzy smaki razem (gdy tekst mówi o całej linii): dwie paczki z tyłu po bokach, jedna z przodu,
    drobne elementy wokół całej grupy. Kolejność packs: [lewa, środkowa (przód), prawa]."""
    props = [p for p in (props or []) if p]
    hb = h * 0.86
    wf = h * img_ratio(packs[1])
    wl, wr = hb * img_ratio(packs[0]), hb * img_ratio(packs[2])
    off = wf * 0.62
    boxes = [(packs[0], cx - off - wl / 2, cy - hb / 2 - h * 0.04, hb, -9),
             (packs[2], cx + off - wr / 2, cy - hb / 2 - h * 0.04, hb, 9),
             (packs[1], cx - wf / 2, cy - h / 2 + h * 0.03, h, -2)]
    x0 = min(b[1] for b in boxes)
    x1 = max(b[1] + b[3] * img_ratio(b[0]) for b in boxes)
    y0, y1 = cy - h / 2, cy + h / 2
    gw, gh = x1 - x0, y1 - y0
    placed = []
    for i, (u, v, f, r, front) in enumerate(SCATTER[:len(props)]):
        ratio = img_ratio(props[i])
        box = h * f * prop_scale * 0.85
        ph = box if ratio <= 1 else box / ratio
        px, py = x0 + u * gw - ph * ratio / 2, y0 + v * gh - ph / 2
        if _hits((px, py, px + ph * ratio, py + ph), avoid):  # element wszedłby na tekst/logo - pomijamy
            continue
        placed.append((front, props[i], px, py, ph, r, i))
    for front, path, px, py, ph, r, i in placed:
        if not front:
            named(place_image(s, path, px, py, h=ph, rot=r), "!!%s_el%d" % (key, i))
    for j, (path, bx, by, bh, r) in enumerate(boxes):
        named(place_image(s, path, bx, by, h=bh, rot=r, shadow=True, shadow_color="3B2A20"),
              "!!pack_%s" % ["l", "r", "c"][j])
    for front, path, px, py, ph, r, i in placed:
        if front:
            named(place_image(s, path, px, py, h=ph, rot=r), "!!%s_el%d" % (key, i))
    return x0, y0, x1, y1


def trio_width(packs, h):
    """Szerokość grupy trzech paczek (do dopasowania h do dostępnego miejsca)."""
    wf = h * img_ratio(packs[1])
    off = wf * 0.62
    return 2 * off + 0.86 * h * (img_ratio(packs[0]) + img_ratio(packs[2])) / 2 + h * 0.12


def fit_trio(packs, h, max_w):
    """Największe h <= h, przy którym trio mieści się w max_w (z zapasem na obrót)."""
    while h > cm(4) and trio_width(packs, h) > max_w:
        h -= cm(0.2)
    return h


def scene(s, pack, cx, cy, h, props=(), rot=-4, key="pack", prop_scale=1.0, avoid=None):
    """Paczka + małe elementy smaku wokół + miękki cień. Bez tła, bez plam. pack = lista 3 ścieżek -> trio."""
    if isinstance(pack, (list, tuple)):
        return scene_trio(s, pack, cx, cy, h, props, key=key, prop_scale=prop_scale, avoid=avoid)
    props = [p for p in (props or []) if p]
    if not pack:
        pack = placeholder(0.72, "PACKSHOT")
    w = h * img_ratio(pack)
    x0, y0 = cx - w / 2, cy - h / 2
    placed = []
    for i, (u, v, f, r, front) in enumerate(SCATTER[:len(props)]):
        ratio = img_ratio(props[i])
        box = h * f * prop_scale
        ph = box if ratio <= 1 else box / ratio
        px, py = x0 + u * w - ph * ratio / 2, y0 + v * h - ph / 2
        if _hits((px, py, px + ph * ratio, py + ph), avoid):  # element wszedłby na tekst/logo - pomijamy
            continue
        placed.append((front, props[i], px, py, ph, r, i))
    for front, path, px, py, ph, r, i in placed:
        if not front:
            named(place_image(s, path, px, py, h=ph, rot=r), "!!%s_el%d" % (key, i))
    named(place_image(s, pack, x0, y0, h=h, rot=rot, shadow=True, shadow_color="3B2A20"), "!!" + key)
    for front, path, px, py, ph, r, i in placed:
        if front:
            named(place_image(s, path, px, py, h=ph, rot=r), "!!%s_el%d" % (key, i))
    return x0, y0, x0 + w, y0 + h


# --- rama slajdu -------------------------------------------------------------------------------------
class Deck(bd.Deck):
    def __init__(self, spec):
        super().__init__()
        self.theme = spec.get("theme", "fresh")
        write_theme(self.prs, self.theme)
        self.page = 0
        self.sections = []  # (nazwa, [sldId...])
        self.footer = spec.get("footer", "")

    def slide(self, bg="paper"):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[0])
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        s.background.fill.solid()
        paint(s.background.fill.fore_color, bg)
        self.page += 1
        return s

    def finish(self, out):
        sld_ids = self.prs.slides._sldIdLst
        for sid in list(sld_ids)[: self.n_tpl]:
            self.prs.part.drop_rel(sid.get(qn("r:id")))
            sld_ids.remove(sid)
        if self.sections:
            self._write_sections()
        import guard  # nie nadpisuj plików edytowanych ręcznie (lekcja 28.09.2026)
        out = guard.safe_target(out)
        self.prs.save(out)
        guard.record(out)
        return out

    def _write_sections(self):
        p14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
        pres = self.prs.part._element
        ext_lst = pres.find(qn("p:extLst"))
        if ext_lst is None:
            ext_lst = etree.SubElement(pres, qn("p:extLst"))
        for e in ext_lst.findall(qn("p:ext")):
            if e.get("uri") == "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}":
                ext_lst.remove(e)
        ext = etree.SubElement(ext_lst, qn("p:ext"))
        ext.set("uri", "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}")
        lst = etree.SubElement(ext, "{%s}sectionLst" % p14, nsmap={"p14": p14})
        for name, ids in self.sections:
            sec = etree.SubElement(lst, "{%s}section" % p14)
            sec.set("name", name)
            sec.set("id", "{%s}" % str(uuid.uuid4()).upper())
            il = etree.SubElement(sec, "{%s}sldIdLst" % p14)
            for i in ids:
                etree.SubElement(il, "{%s}sldId" % p14).set("id", str(i))


def frame(deck, sp, bg="paper"):
    """Rama slajdu treści: kicker, tytuł (Mindset), małe logo, stopka ze źródłem, numer strony."""
    s = deck.slide(bg)
    if sp.get("kicker"):
        kicker(s, MX, cm(1.2), sp["kicker"])  # 08.10: wyżej o 0,3 cm - ogonki wersalików tytułu (Ś, Ó, Ż) nie dotykają etykiety
    if sp.get("title"):
        tw = cm(sp.get("title_w", 26))
        size = title_size(sp["title"], sp.get("title_size", 40), 26, tw)
        ls = display_lines(sp["title"], size, tw)
        txt(s, MX, cm(2.3), tw, len(ls) * size * 12700, ls, size, font="display", line=size, name="!!title")
    logo(s, W - MX - cm(1.9), cm(1.5), cm(1.9))
    foot = sp.get("source") or deck.footer
    if foot:
        txt(s, MX, H - cm(1.2), cm(26), cm(0.6), foot, 10.5, color="muted")
    txt(s, W - MX - cm(1.5), H - cm(1.2), cm(1.5), cm(0.6), "%02d" % deck.page, 10.5, color="muted", font="bold",
        align="r")
    return s


def text_block(s, x, y, w, sp, on_dark=False, max_pt=64, min_pt=36, sub_size=19, one_line=False, kicker_style=None):
    """Kicker + tytuł + podtytuł + etykiety smaków. Zwraca y końca. kicker_style: display (zielony Mindset,
    okładki od 29.09) / button (żółty przycisk sklepu) / label (beżowy tekst); spec 'kicker_style' wygrywa."""
    ink = "white" if on_dark else "ink"
    sub = "on_brand" if on_dark else "muted"
    ks = sp.get("kicker_style") or kicker_style or ("button" if T["tag"] == "price" else "label")
    if sp.get("kicker") and ks == "display":  # 29.09 wersja usera: "NOWOŚĆ" zielonym Mindsetem nad tytułem
        kz = max(22, int(max_pt * 0.64))
        txt(s, x, y, w, kz * 1.2 * 12700, sp["kicker"], kz, color="on_brand" if on_dark else "brand",
            font="display", name="!!kicker")
        y += kz * 1.2 * 12700 + cm(0.1)
    elif sp.get("kicker") and ks == "button" and not on_dark:  # żółty przycisk jak "ZOBACZ WIĘCEJ"
        tag(s, x, y - cm(0.1), sp["kicker"], fill="sun", fg="3B2A20", size=12, h=cm(0.95), style="button")
        y += cm(1.35)
    elif sp.get("kicker"):
        kicker(s, x, y, sp["kicker"], color="on_brand" if on_dark else "tan", dot_color="sun" if on_dark else "accent")
        y += cm(1.0)
    t = sp["title"]
    size = fit(t, max_pt, min_pt, w) if one_line else title_size(t, max_pt, min_pt, w)
    ls = [t] if one_line and bd.text_w_emu(t, size, "Mindset") <= w else display_lines(t, size, w)
    # 30.09: wiersz na granicy szerokości PowerPoint łamał jeszcze raz ("KULKI / Z / KREATYNĄ", +62 pt) -> 5% zapasu
    while size > min_pt and any(bd.text_w_emu(ln, size, "Mindset") > w * 0.95 for ln in ls):
        size -= 2
        ls = display_lines(t, size, w)
    txt(s, x, y, w, len(ls) * size * 12700, ls, size, color=ink, font="display", line=size * 0.98, name="!!title")
    y += len(ls) * size * 0.98 * 12700 + cm(0.45)
    if sp.get("subtitle"):
        ls = lines_for(sp["subtitle"], sub_size, w)
        txt(s, x, y, w, len(ls) * (sub_size * 1.42) * 12700, ls, sub_size, color=sub, line=sub_size * 1.42)
        y += len(ls) * sub_size * 1.42 * 12700 + cm(0.55)
    if sp.get("flavors"):
        xx = x
        for f in sp["flavors"]:
            cw = pill_w(f["name"], 11, spacing=60) + cm(0.3)
            if xx + cw > x + w and xx > x:  # nie mieści się -> nowa linia (nigdy poza slajd)
                xx, y = x, y + cm(1.1)
            xx += chip(s, xx, y, f["name"], on_dark) + cm(0.3)
        y += cm(1.2)
    return y


# --- slajdy powitalne ------------------------------------------------------------------------------
def s_cover(deck, sp):
    """Powitanie Z PRODUKTEM (variant 1-3) - duże logo na zielonym podziale (jak wzór marki).
    1: podział 42%, paczka NA granicy zieleni i papieru, tekst po prawej
    2: tekst biały na zieleni (51%), paczka po jasnej stronie
    3: klasyczny podział 50/50, logo na środku zieleni (1:1 ze wzorem), tytuł + paczka po prawej"""
    v = int(sp.get("variant", 1))
    s = deck.slide("paper")
    pack, props = sp.get("image"), sp.get("props", [])
    trio = isinstance(pack, (list, tuple))  # trzy paczki są ~1,6x szersze niż jedna -> mniejsza scena
    if v == 1:
        pw = cm(14.2)
        rect(s, 0, 0, pw, H, "brand", name="!!panel")
        logo(s, cm(2.0), cm(1.9), cm(6.2), "white_box", "!!logo")
        if trio:
            tx = cm(23.6)
            avoid = [(tx - cm(0.4), 0, W, H), (0, 0, cm(8.6), cm(7.0))]  # tekst + logo
            h = fit_trio(pack, cm(9.4), (tx - cm(0.8)) - cm(8.9))
            scene(s, pack, cm(8.9) + (tx - cm(0.8) - cm(8.9)) / 2, cm(11.6), h, props, rot=-6, avoid=avoid)
            text_block(s, tx, cm(4.6), W - tx - MX, sp, max_pt=56, kicker_style="display")
        else:
            scene(s, pack, pw, cm(10.9), cm(12.4), props, rot=-6)
            text_block(s, cm(21.8), cm(4.6), W - cm(21.8) - MX, sp, max_pt=64, kicker_style="display")
    elif v == 2:
        pw = cm(17.2)
        rect(s, 0, 0, pw, H, "brand", name="!!panel")
        logo(s, MX, cm(1.8), cm(5.6), "white_box", "!!logo")
        text_block(s, MX, cm(7.8), pw - MX - cm(1.4), sp, on_dark=True, max_pt=70, kicker_style="display")
        h = fit_trio(pack, cm(10.5), W - pw - cm(2.6)) if trio else cm(13.4)
        scene(s, pack, pw + (W - pw) / 2, cm(10.2), h, props, rot=5, avoid=[(0, 0, pw, H)])
    elif v == 4:  # 29.09 ręczna wersja usera: duże logo na środku zieleni, "NOWOŚĆ" + tytuł, pod nim 3 paczki
        pw = cm(14.2)
        rect(s, 0, 0, pw, H, "brand", name="!!panel")
        lw = cm(9.9)
        logo(s, (pw - lw) / 2, (H - lw * 295 / 400) / 2, lw, "white_box", "!!logo")
        tx = pw + cm(2.9)
        y = text_block(s, tx, cm(1.8), W - tx - MX, dict(sp, subtitle=None, flavors=None), max_pt=56, min_pt=36,
                       one_line=True, kicker_style="display")
        zx0, zx1 = pw + cm(1.2), W - cm(1.2)
        h = fit_trio(pack, cm(8.8), zx1 - zx0) if trio else cm(10.0)
        scene(s, pack, (zx0 + zx1) / 2, max(y + h / 2 + cm(1.0), cm(12.3)), h, props, rot=-4,
              avoid=[(0, 0, pw, H), (tx, 0, W, y + cm(0.2))])
    else:
        pw = W / 2
        rect(s, 0, 0, pw, H, "brand", name="!!panel")
        lw = cm(9.4)
        logo(s, (pw - lw) / 2, (H - lw * 295 / 400) / 2, lw, "white_box", "!!logo")
        cx = pw + (W - pw) / 2
        sp1 = dict(sp, subtitle=None)
        text_block(s, pw + cm(1.9), cm(1.5), W - pw - cm(3.8), sp1, max_pt=50, min_pt=32, one_line=True, kicker_style="display")
        h = fit_trio(pack, cm(9.0), W - pw - cm(2.6)) if trio else cm(10.4)
        scene(s, pack, cx, cm(12.1), h, props, rot=-4, avoid=[(0, 0, pw, H), (pw, 0, W, cm(5.2))])


def s_cover_text(deck, sp):
    """Powitanie BEZ PRODUKTU (variant 1-3): spotkania, raporty, prezentacje firmowe.
    1: podział 50/50 jak wzór - logo na zieleni, tytuł + podtytuł po prawej
    2: cała zieleń, logo u góry, duży biały tytuł na dole, opcjonalnie drobne owoce przy prawej krawędzi
    3: jasne tło, zielony pas u góry z logo, bardzo duży tytuł, linia z datą/autorem"""
    v = int(sp.get("variant", 1))
    if v == 1:
        s = deck.slide("paper")
        pw = W / 2
        rect(s, 0, 0, pw, H, "brand", name="!!panel")
        lw = cm(9.4)
        logo(s, (pw - lw) / 2, (H - lw * 295 / 400) / 2, lw, "white_box", "!!logo")
        x = pw + cm(2.2)
        w = W - x - MX
        y = text_block(s, x, cm(5.2), w, dict(sp, subtitle=None), max_pt=58, kicker_style="label")
        rect(s, x, y + cm(0.1), cm(3.2), cm(0.22), "brand")
        if sp.get("subtitle"):
            spt = sp.get("subtitle_pt", 20)  # konwersja: długi podtytuł mniejszym pismem (16 / 14), nigdy ucięty
            txt(s, x, y + cm(0.9), w, cm(4), sp["subtitle"], spt, color="muted", line=spt * 1.4)
        if sp.get("meta") and sp.get("meta_big") and not sp.get("subtitle"):
            # 08.10 (konwersja): data / autor to nie drobny druk - pod kreską, Mindset w zieleni marki jak w oryginale
            txt(s, x, y + cm(1.0), w, cm(1.6), sp["meta"], 28, color="brand", font="display", name="!!meta")
        elif sp.get("meta"):
            txt(s, x, H - cm(2.4), w, cm(0.8), sp["meta"], 13, color="muted", font="bold")
    elif v == 2:
        s = deck.slide("brand")
        logo(s, MX, cm(1.8), cm(5.2), "white_box", "!!logo")
        for i, p in enumerate(sp.get("props", [])[:5]):  # drobne owoce "wpadające" z prawej krawędzi
            h = cm([3.2, 2.4, 2.8, 2.0, 2.6][i])
            place_image(s, p, W - cm([4.2, 2.1, 5.8, 3.0, 1.2][i]), cm([2.0, 6.4, 9.6, 13.2, 15.6][i]),
                        h=h, rot=[-18, 22, 8, -30, 14][i]).name = "!!el%d" % i
        w = cm(22)
        size = title_size(sp["title"], 80, 44, w)
        ls = display_lines(sp["title"], size, w)
        y = H - cm(4.2) - len(ls) * size * 12700
        if sp.get("kicker"):
            txt(s, MX, y - cm(0.9), w, cm(0.7), sp["kicker"], 14, color="on_brand", font="bold",
                caps=True, spacing=150, name="!!kicker")
        txt(s, MX, y, w, len(ls) * size * 12700, ls, size, color="white", font="display", line=size * 0.98,
            name="!!title")
        if sp.get("subtitle"):
            txt(s, MX, H - cm(3.6), w, cm(2), sp["subtitle"], 19, color="on_brand", line=27)
    else:
        s = deck.slide("paper")
        band = cm(6.2)
        rect(s, 0, 0, W, band, "brand", name="!!panel")
        logo(s, MX, (band - cm(5.0) * 295 / 400) / 2, cm(5.0), "white_box", "!!logo")
        if sp.get("kicker"):
            txt(s, W - MX - cm(14), cm(2.7), cm(14), cm(0.8), sp["kicker"], 13, color="on_brand", font="bold",
                caps=True, spacing=200, align="r")
        w = W - 2 * MX
        size = title_size(sp["title"], 84, 44, w)
        ls = display_lines(sp["title"], size, w)
        txt(s, MX, band + cm(1.6), w, len(ls) * size * 12700, ls, size, font="display", line=size * 0.98,
            name="!!title")
        y = band + cm(1.6) + len(ls) * size * 0.98 * 12700 + cm(0.5)
        if sp.get("subtitle"):
            txt(s, MX, y, cm(24), cm(3), sp["subtitle"], 20, color="muted", line=28)
        rect(s, MX, H - cm(2.3), W - 2 * MX, cm(0.04), "line")
        if sp.get("meta"):
            txt(s, MX, H - cm(1.9), cm(24), cm(0.8), sp["meta"], 13, color="muted", font="bold")


# --- struktura ------------------------------------------------------------------------------------
def s_agenda(deck, sp):
    """Agenda / spis treści: numerowane punkty (do 8, dwie kolumny od 5)."""
    s = frame(deck, sp)
    items = sp["items"]
    cols = 2 if len(items) > 4 else 1
    per = math.ceil(len(items) / cols)
    cw = (W - 2 * MX - cm(1.5) * (cols - 1)) / cols
    rh = min(cm(2.6), ((CB - CT)) / per)
    for i, it in enumerate(items):
        c, r = divmod(i, per)
        x, y = MX + c * (cw + cm(1.5)), CT + r * rh
        rect(s, x, y, cw, cm(0.03), "line")
        txt(s, x, y + cm(0.35), cm(2.4), rh - cm(0.4), "%02d" % (i + 1), 34, color="brand", font="display")
        txt(s, x + cm(2.6), y + cm(0.45), cw - cm(2.6), cm(0.9), it if isinstance(it, str) else it["title"], 20,
            font="bold")
        if isinstance(it, dict) and it.get("text"):
            txt(s, x + cm(2.6), y + cm(1.3), cw - cm(2.6), rh - cm(1.4), it["text"], 14, color="muted", line=19)


def s_section(deck, sp):
    """Przerywnik rozdziału. variant dark: zieleń marki; light: jasne tło z ogromnym numerem."""
    dark = sp.get("variant", "dark") == "dark"
    s = deck.slide("brand" if dark else "paper")
    num = sp.get("number", "01")
    if dark:  # 29.09 wersja usera: etykieta białym Mindsetem 32 pt, logo w lewym górnym rogu, źródło drobno
        if sp.get("label"):  # 07.10: zamiast numeru - nagłówek ze starej belki (konwersja 1:1, bez dopisanych numerów)
            txt(s, MX, cm(5.25), cm(26), cm(0.8), sp["label"], 16, color="on_brand", font="bold", caps=True,
                spacing=150)
        elif num:  # "number": "" = bez numeru (konwersja nie dopisuje numerów rozdziałów, których nie było)
            txt(s, MX, cm(4.9), cm(14), cm(1.4), num, 32, color="white", font="display")
        w = cm(20)
        size = title_size(sp["title"], 66, 36, w)
        ls = display_lines(sp["title"], size, w)
        txt(s, MX, cm(6.4), w, len(ls) * size * 12700, ls, size, color="white", font="display", line=size,
            name="!!title")
        if sp.get("subtitle"):
            txt(s, MX, cm(6.8) + len(ls) * size * 12700, cm(16), cm(3), sp["subtitle"], 13, color="on_brand", line=18)
        logo(s, MX, cm(1.4), cm(1.9), "green_letters")
        if sp.get("image"):
            scene(s, sp["image"], W * 0.76, H * 0.52, cm(12), sp.get("props", []), rot=6)
    else:
        nw = bd.text_w_emu(num, 300, "Mindset")  # od lewej: prawy margines glifu przy 300 pt wypycha tekst za slajd
        txt(s, W - MX - nw - cm(0.6), cm(0.4), nw + cm(1.5), cm(13.5), num, 300, color="sage", font="display",
            name="tlo-numer")  # dekoracja: test krawędzi pomija (PowerPoint zawyża granice tekstu 300 pt)
        w = cm(20)
        size = title_size(sp["title"], 66, 36, w)
        ls = display_lines(sp["title"], size, w)
        y = H - cm(4.8) - len(ls) * size * 12700
        txt(s, MX, y, w, len(ls) * size * 12700, ls, size, font="display", line=size, name="!!title")
        if sp.get("subtitle"):
            txt(s, MX, H - cm(4.2), cm(18), cm(2.5), sp["subtitle"], 18, color="muted", line=26)
        logo(s, W - MX - cm(1.9), H - cm(2.8), cm(1.9))


# --- tekst -----------------------------------------------------------------------------------------
def s_lead(deck, sp):
    """Wstęp: duży akapit otwierający + 2-3 krótkie akapity rozwinięcia w kolumnach."""
    s = frame(deck, sp)
    w = cm(24)
    ls = lines_for(sp["lead"], 26, w)
    txt(s, MX, CT, w, len(ls) * 36 * 12700, ls, 26, line=36)
    y = CT + len(ls) * 36 * 12700 + cm(1.2)
    cols = sp.get("columns", [])
    if cols:
        cw = (W - 2 * MX - cm(1.2) * (len(cols) - 1)) / len(cols)
        for i, c in enumerate(cols):
            x = MX + i * (cw + cm(1.2))
            rect(s, x, y, cm(1.2), cm(0.1), "brand")
            txt(s, x, y + cm(0.5), cw, cm(0.9), c["title"], 16, font="bold")
            txt(s, x, y + cm(1.35), cw, H - y - cm(3), c["text"], 14, color="muted", line=20)


def s_statement(deck, sp):
    """Tekst krótki: jedno zdanie-hasło na środku (Mindset), mały kicker i podpis."""
    s = deck.slide(sp.get("bg", "card"))
    w = cm(26)
    size = title_size(sp["text"], sp.get("max_pt", 60), 34, w)  # max_pt: konwerter zmniejsza przy wielu liniach
    ls = display_lines(sp["text"], size, w)
    th = len(ls) * size * 12700
    y = (H - th) / 2 - cm(0.4)
    if sp.get("kicker"):
        txt(s, 0, y - cm(1.4), W, cm(0.7), sp["kicker"], 14, color="tan", font="bold", caps=True, spacing=150,
            align="c", name="!!kicker")
    txt(s, (W - w) / 2, y, w, th, ls, size, font="display", align="c", line=size, name="!!title")
    if sp.get("note"):
        txt(s, (W - w) / 2, y + th + cm(0.8), w, cm(1.5), sp["note"], 20, color="tan", align="c")
    logo(s, (W - cm(1.9)) / 2, H - cm(2.6), cm(1.9))


def s_longtext(deck, sp):
    """Tekst długi: dwie kolumny akapitów (np. opis rynku, historia marki). Max ~180 słów."""
    s = frame(deck, sp)
    cw = (W - 2 * MX - cm(1.6)) / 2
    for i, col in enumerate(sp["columns"][:2]):
        x = MX + i * (cw + cm(1.6))
        y = CT
        for para in col if isinstance(col, list) else [col]:
            ls = lines_for(para, 15, cw)
            txt(s, x, y, cw, len(ls) * 22 * 12700, ls, 15, line=22)
            y += len(ls) * 22 * 12700 + cm(0.5)


def s_bullets(deck, sp):
    """Punkty (3-6): kropka w kolorze marki, pogrubione hasło + opcjonalne rozwinięcie."""
    s = frame(deck, sp)
    items = sp["items"]
    has_img = bool(sp.get("image")) or sp.get("with_image")
    w = cm(17.5) if has_img else W - 2 * MX - cm(2)
    rh = min(cm(2.4), ((CB - CT)) / len(items))
    y0 = CT + max(0, ((CB - CT) - rh * len(items)) / 2)
    for i, it in enumerate(items):
        it = it if isinstance(it, dict) else {"title": it}
        y = y0 + i * rh
        dot(s, MX + cm(0.25), y + cm(0.45), cm(0.34), "brand")
        txt(s, MX + cm(0.9), y, w, cm(0.9), it["title"], 20, font="bold")
        if it.get("text"):
            txt(s, MX + cm(0.9), y + cm(0.85), w, rh - cm(0.9), it["text"], 14, color="muted", line=19)
    if has_img:
        x = MX + w + cm(2.4)
        picture(s, sp.get("image"), x, CT, W - MX - x, (CB - CT))


def s_steps(deck, sp):
    """Kroki / proces (3-5): numerowane karty w poziomie, cienka linia łącząca."""
    s = frame(deck, sp)
    items = sp["items"]
    n = len(items)
    g = GAP
    cw = (W - 2 * MX - g * (n - 1)) / n
    y = cm(5.6)
    rect(s, MX + cm(0.9), y + cm(0.85), W - 2 * MX - cm(1.8), cm(0.05), "line")
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        dot(s, x + cm(1.2), y + cm(0.87), cm(1.7), "brand" if i == 0 else "white")
        if i:
            shape(s, MSO_SHAPE.OVAL, x + cm(0.05), y + cm(0.02), cm(1.7), cm(1.7), None, line="brand", line_w=1.5)
        txt(s, x + cm(0.05), y + cm(0.02), cm(1.7), cm(1.7), str(i + 1), 20, color="white" if i == 0 else "brand",
            font="display", align="c", anchor="m")
        card(s, x, y + cm(2.4), cw, cm(8.2), "card")
        txt(s, x + cm(0.6), y + cm(3.0), cw - cm(1.2), cm(1.6), it["title"], 22, font="display")
        txt(s, x + cm(0.6), y + cm(4.5), cw - cm(1.2), cm(5.8), it.get("text", ""), 14, color="muted", line=20)


def s_quote(deck, sp):
    """Cytat / opinia klienta lub partnera: duży cudzysłów, tekst, autor."""
    s = frame(deck, dict(sp, title=None))
    txt(s, MX, (H - cm(8)) / 2 - cm(1.2), cm(6), cm(8.8), "„", 200, color="sage", font="display")
    w = cm(24)
    ls = lines_for(sp["quote"], 30, w)
    block = len(ls) * 42 * 12700 + cm(3.2)
    y0 = max(cm(4.6), (H - block) / 2)  # blok cytatu wysrodkowany w pionie
    txt(s, MX + cm(3.6), y0, w, len(ls) * 42 * 12700, ls, 30, italic=True, line=42)
    y = y0 + len(ls) * 42 * 12700 + cm(1.0)
    rect(s, MX + cm(3.6), y, cm(2.4), cm(0.1), "brand")
    txt(s, MX + cm(3.6), y + cm(0.5), w, cm(0.8), sp.get("author", ""), 16, font="bold")
    txt(s, MX + cm(3.6), y + cm(1.3), w, cm(0.8), sp.get("role", ""), 14, color="muted")


def s_two_cols(deck, sp):
    """Porównanie dwóch stron (np. rynek dziś vs nasza propozycja): prawa karta wyróżniona."""
    s = frame(deck, sp)
    cw = (W - 2 * MX - cm(0.8)) / 2
    for i, col in enumerate(sp["columns"][:2]):
        x = MX + i * (cw + cm(0.8))
        hi = i == 1
        card(s, x, CT, cw, (CB - CT), "brand" if hi else "card")
        txt(s, x + cm(1), cm(5.6), cw - cm(2), cm(1.4), col["title"], 28, color="white" if hi else "ink",
            font="display")
        y = cm(7.4)
        for b in col["items"]:
            dot(s, x + cm(1.15), y + cm(0.35), cm(0.26), "white" if hi else "brand")  # 29.09: bez żółtego
            ls = lines_for(b, 16, cw - cm(2.6))
            txt(s, x + cm(1.6), y, cw - cm(2.6), len(ls) * 22 * 12700, ls, 16,
                color="white" if hi else "ink", line=22)
            y += len(ls) * 22 * 12700 + cm(0.45)


# --- tekst + grafika --------------------------------------------------------------------------------
def s_text_image(deck, sp):
    """Tekst + grafika. side: 'right' (grafika z prawej) / 'left'. Grafika do krawędzi slajdu."""
    s = deck.slide("paper")
    right = sp.get("side", "right") == "right"
    iw = W * 0.46
    ix = W - iw if right else 0
    if sp.get("pack"):
        rect(s, ix, 0, iw, H, "card")
        scene(s, sp["pack"], ix + iw / 2, H / 2 + cm(0.3), cm(12.5), sp.get("props", []), rot=4 if right else -4)
    else:
        picture(s, sp.get("image"), ix, 0, iw, H, name="!!image")
    tx = MX if right else iw + cm(2.2)
    tw = W - iw - cm(2.2) - MX
    logo(s, (W - MX - cm(1.9)) if not right else (MX), cm(1.25), cm(1.9))
    y = text_block(s, tx, cm(4.2), tw, dict(sp, subtitle=None), max_pt=44, min_pt=28)
    if sp.get("text"):
        ls = lines_for(sp["text"], 16, tw)
        txt(s, tx, y + cm(0.2), tw, len(ls) * 23 * 12700, ls, 16, color="muted", line=23)
        y += len(ls) * 23 * 12700 + cm(0.8)
    for b in sp.get("items", []):
        dot(s, tx + cm(0.15), y + cm(0.33), cm(0.26), "brand")
        txt(s, tx + cm(0.6), y, tw - cm(0.6), cm(0.8), b, 15, font="bold")
        y += cm(0.95)


def s_full_image(deck, sp):
    """Tylko grafika: zdjęcie na cały slajd + karta z podpisem w rogu (opcjonalnie)."""
    s = deck.slide("paper")
    picture(s, sp.get("image"), 0, 0, W, H, name="!!image")
    if sp.get("caption") or sp.get("title"):
        cw = cm(12)
        ls = lines_for(sp.get("caption", ""), 14, cw - cm(1.6)) if sp.get("caption") else []
        chh = cm(2.6) + len(ls) * 20 * 12700
        card(s, MX, H - MX - chh, cw, chh, "white")
        txt(s, MX + cm(0.8), H - MX - chh + cm(0.6), cw - cm(1.6), cm(1.2), sp.get("title", ""), 24, font="display")
        if ls:
            txt(s, MX + cm(0.8), H - MX - chh + cm(1.8), cw - cm(1.6), len(ls) * 20 * 12700, ls, 14, color="muted",
                line=20)


def s_gallery(deck, sp):
    """Galeria 2-6 zdjęć z podpisami (zdjęcia z eventów, półki, POS, social media)."""
    s = frame(deck, sp)
    items = sp["items"]
    n = len(items)
    cols = n if n <= 3 else math.ceil(n / 2)
    rows = math.ceil(n / cols)
    g = GAP
    cw = (W - 2 * MX - g * (cols - 1)) / cols
    cap = cm(1.0)
    ch = ((CB - CT) - (rows - 1) * g) / rows - cap
    for i, it in enumerate(items):
        c, r = i % cols, i // cols
        x, y = MX + c * (cw + g), CT + r * (ch + cap + g)
        picture(s, it.get("image"), x, y, cw, ch)
        txt(s, x, y + ch + cm(0.2), cw, cm(0.7), it.get("caption", ""), 13, color="muted", font="bold")


# --- produkt ----------------------------------------------------------------------------------------
def s_product_hero(deck, sp):
    """Anatomia produktu: paczka w centrum z drobnymi elementami, 4 claimy wokół (2 + 2)."""
    s = frame(deck, sp)
    colw = cm(7.8)
    left_r, right_l = MX + colw + cm(0.6), W - MX - colw - cm(0.6)
    img = sp.get("image")
    h = fit_trio(img, cm(11.0), right_l - left_r) if isinstance(img, (list, tuple)) else cm(11.6)
    scene(s, img, W / 2, cm(11.0), h, sp.get("props", []), rot=-3, prop_scale=0.85,
          avoid=[(0, 0, left_r, H), (right_l, 0, W, H), (0, 0, W, CT - cm(0.6))])
    pos = [(MX, cm(5.6)), (MX, cm(11.5)), (W - MX - colw, cm(5.6)), (W - MX - colw, cm(11.5))]
    for i, it in enumerate(sp["items"][:4]):
        x, y = pos[i]
        right = i >= 2
        al = "l" if right else "r"
        if it.get("icon"):  # ikona liniowa jak w sklepie, przy krawędzi zwróconej do produktu
            ix = x if right else x + colw - cm(1.3)
            s.shapes.add_picture(icon(it["icon"]), Emu(int(ix)), Emu(int(y)), Emu(int(cm(1.3))))
        size = title_size(it["title"], 34, 20, colw)
        ls = display_lines(it["title"], size, colw)
        txt(s, x, y + cm(1.45), colw, len(ls) * size * 12700, ls, size, font="display", align=al, line=size)
        txt(s, x, y + cm(1.6) + len(ls) * size * 12700, colw, cm(1.6), it.get("text", ""), 15, color="muted",
            align=al, line=21)


def s_flavor(deck, sp):
    """Karta smaku: nazwa, opis z karty wprowadzenia, 3 twarde dane, paczka z elementami smaku.
    Tło karty w odcieniu smaku (kolor stały - kolor smaku, nie motywu)."""
    s = deck.slide("paper")
    ix = cm(16.0)
    if T["tag"] == "price":  # sklep: kremowa karta z zaokragleniem zamiast pelnego tla
        card(s, ix, cm(1.2), W - ix - MX, H - cm(2.4), "card", name="!!image")
    else:
        rect(s, ix, 0, W - ix, H, sp.get("tint", "F5ECE3"), name="!!image")
    key = "pack_" + sp.get("key", "smak")
    scx = ix + (W - ix - (MX if T["tag"] == "price" else 0)) / 2
    scene(s, sp.get("image"), scx, cm(9.9), cm(12.4 if T["tag"] == "price" else 13.0), sp.get("props", []),
          rot=sp.get("rot", 4), key=key)
    logo(s, MX, cm(1.3), cm(1.9))
    y = cm(4.2)
    txt(s, MX, y, cm(12), cm(0.7), sp.get("kicker", "Smak"), 12, color=sp.get("deep", "accent"), font="bold",
        caps=True, spacing=200, name="!!kicker")
    y += cm(0.85)
    tw = ix - MX - cm(1.2)
    size = title_size(sp["name"], 84, 44, tw)
    ls = display_lines(sp["name"], size, tw)
    txt(s, MX, y, tw, len(ls) * size * 12700, ls, size, font="display", line=size * 0.96, name="!!title")
    y += len(ls) * size * 0.96 * 12700 + cm(0.5)
    if sp.get("text"):
        ls = lines_for(sp["text"], 17, tw)
        txt(s, MX, y, tw, len(ls) * 25 * 12700, ls, 17, color="muted", line=25)
        y += len(ls) * 25 * 12700 + cm(0.8)
    facts = sp.get("facts", [])[:3]
    g = cm(0.3)
    cw = (tw - g * 2) / 3
    for i, f in enumerate(facts):
        x = MX + i * (cw + g)
        card(s, x, y, cw, cm(3.0), "card")
        vs = fit(f["value"], 30, 18, cw - cm(0.9))
        txt(s, x + cm(0.45), y + cm(0.4), cw - cm(0.9), cm(1.3), f["value"], vs, color=sp.get("deep", "brand"),
            font="display")
        txt(s, x + cm(0.45), y + cm(1.7), cw - cm(0.9), cm(1.2), f["label"], 12, color="muted", line=16)
    if sp.get("ean"):
        txt(s, MX, H - cm(1.05), cm(12), cm(0.6), "EAN " + sp["ean"], 10.5, color="muted")
    txt(s, ix - cm(3.2), H - cm(1.05), cm(1.5), cm(0.6), "%02d" % deck.page, 10.5, color="muted", font="bold",
        align="r")


def s_line(deck, sp):
    """Linia produktów / portfolio: 2-4 SKU obok siebie (paczka, nazwa, gramatura, EAN)."""
    s = frame(deck, sp)
    items = sp["items"]
    n = len(items)
    g = GAP
    cw = (W - 2 * MX - g * (n - 1)) / n
    if T["tag"] == "price":
        return _line_shop(deck, s, items, cw, g)
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        card(s, x, CT, cw, (CB - CT), it.get("tint", "card"))
        scene(s, it.get("image"), x + cw / 2, cm(9.2), cm(7.2), it.get("props", [])[:3], rot=[-3, 2, 4, -2][i % 4],
              key="pack_" + it.get("key", str(i)), prop_scale=0.9)
        txt(s, x, cm(13.6), cw, cm(1.1), it["name"], fit(it["name"], 26, 16, cw - cm(1)), font="display", align="c")
        txt(s, x, cm(14.8), cw, cm(0.7), it.get("meta", ""), 13, color="muted", font="bold", align="c")
        if it.get("ean"):
            txt(s, x, cm(15.5), cw, cm(0.7), "EAN " + it["ean"], 12, color="muted", align="c")


def _line_shop(deck, s, items, cw, g):
    """Karty produktu 1:1 z listingu dobrakaloria.pl: biała karta z cienką ramką, packshot z elementami,
    znaczek NOWOŚĆ, nazwa w Lato, krótki opis, zielona metka ceny z gramaturą. Pozycje liczone od góry karty."""
    y0, ch = CT, CB - CT
    badges = any(it.get("badge") for it in items)
    tw = cw - cm(1.8)
    names = [it.get("title") or "%s - %s" % (it["name"], it.get("meta", "")) for it in items]
    nz = 15  # jeden rozmiar nazw w całym rzędzie; zmniejszamy, aż każda mieści się w jednej linii
    while nz > 12 and any(len(lines_for(nm, nz, tw, "bold")) > 1 for nm in names):
        nz -= 1
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        card(s, x, y0, cw, ch, "white", line="line", line_w=1)
        if badges:  # znaczek NOWOŚĆ tylko na życzenie (29.09 user go usunął) - wtedy mniejsza paczka
            scene(s, it.get("image"), x + cw / 2, y0 + cm(2.85), cm(4.4), it.get("props", [])[:3],
                  rot=[-3, 2, 4, -2][i % 4], key="pack_" + it.get("key", str(i)), prop_scale=0.85)
            if it.get("badge"):
                bw = pill_w(it["badge"], 11, spacing=60) + cm(0.4)
                tag(s, x + (cw - bw) / 2, y0 + cm(5.45), it["badge"], fill="brand", size=11, style="badge")
            ly = y0 + cm(6.6)
        else:
            scene(s, it.get("image"), x + cw / 2, y0 + cm(4.3), cm(6.2), it.get("props", [])[:3],
                  rot=[-3, 2, 4, -2][i % 4], key="pack_" + it.get("key", str(i)), prop_scale=0.8)
            ly = y0 + cm(8.9)
        rect(s, x + cm(0.9), ly, cw - cm(1.8), cm(0.03), "line")
        y = ly + cm(0.35)
        ls = lines_for(names[i], nz, tw, "bold")
        txt(s, x + cm(0.9), y, tw, len(ls) * (nz + 5) * 12700, ls, nz, font="bold", line=nz + 5)
        y += len(ls) * (nz + 5) * 12700 + cm(0.25)
        if it.get("text"):  # opis tylko gdy podany (29.09: bez opisu wygląda czyściej)
            ls = lines_for(it["text"], 13, tw)
            txt(s, x + cm(0.9), y, tw, len(ls) * 18 * 12700, ls, 13, color="muted", line=18)
        tag(s, x + cm(0.9), y0 + ch - cm(1.6), it.get("meta", "65 g"), fill="brand", size=15, h=cm(1.1), style="price")


def s_nutrition(deck, sp):
    """Packshot + tabela wartości odżywczych z karty wprowadzenia (100 g / opakowanie)."""
    s = frame(deck, sp)
    scene(s, sp.get("image"), cm(8.4), cm(11.0), cm(11.0), sp.get("props", [])[:4], rot=-4)
    x, w = cm(16.4), W - cm(16.4) - MX
    rows = sp["rows"]
    head = sp.get("head", ["Wartość odżywcza", "100 g", "opakowanie"])
    rh = min(cm(1.05), (H - cm(7.0)) / (len(rows) + 1))
    y = CT
    c1, c2 = x + w * 0.52, x + w * 0.76
    for j, row in enumerate([head] + rows):  # jak "Wartości odżywcze" w sklepie: pasy kremowe co drugi wiersz
        yy = y + j * rh
        if j % 2 == 1:
            rect(s, x, yy, w, rh, "card")
        f = "bold" if j == 0 else "body"
        txt(s, x + cm(0.6), yy, w * 0.5, rh, row[0], 13, font=f, anchor="m")
        txt(s, c1, yy, w * 0.22, rh, row[1], 13, font=f, anchor="m", align="r")
        txt(s, c2, yy, w * 0.24 - cm(0.6), rh, row[2], 13, font=f, anchor="m", align="r")
    if sp.get("note"):
        txt(s, x, y + rh * (len(rows) + 1) + cm(0.6), w, cm(1.2), sp["note"], 12, color="muted")


def s_tiles(deck, sp):
    """Zalety / claimy jako zielone kafle (jak sekcja 'Zalety naszych produktów' w sklepie)."""
    s = frame(deck, sp)
    items = sp["items"][:4]
    n = len(items)
    g = GAP
    cw = (W - 2 * MX - g * (n - 1)) / n
    y, ch = CT, (CB - CT)
    if not any(it.get("text") for it in items):  # same nagłówki (29.09 wersja usera): węższe kafle na środku
        g = cm(1.6)
        cw = min(cw, cm(6.8))
        x0 = (W - n * cw - (n - 1) * g) / 2
        for i, it in enumerate(items):
            x = x0 + i * (cw + g)
            card(s, x, y, cw, ch, "brand")
            if it.get("image"):
                ih = cm(3.4)
                iw = min(ih * img_ratio(it["image"]), cw - cm(1.8))
                place_image(s, it["image"], x + (cw - iw) / 2, y + cm(1.8), w=iw, rot=it.get("rot", 0))
            size = title_size(it["title"], 28, 18, cw - cm(1.0))
            ls = display_lines(it["title"], size, cw - cm(1.0))
            txt(s, x + cm(0.5), y + cm(7.4), cw - cm(1.0), ch - cm(8.2), ls, size, color="white", font="display",
                line=size, align="c", anchor="m")
        return
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        card(s, x, y, cw, ch, "brand")
        if it.get("image"):
            ih = cm(3.4)
            iw = ih * img_ratio(it["image"])
            place_image(s, it["image"], x + (cw - iw) / 2, y + cm(0.9), h=ih, rot=it.get("rot", 0))
        size = title_size(it["title"], 28, 18, cw - cm(1.8))
        ls = display_lines(it["title"], size, cw - cm(1.8))
        ty = y + ch - CT - (len(ls) - 1) * size * 12700
        txt(s, x + cm(0.9), ty, cw - cm(1.8), len(ls) * size * 12700, ls, size, color="white", font="display",
            line=size)
        txt(s, x + cm(0.9), y + ch - cm(3.2), cw - cm(1.8), cm(2.8), it.get("text", ""), 13, color="on_brand", line=18)


# --- dane --------------------------------------------------------------------------------------------
def s_hero_stat(deck, sp):
    """Liczba-bohater: jedna duża liczba + opis + 1-2 liczby pomocnicze; opcjonalnie produkt."""
    s = frame(deck, sp)
    if sp.get("image"):
        scene(s, sp["image"], W - cm(7.0), cm(10.6), cm(11.0), sp.get("props", [])[:4], rot=5)
    txt(s, MX - cm(0.15), cm(4.1), cm(17), cm(6.4), sp["value"], 150, color="brand", font="display")
    ls = lines_for(sp["label"], 22, cm(15))
    txt(s, MX, cm(9.7), cm(15), len(ls) * 30 * 12700, ls, 22, font="bold", line=30)
    cw, g = cm(7.2), GAP
    for i, it in enumerate(sp.get("items", [])[:2]):
        x = MX + i * (cw + g)
        card(s, x, cm(12.6), cw, cm(3.7), "card")
        txt(s, x + cm(0.6), cm(12.9), cw - cm(1.2), cm(1.9), it["value"], 40, font="display")
        txt(s, x + cm(0.6), cm(14.7), cw - cm(1.2), cm(1.4), it["label"], 13.5, color="muted", line=18)


def s_kpis(deck, sp):
    """3-4 wskaźniki obok siebie (KPI, wyniki sprzedaży, zasięgi)."""
    s = frame(deck, sp)
    items = sp["items"]
    n = len(items)
    g = GAP
    cw = (W - 2 * MX - g * (n - 1)) / n
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        hi = i == sp.get("highlight", -1)
        card(s, x, cm(5.2), cw, cm(9.0), "brand" if hi else "card")
        vs = fit(it["value"], 72, 28, cw - cm(2.4))
        txt(s, x + cm(1.1), cm(6.0), cw - cm(2.2), cm(3), it["value"], vs, color="white" if hi else "brand",
            font="display")
        lw = cw - cm(2.2)
        lz = 17
        while lz > 13 and len(lines_for(it["label"], lz, lw, "bold")) > 2:  # etykieta max 2 linie (29.09)
            lz -= 1
        ll = lines_for(it["label"], lz, lw, "bold")
        lh = len(ll) * (lz + 4) * 12700
        txt(s, x + cm(1.1), cm(9.4), lw, lh, ll, lz, color="white" if hi else "ink", font="bold", line=lz + 4)
        if it.get("note"):
            ny = cm(9.4) + lh + cm(0.25)
            nh = cm(14.2) - ny - cm(0.3)
            nz = 13  # opis zmniejszamy do 11 pt, aż zmieści się w karcie (30.09: po większych marginesach wychodził +19 pt)
            while nz > 11 and len(lines_for(it["note"], nz, lw)) * (nz + 5) * 12700 > nh:
                nz -= 1
            txt(s, x + cm(1.1), ny, lw, nh, lines_for(it["note"], nz, lw), nz, color="on_brand" if hi else "muted",
                line=nz + 5)


def s_bars(deck, sp):
    """Poziomy wykres słupkowy: etykieta nad słupkiem, wartość na końcu, bez osi (czytelny z daleka)."""
    s = frame(deck, sp)
    items, hi = sp["items"], set(sp.get("highlight", [0]))
    has_note = bool(sp.get("insight"))
    bw = cm(17.5) if has_note else W - 2 * MX - cm(3.5)
    row = min(cm(2.25), (cm(16.4) - CT) / len(items))
    vmax = sp.get("max", 100)
    for i, it in enumerate(items):
        y = CT + i * row
        on = i in hi
        txt(s, MX, y, bw, cm(0.8), it["label"], 15, color="ink" if on else "muted", font="bold")
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, MX, y + cm(0.85), bw, cm(0.6), "card", radius=0.5)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, MX, y + cm(0.85), max(cm(0.6), bw * it["value"] / vmax), cm(0.6),
              "brand" if on else "tan", radius=0.5)  # 29.09: bez miętowego spoza palety
        txt(s, MX + bw + cm(0.5), y + cm(0.3), cm(3), cm(1.4), it.get("text", "%d%%" % round(it["value"])),
            26 if on else 22, font="display", anchor="m")
    if has_note:
        x = cm(23.4)
        card(s, x, CT, W - MX - x, cm(11.3), "card")
        txt(s, x + cm(0.8), cm(5.7), W - MX - x - cm(1.6), cm(9.6), sp["insight"], 17, font="bold", line=25)


def s_segments(deck, sp):
    """Dwie grupy (segmenty, kanały, regiony) obok siebie; w każdej 2-4 wyniki."""
    s = frame(deck, sp)
    groups = sp["groups"]
    g = GAP
    cw = (W - 2 * MX - g * (len(groups) - 1)) / len(groups)
    y, ch = CT, (CB - CT)
    for i, gr in enumerate(groups):
        x = MX + i * (cw + g)
        card(s, x, y, cw, ch, "white" if i == 0 else "card", line="line" if i == 0 else None, line_w=1)
        txt(s, x + cm(1.2), y + cm(0.7), cw - cm(2.4), cm(1), gr["name"], 24, font="display")
        txt(s, x + cm(1.2), y + cm(1.85), cw - cm(2.4), cm(1.6), gr["desc"], 13, color="muted", line=18)
        ms = gr["metrics"]
        my0 = y + cm(3.8)
        rh = (y + ch - cm(0.4) - my0) / len(ms)
        for j, m in enumerate(ms):
            my = my0 + j * rh
            rect(s, x + cm(1.2), my, cw - cm(2.4), cm(0.03), "line")
            txt(s, x + cm(1.2), my, cm(4.9), rh, m["value"], 50, color="brand" if i == 0 else "ink", font="display",
                anchor="m")
            txt(s, x + cm(6.2), my, cw - cm(7.4), rh, m["label"], 15, font="bold", line=20, anchor="m")


def s_table(deck, sp):
    """Tabela (asortyment, cennik, logistyka): nagłówek w kolorze marki, liczby do prawej."""
    s = frame(deck, sp)
    head, rows = sp["head"], sp["rows"]
    widths = sp.get("widths") or [1] * len(head)
    tot = sum(widths)
    tw = W - 2 * MX
    xs = [MX]
    for wd in widths:
        xs.append(xs[-1] + tw * wd / tot)
    rh = min(cm(1.3), (H - cm(7)) / (len(rows) + 1))
    y = CT
    num = [all(re.match(r"^[\d\s,.%zł-]+$", str(r[c])) for r in rows) for c in range(len(head))]
    for c, hd in enumerate(head):  # nagłówek bez tła, pogrubiony (jak tabela wartości w sklepie)
        txt(s, xs[c] + cm(0.5), y, xs[c + 1] - xs[c] - cm(1), rh, hd, 13, font="bold", anchor="m",
            align="r" if num[c] else "l")
    for r, row in enumerate(rows):
        yy = y + rh * (r + 1)
        if r % 2 == 0:
            rect(s, MX, yy, tw, rh, "card")
        for c, val in enumerate(row):
            txt(s, xs[c] + cm(0.5), yy, xs[c + 1] - xs[c] - cm(1), rh, str(val), 13, anchor="m",
                font="bold" if c == 0 else "body", align="r" if num[c] else "l")


def s_timeline(deck, sp):
    """Oś czasu (wprowadzenie produktu, plan kampanii): 3-6 punktów na linii."""
    s = frame(deck, sp)
    items = sp["items"]
    n = len(items)
    y = cm(10.6)  # os czasu w optycznym srodku obszaru tresci
    x0, x1 = MX + cm(1), W - MX - cm(1)
    rect(s, x0, y - cm(0.04), x1 - x0, cm(0.08), "line")
    step = (x1 - x0) / (n - 1) if n > 1 else 0
    cw = min(cm(6.5), step * 0.92) if n > 1 else cm(8)
    for i, it in enumerate(items):
        cx = x0 + i * step
        now = i == sp.get("current", -1)
        dot(s, cx, y, cm(0.9), "brand" if now else "white")
        shape(s, MSO_SHAPE.OVAL, cx - cm(0.45), y - cm(0.45), cm(0.9), cm(0.9), None, line="brand", line_w=2)
        top = i % 2 == 0
        ty = y - cm(3.4) if top else y + cm(1.0)
        lx = min(max(cx - cw / 2, MX), W - MX - cw)  # etykieta nie wychodzi poza marginesy
        al = "l" if lx == MX else ("r" if lx == W - MX - cw else "c")
        txt(s, lx, ty, cw, cm(0.8), it["date"], 16, color="brand", font="bold", align=al)
        txt(s, lx, ty + cm(0.8), cw, cm(0.9), it["title"], 18, font="display", align=al)
        txt(s, lx, ty + cm(1.7), cw, cm(1.8), it.get("text", ""), 12.5, color="muted", align=al, line=17)


def s_split(deck, sp):
    """A vs B jednym paskiem (np. udział, preferencja nazwy) + opis obu stron."""
    s = frame(deck, sp)
    a, b = sp["a"], sp["b"]
    x0, x1 = MX, W - MX
    txt(s, x0, CT - cm(0.3), cm(14), cm(4.8), a["value"], 110, color="brand", font="display")
    txt(s, x1 - cm(10), cm(6.3), cm(10), cm(2.8), b["value"], 64, color="tan", font="display", align="r")
    by = cm(9.6)
    frac = a.get("share") or float(str(a["value"]).rstrip("%").replace(",", ".")) / 100
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, by, x1 - x0, cm(0.9), "sage", radius=0.5)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, by, (x1 - x0) * frac, cm(0.9), "brand", radius=0.5)
    txt(s, x0, by + cm(1.3), cm(14), cm(1), a["label"], 18, font="bold")
    txt(s, x1 - cm(14), by + cm(1.3), cm(14), cm(1), b["label"], 18, color="muted", font="bold", align="r")
    if sp.get("note"):
        txt(s, x0, cm(13.4), cm(26), cm(2.5), sp["note"], 16, color="muted", line=23)


# --- handel -------------------------------------------------------------------------------------------
def s_reasons(deck, sp):
    """Argumenty dla handlu (3-4): liczba/hasło + tytuł + opis; pierwsza karta w kolorze marki."""
    s = frame(deck, sp)
    items = sp["items"]
    n = len(items)
    g = GAP
    cw = (W - 2 * MX - g * (n - 1)) / n
    y, ch = CT, cm(11.4)
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        hi = i == 0
        card(s, x, y, cw, ch, "brand" if hi else "card")
        txt(s, x + cm(0.8), y + cm(0.8), cw, cm(0.7), "%02d" % (i + 1), 13, color="on_brand" if hi else "muted",
            font="bold", spacing=100)
        vs = fit(it["value"], 54, 26, cw - cm(1.6))
        txt(s, x + cm(0.8), y + cm(2.8), cw - cm(1.6), cm(2.4), it["value"], vs, color="white" if hi else "brand",
            font="display")
        txt(s, x + cm(0.8), y + cm(5.4), cw - cm(1.6), cm(1.6), it["title"], 16, color="white" if hi else "ink",
            font="bold", line=21)
        txt(s, x + cm(0.8), y + cm(7.3), cw - cm(1.6), cm(3.8), it["text"], 13, color="on_brand" if hi else "muted",
            line=18)


def s_facts(deck, sp):
    """Siatka faktów (logistyka: karton, paleta, termin, przechowywanie...) - 4-8 kart wartość + etykieta."""
    s = frame(deck, sp)
    items = sp["items"]
    cols = 4 if len(items) > 3 else len(items)
    rows = math.ceil(len(items) / cols)
    g = GAP
    cw = (W - 2 * MX - g * (cols - 1)) / cols
    ch = min(CT, ((CB - CT) - g * (rows - 1)) / rows)
    for i, it in enumerate(items):
        c, r = i % cols, i // cols
        x, y = MX + c * (cw + g), CT + r * (ch + g)
        card(s, x, y, cw, ch, "card")
        txt(s, x + cm(0.9), y + cm(0.8), cw - cm(1.8), cm(0.7), it["label"], 12, color="muted", font="bold",
            caps=True, spacing=100)
        vs = fit(it["value"], 32, 16, cw - cm(1.8))
        txt(s, x + cm(0.9), y + cm(1.7), cw - cm(1.8), ch - cm(2.4), it["value"], vs, font="display")


def s_cards_images(deck, sp):
    """Karty ze zdjęciem (wsparcie marketingowe, materiały POS, kanały): zdjęcie, tytuł, opis."""
    s = frame(deck, sp)
    items = sp["items"]
    n = len(items)
    g = GAP
    cw = (W - 2 * MX - g * (n - 1)) / n
    y = CT
    ih = cm(5.6)
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        card(s, x, y, cw, (CB - CT), "card")
        picture(s, it.get("image"), x, y, cw, ih, name="tlo-zdjecie")
        if it.get("badge"):
            tag(s, x + cm(0.5), y + cm(0.5), it["badge"], fill="brand", style="badge")  # 29.09: jeden kolor
        txt(s, x + cm(1.1), y + ih + cm(0.6), cw - cm(2.2), cm(1.2), it["title"], 22, font="display")
        txt(s, x + cm(1.1), y + ih + cm(1.8), cw - cm(2.2), cm(3.2), it.get("text", ""), 13, color="muted", line=18)


def s_contact(deck, sp):
    """Osoba kontaktowa: zdjęcie w kole, imię, rola, telefon, e-mail."""
    s = frame(deck, sp)
    d = cm(8.5)
    x, y = MX + cm(1), cm(5.2)
    photo = sp.get("image") or placeholder(1.0, "ZDJĘCIE")
    pic = s.shapes.add_picture(photo, Emu(int(x)), Emu(int(y)), Emu(int(d)), Emu(int(d)))
    pic.auto_shape_type = MSO_SHAPE.OVAL
    tx = x + d + cm(1.6)
    txt(s, tx, cm(6.0), cm(18), cm(1.8), sp["name"], 44, font="display")
    txt(s, tx, cm(8.0), cm(18), cm(0.9), sp.get("role", ""), 18, color="muted", font="bold")
    yy = cm(9.8)
    for label, val in sp.get("lines", []):
        txt(s, tx, yy, cm(4), cm(0.8), label, 12, color="muted", font="bold", caps=True, spacing=100)
        txt(s, tx + cm(3.6), yy - cm(0.1), cm(14), cm(0.9), val, 18)
        yy += cm(1.1)


def s_end(deck, sp):
    """Zakończenie: variant brand (zieleń, logo, #zawszedobra) albo light (dziękujemy + kontakt).
    valign "m" (konwersja): blok logo + hasztag (+ kontakt) wyśrodkowany w pionie; bez niego pozycje jak w szablonie."""
    if sp.get("variant", "brand") == "brand":
        s = deck.slide("brand")
        lw = cm(8.2)
        y0 = cm(4.2)
        if sp.get("valign") == "m":  # konwersja: blok logo + hasztag (+ kontakt) wysrodkowany w pionie (09.10)
            blok = cm(6.8) + cm(1.8) + (cm(2.2) if sp.get("contact") else 0)  # logo 6.0 + odstep 0.8; hasztag 1.8
            y0 = (H - blok) / 2
        logo(s, (W - lw) / 2, y0, lw, "white_box", "!!logo")
        txt(s, 0, y0 + cm(6.8), W, cm(1.8), sp.get("hashtag", "#zawszedobra"), 40, color="white", font="display", align="c")
        if sp.get("contact"):
            txt(s, 0, y0 + cm(9.0), W, cm(1), sp["contact"], 15, color="on_brand", align="c")
    else:
        s = deck.slide("paper")
        rect(s, 0, H - cm(5.2), W, cm(5.2), "brand", name="!!panel")
        txt(s, MX, cm(3.2), cm(24), cm(4.4), sp.get("title", "Dziękujemy"), 96, font="display", name="!!title")
        if sp.get("subtitle"):
            txt(s, MX, cm(7.4), cm(22), cm(2.5), sp["subtitle"], 20, color="muted", line=28)
        logo(s, MX, H - cm(4.0), cm(3.8), "white_box", "!!logo")
        if sp.get("contact"):
            txt(s, cm(8.2), H - cm(3.5), W - cm(10), cm(2), sp["contact"], 16, color="white", line=24, anchor="m")


def s_instructions(deck, sp):
    """Slajd-instrukcja szablonu (ukryty w pokazie)."""
    s = frame(deck, sp)
    cw = (W - 2 * MX - cm(1.0)) / 2
    for i, col in enumerate(sp["columns"][:2]):
        x = MX + i * (cw + cm(1.0))
        card(s, x, CT, cw, (CB - CT), "card")
        y = cm(5.4)
        for head, body in col:
            txt(s, x + cm(0.8), y, cw - cm(1.6), cm(0.8), head, 15, font="bold")
            ls = lines_for(body, 12.5, cw - cm(1.6))
            txt(s, x + cm(0.8), y + cm(0.75), cw - cm(1.6), len(ls) * 17 * 12700, ls, 12.5, color="muted", line=17)
            y += cm(0.9) + len(ls) * 17 * 12700 + cm(0.35)



def icon(name, on_dark=False):
    """Ikona liniowa (Lucide) w kolorze marki bieżącego motywu. Brak pliku -> scripts/make_icons.py."""
    color = "FFFFFF" if on_dark else T["brand"]
    return os.path.join(A, "icons", color, name + ".png")


def round_picture(pic, r):
    """Zaokrąglone rogi zdjęcia LUB filmu (jak karty w sklepie): geometria roundRect na samym obiekcie, promień r
    (EMU). Sprawdzone w PowerPoint 29.09: "Zmień obraz" zachowuje kształt, a Malarz formatów przenosi go z obrazu
    albo filmu na nowo wstawiony film (z kształtu-autokształtu NIE)."""
    geom = pic._element.spPr.find(qn("a:prstGeom"))
    if geom is None:
        geom = etree.SubElement(pic._element.spPr, qn("a:prstGeom"))
    geom.set("prst", "roundRect")
    for g in list(geom):
        geom.remove(g)
    av = etree.SubElement(geom, qn("a:avLst"))
    gd = etree.SubElement(av, qn("a:gd"))
    gd.set("name", "adj")
    gd.set("fmla", "val %d" % int(min(50000, r / min(pic.width, pic.height) * 100000)))
    return pic


def s_icon_list(deck, sp):
    """Lista zalet z ikonami (jak 'Lecimy w kulki!' w sklepie): zdjęcie/produkt w zaokrąglonej karcie po lewej,
    tytuł + 3-4 pozycje (ikona, pogrubiony tytuł, opis) po prawej, opcjonalny żółty przycisk."""
    s = deck.slide("paper")
    cw = W * 0.44
    x0, y0, ch = MX, cm(1.6), H - cm(3.2)
    if sp.get("pack"):
        card(s, x0, y0, cw, ch, sp.get("card_fill", "card"), name="!!image")
        pk = sp["pack"]
        h = fit_trio(pk, cm(10.5), cw - cm(1.2)) if isinstance(pk, (list, tuple)) else cm(11.5)
        scene(s, pk, x0 + cw / 2, y0 + ch / 2 + cm(0.3), h, sp.get("props", []), rot=-4,
              key=sp.get("key", "pack"), avoid=[(x0 + cw + cm(0.3), 0, W, H)])
    else:
        pic = picture(s, sp.get("image"), x0, y0, cw, ch, name="!!image")
        round_picture(pic, cm(0.45))
    tx = x0 + cw + cm(2.2)
    tw = W - tx - MX
    items = sp["items"][:4]
    size = title_size(sp["title"], 44, 28, tw)
    ls = display_lines(sp["title"], size, tw)
    step = cm(3.0)
    block = len(ls) * size * 12700 + cm(1.0) + len(items) * step + (cm(1.8) if sp.get("button") else 0)
    y = max(cm(1.8), (H - block) / 2)
    if sp.get("kicker"):
        kicker(s, tx, y - cm(1.0), sp["kicker"])
    txt(s, tx, y, tw, len(ls) * size * 12700, ls, size, font="display", line=size, name="!!title")
    y += len(ls) * size * 12700 + cm(1.0)
    for it in items:
        s.shapes.add_picture(icon(it.get("icon", "sparkles")), Emu(int(tx)), Emu(int(y)), Emu(int(cm(1.3))))
        txt(s, tx + cm(2.0), y - cm(0.05), tw - cm(2.0), cm(0.9), it["title"], 19, font="bold")
        txt(s, tx + cm(2.0), y + cm(0.9), tw - cm(2.0), cm(1.9), it.get("text", ""), 15, color="muted", line=21)
        y += step
    if sp.get("button"):
        tag(s, tx + cm(1.75), y + cm(0.1), sp["button"], fill="sun", fg="3B2A20", size=12, h=cm(1.0), style="button")


def s_icon_grid(deck, sp):
    """Siatka ikon (jak 'Skład produktu' w sklepie): ikona, zielony nagłówek Mindset, krótki opis. 3-6 pozycji."""
    s = frame(deck, sp)
    items = sp["items"][:6]
    cols = 3 if len(items) in (3, 5, 6) else 2
    rows = (len(items) + cols - 1) // cols
    has_img = bool(sp.get("pack"))
    area_w = (W * 0.6 - MX) if has_img else (W - 2 * MX)
    cw = (area_w - GAP * (cols - 1)) / cols
    ic = cm(1.7)
    size = min(title_size(it["title"], 26, 16, cw - cm(0.6)) for it in items)  # jeden rozmiar dla całej siatki
    tl = max(len(display_lines(it["title"], size, cw - cm(0.6))) for it in items)
    dl = max(len(lines_for(it.get("text", ""), 16, cw - cm(0.6))) for it in items)  # linie opisu (max)
    row_h = ic + cm(0.5) + tl * size * 12700 + cm(0.25) + dl * 22 * 12700  # ikona + nagłówek + opis
    gap_r = cm(0.8)
    y0 = CT + max(0, (CB - CT - rows * row_h - (rows - 1) * gap_r) / 2)
    for i, it in enumerate(items):
        c, r = i % cols, i // cols
        x, y = MX + c * (cw + GAP), y0 + r * (row_h + gap_r)
        s.shapes.add_picture(icon(it.get("icon", "leaf")), Emu(int(x)), Emu(int(y)), Emu(int(ic)))
        ls = display_lines(it["title"], size, cw - cm(0.6))
        ty = y + ic + cm(0.5)
        txt(s, x, ty, cw - cm(0.6), len(ls) * size * 12700, ls, size, color="brand", font="display", line=size)
        txt(s, x, ty + tl * size * 12700 + cm(0.25), cw - cm(0.6), dl * 22 * 12700, it.get("text", ""), 16,
            color="muted", line=22)
    if has_img:
        cx = W * 0.6 + (W * 0.4 - MX) / 2 + cm(0.6)
        scene(s, sp["pack"], cx, (CT + CB) / 2, cm(10.5), sp.get("props", []), rot=4, key=sp.get("key", "pack"))


# =============================================================================
# Nowe układy (28.09.2026): film, przed/po, wykresy edytowalne, cena, porównanie, okazje, social, kroki
# =============================================================================
def white_icon(name):
    return os.path.join(A, "icons", "FFFFFF", name + ".png")


RADIUS = cm(0.45)  # promień rogów kart, zdjęć i filmów (jak w sklepie)
VIDEO_NAME = "Film - podmiana: wstaw nowy film, kliknij TEN obiekt > Malarz formatów > kliknij nowy film"


def video_frame_png(ratio, full=False):
    """Ramka-miejsce na film: ciemny kadr 16:9 z zielonym kołem i trójkątem play (PNG, żeby dało się
    'Zmień obraz' i przenieść zaokrąglenie Malarzem formatów na wstawiony film)."""
    w = 1600
    h = int(w / ratio)
    fn = os.path.join(PH_DIR, "film_%d%s.png" % (int(ratio * 1000), "_full" if full else ""))
    if os.path.exists(fn):
        return fn
    ink = tuple(int(hexof("ink")[i:i + 2], 16) for i in (0, 2, 4))
    brand = tuple(int(hexof("brand")[i:i + 2], 16) for i in (0, 2, 4))
    im = Image.new("RGB", (w, h), tuple(min(255, c + 22) for c in ink))
    d = ImageDraw.Draw(im)
    r = int(min(w, h) * 0.11)
    cx, cy = w // 2, h // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=brand)
    t = r * 0.46
    d.polygon([(cx - t * 0.7, cy - t), (cx - t * 0.7, cy + t), (cx + t * 1.05, cy)], fill=(255, 255, 255))
    im.save(fn)
    return fn


def video_box(s, x, y, w, h, sp, name=None, r=RADIUS):
    """Film w zaokrąglonej ramce (29.09: user chce ładne rogi i łatwą podmianę). Trzy tryby:
    video (mp4)  -> film osadzony, rogi na samym filmie (roundRect), klatka tytułowa = poster
    link (URL)   -> czysta miniatura YouTube + przycisk play + podpis "Kliknij - film otworzy się na YouTube",
                    wszystko z hiperłączem. Wideo online w PowerPoint NIE działa (błąd 153 YouTube, 29.09)
    nic          -> zaokrąglony obraz-ramka z przyciskiem play; na nim Malarz formatów przenosi rogi na film"""
    if sp.get("video"):
        poster = sp.get("poster") or video_frame_png(w / h)
        mv = s.shapes.add_movie(sp["video"], Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)),
                                poster_frame_image=poster, mime_type="video/mp4")
        mv.name = name or VIDEO_NAME
        return round_picture(mv, r)
    if sp.get("link"):  # 29.09: YouTube w PowerPoint = błąd 153 -> miniatura + play + podpis, klik otwiera YouTube
        poster = sp.get("poster") or bd.yt_thumb(sp["link"], PH_DIR) or video_frame_png(w / h)
        pic = picture(s, poster, x, y, w, h, name="Film YouTube (link) - prawy klik: Edytuj link / Zmień obraz")
        pic.click_action.hyperlink.address = sp["link"]
        if r:
            round_picture(pic, r)
        bd.link_overlay(s, x, y, w, h, sp["link"], green=T["brand"])
        return pic
    pic = picture(s, video_frame_png(w / h, full=r == 0), x, y, w, h, name=name or VIDEO_NAME)
    return round_picture(pic, r) if r else pic


def s_video(deck, sp):
    """Film. variant full: film na cały slajd (+ opcjonalny podpis w karcie); variant text: tekst + film 16:9."""
    if sp.get("variant", "full") == "full":
        s = deck.slide("ink")
        video_box(s, 0, 0, W, H, sp, r=0)
        if sp.get("title"):
            cw = cm(12)
            card(s, MX, H - MX - cm(2.6), cw, cm(2.6), "white")
            txt(s, MX + cm(0.8), H - MX - cm(2.1), cw - cm(1.6), cm(1.2), sp["title"], 22, font="display")
            txt(s, MX + cm(0.8), H - MX - cm(1.0), cw - cm(1.6), cm(0.7), sp.get("caption", ""), 13, color="muted")
        return
    s = frame(deck, dict(sp, title=None, kicker=None))
    vw = W * 0.54
    vh = vw * 9 / 16
    vx = W - MX - vw
    vy = (H - vh) / 2 + cm(0.4)
    video_box(s, vx, vy, vw, vh, sp)
    tw = vx - MX - cm(1.6)
    y = text_block(s, MX, vy, tw, dict(sp, subtitle=None), max_pt=40, min_pt=26)
    if sp.get("text"):
        ls = lines_for(sp["text"], 16, tw)
        txt(s, MX, y, tw, len(ls) * 23 * 12700, ls, 16, color="muted", line=23)
        y += len(ls) * 23 * 12700 + cm(0.6)
    for b in sp.get("items", []):
        dot(s, MX + cm(0.15), y + cm(0.33), cm(0.26), "brand")
        txt(s, MX + cm(0.6), y, tw - cm(0.6), cm(0.8), b, 15, font="bold")
        y += cm(0.95)


def s_media(deck, sp):
    """Claim + film (29.09, slajd 'Co dobrego w kreatynie' z wersji usera). Lewa karta: element produktu,
    zielony nagłówek, opis w beżu - wyśrodkowane. Prawa kremowa karta: tytuł filmu (beżowy Mindset) i film
    w zaokrąglonej ramce (video mp4 / link YouTube z miniaturą / ramka do podmiany)."""
    s = frame(deck, sp)
    y0, ch = cm(4.6), CB - cm(4.6)
    lw = (W - 2 * MX - GAP) * 0.41
    rx, rw = MX + lw + GAP, W - 2 * MX - lw - GAP
    card(s, MX, y0, lw, ch, "white", line="line", line_w=1)
    card(s, rx, y0, rw, ch, "card")
    pad = cm(1.0)
    iw = lw - 2 * pad
    ch_title = sp.get("claim_title", "")
    tsz = title_size(ch_title, 30, 20, iw) if ch_title else 0
    tls = display_lines(ch_title, tsz, iw) if ch_title else []
    bls = lines_for(sp.get("text", ""), 15, iw) if sp.get("text") else []
    ih = cm(3.6) if sp.get("claim_image") else 0
    block = ih + (cm(0.8) if ih else 0) + len(tls) * tsz * 12700 + (cm(0.6) if bls else 0) + len(bls) * 21 * 12700
    y = y0 + max(pad, (ch - block) / 2)
    if ih:
        w_img = min(ih * img_ratio(sp["claim_image"]), iw)
        place_image(s, sp["claim_image"], MX + (lw - w_img) / 2, y, w=w_img)
        y += ih + cm(0.8)
    if tls:
        txt(s, MX + pad, y, iw, len(tls) * tsz * 12700, tls, tsz, color="brand", font="display", line=tsz, align="c")
        y += len(tls) * tsz * 12700 + cm(0.6)
    if bls:
        txt(s, MX + pad, y, iw, len(bls) * 21 * 12700, bls, 15, color="muted", line=21, align="c")
    vw = rw - 2 * pad
    vy = y0 + pad
    if sp.get("media_title"):
        msz = 20
        mls = display_lines(sp["media_title"], msz, vw)
        txt(s, rx + pad, vy, vw, len(mls) * msz * 1.05 * 12700, mls, msz, color="tan", font="display",
            line=msz * 1.05)
        vy += len(mls) * msz * 1.05 * 12700 + cm(0.6)
    vh = min(vw * 9 / 16, y0 + ch - pad - vy)
    vw2 = vh * 16 / 9
    video_box(s, rx + pad + (vw - vw2) / 2, vy, vw2, vh, sp)


def s_article(deck, sp):
    """Akapit edukacyjny w kremowej karcie (29.09, 'Dlaczego warto dbać o błonnik'): tytuł-pytanie, 1-3 akapity
    w beżu, wyjustowane; drobne owoce przy lewej i prawej krawędzi karty (nie na tekście)."""
    s = frame(deck, sp)
    cx0, cw = MX + cm(0.6), W - 2 * MX - cm(1.2)
    tx0, tw = cx0 + cm(3.2), cw - cm(6.4)
    paras = sp.get("paragraphs") or [sp.get("text", "")]
    size = 16
    while True:
        lh = size * 1.45
        blocks = [lines_for(p, size, tw) for p in paras]
        th = sum(len(b) for b in blocks) * lh * 12700 + (len(blocks) - 1) * cm(0.5)
        if th <= CB - CT - cm(2.4) or size <= 13:
            break
        size -= 1
    chh = max(th + cm(2.6), cm(8.0))
    cy0 = CT + (CB - CT - chh) / 2 + cm(0.3)
    card(s, cx0, cy0, cw, chh, "card", name="karta-tekst")
    tb = s.shapes.add_textbox(Emu(int(tx0)), Emu(int(cy0 + (chh - th) / 2)), Emu(int(tw)), Emu(int(th)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, ptxt in enumerate(paras):  # jeden akapit = jeden paragraf (PowerPoint sam łamie przy justowaniu)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.JUSTIFY
        p.line_spacing = Pt(size * 1.45)
        if i:
            p.space_before = Pt(14)
        r = p.add_run()
        r.text = bd.typo_nbsp(ptxt)  # akapit wyjustowany łamie PowerPoint - twarde spacje pilnują typografii
        r.font.size = Pt(size)
        r.font.name = FONT_REF["body"][0]
        paint(r.font.color, "muted")
    tb.name = "Tekst - wpisz akapit"
    props = sp.get("props", [])[:4]
    slots = [(cx0 - cm(1.2), cy0 - cm(1.0), cm(3.4), -12), (cx0 - cm(0.6), cy0 + chh - cm(2.6), cm(2.8), 10),
             (cx0 + cw - cm(2.4), cy0 - cm(1.2), cm(3.2), 14), (cx0 + cw - cm(2.2), cy0 + chh - cm(2.8), cm(3.4), -8)]
    for p, (px, py, ph, rot) in zip(props, slots):
        place_image(s, p, px, py, h=ph, rot=rot)


def s_before_after(deck, sp):
    """Przed / po (półka, ekspozycja, opakowanie): dwa zdjęcia obok siebie ze znaczkami i podpisami."""
    s = frame(deck, sp)
    cw = (W - 2 * MX - GAP) / 2
    ih = CB - CT - cm(1.6)
    for i, side in enumerate(sp["items"][:2]):
        x = MX + i * (cw + GAP)
        pic = picture(s, side.get("image"), x, CT, cw, ih, name="tlo-zdjecie")
        round_picture(pic, cm(0.45))
        tag(s, x + cm(0.6), CT + cm(0.6), side.get("badge", ["Przed", "Po"][i]),
            fill="brand" if i else "ink", size=12, h=cm(0.95), style="badge")
        txt(s, x, CT + ih + cm(0.35), cw, cm(1.1), side.get("caption", ""), 15, color="muted")


def _chart_fonts(chart, size=12):
    chart.font.size = Pt(size)
    chart.font.name = "Lato"
    paint(chart.font.color, "muted")


def s_donut(deck, sp):
    """Udział / struktura (2-4 części): edytowalny wykres pierścieniowy (prawy klik > Edytuj dane),
    liczba-bohater w środku, legenda z opisami obok."""
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    s = frame(deck, sp)
    items = sp["items"]
    cd = CategoryChartData()
    cd.categories = [it["label"] for it in items]
    cd.add_series("Udział", [it["value"] for it in items])
    d = CB - CT
    x = MX
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Emu(int(x)), Emu(int(CT)), Emu(int(d)), Emu(int(d)), cd)
    gf.name = "tlo-wykres"
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = False
    _chart_fonts(ch)
    plot = ch.plots[0]
    plot._element.find(qn("c:holeSize")).set("val", "68") if plot._element.find(qn("c:holeSize")) is not None else None
    tokens = ["brand", "tan", "muted", "line"]  # 29.09: 3. kolor był niewidoczny (sage na bieli)
    for i, pt in enumerate(plot.series[0].points):
        pt.format.fill.solid()
        paint(pt.format.fill.fore_color, tokens[i % len(tokens)])
        pt.format.line.fill.background()
    txt(s, x, CT + d / 2 - cm(1.6), d, cm(2.4), sp.get("center", items[0].get("text", "")), 54, color="brand",
        font="display", align="c", anchor="m")
    txt(s, x, CT + d / 2 + cm(0.8), d, cm(0.8), sp.get("center_label", ""), 13, color="muted", align="c")
    lx = x + d + cm(2)
    lw = W - MX - lx
    rh = min(cm(2.6), (CB - CT) / len(items))
    y0 = CT + ((CB - CT) - rh * len(items)) / 2
    for i, it in enumerate(items):
        y = y0 + i * rh
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, lx, y + cm(0.2), cm(0.6), cm(0.6), tokens[i % len(tokens)], radius=0.3)
        txt(s, lx + cm(1.0), y, lw - cm(1.0), cm(1.0), "%s  ·  %s" % (it.get("text", ""), it["label"]), 18,
            font="bold")
        txt(s, lx + cm(1.0), y + cm(0.95), lw - cm(1.0), rh - cm(1.0), it.get("note", ""), 14, color="muted",
            line=19)
    if not sp.get("source") and deck.footer == "":
        pass


def s_columns(deck, sp):
    """Trend w czasie (sprzedaż, dystrybucja): edytowalny wykres kolumnowy + karta wniosku."""
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
    s = frame(deck, sp)
    cd = CategoryChartData()
    cd.categories = sp["categories"]
    for ser in sp["series"]:
        cd.add_series(ser["name"], ser["values"])
    has_note = bool(sp.get("insight"))
    cw = (W - 2 * MX - cm(7.6)) if has_note else (W - 2 * MX)
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Emu(int(MX)), Emu(int(CT)), Emu(int(cw)),
                            Emu(int(CB - CT)), cd)
    gf.name = "tlo-wykres"
    ch = gf.chart
    ch.has_title = False
    _chart_fonts(ch, 13)
    ch.has_legend = len(sp["series"]) > 1
    if ch.has_legend:
        from pptx.enum.chart import XL_LEGEND_POSITION
        ch.legend.position = XL_LEGEND_POSITION.TOP
        ch.legend.include_in_layout = False
    va = ch.value_axis
    va.visible = False
    va.has_major_gridlines = False
    ca = ch.category_axis
    ca.format.line.fill.background()
    ca.tick_labels.font.size = Pt(13)
    plot = ch.plots[0]
    plot.gap_width = 60
    plot.overlap = -10
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.font.size = Pt(14)
    dl.font.bold = True
    dl.number_format = sp.get("number_format", "0")
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    for i, ser in enumerate(plot.series):
        ser.format.fill.solid()
        paint(ser.format.fill.fore_color, ["brand", "tan", "muted"][i % 3])
    if has_note:
        x = MX + cw + cm(1)
        card(s, x, CT, W - MX - x, CB - CT, "card")
        txt(s, x + cm(0.8), CT + cm(0.8), W - MX - x - cm(1.6), cm(0.7), sp.get("insight_label", "Wniosek"), 13,
            color="tan", font="bold", caps=True, spacing=150)
        txt(s, x + cm(0.8), CT + cm(1.8), W - MX - x - cm(1.6), CB - CT - cm(2.6), sp["insight"], 17, font="bold",
            line=25)


def s_price(deck, sp):
    """Cena i marża dla handlu: produkt, duża metka z ceną, siatka warunków (marża, cena zakupu, promocja...)."""
    s = frame(deck, sp)
    img = sp.get("image")
    sx = MX + cm(5.6)
    h = fit_trio(img, cm(10.5), cm(11)) if isinstance(img, (list, tuple)) else cm(11)
    scene(s, img, sx, (CT + CB) / 2 + cm(0.3), h, sp.get("props", []), rot=-4, prop_scale=0.85,
          avoid=[(cm(12.4), 0, W, H)])
    x = cm(13.4)
    w = W - MX - x
    txt(s, x, CT, w, cm(0.7), sp.get("price_label", "Rekomendowana cena detaliczna"), 14, color="tan", font="bold",
        caps=True, spacing=150)
    ph = cm(2.6)
    pw = min(w, bd.text_w_emu(sp["price"], 60, "Mindset") + cm(2.4))
    tagshape = shape(s, MSO_SHAPE.PENTAGON, x, CT + cm(0.9), pw, ph, "brand")
    tagshape.adjustments[0] = 0.22
    tagshape._element.spPr.find(qn("a:xfrm")).set("flipH", "1")
    txt(s, x + cm(1.2), CT + cm(0.9), pw - cm(1.2), ph, sp["price"], 60, color="white", font="display", anchor="m")
    if sp.get("price_note"):
        txt(s, x, CT + cm(3.8), w, cm(0.8), sp["price_note"], 14, color="muted")
    facts = sp.get("facts", [])[:4]
    cols = 2
    g = GAP
    fw = (w - g) / cols
    fh = cm(2.7)
    fy = CT + cm(5.0)
    for i, f in enumerate(facts):
        fx = x + (i % cols) * (fw + g)
        yy = fy + (i // cols) * (fh + g)
        card(s, fx, yy, fw, fh, "card")
        txt(s, fx + cm(0.7), yy + cm(0.5), fw - cm(1.4), cm(0.6), f["label"], 12, color="muted", font="bold",
            caps=True, spacing=100)
        txt(s, fx + cm(0.7), yy + cm(1.2), fw - cm(1.4), cm(1.3), f["value"], fit(f["value"], 30, 16, fw - cm(1.4)),
            font="display")


def s_compare_table(deck, sp):
    """Porównanie z konkurencją / innymi produktami: cechy w wierszach, ✓ i ✗, kolumna 'nasz' wyróżniona."""
    s = frame(deck, sp)
    cols = sp["columns"]
    rows = sp["rows"]
    fw = cm(10.5)
    cw = (W - 2 * MX - fw) / len(cols)
    rh = min(cm(1.5), (CB - CT - cm(1.8)) / len(rows))
    y0 = CT
    # kolumna wyróżniona
    hx = MX + fw
    card(s, hx, y0 - cm(0.2), cw, cm(1.6) + rh * len(rows) + cm(0.4), "brand", name="tlo-kolumna")
    for j, c in enumerate(cols):
        txt(s, MX + fw + j * cw, y0, cw, cm(1.4), c, 16, color="white" if j == 0 else "ink", font="bold",
            align="c", anchor="m")
    for i, r in enumerate(rows):
        y = y0 + cm(1.6) + i * rh
        if i:
            rect(s, MX, y, fw, cm(0.03), "line")
            rect(s, MX + fw + cw, y, W - 2 * MX - fw - cw, cm(0.03), "line")
        txt(s, MX, y, fw - cm(0.4), rh, r[0], 16, font="bold", anchor="m")
        for j, v in enumerate(r[1:]):
            cx = MX + fw + j * cw + cw / 2
            if v in (True, False):
                ic = ("check" if v else "x")
                path = white_icon(ic) if j == 0 else (icon(ic) if v else os.path.join(A, "icons", "AD8767", "x.png"))
                sz = cm(0.9)
                s.shapes.add_picture(path, Emu(int(cx - sz / 2)), Emu(int(y + (rh - sz) / 2)), Emu(int(sz)))
            else:
                txt(s, cx - cw / 2, y, cw, rh, str(v), 15, color="white" if j == 0 else "ink",
                    font="bold" if j == 0 else "body", align="c", anchor="m")


def s_occasions(deck, sp):
    """Okazje spożycia / momenty dnia (rano, trening, kawa, wieczór): ikona w kole, pora, tytuł, opis."""
    s = frame(deck, sp)
    items = sp["items"][:4]
    n = len(items)
    cw = (W - 2 * MX - GAP * (n - 1)) / n
    d = cm(3.0)
    y = CT + cm(0.8)
    rect(s, MX + cw / 2, y + d / 2, (n - 1) * (cw + GAP), cm(0.05), "line")
    for i, it in enumerate(items):
        x = MX + i * (cw + GAP)
        cx = x + cw / 2
        shape(s, MSO_SHAPE.OVAL, cx - d / 2, y, d, d, "card")
        s.shapes.add_picture(icon(it.get("icon", "sunrise")), Emu(int(cx - d * 0.25)), Emu(int(y + d * 0.25)),
                             Emu(int(d * 0.5)))
        txt(s, x, y + d + cm(0.6), cw, cm(0.7), it.get("time", ""), 14, color="tan", font="bold", align="c",
            caps=True, spacing=150)
        txt(s, x, y + d + cm(1.4), cw, cm(1.3), it["title"], fit(it["title"], 26, 18, cw - cm(0.6)), font="display",
            align="c")
        txt(s, x + cm(0.4), y + d + cm(2.7), cw - cm(0.8), cm(2.6), it.get("text", ""), 14, color="muted",
            align="c", line=20)


def s_social(deck, sp):
    """Social media / kampania online: 3 telefony z postami (zdjęcia 9:16), pod każdym kanał i wynik."""
    s = frame(deck, sp)
    items = sp["items"][:3]
    ph = CB - CT - cm(2.9)
    pw = ph * 9 / 19.5
    inset = cm(2.2)  # podpisy pod telefonami są szersze niż telefon - zostają w marginesach
    g = (W - 2 * MX - 2 * inset - 3 * pw) / 2
    for i, it in enumerate(items):
        x = MX + inset + i * (pw + g)
        card(s, x, CT, pw, ph, "ink", name="tlo-telefon")
        b = cm(0.25)
        pic = picture(s, it.get("image"), x + b, CT + b, pw - 2 * b, ph - 2 * b, name="tlo-ekran")
        round_picture(pic, cm(0.35))
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + pw / 2 - cm(0.9), CT + cm(0.45), cm(1.8), cm(0.35), "ink",
              radius=0.5, name="tlo-notch")
        txt(s, x - cm(1), CT + ph + cm(0.35), pw + cm(2), cm(0.9), it.get("channel", ""), 17, font="bold", align="c")
        txt(s, x - cm(2), CT + ph + cm(1.2), pw + cm(4), cm(1.3), it.get("result", ""), 14, color="muted", align="c",
            line=19)
    if sp.get("text"):
        pass


def s_next_steps(deck, sp):
    """Następne kroki / ustalenia: checklista z właścicielem i terminem (tabela akcji po spotkaniu)."""
    s = frame(deck, sp)
    items = sp["items"]
    rh = min(cm(1.7), (CB - CT - cm(1.2)) / len(items))
    cols = [(MX + cm(1.6), cm(15.5), "Zadanie"), (MX + cm(17.6), cm(6.5), "Kto"), (MX + cm(24.6), W - MX - (MX + cm(24.6)), "Termin")]
    for x, w, h in cols:
        txt(s, x, CT, w, cm(0.8), sp.get("heads", {}).get(h, h), 13, color="tan", font="bold", caps=True,
            spacing=150)
    for i, it in enumerate(items):
        y = CT + cm(1.1) + i * rh
        rect(s, MX, y, W - 2 * MX, cm(0.03), "line")
        done = it.get("done", False)
        sz = cm(0.85)
        s.shapes.add_picture(icon("square-check" if done else "square"), Emu(int(MX + cm(0.2))),
                             Emu(int(y + (rh - sz) / 2)), Emu(int(sz)))
        txt(s, cols[0][0], y, cols[0][1], rh, it["task"], 17, font="bold", anchor="m",
            color="muted" if done else "ink")
        txt(s, cols[1][0], y, cols[1][1], rh, it.get("who", ""), 15, anchor="m")
        txt(s, cols[2][0], y, cols[2][1], rh, it.get("when", ""), 15, anchor="m", font="bold", color="brand")


# --- konwersja cudzych prezentacji (pptx_convert.py): typy bez limitów treści -----------------------------------
# Teksty przeniesione ze starej prezentacji nigdy nie są skracane, więc potrzebują typów, które same dobierają
# rozmiar pisma (20 -> 13 pt) i podają, czy treść się mieści (flow_layout / text_cols_layout) - konwerter dzieli
# slajdy PRZED budową, nie ucina po niej.
FLOW_SIZES = (20, 19, 18, 17, 16, 15, 14, 13)
FLOW_LH = 1.38  # interlinia (krotność rozmiaru pisma)


def _flow_style(k, size):
    """(font, pt, kolor, wcięcie EMU, odstęp przed w pt) dla rodzaju bloku: p akapit, li punkt, h podtytuł,
    small / url drobny tekst (źródła, adresy)."""
    if k == "h":
        return "bold", size + 1, "ink", 0, size * 0.9
    if k == "li":
        return "body", size, "ink", cm(0.75), size * 0.45
    if k in ("small", "url"):
        return "body", max(11, size - 3), "muted", 0, size * 0.5
    return "body", size, "ink", 0, size * 0.65


def _nlines(text, size, w, font):
    """Liczba linii z uwzględnieniem słów dłuższych niż szerokość (adresy URL zawija dopiero PowerPoint)."""
    def n(ln):
        tw = bd.text_w_emu(ln, size, FONT_REF[font][1])
        return 1 if tw <= w else math.ceil(tw * 1.2 / max(w, 1))  # 20% zapasu: PowerPoint łamie adres na ukośnikach
    return sum(n(ln) for ln in lines_for(text, size, w, font))


def _flow_h(blocks, size, w):
    """Wysokość (EMU) bloków tekstu przy danym rozmiarze i szerokości - ta sama miara, której używa budowa."""
    tot = 0
    for i, b in enumerate(blocks):
        font, sz, _c, ind, sp = _flow_style(b.get("k", "p"), size)
        n = _nlines(b["t"], sz, w - ind, font)
        tot += n * sz * FLOW_LH * 12700 + (sp * 12700 if i else 0)
    return tot * 1.03


def flow_layout(blocks, w, h, sizes=FLOW_SIZES):
    """Największy rozmiar pisma, przy którym bloki mieszczą się w (w x h) EMU; None = nie mieszczą się."""
    for size in sizes:
        if _flow_h(blocks, size, w) <= h:
            return size
    return None


def _flow_write(s, x, y, w, blocks, size, name="Tekst"):
    """Jedno pole tekstowe: akapit źródła = jeden akapit PowerPointa (łamie sam; twarde spacje pilnują typografii PL),
    punkty to prawdziwe wypunktowania, adresy - prawdziwe hiperłącza."""
    tb = s.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(_flow_h(blocks, size, w))))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, b in enumerate(blocks):
        k = b.get("k", "p")
        font, sz, color, ind, sp = _flow_style(k, size)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = Pt(sz * FLOW_LH)
        if i:
            p.space_before = Pt(sp)
        if k == "li":  # kolejność w pPr: spacing, buClr, buFont, buChar
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(int(ind)))
            pPr.set("indent", str(-int(ind)))
            clr = etree.SubElement(pPr, qn("a:buClr"))
            etree.SubElement(clr, qn("a:schemeClr")).set("val", "accent1")
            etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
            etree.SubElement(pPr, qn("a:buChar")).set("char", "•")
        for j, seg in enumerate(b["t"].split("\n")):  # "\n" w bloku = łamanie wiersza w tym samym akapicie
            if j:
                p.add_line_break()
            r = p.add_run()
            r.text = bd.typo_nbsp(seg)
            r.font.size = Pt(sz)
            r.font.name = FONT_REF[font][0]
            r.font.bold = FONT_REF[font][2]
            paint(r.font.color, color)
            if b.get("url"):
                r.hyperlink.address = b["url"]
    tb.name = name
    return tb


def _bialy_brzeg(path):
    """Obraz ma biały brzeg (rogi i środki krawędzi >= 240) - na białym slajdzie zlewa się z tłem."""
    try:
        im = Image.open(path).convert("RGB")
    except Exception:
        return False
    w, h = im.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3), (w // 2, 2), (w // 2, h - 3), (2, h // 2), (w - 3, h // 2)]
    return all(min(im.getpixel(p)) >= 240 for p in pts if 0 <= p[0] < w and 0 <= p[1] < h)


def _contain_pic(s, path, x, y, w, h, caption="", cap_pt=12):
    """Obraz w całości (bez przycinania) w ramce x,y,w,h; opcjonalny podpis pod obrazem. Zwraca zajętą wysokość."""
    cl = lines_for(caption, cap_pt, w, "bold") if caption else []
    ch = len(cl) * (cap_pt + 5) * 12700 + (cm(0.25) if cl else 0)
    r = img_ratio(path)
    bw, bh = (w, w / r) if r > w / max(1, h - ch) else ((h - ch) * r, h - ch)
    yy = y + (h - ch - bh) / 2
    pic = s.shapes.add_picture(path, Emu(int(x + (w - bw) / 2)), Emu(int(yy)), Emu(int(bw)), Emu(int(bh)))
    pic.name = "Zdjęcie - prawy klik: Zmień obraz"
    round_picture(pic, cm(0.3))
    if _bialy_brzeg(path):  # 10.10: biała grafika na białym slajdzie (s34) - ramka 1 px border #DDDDDD (DS)
        paint(pic.line.color, "DDDDDD")
        pic.line.width = Pt(0.75)
    if cl:  # pole podpisu na całą szerokość komórki (wiersze liczone dla w); pod węższym obrazem - wyśrodkowane
        txt(s, x, yy + bh + cm(0.25), w, len(cl) * (cap_pt + 5) * 12700, cl, cap_pt, color="muted",
            font="bold", line=cap_pt + 5, align="c" if bw < 0.98 * w else "l")
    return bh + ch


def s_flow(deck, sp):
    """Tekst bez limitu długości: akapity (p), punkty (li), podtytuły (h), drobny tekst (small, url) - sam dobiera
    rozmiar 20-13 pt; opcjonalnie 1-2 obrazy (całe, z podpisami) z prawej. Spec: kicker, title, blocks[{k, t, url}],
    images[{image, caption}], source."""
    s = frame(deck, sp)
    y0 = CT if sp.get("title") else cm(3.6)
    imgs = sp.get("images") or []
    tw = cm(16.6) if imgs else cm(24)
    size = flow_layout(sp["blocks"], tw, CB - y0 - cm(0.4)) or FLOW_SIZES[-1]
    _flow_write(s, MX, y0, tw, sp["blocks"], size)
    if imgs:
        x = MX + tw + cm(1.6)
        gap = cm(0.7)
        ih = ((CB - y0) - gap * (len(imgs) - 1)) / len(imgs)
        for i, it in enumerate(imgs):
            _contain_pic(s, it["image"], x, y0 + i * (ih + gap), W - MX - x, ih, it.get("caption", ""))


def text_cols_layout(columns, has_title=True):
    """Układ kolumn z nagłówkami: dict(size, hz, hh, card_h, y0, cw) albo None, gdy treść się nie mieści."""
    n = len(columns)
    y0 = CT if has_title else cm(3.6)
    cw = (W - 2 * MX - GAP * (n - 1)) / n
    pad = cm(1.0)
    iw = cw - 2 * pad
    hz = min([title_size(c["title"], 28, 18, iw) for c in columns if c.get("title")] or [28])
    hh = 0
    if any(c.get("title") for c in columns):
        hh = max(len(display_lines(c["title"], hz, iw)) for c in columns if c.get("title")) * hz * 12700 + cm(0.7)
    avail = (CB - y0) - 2 * pad - hh
    size = None
    heads_ok = all(bd.text_w_emu(max(c["title"].split(), key=len), hz, "Mindset") <= iw for c in columns if c.get("title"))
    for sz in FLOW_SIZES[2:]:  # kolumny: 18 -> 13 pt; żadne słowo nie może być szersze niż kolumna
        if heads_ok and all(_flow_h(c["blocks"], sz, iw) <= avail and
                            all(bd.text_w_emu(w, sz, "Lato") <= iw for b in c["blocks"] for w in b["t"].split())
                            for c in columns):
            size = sz
            break
    need = max(_flow_h(c["blocks"], size or FLOW_SIZES[-1], iw) for c in columns)
    return dict(size=size, hz=hz, hh=hh, y0=y0, cw=cw, pad=pad, iw=iw,
                card_h=min(CB - y0, max(cm(7.5), hh + need + 2 * pad)))


def s_text_cols(deck, sp):
    """2-4 kolumny w kartach: nagłówek (Mindset) + akapity / punkty (jak w s_flow). Spec: kicker, title,
    columns[{title, blocks[{k, t, url}]}], source."""
    s = frame(deck, sp)
    cols = sp["columns"]
    L = text_cols_layout(cols, bool(sp.get("title")))
    size = L["size"] or FLOW_SIZES[-1]
    for i, c in enumerate(cols):
        x = MX + i * (L["cw"] + GAP)
        card(s, x, L["y0"], L["cw"], L["card_h"], "card")
        if c.get("title"):
            ls = display_lines(c["title"], L["hz"], L["iw"])
            txt(s, x + L["pad"], L["y0"] + L["pad"], L["iw"], len(ls) * L["hz"] * 12700, ls, L["hz"], color="brand",
                font="display", line=L["hz"])
        if c["blocks"]:
            _flow_write(s, x + L["pad"], L["y0"] + L["pad"] + L["hh"], L["iw"], c["blocks"], size)


def s_pics(deck, sp):
    """Zdjęcia / zrzuty w całości (bez przycinania), 1-6, z podpisami; opcjonalnie wspólny podpis (note) pod spodem.
    Spec: kicker, title, items[{image, caption}], note, source."""
    s = frame(deck, sp)
    items = sp["items"]
    y0 = CT if sp.get("title") else cm(3.6)
    nl = lines_for(sp["note"], 15, W - 2 * MX) if sp.get("note") else []
    nh = len(nl) * 21 * 12700 + cm(0.5) if nl else 0
    n = len(items)
    cols = {1: 1, 2: 2, 3: 3, 4: 2, 5: 3, 6: 3}[n]
    rows = math.ceil(n / cols)
    area = CB - y0 - nh
    cw = (W - 2 * MX - GAP * (cols - 1)) / cols
    ch = (area - GAP * (rows - 1)) / rows
    for i, it in enumerate(items):
        c, r = i % cols, i // cols
        _contain_pic(s, it["image"], MX + c * (cw + GAP), y0 + r * (ch + GAP), cw, ch, it.get("caption", ""))
    if nl:
        txt(s, MX, CB - nh + cm(0.3), W - 2 * MX, nh - cm(0.3), nl, 15, color="muted", line=21, align="c")


# --- układ 1:1 ze starej prezentacji (07.10.2026) ---------------------------------------------------------------
# User 07.10: "Nie trzymałeś się tekstów w slajdzie i kolejności", "Staraj się trzymać układu ze starej prezentacji",
# "Segment 1 i 3 (...) musi być osobno". Typ `uklad` odtwarza stary slajd wiersz po wierszu (góra-dół) w nowym stylu:
# hasła (Mindset), akapity (Lato), kolumny-karty (obraz, nagłówek, linie, znacznik i metka przypięte na dole), kafle
# haseł, obrazy w całości. Sam zmniejsza pismo, aż wszystko mieści się w polu treści: nic nie ucina i nic nie dopisuje.
UK_KIND = {  # rodzaj wiersza: (czcionka, pt, kolor, interlinia, wyrównanie)
    "big": ("display", 64, "brand", 1.0, "c"), "h": ("display", 36, "brand", 1.06, "c"),
    "lead": ("display", 36, "ink", 1.06, "c"), "sub": ("display", 26, "brand", 1.08, "c"),
    "p": ("body", 25, "ink", 1.36, "l"), "b": ("bold", 25, "ink", 1.36, "l"),
    "small": ("body", 15, "muted", 1.4, "l"),
}
UK_COL = {"h": ("display", 30, "brand", 1.04), "lead": ("display", 26, "ink", 1.08), "p": ("body", 17, "ink", 1.36),
          "b": ("bold", 17, "ink", 1.36), "small": ("body", 13, "muted", 1.4)}  # bloki wewnątrz kolumny


def _uk_wrap(font, t, pt, w):
    """Linie tekstu (ręczne łamanie zostaje); None = jakieś słowo jest szersze niż pole, trzeba zmniejszyć pismo."""
    meas = FONT_REF[font][1]
    if any(bd.text_w_emu(wd, pt, meas) > w * 0.96 for wd in t.replace("\n", " ").split()):
        return None
    return display_lines(t, pt, w) if font == "display" else lines_for(t, pt, w, font)


QUOTE_PT, AUTHOR_PT = 30, 16  # cytat i autor jak w s20 szablonu (make_template: s_quote 30 pt kursywa, autor 16 pt bold)
F_WIERSZ = 1.3  # wiersze poza kartami rosną najwyżej 1,3 x; karty-pojemniki (kont) do 1,6 x - pismo ma wypełnić kartę
KONT_PT = {"p": 26, "b": 26, "lead": 40, "h": 36, "small": 16}  # górna granica pisma w karcie-pojemniku (08.10)


def _uk_text(row, f, width):
    font, pt0, color, lh, align = UK_KIND[row["k"]]
    pt = max(11, round(row.get("pt", pt0) * min(f, F_WIERSZ) * 2) / 2)
    if row.get("max_pt"):  # komentarz pod kartami: nie większy niż tekst kart
        pt = min(pt, row["max_pt"])
    ind = cm(0.85) * min(1, f) if row.get("li") else 0
    w = min(cm(row["w"]) if row.get("w") else (cm(27.5) if font == "display" else cm(26)), width) - ind
    ls = _uk_wrap(font, row["t"], pt, w)
    if ls is None:
        return None
    return dict(kind="text", h=len(ls) * pt * lh * 12700, lines=ls, pt=pt, font=font, color=row.get("color", color),
                lh=lh, align=row.get("align", align), w=w, ind=ind, wyr=row.get("wyr"))


def _rwane(ls, pt, iw, font, waska=False):
    """Akapit Lato w karcie wygląda na „rwany”: średnie wypełnienie wierszy (bez ostatniego) < 82% szerokości pola albo
    któryś wiersz < 60% („Nadwaga nie / wyklucza / niedożywienia”, „Format miękki, łatwy / do przegryzienia.”).
    waska (3-4 karty obok siebie): także średnio < 3,5 słowa w wierszu przy akapicie >= 6 słów."""
    if len(ls) < 2:
        return False
    meas = FONT_REF[font][1]
    ws = [bd.text_w_emu(x, pt, meas) / iw for x in ls[:-1]]
    if sum(ws) / len(ws) < 0.82 or min(ws) < 0.6:
        return True
    slow = sum(len(x.split()) for x in ls)
    return waska and slow >= 6 and slow / len(ls) < 3.5


def _uk_cols(row, f, width):
    items = row["items"]
    n = len(items)
    wts = [it.get("w", 1) for it in items]
    cws = [(width - GAP * (n - 1)) * wt / sum(wts) for wt in wts]
    cards = row.get("card", True)
    kont = bool(row.get("kont"))
    # 10.10 (runda 4): pad karty-pojemnika nie rosnie z pismem (f > 1 dawal 1,4-1,9 cm, tekst zawijal sie na ~60% karty)
    pad = cm(row.get("pad", 0.75)) * min(max(f, 0.8), 1.0 if kont else 1.2) if cards else 0
    gp = cm(row.get("bgap", 0.5)) if kont else cm(0.24)  # karta-pojemnik (08.10): akapity z wiekszym odstepem
    if not kont:
        f = min(f, F_WIERSZ)
    hmax_pt = KONT_PT["h"] if kont else 99
    heads = [(b["t"], cws[i] - 2 * pad, b.get("one_line")) for i, it in enumerate(items) for b in it.get("blocks", [])
             if b["k"] == "h" and "pt" not in b]
    # one_line (naglowki kart-pojemnikow): jedna linia w karcie; inaczej tylko najdluzsze slowo musi sie zmiescic
    hz = min((fit(t, max(15, min(hmax_pt, round(UK_COL["h"][1] * f))), 15, iw) if ol else
              title_size(t, max(15, min(hmax_pt, round(UK_COL["h"][1] * f))), 15, iw)) for t, iw, ol in heads) if heads else 0
    cols, hmax, chs, rwane = [], 0, [], False
    for i, it in enumerate(items):
        iw, parts, y = cws[i] - 2 * pad, [], 0
        for b in it.get("blocks", []):
            k = b["k"]
            if k == "img":
                ih = cm(b.get("h", 4.4)) * f
                parts.append(("img", y, ih, b))
                y += ih + cm(0.4) * f
                continue
            font, pt0, color, lh = UK_COL[k]
            pt = hz if (k == "h" and "pt" not in b) else max(10.5, round(b.get("pt", pt0) * f * 2) / 2)
            if kont and k in KONT_PT and not (k == "h" and "pt" not in b):
                pt = min(pt, KONT_PT[k])
            if b.get("max_pt"):
                pt = min(pt, b["max_pt"])
            ls = _uk_wrap(font, b["t"], pt, iw)
            if ls is None:
                return None
            bh = len(ls) * pt * lh * 12700
            if kont and font != "display" and _rwane(ls, pt, iw, font, n >= 3):
                rwane = True
            parts.append(("txt", y, bh, dict(lines=ls, pt=pt, font=font, color=b.get("color", color), lh=lh,
                                             wyr=b.get("wyr"), align=b.get("align", "l"))))
            y += bh + (cm(0.32) if k == "h" else gp) * f
        cols.append((parts, iw))
        chs.append(parts[-1][1] + parts[-1][2] if parts else 0)  # wysokosc tresci kolumny bez odstepu na koncu
        hmax = max(hmax, y)
    tag_h = cm(1.1) if any(it.get("tag") for it in items) else 0
    meta_h = cm(1.3) if any(it.get("meta") for it in items) else 0
    h = hmax + tag_h + meta_h + 2 * pad
    if row.get("min_h"):  # karta-pojemnik: najnizsza wysokosc (jak karta-artykul z szablonu), maleje razem z pismem
        h = max(h, cm(row["min_h"]) * min(1, f))
    hs = [h] * n  # 10.10: karty obok siebie zawsze rowne (s22); krotsza tresc stoi od gory (valign t)
    return dict(kind="cols", h=h, cols=cols, cws=cws, pad=pad, cards=cards, items=items, tag_h=tag_h, meta_h=meta_h,
                grow=row.get("grow", False), valign=row.get("valign", "t"), chs=chs, hs=hs, rwane=rwane)


def _uk_chips(row, f, width):
    f = min(f, F_WIERSZ)
    pt = max(14, round(row.get("pt", 26) * f))
    items, per, g, padx = row["items"], row.get("per_row", 3), cm(0.5), cm(0.9)
    ws = [bd.text_w_emu(t, pt, "Mindset") + 2 * padx for t in items]
    lines = [list(range(i, min(i + per, len(items)))) for i in range(0, len(items), per)]
    if any(sum(ws[i] for i in ln) + g * (len(ln) - 1) > width for ln in lines):
        return None
    # 10.10: rowna siatka - kafle jednej kolumny maja te sama szerokosc (najszerszy z kolumny), wiec rzedy o tej samej
    # liczbie kafli zaczynaja sie w tym samym miejscu (s09: drugi rzad byl przesuniety o ~20 px); wszystkie rowne, gdy sie mieszcza
    wm = max(ws)
    kol = [max(ws[ln[c]] for ln in lines if c < len(ln)) for c in range(max(len(ln) for ln in lines))]
    if all(wm * len(ln) + g * (len(ln) - 1) <= width for ln in lines):
        ws = [wm] * len(ws)
    elif all(sum(kol[:len(ln)]) + g * (len(ln) - 1) <= width for ln in lines):
        ws = [kol[c] for ln in lines for c in range(len(ln))]
    ch = pt * 2.3 * 12700
    return dict(kind="chips", h=len(lines) * ch + g * (len(lines) - 1), items=items, ws=ws, lines=lines, ch=ch, pt=pt,
                g=g, fill=row.get("fill", "brand"))


def _uk_quote(row, f, width):
    """Cytat jak slajd s20 szablonu: duzy cudzyslow (sage), tekst Lato kursywa, linia marki, autor pogrubiony."""
    f = min(f, 1.0)  # 10.10 (runda 4): cytat jak w s20 szablonu (30 pt, nie wiekszy); maleje tylko, gdy slajd jest ciasny
    pt = max(14, round(row.get("pt", QUOTE_PT) * f * 2) / 2)
    lh = 1.4
    off = cm(3.2) * min(1, f)
    w = width - off
    ls = _uk_wrap("body", row["t"], pt, w)
    if ls is None:
        return None
    th = len(ls) * pt * lh * 12700
    ah = AUTHOR_PT * 1.4 * 12700 if row.get("author") else 0
    h = max(th + (cm(0.5) + cm(0.1) + cm(0.35) + ah if ah else 0), cm(3.4) * min(1, f))
    return dict(kind="quote", h=h, lines=ls, pt=pt, lh=lh, w=w, off=off, th=th, author=row.get("author", ""),
                wyr=row.get("wyr"), color=row.get("color", "ink"), f=f)


def _uk_pics(row, f, width):
    return dict(kind="pics", flex=True, h=0, want=cm(row.get("h", 8.5)), min=cm(row.get("min_h", 5.5)), row=row)


def _wyroznij(tb, flags, size, font, color, italic=False):
    """Pojedyncze słowa w kolorze, jak w oryginale. flags: jeden znak na słowo całego pola, w kolejności czytania
    ('a' = akcent, 'i' = zieleń marki, inny znak = kolor pola). Łamanie wierszy nie zmienia kolejności słów."""
    ref, _, bold = FONT_REF[font]
    k = 0
    for p in tb.text_frame.paragraphs:
        if not p.runs:
            continue
        segs = []
        for part in re.split(r"(\s+)", p.runs[0].text):
            if not part:
                continue
            if part.isspace():
                fl = segs[-1][1] if segs else "-"
            else:
                fl = flags[k] if k < len(flags) else "-"
                k += 1
            if segs and segs[-1][1] == fl:
                segs[-1][0] += part
            else:
                segs.append([part, fl])
        for i, (t, fl) in enumerate(segs):
            r = p.runs[0] if i == 0 else p.add_run()
            r.text = t
            r.font.size = Pt(size)
            r.font.name = ref
            r.font.bold = bold
            r.font.italic = italic
            paint(r.font.color, {"a": "accent", "i": "brand"}.get(fl, color))


def _pics_rzad(items, width, h, y):
    """Obrazy jeden obok drugiego: wspólna wysokość (największa, która mieści się w szerokości i wysokości wiersza),
    wspólna górna krawędź; rząd rozpięty od lewego do prawego brzegu (odstęp do 4 cm), poza tym wyśrodkowany.
    Zwraca [(item, x, szerokość, wysokość, y)]."""
    rs = [img_ratio(it["image"]) for it in items]
    n, g = len(rs), GAP * 0.6
    hh = min(h, (width - g * (n - 1)) / sum(rs))
    tot = hh * sum(rs)
    gap = min((width - tot) / (n - 1), cm(6))  # 09.10: pierwszy obraz przy lewym brzegu kart, ostatni przy prawym
    x = MX + (width - tot - gap * (n - 1)) / 2
    out = []
    for it, r in zip(items, rs):
        out.append((it, x, hh * r, hh, y + (h - hh) / 2))
        x += hh * r + gap
    return out


def _pics_prawa(rs, idx, wr, h, g2, pos=None):
    """Kandydaci ułożenia obrazów idx w polu wr x h: rzędy po 1-2 obrazy (ostatni nieparzysty na całą szerokość) albo
    dwa stosy obok siebie (jak w oryginale: jeden obraz nad drugim i wysoki obok). Zwraca [(pole, [(i, x, y, w, h)])]."""
    def rzedy(grupy):
        hn = [max(((wr - g2 * (len(g) - 1)) / len(g)) / rs[i] for i in g) for g in grupy]
        sc = min(1.0, (h - g2 * (len(grupy) - 1)) / sum(hn))
        yy = (h - (sum(hn) * sc + g2 * (len(grupy) - 1))) / 2
        pole, pl = 0, []
        for g, hr in zip(grupy, hn):
            cw = (wr - g2 * (len(g) - 1)) / len(g)
            for k, i in enumerate(g):
                pl.append((i, k * (cw + g2), yy, cw, hr * sc))
                pole += min(cw, hr * sc * rs[i]) / rs[i] ** 0.5  # pierwiastek z pola: małe obrazy też się liczą
            yy += hr * sc + g2
        return pole, pl

    def stosy(k1, k2, ratio):
        pole, pl, x = 0, [], 0
        if pos:  # stosy w kolejności z oryginału: lewy stos = ten, który stał bardziej na lewo; w stosie góra-dół
            k1, k2 = sorted((k1, k2), key=lambda g: sum(pos[i][0] for i in g) / len(g))
            k1, k2 = sorted(k1, key=lambda i: pos[i][1]), sorted(k2, key=lambda i: pos[i][1])
        for g, cw in ((k1, (wr - g2) * ratio), (k2, (wr - g2) * (1 - ratio))):
            hn = [cw / rs[i] for i in g]
            sc = min(1.0, (h - g2 * (len(g) - 1)) / sum(hn))
            yy = (h - (sum(hn) * sc + g2 * (len(g) - 1))) / 2
            for i, hr in zip(g, hn):
                pl.append((i, x, yy, cw, hr * sc))
                pole += sc * (cw * hr) ** 0.5
                yy += hr * sc + g2
            x += cw + g2
        return pole, pl
    out, n = [], len(idx)

    def podzialy(m):
        if m == 0:
            yield []
            return
        for k in (1, 2):
            if k <= m:
                for t in podzialy(m - k):
                    yield [k] + t
    for comp in podzialy(n):
        grupy, a = [], 0
        for k in comp:
            grupy.append(idx[a:a + k])
            a += k
        out.append(rzedy(grupy))
    for mask in range(1, 2 ** n - 1):
        k1 = [idx[j] for j in range(n) if mask >> j & 1]
        k2 = [idx[j] for j in range(n) if not mask >> j & 1]
        if len(k1) > 1 or len(k2) > 1:
            out += [stosy(k1, k2, r / 100) for r in range(35, 66, 5)]
    return out


def _pics_siatka(items, width, h, y):
    """Duży obraz z lewej + reszta z prawej (rzędy po 2 albo dwa stosy). Udział lewej kolumny i ułożenie prawej dobieram
    tak, żeby obrazy razem zajęły jak najwięcej pola. Zwraca [(item, x, y, szerokość, wysokość)] - pola, w które obraz
    wpisuje się w całości (_contain_pic)."""
    rs = [img_ratio(it["image"]) for it in items]
    g, g2 = GAP, GAP * 0.6
    pos = [it["box"][:2] for it in items] if all(it.get("box") for it in items) else None
    best = None
    for pct in range(30, 68, 2):
        wl = (width - g) * pct / 100
        wr = width - wl - g
        al = min(wl, h * rs[0]) / rs[0] ** 0.5
        for pole, pl in _pics_prawa(rs, list(range(1, len(items))), wr, h, g2, pos):
            if best is None or al + pole > best[0]:
                best = (al + pole, wl, pl)
    _a, wl, pl = best
    out = [(items[0], MX, y, wl, h)]
    for i, x, yy, w_, h_ in pl:
        out.append((items[i], MX + wl + g + x, y + yy, w_, h_))
    return out


def _uk_draw(s, m, y, width, card_fill, cx=None):
    """Rysuje jeden wiersz. Zwraca (lewy, prawy brzeg) obrazów dla wiersza `pics` (do wyśrodkowania podpisu pod rzędem);
    cx = środek, względem którego ustawiamy wyśrodkowany tekst (domyślnie środek slajdu)."""
    n0 = len(s.shapes)
    if m["kind"] == "text":
        x = MX if m["align"] == "l" else (W / 2 if cx is None else cx) - (m["w"] + m["ind"]) / 2
        if cx is not None:
            x = max(MX, min(x, W - MX - m["w"] - m["ind"]))
        if m["ind"]:
            dot(s, x + cm(0.22), y + m["pt"] * m["lh"] * 12700 * 0.5, cm(0.3), "brand")
        tb = txt(s, x + m["ind"], y, m["w"], m["h"], m["lines"], m["pt"], color=m["color"], font=m["font"],
                 align=m["align"], line=m["pt"] * m["lh"])
        if m.get("wyr"):
            _wyroznij(tb, m["wyr"], m["pt"], m["font"], m["color"])
    elif m["kind"] == "quote":
        gz = max(60, round(120 * min(1, m["f"])))  # cudzyslow sage przy lewym marginesie
        txt(s, MX, y - gz * 12700 * 0.34, cm(3.0), gz * 1.3 * 12700, "\u201e", gz, color="brand_soft", font="display")
        x = MX + m["off"]
        tb = txt(s, x, y, m["w"], m["th"], m["lines"], m["pt"], color=m["color"], line=m["pt"] * m["lh"], italic=True)
        if m.get("wyr"):
            _wyroznij(tb, m["wyr"], m["pt"], "body", m["color"], italic=True)
        if m["author"]:
            yy = y + m["th"] + cm(0.5)
            rect(s, x, yy, cm(2.4), cm(0.1), "brand")
            txt(s, x, yy + cm(0.35), m["w"], cm(0.8), m["author"], AUTHOR_PT, color="ink", font="bold")
    elif m["kind"] == "chips":
        for li, ln in enumerate(m["lines"]):
            x = (W - sum(m["ws"][i] for i in ln) - m["g"] * (len(ln) - 1)) / 2
            yy = y + li * (m["ch"] + m["g"])
            for i in ln:
                shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, yy, m["ws"][i], m["ch"], m["fill"], radius=0.28)
                txt(s, x, yy, m["ws"][i], m["ch"], [m["items"][i]], m["pt"], color="white", font="display", align="c",
                    anchor="m")
                x += m["ws"][i] + m["g"]
    elif m["kind"] == "pics":
        row, h = m["row"], m["h"]
        items = row["items"]
        bez_podpisow = not any(it.get("caption") for it in items)
        if bez_podpisow and not row.get("ws") and not row.get("layout") and len(items) >= 2:
            # 08.10: obrazy w jednym rzędzie - ta sama wysokość i górna krawędź, rząd rozpięty między brzegami kart
            for it, x, w_, h_, yy in _pics_rzad(items, width, h, y):
                _contain_pic(s, it["image"], x, yy, w_, h_)
        elif bez_podpisow and row.get("layout") == "1+siatka" and len(items) > 2:
            for it, x, yy, w_, h_ in _pics_siatka(items, width, h, y):
                _contain_pic(s, it["image"], x, yy, w_, h_)
        elif row.get("layout") == "1+siatka" and len(items) > 2:  # duży obraz z lewej, reszta w siatce 2 x n z prawej
            wl = (width - GAP) * row.get("split", 0.5)
            _contain_pic(s, items[0]["image"], MX, y, wl, h, items[0].get("caption", ""))
            rest = items[1:]
            rws = math.ceil(len(rest) / 2)
            g2 = GAP * 0.6
            cw = (width - wl - GAP - g2) / 2
            parts = row.get("rows_h") or [1] * rws  # udziały wysokości wierszy siatki (np. [0.62, 0.38])
            hs = [(h - g2 * (rws - 1)) * p / sum(parts) for p in parts]
            for i, it in enumerate(rest):
                r = i // 2
                _contain_pic(s, it["image"], MX + wl + GAP + (i % 2) * (cw + g2), y + sum(hs[:r]) + g2 * r, cw, hs[r],
                             it.get("caption", ""))
        else:
            n = len(items)
            ws = row["ws"] if len(row.get("ws") or []) == n else [1] * n  # udziały szerokości (mały obraz zostaje mały)
            x = MX
            for it, wt in zip(items, ws):
                cw = (width - GAP * (n - 1)) * wt / sum(ws)
                _contain_pic(s, it["image"], x, y, cw, h, it.get("caption", ""))
                x += cw + GAP
    else:  # kolumny
        x, H_ = MX, m["h"]
        grow = m.get("grow")
        for (parts, iw), cw, it, ch, hi in zip(m["cols"], m["cws"], m["items"], m["chs"], m.get("hs") or [H_] * len(m["cws"])):
            pad = m["pad"]
            hi = H_ if grow else hi
            if m["cards"]:
                card(s, x, y, cw, hi, it.get("fill", card_fill))
            vo = max(0, (hi - 2 * pad - m["tag_h"] - m["meta_h"] - ch) / 2) if m["valign"] == "m" else 0
            for kind, py, ph, d in parts:
                py = py + vo
                if kind == "img":
                    r = img_ratio(d["image"])
                    bw, bh = (iw, iw / r) if r > iw / ph else (ph * r, ph)
                    ox = (iw - bw) / 2 if m["cards"] else 0  # 09.10: bez kart obraz stoi przy lewej krawedzi kolumny (jak naglowek)
                    pic = s.shapes.add_picture(d["image"], Emu(int(x + pad + ox)),
                                               Emu(int(y + pad + py + (ph - bh) / 2)), Emu(int(bw)), Emu(int(bh)))
                    pic.name = d.get("name") or "Wizualizacja - prawy klik: Zmień obraz"
                    if d.get("round"):
                        round_picture(pic, cm(0.3))
                else:
                    tb = txt(s, x + pad, y + pad + py, iw, ph, d["lines"], d["pt"], color=d["color"], font=d["font"],
                             line=d["pt"] * d["lh"], align=d.get("align", "l"))
                    if d.get("wyr"):
                        _wyroznij(tb, d["wyr"], d["pt"], d["font"], d["color"])
            if it.get("tag"):  # osobny znacznik (np. "Zmiana nazwy") - nad metką, na dole karty
                tag(s, x + pad, y + hi - pad - m["meta_h"] - cm(0.8), it["tag"], fill=it.get("tag_fill", "accent"),
                    size=11, h=cm(0.8), style="badge")
            if it.get("meta"):  # osobna metka (np. "Segment 1 & 3") - przypięta do dołu karty
                tag(s, x + pad, y + hi - pad - cm(0.95), it["meta"], fill="brand", size=13, h=cm(0.95), style="price")
            x += cw + GAP
    if m["kind"] == "pics":
        pic = [sh for sh in list(s.shapes)[n0:] if sh.shape_type == 13]
        return (min(p.left for p in pic), max(p.left + p.width for p in pic)) if pic else None
    return None


def uklad_layout(sp):
    """Miary wierszy slajdu `uklad` bez rysowania: (lista miar, współczynnik pisma) albo (None, None), gdy treść się
    nie mieści nawet małym pismem. Jedno źródło dla s_uklad i dla automatu konwersji (pptx_convert), który przed
    budową sprawdza, czy stary slajd wejdzie na jeden nowy."""
    y0 = CT if sp.get("title") else cm(3.3)
    avail = CB - y0 - (cm(0.25) if sp.get("source") else 0)
    width = W - 2 * MX
    fn = {"cols": _uk_cols, "chips": _uk_chips, "pics": _uk_pics, "quote": _uk_quote}
    first = None  # pierwszy (największy) pasujący współczynnik; dalej szukamy układu bez „rwanych” kart
    for f in [x / 100 for x in range(int(sp.get("max_f", 1.0) * 100), 44, -5)]:
        if first and f < 0.7 * first[1]:  # „rwane” karty: do 30% mniejsze pismo, byle linie były pełne
            break
        ms, kart_pt = [], 0
        for r in sp["rows"]:
            if r.get("po_kartach") and kart_pt:  # komentarz pod kartami: hierarchia - nie większy niż tekst kart + 2 pt
                r = dict(r, max_pt=min(r.get("max_pt", 99), kart_pt + 2))
            m = fn.get(r["k"], _uk_text)(r, f, width)
            if m is None:
                break
            if m["kind"] == "cols":
                kart_pt = max([kart_pt] + [d["pt"] for parts, _iw in m["cols"] for (k_, _y, _h, d) in parts
                                           if k_ == "txt" and d["font"] != "display"])
            m["gap"] = cm(r.get("gap", 0.8 if r["k"] in ("cols", "pics", "chips", "big", "h", "quote") else 0.5)) * min(1, f)
            ms.append(m)
        else:
            fixed = sum(m["h"] for m in ms if not m.get("flex")) + sum(m["gap"] for m in ms[1:])
            flex = [m for m in ms if m.get("flex")]
            left = avail - fixed
            ok = False
            if flex:
                if left >= sum(m["want"] for m in flex) or (f <= 0.6 and left >= sum(m["min"] for m in flex)):
                    for m in flex:
                        m["h"] = left / len(flex)
                    ok = True
            elif left >= 0:
                grow = [m for m in ms if m.get("grow")]
                for m in grow:
                    m["h"] += left / len(grow)
                ok = True
            if ok:
                if not any(m.get("rwane") for m in ms):
                    return ms, f
                first = first or (ms, f)
    return first if first else (None, None)


def uklad_fit(sp):
    """Współczynnik pisma, przy którym slajd `uklad` się mieści (1.0 = rozmiary bazowe), albo None."""
    return uklad_layout(sp)[1]


def s_uklad(deck, sp):
    """Układ 1:1 ze starego slajdu (konwersja): kicker / tytuł jak w ramie, pod nimi wiersze w kolejności góra-dół.
    Spec: kicker, title, bg (paper|card), valign (m|t), max_f, source, rows[]:
      {"k": "big|h|lead|sub|p|b|small", "t": tekst, "align": "c|l", "color": token, "pt": n, "w": cm, "li": true,
       "wyr": "a--i-"}  - wyr: kolor słowo po słowie (a = akcent, i = zieleń marki, - = kolor wiersza)
      {"k": "cols", "items": [{"blocks": [{"k": "img", "image": p, "h": cm} | {"k": "h|lead|p|b|small", "t": ...,
                                "align": "l|c", "color": token, "wyr": "a--i-"}],
                               "tag": "Zmiana nazwy", "meta": "Segment 1 & 3", "w": waga}], "card": true, "grow": true,
       "pad": cm (domyslnie 0.75), "min_h": cm (najnizsza karta), "valign": "t|m" (tresc w karcie), "kont": true}
      {"k": "quote", "t": cytat, "author": "Autor, firma", "wyr": "a--i-", "color": token}  - jak slajd s20 szablonu
      {"k": "chips", "items": [hasła], "per_row": 3}
      {"k": "pics", "items": [{"image": p, "caption": "", "box": [x, y, w, h cm w oryginale]}], "h": cm, "min_h": cm,
       "ws": [udziały szerokości], "layout": "1+siatka"}  - obrazy zawsze w całości; bez podpisów: wspólna wysokość i
       górna krawędź, rząd rozpięty między brzegami kart; 1+siatka: ułożenie dobierane do pola (box = kolejność L-P)
    wiersz tekstu / blok karty: "max_pt" - górna granica pisma (komentarz pod kartą nie większy niż tekst karty);
    "po_kartach": true - komentarz pod kartami: pismo najwyżej o 2 pt większe niż tekst kart (dyn. w uklad_layout);
    karty kont (pojemniki): pismo rośnie do 1,6 x (granice KONT_PT), wiersze poza kartami do 1,3 x; dwie karty bez obrazów,
    z których krótsza ma < 70% treści dłuższej: każda ma wysokość swojej treści + pad (górne krawędzie równe);
    kolumny bez kart (card false): obraz przy lewej krawędzi kolumny; rząd obrazów (pics) rozpięty od brzegu do brzegu.
    slajd: "links": [{"t": "Byron Sharp", "url": "https://..."}] - hiperłącze na tych słowach (bez dopisanego tekstu)"""
    bg = sp.get("bg", "paper")
    s = frame(deck, sp, bg)
    y0 = CT if sp.get("title") else cm(3.3)
    avail = CB - y0 - (cm(0.25) if sp.get("source") else 0)
    width = W - 2 * MX
    rows = sp["rows"]
    best, _f = uklad_layout(sp)
    if best is None:
        raise ValueError("uklad: treść nie mieści się na slajdzie (%s) - podziel go" % (sp.get("title") or sp.get("kicker")))
    total = sum(m["h"] for m in best) + sum(m["gap"] for m in best[1:])
    valign = sp.get("valign") or ("t" if all(r["k"] in ("p", "b", "small") for r in rows) else "m")
    y = y0 + ((avail - total) / 2 if valign == "m" else 0)
    rzad = None  # brzegi ostatniego wiersza obrazów: podpis-wniosek (sub) tuż pod nim stoi na jego środku
    for i, m in enumerate(best):
        if i:
            y += m["gap"]
        cx = (rzad[0] + rzad[1]) / 2 if rzad and rows[i]["k"] == "sub" else None
        rzad = _uk_draw(s, m, y, width, "white" if bg == "card" else "card", cx)
        y += m["h"]


BUILDERS = {
    "cover": s_cover, "cover_text": s_cover_text, "agenda": s_agenda, "section": s_section, "lead": s_lead,
    "statement": s_statement, "longtext": s_longtext, "bullets": s_bullets, "steps": s_steps, "quote": s_quote,
    "two_cols": s_two_cols, "text_image": s_text_image, "full_image": s_full_image, "gallery": s_gallery,
    "product_hero": s_product_hero, "flavor": s_flavor, "line": s_line, "nutrition": s_nutrition, "tiles": s_tiles,
    "hero_stat": s_hero_stat, "kpis": s_kpis, "bars": s_bars, "segments": s_segments, "table": s_table,
    "timeline": s_timeline, "split": s_split, "reasons": s_reasons, "facts": s_facts, "cards_images": s_cards_images,
    "contact": s_contact, "end": s_end, "instructions": s_instructions, "icon_list": s_icon_list,
    "icon_grid": s_icon_grid,
    "video": s_video, "before_after": s_before_after, "donut": s_donut, "columns": s_columns, "price": s_price,
    "compare_table": s_compare_table, "occasions": s_occasions, "social": s_social, "next_steps": s_next_steps,
    "media": s_media, "article": s_article,
    "flow": s_flow, "text_cols": s_text_cols, "pics": s_pics,
    "uklad": s_uklad,
}


def link_w_tekscie(s, fragment, url):
    """Hiperłącze na fragmencie tekstu slajdu (np. nazwisko autora cytatu), tak jak w oryginale: widoczny tekst się nie
    zmienia, nie dochodzi żaden napis. Fragment może się zawijać na kilka akapitów-linii; przebiegi dzielimy na granicach
    fragmentu (kolory słów zostają). Zwraca True, gdy fragment znaleziono."""
    from copy import deepcopy
    want = " ".join(fragment.replace(" ", " ").split()).lower()
    if not want:
        return False
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        flat, pos, runs = "", [], {}
        for pi, p in enumerate(sh.text_frame.paragraphs):
            if pi:
                flat, pos = flat + " ", pos + [None]
            for ri, r in enumerate(p.runs):
                runs[(pi, ri)] = r
                flat += r.text
                pos += [(pi, ri, ci) for ci in range(len(r.text))]
        hay = flat.replace(" ", " ").lower()
        i = hay.find(want)
        if i < 0:
            continue
        span = {}
        for pp in pos[i:i + len(want)]:
            if pp:
                a, b = span.get(pp[:2], (pp[2], pp[2]))
                span[pp[:2]] = (min(a, pp[2]), max(b, pp[2]))
        for key, (a, b) in span.items():
            r, t0 = runs[key], runs[key].text
            b += 1
            if a > 0:
                el = deepcopy(r._r)
                el.find(qn("a:t")).text = t0[:a]
                r._r.addprevious(el)
            if b < len(t0):
                el = deepcopy(r._r)
                el.find(qn("a:t")).text = t0[b:]
                r._r.addnext(el)
            r.text = t0[a:b]
            r.hyperlink.address = url
        return True
    return False


def add_label(s, text, number):
    """Opis przeznaczenia: notatki + etykieta POZA obszarem slajdu (w pokazie niewidoczna)."""
    s.notes_slide.notes_text_frame.text = text
    x = W + cm(0.6)
    box = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, cm(0.4), cm(8.5), cm(0.9), "FFD42A", radius=0.3)
    box.name = "OPIS - poza slajdem (niewidoczny w pokazie)"
    txt(s, x + cm(0.4), cm(0.4), cm(8), cm(0.9), "SLAJD %02d - do czego służy" % number, 12, color="1F1F1F",
        font="bold", anchor="m")
    ls = lines_for(text, 13, cm(8.5))
    card_h = len(ls) * 19 * 12700 + cm(0.8)
    c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, cm(1.45), cm(8.5), card_h, "FFF6CC", radius=0.06)
    c.name = "OPIS - tresc"
    txt(s, x + cm(0.4), cm(1.85), cm(7.7), card_h, ls, 13, color="1F1F1F", line=19)


def build(spec, out):
    global PH_DIR, T
    T = dict(THEMES[spec.get("theme", "fresh")])
    PH_DIR = os.path.join(os.environ.get("DK_CACHE_DIR") or os.path.join(A, "placeholdery"), spec.get("theme", "fresh"))
    os.makedirs(PH_DIR, exist_ok=True)  # DK_CACHE_DIR: program portable z dysku sieciowego pisze do katalogu usera
    deck = Deck(spec)
    for sl in spec["slides"]:
        n0 = len(deck.prs.slides)
        BUILDERS[sl["type"]](deck, sl)
        s = deck.prs.slides[n0]
        if sl.get("morph") is True:  # Morph tylko tam, gdzie ma sens (np. kolejne karty smaków) - 28.09
            morph(s)
        if sl.get("notes"):  # notatki prelegenta (konwersja cudzej prezentacji)
            s.notes_slide.notes_text_frame.text = sl["notes"]
        for lk in sl.get("links", []):  # hiperłącza z oryginału na tych samych słowach (bez dopisanego tekstu)
            if not link_w_tekscie(s, lk["t"], lk["url"]):
                print("UWAGA: hiperłącza '%s' nie położono (nie znaleziono tekstu)" % lk["t"])
        if sl.get("label_slide"):  # opis "do czego sluzy" (szablon)
            add_label(s, sl["label_slide"], deck.page)
        if sl.get("hidden"):
            s._element.set("show", "0")
        sid = int(deck.prs.slides._sldIdLst[-1].get("id"))
        if sl.get("section") or not deck.sections:
            deck.sections.append((sl.get("section", "Prezentacja"), []))
        deck.sections[-1][1].append(sid)
    if not spec.get("sections"):
        deck.sections = []
    out = deck.finish(out)
    build.last_out = out
    return len(spec["slides"])


def main():
    spec_path = sys.argv[1]
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    base = os.path.dirname(os.path.abspath(spec_path))

    def resolve(o, key=None):
        if isinstance(o, dict):
            return {k: resolve(v, k) for k, v in o.items()}
        if isinstance(o, list):
            return [resolve(v, key if key in ("props", "image", "pack") else None) for v in o]
        if key in ("path", "image", "props", "pack", "video", "poster", "claim_image") and isinstance(o, str) \
                and not os.path.isabs(o):
            return os.path.join(base, o)
        return o

    spec = resolve(spec)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, spec.get("output", "prezentacja.pptx"))
    n = build(spec, out)
    bd.online_videos(build.last_out)  # znaczniki filmów -> prawdziwe wideo YouTube (PowerPoint)
    print("OK", build.last_out, n, "slajdow")


if __name__ == "__main__":
    main()
