# -*- coding: utf-8 -*-
"""Generator formatów z JEDNEGO źródła: tokens/tokens.json.

    python build_tokens.py                      # generuje wszystko (tokens.css, tokens_qt.py, tokens.md, themes/*)
    python build_tokens.py --check              # kontrast i drabina (WCAG + skoki jasności); kod 1 przy błędzie
    python build_tokens.py --copy-to <katalog>  # po generowaniu kopiuje tokens.css do katalogu aplikacji
    python build_tokens.py --resizer <plik>     # porównuje klucze motywu z app/themes/__init__.py Photo Resizera
                                                 (tylko odczyt - niczego tam nie zapisuje)
    python build_tokens.py --ladder             # wypisuje drabinę i tagi każdego wariantu (hex, L, L*, dL)

Web:  <link rel="stylesheet" href="tokens.css">  -> zmienne --dk-* na :root i [data-theme="..."]
Qt:   from tokens_qt import T; qss = SZABLON.format(**T)   (QSS nie zna zmiennych - wartości wstawiamy szablonem)

Od 1.4.0 (drabina i tagi):
  * sekcja "ladder" w tokens.json: dla każdego wariantu (program, krem-jasny, zielen-jasny, zielen-ciemny, krem-ciemny)
    parametry L0, dL, hue, chroma -> poziomy surface-0..4, border-subtle-0..4, on-surface-0..4 (OKLCH),
  * sekcja "tags": tag-1..8 (-bg, -fg, -border) z odcienia stylu (tag_hue) przesuniętego o offsets,
  * role mogą wskazywać poziom wariantu: "{@surface-1}" (alias; stare nazwy bg/surface/surface-hover działają dalej).
"""
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
TOK = os.path.join(BASE, "tokens")
THEMES = os.path.join(BASE, "themes")
SRC = os.path.join(TOK, "tokens.json")
GROUPS = (("font", "font", "czcionki"), ("font-size", "fs", "rozmiary tekstu"),
          ("line-height", "lh", "interlinie"), ("space", "space", "odstępy (siatka 4 px)"),
          ("radius", "radius", "promienie"), ("shadow", "shadow", "cienie (podbarwione brązem)"),
          ("motion", "motion", "ruch"), ("control", "control", "kontrolki"),
          ("layout", "layout", "układ"),
          ("qt", "qt", "Qt: skala tekstu i odstępy z programu (QSS px)"))
LEVEL_NAMES = ("tło okna", "kontener, sekcja, karta", "rubryka, pole, karta w karcie",
               "element w polu: chip, wiersz, okno w oknie", "nakładka: menu, podpowiedź, modal nad modalem")
# selektor CSS i nazwa słownika Qt dla każdego wariantu drabiny
VARIANT_OUT = {
    "program": (None, "T"),
    "krem-jasny": ('[data-theme="dobra-kaloria-krem-jasny"]', "T_KREM_JASNY"),
    "zielen-jasny": ('[data-theme="dobra-kaloria-zielen-jasny"]', "T_ZIELEN_JASNY"),
    "zielen-ciemny": ('[data-theme="dobra-kaloria-zielen-ciemny"], [data-theme="dobra-kaloria-ciemny"]', "T_DARK"),
    "krem-ciemny": ('[data-theme="dobra-kaloria-krem-ciemny"], [data-theme="dobra-kaloria-krem"]', "T_KREM"),
}


# ---------------------------------------------------------------- kolor: sRGB <-> OKLCH, kontrast, L*
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def to_oklch(h):
    r, g, b = [_lin(x) for x in hex_rgb(h)]
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b2 = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, b2), math.degrees(math.atan2(b2, a)) % 360


def _oklch_lin(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)


def oklch_hex(L, C, H):
    """OKLCH -> #RRGGBB; poza sRGB zmniejsza C o 0.001 (odcień i jasność zostają)."""
    L = min(max(L, 0.0), 1.0)
    while True:
        rgb = _oklch_lin(L, C, H)
        if all(-1e-4 <= x <= 1.0001 for x in rgb) or C <= 0:
            break
        C = max(C - 0.001, 0.0)
    return "#" + "".join("%02X" % round(min(max(_gam(min(max(x, 0.0), 1.0)), 0.0), 1.0) * 255) for x in rgb)


def lum(h):
    c = [_lin(x) for x in hex_rgb(h)]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def lstar(h):
    y = lum(h)
    return 116 * (y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116) - 16


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- drabina i tagi
def tag_offsets(d, v):
    """1.6.0: wariant może mieć własne 'tag_offsets' (zestawy beżowe: tylko ciepłe odcienie); inaczej tags.offsets."""
    return v.get("tag_offsets", d["tags"]["offsets"])


