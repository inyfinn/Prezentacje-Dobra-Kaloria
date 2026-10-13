# Konwersja gotowej prezentacji -> styl Dobra Kaloria (rewizja 13.10.2026: automat 1:1 + cele + szablonowanie + błędy tekstu)

Przypadek wzorcowy: `PREZENTACJE\06.10.2026 - strategia\DK_co_dalej_update.pptx` (43 slajdy) ->
`DK_co_dalej_update - nowy styl.pptx` (**43 slajdy**, `verify` 0 problemów). Wzór ręcznego specu:
`...\06.10.2026 - strategia\_robocze\make_spec.py` (user 07.10 13:40 usunął `_robocze`; wzorem jest teraz sam automat,
pkt 2a). Decyzje usera: `lekcje.md` A27-A52. Błędy i przyczyny: `lekcje.md` D.

**Ten plik opisuje, co robi AUTOMAT i jak go sprawdzić. Dopracowanie wyniku przez agenta AI (hasła, liczby, wnioski, układ
z katalogu, poprawki tekstu, pętla, bramki) opisuje JEDEN dokument: `dopracowanie.md`; w razie sprzeczności wygrywa on.**

> Pierwsza wersja (06.10) przebudowała treść: 57 slajdów, dodana agenda i przekładki, tytuły-wnioski, liczby przerobione
> na osobne kafle KPI (dziś liczba-bohater tylko POWTARZA liczbę nad jej niezmienionym zdaniem: `dopracowanie.md` pkt 2). User ją **odrzucił** (07.10): „kompletnie pomyliłeś teksty… Nie trzymałeś się tekstów w slajdzie
> i kolejności… przerobiłeś prezentację w zły sposób… Staraj się trzymać układu ze starej prezentacji”.
> User porównuje dwa okna PowerPointa obok siebie, slajd N ze slajdem N. Od 07.10 tak samo robi automat.

## 0. Cel konwersji (zapytaj albo przyjmij „zachowaj układ”)

User 07.10: „nie zawsze ma to sens, czasem chcemy dokończyć prezentację, rozwinąć ją albo skrócić. To też powinno
być dostępne jako opcja”. Baza jest ZAWSZE ta sama (slajd w slajd, nic nie ginie); cel zmienia to, co wolno potem.
Jedno źródło nazw i zasad: `pptx_convert.CELE` (czyta je program, wiersz poleceń i ten dokument).

| Cel (`--cel`) | Co robi automat | Co wolno Tobie (AI) potem | Czego nie wolno |
|---|---|---|---|
| `wiernie` „Zachowaj układ” (domyślny) | ten sam slajd w nowym wyglądzie: układ po kształcie treści, hasła, liczby-bohaterowie, pasy-wnioski, ikony marki (pkt 2a-2b) | dopracować według `dopracowanie.md`: układ z katalogu szablonu, hasła, liczby, wnioski w pasie; poprawić czytelność (łamanie, podpis przy właściwym obrazie) i ewidentne błędy tekstu w granicach, z listą „było -> jest” w kluczu `poprawki` (pkt 2c) | własne tytuły i hasła, agenda, przekładki, łączenie i dzielenie slajdów, przestawianie, dopisywanie i skracanie treści |
| `rozwin` „Rozwiń / dokończ” | baza + puste slajdy z szablonu (`--dodaj t10,t58`) wstawione PRZED zakończeniem, w notatkach „NOWY” | slajdy oryginału dopracować jak w `wiernie`; wypełnić [nawiasy] treścią wynikającą z prezentacji; zaproponować brakujące slajdy (miejsce, slajd z katalogu szablonu, tekst), każdy oznaczony NOWY | zmieniać treść slajdów oryginału (ich wygląd dopracowujesz jak w `wiernie`); wymyślać liczby i fakty (czego nie ma w materiałach, zostaje w [nawiasach]) |
| `skroc` „Skróć” | baza; rozdziały spoza `--sekcje` zostają w pliku jako slajdy UKRYTE | slajdy oryginału dopracować jak w `wiernie`; ukrywać slajdy; krótszą wersję albo połączenie dwóch slajdów robić jako NOWY slajd, a oryginały ukryć tuż za nim (pełny tekst także do notatek nowego slajdu); lista „Co ukryte i gdzie jest oryginał” | kasować slajdy albo tekst; zmieniać liczby, nazwy, sens |

**Jedna reguła we wszystkich celach:** rozdział wyłączony w `--sekcje` (w oknie: przełącznik) to slajdy ukryte, nigdy
usunięte. Priorytet nr 1 usera: „NAJ, NAJWAŻNIEJSZE, to nie zgubić danych”. Ukryte slajdy nadal są w pliku: przed
wysłaniem poza firmę trzeba je usunąć albo zapisać PDF (automat przypomina o tym w uwagach).

## 1. Zasada bazy: ten sam slajd, nowy wygląd

| Zostaje bez zmian | Zmienia się |
|---|---|
| liczba i kolejność slajdów (slajd N = slajd N) | tło, czcionki (Mindset / Lato), kolory motywu, karty, metki |
| teksty na slajdzie (te same słowa, ta sama kolejność góra-dół) | role tekstu (hasło, dopisek, liczba-bohater, wniosek, etykieta, punkt: `dopracowanie.md` pkt 1); rozmiar pisma (sam się dopasowuje) |
| podział na osobne elementy (kolumny, etykiety, stos haseł) i łamania wierszy autora w hasłach | pojemnik: układ z katalogu szablonu dobrany do kształtu treści (karty, kafle, pas-wniosek), wyrównanie i odstępy |
| osobne elementy osobno („Zmiana nazwy”, „Segment 1 & 3”, źródło, komentarz autora) | forma: znacznik, metka, drobny podpis |
| obrazy w całości, w tym samym porządku; kolaż zostaje kolażem | zaokrąglone rogi, podpisy pod obrazem |
| wyróżnienie pojedynczych słów kolorem (czerwone / zielone słowa w haśle) | odcień: czerwień = akcent, inny kolor = zieleń marki |

Wolno: ujednolicić wielkość liter tam, gdzie źródło wyświetla wersaliki; dołożyć wizualizacje produktów na slajdach
portfolio (pkt 3); poprawić ewidentne błędy tekstu (pkt 2c). Slajd dzieli tylko automat (drabina awaryjna, oznaczenie „(1/2)”),
gdy tekst nie mieści się pismem 13 pt, i mówi o tym w uwagach; agent slajdów nie dzieli - zgłasza je do DO DECYZJI (`dopracowanie.md` pkt 6).
Priorytety usera (A32): 1) nie zgubić żadnej danej, 2) sens, 3) kolejność góra-dół, 4) kontekst, 5) dopiero wygląd.

## 2. Automat: `scripts/pptx_convert.py`

```powershell
$S = "$env:USERPROFILE\.claude\skills\prezentacje\scripts"
python "$S\pptx_convert.py" "<plik.pptx>" [--cel wiernie|rozwin|skroc] [--sekcje r01,r02] [--slajdy N]
       [--bez-wizualizacji] [--bez-szablonowania] [--wyjscie <katalog>] [--robocze <katalog>] [--bez-qa]
       [--poprawki <poprawki.json>] [--ze-specu <spec_konwersja.json>]
```

Program „Stwórz prezentację” woła te same funkcje (`extract`, `compose`, `coverage`, `wiernosc`); w oknie cel
wybiera się kartą, w `stworz-cli.exe` flagą `--cel` (dodatkowo `--dodaj t10,t58` dla pustych slajdów z szablonu).

**Jak automat czyta slajd** (`compose` -> `_uklad`, niczego nie odgaduje, przenosi pozycje):

