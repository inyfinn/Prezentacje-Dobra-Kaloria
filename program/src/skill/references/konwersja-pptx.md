# Konwersja gotowej prezentacji -> styl Dobra Kaloria (rewizja 07.10.2026, automat 1:1 + cele)

Przypadek wzorcowy: `PREZENTACJE\06.10.2026 - strategia\DK_co_dalej_update.pptx` (43 slajdy) ->
`DK_co_dalej_update - nowy styl.pptx` (**43 slajdy**, `verify` 0 problemów). Wzór ręcznego specu:
`...\06.10.2026 - strategia\_robocze\make_spec.py` (user 07.10 13:40 usunął `_robocze`; wzorem jest teraz sam automat,
pkt 2a). Decyzje usera: `lekcje.md` A27-A44. Błędy i przyczyny: `lekcje.md` D.

> Pierwsza wersja (06.10) przebudowała treść: 57 slajdów, dodana agenda i przekładki, tytuły-wnioski, liczby wyjęte
> do kafli. User ją **odrzucił** (07.10): „kompletnie pomyliłeś teksty… Nie trzymałeś się tekstów w slajdzie
> i kolejności… przerobiłeś prezentację w zły sposób… Staraj się trzymać układu ze starej prezentacji”.
> User porównuje dwa okna PowerPointa obok siebie, slajd N ze slajdem N. Od 07.10 tak samo robi automat.

## 0. Cel konwersji (zapytaj albo przyjmij „zachowaj układ”)

User 07.10: „nie zawsze ma to sens, czasem chcemy dokończyć prezentację, rozwinąć ją albo skrócić. To też powinno
być dostępne jako opcja”. Baza jest ZAWSZE ta sama (slajd w slajd, nic nie ginie); cel zmienia to, co wolno potem.
Jedno źródło nazw i zasad: `pptx_convert.CELE` (czyta je program, wiersz poleceń i ten dokument).

| Cel (`--cel`) | Co robi automat | Co wolno Tobie (AI) potem | Czego nie wolno |
|---|---|---|---|
| `wiernie` „Zachowaj układ” (domyślny) | ten sam slajd w nowym wyglądzie | poprawić czytelność: rozmiar pisma, łamanie, podpis przy właściwym obrazie; oczywiste literówki (z listą „było -> jest”) | własne tytuły, agenda, przekładki, łączenie i dzielenie slajdów, przestawianie, dopisywanie |
| `rozwin` „Rozwiń / dokończ” | baza + puste slajdy z szablonu (`--dodaj t10,t58`) wstawione PRZED zakończeniem, w notatkach „NOWY” | wypełnić [nawiasy] treścią wynikającą z prezentacji; zaproponować brakujące slajdy (miejsce, typ z szablonu, tekst), każdy oznaczony NOWY | ruszać slajdy oryginału; wymyślać liczby i fakty (czego nie ma w materiałach, zostaje w [nawiasach]) |
| `skroc` „Skróć” | baza; rozdziały spoza `--sekcje` zostają w pliku jako slajdy UKRYTE | ukrywać slajdy; krótszą wersję albo połączenie dwóch slajdów robić jako NOWY slajd, a oryginały ukryć tuż za nim (pełny tekst także do notatek nowego slajdu); lista „Co ukryte i gdzie jest oryginał” | kasować slajdy albo tekst; zmieniać liczby, nazwy, sens |

**Jedna reguła we wszystkich celach:** rozdział wyłączony w `--sekcje` (w oknie: przełącznik) to slajdy ukryte, nigdy
usunięte. Priorytet nr 1 usera: „NAJ, NAJWAŻNIEJSZE, to nie zgubić danych”. Ukryte slajdy nadal są w pliku: przed
wysłaniem poza firmę trzeba je usunąć albo zapisać PDF (automat przypomina o tym w uwagach).

## 1. Zasada bazy: ten sam slajd, nowy wygląd

