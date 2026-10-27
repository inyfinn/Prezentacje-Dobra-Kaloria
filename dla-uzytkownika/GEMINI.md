# Prezentacje Dobra Kaloria — instrukcja dla Gemini (Gemini CLI, Antigravity, czat Gemini)

<!-- Plik generowany: WORK\instrukcje\generuj.py z tresc.md. Nie edytuj CLAUDE/AGENTS/GEMINI/GROK.md ani PROMPT BEZ PROGRAMU.md ręcznie. -->

> **Dla człowieka, przed startem:** wybierz najmocniejszy model i wysoki poziom myślenia. W Claude: **Fable**.
> W innych narzędziach: **Astra** albo **SOL**. Ustaw wysoki poziom rozumowania (high / wysokie myślenie),
> jeśli narzędzie na to pozwala. Słabszy model albo niski poziom myślenia robi gorsze prezentacje.

**Pracuj z wysokim poziomem myślenia:** przed każdym slajdem zastanów się nad treścią i układem, po każdym
renderze dokładnie oceń wynik. Nie skracaj pracy kosztem jakości.

Jesteś Gemini — pracujesz w Gemini CLI, w Antigravity albo w czacie. Zadanie: zrobić prezentację marki **Dobra Kaloria** tak piękną jak nasze — z folderu produktu, z notatek
albo dokumentu, albo przełożyć gotową prezentację `.pptx` na nasz styl. **Nie zadawaj pytań w trakcie** — czego nie
wiesz, wpisz na końcu do listy „DO DECYZJI”. Wyjątek: nie dostałeś żadnego materiału — najpierw zrób sekcję 0
(skille, czcionki), potem poproś o materiał jednym zdaniem
(„Podaj folder produktu, dokument albo plik .pptx.”) i czekaj.

**Dobra Kaloria** = polska marka przekąsek (kulki, batony…), producent Kubara. Prezentacje to decki handlowe
(dla sieci, hurtowni) i strategiczne (dla zarządu). Wzorem wyglądu jest sklep dobrakaloria.pl: dużo bieli, kremowe
karty, zieleń marki, hasła grubą czcionką Mindset, krótkie dopiski Lato, duże liczby, packshoty bez tła.

**Najważniejsze w jednym zdaniu:** prezentację składasz z gotowych slajdów naszego szablonu (nie rysujesz od zera),
w każdy slajd wpisujesz krótkie hasła, liczby i wnioski, obrazy wstawiasz w całości, a przed oddaniem oglądasz
każdy slajd jako obraz.

Masz dwie drogi do tego samego wyniku:

- **Droga A — program** (Windows z PowerPointem, dostęp do folderu programu): `stworz-cli.exe` w 30–60 s robi szkic,
  Ty go dopracowujesz (sekcja 3).
- **Droga B — sam z szablonu** (Mac, Linux, czat w przeglądarce, brak programu): składasz prezentację w Pythonie
  ze slajdów szablonu (sekcja 4).

Wybór: istnieje `<folder programu>\WORK\pliki programu\stworz-cli.exe` i jesteś na Windows → Droga A. Inaczej → Droga B.
Styl, treść, dobór slajdów i kontrola (sekcje 5–10) są wspólne dla obu dróg.

---

## 0. Skille — zainstaluj, jeśli jeszcze ich nie masz (zawsze pierwszy krok)

Pracujesz z dwoma skillami. Leżą w paczce `DK - paczka prezentacji dla AI.zip` w folderze `skille\` (w folderze
programu: `WORK\skill-prezentacje\`):

| Skill | Co z niego bierzesz |
|---|---|
| **`prezentacje`** | główna metoda: `SKILL.md`, `references\lekcje.md` (decyzje właściciela i błędy, które już raz się zdarzyły — przeczytaj najpierw), `references\dopracowanie.md` (metoda dopracowania; wygrywa przy sprzeczności), `references\katalog-szablonu.md`, `references\bez-programu.md` (Droga B), `scripts\` (m.in. `dk_szablon.py`), `assets\fonts\` |
| **`ui-ux-pro-max`** | METODA oceny slajdu: hierarchia, czytelność, kontrast (tekst min. 4,5:1), typografia, światło, wykresy. Nie bierzesz z niego kolorów, czcionek ani wyglądu — styl Dobra Kaloria (sekcja 5) zawsze wygrywa. Wyszukiwarka: `python <skille>\ui-ux-pro-max\scripts\search.py "<zapytanie>" --domain <dziedzina>` |

1. **Sprawdź**, czy są zainstalowane: `<katalog skilli>\prezentacje\SKILL.md` i `<katalog skilli>\ui-ux-pro-max\SKILL.md`.
   Katalog skilli: Claude `~/.claude/skills`, Codex / ChatGPT `~/.codex/skills`, Gemini `~/.gemini/skills`,
   Cursor `~/.cursor/skills` (Windows: `%USERPROFILE%\.claude\skills` itd.).
2. **Nie ma albo to inna wersja** — zainstaluj skryptem z paczki (pomija aktualne, starą wersję przenosi do
   `_poprzednie\`, niczego nie kasuje):
   - Windows: `& "<paczka>\zainstaluj-skill.cmd"` (Claude) albo z `-Cel "<katalog skilli>"` (inny agent);
   - Mac / Linux: `bash "<paczka>/zainstaluj-skille.sh" [katalog skilli]` (domyślnie `~/.claude/skills`).
3. **Nie możesz instalować** (czat w przeglądarce, piaskownica): nic nie instaluj — czytaj `SKILL.md` i pliki obu
   skilli prosto z rozpakowanej paczki.
4. **Wczytaj oba skille** (skill zainstalowany w trakcie rozmowy może nie być jeszcze widoczny — wtedy czytaj pliki
   z katalogu) i używaj ich przez całą pracę: `prezentacje` do budowy i treści, `ui-ux-pro-max` przy każdej ocenie
   slajdów (sekcja 9). Ta instrukcja i skill `prezentacje` mówią to samo; przy sprzeczności wygrywa
   `references\dopracowanie.md`, potem ta instrukcja.

---

## 1. Co masz zrobić — tryby

| Użytkownik dał | Tryb | Najważniejsza zasada |
|---|---|---|
| folder produktu (karty wprowadzenia, copy, packshoty), notatki, dane | **nowa prezentacja** | tytuł slajdu = wniosek, nie temat; jedna myśl na slajd; liczby tylko z materiału, ze źródłem |
| dokument (.docx, .pdf, .txt, .md) | **prezentacja z dokumentu** | te same słowa, ułożone w hasła, liczby i wnioski; niczego nie dopisujesz i nie gubisz |
| folder prezentacji (`Źródła\`, `scenariusz.md`, `POLECENIE.md`) albo kilka plików: dokumenty, zdjęcia, zrzuty ekranu | **scenariusz** | piszesz `scenariusz.md` według wzoru (`# SCENARIUSZ DK`, jeden `##` = jeden slajd), program buduje z niego 1:1; szczegóły w `POLECENIE.md` w tym folderze |
| gotowa prezentacja .pptx w innym stylu | **przełożenie 1:1** (cel `wiernie`) | slajd N = slajd N oryginału, te same słowa, kolejność i obrazy; zmienia się wygląd i rola słów (sekcja 6.3) |
| j.w. + „dokończ”, „rozwiń” | cel `rozwin` | slajdy oryginału jak w `wiernie` + nowe slajdy z szablonu, oznaczone w notatkach „NOWY” |
| j.w. + „skróć”, „wersja na 15 minut” | cel `skroc` | slajdy tylko **ukrywasz**, nigdy nie kasujesz; krótsza wersja = NOWY slajd, oryginał ukryty za nim |
| prezentacja już w stylu DK | **dopracowanie** | nie przekładasz drugi raz; poprawiasz na kopii `<nazwa> - dopracowana.pptx` |

Cel wybierasz po słowach użytkownika; nic nie powiedział o celu — `wiernie`.

## 2. Skąd co brać

**Folder programu** `— SZABLON AI - skrypt` (ten plik leży w jego podfolderze `WORK`; dalej `<folder programu>`). Kopie — użyj
pierwszej, która istnieje:

1. `G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\— SZABLON AI - skrypt`
2. `M:\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt`
3. `D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt`

Nie masz dostępu do żadnej (Mac, czat, komputer bez dysków firmy)? Pracujesz z **paczki**
`DK - paczka prezentacji dla AI.zip`: ten plik, szablon `DK - szablon prezentacji - pełen.pptx`, folder `fonty`
(Mindset, Lato) i `dk_szablon.py` (kod z sekcji 4, gotowy do importu). To wystarczy do Drogi B — wszystko inne,
czego potrzebujesz, jest w tym pliku.

