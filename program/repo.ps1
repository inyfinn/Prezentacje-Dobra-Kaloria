# Repozytorium GitHub "Prezentacje - Dobra Kaloria": zebranie plików do osobnego folderu i paczka wydania.
#   repo.ps1            kopiuje źródła do $Repo (tylko dokłada i nadpisuje, niczego nie kasuje)
#   repo.ps1 -Zip       dodatkowo pakuje gotowy program do WORK\dist\wydanie\<nazwa>.zip
# Repo leży poza folderem programu, żeby katalog .git nie trafiał na dyski wspólne.
param([string]$Repo = (Join-Path $HOME "repos\Prezentacje-Dobra-Kaloria"), [switch]$Zip)
$ErrorActionPreference = "Stop"
$W = $PSScriptRoot
$R = Split-Path -Parent $W
$ver = (Get-Content -LiteralPath (Join-Path $W "wersja.txt") -Raw).Trim()
"repo: $Repo"
"program: $R (wersja $ver)"
if (-not $Repo -or $Repo.Length -lt 10 -or $Repo -match '^[A-Za-z]:\\?$') { throw "Podejrzana sciezka repo: '$Repo'" }
New-Item -ItemType Directory -Force $Repo | Out-Null
function Mirror($src, $dst, $xd, $xf) {
    $a = @($src, $dst, "/E", "/R:2", "/W:1", "/NFL", "/NDL", "/NJH", "/NJS", "/NP")
    if ($xd) { $a += "/XD"; $a += $xd }
    if ($xf) { $a += "/XF"; $a += $xf }
    robocopy @a | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy $src -> $dst kod $LASTEXITCODE" }
}
Mirror (Join-Path $W "src") (Join-Path $Repo "program\src") @("__pycache__", ".cache") @("*.pyc")
foreach ($f in "build.ps1", "wydaj.ps1", "repo.ps1", "zip_release.py", "ikona.py", "powitanie.py", "stworz_gui.spec", "stworz_cli.spec", "wersja.txt") {
    Copy-Item -LiteralPath (Join-Path $W $f) -Destination (Join-Path $Repo "program\$f") -Force
}
New-Item -ItemType Directory -Force (Join-Path $Repo "program\testy") | Out-Null
foreach ($f in "e2e_gui.py", "start_test.ps1", "launcher_test.ps1", "test_u_innych.ps1") {
    $p = Join-Path $W "logs\$f"
    if (Test-Path -LiteralPath $p) { Copy-Item -LiteralPath $p -Destination (Join-Path $Repo "program\testy\$f") -Force }
}
$ds = Join-Path $HOME ".claude\skills\ds-dobra-kaloria"
if (Test-Path -LiteralPath $ds) { Mirror $ds (Join-Path $Repo "design-system") @("__pycache__", ".playwright-cli") @("*.pyc") }
New-Item -ItemType Directory -Force (Join-Path $Repo "dla-uzytkownika") | Out-Null
foreach ($f in "AGENTS.md", "CLAUDE.md", "GEMINI.md", "CZYTAJ - jak zrobić prezentację.txt", "DK - szablon prezentacji.pptx") {
    Copy-Item -LiteralPath (Join-Path $R $f) -Destination (Join-Path $Repo "dla-uzytkownika\$f") -Force
}
"zebrano pliki: " + (Get-ChildItem -LiteralPath $Repo -Recurse -File | Where-Object { $_.FullName -notlike "*\.git\*" } | Measure-Object).Count

if ($Zip) {
    $out = Join-Path $W "dist\wydanie"
    New-Item -ItemType Directory -Force $out | Out-Null
    $zipPath = Join-Path $out "Stworz-prezentacje-$ver-Windows.zip"
    if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Confirm:$false }   # pojedynczy plik z tej budowy
    # Python zipfile: flaga UTF-8 w nazwach (Eksplorator inaczej psuje polskie litery)
    python (Join-Path $W "zip_release.py") $R $zipPath
    if ($LASTEXITCODE -ne 0) { throw "zip_release.py kod $LASTEXITCODE" }
}
exit 0
