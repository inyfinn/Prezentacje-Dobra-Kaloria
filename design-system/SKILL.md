---
name: ds-dobra-kaloria
description: Identyfikacja wizualna i design system Dobra Kaloria (wzorzec: sklep dobrakaloria.pl) - jeden język wizualny narzędzi marki (tokeny, drabina powierzchni L0-L4: biel, panel, biała karta, kafel ecru; tagi, komponenty web i Qt, typografia Mindset/Lato, ikony, plansza startowa, ikona aplikacji). Użyj ZAWSZE, gdy user prosi "zrób w stylu Dobra Kaloria", buduje lub poprawia interfejs marki (program "Stwórz prezentację", Inyfinn Photo Resizer, DAM, nowa aplikacja), dodaje motyw Dobra Kaloria albo zmienia kolor, odstęp, czcionkę, tło, tagi marki.
---

# Identyfikacja wizualna i design system Dobra Kaloria (2.0.0 „sklep”)

**Najpierw przeczytaj `IDENTYFIKACJA-WIZUALNA.md`** - jak zrobić dowolny ekran albo aplikację w tym stylu, krok po kroku
(warianty, drabina L0-L4 i liczenie zagnieżdżeń, komponenty web + Qt, tagi, typografia, ikony, plansza startowa, ikona).
Potem, w miarę potrzeby: `tokens/READY-2.0.0.txt` (kontrakt 2.0: style, drabina, role, reguły S1-S12), `DOWODY-SKLEP.md`
(pomiary ze zrzutów sklepu), `DESIGN_SYSTEM.md` (zasady, wersjonowanie), `components.md` (przepisy; rozdz. 25 = przepisy 2.0),
`tokens/tokens.md` (wartości i kontrasty), `ZALECENIA-USERA.md` (decyzje usera, dosłownie).

Wygląd 2.0.0 = sklep dobrakaloria.pl odtworzony ze zrzutów usera (06.10.2026). Słowa usera: `RUNDA-4-SKLEP-2026-10-06.md`.
Wzorzec do porównania: `preview/sklep.html` (zrzuty `preview/shots/70-sklep-*.png`, `71-sklep-*.png`).

## Twarde reguły

1. Wartości zmieniasz tylko w `tokens/tokens.json`. `tokens.css`, `tokens_qt.py`, `tokens.md` i pliki w `themes/`
   są generowane (`python scripts/build_tokens.py`) - nie edytuj ich ręcznie.
2. W komponentach używasz ról (`--dk-color-text`, `--dk-color-surface-2`), nie prymitywów i nie wartości na sztywno.
3. **Okno jest BIAŁE (L0 `#FFFFFF`), bieli jest najwięcej.** Sekcja = panel L1 (jasnoszary ciepły) bez obrysu i cienia;
   w panelu leżą BIAŁE karty i pola (L2); ecru i beż dopiero jako kolejny poziom kafla (L3 w karcie, L4 w kaflu).
   Beż, ecru ani szary nigdy jako tło okna. Biała karta wprost na białym tle: linia 1 px `border`. Każde tło z drabiny
   według głębokości (poziom = rodzic + 1); L2 jest JAŚNIEJSZY od L1. Nakładki (menu, lista, podpowiedź, modal) = rola
   `overlay` + cień, nie L4. Tagi tylko z generatora (odcień stylu), nigdy stałe barwy.
4. **Tekst i tytuły prawie czarne (`#222222`), pomocniczy `#666666`; brąz nie jest kolorem tekstu w stylach jasnych.**
   Mindset wersalikami: tytuł główny, nadtytuł, aktywna zakładka i podpis ikony ciemnozielone (`heading-accent`),
   tytuły kart, sekcji i nazw prawie czarne (`heading`). Tekst Lato. Linki w treści pogrubione i podkreślone.
5. Motyw w cudzej aplikacji to nakładka na jej zmienne. Nie przepisujesz komponentów i nie usuwasz dotychczasowych motywów.
6. Repo Photo Resizera i DAM mają własne sesje i własne zasady. Z tego skilla dostarczasz tokeny, motyw i instrukcję.
7. Każda widoczna zmiana kończy się zrzutem ekranu otwartym narzędziem Read (`ui-taste-reflect`).
8. **Zieleń marki (`brand` `#007936`) to akcent interfejsu** (od 2.0.0; zasada „zero zieleni” z 1.6.0 UCHYLONA): przycisk
   główny pełny zielony z białym tekstem, ikony liniowe, kropki list, metki, aktywna zakładka, fokus, znak checkboxa,
   suwak, przełącznik, pasek postępu (`progress` `#47C33D`). **Żółty (`cta`) = jedna wyróżniona akcja widoku**, tekst
   `#222222` („Wybierz folder” zostaje żółty). Przycisk drugorzędny: biały, obrys 1 px `#222222`. **Checkbox i radio:
   wnętrze BIAŁE zawsze**, obrys `#868E96`, zaznaczony = zielony obrys i zielony znak. Kółko tylko: awatar, kropka, gałka, radio.
   Style ciemne zostają bez zmian (brak dowodu ze sklepu). `--check` pilnuje: biały L0, biały L2, neutralny tekst, zielony akcent.

## Najczęstsze zadania

