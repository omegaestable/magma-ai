param(
    [string]$OutPath = "stage2/submissions/solver.py"
)

$sourcePath = "stage2/solver/solver.py"
$limitBytes = 500000

if (-not (Test-Path $sourcePath)) {
    throw "Missing solver source: $sourcePath"
}

$outDir = Split-Path $OutPath -Parent
if ($outDir) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Get-ChildItem -Force -Path $outDir | Remove-Item -Force -Recurse
}

Copy-Item -Force $sourcePath $OutPath
$sizeBytes = (Get-Item $OutPath).Length

if ($sizeBytes -gt $limitBytes) {
    throw "Packaged solver is $sizeBytes bytes; limit is $limitBytes bytes."
}

Write-Host "Packaged $OutPath ($sizeBytes bytes)."
