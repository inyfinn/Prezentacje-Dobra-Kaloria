# Prezentacja z dokumentu (docx, doc, rtf, odt, pdf, txt, md) - `scripts/dokument.py` (13.10.2026, przebudowa 21.10.2026)

Dla ludzi i dla AI. Program robi z dokumentu tekstowego prezentację w stylu Dobra Kaloria **bez LLM**: slajdy to **streszczenie
strukturalne** dokumentu (liczby, tabele skrócone, listy jako hasła z dopiskiem, pary etykieta: wartość, karty, pytania), a **pełny tekst
dokumentu stoi w notatkach prelegenta** każdego slajdu (słowo w słowo, w kolejności dokumentu). Niczego nie wymyślamy i niczego nie gubimy:
pokrycie 100% liczy slajdy + notatki. Człowiek wybiera dwa suwaki: **ile slajdów** i **podział na rozdziały**.

Dlaczego tak (21.10.2026): raport dla zarządu (11 stron, 2 800 słów) dał w wersji 1.2.3 146 slajdów pociętego tekstu, bo program czytał PDF
bez tabel (0 z 10), brał etykiety i metki za nagłówki (109 fałszywych) i kładł każdy akapit na slajd. Wzorce (kreatynki, strategia) mają
30-36 słów na slajd; 12-18 slajdów z takiego dokumentu mieści ok. 20-30% tekstu - reszta musi być w notatkach.

```powershell
python "$env:USERPROFILE\.claude\skills\prezentacje\scripts\dokument.py" "<plik>" [--slajdy N] [--rozdzialy N] [--wyjscie K] [--robocze K] [--bez-qa]
```

W kodzie (kontrakt stały, okno programu stoi na nim):

```python
import dokument
m    = dokument.wczytaj(plik, rob)          # {"nazwa", "tytul", "bloki": [{"typ": h1|h2|h3|p|li|tabela|obraz|cytat|kpi|kv, ...}], "ostrzezenia"}
s    = dokument.statystyka(m)               # zakresy suwaków Z DOKUMENTU: slajdy_min / slajdy_domyslnie / slajdy_max, rozdzialy_max, na_slajdach {min, domyslnie, max} (%)
pl   = dokument.plan(m, N)                  # rozdziały, nośniki, wybór N (do diagnozy; zloz woła go sam)
spec = dokument.zloz(m, {"slajdy": N, "rozdzialy": R, "wyjscie": katalog, "styl": "nowy"})   # spec dla build_dk.build; każdy slajd ma `notes`
pok  = dokument.pokrycie(m, pptx)           # "Treść: 100% akapitów (N/N) w pliku (slajdy i notatki prelegenta); na slajdach ok. X% słów"
(us, v), poprawione = dokument.petla_poprawek(spec, pomiar, buduj)   # pętla „oko” po renderze (bez zmian)
```

## Formaty

| Format | Jak czytamy | Uwagi |
|---|---|---|
| docx | OOXML bezpośrednio (zipfile + lxml): style nagłówków, poziom konspektu, listy, tabele, obrazy, cytaty | Bez stylów: krótki akapit pogrubiony / większy / WERSALIKAMI bez kropki = nagłówek; spis treści pomijamy |
| doc, rtf, odt | Word przez COM we własnej instancji -> kopia docx w katalogu roboczym | Bez Worda: czytelny komunikat |
| pdf | PyMuPDF (`fitz`). **Pojemniki z wypełnień** (`get_drawings`): karta = sekcja (pierwsza linia pismem ozdobnym = nagłówek), rząd >= 3 równych kafli = blok `kpi` (liczba + opis) albo `kv`, biały prostokąt z liniami pod komórkami = **tabela** (kolumny z segmentów linii, nagłówek = wiersz w całości ozdobny / pogrubiony; 2 kolumny z etykietą WERSALIKAMI = `kv`), wąski prostokąt z 1-2 słowami = metka (nigdy nagłówek), kropka przed linią = punkt; dwie szpalty tekstu bez pojemników = kolumny. **Pismo ozdobne** (druga rodzina pisma, np. Mindset jako Type3) = nagłówki: największe na stronie 1 = tytuł, >= 1,4 x podstawowe na stronie = rozdział (h2), pierwsza linia karty = podrozdział (h3); pogrubione pytanie „…?” = h3 FAQ. **Strona tytułowa** (<= 90 słów, największe pismo, bez innych nagłówków) = okładka: etykieta nad tytułem, tytuł, podtytuł, meta (kafle AUTOR / STAN NA, data). **Logo** = obraz w pasie 15% góry / dołu strony węższy niż 1/4 strony - pomijany. PDF bez wypełnień i bez drugiego pisma (eksport z Worda): rozmiar pisma >= 1,35 x podstawowe = nagłówek, tabele przez `find_tables` z liniami. Zapas: `pypdf` (sam tekst), potem Word |
| txt, md | md: `#`, listy, tabele `\|`, cytaty `>`, obrazy; txt: WERSALIKI, numeracja, krótki wiersz bez kropki przed akapitem = nagłówek | UTF-8 albo cp1250 |

