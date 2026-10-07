# Wydanie programu "Stwórz prezentację" na dyski wspólne - samo kopiowanie (bez kasowania, bez kompilacji).
#   wydaj.ps1 [-Cele <ścieżka>,<ścieżka>]
# Kopiuje: "pliki programu\", "skill-prezentacje\", "Stwórz prezentację.exe", instrukcje dla AI (AGENTS/CLAUDE/GEMINI/GROK.md),
# instalator skilla (zainstaluj-skill.ps1/.cmd), szablon PPTX. WORK\ zostaje tylko na D:.
param([string[]]$Cele = @(
    "M:\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\— SZABLON AI - skrypt",
    "G:\Sprzedaż Marketing\PREZENTACJE\— SZABLON\— SZABLON AI - skrypt"))
$R = Split-Path -Parent $PSScriptRoot
$src = Join-Path $R "pliki programu"
$ver = (Get-Content -LiteralPath (Join-Path $src "wersja.txt") -Raw).Trim()
foreach ($dst in $Cele) {
    if (-not (Test-Path -LiteralPath $dst)) { "POMIJAM (brak folderu): $dst"; continue }
    robocopy $src (Join-Path $dst "pliki programu") /E /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
    $rc = $LASTEXITCODE   # robocopy: 0-7 = sukces (1 = skopiowano), >=8 = błąd
    # kopia skilla /prezentacje dla agentów AI (zainstaluj-skill.ps1 instaluje z niej) - bez /MIR
    $sk = Join-Path $R "skill-prezentacje"
    if (Test-Path -LiteralPath $sk) {
        robocopy $sk (Join-Path $dst "skill-prezentacje") /E /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
        $rcSk = $LASTEXITCODE
        "  skill-prezentacje -> $dst (robocopy rc=$rcSk)"
    }
    # kopia identyfikacji wizualnej (KROK 0b polecenia dla AI) - bez /MIR
    $ds = Join-Path $R "skill-ds-dobra-kaloria"
    if (Test-Path -LiteralPath $ds) {
        robocopy $ds (Join-Path $dst "skill-ds-dobra-kaloria") /E /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
        "  skill-ds-dobra-kaloria -> $dst (robocopy rc=$LASTEXITCODE)"
    }
    foreach ($f in "Stwórz prezentację.exe", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "GROK.md", "zainstaluj-skill.ps1", "zainstaluj-skill.cmd", "CZYTAJ - jak zrobić prezentację.txt", "DK - szablon prezentacji.pptx") {
        $p = Join-Path $R $f
        if (Test-Path -LiteralPath $p) { Copy-Item -LiteralPath $p -Destination $dst -Force }
    }
    $n = (Get-ChildItem -LiteralPath (Join-Path $dst "pliki programu") -Recurse -File | Measure-Object).Count
    "wydano $ver -> $dst  (robocopy rc=$rc, plikow w 'pliki programu': $n)"
}
exit 0
