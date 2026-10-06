# Design system Dobra Kaloria

Wersja 2.0.0 „sklep”, 06.10.2026 (runda 4: wygląd odtworzony ze zrzutów sklepu dobrakaloria.pl - biel, szary panel, biała karta, ecru
dopiero jako kolejny poziom kafla; tekst `#222222`; zieleń marki wraca jako akcent; rozdz. 5f). Źródło wyglądu: 7 zrzutów sklepu
od usera (`assets/sklep-2026-10-06/`, pomiary: `DOWODY-SKLEP.md`), kontrakt: `tokens/READY-2.0.0.txt`. Wcześniej źródłem było okno
programu „Stwórz prezentację” i styl opisany w skillu `prezentacje` (`references/styl-dk.md`); kolory z tamtych wersji są uchylone.

**Nowy ekran albo nowa aplikacja w stylu Dobra Kaloria: zacznij od `IDENTYFIKACJA-WIZUALNA.md`** (jeden język wizualny,
krok po kroku). Ten plik opisuje zasady i tokeny; decyzje usera: `ZALECENIA-USERA.md`.

## 1. Do czego służy

Jedno miejsce, z którego biorą wygląd narzędzia marki:

| Gdzie | Technologia | Jak korzysta | Stan |
|---|---|---|---|
| Program „Stwórz prezentację” | HTML/CSS w oknie WebView2 | `tokens.css`, zmienne `--dk-*` | wdrożone (do przeniesienia na 2.0.0) |
| Prezentacje PPTX | python-pptx, sloty motywu | te same kolory i czcionki (`prezentacje/references/styl-dk.md`) | wdrożone, wartości wpisane osobno |
| Inyfinn Photo Resizer | PySide6, arkusz QSS | `themes/photo-resizer/`, `tokens_qt.py` | wdrożone (do przeniesienia na 2.0.0) |
| DAM Dobra Kaloria | HTML/CSS, zmienne `--dam-*` | `themes/dam/` | wdrożone (do przeniesienia na 2.0.0) |

Wartości są w jednym pliku: `tokens/tokens.json`. Wszystko inne (`tokens.css`, `tokens_qt.py`,
`tokens.md`, pliki w `themes/`) generuje `scripts/build_tokens.py`. Plików generowanych nie edytuje się ręcznie.

## 2. Zasady

1. **Biel i neutralna czerń.** Tło okna jest BIAŁE (L0 `#FFFFFF`), bieli jest najwięcej. Tekst i tytuły prawie czarne
   `#222222`, pomocniczy `#666666`; brąz nie jest kolorem tekstu w stylach jasnych. Cienie neutralne `rgba(34,34,34,…)`
   i tylko dla nakładek, toastów i uchwytów. Style ciemne mają własną, ciepłą paletę (bez zmian).
2. **Każdy kolor ma jedną rolę.** **Zieleń marki `brand` `#007936` jest akcentem interfejsu**: przycisk główny, ikony liniowe,
   kropki list, metki, aktywna zakładka, fokus, znak checkboxa, suwak, przełącznik. Ciemnozielony `heading-accent` `#00642E`:
   tytuł główny widoku, nadtytuł sekcji, aktywna zakładka, podpis ikony (nie tytuły kart i nazw: te `#222222`).
   Żółty `cta`: jedna wyróżniona akcja widoku, tekst `#222222`. Czerwony: tylko błąd. Bursztyn: ostrzeżenie.
   Etykiety: `label` `#333333`. Link w treści: `#222222`, pogrubiony, podkreślony; link nawigacji bez podkreślenia, aktywny zielony.
3. **Dużo światła.** Siatka 4 px. Karta ma 32 px marginesu wewnętrznego, sekcje dzieli 40 px,
   wiersze listy 20 px. Dla gęstych narzędzi jest wariant zwarty (sekcja 4).
4. **Dwie czcionki.** Mindset: nagłówki, wersaliki, krótkie hasła. Lato: cała reszta, najmniej 15 px.
   Mindset nie ma twardej spacji, więc łamanie nagłówków ustawia się ręcznie.
5. **Kształt.** Przycisk, pole, metka pełna 4 px; panel, karta, kafel 8 px; okno nakładki 12 px; wyszukiwarka i tagi pigułki;
   przełącznik w pełni zaokrąglony. Panel i karta bez obrysu i bez cienia (karta wprost na bieli: linia 1 px `border`).
   Kółko tylko: awatar, kropka, gałka, radio.
