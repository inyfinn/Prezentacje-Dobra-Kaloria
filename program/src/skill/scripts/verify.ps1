# Weryfikacja PPTX przez PowerPoint (nie przez XML): Morph, ukryte slajdy, sekcje, kolory motywu, fonty, etykiety.
#   verify.ps1 -Src plik.pptx
param([Parameter(Mandatory)][string]$Src)
$Src = (Resolve-Path $Src).Path
$pp = New-Object -ComObject PowerPoint.Application
$p = $pp.Presentations.Open($Src, $true, $false, $false)
$W = $p.PageSetup.SlideWidth
$effects = @{}; $hidden = @(); $labels = 0; $noLabel = @()
foreach ($s in $p.Slides) {
    $e = [string]$s.SlideShowTransition.EntryEffect
    $effects[$e] = 1 + [int]$effects[$e]
    if ($s.SlideShowTransition.Hidden -eq -1) { $hidden += $s.SlideIndex }
    $off = @($s.Shapes | Where-Object { $_.Left -ge $W })
    if ($off.Count -gt 0) { $labels++ } else { $noLabel += $s.SlideIndex }
}
$sec = $p.SectionProperties
$names = @(); for ($i = 1; $i -le $sec.Count; $i++) { $names += "$($sec.Name($i)) ($($sec.SlidesCount($i)))" }
$scheme = $p.SlideMaster.Theme.ThemeColorScheme
$cols = @(); foreach ($k in 1..12) { $c = $scheme.Colors($k).RGB; $cols += ('{0:X2}{1:X2}{2:X2}' -f ($c -band 255), (($c -shr 8) -band 255), (($c -shr 16) -band 255)) }
$fonts = $p.SlideMaster.Theme.ThemeFontScheme
"Plik:            $([IO.Path]::GetFileName($Src))"
"Slajdy:          $($p.Slides.Count)"
"Przejscia:       $(($effects.GetEnumerator() | ForEach-Object { "efekt $($_.Key) x$($_.Value)" }) -join ', ')  (3954 = Morph wg obiektow, potwierdzone empirycznie 28.09.2026)"
"Ukryte:          $($hidden -join ', ')"
"Sekcje:          $($names -join ' | ')"
"Etykiety poza:   $labels slajdow (bez etykiety: $($noLabel -join ', '))"
"Kolory motywu:   dk1 lt1 dk2 lt2 acc1-6 hl fhl = $($cols -join ' ')"
"Czcionki motywu: naglowki=$($fonts.MajorFont(1).Name) tresc=$($fonts.MinorFont(1).Name)"
# Tekst wychodzący poza pole / slajd / za blisko krawędzi (objaw "prawie przycięty")
$H = $p.PageSetup.SlideHeight; $issues = @()
foreach ($s in $p.Slides) {
  foreach ($sh in $s.Shapes) {
    if (-not $sh.HasTextFrame) { continue }
    if ($sh.Left -ge $W -or $sh.Name -like "tlo*") { continue }  # etykiety poza slajdem i dekoracje "tlo-" - celowo
    $tr = $sh.TextFrame2.TextRange; if ($tr.Text.Trim().Length -eq 0) { continue }
    $bt = $tr.BoundTop; $bh = $tr.BoundHeight; $bl = $tr.BoundLeft; $bw = $tr.BoundWidth
    $t = $tr.Text.Trim(); if ($t.Length -gt 28) { $t = $t.Substring(0, 28) }
    if ($bh -gt $sh.Height + 2) { $issues += "s$($s.SlideIndex) PRZEPELNIENIE pola +$([math]::Round($bh - $sh.Height))pt: '$t'" }
    if ($bl + $bw -gt $W - 8 -or $bl -lt 8) { $issues += "s$($s.SlideIndex) przy krawedzi poziomej: '$t'" }
    if ($bt + $bh -gt $H - 6) { $issues += "s$($s.SlideIndex) przy dolnej krawedzi: '$t'" }
    if ($bt -lt 6) { $issues += "s$($s.SlideIndex) przy gornej krawedzi: '$t'" }
  }
}
# Kolizje: tekst x grafika (packshot, element) oraz grafika x logo  (lekcja 28.09: tekst nachodzil na paczki)
function Box($x, $y, $w, $h) { return @{ l = $x; t = $y; r = $x + $w; b = $y + $h } }
function Inter($a, $b) { $w = [math]::Min($a.r, $b.r) - [math]::Max($a.l, $b.l); $h = [math]::Min($a.b, $b.b) - [math]::Max($a.t, $b.t); if ($w -gt 0 -and $h -gt 0) { return $w * $h } else { return 0 } }
foreach ($s in $p.Slides) {
  $pics = @(); $logos = @(); $texts = @()
  foreach ($sh in $s.Shapes) {
    if ($sh.Left -ge $W) { continue }
    if ($sh.Type -eq 13) {
      $bx = Box $sh.Left $sh.Top $sh.Width $sh.Height
      if ($sh.Name -like "*logo*") { $logos += $bx }
      elseif ($sh.Name -eq "!!image" -or $sh.Name -like "tlo*" -or $sh.Name -like "Zdj*" -or $sh.Name -like "Film*" -or ($sh.Width -gt $W * 0.4 -and $sh.Height -gt $H * 0.6)) { }  # zdjecie tla / pelnoekranowe - celowo pod tekstem
      else { $pics += @{ box = $bx; name = $sh.Name } }
    }
    elseif ($sh.HasTextFrame) {
      $tr = $sh.TextFrame2.TextRange
      if ($tr.Text.Trim().Length -gt 0) { $tt = $tr.Text.Trim(); if ($tt.Length -gt 24) { $tt = $tt.Substring(0, 24) }; $texts += @{ box = (Box $tr.BoundLeft $tr.BoundTop $tr.BoundWidth $tr.BoundHeight); t = $tt } }
    }
  }
  foreach ($tx in $texts) { foreach ($pc in $pics) {
    $a = Inter $tx.box $pc.box
    $ta = ($tx.box.r - $tx.box.l) * ($tx.box.b - $tx.box.t)
    if ($ta -gt 0 -and $a / $ta -gt 0.02) { $issues += "s$($s.SlideIndex) TEKST NA GRAFICE ($([math]::Round(100 * $a / $ta))%): '$($tx.t)' x $($pc.name)" }
  } }
  foreach ($lg in $logos) { foreach ($pc in $pics) {
    $a = Inter $lg $pc.box; $la = ($lg.r - $lg.l) * ($lg.b - $lg.t)
    if ($la -gt 0 -and $a / $la -gt 0.02) { $issues += "s$($s.SlideIndex) GRAFIKA NA LOGO ($([math]::Round(100 * $a / $la))%): $($pc.name)" }
  } }
}
# Typografia PL (reguła usera 29.09, ZAWSZE): linie czytane z PowerPointa (faktyczne łamanie, nie z kodu).
#  ZAWIESZKA = linia kończy się jednoliterowym spójnikiem/przyimkiem (a i o u w z); MYŚLNIK na początku linii;
#  SIEROTA = ostatnia linia akapitu to jedno słowo (także gdy generator rozbił nagłówek na akapity-linie).
$nb = [char]0xA0
foreach ($s in $p.Slides) {
  foreach ($sh in $s.Shapes) {
    if (-not $sh.HasTextFrame) { continue }
    if ($sh.Left -ge $W -or $sh.Name -like "tlo*") { continue }
    $tr = $sh.TextFrame2.TextRange; if ($tr.Text.Trim().Length -eq 0) { continue }
    $np = $tr.Paragraphs().Count; $prevEnd = ""; $prevLine = ""
    for ($i = 1; $i -le $np; $i++) {
      $para = $tr.Paragraphs($i); $nl = $para.Lines().Count
      for ($j = 1; $j -le $nl; $j++) {
        $ln = $para.Lines($j).Text.Replace($nb, " ").Trim()
        if ($ln.Length -eq 0) { continue }
        $last = ($i -eq $np -and $j -eq $nl)
        if (-not $last -and $ln -match '(^|\s)[aiouwzAIOUWZ]$') { $issues += "s$($s.SlideIndex) ZAWIESZKA na koncu linii: '...$($ln.Substring([math]::Max(0,$ln.Length-24)))'" }
        if ($j -gt 1 -and $ln -match '^[-–—]\s') { $issues += "s$($s.SlideIndex) MYSLNIK na poczatku linii: '$($ln.Substring(0,[math]::Min(24,$ln.Length)))'" }
        if ($j -eq $nl -and $nl -gt 1 -and $ln -notmatch '\s' -and (($prevLine -split '\s+').Count -ge 3 -or $ln.Trim('?!.,').Length -le 4)) { $issues += "s$($s.SlideIndex) SIEROTA (1 slowo w ostatniej linii): '$ln'" }
        $prevLine = $ln
      }
      $pt = $para.Text.Replace($nb, " ").Trim()
      $bul = $para.ParagraphFormat.Bullet.Visible -eq -1  # punkty listy = osobne pozycje, nie sieroty
      if (-not $bul -and $i -eq $np -and $np -gt 1 -and $nl -eq 1 -and $pt -notmatch '\s' -and $pt.Length -gt 0 -and (($prevEnd -split '\s+').Count -ge 3 -or $pt.Trim('?!.,').Length -le 4) -and $prevEnd -notmatch '[\.\!\?\:\]\)]$') { $issues += "s$($s.SlideIndex) SIEROTA w naglowku: '$pt'" }
      if ($pt.Length -gt 0) { $prevEnd = $pt }
    }
  }
}
"Tekst - problemy: $($issues.Count)"
$issues | ForEach-Object { "   $_" }
$p.Close()
Add-Type -AssemblyName System.IO.Compression.FileSystem
$z = [IO.Compression.ZipFile]::OpenRead($Src)
"Fonty osadzone:  $(@($z.Entries | Where-Object { $_.FullName -like 'ppt/fonts/*' }).Count) plikow"
$z.Dispose()
