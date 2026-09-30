# Design system Dobra Kaloria

Wersja 1.4.0, 30.09.2026. Źródło wyglądu: okno programu „Stwórz prezentację” i styl sklepu
dobrakaloria.pl opisany w skillu `prezentacje` (`references/styl-dk.md`).

**Nowy ekran albo nowa aplikacja w stylu Dobra Kaloria: zacznij od `IDENTYFIKACJA-WIZUALNA.md`** (jeden język wizualny,
krok po kroku). Ten plik opisuje zasady i tokeny; decyzje usera: `ZALECENIA-USERA.md`.

## 1. Do czego służy

Jedno miejsce, z którego biorą wygląd narzędzia marki:

| Gdzie | Technologia | Jak korzysta | Stan |
|---|---|---|---|
| Program „Stwórz prezentację” | HTML/CSS w oknie WebView2 | `tokens.css`, zmienne `--dk-*` | wdrożone |
| Prezentacje PPTX | python-pptx, sloty motywu | te same kolory i czcionki (`prezentacje/references/styl-dk.md`) | wdrożone, wartości wpisane osobno |
| Inyfinn Photo Resizer | PySide6, arkusz QSS | `themes/photo-resizer/` | szkic, niewdrożony |
| DAM Dobra Kaloria | HTML/CSS, zmienne `--dam-*` | `themes/dam/` | szkic, niewdrożony |

Wartości są w jednym pliku: `tokens/tokens.json`. Wszystko inne (`tokens.css`, `tokens_qt.py`,
`tokens.md`, pliki w `themes/`) generuje `scripts/build_tokens.py`. Plików generowanych nie edytuje się ręcznie.

## 2. Zasady

1. **Ciepło zamiast czerni.** Tekst to ciemny brąz `#3B2A20`, nigdy `#000` ani `#222`. Cienie są
   podbarwione tym samym brązem. Tła: biel i krem.
2. **Każdy kolor ma jedną rolę.** Zieleń: marka, stan, zaznaczenie, linki, postęp. Żółty: główna akcja,
   jedna na ekran. Czerwony: tylko błąd. Bursztyn: ostrzeżenie. Beż `#AD8767`: etykiety nad sekcjami.
3. **Dużo światła.** Siatka 4 px. Karta ma 32 px marginesu wewnętrznego, sekcje dzieli 40 px,
   wiersze listy 20 px. Dla gęstych narzędzi jest wariant zwarty (sekcja 4).
4. **Dwie czcionki.** Mindset: nagłówki, wersaliki, krótkie hasła. Lato: cała reszta, najmniej 15 px.
   Mindset nie ma twardej spacji, więc łamanie nagłówków ustawia się ręcznie.
5. **Kształt.** Przycisk 4 px, pole i miniatura 8 px, karta 12 px, strefa upuszczania 16 px,
   przełącznik w pełni zaokrąglony. Ramki cienkie, piaskowe.
6. **Ikony liniowe.** Kreska 1,6, kolor dziedziczony z tekstu (`currentColor`), jedna rodzina (Lucide).
7. **Dostępność jest sprawdzana, nie zakładana.** Kontrast par tekst/tło liczy generator
   (`--check`, wynik w `tokens/tokens.md`). Obrys fokusu 3 px w zieleni. Cel kliknięcia najmniej 44 px.
   Ruch wyłącza się przy `prefers-reduced-motion`.
8. **Typografia polska.** Na końcu wiersza nie zostają „a, i, o, u, w, z” ani pojedyncze słowa.
   Zasady i kod: skill `prezentacje`, sekcja „Typografia PL”.

## 3. Tokeny

Pełne tabele z wartościami i kontrastem: `tokens/tokens.md` (generowane).

W komponentach używa się **ról**, nie prymitywów: `--dk-color-text`, nie `--dk-brown-900`.
Prymityw wolno wskazać tylko w definicji roli albo motywu.

| Grupa | Przedrostek | Przykład |
|---|---|---|
| kolory, role | `--dk-color-*` | `--dk-color-brand`, `--dk-color-surface`, `--dk-color-cta` |
| czcionki | `--dk-font-*` | `--dk-font-display`, `--dk-font-text` |
| rozmiary tekstu | `--dk-fs-*` | `--dk-fs-base` (16 px), `--dk-fs-display-md` (46 px) |
| odstępy | `--dk-space-*` | `--dk-space-8` = 32 px (numer × 4 px) |
| układ | `--dk-layout-*` | `--dk-layout-card-pad`, `--dk-layout-section-gap` |
| promienie | `--dk-radius-*` | `--dk-radius-md` (12 px) |
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

## 5a. Dwa style kolorystyczne x tryb jasny i ciemny (od 1.3.0)

