# -*- coding: utf-8 -*-
"""
Wersja "DK Fresh" - odswiezony, lzejszy styl prezentacji Dobra Kaloria (propozycja).

    python build_fresh.py spec.json [wyjscie.pptx]

Zasady stylu (references/styl-fresh.md):
  - jasne, cieple tlo papieru, duzo powietrza, brak ciezkich pasow i pedzli
  - Mindset (marka) tylko do tytulow i duzych liczb; tekst w Nunito Sans
  - organiczny motyw: miekkie kola w odcieniach szalwii za packshotami
  - akcent kolorystyczny produktu (accent w spec) uzywany oszczednie
  - zaokraglone karty bez obramowan; wyroznienie = cienka zielona linia
Po zbudowaniu: render.ps1 -EmbedFonts (osadza Nunito Sans).
"""
import json
import os
import sys

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_deck as bd  # noqa: E402
from build_deck import cm, img_ratio, place_image  # noqa: E402

A = os.path.join(bd.ROOT, "assets")
bd.FONT_FILES.update({
    "Nunito Sans": os.path.join(A, "fonts", "NunitoSans-Regular.ttf"),
    "Nunito Sans SemiBold": os.path.join(A, "fonts", "NunitoSans-SemiBold.ttf"),
    "Nunito Sans ExtraBold": os.path.join(A, "fonts", "NunitoSans-ExtraBold.ttf"),
})

# --- tokeny DK Fresh --------------------------------------------------------
PAPER = "FAF6EF"      # tlo
CARD = "F1ECE2"       # karta na tle
SAGE_50 = "E7EEDF"    # najjasniejsza szalwia (kola, tlo konca)
SAGE_200 = "C9DABB"
SAGE_400 = "8DB27A"   # drugorzedne slupki
BRAND = "006400"      # zielen marki - akcenty, wyroznienia
INK = "1F3A24"        # tytuly i tekst (kontrast ~11:1 na PAPER)
MUTED = "5B6B5C"      # opisy (kontrast ~5.4:1 na PAPER)
DISPLAY = "Mindset"
BODY = "Nunito Sans"
BODY_SB = "Nunito Sans SemiBold"
BODY_XB = "Nunito Sans ExtraBold"
MX = cm(1.9)          # margines poziomy
W, H = bd.SLIDE_W, bd.SLIDE_H


class Fresh(bd.Deck):
    def __init__(self, spec):
        super().__init__()
        self.accent = spec.get("accent", BRAND)
        self.page = 0
        self.footer = spec.get("footer", "")


def txt(slide, x, y, w, h, text, size, color=INK, font=BODY, align=PP_ALIGN.LEFT,
        anchor=MSO_ANCHOR.TOP, line=None, spacing=None):
    if isinstance(text, str) and font.startswith("Nunito") and w > 0:
        # lamiemy sami, tylko na spacjach - PowerPoint lamie tez na lacznikach ("slodko-|kwasne"),
        # a fonty nie maja twardego lacznika U+2011
        text = bd.wrap_lines(text, size, int(w * 0.96), font)
        # ochrona przed sierota: pojedyncze slowo w ostatniej linii -> sciagamy slowo z linii wyzej
        if len(text) >= 2 and len(text[-1].split()) == 1 and len(text[-2].split()) > 2:
            prev = text[-2].split()
            text[-2], text[-1] = " ".join(prev[:-1]), prev[-1] + " " + text[-1]
    tb = bd.add_text(slide, int(x), int(y), int(w), int(h), text if isinstance(text, list) else [text], size,
                     color=color, name=font, align=align, anchor=anchor, line_pt=line)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if spacing is not None:
        for p in tf.paragraphs:
            for r in p.runs:
                r.font._rPr.set("spc", str(spacing))
    return tb


def shape(slide, kind, x, y, w, h, fill, radius=None, line=None, line_w=1.5):
    sh = slide.shapes.add_shape(kind, Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = RGBColor.from_string(line)
        sh.line.width = Pt(line_w)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    return sh


def pill_w(text, size, font=BODY_XB, spacing=100, pad=None):
    """Szerokosc pigulki na tekst w wersalikach z rozstrzelem (spc w setnych punktu na znak)."""
    t = text.upper()
    return bd.text_w_emu(t, size, font) + len(t) * spacing / 100 * 12700 + (pad or cm(1.2))


def circle(slide, cx, cy, d, fill):
    return shape(slide, MSO_SHAPE.OVAL, cx - d / 2, cy - d / 2, d, d, fill)


def blob(slide, cx, cy, d, fill, seed=1, amp=0.09, n=7):
    """Miekki, organiczny ksztalt (zamiast idealnego kola): zamknieta krzywa Catmull-Rom -> Bezier.
    seed daje powtarzalny ksztalt; amp = sila odksztalcenia (0.06-0.12 wyglada naturalnie)."""
    import math
    import random
    from lxml import etree
    if not globals().get("BLOBS", True):  # motyw shop: zamiast plamy kremowa zaokraglona karta
        return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, cx - d / 2, cy - d / 2, d, d, fill, radius=0.1)
    rnd = random.Random(seed)
    off = rnd.uniform(0, math.tau)
    pts = []
    for i in range(n):
        a = off + i * math.tau / n
        r = 500 * (0.9 + rnd.uniform(-amp, amp))
        pts.append((500 + r * math.cos(a), 500 + r * math.sin(a)))
    sh = shape(slide, MSO_SHAPE.RECTANGLE, cx - d / 2, cy - d / 2, d, d, fill)
    ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    f = lambda p: '<a:pt x="%d" y="%d"/>' % (round(p[0]), round(p[1]))
    segs = []
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segs.append("<a:cubicBezTo>%s%s%s</a:cubicBezTo>" % (f(c1), f(c2), f(p2)))
    geom = etree.fromstring(
        '<a:custGeom xmlns:a="%s"><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
        '<a:pathLst><a:path w="1000" h="1000"><a:moveTo>%s</a:moveTo>%s<a:close/></a:path></a:pathLst></a:custGeom>'
        % (ns, f(pts[0]), "".join(segs)))
    spPr = sh._element.spPr
    old = spPr.find("{%s}prstGeom" % ns)
    old.addprevious(geom)
    spPr.remove(old)
    sh.name = "Ksztalt organiczny"
    return sh


