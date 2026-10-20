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

## 06.10.2026 — po obejrzeniu DAM 2.5.4 (stary, brązowy wygląd): mniej obrysów

> „…to DAM wygląda okropnie. Jak SEPIA. A te bubble tagi wyglądają okropnie z tymi obrysami, za dużo obrysów,
> wszystko wygląda okropnie brzydko. […] w ogóle nie o to chodziło.”

- **S13 budżet obrysów** (DS 2.0.1): obrys tylko na polu, checkboxie, jednym przycisku drugorzędnym w grupie, białej
  karcie na białym tle i fokusie. Tagi, metki, pigułki filtrów, liczniki, panele, kafle, przyciski-ikony: bez obrysu.
- **Żadnej sepii:** beż nie jest kolorem obrysu, metki ani tekstu w stylach jasnych; występuje tylko jako kafel L3/L4.
- Przepisy: `.dk-tag` (samo wypełnienie), `.dk-btn--quiet`, `.dk-seg` w `components.md` rozdz. 25 i `preview/sklep.html`.

## 06.10.2026 — szczegółowa krytyka DAM 2.5.4 (7 zrzutów): za ciężko, za dużo teł i obrysów

> „To jest zbyt ponure, zbyt ciężkie. Za duże obrysy na przyciskach. Kompletnie brzydkie. Niepotrzebne zagnieżdżenie
> teł w środku, po co beżowe, jak może być białe, rozumiesz? Niepotrzebne tła dla »tło«. Tagi są okropnie brzydkie.
> Powiadomienia mają tło kafelków, a nie muszą, dopiero kafelki wewnątrz, jak »projekty po dopracowaniu«, powinny
> mieć szarość. Tak jak w DOBRA KALORIA. A cały SZUKAJ, za grube i za ciężkie obrysy, coś okropnego. Tak samo
> w eksplorerze, wszystko nie wygląda żywo i ładnie, jak w dobrakaloria.pl, tylko staro, jak SEPIA. I gdzieniegdzie
> kolory się nie zgadzają, dalej są jeszcze jakieś fiolety, albo jakieś paseczki dziwne. Wlej tu więcej życia
> i koloru. Specjalnie pokazałem Ci tamte screenshoty, żebyś wiedział, że raczej przeważa biały kolor, NIE MA aż tak
> dużo BEŻOWYCH kolorów. Są tak ciemne zielone, że niemalże czarne. NIE MA takich cholernie grubych obrysów.”

- **S14 minimum poziomów** (DS 2.0.2): kontener bez tła, jeśli wystarczy biel; w liście szare są dopiero pozycje;
  szary panel tylko dla grupy różnych białych kart lub pól; metadane bez tła; beż dopiero na 3. poziomie; zero fioletów.
- **S15 ciemne = ciemna zieleń, fokus cienki:** ciemne elementy `#00642E` zamiast brązu i czerni; fokus pola = 1 px
  zieleni + miękka poświata, nigdy gruby ciemny pierścień; aktywny segment i zaznaczony tag zielone.
- Przepis listy: `.dk-item` w `components.md` rozdz. 25 i `preview/sklep.html`.

## 06.10.2026 — DAM 2.5.4, widok Wizualizacji: tagi kolorowe, mniej brązu

> „Już jest tak COZY, jest już dużo lepiej, szczególnie to przyciemnienie brązowe, ale dalej za dużo brązu. Dalej jest
> zdecydowanie za dużo brązu, a TAGI »DK, Kulki, DOYPACK« itp. to jest zbyt brzydkie. Powinny być jednak kolorki. Bo
> aktualnie to jest niesamowicie brzydkie. Niepotrzebne są te obrysy w tagach… Różnicuj kolory.”

- **S17** (DS 2.0.5): tagi w 8 różnych barwach, samo wypełnienie bez obrysu, jedna grupa tagów = jedna barwa.
- Ciepłe brązowe przyciemnienie pod oknem dialogowym user pochwalił — zostaje (`shadow-scrim`).
- UCHYLA zasadę z 30.09 „tagi tylko delikatnie zmieniają barwę” oraz zielone odcienie tagów z 2.0.0.

