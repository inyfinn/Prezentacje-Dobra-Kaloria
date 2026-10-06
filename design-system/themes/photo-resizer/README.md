> **Stan 2.0.0 (06.10.2026):** ten plik opisuje szkic motywu sprzed 2.0.0. Wartości obowiązujące: `../../tokens/READY-2.0.0.txt` i wygenerowany plik motywu w tym katalogu (białe tło, szary panel, tekst #222222, zieleń #007936).

# Motyw „Dobra Kaloria” w Inyfinn Photo Resizer

Status: **szkic**. Wartości policzone i sprawdzone pod kątem kontrastu, ale motyw nie był jeszcze
wyświetlony w aplikacji. Zanim trafi do wydania, musi przejść pętlę zrzutów (`ui-taste-reflect`).

Plik z wartościami: `dobra_kaloria.py` (generowany, 37 kluczy - dokładnie te, których używa `app.qss`).
Zgodność kluczy z aplikacją sprawdza:

```
python scripts/build_tokens.py --resizer "<repo>\BIN\dev\src\inyfinn_resizer\app\themes\__init__.py"
```

## Jak działa motyw w tej aplikacji

Jeden arkusz `app/themes/app.qss` ze znacznikami `@NAZWA@`. `apply_theme()` podmienia znaczniki wartościami
ze słownika `_THEME_TOKENS[<motyw>]`. Nowy motyw to nowy słownik. Arkusza nie trzeba ruszać.

## Wdrożenie (4 małe zmiany, motywy jasny i ciemny zostają)

1. `app/themes/__init__.py`: dopisz do `_THEME_TOKENS` wpis `"dobra-kaloria": {...}` z zawartością
   `DOBRA_KALORIA` z pliku `dobra_kaloria.py`.
2. `app/themes/__init__.py`, funkcja `apply_theme`: ikony wybieraj warunkiem `theme != "dark"` zamiast
   `theme == "light"`. Inaczej nowy (jasny) motyw dostanie ikony z motywu ciemnego.
3. `app/user_settings.py`, funkcja `load_theme`: dopuść wartość `"dobra-kaloria"`
   (dziś: `theme in ("light", "dark")`, więc zapisany motyw wróciłby do jasnego po restarcie).
4. `app/main_window.py`, menu Narzędzia: dopisz pozycję „Motyw Dobra Kaloria”
   (`self._set_theme("dobra-kaloria")`) obok „Jasny motyw” i „Ciemny motyw”.

Przełącznik `ThemeToggle` ma dwa stany. W motywie Dobra Kaloria pokaże pozycję „jasny”, a kliknięcie
przejdzie na ciemny. Na początek wystarczy; trzeci stan przełącznika to osobna decyzja.

## Czego ten motyw nie zmienia (i dlaczego)

| Element | Stan | Powód |
|---|---|---|
| Czcionka | zostaje Segoe UI 13 px | rozmiar i krój są wpisane w `app.qss`; zmiana wymaga znacznika `@FONT@` i dołączenia plików Lato |
| Główny przycisk | zielony z białym tekstem, nie żółty | kolor tekstu `#ffffff` jest wpisany w arkusz na stałe; żółty wymaga znaczników `@CTA_BG@` i `@CTA_TEXT@` |
| Odstępy | bez zmian | narzędzie jest gęste z założenia; tokeny `card-pad-sm`, `section-gap-sm`, `stack-sm` czekają na drugi etap |

## Drugi etap (osobna decyzja)

- znacznik `@FONT@` w `app.qss` i Lato z `assets/fonts` (`QFontDatabase.addApplicationFont`),
- żółty przycisk głównej akcji (jeden na ekran),
- promienie 4 / 8 / 12 z design systemu.
