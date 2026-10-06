# Tokeny Dobra Kaloria 2.0.0

PLIK GENEROWANY z `tokens.json` (`scripts/build_tokens.py`). Zasady użycia: `../DESIGN_SYSTEM.md`, `../IDENTYFIKACJA-WIZUALNA.md`.

## Drabina powierzchni L0-L4 (od 1.4.0)

L = jasność OKLCH (0-100), L* = CIELAB. dL = zmiana L względem poziomu niżej. Kontrast: tekst i tekst pomocniczy na danym poziomie (WCAG).

### Sklep Dobra Kaloria (domyślny): biel, szary panel, biała karta

`:root, [data-theme="dobra-kaloria"]` · light · jawna (sklep): #FFFFFF > #F8F7F5 > #FFFFFF > #FDF8EC > #F5ECD8

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna (biel) | `--dk-color-surface-0` | `#FFFFFF` | 100.0 | 100.0 | - | - | 15.91 | 5.74 | `#DDDDDD` |
| L1 panel, sekcja (jasnoszary ciepły) | `--dk-color-surface-1` | `#F8F7F5` | 97.6 | 97.3 | -2.4 | 1.071 | 14.86 | 5.36 | `#DDDDDD` |
| L2 karta lub pole w panelu (biel) | `--dk-color-surface-2` | `#FFFFFF` | 100.0 | 100.0 | +2.4 | 1.071 | 15.91 | 5.74 | `#DDDDDD` |
| L3 kafel w karcie (ecru) | `--dk-color-surface-3` | `#FDF8EC` | 98.0 | 97.7 | -2.0 | 1.060 | 15.01 | 5.42 | `#EADFC6` |
| L4 kafel w kaflu (głębszy beż) | `--dk-color-surface-4` | `#F5ECD8` | 94.5 | 93.6 | -3.5 | 1.109 | 13.54 | 4.89 | `#DDD0B4` |

### Dobra Kaloria 2 · krem, jasny (kafle ecru na bieli, jak strona główna sklepu)

`[data-theme="dobra-kaloria-krem-jasny"]` · light · jawna (sklep): #FFFFFF > #FDF8EC > #FFFFFF > #F5ECD8 > #F0E6CF

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna (biel) | `--dk-color-surface-0` | `#FFFFFF` | 100.0 | 100.0 | - | - | 15.91 | 5.74 | `#DDDDDD` |
| L1 kafel, sekcja (ecru) | `--dk-color-surface-1` | `#FDF8EC` | 98.0 | 97.7 | -2.0 | 1.060 | 15.01 | 5.42 | `#EADFC6` |
| L2 karta lub pole w kaflu (biel) | `--dk-color-surface-2` | `#FFFFFF` | 100.0 | 100.0 | +2.0 | 1.060 | 15.91 | 5.74 | `#DDDDDD` |
| L3 kafel w karcie (beż) | `--dk-color-surface-3` | `#F5ECD8` | 94.5 | 93.6 | -5.5 | 1.175 | 13.54 | 4.89 | `#DDD0B4` |
| L4 kafel w kaflu (głębszy beż) | `--dk-color-surface-4` | `#F0E6CF` | 92.7 | 91.5 | -1.8 | 1.056 | 12.82 | 4.63 | `#D3C5A6` |

### Dobra Kaloria 1 · zieleń, jasny (= sklep)

`[data-theme="dobra-kaloria-zielen-jasny"]` · light · jawna (sklep): #FFFFFF > #F8F7F5 > #FFFFFF > #FDF8EC > #F5ECD8

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna (biel) | `--dk-color-surface-0` | `#FFFFFF` | 100.0 | 100.0 | - | - | 15.91 | 5.74 | `#DDDDDD` |
| L1 panel, sekcja (jasnoszary ciepły) | `--dk-color-surface-1` | `#F8F7F5` | 97.6 | 97.3 | -2.4 | 1.071 | 14.86 | 5.36 | `#DDDDDD` |
| L2 karta lub pole w panelu (biel) | `--dk-color-surface-2` | `#FFFFFF` | 100.0 | 100.0 | +2.4 | 1.071 | 15.91 | 5.74 | `#DDDDDD` |
| L3 kafel w karcie (ecru) | `--dk-color-surface-3` | `#FDF8EC` | 98.0 | 97.7 | -2.0 | 1.060 | 15.01 | 5.42 | `#EADFC6` |
| L4 kafel w kaflu (głębszy beż) | `--dk-color-surface-4` | `#F5ECD8` | 94.5 | 93.6 | -3.5 | 1.109 | 13.54 | 4.89 | `#DDD0B4` |