6. **Ikony liniowe.** Kreska 2, kolor `icon` (zieleń marki), jedna rodzina (Lucide). Przycisk-ikona kwadratowy 44 px.
7. **Dostępność jest sprawdzana, nie zakładana.** Kontrast par tekst/tło liczy generator
   (`--check`, wynik w `tokens/tokens.md`). Obrys fokusu 2 px w roli `focus` (jasne `#007936`; DK2 ciemny `#E6D3A0`,
   DK1 ciemny żółty), odstęp 2 px. Cel kliknięcia najmniej 44 px.
   Ruch wyłącza się przy `prefers-reduced-motion`.
8. **Typografia polska.** Na końcu wiersza nie zostają „a, i, o, u, w, z” ani pojedyncze słowa.
   Zasady i kod: skill `prezentacje`, sekcja „Typografia PL”.

## 3. Tokeny

Pełne tabele z wartościami i kontrastem: `tokens/tokens.md` (generowane).

W komponentach używa się **ról**, nie prymitywów: `--dk-color-text`, nie `--dk-ink-900`.
Prymityw wolno wskazać tylko w definicji roli albo motywu.

| Grupa | Przedrostek | Przykład |
|---|---|---|
| kolory, role | `--dk-color-*` | `--dk-color-brand`, `--dk-color-surface`, `--dk-color-cta` |
| czcionki | `--dk-font-*` | `--dk-font-display`, `--dk-font-text` |
| rozmiary tekstu | `--dk-fs-*` | `--dk-fs-base` (16 px), `--dk-fs-display-md` (46 px) |
| odstępy | `--dk-space-*` | `--dk-space-8` = 32 px (numer × 4 px) |
| układ | `--dk-layout-*` | `--dk-layout-card-pad`, `--dk-layout-section-gap` |
| promienie | `--dk-radius-*` | `--dk-radius-md` (8 px), `--dk-radius-btn` (4 px) |
| cienie | `--dk-shadow-*` | `--dk-shadow-thumb`, `--dk-shadow-toast` |
| ruch | `--dk-motion-*` | `--dk-motion-base` (.18 s) |
| kontrolki | `--dk-control-*` | `--dk-control-h` (48 px), `--dk-control-h-min` (44 px) |

## 4. Odstępy: dwa tryby

| Token | Wygodny (kreator, ekran z jedną czynnością) | Zwarty (narzędzie, listy, tabele) |
|---|---|---|
| margines wewnętrzny karty | `card-pad` 32 px, duża karta `card-pad-lg` 40 px | `card-pad-sm` 20 px |
| odstęp między sekcjami | `section-gap` 40 px | `section-gap-sm` 24 px |
| odstęp między wierszami | `stack` 20 px | `stack-sm` 12 px |

Program „Stwórz prezentację” używa trybu wygodnego. Photo Resizer i DAM to narzędzia gęste:
dla nich tryb zwarty. Trybów nie miesza się na jednym ekranie.

Reguła przy linii dzielącej sekcje: odstęp liczy się z obu stron linii (40 px nad i 40 px pod).

## 5. Platformy

**Web.** Wczytaj `tokens.css` przed własnym arkuszem. Czcionki deklaruje aplikacja (`@font-face`),
bo ścieżka do plików zależy od niej. Pliki: `assets/fonts/`.

```html
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="style.css">
```

**Qt / QSS.** QSS nie zna zmiennych. Wartości wstawia się szablonem: `from tokens_qt import T`,
potem `SZABLON.format(**T)`. Czcionki: `QFontDatabase.addApplicationFont` dla plików z `FONT_FILES`.

**PowerPoint.** Kolory i czcionki siedzą w slotach motywu prezentacji. Wartości w skillu `prezentacje`
są dziś wpisane osobno. Przy zmianie koloru w `tokens.json` trzeba je poprawić także tam
(`scripts/build_dk.py`, `THEMES["shop"]`).

## 5a. Style kolorystyczne x tryb jasny i ciemny (od 1.3.0, jasne przebudowane w 2.0.0)