## 07.10.2026 — tryb ciemny po przełączaniu „przesuwa się do góry” (DAM)

> „Pamiętaj, że tryb dark ma być dosłownie tym samym, co tryb light. Zmieniają się tylko kolorki. Nigdy nie dodawaj
> dodatkowych kafelków, teł, ani nie przesuwaj treści. Zmieniają się tylko kolory.”

- **S19** (DS 2.0.8): geometria jasnego i ciemnego identyczna; reguły zależne od motywu zmieniają tylko kolory.
- Przyczyna zgłoszenia: w DAM odstępy 2.0 (24 px pod nagłówkiem) dostał tylko styl jasny.

## 19.10.2026 — Panel Ankiet (makiety rund 1–3): reguły stylu na stałe

> „Zapisz to sobie w skillu i na zawsze. WSZYSTKIE te poprawki, które daję do stylu, zapisuj od razu w skillu.
> NIGDY nie dajesz kremowego na szarym tle. Jak masz coś takiego, to tło jest białe i koniec.”

- **S20 krem nigdy na szarym:** ecru/krem (`surface-3`) wolno położyć tylko na białym (L2). Na szarym panelu L1 każda
  karta, kafel, baner (także „link testowy”, „zaznaczono 3 osoby”) jest BIAŁY. Bez wyjątków.
- **S21 liczba z jednostką:** wynik pokazuj dużą liczbą po prawej stronie karty, a „/ 11” (mianownik, jednostka)
  mniejszy i wygaszony, „schowany” obok. Chwalone: „lepiej, jak liczba jest po prawej i ta 11 tak ładnie schowana”.
- **S22 bez liczników doklejonych do tekstu:** żadne „6 z 8” na końcu punktu listy. Liczba osób nie jest potrzebna
  w listach mocnych stron; jeśli coś ma stać po prawej, to tag (pigułka) wyrównany do prawej, w jednej kolumnie.
- **S23 nagłówek sekcji ogólny, karta szczegółowa:** nie powtarzaj tego samego tytułu w nagłówku sekcji i w karcie
  pod nim (np. „Terminowość i organizacja” dwa razy). Sekcja brzmi ogólnie, karta niżej szczegółowo.
- **S24 oddech:** sekcje co najmniej 64 px od siebie, padding kart co najmniej 24 px, pigułki co najmniej 6×12 px,
  tekst co najmniej 16 px od paska postępu (zwłaszcza pod paskiem). Za ciasne odstępy = „wszystko zlewa się w jedno”.
- **S25 statusy spokojne:** w listach statusów (Wysłano, Skopiowano, Do wysłania) nie stawiaj obok siebie wielu
  kolorowych pigułek z ikonami; status mały, stonowany, po prawej u góry wiersza. Kolor tylko tam, gdzie wymaga uwagi.
- **S26 karta wyboru (checkbox-karta):** najpierw tytuł (pogrubiony), opis pod nim, tag kategorii w prawym górnym
  rogu; zaznaczenie = tylko zielony obrys 2 px, tło się NIE zmienia.
- **S27 suwak oceny:** zawsze suwak DS (szary tor, zielone wypełnienie, biały uchwyt z zielonym obrysem, wartość nad
  uchwytem, liczby pod torem bez ramek). Gradient czerwony→zielony jest „kompletnie obcy”.
- **S28 polska typografia w UI i PDF:** twarda spacja po słowach jednoliterowych (w, z, i, a, o, u) i po krótkich
  przyimkach; bez sierot i wdów; bez półpauzy i pauzy. Mała litera w Mindset (np. „z” w „6 z 8”) bywa nieczytelna:
  łączniki i małe słowa przy liczbach w Mindset pisz krojem Lato.
- **S29 przyciski z napisem:** ikonę bez napisu zostaw tylko tam, gdzie znaczenie jest oczywiste (strzałka wstecz);
  gdy jest miejsce, przycisk = ikona + krótki napis. Na telefonie przycisk nigdy nie zawija tekstu.