def ladder_variant(d, key):
    """Poziomy L0..L4, ramki i tagi wariantu -> słownik {nazwa roli: hex}."""
    v = d["ladder"]["variants"][key]
    n = d["ladder"]["levels"]
    sgn = -1 if v["mode"] == "light" else 1
    out = {}
    for i in range(n if "surfaces" in v else 0):  # 2.0.0: drabina jawna (wartości ze zrzutów sklepu), bez wzoru
        out["surface-%d" % i] = v["surfaces"][i]
        out["border-subtle-%d" % i] = v["borders"][i]
    for i in range(0 if "surfaces" in v else n):
        L = v["L0"] + sgn * i * v["dL"]
        H = (v["hue"] + i * v.get("hue_step", 0)) % 360  # 1.5.0: opcjonalne ocieplenie głębszych poziomów
        for name, LL in (("surface", L), ("border-subtle", L + sgn * v["border_dL"])):
            C = min(v["chroma_k"] * ((1 - LL) if v["mode"] == "light" else LL), v["chroma_max"])
            out["%s-%d" % (name, i)] = oklch_hex(LL, C, H)
    t = d["tags"]
    spec = t[v["mode"]]
    tdl = v.get("tag_dL", 0)  # 1.5.0: przesunięcie L tła i ramki tagów wariantu (krem ciemny: ciemniej)
    offs = tag_offsets(d, v)
    for k in range(t["count"]):
        H = (v["tag_hue"] + offs[k]) % 360
        bg = oklch_hex(spec["bg"][0] + tdl, spec["bg"][1], H)
        fL = spec["fg"][0]
        fg = oklch_hex(fL, spec["fg"][1], H)
        while contrast(fg, bg) < t["min_contrast"] and 0 < fL < 1:
            fL += -0.01 if v["mode"] == "light" else 0.01
            fg = oklch_hex(fL, spec["fg"][1], H)
        out["tag-%d-bg" % (k + 1)] = bg
        out["tag-%d-fg" % (k + 1)] = fg
        out["tag-%d-border" % (k + 1)] = oklch_hex(spec["border"][0] + tdl, spec["border"][1], H)
    return out


def ladder_desc(v):
    if "surfaces" in v:
        return "jawna (sklep): " + " > ".join(v["surfaces"])
    return "L0 %.3f, dL %.3f (OKLCH), %s" % (v["L0"], v["dL"], "jasny: głębiej = ciemniej" if v["mode"] == "light"
                                             else "ciemny: głębiej = jaśniej")


def roles(d, key):
    """Role wariantu (hex): zestaw 'roles' z tokens.json + drabina + tagi; {@x} -> poziom tego wariantu."""
    v = d["ladder"]["variants"][key]
    prim = d["color"]["primitive"]
    lad = ladder_variant(d, key)
    out = {}
    for k, val in d["color"][v["roles"]].items():
        m = re.fullmatch(r"\{(@?)([a-z0-9-]+)\}", val)
        out[k] = (lad[m.group(2)] if m.group(1) else prim[m.group(2)]) if m else val
    for i in range(d["ladder"]["levels"]):
        lad["on-surface-%d" % i] = out["text"]
    out.update(lad)
    return out


def ladder_keys(d):
    n = d["ladder"]["levels"]
    ks = []
    for i in range(n):
        ks += ["surface-%d" % i, "border-subtle-%d" % i, "on-surface-%d" % i]
    for k in range(d["tags"]["count"]):
        ks += ["tag-%d-bg" % (k + 1), "tag-%d-fg" % (k + 1), "tag-%d-border" % (k + 1)]
    return ks


# ---------------------------------------------------------------- wejście
def load():
    return json.load(open(SRC, encoding="utf8"))


def resolve(d):
    """Płaska mapa nazwa -> wartość (wariant 'program' = :root); {ref} rozwija do prymitywu, tokenu albo poziomu."""
    prim = d["color"]["primitive"]
    flat = {}
    for k, v in prim.items():
        flat["color-" + k] = v
    for group, short, _ in GROUPS:
        for k, v in d[group].items():
            flat["%s-%s" % (short, k)] = v
    for k, v in roles(d, "program").items():
        flat["color-" + k] = v

    def ref(val):
        m = re.fullmatch(r"\{([a-z0-9.-]+)\}", str(val))
        if not m:
            return val
        name = m.group(1)
        if name in prim:
            return prim[name]
        key = name.replace(".", "-")
        if key in flat:
            return ref(flat[key])
        raise KeyError("nieznane odwołanie %s" % val)
    return {k: ref(v) for k, v in flat.items()}, prim, ref


