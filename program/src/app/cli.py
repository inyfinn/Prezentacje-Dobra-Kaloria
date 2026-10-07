# -*- coding: utf-8 -*-
"""Wiersz poleceń programu "Stwórz prezentację" - dla AI (Claude, GPT, Gemini, Antigravity) i skryptów.

    stworz-cli.exe "<folder produktu>" [--styl nowy|stary] [--dlugosc krotka|standard|pelna]
                   [--tekst mniej|standard|wiecej] [--sekcje okladka,smaki,...] [--film <link YouTube>]
                   [--claimy "Claim 1; Claim 2 – opis"] [--wyjscie <katalog>] [--bez-qa] [--json] [--tylko-analiza]
    stworz-cli.exe "<gotowa prezentacja.pptx>" [--cel wiernie|rozwin|skroc] [--sekcje r01,r02,...] [--slajdy N]
                   [--dodaj t10,t58] [--bez-wizualizacji] [--wyjscie <katalog>] [--bez-qa] [--json] [--tylko-analiza]
        konwersja gotowej prezentacji na styl DK, slajd w slajd: te same teksty, kolejność i układ; cały tekst, tabele,
        wykresy i obrazy zostają; program sprawdza pokrycie treści i układ. --cel: wiernie (domyślnie), rozwin (baza +
        puste slajdy z --dodaj), skroc (baza do skrócenia). Rozdziały spoza --sekcje zostają w pliku jako slajdy UKRYTE.
        Wynik: "<nazwa> - nowy styl.pptx" (rozwin: "… - rozwinięta", skroc: "… - skrót") obok pliku albo w --wyjscie.
Kod wyjścia 0 = gotowe. Raport także w <folder>\\_robocze\\raport.json (konwersja: <folder>\\_robocze\\<nazwa>\\raport.json).
"""
import argparse
import ctypes
import json
import os
import sys


def _attach_console():
    """Wersja okienkowa (.exe bez konsoli) uruchomiona z terminala: podłącz się do konsoli rodzica, żeby AI widziało wynik."""
    if sys.stdout is not None:
        return
    try:
        if ctypes.windll.kernel32.AttachConsole(-1):
            sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace", buffering=1)
            sys.stderr = sys.stdout
    except Exception:
        pass


