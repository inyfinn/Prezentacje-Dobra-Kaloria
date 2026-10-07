# Design system Dobra Kaloria – aplikacje marki

Ten dokument opisuje, skąd bierze się wygląd narzędzi marki Dobra Kaloria (program „Stwórz prezentację”, Inyfinn Photo Resizer, DAM, prezentacje PPTX w „nowym stylu”), jakie obowiązują zasady i wartości oraz jak je zmieniać.

- **Data:** 2026-10-07 (stan odczytany z plików na komputerze służbowym, `C:\Users\krzysztof.wieczorek`; program „Stwórz prezentację” jest już w wersji 1.1.7).
- **Wersja tokenów:** 2.0.8 (`meta.version` w `tokens.json`; 2.0.8 z 07.10.2026 dodaje regułę S19, wartości jak w 2.0.7).
- **Wartości pochodzą z `tokens.json` – przy rozbieżności wygrywa `tokens.json`; ten plik jest opisem, nie źródłem.**

Skróty ścieżek używane niżej (`~` = `%USERPROFILE%`; dom `C:\Users\xpret`, praca `C:\Users\krzysztof.wieczorek`):

| Skrót | Ścieżka |
| --- | --- |
| `DS\` | `~\.claude\skills\ds-dobra-kaloria\` |
| `PREZ\` | `~\.claude\skills\prezentacje\` |
| `PAMIEC\` | `~\.claude\projects\d--Marketing---POLSKA-02---FIRMOWE-MATERIA-Y-PREZENTACJE\memory\` (tylko komputer służbowy, pamięć per folder projektu) |
| `WORK\` | `D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt\WORK\` (komputer służbowy) |
| `OBSZAR\` | `…\Marketing\- POLSKA\99 - WYMIANA\Krzysztof\--- Moj obszar pracy\` (praca: dysk `D:`, sprawdzone; dom: dysk `X:` według `~\.claude\knowledge\35-git.md` §5) |

---

## 1. Skąd wiadomo, czym jest design system DK

### 1.1 Źródła prawdy i ich hierarchia

| Nr | Źródło | Co ustala | Gdzie leży | Kto wygrywa przy sprzeczności |
| --- | --- | --- | --- | --- |
| 1 | **Sklep dobrakaloria.pl** – 7 zrzutów od usera z 06.10.2026 | Wygląd stylów jasnych: warstwy tła, kolor tekstu, zieleń, przyciski, ikony, tabele, zakładki, kroki | `DS\assets\sklep-2026-10-06\sklep-20.png` … `sklep-26.png`; pomiary pikseli: `DS\DOWODY-SKLEP.md`; odtworzony wzorzec: `DS\preview\sklep.html`, zrzuty `DS\preview\shots\70-sklep-*.png`, `71-sklep-*.png`; strona `https://dobrakaloria.pl/` | Wygrywa z każdą wcześniejszą regułą wyglądu i z gustem agenta. Zrzuty to „jedyne dowody”; strona na żywo służy wyłącznie do odczytania dokładnych wartości tego, co widać na zrzutach (`RUNDA-4-SKLEP-2026-10-06.md`). Przegrywa tylko z wyraźną, nowszą decyzją usera o marce (wiersz 2) i ze spisanymi „świadomymi odstępstwami” (1.3). |
| 2 | **Decyzje usera z datami** | Co jest regułą marki, co uchylone, co zostaje | `DS\ZALECENIA-USERA.md` (30.09–06.10.2026, dosłowne cytaty, wpisy uchylone oznaczone), `DS\RUNDA-4-SKLEP-2026-10-06.md` (nadpisuje kolory `RUNDA-3-2026-10-06.md`), `PAMIEC\styl-dk-reguly-globalne.md` | Nowsza decyzja wygrywa ze starszą. Decyzja o marce wygrywa z odczytem zrzutu (przykłady: tagi kolorowe S17, wielkość liter przycisków S18, jeden język kształtów). Uwaga usera o jednym motywie NIE jest regułą marki – trzeba zapytać (1.4). |
| 3 | **`tokens.json`** | Jedyne źródło WARTOŚCI: kolory, drabina, tagi, czcionki, odstępy, promienie, cienie, wymiary kontrolek, tokeny Qt | `DS\tokens\tokens.json` | Wygrywa z każdym opisem liczby: z tym plikiem, z `READY-*.txt`, z pamięcią, z komentarzami w aplikacjach. Gdy różni się od zrzutu sklepu: albo jest to spisane odstępstwo, albo błąd do poprawienia w `tokens.json`. |
| 4 | **Kontrakt reguł** | To, czego tokeny nie wyrażają: gdzie wolno dać obrys, ile poziomów tła, wielkość liter, rola każdej zieleni | `DS\tokens\READY-2.0.0.txt` (reguły S1–S19, plik dopisywany przy każdej wersji; S19 w 2.0.8) | Wygrywa ze starszymi opisami w `DESIGN_SYSTEM.md`, `IDENTYFIKACJA-WIZUALNA.md`, `components.md` rozdz. 1–24. |
| 5 | **Zatwierdzony wzorzec ekranu** – okno programu „Stwórz prezentację” 1.1.5 | Układ, proporcje, gęstość, wielkość liter przycisków w aplikacjach | `DS\assets\wzorzec-program-2026-10-06\program-1.1.5-01-start.png`, `…-05-opcje-gora.png`, `…-11-wynik.png` | W aplikacjach wygrywa ze sklepem tam, gdzie się różnią (S18: żółty przycisk w sklepie wersalikami, w aplikacjach zwykłą wielkością liter). User: „bierz przykład z PREZENTACJE, to wygląda doskonale”. |
| 6 | **Identyfikacja wizualna** | Logo, Mindset, Lato, plansza startowa, ikona aplikacji, liczenie zagnieżdżeń | `DS\IDENTYFIKACJA-WIZUALNA.md`, `DS\assets\fonts\` (Mindset.otf, Lato-Regular.ttf, Lato-Bold.ttf), `DS\assets\logo_green_box.png`, `logo_white_box.png`, `DS\assets\icons\` | Logo jest plikiem i nie jest przebarwiane. Mindset: licencja komercyjna firmy, Lato: OFL. |
| 7 | **Przepisy komponentów** | Kod CSS i QSS do skopiowania | `DS\components.md` rozdz. 25 (obowiązujący); rozdz. 1–24: geometria, stany i dostępność aktualne, kolory sprzed 2.0.0 | Przy sprzeczności z S1–S18 wygrywa kontrakt (wiersz 4). |
| 8 | **Dokumenty własne aplikacji** | Gęstość, układ, zachowanie, własne zmienne aplikacji | DAM: `OBSZAR\DAM---Dobra-Kaloria---inyfinn\bin\design-system\DESIGN_SYSTEM.md`, `bin\apps\web\assets\css\dam-tokens.css`; Resizer: `OBSZAR\Inyfinn Image resizer\BIN\dev\design-system\MASTER.md` | Wygląd stylów DK: wygrywa design system. Struktura i zachowanie aplikacji: wygrywają jej dokumenty. Motyw DK to nakładka, nie przebudowa. |

Kolejność z zadania (sklep → decyzje usera → `tokens.json` → wzorzec programu → identyfikacja) zgadza się z plikami, z jedną poprawką: wyraźna nowsza decyzja usera o marce stoi nad odczytem zrzutu, a `READY-2.0.0.txt` jest osobnym, obowiązującym kontraktem reguł.

### 1.2 Co z czego powstaje

| Krok | Plik | Rodzaj |
| --- | --- | --- |
| źródło | `DS\tokens\tokens.json` | edytowany ręcznie, jedyny |
| generator | `DS\scripts\build_tokens.py` (bez argumentów generuje wszystko; `--check` kontrast i drabina, kod 1 przy błędzie; `--ladder` wypisuje drabinę; `--copy-to <katalog>` kopiuje `tokens.css`; `--resizer <plik>` porównuje klucze motywu Resizera, tylko odczyt) | skrypt |
| web | `DS\tokens\tokens.css` – zmienne `--dk-*` na `:root` i `[data-theme="…"]` | generowany |
| Qt | `DS\tokens\tokens_qt.py` – słowniki `T`, `T_KREM_JASNY`, `T_ZIELEN_JASNY`, `T_DARK`, `T_KREM`, `VARIANTS`, `FONT_FILES` | generowany |
| opis | `DS\tokens\tokens.md` – tabele wartości, drabin, tagów i kontrastu | generowany |
| szkice motywów | `DS\themes\photo-resizer\dobra_kaloria.py`, `DS\themes\dam\dam-theme-dobra-kaloria.css` | generowane (nieużywane przez aplikacje, patrz 5.2 i 5.3) |

Kopie design systemu (stan 2026-10-07):

| Kopia | Wersja tokenów | Uwaga |
| --- | --- | --- |
| `DS\` (skill) | 2.0.8 | źródło |
| `~\repos\Prezentacje-Dobra-Kaloria\design-system\` | 2.0.8 | lustro robione przez `WORK\repo.ps1` |
| `~\.cursor\external\claude-skills\ds-dobra-kaloria\` (repo `inyfinn/cursor-global-config`) | 2.0.8 | lustro skilla, odświeżone 07.10.2026 (wcześniej 1.4.0); tu leży też ten plik |

### 1.3 Świadome odstępstwa od zrzutów sklepu (`DS\DOWODY-SKLEP.md`)

| Temat | Sklep | System | Powód |
| --- | --- | --- | --- |
| Promienie | panele proste, przyciski 2–5 px | przycisk, pole, metka 4 px; panel, karta, kafel 8 px | jeden język kształtów (wcześniejsza reguła usera) |
| Obrys checkboxa | `#ADB5BD` (2,1:1) | `#868E96` (3:1) | widoczność kontrolki |
| Zieleń przycisków | rodzina `#007936` / `#0F763E` / `#097038` / `#08743A` | jedna: `brand` `#007936`, hover `#00642E` | odcienie to wariacje strony, nie reguła |
| Strzałki karuzeli | okrągłe | kwadratowy przycisk-ikona 44 px | kółko tylko: awatar, kropka, gałka, radio |
| Style ciemne | brak na zrzutach | bez zmian względem 1.6.0 | brak dowodu |
| Grafika banera | „ZAMÓW” `#63B32E`, odznaka `#008142` | brak roli | to grafika marketingowa, nie interfejs |