### Dobra Kaloria 1 · zieleń, ciemny

`[data-theme="dobra-kaloria-zielen-ciemny"], [data-theme="dobra-kaloria-ciemny"]` · dark · L0 0.235, dL 0.034 (OKLCH), ciemny: głębiej = jaśniej

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna | `--dk-color-surface-0` | `#0F2315` | 23.4 | 11.7 | - | - | 14.94 | 8.97 | `#213B28` |
| L1 kontener, sekcja, karta | `--dk-color-surface-1` | `#192C18` | 27.0 | 15.9 | +3.6 | 1.113 | 13.43 | 8.06 | `#2E432D` |
| L2 rubryka, pole, karta w karcie | `--dk-color-surface-2` | `#24341C` | 30.4 | 19.7 | +3.3 | 1.119 | 12.00 | 7.20 | `#3B4C33` |
| L3 element w polu: chip, wiersz, okno w oknie | `--dk-color-surface-3` | `#303C21` | 33.7 | 23.6 | +3.4 | 1.133 | 10.59 | 6.35 | `#485439` |
| L4 nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `#3D4427` | 37.2 | 27.5 | +3.5 | 1.145 | 9.25 | 5.55 | `#555C3F` |

### Dobra Kaloria 2 · krem, ciemny

`[data-theme="dobra-kaloria-krem-ciemny"], [data-theme="dobra-kaloria-krem"]` · dark · L0 0.170, dL 0.034 (OKLCH), ciemny: głębiej = jaśniej

| Poziom | Zmienna | Hex | L | L* | dL | Kontrast z niższym | Tekst | Pomocniczy | Ramka `border-subtle` |
|---|---|---|---|---|---|---|---|---|---|
| L0 tło okna | `--dk-color-surface-0` | `#120F0A` | 17.0 | 4.4 | - | - | 16.96 | 10.52 | `#28231B` |
| L1 kontener, sekcja, karta | `--dk-color-surface-1` | `#1A1611` | 20.3 | 7.5 | +3.3 | 1.062 | 15.97 | 9.91 | `#312B22` |
| L2 rubryka, pole, karta w karcie | `--dk-color-surface-2` | `#231E17` | 23.8 | 11.6 | +3.5 | 1.088 | 14.67 | 9.10 | `#3B3429` |
| L3 element w polu: chip, wiersz, okno w oknie | `--dk-color-surface-3` | `#2C261E` | 27.3 | 15.6 | +3.4 | 1.105 | 13.28 | 8.24 | `#443C31` |
| L4 nakładka: menu, podpowiedź, modal nad modalem | `--dk-color-surface-4` | `#352E25` | 30.6 | 19.4 | +3.3 | 1.118 | 11.87 | 7.37 | `#4E4538` |

## Tagi (od 1.4.0)

Wzór: hue = `tag_hue` wariantu + przesunięcie `[0, 8, -8, 16, -16, 24, -24, 32]` (stopnie OKLCH; od 1.6.0 wariant może mieć własne `tag_offsets` - zestawy beżowe mają tylko ciepłe odcienie, zob. kolumnę Hue). Tło L 0.930 C 0.038 / ramka L 0.845 C 0.055 / tekst L 0.440 C 0.085 w jasnym; w ciemnym tło L 0.360 C 0.048 / ramka L 0.470 C 0.062 / tekst L 0.870 C 0.070. Tekst dociągany o 0.01 L do kontrastu >= 4.6.

