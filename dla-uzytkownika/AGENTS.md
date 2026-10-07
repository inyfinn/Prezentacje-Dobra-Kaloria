# Stwórz prezentację — instrukcja dla AI

**KROK 0 (zawsze pierwszy).** Sprawdź, czy masz skill `/prezentacje`: plik `%USERPROFILE%\.claude\skills\prezentacje\SKILL.md`
(Claude Code; Codex: `%USERPROFILE%\.codex\skills\prezentacje`, Gemini: `%USERPROFILE%\.gemini\skills\prezentacje`,
Cursor: `%USERPROFILE%\.cursor\skills\prezentacje`). Jeśli go nie ma, zainstaluj: uruchom `zainstaluj-skill.cmd` z folderu
programu (obok tego pliku; opcjonalnie `-Cel "<katalog skilli Twojego agenta>"`) albo skopiuj folder `skill-prezentacje\`
(też obok tego pliku) w to miejsce. Potem wczytaj skill i pracuj według niego (konwersja PPTX:
`references/konwersja-pptx.md`).

Jesteś asystentem AI (Claude, GPT/Codex, Gemini, Antigravity, Cursor…). Twoje zadanie: **zrobić prezentację
handlową marki Dobra Kaloria z folderu produktu**, którego ścieżkę podał użytkownik. **Nie zadawaj pytań** —
działaj według tej instrukcji; wszystko, czego nie wiesz, wpisz na końcu w raporcie jako „do decyzji”.

## 1. Gdzie jest program

Ten plik leży w folderze programu. Obok niego:

- `Stwórz prezentację.exe` — okno dla ludzi (nie używaj z AI),
- `pliki programu\stworz-cli.exe` — **wersja dla Ciebie** (wiersz poleceń, drukuje postęp i raport).

Kopie folderu programu (użyj pierwszej, która istnieje):

1. `G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\— SZABLON AI - skrypt`
2. `M:\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt`
3. `D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt`

Program jest przenośny — niczego nie instaluje i nie kopiuje; uruchamiaj go prosto z tej lokalizacji.

## 2. Co to jest folder produktu

Folder z materiałami jednego produktu, np. `…\24.09.2026 - KULKI z kreatyną`. Program rozpoznaje:

| Plik / podfolder | Co z niego bierze |
|---|---|
| `Karta wprowadzenia_*.xlsx` (jedna na smak) | nazwa, smaki, EAN, gramatura, % owoców, oświadczenia, wartości odżywcze |
| pliki Word / txt (`Copy...`, `Tekst...`) | akapity tekstu o produkcie |
| pliki Word / txt (`Badanie...`, `Dane...`, `Analiza...`) | liczby i notatki z badań |
| plik Word o innej nazwie | program ocenia po treści: większość akapitów z procentami = badanie, inaczej copy |
| `Wizualizacje\` | packshoty (PNG) |
| `Elementy\` | owoce, kulki, listki dorysowywane wokół paczki |
| inne `*.xlsx` (np. OMNIBUS) | nazwa badania do stopki źródła |

Bez kart wprowadzenia program odmawia — wtedy powiedz użytkownikowi, czego brakuje. Gdy użytkownik podał gotową
prezentację (plik `.pptx`), a nie folder produktu, użyj trybu konwersji z sekcji „Konwersja gotowej prezentacji”.

## 3. Zrób prezentację (jedno polecenie)

PowerShell:

```powershell
& "G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\— SZABLON AI - skrypt\pliki programu\stworz-cli.exe" "<folder produktu>"
```

cmd: to samo bez `&`. Program pracuje ok. 30–60 s i wypisuje postęp `[ 37%] Przygotowuję grafiki (12/44)`.

Opcje (wszystkie mają sensowne wartości domyślne):

| Opcja | Wartości | Domyślnie |
|---|---|---|
| `--styl` | `nowy` (styl sklepu dobrakaloria.pl) / `stary` (klasyczny) | `nowy` |
| `--dlugosc` | `krotka` (~6 slajdów) / `standard` (~9) / `pelna` (~13) | `standard` |
| `--tekst` | `mniej` / `standard` / `wiecej` | `standard` |
| `--sekcje` | lista po przecinku: `okladka,smaki,wyroznia,sklad,wartosci,karty_smakow,copy,badanie,film,koniec` | wg `--dlugosc` |
| `--film` | link YouTube (włącza slajd z filmem) | brak |
| `--claimy` | `"Claim 1; Claim 2 – opis"` (zamiast oświadczeń z kart) | z kart |
| `--packshoty` | `"Arbuz=plik.png;Cola=plik2.png"` — ręczne przypisanie packshotów do smaków | po nazwie pliku, inaczej po kolejności |
| `--wyjscie` | katalog na PPTX | folder produktu |
| `--bez-qa` | pomiń PowerPoint (czcionki, zrzuty, kontrola) | — |
| `--json` | pełny raport JSON na końcu | — |
| `--tylko-analiza` | tylko pokaż, co program znalazł | — |

Wynik:

- `<folder produktu>\<Produkt> - nowy styl.pptx` (albo `- stary styl.pptx`),
- `<folder produktu>\_robocze\raport.json` — ścieżka pliku, liczba slajdów, wynik kontroli, uwagi,
- `<folder produktu>\_robocze\qa\<nazwa>\s01.png…` — zrzuty każdego slajdu (jeśli jest PowerPoint),
- `<folder produktu>\_robocze\spec_program.json` — układ slajdów, z którego powstał plik.

Jeśli plik o tej nazwie był otwarty albo zmieniony ręcznie, program zapisze `… (nowa wersja).pptx` i powie o tym.

## 3a. Konwersja gotowej prezentacji (.pptx)

Użytkownik podał **plik** `.pptx` (albo `.ppsx`), a nie folder produktu? Program przełoży go na styl Dobra Kaloria
**slajd w slajd** (slajd N wyniku = slajd N oryginału: te same teksty, kolejność i układ) i nie pominie żadnej informacji:

```powershell
& "G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\— SZABLON AI - skrypt\pliki programu\stworz-cli.exe" "<plik.pptx>" --cel wiernie
```

**Cel** wybierz po słowach użytkownika (nie pytaj; gdy nic nie powiedział - `wiernie`):

| `--cel` | Kiedy | Co robi program | Co robisz Ty potem |
|---|---|---|---|
| `wiernie` (domyślnie) | „przełóż na nasz styl”, „popraw wygląd” | ten sam slajd w nowym wyglądzie | tylko czytelność: rozmiar pisma, łamanie wierszy, podpis przy właściwym obrazie. Bez własnych tytułów, agendy, przekładek, łączenia i dzielenia slajdów |
| `rozwin` | „dokończ”, „rozwiń”, „dopisz” | to samo + puste slajdy z szablonu (`--dodaj t10,t58`), wstawione przed zakończeniem, w notatkach „NOWY” | wypełniasz [nawiasy] treścią wynikającą z prezentacji, proponujesz brakujące slajdy (miejsce, typ, tekst) oznaczone NOWY. Slajdów oryginału nie ruszasz, liczb nie wymyślasz |
| `skroc` | „skróć”, „wersja na 15 minut” | to samo; rozdziały spoza `--sekcje` zostają jako slajdy **ukryte**; `--slajdy N` = ile ma zostać w pokazie | **ukrywasz** slajdy, nigdy nie kasujesz. Krótszą wersję albo połączenie dwóch slajdów robisz jako NOWY slajd, oryginały ukrywasz tuż za nim; na końcu lista „Co ukryte i gdzie jest oryginał” |

| Opcja | Znaczenie |
|---|---|
| `--sekcje r01,r02,...` | rozdziały widoczne w pokazie (id z `--tylko-analiza`); pozostałe **zostają w pliku jako slajdy ukryte** (nic nie znika). Domyślnie wszystkie widoczne |
| `--slajdy N` | cel `skroc`: docelowa liczba slajdów w pokazie (trafia do polecenia dla AI) |
| `--dodaj t10,t58,...` | cel `rozwin`: puste slajdy z szablonu do dołożenia (lista id: `--tylko-analiza`) |
| `--bez-wizualizacji` | nie dokładaj packshotów z biblioteki produktów na slajdach portfolio |
| `--wyjscie <katalog>` | gdzie zapisać wynik (domyślnie obok pliku źródłowego) |
| `--tylko-analiza` | pokaż, co program znalazł: slajdy, akapity, grafiki, tabele, wykresy, rozdziały, bibliotekę wizualizacji |
| `--bez-qa`, `--json` | jak przy folderze produktu |

Wynik: `<nazwa pliku> - nowy styl.pptx` (cel `rozwin`: `… - nowy styl - rozwinięta.pptx`, `skroc`: `… - nowy styl -
skrót.pptx`) obok źródła; raport i zrzuty w `<folder pliku>\_robocze\<nazwa pliku>\` (`raport.json`, `qa\...\s01.png`,
`spec_program.json`, `img\` z obrazami z oryginału, `wielkosc-liter.txt`). Plik źródłowy nie jest zmieniany.

**Co program gwarantuje.** Czyta wszystko: teksty (także w grupach i SmartArt), tabele, wykresy (zostają edytowalne),
obrazy w całości (także zdjęcia wstawione jako wypełnienie kształtu - eksport z Canvy; obrazy nachodzące na siebie
składa w jeden kolaż), hiperłącza, notatki prelegenta, sekcje. Tekst leżący obok slajdu (poza kadrem) przenosi do
notatek. Układ bierze z pozycji pól na starym slajdzie: kolumny zostają kolumnami, drobne etykiety pod kolumną zostają
osobnymi znacznikami, słowa wyróżnione kolorem zostają wyróżnione. Slajd dzieli tylko wtedy, gdy tekst nie mieści się
pismem 13 pt, i pisze o tym. Literówek nie poprawia. Gdy oryginał wyświetla wersaliki, ustawia zwykłą wielkość liter
i wypisuje zmiany w `wielkosc-liter.txt`. Pomija tylko logo i belki stojące w tym samym miejscu na większości slajdów,
drobne ozdobniki oraz animacje i tła (mówi o tym w uwagach). Stary styl nie jest dostępny dla konwersji.

**Dwie kontrole na końcu - obie muszą być czyste, inaczej nie oddawaj:**
- `Treść: 100% akapitów (N/N) przeniesionych` - są wszystkie słowa;
- `Układ: osobne napisy X z X, kolejność góra-dół bez zmian, liczby X z X, slajdów tyle samo (N)` - osobne napisy są
  osobno, to, co stało wyżej, nadal jest wyżej, są wszystkie liczby.

**Wizualizacje.** Na slajdach portfolio (kolumny z nazwami linii, tytuł „Kulki”, „Batony”…) program dokłada gotowe
packshoty z biblioteki `01 - PRODUKTY\- DK` - tylko gdy każda kolumna ma pewne dopasowanie - i wypisuje, które produkty
wstawił. Pokaż tę listę użytkownikowi: słownik nazw linii (`skill-prezentacje\assets\linie-aliasy.json`) to założenie.

Twoja część po konwersji (pary stary | nowy, poprawki, kontrola, lista „DO DECYZJI”): sekcja 3b niżej.

## 3b. Konwersja gotowej prezentacji: jak dopracować wynik

Program robi **szkic** (ten sam slajd w stylu marki, 100% treści). Dopracowujesz go Ty - a o firmie nic nie wiesz, więc
oto skąd brać wiedzę, według czego oceniać i czego nie wolno ruszać. **Dobra Kaloria** = polska marka przekąsek (kulki,
batony…); jej prezentacje to deck handlowy i strategiczny, a wzorem wyglądu jest sklep dobrakaloria.pl.

**Skąd wiedza (czytaj, nie zgaduj).** (1) Skill `/prezentacje` (KROK 0): `SKILL.md` sekcje 0 i 1b, `references\konwersja-pptx.md`
(zasady, pułapki, kroki), `references\lekcje.md` A27-A44 (decyzje właściciela) - kopia zawsze leży w
`<folder programu>\skill-prezentacje\`. (2) Design system: `%USERPROFILE%\.claude\skills\ds-dobra-kaloria\DESIGN-SYSTEM-DOBRA-KALORIA.md`
(§2 zasady, §5.4 prezentacje PPTX); **nie masz go** (to osobny skill, program nie kopiuje go w całości) - wystarczy 10 reguł
niżej. (3) Wzorzec układów: `DK - szablon prezentacji.pptx` obok programu (60 typów slajdów; format opisu: `references\spec-dk.md`).

**10 reguł stylu Dobra Kaloria w prezentacji.**

1. Tło slajdu **białe**; bieli jest najwięcej. Beż, ecru i szary nigdy jako tło całego slajdu.
2. **Kremowy** (ecru `#FDF8EC`) tylko jako karta albo kafel na bieli. Głębiej niż karta w karcie nie schodzisz.
3. **Mindset** (nagłówkowa, wersaliki) tylko na tytuł i krótkie hasło (ok. do 12 słów).
4. **Lato** na zdania i akapity. Zdanie wielkimi literami Mindset jest nieczytelne - to częsty błąd.
5. Tekst ciemny z motywu (nie czysta czerń); drobne podpisy i etykiety w beżu motywu.
6. **Zieleń marki** `#007936` (w motywie PPTX: slot Akcent 1) na tytuły, kropki, metki. Czerwień motywu to tylko akcent
   i wyróżnione słowo - jeśli było wyróżnione w oryginale.