| Co | Gdzie | Do czego |
|---|---|---|
| **pełny szablon, 65 slajdów** | `<folder programu>\WORK\pliki programu\DK - szablon prezentacji - pełen.pptx` | źródło wszystkich układów; slajdy 1–2 to instrukcje (nie bierz) |
| katalog slajdów | sekcja 7 tego pliku (pełna wersja: `WORK\skill-prezentacje\references\katalog-szablonu.md`) | który slajd do jakiej treści |
| skill `/prezentacje` | `<folder programu>\WORK\skill-prezentacje\` | Droga A: metoda dopracowania (`references\dopracowanie.md`), lekcje (`references\lekcje.md`), skrypty |
| design system marki | `<folder programu>\WORK\skill-ds-dobra-kaloria\DESIGN-SYSTEM-DOBRA-KALORIA.md` (§2, §5.4) | gdy potrzebujesz więcej niż sekcja 5 |
| **czcionki (obowiązkowe)** | `<folder programu>\WORK\skill-prezentacje\assets\fonts\` (`Mindset.otf`, `MindsetSlim.otf`, `Lato-Regular.ttf`, `Lato-Bold.ttf`); poza firmą — folder `fonty` od użytkownika | bez nich nie sprawdzisz, czy tekst się mieści (sekcja 4a). Mindset osadzona w szablonie działa tylko w PowerPoincie, nie w Pythonie ani LibreOffice |

**Folder produktu** — materiały jednego produktu, np. `…\24.09.2026 - KULKI z kreatyną`:

| Plik / podfolder | Co z niego bierzesz |
|---|---|
| `Karta wprowadzenia_*.xlsx` (jedna na smak) | nazwa, smaki, EAN, gramatura, % owoców, oświadczenia żywieniowe, wartości odżywcze |
| Word / txt `Copy…`, `Tekst…` | teksty o produkcie |
| Word / txt / Excel `Badanie…`, `Dane…`, `Analiza…`, `OMNIBUS…` | liczby z badań i nazwa badania do stopki źródła |
| `Wizualizacje\` | packshoty (PNG bez tła); smak rozpoznaj po obrazie, nie po nazwie pliku |
| `Elementy\` | owoce, kulki, listki wokół paczki |

## 3. Droga A — z programem (Windows)

### KROK 0 — skill `/prezentacje`

Sprawdź, czy masz skill: `%USERPROFILE%\.gemini\skills\prezentacje\SKILL.md` (Gemini CLI; PowerShell: `Test-Path "$env:USERPROFILE\.gemini\skills\prezentacje\SKILL.md"`).

- **Nie ma albo brakuje w nim `references\dopracowanie.md`:** uruchom `& "<folder programu>\WORK\zainstaluj-skill.cmd" -Cel "$env:USERPROFILE\.gemini\skills\prezentacje"` (albo skopiuj folder `<folder programu>\WORK\skill-prezentacje\` w to miejsce). Skrypt niczego nie kasuje — istniejącą wersję przenosi do `…\skills\_poprzednie\`. Sprawdź jeszcze raz.
- **Potem** wczytaj skill `/prezentacje` (`SKILL.md` sekcje 0 i 1b, `references\dopracowanie.md`, `references\lekcje.md`). Skill zainstalowany w trakcie rozmowy może nie być widoczny — czytaj wtedy te pliki prosto z katalogu (bez restartu).
- **Brak mechanizmu skilli albo dostępu do profilu** (czat, piaskownica): nic nie instaluj — czytaj `<folder programu>\WORK\skill-prezentacje\SKILL.md` i `references\` prosto z folderu programu.

### Zrób szkic jednym poleceniem

PowerShell (cmd: to samo bez `&`):

```powershell
& "<folder programu>\WORK\pliki programu\stworz-cli.exe" "<folder produktu>"
& "<folder programu>\WORK\pliki programu\stworz-cli.exe" "<plik.pptx>" --cel wiernie
& "<folder programu>\WORK\pliki programu\stworz-cli.exe" "<plik.docx>" [--slajdy N] [--rozdzialy N]
& "<folder programu>\WORK\pliki programu\stworz-cli.exe" --scenariusz "<folder prezentacji>\scenariusz.md"
```

**Scenariusz (od 1.3).** Najlepszy wynik z dokumentów, zdjęć i zrzutów ekranu: najpierw piszesz `scenariusz.md` według
wzoru `WORK\skill-prezentacje\assets\scenariusz-wzor.md` (`# SCENARIUSZ DK`, `tytuł:`, potem każdy `## Hasło` = dokładnie
jeden slajd: jedna linia dopisku, do 4 punktów, `**42%** opis` = liczba-bohater, tabela, `![podpis](Źródła/plik.jpg)`,
`> cytat — autor`, `## Rozdział: Nazwa` = przekładka). Treść tylko ze `Źródła\`, nic nie wymyślasz. Program sprawdza
scenariusz (linie `BŁĄD` blokują budowę, `uwaga` – nie), buduje 1:1 do folderu prezentacji (`<tytuł>.pptx`, kolejne
budowy: `v2`, `v3`…) i robi `plansze\`. Poprawki robisz w scenariuszu (nowa wersja `scenariusz-2.md`), nie w pliku pptx.

Program pracuje 30–60 s, drukuje postęp i raport. Nie używaj `Prezentacje.exe` — to okno dla ludzi.
Folder bez kart wprowadzenia program odrzuca — powiedz użytkownikowi, czego brakuje (albo przejdź na Drogę B).

| Opcja | Wartości | Domyślnie |
|---|---|---|
| `--styl` | `nowy` (sklep dobrakaloria.pl) / `stary` (klasyczny; nie dla konwersji) | `nowy` |
| `--dlugosc` | `krotka` (~6 slajdów) / `standard` (~9) / `pelna` (~13) | `standard` |
| `--tekst` | `mniej` / `standard` / `wiecej` | `standard` |
| `--sekcje` | folder: `okladka,smaki,wyroznia,sklad,wartosci,karty_smakow,copy,badanie,film,koniec`; .pptx: `r01,r02…` (reszta ukryta) | wg `--dlugosc` / wszystkie |
| `--film` | link YouTube (slajd z filmem) | brak |
| `--claimy` | `"Claim 1; Claim 2 – opis"` zamiast oświadczeń z kart | z kart |
| `--packshoty` | `"Arbuz=plik.png;Cola=plik2.png"` | po nazwie pliku, potem po kolejności |
| `--cel` | `wiernie` / `rozwin` (+ `--dodaj t10,t58`) / `skroc` (+ `--slajdy N`) | `wiernie` |
| `--wyjscie`, `--robocze` | katalog wyniku / katalog roboczy | obok źródła / `_robocze\<nazwa>` |
| `--bez-wizualizacji` | bez packshotów z biblioteki na slajdach portfolio | — |
| `--bez-oka` | bez automatycznej poprawy układu po obejrzeniu zrzutów | — |
| `--bez-qa`, `--json`, `--tylko-analiza` | bez PowerPointa / raport JSON / tylko pokaż, co program znalazł | — |
| `--mimo-to` | wymuś konwersję pliku już w stylu DK (prawie nigdy) | — |

**Wynik:** `<nazwa> - nowy styl.pptx` (rozwin: `… - rozwinięta.pptx`, skroc: `… - skrót.pptx`) obok źródła;
w `_robocze\…\`: `raport.json`, `spec_program.json` (układ slajdów; polecenia nazywają go też `spec_konwersja.json`),
`qa\…\s01.png…` (zrzuty), `podglad_grafik.png` (paczki do smaków), `wielkosc-liter.txt`, `img\`; obok wyniku
`plansze\` (obrazy slajdów po 6). Plik był otwarty albo zmieniony ręcznie → program zapisze `… (nowa wersja).pptx`
— nie obchodź tego. Plik źródłowy nie jest zmieniany.

**Co program gwarantuje przy konwersji .pptx.** Czyta wszystko: teksty (też w grupach i SmartArt), tabele, wykresy
(zostają edytowalne), obrazy w całości (też wypełnienia kształtów z Canvy; nachodzące składa w kolaż), hiperłącza,
notatki, sekcje. Tekst spoza kadru przenosi do notatek. Kolumny zostają kolumnami, wyróżnione kolorem słowa zostają
wyróżnione. Slajd dzieli tylko, gdy tekst nie mieści się pismem 13 pt. Literówek nie poprawia, tylko ostrzega
(„Możliwe błędy w tekście oryginału”). Wersaliki z oryginału zamienia na zwykłą wielkość liter (lista w
`wielkosc-liter.txt`). Pomija logo i belki powtarzane na większości slajdów, drobne ozdobniki, animacje i tła. Na
slajdach portfolio dokłada packshoty z biblioteki `01 - PRODUKTY\- DK` i wypisuje, które — pokaż tę listę
użytkownikowi (słownik nazw linii `WORK\skill-prezentacje\assets\linie-aliasy.json` to założenie).

**Dwie kontrole programu — obie muszą być czyste:** `Treść: 100% akapitów (N/N) przeniesionych` oraz
`Układ: osobne napisy X z X, kolejność góra-dół bez zmian, liczby X z X, slajdów tyle samo (N)`.

### 3b. Dopracowanie wyniku programu

Program robi **szkic**: ten sam slajd w stylu marki, 100% treści, hasła i liczby wstępnie wyciągnięte, układ z klocków
szablonu. Gotową prezentację robisz z niego Ty — według sekcji 5 (styl), 6 (treść), 7 (dobór slajdu) i 9 (kontrola).
W razie sprzeczności wygrywa `WORK\skill-prezentacje\references\dopracowanie.md` (pełna metoda; przeczytaj ją pierwszą
i w całości). Zapisy „zdania w Lato”, „bez wyjmowania liczb do kafli”, „akapit = karta-artykuł” są nieaktualne od 13.10.2026.

- **Folder produktu:** obejrzyj `_robocze\podglad_grafik.png` — czy paczka pasuje do smaku (kolor, napis); nie →
  ponów z `--packshoty`. Uzupełnij `[nawiasy]` danymi z folderu (python-pptx albo PowerPoint COM; funkcje z sekcji 4
  działają też tu). Nie zmieniaj układu, kolorów ani czcionek.
- **Konwersja .pptx i dokument:** poprawki wpisujesz w specu `_robocze\<nazwa>\spec_program.json` (nie w PowerPoincie)
  i budujesz: `python "<folder programu>\WORK\pliki programu\app\skill\scripts\build_dk.py" <spec>`. Format klocków
  (`lead`, `p`, `hero`, `band`, `kv`, `li`, `bars`, `quote`, `pics`, `icon`): `WORK\skill-prezentacje\references\spec-dk.md`.
  Poprawki błędów tekstu deklarujesz w specu (sekcja 6.4). Pełną kontrolę po poprawkach daje jedno polecenie:
  `python "<folder programu>\WORK\pliki programu\app\skill\scripts\pptx_convert.py" "<plik.pptx>" --ze-specu "<spec>" --robocze "<katalog roboczy>"`.
- Nie edytujesz skryptów skilla ani programu — błąd skryptu zgłaszasz w DO DECYZJI.

## 4. Droga B — sam z szablonu (Python + python-pptx)

Pracujesz w Pythonie z `python-pptx` (`pip install python-pptx pillow`; w claude.ai i ChatGPT jest w piaskownicy).
Zapisz poniższy kod jako `dk_szablon.py` obok szablonu i używaj jego funkcji. Kod jest sprawdzony na tym szablonie:
kopiuje slajdy z tłem, obrazami i linkami, usuwa ramki-instrukcje spoza kadru, czyści notatki szablonu,
przenumerowuje strony, wstawia obrazy w całości (obcina przezroczyste marginesy PNG), mierzy prawdziwymi czcionkami,
czy tekst mieści się w polach (`sprawdz`), i robi uczciwą kopię do podglądu w LibreOffice (`podglad`).

```python
"""Złóż prezentację Dobra Kaloria ze slajdów pełnego szablonu (python-pptx >= 0.6.21).

python dk_szablon.py "DK - szablon prezentacji - pełen.pptx" wynik.pptx 4,17,62,62,65
-> wynik ma slajdy szablonu t04, t17, t62 (dwa razy), t65 w tej kolejności; reszta usunięta.
"""
import copy
import os
import re
import sys

