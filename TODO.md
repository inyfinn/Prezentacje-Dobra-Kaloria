# Do zrobienia

Stan na 30.09.2026, program w wersji 1.1.1. Kolejność = priorytet.

## Zasada: każde wydanie przechodzi test „u innych” przed publikacją

`program/testy/test_u_innych.ps1 -Zip <zip> -Sieci <M:...>,<G:...>` odtwarza komputer handlowca: zip oznaczony jako
pobrany z internetu i rozpakowany jak w Eksploratorze, start bez zmiennych Pythona, start z dysków sieciowych
(M: przez adres IP = strefa Internet, G: = Intranet), spis bibliotek wczytanych spoza folderu programu.
Potem `program/testy/e2e_gui.py --exe <rozpakowana kopia>` (cały proces do gotowej prezentacji).
Czystej maszyny wirtualnej nie mamy (brak Windows Sandbox i Hyper-V) - to jest najbliższe przybliżenie.

## Program „Stwórz prezentację”

Zrobione w 1.1.1 (30.09.2026):
- lista slajdów: 60 typów w 7 grupach (Nagłówki, Opis, Cechy, Szczegóły, Dane, Multimedia, Cytaty) - 10 wypełnianych
  danymi z folderu i 50 z szablonu z podpowiedziami w [nawiasach];
- suwaki pokazują skutek od razu: liczba slajdów przy przycisku, „Dodano / Usunięto” pod suwakiem długości,
  opis zmian pod suwakiem tekstu; „Ilość tekstu” realnie zmienia treść (np. 241 / 296 / 343 słowa);
- okładkę można wyłączyć;
- paczki bez smaku w nazwie pliku są dopasowywane po napisie na opakowaniu (rozpoznawanie tekstu wbudowane w Windows);
- przyciski Claude / ChatGPT / Gemini sprawdzone w prawdziwym oknie (aplikacje Claude i ChatGPT, Gemini w przeglądarce).

Zostało:
1. **Kolejność slajdów z szablonu.** Program wstawia je w stałe miejsca (okładki i agenda na początku, reszta przed
   zakończeniem). Przestawianie w oknie nie istnieje - kolejność zmienia się w PowerPoincie.
2. **Mac.** Okno działa tylko w Windows. Na Macu jest tylko instrukcja dla AI (README), nietestowana.
3. **Wydania 1.0.7-1.0.9:** nie uruchamiają się z dysku M: (adres IP), a po rozpakowaniu zipa w Eksploratorze
   mają zniekształcone polskie nazwy plików; 1.0.7-1.0.8 mają też zepsutą samoaktualizację. Poprawione w 1.1.0.
   Kto ma starsze wydanie, pobiera najnowsze ręcznie.
4. **Start z dysku M:** 10-30 s (dysk sieciowy). Rozważyć kopię programu na dysk lokalny przy pierwszym starcie.

## Wygląd w innych aplikacjach (design system)

Wartości i motywy: `design-system/`. Ten wygląd (układ, animacje, kolory, odstępy) ma stać się domyślny.

5. **Inyfinn Photo Resizer** (repo `inyfinn/Inyfinn-photo-resizer`): motyw Dobra Kaloria jako domyślny, jasny i ciemny
   zostają do wyboru. Instrukcja: `design-system/themes/photo-resizer/README.md`. Wpis o zmianie designu w dokumentacji
   i logach aplikacji, commit, push, instalator.
6. **DAM Dobra Kaloria** (repo `inyfinn/DAM---Dobra-Kaloria---inyfinn`): to samo, nakładka
   `design-system/themes/dam/`. Uwaga: DAM ma zapis, że tło nie ma być kremowe, więc krem jako domyślne tło to decyzja
   właściciela. Wydanie według łańcucha wydań DAM.
7. **Jedna zieleń interfejsu.** Program ma `#0F763E`, DAM `#007936` i `#008244`, logo `#006400`. Ustalić jedną.

## Zasady pracy

- Wartości (kolory, odstępy, czcionki) zmienia się tylko w `design-system/tokens/tokens.json`, potem
  `python design-system/scripts/build_tokens.py`.
- Nazywanie plików w folderze produktu: `dla-uzytkownika/CZYTAJ - jak zrobić prezentację.txt`.
- Budowa i wydanie: `program/build.ps1 -Bump`, `program/repo.ps1 -Zip`, potem wydanie na GitHubie.
