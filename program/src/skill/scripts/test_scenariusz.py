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


SZK = "```markdown\n" + scenariusz.SZKIELET.strip("\n") + "\n```"


def _wzor():
    """Wzór bez nazw „przykładu” (Baton Przykład, baton-przyklad.jpg): sprawdz() uznaje je za przepisany przykład."""
    return scenariusz.wzor().replace("Baton Przykład", "Baton Testowy").replace("baton-przyklad", "baton-testowy").replace("Anna Przykładowa", "Anna Testowa")


@pytest.fixture(scope="module")
def folder(tmp_path_factory):
    """Folder prezentacji z obrazem Źródła/baton-testowy.jpg (jak w scenariusz-wzor.md)."""
    from PIL import Image
    f = tmp_path_factory.mktemp("prez")
    (f / "Źródła").mkdir()
    Image.new("RGB", (400, 600), (200, 120, 40)).save(str(f / "Źródła" / "baton-testowy.jpg"))
    return str(f)


@pytest.fixture(scope="module")
def spec_wzoru(folder):
    return scenariusz.zloz(_wzor(), {"folder": folder, "wyjscie": folder, "nazwa": "wzor"})


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
    wkl = "```markdown\n" + _wzor() + "```\n\nA oto Twój:\n```markdown\n" + SC + "```"
    t = scenariusz.wyciagnij(wkl)
    assert "Baton Przykład" not in t and "tytuł: Test" in t


def test_wyciagnij_marker_z_innymi_odstepami_i_wielkoscia():
    assert scenariusz.wyciagnij("  #   scenariusz dk  \ntytuł: A\n## B\nC").startswith(scenariusz.MARKER)