from pptx import Presentation

R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
SKIP = ("notesSlide", "slideLayout")


def duplikuj(prs, src):
    """Kopia slajdu na końcu pliku: tło, kształty, obrazy, linki (rId przemapowane)."""
    new = prs.slides.add_slide(src.slide_layout)
    mapa = {}
    for rid, rel in src.part.rels.items():
        if rel.reltype.endswith(SKIP):
            continue
        if rel.is_external:
            mapa[rid] = new.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            mapa[rid] = new.part.relate_to(rel.target_part, rel.reltype)
    zrodlo = copy.deepcopy(src._element.cSld)
    for el in zrodlo.iter():
        for k, v in list(el.attrib.items()):
            if k.startswith(R) and v in mapa:
                el.set(k, mapa[v])
    # Podmieniamy dzieci spTree, nie sam element: python-pptx trzyma do niego odwołanie.
    tree = new.shapes._spTree
    for ch in list(tree):
        tree.remove(ch)
    for ch in list(zrodlo.spTree):
        tree.append(ch)
    if zrodlo.bg is not None:  # tło slajdu
        tree.addprevious(zrodlo.bg)
    return new


def zloz(prs, numery):
    """Zostaw tylko slajdy o numerach z listy (1 = pierwszy), w tej kolejności, z powtórzeniami."""
    src = list(prs.slides)
    lst = prs.slides._sldIdLst
    stare = list(lst)
    uzyte, kolejnosc = set(), []
    for n in numery:
        s = src[n - 1]
        if n in uzyte:
            duplikuj(prs, s)
            kolejnosc.append(lst[-1])
        else:
            uzyte.add(n)
            kolejnosc.append(stare[n - 1])
    for sid in stare:
        if sid not in kolejnosc:
            prs.part.drop_rel(sid.rId)
    for sid in list(lst):
        lst.remove(sid)
    for sid in kolejnosc:
        lst.append(sid)
    for i, (slide, n) in enumerate(zip(prs.slides, numery), 1):
        slide._element.attrib.pop("show", None)  # ukryte slajdy instrukcji -> zwykłe
        usun_instrukcje(prs, slide)
        if slide.has_notes_slide:  # notatki szablonu to opis slajdu, nie treść dla prelegenta
            slide.notes_slide.notes_text_frame.text = ""
        for sh in slide.shapes:  # numer strony w rogu = numer w szablonie -> nowy numer
            if sh.has_text_frame and sh.text_frame.text.strip() == f"{n:02d}" and sh.top > prs.slide_height * 0.8:
                wpisz(sh, f"{i:02d}")


def usun_instrukcje(prs, slide):
    """Usuń ramki „SLAJD NN - do czego służy” leżące poza kadrem."""
    W = prs.slide_width
    for sh in list(slide.shapes):
        if sh.left is not None and (sh.left >= W or sh.left + sh.width <= 0):
            sh._element.getparent().remove(sh._element)


def wpisz(shape_or_tf, *akapity):
    """Podmień tekst, zachowując format pierwszego fragmentu każdego akapitu."""
    tf = getattr(shape_or_tf, "text_frame", shape_or_tf)
    while len(tf.paragraphs) < len(akapity):  # brakuje akapitów: kopiuj ostatni
        tf.paragraphs[-1]._p.addnext(copy.deepcopy(tf.paragraphs[-1]._p))
    for i, p in enumerate(list(tf.paragraphs)):
        if i >= len(akapity):
            p._p.getparent().remove(p._p)
        elif p.runs:
            p.runs[0].text = akapity[i]
            for r in p.runs[1:]:
                r._r.getparent().remove(r._r)
        else:
            p.text = akapity[i]


def ksztalty(shapes):
    """Wszystkie kształty slajdu, także w grupach. Nazwy mówią, co to jest (np. 'Packshot - ...')."""
    for sh in shapes:
        yield sh
        if sh.shape_type == 6:  # grupa
            yield from ksztalty(sh.shapes)


def obraz(slide, pic, plik):
    """Podmień obrazek w ramce szablonu; nowy mieści się w starej ramce w całości (bez kadrowania).
    Przezroczyste marginesy PNG (packshoty) są obcinane, żeby paczka nie wyszła mała."""
    import io
    from PIL import Image

    im = Image.open(plik)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bbox = im.getchannel("A").getbbox()
        if bbox and bbox != (0, 0) + im.size:
            im = im.crop(bbox)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    buf.seek(0)
    _, rid = slide.part.get_or_add_image_part(buf)
    pic._element.blipFill.blip.rEmbed = rid
    kadr = pic._element.blipFill.find("{http://schemas.openxmlformats.org/drawingml/2006/main}srcRect")
    if kadr is not None:  # zdejmij kadrowanie starego obrazka
        pic._element.blipFill.remove(kadr)
    w, h = im.size
    L, T, W, H = pic.left, pic.top, pic.width, pic.height
    s = min(W / w, H / h)
    pic.width, pic.height = int(w * s), int(h * s)
    pic.left, pic.top = L + (W - pic.width) // 2, T + (H - pic.height) // 2


def pola(shapes, poczatek):
    """Pola tekstowe, których tekst zaczyna się od `poczatek` (np. "[Claim", "00%"), w kolejności czytania
    (wiersz po wierszu, od lewej). Twarde spacje i podziały linii szablonu traktuje jak zwykłe spacje."""
    norm = lambda s: " ".join(s.replace("\u00a0", " ").split())
    out = [sh for sh in ksztalty(shapes) if sh.has_text_frame and norm(sh.text_frame.text).startswith(norm(poczatek))]
    return sorted(out, key=lambda sh: (round(sh.top / 300000), sh.left))


def twarde(tekst):
    """Polska typografia: twarda spacja po jednoliterowych słowach (w, z, i, a, o, u), żeby nie zostały na końcu linii."""
    return re.sub(r"(?<!\S)([wWzZiIaAoOuU]) ", "\\1\u00a0", tekst)


A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PLIKI_CZCIONEK = {"mindset": "Mindset.otf", "mindset slim": "MindsetSlim.otf",
                  "lato": "Lato-Regular.ttf", "lato bold": "Lato-Bold.ttf"}


def _czcionka(fonty, rp, size):
    """Czcionka PIL dla fragmentu tekstu: +mj-lt = Mindset (nagłówki), +mn-lt = Lato (tekst)."""
    from PIL import ImageFont

    lat = rp.find(A + "latin") if rp is not None else None
    tf = (lat.get("typeface") if lat is not None else "+mn-lt") or "+mn-lt"
    nazwa = {"+mj-lt": "mindset", "+mn-lt": "lato"}.get(tf, tf.lower())
    if nazwa == "lato" and rp is not None and rp.get("b") == "1":
        nazwa = "lato bold"
    plik = PLIKI_CZCIONEK.get(nazwa, "Lato-Regular.ttf")
    return ImageFont.truetype(os.path.join(fonty, plik), max(1, round(size * 4))), nazwa  # x4: dokładność


def _rozmiar(rp, p, domyslny):
    for el in (rp, p._p.find(A + "pPr/" + A + "defRPr") if p._p.find(A + "pPr") is not None else None):
        if el is not None and el.get("sz"):
            return int(el.get("sz")) / 100
    return domyslny


def sprawdz(prs, fonty):
    """Czy tekst mieści się w polach — liczone PRAWDZIWYMI czcionkami (Mindset, Lato), przy piśmie 100%.

    PowerPoint nie zmniejsza pisma sam (autodopasowanie bez zapisanej skali = 100%), a LibreOffice zmniejsza —
    dlatego podgląd z LibreOffice potrafi kłamać. Ta funkcja nie zależy od renderu.
    `fonty` = folder z Mindset.otf, MindsetSlim.otf, Lato-Regular.ttf, Lato-Bold.ttf.
    Zwraca listę usterek (slajd, pole, opis); pusta lista = wszystko się mieści.
    """
    usterki = []
    for nr, slide in enumerate(prs.slides, 1):
        for sh in ksztalty(slide.shapes):
            if not sh.has_text_frame or not sh.text_frame.text.strip() or sh.width is None:
                continue
            bp = sh.text_frame._txBody.bodyPr
            ins = lambda k, d=91440: int(bp.get(k, d))
            szer = (sh.width - ins("lIns") - ins("rIns")) / 12700  # pt
            wys = (sh.height - ins("tIns", 45720) - ins("bIns", 45720)) / 12700
            if bp.get("wrap") == "none":
                continue
            potrzeba, nazwa_pola = 0.0, sh.text_frame.text.strip().replace("\n", " / ")[:40]
            for p in sh.text_frame.paragraphs:
                runs = p.runs
                if not runs:
                    potrzeba += 0.6 * 18
                    continue
                rp = runs[0]._r.find(A + "rPr")
                size = _rozmiar(rp, p, 18)
                font, nazwa = _czcionka(fonty, rp, size)
                spc = int(rp.get("spc", 0)) / 100 if rp is not None else 0  # rozstrzelenie liter, pt
                asc, desc = font.getmetrics()
                ln = p._p.find(A + "pPr/" + A + "lnSpc/" + A + "spcPct")
                proc = int(ln.get("val")) / 100000 if ln is not None else 1.0
                linia = (asc + desc) / 4 * proc
                tekst = "".join(r.text for r in runs)
                for kawalek in tekst.split("\v"):
                    slowa, linie, biez = kawalek.split(" "), 1, ""
                    for s in slowa:  # twarda spacja   nie łamie — „2 800” to jedno słowo
                        w = (font.getlength(s) / 4) + spc * len(s)
                        if w > szer + 0.5:
                            usterki.append((nr, nazwa_pola, "słowo „%s” szersze niż pole (%.0f > %.0f pt) — złamie się w środku" % (s, w, szer)))
                        proba = (biez + " " + s).strip()
                        if (font.getlength(proba) / 4) + spc * len(proba) > szer and biez:
                            linie, biez = linie + 1, s
                        else:
                            biez = proba
                    potrzeba += linie * linia
            if potrzeba <= wys * 1.05 + 2:  # 5% zapasu na różnice silników
                continue
            kolizja = _kolizja(prs, slide, sh, (potrzeba - wys) * 12700, bp.get("anchor", "t"))
            if kolizja:
                usterki.append((nr, nazwa_pola, "tekst wymaga %.0f pt wysokości, pole ma %.0f pt — %s"
                                % (potrzeba, wys, kolizja)))
    return usterki


