# Dowody: sklep dobrakaloria.pl (06.10.2026) — źródło wyglądu DS 2.0.0

Siedem zrzutów od usera: `assets/sklep-2026-10-06/sklep-20.png` ... `sklep-26.png`. Kolory próbkowane pikselami
(wartość z płaskiej powierzchni elementu, nie z krawędzi z wygładzaniem). Słowa usera: `RUNDA-4-SKLEP-2026-10-06.md`.
Kontrakt wynikający z pomiarów: `tokens/READY-2.0.0.txt`. Wzorzec do porównania: `preview/sklep.html`
(zrzuty `preview/shots/70-sklep-*.png`, `71-sklep-*.png`). Przepisy: `components.md` rozdz. 25.

Kolumna „token / rola w 2.0”: tak system nazywa dany kolor. Gdy sklep ma kolor bliski, ale nie ten sam, wpisana jest
rola, a różnica jest w „Świadomych odstępstwach” na końcu.

## sklep-20.png — strona główna

Pasek menu, baner, tytuł sekcji, siatka kafli kategorii na białym tle.

| Element | Zmierzona wartość | Token / rola w 2.0 |
|---|---|---|
| tło strony | `#FFFFFF` | `bg` = L0 |
| pasek menu | `#F8F4F1`, tekst `#000000` wersalikami | `strip`, tekst menu |
| kafle kategorii | `#FDF8EC`, promień ok. 8 px | L3 (ecru), `radius-md` |
| podpisy kafli | Mindset `#333333` | `label` |
| tytuł H1 | Mindset `#222222` | `heading` |
| tekst | `#222222` | `text` |
| przycisk w banerze | `#63B32E` | brak roli (grafika banera, nie interfejs) |
| odznaka „%” | `#008142` | grafika, bliska `brand` |

## sklep-21.png — karta produktu

Zielony pasek górny, logo, wyszukiwarka-pigułka, ikony nagłówka, okruszki, tytuł, metka ceny, przycisk „DO KOSZYKA”.

| Element | Zmierzona wartość | Token / rola w 2.0 |
|---|---|---|
| pasek górny | `#00642E`, biały tekst wersalikami | `heading-accent` jako tło paska |
| logo | `#00642E` | plik logo (nie przebarwiane) |
| „OFICJALNY SKLEP PRODUCENTA” | Mindset `#00642E` | `heading-accent` |
| obrys wyszukiwarki | `#007936` (wygładzone `#19A557`) | `brand`, `radius-pill` |
| przycisk „SZUKAJ” | `#007936`, pigułka | `brand`, `radius-pill` |
| ikony nagłówka (linia) | `#007935`, podpisy `#00642E` | `icon`, podpis `heading-accent` |
| licznik na koszyku | `#007936` | `brand` (metka pełna) |
| okruszki | `#000000`, ostatni `#6C757D` | `text`, kolor pomocniczy |
| linie podziału | `#DEDEDE` | `border` (`#DDDDDD`) |
| tytuł produktu | Mindset `#222222` | `heading` |
| flaga ceny | `#08743A`, biały tekst | metka pełna: `brand` |
| „DO KOSZYKA” | `#0F763E`, promień ok. 5 px, 175 × 48 px | przycisk główny: `brand`, promień 4 |
| znaki +/- ilości | `#00642E` | `heading-accent` |
| kropki listy | `#11753F` | `brand` |
| ikony cech | ok. `#057539`, podpisy Mindset `#0E763B` | `icon`, `heading-accent` |
| ramka miniatury | `#EBEBEB` | `border` |
| licznik zdjęć „1/2” | `#0E773E`, promień ok. 5 px | metka pełna: `brand`, promień 4 |

## sklep-22.png — zakładki, tabela, przyciski „Sprawdź”

| Element | Zmierzona wartość | Token / rola w 2.0 |
|---|---|---|
| przyciski „Sprawdź” | `#097038`, promień ok. 5 px, 116 × 37 px | przycisk główny: `brand` |
| aktywna zakładka | Mindset `#097038` | `heading-accent` |
| zakładka nieaktywna | `#000000` | `heading` |
| linia pod zakładkami | 1 px `#222222` | `text` (reguła S10) |
| nagłówki H2 | Mindset `#222222` | `heading` |
| tekst, pogrubienia, linki | `#222222`; linki pogrubione i podkreślone | `text`, reguła S12 |
| nagłówek tabeli | `#333333` | `label` |
| pasy tabeli | `#F6F2EF` / `#FFFFFF`, bez linii pionowych | `zebra` / `bg` |
| ikony ilustracyjne | ok. `#0B7A3C` | `icon` |

