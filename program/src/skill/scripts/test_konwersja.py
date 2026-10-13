# -*- coding: utf-8 -*-
"""Testy konwersji 1:1 (pptx_convert): pojemniki z szablonu dobierane do ksztaltu tresci (08.10.2026).

    python -m pytest test_konwersja.py -q

Czesc 1 - jednostkowe, na sztucznych wierszach (bez plikow). Czesc 2 - integracyjne na prawdziwych prezentacjach
(pomijane, gdy pliku nie ma na tym komputerze). Zadne z nich nie uruchamia PowerPointa ani modeli AI.
"""
import collections
import os
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_dk  # noqa: E402
import pptx_convert as pc  # noqa: E402

PREZ = r"D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE"
PLIKI = {
    "co_dalej": os.path.join(PREZ, "06.10.2026 - strategia", "DK_co_dalej_update.pptx"),
    "datesy": os.path.join(PREZ, "DATESY", "DOBRA KALORIA - DATESY.pptx"),
    "kulki": os.path.join(PREZ, "24.09.2026 - KULKI z kreatyną", "DK_KULKI z kreatyną.pptx"),
    "onlien": os.path.join(PREZ, "onlien.pptx"),
}
# Znane usterki wiernosci PRZED zmiana (07.10): konwersja nie moze ich pomnozyc
USTERKI_PRZED = {"co_dalej": 0, "datesy": 0, "kulki": 1, "onlien": 152}


# --- 1. jednostkowe ---------------------------------------------------------------------------------------------
def _w(*lines):
    return [{"t": t, "pt": 36, "li": False, "pusty": False} for t in lines]


def test_zdanie_progi_slow():
    n12 = " ".join(["slowo"] * 12)
    n13 = " ".join(["slowo"] * 13)
    assert not pc._zdanie_grupa(_w(n12))
    assert pc._zdanie_grupa(_w(n13))
    assert not pc._zdanie_grupa(_w(" ".join(["slowo"] * 7) + "."))
    assert pc._zdanie_grupa(_w(" ".join(["slowo"] * 8) + "."))
    assert not pc._zdanie_grupa(_w(" ".join(["slowo"] * 8) + "?"))  # pytanie bywa haslem


def _row(k, t, pole, pt=36.0, duze=True, **kw):
    r = {"k": k, "t": t, "_pole": pole, "_pt": pt, "_duze": duze}
    r.update(kw)
    return r


def test_dobra_zla_wiadomosc_dwie_karty():
    out = pc._pojemniki([
        _row("h", "Dobra wiadomość – rynek zdrowych przekąsek rośnie", 1, _fl="iiiiiii"),
        _row("lead", "Zła wiadomość – rośniemy wolniej\nniż sam rynek", 1, _fl="aaaaa----"[:8]),
    ])
    assert len(out) == 1 and out[0]["k"] == "cols" and out[0]["kont"] and len(out[0]["items"]) == 2
    h = [it["blocks"][0] for it in out[0]["items"]]
    assert [b["k"] for b in h] == ["h", "h"]
    assert h[0]["t"] == "Dobra wiadomość –" and h[1]["t"] == "Zła wiadomość –"  # myślnik z oryginału zostaje (09.10)


def test_cytat_i_karta_hasla():
    out = pc._pojemniki([
        _row("lead", "Brands grow through constant exposure\nto new buyers (Byron Sharp, Ehrenberg-Bass).", 1,
             _fl="--aa-aa--------"[:11]),
        _row("lead", "Produkt: jasno zdefiniowany", 2, pt=36),
        _row("lead", "Potrzeba, grupa docelowa, okazja", 2, pt=47),
        _row("lead", "= Rozwiązanie produktowe", 3, pt=36),
    ])
    assert [r["k"] for r in out] == ["quote", "cols"]
    assert out[0]["author"] == "(Byron Sharp, Ehrenberg-Bass)." and out[0]["t"].endswith("new buyers")  # nawiasy i kropka zostają
    assert len(out[1]["items"]) == 1 and len(out[1]["items"][0]["blocks"]) == 3  # R6 odrzucone (pt 47/36, '=')


def test_trzy_fakty_i_wniosek_goly():
    pole_a, pole_b = 1, 2
    out = pc._pojemniki([
        _row("p", " ".join(["fakt"] * 18) + ".", pole_a, pt=32), _row("p", " ".join(["dane"] * 9) + ".", pole_a, pt=32),
        _row("p", " ".join(["liczba"] * 9) + ".", pole_a, pt=32),
        _row("lead", "Ważna kwestia – to nie jest jednolity segment", pole_b, pt=30),
    ])
    assert [r["k"] for r in out] == ["cols", "lead"]
    assert len(out[0]["items"]) == 3 and out[1]["t"].startswith("Ważna")


def test_etykieta_ct_ta_zostaje_goly_h():
    out = pc._pojemniki([_row("lead", "CT: młodzi z segmentu 20-35 lat\nTA: mężczyźni 35-55 lat", 1)])
    assert out[0]["k"] == "h" and out[0]["align"] == "l" and not out[0].get("kont")


def test_wstep_przed_kafelkami_i_akapit_w_karcie():
    out = pc._pojemniki([
        _row("h", "Kierunek zmian:", 1),
        {"k": "chips", "items": ["A", "B", "C"], "per_row": 3},
        _row("p", " ".join(["slowo"] * 25) + ".", 2, pt=18, duze=False),
    ])
    assert [r["k"] for r in out] == ["h", "chips", "cols"]
    assert out[2]["items"][0]["blocks"][0]["k"] == "p"


def test_lista_pozycji_laczy_oraz_i_nie_skleja_sierot():
    assert pc._pozycje_listy(["Ewaluacja portfolio", "Kierunki", "Kreacja nowych segmentów", "oraz kategorii"], 6) == \
        ["Ewaluacja portfolio", "Kierunki", "Kreacja nowych segmentów oraz kategorii"]
    assert pc._pozycje_listy(["Polifenole i flawonoidy", "Beta-karoten", "Cynk", "Magnez"], 4) is not None
    assert pc._pozycje_listy(["Jedno zdanie.", "Drugie zdanie.", "Trzecie zdanie."], 6) is None


# --- 1b. klocki `uklad` z szablonu marki (13.10.2026): hero, icon, kv, bars, li, band, karta zielona, tytul 3-liniowy ----
def _uk(rows, **kw):
    return dict(type="uklad", kicker="Test", rows=rows, **kw)


def _zbuduj_spec(sl, tmp_path):
    """Buduje jeden slajd `uklad` (motyw shop) do pliku i zwraca (Presentation, miary ukladu)."""
    from pptx import Presentation
    os.environ.setdefault("DK_CACHE_DIR", str(tmp_path / "cache"))
    out = str(tmp_path / "t.pptx")
    build_dk.build({"theme": "shop", "slides": [sl]}, out)
    return Presentation(build_dk.build.last_out), build_dk.uklad_layout(sl)[0]


def _karta(*blocks, **kw):
    return dict(blocks=list(blocks), **kw)


KLOCKI = [
    {"k": "hero", "t": "7,8%"},
    {"k": "icon", "name": "leaf", "d": 1.8},
    {"k": "kv", "label": "CT", "t": "kobiety z segmentu 20-35 lat"},
    {"k": "bars", "items": [{"label": "owoce", "value": 49, "t": "49%"}, {"label": "slodkosci", "value": 4, "t": "4%"}]},
    {"k": "li", "t": "Mala porcja i otwieranie bez wysilku.", "icon": "check"},
]


def test_klocki_layout_liczy_wysokosci_kazdego_bloku():
    sl = _uk([{"k": "cols", "items": [_karta(*KLOCKI)]}])
    ms, f = build_dk.uklad_layout(sl)
    assert ms is not None and f
    parts = ms[0]["cols"][0][0]
    assert [p[0] for p in parts] == ["hero", "icon", "kv", "bars", "li"]  # jeden element miary na blok, w kolejnosci
    assert all(h > 0 for (_k, _y, h, _d) in parts)
    ys = [p[1] for p in parts]
    assert ys == sorted(ys) and len(set(ys)) == 5  # kolejne bloki leza jeden pod drugim
    assert ms[0]["h"] >= parts[-1][1] + parts[-1][2]  # karta obejmuje cala tresc


def test_hero_granice_pisma_i_dopasowanie_do_karty():
    from pptx.util import Pt  # noqa: F401
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "items": [_karta({"k": "hero", "t": "7,8%"})]}]))
    assert 30 <= ms[0]["cols"][0][0][0][3]["pt"] <= 60
    wiele = [_karta({"k": "hero", "t": "ogromna liczba bohater"}) for _ in range(3)]
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "items": wiele}]))
    d = ms[0]["cols"][0][0][0][3]
    iw = ms[0]["cols"][0][1]
    assert d["pt"] < 30 and build_dk.bd.text_w_emu(d["text"], d["pt"], "Mindset") <= iw  # zmniejszony do szerokosci karty


def test_karta_zielona_biale_teksty_i_zolty_zamiast_czerwieni(tmp_path):
    from pptx.enum.dml import MSO_THEME_COLOR
    bl = [{"k": "h", "t": "Zla wiadomosc", "color": "brand"}, {"k": "p", "t": "Rosniemy wolniej niz sam rynek.", "wyr": "-a---"},
          {"k": "hero", "t": "7,8%", "color": "accent"}, {"k": "li", "t": "Punkt listy", "wyr": "a-"},
          {"k": "kv", "label": "CT", "t": "wartosc"}]
    sl = _uk([{"k": "cols", "items": [_karta(*bl, fill="brand")]}])
    prs, ms = _zbuduj_spec(sl, tmp_path)
    for kind, _y, _h, d in ms[0]["cols"][0][0]:
        if kind in ("txt", "li", "hero"):
            assert d["color"] in ("white", "sun"), (kind, d["color"])  # zadnej zieleni na zieleni ani czerwieni
    kolory = set()
    for sh in prs.slides[0].shapes:
        if sh.has_text_frame and not sh.name.startswith("!!"):
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.text.strip():
                        kolory.add(r.font.color.theme_color if r.font.color.type is not None else None)
    kolory.discard(MSO_THEME_COLOR.ACCENT_5)  # kicker (tan) i stopka - poza karta
    assert MSO_THEME_COLOR.ACCENT_2 not in kolory  # czerwien (akcent) nie wystepuje na zielonej karcie
    assert MSO_THEME_COLOR.BACKGROUND_1 in kolory  # bialy tekst jest


def test_brak_pliku_ikony_to_lisc_i_ostrzezenie_nie_wyjatek(tmp_path, capsys):
    sl = _uk([{"k": "cols", "items": [_karta({"k": "icon", "name": "nie-ma-takiej-ikony", "d": 1.8},
                                             {"k": "li", "t": "tez bez pliku", "icon": "tez-nie-ma"})]}])
    prs, _ms = _zbuduj_spec(sl, tmp_path)
    err = capsys.readouterr().err
    assert "nie-ma-takiej-ikony" in err and "tez-nie-ma" in err
    assert sum(1 for sh in prs.slides[0].shapes if sh.name.startswith("Ikona - ")) == 2  # obie ikony narysowane (jako liść)


def test_tytul_trzyliniowy_przesuwa_tresc():
    wiersz = [{"k": "cols", "items": [_karta({"k": "p", "t": "Tresc."})]}]
    krotki = _uk(wiersz, title="Wielkosc segmentow")
    dlugi = _uk(wiersz, title="Kierunek, w ktorym zmierzamy (globalnie i rynkowo): tworzy hiper-czlowieka - dlugowiecznego, sprawnego i atrakcyjnego", title_size=40)
    assert build_dk.uklad_top(krotki) == build_dk.CT  # 1 linia: bez zmian (5,3 cm)
    sz, ls = build_dk.title_geom(dlugi, 3)
    assert len(ls) == 3
    assert build_dk.uklad_top(dlugi) == pytest.approx(build_dk.TITLE_Y + 3 * sz * 12700 + build_dk.cm(0.6), abs=2)
    assert build_dk.uklad_top(dlugi) > build_dk.CT + build_dk.cm(1)
    # dluzszy tytul: dostepna wysokosc maleje - pismo kart nie moze byc wieksze niz pod krotkim tytulem
    karta = [{"k": "cols", "items": [_karta({"k": "p", "t": "Zdanie. " * 60})]}]
    _m1, f1 = build_dk.uklad_layout(_uk(karta, title="Krotki"))
    _m2, f2 = build_dk.uklad_layout(_uk(karta, title=dlugi["title"], title_size=40))
    assert f2 <= f1
    # tytul > 3 linie: zmniejszany do 3 (nie wjedzie w karty)
    olbrzym = _uk(wiersz, title="Slowo " * 30)
    _sz, ls = build_dk.title_geom(olbrzym, 3)
    assert len(ls) <= 3 or _sz == 26


def test_pas_wysokosc_tekst_plus_marginesy_do_trzech_linii():
    ms, _f = build_dk.uklad_layout(_uk([{"k": "band", "t": "Wazna kwestia", "fill": "brand"}]))
    m = ms[0]
    assert m["kind"] == "band" and 18 <= m["pt"] <= 30 and len(m["lines"]) == 1
    assert m["h"] == pytest.approx(m["pt"] * m["lh"] * 12700 + 2 * build_dk.cm(0.55), abs=2)  # tekst + 2 x 0,55 cm
    dlugi = "Bardzo dlugi wniosek ktory musi sie zlamac w kilku liniach bo inaczej nie zmiesci sie w pasie " * 3
    ms, _f = build_dk.uklad_layout(_uk([{"k": "band", "t": dlugi, "fill": "card"}]))
    assert len(ms[0]["lines"]) <= 3 and ms[0]["pt"] >= 18
    assert ms[0]["color"] == "ink"  # na kremie ciemny tekst
    ms, _f = build_dk.uklad_layout(_uk([{"k": "band", "t": "Wniosek", "fill": "accent", "icon": "megaphone"}]))
    assert ms[0]["color"] == "white" and ms[0]["ico"] == "megaphone" and ms[0]["align"] == "l"


def test_karta_align_c_i_valign_na_karte():
    sl = _uk([{"k": "cols", "valign": "t", "items": [_karta({"k": "h", "t": "Naglowek"}, {"k": "p", "t": "Opis."}, align="c"),
                                                      _karta({"k": "p", "t": "Zwykla.", "align": "l"}, valign="m")]}])
    ms, _f = build_dk.uklad_layout(sl)
    c = ms[0]["cols"]
    assert all(d["align"] == "c" for (k, _y, _h, d) in c[0][0] if k == "txt")  # cala tresc karty na srodku
    assert c[1][0][0][3]["align"] == "l"  # wlasny align bloku wygrywa
    assert ms[0]["items"][1]["valign"] == "m" and ms[0]["valign"] == "t"  # valign per karta, domyslnie z wiersza


def test_karty_biala_z_linia_i_rowna_wysokosc(tmp_path):
    sl = _uk([{"k": "cols", "items": [_karta({"k": "p", "t": "Biala karta."}, fill="white"),
                                      _karta({"k": "p", "t": "Druga, dluzsza karta z wiekszym tekstem w srodku."})]}])
    prs, ms = _zbuduj_spec(sl, tmp_path)
    assert len({round(h) for h in ms[0]["hs"]}) == 1  # karty jednego wiersza zawsze rowne
    karty = [sh for sh in prs.slides[0].shapes if sh.shape_type == 1 and sh.height > build_dk.cm(2)]
    from pptx.enum.dml import MSO_FILL
    z_linia = [sh for sh in karty if sh.line.fill.type == MSO_FILL.SOLID]
    assert len(z_linia) == 1 and z_linia[0].line.width == build_dk.Pt(0.75)  # tylko biala karta ma linie 0,75 pt


