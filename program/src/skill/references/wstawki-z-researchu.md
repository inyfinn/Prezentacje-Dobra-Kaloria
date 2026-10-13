# Wstawki ze źródłami (research -> prezentacja)

Kiedy: user ma gotową prezentację i audyt / research do niej (zwykle z ChatGPT, skill `gpt`) i prosi, żeby ją „wzbogacić o
wstawki niewielkie, ale udokumentowane” (13.10.2026, strategia „NPD + Portfolio”). Wstawka to świadomy **wyjątek od zasady
konwersji 1:1** (lekcje A33): mały dodatek ze źródłem, nie przebudowa slajdu. Cytat decyzji usera wpisz do paczki.

To jest praca AI w skillu. **W programie „Stwórz prezentację” nie ma i nie będzie do tego kroku ani przełącznika**
(user 13.10: „funkcjonalny, ale nie przeładowany”). Używasz pola `source` i istniejących typów slajdów.

## Co wolno dodać na slajd

| Rodzaj | Co to jest | Limit |
|---|---|---|
| stopka | pole `source`: „Źródło: wydawca, tytuł, data”; bez adresu (adres zostaje w paczce) | jedna na slajd, ok. 150 znaków |
| znak braku źródła | zdanie „Źródło do uzupełnienia: …” w tej samej stopce; treść autorki zostaje | tylko dla liczb, których szukano i nie znaleziono |
| korekta | podmiana zdania mocniejszego niż dowody („było -> jest”), w tym samym polu | bez zmiany układu |
| wstawka | jedno zdanie albo liczba z podpisem, 10-16 słów | najwyżej jedna na slajd, razem kilka na całą prezentację |

Brak miejsca na slajdzie: wstawka idzie do notatek prelegenta. Nie zmniejszaj pisma i nie zamieniaj haseł w bloki tekstu.
Nowe slajdy (plansza dowodów, karta oceny, „co dalej”) tylko jako opcja do decyzji usera, na końcu jako aneks.

## Kolejność pracy

1. **Lista twierdzeń z identyfikatorami** (P01…, D01…, N01…): każda liczba z audytu i ze slajdów, z numerem slajdu
   sprawdzonym na tekście (`python-pptx`, slajd po slajdzie). Numery z audytu bywają przesunięte o jeden.
2. **Źródło pierwotne otwarte dziś** dla każdego ID: adres do konkretnej strony albo pliku, data, cytat dosłowny, status:
   `POTWIERDZONE` / `POTWIERDZONE POŚREDNIO` / `INNA LICZBA` / `NIE ZNALEZIONO`. Nic z pamięci. Audyt modelu to wskazówka,
   gdzie szukać, nie dowód (skill `gpt`: ufamy kierunkowi, sprawdzamy liczby i cytowane źródła).
3. **Mapa**: slajd -> stopka / korekta / wstawka / znak braku źródła / bez zmian. Brzmienia bierz z cytatów, nie z audytu.
4. **Paczka** `wstawki.json` + `wstawki.md`: pozycje z polem `domyslnie` (`zastosuj` / `decyzja` / `opcja`), gotowy tekst
   `source` na slajd, przy każdej pozycji `zrodla[]` (id, status, wydawca, tytuł, adres, data, cytat, zastrzeżenie).
5. **Wbudowanie w spec** (nie w plik PPTX: prezentacja z konwersji jest generowana, ręczna edycja ginie przy przebudowie),
   potem plansze par stary | nowy dla zmienionych slajdów i `verify.ps1`.
6. **Raport**: co wbudowane, lista `decyzja` dla usera / autorki, lista liczb bez źródła.

Duży audyt (ponad ok. 10 twierdzeń): research dziel między workerów według dziedzin (`orchestrator`), kierownik sam otwiera
wyrywkowo co najmniej jedną trzecią adresów.

## Co jest czyją decyzją