7. **Żółty** `#FFD821` to jedna wyróżniona akcja na widok; w konwersji zwykle wcale.
8. **Bez obrysów** wokół kart, kafli i tagów (karta = wypełnienie). Ikony liniowe, zielone. Zero plam i bąbelków za produktem.
9. Kolory i czcionki **tylko ze slotów motywu** (Projektowanie > Warianty), bez własnych kodów hex; kolory smaków produktu to wyjątek.
10. **1:1** (niżej): slajd to ten sam slajd, tylko w nowym wyglądzie.

**Zasada 1:1 (lekcje A33-A35).** Slajd N wyniku = slajd N oryginału: ta sama liczba slajdów, te same teksty i kolejność góra-dół,
kolumny zostają kolumnami, osobny napis („Zmiana nazwy”, „Segment 1 & 3”, źródło) zostaje osobnym elementem, obrazy w całości
(bez kadrowania - ucina tekst na zrzucie). Priorytety właściciela: 1) nie zgubić żadnej danej, 2) sens, 3) kolejność,
4) kontekst, 5) dopiero wygląd. Właściciel porównuje dwa okna obok siebie, slajd po slajdzie. Cel (`wiernie`/`rozwin`/`skroc`):
tabela wyżej / w KROKU 1.

**Dobór pojemnika z szablonu po kształcie treści** (reguły silnika R0-R12, projekt 07.10; sprawdzasz, czy automat wybrał
dobry pojemnik, a przy ręcznej poprawce w specu `uklad` bierzesz go z tej tabeli; tekstu nie zmieniasz):