### 1.4 Historia wersji i lekcja z rundy 3

| Wersja | Data | Co |
| --- | --- | --- |
| 1.0.0 | 29.09.2026 | design system wyciągnięty z okna programu „Stwórz prezentację” (`PAMIEC\design-system-dobra-kaloria.md`) |
| 1.3.0 / 1.3.1 | 30.09.2026 | dwa style kolorystyczne × tryb jasny i ciemny; 1.3.1 wymienia dziennik zmian DAM 2.5.2 |
| 1.4.0 / 1.4.1 | 30.09.2026 / brak daty | drabina powierzchni L0–L4 (OKLCH), tagi generowane, kontrola `--check`; 1.4.1: czerwień błędu `red-700` |
| 1.5.0 | 05.10.2026 | jasne style = drabina programu 1:1, tokeny `qt.*` |
| 1.6.0 | 06.10.2026 rano | runda 3 (G1–G9): „zero zieleni, brązowy tekst”, 29 ról kontrolek; kolory uchylone tego samego dnia |
| 2.0.0 | 06.10.2026 | runda 4 „sklep” (S1–S12): biel, szary panel, biała karta, tekst `#222222`, zieleń wraca; 6 nowych ról; żaden token nie usunięty ani przemianowany; kopia poprzednich wartości `DS\tokens\tokens-1.6.0.json` |
| 2.0.1 – 2.0.6 | 06.10.2026 | S13 budżet obrysów (2.0.1), S14 minimum poziomów i S15 ciemna zieleń (2.0.2), S16 ostrzeżenie bez brązu (2.0.4), S17 tagi w 8 barwach (2.0.5), S18 wielkość liter przycisków (2.0.6); 2.0.3: brak opisu w źródłach |
| 2.0.7 | 06.10.2026 | także style ciemne mają 8 rozróżnialnych barw tagów (`tags.note` w `tokens.json`) |
| **2.0.8** | 07.10.2026 | S19: tryb ciemny ma tę samą geometrię co jasny, zmieniają się tylko kolory; wartości tokenów bez zmian |

**Lekcja z rundy 3.** Reguła „zero zieleni, soczyste brązy” (1.6.0) powstała z uogólnienia pojedynczych uwag usera o zieleni w ciemnym, brązowym motywie na regułę całej marki. User odrzucił ją w całości, gdy zobaczył efekt: „Ok, ale miałeś zachować ten ciemnozielony dla nagłówków. I nie wszystko ma być CAŁKOWICIE zawsze beżowe.” Wniosek zapisany w `PAMIEC\styl-dk-reguly-globalne.md`: uwagi usera o jednym motywie nie są regułą marki – regułą marki jest sklep; gdy uwaga wygląda na sprzeczną ze sklepem, pytaj, czy dotyczy jednego motywu.

---

## 2. Zasady marki

### 2.1 Dwanaście zasad S1–S12 (`DS\tokens\READY-2.0.0.txt`; style jasne, ciemne bez zmian)

| Nr | Zasada | Dlaczego | Słowa usera albo dowód |
| --- | --- | --- | --- |
| S1 | Tło okna jest białe. Bieli jest najwięcej. Beż, ecru ani szary nigdy jako tło okna. | W sklepie tło strony to `#FFFFFF` (sklep-20, sklep-26). | „Jest więcej BIELI niż tych beży. […] Biały to tło.” |
| S2 | Sekcja = panel L1 (jasnoszary ciepły) bez obrysu i cienia; w panelu białe karty i pola (L2). Biała karta wprost na bieli dostaje linię 1 px `border`. | Tak zbudowany jest koszyk sklepu: panel `#F8F7F5`, w środku białe karty. | „Białe tło, lekko szare, a później znów białe kafelki wewnątrz. O to właśnie chodzi.” |
| S3 | Ecru i beż dopiero jako kolejny poziom kafla: L3 w białej karcie, L4 w kaflu ecru. Głębiej się nie schodzi. | Beż w sklepie pojawia się dopiero od poziomu kafla (kafle kategorii). | „Beże są tylko dla kolejnego poziomu kafelka, a nie od razu do stosowania jako tło.” |
| S4 | Tekst i tytuły prawie czarne `#222222`, pomocniczy `#666666`. Brąz nie jest kolorem tekstu w stylach jasnych. | Zmierzony tekst sklepu to `#222222`; wersję brązową user odrzucił. | O DAM w brązach: „wygląda okropnie. Jak SEPIA.” |
| S5 | Tytuły Mindset wersalikami (+0.01em). Ciemna zieleń `heading-accent` `#00642E`: tytuł główny widoku, nadtytuł sekcji, aktywna zakładka, podpis ikony. Prawie czarny `heading`: tytuły kart i sekcji z treścią, nazwy, tytuły okien dialogowych. | Tak rozkładają się nagłówki w sklepie (sklep-21, sklep-22). | „miałeś zachować ten ciemnozielony dla nagłówków” |
| S6 | Przycisk główny: zielony pełny `brand`, biały tekst Lato 700 wersalikami, promień 4. Drugorzędny: biały, obrys 1 px `#222222`. Żółty `cta` = jedna wyróżniona akcja widoku, tekst `#222222`. | Koszyk: „REALIZUJ ZAMÓWIENIE” `#007936`, „POWRÓT DO SKLEPU” biały z obrysem `#222222`; żółty „ZOBACZ WIĘCEJ” `#FFD821`. | „Przycisk »Wybierz folder« jest piękny.” |
| S7 | Ikony liniowe, kreska 2, zielone (`icon`). Przycisk-ikona kwadratowy 44 px, tło `icon-bg` `#F5F5F5`, promień 4. Kółko tylko: awatar, kropka, gałka, radio. Podpis: Lato 700, 11 px, wersaliki, `heading-accent`. | Ikony nagłówka sklepu są liniowe i zielone (`#007935`–`#0F763E`). | „Zwróć uwagę na ikony.” |
| S8 | Checkbox i radio: wnętrze białe zawsze, obrys 1,5 px `#868E96`; zaznaczony = zielony obrys i zielony znak. Przełącznik włączony zielony, gałka biała. Suwak: tor `#E9E9E9`, wypełnienie zielone, uchwyt biały z zielonym obrysem 2 px. Postęp i aktywny krok: `progress` `#47C33D`. | Checkbox w stopce sklepu jest biały z cienkim szarym obrysem; kroki koszyka `#47C33D` na `#E9E9E9`. | „checkboxy nie mogą być takie ciemne, mogą mieć ciemny obrys (daj trochę jaśniejszy), ale wnętrze musi być jasne” |
| S9 | Pole: białe, obrys 1 px `#868E96`, promień 4; fokus = obrys `brand` + poświata `shadow-focus-field`. Bez grubych obrysów. | Pola w sklepie mają cienką szarą ramkę; `#868E96` daje 3:1. | „NIE MA takich cholernie grubych obrysów.” |
| S10 | Linie podziału 1 px `#DDDDDD`. Tabela w pasy `zebra` / biel, bez linii pionowych. Zakładki: pod spodem linia 1 px `#222222`. | Zmierzone w sklepie: linie `#DDDDDD`, pasy `#F6F2EF` / `#FFFFFF` (sklep-22, sklep-23). | – |
| S11 | Metka pełna (licznik, cena, znaczek) = `brand` + biały tekst, promień 4. Tagi kategorii = `tag-N`, pigułki. | Flaga ceny i licznik koszyka w sklepie są zielone z białym tekstem. | Druga połowa („zielone odcienie tagów”) zastąpiona przez S17. |
| S12 | Linki w treści: `#222222`, pogrubione, podkreślone. Linki nawigacji: bez podkreślenia, aktywny lub hover zielony. | Tak wyglądają linki w opisie produktu (sklep-22). | – |

### 2.2 Reguły dopisane po 2.0.0 (obowiązują)

