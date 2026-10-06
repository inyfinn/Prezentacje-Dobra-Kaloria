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
23. Skala tekstu i odstępy skopiowane z programu (od 1.5.0)
24. Kontrolki 1.6.0: checkbox, radio, przełącznik, suwak, przycisk drugorzędny, krokomierz, kółko ikony (kolory sprzed 2.0.0)
25. [Przepisy 2.0 „sklep” (web CSS + Qt QSS)](#25-przepisy-20-sklep-web-css) - **obowiązujące przepisy kolorystyczne od 2.0.0**

**Uwaga (2.0.0, 06.10.2026).** Sekcje 1-24 powstały przed rundą 4. Ich **geometria, stany i dostępność** nadal obowiązują, ale **kolory
w nich są sprzed 2.0.0** (brązowy tekst i akcent, kremowa karta jako L1, „zero zieleni”). Obowiązują role i reguły z **rozdz. 25** oraz
`tokens/READY-2.0.0.txt` (S1-S12). Tam, gdzie to była prosta podmiana roli albo hexa, tekst sekcji poprawiono.

Jak z tych klocków złożyć nowy ekran albo nową aplikację: `IDENTYFIKACJA-WIZUALNA.md`.

## Zasady wspólne (dotyczą każdego komponentu)

- **Odstępy (zasada użytkownika "więcej powietrza")**: karta ma wewnętrzny margines `--dk-layout-card-pad` (32 px) lub `--dk-layout-card-pad-lg` (40 px);
  wiersze w listach oddziela min. `--dk-space-5` (20 px); bloki i sekcje `--dk-layout-section-gap` (40 px); podpis od treści min. `--dk-space-3` (12 px).
  Stara aplikacja miała ciaśniej (26 px w kartach, 14 px między wierszami) - w bibliotece obowiązują nowe wartości.
  W wąskim oknie (do 860 px) karty schodzą do `--dk-layout-card-pad-sm`, odstęp między polami do `--dk-layout-stack-sm`.
- **Fokus**: każdy element interaktywny ma pierścień `--dk-control-focus-width` (2 px od 2.0.0) w kolorze `--dk-color-focus`, odsunięty o `--dk-control-focus-offset` (2 px). Nigdy `outline: none` bez zamiennika.
- **Cel dotykowy**: min. `--dk-control-h-min` (44 px) w każdym wymiarze.
- **Kolory**: tylko role `--dk-color-*`, nigdy prymitywy (`--dk-green-750` itp.). Tekst w stylach jasnych `--dk-color-text` `#222222` (od 2.0.0; brąz uchylony), tytuły `--dk-color-heading`, tytuł-akcent `--dk-color-heading-accent`.
- **Czcionki**: Mindset (`--dk-font-display`) tylko w nagłówkach i liczbach, zawsze `text-transform: uppercase` (font nie ma małych liter). Lato (`--dk-font-text`) do reszty.
- **Etykieta** (`--dk-color-label`): od 2.0.0 w stylach jasnych `#333333` (kontrast > 11:1 na L0-L1; wcześniej brąz `#85654A`). Pogrubiony tekst min. 14-15 px (etykieta nad tytułem). Nigdy tekst ciągły. Zasada „tylko L0-L1” dotyczy stylów ciemnych (tam etykieta jest beżowa): na L2 i głębiej w ciemnych etykieta w `--dk-color-text-muted`. Dekoracja (ramka przerywana, punktory) = `--dk-color-accent-beige`.
- **Zieleń (od 2.0.0)**: `--dk-color-brand` `#007936` to akcent interfejsu: przycisk główny, ikony liniowe (`icon`), kropki list, metki, aktywna zakładka, fokus, znak checkboxa, suwak, przełącznik. `--dk-color-heading-accent` `#00642E`: tytuł główny, nadtytuł, aktywna zakładka, podpis ikony. Zasada 1.6.0 „zero zieleni” (G2/G3) UCHYLONA. Kontrolki: rozdz. 25.
- **Powierzchnie (od 1.4.0, jasne przebudowane w 2.0.0)**: każde tło bierzesz z drabiny `--dk-color-surface-0..4` według głębokości zagnieżdżenia (rozdz. 21), nie „na oko”. `--dk-color-bg` = L0 (białe), `--dk-color-surface` = L1 (panel), `--dk-color-surface-hover` = `#F6F2EF` (hover, pasy tabeli; od 2.0.0 NIE jest już aliasem L2). W stylach jasnych L2 jest BIAŁE i jaśniejsze od L1.
- **Ruch**: przejścia `--dk-motion-fast/base/slow` + `--dk-motion-ease`; przy `prefers-reduced-motion: reduce` animacje są wyłączone (spinner staje się statyczny).
- **Ikony**: Lucide-style, kreska `--dk-control-stroke-icon`, `currentColor`, `aria-hidden="true"` gdy dekoracyjne (lista w rozdz. 20).
- **Stany wymuszone** w galerii (`.is-hover`, `.is-focus`, `.is-active`) służą tylko do dokumentacji - w produkcji działają `:hover`, `:focus-visible`, `:active`.
- Bez pauz długich w tekście interfejsu (używaj zwykłego łącznika "-"), bez emoji.

---

## 1. Przyciski

> Kolory w tej sekcji sprzed 2.0.0 — obowiązują role i reguły z rozdz. 25 i READY-2.0.0.txt.

**Opis i kiedy używać.** Od 2.0.0 przycisk główny jest zielony pełny (`brand`, biały tekst Lato 700 wersalikami, róg 4 px); żółty (`cta`, tekst `#222222`) to jedna wyróżniona akcja widoku („Wybierz folder”). Obok niego przycisk drugorzędny (S6: tło białe, tekst `#222222` wersalikami, ramka 1 px `btn2-border` `#222222`, promień 4 px, hover `#F6F2EF`) i link-przycisk (nawigacja: bez podkreślenia, aktywny lub hover zielony) do akcji pobocznych. Przepis kodu: rozdz. 25.

**Warianty.** `.btn.btn-primary` (56 px, 20 px tekst), `.btn.btn-secondary` (48 px, 17 px), `.link-btn` (44 px, 16 px). Ikona 20-24 px przed tekstem, odstęp `--dk-space-3`.

**Stany.** Domyślny, hover (`.is-hover`), focus-visible (`.is-focus`), aktywny (`.is-active`, przesunięcie o 1 px w dół), wyłączony (`disabled` / `.is-disabled`: tło `--dk-color-disabled-bg`, tekst przygaszony, kursor `not-allowed`).

**Tokeny.**
- Kolory: `--dk-color-cta`, `--dk-color-cta-hover`, `--dk-color-on-cta`, `--dk-color-btn2-bg`, `--dk-color-btn2-text`, `--dk-color-btn2-border`, `--dk-color-btn2-hover-bg`, `--dk-color-accent`, `--dk-color-accent-hover`, `--dk-color-disabled-bg`, `--dk-color-text-muted`, `--dk-color-focus`
- Typografia: `--dk-font-text`, `--dk-fs-base`, `--dk-fs-md`, `--dk-fs-lg`, `--dk-lh-tight`
- Kształt i odstępy: `--dk-radius-btn`, `--dk-space-1`, `--dk-space-2`, `--dk-space-3`, `--dk-space-6`, `--dk-space-8`, `--dk-space-10`
- Kontrolki i ruch: `--dk-control-h`, `--dk-control-h-lg`, `--dk-control-h-min`, `--dk-control-btn2-border-width`, `--dk-control-focus-width`, `--dk-control-focus-offset`, `--dk-motion-fast`, `--dk-motion-ease`

**Dostępność.** Natywny `<button type="button">` (lub `type="submit"`); Enter i Spacja aktywują. Wyłączenie atrybutem `disabled`. Ikony `aria-hidden`. Wysokości 56 / 48 / 44 px spełniają cel dotykowy. Kontrast tekstu: on-brand na brand 5,54:1, on-cta na cta 11,44:1, btn2-text na btn2-bg 15,91:1, obrys btn2-border na btn2-bg 15,91:1 (sprawdza `--check`).

**Rób / Nie rób.**
- Rób: czasownik w etykiecie ("Stwórz prezentację"); jeden żółty przycisk wyróżnionej akcji na widok.
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

**Dostępność.** Nagłówek to prawdziwy `<h1>`/`<h2>` (jedna `h1` na ekran); etykieta może być `<p>` lub nagłówkiem niższego rzędu. Etykieta nie zastępuje `<label>` pojedynczego pola. Od 2.0.0 etykieta `#333333` ma kontrast > 11:1 (w stylach ciemnych beżowa etykieta nadal tylko na L0-L1 i dla pogrubionego tekstu min. 15 px). Nagłówek: tytuł główny `heading-accent`, tytuł karty `heading`.

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

> Kolory w tej sekcji sprzed 2.0.0 — obowiązują role i reguły z rozdz. 25 i READY-2.0.0.txt.

**Stany (od 2.0.0).** Krok bieżący (`li[aria-current="step"]`): wypełnienie `step-active-bg` (zieleń `#007936`) + tekst `step-active-text` (biały); nieaktywny: obrys `step-idle-border`, tekst `step-idle-text`; zrobiony: zielony ptaszek `step-done`. Łącznik przed krokiem bieżącym i po zrobionym ma kolor `step-done`, pozostałe `step-idle-border`. W DK1 ciemny wszystkie role akcentu są limonką. Pasek kroków sklepu (5 px, aktywny `progress`): rozdz. 25. Przepis: rozdz. 25.

**Tokeny.**
- Kolory: `--dk-color-step-active-bg`, `--dk-color-step-active-text`, `--dk-color-step-idle-border`, `--dk-color-step-idle-text`, `--dk-color-step-done`, `--dk-color-text`, `--dk-color-text-muted`, `--dk-color-border-strong`, `--dk-color-bg`
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

**Warianty.** Jedna strefa; zawartość: ikona w kwadracie 48 px (tło `icon-bg` `#F5F5F5`, promień 4, ikona `icon` zielona; od 2.0.0 nie w kole), tytuł Mindset w kolorze `heading`, podtytuł, przycisk `.btn-secondary`.

**Stany.** Bezczynna (przerywana ramka w kolorze `accent-beige`, tło `--dk-color-surface`), hover (tło `--dk-color-surface-hover`), nad strefą (`.is-over`: ciągła ramka `accent`, tło `surface-2`, ikona `accent`, tekst "Puść teraz"), z fokusem na przycisku wewnątrz.

**Tokeny.**
- Kolory: `--dk-color-surface`, `--dk-color-surface-hover`, `--dk-color-accent-beige`, `--dk-color-accent`, `--dk-color-icon`, `--dk-color-icon-bg`, `--dk-color-text-muted`
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

**Opis i kiedy używać.** Podsumowanie wyniku analizy: co program znalazł w folderze. Od 2.0.0 biała karta (L2) w panelu L1 (nie kremowa karta jako L1) z tytułem produktu i listą wierszy, każdy z ikoną stanu, nazwą i opcjonalną drugą linią.

**Warianty.** Wiersz: znaleziono (zielone koło ze znacznikiem), brak (`.f-none`: szare koło z minusem, tekst przygaszony), ostrzeżenie (`.f-warn`, propozycja: bursztynowe koło). Opcjonalnie `.f-sub` (druga linia) i `.f-hint` (ikona informacji + zdanie).

**Stany.** Statyczne; karta może zawierać `.flavs` (rozdz. 6) i `.notes` (rozdz. 7) jako osobne bloki.

**Tokeny.**
- Kolory: `--dk-color-surface`, `--dk-color-border`, `--dk-color-brand`, `--dk-color-brand-soft`, `--dk-color-disabled-bg`, `--dk-color-text-muted`, `--dk-color-warning-bg`, `--dk-color-warning-border`, `--dk-color-warning-text`
- Typografia: `--dk-fs-base`, `--dk-fs-sm`, `--dk-lh-base`, `--dk-lh-snug`
- Kształt i odstępy: `--dk-layout-card-pad`, `--dk-layout-card-pad-sm` (do 860 px), `--dk-radius-md`, `--dk-radius-pill`, `--dk-space-1`, `--dk-space-2`, `--dk-space-3`, `--dk-space-4`, `--dk-space-5`, `--dk-space-6`

**Dostępność.** `<ul>`; ikony `aria-hidden`. Stan musi wynikać z tekstu, nie tylko z ikony i koloru - dla braku zawsze dopisz "nie znaleziono" w `.f-sub`. Kontrast tekstu muted na tle karty powyżej 4,5:1 (`#666666` na bieli 5,74:1).

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

**Stany (G1, kolory 2.0.0).** Niezaznaczona (ramka `--dk-color-border-strong`, w rogu pusty radio), hover (ramka `check-border`), zaznaczona (ramka 2 px `brand`, tło `surface-2`, w rogu **radio wg rozdz. 25**: białe wnętrze `check-bg`, zielony obrys i zielona kropka `check-mark`; nie wypełnione ciemne koło), focus-visible (pierścień wokół całej karty). Nie ma kółek obok kwadratów: w kafelku wyboru jednokrotnego radio, w liście wielokrotnego checkbox, nigdy oba.

**Tokeny.**
- Kolory: `--dk-color-bg`, `--dk-color-surface`, `--dk-color-border-strong`, `--dk-color-accent`, `--dk-color-check-bg`, `--dk-color-check-border`, `--dk-color-check-border-hover`, `--dk-color-check-mark`, `--dk-color-text-muted`, `--dk-color-focus`
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

**Stany (kolory 2.0.0).** Tor `slider-track` `#E9E9E9`, wypełnienie `slider-fill` (zieleń `#007936`; w DK1 ciemny limonka), uchwyt `slider-thumb` (biały; w ciemnych poziom L1) z obrysem 2 px `slider-thumb-border` (zielony). Wartość minimalna / środkowa / maksymalna, hover (uchwyt +5%), aktywny (uchwyt +10%), focus-visible (podwójny pierścień na uchwycie: odstęp w kolorze tła + obrys `focus`). Przepis: rozdz. 25.

**Tokeny.**
- Kolory: `--dk-color-slider-track`, `--dk-color-slider-fill`, `--dk-color-slider-thumb`, `--dk-color-slider-thumb-border`, `--dk-color-bg`, `--dk-color-border-strong`, `--dk-color-field-border`, `--dk-color-text`, `--dk-color-text-muted`, `--dk-color-focus`
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

**Stany (kolory 2.0.0).** Wyłączony (tor `--dk-color-switch-off` `#E9E9E9` + obrys 1,5 px `switch-off-border` `#868E96`, gałka `switch-knob`), włączony (tor `switch-on` = zieleń `#007936`, gałka biała, znacznik na gałce w kolorze toru), hover (tor ciemniejszy o 8%), focus-visible (pierścień na torze), niedostępny (wyłączony + `disabled`, 45% krycia), zablokowany (włączony + `disabled`). Uwaga: od 1.6.0 `switch-off` to tor (jasny, ok. 1,4:1 z tłem); widoczność wyłączonego przełącznika niesie jego obrys `switch-off-border` (3,3:1). Przepis: rozdz. 25.

**Tokeny.**
- Kolory: `--dk-color-switch-off`, `--dk-color-switch-off-border`, `--dk-color-switch-on`, `--dk-color-switch-knob`, `--dk-color-bg`, `--dk-color-focus`
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

**Stany.** Domyślne (białe wnętrze `check-bg`, ramka 1 px `--dk-color-field-border` `#868E96` od 2.0.0, promień 4; w galerii sprzed 2.0.0 2 px), hover (ramka `--dk-color-text-muted`), focus (zielona ramka + miękka poświata `--dk-shadow-focus-field`), z wartością, z podpowiedzią. Stan błędu nie jest zdefiniowany w aplikacji (patrz luki w tokenach).

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

**Warianty.** `.hero-num` (Mindset 168 px, `heading-accent`, znak % w kolorze etykiety), `.progress` (pasek 16 px, wypełnienie `progress` `#47C33D` na torze `#E9E9E9`), `.work-step` (etap), `.work-eta` (czas), `.link-btn` "Anuluj".

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

**Warianty.** Pojedyncza lista w białej karcie (L2) na panelu; wiersz: zrobiony, teraz, oczekujący. Wskaźnik `.spinner` (24 px) także osobno (`.spinner-lg` 64 px).

**Stany (G1, kolory 2.0.0).** `li.done` (znacznik: białe wnętrze `check-bg`, obrys `check-border`, zielony ptaszek `check-mark`; tekst podstawowy; to znacznik postępu, nie pole do kliknięcia), `li.now` (spinner w kolorze `accent`, tekst pogrubiony, `aria-current="step"`), oczekujący (pusty znacznik z obrysem `check-disabled-border`, tekst przygaszony). Przy ograniczeniu ruchu spinner jest statyczny. Wnętrze znacznika zawsze białe (nie zielone wypełnienie).

**Tokeny.**
- Kolory: `--dk-color-surface`, `--dk-color-border`, `--dk-color-border-strong`, `--dk-color-bg`, `--dk-color-check-bg`, `--dk-color-check-border`, `--dk-color-check-mark`, `--dk-color-check-disabled-border`, `--dk-color-accent`, `--dk-color-text`, `--dk-color-text-muted`
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

**Opis i kiedy używać.** Karta z punktami (od 2.0.0 biała karta L2 w panelu L1) - rzeczy, które użytkownik może poprawić ręcznie po wygenerowaniu. Miękka, nieinwazyjna (nie jest ostrzeżeniem).

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

**Dostępność.** Kontener `aria-live="polite"`; toast błędu `role="alert"`. Przycisk zamknięcia: `aria-label="Zamknij powiadomienie"`, 44 x 44 px, biały pierścień fokusu. Nie zamykaj błędów samoczynnie zbyt szybko; wstrzymaj zamykanie po najechaniu/fokusie. Kontrast białego tekstu: na `inverse-bg` `#222222` 15,91:1, na czerwieni 5,91:1.

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

**Ikony.** 22 ikony w spricie SVG (`<symbol id="i-...">`), styl Lucide, kreska `--dk-control-stroke-icon` (2 od 2.0.0; wcześniej 1,6), `currentColor`, domyślnie 20 px (`--dk-space-5`), w przycisku-ikonie 24 px. Od 2.0.0 ikona ma kolor `--dk-color-icon` (zieleń `#007936`), a przycisk-ikona kwadrat 44 px z tłem `--dk-color-icon-bg` (`#F5F5F5`, promień 4; nie koło); kontrast ikony na tle >= 3:1 (sprawdza `--check`). W DK1 ciemny `icon` = limonka.
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

> Kolory poziomów jasnych w tej sekcji przepisano na 2.0.0 (sklep); pełny przepis: rozdz. 25 i `tokens/READY-2.0.0.txt`.

**Opis i kiedy używać.** Każde tło w aplikacji ma poziom L0-L4 zależny od głębokości zagnieżdżenia. **Style jasne (2.0.0, jawne wartości ze sklepu):**
L0 biel, L1 panel jasnoszary ciepły, L2 BIAŁA karta lub pole w panelu, L3 kafel ecru, L4 kafel w kaflu (głębszy beż). L2 jest JAŚNIEJSZY od L1,
a L4 nie jest nakładką. **Style ciemne** liczone wzorem jak dotąd (OKLCH: ciemny 0,034 w górę, L4 = nakładka). Dzięki temu okno w oknie zawsze
odcina się od rodzica, a aplikacja z głębokim drzewem (DAM) nie „przepala” kolorów. Wartości: `tokens/tokens.md`, sekcja „Drabina”.

| Poziom | Zmienna | Co na nim leży (jasne) | Wartość jasna sklep / krem | Przykład: program / Resizer / DAM |
|---|---|---|---|---|
| L0 | `--dk-color-surface-0` (= `--dk-color-bg`) | tło okna, pasek akcji | `#FFFFFF` / `#FFFFFF` | strona / okno / tło aplikacji |
| L1 | `--dk-color-surface-1` (= `--dk-color-surface`) | panel, sekcja | `#F8F7F5` / `#FDF8EC` | panel „znalazłem”, karta AI / panel „Lista plików” / panel filtrów, sidebar |
| L2 | `--dk-color-surface-2` | biała karta lub pole w panelu | `#FFFFFF` / `#FFFFFF` | karty i pola w panelu / lista plików, combo / pole wyszukiwania, karta wyniku |
| L3 | `--dk-color-surface-3` | kafel w karcie: ecru | `#FDF8EC` / `#F5ECD8` | kafelek smaku / wiersz listy / grupa tagów, sekcja w oknie podglądu |
| L4 | `--dk-color-surface-4` | kafel w kaflu (głębszy beż) | `#F5ECD8` / `#F0E6CF` | miniatura w kafelku / - / kafel w kaflu |

**Nakładki** (menu, lista rozwijana, podpowiedź, modal): rola `--dk-color-overlay` (`#FFFFFF`) + `--dk-shadow-toast` + ramka `--dk-color-border`.
W stylach ciemnych nakładką nadal jest L4.

**Warianty.** Jeden zestaw poziomów na każdy styl i tryb (`data-theme`): program (`:root`, = sklep), krem jasny, zieleń jasna (= sklep),
zieleń ciemna, krem ciemny. Ramka elementu na poziomie N: `--dk-color-border-subtle-N`. Tekst: `--dk-color-on-surface-N` (= `text`).

**Stany.** Hover = rola `--dk-color-surface-hover` (`#F6F2EF`) w stylach jasnych; w ciemnych poziom N+1. Zaznaczenie = obrys `--dk-color-brand` (zieleń; w 1.6.0 był brąz) + znak wg rozdz. 25, nie kolejny poziom.

**Tokeny.** `--dk-color-surface-0..4`, `--dk-color-border-subtle-0..4`, `--dk-color-on-surface-0..4`, `--dk-color-text-muted`, `--dk-color-label` (tylko L0-L1).
Qt: `T["color_surface_2"]`, `T_DARK["color_surface_2"]` itd.

**Dostępność.** `text` i `text-muted` mają >= 4,5:1 na każdym poziomie każdego wariantu, zielony tekst i link (`brand`) >= 4,5:1 na L0-L4 stylów jasnych.
Sprawdza to `build_tokens.py --check`. Skok jasności nie niesie znaczenia sam: zaznaczenie i błąd mają też ramkę, ikonę albo tekst.

**Rób / Nie rób.**
- Rób: policz głębokość (ile razy kontener leży w kontenerze) i przypisz poziom, zanim wybierzesz kolor.
- Rób: ramkę `border-subtle-N` dodawaj tylko tam, gdzie sam skok jasności nie wystarcza (np. pole na tym samym poziomie co rodzic, lista kart).
- Nie rób: beżowego, ecru ani szarego tła okna w stylach jasnych (S1: L0 zawsze biel). Biała karta wprost na bieli dostaje linię 1 px `border`.
- Nie rób: przeskoku o dwa poziomy, żeby „mocniej odciąć” - zamiast tego ramka albo cień nakładki.
- Nie rób: poziomu wyżej niż L4. Głębsze drzewo spłaszcz (np. wiersz w oknie w oknie dostaje ramkę, nie L5).

**Przykład HTML/CSS.**
```css
.page    { background: var(--dk-color-surface-0); }
.panel   { background: var(--dk-color-surface-1); border-radius: var(--dk-radius-md); padding: var(--dk-layout-card-pad); }
.card    { background: var(--dk-color-surface-2); border-radius: var(--dk-radius-md); }      /* biała karta w panelu */
.field   { background: var(--dk-color-surface-2); border: 1px solid var(--dk-color-field-border); border-radius: var(--dk-radius-sm); }
.tile    { background: var(--dk-color-surface-3); border-radius: var(--dk-radius-md); }      /* kafel ecru w karcie */
.row:hover { background: var(--dk-color-surface-hover); }
.menu    { background: var(--dk-color-overlay); border: 1px solid var(--dk-color-border); box-shadow: var(--dk-shadow-toast); }
```

**Przykład Qt (QSS przez `str.format(**T)`, podwójne klamry = dosłowna klamra).**
```python
from tokens_qt import VARIANTS
T = VARIANTS["program"]                  # albo "krem-jasny", "zielen-jasny", "zielen-ciemny", "krem-ciemny"
QSS = """
QMainWindow, QWidget#okno {{ background: {color_surface_0}; color: {color_text}; }}
QFrame#panel   {{ background: {color_surface_1}; border-radius: {qt_radius_card}; }}
QFrame#karta   {{ background: {color_surface_2}; border-radius: {qt_radius_card}; }}
QLineEdit, QComboBox, QListView {{ background: {color_surface_2}; border: 1px solid {color_field_border};
                                   border-radius: {qt_radius_field}; color: {color_text}; }}
QListView::item:hover {{ background: {color_surface_hover}; }}
QMenu, QComboBox QAbstractItemView {{ background: {color_overlay}; border: 1px solid {color_border}; }}
""".format(**T)
```

---

## 22. Tagi i chipy kategorii (od 1.4.0)

**Opis i kiedy używać.** Oznaczenie kategorii (typ, smak, opakowanie, autor, rodzaj slajdu). Kolor tagu to odcień stylu z małym
przesunięciem barwy, nie stała barwa (fiolet, pomarańcz, niebieski). Kategorie rozróżnia etykieta i kolejność; kolor tylko pomaga.

**Wzór (do odtworzenia).** `hue_k = tag_hue stylu + offsets[k-1]` (stopnie OKLCH). **Od 2.0.0 style jasne (program, krem jasny, zieleń jasny) mają tagi w odcieniach zieleni**: `tag_hue` 152, `offsets` `[0, +8, -8, +16, -16, +24, -24, +32]`, czyli odcienie 120...184 (tag-1: tło `#D6F0DC`, tekst `#28603A`, ramka `#B2D7BB`). Ciepłe odcienie 98...62 z 1.6.0 („zero zieleni”, G2) są uchylone dla stylów jasnych. Zieleń ciemny: `tag_hue` 146 i te same `offsets`; krem ciemny zostaje przy `tag_hue` 90 i ciepłych `tag_offsets` `[0, +8, -8, -12, -16, -20, -24, -28]` (bez zmian).
`tag_hue`: style jasne 152, zieleń ciemny 146, krem ciemny 90. Tło, ramka i tekst mają stałą jasność i nasycenie trybu:

| Tryb | Tło L / C | Ramka L / C | Tekst L / C (start) |
|---|---|---|---|
| jasny | 0,930 / 0,038 | 0,845 / 0,055 | 0,440 / 0,085, przyciemniany o 0,01 aż kontrast >= 4,6:1 |
| ciemny | 0,360 / 0,048 | 0,470 / 0,062 | 0,870 / 0,070, rozjaśniany o 0,01 aż kontrast >= 4,6:1 |

Kolor poza sRGB: nasycenie maleje o 0,001, odcień i jasność zostają. Parametry: `tokens.json` → `tags`; generator: `build_tokens.py`.

**Warianty.** `tag-1` ... `tag-8` (8 kategorii). Więcej kategorii = powtórz od `tag-1` i rozróżniaj etykietą. Wariant „aktywny filtr”:
tło `--dk-color-brand`, tekst `--dk-color-on-brand` (to już nie tag, tylko wybrany chip; metka pełna jak w sklepie, promień 4). Licznik „+12”: `tag` bez koloru (`surface-3`, `text-muted`).

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

> Kolory w tej sekcji sprzed 2.0.0 — obowiązują role i reguły z rozdz. 25 i READY-2.0.0.txt. Skala tekstu i odstępy nadal obowiązują.

Źródło: pomiar okna programu „Stwórz prezentację” (`WORK/src/ui/style.css`, `getComputedStyle` w Chromium, 1366x768,
05.10.2026). Web używa wartości programu wprost; Qt (PySide6/QSS, px) używa tokenów `qt.*` - te same proporcje,
ok. 10 % mniej, żeby okno aplikacji desktopowej mieściło się w 1366x768. Wzorcowa aplikacja Qt: Inyfinn Photo Resizer 2.6.4.

### Web (program 1:1)

| Element | Wartość |
|---|---|
| strona | tło L0 `#FFFFFF`, tekst 16 px / 24 px Lato, kolor `text` |
| panel (`.hints`, `.found`, `.checklist`) | od 2.0.0 tło L1 `#F8F7F5`, bez ramki i cienia, promień 8 px, wypełnienie 32 px; w nim biała karta L2 (do 1.6.0: kremowa karta L1 `#FDF8ED` z ramką `#EDE7DA`, promień 12) |
| kafelek w karcie (`.flav`) | od 2.0.0 tło L3 `#FDF8EC` (ecru), promień 8 px, wypełnienie 8-12 px (do 1.6.0: L2 `#F8F1E0` z ramką, promień 10) |
| eyebrow | 15 px bold, wersaliki, odstęp liter 0,1 em, kolor `label`, odstęp pod 12-20 px |
| nagłówek | Mindset 40 px (`.h-md`), 44 px produkt, 60 px „Gotowe” |
| lead / podtytuł | 19 px / 1,4 `text-muted` |
| lista w karcie | 16 px / 1,35, podpis 15 px `text-muted`, odstęp wierszy 16-20 px |
| pole | 48 px, białe, ramka 1 px `field-border` `#868E96`, promień 4 px (2.0.0; do 1.6.0: 1,5 px i 8 px), 16 px tekst, wypełnienie 12/16 px, fokus: ramka `brand` + `shadow-focus-field` |
| etykieta pola | 15 px bold, 8 px nad polem; podpowiedź 15 px `text-muted` |
| przycisk | 48 px, 15-17 px bold wersaliki, promień 4 px; drugorzędny: białe tło, tekst `btn2-text` `#222222`, ramka 1 px `btn2-border` `#222222`; główny od 2.0.0 zielony `brand` z białym tekstem (do 1.6.0 żółty 56 px / 19 px; żółty zostaje dla wyróżnionej akcji) |
| pasek akcji | tło L0, ramka górna 1 px `border-strong`, cień `shadow-bar`, przycisk 58 px / 20 px |
| odstępy | sekcje 40 px (`layout.section-gap`), kolumny 48 px, stos 20 px (`layout.stack`) |

### Qt (tokeny `qt.*`)

| Element | QSS |
|---|---|
| tekst okna | `font-size: 15px` (`app.setFont` z `setPixelSize(15)`; menu: `app.setFont(font, "QMenuBar")`) |
| panel / karta | panel `background: {color_surface_1}; border-radius: {qt_radius_card}` (8 px), karta w nim `{color_surface_2}`; karta na bieli `border: 1px solid {color_border}`; wypełnienie 20 px, odstęp między kartami 12-16 px |
| nagłówek karty | Mindset 22 px, wersaliki; okno dialogu 26 px |
| eyebrow | Lato 14 px bold, wersaliki, `letterSpacing` 110 %, kolor `label` |
| etykieta pola | 14 px bold (Lato ma tylko 400 i 700 - nie używaj 600) |
| podpowiedź | 14 px `text-muted` |
| pole (`QLineEdit`, `QComboBox`, `QSpinBox`) | 40 px: `min-height: 30px; padding: 4px 12px; border: 1px solid <field-border>`; fokus `2px solid <focus>`, `padding: 3px 11px` |
| przycisk | 40 px, 15 px bold; drugorzędny: tło `btn2_bg`, tekst `btn2_text`, ramka 1 px `btn2_border` (`#222222`); mały 36 px |
| przycisk główny | 48 px, 17 px bold, od 2.0.0 `brand` z `on_brand` bez ramki (żółty `cta` tylko dla wyróżnionej akcji) |
| chip / tag klikalny | 48 px, ramka 1 px w kolorze tekstu tagu |
| okno dialogu | marginesy 20/16 px, odstęp 10-12 px |
| okno | min. 1180x700 (mieści się na 1366x768); widok, który nie mieści się w wysokości, przewija się (`QScrollArea`), a nie ściska listy |

---

## 24. Kontrolki 1.6.0: checkbox, radio, przełącznik, suwak, przycisk drugorzędny, krokomierz, kółko ikony

> Kolory w tej sekcji sprzed 2.0.0 — obowiązują role i reguły z rozdz. 25 i READY-2.0.0.txt. Kolumna „jasne” w tabeli poniżej i teksty reguł poprawiono na 2.0.0; kod CSS/QSS (struktura, wymiary) nadal się zgadza.

**Opis i kiedy używać.** Jeden zestaw przepisów dla trzech aplikacji (program, Photo Resizer, DAM), pierwotnie wynik rundy 3 (06.10.2026, reguły G1-G9
w `RUNDA-3-2026-10-06.md`); kolory przepisane na 2.0.0 (runda 4, `RUNDA-4-SKLEP-2026-10-06.md`). Żywy test: `preview/kontrolki.html`
(galeria SPRZED 2.0.0, kolory nieaktualne; wzorzec 2.0: `preview/sklep.html`, zrzut `preview/shots/71-sklep-kontrolki.png`).

**Zasady (skrót; G1 zostaje, kolory G2-G6 zastąpione przez S6-S8).**
- **Zieleń marki (`brand`) jest akcentem kontrolek** (od 2.0.0; zasada G3 „tylko logo, splash, KPI, status” uchylona). Kontrolki biorą role `check-*`, `slider-*`, `switch-*`, `btn2-*`, `step-*`, `accent`, `icon`.
- **Checkbox i radio (G1, S8):** wnętrze zawsze BIAŁE (`check-bg`), także zaznaczone; obrys `check-border` `#868E96`, hover i zaznaczenie `check-border-hover` (zielony); zaznaczenie to zielony ptaszek (radio: kropka) w `check-mark`, NIE wypełniony ciemny kwadrat. Wyłączony: obrys `check-disabled-border`, znak `check-disabled-mark`. Rozmiar `control-check-size` (20 px), promień `control-check-radius` (4 px; radio okrągłe), obrys `control-check-border-width` (1,5 px).
- **Przycisk drugorzędny (S6):** tło `btn2-bg` (białe), tekst `btn2-text` `#222222` pogrubiony wersalikami, obrys 1 px `btn2-border` `#222222`, promień 4 px, hover tło `btn2-hover-bg` `#F6F2EF`.
- **Suwak i przełącznik (S8):** tor `slider-track` / `switch-off` `#E9E9E9`, wypełnienie `slider-fill` zielone, uchwyt `slider-thumb` biały z obrysem 2 px `slider-thumb-border` zielonym; przełącznik wyłączony = tor `switch-off` + obrys `switch-off-border`, włączony = tor `switch-on` zielony, gałka `switch-knob`.
- **Krokomierz (S8):** aktywny segment = wypełnienie `step-active-bg` (zielone) + tekst `step-active-text`; nieaktywny = obrys `step-idle-border` + tekst `step-idle-text`; ukończony = ptaszek `step-done`. Pasek kroków sklepu (5 px, `progress`): rozdz. 25.
- **Ikona (S7):** przycisk-ikona kwadratowy 44 px z tłem `icon-bg` `#F5F5F5` (kółko od 2.0.0 tylko dla awatara, kropki, gałki i radio), ikona `icon` zielona. Link w treści: `#222222`, pogrubiony, podkreślony (S12).
- **DK1 ciemny (G9)** zostaje zielony, ale checkbox ma wnętrze `check-bg` = L3 (jaśniejsze od tła, nie ciemna dziura), obrys `moss-400`, znak limonka. **DK2 ciemny:** wnętrze = poziom tła (L0), obrys `#CBBFA8`, znak `#E6D3A0`.

**Wartości (wygenerowane z `tokens.json`; style jasne = program, krem jasny i zieleń jasny mają identyczne role; kolumny ciemne bez zmian od 1.6.0).**

| Rola | Style jasne (2.0.0: program, DK2 jasny, DK1 jasny) | DK2 ciemny (krem) | DK1 ciemny (zieleń) |
|---|---|---|---|
| `accent` | `#007936` | `#E6D3A0` | `#A2D686` |
| `accent-hover` | `#00642E` | `#F5F1E8` | `#C2E59F` |
| `on-accent` | `#FFFFFF` | `#1C1812` | `#0F190C` |
| `accent-beige` (dekoracja) | `#AD8767` | `#D2B48F` | `#ECCA76` |
| `icon` / `icon-bg` | `#007936` / `#F5F5F5` | `#CBBFA8` / `#2C261E` | `#A2D686` / `#303C21` |
| `check-bg` | `#FFFFFF` | `#120F0A` | `#303C21` |
| `check-border` / `-hover` | `#868E96` / `#007936` | `#CBBFA8` / `#E6D3A0` | `#889979` / `#A2D686` |
| `check-mark` | `#007936` | `#E6D3A0` | `#A2D686` |
| `check-disabled-border` / `-mark` | `#CED4DA` / `#ADB5BD` | `#5F5240` / `#8C7D65` | `#516448` / `#889979` |
| `slider-track` / `-fill` | `#E9E9E9` / `#007936` | `#3F362A` / `#CBBFA8` | `#3B4E37` / `#A2D686` |
| `slider-thumb` / `-border` | `#FFFFFF` / `#007936` | `#1A1611` / `#E6D3A0` | `#192C18` / `#A2D686` |
| `switch-off` / `-border` | `#E9E9E9` / `#868E96` | `#3F362A` / `#8C7D65` | `#889979` / `#889979` |
| `switch-on` / `switch-knob` | `#007936` / `#FFFFFF` | `#AD8767` / `#FFFFFF` | `#A2D686` / `#0F190C` |
| `btn2-bg` / `-text` | `#FFFFFF` / `#222222` | `#1A1611` / `#F5F1E8` | `#192C18` / `#A2D686` |
| `btn2-border` / `-hover-bg` | `#222222` / `#F6F2EF` | `#8C7D65` / `#231E17` | `#A2D686` / `#24341C` |
| `step-active-bg` / `-text` | `#007936` / `#FFFFFF` | `#E6D3A0` / `#1C1812` | `#A2D686` / `#0F190C` |
| `step-idle-border` / `-text` | `#CED4DA` / `#666666` | `#5F5240` / `#CBBFA8` | `#516448` / `#C9BEA6` |
| `step-done` | `#007936` | `#E6D3A0` | `#A2D686` |
| `label` / `focus` | `#333333` / `#007936` | `#D2B48F` / `#E6D3A0` | `#ECCA76` / `#FFD42A` |

(Wartości z aliasów drabiny (`icon-bg`, `check-bg`, `slider-thumb`, `btn2-bg`, `btn2-hover-bg`) w kolumnach ciemnych to poziomy L0-L3 tego wariantu; pełna drabina: `tokens/tokens.md`. Odstępstwo od kontraktu: `switch-knob` w DK2 ciemny to `#FFFFFF`, bo ivory `#F5F1E8` dawał 2,89:1 na torze `#AD8767`, a wymagane jest 3:1.)

**Tokeny.** Kolory: `--dk-color-check-*`, `slider-*`, `switch-*`, `btn2-*`, `step-*`, `accent`, `accent-hover`, `icon`, `icon-bg`, `focus`. Kontrolki: `--dk-control-check-size`, `check-radius`, `check-border-width`, `btn2-border-width`, `slider-thumb-border-width`, `focus-width`, `focus-offset`, `h`, `h-min`.

**Dostępność (sprawdza `build_tokens.py --check`, każdy wariant).** `check-mark` na `check-bg` >= 4,5:1; `check-border` na `check-bg`, `surface-0` i `surface-1` >= 3:1; `slider-fill` na `slider-track` >= 3:1; obrys uchwytu na uchwycie >= 3:1; `switch-on` i obrys wyłączonego na tle >= 3:1; gałka na torze `switch-on` >= 3:1; `btn2-text` na `btn2-bg` i `btn2-hover-bg` >= 4,5:1; `btn2-border` >= 3:1; `step-active-text` na `step-active-bg` >= 4,5:1; `icon` na `icon-bg` >= 3:1; `focus` >= 3:1. Stan niesie nie tylko kolor: ptaszek / kropka / położenie gałki / pozycja suwaka. Cel dotykowy 44 px: etykieta obok kontrolki jest klikalna (`<label>`), suwak ma wysokość `control-h-min`.

### Web (CSS; tylko `--dk-color-*` i `--dk-control-*`)

```css
/* znak: ptaszek rysowany clip-path w kolorze currentColor (bez obrazków) */
.dk-tick { display: inline-block; width: 14px; height: 14px; background: currentColor;
           clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%); }

/* checkbox i radio: <input type="checkbox" class="dk-check"> / <input type="radio" class="dk-radio"> */
.dk-check, .dk-radio {
  appearance: none; -webkit-appearance: none; flex: none; margin: 0; display: inline-grid; place-content: center;
  width: var(--dk-control-check-size); height: var(--dk-control-check-size);
  background: var(--dk-color-check-bg);                       /* wnętrze JASNE, także zaznaczone */
  border: var(--dk-control-check-border-width) solid var(--dk-color-check-border);
  border-radius: var(--dk-control-check-radius);
  color: var(--dk-color-check-mark); cursor: pointer;
  transition: border-color var(--dk-motion-fast) var(--dk-motion-ease);
}
.dk-radio { border-radius: 50%; }
.dk-check::after { content: ""; width: 12px; height: 12px; background: currentColor; transform: scale(0);
  clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%); transition: transform var(--dk-motion-fast) var(--dk-motion-ease); }
.dk-radio::after { content: ""; width: 10px; height: 10px; border-radius: 50%; background: currentColor; transform: scale(0);
  transition: transform var(--dk-motion-fast) var(--dk-motion-ease); }
.dk-check:checked::after, .dk-radio:checked::after { transform: scale(1); }
.dk-check:hover, .dk-radio:hover { border-color: var(--dk-color-check-border-hover); }
.dk-check:focus-visible, .dk-radio:focus-visible, .dk-switch input:focus-visible, .dk-slider:focus-visible, .dk-btn2:focus-visible, .dk-btn1:focus-visible {
  outline: var(--dk-control-focus-width) solid var(--dk-color-focus); outline-offset: var(--dk-control-focus-offset); }
.dk-check:disabled, .dk-radio:disabled { border-color: var(--dk-color-check-disabled-border); color: var(--dk-color-check-disabled-mark); cursor: not-allowed; }
.dk-field { display: inline-flex; align-items: center; gap: var(--dk-space-3); min-height: var(--dk-control-h-min); cursor: pointer; color: var(--dk-color-text); }
.dk-field:has(:disabled) { color: var(--dk-color-text-muted); cursor: not-allowed; }

/* przełącznik: <span class="dk-switch"><input type="checkbox" role="switch" aria-label="..."></span> */
.dk-switch { position: relative; display: inline-block; width: 48px; height: 32px; flex: none; }
.dk-switch input { appearance: none; -webkit-appearance: none; position: absolute; inset: 0; width: 100%; height: 100%; margin: 0; cursor: pointer;
  background: var(--dk-color-switch-off); border: var(--dk-control-check-border-width) solid var(--dk-color-switch-off-border);
  border-radius: var(--dk-radius-pill); transition: background var(--dk-motion-base) var(--dk-motion-ease), border-color var(--dk-motion-base) var(--dk-motion-ease); }
.dk-switch input::before { content: ""; position: absolute; top: 50%; left: 3px; width: 22px; height: 22px; margin-top: -11px; border-radius: 50%;
  background: var(--dk-color-switch-knob); box-shadow: var(--dk-shadow-raised);
  transition: transform var(--dk-motion-base) var(--dk-motion-ease); }
.dk-switch input:checked { background: var(--dk-color-switch-on); border-color: var(--dk-color-switch-on); }
.dk-switch input:checked::before { transform: translateX(16px); }
.dk-switch input:hover { border-color: var(--dk-color-check-border-hover); }
.dk-switch input:checked:hover { background: var(--dk-color-accent-hover); border-color: var(--dk-color-accent-hover); }
.dk-switch input:disabled { opacity: .45; cursor: not-allowed; }

/* suwak: <input type="range" class="dk-slider" style="--pct:50%"> ; --pct aktualizuj w zdarzeniu input (value / max * 100) */
.dk-slider { -webkit-appearance: none; appearance: none; width: 100%; height: var(--dk-control-h-min); margin: 0; background: transparent; cursor: pointer; --pct: 50%; }
.dk-slider::-webkit-slider-runnable-track { height: 8px; border-radius: var(--dk-radius-pill);
  background: linear-gradient(to right, var(--dk-color-slider-fill) var(--pct), var(--dk-color-slider-track) var(--pct)); }
.dk-slider::-webkit-slider-thumb { -webkit-appearance: none; box-sizing: border-box; width: 24px; height: 24px; margin-top: -8px; border-radius: 50%;
  background: var(--dk-color-slider-thumb); border: var(--dk-control-slider-thumb-border-width) solid var(--dk-color-slider-thumb-border); box-shadow: var(--dk-shadow-thumb); }
.dk-slider::-moz-range-track { height: 8px; border-radius: var(--dk-radius-pill); background: var(--dk-color-slider-track); }
.dk-slider::-moz-range-progress { height: 8px; border-radius: var(--dk-radius-pill); background: var(--dk-color-slider-fill); }
.dk-slider::-moz-range-thumb { box-sizing: border-box; width: 24px; height: 24px; border-radius: 50%;
  background: var(--dk-color-slider-thumb); border: var(--dk-control-slider-thumb-border-width) solid var(--dk-color-slider-thumb-border); box-shadow: var(--dk-shadow-thumb); }
.dk-slider:hover::-webkit-slider-thumb { transform: scale(1.05); }

/* przyciski: główny (jeden na widok) i drugorzędny */
.dk-btn1, .dk-btn2 { display: inline-flex; align-items: center; justify-content: center; gap: var(--dk-space-2); cursor: pointer;
  border-radius: var(--dk-radius-btn); font: 700 var(--dk-fs-md)/1 var(--dk-font-text); transition: background var(--dk-motion-fast) var(--dk-motion-ease); }
.dk-btn1 { min-height: var(--dk-control-h); padding: 0 var(--dk-space-8); background: var(--dk-color-cta); color: var(--dk-color-on-cta); border: 0; }
.dk-btn1:hover { background: var(--dk-color-cta-hover); }
.dk-btn2 { min-height: var(--dk-control-h); padding: 0 var(--dk-space-6); background: var(--dk-color-btn2-bg); color: var(--dk-color-btn2-text);
  border: var(--dk-control-btn2-border-width) solid var(--dk-color-btn2-border); }
.dk-btn2:hover { background: var(--dk-color-btn2-hover-bg); }
.dk-btn1:active, .dk-btn2:active { transform: translateY(1px); }
.dk-btn2:disabled { background: var(--dk-color-disabled-bg); color: var(--dk-color-text-muted); border-color: var(--dk-color-border-strong); cursor: not-allowed; }

/* krokomierz: segmenty, nie kółka. <ol class="dk-steps"><li class="done"><span class="dk-tick"></span>Folder</li><li aria-current="step">Ustawienia</li><li>Tworzenie</li></ol> */
.dk-steps { display: flex; flex-wrap: wrap; gap: var(--dk-space-2); margin: 0; padding: 0; list-style: none; }
.dk-steps li { display: inline-flex; align-items: center; gap: var(--dk-space-2); min-height: 36px; padding: 0 var(--dk-space-4);
  border: 1px solid var(--dk-color-step-idle-border); border-radius: var(--dk-radius-btn);
  color: var(--dk-color-step-idle-text); font: 700 var(--dk-fs-sm)/1 var(--dk-font-text); }
.dk-steps li.done { color: var(--dk-color-text); }
.dk-steps li.done .dk-tick { color: var(--dk-color-step-done); }
.dk-steps li[aria-current="step"] { background: var(--dk-color-step-active-bg); border-color: var(--dk-color-step-active-bg); color: var(--dk-color-step-active-text); }

/* kółko pod ikoną: <span class="dk-icon-circle"><svg class="ic" aria-hidden="true">...</svg></span> */
.dk-icon-circle { display: inline-grid; place-content: center; width: 48px; height: 48px; border-radius: 50%;
  background: var(--dk-color-icon-bg); color: var(--dk-color-icon); }
.dk-icon-circle .ic { width: 24px; height: 24px; fill: none; stroke: currentColor; stroke-width: var(--dk-control-stroke-icon); stroke-linecap: round; stroke-linejoin: round; }

/* link w treści (S12, 2.0.0): #222222, pogrubiony, PODKREŚLONY; reguła 05.10 „bez podkreślenia w spoczynku” uchylona (link nawigacji: bez podkreślenia, aktywny/hover zielony) */
.dk-link { color: var(--dk-color-text); font-weight: 700; text-decoration: underline; text-underline-offset: 3px; }
.dk-link:hover, .dk-link:focus-visible { color: var(--dk-color-accent-hover); }
.dk-link:focus-visible { outline: var(--dk-control-focus-width) solid var(--dk-color-focus); outline-offset: var(--dk-control-focus-offset); }
```

```html
<label class="dk-field"><input type="checkbox" class="dk-check" checked> Sekcja Smaki</label>
<label class="dk-field"><input type="radio" name="styl" class="dk-radio" checked> Nowy styl</label>
<span class="dk-switch"><input type="checkbox" role="switch" aria-label="Uwzględnij sekcję" checked></span>
<input type="range" class="dk-slider" min="0" max="100" value="50" style="--pct:50%" aria-label="Długość">
<button type="button" class="dk-btn2">Wybierz folder</button>
```

### Qt (QSS przez `str.format(**T)`, `T = VARIANTS["krem-jasny"]` itd.)

QSS nie rysuje ptaszka. Ptaszek, kropka radio i gałka przełącznika to obrazek `image: url(...)`: mały SVG w kolorze `check-mark` (a dla stanu
wyłączonego `check-disabled-mark`) generowany raz na wariant do katalogu tymczasowego aplikacji. Jeśli wtyczka SVG Qt jest niedostępna,
wyrenderuj ten sam SVG przez `QSvgRenderer` do PNG 20x20 i podaj ścieżkę PNG. Całkowite px w QSS: obrys 1,5 px zapisz jako `2px`
(ułamków QSS nie obsługuje; do potwierdzenia na ekranie w aplikacji).

```python
import os, tempfile
from tokens_qt import VARIANTS

def dk_kontrolki_svg(T, katalog=None):
    """Zapisuje SVG-i kontrolek w kolorach wariantu; zwraca słownik nazwa -> ścieżka z ukośnikami (do url(...) w QSS)."""
    katalog = katalog or tempfile.mkdtemp(prefix="dk_ctrl_")
    ptaszek = '<path d="M5 10.5l3.2 3.2L15 6.8" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    pliki = {
        "check":          ('0 0 20 20', ptaszek.format(c=T["color_check_mark"])),
        "check_disabled": ('0 0 20 20', ptaszek.format(c=T["color_check_disabled_mark"])),
        "radio":          ('0 0 20 20', '<circle cx="10" cy="10" r="5" fill="%s"/>' % T["color_check_mark"]),
        "radio_disabled": ('0 0 20 20', '<circle cx="10" cy="10" r="5" fill="%s"/>' % T["color_check_disabled_mark"]),
        "knob_off":       ('0 0 44 28', '<circle cx="14" cy="14" r="11" fill="%s"/>' % T["color_switch_knob"]),
        "knob_on":        ('0 0 44 28', '<circle cx="30" cy="14" r="11" fill="%s"/>' % T["color_switch_knob"]),
    }
    out = {}
    for nazwa, (vb, kszt) in pliki.items():
        sciezka = os.path.join(katalog, "%s.svg" % nazwa)
        w, h = vb.split()[2:]
        with open(sciezka, "w", encoding="utf8") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="%s">%s</svg>' % (w, h, vb, kszt))
        out[nazwa] = sciezka.replace("\\", "/")
    return out

T = dict(VARIANTS["krem-jasny"]); T.update({"img_" + k: v for k, v in dk_kontrolki_svg(T).items()})
QSS_KONTROLKI = """
/* checkbox i radio: wnętrze jasne, obrys check_border, znak z obrazka */
QCheckBox, QRadioButton {{ color: {color_text}; spacing: 10px; min-height: 28px; }}
QCheckBox:disabled, QRadioButton:disabled {{ color: {color_text_muted}; }}
QCheckBox::indicator, QRadioButton::indicator {{ width: 16px; height: 16px; background: {color_check_bg};
    border: 2px solid {color_check_border}; border-radius: 4px; }}
QRadioButton::indicator {{ border-radius: 10px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {color_check_border_hover}; }}
QCheckBox::indicator:checked {{ image: url({img_check}); }}
QRadioButton::indicator:checked {{ image: url({img_radio}); }}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{ border-color: {color_check_disabled_border}; }}
QCheckBox::indicator:checked:disabled {{ image: url({img_check_disabled}); }}
QRadioButton::indicator:checked:disabled {{ image: url({img_radio_disabled}); }}
QCheckBox:focus, QRadioButton:focus {{ outline: none; }}
QCheckBox::indicator:focus, QRadioButton::indicator:focus {{ border-color: {color_focus}; }}

/* przełącznik = QCheckBox z objectName "przelacznik": tor w QSS, gałka w obrazku */
QCheckBox#przelacznik::indicator {{ width: 44px; height: 28px; border-radius: 16px; background: {color_switch_off};
    border: 2px solid {color_switch_off_border}; image: url({img_knob_off}); }}
QCheckBox#przelacznik::indicator:checked {{ background: {color_switch_on}; border-color: {color_switch_on}; image: url({img_knob_on}); }}
QCheckBox#przelacznik::indicator:disabled {{ border-color: {color_check_disabled_border}; }}

/* suwak */
QSlider::groove:horizontal {{ height: 8px; background: {color_slider_track}; border-radius: 4px; }}
QSlider::sub-page:horizontal {{ background: {color_slider_fill}; border-radius: 4px; }}
QSlider::handle:horizontal {{ width: 20px; height: 20px; margin: -8px 0; background: {color_slider_thumb};
    border: 2px solid {color_slider_thumb_border}; border-radius: 12px; }}
QSlider::handle:horizontal:focus {{ border-color: {color_focus}; }}

/* przycisk drugorzędny: setProperty("dk", "secondary") */
QPushButton[dk="secondary"] {{ min-height: 38px; padding: 0 20px; background: {color_btn2_bg}; color: {color_btn2_text};
    border: 1px solid {color_btn2_border}; border-radius: 4px; font-weight: 700; font-size: 15px; }}
QPushButton[dk="secondary"]:hover {{ background: {color_btn2_hover_bg}; }}
QPushButton[dk="secondary"]:focus {{ border-color: {color_focus}; }}
QPushButton[dk="secondary"]:disabled {{ background: {color_disabled_bg}; color: {color_text_muted}; border-color: {color_border_strong}; }}

/* krokomierz: QLabel z właściwością step = active | idle | done */
QLabel[step] {{ min-height: 24px; padding: 4px 14px; border-radius: 4px; font-weight: 700; font-size: 14px;
    border: 1px solid {color_step_idle_border}; color: {color_step_idle_text}; background: transparent; }}
QLabel[step="active"] {{ background: {color_step_active_bg}; border-color: {color_step_active_bg}; color: {color_step_active_text}; }}
QLabel[step="done"] {{ color: {color_text}; }}   /* tekst etykiety: '<span style="color:{color_step_done}">&#10003;</span> Folder' */

/* kółko pod ikoną: QLabel#kolko_ikony 48x48, ikona (QIcon / SVG) przemalowana na color_icon */
QLabel#kolko_ikony {{ background: {color_icon_bg}; border-radius: 24px; min-width: 48px; max-width: 48px; min-height: 48px; max-height: 48px; }}
""".format(**T)
# po zmianie właściwości (step, dk) odśwież styl: w.style().unpolish(w); w.style().polish(w)
```

Link w treści w `QLabel` z tekstem sformatowanym (S12, 2.0.0): `<a href="..." style="color:{color_text}; font-weight:700; text-decoration:underline">` (Qt rich text domyślnie podkreśla linki, co tu jest pożądane); kolor `color_accent_hover` na hover przez `linkHovered(str)` (nie sprawdzone w aplikacji). Link nawigacji (przycisk-link): `QPushButton#link { background: transparent; border: 0; color: {color_text}; font-weight: 700; }` i `QPushButton#link:hover, QPushButton#link:focus { color: {color_accent_hover}; }` (bez podkreślenia, aktywny zielony).

**Rób / Nie rób.**
- Rób: te same role w web i Qt; różni się tylko sposób narysowania znaku.
- Rób: w stylu DK1 ciemny zostaw limonkę w znaku i obrysie (G9), ale tło wnętrza z `check-bg`.
- Nie rób: ciemnego, wypełnionego kwadratu dla zaznaczonego checkboxa; zielonego obrysu 2 px na przycisku drugorzędnym (jest biały z obrysem `#222222`); kółek (radio) obok kwadratów (checkbox) w tej samej grupie wyboru.
- Nie rób: brązowych kontrolek w stylach jasnych (brąz z 1.6.0 uchylony); kontrolki biorą role, które w stylach jasnych dają zieleń `#007936`.

---

## 25. Przepisy 2.0 „sklep” (web CSS)

**Opis i kiedy używać.** Obowiązujące przepisy komponentów od 2.0.0 (runda 4, 06.10.2026): wygląd sklepu dobrakaloria.pl odtworzony ze zrzutów
(`DOWODY-SKLEP.md`), reguły S1-S12 z `tokens/READY-2.0.0.txt`. Rozdział zastępuje kolorystykę rozdz. 1-24 dla stylów jasnych; style ciemne
bez zmian (role te same, wartości ciemne). Kod CSS niżej jest skopiowany **bez zmian** z `preview/sklep.html` (blok od komentarza
`==== 25. PRZEPISY 2.0 ====` do `---- układ tej planszy`); tam działa też jako test, zrzuty: `preview/shots/70-sklep-*.png`, `71-sklep-*.png`.
Używa wyłącznie zmiennych `--dk-*` z `tokens/tokens.css`, więc działa w każdym stylu (`data-theme`).

**Qt.** Dla każdej grupy podano równoważny QSS przez `str.format(**T)` (`T = VARIANTS["program"]` itd., podwójne klamry `{{ }}` = dosłowna klamra),
z rolami jako `{color_*}` z `tokens_qt.py` i wymiarami `{qt_*}`. QSS nie ma `clip-path`, `text-transform` ani cienia pudełkowego: wersaliki ustaw w tekście
(`.upper()`), flagę ceny narysuj `paintEvent`em albo użyj prostokąta z metką, cień nakładki daj `QGraphicsDropShadowEffect`. Ułamkowe px QSS nie obsługuje.

### 25.1 Strona i poziomy (S1, S2, S3)

Okno białe; panel jasnoszary (L1) bez obrysu i cienia; w nim biała karta (L2); w karcie kafel ecru (L3), w kaflu głębszy beż (L4). Biała karta wprost na
białym tle (`.dk-card--on-page`) dostaje linię 1 px. Jasne style: L2 jaśniejszy od L1. Panel, karta, kafel: 8 px.

```css
/* ==== 25. PRZEPISY 2.0 ==== */
.dk-page { background: var(--dk-color-bg); color: var(--dk-color-text); font: 400 var(--dk-fs-base)/var(--dk-lh-base) var(--dk-font-text); }

/* poziomy: biel -> panel -> biała karta -> kafel ecru -> kafel w kaflu */
.dk-panel { background: var(--dk-color-surface-1); border-radius: var(--dk-radius-md); padding: var(--dk-space-8); }
.dk-card { background: var(--dk-color-surface-2); border-radius: var(--dk-radius-md); padding: var(--dk-space-6); }
.dk-card--on-page { border: 1px solid var(--dk-color-border); }      /* biała karta bez panelu pod spodem */
.dk-tile { background: var(--dk-color-surface-3); border-radius: var(--dk-radius-md); padding: var(--dk-space-5); }
.dk-tile .dk-tile { background: var(--dk-color-surface-4); }
/* S14: lista pozycji na bieli - kontener BEZ tła, szare są dopiero pozycje (kafle listy) */
.dk-item { background: var(--dk-color-surface-1); border-radius: var(--dk-radius-md); padding: var(--dk-space-4) var(--dk-space-5); }
.dk-panel .dk-item { background: var(--dk-color-surface-2); }
.dk-divider { border: 0; border-top: 1px solid var(--dk-color-border); margin: var(--dk-space-4) 0; }
```

```css
QMainWindow, QWidget#okno {{ background: {color_surface_0}; color: {color_text}; font-size: {qt_fs_body}; }}
QFrame#panel {{ background: {color_surface_1}; border-radius: {qt_radius_card}; }}
QFrame#karta {{ background: {color_surface_2}; border-radius: {qt_radius_card}; }}
QFrame#karta[naBialym="true"] {{ border: 1px solid {color_border}; }}          /* karta wprost na białym oknie */
QFrame#kafel {{ background: {color_surface_3}; border-radius: {qt_radius_card}; }}
QFrame#kafel QFrame#kafel {{ background: {color_surface_4}; }}                 /* kafel w kaflu */
QFrame#linia {{ background: {color_border}; max-height: 1px; min-height: 1px; border: 0; }}
```

### 25.2 Tytuły, etykiety i linki (S4, S5, S12)

Tytuły Mindset wersalikami (+0.01em). `.dk-h1`-`.dk-h3` prawie czarne (`heading`), `.dk-h-accent` ciemnozielony (`heading-accent`): tytuł główny widoku,
nadtytuł sekcji, aktywna zakładka, podpis ikony. Tekst `#222222`, pomocniczy `.dk-muted` `#666666`, etykieta `.dk-label` `#333333`. Link w treści pogrubiony i
podkreślony; link nawigacji bez podkreślenia (aktywny lub hover zielony).

```css
/* tytuły: Mindset wersalikami, prawie czarne; tytuł-akcent zielony */
.dk-h1, .dk-h2, .dk-h3, .dk-h-accent { font-family: var(--dk-font-display); font-weight: 400; text-transform: uppercase;
  letter-spacing: .01em; line-height: 1.05; color: var(--dk-color-heading); margin: 0; }
.dk-h1 { font-size: var(--dk-fs-display-sm); }
.dk-h2 { font-size: 30px; }
.dk-h3 { font-size: 22px; }
.dk-h-accent { font-size: 22px; color: var(--dk-color-heading-accent); }
.dk-label { font: 700 14px/1.3 var(--dk-font-text); text-transform: uppercase; letter-spacing: .02em; color: var(--dk-color-label); }
.dk-muted { color: var(--dk-color-text-muted); }
.dk-link { color: var(--dk-color-text); font-weight: 700; text-decoration: underline; text-underline-offset: 3px; }
.dk-link:hover { color: var(--dk-color-accent-hover); }
```

```css
QLabel#h1, QLabel#h2, QLabel#h3 {{ font-family: "Mindset"; color: {color_heading}; }}
QLabel#h1 {{ font-size: {qt_fs_dialog_title}; }}
QLabel#h2 {{ font-size: {qt_fs_title}; }}
QLabel#h3 {{ font-size: {qt_fs_app_title}; }}
QLabel#hAccent {{ font-family: "Mindset"; font-size: {qt_fs_title}; color: {color_heading_accent}; }}
QLabel#etykieta {{ font-weight: 700; font-size: {qt_fs_label}; color: {color_label}; }}
QLabel#pomocniczy {{ color: {color_text_muted}; font-size: {qt_fs_hint}; }}
/* link w treści (QLabel, rich text): '<a href="..." style="color:{color_text}; font-weight:700; text-decoration:underline">' */
```

### 25.3 Przyciski (S6)

Główny: zielony pełny, biały tekst Lato 700 wersalikami, promień 4, hover `brand-hover`. Drugorzędny: biały, obrys 1 px `#222222`, hover `#F6F2EF`.
Żółty `.dk-btn--cta` = jedna wyróżniona akcja widoku, tekst `#222222`. `.dk-btn--display` to napis Mindset 20 px jak „DO KOSZYKA”. Wyłączony: tło `disabled-bg`.

```css
/* przyciski: główny zielony, drugorzędny biały z ciemnym obrysem, wyróżniony żółty */
.dk-btn { display: inline-flex; align-items: center; justify-content: center; gap: var(--dk-space-2); min-height: var(--dk-control-h);
  padding: 0 var(--dk-space-6); border-radius: var(--dk-radius-btn); border: 1px solid transparent; cursor: pointer;
  font: 700 15px/1 var(--dk-font-text); text-transform: uppercase; letter-spacing: .02em; white-space: nowrap;
  transition: background-color var(--dk-motion-fast) var(--dk-motion-ease), border-color var(--dk-motion-fast) var(--dk-motion-ease); }
.dk-btn:focus-visible { outline: var(--dk-control-focus-width) solid var(--dk-color-focus); outline-offset: var(--dk-control-focus-offset); }
.dk-btn--primary { background: var(--dk-color-brand); color: var(--dk-color-on-brand); }
.dk-btn--primary:hover { background: var(--dk-color-brand-hover); }
.dk-btn--secondary { background: var(--dk-color-btn2-bg); color: var(--dk-color-btn2-text); border-color: var(--dk-color-btn2-border); }
.dk-btn--secondary:hover { background: var(--dk-color-btn2-hover-bg); }
.dk-btn--cta { background: var(--dk-color-cta); color: var(--dk-color-on-cta); }
.dk-btn--cta:hover { background: var(--dk-color-cta-hover); }
.dk-btn--display { font: 400 20px/1 var(--dk-font-display); letter-spacing: .01em; }   /* jak „DO KOSZYKA” */
.dk-btn:disabled { background: var(--dk-color-disabled-bg); color: var(--dk-color-text-muted); border-color: transparent; cursor: not-allowed; }
.dk-btn--block { display: flex; width: 100%; }
/* S13: przycisk cichy (trzeciorzędny) - samo wypełnienie, bez obrysu; w grupie najwyżej 1 główny i 1 z obrysem, reszta cicha */
.dk-btn--quiet { background: var(--dk-color-icon-bg); color: var(--dk-color-text); }
.dk-panel .dk-btn--quiet, .dk-panel .dk-iconbtn { background: var(--dk-color-surface-2); }
.dk-card .dk-btn--quiet, .dk-card .dk-iconbtn, .dk-tile .dk-btn--quiet { background: var(--dk-color-icon-bg); }
.dk-btn--quiet:hover, .dk-panel .dk-btn--quiet:hover, .dk-card .dk-btn--quiet:hover { background: var(--dk-color-brand-soft); }
/* S13: przełącznik segmentowy (filtry „Wszystko / Produkty”) - aktywny zielony, nieaktywny cichy, bez obrysów */
.dk-seg { display: inline-flex; gap: 4px; }
.dk-seg > button { min-height: 36px; padding: 0 var(--dk-space-4); border: 0; border-radius: var(--dk-radius-btn); cursor: pointer;
  background: var(--dk-color-icon-bg); color: var(--dk-color-text); font: 700 14px/1 var(--dk-font-text); }
.dk-panel .dk-seg > button { background: var(--dk-color-surface-2); }
.dk-card .dk-seg > button, .dk-tile .dk-seg > button { background: var(--dk-color-icon-bg); }
.dk-seg > button[aria-pressed="true"] { background: var(--dk-color-brand); color: var(--dk-color-on-brand); }
```

```css
QPushButton#glowny {{ min-height: {qt_control_h}; padding: 0 {space_6}; background: {color_brand}; color: {color_on_brand};
    border: 1px solid transparent; border-radius: {qt_radius_btn}; font-weight: 700; font-size: {qt_fs_btn}; }}
QPushButton#glowny:hover {{ background: {color_brand_hover}; }}
QPushButton#drugorzedny {{ min-height: {qt_control_h}; padding: 0 {space_6}; background: {color_btn2_bg}; color: {color_btn2_text};
    border: 1px solid {color_btn2_border}; border-radius: {qt_radius_btn}; font-weight: 700; font-size: {qt_fs_btn}; }}
QPushButton#drugorzedny:hover {{ background: {color_btn2_hover_bg}; }}
QPushButton#wyrozniony {{ min-height: {qt_control_h}; padding: 0 {space_6}; background: {color_cta}; color: {color_on_cta};
    border: 1px solid transparent; border-radius: {qt_radius_btn}; font-weight: 700; font-size: {qt_fs_btn}; }}
QPushButton#wyrozniony:hover {{ background: {color_cta_hover}; }}
QPushButton:disabled {{ background: {color_disabled_bg}; color: {color_text_muted}; border-color: transparent; }}
QPushButton:focus {{ border: 2px solid {color_focus}; }}
```

### 25.4 Ikony (S7)

Ikony liniowe (Lucide), kreska 2, zielone (`icon`). Przycisk-ikona kwadratowy 44 px, tło `icon-bg` `#F5F5F5`, promień 4 (kółko tylko: awatar, kropka, gałka, radio).
Podpis pod ikoną: Lato 700, 11 px, wersaliki, `heading-accent`. Ikona cechy w sekcji: 32 px obok tytułu pogrubionego i opisu.

```css
/* ikony: liniowe (Lucide), kreska 2, zieleń marki; przycisk-ikona kwadratowy */
.dk-icon { width: 24px; height: 24px; fill: none; stroke: var(--dk-color-icon); stroke-width: var(--dk-control-stroke-icon);
  stroke-linecap: round; stroke-linejoin: round; flex: none; }
.dk-iconbtn { display: inline-grid; place-items: center; width: var(--dk-control-h-min); height: var(--dk-control-h-min);
  background: var(--dk-color-icon-bg); border: 0; border-radius: var(--dk-radius-btn); cursor: pointer; }
.dk-iconbtn:hover { background: var(--dk-color-brand-soft); }
.dk-iconlabel { display: inline-flex; flex-direction: column; align-items: center; gap: 4px;
  font: 700 11px/1 var(--dk-font-text); text-transform: uppercase; letter-spacing: .03em; color: var(--dk-color-heading-accent); }
.dk-feature { display: flex; gap: var(--dk-space-4); align-items: flex-start; }
.dk-feature .dk-icon { width: 32px; height: 32px; margin-top: 2px; }
.dk-feature b { display: block; font-size: 18px; }
```

```css
QToolButton#ikona {{ min-width: {control_h_min}; min-height: {control_h_min}; background: {color_icon_bg}; border: 0; border-radius: {qt_radius_btn}; }}
QToolButton#ikona:hover {{ background: {color_brand_soft}; }}
QLabel#podpisIkony {{ font-weight: 700; font-size: 11px; color: {color_heading_accent}; }}   /* tekst wpisz wersalikami */
/* SVG ikon: stroke="currentColor" podmień na {color_icon} przy wczytaniu; kreska {control_stroke_icon} */
```

### 25.5 Zakładki i kroki (S10)

Zakładki główne: Mindset, aktywna ciemnozielona, nieaktywna prawie czarna, pod spodem linia 1 px `#222222`. Podzakładki: Lato wersaliki `label`, aktywna z zieloną
kreską 2 px. Kroki: pasek 5 px, aktywny `progress` `#47C33D`, reszta `#E9E9E9`.

```css
/* zakładki: Mindset, aktywna zielona, pod spodem linia 1 px */
.dk-tabs { display: flex; gap: var(--dk-space-10); border-bottom: 1px solid var(--dk-color-text); padding-bottom: var(--dk-space-5); }
.dk-tab { font: 400 20px/1 var(--dk-font-display); text-transform: uppercase; letter-spacing: .01em; color: var(--dk-color-heading);
  background: none; border: 0; padding: 0; cursor: pointer; }
.dk-tab[aria-selected="true"] { color: var(--dk-color-heading-accent); }
/* pod-zakładki: Lato wersaliki, zielona kreska 2 px */
.dk-subtabs { display: flex; border-bottom: 1px solid var(--dk-color-border); }
.dk-subtab { font: 400 13px/1 var(--dk-font-text); text-transform: uppercase; letter-spacing: .02em; color: var(--dk-color-label);
  padding: var(--dk-space-4); margin-bottom: -1px; border-bottom: 2px solid transparent; background: none; border-width: 0 0 2px; cursor: pointer; }
.dk-subtab[aria-selected="true"] { border-bottom-color: var(--dk-color-brand); }

/* kroki: pasek 5 px, aktywny jasnozielony */
.dk-steps { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: 6px; }
.dk-step { text-align: center; padding-bottom: var(--dk-space-3); border-bottom: 5px solid var(--dk-color-switch-off);
  color: var(--dk-color-step-idle-text); font-size: 15px; }
.dk-step[aria-current="step"] { border-bottom-color: var(--dk-color-progress); color: var(--dk-color-text); }
```

```css
QTabBar::tab {{ font-family: "Mindset"; font-size: {qt_fs_app_title}; color: {color_heading}; padding: 0 {space_5} {space_4} 0; background: transparent; border: 0; }}
QTabBar::tab:selected {{ color: {color_heading_accent}; }}
QTabWidget::pane {{ border: 0; border-top: 1px solid {color_text}; }}
/* podzakładki: ta sama QTabBar z objectName "pod": Lato, color_label, wybrana: border-bottom: 2px solid {color_brand} */
QWidget#krok {{ border-bottom: 5px solid {color_switch_off}; color: {color_step_idle_text}; padding-bottom: {space_3}; }}
QWidget#krok[aktywny="true"] {{ border-bottom-color: {color_progress}; color: {color_text}; }}
```

### 25.6 Pola (S9)

Pole białe, obrys 1 px `#868E96`, promień 4; fokus = obrys `brand` + poświata `shadow-focus-field`. Wyszukiwarka: pigułka z zielonym obrysem i zielonym przyciskiem.
Ilość: trzy komórki z ramką `border-strong`, znaki +/- ciemnozielone.

```css
/* pola */
.dk-input { min-height: var(--dk-control-h-min); padding: 0 var(--dk-space-3); background: var(--dk-color-check-bg);
  border: 1px solid var(--dk-color-field-border); border-radius: var(--dk-radius-sm); color: var(--dk-color-text); font: inherit; }
.dk-input:focus { outline: none; border-color: var(--dk-color-brand); box-shadow: var(--dk-shadow-focus-field); }
.dk-search { display: flex; align-items: center; gap: var(--dk-space-3); padding: 4px 4px 4px var(--dk-space-4);
  border: 1px solid var(--dk-color-brand); border-radius: var(--dk-radius-pill); background: var(--dk-color-check-bg); }
.dk-search input { flex: 1; border: 0; outline: 0; background: none; font: inherit; color: var(--dk-color-text); min-width: 0; }
.dk-search .dk-btn { min-height: 34px; border-radius: var(--dk-radius-pill); font-size: 12px; padding: 0 var(--dk-space-5); }
.dk-qty { display: inline-grid; grid-template-columns: 32px 44px 32px; border: 1px solid var(--dk-color-border-strong); border-radius: var(--dk-radius-sm); }
.dk-qty > * { height: var(--dk-control-h-min); display: grid; place-items: center; background: var(--dk-color-check-bg); border: 0; font: inherit; color: var(--dk-color-text); }
.dk-qty > button { cursor: pointer; color: var(--dk-color-heading-accent); font-weight: 700; }
.dk-qty > span { border-inline: 1px solid var(--dk-color-border-strong); font-weight: 700; }
```

```css
QLineEdit, QComboBox, QSpinBox, QTextEdit {{ min-height: 30px; padding: 4px 12px; background: {color_check_bg}; color: {color_text};
    border: 1px solid {color_field_border}; border-radius: {qt_radius_field}; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{ border: 2px solid {color_brand}; padding: 3px 11px; }}
QLineEdit#szukaj {{ border: 1px solid {color_brand}; border-radius: 18px; min-height: 34px; }}
QPushButton#plus, QPushButton#minus {{ min-width: 32px; min-height: {control_h_min}; background: {color_check_bg}; color: {color_heading_accent};
    border: 1px solid {color_border_strong}; font-weight: 700; }}
```

### 25.7 Checkbox i radio (S8, G1)

Wnętrze białe ZAWSZE (także zaznaczone), obrys 1,5 px `#868E96`; hover i zaznaczony: zielony obrys; znak (ptaszek, kropka) zielony. Wyłączony: obrys `#CED4DA`, znak `#ADB5BD`.

```css
/* checkbox / radio: wnętrze białe, znak zielony */
.dk-check, .dk-radio { appearance: none; -webkit-appearance: none; flex: none; margin: 0; display: inline-grid; place-content: center;
  width: var(--dk-control-check-size); height: var(--dk-control-check-size); background: var(--dk-color-check-bg);
  border: var(--dk-control-check-border-width) solid var(--dk-color-check-border); border-radius: var(--dk-control-check-radius);
  color: var(--dk-color-check-mark); cursor: pointer; }
.dk-radio { border-radius: 50%; }
.dk-check::after { content: ""; width: 12px; height: 12px; background: currentColor; transform: scale(0);
  clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%); transition: transform var(--dk-motion-fast) var(--dk-motion-ease); }
.dk-radio::after { content: ""; width: 10px; height: 10px; border-radius: 50%; background: currentColor; transform: scale(0); }
.dk-check:checked::after, .dk-radio:checked::after { transform: scale(1); }
.dk-check:checked, .dk-radio:checked, .dk-check:hover, .dk-radio:hover { border-color: var(--dk-color-check-border-hover); }
.dk-check:focus-visible, .dk-radio:focus-visible { outline: var(--dk-control-focus-width) solid var(--dk-color-focus); outline-offset: var(--dk-control-focus-offset); }
.dk-check:disabled, .dk-radio:disabled { border-color: var(--dk-color-check-disabled-border); color: var(--dk-color-check-disabled-mark); cursor: not-allowed; }
.dk-field { display: inline-flex; align-items: center; gap: var(--dk-space-3); min-height: var(--dk-control-h-min); cursor: pointer; }
```

Qt: ptaszek i kropka radio to obrazek SVG w kolorze `{color_check_mark}` (generator `dk_kontrolki_svg` z rozdz. 24, kolory z ról, więc po przejściu na 2.0.0 są zielone); obrys 1,5 px zapisz jako `2px`.

```css
QCheckBox, QRadioButton {{ color: {color_text}; spacing: 10px; min-height: 28px; }}
QCheckBox::indicator, QRadioButton::indicator {{ width: 16px; height: 16px; background: {color_check_bg};
    border: 2px solid {color_check_border}; border-radius: {qt_radius_field}; }}
QRadioButton::indicator {{ border-radius: 10px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover, QCheckBox::indicator:checked, QRadioButton::indicator:checked {{ border-color: {color_check_border_hover}; }}
QCheckBox::indicator:checked {{ image: url({img_check}); }}
QRadioButton::indicator:checked {{ image: url({img_radio}); }}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{ border-color: {color_check_disabled_border}; }}
```

### 25.8 Przełącznik, suwak, postęp (S8)

Przełącznik: tor wyłączony `#E9E9E9` z obrysem `#868E96`, włączony zielony, gałka biała. Suwak: tor `#E9E9E9`, wypełnienie zielone, uchwyt biały z zielonym obrysem 2 px.
Pasek postępu: `progress` `#47C33D` na torze `#E9E9E9`.

```css
/* przełącznik i suwak */
.dk-switch { position: relative; display: inline-block; width: 48px; height: 28px; flex: none; }
.dk-switch input { appearance: none; -webkit-appearance: none; position: absolute; inset: 0; margin: 0; cursor: pointer; border-radius: var(--dk-radius-pill);
  background: var(--dk-color-switch-off); border: 1px solid var(--dk-color-switch-off-border); }
.dk-switch input:checked { background: var(--dk-color-switch-on); border-color: var(--dk-color-switch-on); }
.dk-switch span { position: absolute; top: 4px; left: 4px; width: 20px; height: 20px; border-radius: 50%; background: var(--dk-color-switch-knob);
  box-shadow: var(--dk-shadow-raised); pointer-events: none; transition: transform var(--dk-motion-fast) var(--dk-motion-ease); }
.dk-switch input:checked + span { transform: translateX(20px); }
.dk-slider { appearance: none; -webkit-appearance: none; width: 220px; height: 6px; border-radius: 3px; cursor: pointer;
  background: linear-gradient(to right, var(--dk-color-slider-fill) var(--v, 50%), var(--dk-color-slider-track) var(--v, 50%)); }
.dk-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%; background: var(--dk-color-slider-thumb);
  border: var(--dk-control-slider-thumb-border-width) solid var(--dk-color-slider-thumb-border); }
.dk-progress { height: 8px; border-radius: 4px; background: var(--dk-color-slider-track); overflow: hidden; }
.dk-progress i { display: block; height: 100%; background: var(--dk-color-progress); }
```

```css
QCheckBox#przelacznik::indicator {{ width: 44px; height: 28px; border-radius: 16px; background: {color_switch_off};
    border: 2px solid {color_switch_off_border}; image: url({img_knob_off}); }}
QCheckBox#przelacznik::indicator:checked {{ background: {color_switch_on}; border-color: {color_switch_on}; image: url({img_knob_on}); }}
QSlider::groove:horizontal {{ height: 6px; background: {color_slider_track}; border-radius: 3px; }}
QSlider::sub-page:horizontal {{ background: {color_slider_fill}; border-radius: 3px; }}
QSlider::handle:horizontal {{ width: 18px; height: 18px; margin: -7px 0; background: {color_slider_thumb};
    border: 2px solid {color_slider_thumb_border}; border-radius: 11px; }}
QProgressBar {{ height: 8px; background: {color_slider_track}; border: 0; border-radius: 4px; text-align: center; }}
QProgressBar::chunk {{ background: {color_progress}; border-radius: 4px; }}
```

### 25.9 Metki i tagi (S11)

Metka pełna (cena, licznik, znaczek): `brand` + biały tekst, promień 4. Tagi kategorii: `tag-N` (od 2.0.0 odcienie zieleni), pigułki (rozdz. 22). Flaga ceny: Mindset 28 px na zielonym
tle ze ściętym lewym rogiem.

```css
/* metki: pełna zielona (cena, licznik) i odcieniowe (kategorie) */
.dk-chip { display: inline-flex; align-items: center; min-height: 28px; padding: 0 var(--dk-space-3); border-radius: var(--dk-radius-sm);
  background: var(--dk-color-brand); color: var(--dk-color-on-brand); font: 700 13px/1 var(--dk-font-text); }
.dk-tag { display: inline-flex; align-items: center; min-height: 26px; padding: 0 var(--dk-space-3); border-radius: var(--dk-radius-pill);
  font: 700 13px/1 var(--dk-font-text); border: 0; }   /* S13: tag bez obrysu */
.dk-price { font: 400 28px/1 var(--dk-font-display); background: var(--dk-color-brand); color: var(--dk-color-on-brand); padding: 10px 16px 10px 24px;
  clip-path: polygon(10px 0, 100% 0, 100% 100%, 10px 100%, 0 50%); display: inline-block; }
```

```css
QLabel#metka {{ background: {color_brand}; color: {color_on_brand}; border-radius: {qt_radius_field}; padding: 4px 10px; font-weight: 700; font-size: 13px; }}
/* tag kategorii k=1..8: funkcja tag_qss(T, k) z rozdz. 22; pigułka: border-radius: 13px */
QLabel#cena {{ background: {color_brand}; color: {color_on_brand}; font-family: "Mindset"; font-size: 28px; padding: 8px 16px 8px 24px; }}
```

### 25.10 Lista, tabela i paski (S10)

Lista z zielonymi kropkami (pogrubione pozycje). Tabela: pasy `zebra` / biel, bez linii pionowych, nagłówek bez tła w kolorze `label`. Pasek górny `heading-accent` z białym tekstem
wersalikami; pasek menu `strip` `#F8F4F1`.

```css
/* lista z zielonymi kropkami, tabela w pasy */
.dk-list { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--dk-space-2); font-weight: 700; }
.dk-list li { display: flex; gap: var(--dk-space-3); align-items: baseline; }
.dk-list li::before { content: ""; width: 9px; height: 9px; border-radius: 50%; background: var(--dk-color-brand); flex: none; }
.dk-table { width: 100%; border-collapse: collapse; font-size: 15px; }
.dk-table th { text-align: left; font-weight: 700; padding: var(--dk-space-3) var(--dk-space-5); color: var(--dk-color-label); }
.dk-table td { padding: var(--dk-space-5); }
.dk-table tbody tr:nth-child(odd) { background: var(--dk-color-zebra); }
.dk-topbar { background: var(--dk-color-heading-accent); color: var(--dk-color-on-brand); font: 700 12px/1 var(--dk-font-text); text-transform: uppercase;
  letter-spacing: .02em; padding: var(--dk-space-3) var(--dk-space-6); }
.dk-strip { background: var(--dk-color-strip); display: flex; gap: var(--dk-space-10); padding: var(--dk-space-4) var(--dk-space-6);
  font: 700 14px/1 var(--dk-font-text); text-transform: uppercase; letter-spacing: .01em; }
```

```css
QTableView {{ background: {color_bg}; alternate-background-color: {color_zebra}; gridline-color: transparent; border: 0; font-size: {qt_fs_body}; }}
QTableView::item {{ padding: {space_5}; border: 0; }}
QHeaderView::section {{ background: transparent; color: {color_label}; font-weight: 700; border: 0; padding: {space_3} {space_5}; }}
QWidget#paskGorny {{ background: {color_heading_accent}; color: {color_on_brand}; font-weight: 700; font-size: 12px; }}
QMenuBar, QWidget#paskMenu {{ background: {color_strip}; color: {color_text}; font-weight: 700; }}
/* kropki listy: QListWidget bez ikon + delegat rysujący kółko 9 px w {color_brand}; tabela: setAlternatingRowColors(True), setShowGrid(False) */
```

**Dostępność.** Kontrasty par sprawdza `build_tokens.py --check` (556 sprawdzeń): zielony `brand` `#007936` na bieli 5,54:1, biały tekst na zieleni 5,54:1, `#222222`
na bieli 15,91:1, `#666666` na bieli 5,74:1, obrys pola `#868E96` na bieli 3,32:1. Stan niesie nie tylko kolor (ptaszek, kropka, podkreślenie linku, pogrubienie aktywnej zakładki).
Cel dotykowy >= 44 px, fokus 2 px `focus`.

**Rób / Nie rób.**
- Rób: panel (L1) → biała karta (L2) → kafel ecru (L3) → beż (L4), w tej kolejności i nie głębiej.
- Rób: jedną zieleń przycisków (`brand`), jeden żółty przycisk wyróżnionej akcji na widok.
- Nie rób: beżowego, ecru ani szarego tła okna; brązowego tekstu w stylach jasnych; ikon-przycisków w kółku; nakładek na L4 (nakładka = `overlay` + cień).
- Nie rób: kolorów na sztywno z tego rozdziału w aplikacji - tylko role. Hexy w opisach to wartości ról w 2.0.0.
