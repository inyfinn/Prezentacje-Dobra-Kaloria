# -*- coding: utf-8 -*-
"""Testy oko.py (ocena zrzutu slajdu z samego obrazu).

    python -m pytest -p no:cacheprovider test_oko.py -q

Obrazy syntetyczne: PIL rysuje bialy slajd 1600 x 900 z kremowymi kartami (FDF8EC), zielenia marki (0F763E) i
"tekstem" (ciemne paski 3B2A20). Zadnych plikow z dysku usera, zadnego PowerPointa ani modeli AI.
"""
import os
import sys
import time

import pytest
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oko  # noqa: E402

W, H = 1600, 900
BIEL, KREM, ZIEL, TEKST = (255, 255, 255), (253, 248, 236), (15, 118, 62), (59, 42, 32)


def kody(w):
    return sorted(u["kod"] for u in w["usterki"])


def zapisz(im, tmp_path, nazwa="s01.png"):
    p = str(tmp_path / nazwa)
    im.save(p)
    return p


class Slajd:
    """Rysuje slajd w ulamkach wysokosci / szerokosci."""

    def __init__(self, tlo=BIEL, tytul=True, logo=True, numer=True):
        self.im = Image.new("RGB", (W, H), tlo)
        self.d = ImageDraw.Draw(self.im)
        if logo:
            self.d.rectangle([W * 0.90, H * 0.05, W * 0.96, H * 0.11], fill=ZIEL)
        if numer:
            self.d.rectangle([W * 0.94, H * 0.945, W * 0.96, H * 0.96], fill=TEKST)
        if tytul:
            self.tekst(0.07, 0.10, 0.45, 0.13)

    def rect(self, x0, y0, x1, y1, kolor=KREM):
        self.d.rectangle([x0 * W, y0 * H, x1 * W - 1, y1 * H - 1], fill=kolor)

    def tekst(self, x0, y0, x1, y1):
        """Wiersze tekstu (paski) od y0 do y1 w ulamkach."""
        y = y0
        while y + 0.018 <= y1 + 1e-9:
            self.d.rectangle([x0 * W, y * H, x1 * W, (y + 0.018) * H], fill=TEKST)
            y += 0.034

    def karta(self, x0, y0, x1, y1, tekst_do=None, kolor=KREM):
        """Karta; tekst_do = do jakiej wysokosci (ulamek wysokosci karty) siega tekst; None = prawie do konca."""
        self.rect(x0, y0, x1, y1, kolor)
        do = 0.94 if tekst_do is None else tekst_do
        self.tekst(x0 + 0.02, y0 + 0.03, x1 - 0.03, y0 + (y1 - y0) * do)
        return self

    def zapisz(self, tmp_path, nazwa="s01.png"):
        return zapisz(self.im, tmp_path, nazwa)


def trzy_karty(s, y0=0.30, y1=0.90, tekst_do=(None, None, None)):
    for i, td in enumerate(tekst_do):
        x0 = 0.07 + i * 0.30
        s.karta(x0, y0, x0 + 0.27, y1, td)
    return s


# --- poprawny slajd, pominiecia -------------------------------------------------------------------------------------
def test_poprawny_slajd_bez_usterek(tmp_path):
    p = trzy_karty(Slajd()).zapisz(tmp_path)
    w = oko.ocen(p)
    assert w["usterki"] == [], w["usterki"]
    m = w["miary"]
    assert len(m["karty"]) == 3
    assert m["dol_pusty"] == pytest.approx(0.10, abs=0.02)
    assert m["przy_krawedzi"] is False
    assert m["tresc_bbox"][3] == pytest.approx(0.90, abs=0.02)
    for c in m["karty"]:
        assert c["pusta"] < 0.15


def test_kontrakt_kluczy_i_ulamkow(tmp_path):
    p = trzy_karty(Slajd()).zapisz(tmp_path)
    m = oko.ocen(p)["miary"]
    for k in ("dol_pusty", "wypelnienie", "karty", "przy_krawedzi", "tresc_bbox"):
        assert k in m
    for c in m["karty"]:
        assert {"x0", "y0", "x1", "y1", "pusta"} <= set(c)
        assert 0 <= c["x0"] < c["x1"] <= 1 and 0 <= c["y0"] < c["y1"] <= 1
    assert all(0 <= v <= 1 for v in m["tresc_bbox"])