| Nr | Od | Treść | Słowa usera |
| --- | --- | --- | --- |
| S13 | 2.0.1 | Budżet obrysów. Obrys 1 px tylko na: polu, checkboxie i radiu, JEDNYM przycisku drugorzędnym w grupie, białej karcie na bieli, fokusie. Tagi, metki, pigułki filtrów, liczniki, panele, karty w panelu, kafle, przyciski-ikony: bez obrysu. Żadnej sepii: beż tylko jako L3/L4, nigdy jako obrys, metka czy tekst. | „bubble tagi wyglądają okropnie z tymi obrysami, za dużo obrysów” |
| S14 | 2.0.2 | Minimum poziomów. Kontener nie dostaje tła, jeśli wystarczy biel; w liście szare są dopiero pozycje; szary panel tylko dla grupy różnych białych kart lub pól; metadane bez tła; beż dopiero na 3. poziomie. Żadnych fioletów z motywu bazowego. | „po co beżowe, jak może być białe” |
| S15 | 2.0.2 | Elementy ciemne (pasek górny, toast, podpowiedź, licznik) mają tło `inverse-bg` `#00642E`, nie brąz i nie czerń. Fokus pola: 1 px `brand` + poświata 3 px, nigdy gruby ciemny pierścień. Aktywny segment, filtr, zaznaczony tag: `brand` z białym tekstem. | „Wlej tu więcej życia i koloru. […] Są tak ciemne zielone, że niemalże czarne.” |
| S16 | 2.0.4 | Ostrzeżenie: tekst `#222222`, znak = żółty kwadrat `cta` z ciemnym symbolem, tło `warning-bg` tylko dla samego komunikatu, bez obrysu. Błąd: `danger`. | – |
| S17 | 2.0.5 | Tagi w 8 różnych barwach, samo wypełnienie, jedna grupa tagów = jedna barwa. Zaznaczony tag: `brand` + biały tekst. Licznik „+16”: `#F5F5F5`. Ciepłe przyciemnienie pod dialogiem (`shadow-scrim`) zostaje. | „Powinny być jednak kolorki. […] Różnicuj kolory.” / „szczególnie to przyciemnienie brązowe” |
| S18 | 2.0.6 | Wersaliki tylko na przycisku głównym (zielonym) i jednym drugorzędnym z obrysem. Przycisk cichy, żółty i linki: zwykła wielkość liter, Lato 700. | z zatwierdzonego wzorca programu 1.1.5 |
| S19 | 2.0.8 | Ciemny = jasny, zmieniają się tylko kolory. Geometria, odstępy, rozmiary, liczba i układ kontenerów identyczne w stylu jasnym i ciemnym; reguły zależne od motywu mogą zmieniać wyłącznie tło, tekst, obramowanie, wypełnienie ikon i kolor cienia. Kontrola: prostokąt każdego elementu z tłem w jasnym = w ciemnym (różnica 0 px). | „tryb dark ma być dosłownie tym samym, co tryb light. Zmieniają się tylko kolorki. Nigdy nie dodawaj dodatkowych kafelków, teł, ani nie przesuwaj treści.” (07.10.2026) |

Zostaje z wcześniejszych rund: Mindset także w nazwach (+10), duży tekst (co najmniej 14–15 px), jeden język kształtów, okno nigdy większe niż ekran i nigdy przycięte (G7), brak zbędnych linijek-podpowiedzi.

---

## 3. Tokeny (wersja 2.0.8, wartości jak w 2.0.7)

Kolumna „Klucz” to ścieżka w `DS\tokens\tokens.json`. W komponentach używa się ról (`--dk-color-text`), nie prymitywów (`--dk-ink-900`) i nie wartości na sztywno.

### 3.1 Style i tryby (`themes-list`)

| Styl | Tryb | `data-theme` | Role | Drabina | Słownik Qt |
| --- | --- | --- | --- | --- | --- |
| Sklep Dobra Kaloria (domyślny) | jasny | `:root`, `dobra-kaloria` | `color.semantic` | `program` | `T` |
| Dobra Kaloria 1 · zieleń | jasny | `dobra-kaloria-zielen-jasny` | `color.semantic-zielen-jasny` | `zielen-jasny` | `T_ZIELEN_JASNY` |
| Dobra Kaloria 1 · zieleń | ciemny | `dobra-kaloria-zielen-ciemny` | `color.semantic-dark` | `zielen-ciemny` | `T_DARK` |
| Dobra Kaloria 2 · krem | jasny | `dobra-kaloria-krem-jasny` | `color.semantic-krem-jasny` | `krem-jasny` | `T_KREM_JASNY` |
| Dobra Kaloria 2 · krem | ciemny | `dobra-kaloria-krem-ciemny` | `color.semantic-krem` | `krem-ciemny` | `T_KREM` |

Trzy style jasne mają identyczne wartości ról; różni je tylko drabina. Niżej podane są wartości stylów jasnych.

### 3.2 Drabina powierzchni L0–L4 (`ladder.variants.<wariant>.surfaces` / `.borders`)

| Poziom | Co to jest | Zmienna | sklep (`program`, `zielen-jasny`) | ramka | `krem-jasny` | ramka |
| --- | --- | --- | --- | --- | --- | --- |
| L0 | tło okna | `--dk-color-surface-0` (= `bg`) | `#FFFFFF` | `#DDDDDD` | `#FFFFFF` | `#DDDDDD` |
| L1 | panel, sekcja | `--dk-color-surface-1` (= `surface`) | `#F8F7F5` | `#DDDDDD` | `#FDF8EC` | `#EADFC6` |
| L2 | karta lub pole w panelu | `--dk-color-surface-2` | `#FFFFFF` | `#DDDDDD` | `#FFFFFF` | `#DDDDDD` |
| L3 | kafel w karcie | `--dk-color-surface-3` | `#FDF8EC` | `#EADFC6` | `#F5ECD8` | `#DDD0B4` |
| L4 | kafel w kaflu | `--dk-color-surface-4` | `#F5ECD8` | `#DDD0B4` | `#F0E6CF` | `#D3C5A6` |

- Poziom = poziom rodzica + 1. L2 jest JAŚNIEJSZY od L1. L4 nie jest nakładką.
- Nakładki (menu, lista rozwijana, podpowiedź, modal) = rola `overlay` `#FFFFFF` + cień `shadow.toast` + ramka `border`.
- Kontrast tekstu i tekstu pomocniczego na poziomach sklepu (`tokens.md`): L0 15,91 / 5,74; L1 14,86 / 5,36; L2 15,91 / 5,74; L3 15,01 / 5,42; L4 13,54 / 4,89.
- Style ciemne liczone wzorem `L_n = L0 + n · dL` (OKLCH, `dL` 0,034; głębiej = jaśniej; L4 = nakładka). Wartości z `tokens.md`: zieleń ciemny `#0F2315` → `#192C18` → `#24341C` → `#303C21` → `#3D4427` (`L0` 0,235); krem ciemny `#120F0A` → `#1A1611` → `#231E17` → `#2C261E` → `#352E25` (`L0` 0,17).

### 3.3 Tekst i nagłówki (`color.semantic.*`)

| Rola | Prymityw | Wartość | Do czego |
| --- | --- | --- | --- |
| `text` | `ink-900` | `#222222` | tekst, linki w treści |
| `text-muted` | `ink-600` | `#666666` | tekst pomocniczy |
| `label` | `ink-800` | `#333333` | etykiety, nagłówek tabeli, podzakładki |
| `heading` | `ink-900` | `#222222` | tytuły kart, sekcji, nazwy, tytuły okien dialogowych |
| `heading-accent` | `green-900` | `#00642E` | tytuł główny widoku, nadtytuł, aktywna zakładka, podpis ikony |
| `on-brand`, `on-accent`, `on-inverse` | `white` | `#FFFFFF` | tekst na zieleni |
| `on-cta` | `ink-900` | `#222222` | tekst na żółtym |

### 3.4 Zielenie

| Rola albo plik | Prymityw | Wartość | Do czego |
| --- | --- | --- | --- |
| `brand`, `accent`, `focus`, `icon`, `check-mark`, `check-border-hover`, `slider-fill`, `slider-thumb-border`, `switch-on`, `step-active-bg`, `step-done` | `green-750` | `#007936` | zieleń interfejsu: przycisk główny, ikony, kropki, metki, fokus, kontrolki |
| `brand-hover`, `accent-hover`, `heading-accent`, `inverse-bg` | `green-900` | `#00642E` | hover przycisku, zielone nagłówki, ciemne elementy (pasek, toast) |
| `progress` | `green-450` | `#47C33D` | pasek postępu, aktywny krok |
| `brand-soft` | `green-100` | `#E9F2EC` | hover przycisku cichego i przycisku-ikony |
| `brand-soft-strong` | `green-200` | `#CFE0D4` | mocniejsze jasnozielone tło |
| (bez roli w stylach jasnych) | `green-700` | `#0F763E` | plansza startowa i ikona aplikacji (zatwierdzony wyjątek); zieleń interfejsu do wersji 1.6.0 |
| logo SVG | plik | `#008244` | `--dam-brand-green` w DAM; logo nie jest przebarwiane |
| logo PNG w programie | plik | `#006400` | plik (`DESIGN_SYSTEM.md` §9) |
| `brand` w stylach ciemnych | `lime-300` / `green-350` | `#A2D686` (zieleń ciemny) / `#4CC46A` (krem ciemny) | akcent ciemny |

