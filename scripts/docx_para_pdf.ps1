# Converte um .docx em .pdf usando o Microsoft Word instalado.
# Uso: powershell -File scripts/docx_para_pdf.ps1 <entrada.docx> <saida.pdf>
param([string]$Entrada, [string]$Saida)
$entradaAbs = (Resolve-Path $Entrada).Path
if (-not [System.IO.Path]::IsPathRooted($Saida)) { $Saida = Join-Path (Get-Location) $Saida }
$saidaAbs = [System.IO.Path]::GetFullPath($Saida)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($entradaAbs, $false, $true)
    $doc.ExportAsFixedFormat($saidaAbs, 17)  # 17 = wdExportFormatPDF
    $paginas = $doc.ComputeStatistics(2)       # 2 = wdStatisticPages
    $doc.Close($false)
    Write-Output "PDF gerado: $saidaAbs ($paginas paginas)"
} finally {
    $word.Quit()
}
