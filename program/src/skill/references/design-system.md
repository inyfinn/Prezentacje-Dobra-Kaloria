# Design system - styl "szablon" (DK_WZÓR_PREZENTACJI_01)

Źródła analizy (24.09.2026, `D:\Marketing\- POLSKA\09 - PREZENTACJE\— SZABLON\`):
`DK_WZÓR_PREZENTACJI_01 (1) 3.pptx` (wzór) + gotowe: `DK_CYNAMONKA I ŚLIWKA 1`, `DK_KREMY`, `DK_KULKI TIRAMISU BANOFFEE`,
oraz raport `DOBRA KALORIA - DATESY.pptx` (folder wyżej).

## Format
16:9, 33,867 × 19,05 cm (12192000 × 6858000 EMU). Wszystkie slajdy na układzie "Slajd tytułowy", treść ręcznie (bez placeholderów).

## Kolory
| Token | Hex | Użycie |
|---|---|---|
| CREAM | FCF3E9 | tło slajdów treści i prawej połowy okładki |
| GREEN | 006400 | zielone pasy/panele, tło slajdu końcowego, tekst punktów we wzorze |
| TEXT_GREEN | 005900 | tekst w prezentacjach produktowych (tytuły okładki, punkty) |
| DARK_GREEN | 084C1D | tytuł okładki we wzorze |
| LIGHT_GREEN | 11953B | podtytuł, strzałki, drugi kolor linii w raporcie |
| DOT_GREEN | 009114 | kropki punktów we wzorze |
| SHADOW | 461600 | cień pod packshotem (owal, softEdge 10 pt); 311D22 pod pudełkami |
| biały | FFFFFF | tytuł w pędzlu, tekst na zielonym |

## Typografia
- **Mindset** (PintassilgoPrints) - wszystko; krój wersalikowy (wpisany mały tekst i tak renderuje się wersalikami).
- **Mindset Slim** - "#" w #zawszedobra, akcent w strzałkach, drobny opis w raporcie.
- Fonty są OSADZONE we wzorze -> budując z `assets/DK_WZOR.pptx` prezentacja działa bez instalacji fontów.
- Rozmiary: okładka wzór 115/48/44; okładka produktowa "NOWOŚĆ" 75, nazwa 54-60, smaki 28 (albo 50 gdy krótko);
  tytuł w pędzlu 40-44 (biały); punkty 24 pt, interlinia 35 pt, kropka Arial 150% w kolorze tekstu; punkty wzoru 32 pt.

## Slajdy (anatomia)
1. **Okładka**: lewa zielona połowa (wzór 5,95 M EMU; produktowe 6,25 M) z logo (biała ramka) na środku;
   prawa kremowa: stos napisów wyśrodkowany + krótkie pociągnięcie pędzla (EMF) pod spodem.
2. **Slajd treści**: zielony pas 1,2 M EMU po lewej z małym logo u góry; tytuł w zielonym pędzlu (EMF) u góry;
   lewa kolumna: punkty; prawa połowa: packshoty.
3. **Packshoty**: PNG bez tła, lekko obrócone (±4-10°), nachodzące na siebie (kaskada / trójkąt), mogą wychodzić poza kadr
   u dołu/prawej; pod każdym miękki brązowy owal (cień). Rekwizyty smaku (owoce, cynamon, kawałki produktu) rozrzucone
   wokół - różne dla każdego produktu (to jest "osobne podejście do każdego produktu").
4. Wzór pokazuje też: strzałki 11953B + tekst 36 pt (Mindset / Mindset Slim) oraz ozdobniki do wybijania ważnych
   informacji: baner-strzałka, baner zaokrąglony, ramka, dymek duży i mały, "Polska firma rodzinna" z mapką.
5. **Koniec**: tło 006400, duże logo, "#zawszedobra" (# w Mindset Slim) białe 48 pt.

Raport kampanii (DATESY): okładka z logo w panelu + lista tytułów naprzemiennie 005900/11953B; slajdy z siatką zrzutów
telefonów i drobnym opisem (Mindset Slim) obok -> `gallery` w builderze.

## Mapowanie na builder (`build_deck.py`)
cover (variant product | template), product, bullets, arrows, stats, compare, bars, gallery, free, end.
Elementy klonowane ze wzoru (nie rysowane od nowa): pasy, logo, pędzel tytułu, pędzel pod okładką, ramka "box"
(pod dużymi liczbami), ozdobniki `callouts`.
