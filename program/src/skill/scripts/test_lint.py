# -*- coding: utf-8 -*-
"""Testy lint_tekst.py (ostrzezenia o ewidentnych bledach tekstu slajdow).

    python -m pytest -p no:cacheprovider test_lint.py -q

Czesc 1 - jednostkowe (bez plikow). Czesc 2 - prawdziwe prezentacje (pomijane, gdy pliku nie ma na komputerze).
Nie uruchamiaja PowerPointa ani modeli AI.
"""
import os
import sys
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_tekst as L  # noqa: E402


def lint(*teksty, nr=1):
    return L.sprawdz([(nr, list(teksty))])


def rodzaje(uw, rodzaj=None):
    return [(u["rodzaj"], u["jest"], u["propozycja"], u["pewnosc"]) for u in uw if rodzaj in (None, u["rodzaj"])]


def cisza(*teksty):
    assert lint(*teksty) == [], lint(*teksty)


# --- sklejone ---------------------------------------------------------------------------------------------------
def test_sklejone_komunikacjaod():
    uw = lint("Kategoria > 500 zł. komunikacjaod anti-agingu do prewencji", nr=12)
    assert len(uw) == 1
    u = uw[0]
    assert (u["slajd"], u["rodzaj"], u["jest"], u["propozycja"], u["pewnosc"]) == \
           (12, "sklejone", "komunikacjaod", "komunikacja od", "wysoka")
    assert "komunikacjaod anti-agingu" in u["kontekst"]
    assert L.opis(u) == "Slajd 12: „komunikacjaod” wygląda na sklejone słowa - może „komunikacja od”?"


def test_sklejone_przyimek_na_poczatku_i_wersaliki():
    assert rodzaje(lint("Produkt dlaklientów sklepów"), "sklejone")[0][2:] == ("dla klientów", "wysoka")
    assert rodzaje(lint("KOMUNIKACJAOD ANTI-AGINGU DO PREWENCJI"), "sklejone")[0][2] == "KOMUNIKACJA OD"


def test_sklejone_bez_falszywych_alarmow():
    cisza("Dostępny w sklepach, doskonały smak. Podnagłówek bezglutenowy; zawartość białka.")
    cisza("Mamy produkty nadające się do jedzenia przed treningiem oraz po nim")
    cisza("Wysokobłonnikowymi przekąskami karmimy seniorów")  # rzadkie, ale poprawne zlozenie


# --- literowka --------------------------------------------------------------------------------------------------
def test_literowka_trafienia():
    assert rodzaje(lint("Kamapania do influencerów"), "literowka") == [("literowka", "Kamapania", "Kampania", "srednia")]
    assert rodzaje(lint("Wyniki kampanii z twócami"), "literowka")[0][2] == "twórcami"
    assert rodzaje(lint("Skill obowiazkowy dla zadania"), "literowka")[0][2] == "obowiązkowy"  # brak ogonkow


def test_literowka_bez_falszywych_alarmow():
    cisza("Mcdonaldsem sie nie przejmujemy")  # nazwa wlasna, sentencja bez ogonkow w poprawnych slowach
    cisza("Rośnie udział GLP-1 oraz Gen Z w zakupach")
    cisza("Trend well-beingu i longevity wśród millenialsów")
    cisza("Kupił Euromonitor raport od Mintel oraz Black Swan Data")  # nazwy wlasne w srodku zdania
    cisza("Protein snack, matcha shot i clean label dla fit lifestyle")  # biala lista


def test_literowka_slowo_powtarzane_to_celowe():
    assert lint("Kamapania do influencerów", "Kamapania dla marki") == []  # 2 x w prezentacji = autor tak pisze


def test_literowka_zdanie_obce_pomijane():
    cisza("brands grow through constant exposure and the best simulators")


# --- powtorzenie ------------------------------------------------------------------------------------------------
def test_powtorzenie():
    assert rodzaje(lint("Dobry produkt na na rynek"), "powtorzenie") == [("powtorzenie", "na na", "na", "wysoka")]
    assert L.opis(lint("Dobry produkt na na rynek")[0]).startswith("Slajd 1: powtórzone słowo „na na”")


def test_powtorzenie_bez_falszywych_alarmow():
    cisza("To jest bardzo bardzo dobre, a nie nie wiem; tak tak, ha ha")
    cisza("Produkt\nProdukt")  # dwa akapity, nie ciag
    cisza("Zdrowie, zdrowie i jeszcze raz zdrowie")  # przecinek rozdziela


# --- interpunkcja / spacje --------------------------------------------------------------------------------------
def test_interpunkcja_trafienia():
    assert rodzaje(lint("Dobry smak,ale drogi"), "interpunkcja") == [("interpunkcja", "smak,ale", "smak, ale", "wysoka")]
    assert rodzaje(lint("Koniec zdania.Nowe zdanie"), "interpunkcja")[0][2] == "zdania. Nowe"
    assert rodzaje(lint("Dobre , bo tanie"), "interpunkcja")[0][2] == "Dobre,"
    assert rodzaje(lint("Tak to było ."), "interpunkcja")[0][2] == "było."
    assert rodzaje(lint("A konkurencja nam odjechała.."), "interpunkcja")[0][2:] == ("odjechała…", "wysoka")