| Zostaje bez zmian | Zmienia się |
|---|---|
| liczba i kolejność slajdów (slajd N = slajd N) | tło, czcionki (Mindset / Lato), kolory motywu, karty, metki |
| teksty na slajdzie (te same słowa, ta sama kolejność góra-dół) | rozmiar pisma (sam się dopasowuje) |
| układ: kolumny to kolumny, stos haseł to stos haseł, łamania wierszy autora w hasłach | wyrównanie i odstępy w ramach tego układu |
| osobne elementy osobno („Zmiana nazwy”, „Segment 1 & 3”, źródło, komentarz autora) | forma: znacznik, metka, drobny podpis |
| obrazy w całości, w tym samym porządku; kolaż zostaje kolażem | zaokrąglone rogi, podpisy pod obrazem |
| wyróżnienie pojedynczych słów kolorem (czerwone / zielone słowa w haśle) | odcień: czerwień = akcent, inny kolor = zieleń marki |

Wolno: ujednolicić wielkość liter tam, gdzie źródło wyświetla wersaliki; dołożyć wizualizacje produktów na slajdach
portfolio (pkt 3). Slajd dzielimy tylko wtedy, gdy tekst nie mieści się pismem 13 pt - i mówimy o tym w raporcie.
Priorytety usera (A32): 1) nie zgubić żadnej danej, 2) sens, 3) kolejność góra-dół, 4) kontekst, 5) dopiero wygląd.

## 2. Automat: `scripts/pptx_convert.py`