Skan bez tekstu = „To skan bez tekstu…”. Dokument > 60 000 słów = rada podziału. Pusty dokument = okładka i zakończenie.

## Plan: rozdziały, nośniki, budżet (sekcja 3 w `dokument.py`)

1. **Rozdziały** = sekcje najwyższego poziomu z nagłówkiem (w pdf DK: strony); krótsze niż 40 słów doklejają się (sam wstęp do następnego,
   inne do poprzedniego). Tytułów nie wymyślamy.
2. **Nośniki** (jednostki, z których każda daje jeden slajd z katalogu szablonu), ranga = kolejność ważności:

   | Nośnik | Ranga | Slajd | Na slajdzie | W notatkach |
   |---|---|---|---|---|
   | `kpi` (rząd kafli z liczbą) | 1 | t62 karty liczba-bohater + hasło (+ pas) | do 4 kafli | reszta |
   | tabela o kształcie **tabeli** (>= 3 sensowne kolumny) | 2 | t42 `table`: pierwsza kolumna + druga + najkrótsze do 3 (Szczegółowo 4) kolumn, do 6 (8) wierszy, komórka = pierwsza pełna fraza do 7 słów; kolumna, w której > 1/3 komórek nie ma pełnej frazy, znika | skrót | pełna tabela wiersz po wierszu |
   | tabela z **kolumną liczb** (<= 6 wierszy) | 2 | t62 karty: liczba + nazwa (3 + 3) | nazwa + liczba | reszta komórek |
   | tabela z **kolumną dat** (2 kolumny) | 2 | t43 oś czasu: data, nazwa, reszta | | pełne komórki |
   | tabela z **kolumną tak / nie / częściowo** | 2 | karty: jedna na wartość, pozycje z ikoną ✓ – ✗ | | reszta |
   | tabela 2 kolumny krótkich wartości | 2 | t45 kafle etykieta: wartość | do 8 | reszta |
   | **siatka** (>= 3 sąsiednie karty z `kv` o wspólnych etykietach, np. karty programów, także przez nagłówek „(cd.)”) | 2 | karty: nazwa + do 3 wspólnych par | | wszystkie pary |
   | lista z liczbami (>= 2 pozycje z liczbą) | 2 | kafle: hasło (pierwsza fraza do 6 słów) + dopisek Lato do 16 słów; ikona na wszystkich kaflach albo na żadnym; 1-4 w rzędzie, 5 = 3 + 2, 6 = 3 + 3 | do 6 pozycji | reszta |
   | lista, lista numerowana (kroki z numerem), `kv` >= 3 par, karty (>= 2 podsekcje po 1-2 akapity), cytat | 3 | jw. / t19 / t45 / karty z hasłem i dopiskiem / t20 | | |
   | FAQ (>= 2 podsekcje-pytania „…?”) | 4 | karty: pytanie + pierwsza fraza odpowiedzi, 5 na slajd (3 + 2) | | pełne odpowiedzi |
   | akapity (`tekst`) | 5 (2, gdy rozdział ma sam tekst) | t61 karta: hasło (`haslo_cut`) + dopisek do 25 słów; jedno zdanie <= 10 słów = zielona karta | pierwszy akapit | reszta |

   Akapit przed pierwszym nośnikiem sekcji = **wstęp**, po nim = **komentarz**: pierwsze zdanie (albo jego pierwsza fraza) <= 12 słów idzie jako
   **pas-wniosek** pod treść nośnika; dłuższe tylko do notatek (na zieleń nigdy nie trafia tekst > 12 słów, zielona karta > 10 słów - twarda bramka).
   Wstęp / komentarz >= 12 słów jest też osobną częścią „Szczegółowo” (karta hasło + dopisek).
