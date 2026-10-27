# -*- coding: utf-8 -*-
"""Testy dokument.py (prezentacja z dokumentu: docx, doc, rtf, odt, pdf, txt, md). Bez PowerPointa i bez LLM:
    python -m pytest -p no:cacheprovider test_dokument.py -q
Pliki testowe powstają w katalogu tymczasowym. .doc / .rtf / .odt wymagają Worda (bez niego test jest pomijany), pdf - PyMuPDF (fitz)."""
import io
import os
import re
import sys
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dokument  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = ('xmlns:w="%s" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"' % W)


# --- pomocnicy: minimalny docx ręcznie (bez python-docx) ------------------------------------------------------------------
def _p(t, styl=None, num=None, bold=False):
    ppr = ""
    if styl:
        ppr += '<w:pStyle w:val="%s"/>' % styl
    if num:
        ppr += '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="%d"/></w:numPr>' % num
    rpr = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return '<w:p><w:pPr>%s</w:pPr><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>' % (ppr, rpr, t)


def _tab(wiersze):
    return "<w:tbl>" + "".join("<w:tr>" + "".join("<w:tc><w:p><w:r><w:t>%s</w:t></w:r></w:p></w:tc>" % c for c in w) + "</w:tr>"
                               for w in wiersze) + "</w:tbl>"


def _obraz(rid="rId9"):
    return ('<w:p><w:r><w:drawing><a:graphic><a:graphicData><a:blip r:embed="%s"/></a:graphicData></a:graphic></w:drawing></w:r></w:p>' % rid)


STYLES = ('<w:styles xmlns:w="%s">' % W + "".join(
    '<w:style w:type="paragraph" w:styleId="%s"><w:name w:val="%s"/></w:style>' % (i, n) for i, n in (
        ("Title", "Title"), ("Heading1", "heading 1"), ("Heading2", "heading 2"), ("Heading3", "heading 3"), ("Quote", "Quote"),
        ("TOC1", "toc 1"))) + "</w:styles>")
NUMBERING = ('<w:numbering xmlns:w="%s"><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:numFmt w:val="bullet"/></w:lvl></w:abstractNum>'
             '<w:abstractNum w:abstractNumId="1"><w:lvl w:ilvl="0"><w:numFmt w:val="decimal"/></w:lvl></w:abstractNum>'
             '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num><w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num></w:numbering>' % W)


def _png(rozm=(300, 200)):
    from PIL import Image
    b = io.BytesIO()
    Image.new("RGB", rozm, (200, 120, 40)).save(b, "PNG")
    return b.getvalue()


def zrob_docx(sciezka, body, obraz=None, styles=True):
    with zipfile.ZipFile(sciezka, "w") as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="xml" ContentType="application/xml"/></Types>')
        z.writestr("word/document.xml", '<?xml version="1.0" encoding="UTF-8"?><w:document %s><w:body>%s</w:body></w:document>' % (NS, body))
        if styles:
            z.writestr("word/styles.xml", STYLES)
            z.writestr("word/numbering.xml", NUMBERING)
        if obraz is not None:
            z.writestr("word/_rels/document.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId9" Type="image" Target="media/image1.png"/></Relationships>')
            z.writestr("word/media/image1.png", obraz)
    return sciezka


TRESC = {
    "Zasady": _p("Zasady pracy", "Title") + _p("Krótki przewodnik dla zespołu.") +
    _p("Wstęp", "Heading1") + _p("Pierwsze zdanie wstępu. Drugie zdanie wstępu, które ma więcej słów niż poprzednie.") +
    _p("Szczegóły", "Heading2") + _p("Prezentacja wygląda jak sklep: dużo światła. Zieleń marki to akcent.") +
    _p("Zielony punkt", num=1) + _p("Czerwony punkt", num=1) + _p("Pierwszy krok", num=2) + _p("Drugi krok", num=2) +
    _p("Drobiazg", "Heading3") + _p("Krótki akapit pod trzecim poziomem.") +
    _tab([["Slot", "Rola"], ["Akcent 1", "zieleń"], ["Akcent 2", "czerwień"]]) +
    _p("Cytat do zapamiętania.", "Quote") + _obraz() + _p("Podpis pod obrazem.") +
    _p("Spis treści", "TOC1") +
    _p("Zakończenie", "Heading1") + _p("Ostatni akapit dokumentu.")
}


def _model_docx(tmp_path):
    p = zrob_docx(str(tmp_path / "zasady.docx"), TRESC["Zasady"], obraz=_png())
    return dokument.wczytaj(p, str(tmp_path / "rob"))


def _typy(m):
    return [b["typ"] for b in m["bloki"]]


# --- wczytanie -------------------------------------------------------------------------------------------------------------------
def test_docx_style_listy_tabela_obraz_cytat(tmp_path):
    m = _model_docx(tmp_path)
    assert m["tytul"] == "Zasady pracy"
    assert m["tytul_idx"] == 0
    assert _typy(m) == ["h1", "p", "h1", "p", "h2", "p", "li", "li", "li", "li", "h3", "p", "tabela", "cytat", "obraz", "p", "h1", "p"]
    li = [b for b in m["bloki"] if b["typ"] == "li"]
    assert [b.get("num") for b in li] == [False, False, True, True]
    tab = next(b for b in m["bloki"] if b["typ"] == "tabela")
    assert tab["wiersze"][0] == ["Slot", "Rola"] and len(tab["wiersze"]) == 3
    obr = next(b for b in m["bloki"] if b["typ"] == "obraz")
    assert os.path.isfile(obr["obraz"])
    assert any("spis treści" in o.lower() for o in m["ostrzezenia"])      # spis treści pominięty z komunikatem
    assert not any(b["t"] == "Spis treści" for b in m["bloki"])


def test_docx_bez_stylow_pogrubiony_krotki_akapit_to_naglowek(tmp_path):
    body = (_p("Wyniki badania", bold=True) + _p("Wynik wyniósł 37% w obu grupach. To najwyższy wynik w badaniu.") +
            _p("Wnioski", bold=True) + _p("Rekomendujemy tę koncepcję do produkcji, ponieważ wygrała w badaniu konsumenckim.") +
            _p("Kolejny akapit bez nagłówka, dłuższy, żeby nagłówków było mniej niż połowa wszystkich akapitów."))
    m = dokument.wczytaj(zrob_docx(str(tmp_path / "bez.docx"), body, styles=False), str(tmp_path / "r"))
    assert _typy(m) == ["h1", "p", "h1", "p", "p"]
    assert m["tytul"] == "bez"                               # dwa nagłówki 1 = rozdziały, tytuł z nazwy pliku


def test_docx_uszkodzony_i_nieznany_format(tmp_path):
    bad = tmp_path / "zly.docx"
    bad.write_bytes(b"to nie jest zip")
    with pytest.raises(ValueError, match="docx"):
        dokument.wczytaj(str(bad), str(tmp_path / "r"))
    x = tmp_path / "a.xyz"
    x.write_text("tekst")
    with pytest.raises(ValueError, match="nie jest obsługiwany"):
        dokument.wczytaj(str(x), str(tmp_path / "r"))


def test_txt_naglowki_listy_zawiniecia(tmp_path):
    txt = ("WSTĘP\n\nTo jest pierwszy akapit dokumentu tekstowego, który ma kilka słów i kończy się kropką.\n\n"
           "Wyniki badania\n\nDrugi akapit jest dłuższy i opisuje wyniki badania w kilku zdaniach. Wynik jest dobry.\n\n"
           "- pierwszy punkt\n- drugi punkt\n- trzeci punkt\n\n1. Krok pierwszy\n2. Krok drugi\n")
    p = tmp_path / "a.txt"
    p.write_text(txt, encoding="utf-8")
    m = dokument.wczytaj(str(p), str(tmp_path / "r"))
    assert _typy(m) == ["h1", "p", "h1", "p", "li", "li", "li", "li", "li"]
    assert [b.get("num") for b in m["bloki"][4:]] == [False, False, False, True, True]


def test_txt_kodowanie_cp1250_i_krotkie_linie_to_lista(tmp_path):
    p = tmp_path / "pl.txt"
    p.write_bytes("Zażółć\nGęślą\nJaźń\n".encode("cp1250"))
    m = dokument.wczytaj(str(p), str(tmp_path / "r"))
    assert [b["t"] for b in m["bloki"]] == ["Zażółć", "Gęślą", "Jaźń"] and set(_typy(m)) == {"li"}


def test_md_naglowki_listy_tabela_cytat(tmp_path):
    md = ("# Raport\n\nWstęp do raportu.\n\n## Wyniki\n\n- **82%** osób jest zadowolonych.\n- 75% poleca.\n\n"
          "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n\n> Cytat z [linkiem](http://x.pl) - Jan Kowalski\n")
    p = tmp_path / "a.md"
    p.write_text(md, encoding="utf-8")
    m = dokument.wczytaj(str(p), str(tmp_path / "r"))
    assert m["tytul"] == "Raport"
    assert _typy(m) == ["h1", "p", "h2", "li", "li", "tabela", "cytat"]
    assert m["bloki"][3]["t"] == "82% osób jest zadowolonych."      # znaczniki markdown znikają
    assert m["bloki"][6]["t"] == "Cytat z linkiem - Jan Kowalski"


def test_naglowki_z_haszami_wpisanymi_w_wordzie(tmp_path):
    body = _p("## Strona główna", "Heading1") + _p("#### Karta", "Heading2") + _p("Treść karty jest tutaj.")
    m = dokument.wczytaj(zrob_docx(str(tmp_path / "h.docx"), body), str(tmp_path / "r"))
    assert [b["t"] for b in m["bloki"] if b["typ"].startswith("h")] == ["Strona główna", "Karta"]


def test_limit_60000_slow(tmp_path):
    p = tmp_path / "duzy.txt"
    p.write_text(("Słowo " * 400 + ".\n\n") * 160, encoding="utf-8")
    with pytest.raises(ValueError, match="za dużo"):
        dokument.wczytaj(str(p), str(tmp_path / "r"))


def test_pdf_skan_bez_tekstu(tmp_path):
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    page = doc.new_page()
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 300, 300), False)
    page.insert_image(page.rect, pixmap=pix)
    p = str(tmp_path / "skan.pdf")
    doc.save(p)
    with pytest.raises(ValueError, match="skan bez tekstu"):
        dokument.wczytaj(p, str(tmp_path / "r"))


