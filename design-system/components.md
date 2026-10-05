# Dobra Kaloria - komponenty

Biblioteka komponentów wyciągnięta z aplikacji "Stwórz prezentację". Żywy podgląd każdego komponentu w każdym stanie:
`preview/index.html` (serwuj folder skilla przez HTTP, np. `python -m http.server 8793`). Style komponentów: `preview/preview.css`
(nazwy klas jak w aplikacji), wartości wyłącznie ze zmiennych `--dk-*` z `tokens/tokens.css`.

## Spis treści

1. [Przyciski](#1-przyciski)
2. [Etykieta nad tytułem i nagłówek](#2-etykieta-nad-tytułem-i-nagłówek)
3. [Kroki (stepper)](#3-kroki-stepper)
4. [Strefa upuszczania](#4-strefa-upuszczania)
5. [Karta "znalazłem" i lista](#5-karta-znalazłem-i-lista)
6. [Kafelek smaku z miniaturą](#6-kafelek-smaku-z-miniaturą)
7. [Uwagi (ostrzeżenia)](#7-uwagi-ostrzeżenia)
8. [Karta stylu do wyboru](#8-karta-stylu-do-wyboru)
9. [Suwak 3-stopniowy](#9-suwak-3-stopniowy)
10. [Przełącznik](#10-przełącznik)
11. [Wiersz sekcji](#11-wiersz-sekcji)
12. [Pole tekstowe i textarea](#12-pole-tekstowe-i-textarea)
13. [Pasek akcji](#13-pasek-akcji)
14. [Liczba-bohater i pasek postępu](#14-liczba-bohater-i-pasek-postępu)
15. [Lista kontrolna](#15-lista-kontrolna)
16. [Znaczek kontroli](#16-znaczek-kontroli)
17. [Lista "do dopracowania"](#17-lista-do-dopracowania)
18. [Toast](#18-toast)
19. [Pasek miniatur](#19-pasek-miniatur)
20. [Dodatek: ikony i zasady wspólne](#20-dodatek-ikony-i-zasady-wspólne)
21. [Drabina powierzchni: tło, karta, rubryka, okno w oknie, nakładka (od 1.4.0)](#21-drabina-powierzchni-od-140)
22. [Tagi i chipy kategorii (od 1.4.0)](#22-tagi-i-chipy-kategorii-od-140)

Jak z tych klocków złożyć nowy ekran albo nową aplikację: `IDENTYFIKACJA-WIZUALNA.md`.

## Zasady wspólne (dotyczą każdego komponentu)

- **Odstępy (zasada użytkownika "więcej powietrza")**: karta ma wewnętrzny margines `--dk-layout-card-pad` (32 px) lub `--dk-layout-card-pad-lg` (40 px);
  wiersze w listach oddziela min. `--dk-space-5` (20 px); bloki i sekcje `--dk-layout-section-gap` (40 px); podpis od treści min. `--dk-space-3` (12 px).
  Stara aplikacja miała ciaśniej (26 px w kartach, 14 px między wierszami) - w bibliotece obowiązują nowe wartości.
  W wąskim oknie (do 860 px) karty schodzą do `--dk-layout-card-pad-sm`, odstęp między polami do `--dk-layout-stack-sm`.
- **Fokus**: każdy element interaktywny ma pierścień `--dk-control-focus-width` (3 px) w kolorze `--dk-color-focus`, odsunięty o `--dk-control-focus-offset` (3 px). Nigdy `outline: none` bez zamiennika.
- **Cel dotykowy**: min. `--dk-control-h-min` (44 px) w każdym wymiarze.
- **Kolory**: tylko role `--dk-color-*`, nigdy prymitywy (`--dk-green-700` itp.). Tekst jest brązowy (`--dk-color-text`), nigdy czarny.
- **Czcionki**: Mindset (`--dk-font-display`) tylko w nagłówkach i liczbach, zawsze `text-transform: uppercase` (font nie ma małych liter). Lato (`--dk-font-text`) do reszty.
- **Etykieta w kolorze tan** (`--dk-color-label`, kontrast ok. 3,26:1 na bieli): tylko pogrubiony tekst min. 15 px (etykieta nad tytułem) i elementy ozdobne. Nigdy tekst ciągły. Od 1.4.0: tylko na poziomach L0-L1; na L2 i głębiej etykieta w `--dk-color-text-muted`.
- **Powierzchnie (od 1.4.0)**: każde tło bierzesz z drabiny `--dk-color-surface-0..4` według głębokości zagnieżdżenia (rozdz. 21), nie „na oko”. `--dk-color-bg` = L0, `--dk-color-surface` = L1, `--dk-color-surface-hover` = L2 (aliasy, stare nazwy działają).
- **Ruch**: przejścia `--dk-motion-fast/base/slow` + `--dk-motion-ease`; przy `prefers-reduced-motion: reduce` animacje są wyłączone (spinner staje się statyczny).
- **Ikony**: Lucide-style, kreska `--dk-control-stroke-icon`, `currentColor`, `aria-hidden="true"` gdy dekoracyjne (lista w rozdz. 20).
- **Stany wymuszone** w galerii (`.is-hover`, `.is-focus`, `.is-active`) służą tylko do dokumentacji - w produkcji działają `:hover`, `:focus-visible`, `:active`.
- Bez pauz długich w tekście interfejsu (używaj zwykłego łącznika "-"), bez emoji.

---

## 1. Przyciski

**Opis i kiedy używać.** Jeden główny przycisk (żółty CTA, brązowy tekst, róg 4 px) na ekran - to akcja, którą użytkownik ma wykonać. Obok niego przycisk drugorzędny (zielona ramka) i link-przycisk (podkreślony, zielony) do akcji pobocznych.

**Warianty.** `.btn.btn-primary` (56 px, 20 px tekst), `.btn.btn-secondary` (48 px, 17 px), `.link-btn` (44 px, 16 px). Ikona 20-24 px przed tekstem, odstęp `--dk-space-3`.

**Stany.** Domyślny, hover (`.is-hover`), focus-visible (`.is-focus`), aktywny (`.is-active`, przesunięcie o 1 px w dół), wyłączony (`disabled` / `.is-disabled`: tło `--dk-color-disabled-bg`, tekst przygaszony, kursor `not-allowed`).

**Tokeny.**
- Kolory: `--dk-color-cta`, `--dk-color-cta-hover`, `--dk-color-on-cta`, `--dk-color-brand`, `--dk-color-brand-hover`, `--dk-color-brand-soft`, `--dk-color-bg`, `--dk-color-disabled-bg`, `--dk-color-text-muted`, `--dk-color-focus`
- Typografia: `--dk-font-text`, `--dk-fs-base`, `--dk-fs-md`, `--dk-fs-lg`, `--dk-lh-tight`
- Kształt i odstępy: `--dk-radius-btn`, `--dk-space-1`, `--dk-space-2`, `--dk-space-3`, `--dk-space-6`, `--dk-space-8`, `--dk-space-10`
- Kontrolki i ruch: `--dk-control-h`, `--dk-control-h-lg`, `--dk-control-h-min`, `--dk-control-focus-width`, `--dk-control-focus-offset`, `--dk-motion-fast`, `--dk-motion-ease`

**Dostępność.** Natywny `<button type="button">` (lub `type="submit"`); Enter i Spacja aktywują. Wyłączenie atrybutem `disabled`. Ikony `aria-hidden`. Wysokości 56 / 48 / 44 px spełniają cel dotykowy. Kontrast tekstu: on-cta na cta 9,56:1, brand na bg 5,70:1.

**Rób / Nie rób.**
- Rób: jeden `.btn-primary` na widok; czasownik w etykiecie ("Stwórz prezentację").
- Rób: link-btn dla akcji anulowania i powrotu.
- Nie rób: dwóch żółtych przycisków obok siebie; białego tekstu na żółtym; ostrych i zaokrąglonych przycisków w jednym widoku (zawsze 4 px).
- Nie rób: wyłączonego przycisku bez wyjaśnienia, dlaczego jest nieaktywny.

**Przykład HTML.**
```html
<button type="button" class="btn btn-primary"><svg class="ic" aria-hidden="true"><use href="#i-sparkles"/></svg>Stwórz prezentację</button>
<button type="button" class="btn btn-secondary">Wybierz folder</button>
<button type="button" class="link-btn">Zrób kolejną</button>
```

---

## 2. Etykieta nad tytułem i nagłówek

**Opis i kiedy używać.** Mała etykieta wielkimi literami nad nagłówkiem nazywa kontekst ("Znalazłem w folderze"), nagłówek Mindset mówi, co jest najważniejsze na ekranie. Etykieta bywa też nagłówkiem grupy pól ("Sekcje prezentacji").

**Warianty.** `.eyebrow` (+ `.eyebrow-opt` dla dopisku "- opcjonalnie"); nagłówki: `.display.h-md` (40 px), `.display.h-product` (46 px), `.display.h-done` (76 px, zielony). Rozmiar 168 px zarezerwowany dla liczby-bohatera (rozdz. 14).

**Stany.** Statyczne. Wariant koloru: etykieta bursztynowa wewnątrz Uwag (`.notes .eyebrow`).

**Tokeny.**
- Kolory: `--dk-color-label`, `--dk-color-text-muted`, `--dk-color-brand`
- Typografia: `--dk-font-display`, `--dk-font-text`, `--dk-fs-sm`, `--dk-fs-display-sm`, `--dk-fs-display-md`, `--dk-fs-display-lg`, `--dk-lh-display`, `--dk-lh-tight`
- Odstępy: `--dk-space-3` (etykieta od treści)

**Dostępność.** Nagłówek to prawdziwy `<h1>`/`<h2>` (jedna `h1` na ekran); etykieta może być `<p>` lub nagłówkiem niższego rzędu. Etykieta nie zastępuje `<label>` pojedynczego pola. Kontrast etykiety 3,26:1 jest dopuszczalny tylko dla pogrubionego tekstu min. 15 px.

**Rób / Nie rób.**
- Rób: krótka etykieta (1-3 słowa), wielkie litery ustawia CSS, nie wpisuj ich w treści.
- Rób: `overflow-wrap: anywhere` dla nagłówka z nazwą produktu.
- Nie rób: Mindset w małych rozmiarach (< 40 px) ani w tekście ciągłym; małych liter w Mindset (font ich nie ma).
- Nie rób: koloru etykiety dla tekstu niepogrubionego lub mniejszego niż 15 px.

**Przykład HTML.**
```html
<p class="eyebrow">Znalazłem w folderze</p>
<h1 class="display h-product">Baton białkowy kokos</h1>
```

---

## 3. Kroki (stepper)

**Opis i kiedy używać.** Pasek postępu procesu o stałej liczbie kroków (tu 4: Folder, Ustawienia, Tworzenie, Gotowe) w nagłówku aplikacji. Pokazuje, gdzie użytkownik jest, nie służy do nawigacji.

**Warianty.** Pełny (numer + podpis) i zwarty (`.is-compact`, automatycznie do 860 px): podpis tylko przy kroku bieżącym.

**Stany.** Krok zrobiony (`li.done`: jasnozielone koło z zielonym obrysem i znacznikiem), bieżący (`li[aria-current="step"]`: pełne zielone koło, tekst podstawowy), oczekujący (szare koło, tekst przygaszony). Łącznik przed krokiem bieżącym i po zrobionym jest zielony.

**Tokeny.**
- Kolory: `--dk-color-brand`, `--dk-color-brand-soft`, `--dk-color-on-brand`, `--dk-color-text`, `--dk-color-text-muted`, `--dk-color-border-strong`, `--dk-color-bg`
- Typografia: `--dk-font-text`, `--dk-fs-sm`, `--dk-lh-tight`
- Kształt i odstępy: `--dk-radius-pill`, `--dk-space-3`, `--dk-space-4`, `--dk-space-8` (koło 32 px, łącznik 32 px)

**Dostępność.** `<ol aria-label="Postęp: krok 2 z 4">`, bieżący krok `aria-current="step"`. Koła są `aria-hidden`; informacja jest w tekście podpisu, a stan zrobiony pokazuje też znacznik (nie tylko kolor). Element nieinteraktywny, więc brak wymogu celu dotykowego.

**Rób / Nie rób.**
- Rób: aktualizuj `aria-label` przy zmianie kroku; zrobione kroki oznacz znacznikiem.
- Rób: zwarty wariant w oknie węższym niż 860 px.
- Nie rób: więcej niż 5 kroków; klikalnych kroków bez pełnej obsługi klawiatury (to inny komponent).
- Nie rób: samego koloru jako nośnika stanu.

**Przykład HTML.**
```html
<ol class="steps" aria-label="Postęp: krok 2 z 4">
  <li class="done"><span class="n" aria-hidden="true"><svg class="ic"><use href="#i-check"/></svg></span><span class="lbl">Folder</span></li>
  <li aria-current="step"><span class="n" aria-hidden="true">2</span><span class="lbl">Ustawienia</span></li>
  <li><span class="n" aria-hidden="true">3</span><span class="lbl">Tworzenie</span></li>
</ol>
```

---

## 4. Strefa upuszczania

**Opis i kiedy używać.** Duży cel dla przeciągnięcia folderu lub plików na start procesu. Zawsze towarzyszy jej przycisk alternatywny (wybór z dysku), bo przeciąganie nie działa z klawiatury.

**Warianty.** Jedna strefa; zawartość: ikona w kole, tytuł Mindset, podtytuł, przycisk `.btn-secondary`.

**Stany.** Bezczynna (przerywana ramka w kolorze etykiety, tło `--dk-color-surface`), hover (tło `--dk-color-surface-hover`), nad strefą (`.is-over`: ciągła zielona ramka, jasnozielone tło, zielona ikona, tekst "Puść teraz"), z fokusem na przycisku wewnątrz.

**Tokeny.**
- Kolory: `--dk-color-surface`, `--dk-color-surface-hover`, `--dk-color-label`, `--dk-color-brand`, `--dk-color-brand-soft`, `--dk-color-on-brand`, `--dk-color-text-muted`
- Typografia: `--dk-font-display`, `--dk-fs-display-md`, `--dk-fs-lg`, `--dk-lh-display`
- Kształt i odstępy: `--dk-radius-lg`, `--dk-radius-pill`, `--dk-space-1`, `--dk-space-3`, `--dk-space-6`, `--dk-space-8`, `--dk-space-10`, `--dk-space-12`, `--dk-space-20`
- Ruch: `--dk-motion-base`, `--dk-motion-ease`

**Dostępność.** Strefa jest dekoracją dla myszy; klawiaturę obsługuje przycisk wewnątrz (natywny `<button>`). Zmianę stanu `.is-over` uzupełnij komunikatem w regionie `aria-live="polite"` po upuszczeniu ("Wczytuję folder..."). Przycisk ma 48 px wysokości.

**Rób / Nie rób.**
- Rób: `dragenter/dragover` dodają `.is-over`, `dragleave/drop` zdejmują; `preventDefault` na `dragover` i `drop`.
- Rób: podpowiedz, jakie pliki są oczekiwane (lista pod strefą).
- Nie rób: strefy bez przycisku alternatywnego; dziesiątek stref na jednym ekranie.
- Nie rób: kolor `--dk-color-label` jako koloru tekstu wewnątrz strefy (użyj `--dk-color-text-muted`).

**Przykład HTML.**
```html
<div class="drop">
  <span class="drop-ic" aria-hidden="true"><svg class="ic"><use href="#i-folder-open"/></svg></span>
  <h1 class="drop-title">Upuść tu folder z produktem</h1>
  <p class="drop-sub"><span class="when-idle">...albo dowolny plik z tego folderu</span><span class="when-over">Puść teraz - wczytam ten folder</span></p>
  <button type="button" class="btn btn-secondary">Wybierz folder</button>
</div>
```

---

## 5. Karta "znalazłem" i lista

**Opis i kiedy używać.** Podsumowanie wyniku analizy: co program znalazł w folderze. Karta na kremowej powierzchni z tytułem produktu i listą wierszy, każdy z ikoną stanu, nazwą i opcjonalną drugą linią.

**Warianty.** Wiersz: znaleziono (zielone koło ze znacznikiem), brak (`.f-none`: szare koło z minusem, tekst przygaszony), ostrzeżenie (`.f-warn`, propozycja: bursztynowe koło). Opcjonalnie `.f-sub` (druga linia) i `.f-hint` (ikona informacji + zdanie).

**Stany.** Statyczne; karta może zawierać `.flavs` (rozdz. 6) i `.notes` (rozdz. 7) jako osobne bloki.

**Tokeny.**
- Kolory: `--dk-color-surface`, `--dk-color-border`, `--dk-color-brand`, `--dk-color-brand-soft`, `--dk-color-disabled-bg`, `--dk-color-text-muted`, `--dk-color-warning-bg`, `--dk-color-warning-border`, `--dk-color-warning-text`
- Typografia: `--dk-fs-base`, `--dk-fs-sm`, `--dk-lh-base`, `--dk-lh-snug`
- Kształt i odstępy: `--dk-layout-card-pad`, `--dk-layout-card-pad-sm` (do 860 px), `--dk-radius-md`, `--dk-radius-pill`, `--dk-space-1`, `--dk-space-2`, `--dk-space-3`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`

**Dostępność.** `<ul>`; ikony `aria-hidden`. Stan musi wynikać z tekstu, nie tylko z ikony i koloru - dla braku zawsze dopisz "nie znaleziono" w `.f-sub`. Kontrast tekstu muted na kremowym tle powyżej 4,5:1.

**Rób / Nie rób.**
- Rób: pierwszą linią nazwa (pogrubiona), drugą szczegół (nazwa pliku, liczba).
- Rób: odstęp między wierszami min. `--dk-space-5`.
- Nie rób: zielonego koła dla ostrzeżenia (w aplikacji ikona ostrzeżenia dostaje dziś zielone koło - użyj `.f-warn`).
- Nie rób: cienia na karcie (obramowanie 1 px wystarcza).

**Przykład HTML.**
```html
<div class="found">
  <p class="eyebrow">Znalazłem w folderze</p>
  <h1 class="display h-product">Baton białkowy kokos</h1>
  <ul class="found-list">
    <li><span class="f-ic" aria-hidden="true"><svg class="ic"><use href="#i-check"/></svg></span>
      <div class="f-txt"><strong>Karty wprowadzenia</strong><span class="f-sub">3 pliki xlsx</span></div></li>
    <li class="f-none"><span class="f-ic" aria-hidden="true"><svg class="ic"><use href="#i-minus"/></svg></span>
      <div class="f-txt">Badania<span class="f-sub">nie znaleziono</span></div></li>
  </ul>
</div>
```

---

## 6. Kafelek smaku z miniaturą

**Opis i kiedy używać.** Kafelek jednego smaku: miniatura opakowania (packshot), nazwa, gramatura. Miniatura jest przyciskiem, gdy w folderze jest kilka zdjęć do wyboru (klik = następny plik).

**Warianty.** Do zamiany (miniatura-`<button>` z odznaką odświeżenia), tylko podgląd (`<span>`), brak zdjęcia (`.is-none`, przerywana ramka, tekst "brak packshotu"), jest bez obrazka (`.is-ok`, znacznik na jasnozielonym).

**Stany.** Miniatura-przycisk: domyślny, hover (`.is-hover`: zielona ramka + poświata), focus-visible (`.is-focus`). Kafelki układa się w siatce 2 kolumn (`.flavs`).

**Tokeny.**
- Kolory: `--dk-color-bg`, `--dk-color-border`, `--dk-color-border-strong`, `--dk-color-surface`, `--dk-color-brand`, `--dk-color-brand-soft`, `--dk-color-disabled-bg`, `--dk-color-text-muted`, `--dk-color-focus`
- Typografia: `--dk-fs-base`, `--dk-fs-sm`, `--dk-lh-tight`
- Kształt i cień: `--dk-radius-md`, `--dk-radius-sm`, `--dk-radius-pill`, `--dk-shadow-raised`, `--dk-shadow-focus-field`
- Odstępy i kontrolki: `--dk-space-1`, `--dk-space-3`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`, `--dk-space-14` (miniatura 56 px), `--dk-control-h-min`, `--dk-control-focus-width`, `--dk-control-focus-offset`
- Ruch: `--dk-motion-fast`, `--dk-motion-ease`

**Dostępność.** Miniatura-przycisk: `aria-label="Zamień zdjęcie opakowania dla smaku Kokos. Teraz: plik.png."`, obraz wewnątrz `alt=""`. Tekst "brak packshotu" jest widoczny (stan nie tylko kolorem). Miniatura 56 px spełnia cel dotykowy.

**Rób / Nie rób.**
- Rób: `object-fit: contain`, żeby opakowanie nie było przycinane.
- Rób: odznaka odświeżenia tylko gdy jest co zamieniać.
- Nie rób: miniatury-przycisku bez `aria-label`; kafelków w jednej kolumnie na szerokim ekranie.
- Nie rób: rozmiarów miniatury poza siatką 4 px.

**Przykład HTML.**
```html
<div class="flav">
  <button type="button" class="flav-media" aria-label="Zamień zdjęcie opakowania dla smaku Kokos">
    <img src="kokos.png" alt="">
    <span class="flav-swap" aria-hidden="true"><svg class="ic"><use href="#i-refresh"/></svg></span>
  </button>
  <div class="flav-txt"><span class="flav-name">Kokos</span><span class="flav-mass">45 g</span></div>
</div>
```

---

## 7. Uwagi (ostrzeżenia)

**Opis i kiedy używać.** Bursztynowe pudełko z listą rzeczy, na które użytkownik powinien zwrócić uwagę po analizie (braki, niezgodności). Nie blokuje pracy - informuje.

**Warianty.** Same ostrzeżenia (ikona trójkąta) oraz z pozycją informacyjną (`li.info`: zwykły kolor tekstu, szara ikona).

**Stany.** Statyczne. Pudełko można ukryć atrybutem `hidden`, gdy nie ma uwag.

**Tokeny.**
- Kolory: `--dk-color-warning-bg`, `--dk-color-warning-border`, `--dk-color-warning-text`, `--dk-color-text`, `--dk-color-text-muted`
- Typografia: `--dk-fs-sm`, `--dk-lh-base`
- Kształt i odstępy: `--dk-radius-md`, `--dk-space-1`, `--dk-space-3`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`

**Dostępność.** Nagłówek "Uwagi" nazywa grupę (użyj `aria-labelledby` na kontenerze). Ikona nie jest jedynym nośnikiem znaczenia - każdy punkt to pełne zdanie. Kontrast warning-text na warning-bg: 6,57:1.

**Rób / Nie rób.**
- Rób: jedno zdanie na punkt, konkret ("brakuje składu smaku Wanilia").
- Rób: odstęp między punktami min. `--dk-space-5`.
- Nie rób: czerwieni dla uwag (czerwień zarezerwowana dla błędów: toast, `--dk-color-danger`).
- Nie rób: więcej niż ok. 5 punktów - dłuższą listę skróć lub zgrupuj.

**Przykład HTML.**
```html
<div class="notes" aria-labelledby="h-uwagi">
  <p class="eyebrow" id="h-uwagi">Uwagi</p>
  <ul>
    <li><svg class="ic" aria-hidden="true"><use href="#i-alert"/></svg><span>W karcie brakuje składu smaku Wanilia.</span></li>
    <li class="info"><svg class="ic" aria-hidden="true"><use href="#i-info"/></svg><span>Zdjęcie opakowania wybrałem automatycznie.</span></li>
  </ul>
</div>
```

---

## 8. Karta stylu do wyboru

**Opis i kiedy używać.** Duże kafle jednokrotnego wyboru z podglądem (tu: styl prezentacji). Używaj, gdy wybór jest wizualny i opcji jest 2-4.

**Warianty.** Siatka `.styles` po 2 kolumny (w galerii 4 stany obok siebie). Kafel: podgląd 16:9, nazwa, dopisek w nawiasie (`.style-sub`), znacznik wyboru.

**Stany.** Niezaznaczona (ramka `--dk-color-border-strong`), hover (ramka w kolorze etykiety), zaznaczona (zielona ramka, jasnozielone tło, znacznik w rogu), focus-visible (pierścień wokół całej karty).

**Tokeny.**
- Kolory: `--dk-color-bg`, `--dk-color-surface`, `--dk-color-border-strong`, `--dk-color-label`, `--dk-color-brand`, `--dk-color-brand-soft`, `--dk-color-on-brand`, `--dk-color-text-muted`, `--dk-color-focus`
- Typografia: `--dk-fs-base`, `--dk-lh-tight`
- Kształt i cień: `--dk-radius-md`, `--dk-radius-sm`, `--dk-radius-pill`, `--dk-shadow-raised`
- Odstępy i kontrolki: `--dk-space-2`, `--dk-space-3`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`, `--dk-control-focus-width`, `--dk-control-focus-offset`
- Ruch: `--dk-motion-fast`, `--dk-motion-ease`

**Dostępność.** `<label>` z ukrytym (ale rozciągniętym na całą kartę) `<input type="radio">`; grupa w `role="radiogroup"` z `aria-labelledby`. Strzałki zmieniają wybór, Tab wchodzi do grupy. Fokus widoczny przez `:has(input:focus-visible)`. Cała karta to cel dotykowy (znacznie ponad 44 px). Stan "zaznaczona" niesie też znacznik, nie tylko kolor.

**Rób / Nie rób.**
- Rób: jedna opcja zaznaczona domyślnie.
- Rób: podgląd, który naprawdę pokazuje różnicę między opcjami.
- Nie rób: kart do wyboru wielokrotnego (użyj przełączników lub pól wyboru).
- Nie rób: ukrywania inputu przez `display: none` (zniknie z klawiatury) - tylko `opacity: 0`.

**Przykład HTML.**
```html
<div class="styles" role="radiogroup" aria-labelledby="l-styl">
  <label class="style-card"><input type="radio" name="styl" value="nowy" checked>
    <span class="style-img"><img src="nowy.png" alt=""></span>
    <span class="style-name">Nowy styl <span class="style-sub">(sklep)</span></span>
    <span class="style-tick" aria-hidden="true"><svg class="ic"><use href="#i-check"/></svg></span></label>
</div>
```

---

## 9. Suwak 3-stopniowy

**Opis i kiedy używać.** Wybór jednej z trzech wartości (krótka / standardowa / pełna), wzorowany na suwaku "reasoning effort" w ChatGPT: kropkowana szyna, duży biały uchwyt, aktualna wartość nad szyną. Używaj przy ustawieniach o naturalnej skali.

**Warianty.** Dowolna liczba stopni przez `min/max`; etykiety stopni (`.stops`) i opisy wartości ustawiane skryptem (`data-labels`, `data-notes` w galerii). Dwa suwaki jeden pod drugim mają odstęp `--dk-space-8`.

**Stany.** Wartość minimalna / środkowa / maksymalna, hover (uchwyt +5%), aktywny (uchwyt +10%), focus-visible (podwójny pierścień na uchwycie: biały odstęp + zielony obrys).

**Tokeny.**
- Kolory: `--dk-color-brand`, `--dk-color-brand-soft-strong`, `--dk-color-bg`, `--dk-color-border-strong`, `--dk-color-field-border`, `--dk-color-text`, `--dk-color-text-muted`, `--dk-color-focus`
- Typografia: `--dk-font-text`, `--dk-fs-sm`, `--dk-fs-base`, `--dk-fs-xl`, `--dk-lh-snug`, `--dk-lh-tight`
- Kształt i cień: `--dk-radius-pill`, `--dk-shadow-thumb`
- Odstępy i kontrolki: `--dk-space-1`, `--dk-space-2`, `--dk-space-3`, `--dk-space-4`, `--dk-space-8` (uchwyt 32 px), `--dk-control-h-min` (wysokość obszaru 44 px), `--dk-control-focus-width`, `--dk-control-focus-offset`
- Ruch: `--dk-motion-fast`, `--dk-motion-base`, `--dk-motion-ease`

**Dostępność.** Natywny `<input type="range">` z `<label for>`; strzałki, Home, End, PageUp/PageDown działają bez kodu. Ustawiaj `aria-valuetext` ("Standardowa, ok. 14 slajdów"). Przyciski `.stops` to wygoda dla myszy (`aria-hidden`, `tabindex="-1"`, wysokość 44 px). Uchwyt 32 px leży w obszarze 44 px.

**Rób / Nie rób.**
- Rób: pokaż aktualną wartość tekstem nad szyną (nie tylko pozycją uchwytu).
- Rób: podpisz oba końce i środek.
- Nie rób: suwaka do wartości dowolnej z wielu kroków (użyj pola liczbowego).
- Nie rób: `outline: none` bez pierścienia na uchwycie.

**Przykład HTML.**
```html
<div class="slider" data-labels="Krótka|Standardowa|Pełna" data-notes="ok. 8 slajdów|ok. 14 slajdów|ok. 22 slajdy">
  <div class="slider-head"><label class="slider-name" for="in-dlugosc">Długość prezentacji</label>
    <p class="slider-value" aria-hidden="true"><strong></strong> <span></span></p></div>
  <div class="slider-body"><div class="rail" aria-hidden="true"><i class="fill"></i><i class="dot" style="left:0"></i><i class="dot" style="left:50%"></i><i class="dot" style="left:100%"></i></div>
    <input type="range" id="in-dlugosc" min="0" max="2" step="1" value="1"></div>
</div>
```

---

## 10. Przełącznik

**Opis i kiedy używać.** Włącz/wyłącz z natychmiastowym skutkiem (uwzględnij sekcję w prezentacji). Nie używaj do akcji wymagających potwierdzenia.

**Warianty.** Sam przełącznik (tor 48 x 32 px, uchwyt 24 px) lub w wierszu sekcji (rozdz. 11).

**Stany.** Wyłączony (tor `--dk-color-switch-off`), włączony (zielony tor, znacznik na uchwycie), hover (tor ciemniejszy o 8%), focus-visible (pierścień na torze), niedostępny (wyłączony + `disabled`, 45% krycia), zablokowany (włączony + `disabled`).

**Tokeny.**
- Kolory: `--dk-color-switch-off`, `--dk-color-brand`, `--dk-color-bg`, `--dk-color-focus`
- Kształt i cień: `--dk-radius-pill`, `--dk-shadow-raised`
- Odstępy i kontrolki: `--dk-space-1`, `--dk-space-2`, `--dk-space-4`, `--dk-space-6`, `--dk-space-8`, `--dk-space-12`, `--dk-control-focus-width`, `--dk-control-focus-offset`
- Ruch: `--dk-motion-base`, `--dk-motion-ease`

**Dostępność.** `<input type="checkbox" role="switch">` nałożony przezroczyście na grafikę; Spacja przełącza. Nazwa przez `aria-label` lub `aria-labelledby`. Obszar klikalny rozszerzony do 48 x 48 px (tor ma 32 px wysokości). Stan włączony ma znacznik na uchwycie, więc nie polega tylko na kolorze. Kontrast toru vs tło: 3,31:1.

**Rób / Nie rób.**
- Rób: etykieta opisuje stan "włączony" (np. "Sekcja Smaki"), nie akcję.
- Rób: dla stanów niedostępnych wyjaśnij powód tekstem obok.
- Nie rób: przełącznika bez nazwy dostępnej; przełącznika jako przycisku "Zapisz".
- Nie rób: zmiany rozmiarów toru poza siatką 4 px.

**Przykład HTML.**
```html
<span class="switch">
  <input type="checkbox" role="switch" aria-label="Sekcja Smaki" checked>
  <i class="track"></i><i class="knob"><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg></i>
</span>
```

---

## 11. Wiersz sekcji

**Opis i kiedy używać.** Pozycja listy z miniaturą, nazwą, opisem i przełącznikiem - wybór, które części zawartości zostaną uwzględnione. Cały wiersz jest `<label>` przełącznika.

**Warianty.** Zwykły, z tagiem "zawsze" (`.sec-tag` z ikoną kłódki) dla sekcji obowiązkowych. Wiersze układa się w `ul.secs`, między nimi cienka linia `--dk-color-border`.

**Stany.** Włączona (`.is-on`), wyłączona (miniatura przygaszona), hover (nazwa w `--dk-color-brand-hover`), focus-visible (pierścień na przełączniku), niedostępna (`.is-off`: przełącznik `disabled`, opis kursywą z powodem, np. "brak danych w folderze"), zablokowana (`.is-locked`: włączona, `disabled`, tag "zawsze"). Uwaga: w aplikacji `.is-off` znaczy "niedostępna", nie "wyłączona".

**Tokeny.**
- Kolory: `--dk-color-border`, `--dk-color-border-strong`, `--dk-color-surface`, `--dk-color-text-muted`, `--dk-color-brand-hover`
- Typografia: `--dk-fs-base`, `--dk-fs-sm`, `--dk-lh-snug`, `--dk-lh-tight`
- Kształt i odstępy: `--dk-radius-sm`, `--dk-space-1`, `--dk-space-2`, `--dk-space-4`, `--dk-space-5`, `--dk-space-16` i `--dk-space-20` (miniatura 144 px)
- Ruch: `--dk-motion-base`, `--dk-motion-ease`
- Przełącznik: patrz rozdz. 10

**Dostępność.** `aria-labelledby` (nazwa) i `aria-describedby` (opis) na inpucie. Powód niedostępności musi być w opisie (czytany przez czytnik). Wiersz ma ok. 110 px wysokości, przełącznik 48 x 48 px. Miniatura `alt=""`/`aria-hidden`, bo nazwa niesie treść.

**Rób / Nie rób.**
- Rób: opis w jednej linii, konkret ("Tabela na 100 g").
- Rób: odstęp pionowy wiersza min. `--dk-space-4` z każdej strony.
- Nie rób: ukrywania niedostępnej sekcji - pokaż ją i wyjaśnij.
- Nie rób: zmiany kolejności wierszy po włączeniu/wyłączeniu.

**Przykład HTML.**
```html
<ul class="secs"><li>
  <label class="sec is-on">
    <span class="sec-img" aria-hidden="true"><img src="sekcja-smaki.png" alt=""></span>
    <span class="sec-txt"><span class="sec-name" id="sn-smaki"><span>Smaki</span></span><span class="sec-desc" id="sd-smaki">Kafelki z opakowaniami</span></span>
    <span class="switch"><input type="checkbox" role="switch" checked aria-labelledby="sn-smaki" aria-describedby="sd-smaki"><i class="track"></i><i class="knob"><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg></i></span>
  </label>
</li></ul>
```

---

## 12. Pole tekstowe i textarea

**Opis i kiedy używać.** Wpisywanie krótkiego tekstu (`input type="text"`) lub kilku linii (`textarea`). Podpis zawsze nad polem, opcjonalna podpowiedź pod polem.

**Warianty.** `input` (min. 48 px), `textarea` (min. 96 px, `resize: vertical`), z podpowiedzią `.field-hint`. Kolejne pola oddzielone `--dk-layout-stack` (20 px).

**Stany.** Domyślne (ramka 2 px `--dk-color-field-border`), hover (ramka `--dk-color-text-muted`), focus (zielona ramka + miękka poświata `--dk-shadow-focus-field`), z wartością, z podpowiedzią. Stan błędu nie jest zdefiniowany w aplikacji (patrz luki w tokenach).

**Tokeny.**
- Kolory: `--dk-color-field-border`, `--dk-color-text-muted`, `--dk-color-brand`, `--dk-color-bg`
- Typografia: `--dk-font-text`, `--dk-fs-base`, `--dk-fs-sm`, `--dk-lh-snug`
- Kształt i cień: `--dk-radius-sm`, `--dk-shadow-focus-field`
- Odstępy i kontrolki: `--dk-space-2`, `--dk-space-3`, `--dk-space-4`, `--dk-layout-stack`, `--dk-layout-stack-sm`, `--dk-control-h`
- Ruch: `--dk-motion-fast`, `--dk-motion-ease`

**Dostępność.** `<label for>` zawsze widoczny (placeholder nie zastępuje podpisu). Podpowiedź przez `aria-describedby`. `inputmode="url"`, `spellcheck="false"` dla adresów. Ramka pola ma kontrast 3,31:1 z tłem (wymagane 3:1); fokus zmienia kolor ramki i dodaje poświatę (nie tylko kolor). Wysokość 48 px.

**Rób / Nie rób.**
- Rób: odstęp podpisu od pola `--dk-space-3` (12 px).
- Rób: placeholder jako przykład ("np. https://..."), nie instrukcję.
- Nie rób: jasnej ramki `--dk-color-border` na polach (za niski kontrast).
- Nie rób: pól bez widocznego podpisu.

**Przykład HTML.**
```html
<div class="field">
  <label for="in-film">Link do filmu (YouTube) - opcjonalnie</label>
  <input type="text" id="in-film" inputmode="url" placeholder="np. https://www.youtube.com/watch?v=..." spellcheck="false" aria-describedby="film-hint">
  <p class="field-hint" id="film-hint">Wklej link, a dodam slajd z filmem.</p>
</div>
```

---

## 13. Pasek akcji

**Opis i kiedy używać.** Przyklejony do dołu ekranu pasek z główną akcją formularza (tu "Stwórz prezentację") i krótką notatką (szacowany czas). Zawartość ekranu przewija się pod nim.

**Warianty.** `.bar` (sticky w aplikacji), `.bar.is-static` (do dokumentacji). Przycisk główny rozciąga się do `max-width` ok. 580 px.

**Stany.** Statyczny; stan przycisku wg rozdz. 1. Notatka `.bar-note` ukrywana w wąskim oknie.

**Tokeny.**
- Kolory: `--dk-color-bg`, `--dk-color-border-strong`, `--dk-color-text-muted`
- Typografia: `--dk-fs-sm`
- Cień i odstępy: `--dk-shadow-bar`, `--dk-space-2`, `--dk-space-5`, `--dk-space-6`, `--dk-space-8`, `--dk-space-20`
- Przycisk: patrz rozdz. 1

**Dostępność.** Pasek jest w kolejności DOM po treści formularza, więc Tab dochodzi do niego na końcu. Dodaj `scroll-padding-bottom` na dokumencie równe wysokości paska, żeby fokus nie chował się pod nim. Notatka jest tekstem, nie tylko ikoną.

**Rób / Nie rób.**
- Rób: jedna akcja główna + max. jedna notatka.
- Rób: cień `--dk-shadow-bar` rzucany w górę, obramowanie z góry.
- Nie rób: wielu przycisków na pasku ani linków nawigacyjnych.
- Nie rób: paska nad treścią bez zapasu na dole ekranu (ostatni element zostanie zasłonięty).

**Przykład HTML.**
```html
<div class="bar"><div class="wrap bar-in">
  <button type="submit" class="btn btn-primary"><svg class="ic" aria-hidden="true"><use href="#i-sparkles"/></svg>Stwórz prezentację</button>
  <p class="bar-note"><svg class="ic" aria-hidden="true"><use href="#i-clock"/></svg><span>zwykle ok. 30 sekund</span></p>
</div></div>
```

---

## 14. Liczba-bohater i pasek postępu

**Opis i kiedy używać.** Ekran oczekiwania na dłuższy proces: ogromna liczba procentów, pasek postępu, bieżący etap, szacowany czas i możliwość anulowania.

**Warianty.** `.hero-num` (Mindset 168 px, zielony, znak % w kolorze etykiety), `.progress` (pasek 16 px), `.work-step` (etap), `.work-eta` (czas), `.link-btn` "Anuluj".

**Stany.** Postęp 0-100% (szerokość wypełnienia z `--pct`), animowana zmiana szerokości `--dk-motion-slow`.

**Tokeny.**
- Kolory: `--dk-color-brand`, `--dk-color-brand-soft`, `--dk-color-brand-soft-strong`, `--dk-color-label`, `--dk-color-text-muted`
- Typografia: `--dk-font-display`, `--dk-font-text`, `--dk-fs-display-hero`, `--dk-fs-md`, `--dk-fs-xl`, `--dk-lh-display`, `--dk-lh-snug`
- Kształt i odstępy: `--dk-radius-sm`, `--dk-space-1`, `--dk-space-2`, `--dk-space-3`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`
- Ruch: `--dk-motion-slow`, `--dk-motion-ease`

**Dostępność.** Pasek: `role="progressbar"` z `aria-valuemin/max/now` i `aria-label`. Liczba jest ozdobna (`aria-hidden`), żeby czytnik nie powtarzał wartości. Etap w `aria-live="polite"`. Przycisk Anuluj ma 44 px. Zmiana szerokości przy ograniczeniu ruchu jest natychmiastowa.

**Rób / Nie rób.**
- Rób: `font-variant-numeric: tabular-nums`, żeby liczba nie "skakała".
- Rób: podawaj czas jako szacunek ("ok. 12 sekund"), nie obietnicę.
- Nie rób: Mindset 168 px dla tekstu ani dla czegokolwiek poza liczbą.
- Nie rób: paska bez etykiety dostępnej (`aria-label`).

**Przykład HTML.**
```html
<p class="hero-num" aria-hidden="true"><span>68</span><span class="pct-sign">%</span></p>
<div class="progress" role="progressbar" aria-label="Postęp tworzenia prezentacji" aria-valuemin="0" aria-valuemax="100" aria-valuenow="68" style="--pct:68%"><i></i></div>
<p class="work-step" aria-live="polite">Buduję slajdy z kartami smaków</p>
<p class="work-eta">jeszcze ok. 12 sekund</p>
```

---

## 15. Lista kontrolna

**Opis i kiedy używać.** Kolejne etapy procesu w kolejności: co zrobione, co trwa, co czeka. Towarzyszy liczbie-bohaterowi (rozdz. 14).

**Warianty.** Pojedyncza lista w kremowej karcie; wiersz: zrobiony, teraz, oczekujący. Wskaźnik `.spinner` (24 px) także osobno (`.spinner-lg` 64 px).

**Stany.** `li.done` (pełne zielone koło ze znacznikiem, tekst podstawowy), `li.now` (spinner, tekst pogrubiony, `aria-current="step"`), oczekujący (puste koło z obrysem, tekst przygaszony). Przy ograniczeniu ruchu spinner jest statyczny.

**Tokeny.**
- Kolory: `--dk-color-surface`, `--dk-color-border`, `--dk-color-border-strong`, `--dk-color-bg`, `--dk-color-brand`, `--dk-color-brand-soft-strong`, `--dk-color-on-brand`, `--dk-color-text`, `--dk-color-text-muted`
- Typografia: `--dk-fs-md`, `--dk-lh-base`
- Kształt i odstępy: `--dk-layout-card-pad`, `--dk-layout-card-pad-sm`, `--dk-radius-md`, `--dk-radius-pill`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`, `--dk-space-16`

**Dostępność.** `<ol aria-label="Etapy">`; bieżący etap `aria-current="step"`. Koła i spinner `aria-hidden` - stan wynika z kolejności i pogrubienia oraz z komunikatu `aria-live` przy zmianie etapu. Element nieinteraktywny.

**Rób / Nie rób.**
- Rób: nazwy etapów w czasie teraźniejszym ("Buduję slajdy").
- Rób: odstęp między wierszami `--dk-space-5` (20 px).
- Nie rób: więcej niż ok. 7 etapów.
- Nie rób: kilku spinnerów naraz (jeden bieżący etap).

**Przykład HTML.**
```html
<ol class="checklist" aria-label="Etapy">
  <li class="done"><span class="st" aria-hidden="true"><svg class="ic"><use href="#i-check"/></svg></span><span>Czytam folder</span></li>
  <li class="now" aria-current="step"><span class="st" aria-hidden="true"><span class="spinner"></span></span><span>Buduję slajdy</span></li>
  <li><span class="st" aria-hidden="true"></span><span>Zapisuję plik</span></li>
</ol>
```

---

## 16. Znaczek kontroli

**Opis i kiedy używać.** Wynik automatycznej kontroli jakości pod wygenerowanym plikiem: zielony (wszystko dobrze) lub bursztynowy (są rzeczy do sprawdzenia) z krótką listą szczegółów.

**Warianty.** `.qa` (zielony, ikona tarczy), `.qa.warn` (bursztynowy, ikona trójkąta) z listą `.qa-details`.

**Stany.** OK, ostrzeżenie (z listą lub bez). Statyczne.

**Tokeny.**
- Kolory: `--dk-color-brand-soft`, `--dk-color-brand-hover`, `--dk-color-warning-bg`, `--dk-color-warning-border`, `--dk-color-warning-text`
- Typografia: `--dk-font-text`, `--dk-fs-md`, `--dk-fs-sm`, `--dk-lh-snug`
- Kształt i odstępy: `--dk-radius-md`, `--dk-radius-pill`, `--dk-space-2`, `--dk-space-3`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`

**Dostępność.** Wynik w tekście ("Kontrola: 3 rzeczy do sprawdzenia"), nie tylko kolor i ikona. Gdy znaczek pojawia się dynamicznie, nadaj `role="status"`. Kontrast: brand-hover na brand-soft ponad 6:1, warning-text na warning-bg 6,57:1.

**Rób / Nie rób.**
- Rób: konkret w szczegółach ("Slajd 7: brak zdjęcia opakowania").
- Rób: odstęp między punktami szczegółów `--dk-space-5`.
- Nie rób: czerwieni dla ostrzeżeń kontroli.
- Nie rób: znaczka bez liczby/konkretu ("Są problemy").

**Przykład HTML.**
```html
<p class="qa warn" role="status"><svg class="ic" aria-hidden="true"><use href="#i-alert"/></svg>Kontrola: 3 rzeczy do sprawdzenia</p>
<ul class="qa-details"><li>Slajd 4: tekst może być za długi.</li><li>Slajd 7: brak zdjęcia opakowania.</li></ul>
```

---

## 17. Lista "do dopracowania"

**Opis i kiedy używać.** Kremowa karta z punktami - rzeczy, które użytkownik może poprawić ręcznie po wygenerowaniu. Miękka, nieinwazyjna (nie jest ostrzeżeniem).

**Warianty.** Jeden wariant; punkty ozdobne (`::before`, kolor etykiety).

**Stany.** Statyczne; blok ukrywany atrybutem `hidden`, gdy lista jest pusta.

**Tokeny.**
- Kolory: `--dk-color-surface`, `--dk-color-border`, `--dk-color-label`
- Typografia: `--dk-fs-base`, `--dk-lh-base`
- Kształt i odstępy: `--dk-layout-card-pad`, `--dk-layout-card-pad-sm`, `--dk-radius-md`, `--dk-radius-pill`, `--dk-space-1`, `--dk-space-2`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`

**Dostępność.** Zwykły `<ul>`; punkty to ozdoba (nie są w drzewie dostępności). Etykieta "Do dopracowania" powinna być nagłówkiem (`<h2 class="eyebrow">`). Kolor punktów (3,26:1) jest dopuszczalny, bo nie niesie treści.

**Rób / Nie rób.**
- Rób: krótkie, wykonalne punkty z numerem slajdu.
- Rób: odstęp `--dk-space-5` między punktami.
- Nie rób: mieszania z Uwagami (rozdz. 7): Uwagi to przed pracą, ta lista po pracy.
- Nie rób: koloru etykiety jako koloru tekstu punktów.

**Przykład HTML.**
```html
<div class="todo"><h2 class="eyebrow">Do dopracowania</h2>
  <ul><li>Slajd 6: dopisz krótki opis smaku Wanilia.</li><li>Slajd 12: sprawdź zapis liczby porcji.</li></ul>
</div>
```

---

## 18. Toast

**Opis i kiedy używać.** Krótkie, znikające powiadomienie o zdarzeniu (skopiowano, błąd zapisu). Nie zastępuje komunikatu, który użytkownik musi przeczytać - wtedy użyj bloku na stałe.

**Warianty.** Informacja (`.toast`, tło `--dk-color-inverse-bg`), sukces (`.toast.ok`, zielonkawa ikona), błąd (`.toast.error`, tło `--dk-color-danger`). Ikona 24 px, treść, przycisk zamknięcia 44 px.

**Stany.** Domyślny, wejście (`.enter`, animacja `toast-in`), zamykanie (`.leaving`), hover/focus na przycisku zamknięcia (obwódka).

**Tokeny.**
- Kolory: `--dk-color-inverse-bg`, `--dk-color-on-inverse`, `--dk-color-danger`, `--dk-color-brand-soft-strong`
- Typografia: `--dk-fs-base`, `--dk-lh-snug`
- Kształt i cień: `--dk-radius-md`, `--dk-radius-sm`, `--dk-shadow-toast`
- Odstępy i kontrolki: `--dk-space-1`, `--dk-space-2`, `--dk-space-3`, `--dk-space-5`, `--dk-space-6`, `--dk-control-h-min`, `--dk-control-focus-width`
- Ruch: `--dk-motion-base`, `--dk-motion-slow`, `--dk-motion-ease`

**Dostępność.** Kontener `aria-live="polite"`; toast błędu `role="alert"`. Przycisk zamknięcia: `aria-label="Zamknij powiadomienie"`, 44 x 44 px, biały pierścień fokusu. Nie zamykaj błędów samoczynnie zbyt szybko; wstrzymaj zamykanie po najechaniu/fokusie. Kontrast białego tekstu: na brązie 13,65:1, na czerwieni 4,87:1.

**Rób / Nie rób.**
- Rób: jedno zdanie, co się stało i (dla błędu) co zrobić dalej.
- Rób: odstęp między toastami `--dk-space-4`.
- Nie rób: stosu więcej niż 3 toastów; toastów bez możliwości zamknięcia.
- Nie rób: koloru czerwonego dla ostrzeżeń (to Uwagi).

**Przykład HTML.**
```html
<div class="toasts" aria-live="polite" aria-atomic="false">
  <div class="toast error" role="alert"><svg class="ic" aria-hidden="true"><use href="#i-circle-alert"/></svg><span>Nie udało się zapisać pliku.</span>
    <button type="button" class="x" aria-label="Zamknij powiadomienie"><svg class="ic" aria-hidden="true"><use href="#i-x"/></svg></button></div>
</div>
```

---

## 19. Pasek miniatur

**Opis i kiedy używać.** Poziomo przewijany podgląd wielu obrazów 16:9 (slajdy wyniku) z numerem. Używaj, gdy elementów jest więcej, niż mieści się w rzędzie.

**Warianty.** Z zanikaniem prawej krawędzi (gdy jest co przewijać) i `.at-end` (bez zanikania, na końcu listy lub gdy wszystko się mieści).

**Stany.** Domyślny, przewinięty, `.at-end`, fokus na pasku (pierścień). Przewijanie z przyciąganiem (`scroll-snap`, `proximity`).

**Tokeny.**
- Kolory: `--dk-color-bg` (maska zanikania), `--dk-color-border-strong`, `--dk-color-surface`, `--dk-color-inverse-bg`, `--dk-color-on-inverse`
- Typografia: `--dk-font-text`, `--dk-fs-sm`
- Kształt i odstępy: `--dk-radius-btn`, `--dk-radius-pill`, `--dk-radius-sm`, `--dk-space-1`, `--dk-space-2`, `--dk-space-4`, `--dk-space-6`, `--dk-space-8`, `--dk-space-10`, `--dk-space-20` (miniatura 192 px)

**Dostępność.** `<ul tabindex="0" aria-label="Podgląd slajdów (przewiń w bok)">`: fokus na liście pozwala przewijać strzałkami. Każda miniatura powinna mieć `alt="Slajd 3"` (lub podobny), numer w plakietce jest widoczny. Zanikanie krawędzi to sygnał wizualny, nie jedyny - pasek przewijania (cienki, `scrollbar-width: thin`) zostaje widoczny.

**Rób / Nie rób.**
- Rób: stała szerokość miniatury, żeby przewijanie było przewidywalne.
- Rób: zdejmij zanikanie (`.at-end`) po dojściu do końca lub gdy nic nie przewija.
- Nie rób: pionowego przewijania w środku poziomego paska.
- Nie rób: miniatur bez tekstu alternatywnego, gdy niosą treść.

**Przykład HTML.**
```html
<ul class="strip" tabindex="0" aria-label="Podgląd slajdów (przewiń w bok)">
  <li><span class="slide"><img src="slajd-1.png" alt="Slajd 1"></span><span class="num">1</span></li>
  <li><span class="slide"><img src="slajd-2.png" alt="Slajd 2"></span><span class="num">2</span></li>
</ul>
```

---

## 20. Dodatek: ikony i zasady wspólne

**Ikony.** 22 ikony w spricie SVG (`<symbol id="i-...">`), styl Lucide, kreska `--dk-control-stroke-icon` (1,6), `currentColor`, domyślnie 20 px (`--dk-space-5`):
`check`, `minus`, `x`, `folder`, `folder-open`, `sheet`, `doc`, `image`, `alert`, `info`, `lock`, `copy`, `clock`, `chevron`, `shield`, `sparkles`, `refresh`, `present`, `file`, `plus`, `arrow-left`, `circle-alert`.
Użycie: `<svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>`. Ikona bez tekstu obok musi mieć nazwę (`aria-label` na przycisku).

**Podłączenie do projektu.**
```html
<link rel="stylesheet" href="tokens/tokens.css">
<link rel="stylesheet" href="preview/preview.css">   <!-- style komponentów -->
```
Czcionki (`@font-face`) są zdefiniowane w `preview/preview.css` względem `assets/fonts/`.

**Różnice względem aplikacji (świadome).**

| Miejsce | Aplikacja | Biblioteka |
|---|---|---|
| Padding kart | 22-26 px | `--dk-layout-card-pad` (32 px) |
| Odstęp wierszy list | 8-14 px | min. `--dk-space-5` (20 px) |
| Etykieta nad tytułem | margines 10 px | `--dk-space-3` (12 px) |
| Przełącznik | 50 x 30 px | 48 x 32 px (siatka 4 px), obszar klikalny 48 x 48 |
| Pole tekstowe | ramka 1,5 px | ramka 2 px (Chrome zaokrągla 1,5 px w dół przy 100% skali) |
| Zamknięcie toasta | 32 px | 44 px |
| Przyciski `.stops` suwaka | 30 px | 44 px |
| Ramka strefy upuszczania, punkty listy | surowy kolor tan | `--dk-color-label` |

---

## 21. Drabina powierzchni (od 1.4.0)

**Opis i kiedy używać.** Każde tło w aplikacji ma poziom L0-L4 zależny od głębokości zagnieżdżenia. Sąsiednie poziomy różnią się
stałym, małym skokiem jasności (OKLCH: jasny tryb 0,020 w dół, ciemny 0,034 w górę). Dzięki temu okno w oknie zawsze odcina się
od rodzica, a aplikacja z głębokim drzewem (DAM) nie „przepala” kolorów. Wartości: `tokens/tokens.md`, sekcja „Drabina”.

| Poziom | Zmienna | Co na nim leży | Przykład: program / Resizer / DAM |
|---|---|---|---|
| L0 | `--dk-color-surface-0` (= `--dk-color-bg`) | tło okna, pasek akcji | strona / okno / tło aplikacji |
| L1 | `--dk-color-surface-1` (= `--dk-color-surface`) | kontener, sekcja, karta | karta „znalazłem”, karta AI / panel „Lista plików” / panel filtrów, sidebar |
| L2 | `--dk-color-surface-2` (= `--dk-color-surface-hover`) | rubryka, pole, karta w karcie | kafelek smaku, grupa slajdów / lista plików, combo / pole wyszukiwania, karta wyniku |
| L3 | `--dk-color-surface-3` | element w polu: chip, wiersz, okno w oknie | miniatura w kafelku / wiersz listy / wiersz podpowiedzi, sekcja w oknie podglądu |
| L4 | `--dk-color-surface-4` | nakładka: menu, podpowiedź, modal nad modalem | instrukcja po kopiowaniu / menu combo / menu kontekstowe nad podglądem |

**Warianty.** Jeden zestaw poziomów na każdy styl i tryb (`data-theme`): program (`:root`, L0 = biała kartka), krem jasny, zieleń jasna,
zieleń ciemna, krem ciemny. Ramka elementu na poziomie N: `--dk-color-border-subtle-N`. Tekst: `--dk-color-on-surface-N` (= `text`).

**Stany.** Hover elementu na poziomie N = poziom N+1 (jeden krok). Zaznaczenie = `--dk-color-brand-soft` + ramka `--dk-color-brand`, nie kolejny poziom.

**Tokeny.** `--dk-color-surface-0..4`, `--dk-color-border-subtle-0..4`, `--dk-color-on-surface-0..4`, `--dk-color-text-muted`, `--dk-color-label` (tylko L0-L1).
Qt: `T["color_surface_2"]`, `T_DARK["color_surface_2"]` itd.

**Dostępność.** `text` i `text-muted` mają >= 4,5:1 na każdym poziomie każdego wariantu, link (`brand`) na L0-L3, na L4 link w `brand-hover`.
Sprawdza to `build_tokens.py --check`. Skok jasności nie niesie znaczenia sam: zaznaczenie i błąd mają też ramkę, ikonę albo tekst.

**Rób / Nie rób.**
- Rób: policz głębokość (ile razy kontener leży w kontenerze) i przypisz poziom, zanim wybierzesz kolor.
- Rób: ramkę `border-subtle-N` dodawaj tylko tam, gdzie sam skok jasności nie wystarcza (np. pole na tym samym poziomie co rodzic, lista kart).
- Nie rób: białych płyt na kremie albo szałwii w stylach DK (czysta biel tylko jako L0 programu).
- Nie rób: przeskoku o dwa poziomy, żeby „mocniej odciąć” - zamiast tego ramka albo cień nakładki.
- Nie rób: poziomu wyżej niż L4. Głębsze drzewo spłaszcz (np. wiersz w oknie w oknie dostaje ramkę, nie L5).

**Przykład HTML/CSS.**
```css
.page    { background: var(--dk-color-surface-0); }
.card    { background: var(--dk-color-surface-1); border-radius: var(--dk-radius-md); padding: var(--dk-layout-card-pad); }
.field   { background: var(--dk-color-surface-2); border: 1.5px solid var(--dk-color-field-border); border-radius: var(--dk-radius-sm); }
.row     { background: var(--dk-color-surface-3); border-radius: var(--dk-radius-sm); }
.row:hover { background: var(--dk-color-surface-4); }
.menu    { background: var(--dk-color-surface-4); border: 1px solid var(--dk-color-border-subtle-4); box-shadow: var(--dk-shadow-toast); }
```

**Przykład Qt (QSS przez `str.format(**T)`, podwójne klamry = dosłowna klamra).**
```python
from tokens_qt import VARIANTS
T = VARIANTS["zielen-ciemny"]            # albo "program", "krem-jasny", "zielen-jasny", "krem-ciemny"
QSS = """
QMainWindow, QWidget#okno {{ background: {color_surface_0}; color: {color_text}; }}
QFrame#karta   {{ background: {color_surface_1}; border-radius: 12px; }}
QLineEdit, QComboBox, QListView {{ background: {color_surface_2}; border: 1px solid {color_border_subtle_2};
                                   border-radius: 8px; color: {color_text}; }}
QListView::item:hover {{ background: {color_surface_3}; }}
QMenu, QComboBox QAbstractItemView {{ background: {color_surface_4}; border: 1px solid {color_border_subtle_4}; }}
""".format(**T)
```

---

## 22. Tagi i chipy kategorii (od 1.4.0)

**Opis i kiedy używać.** Oznaczenie kategorii (typ, smak, opakowanie, autor, rodzaj slajdu). Kolor tagu to odcień stylu z małym
przesunięciem barwy, nie stała barwa (fiolet, pomarańcz, niebieski). Kategorie rozróżnia etykieta i kolejność; kolor tylko pomaga.

**Wzór (do odtworzenia).** `hue_k = tag_hue stylu + [0, +8, -8, +16, -16, +24, -24, +32][k-1]` (stopnie OKLCH).
`tag_hue`: krem i program 90 (miód, piasek, morela, oliwka), zieleń 146. Tło, ramka i tekst mają stałą jasność i nasycenie trybu:

| Tryb | Tło L / C | Ramka L / C | Tekst L / C (start) |
|---|---|---|---|
| jasny | 0,930 / 0,038 | 0,845 / 0,055 | 0,440 / 0,085, przyciemniany o 0,01 aż kontrast >= 4,6:1 |
| ciemny | 0,360 / 0,048 | 0,470 / 0,062 | 0,870 / 0,070, rozjaśniany o 0,01 aż kontrast >= 4,6:1 |

Kolor poza sRGB: nasycenie maleje o 0,001, odcień i jasność zostają. Parametry: `tokens.json` → `tags`; generator: `build_tokens.py`.

**Warianty.** `tag-1` ... `tag-8` (8 kategorii). Więcej kategorii = powtórz od `tag-1` i rozróżniaj etykietą. Wariant „aktywny filtr”:
tło `--dk-color-brand`, tekst `--dk-color-on-brand` (to już nie tag, tylko wybrany chip). Licznik „+12”: `tag` bez koloru (`surface-3`, `text-muted`).

**Stany.** Hover (klikalny tag): ramka w kolorze tekstu tagu. Fokus: pierścień `--dk-color-focus`. Wyłączony: `opacity: .55`.

**Tokeny.** `--dk-color-tag-N-bg`, `--dk-color-tag-N-fg`, `--dk-color-tag-N-border`, `--dk-radius-pill`, `--dk-space-1`, `--dk-space-2`.

**Dostępność.** Tekst tagu >= 4,5:1 w każdym wariancie (sprawdza `--check`). Tag klikalny ma cel min. 32 px wysokości w gęstym
widoku i 44 px w wygodnym (albo obszar klikalny powiększony paddingiem wiersza).

**Rób / Nie rób.**
- Rób: przypisz kategorię do numeru tagu raz, na stałe (np. smak = 1, typ = 2, opakowanie = 3), w każdej aplikacji tak samo.
- Nie rób: kolorów spoza wzoru, nawet „bo ładniej” - zmień `tag_hue` albo `offsets` w `tokens.json`.
- Nie rób: tagu jako jedynej informacji o stanie (błąd, ostrzeżenie mają swoje role).

**Przykład HTML/CSS.**
```css
.tag { display: inline-flex; align-items: center; min-height: 24px; padding: 0 var(--dk-space-2); border-radius: var(--dk-radius-pill);
       font: 700 13px/1 var(--dk-font-text); background: var(--tag-bg); color: var(--tag-fg); border: 1px solid var(--tag-bd); }
.tag[data-k="1"] { --tag-bg: var(--dk-color-tag-1-bg); --tag-fg: var(--dk-color-tag-1-fg); --tag-bd: var(--dk-color-tag-1-border); }
.tag[data-k="2"] { --tag-bg: var(--dk-color-tag-2-bg); --tag-fg: var(--dk-color-tag-2-fg); --tag-bd: var(--dk-color-tag-2-border); }
/* ... do 8 */
```
```html
<span class="tag" data-k="1">Smak</span> <span class="tag" data-k="3">Opakowanie</span>
```

**Przykład Qt.**
```python
def tag_qss(T, k):   # k = 1..8
    return ("background:{bg}; color:{fg}; border:1px solid {bd}; border-radius:10px; padding:2px 8px;"
            .format(bg=T["color_tag_%d_bg" % k], fg=T["color_tag_%d_fg" % k], bd=T["color_tag_%d_border" % k]))
```


## 23. Skala tekstu i odstępy skopiowane z programu (web i Qt, od 1.5.0)

Źródło: pomiar okna programu „Stwórz prezentację” (`WORK/src/ui/style.css`, `getComputedStyle` w Chromium, 1366x768,
05.10.2026). Web używa wartości programu wprost; Qt (PySide6/QSS, px) używa tokenów `qt.*` - te same proporcje,
ok. 10 % mniej, żeby okno aplikacji desktopowej mieściło się w 1366x768. Wzorcowa aplikacja Qt: Inyfinn Photo Resizer 2.6.4.

### Web (program 1:1)

| Element | Wartość |
|---|---|
| strona | tło L0 `#FFFFFF`, tekst 16 px / 24 px Lato, kolor `text` |
| karta (`.hints`, `.found`, `.checklist`) | tło L1 `#FDF8ED`, ramka 1 px `border` `#EDE7DA`, promień 12 px, wypełnienie 32 px, bez cienia |
| kafelek w karcie (`.flav`) | tło L2 `#F8F1E0`, ramka 1 px `border-subtle-2` `#E8E1D0`, promień 10 px, wypełnienie 8-12 px |
| eyebrow | 15 px bold, wersaliki, odstęp liter 0,1 em, kolor `label`, odstęp pod 12-20 px |
| nagłówek | Mindset 40 px (`.h-md`), 44 px produkt, 60 px „Gotowe” |
| lead / podtytuł | 19 px / 1,4 `text-muted` |
| lista w karcie | 16 px / 1,35, podpis 15 px `text-muted`, odstęp wierszy 16-20 px |
| pole | 48 px, ramka 1,5 px `field-border`, promień 8 px, 16 px tekst, wypełnienie 12/16 px, fokus: ramka `brand` + `shadow-focus-field` |
| etykieta pola | 15 px bold, 8 px nad polem; podpowiedź 15 px `text-muted` |
| przycisk | 48 px, 17 px bold, promień 4 px, ramka 2 px (drugorzędny zielony); główny żółty 56 px / 19 px |
| pasek akcji | tło L0, ramka górna 1 px `border-strong`, cień `shadow-bar`, przycisk 58 px / 20 px |
| odstępy | sekcje 40 px (`layout.section-gap`), kolumny 48 px, stos 20 px (`layout.stack`) |

### Qt (tokeny `qt.*`)

| Element | QSS |
|---|---|
| tekst okna | `font-size: 15px` (`app.setFont` z `setPixelSize(15)`; menu: `app.setFont(font, "QMenuBar")`) |
| karta | `background: L1; border: 1px solid <border>; border-radius: 12px`, wypełnienie 20 px, odstęp między kartami 12-16 px |
| nagłówek karty | Mindset 22 px, wersaliki; okno dialogu 26 px |
| eyebrow | Lato 14 px bold, wersaliki, `letterSpacing` 110 %, kolor `label` |
| etykieta pola | 14 px bold (Lato ma tylko 400 i 700 - nie używaj 600) |
| podpowiedź | 14 px `text-muted` |
| pole (`QLineEdit`, `QComboBox`, `QSpinBox`) | 40 px: `min-height: 30px; padding: 4px 12px; border: 1px solid <field-border>`; fokus `2px solid <focus>`, `padding: 3px 11px` |
| przycisk | 40 px, 15 px bold, ramka 2 px `brand`; mały 36 px |
| przycisk główny | 48 px, 17 px bold, `cta` bez ramki |
| chip / tag klikalny | 48 px, ramka 1 px w kolorze tekstu tagu |
| okno dialogu | marginesy 20/16 px, odstęp 10-12 px |
| okno | min. 1180x700 (mieści się na 1366x768); widok, który nie mieści się w wysokości, przewija się (`QScrollArea`), a nie ściska listy |