**Sprawa trzech zieleni.** W interfejsie aplikacji rozstrzygnięta od 2.0.0: jedna zieleń `brand` `#007936` z hoverem `#00642E` (`DESIGN_SYSTEM.md` §9). Nadal otwarte: prezentacje PPTX używają `0F763E` (5.4), plansza startowa i ikona aplikacji zostają przy `#0F763E` jako wyjątek, logo ma własne wartości w plikach. `PAMIEC\design-system-dobra-kaloria.md` (29.09) podaje jeszcze `#0F763E` jako zieleń interfejsu – wpis nieaktualny, wygrywa `tokens.json`.

### 3.5 Żółty akcent, powierzchnie pomocnicze, linie

| Rola | Prymityw | Wartość | Do czego |
| --- | --- | --- | --- |
| `cta` | `yellow-450` | `#FFD821` | jedna wyróżniona akcja widoku |
| `cta-hover` | `yellow-500` | `#F6C700` | hover żółtego przycisku |
| (prymityw) | `yellow-400` | `#FFD42A` | `cta` stylów ciemnych, pasek planszy startowej |
| `surface-hover`, `zebra`, `btn2-hover-bg` | `stone-200` | `#F6F2EF` | hover, pasy tabeli, stopka |
| `strip` | `stone-150` | `#F8F4F1` | pasek menu |
| `overlay`, `check-bg`, `btn2-bg`, `slider-thumb`, `switch-knob` | `white` | `#FFFFFF` | nakładki, wnętrza kontrolek |
| `icon-bg`, `disabled-bg` | `grey-100` | `#F5F5F5` | tło przycisku-ikony i przycisku cichego, stan wyłączony |
| `border` | `grey-250` | `#DDDDDD` | linie podziału, ramka białej karty na bieli |
| `border-strong`, `step-idle-border`, `check-disabled-border` | `grey-300` | `#CED4DA` | mocniejsza linia, ramka pola ilości |
| `field-border`, `check-border`, `switch-off-border` | `grey-500` | `#868E96` | obrys pola i kontrolek (3,32:1 na bieli) |
| `switch-off`, `slider-track` | `grey-200` | `#E9E9E9` | tor przełącznika, suwaka, postępu |
| `btn2-text`, `btn2-border` | `ink-900` | `#222222` | przycisk drugorzędny |
| `accent-beige` | `tan-400` | `#AD8767` | wyłącznie dekoracja |

### 3.6 Tagi – 8 barw (style jasne)

Parametry w `tokens.json`: `ladder.variants.program.tag_hue` 152, `tag_offsets` `[0, -27, -57, -92, -127, -157, 38, 88]`, `tags.light.bg` L 0,93 C 0,06, `tags.light.fg` L 0,4 C 0,11, `tags.min_contrast` 4,6. Wartości hex liczy generator; przepisane z `DS\tokens\tokens.md`.

| Tag | Barwa | Hue | Tło `--dk-color-tag-N-bg` | Tekst `--dk-color-tag-N-fg` | Kontrast |
| --- | --- | --- | --- | --- | --- |
| tag-1 | zieleń | 152 | `#CBF4D5` | `#005729` | 7,28:1 |
| tag-2 | limonka | 125 | `#DFF0C4` | `#3B5001` | 7,45:1 |
| tag-3 | żółty | 95 | `#F4E8BB` | `#564700` | 7,45:1 |
| tag-4 | pomarańcz | 60 | `#FFE2CB` | `#6B3900` | 7,69:1 |
| tag-5 | czerwień | 25 | `#FFDFDC` | `#782A28` | 7,79:1 |
| tag-6 | róż | 355 | `#FFDEE9` | `#73294B` | 7,86:1 |
| tag-7 | morski | 190 | `#BAF5F1` | `#005350` | 7,40:1 |
| tag-8 | niebieski | 240 | `#D3ECFF` | `#014D73` | 7,45:1 |

Tag to samo wypełnienie i tekst, bez obrysu (`tag-N-border` zostaje w tokenach dla zgodności wstecznej). Bez fioletu. Jedna grupa tagów = jedna barwa; przypisanie grup do barw: patrz „Otwarte sprawy” pkt 8. Od 2.0.7 style ciemne też mają 8 barw (krem ciemny bez zieleni).

### 3.7 Stany

| Stan | Tokeny | Wartość |
| --- | --- | --- |
| hover powierzchni | `surface-hover` | `#F6F2EF` (nie kolejny poziom drabiny) |
| hover przycisku głównego | `brand-hover` | `#00642E` |
| hover przycisku cichego i przycisku-ikony | `brand-soft` | `#E9F2EC` |
| fokus (przycisk, kontrolka) | `focus`, `control.focus-width`, `control.focus-offset` | `#007936`, 2 px, odstęp 2 px |
| fokus pola | `brand` + `shadow.focus-field` | obrys 1 px + `0 0 0 3px rgba(0,121,54,.22)` |
| wyłączony | `disabled-bg`, `text-muted`, `check-disabled-border`, `check-disabled-mark` | `#F5F5F5`, `#666666`, `#CED4DA`, `#ADB5BD` (`grey-400`) |
| błąd | `danger`, `danger-soft` | `#C0262C` (`red-700`), `#FCE8E9` (`red-50`) |
| ostrzeżenie | `warning-text`, `warning-bg`, `warning-border` | `#222222`, `#FFF4D6`, `#EBCB6B` |
| zaznaczony tag, aktywny segment | `brand` + `on-brand` | `#007936` + `#FFFFFF` |

### 3.8 Typografia

| Klucz | Wartość |
| --- | --- |
| `font.display` | `"Mindset", "Arial Narrow", Impact, sans-serif` – nagłówki, zawsze wersaliki |
| `font.text` | `"Lato", "Segoe UI", Arial, sans-serif` – cała reszta |
| `font.mono` | `Consolas, "Cascadia Mono", "Courier New", monospace` |
| `font-size.sm` / `base` / `md` / `lg` / `xl` | 15 / 16 / 17 / 20 / 22 px |
| `font-size.display-sm` / `display-md` / `display-lg` / `display-hero` | 40 / 46 / 76 / 168 px |
| `line-height.display` / `tight` / `snug` / `base` | 1,02 / 1,25 / 1,35 / 1,5 |
| `qt.fs-body` / `fs-label` / `fs-hint` / `fs-eyebrow` | 15 / 14 / 14 / 14 px |
| `qt.fs-btn` / `fs-btn-primary` | 15 / 17 px |
| `qt.fs-title` / `fs-app-title` / `fs-dialog-title` | 22 / 20 / 26 px |

Tracking nie ma tokenu; wartości żyją w przepisach (`components.md` rozdz. 25): tytuły Mindset `.01em`, przycisk i etykieta `.02em`, podpis ikony `.03em`; etykieta sekcji (eyebrow) w programie `0,1em` (`DESIGN_SYSTEM.md` §10). Mindset nie ma małych liter ani twardej spacji – łamanie nagłówków ustawia się ręcznie. Polska typografia: na końcu wiersza nie zostają „a, i, o, u, w, z” ani pojedyncze słowa.

### 3.9 Odstępy, promienie, obrysy, cienie, ruch

| Grupa | Klucz | Wartość |
| --- | --- | --- |
| siatka | `space.1` … `space.6` | 4, 8, 12, 16, 20, 24 px |
| siatka | `space.8`, `10`, `12`, `14`, `16`, `20` | 32, 40, 48, 56, 64, 80 px |
| układ | `layout.wrap`, `layout.gutter` | 920 px, 24 px |
| tryb wygodny (kreator) | `layout.card-pad`, `card-pad-lg`, `section-gap`, `stack` | 32, 40, 40, 20 px |
| tryb zwarty (narzędzie) | `layout.card-pad-sm`, `section-gap-sm`, `stack-sm` | 20, 24, 12 px |
| Qt | `qt.pad-card`, `gap-cards`, `gap-stack`, `gap-row`, `margin-window` | 20, 16, 12, 10, 20 px |
| promienie | `radius.btn`, `sm`, `md`, `lg`, `pill` | 4, 4, 8, 12, 999 px |
| promienie Qt | `qt.radius-btn`, `radius-field`, `radius-card`, `radius-drop` | 4, 4, 8, 12 px |
| obrysy | `control.check-border-width`, `btn2-border-width`, `slider-thumb-border-width` | 1,5 px, 1 px, 2 px |
| obrysy Qt | `qt.card-border`, `field-border`, `focus-border` | 1 px, 1 px, 1 px |
| kontrolki | `control.h-min`, `h`, `h-lg`, `check-size`, `check-radius`, `stroke-icon` | 44, 48, 56, 20, 4 px, kreska 2 |
| kontrolki Qt | `qt.control-h`, `control-h-primary`, `control-h-sm` | 40, 48, 36 px |
| cień | `shadow.thumb` | `0 1px 2px rgba(34,34,34,.14), 0 4px 10px rgba(34,34,34,.10)` |
| cień | `shadow.raised` / `shadow.bar` | `0 1px 4px rgba(34,34,34,.16)` / `0 2px 8px rgba(34,34,34,.08)` |
| cień | `shadow.toast` | `0 10px 30px rgba(34,34,34,.22)` |
| przyciemnienie pod dialogiem | `shadow.scrim` | `rgba(59,42,32,.55)` (ciepły brąz, tylko style jasne) |
| ruch | `motion.fast`, `base`, `slow`, `ease` | .15s, .18s, .28s, ease-out |

