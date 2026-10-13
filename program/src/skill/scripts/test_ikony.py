# -*- coding: utf-8 -*-
"""Testy ikon marki „W stylu DK” (build_dk.icon + słownik ikony-slowa.json). Bez PowerPointa, bez sieci.

    python -m pytest -p no:cacheprovider test_ikony.py -q
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_dk  # noqa: E402

DK = os.path.join(HERE, "..", "assets", "icons", "dk")
SLOWNIK = os.path.join(HERE, "..", "assets", "ikony-slowa.json")


def _kryjace(path):
    """RGB pikseli prawie nieprzezroczystych (alfa > 200)."""
    b = Image.open(path).convert("RGBA").tobytes()
    return {tuple(b[i:i + 3]) for i in range(0, len(b), 4) if b[i + 3] > 200}


def _nazwy_slownika():
    d = json.load(open(SLOWNIK, encoding="utf-8"))
    return d, set(d["rdzenie"].values()) | set(d["slowa"].values())


def test_zestaw_dk_pelny():
    assert len([f for f in os.listdir(DK) if f.endswith(".png")]) >= 1000
    im = Image.open(os.path.join(DK, "activity.png"))
    assert im.size == (256, 256) and im.mode == "RGBA"


def test_slownik_450_rdzeni_i_kazda_nazwa_istnieje_w_dk():
    d, nazwy = _nazwy_slownika()
    assert len(d["rdzenie"]) >= 450
    assert all(os.path.exists(os.path.join(DK, n + ".png")) for n in nazwy), sorted(
        n for n in nazwy if not os.path.exists(os.path.join(DK, n + ".png")))
    assert all(k == k.strip() and " " not in k for k in list(d["rdzenie"]) + list(d["slowa"]))


def test_slownik_trafia_bez_wieloznacznosci():
    import szablonuj as sz
    assert sz.ikona_dla("Trend na białko jest powrotem do piramidy") == "biceps-flexed"
    assert sz.ikona_dla("Tkanka tłuszczowa nie oznacza sprawnych mięśni") == "droplet"
    assert sz.ikona_dla("Odsetek nastolatków z otyłością wzrósł") == "weight-tilde"
    assert sz.ikona_dla("Przekąska jako część make-upu") == "sparkle"
    assert sz.ikona_dla("Dobra Kaloria") is None  # nazwa marki nie jest ikoną
    assert sz.ikona_dla("zupełnie bez trafienia xyz") is None


def test_aliasy_wskazuja_istniejace_ikony():
    assert all(os.path.exists(os.path.join(DK, v + ".png")) for v in build_dk.IKONA_ALIAS.values())
    assert build_dk.ikona_jest("leaf") and build_dk.ikona_jest("activity") and not build_dk.ikona_jest("nie-ma-takiej")


def test_icon_cztery_kolory_i_biel_jest_biala():
    for hexc in ("006400", "0F763E", "FFFFFF", "AD8767"):
        p = build_dk._ikona_dk("activity", hexc)
        assert p and os.path.exists(p), hexc
        assert _kryjace(p) == {tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4))}, hexc
    old = dict(build_dk.T)
    try:
        build_dk.T.update(brand="0F763E")
        assert os.path.exists(build_dk.icon("activity")) and os.path.exists(build_dk.icon("activity", True))
        assert build_dk.icon("activity", True) != build_dk.icon("activity")
        assert _kryjace(build_dk.icon("activity", True)) == {(255, 255, 255)}
    finally:
        build_dk.T.clear()
        build_dk.T.update(old)


def test_brak_ikony_zapas_bez_wyjatku(capsys):
    p = build_dk.icon("nie-ma-takiej-ikony")  # ścieżka do (nieistniejącego) zapasu Lucide, bez wyjątku
    assert not os.path.exists(p)
    q = build_dk._ikona("nie-ma-takiej-ikony", False)  # builder: `leaf` + ostrzeżenie na stderr
    assert os.path.exists(q) and "UWAGA" in capsys.readouterr().err
    assert os.path.exists(build_dk.white_icon("activity"))


def test_pamiec_podreczna_gdy_katalog_niedostepny(tmp_path, monkeypatch):
    blok = tmp_path / "plik"
    blok.write_text("x")
    monkeypatch.setenv("LOCALAPPDATA", str(blok))  # do pliku nie da się utworzyć podkatalogu -> katalog tymczasowy systemu
    monkeypatch.setattr(build_dk, "_IK_CACHE", None)
    p = build_dk._ikona_dk("activity", "FFFFFF")
    assert p and os.path.exists(p) and not p.startswith(str(blok))
