param(
    [string]$OutPath = "stage2/submissions/solver.py",
    [switch]$SkipTests,
    [int]$WarnBytes = 150000
)

$sourcePath = "stage2/solver/solver.py"
$limitBytes = 500000

if (-not (Test-Path $sourcePath)) {
    throw "Missing solver source: $sourcePath"
}

# Offline correctness gate. The Lean judge is cloud-only, so these oracles
# (proof kernel + finite-model checks + golden routes) are the local guard
# against shipping `incorrect` certificates. Do not package around a failure.
if (-not $SkipTests) {
    $python = if (Test-Path ".venv/Scripts/python.exe") { ".venv/Scripts/python.exe" } else { "python" }
    Write-Host "Running offline correctness gate..."
    & $python -m pytest stage2/tests -q
    if ($LASTEXITCODE -ne 0) {
        throw "Offline correctness gate failed; refusing to package. Re-run with -SkipTests only for a deliberate spike."
    }
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

if ($sizeBytes -gt $WarnBytes) {
    Write-Warning "Packaged solver is $sizeBytes bytes, above the $WarnBytes byte de-bloat target (hard limit $limitBytes)."
}

Write-Host "Packaged $OutPath ($sizeBytes bytes)."