| Wariant | Tag | Hue | Tło | Tekst | Ramka | Kontrast |
|---|---|---|---|---|---|---|
| program | tag-1 | 152 | `#D6F0DC` | `#28603A` | `#B2D7BB` | 6.15:1 |
| program | tag-2 | 160 | `#D3F0DF` | `#1C6142` | `#AED8C0` | 6.10:1 |
| program | tag-3 | 144 | `#D9EFD8` | `#335F33` | `#B7D6B6` | 6.12:1 |
| program | tag-4 | 168 | `#D1F1E3` | `#0C6149` | `#AAD8C5` | 6.17:1 |
| program | tag-5 | 136 | `#DDEED5` | `#3C5D2B` | `#BCD5B1` | 6.18:1 |
| program | tag-6 | 176 | `#CFF1E7` | `#016151` | `#A7D8CB` | 6.14:1 |
| program | tag-7 | 128 | `#E0EDD2` | `#455B24` | `#C2D4AD` | 6.20:1 |
| program | tag-8 | 184 | `#CDF1EB` | `#006057` | `#A4D8D0` | 6.18:1 |
| krem-jasny | tag-1 | 152 | `#D6F0DC` | `#28603A` | `#B2D7BB` | 6.15:1 |
| krem-jasny | tag-2 | 160 | `#D3F0DF` | `#1C6142` | `#AED8C0` | 6.10:1 |
| krem-jasny | tag-3 | 144 | `#D9EFD8` | `#335F33` | `#B7D6B6` | 6.12:1 |
| krem-jasny | tag-4 | 168 | `#D1F1E3` | `#0C6149` | `#AAD8C5` | 6.17:1 |
| krem-jasny | tag-5 | 136 | `#DDEED5` | `#3C5D2B` | `#BCD5B1` | 6.18:1 |
| krem-jasny | tag-6 | 176 | `#CFF1E7` | `#016151` | `#A7D8CB` | 6.14:1 |
| krem-jasny | tag-7 | 128 | `#E0EDD2` | `#455B24` | `#C2D4AD` | 6.20:1 |
| krem-jasny | tag-8 | 184 | `#CDF1EB` | `#006057` | `#A4D8D0` | 6.18:1 |
| zielen-jasny | tag-1 | 152 | `#D6F0DC` | `#28603A` | `#B2D7BB` | 6.15:1 |
| zielen-jasny | tag-2 | 160 | `#D3F0DF` | `#1C6142` | `#AED8C0` | 6.10:1 |
| zielen-jasny | tag-3 | 144 | `#D9EFD8` | `#335F33` | `#B7D6B6` | 6.12:1 |
| zielen-jasny | tag-4 | 168 | `#D1F1E3` | `#0C6149` | `#AAD8C5` | 6.17:1 |
| zielen-jasny | tag-5 | 136 | `#DDEED5` | `#3C5D2B` | `#BCD5B1` | 6.18:1 |
| zielen-jasny | tag-6 | 176 | `#CFF1E7` | `#016151` | `#A7D8CB` | 6.14:1 |
| zielen-jasny | tag-7 | 128 | `#E0EDD2` | `#455B24` | `#C2D4AD` | 6.20:1 |
| zielen-jasny | tag-8 | 184 | `#CDF1EB` | `#006057` | `#A4D8D0` | 6.18:1 |
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
| krem-ciemny | tag-4 | 78 | `#3E2D12` | `#EECFA1` | `#604923` | 8.86:1 |
| krem-ciemny | tag-5 | 74 | `#3F2C12` | `#F0CEA1` | `#614824` | 8.89:1 |
| krem-ciemny | tag-6 | 70 | `#402C13` | `#F3CDA3` | `#634725` | 8.86:1 |
| krem-ciemny | tag-7 | 66 | `#412B14` | `#F5CCA4` | `#644626` | 8.89:1 |
| krem-ciemny | tag-8 | 62 | `#422A15` | `#F6CBA5` | `#654528` | 8.90:1 |

## Kolory - role programu (tych używaj)

