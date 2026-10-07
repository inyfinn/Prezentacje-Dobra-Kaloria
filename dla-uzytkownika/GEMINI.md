# Stwórz prezentację — instrukcja dla Gemini (Gemini CLI, Gemini w Antigravity)

Jesteś Gemini — pracujesz w Gemini CLI, w Antigravity albo w czacie.
Zadanie: zrobić prezentację handlową marki Dobra Kaloria z **folderu produktu** albo z **gotowej prezentacji .pptx**
(przełożysz ją na styl marki — nic z niej nie ginie). **Nie zadawaj pytań** — czego nie wiesz, wpisz w raporcie jako
„DO DECYZJI”.

Ten plik leży w folderze programu `— SZABLON AI - skrypt` (dalej `<folder programu>`). Kopie folderu — użyj pierwszej,
która istnieje:

1. `G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\— SZABLON AI - skrypt`
2. `M:\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt`
3. `D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt`

Obok tego pliku: `pliki programu\stworz-cli.exe` (**wersja dla Ciebie**), `skill-prezentacje\` (skill `/prezentacje`),
`zainstaluj-skill.cmd` (instalator skilla), `Stwórz prezentację.exe` (okno dla ludzi — nie używaj).

## KROK 0 — skill `/prezentacje` (zrób najpierw)

Sprawdź, czy istnieje `%USERPROFILE%\.gemini\skills\prezentacje\SKILL.md`
(PowerShell: `Test-Path "$env:USERPROFILE\.gemini\skills\prezentacje\SKILL.md"`).

- **Jeśli nie:** `<folder programu>\zainstaluj-skill.cmd -Cel "%USERPROFILE%\.gemini\skills\prezentacje"`
  (w PowerShellu: `& "<folder programu>\zainstaluj-skill.cmd" -Cel "$env:USERPROFILE\.gemini\skills\prezentacje"`).
  Skrypt niczego nie kasuje — istniejącą wersję przenosi do `…\skills\_poprzednie\`. Sprawdź `Test-Path` jeszcze raz.
- **Potem** wczytaj skill `/prezentacje` (o ile narzędzie go widzi w tej sesji) i przeczytaj `references\lekcje.md`.
- **Nie masz mechanizmu skilli** (Gemini w Antigravity, czat) albo skill nie jest widoczny: nic nie instaluj —
  przeczytaj `<folder programu>\skill-prezentacje\SKILL.md` i `<folder programu>\skill-prezentacje\references\lekcje.md`
  jako instrukcję i pracuj według nich.

## KROK 1 — czekaj na materiał

Po kroku 0 napisz jedno zdanie („Skill gotowy. Podaj folder produktu albo plik .pptx.”) i **czekaj**. Nie zaczynaj bez
materiału.

- **Folder produktu** (`Karta wprowadzenia_*.xlsx`, copy, `Wizualizacje\`, `Elementy\`):
  `& "<folder programu>\pliki programu\stworz-cli.exe" "<folder produktu>"`
- **Plik .pptx** (gotowa prezentacja): `& "<folder programu>\pliki programu\stworz-cli.exe" "<plik.pptx>" --cel wiernie`
  — konwersja na styl Dobra Kaloria slajd w slajd, nic nie ginie. Cel wybierz po słowach użytkownika: `wiernie`
  („przełóż na nasz styl”; domyślnie), `rozwin` („dokończ”, „rozwiń”; puste slajdy z szablonu: `--dodaj t10,t58`),
  `skroc` („skróć”; `--sekcje r01,r02` = rozdziały widoczne, reszta zostaje jako slajdy ukryte; `--slajdy N`).

(cmd: to samo bez `&`.) Program pracuje 30–60 s, drukuje postęp i raport (ścieżka pliku, liczba slajdów, uwagi).
Opcje — domyślne wystarczą: `--styl nowy|stary`, `--dlugosc krotka|standard|pelna`, `--tekst mniej|standard|wiecej`,
`--film <link YouTube>`, `--claimy "A; B"`, `--packshoty "Smak=plik.png;…"` (pełna lista: `AGENTS.md` §3 albo
`stworz-cli.exe --help`). Folder bez kart wprowadzenia program odrzuca — powiedz użytkownikowi, czego brakuje.

## KROK 2 — po zbudowaniu (to Twoja praca)

1. **Obejrzyj każdy zrzut** `_robocze\qa\…\s01.png…` narzędziem do czytania obrazów — nie oceniaj po samym raporcie.
   Dla folderu produktu obejrzyj też `_robocze\podglad_grafik.png`: czy paczka pasuje do smaku (jeśli nie — ponów z
   `--packshoty`).
2. **Dopracuj treść** według `SKILL.md` i `references\lekcje.md` skilla: uzupełnij podpowiedzi w `[nawiasach]` danymi z
   folderu (każda liczba ma źródło w stopce). Dla pliku .pptx: sekcja „Konwersja gotowej prezentacji: jak dopracować wynik” niżej
   (jeśli nie ma `references\konwersja-pptx.md` w Twojej kopii skilla — `references\lekcje.md`, reguły A27–A44). Cel `wiernie`: slajd N = slajd N
   oryginału, te same teksty, kolejność i układ, obrazy w całości; bez własnych tytułów, agendy i przekładek. Cel
   `rozwin`: slajdów oryginału nie ruszasz, wypełniasz [nawiasy] na slajdach „NOWY” i proponujesz brakujące. Cel
   `skroc`: tylko **ukrywasz** slajdy (nic nie kasujesz); krótsza wersja slajdu to NOWY slajd, oryginał ukryty za nim.
   Edytuj python-pptx albo PowerPointem (COM); nie zmieniaj układu, kolorów ani czcionek.
3. **Kontrola** — oddajesz dopiero przy `Tekst - problemy: 0`:
   `powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\pliki programu\app\skill\scripts\verify.ps1" -Src "<wynik.pptx>"`
   Nowe zrzuty po poprawkach: `…\pliki programu\app\app\render_app.ps1 -Src "<wynik.pptx>" -Out "<katalog png>"`.

