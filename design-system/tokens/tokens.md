# Tokeny Dobra Kaloria 1.5.0

PLIK GENEROWANY z `tokens.json` (`scripts/build_tokens.py`). Zasady użycia: `../DESIGN_SYSTEM.md`, `../IDENTYFIKACJA-WIZUALNA.md`.

## Drabina powierzchni L0-L4 (od 1.4.0)

L = jasność OKLCH (0-100), L* = CIELAB. dL = zmiana L względem poziomu niżej. Kontrast: tekst i tekst pomocniczy na danym poziomie (WCAG).

### Program 'Stwórz prezentację' (domyślny, biała kartka)

`:root, [data-theme="dobra-kaloria"]` · light · L0 1.000, dL 0.020

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna | `--dk-color-surface-0` | `#FFFFFF` | 100.0 | 100.0 | - | - | 13.65 | 5.90 | `#F5EEDD` |
| L1 kontener, sekcja, karta | `--dk-color-surface-1` | `#FDF8ED` | 98.0 | 97.7 | -2.0 | 1.059 | 12.89 | 5.57 | `#EEE7D6` |
| L2 rubryka, pole, karta w karcie | `--dk-color-surface-2` | `#F8F1E0` | 95.9 | 95.3 | -2.1 | 1.063 | 12.13 | 5.24 | `#E8E1D0` |
| L3 element w polu: chip, wiersz, okno w oknie | `--dk-color-surface-3` | `#F2EBDA` | 94.1 | 93.2 | -1.8 | 1.055 | 11.49 | 4.97 | `#E1DAC9` |
| L4 nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `#EBE4D3` | 92.0 | 90.7 | -2.1 | 1.066 | 10.77 | 4.66 | `#DBD4C3` |

### Dobra Kaloria 2 · krem, jasny

`[data-theme="dobra-kaloria-krem-jasny"]` · light · L0 1.000, dL 0.020

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna | `--dk-color-surface-0` | `#FFFFFF` | 100.0 | 100.0 | - | - | 13.65 | 5.90 | `#F5EEDD` |
| L1 kontener, sekcja, karta | `--dk-color-surface-1` | `#FDF8ED` | 98.0 | 97.7 | -2.0 | 1.059 | 12.89 | 5.57 | `#EEE7D6` |
| L2 rubryka, pole, karta w karcie | `--dk-color-surface-2` | `#F8F1E0` | 95.9 | 95.3 | -2.1 | 1.063 | 12.13 | 5.24 | `#E8E1D0` |
| L3 element w polu: chip, wiersz, okno w oknie | `--dk-color-surface-3` | `#F2EBDA` | 94.1 | 93.2 | -1.8 | 1.055 | 11.49 | 4.97 | `#E1DAC9` |
| L4 nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `#EBE4D3` | 92.0 | 90.7 | -2.1 | 1.066 | 10.77 | 4.66 | `#DBD4C3` |

### Dobra Kaloria 1 · zieleń, jasny

`[data-theme="dobra-kaloria-zielen-jasny"]` · light · L0 1.000, dL 0.020

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna | `--dk-color-surface-0` | `#FFFFFF` | 100.0 | 100.0 | - | - | 15.31 | 6.57 | `#F5EEDD` |
| L1 kontener, sekcja, karta | `--dk-color-surface-1` | `#FDF8ED` | 98.0 | 97.7 | -2.0 | 1.059 | 14.46 | 6.20 | `#EEE7D6` |
| L2 rubryka, pole, karta w karcie | `--dk-color-surface-2` | `#F8F1E0` | 95.9 | 95.3 | -2.1 | 1.063 | 13.60 | 5.83 | `#E8E1D0` |
| L3 element w polu: chip, wiersz, okno w oknie | `--dk-color-surface-3` | `#F2EBDA` | 94.1 | 93.2 | -1.8 | 1.055 | 12.89 | 5.53 | `#E1DAC9` |
| L4 nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `#EBE4D3` | 92.0 | 90.7 | -2.1 | 1.066 | 12.08 | 5.18 | `#DBD4C3` |