def logo(slide, x, y, w):
    slide.shapes.add_picture(os.path.join(A, "logo_green_box.png"), Emu(int(x)), Emu(int(y)), Emu(int(w)))


def kicker(deck, slide, text, x, y, color=None):
    """Mala etykieta nad tytulem: kropka w kolorze akcentu + wersaliki z rozstrzelem."""
    circle(slide, x + 55000, y + 95000, 110000, color or deck.accent)
    txt(slide, x + 200000, y, cm(16), 260000, text.upper(), 12, color=MUTED, font=BODY_XB, spacing=200)


def frame(deck, spec, bg=PAPER):
    """Wspolna rama slajdu tresci: tlo, kicker, tytul, maly znak marki, numer strony."""
    s = deck.new_slide(bg=bg)
    deck.page += 1
    if spec.get("kicker"):
        kicker(deck, s, spec["kicker"], MX, cm(1.3))
    if spec.get("title"):
        size = bd.fit_size(spec["title"], spec.get("title_size", 40), 26, cm(24), DISPLAY)
        txt(s, MX, cm(1.95), cm(26), cm(2.2), spec["title"], size, color=INK, font=DISPLAY)
    logo(s, W - MX - cm(1.9), cm(1.25), cm(1.9))
    foot = spec.get("source") or deck.footer
    if foot:
        txt(s, MX, H - cm(1.05), cm(26), cm(0.6), foot, 10.5, color=MUTED)
    txt(s, W - MX - cm(1.5), H - cm(1.05), cm(1.5), cm(0.6), "%02d" % (deck.page + 1), 10.5,
        color=MUTED, font=BODY_SB, align=PP_ALIGN.RIGHT)
    return s


def packshot_on_circle(deck, s, path, cx, cy, h, d=None, rot=0, shadow="3B2A20", circle_fill=SAGE_50):
    d = d or h * 0.92
    blob(s, cx, cy + h * 0.04, d, circle_fill, seed=int(cx) % 97)
    w = h * img_ratio(path)
    place_image(s, path, cx - w / 2, cy - h / 2, h=h, rot=rot, shadow=True, shadow_color=shadow)


# --- slajdy -----------------------------------------------------------------
def f_cover(deck, spec):
    s = deck.new_slide(bg=PAPER)
    # organiczne tlo: duze kolo szalwii wychodzace poza kadr + mniejsze w akcencie
    blob(s, W * 0.75, H * 0.52, cm(17.5), SAGE_50, seed=3)
    blob(s, W * 0.92, H * 0.15, cm(3.4), SAGE_200, seed=11, amp=0.12)
    logo(s, MX, cm(1.5), cm(2.6))
    kicker(deck, s, spec.get("kicker", "Nowość"), MX, cm(6.2))
    tsize = bd.fit_size(spec["title"], 80, 44, cm(15), DISPLAY)
    lines = bd.wrap_lines(spec["title"], tsize, cm(15), DISPLAY)
    th = len(lines) * tsize * 1.02 * 12700
    txt(s, MX, cm(6.9), cm(15.5), th, "\n".join(lines).split("\n"), tsize, color=INK, font=DISPLAY, line=tsize * 1.0)
    y = cm(6.9) + th + cm(0.5)
    if spec.get("subtitle"):
        n_sub = len(bd.wrap_lines(spec["subtitle"], 20, int(cm(15.5) * 0.96), BODY))
        txt(s, MX, y, cm(15.5), cm(3), spec["subtitle"], 20, color=MUTED, line=28)
        y += n_sub * 28 * 12700 + cm(0.8)
    if spec.get("tag"):  # pigulka pod podtytulem w kolorze akcentu
        tw = pill_w(spec["tag"], 14)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, MX, y, tw, cm(1.0), deck.accent, radius=0.5)
        txt(s, MX, y, tw, cm(1.0), spec["tag"].upper(), 14, color="FFFFFF", font=BODY_XB,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=100)
    img = spec["image"]
    h = cm(spec.get("image_h", 14.5))
    w = h * img_ratio(img)
    place_image(s, img, W * 0.75 - w / 2, H * 0.52 - h / 2, h=h, rot=spec.get("rot", -4), shadow=True,
                shadow_color="3B2A20")