- `zastosuj`: stopki, znaki braku źródła, korekty błędu przypisania (np. cudza prognoza podpisana inną instytucją),
  doprecyzowania bez zmiany tezy (kraj próby, rok, zakres kwoty), wstawki ze statusem `POTWIERDZONE`.
- `decyzja` (user albo autorka prezentacji): każda korekta, która zmienia liczbę albo siłę tezy autorki.
- `opcja`: nowe slajdy, dodatkowe wstawki, kredyty zdjęć.

## Słowa, które muszą być widać w brzmieniu

- deklaracje w ankiecie to nie sprzedaż („deklarują”, nie „kupują”);
- prognoza to nie fakt (rok prognozy i autor);
- związek to nie przyczyna (badania obserwacyjne);
- kraj próby, gdy nie jest to Polska (USA przy danych BCG, PwC, Numerator);
- liczba wyliczona przez nas z tabeli: „obliczenia z danych …”, nie cytat;
- hasło firmy o sobie („największa sieć kawiarni”) to nie ranking.

## Pułapki z 13.10.2026

| Objaw | Reguła |
|---|---|
| Audyt przypisał liczbę instytucji, która ją tylko cytuje (prognoza otyłości „NFZ” = World Obesity Atlas) | w stopce autor pierwotny + „za: …” |
| Liczba jest w raporcie, ale znaczy co innego niż na slajdzie (23% = normy WHO w czasie wolnym, 15-69 lat) | zapisz definicję; korekta idzie jako `decyzja` |
| Tytuł publikacji podany przez audyt nie zawiera liczby (GUS „Sytuacja osób starszych” liczy 60+, nie 65+) | stopka wskazuje stronę, na której liczba naprawdę stoi |
| Wyciąg tekstu z PDF przestawił wartości na wykresie | liczby z wykresu czytaj z renderu strony (obraz), nie z `pdftotext` |
| Strona instytucji pusta dla `curl` (EUR-Lex, PubMed, PwC 403) | teksty prawne z `publications.europa.eu`, PubMed przez API; nieotwarte = status pośredni albo brak, nigdy „potwierdzone” |
| Zrzut odpowiedzi AI albo zdjęcie slajdu z konferencji jako „dowód” na slajdzie | znak „Źródło do uzupełnienia”, nie stopka udająca źródło |
| Wstawka powtarza to, co slajd już mówi | przed mapą przeczytaj aktualną wersję slajdów, nie oryginał |
| „Teza” do korekty okazała się tytułem podlinkowanego artykułu (slajd 41, pole `links` w specu) | przed korektą zdania sprawdź w specu, czy to nie link do lektury; tytułu cudzego artykułu nie przepisujesz |
| Wiersz `small` pod kartami zmniejszył hasła (slajd 19) i wykresy (slajd 25) | wstawka idzie jako blok `p` do karty, która ma wolne miejsce, albo do `notes`; sama stopka `source` zabiera tylko 0,25 cm |
| Dłuższe brzmienia na najgęstszym slajdzie zbiły pismo poniżej 13 pt | na gęstym slajdzie tylko stopka; korekty i niuanse do notatek prelegenta i na listę decyzji |

Gdzie co ląduje w specu (`uklad`): `source` = stopka; `notes` = pełne adresy źródeł i niuanse (na slajdzie adresów nie ma);
korekta = podmiana `t` bloku (blok z `wyr`: po zmianie liczby słów popraw `wyr`). Zaakceptowanego pliku nie nadpisujesz:
wynik zapisz obok jako „… ze źródłami.pptx”, a korekty brzmienia wypisz userowi „było -> jest” do akceptacji.

Wątek ChatGPT z audytem czytasz skillami `browser` / `gpt` (zalogowany profil automatyzacji); plakietki źródeł w odpowiedzi
kryją adresy, które warto zebrać przed własnym szukaniem. Widżety interaktywne z odpowiedzi (np. karta oceny z suwakami)
odtwarzaj jako zwykłą tabelę do wypełnienia przez zespół: wagi i wzór podaj wprost, ocen startowych nie wymyślaj.
