# Prezentacja z dokumentu (docx, doc, rtf, odt, pdf, txt, md) - `scripts/dokument.py` (13.10.2026)

Dla ludzi i dla AI. Program robi z dokumentu tekstowego prezentację w stylu Dobra Kaloria **bez LLM, bez gubienia i bez wymyślania
treści**: slajdy z pełnego szablonu (`katalog-szablonu.md`), plakat zamiast kartki (hasło Mindset + dopisek Lato, liczba-bohater, pas-wniosek,
kafle z ikonami - reguły S1-S15 z `szablonuj.py`, metoda: `dopracowanie.md`). Człowiek wybiera dwa suwaki: **liczbę slajdów** i **liczbę rozdziałów**.

```powershell
python "$env:USERPROFILE\.claude\skills\prezentacje\scripts\dokument.py" "<plik>" [--slajdy N] [--rozdzialy N] [--wyjscie K] [--robocze K] [--bez-qa]
```

W kodzie (kontrakt stały, okno programu stoi na nim):

```python
import dokument
m    = dokument.wczytaj(plik, rob)          # {"nazwa", "tytul", "bloki": [{"typ": h1|h2|h3|p|li|tabela|obraz|cytat, "t", "poziom", ...}], "ostrzezenia"}
s    = dokument.statystyka(m)               # zakresy suwaków Z DOKUMENTU: slajdy_min / slajdy_domyslnie / slajdy_max, rozdzialy_max (+ słowa, nagłówki...)
spec = dokument.zloz(m, {"slajdy": N, "rozdzialy": R, "wyjscie": katalog, "styl": "nowy"})   # spec dla build_dk.build
pok  = dokument.pokrycie(m, pptx)           # "Treść: 100% akapitów (N/N) przeniesionych" (opcjonalnie mapa_blokow ze specu)
# po renderze (okno i CLI): pętla „oko” - inny wariant układu tam, gdzie kontrole widzą usterkę
(us, v), poprawione = dokument.petla_poprawek(spec, pomiar, buduj)   # pomiar() -> (usterki_po_renderze(png, spec, verify_tekst), verify_tekst); buduj() = build_dk.build(spec, ...)
```

Pętla (`petla_poprawek`, do 2 rund) bierze usterki wagi >= 2 z `oko.py` (PUSTY_DOL, KARTA_PUSTA...) i z `verify.ps1` (PRZEPELNIENIE, SIEROTA, ZAWIESZKA...), podmienia slajd na
następnego kandydata układu (`szablonuj.inny_wariant`, kandydaci w `spec["warianty"]`), buduje plik jeszcze raz i zostawia zmianę tylko tam, gdzie slajd ma mniej usterek (inaczej cofa).
CLI robi to samo (`dokument.py <plik>` bez `--bez-qa`: render, pętla, „Kontrola układu (oko)”, „Tekst - problemy: N”).

## Formaty

| Format | Jak czytamy | Uwagi |
|---|---|---|
| docx | OOXML bezpośrednio (zipfile + lxml, bez python-docx): style nagłówków (Nagłówek 1-3, Tytuł, Podtytuł), poziom konspektu, listy (punktowane / numerowane), tabele, obrazy z relacji, cytaty (styl Cytat) | Dokument **bez stylów**: krótki akapit pogrubiony, większy albo WERSALIKAMI, bez kropki = nagłówek. Spis treści pomijamy (jest agenda programu) |
| doc, rtf, odt | Microsoft Word przez COM, w **własnej** instancji bez okna (`New-Object -ComObject Word.Application` z PowerShella; Word użytkownika zostaje, zamykamy tylko własny) -> kopia docx w katalogu roboczym | Bez Worda: czytelny komunikat. Bez pywin32 |
| pdf | PyMuPDF (`fitz`): rozmiar pisma -> poziom nagłówka, sklejanie linii w akapity, dzielenie wyrazów, punktory, tabele (`find_tables`), obrazy > 200 px, usuwanie powtarzalnych nagłówków i stopek stron oraz numerów stron. Zapas: `pypdf` (sam tekst), potem Word | W paczce programu `fitz` / `pypdf` na razie nie ma - patrz „Ograniczenia” |
| txt, md | md: `#`, listy, tabele `\|`, cytaty `>`, obrazy; txt: WERSALIKI, numeracja `1.2`, krótki wiersz bez kropki przed dłuższym akapitem = nagłówek; puste linie dzielą akapity; kilka krótkich linii bez kropek pod sobą = lista | Kodowanie UTF-8 albo cp1250 |