| Na starym slajdzie | W nowym (typ `uklad`, format: `spec-dk.md`) |
|---|---|
| belka u góry (tekst w górnych 22% wysokości) | `title`; gdy pod belką stoi krótka etykieta slajdu („Kulki”, „Dane wejściowe”, do 4 słów): belka = `kicker`, etykieta = `title` |
| pierwszy wiersz pola zakończony „?” albo „:” | `title`, reszta pola idzie dalej |
| jedno duże hasło (>= 54 pt, do 6 słów), bez obrazów | `section` z belką jako `label`, **bez numeru** |
| pierwszy slajd z samym tekstem / ostatni z hashtagiem | `cover_text` / `end` |
| pola tekstu i obrazy w tym samym paśmie poziomym, obok siebie | wiersz `cols`: kolumna = bloki w kolejności góra-dół (`h` nagłówek, `lead` hasło, `p` opis, `img` obraz, `small` podpis) |
| krótkie etykiety pod kolumną, drobnym pismem | **osobne elementy**: ostatnie pasmo = `meta` (zielona metka na dole karty), przedostatnie = `tag` (czerwony znacznik) |
| krótkie hasła w rzędach (np. 3 + 2) albo lista z myślnikami | wiersz `chips` (`per_row` jak w źródle), bez myślnika na początku |
| duże pismo (>= 28 pt), krótko | `lead` / `h` / `big` z łamaniami autora; pismo dobrane tak, żeby wiersz autora nie złamał się drugi raz |
| mały tekst, krótko (opisy, podpisy) | `p` z akapitami autora; długi tekst (>= 180 znaków, pełne wiersze) = proza: zdania sklejone, układane na nowo |
| słowa w innym kolorze | `wyr`: znak na słowo (`a` akcent, `i` zieleń marki); całe pole czerwone = `color: accent`, całe w innym kolorze = `h` |
| obrazy obok siebie / siatka 2 x 2 / jeden pod drugim | `pics` (rząd = rząd; stos pojedynczych obrazów staje obok siebie; duży zrzut + małe = `layout: "1+siatka"`) |
| obrazy nachodzące na siebie (kolaż, paczka z owocami) | jedna grafika złożona w ich układzie (`sNN_kolazK.png`) |
| zdjęcie jako wypełnienie kształtu (Canva, Google Slides) | zwykły obraz (do 07.10 takie zdjęcia ginęły bez śladu) |
| tekst albo obraz leżący obok slajdu (poza kadrem) | notatki prelegenta, z dopiskiem „[Obok slajdu w oryginale]” |
| obraz stojący w tym samym miejscu na większości slajdów (logo, belka) | pomijany wszędzie; packshot powtarzany w różnych miejscach zostaje |
| tabela, wykres | `table`, `columns` (wykres edytowalny) |

**Drabina awaryjna** (nigdy utrata treści): układ z pozycji -> siatka obrazów z podpisami przy najbliższym obrazie
(slajd-kolaż, >= 3 obrazy) -> zwykłe wiersze w kolejności oryginału -> podział na „(1/2)”. Każdy szczebel poniżej
pierwszego trafia na listę **„Sprawdź najpierw slajdy…”** w uwagach - od nich zaczynaj przegląd.

**Wielkość liter.** Tylko pola, które źródło wyświetla wersalikami (czcionka Mindset / Bebas albo `cap="all"`):
słowa wpisane WERSALIKAMI idą małymi, poza skrótami (bez samogłosek, z cyfrą, z listy `SKROTY`, krótkie w wierszu
z małymi literami: WHO, FDA) i słowami chronionymi (w pliku stoją w środku wiersza z wielkiej litery). Wiersz po
kropce albo po liczbie zaczyna się wielką literą, wiersz-kontynuacja małą. Lista zmian: `<rob>\wielkosc-liter.txt`.
W pozostałych plikach tekst zostaje znak w znak. Błędów tekstu (literówek, sklejonych słów) automat nie poprawia, tylko ostrzega (pkt 2c).

**Dwie kontrole** (obie w raporcie, obie muszą być czyste):
- `coverage` „Treść: 100% akapitów” - czy są wszystkie słowa (to worek słów: nie widzi kolejności ani sklejenia);
- `wiernosc` „Układ: osobne napisy X z X, kolejność góra-dół bez zmian, liczby X z X, slajdów tyle samo” - czy każdy
  krótki, osobny napis źródła jest osobnym elementem, czy pole stojące wyżej nadal jest wyżej, czy są wszystkie liczby.
  Stary automat dostaje tu usterkę „napis »Segment 1 & 3« nie jest osobnym elementem”, a pokrycie pokazywał 100%.

## 2a. Etap 1 - dobór pojemnika z szablonu po KSZTAŁCIE treści (07.10.2026, runda 2-3; role tekstu nadaje etap 2, pkt 2b)

Werdykt usera 07.10 o dwóch wersjach (ręcznej 08:15 i programu 13:12): „slajdy 6, 7 i zdecydowana większość dalej
kompletnie źle. Nie korzystałeś z naszego szablonu. Brzydkie. Po slajdzie 5 dramat.” Przyczyna na planszach trójek
(oryginał | ręczna | program): każde pole >= 28 pt szło jako wielkie hasło Mindset wersalikami na całą szerokość,
akapity gołym Lato bez karty, kremowe tło całego slajdu losowo (s07, s13, s26, s29), a karty / kafle / cytaty / kolumny
z szablonu `DK - szablon prezentacji.pptx` (wtedy 60 slajdów, dziś 65: `katalog-szablonu.md`) nie były używane poza s05 i s14.
User chce, żeby **program** (nie ręka) robił to dobrze - dla ludzi, którzy niczego nie poprawiają.

**Zasada: tekst 1:1, zmienia się tylko pojemnik.** Te same słowa, ta sama kolejność góra-dół, liczby w swoich
zdaniach, kolory słów, obrazy w całości, 43 = 43 (A33-A35, A41-A42). Automat dobiera do kształtu treści **typ pojemnika
z szablonu** (karta, kafle, cytat, kolumny, punkty), nigdy nie zmienia treści. Etap 1 (R0-R12) dobiera pojemnik i tymczasowo
rozróżnia pismo (zdanie = Lato, hasło = Mindset); hasła, dopiski, liczby i wnioski nadaje etap 2 (pkt 2b, S1-S15) według `dopracowanie.md` pkt 1. Tło zawsze białe (`paper`), krem tylko w kartach. Kod: `pptx_convert._uklad` i funkcje
`_tryb`, `_hasla_grupy`, `_karty6`, `_cytaty`, `_kolumny`, `_specjalny`; rysuje `build_dk.s_uklad` (wiersze `cols` z
kartami, `chips`, `quote`, `pics`, `sub`, `b`). Spec: `spec-dk.md`, typ `uklad`.

Oznaczenia w tabeli i niżej: `sNN` = slajd prezentacji strategii (źródło przykładów i testów), `tNN Nazwa` = slajd szablonu (nazwy: `katalog-szablonu.md`).