def _kolizja(prs, slide, sh, nadmiar, anchor):
    """Czy tekst rosnący o `nadmiar` (EMU) wejdzie na inny element, wyjdzie poza swoją kartę albo poza slajd."""
    if anchor == "ctr":
        gora, dol = sh.top - nadmiar / 2, sh.top + sh.height + nadmiar / 2
    elif anchor == "b":
        gora, dol = sh.top - nadmiar, sh.top + sh.height
    else:
        gora, dol = sh.top, sh.top + sh.height + nadmiar
    if gora < 0 or dol > prs.slide_height:
        return "wyjdzie poza slajd"
    for o in ksztalty(slide.shapes):
        if o._element is sh._element or o.shape_type == 6 or o.width is None or o.left >= prs.slide_width:
            continue
        if min(o.left + o.width, sh.left + sh.width) - max(o.left, sh.left) <= 12700 * 4:
            continue  # nie leżą nad sobą
        o_dol = o.top + o.height
        if o.left <= sh.left and o.left + o.width >= sh.left + sh.width and o.top <= sh.top and o_dol >= sh.top + sh.height:
            if dol > o_dol or gora < o.top:
                return "wyjdzie poza swoją kartę / pas"
            continue
        if o.top >= sh.top + sh.height - 12700 and o.top < dol:
            return "wejdzie na element poniżej („%s”)" % (o.text_frame.text.strip()[:25] if o.has_text_frame else o.name[:25])
        if o_dol <= sh.top + 12700 and o_dol > gora:
            return "wejdzie na element powyżej"
    return None


