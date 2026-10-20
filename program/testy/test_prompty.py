# -*- coding: utf-8 -*-
"""Testy polecen dla AI, petli "oka", plansz i listy slajdow szablonu w silniku programu (bez PowerPointa i bez sieci).

    python -m pytest -p no:cacheprovider WORK\\logs\\test_prompty.py -q

Silnik importuje skill z paths.SKILL_SCRIPTS; w zrodlach (bez builda) jest to stara kopia WORK\\src\\skill, wiec test
wybiera skill z NOWSZYM polecenia.py (kopia po buildzie albo ~\\.claude\\skills\\prezentacje - zrodlo tekstow polecen).
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORK, "src", "app"))
import paths  # noqa: E402

_KAND = [k for k in (os.path.join(WORK, "src", "skill"), os.path.join(os.path.expanduser("~"), ".claude", "skills", "prezentacje"))
         if os.path.exists(os.path.join(k, "scripts", "polecenia.py"))]
for _k in sorted(_KAND, key=lambda k: -os.path.getmtime(os.path.join(k, "scripts", "polecenia.py"))):
    if True:
        paths.SKILL_DIR, paths.SKILL_SCRIPTS = _k, os.path.join(_k, "scripts")
        paths.VERIFY_PS = os.path.join(_k, "scripts", "verify.ps1")
        break
import engine  # noqa: E402
import polecenia  # noqa: E402
import pptx_convert  # noqa: E402

ORYG = r"D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\06.10.2026 - strategia\DK_co_dalej_update.pptx"
SPEC_STRATEGIA = os.environ.get("DK_TEST_SPEC", "")   # spec_konwersja.json strategii (opcjonalnie); bez niego test pomija
KATALOG = os.path.join(paths.SKILL_DIR, "assets", "katalog-szablonu.json")
DANE = {"cel_slajdy": 25, "widoczne": 43, "wszystkie": 43}


# --- krok0, EXTRA ----------------------------------------------------------------------------------------------------
def test_krok0_wymienia_nowe_pliki_i_skrot_stylu():
    k = engine.krok0()
    for s in ("dopracowanie.md", "katalog-szablonu.md", "lekcje.md", "konwersja-pptx.md", "pkt 2a i 2b", "KROK 0b",
              "hasła w Mindset, Lato tylko jako krótki dopisek", "kremowe tylko karty"):
        assert s in k, s
    assert "Mindset tylko tytuł" not in k and "reszta Lato" not in k


@pytest.mark.skipif(not os.path.exists(KATALOG), reason="brak katalogu szablonu w skillu")
def test_extra_zgodne_z_katalogiem_szablonu():
    kat = {s["nr"]: s for s in json.load(open(KATALOG, encoding="utf8"))["slajdy"]}
    for nr, grupa, nazwa in engine.EXTRA:
        assert kat[nr]["nazwa"] == nazwa, (nr, nazwa, kat[nr]["nazwa"])
        assert kat[nr]["grupa"] == grupa, (nr, grupa, kat[nr]["grupa"])
    nry = [n for n, _g, _t in engine.EXTRA]
    assert len(nry) == len(set(nry))
    assert {59, 60, 61, 62, 63, 65} <= set(nry) and 64 not in nry     # 64 = zakończenie budowane z danych
    assert all(n in nry for n in engine.PPTX_DODATKI) and 65 in engine.PPTX_DODATKI and 60 not in engine.PPTX_DODATKI


def test_zakonczenie_z_podziekowaniem_idzie_na_koniec():
    src = open(os.path.join(WORK, "src", "app", "engine.py"), encoding="utf8").read()
    assert 'back = [x for x in extra if x == "t65"]' in src and "t60" not in src


# --- polecenia: agent i czat -----------------------------------------------------------------------------------------
def _model_i_spec(tmp_path):
    if not (os.path.exists(ORYG) and SPEC_STRATEGIA and os.path.exists(SPEC_STRATEGIA)):
        pytest.skip("brak oryginału strategii albo DK_TEST_SPEC")
    model = pptx_convert.extract(ORYG, str(tmp_path))
    spec = json.load(open(SPEC_STRATEGIA, encoding="utf8"))
    spec.setdefault("bledy_tekstu", [{"slajd": 12, "rodzaj": "sklejone", "jest": "komunikacjaod", "propozycja": "komunikacja od",
                                      "kontekst": "x", "pewnosc": "wysoka"}])
    return model, spec


def _czat(model, spec, **kw):
    return engine.ai_prompt_pptx("DK.pptx", ORYG, model, spec, ["Sprawdź najpierw: slajd 12 - coś"],
                                 {"tekst": "Treść: 100% akapitów (201/201) przeniesionych."}, {"szczegoly": []},
                                 r"C:\wynik\DK.pptx", cel="wiernie", dane=DANE, **kw)


def test_czat_ma_role_ksztalty_bledy_i_miesci_sie(tmp_path):
    model, spec = _model_i_spec(tmp_path)
    t = _czat(model, spec)
    for s in ("[hasło]", "[liczba]", "[wniosek]", "[tytuł]", "[etykieta nad tytułem]", "KSZTAŁT TREŚCI -> WZÓR Z SZABLONU",
              "MOŻLIWE BŁĘDY W TEKŚCIE ORYGINAŁU", "FORMAT ODPOWIEDZI", "Jeśli nie masz pliku prezentacji ani zrzutów", "„dla agenta”"):
        assert s in t, s
    # uwaga: sam punkt „Sprawdź pokrycie…” (PROMPTY.md D) zawiera tekst „(dalsza część … pominięta)” - szukamy znaczników ucięcia
    assert "(dalsza część wyniku pominięta" not in t and "(dalsza część oryginału pominięta" not in t
    assert "PLIKI NA KOMPUTERZE" not in t and "KROK 0" not in t and "verify" not in t and "spec_konwersja" not in t
    assert "Program ułożył slajdy automatycznie" in t and "Program przełożył" not in t
    assert len(t) <= engine.LIMIT_POLECENIE, len(t)
    print("dlugosc polecenia dla czatu:", len(t))
    assert t.index("UWAGI PROGRAMU") < t.index("MOŻLIWE BŁĘDY W TEKŚCIE ORYGINAŁU (program")   # w czacie błędy PO uwagach


def test_czat_z_planszami_zastepuje_zdanie_o_braku_wygladu(tmp_path):
    model, spec = _model_i_spec(tmp_path)
    t = _czat(model, spec, plansze={"folder": r"C:\wynik\plansze", "pliki": ["a.png"] * 8})
    assert 'ZAŁĄCZNIKI: dołącz do tej wiadomości obrazy z folderu "C:\\wynik\\plansze" (8 plików)' in t
    assert "Nie masz dostępu do plików, więc" not in t and "„dla agenta”" in t


def test_plikow_liczba_mnoga():
    assert [engine._plikow(n) for n in (1, 2, 5, 12, 22, 25)] == ["1 plik", "2 pliki", "5 plików", "12 plików", "22 pliki", "25 plików"]


def test_czat_ucina_nazwanie_i_trzyma_limit(tmp_path, monkeypatch):
    model, spec = _model_i_spec(tmp_path)
    monkeypatch.setattr(engine, "LIMIT_POLECENIE", 20000)
    monkeypatch.setattr(engine, "LIMITY_ZAPASOWE", ((3000, 3000), (1000, 1000)))
    t = _czat(model, spec)
    assert "(dalsza część wyniku pominięta" in t and "(dalsza część oryginału pominięta" in t and len(t) < 30000


def test_agent_punkty_w_liniach_i_bledy_przed_uwagami(tmp_path):
    model, spec = _model_i_spec(tmp_path)
    t = engine.ai_prompt_agent_pptx("DK.pptx", ORYG, r"C:\wynik\DK.pptx", str(tmp_path), spec,
                                    ["Sprawdź najpierw: slajd 3 - x", "inna uwaga"], cel="wiernie", dane=DANE)
    assert t.count("\n") >= 12
    assert t.startswith("Nie masz dostępu do plików i skryptów") and (chr(10) + "KROK 0") in t and "CO MASZ ZROBIĆ" in t and "\n1. ZANIM COKOLWIEK POPRAWISZ" in t
    assert t.index("MOŻLIWE BŁĘDY W TEKŚCIE ORYGINAŁU") < t.index("UWAGI PROGRAMU")
    assert "dopracowanie.md" in t and "KSZTAŁT TREŚCI -> WZÓR Z SZABLONU" in t and "spec_program.json" in t
    assert "[hasło]" not in t and "ORYGINAŁ (tekst slajdów)" not in t   # agent czyta pliki sam
    for stare in ("zamiany zdań na hasła", "wyjmowania liczb", "karta-artykuł w Lato"):
        assert stare not in t


def test_agent_bez_bledow_pisze_o_tym():
    t = engine.ai_prompt_agent_pptx("a.pptx", "o.pptx", "a.pptx", ".", {"bledy_tekstu": []}, [], cel="skroc", dane=DANE)
    assert "program nie znalazł - przeczytaj slajdy sam" in t and "UWAGI PROGRAMU" not in t
    assert "około 25 slajdów" in t


# --- uwagi -----------------------------------------------------------------------------------------------------------
def _blad(i, pew="wysoka"):
    return {"slajd": i, "rodzaj": "literowka", "jest": "słowo%d" % i, "propozycja": "slowo", "kontekst": "x", "pewnosc": pew}


def test_uwagi_okno_blok_bledow_na_poczatku_max_5_linii():
    bledy = [_blad(i) for i in range(1, 4)] + [_blad(i, "srednia") for i in range(4, 9)]
    opisy = [engine._lint_opis(u) for u in bledy]
    uwagi = ["Treść: 100% akapitów (1/1)", "Układ: ok", engine.NAGLOWEK_BLEDOW + ": 8 (x)"] + opisy + ["…i 2 innych podejrzeń o średniej pewności", "Inna uwaga"]
    out, blok = engine.uwagi_okno(uwagi, bledy)
    assert out[:2] == ["Treść: 100% akapitów (1/1)", "Układ: ok"]
    assert out[2].startswith(engine.NAGLOWEK_BLEDOW + ": 8") and len(blok) == 1 + 5 + 1
    assert blok[-1] == "…i 3 kolejnych w poleceniu dla AI"
    assert "wysoka" not in " ".join(blok) and "(średnia pewność - do sprawdzenia)" in blok[4]    # wysokie pierwsze
    assert out[-1] == "Inna uwaga" and not any("innych podejrzeń" in x for x in out)
    assert sum(1 for x in out if x.startswith("Slajd ")) == 5
    assert engine.uwagi_okno(["a"], []) == (["a"], [])


def test_uwagi_dla_ai_kolejnosc_limit_i_brak_linii_lintu():
    bledy = [_blad(1)]
    opisy = [engine._lint_opis(u) for u in bledy]
    uw = ["x1", "Do sprawdzenia - y", engine.NAGLOWEK_BLEDOW + ": 1 (x)"] + opisy + ["Sprawdź najpierw: slajd 2 - z", "x2"]
    out = engine._uwagi_dla_ai(uw, bledy)
    assert out == ["Do sprawdzenia - y", "Sprawdź najpierw: slajd 2 - z", "x1", "x2"]
    dlugie = engine._uwagi_dla_ai(["u%d" % i for i in range(60)], [])
    assert len(dlugie) == engine.LIMIT_UWAG + 1 and dlugie[-1].startswith("…i 20 kolejnych")


# --- folder produktu: punkty o błędach -------------------------------------------------------------------------------
def test_ai_prompt_folderowy_ma_punkty_o_bledach():
    t = engine.ai_prompt("a.pptx", "folder", ["u"])
    assert "5) ewidentne błędy tekstu (sklejone słowa, literówki, interpunkcja) wypisz jako „było -> jest”" in t
    assert "Oświadczeń, nazw prawnych, liczb i danych z kart wprowadzenia nie zmieniasz" in t
    assert "6) sieroty i spójniki na końcu linii usuwa kontrola z instrukcji" in t and "„Tekst - problemy: 0”" in t
    assert "3) nie zmieniaj układu, kolorów ani czcionek" in t
    c = engine.ai_prompt_chat("a.pptx", {"smaki": [], "copy": []}, {"slides": []}, [])
    assert "7. ewidentne błędy tekstu (sklejone słowa, literówki, interpunkcja) wypisz jako „było -> jest”" in c
    assert "sieroty i spójniki" not in c       # czat nie ma kontroli z instrukcji


# --- verify -> kody, pętla "oka" -------------------------------------------------------------------------------------
def test_usterki_verify_kody():
    qa = {"szczegoly": ["s3 ZAWIESZKA na koncu linii: '...w'", "s3 SIEROTA (1 slowo w ostatniej linii): 'x'", "s5 PRZEPELNIENIE pola +10pt: 'a'",
                        "s7 przy dolnej krawedzi: 'x'", "s8 TEKST NA GRAFICE (30%): 'a' x b", "s9 MYSLNIK na poczatku linii: '- a'",
                        "s10 SIEROTA w naglowku: 'x'", "smieci"]}
    u = engine.usterki_verify(qa)
    assert [x["kod"] for x in u[3]] == ["ZAWIESZKA", "SIEROTA"] and u[5][0]["kod"] == "PRZEPELNIENIE" and u[5][0]["waga"] == 3
    assert u[7][0]["kod"] == "PRZY_KRAWEDZI" and u[8][0]["kod"] == "KOLIZJA" and u[9][0]["kod"] == "ZAWIESZKA" and u[10][0]["kod"] == "SIEROTA"
    assert engine.usterki_verify({}) == {} and engine.usterki_verify(None) == {}


class Atrapa:
    """Świat atrap dla petla_oka: slajd to {"v": wariant}; wariant "ok" ma 0 usterek, "zly" ma wskazane."""
    def __init__(self, slajdy, usterki, popraw_na, wykonano=True):
        self.slajdy = slajdy              # lista wariantów początkowych
        self.usterki = usterki            # {(nr, wariant): [waga, ...]}
        self.popraw_na = popraw_na        # {nr: nowy wariant}
        self.budowy = 0
        self.wykonano = wykonano
        self.popraw_wywolania = []

    def spec(self):
        return {"slides": [{"type": "uklad", "v": v} for v in self.slajdy], "output": "x.pptx"}

    def ocen(self, wynik, spec):
        qa = wynik[1]
        if not qa.get("wykonano", True):
            return {}
        out = {}
        for i, sl in enumerate(spec["slides"], 1):
            ws = self.usterki.get((i, sl["v"]), [])
            if ws:
                out[i] = [{"kod": "PUSTY_DOL", "opis": "o%d" % i, "waga": w, "zrodlo": "oko"} for w in ws]
        return out

    def zbuduj(self, spec, r, faza):
        self.budowy += 1
        return ("x.pptx", {"wykonano": self.wykonano}, [])

    def popraw(self, path, kody):
        self.popraw_wywolania.append(dict(kody))
        sp = json.load(open(path, encoding="utf8"))
        zm = []
        for nr in kody:
            nowy = self.popraw_na.get(nr)
            if nowy and sp["slides"][nr - 1]["v"] != nowy:
                sp["slides"][nr - 1]["v"] = nowy
                zm.append(nr)
        json.dump(sp, open(path, "w", encoding="utf8"))
        return zm


def _petla(tmp_path, at, **kw):
    sp = at.spec()
    return engine.petla_oka(sp, ("x.pptx", {"wykonano": True}, []), at.zbuduj, at.ocen, at.popraw, str(tmp_path / "s.json"), **kw)


def test_petla_zostawia_lepszy_wariant(tmp_path):
    at = Atrapa(["a", "a", "a"], {(2, "a"): [3], (3, "a"): [2, 2]}, {2: "ok", 3: "ok"})
    w = _petla(tmp_path, at)
    assert [s["v"] for s in w["spec"]["slides"]] == ["a", "ok", "ok"] and w["zmienione"] == [2, 3] and w["odrzucone"] == []
    assert w["rundy"] == 1 and at.budowy == 1 and w["ocena"] == {}
    assert at.popraw_wywolania == [{2: ["PUSTY_DOL"], 3: ["PUSTY_DOL"]}]


def test_petla_cofa_gorszy_i_remis_i_buduje_ponownie(tmp_path):
    at = Atrapa(["a", "a", "a"], {(1, "a"): [3], (1, "b"): [3], (2, "a"): [2], (2, "b"): [2, 3], (3, "a"): [3]}, {1: "b", 2: "b", 3: "ok"})
    w = _petla(tmp_path, at, rundy=1)
    assert [s["v"] for s in w["spec"]["slides"]] == ["a", "a", "ok"]     # 1: remis -> cofnięte; 2: gorszy -> cofnięty; 3: lepszy
    assert w["zmienione"] == [3] and w["odrzucone"] == [1, 2]
    assert at.budowy == 2                                                # próba + odbudowa po cofnięciu


def test_petla_nie_rusza_slajdu_gdy_pismo_hasel_spadlo(tmp_path):
    at = Atrapa(["a"], {(1, "a"): [3]}, {1: "ok"})
    w = _petla(tmp_path, at, pismo=lambda sl: 24 if sl["v"] == "a" else 18)
    assert w["spec"]["slides"][0]["v"] == "a" and w["odrzucone"] == [1] and w["zmienione"] == []
    at = Atrapa(["a"], {(1, "a"): [3]}, {1: "ok"})
    w = _petla(tmp_path, at, pismo=lambda sl: 20 if sl["v"] == "a" else 20)    # pismo bez zmiany - zostaje nowy
    assert w["spec"]["slides"][0]["v"] == "ok"


def test_petla_waga_1_nie_uruchamia_przebudowy_i_zostaje_w_ocenie(tmp_path):
    at = Atrapa(["a", "a"], {(1, "a"): [1], (2, "a"): [2]}, {1: "ok", 2: "ok"})
    w = _petla(tmp_path, at)
    assert at.popraw_wywolania == [{2: ["PUSTY_DOL"]}] and w["zmienione"] == [2]
    assert w["ocena"][1][0]["waga"] == 1                                 # zostaje do "Sprawdź najpierw"


def test_petla_druga_runda_i_limit_rund(tmp_path):
    class Dwa(Atrapa):     # po 1. rundzie slajd 2 nadal ma usterkę (inny kod), po 2. znika
        pass
    at = Dwa(["a", "a"], {(1, "a"): [3], (2, "a"): [3], (2, "b"): [2]}, {1: "ok", 2: "b"})
    w = _petla(tmp_path, at, rundy=2)
    assert w["spec"]["slides"][1]["v"] == "b" and w["spec"]["slides"][0]["v"] == "ok"      # 2: 3 -> 2 jest lepsze
    assert w["rundy"] == 1 and at.budowy == 1                                              # slajd 2 raz próbowany; nr w "proby"
    at = Atrapa(["a"], {(1, "a"): [3]}, {1: "a"})                                          # brak innego wariantu
    w = _petla(tmp_path, at)
    assert w["rundy"] == 0 and at.budowy == 0 and w["zmienione"] == []


def test_petla_odrzuca_zmiane_liczby_slajdow_i_wyjatek_popraw(tmp_path):
    at = Atrapa(["a", "a"], {(1, "a"): [3]}, {})
    sp = at.spec()
    def zla(path, kody):
        s = json.load(open(path, encoding="utf8"))
        s["slides"].append({"type": "uklad", "v": "n"})
        json.dump(s, open(path, "w", encoding="utf8"))
        return [1]
    w = engine.petla_oka(sp, ("x.pptx", {"wykonano": True}, []), at.zbuduj, at.ocen, zla, str(tmp_path / "s.json"))
    assert len(w["spec"]["slides"]) == 2 and at.budowy == 0
    def wyjatek(path, kody):
        raise RuntimeError("boom")
    w = engine.petla_oka(at.spec(), ("x.pptx", {"wykonano": True}, []), at.zbuduj, at.ocen, wyjatek, str(tmp_path / "s.json"))
    assert w["zmienione"] == [] and at.budowy == 0


def test_petla_cofa_gdy_powerpoint_nie_oddal_zrzutow(tmp_path):
    at = Atrapa(["a"], {(1, "a"): [3]}, {1: "ok"}, wykonano=False)
    w = _petla(tmp_path, at)
    assert w["spec"]["slides"][0]["v"] == "a" and w["odrzucone"] == [1] and at.budowy == 2


def test_oko_dla_pptx_pomija_petle_bez_funkcji(monkeypatch):
    komunikaty = []
    monkeypatch.delattr(pptx_convert, "popraw_po_renderze", raising=False)
    w = engine._oko_dla_pptx({"slides": []}, ("x", {}, []), ".", {}, lambda *a: None, komunikaty.append, 10)
    assert w is None and any("niedostępne" in k or "pomijam" in k for k in komunikaty)


# --- plansze ---------------------------------------------------------------------------------------------------------
def test_plansze_po_6_slajdow_z_numerami(tmp_path):
    from PIL import Image
    png = tmp_path / "png"
    png.mkdir()
    for i in range(1, 14):
        Image.new("RGB", (1600, 900), (255, 255, 255)).save(png / ("s%02d.png" % i))
    out = tmp_path / "plansze"
    out.mkdir()
    stare = out / "wynik_01-06.png"
    stare.write_bytes(b"stary")
    inne = out / "moje.png"
    inne.write_bytes(b"x")
    pliki = engine.zrob_plansze(str(png), str(out))
    assert [os.path.basename(p) for p in pliki] == ["wynik_01-06.png", "wynik_07-12.png", "wynik_13-13.png"]
    im = Image.open(pliki[0])
    assert im.size[0] == 1920 and 1500 < im.size[1] < 1800
    assert Image.open(pliki[2]).size[1] < im.size[1] / 2 + 40
    assert inne.read_bytes() == b"x"                                           # cudzych plików nie ruszamy
    assert engine.zrob_plansze(str(tmp_path / "brak"), str(out)) == []


# --- CLI -------------------------------------------------------------------------------------------------------------
def test_cli_ma_flagi_bez_oka_i_robocze(capsys):
    import cli
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    h = capsys.readouterr().out
    assert "--bez-oka" in h and "--robocze" in h


def test_robocze_wymuszone(tmp_path):
    try:
        engine.set_robocze(str(tmp_path / "r"))
        assert engine._pptx_rob(r"C:\gdzies\a.pptx") == str(tmp_path / "r") and (tmp_path / "r").is_dir()
    finally:
        engine.set_robocze("")
    assert engine._pptx_rob.__doc__


# --- lista uwag w oknie: krótka, pełne brzmienie zostaje w poleceniach i raporcie ------------------------------------------
UWAGI_STRATEGIA = [
    "Treść: 100% akapitów (201/201) przeniesionych", "Układ: osobne napisy 80 z 80, kolejność góra-dół bez zmian, slajdów tyle samo (43)",
    "Sprawdź najpierw: slajd 12 - karta ma 57% wysokości pusta pod tekstem, a obok stoi wypełniona",
    "Możliwe błędy w tekście oryginału: 2 (program ich nie poprawia - popraw w pliku albo zleć AI)",
    "Slajd 12: „komunikacjaod” wygląda na sklejone słowa - może „komunikacja od”?",
    "Slajd 38: błąd interpunkcji w „odjechała..” - powinno być „odjechała…”.",
    "Pominięto 85 obrazów powtarzających się na slajdach (logo, ozdobniki) albo mniejszych niż 160 px.",
    "Slajd 4: dodałem wizualizacje z biblioteki produktów - Pralinowe: słownik: Pralinowe = deserowe (Banoffee kakao, Tiramisu). Sprawdź dobór.",
    "Slajd 5: dodałem wizualizacje z biblioteki produktów - Protein: słownik: Protein = IG (Proteina banoffee). Sprawdź dobór.",
    "Dobór układu z pomiaru: na slajdach 41 (pad kart x0.75) wybrałem wariant inny niż domyślny, bo miał mniej usterek.",
    "Ułożyłem w klocki szablonu marki (liczby, pasy-wnioski, kafle z ikonami, etykiety) slajdy: 2, 3, 6, 7, 9, 10, 12, 14, 15, 16, 18, 19, "
    "20, 21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41. Wzory z szablonu: slajd 2: Okazje spożycia (wzór: slajd 56 "
    "szablonu); …i 17 innych (decyzje-szablon.json). Ikony dobrane ze słownika po słowach - sprawdź, czy pasują; lista decyzji: decyzje-szablon.json.",
    "Grafiki: przeniesiono 15 (całe, bez przycinania). Tekst na zrzutach ekranu zostaje obrazem - nie jest przepisywany automatycznie.",
    "Oryginał jest pisany wersalikami: ustawiłem zwykłą wielkość liter w 62 wierszach (np. „WSTĘP” -> „Wstęp”; „EWALUACJA PORTFOLIO” -> "
    "„Ewaluacja portfolio”). Sprawdź nazwy własne i skróty - pełna lista: wielkosc-liter.txt.",
    "Animacje, przejścia i tła slajdów z oryginału nie są przenoszone - to kwestia stylu, nie treści."]


def test_lista_uwag_w_oknie_jest_krotka():
    bledy = [{"slajd": 12, "rodzaj": "sklejone", "jest": "komunikacjaod", "propozycja": "komunikacja od", "kontekst": "x", "pewnosc": "wysoka"},
             {"slajd": 38, "rodzaj": "interpunkcja", "jest": "odjechała..", "propozycja": "odjechała…", "kontekst": "x", "pewnosc": "wysoka"}]
    # opisy błędów jak z lint_tekst (stoją w uwagach z compose)
    uw = list(UWAGI_STRATEGIA)
    okno, blok = engine.uwagi_okno(uw, bledy)
    teraz = [x for x in okno if not x.startswith(("Treść:", "Układ:"))]
    assert len(teraz) <= 8, (len(teraz), teraz)
    assert all(len(x) <= 180 for x in okno)
    tekst = "\n".join(okno)
    assert "Ułożyłem w układy z szablonu marki 31 slajdów (hasła, liczby, wnioski)." in okno
    assert "wzór" not in tekst and "Dobór układu" not in tekst and "dodałem wizualizacje" not in tekst and "Animacje" not in tekst
    assert "Sprawdź najpierw: slajd 12" in tekst and okno[2].startswith(engine.NAGLOWEK_BLEDOW)
    assert any(x.startswith("Oryginał był pisany wersalikami: w 62 wierszach") for x in okno)
    assert uw == UWAGI_STRATEGIA                        # lista pełna (polecenia, raport.json) nie jest zmieniana
    # polecenie dla agenta dostaje pełne brzmienie
    ag = engine.ai_prompt_agent_pptx("a.pptx", "o.pptx", "a.pptx", ".", {"bledy_tekstu": bledy}, uw)
    assert "Ułożyłem w klocki szablonu marki" in ag and "Dobór układu z pomiaru" in ag and "dodałem wizualizacje" in ag


# --- v15 (13.10, po teście na Claude): układ, granice korekty, praca bez skryptów - w 4 poleceniach z okna -----------------
BLEDY2 = [{"slajd": 12, "rodzaj": "sklejone", "jest": "komunikacjaod", "propozycja": "komunikacja od", "kontekst": "x", "pewnosc": "wysoka"},
          {"slajd": 38, "rodzaj": "interpunkcja", "jest": "odjechała..", "propozycja": "odjechała…", "kontekst": "x", "pewnosc": "wysoka"}]
WYNIK = ORYG.replace(".pptx", " - nowy styl.pptx")
ROB = os.path.join(os.path.dirname(ORYG), "_robocze", "DK_co_dalej_update")


def _cztery(cel="wiernie"):
    """Cztery polecenia, które okno daje do skopiowania: czat i agent po konwersji, czat i agent przy dopracowaniu
    (bez plików na dysku: pusty model i spec, uwagi i błędy jak dla strategii)."""
    spec = {"slides": [], "bledy_tekstu": BLEDY2}
    rozp = {"rodzaj": "wynik_programu", "spec": None}
    pr = {"teksty": [(1, ["Tytuł"]), (19, ["Białko –", "1,2 g/kg"])]}
    kopia = WYNIK.replace(".pptx", " - dopracowana.pptx")
    return {
        "czat pptx": engine.ai_prompt_pptx(os.path.basename(WYNIK), ORYG, {"slajdy": [], "h_cm": 19.05}, spec, UWAGI_STRATEGIA,
                                           {"tekst": "Treść: 100% akapitów (201/201) przeniesionych."}, {"szczegoly": []}, WYNIK,
                                           cel=cel, dane=DANE),
        "agent pptx": engine.ai_prompt_agent_pptx(os.path.basename(WYNIK), ORYG, WYNIK, ROB, spec, UWAGI_STRATEGIA, cel=cel, dane=DANE),
        "czat dopracowanie": engine.ai_prompt_dopracowanie(WYNIK, rozp, pr, UWAGI_STRATEGIA, BLEDY2),
        "agent dopracowanie": engine.ai_prompt_agent_dopracowanie(WYNIK, kopia, ROB, rozp, UWAGI_STRATEGIA, BLEDY2),
    }


@pytest.mark.parametrize("cel", ["wiernie", "rozwin", "skroc"])
def test_cztery_polecenia_maja_uklad_granice_i_galaz_bez_skryptow(cel):
    for n, t in _cztery(cel).items():
        for s in ("PO KOREKCIE TEKSTU PRZEJDŹ SLAJD PO SLAJDZIE I NAPRAW UKŁAD", "pusty dół slajdu (ponad 1/3 wysokości)",
                  "urwane na końcu myślnikiem, przecinkiem lub dwukropkiem", "karta pusta w ponad połowie obok pełnej",
                  "NIE MASZ DOSTĘPU DO PLIKÓW I SKRYPTÓW SKILLA", "Pracuj bezpośrednio na otwartej prezentacji",
                  "hasło co najmniej 16 pt, dopisek 13 pt", "NIE PRZEREDAGOWUJESZ", "„do decyzji autora”",
                  "Sprawdź najpierw: slajd 12 - karta ma 57% wysokości pusta"):        # lista z pomiaru, od której polecenie każe zacząć
            assert s in t, (cel, n, s)
        assert t.count("PO KOREKCIE TEKSTU PRZEJDŹ") == 1 and t.count("NIE MASZ DOSTĘPU DO PLIKÓW I SKRYPTÓW") == 1, (cel, n)
        assert t.index("PO KOREKCIE TEKSTU PRZEJDŹ") < t.index("UWAGI PROGRAMU"), (cel, n)
        assert len(t) <= engine.LIMIT_POLECENIE, (cel, n, len(t))


def test_czat_nadal_nie_dostaje_polecen_dla_plikow():
    c = _cztery()
    for n in ("czat pptx", "czat dopracowanie"):
        for s in ("KROK 0", "verify", "spec_konwersja", "render.ps1", "build_dk", "dopracowanie.md"):
            assert s not in c[n], (n, s)
    assert "FORMAT ODPOWIEDZI" in c["czat dopracowanie"] and "z listy „Sprawdź najpierw”" in c["czat dopracowanie"]


@pytest.mark.parametrize("cel", ["wiernie", "rozwin", "skroc"])
def test_dopisane_bloki_to_najwyzej_cwierc_polecenia_agenta(cel):
    """Limit z 13.10: polecenie nie rośnie o więcej niż ok. 25%. Liczone na poleceniach agenta (najkrótsze; czat ma do
    tego tekst slajdów): dopisane = blok układu + gałąź bez skryptów + zdanie o przeredagowaniu (+ skrót punktu o błędach)."""
    p = polecenia
    c = _cztery(cel)
    dop = len(p.UKLAD) + len(p.BEZ_SKRYPTOW) + (len(p.GRANICE) if cel == "wiernie" else len(p.BLEDY_KROTKO))
    for n, d in (("agent pptx", dop), ("agent dopracowanie", len(p.UKLAD) + len(p.BEZ_SKRYPTOW) + len(p.GRANICE))):
        przed = len(c[n]) - d
        assert d <= 0.26 * przed, (cel, n, d, przed, round(d / przed, 3))


def test_polecenia_dok_bierze_teksty_ze_skilla():
    import polecenia_dok
    assert polecenia_dok.punkty_dopracowanie is polecenia.punkty_dopracowanie and polecenia_dok.pracuj_na is polecenia.pracuj_na
    assert polecenia_dok.FORMAT_DOPRACOWANIE is polecenia.FORMAT_DOPRACOWANIE
    assert polecenia_dok.punkty(False) == polecenia.polecenie_ai("dokument", pliki=False)
    assert polecenia_dok.punkty(True) == polecenia.polecenie_ai("dokument", pliki=True) == engine._punkty("dokument", {}, True, "dokument")
