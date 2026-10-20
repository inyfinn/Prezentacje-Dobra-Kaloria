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
| `wiernie` (domyślnie) | „przełóż na nasz styl”, „popraw wygląd” | ten sam slajd w stylu marki: hasła, liczby i wnioski w klockach szablonu; ostrzega o błędach tekstu; sam ogląda zrzuty i poprawia układ | dopracowujesz według sekcji 3b: hasła, liczby, wnioski, układ z katalogu szablonu, poprawione błędy tekstu; treść 1:1 |
| `rozwin` | „dokończ”, „rozwiń”, „dopisz” | to samo + puste slajdy z szablonu (`--dodaj t10,t58`), wstawione przed zakończeniem, w notatkach „NOWY” | wypełniasz [nawiasy] treścią wynikającą z prezentacji, proponujesz brakujące slajdy (miejsce, typ, tekst) oznaczone NOWY. Slajdy oryginału dopracowujesz jak w `wiernie` (3b), treści nie ruszasz, liczb nie wymyślasz |
| `skroc` | „skróć”, „wersja na 15 minut” | to samo; rozdziały spoza `--sekcje` zostają jako slajdy **ukryte**; `--slajdy N` = ile ma zostać w pokazie | **ukrywasz** slajdy, nigdy nie kasujesz. Krótszą wersję albo połączenie dwóch slajdów robisz jako NOWY slajd, oryginały ukrywasz tuż za nim; na końcu lista „Co ukryte i gdzie jest oryginał” |

| Opcja | Znaczenie |
|---|---|
| `--sekcje r01,r02,...` | rozdziały widoczne w pokazie (id z `--tylko-analiza`); pozostałe **zostają w pliku jako slajdy ukryte** (nic nie znika). Domyślnie wszystkie widoczne |
| `--slajdy N` | cel `skroc`: docelowa liczba slajdów w pokazie (trafia do polecenia dla AI) |
| `--dodaj t10,t58,...` | cel `rozwin`: puste slajdy z szablonu do dołożenia (lista id: `--tylko-analiza`) |
| `--bez-wizualizacji` | nie dokładaj packshotów z biblioteki produktów na slajdach portfolio |
| `--wyjscie <katalog>` | gdzie zapisać wynik (domyślnie obok pliku źródłowego) |
| `--tylko-analiza` | pokaż, co program znalazł: slajdy, akapity, grafiki, tabele, wykresy, rozdziały, bibliotekę wizualizacji |
| `--robocze <katalog>` | katalog roboczy konwersji (`raport.json`, spec, zrzuty, obrazy z oryginału); domyślnie `<folder pliku>\_robocze\<nazwa>` |
| `--bez-oka` | nie poprawiaj układu po obejrzeniu zrzutów (domyślnie program ocenia zrzuty slajdów i zmienia układ slajdów z usterkami wyglądu, do 2 rund) |
| `--bez-qa`, `--json` | jak przy folderze produktu |