| Rola | Zmienna CSS | Wartość | Źródło |
|---|---|---|---|
| text | `--dk-color-text` | `#222222` | ink-900 |
| text-muted | `--dk-color-text-muted` | `#666666` | ink-600 |
| label | `--dk-color-label` | `#333333` | ink-800 |
| heading | `--dk-color-heading` | `#222222` | ink-900 |
| heading-accent | `--dk-color-heading-accent` | `#00642E` | green-900 |
| bg | `--dk-color-bg` | `#FFFFFF` | @surface-0 |
| surface | `--dk-color-surface` | `#F8F7F5` | @surface-1 |
| surface-hover | `--dk-color-surface-hover` | `#F6F2EF` | stone-200 |
| overlay | `--dk-color-overlay` | `#FFFFFF` | white |
| strip | `--dk-color-strip` | `#F8F4F1` | stone-150 |
| zebra | `--dk-color-zebra` | `#F6F2EF` | stone-200 |
| border | `--dk-color-border` | `#DDDDDD` | grey-250 |
| border-strong | `--dk-color-border-strong` | `#CED4DA` | grey-300 |
| field-border | `--dk-color-field-border` | `#868E96` | grey-500 |
| brand | `--dk-color-brand` | `#007936` | green-750 |
| brand-hover | `--dk-color-brand-hover` | `#00642E` | green-900 |
| brand-soft | `--dk-color-brand-soft` | `#E9F2EC` | green-100 |
| brand-soft-strong | `--dk-color-brand-soft-strong` | `#CFE0D4` | green-200 |
| on-brand | `--dk-color-on-brand` | `#FFFFFF` | white |
| progress | `--dk-color-progress` | `#47C33D` | green-450 |
| cta | `--dk-color-cta` | `#FFD821` | yellow-450 |
| cta-hover | `--dk-color-cta-hover` | `#F6C700` | yellow-500 |
| on-cta | `--dk-color-on-cta` | `#222222` | ink-900 |
| disabled-bg | `--dk-color-disabled-bg` | `#F5F5F5` | grey-100 |
| switch-off | `--dk-color-switch-off` | `#E9E9E9` | grey-200 |
| danger | `--dk-color-danger` | `#C0262C` | red-700 |
| danger-soft | `--dk-color-danger-soft` | `#FCE8E9` | red-50 |
| warning-text | `--dk-color-warning-text` | `#6F4A00` | amber-950 |
| warning-border | `--dk-color-warning-border` | `#EBCB6B` | amber-300 |
| warning-bg | `--dk-color-warning-bg` | `#FFF4D6` | amber-50 |
| inverse-bg | `--dk-color-inverse-bg` | `#222222` | ink-900 |
| on-inverse | `--dk-color-on-inverse` | `#FFFFFF` | white |
| focus | `--dk-color-focus` | `#007936` | green-750 |
| accent | `--dk-color-accent` | `#007936` | green-750 |
| accent-hover | `--dk-color-accent-hover` | `#00642E` | green-900 |
| on-accent | `--dk-color-on-accent` | `#FFFFFF` | white |
| accent-beige | `--dk-color-accent-beige` | `#AD8767` | tan-400 |
| icon | `--dk-color-icon` | `#007936` | green-750 |
| icon-bg | `--dk-color-icon-bg` | `#F5F5F5` | grey-100 |
| check-bg | `--dk-color-check-bg` | `#FFFFFF` | white |
| check-border | `--dk-color-check-border` | `#868E96` | grey-500 |
| check-border-hover | `--dk-color-check-border-hover` | `#007936` | green-750 |
| check-mark | `--dk-color-check-mark` | `#007936` | green-750 |
| check-disabled-border | `--dk-color-check-disabled-border` | `#CED4DA` | grey-300 |
| check-disabled-mark | `--dk-color-check-disabled-mark` | `#ADB5BD` | grey-400 |
| slider-track | `--dk-color-slider-track` | `#E9E9E9` | grey-200 |
| slider-fill | `--dk-color-slider-fill` | `#007936` | green-750 |
| slider-thumb | `--dk-color-slider-thumb` | `#FFFFFF` | white |
| slider-thumb-border | `--dk-color-slider-thumb-border` | `#007936` | green-750 |
| switch-off-border | `--dk-color-switch-off-border` | `#868E96` | grey-500 |
| switch-on | `--dk-color-switch-on` | `#007936` | green-750 |
| switch-knob | `--dk-color-switch-knob` | `#FFFFFF` | white |
| btn2-bg | `--dk-color-btn2-bg` | `#FFFFFF` | white |
| btn2-text | `--dk-color-btn2-text` | `#222222` | ink-900 |
| btn2-border | `--dk-color-btn2-border` | `#222222` | ink-900 |
| btn2-hover-bg | `--dk-color-btn2-hover-bg` | `#F6F2EF` | stone-200 |
| step-active-bg | `--dk-color-step-active-bg` | `#007936` | green-750 |
| step-active-text | `--dk-color-step-active-text` | `#FFFFFF` | white |
| step-idle-border | `--dk-color-step-idle-border` | `#CED4DA` | grey-300 |
| step-idle-text | `--dk-color-step-idle-text` | `#666666` | ink-600 |
| step-done | `--dk-color-step-done` | `#007936` | green-750 |

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
| brown-800 | `--dk-brown-800` | `#5A4232` |
| brown-500 | `--dk-brown-500` | `#85654A` |
| sand-250 | `--dk-sand-250` | `#E1DAC9` |
| sand-225 | `--dk-sand-225` | `#F2EBDA` |
| wheat-200 | `--dk-wheat-200` | `#E6D3A0` |
| ink-900 | `--dk-ink-900` | `#222222` |
| ink-800 | `--dk-ink-800` | `#333333` |
| ink-600 | `--dk-ink-600` | `#666666` |
| grey-600 | `--dk-grey-600` | `#6C757D` |
| grey-500 | `--dk-grey-500` | `#868E96` |
| grey-400 | `--dk-grey-400` | `#ADB5BD` |
| grey-300 | `--dk-grey-300` | `#CED4DA` |
| grey-250 | `--dk-grey-250` | `#DDDDDD` |
| grey-200 | `--dk-grey-200` | `#E9E9E9` |
| grey-100 | `--dk-grey-100` | `#F5F5F5` |
| stone-100 | `--dk-stone-100` | `#F8F7F5` |
| stone-150 | `--dk-stone-150` | `#F8F4F1` |
| stone-200 | `--dk-stone-200` | `#F6F2EF` |
| ecru-100 | `--dk-ecru-100` | `#FDF8EC` |
| ecru-300 | `--dk-ecru-300` | `#F5ECD8` |
| ecru-400 | `--dk-ecru-400` | `#F0E6CF` |
| ecru-line | `--dk-ecru-line` | `#EADFC6` |
| ecru-line-strong | `--dk-ecru-line-strong` | `#DDD0B4` |
| green-900 | `--dk-green-900` | `#00642E` |
| green-750 | `--dk-green-750` | `#007936` |
| green-450 | `--dk-green-450` | `#47C33D` |
| yellow-450 | `--dk-yellow-450` | `#FFD821` |

