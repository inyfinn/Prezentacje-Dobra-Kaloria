# Zalecenia usera — jeden język wizualny Dobra Kaloria (30.09.2026)

Źródło prawdy dla agentów pracujących nad: programem „Stwórz prezentację”, Inyfinn Photo Resizer, DAM.
Właściciel wdrożenia w design systemie: agent „Identyfikacja” (wersja tokenów 1.4.0). Po wdrożeniu treść
przechodzi do `IDENTYFIKACJA-WIZUALNA.md` i `DESIGN_SYSTEM.md`, a ten plik zostaje jako zapis decyzji.

**Stan na 06.10.2026 (DS 2.0.0): kolory z wpisów z 30.09, 05.10 i rundy 3 (06.10 rano) są UCHYLONE przez rundę 4**
(sekcja na końcu pliku: „sklep jest wzorcem”). Wpisy zostają jako historia; oznaczenia „UCHYLONE przez rundę 4 (kolor)”
stoją przy regułach, których kolorystyka już nie obowiązuje. Reguły niekolorystyczne (G1 jasne wnętrze checkboxa,
G7 okno, Mindset +10, jeden język kształtów, duży tekst, tagi jako odcień stylu) obowiązują dalej.

## Słowa usera (dosłownie)

> „niech DAM bierze też przykład z rozwiązań stricte w photoresizerze? bo ja już to widziałem i mi się podobają
> te rozwiązania. Co prawda, w każdej aplikacji trzeba zmierzyć tzw. liczbę zakorzenień okna. Tzn. że np. jeśli
> tło jest fundamentem, a na tle rysuje się kontener jeden, a później kolejny, typu rubryka do wypełnienia, to
> niby zakorzenienia są 2. A przecież DAM ma takich zakorzenień więcej. Dlatego trzeba umieć to lepiej rozegrać,
> żeby to pięknie wyglądało. Postaraj się, żeby TAGI też miały raczej ODCIEŃ zastosowanego stylu i tylko
> delikatnie zmieniały barwę Hue, zamiast stałych barw, bo czasem to nie będzie kompletnie pasować.
> Na pewno w Inyfinn Photo Resizer wewnętrzne rubryki były MINIMALNIE za jasne. Jakby były o troszkę ciemniejsze,
> to byłoby już idealnie. I tak samo można budować kwestie wizualne w PREZENTACJE oraz DAM. Fajnie jakby
> ostatecznie powstał taki jeden główny język komunikacji wizualnej. IDENTYFIKACJA WIZUALNA. Że na przyszłość,
> jak cię o coś poproszę, to zrobisz w tym stylu i odtworzysz to bez problemu.”

Wcześniej (wiążące): nagłówki Mindset, tekst Lato. Dwa style „Dobra Kaloria 1 · zieleń” i „Dobra Kaloria 2 ·
krem”, każdy jasny i ciemny. Wzorzec wyglądu: program „Stwórz prezentację” („tam jest pięknie”) oraz rozwiązania
z Photo Resizer 2.6.2. Tło główne w trybie jasnym ma być jaśniejsze niż w obecnym szkicu DAM. Za dużo białych
płyt w DAM = błąd. Sama zmiana czcionki i kolorów to za mało: komponenty (przyciski, karty, okna w oknach,
pola, filtry) mają mieć ten sam język.

## Co z tego wynika (reguły do wdrożenia)

1. **Drabina zagnieżdżeń (poziomy powierzchni).** Każdy styl × tryb ma poziomy L0…L4:
   L0 tło okna → L1 kontener/sekcja/karta → L2 rubryka/pole/karta w karcie → L3 element w polu (chip, wiersz
   listy, okno w oknie) → L4 nakładka (menu, podpowiedź, modal nad modalem). Każdy krok w górę różni się od
   poprzedniego o stały, mały skok jasności (w jasnym: głębiej = minimalnie ciemniej albo jaśniej wg jednego
   kierunku, nigdy losowo; w ciemnym: głębiej = jaśniej). Różnica sąsiadów wyraźna, ale delikatna; ramka tylko
   tam, gdzie sam skok jasności nie wystarcza. Brak czystej bieli na żadnym poziomie w stylach DK.
   **UCHYLONE przez rundę 4 (kolor) dla stylów jasnych:** L0 i L2 są białe, L1 jasnoszary panel, L4 nie jest nakładką;
   kierunek „głębiej = ciemniej” nie obowiązuje (L2 jaśniejszy od L1). Ciemne style bez zmian.