Wynik: `<nazwa pliku> - nowy styl.pptx` (cel `rozwin`: `… - nowy styl - rozwinięta.pptx`, `skroc`: `… - nowy styl -
skrót.pptx`) obok źródła; raport i zrzuty w `<folder pliku>\_robocze\<nazwa pliku>\` (`raport.json`, `qa\...\s01.png`,
`spec_program.json`, `img\` z obrazami z oryginału, `wielkosc-liter.txt`); obok wyniku podfolder `plansze\` (obrazy slajdów po 6 na planszę, do załączenia w czacie bez dostępu do plików). Plik źródłowy nie jest zmieniany.

**Co program gwarantuje.** Czyta wszystko: teksty (także w grupach i SmartArt), tabele, wykresy (zostają edytowalne),
obrazy w całości (także zdjęcia wstawione jako wypełnienie kształtu - eksport z Canvy; obrazy nachodzące na siebie
składa w jeden kolaż), hiperłącza, notatki prelegenta, sekcje. Tekst leżący obok slajdu (poza kadrem) przenosi do
notatek. Układ bierze z pozycji pól na starym slajdzie: kolumny zostają kolumnami, drobne etykiety pod kolumną zostają
osobnymi znacznikami, słowa wyróżnione kolorem zostają wyróżnione. Slajd dzieli tylko wtedy, gdy tekst nie mieści się
pismem 13 pt, i pisze o tym. Literówek nie poprawia, ale ostrzega w uwagach („Możliwe błędy w tekście oryginału”); poprawiasz je Ty (3b, pkt 5). Gdy oryginał wyświetla wersaliki, ustawia zwykłą wielkość liter
i wypisuje zmiany w `wielkosc-liter.txt`. Pomija tylko logo i belki stojące w tym samym miejscu na większości slajdów,
drobne ozdobniki oraz animacje i tła (mówi o tym w uwagach). Stary styl nie jest dostępny dla konwersji. Potem układa tekst w klocki szablonu (hasła, liczby-bohaterowie, pasy-wnioski, kafle z ikonami z zestawu marki), a po zbudowaniu ogląda zrzuty i zmienia układ slajdów z usterkami wyglądu (pusty dół, puste karty, tekst przy krawędzi).

**Dwie kontrole na końcu - obie muszą być czyste, inaczej nie oddawaj:**
- `Treść: 100% akapitów (N/N) przeniesionych` - są wszystkie słowa;
- `Układ: osobne napisy X z X, kolejność góra-dół bez zmian, liczby X z X, slajdów tyle samo (N)` - osobne napisy są
  osobno, to, co stało wyżej, nadal jest wyżej, są wszystkie liczby.

**Wizualizacje.** Na slajdach portfolio (kolumny z nazwami linii, tytuł „Kulki”, „Batony”…) program dokłada gotowe
packshoty z biblioteki `01 - PRODUKTY\- DK` - tylko gdy każda kolumna ma pewne dopasowanie - i wypisuje, które produkty
wstawił. Pokaż tę listę użytkownikowi: słownik nazw linii (`skill-prezentacje\assets\linie-aliasy.json`) to założenie.

Twoja część po konwersji (pary stary | nowy, poprawki, kontrola, lista „DO DECYZJI”): sekcja 3b niżej.

## 3a-2. Dokument zamiast prezentacji (.docx, .doc, .rtf, .odt, .pdf, .txt, .md)

Użytkownik podał dokument tekstowy? Ten sam program zrobi z niego prezentację w stylu Dobra Kaloria:

```
& "<folder programu>\pliki programu\stworz-cli.exe" "<plik.docx>" [--slajdy N] [--rozdzialy N]
```

Bez `--slajdy` i `--rozdzialy` program bierze wartości domyślne (dobre w większości przypadków). `--rozdzialy 0` = bez
przekładek. Program niczego nie dopisuje i nie gubi (wiersz „Treść: 100%”); o możliwych błędach w tekście dokumentu
tylko ostrzega. Skan bez tekstu nie zostanie odczytany - powiedz to użytkownikowi. Wynik dopracowujesz tak samo jak
po konwersji (sekcja 3b).

## 3a-3. Plik już w stylu Dobra Kaloria (szablon, wynik programu)

Takiego pliku program nie konwertuje drugi raz. `stworz-cli.exe "<plik.pptx>"` wypisze przegląd: możliwe błędy
w tekście, slajdy z podpowiedziami w [nawiasach], usterki wyglądu - i NIE zmieni pliku. Dopracowujesz go sam według
sekcji 3b, na kopii `<nazwa> - dopracowana.pptx`. `--mimo-to` wymusza konwersję (prawie nigdy nie jest potrzebne).

## 3b. Konwersja gotowej prezentacji: jak dopracować wynik

W razie sprzeczności wygrywa `skill-prezentacje\references\dopracowanie.md` (pełna metoda; poniżej jej skrót w tej samej kolejności). Starsze zapisy „zdania w Lato”, „bez wyjmowania liczb do kafli”, „akapit = karta-artykuł” są nieaktualne od 13.10.2026.

Na końcu raportu przypomnij użytkownikowi: „Masz Claude na komputerze? Otwórz plik w PowerPoincie i użyj wtyczki Claude (Claude for Microsoft 365) - wklej to samo polecenie, poprawi slajdy od razu w pliku.”

Program robi **szkic** (ten sam slajd w stylu marki, 100% treści, hasła i liczby wstępnie wyciągnięte, układ z klocków szablonu). Dopracowujesz go Ty - a o firmie nic nie wiesz, więc oto skąd brać wiedzę, według czego oceniać i czego nie wolno ruszać. **Dobra Kaloria** = polska marka przekąsek (kulki, batony…); jej prezentacje to deck handlowy i strategiczny, a wzorem wyglądu jest sklep dobrakaloria.pl.

**Skąd wiedza (czytaj, nie zgaduj).** (1) Skill `/prezentacje` (KROK 0): `SKILL.md` sekcje 0 i 1b, **`references\dopracowanie.md`** (metoda dopracowania - czytasz ją pierwszą i w całości), **`references\katalog-szablonu.md`** (tabela „kształt treści -> slajd szablonu” i 65 slajdów z „użyj gdy / nie gdy”), `references\konwersja-pptx.md` (zasady, pułapki, pkt 2a i 2b), `references\lekcje.md` A27-A44 (decyzje właściciela) - kopia zawsze leży w `<folder programu>\skill-prezentacje\`. (2) Design system: `%USERPROFILE%\.claude\skills\ds-dobra-kaloria\DESIGN-SYSTEM-DOBRA-KALORIA.md` (§2 zasady, §5.4 prezentacje PPTX); **nie masz go** (to osobny skill, program nie kopiuje go w całości) - wystarczy 10 reguł niżej. (3) Wzorzec układów: `references\katalog-szablonu.md` (65 slajdów „tNN Nazwa” i tabela kształt treści -> wzór; format opisu klocków: `references\spec-dk.md`) oraz, do obejrzenia, pełny szablon (65 slajdów) `pliki programu\DK - szablon prezentacji - pełen.pptx`. Krótki plik `DK - szablon prezentacji.pptx` obok programu (7 slajdów, po jednej opcji: okładka, punkty, tekst i zdjęcie, produkt i zalety, trzy liczby i wniosek, porównanie, zakończenie) jest dla ludzi - nie traktuj go jako pełnej listy możliwości.

**10 reguł stylu Dobra Kaloria w prezentacji.**

1. Tło slajdu **białe**; bieli jest najwięcej. Beż, ecru i szary nigdy jako tło całego slajdu.
2. **Kremowy** (ecru `#FDF8EC`) tylko jako karta albo kafel na bieli. Głębiej niż karta w karcie nie schodzisz.
3. **Hasła w Mindset** (nagłówkowa, wersaliki): zdanie do 12 słów albo początek dłuższego zdania.
4. **Lato** tylko jako krótki dopisek pod hasłem, najwyżej 18 pt; akapit Lato bez hasła to błąd poza wyjątkami z `dopracowanie.md` pkt 3 (czego hasłowanie nie dotyczy).
5. Tekst ciemny z motywu (nie czysta czerń); drobne podpisy i etykiety w beżu motywu.
6. **Zieleń marki** `#007936` (w motywie PPTX: slot Akcent 1) na tytuły, kropki, metki. Czerwień motywu to tylko akcent
   i wyróżnione słowo - jeśli było wyróżnione w oryginale.