def test_dlugie_slowo_zmniejsza_tylko_swoj_blok_nie_slajd():
    # waska zielona karta z dlugim slowem obok szerokiej: f slajdu i naglowek szerokiej karty zostaja, kurczy sie tylko ten blok
    sl = _uk([{"k": "cols", "items": [
        _karta({"k": "h", "t": "Smak i mikroskładniki.", "color": "white"}, fill="brand", w=0.62),
        _karta({"k": "h", "t": "Krótki nagłówek"}, {"k": "p", "t": "Tekst akapitu w szerokiej karcie."}, w=1.5)]}])
    ms, f = build_dk.uklad_layout(sl)
    assert f == 1.0
    (pa, iwa), (pb, iwb) = ms[0]["cols"]
    ha, hb = pa[0][3], pb[0][3]
    assert ha["pt"] == hb["pt"]  # jeden rozmiar w wierszu kafli = najmniejszy z dopasowanych (jak siatka ikon)
    assert 16.5 <= ha["pt"] <= 30  # nie mniej niz 55% bazowego
    assert build_dk.bd.text_w_emu("mikroskładniki.", ha["pt"], "Mindset") <= iwa * 0.96  # slowo sie miesci
    # lead w pieciu waskich kaflach: ten sam wzorzec, f nie spada
    lead = [_karta({"k": "lead", "t": "Starzejące się społeczeństwo", "pt": 18, "align": "c"}, align="c") for _ in range(5)]
    ms, f = build_dk.uklad_layout(_uk([{"k": "cols", "items": lead, "kont": True}]))
    assert f == 1.0
    for parts, iw in ms[0]["cols"]:
        d = parts[0][3]
        assert 13 <= d["pt"] <= 18 * 1.6
        assert build_dk.bd.text_w_emu("społeczeństwo", d["pt"], "Mindset") <= iw * 0.96
    # kv: wartosc z dlugim slowem tez dopasowuje sie sama
    ms, f = build_dk.uklad_layout(_uk([{"k": "cols", "items": [_karta({"k": "kv", "label": "X", "t": "mikroskładniki odżywcze"})
                                                                   for _ in range(4)]}]))
    assert f == 1.0


def test_pas_staly_odstep_0_5_cm_i_start_od_gory(tmp_path):
    wiersze = [{"k": "cols", "items": [_karta({"k": "p", "t": "Karta."})]}, {"k": "band", "t": "Wniosek", "fill": "brand"}]
    for mf in (1.0, 0.6):  # odstep nie zalezy od f slajdu
        ms, _f = build_dk.uklad_layout(_uk(wiersze, max_f=mf))
        assert ms[1]["gap"] == build_dk.cm(0.5)
    sl = _uk(wiersze, title="Tytul", valign="t")
    prs, ms = _zbuduj_spec(sl, tmp_path)
    karty = sorted((sh for sh in prs.slides[0].shapes if sh.shape_type == 1 and sh.height > build_dk.cm(1)),
                   key=lambda sh: sh.top)
    assert karty[0].top == pytest.approx(build_dk.uklad_top(sl), abs=2)  # valign t: wiersze od gory pola tresci
    assert karty[1].top - (karty[0].top + karty[0].height) == pytest.approx(build_dk.cm(0.5), abs=2)  # karta -> pas 0,5 cm


def test_wiersz_kafli_jeden_rozmiar_lead_hero_kv():
    # s09: cztery kafle ikona + lead - "Dlugowiecznosc" wymusza mniejsze pismo, reszta ma ten sam rozmiar (najmniejszy)
    teksty = ["Długowieczność", "Wysoka sprawność fizyczna", "Atrakcyjność", "Większe funkcje poznawcze"]
    kafle = [_karta({"k": "icon", "name": "leaf"}, {"k": "lead", "t": t, "align": "c"}, align="c") for t in teksty]
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "items": kafle, "kont": True}]))
    pts = [parts[1][3]["pt"] for parts, _iw in ms[0]["cols"]]
    assert len(set(pts)) == 1, pts
    # hero i kv w rzedzie: tez jeden rozmiar
    hero = [_karta({"k": "hero", "t": t}) for t in ("7,7 mln", "ok. 30%", "11,6%")]
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "items": hero}]))
    assert len({parts[0][3]["pt"] for parts, _iw in ms[0]["cols"]}) == 1
    kv = [_karta({"k": "kv", "label": "CT", "t": t}) for t in ("kobiety z segmentu 20-35 lat", "mikroskładniki")]
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "items": kv}]))
    assert len({parts[0][3]["vpt"] for parts, _iw in ms[0]["cols"]}) == 1
    # bloki o ROZNYCH zadanych rozmiarach (hierarchia autora) nie sa wyrownywane
    roz = [_karta({"k": "lead", "t": "Duże", "pt": 30}), _karta({"k": "lead", "t": "Małe", "pt": 20})]
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "items": roz}]))
    assert [parts[0][3]["pt"] for parts, _iw in ms[0]["cols"]] == [30, 20]


def test_akapity_kart_nie_ponizej_15_pt_gdy_sie_mieszcza():
    # trzy wiersze kart: przy f < 0.88 akapit (17 pt x f) spadlby ponizej 15 pt, a przy 15 pt slajd sie jeszcze miesci
    karta = lambda: _karta({"k": "p", "t": "Krótki akapit w karcie."})
    sl = _uk([{"k": "cols", "items": [karta(), karta()], "kont": True} for _ in range(4)], title="Tytuł")
    ms, f = build_dk.uklad_layout(sl)
    assert ms is not None
    ps = [d["pt"] for m in ms for parts, _iw in m["cols"] for (k, _y, _h, d) in parts if k == "txt"]
    assert min(ps) >= 15, (f, ps)


def test_naglowek_karty_z_akapitem_najwyzej_1_6_razy_p():
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "kont": True, "items": [
        _karta({"k": "h", "t": "Matcha to nie tylko smak"}, {"k": "p", "t": "Młodzi nie chcą przepłacać."})]}], max_f=1.6))
    h, p = [d for (_k, _y, _h, d) in ms[0]["cols"][0][0]]
    assert h["pt"] <= 1.6 * p["pt"] + 0.01
    # poza kartami-pojemnikami (stare slajdy): bez ograniczenia 1,6 x
    ms, _f = build_dk.uklad_layout(_uk([{"k": "cols", "items": [
        _karta({"k": "h", "t": "Nagłówek"}, {"k": "p", "t": "Akapit."})]}]))
    h, p = [d for (_k, _y, _h, d) in ms[0]["cols"][0][0]]
    assert h["pt"] > 1.6 * p["pt"]


def test_kv_etykieta_min_12_pt_i_pad_pionowy_min_0_55_cm():
    sl = _uk([{"k": "cols", "kont": True, "pad": 0.3, "items": [_karta({"k": "kv", "label": "CT:", "t": "kobiety"})]}], max_f=0.6)
    ms, _f = build_dk.uklad_layout(sl)
    d = ms[0]["cols"][0][0][0][3]
    assert d["lpt"] >= 12 and ms[0]["pad"] >= build_dk.cm(0.55)
    assert ms[0]["h"] == pytest.approx(d["h"] + 2 * ms[0]["pad"], abs=2)  # za ostatnim klockiem nie ma dodatkowego odstepu


def test_twarda_spacja_nie_jest_punktem_lamania(tmp_path):
    nb = " "
    tekst = "Najszybciej rośnie grupa wśród Gen%sZ i millenialsów, a liderem sprzedaży są napoje." % nb
    wd = lambda t: build_dk.bd.text_w_emu(t, 20, "Lato")
    # szerokość: „… wśród Gen” się mieści, „… wśród Gen Z” już nie - zwykła spacja łamałaby między Gen i Z
    w = (wd("Najszybciej rośnie grupa wśród Gen") + wd("Najszybciej rośnie grupa wśród Gen Z")) / 2 / 0.96
    ls = build_dk.lines_for(tekst, 20, w)
    assert not any(l.endswith("Gen") for l in ls), ls
    assert any("Gen" + nb + "Z" in l for l in ls), ls  # twarda spacja zostaje w tekście
    assert any(l.endswith("Gen") for l in build_dk.lines_for(tekst.replace(nb, " "), 20, w))  # kontrola: zwykła spacja łamie
    assert build_dk._uk_wrap("body", tekst, 20, w) == ls  # ten sam wynik w łamaniu wierszy układu
    assert build_dk.lines_for(tekst, 20, 40 * build_dk.cm(1)) == [tekst]  # mierzona jak spacja: mieści się w jednej linii
    # tekst na slajdzie: U+00A0 przeżywa (txt nie zamienia jej na zwykłą spację)
    sl = _uk([{"k": "cols", "items": [_karta({"k": "p", "t": tekst})]}])
    prs, _ms = _zbuduj_spec(sl, tmp_path)
    teksty = " ".join(sh.text_frame.text for sh in prs.slides[0].shapes if sh.has_text_frame)
    assert "Gen" + nb + "Z" in teksty


def test_min_h_nie_rosnie_z_f_a_rwane_ok_pozwala_na_wieksze_pismo():
    # min_h = minimum w cm przy f = 1: przy f > 1 karta nie jest wyższa niż min_h (tylko tyle, ile wymaga treść)
    ms, f = build_dk.uklad_layout(_uk([{"k": "cols", "kont": True, "min_h": 7, "items": [_karta({"k": "p", "t": "Krótko."})]}],
                                      max_f=1.6))
    assert f > 1.0 and ms[0]["h"] == pytest.approx(build_dk.cm(7), abs=2)
    # slajd 19 z dopracowanej prezentacji: pas nad dwiema kartami (hero + p); domyślnie szukamy układu bez „rwanych” linii
    # (mniejsze pismo), rwane_ok: true - większe pismo bez tego szukania
    wiersze = lambda ok: [{"k": "band", "t": "Białko –", "fill": "brand", "icon": "biceps-flexed", "align": "l"},
                          dict({"k": "cols", "kont": True, "pad": 1.2, "min_h": 7.0, "valign": "t", "items": [
                              _karta({"k": "hero", "t": "1,2 g/kg"},
                                     {"k": "p", "t": "NCEŻ zaleca seniorom 1,2 g/kg dziennie, więc więcej niż ogólna norma 0,9."}),
                              _karta({"k": "hero", "t": "50%"},
                                     {"k": "p", "t": "Sarkopenia dotyczy ok. 10% osób w wieku 60–70 lat i ponad 50% po 80., "
                                                      "a w badaniu IŻŻ ponad połowa 70-letnich kobiet jadła za mało białka"})]},
                               **({"rwane_ok": True} if ok else {}))]
    _m0, f0 = build_dk.uklad_layout(_uk(wiersze(False), title="Potrzeby na przekąskę:", max_f=1.6))
    _m1, f1 = build_dk.uklad_layout(_uk(wiersze(True), title="Potrzeby na przekąskę:", max_f=1.6))
    assert f1 >= f0


def test_stary_wiersz_cols_bez_zmian_wygladu():
    # karta bez fill / align / valign: teksty jak dawniej (lewo, kolory z rodzaju bloku, bez znacznika dark)
    sl = _uk([{"k": "cols", "items": [_karta({"k": "h", "t": "Naglowek"}, {"k": "p", "t": "Opis."})]}], title="Tytul")
    ms, _f = build_dk.uklad_layout(sl)
    h, p = [d for (_k, _y, _h, d) in ms[0]["cols"][0][0]]
    assert (h["color"], h["align"], h["dark"]) == ("brand", "l", False)
    assert (p["color"], p["align"], p["dark"]) == ("ink", "l", False)
    assert build_dk.uklad_top(sl) == build_dk.CT


# --- 2. integracyjne --------------------------------------------------------------------------------------------
_CACHE = {}


def _zbuduj(nazwa, tmp_path_factory):
    if nazwa in _CACHE:
        return _CACHE[nazwa]
    plik = PLIKI[nazwa]
    if not os.path.isfile(plik):
        pytest.skip("brak pliku %s" % plik)
    rob = str(tmp_path_factory.mktemp("rob_" + nazwa))
    model = pc.extract(plik, rob)
    spec = pc.compose(model, {"wizualizacje": False, "wyjscie": rob, "szablonuj": False})  # testy rund 1-4: sam układ
    out = os.path.join(rob, "wynik.pptx")
    build_dk.build(spec, out)
    pptx = build_dk.build.last_out
    cov = pc.coverage(plik, pptx, spec["mapa"], rob=rob)
    wier = pc.wiernosc(model, pptx, spec["mapa"])
    _CACHE[nazwa] = (model, spec, cov, wier)
    return _CACHE[nazwa]


def _zbuduj_szablon(nazwa, tmp_path_factory):
    """Jak _zbuduj, ale z krokiem szablonowania (domyślnym w programie)."""
    klucz = nazwa + "+szablon"
    if klucz in _CACHE:
        return _CACHE[klucz]
    plik = PLIKI[nazwa]
    if not os.path.isfile(plik):
        pytest.skip("brak pliku %s" % plik)
    rob = str(tmp_path_factory.mktemp("rob_sz_" + nazwa))
    model = pc.extract(plik, rob)
    spec = pc.compose(model, {"wizualizacje": False, "wyjscie": rob})
    build_dk.build(spec, os.path.join(rob, "wynik.pptx"))
    pptx = build_dk.build.last_out
    cov = pc.coverage(plik, pptx, spec["mapa"], rob=rob)
    wier = pc.wiernosc(model, pptx, spec["mapa"])
    _CACHE[klucz] = (model, spec, cov, wier)
    return _CACHE[klucz]


@pytest.mark.parametrize("nazwa", sorted(PLIKI))
def test_tresc_i_wiernosc(nazwa, tmp_path_factory):
    model, spec, cov, wier = _zbuduj(nazwa, tmp_path_factory)
    assert cov["brakuje"] == []
    assert len(wier["usterki"]) <= USTERKI_PRZED[nazwa]
    if nazwa != "onlien":  # onlien (instrukcja szablonu) dzieli dlugie slajdy juz od 06.10
        assert len(spec["slides"]) == len(model["slajdy"])