def test_pdf_naglowki_lista_stopki_i_numery_stron(tmp_path):
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    for strona in range(3):
        pg = doc.new_page()
        pg.insert_text((72, 40), "Firma Test - raport poufny", fontsize=9)             # nagłówek na każdej stronie
        pg.insert_text((290, 810), str(strona + 1), fontsize=9)                         # numer strony
        y = 100
        if strona == 0:
            pg.insert_text((72, y), "Raport roczny", fontsize=24)
            y += 50
        pg.insert_text((72, y), "Rozdzial %d" % (strona + 1), fontsize=16)      # Helvetica bez polskich liter
        y += 28
        for l in ("To jest akapit rozdzialu numer %d. Opisuje on sytuacje na rynku" % (strona + 1), "i konczy sie po drugiej linii tekstu."):
            pg.insert_text((72, y), l, fontsize=11)
            y += 15
        y += 20
        pg.insert_text((72, y), "• punkt pierwszy", fontsize=11)
        pg.insert_text((72, y + 16), "• punkt drugi", fontsize=11)
    p = str(tmp_path / "r.pdf")
    doc.save(p)
    m = dokument.wczytaj(p, str(tmp_path / "rob"))
    tx = [b["t"] for b in m["bloki"]]
    assert not any("poufny" in t for t in tx) and not any(re.fullmatch(r"\d", t) for t in tx)
    assert m["tytul"] == "Raport roczny"
    assert [b["t"] for b in m["bloki"] if b["typ"].startswith("h") and b["t"].startswith("Rozdzial")] == ["Rozdzial 1", "Rozdzial 2", "Rozdzial 3"]
    assert sum(1 for b in m["bloki"] if b["typ"] == "li") == 6
    assert any(b["typ"] == "p" and "na rynku i konczy sie po drugiej linii" in b["t"] for b in m["bloki"])    # linie sklejone w akapit


def _jest_word():
    try:
        import winreg
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Word.Application"))
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _jest_word(), reason="brak Microsoft Word - formaty doc / rtf / odt czyta Word")
def test_rtf_przez_word(tmp_path):
    p = tmp_path / "a.rtf"
    p.write_text(r"{\rtf1\ansi\deff0 {\fonttbl{\f0 Arial;}}\pard Pierwszy akapit rtf.\par Drugi akapit rtf jest dluzszy.\par}", encoding="ascii")
    m = dokument.wczytaj(str(p), str(tmp_path / "rob"))
    assert [b["t"] for b in m["bloki"]] == ["Pierwszy akapit rtf.", "Drugi akapit rtf jest dluzszy."]


def test_skrypt_worda_zamyka_wlasna_instancje():
    ps = dokument._PS_WORD
    assert "$w.Quit()" in ps and "$d.Close()" in ps          # Quit($false) w PowerShellu rzuca błąd i zostawia ukryty winword.exe
    assert "AutomationSecurity" in ps


# --- struktura, zakresy suwaków, składanie ---------------------------------------------------------------------------------
def _doc_tekstowy(tmp_path, n_sekcji=6, zdan=6, punkty=3):
    czesci = ["# Dokument testowy\n\nKrótki opis dokumentu testowego dla programu.\n"]
    for i in range(n_sekcji):
        czesci.append("## Sekcja %d\n" % (i + 1))
        czesci.append(" ".join("To jest zdanie numer %d w sekcji %d i ma kilkanaście słów, żeby plakat miał z czego robić hasła." % (j, i + 1)
                               for j in range(zdan)) + "\n")
        czesci.append("".join("- punkt %d %s\n" % (i, s) for s in ("jeden", "dwa", "trzy", "cztery", "pięć", "sześć")[:punkty]))
    p = tmp_path / "dok.md"
    p.write_text("\n".join(czesci), encoding="utf-8")
    return dokument.wczytaj(str(p), str(tmp_path / "rob"))


def test_zakresy_suwakow_rosnace_i_liczone_z_dokumentu(tmp_path):
    m = _doc_tekstowy(tmp_path)
    s = dokument.statystyka(m)
    assert s["naglowki"] == {1: 0, 2: 6, 3: 0}
    assert 1 <= s["slajdy_min"] <= s["slajdy_domyslnie"] <= s["slajdy_max"] <= 80
    assert s["slajdy_min"] < s["slajdy_max"]
    assert s["rozdzialy_max"] == 6
    mala = dokument.statystyka(_doc_tekstowy(tmp_path, n_sekcji=2, zdan=2))
    assert mala["slajdy_max"] < s["slajdy_max"] and mala["rozdzialy_max"] == 2     # zakres zależy od dokumentu