### Dobra Kaloria 1 · zieleń, ciemny

`[data-theme="dobra-kaloria-zielen-ciemny"], [data-theme="dobra-kaloria-ciemny"]` · dark · L0 0.235, dL 0.034

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna | `--dk-color-surface-0` | `#0F2315` | 23.4 | 11.7 | - | - | 14.94 | 8.97 | `#213B28` |
| L1 kontener, sekcja, karta | `--dk-color-surface-1` | `#192C18` | 27.0 | 15.9 | +3.6 | 1.113 | 13.43 | 8.06 | `#2E432D` |
| L2 rubryka, pole, karta w karcie | `--dk-color-surface-2` | `#24341C` | 30.4 | 19.7 | +3.3 | 1.119 | 12.00 | 7.20 | `#3B4C33` |
| L3 element w polu: chip, wiersz, okno w oknie | `--dk-color-surface-3` | `#303C21` | 33.7 | 23.6 | +3.4 | 1.133 | 10.59 | 6.35 | `#485439` |
| L4 nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `#3D4427` | 37.2 | 27.5 | +3.5 | 1.145 | 9.25 | 5.55 | `#555C3F` |

### Dobra Kaloria 2 · krem, ciemny

`[data-theme="dobra-kaloria-krem-ciemny"], [data-theme="dobra-kaloria-krem"]` · dark · L0 0.170, dL 0.034

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna | `--dk-color-surface-0` | `#120F0A` | 17.0 | 4.4 | - | - | 16.96 | 10.52 | `#28231B` |
| L1 kontener, sekcja, karta | `--dk-color-surface-1` | `#1A1611` | 20.3 | 7.5 | +3.3 | 1.062 | 15.97 | 9.91 | `#312B22` |
| L2 rubryka, pole, karta w karcie | `--dk-color-surface-2` | `#231E17` | 23.8 | 11.6 | +3.5 | 1.088 | 14.67 | 9.10 | `#3B3429` |
| L3 element w polu: chip, wiersz, okno w oknie | `--dk-color-surface-3` | `#2C261E` | 27.3 | 15.6 | +3.4 | 1.105 | 13.28 | 8.24 | `#443C31` |
| L4 nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `#352E25` | 30.6 | 19.4 | +3.3 | 1.118 | 11.87 | 7.37 | `#4E4538` |

## Tagi (od 1.4.0)

Wzór: hue = `tag_hue` wariantu + przesunięcie `[0, 8, -8, 16, -16, 24, -24, 32]` (stopnie OKLCH). Tło L 0.930 C 0.038 / ramka L 0.845 C 0.055 / tekst L 0.440 C 0.085 w jasnym; w ciemnym tło L 0.360 C 0.048 / ramka L 0.470 C 0.062 / tekst L 0.870 C 0.070. Tekst dociągany o 0.01 L do kontrastu >= 4.6.

