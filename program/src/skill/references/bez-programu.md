# Prezentacja bez programu (Droga B): Mac, czat, komputer bez dysków firmy

Stan: 21.10.2026. Pełna instrukcja dla ludzi i agentów spoza firmy: `PROMPT BEZ PROGRAMU.md` w folderze programu
i w paczce `DK - paczka prezentacji dla AI.zip` (źródło obu: `WORK\instrukcje\tresc.md`, generator `generuj.py`).
Ten plik to skrót dla agenta, który ma skill, ale nie ma programu ani skryptów Windows.

## Zasada

Prezentację składasz z gotowych slajdów pełnego szablonu `DK - szablon prezentacji - pełen.pptx` (65 slajdów; 1-2 to
instrukcje). Nie rysujesz od zera. Narzędzie: `scripts/dk_szablon.py` (python-pptx + Pillow):

| Funkcja | Co robi |
|---|---|
| `zloz(prs, [4, 17, 62, 62, 65])` | zostawia wybrane slajdy szablonu w podanej kolejności (z kopiami), usuwa resztę, ramki-instrukcje spoza kadru i notatki szablonu, przenumerowuje strony |
| `wpisz(pole, "akapit 1", "akapit 2")` | wpisuje tekst z zachowaniem formatu szablonu |
| `pola(slide.shapes, "[Claim")` | pola o danym początku tekstu w kolejności czytania (twarde spacje szablonu nie przeszkadzają) |
| `ksztalty(slide.shapes)` | wszystkie kształty, także w grupach (packshot z owocami to grupa) |
| `obraz(slide, pic, plik)` | podmienia obraz w ramce, w całości, z obcięciem przezroczystych marginesów PNG |
| `twarde(tekst)` | twarda spacja po w, z, i, a, o, u (zawieszki) |
| `sprawdz(prs, fonty)` | **czy tekst się mieści** — pomiar czcionkami Mindset i Lato przy piśmie 100%; zwraca usterki |
| `podglad(plik, kopia)` | kopia bez autodopasowania do renderu w LibreOffice |
| `nawiasy(prs)` | pozostałe `[podpowiedzi]` |
| `duplikuj(prs, slajd)` | kopia slajdu z tłem, obrazami i linkami |

Katalog slajdów: `katalog-szablonu.md`. Styl i treść: `dopracowanie.md`, `styl-dk.md` — te same zasady co z programem.

## Czy tekst się mieści (lekcja 21.10.2026, `lekcje.md` A55)

Agent w czacie złożył prezentację, obejrzał ją w LibreOffice i uznał za dobrą. W PowerPoincie tytuł okładki wchodził
na podtytuł, „2 800” łamało się na „2 8 / 00”, hasła wchodziły na dopiski, pas wylewał się. Przyczyny:

1. Brak Mindset przy renderze — czcionka zastępcza jest węższa.
2. Pola szablonu mają „zmniejsz tekst przy przepełnieniu” (`normAutofit` bez `fontScale`). LibreOffice zmniejsza pismo
   przy renderze, PowerPoint pokazuje 100%, dopóki ktoś nie kliknie w pole.

Reguły:
- `sprawdz(prs, fonty)` = pusta lista przed zapisem. Czcionki: `assets/fonts/` (Mindset.otf, MindsetSlim.otf,
  Lato-Regular.ttf, Lato-Bold.ttf). Na czystym szablonie daje 0 zgłoszeń; na prezentacji z 21.10 znalazła dokładnie
  usterki widoczne w PowerPoincie.
- Gdy zgłasza: skróć tekst → krótszy zapis liczby / rok poza kaflem → mniej kart w rzędzie (szersze pola) → inny
  slajd z katalogu → DO DECYZJI. Nigdy mniejsze pismo ani większe pole.
- **Render: wzorcem jest PowerPoint.** Windows z PowerPointem (Claude Code, Codex, Gemini CLI, Cursor) — tylko
  PowerPoint (COM, `scripts/render.ps1`). Mac — eksport PDF z PowerPointa. Czat w chmurze i **Cowork** (kod w maszynie
  z Linuksem, bez PowerPointa i bez dysków sieciowych) — LibreOffice z zainstalowanymi czcionkami, na kopii z
  `podglad()`, i w raporcie: „podgląd nie z PowerPointa — przejrzyj w PowerPoincie”.
- Zrzut bez grubych wersalików Mindset w nagłówkach = render nieważny.

## Wybór modelu (decyzja usera 21.10.2026)

Prezentacje robi najmocniejszy model z wysokim poziomem myślenia: w Claude **Fable**, w innych narzędziach **Astra**
albo **SOL**. Model wybiera człowiek przed startem — agent tylko o tym przypomina, gdy widzi słabszy.