| # | Kształt treści na starym slajdzie (warunek) | Typ pojemnika (wzór w szablonie) | Pola |
|---|---|---|---|
| R0 | każdy slajd `uklad`, zawsze | tło `paper`, karty kremowe; hasło > 4 słów max 36 pt; akapit pocięty Enterem autora sklejony w prozie kart (bez zmiany słów; twarde łamanie zostaje tylko w haśle Mindset i w pozycji listy); wielkość liter po łamaniu: wiersz po wierszu bez `.!?:` zaczyna się małą (słowo po kropce nie jest „chronione”, s26 „ale”), po `.!?:` albo po wierszu kończącym się hiperłączem - wielką i jako osobny akapit (s41 „Dla segmentu…”) | `bg` nigdy `card`; każda zmiana liter w `wielkosc-liter.txt` |
| R-ZD | pole >= 28 pt bez znaczników listy; grupa = zdanie, gdy >= 13 słów albo kończy się `.!…` i ma >= 8 słów (`?` nie liczy się); zdania >= 50% słów pola | pismo w etapie 1: zdanie (proza) = tymczasowo `p` (Lato), hasło = `lead` / `h` / `sub` (Mindset); wejście do R4-R7. Etap 2 (S14) zamienia potem każde zdanie w karcie na hasło Mindset + krótki dopisek Lato | tylko pismo, treść bez zmian |
| R1 | pierwszy slajd z samym tekstem / ostatni z `#…` / jedno duże hasło | `cover_text` / `end` / `section` (belka = `label`, bez numeru) | jak w pkt 2 |
| R2 | pasmo poziome z 2-4 klastrami x (pola i obrazy obok siebie) | wiersz `cols`: karty obok siebie (t34 Linia produktów / t46 Karty ze zdjęciem / t21 Porównanie: dziś i propozycja); `card=False`, gdy w kolumnie jest obraz | `h`, `p`/`lead`, `img` w całości, `tag`, `meta` |
| R3 | lista krótkich pozycji: >= 3 wiersze po <= 6 słów bez `.!?;:` pod pytaniem / dwukropkiem, albo w kolumnie pod `h`, albo z myślnikami; wiersz od „oraz / lub / albo” dokleja się do poprzedniego | `chips` (t36 Zalety w zielonych kaflach) przy 2-8 pozycjach <= 36 znaków; inaczej punkty z kropką marki (t17 Punkty, `b`, `li`); w kolumnie blok `p` z „• ” | pozycje 1:1, tytuł = zabrany 1. wiersz; wiodący myślnik listy = marker (jak punktor): kafle go nie mają, zawsze zielone (s09), marker w pokryciu jako `markery`, nie w `znaki`; kafle jednej kolumny równej szerokości |
| R4 | cytat: wiersz kończy się nawiasem z >= 2 słowami wielką literą, albo fragment w „…” i następny wiersz <= 6 słów bez `.!?:` | wiersz `quote` jak t20 Cytat / opinia (30 pt kursywa Lato kolor tekstu, zielona kreska, autor bold 16 pt kolor tekstu); tytuł i belka slajdu zostają | `t` = cytat, `author` = reszta wiersza z nawiasem („(Byron Sharp, Ehrenberg-Bass).”, hiperłącze zostaje) |
| R5 | 1-4 kolejne wiersze Mindset (po R-ZD) z pól >= 28 pt, nie lista, nie wstęp (R9), nie wniosek (R10b) | **jedna karta** kremowa na białym, wyśrodkowana (t14 Jedno zdanie – teza w karcie) | bloki = wiersze w kolejności, `k`/`color`/`wyr` bez zmian, pad 2 cm, min 6 cm |
| R6 | 2-4 jednostki (pole = jednostka albo wiersz = jednostka), każda <= 22 słów, długości max/min <= 2.5, pt max/min <= 1.15, żadna od „=”, „+”, „pod / oraz / i / a / ale / lub / albo / czyli / bo”, żadna z `:` na końcu | **2-4 równe karty obok siebie** (t21 Porównanie: dziś i propozycja bez „lepszej” zielonej / t19 Kroki / proces bez numerów); R6a: każda „prefiks – reszta” -> `h` = prefiks z separatorem („Dobra wiadomość –” zieleń / „Zła wiadomość –” czerwień), `lead` = reszta; karty obok siebie mają zawsze równą wysokość, krótsza treść od góry (s22) | 1 karta = 1 jednostka, lewa-prawa = góra-dół; Lato w jednej = Lato we wszystkich |
| R7 | ciąg z choć jednym wierszem Lato, który nie przeszedł R6, albo pole < 28 pt z >= 20 słów / >= 2 wierszy; R7b: samotny nagłówek Mindset <= 6 słów albo wiersz z `:` tuż przed -> pierwszy blok `h` karty | **karta z akapitami** na całą szerokość (wzór t16 Akapit w karcie); po S14 każdy akapit dostaje hasło Mindset + dopisek (`dopracowanie.md` pkt 6), a karta z samym Lato zostaje tylko jako wyjątek z `dopracowanie.md` pkt 3 (zdanie dłuższe niż 24 słowa bez granicy; w katalogu: kształt „akapit do czytania”, t61 Akapit w karcie z wyróżnieniem) | akapity 1:1 (`li` -> „• ”), `wyr` z kolorów źródła, pad 1 cm, jeden rozmiar pisma w karcie (s41 >= 14 pt); dwie grupy rozdzielone nagłówkiem = dwie karty jedna pod drugą; samotny krótki wiersz < 20 słów zostaje gołym `p` |
| R8 | wiersz od `CT:`, `TA:`, `Insight:` | goły wiersz `h` do lewej (jak s14) - przerywa ciąg R5-R7 | `t` bez zmian |
| R9 | samotny wiersz Mindset <= 12 słów (albo z `:`) tuż PRZED `chips` / `pics` / `cols` z R2 | goły wiersz `h` zieleń, środek („Tytuł listy” z t17 Punkty) | `t` bez zmian |
| R10 | (a) podpis-wniosek pod obrazami: pole >= 24 pt albo całe w kolorze (poza „Źródło:” = `small`); (b) samotny wiersz Mindset <= 12 słów tuż PO kartach R6/R7 | (a) `sub` Mindset 26 pod `pics` (wyśrodkowany względem rzędu obrazów, nie slajdu), kolor `accent` gdy całe czerwone, inaczej `brand`; (b) goły wiersz | `t` bez zmian |
| R11 | obrazy | `pics` (t28 Galeria 3 zdjęć / t26 Zdjęcie na cały slajd z podpisem), bez kadrowania (`_contain_pic`); rząd rozpięty od brzegu do brzegu kart (s34) | items w kolejności źródła, `layout: "1+siatka"` |
| R12 | po R3-R10 | bramka mieszczenia: nowe wiersze tylko gdy `_miesci()`; inaczej stare wiersze + wpis „Sprawdź najpierw”; dalej drabina z pkt 2; 43 = 43 | `ctx['sprawdz']` |

Karty z `kont=True` pomija `_wizualizacje` (inaczej „Dobra wiadomość” szłoby do biblioteki packshotów).

**Poprawki progów, runda 4 (10.10.2026):** pad karty-pojemnika nie rośnie z pismem (3-4 karty: 0,6 cm, 2 karty: 1,2 cm,
karta z akapitami R7: 1,0 cm zamiast 1,6-1,9); karty z „rwanym” Lato (średnie wypełnienie wierszy < 82% albo wiersz < 60% pola,
przy 3-4 kartach także < 3,5 słowa w wierszu) dostają do 30% mniejsze pismo, a gdy nie pomaga - 3+ karty układają się jedna
pod drugą na pełną szerokość (`_ocena`: kara 8; s18, s21, s40); komentarz pod kartami nie większy niż tekst kart + 2 pt;
krótka lista (2-4 punkty) idzie na środek slajdu pismem do 32 pt (s02); obraz z białym brzegiem dostaje ramkę 0,75 pt
`#DDDDDD` (`border` z DS, s34).

**Przykłady z `DK_co_dalej_update.pptx`** (rendery par: `v5\pary\para_*.png`):
- **s06** - dwa pola 32 pt „DOBRA wiadomość – rynek zdrowych przekąsek rośnie” / „ZŁA wiadomość – rośniemy wolniej niż
  sam rynek”. Było: dwa wielkie hasła Mindset jedno pod drugim na kremowym tle. Jest (R6 + R6a): dwie równe karty
  obok siebie, nagłówek „Dobra wiadomość –” zielony / „Zła wiadomość –” czerwony, reszta Mindset; te same słowa.
- **s07** - cytat „Brands grow through constant exposure to new buyers (Byron Sharp, Ehrenberg-Bass).” z hiperłączem
  i pod nim 3 wiersze: „Produkt: jasno zdefiniowany”, „Potrzeba, grupa docelowa, okazja”, „= Rozwiązanie produktowe”.
  Było: wszystko wersalikami na całą szerokość. Jest (R4 + R5): wiersz `quote` (kursywa Lato, autor bold z nawiasem,
  hiperłącze na „Byron Sharp”) + jedna karta-hasło z 3 liniami; „= Rozwiązanie” nie staje się osobną kartą (zaczyna się od „=”).
- **s14** - dwie kolumny „Młodzi | Starsi” z etykietami „Insight:”, „CT: … / TA: …”. Wzorzec zaakceptowany przez usera
  wcześniej (R2 + R8): dwie karty + etykiety jako gołe wiersze `h` do lewej - nie ruszać.