@pytest.mark.parametrize("nazwa", sorted(PLIKI))
def test_tlo_papierowe_i_pismo_miesci_sie(nazwa, tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj(nazwa, tmp_path_factory)
    for sp in spec["slides"]:
        assert sp.get("bg") != "card"  # krem tylko jako karta, nigdy tlo calego slajdu
        if sp["type"] == "uklad" and sp.get("rows"):
            assert pc._miesci(sp)


def test_co_dalej_haslo_to_nie_zdanie_i_kazdy_slajd_ma_pojemnik(tmp_path_factory):
    model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    for i, sp in enumerate(spec["slides"], 1):
        if sp["type"] != "uklad":
            continue
        for r in sp["rows"]:
            blocks = [b for it in r.get("items", []) for b in it.get("blocks", [])] if r["k"] == "cols" else [r]
            for b in blocks:
                if b["k"] in ("lead", "h", "sub", "big") and b.get("t"):
                    assert len(b["t"].split()) < 13, "slajd %d: Mindset z %d slowami" % (i, len(b["t"].split()))
    for src in range(6, 43):
        idx = spec["mapa"][str(src)]
        sps = [spec["slides"][k] for k in idx]
        if all(sp["type"] != "uklad" for sp in sps):
            continue  # przerywnik
        assert any(r["k"] in ("cols", "quote", "chips", "pics") or r.get("li") for sp in sps for r in sp["rows"]), \
            "slajd %d bez pojemnika" % src


# --- 3. runda 2 (08.10): hiperlacza zamiast 'Link:', wielkosc liter, zdanie z kropka to nie haslo -------------------
def test_zdaniowo_mala_litera_w_srodku_zdania():
    t = "Matcha to nie tylko smak ale pewien Manifest – młodzi, nie chcą przepłacać Za dobra luksusowe ale Chcą się"
    out = pc._zdaniowo([t], set(), {"za", "chcą", "smak"})[0]
    assert " za dobra " in out and " chcą się" in out and "Manifest" in out  # 'Manifest' nie ma malej wersji w pliku
    assert pc._zdaniowo(["To jest. Za chwile"], set(), {"za"})[0].startswith("To jest. Za")  # po kropce zostaje


def test_hiperlacza_bez_napisu_link(tmp_path_factory):
    model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    assert "Link:" not in str(spec["slides"])
    lk = {sp["zrodlo"]: sp["links"] for sp in spec["slides"] if sp.get("links")}
    assert lk[7][0]["t"] == "Byron Sharp" and lk[41][0]["t"].startswith("Bezkaloryczny")


def test_hiperlacze_w_pliku_na_tych_samych_slowach(tmp_path_factory):
    from pptx import Presentation
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    rob = str(tmp_path_factory.mktemp("lk"))
    build_dk.build(spec, os.path.join(rob, "w.pptx"))
    prs = Presentation(build_dk.build.last_out)
    idx = spec["mapa"]["7"][0]
    runs = [r for sh in prs.slides[idx].shapes if sh.has_text_frame for p in sh.text_frame.paragraphs for r in p.runs
            if r.hyperlink and r.hyperlink.address]
    assert [r.text for r in runs] == ["Byron Sharp"]


def test_zdanie_z_kropka_nie_jest_mindsetem(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    for sp in spec["slides"]:
        for r in sp.get("rows", []):
            blocks = [b for it in r.get("items", []) for b in it.get("blocks", [])] if r["k"] == "cols" else [r]
            for b in blocks:
                if b.get("k") in ("lead", "h", "big") and b.get("t"):  # 'sub' = wniosek pod obrazami (R10a, K10)
                    assert not (len(b["t"].split()) >= 8 and b["t"].rstrip().endswith((".", "!"))), b["t"]


def test_komentarz_po_kartach_nie_wiekszy_niz_karty(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    sp = next(s for s in spec["slides"] if s["zrodlo"] == 37)
    ms, _f = build_dk.uklad_layout(sp)
    karta = max(d["pt"] for parts, _w in ms[0]["cols"] for (kind, _y, _h, d) in parts if kind == "txt")
    kom = [m["pt"] for m, r in zip(ms, sp["rows"]) if r["k"] == "p"]
    assert kom and max(kom) <= karta


# --- 4. runda 3 (09.10): znak w znak, karty wg tresci, obrazy do brzegow, zakonczenie na srodku -----------------------
def test_interpunkcja_bez_roznic_co_dalej(tmp_path_factory):
    _model, _spec, _cov, wier = _zbuduj("co_dalej", tmp_path_factory)
    assert wier["znaki"] == [], wier["znaki"]  # zadnego zdjetego nawiasu, myslnika ani kropki (s06, s07, s09)


def test_s09_kafle_zielone_bez_wiodacego_myslnika(tmp_path_factory):
    _model, spec, _cov, wier = _zbuduj("co_dalej", tmp_path_factory)
    ch = [r for k in spec["mapa"]["9"] for r in spec["slides"][k]["rows"] if r["k"] == "chips"][0]
    # 10.10 (runda 4): myslnik listy to marker (jak punktor): kafle go nie maja, zawsze zielen marki (nie akcent)
    assert len(ch["items"]) == 4 and not any(t.startswith(("–", "-")) for t in ch["items"]) and ch.get("fill", "brand") == "brand"
    assert wier["znaki"] == [] and any(m["slajd"] == 9 for m in wier["markery"])  # zdjety marker wpisany w pokrycie


def test_wiernosc_zlapie_zdjety_nawias():
    assert pc._interp("(Byron Sharp, Ehrenberg-Bass).") - pc._interp("Byron Sharp, Ehrenberg-Bass") ==         pc.collections.Counter({"(": 1, ")": 1, ".": 1})


def test_obrazy_w_calosci_proporcje_bez_kadrowania(tmp_path_factory):
    import io
    from PIL import Image
    from pptx import Presentation
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    rob = str(tmp_path_factory.mktemp("img"))
    build_dk.build(spec, os.path.join(rob, "w.pptx"))
    prs = Presentation(build_dk.build.last_out)
    for src in (15, 25, 34, 35, 36, 38, 42):
        for k in spec["mapa"][str(src)]:
            for sh in prs.slides[k].shapes:
                if sh.shape_type == 13 and not sh.name.startswith("!!"):
                    w, h = Image.open(io.BytesIO(sh.image.blob)).size
                    assert abs(sh.width / sh.height - w / h) / (w / h) < 0.02, "slajd %d: obraz rozciagniety" % src
                    assert not (sh.crop_left or sh.crop_right or sh.crop_top or sh.crop_bottom), "slajd %d: kadrowanie" % src


def test_s34_rzad_obrazow_od_brzegu_do_brzegu(tmp_path_factory):
    from pptx import Presentation
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    rob = str(tmp_path_factory.mktemp("rz"))
    build_dk.build(spec, os.path.join(rob, "w.pptx"))
    prs = Presentation(build_dk.build.last_out)
    pics = [sh for sh in prs.slides[spec["mapa"]["34"][0]].shapes if sh.shape_type == 13 and not sh.name.startswith("!!")]
    assert abs(min(p.left for p in pics) - build_dk.MX) < 20000  # < 0,6 mm
    assert abs(max(p.left + p.width for p in pics) - (build_dk.W - build_dk.MX)) < 20000


def test_s22_dwie_karty_rownej_wysokosci_tresc_od_gory(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    sp = spec["slides"][spec["mapa"]["22"][0]]
    ms, _f = build_dk.uklad_layout(sp)
    m = next(x for x in ms if x["kind"] == "cols")
    assert len({round(x) for x in m["hs"]}) == 1 and m["valign"] == "t"  # 10.10: równa wysokość kart, krótsza treść od góry
    assert min(m["chs"]) < 0.85 * max(m["chs"])  # treść faktycznie nierówna
    assert not any("łatwy" in ln and "do przegryzienia" not in ln and ln.endswith("łatwy")
                   for parts, _w in m["cols"] for (kind, _y, _h, d) in parts if kind == "txt" for ln in d["lines"])
    for n in (18, 24, 37, 40):  # trzy karty / podobna tresc: wszystkie karty rowne
        ms, _f = build_dk.uklad_layout(spec["slides"][spec["mapa"][str(n)][0]])
        assert all(len({round(x) for x in m["hs"]}) == 1 for m in ms if m["kind"] == "cols")


def test_zakonczenie_na_srodku_pionowo(tmp_path_factory):
    from pptx import Presentation
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    sp = spec["slides"][spec["mapa"]["43"][0]]
    assert sp["type"] == "end" and sp["valign"] == "m"
    rob = str(tmp_path_factory.mktemp("end"))
    build_dk.build(dict(spec, slides=[sp]), os.path.join(rob, "e.pptx"))
    sl = Presentation(build_dk.build.last_out).slides[0]
    logo = next(sh for sh in sl.shapes if sh.name == "!!logo")
    tag = next(sh for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.startswith("#"))
    srodek = (logo.top + tag.top + tag.height - build_dk.cm(0.2)) / 2  # tekst hasztagu zajmuje ok. 1,4 z 1,8 cm
    assert abs(srodek - build_dk.H / 2) < build_dk.cm(0.8)


# --- 4a. runda 4 (10.10): karty na pelna szerokosc, wielkosc liter po lamaniu, cytat jak s20, kafle, podpis pod rzedem ----
def _linie_kart(spec, n):
    """[(liczba kart w wierszu, [wiersze tekstu Lato])] dla slajdu zrodla n (z miar ukladu)."""
    out = []
    for k in spec["mapa"][str(n)]:
        sp = spec["slides"][k]
        ms, _f = build_dk.uklad_layout(sp)
        for m in ms:
            if m["kind"] == "cols":
                out.append((len(m["cols"]), m["pad"], [d for parts, _w in m["cols"] for (kind, _y, _h, d) in parts
                                                      if kind == "txt" and d["font"] == "body"]))
    return out


def test_s18_s21_s40_linie_w_kartach_nie_sa_rwane(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    for n in (18, 21, 40):
        for ncols, pad, bloki in _linie_kart(spec, n):
            assert pad <= build_dk.cm(0.61)  # pole tekstu = szerokosc karty minus 2 x ~0,6 cm
            for d in bloki:
                slow = sum(len(x.split()) for x in d["lines"])
                if slow >= 8:  # 3 wąskie karty obok siebie: >= 3,5 słowa w wierszu; karty jedna pod drugą: pełna szerokość
                    assert slow / len(d["lines"]) >= (3.5 if ncols >= 3 else 4), (n, d["lines"])


def test_kontynuacja_mala_litera_i_nowy_akapit_wielka(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    t26 = " ".join(bl["t"] for r in spec["slides"][spec["mapa"]["26"][0]]["rows"] for it in r.get("items", [])
                   for bl in it["blocks"])
    assert "ważny ale równie" in t26 and "Ale równie" not in t26  # wiersz-kontynuacja po wierszu bez kropki: mała litera
    bl41 = [bl["t"] for r in spec["slides"][spec["mapa"]["41"][0]]["rows"] for it in r.get("items", []) for bl in it["blocks"]]
    assert any(t.startswith("Dla segmentu szkolnego") for t in bl41)  # po łączu kończącym zdanie: osobny akapit, wielka litera
    assert not any("udaru dla segmentu" in t for t in bl41)


def test_split_vt_lacze_konczy_zdanie():
    t = "Erytrytol bez kropki na koncu\vDla segmentu szkolnego"
    assert [x for x, _h, _e in pc._split_vt(t, True)] == ["Erytrytol bez kropki na koncu Dla segmentu szkolnego"]
    assert [x for x, _h, _e in pc._split_vt(t, True, [True, False])] == ["Erytrytol bez kropki na koncu", "Dla segmentu szkolnego"]
    assert [x for x, _h, _e in pc._split_vt("Ala ma\vkota", True, [True, False])] == ["Ala ma kota"]  # po łączu, ale mała litera


def test_chronione_slowo_po_kropce_to_poczatek_zdania(tmp_path_factory):
    model, _spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    assert "Ale" not in pc._chronione(model)  # „…fizycznej. Ale samo białko” - początek zdania, nie nazwa własna


def test_s41_jeden_rozmiar_pisma_min_14(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    bloki = _linie_kart(spec, 41)[0][2]
    assert len({d["pt"] for d in bloki}) == 1 and bloki[0]["pt"] >= 14 and len(bloki) == 3  # WHO + Erytrytol + Dla segmentu


def test_cytat_jak_s20_i_autor_pogrubiony(tmp_path_factory):
    from pptx import Presentation
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    rob = str(tmp_path_factory.mktemp("cyt"))
    build_dk.build(spec, os.path.join(rob, "w.pptx"))
    sl = Presentation(build_dk.build.last_out).slides[spec["mapa"]["7"][0]]
    runy = [(r, p.text) for sh in sl.shapes if sh.has_text_frame for p in sh.text_frame.paragraphs for r in p.runs]
    q = next(r for r, t in runy if t.startswith("Brands grow") or t.startswith("new buyers") or "constant" in t)
    assert q.font.size.pt >= 28 and q.font.italic  # s20 szablonu: 30 pt kursywa
    aut = [r for r, t in runy if t in ("(", "Byron Sharp", ", Ehrenberg-Bass).") or t.endswith("Ehrenberg-Bass).")]
    assert aut and all(r.font.bold and r.font.size.pt >= 14 for r in aut)  # autor pogrubiony Lato >= 14 pt (hiperłącze zostaje)


def test_kafle_rowna_siatka():
    m = build_dk._uk_chips({"k": "chips", "items": ["– A", "Dluzsze haslo wiersza", "B", "Haslo srednie"], "per_row": 2},
                           1.0, build_dk.W - 2 * build_dk.MX)
    assert m["ws"][0] == m["ws"][2] and m["ws"][1] == m["ws"][3]  # kafle jednej kolumny tej samej szerokosci
    assert m["fill"] == "brand"


def test_s38_podpis_pod_srodkiem_rzedu_obrazow(tmp_path_factory):
    from pptx import Presentation
    _model, spec, _cov, _wier = _zbuduj("co_dalej", tmp_path_factory)
    rob = str(tmp_path_factory.mktemp("sub"))
    build_dk.build(spec, os.path.join(rob, "w.pptx"))
    sl = Presentation(build_dk.build.last_out).slides[spec["mapa"]["38"][0]]
    pics = [sh for sh in sl.shapes if sh.shape_type == 13 and not sh.name.startswith("!!")]
    sub = next(sh for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.startswith("A konkurencja"))
    cx = (min(p.left for p in pics) + max(p.left + p.width for p in pics)) / 2
    assert abs((sub.left + sub.width / 2) - cx) < build_dk.cm(0.1)


# --- 4b. szablonowanie S1-S13 (13.10.2026, szablonuj.py): sztuczne wiersze, po jednym teście na regułę ------------------
import szablonuj as sz  # noqa: E402


def _sp(rows, **kw):
    return dict({"type": "uklad", "title": "Tytuł slajdu", "rows": rows, "zrodlo": 1}, **kw)


def _cols(*items, **kw):
    return dict({"k": "cols", "items": list(items), "card": True, "kont": True, "pad": 1.0, "min_h": 0, "valign": "m"}, **kw)


def _it(*blocks, **kw):
    return dict({"blocks": list(blocks)}, **kw)


def _b(k, t, **kw):
    return dict({"k": k, "t": t, "align": "l"}, **kw)


def _rodzaje(sp):
    return [r["k"] for r in sp["rows"]]


def _bloki(sp, k):
    return [b for r in sp["rows"] if r["k"] == "cols" for it in r["items"] for b in it["blocks"] if b["k"] == k]


def _stosuj(rows, wstrzymane=None, **kw):
    sp = _sp(rows, **kw)
    nowy, dec = sz.stosuj(sp, 7, wstrzymane)
    assert nowy is not None, "reguła nie zadziałała"
    assert sz.slowa(sp) == sz.slowa(nowy)  # żadne słowo nie zginęło ani nie doszło (poza hero / ikonami)
    return nowy, dec


def test_s1_wniosek_pas_pod_obrazami_i_po_kartach():
    pics = {"k": "pics", "items": [{"image": "a.png", "caption": ""}]}
    n, d = _stosuj([pics, {"k": "sub", "t": "Ale dania gotowe to inny dzień i temat….", "color": "brand"}])
    assert _rodzaje(n) == ["pics", "band"] and n["rows"][1]["fill"] == "brand" and n["valign"] == "t"
    n, _d = _stosuj([pics, {"k": "sub", "t": "A konkurencja nam odjechała..", "color": "accent"}])
    assert n["rows"][1]["fill"] == "accent"  # czerwony podpis (zła wiadomość) -> pas czerwony
    n, _d = _stosuj([_cols(_it(_b("p", "Fakt jeden."))), {"k": "lead", "t": "Ważna kwestia – to nie jest jednolity segment",
                                                          "po_kartach": True, "pt": 22}])
    assert _rodzaje(n) == ["cols", "band"] and n["rows"][1]["t"].startswith("Ważna kwestia")


def test_s1_wniosek_z_karty_c_d_e_f():
    # (d) ostatnia linia od „=”
    n, _d = _stosuj([_cols(_it(_b("lead", "Produkt: jasno zdefiniowany"), _b("lead", "= Rozwiązanie produktowe", color="accent")))])
    assert _rodzaje(n)[-1] == "band" and n["rows"][-1]["t"] == "= Rozwiązanie produktowe"
    # (c) ostatni akapit karty cały w kolorze i <= 14 słów
    n, _d = _stosuj([_cols(_it(_b("p", "Pierwszy akapit z faktami i liczbami o rynku."), _b("p", "Konsumenci rozumieją oś jelita–skóra",
                                                                                          color="accent")))])
    assert _rodzaje(n) == ["cols", "band"] and [b["k"] for b in n["rows"][0]["items"][0]["blocks"] if b["k"] != "icon"] == ["lead"]
    # (e) ostatnie zdanie ostatniej karty zaczyna się od „Ale ”; ostatnia karta-zdanie od „Temat do”
    n, _d = _stosuj([_cols(_it(_b("p", "Trend na białko jest powrotem do piramidy.")),
                           _it(_b("p", "Idzie w parze razem z propagacją aktywności. Ale samo białko człowiekowi nie wystarcza")))])
    assert n["rows"][-1]["k"] == "band" and n["rows"][-1]["t"].startswith("Ale samo")
    n, _d = _stosuj([_cols(_it(_b("p", "Pierwsze zdanie karty jeden.")), _it(_b("p", "Drugie zdanie karty dwa.")),
                           _it(_b("p", "Temat do rozwinięcia zarówno produktowo jak i komunikacji")))])
    assert n["rows"][-1]["k"] == "band" and len(n["rows"][0]["items"]) == 2
    # (f) karta-artykuł z dokładnie 2 zdaniami, drugie <= 12 słów
    n, _d = _stosuj([_cols(_it(_b("p", "Ludzie coraz bardziej przenoszą zasadę balansu na sferę aktywności. Trening jest ważny ale "
                                       "równie ważna staje się ta część po nim.")))])
    assert _rodzaje(n) == ["cols", "band"]
    # „Insight:” jako goły wiersz -> pas z żarówką
    n, _d = _stosuj([{"k": "h", "t": "Insight: potrzeba bycia pięknym i zadbanym", "align": "l"}])
    assert n["rows"][0]["k"] == "band" and n["rows"][0]["icon"] == "lightbulb"


def test_s3_naglowek_na_tytul():
    pics = {"k": "pics", "items": [{"image": "a.png", "caption": ""}]}
    n, _d = _stosuj([{"k": "h", "t": "Lubimy się rozpieszczać a przeżycia są ważniejsze"}, pics], title="Inna percepcja premium")
    assert n["kicker"] == "Inna percepcja premium" and n["title"].startswith("Lubimy") and _rodzaje(n) == ["pics"]


def test_s4_kafle_ikony_chips_i_punkty():
    n, _d = _stosuj([{"k": "chips", "items": ["Długowieczność", "Wysoka sprawność fizyczna", "Atrakcyjność", "Większe funkcje"],
                      "per_row": 2}])
    assert _rodzaje(n) == ["cols", "cols"] and all(len(r["items"]) == 2 for r in n["rows"])  # 4 pozycje = 2 x 2
    assert len(_bloki(n, "icon")) == 4 and len(_bloki(n, "lead")) == 4
    n, _d = _stosuj([_b("b", "Alfa beta", li=True), _b("b", "Gamma delta", li=True), _b("b", "Epsilon zeta", li=True)])
    assert _rodzaje(n) == ["cols"] and len(n["rows"][0]["items"]) == 3 and all(
        b["name"] == "sparkles" for b in _bloki(n, "icon"))  # brak trafienia w słowniku -> sparkles


def test_s6_etykieta_wartosc():
    n, _d = _stosuj([{"k": "h", "t": "CT: kobiety z segmentu 20-35 lat\nTA: kobiety 35-60 lat", "align": "l"}])
    kv = _bloki(n, "kv")
    assert [b["label"] for b in kv] == ["CT:", "TA:"] and kv[1]["t"] == "kobiety 35-60 lat"


def test_s7_lista_z_ikona():
    n, _d = _stosuj([_cols(_it(_b("h", "Kierunki / rozwiązania"), _b("p", "Format miękki, łatwy do przegryzienia.", wyr="-aaaa"),
                               _b("p", "Mała porcja i otwieranie bez wysiłku."), _b("p", "Białko plus witamina D, wapń i B12.", color="accent"),
                               _b("p", "Bez komunikacji dla seniorów, bo takie etykiety zwykle odpychają.")))])
    li = _bloki(n, "li")
    assert len(li) == 4 and all(b["icon"] == "check" for b in li) and li[2]["wyr"] == "a" * len(li[2]["t"].split())
    # kolumny bez kart: nagłówek + akapit z punktorami „• ”
    kol = {"k": "cols", "card": False, "items": [_it(_b("h", "Osoby")), _it(_b("h", "Wartości odżywcze"),
                                                                           _b("p", "•\xa0Cynk\n•\xa0Magnez\n•\xa0Kolagen"))]}
    n, _d = _stosuj([kol])
    assert n["rows"][0]["card"] is True and len(_bloki(n, "li")) == 3


def test_s8_teza_zielona_i_haslo_z_ikona():
    n, _d = _stosuj([_cols(_it(_b("lead", "Konieczność większego oddalenia produktów od siebie"),
                               _b("lead", "Pod względem okazji oraz benefitu")))])
    assert n["rows"][0]["items"][0]["fill"] == "brand" and n["rows"][0]["items"][0]["align"] == "c"
    n, _d = _stosuj([_cols(_it(_b("lead", "To slajdy z konceptem – wpiszesz dane?")))])
    assert _bloki(n, "icon") and "fill" not in n["rows"][0]["items"][0]


def test_s9_para_kontrast():
    n, _d = _stosuj([_cols(_it(_b("h", "Dobra wiadomość –", one_line=True), _b("lead", "rynek rośnie", color="brand")),
                           _it(_b("h", "Zła wiadomość –", one_line=True, color="accent"), _b("lead", "rośniemy wolniej", color="brand")))])
    ik = [b["name"] for b in _bloki(n, "icon")]
    assert ik == ["trending-up", "trending-down"] and all(b["color"] == "ink" for b in _bloki(n, "lead"))


def test_s10_temat_pas_i_lista_pod_naglowkiem():
    t = ("Białko – NCEŻ zaleca seniorom 1,2 g/kg dziennie, więc więcej niż ogólna norma 0,9. Sarkopenia dotyczy ok. 10% osób w "
         "wieku 60–70 lat i ponad 50% po 80., a w badaniu IŻŻ ponad połowa 70-letnich kobiet jadła za mało białka")
    w = "a" + "-" * (len(t.split()) - 1)
    n, _d = _stosuj([_cols(_it(_b("p", t, wyr=w)))])
    assert n["rows"][0]["k"] == "band" and n["rows"][0]["t"] == "Białko –" and n["rows"][0]["icon"]
    assert n["rows"][1]["k"] == "cols" and len(n["rows"][1]["items"]) == 2
    n, _d = _stosuj([_cols(_it(_b("h", "2 kierunki poszukiwań:"), _b("lead", "Odpowiedź na potrzeby obecnych konsumentów"),
                               _b("lead", "Pozyskanie szczególnie młodych konsumentów")))])
    # S14f: jeden wiersz - karta zielona z nagłówkiem + 2 karty-hasła (ink) obok siebie
    assert _rodzaje(n) == ["cols"] and len(n["rows"][0]["items"]) == 3 and n["rows"][0]["items"][0]["fill"] == "brand"
    assert [b["color"] for it in n["rows"][0]["items"][1:] for b in it["blocks"]] == ["ink", "ink"]
    # wersja wejścia z programu: nagłówek jako goły wiersz h + wiersz 2 kart z hasłami
    n, _d = _stosuj([{"k": "h", "t": "2 kierunki poszukiwań:", "align": "c"},
                     _cols(_it(_b("lead", "Odpowiedź na potrzeby obecnych konsumentów")),
                           _it(_b("lead", "Pozyskanie szczególnie młodych konsumentów")))], kicker="Kierunki")  # kicker: nagłówek nie idzie na tytuł (S3)
    assert _rodzaje(n) == ["cols"] and len(n["rows"][0]["items"]) == 3


# --- S14 „hasłowanie” (13.10, user: „za dużo Lato, za mało haseł”): zdanie w karcie = hasło Mindset + krótki dopisek ------------
def test_s2_s5_s11_s14_domyslnie_wlaczone():
    assert sz.WSTRZYMANE == set()
    karty = [_it(_b("p", "W 2024 r. osoby 65+ to 7,7 mln, czyli 20,6% ludności, a mediana wieku ma przekroczyć 50 lat.")),
             _it(_b("p", "GUS prognozuje ok. 30% populacji 65+ w 2060 r.")), _it(_b("p", "Udział osób 80+ ma wzrosnąć z 4,2% do 11,6%."))]
    n, _d = _stosuj([_cols(*karty)])
    assert [b["t"] for b in _bloki(n, "hero")] == ["7,7 mln", "30%", "11,6%"]  # S14d: pierwsza liczba z jednostką W HAŚLE, „z X do Y” = Y
    nowy, _d = sz.stosuj(_sp([_cols(*karty)]), 7, {"S14", "S2"})  # wyłączone: zdania zostają akapitami p
    assert nowy is None or not (_bloki(nowy, "hero") or _bloki(nowy, "lead"))
    n, _d = _stosuj([_cols(_it(_b("p", "Zaskakujące? Skoro numerem 1 jest ciągle energia.")), _it(_b("p", "Inna karta bez nagłówka tutaj.")))])
    assert _bloki(n, "h")[0]["t"] == "Zaskakujące?"  # S5: pierwsze zdanie <= 4 słowa -> nagłówek karty


def test_s14a_haslo_ze_zdania_trzy_przypadki():
    # (1) zdanie <= 12 słów: całe jako lead ink, bez dopisku
    n, _d = _stosuj([_cols(_it(_b("p", "Idzie w parze razem z propagacją aktywności fizycznej.")),
                           _it(_b("p", "Tkanka tłuszczowa nie oznacza sprawnych mięśni.")))])
    ld = _bloki(n, "lead")
    assert [b["t"] for b in ld] == ["Idzie w parze razem z propagacją aktywności fizycznej.", "Tkanka tłuszczowa nie oznacza sprawnych mięśni."]
    assert all(b["color"] == "ink" for b in ld) and not _bloki(n, "p")
    # (2) dłuższe z przecinkiem po 4-15 słowach: lead do przecinka, reszta = p max_pt 18
    n, _d = _stosuj([_cols(_it(_b("p", "Polacy wydali na leki GLP-1 w 2025 r. ok. 3,4 mld zł, wobec 1,8 mld w 2024. Użytkownicy jedzą mniej.")),
                           _it(_b("p", "Inna krótka karta tutaj.")))], wstrzymane={"S15"})  # S15 rozdzieliłaby zdania na kafle
    assert _bloki(n, "lead")[0]["t"].endswith("3,4 mld zł,")
    p = _bloki(n, "p")[0]
    assert p["t"] == "wobec 1,8 mld w 2024. Użytkownicy jedzą mniej." and p["max_pt"] == 18  # kolejne zdania zostają p
    # (3) bez przecinka: przed pierwszym spójnikiem i / oraz / ale / wobec / czyli na pozycji 4-15
    n, _d = _stosuj([_cols(_it(_b("p", "Trend na białko jest powrotem do właściwej piramidy żywienia i odwrotem o węglowodanów")),
                           _it(_b("p", "Inna krótka karta tutaj.")))])
    assert _bloki(n, "lead")[0]["t"] == "Trend na białko jest powrotem do właściwej piramidy żywienia"
    assert _bloki(n, "p")[0]["t"] == "i odwrotem o węglowodanów"
    # bez granicy i bardzo długie (> 24 słów): zostaje akapitem Lato
    dlugie = " ".join(["słowo"] * 30) + "."
    n, _d = _stosuj([_cols(_it(_b("p", dlugie)), _it(_b("p", "Inna krótka karta tutaj.")))])
    assert dlugie in [b["t"] for b in _bloki(n, "p")]


def test_s14b_czerwone_haslo_traci_wyroznienie():
    t = "Zaburzenia lipidowe dotyczą 21–22 mln dorosłych"
    n, _d = _stosuj([_cols(_it(_b("p", t, wyr="a" * len(t.split()))), _it(_b("p", "Inna krótka karta tutaj.")))])
    ld = _bloki(n, "lead")[0]
    assert "wyr" not in ld and ld["color"] == "ink"  # >= 80% „a” = bez wyróżnienia
    n, _d = _stosuj([_cols(_it(_b("p", "Nadwaga nie wyklucza niedożywienia mięśniowego.", wyr="a----")),
                           _it(_b("p", "Inna krótka karta tutaj.")))])
    assert _bloki(n, "lead")[0]["wyr"] == "a----"  # pojedyncze wyróżnione słowo zostaje


def test_s14c_jedno_haslo_na_karte_w_rzedzie_3_kart():
    karty = [_it(_b("p", "Wzrost napędza kolagen. Żelki funkcjonalne to najszybciej rosnący format, szczególnie wśród Gen Z.")),
             _it(_b("p", "Druga karta ma krótkie zdanie.")), _it(_b("p", "Trzecia karta ma krótkie zdanie."))]
    n, _d = _stosuj([_cols(*karty)])
    k1 = n["rows"][0]["items"][0]["blocks"]
    assert [b["k"] for b in k1 if b["k"] != "icon"] == ["h", "p"] and k1[-1]["max_pt"] == 18  # h-hasło (3 słowa) + sam dopisek
    n, _d = _stosuj([_cols(karty[0], karty[1])])  # w rzędzie 2 kart: hasło + dopisek też pod nagłówkiem
    assert [b["k"] for b in n["rows"][0]["items"][0]["blocks"] if b["k"] != "icon"][:2] == ["h", "lead"]


def test_s14d_liczba_bohater_z_hasla_nie_z_dopisku():
    karty = [_it(_b("p", "Prognoza NFZ na 2035 r. to ponad 35% mężczyzn i ponad 25% kobiet z otyłością, a samo leczenie kosztowało NFZ 3,8 mld zł.")),
             _it(_b("p", "Cukrzyca dotyczy ok. 3 mln osób.")), _it(_b("p", "Druga karta bez liczby tutaj jest."))]
    n, _d = _stosuj([_cols(*karty)])
    assert [b["t"] for b in _bloki(n, "hero")] == ["35%", "3 mln"]  # nie „3,8 mld zł” z dopisku
    # hero tuż przed hasłem swojej karty, karta bez liczby dostaje ikonę (jeśli słownik trafia) albo nic
    assert [b["k"] for b in n["rows"][0]["items"][0]["blocks"]][:2] == ["hero", "lead"]
    # nagłówek-liczba autora („11 g”) to już bohater: bez drugiego hero
    n, _d = _stosuj([_cols(_it(_b("h", "11 g"), _b("p", "Błonnika w 100 g")), _it(_b("h", "0%"), _b("p", "Dodatku cukru")))])
    assert not _bloki(n, "hero")


def test_s14e_akapit_4_zdan_w_karcie_z_etykieta_pierwsze_haslo_reszta_li():
    t = ("w badaniu osoby z najwyższym poziomem erytrytolu we krwi i czynnikami ryzyka miały dwa razy większe ryzyko zawału. "
         "Krytycy zwracają uwagę na dane. EFSA i FDA uznają erytrytol za bezpieczny. Podobny sygnał opisano dla ksylitolu.")
    n, _d = _stosuj([_cols(_it(_b("h", "Erytrytol:"), _b("p", t)), _it(_b("h", "Słodziki:"), _b("p", "WHO zaleca warunkowo, by nie stosować.")))])
    bl = n["rows"][0]["items"][0]["blocks"]
    assert [b["k"] for b in bl] == ["h", "lead", "p", "li", "li", "li"] and all(b["icon"] == "check" for b in bl[3:])
    assert bl[3]["t"] == "Krytycy zwracają uwagę na dane."


def test_s14f_krotkie_zdania_w_kartach_zawsze_lead():
    n, _d = _stosuj([_cols(_it(_b("p", "Z wiekiem spada liczba kubków smakowych.")), _it(_b("p", "Rośnie zapotrzebowanie na witaminę D.")))])
    assert len(_bloki(n, "lead")) == 2 and not _bloki(n, "p")


def test_s14g_wniosek_z_danych_zdanie_od_to():
    t = ("Osoby 65+ podjadają głównie owoce i warzywa (49%) oraz słodkości (31%), a słone przekąski prawie odrzucają (4%). "
         "To naturalne terytorium marki opartej na owocach i orzechach, a nie na solonych chrupkach")
    n, _d = _stosuj([_cols(_it(_b("p", t)), _it(_b("h", "Kierunki:"), _b("p", "Format miękki, łatwy do przegryzienia.")))])
    assert n["rows"][-1]["k"] == "band" and n["rows"][-1]["t"].startswith("To naturalne terytorium")


def test_s14h_naglowek_do_myslnika_na_slajdzie_z_3_wierszami():
    kv = {"k": "h", "t": "CT: młodzi z segmentu 20-35 lat\nTA: mężczyźni 35-55 lat", "align": "l"}
    karty = _cols(_it(_b("p", "Matcha to nie tylko smak ale pewien Manifest – młodzi, nie chcą przepłacać za dobra luksusowe ale chcą się rozpieszczać")),
                  _it(_b("p", "Główna kawiarnia w PL to żabka a poza Mcdonaldsem to costa coffee (110)")))
    pas = {"k": "p", "t": "Ważna kwestia – żabka się otwiera na X I Y", "po_kartach": True, "pt": 17}
    n, _d = _stosuj([karty, kv, pas])
    assert n["rows"][0]["k"] == "h" and n["rows"][0]["color"] == "brand" and n["rows"][0]["t"].endswith("Manifest –")
    assert _rodzaje(n) == ["h", "cols", "cols", "band"] and not _bloki(n, "icon")  # karty bez ikon (ikony zabierały wysokość)
    # slajd z 2 wierszami (karty + obrazy): nagłówek zostaje w karcie (s34)
    pics = {"k": "pics", "items": [{"image": "a.png", "caption": ""}]}
    n, _d = _stosuj([_cols(karty["items"][0]), pics])
    assert n["rows"][0]["k"] == "cols" and _bloki(n, "h")[0]["t"].endswith("Manifest –")


def test_karta_z_5_akapitami_zostaje_lista_bez_hasel():
    bl = [_b("p", "Pierwszy punkt listy tutaj jest.")] * 5
    sp = _sp([_cols(_it(*bl), _it(_b("p", "Inna karta jest krótka.")))])
    n, _d = sz.stosuj(sp, 3)
    assert n is None or len(_bloki(n, "p")) == 5 and len(_bloki(n, "lead")) <= 1


def test_miara_slow_mindset_wiecej_niz_lato_w_kartach(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj_szablon("co_dalej", tmp_path_factory)
    m = sz.miara_slow(spec["slides"])
    assert m["lead"] + m["h"] > m["p"] + m["li"], m  # 13.10: za dużo Lato = odwrócone proporcje; ręczna ma 492 / 309, automat ~480 / ~320


def test_s12_wysokosc_kart_min_65_proc_pola():
    sp, _d = _stosuj([_cols(_it(_b("h", "Dobra wiadomość –", one_line=True), _b("lead", "rynek rośnie")),
                            _it(_b("h", "Zła wiadomość –", one_line=True), _b("lead", "rośniemy wolniej")))], pad=0.5)
    sp2 = sz.rozloz(dict(sp, rows=[dict(sp["rows"][0], min_h=0, pad=0.5)]), build_dk)
    ms, f = build_dk.uklad_layout(sp2)
    avail = build_dk.CB - build_dk.uklad_top(sp2)
    total = sum(m["h"] for m in ms) + sum(m["gap"] for m in ms[1:])
    assert sp2["valign"] == "t" and total >= 0.64 * avail


def test_s13_slownik_ikon_80_wpisow_i_ikony_istnieja():
    import json
    d = json.load(open(sz.IKONY_JSON, encoding="utf-8"))
    assert len(d["rdzenie"]) + len(d["slowa"]) >= 80
    # 13.10: zestaw marki `dk` (<nazwa>.png; zapas: stare svg) - każda nazwa słownika ma swój plik ikony
    brak = sorted((set(d["rdzenie"].values()) | set(d["slowa"].values())) - {n for n in set(d["rdzenie"].values()) | set(d["slowa"].values())
                                                                             if sz.ikona_istnieje(n)})
    assert brak == [], brak
    assert sz.ikona_dla("zupełnie bez trafienia xyz") is None  # brak trafienia = None (S4: wtedy sparkles)


def test_s13_ikona_dla_pierwsze_trafienie_wlasny_slownik(monkeypatch):
    monkeypatch.setattr(sz, "_IK", ([("białk", "biceps-flexed"), ("czas", "clock")], {"pieniądz": "wallet"}))
    assert sz.ikona_dla("Białko dla seniorów") == "biceps-flexed"
    assert sz.ikona_dla("Czas to pieniądz") == "clock"  # pierwsze trafienie w tekście wygrywa
    assert sz.ikona_dla("Pieniądz i czas") == "wallet" and sz.ikona_dla("nic tu nie ma") is None


def test_szablonowanie_nic_nie_zmienia_gdy_brak_wzorca():
    sp = _sp([_cols(_it(_b("p", " ".join(["zwykły"] * 30) + ".")))])  # > 24 słów bez granicy: S14a zostawia akapit, żadna reguła nie pasuje
    assert sz.stosuj(sp, 3) == (None, [])


def test_szablon_co_dalej_klocki_i_tresc_bez_strat(tmp_path_factory):
    model, spec, cov, wier = _zbuduj_szablon("co_dalej", tmp_path_factory)
    assert cov["brakuje"] == [] and wier["usterki"] == [] and wier["znaki"] == []
    assert len(spec["slides"]) == 43 and len(spec["szablon"]) >= 25
    def sl(n):
        return spec["slides"][spec["mapa"][str(n)][0]]
    assert sl(9)["kicker"] == "Kluczowe kierunku rozwoju" and sl(9)["title"].startswith("Kierunek, w którym")  # S3
    assert [r["k"] for r in sl(7)["rows"]][-1] == "band"  # S1(d)
    assert len(_bloki(sl(14), "kv")) == 2 and any(r["k"] == "band" and r.get("icon") == "lightbulb" for r in sl(14)["rows"])  # S6 + Insight
    assert any(r["k"] == "band" and r["fill"] == "accent" for r in sl(38)["rows"])  # czerwony podpis -> pas czerwony
    assert sl(3)["rows"][0]["items"][0]["fill"] == "brand"  # S8
    assert len(_bloki(sl(22), "li")) == 4 and len(_bloki(sl(15), "li")) == 6  # S7
    teksty10 = [b["t"] for b in _bloki(sl(10), "lead") + _bloki(sl(10), "p")]
    assert "Odpowiedź na potrzeby obecnych konsumentów" in teksty10 and "Pozyskanie szczególnie młodych konsumentów" in teksty10


# --- 4c. S15, ikony tylko tam gdzie pomagają, placeholdery, wzory z katalogu, lint, poprawki (13.10, kontynuacja) ----------------
IK_TEST = ([("komunikac", "megaphone"), ("użytkown", "users"), ("młod", "users"), ("wzrost", "trending-up"), ("produkt", "package")], {})
P12_1 = ("Wydatki Polaków na beauty wzrosły w 2025 r. o 7,8%, a najszybciej rośnie grupa wydająca jednorazowo > 500 zł. "
         "komunikacjaod anti-agingu do prewencji i longevity.")
P12_2 = ("Wzrost napędza kolagen. Żelki funkcjonalne to najszybciej rosnący format, szczególnie wśród Gen Z i millenialsów, "
         "a liderem sprzedaży są napoje i shoty kolagenowe.")
P31_1 = ("Polacy wydali na leki GLP-1 w 2025 r. ok. 3,4 mld zł wobec 1,8 mld w 2024. Użytkownicy jedzą mniej, przechodzą na białko "
         "i świeże produkty, odchodzą od cukru oraz przetworzonych przekąsek.")


def test_s15_s12_jedno_zdanie_jeden_kafel_trzy_kafle_i_pas(monkeypatch):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    n, d = _stosuj([_cols(_it(_b("p", P12_1, wyr="a" * 10 + "-" * 15), _b("p", P12_2),
                              _b("p", "Konsumenci rozumieją oś jelita–skóra", color="accent")))])
    assert _rodzaje(n) == ["cols", "band"] and n["rows"][1]["t"].startswith("Konsumenci")
    k = n["rows"][0]["items"]
    assert len(k) == 3  # 7,8 % | komunikacjaod… | Wzrost napędza kolagen + dopisek
    assert [b["k"] for b in k[0]["blocks"]][:2] == ["hero", "lead"] and k[0]["blocks"][0]["t"] == "7,8%"
    assert k[1]["blocks"][0]["k"] == "icon" and k[1]["blocks"][0]["name"] == "megaphone"  # kafel bez liczby = ikona (S13)
    assert k[1]["blocks"][1]["t"] == "komunikacjaod anti-agingu do prewencji i longevity."
    assert [b["k"] for b in k[2]["blocks"] if b["k"] != "icon"] == ["h", "p"] and k[2]["blocks"][-2]["t"] == "Wzrost napędza kolagen."
    assert any(x["wzorzec"] == "jedno-zdanie-kafel" for x in d)


def test_s15_s31_cztery_kafle_siatka_2x2_kolejnosc_wierszami(monkeypatch):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    n, _d = _stosuj([_cols(_it(_b("p", P31_1), _b("p", "Według PwC spożywają ok. 40% mniej kalorii, co daje koszyki mniejsze o 4–6%."),
                              _b("p", "Wydatki na słone przekąski spadły w tej grupie o 10,1%.")))])
    assert _rodzaje(n) == ["cols", "cols"] and [len(r["items"]) for r in n["rows"]] == [2, 2]
    kafle = [it for r in n["rows"] for it in r["items"]]
    assert [next((b["t"] for b in it["blocks"] if b["k"] == "hero"), None) for it in kafle] == ["3,4 mld zł", None, "40%", "10,1%"]
    assert kafle[1]["blocks"][0] == {"k": "icon", "name": "users", "bg": True}  # „Użytkownicy jedzą mniej…” bez liczby = ikona
    l1 = next(b for b in kafle[1]["blocks"] if b["k"] == "lead")
    assert l1["t"] == "Użytkownicy jedzą mniej, przechodzą na białko i świeże produkty,"  # hasło do przecinka po 4-15 słowach
    assert sum(1 for it in kafle for b in it["blocks"] if b["k"] == "p" and b["max_pt"] == 18) == 3


def test_s15_nie_dzieli_gdy_nie_spelnione(monkeypatch):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    # pierwsze zdanie <= 4 słowa to nagłówek karty (S5), nie osobny kafel; kolejne zdanie > 16 słów to nie „samodzielna myśl”
    n, _d = _stosuj([_cols(_it(_b("p", "Zaskakujące? Skoro numerem 1 jest ciągle energia a grupa stale aktywna sportowo wynosi 23%.")),
                           _it(_b("p", "Druga karta ma krótkie zdanie.")))])
    assert len(n["rows"][0]["items"]) == 2 and _bloki(n, "h")[0]["t"] == "Zaskakujące?"
    # bez liczby z jednostką to nie rząd kart-faktów
    n, _d = _stosuj([_cols(_it(_b("p", "Pierwsze zdanie ma pięć słów tutaj. Drugie zdanie jest krótkie.")),
                           _it(_b("p", "Inna karta jest krótka tutaj.")))])
    assert len(n["rows"][0]["items"]) == 2
    # po rozdzieleniu byłoby > 4 kafli: zostaje jak dziś
    karty = [_it(_b("p", "Pierwsze zdanie ma 5 mln słów tutaj. Drugie zdanie krótkie.")) for _ in range(3)]
    n, _d = _stosuj([_cols(*karty)])
    assert len(n["rows"][0]["items"]) == 3
    # karta z nagłówkiem-etykietą z „:” (S14e) zostaje
    n, _d = _stosuj([_cols(_it(_b("h", "Słodziki:"), _b("p", "WHO zaleca warunkowo, by nie stosować do 10% dawki. Drugie zdanie krótkie.")),
                           _it(_b("p", "Inna karta jest krótka tutaj.")))])
    assert len(n["rows"][0]["items"]) == 2
    # wyłączona regułą
    n, _d = _stosuj([_cols(_it(_b("p", P12_1), _b("p", P12_2), _b("p", "Konsumenci rozumieją oś jelita–skóra", color="accent")))],
                    wstrzymane={"S15"})
    assert len(n["rows"][0]["items"]) == 2


def test_s15_zl_kropka_w_srodku_wiersza_konczy_zdanie():
    zd = [x for x, _w in sz.zdania((P12_1, None))]
    assert zd[1] == "komunikacjaod anti-agingu do prewencji i longevity." and zd[0].endswith("500 zł.")
    assert len(sz.zdania(("Kosztuje 500 zł wobec 3 zł", None))) == 1  # „zł” bez kropki nie dzieli


def test_ikony_s7_haslo_w_karcie_bez_ikony(monkeypatch):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    quote = {"k": "quote", "t": "Cytat o produkcie", "author": "(Autor X)"}
    n, _d = _stosuj([quote, _cols(_it(_b("lead", "Produkt: jasno zdefiniowany", align="c"),
                                      _b("lead", "Potrzeba, grupa docelowa, okazja", align="c"),
                                      _b("lead", "= Rozwiązanie produktowe", color="accent", align="c")), valign="m")])
    assert _rodzaje(n) == ["quote", "cols", "band"] and not _bloki(n, "icon")  # wynik równania (s7): ani jednej ikony


def test_ikony_slajd_z_4_wierszami_bez_ikon_a_s14_z_ikonami(monkeypatch):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    kv = {"k": "h", "t": "CT: młodzi z segmentu 20-35 lat\nTA: mężczyźni 35-55 lat", "align": "l"}
    # s37: nagłówek + karty + kv + pas = 4 wiersze: karty bez ikon od razu
    karty = _cols(_it(_b("p", "Matcha to nie tylko smak ale pewien Manifest – młodzi, nie chcą przepłacać za dobra luksusowe ale chcą się rozpieszczać")),
                  _it(_b("p", "Główna kawiarnia w PL to produkt a poza Mcdonaldsem to costa coffee (110)")))
    pas = {"k": "p", "t": "Ważna kwestia – żabka się otwiera na X I Y", "po_kartach": True, "pt": 17}
    n, _d = _stosuj([karty, kv, pas])
    assert len(n["rows"]) >= 4 and not _bloki(n, "icon")
    # s14: dwie karty-hasła + Insight + kv = 3 wiersze: ikony zostają (jak we wzorcu)
    insight = {"k": "h", "t": "Insight: potrzeba bycia pięknym i zadbanym", "align": "l"}
    k14 = _cols(_it(_b("lead", "Młodzi wydają najwięcej ze wszystkich grup na zabiegi kosmetyczne")),
                _it(_b("lead", "Starsi poddani są presji bycia zdrowymi i wiecznie młodymi")))
    n, _d = _stosuj([k14, insight, kv])
    assert len(n["rows"]) == 3 and len(_bloki(n, "icon")) == 2


def test_placeholdery_w_nawiasach_kwadratowych_nietkniete():
    sp = _sp([_cols(_it(_b("p", "[Akapit 1: najważniejsza informacja. Krótkie zdania, jedna myśl w akapicie.]"),
                        _b("p", "[Akapit 2: rozwinięcie albo przykład. Więcej tekstu? Podziel na dwa slajdy.]")))])
    assert sz.stosuj(sp, 7) == (None, [])  # bez hasłowania, kafli, liczb-bohaterów
    sp = _sp([{"k": "chips", "items": ["[Hasło 1]", "[Hasło 2]", "[Hasło 3]"], "per_row": 3}], title="[Tytuł]")
    assert sz.stosuj(sp, 7) == (None, [])
    assert sz.stosuj(_sp([_cols(_it(_b("p", P12_1), _b("p", P12_2)))]), 7)[0] is not None  # bez nawiasów reguły działają


_KOMP = {}


def _skomponuj(nazwa, szablonuj, tpf):
    """compose na tym samym modelu i w tym samym katalogu roboczym (te same ścieżki obrazów), z szablonowaniem albo bez."""
    k = (nazwa, szablonuj)
    if k not in _KOMP:
        plik = PLIKI[nazwa]
        if not os.path.isfile(plik):
            pytest.skip("brak pliku %s" % plik)
        if ("model", nazwa) not in _KOMP:
            rob = str(tpf.mktemp("komp_" + nazwa))
            _KOMP[("model", nazwa)] = (pc.extract(plik, rob), rob)
        model, rob = _KOMP[("model", nazwa)]
        _KOMP[k] = pc.compose(model, {"wizualizacje": False, "wyjscie": rob, "szablonuj": szablonuj})
    return _KOMP[k]


def test_onlien_slajdy_z_placeholderami_nietkniete_przez_szablonowanie(tmp_path_factory):
    import json
    z, bez = _skomponuj("onlien", True, tmp_path_factory), _skomponuj("onlien", False, tmp_path_factory)
    assert len(z["slides"]) == len(bez["slides"])
    ile = 0

    def teksty(o):  # widoczne napisy slajdu (nie ścieżki obrazów ani listy liczb w JSON-ie)
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for k, v in o.items():
                if k in ("t", "title", "kicker", "label", "author", "caption", "items", "rows", "blocks"):
                    yield from teksty(v)
        elif isinstance(o, list):
            for x in o:
                yield from teksty(x)
    for a, b in zip(z["slides"], bez["slides"]):
        if any("[" in t or "]" in t for t in teksty({"title": b.get("title"), "kicker": b.get("kicker"), "rows": b.get("rows", [])})):
            ile += 1
            assert a == b, "slajd %s ze źródła z placeholderem został zmieniony" % b.get("zrodlo")
    assert ile >= 10  # onlien to instrukcja szablonu: dziesiątki slajdów z [...]
    assert {s["slajd"] for s in z["szablon"]} <= {a["zrodlo"] for a, b in zip(z["slides"], bez["slides"]) if a != b}


def test_s15_s18_s19_s20_s21_s28_ukladu_nie_zmienia(tmp_path_factory):
    _model, spec, _cov, _wier = _zbuduj_szablon("co_dalej", tmp_path_factory)

    def uklad(n):
        return [(r["k"], len(r["items"]) if r["k"] == "cols" else 0) for r in spec["slides"][spec["mapa"][str(n)][0]]["rows"]]
    assert uklad(18) == [("cols", 3), ("band", 0)] and uklad(28) == [("cols", 3)] and uklad(21) == [("cols", 3)]
    assert uklad(19) == [("band", 0), ("cols", 2)] and uklad(20) == [("band", 0), ("cols", 2)]
    assert uklad(12) == [("cols", 3), ("band", 0)] and uklad(31) == [("cols", 2), ("cols", 2)]  # S15
    assert not _bloki(spec["slides"][spec["mapa"]["7"][0]], "icon") and not _bloki(spec["slides"][spec["mapa"]["37"][0]], "icon")
    assert len(_bloki(spec["slides"][spec["mapa"]["14"][0]], "icon")) == 2


def _katalog_testowy(tmp_path, monkeypatch, ids):
    import json
    p = tmp_path / "katalog.json"
    p.write_text(json.dumps({"wersja": 1, "slajdy": [{"nr": int(i[1:]), "id": i, "nazwa": "Nazwa " + i} for i in ids]}), encoding="utf-8")
    monkeypatch.setattr(sz, "KATALOG_JSON", str(p))
    sz._KAT.clear()


def test_wzor_z_katalogu_w_decyzjach_i_w_uwadze(tmp_path, monkeypatch):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    rows = [_cols(_it(_b("p", P12_1), _b("p", P12_2), _b("p", "Konsumenci rozumieją oś jelita–skóra", color="accent")))]
    _katalog_testowy(tmp_path, monkeypatch, ["t62", "t38", "t56", "t61"])
    _n, d = _stosuj(rows)
    w = {x["wzorzec"]: x["wzor"] for x in d}
    assert w["jedno-zdanie-kafel"] == {"id": "t62", "nr": 62, "nazwa": "Nazwa t62"} and w["fakt-z-liczba"]["id"] == "t62"
    assert "wniosek-pas" in w and w["wniosek-pas"] is None  # reguła bez wzoru w mapowaniu: pole puste
    assert sz.opis_wzorow(d) == "slajd 7: Nazwa t62 (wzór: slajd 62 szablonu)"  # „Akapit w karcie” (t61) pominięty, gdy jest lepszy wzór
    _katalog_testowy(tmp_path, monkeypatch, ["t38"])  # brak t62 -> zapas t38 („Wskaźniki (KPI)”)
    assert sz.wzor("fakt-z-liczba")["id"] == "t38" and sz.wzor("kafle-ikony") is None
    monkeypatch.setattr(sz, "KATALOG_JSON", str(tmp_path / "nie-ma.json"))
    sz._KAT.clear()
    _n, d = _stosuj(rows)  # brak pliku katalogu: pole `wzor` puste, bez błędu
    assert all(x["wzor"] is None for x in d) and sz.opis_wzorow(d) == ""
    sz._KAT.clear()


def test_opis_wzorow_limit_12_i_reszta(tmp_path, monkeypatch):
    _katalog_testowy(tmp_path, monkeypatch, ["t62", "t56"])
    d = [{"slajd": i, "wzorzec": "kafle-ikony", "wzor": sz.wzor("kafle-ikony")} for i in range(1, 15)]
    d += [{"slajd": 1, "wzorzec": "haslowanie", "wzor": None}]
    s = sz.opis_wzorow(d)
    assert s.count("(wzór: slajd 56 szablonu)") == 12 and s.endswith("…i 2 innych (decyzje-szablon.json)")
    assert s.startswith("slajd 1: Nazwa t56 (wzór: slajd 56 szablonu); slajd 2:")
    sz._KAT.clear()


class _LintAtrapa:
    """Atrapa modułu lint_tekst zgodna z kontraktem (BRIEF-LINT): sprawdz([(nr, [teksty])]) i opis(u)."""
    def __init__(self, wyniki=None, wyjatek=None):
        self.wyniki, self.wyjatek, self.wywolania = wyniki or [], wyjatek, []

    def sprawdz(self, slajdy):
        self.wywolania.append(slajdy)
        if self.wyjatek:
            raise self.wyjatek
        return self.wyniki

    def opis(self, u):
        return "Slajd %d: „%s” wygląda na sklejone słowa - może „%s”?" % (u["slajd"], u["jest"], u["propozycja"])


def _u(nr, jest, prop, pewnosc="wysoka"):
    return {"slajd": nr, "rodzaj": "sklejone", "jest": jest, "propozycja": prop, "kontekst": "…" + jest + "…", "pewnosc": pewnosc}


def _model_lint():
    return {"slajdy": [{"n": 1, "texts": [{"paras": [{"t": "Raz  dwa\vtrzy"}]}], "tables": [{"rows": [["komórka", ""]]}]},
                       {"n": 12, "texts": [{"paras": [{"t": "komunikacjaod anti-agingu"}]}], "tables": []}]}


def test_lint_wpiecie_uwagi_i_bledy_tekstu(monkeypatch, tmp_path):
    atrapa = _LintAtrapa([_u(12, "komunikacjaod", "komunikacja od")] + [_u(3, "słowo%d" % i, "słowa", "srednia") for i in range(12)])
    monkeypatch.setitem(sys.modules, "lint_tekst", atrapa)
    uwagi = []
    wyn = pc._lint(_model_lint(), uwagi, str(tmp_path))
    assert len(wyn) == 13 and atrapa.wywolania[0][0] == (1, ["Raz  dwa\vtrzy", "komórka"])  # kolejne akapity, tekst surowy
    assert atrapa.wywolania[0][1] == (12, ["komunikacjaod anti-agingu"])
    assert uwagi[0] == "Możliwe błędy w tekście oryginału: 13 (program ich nie poprawia - popraw w pliku albo zleć AI)"
    assert uwagi[1] == "Slajd 12: „komunikacjaod” wygląda na sklejone słowa - może „komunikacja od”?"
    assert len(uwagi) == 1 + 1 + 10 + 1 and uwagi[-1].startswith("…i 2 innych")  # wysoka wszystkie, srednia do 10


def test_lint_brak_modulu_albo_wyjatek_nie_psuje_konwersji(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "lint_tekst", None)  # import -> ImportError
    uwagi = []
    assert pc._lint(_model_lint(), uwagi, str(tmp_path)) == [] and uwagi == []
    monkeypatch.setitem(sys.modules, "lint_tekst", _LintAtrapa(wyjatek=RuntimeError("zepsuty słownik")))
    assert pc._lint(_model_lint(), uwagi, str(tmp_path)) == [] and uwagi == []
    assert "zepsuty słownik" in (tmp_path / "lint.log").read_text(encoding="utf-8")  # wpis do logu


def test_lint_w_compose_klucz_bledy_tekstu_w_specu(monkeypatch, tmp_path):
    from pptx import Presentation
    from pptx.util import Inches
    prs = Presentation()
    for t in ("Pierwszy slajd z komunikacjaod tutaj", "Drugi slajd bez błędów"):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_textbox(Inches(1), Inches(2), Inches(6), Inches(1)).text_frame.text = t
    plik = str(tmp_path / "mini.pptx")
    prs.save(plik)
    atrapa = _LintAtrapa([_u(1, "komunikacjaod", "komunikacja od")])
    monkeypatch.setitem(sys.modules, "lint_tekst", atrapa)
    model = pc.extract(plik, str(tmp_path / "rob"))
    spec = pc.compose(model, {"wizualizacje": False, "wyjscie": str(tmp_path)})
    assert spec["bledy_tekstu"] == [_u(1, "komunikacjaod", "komunikacja od")]
    assert any(u.startswith("Możliwe błędy w tekście oryginału: 1") for u in spec["uwagi"])
    assert "komunikacjaod" in str(atrapa.wywolania[0][0])  # lint dostaje teksty ŹRÓDŁA; tekst slajdu nie jest poprawiany
    assert any("komunikacjaod" in str(sl) for sl in spec["slides"])


def test_poprawka_w_granicach_przyjete_i_odrzucone():
    for a, b in (("komunikacjaod", "komunikacja od"), ("o węglowodanów", "od węglowodanów"), ("do zbudowanie", "do zbudowania"),
                 ("Kluczowe kierunku", "Kluczowe kierunki"), ("Starzejąca się społeczeństwo", "Starzejące się społeczeństwo"),
                 ("na na smak", "na smak"), ("smak ,ale", "smak, ale"), ("a  b", "a b")):
        assert pc.poprawka_w_granicach(a, b), (a, b)
    for a, b in (("całe zdanie źródła tutaj", ""), ("7,8%", "7,9%"), ("Ala ma kota i psa", "Zupełnie inne zdanie tu"),
                 ("słowo", "słoiki"), ("kot", "koniec"), ("a b", "a b")):
        assert not pc.poprawka_w_granicach(a, b), (a, b)  # puste jest, zmiana cyfry, nowe zdanie, 3 znaki w słowie, bez zmiany


def _mini(tmp_path, nazwa, tekst):
    from pptx import Presentation
    from pptx.util import Inches
    prs = Presentation()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.shapes.add_textbox(Inches(1), Inches(2), Inches(6), Inches(1)).text_frame.text = tekst
    p = str(tmp_path / nazwa)
    prs.save(p)
    return p


def _kontrola(tmp_path, poprawki, tekst_wyniku="Ala ma komunikacja od kota"):
    zrodlo, wynik = _mini(tmp_path, "z.pptx", "Ala ma komunikacjaod kota"), _mini(tmp_path, "w.pptx", tekst_wyniku)
    model = pc.extract(zrodlo, str(tmp_path / "rob"))
    mapa = {"1": [0]}
    return pc.coverage(zrodlo, wynik, mapa, rob=str(tmp_path / "rob"), poprawki=poprawki), \
        pc.wiernosc(model, wynik, mapa, poprawki=poprawki)


def test_poprawki_deklaracja_przechodzi_bez_deklaracji_nie(tmp_path):
    p = [{"slajd": 1, "bylo": "komunikacjaod", "jest": "komunikacja od", "powod": "sklejone słowa"}]
    cov, wier = _kontrola(tmp_path, p)
    assert cov["procent"] == 100.0 and cov["brakuje"] == [] and wier["usterki"] == []
    assert [x["status"] for x in cov["poprawki"]] == ["przyjeta"] and [x["status"] for x in wier["poprawki"]] == ["przyjeta"]
    cov0, wier0 = _kontrola(tmp_path, None)  # ta sama zmiana bez deklaracji: nie przechodzi
    assert cov0["procent"] < 100.0 and cov0["brakuje"] and wier0["usterki"]


def test_poprawki_spoza_zrodla_i_poza_granicami_to_usterki_i_nie_sa_stosowane(tmp_path):
    cov, wier = _kontrola(tmp_path, [{"slajd": 1, "bylo": "tego nie ma", "jest": "tego nie ma 2", "powod": "x"}])
    assert [x["status"] for x in cov["poprawki"]] == ["nie_w_zrodle"]
    assert any("poprawka nie pasuje do oryginału" in u for u in wier["usterki"])
    # puste `jest` albo zamiana całego zdania = poza granicami: usterka i brak zastosowania (coverage nie wychodzi na 100 %)
    for jest in ("", "Zupełnie inne zdanie"):
        cov, wier = _kontrola(tmp_path, [{"slajd": 1, "bylo": "Ala ma komunikacjaod kota", "jest": jest, "powod": "x"}], tekst_wyniku=jest or "x y z")
        assert [x["status"] for x in cov["poprawki"]] == ["poza_granicami"]
        assert any(u.startswith("poprawka poza granicami (slajd 1:") for u in wier["usterki"])
        assert cov["procent"] < 100.0


def test_poprawki_duzo_przyjetych_to_ostrzezenie():
    rap = pc._raport_poprawek([{"slajd": 1, "bylo": "a%d" % i, "jest": "ab%d" % i, "powod": "x"} for i in range(16)],
                              [(["a%d" % i for i in range(16)], [])])
    assert all(x["status"] == "przyjeta" for x in rap) and pc._ostrzezenia_poprawek(rap) == ["dużo poprawek tekstu: 16 - sprawdź listę"]
    assert pc._ostrzezenia_poprawek(rap[:15]) == []


# --- 4d. samoocena układu, kandydaci, wybór wariantu, poprawka po renderze (pkt 9, 13.10) ----------------------------------------
class _FakeBD:
    """Atrapa build_dk dla `ocena`: układ podany wprost (miary jak z `uklad_layout`), bez pomiaru tekstu."""
    CB = 10000.0
    KONT_PT = {"p": 26, "b": 26, "lead": 40, "h": 36, "small": 16}

    def __init__(self, ms, f=1.0):
        self._ms, self._f = ms, f

    @staticmethod
    def cm(x):
        return x * 360.0

    def uklad_layout(self, sp):
        return self._ms, self._f

    def uklad_top(self, sp):
        return 1000.0


def _t(k, pt, linie):
    return ("txt", 0, 0, {"k": k, "pt": pt, "lines": linie, "font": "display" if k in ("lead", "h") else "body"})


def _karta_f(*czesci):
    return (list(czesci), 1000)


def _cols_m(karty, h=8000.0, chs=None, pad=100.0):
    return {"kind": "cols", "h": h, "cols": karty, "pad": pad, "tag_h": 0, "meta_h": 0, "gap": 0,
            "chs": chs or [h - 2 * pad] * len(karty), "hs": [h] * len(karty)}


def _ocena_f(karty, **kw):
    ms = [_cols_m(karty, **{k: v for k, v in kw.items() if k in ("h", "chs", "pad")})]
    sp = {"type": "uklad", "rows": [{"k": "cols"}]}
    return sz.ocena(sp, _FakeBD(ms))


def _kody(o):
    return [u["kod"] for u in o["usterki"]]


def _dobra(n=3):
    return [_karta_f(_t("lead", 24, ["Hasło jeden", "dwa trzy"]), _t("p", 16, ["Dopisek krótki tutaj", "jest."])) for _ in range(n)]


def test_ocena_dobry_slajd_bez_usterek_i_wyzsze_punkty_niz_zly():
    dobry = _ocena_f(_dobra())
    assert dobry["usterki"] == [] and dobry["punkty"] > 110 and dobry["miary"]["wypelnienie"] > 0.85
    zly = _ocena_f([_karta_f(_t("lead", 12, ["a", "b", "c", "d"]), _t("p", 10, ["x y"]))] * 3)
    assert zly["punkty"] < dobry["punkty"] - 20


def test_ocena_haslo_male_i_wyjatek_dla_5_6_kart():
    assert "HASLO_MALE" in _kody(_ocena_f(_dobra(3)[:2] + [_karta_f(_t("lead", 14, ["Hasło"]))]))
    pięć = [_karta_f(_t("lead", 14.5, ["Hasło jeden"])) for _ in range(5)]
    assert "HASLO_MALE" not in _kody(_ocena_f(pięć))  # rząd 5-6 kafli: 14 pt dopuszczalne
    assert "HASLO_MALE" in _kody(_ocena_f([_karta_f(_t("lead", 13, ["Hasło"])) for _ in range(5)]))


def test_ocena_dopisek_maly_i_haslo_mniejsze_od_dopisku():
    assert "DOPISEK_MALY" in _kody(_ocena_f([_karta_f(_t("lead", 24, ["Hasło"]), _t("p", 12, ["dopisek"]))] * 2))
    assert "DOPISEK_MALY" not in _kody(_ocena_f([_karta_f(_t("lead", 24, ["Hasło"]), _t("p", 13, ["dopisek"]))] * 2))
    assert "HASLO_MNIEJSZE" in _kody(_ocena_f([_karta_f(_t("lead", 18, ["Hasło"]), _t("p", 20, ["dopisek"]))] * 2))


def test_ocena_slowo_po_slowie_i_haslo_dlugie():
    o = _ocena_f([_karta_f(_t("lead", 24, ["Kreacja", "nowych", "segmentów", "oraz kategorii"]))] * 2)
    assert "SLOWO_PO_SLOWIE" in _kody(o)
    assert "SLOWO_PO_SLOWIE" not in _kody(_ocena_f([_karta_f(_t("lead", 24, ["Kreacja", "nowych", "segmentów oraz", "kategorii"]))] * 2))
    assert "HASLO_DLUGIE" in _kody(_ocena_f([_karta_f(_t("lead", 24, ["a b", "c d", "e f", "g h", "i j", "k l"]))] * 2))
    assert "HASLO_DLUGIE" not in _kody(_ocena_f([_karta_f(_t("lead", 24, ["a b", "c d", "e f", "g h", "i j"]))] * 2))


def test_ocena_pusty_dol_tylko_przy_pismie_ponizej_gornych_granic():
    maly = _ocena_f([_karta_f(_t("lead", 20, ["Hasło"]))] * 2, h=2500.0)
    assert "PUSTY_DOL" in _kody(maly) and maly["miary"]["wypelnienie"] < 0.35
    assert "PUSTY_DOL" not in _kody(_ocena_f([_karta_f(_t("lead", 40, ["Hasło"]))] * 2, h=2500.0))  # pismo już na górnej granicy
    assert "PUSTY_DOL" not in _kody(_ocena_f(_dobra()))


def test_ocena_nie_miesci_sie():
    o = sz.ocena({"type": "uklad", "rows": [{"k": "cols"}]}, type("B", (), {
        "uklad_layout": staticmethod(lambda sp: (None, None))})())
    assert _kody(o) == ["NIE_MIESCI_SIE"] and o["punkty"] == sz.PUNKTY_NIE_MIESCI
    # prawdziwy układ: dziesięć akapitów po 200 słów nie mieści się nawet najmniejszym pismem
    sp = {"type": "uklad", "title": "T", "rows": [{"k": "p", "t": " ".join(["słowo"] * 200) + "."} for _ in range(10)]}
    assert _kody(sz.ocena(sp, build_dk)) == ["NIE_MIESCI_SIE"]


def test_ocena_karta_pusta_i_karty_nierowne():
    karty = [_karta_f(_t("lead", 24, ["Hasło"])), _karta_f(_t("lead", 24, ["Hasło"]))]
    o = _ocena_f(karty, h=6000.0, chs=[500.0, 5500.0])
    assert "KARTA_PUSTA" in _kody(o) and "KARTY_NIEROWNE" in _kody(o)
    assert "KARTA_PUSTA" not in _kody(_ocena_f(karty, h=6000.0, chs=[3500.0, 5000.0]))
    assert "KARTY_NIEROWNE" not in _kody(_ocena_f(karty, h=6000.0, chs=[2500.0, 5000.0]))  # 2,0 x < 2,5 x
    assert "KARTA_PUSTA" not in _kody(_ocena_f(karty[:1], h=6000.0, chs=[500.0]))  # jedna karta w rzędzie: nie oceniamy


def test_ocena_za_duzo_lato_i_akapit_bez_hasla():
    lato = _karta_f(_t("lead", 24, ["Hasło dwa"]), _t("p", 16, ["x y z " * 2] * 6))
    assert "ZA_DUZO_LATO" in _kody(_ocena_f([lato, lato]))
    assert "ZA_DUZO_LATO" not in _kody(_ocena_f(_dobra()))  # mało słów Lato
    bez = _karta_f(_t("p", 16, ["linia jeden"] * 5))
    assert "AKAPIT_BEZ_HASLA" in _kody(_ocena_f([bez, bez]))
    assert "AKAPIT_BEZ_HASLA" not in _kody(_ocena_f([_karta_f(_t("lead", 24, ["Hasło"]), _t("p", 16, ["linia jeden"] * 5))] * 2))


def _kand(punkty, usterki=(), dop=True, nazwa="k"):
    return {"nazwa": nazwa, "dopuszczony": dop, "ocena": {"punkty": punkty, "miary": {}, "usterki": [{"kod": u, "opis": ""} for u in usterki]}}


def test_wybierz_domyslny_wygrywa_przy_lekkiej_przewadze_i_jest_deterministyczny():
    assert sz.wybierz([_kand(100), _kand(105), _kand(108)]) == 0  # przewaga <= PROG_REMISU: zostaje kolejność reguł
    assert sz.wybierz([_kand(80), _kand(112), _kand(113)]) == 1  # ciężka usterka domyślnego: pierwszy z równorzędnych najlepszych
    assert sz.wybierz([_kand(80), _kand(100), _kand(100)]) == 1  # remis punktów: niższy indeks
    assert sz.wybierz([_kand(120, dop=False), _kand(60, dop=False)]) is None  # żaden dopuszczony
    assert sz.wybierz([_kand(120, dop=False), _kand(100), _kand(100)]) == 1  # niedopuszczony nie bywa wybrany
    for _ in range(2):
        assert sz.wybierz([_kand(50), _kand(70), _kand(71), _kand(70)]) == 1


def test_kandydaci_te_same_slowa_domyslny_pierwszy_deterministyczni(monkeypatch, tmp_path_factory):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    karty = _cols(_it(_b("p", P31_1), _b("p", "Według PwC spożywają ok. 40% mniej kalorii, co daje koszyki mniejsze o 4–6%."),
                      _b("p", "Wydatki na słone przekąski spadły w tej grupie o 10,1%.")))
    sp = dict(_sp([karty]), max_f=1.6)
    k1 = sz.kandydaci(sp, 31, build_dk, pc._miesci)
    k2 = sz.kandydaci(sp, 31, build_dk, pc._miesci)
    assert len(k1) >= 3 and k1[0]["nazwa"] == "domyślny" and len({k["nazwa"] for k in k1}) == len(k1)
    assert all(sz.slowa(k["slajd"]) == sz.slowa(k1[0]["slajd"]) for k in k1)  # żaden kandydat nie gubi ani nie dodaje słów
    assert sz.opis_wariantow(k1, sz.wybierz(k1)) == sz.opis_wariantow(k2, sz.wybierz(k2))  # ten sam wynik w 2 przebiegach
    assert sum(1 for x in sz.opis_wariantow(k1, sz.wybierz(k1)) if x["wybrany"]) == 1
    assert all(isinstance(k["ocena"]["punkty"], float) for k in k1)
    assert sz.kandydaci(_sp([{"k": "p", "t": "Zwykły krótki akapit bez wzorca."}]), 1, build_dk) == []  # nic do szablonowania


def test_kandydaci_osie_siatka_rzad_i_siatka_zmieniaja_uklad_kafli(monkeypatch):
    monkeypatch.setattr(sz, "_IK", IK_TEST)
    sp = dict(_sp([{"k": "chips", "items": ["Długowieczność", "Wysoka sprawność", "Atrakcyjność", "Większe funkcje"], "per_row": 2}]),
              max_f=1.25)
    k = sz.kandydaci(sp, 9, build_dk, pc._miesci)
    uklady = {x["nazwa"]: [len(r["items"]) for r in x["slajd"]["rows"] if r["k"] == "cols"] for x in k}
    assert uklady["domyślny"] == [2, 2] and uklady["kafle: rząd"] == [4]  # 2 x 2 -> jeden rząd (oś `siatka`)


def _spec_wariantow():
    sl = lambda *rows: {"type": "uklad", "zrodlo": 5, "title": "T", "rows": list(rows)}  # noqa: E731
    s_a = sl({"k": "p", "t": "jeden dwa trzy"})
    s_b = sl({"k": "lead", "t": "jeden dwa"}, {"k": "p", "t": "trzy"})
    s_c = sl({"k": "h", "t": "jeden dwa trzy"})
    s_d = sl({"k": "lead", "t": "jeden"}, {"k": "p", "t": "dwa trzy"})
    spec = {"slides": [{"type": "cover", "zrodlo": 1}, s_a]}
    k = lambda n, p, u, w, g, sl_, dop=True: {"nazwa": n, "opcje": {}, "punkty": p, "miary": {"wypelnienie": w, "gestosc": g},  # noqa: E731
                                              "usterki": [{"kod": x, "opis": ""} for x in u], "dopuszczony": dop, "slajd": sl_}
    rek = {"zrodlo": 5, "czesc": 0, "wybrany": 0, "kandydaci": [
        k("A", 100, ["PUSTY_DOL"], 0.4, 5.0, s_a), k("B", 98, [], 0.7, 4.0, s_b), k("C", 60, [], 0.9, 3.0, s_c),
        k("D", 99, ["KARTA_PUSTA"], 0.9, 8.0, s_d)]}
    return spec, {"wersja": 1, "slajdy": [rek]}, rek


def test_inny_wariant_podmienia_slajd_bez_gubienia_slow_i_respektuje_kody():
    spec, war, rek = _spec_wariantow()
    przed = sz.slowa(spec["slides"][1])
    assert sz.inny_wariant(spec, 2, ["KARTA_PUSTA"], war) is True  # B: bez KARTA_PUSTA, 98 >= 100 - tolerancja
    assert spec["slides"][1]["rows"][0]["k"] == "lead" and rek["wybrany"] == 1
    assert sz.slowa(spec["slides"][1]) == przed  # zestaw słów identyczny przed / po
    assert spec["poprawki_ukladu"] == [{"slajd": 2, "kody": ["KARTA_PUSTA"], "bylo": "A", "jest": "B"}]
    # obecny = B; PUSTY_DOL ma A (odpada), C jest poza tolerancją punktów (60), D (99, KARTA_PUSTA) nie ma PUSTY_DOL -> D
    assert sz.inny_wariant(spec, 2, ["PUSTY_DOL"], war) is True and rek["wybrany"] == 3
    assert sz.slowa(spec["slides"][1]) == przed
    # obecny = D; kody KARTA_PUSTA wykluczają D; A ma PUSTY_DOL (nie ma KARTA_PUSTA) i 100 pkt -> A (wraca do wyższych punktów)
    assert sz.inny_wariant(spec, 2, ["KARTA_PUSTA"], war) is True and rek["wybrany"] == 0


def test_inny_wariant_false_gdy_brak_lepszego_kandydata_albo_rekordu():
    spec, war, rek = _spec_wariantow()
    assert sz.inny_wariant(spec, 2, ["PUSTY_DOL", "KARTA_PUSTA"], war) is True  # B ma obie bez usterek
    assert sz.inny_wariant(spec, 2, ["PUSTY_DOL", "KARTA_PUSTA", "KARTY_NIEROWNE"], {"wersja": 1, "slajdy": [dict(
        rek, kandydaci=rek["kandydaci"][:2], wybrany=1)]}) is False  # został tylko obecny i A (PUSTY_DOL)
    assert sz.inny_wariant(spec, 1, ["PUSTY_DOL"], war) is False  # slajd 1 (okładka) nie ma rekordu
    assert sz.inny_wariant(spec, 99, ["PUSTY_DOL"], war) is False
    assert sz.inny_wariant(spec, 2, ["PUSTY_DOL"], None) is False  # brak wariantów
    s2, w2, r2 = _spec_wariantow()
    r2["kandydaci"] = r2["kandydaci"][:1]
    assert sz.inny_wariant(s2, 2, ["PUSTY_DOL"], w2) is False  # jeden kandydat


def test_inny_wariant_kody_po_renderze_wymagaja_zmiany_miary_w_dobra_strone():
    spec, war, rek = _spec_wariantow()
    rek["wybrany"] = 2  # obecny C: wypełnienie 0,9, gęstość 3,0
    spec["slides"][1] = dict(rek["kandydaci"][2]["slajd"])
    for k in rek["kandydaci"]:
        if k["nazwa"] != "C":
            k["miary"]["wypelnienie"] = 0.95  # pozostali mają większe wypełnienie i większą gęstość niż C
    assert sz.inny_wariant(spec, 2, ["GESTO"], war) is False  # żaden kandydat nie jest luźniejszy niż C
    spec, war, rek = _spec_wariantow()
    assert sz.inny_wariant(spec, 2, ["GESTO"], war) is True and rek["wybrany"] == 1  # A (5,0) -> B (4,0): mniej gęsto
    spec, war, rek = _spec_wariantow()
    assert sz.inny_wariant(spec, 2, ["MALO_TRESCI"], war) is True and rek["wybrany"] == 3  # A (0,4) -> D (0,9, 99 pkt): więcej treści, wyżej punktowany niż B


def test_popraw_po_renderze_zapisuje_spec_i_plik_wariantow(tmp_path):
    import json
    spec, war, rek = _spec_wariantow()
    sp_path, w_path = tmp_path / "spec_konwersja.json", tmp_path / "warianty-szablon.json"
    spec["warianty_plik"], spec["uwagi"] = "warianty-szablon.json", []
    sp_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    w_path.write_text(json.dumps(war, ensure_ascii=False), encoding="utf-8")
    assert pc.popraw_po_renderze(str(sp_path), {"2": ["KARTA_PUSTA"]}) == [2]  # klucze tekstowe też są przyjmowane
    nowy = json.loads(sp_path.read_text(encoding="utf-8"))
    assert nowy["slides"][1]["rows"][0]["k"] == "lead" and nowy["poprawki_ukladu"][0]["jest"] == "B"
    assert any(u.startswith("Po obejrzeniu zrzutów poprawiłem układ slajdów: 2") for u in nowy["uwagi"])
    assert json.loads(w_path.read_text(encoding="utf-8"))["slajdy"][0]["wybrany"] == 1
    assert pc.popraw_po_renderze(str(sp_path), {3: ["PUSTY_DOL"]}) == []  # slajd bez rekordu
    w_path.unlink()
    nowy["warianty_plik"] = "nie-ma.json"
    sp_path.write_text(json.dumps(nowy), encoding="utf-8")
    assert pc.popraw_po_renderze(str(sp_path), {2: ["PUSTY_DOL"]}) == []  # brak pliku wariantów: nic się nie zmienia


def _petla_srodowisko(tmp_path, monkeypatch, oko_per_budowa):
    """Atrapa pętli oka: `oko_per_budowa[k]` = {nr: [(kod, waga), ...]} dla zrzutów po k-tej budowie (k = 0: przed pierwszą zmianą)."""
    import json
    spec, war, rek = _spec_wariantow()
    spec["warianty_plik"], spec["uwagi"] = "warianty-szablon.json", []
    (tmp_path / "spec_konwersja.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "warianty-szablon.json").write_text(json.dumps(war, ensure_ascii=False), encoding="utf-8")
    budowy = []

    def katalog(png, sp):
        dane = oko_per_budowa[min(len(budowy), len(oko_per_budowa) - 1)]
        return {nr: [{"kod": k, "waga": w} for k, w in us] for nr, us in dane.items()}
    monkeypatch.setattr(pc, "_oko_katalog", katalog)

    class Szybka:
        @staticmethod
        def build_and_qa(sp, rob):
            budowy.append(json.loads(open(sp, encoding="utf-8").read())["slides"][1]["rows"][0]["k"])
            return str(tmp_path / ("w%d.pptx" % len(budowy)))
    return str(tmp_path / "spec_konwersja.json"), Szybka, budowy


def test_petla_oka_zostawia_wariant_gdy_slajd_ma_mniej_usterek_wagi_2(tmp_path, monkeypatch):
    import json
    sp, Szybka, budowy = _petla_srodowisko(tmp_path, monkeypatch, [
        {2: [("KARTA_PUSTA", 3), ("GESTO", 1)]},  # przed: jedna usterka wagi 3 (waga 1 się nie liczy)
        {2: [("GESTO", 1)]}])  # po: zero usterek wagi >= 2
    pptx, zm = pc._petla_oka(sp, str(tmp_path), str(tmp_path / "w0.pptx"), Szybka)
    assert zm == [2] and budowy == ["lead"] and pptx.endswith("w1.pptx")  # jedna budowa, bez cofania, kolejna runda bez usterek
    nowy = json.loads(open(sp, encoding="utf-8").read())
    assert nowy["slides"][1]["rows"][0]["k"] == "lead" and nowy["poprawki_ukladu"][0]["jest"] == "B"


def test_petla_oka_cofa_wariant_gdy_nie_ma_mniej_usterek_i_nie_ponawia(tmp_path, monkeypatch):
    import json
    sp, Szybka, budowy = _petla_srodowisko(tmp_path, monkeypatch, [
        {2: [("KARTA_PUSTA", 2)]},  # przed
        {2: [("PUSTY_DOL", 2)]},  # po zmianie na B: nadal jedna usterka wagi 2 -> cofamy (nie ma poprawy)
        {2: [("KARTA_PUSTA", 2)]}])  # po cofnięciu: jak przed; slajd 2 jest już odrzucony i drugi raz nie jest ruszany
    pptx, zm = pc._petla_oka(sp, str(tmp_path), str(tmp_path / "w0.pptx"), Szybka)
    assert zm == [] and budowy == ["lead", "p"] and pptx.endswith("w2.pptx")  # budowa B, cofnięcie = budowa A, koniec
    nowy = json.loads(open(sp, encoding="utf-8").read())
    assert nowy["slides"][1]["rows"][0]["k"] == "p" and nowy.get("poprawki_ukladu", []) == []
    assert json.loads((tmp_path / "warianty-szablon.json").read_text(encoding="utf-8"))["slajdy"][0]["wybrany"] == 0
    assert any("zostawiłem poprzedni" in u for u in nowy["uwagi"]) and not any("poprawiłem układ slajdów" in u for u in nowy["uwagi"])


def test_petla_oka_waga_1_nie_uruchamia_zmiany_i_brak_zrzutu_po_budowie_cofa(tmp_path, monkeypatch):
    sp, Szybka, budowy = _petla_srodowisko(tmp_path, monkeypatch, [{2: [("PUSTY_DOL", 1)]}])
    assert pc._petla_oka(sp, str(tmp_path), "x.pptx", Szybka) == ("x.pptx", []) and budowy == []  # tylko waga 1: bez zmian
    sp, Szybka, budowy = _petla_srodowisko(tmp_path, monkeypatch, [{2: [("KARTA_PUSTA", 3)]}, {}])
    pptx, zm = pc._petla_oka(sp, str(tmp_path), "x.pptx", Szybka)
    assert zm == [] and budowy == ["lead", "p"]  # po budowie brak zrzutu slajdu 2 = nie da się zweryfikować -> cofnięcie


def test_kody_z_oka_atrapa_i_brak_modulu(monkeypatch):
    class Oko:
        @staticmethod
        def ocen_katalog(png, spec):
            return {1: {"usterki": []}, 3: {"usterki": [{"kod": "PUSTY_DOL", "waga": 3}, {"kod": "GESTO", "waga": 1}]}}
    monkeypatch.setitem(sys.modules, "oko", Oko)
    assert pc._kody_z_oka("png", "spec.json") == {3: ["PUSTY_DOL", "GESTO"]}
    assert pc._kody_z_oka("png", "spec.json", min_waga=2) == {3: ["PUSTY_DOL"]}
    assert pc._oko_katalog("png", "spec.json")[1] == []  # slajd bez usterek też jest w katalogu (dowód, że zrzut istnieje)
    monkeypatch.setitem(sys.modules, "oko", None)
    assert pc._kody_z_oka("png", "spec.json") == {} and pc._oko_katalog("png", "spec.json") == {}


def test_compose_zapisuje_warianty_i_decyzje_wyboru(tmp_path_factory):
    import json
    model, spec, _cov, _wier = _zbuduj_szablon("co_dalej", tmp_path_factory)
    plik = os.path.join(model["rob"], pc.WARIANTY_PLIK)
    assert os.path.isfile(plik) and spec["warianty_plik"] == pc.WARIANTY_PLIK
    war = json.load(open(plik, encoding="utf-8"))
    assert len(war["slajdy"]) >= 25 and all(0 <= r["wybrany"] < len(r["kandydaci"]) for r in war["slajdy"])
    assert all(r["kandydaci"][r["wybrany"]]["dopuszczony"] for r in war["slajdy"])
    wyb = [d for d in spec["szablon"] if d["wzorzec"] == "wybor-wariantu"]
    assert len(wyb) == len(war["slajdy"])
    assert all(sum(1 for w in d["warianty"] if w["wybrany"]) == 1 and {"nazwa", "punkty", "usterki"} <= set(d["warianty"][0]) for d in wyb)
    # spec w pamięci ma te same rekordy co plik (program dumpuje spec sam: inny_wariant działa na `spec["warianty"]`)
    assert len(spec["warianty"]["slajdy"]) == len(war["slajdy"])


# --- 5. tabela regresji (4 prezentacje z zadania; bez PowerPointa i modeli AI): pytest test_konwersja.py -k tabela -s -
REG = os.environ.get("DK_TEST_REG") or os.path.join(tempfile.gettempdir(), "dk-prezentacje-regresja")  # katalog roboczy testu
REG_PLIKI = {
    "co_dalej": PLIKI["co_dalej"],
    "onlien": PLIKI["onlien"],
    "DATESY": PLIKI["datesy"],
    "KULKI_stary": os.path.join(PREZ, "24.09.2026 - KULKI z kreatyną", "KULKI z kreatyną - stary styl.pptx"),
}
_GOLE = ("lead", "h", "p")


def _gola(sp):
    return sp["type"] == "uklad" and bool(sp.get("rows")) and all(r["k"] in _GOLE and not r.get("li") for r in sp["rows"])


@pytest.mark.parametrize("nazwa", sorted(REG_PLIKI))
def test_tabela_regresji(nazwa):
    plik = REG_PLIKI[nazwa]
    if not os.path.isfile(plik):
        pytest.skip("brak pliku %s" % plik)
    rob = os.path.join(REG, nazwa)
    os.makedirs(rob, exist_ok=True)
    model = pc.extract(plik, rob)
    spec = pc.compose(model, {"wizualizacje": False, "wyjscie": rob})
    build_dk.build(spec, os.path.join(rob, "wynik.pptx"))
    pptx = build_dk.build.last_out
    cov = pc.coverage(plik, pptx, spec["mapa"], rob=rob)
    wier = pc.wiernosc(model, pptx, spec["mapa"])
    sl = spec["slides"]
    uk = [s for s in sl if s["type"] == "uklad"]
    typy = collections.Counter(s["type"] for s in sl)
    gole = sum(_gola(s) for s in uk)
    wiersze = collections.Counter(r["k"] for s in uk for r in s.get("rows", []))
    wiersz = "%s | slajdy %d->%d | tresc %s | wiernosc usterek %d, znaki %d | uklad %d, szablon %d, gole %d (%.0f%% ukladow) | %s" % (
        nazwa, len(model["slajdy"]), len(sl), "brakuje %d" % len(cov["brakuje"]), len(wier["usterki"]),
        len(wier.get("znaki", [])), len(uk), len(sl) - len(uk), gole, 100.0 * gole / max(1, len(uk)),
        dict(typy))
    with open(os.path.join(REG, "tabela.txt"), "a", encoding="utf-8") as f:
        f.write(wiersz + "\n  wiersze: %s\n  usterki: %s\n" % (dict(wiersze), wier["usterki"][:10]))
    print(wiersz)
    assert cov["brakuje"] == [], cov["brakuje"][:5]
    assert wier["usterki"] == [] or len(wier["usterki"]) <= USTERKI_PRZED.get(nazwa, 0), wier["usterki"][:5]
    assert wier.get("znaki", []) == [], wier["znaki"][:5]
    if nazwa != "onlien":  # onlien (instrukcja szablonu) dzieli dlugie slajdy od 06.10
        assert len(sl) == len(model["slajdy"])


class _FakeBDH(_FakeBD):
    H = 10000.0  # wysokość slajdu: `ocena` liczy z niej PLYWAJACA_TRESC


def test_ocena_plywajaca_tresc_maly_blok_w_pustym_polu():
    # CB 10000, górę pola daje uklad_top 1000 -> avail 9000; blok 2000 wyśrodkowany: pasy po 3500 (35% wysokości) i dół
    sp = {"type": "uklad", "rows": [{"k": "cols"}]}
    ms = [_cols_m([_karta_f(_t("lead", 40, ["Hasło"]))] * 2, h=2000.0)]
    o = sz.ocena(sp, _FakeBDH(ms))
    assert "PLYWAJACA_TRESC" in _kody(o) and "PLYWAJACA_TRESC" in sz.KODY_WIECEJ_TRESCI
    assert "PLYWAJACA_TRESC" not in _kody(sz.ocena(sp, _FakeBD(ms)))  # atrapa bez wysokości slajdu: kod się nie liczy
    sp_t = dict(sp, valign="t")  # treść od góry: nie „pływa”
    assert "PLYWAJACA_TRESC" not in _kody(sz.ocena(sp_t, _FakeBDH(ms)))
    duzy = [_cols_m([_karta_f(_t("lead", 40, ["Hasło"]))] * 2, h=6000.0)]
    assert "PLYWAJACA_TRESC" not in _kody(sz.ocena(sp, _FakeBDH(duzy)))  # treść > 50% wysokości


def test_inny_wariant_po_renderze_zmienia_tylko_wyglad_nie_podzial_tresci():
    spec, war, rek = _spec_wariantow()
    rek["kandydaci"][1]["opcje"] = {"zdania": "li"}  # B zmienia podział treści (oś zdania) - po renderze go nie wolno wybrać
    assert sz.inny_wariant(spec, 2, ["KARTA_PUSTA"], war) is False
    assert rek["wybrany"] == 0
    rek["kandydaci"][1]["opcje"] = {"pad": 0.75, "ikony": False}  # wygląd - wolno
    assert sz.inny_wariant(spec, 2, ["KARTA_PUSTA"], war) is True and rek["wybrany"] == 1


def test_przelotka_polecenia_cele_i_polecenie_ai_biora_tresc_z_polecenia_py(monkeypatch):
    import polecenia
    dane = {"cel_slajdy": 10, "widoczne": 20, "wszystkie": 25}
    for cel in ("wiernie", "rozwin", "skroc"):
        assert pc.polecenie_ai(cel, dane) == polecenia.polecenie_ai(cel, dane, pliki=True)
        assert pc.CELE[cel]["opis"] == polecenia.POLECENIA[cel]["opis"]  # opis i polecenie z polecenia.py
        assert pc.CELE[cel]["nazwa"] and "sufiks" in pc.CELE[cel]  # nazwa i sufiks zostają w pptx_convert
    assert pc.polecenie_ai("cokolwiek") == pc.polecenie_ai("wiernie")
    assert "około 10 slajdów" in "\n".join(pc.polecenie_ai("skroc", dane))
    monkeypatch.setitem(sys.modules, "polecenia", None)  # brak modułu: stare teksty z CELE (zapas)
    assert any("%(cel_slajdy)s" not in p and "około 10 slajdów" in p for p in pc.polecenie_ai("skroc", dane))