# ---------------------------------------------------------------- wyjścia
def _css_val(p, v):
    m = re.fullmatch(r"\{(@?)([a-z0-9-]+)\}", v)
    if not m:
        return v
    return "var(--%s-%s%s)" % (p, "color-" if m.group(1) else "", m.group(2))


def css(d, prim):
    p = d["meta"]["prefix"]
    out = ["/* Design system %s %s (%s) - PLIK GENEROWANY z tokens.json (scripts/build_tokens.py). Nie edytuj ręcznie. */"
           % (d["meta"]["name"], d["meta"]["version"], d["meta"]["date"]),
           "/* Drabina powierzchni: --dk-color-surface-0 (tło okna) ... -4 (nakładka); tagi: --dk-color-tag-N-bg/-fg/-border. */",
           ':root, [data-theme="dobra-kaloria"] {', "  color-scheme: light;"]
    out.append("  /* kolory - prymitywy */")
    for k, v in prim.items():
        out.append("  --%s-%s: %s;" % (p, k, v))

    def role_block(key):
        v = d["ladder"]["variants"][key]
        lad = roles(d, key)
        lines = ["  /* drabina %s: %s */" % (key, ladder_desc(v))]
        for k in ladder_keys(d):
            val = "var(--%s-color-text)" % p if k.startswith("on-surface-") else lad[k]
            lines.append("  --%s-color-%s: %s;" % (p, k, val))
        lines.append("  /* kolory - role (tych używaj w komponentach) */")
        for k, val in d["color"][v["roles"]].items():
            lines.append("  --%s-color-%s: %s;" % (p, k, _css_val(p, val)))
        return lines
    out += role_block("program")
    for group, short, title in GROUPS:
        out.append("  /* %s */" % title)
        for k, v in d[group].items():
            m = re.fullmatch(r"\{([a-z0-9.-]+)\}", str(v))
            val = "var(--%s-%s)" % (p, m.group(1).replace(".", "-")) if m else v
            out.append("  --%s-%s-%s: %s;" % (p, short, k, val))
    out.append("}")
    for key, (sel, _) in VARIANT_OUT.items():
        if not sel:
            continue
        out.append("%s {" % sel)
        out.append("  color-scheme: %s;" % d["ladder"]["variants"][key]["mode"])
        out += role_block(key)
        out.append("}")
    return "\n".join(out) + "\n"


def qt(d, flat):
    lines = ['# -*- coding: utf-8 -*-',
             '"""Tokeny %s %s dla Qt/QSS - PLIK GENEROWANY z tokens.json. Użycie: QSS_SZABLON.format(**T).'
             % (d["meta"]["name"], d["meta"]["version"]),
             "",
             "T              program (biała kartka) - pełny zestaw: kolory, odstępy, czcionki, drabina, tagi",
             "T_KREM_JASNY   Dobra Kaloria 2 · krem, jasny   (role + drabina + tagi; nazwy jak w T)",
             "T_ZIELEN_JASNY Dobra Kaloria 1 · zieleń, jasny",
             "T_DARK         Dobra Kaloria 1 · zieleń, ciemny",
             "T_KREM         Dobra Kaloria 2 · krem, ciemny",
             "Drabina: color_surface_0 (tło okna) .. color_surface_4 (nakładka), color_border_subtle_N, color_on_surface_N.",
             "Tagi: color_tag_1_bg / _fg / _border .. color_tag_8_*.",
             '"""', "T = {"]
    for k, v in flat.items():
        lines.append('    "%s": %r,' % (k.replace("-", "_"), v))
    lines.append("}")
    for key, (_, name) in VARIANT_OUT.items():
        if name == "T":
            continue
        lines.append("%s = {  # %s (%s): role kolorów, drabina, tagi (nazwy jak w T)"
                     % (name, key, d["ladder"]["variants"][key]["roles"]))
        for k, v in roles(d, key).items():
            lines.append('    "color_%s": %r,' % (k.replace("-", "_"), v))
        lines.append("}")
    lines.append("VARIANTS = {%s}" % ", ".join('"%s": %s' % (k, n) for k, (_, n) in VARIANT_OUT.items()))
    lines.append("FONT_FILES = ['Mindset.otf', 'Lato-Regular.ttf', 'Lato-Bold.ttf']  # QFontDatabase.addApplicationFont")
    return "\n".join(lines) + "\n"