- **S30 bez ramki w ramce (19.10.2026):** „W widoku na telefon niepotrzebnie robisz ramkę w ramce i znów ramkę. Za dużo
  ramek.” Na telefonie najwyżej jeden poziom obramowania: kontener sekcji bez obrysu i tła (pełna szerokość), w nim
  karty z jedną linią albo same odstępy i separatory. Na desktopie też unikaj trzech zagnieżdżonych obrysów.
- **S31 raport jak dokument (19.10.2026):** „Zostaw już wersję bez bocznego paska, zupełnie jakby to było PDF.” Raport
  na ekranie to jedna kolumna jak strona dokumentu, bez spisu/menu bocznego.
- **S32 animacje fade (19.10.2026):** „Do całego programu dodaj animacje fade in, fade out.” Wejście widoków, kart,
  rozwijanych sekcji i komunikatów: łagodne pojawianie się (opacity + delikatny ruch 4-8 px, 150-250 ms, ease-out);
  znikanie odwrotnie. Zawsze `prefers-reduced-motion: reduce` = bez animacji.
- **S33 zawsze jest wyjście (19.10.2026):** „Z perspektywy UX nigdy nie wolno zostawiać użytkownika bez wyjścia. Tu
  nie ma żadnego przycisku powrót.” Każdy ekran komunikatu (szkic, błąd, brak dostępu, podgląd) ma przycisk powrotu
  albo link do miejsca, z którego user przyszedł.
- **S34 oddech między grupami (19.10.2026):** „Większe odstępy między Aktywne, Szkice i Zakończone, bo są za małe,
  zlewa się w jedno. Może przydałoby się jakieś 100 px.” Odstęp między grupami sekcji na stronie ok. 96 px.
- **S35 przestrzeń się wypełnia (19.10.2026):** „Teksty daj w 2 kolumnach, a wykresy daj z większym odstępem od góry
  i w biały kafelek. Przenoś treści CSS GRID, żeby nie było takiej wolnej przestrzeni dookoła. Teksty trzeba układać
  tak, by przestrzeń się uzupełniała. Daj dobry odstęp w poziomie pomiędzy kolumnami.” Długie listy w siatce 2 kolumn
  (odstęp poziomy ok. 56 px), nie jedna wąska kolumna obok pustego pola; wykresy w osobnym białym kaflu. Liczniki
  typu „2 z 8” tylko, gdy user ich potrzebuje (tu: nie rozumiał, usunięte).
- **S36 kategoria jako tag (20.10.2026):** „Najwyżej oceniony obszar” ma być wyróżnione jako pigułka/tag (kategoria), a
  pod nim nazwa (treść). Nigdy kategoria i treść tym samym krojem i wielkością. Liczniki typu „6 z 8” jako pigułka.
- **S37 nigdy nie ucinaj tekstu (20.10.2026):** „Nie może tak być, że teksty są ucięte. Nigdy nie możesz żadnych
  tekstów uciąć.” Zakaz `text-overflow: ellipsis` / `line-clamp` na treści; tekst się zawija.
- **S38 telefon = więcej powietrza (20.10.2026):** na telefonie listy w białych kaflach na szarym tle, każdy element
  wyraźnie oddzielony (kafel albo punktor), większe odstępy między elementami nagłówka i sekcjami.
- **S39 przejrzystość kosztem przestrzeni (20.10.2026):** „Mamy cały ekran komputera do dyspozycji, dobrze, żeby było
  przejrzyste bardziej, kosztem przestrzeni.” Na desktopie wolę mniej elementów naraz i więcej oddechu niż gęste trzy
  kolumny; panele pomocnicze (podgląd) pokazywane na żądanie, nie zawsze.
- **S40 elementy nie nachodzą (20.10.2026):** „Zwracaj uwagę, żeby elementy nie nachodziły na siebie — suwak na siebie
  nachodzi.” Każdy zrzut sprawdzaj pod kątem nakładania (dymek wartości, etykiety, liczby pod torem).
- **S41 ramki urządzeń lekkie (20.10.2026):** ramka telefonu w podglądzie cienka i jasna, nie ciężka.
- **S42 hierarchia treść > metadane (20.10.2026):** treść główna (np. cytat zachowania) minimalnie większa; metadane
  („Wskazało 6 z 8 osób. Obszar: …”) mniejsze i wygaszone, z wyraźnym odstępem od treści.
