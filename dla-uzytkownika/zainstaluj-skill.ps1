# Instalacja skilli dla agenta AI (Dobra Kaloria): /prezentacje i /ui-ux-pro-max - kopiowanie bez kasowania.
#   zainstaluj-skill.ps1 [-Cel <katalog skilli>] [-DryRun]
#   (bez parametrow)  -> %USERPROFILE%\.claude\skills\<nazwa>          (Claude Code / Claude Desktop)
#   -Cel "%USERPROFILE%\.codex\skills"     Codex (ChatGPT)
#   -Cel "%USERPROFILE%\.gemini\skills"    Gemini CLI
#   -Cel "%USERPROFILE%\.cursor\skills"    Cursor
#   Stary zapis "-Cel ...\skills\prezentacje" tez dziala (bierze katalog nadrzedny).
#   -DryRun   tylko pokaz, co zostanie zrobione (nic nie zapisuje)
# Zrodla: kazdy folder skille\<nazwa>\ z SKILL.md obok tego pliku (paczka zip);
#         bez folderu skille\ - skill-prezentacje\ (zapas: pliki programu\app\skill\) jako "prezentacje".
# Skill juz zainstalowany i taki sam -> pomija. Lekka wersja z paczki (PACZKA-LEKKA.txt) nie nadpisuje pelnej.
# Inny (starszy) -> stary PRZENOSI (nie kasuje) do <katalog skilli>\_poprzednie\<nazwa>-<data_godzina>, potem kopiuje nowy.
# Wyjscie: kod 0 = gotowe (albo DryRun), kod 1 = blad (komunikat po "BLAD:").
# Zrodlo tego pliku: WORK\instrukcje\ (generuj.py wklada go do paczki).
param([string]$Cel = "", [switch]$DryRun)
$ErrorActionPreference = "Stop"
$R = $PSScriptRoot