## sklep-23.png — przyklejony pasek produktu, sekcja z ikonami

| Element | Zmierzona wartość | Token / rola w 2.0 |
|---|---|---|
| przyklejony pasek | `#FFFFFF` | `bg` + cień `bar` |
| przycisk na pasku i kwadrat z sercem | `#007936`, promień ok. 2 px | `brand`, promień 4 |
| podzakładka aktywna | kreska 2 px `#087035`, linia `#EFEFEF` | `brand`, `border` |
| tekst podzakładek | `#333333` wersalikami | `label` |
| „PROSTY SKŁAD” | Mindset `#0A6B36` | `heading-accent` |
| linia podziału | `#DDDDDD` | `border` |
| H2 sekcji | Mindset `#222222` | `heading` |
| tytuły cech | pogrubione `#222222` | `text` |
| przycisk żółty „ZOBACZ WIĘCEJ” | `#FFD821`, tekst `#222222`, promień ok. 3 px, 168 × 43 px | `cta`, `on-cta`, promień 4 |
| kółka strzałek | `#F5F5F5` (nieaktywne `#FBFBFB`), strzałka `#0F763E` | `icon-bg`, `icon` |

## sklep-24.png — strzałki karuzeli

| Element | Zmierzona wartość | Token / rola w 2.0 |
|---|---|---|
| kółko strzałki | `#F5F5F5` | `icon-bg` |
| strzałka | `#0F763E` | `icon` |

## sklep-25.png — stopka z newsletterem

| Element | Zmierzona wartość | Token / rola w 2.0 |
|---|---|---|
| tło stopki | `#F6F2EF` | `zebra` / `surface-hover` |
| nagłówki | `#222222` | `heading` |
| pigułka newslettera | `#0F773E`, przycisk `#007936` | `brand`, `radius-pill` |
| checkbox | wnętrze `#FFFFFF`, obrys `#ADB5BD` | `check-bg`, `check-border` (patrz odstępstwa) |
| drobny druk | `#666666` | `text-muted` |
| linia podziału | `#E3E3E2` | `border` |
| nagłówki kolumn i linki | `#333333` | `label` |

## sklep-26.png — koszyk (wzorzec poziomów)

| Element | Zmierzona wartość | Token / rola w 2.0 |
|---|---|---|
| tło strony | `#FFFFFF` | `bg` = L0 |
| linki, „Bezpieczne zakupy” | `#00642E` | `heading-accent` |
| linia pod nagłówkiem | `#DDDDDD` | `border` |
| aktywny krok | pasek `#47C33D` | `progress` |
| krok nieaktywny | pasek `#E9E9E9`, tekst `#555555` | `switch-off`, `step-idle-text` |
| tytuł „ZAWARTOŚĆ KOSZYKA” | Mindset `#222222` | `heading` |
| panel informacji i panel boczny | `#F8F7F5`, rogi proste | `surface` = L1 (patrz odstępstwa) |
| karty w panelu bocznym | `#FFFFFF` | L2 |
| separatory pozycji | `#DEE2E6` | `border-strong` (`#CED4DA`) |
| nazwy pozycji | `#333333` | `label` |
| tekst pomocniczy | `#666666` | `text-muted` |
| ramka pola ilości | `#CED4DA` | `border-strong` |
| ikona w panelu | `#007936` | `icon` |
| „REALIZUJ ZAMÓWIENIE” | `#007936`, 372 × 51 px, promień ok. 2 px, biały tekst wersalikami | przycisk główny: `brand` |
| „POWRÓT DO SKLEPU” | `#FFFFFF`, obrys 1 px `#222222` | przycisk drugorzędny: `btn2-*` |
| sumy | `#222222` | `text` |

## Wzorce

Wnioski z siedmiu zrzutów. Reguły S1-S12 w `tokens/READY-2.0.0.txt` są ich zapisem.

