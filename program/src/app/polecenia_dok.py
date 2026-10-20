# -*- coding: utf-8 -*-
"""Polecenia dla AI po zrobieniu prezentacji Z DOKUMENTU (docx, pdf, txt…) - cel "dokument".

Od v15 (13.10.2026) teksty celów "dokument" i "dopracowanie" są w skillu (`polecenia.py`: POLECENIA["dokument"],
punkty_dopracowanie, pracuj_na, FORMAT_DOPRACOWANIE). Na końcu tego pliku nazwy są podmieniane na te ze skilla; teksty
niżej to ZAPAS dla starszej kopii skilla (np. WORK\\src\\skill przed build.ps1) - nie rozwijaj ich, zmiany rób w skillu.
Punkty wspólne i P1-P6 pochodzą z `polecenia.py`
(jedno źródło metody: references\\dopracowanie.md), tu zmienione są tylko te, które zakładają oryginalną prezentację
(„slajd N = slajd N”, render oryginału, plansze par stary | nowy).
"""
import polecenia as P

OPIS = ("Prezentacja z dokumentu: slajdy w stylu marki z tych samych słów, w kolejności dokumentu. "
        "Liczbę slajdów i przekładek ustawia człowiek suwakiem.")

TRESC = ("TREŚĆ Z DOKUMENTU, NIC WIĘCEJ: slajdy powstały z dokumentu, w jego kolejności. Wszystkie słowa, liczby i znaki "
         "dokumentu zostają; żadnych własnych tytułów, haseł, wniosków ani liczb (tytuł slajdu = nagłówek z dokumentu); "
         "nie łącz i nie dziel sekcji w środku zdania; obrazy w całości; słowa wyróżnione przez autora zostają wyróżnione. "
         "Liczbę slajdów i przekładek rozdziałów ustawił człowiek suwakiem - nie zmieniaj jej (wyjątek: slajd, na którym "
         "treść nie mieści się pismem 13 pt - wtedy podziel go i zgłoś w DO DECYZJI).")

P4 = ("PĘTLA: obejrzyj KAŻDĄ planszę z folderu „plansze” obok pliku wyniku (wynik_01-06.png…; to zrzuty gotowego pliku, "
      "6 slajdów na planszę) jako obraz. Dla każdego slajdu przejdź 8 pytań z dopracowanie.md pkt 7. Poprawki wpisuj do "
      "spec_konwersja.json (typ „uklad”) i buduj build_dk.py - nigdy ręcznie w PowerPoincie; skryptów programu i skilla nie "
      "edytujesz. Po każdej zmianie wyrenderuj plik (render.ps1), zrób nowe plansze (contact_sheet.py <katalog png> <plik.png> 2) "
      "i obejrzyj je ponownie. Najwyżej 3 podejścia na slajd.")
P5 = ("BRAMKI ODDANIA (wszystkie, z dowodem): verify.ps1 „Tekst - problemy: 0” bez błędu COM; „Treść: 100% akapitów” "
      "(kontrola pokrycia dokumentu: dokument.py); liczba slajdów taka, jaką ustawił człowiek (albo wyższa z powodu "
      "podziału, opisanego w DO DECYZJI); plansze obejrzane po ostatniej zmianie. Bez tych wyników nie pisz, że gotowe.")
P6 = ("RAPORT PO POLSKU, KRÓTKO: plik i liczba slajdów; wyniki bramek; co zmieniłeś względem wersji z programu (slajd -> "
      "wzór z katalogu); poprawione błędy tekstu (slajd: było -> jest); DO DECYZJI. Pracuj sam do bramek: nie pytaj o zgodę na "
      "kolejne kroki, pytaj tylko o rzeczy z listy DO DECYZJI.")