def podglad(prs_plik, wyjscie):
    """Kopia do renderu w LibreOffice bez autodopasowania, żeby podgląd pokazał to, co PowerPoint (pismo 100%)."""
    import zipfile

    with zipfile.ZipFile(prs_plik) as zin, zipfile.ZipFile(wyjscie, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            dane = zin.read(it.filename)
            if it.filename.startswith("ppt/slides/slide") and it.filename.endswith(".xml"):
                dane = re.sub(rb"<a:normAutofit[^>]*?(/>|>.*?</a:normAutofit>)", b"<a:noAutofit/>", dane, flags=re.S)
            zout.writestr(it, dane)


def nawiasy(prs):
    """Lista [podpowiedzi] zostawionych w pliku: (slajd, nazwa kształtu, tekst)."""
    out = []
    for i, s in enumerate(prs.slides, 1):
        for sh in ksztalty(s.shapes):
            if sh.has_text_frame and re.search(r"\[[^\]]+\]", sh.text_frame.text):
                out.append((i, sh.name, sh.text_frame.text))
    return out


if __name__ == "__main__":
    prs = Presentation(sys.argv[1])
    zloz(prs, [int(x) for x in sys.argv[3].split(",")])
    prs.save(sys.argv[2])
    for row in nawiasy(prs):
        print(*row, sep=" | ")
```

Przykład:

```python
from pptx import Presentation
from dk_szablon import zloz, wpisz, ksztalty, obraz, pola, twarde, nawiasy, sprawdz, podglad

FONTY = "fonty"   # folder fonty z paczki (Mindset.otf, MindsetSlim.otf, Lato-Regular.ttf, Lato-Bold.ttf)

prs = Presentation("DK - szablon prezentacji - pełen.pptx")
zloz(prs, [4, 17, 62, 31, 65])          # okładka, punkty, trzy fakty, produkt, zakończenie
s = prs.slides[0]
for sh in ksztalty(s.shapes):
    if sh.name == "Tytuł slajdu":
        wpisz(sh, "Kulki", twarde("z kreatyną"))   # dwa akapity = dwie linie, jak w szablonie
    elif sh.name.startswith("Packshot"):
        obraz(s, sh, "Wizualizacje/paczka.png")
fakty = prs.slides[2]
for pole, liczba in zip(pola(fakty.shapes, "00%"), ["82%", "80%", "37%"]):   # od lewej do prawej
    wpisz(pole, liczba)
for usterka in sprawdz(prs, FONTY):     # MUSI być pusta przed zapisem (sekcja 4a)
    print(*usterka, sep=" | ")
prs.save("Prezentacja - nowy styl.pptx")
podglad("Prezentacja - nowy styl.pptx", "podglad.pptx")   # tę kopię renderujesz w LibreOffice
print(nawiasy(prs))                     # co jeszcze stoi w [nawiasach]
```

### 4a. Czy tekst się mieści — mierzysz, nie zgadujesz

**Dlaczego (21.10.2026).** Agent złożył prezentację, obejrzał ją w LibreOffice i uznał, że wszystko pasuje.
W PowerPoincie u człowieka: tytuł okładki nachodził na podtytuł, „2 800” łamało się na „2 8 / 00”, „2026” na
„202 / 6”, hasła w kartach wchodziły na dopiski, tekst w zielonym pasie wylewał się poza pas. Dwie przyczyny:

1. **Brak Mindset przy renderze.** Mindset to szeroka czcionka z samymi wersalikami. Czcionka zastępcza jest
   węższa, więc u agenta tekst się mieścił, a w PowerPoincie już nie.
2. **Autodopasowanie kłamie.** Pola szablonu mają „zmniejsz tekst przy przepełnieniu”. LibreOffice zmniejsza pismo
   sam przy każdym renderze, PowerPoint pokazuje pismo 100%, dopóki ktoś nie kliknie w pole. Podgląd z LibreOffice
   pokazuje więc ciaśniejszy tekst, niż zobaczy człowiek.

**Co robisz:**

- Przed zapisem i przed renderem uruchamiasz `sprawdz(prs, FONTY)`. Lista musi być **pusta**. Funkcja liczy linie
  prawdziwymi czcionkami przy piśmie 100% i zgłasza: tekst wyższy niż pole (wyleje się na sąsiednie) oraz słowo
  szersze niż pole (złamie się w środku, np. „2 800”, „2026”, długie nazwy). Na czystym szablonie daje 0 zgłoszeń.
- Nie masz plików czcionek? Poproś o nie użytkownika (folder `fonty` z paczki albo `assets/fonts` skilla `prezentacje`) —
  to jedyne pytanie, które wolno zadać w trakcie. Nie dostaniesz ich: nie oddajesz jako gotowej; w raporcie piszesz
  wprost „nie sprawdziłem, czy tekst się mieści — brak czcionek”.
- Do renderu w LibreOffice: zainstaluj czcionki (Linux / czat: skopiuj do `~/.fonts` i `fc-cache -f`; sprawdź
  `fc-list | grep -i mindset`; Mac: `~/Library/Fonts`) i renderuj kopię z `podglad()` — bez autodopasowania, tak jak
  zobaczy to PowerPoint.

**Gdy `sprawdz` coś zgłasza** — w tej kolejności, nigdy przez zmniejszenie pisma ani powiększenie pola:

1. Skróć tekst (nowa prezentacja): hasło do tylu słów, ile mieści pole; reszta do dopisku. Tytuł na okładce ma tyle
   linii, ile podpowiedź szablonu (zwykle jedna) — dłuższy podziel: krótki tytuł + reszta w podtytule.
2. Liczba za szeroka dla kafla (np. 4 cyfry w Mindset 72 pt w wąskim kaflu): zapis krótszy, jeśli nie zmienia sensu
   („2,8 tys.”), a rok („2026”) nie jest liczbą-bohaterem (sekcja 6.1) — przenieś go do hasła, a w kaflu daj liczbę.
   Inaczej weź slajd z szerszymi kartami (3 karty t62 zamiast 4 kafli t38).
3. Mniej elementów w rzędzie: 3 karty zamiast 4 dają szersze pola.
4. Inny slajd z katalogu z pojemniejszym polem; w przełożeniu 1:1 — tylko to (treści nie skracasz).
5. Nie da się: DO DECYZJI z numerem slajdu.

**Zasady pracy na pliku:**

- Szukaj kształtów po **nazwie** (`sh.name`) albo `pola(slide.shapes, "[Claim")` — pola o danym początku tekstu
  w kolejności czytania (wiersz po wierszu, od lewej); powtarzające się pola (`00%`, `[wartość]`,
  `[krótkie rozwinięcie]`) wypełniasz po kolei. Nie porównuj tekstu ręcznie: szablon ma twarde spacje (`\u00a0`).
  Nazwy mówią, co to jest: „Tytuł slajdu”, „Packshot - …”, „Owoc / element smaku - …”, „Zdjęcie - …”,
  „Ikona / grafika - …”, „Logo marki”, „Film … (link)”.
- `wpisz()` zachowuje czcionkę, kolor i rozmiar z szablonu. Nie ustawiaj własnych kolorów, czcionek ani rozmiarów
  pisma, nie przesuwaj i nie zmieniaj rozmiaru pól tekstowych. `/` w podpowiedzi (`[Nazwa / produktu]`) = dwa akapity.
- Pola mają stałą wysokość. Tekst ma mieć **tyle linii i mniej więcej tyle znaków, ile podpowiedź w szablonie**.
  Kolumna „Mieści” (sekcja 7) to orientacja; rozstrzyga `sprawdz()` (sekcja 4a), potem render. Z testów: tytuł t31 i t37 krótko (t37:
  jedna linia, ok. 35 znaków, pod nim duża liczba), nazwa w t34 — jedna linia, wartość w kaflu t45 — najwyżej 2 linie.
  Nie mieści się? Nie zmniejszaj pisma — skróć (nowa prezentacja), weź inny slajd albo podziel treść na dwa slajdy.
- Niepotrzebny element (czwarty claim, trzecia metka smaku): usuń komplet — pole, jego kartę/tło i ikonę
  (`sh._element.getparent().remove(sh._element)`), żeby nie została pusta karta. Wyjątek: w siatkach (t45, t32)
  brakujące dane zostaw jako `[nawias]` i wpisz do DO DECYZJI — dziura w siatce wygląda gorzej.
- **Obrazy:** `obraz()` wstawia plik w ramkę szablonu w całości. Paczki i owoce w szablonie to kulki z kreatyną
  (cola-lemon, arbuz, mango-marakuja): ten produkt — możesz je zostawić; inny — podmień paczkę, a owoce zastąp
  elementami z materiału albo usuń. Ikony: zostaw ikony szablonu albo skopiuj pasującą z innego slajdu szablonu;
  bez emoji i obcych ikon; ikona nie pasuje i nie ma lepszej — usuń.
- Wykresy t52, t53 to prawdziwe wykresy: `sh.chart.replace_data(...)` (`CategoryChartData`). Tabele (t35, t42, t55)
  i słupki (t39) są złożone z kształtów: tekst przez `wpisz()`, długość słupka przez `sh.width` proporcjonalnie do liczby.
- Film (t48–t50): link YouTube ustaw na każdym kształcie z „(link)” w nazwie (`sh.click_action.hyperlink.address = url`).
- **Przełożenie gotowej .pptx bez programu:** czytasz oryginał python-pptx (teksty, także w grupach i tabelach;
  obrazy `shape.image.blob`), dla każdego slajdu nazywasz kształt treści, bierzesz slajd z katalogu i wpisujesz te
  same słowa w nowych rolach (sekcja 6). Slajd N = slajd N. Tekst, który się nie mieści, zostaje — wybierasz
  pojemniejszy slajd (t15, t16, t61, t17), nie skracasz.

## 5. Styl Dobra Kaloria (pilnuje go szablon — nie psuj)

**Skąd ta metoda (13.10.2026).** Właściciel odrzucił dwie wersje tej samej prezentacji i przyjął trzecią. Odrzucona 1
(sam tekst w Mindset na całą szerokość): „tekst jednolity, bez sensownych akapitów, podnagłówków, widać, że to nie jest
z szablonu”. Odrzucona 2 (zdania jako akapity Lato w kartach): „Za dużo czcionki Lato. Za mało tam jest prezentacji, za
dużo tekstu, bloków tekstu. Za mało jakichś haseł.” Przyjęta 3 (hasła, liczby, wnioski w klockach szablonu): „TAK! teraz
ta prezentacja jest cudownie piękna.” O błędach tekstu: „Tego typu błędy, literówki, sieroty itp. - POPRAWIASZ.”

1. Tło slajdu **białe**; bieli jest najwięcej. Beż, ecru i szary nigdy jako tło całego slajdu (wyjątki z szablonu:
   okładki, przekładki, zakończenia na zieleni, karta smaku w kolorze smaku).
2. **Kremowy** (Akcent 3) tylko jako karta albo kafel na bieli. Bez karty w karcie.
3. **Hasła czcionką Mindset** (nagłówkowa, sama robi wersaliki — tekst wpisujesz normalnie): zdanie do 12 słów albo
   początek dłuższego zdania.
4. **Lato** tylko jako krótki dopisek pod hasłem, najwyżej 18 pt. Akapit Lato bez hasła to błąd (wyjątki: sekcja 6.2).
5. Tekst ciemnobrązowy z motywu (Tekst 1, nie czysta czerń); drobne etykiety i podpisy w beżu (Akcent 5).
6. **Zieleń marki** (Akcent 1) na liczby, etykiety, pasy-wnioski, kropki, metki. Czerwień (Akcent 2) tylko jako akcent
   i słowo wyróżnione w oryginale albo zła wiadomość.
7. **Żółty** (Akcent 6) — najwyżej jedna wyróżniona rzecz; w konwersji zwykle wcale. Bez przycisków CTA.
8. **Bez obrysów** wokół kart, kafli i tagów (karta = wypełnienie). Ikony liniowe, zielone. Zero plam i bąbelków za produktem.
9. Kolory i czcionki **tylko ze slotów motywu** (Projektowanie > Warianty), bez własnych kodów hex; wyjątek: kolory smaków.
10. Logo, numer strony, pasy i karty zostają tam, gdzie są w szablonie.

| Slot motywu | Kolor | Rola |
|---|---|---|
| Tekst 1 | `#3B2A20` | tekst („miły ciemny ton”, nie czerń) |
| Tło 1 / Tło 2 | `#FFFFFF` | tło slajdu |
| Akcent 1 / Tekst 2 | `#0F763E` | zieleń marki |
| Akcent 2 | `#DA272D` | czerwony akcent |
| Akcent 3 | `#FDF8EC` | kremowa karta |
| Akcent 4 | `#E9F2EC` | jasna zieleń |
| Akcent 5 | `#AD8767` | beż etykiet i podpisów |
| Akcent 6 | `#FFD42A` | żółty akcent |
| czcionki | Mindset (nagłówki), Lato (tekst, pogrubienie = Lato Bold) | |

Kody podaję tylko, żebyś rozpoznał kolor na zrzucie — w pliku używasz slotów, nie kodów.

## 6. Treść: slajd to plakat, nie kartka

Na slajdzie widać: tytuł, 1–4 hasła w Mindset, przy nich liczbę albo ikonę, pod hasłem krótki dopisek w Lato, na dole
wniosek w pasie. Słowa dostają **role**:

| Rola | Co to jest | Jak wygląda (klocek specu) |
|---|---|---|
| hasło | zdanie do 12 słów albo początek dłuższego zdania | Mindset, kolor tekstu (`lead`) |
| dopisek | reszta zdania i kolejne zdania akapitu | Lato, najwyżej 18 pt (`p`) |
| liczba-bohater | liczba z jednostką stojąca w haśle, powtórzona nad nim | Mindset, zieleń (`hero`) |
| wniosek | zdanie-puenta, „Ważna kwestia – …”, „Insight: …”, linia od „=” | pas zielony, czerwony = zła wiadomość (`band`) |
| etykieta | „CT: …”, „TA: …”, „Karton: 12 szt.” | kafel etykieta + wartość (`kv`) albo nagłówek karty (`h`) |
| punkt | pozycja listy, kolejne zdanie długiego akapitu | punkt z ikoną albo kafel z ikoną (`li`) |

Miara kontrolna: w kartach z tekstem więcej słów stoi w Mindset niż w Lato (wzorzec przyjętej prezentacji: 492 do 309).

### 6.1 Hasłowanie i progi pisma

1. Zdanie do 12 słów jest hasłem w całości.
2. Dłuższe: hasło kończy się na pierwszym przecinku po 4–15 słowach (przecinek zostaje przy haśle); gdy go nie ma —
   przed pierwszym `i / oraz / ale / wobec / czyli` na pozycji 4–15; bez granicy do 24 słów — całe jest hasłem; powyżej
   24 — akapit w karcie i DO DECYZJI. Hasło nie może wyjść puste („WHO (2023) zaleca warunkowo,”) — przesuń granicę.
3. Jedno hasło na kartę w rzędzie trzech i więcej kart. Nagłówek-etykieta (1–2 słowa albo z dwukropkiem) hasła nie blokuje.
4. Liczba-bohater: pierwsza liczba z jednostką (%, mln, mld, zł, g/kg…) w HAŚLE, jedna na kartę. Nie jest bohaterem:
   rok i data, EAN, gramatura opakowania, nazwa z cyfrą (B12, GLP-1), zakres wieku w etykiecie, liczba z oświadczenia żywieniowego.
5. Hasło wyróżnione kolorem w całości idzie w kolorze tekstu; wyróżnione pojedyncze słowa zostają wyróżnione.
6. Hasło nigdy mniejsze od dopisku tej samej karty (co najmniej +2 pt). Zielony tekst tylko jako etykieta, liczba albo pas.
7. **Progi:** hasło od 16 pt (cel 18+), dopisek i punkty od 13 pt (cel 14), etykiety od 11 pt; rząd 5–6 kafli z krótkimi
   hasłami: 14–16 pt. Treść spada poniżej progu → NIE zmniejszasz pisma i nie usuwasz słów; upraszczasz układ w tej
   kolejności: zdejmij ikony z kart; 4 karty w rzędzie → siatka 2 × 2; nagłówek karty → wiersz nad kartami; kolejne
   zdania długiego akapitu → punkty. Dalej się nie mieści → DO DECYZJI (za dużo treści na slajd — decyzja autora).

### 6.2 Czego hasłowanie nie dotyczy

Tabela, wykres, slajd z samym zdjęciem albo zrzutem, okładka, przekładka rozdziału, zakończenie, wartości odżywcze,
slajd produktu (EAN, gramatura, claimy z karty) i cytat zostają w układzie szablonu; sprawdzasz w nich tylko błędy
tekstu i czytelność. Komórek tabeli nie dzielisz. Dopuszczalne akapity Lato: t15, t16, t61 i zdanie > 24 słów bez
miejsca podziału (DO DECYZJI).

### 6.3 Przełożenie gotowej prezentacji (1:1) — co wolno, czego nie

**Zostaje bez zmian:** liczba slajdów (slajd N = slajd N — właściciel porównuje dwa okna obok siebie), każde słowo
i liczba, kolejność czytania, obrazy w całości, słowa wyróżnione kolorem, hiperłącza (na tych samych słowach, bez
dopisanej stopki „Link: …”; adres, którego nie ma na slajdzie, idzie do notatek), interpunkcja.

**Wolno:** podzielić zdanie na hasło i dopisek; powtórzyć liczbę z hasła jako liczbę-bohatera (jedyne dozwolone
powtórzenie); rozdzielić akapit na kafle (zdanie = kafel, najwyżej 4, 4 = siatka 2 × 2); przenieść zdanie-wniosek,
które i tak stoi najniżej, do pasa; dać ikonę; zrobić z nagłówka slajdu tytuł, a z belki rozdziału etykietę nad tytułem.

**Nie wolno:** dodawać ani kasować slajdów, agendy, przekładek; pisać własnych tytułów i haseł; łączyć, dzielić,
przestawiać slajdów; dopisywać, skracać, przestawiać treści; wymyślać liczb; przycinać obrazów; kolorów i czcionek
spoza motywu; przepisywać tekstu ze zrzutu; zmniejszać pisma, żeby się zmieściło. „Tytuł = wniosek” i „jedna myśl na
slajd” dotyczą nowej prezentacji, **nie** przełożenia.

### 6.4 Błędy w tekście: poprawiasz, ale ostrożnie

Poprawiasz tylko, gdy spełnione są WSZYSTKIE cztery warunki: a) to, co stoi w źródle, nie jest w tym zdaniu poprawnym
polskim słowem, formą, nazwą, skrótem ani słowem obcym; b) jest jedna oczywista poprawna forma, różna najwyżej o spację
albo 2 znaki w jednym słowie; c) słowo nie stoi w cytacie, tekście obcojęzycznym, liczbie, oświadczeniu żywieniowym
lub zdrowotnym, nazwie prawnej ani hiperłączu; d) nie zmieniasz szyku, stylu ani wielkości liter. Wątpliwość = nie
poprawiasz, wpisujesz do DO DECYZJI. Mieszczą się tu: sklejone słowa („komunikacjaod” → „komunikacja od”), literówki
(„odwrotem o węglowodanów” → „odwrotem od węglowodanów”), oczywisty błąd odmiany („do zbudowanie trialu” → „do
zbudowania trialu”), zdublowane słowo, brak spacji po przecinku, spacja przed przecinkiem, podwójne spacje. Nie
poprawiasz, tylko zgłaszasz: nazwy własne i marki, skróty, liczby i jednostki, wielokropki i myślniki autora, zdania
niezręczne, wszystko, co zmienia sens. Program łapie tylko słowa spoza słownika — przeczytaj każdy slajd sam.