**Jak sprawdzić** (żadnej z trzech kontroli nie pomijaj):
1. `python scripts\pary_slajdow.py <png oryginału> <png wyniku> <katalog>` i `Read` każdej planszy „stary | nowy”:
   ten sam slajd, te same słowa, ta sama kolejność, obrazy w całości, każdy slajd ma pojemnik z szablonu (karta / kafle /
   cytat / kolumny), żaden goły akapit Mindset na całą szerokość, żadne kremowe tło całego slajdu.
2. `verify.ps1`: „Tekst - problemy: 0”, liczba slajdów, bez wyjątku COM; raport automatu: „Treść: 100%”, `wiernosc`
   usterki = [] i **`znaki` = []** (żaden nawias, myślnik, kropka ani cudzysłów ze źródła nie zniknął; `pokrycie.json`).
3. `python -m pytest scripts\test_konwersja.py -q` (bez PowerPointa i modeli AI, ok. 45 s): testy jednostkowe reguł
   (R-ZD progi słów, s06 dwie karty, s07 cytat 30 pt + karta, s14 CT/TA, s09 zielone kafle bez myślnika, s22 karty równej
   wysokości, s18/s21/s40 linie nie rwane, s26 „ale”, s41 osobny akapit i jeden rozmiar, s38 podpis pod środkiem rzędu,
   s34 rząd do brzegów, s43 środek) i tabela regresji `-k tabela -s` na 4 prezentacjach (co_dalej 43->43, DATESY 16->16,
   KULKI 9->9, onlien 50->57 - dzieli długie slajdy instrukcji szablonu, 152 usterki to placeholdery w [nawiasach]):
   treść brakuje 0, znaki 0, slajdów tyle samo, „gołych” slajdów `uklad` (same `lead`/`h`/`p`) 0% w co_dalej.
   Każda nowa reguła = nowy test z numerem slajdu.

## 2b. Etap 2 - szablonowanie: goły tekst -> klocki szablonu (13.10.2026, `scripts/szablonuj.py`)

User 13.10 o wyniku programu 1.2.0: „dalej wygląda okropnie… tekst jednolity, bez sensownych akapitów, podnagłówków, widać,
że to nie jest z szablonu… slajd 9: zielone napisy i zielone przyciski, źle się to czyta”. Kierownik dopracował
prezentację strategii ręcznie na nowych klockach buildera (`hero`, `icon`, `kv`, `bars`, `li`, wiersz `band`, karta
`fill: brand`; kontrakt: docstring `build_dk.s_uklad` i `spec-dk.md`), a automat robi to samo regułami S1-S15. Krok
działa w `compose` po `_pojemniki` i `_czysc`, na wierszach `uklad` jednego slajdu (`pptx_convert._szablonuj` -> `szablonuj.stosuj`
-> `szablonuj.rozloz`). **Twarde:** żadne słowo nie znika, nie dochodzi i nie zmienia kolejności (jedyny jawny wyjątek:
`hero` powtarza liczbę, która stoi w zdaniu pod nią); po każdym slajdzie `szablonuj.slowa()` porównuje zestawy słów, a slajd,
który zmienił zestaw albo po zmianie się nie mieści (`_miesci`), zostaje taki, jaki był (wpis w uwagach). Wyłączenie:
`--bez-szablonowania` / `opts["szablonuj"] = False`. Decyzje na slajd: `<rob>\decyzje-szablon.json` i klucz `szablon` specu.
Gdy karty z klockami po układzie mają pismo < 15 pt, krok próbuje wariantu bez ikon na kartach (S14h) i bierze lepszy.

| # | Wzorzec | Warunek (deterministyczny) | Wynik | Slajdy wzorca | Wzór z katalogu |
|---|---|---|---|---|---|
| S1 | wniosek-pas | (a) wiersz `sub` pod `pics`; (b) wiersz z `po_kartach`; (c) ostatni blok karty (karta ma >= 2 bloki) cały w kolorze (`color: accent` albo `wyr` bez „-”) i <= 14 słów; (d) ostatnia linia od „=”; (e) ostatnie zdanie ostatniej karty / ostatnia karta-zdanie zaczyna się od znacznika `Ale `, `Ważna kwestia`, `Insight:`, `Wniosek`, `Temat do`, `Dlatego`, `Czyli` i ma <= 14 słów; (f) jedyna karta z 1 akapitem o 2 zdaniach, drugie <= 12 słów; (g) ostatni akapit karty z >= 3 akapitami, od „Dla / Zatem / Podsumowując / Wniosek”, <= 20 słów; goły wiersz „Insight: …” | wiersz `band`; `fill: accent`, gdy wniosek jest czerwonym podpisem pod obrazami albo zawiera „ślepy zaułek / odjechał / zła wiadomość / zagroż”, inaczej `brand`; „Insight:” dostaje `icon: lightbulb` | 7, 10, 12, 14, 18, 24, 25, 26, 36, 37, 38, 40, 41 | t62 Trzy fakty w kartach (pas pod kartami); t63 Zrzuty w całości i wniosek; t60 Cytat i wniosek |
| S2 | fakt-z-liczba | 2-4 karty obok siebie (albo 2-4 akapity jednej karty), każda <= 45 słów, w co najmniej jednej liczba z jednostką `\d[\d,.]*\s?(%\|mln\|mld\|tys.\|zł\|g/kg\|kg\|g\|lat)` (także „21–22 mln”, „+11%”, „3,8 mld zł”; rok i liczby porządkowe nie liczą się) | karty OBOK siebie; blok `hero` z liczbą (pierwsza wyróżniona `wyr`, inaczej pierwsza z jednostką, „z X do Y” = Y; stoi dosłownie w HAŚLE karty, S14d; karta z nagłówkiem-liczbą „11 g” już ją ma) nad hasłem; karta bez liczby dostaje `icon` ze słownika (S13) albo nic | 12, 18, 19, 21, 28, 29, 31, 32, 39 | t62 Trzy fakty w kartach (zapas t38 Wskaźniki (KPI)) |
| S3 | nagłówek-na-tytuł | pierwszy wiersz to goły `h` (<= 14 słów) nad `pics` / `chips` / `cols`, slajd ma `title` z belki i nie ma `kicker` | `kicker` = dawny `title`, `title` = tekst `h`, wiersz `h` znika | 9, 35, 36, 38 | - |
| S4 | kafle-ikony | wiersz `chips` albo 2-6 kolejnych wierszy `b` / `li` po <= 6 słów | `cols` kafli: `icon` (S13, `align c`, kółko) + `lead` ink `align c`; 4 pozycje = 2 x 2, 2, 3, 5 = jeden rząd, 6 = 2 x 3 | 2, 9, 10 | t56 Okazje spożycia |
| S5 | nagłówek karty | pierwszy fragment akapitu bez `h`: pierwsze zdanie <= 4 słowa (także pytanie), albo pierwsze słowo z „:”, albo tekst do „ – ” <= 9 słów i reszta >= 5, albo do „np.” <= 6 słów (karta `fill: brand`); S5b: nagłówek + dokładnie 2 krótkie zdania, ostatnie „Najlepiej / Warto / Zalecamy …” = osobna karta zielona; S5c: akapity od „Słowo:” = osobne karty | blok `h` (zielony, `wyr` zostaje) + hasło / dopisek z resztą (S14); (iii) na slajdzie z >= 3 wierszami = goły wiersz `h` (brand, `align l`, 28 pt) NAD kartami, karty bez ikon (S14h, s37) | 12, 16, 34, 37, 39, 41 | - |
| S6 | etykieta-wartość | linie `^(CT\|TA)\s*:` (goły `h`, R8) | rząd kafli `kv` (`label` „CT:”, `t` reszta); jedna linia = jeden kafel | 14, 37 | t45 Logistyka |
| S7 | lista-z-ikoną | karta: `h` + >= 3 krótkie akapity-linie (<= 12 słów) albo blok `p` z liniami „• ” (także kolumny bez kart: wiersz dostaje karty) | `h` + bloki `li` (`icon: check`), czerwona linia -> `wyr` same „a” | 15, 22 | t17 Punkty |
| S8 | teza-zielona | slajd = jedna karta z >= 2 blokami `lead` (<= 16 słów razem) bez innych wierszy; jedno `lead` (<= 12 słów) z trafieniem w słowniku -> ikona nad hasłem | karta `fill: brand`, `align: c`; hasło: karta z ikoną | 3, 23 | t14 Jedno zdanie – teza |
| S9 | para-kontrast | R6a: dwie karty „Prefiks – reszta” | `lead` pod nagłówkiem `color: ink` (nie zielony na zielonym); ikona `trending-up` / `trending-down`, gdy nagłówek zawiera „dobr” / „zł” | 6 | t59 Dwie karty: dobra i zła wiadomość (zapas t21 Porównanie: dziś i propozycja) |
| S10 | temat-pas | jedyny akapit zaczyna się wyróżnionym (`wyr` a) słowem + „ –” albo wyróżnionym pierwszym zdaniem <= 4 słowa, a reszta ma >= 20 słów w 2-4 zdaniach; lista pod nagłówkiem z „:” (>= 2 pozycje) | `band` (brand, `align: l`, ikona S13) NAD kartami, każde zdanie = karta; lista: nagłówek ink + karty obok siebie (s10: linie źródła „Odpowiedź … / Pozyskanie …” to osobne pozycje - `_pozycje`) | 10, 19, 20 | - |
| S11 | hasło w karcie | `lead` w karcie z `h` albo `icon` | `color: ink` (także każde zielone hasło w kremowej karcie); wymuszone łamania autora zdejmowane w kartach węższych niż 60% slajdu | 6, 14 | - |
| S12 | układ slajdu | każdy slajd `uklad` | `valign: "t"`; `min_h` kart (do 9,5 cm) tak, by karty + pasy zajęły >= 65% pola treści, bez rozciągania kart z obrazami (`szablonuj.rozloz`) | wszystkie | - |
| S13 | słownik ikon | `assets/ikony-slowa.json`: `rdzenie` (słowo zaczyna się od rdzenia, >= 4 litery; ponad 690 wpisów) i `slowa` (całe słowo; ponad 110) -> nazwa ikony z zestawu marki „W stylu DK” (`assets/icons/dk`, te same nazwy co Lucide; zapas: `assets/icons/svg`); zdrowie, sport, białko, cukier, energia, kobiety, młodzi, seniorzy, czas, pieniądze, wzrost, spadek, mózg, serce, woda, kawa, impreza, cel, uwaga, sklep… | pierwsze trafienie w tekście karty; brak: kafle S4 dostają `sparkles`, pozostałe karty bez ikony | - | - |