| Kształt treści na starym slajdzie | Pojemnik (typ z szablonu) |
|---|---|
| pierwszy slajd z samym tekstem / ostatni z `#…` / jedno hasło >= 54 pt | okładka tekstowa / zakończenie / przekładka ciemna (bez numeru) |
| 2-4 kolumny (pola i obrazy obok siebie) | kolumny z kartami (s34, s46, s21), obraz w całości |
| 2-8 krótkich pozycji (<= 36 znaków, bez kropki, lista) | kafle `chips` (s36), **zawsze zielone**; wiodący myślnik „–” listy to marker (jak punktor): kafle go nie mają, zapis w `pokrycie.json` jako `markery` (nie w `znaki`). Dłuższe lub > 8: punkty z kropką marki (s17); 2-4 punkty: środek slajdu, pismo do 32 pt |
| cytat: zdanie + `(Autor Nazwisko)` albo „…” i krótka linijka autora pod spodem | cytat (s20): cudzysłów, kursywa Lato, autor pogrubiony |
| 1-4 wiersze dużego pisma (>= 28 pt), same hasła | jedna karta z hasłem na środku (s14 w karcie) |
| 2-4 podobne jednostki dużego pisma (<= 22 słowa, podobna długość) | 2-4 karty obok siebie (s21); „Prefiks - reszta” = nagłówek zielony/czerwony + hasło. 3+ karty z „rwanym” tekstem (krótkie wiersze Lato), którym nie pomaga mniejsze pismo, układają się **jedna pod drugą** na pełną szerokość - to nie błąd |
| akapity zdań (> 22 słów lub nierówne) | jedna karta na całą szerokość (s16), nagłówek przed nią wchodzi do karty |
| pole dużego pisma, w którym >= 50% słów to zdania (>= 13 słów albo >= 8 + kropka) | Lato, nie Mindset |
| etykiety `CT:` / `TA:` / `Insight:` | goły wiersz pod kartami, osobno (nie w karcie) |
| krótkie hasło (<= 12 słów lub kończące się „:”) przed listą / obrazami | goły zielony nagłówek nad pojemnikiem |
| podpis-wniosek pod obrazami, hasło po kartach | osobny wiersz pod spodem; „Źródło:” małym pismem |
| hiperłącze na słowach (np. „Byron Sharp”) | zostaje na tych samych słowach, **bez dopisanej stopki „Link: …”**; adres, którego nie ma na slajdzie, idzie do notatek |
| tekst nie mieści się w pojemniku | zostaje stary układ + wpis na listę „Sprawdź najpierw”; tekstu nie skracasz |

