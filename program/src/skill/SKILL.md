---
name: prezentacje
description: Tworzenie prezentacji PPTX marki Dobra Kaloria (Kubara) z folderu produktu (karty wprowadzenia, copy, Wizualizacje, Elementy, opcjonalnie badania) - jednym poleceniem szybka.py w ~25 s do sprawdzonego szkicu, potem dopracowanie. Też szablon 56 slajdów dla pracowników. Styl ze sklepu dobrakaloria.pl, kolory i czcionki motywu (globalne). Style - C "sklep" (ulubiony), B "odświeżona", A "klasyczna" (DK_WZÓR). Używaj, gdy user prosi o prezentację produktu / nowości / dla handlu / szablon / "zrób preskę", wskazuje folder w "D:\Marketing\- POLSKA\09 - PREZENTACJE\", albo wywołuje /prezentacje.
---

# /prezentacje - prezentacje Dobra Kaloria

**Zawsze razem z tym skillem wywołaj `ui-ux-pro-max:ui-ux-pro-max` i `uidesigner`** (polecenie usera). Bierzesz z
nich METODĘ: hierarchia, jedna myśl na slajd, liczba-bohater, kontrast AA, światło, pętla zrzut -> ocena -> poprawka.
Nie bierzesz ich wyglądu ani HTML - wynik to zawsze PPTX w stylu marki. Przy dopracowywaniu wyglądu: `ui-taste-reflect`.

**Najpierw przeczytaj `references/lekcje.md`** (decyzje usera + błędy, które już raz popełniłem - 5 minut, oszczędza godziny).

## 0. Program dla handlowców „Stwórz prezentację” (29.09.2026)

