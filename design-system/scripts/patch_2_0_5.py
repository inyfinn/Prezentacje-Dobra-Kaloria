# -*- coding: utf-8 -*-
"""Jednorazowa łatka 2.0.4 -> 2.0.5 (user 06.10.2026: „TAGI… powinny być jednak kolorki… różnicuj kolory”,
„szczególnie to przyciemnienie brązowe” podoba się). Tagi jasnych stylów w 8 różnych barwach, rola scrim. Idempotentna."""
import io
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "tokens", "tokens.json")

d = json.load(open(SRC, encoding="utf8"))
# barwy OKLCH: zieleń 152, limonka 125, żółty 95, pomarańcz 60, czerwień 25, róż 355, morski 190, niebieski 240 (bez fioletu)
HUES = [0, -27, -57, -92, -127, -157, 38, 88]
for key in ("program", "krem-jasny", "zielen-jasny"):
    d["ladder"]["variants"][key]["tag_hue"] = 152
    d["ladder"]["variants"][key]["tag_offsets"] = HUES
d["tags"]["light"] = {"bg": [0.93, 0.06], "border": [0.86, 0.075], "fg": [0.40, 0.11]}
d["tags"]["note"] = (
    "Tag k (1..count): hue = tag_hue wariantu + tag_offsets[k-1] (stopnie OKLCH). Od 2.0.5 style jasne mają 8 RÓŻNYCH barw "
    "(zieleń, limonka, żółty, pomarańcz, czerwień, róż, morski, niebieski; bez fioletu) - user: „powinny być jednak kolorki, "
    "różnicuj kolory”. Tag to samo wypełnienie (tag-N-bg) i tekst (tag-N-fg), BEZ obrysu (S13); tag-N-border zostaje w tokenach "
    "dla stylów ciemnych i wstecznej zgodności. Jedna grupa tagów (smak, typ, opakowanie, autor, język, marka…) = jedna barwa. "
    "Metka pełna (cena, licznik, znaczek) = brand + on-brand."
)
d["shadow"]["scrim"] = "rgba(59,42,32,.55)"
d["meta"]["version"] = "2.0.5"
json.dump(d, open(SRC, "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=2)
open(SRC, "a", encoding="utf8", newline="\n").write("\n")

p = os.path.join(BASE, "tokens", "READY-2.0.0.txt")
r = io.open(p, encoding="utf8", newline="").read()
if "S17" not in r:
    nl = "\r\n" if "\r\n" in r else "\n"
    add = (
        "  S17 TAGI KOLOROWE, PRZYCIEMNIENIE CIEPŁE (2.0.5; user 06.10: „TAGI DK, Kulki, DOYPACK… zbyt brzydkie. Powinny być\n"
        "      jednak kolorki… niepotrzebne są te obrysy w tagach… Różnicuj kolory” oraz „szczególnie to przyciemnienie\n"
        "      brązowe” - podoba się). Tagi mają 8 różnych barw tag-1..8: zieleń, limonka, żółty, pomarańcz, czerwień, róż,\n"
        "      morski, niebieski (bez fioletu); samo wypełnienie + tekst, bez obrysu. Jedna GRUPA tagów = jedna barwa\n"
        "      (np. marka zielona, kategoria pomarańczowa, opakowanie żółte, język niebieski, smak różowy, autor morski,\n"
        "      opis limonkowy, podkategoria czerwona) - w filtrach i na kartach ta sama grupa ma tę samą barwę.\n"
        "      Zaznaczony tag: pełna zieleń brand z białym tekstem. Licznik „+16”: #F5F5F5.\n"
        "      Przyciemnienie tła pod oknem dialogowym: shadow-scrim rgba(59,42,32,.55) (ciepły brąz) - zostaje.\n"
    ).replace("\n", nl)
    r = r.replace("  S16 OSTRZEŻENIE BEZ BRĄZU", add + "  S16 OSTRZEŻENIE BEZ BRĄZU", 1)
    r = r.replace("  tagi tag-1..8: odcienie zieleni (hue 120-184), tag-1 #D6F0DC / #28603A / #B2D7BB",
                  "  tagi tag-1..8: 8 różnych barw (S17), wartości w tokens.md; bez obrysu", 1)
    io.open(p, "w", encoding="utf8", newline="").write(r)

z = os.path.join(BASE, "ZALECENIA-USERA.md")
t = io.open(z, encoding="utf8", newline="").read()
if "S17" not in t:
    nl = "\r\n" if "\r\n" in t else "\n"
    t = t.rstrip() + (
        "\n\n## 06.10.2026 — DAM 2.5.4, widok Wizualizacji: tagi kolorowe, mniej brązu\n\n"
        "> „Już jest tak COZY, jest już dużo lepiej, szczególnie to przyciemnienie brązowe, ale dalej za dużo brązu. Dalej jest\n"
        "> zdecydowanie za dużo brązu, a TAGI »DK, Kulki, DOYPACK« itp. to jest zbyt brzydkie. Powinny być jednak kolorki. Bo\n"
        "> aktualnie to jest niesamowicie brzydkie. Niepotrzebne są te obrysy w tagach… Różnicuj kolory.”\n\n"
        "- **S17** (DS 2.0.5): tagi w 8 różnych barwach, samo wypełnienie bez obrysu, jedna grupa tagów = jedna barwa.\n"
        "- Ciepłe brązowe przyciemnienie pod oknem dialogowym user pochwalił — zostaje (`shadow-scrim`).\n"
        "- UCHYLA zasadę z 30.09 „tagi tylko delikatnie zmieniają barwę” oraz zielone odcienie tagów z 2.0.0.\n"
    ).replace("\n", nl)
    io.open(z, "w", encoding="utf8", newline="").write(t)
print("2.0.5: tagi kolorowe, scrim")