**S14 „hasłowanie” (decyzja usera 13.10, po obejrzeniu pierwszej ręcznej wersji; wygrywa z S2, S5, S11 tam, gdzie się różnią).**
„Slajdy w szablonie są przepiękne, a slajdy w prezentacji strategii zrobiłeś bardzo brzydko. Za dużo czcionki Lato. Za mało tam
jest prezentacji, za dużo bloków tekstu… za mało haseł.” Karta nie zostawia zdania jako bloku Lato: zdanie staje się HASŁEM Mindset
(`lead`, ink), reszta - krótkim dopiskiem Lato (`p`, `max_pt: 18`). Wzorzec ręczny: `dopracuj.py` (`haslo_cut`, `H`), kod: `szablonuj.py`
(`haslo_cut`, `_haslowanie_bloku`, `_haslowanie_karty`; stałe `CALE`, `HMIN`, `HMAX`, `HDLUGIE`).

| # | Wzorzec | Warunek | Wynik | Wzór z katalogu |
|---|---|---|---|---|
| S14a | hasło ze zdania | każdy akapit `p` karty (pierwsze zdanie) | zdanie <= 12 słów: całe jako `lead` ink; dłuższe: `lead` do pierwszego przecinka stojącego po 4-15 słowach, a gdy go nie ma - przed pierwszym „i / oraz / ale / wobec / czyli” na pozycji 4-15; reszta zdania + kolejne zdania = jeden `p` max 18 pt. Bez granicy: całe zdanie (do 24 słów; dłuższe zostaje akapitem Lato) | t61 Akapit w karcie z wyróżnieniem |
| S14b | czerwone hasło | `wyr` hasła ma >= 80% „a” | `wyr` znika (wyróżnienie wszystkiego = brak wyróżnienia) | - |
| S14c | jedno hasło na kartę | karta ma już `h` >= 3 słowa (nie etykietę z „:”) i stoi w rzędzie >= 3 kart | reszta akapitu = sam dopisek `p` (bez drugiego `lead`) | - |
| S14d | liczba-bohater z hasła | S2 | `hero` = liczba z jednostką stojąca w haśle (slajd 28: „35%”, nie „3,8 mld zł”) | t62 Trzy fakty w kartach |
| S14e | akapit >= 4 zdań | karta z `h` i akapit >= 4 zdań (s41) | 1. zdanie = S14a, każde kolejne = `li` (`icon: check`) | t17 Punkty |
| S14f | krótkie hasła w kafelkach | pozycje listy pod nagłówkiem z „:” (s10: nagłówek + 2-3 pozycje = jeden wiersz: karta zielona z nagłówkiem + karty-hasła obok), zdania <= 12 słów w kartach | zawsze `lead`, nigdy `p` | - |
| S14g | wniosek z danych | ostatnie zdanie karty (>= 2 zdania, <= 14 słów) zaczyna się od „To ” (s22), z dowolnej karty wiersza | `band` brand pod kartami (S1) | t62 Trzy fakty w kartach (pas) |
| S14h | nagłówek do myślnika w rzędzie z `kv` | S5 (iii) na slajdzie z >= 3 wierszami (s37) | goły wiersz `h` nad kartami; karty bez ikon | - |
| S15 | jedno zdanie = jeden kafel (`szablonuj._s15`, stałe `S15_MAKS = 16`, `S15_KAFLE = 4`) | rząd 1-4 kart-faktów, w którym jest co najmniej jedno zdanie z liczbą z jednostką; karta z jednym akapitem `p` o 2-3 zdaniach, gdzie pierwsze zdanie ma >= 5 słów (krótsze = nagłówek karty, S5), a kolejne <= 16 słów (samodzielna myśl) | akapit rozpada się na osobne kafle, o ile po rozdzieleniu jest <= 4 kafli: 4 = siatka 2 x 2 (kolejność wierszami = kolejność źródła), <= 3 = jeden rząd; kafel bez liczby dostaje ikonę (S13). Nie dzieli: karty z nagłówkiem-etykietą (S14e), karty z kilkoma blokami, > 4 kafli po rozdzieleniu. Wyłączenie: `wstrzymane={"S15"}`. Efekt: s12 = 3 kafle (liczba / ikona / nagłówek + dopisek) + pas; s31 = 2 x 2 | t62 Trzy fakty w kartach (zapas t38 Wskaźniki (KPI)) |

**Dodatki z 13.10 (po S14):**
- **Ikony tylko tam, gdzie pomagają** (przykłady to slajdy strategii): karta z samymi wyśrodkowanymi hasłami albo wynikiem równania (s7) jest bez ikony; slajd z >= 4 wierszami (nagłówek + karty + `kv` + pas, s37) dostaje karty bez ikon od razu (`stosuj` ponawia z `ikony_kart=False`; wcześniej dopiero gdy pismo < 15 pt); dwie karty-hasła u góry slajdu z pasem i `kv` (s14) zachowują ikony.
- **Ikony marki:** `szablonuj.IKONY_SVG` wskazuje `assets/icons/dk` (`<nazwa>.png`; zapas: stare `icons/svg`), `ikona_istnieje(nazwa)`; każda nazwa słownika `ikony-slowa.json` ma plik ikony (test S13).
- **Placeholdery `[...]`** (`szablonuj._placeholder`): slajd z jakimkolwiek tekstem w nawiasach kwadratowych zostaje jak przed szablonowaniem (żadnych haseł, kafli S4, liczb-bohaterów) - to szablon do wypełnienia, nie treść.
- **Wzór z katalogu:** każda decyzja w `decyzje-szablon.json` (klucz `szablon` specu) ma pole `wzor` = `{id, nr, nazwa}` z `assets/katalog-szablonu.json` (mapowanie `szablonuj.WZORY` = ostatnia kolumna tabel; puste, gdy brak mapowania albo pliku). W uwagach: „Wzory z szablonu: slajd 18: Trzy fakty w kartach (wzór: slajd 62 szablonu); …” (do 12 pozycji, reszta „…i N innych”); t61 jest pomijany na slajdzie, który ma lepszy wzór.
- **Błędy tekstu źródła:** ostrzeżenia i jawne poprawki - pkt 2c. Pomocniczo `zdania()` dzieli zdanie po „zł.” w środku wiersza.