**Bramka oddania - dowód, nie raport.** (1) Render oryginału i wyniku do PNG, pojedynczo (PowerPoint COM nie lubi dwóch naraz):
`powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\pliki programu\app\app\render_app.ps1" -Src "<plik.pptx>" -Out "<katalog png>"`.
(2) **Plansze par** stary | nowy: `python "<folder programu>\pliki programu\app\skill\scripts\pary_slajdow.py" <png oryginału> <png wyniku> <katalog>`
(3 pary na planszę; różna liczba slajdów = błąd). (3) Obejrzyj **każdą planszę** narzędziem do czytania obrazów, najpierw slajdy
z listy „Sprawdź najpierw”: ten sam slajd? te same teksty i kolejność? nic nie ucięte? podpis przy swoim obrazie? (4) Poprawki
w `_robocze\<nazwa>\spec_konwersja.json` (albo `spec_program.json`), potem `python "<folder programu>\pliki programu\app\skill\scripts\build_dk.py" <spec>`.
(5) `verify.ps1` (sekcja 4 pkt 4): **`Tekst - problemy: 0`**. (6) Raport programu: `Treść: 100%` i `Układ: … slajdów tyle samo (N)` czyste.
Bez par obejrzanych i bez tych wyników nie pisz „gotowe”.