| Wariant | Tag | Hue | Tło | Tekst | Ramka | Kontrast |
|---|---|---|---|---|---|---|
| program | tag-1 | 90 | `#F2E7CC` | `#65500B` | `#DACBA4` | 6.31:1 |
| program | tag-2 | 98 | `#EEE9CC` | `#5F520D` | `#D5CDA4` | 6.36:1 |
| program | tag-3 | 82 | `#F5E6CC` | `#6A4D0C` | `#DEC9A4` | 6.37:1 |
| program | tag-4 | 106 | `#EBEACD` | `#595512` | `#D0CFA6` | 6.29:1 |
| program | tag-5 | 74 | `#F8E5CD` | `#6E4A11` | `#E2C7A5` | 6.44:1 |
| program | tag-6 | 114 | `#E7EBCF` | `#525718` | `#CBD1A8` | 6.28:1 |
| program | tag-7 | 66 | `#FAE3CE` | `#724816` | `#E6C6A7` | 6.38:1 |
| program | tag-8 | 122 | `#E3ECD1` | `#4B5A1F` | `#C6D2AB` | 6.18:1 |
| krem-jasny | tag-1 | 90 | `#F2E7CC` | `#65500B` | `#DACBA4` | 6.31:1 |
| krem-jasny | tag-2 | 98 | `#EEE9CC` | `#5F520D` | `#D5CDA4` | 6.36:1 |
| krem-jasny | tag-3 | 82 | `#F5E6CC` | `#6A4D0C` | `#DEC9A4` | 6.37:1 |
| krem-jasny | tag-4 | 106 | `#EBEACD` | `#595512` | `#D0CFA6` | 6.29:1 |
| krem-jasny | tag-5 | 74 | `#F8E5CD` | `#6E4A11` | `#E2C7A5` | 6.44:1 |
| krem-jasny | tag-6 | 114 | `#E7EBCF` | `#525718` | `#CBD1A8` | 6.28:1 |
| krem-jasny | tag-7 | 66 | `#FAE3CE` | `#724816` | `#E6C6A7` | 6.38:1 |
| krem-jasny | tag-8 | 122 | `#E3ECD1` | `#4B5A1F` | `#C6D2AB` | 6.18:1 |
| zielen-jasny | tag-1 | 146 | `#D8EFD9` | `#305F35` | `#B6D6B7` | 6.14:1 |
| zielen-jasny | tag-2 | 154 | `#D5F0DD` | `#26603C` | `#B1D7BC` | 6.15:1 |
| zielen-jasny | tag-3 | 138 | `#DCEED6` | `#3A5D2D` | `#BBD5B3` | 6.19:1 |
| zielen-jasny | tag-4 | 162 | `#D2F0E0` | `#196144` | `#ADD8C1` | 6.10:1 |
| zielen-jasny | tag-5 | 130 | `#E0EDD3` | `#435C26` | `#C0D4AE` | 6.16:1 |
| zielen-jasny | tag-6 | 170 | `#D0F1E4` | `#06614B` | `#A9D8C7` | 6.17:1 |
| zielen-jasny | tag-7 | 122 | `#E3ECD1` | `#4B5A1F` | `#C6D2AB` | 6.18:1 |
| zielen-jasny | tag-8 | 178 | `#CEF1E8` | `#006152` | `#A6D8CC` | 6.13:1 |
| zielen-ciemny | tag-1 | 146 | `#2C442E` | `#B7E1B9` | `#446446` | 7.34:1 |
| zielen-ciemny | tag-2 | 154 | `#284531` | `#B1E2C0` | `#3E654B` | 7.31:1 |
| zielen-ciemny | tag-3 | 138 | `#31432A` | `#BEE0B3` | `#496341` | 7.37:1 |
| zielen-ciemny | tag-4 | 162 | `#244535` | `#ABE3C6` | `#386650` | 7.35:1 |
| zielen-ciemny | tag-5 | 130 | `#354227` | `#C5DEAE` | `#4F623C` | 7.36:1 |
| zielen-ciemny | tag-6 | 170 | `#204539` | `#A6E4CD` | `#336655` | 7.40:1 |
| zielen-ciemny | tag-7 | 122 | `#394124` | `#CCDCA9` | `#556038` | 7.35:1 |
| zielen-ciemny | tag-8 | 178 | `#1D453D` | `#A2E4D4` | `#2F665B` | 7.40:1 |
| krem-ciemny | tag-1 | 90 | `#3A2F11` | `#E6D3A0` | `#5A4B22` | 8.90:1 |
| krem-ciemny | tag-2 | 98 | `#373011` | `#E0D5A0` | `#564D23` | 8.91:1 |
| krem-ciemny | tag-3 | 82 | `#3C2E11` | `#EBD0A0` | `#5E4A22` | 8.84:1 |
| krem-ciemny | tag-4 | 106 | `#333213` | `#DAD8A2` | `#514F25` | 8.92:1 |
| krem-ciemny | tag-5 | 74 | `#3F2C12` | `#F0CEA1` | `#614824` | 8.89:1 |
| krem-ciemny | tag-6 | 114 | `#303315` | `#D3DAA5` | `#4D5127` | 8.91:1 |
| krem-ciemny | tag-7 | 66 | `#412B14` | `#F5CCA4` | `#644626` | 8.89:1 |
| krem-ciemny | tag-8 | 122 | `#2C3417` | `#CCDCA9` | `#47522B` | 8.93:1 |

