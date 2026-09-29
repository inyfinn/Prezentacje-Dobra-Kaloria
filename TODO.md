# Do zrobienia

Stan na 29.09.2026, program w wersji 1.0.9. Kolejność = priorytet.

## Program „Stwórz prezentację”

1. **Suwaki „Długość” i „Ilość tekstu” nie pokazują skutku.** Użytkownik nie wie, na co wpływają.
   Pokazać na żywo liczbę slajdów i zmianę listy sekcji albo sprawdzić, czy suwaki w ogóle zmieniają wynik.
2. **Okładka jest zablokowana** (nie da się jej wyłączyć). Ma być do wyboru jak reszta.
3. **Lista slajdów do wyboru** ma obejmować około 40 typów z szablonu, pogrupowanych:
   dane, multimedia, opis, cechy, szczegóły, cytaty, nagłówki. Wzór grupowania: slajd 14 szablonu.
   Dziś lista ma tylko 10 pozycji (`SECTIONS` w `program/src/app/engine.py`).
4. **Miniatury paczek w „Znalazłem w folderze”.** Pliki bez nazwy smaku przypisują się po kolejności,
   więc smak może dostać cudzą paczkę (kliknięcie miniatury podmienia ją).
5. **Przyciski Claude / ChatGPT / Gemini** sprawdzone tylko częściowo: kopiowanie i wyszukanie aplikacji działa,
   samo otwarcie aplikacji w prawdziwym oknie nie było klikane.
6. **Mac.** Okno działa tylko w Windows. Na Macu jest tylko instrukcja dla AI (README), nietestowana.
7. **Wydania 1.0.7 i 1.0.8** mają zepsutą samoaktualizację. Kto je ma, pobiera 1.0.9 ręcznie.

## Wygląd w innych aplikacjach (design system)

Wartości i motywy: `design-system/`. Ten wygląd (układ, animacje, kolory, odstępy) ma stać się domyślny.

8. **Inyfinn Photo Resizer** (repo `inyfinn/Inyfinn-photo-resizer`): motyw Dobra Kaloria jako domyślny, jasny i ciemny
   zostają do wyboru. Instrukcja: `design-system/themes/photo-resizer/README.md`. Wpis o zmianie designu w dokumentacji
   i logach aplikacji, commit, push, instalator.
9. **DAM Dobra Kaloria** (repo `inyfinn/DAM---Dobra-Kaloria---inyfinn`): to samo, nakładka
   `design-system/themes/dam/`. Uwaga: DAM ma zapis, że tło nie ma być kremowe, więc krem jako domyślne tło to decyzja
   właściciela. Wydanie według łańcucha wydań DAM.
10. **Jedna zieleń interfejsu.** Program ma `#0F763E`, DAM `#007936` i `#008244`, logo `#006400`. Ustalić jedną.

## Zasady pracy

- Wartości (kolory, odstępy, czcionki) zmienia się tylko w `design-system/tokens/tokens.json`, potem
  `python design-system/scripts/build_tokens.py`.
- Nazywanie plików w folderze produktu: `dla-uzytkownika/CZYTAJ - jak zrobić prezentację.txt`.
- Budowa i wydanie: `program/build.ps1 -Bump`, `program/repo.ps1 -Zip`, potem wydanie na GitHubie.