Zabezpieczenia: karta z >= 5 akapitami (lista) zostaje bez haseł; karta z nagłówkiem-liczbą („11 g”, „0%”) nie dostaje drugiego `hero`
ani ikony; hasło w karcie kremowej nigdy nie jest zielone (S11). Miara (`szablonuj.miara_slow`, słowa w kartach `cols`): ręczny wzorzec
`out2` Mindset (lead + h) 492 / Lato (p + li) 309, automat ok. 480 / 320, program 1.2.0 sprzed szablonowania 92 / 766. Różnice wobec
wzorca ręcznego (nie błąd): s22 (słupki `bars`), ikony „po sensie” (słownik trafia po słowie); s12 i s31 zgadzają się po S15 (s12 = 3 kafle, s31 = siatka 2 x 2).

**Czego automat NIE robi** (zostaje dla agenta AI z polecenia po konwersji): słupki `bars` (etykiet nie da się pewnie wyciąć ze
zdania: s22 „owoce i warzywa 49%, słodkości 31%, słone przekąski 4%”), wybór ikony „po sensie” (słownik trafia po słowie, nie po
sensie zdania), łączenie zdań w pary pytanie / odpowiedź, poprawianie tekstu (tylko ostrzeżenia lint; poprawki wpisuje człowiek albo AI do `poprawki`, pkt 2c), a także ocena, czy pas-wniosek jest czerwony („zła wiadomość”) - automat zna tylko kolor źródła i krótką listę słów negatywnych.

**Jak sprawdzić:** (1) `python scripts\pptx_convert.py <plik> --wyjscie <katalog> --robocze <rob> --bez-qa` - w raporcie wiersz
„Ułożyłem w klocki szablonu marki … slajdy: …”, `coverage` 100%, `wiernosc` usterki 0 i znaki 0; (2) render i plansze
„oryginał | ręczna | automat”; (3) `pytest scripts\test_konwersja.py` - po jednym teście na regułę S1-S15 (sztuczne wiersze) i
testy integracyjne `test_szablon_co_dalej_klocki_i_tresc_bez_strat`, `test_miara_slow_mindset_wiecej_niz_lato_w_kartach`.

## 2c. Błędy tekstu źródła: ostrzeżenia i jawne poprawki (13.10.2026)

User 13.10: „Jeśli widzisz ewidentne błędy, jak „komunikacjaod”, to w programie ostrzegaj przed czymś takim… Tego typu błędy,
literówki, sieroty itp. - POPRAWIASZ.” Podział ról: **program ostrzega** (automat dalej nie zmienia słów, zasada 1:1),
**AI poprawia** w granicach i jawnie, **kontrola sprawdza**, że poprawka mieści się w granicach. Zasady dla agenta (4 warunki,
przykłady, czego nie poprawiasz, sieroty i zawieszki to sprawa łamania, nie tekstu): `dopracowanie.md` pkt 4 - tu tylko mechanika.

**Ostrzeżenia (lint).** `pptx_convert._lint` woła `lint_tekst.sprawdz([(nr, [teksty])])` na tekstach ŹRÓDŁA (akapity, komórki
tabel; bez notatek). Wynik trafia do specu w klucz `bledy_tekstu`: `[{slajd, rodzaj, jest, propozycja, kontekst, pewnosc}]`.
W uwagach: nagłówek „Możliwe błędy w tekście oryginału: N (program ich nie poprawia…)”, wszystkie `wysoka`, do 10 `srednia`,
reszta jako „…i N innych”; ta sama lista idzie do polecenia dla AI. Słownik offline: `assets/slownik/` (licencje:
`LICENCJA.txt`). Brak modułu albo słownika = cisza, wyjątek = wpis w `<rob>\lint.log`; lint nigdy nie psuje konwersji. Fałszywy
alarm jest gorszy niż pominięcie, więc lint nie widzi błędów odmiany („kierunku” zamiast „kierunki”) - tych szuka agent, czytając slajdy.

| rodzaj | co łapie | pewność |
|---|---|---|
| `sklejone` | słowo spoza słownika, które dzieli się na dwa słowa („komunikacjaod” -> „komunikacja od”) | `wysoka`, gdy jedno z nich jest częste (przyimek, spójnik) albo oba mają >= 4 litery, inaczej `srednia` |
| `literowka` | słowo spoza słownika z jednym bliskim sąsiadem wśród częstych słów; nie: nazwa własna, skrót, słowo z cyfrą lub łącznikiem, słowo obce z białej listy, słowo powtarzane w prezentacji | `srednia` |
| `powtorzenie` | to samo słowo dwa razy pod rząd („na na”) | `wysoka` dla przyimków i spójników, inaczej `srednia` |
| `interpunkcja` | brak spacji po przecinku lub kropce („smak,ale”), spacja przed przecinkiem lub kropką, „..” zamiast „…” | `wysoka` |
| `spacje` | dwie i więcej spacji w środku zdania | `srednia` |
| `nawias` | niedomknięty nawias lub cudzysłów w obrębie jednego tekstu | `srednia` |

**Poprawki (klucz `poprawki` specu).** Format i przykład: `dopracowanie.md` pkt 4; `slajd` = numer slajdu ŹRÓDŁA. Kontrole
(`coverage`, `wiernosc`) podmieniają `bylo` -> `jest` w tekstach tego slajdu źródła przed porównaniem, ale tylko dla wpisów
o statusie `przyjeta` (`pptx_convert._raport_poprawek`):

| status | znaczy | skutek |
|---|---|---|
| `przyjeta` | `bylo` stoi w tekście slajdu źródła, a zmiana mieści się w granicach | stosowana przed porównaniem; w raporcie „sNN: „było” -> „jest” (powód)” |
| `nie_w_zrodle` | `bylo` nie ma w źródle | usterka „poprawka nie pasuje do oryginału” |
| `poza_granicami` | zmiana większa niż granice | usterka „poprawka poza granicami (slajd N: „…” -> „…”)”, nie stosowana |

Granice (`poprawka_w_granicach`): (a) wstawienie lub usunięcie spacji (sklejone i rozklejone słowa, podwójna spacja, spacja przy
przecinku lub kropce); (b) usunięcie zdublowanego słowa; (c) zmiana, wstawienie lub usunięcie najwyżej 2 znaków w obrębie jednego
słowa; cyfry w `bylo` i `jest` identyczne i w tej samej kolejności. Więcej niż 15 przyjętych poprawek = ostrzeżenie „dużo poprawek
tekstu: N - sprawdź listę”. Wynik kontroli ma klucze `poprawki` i `ostrzezenia`. Wpis w `poprawki` to tylko deklaracja: tekst
poprawiasz też w specu slajdu (`jest` ma stać w wyniku).

**Kontrola z poprawkami** (po edycji specu przez AI):

```powershell
python "$S\pptx_convert.py" "<oryginał.pptx>" --ze-specu "<rob>\spec_konwersja.json" [--poprawki "<poprawki.json>"] `
       --wyjscie <katalog> --robocze <rob>
