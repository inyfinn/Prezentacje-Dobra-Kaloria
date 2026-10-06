# -*- coding: utf-8 -*-
"""Jednorazowa łatka 2.0.0 -> 2.0.1: reguła S13 „budżet obrysów” (uwaga usera z 06.10.2026 po obejrzeniu DAM).
Tagi i pigułki bez obrysu, nowy przycisk cichy (.dk-btn--quiet) i przełącznik segmentowy (.dk-seg). Idempotentna."""
import io
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rd(rel):
    return io.open(os.path.join(BASE, rel), encoding="utf8", newline="").read()


def wr(rel, s):
    io.open(os.path.join(BASE, rel), "w", encoding="utf8", newline="").write(s)


QUIET = (
    ".dk-btn--block { display: flex; width: 100%; }\n"
    "/* S13: przycisk cichy (trzeciorzędny) - samo wypełnienie, bez obrysu; w grupie najwyżej 1 główny i 1 z obrysem, reszta cicha */\n"
    ".dk-btn--quiet { background: var(--dk-color-icon-bg); color: var(--dk-color-text); }\n"
    ".dk-panel .dk-btn--quiet, .dk-panel .dk-iconbtn { background: var(--dk-color-surface-2); }\n"
    ".dk-card .dk-btn--quiet, .dk-card .dk-iconbtn, .dk-tile .dk-btn--quiet { background: var(--dk-color-icon-bg); }\n"
    ".dk-btn--quiet:hover, .dk-panel .dk-btn--quiet:hover, .dk-card .dk-btn--quiet:hover { background: var(--dk-color-brand-soft); }\n"
    "/* S13: przełącznik segmentowy (filtry „Wszystko / Produkty”) - aktywny zielony, nieaktywny cichy, bez obrysów */\n"
    ".dk-seg { display: inline-flex; gap: 4px; }\n"
    ".dk-seg > button { min-height: 36px; padding: 0 var(--dk-space-4); border: 0; border-radius: var(--dk-radius-btn); cursor: pointer;\n"
    "  background: var(--dk-color-icon-bg); color: var(--dk-color-text); font: 700 14px/1 var(--dk-font-text); }\n"
    ".dk-panel .dk-seg > button { background: var(--dk-color-surface-2); }\n"
    ".dk-seg > button[aria-pressed=\"true\"] { background: var(--dk-color-brand); color: var(--dk-color-on-brand); }\n"
)
for rel in ("preview/sklep.html", "components.md"):
    s = rd(rel)
    nl = "\r\n" if "\r\n" in s else "\n"
    s = s.replace("font: 700 13px/1 var(--dk-font-text); border: 1px solid; }",
                  "font: 700 13px/1 var(--dk-font-text); border: 0; }   /* S13: tag bez obrysu */")
    if ".dk-btn--quiet" not in s:
        s = s.replace(".dk-btn--block { display: flex; width: 100%; }" + nl, QUIET.replace("\n", nl), 1)
    wr(rel, s)

s = rd("preview/sklep.html")
s = re.sub(r";border-color:var\(--dk-color-tag-\d-border\)", "", s)
if "dk-seg" not in s.split("</style>")[1]:
    s = s.replace('<button class="dk-btn" disabled>Niedostępne</button></div>',
                  '<button class="dk-btn dk-btn--quiet">Odśwież</button><button class="dk-btn" disabled>Niedostępne</button></div>\n'
                  '      <div class="row"><div class="dk-seg"><button aria-pressed="true">Wszystko</button><button aria-pressed="false">Produkty</button>'
                  '<button aria-pressed="false">Warianty</button></div></div>', 1)
    s = s.replace('<div class="dk-feature">',
                  '<div class="row"><div class="dk-seg"><button aria-pressed="true">Produkty</button><button aria-pressed="false">Materiały</button></div>'
                  '<button class="dk-btn dk-btn--quiet">Odśwież z dysku</button></div>\n        <div class="dk-feature">', 1)
wr("preview/sklep.html", s)

r = rd("tokens/READY-2.0.0.txt")
if "S13" not in r:
    nl = "\r\n" if "\r\n" in r else "\n"
    add = (
        "  S13 BUDŻET OBRYSÓW (2.0.1; user 06.10 o DAM: „bubble tagi wyglądają okropnie z tymi obrysami, za dużo obrysów”).\n"
        "      Obrys 1 px wolno dać TYLKO na: pole formularza, checkbox/radio, JEDEN przycisk drugorzędny w grupie przycisków,\n"
        "      białą kartę leżącą wprost na białym tle, fokus. BEZ obrysu: tagi, metki, pigułki filtrów, liczniki, panele,\n"
        "      karty w panelu, kafle, przyciski-ikony, nagłówki zwijanych sekcji. Tag = samo wypełnienie (tag-N-bg + tag-N-fg).\n"
        "      Przycisk cichy (trzeciorzędny): wypełnienie #F5F5F5 na bieli / #FFFFFF na panelu, bez obrysu, tekst #222222,\n"
        "      hover brand-soft. Przełącznik segmentowy: aktywny zielony z białym tekstem, nieaktywny jak przycisk cichy.\n"
        "      Żadnej sepii: beż tylko jako L3/L4, nigdy jako kolor obrysu, metki czy tekstu w stylach jasnych.\n"
    ).replace("\n", nl)
    r = r.replace("  ZOSTAJE z wcześniejszych rund:", add + "  ZOSTAJE z wcześniejszych rund:", 1)
    r = r.replace("REGUŁY 2.0 (S1-S12)", "REGUŁY 2.0 (S1-S13; S13 dodana w 2.0.1)", 1)
    wr("tokens/READY-2.0.0.txt", r)

z = rd("ZALECENIA-USERA.md")
if "S13" not in z:
    nl = "\r\n" if "\r\n" in z else "\n"
    z = z.rstrip() + (
        "\n\n## 06.10.2026 — po obejrzeniu DAM 2.5.4 (stary, brązowy wygląd): mniej obrysów\n\n"
        "> „…to DAM wygląda okropnie. Jak SEPIA. A te bubble tagi wyglądają okropnie z tymi obrysami, za dużo obrysów,\n"
        "> wszystko wygląda okropnie brzydko. […] w ogóle nie o to chodziło.”\n\n"
        "- **S13 budżet obrysów** (DS 2.0.1): obrys tylko na polu, checkboxie, jednym przycisku drugorzędnym w grupie, białej\n"
        "  karcie na białym tle i fokusie. Tagi, metki, pigułki filtrów, liczniki, panele, kafle, przyciski-ikony: bez obrysu.\n"
        "- **Żadnej sepii:** beż nie jest kolorem obrysu, metki ani tekstu w stylach jasnych; występuje tylko jako kafel L3/L4.\n"
        "- Przepisy: `.dk-tag` (samo wypełnienie), `.dk-btn--quiet`, `.dk-seg` w `components.md` rozdz. 25 i `preview/sklep.html`.\n"
    ).replace("\n", nl)
    wr("ZALECENIA-USERA.md", z)

t = rd("tokens/tokens.json")
t = t.replace('"version": "2.0.0"', '"version": "2.0.1"', 1)
wr("tokens/tokens.json", t)
print("2.0.1: S13 dopisana (sklep.html, components.md, READY-2.0.0.txt, ZALECENIA-USERA.md, tokens.json)")