def f_features(deck, spec):
    """Packshot na kole po lewej, 2x2 karty cech po prawej."""
    s = frame(deck, spec)
    packshot_on_circle(deck, s, spec["image"], cm(8.2), cm(11.3), cm(12.5), d=cm(12))
    items = spec["items"]
    x0, y0 = cm(15.6), cm(5.0)
    cw, ch, g = cm(8.3), cm(5.6), cm(0.45)
    for i, it in enumerate(items[:4]):
        x = x0 + (i % 2) * (cw + g)
        y = y0 + (i // 2) * (ch + g)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, ch, CARD, radius=0.12)
        circle(s, x + cm(1.25), y + cm(1.3), cm(1.1), SAGE_200)
        txt(s, x + cm(0.7), y + cm(0.85), cm(1.1), cm(0.9), "%02d" % (i + 1), 12, color=INK, font=BODY_XB,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        tsize = bd.fit_size(it["title"], 28, 18, cw - cm(1.4), DISPLAY)
        txt(s, x + cm(0.7), y + cm(2.3), cw - cm(1.4), cm(1.4), it["title"], tsize, color=INK, font=DISPLAY)
        txt(s, x + cm(0.7), y + cm(3.7), cw - cm(1.4), cm(1.8), it["text"], 16, color=MUTED, line=22)


def f_hero_stat(deck, spec):
    """Jedna liczba-bohater + 2-3 mniejsze liczby w kartach + packshot na kole."""
    s = frame(deck, spec)
    named(blob(s, W - cm(6.2), H * 0.60, cm(12.5), SAGE_50, seed=5), "!!blob")
    if spec.get("image"):
        product_scene(s, spec["image"], W - cm(6.2), H * 0.60, cm(10.5), spec.get("props", []), rot=5)
    txt(s, MX - cm(0.15), cm(4.4), cm(16), cm(5.2), spec["value"], 150, color=BRAND, font=DISPLAY)
    txt(s, MX, cm(9.6), cm(15), cm(2.2), spec["label"], 22, color=INK, font=BODY_SB, line=30)
    subs = spec.get("items", [])
    cw, g = cm(7.2), cm(0.45)
    for i, it in enumerate(subs):
        x = MX + i * (cw + g)
        y = cm(12.6)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, cm(3.7), CARD, radius=0.14)
        txt(s, x + cm(0.6), y + cm(0.45), cw - cm(1.2), cm(1.6), it["value"], 40, color=INK, font=DISPLAY)
        txt(s, x + cm(0.6), y + cm(2.1), cw - cm(1.2), cm(1.4), it["label"], 13.5, color=MUTED, line=18)


def f_compare(deck, spec):
    """Warianty na kartach; zwyciezca na bialej karcie z zielona linia i etykieta."""
    s = frame(deck, spec)
    items, hi = spec["items"], spec.get("highlight")
    n = len(items)
    g = cm(0.5)
    cw = (W - 2 * MX - g * (n - 1)) / n
    y, ch = cm(4.7), cm(12.2)
    vals = [float(it["value"].rstrip("%")) for it in items if it.get("value")]
    vmax = max(vals) if vals else 1
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        win = i == hi
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, ch, "FFFFFF" if win else CARD, radius=0.07,
              line=BRAND if win else None, line_w=2.25)
        if win and spec.get("badge"):
            bw = pill_w(spec["badge"], 11, pad=cm(1.0))
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + (cw - bw) / 2, y - cm(0.45), bw, cm(0.9), BRAND, radius=0.5)
            txt(s, x + (cw - bw) / 2, y - cm(0.45), bw, cm(0.9), spec["badge"].upper(), 11, color="FFFFFF",
                font=BODY_XB, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=100)
        ih = cm(6.3)
        iw = ih * img_ratio(it["path"])
        place_image(s, it["path"], x + (cw - iw) / 2, y + cm(0.8), h=ih, shadow=True, shadow_color="3B2A20")
        if it.get("value"):
            txt(s, x + cm(0.7), y + cm(7.6), cw - cm(1.4), cm(1.7), it["value"], 44 if win else 36,
                color=BRAND if win else INK, font=DISPLAY)
            # cienki pasek proporcji pod liczba (tylko gdy wszystkie warianty maja wartosc)
            if len(vals) == len(items):
                bw_full = cw - cm(1.4)
                shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + cm(0.7), y + cm(9.45), bw_full, cm(0.22), SAGE_50, radius=0.5)
                shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + cm(0.7), y + cm(9.45),
                      bw_full * float(it["value"].rstrip("%")) / vmax, cm(0.22), BRAND if win else SAGE_400, radius=0.5)
        txt(s, x + cm(0.7), y + cm(9.95), cw - cm(1.4), cm(0.7), it["label"], 14, color=INK, font=BODY_XB)
        if it.get("sub"):
            txt(s, x + cm(0.7), y + cm(10.75), cw - cm(1.4), cm(1.2), it["sub"], 12.5, color=MUTED)


def f_split(deck, spec):
    """Podzial A vs B jednym paskiem + wiersz wynikow w grupach."""
    s = frame(deck, spec)
    a, b = spec["a"], spec["b"]
    x0, x1 = MX, W - MX
    y = cm(5.2)
    txt(s, x0, y, cm(12), cm(4), a["value"], 110, color=BRAND, font=DISPLAY)
    txt(s, x1 - cm(8), y + cm(1.3), cm(8), cm(2.8), b["value"], 64, color=SAGE_400, font=DISPLAY, align=PP_ALIGN.RIGHT)
    by = cm(9.5)
    frac = float(a["value"].rstrip("%")) / 100
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, by, (x1 - x0), cm(0.9), SAGE_200, radius=0.5)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, by, (x1 - x0) * frac, cm(0.9), BRAND, radius=0.5)
    txt(s, x0, by + cm(1.2), cm(14), cm(1), a["label"], 18, color=INK, font=BODY_XB)
    txt(s, x1 - cm(14), by + cm(1.2), cm(14), cm(1), b["label"], 18, color=MUTED, font=BODY_SB, align=PP_ALIGN.RIGHT)
    groups = spec.get("groups", [])
    if groups:
        gy = cm(12.9)
        txt(s, x0, gy, cm(20), cm(0.7), spec.get("groups_title", ""), 13, color=MUTED, font=BODY_XB, spacing=100)
        cw, g = cm(7.2), cm(0.45)
        for i, it in enumerate(groups):
            x = x0 + i * (cw + g)
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, gy + cm(0.8), cw, cm(2.7), CARD, radius=0.16)
            txt(s, x + cm(0.6), gy + cm(1.15), cm(3.5), cm(1.8), it["value"], 36, color=INK, font=DISPLAY)
            txt(s, x + cm(3.4), gy + cm(1.1), cw - cm(3.8), cm(2.2), it["label"], 13.5, color=MUTED,
                anchor=MSO_ANCHOR.MIDDLE)
        if spec.get("note"):
            nx = x0 + len(groups) * (cw + g)
            txt(s, nx + cm(0.3), gy + cm(0.95), x1 - nx - cm(0.3), cm(2.5), spec["note"], 15, color=INK,
                font=BODY_SB, line=21, anchor=MSO_ANCHOR.MIDDLE)