2. **Zmierz liczbę zagnieżdżeń w każdej aplikacji** (program ~2–3, Resizer ~2–3, DAM 4–5) i przypisz każdy
   kontener do poziomu. Aplikacja z głębszym drzewem nie może „przepalić” drabiny — poziomy dobrane tak, żeby
   L4 dalej był czytelny i nie zlewał się z L0.
3. **Rubryki (L2) w Photo Resizer minimalnie ciemniejsze** niż w 2.6.2 — ta sama korekta obowiązuje jako
   wzorzec dla programu i DAM.
4. **Tagi = odcień stylu z lekkim przesunięciem Hue.** Kolory tagów liczone z koloru bazowego stylu (HSL/OKLCH):
   ta sama jasność i nasycenie co styl, Hue przesunięte o małe kroki (np. ±8…±18°) dla kolejnych kategorii.
   Zero stałych barw (fiolet, pomarańcz, niebieski) w stylach DK. Tekst tagu ≥ 4.5:1 w obu trybach.
   Kategorie rozróżnialne także bez koloru (etykieta kategorii / kolejność).
5. **Komponenty jednego języka:** przycisk główny żółty (jeden na widok), drugorzędny zielony obrys, link,
   przyciski-ikony, chipy/segmenty, pola, suwaki, przełączniki, karty, okna w oknach, menu, podpowiedzi,
   powiadomienia — przepis w `components.md`, identyczny dla trzech aplikacji (HTML/CSS i Qt).
   **UCHYLONE przez rundę 4 (kolor):** przycisk główny żółty i drugorzędny „zielony obrys”. Od 2.0.0: główny zielony pełny,
   drugorzędny biały z obrysem `#222222`, żółty = jedna wyróżniona akcja (components.md rozdz. 25).
6. **Odtwarzalność:** dokument `IDENTYFIKACJA-WIZUALNA.md` mówi, jak zrobić nowy ekran/aplikację w tym stylu
   krok po kroku (tokeny, drabina, komponenty, tagi, typografia, ikony, plansza startowa, ikona aplikacji),
   z przykładami z trzech aplikacji i zrzutami.

## 05.10.2026 (DS 1.5.0)

Dosłownie: „Jak dla mnie to szablony kolorystyczne i UI dla photo resizer są bardzo słabe. Bardzo nieczytelne. Większe
teksty powinny być, a schemat kolorystyczny jest po prostu niepotrzebnie cały całkowicie kremowy, a brakuje bieli.
Zerżnij kurwa wprost z PREZENTACJE. Widzę, że wszystko jest zbyt ciasno, nieczytelnie, bloki mają jakiś chujowy obrys.
Nie zastosowałeś schematu. I tak samo na Dobra Kaloria DAM.”
„Popraw całą Dobrą Kalorię Zieleń, bo cały ten motyw jest nijako zły. Po prostu jest taki… mało ciekawy, nieprzyjazny.
Brakuje mu, żeby te ciemniejsze kolorki były inne, jakieś takie… kremowe być może właśnie.”
„Brązy w schemacie brązowym powinny być ciemniejsze. Wprowadź zmiany na Inyfinn Resizer oraz DAM natychmiastowo, w całym spektrum.”

Reguły z tego wynikające:
7. **Wzorzec = program „Stwórz prezentację”, 1:1.** Jasne style: biała strona, kremowe karty, cienka jasna ramka karty, bez
   ciemnego obrysu. Zieleń tylko w akcentach, nigdy jako tło powierzchni.
   **UCHYLONE przez rundę 4 (kolor):** kremowa karta jako poziom 1. Od 2.0.0 wzorcem jest sklep: biała strona, szary panel,
   biała karta w panelu. Zostaje: biała strona, brak ciemnego obrysu, zieleń nigdy jako tło powierzchni.
8. **Czytelność:** tekst co najmniej 15 px w Qt (16 px web), etykiety 14-15 px, kontrolki 40-48 px, więcej odstępu.
9. **Zieleń ciemna ciepła:** kremowy tekst, miodowe/żółte wyróżnienia, głębsze poziomy w stronę oliwki.
10. **Krem ciemny ciemniejszy** na wszystkich poziomach (tło, karty, pola, ramki, tagi).

