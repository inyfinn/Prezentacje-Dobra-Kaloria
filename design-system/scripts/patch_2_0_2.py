# -*- coding: utf-8 -*-
"""Jednorazowa łatka 2.0.1 -> 2.0.2 (uwagi usera z 06.10.2026 do DAM 2.5.4, zrzuty 28-34): S14 minimum poziomów,
S15 ciemne elementy w ciemnej zieleni i cienki fokus. Idempotentna."""
import io
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rd(rel):
    return io.open(os.path.join(BASE, rel), encoding="utf8", newline="").read()


def wr(rel, s):
    io.open(os.path.join(BASE, rel), "w", encoding="utf8", newline="").write(s)


ITEM = (
    ".dk-tile .dk-tile { background: var(--dk-color-surface-4); }\n"
    "/* S14: lista pozycji na bieli - kontener BEZ tła, szare są dopiero pozycje (kafle listy) */\n"
    ".dk-item { background: var(--dk-color-surface-1); border-radius: var(--dk-radius-md); padding: var(--dk-space-4) var(--dk-space-5); }\n"
    ".dk-panel .dk-item { background: var(--dk-color-surface-2); }\n"
)
for rel in ("preview/sklep.html", "components.md"):
    s = rd(rel)
    nl = "\r\n" if "\r\n" in s else "\n"
    if ".dk-item {" not in s:
        s = s.replace(".dk-tile .dk-tile { background: var(--dk-color-surface-4); }" + nl, ITEM.replace("\n", nl), 1)
    wr(rel, s)

s = rd("preview/sklep.html")
if 'class="dk-item"' not in s:
    s = s.replace('      <div class="row">\n        <span class="dk-iconlabel">',
                  '      <div class="stack" style="max-width:360px"><h3 class="dk-h3">Powiadomienia</h3>'
                  '<div class="dk-item"><b class="dk-h3" style="font-size:18px">Projekty po dopracowaniu</b><div class="row" style="gap:8px;margin-top:6px">'
                  '<span class="dk-tag" style="background:var(--dk-color-tag-1-bg);color:var(--dk-color-tag-1-fg)">Marketing</span>'
                  '<span class="dk-muted">31.10.2025</span></div></div>'
                  '<div class="dk-item"><b class="dk-h3" style="font-size:18px">Akceptacja</b><div class="row" style="gap:8px;margin-top:6px">'
                  '<span class="dk-tag" style="background:var(--dk-color-tag-2-bg);color:var(--dk-color-tag-2-fg)">Miksy</span>'
                  '<span class="dk-muted">06.11.2025</span></div></div></div>\n'
                  '      <div class="row">\n        <span class="dk-iconlabel">', 1)
    wr("preview/sklep.html", s)

r = rd("tokens/READY-2.0.0.txt")
if "S14" not in r:
    nl = "\r\n" if "\r\n" in r else "\n"
    add = (
        "  S14 MINIMUM POZIOMÓW (2.0.2; user 06.10 o DAM: „niepotrzebne zagnieżdżenie teł w środku, po co beżowe, jak może być\n"
        "      białe… powiadomienia mają tło kafelków, a nie muszą, dopiero kafelki wewnątrz powinny mieć szarość”).\n"
        "      Kontener nie dostaje tła, jeśli wystarczy biel. Lista pozycji (powiadomienia, kategorie, wyniki, materiały):\n"
        "      kontener BIAŁY bez tła, szare (L1) są dopiero pozycje. Szary panel tylko wtedy, gdy grupuje kilka różnych\n"
        "      białych kart lub pól (formularz, podsumowanie - jak w koszyku). Etykiety i wartości metadanych bez tła.\n"
        "      Beż/ecru wolno dopiero na prawdziwym 3. poziomie (kafel w białej karcie w szarym panelu) - w większości\n"
        "      widoków nie występuje wcale. Żadnych fioletów ani obcych kolorów z motywu bazowego.\n"
        "  S15 CIEMNE = CIEMNA ZIELEŃ, FOKUS CIENKI (2.0.2; user: „są tak ciemne zielone, że niemalże czarne… NIE MA takich\n"
        "      cholernie grubych obrysów… więcej życia i koloru”). Elementy ciemne (pływający przycisk pomocy, licznik,\n"
        "      podpowiedź, toast, pasek górny) mają tło inverse-bg = #00642E z białym tekstem - nie brąz i nie czerń.\n"
        "      Fokus pola: obrys 1 px brand + poświata shadow-focus-field (3 px, przezroczysta zieleń); nigdy gruby ciemny\n"
        "      pierścień. Aktywny segment, aktywny filtr, zaznaczony tag: zielone wypełnienie brand z białym tekstem.\n"
    ).replace("\n", nl)
    r = r.replace("  ZOSTAJE z wcześniejszych rund:", add + "  ZOSTAJE z wcześniejszych rund:", 1)
    r = r.replace("(S1-S13; S13 dodana w 2.0.1)", "(S1-S15; S13 dodana w 2.0.1, S14-S15 w 2.0.2)", 1)
    r = r.replace("inverse-bg #222222", "inverse-bg #00642E", 1)
    wr("tokens/READY-2.0.0.txt", r)