def f_bars(deck, spec):
    """Poziome slupki z etykieta nad slupkiem (czytelniej niz z boku) + karta wniosku."""
    s = frame(deck, spec)
    items, hi = spec["items"], set(spec.get("highlight", []))
    x0, bw = MX, cm(17.5)
    y0 = cm(4.9)
    row = min(cm(2.25), (cm(16.4) - y0) / len(items))
    for i, it in enumerate(items):
        y = y0 + i * row
        on = i in hi
        txt(s, x0, y, cm(13), cm(0.8), it["label"], 15, color=INK if on else MUTED, font=BODY_XB if on else BODY_SB)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, y + cm(0.85), bw, cm(0.6), SAGE_50, radius=0.5)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, y + cm(0.85), bw * it["value"] / 100, cm(0.6),
              BRAND if on else SAGE_400, radius=0.5)
        txt(s, x0 + bw + cm(0.5), y + cm(0.3), cm(3), cm(1.4), "%d%%" % round(it["value"]), 26 if on else 22,
            color=INK, font=DISPLAY, anchor=MSO_ANCHOR.MIDDLE)
    if spec.get("insight"):
        cx = cm(23.2)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, cx, y0, W - MX - cx, cm(11.3), SAGE_50, radius=0.08)
        if spec.get("image"):
            ih = cm(5.6)
            iw = ih * img_ratio(spec["image"])
            place_image(s, spec["image"], cx + (W - MX - cx - iw) / 2, y0 + cm(0.7), h=ih, rot=4, shadow=True,
                        shadow_color="3B2A20")
        txt(s, cx + cm(0.7), y0 + cm(6.9), W - MX - cx - cm(1.4), cm(4), spec["insight"], 15, color=INK,
            font=BODY_SB, line=21)


def f_reasons(deck, spec):
    """Argumenty dla handlu: 4 karty z numerem, liczba/haslo + opis."""
    s = frame(deck, spec)
    items = spec["items"]
    n = len(items)
    g = cm(0.5)
    cw = (W - 2 * MX - g * (n - 1)) / n
    y, ch = cm(5.0), cm(11.4)
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        fill = BRAND if i == 0 else CARD
        fg = "FFFFFF" if i == 0 else INK
        sub = "DCEBD5" if i == 0 else MUTED
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, ch, fill, radius=0.08)
        txt(s, x + cm(0.8), y + cm(0.8), cw, cm(0.7), "%02d" % (i + 1), 13, color=sub, font=BODY_XB, spacing=100)
        vs = bd.fit_size(it["value"], 54, 26, cw - cm(1.6), DISPLAY)
        txt(s, x + cm(0.8), y + cm(3.0), cw - cm(1.6), cm(2.4), it["value"], vs, color=fg, font=DISPLAY)
        txt(s, x + cm(0.8), y + cm(5.6), cw - cm(1.6), cm(1.4), it["title"], 16, color=fg, font=BODY_XB, line=21)
        txt(s, x + cm(0.8), y + cm(7.4), cw - cm(1.6), cm(3.6), it["text"], 13, color=sub, line=18)


def f_end(deck, spec):
    s = deck.new_slide(bg=SAGE_50)
    blob(s, W * 0.12, H * 0.92, cm(9), SAGE_200, seed=7)
    blob(s, W * 0.93, H * 0.08, cm(5), "FFFFFF", seed=13, amp=0.12)
    lw = cm(7.5)
    logo(s, (W - lw) / 2, cm(4.6), lw)
    txt(s, 0, cm(11.2), W, cm(1.6), spec.get("hashtag", "#zawszedobra"), 36, color=BRAND, font=DISPLAY,
        align=PP_ALIGN.CENTER)
    if spec.get("contact"):
        txt(s, 0, cm(13.2), W, cm(1.2), spec["contact"], 15, color=MUTED, align=PP_ALIGN.CENTER)


def f_segments(deck, spec):
    """2 grupy konsumentow obok siebie; w kazdej 2-4 wyniki (duza liczba + opis).
    groups: [{name, desc, metrics:[{value,label}]}]"""
    s = frame(deck, spec)
    groups = spec["groups"]
    n = len(groups)
    g = cm(0.6)
    cw = (W - 2 * MX - g * (n - 1)) / n
    y = cm(4.6)
    ch = H - cm(1.6) - y
    if spec.get("lead"):
        txt(s, MX, cm(3.9), cm(28), cm(0.8), spec["lead"], 15, color=MUTED)
        y += cm(0.7)
        ch -= cm(0.7)
    for i, gr in enumerate(groups):
        x = MX + i * (cw + g)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, ch, "FFFFFF" if i == 0 else CARD, radius=0.05)
        circle(s, x + cm(1.1), y + cm(1.15), cm(0.5), BRAND if i == 0 else SAGE_400)
        txt(s, x + cm(1.7), y + cm(0.7), cw - cm(2.4), cm(1), gr["name"], 24, color=INK, font=DISPLAY)
        txt(s, x + cm(0.9), y + cm(1.85), cw - cm(1.8), cm(1.6), gr["desc"], 13, color=MUTED, line=18)
        ms = gr["metrics"]
        my0 = y + cm(3.7)
        rh = (y + ch - cm(0.4) - my0) / len(ms)
        for j, m in enumerate(ms):
            my = my0 + j * rh
            ln = s.shapes.add_connector(1, Emu(int(x + cm(0.9))), Emu(int(my)), Emu(int(x + cw - cm(0.9))), Emu(int(my)))
            ln.line.color.rgb = RGBColor.from_string(SAGE_200)
            ln.line.width = Pt(1)
            txt(s, x + cm(0.9), my, cm(5.4), rh, m["value"], 50, color=BRAND if i == 0 else INK, font=DISPLAY,
                anchor=MSO_ANCHOR.MIDDLE)
            txt(s, x + cm(6.4), my, cw - cm(7.3), rh, m["label"], 15, color=INK, font=BODY_SB, line=20,
                anchor=MSO_ANCHOR.MIDDLE)