```

Jedno polecenie buduje plik, robi zrzuty i wszystkie kontrole („Tekst - problemy”, „Treść”, „Układ”, status każdej poprawki). `--ze-specu` buduje z gotowego specu (zamiast składać od nowa) i czyta `poprawki` ze specu; `--poprawki` dokłada wpisy z pliku (lista jak w `dopracowanie.md` pkt 4). Bez PowerPointa dodaj `--bez-qa`: kontrole treści i układu działają, zrzutów i kontroli tekstu nie ma (w raporcie piszesz wtedy, że wyglądu nie sprawdzono). Pętla „oko” (2d) przy `--ze-specu` jest zawsze wyłączona: spec poprawiony ręcznie albo przez AI nie dostaje innych układów.
`pc.coverage(src, out, mapa, rob=rob, poprawki=spec["poprawki"])` i `pc.wiernosc(model, out, mapa, poprawki=spec["poprawki"])`.

## 2d. Samoocena układu i oko programu (13.10.2026)

User 13.10: „każda prezentacja to trochę coś innego, dlatego ocenianie przez screenshot to ważna sprawa. Tylko program sam w sobie
nie będzie mieć LLM, który oceni to, dlatego trzeba umieć tak zbudować program, by on umiał patrzeć na to, co widzi, i podejmować
decyzje.” Reguły S1-S15 nadal ustalają wzorzec; o wyborze między wariantami układu decyduje POMIAR, w dwóch krokach: przed renderem
(a) i po renderze (b). Kod: `szablonuj.py` (9a-9c), `oko.py`, `pptx_convert.popraw_po_renderze`, w programie `engine.petla_oka`.

**(a) Przed renderem: `szablonuj.ocena(slajd)`** liczy z miar układu (`build_dk.uklad_layout`: rozmiary pisma, wysokości, linie) -
bez PowerPointa i bez obrazu - punkty = 100 + premie (hasło do 8, dopisek do 6, wypełnienie pola do 6, udział Mindset do 6) - kary.
Zwraca `{punkty, miary, usterki: [{kod, opis}]}`:

| kod | kara | warunek |
|---|---|---|
| `HASLO_MALE` | 14 | hasło < 16 pt (w rzędzie 5-6 kart: < 14 pt) |
| `DOPISEK_MALY` | 8 | dopisek albo punkt < 13 pt |
| `HASLO_MNIEJSZE` | 6 | hasło mniejsze od dopisku w tej samej karcie |
| `SLOWO_PO_SLOWIE` | 10 | 3 kolejne jednowyrazowe linie hasła |
| `HASLO_DLUGIE` | 5 | hasło ma > 5 linii |
| `PUSTY_DOL` | 8 | > 30% pola treści wolne, a pismo jeszcze może rosnąć |
| `KARTA_PUSTA` | 6 | > 50% wysokości karty puste (rząd >= 2 kart z kartami) |
| `KARTY_NIEROWNE` | 5 | treść kart w rzędzie różni się > 2,5 x |
| `ZA_DUZO_LATO` | 6 | > 60% słów kart w Lato (od 20 słów Lato) |
| `AKAPIT_BEZ_HASLA` | 7 | akapit Lato > 3 linie w karcie bez hasła i bez liczby |
| `PLYWAJACA_TRESC` | 9 | treść <= 50% wysokości slajdu, pusty pas >= 18% wysokości pod tytułem i pod treścią |
| `NIE_MIESCI_SIE` | -1000 | treść nie mieści się nawet najmniejszym pismem |

Ten sam kod karze do 3 razy (`HASLO_MALE`, `DOPISEK_MALY`, `SLOWO_PO_SLOWIE`, `KARTA_PUSTA`, `AKAPIT_BEZ_HASLA`, `HASLO_DLUGIE`), pozostałe raz.
`szablonuj.kandydaci` buduje wariant domyślny (wzorzec reguł) i warianty z osi, w kolejności od najmniej inwazyjnej: `pad` (odstęp kart x 0,75),
`ikony` (kafle z ikonami / bez), `siatka` (kafle w jednym rzędzie / w siatce 2 x 2, 3 + 2), `h_wiersz` (nagłówek w karcie / w wierszu nad
kartami), `zdania` (kolejne zdania jako dopisek / jako punkty `li`; kafle z S15 to wzorzec reguł); najwyżej 12. Kandydat to pełny slajd z tymi
samymi słowami (`szablonuj.slowa()`), „dopuszczony”, gdy mieści się pismem >= 15 pt. `szablonuj.wybierz`: najwięcej punktów wśród
dopuszczonych, ale kandydaci w granicach 10 punktów od najlepszego są równorzędni i wygrywa ten bliższy kolejności reguł - zaakceptowany
wzorzec zostaje, chyba że ma ciężką usterkę. Zapis: `decyzje-szablon.json` (wpis `wybor-wariantu`, pole `warianty`: nazwa, punkty, usterki,
wybrany) i `warianty-szablon.json` obok specu (pełne slajdy kandydatów; spec ma `warianty_plik` i `poprawki_ukladu`). Uwaga dla człowieka
tylko wtedy, gdy wybrano wariant inny niż domyślny.

**(b) Po renderze: `oko.py`** mierzy zrzut PNG (zmniejszony do ok. 480 px, ok. 7 ms na slajd; piksele w klasach: biel, krem kart, zieleń
marki, reszta; bez PowerPointa, bez LLM; wymaga `numpy` i `PIL`). Pomija slajdy na zielonym tle (okładka, przekładka, zakończenie) i typy
luźne. Progi są stałymi na górze `oko.py`, strojonymi na zbiorach: zaakceptowana wersja strategii (43 slajdy) ma jeden slajd z usterką wagi
>= 2, odrzucona wersja 1.2.0 osiem razy `PLYWAJACA_TRESC`, szablon marki 0 usterek wagi 3.

| kod | waga | próg |
|---|---|---|
| `PUSTY_DOL` | 1 / 2 / 3 | pusty pas pod najniższą treścią > 0,30 wysokości slajdu (waga 2 od 0,40, 3 od 0,55) |
| `KARTA_PUSTA` | 2 / 3 | > 0,50 wysokości karty pusta pod tekstem, sąsiadka wypełniona (waga 3 od 0,75) |
| `KARTY_NIEROWNE` | 2 / 3 | treść najwyższej karty w rzędzie > 2,5 x niższej (waga 3 od 4,0) |
| `PRZY_KRAWEDZI` | 2 / 3 | treść bliżej niż 0,02 od krawędzi (waga 3, gdy dotyka krawędzi) |
| `GESTO` | 1 | tekst albo karta niżej niż 0,935 wysokości: brak światła u dołu |
| `MALO_TRESCI` | 1 / 2 | wypełnienie pola treści < 0,50 (waga 2 poniżej 0,25); nie, gdy jest `PLYWAJACA_TRESC` |
| `PLYWAJACA_TRESC` | 2 | pusty pas pod tytułem >= 0,18, pod treścią >= 0,18, treść <= 0,50 wysokości |

Pętla (`popraw_po_renderze` -> `szablonuj.inny_wariant`): tylko usterki wagi >= 2 (waga 1 trafia do „Sprawdź najpierw”, nie do przebudowy).
Slajd dostaje kandydata, który jest dopuszczony, nie ma tych kodów według `ocena`, nie jest gorszy o więcej niż 6 punktów i różni się od
obecnego TYLKO osiami wyglądu `OSIE_PO_RENDERZE` = `pad`, `ikony`, `siatka`, `h_wiersz` (podział treści na kafle, oś `zdania`, zostaje);
dla kodów widocznych tylko na obrazie miara musi iść w dobrą stronę. Po przebudowie i ponownym renderze wariant zostaje WYŁĄCZNIE przy mniejszej
liczbie usterek wagi >= 2 (w programie: miara = liczba ciężkich usterek, potem suma wag, razem z kodami kontroli PowerPointa; wariant z mniejszym
pismem haseł jest cofany nawet przy mniejszej liczbie usterek); inaczej układ wraca, a slajdu nie rusza się drugi raz. Najwyżej 2 rundy (program:
1 runda, gdy pierwsza budowa z kontrolą trwała > 240 s). Wynik w uwagach: „Po obejrzeniu zrzutów poprawiłem układ slajdów: …” oraz „Sprawdź
najpierw: slajd N - <opis usterki>” (do 10 linii, resztę zapisuje `raport.json`, pole `oko`). Wyłączenie: `stworz-cli.exe --bez-oka` (program;
w silniku `opts["oko"] = False`); w `pptx_convert.py` skilla: `--bez-oka`; pętla nie działa też z `--bez-qa` (brak zrzutów) ani z `--ze-specu` (spec poprawiony ręcznie / przez AI zostaje nietknięty). Ręcznie:
`python $S\oko.py <katalog png> [spec.json]` wypisuje tabelę slajd | kody | miary.

**(c) Granica narzędzia.** Oko widzi geometrię (puste miejsce, nierówne karty, krawędź), nie treść: nie wie, czy ikona pasuje, czy hasło ma
sens, czy wniosek stoi w pasie ani czy tekst ma błąd. Takie decyzje smaku zostają dla AI z kopiowanego polecenia i `dopracowanie.md`
(8 pytań na slajd); lista „Sprawdź najpierw” mówi, gdzie spojrzeć najpierw, i nie zastępuje oglądania plansz.

## 3. Wizualizacje produktów (A36): `scripts/wizki.py`

Biblioteka: `…\- POLSKA\01 - PRODUKTY\- DK\<kategoria>\<SMAK — [ linia ]>\<wersja>\4 - WIZKI\*FRONT-S*.png`
(także podfolder `INTERNET-PREZENTACJE-RGB`; nigdy ARCHIWUM, PROJEKT, DRUK). Szukana od pliku prezentacji w górę,
potem `M:\…`, `D:\Marketing\…`; `DK_PRODUKTY=<ścieżka>` wskazuje ją wprost, `DK_PRODUKTY=brak` wyłącza.

```powershell
python "$S\wizki.py" --lista --kategoria batony                 # linie i smaki w bibliotece
python "$S\wizki.py" "pralinowe" --kategoria kulki --zloz wiz\kol_pralinowe.png   # dopasowanie + złożona grafika
```

Automat wstawia grafikę nad nagłówkiem kolumny tylko wtedy, gdy **każda** kolumna wiersza ma pewne dopasowanie w
kategorii nazwanej w tytule slajdu („Kulki”, „Batony”): nazwa linii dokładnie, ta sama nazwa bez końcówki
(„funkcjonal” = funkcjonalny) albo wpis w słowniku `assets\linie-aliasy.json`. Podobna nazwa to tylko „kandydat”
w uwagach. Bierze do 3 smaków linii, jedną rangę wersji (pojedyncza sztuka przed kartonem i mini), nie miesza paczek
stojących z leżącymi, składa je z miękkim cieniem. Nie wstawia, gdy tekst karty spadłby poniżej 12 pt. Każdy wybór
jest w uwagach („Pralinowe: słownik: Pralinowe = deserowe (Banoffee kakao, Tiramisu)”) i w nazwie kształtu.

**Słownik linii jest założeniem** (pralinowe = deserowe, posiłkowe = śniadaniowe, protein = paczki „Proteina”,
nerkowiec = nerkowcowy): dobór z 07.10, którego user nie odrzucił, ale nie potwierdził wprost. Zawsze pokaż userowi,
co wstawiono, i popraw słownik, gdy linie są inne. Ręcznie: obejrzyj kandydatów (`Read`) przed użyciem.

## 4. Twoje kroki po automacie

Kroki (render oryginału i wyniku, plansze par, 8 pytań na slajd, poprawki w specu, bramki, raport z DO DECYZJI) opisuje JEDEN
dokument: `dopracowanie.md` pkt 7-9; nie powtarzam ich tutaj. Komendy (`render` i `verify` uruchamiaj pojedynczo; po wyjątku COM
wynik jest nieważny, `lekcje.md` D):

```powershell
$S = "$env:USERPROFILE\.claude\skills\prezentacje\scripts"
& "$S\render.ps1" -Src "<plik>" -Out "<katalog png>"                       # oryginał; wynik: dodaj -EmbedFonts
python "$S\pary_slajdow.py" <png oryginału> <png wyniku> <katalog>        # plansze par stary | nowy
python "$S\pptx_convert.py" "<oryginał.pptx>" --ze-specu "<rob>\spec_konwersja.json" --wyjscie <katalog> --robocze <rob>
                                                                          # po poprawce w specu: plik, zrzuty i wszystkie kontrole (2c)
