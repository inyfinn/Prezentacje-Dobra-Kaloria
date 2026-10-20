# -*- coding: utf-8 -*-
"""Polecenia dla AI po konwersji gotowej prezentacji (13.10.2026). Jedno źródło dla programu (engine.py), wiersza
poleceń i dokumentów. Skrót metody z references/dopracowanie.md (w razie sprzeczności wygrywa tamten plik).

    import polecenia
    polecenia.polecenie_ai("wiernie", dane, pliki=True)   # agent z plikami (Claude Code / Cowork, Codex, Gemini CLI)
    polecenia.polecenie_ai("wiernie", dane, pliki=False)  # czat bez plików (Claude.ai, ChatGPT, Gemini w przeglądarce)
    polecenia.tabela_ksztaltow(14)                        # zwarta tabela "kształt treści -> wzór" z katalogu szablonu
    polecenia.role_slajdu(slajd)                          # [(rola, tekst)] dla slajdu `uklad` (czat widzi role tekstu)
    polecenia.polecenie_ai("dokument", pliki=...)         # prezentacja zrobiona z dokumentu (docx, pdf, txt)
    polecenia.punkty_dopracowanie(pliki, spec, plik, kopia)   # plik już w stylu marki: przegląd i dopracowanie

Czat nie może dostać polecenia, którego nie da się wykonać bez plików: punkty tylko dla agenta są w `polecenie_pliki`.
`pptx_convert.CELE` zachowuje `nazwa` i `sufiks`; `opis` i `polecenie` bierze stąd.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# --- punkty tylko dla agenta z plikami ----------------------------------------------------------------------------
P1 = ("ZANIM COKOLWIEK POPRAWISZ, wczytaj pliki z KROKU 0 i 0b. Najważniejszy: references\\dopracowanie.md (cały - to "
      "metoda, według której pracujesz; w razie sprzeczności z innym dokumentem wygrywa ten plik) oraz "
      "references\\katalog-szablonu.md (tabela „kształt treści -> slajd szablonu”). Bez nich nie zmieniaj wyglądu.")
P2 = ("KAŻDĄ POPRAWKĘ TEKSTU wpisz do specu w kluczu „poprawki”: {\"slajd\": numer slajdu oryginału, \"bylo\", \"jest\", "
      "\"powod\"}. Kontrola treści przyjmie tylko poprawki w granicach z punktu o błędach; inne zgłosi jako usterkę (także zdjęcie "
      "końcowego myślnika po spacji - wtedy znak zostaje, a slajd idzie do DO DECYZJI).")
P4 = ("PĘTLA: wyrenderuj oryginał i wynik, zrób plansze par stary | nowy i OBEJRZYJ KAŻDĄ planszę jako obraz (polecenia: "
      "instrukcja programu, sekcja 3b). Dla każdego slajdu przejdź 8 pytań z dopracowanie.md pkt 7. Poprawki wpisuj do "
      "specu (spec_konwersja.json; program zapisuje go jako spec_program.json; typ slajdu „uklad”) i buduj jednym "
      "poleceniem z dopracowanie.md pkt 7 (pptx_convert.py … --ze-specu <spec>) - nigdy "
      "ręcznie w PowerPoincie; skryptów programu i skilla nie edytujesz. Rozmiary pisma i usterki układu przed renderem "
      "pokaże szablonuj.py <spec>. Po każdej zmianie nowe zrzuty i ponowny ogląd. Najwyżej 3 podejścia na slajd. Gdy "
      "budowa zapisze wynik jako „… (nowa wersja).pptx” (plik zmieniony ręcznie albo otwarty w PowerPoincie), oddajesz "
      "ten nowy plik i piszesz o tym w raporcie.")
P3 = ("GDY TREŚĆ SIĘ NIE MIEŚCI (hasło poniżej 16 pt, dopisek albo punkt poniżej 13 pt; wyjątek: rząd 5-6 kafli "
      "z krótkimi hasłami, 14-16 pt): nie zmniejszaj pisma i nie usuwaj słów. Uprość układ w tej kolejności: zdejmij ikony "
      "z kart; 4 karty w rzędzie zamień na siatkę 2 x 2; nagłówek karty wynieś jako wiersz nad karty; kolejne zdania długiego "
      "akapitu zamień na punkty z ikoną. Gdy to nie pomaga - DO DECYZJI.")
P5 = ("BRAMKI ODDANIA (wszystkie, z dowodem): verify.ps1 „Tekst - problemy: 0” bez błędu COM; „Treść: 100% akapitów”; "
      "linia „Kontrola układu: usterki 0, znaki 0, slajdów N z N”; plansze par obejrzane po ostatniej zmianie. Wyniki wypisuje "
      "polecenie budowy i zapisuje pokrycie.json w katalogu roboczym. Bez tych wyników nie pisz, że gotowe.")
P6 = ("RAPORT PO POLSKU, KRÓTKO: plik i liczba slajdów; wyniki bramek; co zmieniłeś względem wersji z programu (slajd -> "
      "wzór z katalogu); poprawione błędy tekstu (slajd: było -> jest); DO DECYZJI. Pracuj sam do bramek: nie pytaj o zgodę na "
      "kolejne kroki, pytaj tylko o rzeczy z listy DO DECYZJI.")

# --- punkty wspólne (czat i agent) ---------------------------------------------------------------------------------
# 13.10 (test na Claude): AI zmieniło tytuły ponad literówki i dopisało własne zdania. Zdanie stoi W punkcie o błędach
# (doprecyzowanie warunku d), nie jako osobny punkt - lista WSPOLNE ma stałą długość (inne cele biorą z niej po indeksie).
GRANICE = ("Tytułów, haseł i zdań NIE PRZEREDAGOWUJESZ („Rola socjalna snacków” zostaje, nie „Społeczna rola snacków”) "
           "i nie dopisujesz liczb, wniosków ani zdań, których nie ma w źródle. Każda zmiana słowa inna niż taki błąd idzie "
           "do DO DECYZJI („do decyzji autora”), nie do pliku. Wyjątek: znak urwany na końcu hasła (punkt o układzie).")

WSPOLNE = [
    "SLAJD TO PLAKAT, NIE KARTKA. Na slajdzie z tekstem: tytuł, 1-4 hasła w Mindset, przy nich liczba albo ikona, pod "
    "hasłem krótki dopisek w Lato (do 18 pt), na dole wniosek w pasie. Wszystkie słowa, liczby i znaki autora zostają, "
    "w tej samej kolejności; zmienia się ich rola. W kartach z tekstem ma być więcej słów w Mindset niż w Lato. Tło "
    "slajdu białe, kremowe są tylko karty, zieleń i czerwień tylko z motywu.",
    "HASŁOWANIE. Zdanie do 12 słów jest hasłem w całości. Dłuższe: hasło do pierwszego przecinka stojącego po 4-15 "
    "słowach (przecinek zostaje przy haśle) albo przed spójnikiem „i / oraz / ale / wobec / czyli”; reszta zdania "
    "i kolejne zdania to dopisek. Zdanie bez takiej granicy: do 24 słów całe jest hasłem, dłuższe zostaje akapitem "
    "w karcie. Pierwsza liczba z jednostką stojąca w haśle (%, mln, mld, zł…) jest powtórzona nad nim jako "
    "liczba-bohater; nie dotyczy roku, daty, EAN, gramatury, nazw z cyfrą (B12, GLP-1). Zdanie z co najmniej trzema parami "
    "„nazwa (NN%)” może dostać pod hasłem słupki z tymi samymi nazwami i liczbami. Liczba-bohater i słupki to jedyne "
    "dozwolone powtórzenia tekstu. Ostatnie zdanie-puenta slajdu, „Ważna kwestia – …”, „Insight: …” i linia od „=” idą do pasa pod kartami. "
    "„CT: …” / „TA: …” to kafle etykieta-wartość. Akapit z 4 i więcej zdań: pierwsze zdanie jako hasło z dopiskiem, "
    "kolejne jako punkty z ikoną.",
    "HASŁOWANIE NIE DOTYCZY: tabel, wykresów, slajdów z samym zdjęciem albo zrzutem, okładki, przekładek, zakończenia, "
    "wartości odżywczych, danych produktu (EAN, gramatura, oświadczenia z karty wprowadzenia) i cytatów. Te zostają "
    "takie, jakie dał program; sprawdzasz w nich tylko błędy tekstu i czytelność.",
    "UKŁAD BIERZESZ Z SZABLONU. Dla każdego slajdu nazwij kształt treści i weź wzór z tabeli „kształt treści -> wzór”. "
    "Gdy żaden wiersz nie pasuje, złóż układ z tych samych klocków i wpisz slajd do DO DECYZJI. Bez własnych kolorów "
    "i czcionek.",
    "1:1 W TREŚCI: slajd N wyniku = slajd N oryginału. Żadnych nowych slajdów, agendy, przekładek, własnych tytułów "
    "i haseł; bez łączenia, dzielenia i przestawiania slajdów; bez dopisywania i skracania; bez wymyślania liczb; obrazy "
    "w całości; słowa wyróżnione kolorem przez autora zostają wyróżnione. Wniosek przenosisz do pasa tylko wtedy, gdy "
    "w oryginale i tak stoi najniżej.",
    "BŁĘDY W TEKŚCIE ORYGINAŁU POPRAWIASZ, ale tylko ewidentne, czyli gdy spełnione są wszystkie warunki: (a) to, co "
    "stoi w źródle, nie jest w tym zdaniu poprawnym polskim słowem lub formą, nazwą, skrótem ani słowem obcym; (b) jest "
    "jedna oczywista poprawna forma, różna najwyżej o spację albo 2 znaki w jednym słowie; (c) słowo nie stoi w cytacie, "
    "w tekście obcojęzycznym, w liczbie, w oświadczeniu żywieniowym lub zdrowotnym, w nazwie prawnej ani w hiperłączu; "
    "(d) nie zmieniasz szyku, stylu ani wielkości liter. Przykłady: „komunikacjaod” -> „komunikacja od”, „odwrotem "
    "o węglowodanów” -> „odwrotem od węglowodanów”, „do zbudowanie” -> „do zbudowania”, zdublowane słowo, brak spacji po "
    "przecinku, podwójna spacja. Nie poprawiasz nazw własnych, skrótów, liczb, wielokropków i myślników autora ani zdań "
    "niezręcznych - te zgłaszasz w DO DECYZJI. " + GRANICE + " Zacznij od listy „MOŻLIWE BŁĘDY W TEKŚCIE ORYGINAŁU” z programu, potem "
    "przeczytaj każdy slajd sam: program widzi tylko słowa spoza słownika, a błędu odmiany nie zauważy.",
    "TYPOGRAFIA: żadnej linii zakończonej na „a, i, o, u, w, z”, żadnego pojedynczego słowa w ostatniej linii hasła, "
    "skrót i liczba razem ze swoim słowem („ok. 12 mln”, „2025 r.”), żadnego hasła łamanego słowo po słowie w wąskiej "
    "karcie. To błędy łamania, nie tekstu: poprawia się je podziałem hasło / dopisek albo układem kart.",
]

# 13.10 (test na Claude): ok. 40 poprawek tekstu, układ nietknięty. Lista sprawdzalna okiem, od listy z pomiaru zrzutów.
UKLAD = (
    "PO KOREKCIE TEKSTU PRZEJDŹ SLAJD PO SLAJDZIE I NAPRAW UKŁAD - same literówki to za mało. Zacznij od "
    "linii „Sprawdź najpierw: slajd N - …” w UWAGACH PROGRAMU (pomiar zrzutów). "
    "Szukaj i poprawiaj: (a) hasło albo pas (zielona belka) urwane na końcu myślnikiem, przecinkiem lub "
    "dwukropkiem, np. „BIAŁKO –”: złącz z ciągiem dalszym zdania z tego slajdu, a gdy go nie ma - zdejmij sam końcowy znak; (b) duża "
    "liczba, a hasło pod nią urywa się na tej samej liczbie („7,7 MLN” nad „…osoby 65+ to 7,7 mln,”): złącz hasło "
    "z dopiskiem w jedno zdanie albo zdejmij dużą liczbę (liczba nad pełnym zdaniem to nie błąd); (c) karta pusta "
    "w ponad połowie obok pełnej: wyrównaj treść kart albo zmień ich układ; (d) pusty dół slajdu (ponad 1/3 wysokości): "
    "powiększ obrazy z zachowaniem proporcji albo rozłóż treść na całą wysokość; (e) slajd z podpowiedziami "
    "w [nawiasach]: wpisz WYŁĄCZNIE tytuły i zdania przepisane z tej prezentacji, bez własnych streszczeń, wniosków "
    "i liczb; gdy nie ma czym go wypełnić - slajd dodany przez program (w notatkach „NOWY”) usuń, a pojedyncze puste "
    "pole zostaw w nawiasach. W raporcie albo odpowiedzi jedna linia na każdą pozycję „Sprawdź najpierw” i każdy slajd z (a)-(e): slajd - "
    "co było - co zrobiłeś albo dlaczego zostaje. Nie możesz zmienić pliku? Podaj gotową poprawkę przy numerze slajdu.")
# Wtyczka Claude w PowerPoincie / sam plik .pptx w rozmowie: jedna gałąź w tym samym poleceniu (bez nowego przycisku).
# Co wtyczka umie - niesprawdzone, dlatego gałąź jest warunkiem („nie masz dostępu…”), nie opisem narzędzia.
BEZ_SKRYPTOW = (
    "NIE MASZ DOSTĘPU DO PLIKÓW I SKRYPTÓW SKILLA (np. wtyczka Claude w PowerPoincie albo sam plik "
    ".pptx)? Pracuj bezpośrednio na otwartej prezentacji: błędy tekstu i układ poprawiasz w pliku, nie tylko "
    "w odpowiedzi. Punkty, które wymagają plików skilla, specu albo skryptów, pomiń i napisz w raporcie, czego nie "
    "sprawdziłeś. Zamiast plików skilla obowiązują wtedy te reguły stylu: hasła czcionką Mindset, dopiski czcionką Lato; "
    "hasło co najmniej 16 pt, dopisek 13 pt (nie zmniejszaj pisma, żeby się zmieściło); kolory tylko z motywu prezentacji; "
    "niczego nie rozciągaj - obrazy i kształty zmieniasz z zachowaniem proporcji; zdjęcia paczek i zrzuty w całości, bez "
    "przycinania.")
NA_KONIEC = [UKLAD, BEZ_SKRYPTOW]   # dwa ostatnie punkty wspólne każdego celu po konwersji i dopracowania
# Cele „rozwiń” i „skróć” nie mają pełnego punktu o błędach (WSPOLNE[5]); dostają jego skrót z tym samym zdaniem GRANICE.
BLEDY_KROTKO = ("BŁĘDY TEKSTU poprawiasz tylko ewidentne: literówka, sklejone słowa, błąd odmiany albo interpunkcji (najwyżej "
                "spacja albo 2 znaki w jednym słowie); nazw własnych, liczb i cytatów nie zmieniasz. " + GRANICE)

DOPISEK_ROZWIN_SKROC = (
    "Slajdy z oryginału dopracuj jak w celu „Zachowaj układ”: hasła, liczby, wnioski, układ z katalogu szablonu, "
    "poprawione ewidentne błędy tekstu. Nowe slajdy bierz z katalogu szablonu (nazwa wzoru).")

# punkty tylko dla agenta, po punktach wspólnych (P1 stoi PRZED nimi)
_PO_WSPOLNYCH = [P2, P3, P4, P5, P6]

POLECENIA = {
    "wiernie": {
        "opis": "Ten sam slajd w stylu marki. Te same słowa i kolejność, ułożone w hasła, liczby i wnioski z szablonu.",
        "polecenie": list(WSPOLNE) + NA_KONIEC,
        "polecenie_pliki": [P1] + _PO_WSPOLNYCH,
    },
    "rozwin": {
        "opis": "Slajdy z oryginału zostają. Program dołoży puste slajdy z podpowiedziami w [nawiasach]. Treść dopisze "
                "AI albo Ty; sam program niczego nie napisze.",
        "polecenie": [
            # stare punkty celu (przeniesione bez zmian z pptx_convert.CELE, 13.10.2026) + jeden dopisek
            "Prezentacja ma zostać dokończona i rozwinięta. Slajdy z oryginału zostają: te same teksty i kolejność "
            "(układ dopracowujesz - punkty niżej). Niczego z nich nie zabieraj.",
            "Uzupełnij slajdy oznaczone w notatkach „NOWY” (teksty w [nawiasach kwadratowych]) treścią przepisaną "
            "z prezentacji, nie własnym streszczeniem: agenda z tytułów rozdziałów, podsumowanie z wniosków, które stoją "
            "na slajdach, następne kroki z ustaleń.",
            "Zaproponuj brakujące slajdy. Dla każdego podaj: po którym slajdzie ma stać, typ slajdu z szablonu "
            "(np. Punkty, Tabela, Następne kroki) i gotowy tekst. Każdy oznacz słowem NOWY.",
            "Nowe liczby i fakty tylko z materiałów, które dostałeś. Czego w nich nie ma, zostaw w [nawiasach] jako "
            "„do uzupełnienia”. Niczego nie wymyślaj.",
            "Na końcu lista: co dopisałeś, na którym slajdzie i skąd wziąłeś treść.",
            DOPISEK_ROZWIN_SKROC, BLEDY_KROTKO,
        ] + NA_KONIEC,
        "polecenie_pliki": [P1, P2, P4, P5, P6],
    },
    "skroc": {
        "opis": "Nic nie znika: rozdziały, które wyłączysz, zostają w pliku jako slajdy ukryte. Dalszy skrót zrobi AI "
                "z gotowego polecenia.",
        "polecenie": [
            "Prezentacja ma być krótsza: do pokazu ma zostać około %(cel_slajdy)s slajdów (teraz widocznych jest "
            "%(widoczne)s z %(wszystkie)s).",
            "Niczego nie kasuj. Slajd, który nie wchodzi do pokazu, UKRYJ (prawy klik na miniaturze > Ukryj slajd) - "
            "zostaje w pliku na swoim miejscu.",
            "Gdy chcesz podać treść slajdu krócej albo połączyć dwa sąsiednie slajdy o tym samym temacie: zrób NOWY "
            "slajd z krótszą treścią, a oryginały ukryj tuż za nim. Pełny tekst oryginału wklej też do notatek nowego slajdu.",
            "Nie zmieniaj liczb, nazw ani sensu. Nie dopisuj treści, której nie ma w źródle.",
            "Na końcu lista „Co ukryte i gdzie jest oryginał”: numer slajdu oryginału, powód, numer nowego slajdu "
            "(jeśli powstał).",
            DOPISEK_ROZWIN_SKROC, BLEDY_KROTKO,
        ] + NA_KONIEC,
        "polecenie_pliki": [P1, P2, P4, P5, P6],
    },
}


# --- cel "dokument": prezentacja zrobiona Z DOKUMENTU (docx, pdf, txt…) --------------------------------------------------
# Przeniesione z programu (WORK\src\app\polecenia_dok.py, 13.10). Zmienione są tylko punkty, które zakładają oryginalną
# prezentację („slajd N = slajd N”, render oryginału, plansze par stary | nowy).
TRESC_DOKUMENT = (
    "TREŚĆ Z DOKUMENTU, NIC WIĘCEJ: slajdy powstały z dokumentu, w jego kolejności. Wszystkie słowa, liczby i znaki "
    "dokumentu zostają; żadnych własnych tytułów, haseł, wniosków ani liczb (tytuł slajdu = nagłówek z dokumentu); "
    "nie łącz i nie dziel sekcji w środku zdania; obrazy w całości; słowa wyróżnione przez autora zostają wyróżnione. "
    "Liczbę slajdów i przekładek rozdziałów ustawił człowiek suwakiem - nie zmieniaj jej (wyjątek: slajd, na którym "
    "treść nie mieści się pismem 13 pt - wtedy podziel go i zgłoś w DO DECYZJI).")
DOK_P4 = ("PĘTLA: obejrzyj KAŻDĄ planszę z folderu „plansze” obok pliku wyniku (wynik_01-06.png…; to zrzuty gotowego pliku, "
          "6 slajdów na planszę) jako obraz. Dla każdego slajdu przejdź 8 pytań z dopracowanie.md pkt 7. Poprawki wpisuj do "
          "spec_konwersja.json (typ „uklad”) i buduj build_dk.py - nigdy ręcznie w PowerPoincie; skryptów programu i skilla nie "
          "edytujesz. Po każdej zmianie wyrenderuj plik (render.ps1), zrób nowe plansze (contact_sheet.py <katalog png> <plik.png> 2) "
          "i obejrzyj je ponownie. Najwyżej 3 podejścia na slajd.")
DOK_P5 = ("BRAMKI ODDANIA (wszystkie, z dowodem): verify.ps1 „Tekst - problemy: 0” bez błędu COM; „Treść: 100% akapitów” "
          "(kontrola pokrycia dokumentu: dokument.py); liczba slajdów taka, jaką ustawił człowiek (albo wyższa z powodu "
          "podziału, opisanego w DO DECYZJI); plansze obejrzane po ostatniej zmianie. Bez tych wyników nie pisz, że gotowe.")
# 7 punktów wspólnych + NA_KONIEC (2) i 5 dla agenta: test programu (WORK\logs\test_wejscie.py) pilnuje tych liczb
POLECENIA["dokument"] = {
    "nazwa": "Dokument", "sufiks": " - prezentacja",
    "opis": "Prezentacja z dokumentu: slajdy w stylu marki z tych samych słów, w kolejności dokumentu. "
            "Liczbę slajdów i przekładek ustawia człowiek suwakiem.",
    "polecenie": WSPOLNE[:4] + [TRESC_DOKUMENT] + WSPOLNE[5:] + NA_KONIEC,
    "polecenie_pliki": [P1, P2, DOK_P4, DOK_P5, P6],
}

# --- cel "dopracowanie": plik JUŻ w stylu marki (szablon DK, wynik programu). Program go nie przekłada, tylko sprawdza -----
OPIS_DOPRACOWANIE = ("Prezentacja już w stylu marki: program jej nie zmienia, tylko sprawdza (zrzuty, tekst, podpowiedzi "
                     "w [nawiasach]) i przygotowuje polecenie do dopracowania.")
DOPR_TRESC = ("DOPRACOWANIE, NIE PRZEBUDOWA: slajdy już są w stylu marki. Zostaw kolory i czcionki z motywu oraz kolejność "
              "slajdów; układ zmieniasz tylko tam, gdzie widać wadę na planszach albo w tekście: sieroty i zawieszki, pusty "
              "dół slajdu, pusta karta, za małe pismo, hasło łamane słowo po słowie, wniosek poza pasem, ikona niepasująca do "
              "treści (co sprawdzić: punkt o układzie) oraz błędy tekstu. Nie dopisuj faktów ani liczb.")
DOPR_PODPOWIEDZI = ("PODPOWIEDZI W [NAWIASACH]: każda to miejsce na treść użytkownika (np. [Tytuł: wniosek z badania]). "
                    "Wypełnij ją WYŁĄCZNIE tytułami i zdaniami przepisanymi z tej prezentacji, bez własnych streszczeń; czego w niej "
                    "nie ma, zostaw w nawiasach i wpisz do DO DECYZJI z numerem slajdu (cały pusty slajd „NOWY”: punkt "
                    "o układzie, lit. e). Niczego nie wymyślaj.")
FORMAT_DOPRACOWANIE = (
    "FORMAT ODPOWIEDZI - trzy części, nic poza nimi:\n"
    "   A. BŁĘDY TEKSTU - tabela: slajd | było | jest | powód. Tylko ewidentne (punkt o błędach). Na końcu jedno zdanie:\n"
    "      „W PowerPoincie: Ctrl+H, wpisz „było”, zamień na „jest”.”\n"
    "   B. SLAJDY DO POPRAWY - tylko slajdy z wadami (z tekstu, z plansz, z listy „Sprawdź najpierw”): numer | co jest nie\n"
    "      tak | co zrobiłeś albo gotowy poprawiony tekst pól. Dla podpowiedzi w [nawiasach]: numer | podpowiedź | treść\n"
    "      przepisana z prezentacji albo „brak danych”. Slajdów dobrych nie wypisuj.\n"
    "   C. DO DECYZJI: wątpliwe słowa, nazwy, liczby, brakujące informacje, slajdy z za dużą ilością treści.")
DOPR_P4 = ("PĘTLA: obejrzyj KAŻDĄ planszę z folderu „plansze” w katalogu roboczym (wynik_01-06.png…; to zrzuty kopii pliku, "
           "6 slajdów na planszę) jako obraz. Dla każdego slajdu przejdź 8 pytań z dopracowanie.md pkt 7. Po każdej zmianie "
           "wyrenderuj poprawiony plik (render.ps1), zrób nowe plansze (contact_sheet.py <katalog png> <plik.png> 2) i obejrzyj "
           "je ponownie. Najwyżej 3 podejścia na slajd.")
DOPR_P5 = ("BRAMKI ODDANIA (wszystkie, z dowodem): verify.ps1 „Tekst - problemy: 0” bez błędu COM; liczba slajdów taka sama "
           "jak w oryginale (mniej tylko o usunięte slajdy „NOWY” z podpowiedziami, wypisane w raporcie); treść nie ginie "
           "(każdy tekst oryginału jest w poprawionym pliku albo na liście „było -> jest”: poprawki i wypełnione podpowiedzi); "
           "plansze poprawionego pliku obejrzane po ostatniej zmianie. Bez tych wyników nie pisz, że gotowe.")


def pracuj_na(spec=None, plik="", kopia=""):
    """Punkt o miejscu pracy agenta: spec (jak w dopracowanie.md pkt 7) albo kopia pliku .pptx obok oryginału."""
    if spec:
        return ("PRACUJ NA SPECU: spec tej prezentacji to \"%s\". Poprawki wpisujesz w specu (typ „uklad”) i budujesz "
                "build_dk.py, jak w dopracowanie.md pkt 7; wynik zapisz jako nową wersję „%s” obok oryginału. Oryginału "
                "„%s” nie nadpisujesz." % (spec, kopia, plik))
    return ("PRACUJ NA KOPII: oryginału „%s” nie zmieniasz. Zrób kopię „%s” i poprawiaj ją (python-pptx albo PowerPoint "
            "przez COM) w ramach istniejących kształtów i motywu: kolory i czcionki z motywu, żadnych nowych slajdów; "
            "zmieniasz tekst (błędy, podpowiedzi) i to, co plansze pokazują jako wadę (łamanie wierszy, rozmiar pisma, "
            "położenie i rozmiar pól oraz obrazów). Nie edytujesz skryptów programu ani skilla." % (plik, kopia))


def punkty_dopracowanie(pliki=True, spec=None, plik="", kopia=""):
    """Punkty celu "dopracowanie": czat (wspólne) albo agent z plikami (P1 + wspólne + praca na kopii / specu, P4-P6).
    Punkt o „poprawkach” w specu (P2) tylko wtedy, gdy agent ma spec."""
    wspolne = [WSPOLNE[0], DOPR_TRESC, DOPR_PODPOWIEDZI, WSPOLNE[3], WSPOLNE[5], WSPOLNE[6]] + NA_KONIEC
    if not pliki:
        return wspolne
    return [P1] + wspolne + [pracuj_na(spec, plik, kopia)] + ([P2] if spec else []) + [DOPR_P4, DOPR_P5, P6]


class _Dane(dict):
    """Brakujący klucz w `dane` daje „?”, nie wyjątek (polecenie powstaje także bez licznika slajdów)."""
    def __missing__(self, k):
        return "?"


def polecenie_ai(cel, dane=None, pliki=True):
    """Punkty polecenia dla AI. pliki=True (domyślnie, zgodność wsteczna): agent z plikami =
    polecenie_pliki[:1] + polecenie + polecenie_pliki[1:]; pliki=False: czat bez plików = same punkty wspólne.
    Podstawianie %(klucz)s z `dane` tylko w punktach, które mają „%(”."""
    c = POLECENIA[cel if cel in POLECENIA else "wiernie"]
    pts = (c["polecenie_pliki"][:1] + c["polecenie"] + c["polecenie_pliki"][1:]) if pliki else list(c["polecenie"])
    d = _Dane(dane or {})
    return [p % d if "%(" in p else p for p in pts]


# --- tabela „kształt treści -> wzór” z katalogu szablonu ----------------------------------------------------------
def _katalog():
    for d in (os.path.join(HERE, "..", "assets"), os.path.join(HERE, "assets"), HERE):
        p = os.path.join(d, "katalog-szablonu.json")
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError):
                return None
    return None


_RE_S = re.compile(r"\bS\d*\b")   # reguła automatu (S1-S15, „S (bars ręcznie)”); R = reguły sprzed szablonowania


def _skroc(t, n):
    t = " ".join((t or "").split())
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;: ") + "…"


def tabela_ksztaltow(n=14):
    """Zwarty tekst: po linii „<kształt treści> -> wzór: <nazwy z „wez”, do 2> (<uklad>)”. Pierwsze n wierszy: najpierw
    te, które mają regułę S (robi je automat), potem reszta (kolejność z katalogu). Brak pliku = pusty tekst."""
    kat = _katalog()
    if not kat:
        return ""
    nazwy = {s.get("id"): s.get("nazwa", "") for s in kat.get("slajdy", [])}
    wiersze = kat.get("ksztalty", [])
    wiersze = [k for k in wiersze if _RE_S.search(k.get("regula") or "")] + \
              [k for k in wiersze if not _RE_S.search(k.get("regula") or "")]
    out = []
    for k in wiersze[:max(0, n)]:
        wzory = ", ".join("%s %s" % (i, nazwy.get(i, "")) if nazwy.get(i) else i for i in (k.get("wez") or [])[:2])
        out.append("%s -> wzór: %s (%s)" % (k.get("ksztalt", ""), wzory, _skroc(k.get("uklad"), 110)))
    return "\n".join(out)


# --- role tekstu na slajdzie `uklad` (czat nie widzi wyglądu, widzi role) --------------------------------------------
ROLE_POLE = {"title": "tytuł", "kicker": "etykieta nad tytułem", "lead": "hasło", "big": "hasło", "p": "dopisek",
             "b": "dopisek", "hero": "liczba", "band": "wniosek", "kv": "etykieta", "li": "punkt", "h": "nagłówek",
             "quote": "cytat", "small": "podpis", "sub": "podpis"}


def _t(x):
    return " ".join(str(x).split()) if isinstance(x, str) else ""


def _blok(b, out):
    if not isinstance(b, dict):
        return
    k = b.get("k")
    if k == "pics":
        out.append(("obraz", ""))
        for it in b.get("items") or []:
            if _t(it.get("caption")):
                out.append(("podpis", _t(it["caption"])))
    elif k == "img":
        out.append(("obraz", ""))
    elif k == "kv":
        lab, val = _t(b.get("label")), _t(b.get("t"))
        out.append(("etykieta", (lab + (" " if lab.endswith(":") else ": ") + val) if lab and val else (lab or val)))
    elif k == "quote":
        out.append(("cytat", _t(b.get("t"))))
        if _t(b.get("author")):
            out.append(("podpis", _t(b["author"])))
    elif k == "chips":
        out += [("hasło", _t(x)) for x in b.get("items") or [] if _t(x)]
    elif k == "bars":
        for it in b.get("items") or []:
            out.append(("etykieta", _t(it.get("label"))))
            if _t(it.get("t")):
                out.append(("liczba", _t(it["t"])))
    elif k == "cols":
        for it in b.get("items") or []:
            if _t(it.get("tag")):
                out.append(("etykieta", _t(it["tag"])))
            for bl in it.get("blocks") or []:
                _blok(bl, out)
            if _t(it.get("meta")):
                out.append(("etykieta", _t(it["meta"])))
    elif k in ROLE_POLE and _t(b.get("t")):
        out.append((ROLE_POLE[k], _t(b["t"])))


def role_slajdu(slajd):
    """[(rola, tekst)] w kolejności czytania dla slajdu typu `uklad`: etykieta nad tytułem, tytuł, wiersze (pola
    title/kicker/lead/p/hero/band/kv/li/h/quote/small/sub), stopka źródła. Obraz = jedna linia ("obraz", ""). Inne typy
    slajdów: pusta lista (wywołujący pokazuje je bez prefiksu)."""
    if not isinstance(slajd, dict) or slajd.get("type") != "uklad":
        return []
    out = []
    for key in ("kicker", "title"):
        if _t(slajd.get(key)):
            out.append((ROLE_POLE[key], _t(slajd[key])))
    for r in slajd.get("rows") or []:
        _blok(r, out)
    if _t(slajd.get("source")):
        out.append(("podpis", _t(slajd["source"])))
    return out


def format_roli(rola, tekst):
    return "[%s]" % rola + (" " + tekst if tekst else "")
