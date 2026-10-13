# -*- coding: utf-8 -*-
"""Testy polecenia.py: python -m pytest -p no:cacheprovider test_polecenia.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polecenia  # noqa: E402

STARE = ["zamiany zdań na hasła", "wyjmowania liczb", "karta-artykuł w Lato", "Mindset tylko w tytule", "tylko czytelność"]
DANE = {"cel_slajdy": 25, "widoczne": 43, "wszystkie": 43}


def _tekst(cel, pliki):
    return "\n".join(polecenia.polecenie_ai(cel, DANE, pliki=pliki))


def test_agent_ma_metode_i_pliki():
    t = _tekst("wiernie", True)
    for s in ("dopracowanie.md", "katalog-szablonu.md", "poprawki", "PLAKAT", "verify.ps1", "spec_konwersja.json"):
        assert s in t, s
    pts = polecenia.polecenie_ai("wiernie", DANE, pliki=True)
    assert pts[0].startswith("ZANIM COKOLWIEK POPRAWISZ")      # P1 stoi PRZED punktami wspólnymi
    assert pts[1].startswith("SLAJD TO PLAKAT")
    assert pts[-1].startswith("RAPORT PO POLSKU")


def test_domyslnie_pliki_true_zgodnosc_wsteczna():
    assert polecenia.polecenie_ai("wiernie") == polecenia.polecenie_ai("wiernie", None, pliki=True)


def test_czat_bez_plikow_nie_ma_nic_z_plikow():
    for cel in polecenia.POLECENIA:
        t = _tekst(cel, False)
        for s in ("verify", "render", "spec_konwersja", "dopracowanie.md", "katalog-szablonu.md", "build_dk"):
            assert s not in t, (cel, s)


def test_czat_wiernie_ma_7_punktow_wspolnych():
    pts = polecenia.polecenie_ai("wiernie", DANE, pliki=False)
    assert len(pts) == 7
    assert [p.split(".")[0].split(":")[0].split(" ")[0] for p in pts][:2] == ["SLAJD", "HASŁOWANIE"]


def test_zadna_wersja_nie_ma_starych_zdan_ani_nierozwinietego_formatu():
    for cel in polecenia.POLECENIA:
        for pliki in (True, False):
            t = _tekst(cel, pliki)
            assert "%(" not in t, (cel, pliki)
            for s in STARE:
                assert s not in t, (cel, pliki, s)
    # także surowe teksty w słowniku (np. opis celu)
    surowo = json.dumps(polecenia.POLECENIA, ensure_ascii=False)
    for s in STARE:
        assert s not in surowo, s


def test_rozwin_i_skroc_dostaja_dopisek_i_zestaw_agenta():
    for cel in ("rozwin", "skroc"):
        c = polecenia.POLECENIA[cel]
        assert c["polecenie"][-1] == polecenia.DOPISEK_ROZWIN_SKROC
        assert c["polecenie_pliki"] == [polecenia.P1, polecenia.P2, polecenia.P4, polecenia.P5, polecenia.P6]
        ag = polecenia.polecenie_ai(cel, DANE, pliki=True)
        assert ag[0] == polecenia.P1 and ag[-1] == polecenia.P6 and len(ag) == len(c["polecenie"]) + 5
        assert polecenia.polecenie_ai(cel, DANE, pliki=False) == [p % DANE if "%(" in p else p for p in c["polecenie"]]


def test_skroc_podstawia_liczby_i_nie_wywraca_sie_bez_danych():
    assert "około 25 slajdów (teraz widocznych jest 43 z 43)" in _tekst("skroc", False)
    assert "około ? slajdów" in "\n".join(polecenia.polecenie_ai("skroc"))


def test_nieznany_cel_to_wiernie():
    assert polecenia.polecenie_ai("cokolwiek", DANE) == polecenia.polecenie_ai("wiernie", DANE)


def test_tabela_ksztaltow_z_katalogu():
    t = polecenia.tabela_ksztaltow()
    if not polecenia._katalog():
        return
    linie = t.splitlines()
    assert len(linie) == 14 and len(polecenia.tabela_ksztaltow(10).splitlines()) == 10
    assert all(" -> wzór: " in l and l.endswith(")") for l in linie)
    kat = polecenia._katalog()
    z_s = [k for k in kat["ksztalty"] if polecenia._RE_S.search(k.get("regula") or "")]
    # najpierw kształty z regułą S (robi je automat), potem reszta
    assert linie[0].startswith(z_s[0]["ksztalt"] + " -> wzór: ")
    assert all(l.split(" -> wzór: ")[0] in {k["ksztalt"] for k in z_s} for l in linie[:min(len(z_s), 14)])
    assert len(polecenia.tabela_ksztaltow(0)) == 0


def test_tabela_pusta_gdy_brak_katalogu(tmp_path, monkeypatch):
    monkeypatch.setattr(polecenia, "HERE", str(tmp_path / "scripts"))
    assert polecenia.tabela_ksztaltow() == ""


def test_role_slajdu_uklad():
    sl = {"type": "uklad", "kicker": "Rozdział", "title": "Tytuł", "rows": [
        {"k": "cols", "items": [
            {"blocks": [{"k": "hero", "t": "7,8%"}, {"k": "lead", "t": "Wydatki wzrosły o 7,8%,"},
                        {"k": "p", "t": "a najszybciej rośnie grupa."}]},
            {"blocks": [{"k": "icon", "name": "leaf"}, {"k": "h", "t": "Nagłówek"}, {"k": "li", "t": "punkt 1"},
                        {"k": "kv", "label": "CT:", "t": "20-35"}, {"k": "img", "image": "x.png"}]}]},
        {"k": "quote", "t": "Cytat", "author": "Autor"},
        {"k": "pics", "items": [{"image": "a.png", "caption": "podpis"}, {"image": "b.png", "caption": ""}]},
        {"k": "band", "t": "Wniosek"}, {"k": "small", "t": "Źródło: GUS"}], "source": "Źródło: GUS 2025"}
    r = polecenia.role_slajdu(sl)
    assert r[:2] == [("etykieta nad tytułem", "Rozdział"), ("tytuł", "Tytuł")]
    assert ("liczba", "7,8%") in r and ("hasło", "Wydatki wzrosły o 7,8%,") in r and ("dopisek", "a najszybciej rośnie grupa.") in r
    assert ("nagłówek", "Nagłówek") in r and ("punkt", "punkt 1") in r and ("etykieta", "CT: 20-35") in r
    assert r.count(("obraz", "")) == 2   # img w karcie i wiersz pics; ikona nie daje linii
    assert ("cytat", "Cytat") in r and ("podpis", "Autor") in r and ("podpis", "podpis") in r and ("wniosek", "Wniosek") in r
    assert r[-1] == ("podpis", "Źródło: GUS 2025")
    assert polecenia.format_roli("obraz", "") == "[obraz]" and polecenia.format_roli("hasło", "x") == "[hasło] x"


def test_role_slajdu_inne_typy_i_smieci():
    assert polecenia.role_slajdu({"type": "section", "title": "x"}) == []
    assert polecenia.role_slajdu(None) == [] and polecenia.role_slajdu({"type": "uklad"}) == []
    assert polecenia.role_slajdu({"type": "uklad", "rows": [{"k": "nieznany", "t": "x"}, "śmieć"]}) == []