Droga A: każdą poprawkę wpisz do specu, inaczej kontrola treści uzna ją za zgubione słowo:
`"poprawki": [{"slajd": 12, "bylo": "komunikacjaod", "jest": "komunikacja od", "powod": "sklejone słowa"}]`
(`slajd` = numer slajdu oryginału; zacznij od listy `bledy_tekstu` w specu i `raport.json`). Droga B: Wypisz poprawki w raporcie.

### 6.5 Dane, źródła, typografia

- **Nie wymyślaj danych.** Każda liczba ma źródło z materiału, wpisane w stopkę „[Źródło: …]” (kto, kiedy, próba).
  Brak liczby — zostaje `00%` / `[nawias]` i wpis w DO DECYZJI.
- Claimy produktu i oświadczenia żywieniowe tylko dosłownie z karty wprowadzenia — to sprawy prawne. Materiały się
  rozjeżdżają (inna nazwa na karcie i na paczce, dwie wersje claimu)? Weź wersję z karty / oświadczeń, różnicę wpisz
  do DO DECYZJI. Bez porównań koncepcji opakowań.
- Packshoty ze znakiem „DEMO” (w szablonie albo w materiale) trzeba podmienić przed wysłaniem poza firmę — zgłoś to.
- Polska typografia: bez jednoliterowych słów i spójników na końcu linii (`twarde()`; Droga A: kontrola
  `verify.ps1`), bez jednego słowa w ostatniej linii, bez „ok. / 12 mln” rozdzielonego łamaniem. Sieroty to błędy
  łamania, nie tekstu: poprawiasz podziałem hasło / dopisek albo szerokością karty.

## 7. Dobór slajdu: z katalogu szablonu, nie z głowy

Dla każdego slajdu nazwij **kształt treści**, potem weź wzór. Żaden nie pasuje → złóż z tych samych klocków
i wpisz slajd do DO DECYZJI.

| Kształt treści | Wzór w szablonie |
|---|---|
| 2–4 fakty, każdy z liczbą (+ wniosek) | t62 Trzy fakty w kartach, t38 KPI, t44 Argumenty dla handlu |
| 2–4 zdania, część bez liczby | t62 (ikona zamiast liczby), t56 Okazje spożycia |
| 2–6 krótkich haseł | t36 Zalety w zielonych kaflach, t32 Siatka cech z ikonami, t56 |
| jedna teza | t14 Jedno zdanie – teza |
| jedna liczba-bohater | t37 Liczba-bohater |
| dwie strony („dobra / zła wiadomość”) | t59 Dwie karty |
| „dziś” kontra „z nami” | t21 Porównanie, t55 Porównanie z konkurencją |
| etykieta: wartość („CT: …”, logistyka) | t45 Logistyka |
| nagłówek + lista zdań, długi akapit | t17 Punkty, t18 Punkty ze zdjęciem, t13 Wstęp |
| proces, kroki, daty | t19 Kroki, t43 Oś czasu |
| zdanie z 3+ parami „nazwa (NN%)” | t39 Wykres słupkowy |
| udział / trend | t52 Wykres pierścieniowy, t53 Wykres kolumnowy, t41 A kontra B |
| cytat z autorem (+ wynik) | t20 Cytat, t60 Cytat i wniosek |
| obrazy + podpis-wniosek | t63 Zrzuty w całości i wniosek, t51 Przed i po, t28 Galeria |
| produkt i claimy | t30 Anatomia produktu, t31 Zalety z produktem, t24 Tekst i produkt, t25 |
| smaki, linia, wartości odżywcze | t33 Karta smaku, t34 Linia produktów, t35 Wartości odżywcze |
| dla handlu | t44, t45, t54 Cena i marża, t58 Następne kroki |
| akapit, który musi zostać akapitem | t61, t16, t15 |
| okładka / przekładka / zakończenie | t03–t09 / t11, t12 / t64, t65, t47 |

**Katalog** (numer = slajd w pliku `DK - szablon prezentacji - pełen.pptx`; slajdy 1–2 to instrukcje — nigdy ich nie bierz):