Decyzja usera 30.09.2026: tryb wyświetlania (jasny / ciemny) i styl kolorystyczny to dwa osobne ustawienia.
Dobra Kaloria ma dwa style, każdy w obu trybach. W aplikacjach z wieloma stylami (DAM) to dwie nowe pozycje
na liście stylów, obok dotychczasowych. Styl to nie tylko kolory: we wszystkich wariantach obowiązują nagłówki
Mindset, przyciski, karty i pola jak w `components.md`. Mindset: firma ma licencję na użytek komercyjny.

| Styl | Tryb | id (`data-theme`) | Tło L0 | L1 | L2 | L3 | L4 | Tekst | Etykieta | Akcent | Qt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Program „Stwórz prezentację” = sklep | jasny | `:root`, `dobra-kaloria` | `#FFFFFF` | `#F8F7F5` | `#FFFFFF` | `#FDF8EC` | `#F5ECD8` | `#222222` | `#333333` | `#007936` | `T` |
| Dobra Kaloria 1 · zieleń (= sklep) | jasny | `dobra-kaloria-zielen-jasny` | `#FFFFFF` | `#F8F7F5` | `#FFFFFF` | `#FDF8EC` | `#F5ECD8` | `#222222` | `#333333` | `#007936` | `T_ZIELEN_JASNY` |
| Dobra Kaloria 1 · zieleń | ciemny | `dobra-kaloria-zielen-ciemny` | `#0F2315` | `#192C18` | `#24341C` | `#303C21` | `#3D4427` | `#FBF3E0` | `#ECCA76` | `#A2D686` | `T_DARK` |
| Dobra Kaloria 2 · krem (kafle ecru na bieli) | jasny | `dobra-kaloria-krem-jasny` | `#FFFFFF` | `#FDF8EC` | `#FFFFFF` | `#F5ECD8` | `#F0E6CF` | `#222222` | `#333333` | `#007936` | `T_KREM_JASNY` |
| Dobra Kaloria 2 · krem | ciemny | `dobra-kaloria-krem-ciemny` | `#120F0A` | `#1A1611` | `#231E17` | `#2C261E` | `#352E25` | `#F5F1E8` | `#D2B48F` | `#E6D3A0` | `T_KREM` |

**Od 2.0.0 (runda 4).** Trzy style jasne mają te same wartości ról (tekst, akcent, kontrolki, przyciski, tagi); różni je tylko
drabina: program i DK1 jasny = sklep (biel → szary panel → biała karta → ecru → beż), DK2 jasny = kafle ecru na bieli (jak strona
główna sklepu: biel → ecru → biała karta → beż → głębszy beż). „Zieleń” i „krem” w nazwach to dziś nazwy drabin, nie kolor tekstu.
**Style ciemne są bez zmian** (zrzuty sklepu nie pokazują trybu ciemnego): DK1 ciemny cieplejszy (`hue_step` -8° na poziom, tekst
kremowy, etykiety miodowe `#ECCA76`, akcent żółtawozielony `#A2D686`, fokus żółty `#FFD42A`, ramki mchowe), DK2 ciemny ciemniejszy
(L0 0,170, ramki `espresso-*`, tła tagów -0,05 L). Zyskały tylko nowe role (`heading`, `heading-accent`, `overlay`, `strip`,
`zebra`, `progress`).

Historia: 1.5.0 dała jasnym stylom białą kartkę programu z kremowymi kartami; 1.6.0 (runda 3) przebarwiła tekst i kontrolki na brąz i
wycofała zieleń z interfejsu; 2.0.0 uchyla oba kolory (kremowa karta jako L1, brązowy tekst, „zero zieleni”). Do 1.4.1 czerwień błędu
kremu jasnego zmieniona na `red-700` `#C0262C` (kontrast >= 4,5:1) i tak zostaje we wszystkich stylach jasnych.

Przycisk główny w stylach jasnych: zielony pełny (`brand` `#007936`, biały tekst Lato 700 wersalikami, hover `brand-hover` `#00642E`).
Żółty `#FFD821` z tekstem `#222222` to jedna wyróżniona akcja widoku („Wybierz folder” w programie zostaje żółty). W stylach ciemnych
główny przycisk zostaje żółty `#FFD42A` z ciemnym tekstem (zieleń marki ginie na ciemnym tle). Źródło: `color.semantic*` i `themes-list` w
`tokens.json`; Qt: słowniki `T`, `T_KREM_JASNY`, `T_ZIELEN_JASNY`, `T_DARK`, `T_KREM` (i `VARIANTS[nazwa]`).
Kontrola: `build_tokens.py --check` (556 sprawdzeń od 2.0.0: role, kontrolki, biały L0 i L2, neutralny tekst, zielony akcent, drabina, tagi).

