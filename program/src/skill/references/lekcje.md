# Lekcje z iteracji (24-28.09.2026, kulki z kreatyną) - czytaj PRZED budowaniem

Każda lekcja: objaw -> przyczyna -> reguła. To są błędy, które już raz popełniłem; nie powtarzaj ich.

## A. Czego chce zespół (decyzje usera)

| # | Decyzja | Skąd |
|---|---|---|
| A1 | Wzór stylu nr 1 = **sklep dobrakaloria.pl** (biel/krem, zaokrąglone karty, prawie czarne nagłówki Mindset, zieleń, metki cenowe ze ściętymi rogami, żółte CTA, drobne ilustracje składników wokół paczek) | 28.09 "wzoruj się szczególnie na sklepie, to ważne" |
| A2 | **Zero plam / bąbelków / kół za produktem.** Tło za paczką = nic (albo karta sklepowa). Cień pod paczką OK | 28.09 "usuń te bubble za produktem" |
| A3 | Wokół paczki **małe, miłe elementy** (kawałki owoców, kulki, listki), nie duże ilustracje (szklanka coli z TIF była "za duża") | 24.09 |
| A4 | Okładka: **duże logo na zielonym podziale** (wymóg szefowej), ale ładniej niż stary wzór: 3 warianty w `s_cover` | 24.09 |
| A5 | Czcionka treści: **Lato** (nie Nunito). Nagłówki: Mindset | 28.09 |
| A6 | Nie pokazujemy porównań wygranych koncepcji opakowań - lepiej **osobny slajd dla każdego smaku** | 24.09 |
| A7 | Delikatne animacje: **Morph** | 24.09 |
| A8 | Kolory i czcionki mają dać się zmienić **globalnie** | 28.09 |
| A9 | Styl "fresh" (B) bardzo się podobał; "szablon" klasyczny (A) nadal potrzebny. **29.09: B usunięte - robimy tylko "stary styl" (A) i "nowy styl" (C)** | 24.09 / 29.09 |
| A15 | **Szablon = teksty-podpowiedzi w [nawiasach]** ("[Nazwa produktu]", "[Tytuł: wniosek]", "00%"), żadnych przykładowych treści produktu | 28.09 |
| A16 | **Bez przycisków CTA** ("Zobacz więcej") - w prezentacji nie da się kliknąć | 28.09 |
| A17 | **Morph oszczędnie**: tylko między kolejnymi slajdami tego samego układu (np. karty smaków), reszta bez przejść; szablon bez żadnych przejść | 28.09 |
| A18 | **Kolejność treści handlowej (wzór: ręczna wersja usera `DK_KULKI z kreatyną.pptx`, 29.09):** okładka -> linia smaków ("Trzy smaki na start") -> co wyróżnia (ikony + 3 paczki) -> skład (kafle) -> **edukacja o składniku** (claim + film/podcast) -> **edukacja: dlaczego to ważne** (akapit w karcie) -> przerywnik "Badanie" -> wyniki -> koniec. Karty każdego smaku user usunął (krótka prezentacja: linia smaków wystarcza) | 29.09 |
| A19 | **Etykiety nad tytułem (kicker) prawie nigdzie.** Żółte pigułki "PRODUKT / PORTFOLIO / SKŁAD" usunięte; zostaje tylko tam, gdzie niesie informację ("BADANIE KONSUMENCKIE"), jako zwykły beżowy tekst | 29.09 |
| A20 | Okładka: **3 paczki** + nad tytułem "NOWOŚĆ" jako zielony Mindset (bez pigułki), bez podtytułu i bez listy smaków | 29.09 |
| A21 | Karta linii smaków: packshot + drobne elementy, kreska, "Kulki z kreatyną arbuz", metka "65 G". **Bez znaczka NOWOŚĆ i bez opisu** | 29.09 |
| A22 | Skład: tylko cechy, których nie było wcześniej (1 g kreatyny jest już w "co wyróżnia" -> 3 kafle), kafle **wyśrodkowane**, same nagłówki bez podpisów | 29.09 |
| A23 | Wyniki badania bez wiersza "wybiera nasz produkt spośród 4 koncepcji" (zgodnie z A6); przed nazwą grupy bez kropki | 29.09 |
| A24 | **Film = zaokrąglona ramka.** User wstawił podcast YouTube jako zrzut + link (klik w pokazie otwiera przeglądarkę). Tytuł nad filmem w beżu Mindset ("Zapraszamy do odsłuchania podcastu..."). Rogi mają być zaokrąglone jak karty | 29.09 |
| A25 | Opis/ciało tekstu na slajdach edukacyjnych w beżu (Akcent 5), wyśrodkowane w karcie claimu; długi akapit w kremowej karcie z drobnymi owocami przy krawędziach | 29.09 |
| A26 | **Typografia PL zawsze**: bez zawieszek (a i o u w z) na końcu linii, bez jednego słowa w ostatniej linii (sieroty/wdowy/bękarty), bez myślnika na początku linii. Wbudowane w generator + test `verify.ps1` na liniach z PowerPointa | 29.09 |
| A10 | **Żółte elementy = prostokąt z lekko zaokrąglonymi rogami** (przycisk "ZOBACZ WIĘCEJ"), NIE ścięte rogi. Ścięta z LEWEJ jest tylko zielona **metka ceny**; znaczki NOWOŚĆ/BESTSELLER mają ostre końce | 28.09 zrzuty sklepu |
| A11 | Teksty drugorzędne (etykieta nad tytułem, podpisy) w beżu **#AD8767** "pod tło" - user sam tak przemalował slajd | 28.09 |
| A12 | **Więcej "światła"**: marginesy 2,4 cm, odstęp kart 0,7 cm, treść od 5,3 cm | 28.09 |
| A13 | Ikony **liniowe, zielone** (jak w sklepie: gwiazdka, uśmiech, kciuk, serce, listek) przy listach zalet; zielone nagłówki Mindset przy ikonach ("Skład produktu") | 28.09 |
| A14 | Tabele wartości jak w sklepie: nagłówek bez tła, co drugi wiersz kremowy | 28.09 |