## Kolory - role programu (tych używaj)

| Rola | Zmienna CSS | Wartość | Źródło |
|---|---|---|---|
| text | `--dk-color-text` | `#3B2A20` | brown-900 |
| text-muted | `--dk-color-text-muted` | `#7D5E44` | brown-600 |
| label | `--dk-color-label` | `#AD8767` | tan-400 |
| bg | `--dk-color-bg` | `#FFFFFF` | @surface-0 |
| surface | `--dk-color-surface` | `#FDF8ED` | @surface-1 |
| surface-hover | `--dk-color-surface-hover` | `#F8F1E0` | @surface-2 |
| border | `--dk-color-border` | `#EDE7DA` | sand-200 |
| border-strong | `--dk-color-border-strong` | `#D9CFBB` | sand-300 |
| field-border | `--dk-color-field-border` | `#9C8B72` | sand-700 |
| brand | `--dk-color-brand` | `#0F763E` | green-700 |
| brand-hover | `--dk-color-brand-hover` | `#0B5F31` | green-800 |
| brand-soft | `--dk-color-brand-soft` | `#E9F2EC` | green-100 |
| brand-soft-strong | `--dk-color-brand-soft-strong` | `#CFE0D4` | green-200 |
| on-brand | `--dk-color-on-brand` | `#FFFFFF` | white |
| cta | `--dk-color-cta` | `#FFD42A` | yellow-400 |
| cta-hover | `--dk-color-cta-hover` | `#F6C700` | yellow-500 |
| on-cta | `--dk-color-on-cta` | `#3B2A20` | brown-900 |
| disabled-bg | `--dk-color-disabled-bg` | `#F0EBDD` | sand-150 |
| switch-off | `--dk-color-switch-off` | `#9C8B72` | sand-700 |
| danger | `--dk-color-danger` | `#DA272D` | red-600 |
| danger-soft | `--dk-color-danger-soft` | `#FCE8E9` | red-50 |
| warning-text | `--dk-color-warning-text` | `#7A4E00` | amber-900 |
| warning-border | `--dk-color-warning-border` | `#EBCB6B` | amber-300 |
| warning-bg | `--dk-color-warning-bg` | `#FFF4D6` | amber-50 |
| inverse-bg | `--dk-color-inverse-bg` | `#3B2A20` | brown-900 |
| on-inverse | `--dk-color-on-inverse` | `#FFFFFF` | white |
| focus | `--dk-color-focus` | `#0F763E` | green-700 |