## 5b. Drabina powierzchni L0-L4 (od 1.4.0; jasne jawne od 2.0.0)

Decyzja usera 30.09.2026 (`ZALECENIA-USERA.md`): każda aplikacja liczy „zakorzenienia” okna (ile razy kontener leży
w kontenerze) i każde tło bierze z drabiny, a nie „na oko”.

| Poziom | Rola (style jasne) | Zmienna | Qt |
|---|---|---|---|
| L0 | tło okna, zawsze BIAŁE | `--dk-color-surface-0` (= `bg`) | `color_surface_0` |
| L1 | panel, sekcja (jasnoszary ciepły; w DK2 jasny kafel ecru) | `--dk-color-surface-1` (= `surface`) | `color_surface_1` |
| L2 | karta lub pole w panelu, BIAŁE | `--dk-color-surface-2` | `color_surface_2` |
| L3 | kafel w karcie (ecru) | `--dk-color-surface-3` | `color_surface_3` |
| L4 | kafel w kaflu (głębszy beż) | `--dk-color-surface-4` | `color_surface_4` |

Do każdego poziomu: `--dk-color-border-subtle-N` (ramka elementu na tym poziomie) i `--dk-color-on-surface-N` (tekst).
**Nakładki** (menu, lista rozwijana, podpowiedź, modal) to rola `overlay` (biel) + `--dk-shadow-toast` + ramka `border`; **L4 nie jest już nakładką**
(w stylach ciemnych L4 nadal służy za nakładkę, bo tam głębiej = jaśniej).

Wartości jasne (jawne, ze zrzutów sklepu):

| Styl | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| sklep (program, DK1 jasny) | `#FFFFFF` | `#F8F7F5` | `#FFFFFF` | `#FDF8EC` | `#F5ECD8` |
| krem jasny | `#FFFFFF` | `#FDF8EC` | `#FFFFFF` | `#F5ECD8` | `#F0E6CF` |

**Uwaga: w stylach jasnych L2 jest JAŚNIEJSZY od L1** (biała karta na szarym panelu, jak w koszyku sklepu). Zdanie „głębiej = ciemniej” dotyczy
tylko par L2 → L3 → L4 (wtedy każdy kafel jest nieco ciemniejszym beżem). W stylach ciemnych bez zmian: wzór `L_n = L0 + n · dL`,
`dL = 0,034` OKLCH, głębiej = jaśniej; ramka poziomu `L_n ± border_dL` (ciemny 0,09). Parametry: `tokens.json` → `ladder.variants`
(jasne: `surfaces` i `borders` podane jawnie).

Reguły (sprawdza `--check`): `text` i `text-muted` >= 4,5:1 na każdym poziomie L0-L4; `brand` >= 4,5:1 na L0-L4 (zielony tekst, link,
ikona); `label` >= 4,5:1 na L0-L1; w stylach jasnych L0 i L2 = `#FFFFFF`, a sąsiednie poziomy różne (kontrast >= 1,03); w stylach ciemnych
skok sąsiadów 0,015-0,045 L, L4-L0 >= 0,06. Pełne tabele (hex, L, L*, dL, kontrast): `tokens/tokens.md`. Zrzuty: `preview/shots/50-drabina-*.png`
(1.4-1.6, jasne nieaktualne), `70-sklep-*.png`, `71-sklep-poziomy.png` (2.0.0).

## 5c. Tagi (od 1.4.0)