def f_skus(deck, spec):
    """Warianty/SKU jako karty: kolorowe kolo smaku (albo packshot), nazwa, gramatura, EAN."""
    s = frame(deck, spec)
    items = spec["items"]
    n = len(items)
    g = cm(0.6)
    cw = (W - 2 * MX - g * (n - 1)) / n
    y, ch = cm(4.8), cm(11.6)
    for i, it in enumerate(items):
        x = MX + i * (cw + g)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, ch, CARD, radius=0.07)
        cx, cy = x + cw / 2, y + cm(4.0)
        blob(s, cx, cy, cm(5.6), it.get("color", SAGE_200), seed=20 + i)
        if it.get("path"):
            ih = cm(6.2)
            iw = ih * img_ratio(it["path"])
            place_image(s, it["path"], cx - iw / 2, cy - ih / 2 - cm(0.3), h=ih, shadow=True, shadow_color="3B2A20")
        txt(s, x + cm(0.8), y + cm(7.6), cw - cm(1.6), cm(1.2), it["name"], 26, color=INK, font=DISPLAY,
            align=PP_ALIGN.CENTER)
        txt(s, x + cm(0.8), y + cm(8.9), cw - cm(1.6), cm(0.8), it.get("meta", ""), 14, color=MUTED, font=BODY_SB,
            align=PP_ALIGN.CENTER)
        if it.get("ean"):
            txt(s, x + cm(0.8), y + cm(9.8), cw - cm(1.6), cm(0.8), "EAN " + it["ean"], 13, color=MUTED,
                align=PP_ALIGN.CENTER)


def f_section(deck, spec):
    """Slajd przejscia rozdzialu: gleboka zielen, jasny tytul - rytm jasne/ciemne w prezentacji."""
    s = deck.new_slide(bg=BRAND)
    deck.page += 1
    blob(s, W * 0.86, H * 0.78, cm(15), "0B7714", seed=31)
    blob(s, W * 0.97, H * 0.12, cm(5), "0B7714", seed=37, amp=0.12)
    if spec.get("image"):
        h = cm(spec.get("image_h", 11))
        w = h * img_ratio(spec["image"])
        place_image(s, spec["image"], W * 0.8 - w / 2, H * 0.55 - h / 2, h=h, rot=spec.get("rot", 6), shadow=True,
                    shadow_color="00270A")
    txt(s, MX, cm(5.2), cm(6), cm(1), spec.get("number", "%02d" % (deck.page + 1)), 16, color=SAGE_200, font=BODY_XB,
        spacing=200)
    tsize = bd.fit_size(spec["title"], 64, 36, cm(17), DISPLAY)
    lines = bd.wrap_lines(spec["title"], tsize, cm(17), DISPLAY)
    txt(s, MX, cm(6.3), cm(18), cm(7), lines, tsize, color="FFFFFF", font=DISPLAY, line=tsize * 1.0)
    if spec.get("subtitle"):
        txt(s, MX, cm(6.6) + len(lines) * tsize * 12700, cm(15), cm(3), spec["subtitle"], 18, color=SAGE_50, line=26)
    logo_w = cm(1.9)
    s.shapes.add_picture(os.path.join(A, "logo_green_letters.png"), Emu(int(MX)), Emu(int(H - cm(2.8))), Emu(int(logo_w)))


# =============================================================================
# Sceny produktu, okladki WOW, slajdy smakow, Morph, motywy (24.09.2026, runda 2)
# =============================================================================
THEMES = {
    # fresh: cieply papier, szalwia, organiczne plamy (domyslny)
    "fresh": dict(PAPER="FAF6EF", CARD="F1ECE2", SAGE_50="E7EEDF", SAGE_200="C9DABB", SAGE_400="8DB27A",
                  BRAND="006400", INK="1F3A24", MUTED="5B6B5C", BLOBS=True, TAG="pill"),
    # shop: jak dobrakaloria.pl - biel, kremowe karty, prawie czarne naglowki, zielen sklepu, metki cenowe
    "shop": dict(PAPER="FFFFFF", CARD="FDF8EC", SAGE_50="FDF8EC", SAGE_200="EFE6D2", SAGE_400="9CC9A8",
                 BRAND="0F763E", INK="1F1F1F", MUTED="5E5E5E", BLOBS=False, TAG="price"),
}
BLOBS, TAG = True, "pill"
THEME = "fresh"
PANEL_TONE = {"fresh": "0B7714", "shop": "13874A"}


def set_theme(name):
    """Przelacza tokeny kolorow modulu (fresh | shop). Wolac przed budowaniem slajdow."""
    global THEME
    THEME = name
    g = globals()
    for k, v in THEMES[name].items():
        g[k] = v


def named(sh, name):
    """Nazwa obiektu. Prefiks '!!' = Morph laczy obiekty o tej samej nazwie na sasiednich slajdach."""
    sh.name = name
    return sh


def add_morph(slide, dur=1400):
    """Przejscie Morph (PowerPoint 2019+/365); starsze wersje dostaja Fade (mc:Fallback)."""
    from lxml import etree
    pns = "http://schemas.openxmlformats.org/presentationml/2006/main"
    xml = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
           'xmlns:p="%s" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" '
           'xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main">'
           '<mc:Choice Requires="p159"><p:transition spd="slow" p14:dur="%d"><p159:morph option="byObject"/>'
           '</p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition>'
           '</mc:Fallback></mc:AlternateContent>' % (pns, dur))
    el = etree.fromstring(xml)
    root = slide._element
    anchor = root.find("{%s}clrMapOvr" % pns)
    if anchor is None:
        anchor = root.find("{%s}cSld" % pns)
    anchor.addnext(el)


