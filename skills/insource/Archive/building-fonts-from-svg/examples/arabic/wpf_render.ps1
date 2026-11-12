Add-Type -AssemblyName PresentationCore, WindowsBase, PresentationFramework, System.Xaml

$fontDir  = Split-Path -Parent $PSScriptRoot
$outPng   = Join-Path $PSScriptRoot "wpf_directwrite.png"

$baseUri = New-Object System.Uri(("file:///" + ($fontDir -replace '\\','/') + "/arabic/"))
$family  = New-Object System.Windows.Media.FontFamily($baseUri, "./ArabicSans.ttf#ArabicSans")
$typeface = New-Object System.Windows.Media.Typeface($family)

function U { param([int[]]$cps) -join ($cps | ForEach-Object { [char]$_ }) }
$nl = [char]10
# سلام / العربية / مرحبا / الحمد لله
$text = (U 0x0633,0x0644,0x0627,0x0645) + $nl +
        (U 0x0627,0x0644,0x0639,0x0631,0x0628,0x064A,0x0629) + $nl +
        (U 0x0645,0x0631,0x062D,0x0628,0x0627) + $nl +
        (U 0x0627,0x0644,0x062D,0x0645,0x062F) + [char]32 + (U 0x0627,0x0644,0x0644,0x0647)

$culture = [System.Globalization.CultureInfo]::GetCultureInfo("ar-SA")
$flow = [System.Windows.FlowDirection]::LeftToRight
$ft = New-Object System.Windows.Media.FormattedText($text, $culture, $flow,
        (New-Object System.Windows.Media.Typeface($family, [System.Windows.FontStyles]::Normal,
        [System.Windows.FontWeights]::Normal, [System.Windows.FontStretches]::Normal)),
        80.0, [System.Windows.Media.Brushes]::Black, 1.0)

$w = [int]($ft.Width) + 120
$h = [int]($ft.Height) + 80
$dv = New-Object System.Windows.Media.DrawingVisual
$dc = $dv.RenderOpen()
$dc.DrawText($ft, (New-Object System.Windows.Point(60, 40)))
$dc.Close()
$rtb = New-Object System.Windows.Media.Imaging.RenderTargetBitmap($w, $h, 96, 96,
        [System.Windows.Media.PixelFormats]::Pbgra32)
$rtb.Render($dv)
$enc = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
$enc.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($rtb))
$fs = [System.IO.File]::Create($outPng); $enc.Save($fs); $fs.Close()

Write-Output ("family: " + ($family.FamilyNames.Values -join ','))
Write-Output ("rendered " + $outPng + " " + $w + "x" + $h)
