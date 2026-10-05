---
name: ds-dobra-kaloria
description: Identyfikacja wizualna i design system Dobra Kaloria - jeden język wizualny narzędzi marki (tokeny, drabina powierzchni L0-L4, tagi, komponenty web i Qt, typografia Mindset/Lato, ikony, plansza startowa, ikona aplikacji). Użyj ZAWSZE, gdy user prosi "zrób w stylu Dobra Kaloria", buduje lub poprawia interfejs marki (program "Stwórz prezentację", Inyfinn Photo Resizer, DAM, nowa aplikacja), dodaje motyw Dobra Kaloria albo zmienia kolor, odstęp, czcionkę, tło, tagi marki.
---

# Identyfikacja wizualna i design system Dobra Kaloria

**Najpierw przeczytaj `IDENTYFIKACJA-WIZUALNA.md`** - jak zrobić dowolny ekran albo aplikację w tym stylu, krok po kroku
(warianty, drabina L0-L4 i liczenie zagnieżdżeń, komponenty web + Qt, tagi, typografia, ikony, plansza startowa, ikona).
Potem, w miarę potrzeby: `DESIGN_SYSTEM.md` (zasady, wersjonowanie), `components.md` (przepisy komponentów),
`tokens/tokens.md` (wartości i kontrasty), `ZALECENIA-USERA.md` (decyzje usera, dosłownie).

## Twarde reguły

1. Wartości zmieniasz tylko w `tokens/tokens.json`. `tokens.css`, `tokens_qt.py`, `tokens.md` i pliki w `themes/`
   są generowane (`python scripts/build_tokens.py`) - nie edytuj ich ręcznie.
2. W komponentach używasz ról (`--dk-color-text`, `--dk-color-surface-2`), nie prymitywów i nie wartości na sztywno.
3. Każde tło z drabiny według głębokości zagnieżdżenia (poziom = rodzic + 1). Bez czystej bieli w stylach DK
   (wyjątek: L0 programu). Tagi tylko z generatora (odcień stylu), nigdy stałe barwy.
4. Tekst nigdy nie jest czarny. Żółty przycisk jest jeden na ekran. Nagłówki Mindset wersalikami, tekst Lato.
5. Motyw w cudzej aplikacji to nakładka na jej zmienne. Nie przepisujesz komponentów i nie usuwasz dotychczasowych motywów.
6. Repo Photo Resizera i DAM mają własne sesje i własne zasady. Z tego skilla dostarczasz tokeny, motyw i instrukcję.
7. Każda widoczna zmiana kończy się zrzutem ekranu otwartym narzędziem Read (`ui-taste-reflect`).

## Najczęstsze zadania

| Zadanie | Kroki |
|---|---|
| Nowy ekran / nowa aplikacja w stylu DK | `IDENTYFIKACJA-WIZUALNA.md`, rozdz. 10 |
| Zmiana koloru, odstępu, promienia, drabiny, tagów | `tokens.json` -> `python scripts/build_tokens.py` -> podbij `meta.version` -> odśwież aplikacje (DESIGN_SYSTEM.md 8) |
| Podgląd drabiny i tagów, zrzuty | `python scripts/zrzuty_drabiny.py` -> `preview/shots/50-*.png`, `51-tagi.png` |
| Wartości drabiny w konsoli | `python scripts/build_tokens.py --ladder` |
| Sprawdzenie kontrastu i drabiny | `python scripts/build_tokens.py --check` (288 sprawdzeń) |
| Skala tekstu i odstępy Qt (z programu) | `components.md` sekcja 23, tokeny `qt.*` (od 1.5.0) |
| Ikona nowej aplikacji | wpis w `APPS`, `python scripts/ikony_aplikacji.py` |
| Motyw DK w Photo Resizerze / DAM | `themes/photo-resizer/README.md`, `themes/dam/README.md` (szkice 1.2; 1.4.0: `T_*` / `VARIANTS` z `tokens_qt.py`, `data-theme` z `tokens.css`) |
| Czy motyw Photo Resizera ma komplet kluczy | `python scripts/build_tokens.py --resizer "<ścieżka do app/themes/__init__.py>"` |

## Pliki

```text
IDENTYFIKACJA-WIZUALNA.md   START: jeden język wizualny, krok po kroku, zrzuty trzech aplikacji
ZALECENIA-USERA.md          decyzje usera (30.09.2026), dosłownie + reguły
DESIGN_SYSTEM.md            zasady, style x tryby (5a), drabina (5b), tagi (5c), wersjonowanie, otwarte decyzje
components.md               komponenty: warianty, stany, dostępność; 21 drabina, 22 tagi (web + Qt)
tokens/tokens.json          JEDYNE źródło wartości (sekcje color, ladder, tags, ...)
tokens/tokens.css           web: zmienne --dk-* na :root i [data-theme] (generowany)
tokens/tokens_qt.py         Qt: T, T_KREM_JASNY, T_ZIELEN_JASNY, T_DARK, T_KREM, VARIANTS (generowany)
tokens/tokens.md            tabele wartości, drabiny, tagów i kontrastu (generowany)
tokens/READY-1.5.0.txt      znacznik gotowości tokenów dla agentów Resizera i DAM (1.5.0: jasne = biała kartka programu)
themes/photo-resizer/       słownik motywu + instrukcja wdrożenia
themes/dam/                 nakładka CSS na --dam-* + instrukcja wdrożenia
scripts/build_tokens.py     generator (OKLCH: drabina, tagi) i kontrola
scripts/zrzuty_drabiny.py   zrzuty preview/drabina.html
scripts/ikony_aplikacji.py  ikony aplikacji (liść + litery Mindset)
assets/fonts, assets/*.png  Mindset, Lato, logo; assets/icons ikony aplikacji
preview/                    galeria komponentów (index.html), drabina (drabina.html), zrzuty
```
