# -*- coding: utf-8 -*-
"""Wiersz poleceń programu "Stwórz prezentację" - dla AI (Claude, GPT, Gemini, Antigravity) i skryptów.

    stworz-cli.exe "<folder produktu>" [--styl nowy|stary] [--dlugosc krotka|standard|pelna]
                   [--tekst mniej|standard|wiecej] [--sekcje okladka,smaki,...] [--film <link YouTube>]
                   [--claimy "Claim 1; Claim 2 – opis"] [--wyjscie <katalog>] [--bez-qa] [--json] [--tylko-analiza]
Kod wyjścia 0 = gotowe. Raport także w <folder>\\_robocze\\raport.json.
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
    ap.add_argument("folder", help="folder produktu (karty wprowadzenia, copy, Wizualizacje, Elementy)")
    ap.add_argument("--styl", choices=["nowy", "stary"], default="nowy")
    ap.add_argument("--dlugosc", choices=["krotka", "standard", "pelna"], default="standard")
    ap.add_argument("--tekst", choices=["mniej", "standard", "wiecej"], default="standard")
    ap.add_argument("--sekcje", default="", help="lista id sekcji po przecinku (nadpisuje --dlugosc)")
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
    print("Produkt: %s | smaki: %s | karty: %d | copy: %d akapitów | badania: %s | grafiki: %d packshotów, %d elementów"
          % (an["produkt"], ", ".join(s["nazwa"] for s in an["smaki"]), an["karty"], an["copy_akapity"],
             ", ".join(an["badania"]) or "brak", an["grafiki"]["packshoty"], an["grafiki"]["elementy"]))
    for u in an["uwagi"]:
        print(" -", u["tekst"])
    if a.tylko_analiza:
        print(json.dumps({k: v for k, v in an.items() if k != "sekcje"}, ensure_ascii=False, indent=1))
        print("Sekcje:", ", ".join("%s%s" % (s["id"], "" if s["dostepna"] else "(brak danych)") for s in an["sekcje"]))
        return 0
    dl = {"krotka": 0, "standard": 1, "pelna": 2}[a.dlugosc]
    sekcje = [s.strip() for s in a.sekcje.split(",") if s.strip()] or [s["id"] for s in an["sekcje"]
                                                                       if s["dostepna"] and s["id"] in engine.LENGTH_PRESETS[dl]]
    if a.film and "film" not in sekcje:
        sekcje.append("film")
    opts = {"styl": a.styl, "dlugosc": dl, "tekst": {"mniej": 0, "standard": 1, "wiecej": 2}[a.tekst],
            "sekcje": sekcje, "film": a.film, "claimy": a.claimy, "wyjscie": a.wyjscie or None, "bez_qa": a.bez_qa,
            "szacowany_czas_s": an["szacowany_czas_s"],
            "packshoty": dict(x.split("=", 1) for x in a.packshoty.split(";") if "=" in x)}
    last = [""]

    def progress(step, opis, pct, eta):
        line = "[%3d%%] %s" % (pct, opis)
        if line != last[0]:
            print(line, flush=True)
            last[0] = line

    res = engine.safe_build(an["folder"], opts, progress=progress, log=lambda t: print("   ", t, flush=True))
    if not res.get("ok"):
        print("BŁĄD:", res.get("blad"))
        if res.get("traceback"):
            print(res["traceback"])
        return 1
    print("\nGOTOWE: %s (%d slajdów, %d s)" % (res["pptx"], res["slajdy"], res["czas_s"]))
    q = res["qa"]
    if q["wykonano"]:
        print("Kontrola tekstu w PowerPoint: %s" % ("0 problemów" if q["problemy"] == 0 else "%d problemów" % q["problemy"]))
        for s in q["szczegoly"]:
            print("   ", s)
    for u in res["uwagi"]:
        print(" - " + u)
    print("Raport: %s" % os.path.join(res["folder"], "_robocze", "raport.json"))
    if a.json:
        print(json.dumps({k: v for k, v in res.items() if k != "miniatury"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