def test_zakres_bez_naglowkow_rozdzialy_zero(tmp_path):
    p = tmp_path / "p.txt"
    p.write_text("Pierwszy akapit tekstu. Ma dwa zdania.\n\nDrugi akapit tekstu. Też ma dwa zdania.\n", encoding="utf-8")
    m = dokument.wczytaj(str(p), str(tmp_path / "r"))
    s = dokument.statystyka(m)
    assert s["rozdzialy_max"] == 0 and s["naglowki"] == {1: 0, 2: 0, 3: 0}


def _zbuduj(spec, tmp_path, monkeypatch, nazwa="w.pptx"):
    import guard
    monkeypatch.setattr(guard, "CACHE", str(tmp_path / "guard.json"))
    import build_dk
    spec = dict(spec, output=str(tmp_path / nazwa))
    build_dk.build(spec, spec["output"])
    return build_dk.build.last_out


@pytest.mark.parametrize("ktora", ["min", "domyslnie", "max"])
def test_pokrycie_100_procent_na_trzech_wartosciach_suwaka(tmp_path, monkeypatch, ktora):
    m = _doc_tekstowy(tmp_path, n_sekcji=4, zdan=5)
    s = dokument.statystyka(m)
    n = {"min": s["slajdy_min"], "domyslnie": s["slajdy_domyslnie"], "max": s["slajdy_max"]}[ktora]
    spec = dokument.zloz(m, {"slajdy": n, "rozdzialy": 0, "wyjscie": str(tmp_path), "styl": "nowy"})
    assert all(sl.get("title") for sl in spec["slides"] if sl["type"] not in ("cover_text", "end"))      # każdy slajd ma tytuł
    pptx = _zbuduj(spec, tmp_path, monkeypatch)
    pok = dokument.pokrycie(m, pptx, spec["mapa_blokow"])
    assert pok["tekst"].startswith("Treść: 100%") and not pok["brakuje"], pok["brakuje"]
    assert dokument.pokrycie(m, pptx)["tekst"].startswith("Treść: 100%")                           # także bez mapy
    assert spec["ustawienia"]["slajdy"] <= n                                                         # twarda bramka: nigdy więcej niż suwak
    assert all(sl.get("notes") for sl in spec["slides"] if sl["type"] not in ("end", "agenda", "section"))   # pełny tekst w notatkach


def test_kontrakt_specu_agenda_przekladki_wzory(tmp_path, monkeypatch):
    m = _doc_tekstowy(tmp_path, n_sekcji=4, zdan=4)
    spec = dokument.zloz(m, {"slajdy": 8, "rozdzialy": 3, "wyjscie": str(tmp_path), "styl": "nowy"})
    for k in ("slides", "output", "uwagi", "mapa_blokow", "bledy_tekstu", "szablon"):
        assert k in spec
    typy = [sl["type"] for sl in spec["slides"]]
    assert typy[0] == "cover_text" and typy[1] == "agenda" and typy[-1] == "end"
    assert typy.count("section") == 3
    assert spec["slides"][1]["items"] == [sl["title"] for sl in spec["slides"] if sl["type"] == "section"]
    assert spec["sections"] is True
    assert all(d.get("wzor") and d["wzor"]["id"].startswith("t") for d in spec["szablon"]), "każda decyzja ma wzór z katalogu szablonu"
    assert {"okladka", "agenda", "przekladka", "zakonczenie"} <= {d["wzorzec"] for d in spec["szablon"]}
    pptx = _zbuduj(spec, tmp_path, monkeypatch)
    assert dokument.pokrycie(m, pptx, spec["mapa_blokow"])["tekst"].startswith("Treść: 100%")


def test_zero_rozdzialow_bez_agendy_i_przekladek(tmp_path):
    m = _doc_tekstowy(tmp_path)
    spec = dokument.zloz(m, {"slajdy": 10, "rozdzialy": 0, "wyjscie": str(tmp_path)})
    typy = [sl["type"] for sl in spec["slides"]]
    assert "agenda" not in typy and "section" not in typy


def test_pusty_i_jednoakapitowy_dokument_bez_wyjatku(tmp_path, monkeypatch):
    for tresc in ("", "To jest jedyny akapit."):
        p = tmp_path / "x.txt"
        p.write_text(tresc, encoding="utf-8")
        m = dokument.wczytaj(str(p), str(tmp_path / "r"))
        s = dokument.statystyka(m)
        spec = dokument.zloz(m, {"slajdy": s["slajdy_domyslnie"], "rozdzialy": 0, "wyjscie": str(tmp_path)})
        pptx = _zbuduj(spec, tmp_path, monkeypatch)
        assert dokument.pokrycie(m, pptx)["tekst"].startswith("Treść: 100%")
        assert spec["slides"][0]["type"] == "cover_text" and spec["slides"][-1]["type"] == "end"
    assert dokument.statystyka(dokument.wczytaj(str(p), str(tmp_path / "r")))["slajdy_min"] >= 1


def test_tabela_krotka_to_slajd_table_dluga_dzieli_sie(tmp_path):
    body = _p("Dane", "Heading1") + _tab([["Produkt", "Cena", "Uwagi"]] + [["Produkt %d" % i, "%d zł" % i, "uwaga %d" % i] for i in range(20)])
    m = dokument.wczytaj(zrob_docx(str(tmp_path / "t.docx"), body), str(tmp_path / "r"))
    s = dokument.statystyka(m)
    spec = dokument.zloz(m, {"wyjscie": str(tmp_path)})
    tabele = [sl for sl in spec["slides"] if sl["type"] == "table"]
    assert len(tabele) == 1 and len(tabele[0]["rows"]) == 6 and tabele[0]["head"] == ["Produkt", "Cena", "Uwagi"]   # Standardowo: 6 wierszy, reszta w notatkach
    assert "Produkt 19" in tabele[0]["notes"] and any("skrócone" in u for u in spec["uwagi"])
    spec = dokument.zloz(m, {"slajdy": s["slajdy_max"], "wyjscie": str(tmp_path)})
    tabele = [sl for sl in spec["slides"] if sl["type"] == "table"]
    assert len(tabele) == 3 and all(len(t["rows"]) <= 8 for t in tabele)                                          # Szczegółowo: 20 wierszy / 8
    assert [t["title"] for t in tabele] == ["Dane", "Dane (2)", "Dane (3)"]


def test_tabela_z_dlugimi_komorkami_na_slajdzie_pierwsza_fraza_reszta_w_notatkach(tmp_path):
    dlugi = "To jest bardzo długi opis w komórce tabeli, który nie zmieściłby się w jednej linii wiersza tabeli. " * 2
    body = _p("Brief", "Heading1") + _tab([["Marka", "Opis", "Cel"], ["Kubara", dlugi, "sprzedaż"], ["Dobra Kaloria", dlugi, "marka"]])
    m = dokument.wczytaj(zrob_docx(str(tmp_path / "t.docx"), body), str(tmp_path / "r"))
    spec = dokument.zloz(m, {"wyjscie": str(tmp_path)})
    t = next(sl for sl in spec["slides"] if sl["type"] == "table")
    assert t["head"] == ["Marka", "Cel"]                       # kolumna bez pełnej frazy do 7 słów w komórkach znika ze slajdu
    assert dlugi.strip() in t["notes"]                         # ...a jej treść jest w notatkach


def test_obraz_z_podpisem_i_zapowiedzia_jest_zrzutem_w_calosci(tmp_path):
    body = _p("Wynik", "Heading1") + _p("Zrzut ekranu z wynikiem:") + _obraz() + _p("Podpis pod obrazem.")
    m = dokument.wczytaj(zrob_docx(str(tmp_path / "o.docx"), body, obraz=_png()), str(tmp_path / "r"))
    spec = dokument.zloz(m, {"wyjscie": str(tmp_path)})
    pics = [sl for sl in spec["slides"] if sl["type"] == "pics"]
    assert len(pics) == 1 and pics[0]["items"][0]["caption"] == "Zrzut ekranu z wynikiem: Podpis pod obrazem."
    assert pics[0]["title"] == "Wynik"


