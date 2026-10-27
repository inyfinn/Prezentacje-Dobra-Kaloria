# -*- coding: utf-8 -*-
"""Wiersz poleceń programu "Stwórz prezentację" - dla AI (Claude, GPT, Gemini, Antigravity) i skryptów.

    stworz-cli.exe "<folder produktu>" [--styl nowy|stary] [--dlugosc krotka|standard|pelna]
                   [--tekst mniej|standard|wiecej] [--sekcje okladka,smaki,...] [--film <link YouTube>]
                   [--claimy "Claim 1; Claim 2 – opis"] [--wyjscie <katalog>] [--bez-qa] [--json] [--tylko-analiza]
    stworz-cli.exe "<gotowa prezentacja.pptx>" [--cel wiernie|rozwin|skroc] [--sekcje r01,r02,...] [--slajdy N]
                   [--dodaj t10,t58] [--bez-wizualizacji] [--wyjscie <katalog>] [--robocze <katalog>] [--bez-qa]
                   [--bez-oka] [--json] [--tylko-analiza]
        konwersja gotowej prezentacji na styl DK, slajd w slajd: te same teksty, kolejność i układ; cały tekst, tabele,
        wykresy i obrazy zostają; program sprawdza pokrycie treści i układ. --cel: wiernie (domyślnie), rozwin (baza +
        puste slajdy z --dodaj), skroc (baza do skrócenia). Rozdziały spoza --sekcje zostają w pliku jako slajdy UKRYTE.
        Wynik: "<nazwa> - nowy styl.pptx" (rozwin: "… - rozwinięta", skroc: "… - skrót") obok pliku albo w --wyjscie.
        Po budowie program "ogląda" zrzuty slajdów (render w PowerPoint), zmienia układ slajdów z usterkami wyglądu
        (pusty dół, puste karty, tekst przy krawędzi…) i buduje ponownie, najwyżej 2 rundy; --bez-oka wyłącza tę pętlę.
        Podfolder "plansze" obok wyniku: obrazy slajdów (6 na planszę) do dołączenia w czacie bez dostępu do plików.
        Raport (raport.json) ma gotowe polecenia dla AI: prompt_agent (agent z plikami) i prompt_ai (czat bez plików).
    stworz-cli.exe "<dokument .docx|.doc|.rtf|.odt|.pdf|.txt|.md>" [--slajdy N] [--rozdzialy N] [--wyjscie <katalog>]
                   [--robocze <katalog>] [--bez-qa] [--bez-oka] [--json] [--tylko-analiza]
        prezentacja z dokumentu: nagłówki i akapity stają się slajdami w stylu marki (hasła, liczby, wnioski), bez gubienia
        i bez wymyślania treści. --slajdy N: ile slajdów (domyślnie wg dokumentu; zakres wypisuje --tylko-analiza),
        --rozdzialy N: ile przekładek rozdziałów (0 = bez przekładek). Folder z JEDNYM takim plikiem (bez kart wprowadzenia)
        też działa. Folder programu jest odrzucany z komunikatem (kod 2).
    stworz-cli.exe "<prezentacja .pptx już w stylu marki: szablon DK, wynik programu, zrobiona z szablonu>" [--robocze <katalog>]
                   [--bez-qa] [--json] [--tylko-analiza]
        DOPRACOWANIE (program sam rozpoznaje taki plik): niczego nie buduje i nie zmienia pliku. Robi przegląd: liczy podpowiedzi
        w [nawiasach] i możliwe błędy tekstu, robi zrzuty i kontrolę tekstu w PowerPoint na KOPII w katalogu roboczym, ocenia
        wygląd zrzutów („Sprawdź najpierw: slajd N…”), robi plansze (<robocze>\\plansze) i zapisuje dwa polecenia dla AI
        (raport.json: prompt_agent, prompt_ai) z celem „dopracuj prezentację w stylu DK”. Plik z folderu programu (np. szablon)
        też jest dopracowaniem - program nic tam nie zapisuje. --mimo-to: skonwertuj taki plik jak obcą prezentację.
    stworz-cli.exe "<folder prezentacji>" --scenariusz "<folder>\\scenariusz.md" [--wyjscie <folder>] [--bez-qa] [--bez-oka] [--json]
        budowa ze SCENARIUSZA (Markdown od AI, wzór: skill\\assets\\scenariusz-wzor.md): jeden nagłówek ## = jeden slajd, 1:1. Najpierw
        kontrola scenariusza (linie „BŁĄD” trzeba poprawić w pliku i zbudować jeszcze raz, „uwaga” to wskazówki), potem budowa i te same
        kontrole co przy dokumencie. Wynik: "<tytuł>.pptx" (kolejne: "<tytuł> v2.pptx"…) w folderze prezentacji, obok "_robocze" i "plansze".
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
    ap.add_argument("folder", nargs="?", default="",
                    help="folder produktu (karty wprowadzenia, copy, Wizualizacje, Elementy) ALBO gotowa "
                         "prezentacja .pptx do przełożenia na styl DK; z --scenariusz: folder prezentacji")
    ap.add_argument("--scenariusz", default="", help="plik scenariusza (.md): buduje prezentację ze scenariusza do folderu prezentacji "
                                                     "(domyślnie folder tego pliku)")
    ap.add_argument("--styl", choices=["nowy", "stary"], default="nowy")
    ap.add_argument("--dlugosc", choices=["krotka", "standard", "pelna"], default="standard")
    ap.add_argument("--tekst", choices=["mniej", "standard", "wiecej"], default="standard")
    ap.add_argument("--sekcje", default="", help="lista id sekcji po przecinku (nadpisuje --dlugosc); "
                                                 "dla .pptx: id rozdziałów r01,r02... widocznych w pokazie - "
                                                 "pozostałe zostają w pliku jako slajdy ukryte")
    ap.add_argument("--cel", choices=["wiernie", "rozwin", "skroc"], default="wiernie",
                    help="tylko .pptx: wiernie = ten sam slajd w nowym wyglądzie; rozwin = baza do dokończenia "
                         "(z --dodaj); skroc = baza do skrócenia (z --sekcje i --slajdy)")
    ap.add_argument("--slajdy", type=int, default=0, help="dokument: ile slajdów; .pptx, cel skroc: ile slajdów ma zostać w pokazie")
    ap.add_argument("--dodaj", default="", help="tylko .pptx, cel rozwin: puste slajdy z szablonu do dołożenia, "
                                                "np. t10,t58 (id z --tylko-analiza)")
    ap.add_argument("--bez-wizualizacji", action="store_true",
                    help="tylko .pptx: nie dokładaj packshotów z biblioteki produktów na slajdach portfolio")
    ap.add_argument("--film", default="", help="link do filmu na YouTube (włącza sekcję film)")
    ap.add_argument("--claimy", default="", help="claimy produktowe rozdzielone średnikiem; 'Tytuł – opis'")
    ap.add_argument("--packshoty", default="", help="ręczne przypisanie packshotów: 'Arbuz=plik.png;Cola=plik2.png'")
    ap.add_argument("--wyjscie", default="", help="katalog na PPTX (domyślnie folder produktu)")
    ap.add_argument("--robocze", default="", help="tylko .pptx: katalog roboczy konwersji (raport.json, spec, zrzuty, obrazy "
                                                  "z oryginału); domyślnie <folder pliku>\\_robocze\\<nazwa>")
    ap.add_argument("--rozdzialy", type=int, default=-1,
                    help="tylko dokument: ile przekładek rozdziałów (0 = bez przekładek; domyślnie wg dokumentu)")
    ap.add_argument("--mimo-to", action="store_true",
                    help="tylko .pptx: skonwertuj jak obcą także prezentację, którą program uznał za już gotową w stylu Dobra "
                         "Kaloria (szablon, wynik programu); domyślnie taki plik tylko sprawdza (dopracowanie)")
    ap.add_argument("--bez-oka", action="store_true",
                    help="tylko .pptx: nie poprawiaj układu po obejrzeniu zrzutów (domyślnie program ocenia zrzuty slajdów "
                         "i zmienia układ slajdów z usterkami wyglądu)")
    ap.add_argument("--bez-qa", action="store_true", help="pomiń PowerPoint (czcionki, zrzuty, kontrola tekstu)")
    ap.add_argument("--json", action="store_true", help="na końcu wypisz pełny raport JSON")
    ap.add_argument("--tylko-analiza", action="store_true", help="tylko pokaż, co program znalazł w folderze")
    a = ap.parse_args(argv)
    import engine
    if a.scenariusz:
        return _scenariusz(engine, a)
    if not a.folder:
        ap.error("podaj folder produktu, plik albo --scenariusz")
    engine.set_robocze(a.robocze)
    try:
        an = engine.analyze(a.folder, mimo_to=a.mimo_to)
    except Exception as e:
        print("BŁĄD:", e)
        return 2
    if an.get("tryb") == "scenariusz":      # folder prezentacji z gotowym scenariuszem: najnowszy scenariusz
        a.scenariusz = an["scenariusz"]
        return _scenariusz(engine, a)
    if an.get("tryb") == "pakiet":          # folder prezentacji bez scenariusza: Źródła zamieniane na prezentację jak dokument
        sw = an["suwaki"]
        print("Folder prezentacji: %s | pliki ze Źródeł: %s | slajdy: %d-%d (domyślnie %d)" % (
            an["nazwa_folderu"], ", ".join(x["nazwa"] for x in an["pliki"]) or "brak", sw["slajdy"]["min"], sw["slajdy"]["max"], sw["slajdy"]["domyslnie"]))
        for u in an["uwagi"]:
            print(" -", u)
        if a.tylko_analiza:
            return 0
        opts = {"slajdy": a.slajdy or None, "rozdzialy": None if a.rozdzialy < 0 else a.rozdzialy, "bez_qa": a.bez_qa,
                "oko": not a.bez_oka, "szacowany_czas_s": an["szacowany_czas_s"]}
        return _run(engine, an, opts, a)
    pptx = an.get("tryb") == "pptx"
    dok = an.get("tryb") == "dokument"
    dopr = an.get("tryb") == "dopracowanie"
    if dopr:
        print("Dopracowanie: %s | %d slajdów, podpowiedzi w [nawiasach]: %d, możliwe błędy tekstu: %d | spec: %s"
              % (an["produkt"], an["slajdy"], an["podpowiedzi"], an["bledy_tekstu_liczba"], an.get("spec") or "brak"))
    elif dok:
        sw = an["suwaki"]
        print("Dokument: %s | %d słów, %d akapitów, nagłówki: %s, %d tabel, %d obrazów | slajdy: %d-%d (domyślnie %d), "
              "przekładki rozdziałów: 0-%d (domyślnie %d)"
              % (an["produkt"], an["slowa"], an["akapity"], ", ".join("%s:%s" % kv for kv in sorted(an["naglowki"].items())) or "brak",
                 an["tabele"], an["obrazy"], sw["slajdy"]["min"], sw["slajdy"]["max"], sw["slajdy"]["domyslnie"],
                 sw["rozdzialy"]["max"], sw["rozdzialy"]["domyslnie"]))
    elif pptx:
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
        if dok or dopr:
            return 0
        print("Sekcje:", ", ".join("%s%s" % (s["id"], "" if s["dostepna"] else "(brak danych)") for s in an["sekcje"]))
        if pptx:
            print("Puste slajdy do dołożenia (--cel rozwin --dodaj ...):",
                  ", ".join("%s=%s" % (s["id"], s["nazwa"]) for s in an["sekcje"] if s.get("rodzaj") == "szablon"))
        return 0
    if dok:
        opts = {"slajdy": a.slajdy or None, "rozdzialy": None if a.rozdzialy < 0 else a.rozdzialy, "wyjscie": a.wyjscie or None,
                "bez_qa": a.bez_qa, "oko": not a.bez_oka, "szacowany_czas_s": an["szacowany_czas_s"]}
        return _run(engine, an, opts, a)
    if dopr:  # plik w stylu marki: bez rozdziałów, celu i suwaków - sam przegląd
        opts = {"wyjscie": None, "bez_qa": a.bez_qa, "szacowany_czas_s": an["szacowany_czas_s"]}
        return _run(engine, an, opts, a)
    if pptx:  # konwersja: domyślnie wszystkie rozdziały; nie ma długości ani ilości tekstu - treść zawsze w całości
        sekcje = [s.strip() for s in a.sekcje.split(",") if s.strip()] or \
            [s["id"] for s in an["sekcje"] if s.get("rodzaj") == "pptx"]
        if a.cel == "rozwin":  # puste slajdy z szablonu (t10, t58...) idą tą samą listą co rozdziały
            sekcje += [s.strip() for s in a.dodaj.split(",") if s.strip()]
        opts = {"styl": a.styl, "sekcje": sekcje, "wyjscie": a.wyjscie or None, "bez_qa": a.bez_qa, "cel": a.cel,
                "cel_slajdy": a.slajdy, "wizualizacje": not a.bez_wizualizacji, "oko": not a.bez_oka, "mimo_to": a.mimo_to,
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


def _scenariusz(engine, a):
    """--scenariusz: kontrola pliku scenariusza, potem budowa 1:1 w folderze prezentacji (wynik i _robocze zawsze tam)."""
    sc = os.path.abspath(a.scenariusz)
    if not os.path.isfile(sc):
        print("BŁĄD: Nie znalazłem scenariusza:", sc)
        return 2
    folder = os.path.abspath(a.folder) if a.folder else os.path.dirname(sc)
    if not os.path.isdir(folder):
        print("BŁĄD: Nie znalazłem folderu prezentacji:", folder)
        return 2
    try:
        S = engine.scenariusz_modul()
        k = S.sprawdz(engine._czytaj_scenariusz(sc), folder, a.slajdy or None)
    except (ValueError, OSError) as e:
        print("BŁĄD:", e)
        return 2
    print("Scenariusz: %s | tytuł: %s | slajdów z treścią: %d, przekładek: %d" % (os.path.basename(sc), k["tytul"] or "brak", k["slajdy"], k["rozdzialy"]))
    for u in k["uwagi"]:
        print(" - uwaga:", u)
    for b in k["bledy"]:
        print("BŁĄD:", b)
    if not k["ok"]:
        return 1
    if a.tylko_analiza:
        print(json.dumps(k, ensure_ascii=False, indent=1))
        return 0
    opts = {"scenariusz": sc, "wyjscie": folder, "bez_qa": a.bez_qa, "oko": not a.bez_oka, "slajdy": a.slajdy or None,
            "szacowany_czas_s": engine._czas_slajdow(k["slajdy"])}
    return _run(engine, {"folder": folder}, opts, a)


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
    if res.get("tryb") == "dopracowanie":
        print("\nSPRAWDZONE: %s (%d slajdów, %d s); plik %s" % (res["pptx"], res["slajdy"], res["czas_s"],
                                                           "nie został zmieniony" if res.get("plik_bez_zmian") else "ZMIENIŁ SIĘ w trakcie sprawdzania"))
    else:
        print("\nGOTOWE: %s (%d slajdów, %d s)" % (res["pptx"], res["slajdy"], res["czas_s"]))
    if res.get("tryb") in ("pptx", "dokument", "dopracowanie", "scenariusz"):
        if res["tryb"] == "scenariusz":
            print("Ze scenariusza %s | suwaki: slajdy z treścią %s, przekładki %s" % (
                os.path.basename(res["scenariusz"]), res["suwaki"]["slajdy"], res["suwaki"]["rozdzialy"]))
        elif res["tryb"] == "pptx":
            print("Cel: %s | ukryte slajdy: %d | nowe slajdy z szablonu: %d" % (res["cel_nazwa"], res["ukryte"], len(res["nowe"])))
        elif res["tryb"] == "dokument":
            print("Z dokumentu | suwaki: slajdy %s, przekładki rozdziałów %s" % (res["suwaki"]["slajdy"], res["suwaki"]["rozdzialy"]))
        else:
            print("Dopracowanie | podpowiedzi w [nawiasach]: %d | spec: %s | kopia do renderu: %s" % (
                res["podpowiedzi"], res.get("spec") or "brak", res["kopia_przegladu"]))
        ok = res.get("oko") or {}
        if ok.get("uruchomione"):
            print("Oko programu: rundy %d, zmieniony układ slajdów: %s, cofnięte: %s, usterki do sprawdzenia: %d (%d s)" % (
                ok["rundy"], ", ".join(str(n) for n in ok["zmienione"]) or "-", ", ".join(str(n) for n in ok["odrzucone"]) or "-",
                len(ok["pozostale"]), ok["czas_s"]))
        if res.get("plansze"):
            print("Plansze dla czatu (%d): %s" % (len(res["plansze"]), res["plansze_folder"]))
    q = res["qa"]
    if q["wykonano"]:
        print("Kontrola tekstu w PowerPoint: %s" % ("0 problemów" if q["problemy"] == 0 else "%d problemów" % q["problemy"]))
        for s in q["szczegoly"]:
            print("   ", s)
    for u in res.get("uwagi_pelne") or res["uwagi"]:   # pełne brzmienie (okno dostaje krótszą listę w res["uwagi"])
        print(" - " + u)
    print("Raport: %s" % (res.get("raport") or os.path.join(res["folder"], "_robocze", "raport.json")))
    if a.json:
        print(json.dumps({k: v for k, v in res.items() if k != "miniatury"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