3. **Ranga 0 (zawsze na slajdzie, także „Krótko”)**: nośniki sekcji i rozdziałów o nagłówku z „decyz”, „wniosk”, „rekomend”, „podsumow”, „plan”,
   „następne kroki” oraz najlepszy nośnik ostatniego rozdziału (poza FAQ).
4. **Budżet = suwak „Ile slajdów”** (slajdy z treścią; okładka, spis treści, slajdy tytułowe rozdziałów i zakończenie dochodzą):
   - min („Krótko”) = najlepszy nośnik każdego rozdziału + nośniki rangi 0;
   - domyślnie („Standardowo”) = min + nośniki rangi 1-2 (liczby, tabele, siatki, listy z liczbami);
   - max („Szczegółowo”) = wszystkie nośniki + dalsze części (kolejne 8 wierszy tabeli, kolejne pytania FAQ, kolejne akapity, wstępy), najwyżej 80.
   Nośniki wchodzą według rangi, przy równej w kolejności dokumentu; nośnik niewybrany idzie w całości do notatek poprzedniego wybranego slajdu
   (uwaga „W notatkach prelegenta (nie na slajdach): …”). `statystyka["na_slajdach"]` = procent słów na slajdach dla min / domyślnie / max.
   **Twarda bramka**: slajdów treści nigdy więcej niż ustawienie (`RuntimeError` zamiast nadwyżki; nośnik, który się nie mieści, dostaje mniej
   pozycji / bez dopisków, w ostateczności `flow`, nigdy dodatkowy slajd).
5. **Cięcie tekstu** (`_fraza`, `_czlon`): tylko na granicy pełnej frazy (przecinek, średnik, dwukropek, „ – ”, koniec zdania); tekst na slajdzie
   nigdy nie kończy się spójnikiem, przyimkiem ani otwartym nawiasem; bez granicy - cięcie przed ostatnim przyimkiem w zasięgu; dwa wiersze
   tabeli o tej samej nazwie dostają dłuższy człon. Słowa zawsze z dokumentu, w jego kolejności.
6. **Suwak „Podział na rozdziały”**: 0 = slajdy jeden za drugim; N = N rozdziałów (największe, w kolejności dokumentu) dostaje zielony slajd z samym
   tytułem, od 3 także spis treści (gdy nazwy mieszczą się w punkcie). Domyślnie 0, chyba że rozdział ma średnio >= 3 slajdy.
7. **Tytuły**: slajd = nagłówek sekcji nośnika, nad nim nazwa rozdziału (<= 52 znaki; dłuższa dopisana do tytułu); dalsze części „Tytuł (2)”.
   Okładka t09 (jasna): etykieta nad tytułem, tytuł, podtytuł = pierwsza fraza pierwszego akapitu (do 14 słów), autor i data w stopce.
8. **Typografia i błędy tekstu**: `lint_tekst.sprawdz` -> `spec["bledy_tekstu"]`; program nie poprawia tekstu (robi to AI według `dopracowanie.md`).

## Ograniczenia

- Wagę treści poza typem nośnika program ocenia tylko regułą rangi 0 (słowa w nagłówku) - akapit ważny dla zarządu bez takiego nagłówka pokaże się
  dopiero przy „Szczegółowo”; sterowanie: suwak, a dopracowanie przez polecenie dla AI.
- Tabela t42 ma pismo 13 pt przy 6 wierszach i zostawia pusty dół (`build_dk.s_table` powiększa pismo tylko do 7 wierszy łącznie) - zmiana wymaga
  edycji `build_dk.py`.
- PDF: pojemniki wymagają wypełnień (eksport z HTML / DK); PDF z Worda czyta się rozmiarem pisma i `find_tables` z liniami. Pismo ozdobne
  rozpoznajemy po rodzinie innej niż podstawowa (>= 2% znaków). Kolumny tekstu: do 4 szpalt bez pojemników.
- Etykieta nad tytułem ma jedną linię (do 52 znaków); spis treści tylko, gdy nazwy rozdziałów mieszczą się w punkcie (70 / 34 znaki).
- Czas: `statystyka` liczy trzy plany bez pomiaru układu (< 0,1 s); `zloz` mierzy układ każdego slajdu (1-2 s na slajd).