Tag = odcień stylu z małym przesunięciem barwy, nie stała barwa. `hue_k = tag_hue + offsets[k]` (OKLCH), `offsets` `[0, +8, -8, +16, -16, +24, -24, +32]`.
**Od 2.0.0 style jasne mają tagi w odcieniach zieleni** (`tag_hue` 152, odcienie 120°-184°; tag-1 `#D6F0DC` tło, `#28603A` tekst, `#B2D7BB` ramka),
bo zieleń znów jest kolorem marki. Ciemne: DK1 146°, DK2 krem ciemny 90° z ciepłymi `tag_offsets` `[0, +8, -8, -12, -16, -20, -24, -28]` (bez zmian).
Tło, ramka i tekst mają jasność i nasycenie trybu (jasny: tło L 0,930, ciemny: 0,360); tekst generator dociąga o 0,01 L aż do kontrastu >= 4,6:1.
Zmienne `--dk-color-tag-1..8-bg / -fg / -border`, Qt `color_tag_N_bg`. Przepis komponentu: `components.md`, rozdz. 22 i 25. Zrzut: `preview/shots/51-tagi.png`
(sprzed 2.0.0, jasne odcienie ciepłe nieaktualne).

## 5e. Runda 3: reguły G1-G9 i role kontrolek (1.6.0; kolory UCHYLONE przez 2.0.0)

Słowa usera dosłownie: `ZALECENIA-USERA.md` (06.10.2026, runda 3) i `RUNDA-3-2026-10-06.md`. **Od 2.0.0 część kolorystyczna tej rundy
(G2, G3, G4, G5, G6) jest UCHYLONA** przez rundę 4 (5f). Zostają reguły niekolorystyczne i G1 (jasne wnętrze):

| Reguła | Stan w 2.0.0 |
|---|---|
| G1 | ZOSTAJE. Checkbox i radio: wnętrze JASNE (`check-bg` `#FFFFFF`) także zaznaczone; obrys 1,5 px `check-border` `#868E96`, hover i zaznaczenie `check-border-hover` `#007936`, znak (ptaszek, kropka) `check-mark` `#007936`; wyłączony obrys `#CED4DA`, znak `#ADB5BD`. 20 px, promień 4 px (radio okrągłe). Nie ciemny kwadrat. |
| G2, G3 | UCHYLONE (kolor). Było: zero zieleni w tekście i drobnych elementach, zieleń tylko logo / splash / KPI / status. Jest: zieleń marki to akcent (5f). Plansza startowa zielona zostaje. |
| G3a | Link w treści: wg sklepu pogrubiony, `#222222`, podkreślony (S12). Link nawigacji: bez podkreślenia, aktywny / hover zielony. Zasada „bez podkreślenia w spoczynku” z 05.10 UCHYLONA dla treści. |
| G4, G5, G6 | UCHYLONE (kolor). Przycisk drugorzędny: biały, obrys 1 px `#222222`. Suwak: tor `#E9E9E9`, wypełnienie zielone, uchwyt biały z zielonym obrysem 2 px. Przełącznik włączony zielony, gałka biała. Krok aktywny zielony pełny z białym tekstem; pasek postępu `progress` `#47C33D`. |
| G7 | ZOSTAJE. Okno nie wyższe ani szersze niż dostępny obszar ekranu; cała treść widoczna (tryb zwarty albo przewijanie wewnątrz panelu). Dotyczy aplikacji, nie tokenów. |
| G8 | ZOSTAJE, kształty nowe: przycisk i pole 4, panel/karta/kafel 8, tagi pigułki; Mindset +10 w nazwach, Lato >= 14-15 px; kontrast tekstu >= 4,5:1. |
| G9 | ZOSTAJE. DK1 ciemny zielony; checkbox ma jasne (L3) wnętrze względem tła i znak w limonce. |

**Role dodane w 1.6.0 (29, wszystkie nadal istnieją; wartości jasne zmienione w 2.0.0, patrz `tokens/tokens.md`):**

| Grupa | Role |
|---|---|
| akcent | `accent`, `accent-hover`, `on-accent`, `accent-beige` (dekoracja) |
| ikona | `icon`, `icon-bg` |
| checkbox / radio | `check-bg`, `check-border`, `check-border-hover`, `check-mark`, `check-disabled-border`, `check-disabled-mark` |
| suwak | `slider-track`, `slider-fill`, `slider-thumb`, `slider-thumb-border` |
| przełącznik | `switch-off`, `switch-off-border`, `switch-on`, `switch-knob` |
| przycisk drugorzędny | `btn2-bg`, `btn2-text`, `btn2-border`, `btn2-hover-bg` |
| krokomierz | `step-active-bg`, `step-active-text`, `step-idle-border`, `step-idle-text`, `step-done` |

Tokeny `control`: `check-size` 20 px, `check-radius` 4 px, `check-border-width` 1,5 px, `btn2-border-width` 1 px, `slider-thumb-border-width` 2 px.

