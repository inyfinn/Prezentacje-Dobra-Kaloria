# Test "czy zadziała u innych" - odtwarza warunki komputera handlowca na tym komputerze (czystej maszyny tu nie ma):
#   1. zip wydania z oznaczeniem "pobrany z internetu" (Zone.Identifier=3), rozpakowany jak w Eksploratorze
#   2. start z okrojonym środowiskiem: PATH tylko Windows, bez zmiennych Pythona
#   3. start z dysków sieciowych: M: (\\192.168.82.36 = strefa Internet) i G: (\\kubara.net = Intranet)
#   4. spis bibliotek wczytanych SPOZA folderu programu i spoza Windows (wszystko inne = zależność od tego komputera)
#   test_u_innych.ps1 -Zip <zip wydania> [-Sieci "M:\...\— SZABLON AI - skrypt","G:\..."]
param([Parameter(Mandatory)][string]$Zip, [string[]]$Sieci = @(), [int]$Limit = 90)
$log = Join-Path $env:LOCALAPPDATA "Dobra Kaloria\Stworz prezentacje\logi\ostatni.log"
# LOCALAPPDATA ma długą ścieżkę; TEMP bywa krótka (KRZYSZ~1.WIE), a procesy zgłaszają długą - inaczej okna zostają otwarte
$work = Join-Path $env:LOCALAPPDATA ("Temp\dk-test-u-innych\" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Force $work | Out-Null
$wynik = @()

function Start-Clean($exe) {
    $psi = New-Object Diagnostics.ProcessStartInfo $exe
    $psi.UseShellExecute = $false
    $psi.WorkingDirectory = Split-Path -Parent $exe
    foreach ($k in @($psi.EnvironmentVariables.Keys)) { if ($k -match '^(PYTHON|VIRTUAL_ENV|CONDA|PYINSTALLER)') { $psi.EnvironmentVariables.Remove($k) } }
    $psi.EnvironmentVariables["PATH"] = "$env:WINDIR\System32;$env:WINDIR;$env:WINDIR\System32\WindowsPowerShell\v1.0"
    [Diagnostics.Process]::Start($psi) | Out-Null
}

function Test-Start($root, $nazwa, [switch]$Moduly) {
    $exe = Join-Path $root "Stwórz prezentację.exe"
    $dir = Join-Path $root "pliki programu"
    $n0 = if (Test-Path -LiteralPath $log) { @(Get-Content -LiteralPath $log -Encoding UTF8).Count } else { 0 }
    $sw = [Diagnostics.Stopwatch]::StartNew()
    Start-Clean $exe
    $ready = $null; $blad = $null; $prog = $null
    while ($sw.Elapsed.TotalSeconds -lt $Limit -and -not $ready -and -not $blad) {
        Start-Sleep -Milliseconds 400
        if (-not $prog) { $prog = Get-Process -Name program -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$dir\*" } | Select-Object -First 1 }
        if ($prog) { $prog.Refresh(); if ($prog.MainWindowTitle -like "*exception*" -or $prog.MainWindowTitle -like "*error*") { $blad = $prog.MainWindowTitle } }
        $new = @(Get-Content -LiteralPath $log -Encoding UTF8 -ErrorAction SilentlyContinue | Select-Object -Skip $n0)
        if ($new -match "most JS") { $ready = $sw.Elapsed.TotalSeconds }
    }
    $obce = @()
    if ($prog -and $ready -and $Moduly) {
        Start-Sleep -Seconds 2
        $prog.Refresh()
        $obce = @($prog.Modules | Where-Object { $_.FileName -notlike "$dir\*" -and $_.FileName -notlike "$env:WINDIR\*" } | ForEach-Object { $_.FileName })
    }
    if ($prog) { $prog.Refresh(); if (-not $prog.HasExited) { $prog.CloseMainWindow() | Out-Null; if (-not $prog.WaitForExit(5000)) { Stop-Process -Id $prog.Id -Force -Confirm:$false } } }
    Get-Process -Name program, "Stwórz prezentację" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$root\*" } | Stop-Process -Force -Confirm:$false
    $ok = [bool]$ready -and -not $blad
    $script:wynik += [pscustomobject]@{ Test = $nazwa; Wynik = $(if ($ok) { "OK" } else { "BLAD" }); Gotowe_s = $(if ($ready) { [math]::Round($ready, 1) } else { "-" }); Uwagi = $(if ($blad) { $blad } elseif (-not $ready) { "brak gotowosci w $Limit s" } else { "" }) }
    if ($Moduly) {
        "Biblioteki spoza folderu programu i spoza Windows ($nazwa):"
        if ($obce.Count) { $obce | Sort-Object -Unique | ForEach-Object { "   $_" } } else { "   (brak)" }
    }
    Start-Sleep -Seconds 2
}

# 1. zip z internetu, rozpakowany przez powłokę Windows (tak jak zrobi to człowiek w Eksploratorze)
$z = Join-Path $work (Split-Path -Leaf $Zip)
Copy-Item -LiteralPath $Zip -Destination $z
Set-Content -LiteralPath $z -Stream Zone.Identifier -Value "[ZoneTransfer]`r`nZoneId=3`r`nHostUrl=https://github.com/" -Encoding ASCII
$dst = Join-Path $work "rozpakowany"
New-Item -ItemType Directory -Force $dst | Out-Null
$sh = New-Object -ComObject Shell.Application
$sh.NameSpace($dst).CopyHere($sh.NameSpace($z).Items(), 0x14)
for ($i = 0; $i -lt 300 -and -not (Test-Path -LiteralPath (Join-Path $dst "Stwórz prezentację.exe")); $i++) { Start-Sleep -Milliseconds 500 }
Start-Sleep -Seconds 3
$dll = Join-Path $dst "pliki programu\pythonnet\runtime\Python.Runtime.dll"
$motw = [bool](Get-Item -LiteralPath $dll -Stream Zone.Identifier -ErrorAction SilentlyContinue)
"Rozpakowano do $dst (pliki oznaczone jako pobrane z internetu: $motw)"
Test-Start $dst "zip z internetu, czyste srodowisko" -Moduly

# 2. dyski sieciowe
foreach ($s in $Sieci) { Test-Start $s ("dysk sieciowy " + (Split-Path -Qualifier $s)) }

""
$wynik | Format-Table -AutoSize | Out-String
"WebView2 na tym komputerze: " + (Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv
"WYNIK: {0} / {1} OK" -f @($wynik | Where-Object Wynik -eq "OK").Count, $wynik.Count