def test_wspolrzedne_nie_zaleza_od_rozdzielczosci(tmp_path):
    s = trzy_karty(Slajd())
    p1 = s.zapisz(tmp_path, "s01.png")
    mala = s.im.resize((800, 450), Image.LANCZOS)
    p2 = zapisz(mala, tmp_path, "s02.png")
    a, b = oko.ocen(p1)["miary"], oko.ocen(p2)["miary"]
    assert a["dol_pusty"] == pytest.approx(b["dol_pusty"], abs=0.02)
    assert a["karty"][0]["x0"] == pytest.approx(b["karty"][0]["x0"], abs=0.02)
    assert kody(oko.ocen(p1)) == kody(oko.ocen(p2)) == []


def test_zielony_slajd_pominiety(tmp_path):
    s = Slajd(tlo=ZIEL, tytul=False, logo=False, numer=False)
    s.tekst(0.07, 0.40, 0.60, 0.46)  # jedno haslo wysoko, dol pusty
    w = oko.ocen(s.zapisz(tmp_path))
    assert w["usterki"] == []
    assert w["miary"]["pominiety"] == "tlo_zielone"


def test_okladka_pol_na_pol_pominieta(tmp_path):
    s = Slajd(tytul=False, logo=False, numer=False)
    s.rect(0, 0, 0.5, 1.0, ZIEL)  # zielona polowa, tytul po bialej stronie wysoko
    s.tekst(0.58, 0.30, 0.90, 0.36)
    w = oko.ocen(s.zapisz(tmp_path))
    assert w["usterki"] == [] and w["miary"]["pominiety"] == "tlo_zielone"


def test_zielona_karta_na_bialym_nie_jest_zielonym_slajdem(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.93, 0.90, None, kolor=ZIEL)
    w = oko.ocen(s.zapisz(tmp_path))
    assert "pominiety" not in w["miary"]
    assert w["usterki"] == []


# --- PUSTY_DOL ------------------------------------------------------------------------------------------------------
def test_pusty_dol(tmp_path):
    p = trzy_karty(Slajd(), y1=0.50).zapisz(tmp_path)
    w = oko.ocen(p)
    u = [x for x in w["usterki"] if x["kod"] == "PUSTY_DOL"]
    assert len(u) == 1
    assert u[0]["waga"] == 2
    assert 45 <= int(u[0]["opis"].split("%")[0]) <= 55
    assert "pod treścią jest puste" in u[0]["opis"]


def test_pusty_dol_waga_zalezy_od_wielkosci(tmp_path):
    lekki = oko.ocen(trzy_karty(Slajd(), y1=0.68).zapisz(tmp_path, "a.png"))  # ok. 32 % pustego
    assert [u["waga"] for u in lekki["usterki"] if u["kod"] == "PUSTY_DOL"] == [1]
    ciezki = oko.ocen(trzy_karty(Slajd(), y1=0.38).zapisz(tmp_path, "b.png"))  # ok. 62 %
    assert [u["waga"] for u in ciezki["usterki"] if u["kod"] == "PUSTY_DOL"] == [3]


def test_pusty_dol_ponizej_progu_cisza(tmp_path):
    w = oko.ocen(trzy_karty(Slajd(), y1=0.75).zapisz(tmp_path))  # 25 % pustego
    assert "PUSTY_DOL" not in kody(w)


def test_stopka_zrodla_i_numer_nie_licza_sie_jako_tresc(tmp_path):
    s = trzy_karty(Slajd(), y1=0.50)
    s.tekst(0.07, 0.955, 0.30, 0.973)  # stopka zrodla nisko po lewej
    w = oko.ocen(s.zapisz(tmp_path))
    assert w["miary"]["dol_pusty"] == pytest.approx(0.50, abs=0.02)
    assert "PUSTY_DOL" in kody(w)


def test_logo_nie_liczy_sie_jako_tresc(tmp_path):
    s = Slajd(tytul=False)  # tylko logo i numer
    s.tekst(0.07, 0.10, 0.45, 0.13)
    s.karta(0.07, 0.30, 0.93, 0.90, None)
    w = oko.ocen(s.zapisz(tmp_path))
    assert w["miary"]["tresc_bbox"][0] == pytest.approx(0.07, abs=0.02)
    assert w["miary"]["tresc_bbox"][2] == pytest.approx(0.93, abs=0.02)