- **S43 jeden zapis liczb (20.10.2026):** każdy wynik „x / max” wszędzie tak samo: liczba Mindset zielona, „/ max”
  Lato mniejsze i wygaszone, ten sam odstęp wokół ukośnika („6 / 8” = „9,3 / 11”).
- **S44 nagłówki sekcji większe i zielone (20.10.2026):** „Trzy wnioski”, „Cztery obszary” itp. większe, zielone
  (heading-accent); nazwy obszarów w kartach ok. 3 px większe.
- **S45 bliskość (gestalt) (20.10.2026):** etykieta należy wizualnie do swojej danej: werdykt „Bardzo dobrze” tuż nad
  albo pod paskiem, nazwa pytania o połowę bliżej swojego paska; odstęp między grupami większy niż w grupie. Bez
  wdów (jedno słowo w ostatnim wierszu nagłówka).
- **S46 telefon: wynik jako blok danych (20.10.2026):** na telefonie liczba wyniku po lewej w wyraźnym prostokącie
  (pigułka/kafel), ikona nad tytułem; spójny szablon z resztą strony (liczby po lewej).
- **S47 liczniki z opisem (20.10.2026):** pigułka „6 z 8” zawsze z wyjaśnieniem (np. „6 z 8 ankietowanych”).
- **S48 przyciski w jednym rzędzie (20.10.2026):** „Przyciski wszędzie nie są równo ułożone w jednym wierszu.” Grupa
  akcji wiersza zawsze w jednym rzędzie, równe wysokości; na telefonie: główna akcja na pełną szerokość, pozostałe w
  jednym rzędzie obok siebie (równe kolumny siatki) albo w menu „⋯” — nigdy schodkowe zawijanie 2+1.
- **S49 biblioteka jako wysuwany panel (20.10.2026):** na telefonie biblioteka bloków = panel wysuwany z boku, kategorie,
  małe podglądy bloków (jak Elementor, ale nie kopia); więcej odstępów w kreatorze na telefonie.
- **S58 tryb prosty bez kolorowych przycisków (20.10.2026, program „Stwórz prezentację”):** „Widzę, że aplikacja do
  konwersji wygląda brzydko. Na pewno niepotrzebne są te przyciski kolorowe w trybie prostym.” Reguła (interpretacja
  agenta; 20.10 potwierdzone: chodziło o pastelowe kafle PNG / JPG / AVIF w trybie prostym Photo Resizera): w najprostszej ścieżce widoku nie stawiaj rzędu kolorowych
  kontrolek (duże zielone przełączniki, żółte znaczki, kafle-przyciski); ustawienia rzadkie chowaj pod „Więcej
  ustawień”, kontrolki DS w spokojnej wersji (checkbox / radio z białym wnętrzem).
- **S50 akcja = widoczny skutek w miejscu (20.10.2026):** „+ z banku nie działa — albo działa, ale nie wiedziałem, że
  wyświetla się po prawej.” Przycisk otwiera wybór tuż przy nim (popover / rozwinięcie w miejscu) albo wyraźnie wskazuje
  i podświetla miejsce, gdzie coś się pojawiło. Nigdy cicho po drugiej stronie ekranu.
- **S51 przeciąganie (20.10.2026):** w trakcie drag & drop przyciemnij (fade 0,15 s) wszystko, na co nie wolno upuścić;
  miejsca docelowe wyraźnie zaznaczone.
- **S52 części bloku razem i zwijane (20.10.2026):** „zachowania do zaznaczenia muszą być częścią pytania, tego
  segmentu. Musi to się dać ZWINĄĆ i rozwinąć, bo zajmuje w chuj miejsca.” Elementy należące do jednego bloku (obszar:
  pytania + zachowania + komentarz) leżą w jednej karcie; długie listy (zachowania, opisy) domyślnie zwinięte do
  jednego wiersza podsumowania („Zachowania: 6 · 2 · 4 ▸”), rozwijane klikiem.