| Nr | Slajd | Kiedy | Mieści |
|---|---|---|---|
| 3 | Okładka: cała linia smaków | Nowa linia 2-3 smaków: duże białe logo na zieleni, „NOWOŚĆ” i nazwa linii po prawej, pod spodem trzy paczki naraz. | tytuł 1-2 linie Mindset; 3 paczki (packshot-trio) |
| 4 | Okładka: paczka na granicy zieleni | Nowość jednego produktu: duża paczka przecina granicę zieleni i bieli, po prawej tytuł, claim i trzy metki smaków. Najmocniejsze wejście. | tytuł do 3 linii; 1 zdanie claimu; do 3 metek smaków; 1 packshot |
| 5 | Okładka: biały tytuł na zieleni | Prezentacja produktu dla sieci handlowej: zielone tło z logo i dużym białym tytułem, paczka po jasnej stronie. | tytuł do 3 linii; claim 1-2 linie; do 3 metek; 1 packshot |
| 6 | Okładka klasyczna 50/50 | Najbezpieczniejszy wybór: połowa zielona z dużym logo na środku, połowa biała z tytułem, metkami smaków i paczką. | tytuł do 2 linii; do 3 metek; 1 packshot |
| 7 | Okładka bez produktu 50/50 | Spotkanie, raport, prezentacja firmowa: lewa połowa zielona z logo, prawa biała z tytułem, kreską i jedną linią opisu. | tytuł do 3 linii; 1 linia opisu; autor i data w stopce |
| 8 | Okładka bez produktu na zieleni | Otwarcie konferencji, szkolenia, eventu: cała zieleń marki, duży biały tytuł, drobne owoce przy krawędzi. | tytuł do 3 linii; 1 linia daty i miejsca |
| 9 | Okładka bez produktu, jasna | Raporty, podsumowania kwartału, prezentacje wewnętrzne: jasne tło, zielony pas z logo na górze, bardzo duży tytuł. | tytuł do 2 linii bardzo dużym pismem; 1 linia zakresu; autor i data |
| 10 | Agenda | Spis 3-8 punktów z numerami 01, 02...; od 5 punktów układ sam dzieli się na dwie kolumny. | 3-8 punktów; tytuł punktu 1 linia, opis do 1 linii |
| 11 | Przerywnik rozdziału, ciemny | Rozdziela główne części: zielone tło, nad tytułem etykieta rozdziału, pod nim jedno zdanie, co będzie w części. | etykieta + tytuł 1-2 linie + 1 zdanie |
| 12 | Przerywnik rozdziału z numerem | Jasny przerywnik z gigantycznym bladym numerem (02) w rogu, tytuł rozdziału i jedno zdanie. Spokojniejsza wersja t11. | numer 1-2 cyfry + tytuł 1-2 linie + 1 zdanie |
| 13 | Wstęp z akapitem | Początek prezentacji albo rozdziału: duży akapit otwierający (2-3 zdania) i pod nim trzy krótkie rozwinięcia z kreską. | akapit 2-3 zdania; 3 kolumny: hasło + 1-2 zdania |
| 14 | Jedno zdanie – teza | Jedna mocna teza, wniosek albo cytat z badania na środku kremowego slajdu, nad nim etykieta, pod nim opcjonalny podpis. | 1 zdanie do ok. 12 słów (pismo samo maleje od 60 pt); podpis 1 linia |
| 15 | Tekst długi w dwóch kolumnach | Opis rynku, historii, strategii, gdy tekst naprawdę musi zostać akapitami: dwie kolumny drobnego Lato. | ok. 180 słów w 2 kolumnach po 1-3 akapity |
| 16 | Akapit w karcie | Edukacja i kontekst: tytuł-pytanie („Dlaczego warto…?”) i 1-3 akapity w kremowej karcie, drobne owoce w rogach. | tytuł-pytanie do 2 linii; 1-3 akapity (pismo 16 -> 13 pt) |
| 17 | Punkty | Lista 3-6 haseł z jednym zdaniem rozwinięcia: zalety, warunki, ustalenia. Zielona kropka przy każdym haśle. | 3-6 pozycji: hasło 1 linia + 1 zdanie |
| 18 | Punkty ze zdjęciem | Lista 3 haseł z rozwinięciem i zdjęcie po prawej w kremowym polu (półka, event) - gdy punkty potrzebują kontekstu. | 3 pozycje: hasło + 1 zdanie; 1 zdjęcie |
| 19 | Kroki / proces | 3-5 etapów w kolejności: kółka 1-4 na linii, pod każdym kremowa karta z nazwą etapu i jednym zdaniem. | 3-5 kart: etap 1 linia + do 3 linii opisu |
| 20 | Cytat / opinia | Opinia klienta, partnera, konsumenta, influencera: duży kursywny cytat z zieloną kreską i autorem (imię, funkcja, firma). | cytat 1-2 zdania; autor 1 linia + rola |
| 21 | Porównanie: dziś i propozycja | Dwie kolumny „dziś” kontra „z nami”: lewa kremowa z obserwacjami, prawa zielona (wyróżniona) z korzyściami. | 2 kolumny: nagłówek + 3-5 punktów |
| 22 | Tekst i zdjęcie | Opis produktu, kampanii, eventu: tytuł, 2-4 zdania i 3 punkty po lewej; zdjęcie po prawej do krawędzi slajdu. | 2-4 zdania + 3 punkty; 1 zdjęcie |
| 23 | Zdjęcie i tekst | Lustro t22: zdjęcie po lewej do krawędzi, tekst po prawej. Użyj na zmianę z t22 dla rytmu. | 2-4 zdania + 3 punkty; 1 zdjęcie |
| 24 | Tekst i produkt | Opis produktu z 3 claimami po lewej, packshot po prawej na kremowym tle z drobnymi elementami smaku. | tytuł do 2 linii; zdanie opisu; 3 claimy; 1 packshot |
| 25 | Zalety z ikonami i zdjęciem | Zdjęcie w zaokrąglonej kremowej karcie po lewej, po prawej tytuł z hasłem i 4 zalety, każda z ikoną i jednym zdaniem. | 3-4 zalety: ikona + nazwa + 1-2 zdania; 1 zdjęcie |
| 26 | Zdjęcie na cały slajd z podpisem | Kadr z kampanii, półka w sklepie, event: zdjęcie na cały slajd, w rogu biała karta z podpisem (gdzie, kiedy, co widać). | 1 zdjęcie + podpis 1 zdanie |
| 27 | Zdjęcie na cały slajd | Zdjęcie, które mówi samo za siebie: cały slajd, bez podpisu i bez tytułu. | 1 zdjęcie |
| 28 | Galeria 3 zdjęć | Trzy wysokie zdjęcia z podpisami: półki, POS, materiały. | 3 zdjęcia + podpis 1 linia pod każdym |
| 29 | Galeria 6 zdjęć | Relacja z eventu, materiały od twórców, ekspozycje: siatka 3 x 2 niskich zdjęć z podpisami. | 6 zdjęć w 2 rzędach + podpisy |
| 30 | Anatomia produktu | Główny slajd produktowy: paczka pośrodku, po 2 claimy z ikoną po każdej stronie. | 4 claimy: ikona + hasło + 1 linia; 1 packshot |
| 31 | Zalety z ikonami i produktem | „Dlaczego ten produkt”: packshot w kremowej karcie po lewej, po prawej 4 claimy z karty wprowadzenia, każdy z ikoną. | 3-4 claimy: ikona + nazwa + 1 zdanie; 1 packshot |
| 32 | Siatka cech z ikonami | 3-6 cech w siatce 3 x 2: ikona, zielony nagłówek, opis. Skład, oświadczenia żywieniowe, wartości marki. | 3-6 cech: ikona + nagłówek 1 linia + 1-2 linie |
| 33 | Karta smaku | Jeden smak na slajd: kolorowe tło smaku, nazwa Mindsetem, opis, trzy twarde dane (%, 0%, gramy) i EAN, paczka po prawej. | 1 smak: nazwa 2 linie; opis 2 linie; 3 dane; EAN |
| 34 | Linia produktów | Portfolio: 2-4 karty obok siebie, każda z packshotem, nazwą i zieloną metką z gramaturą. | 2-4 SKU: packshot + nazwa 1-2 linie + metka |
| 35 | Wartości odżywcze | Packshot po lewej, po prawej tabela 100 g / porcja przepisana z karty wprowadzenia (8-9 wierszy). | ok. 9 wierszy x 3 kolumny + przypis |
| 36 | Zalety w zielonych kaflach | 3-4 zielone kafle z obrazkiem owocu u góry, nazwą zalety i zdaniem (jak sekcja „Zalety” w sklepie). | 3-4 kafle: obrazek + nazwa 1-2 linie + 1 zdanie |
| 37 | Liczba-bohater | Jeden najważniejszy wynik: ogromna zielona liczba, pod nią opis, dwa małe kafle z liczbami pomocniczymi, packshot po prawej. | 1 liczba do ok. 5 znaków; opis 1 linia; 1-2 liczby pomocnicze |
| 38 | Wskaźniki (KPI) | 3-4 liczby obok siebie w kaflach, pierwszy zielony (wyróżniony); każda z krótkim opisem pod spodem. | 3-4 kafle; liczba do ok. 8 znaków; opis do 3 linii |
| 39 | Wykres słupkowy | 3-7 pozycji jako poziome słupki (zielone mocne, brązowe słabsze) z liczbą po prawej i kremową kartą wniosku. | 3-7 pozycji; podpis 1 linia; wniosek 1-2 zdania |
| 40 | Dwie grupy wyników | Dwie karty obok siebie (segmenty, kanały, regiony): nagłówek, opis i w każdej 2 duże liczby z opisem. | 2 grupy x 2-4 wyniki; opis grupy 1 linia |
| 41 | A kontra B | Jeden pasek dzieli dwie opcje: duże liczby po bokach, zielony i jasny odcinek, pod nim nazwy opcji i komentarz. | 2 wartości (liczba + nazwa) + 1 komentarz |
| 42 | Tabela | Asortyment, cennik, indeksy: nagłówek kolumn i wiersze naprzemiennie kremowe; liczby wyrównane do prawej. | do ok. 5 kolumn x 8 wierszy |
| 43 | Oś czasu | 3-6 etapów z datami na poziomej osi; wypełnione kółko to bieżący etap, opisy na przemian nad i pod osią. | 3-6 etapów: data + nazwa + 1 linia |
| 44 | Argumenty dla handlu | 3-4 powody, by wprowadzić produkt: pierwsza karta zielona, w każdej numer, liczba, argument i uzasadnienie ze źródłem. | 3-4 karty: liczba + argument + uzasadnienie 2 linie |
| 45 | Logistyka | Siatka 4 x 2 kafli: mała etykieta wersalikami i pod nią wartość Mindsetem (karton, paleta, termin, przechowywanie). | 4-8 kafli: etykieta 1 linia + wartość 1 linia |
| 46 | Karty ze zdjęciem | 3 kremowe karty z zielonym znaczkiem kanału, zdjęciem, nazwą działania i opisem: wsparcie marketingowe, POS, kanały. | 3 karty: znaczek + zdjęcie + nazwa + 1-2 zdania |
| 47 | Osoba kontaktowa | Koniec spotkania handlowego: okrągłe zdjęcie, imię i rola Mindsetem, pod spodem telefon, e-mail, www. | 1 osoba: imię, rola, 3 linie kontaktu |
| 48 | Film na cały slajd | Spot, film produktowy, relacja z eventu: film na cały slajd z biała kartą tytułu; w pokazie klik odtwarza. | 1 film 16:9 + tytuł + 1 zdanie |
| 49 | Claim i film | Po lewej kremowa karta z elementem produktu i zielonym claimem („Co dobrego w kreatynie”), po prawej karta z tytułem i miniaturą filmu. | 1 claim (hasło + 1-2 zdania) + 1 film |
| 50 | Film z tekstem | Film 16:9 w zaokrąglonej ramce po prawej; po lewej opis (2-3 zdania) i 3 punkty. Gdy film trzeba skomentować. | 1 film + 2-3 zdania + 3 punkty |
| 51 | Przed i po | Dwa zdjęcia obok siebie ze znaczkami „Przed” i „Po”: półka przed i po, stare i nowe opakowanie, ekspozycja. | 2 zdjęcia + podpis 1 linia pod każdym |
| 52 | Wykres pierścieniowy | Udział, struktura sprzedaży, podział grupy: edytowalny pierścień z liczbą w środku i legendą z procentami. | 3-5 części; liczba w środku wpisana ręcznie |
| 53 | Wykres kolumnowy | Trend w czasie (sprzedaż, dystrybucja, zasięg): edytowalne zielone kolumny z wartościami i karta wniosku. | ok. 6 miesięcy / okresów; wniosek 1-2 zdania |
| 54 | Cena i marża | Dla handlu: packshot, zielona metka z rekomendowaną ceną detaliczną i 4 karty warunków (cena zakupu, marża, promocja, min. zamówienie). | 1 produkt: cena + 4 karty wartość / etykieta |
| 55 | Porównanie z konkurencją | Cechy w wierszach, kolumny: nasz produkt (zielona, wyróżniona) i konkurenci, w komórkach ✓ lub ✗ albo wartość. | 4-6 cech x 2-3 kolumny |
| 56 | Okazje spożycia | 4 momenty dnia na osi z ikonami w kółkach: pora, okazja i jedno zdanie, dlaczego wtedy. | 4 momenty: ikona + pora + nazwa + 1-2 linie |
| 57 | Social media | Trzy telefony z postami lub reelsami kampanii; pod każdym kanał i wynik (zasięg, wyświetlenia). | 3 zrzuty + kanał + wynik |
| 58 | Następne kroki | Checklista po spotkaniu: zadanie, kto, termin; zaznaczony kwadrat = zrobione. | do 5 wierszy: zadanie + osoba + termin |
| 59 | Dwie karty: dobra i zła wiadomość | Dwie równe karty obok siebie: nagłówek (zielony / czerwony) i jedno zdanie Mindsetem pod nim. Dwie strony jednej sprawy. | 2 karty: nagłówek 1-3 słowa + 1 zdanie do ok. 12 słów |
| 60 | Cytat i wniosek | Cytat z autorem (kursywa, zielona kreska) i pod nim kremowa karta z 2-3 wyśrodkowanymi hasłami, ostatnie czerwone („= wniosek”). | cytat 1 zdanie; autor 1 linia; karta 2-3 hasła |
| 61 | Akapit w karcie z wyróżnieniem | 1-3 akapity Lato w kremowej karcie; 2-3 najważniejsze słowa w kolorze (czerwień = akcent, zieleń = marka). Dla tekstu, który musi zostać zdaniami. | 1-3 akapity po 2-3 zdania; stopka ze źródłem |
| 62 | Trzy fakty w kartach | 2-4 fakty z liczbą: w każdej karcie liczba-bohater (zielona), pod nią hasło Mindsetem (do 12 słów) i krótki dopisek Lato; pod kartami wniosek w zielonym pasie. | 3 karty (2-4); liczba do ok. 8 znaków; hasło do 12 słów; dopisek do 2 linii (max 18 pt); pas wniosku 1 zdanie, do 3 linii |
| 63 | Zrzuty w całości i wniosek | Dwa obrazy bez kadrowania (zrzuty ekranu, wykresy, paczki) i pod nimi jedno zdanie Mindsetem w zieleni; źródło drobnym drukiem. | 2 obrazy w całości + 1 zdanie wniosku |
| 64 | Zakończenie | Standardowy ostatni slajd: zieleń marki, logo, #zawszedobra i adres kontaktowy. | logo + hasztag + 1 linia kontaktu |
| 65 | Zakończenie z podziękowaniem | Jasne „DZIĘKUJEMY”, jedno zdanie na pożegnanie i zielony pas z logo oraz imieniem, telefonem, e-mailem. Dane zostają na ekranie w rozmowie. | tytuł; 1 zdanie; 1 linia kontaktu |

