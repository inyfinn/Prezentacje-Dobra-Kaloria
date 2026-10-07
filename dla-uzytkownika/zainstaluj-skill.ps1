# Instalacja skilla /prezentacje (Dobra Kaloria) dla agenta AI - kopiowanie bez kasowania.
#   zainstaluj-skill.ps1 [-Cel <katalog skilla>] [-DryRun]
#   (bez parametrow)  -> %USERPROFILE%\.claude\skills\prezentacje   (Claude Code / Claude Desktop / Cowork)
#   -Cel "%USERPROFILE%\.cursor\skills\prezentacje"   Cursor / Grok w Cursorze
#   -Cel "%USERPROFILE%\.codex\skills\prezentacje"    Codex (ChatGPT)
#   -Cel "%USERPROFILE%\.gemini\skills\prezentacje"   Gemini CLI
#   -DryRun   tylko pokaz, co zostanie zrobione (nic nie zapisuje)
# Zrodlo: skill-prezentacje\ obok tego pliku (zapas: pliki programu\app\skill\).
# Gdy katalog docelowy juz istnieje, jest PRZENOSZONY (nie kasowany) do <rodzic>\_poprzednie\<nazwa>-<data_godzina>.
# Wyjscie: kod 0 = zainstalowano (albo DryRun), kod 1 = blad (komunikat po "BLAD:").
param([string]$Cel = "", [switch]$DryRun)
$ErrorActionPreference = "Stop"
$R = $PSScriptRoot

function Blad($t) { Write-Host "BLAD: $t"; exit 1 }
# pliki skilla po odfiltrowaniu tego, czego nie kopiujemy (.cache, examples, __pycache__, *.pyc)
function Pliki($d) {
    $p = $d.TrimEnd('\').Length + 1
    @(Get-ChildItem -LiteralPath $d -Recurse -File -Force | Where-Object {
        $_.Extension -ne ".pyc" -and ($_.FullName.Substring($p) -notmatch '(^|\\)(\.cache|examples|__pycache__)\\')
    })
}

# 1. zrodlo
$zrodlo = Join-Path $R "skill-prezentacje"
if (-not (Test-Path -LiteralPath (Join-Path $zrodlo "SKILL.md"))) { $zrodlo = Join-Path $R "pliki programu\app\skill" }
if (-not (Test-Path -LiteralPath (Join-Path $zrodlo "SKILL.md"))) {
    Blad "nie znaleziono skilla (ani 'skill-prezentacje\SKILL.md', ani 'pliki programu\app\skill\SKILL.md') obok $R"
}
$zrodlo = [IO.Path]::GetFullPath($zrodlo).TrimEnd('\')

# 2. cel (domyslnie Claude Code); %ZMIENNE% rozwijamy sami - agent w PowerShellu moze podac je doslownie
if ([string]::IsNullOrWhiteSpace($Cel)) { $Cel = Join-Path $env:USERPROFILE ".claude\skills\prezentacje" }
$Cel = [Environment]::ExpandEnvironmentVariables($Cel.Trim().Trim('"'))
if (-not [IO.Path]::IsPathRooted($Cel) -or $Cel -match '^[A-Za-z]:\\?$') { Blad "-Cel musi byc pelna sciezka do katalogu skilla (dostalem: '$Cel')" }
$Cel = [IO.Path]::GetFullPath($Cel).TrimEnd('\')
Write-Host "zrodlo: $zrodlo"
Write-Host "cel:    $Cel"
if ([IO.Path]::GetPathRoot($Cel).TrimEnd('\') -eq $Cel) { Blad "cel to korzen dysku - odmawiam" }
if ($Cel -eq $env:USERPROFILE.TrimEnd('\')) { Blad "cel to katalog domowy - odmawiam" }
$oc = [StringComparison]::OrdinalIgnoreCase
if (($Cel + "\").StartsWith($zrodlo + "\", $oc) -or ($zrodlo + "\").StartsWith($Cel + "\", $oc)) { Blad "cel i zrodlo nie moga sie zawierac nawzajem" }

# 3. plan
$n = (Pliki $zrodlo).Count
$stary = Test-Path -LiteralPath $Cel
$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$old = Join-Path (Join-Path (Split-Path -Parent $Cel) "_poprzednie") ((Split-Path -Leaf $Cel) + "-" + $stamp)
if ($DryRun) {
    Write-Host "[DryRun] plikow do skopiowania: $n"
    if ($stary) { Write-Host "[DryRun] istniejacy cel zostalby PRZENIESIONY do: $old" } else { Write-Host "[DryRun] cel nie istnieje - kopia od zera" }
    Write-Host "[DryRun] nic nie zapisano. Bez -DryRun zainstaluje skill."
    exit 0
}

# 4. poprzednia wersja -> _poprzednie (Move-Item, nie Remove)
if ($stary) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $old) | Out-Null
    Move-Item -LiteralPath $Cel -Destination $old
    if (Test-Path -LiteralPath $Cel) { Blad "nie udalo sie przeniesc starego '$Cel' - przerywam" }
    Write-Host "poprzednia wersja przeniesiona do: $old"
}

# 5. kopia (robocopy kody 0-7 = sukces, >=8 = blad; bez /MIR i /PURGE)
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Cel) | Out-Null
robocopy $zrodlo $Cel /E /R:2 /W:2 /XD .cache examples __pycache__ /XF *.pyc /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Blad "robocopy zakonczyl sie kodem $LASTEXITCODE" }

# 6. kontrola i raport
$ok = Test-Path -LiteralPath (Join-Path $Cel "SKILL.md")
$m = (Pliki $Cel).Count
Write-Host ""
Write-Host "Zainstalowano skill /prezentacje: $m plikow (zrodlo: $n) -> $Cel"
Write-Host "Sprawdz: Test-Path `"$Cel\SKILL.md`"   (teraz: $ok)"
Write-Host "Agent zobaczy skill po wczytaniu go z tej sciezki albo po nowej sesji/przeladowaniu agenta."
if (-not $ok -or $m -ne $n) { Blad "kontrola nie przeszla (SKILL.md: $ok, plikow $m z $n)" }
exit 0
