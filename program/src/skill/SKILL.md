---
name: prezentacje
description: Tworzenie prezentacji PPTX marki Dobra Kaloria (Kubara) z folderu produktu (karty wprowadzenia, copy, Wizualizacje, Elementy, opcjonalnie badania) - jednym poleceniem szybka.py w ~25 s do sprawdzonego szkicu, potem dopracowanie. Też konwersja gotowej prezentacji .pptx na styl marki slajd w slajd (cele: zachowaj układ, rozwiń / dokończ, skróć) i szablon dla pracowników. Styl ze sklepu dobrakaloria.pl, kolory i czcionki motywu (globalne). Style - C "sklep" (ulubiony), B "odświeżona", A "klasyczna" (DK_WZÓR). Używaj, gdy user prosi o prezentację produktu / nowości / dla handlu / szablon / "zrób preskę", wskazuje folder w "D:\Marketing\- POLSKA\09 - PREZENTACJE\", wrzuca gotowy plik .pptx do przełożenia na nasz styl, dokończenia albo skrócenia, albo wywołuje /prezentacje.
---

# /prezentacje - prezentacje Dobra Kaloria

**Zawsze razem z tym skillem wywołaj `ui-ux-pro-max`** (w paczce: `skille/ui-ux-pro-max`; w pluginie `ui-ux-pro-max:ui-ux-pro-max`) **i, jeśli go masz, `uidesigner`** (polecenie usera). Bierzesz z
nich METODĘ: hierarchia, jedna myśl na slajd, liczba-bohater, kontrast AA, światło, pętla zrzut -> ocena -> poprawka.
Nie bierzesz ich wyglądu ani HTML - wynik to zawsze PPTX w stylu marki. Przy dopracowywaniu wyglądu: `ui-taste-reflect`.

**Najpierw przeczytaj `references/lekcje.md`** (decyzje usera + błędy, które już raz popełniłem - 5 minut, oszczędza godziny).
**Dopracowujesz prezentację po konwersji? Czytaj `references/dopracowanie.md` - w razie sprzeczności z innym plikiem wygrywa on.**

## 0. Program dla handlowców „Stwórz prezentację” (29.09.2026, zaktualizowane 13.10.2026)