**Czego nie wolno (to odrzucił właściciel 07.10).** Dodawać agendę, przekładki, numery rozdziałów; pisać własne tytuły-wnioski;
wyjmować liczby ze zdań do kafli KPI; łączyć, dzielić, przestawiać, kasować slajdy; dopisywać treść; przycinać obrazy; zmieniać
kolory i czcionki; zastępować zrzut z tekstem przepisanym tekstem. Zasady „tytuł = wniosek” i „jedna myśl na slajd” dotyczą
prezentacji budowanych z folderu produktu, **nie konwersji**. Prezentacji, która już jest w stylu DK, nie konwertuj.

**Lista „DO DECYZJI” dla człowieka (zawsze na końcu raportu).** Literówki źródła (oczywiste popraw i wypisz: było -> jest; niejasne zostaw i zgłoś) ·
zmiany wielkości liter z `wielkosc-liter.txt` · wstawione wizualizacje produktów (słownik nazw linii to założenie) ·
slajdy z listy „Sprawdź najpierw” i te, gdzie karty się nie zmieściły · slajdy podzielone, ukryte lub NOWE (ukryte zostają
w pliku - przed wysłaniem poza firmę trzeba je usunąć albo zapisać PDF) · niejasne dane i [nawiasy] bez źródła · znak „DEMO”.

