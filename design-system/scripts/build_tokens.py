# -*- coding: utf-8 -*-
"""Generator formatów z JEDNEGO źródła: tokens/tokens.json.

    python build_tokens.py                      # generuje wszystko (tokens.css, tokens_qt.py, themes/*)
    python build_tokens.py --check              # kontrast par tekst/tło (WCAG); kod 1 przy błędzie
    python build_tokens.py --copy-to <katalog>  # po generowaniu kopiuje tokens.css do katalogu aplikacji
    python build_tokens.py --resizer <plik>     # porównuje klucze motywu z app/themes/__init__.py Photo Resizera
                                                 (tylko odczyt - niczego tam nie zapisuje)

Web:  <link rel="stylesheet" href="tokens.css">  -> zmienne --dk-* na :root i [data-theme="dobra-kaloria"]
Qt:   from tokens_qt import T; qss = SZABLON.format(**T)   (QSS nie zna zmiennych - wartości wstawiamy szablonem)
Motywy dla istniejących aplikacji (nakładki, nie przebudowa): themes/photo-resizer, themes/dam
"""
import json
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
          ("layout", "layout", "układ"))


def load():
    return json.load(open(SRC, encoding="utf8"))


def resolve(d):
    """Płaska mapa nazwa -> wartość; {ref} rozwija do prymitywu albo innego tokenu (np. {space.8})."""
    prim = d["color"]["primitive"]
    flat = {}
    for k, v in prim.items():
        flat["color-" + k] = v
    for group, short, _ in GROUPS:
        for k, v in d[group].items():
            flat["%s-%s" % (short, k)] = v
    for k, v in d["color"]["semantic"].items():
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


def css(d, prim):
    p = d["meta"]["prefix"]
    out = ["/* Design system %s %s (%s) - PLIK GENEROWANY z tokens.json (scripts/build_tokens.py). Nie edytuj ręcznie. */"
           % (d["meta"]["name"], d["meta"]["version"], d["meta"]["date"]),
           ':root, [data-theme="dobra-kaloria"] {']
    out.append("  /* kolory - prymitywy */")
    for k, v in prim.items():
        out.append("  --%s-%s: %s;" % (p, k, v))
    out.append("  /* kolory - role (tych używaj w komponentach) */")
    for k, v in d["color"]["semantic"].items():
        m = re.fullmatch(r"\{([a-z0-9-]+)\}", v)
        out.append("  --%s-color-%s: %s;" % (p, k, "var(--%s-%s)" % (p, m.group(1)) if m else v))
    for group, short, title in GROUPS:
        out.append("  /* %s */" % title)
        for k, v in d[group].items():
            m = re.fullmatch(r"\{([a-z0-9.-]+)\}", str(v))
            val = "var(--%s-%s)" % (p, m.group(1).replace(".", "-")) if m else v
            out.append("  --%s-%s-%s: %s;" % (p, short, k, val))
    out.append("}")
    dark = d["color"].get("semantic-dark")
    if dark:  # motyw ciemny: te same role, wartości z leśnej zieleni
        out.append('[data-theme="dobra-kaloria-ciemny"] {')
        out.append("  color-scheme: dark;")
        for k, v in dark.items():
            m = re.fullmatch(r"\{([a-z0-9-]+)\}", v)
            out.append("  --%s-color-%s: %s;" % (p, k, "var(--%s-%s)" % (p, m.group(1)) if m else v))
        out.append("}")
    return "\n".join(out) + "\n"


def qt(d, flat):
    lines = ['# -*- coding: utf-8 -*-',
             '"""Tokeny %s %s dla Qt/QSS - PLIK GENEROWANY z tokens.json. Użycie: QSS_SZABLON.format(**T)."""'
             % (d["meta"]["name"], d["meta"]["version"]), "T = {"]
    for k, v in flat.items():
        lines.append('    "%s": %r,' % (k.replace("-", "_"), v))
    lines.append("}")
    dark = d["color"].get("semantic-dark", {})
    lines.append("T_DARK = {  # motyw ciemny: role kolorów (nazwy jak w T)")
    for k, v in dark.items():
        lines.append('    "color_%s": %r,' % (k.replace("-", "_"), d["color"]["primitive"].get(v.strip("{}"), v)))
    lines.append("}")
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


