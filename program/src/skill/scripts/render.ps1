# Renderuje slajdy PPTX do PNG (przez PowerPoint) i opcjonalnie zapisuje kopie z osadzonymi fontami.
#   render.ps1 -Src plik.pptx -Out katalog_png [-EmbedFonts]
# -EmbedFonts: zapisuje plik ponownie przez PowerPoint z osadzonymi fontami TrueType/OTF
# (np. Nunito w wersji odswiezonej), zeby prezentacja wygladala tak samo na innym komputerze.
param([Parameter(Mandatory)][string]$Src, [Parameter(Mandatory)][string]$Out, [switch]$EmbedFonts)
$Src = (Resolve-Path $Src).Path
New-Item -ItemType Directory -Force $Out | Out-Null
$guard = Join-Path $PSScriptRoot "guard.py"
if ($EmbedFonts) {  # kontrola PRZED otwarciem (PowerPoint sam tworzy plik blokady ~$)
    & python $guard check $Src | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Output "UWAGA: pomijam osadzanie fontow - plik edytowany recznie albo otwarty (guard.py)"; $EmbedFonts = $false }
}
$pp = New-Object -ComObject PowerPoint.Application
$p = $pp.Presentations.Open($Src, [int](-not $EmbedFonts), $false, $false)  # bez osadzania: tylko do odczytu
if ($EmbedFonts) {
    # 24 = ppSaveAsOpenXMLPresentation; EmbedTrueTypeFonts = -1 (msoTrue)
    $tmp = [IO.Path]::Combine([IO.Path]::GetDirectoryName($Src), "~embed_" + [IO.Path]::GetFileName($Src))
    $p.SaveAs($tmp, 24, -1)
    $p.Close()
    Move-Item -LiteralPath $tmp -Destination $Src -Force
    & python $guard record $Src
    $p = $pp.Presentations.Open($Src, $true, $false, $false)
}
$i = 1
foreach ($s in $p.Slides) { $s.Export((Join-Path $Out ("s{0:D2}.png" -f $i)), "PNG", 1600, 900); $i++ }
$p.Close()
Write-Output "OK $($i-1) slajdow -> $Out"