```powershell
$S = "$env:USERPROFILE\.claude\skills\prezentacje\scripts"
python "$S\pptx_convert.py" "<plik.pptx>" [--cel wiernie|rozwin|skroc] [--sekcje r01,r02] [--slajdy N]
       [--bez-wizualizacji] [--wyjscie <katalog>] [--robocze <katalog>] [--bez-qa]
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
W pozostałych plikach tekst zostaje znak w znak. Literówek automat nie poprawia.

**Dwie kontrole** (obie w raporcie, obie muszą być czyste):
- `coverage` „Treść: 100% akapitów” - czy są wszystkie słowa (to worek słów: nie widzi kolejności ani sklejenia);
- `wiernosc` „Układ: osobne napisy X z X, kolejność góra-dół bez zmian, liczby X z X, slajdów tyle samo” - czy każdy
  krótki, osobny napis źródła jest osobnym elementem, czy pole stojące wyżej nadal jest wyżej, czy są wszystkie liczby.
  Stary automat dostaje tu usterkę „napis »Segment 1 & 3« nie jest osobnym elementem”, a pokrycie pokazywał 100%.

## 2a. Dobór typu z szablonu po KSZTAŁCIE treści (07.10.2026, runda 2-3)

Werdykt usera 07.10 o dwóch wersjach (ręcznej 08:15 i programu 13:12): „slajdy 6, 7 i zdecydowana większość dalej
kompletnie źle. Nie korzystałeś z naszego szablonu. Brzydkie. Po slajdzie 5 dramat.” Przyczyna na planszach trójek
(oryginał | ręczna | program): każde pole >= 28 pt szło jako wielkie hasło Mindset wersalikami na całą szerokość,
akapity gołym Lato bez karty, kremowe tło całego slajdu losowo (s07, s13, s26, s29), a karty / kafle / cytaty / kolumny
z szablonu `DK - szablon prezentacji.pptx` (60 slajdów, `make_template.py`) nie były używane poza s05 i s14.
User chce, żeby **program** (nie ręka) robił to dobrze - dla ludzi, którzy niczego nie poprawiają.

**Zasada: tekst 1:1, zmienia się tylko pojemnik.** Te same słowa, ta sama kolejność góra-dół, liczby w swoich
zdaniach, kolory słów, obrazy w całości, 43 = 43 (A33-A35, A41-A42). Automat dobiera do kształtu treści **typ pojemnika
z szablonu** (karta, kafle, cytat, kolumny, punkty), nigdy nie zmienia treści. Mindset tylko dla tytułu i haseł do
ok. 12 słów, reszta Lato; tło zawsze białe (`paper`), krem tylko w kartach. Kod: `pptx_convert._uklad` i funkcje
`_tryb`, `_hasla_grupy`, `_karty6`, `_cytaty`, `_kolumny`, `_specjalny`; rysuje `build_dk.s_uklad` (wiersze `cols` z
kartami, `chips`, `quote`, `pics`, `sub`, `b`). Spec: `spec-dk.md`, typ `uklad`.

| # | Kształt treści na starym slajdzie (warunek) | Typ pojemnika (wzór w szablonie) | Pola |
|---|---|---|---|
| R0 | każdy slajd `uklad`, zawsze | tło `paper`, karty kremowe; hasło > 4 słów max 36 pt; akapit pocięty Enterem autora sklejony w prozie kart (bez zmiany słów; twarde łamanie zostaje tylko w haśle Mindset i w pozycji listy); wielkość liter po łamaniu: wiersz po wierszu bez `.!?:` zaczyna się małą (słowo po kropce nie jest „chronione”, s26 „ale”), po `.!?:` albo po wierszu kończącym się hiperłączem - wielką i jako osobny akapit (s41 „Dla segmentu…”) | `bg` nigdy `card`; każda zmiana liter w `wielkosc-liter.txt` |
| R-ZD | pole >= 28 pt bez znaczników listy; grupa = zdanie, gdy >= 13 słów albo kończy się `.!…` i ma >= 8 słów (`?` nie liczy się); zdania >= 50% słów pola | pismo: **proza = Lato** (`p`), inaczej **hasło = Mindset** (`lead`/`h`/`sub`); wejście do R4-R7 | tylko pismo, treść bez zmian |
| R1 | pierwszy slajd z samym tekstem / ostatni z `#…` / jedno duże hasło | `cover_text` / `end` / `section` (belka = `label`, bez numeru) | jak w pkt 2 |
| R2 | pasmo poziome z 2-4 klastrami x (pola i obrazy obok siebie) | wiersz `cols`: karty obok siebie (s34 line / s46 cards_images / s21 two_cols); `card=False`, gdy w kolumnie jest obraz | `h`, `p`/`lead`, `img` w całości, `tag`, `meta` |
| R3 | lista krótkich pozycji: >= 3 wiersze po <= 6 słów bez `.!?;:` pod pytaniem / dwukropkiem, albo w kolumnie pod `h`, albo z myślnikami; wiersz od „oraz / lub / albo” dokleja się do poprzedniego | `chips` (s36 kafle) przy 2-8 pozycjach <= 36 znaków; inaczej punkty z kropką marki (s17 bullets, `b`, `li`); w kolumnie blok `p` z „• ” | pozycje 1:1, tytuł = zabrany 1. wiersz; wiodący myślnik listy = marker (jak punktor): kafle go nie mają, zawsze zielone (s09), marker w pokryciu jako `markery`, nie w `znaki`; kafle jednej kolumny równej szerokości |
| R4 | cytat: wiersz kończy się nawiasem z >= 2 słowami wielką literą, albo fragment w „…” i następny wiersz <= 6 słów bez `.!?:` | wiersz `quote` jak s20 szablonu (30 pt kursywa Lato kolor tekstu, zielona kreska, autor bold 16 pt kolor tekstu); tytuł i belka slajdu zostają | `t` = cytat, `author` = reszta wiersza z nawiasem („(Byron Sharp, Ehrenberg-Bass).”, hiperłącze zostaje) |
| R5 | 1-4 kolejne wiersze Mindset (po R-ZD) z pól >= 28 pt, nie lista, nie wstęp (R9), nie wniosek (R10b) | **jedna karta** kremowa na białym, wyśrodkowana (s14 statement w karcie) | bloki = wiersze w kolejności, `k`/`color`/`wyr` bez zmian, pad 2 cm, min 6 cm |
| R6 | 2-4 jednostki (pole = jednostka albo wiersz = jednostka), każda <= 22 słów, długości max/min <= 2.5, pt max/min <= 1.15, żadna od „=”, „+”, „pod / oraz / i / a / ale / lub / albo / czyli / bo”, żadna z `:` na końcu | **2-4 równe karty obok siebie** (s21 two_cols bez „lepszej” zielonej / s19 karty bez numerów); R6a: każda „prefiks – reszta” -> `h` = prefiks z separatorem („Dobra wiadomość –” zieleń / „Zła wiadomość –” czerwień), `lead` = reszta; karty obok siebie mają zawsze równą wysokość, krótsza treść od góry (s22) | 1 karta = 1 jednostka, lewa-prawa = góra-dół; Lato w jednej = Lato we wszystkich |
| R7 | ciąg z choć jednym wierszem Lato, który nie przeszedł R6, albo pole < 28 pt z >= 20 słów / >= 2 wierszy; R7b: samotny nagłówek Mindset <= 6 słów albo wiersz z `:` tuż przed -> pierwszy blok `h` karty | **karta-artykuł** na całą szerokość (s16 article) | akapity 1:1 (`li` -> „• ”), `wyr` z kolorów źródła, pad 1 cm, jeden rozmiar pisma w karcie (s41 >= 14 pt); dwie grupy rozdzielone nagłówkiem = dwie karty jedna pod drugą; samotny krótki wiersz < 20 słów zostaje gołym `p` |
| R8 | wiersz od `CT:`, `TA:`, `Insight:` | goły wiersz `h` do lewej (jak s14) - przerywa ciąg R5-R7 | `t` bez zmian |
| R9 | samotny wiersz Mindset <= 12 słów (albo z `:`) tuż PRZED `chips` / `pics` / `cols` z R2 | goły wiersz `h` zieleń, środek („Tytuł listy” z s17) | `t` bez zmian |
| R10 | (a) podpis-wniosek pod obrazami: pole >= 24 pt albo całe w kolorze (poza „Źródło:” = `small`); (b) samotny wiersz Mindset <= 12 słów tuż PO kartach R6/R7 | (a) `sub` Mindset 26 pod `pics` (wyśrodkowany względem rzędu obrazów, nie slajdu), kolor `accent` gdy całe czerwone, inaczej `brand`; (b) goły wiersz | `t` bez zmian |
| R11 | obrazy | `pics` (s28 gallery / s26 full_image), bez kadrowania (`_contain_pic`); rząd rozpięty od brzegu do brzegu kart (s34) | items w kolejności źródła, `layout: "1+siatka"` |
| R12 | po R3-R10 | bramka mieszczenia: nowe wiersze tylko gdy `_miesci()`; inaczej stare wiersze + wpis „Sprawdź najpierw”; dalej drabina z pkt 2; 43 = 43 | `ctx['sprawdz']` |