## 5f. Runda 4: sklep jest wzorcem (od 2.0.0, 06.10.2026)

Słowa usera dosłownie: `ZALECENIA-USERA.md` (06.10.2026, runda 4) i `RUNDA-4-SKLEP-2026-10-06.md`. Pomiary: `DOWODY-SKLEP.md`. Kontrakt: `tokens/READY-2.0.0.txt`.
Reguły S1-S12 obowiązują wszystkie style jasne (ciemne bez zmian):

| Reguła | Treść w skrócie |
|---|---|
| S1 | Tło okna BIAŁE; bieli jest najwięcej; beż, ecru i szary nigdy jako tło okna. |
| S2 | Sekcja = panel L1 (jasnoszary ciepły), bez obrysu i cienia; w panelu BIAŁE karty i pola (L2). Biała karta wprost na bieli: linia 1 px `border` albo panel. |
| S3 | Ecru i beż dopiero jako kolejny poziom kafla: L3 w białej karcie, L4 w kaflu ecru. Głębiej się nie schodzi. |
| S4 | Tekst i tytuły `#222222`, pomocniczy `#666666`. Brąz nie jest kolorem tekstu w stylach jasnych. |
| S5 | Tytuły Mindset wersalikami (+0.01em). Ciemnozielony `heading-accent` `#00642E`: tytuł główny widoku, nadtytuł sekcji, aktywna zakładka, podpis ikony. Prawie czarny `heading` `#222222`: tytuły kart i sekcji z treścią, nazwy, tytuły okien dialogowych. |
| S6 | Przycisk główny: zielony pełny, biały tekst Lato 700 wersalikami, promień 4, hover `brand-hover`. Drugorzędny: biały, obrys 1 px `#222222`, tekst `#222222` wersalikami, hover `#F6F2EF`. Żółty = jedna wyróżniona akcja, tekst `#222222`. |
| S7 | Ikony liniowe, kreska 2, zielone. Przycisk-ikona kwadratowy 44 px, tło `icon-bg` `#F5F5F5`, promień 4. Podpis pod ikoną: Lato 700, 11 px, wersaliki, `heading-accent`. |
| S8 | Checkbox i radio: wnętrze białe, obrys 1,5 px `#868E96`, zaznaczony zielony obrys i znak. Przełącznik włączony zielony. Suwak: tor `#E9E9E9`, wypełnienie zielone, uchwyt biały z zielonym obrysem. Postęp i aktywny krok: `progress` `#47C33D`. |
| S9 | Pole: białe, obrys 1 px `#868E96`, promień 4; fokus = obrys `brand` + `shadow-focus-field`. |
| S10 | Linie podziału 1 px `#DDDDDD`. Tabela w pasy `zebra` / biel, bez linii pionowych. Zakładki: pod spodem linia 1 px `#222222`. |
| S11 | Metka pełna (licznik, cena, znaczek) = `brand` + biały tekst, promień 4. Tagi kategorii = `tag-N` (odcienie zieleni), pigułki. |
| S12 | Linki w treści `#222222`, pogrubione, podkreślone; linki nawigacji bez podkreślenia, aktywny lub hover zielony. |

Zostaje z wcześniejszych rund: Mindset także w nazwach (+10), duży tekst (>= 14-15 px), jeden język kształtów, okno nigdy większe niż ekran
i nigdy przycięte, żadnych zbędnych linijek-podpowiedzi.

**Nowe role w 2.0.0** (są też w stylach ciemnych): `heading`, `heading-accent`, `overlay`, `strip` (pasek menu `#F8F4F1`), `zebra` (pasy tabeli, stopka `#F6F2EF`),
`progress` (`#47C33D`). Nazwy ról z wcześniejszych wersji nie zniknęły; zmieniły się ich wartości w stylach jasnych (m.in. `text`, `text-muted`, `label`,
`brand`, `accent`, `focus`, `icon`, `check-*`, `slider-*`, `switch-*`, `btn2-*`, `step-*`, `cta`, `on-cta`, `border`, `field-border`, cienie, tagi).

