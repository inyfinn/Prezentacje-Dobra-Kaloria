# -*- coding: utf-8 -*-
"""Polecenia dla AI po konwersji gotowej prezentacji (13.10.2026). Jedno źródło dla programu (engine.py), wiersza
poleceń i dokumentów. Skrót metody z references/dopracowanie.md (w razie sprzeczności wygrywa tamten plik).

    import polecenia
    polecenia.polecenie_ai("wiernie", dane, pliki=True)   # agent z plikami (Claude Code / Cowork, Codex, Gemini CLI)
    polecenia.polecenie_ai("wiernie", dane, pliki=False)  # czat bez plików (Claude.ai, ChatGPT, Gemini w przeglądarce)
    polecenia.tabela_ksztaltow(14)                        # zwarta tabela "kształt treści -> wzór" z katalogu szablonu
    polecenia.role_slajdu(slajd)                          # [(rola, tekst)] dla slajdu `uklad` (czat widzi role tekstu)

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
      "\"powod\"}. Kontrola treści przyjmie tylko poprawki w granicach z punktu o błędach; inne zgłosi jako usterkę.")
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
    "niezręcznych - te zgłaszasz w DO DECYZJI. Zacznij od listy „MOŻLIWE BŁĘDY W TEKŚCIE ORYGINAŁU” z programu, potem "
    "przeczytaj każdy slajd sam: program widzi tylko słowa spoza słownika, a błędu odmiany nie zauważy.",
    "TYPOGRAFIA: żadnej linii zakończonej na „a, i, o, u, w, z”, żadnego pojedynczego słowa w ostatniej linii hasła, "
    "skrót i liczba razem ze swoim słowem („ok. 12 mln”, „2025 r.”), żadnego hasła łamanego słowo po słowie w wąskiej "
    "karcie. To błędy łamania, nie tekstu: poprawia się je podziałem hasło / dopisek albo układem kart.",
]

DOPISEK_ROZWIN_SKROC = (
    "Slajdy z oryginału dopracuj jak w celu „Zachowaj układ”: hasła, liczby, wnioski, układ z katalogu szablonu, "
    "poprawione ewidentne błędy tekstu. Nowe slajdy bierz z katalogu szablonu (nazwa wzoru).")

# punkty tylko dla agenta, po punktach wspólnych (P1 stoi PRZED nimi)
_PO_WSPOLNYCH = [P2, P3, P4, P5, P6]

POLECENIA = {
    "wiernie": {
        "opis": "Ten sam slajd w stylu marki. Te same słowa i kolejność, ułożone w hasła, liczby i wnioski z szablonu.",
        "polecenie": list(WSPOLNE),
        "polecenie_pliki": [P1] + _PO_WSPOLNYCH,
    },
    "rozwin": {
        "opis": "Slajdy z oryginału zostają. Program dołoży puste slajdy z podpowiedziami w [nawiasach]. Treść dopisze "
                "AI albo Ty; sam program niczego nie napisze.",
        "polecenie": [
            # stare punkty celu (przeniesione bez zmian z pptx_convert.CELE, 13.10.2026) + jeden dopisek
            "Prezentacja ma zostać dokończona i rozwinięta. Slajdy z oryginału zostają bez zmian: te same teksty, "
            "kolejność i układ. Niczego z nich nie zabieraj.",
            "Uzupełnij slajdy oznaczone w notatkach „NOWY” (teksty w [nawiasach kwadratowych]) treścią, która wynika "
            "z prezentacji: agenda z tytułów rozdziałów, podsumowanie z wniosków, następne kroki z ustaleń.",
            "Zaproponuj brakujące slajdy. Dla każdego podaj: po którym slajdzie ma stać, typ slajdu z szablonu "
            "(np. Punkty, Tabela, Następne kroki) i gotowy tekst. Każdy oznacz słowem NOWY.",
            "Nowe liczby i fakty tylko z materiałów, które dostałeś. Czego w nich nie ma, zostaw w [nawiasach] jako "
            "„do uzupełnienia”. Niczego nie wymyślaj.",
            "Na końcu lista: co dopisałeś, na którym slajdzie i skąd wziąłeś treść.",
            DOPISEK_ROZWIN_SKROC,
        ],
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
            DOPISEK_ROZWIN_SKROC,
        ],
        "polecenie_pliki": [P1, P2, P4, P5, P6],
    },
}


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
