# Stwórz prezentację — instrukcja dla AI

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
| `*.docx` (copy) | akapity tekstu i liczby z badania |
| `Wizualizacje\` | packshoty (PNG) |
| `Elementy\` | owoce, kulki, listki dorysowywane wokół paczki |
| inne `*.xlsx` (np. OMNIBUS) | nazwa badania do stopki źródła |

Bez kart wprowadzenia program odmawia — wtedy powiedz użytkownikowi, czego brakuje.

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

5. Zasady treści (skrót): tytuł slajdu = wniosek, nie temat; jeden slajd = jedna myśl; liczby ze źródłem w stopce;
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