Karty z `kont=True` pomija `_wizualizacje` (inaczej „Dobra wiadomość” szłoby do biblioteki packshotów).

**Poprawki progów, runda 4 (10.10.2026):** pad karty-pojemnika nie rośnie z pismem (3-4 karty: 0,6 cm, 2 karty: 1,2 cm,
karta-artykuł R7: 1,0 cm zamiast 1,6-1,9); karty z „rwanym” Lato (średnie wypełnienie wierszy < 82% albo wiersz < 60% pola,
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

`render` i `verify` uruchamiaj pojedynczo; po wyjątku COM wynik jest nieważny (lekcje D).

| # | Krok | Jak |
|---|---|---|
| 1 | Render oryginału i wyniku | `& "$S\render.ps1" -Src "<plik>" -Out "<katalog png>"` (wynik: `-EmbedFonts`) |
| 2 | **Plansze par** | `python "$S\pary_slajdow.py" <png oryginału> <png wyniku> <katalog>` |
| 3 | **Przegląd par** (bramka) | `Read` każdej planszy „stary \| nowy”, najpierw slajdy z listy „Sprawdź najpierw”: ten sam slajd? te same teksty? ta sama kolejność? nic nie ucięte? podpis przy swoim obrazie? |
| 4 | Poprawki | w `<rob>\spec_konwersja.json` (albo `spec_program.json`): typ `uklad`, potem `python "$S\build_dk.py" <spec>`; przy dużych zmianach własny `make_spec.py` z `assert len(slides) == <liczba>` |
| 5 | `verify.ps1` | „Tekst - problemy: 0”, bez wyjątku COM |
| 6 | Raport | plik + godzina, N = N, obie kontrole, `verify`, lista zmian wielkości liter i literówek „było -> jest”, wstawione wizualizacje, slajdy ukryte / nowe, DO DECYZJI |

Krytyk (`Agent`, `critic`) jest pomocą, nie bramką: 06.10 dwie rundy krytyka i audyt przeszły, a user odrzucił całość,
bo kryteria były moje („tytuł-wniosek”, „jedna myśl na slajd”), nie jego. **Bramką jest krok 3.**

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