# punkty wspólne: PLAKAT, HASŁOWANIE, NIE DOTYCZY, UKŁAD, [TREŚĆ zamiast „1:1 w treści”], BŁĘDY, TYPOGRAFIA
WSPOLNE = list(P.WSPOLNE[:4]) + [TRESC] + list(P.WSPOLNE[5:])
POLECENIE_DOKUMENT = {
    "nazwa": "Dokument", "sufiks": " - prezentacja", "opis": OPIS,
    "polecenie": WSPOLNE,
    "polecenie_pliki": [P.P1, P.P2, P4, P5, P6],
}


def punkty(pliki=True):
    """Punkty polecenia dla celu "dokument": agent z plikami (P1 + wspólne + P2, P4-P6) albo czat (same wspólne)."""
    c = POLECENIE_DOKUMENT
    return (c["polecenie_pliki"][:1] + c["polecenie"] + c["polecenie_pliki"][1:]) if pliki else list(c["polecenie"])


# ---------------------------------------------------------------------------------------------------------------------------
# Cel "dopracowanie": prezentacja JUŻ w stylu marki (szablon DK, wynik programu, zrobiona z szablonu). Program jej nie
# przekłada i nie zmienia pliku: robi przegląd (zrzuty, kontrola tekstu, podpowiedzi w [nawiasach], błędy tekstu) i daje
# polecenie, które pomoże ją dopracować. Wpis `polecenia.POLECENIA["dopracowanie"]` doda main; silnik bierze go ze skilla,
# gdy się pojawi (engine._punkty_dopracowanie), a te teksty zostają zapasem.
OPIS_DOPRACOWANIE = ("Prezentacja już w stylu marki: program jej nie zmienia, tylko sprawdza (zrzuty, tekst, podpowiedzi "
                     "w [nawiasach]) i przygotowuje polecenie do dopracowania.")

DOPR_TRESC = ("DOPRACOWANIE, NIE PRZEBUDOWA: slajdy już są w stylu marki. Zostaw układ, kolory i czcionki z motywu oraz "
              "liczbę i kolejność slajdów. Poprawiasz tylko to, co widać jako wadę na planszach albo w tekście: sieroty i "
              "zawieszki, pusty dół slajdu, za małe pismo, hasło łamane słowo po słowie, wniosek poza pasem, ikona niepasująca do "
              "treści, błędy tekstu. Nie dopisuj faktów ani liczb; podpowiedzi w [nawiasach] wypełniasz tylko tym, co wynika "
              "z materiałów użytkownika.")
DOPR_PODPOWIEDZI = ("PODPOWIEDZI W [NAWIASACH]: każda to miejsce na treść użytkownika (np. [Tytuł: wniosek z badania]). "
                    "Wypełnij ją tylko wtedy, gdy materiały (tekst prezentacji, dokumenty od użytkownika) podają tę informację; "
                    "czego nie ma, zostaw w nawiasach i wpisz do DO DECYZJI z numerem slajdu. Niczego nie wymyślaj.")
FORMAT_DOPRACOWANIE = (
    "FORMAT ODPOWIEDZI - trzy części, nic poza nimi:\n"
    "   A. BŁĘDY TEKSTU - tabela: slajd | było | jest | powód. Tylko ewidentne (punkt o błędach). Na końcu jedno zdanie:\n"
    "      „W PowerPoincie: Ctrl+H, wpisz „było”, zamień na „jest”.”\n"
    "   B. SLAJDY DO POPRAWY - tylko slajdy z wadami (z tekstu albo z plansz): numer | co jest nie tak | gotowy poprawiony tekst\n"
    "      pól. Dla podpowiedzi w [nawiasach]: numer | podpowiedź | proponowana treść z materiałów albo „brak danych”.\n"
    "      Slajdów dobrych nie wypisuj.\n"
    "   C. DO DECYZJI: wątpliwe słowa, nazwy, liczby, brakujące informacje, slajdy z za dużą ilością treści.")