def test_dziwny_slajd_ze_specu_nie_wywala(tmp_path):
    p = trzy_karty(Slajd(), y1=0.45).zapisz(tmp_path)
    for dziwny in ("tekst", 5, [], {"type": None, "rows": "x"}, {"rows": [1, None, "q"]}):
        assert "PUSTY_DOL" in kody(oko.ocen(p, dziwny))


def test_pusty_dol_pomijany_dla_typu_i_cytatu(tmp_path):
    p = trzy_karty(Slajd(), y1=0.45).zapisz(tmp_path)
    assert "PUSTY_DOL" in kody(oko.ocen(p))
    assert "PUSTY_DOL" not in kody(oko.ocen(p, {"type": "section"}))
    assert "PUSTY_DOL" not in kody(oko.ocen(p, {"type": "statement"}))
    assert "PUSTY_DOL" not in kody(oko.ocen(p, {"type": "uklad", "rows": [{"k": "quote", "t": "x"}]}))
    assert "PUSTY_DOL" in kody(oko.ocen(p, {"type": "uklad", "rows": [{"k": "cols", "items": []}]}))


def test_slajd_z_panelem_na_cala_wysokosc_nie_ma_pustego_dolu(tmp_path):
    s = Slajd(tytul=False)
    s.rect(0.55, 0, 1.0, 1.0, KREM)  # zdjecie / panel do krawedzi
    s.tekst(0.07, 0.20, 0.45, 0.40)
    w = oko.ocen(s.zapisz(tmp_path))
    assert w["usterki"] == [], w["usterki"]


def test_kremowe_tlo_calego_slajdu_bez_alarmu(tmp_path):
    s = Slajd(tlo=KREM, tytul=False)
    s.tekst(0.20, 0.40, 0.80, 0.55)
    assert oko.ocen(s.zapisz(tmp_path))["usterki"] == []


# --- KARTA_PUSTA / KARTY_NIEROWNE -----------------------------------------------------------------------------------
def test_karta_pusta_obok_wypelnionej(tmp_path):
    p = trzy_karty(Slajd(), tekst_do=(None, 0.25, None)).zapisz(tmp_path)
    w = oko.ocen(p)
    assert kody(w) == ["KARTA_PUSTA"]
    u = w["usterki"][0]
    assert u["waga"] == 2
    assert "pusta" in u["opis"] and "%" in u["opis"]
    pusta = [c["pusta"] for c in w["miary"]["karty"]]
    assert pusta[1] > 0.6 and pusta[0] < 0.2 and pusta[2] < 0.2


def test_karta_calkiem_pusta_waga_3(tmp_path):
    p = trzy_karty(Slajd(), tekst_do=(None, 0.0, None))
    p.rect(0.37, 0.30, 0.64, 0.90, KREM)  # druga karta bez tekstu
    w = oko.ocen(p.zapisz(tmp_path))
    assert kody(w) == ["KARTA_PUSTA"] and w["usterki"][0]["waga"] == 3


def test_wszystkie_karty_rownie_puste_to_nie_karta_pusta(tmp_path):
    p = trzy_karty(Slajd(), y1=0.80, tekst_do=(0.3, 0.3, 0.3)).zapisz(tmp_path)
    assert "KARTA_PUSTA" not in kody(oko.ocen(p))


def test_wysrodkowana_zawartosc_karty_to_nie_pusta_karta(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.37, 0.90, None)
    s.rect(0.40, 0.30, 0.70, 0.90, KREM)
    s.tekst(0.45, 0.55, 0.65, 0.62)  # ikona / napis na srodku karty (jak wstawiony obraz)
    assert "KARTA_PUSTA" not in kody(oko.ocen(s.zapisz(tmp_path)))


def test_karty_nierowne(tmp_path):
    s = Slajd()
    s.rect(0.07, 0.30, 0.37, 0.90, KREM)
    s.tekst(0.09, 0.33, 0.35, 0.33 + 0.60 * 0.55)   # 55 % wysokosci karty: pusta 0.45, wiec nie "pelna"
    s.rect(0.40, 0.30, 0.70, 0.90, KREM)
    s.tekst(0.42, 0.33, 0.68, 0.33 + 0.60 * 0.18)   # 18 %
    w = oko.ocen(s.zapisz(tmp_path))
    assert kody(w) == ["KARTY_NIEROWNE"], w["usterki"]
    assert w["usterki"][0]["waga"] == 2


