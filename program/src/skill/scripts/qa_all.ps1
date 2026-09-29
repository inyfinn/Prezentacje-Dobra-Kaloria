# Przebudowa + osadzenie fontów + test kolizji dla wszystkich prezentacji projektu.
#   qa_all.ps1 -Robocze "<folder produktu>\_robocze" [-Szablon "<folder szablonu>"] [-Only B,C]
param([Parameter(Mandatory)][string]$Robocze, [string]$Szablon = "", [string[]]$Only = @("A", "B", "C"))
$SK = $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
Push-Location $Robocze
if (Test-Path "make_specs.py") { python make_specs.py | Out-Null }  # jedno źródło treści, jeśli jest
$files = @()
foreach ($x in $Only) {
    $builder = if ($x -eq "A") { "build_deck.py" } else { "build_dk.py" }
    $out = python "$SK\$builder" "spec_$x.json" | Select-Object -Last 1
    $out
    if ($out -match "^OK (.+\.pptx) \d+ slajdow") { $files += (Resolve-Path $Matches[1]).Path }
}
Pop-Location
if ($Szablon) {
    python "$SK\make_template.py" $Szablon | ForEach-Object { $_; if ($_ -match "^OK (.+\.pptx) \d+ slajdow") { $files += $Matches[1] } }
}
foreach ($f in $files) {
    $name = [IO.Path]::GetFileNameWithoutExtension($f)
    & "$SK\render.ps1" -Src $f -Out (Join-Path $Robocze ("qa\" + $name)) -EmbedFonts:($name -notlike "*A (szablon*") | Out-Null
    "=== $name"
    & "$SK\verify.ps1" -Src $f | Select-String -Pattern "Tekst - problemy|TEKST|GRAFIKA|PRZEPE|krawedzi|Przejscia|Fonty"
}