Trybów wygodnego i zwartego nie miesza się na jednym ekranie. Program „Stwórz prezentację” używa wygodnego, Photo Resizer i DAM zwartego. Cienie tylko dla nakładek, toastów i uchwytów; panele i karty bez cienia.

---

## 4. Komponenty

Przepisy z kodem: `DS\components.md` rozdz. 25 (web CSS + Qt QSS), żywa galeria `DS\preview\sklep.html`. Niżej skrót.

| Komponent | Wygląd | Tokeny | Czego nie robić |
| --- | --- | --- | --- |
| Przycisk główny | Pełna zieleń, biały tekst Lato 700 15 px wersalikami, wysokość 48 px, promień 4. | `brand`, `on-brand`, `brand-hover`, `control.h`, `radius.btn`, `space.6` | Dwóch głównych w grupie; zielonego obrysu zamiast wypełnienia. |
| Przycisk drugorzędny | Biały, obrys 1 px `#222222`, tekst `#222222` wersalikami, hover `#F6F2EF`. | `btn2-bg`, `btn2-text`, `btn2-border`, `btn2-hover-bg`, `control.btn2-border-width` | Więcej niż jednego z obrysem w grupie (S13); obrysu zielonego albo brązowego. |
| Przycisk żółty | Jedna wyróżniona akcja widoku („Wybierz folder”, „Konwertuj”), tekst `#222222`, zwykła wielkość liter, 16 px. | `cta`, `on-cta`, `cta-hover` | Dwóch żółtych na widoku; wersalików (S18); żółtego tekstu na jasnym tle. |
| Przycisk cichy | Samo wypełnienie `#F5F5F5` na bieli albo białe na panelu, bez obrysu, zwykła wielkość liter, hover `brand-soft`. | `icon-bg`, `surface-2`, `text`, `brand-soft` | Obrysu; wersalików. |
| Pole | Białe, obrys 1 px `#868E96`, promień 4, wysokość co najmniej 44 px (Qt 40 px). Fokus: obrys `brand` + poświata. Wyszukiwarka: pigułka z zielonym obrysem. | `check-bg`, `field-border`, `radius.sm`, `shadow.focus-field`, `control.h-min`, `qt.control-h` | Grubego obrysu; ciemnego pierścienia fokusu; `outline: none` bez zamiennika. |
| Checkbox, radio | 20 px, promień 4 (radio koło), wnętrze białe także po zaznaczeniu, obrys 1,5 px (w QSS 2 px), znak zielony. | `check-bg`, `check-border`, `check-border-hover`, `check-mark`, `check-disabled-*`, `control.check-*` | Ciemnego wypełnionego kwadratu po zaznaczeniu. |
| Przełącznik | 48 × 28 px, tor wyłączony `#E9E9E9` z obrysem `#868E96`, włączony zielony, gałka biała. | `switch-off`, `switch-off-border`, `switch-on`, `switch-knob`, `shadow.raised` | Brązowego albo szarego stanu „włączony”. |
| Suwak, postęp | Tor 6 px `#E9E9E9`, wypełnienie zielone, uchwyt 22 px biały z zielonym obrysem 2 px. Postęp: 8 px, `progress` na torze. | `slider-track`, `slider-fill`, `slider-thumb`, `slider-thumb-border`, `progress` | Uchwytu w kolorze toru. |
| Panel, karta, kafel | Panel L1 bez obrysu i cienia, promień 8; w nim biała karta L2; w karcie kafel ecru L3; w kaflu L4. Biała karta wprost na bieli: linia 1 px. Lista: kontener bez tła, szare są pozycje. | `surface-0..4`, `border`, `border-subtle-N`, `radius.md`, `layout.card-pad*` | Beżowego, ecru albo szarego tła okna; cienia i obrysu na panelu; poziomu głębiej niż L4; tła „na oko”. |
| Tag (pigułka) | Wypełnienie `tag-N-bg`, tekst `tag-N-fg`, Lato 700 13 px, wysokość 26 px, bez obrysu. Zaznaczony: `brand` + biały tekst. | `tag-1..8-bg/-fg`, `radius.pill`, `brand`, `on-brand` | Obrysu; fioletu; dwóch barw w jednej grupie; koloru jako jedynego nośnika znaczenia. |
| Metka pełna | Cena, licznik, znaczek: zielona, biały tekst, promień 4, wysokość 28 px. | `brand`, `on-brand`, `radius.sm` | Beżowej albo żółtej metki. |
| Zakładki | Mindset 20 px wersalikami, aktywna `heading-accent`, nieaktywna `heading`, pod spodem linia 1 px `#222222`. Podzakładki: Lato 13 px wersalikami, aktywna z zieloną kreską 2 px. | `heading`, `heading-accent`, `text`, `label`, `brand`, `border` | Zakładek w ramkach albo kafelkach. |
| Segmenty, kroki | Segment: aktywny zielony z białym tekstem, nieaktywny jak przycisk cichy, bez obrysów. Kroki: paski 5 px, aktywny `#47C33D`, reszta `#E9E9E9`. | `brand`, `on-brand`, `icon-bg`, `progress`, `switch-off`, `step-idle-text` | Obrysów na segmentach; brązowego aktywnego kroku. |
| Menu boczne | Brak osobnego przepisu. Z istniejących zapisów: tło L1 (DAM), linki bez podkreślenia, aktywny albo hover zielony (S12), zaznaczenie bez grubego paska na krawędzi (`PAMIEC\styl-dk-reguly-globalne.md` pkt 10). | `surface-1`, `brand`, `text` | Fioletów z motywu bazowego; grubego paska przy krawędzi. |
| Okno dialogowe | Brak osobnego przepisu. Z istniejących zapisów: okno = `overlay` (biel) + ramka `border` + promień 12 + cień `shadow.toast`; pod spodem `shadow.scrim`; zawartość liczona od panelu L1; tytuł Mindset `heading` (Qt 26 px). | `overlay`, `border`, `radius.lg`, `shadow.toast`, `shadow.scrim`, `qt.fs-dialog-title` | L4 jako tło okna; czarnego albo szarego przyciemnienia w stylach jasnych. |
| Toast | Ciemna zieleń `inverse-bg` z białym tekstem, promień 8, cień; błąd na `danger`. Zamknięcie 44 px, `aria-live`. | `inverse-bg`, `on-inverse`, `danger`, `radius.md`, `shadow.toast` | Brązowego albo czarnego tła (S15); więcej niż 3 naraz; czerwieni dla ostrzeżeń. |
| Komunikat ostrzeżenia i błędu | Ostrzeżenie: tekst `#222222`, żółty kwadrat ze znakiem, tło `#FFF4D6` bez obrysu. Błąd: `danger` `#C0262C`. | `warning-text`, `warning-bg`, `cta`, `danger`, `danger-soft` | Bursztynowego brązu w tekście (S16). |
| Ikony | Lucide, liniowe, kreska 2, kolor `icon`, 20–24 px. Przycisk-ikona: kwadrat 44 px, tło `#F5F5F5`, promień 4. Odręczne ikony marki (skill `ikony-dobra-kaloria`) są do materiałów, nie do interfejsu. | `icon`, `icon-bg`, `control.stroke-icon`, `control.h-min`, `brand-soft` | Okrągłych przycisków-ikon; mieszania rodzin ikon; ikony bez nazwy dostępnej. |
| Plansza startowa | 560 × 330 px, tło `#0F763E`, logo w białym polu ok. 190 px, nazwa Mindset 34 px biała, kółko i „Uruchamiam program…”, pasek żółty `#FFD42A` na białym torze 27% krycia. | prymitywy `green-700`, `yellow-400`; `DS\assets\logo_white_box.png` | Przebarwiania na `brand`; `Splash()` PyInstallera (blokuje okno). |
| Ikona aplikacji | Zielony „liść” `#0F763E`: zaokrąglone narożniki lewy górny i prawy dolny (24%), białe litery Mindset (PR, RE, DAM). Generator `DS\scripts\ikony_aplikacji.py`. | `green-700`; `DS\assets\icons\<id>.ico`, `-256.png`, `-1024.png` | Rysowania ręcznie; innych liter niż w `APPS`. |

---

## 5. Aplikacja po aplikacji

