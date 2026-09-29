# Podmienia znaczniki filmu na PRAWDZIWE wideo online (YouTube), odtwarzane w slajdzie po kliknięciu.
#   online_video.ps1 -Src plik.pptx
# Generator (build_dk / build_deck) wstawia w miejsce filmu obraz o nazwie "ONLINE|<adres>|<promień 0-0.5>".
# Tu PowerPoint sam wstawia wideo online (ten sam obiekt co Wstawianie > Wideo > Wideo online), w tym samym
# miejscu i rozmiarze, z zaokrąglonymi rogami (kształt wideo = zaokrąglony prostokąt), a znacznik usuwa.
# Lekcja 29.09.2026: obraz z hiperłączem NIE jest filmem - user: "dodałeś film jako grafikę i nie da się go uruchomić".
# Wymaga internetu (PowerPoint pobiera miniaturę z YouTube). Plik zapisuje w miejscu i zapisuje sumę w guard.py.
param([Parameter(Mandatory)][string]$Src)
$Src = (Resolve-Path -LiteralPath $Src).Path
$NAME = "Film YouTube (odtwarza się w slajdzie) - podmiana: Wstawianie > Wideo > Wideo online, potem Malarz formatów z tego filmu na nowy"
$pp = New-Object -ComObject PowerPoint.Application
$p = $pp.Presentations.Open($Src, 0, 0, 0)
$n = 0
foreach ($s in $p.Slides) {
    $marks = @($s.Shapes | Where-Object { $_.Name -like "ONLINE|*" })
    foreach ($m in $marks) {
        $parts = $m.Name.Split("|")
        $url = $parts[1]; $adj = [double]::Parse($parts[2], [Globalization.CultureInfo]::InvariantCulture)
        $id = $null
        if ($url -match "(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})") { $id = $Matches[1] }
        if (-not $id) { Write-Output "POMIJAM (to nie adres YouTube): $url"; continue }
        $start = if ($url -match "[?&]t=(\d+)") { "?start=$($Matches[1])" } else { "" }
        $tag = "<iframe width=""560"" height=""315"" src=""https://www.youtube.com/embed/$id$start"" frameborder=""0"" allowfullscreen></iframe>"
        $v = $s.Shapes.AddMediaObjectFromEmbedTag($tag, $m.Left, $m.Top, $m.Width, $m.Height)
        $v.LockAspectRatio = 0
        $v.Left = $m.Left; $v.Top = $m.Top; $v.Width = $m.Width; $v.Height = $m.Height
        if ($adj -gt 0) { $v.AutoShapeType = 5; $v.Adjustments.Item(1) = $adj }
        $v.Name = $NAME
        while ($v.ZOrderPosition -gt $m.ZOrderPosition + 1) { $v.ZOrder(3) }  # 3 = msoSendBackward: warstwa znacznika
        $m.Delete()
        $n++
        Write-Output ("slajd {0}: wideo online {1} (typ {2}, ksztalt {3})" -f $s.SlideIndex, $id, $v.Type, $v.AutoShapeType)
    }
}
if ($n -gt 0) { $p.Save() }
$p.Close()
if ($n -gt 0) { & python (Join-Path $PSScriptRoot "guard.py") record $Src | Out-Null }
Write-Output "OK: $n film(y) online -> $([IO.Path]::GetFileName($Src))"