## 4. Po zbudowaniu — Twoja część pracy

0. **Packshoty do smaków.** Gdy pliki w `Wizualizacje\` nie mają w nazwie smaku, program przypisuje je po kolejności
   i pisze o tym w uwagach. Otwórz `_robocze\podglad_grafik.png` (obraz), sprawdź, czy paczka pasuje do smaku
   (kolor, napis na paczce). Jeśli nie — uruchom ponownie z `--packshoty "Smak=plik.png;…"`.
1. **Obejrzyj każdy zrzut** z `_robocze\qa\…` (narzędziem do czytania obrazów). Nie oceniaj po samym raporcie.
2. **Uzupełnij podpowiedzi w `[nawiasach]`** (np. liczby z badania) danymi z folderu. Każda liczba ma źródło.
   Edytuj plik przez python-pptx (`pip install python-pptx`) albo PowerPoint (COM). Nie zmieniaj układu, kolorów
   ani czcionek — kolory i czcionki są w motywie, teksty w polach tekstowych.
3. **Nie wymyślaj danych.** Czego nie ma w folderze, zostaw w `[nawiasach]` i wpisz do raportu.
4. **Sprawdź ponownie** (kontrola tekstu w PowerPoint: kolizje, krawędzie, typografia PL — sieroty, zawieszki):

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\pliki programu\app\skill\scripts\verify.ps1" -Src "<plik.pptx>"
   ```

   Oddajesz dopiero przy `Tekst - problemy: 0`. Nowe zrzuty:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\pliki programu\app\app\render_app.ps1" -Src "<plik.pptx>" -Out "<katalog png>"
   ```

5. Zasady treści (skrót; dla prezentacji z folderu produktu, **nie** dla konwersji .pptx - tam sekcja 3b): tytuł slajdu = wniosek, nie temat; jeden slajd = jedna myśl; liczby ze źródłem w stopce;
   bez porównań koncepcji opakowań; zero plam/bąbelków za produktem; packshoty ze znakiem „DEMO” trzeba podmienić
   przed wysłaniem na zewnątrz (zgłoś to użytkownikowi).

## 5. Jeśli nie możesz uruchamiać programów na komputerze użytkownika

Powiedz użytkownikowi wprost: „Otwórz folder `— SZABLON AI - skrypt` na dysku G: i uruchom
**Stwórz prezentację.exe**, potem upuść folder produktu do okna.” Program zrobi resztę bez pytań.

## 6. Raport na koniec (dla użytkownika, po polsku)

- ścieżka gotowego pliku i liczba slajdów,
- wynik kontroli (`Tekst - problemy: 0`),
- co uzupełniłeś i skąd wziąłeś liczby,
- lista rzeczy do decyzji użytkownika (braki, niepewne dopasowania grafik, znak wodny DEMO).