def tokens_md(d, flat, prim):
    """Tabele wartości do czytania przez człowieka i AI - zawsze zgodne z tokens.json."""
    p = d["meta"]["prefix"]
    o = ["# Tokeny %s %s" % (d["meta"]["name"], d["meta"]["version"]), "",
         "PLIK GENEROWANY z `tokens.json` (`scripts/build_tokens.py`). Zasady użycia: `../DESIGN_SYSTEM.md`.", "",
         "## Kolory - role (tych używaj)", "", "| Rola | Zmienna CSS | Wartość | Prymityw |", "|---|---|---|---|"]
    for k, v in d["color"]["semantic"].items():
        o.append("| %s | `--%s-color-%s` | `%s` | %s |" % (k, p, k, flat["color-" + k], v.strip("{}")))
    o += ["", "## Kolory - prymitywy", "", "| Nazwa | Zmienna CSS | Wartość |", "|---|---|---|"]
    for k, v in prim.items():
        o.append("| %s | `--%s-%s` | `%s` |" % (k, p, k, v))
    o += ["", "## Kontrast (WCAG)", "", "| Tekst | Tło | Kontrast | Minimum | Zastosowanie |", "|---|---|---|---|---|"]
    for fg, bg, need, what in PAIRS:
        o.append("| %s | %s | %.2f:1 | %.1f:1 | %s |" % (fg, bg, contrast(flat["color-" + fg], flat["color-" + bg]), need, what))
    for group, short, title in GROUPS:
        o += ["", "## %s" % (title[0].upper() + title[1:]), "", "| Nazwa | Zmienna CSS | Wartość |", "|---|---|---|"]
        for k, v in d[group].items():
            val = flat["%s-%s" % (short, k)]
            src = " (= %s)" % str(v).strip("{}") if str(v).startswith("{") else ""
            o.append("| %s | `--%s-%s-%s` | `%s`%s |" % (k, p, short, k, val, src))
    return "\n".join(o) + "\n"


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# pary (tekst, tło, minimalny kontrast, opis)
PAIRS = [("text", "bg", 4.5, "tekst na tle"), ("text", "surface", 4.5, "tekst na karcie"),
         ("text-muted", "bg", 4.5, "tekst pomocniczy na tle"), ("text-muted", "surface", 4.5, "tekst pomocniczy na karcie"),
         ("label", "bg", 3.0, "etykieta (tylko >=14 px bold)"), ("label", "surface", 3.0, "etykieta na karcie"),
         ("brand", "bg", 4.5, "zielony tekst/link na tle"), ("brand", "brand-soft", 4.5, "zielony na jasnej zieleni"),
         ("on-brand", "brand", 4.5, "biały na zieleni"), ("on-cta", "cta", 4.5, "tekst na żółtym przycisku"),
         ("on-inverse", "inverse-bg", 4.5, "biały na brązie (toast)"), ("on-inverse", "danger", 4.5, "biały na czerwieni"),
         ("warning-text", "warning-bg", 4.5, "ostrzeżenie"), ("field-border", "bg", 3.0, "ramka pola"),
         ("switch-off", "bg", 3.0, "wyłączony przełącznik")]