def test_rowne_karty_bez_alarmu(tmp_path):
    p = trzy_karty(Slajd(), tekst_do=(0.8, 0.7, 0.75)).zapisz(tmp_path)
    assert oko.ocen(p)["usterki"] == []


def test_karty_w_roznych_rzedach_nie_sa_porownywane(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.93, 0.55, None)      # szeroka karta u gory
    s.karta(0.07, 0.60, 0.37, 0.90, 0.25)      # druga linia: inne wysokosci nie powinny tworzyc rzedu z gorna
    assert "KARTA_PUSTA" not in kody(oko.ocen(s.zapisz(tmp_path)))


# --- PRZY_KRAWEDZI ---------------------------------------------------------------------------------------------------
def test_tresc_przy_prawej_krawedzi(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.985, 0.90, None)
    w = oko.ocen(s.zapisz(tmp_path))
    assert "PRZY_KRAWEDZI" in kody(w)
    assert w["miary"]["przy_krawedzi"] is True
    assert w["usterki"][0]["waga"] == 2 or any(u["kod"] == "PRZY_KRAWEDZI" and u["waga"] == 2 for u in w["usterki"])


def test_tresc_uciecta_krawedzia_waga_3(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.93, 0.90, None)
    s.rect(0.07, 0.93, 0.60, 1.0, TEKST)  # tekst wychodzi poza slajd
    w = oko.ocen(s.zapisz(tmp_path))
    u = [x for x in w["usterki"] if x["kod"] == "PRZY_KRAWEDZI"]
    assert len(u) == 1 and u[0]["waga"] == 3 and "ucięta" in u[0]["opis"]


def test_margines_poprawny_bez_alarmu(tmp_path):
    s = Slajd()
    s.karta(0.05, 0.30, 0.95, 0.90, None)  # 5 % od krawedzi: ok
    assert "PRZY_KRAWEDZI" not in kody(oko.ocen(s.zapisz(tmp_path)))


# --- GESTO / MALO_TRESCI ---------------------------------------------------------------------------------------------
def test_gesto_tekst_schodzi_na_sam_dol(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.93, 0.96, None)
    w = oko.ocen(s.zapisz(tmp_path))
    assert "GESTO" in kody(w)
    assert [u["waga"] for u in w["usterki"] if u["kod"] == "GESTO"] == [1]


def test_gesto_nie_dla_zdjecia(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.50, 0.90, None)
    # "zdjecie" na dole: szum kolorow w prostokacie
    import random
    rnd = random.Random(1)
    ph = Image.new("RGB", (int(0.4 * W), int(0.62 * H)))
    ph.putdata([(rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255)) for _ in range(ph.width * ph.height)])
    s.im.paste(ph, (int(0.53 * W), int(0.33 * H)))
    assert "GESTO" not in kody(oko.ocen(s.zapisz(tmp_path)))


def test_malo_tresci_jedno_drobne_zdanie(tmp_path):
    s = Slajd()
    s.karta(0.30, 0.27, 0.70, 0.34, None)  # drobna karta tuz pod tytulem: nie "plywa", ale prawie pusty slajd
    w = oko.ocen(s.zapisz(tmp_path))
    assert "MALO_TRESCI" in kody(w) and "PLYWAJACA_TRESC" not in kody(w)
    assert w["miary"]["wypelnienie"] < 0.25
    assert [u["waga"] for u in w["usterki"] if u["kod"] == "MALO_TRESCI"] == [2]


def test_malo_tresci_tylko_dla_slajdow_z_kartami(tmp_path):
    s = Slajd()
    s.tekst(0.07, 0.30, 0.45, 0.32)  # jedno zdanie, brak kart
    assert "MALO_TRESCI" not in kody(oko.ocen(s.zapisz(tmp_path)))


