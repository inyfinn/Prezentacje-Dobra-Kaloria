param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Path)   # -File przekazuje ścieżki jako osobne argumenty
# Rozpoznawanie tekstu wbudowane w Windows 10/11 (Windows.Media.Ocr) - bez instalowania czegokolwiek.
# Wypisuje JSON: [{ "plik": ..., "tekst": ... }]. Używane do rozpoznania smaku po napisie na opakowaniu.
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]
$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq "AsTask" -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
function Await($op, $type) { $t = $asTask.MakeGenericMethod($type).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result }
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $engine) { $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage((New-Object Windows.Globalization.Language "en-US")) }
$out = @()
foreach ($p in $Path) {
    $txt = ""
    try {
        $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path -LiteralPath $p).ProviderPath)) ([Windows.Storage.StorageFile])
        $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $dec = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bmp = Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        if ($bmp.PixelWidth -gt [Windows.Media.Ocr.OcrEngine]::MaxImageDimension -or $bmp.PixelHeight -gt [Windows.Media.Ocr.OcrEngine]::MaxImageDimension) {
            $s = [Windows.Media.Ocr.OcrEngine]::MaxImageDimension / [Math]::Max($bmp.PixelWidth, $bmp.PixelHeight)
            $tr = New-Object Windows.Graphics.Imaging.BitmapTransform
            $tr.ScaledWidth = [uint32]($bmp.PixelWidth * $s); $tr.ScaledHeight = [uint32]($bmp.PixelHeight * $s)
            $bmp = Await ($dec.GetSoftwareBitmapAsync($dec.BitmapPixelFormat, [Windows.Graphics.Imaging.BitmapAlphaMode]::Premultiplied, $tr,
                [Windows.Graphics.Imaging.ExifOrientationMode]::IgnoreExifOrientation, [Windows.Graphics.Imaging.ColorManagementMode]::DoNotColorManage)) ([Windows.Graphics.Imaging.SoftwareBitmap])
        }
        $res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
        $txt = $res.Text
        $stream.Dispose()
    } catch { $txt = "" }
    $out += [pscustomobject]@{ plik = $p; tekst = $txt }
}
[Console]::OutputEncoding = [Text.Encoding]::UTF8
ConvertTo-Json -InputObject @($out) -Compress