Ten skill jest silnikiem programu portable „Stwórz prezentację” (stan od wersji wydanej 13.10.2026; w oknie typy slajdów w 7 grupach: sekcje z danymi z folderu i slajdy z pełnego szablonu przez `make_template.spec`, nazwy w `references/katalog-szablonu.md`; paczki bez smaku w nazwie pliku rozpoznaje `szybka.match_by_ocr` (OCR Windows); wygląd okna z design systemu: skill `ds-dobra-kaloria`, `tokens.css` kopiuje `build.ps1`). Układ u użytkownika (od 1.3, czysty wierzch): `Prezentacje.exe`
(maleńki plik startowy C# z planszą „Uruchamiam…”), `Prezentacje na Maca.dmg`, `DK - paczka prezentacji dla AI.zip` i folder `WORK\` z `pliki programu\` (`program.exe` = okno
pywebview/WebView2, `stworz-cli.exe` = wiersz poleceń dla AI, biblioteki, `app\ui`, `app\skill`). Jedno źródło:
- kod programu: `D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt\WORK\` (src\app =
  silnik `engine.py`, okno `gui.py`, CLI `cli.py`, samoaktualizacja `update.py`; src\ui = HTML; src\launcher = plik startowy;
  src\skill = KOPIA tego skilla odświeżana przy budowie),
- budowa i wydanie: `WORK\build.ps1 [-Bump] [-Wydaj]` (PyInstaller + csc; `wydaj.ps1` kopiuje na M: i G:); testy spakowanego
  programu: `WORK\logs\e2e_gui.py` (Playwright przez CDP przeklikuje prawdziwe okno), `WORK\logs\launcher_test.ps1` (czasy planszy i okna),
- instrukcja dla AI: `AGENTS.md` obok programu (kopie na G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\… i M:).
Okno od 1.1.9 (07.10.2026) to osobne kroki zamiast jednej strony ustawień: folder = Materiały, Styl, Dodatki, Slajdy; gotowa prezentacja = Przegląd, Cel, Rozdziały (`app.js`: `PANES`, `gotoPane`; testy okna klikają `#btn-next`, na końcu `#btn-build`).
Zmiana w skrypcie skilla = po `build.ps1` trafia do programu. Program NIC nie zapisuje do własnego folderu (dysk
sieciowy): cache blokady/placeholderów w `%LOCALAPPDATA%\Dobra Kaloria\Stworz prezentacje` (env `DK_GUARD_CACHE`,
`DK_CACHE_DIR`). Pułapka: kopia skilla w programie ≠ ten katalog - po ręcznej zmianie skilla odśwież (`build.ps1`).
**Tryb pptx: upuszczony / podany plik .pptx = konwersja gotowej prezentacji** (`scripts/pptx_convert.py`: `extract` -> `compose` -> `build_dk` -> `coverage`; `stworz-cli.exe "<plik.pptx>"` albo `python pptx_convert.py <plik.pptx>`): cała treść zostaje (długi tekst dzieli „(1/2)” tylko gdy się nie mieści), wynik `<nazwa> - nowy styl.pptx`, raport „Treść: 100% akapitów (N/N)”. Po konwersji program ostrzega o ewidentnych błędach tekstu źródła (`lint_tekst.py`), robi pętlę „oko” (pomiar zrzutów i inny wariant układu; `stworz-cli.exe --bez-oka` ją wyłącza; `konwersja-pptx.md` 2d), zapisuje plansze slajdów dla czatu w `<folder wyniku>\plansze` i daje DWA polecenia dla AI (teksty: `scripts/polecenia.py` - `POLECENIA`, `polecenie_ai(cel, dane, pliki)`, `tabela_ksztaltow`): dla czatu bez plików (przyciski Claude / ChatGPT / Gemini kopiują je do schowka i otwierają czat) i dla agenta z plikami (jedyny nowy element okna: link „Polecenie dla agenta z plikami”). To szkic, który AI dopracowuje według `references/dopracowanie.md`.
**Tryb dokument: plik .docx / .doc / .rtf / .odt / .pdf / .txt / .md = prezentacja z dokumentu** (`scripts/dokument.py`: `wczytaj` -> `statystyka` -> `zloz(m, {"slajdy": N, "rozdzialy": R})` -> `build_dk` -> `pokrycie`; CLI `python dokument.py <plik> [--slajdy N] [--rozdzialy N] [--wyjscie K] [--robocze K]`). Slajdy = streszczenie strukturalne (liczby, tabele skrócone, listy jako hasła), pełny tekst w notatkach prelegenta; pokrycie 100% w pliku (slajdy + notatki) dla każdej wartości suwaka; niczego nie wymyśla. Opis i ograniczenia: `references/z-dokumentu.md`.
**Tryb dopracowanie: plik już w stylu DK (szablon, wynik programu, deck z szablonu) nie jest konwertowany** - `pptx_convert.rozpoznaj(plik)` zwraca `tryb: "dopracowanie"`, `pptx_convert.przeglad(plik, rob)` daje listę błędów tekstu, podpowiedzi w [nawiasach] i uwagi; plik usera zostaje bez zmian. CLI bez `--mimo-to` wypisuje przegląd (kod 0); `--mimo-to` wymusza konwersję. Dopracowanie robi AI według `references/dopracowanie.md`.
**Zasada usera 13.10: program „funkcjonalny, ale nie przeładowany”** - żadnych nowych kroków, ekranów ani przełączników; nowe możliwości idą w automat i w polecenia dla AI (`lekcje.md` A53). Samoaktualizacja kopiuje też `skill-prezentacje` i `skill-ds-dobra-kaloria` do `WORK` i podmienia `DK - szablon prezentacji.pptx` tylko wtedy, gdy to niezmieniona stara wersja.

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

## 1b. Drugie wejście: gotowa prezentacja (.pptx) -> styl DK (06-13.10.2026)