# --- PLYWAJACA_TRESC -------------------------------------------------------------------------------------------------
def test_plywajaca_tresc_pusto_nad_i_pod(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.36, 0.93, 0.64, 0.5)  # karta posrodku: ok. 24 % pustego pod tytulem i 36 % pod trescia
    w = oko.ocen(s.zapisz(tmp_path))
    u = [x for x in w["usterki"] if x["kod"] == "PLYWAJACA_TRESC"]
    assert len(u) == 1 and u[0]["waga"] == 2
    assert "pływa" in u[0]["opis"] and "%" in u[0]["opis"]
    assert "MALO_TRESCI" not in kody(w)  # to samo zjawisko, bez dubla
    m = w["miary"]
    assert m["pas_gora"] == pytest.approx(0.24, abs=0.02) and m["wys_tresci"] == pytest.approx(0.28, abs=0.02)


def test_plywajaca_tresc_wymaga_obu_pasow(tmp_path):
    gora_tylko = Slajd()
    gora_tylko.karta(0.07, 0.45, 0.93, 0.92, None)    # duzy pas pod tytulem, ale tresc dochodzi do dolu
    assert "PLYWAJACA_TRESC" not in kody(oko.ocen(gora_tylko.zapisz(tmp_path, "a.png")))
    dol_tylko = Slajd()
    dol_tylko.karta(0.07, 0.25, 0.93, 0.58, None)     # tresc tuz pod tytulem, pusty dol: to PUSTY_DOL, nie plywanie
    w = oko.ocen(dol_tylko.zapisz(tmp_path, "b.png"))
    assert "PLYWAJACA_TRESC" not in kody(w) and "PUSTY_DOL" in kody(w)
    lekko = Slajd()
    lekko.karta(0.07, 0.28, 0.93, 0.76, None)         # pasy ok. 16 % i 24 %: ponizej progu gory
    assert "PLYWAJACA_TRESC" not in kody(oko.ocen(lekko.zapisz(tmp_path, "c.png")))


def test_plywajaca_tresc_prog_blisko_granicy(tmp_path):
    ok = Slajd()
    ok.karta(0.07, 0.32, 0.93, 0.78, None)            # pas gora ok. 20 %, dol 22 %: alarm
    assert "PLYWAJACA_TRESC" in kody(oko.ocen(ok.zapisz(tmp_path, "a.png")))
    brak = Slajd()
    brak.karta(0.07, 0.29, 0.93, 0.78, None)          # pas gora ok. 17 %: bez alarmu
    assert "PLYWAJACA_TRESC" not in kody(oko.ocen(brak.zapisz(tmp_path, "b.png")))


def test_plywajaca_tresc_nie_dla_typow_luznych_i_bez_kart(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.36, 0.93, 0.64, 0.5)
    p = s.zapisz(tmp_path)
    assert "PLYWAJACA_TRESC" in kody(oko.ocen(p))
    assert "PLYWAJACA_TRESC" not in kody(oko.ocen(p, {"type": "statement"}))
    assert "PLYWAJACA_TRESC" not in kody(oko.ocen(p, {"type": "uklad", "rows": [{"k": "quote", "t": "x"}]}))
    bez = Slajd()
    bez.tekst(0.07, 0.40, 0.60, 0.50)                 # sam tekst na bialym, bez kart
    assert "PLYWAJACA_TRESC" not in kody(oko.ocen(bez.zapisz(tmp_path, "b.png")))
    bez_tytulu = Slajd(tytul=False)
    bez_tytulu.karta(0.07, 0.36, 0.93, 0.64, 0.5)
    w = oko.ocen(bez_tytulu.zapisz(tmp_path, "c.png"))
    assert "PLYWAJACA_TRESC" not in kody(w) and w["miary"]["pas_gora"] is None


def test_plywajaca_tresc_nie_dla_zielonego_slajdu_i_poprawnego(tmp_path):
    z = Slajd(tlo=ZIEL, tytul=False, logo=False, numer=False)
    z.karta(0.07, 0.36, 0.93, 0.64, 0.5, kolor=KREM)
    assert oko.ocen(z.zapisz(tmp_path, "a.png"))["usterki"] == []
    assert "PLYWAJACA_TRESC" not in kody(oko.ocen(trzy_karty(Slajd()).zapisz(tmp_path, "b.png")))