z = rd("ZALECENIA-USERA.md")
if "S14" not in z:
    nl = "\r\n" if "\r\n" in z else "\n"
    z = z.rstrip() + (
        "\n\n## 06.10.2026 — szczegółowa krytyka DAM 2.5.4 (7 zrzutów): za ciężko, za dużo teł i obrysów\n\n"
        "> „To jest zbyt ponure, zbyt ciężkie. Za duże obrysy na przyciskach. Kompletnie brzydkie. Niepotrzebne zagnieżdżenie\n"
        "> teł w środku, po co beżowe, jak może być białe, rozumiesz? Niepotrzebne tła dla »tło«. Tagi są okropnie brzydkie.\n"
        "> Powiadomienia mają tło kafelków, a nie muszą, dopiero kafelki wewnątrz, jak »projekty po dopracowaniu«, powinny\n"
        "> mieć szarość. Tak jak w DOBRA KALORIA. A cały SZUKAJ, za grube i za ciężkie obrysy, coś okropnego. Tak samo\n"
        "> w eksplorerze, wszystko nie wygląda żywo i ładnie, jak w dobrakaloria.pl, tylko staro, jak SEPIA. I gdzieniegdzie\n"
        "> kolory się nie zgadzają, dalej są jeszcze jakieś fiolety, albo jakieś paseczki dziwne. Wlej tu więcej życia\n"
        "> i koloru. Specjalnie pokazałem Ci tamte screenshoty, żebyś wiedział, że raczej przeważa biały kolor, NIE MA aż tak\n"
        "> dużo BEŻOWYCH kolorów. Są tak ciemne zielone, że niemalże czarne. NIE MA takich cholernie grubych obrysów.”\n\n"
        "- **S14 minimum poziomów** (DS 2.0.2): kontener bez tła, jeśli wystarczy biel; w liście szare są dopiero pozycje;\n"
        "  szary panel tylko dla grupy różnych białych kart lub pól; metadane bez tła; beż dopiero na 3. poziomie; zero fioletów.\n"
        "- **S15 ciemne = ciemna zieleń, fokus cienki:** ciemne elementy `#00642E` zamiast brązu i czerni; fokus pola = 1 px\n"
        "  zieleni + miękka poświata, nigdy gruby ciemny pierścień; aktywny segment i zaznaczony tag zielone.\n"
        "- Przepis listy: `.dk-item` w `components.md` rozdz. 25 i `preview/sklep.html`.\n"
    ).replace("\n", nl)
    wr("ZALECENIA-USERA.md", z)

t = rd("tokens/tokens.json")
t = t.replace('"inverse-bg": "{ink-900}"', '"inverse-bg": "{green-900}"')
t = t.replace('"version": "2.0.1"', '"version": "2.0.2"', 1)
wr("tokens/tokens.json", t)
print("2.0.2: S14, S15 dopisane; inverse-bg = green-900")