## Kolory - prymitywy

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| green-700 | `--dk-green-700` | `#0F763E` |
| green-800 | `--dk-green-800` | `#0B5F31` |
| green-200 | `--dk-green-200` | `#CFE0D4` |
| green-100 | `--dk-green-100` | `#E9F2EC` |
| brown-900 | `--dk-brown-900` | `#3B2A20` |
| brown-600 | `--dk-brown-600` | `#7D5E44` |
| tan-400 | `--dk-tan-400` | `#AD8767` |
| tan-450 | `--dk-tan-450` | `#A47E5E` |
| sand-700 | `--dk-sand-700` | `#9C8B72` |
| sand-300 | `--dk-sand-300` | `#D9CFBB` |
| sand-200 | `--dk-sand-200` | `#EDE7DA` |
| sand-150 | `--dk-sand-150` | `#F0EBDD` |
| cream-100 | `--dk-cream-100` | `#FBF3E0` |
| cream-50 | `--dk-cream-50` | `#FDF8EC` |
| white | `--dk-white` | `#FFFFFF` |
| yellow-400 | `--dk-yellow-400` | `#FFD42A` |
| yellow-500 | `--dk-yellow-500` | `#F6C700` |
| red-600 | `--dk-red-600` | `#DA272D` |
| red-200 | `--dk-red-200` | `#F3B9BB` |
| red-100 | `--dk-red-100` | `#F8D4D5` |
| red-50 | `--dk-red-50` | `#FCE8E9` |
| amber-900 | `--dk-amber-900` | `#7A4E00` |
| amber-300 | `--dk-amber-300` | `#EBCB6B` |
| amber-50 | `--dk-amber-50` | `#FFF4D6` |
| forest-950 | `--dk-forest-950` | `#0F1F15` |
| forest-900 | `--dk-forest-900` | `#162B1E` |
| forest-850 | `--dk-forest-850` | `#1D3526` |
| forest-800 | `--dk-forest-800` | `#26422F` |
| forest-700 | `--dk-forest-700` | `#2F4D39` |
| forest-600 | `--dk-forest-600` | `#44664F` |
| forest-400 | `--dk-forest-400` | `#7E9C88` |
| ivory-50 | `--dk-ivory-50` | `#F5F1E8` |
| sand-400 | `--dk-sand-400` | `#C9BEA6` |
| tan-300 | `--dk-tan-300` | `#D2B48F` |
| green-300 | `--dk-green-300` | `#6FC792` |
| green-250 | `--dk-green-250` | `#8AD6A8` |
| red-300 | `--dk-red-300` | `#F2878A` |
| cocoa-950 | `--dk-cocoa-950` | `#1C1812` |
| cocoa-900 | `--dk-cocoa-900` | `#26211A` |
| cocoa-850 | `--dk-cocoa-850` | `#302A21` |
| cocoa-800 | `--dk-cocoa-800` | `#3A3329` |
| cocoa-700 | `--dk-cocoa-700` | `#4A4135` |
| cocoa-600 | `--dk-cocoa-600` | `#6B5E4B` |
| cocoa-400 | `--dk-cocoa-400` | `#8C7D65` |
| sand-450 | `--dk-sand-450` | `#CBBFA8` |
| green-350 | `--dk-green-350` | `#4CC46A` |
| green-500 | `--dk-green-500` | `#1EA03A` |
| tan-500 | `--dk-tan-500` | `#8E7C50` |
| tan-350 | `--dk-tan-350` | `#B8A274` |
| tan-650 | `--dk-tan-650` | `#6E5F3C` |
| sage-50 | `--dk-sage-50` | `#EEF4EF` |
| sage-100 | `--dk-sage-100` | `#E4EEE7` |
| sage-150 | `--dk-sage-150` | `#DDEBE1` |
| sage-200 | `--dk-sage-200` | `#D3E1D7` |
| sage-300 | `--dk-sage-300` | `#B3C9BA` |
| sage-500 | `--dk-sage-500` | `#6E8C78` |
| pine-900 | `--dk-pine-900` | `#17291D` |
| pine-600 | `--dk-pine-600` | `#4A6352` |
| olive-500 | `--dk-olive-500` | `#5E7A4A` |
| red-700 | `--dk-red-700` | `#C0262C` |
| amber-950 | `--dk-amber-950` | `#6F4A00` |
| lime-300 | `--dk-lime-300` | `#A2D686` |
| lime-200 | `--dk-lime-200` | `#C2E59F` |
| honey-300 | `--dk-honey-300` | `#ECCA76` |
| moss-950 | `--dk-moss-950` | `#0F190C` |
| moss-850 | `--dk-moss-850` | `#242F1E` |
| moss-800 | `--dk-moss-800` | `#2C3A25` |
| moss-700 | `--dk-moss-700` | `#3B4E37` |
| moss-600 | `--dk-moss-600` | `#516448` |
| moss-400 | `--dk-moss-400` | `#889979` |
| espresso-850 | `--dk-espresso-850` | `#262017` |
| espresso-800 | `--dk-espresso-800` | `#2F291F` |
| espresso-700 | `--dk-espresso-700` | `#3F362A` |
| espresso-600 | `--dk-espresso-600` | `#5F5240` |