def theme_resizer(d, ref):
    t = d["themes"]["photo-resizer"]
    lines = ['# -*- coding: utf-8 -*-',
             '"""Motyw "Dobra Kaloria" dla Inyfinn Photo Resizer - PLIK GENEROWANY (design system %s %s).'
             % (d["meta"]["name"], d["meta"]["version"]),
             "Status: %s. Wdrożenie: themes/photo-resizer/README.md." % t["status"], '"""',
             "DOBRA_KALORIA = {"]
    for k, v in t["tokens"].items():
        src = "  # %s" % v[1:-1] if str(v).startswith("{") else ""
        lines.append('    "%s": "%s",%s' % (k, ref(v), src))
    lines.append("}")
    return "\n".join(lines) + "\n"


def theme_dam(d, ref):
    t = d["themes"]["dam"]
    out = ["/* Motyw \"Dobra Kaloria\" dla DAM - PLIK GENEROWANY (design system %s %s)." % (d["meta"]["name"], d["meta"]["version"]),
           "   Status: %s. Nakładka na istniejące zmienne --dam-*: komponentów nie przepisujemy," % t["status"],
           "   motywy light i dark zostają bez zmian. Wdrożenie: themes/dam/README.md. */",
           'html[data-theme="dobra-kaloria"] {', "  color-scheme: light;",
           "  background-color: var(--dam-bg, %s);" % ref(t["tokens"]["--dam-bg"])]
    for k, v in t["tokens"].items():
        src = "  /* %s */" % v[1:-1] if str(v).startswith("{") else ""
        out.append("  %s: %s;%s" % (k, ref(v), src))
    out.append("}")
    return "\n".join(out) + "\n"


def ladder_rows(d, key):
    """(poziom, hex, L oklch, L*, dL do poprzedniego, kontrast z poprzednim, tekst, pomocniczy)."""
    r = roles(d, key)
    rows, prev = [], None
    for i in range(d["ladder"]["levels"]):
        h = r["surface-%d" % i]
        L = to_oklch(h)[0]
        rows.append((i, h, L, lstar(h), (L - to_oklch(prev)[0]) if prev else None,
                     contrast(h, prev) if prev else None, contrast(r["text"], h), contrast(r["text-muted"], h),
                     r["border-subtle-%d" % i]))
        prev = h
    return rows


