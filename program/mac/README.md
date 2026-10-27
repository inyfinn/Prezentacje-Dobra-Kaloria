# Stwórz prezentację na Maca (1.3)

Wersja programu dla macOS. To ten sam program co na Windows (okno i silnik w Pythonie), tylko pakowany jako
`Stwórz prezentację.app` i obraz `Prezentacje na Maca.dmg`. **Nie była jeszcze uruchomiona na prawdziwym Macu**
(budujemy ją w GitHub Actions). Lista rzeczy do sprawdzenia jest na końcu.

Działa na Macach z procesorem Apple (M1 i nowsze), macOS 11 albo nowszy. Mac z procesorem Intel: ta paczka na nim
nie ruszy (zgłoś, zbudujemy osobną).

## Jak dostać program (dla opiekuna)

1. Na GitHubie: repozytorium `inyfinn/Prezentacje-Dobra-Kaloria` -> **Actions** -> **Mac** -> **Run workflow**.
2. Po kilkunastu minutach otwórz ukończone uruchomienie. Na dole, w **Artifacts**, jest
   `Prezentacje-na-Maca-<wersja>`. Pobierz go (trzeba być zalogowanym na GitHubie).
3. GitHub pakuje artefakt w zip. Rozpakuj go: w środku jest plik **`Prezentacje na Maca.dmg`**. Ten plik przekaż dalej.

To nie jest GitHub Release. Wydania (Release) są tylko dla Windows i uruchamiają aktualizację u użytkowników Windows,
dlatego Maca nigdy tam nie wrzucamy.

## Instalacja na Macu (dla użytkownika)

1. Kliknij dwa razy `Prezentacje na Maca.dmg`. Otworzy się okno z programem i skrótem do **Programów**.
2. Przeciągnij **Stwórz prezentację** na **Programy**.
3. Pierwsze uruchomienie: program nie ma podpisu Apple, więc macOS go zatrzyma. Zrób jedno z dwóch:
   - Kliknij program **prawym przyciskiem** (albo Control + klik) -> **Otwórz** -> w oknie ostrzeżenia znów **Otwórz**.
   - W macOS 15 (Sequoia) i nowszym to bywa za mało: wejdź w **Ustawienia systemowe -> Prywatność i ochrona**, przewiń
     na dół i przy komunikacie o programie kliknij **Otwórz mimo to**.
   - Albo w Terminalu (zawsze działa):
     `xattr -dr com.apple.quarantine "/Applications/Stwórz prezentację.app"`
4. Kolejne uruchomienia: zwykłe dwukliknięcie.

## Co działa inaczej niż na Windows

- **Bez PowerPointa.** Program robi prezentację, ale nie robi zrzutów slajdów i nie sprawdza tekstu w PowerPoint.
  Zamiast tego pisze: „Nie sprawdzono w PowerPoint: na Macu program nie robi podglądu slajdów. Otwórz plik i przejrzyj slajdy.”
  Z tego powodu nie powstaje też „oko programu” (automatyczna zmiana układu po zrzutach) ani plansze PNG do czatu.
  Podgląd przez LibreOffice celowo pominięty: bez czcionki Mindset pokazałby fałszywy wygląd.
- **Czcionki.** Mindset jest zapisany w szablonie. Czcionkę Lato na Windows osadza w pliku PowerPoint, a na Macu tego kroku nie ma:
  zainstaluj Lato w Macu (pliki w `Stwórz prezentację.app/Contents/Resources/app/skill/assets/fonts`, dwukliknięcie ->
  **Zainstaluj czcionkę**), inaczej PowerPoint na Macu podstawi inną.
- **Folder prezentacji** powstaje domyślnie w `Dokumenty/Prezentacje Dobra Kaloria` (dysku M: na Macu nie ma). Inne miejsce
  wskazujesz przyciskiem „Zmień…”.