def test_cytat_z_autorem_i_podtytul_okladki(tmp_path):
    body = (_p("Raport", "Title") + _p("Pierwszy krótki akapit staje się podtytułem okładki.") + _p("Rozdział", "Heading1") +
            _p("Brands grow through constant exposure to new buyers - Byron Sharp", "Quote"))
    m = dokument.wczytaj(zrob_docx(str(tmp_path / "c.docx"), body), str(tmp_path / "r"))
    spec = dokument.zloz(m, {"wyjscie": str(tmp_path)})
    assert spec["slides"][0]["subtitle"] == "Pierwszy krótki akapit staje się podtytułem okładki."
    q = next(sl for sl in spec["slides"] if sl["type"] == "uklad")
    assert q["rows"][0] == {"k": "quote", "t": "Brands grow through constant exposure to new buyers", "author": "Byron Sharp"}


def test_numery_pozycji_nie_koncza_zdan():
    z = dokument._zdania("Naszymi kategoriami są: 1. Słodkie przekąski 2. Roślinne zamienniki 3. Produkty śniadaniowe.")
    assert z == ["Naszymi kategoriami są: 1. Słodkie przekąski", "2. Roślinne zamienniki", "3. Produkty śniadaniowe."]
    assert dokument._zdania("W 2024 r. osoby 65+ to 7,7 mln osób. GUS prognozuje ok. 30%.") == [
        "W 2024 r. osoby 65+ to 7,7 mln osób.", "GUS prognozuje ok. 30%."]      # „r.” i „ok.” nie kończą zdań


def test_tytul_z_nazwy_pliku_bez_podkreslnikow(tmp_path):
    p = tmp_path / "Brief_redesign_DK_25_09.txt"
    p.write_text("Pierwszy akapit.\n\nDrugi akapit tego dokumentu jest dłuższy.\n", encoding="utf-8")
    assert dokument.wczytaj(str(p), str(tmp_path / "r"))["tytul"] == "Brief redesign DK 25 09"


def test_blad_tekstu_trafia_do_uwag_i_listy(tmp_path):
    p = tmp_path / "b.md"
    p.write_text("# Raport\n\n## Wyniki\n\nProgram zrobił komunikacjaod konsumentów dla wszystkich klientów.\n", encoding="utf-8")
    m = dokument.wczytaj(str(p), str(tmp_path / "r"))
    spec = dokument.zloz(m, {"wyjscie": str(tmp_path)})
    assert any(u["jest"] == "komunikacjaod" for u in spec["bledy_tekstu"])
    assert any("komunikacjaod" in u for u in spec["uwagi"])
    assert m["bloki"][-1]["t"].count("komunikacjaod") == 1          # nie poprawiamy tekstu, tylko ostrzegamy


def test_cli_wersja_bez_qa(tmp_path):
    import subprocess
    p = tmp_path / "k.md"
    p.write_text("# Raport\n\n## Wyniki\n\nTo jest akapit z kilkoma słowami i wynikiem 37% w badaniu.\n", encoding="utf-8")
    env = dict(os.environ, DK_GUARD_CACHE=str(tmp_path / "g.json"), PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(HERE, "dokument.py"), str(p), "--slajdy", "2", "--rozdzialy", "0", "--bez-qa",
                        "--wyjscie", str(tmp_path / "wyj"), "--robocze", str(tmp_path / "rob")], capture_output=True, env=env, timeout=240)
    out = r.stdout.decode("utf-8", "replace")
    assert r.returncode == 0, out + r.stderr.decode("utf-8", "replace")
    assert "Treść: 100%" in out and os.path.isfile(str(tmp_path / "wyj" / "k - nowy styl.pptx"))


def test_zakresy_planu_min_dom_max_i_udzial_na_slajdach(tmp_path):
    m = _doc_tekstowy(tmp_path, n_sekcji=8, zdan=9)
    s = dokument.statystyka(m)
    assert s["slajdy_min"] <= s["slajdy_domyslnie"] < s["slajdy_max"] <= 80
    assert s["slajdy_min"] == 8                                               # jeden nośnik (lista) na rozdział
    assert s["slajdy_max"] >= 16                                              # Szczegółowo: także wstępy sekcji jako karty hasło + dopisek
    pct = s["na_slajdach"]
    assert 0 < pct["min"] <= pct["domyslnie"] <= pct["max"] <= 100


def test_statystyka_jest_natychmiastowa(tmp_path):
    import time
    m = _doc_tekstowy(tmp_path, n_sekcji=30, zdan=12)
    t0 = time.time()
    dokument.statystyka(m)
    assert time.time() - t0 < 1.0


def test_zloz_dwa_tysiace_slow_w_kilkanascie_sekund(tmp_path):
    import time
    m = _doc_tekstowy(tmp_path, n_sekcji=18, zdan=8)         # ok. 2000 słów
    assert dokument.statystyka(m)["slowa"] > 1800
    t0 = time.time()
    dokument.zloz(m, {"wyjscie": str(tmp_path)})
    assert time.time() - t0 < 30          # zwykle 2-10 s; zapas na obciążony komputer


def test_dluga_etykieta_i_dluga_agenda_nie_psuja_slajdow(tmp_path):
    dlugi = "Bardzo długi nagłówek nadrzędny, który nie zmieści się w jednej linii etykiety nad tytułem"
    body = (_p("Tytuł dokumentu", "Title") + _p(dlugi, "Heading1") + _p("Podrozdział", "Heading2") +
            _p("Treść podrozdziału, krótka. Drugie zdanie podrozdziału jest dłuższe i ma kilka słów więcej niż pierwsze.") +
            _p("Punkt pierwszy", num=1) + _p("Punkt drugi", num=1) + _p("Punkt trzeci", num=1) +
            "".join(_p("Rozdział numer %d, którego nazwa jest długa i nie zmieści się w kolumnie agendy" % i, "Heading1") +
                    _p("Treść rozdziału %d ma kilka zdań i sporo słów, żeby rozdział był osobnym rozdziałem planu. Drugie zdanie rozdziału "
                       "też jest długie i dokłada słów do sumy. Trzecie zdanie rozdziału, które kończy akapit, ma jeszcze kilka słów." % i) +
                    _p("Punkt %d a" % i, num=1) + _p("Punkt %d b" % i, num=1) + _p("Punkt %d c" % i, num=1)
                    for i in range(4)))
    m = dokument.wczytaj(zrob_docx(str(tmp_path / "d.docx"), body), str(tmp_path / "r"))
    spec = dokument.zloz(m, {"rozdzialy": 5, "wyjscie": str(tmp_path)})
    pod = next(sl for sl in spec["slides"] if sl.get("title", "").endswith("Podrozdział"))
    assert pod["title"].startswith("Bardzo długi") and "kicker" not in pod          # za długa etykieta idzie do tytułu
    assert not [sl for sl in spec["slides"] if sl["type"] == "agenda"]               # 5 długich punktów: bez spisu treści
    assert any("nie dodałem" in u for u in spec["uwagi"])


