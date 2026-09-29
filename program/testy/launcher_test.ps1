# Test pliku startowego: kiedy pojawia się plansza, kiedy okno programu, kiedy plansza znika. Zrzut SAMEJ planszy
# (PrintWindow po uchwycie okna - bez przechwytywania pulpitu). Na końcu zamyka uruchomiony program.
param([Parameter(Mandatory)][string]$Exe, [string]$Shot = "", [int]$Razy = 1)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public static class W32 {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr h, int i);
  public struct RECT { public int L, T, R, B; }
}
"@
$dir = Split-Path -Parent $Exe
for ($k = 1; $k -le $Razy; $k++) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $l = Start-Process -FilePath $Exe -PassThru
    $tSplash = $null; $tProg = $null; $tClosed = $null; $shotDone = $false; $title = ""; $top = ""
    while ($sw.Elapsed.TotalSeconds -lt 90 -and (-not $tClosed -or -not $tProg)) {
        Start-Sleep -Milliseconds 200
        $l.Refresh()
        if (-not $tSplash -and -not $l.HasExited -and $l.MainWindowHandle -ne [IntPtr]::Zero) {
            $tSplash = $sw.Elapsed.TotalSeconds
            $top = if (([W32]::GetWindowLong($l.MainWindowHandle, -20) -band 0x8) -ne 0) { "TAK" } else { "nie" }
        }
        if ($tSplash -and -not $shotDone -and $Shot -and -not $l.HasExited -and $sw.Elapsed.TotalSeconds -gt ($tSplash + 0.6)) {
            $r = New-Object W32+RECT; [W32]::GetWindowRect($l.MainWindowHandle, [ref]$r) | Out-Null
            $bmp = New-Object Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
            $g = [Drawing.Graphics]::FromImage($bmp); $hdc = $g.GetHdc()
            [W32]::PrintWindow($l.MainWindowHandle, $hdc, 2) | Out-Null
            $g.ReleaseHdc($hdc); $bmp.Save($Shot); $g.Dispose(); $bmp.Dispose(); $shotDone = $true
        }
        if (-not $tProg) {
            $p = Get-Process -Name program -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$dir\*" -and $_.MainWindowTitle } | Select-Object -First 1
            if ($p) { $tProg = $sw.Elapsed.TotalSeconds; $title = $p.MainWindowTitle }
        }
        if (-not $tClosed -and $l.HasExited) { $tClosed = $sw.Elapsed.TotalSeconds }
    }
    "start {0}: plansza po {1:N1} s (zawsze na wierzchu: {2}); okno programu po {3:N1} s [{4}]; plansza zamknieta po {5:N1} s" -f $k, $tSplash, $top, $tProg, $title, $tClosed
    Start-Sleep -Seconds 1
    Get-Process -Name program -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$dir\*" } | Stop-Process -Force -Confirm:$false
    Start-Sleep -Seconds 2
}