| | Stwórz prezentację | Photo Resizer | DAM | Prezentacje PPTX |
| --- | --- | --- | --- | --- |
| Technologia | HTML/CSS/JS w oknie pywebview (WebView2) | PySide6, arkusz QSS | aplikacja web (HTML/CSS/JS, zmienne `--dam-*`) | python-pptx, sloty motywu |
| Wersja aplikacji | 1.1.6 (`WORK\wersja.txt`) | 2.6.6 (`BIN\WERSJA.txt`) | 2.5.8 (`bin\apps\web\version.json`) | skill `prezentacje`, motyw `shop` |
| Wersja DS w aplikacji | 2.0.6 (`src\ui\tokens.css`) | 2.0.7 (`palettes.py`) | 2.0.5–2.0.6 w stylach jasnych, przepisane ręcznie | brak – wartości wpisane osobno |
| Przepływ tokenów | automatyczny (kopia pliku) | półautomatyczny (skrypt) | ręczny | ręczny |

### 5.1 Program „Stwórz prezentację”

| Temat | Stan |
| --- | --- |
| Źródła | `WORK\src\ui\`: `index.html`, `style.css`, `app.js`, `tokens.css` |
| Skąd tokeny | `WORK\build.ps1`, krok 1b: kopiuje `~\.claude\skills\ds-dobra-kaloria\tokens\tokens.css` do `WORK\src\ui\tokens.css` (gdy skilla nie ma, zostaje dotychczasowy plik). `index.html` ładuje `tokens.css` przed `style.css`; `style.css` mapuje krótkie nazwy (`--ink`, `--l0`…`--l3`, `--yellow`) na `--dk-*`. |
| Wersje | `wersja.txt` 1.1.6, zbudowane 06.10.2026 14:02 (`WORK\logs\build.log`). Pamięć mówi o wydanym 1.1.5 – czy 1.1.6 jest wydane: niesprawdzone. `src\ui\tokens.css` ma 2.0.6; różnica do 2.0.7 to wyłącznie tagi stylów ciemnych, których program nie używa. |
| Co wdrożone | Styl domyślny (`:root`), tylko tryb jasny, tryb odstępów wygodny. Drabina: L0 strona i pasek akcji, L1 panele, L2 białe kafle w panelu, L3 ecru (miniatura w kafelku smaku). Żółty „Wybierz folder”, zielony przycisk główny (`.btn-primary.btn-brand`), drugorzędny biały z obrysem. Mindset i Lato z `src\ui\assets\fonts`. |
| Znane odstępstwa | Ikona w żółtym przycisku ma kreskę 1,6 (zostawiona celowo). Okno „Co teraz” (`.guide`) ma białą zasłonę 80%, nie `shadow.scrim`. Poza tokenami zostały `rgba(31,31,31,.3)` (cień gałki) i `rgba(255,255,255,.18)` (hover zamknięcia toasta). Komentarz w `index.html` mówi „kreska 1,6” – nieaktualny. |
| Rola | To zatwierdzony wzorzec dla pozostałych aplikacji (ekran „Gotowe!” w 1.1.5). |

Zmiana: `tokens.json` → `python scripts\build_tokens.py` → `WORK\build.ps1 -Bump` (sam odświeża `tokens.css`) → testy `WORK\logs\e2e_gui.py`, `start_test.ps1`, `launcher_test.ps1` → zrzuty przed i po → `WORK\wydaj.ps1`. Nowe krótkie nazwy dopisuj w `:root` pliku `style.css` jako aliasy `--dk-*`, nie jako wartości.

### 5.2 Inyfinn Photo Resizer

| Temat | Stan |
| --- | --- |
| Źródła | `OBSZAR\Inyfinn Image resizer\BIN\dev\src\inyfinn_resizer\app\themes\`: `__init__.py` (słownik `_THEME_TOKENS`), `app.qss`, `palettes.py`, `typography.py`, `fonts\` |
| Skąd tokeny | `BIN\dev\scripts\sync_design_tokens.py` czyta `~\.claude\skills\ds-dobra-kaloria\tokens\tokens_qt.py` (tylko odczyt) i nadpisuje w całości `palettes.py` (`ROLES`, `LADDER`, `TAGS`, `SHAPE`). `_theme_tokens()` zamienia role na znaczniki `@NAZWA@`; `app.qss` ma 111 znaczników i ani jednej wartości hex. |
| Wersje | 2.6.6 (`BIN\WERSJA.txt`, zbudowano 2026-10-06 16:23:15; `BIN\dev\pyproject.toml`). Nagłówek `palettes.py`: design system 2.0.7. Pamięć: 2.6.5 i 2.6.6 wydane. |
| Co wdrożone | Cztery motywy `dobra-kaloria-<styl>-<tryb>` (zieleń, krem × jasny, ciemny), domyślny zieleń jasny. Drabina L0 okno → L1 panel → L2 lista i pola. Zasłona okien modalnych w jasnych = `shadow.scrim`. Tagi formatów: PNG tag-1, JPG tag-4, AVIF tag-8, WEBP tag-3, GIF tag-5, TIF tag-6, JP2 i HEIC tag-7, inne tag-2. Lista plików w jasnych: białe wiersze z linią 1 px (S14). |
| Znane odstępstwa | Brak roli DS dla zaznaczonego wiersza (w ciemnych zaznaczenie = L4, hover = L3). Zasłona w motywach ciemnych wpisana na sztywno (`rgba(8, 18, 12, 0.62)`, `rgba(20, 16, 11, 0.62)`), bo DS nie ma takiej roli. Nieaktualne opisy: nagłówek `app.qss` („design system 1.5.0”), sekcja „Wygląd” w `BIN\README.md` (żółty przycisk główny z 2.6.1), `BIN\dev\design-system\MASTER.md` (paleta sprzed stylu DK). |
| Szkic w DS | `DS\themes\photo-resizer\dobra_kaloria.py` (37 kluczy, status „szkic – nie renderowany”) NIE jest mechanizmem, którego używa aplikacja. |
| Niesprawdzone | Ekran ze skalą 125 / 150 %, instalacja z instalatora (`PAMIEC\stan-prac-3009.md`); sześć starych ikon `check-*.png` – usunąć czy zostawić. |

Zmiana: `tokens.json` → `python scripts\build_tokens.py` → w repo Resizera `python scripts\sync_design_tokens.py` → nowy znacznik dopisz w `_tokens()` i w `app.qss` (każdy motyw musi definiować każdy znacznik) → testy → zrzuty czterech motywów → podbicie `pyproject.toml` i `WERSJA.txt` → budowa. Repo ma własną sesję i własne zasady.

### 5.3 DAM Dobra Kaloria

| Temat | Stan |
| --- | --- |
| Źródła | `OBSZAR\DAM---Dobra-Kaloria---inyfinn\bin\apps\web\`: `assets\js\dam-theme.js`, `assets\css\dam-tokens.css`, `dam-dk-components.css`, `dam-theme-dk.css`, `dam-fonts.css`, `scripts\build-dam-theme-dk.py` |
| Skąd tokeny | Nie ma automatu. Wartości DS są przepisane ręcznie do `dam-theme.js`: `DK_PACKS` (powierzchnie, tekst, drabina `l0..l4`, ramki `bs0..bs4`, tagi) oraz `DK_CTRL_BASE` / `DK_CTRL` (role kontrolek → zmienne `--dam-<rola>`). Zestaw DK włącza `html[data-dam-style="dk"]`. `dam-theme-dk.css` generuje własny skrypt DAM ze skanu arkuszy `dam-*.css` – nie czyta `tokens.json`. |
| Wersje | 2.5.8 (`version.json`, `released_at` 2026-10-06). Według notatek wersji: 2.5.5 = DS 2.0.5 „sklep” w zestawach jasnych, 2.5.7 = szlif według DS 2.0.6 (S18), 2.5.8 = logika. Pamięć mówi „2.5.7 w budowie” – nieaktualne; stan wydania na GitHub: niesprawdzony. |
| Co wdrożone | Dwa zestawy: `dobra-kaloria` (DK 1 · zieleń, domyślny) i `dobra-kaloria-krem` (DK 2 · krem), każdy jasny i ciemny, obok zestawów nie-DK. Jasne: wartości zgodne z `tokens.json` 2.0.7 (drabina, tekst, akcent, role kontrolek, 8 barw tagów). Tryb zwarty. Czcionki w paczce (`assets\vendor\fonts\`). Tagi według grupy: smak róż, typ i kategoria pomarańcz, opakowanie żółty, autor morski, opis limonka, podkategoria czerwień, język niebieski, marka zieleń. |
| Znane odstępstwa | Tagi w trybach ciemnych to jeszcze odcienie sprzed 2.0.7. W `dam-dk-components.css` zostało 16 wartości hex w deklaracjach (m.in. `#0B5F31` ×3, `#0F763E` ×2, `#7D5E44`) – nie sprawdzałem, w których selektorach działają. Dziennik zmian w `bin\design-system\DESIGN_SYSTEM.md` kończy się na DAM 2.5.2 / DS 1.3.1 (żółty przycisk główny, `#0F763E`). Bazowe `:root`: `--dam-brand-green` `#008244`, `--dam-primary` `#007936`, `--dam-primary-hover` `#00642E`. |
| Szkic w DS | `DS\themes\dam\dam-theme-dobra-kaloria.css` (18 zmiennych pod `html[data-theme="dobra-kaloria"]`, status „szkic – nie renderowany”) NIE jest mechanizmem, którego używa DAM. |
| Niesprawdzone | Przyklejony pasek filtrów w prawdziwym oknie; wariant „krem jasny” (krytyk widzi nadal sepię – rozstrzyga user). |