7. **Żółty** `#FFD821` to jedna wyróżniona akcja na widok; w konwersji zwykle wcale.
8. **Bez obrysów** wokół kart, kafli i tagów (karta = wypełnienie). Ikony liniowe, zielone. Zero plam i bąbelków za produktem.
9. Kolory i czcionki **tylko ze slotów motywu** (Projektowanie > Warianty), bez własnych kodów hex; kolory smaków produktu to wyjątek.
10. **1:1** (niżej): slajd to ten sam slajd, tylko w nowym wyglądzie i z tymi samymi słowami w nowych rolach.

**1. Skąd ta metoda (13.10.2026).** Właściciel odrzucił dwie wersje tej samej prezentacji i przyjął trzecią. Odrzucona 1 (sam tekst w Mindset na całą szerokość): „tekst jednolity, bez sensownych akapitów, podnagłówków, widać, że to nie jest z szablonu”. Odrzucona 2 (zdania jako akapity Lato w kartach): „Za dużo czcionki Lato. Za mało tam jest prezentacji, za dużo tekstu, bloków tekstu. Za mało jakichś haseł.” Przyjęta 3 (hasła, liczby, wnioski w klockach szablonu): „TAK! teraz ta prezentacja jest cudownie piękna.” O błędach tekstu: „Tego typu błędy, literówki, sieroty itp. - POPRAWIASZ.”