python "$S\oko.py" <katalog png> "<rob>\spec_konwersja.json"              # pomiar zrzutów: gdzie patrzeć najpierw (2d)
```

Samą kontrolę tekstu puszczasz osobno: `& "$S\verify.ps1" -Src "<wynik.pptx>"` („Tekst - problemy: 0”). Spec z programu to
`spec_program.json` (ścieżkę podaje polecenie dla AI); po CLI leży w `<folder prezentacji>\_robocze\<nazwa>\spec_konwersja.json`.

Krytyk (`Agent`, `critic`) jest pomocą, nie bramką: 06.10 dwie rundy krytyka i audyt przeszły, a user odrzucił całość,
bo kryteria były moje („tytuł-wniosek”, „jedna myśl na slajd”), nie jego. **Bramką są plansze par obejrzane co do jednej (`dopracowanie.md` pkt 7-8).**

## 5. Pułapki

| Pułapka | Jak jej unikasz |
|---|---|
| przebudowa zamiast konwersji (agenda, przekładki, KPI, tytuły-wnioski) | cel `wiernie` to zasada z pkt 1; inne cele tylko na życzenie usera |
| „100% treści”, a slajd zły (etykieta wklejona w zdanie, zmieniona kolejność) | druga kontrola `wiernosc`; plansze par |
| zdjęcia zniknęły (Canva: obraz jako wypełnienie kształtu) | `extract` czyta `a:blipFill`; porównaj liczbę obrazów na planszach |
| packshot powtarzany na wielu slajdach uznany za ozdobnik | pomijany jest tylko obraz stojący w tym samym miejscu na większości slajdów albo drobiazg |
| obraz przycięty (cover) - ucięty tekst na zdjęciu, logo, legenda | tylko `uklad` / `pics` (`_contain_pic`) |
| zrzut z tekstem zastąpiony przepisanym tekstem | zrzut zostaje; przepisany tekst do `notes` |
| slajd-kolaż rozbity na trzy slajdy | siatka obrazów z podpisami; sprawdź, czy podpisy trafiły do swoich obrazów |
| skrót przez kasowanie | tylko ukrywanie; krótsza wersja = NOWY slajd, oryginał ukryty za nim |
| zły packshot na slajdzie | automat wstawia tylko pewne dopasowania i wypisuje je; słownik to założenie |
| nazwa własna albo skrót małą literą | lista `wielkosc-liter.txt`; dopisz skrót do `SKROTY` w `pptx_convert.py` |
| myślnik na początku linii, zawieszki | bez ręcznych `\n` poza rozdzieleniem pozycji listy; `verify` |
| fałszywe „problemy: 0” po wyjątku COM | powtórz `verify`, gdy PowerPoint był zajęty |
| łatka z `\n` albo `\\` pisana heredokiem | plik łatki narzędziem Write (lekcje B) |
| plik 20+ MB | zdjęcia do 2400 px robi `extract`; ręcznie: do 2200 px (JPG 88) |
| prezentacja już w nowym stylu DK | nie ma czego konwertować: sceny z paczkami i ikonami wychodzą gorzej niż oryginał |
| akapity Lato w kartach zamiast haseł, akapit Lato bez hasła | hasłowanie: `dopracowanie.md` pkt 6; miara: w kartach z tekstem więcej słów w Mindset niż w Lato |
| własny układ „z głowy” zamiast slajdu szablonu | tabela „kształt treści -> slajd” z `katalog-szablonu.md`; brak wzoru = DO DECYZJI |
| poprawka tekstu bez wpisu w `poprawki` (kontrola uzna ją za zgubione słowa) | każdą poprawkę zadeklaruj; poza granicami nie poprawiaj, zgłoś |
| „poprawiona” nazwa własna, cytat, liczba albo oświadczenie | czterech warunków z `dopracowanie.md` pkt 4 nie obchodzisz; wątpliwość = DO DECYZJI |