- **S53 nigdy nie blokuj dodawania (20.10.2026):** „mimo wyboru głównej ankiety NIGDY nie blokuj żadnej możliwości
  dodawania kolejnych bloków pytań. Nigdy.” Żadnych wyszarzonych bloków ani komunikatów „Ukryto: …” w bibliotece.
- **S54 podpowiedź znaczenia (20.10.2026):** „jak najadę na obszary, to nie wiem, co one znaczą.” Każda karta pojęcia
  z banku (obszar, zestaw) ma krótki opis, czego dotyczy, widoczny na karcie lub po najechaniu; pojęcie „obszar”
  wyjaśnione jednym zdaniem („kategoria pytań na jeden temat, etap ankiety”).
- **S55 szeroki ekran (20.10.2026):** narzędzia robocze (kreator) rozciągają się z oknem do 2540 px szerokości;
  progi tablet/telefon bez zmian.
- **S56 panel boczny chowany (20.10.2026):** panel boczny (biblioteka) ma przycisk schowaj/pokaż; gdy schowany, a akcja
  zmienia jego treść, przycisk pokazu pulsuje/rozjaśnia się (fade, krótko), żeby było widać, że tam coś się zmieniło.
- **S57 komplet opisów skali (20.10.2026):** suwak 1–11 zawsze ma opisane wszystkie 11 poziomów (pasma: 1–3 Znaczne
  trudności, 4–6 Wymaga poprawy, 7–8 Zgodne z oczekiwaniami, 9 Bardzo dobrze, 10 Doskonale, 11 Ponad oczekiwania);
  nigdy komunikat „ten poziom nie ma opisu”. Brakujące uzupełnia się samo.
