# -*- coding: utf-8 -*-
"""Testy katalogu slajdow szablonu (assets/katalog-szablonu.json, references/katalog-szablonu.md).

    python -m pytest -p no:cacheprovider test_katalog.py -q

Bez PowerPointa, bez modeli AI, bez plikow poza skillem.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_dk  # noqa: E402
import make_template  # noqa: E402

with open(os.path.join(SK, "assets", "katalog-szablonu.json"), encoding="utf-8") as _f:
    KAT = json.load(_f)
SL = KAT["slajdy"]
TPL = make_template.spec("shop")["slides"]
POLA = {"nr", "id", "typ", "nazwa", "grupa", "uzyj_gdy", "nie_gdy", "miesci", "pola", "uklad", "slowa_kluczowe", "w_krotkim"}


def test_wersja_i_65_pozycji():
    assert KAT["wersja"] == 1
    assert len(SL) == len(TPL) == 65


def test_nr_ciagle_id_zgodne():
    assert [s["nr"] for s in SL] == list(range(1, 66))
    assert all(s["id"] == "t%02d" % s["nr"] for s in SL)


def test_klucze_i_niepuste_teksty():
    for s in SL:
        assert set(s) == POLA, s["nr"]
        for k in ("nazwa", "grupa", "uzyj_gdy", "nie_gdy", "miesci", "pola"):
            assert isinstance(s[k], str) and s[k].strip(), (s["nr"], k)
        assert s["uklad"] is None or (isinstance(s["uklad"], str) and s["uklad"].strip()), s["nr"]
        assert s["slowa_kluczowe"] and all(isinstance(w, str) and w for w in s["slowa_kluczowe"]), s["nr"]


def test_typ_istnieje_w_builderach_i_zgadza_sie_z_szablonem():
    for s in SL:
        assert s["typ"] in build_dk.BUILDERS, (s["nr"], s["typ"])
        assert s["typ"] == TPL[s["nr"] - 1]["type"], s["nr"]


def test_nazwy_unikalne():
    nazwy = [s["nazwa"] for s in SL]
    assert len(set(nazwy)) == len(nazwy)


def test_ksztalty_wskazuja_istniejace_id():
    ids = {s["id"] for s in SL}
    assert len(KAT["ksztalty"]) >= 18
    for k in KAT["ksztalty"]:
        assert set(k) == {"ksztalt", "wez", "uklad", "regula", "przyklad"}, k
        assert k["ksztalt"].strip() and k["wez"], k
        assert set(k["wez"]) <= ids, k


def test_ksztalty_obejmuja_wymagane_tematy():
    tekst = " | ".join(k["ksztalt"] for k in KAT["ksztalty"]).lower()
    for slowo in ("teza", "hasła", "lista", "fakty", "liczba-bohater", "porównanie", "kroki", "cytat", "zdjęcie",
                  "obrazy", "etykieta", "wniosek", "tabela", "wykres", "pytanie", "akapit", "przekładka", "okładka",
                  "zakończenie"):
        assert slowo in tekst, slowo


def test_markdown_ma_wszystkie_slajdy_i_ksztalty():
    with open(os.path.join(SK, "references", "katalog-szablonu.md"), encoding="utf-8") as f:
        md = f.read()
    assert md.index("## 1.") < md.index("## 2.")  # tabela decyzyjna na gorze
    for s in SL:
        assert "| %d | %s%s |" % (s["nr"], "★ " if s["w_krotkim"] else "", s["nazwa"]) in md, s["nr"]
    for k in KAT["ksztalty"]:
        assert k["ksztalt"] in md, k["ksztalt"]


def test_markdown_zgodny_z_json():
    import katalog_md
    with open(katalog_md.MD_PATH, encoding="utf-8", newline="") as f:
        assert f.read() == katalog_md.render(KAT), "uruchom: python katalog_md.py"


def test_krotki_szablon_7_slajdow_zgodny_z_katalogiem():
    krotkie = [s for s in SL if s["w_krotkim"]]
    assert len(krotkie) == 7 and all(isinstance(s["w_krotkim"], bool) for s in SL)
    assert sorted(s["nr"] for s in krotkie) == sorted(make_template.KROTKI_NR)
    k = make_template.spec_krotki("shop")
    assert len(k["slides"]) == 7 and not k["sections"]
    assert [sl["type"] for sl in k["slides"]] == [SL[nr - 1]["typ"] for nr in make_template.KROTKI_NR]
    for sl, nr in zip(k["slides"], make_template.KROTKI_NR):
        assert sl["type"] in build_dk.BUILDERS and not sl.get("hidden") and "section" not in sl
        assert sl.get("title") == TPL[nr - 1].get("title"), nr  # ten sam wzor co w pelnym
    assert "Dopisz" in k["slides"][-1]["contact"]


def test_pelny_szablon_nadal_65_slajdow():
    assert len(make_template.spec("shop")["slides"]) == 65