## Kontrast (WCAG) - program

| Tekst | Tło | Kontrast | Minimum | Zastosowanie |
|---|---|---|---|---|
| text | bg | 13.65:1 | 4.5:1 | tekst na tle |
| text | surface | 12.89:1 | 4.5:1 | tekst na karcie |
| text-muted | bg | 5.90:1 | 4.5:1 | tekst pomocniczy na tle |
| text-muted | surface | 5.57:1 | 4.5:1 | tekst pomocniczy na karcie |
| label | bg | 3.26:1 | 3.0:1 | etykieta (tylko >=14 px bold) |
| label | surface | 3.08:1 | 3.0:1 | etykieta na karcie |
| brand | bg | 5.70:1 | 4.5:1 | zielony tekst/link na tle |
| brand | brand-soft | 4.99:1 | 4.5:1 | zielony na jasnej zieleni |
| on-brand | brand | 5.70:1 | 4.5:1 | biały na zieleni |
| on-cta | cta | 9.56:1 | 4.5:1 | tekst na żółtym przycisku |
| on-inverse | inverse-bg | 13.65:1 | 4.5:1 | biały na brązie (toast) |
| on-inverse | danger | 4.87:1 | 4.5:1 | biały na czerwieni |
| danger | bg | 4.87:1 | 4.5:1 | czerwony tekst błędu na tle |
| danger | surface | 4.60:1 | 4.5:1 | czerwony tekst błędu na karcie |
| warning-text | warning-bg | 6.57:1 | 4.5:1 | ostrzeżenie |
| field-border | bg | 3.31:1 | 3.0:1 | ramka pola |
| switch-off | bg | 3.31:1 | 3.0:1 | wyłączony przełącznik |

## Czcionki

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| display | `--dk-font-display` | `"Mindset", "Arial Narrow", Impact, sans-serif` |
| text | `--dk-font-text` | `"Lato", "Segoe UI", Arial, sans-serif` |
| mono | `--dk-font-mono` | `Consolas, "Cascadia Mono", "Courier New", monospace` |

## Rozmiary tekstu

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| sm | `--dk-fs-sm` | `15px` |
| base | `--dk-fs-base` | `16px` |
| md | `--dk-fs-md` | `17px` |
| lg | `--dk-fs-lg` | `20px` |
| xl | `--dk-fs-xl` | `22px` |
| display-sm | `--dk-fs-display-sm` | `40px` |
| display-md | `--dk-fs-display-md` | `46px` |
| display-lg | `--dk-fs-display-lg` | `76px` |
| display-hero | `--dk-fs-display-hero` | `168px` |

## Interlinie

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| display | `--dk-lh-display` | `1.02` |
| tight | `--dk-lh-tight` | `1.25` |
| snug | `--dk-lh-snug` | `1.35` |
| base | `--dk-lh-base` | `1.5` |

## Odstępy (siatka 4 px)

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| 1 | `--dk-space-1` | `4px` |
| 2 | `--dk-space-2` | `8px` |
| 3 | `--dk-space-3` | `12px` |
| 4 | `--dk-space-4` | `16px` |
| 5 | `--dk-space-5` | `20px` |
| 6 | `--dk-space-6` | `24px` |
| 8 | `--dk-space-8` | `32px` |
| 10 | `--dk-space-10` | `40px` |
| 12 | `--dk-space-12` | `48px` |
| 14 | `--dk-space-14` | `56px` |
| 16 | `--dk-space-16` | `64px` |
| 20 | `--dk-space-20` | `80px` |