**Świadome odstępstwa od zrzutów** (`DOWODY-SKLEP.md`, „Świadome odstępstwa”): panele sklepu mają rogi proste, system daje 8 px (jeden język kształtów);
obrys checkboxa w sklepie `#ADB5BD` (2,1:1), system `#868E96` (3:1); jedna zieleń przycisków `#007936` zamiast rodziny odcieni sklepu; strzałki
karuzeli w sklepie są okrągłe, w systemie kwadratowe (kółko tylko: awatar, kropka, gałka, radio); style ciemne bez dowodu ze sklepu.

## 6. Motyw w istniejącej aplikacji

Zasada: motyw to **nakładka**, nie przebudowa. Aplikacja zostaje taka, jaka jest, a jej własne zmienne
dostają nowe wartości pod osobną nazwą motywu. Dotychczasowe motywy działają dalej.

| Aplikacja | Pliki | Instrukcja |
|---|---|---|
| Inyfinn Photo Resizer | `themes/photo-resizer/dobra_kaloria.py` | `themes/photo-resizer/README.md` |
| DAM | `themes/dam/dam-theme-dobra-kaloria.css` | `themes/dam/README.md` |

Pliki motywów generuje `build_tokens.py`; po 2.0.0 trzeba je przenieść do repozytoriów aplikacji (osobne sesje, osobne zasady).

## 7. Komponenty

Opis wariantów, stanów i dostępności: `components.md` (przepisy 2.0: rozdz. 25). Żywa galeria 2.0: `preview/sklep.html` (zrzuty `preview/shots/70-71-*.png`).
Galerie `preview/index.html` i `preview/kontrolki.html` są SPRZED 2.0.0 (kolory nieaktualne). Galeria używa wyłącznie zmiennych `--dk-*`.

## 8. Zmiana i wersja

1. Zmień wartość w `tokens/tokens.json`.
2. `python scripts/build_tokens.py` (generuje pliki i liczy kontrast; kod wyjścia 1 = za słaby kontrast).
3. Podbij `meta.version`: poprawka wartości = trzecia cyfra, nowy token = druga, usunięcie albo zmiana
   nazwy tokenu = pierwsza (i lista zamian dla aplikacji). Stare nazwy tokenów nie znikają w wersji bez zmiany majora: aplikacje w terenie je czytają
   (2.0.0 jest wydaniem głównym ze względu na zmianę WYGLĄDU, ale nie usunęło ani nie przemianowało żadnego tokenu; dodało 6 ról, zmieniło wartości jasnych stylów;
   kopia poprzednich wartości: `tokens/tokens-1.6.0.json`).
   Po zmianie wartości zapisz znacznik `tokens/READY-<wersja>.txt` (poprzednie zostają).
4. Odśwież aplikacje:
   - program „Stwórz prezentację”: `WORK\build.ps1` sam kopiuje `tokens.css` do `src\ui`,
   - Photo Resizer i DAM: skopiuj wygenerowany plik motywu do repo aplikacji.
5. Zrzuty ekranu „przed” i „po” w każdej aplikacji, której zmiana dotyczy.

## 9. Otwarte decyzje

| Temat | Stan | Propozycja |
|---|---|---|
| Zielenie | od 2.0.0 jedna zieleń interfejsu `brand` `#007936` (hover `#00642E`); logo SVG `#008244` i logo PNG w programie `#006400` to pliki | logo zostaje plikiem i nie jest przebarwiane; splash `#0F763E` zostaje (zatwierdzony wyjątek) |
| Prezentacje poza generatorem | kolory wpisane w `build_dk.py` | czytać je z `tokens.json` przy budowie |
| Style ciemne | bez dowodu ze sklepu (zrzuty tylko jasne) | zapytać usera, czy sklep ma tryb ciemny, albo zostawić ciepłe ciemne jak są |
| Przeniesienie 2.0.0 do trzech programów | tokeny gotowe, aplikacje na 1.6.0 | osobne sesje każdej aplikacji (sekcja 8, pkt 4) |
| Wartości jeszcze wpisane na sztywno w programie | kilka kolorów pomocniczych w `style.css` | przenieść do tokenów przy przenoszeniu na 2.0.0 |


## 10. Skala tekstu i odstępy: program -> Qt (od 1.5.0, kształty 2.0.0)