Ten skill jest silnikiem programu portable „Stwórz prezentację” (wersja 1.1.1; w oknie 60 typów slajdów w 7 grupach - 10 z danymi z folderu, 50 z szablonu przez `make_template.spec`; paczki bez smaku w nazwie pliku rozpoznaje `szybka.match_by_ocr` (OCR Windows); wygląd okna z design systemu: skill `ds-dobra-kaloria`, `tokens.css` kopiuje `build.ps1`; ekran „Gotowe” ma wybór czatu Claude / ChatGPT / Gemini: polecenie z całą treścią slajdów trafia do schowka i otwiera się czat). Układ u użytkownika: `Stwórz
prezentację.exe` (maleńki plik startowy C# z planszą „Uruchamiam…”) + `pliki programu\` (`program.exe` = okno
pywebview/WebView2, `stworz-cli.exe` = wiersz poleceń dla AI, biblioteki, `app\ui`, `app\skill`). Jedno źródło:
- kod programu: `D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt\WORK\` (src\app =
  silnik `engine.py`, okno `gui.py`, CLI `cli.py`; src\ui = HTML; src\launcher = plik startowy; src\skill = KOPIA
  tego skilla odświeżana przy budowie),
- budowa i wydanie: `WORK\build.ps1 [-Bump] [-Wydaj]` (PyInstaller + csc; `wydaj.ps1` kopiuje na M: i G:),
- testy spakowanego programu: `WORK\logs\e2e_gui.py` (Playwright przez CDP przeklikuje prawdziwe okno),
  `WORK\logs\launcher_test.ps1` (czasy planszy i okna),
- instrukcja dla AI: `AGENTS.md` obok programu (kopie na G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\… i M:).
Zmiana w skrypcie skilla = po `build.ps1` trafia do programu. Program NIC nie zapisuje do własnego folderu (dysk
sieciowy): cache blokady/placeholderów w `%LOCALAPPDATA%\Dobra Kaloria\Stworz prezentacje` (env `DK_GUARD_CACHE`,
`DK_CACHE_DIR`). Pułapka: kopia skilla w programie ≠ ten katalog - po ręcznej zmianie skilla odśwież (`build.ps1`).

## 1. Szybka ścieżka (domyślna)

```bash
python "%USERPROFILE%\.claude\skills\prezentacje\scripts\szybka.py" "<folder produktu>" --claimy "claim 1;claim 2;claim 3;claim 4"
```

W ~25 s robi wszystko, co wcześniej zajmowało godziny:
1. **Inwentarz** kart (nazwa, smaki z nazw plików, EAN, gramatura, % owoców, oświadczenia, wartości), copy, badania
   -> `_robocze\inwentarz.json`
2. **Mapa grafik**: packshot i elementy przypisane do smaków -> `_robocze\mapa_grafik.json` + `podglad_grafik.png`
3. **Grafiki**: tło wycinane automatycznie (alfa / czarne / białe / TIF), cache - powtórka nic nie liczy od nowa
4. **Szkic** `spec_B.json` + `spec_C.json` (okładka z 3 paczkami, claimy z ikonami, linia smaków, skład, karta
   każdego smaku, koniec). Istniejącego specu nie nadpisuje -> `szkic_*.json` i PPTX "(szkic)"
5. **Budowa + QA**: render, osadzenie fontów, test kolizji, plansze -> na końcu lista **DO DECYZJI**

**Twoja praca po uruchomieniu (w tej kolejności):**
1. `Read` na `podglad_grafik.png`. Packshot w złym wierszu (pliki bez nazwy smaku przypisuje po kolejności!) ->
   popraw `mapa_grafik.json`, ustaw `"recznie": true`, skasuj złe `_robocze\pack_*.png`, uruchom ponownie (~20 s).
2. `Read` na planszach `_robocze\qa\*.png`.
3. Uzupełnij, czego automat nie zrobi: **copy** (np. wyniki badania -> `section` + `segments`/`hero_stat`,
   liczby sprawdź w arkuszu), nazwy smaków z opakowania (np. "Cola lemon"), elementy dla smaków bez własnych.
   Edytuj `spec_*.json` (format: `references/spec-dk.md`) i buduj: `python scripts\build_dk.py spec_C.json`.
   Przy większych zmianach przenieś treść do `_robocze\make_specs.py` (jedno źródło dla A/B/C, wzór w `examples/`).
4. `qa_all.ps1 -Robocze <_robocze> -Only B,C` -> **"Tekst - problemy: 0"** na każdym pliku + obejrzane rendery.
5. Raport: co na slajdach, skąd liczby, braki, decyzje.

Tylko część kroków: `--tylko inwentarz|grafiki|szkic`; inne style: `--style C` / `--style B,C`; test bez ruszania
folderu usera: `--robocze <tmp> --wyjscie <tmp>`.

## 2. Wejście: folder produktu

| Źródło | Co z niego | Uwaga |
|---|---|---|
| `Karta wprowadzenia_*.xlsx` (1/SKU) | nazwa, oświadczenia, GTIN, gramatura, % owoców, wartości | **nigdy nie ma zdjęć produktu** |
| `Copy*.docx` / tekst w czacie | kanon treści - wstawiasz wiernie | liczby weryfikuj w arkuszu |
| Claimy od usera | slajd "co wyróżnia" | `--claimy` |
| `Wizualizacje\` | packshoty (PNG z alfą) | znak wodny "DEMO" -> zgłoś userowi |
| `Elementy\` | owoce, liście **i zdjęcia samego produktu** | produkt ZAWSZE stąd |
| Biblioteka marki `99 - WYMIANA\Krzysztof\--- Moj obszar pracy\Materiały  - Dobra kaloria - Brand - elemenety\Liście i owoce - warzywa` | brakujące owoce/liście | nie produkt (kulki kakaowe = inny produkt!) |
| `OMNIBUS*.xlsx` / badania | twarde dane dla handlu | dodatek |

## 3. Zasady treści i stylu (skrót - pełne w `references/styl-dk.md`)
- Handel = twarde dane podane przyjemnie; tytuł = wniosek; liczba ma źródło w stopce; bez wymyślania danych.
- Kolejność (wzór usera 29.09, `DK_KULKI z kreatyną.pptx`): okładka (3 paczki, "NOWOŚĆ") -> linia smaków -> co wyróżnia
  (ikony) -> skład (kafle) -> **claim + film** (`media`) -> **akapit edukacyjny** (`article`) -> przerywnik Badanie ->
  wyniki -> koniec. Karty smaków tylko na życzenie. Etykiety nad tytułem prawie nigdzie (lekcje A18-A25).
- **Film YouTube = miniatura + ▶ + podpis „Kliknij - film otworzy się na YouTube”, wszystko z linkiem** (user 29.09:
  „ktoś klika i się otwiera filmik, może być link”). Wideo online w PowerPoint daje błąd 153 YouTube - nie używamy
  (`online_video.ps1` zostaje tylko na wyraźne życzenie). Plik mp4 = osadzony film z rogami. Nigdy nie nazywaj
  obrazu z linkiem "filmem w slajdzie".
- Gdy mowa o całej linii: **3 paczki** (`"image": [p1, p2, p3]`). Bez porównań wygranych koncepcji.
- Wygląd = sklep dobrakaloria.pl: Mindset (nagłówki) + Lato (treść), zieleń, beż AD8767 dla etykiet, kremowe karty,
  ikony liniowe, metka ceny, znaczek NOWOŚĆ; bez kropek, bez plam za produktem, bez przycisków CTA; dużo światła.
- Kolory i czcionki tylko ze slotów motywu (zmiana globalna: Projektowanie > Warianty). Kolory smaków stałe.
- Morph tylko między kolejnymi slajdami tego samego układu (karty smaków). Szablon bez przejść.

| Styl | Builder | Plik |
|---|---|---|
| **nowy styl** (C sklep, domyślny) | `build_dk.py`, `"theme": "shop"` | `<PRODUKT> - nowy styl.pptx` |
| **stary styl** (A klasyczny DK_WZÓR) | `build_deck.py` | `<PRODUKT> - stary styl.pptx` |
| B odświeżona - **nie robimy** (user 29.09: "usuń wersję B, zostaw A i C") | `build_dk.py`, `"theme": "fresh"` | tylko na wyraźne życzenie |
| **Szablon** | `make_template.py "<katalog>"` | `PREZENTACJE\DK - szablon prezentacji.pptx` (60 slajdów, 9 sekcji, podpowiedzi w [nawiasach]) |

Szablon: jeden plik (motyw sklep). **Łatwa edycja** (`easy_edit()` w make_template, 29.09): każdy obiekt ma w Okienku
zaznaczenia nazwę-instrukcję ("Packshot - prawy klik: Zmień obraz"), paczka + owoce + cień = jedna grupa, pola
tekstowe = jeden akapit z "zmniejsz tekst przy przepełnieniu", 2 ukryte slajdy instrukcji (w tym film). Teksty wyłącznie podpowiedzi w [nawiasach], opis "do czego służy" w notatkach i na
karteczce poza kadrem, sekcje, instrukcja ukryta. Nowy typ slajdu = funkcja w `build_dk.py` + BUILDERS + wpis w
`make_template.py` z opisem.

## 3a. Typografia PL - ZAWSZE (polecenie usera 29.09: "nigdy nie zostawiamy na końcu spójników i jednych słów")
- **Zawieszki**: jednoliterowe spójniki/przyimki (a, i, o, u, w, z) nigdy na końcu linii - klejone do następnego słowa.
- **Sieroty / wdowy / bękarty**: ostatnia linia akapitu lub nagłówka nigdy nie jest jednym słowem (chyba że cały
  blok to kolumna po słowie w linii, np. wąski kafel "0% / DODATKU / CUKRU").
- **Myślnik** nie zaczyna linii (klejony do poprzedniego słowa).
- Jak to działa (nie ręcznie!): `build_deck.typo_tokens` / `wrap_lines` (łamanie Mindset i Lato w generatorze),
  `typo_nbsp` (twarde spacje U+00A0 w tekstach Lato - PowerPoint pilnuje też po edycji; **Mindset nie ma U+00A0**,
  więc nagłówki łamiemy sami), `build_dk.title_size` (max ~15% mniejsza czcionka, potem "po słowie w linii").
- **Dowód**: `verify.ps1` czyta FAKTYCZNE linie z PowerPointa (ZAWIESZKA / SIEROTA / MYŚLNIK) - wynik
  "Tekst - problemy: 0" jest warunkiem oddania. Ręczne łamanie w specu: `\n`.

## 4. Bezpieczeństwo (twarde)
- **Gdy user każe "edytuj istniejące / nie rób nowej wersji"**: kopia zapasowa, `guard.py record <plik>`, potem budowa
  w miejscu. Bez takiego polecenia: **nie nadpisuj ręcznych poprawek usera.** `guard.py` (w build_dk, build_deck, render.ps1) zapisze wynik jako
  "(nowa wersja)", gdy plik był edytowany lub jest otwarty. Nie obchodź tego. Ręczne poprawki usera = wzorzec: czytaj je.
- Pliki robocze w `_robocze\`. Nic nie kasuj rekurencyjnie; stare wersje przenoś do `_robocze\poprzednie wersje (data)`.
- Długie łatki w Pythonie pisz do pliku w scratchpadzie (Write), nie w heredoc bash.

## 5. W kolejce (od usera)
Film 15 s z dźwiękiem o 3 smakach (Magnific, Seedance) z `Elementy\`, do osadzenia (`"video"` w slajdzie `video`).

## 6. Pliki
```text
scripts/szybka.py          START: folder -> inwentarz, mapa grafik, grafiki, szkic, budowa, QA, lista DO DECYZJI
scripts/build_dk.py        B/C: 43 typy slajdów (spec-dk.md), motywy, sceny produktu, wykresy edytowalne, film
scripts/build_deck.py      A: styl klasyczny DK_WZÓR
scripts/make_template.py   szablon 56 slajdów
scripts/prep_images.py     cutout / cutout_dark / trim / tif / xlsx
scripts/qa_all.ps1         przebudowa + fonty + test kolizji wielu plików
scripts/verify.ps1         kontrola w PowerPoint: kolizje tekst/grafika/logo, przepełnienia, Morph, motyw, fonty
scripts/render.ps1         PPTX -> PNG (+ -EmbedFonts)      scripts/contact_sheet.py  plansza
scripts/guard.py           blokada nadpisania              scripts/make_icons.py     ikony Lucide -> PNG
assets/                    DK_WZOR.pptx, fonty, logo, ikony, demo (packshoty i elementy do szablonu)
references/lekcje.md       CZYTAJ NAJPIERW                 references/styl-dk.md     tokeny i zasady B/C
references/spec-dk.md      format spec B/C                 references/checklist.md   QA
references/design-system.md, spec-format.md                styl A
examples/kulki-kreatyna/   make_specs.py + specy A/B/C + podglądy (pełny, dopracowany przykład)
```