Zmiana: `tokens.json` → `python scripts\build_tokens.py` → przepisz zmienione wartości do `DK_PACKS` i `DK_CTRL*` w `dam-theme.js` (z `DS\tokens\tokens.md`) → gdy zmieniały się arkusze `dam-*.css`: `python bin\apps\web\scripts\build-dam-theme-dk.py` → podbij `?v=` każdego zmienionego pliku we wszystkich `apps\web\*.html` → zrzuty zestawów DK w obu trybach → `version.json`. Obowiązuje skill `dam-dobrakaloria`; repo jest dzielone z drugą sesją (logika, testy) – pliki wersji podbija ten, kto wydaje.

### 5.4 Prezentacje PPTX („nowy styl”)

Generator: `PREZ\scripts\build_dk.py`, motyw `"theme": "shop"` (styl C, domyślny). `write_theme()` wpisuje schemat kolorów i czcionek do motywu prezentacji, `paint()` ustawia kolor przez slot motywu (plus jasność).

| Slot PowerPointa | Token w kodzie | `THEMES["shop"]` | Odpowiednik w DS 2.0.7 | Zgodność |
| --- | --- | --- | --- | --- |
| Tekst 1 (dk1) | `ink` | `3B2A20` | `text` `#222222` | RÓŻNE (prymityw `brown-900`) |
| Tło 1 (lt1) | `white` | `FFFFFF` | `white` | zgodne |
| Tekst 2 (dk2) | `brand` | `0F763E` | `brand` `#007936` | RÓŻNE (prymityw `green-700`) |
| Tło 2 (lt2) | `paper` | `FFFFFF` | L0 `#FFFFFF` | zgodne |
| Akcent 1 | `brand` | `0F763E` | `brand` `#007936` | RÓŻNE |
| Akcent 2 | `accent` | `DA272D` | `danger` `#C0262C` | RÓŻNE (prymityw `red-600`; w PPTX to kropka i kolor produktu, nie błąd) |
| Akcent 3 | `card` | `FDF8EC` | L3 ecru `#FDF8EC` | ta sama wartość, inna rola (w PPTX karta) |
| Akcent 4 | `sage` | `E9F2EC` | `brand-soft` `#E9F2EC` | zgodne |
| Akcent 5 | `sage2` (`tan`) | `AD8767` | `accent-beige` `#AD8767` | ta sama wartość; w PPTX także tekst etykiet |
| Akcent 6 | `sun` | `FFD42A` | `cta` `#FFD821` | RÓŻNE (prymityw `yellow-400`) |
| Hiperłącze | `brand` | `0F763E` | – | – |
| Odwiedzone hiperłącze | `sage2` | `AD8767` | – | – |

| Token pochodny | Slot i jasność |
| --- | --- |
| `muted` | Akcent 5, −30% |
| `brand_soft` / `brand_hi` / `brand_lo` | Akcent 1, +55% / +18% / −25% |
| `line` | Akcent 3, −10% |
| `on_brand` | Tło 1, −12% |

- **Czcionki motywu:** nagłówki (`+mj-lt`) Mindset, tekst (`+mn-lt`) Lato; pogrubienie = Lato Bold.
- **Zasada:** kolory i czcionki tylko ze slotów motywu, żeby user mógł zmienić je globalnie (Projektowanie > Warianty). Wyjątek: kolory smaków są stałe (hex w specyfikacji), bo to kolory produktu.
- **Skąd wartości:** wpisane osobno w `build_dk.py`, bez związku z `tokens.json` (`DESIGN_SYSTEM.md` §5 i §9). Motyw `shop` odpowiada stanowi sprzed rundy 4.
- **Decyzje usera specyficzne dla prezentacji** (`PREZ\references\lekcje.md`): tekst „nie czarny, tylko miły ciemny ton” = `3B2A20`; etykiety i podpisy w beżu `AD8767` (A11); bez przycisków CTA (A16); ikony liniowe zielone (A13); tabele jak w sklepie (A14).

