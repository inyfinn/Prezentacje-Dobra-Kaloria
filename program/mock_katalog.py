# -*- coding: utf-8 -*-
"""Katalog slajdów dla atrapy okna (src\\ui\\mock-katalog.js) - z prawdziwego silnika, żeby zrzuty w przeglądarce
pokazywały te same grupy i opisy co program. Uruchom po zmianie EXTRA/SECTIONS w engine.py:
    python mock_katalog.py "<folder produktu>"
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src", "app"))
import engine  # noqa: E402

r = engine.analyze(sys.argv[1])
data = {"sekcje": r["sekcje"], "grupy": r["grupy"], "presety": r["presety"]}
out = os.path.join(HERE, "src", "ui", "mock-katalog.js")
with open(out, "w", encoding="utf8", newline="\n") as f:
    f.write("/* PLIK GENEROWANY (WORK\\mock_katalog.py) - katalog slajdów tylko dla atrapy okna w przeglądarce. */\n")
    f.write("window.MOCK_KATALOG = %s;\n" % json.dumps(data, ensure_ascii=False))
print("ok", out, len(data["sekcje"]), "slajdów")