Skan bez tekstu (pdf z samymi obrazami) = „To skan bez tekstu - program nie czyta obrazów…”. Dokument > 60 000 słów = rada podziału. Pusty dokument = okładka i zakończenie, bez wyjątku.

## Reguły składania (1-6)

1. **Szkielet**: okładka (tytuł dokumentu = akapit „Tytuł” albo jedyny / pierwszy nagłówek 1 będący stroną tytułową, inaczej nazwa pliku bez podkreślników; podtytuł =
   pierwszy krótki akapit pod tytułem; tytuł dłuższy niż 44 znaki dostaje okładkę z jednym zdaniem na środku - `statement` t14, bo `cover_text` nie mieści długiego tytułu),
   agenda (gdy rozdziałów >= 3, do 8), przekładki rozdziałów (`section`, numer 01, 02…), slajdy treści, zakończenie
   (`end`, #zawszedobra). Rozdział = nagłówek: najwyższy poziomem, przy równym - najdłuższy.
2. **Slajd treści**: tytuł = nagłówek sekcji (nadrzędny nagłówek jako etykieta nad nim). **Sekcja na 1-2 slajdy**: kolejny slajd = „Nagłówek (2)”. **Sekcja rozciągnięta
   na więcej niż 2 slajdy** (i dokument płaski) nie dostaje numerków „(3)…(9)”: pierwszy slajd sekcji zostaje z nagłówkiem, na kolejnych **nazwa sekcji stoi nad tytułem**
   (etykieta, za długa skracana do pełnych słów i „…”; w dokumencie płaskim - tytuł dokumentu), a **tytułem jest hasło z pierwszego zdania slajdu** (`szablonuj.haslo_cut`, słowa
   dokumentu; reszta tego zdania jest dopiskiem w karcie). Hasło nie zostaje tytułem, gdy ma liczbę-bohatera (fakt zostaje kartą z liczbą), zaczyna się od liczby i małej litery
   („1 łyżeczka…”), jest ucięte po „:” albo dłuższe niż 15 słów / 100 znaków, a także gdy slajd zaczyna się od listy - wtedy zostaje „Nagłówek (n)”. Sekcja bez nagłówka
   = tytuł dokumentu. Tytułów nie wymyślamy. Wiersze `uklad` składa `szablonuj.stosuj` (hasła, liczby-bohaterowie, pasy, kafle,
   punkty z ikoną) z wyborem wariantu z pomiaru (`szablonuj.ocena`); gdy nie ma reguły - układ ręczny z tych samych klocków.
   Tabela -> `table` (t42, do 6 kolumn i 8 wierszy na slajd, dłuższa dzieli się z powtórzonym nagłówkiem; komórki dłuższe niż linia -> karty
   „nagłówek - treść”), cytat -> `quote` (t20), obrazy -> `pics` (t26 / t63 / t28; akapit pod obrazem do 15 słów = podpis, zapowiedź z „:” nad
   obrazem dołącza do podpisu), numerowana lista 2-5 pozycji -> kroki (t19, numer-bohater), 2-6 krótkich haseł (do 6 słów; z liczbą do 4, np. „300 g wody”; kilka krótkich akapitów bez kropki pod rząd to też lista) -> kafle z ikonami (t56), lista +
   zdanie na końcu -> kafle + pas, zdanie wprowadzające + lista -> karta z punktami (t17), jedna teza -> zielona karta (t14), fakt z liczbą -> karta z liczbą (t37 / t62).
3. **Suwak „slajdy”** = slajdy **z treścią** (okładka, agenda, przekładki i zakończenie dochodzą: razem w pliku = wartość + ramka, wynik w `spec["ustawienia"]`).
   `statystyka`: min = najgęściej bez łamania progów (max 110 słów i 4 kart na slajd, hasło od 16 pt, dopisek od 13 pt; sekcje się nie łączą), max = jedna
   myśl (zdanie) na slajd, najwyżej 80, **domyślnie** ok. 1 slajd na 45 słów treści i nie rzadziej niż na 5 zdań (`max(słowa/45, zdania/5)`, w granicach min-max): slajd
   niesie 2-3 myśli jako 2-3 karty obok siebie (hasło + dopisek w każdej; wniosek idzie w pas), nie jedną kartę z pustą połową. „Najkrócej” to świadomy wybór min, „jedna myśl na slajd”
   - max. Zdania jednego akapitu dzielą się na karty wg słów (do 26 słów jedna karta, do 48 dwie, dalej trzy; `_ile_kart`), kolejne akapity to kolejne karty. Przekładki rozdziałów
   domyślnie tylko od 9 slajdów treści i średnio >= 3 slajdy na rozdział.
   Cięcie tylko między zdaniami, najchętniej między akapitami. Gdy czytelność wymusi więcej slajdów, wychodzi N+k i `uwagi` to mówią.
4. **Zawsze 100 %**: żadna wartość suwaka nie gubi treści (`pokrycie` na min, domyślnej i max); jedyne powtórzenia to liczba-bohater i numery kroków.
5. **Typografia i błędy tekstu**: `lint_tekst.sprawdz` -> `spec["bledy_tekstu"]` i linie w `uwagi`. Program **nie poprawia** tekstu dokumentu (poprawia AI według
   `dopracowanie.md` pkt 4 albo autor w pliku). Zawieszki / sieroty łamie builder.
6. **Niczego nie wymyślamy**: żadnych własnych tytułów, wniosków, liczb; podpowiedzi w [nawiasach] nie dodajemy.

## Ograniczenia (czego reguły nie pokonują)

- **Źródło bez struktury** (tekst z wyeksportowanych slajdów, strony WWW wklejone do Worda): setki mikro-akapitów dają dużo małych slajdów (`slajdy_min` bywa większe
  niż 80); to jest wierne odwzorowanie, nie błąd. Dodaj nagłówki w dokumencie.
- **Tytuły bez nagłówków**: dokument płaski ma tytuł dokumentu nad tytułem slajdu (tytuł slajdu = hasło z jego pierwszego zdania); gdy hasła nie da się wyciąć (zdanie > 15 słów
  bez przecinka, liczba-bohater, lista na początku slajdu), zostaje „Raport (3)”. Slajdy niebędące tekstem (tabela, cytat, obraz) w sekcji > 2 slajdy też mają „Nagłówek (n)”.
- **Pola tekstowe i przypisy dolne** w docx nie są czytane (program ostrzega); spis treści pomijamy.
- **Tabele**: wielokolumnowa tabela tekstowa staje się kartami „kolumna = karta” (kolejność komórek: kolumnami); obraz tabeli w pdf-ie (skan) nie jest czytany.
- **PDF w paczce programu**: dopisz `pymupdf` (najlepiej) albo `pypdf` do `HIDDEN` w `stworz_cli.spec` i `stworz_gui.spec`; bez nich pdf czyta Word (może się zawiesić na
  oknie konwersji - limit 60 s, zabijamy tylko własną instancję).
- **Po pętli poprawek zostają pojedyncze usterki kontroli tekstu**, których zmiana wariantu nie naprawia: sierota w ostatnim słowie hasła w wąskiej karcie („300 G / WODY”,
  pojedyncze długie słowo), przepełnienie pola o 2-3 pt (szacunek buildera vs PowerPoint) i słowa sklejone w źródle („energiijako”, `lint_tekst` je zgłasza). Raport pokazuje je z numerem slajdu.
- **Etykieta nad tytułem** (nagłówek nadrzędny) ma jedną linię (do 52 znaków): dłuższa trafia do tytułu („Nadrzędny - Nagłówek”). **Agenda** tylko gdy nazwy rozdziałów mieszczą się w punkcie
  (do 70 znaków przy 3-4 rozdziałach, do 34 przy 5-8); inaczej bez agendy, przekładki zostają.
- Czas (zmierzony): `statystyka` < 10 ms; `zloz` 1-2 s dla 500-1100 słów, ok. 10 s dla 3500 słów (pamięć podręczna pomiaru tekstu); zimny start +3 s (import).
