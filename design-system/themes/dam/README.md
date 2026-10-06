> **Stan 2.0.0 (06.10.2026):** ten plik opisuje szkic motywu sprzed 2.0.0. Wartości obowiązujące: `../../tokens/READY-2.0.0.txt` i wygenerowany plik motywu w tym katalogu (białe tło, szary panel, tekst #222222, zieleń #007936).

# Motyw „Dobra Kaloria” w DAM

Status: **szkic**. Wartości policzone i sprawdzone pod kątem kontrastu, ale motyw nie był jeszcze
wyświetlony w DAM. Wdraża go sesja pracująca w repo DAM, według jego własnego design systemu
(`bin/design-system/DESIGN_SYSTEM.md`) i jego łańcucha wydań.

Plik: `dam-theme-dobra-kaloria.css` (generowany). To nakładka na zmienne `--dam-*` pod selektorem
`html[data-theme="dobra-kaloria"]`, zbudowana tak samo jak istniejący motyw ciemny.

## Dlaczego nakładka, a nie przebudowa

DAM ma 93 zmienne `--dam-*`, z których korzystają wszystkie komponenty i nakładka na Geex. Motyw ciemny
już dziś działa przez podmianę tych zmiennych. Trzeci motyw idzie tą samą drogą: komponenty zostają,
motywy jasny i ciemny zostają, a nowy wygląd można włączyć, porównać na zrzutach i wyłączyć.

## Co nakładka zmienia

| Zmienna | Dziś (jasny) | Motyw Dobra Kaloria |
|---|---|---|
| `--dam-bg`, `--dam-surface-muted`, `--dam-sidebar-bg` | `#F6F7F6` | `#FDF8EC` (krem) |
| `--dam-surface-sunken` | `#F2F3F2` | `#FBF3E0` |
| `--dam-border`, `--dam-chrome` | `#E4E6E4` | `#EDE7DA` (piasek) |
| `--dam-text` | `#222222` | `#3B2A20` (ciemny brąz) |
| `--dam-text-muted` | `#6B6B6B` | `#7D5E44` |
| `--dam-shadow-rgb` | `34 34 34` | `59 42 32` (cień podbarwiony brązem) |
| `--dam-danger` | `#ff5b5b` | `#DA272D` |

## Czego nakładka celowo nie rusza

| Element | Powód |
|---|---|
| `--dam-primary` `#007936`, `--dam-brand-green` `#008244` | wzięte z realnego sklepu i z logo SVG; design system ma `#0F763E` - różnica do rozstrzygnięcia (DESIGN_SYSTEM.md, „Otwarte decyzje”) |
| czcionka Jost, skala 11-16 px | DAM to gęste narzędzie; Lato i Mindset to drugi etap |
| wysokości kontrolek, rytm paneli, sidebar | wymiary są dostrojone do list i tabel |
| `--dam-ok`, `--dam-warn`, `--info-color` | statusy mają własne znaczenie w DAM |

## Konflikt, o którym trzeba wiedzieć

W `dam-tokens.css` jest zapis: tło `#F6F7F6`, „not cream #FDF8EC”. To świadoma decyzja z wcześniejszej
pracy nad DAM. Motyw Dobra Kaloria wprowadza krem tylko u siebie, jasny motyw zostaje neutralny.
Jeśli krem ma zostać domyślnym wyglądem DAM, to jest decyzja usera, nie tej nakładki.

## Wdrożenie

1. Skopiuj `dam-theme-dobra-kaloria.css` obok `dam-tokens.css` i wczytaj po nim.
2. Dopisz trzecią wartość `dobra-kaloria` w przełączniku motywu. Nie czytałem kodu przełącznika:
   z komentarzy w `dam-tokens.css` wynika tylko, że motywy to `light` i `dark`, a kolory sidebara
   nadpisuje JS zależnie od schematu. Sprawdź oba miejsca, zanim zaczniesz.
3. Zrzuty „przed” i „po” list, kart, filtrów, modali i logowania w trzech motywach.
4. Drugi etap, po akceptacji kolorów: nagłówki Mindset, tekst Lato, odstępy `--dk-layout-*-sm`.