def test_xml_bez_rozwijania_encji(tmp_path):
    zly = ('<?xml version="1.0"?><!DOCTYPE w [<!ENTITY x SYSTEM "file:///C:/Windows/win.ini">]>'
           '<w:document xmlns:w="%s"><w:body><w:p><w:r><w:t>&x;</w:t></w:r></w:p></w:body></w:document>' % W)
    p = str(tmp_path / "x.docx")
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("word/document.xml", zly)
    m = dokument.wczytaj(p, str(tmp_path / "r"))
    assert not any("[fonts]" in b["t"] or "for 16-bit" in b["t"] for b in m["bloki"])


def test_usterki_z_verify_i_zamiana_wariantu_zachowuje_tytul(tmp_path):
    m = _doc_tekstowy(tmp_path, n_sekcji=4, zdan=5, punkty=4)      # 4 kafle: warianty rząd / siatka 2 x 2 = kandydaci układu
    spec = dokument.zloz(m, {"slajdy": 4, "rozdzialy": 0, "wyjscie": str(tmp_path)})
    v = "Tekst - problemy: 2\n   s5 PRZEPELNIENIE pola +2pt: 'abc'\n   s7 SIEROTA w naglowku: 'wody'\n"
    assert dokument.usterki_po_renderze(str(tmp_path / "brak"), spec, v) == {5: ["PRZEPELNIENIE"], 7: ["SIEROTA"]}
    z_kand = [i for i, sl in enumerate(spec["slides"], 1) if any(r["zrodlo"] == sl.get("zrodlo") and len(r["kandydaci"]) > 1
                                                                   for r in spec["warianty"]["slajdy"])]
    assert z_kand, "slajdy tekstowe mają listę kandydatów układu"
    tytuly = {nr: (spec["slides"][nr - 1]["title"], spec["slides"][nr - 1].get("kicker")) for nr in z_kand}
    zm = dokument.popraw_po_renderze(spec, {nr: ["SIEROTA"] for nr in z_kand})
    assert zm
    for nr in zm:       # zamieniony wariant ma ten sam tytuł i etykietę, nie roboczy „(2)”
        assert (spec["slides"][nr - 1]["title"], spec["slides"][nr - 1].get("kicker")) == tytuly[nr]
    assert any("poprawiłem układ" in u for u in spec["uwagi"])


def test_petla_poprawek_cofa_zmiane_bez_poprawy(tmp_path):
    m = _doc_tekstowy(tmp_path, n_sekcji=3, zdan=5, punkty=4)
    spec = dokument.zloz(m, {"slajdy": 3, "rozdzialy": 0, "wyjscie": str(tmp_path)})
    nr = next(i for i, sl in enumerate(spec["slides"], 1)
              if any(r["zrodlo"] == sl.get("zrodlo") and len(r["kandydaci"]) > 1 for r in spec["warianty"]["slajdy"]))
    przed = dokument.json.dumps(spec["slides"][nr - 1], sort_keys=True)
    budowy = []
    wynik, popr = dokument.petla_poprawek(spec, lambda: ({nr: ["KARTA_PUSTA"]}, ""), lambda: budowy.append(1))
    assert popr == [] and budowy                              # usterka nie zniknęła -> zmiana cofnięta
    assert dokument.json.dumps(spec["slides"][nr - 1], sort_keys=True) == przed
    stan = {"n": 0}

    def pomiar():
        stan["n"] += 1
        return ({nr: ["KARTA_PUSTA"]} if stan["n"] == 1 else {}), ""      # po zamianie usterki nie ma
    wynik, popr = dokument.petla_poprawek(spec, pomiar, lambda: None)
    assert popr == [nr]