Zmiana: popraw wartości w `THEMES["shop"]` w `PREZ\scripts\build_dk.py` i tabelę w `PREZ\references\styl-dk.md` → zbuduj prezentację próbną i sprawdź `verify.ps1` → `WORK\build.ps1 -Bump` (odświeża kopię skilla w programie i w `skill-prezentacje\`) → `WORK\wydaj.ps1`.

---

## 6. Jak zmieniać design system

### 6.1 Procedura

| Krok | Co | Gdzie |
| --- | --- | --- |
| 1 | Zapisz słowa usera dosłownie, z datą, i ustal, czy dotyczą marki, czy jednego motywu. | `DS\ZALECENIA-USERA.md` |
| 2 | Zmień wartość. | `DS\tokens\tokens.json` |
| 3 | `python scripts\build_tokens.py` (generuje pliki; kod wyjścia 1 = za słaby kontrast), potem `--check`. | `DS\scripts\` |
| 4 | Podbij `meta.version`: poprawka wartości = trzecia cyfra, nowy token = druga, usunięcie albo zmiana nazwy tokenu = pierwsza (plus lista zamian dla aplikacji). Zapisz `tokens\READY-<wersja>.txt`. | `DS\tokens\` |
| 5 | Odśwież aplikacje, których zmiana dotyczy (5.1–5.4). | repozytoria aplikacji |
| 6 | Zrzuty „przed” i „po” w każdej z nich, otwarte i obejrzane. | katalog dowodów aplikacji |
| 7 | Odśwież kopie: `WORK\repo.ps1` (lustro w `~\repos\Prezentacje-Dobra-Kaloria\design-system`) oraz kopię w repo `cursor-global-config`. | – |

### 6.2 Czego nie wolno

| Zakaz | Dlaczego |
| --- | --- |
| Wartości na sztywno w aplikacji (hex, px poza tokenami) | Zmiana w `tokens.json` przestaje działać; każda aplikacja rozjeżdża się osobno. |
| Ręcznej edycji plików generowanych (`tokens.css`, `tokens_qt.py`, `tokens.md`, `themes\*`, `palettes.py`, `dam-theme-dk.css`) | Następna budowa je nadpisze. |
| Przepisywania komponentów cudzej aplikacji | Motyw to nakładka na jej zmienne; repo Resizera i DAM mają własne sesje i zasady. |
| Usuwania motywów jasny i ciemny ani dotychczasowych zestawów | Decyzja usera: styl DK dochodzi obok, nic nie znika. |
| Usuwania albo zmiany nazwy tokenu bez podbicia pierwszej cyfry wersji | Aplikacje w terenie czytają stare nazwy. |
| Uogólniania uwagi o jednym motywie na regułę marki | Lekcja z rundy 3 (1.4). |
| Przebarwiania logo | Logo jest plikiem. |
| Ponownego uruchamiania `scripts\migrate_2_0_0.py` | Migracja jednorazowa, już wykonana. |
| Prymitywów w komponentach (`--dk-green-750`) | Używa się ról; prymityw tylko w definicji roli albo motywu. |

### 6.3 Checklista przed oddaniem zmiany UI

| Nr | Sprawdzenie |
| --- | --- |
| 1 | Zrzut ekranu własnego okna (nie całego ekranu) otwarty i obejrzany; bez zrzutu nie ma „gotowe”. |
| 2 | Zrzut porównany ze sklepem (`DS\assets\sklep-2026-10-06\`), wzorcem programu (`DS\assets\wzorzec-program-2026-10-06\`) i `DS\preview\shots\71-sklep-*.png`. |
| 3 | Tło okna białe; każde tło ma poziom z drabiny (rodzic + 1); nie głębiej niż L4; kontener bez tła, jeśli wystarczy biel. |
| 4 | Kontrast tekstu co najmniej 4,5:1 na swoim poziomie; obrys pola i kontrolki co najmniej 3:1. |
| 5 | Fokus widoczny na każdym elemencie interaktywnym: 2 px `focus` z odstępem 2 px, w polu 1 px + poświata. |
| 6 | Cel kliknięcia co najmniej 44 px (w zwartym narzędziu co najmniej 32 px z powiększonym obszarem klikania). |
| 7 | Budżet obrysów (S13): obrys tylko na polu, checkboxie, jednym przycisku drugorzędnym, białej karcie na bieli, fokusie. |
| 8 | Jeden żółty przycisk na widok; wersaliki tylko na głównym i jednym drugorzędnym (S18). |
| 9 | Tytuł główny i aktywna zakładka ciemnozielone; tytuły kart `#222222`; Mindset wyłącznie wersalikami w nagłówkach. |
| 10 | Okno nie większe niż obszar roboczy ekranu i nic nie jest przycięte (G7). |
| 11 | Stan nie jest niesiony samym kolorem (znak, podkreślenie, pogrubienie). Ruch wyłącza się przy `prefers-reduced-motion`. |
| 12 | Żadnej wartości na sztywno; polska typografia bez zawieszek; wersja aplikacji podbita we wszystkich plikach wersji. |

---

## 7. Otwarte sprawy / do decyzji

### 7.1 Rozbieżności między źródłami

| Nr | Sprawa | Źródła | Co wygrywa dziś / co do decyzji |
| --- | --- | --- | --- |
| 1 | Motyw PPTX `shop` nie jest zgodny z DS 2.0: tekst `3B2A20` zamiast `#222222`, zieleń `0F763E` zamiast `#007936`, żółty `FFD42A` zamiast `#FFD821`, czerwień `DA272D` zamiast `#C0262C`. | `PREZ\scripts\build_dk.py` kontra `tokens.json` | Do decyzji usera: czy prezentacje przechodzą na wartości sklepu. Tekst `3B2A20` to jego wcześniejsza decyzja dla prezentacji, a S4 („brąz nie jest kolorem tekstu”) powstała dla narzędzi. |
| 2 | `styl-dk.md` podaje Tekst 1 motywu `shop` jako `1F1F1F`, kod ma `3B2A20`. | `PREZ\references\styl-dk.md` kontra `build_dk.py`, `lekcje.md` | Wygrywa kod; tabela w `styl-dk.md` do poprawienia. |
| 3 | Zieleń interfejsu: pamięć z 29.09 mówi `#0F763E`, `tokens.json` mówi `#007936`. | `PAMIEC\design-system-dobra-kaloria.md` kontra `tokens.json` | Wygrywa `tokens.json`. Ten sam wpis pamięci jest nieaktualny także co do: wersji 1.0.0, motywów „niewdrożonych”, Resizera 2.5.2, 37 znaczników (jest 111). |
| 4 | Kopia DS w repo `cursor-global-config` była w wersji 1.4.0; 07.10.2026 odświeżona do 2.0.8 razem z tym plikiem. | `~\.cursor\external\claude-skills\ds-dobra-kaloria\` | Wygrywa skill; kopię odświeża się przed wypchnięciem repo (`scripts\sync-external-mirrors.ps1`, kierunek Collect). |
| 5 | Opisy w skillu zatrzymały się na 2.0.0: tytuł `SKILL.md`; `DESIGN_SYSTEM.md` §1 („do przeniesienia na 2.0.0”), §5c (tagi w odcieniach zieleni), §9 („aplikacje na 1.6.0”), §11 (historia kończy się na 2.0.0); `IDENTYFIKACJA-WIZUALNA.md` §5 (tagi zielone, „stałe barwy zakazane”); `components.md` §22 (tag z obrysem), §18 (toast `#222222` 15,91:1; token: `#00642E`, 7,34:1), §7 (ostrzeżenie 6,57:1; token: 14,52:1). | pliki skilla kontra `tokens.json` i `READY-2.0.0.txt` | Wygrywają `tokens.json` i S13–S18; opisy do aktualizacji. |
| 6 | `tokens.json` oznacza motywy Resizera i DAM jako „szkic – nie renderowany”, a obie aplikacje mają styl DK wdrożony innym mechanizmem. README szkiców opisują wartości sprzed 2.0. | `themes.*.status`, `DS\themes\*\README.md` kontra repozytoria | Do decyzji: usunąć szkice z generatora czy uzgodnić je z mechanizmami aplikacji. Wynik `build_tokens.py --resizer` na dzisiejszym Resizerze: niesprawdzony (nie uruchamiałem). |
| 7 | Brak opisu wersji 2.0.3 i brak znaczników `READY-2.0.1` … `READY-2.0.7`, choć procedura każe zapisywać znacznik po każdej zmianie wartości. Wynik „556 sprawdzeń, 0 błędów” dotyczy 2.0.0. | `DESIGN_SYSTEM.md` §8 kontra `DS\tokens\` | Do uzupełnienia; wynik `--check` dla 2.0.7: niesprawdzony. |
| 8 | Przypisanie grup tagów do barw: `IDENTYFIKACJA-WIZUALNA.md` §5 (1 smak, 2 typ, 3 opakowanie, 4 autor, 5 opis, 6 podkategoria, 7 marka, 8 „z folderu”) kontra S17 i DAM (marka zieleń, opis limonka, opakowanie żółty, kategoria pomarańcz, podkategoria czerwień, smak róż, autor morski, język niebieski). | pliki skilla kontra `READY-2.0.0.txt`, `dam-theme.js` | Nowsze jest S17 (zgodne z DAM); jedna tabela do zapisania w DS. |
| 9 | Zaznaczenie pozycji listy i menu: pamięć „bez grubego paska na krawędzi”, przepis Qt w `IDENTYFIKACJA-WIZUALNA.md` §4 ma `border-left: 3px solid`. DS nie ma roli „zaznaczony wiersz”. | `PAMIEC\styl-dk-reguly-globalne.md` pkt 10 kontra `IDENTYFIKACJA-WIZUALNA.md`; komentarz w `themes\__init__.py` Resizera | Nowsza jest decyzja usera; przepis i rola do dopisania. |
| 10 | Fokus: `control.focus-width` 2 px, `qt.focus-border` 1 px, S15 „pole: 1 px + poświata”, a `DESIGN_SYSTEM.md` §10 i przepis Qt podają fokus pola 2 px. | `tokens.json` kontra opisy | Wygrywa `tokens.json` + S15; opisy do poprawienia. |
| 11 | Stan aplikacji w pamięci (program 1.1.5, DAM 2.5.7 w budowie) kontra pliki wersji (1.1.6, 2.5.8). | `PAMIEC\stan-prac-3009.md` kontra `wersja.txt`, `version.json` | Wygrywają pliki wersji. |
| 12 | Etykiety generatora nieaktualne: „cienie (podbarwione brązem)”, „biały na brązie (toast)”, komentarz „-4 (nakładka)” w `tokens.css`. | `DS\scripts\build_tokens.py` | Kosmetyka, wartości poprawne. |

### 7.2 Braki i decyzje

| Nr | Sprawa | Skąd |
| --- | --- | --- |
| 13 | Style ciemne nie mają dowodu ze sklepu: zapytać usera, czy sklep ma tryb ciemny, albo zostawić ciepłe ciemne jak są. | `DESIGN_SYSTEM.md` §9 |
| 14 | Brak przepisu komponentu dla okna dialogowego i menu bocznego (tylko zapisy cząstkowe). | `components.md` |
| 15 | Przyciemnienie pod dialogiem: rola tylko dla stylów jasnych (`shadow.scrim`); style ciemne bez roli (Resizer ma wartości na sztywno); program używa białej zasłony zamiast ciepłego brązu, który user pochwalił w DAM. | `tokens.json`, `themes\__init__.py`, `WORK\src\ui\style.css` |
| 16 | Tracking nie jest tokenem – wartości rozproszone po przepisach. | `tokens.json`, `components.md` |
| 17 | DAM: brak automatu przenoszącego tokeny; tagi trybów ciemnych sprzed 2.0.7; 16 wartości hex w `dam-dk-components.css`; dziennik zmian DS w repo DAM nieaktualny; wariant „krem jasny” do rozstrzygnięcia przez usera. | 5.3 |
| 18 | Resizer: sześć starych ikon `check-*.png`; nieaktualne `MASTER.md` i `BIN\README.md`. | 5.2 |
| 19 | Program: czy 1.1.6 jest wydane; dwie wartości `rgba` poza tokenami; biała zasłona dialogu. | 5.1 |
| 20 | Prezentacje: propozycja z DS – czytać kolory motywu z `tokens.json` przy budowie zamiast wpisywać je osobno. | `DESIGN_SYSTEM.md` §9 |
| 21 | Pamięć z regułami stylu leży tylko na komputerze służbowym, pod ścieżką projektu; na drugim komputerze jej nie ma. | `~\.claude\knowledge\50-maszyna.md` §4 |

### 7.3 Niesprawdzone

| Co | Gdzie szukałem |
| --- | --- |
| Stan wydań na GitHub (program 1.1.6, DAM 2.5.8, Resizer 2.6.6) | tylko pliki wersji i `build.log`; poleceń `git` i `gh` nie uruchamiałem |
| Wynik `build_tokens.py --check` i `--resizer` dla 2.0.7 | skryptów nie uruchamiałem |
| Ścieżki repozytoriów na komputerze domowym | `35-git.md` §5 podaje tylko DAM (`X:\…`); Resizera nie wymienia; `50-maszyna.md` opisuje wyłącznie komputer domowy |
| Wartości na żywej stronie `https://dobrakaloria.pl/` | nie otwierałem; opieram się na `DOWODY-SKLEP.md` i trzech obejrzanych zrzutach (`sklep-26.png`, `program-1.1.5-01-start.png`, `program-1.1.5-11-wynik.png`) |
| W których selektorach działa 16 wartości hex w `dam-dk-components.css` | policzone skryptem, nie czytane |
| Wygląd aplikacji na ekranie ze skalą 125 / 150 %, instalator Resizera, przyklejony pasek filtrów DAM | `PAMIEC\stan-prac-3009.md` – niesprawdzone nigdzie |