## Kontrast (WCAG) - program

| Tekst | Tło | Kontrast | Minimum | Zastosowanie |
|---|---|---|---|---|
| text | bg | 15.91:1 | 4.5:1 | tekst na tle |
| text | surface | 14.86:1 | 4.5:1 | tekst na karcie |
| text-muted | bg | 5.74:1 | 4.5:1 | tekst pomocniczy na tle |
| text-muted | surface | 5.36:1 | 4.5:1 | tekst pomocniczy na karcie |
| label | surface-0 | 12.63:1 | 4.5:1 | etykieta na tle (od 1.6.0 >= 4.5) |
| label | surface-1 | 11.80:1 | 4.5:1 | etykieta na karcie (od 1.6.0 >= 4.5) |
| brand | bg | 5.54:1 | 4.5:1 | zielony tekst/link na tle |
| brand | brand-soft | 4.85:1 | 4.5:1 | zielony na jasnej zieleni |
| on-brand | brand | 5.54:1 | 4.5:1 | biały na zieleni |
| on-cta | cta | 11.44:1 | 4.5:1 | tekst na żółtym przycisku |
| on-inverse | inverse-bg | 15.91:1 | 4.5:1 | biały na brązie (toast) |
| on-inverse | danger | 5.91:1 | 4.5:1 | biały na czerwieni |
| danger | bg | 5.91:1 | 4.5:1 | czerwony tekst błędu na tle |
| danger | surface | 5.52:1 | 4.5:1 | czerwony tekst błędu na karcie |
| warning-text | warning-bg | 7.22:1 | 4.5:1 | ostrzeżenie |
| field-border | bg | 3.32:1 | 3.0:1 | ramka pola |
| switch-off-border | bg | 3.32:1 | 3.0:1 | obrys wyłączonego przełącznika |
| check-mark | check-bg | 5.54:1 | 4.5:1 | znak checkboxa/radio na jasnym wnętrzu |
| check-border | check-bg | 3.32:1 | 3.0:1 | obrys checkboxa na wnętrzu |
| check-border | surface-0 | 3.32:1 | 3.0:1 | obrys checkboxa na tle |
| check-border | surface-1 | 3.10:1 | 3.0:1 | obrys checkboxa na karcie |
| accent | surface-0 | 5.54:1 | 4.5:1 | akcent (link, tytuł) na L0 |
| accent | surface-1 | 5.18:1 | 4.5:1 | akcent na L1 |
| accent | surface-2 | 5.54:1 | 4.5:1 | akcent na L2 |
| accent | surface-3 | 5.23:1 | 4.5:1 | akcent na L3 |
| on-accent | accent | 5.54:1 | 4.5:1 | tekst na akcencie |
| step-active-text | step-active-bg | 5.54:1 | 4.5:1 | tekst aktywnego kroku |
| step-idle-text | surface-0 | 5.74:1 | 4.5:1 | tekst nieaktywnego kroku |
| btn2-text | btn2-bg | 15.91:1 | 4.5:1 | tekst przycisku drugorzędnego |
| btn2-text | btn2-hover-bg | 14.29:1 | 4.5:1 | tekst przycisku drugorzędnego (hover) |
| btn2-border | btn2-bg | 15.91:1 | 3.0:1 | obrys przycisku drugorzędnego |
| slider-fill | slider-track | 4.57:1 | 3.0:1 | wypełnienie suwaka na torze |
| slider-thumb-border | slider-thumb | 5.54:1 | 3.0:1 | obrys uchwytu suwaka |
| switch-on | surface-0 | 5.54:1 | 3.0:1 | włączony przełącznik na tle |
| switch-on | surface-1 | 5.18:1 | 3.0:1 | włączony przełącznik na karcie |
| switch-off-border | surface-0 | 3.32:1 | 3.0:1 | obrys wyłączonego przełącznika na tle |
| switch-knob | switch-on | 5.54:1 | 3.0:1 | gałka na włączonym torze |
| icon | icon-bg | 5.08:1 | 3.0:1 | ikona na kółku |
| focus | surface-0 | 5.54:1 | 3.0:1 | obrys fokusa |

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
| sm | `--dk-radius-sm` | `4px` |
| md | `--dk-radius-md` | `8px` |
| lg | `--dk-radius-lg` | `12px` |
| pill | `--dk-radius-pill` | `999px` |