Decyzja usera 30.09.2026: tryb wyświetlania (jasny / ciemny) i styl kolorystyczny to dwa osobne ustawienia.
Dobra Kaloria ma dwa style, każdy w obu trybach. W aplikacjach z wieloma stylami (DAM) to dwie nowe pozycje
na liście stylów, obok dotychczasowych. Styl to nie tylko kolory: we wszystkich wariantach obowiązują nagłówki
Mindset, przyciski, karty i pola jak w `components.md`. Mindset: firma ma licencję na użytek komercyjny.

| Styl | Tryb | id (`data-theme`) | Tło L0 | Karta L1 | Rubryka L2 | Tekst | Akcent | Qt |
|---|---|---|---|---|---|---|---|---|
| Program „Stwórz prezentację” | jasny | `:root`, `dobra-kaloria` | `#FFFFFF` | `#FDF8ED` | `#F8F1E0` | `#3B2A20` | `#0F763E` | `T` |
| Dobra Kaloria 1 · zieleń | jasny | `dobra-kaloria-zielen-jasny` | `#F8FBF9` | `#EFF5F1` | `#E6F0E8` | `#17291D` | `#0F763E` | `T_ZIELEN_JASNY` |
| Dobra Kaloria 1 · zieleń | ciemny | `dobra-kaloria-zielen-ciemny` | `#0F1F15` | `#14281C` | `#1A3123` | `#F5F1E8` | `#6FC792` | `T_DARK` |
| Dobra Kaloria 2 · krem | jasny | `dobra-kaloria-krem-jasny` | `#FEFCF6` | `#FCF5E3` | `#F5EEDD` | `#3B2A20` | `#0F763E` | `T_KREM_JASNY` |
| Dobra Kaloria 2 · krem | ciemny | `dobra-kaloria-krem-ciemny` | `#1C1812` | `#252019` | `#2E2820` | `#F5F1E8` | `#4CC46A` | `T_KREM` |

Od 1.4.0 krem jasny ma własny zestaw ról (`semantic-krem-jasny`, bez czystej bieli); do 1.3.x był równy programowi.
Program zostaje z białą kartką (L0 `#FFFFFF`) - to jedyny wariant, w którym biel jest dozwolona.

Główny przycisk we wszystkich wariantach: żółty `#FFD42A` z tekstem `#3B2A20`. Na ciemnym tle ciemna zieleń marki
ginie, dlatego akcent jest jaśniejszy, a tekst na nim ciemny. Źródło: `color.semantic*` i `themes-list` w
`tokens.json`; Qt: słowniki `T`, `T_KREM_JASNY`, `T_ZIELEN_JASNY`, `T_DARK`, `T_KREM` (i `VARIANTS[nazwa]`).
Kontrola: `build_tokens.py --check` (288 sprawdzeń: role, drabina, skoki jasności, tagi).

## 5b. Drabina powierzchni L0-L4 (od 1.4.0)

Decyzja usera 30.09.2026 (`ZALECENIA-USERA.md`): każda aplikacja liczy „zakorzenienia” okna (ile razy kontener leży
w kontenerze) i każde tło bierze z drabiny, a nie „na oko”.

| Poziom | Rola | Zmienna | Qt |
|---|---|---|---|
| L0 | tło okna | `--dk-color-surface-0` (= `bg`) | `color_surface_0` |
| L1 | kontener, sekcja, karta | `--dk-color-surface-1` (= `surface`) | `color_surface_1` |
| L2 | rubryka, pole, karta w karcie | `--dk-color-surface-2` (= `surface-hover`) | `color_surface_2` |
| L3 | element w polu: chip, wiersz listy, okno w oknie | `--dk-color-surface-3` | `color_surface_3` |
| L4 | nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `color_surface_4` |

Do każdego poziomu: `--dk-color-border-subtle-N` (ramka elementu na tym poziomie) i `--dk-color-on-surface-N` (tekst).

**Wzór.** Jasność OKLCH: `L_n = L0 + n · dL · kierunek`. Tryb jasny: kierunek w dół (głębiej = ciemniej), `dL = 0,020`.
Tryb ciemny: kierunek w górę (głębiej = jaśniej), `dL = 0,034` (w ciemnym oko potrzebuje większego skoku). Odcień stały
dla wariantu (krem 88°, zieleń 153-156°, ciemny krem 77,5°). Nasycenie: jasny `C = min(k·(1-L), max)`, ciemny `C = min(k·L, max)`.
Ramka poziomu: `L_n ± border_dL` (jasny 0,05, ciemny 0,09). Parametry: `tokens.json` → `ladder.variants`.

Dlaczego tak:
- jasne tło zostaje jasne (L0 0,985-1,000; szkic DAM miał szałwię `#EEF4EF` = 0,961, za ciemno), a karty i rubryki
  schodzą w dół małymi krokami - dlatego nie ma białych płyt na kremie,