# --- runda 2 (13.10): 2-3 myśli na slajd, tytuł z hasła zamiast licznika ----------------------------------------------------------
def _doc_prozy(tmp_path, nazwa="proza.md", sekcje=(("Długa sekcja", 14),), nagl=True):
    """Proza: akapity po 2 zdania (po ok. 14 słów, bez cyfr), każde zdanie ma przecinek po 6. słowie (hasło = jego początek)."""
    czesci = ["# Tytuł prozy\n\nKrótki opis dokumentu z prozą.\n"] if nagl else []
    j = 0
    for nag, ile in sekcje:
        if nagl:
            czesci.append("## %s\n" % nag)
        for a in range(0, ile, 2):
            czesci.append(" ".join("Zdanie %s%s opisuje pewną myśl, która ma kilkanaście słów i kończy się kropką." % (chr(65 + (j + k) % 26), chr(97 + (j + k) // 26))
                                   for k in range(2)) + "\n")
            j += 2
    p = tmp_path / nazwa
    p.write_text("\n".join(czesci), encoding="utf-8")
    return dokument.wczytaj(str(p), str(tmp_path / ("rob_" + nazwa)))


def _karty_slajdu(sl):
    return sum(len(r["items"]) for r in sl.get("rows", []) if r["k"] == "cols")


def test_proza_bez_list_pokazuje_akapity_standardowo(tmp_path):
    m = _doc_prozy(tmp_path, sekcje=(("Pierwsza", 8), ("Druga", 8), ("Trzecia", 8)))
    s = dokument.statystyka(m)
    assert s["slajdy_min"] == 3 and s["slajdy_domyslnie"] == 3 and s["slajdy_max"] == 12       # 3 sekcje x 4 akapity: Szczegółowo = akapit na slajd
    spec = dokument.zloz(m, {"wyjscie": str(tmp_path), "rozdzialy": 0})
    tresc = [sl for sl in spec["slides"] if sl["type"] == "uklad"]
    assert [sl["title"] for sl in tresc] == ["Pierwsza", "Druga", "Trzecia"]
    for sl in tresc:                                                                   # karta: hasło Mindset + dopisek Lato, cały tekst w notatkach
        bl = sl["rows"][0]["items"][0]["blocks"]
        assert bl[0]["k"] == "lead" and bl[0]["t"].startswith("Zdanie") and any(b["k"] == "p" for b in bl)
        assert sl["notes"].count("Zdanie") == 8


def test_na_karty_dzieli_zdania_po_slowach_i_ile_kart():
    zd = ["a b c d e f g h", "i j k l", "m n o p q r s t u v", "w x y z"]
    assert dokument._na_karty(zd, 1) == [zd]
    g = dokument._na_karty(zd, 2)
    assert len(g) == 2 and sum(g, []) == zd                                       # kolejność zachowana, nic nie ginie
    assert dokument._ile_kart(["jedno krótkie zdanie"]) == 1
    assert dokument._ile_kart(["x " * 14, "y " * 14]) == 2 and dokument._ile_kart(["x " * 17, "y " * 17, "z " * 17]) == 3


def test_szczegolowo_kazdy_akapit_na_slajdzie_z_numerem_czesci(tmp_path, monkeypatch):
    m = _doc_prozy(tmp_path)
    s = dokument.statystyka(m)
    spec = dokument.zloz(m, {"slajdy": s["slajdy_max"], "rozdzialy": 0, "wyjscie": str(tmp_path)})
    tresc = [sl for sl in spec["slides"] if sl["type"] == "uklad"]
    assert len(tresc) == 7 and tresc[0]["title"] == "Długa sekcja"                 # 14 zdań po 2 = 7 akapitów
    assert [sl["title"] for sl in tresc[1:]] == ["Długa sekcja (%d)" % i for i in range(2, 8)]
    assert spec["ustawienia"]["slajdy"] <= s["slajdy_max"]
    pptx = _zbuduj(spec, tmp_path, monkeypatch)
    assert dokument.pokrycie(m, pptx, spec["mapa_blokow"])["tekst"].startswith("Treść: 100%")
    assert dokument.pokrycie(m, pptx)["tekst"].startswith("Treść: 100%")


def test_dwa_slajdy_sekcji_zostaja_z_numerkiem(tmp_path):
    m = _doc_prozy(tmp_path, sekcje=(("Krótka sekcja", 6),))
    spec = dokument.zloz(m, {"slajdy": 2, "rozdzialy": 0, "wyjscie": str(tmp_path)})
    tresc = [sl for sl in spec["slides"] if sl["type"] == "uklad"]
    assert [sl["title"] for sl in tresc] == ["Krótka sekcja", "Krótka sekcja (2)"]


def test_dokument_plaski_ma_tytul_dokumentu_jako_tytul_slajdu(tmp_path):
    m = _doc_prozy(tmp_path, nazwa="plaski.md", sekcje=(("-", 14),), nagl=False)
    s = dokument.statystyka(m)
    spec = dokument.zloz(m, {"slajdy": 4, "wyjscie": str(tmp_path)})
    tresc = [sl for sl in spec["slides"] if sl["type"] == "uklad"]
    assert len(tresc) == 4 and tresc[0]["title"] == m["tytul"] and all("kicker" not in sl for sl in tresc)
    assert s["slajdy_min"] == 1 and s["rozdzialy_max"] == 0


def test_etykieta_sekcji_skraca_do_pelnych_slow_i_wielokropka():
    dlugi = "Ale skoro dobrze się znamy, chcemy się pochwalić super spotkaniem!"
    e = dokument._etykieta_sekcji(dlugi)
    assert len(e) <= dokument.KICKER_MAX and e.endswith("…") and dlugi.upper().startswith(e[:-1].upper())
    assert dokument._etykieta_sekcji("Krótka nazwa") == "Krótka nazwa"


def test_skladnik_i_numer_nie_sa_tytulem_ale_nazwa_z_cyfra_tak():
    assert dokument._ilosc("1 łyżeczka harissy lub innej ostrej pasty") and dokument._ilosc("2-3 pęczki natki")
    assert not dokument._ilosc("4 Szpaki wykorzystują naturalne oleje") and not dokument._ilosc("Zwykłe zdanie")


def test_wybrany_kandydat_zachowuje_etykiete_nad_tytulem(tmp_path):
    m = _doc_prozy(tmp_path)
    spec = dokument.zloz(m, {"slajdy": 5, "rozdzialy": 0, "wyjscie": str(tmp_path)})
    for r in spec["warianty"]["slajdy"]:
        sl = next(x for x in spec["slides"] if x.get("zrodlo") == r["zrodlo"])
        for k in r["kandydaci"]:
            assert k["slajd"].get("kicker") == sl.get("kicker") and k["slajd"].get("title") == sl.get("title")


def test_max_jednozdaniowe_akapity_to_zielone_karty_albo_haslo_z_dopiskiem(tmp_path, monkeypatch):
    p = tmp_path / "krotkie.md"
    p.write_text("# Tytuł\n\nOpis.\n\n## Sekcja jednozdaniowych myśli\n\n" + "\n\n".join(
        "Myśl numer %s jest krótka i ma pełne zdanie." % w for w in
        ("alfa", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "teta")) + "\n", encoding="utf-8")
    m = dokument.wczytaj(str(p), str(tmp_path / "r"))
    s = dokument.statystyka(m)
    spec = dokument.zloz(m, {"slajdy": s["slajdy_max"], "rozdzialy": 0, "wyjscie": str(tmp_path)})
    tresc = [sl for sl in spec["slides"] if sl["type"] == "uklad"]
    assert len(tresc) == 8 and all(sl.get("kicker") in (None, "Tytuł") for sl in tresc)
    for sl in tresc:
        it = sl["rows"][0]["items"][0]
        assert it.get("fill") == "brand" and dokument._slow(it["blocks"][0]["t"]) <= dokument.ZIELONA_MAX      # zdanie <= 10 słów = zielona karta
    pptx = _zbuduj(spec, tmp_path, monkeypatch)
    assert dokument.pokrycie(m, pptx, spec["mapa_blokow"])["tekst"].startswith("Treść: 100%")
    assert dokument.pokrycie(m, pptx)["tekst"].startswith("Treść: 100%")


# --- 21.10.2026: streszczenie strukturalne + notatki, pdf z pojemnikami, cięcie fraz, bramki ----------------------------------------
def _pdf_dk(tmp_path, fitz):
    """PDF jak z HTML (Chrome): strona tytułowa z logo w rogu, strona z kaflami liczb, kartą z tabelą (linie pod komórkami), listą z kropkami,
    kartą programu z parami etykieta: wartość, strona FAQ w dwóch szpaltach. Pismo ozdobne = Helvetica-Bold, podstawowe = Helvetica."""
    doc = fitz.open()
    W, H = 595, 842
    B, D = "helv", "tibo"       # podstawowe / ozdobne (druga rodzina pisma: Times-Bold)
    # strona 1: okładka
    pg = doc.new_page(width=W, height=H)
    pg.insert_image(fitz.Rect(40, 37, 137, 108), pixmap=fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 400, 295), 0))   # logo w pasie góry, 16% szerokości
    pg.insert_text((400, 60), "Pazdziernik 2026", fontsize=9, fontname=B)
    pg.insert_text((40, 300), "PRZEGLAD DLA ZARZADU", fontsize=11, fontname=D)
    pg.insert_text((40, 340), "NARZEDZIA CYFROWE DZIALU", fontsize=29, fontname=D)
    pg.insert_text((40, 400), "Oprogramowanie, ktore wspiera codzienna prace marketingu: do czego sluzy, na jakiej", fontsize=12, fontname=B)
    pg.insert_text((40, 416), "technologii dziala, jak powstaje, jak chronimy dane oraz jakie dzialania planujemy.", fontsize=12, fontname=B)
    for x, lab, val in ((40, "AUTOR", "Jan Kowalski"), (174, "STAN NA", "21 pazdziernika 2026"), (308, "ZAKRES", "DAM, Photo Resizer")):
        pg.draw_rect(fitz.Rect(x, 720, x + 124, 796), color=None, fill=(0.97, 0.97, 0.96))
        pg.insert_text((x + 10, 740), lab, fontsize=8, fontname=D)
        pg.insert_text((x + 10, 760), val, fontsize=9, fontname=B)
    # strona 2: nagłówek strony, kafle liczb, karta z tabelą, karta z listą
    pg = doc.new_page(width=W, height=H)
    pg.insert_text((40, 60), "PODSUMOWANIE", fontsize=16, fontname=D)
    pg.insert_text((40, 78), "Narzedzia powstaja od marca 2026 jako odpowiedz na potrzeby zespolu.", fontsize=9, fontname=B)
    for i, (v, lab) in enumerate((("7", "obszarow, lacznie 11 narzedzi"), ("Python", "glowny jezyk programow"), ("ok. 2 800", "testow automatycznych"), ("03.2026", "poczatek prac"))):
        x = 40 + i * 131
        pg.draw_rect(fitz.Rect(x, 88, x + 122, 174), color=None, fill=(0.97, 0.97, 0.96))
        pg.insert_text((x + 10, 115), v, fontsize=22, fontname=D)
        pg.insert_text((x + 10, 135), lab, fontsize=8, fontname=B)
    pg.draw_rect(fitz.Rect(40, 182, 556, 420), color=None, fill=(0.97, 0.97, 0.96))      # karta
    pg.insert_text((52, 200), "PROGRAMY", fontsize=11, fontname=D)
    pg.draw_rect(fitz.Rect(52, 214, 543, 410), color=None, fill=(1, 1, 1))                # biała tabela
    kol = [(52, 146), (146, 319), (319, 402), (402, 490), (490, 543)]
    head = ["PROGRAM", "PRZEZNACZENIE", "PLATFORMA", "OD", "STATUS"]
    for (x0, _x1), h in zip(kol, head):
        pg.insert_text((x0 + 4, 228), h, fontsize=8, fontname=D)
    rows = [["DAM", "Katalog materialow marki z dysku firmowego M: wyszukiwanie, powiazania", "Windows, macOS", "03.2026", "beta"],
            ["Photo Resizer", "Masowa zmiana rozmiaru, konwersja i kompresja zdjec", "Windows", "07.2026", "w uzyciu"],
            ["Panel Ankiet", "Anonimowe ankiety i glosowania pracownikow", "przegladarka", "09.2026", "beta"],
            ["Skrypty Adobe", "Automatyzacja Photoshopa i Illustratora: eksport wizualizacji", "Photoshop", "06.2026", "w uzyciu"]]
    y = 233
    for r in rows:
        for (x0, x1) in kol:
            pg.draw_rect(fitz.Rect(x0, y, x1, y + 0.8), color=None, fill=(0.9, 0.9, 0.9))   # linia pod komórką
        for (x0, _x1), c in zip(kol, r):
            if len(c) > 30:
                pg.insert_text((x0 + 4, y + 16), c[:28], fontsize=8, fontname=B)
                pg.insert_text((x0 + 4, y + 27), c[28:], fontsize=8, fontname=B)
            else:
                pg.insert_text((x0 + 4, y + 16), c, fontsize=8, fontname=B)
        y += 40
    pg.draw_rect(fitz.Rect(40, 440, 293, 600), color=None, fill=(0.97, 0.97, 0.96))
    pg.insert_text((52, 458), "KORZYSCI DLA FIRMY", fontsize=11, fontname=D)
    for i, t in enumerate(("Powtarzalne zadania w minutach zamiast godzin: zdjecia, prezentacje.", "Jedno miejsce na materialy marki, widoczne na kazdym komputerze.",
                           "Spojny wyglad materialow zgodny z identyfikacja marki.", "Dodatkowa kontrola opakowan przed drukiem.")):
        yy = 480 + i * 24
        pg.draw_rect(fitz.Rect(54, yy - 6, 57, yy - 3), color=None, fill=(0, 0.5, 0.2))          # kropka punktora
        pg.insert_text((65, yy), t[:48], fontsize=8, fontname=B)
        pg.insert_text((65, yy + 10), t[48:], fontsize=8, fontname=B)
    pg.draw_rect(fitz.Rect(303, 440, 556, 600), color=None, fill=(0.97, 0.97, 0.96))
    pg.insert_text((315, 458), "DAM DOBRA KALORIA", fontsize=11, fontname=D)
    pg.draw_rect(fitz.Rect(315, 470, 543, 590), color=None, fill=(1, 1, 1))
    y = 470
    for lab, val in (("JEZYK", "Python JavaScript SQL"), ("DANE", "PostgreSQL na NAS (SSL), lokalnie SQLite"), ("TESTY", "ponad 1 900 automatycznych"), ("ROZWOJ", "od 03.2026, ok. 430 zmian")):
        for (x0, x1) in ((315, 391), (392, 543)):
            pg.draw_rect(fitz.Rect(x0, y + 28, x1, y + 28.8), color=None, fill=(0.9, 0.9, 0.9))
        pg.insert_text((321, y + 18), lab, fontsize=7, fontname=D)
        pg.insert_text((398, y + 18), val, fontsize=8, fontname=B)
        y += 29
    # strona 3: FAQ w dwóch szpaltach
    pg = doc.new_page(width=W, height=H)
    pg.insert_text((40, 60), "NAJCZESTSZE PYTANIA", fontsize=16, fontname=D)
    for col, x in ((0, 40), (1, 303)):
        for i in range(3):
            yy = 100 + i * 60
            pg.insert_text((x, yy), "Czy pytanie numer %d jest proste?" % (col * 3 + i + 1), fontsize=9, fontname=D)
            pg.insert_text((x, yy + 14), "Odpowiedz na pytanie %d jest krotka, ale ma dwa zdania." % (col * 3 + i + 1), fontsize=9, fontname=B)
            pg.insert_text((x, yy + 26), "Drugie zdanie odpowiedzi dopowiada szczegoly sprawy.", fontsize=9, fontname=B)
    p = str(tmp_path / "dk.pdf")
    doc.save(p)
    return p