## Cienie (podbarwione brązem)

| Nazwa | Zmienna CSS | Wartość |
|---|---|---|
| thumb | `--dk-shadow-thumb` | `0 1px 2px rgba(34,34,34,.14), 0 4px 10px rgba(34,34,34,.10)` |
| raised | `--dk-shadow-raised` | `0 1px 4px rgba(34,34,34,.16)` |
| bar | `--dk-shadow-bar` | `0 2px 8px rgba(34,34,34,.08)` |
| toast | `--dk-shadow-toast` | `0 10px 30px rgba(34,34,34,.22)` |
| focus-field | `--dk-shadow-focus-field` | `0 0 0 3px rgba(0,121,54,.22)` |

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
| focus-width | `--dk-control-focus-width` | `2px` |
| focus-offset | `--dk-control-focus-offset` | `2px` |
| stroke-icon | `--dk-control-stroke-icon` | `2` |
| check-size | `--dk-control-check-size` | `20px` |
| check-radius | `--dk-control-check-radius` | `4px` |
| check-border-width | `--dk-control-check-border-width` | `1.5px` |
| btn2-border-width | `--dk-control-btn2-border-width` | `1px` |
| slider-thumb-border-width | `--dk-control-slider-thumb-border-width` | `2px` |

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
| radius-card | `--dk-qt-radius-card` | `8px` |
| radius-field | `--dk-qt-radius-field` | `4px` |
| radius-btn | `--dk-qt-radius-btn` | `4px` |
| radius-drop | `--dk-qt-radius-drop` | `12px` |
