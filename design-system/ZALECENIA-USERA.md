# Zalecenia usera — jeden język wizualny Dobra Kaloria (30.09.2026)

Źródło prawdy dla agentów pracujących nad: programem „Stwórz prezentację”, Inyfinn Photo Resizer, DAM.
Właściciel wdrożenia w design systemie: agent „Identyfikacja” (wersja tokenów 1.4.0). Po wdrożeniu treść
przechodzi do `IDENTYFIKACJA-WIZUALNA.md` i `DESIGN_SYSTEM.md`, a ten plik zostaje jako zapis decyzji.

## Słowa usera (dosłownie)

> „niech DAM bierze też przykład z rozwiązań stricte w photoresizerze? bo ja już to widziałem i mi się podobają
> te rozwiązania. Co prawda, w każdej aplikacji trzeba zmierzyć tzw. liczbę zakorzenień okna. Tzn. że np. jeśli
> tło jest fundamentem, a na tle rysuje się kontener jeden, a później kolejny, typu rubryka do wypełnienia, to
> niby zakorzenienia są 2. A przecież DAM ma takich zakorzenień więcej. Dlatego trzeba umieć to lepiej rozegrać,
> żeby to pięknie wyglądało. Postaraj się, żeby TAGI też miały raczej ODCIEŃ zastosowanego stylu i tylko
> delikatnie zmieniały barwę Hue, zamiast stałych barw, bo czasem to nie będzie kompletnie pasować.
> Na pewno w Inyfinn Photo Resizer wewnętrzne rubryki były MINIMALNIE za jasne. Jakby były o troszkę ciemniejsze,
> to byłoby już idealnie. I tak samo można budować kwestie wizualne w PREZENTACJE oraz DAM. Fajnie jakby
> ostatecznie powstał taki jeden główny język komunikacji wizualnej. IDENTYFIKACJA WIZUALNA. Że na przyszłość,
> jak cię o coś poproszę, to zrobisz w tym stylu i odtworzysz to bez problemu.”

Wcześniej (wiążące): nagłówki Mindset, tekst Lato. Dwa style „Dobra Kaloria 1 · zieleń” i „Dobra Kaloria 2 ·
krem”, każdy jasny i ciemny. Wzorzec wyglądu: program „Stwórz prezentację” („tam jest pięknie”) oraz rozwiązania
z Photo Resizer 2.6.2. Tło główne w trybie jasnym ma być jaśniejsze niż w obecnym szkicu DAM. Za dużo białych
płyt w DAM = błąd. Sama zmiana czcionki i kolorów to za mało: komponenty (przyciski, karty, okna w oknach,
pola, filtry) mają mieć ten sam język.

## Co z tego wynika (reguły do wdrożenia)

1. **Drabina zagnieżdżeń (poziomy powierzchni).** Każdy styl × tryb ma poziomy L0…L4:
   L0 tło okna → L1 kontener/sekcja/karta → L2 rubryka/pole/karta w karcie → L3 element w polu (chip, wiersz
   listy, okno w oknie) → L4 nakładka (menu, podpowiedź, modal nad modalem). Każdy krok w górę różni się od
   poprzedniego o stały, mały skok jasności (w jasnym: głębiej = minimalnie ciemniej albo jaśniej wg jednego
   kierunku, nigdy losowo; w ciemnym: głębiej = jaśniej). Różnica sąsiadów wyraźna, ale delikatna; ramka tylko
   tam, gdzie sam skok jasności nie wystarcza. Brak czystej bieli na żadnym poziomie w stylach DK.
2. **Zmierz liczbę zagnieżdżeń w każdej aplikacji** (program ~2–3, Resizer ~2–3, DAM 4–5) i przypisz każdy
   kontener do poziomu. Aplikacja z głębszym drzewem nie może „przepalić” drabiny — poziomy dobrane tak, żeby
   L4 dalej był czytelny i nie zlewał się z L0.
3. **Rubryki (L2) w Photo Resizer minimalnie ciemniejsze** niż w 2.6.2 — ta sama korekta obowiązuje jako
   wzorzec dla programu i DAM.
4. **Tagi = odcień stylu z lekkim przesunięciem Hue.** Kolory tagów liczone z koloru bazowego stylu (HSL/OKLCH):
   ta sama jasność i nasycenie co styl, Hue przesunięte o małe kroki (np. ±8…±18°) dla kolejnych kategorii.
   Zero stałych barw (fiolet, pomarańcz, niebieski) w stylach DK. Tekst tagu ≥ 4.5:1 w obu trybach.
   Kategorie rozróżnialne także bez koloru (etykieta kategorii / kolejność).
5. **Komponenty jednego języka:** przycisk główny żółty (jeden na widok), drugorzędny zielony obrys, link,
   przyciski-ikony, chipy/segmenty, pola, suwaki, przełączniki, karty, okna w oknach, menu, podpowiedzi,
   powiadomienia — przepis w `components.md`, identyczny dla trzech aplikacji (HTML/CSS i Qt).
6. **Odtwarzalność:** dokument `IDENTYFIKACJA-WIZUALNA.md` mówi, jak zrobić nowy ekran/aplikację w tym stylu
   krok po kroku (tokeny, drabina, komponenty, tagi, typografia, ikony, plansza startowa, ikona aplikacji),
   z przykładami z trzech aplikacji i zrzutami.

## 05.10.2026 (DS 1.5.0)

Dosłownie: „Jak dla mnie to szablony kolorystyczne i UI dla photo resizer są bardzo słabe. Bardzo nieczytelne. Większe
teksty powinny być, a schemat kolorystyczny jest po prostu niepotrzebnie cały całkowicie kremowy, a brakuje bieli.
Zerżnij kurwa wprost z PREZENTACJE. Widzę, że wszystko jest zbyt ciasno, nieczytelnie, bloki mają jakiś chujowy obrys.
Nie zastosowałeś schematu. I tak samo na Dobra Kaloria DAM.”
„Popraw całą Dobrą Kalorię Zieleń, bo cały ten motyw jest nijako zły. Po prostu jest taki… mało ciekawy, nieprzyjazny.
Brakuje mu, żeby te ciemniejsze kolorki były inne, jakieś takie… kremowe być może właśnie.”
„Brązy w schemacie brązowym powinny być ciemniejsze. Wprowadź zmiany na Inyfinn Resizer oraz DAM natychmiastowo, w całym spektrum.”

Reguły z tego wynikające:
7. **Wzorzec = program „Stwórz prezentację”, 1:1.** Jasne style: biała strona, kremowe karty, cienka jasna ramka karty, bez
   ciemnego obrysu. Zieleń tylko w akcentach, nigdy jako tło powierzchni.
8. **Czytelność:** tekst co najmniej 15 px w Qt (16 px web), etykiety 14-15 px, kontrolki 40-48 px, więcej odstępu.
9. **Zieleń ciemna ciepła:** kremowy tekst, miodowe/żółte wyróżnienia, głębsze poziomy w stronę oliwki.
10. **Krem ciemny ciemniejszy** na wszystkich poziomach (tło, karty, pola, ramki, tagi).
