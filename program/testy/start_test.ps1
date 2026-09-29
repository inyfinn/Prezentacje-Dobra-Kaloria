# Test startu tak, jak robi to użytkownik: uruchamia plik startowy (bez portu debugowania) i czeka na GOTOWOŚĆ programu
# (wpis "most JS<->Python gotowy" w logu + okno odpowiada), a nie tylko na pojawienie się okna. Lekcja 29.09: okno
# widoczne != program gotowy (user dostał "brak odpowiedzi").
#   start_test.ps1 -Exe "<...>\Stwórz prezentację.exe" [-Razy 5] [-Limit 90]
param([Parameter(Mandatory)][string]$Exe, [int]$Razy = 5, [int]$Limit = 90)
$dir = Split-Path -Parent $Exe
$log = Join-Path $env:LOCALAPPDATA "Dobra Kaloria\Stworz prezentacje\logi\ostatni.log"
$ok = 0
for ($k = 1; $k -le $Razy; $k++) {
    $n0 = if (Test-Path -LiteralPath $log) { @(Get-Content -LiteralPath $log -Encoding UTF8).Count } else { 0 }
    $sw = [Diagnostics.Stopwatch]::StartNew()
    Start-Process -FilePath $Exe | Out-Null
    $tWin = $null; $tLoad = $null; $tReady = $null; $resp = $null; $prog = $null
    while ($sw.Elapsed.TotalSeconds -lt $Limit -and -not $tReady) {
        Start-Sleep -Milliseconds 300
        if (-not $prog) { $prog = Get-Process -Name program -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$dir\*" } | Select-Object -First 1 }
        if ($prog) {
            $prog.Refresh()
            if (-not $tWin -and $prog.MainWindowHandle -ne [IntPtr]::Zero) { $tWin = $sw.Elapsed.TotalSeconds }
        }
        $new = @(Get-Content -LiteralPath $log -Encoding UTF8 -ErrorAction SilentlyContinue | Select-Object -Skip $n0)
        if (-not $tLoad -and ($new -match "okno za")) { $tLoad = $sw.Elapsed.TotalSeconds }
        if (-not $tReady -and ($new -match "most JS")) { $tReady = $sw.Elapsed.TotalSeconds }
    }
    Start-Sleep -Milliseconds 800
    if ($prog) { $prog.Refresh(); $resp = $prog.Responding }
    $wynik = if ($tReady -and $resp) { $ok++; "OK" } else { "BLAD" }
    "start {0}: {1}  okno po {2:N1} s, zaladowane po {3:N1} s, GOTOWE po {4:N1} s, odpowiada: {5}" -f $k, $wynik, $tWin, $tLoad, $tReady, $resp
    if ($prog) {
        $prog.CloseMainWindow() | Out-Null
        if (-not $prog.WaitForExit(5000)) { Stop-Process -Id $prog.Id -Force -Confirm:$false }
    }
    Get-Process -Name "Stwórz prezentację" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$dir\*" } | Stop-Process -Force -Confirm:$false
    Start-Sleep -Seconds 2
}
"WYNIK: $ok / $Razy startow gotowych"