## Konwersja gotowej prezentacji: jak dopracować wynik

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

## Zasady

- **Nie pytaj, nie wymyślaj danych.** Czego nie ma w materiale, zostaje w `[nawiasach]` i trafia do „DO DECYZJI”.
- Folder produktu: tytuł slajdu = wniosek; jedna myśl na slajd (konwersja .pptx: nie - patrz sekcja o konwersji); liczby ze źródłem w stopce; packshoty ze znakiem „DEMO” trzeba podmienić
  przed wysłaniem na zewnątrz (zgłoś to).
- Nie nadpisuj ręcznych poprawek użytkownika: gdy plik był edytowany albo otwarty, program zapisze „… (nowa
  wersja).pptx” — nie obchodź tego. Nic nie kasuj rekurencyjnie.
- Zrzuty obejrzane (przy konwersji: plansze par) + `Tekst - problemy: 0` = warunek oddania. Bez tego nie pisz „gotowe”.

## Raport na koniec (po polsku)

Ścieżka pliku i liczba slajdów · wynik kontroli (`Tekst - problemy: 0`) · co uzupełniłeś i skąd liczby · lista
**DO DECYZJI** (braki, niepewne dopasowania grafik, znak DEMO, literówki źródła).

## Jeśli nie możesz uruchamiać programów

Powiedz użytkownikowi wprost: „Otwórz folder `— SZABLON AI - skrypt` na dysku G: i uruchom **Stwórz prezentację.exe**,
potem upuść folder produktu (albo plik .pptx) do okna.” Program zrobi resztę bez pytań.

## Dla czatu bez dostępu do dysku

Użytkownik klika w programie na ekranie **Gotowe** „Kopiuj polecenie” i wkleja je do czatu — dostajesz pełną treść
slajdów i dopracowujesz ją według zasad z tego pliku oraz z polecenia (`SKILL.md` i `references\lekcje.md` — jeśli masz
do nich dostęp).
