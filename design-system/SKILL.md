---
name: ds-dobra-kaloria
description: Design system Dobra Kaloria - tokeny (kolory, odstępy, czcionki, promienie, cienie), komponenty i motywy dla narzędzi marki. Użyj, gdy budujesz lub poprawiasz interfejs w stylu Dobra Kaloria (program "Stwórz prezentację"), dodajesz motyw "Dobra Kaloria" do istniejącej aplikacji (Inyfinn Photo Resizer, DAM) albo zmieniasz kolor, odstęp lub czcionkę marki.
---

# Design system Dobra Kaloria

Najpierw przeczytaj `DESIGN_SYSTEM.md` (zasady, tryby odstępów, platformy). Wartości: `tokens/tokens.md`.
Komponenty: `components.md`, galeria `preview/index.html`.

## Twarde reguły

1. Wartości zmieniasz tylko w `tokens/tokens.json`. `tokens.css`, `tokens_qt.py`, `tokens.md` i pliki
   w `themes/` są generowane - nie edytuj ich ręcznie.
2. W komponentach używasz ról (`--dk-color-text`), nie prymitywów (`--dk-brown-900`) i nie wartości
   wpisanych na sztywno.
3. Tekst nigdy nie jest czarny. Żółty przycisk jest jeden na ekran.
4. Motyw w cudzej aplikacji to nakładka na jej zmienne. Nie przepisujesz komponentów i nie usuwasz
   dotychczasowych motywów.
5. Repo Photo Resizera i DAM mają własne sesje i własne zasady. Z tego skilla dostarczasz plik motywu
   i instrukcję; zmiany w tamtych repo robi się tam, po decyzji usera.
6. Każda widoczna zmiana kończy się zrzutem ekranu otwartym narzędziem Read (`ui-taste-reflect`).

## Najczęstsze zadania

| Zadanie | Kroki |
|---|---|
| Zmiana koloru, odstępu, promienia | `tokens.json` -> `python scripts/build_tokens.py` -> podbij `meta.version` -> odśwież aplikacje (DESIGN_SYSTEM.md, sekcja 8) |
| Nowy ekran lub komponent w stylu DK | wczytaj `tokens.css`, wybierz tryb odstępów (wygodny albo zwarty), komponenty z `components.md` |
| Motyw DK w Photo Resizerze | `themes/photo-resizer/README.md` |
| Motyw DK w DAM | `themes/dam/README.md` |
| Sprawdzenie kontrastu | `python scripts/build_tokens.py --check` |
| Czy motyw Photo Resizera ma komplet kluczy | `python scripts/build_tokens.py --resizer "<ścieżka do app/themes/__init__.py>"` |

## Pliki

```text
DESIGN_SYSTEM.md            zasady, tryby odstępów, platformy, wersjonowanie, otwarte decyzje
components.md               komponenty: warianty, stany, dostępność
tokens/tokens.json          JEDYNE źródło wartości
tokens/tokens.css           web: zmienne --dk-* (generowany)
tokens/tokens_qt.py         Qt: słownik T do szablonu QSS (generowany)
tokens/tokens.md            tabele wartości i kontrastu (generowany)
themes/photo-resizer/       słownik motywu + instrukcja wdrożenia
themes/dam/                 nakładka CSS na --dam-* + instrukcja wdrożenia
scripts/build_tokens.py     generator i kontrola kontrastu
assets/fonts, assets/*.png  Mindset, Lato, logo
preview/                    galeria komponentów i zrzuty
```