| Zadanie | Kroki |
|---|---|
| Nowy ekran / nowa aplikacja w stylu DK | `IDENTYFIKACJA-WIZUALNA.md`, rozdz. 10; przepisy komponentów `components.md` rozdz. 25 |
| Zmiana koloru, odstępu, promienia, drabiny, tagów | `tokens.json` -> `python scripts/build_tokens.py` -> podbij `meta.version` -> odśwież aplikacje (DESIGN_SYSTEM.md 8) |
| Podgląd drabiny i tagów, zrzuty | `python scripts/zrzuty_drabiny.py` -> `preview/shots/50-*.png`, `51-tagi.png` |
| Zrzuty wzorca „sklep” | `python scripts/zrzuty_sklep.py` -> `preview/shots/70-sklep-*.png`, `71-sklep-*.png` (strona `preview/sklep.html`) |
| Wartości drabiny w konsoli | `python scripts/build_tokens.py --ladder` |
| Sprawdzenie kontrastu, drabiny i reguł 2.0 | `python scripts/build_tokens.py --check` (556 sprawdzeń, błędów: 0; pilnuje: biały L0, biały L2, neutralny tekst, zielony akcent) |
| Checkbox / radio / suwak / przełącznik / przycisk drugorzędny / krokomierz / kółko ikony | `components.md` rozdz. 25 (przepisy 2.0, web CSS + Qt QSS); rozdz. 24 to wersja 1.6.0 (kolory nieaktualne) |
| Skala tekstu i odstępy Qt (z programu) | `components.md` sekcja 23, tokeny `qt.*` (od 1.5.0) |
| Ikona nowej aplikacji | wpis w `APPS`, `python scripts/ikony_aplikacji.py` |
| Motyw DK w Photo Resizerze / DAM | `themes/photo-resizer/README.md`, `themes/dam/README.md` (szkice 1.2; `T_*` / `VARIANTS` z `tokens_qt.py`, `data-theme` z `tokens.css`) |
| Czy motyw Photo Resizera ma komplet kluczy | `python scripts/build_tokens.py --resizer "<ścieżka do app/themes/__init__.py>"` |

## Pliki

```text
DESIGN-SYSTEM-DOBRA-KALORIA.md  JEDEN PLIK dla usera i innych agentów (07.10): skąd wiadomo, czym jest DS (źródła prawdy), zasady S1-S18,
                            tokeny 2.0.7, komponenty, cztery aplikacje, otwarte sprawy. Opis, nie źródło wartości (źródłem jest tokens.json)
IDENTYFIKACJA-WIZUALNA.md   START: jeden język wizualny, krok po kroku, zrzuty trzech aplikacji
DOWODY-SKLEP.md             pomiary ze zrzutów sklepu (tabele element / wartość / rola), wzorce, świadome odstępstwa
RUNDA-4-SKLEP-2026-10-06.md słowa usera dosłownie i zakres rundy 4 (2.0.0); NADPISUJE kolory rundy 3
ZALECENIA-USERA.md          decyzje usera (30.09-06.10.2026), dosłownie + reguły; wpisy uchylone są oznaczone
DESIGN_SYSTEM.md            zasady, style x tryby (5a), drabina (5b), tagi (5c), reguły 2.0 (5f), wersjonowanie, otwarte decyzje
components.md               komponenty: warianty, stany, dostępność; 21 drabina, 22 tagi, 24 kontrolki 1.6.0, 25 PRZEPISY 2.0 (web + Qt)
tokens/tokens.json          JEDYNE źródło wartości (sekcje color, ladder, tags, ...)
tokens/tokens.css           web: zmienne --dk-* na :root i [data-theme] (generowany)
tokens/tokens_qt.py         Qt: T, T_KREM_JASNY, T_ZIELEN_JASNY, T_DARK, T_KREM, VARIANTS (generowany)
tokens/tokens.md            tabele wartości, drabin, tagów i kontrastu (generowany)
tokens/READY-2.0.0.txt      kontrakt 2.0.0: style, drabina, role, kształt, reguły S1-S12, świadome odstępstwa (556 sprawdzeń, 0 błędów)
tokens/tokens-1.6.0.json    kopia zapasowa tokenów sprzed 2.0.0 (powrót: skopiuj z powrotem jako tokens.json i przebuduj)
tokens/READY-1.6.0.txt      znacznik 1.6.0 (runda 3; kolory UCHYLONE przez 2.0.0); READY-1.5.0.txt, READY-1.4.0.txt starsze
RUNDA-3-2026-10-06.md       specyfikacja rundy 3 (G1-G9); część kolorystyczna (G2-G6) UCHYLONA przez rundę 4
themes/photo-resizer/       słownik motywu + instrukcja wdrożenia
themes/dam/                 nakładka CSS na --dam-* + instrukcja wdrożenia
scripts/build_tokens.py     generator (drabina jawna dla jasnych, OKLCH dla ciemnych, tagi) i kontrola
scripts/zrzuty_drabiny.py   zrzuty preview/drabina.html
scripts/zrzuty_sklep.py     zrzuty preview/sklep.html (70-sklep-*, 71-sklep-*)
scripts/migrate_2_0_0.py    JEDNORAZOWA migracja tokens.json 1.6.0 -> 2.0.0 (już wykonana, nie uruchamiaj ponownie)
scripts/ikony_aplikacji.py  ikony aplikacji (liść + litery Mindset)
assets/fonts, assets/*.png  Mindset, Lato, logo; assets/icons ikony aplikacji
assets/sklep-2026-10-06/    7 zrzutów sklepu od usera (sklep-20..26.png) = jedyne dowody wyglądu 2.0
preview/                    sklep.html (wzorzec 2.0), drabina.html (drabina), index.html i kontrolki.html (galerie SPRZED 2.0.0, kolory nieaktualne), zrzuty shots/
```