def soft_card_or_blob(s, cx, cy, d, fill, seed, name=None):
    """Motyw fresh: organiczna plama; motyw shop: kremowa zaokraglona karta (sklep nie ma plam)."""
    if BLOBS:
        sh = blob(s, cx, cy, d, fill, seed=seed)
    else:
        sh = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, cx - d / 2, cy - d / 2, d, d, CARD, radius=0.08)
    if name:
        named(sh, name)
    return sh


# Miejsca na MALE rekwizyty wokol paczki (styl sklepu dobrakaloria.pl: drobne kawalki owocow/kulek,
# lekko nachodzace na krawedz paczki). (u, v) wzgledem ramki paczki 0..1, rozmiar = ulamek wysokosci
# paczki, obrot, przod (True) / za paczka (False).
SCATTER = [
    (-0.16, 0.30, 0.20, -16, True),
    (1.10, 0.16, 0.17, 24, False),
    (-0.10, 0.86, 0.22, 10, True),
    (1.14, 0.70, 0.21, -12, True),
    (0.26, 1.04, 0.15, 34, True),
    (0.80, 1.06, 0.17, -28, True),
    (0.62, -0.06, 0.13, 12, False),
    (-0.26, 0.58, 0.12, 40, False),
]


def product_scene(s, pack, cx, cy, h, props=(), rot=-5, key="pack", scale_props=1.0, shadow_col="3B2A20"):
    """Paczka + male rekwizyty rozsypane wokol. pack=None -> kompozycja z samych rekwizytow
    (np. gdy packshot smaku jeszcze nie dotarl). Zwraca ramke (x0,y0,x1,y1) paczki."""
    props = [p for p in props if p]
    if not pack:  # zastepczo: pierwszy rekwizyt jako srodek sceny
        pack, props = props[0], props[1:]
        h = h * 0.62
    w = h * img_ratio(pack)
    x0, y0 = cx - w / 2, cy - h / 2
    placed = []
    for i, (u, v, f, r, front) in enumerate(SCATTER[:len(props)]):
        ratio = img_ratio(props[i])
        box = h * f * scale_props  # dluzszy bok rekwizytu
        ph = box if ratio <= 1 else box / ratio
        pw = ph * ratio
        placed.append((front, props[i], x0 + u * w - pw / 2, y0 + v * h - ph / 2, ph, r, i))
    for front, path, px, py, ph, r, i in placed:
        if not front:
            named(place_image(s, path, px, py, h=ph, rot=r), "!!%s_prop%d" % (key, i))
    named(place_image(s, pack, x0, y0, h=h, rot=rot, shadow=True, shadow_color=shadow_col), "!!%s" % key)
    for front, path, px, py, ph, r, i in placed:
        if front:
            named(place_image(s, path, px, py, h=ph, rot=r), "!!%s_prop%d" % (key, i))
    return x0, y0, x0 + w, y0 + h


def chip(s, x, y, text, dot=None, bg="FFFFFF", fg=None, size=13, h=None):
    """Etykieta smaku: kropka w kolorze owocu + nazwa. Motyw shop: ksztalt metki cenowej."""
    fg = fg or INK
    h = h or cm(1.0)
    pad = cm(0.45)
    tw = bd.text_w_emu(text, size, BODY_XB) + (cm(0.55) if dot else 0) + 2 * pad
    kind = MSO_SHAPE.SNIP_2_DIAG_RECTANGLE if TAG == "price" else MSO_SHAPE.ROUNDED_RECTANGLE
    sh = shape(s, kind, x, y, tw, h, bg, radius=0.5 if TAG == "pill" else None)
    if TAG == "price":
        sh.adjustments[0] = 0.0
        sh.adjustments[1] = 0.35
    tx = x + pad
    if dot:
        circle(s, tx + cm(0.15), y + h / 2, cm(0.3), dot)
        tx += cm(0.55)
    txt(s, tx, y, tw, h, text, size, color=fg, font=BODY_XB, anchor=MSO_ANCHOR.MIDDLE)
    return tw


def chips_row(s, x, y, items, bg="FFFFFF", fg=None, gap=None):
    gap = gap or cm(0.3)
    for it in items:
        x += chip(s, x, y, it["name"], dot=it.get("dot"), bg=bg, fg=fg) + gap


def wave_panel(s, w, fill, amp=cm(1.4), seed=4, name="!!panel"):
    """Zielony panel od lewej krawedzi z organiczna (falista) prawa krawedzia."""
    from lxml import etree
    import random
    rnd = random.Random(seed)
    sh = shape(s, MSO_SHAPE.RECTANGLE, 0, 0, w + amp, H, fill)
    W1 = 10000
    base = int(W1 * w / (w + amp))
    ys = [0, 2500, 5000, 7500, 10000]
    xs = [base + int(rnd.uniform(-0.5, 1.0) * (W1 - base)) for _ in ys]
    ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    segs = "".join('<a:cubicBezTo><a:pt x="%d" y="%d"/><a:pt x="%d" y="%d"/><a:pt x="%d" y="%d"/></a:cubicBezTo>'
                   % (xs[i], ys[i] + 900, xs[i + 1], ys[i + 1] - 900, xs[i + 1], ys[i + 1]) for i in range(4))
    geom = etree.fromstring(
        '<a:custGeom xmlns:a="%s"><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
        '<a:pathLst><a:path w="10000" h="10000"><a:moveTo><a:pt x="0" y="0"/></a:moveTo>'
        '<a:lnTo><a:pt x="%d" y="0"/></a:lnTo>%s<a:lnTo><a:pt x="0" y="10000"/></a:lnTo><a:close/></a:path>'
        '</a:pathLst></a:custGeom>' % (ns, xs[0], segs))
    spPr = sh._element.spPr
    old = spPr.find("{%s}prstGeom" % ns)
    old.addprevious(geom)
    spPr.remove(old)
    return named(sh, name)


