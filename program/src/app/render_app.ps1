# Program "Stwórz prezentację": osadza czcionki i eksportuje slajdy do PNG przez PowerPoint (bez Pythona - program
# jest spakowany, więc nie może wołać "python guard.py" jak render.ps1 ze skilla; blokadę zapisuje silnik).
#   render_app.ps1 -Src plik.pptx -Out katalog_png [-NoEmbed]
param([Parameter(Mandatory)][string]$Src, [Parameter(Mandatory)][string]$Out, [switch]$NoEmbed)
$Src = (Resolve-Path -LiteralPath $Src).Path
New-Item -ItemType Directory -Force $Out | Out-Null
$pp = New-Object -ComObject PowerPoint.Application
if (-not $NoEmbed) {
    $p = $pp.Presentations.Open($Src, 0, 0, 0)
    $tmp = Join-Path (Split-Path -LiteralPath $Src) ("~embed_" + [IO.Path]::GetFileName($Src))
    $p.SaveAs($tmp, 24, -1)   # 24 = ppSaveAsOpenXMLPresentation, -1 = osadź czcionki TrueType/OTF
    $p.Close()
    Move-Item -LiteralPath $tmp -Destination $Src -Force
}
$p = $pp.Presentations.Open($Src, -1, 0, 0)   # tylko do odczytu, bez okna
$i = 1
foreach ($s in $p.Slides) { $s.Export((Join-Path $Out ("s{0:D2}.png" -f $i)), "PNG", 1600, 900); $i++ }
$p.Close()
Write-Output "OK $($i-1) slajdow -> $Out"