# --- odpornosc, katalog, opis ---------------------------------------------------------------------------------------
def test_brak_pliku_i_smieci_to_wynik_pusty(tmp_path):
    assert oko.ocen(str(tmp_path / "nie_ma.png")) == {"miary": {}, "usterki": []}
    bad = tmp_path / "s01.png"
    bad.write_bytes(b"to nie jest obraz")
    assert oko.ocen(str(bad)) == {"miary": {}, "usterki": []}
    zero = tmp_path / "s02.png"
    zero.write_bytes(b"")
    assert oko.ocen(str(zero)) == {"miary": {}, "usterki": []}
    ucieta = trzy_karty(Slajd()).zapisz(tmp_path, "s03.png")
    dane = open(ucieta, "rb").read()
    (tmp_path / "s04.png").write_bytes(dane[: len(dane) // 2])  # urwany PNG
    assert oko.ocen(str(tmp_path / "s04.png")) == {"miary": {}, "usterki": []}
    assert oko.ocen(None) == {"miary": {}, "usterki": []}


def test_maly_obraz_nie_wywala(tmp_path):
    p = zapisz(Image.new("RGB", (10, 10), BIEL), tmp_path)
    assert oko.ocen(p) == {"miary": {}, "usterki": []}


def test_cala_biala_plansza(tmp_path):
    w = oko.ocen(zapisz(Image.new("RGB", (W, H), BIEL), tmp_path))
    assert [u["kod"] for u in w["usterki"]] == []
    assert w["miary"]["dol_pusty"] == 1.0


def test_png_z_alfa_i_paleta(tmp_path):
    base = trzy_karty(Slajd()).im
    p1 = zapisz(base.convert("RGBA"), tmp_path, "s01.png")
    p2 = zapisz(base.convert("P"), tmp_path, "s02.png")
    assert oko.ocen(p1)["usterki"] == []
    assert isinstance(oko.ocen(p2), dict)


def test_ocen_katalog_i_spec(tmp_path):
    trzy_karty(Slajd(), y1=0.45).zapisz(tmp_path, "s01.png")
    trzy_karty(Slajd()).zapisz(tmp_path, "s02.png")
    (tmp_path / "inny.png").write_bytes(b"x")
    (tmp_path / "s03.png").write_bytes(b"zepsuty")
    wyn = oko.ocen_katalog(str(tmp_path))
    assert sorted(wyn) == [1, 2, 3]
    assert "PUSTY_DOL" in kody(wyn[1]) and wyn[2]["usterki"] == [] and wyn[3]["miary"] == {}
    spec = {"slides": [{"type": "section"}, {"type": "uklad", "rows": []}]}
    assert "PUSTY_DOL" not in kody(oko.ocen_katalog(str(tmp_path), spec)[1])
    assert "PUSTY_DOL" not in kody(oko.ocen_katalog(str(tmp_path), spec["slides"])[1])
    import json
    sp = tmp_path / "spec.json"
    sp.write_text(json.dumps(spec), encoding="utf-8")
    assert "PUSTY_DOL" not in kody(oko.ocen_katalog(str(tmp_path), str(sp))[1])
    assert oko.ocen_katalog(str(tmp_path / "brak")) == {}
    assert "PUSTY_DOL" in kody(oko.ocen_katalog(str(tmp_path), str(tmp_path / "nie_ma.json"))[1])


def test_opis_i_kody():
    u = {"kod": "PUSTY_DOL", "opis": "34% wysokości slajdu pod treścią jest puste", "waga": 2}
    assert oko.opis(12, u) == "Slajd 12: 34% wysokości slajdu pod treścią jest puste"
    assert set(oko.KODY) == {"PUSTY_DOL", "KARTA_PUSTA", "KARTY_NIEROWNE", "PRZY_KRAWEDZI", "GESTO", "MALO_TRESCI",
                             "PLYWAJACA_TRESC"}


def test_usterki_maja_kod_opis_i_wage_1_do_3(tmp_path):
    s = Slajd()
    s.karta(0.07, 0.30, 0.985, 0.50, None)
    for u in oko.ocen(s.zapisz(tmp_path))["usterki"]:
        assert u["kod"] in oko.KODY and isinstance(u["opis"], str) and u["opis"] and u["waga"] in (1, 2, 3)


def test_szybkosc_60_slajdow(tmp_path):
    p = trzy_karty(Slajd()).zapisz(tmp_path, "s01.png")
    for i in range(2, 61):
        Image.open(p).save(str(tmp_path / ("s%02d.png" % i)))
    t = time.perf_counter()
    wyn = oko.ocen_katalog(str(tmp_path))
    dt = time.perf_counter() - t
    assert len(wyn) == 60
    assert dt < 4.0, dt