- **S59 obrysy przycisków lżejsze (20.10.2026, przy Photo Resizerze):** „Pamiętaj o tym, żeby obrysy przycisków
  transparency 50%, nie takie mocne. Wszędzie. Ogólnie, to ogólny styl Dobrej Kalorii.” Przycisk drugorzędny (biały
  z obrysem) ma obrys `btn2-border` = `grey-500` (#868E96, jak obrys checkboxa) zamiast `ink-900` (#222222) we wszystkich
  stylach jasnych; tekst przycisku zostaje #222222. Tokeny 2.0.10.
- **S60 odstęp między krokami ekranu ~70 px (20.10.2026, Photo Resizer):** „Pomiędzy sekcjami 2 i 3 zrób odstępy od
  sekcji 70 px.” Kolejne kroki / sekcje ekranu jednej czynności oddzielaj ok. 70 px.
- **S61 działający ekran zostaje (20.10.2026, DAM):** przy 4 ekranach DAM user odrzucił WSZYSTKIE warianty („Wszystkie
  wersje są okropne. Aktualna jest najlepsza”; „Żadna nie jest dobra, obecna jest najlepsza”). Reguła: ekranu, który
  działa i był już dopracowywany w rundach, nie przebudowuj - poprawiaj tylko konkretne wady (kolor, jeden przycisk).
  W rundzie /design dla takiego ekranu warianty = A + jedna punktowa zmiana, nie nowy układ.
- **S62 lista to lista, nie kafelki (20.10.2026, DAM eksplorator):** „W ogóle nie. Żadne kafelki. Nic z tego mi nie
  pasuje.” Lista produktów / plików zostaje listą wierszy; nie zamieniaj jej w kafle ani karty.
- **S63 akcje wiersza: jeden przycisk z listą (20.10.2026, DAM):** „Tam jest tak wielki tłok z tym F X D. To powinno być
  tak, że to jest jeden przycisk, nazwany jakoś, np. Zmień wersję, i wtedy można z listy rozwijanej wybrać F - Ukończona,
  X - Archiwalna, D - Demo.” Kilka jednoliterowych przycisków stanu w wierszu = jeden przycisk z nazwą czynności i lista
  rozwijana z pełnymi nazwami (skrót + nazwa).
- **S64 metki nie biją po oczach (20.10.2026, DAM pulpit):** „Zmieniłbym kolor marketing w Asanie na jakiś lżejszy, bo ten
  bije po oczach. Może coś z szarością.” Metki / pigułki kategorii w listach: stonowane, przygaszone (odcień z szarością),
  nigdy nasycony turkus / cyjan na całą szerokość wiersza.
- **S65 bez czarnych obrysów i ciężkiego wyszukiwania (20.10.2026, DAM ustawienia):** „Widać, że wersja B jest okropna, bo
  ma ten obrys czarnego na przycisku, a my tego nie chcemy. I tak samo pasek wyszukiwania jest bardzo toporny.” Potwierdza
  S59; pole wyszukiwania lekkie (jasne tło lub cienka jasna linia, bez grubego zielonego obrysu i dużego przycisku „Szukaj”).
- **S58 rozwiń/zwiń widoczne (20.10.2026):** „rozwiń i zwiń powinno być znacznie lepiej widoczne.” Przełącznik zwijania
  to przycisk-pigułka z podpisem i chevronem (zielony obrys 1,5 px, tekst zielony pogrubiony, hover: pełna zieleń),
  wyrównany do prawej w wierszu nagłówka; nigdy sam mały link ani sama ikona.
- **S59 bez żargonu w metkach (20.10.2026):** „bank: Ogólna ocena… jest niepotrzebne”, „ocena 360 nie jest potrzebna”.
  Metka pokazuje samą nazwę (np. typ obszaru „Komunikacja”) z ikoną „i”; znaczenie w podpowiedzi zwykłym językiem
  (co z tego wynika dla respondenta). Nagłówek bloku: „Obszar 1”, bez dopisków technicznych.
- **S60 listy wyboru z oddechem (20.10.2026):** „za bardzo skondensowany… napisy nachodzą na siebie, nie ma paddingu”.
  Wiersz listy wyboru = biała karta z obrysem, padding min. 14×18 px, odstęp 10 px między wierszami, nazwa 16 px, opis
  14 px / 1,5. Wiersze w przewijanej liście nigdy się nie ściskają (`flex: none`).
- **S61 grupy główne daleko od siebie (20.10.2026):** „Oddal o 100 px od siebie obszary. Nowy obszar ma być wyraźnie
  zaznaczony, większa czcionka.” Główne grupy (obszary) ~140 px odstępu, zielony pasek 4 px u góry karty, większy
  nagłówek grupy i tytuł; elementy opcjonalne bloku (np. komentarz) mają przełącznik wł./wył. w miejscu.
- **S62 globalne style, nie lokalne (20.10.2026):** „Musisz stosować GLOBALNE style.” Zaznaczenie, przewijanie, przyciski
  potwierdzenia biorą wygląd z jednej definicji w CSS globalnym (`src/index.css` / tokeny), nie z lokalnych wariantów.
- **S63 paski przewijania w stylu DK (20.10.2026):** „scrolle są takie szare i beznadziejne.” Pasek przewijania globalnie:
  cienki (8 px), tor jasny (L1), uchwyt zielony marki z zaokrągleniem, bez strzałek; `scrollbar-color` + `::-webkit-scrollbar`.
  Treść nie wchodzi pod pasek: wewnętrzny odstęp po stronie paska (`scrollbar-gutter: stable` + padding).
- **S64 zaznaczone = TYLKO zielony obrys (20.10.2026, przypomnienie S26):** zaznaczona pozycja listy/karty: biała,
  zielony obrys 2 px, znacznik ✓; bez zielonego tła.
- **S65 „Gotowe” żółte (20.10.2026):** przycisk zamykający/zatwierdzający panel wyboru (popover) = żółty `cta`.
- **S66 ikony i bez powtórzeń (20.10.2026):** pozycje listy zestawów mają ikony (rozpoznawalność); w opisach pozycji nie
  powtarzaj stałego wstępu (np. „7: Zgodne z oczekiwaniami.”), pokaż samą treść.
- **S67 kolejność i oddech w nagłówku bloku (20.10.2026):** przyciski nagłówka (Zwiń, Dobierz z banku) w jednym rzędzie
  z tytułem, nigdy nie „wędrują” pod napisy; akcja dotycząca listy stoi NAD pytaniem do respondenta, a pytanie ma
  ~50 px odstępu od góry. Gdy mało miejsca: więcej oddechu, nie ciaśniej.