User wrzuca SAM plik .pptx (stary / chaotyczny styl), bez folderu produktu. **Konwersja = ten sam slajd, te same słowa,
nowe role tekstu**: slajd N = slajd N (ta sama liczba slajdów), treść i kolejność 1:1, obrazy w całości, wyróżnienia
kolorem zostają. Zmienia się rola słów: **hasło** (Mindset), **dopisek** (Lato, krótki), **liczba-bohater**, **wniosek**
w pasie, **etykieta**, **punkt**; slajd ma być plakatem, nie kartką (user 13.10: „TAK! teraz ta prezentacja jest
cudownie piękna”). Układ bierzesz z katalogu szablonu (`references/katalog-szablonu.md`: kształt treści -> slajd
„tNN Nazwa”), nie z głowy. Bez dodanej agendy, przekładek, tytułów-wniosków, łączenia i dzielenia slajdów. Reguły
„tytuł = wniosek” i „jedna myśl na slajd” z pkt 3 dotyczą prezentacji z folderu produktu, NIE konwersji.

```powershell
python "$env:USERPROFILE\.claude\skills\prezentacje\scripts\pptx_convert.py" "<plik.pptx>" [--cel wiernie|rozwin|skroc]
```

- **Cel** (zapytaj, gdy user nie powiedział; domyślnie `wiernie`): `wiernie` = zachowaj układ; `rozwin` = baza do
  dokończenia (nowe slajdy oznaczone NOWY, treści slajdów oryginału nie zmieniasz); `skroc` = baza do skrócenia (**ukrywasz**,
  nigdy nie kasujesz). Co wolno w każdym celu: `references/konwersja-pptx.md` pkt 0.
- **Automat** (`pptx_convert.py`): układa slajd z pozycji pól (R0-R12, typ `uklad`), potem szablonuje (S1-S15,
  `szablonuj.py`: hasła, liczby-bohaterowie, pasy-wnioski, kafle z ikonami marki „W stylu DK”, etykiety `kv`; wzór
  z katalogu w `decyzje-szablon.json`, pole `wzor`), czyta zdjęcia-wypełnienia, składa kolaże, dokłada wizualizacje
  (`wizki.py`, tylko pewne), OSTRZEGA o ewidentnych błędach tekstu (`lint_tekst.py` -> `bledy_tekstu`; sam nie poprawia)
  i robi kontrole „Treść: 100% akapitów” oraz „Układ: …”. Reguły: `references/konwersja-pptx.md`.
- **Twoja część = dopracowanie** według `references/dopracowanie.md` (jedyny opis metody, tam też pętla i bramki).
  W skrócie: układ z katalogu szablonu; każda karta ma hasło w Mindset, a w kartach z tekstem więcej słów stoi w Mindset
  niż w Lato; najważniejsza liczba jest bohaterem, wniosek stoi w pasie; ewidentne błędy tekstu poprawiasz w granicach
  (spacja, najwyżej 2 znaki w słowie) i deklarujesz w specu w kluczu `poprawki`, wątpliwe idą do DO DECYZJI; gdy treść
  się nie mieści, upraszczasz układ, a nie zmniejszasz pisma ani nie kasujesz słów; poprawki robisz w specu, nie w PowerPoincie.
- **Bramki** (z dowodem; pierwsze trzy wypisuje jedno polecenie `pptx_convert.py … --ze-specu`, `dopracowanie.md` pkt 7-8): „Tekst - problemy: 0”;
  „Treść: 100% akapitów”; kontrola układu bez usterek; plansze par stary | nowy (`scripts/pary_slajdow.py`) obejrzane po ostatniej zmianie.
- **Program**: w oknie karta „Co zrobić z prezentacją”, w `stworz-cli.exe "<plik.pptx>" --cel …` (te same funkcje).
- **Test bez PowerPointa**: `python -m pytest -p no:cacheprovider scripts\test_konwersja.py -q` (reguły R / S na slajdach
  wzorcowych + `-k tabela` = regresja 4 prezentacji: treść 100%, `wiernosc` usterki i `znaki` puste, 43 = 43) oraz
  `test_ikony.py`, `test_lint.py`, `test_katalog.py`, `test_oko.py`, `test_polecenia.py`. Nowa reguła = nowy test z numerem slajdu.