def tokens_md(d, flat, prim):
    """Tabele wartości do czytania przez człowieka i AI - zawsze zgodne z tokens.json."""
    p = d["meta"]["prefix"]
    o = ["# Tokeny %s %s" % (d["meta"]["name"], d["meta"]["version"]), "",
         "PLIK GENEROWANY z `tokens.json` (`scripts/build_tokens.py`). Zasady użycia: `../DESIGN_SYSTEM.md`, "
         "`../IDENTYFIKACJA-WIZUALNA.md`.", "",
         "## Drabina powierzchni L0-L4 (od 1.4.0)", "",
         "L = jasność OKLCH (0-100), L* = CIELAB. dL = zmiana L względem poziomu niżej. "
         "Kontrast: tekst i tekst pomocniczy na danym poziomie (WCAG).", ""]
    for key, v in d["ladder"]["variants"].items():
        sel = VARIANT_OUT[key][0] or ':root, [data-theme="dobra-kaloria"]'
        o += ["### %s" % v["name"], "", "`%s` · %s · %s" % (sel, v["mode"], ladder_desc(v)), "",
              "| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for i, h, L, ls, dl, cr, ct, cm, bs in ladder_rows(d, key):
            o.append("| L%d %s | `--%s-color-surface-%d` | `%s` | %.1f | %.1f | %s | %s | %.2f | %.2f | `%s` |"
                     % (i, v.get("level_names", LEVEL_NAMES)[i], p, i, h, L * 100, ls, "-" if dl is None else "%+.1f" % (dl * 100),
                        "-" if cr is None else "%.3f" % cr, ct, cm, bs))
        o.append("")
    t = d["tags"]
    o += ["## Tagi (od 1.4.0)", "",
          "Wzór: hue = `tag_hue` wariantu + przesunięcie `%s` (stopnie OKLCH; od 1.6.0 wariant może mieć własne "
          "`tag_offsets` - zestawy beżowe mają tylko ciepłe odcienie, zob. kolumnę Hue). Tło L %.3f C %.3f / ramka L %.3f C %.3f / "
          "tekst L %.3f C %.3f w jasnym; w ciemnym tło L %.3f C %.3f / ramka L %.3f C %.3f / tekst L %.3f C %.3f. "
          "Tekst dociągany o 0.01 L do kontrastu >= %.1f." % (
              t["offsets"], *t["light"]["bg"], *t["light"]["border"], *t["light"]["fg"],
              *t["dark"]["bg"], *t["dark"]["border"], *t["dark"]["fg"], t["min_contrast"]), "",
          "| Wariant | Tag | Hue | Tło | Tekst | Ramka | Kontrast |", "|---|---|---|---|---|---|---|"]
    for key, v in d["ladder"]["variants"].items():
        r = roles(d, key)
        for k in range(t["count"]):
            n = k + 1
            o.append("| %s | tag-%d | %.0f | `%s` | `%s` | `%s` | %.2f:1 |" % (
                key, n, (v["tag_hue"] + tag_offsets(d, v)[k]) % 360, r["tag-%d-bg" % n], r["tag-%d-fg" % n],
                r["tag-%d-border" % n], contrast(r["tag-%d-fg" % n], r["tag-%d-bg" % n])))
    o += ["", "## Kolory - role programu (tych używaj)", "", "| Rola | Zmienna CSS | Wartość | Źródło |", "|---|---|---|---|"]
    for k, v in d["color"]["semantic"].items():
        o.append("| %s | `--%s-color-%s` | `%s` | %s |" % (k, p, k, flat["color-" + k], v.strip("{}")))
    o += ["", "## Kolory - prymitywy", "", "| Nazwa | Zmienna CSS | Wartość |", "|---|---|---|"]
    for k, v in prim.items():
        o.append("| %s | `--%s-%s` | `%s` |" % (k, p, k, v))
    o += ["", "## Kontrast (WCAG) - program", "", "| Tekst | Tło | Kontrast | Minimum | Zastosowanie |", "|---|---|---|---|---|"]
    for fg, bg, need, what in PAIRS:
        o.append("| %s | %s | %.2f:1 | %.1f:1 | %s |" % (fg, bg, contrast(flat["color-" + fg], flat["color-" + bg]), need, what))
    for group, short, title in GROUPS:
        o += ["", "## %s" % (title[0].upper() + title[1:]), "", "| Nazwa | Zmienna CSS | Wartość |", "|---|---|---|"]
        for k, v in d[group].items():
            val = flat["%s-%s" % (short, k)]
            src = " (= %s)" % str(v).strip("{}") if str(v).startswith("{") else ""
            o.append("| %s | `--%s-%s-%s` | `%s`%s |" % (k, p, short, k, val, src))
    return "\n".join(o) + "\n"


# pary (tekst, tło, minimalny kontrast, opis)
PAIRS = [("text", "bg", 4.5, "tekst na tle"), ("text", "surface", 4.5, "tekst na karcie"),
         ("text-muted", "bg", 4.5, "tekst pomocniczy na tle"), ("text-muted", "surface", 4.5, "tekst pomocniczy na karcie"),
         ("label", "surface-0", 4.5, "etykieta na tle (od 1.6.0 >= 4.5)"), ("label", "surface-1", 4.5, "etykieta na karcie (od 1.6.0 >= 4.5)"),
         ("brand", "bg", 4.5, "zielony tekst/link na tle"), ("brand", "brand-soft", 4.5, "zielony na jasnej zieleni"),
         ("on-brand", "brand", 4.5, "biały na zieleni"), ("on-cta", "cta", 4.5, "tekst na żółtym przycisku"),
         ("on-inverse", "inverse-bg", 4.5, "biały na brązie (toast)"), ("on-inverse", "danger", 4.5, "biały na czerwieni"),
         ("danger", "bg", 4.5, "czerwony tekst błędu na tle"), ("danger", "surface", 4.5, "czerwony tekst błędu na karcie"),
         ("warning-text", "warning-bg", 4.5, "ostrzeżenie"), ("field-border", "bg", 3.0, "ramka pola"),
         # od 1.6.0 switch-off to tor (jasny), widoczność wyłączonego przełącznika niesie jego obrys (switch-off-border)
         ("switch-off-border", "bg", 3.0, "obrys wyłączonego przełącznika"),
         # --- 1.6.0 kontrolki i akcent (G1-G6)
         ("check-mark", "check-bg", 4.5, "znak checkboxa/radio na jasnym wnętrzu"),
         ("check-border", "check-bg", 3.0, "obrys checkboxa na wnętrzu"),
         ("check-border", "surface-0", 3.0, "obrys checkboxa na tle"), ("check-border", "surface-1", 3.0, "obrys checkboxa na karcie"),
         ("accent", "surface-0", 4.5, "akcent (link, tytuł) na L0"), ("accent", "surface-1", 4.5, "akcent na L1"),
         ("accent", "surface-2", 4.5, "akcent na L2"), ("accent", "surface-3", 4.5, "akcent na L3"),
         ("on-accent", "accent", 4.5, "tekst na akcencie"),
         ("step-active-text", "step-active-bg", 4.5, "tekst aktywnego kroku"),
         ("step-idle-text", "surface-0", 4.5, "tekst nieaktywnego kroku"),
         ("btn2-text", "btn2-bg", 4.5, "tekst przycisku drugorzędnego"),
         ("btn2-text", "btn2-hover-bg", 4.5, "tekst przycisku drugorzędnego (hover)"),
         ("btn2-border", "btn2-bg", 3.0, "obrys przycisku drugorzędnego"),
         ("slider-fill", "slider-track", 3.0, "wypełnienie suwaka na torze"),
         ("slider-thumb-border", "slider-thumb", 3.0, "obrys uchwytu suwaka"),
         ("switch-on", "surface-0", 3.0, "włączony przełącznik na tle"), ("switch-on", "surface-1", 3.0, "włączony przełącznik na karcie"),
         ("switch-off-border", "surface-0", 3.0, "obrys wyłączonego przełącznika na tle"),
         ("switch-knob", "switch-on", 3.0, "gałka na włączonym torze"),
         ("icon", "icon-bg", 3.0, "ikona na kółku"), ("focus", "surface-0", 3.0, "obrys fokusa"),
         ("on-solid", "solid", 4.5, "tekst na pełnym kaflu (KPI, suma, LIVE, przycisk pomocy) - 2.0.9")]
# 2.0.0: bez zieleni poza brand* zostaje tylko DK2 krem ciemny (decyzja usera 05.10); style jasne = sklep, zieleń jest akcentem
NO_GREEN = ("krem-ciemny",)
GREEN_CHROMA, GREEN_H = 0.04, (105.0, 200.0)
# pary w motywie Photo Resizera (klucz tekstu, klucz tła, minimum)
RESIZER_PAIRS = [("@FG_TEXT@", "@BG_WINDOW@", 4.5), ("@FG_TEXT@", "@BG_PANEL@", 4.5), ("@FG_TEXT@", "@BG_INPUT@", 4.5),
                 ("@FG_TEXT@", "@BG_HOVER@", 4.5), ("@FG_MUTED@", "@BG_WINDOW@", 4.5), ("@FG_MUTED@", "@BG_PANEL@", 4.5),
                 ("@FG_MUTED@", "@BG_HOVER@", 4.5), ("@FG_ACCENT@", "@BG_PANEL@", 4.5), ("@FG_ACCENT@", "@BG_WINDOW@", 4.5),
                 ("#FFFFFF", "@ACCENT@", 4.5), ("#FFFFFF", "@ACCENT_HOVER@", 4.5),
                 ("@UPDATE_TOAST_INSTALL_TEXT@", "@UPDATE_TOAST_INSTALL_BG@", 4.5),
                 ("@UPDATE_TOAST_TEXT@", "@UPDATE_TOAST_BG@", 4.5), ("@OVERLAY_ABORT_COLOR@", "@OVERLAY_ABORT_HOVER_BG@", 3.0)]
# drabina: minimalny i maksymalny skok jasności sąsiadów (OKLCH L) oraz minimalna różnica L4-L0
LADDER_DL_MIN, LADDER_DL_MAX, LADDER_SPAN_MIN = 0.015, 0.045, 0.06


def check(d, flat, ref, quiet=False):
    bad, total = 0, 0

    def rep(ok, line):
        nonlocal bad, total
        total += 1
        bad += 0 if ok else 1
        if not quiet or not ok:
            print(("OK  " if ok else "ZLE ") + line)
    for key, v in d["ladder"]["variants"].items():
        r = roles(d, key)
        tag = key.upper()[:13]
        for fg, bg, need, what in PAIRS:
            c = contrast(r[fg], r[bg])
            rep(c >= need, "%5.2f:1 (min %.1f)  %-13s %-14s na %-12s %s" % (c, need, tag, fg, bg, what))
        rows = ladder_rows(d, key)
        for i, h, L, ls, dl, cr, ct, cm, bs in rows:
            rep(ct >= 4.5, "%5.2f:1 (min 4.5)  %-13s text na surface-%d" % (ct, tag, i))
            rep(cm >= 4.5, "%5.2f:1 (min 4.5)  %-13s text-muted na surface-%d" % (cm, tag, i))
            if i <= 1:  # etykieta beżowa tylko na L0-L1 (ladder.rules.label)
                cl = contrast(r["label"], h)
                rep(cl >= 3.0, "%5.2f:1 (min 3.0)  %-13s label na surface-%d" % (cl, tag, i))
            lk = "brand" if i <= 3 else "brand-hover"  # na nakładce L4 link w brand-hover (ladder.rules.brand)
            cb = contrast(r[lk], h)
            rep(cb >= 4.5, "%5.2f:1 (min 4.5)  %-13s %s (link) na surface-%d" % (cb, tag, lk, i))
            cbs = contrast(bs, h)
            rep(cbs >= 1.12, "%5.3f:1 (min 1.12) %-13s border-subtle-%d widoczna na surface-%d" % (cbs, tag, i, i))
            if dl is not None and "surfaces" in v:  # drabina jawna: poziomy sąsiednie muszą się różnić
                rep(cr >= 1.03, "%5.3f:1 (min 1.03) %-13s surface-%d odróżnia się od surface-%d" % (cr, tag, i, i - 1))
            elif dl is not None:
                sgn = -1 if v["mode"] == "light" else 1
                ok = LADDER_DL_MIN <= dl * sgn <= LADDER_DL_MAX
                rep(ok, "dL %+.3f (%.3f..%.3f, kierunek %s)  %-13s surface-%d -> surface-%d, kontrast sąsiadów %.3f"
                    % (dl, LADDER_DL_MIN, LADDER_DL_MAX, "w dół" if sgn < 0 else "w górę", tag, i - 1, i, cr))
            if not v.get("white_ok"):
                rep(h.upper() != "#FFFFFF", "%-13s surface-%d %s nie jest czystą bielą" % (tag, i, h))
        if "surfaces" in v:  # 2.0.0 "sklep": biel jako tło, biała karta w panelu, tekst neutralny, akcent zielony
            rep(r["surface-0"].upper() == "#FFFFFF", "%-13s tło okna (surface-0) %s jest białe" % (tag, r["surface-0"]))
            rep(r["surface-2"].upper() == "#FFFFFF", "%-13s karta w panelu (surface-2) %s jest biała" % (tag, r["surface-2"]))
            for name in ("text", "text-muted", "label", "heading"):
                C = to_oklch(r[name])[1]
                rep(C <= 0.02, "tekst neutralny  %-13s %-10s %s (C %.3f, max 0.02)" % (tag, name, r[name], C))
            for name in ("brand", "accent", "heading-accent", "icon", "check-mark", "focus"):
                _, C, H = to_oklch(r[name])
                rep(C > GREEN_CHROMA and GREEN_H[0] <= H <= GREEN_H[1],
                    "akcent zielony   %-13s %-14s %s (C %.3f, H %.0f)" % (tag, name, r[name], C, H))
            for name in ("heading", "heading-accent"):
                for i in range(d["ladder"]["levels"]):
                    c = contrast(r[name], r["surface-%d" % i])
                    rep(c >= 4.5, "%5.2f:1 (min 4.5)  %-13s %s na surface-%d" % (c, tag, name, i))
        else:
            span = abs(rows[-1][2] - rows[0][2])
            rep(span >= LADDER_SPAN_MIN, "L4-L0 = %.3f (min %.2f)  %-13s nakładka nie zlewa się z tłem" % (span, LADDER_SPAN_MIN, tag))
        for k in range(d["tags"]["count"]):
            n = k + 1
            c = contrast(r["tag-%d-fg" % n], r["tag-%d-bg" % n])
            rep(c >= 4.5, "%5.2f:1 (min 4.5)  %-13s tag-%d tekst na tle tagu" % (c, tag, n))
        if key in NO_GREEN:  # G2/G3: poza brand* i on-brand żadna rola ani tag nie jest zielone
            for name, val in r.items():
                if name.startswith("brand") or name == "on-brand":
                    continue
                _, C, H = to_oklch(val)
                green = C > GREEN_CHROMA and GREEN_H[0] <= H <= GREEN_H[1]
                rep(not green, "bez zieleni  %-13s %-22s %s (C %.3f, H %.0f)" % (tag, name, val, C, H))
    rz ={k: ref(v) for k, v in d["themes"]["photo-resizer"]["tokens"].items()}
    for fg, bg, need in RESIZER_PAIRS:
        a, b = rz.get(fg, fg), rz.get(bg, bg)
        c = contrast(a, b)
        rep(c >= need, "%5.2f:1 (min %.1f)  motyw photo-resizer (szkic 1.2): %s na %s" % (c, need, fg, bg))
    dm = {k: ref(v) for k, v in d["themes"]["dam"]["tokens"].items()}
    for fg, bg, need in (("--dam-text", "--dam-bg", 4.5), ("--dam-text", "--dam-surface", 4.5),
                         ("--dam-text-muted", "--dam-bg", 4.5), ("--dam-text-muted", "--dam-surface-sunken", 4.5)):
        c = contrast(dm[fg], dm[bg])
        rep(c >= need, "%5.2f:1 (min %.1f)  motyw dam (szkic 1.2): %s na %s" % (c, need, fg, bg))
    print("kontrola: %d sprawdzeń, błędów: %d" % (total, bad))
    return bad


def print_ladder(d):
    for key, v in d["ladder"]["variants"].items():
        print("== %s (%s, %s)" % (key, v["mode"], ladder_desc(v)))
        for i, h, L, ls, dl, cr, ct, cm, bs in ladder_rows(d, key):
            print("  L%d %s  L=%.1f L*=%.1f dL=%s  sasiad %s  tekst %.2f  pomocn %.2f  ramka %s"
                  % (i, h, L * 100, ls, "  -  " if dl is None else "%+.1f" % (dl * 100),
                     "  -  " if cr is None else "%.3f" % cr, ct, cm, bs))
        r = roles(d, key)
        print("  tagi: " + "  ".join("%s/%s" % (r["tag-%d-bg" % n], r["tag-%d-fg" % n]) for n in range(1, d["tags"]["count"] + 1)))


def compare_resizer(d, path):
    """Czy motyw ma dokładnie te klucze, których używa aplikacja (tylko odczyt pliku aplikacji)."""
    src = open(path, encoding="utf8").read()
    m = re.search(r'"light"\s*:\s*\{(.*?)\n\s*\},', src, re.S)
    if not m:
        print("ZLE nie znalazłem słownika \"light\" w %s" % path)
        return 1
    theirs = set(re.findall(r'"(@[A-Z_]+@)"\s*:', m.group(1)))
    ours = set(d["themes"]["photo-resizer"]["tokens"])
    miss, extra = sorted(theirs - ours), sorted(ours - theirs)
    print("motyw photo-resizer: aplikacja ma %d kluczy, motyw %d; brakuje: %s; zbędne: %s"
          % (len(theirs), len(ours), miss or "-", extra or "-"))
    return 1 if (miss or extra) else 0


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf8", newline="\n").write(text)


def main():
    d = load()
    flat, prim, ref = resolve(d)
    if "--check" in sys.argv:
        sys.exit(1 if check(d, flat, ref) else 0)
    if "--ladder" in sys.argv:
        print_ladder(d)
        sys.exit(0)
    if "--resizer" in sys.argv:
        sys.exit(compare_resizer(d, sys.argv[sys.argv.index("--resizer") + 1]))
    write(os.path.join(TOK, "tokens.css"), css(d, prim))
    write(os.path.join(TOK, "tokens_qt.py"), qt(d, flat))
    write(os.path.join(TOK, "tokens.md"), tokens_md(d, flat, prim))
    write(os.path.join(THEMES, "photo-resizer", "dobra_kaloria.py"), theme_resizer(d, ref))
    write(os.path.join(THEMES, "dam", "dam-theme-dobra-kaloria.css"), theme_dam(d, ref))
    print("OK tokens.css (%d zmiennych :root), tokens_qt.py, tokens.md, themes/photo-resizer, themes/dam; wersja %s"
          % (len(flat), d["meta"]["version"]))
    if "--copy-to" in sys.argv:
        dst = os.path.abspath(sys.argv[sys.argv.index("--copy-to") + 1])
        print("kopiuję tokens.css do:", dst)
        if not os.path.isdir(dst):
            sys.exit("katalog docelowy nie istnieje - przerywam")
        shutil.copy2(os.path.join(TOK, "tokens.css"), os.path.join(dst, "tokens.css"))
    sys.exit(1 if check(d, flat, ref, quiet=True) else 0)


if __name__ == "__main__":
    main()