# --- wzór ---------------------------------------------------------------------------------------------------------------------
def test_wzor_przechodzi_wlasny_lint_bez_uwag(folder):
    w = _wzor()
    assert w.startswith(scenariusz.MARKER)
    r = scenariusz.sprawdz(w, folder=folder)
    assert r["ok"] and r["bledy"] == [] and r["uwagi"] == []
    assert (r["slajdy"], r["rozdzialy"], r["tytul"]) == (6, 2, "Baton Testowy – oferta dla handlu")
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
    assert "za dużo punktów (9)" in _blad("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, pkt))
    tab = "| a | b |\n|---|---|\n" + "\n".join("| %d | x |" % i for i in range(9))
    assert "9 wierszy" in _blad("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, tab))
    assert "zajmuje cały slajd" in _blad("%s\ntytuł: X\n\n## Hasło\n| a | b |\n|---|---|\n| 1 | 2 |\n- punkt\n" % scenariusz.MARKER)
    assert "Pod przekładką" in _blad("%s\ntytuł: X\n\n## Rozdział: Jeden\nTekst pod przekładką\n\n## Hasło\nD\n" % scenariusz.MARKER)
    cztery = "\n".join("**%d%%** opis" % i for i in range(5))
    assert "za dużo liczb-bohaterów (5)" in _blad("%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, cztery))


def test_sprawdz_obraz_nieistniejacy_tylko_z_folderem(folder):
    md = scenariusz.MARKER + "\ntytuł: X\n\n## Hasło\n![a](Źródła/nie-ma.jpg)\n"
    assert "nie-ma.jpg" in _blad(md, folder=folder)
    assert scenariusz.sprawdz(md)["ok"]                       # bez folderu: ścieżka względna nie jest sprawdzana
    ok = scenariusz.MARKER + "\ntytuł: X\n\n## Hasło\n![a](Źródła/baton-testowy.jpg)\n"
    assert scenariusz.sprawdz(ok, folder=folder)["ok"]
    assert not scenariusz.sprawdz(scenariusz.MARKER + "\ntytuł: X\n\n## H\n![a](C:/nie/ma/tego.jpg)\n")["ok"]    # bezwzględna: zawsze


def test_sprawdz_limit_to_uwaga():
    assert "limit to 1" in _uwaga(_wzor(), limit=1)
    assert "limit" not in " ".join(scenariusz.sprawdz(_wzor(), limit=6)["uwagi"])


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
    assert sl[0]["title"] == "Baton Testowy – oferta dla handlu" and sl[0]["subtitle"].startswith("Trzy smaki")
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
    assert pics["items"][0]["caption"] == "Baton Testowy w trzech smakach" and os.path.isabs(pics["items"][0]["image"])
    cyt = sl[8]["rows"][0]
    assert sl[8]["title"] == "Co mówią sklepy" and cyt["k"] == "quote" and cyt["author"] == "Anna Testowa, kierowniczka sklepu"
    assert cyt["t"] == "Klienci pytają o ten baton częściej niż o poprzednią nowość."
    hero = [b for r in sl[4]["rows"] for it in r["items"] for b in it["blocks"] if b["k"] == "hero"]
    assert hero and hero[0]["t"] == "42%"                                          # liczba-bohater
    punkty = [b for r in sl[3]["rows"] for it in r["items"] for b in it["blocks"] if b["k"] == "li"]
    assert [b["t"] for b in punkty] == ["Skład bez cukru dodanego", "Jedna wygodna porcja na drogę", "Smaki, które znają z półek"]


def test_zloz_samo_haslo_i_tabela_z_dopiskiem_i_obrazy_z_nota(folder):
    md = (scenariusz.MARKER + "\ntytuł: X\n\n## Samo hasło\n\n## Tabela\nCeny netto.\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
          "## Dwa zdjęcia\nNota pod nimi.\n![Jeden](Źródła/baton-testowy.jpg)\n![Dwa](Źródła/baton-testowy.jpg)\n")
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
    m = scenariusz.model(_wzor(), folder)
    pok = dokument.pokrycie(m, out, spec_wzoru["mapa_blokow"])
    assert not pok["brakuje"] and "100%" in pok["tekst"], pok


# --- polecenia dla AI ------------------------------------------------------------------------------------------------------------------------------------------
def test_polecenie_przygotowania_ma_role_zasady_wzor_i_koniec():
    t = scenariusz.polecenie_przygotowania([{"plik": "karta.docx", "tekst": "Skład: daktyle, orzechy."}], ["zrzut1.png", "zdjecie.jpg"], 9,
                                           tytul="Nowy baton", folder=r"M:\X\Prez")
    for s in ("Dobra Kaloria", "Niczego nie wymyślasz", "Najwyżej 9 slajdów", "„Nowy baton”", "# SCENARIUSZ DK", "tytuł: <tytuł z materiałów>",
              "## <hasło slajdu>", "=== PLIK: karta.docx ===", "Skład: daktyle, orzechy.", "- zrzut1.png", "- zdjecie.jpg", "Odczytaj z nich treść"):
        assert s in t, s
    koniec = t.split("CO MASZ ODDAĆ")[-1]                                    # blok na samym końcu polecenia
    assert "Odpowiedz WYŁĄCZNIE pełnym scenariuszem w jednym bloku kodu" in koniec and "od linii # SCENARIUSZ DK; bez komentarzy przed blokiem i po nim" in koniec
    assert t.rstrip().endswith("jeszcze raz.”")
    assert SZK in t and "Baton Przykład" not in t and "baton-przyklad" not in t          # szkielet z nawiasami, nie przykład do przepisania
    assert "nie przepisuj żadnego słowa z tego szkieletu" in t


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
              "OBEJRZYJ", "# SCENARIUSZ DK", "tytuł: <tytuł z materiałów>"):
        assert s in t, s
    assert "Baton Przykład" not in t and "scenariusz-wzor.md" not in t            # agent nie dostaje przykładu do przepisania ani wskazania na plik wzoru
    assert "Przeczytaj KAŻDY plik z folderu Źródła" in t


def test_okladka_pelny_podtytul_i_uwaga_gdy_za_dlugi():
    pod = "Trzy smaki, krótki skład i miejsce na półce"
    sp = scenariusz.zloz("%s\ntytuł: Krótki tytuł\npodtytuł: %s\n\n## A\nB\n" % (scenariusz.MARKER, pod))
    assert sp["slides"][0]["type"] == "cover_text" and sp["slides"][0]["subtitle"] == pod and pod in sp["slides"][0]["notes"]
    dlugi = " ".join(["słowo"] * 30)
    assert "Podtytuł ma 30 słów" in " ".join(scenariusz.sprawdz("%s\ntytuł: X\npodtytuł: %s\n\n## A\nB\n" % (scenariusz.MARKER, dlugi))["uwagi"])
    sp = scenariusz.zloz("%s\ntytuł: %s\npodtytuł: %s\n\n## A\nB\n" % (scenariusz.MARKER, "T" * 50, pod))      # długi tytuł: statement z notą
    assert sp["slides"][0]["type"] == "statement" and sp["slides"][0]["note"] == pod


def test_polecenie_poprawki_lista_problemow_ocena_planszy_i_jednoznaczny_koniec():
    t = scenariusz.polecenie_poprawki(SC, ["Slajd 4: puste miejsce"], ["wynik_01-06.png"], 7, folder=r"M:\X\Prez\plansze",
                                      problemy=["Slajd 7: tekst „Badanie wykonała Chilli insi…” nie mieści się w polu (wystaje o 5 pt) - skróć go."])
    assert "PROBLEMY NA SLAJDACH" in t and "- Slajd 7: tekst „Badanie wykonała Chilli insi…” nie mieści się w polu" in t
    assert "Dla KAŻDEJ planszy i KAŻDEGO slajdu" in t and "UWAGI PROGRAMU" in t
    assert t.index("PROBLEMY NA SLAJDACH") < t.index("UWAGI PROGRAMU")
    koniec = t.split("CO MASZ ODDAĆ")[1]
    assert "pełnym, poprawionym scenariuszem w jednym bloku kodu" in koniec and "od linii # SCENARIUSZ DK" in koniec
    assert "bez komentarzy przed blokiem i po nim" in koniec and "Nie widzę plansz" in koniec
    bez = scenariusz.polecenie_poprawki(SC, [], [], 7)
    assert "PROBLEMY NA SLAJDACH" not in bez and "Nie widzę plansz" not in bez     # bez plansz nie ma czego „nie widzieć”


def test_polecenie_przygotowania_koniec_i_obrazy():
    z = [{"plik": "a.txt", "tekst": "x"}]
    t = scenariusz.polecenie_przygotowania(z, ["zrzut.png"], 6)
    assert "CO MASZ ODDAĆ" in t and "w jednym bloku kodu" in t and "Nie widzę obrazów" in t
    assert "Nie widzę obrazów" not in scenariusz.polecenie_przygotowania(z, [], 6)


def test_polecenie_poprawki_agenta_zapisuje_kolejny_plik_i_konczy_zdaniem():
    t = scenariusz.polecenie_poprawki_agenta(r"M:\X\Prez", r"M:\X\Prez\scenariusz-2.md", r"M:\X\Prez\scenariusz-3.md", ["Slajd 2: pusty dół"],
                                             ["wynik_01-06.png", "wynik_07-10.png"], 9, plansze_folder=r"M:\X\Prez\plansze",
                                             problemy=["Slajd 7: tekst „…” nie mieści się w polu - skróć go."])
    for s in (r"Zapisz poprawiony scenariusz jako NOWY plik: M:\X\Prez\scenariusz-3.md", r"M:\X\Prez\plansze", "wynik_07-10.png", "KAŻDĄ planszę",
              "Dla KAŻDEJ planszy", "- Slajd 7: tekst", "nie nadpisuj poprzednich wersji", "Gotowe – wróć do programu Stwórz prezentację.", "# SCENARIUSZ DK"):
        assert s in t, s
    assert t.rstrip().split("\n\n")[-1].startswith("## CO MASZ ODDAĆ")                 # blok „CO MASZ ODDAĆ” zamyka polecenie
    assert "Gotowe – wróć do programu" in scenariusz.polecenie_agenta(r"M:\X\Prez")


# --- przepisany przykład i szkielet ---------------------------------------------------------------------------------------------------------------------
def test_sprawdz_wykrywa_przepisany_przyklad_z_wzoru():
    r = scenariusz.sprawdz(scenariusz.wzor())                      # nazwy ze starego wzoru: „Baton Przykład”, baton-przyklad.jpg
    assert not r["ok"] and r["bledy"][0] == scenariusz.BLAD_PRZYKLAD and "przepisał przykład zamiast Twoich materiałów" in r["bledy"][0]
    assert scenariusz.sprawdz(scenariusz.wzor(), przyklad_ok=True)["ok"]
    # wystarczy jedna nazwa z przykładu
    for md in (scenariusz.MARKER + "\ntytuł: Oferta\n\n## Hasło\n![a](Źródła/baton-przyklad.jpg)\n",
               scenariusz.MARKER + "\ntytuł: Baton Przykład\n\n## Hasło\nTekst\n",
               scenariusz.MARKER + "\ntytuł: Oferta\n\n## Hasło\n> Cytat — Anna Przykładowa\n"):
        assert not scenariusz.sprawdz(md)["ok"] and scenariusz.sprawdz(md)["bledy"][0] == scenariusz.BLAD_PRZYKLAD
    assert scenariusz.sprawdz(_wzor())["ok"]                       # ten sam wzór z innymi nazwami przechodzi
    with pytest.raises(ValueError, match="przepisał przykład"):
        scenariusz.zloz(scenariusz.wzor(), {})


def test_sprawdz_wykrywa_puste_miejsca_ze_szkieletu():
    r = scenariusz.sprawdz(scenariusz.SZKIELET)
    assert not r["ok"] and r["bledy"][0] == scenariusz.BLAD_SZKIELET
    md = scenariusz.MARKER + "\ntytuł: Oferta\n\n## <hasło slajdu>\nTekst\n"
    assert scenariusz.sprawdz(md)["bledy"][0] == scenariusz.BLAD_SZKIELET
    assert scenariusz.sprawdz(scenariusz.MARKER + "\ntytuł: Oferta\n\n## Cena < 5 zł i > 3 zł\nTekst\n")["ok"]   # zwykłe < > w treści nie są szkieletem


def test_blad_krotko_jedno_zdanie():
    assert scenariusz.blad_krotko([scenariusz.BLAD_PRZYKLAD, "inny"]) == scenariusz.BLAD_PRZYKLAD
    assert scenariusz.BLAD_PRZYKLAD == "Czat przepisał przykład zamiast Twoich materiałów – poproś go o scenariusz z plików w folderze Źródła."
    assert scenariusz.blad_krotko([scenariusz.BLAD_SZKIELET]) == scenariusz.BLAD_SZKIELET
    assert scenariusz.blad_krotko([]) == "Z tego scenariusza nie da się zbudować slajdów."
    assert scenariusz.blad_krotko(["Zdanie krótko — a tu szczegóły, które okno zwija."]) == "Zdanie krótko."
    # każdy błąd z sprawdz() to JEDNO krótkie zdanie (po „ — ” stoją szczegóły) i nie zaczyna się od numeru ani kodu
    pkt = "\n".join("- p %d" % i for i in range(9))
    tab = "| a | b |\n|---|---|\n" + "\n".join("| %d | x |" % i for i in range(9))
    for md in ("## Hasło\nD", scenariusz.MARKER + "\n\n## Hasło\nD\n", scenariusz.MARKER + "\ntytuł: X\n",
               "%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, pkt), "%s\ntytuł: X\n\n## Hasło\n%s\n" % (scenariusz.MARKER, tab),
               "%s\ntytuł: X\n\n## H\n![a](C:/nie/ma/tego.jpg)\n" % scenariusz.MARKER):
        b = scenariusz.sprawdz(md)["bledy"]
        assert b and all(" — " in x for x in b), b                          # zdanie — szczegóły
        z = scenariusz.blad_krotko(b)
        assert len(z) < 90 and z.endswith(".") and " — " not in z and "(##)" not in z, z


def test_polecenie_naprawy_czat_i_agent(tmp_path):
    bl = [scenariusz.BLAD_PRZYKLAD]
    t = scenariusz.polecenie_naprawy("# SCENARIUSZ DK\ntytuł: Baton Przykład\n", bl, slajdy=8)
    for s in ("POPRAWKA", "- " + scenariusz.BLAD_PRZYKLAD, "WYŁĄCZNIE z materiałów", "Najwyżej 8 slajdów", "TWOJA POPRZEDNIA ODPOWIEDŹ", "tytuł: Baton Przykład",
              "Nie widzę materiałów", "CO MASZ ODDAĆ", "w jednym bloku kodu", "od linii # SCENARIUSZ DK"):
        assert s in t, s
    assert "tytuł: <tytuł z materiałów>" not in t and len(t) < 2500                 # krótkie: bez formatu i szkieletu (czat ma je z pierwszego polecenia)
    assert t.rstrip().split("\n\n")[-1].startswith("CO MASZ ODDAĆ")
    z = tmp_path / "Źródła"
    z.mkdir()
    (z / "opis.docx").write_text("x")
    (tmp_path / "scenariusz.md").write_text("x")
    a = scenariusz.polecenie_naprawy("# SCENARIUSZ DK\ntytuł: Baton Przykład\n", bl, str(tmp_path), agent=True, slajdy=8)
    assert a == scenariusz.polecenie_naprawy_agenta(str(tmp_path), bl, str(tmp_path / "scenariusz-2.md"), 8, md="# SCENARIUSZ DK\ntytuł: Baton Przykład\n")
    for s in ("Powody odrzucenia", scenariusz.BLAD_PRZYKLAD, "Zapisz poprawiony scenariusz jako NOWY plik: " + str(tmp_path / "scenariusz-2.md"),
              "Przeczytaj KAŻDY plik z folderu Źródła: opis.docx", "Odrzucona wersja", "nie nadpisuj poprzednich wersji", "Gotowe – wróć do programu Stwórz prezentację."):
        assert s in a, s
    assert a.rstrip().split("\n\n")[-1].startswith("## CO MASZ ODDAĆ")


def test_polecenie_agenta_wymienia_pliki_ze_zrodel(tmp_path):
    z = tmp_path / "Źródła"
    z.mkdir()
    (z / "opis produktu.docx").write_text("x")
    (z / "zrzut ekranu.png").write_text("x")
    t = scenariusz.polecenie_agenta(str(tmp_path))
    assert "Przeczytaj KAŻDY plik z folderu Źródła: opis produktu.docx, zrzut ekranu.png." in t


def test_polecenie_agenta_kolejny_plik_i_koniec(tmp_path):
    (tmp_path / "Źródła").mkdir()
    pierwsze = scenariusz.polecenie_agenta(str(tmp_path))
    assert "Scenariusz do napisania (nowy plik): " + str(tmp_path / "scenariusz.md") in pierwsze and "Poprzedni scenariusz" not in pierwsze
    (tmp_path / "scenariusz.md").write_text("x")
    (tmp_path / "scenariusz-3.md").write_text("x")
    kolejne = scenariusz.polecenie_agenta(str(tmp_path))
    assert "Scenariusz do napisania (nowy plik): " + str(tmp_path / "scenariusz-4.md") in kolejne and "Poprzedni scenariusz (zostaje bez zmian): " + str(tmp_path / "scenariusz-3.md") in kolejne
    koniec = kolejne.rstrip().split("\n\n")[-1]
    assert koniec.startswith("## CO MASZ ODDAĆ") and "kolejny plik " + str(tmp_path / "scenariusz-4.md") in koniec and "nie nadpisuj poprzednich wersji" in koniec
    assert "Gotowe – wróć do programu Stwórz prezentację." in koniec


def test_kazde_polecenie_konczy_sie_blokiem_co_masz_oddac():
    z = [{"plik": "a.txt", "tekst": "x"}]
    for t in (scenariusz.polecenie_przygotowania(z, [], 6), scenariusz.polecenie_poprawki(SC, [], [], 6), scenariusz.polecenie_naprawy(SC, ["x"])):
        ostatni = t.rstrip().split("\n\n")[-1]
        assert ostatni.startswith("CO MASZ ODDAĆ") and "w jednym bloku kodu" in ostatni and "od linii # SCENARIUSZ DK" in ostatni and "bez komentarzy" in ostatni
        assert t.count("CO MASZ ODDAĆ") == 1


def test_znaki_przykladu_ida_za_wzorem(monkeypatch):
    assert {"baton przykład", "baton-przyklad", "anna przykładowa"} <= set(scenariusz.znaki_przykladu())
    nowy = ("# SCENARIUSZ DK\ntytuł: Granola Wzorcowa – oferta\n\n## Okładka\n![Zdjęcie](Źródła/granola-wzor.png)\n\n"
            "## Opinia\n> Dobry produkt. — Jan Wzorcowy, sklep\n")
    monkeypatch.setattr(scenariusz, "wzor", lambda: nowy)
    znaki = scenariusz.znaki_przykladu()
    assert {"granola wzorcowa", "granola-wzor", "jan wzorcowy"} <= set(znaki) and "baton przykład" not in znaki
    for md in (scenariusz.MARKER + "\ntytuł: Granola Wzorcowa\n\n## H\nTekst\n", scenariusz.MARKER + "\ntytuł: Oferta\n\n## H\n![a](Źródła/granola-wzor.png)\n",
               scenariusz.MARKER + "\ntytuł: Oferta\n\n## H\n> Cytat — Jan Wzorcowy\n"):
        assert scenariusz.sprawdz(md)["bledy"][:1] == [scenariusz.BLAD_PRZYKLAD], md
    assert scenariusz.sprawdz(scenariusz.MARKER + "\ntytuł: Baton Przykład\n\n## H\nTekst\n")["ok"]      # stary przykład już nie jest wzorem
    monkeypatch.setattr(scenariusz, "wzor", lambda: (_ for _ in ()).throw(OSError("brak pliku")))
    assert not scenariusz.sprawdz(scenariusz.MARKER + "\ntytuł: Baton Przykład\n\n## H\nTekst\n")["ok"]    # bez wzoru: nazwy awaryjne