- rubryka L2 jest ciemniejsza (w jasnym) albo mniej rozjaśniona (w ciemnym) niż pola w Photo Resizer 2.6.2:
  zieleń ciemna `#1D3526` (L 30,4) → `#1A3123` (L 28,9), krem ciemny `#302A21` (28,9) → `#2E2820` (28,1),
  krem jasny `#FBF3E0` (96,5) → `#F5EEDD` (95,0), zieleń jasna `#FFFFFF` (100) → `#E6F0E8` (94,5),
- pięć poziomów mieści DAM (głębokość 4-5): L4 dalej różni się od L0 o 0,08 (jasny) i 0,136 (ciemny).

Reguły kontrastu (sprawdza `--check`): `text` i `text-muted` >= 4,5:1 na każdym poziomie; link `brand` na L0-L3,
na L4 link w `brand-hover`; beżowa etykieta `label` tylko na L0-L1 (na L2+ etykieta w `text-muted`); sąsiednie poziomy
różnią się o 0,015-0,045 L; L4-L0 >= 0,06; brak `#FFFFFF` na żadnym poziomie stylów DK. Pełne tabele (hex, L, L*, dL,
kontrast): `tokens/tokens.md`. Zrzuty: `preview/shots/50-drabina-*.png`.

## 5c. Tagi (od 1.4.0)

Tag = odcień stylu z małym przesunięciem barwy, nie stała barwa. `hue_k = tag_hue + [0, +8, -8, +16, -16, +24, -24, +32]`
(OKLCH; `tag_hue` krem i program 90°, zieleń 146°). Tło, ramka i tekst mają jasność i nasycenie trybu (jasny: tło L 0,930,
ciemny: 0,360); tekst generator dociąga o 0,01 L aż do kontrastu >= 4,6:1. Zmienne `--dk-color-tag-1..8-bg / -fg / -border`,
Qt `color_tag_N_bg`. Przepis komponentu: `components.md`, rozdz. 22. Zrzut: `preview/shots/51-tagi.png`.

## 6. Motyw w istniejącej aplikacji

Zasada: motyw to **nakładka**, nie przebudowa. Aplikacja zostaje taka, jaka jest, a jej własne zmienne
dostają nowe wartości pod osobną nazwą motywu. Dotychczasowe motywy działają dalej.

| Aplikacja | Pliki | Instrukcja |
|---|---|---|
| Inyfinn Photo Resizer | `themes/photo-resizer/dobra_kaloria.py` | `themes/photo-resizer/README.md` |
| DAM | `themes/dam/dam-theme-dobra-kaloria.css` | `themes/dam/README.md` |

Oba motywy to szkice. Kontrast jest policzony, ale żaden nie był wyświetlony w swojej aplikacji.

## 7. Komponenty

Opis wariantów, stanów i dostępności: `components.md`. Żywa galeria: `preview/index.html`
(zrzuty w `preview/shots/`). Galeria używa wyłącznie zmiennych `--dk-*`.

## 8. Zmiana i wersja

1. Zmień wartość w `tokens/tokens.json`.
2. `python scripts/build_tokens.py` (generuje pliki i liczy kontrast; kod wyjścia 1 = za słaby kontrast).
3. Podbij `meta.version`: poprawka wartości = trzecia cyfra, nowy token = druga, usunięcie albo zmiana
   nazwy tokenu = pierwsza (i lista zamian dla aplikacji).
4. Odśwież aplikacje:
   - program „Stwórz prezentację”: `WORK\build.ps1` sam kopiuje `tokens.css` do `src\ui`,
   - Photo Resizer i DAM: skopiuj wygenerowany plik motywu do repo aplikacji.
5. Zrzuty ekranu „przed” i „po” w każdej aplikacji, której zmiana dotyczy.

## 9. Otwarte decyzje

| Temat | Stan | Propozycja |
|---|---|---|
| Trzy zielenie | interfejs `#0F763E`, DAM `#007936` (przycisk sklepu) i `#008244` (logo SVG), logo PNG w programie `#006400` | ustalić jedną zieleń interfejsu; logo zostaje plikiem i nie jest przebarwiane |
| Prezentacje poza generatorem | kolory wpisane w `build_dk.py` | czytać je z `tokens.json` przy budowie |
| Kierunek drabiny w jasnym | 1.4.0: głębiej = ciemniej (menu L4 najciemniejsze, z cieniem) | wrócić, jeśli w DAM menu na L4 będzie wyglądać „zapadnięte” - wtedy menu na L1 + cień |
| Wartości jeszcze wpisane na sztywno w programie | kilka kolorów pomocniczych w `style.css` (np. ramka kropki suwaka, tekst w polu uwag) | przenieść do tokenów przy następnej zmianie tych elementów |
