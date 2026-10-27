# -*- coding: utf-8 -*-
"""Testy scenariusz.py (prezentacja ze scenariusza Markdown). Bez PowerPointa i bez LLM:
    python -m pytest -p no:cacheprovider test_scenariusz.py -q
Pliki testowe (obraz, pptx) powstają w katalogu tymczasowym pytest."""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scenariusz  # noqa: E402

SC = scenariusz.MARKER + "\ntytuł: Test\n\n## Hasło\nDopisek.\n"


@pytest.fixture(scope="module")
def folder(tmp_path_factory):
    """Folder prezentacji z obrazem Źródła/baton-przyklad.jpg (jak w scenariusz-wzor.md)."""
    from PIL import Image
    f = tmp_path_factory.mktemp("prez")
    (f / "Źródła").mkdir()
    Image.new("RGB", (400, 600), (200, 120, 40)).save(str(f / "Źródła" / "baton-przyklad.jpg"))
    return str(f)


@pytest.fixture(scope="module")
def spec_wzoru(folder):
    return scenariusz.zloz(scenariusz.wzor(), {"folder": folder, "wyjscie": folder, "nazwa": "wzor"})


# --- wyciągnij ------------------------------------------------------------------------------------------------------------
def test_wyciagnij_z_bloku_kodu_z_gadaniem_przed_i_po():
    wkl = "Oto scenariusz:\n\n```markdown\n" + SC + "```\n\nDaj znać, czy coś poprawić."
    assert scenariusz.wyciagnij(wkl) == SC.strip() + "\n"


def test_wyciagnij_bez_plotkow_i_z_crlf():
    wkl = ("Cześć\r\n" + SC).replace("\n", "\r\n")
    t = scenariusz.wyciagnij(wkl)
    assert t.startswith(scenariusz.MARKER) and "\r" not in t and "## Hasło" in t


def test_wyciagnij_brak_markera():
    assert scenariusz.wyciagnij("tytuł: x\n## Hasło\nDopisek") is None
    assert scenariusz.wyciagnij("") is None and scenariusz.wyciagnij(None) is None


def test_wyciagnij_bierze_ostatni_marker_gdy_czat_powtorzyl_wzor():
    wkl = "```markdown\n" + scenariusz.wzor() + "```\n\nA oto Twój:\n```markdown\n" + SC + "```"
    t = scenariusz.wyciagnij(wkl)
    assert "Baton Przykład" not in t and "tytuł: Test" in t


def test_wyciagnij_marker_z_innymi_odstepami_i_wielkoscia():
    assert scenariusz.wyciagnij("  #   scenariusz dk  \ntytuł: A\n## B\nC").startswith(scenariusz.MARKER)


# --- wzór ---------------------------------------------------------------------------------------------------------------------
def test_wzor_przechodzi_wlasny_lint_bez_uwag(folder):
    w = scenariusz.wzor()
    assert w.startswith(scenariusz.MARKER)
    r = scenariusz.sprawdz(w, folder=folder)
    assert r["ok"] and r["bledy"] == [] and r["uwagi"] == []
    assert (r["slajdy"], r["rozdzialy"], r["tytul"]) == (6, 2, "Baton Przykład – oferta dla handlu")
    assert scenariusz.sprawdz(w)["ok"]            # bez folderu obrazów nie sprawdzamy plików


# --- sprawdz: błędy i uwagi -------------------------------------------------------------------------------------------------
def _blad(md, **kw):
    r = scenariusz.sprawdz(md, **kw)
    assert not r["ok"], r
    return " ".join(r["bledy"])


def _uwaga(md, **kw):
    r = scenariusz.sprawdz(md, **kw)
    assert r["ok"], r["bledy"]
    return " ".join(r["uwagi"])