**2. Zasada naczelna: slajd to plakat, nie kartka.** Na slajdzie widać: tytuł, 1-4 hasła w Mindset, przy nich liczbę albo ikonę, pod hasłem krótki dopisek w Lato, na dole wniosek w pasie. Słowa autora zostają wszystkie i w tej samej kolejności; zmienia się ich ROLA:

| Rola | Co to jest | Jak wygląda |
|---|---|---|
| hasło | zdanie do 12 słów albo początek dłuższego zdania | `lead`, Mindset, kolor tekstu (ink) |
| dopisek | reszta zdania i kolejne zdania akapitu | `p`, Lato, najwyżej 18 pt |
| liczba-bohater | liczba z jednostką stojąca w haśle, powtórzona nad nim | `hero`, Mindset, zieleń |
| wniosek | ostatnie zdanie-puenta, „Ważna kwestia – …”, „Insight: …”, linia od „=” | `band`, pas zielony (czerwony = zła wiadomość) |
| etykieta | „CT: …”, „TA: …”, „Słodziki:” | `kv` albo nagłówek karty `h` |
| punkt | pozycja listy, kolejne zdanie długiego akapitu | `li` z ikoną albo kafel z ikoną |

Miara kontrolna: w kartach z tekstem więcej słów stoi w Mindset niż w Lato (wzorzec: 492 do 309). Wersaliki robi czcionka Mindset: w specu tekst zostaje w wielkości liter oryginału.

**3. Co wolno, czego nie wolno.** Zostaje bez zmian: liczba slajdów (slajd N = slajd N, właściciel porównuje dwa okna obok siebie), każde słowo i każda liczba, kolejność czytania, obrazy w całości, słowa wyróżnione kolorem przez autora, hiperłącza (zostają na tych samych słowach, bez dopisanej stopki „Link: …”; adres, którego nie ma na slajdzie, idzie do notatek), znaki interpunkcji (przecinek, na którym tniesz zdanie, zostaje przy haśle). Wolno: podzielić zdanie na hasło i dopisek; powtórzyć liczbę z hasła jako liczbę-bohatera nad nim (jedyne dozwolone powtórzenie tekstu); rozdzielić akapit na kafle (jedno zdanie = jeden kafel, najwyżej 4, 4 = siatka 2 x 2); przenieść do pasa pod kartami zdanie-wniosek, które w oryginale i tak stoi najniżej; dać ikonę ze słownika; zrobić z nagłówka slajdu tytuł, a z belki rozdziału etykietę nad tytułem. **Nie wolno:** dodawać ani kasować slajdów, agendy, przekładek; pisać własnych tytułów i haseł; łączyć, dzielić, przestawiać slajdów; dopisywać, skracać ani przestawiać treści; wymyślać liczb; przycinać obrazów; używać kolorów i czcionek spoza motywu; przepisywać tekstu ze zrzutu; zmniejszać pisma, żeby „się zmieściło”; edytować skryptów skilla ani programu (błąd skryptu zgłoś w DO DECYZJI). Zasady „tytuł = wniosek” i „jedna myśl na slajd” dotyczą prezentacji z folderu produktu, **nie konwersji**. Prezentacji, która już jest w stylu DK, nie konwertuj.

