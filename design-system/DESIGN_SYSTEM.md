# Design system Dobra Kaloria

Wersja 1.2.0, 30.09.2026. Źródło wyglądu: okno programu „Stwórz prezentację” i styl sklepu
dobrakaloria.pl opisany w skillu `prezentacje` (`references/styl-dk.md`).

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

## 5a. Trzy motywy: jasny, ciemna zieleń, ciemny krem (od 1.2.0)

Decyzja usera 30.09.2026: aplikacje marki mają trzy motywy do przełączania: **Dobra Kaloria jasny**, **Dobra Kaloria
ciemna zieleń** i **Dobra Kaloria ciemny krem**. Motyw to nie tylko kolory: we wszystkich trzech obowiązuje ten sam
styl (nagłówki Mindset, przyciski, karty i pola jak w `components.md`). Stare motywy aplikacji (np. indygo w Photo Resizerze) są zastąpione, zapisany wybór „ciemny” przechodzi
na DK ciemny, każdy inny na DK jasny.

Role są te same we wszystkich motywach, zmieniają się wartości: ciemna zieleń `color.semantic-dark`
(`[data-theme="dobra-kaloria-ciemny"]`, Qt `T_DARK`), ciemny krem `color.semantic-krem`
(`[data-theme="dobra-kaloria-krem"]`, Qt `T_KREM`). Lista motywów: `themes-list` w `tokens.json`.

| Rola | Jasny | Ciemna zieleń | Ciemny krem |
|---|---|---|---|
| tło okna | `#FFFFFF` | `#0F1F15` | `#1C1812` |
| karta | `#FDF8EC` | `#162B1E` | `#26211A` |
| tekst | `#3B2A20` | `#F5F1E8` | `#F5F1E8` |
| tekst pomocniczy | `#7D5E44` | `#C9BEA6` | `#CBBFA8` |
| akcent (linki, suwaki, zaznaczenie) | `#0F763E` | `#6FC792` | `#4CC46A` |
| główny przycisk | `#FFD42A` z tekstem `#3B2A20` | bez zmian | bez zmian |

Na ciemnym tle ciemna zieleń marki `#0F763E` ginie, dlatego akcent jest jaśniejszy, a tekst na nim ciemny.

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
| Wartości jeszcze wpisane na sztywno w programie | kilka kolorów pomocniczych w `style.css` (np. ramka kropki suwaka, tekst w polu uwag) | przenieść do tokenów przy następnej zmianie tych elementów |