**Warstwy (koszyk).** Biel strony → jasnoszary ciepły panel `#F8F7F5` → biała karta w panelu → kafel ecru `#FDF8EC` w
karcie → głębszy beż `#F5ECD8` w tym kaflu (zrzut `71-sklep-koszyk.png` pokazuje całą drabinę na kodzie rabatowym).
Biel jest tłem i jest jej najwięcej. Beż i ecru pojawiają się dopiero od poziomu kafla (kafle kategorii na stronie
głównej: ecru na bieli). Panel nie ma obrysu ani cienia. Biała karta wprost na białym tle dostaje linię 1 px.

**Nagłówki.** Mindset, wersaliki. Prawie czarne (`#222222`) dla tytułów treści i kart; ciemnozielone (`#00642E`) dla
tytułu głównego, nadtytułu, aktywnej zakładki i podpisu ikony. Tekst Lato `#222222`, pomocniczy `#666666`.

**Przyciski.** Główny: zielony pełny, biały tekst wersalikami, mały promień (2-5 px; system: 4). Drugorzędny: biały,
obrys 1 px `#222222`, tekst `#222222`. Żółty `#FFD821` z tekstem `#222222` jako jedna wyróżniona akcja („ZOBACZ WIĘCEJ”).
Metka pełna (cena, licznik): zielona, biały tekst, promień ok. 5 px.

**Ikony.** Liniowe, kreska ok. 2, zielone (`#007935`-`#0F763E`); podpis pod ikoną Lato 700, wersaliki, ciemnozielony.
Przycisk-ikona: kwadrat z tłem `#F5F5F5`. Ikony ilustracyjne w sekcjach cech większe (ok. 32 px).

**Kontrolki.** Pole i checkbox: wnętrze białe, obrys szary. Wyszukiwarka: pigułka z zielonym obrysem i zielonym
przyciskiem. Ilość: trzy komórki z ramką `#CED4DA`, znaki ciemnozielone. Postęp i kroki: `#47C33D` na torze `#E9E9E9`.

**Tabele.** Pasy `#F6F2EF` / biel, bez linii pionowych, nagłówek `#333333` bez tła. Linki w treści pogrubione i
podkreślone, `#222222`.

**Zakładki.** Główne: Mindset, aktywna ciemnozielona, nieaktywna czarna, pod spodem linia 1 px `#222222`. Podzakładki:
Lato wersaliki `#333333`, aktywna z zieloną kreską 2 px i linią `#EFEFEF`.

**Kroki.** Trzy paski 5 px; aktywny `#47C33D`, reszta `#E9E9E9`; podpisy `#555555` (aktywny ciemniejszy).

## Świadome odstępstwa

Miejsca, gdzie system 2.0.0 celowo różni się od zrzutów (decyzje w `tokens/READY-2.0.0.txt`).

1. **Promienie.** Panele sklepu mają rogi proste, a przyciski 2-5 px. System ujednolica: przycisk, pole, metka 4 px;
   panel, karta, kafel 8 px (jeden język kształtów: wcześniejsza reguła usera). Tło panelu i kart nadal jak w sklepie.
2. **Obrys checkboxa.** Sklep: `#ADB5BD` (kontrast 2,1:1 z bielą). System: `#868E96` (3:1), żeby kontrolka była
   widoczna na każdym poziomie. Wnętrze białe jak w sklepie.
3. **Jedna zieleń przycisków.** Sklep używa rodziny `#007936` / `#0F763E` / `#097038` / `#08743A` (każdy przycisk nieco
   inny). System ma jedną: `brand` `#007936`, hover `#00642E`. Zmierzone odcienie ponad `brand` to wariacje strony, nie reguła.
4. **Kółka.** Strzałki karuzeli w sklepie są okrągłe. System trzyma regułę „kółko tylko: awatar, kropka, gałka, radio”;
   przycisk-ikona (także strzałka) jest kwadratem 44 px z promieniem 4. Okrągłe strzałki zostają tylko na zrzucie.
5. **Style ciemne.** Zrzuty pokazują wyłącznie tryb jasny. Style ciemne (DK1 zieleń ciemny, DK2 krem ciemny) są bez zmian
   względem 1.6.0 i nie mają dowodu ze sklepu; zyskały tylko nowe role (`heading`, `heading-accent`, `overlay`, `strip`,
   `zebra`, `progress`).
6. **Grafika sklepu.** Przycisk „ZAMÓW” `#63B32E` w banerze i odznaka „%” `#008142` to grafika marketingowa, nie
   komponenty interfejsu; nie mają roli.