- Prezentacji, która już jest w nowym stylu DK, nie konwertuj - wychodzi gorzej niż oryginał.
- Wyjątek od 1:1 tylko na życzenie: wstawki ze źródłem z researchu (`references/wstawki-z-researchu.md`).
Odrzucone przez usera: 07.10 wersja 57-slajdowa z przebudowaną treścią i wersje 1:1 z gołym tekstem; 13.10 sam tekst
Mindset na całą szerokość oraz zdania jako akapity Lato w kartach („za dużo czcionki Lato, za mało haseł”) - `lekcje.md` A33-A52.

## 1c. Bez programu: Mac, czat, Cowork (Droga B, 21.10.2026)

Brak `stworz-cli.exe` albo PowerPointa (Mac, claude.ai, Cowork - kod w maszynie z Linuksem, bez dysków sieciowych):
składasz prezentację ze slajdów `DK - szablon prezentacji - pełen.pptx` funkcjami `scripts/dk_szablon.py`
(`zloz`, `wpisz`, `pola`, `obraz`, `twarde`). **Przed oddaniem `sprawdz(prs, "assets/fonts")` musi być pusta** - pomiar
czcionkami Mindset i Lato; podgląd z LibreOffice kłamie (czcionka zastępcza + LibreOffice sam zmniejsza pismo w polach
z autodopasowaniem, PowerPoint nie). Render: PowerPoint, gdy jest; inaczej LibreOffice na kopii z `podglad()`.
Całość: `references/bez-programu.md`, lekcja A55. Model: Fable (Claude), Astra albo SOL (inne), wysokie myślenie.

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
  ikony marki „W stylu DK” (`assets/icons/dk`, zapas: liniowe Lucide), metka ceny, znaczek NOWOŚĆ; bez kropek, bez plam za produktem, bez przycisków CTA; dużo światła.
- Kolory i czcionki tylko ze slotów motywu (zmiana globalna: Projektowanie > Warianty). Kolory smaków stałe.
- Morph tylko między kolejnymi slajdami tego samego układu (karty smaków). Szablon bez przejść.

| Styl | Builder | Plik |
|---|---|---|
| **nowy styl** (C sklep, domyślny) | `build_dk.py`, `"theme": "shop"` | `<PRODUKT> - nowy styl.pptx` |
| **stary styl** (A klasyczny DK_WZÓR) | `build_deck.py` | `<PRODUKT> - stary styl.pptx` |
| B odświeżona - **nie robimy** (user 29.09: "usuń wersję B, zostaw A i C") | `build_dk.py`, `"theme": "fresh"` | tylko na wyraźne życzenie |
| **Szablon** | `make_template.py "<katalog>" [--krotki \| --pelny]` | dwa pliki: `PREZENTACJE\DK - szablon prezentacji.pptx` (KRÓTKI, 7 slajdów dla ludzi) i `DK - szablon prezentacji - pełen.pptx` (65 slajdów, 10 sekcji, dla programu i AI; podpowiedzi w [nawiasach]; co do czego: `references/katalog-szablonu.md`) |