## 8. Kolejność slajdów nowej prezentacji

Typowo 6–13 slajdów. Okładka (t03–t09) → [agenda t10, gdy ≥ 8 slajdów] → problem / kontekst (t14, t62, t37) →
produkt (t30, t31, t24, t33, t34) → dowody: liczby, badania (t62, t38, t39, t40, t44) → dla handlu (t44, t45, t54, t58)
→ zakończenie (t64, t65, t47). Przekładka rozdziału (t11 albo t12 — jeden wariant na całą prezentację) tylko przy ≥ 10
slajdach. Ten sam slajd szablonu najwyżej 2 razy z rzędu; dla rytmu zmieniaj układy (t22 / t23).

## 9. Sprawdzenie przed oddaniem — dowód, nie raport

**Render do PNG** (zawsze pojedynczo, jeden plik naraz):

- Droga A: `powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\WORK\pliki programu\app\skill\scripts\render.ps1" -Src "<plik.pptx>" -Out "<katalog png>"`
  (otwiera tylko do odczytu; po OSTATNIEJ zmianie dodaj `-EmbedFonts`). Nie używaj `app\app\render_app.ps1` — zapisuje
  plik od nowa bez sumy kontrolnej i kolejna budowa zrobi „… (nowa wersja)”. Przy przełożeniu: plansze par stary | nowy
  `python "<folder programu>\WORK\pliki programu\app\skill\scripts\pary_slajdow.py" <png oryginału> <png wyniku> <katalog>`.
- Droga B: Najpierw `sprawdz()` = pusta lista (sekcja 4a). Potem render. **Wzorcem jest PowerPoint** — w nim
  prezentację zobaczy człowiek. Zanim wybierzesz render, ustal, gdzie pracujesz:
  1. **Na komputerze użytkownika z Windows** (Claude Code, Codex, Gemini CLI, Cursor — polecenia idą wprost do
     Windows; **nie Cowork**: Cowork uruchamia kod w maszynie z Linuksem, bez PowerPointa i bez dysków sieciowych,
     więc działa jak pkt 3) — sprawdź PowerPointa
     (`New-Object -ComObject PowerPoint.Application`). Jest → renderujesz **tylko nim**: `Presentations.Open(plik,
     ReadOnly)`, `slide.Export(png, "PNG", 1600, 900)`, zamknij. LibreOffice wtedy nie używasz.
  2. **Na Macu użytkownika z PowerPointem** — eksport do PDF przez AppleScript (`osascript`, aplikacja
     „Microsoft PowerPoint”) i obejrzenie stron PDF. Polecenie nie działa → poproś użytkownika o eksport
     (Plik > Eksportuj > PDF) i obejrzyj ten PDF. To polecenie nie było sprawdzane na Macu.
  3. **W czacie w chmurze** (claude.ai, Claude Desktop bez Cowork, ChatGPT, Gemini w przeglądarce) — pracujesz na
     serwerze bez PowerPointa. Dopiero tu: LibreOffice z zainstalowanymi Mindset i Lato, na kopii z `podglad()`:
     `soffice --headless --convert-to pdf podglad.pptx`, potem `pdftoppm -png -r 80 podglad.pdf slajd` albo PyMuPDF.
     W raporcie napisz wprost: „Podgląd z LibreOffice, nie z PowerPointa — otwórz plik w PowerPoincie i przejrzyj
     slajdy.”
  **Na zrzucie nagłówki muszą być grubymi wersalikami Mindset** — widzisz zwykłą czcionkę z małymi literami? Render
  jest nieważny: zainstaluj czcionki i powtórz. Brak renderu → powiedz wprost, że slajdów nie widziałeś (i oddaj
  wynik `sprawdz()`).

**Obejrzyj każdy slajd** narzędziem do czytania obrazów (z metodą `ui-ux-pro-max`: hierarchia, kontrast, czytelność)
i dla każdego odpowiedz:

1. Jaki to kształt treści i czy slajd jest z katalogu?
2. Czy każda karta ma hasło w Mindset, a akapit Lato dłuższy niż 3 linie nie stoi bez hasła?
3. Czy najważniejsza liczba jest bohaterem? Czy wniosek stoi w pasie?
4. Czy pismo trzyma progi (6.1) i nic nie wychodzi z karty ani nie nachodzi na inne pole?
5. Czy nic nie łamie się źle (słowo po słowie w wąskiej karcie, sierota, spójnik na końcu linii)?
6. Czy nie zostały puste karty, `00%`, `[nawiasy]` bez wpisu w DO DECYZJI, owoce innego produktu, znak DEMO bez zgłoszenia?
7. Czy ikona pasuje do treści?
8. Czy są błędy w tekście (6.4)?

Popraw i obejrzyj ponownie — najwyżej 3 podejścia na slajd; czego nie rozwiążesz, idzie do DO DECYZJI z numerem slajdu.

**Bramki oddania.** Droga A: `verify.ps1` —
`powershell -NoProfile -ExecutionPolicy Bypass -File "<folder programu>\WORK\pliki programu\app\skill\scripts\verify.ps1" -Src "<plik.pptx>"`
daje **`Tekst - problemy: 0`** bez błędu COM; przy konwersji dodatkowo `Treść: 100% akapitów` i czysta kontrola układu.
Droga B: **`sprawdz(prs, FONTY)` pusta** (pomiar prawdziwymi czcionkami) i `nawiasy(prs)` pusta albo każdy wpis
w DO DECYZJI. Obie drogi: Wszystkie slajdy obejrzane po ostatniej zmianie.
Bez tego nie piszesz „gotowe”.

Plik wynikowy: `<Temat> - nowy styl.pptx` obok materiału (w czacie: do pobrania). Nie nadpisujesz plików użytkownika.
Nic nie kasujesz rekurencyjnie; pliki robocze trzymasz w `_robocze\`.

## 10. Raport na koniec (po polsku, krótko)

1. Plik wynikowy, liczba slajdów, wyniki bramek; czy obejrzałeś slajdy jako obrazy.
2. Lista slajd → numer slajdu szablonu (Droga A: co zmieniłeś względem wersji z programu).
3. Co uzupełniłeś i skąd liczby; poprawione błędy tekstu (slajd, było → jest).
4. **DO DECYZJI:** brakujące dane i `[nawiasy]`; liczby bez źródła; rozbieżności w materiale; wątpliwe słowa i błędy,
   których nie wolno było poprawić; zmiany wielkości liter (`wielkosc-liter.txt`); wstawione wizualizacje produktów;
   packshoty ze znakiem DEMO; niepewne ikony i obrazy; slajdy, gdzie treść się nie mieści mimo uproszczeń; slajdy
   z własnym układem; slajdy ukryte lub NOWE (ukryte zostają w pliku — przed wysłaniem poza firmę usuń je albo zapisz PDF).

## 11. Gdy nie możesz uruchamiać kodu

- Masz dostęp do Windows z programem, ale nie możesz nic uruchomić: powiedz użytkownikowi „Otwórz folder
  `— SZABLON AI - skrypt` na dysku G:, uruchom **Prezentacje.exe** i upuść do okna folder produktu albo plik .pptx.”
- Czat bez plików i bez kodu: rozpisz prezentację slajd po slajdzie — numer slajdu szablonu, a pod nim tekst dla
  każdego pola (tytuł, hasła, dopiski, liczby, wniosek, źródło) w limitach z kolumny „Mieści”. Człowiek zduplikuje te
  slajdy w PowerPoincie (lewy panel: prawy klik > Duplikuj slajd), wklei tekst i usunie resztę.
- Użytkownik wkleił „Kopiuj polecenie” z programu: dostajesz tekst slajdów z rolami ([hasło], [liczba], [wniosek]…);
  wygląd widzisz tylko z dołączonych obrazów z folderu `plansze`. Masz dostęp do plików? Poproś o „polecenie dla
  agenta” z programu i pracuj według tego pliku.