## B. Błędy techniczne i ich przyczyny

| Objaw | Przyczyna | Reguła |
|---|---|---|
| User "nie widzi poprawek" | miał otwarty stary PPTX / podgląd PNG z cache | Po przebudowie podaj godzinę zapisu pliku i każ zamknąć/otworzyć plik; pokaż zrzut przed/po |
| "słodko-\|kwaśne" łamane na łączniku | PowerPoint łamie na "-"; żaden font (Mindset, Lato, Nunito) nie ma U+2011 | Łam sami tylko na spacjach (`lines_for()`), wstawiaj linie jako akapity |
| Samotne słowo w ostatniej linii | brak kontroli sierot | `lines_for()` przenosi ostatnie słowo poprzedniej linii |
| Pigułka "WYBÓR KONSUMENTÓW" w 2 liniach | szerokość liczona dla małych liter, bez rozstrzału | `pill_w()` mierzy WERSALIKI + `spc` na znak |
| Mindset mierzony za wąsko/szeroko | Mindset jest wersalikowy | `text_w_emu()` mierzy `.upper()` tylko dla Mindset |
| Tekst etykiet smaków wyszedł poza slajd | brak zawijania rzędu etykiet | etykiety zawijają się do nowej linii (`text_block`) |
| Opis produktu ucięty w pół zdania | obcinanie linii do dostępnej wysokości | nie obcinaj - skróć treść w specu, żeby się mieściła |
| Biały tekst ozdobnika szablonu niewidoczny | ozdobniki DK_WZOR są białe, projektowane na zieleni | pod białym tekstem zawsze zielona ramka (`callouts` polska dodaje "box") |
| Logo niewidoczne na jasnym tle | `logo_white_box.png` ma przezroczyste litery | na jasnym tle `logo_green_box.png`; white_box tylko na zieleni (litery = kolor panelu, więc zmieniają się z motywem) |
| Kontrast opisów 3,06:1 | "muted" = Tekst 1 rozjaśniony o 36% | jasność 0,18 -> ≥5,1:1 na wszystkich tłach; licz kontrast skryptem, nie na oko |
| Karta wprowadzenia "ma obrazek" | jedyny obraz w karcie to logo Kubara | karty NIGDY nie mają zdjęć produktu - nie szukaj tam packshotów |
| Drukarski TIF się nie otwiera | CMYK + alfa skojarzona, 100+ MB, PIL nie czyta | `prep_images.py tif` (tifffile, CMYK->RGB, odwrócenie premultiply) |
| Packshoty z Excela na białym tle | zdjęcia wklejone do arkusza | `prep_images.py cutout` (zalewanie od krawędzi) + sprawdź na kolorowym tle |
| Heredoc w bashu "unexpected EOF" | dużo cudzysłowów/nawiasów w kodzie | dłuższe łatki: zapisz skrypt Write-em do scratchpada i uruchom |
| `rm -r` zablokowany | reguła bezpieczeństwa CLAUDE.md §0 | nieaktualne wersje PRZENOŚ do `_robocze\poprzednie wersje (data)`, nie kasuj |
| Nie wiadomo, czy Morph działa | XML to nie dowód | `verify.ps1` pyta PowerPoint: EntryEffect **3954 = Morph wg obiektów** (potwierdzone empirycznie: PowerPoint zapisał `p159:morph option="byObject"`) |
| **Tekst nachodził na paczki na okładce C** (3 paczki szersze niż jedna) | scena ustawiana na sztywno, bez znajomości stref tekstu; miniatury nie pokazały problemu | `scene(..., avoid=[strefy])` + `fit_trio()`; test kolizji w `verify.ps1` z wynikiem 0 jako warunek oddania |
| **Kulki czekoladowe z biblioteki marki w prezentacji kulek z kreatyną** | wziąłem "KULKI Ugryzione.tif" z biblioteki (inny produkt - kulki kakaowe) | element produktu bierz TYLKO z folderu produktu (`Elementy\`); z biblioteki marki tylko owoce/liście. Zdjęcia z sesji na czarnym tle -> `prep_images.py cutout_dark` |
| Kropki przed etykietami | mój wymysł, nie ma ich w sklepie | etykiety bez kropek; wyróżnienia tylko z elementów sklepu (pigułki filtrów, przyciski, znaczki, ikony) |
| Gdy tekst mówi o 3 smakach, pokazywałem 1 paczkę | leniwe użycie jednego packshotu | cała linia = 3 paczki (`image: [arbuz, cola, mango]`) |
| Beż AD8767 ma tylko 3,1:1 | kolor "pod tło" jest z natury jasny | AD8767 tylko dla tekstu dużego (≥14 pt bold albo ≥18 pt); drobny tekst = ten sam beż przyciemniony 30% (#7D5E44, ≥4,87:1 na wszystkich tłach) - tokeny `tan` / `muted` |
| **Nadpisałem ręczne poprawki usera w C (28.09, 10:09:56) - drugi raz tego dnia** | przebudowa bez sprawdzenia, czy ktoś edytował plik; widziałem plik blokady `~$` i zignorowałem | `scripts/guard.py` (wbudowany w build_dk, build_deck, render.ps1): zapisuje SHA-256 każdego naszego zapisu; plik zmieniony ręcznie, nieznany albo otwarty -> NIE nadpisujemy, wynik idzie do "(nowa wersja)". Nigdy nie obchodź tej blokady. Ręczne poprawki usera to wzorzec do nauki: przeczytaj je, zanim cokolwiek przebudujesz |
| Moja przebudowa nadpisała ręczną zmianę usera w szablonie | generator odtwarza plik od zera | zanim przebudujesz plik, sprawdź datę modyfikacji; zmianę usera wbuduj w generator i powiedz o tym wprost |
| Po zwiększeniu marginesów kolidowały karty produktu | pozycje liczone od stałych, a obszar treści zmalał | pozycje w kartach licz od góry karty (y0 + ...), tekst przepływa linia po linii; po każdej zmianie odstępów przejrzyj WSZYSTKIE slajdy |
| **Zaokrąglony film "sam z siebie" po wstawieniu w slot** - nie działa | test w PowerPoint 29.09: film wklejony w pusty slot multimediów o kształcie zaokrąglonym dostaje `prstGeom rect` (kształt slotu się NIE dziedziczy) | zaokrąglenie nadaje generator na samym filmie (`prstGeom roundRect`, sprawdzone: AutoShapeType=5, rogi na renderze). Podmiana filmu przez usera: **Malarz formatów** ze starego filmu na nowy przenosi zaokrąglenie 1:1 (sprawdzone COM PickUp/Apply), albo Formatowanie wideo > Kształt wideo. Link do YouTube = zaokrąglony OBRAZ z hiperłączem: "Zmień obraz" zachowuje kształt i link |
| Łatka w Pythonie pisana heredokiem zapisała PRAWDZIWY znak nowej linii zamiast ukośnika-n, a w regexie znak sterujący zamiast ukośnika-1 (stąd `_x0001_% DODATKU CUKRU` na slajdach; 4x 29.09) | heredoc w tym środowisku zjada jeden poziom ukośników | kod z ukośnikami (regex, znaki nowej linii, ścieżki) zapisuj narzędziem Write do pliku i uruchamiaj plik; po każdej łatce `ast.parse` + test wartości |
| Scalanie linii w jeden akapit (szablon) zlepiło osobne akapity i zrobiło sierotę w nagłówku | heurystyka "wszystko w jeden akapit" | scalaj tylko linie, które NIE kończą się `] . ? ! :`; nagłówków Mindset nie scalaj |
| **"Okłamałeś mnie - film jest grafiką, nie da się go uruchomić"** (29.09) | wstawiłem miniaturę YouTube jako obraz z hiperłączem i nazwałem to filmem; sprawdziłem tylko kształt i link, nie odtwarzanie | nie nazywaj niczego "filmem w slajdzie", zanim nie zobaczysz go odtwarzanego w pokazie. Stan końcowy (patrz wiersz o błędzie 153): YouTube = miniatura + przycisk + podpis "Kliknij - film otworzy się na YouTube" (uczciwie nazwany link); plik mp4 = osadzony film z zaokrąglonymi rogami |
| Wideo online YouTube wstawione przez PowerPoint "nie działa" (29.09) | YouTube odrzuca odtwarzacz PowerPointa - błąd 153 (brak nagłówka Referer); plik był poprawny | film z YouTube = czysta miniatura (img.youtube.com/vi/ID/maxresdefault.jpg) + ▶ + podpis "Kliknij - film otworzy się na YouTube", link na wszystkich 4 elementach; gra w przeglądarce |
| User: "nie zapisuj nowa wersja, edytuj na istniejących" | guard.py przekierowywał każdy zapis do "(nowa wersja)", bo pliki nie miały zapisanej sumy | na polecenie usera: kopia zapasowa -> `guard.py record` -> budowa w miejscu; duplikaty "(nowa wersja)" do kosza (`send-to-trash.ps1`) |
| **Zielony ekran powitalny zostawał na wierzchu, okno nie wstawało** (program, 29.09) | `Splash()` PyInstallera (Tcl/Tk w tym samym procesie) gryzie się ze startem okna pywebview/WebView2; 1 z 3 startów nie wstał w 40 s | nigdy `Splash()` z pywebview. Plansza startowa = OSOBNY proces (launcher.cs): znika, gdy okno programu ma uchwyt, limit 120 s, bez TopMost |
| **Okno „brak odpowiedzi” zaraz po starcie, w stopce „Wersja —”** (zgłoszenie usera, 1.0.2; odtworzone: 2 z 4 startów) | klasa API miała PUBLICZNE pole `window`; pywebview (`util.get_functions`) przegląda rekurencyjnie wszystkie publiczne pola obiektu `js_api`, wchodził w obiekt okna i odpytywał jego właściwości, które czekają na wątek interfejsu | w klasie API tylko pola prywatne (`_window`, `_cancel`) i proste typy. Po poprawce 6/6 startów, gotowość po 3 s zamiast 8 s |
| Ogłosiłem „start działa”, a user dostał zawieszone okno | test sprawdzał tylko, czy okno się POJAWIŁO, i zabijał proces sekundę później; testy pełne szły inną drogą niż user (z portem debugowania, z pominięciem pliku startowego) | test startu = droga usera (plik startowy, bez portu) i czeka na GOTOWOŚĆ: wpis „most JS<->Python gotowy” w logu + okno odpowiada (`logs\start_test.ps1`), min. 5 powtórzeń, też z G: |
| Logo i czcionki nie ładowały się w spakowanym oknie (404) | pywebview serwuje UI własnym serwerem HTTP z korzeniem w katalogu `ui` - ścieżki `../skill/...` wychodzą poza korzeń | wszystkie zasoby UI trzymaj wewnątrz `ui\` (`ui\assets`); sprawdzaj `naturalWidth` obrazów i `document.fonts` na SPAKOWANYM programie, nie na atrapie |
| Most JS-Python gotowy dopiero po ~20 s | rejestracja `dom.get_element().events` w handlerze `window.events.loaded` - `evaluate_js` czeka 15 s na to samo zdarzenie | rejestruj w `webview.start(func, window)` po `window.events.loaded.wait()` |
| Pasek miniatur pokazywał 12 kafelków przy 7 slajdach | eksport PNG do katalogu, w którym leżały zrzuty poprzedniej, dłuższej wersji | przed eksportem usuń stare `s*.png` (własne pliki programu) |
| Packshoty przypisane do złych smaków | pliki w `Wizualizacje\` bez nazwy smaku ("Znak wodny (2).png") - dopasowanie po kolejności | program pokazuje miniaturę przy smaku (klik = zamiana), CLI `--packshoty "Smak=plik"`; zawsze obejrzyj `podglad_grafik.png` |
| User: teksty nie czarne, tylko "miły" ciemny ton | czerń 1F1F1F wyglądała twardo | Tekst 1 motywu sklepu = ciemna czekolada **3B2A20** (kontrast ~12:1); stary styl zostaje w ciemnej zieleni; to samo w oknie programu (`--ink`) |
| Znak wodny "ZAKAZ ROZPOWSZECHNIANIA DEMO" na paczkach | pliki od agencji w wersji demo | nie usuwaj znaku; zgłoś userowi, że przed wysyłką na zewnątrz trzeba podmienić pliki |

## C. Szablony myślenia, które zadziałały

1. **Najpierw rola, potem wzorzec.** "Co ten slajd ma zrobić dla handlowca?" -> dopiero potem układ. Handel = liczba + źródło + produkt.
2. **Wzór z żywego źródła.** Styl firmy czytaj ze zrzutu sklepu (playwright screenshot + próbkowanie pikseli), nie z opisu tekstowego strony - WebFetch nie widzi wyglądu.
3. **Jedno źródło treści, wiele stylów.** `make_specs.py` w `_robocze` generuje A/B/C z tych samych danych -> liczby nie rozjadą się między wersjami.
4. **Liczby z copy sprawdzaj w arkuszu** (np. 37% "w obu grupach" = 36,7% i 37,4%). Wartości "wspólne dla smaków" sprawdź we wszystkich kartach.
5. **Pętla: build -> render -> Read PNG -> lista wad -> poprawka.** Min. 2 przebiegi; sprawdzaj pełną rozdzielczość, nie tylko miniatury.
6. **Krytyk na końcu, ale weryfikuj jego zarzuty na obrazach** - krytyk z miniatur potrafi się pomylić (np. "brak 3. okładki z produktem", kiedy była).
7. **Globalne > lokalne.** Kolor/czcionka ustawione na pojedynczym obiekcie łamią zmianę globalną - używaj slotów motywu (`paint()` z tokenem) i czcionek `+mj-lt` / `+mn-lt`.
8. **Nie tnij zakresu po cichu.** Brakujące packshoty -> placeholder + informacja, nie pominięcie slajdu.