## Promienie

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| btn | `--dk-radius-btn` | `4px` |
| sm | `--dk-radius-sm` | `8px` |
| md | `--dk-radius-md` | `12px` |
| lg | `--dk-radius-lg` | `16px` |
| pill | `--dk-radius-pill` | `999px` |

## Cienie (podbarwione brązem)

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| thumb | `--dk-shadow-thumb` | `0 1px 2px rgba(59,42,32,.18), 0 5px 12px rgba(59,42,32,.16)` |
| raised | `--dk-shadow-raised` | `0 1px 4px rgba(59,42,32,.25)` |
| bar | `--dk-shadow-bar` | `0 -8px 24px rgba(59,42,32,.05)` |
| toast | `--dk-shadow-toast` | `0 10px 30px rgba(59,42,32,.28)` |
| focus-field | `--dk-shadow-focus-field` | `0 0 0 3px rgba(15,118,62,.22)` |

## Ruch

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| fast | `--dk-motion-fast` | `.15s` |
| base | `--dk-motion-base` | `.18s` |
| slow | `--dk-motion-slow` | `.28s` |
| ease | `--dk-motion-ease` | `ease-out` |

## Kontrolki

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| h-min | `--dk-control-h-min` | `44px` |
| h | `--dk-control-h` | `48px` |
| h-lg | `--dk-control-h-lg` | `56px` |
| focus-width | `--dk-control-focus-width` | `3px` |
| focus-offset | `--dk-control-focus-offset` | `3px` |
| stroke-icon | `--dk-control-stroke-icon` | `1.6` |

## Układ

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| wrap | `--dk-layout-wrap` | `920px` |
| gutter | `--dk-layout-gutter` | `24px` |
| card-pad | `--dk-layout-card-pad` | `32px` (= space.8) |
| card-pad-lg | `--dk-layout-card-pad-lg` | `40px` (= space.10) |
| section-gap | `--dk-layout-section-gap` | `40px` (= space.10) |
| stack | `--dk-layout-stack` | `20px` (= space.5) |
| card-pad-sm | `--dk-layout-card-pad-sm` | `20px` (= space.5) |
| section-gap-sm | `--dk-layout-section-gap-sm` | `24px` (= space.6) |
| stack-sm | `--dk-layout-stack-sm` | `12px` (= space.3) |

## Qt: skala tekstu i odstępy z programu (QSS px)

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| fs-body | `--dk-qt-fs-body` | `15px` |
| fs-label | `--dk-qt-fs-label` | `14px` |
| fs-hint | `--dk-qt-fs-hint` | `14px` |
| fs-eyebrow | `--dk-qt-fs-eyebrow` | `14px` |
| fs-btn | `--dk-qt-fs-btn` | `15px` |
| fs-btn-primary | `--dk-qt-fs-btn-primary` | `17px` |
| fs-title | `--dk-qt-fs-title` | `22px` |
| fs-app-title | `--dk-qt-fs-app-title` | `20px` |
| fs-dialog-title | `--dk-qt-fs-dialog-title` | `26px` |
| control-h | `--dk-qt-control-h` | `40px` |
| control-h-primary | `--dk-qt-control-h-primary` | `48px` |
| control-h-sm | `--dk-qt-control-h-sm` | `36px` |
| pad-card | `--dk-qt-pad-card` | `20px` |
| gap-cards | `--dk-qt-gap-cards` | `16px` |
| gap-stack | `--dk-qt-gap-stack` | `12px` |
| gap-row | `--dk-qt-gap-row` | `10px` |
| margin-window | `--dk-qt-margin-window` | `20px` |
| card-border | `--dk-qt-card-border` | `1px` |
| field-border | `--dk-qt-field-border` | `1px` |
| focus-border | `--dk-qt-focus-border` | `2px` |
| radius-card | `--dk-qt-radius-card` | `12px` |
| radius-field | `--dk-qt-radius-field` | `8px` |
| radius-btn | `--dk-qt-radius-btn` | `4px` |
| radius-drop | `--dk-qt-radius-drop` | `16px` |