**4. Czego hasłowanie nie dotyczy.** Tabela, wykres, slajd z samym zdjęciem albo zrzutem, okładka, przekładka rozdziału, zakończenie, wartości odżywcze, slajd produktu (EAN, gramatura, claimy z karty wprowadzenia) i cytat zostają takie, jakie dał program albo katalog szablonu; sprawdzasz w nich tylko błędy tekstu i czytelność. Nie dzielisz komórek tabeli na hasła i dopiski. Zdanie dłuższe niż 24 słowa bez przecinka i spójnika, na którym da się je podzielić, zostaje akapitem w karcie (jedyny dopuszczalny akapit bez hasła) i trafia do DO DECYZJI.

**5. Błędy w tekście oryginału: poprawiasz.** Tylko gdy spełnione są WSZYSTKIE cztery warunki: a) to, co stoi w źródle, nie jest w tym zdaniu poprawnym polskim słowem lub formą, nazwą, skrótem ani słowem obcym; b) jest jedna oczywista poprawna forma, różna najwyżej o spację albo 2 znaki w jednym słowie; c) słowo nie stoi w cytacie, w tekście obcojęzycznym, w liczbie, w oświadczeniu żywieniowym lub zdrowotnym, w nazwie prawnej ani w hiperłączu; d) nie zmieniasz szyku, stylu ani wielkości liter. Wątpliwość = nie poprawiasz, wpisujesz do DO DECYZJI. Mieszczą się tu: sklejone słowa („komunikacjaod” -> „komunikacja od”), literówki („odwrotem o węglowodanów” -> „odwrotem od węglowodanów”), oczywisty błąd odmiany z sąsiedniego słowa („do zbudowanie trialu” -> „do zbudowania trialu”), zdublowane słowo, brak spacji po przecinku, spacja przed przecinkiem, podwójne spacje. Nie poprawiasz, tylko zgłaszasz: nazw własnych i marek, skrótów, liczb i jednostek, wielokropków i myślników autora, zdań niezręcznych, wszystkiego, co zmienia sens. Sieroty i zawieszki (spójnik albo jedna litera na końcu linii, jedno słowo w ostatniej linii, „ok. / 12 mln”) to błędy łamania, nie tekstu: poprawiasz podziałem hasło / dopisek albo szerokością karty. **Każdą poprawkę wpisz do specu**, inaczej kontrola treści uzna ją za zgubione słowo: `"poprawki": [{"slajd": 12, "bylo": "komunikacjaod", "jest": "komunikacja od", "powod": "sklejone słowa"}]` (`slajd` = numer slajdu oryginału). Zacznij od listy „Możliwe błędy w tekście oryginału” z programu (`bledy_tekstu` w specu i w `raport.json`), potem przeczytaj każdy slajd sam: program łapie tylko słowa spoza słownika, błędu odmiany („kierunku” zamiast „kierunki”) nie zobaczy.

**6. Dobór układu: z katalogu szablonu, nie z głowy.** Dla każdego slajdu nazwij kształt treści i weź wzór z `references\katalog-szablonu.md`; gdy żaden wiersz nie pasuje, złóż układ z tych samych klocków i wpisz slajd do DO DECYZJI. Najczęstsze kształty (typ slajdu `uklad`; klocki: `references\spec-dk.md`):

| Kształt treści | Układ | Wzór w szablonie |
|---|---|---|
| 2-4 fakty, każdy z liczbą | rząd równych kart: `hero` + `lead` + `p`, wniosek w `band` | t62 Trzy fakty w kartach |
| 2-4 zdania, część bez liczby | te same karty; bez liczby = `icon` zamiast `hero` | t62, t56 Okazje spożycia |
| lista 2-6 krótkich haseł | kafle `icon` + `lead` na środku; 4 = 2 x 2; 5 = jeden rząd | t56 Okazje spożycia, t36 |
| jedna teza slajdu | jedna karta `fill: brand`, tekst na środku | t14 Jedno zdanie – teza |
| dwie strony („dobra / zła wiadomość”) | 2 karty: `icon`, nagłówek `h` w kolorze, `lead` | t59 Dwie karty |
| temat + kilka zdań o nim | pas `band` z ikoną NAD kartami, zdania = karty | t62 |
| etykieta: wartość („CT: …”) | rząd kafli `kv` | t45 Logistyka |
| nagłówek + lista zdań | karta: `h` + punkty `li` | t17 Punkty |
| długi akapit (4 i więcej zdań) | karta: etykieta `h`, 1. zdanie = hasło + dopisek, reszta = `li` | t17 Punkty |
| zdanie z 3+ parami „nazwa (NN%)” | hasło + słupki `bars` z tymi samymi nazwami i liczbami | t39 Wykres słupkowy |
| cytat z autorem (+ wynik) | `quote` (+ karta i pas) | t20 Cytat, t60 Cytat i wniosek |
| obrazy + podpis-wniosek | `pics` + `band` | t63 Zrzuty w całości i wniosek |
| zdanie-puenta na końcu | `band` pod kartami | t62, t63 |

