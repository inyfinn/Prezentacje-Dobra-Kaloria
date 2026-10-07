# Budowa programu "Stwórz prezentację" (portable, bez instalacji).
#   build.ps1 [-Wydaj] [-Bump] [-BezSkilla]
#   -Bump      podbij wersję (patch) w WORK\wersja.txt
#   -BezSkilla nie odświeżaj kopii skilla z ~\.claude\skills\prezentacje
#   -Wydaj     po budowie skopiuj program na M: i G: (wydaj.ps1 - kopiowanie bez kasowania)
# Wynik w folderze nadrzędnym (— SZABLON AI - skrypt):
#   Stwórz prezentację.exe   maleńki plik startowy (launcher.cs): plansza "Uruchamiam…" + start programu
#   pliki programu\          program.exe (okno), stworz-cli.exe (dla AI), biblioteki, app\ (ui, skill)
# Stara wersja "pliki programu" jest PRZENOSZONA do WORK\poprzednie\<data_godzina> (nigdy kasowana).
param([switch]$Wydaj, [switch]$Bump, [switch]$BezSkilla)
$ErrorActionPreference = "Stop"
$W = $PSScriptRoot
$R = Split-Path -Parent $W
$SRC = Join-Path $W "src"
$logs = Join-Path $W "logs"
$log = Join-Path $logs "build.log"
New-Item -ItemType Directory -Force $logs | Out-Null
function Log($t) { $l = "{0} {1}" -f (Get-Date -Format "HH:mm:ss"), $t; $l | Tee-Object -FilePath $log -Append }
function Run($exe, $argList, $name) {
    # Start-Process zamiast "2>&1": PowerShell 5.1 zamieniłby logi na stderr w błąd i przerwał budowę
    $lg = Join-Path $logs "$name.log"
    $pr = Start-Process -FilePath $exe -ArgumentList $argList -Wait -NoNewWindow -PassThru -RedirectStandardOutput "$lg.out" -RedirectStandardError $lg
    if ($pr.ExitCode -ne 0) { throw "$name nie powiodl sie (kod $($pr.ExitCode), patrz $lg i $lg.out)" }
}

# 0. wersja
$verFile = Join-Path $W "wersja.txt"
$ver = (Get-Content $verFile -Raw).Trim()
# licznik dziesiętny z przeniesieniem: 1.0.9 -> 1.1.0 (nigdy 1.0.10), tak samo jak w DAM
if ($Bump) { $p = [int[]]$ver.Split("."); $p[2]++; if ($p[2] -gt 9) { $p[2] = 0; $p[1]++ }; if ($p[1] -gt 9) { $p[1] = 0; $p[0]++ }; $ver = $p -join "."; Set-Content -Path $verFile -Value $ver -Encoding ASCII }
Log "=== build $ver ==="