Tokeny `qt.*` w `tokens.json` (CSS `--dk-qt-*`, Qt `T["qt_*"]`). Wartości web to pomiar programu (`getComputedStyle`, 05.10.2026);
Qt to te same proporcje zmniejszone o ok. 10 %, żeby okno mieściło się na ekranie 1366x768. Kolory, ramki i promienie wiersza „pole” i „karta”
uaktualnione do 2.0.0. Szczegóły i komponenty: `components.md` sekcja 23.

| Rola | Program (web) | Qt (`qt.*`) |
|---|---|---|
| tekst | 16 px / 1,5 Lato | `fs-body` 15 px |
| etykieta pola | 15 px bold | `fs-label` 14 px bold |
| podpowiedź / opis | 15 px `text-muted` | `fs-hint` 14 px |
| eyebrow (etykieta sekcji) | 15 px bold, wersaliki, 0,1 em | `fs-eyebrow` 14 px bold, wersaliki, 110 % |
| nagłówek karty (Mindset) | 40-44 px | `fs-title` 22 px; okno dialogu `fs-dialog-title` 26 px |
| przycisk | 17 px bold, 48 px | `fs-btn` 15 px, `control-h` 40 px |
| przycisk główny | 19-20 px bold, 56-58 px | `fs-btn-primary` 17 px, `control-h-primary` 48 px |
| pole | 16 px, 48 px, biała, ramka 1 px `#868E96`, promień 4 | 15 px, 40 px, `field-border` 1 px, fokus 2 px, `radius-field` 4 |
| panel / karta | panel L1 bez ramki i cienia, karta L2 biała, promień 8, wypełnienie 32 px | `pad-card` 20 px, `card-border` 1 px (tylko karta na bieli), `radius-card` 8 |
| odstęp między kartami | 40-48 px | `gap-cards` 16 px (w oknie Resizera 12) |
| odstęp w karcie | 20 px | `gap-stack` 12 px, w rzędzie `gap-row` 10 px |


## 11. Historia wersji

| Wersja | Data | Zmiana |
|---|---|---|
| 2.0.0 | 06.10.2026 | Runda 4 „sklep” (S1-S12): jasne style odtwarzają sklep dobrakaloria.pl ze zrzutów. Drabina jasnych jawna: biel, szary panel `#F8F7F5`, biała karta, ecru `#FDF8EC`, beż `#F5ECD8`; L2 jaśniejszy od L1, L4 nie jest nakładką (rola `overlay`). Tekst `#222222`, brąz wycofany z tekstu. Zieleń marki `#007936` wraca jako akcent (przycisk, ikony, metki, zakładka, fokus, kontrolki); `heading-accent` `#00642E`. Przycisk drugorzędny biały z obrysem `#222222`, żółty = jedna wyróżniona akcja. Promienie 4 / 4 / 8 (panel, karta, kafel). Cienie neutralne. Nowe role: `heading`, `heading-accent`, `overlay`, `strip`, `zebra`, `progress`. Tagi jasne w zieleniach. Kontrola 556 sprawdzeń (biały L0 i L2, neutralny tekst, zielony akcent). Style ciemne bez zmian. Kopia: `tokens/tokens-1.6.0.json`, kontrakt: `tokens/READY-2.0.0.txt`. Kolory z 1.4.0-1.6.0 uchylone. |
| 1.6.0 | 06.10.2026 | Runda 3 (G1-G9). 29 nowych ról kontrolek i akcentu (`accent`, `icon`, `check-*`, `slider-*`, `switch-*`, `btn2-*`, `step-*`), 5 prymitywów, 5 tokenów `control`. Zieleń marki tylko dla logo, kafli KPI, kropki statusu (UCHYLONE w 2.0.0). Kontrola 754 sprawdzenia. Przepisy: `components.md` rozdz. 24. |
| 1.5.0 | 05.10.2026 | Jasne style = drabina programu 1:1 (L0 biała kartka), DK1 ciemny cieplejszy (`hue_step`), DK2 ciemny ciemniejszy (`tag_dL`), tokeny `qt.*`. |
| 1.4.1 | brak daty w źródłach | Czerwień błędu kremu jasnego `red-700`; kontrola `danger` na tle i karcie. |
| 1.4.0 | 30.09.2026 | Drabina powierzchni L0-L4 (OKLCH), tagi generowane, kontrola `--check`. |
| 1.3.0 | 30.09.2026 | Dwa style kolorystyczne x tryb jasny / ciemny. |
