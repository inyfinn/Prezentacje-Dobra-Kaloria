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
- [ ] Tekst poza nagłówkami w Lato; `verify.ps1`: czcionki motywu Mindset/Lato, fonty osadzone (>0 plików).
- [ ] Kolory ze slotów motywu (zmiana w Projektowanie > Warianty > Kolory przemalowuje slajdy) - kolory smaków wyjątkiem.
- [ ] `verify.ps1`: każdy slajd ma przejście 3954 (Morph); szablon: sekcje, ukryta instrukcja, etykiety na każdym slajdzie.
- [ ] Kontrast policzony skryptem (muted ≥4,5:1 na papierze, kartach i tłach smaków).
- [ ] Znak wodny na packshotach zgłoszony userowi (nie usuwamy).

## P1
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