def main(argv=None):
    _attach_console()
    if sys.stdout is not None and not sys.stdout.isatty():
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(prog="stworz-cli", description="Stwórz prezentację Dobra Kaloria z folderu produktu.")
    ap.add_argument("folder", help="folder produktu (karty wprowadzenia, copy, Wizualizacje, Elementy) ALBO gotowa "
                                   "prezentacja .pptx do przełożenia na styl DK")
    ap.add_argument("--styl", choices=["nowy", "stary"], default="nowy")
    ap.add_argument("--dlugosc", choices=["krotka", "standard", "pelna"], default="standard")
    ap.add_argument("--tekst", choices=["mniej", "standard", "wiecej"], default="standard")
    ap.add_argument("--sekcje", default="", help="lista id sekcji po przecinku (nadpisuje --dlugosc); "
                                                 "dla .pptx: id rozdziałów r01,r02... widocznych w pokazie - "
                                                 "pozostałe zostają w pliku jako slajdy ukryte")
    ap.add_argument("--cel", choices=["wiernie", "rozwin", "skroc"], default="wiernie",
                    help="tylko .pptx: wiernie = ten sam slajd w nowym wyglądzie; rozwin = baza do dokończenia "
                         "(z --dodaj); skroc = baza do skrócenia (z --sekcje i --slajdy)")
    ap.add_argument("--slajdy", type=int, default=0, help="tylko .pptx, cel skroc: ile slajdów ma zostać w pokazie")
    ap.add_argument("--dodaj", default="", help="tylko .pptx, cel rozwin: puste slajdy z szablonu do dołożenia, "
                                                "np. t10,t58 (id z --tylko-analiza)")
    ap.add_argument("--bez-wizualizacji", action="store_true",
                    help="tylko .pptx: nie dokładaj packshotów z biblioteki produktów na slajdach portfolio")
    ap.add_argument("--film", default="", help="link do filmu na YouTube (włącza sekcję film)")
    ap.add_argument("--claimy", default="", help="claimy produktowe rozdzielone średnikiem; 'Tytuł – opis'")
    ap.add_argument("--packshoty", default="", help="ręczne przypisanie packshotów: 'Arbuz=plik.png;Cola=plik2.png'")
    ap.add_argument("--wyjscie", default="", help="katalog na PPTX (domyślnie folder produktu)")
    ap.add_argument("--bez-qa", action="store_true", help="pomiń PowerPoint (czcionki, zrzuty, kontrola tekstu)")
    ap.add_argument("--json", action="store_true", help="na końcu wypisz pełny raport JSON")
    ap.add_argument("--tylko-analiza", action="store_true", help="tylko pokaż, co program znalazł w folderze")
    a = ap.parse_args(argv)
    import engine
    try:
        an = engine.analyze(a.folder)
    except Exception as e:
        print("BŁĄD:", e)
        return 2
    pptx = an.get("tryb") == "pptx"
    if pptx:
        print("Prezentacja: %s | %d slajdów, %d akapitów, %d grafik, %d tabel, %d wykresów | rozdziały: %s"
              % (an["produkt"], an["slajdy"], an["akapity"], an["grafiki"], an["tabele"], an["wykresy"],
                 "; ".join("%s=%s" % (x["id"], x["nazwa"]) for x in an["sekcje"] if x.get("rodzaj") == "pptx")))
        print("Biblioteka wizualizacji: %s" % (an["wizualizacje"]["sciezka"] or "niedostępna"))
    else:
        print("Produkt: %s | smaki: %s | karty: %d | copy: %d akapitów | badania: %s | grafiki: %d packshotów, %d elementów"
              % (an["produkt"], ", ".join(s["nazwa"] for s in an["smaki"]), an["karty"], an["copy_akapity"],
                 ", ".join(an["badania"]) or "brak", an["grafiki"]["packshoty"], an["grafiki"]["elementy"]))
    for u in an["uwagi"]:
        print(" -", u["tekst"])
    if a.tylko_analiza:
        print(json.dumps({k: v for k, v in an.items() if k != "sekcje"}, ensure_ascii=False, indent=1))
        print("Sekcje:", ", ".join("%s%s" % (s["id"], "" if s["dostepna"] else "(brak danych)") for s in an["sekcje"]))
        if pptx:
            print("Puste slajdy do dołożenia (--cel rozwin --dodaj ...):",
                  ", ".join("%s=%s" % (s["id"], s["nazwa"]) for s in an["sekcje"] if s.get("rodzaj") == "szablon"))
        return 0
    if pptx:  # konwersja: domyślnie wszystkie rozdziały; nie ma długości ani ilości tekstu - treść zawsze w całości
        sekcje = [s.strip() for s in a.sekcje.split(",") if s.strip()] or \
            [s["id"] for s in an["sekcje"] if s.get("rodzaj") == "pptx"]
        if a.cel == "rozwin":  # puste slajdy z szablonu (t10, t58...) idą tą samą listą co rozdziały
            sekcje += [s.strip() for s in a.dodaj.split(",") if s.strip()]
        opts = {"styl": a.styl, "sekcje": sekcje, "wyjscie": a.wyjscie or None, "bez_qa": a.bez_qa, "cel": a.cel,
                "cel_slajdy": a.slajdy, "wizualizacje": not a.bez_wizualizacji,
                "szacowany_czas_s": an["szacowany_czas_s"]}
        return _run(engine, an, opts, a)
    dl = {"krotka": 0, "standard": 1, "pelna": 2}[a.dlugosc]
    sekcje = [s.strip() for s in a.sekcje.split(",") if s.strip()] or [s["id"] for s in an["sekcje"]
                                                                       if s["dostepna"] and s["id"] in engine.LENGTH_PRESETS[dl]]
    if a.film and "film" not in sekcje:
        sekcje.append("film")
    opts = {"styl": a.styl, "dlugosc": dl, "tekst": {"mniej": 0, "standard": 1, "wiecej": 2}[a.tekst],
            "sekcje": sekcje, "film": a.film, "claimy": a.claimy, "wyjscie": a.wyjscie or None, "bez_qa": a.bez_qa,
            "szacowany_czas_s": an["szacowany_czas_s"],
            "packshoty": dict(x.split("=", 1) for x in a.packshoty.split(";") if "=" in x)}
    return _run(engine, an, opts, a)


def _run(engine, an, opts, a):
    last = [""]

    def progress(step, opis, pct, eta):
        line = "[%3d%%] %s" % (pct, opis)
        if line != last[0]:
            print(line, flush=True)
            last[0] = line

    res = engine.safe_build(an.get("plik") or an["folder"], opts, progress=progress,  # konwersja: ścieżką jest plik .pptx
                            log=lambda t: print("   ", t, flush=True))
    if not res.get("ok"):
        print("BŁĄD:", res.get("blad"))
        if res.get("traceback"):
            print(res["traceback"])
        return 1
    print("\nGOTOWE: %s (%d slajdów, %d s)" % (res["pptx"], res["slajdy"], res["czas_s"]))
    if res.get("tryb") == "pptx":
        print("Cel: %s | ukryte slajdy: %d | nowe slajdy z szablonu: %d" % (res["cel_nazwa"], res["ukryte"], len(res["nowe"])))
    q = res["qa"]
    if q["wykonano"]:
        print("Kontrola tekstu w PowerPoint: %s" % ("0 problemów" if q["problemy"] == 0 else "%d problemów" % q["problemy"]))
        for s in q["szczegoly"]:
            print("   ", s)
    for u in res["uwagi"]:
        print(" - " + u)
    print("Raport: %s" % (res.get("raport") or os.path.join(res["folder"], "_robocze", "raport.json")))
    if a.json:
        print(json.dumps({k: v for k, v in res.items() if k != "miniatury"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
