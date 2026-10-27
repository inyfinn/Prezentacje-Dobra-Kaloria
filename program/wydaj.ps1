# Wydanie programu "Stwórz prezentację" na dyski wspólne - samo kopiowanie (bez kasowania, bez kompilacji).
#   wydaj.ps1 [-Cele <ścieżka>,<ścieżka>]
# Układ na dysku wspólnym (od 1.3, ten sam co na D:; czysty wierzch):
#   <cel>\Prezentacje.exe                 plik startowy
#   <cel>\Prezentacje na Maca.dmg         obraz dla Maca (kopiowany, jeśli leży obok na D:)
#   <cel>\DK - paczka prezentacji dla AI.zip
#   <cel>\WORK\pliki programu\            program.exe, stworz-cli.exe, biblioteki, app\
#   <cel>\WORK\skill-prezentacje\, WORK\skill-ds-dobra-kaloria\                    kopie skilli dla agentów AI
#   <cel>\WORK\AGENTS.md, CLAUDE.md, GEMINI.md, GROK.md, PROMPT BEZ PROGRAMU.md, zainstaluj-skill.ps1/.cmd
# Do WORK na dysku wspólnym NIE trafiają: src, logs, poprzednie, build, dist, mac, instrukcje (to zostaje tylko na D:).
# Nic nie jest kasowane ani przenoszone: robocopy /E i Copy-Item, bez /MIR i /PURGE. STARYCH plików na dysku wspólnym (sprzed 1.3:
# "pliki programu\" i "Stwórz prezentację.exe" na wierzchu, skill-*, AGENTS.md itd. obok nich) skrypt nie rusza - zostają jako stara
# kopia, a stary plik startowy dalej uruchamia stary program. Opiekun przenosi je ręcznie (patrz ostrzeżenie na końcu wydania).
param([string[]]$Cele = @(
    "M:\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt",
    "G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\— SZABLON AI - skrypt"))
$W = $PSScriptRoot
$R = Split-Path -Parent $W
$src = Join-Path $W "pliki programu"
$ver = (Get-Content -LiteralPath (Join-Path $src "wersja.txt") -Raw).Trim()
foreach ($dst in $Cele) {
    if (-not (Test-Path -LiteralPath $dst)) { "POMIJAM (brak folderu): $dst"; continue }
    $dw = Join-Path $dst "WORK"
    New-Item -ItemType Directory -Force $dw | Out-Null
    robocopy $src (Join-Path $dw "pliki programu") /E /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
    $rc = $LASTEXITCODE   # robocopy: 0-7 = sukces (1 = skopiowano), >=8 = błąd
    # kopie skilli dla agentów AI (zainstaluj-skill.ps1 instaluje z pierwszej, KROK 0b polecenia czyta drugą) - bez /MIR
    foreach ($d in "skill-prezentacje", "skill-ds-dobra-kaloria") {
        $s = Join-Path $W $d
        if (Test-Path -LiteralPath $s) {
            robocopy $s (Join-Path $dw $d) /E /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
            "  $d -> $dw (robocopy rc=$LASTEXITCODE)"
        }
    }
    # instrukcje dla AI i instalator skilla: w WORK, obok skill-prezentacje i pliki programu
    foreach ($f in "AGENTS.md", "CLAUDE.md", "GEMINI.md", "GROK.md", "PROMPT BEZ PROGRAMU.md", "zainstaluj-skill.ps1", "zainstaluj-skill.cmd") {
        $p = Join-Path $W $f
        if (Test-Path -LiteralPath $p) { Copy-Item -LiteralPath $p -Destination $dw -Force }
    }
    # wierzch: plik startowy, obraz dla Maca i paczka dla AI
    foreach ($f in "Prezentacje.exe", "Prezentacje na Maca.dmg", "DK - paczka prezentacji dla AI.zip") {
        $p = Join-Path $R $f
        if (Test-Path -LiteralPath $p) { Copy-Item -LiteralPath $p -Destination $dst -Force } else { "  brak na D: (pomijam): $f" }
    }
    $n = (Get-ChildItem -LiteralPath (Join-Path $dw "pliki programu") -Recurse -File | Measure-Object).Count
    "wydano $ver -> $dst  (robocopy rc=$rc, plikow w 'WORK\pliki programu': $n)"
    # stare pliki sprzed 1.3 zostają nietknięte - tylko o nich mówimy
    $stare = @("pliki programu", "Stwórz prezentację.exe", "skill-prezentacje", "skill-ds-dobra-kaloria", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "GROK.md",
               "PROMPT BEZ PROGRAMU.md", "zainstaluj-skill.ps1", "zainstaluj-skill.cmd", "DK - szablon prezentacji - pełen.pptx", "plansze") |
        Where-Object { Test-Path -LiteralPath (Join-Path $dst $_) }
    if ($stare.Count -gt 0) { "  UWAGA: na wierzchu $dst zostały STARE pliki sprzed 1.3 (nie ruszam): " + ($stare -join ", ") + ". Stary 'Stwórz prezentację.exe' uruchamia starą wersję z 'pliki programu'. Przenieś je ręcznie do osobnego folderu, gdy nikt ich nie używa." }
}
exit 0
