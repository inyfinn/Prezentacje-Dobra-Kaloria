# -*- coding: utf-8 -*-
"""Pisze references/katalog-szablonu.md z assets/katalog-szablonu.json (JSON = jedyne zrodlo, MD nie edytuj recznie).

    python katalog_md.py          # zapisuje references/katalog-szablonu.md
    python katalog_md.py --check  # kod 1, gdy MD rozjechal sie z JSON
"""
import json
import os
import sys

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(SK, "assets", "katalog-szablonu.json")
MD_PATH = os.path.join(SK, "references", "katalog-szablonu.md")


def _c(t):
    return str(t).replace("|", "/").replace("\n", " ")


def _gwiazdka(s):
    return "★ " if s.get("w_krotkim") else ""


def render(kat):
    nazwy = {s["id"]: s["nazwa"] for s in kat["slajdy"]}
    L = ["# Katalog slajdów szablonu: co do czego", "",
         "Krótki szablon dla ludzi ma 7 slajdów (oznaczone ★); program i AI korzystają z pełnego katalogu. "
         "Źródło: `assets/katalog-szablonu.json` (65 slajdów szablonu `make_template.py`). Ten plik generuje "
         "`scripts/katalog_md.py` - nie edytuj go ręcznie, zmieniaj JSON i uruchom skrypt. Agent: najpierw tabela 1 "
         "(kształt treści -> slajd), potem tabela 2 (czy slajd naprawdę pasuje: „użyj gdy”, „nie gdy”, „mieści”). "
         "Nie wymyślaj własnego układu, gdy któryś slajd pasuje. `tNN` = numer slajdu w szablonie. Reguły R / S: "
         "`konwersja-pptx.md` (2a, 2b).", "",
         "## 1. Kształt treści -> slajd szablonu", "",
         "| Kształt treści | Weź | Jak to zbudować w konwersji (`uklad`) | Reguła | Przykład |", "|---|---|---|---|---|"]
    for k in kat["ksztalty"]:
        L.append("| %s | %s | %s | %s | %s |" % (
            _c(k["ksztalt"]), ", ".join("%s %s" % (w, nazwy[w]) for w in k["wez"]), _c(k["uklad"]), _c(k["regula"]),
            _c(k["przyklad"])))
    L += ["", "## 2. Wszystkie slajdy szablonu", "",
          "| nr | Nazwa | Użyj gdy | Nie gdy | Mieści | Typ |", "|---|---|---|---|---|---|"]
    for s in kat["slajdy"]:
        L.append("| %d | %s | %s | %s | %s | `%s` |" % (s["nr"], _gwiazdka(s) + _c(s["nazwa"]), _c(s["uzyj_gdy"]), _c(s["nie_gdy"]),
                                                       _c(s["miesci"]), s["typ"]))
    L.append("")
    return "\n".join(L)


def main(argv):
    with open(JSON_PATH, encoding="utf-8") as f:
        md = render(json.load(f))
    if "--check" in argv:
        with open(MD_PATH, encoding="utf-8", newline="") as f:
            return 0 if f.read() == md else 1
    with open(MD_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print("OK", MD_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