def big_logo(s, x, y, w, on_green=True):
    """Duze logo jak we wzorze: na zieleni biala ramka z przezroczystymi literami (litery = kolor panelu)."""
    f = "logo_white_box.png" if on_green else "logo_green_box.png"
    pic = s.shapes.add_picture(os.path.join(A, f), Emu(int(x)), Emu(int(y)), Emu(int(w)))
    return named(pic, "!!logo")


def title_block(s, x, y, w, spec, on_dark=False, max_pt=72, show_sub=True):
    """Kicker + tytul (Mindset) + podtytul (Nunito) + etykiety smakow. Zwraca y konca."""
    ink = "FFFFFF" if on_dark else INK
    sub = SAGE_50 if on_dark else MUTED
    if spec.get("kicker"):
        circle(s, x + 55000, y + 95000, 110000, spec.get("accent", "F2C94C" if on_dark else BRAND))
        txt(s, x + 200000, y, w, 260000, spec["kicker"].upper(), 12, color=SAGE_200 if on_dark else MUTED,
            font=BODY_XB, spacing=200)
        y += cm(0.75)
    if bd.text_w_emu(spec["title"], 40, DISPLAY) <= w and spec.get("title_one_line"):
        tsize = bd.fit_size(spec["title"], max_pt, 40, w, DISPLAY)
    else:
        tsize = bd.fit_size(max(spec["title"].split(), key=len), max_pt, 40, w, DISPLAY)
    lines = bd.wrap_lines(spec["title"], tsize, w, DISPLAY)
    named(txt(s, x, y, w, len(lines) * tsize * 12700, lines, tsize, color=ink, font=DISPLAY, line=tsize * 0.98),
          "!!title")
    y += len(lines) * tsize * 0.98 * 12700 + cm(0.45)
    if spec.get("subtitle") and show_sub:
        n = len(bd.wrap_lines(spec["subtitle"], 19, int(w * 0.96), BODY))
        txt(s, x, y, w, n * 27 * 12700, spec["subtitle"], 19, color=sub, line=27)
        y += n * 27 * 12700 + cm(0.6)
    if spec.get("flavors"):
        chips_row(s, x, y, spec["flavors"], bg="FFFFFF", fg=INK)
        y += cm(1.3)
    return y


def f_cover_split(deck, spec):
    """Okladka z DUZYM LOGO na ZIELONYM PODZIALE (wymog szefowej - jak we wzorze), 3 warianty WOW:
    1: prosty podzial, paczka z rekwizytami NA granicy paneli (paczka 'wychodzi' z zieleni)
    2: tekst bialy na zieleni, paczka na plamie po jasnej stronie
    3: falista krawedz panelu, logo wysrodkowane jak we wzorze, paczka duza przy prawej dolnej krawedzi"""
    v = int(spec.get("variant", 1))
    s = deck.new_slide(bg=PAPER)
    props = spec.get("props", [])
    pack = spec.get("image")
    if v == 1:
        pw = cm(14.2)
        named(shape(s, MSO_SHAPE.RECTANGLE, 0, 0, pw, H, BRAND), "!!panel")
        if BLOBS:
            named(blob(s, cm(2), H - cm(1.5), cm(9), PANEL_TONE[THEME], seed=41), "!!panel_blob")
        big_logo(s, cm(2.0), cm(1.9), cm(6.2))
        soft_card_or_blob(s, pw + cm(0.4), cm(11.2), cm(13.5), SAGE_50, 43, "!!blob")
        product_scene(s, pack, pw, cm(11.0), cm(11.8), props, rot=-6)
        title_block(s, cm(21.8), cm(4.6), W - cm(21.8) - MX, spec, max_pt=66)
    elif v == 2:
        pw = cm(17.2)
        named(shape(s, MSO_SHAPE.RECTANGLE, 0, 0, pw, H, BRAND), "!!panel")
        if BLOBS:
            named(blob(s, pw - cm(1), cm(1), cm(8), PANEL_TONE[THEME], seed=47), "!!panel_blob")
        big_logo(s, MX, cm(1.8), cm(5.8))
        title_block(s, MX, cm(8.0), pw - MX - cm(1.4), spec, on_dark=True, max_pt=70)
        soft_card_or_blob(s, cm(25.6), cm(10), cm(15.5), SAGE_50, 53, "!!blob")
        product_scene(s, pack, cm(25.6), cm(9.9), cm(13.2), props, rot=5)
    else:
        # jak wzor: duze logo na srodku zielonej polowy; prawa strona: tytul w 1 linii nad scena produktu
        pw = cm(13.8)
        wave_panel(s, pw, BRAND, seed=spec.get("seed", 4))
        lw = cm(8.6)
        big_logo(s, (pw - lw) / 2, (H - lw * 295 / 400) / 2, lw)
        cx = pw + (W - pw) / 2 + cm(0.6)
        one = dict(spec, title_one_line=True)
        tw = W - pw - cm(3.4)
        title_block(s, pw + cm(2.6), cm(1.4), tw, one, max_pt=54, show_sub=False)
        soft_card_or_blob(s, cx, cm(12.0), cm(12.8), SAGE_50, 59, "!!blob")
        product_scene(s, pack, cx, cm(12.0), cm(10.8), props, rot=-4)