def test_interpunkcja_bez_falszywych_alarmow():
    cisza("Zobacz ok. 5 kg, m.in. białko; np. 1,2 g/kg dziennie, tzn. dużo.")
    cisza("Dla 65+ i seniorów: 1,2 g/kg masy ciała (NCEŻ).")
    cisza("Pisz na www.dobrakaloria.pl lub biuro@dobrakaloria.pl, a my odpiszemy...")
    cisza("Spółka S.A. oraz Sp. z o.o. działa od 2015 r. w Polsce… i dalej")
    cisza("Kody PL,EN,DE obowiązują; wersja 2.0 i 3,5 punktu")


def test_spacje():
    assert rodzaje(lint("Dobry  smak"), "spacje") == [("spacje", "Dobry  smak", "Dobry smak", "srednia")]
    cisza("Dobry smak")


# --- nawias -----------------------------------------------------------------------------------------------------
def test_nawias():
    assert rodzaje(lint("Dobry smak (zdrowie i uroda"), "nawias")[0][1] == "("
    assert rodzaje(lint("Cytat: „Dobry smak"), "nawias")[0][1] == "„"
    assert rodzaje(lint("Dobry smak i zdrowie)"), "nawias")[0][1] == ")"


def test_nawias_bez_falszywych_alarmow():
    cisza("Dobry smak (zdrowie)", "Cytat: „Dobry smak”")
    cisza("Zwiń: (Ctrl+C, Ctrl+V w", "tym oknie)")  # zawiniety wiersz: nawias zamyka sie w innym kawalku tego slajdu
    cisza("1) pierwsze", "2) drugie", "a) trzecie")  # numeracja
    cisza("Super :) i tak :(")
    cisza("„", "Opinia klienta o produkcie")  # samotny duzy cudzyslow-ozdoba
    cisza('Odsłuchaj podcastu "Diary', 'of CEO": kreatyna')


# --- opis / kontrakt --------------------------------------------------------------------------------------------
def test_kontrakt_pol_i_opisy():
    for tekst in ("komunikacjaod anti-agingu", "Kamapania do ludzi", "na na", "smak,ale", "smak  ale", "(smak"):
        for u in lint("Zdanie testowe " + tekst + " koniec"):
            assert set(u) == {"slajd", "rodzaj", "jest", "propozycja", "kontekst", "pewnosc"}
            assert u["pewnosc"] in ("wysoka", "srednia")
            assert u["rodzaj"] in ("sklejone", "literowka", "powtorzenie", "interpunkcja", "spacje", "nawias")
            assert L.opis(u).startswith("Slajd 1: ")


def test_puste_wejscie():
    assert L.sprawdz([]) == []
    assert L.sprawdz([(1, []), (2, ["", "   "])]) == []


def test_slownik_rozmiar_i_licencja():
    d = os.path.join(HERE, "..", "assets", "slownik")
    ile = sum(os.path.getsize(os.path.join(d, f)) for f in ("czeste.xz", "forms.bloom"))
    assert ile < 3 * 1024 * 1024
    assert os.path.exists(os.path.join(d, "LICENCJA.txt"))


def test_czas_60_slajdow():
    tekst = ["Żelki funkcjonalne to najszybciej rosnący format, szczególnie wśród seniorów i sportowców, dlatego",
             "komunikacja od anti-agingu do prewencji i longevity: białko 1,2 g/kg dziennie, ok. 30 g (NCEŻ).",
             "Kategoria rośnie szybciej niż rynek, a konkurencja nam odjechała. Pora na zmianę podejścia do marki."] * 8
    slajdy = [(n, list(tekst)) for n in range(1, 61)]
    t = time.time()
    L.sprawdz(slajdy)
    assert time.time() - t < 1.0


# --- prawdziwe prezentacje --------------------------------------------------------------------------------------
PREZ = r"D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE"
PLIKI = {
    "strategia": os.path.join(PREZ, "06.10.2026 - strategia", "DK_co_dalej_update.pptx"),
    "onlien": os.path.join(PREZ, "onlien.pptx"),
    "datesy": os.path.join(PREZ, "DATESY", "DOBRA KALORIA - DATESY.pptx"),
    "kulki": os.path.join(PREZ, "24.09.2026 - KULKI z kreatyną", "KULKI z kreatyną - stary styl.pptx"),
}
# oczekiwane ostrzezenia o pewnosci `wysoka` (wszystko inne wysokiego = falszywy alarm)
WYSOKA = {"strategia": {"komunikacjaod", "odjechała.."}, "onlien": set(), "datesy": set(), "kulki": set()}


def _teksty(plik, rob):
    import pptx_convert as pc
    m = pc.extract(plik, str(rob))
    return [(s["n"], [p["t"] for b in s["texts"] for p in b["paras"]] + [c for tb in s["tables"] for r in tb["rows"] for c in r])
            for s in m["slajdy"]]


@pytest.mark.parametrize("nazwa", list(PLIKI))
def test_prawdziwe_prezentacje(nazwa, tmp_path):
    if not os.path.exists(PLIKI[nazwa]):
        pytest.skip("brak pliku na tym komputerze")
    uw = L.sprawdz(_teksty(PLIKI[nazwa], tmp_path))
    assert {u["jest"] for u in uw if u["pewnosc"] == "wysoka"} == WYSOKA[nazwa], rodzaje(uw)
    assert sum(1 for u in uw if u["pewnosc"] == "srednia") <= 3  # zapas: do 1 falszywego na 10 slajdow
