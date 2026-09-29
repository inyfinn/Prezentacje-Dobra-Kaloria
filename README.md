# Prezentacje - Dobra Kaloria

Program „Stwórz prezentację”: wskazujesz folder produktu, dostajesz gotowy plik PowerPoint w stylu marki
Dobra Kaloria. Bez instalacji.

## Pobierz i uruchom (Windows)

1. Wejdź w [Releases](../../releases/latest) i pobierz plik `Stworz-prezentacje-...-Windows.zip`.
2. Rozpakuj go w dowolnym miejscu na dysku.
3. Uruchom `Stwórz prezentację.exe`.
4. Przeciągnij do okna folder produktu, wybierz styl i kliknij „Stwórz prezentację”.

Przy pierwszym uruchomieniu Windows może pokazać ostrzeżenie o nieznanym wydawcy. Wybierz „Więcej informacji”,
potem „Uruchom mimo to”.

Program sam sprawdza, czy jest nowsze wydanie, i pokazuje przycisk „Zaktualizuj”.
Kopia stojąca na dysku wspólnym nie aktualizuje się sama, wgrywa ją opiekun.

Do kontroli tekstu i osadzenia czcionek program używa PowerPointa. Bez niego prezentacja też powstanie,
ale bez tej kontroli.

## Co powinno być w folderze produktu

| Co | Format |
|---|---|
| Karty wprowadzenia | pliki xlsx, jeden na smak |
| Copy | plik docx |
| Wizualizacje i Elementy | zdjęcia opakowań i owoców, png |
| Badanie (opcjonalnie) | plik xlsx |

## Mac

Okno programu działa tylko w Windows. Na Macu prezentację robi AI według instrukcji:

1. Pobierz repozytorium (zielony przycisk „Code”, potem „Download ZIP”).
2. Otwórz folder w Claude (tryb Cowork albo Code), ChatGPT lub Gemini.
3. Napisz: „Przeczytaj `dla-uzytkownika/AGENTS.md` i zrób prezentację z folderu <ścieżka>”.

Silnik to skrypty Pythona w `program/src/skill/scripts` (`python-pptx`, `Pillow`, `openpyxl`).
Ta ścieżka nie była testowana na Macu. Kontrola w PowerPoint (`verify.ps1`, `render.ps1`) działa tylko w Windows.

## Dokończenie tekstów z AI

Na ekranie „Gotowe” kliknij Claude, ChatGPT albo Gemini. Program kopiuje polecenie z treścią slajdów
i ścieżkami do plików, a potem otwiera czat. Wklejasz (Ctrl+V) i naciskasz Enter.
Najlepiej działa aplikacja Claude na komputerze w trybie Cowork albo Code, bo widzi pliki.

## Co jest w repozytorium

| Folder | Zawartość |
|---|---|
| `program/src/app` | logika programu (Python): analiza folderu, układ slajdów, okno, aktualizacja |
| `program/src/ui` | wygląd okna (HTML, CSS, JS) |
| `program/src/skill` | silnik prezentacji: generatory PPTX, kontrola tekstu, zasady stylu |
| `program/src/launcher` | plik startowy (C#) |
| `program/testy` | testy uruchomienia i pełnego przejścia w prawdziwym oknie |
| `design-system` | design system Dobra Kaloria: tokeny, komponenty, galeria, motywy dla innych aplikacji |
| `dla-uzytkownika` | instrukcje dla ludzi i dla AI, szablon prezentacji |

## Design system

`design-system/DESIGN_SYSTEM.md` opisuje zasady, a `design-system/tokens/tokens.json` jest jedynym źródłem
wartości (kolory, odstępy, czcionki). Z niego generowane są pliki dla stron (`tokens.css`), aplikacji Qt
(`tokens_qt.py`) i motywy dla Inyfinn Photo Resizer oraz DAM. Galeria komponentów: `design-system/preview/index.html`.

## Budowa ze źródeł (Windows)

Wymagania: Python 3.12, `pyinstaller`, `pywebview`, `python-pptx`, `Pillow`, `openpyxl`, PowerPoint.

```powershell
program\build.ps1 -Bump     # buduje program, podbija wersję
program\repo.ps1 -Zip       # pakuje wydanie
```

Skrypty zakładają układ folderów z dysku roboczego (`WORK\` obok `pliki programu\`).

## Wersje

Licznik dziesiętny: po 1.0.9 jest 1.1.0. Wydanie ma znacznik `v<wersja>` i jeden plik zip dla Windows.