## 06.10.2026 (runda 3, DS 1.6.0)

Dosłownie (po obejrzeniu Resizera 2.6.4 i programu 1.1.4; źródło: `RUNDA-3-2026-10-06.md`):

> „Ok, bardzo ładnie to już wygląda, natomiast jako globalny styl po prostu zapamiętaj, że checkboxy nie mogą być
> takie ciemne, mogą mieć ciemny obrys (daj trochę jaśniejszy), ale wnętrze musi być jasne. Daj odstęp pomiędzy
> »Lista plików« a elementami po prawej. Wywal informację »Krok po kroku: format i jakość«. Niepotrzebnie obniża to
> wszystkie sekcje. Spraw, żeby nowo otwarte okno nie było większe niż aktualna wysokość rozdzielczości danego
> komputera, ale jednocześnie niech wszystko, co jest w aplikacji, nie będzie przycięte. Bo zawsze muszę poszerzać
> okno na wysokość, bo jest tak przycięte. Popraw kwestie kolorystyczne. Dalej widzę jakieś zielenie w tekstach,
> zamiast soczystych brązów. Zmień to, tak samo popraw to w PREZENTACJE, gdzie mamy jakieś zielone ikony i zielone
> tła, zamiast białych i beżowych, ciemnych brązów. Przycisk »Wybierz folder« jest piękny.”
> „Każdy worker i kierownik ma używać odpowiednich skilli dla DESIGN.”

Wcześniejsze, nadal wiążące (05.10): „Te zielenie wewnątrz brązów są kompletnie brzydkie. Jak już, to ciemne brązy
i czarne kolory. Zielenie mogą być dla innych, osobnych elementów, jak kafelki górne w dashboardzie.” / „Mindset także
w nazwach, kerning +10.” / jeden język kształtów (bez kółek obok kwadratów) / duży tekst / bez grubych obrysów.

Reguły z tego wynikające (pełny opis: `DESIGN_SYSTEM.md` 5e; dotyczą zestawów beżowych: program, DK1 jasny, DK2 jasny, DK2 ciemny).
**UCHYLONE przez rundę 4 (kolor): G2, G3, G4, G5 (kolory), G6.** Zostają: G1 (jasne wnętrze checkboxa; obrys i znak zmienione), G7, G8
(typografia, kształty: promienie teraz 4 / 4 / 8), G9 (DK1 ciemny):
- **G1** Checkbox i radio: wnętrze JASNE także zaznaczone, obrys jaśniejszy od tekstu (`#7D5E44`), znak = brązowy ptaszek / kropka `#3B2A20`; nie ciemny kwadrat.
- **G2** Zero zieleni w tekście i drobnych elementach (liczniki, etykiety, linki, tytuły, ikony, kółka pod ikonami, aktywny krok, suwaki, przełączniki, przyciski drugorzędne). Brąz `#3B2A20`, `#7D5E44`, `#85654A`, akcent `#AD8767`.
- **G3** Zieleń tylko: logo, plansza startowa (splash; zatwierdzony wyjątek), kafle KPI na pulpicie DAM, kropka statusu „online”. Żółty `#FFD42A` z brązowym tekstem = jedyna główna akcja; „Wybierz folder” to wzorzec (bez zmian).
- **G4** Przycisk drugorzędny: tło białe/L1, tekst brązowy pogrubiony, obrys 1 px `#9C8B72`, promień 4 px, hover L2.
- **G5** Suwak: tor `#E1DAC9`, wypełnienie `#7D5E44`, biały uchwyt z obrysem 2 px `#3B2A20`. Przełącznik: tor `#E1DAC9` + obrys `#9C8B72`, włączony `#7D5E44`, gałka biała.
- **G6** Krokomierz: aktywny `#3B2A20` + biały tekst; nieaktywny obrys `#D9CFBB`, tekst `#7D5E44`; ukończony brązowy ptaszek.
- **G7** Okno przy starcie nie wyższe ani szersze niż dostępny obszar ekranu, treść nieprzycięta (zwarty tryb albo przewijanie w panelu). Dotyczy aplikacji.
- **G8** Typografia bez zmian (Mindset +10 w nazwach, Lato >= 14-15 px); kształty: przycisk 4, pole 8, karta 12, tagi pigułki; kontrast tekstu >= 4,5:1.
- **G9** DK1 ciemny zostaje zielony, ale checkbox ma jasne (L3) wnętrze względem tła i znak w limonce.

