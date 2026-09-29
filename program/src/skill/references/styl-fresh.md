> WYCOFANE 28.09.2026: zastąpione przez references/styl-dk.md (build_dk.py). Plamy za produktem i Nunito - user kazał usunąć.

# Styl "fresh" - DOMYŚLNY styl prezentacji DK (od 24.09.2026, zaakceptowany przez usera)

Cel od usera: lżejsze, piękniejsze, "miłe dla oka, naturalne". Zostaje DNA marki (Mindset, zieleń 006400, logo),
znika ciężar (pełne zielone pasy, pędzle na każdym slajdzie).

## Tokeny
| Token | Hex | Rola |
|---|---|---|
| PAPER | FAF6EF | tło (ciepły papier) |
| CARD | F1ECE2 | karty na tle |
| SAGE_50 / 200 / 400 | E7EEDF / C9DABB / 8DB27A | organiczne koła, tło końca, drugorzędne słupki |
| BRAND | 006400 | wyróżnienia, liczba-bohater, zwycięzca |
| INK | 1F3A24 | tytuły i tekst (kontrast ~11:1) |
| MUTED | 5B6B5C | opisy, stopki (kontrast ~5,4:1 - AA) |
| accent (spec) | np. D6232A | kolor produktu z opakowania - TYLKO kropka kickera i pigułka na okładce |

## Typografia
- **Mindset** - tytuły (40), duże liczby (50-150). Nigdy do akapitów.
- **Nunito Sans** (Regular / SemiBold / ExtraBold) - tekst, etykiety, kicker (ExtraBold 12 pt, rozstrzelony, wersaliki).
- Minimum: opisy 13,5 pt, stopka 10,5 pt; tekst na kartach 15-16 pt.
- Osadzanie: `render.ps1 -EmbedFonts` (statyczne pliki Nunito Sans z `assets/fonts` - wariable Nunito osadza się źle).

## Zasady
1. Dużo powietrza: margines 1,9 cm, max 4 karty w rzędzie, 1 liczba-bohater na slajd.
2. Motyw organiczny: miękkie **kształty organiczne** (`blob()` - zamknięta krzywa Béziera przez lekko odkształcony
   okrąg, `seed` = powtarzalny kształt) w szałwii za packshotami, 1-2 dekoracyjne na okładce/końcu. Idealne koła tylko
   jako małe kropki (kicker, numer karty). Bez pędzli.
7. Rytm: przed dłuższym rozdziałem (np. badanie) slajd `section` na zieleni BRAND - jedyny ciemny slajd w środku decku.
8. Łamanie tekstu: Nunito łamiemy sami na spacjach (`txt()` robi to automatycznie) - PowerPoint łamie też na łącznikach
   ("słodko-|kwaśne"), a fonty nie mają twardego łącznika U+2011. Po renderze sprawdź sieroty (jedno słowo w linii).
3. Karty zaokrąglone, bez obramowań i cieni; wyróżnienie = biała karta + zielona linia 2,25 pt + pigułka-etykieta.
4. Rama slajdu: kicker (kropka akcentu + etykieta) -> tytuł Mindset -> treść; małe logo (zielona ramka) prawy górny róg;
   stopka ze źródłem po lewej, numer strony po prawej.
5. Wykresy: słupki zaokrąglone na torze SAGE_50, etykieta NAD słupkiem, wartość na końcu (bez osi i legendy);
   wyróżnione = BRAND, reszta = SAGE_400.
6. Packshot: cień brązowy 3B2A20 (softEdge) + koło SAGE_50 pod spodem; lekki obrót (-4..+5°).

## Typy slajdów (`build_fresh.py`)
cover, section (slajd przejścia rozdziału), features (2x2 claimy), hero_stat (liczba-bohater + karty), segments (2 grupy × 2-4 wyniki), compare (warianty,
zwycięzca z pigułką), split (A vs B jednym paskiem + grupy), bars, reasons (4 karty argumentów), skus (smaki + EAN), end.
