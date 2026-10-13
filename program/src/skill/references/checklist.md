# QA przed oddaniem (plansza z render.ps1 obejrzana narzędziem Read)

## P0 - blokuje oddanie
- [ ] Każda liczba zgadza się z kartą wprowadzenia / arkuszem badania (sprawdzone, nie przepisane z pamięci).
- [ ] Każdy slajd z danymi ma stopkę źródła (kto, kiedy, próba, którego SKU dotyczy).
- [ ] Copy od zespołu wstawione wiernie (poprawione tylko literówki); nic nie dopisane jako fakt bez źródła.
- [ ] Brak tekstu wychodzącego poza kadr / nachodzącego na packshot lub inny tekst.
- [ ] Biały tekst ma pod sobą zielone tło (ozdobniki szablonu są białe - bez ramki znikają na kremie).
- [ ] Packshot bez białej obwódki po wycięciu (sprawdź na kolorowym tle), bez rozciągnięcia proporcji.
- [ ] Logo czytelne: na jasnym tle `logo_green_box.png` / `logo_green_letters.png`, nigdy `logo_white_box.png`.
- [ ] Styl szablon: fonty osadzone (buduj z DK_WZOR). Styl fresh: `render.ps1 -EmbedFonts` wykonane.

## P0 - styl DK 2026 (build_dk)
- [ ] Brak plam/kół/bąbelków za produktem (tylko cień pod paczką).
- [ ] Elementy wokół paczki MAŁE (12-21% wysokości paczki), nie zasłaniają tekstu.
- [ ] Tekst poza nagłówkami w Lato (prezentacje z folderu produktu; w konwersji hasła i liczby też w Mindset, `dopracowanie.md` pkt 1); `verify.ps1`: czcionki motywu Mindset/Lato, fonty osadzone (>0 plików).
- [ ] Kolory ze slotów motywu (zmiana w Projektowanie > Warianty > Kolory przemalowuje slajdy) - kolory smaków wyjątkiem.
- [ ] `verify.ps1`: każdy slajd ma przejście 3954 (Morph); szablon: sekcje, ukryta instrukcja, etykiety na każdym slajdzie.
- [ ] Kontrast policzony skryptem (muted ≥4,5:1 na papierze, kartach i tłach smaków).
- [ ] Znak wodny na packshotach zgłoszony userowi (nie usuwamy).

## P0 - konwersja gotowej prezentacji (`dopracowanie.md` pkt 7-8, `konwersja-pptx.md`; 13.10.2026)
Dla KAŻDEGO slajdu z tekstem odpowiedz na 8 pytań (`dopracowanie.md` pkt 7), patrząc na plansze par stary | nowy:
- [ ] 1. Jaki to kształt treści i czy układ jest z katalogu szablonu (`katalog-szablonu.md`, nazwy „tNN Nazwa”)? Czy hasłowanie w ogóle go dotyczy (pkt 3: tabela, wykres, zdjęcie lub zrzut, okładka, przekładka, wartości odżywcze, dane produktu, cytat - nie)?
- [ ] 2. Czy każda karta ma hasło w Mindset? Czy gdzieś stoi akapit Lato dłuższy niż 3 linie bez hasła? (miara: w kartach z tekstem więcej słów w Mindset niż w Lato)
- [ ] 3. Czy najważniejsza liczba jest bohaterem (nie rok, data, EAN, gramatura, nazwa z cyfrą)?
- [ ] 4. Czy wniosek stoi w pasie?
- [ ] 5. Czy pismo trzyma progi (hasło od 16 pt, dopisek i punkty od 13 pt, etykiety od 11 pt)? Treść nie została wciśnięta mniejszym pismem ani skrócona - gdy się nie mieści, układ jest uproszczony albo slajd idzie do DO DECYZJI.
- [ ] 6. Czy coś łamie się źle: słowo po słowie w wąskiej karcie, sierota, spójnik, skrót lub liczba oderwane od swojego słowa na końcu linii?
- [ ] 7. Czy ikona pasuje do treści? Jeśli nie: wymień (`assets/ikony-slowa.json`, zestaw `assets/icons/dk`) albo zdejmij.
- [ ] 8. Czy ewidentne błędy tekstu są poprawione w granicach i wpisane do specu w `poprawki` (slajd, było, jest, powód)? Wątpliwe, nazwy własne, liczby i cytaty są w DO DECYZJI, nie poprawione?