**7. Reguły hasłowania i progi pisma.** (1) Zdanie do 12 słów jest hasłem w całości. (2) Dłuższe: hasło kończy się na pierwszym przecinku stojącym po 4-15 słowach (przecinek zostaje przy haśle); gdy go nie ma - przed pierwszym spójnikiem `i / oraz / ale / wobec / czyli` na pozycji 4-15; bez granicy do 24 słów - całe jest hasłem; powyżej 24 - pkt 4. Hasło nie może wyjść puste w treść („WHO (2023) zaleca warunkowo,”) - przesuń granicę. (3) Jedno hasło na kartę w rzędzie trzech i więcej kart; karta z nagłówkiem-hasłem (3+ słowa) dostaje resztę jako dopisek; nagłówek-etykieta (1-2 słowa albo z dwukropkiem) hasła nie blokuje. (4) Liczba-bohater: pierwsza liczba z jednostką (%, mln, mld, zł, g/kg…) stojąca w HAŚLE, jedna na kartę; nie jest bohaterem rok i data, EAN, gramatura opakowania, nazwa z cyfrą (B12, GLP-1), zakres wieku w etykiecie („CT: 20-35”), liczba z oświadczenia żywieniowego. (5) Hasło wyróżnione przez autora kolorem w całości idzie w kolorze tekstu; wyróżnione pojedyncze słowa zostają. (6) Hasło nigdy nie jest mniejsze od dopisku tej samej karty (builder pilnuje: co najmniej + 2 pt). (7) Zielony tekst tylko jako nagłówek-etykieta, liczba albo pas. **Progi:** hasło od 16 pt (cel 18+), dopisek i punkty `li` od 13 pt (cel 14), etykiety od 11 pt; wyjątek: rząd 5-6 kafli z krótkimi hasłami, 14-16 pt. Gdy treść spada poniżej progu, NIE zmniejszasz pisma i nie usuwasz słów - upraszczasz układ w tej kolejności: zdejmij ikony z kart; 4 karty w rzędzie zamień na siatkę 2 x 2; nagłówek karty wynieś jako wiersz nad karty; kolejne zdania długiego akapitu zamień na punkty `li`. Gdy i to nie pomaga: DO DECYZJI (za dużo treści na jeden slajd - decyzja autora, nie Twoja).