def test_sprawdz_bledy_ramki():
    assert "SCENARIUSZ DK" in _blad("## Hasło\nDopisek")
    assert "tytuł" in _blad(scenariusz.MARKER + "\n\n## Hasło\nDopisek\n")
    assert "żadnego slajdu" in _blad(scenariusz.MARKER + "\ntytuł: X\n")
    assert "nie ma hasła" in _blad(scenariusz.MARKER + "\ntytuł: X\n\n##\nDopisek\n")


def test_sprawdz_uwagi_dlugosci():
    haslo = " ".join(["słowo"] * 11)
    assert "hasło ma 11 słów" in _uwaga("%s\ntytuł: X\n\n## %s\nDopisek.\n" % (scenariusz.MARKER, haslo))
    dop = " ".join(["słowo"] * 31)
    assert "dopisek ma 31 słów" in _uwaga("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, dop))
    pkt = "\n".join("- punkt %d" % i for i in range(5))
    assert "ma 5 punktów" in _uwaga("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, pkt))
    assert "samo hasło" in _uwaga("%s\ntytuł: X\n\n## Hasło\n" % scenariusz.MARKER)


def test_sprawdz_za_duzo_punktow_tabela_i_mieszanie_to_bledy():
    pkt = "\n".join("- punkt %d" % i for i in range(9))
    assert "9 punktów" in _blad("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, pkt))
    tab = "| a | b |\n|---|---|\n" + "\n".join("| %d | x |" % i for i in range(9))
    assert "9 wierszy" in _blad("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, tab))
    assert "zajmuje cały slajd" in _blad("%s\ntytuł: X\n\n## Hasło\n| a | b |\n|---|---|\n| 1 | 2 |\n- punkt\n" % scenariusz.MARKER)
    assert "Pod przekładką" in _blad("%s\ntytuł: X\n\n## Rozdział: Jeden\nTekst pod przekładką\n\n## Hasło\nD\n" % scenariusz.MARKER)
    cztery = "\n".join("**%d%%** opis" % i for i in range(5))
    assert "5 liczb" in _blad("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, cztery))


def test_sprawdz_obraz_nieistniejacy_tylko_z_folderem(folder):
    md = scenariusz.MARKER + "\ntytuł: X\n\n## Hasło\n![a](Źródła/nie-ma.jpg)\n"
    assert "nie-ma.jpg" in _blad(md, folder=folder)
    assert scenariusz.sprawdz(md)["ok"]                       # bez folderu: ścieżka względna nie jest sprawdzana
    ok = scenariusz.MARKER + "\ntytuł: X\n\n## Hasło\n![a](Źródła/baton-przyklad.jpg)\n"
    assert scenariusz.sprawdz(ok, folder=folder)["ok"]
    assert not scenariusz.sprawdz(scenariusz.MARKER + "\ntytuł: X\n\n## H\n![a](C:/nie/ma/tego.jpg)\n")["ok"]    # bezwzględna: zawsze


def test_sprawdz_limit_to_uwaga():
    assert "limit to 1" in _uwaga(scenariusz.wzor(), limit=1)
    assert "limit" not in " ".join(scenariusz.sprawdz(scenariusz.wzor(), limit=6)["uwagi"])


def test_sprawdz_rozdzial_bez_slajdow_i_dlugi_tytul():
    u = _uwaga("%s\ntytuł: %s\n\n## Hasło\nD\n\n## Rozdział: Koniec\n" % (scenariusz.MARKER, "T" * 50))
    assert "Rozdział „Koniec”" in u and "50 znaków" in u


def test_sprawdz_wklejka_z_gadaniem_tez_dziala():
    r = scenariusz.sprawdz("Proszę:\n```markdown\n" + SC + "```")
    assert r["ok"] and r["slajdy"] == 1 and r["tytul"] == "Test"


# --- parser: elementy i typografia ------------------------------------------------------------------------------------------------
def test_model_elementy_i_typografia():
    md = (scenariusz.MARKER + '\ntytuł: "Cudzysłów" - półpauza\n\n## **Hasło** z bold\nDopisek...\n- punkt **ważny**\n  ciąg dalszy\n'
          "1. numer\n**3,5 mln** klientów\n> cytat tekst — Jan Kowalski\n")
    m = scenariusz.model(md)
    assert m["tytul"] == "„Cudzysłów” – półpauza"
    el = m["slajdy"][0]["el"]
    assert m["slajdy"][0]["haslo"] == "Hasło z bold"
    assert [e["k"] for e in el] == ["dop", "li", "li", "liczba", "cyt"]
    assert el[0]["t"] == "Dopisek…"
    assert el[1]["poz"] == ["punkt ważny ciąg dalszy"] and not el[1]["num"]
    assert el[2]["num"] and el[3]["l"] == "3,5 mln" and el[3]["o"] == "klientów"
    assert scenariusz._cytat(el[4]["t"]) == ("cytat tekst", "Jan Kowalski")


# --- zloz: 1:1 i typy slajdów ---------------------------------------------------------------------------------------------------
def test_zloz_jeden_naglowek_to_jeden_slajd(spec_wzoru):
    typy = [s["type"] for s in spec_wzoru["slides"]]
    assert typy == ["cover_text", "section", "statement", "uklad", "uklad", "section", "table", "pics", "uklad", "end"]
    assert spec_wzoru["ustawienia"] == {"slajdy": 6, "rozdzialy": 2, "razem": 10, "ramka": 4}
    assert len(spec_wzoru["slides"]) == 6 + 2 + 2           # ## treści + przekładki + okładka + zakończenie


def test_zloz_ramka_okladka_zakonczenie_i_przekladki(spec_wzoru):
    sl = spec_wzoru["slides"]
    assert sl[0]["title"] == "Baton Przykład – oferta dla handlu" and sl[0]["subtitle"].startswith("Trzy smaki")
    assert sl[-1]["type"] == "end"
    roz = [s for s in sl if s["type"] == "section"]
    assert [(r["number"], r["title"], r["section"]) for r in roz] == [("01", "Dlaczego ten baton", "Dlaczego ten baton"),
                                                                      ("02", "Oferta dla sklepu", "Oferta dla sklepu")]
    assert spec_wzoru["sections"] is True


def test_zloz_ksztalt_specu_jak_dokument(spec_wzoru):
    for k in ("theme", "sections", "slides", "mapa_blokow", "uwagi", "cel", "szablon", "bledy_tekstu", "warianty", "warianty_plik",
              "nazwa", "tytul", "ustawienia", "output"):
        assert k in spec_wzoru, k
    assert spec_wzoru["cel"] == "scenariusz" and spec_wzoru["theme"] == "shop"
    assert spec_wzoru["output"].endswith("wzor.pptx")
    assert set(spec_wzoru["mapa_blokow"]) == set(range(1, 11))
    assert all(d["wzor"] is None or "id" in d["wzor"] for d in spec_wzoru["szablon"])


def test_zloz_tytuly_slajdow_to_hasla_i_typy_tresci(spec_wzoru):
    sl = spec_wzoru["slides"]
    assert [s.get("title") for s in sl[2:5]] == ["Prosty skład, bez dodatku cukru", "Trzy powody, dla których klienci wracają",
                                                  "Skład ma znaczenie przy zakupie"]
    assert sl[2]["text"] == "Prosty skład, bez dodatku cukru" and sl[2]["note"] == "Pięć składników, które każdy przeczyta w kilka sekund."
    tab = sl[6]
    assert tab["title"] == "Trzy smaki na start" and tab["head"] == ["Smak", "Gramatura", "W kartonie"] and len(tab["rows"]) == 3
    pics = sl[7]
    assert pics["title"] == "Tak wygląda na półce" and len(pics["items"]) == 1
    assert pics["items"][0]["caption"] == "Baton Przykład w trzech smakach" and os.path.isabs(pics["items"][0]["image"])
    cyt = sl[8]["rows"][0]
    assert sl[8]["title"] == "Co mówią sklepy" and cyt["k"] == "quote" and cyt["author"] == "Anna Przykładowa, kierowniczka sklepu"
    assert cyt["t"] == "Klienci pytają o ten baton częściej niż o poprzednią nowość."
    hero = [b for r in sl[4]["rows"] for it in r["items"] for b in it["blocks"] if b["k"] == "hero"]
    assert hero and hero[0]["t"] == "42%"                                          # liczba-bohater
    punkty = [b for r in sl[3]["rows"] for it in r["items"] for b in it["blocks"] if b["k"] == "li"]
    assert [b["t"] for b in punkty] == ["Skład bez cukru dodanego", "Jedna wygodna porcja na drogę", "Smaki, które znają z półek"]


def test_zloz_samo_haslo_i_tabela_z_dopiskiem_i_obrazy_z_nota(folder):
    md = (scenariusz.MARKER + "\ntytuł: X\n\n## Samo hasło\n\n## Tabela\nCeny netto.\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
          "## Dwa zdjęcia\nNota pod nimi.\n![Jeden](Źródła/baton-przyklad.jpg)\n![Dwa](Źródła/baton-przyklad.jpg)\n")
    sp = scenariusz.zloz(md, {"folder": folder})
    assert [s["type"] for s in sp["slides"]] == ["cover_text", "statement", "table", "pics", "end"]
    assert sp["slides"][1]["text"] == "Samo hasło"
    assert sp["slides"][2]["source"] == "Ceny netto."
    assert sp["slides"][3]["note"] == "Nota pod nimi." and len(sp["slides"][3]["items"]) == 2
    assert sp["sections"] is False


def test_zloz_dlugi_tekst_to_nadal_jeden_slajd():
    dop = " ".join("słowo%d" % i for i in range(120))
    sp = scenariusz.zloz("%s\ntytuł: X\n\n## Za dużo tekstu\n%s\n" % (scenariusz.MARKER, dop))
    tresc = [s for s in sp["slides"] if s["type"] not in ("cover_text", "end", "statement")]
    assert len(tresc) == 1 and tresc[0]["title"] == "Za dużo tekstu"
    assert any("Za dużo tekstu" in u for u in sp["uwagi"])


def test_zloz_nazwa_wyjscie_i_domyslna_nazwa(tmp_path):
    sp = scenariusz.zloz(SC, {"wyjscie": str(tmp_path), "nazwa": "moja"})
    assert sp["output"] == os.path.join(str(tmp_path), "moja.pptx") and sp["nazwa"] == "moja"
    sp = scenariusz.zloz(scenariusz.MARKER + '\ntytuł: Plik: "ważny"?\n\n## A\nB\n', {"wyjscie": str(tmp_path)})
    assert os.path.basename(sp["output"]) == "Plik „ważny”.pptx"


def test_zloz_rzuca_valueerror_po_polsku_gdy_blad(folder):
    with pytest.raises(ValueError) as e:
        scenariusz.zloz(scenariusz.MARKER + "\ntytuł: X\n\n## H\n![a](Źródła/brak.jpg)\n", {"folder": folder})
    assert "nie da się zbudować" in str(e.value) and "brak.jpg" in str(e.value)
    with pytest.raises(ValueError):
        scenariusz.zloz("bez markera")


# --- krótka treść wypełnia slajd; kandydaci dla pętli „oka” ----------------------------------------------------------------------------------------
def test_zloz_dlugi_dopisek_nie_miesci_sie_w_statement_i_dostaje_duza_karte():
    dop = " ".join("słowo%d" % i for i in range(60))
    sp = scenariusz.zloz("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, dop))
    sl = sp["slides"][1]
    assert sl["type"] == "uklad" and sl["title"] == "Hasło" and sl["rows"][0]["min_h"] > 5           # duża karta, nie mała na górze


def test_zloz_liczba_bohater_stoi_duza_w_karcie_na_wysokosc_pola():
    sp = scenariusz.zloz("%s\ntytuł: X\n\n## Wynik\n**42%%** kupujących czyta skład\n" % scenariusz.MARKER)
    sl = sp["slides"][1]
    hero = sl["rows"][0]["items"][0]["blocks"][0]
    assert hero == {"k": "hero", "t": "42%", "pt": 60} and sl["rows"][0]["min_h"] > 8
    assert [k["nazwa"] for k in sp["warianty"]["slajdy"][0]["kandydaci"]][-1].endswith("(hero_stat)")


def test_warianty_dla_oka_sa_w_specu_i_inny_wariant_podmienia_slajd(spec_wzoru):
    import copy
    import dokument
    import szablonuj
    rek = {r["zrodlo"]: r for r in spec_wzoru["warianty"]["slajdy"]}
    assert len(rek) == 3 and all(len(r["kandydaci"]) >= 2 and r["wybrany"] == 0 for r in rek.values())   # dopisek, liczba, tabela
    assert all({"nazwa", "opcje", "punkty", "miary", "usterki", "dopuszczony", "slajd"} <= set(k) for r in rek.values() for k in r["kandydaci"])
    sp = copy.deepcopy(spec_wzoru)
    n = len(sp["slides"])
    assert szablonuj.inny_wariant(sp, 3, {"SIEROTA"}, sp["warianty"])            # statement -> duża karta z dopiskiem
    assert sp["slides"][2]["type"] == "uklad" and sp["slides"][2]["title"] == "Prosty skład, bez dodatku cukru"
    assert dokument.popraw_po_renderze(sp, {7: ["PLYWAJACA_TRESC"]}) == [7]       # tak robi pętla „oka”: tabela -> karty
    assert sp["slides"][6]["type"] == "uklad" and sp["slides"][6]["title"] == "Trzy smaki na start"
    labels = [b["label"] for it in sp["slides"][6]["rows"][0]["items"] for b in it["blocks"]]
    assert labels[:3] == ["Smak", "Gramatura", "W kartonie"] and len(sp["slides"]) == n


def test_zwykla_lista_ma_kandydatow_z_regul_szablonu():
    sp = scenariusz.zloz(scenariusz.MARKER + "\ntytuł: X\n\n## Trzy hasła\n- Bez cukru\n- Bez konserwantów\n- Bez glutenu\n")
    assert sp["slides"][1]["type"] == "uklad" and sp["warianty"]["slajdy"]


# --- prawdziwa budowa: pptx z wzoru, pokrycie treści ---------------------------------------------------------------------------------------
def test_budowa_pptx_ze_wzoru_i_pokrycie(spec_wzoru, folder):
    import build_dk
    import dokument
    from pptx import Presentation
    out = os.path.join(folder, "wzor.pptx")
    spec_wzoru["output"] = out
    build_dk.build(spec_wzoru, out)
    assert len(Presentation(out).slides) == len(spec_wzoru["slides"]) == 10
    m = scenariusz.model(scenariusz.wzor(), folder)
    pok = dokument.pokrycie(m, out, spec_wzoru["mapa_blokow"])
    assert not pok["brakuje"] and "100%" in pok["tekst"], pok


# --- polecenia dla AI ------------------------------------------------------------------------------------------------------------------------------------------
def test_polecenie_przygotowania_ma_role_zasady_wzor_i_koniec():
    t = scenariusz.polecenie_przygotowania([{"plik": "karta.docx", "tekst": "Skład: daktyle, orzechy."}], ["zrzut1.png", "zdjecie.jpg"], 9,
                                           tytul="Nowy baton", folder=r"M:\X\Prez")
    for s in ("Dobra Kaloria", "Niczego nie wymyślasz", "Najwyżej 9 slajdów", "„Nowy baton”", "# SCENARIUSZ DK", "Baton Przykład",
              "=== PLIK: karta.docx ===", "Skład: daktyle, orzechy.", "- zrzut1.png", "- zdjecie.jpg", "Odczytaj z nich treść"):
        assert s in t, s
    assert t.rstrip().endswith("Bez wstępu i komentarza.")
    assert "zaczynając od linii # SCENARIUSZ DK" in t
    assert scenariusz.wzor().strip() in t


def test_polecenie_przygotowania_przycina_zrodla_po_rowno():
    dlugi = "akapit z tekstem. " * 5000                  # 90 000 znaków
    t = scenariusz.polecenie_przygotowania([{"plik": "a.pdf", "tekst": dlugi}, {"plik": "b.txt", "tekst": "krótki"}], [], 5, folder=r"M:\X\Prez")
    assert len(t) < 60000
    assert "tekst przycięty" in t and "reszta jest w pliku „a.pdf”" in t and r"M:\X\Prez\Źródła" in t
    assert "krótki" in t and "b.txt”" not in t.split("krótki", 1)[1][:80]      # krótki dokument bez dopisku o przycięciu
    assert "OBRAZY I ZRZUTY" not in t
    assert scenariusz.wyciagnij(t) is not None and scenariusz.wyciagnij(t).startswith(scenariusz.MARKER)


def test_polecenie_poprawki_ma_scenariusz_uwagi_plansze_i_prosbe_o_caly():
    t = scenariusz.polecenie_poprawki(SC, ["Slajd 3: pusty dół", "Hasło za długie"], ["plansza-1.png", "plansza-2.png"], 7, folder=r"M:\X\Prez")
    for s in ("tytuł: Test", "- Slajd 3: pusty dół", "- Hasło za długie", "- plansza-1.png", "- plansza-2.png", "Najwyżej 7 slajdów",
              "pełnym, poprawionym scenariuszem", "# SCENARIUSZ DK", r"M:\X\Prez"):
        assert s in t, s
    assert scenariusz.wyciagnij(t).startswith(scenariusz.MARKER)       # ostatni marker = ten z poleceniem, nie z bloku wzoru
    assert "(brak uwag" in scenariusz.polecenie_poprawki(SC, [], [], 7)


def test_polecenie_agenta():
    t = scenariusz.polecenie_agenta(r"M:\X\2026-10-27 - Baton")
    for s in (r"M:\X\2026-10-27 - Baton\Źródła", r"M:\X\2026-10-27 - Baton\scenariusz.md", "--scenariusz", "stworz-cli.exe", "plansz",
              "OBEJRZYJ", "# SCENARIUSZ DK", "Baton Przykład"):
        assert s in t, s


def test_okladka_pelny_podtytul_i_uwaga_gdy_za_dlugi():
    pod = "Trzy smaki, krótki skład i miejsce na półce"
    sp = scenariusz.zloz("%s\ntytuł: Krótki tytuł\npodtytuł: %s\n\n## A\nB\n" % (scenariusz.MARKER, pod))
    assert sp["slides"][0]["type"] == "cover_text" and sp["slides"][0]["subtitle"] == pod and pod in sp["slides"][0]["notes"]
    dlugi = " ".join(["słowo"] * 30)
    assert "Podtytuł ma 30 słów" in " ".join(scenariusz.sprawdz("%s\ntytuł: X\npodtytuł: %s\n\n## A\nB\n" % (scenariusz.MARKER, dlugi))["uwagi"])
    sp = scenariusz.zloz("%s\ntytuł: %s\npodtytuł: %s\n\n## A\nB\n" % (scenariusz.MARKER, "T" * 50, pod))      # długi tytuł: statement z notą
    assert sp["slides"][0]["type"] == "statement" and sp["slides"][0]["note"] == pod