DOPR_P4 = ("PĘTLA: obejrzyj KAŻDĄ planszę z folderu „plansze” w katalogu roboczym (wynik_01-06.png…; to zrzuty kopii pliku, "
           "6 slajdów na planszę) jako obraz. Dla każdego slajdu przejdź 8 pytań z dopracowanie.md pkt 7. Po każdej zmianie "
           "wyrenderuj poprawiony plik (render.ps1), zrób nowe plansze (contact_sheet.py <katalog png> <plik.png> 2) i obejrzyj "
           "je ponownie. Najwyżej 3 podejścia na slajd.")
DOPR_P5 = ("BRAMKI ODDANIA (wszystkie, z dowodem): verify.ps1 „Tekst - problemy: 0” bez błędu COM; liczba slajdów taka sama "
           "jak w oryginale; treść nie ginie (każdy tekst oryginału jest w poprawionym pliku albo na liście „było -> jest”: "
           "poprawki i wypełnione podpowiedzi); plansze poprawionego pliku obejrzane po ostatniej zmianie. Bez tych wyników "
           "nie pisz, że gotowe.")


def pracuj_na(spec=None, plik="", kopia=""):
    """Punkt o miejscu pracy agenta: spec (jak w dopracowanie.md pkt 7) albo kopia pliku .pptx obok oryginału."""
    if spec:
        return ("PRACUJ NA SPECU: spec tej prezentacji to \"%s\". Poprawki wpisujesz w specu (typ „uklad”) i budujesz "
                "build_dk.py, jak w dopracowanie.md pkt 7; wynik zapisz jako nową wersję „%s” obok oryginału. Oryginału "
                "„%s” nie nadpisujesz." % (spec, kopia, plik))
    return ("PRACUJ NA KOPII: oryginału „%s” nie zmieniasz. Zrób kopię „%s” i poprawiaj ją (python-pptx albo PowerPoint "
            "przez COM) w ramach istniejących kształtów i motywu: kolory i czcionki z motywu, żadnych nowych ani usuniętych "
            "slajdów; zmieniasz tylko tekst (błędy, podpowiedzi) i to, co plansze pokazują jako wadę (łamanie wierszy, "
            "rozmiar pisma, położenie pól). Nie edytujesz skryptów programu ani skilla." % (plik, kopia))


def punkty_dopracowanie(pliki=True, spec=None, plik="", kopia=""):
    """Punkty polecenia dla celu "dopracowanie": czat (wspólne) albo agent z plikami (P1 + wspólne + praca na kopii / specu, P4-P6)."""
    wspolne = [P.WSPOLNE[0], DOPR_TRESC, DOPR_PODPOWIEDZI, P.WSPOLNE[3], P.WSPOLNE[5], P.WSPOLNE[6]]
    if not pliki:
        return wspolne
    praca = [pracuj_na(spec, plik, kopia)] + ([P.P2] if spec else [])   # punkt o „poprawkach” w specu tylko, gdy agent ma spec
    return [P.P1] + wspolne + praca + [DOPR_P4, DOPR_P5, P.P6]


# --- v15: jedno źródło tekstów = skill (polecenia.py). Te same nazwy co wyżej, więc silnik (engine.py) nie wymaga zmian. --------
if getattr(P, "punkty_dopracowanie", None) and "dokument" in getattr(P, "POLECENIA", {}):
    POLECENIE_DOKUMENT = P.POLECENIA["dokument"]
    OPIS, TRESC, WSPOLNE = POLECENIE_DOKUMENT["opis"], P.TRESC_DOKUMENT, POLECENIE_DOKUMENT["polecenie"]
    P4, P5, P6 = P.DOK_P4, P.DOK_P5, P.P6
    OPIS_DOPRACOWANIE, DOPR_TRESC, DOPR_PODPOWIEDZI = P.OPIS_DOPRACOWANIE, P.DOPR_TRESC, P.DOPR_PODPOWIEDZI
    FORMAT_DOPRACOWANIE, DOPR_P4, DOPR_P5 = P.FORMAT_DOPRACOWANIE, P.DOPR_P4, P.DOPR_P5
    pracuj_na, punkty_dopracowanie = P.pracuj_na, P.punkty_dopracowanie