**8. Pętla pracy i bramki oddania - dowód, nie raport.** Pracujesz sam, do bramek. (1) Render oryginału i wyniku do PNG, **pojedynczo** (PowerPoint COM nie lubi dwóch naraz):
`powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\pliki programu\app\skill\scripts\render.ps1" -Src "<plik.pptx>" -Out "<katalog png>"`.
Do renderu używasz zawsze `render.ps1` ze skilla, nie `app\app\render_app.ps1`: oba robią to samo (PNG 1600 x 900), ale `render_app.ps1` jest skryptem samego programu (bez Pythona) i **domyślnie zapisuje plik od nowa z osadzonymi czcionkami**, nie zapisując sumy kontrolnej - kolejna budowa uznałaby plik za zmieniony ręcznie i zapisałaby „… (nowa wersja)”. `render.ps1` otwiera plik tylko do odczytu; po OSTATNIEJ zmianie dodaj `-EmbedFonts` (osadza czcionki i zapisuje sumę; wymaga Pythona, który i tak masz do kolejnych kroków). (2) **Plansze par** stary | nowy: `python "<folder programu>\pliki programu\app\skill\scripts\pary_slajdow.py" <png oryginału> <png wyniku> <katalog>` (3 pary na planszę; różna liczba slajdów = błąd). (3) Obejrzyj **każdą planszę** narzędziem do czytania obrazów, najpierw slajdy z listy „Sprawdź najpierw”; dla każdego slajdu 8 pytań: jaki to kształt treści i czy układ jest z katalogu (czy hasłowanie w ogóle go dotyczy)? czy każda karta ma hasło w Mindset, a akapit Lato dłuższy niż 3 linie nie stoi bez hasła? czy najważniejsza liczba jest bohaterem? czy wniosek stoi w pasie? czy pismo trzyma progi z pkt 7? czy nic nie łamie się źle (słowo po słowie w wąskiej karcie, sierota, spójnik na końcu linii)? czy ikona pasuje do treści (jeśli nie - wymień w `assets\ikony-slowa.json` albo zdejmij)? czy są błędy w tekście (pkt 5)? (4) Poprawki wpisujesz w specu (nie w PowerPoincie): `_robocze\<nazwa>\spec_program.json` (to ten sam spec, który polecenia nazywają `spec_konwersja.json`), potem `python "<folder programu>\pliki programu\app\skill\scripts\build_dk.py" <spec>`; po każdej zmianie render i ponowny ogląd, najwyżej 3 podejścia na slajd. Czego nie rozwiążesz - DO DECYZJI z numerem slajdu. (5) `verify.ps1`: `powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\pliki programu\app\skill\scripts\verify.ps1" -Src "<plik.pptx>"` - **`Tekst - problemy: 0`**, bez błędu COM. (6) Raport programu: `Treść: 100% akapitów` (poprawki z pkt 5 zadeklarowane w `poprawki` i przyjęte) oraz kontrola układu: usterki 0, znaki 0, slajdów tyle samo. Po poprawkach tekstu pełną kontrolę (budowa, zrzuty, `verify`, pokrycie z `poprawki`) daje jedno polecenie: `python "<folder programu>\pliki programu\app\skill\scripts\pptx_convert.py" "<plik.pptx>" --ze-specu "<spec>" --robocze "<katalog roboczy>"`. Bez par obejrzanych po ostatniej zmianie i bez tych wyników nie pisz „gotowe”.

**9. Raport dla człowieka i lista „DO DECYZJI” (zawsze na końcu, po polsku, krótko).** (1) Plik wynikowy, liczba slajdów, wyniki bramek. (2) Co zmieniłeś względem wersji z programu: slajd -> wzór z katalogu. (3) Poprawione błędy tekstu: slajd, było -> jest. (4) **DO DECYZJI**: wątpliwe słowa i nazwy; błędy, których nie wolno było poprawić; zmiany wielkości liter z `wielkosc-liter.txt`; wstawione wizualizacje produktów (słownik nazw linii to założenie); slajdy z listy „Sprawdź najpierw” i te, gdzie treść się nie mieści mimo uproszczeń; slajdy z własnym układem (bez wzoru w katalogu); slajdy podzielone, ukryte lub NOWE (ukryte zostają w pliku - przed wysłaniem poza firmę trzeba je usunąć albo zapisać PDF); niepewne ikony i wizualizacje produktów; niejasne dane i [nawiasy] bez źródła; znak „DEMO”.

## 4. Po zbudowaniu — Twoja część pracy

(Dotyczy prezentacji z folderu produktu. Dla konwersji `.pptx`: sekcja 3b.)

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
   powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\pliki programu\app\skill\scripts\render.ps1" -Src "<plik.pptx>" -Out "<katalog png>"
   ```

   (`render.ps1` otwiera plik tylko do odczytu; po OSTATNIEJ zmianie dodaj `-EmbedFonts` - osadza czcionki, wymaga Pythona.)

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