# pary w motywie Photo Resizera (klucz tekstu, klucz tła, minimum)
RESIZER_PAIRS = [("@FG_TEXT@", "@BG_WINDOW@", 4.5), ("@FG_TEXT@", "@BG_PANEL@", 4.5), ("@FG_TEXT@", "@BG_INPUT@", 4.5),
                 ("@FG_TEXT@", "@BG_HOVER@", 4.5), ("@FG_MUTED@", "@BG_WINDOW@", 4.5), ("@FG_MUTED@", "@BG_PANEL@", 4.5),
                 ("@FG_MUTED@", "@BG_HOVER@", 4.5), ("@FG_ACCENT@", "@BG_PANEL@", 4.5), ("@FG_ACCENT@", "@BG_WINDOW@", 4.5),
                 ("#FFFFFF", "@ACCENT@", 4.5), ("#FFFFFF", "@ACCENT_HOVER@", 4.5),
                 ("@UPDATE_TOAST_INSTALL_TEXT@", "@UPDATE_TOAST_INSTALL_BG@", 4.5),
                 ("@UPDATE_TOAST_TEXT@", "@UPDATE_TOAST_BG@", 4.5), ("@OVERLAY_ABORT_COLOR@", "@OVERLAY_ABORT_HOVER_BG@", 3.0)]


def check(d, flat, ref):
    bad = 0
    prim = d["color"]["primitive"]
    dk = {k: prim.get(v.strip("{}"), v) for k, v in d["color"].get("semantic-dark", {}).items()}
    for fg, bg, need, what in PAIRS:
        if dk:
            r = contrast(dk[fg], dk[bg])
            bad += 0 if r >= need else 1
            print("%s %5.2f:1 (min %.1f)  CIEMNY %-14s na %-12s %s" % ("OK " if r >= need else "ZLE", r, need, fg, bg, what))
    for fg, bg, need, what in PAIRS:
        r = contrast(flat["color-" + fg], flat["color-" + bg])
        ok = r >= need
        bad += 0 if ok else 1
        print("%s %5.2f:1 (min %.1f)  %-14s na %-12s %s" % ("OK " if ok else "ZLE", r, need, fg, bg, what))
    rz = {k: ref(v) for k, v in d["themes"]["photo-resizer"]["tokens"].items()}
    for fg, bg, need in RESIZER_PAIRS:
        a, b = rz.get(fg, fg), rz.get(bg, bg)
        r = contrast(a, b)
        ok = r >= need
        bad += 0 if ok else 1
        print("%s %5.2f:1 (min %.1f)  motyw photo-resizer: %s na %s" % ("OK " if ok else "ZLE", r, need, fg, bg))
    dm = {k: ref(v) for k, v in d["themes"]["dam"]["tokens"].items()}
    for fg, bg, need in (("--dam-text", "--dam-bg", 4.5), ("--dam-text", "--dam-surface", 4.5),
                         ("--dam-text-muted", "--dam-bg", 4.5), ("--dam-text-muted", "--dam-surface-sunken", 4.5)):
        r = contrast(dm[fg], dm[bg])
        ok = r >= need
        bad += 0 if ok else 1
        print("%s %5.2f:1 (min %.1f)  motyw dam: %s na %s" % ("OK " if ok else "ZLE", r, need, fg, bg))
    return bad


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
    if "--resizer" in sys.argv:
        sys.exit(compare_resizer(d, sys.argv[sys.argv.index("--resizer") + 1]))
    write(os.path.join(TOK, "tokens.css"), css(d, prim))
    write(os.path.join(TOK, "tokens_qt.py"), qt(d, flat))
    write(os.path.join(TOK, "tokens.md"), tokens_md(d, flat, prim))
    write(os.path.join(THEMES, "photo-resizer", "dobra_kaloria.py"), theme_resizer(d, ref))
    write(os.path.join(THEMES, "dam", "dam-theme-dobra-kaloria.css"), theme_dam(d, ref))
    print("OK tokens.css (%d zmiennych), tokens_qt.py, themes/photo-resizer, themes/dam; wersja %s"
          % (len(flat), d["meta"]["version"]))
    if "--copy-to" in sys.argv:
        dst = os.path.abspath(sys.argv[sys.argv.index("--copy-to") + 1])
        print("kopiuję tokens.css do:", dst)
        if not os.path.isdir(dst):
            sys.exit("katalog docelowy nie istnieje - przerywam")
        shutil.copy2(os.path.join(TOK, "tokens.css"), os.path.join(dst, "tokens.css"))
    sys.exit(1 if check(d, flat, ref) else 0)


if __name__ == "__main__":
    main()