- **Ustawienia i logi:** `~/Library/Application Support/Dobra Kaloria/Stworz prezentacje` (log: `logi/ostatni.log`).
- **Aktualizacja** jest ręczna. Program sam sprawdza, czy jest nowsza wersja, i pokazuje stronę, z której ją pobrać;
  nie podmienia własnych plików.
- **Claude Code** otwiera się w Terminalu (Terminal.app). Przy pierwszym użyciu macOS zapyta, czy program może sterować
  Terminalem: kliknij **OK**. Polecenie `claude` znajdujemy też w `~/.local/bin`, `/opt/homebrew/bin` i `/usr/local/bin`.
- **Claude, ChatGPT:** jeśli aplikacja jest w `/Applications` (albo `~/Applications`), program otwiera ją; inaczej otwiera stronę w przeglądarce.
- **Pliki .doc, .rtf, .odt** program na Macu nie czyta (na Windows robi to przez Word). Zapisz je jako .docx, .txt albo PDF.
- **Wideo online** (YouTube w slajdzie) wstawia PowerPoint na Windows. Na Macu w slajdzie zostaje obraz z linkiem do filmu.
- **Przeciąganie plików** do okna: pliki powinny działać. Przeciąganie całego folderu może nie działać (patrz niżej);
  przyciski „Wybierz folder” i „Wybierz pliki” działają zawsze.

## Dla AI i skryptów (wiersz poleceń)

Osobnego `stworz-cli` w pakiecie nie ma. Ten sam plik wykonywalny z argumentami działa jak wiersz poleceń:

```bash
"/Applications/Stwórz prezentację.app/Contents/MacOS/stworz-prezentacje" --help
"/Applications/Stwórz prezentację.app/Contents/MacOS/stworz-prezentacje" "<folder prezentacji>" --scenariusz "<folder>/scenariusz.md"
```

Bez argumentów (albo z nieistniejącą ścieżką) otwiera się okno. `POLECENIE.md` w folderze prezentacji podaje agentowi
tę ścieżkę automatycznie.

## Budowa lokalna (na Macu)

```bash
cd mac
python3 -m pip install -r requirements-mac.txt
bash buduj-mac.sh
```

Wynik: `mac/_wynik/dist/Stwórz prezentację.app` i `mac/_wynik/Prezentacje na Maca.dmg`. Skrypt niczego nie kasuje.
Pliki: `stworz_mac.spec` (PyInstaller), `ikona_icns.py` (ikona z `src/ikona.ico`), `github-workflow-mac.yml` (idzie do
`.github/workflows/mac.yml`).

## Niesprawdzone (nikt nie uruchomił tego na Macu)

- cała budowa w GitHub Actions (runner `macos-14`, wersje akcji, instalacja pakietów, PyInstaller, DMG);
- start okna (WKWebView), wygląd interfejsu w trybie ciemnym macOS, rozmiar okna na małym ekranie;
- przeciąganie: pywebview 6.2.1 na macOS przepisuje pełną ścieżkę upuszczonego **pliku** (`pywebviewFullPath`). Dla
  upuszczonego **folderu** jego kod porównuje nazwę z nazwą folderu nadrzędnego i może pominąć ścieżkę; wtedy program
  pokaże komunikat z prośbą o użycie przycisku „Wybierz folder”;
- okno wyboru plików z filtrem „Wszystkie pliki” (pusta lista rozszerzeń w `NSOpenPanel`);
- schowek (`pbcopy`/`pbpaste`), otwieranie aplikacji Claude i linków `claude://`, Claude Code w Terminalu (zgoda na sterowanie);
- nazwy plików z polskimi literami zapisane przez macOS w innej postaci Unicode (NFD) mogą nie pasować do wzorców w nazwach
  kart i plików produktu;
- polecenia „dopracuj w AI” dla konwersji i dokumentów nadal wspominają narzędzia Windows (`render.ps1`, `verify.ps1`);
  ścieżka scenariusza (główna w 1.3) ich nie używa.