Szablon: dwa pliki z jednego źródła (motyw sklep; user 13.10: „Skrócić… do maksymalnie 7 slajdów. I tylko po jednej opcji… program niech i tak korzysta z pełnej wersji, bo AI zrobi to lepiej”). Krótki (`spec_krotki`, `KROTKI_NR`: t04 Okładka: paczka na granicy zieleni, t17 Punkty, t22 Tekst i zdjęcie, t31 Zalety z ikonami i produktem, t62 Trzy fakty w kartach, t21 Porównanie: dziś i propozycja, t65 Zakończenie z podziękowaniem) leży w folderze PREZENTACJE i obok programu; pełny (`spec`) w `WORK\` programu i po buildzie w `pliki programu\`. **Łatwa edycja** (`easy_edit()` w make_template, 29.09): każdy obiekt ma w Okienku
zaznaczenia nazwę-instrukcję ("Packshot - prawy klik: Zmień obraz"), paczka + owoce + cień = jedna grupa, pola
tekstowe = jeden akapit z "zmniejsz tekst przy przepełnieniu", w pełnym 2 ukryte slajdy instrukcji (t01, t02; w tym film). Teksty wyłącznie podpowiedzi w [nawiasach], opis "do czego służy" w notatkach i na
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
scripts/build_dk.py        B/C: 49 typów slajdów w BUILDERS (spec-dk.md; `uklad` = konwersja 1:1 z kartami, kaflami, cytatem, obrazami), motywy, sceny produktu, wykresy edytowalne, film
scripts/pptx_convert.py    KONWERSJA gotowej prezentacji 1:1: extract -> compose (układ z pozycji, pojemnik z szablonu wg R0-R12, szablonowanie S1-S15, ostrzeżenia lint, `poprawki`, cele CELE) -> coverage + wiernosc (usterki, znaki)
scripts/szablonuj.py       reguły S1-S15: klocki szablonu (hasło, liczba-bohater, pas-wniosek, kafle z ikoną marki, kv), wzór z katalogu w decyzjach
scripts/lint_tekst.py      ostrzeżenia o ewidentnych błędach tekstu źródła (offline; słownik w assets/slownik/); oko.py: ocena PNG slajdu bez LLM (miary, kody usterek)
scripts/polecenia.py       teksty poleceń dla AI (agent z plikami / czat bez plików); katalog_md.py: references/katalog-szablonu.md z assets/katalog-szablonu.json
scripts/test_*.py          pytest bez PowerPointa: test_konwersja (R0-R12, S1-S15, tabela regresji `-k tabela -s`), test_ikony, test_lint, test_katalog, test_oko, test_polecenia
scripts/wizki.py           wizualizacje produktów z biblioteki 01 - PRODUKTY\- DK (dopasowanie linii, packshot, złożenie 2-3 paczek)
scripts/pary_slajdow.py    plansze par stary | nowy slajd - bramka oddania konwersji 1:1
scripts/dk_szablon.py      Droga B bez programu: zloz / wpisz / pola / obraz / twarde / sprawdz (pomiar Mindset+Lato) / podglad
scripts/build_deck.py      A: styl klasyczny DK_WZÓR
scripts/make_template.py   szablon: KRÓTKI 7 slajdów (`spec_krotki`) i PEŁNY 65 (`spec`; wpisy add(); wzory dla konwersji: t14 Jedno zdanie – teza, t17 Punkty, t20 Cytat, t36 Zalety w kaflach, t62 Trzy fakty w kartach; katalog: references/katalog-szablonu.md)
scripts/prep_images.py     cutout / cutout_dark / trim / tif / xlsx
scripts/qa_all.ps1         przebudowa + fonty + test kolizji wielu plików
scripts/verify.ps1         kontrola w PowerPoint: kolizje tekst/grafika/logo, przepełnienia, Morph, motyw, fonty
scripts/render.ps1         PPTX -> PNG (+ -EmbedFonts)      scripts/contact_sheet.py  plansza
scripts/guard.py           blokada nadpisania              scripts/make_icons.py     ikony marki / Lucide -> PNG
assets/                    DK_WZOR.pptx, fonty, logo, ikony, demo (packshoty i elementy do szablonu)
assets/icons/dk/           ikony marki „W stylu DK” (ok. 1000 PNG, 256 px; kolor w locie przez `build_dk.icon()`); icons/<kolor>/ = zapas Lucide
assets/ikony-slowa.json    słownik słowo -> ikona (S13); katalog-szablonu.json: 65 slajdów + tabela kształtów; slownik/: słownik polski dla lintu
assets/linie-aliasy.json   słownik: nazwa linii na slajdzie -> linia w bibliotece (ZAŁOŻENIE z 07.10, do potwierdzenia)
references/lekcje.md       CZYTAJ NAJPIERW                 references/styl-dk.md     tokeny i zasady B/C
references/dopracowanie.md metoda dopracowania po konwersji (WYGRYWA)  references/katalog-szablonu.md  kształt treści -> slajd
references/bez-programu.md Droga B (Mac, czat, Cowork): szablon + dk_szablon.py, pomiar zamiast podglądu
references/wstawki-z-researchu.md  research / audyt -> stopki źródeł, korekty i małe wstawki (paczka wstawki.json)
references/spec-dk.md      format spec B/C                 references/checklist.md   QA
references/design-system.md, spec-format.md                styl A
examples/kulki-kreatyna/   make_specs.py + specy A/B/C + podglądy (pełny, dopracowany przykład)
```