def test_pdf_z_pojemnikami_tabele_kafle_logo_okladka(tmp_path):
    fitz = pytest.importorskip("fitz")
    m = dokument.wczytaj(_pdf_dk(tmp_path, fitz), str(tmp_path / "rob"))
    typy = _typy(m)
    assert m["tytul"] == "NARZEDZIA CYFROWE DZIALU" and m["bloki"][0].get("kicker") == "PRZEGLAD DLA ZARZADU"
    assert "obraz" not in typy                                                              # logo w pasie góry strony pominięte
    assert typy.count("kpi") == 1 and [it["value"] for it in next(b for b in m["bloki"] if b["typ"] == "kpi")["items"]] == ["7", "Python", "ok. 2 800", "03.2026"]
    tab = [b for b in m["bloki"] if b["typ"] == "tabela"]
    assert len(tab) == 1 and tab[0]["wiersze"][0] == ["PROGRAM", "PRZEZNACZENIE", "PLATFORMA", "OD", "STATUS"] and len(tab[0]["wiersze"]) == 5
    assert tab[0]["wiersze"][1][0] == "DAM" and tab[0]["wiersze"][1][4] == "beta"
    kv = [b for b in m["bloki"] if b["typ"] == "kv" and not b.get("meta")]
    assert len(kv) == 1 and [p[0] for p in kv[0]["pary"]] == ["JEZYK", "DANE", "TESTY", "ROZWOJ"]
    assert typy.count("li") == 4                                                             # kropki = punkty
    nagl = [(b["typ"], b["t"]) for b in m["bloki"] if b["typ"] in ("h2", "h3")]
    assert ("h2", "PODSUMOWANIE") in nagl and ("h3", "PROGRAMY") in nagl and ("h3", "KORZYSCI DLA FIRMY") in nagl
    assert not any(t in ("beta", "w uzyciu", "JEZYK", "DANE") for _k, t in nagl)            # metki i etykiety to nie nagłówki
    pyt = [b for b in m["bloki"] if b.get("pytanie")]
    assert len(pyt) == 6 and [re.search(r"\d", b["t"]).group() for b in pyt] == ["1", "2", "3", "4", "5", "6"]       # dwie szpalty czytane kolumnami
    s = dokument.statystyka(m)
    assert s["tabele"] == 1 and s["obrazy"] == 0 and s["naglowki"][2] == 2


def test_plan_rangi_i_budzet(tmp_path):
    fitz = pytest.importorskip("fitz")
    m = dokument.wczytaj(_pdf_dk(tmp_path, fitz), str(tmp_path / "rob"))
    pl = dokument.plan(m)
    rodz = [n["k"] for n in pl["nosniki"]]
    assert rodz == ["kpi", "tab", "lista", "kv", "faq"]
    assert [n["ranga"] for n in pl["nosniki"]] == [0, 0, 0, 0, 4]                              # rozdział „Podsumowanie” = ranga 0 (cały); FAQ 4
    assert pl["min"] == 4 and pl["dom"] == 4 and pl["max"] >= 6
    assert [n["wybrany"] for n in pl["nosniki"]] == [1, 1, 1, 1, 0]
    assert pl["nosniki"][3]["pominiete"][0]["k"] == "faq"                                   # pominięty nośnik idzie do notatek poprzedniego
    s = dokument.statystyka(m)
    assert s["slajdy_min"] == 4 and s["na_slajdach"]["min"] < s["na_slajdach"]["max"]