Bramki oddania (wszystkie, z dowodem; `dopracowanie.md` pkt 8; pierwsze trzy wypisuje jedno polecenie `pptx_convert.py … --ze-specu`, bez PowerPointa z `--bez-qa` - wtedy w raporcie piszesz, że wyglądu i łamania tekstu nie sprawdzono, i nie piszesz „gotowe”):
- [ ] `verify.ps1`: „Tekst - problemy: 0”, **bez wyjątku COM (`RPC_E_CALL_REJECTED`) w logu**; render i verify nie szły równolegle z innym PowerPointem.
- [ ] Kontrola treści: „Treść: 100% akapitów” (poprawki zadeklarowane w `poprawki` i przyjęte przez kontrolę, status `przyjeta`).
- [ ] Kontrola układu: usterki 0, znaki 0, liczba slajdów jak w oryginale (slajd N = slajd N, bez agendy i przekładek).
- [ ] Plansze par stary | nowy obejrzane co do jednej PO ostatniej zmianie.

Nadal obowiązuje (lekcje A27-A41):
- [ ] Nic nie dopisane: każde widoczne pole ma odpowiednik w źródle; jedyne dozwolone powtórzenie to liczba-bohater nad swoim zdaniem.
- [ ] Każdy obraz z podpisem obejrzany w pełnej rozdzielczości i pokazany w całości; tekst ze zrzutów zostaje w obrazie (przepisany idzie do notatek).
- [ ] Kwantyfikatory zostały („ok.”, „ponad”, „do”); stopka źródła tylko pod liczbami, których dotyczy; link do lektury nie jest „Źródłem”.
- [ ] Żadnej etykiety produkcyjnej / notatki roboczej w polach widocznych (uwagi -> notatki slajdu lub raport).
- [ ] Raport po polsku z listą DO DECYZJI i poprawionymi błędami „było -> jest” (`dopracowanie.md` pkt 9).
- [ ] (pomoc, nie bramka) Krytyk (`critic`) przejrzał plansze i pełne rendery; jego zarzuty sprawdzone na obrazach.

## P1 (prezentacje z folderu produktu; w konwersji nie dotyczy „tytuł = wniosek” ani „jedna myśl na slajd”)
- [ ] 1 myśl i 1 liczba-bohater na slajd; tytuł mówi wniosek ("Najwyższy wynik spośród 4 koncepcji"), nie temat ("Wyniki").
- [ ] Rozmiary: tekst ≥ 13,5 pt (fresh) / ≥ 16 pt (szablon), stopka ≥ 10,5 pt.
- [ ] Kontrast tekstu ≥ 4,5:1 (MUTED 5B6B5C na FAF6EF = ok; jasna szałwia tylko dla dekoracji).
- [ ] Bloki treści wyśrodkowane w pionie w obszarze treści (bez pustej dolnej połowy).
- [ ] Wyróżnienie tylko jedno na slajd (zwycięzca / kluczowa grupa).
- [ ] Kolejność: okładka -> produkt -> skład -> (section) badanie -> SKU -> koniec.
- [ ] Brak sierot i złamań na łączniku ("słodko-|kwaśne"); pigułki/etykiety w jednej linii.

## P2
- [ ] Nazwy plików: `<PRODUKT> - prezentacja (szablon).pptx`, `(propozycja odświeżona).pptx` w folderze produktu.
- [ ] Rozmiar pliku < 20 MB (packshoty ~1100 px wysokości).
- [ ] Raport dla usera: braki (packshoty SKU, dane), rozbieżności (nazwy, liczby), decyzje do podjęcia.
- [ ] Typografia PL: `verify.ps1` bez ZAWIESZKA / SIEROTA / MYSLNIK (sprawdza faktyczne łamanie w PowerPoint)