function Blad($t) { Write-Host "BLAD: $t"; exit 1 }
# pliki skilla bez .cache, examples, __pycache__, *.pyc
function Pliki($d) {
    $p = $d.TrimEnd('\').Length + 1
    @(Get-ChildItem -LiteralPath $d -Recurse -File -Force | Where-Object {
        $_.Extension -ne ".pyc" -and ($_.FullName.Substring($p) -notmatch '(^|\\)(\.cache|examples|__pycache__)\\')
    })
}
function Odcisk($d) {  # liczba plikow + skrot SKILL.md: wystarczy, by odroznic wersje
    "{0}|{1}" -f (Pliki $d).Count, (Get-FileHash -LiteralPath (Join-Path $d "SKILL.md") -Algorithm SHA256).Hash
}

# 1. zrodla
$zrodla = @{}
$sk = Join-Path $R "skille"
if (Test-Path -LiteralPath $sk) {
    foreach ($d in Get-ChildItem -LiteralPath $sk -Directory) {
        if (Test-Path -LiteralPath (Join-Path $d.FullName "SKILL.md")) { $zrodla[$d.Name] = $d.FullName }
    }
}
if ($zrodla.Count -eq 0) {
    foreach ($d in (Join-Path $R "skill-prezentacje"), (Join-Path $R "pliki programu\app\skill")) {
        if (Test-Path -LiteralPath (Join-Path $d "SKILL.md")) { $zrodla["prezentacje"] = $d; break }
    }
}
if ($zrodla.Count -eq 0) { Blad "nie znaleziono skilli (ani 'skille\<nazwa>\SKILL.md', ani 'skill-prezentacje\SKILL.md') obok $R" }

# 2. katalog skilli (domyslnie Claude Code); %ZMIENNE% rozwijamy sami
if ([string]::IsNullOrWhiteSpace($Cel)) { $Cel = Join-Path $env:USERPROFILE ".claude\skills" }
$Cel = [Environment]::ExpandEnvironmentVariables($Cel.Trim().Trim('"'))
if (-not [IO.Path]::IsPathRooted($Cel) -or $Cel -match '^[A-Za-z]:\\?$') { Blad "-Cel musi byc pelna sciezka do katalogu skilli (dostalem: '$Cel')" }
$Kat = [IO.Path]::GetFullPath($Cel).TrimEnd('\')
if ($zrodla.ContainsKey((Split-Path -Leaf $Kat))) { $Kat = Split-Path -Parent $Kat }  # stary zapis ...\skills\prezentacje
if ([IO.Path]::GetPathRoot($Kat).TrimEnd('\') -eq $Kat) { Blad "katalog skilli to korzen dysku - odmawiam" }
if ($Kat -eq $env:USERPROFILE.TrimEnd('\')) { Blad "katalog skilli to katalog domowy - odmawiam" }
Write-Host "katalog skilli: $Kat"
$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$oc = [StringComparison]::OrdinalIgnoreCase

# 3. kazdy skill: pomin aktualny, stary przenies, skopiuj nowy
foreach ($nazwa in ($zrodla.Keys | Sort-Object)) {
    $zr = [IO.Path]::GetFullPath($zrodla[$nazwa]).TrimEnd('\')
    $cel1 = Join-Path $Kat $nazwa
    if (($cel1 + "\").StartsWith($zr + "\", $oc) -or ($zr + "\").StartsWith($cel1 + "\", $oc)) { Blad "cel i zrodlo '$nazwa' zawieraja sie nawzajem" }
    $n = (Pliki $zr).Count
    $jest = Test-Path -LiteralPath (Join-Path $cel1 "SKILL.md")
    if ($jest -and (Odcisk $cel1) -eq (Odcisk $zr)) { Write-Host "[$nazwa] juz zainstalowany i aktualny - pomijam ($cel1)"; continue }
    # lekka wersja z paczki (PACZKA-LEKKA.txt) nie nadpisuje pelnej instalacji
    if ($jest -and (Test-Path -LiteralPath (Join-Path $zr "PACZKA-LEKKA.txt")) -and -not (Test-Path -LiteralPath (Join-Path $cel1 "PACZKA-LEKKA.txt"))) {
        Write-Host "[$nazwa] jest juz pelna wersja - nie nadpisuje jej lekka z paczki ($cel1)"; continue
    }
    $old = Join-Path (Join-Path $Kat "_poprzednie") ("$nazwa-$stamp")
    if ($DryRun) {
        if (Test-Path -LiteralPath $cel1) { Write-Host "[DryRun][$nazwa] inna wersja - zostalaby przeniesiona do $old, potem kopia $n plikow" }
        else { Write-Host "[DryRun][$nazwa] brak - kopia $n plikow do $cel1" }
        continue
    }
    if (Test-Path -LiteralPath $cel1) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $old) | Out-Null
        Move-Item -LiteralPath $cel1 -Destination $old
        if (Test-Path -LiteralPath $cel1) { Blad "nie udalo sie przeniesc starego '$cel1' - przerywam" }
        Write-Host "[$nazwa] poprzednia wersja przeniesiona do: $old"
    }
    # Copy-Item plik po pliku, nie robocopy: robocopy wolany z narzedzia PowerShell agenta bywa ucinany w polowie
    foreach ($f in (Pliki $zr)) {
        $d = Join-Path $cel1 $f.FullName.Substring($zr.Length + 1)
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $d) | Out-Null
        Copy-Item -LiteralPath $f.FullName -Destination $d -Force
    }
    $m = (Pliki $cel1).Count
    if (-not (Test-Path -LiteralPath (Join-Path $cel1 "SKILL.md")) -or $m -ne $n) { Blad "[$nazwa] kontrola nie przeszla (plikow $m z $n)" }
    Write-Host "[$nazwa] zainstalowano: $m plikow -> $cel1"
}
if ($DryRun) { Write-Host "[DryRun] nic nie zapisano." }
Write-Host "Agent zobaczy skille po nowej sesji albo po wczytaniu SKILL.md z tych katalogow."
exit 0