def test_zloz_notatki_bramki_i_pojemniki(tmp_path, monkeypatch):
    fitz = pytest.importorskip("fitz")
    m = dokument.wczytaj(_pdf_dk(tmp_path, fitz), str(tmp_path / "rob"))
    s = dokument.statystyka(m)
    spec = dokument.zloz(m, {"slajdy": s["slajdy_max"], "rozdzialy": 0, "wyjscie": str(tmp_path)})
    typy = [sl["type"] for sl in spec["slides"]]
    assert typy[0] == "cover_text" and typy[-1] == "end" and spec["slides"][0]["kicker"] == "PRZEGLAD DLA ZARZADU"
    assert spec["slides"][0]["subtitle"].startswith("Oprogramowanie, ktore wspiera") and "21 pazdziernika 2026" in spec["slides"][0]["meta"]
    assert spec["ustawienia"]["slajdy"] <= s["slajdy_max"]
    tab = next(sl for sl in spec["slides"] if sl["type"] == "table")
    assert len(tab["head"]) == 4 and tab["head"][:2] == ["PROGRAM", "PRZEZNACZENIE"]
    for r in tab["rows"]:
        for c in r:
            assert dokument._konc_ok(c.split()) or not c, c                                  # bez zawieszki na końcu komórki
    assert len({r[0] for r in tab["rows"]}) == len(tab["rows"])                              # nazwy wierszy nie powtarzają się
    for sl in spec["slides"]:
        if sl["type"] == "uklad":
            for r in sl["rows"]:
                if r.get("k") == "band":
                    assert dokument._slow(r["t"]) <= dokument.PAS_MAX
                for it in (r.get("items") or []):
                    if it.get("fill") == "brand":
                        assert dokument._slow(it["blocks"][0]["t"]) <= dokument.ZIELONA_MAX
    assert all(sl.get("notes") for sl in spec["slides"] if sl["type"] in ("uklad", "table", "cover_text"))
    pptx = _zbuduj(spec, tmp_path, monkeypatch)
    pok = dokument.pokrycie(m, pptx, spec["mapa_blokow"])
    assert pok["tekst"].startswith("Treść: 100%") and 0 < pok["na_slajdach"] < 100


def test_fraza_i_czlon_nie_koncza_sie_zawieszka():
    assert dokument._fraza("Katalog materialow marki z dysku firmowego M: wyszukiwanie, powiazania", 7) == "Katalog materialow marki z dysku firmowego M"
    assert dokument._fraza("zrzuty ekranow porownywane z projektem i design systemem marki", 7) == "zrzuty ekranow porownywane z projektem i design systemem marki"   # cały tekst do 9 słów
    assert dokument._fraza("zrzuty ekranow porownywane z projektem i design systemem marki na stronie", 7) is None            # pierwsza fraza > 7 słów
    assert dokument._czlon("zrzuty ekranow porownywane z projektem i design systemem marki na stronie", 7) == "zrzuty ekranow porownywane z projektem"
    assert dokument._czlon("interfejs programow (okno aplikacji z silnikiem przegladarki Windows) i reszta zdania tutaj", 7) == "interfejs programow"
    assert dokument._fraza("K. Wieczorek, IOD / prawnik", 7, min_sl=2) == "K. Wieczorek"
    assert dokument._fraza("Oprogramowanie, ktore wspiera prace marketingu: do czego sluzy", 14, min_sl=4) == "Oprogramowanie, ktore wspiera prace marketingu"
    for t in ("Powtarzalne zadania w minutach zamiast godzin: zdjecia, prezentacje.", "Dodatkowa kontrola opakowan przed drukiem."):
        h, d = dokument._haslo_poz(t)
        assert dokument._slow(h) <= 7 and dokument._konc_ok(h.split())
    assert dokument._haslo_poz("Dodatkowa kontrola opakowan przed drukiem.") == ("Dodatkowa kontrola opakowan przed drukiem", None)


def test_ksztalt_tabeli_dobiera_pojemnik():
    assert dokument._ksztalt_tabeli([["PROGRAM", "TESTY"], ["DAM", "ponad 1 900"], ["Photo Resizer", "534"], ["Stworz", "360"]]) == ("kpi", 1)
    assert dokument._ksztalt_tabeli([["ZAGROZENIE", "CHRONI?"], ["podsluch", "tak"], ["podszycie", "czesciowo"], ["haslo", "nie"]]) == ("taknie", 1)
    assert dokument._ksztalt_tabeli([["PROGRAM", "OKRES"], ["DAM", "od marca 2026, ok. 7 miesiecy"], ["Resizer", "od lipca 2026, ok. 3 miesiace"], ["Ankiety", "od wrzesnia 2026"]]) == ("czas", 1)
    assert dokument._ksztalt_tabeli([["A", "B"], ["x", "krotka wartosc"], ["y", "inna wartosc"]]) == ("kv", 1)
    assert dokument._ksztalt_tabeli([["A", "B", "C"], ["x", "opis dluzszy niz cztery slowa w komorce", "z"], ["y", "inny opis dluzszy niz cztery slowa", "w"]]) == ("tab", None)


RAPORT = r"C:\Users\krzysztof.wieczorek\AppData\Local\Temp\claude-tmp\2026-10-21-prezentacje-test\wejscie.pdf"


@pytest.mark.skipif(not os.path.isfile(RAPORT), reason="lokalny raport dla zarządu (dane firmy) - test tylko na komputerze autora")
def test_raport_dla_zarzadu_lokalnie(tmp_path):
    """Raport z 21.10.2026 (11 stron, 146 slajdów w wersji 1.2.3): dziś 13 / 16 / ok. 48 slajdów, bez logo z PDF, decyzje zarządu zawsze."""
    pytest.importorskip("fitz")
    m = dokument.wczytaj(RAPORT, str(tmp_path / "rob"))
    s = dokument.statystyka(m)
    assert m["tytul"].upper().startswith("NARZĘDZIA CYFROWE") and s["obrazy"] == 0 and s["tabele"] >= 9
    assert 10 <= s["slajdy_min"] <= 14 and 14 <= s["slajdy_domyslnie"] <= 18 and s["slajdy_max"] <= 60
    pl = dokument.plan(m)
    tyt = [n["tytul"] for n in pl["nosniki"] if n["wybrany"]]
    assert any("DECYZJE" in (t or "").upper() for t in tyt) and any("PLAN DZIAŁAŃ" in (t or "").upper() for t in tyt)
    pl_min = dokument.plan(m, s["slajdy_min"])
    assert any("DECYZJE" in (n["tytul"] or "").upper() for n in pl_min["nosniki"] if n["wybrany"])
    spec = dokument.zloz(m, {"wyjscie": str(tmp_path)})
    assert spec["ustawienia"]["slajdy"] == s["slajdy_domyslnie"] and spec["slides"][0]["type"] == "cover_text"
    for sl in spec["slides"]:
        txt = dokument._tekst_pokazany(sl)
        if sl["type"] == "table":
            for r in sl["rows"]:
                assert all(dokument._konc_ok(c.split()) for c in r if c), r
            assert len({r[0] for r in sl["rows"]}) == len(sl["rows"]), sl["title"]
        if sl["type"] == "uklad":
            for r in sl["rows"]:
                if r.get("k") == "band":
                    assert dokument._slow(r["t"]) <= dokument.PAS_MAX