# 1. świeża kopia skilla (silnik) - bez .cache, examples, __pycache__
if (-not $BezSkilla) {
    $SK = Join-Path $HOME ".claude\skills\prezentacje"
    robocopy $SK (Join-Path $SRC "skill") /E /XD .cache examples __pycache__ /XF *.pyc /NFL /NDL /NJH /NJS /NP | Out-Null
    Log "skill odswiezony z $SK"
    # 1a. kopia skilla w korzeniu folderu programu (skill-prezentacje\) - z niej zainstaluj-skill.ps1 instaluje skill agentom AI.
    #     Bez /MIR i /PURGE (zakaz kasowania): plik usuniety ze skilla zostaje w kopii az do reczneho przeniesienia.
    robocopy $SK (Join-Path $R "skill-prezentacje") /E /XD .cache examples __pycache__ /XF *.pyc /NFL /NDL /NJH /NJS /NP | Out-Null
    Log "skill-prezentacje odswiezony w $R"
}
# 1b. tokeny design systemu (kolory, odstępy, promienie) - jedno źródło: skill ds-dobra-kaloria
$DS = Join-Path $HOME ".claude\skills\ds-dobra-kaloria\tokens\tokens.css"
if (Test-Path -LiteralPath $DS) {
    Copy-Item -LiteralPath $DS -Destination (Join-Path $SRC "ui\tokens.css") -Force
    Log "tokens.css odswiezony z $DS"
} else { Log "design system niedostepny - zostaje tokens.css z src\ui" }
# 1c. identyfikacja wizualna dla agentów AI (KROK 0b polecenia): kopia dokumentów i tokenów skilla ds-dobra-kaloria
#     obok programu (skill-ds-dobra-kaloria\), bez assets/preview/scripts (ok. 0,5 MB). Bez /MIR i /PURGE.
$DSK = Join-Path $HOME ".claude\skills\ds-dobra-kaloria"
if (Test-Path -LiteralPath $DSK) {
    robocopy $DSK (Join-Path $R "skill-ds-dobra-kaloria") /E /XD assets preview scripts themes __pycache__ .cache /XF *.pyc /NFL /NDL /NJH /NJS /NP | Out-Null
    Log "skill-ds-dobra-kaloria odswiezony z $DSK"
}
# 2. ikona i plansza startowa
python (Join-Path $W "ikona.py") | Out-Null
python (Join-Path $W "powitanie.py") | Out-Null
# 2b. PyInstaller nie przebudowuje exe po samej zmianie ikony/zasobów - odkładamy jego pliki pośrednie (nigdy nie kasujemy)
$aside = Join-Path (Join-Path $W "poprzednie") ("_build-cache-" + (Get-Date -Format "yyyy-MM-dd_HHmmss"))
foreach ($n in "stworz_gui", "stworz_cli") {
    $bd = Join-Path (Join-Path $W "build") $n
    if (Test-Path -LiteralPath $bd) {
        foreach ($f in @(Get-ChildItem -LiteralPath $bd -Filter "EXE-*.toc" -File)) {
            New-Item -ItemType Directory -Force (Join-Path $aside $n) | Out-Null
            Move-Item -LiteralPath $f.FullName -Destination (Join-Path $aside $n)
        }
    }
}
# 3. PyInstaller: okno (program.exe) + konsola (stworz-cli.exe), oba z zawartością obok siebie
$dist = Join-Path $W "dist"; $work = Join-Path $W "build"
foreach ($spec in "stworz_gui", "stworz_cli") {
    Log "pyinstaller $spec"
    Run "python" @("-m", "PyInstaller", "--noconfirm", "--distpath", "`"$dist`"", "--workpath", "`"$work`"", "`"$(Join-Path $W "$spec.spec")`"") "pyinstaller-$spec"
}
# 4. plik startowy (C#) - kompilator csc jest w każdym Windows (.NET Framework 4)
$csc = Join-Path $env:WINDIR "Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$lexe = Join-Path $work "launcher.exe"
Run $csc @("/nologo", "/target:winexe", "/optimize+", "/codepage:65001", "/win32icon:`"$(Join-Path $SRC 'ikona.ico')`"", "/out:`"$lexe`"", "/reference:System.Windows.Forms.dll", "/reference:System.Drawing.dll", "`"$(Join-Path $SRC 'launcher\launcher.cs')`"") "csc-launcher"
# 5. złożenie
$new = Join-Path $dist "program"
Copy-Item -LiteralPath (Join-Path $dist "stworz-cli\stworz-cli.exe") -Destination $new -Force
Set-Content -Path (Join-Path $new "wersja.txt") -Value $ver -Encoding ASCII
# .NET Framework odmawia wczytania Python.Runtime.dll (okno programu), gdy program stoi na dysku sieciowym
# adresowanym przez IP (strefa Internet) albo jest rozpakowany z zipa pobranego z internetu (30.09, błąd z M:)
foreach ($e in "program.exe", "stworz-cli.exe") {
    Copy-Item -LiteralPath (Join-Path $SRC "app\program.exe.config") -Destination (Join-Path $new "$e.config") -Force
}
$target = Join-Path $R "pliki programu"
$running = @(Get-Process -Name program, stworz-cli -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$target\*" })
if ($running.Count -gt 0) { throw "Program jest uruchomiony z '$target' (procesy: $($running.Id -join ', ')). Zamknij okno i uruchom budowe ponownie." }
if (Test-Path -LiteralPath $target) {
    $old = Join-Path (Join-Path $W "poprzednie") (Get-Date -Format "yyyy-MM-dd_HHmmss")
    New-Item -ItemType Directory -Force $old | Out-Null
    Move-Item -LiteralPath $target -Destination (Join-Path $old "pliki programu")
    if (Test-Path -LiteralPath $target) { throw "Stary folder 'pliki programu' nadal istnieje - przerywam" }
    Log "stara wersja przeniesiona do $old"
}
Move-Item -LiteralPath $new -Destination $target
Copy-Item -LiteralPath $lexe -Destination (Join-Path $R "Stwórz prezentację.exe") -Force
Log ("gotowe: {0}  ({1:N0} MB, {2} plikow; plik startowy {3:N0} KB)" -f $R, ((Get-ChildItem -LiteralPath $target -Recurse -File | Measure-Object Length -Sum).Sum / 1MB), (Get-ChildItem -LiteralPath $target -Recurse -File).Count, ((Get-Item -LiteralPath (Join-Path $R "Stwórz prezentację.exe")).Length / 1KB))
# 6. test dymny wersji konsolowej (bez Select-Object -First: ucięty potok daje fałszywy kod wyjścia)
$smoke = @(& (Join-Path $target "stworz-cli.exe") --help)
Log "smoke: $($smoke[0]) (kod $LASTEXITCODE)"
# 7. wydanie na dyski wspólne
if ($Wydaj) { & (Join-Path $W "wydaj.ps1") | ForEach-Object { Log $_ } }
Log "OK $ver"
exit 0