def f_product_hero(deck, spec):
    """Paczka w centrum z rekwizytami, claimy wokol (2 z lewej, 2 z prawej) - 'anatomia produktu'."""
    s = frame(deck, spec)
    soft_card_or_blob(s, W / 2, cm(11.1), cm(12.5), SAGE_50, 61, "!!blob")
    product_scene(s, spec.get("image"), W / 2, cm(11.0), cm(11.4), spec.get("props", []), rot=-3)
    items = spec["items"][:4]
    colw = cm(8.6)
    pos = [(MX, cm(5.6)), (MX, cm(11.4)), (W - MX - colw, cm(5.6)), (W - MX - colw, cm(11.4))]
    for i, it in enumerate(items):
        x, y = pos[i]
        right = i >= 2
        al = PP_ALIGN.LEFT if right else PP_ALIGN.RIGHT
        nx = x + cm(0.55) if right else x + colw - cm(0.55)  # numer przy krawedzi zwroconej do produktu
        circle(s, nx, y + cm(0.55), cm(1.1), SAGE_200)
        txt(s, nx - cm(0.55), y, cm(1.1), cm(1.1), "%02d" % (i + 1), 12, color=INK, font=BODY_XB,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        tw = colw
        tsize = bd.fit_size(max(it["title"].split(), key=len), 34, 20, tw, DISPLAY)
        lines = bd.wrap_lines(it["title"], tsize, tw, DISPLAY)
        txt(s, x, y + cm(1.45), tw, len(lines) * tsize * 12700, lines, tsize, color=INK, font=DISPLAY,
            align=al, line=tsize)
        txt(s, x, y + cm(1.6) + len(lines) * tsize * 12700, tw, cm(1.6), it.get("text", ""), 15, color=MUTED,
            align=al, line=21)


def f_flavor(deck, spec):
    """Slajd jednego smaku: tlo w odcieniu owocu, duza nazwa, twarde dane z karty, paczka + drobne owoce."""
    tint, deep = spec.get("tint", "FBEDEA"), spec.get("deep", "C43D46")
    s = deck.new_slide(bg=tint if BLOBS else PAPER)
    deck.page += 1
    key = "pack_" + spec.get("key", "smak")
    soft_card_or_blob(s, cm(24.3), cm(9.9), cm(16.5), spec.get("blob", "FFFFFF"), 71 + len(spec["name"]), "!!blob")
    product_scene(s, spec.get("image"), cm(24.3), cm(9.8), cm(12.6), spec.get("props", []), rot=spec.get("rot", 4),
                  key=key)
    logo(s, MX, cm(1.3), cm(1.9))
    y = cm(4.6)
    txt(s, MX, y, cm(10), cm(0.8), spec.get("kicker", "Smak").upper(), 12, color=deep, font=BODY_XB, spacing=200)
    y += cm(0.8)
    tsize = bd.fit_size(max(spec["name"].split(), key=len), 88, 44, cm(14.5), DISPLAY)
    lines = bd.wrap_lines(spec["name"], tsize, cm(14.5), DISPLAY)
    named(txt(s, MX, y, cm(15), len(lines) * tsize * 12700, lines, tsize, color=INK, font=DISPLAY,
              line=tsize * 0.96), "!!title")
    y += len(lines) * tsize * 0.96 * 12700 + cm(0.5)
    if spec.get("text"):
        n = len(bd.wrap_lines(spec["text"], 18, int(cm(13.5) * 0.96), BODY))
        txt(s, MX, y, cm(13.5), n * 26 * 12700, spec["text"], 18, color=MUTED, line=26)
        y += n * 26 * 12700 + cm(0.8)
    cw, g = cm(4.3), cm(0.35)
    for i, f in enumerate(spec.get("facts", [])[:3]):
        x = MX + i * (cw + g)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, cm(3.0), "FFFFFF" if BLOBS else CARD, radius=0.14)
        vs = bd.fit_size(f["value"], 30, 18, cw - cm(0.9), DISPLAY)
        txt(s, x + cm(0.45), y + cm(0.4), cw - cm(0.9), cm(1.3), f["value"], vs, color=deep, font=DISPLAY)
        txt(s, x + cm(0.45), y + cm(1.65), cw - cm(0.9), cm(1.2), f["label"], 12, color=MUTED, line=16)
    if spec.get("ean"):
        txt(s, MX, H - cm(1.05), cm(12), cm(0.6), "EAN " + spec["ean"], 10.5, color=MUTED)
    txt(s, W - MX - cm(1.5), H - cm(1.05), cm(1.5), cm(0.6), "%02d" % (deck.page + 1), 10.5, color=MUTED,
        font=BODY_SB, align=PP_ALIGN.RIGHT)


BUILDERS = {"cover_split": f_cover_split, "product_hero": f_product_hero, "flavor": f_flavor,
            "section": f_section, "skus": f_skus, "segments": f_segments, "cover": f_cover, "features": f_features, "hero_stat": f_hero_stat, "compare": f_compare,
            "split": f_split, "bars": f_bars, "reasons": f_reasons, "end": f_end}


def main():
    spec_path = sys.argv[1]
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    base = os.path.dirname(os.path.abspath(spec_path))

    def resolve(o, key=None):
        if isinstance(o, dict):
            return {k: resolve(v, k) for k, v in o.items()}
        if isinstance(o, list):
            return [resolve(v, key if key == "props" else None) for v in o]
        if key in ("path", "image", "props") and isinstance(o, str) and not os.path.isabs(o):
            return os.path.join(base, o)
        return o

    spec = resolve(spec)
    set_theme(spec.get("theme", "fresh"))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, spec.get("output", "prezentacja-fresh.pptx"))
    deck = Fresh(spec)
    for sl in spec["slides"]:
        n0 = len(deck.prs.slides)
        BUILDERS[sl["type"]](deck, sl)
        # Morph na kazdym slajdzie - lagodne przejscia; wylaczenie: "morph": false (globalnie lub na slajdzie)
        new = deck.prs.slides[n0] if len(deck.prs.slides) > n0 else None
        if new is not None and spec.get("morph", True) and sl.get("morph", True):
            add_morph(new)
    deck.finish(out)
    print("OK", out, len(spec["slides"]), "slajdow")


if __name__ == "__main__":
    main()