## 06.10.2026 — runda 4: sklep jest wzorcem (DS 2.0.0)

Dosłownie (po siedmiu zrzutach sklepu dobrakaloria.pl; pełny tekst i opis zrzutów: `RUNDA-4-SKLEP-2026-10-06.md`):

> „Ok, ale miałeś zachować ten ciemnozielony dla nagłówków. I nie wszystko ma być CAŁKOWICIE zawsze beżowe. Pamiętaj,
> że Dobra Kaloria to przecież zielenie i lekkie beżyki ecru też. https://dobrakaloria.pl/
> Jest więcej BIELI niż tych beży. Beże są tylko dla kolejnego poziomu kafelka, a nie od razu do stosowania jako tło.
> Odtwórz ten design. Zwróć uwagę na ikony. To jest design Dobrej Kalorii. Trzymaj się go BEZWZGLĘDNIE. W sensie,
> pamiętaj o kolejnych poziomach hierarchii brązów, bo kafelków jest więcej w głąb, ale zobacz, jak to jest tutaj…
> Biały to tło. Zobacz na stronę koszyka, jak to jest rozwiązane. Białe tło, lekko szare, a później znów białe kafelki
> wewnątrz. O to właśnie chodzi. Przeanalizuj bardzo dobrze te screeny. I zaktualizuj cały DESIGN SYSTEM o to. Pracuj
> nad tym intensywnie. NAJPIERW budujemy nowy design system oparty STRICTE na tych screenshotach, jako jedyne dowody
> na to, jak to powinno wyglądać. A później aktualizuj skill designu Dobrej Kalorii (ds-dobra-kaloria). I użyj
> wszelkich potrzebnych metod i skilli, by dobrze rozkodować moje screenshoty i poprawnie zastosować design do skilla,
> a później rozpropagować go PONOWNIE na nasze 3 programy.”

Reguły z tego wynikające (pełny opis: `tokens/READY-2.0.0.txt` S1-S12, pomiary: `DOWODY-SKLEP.md`, przepisy: `components.md` rozdz. 25):
- **S1** Tło okna BIAŁE; bieli jest najwięcej. Beż, ecru i szary nigdy jako tło okna.
- **S2** Sekcja = panel jasnoszary (L1) bez obrysu i cienia; w panelu BIAŁE karty i pola (L2), jak w koszyku sklepu.
- **S3** Ecru i beż dopiero jako kolejny poziom kafla (L3 w karcie, L4 w kaflu); głębiej się nie schodzi.
- **S4** Tekst i tytuły prawie czarne `#222222`, pomocniczy `#666666`; brąz nie jest kolorem tekstu w stylach jasnych.
- **S5** Ciemnozielony `#00642E` dla nagłówków (tytuł główny, nadtytuł, aktywna zakładka, podpis ikony): to jest „ten
  ciemnozielony dla nagłówków”, który user kazał zachować. Tytuły kart i sekcji: prawie czarne.
- **S6-S9** Przycisk główny zielony pełny; drugorzędny biały z obrysem `#222222`; żółty = jedna wyróżniona akcja
  („Wybierz folder” zostaje); ikony liniowe zielone, kółko tylko dla awatara, kropki, gałki i radio; checkbox biały w środku.
- **Zostaje z wcześniejszych rund:** Mindset także w nazwach (+10), duży tekst, jeden język kształtów, okno nigdy
  większe niż ekran i nigdy przycięte, G1 (wnętrze checkboxa jasne), brak zbędnych linijek-podpowiedzi.

Co ta runda UCHYLA (kolor; historia zostaje wyżej, oznaczona): „zero zieleni w tekście”, „zieleń tylko logo/splash/KPI/status”
(G2, G3), tekst brązowy `#3B2A20` i brązowy akcent, przycisk drugorzędny z brązowym obrysem (G4), suwak, przełącznik
i krokomierz w brązie (G5, G6), kremowa karta jako poziom 1, „brak czystej bieli na żadnym poziomie”, L4 jako nakładka.
