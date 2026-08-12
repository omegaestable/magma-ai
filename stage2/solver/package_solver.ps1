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
    # -n auto: the gate re-solves ~170 real problems, which is ~160 s serially
    # and ~47 s across cores. Speed matters here because a slow gate is a gate
    # people skip. Falls back to serial when pytest-xdist is not installed.
    & $python -m pytest stage2/tests -q -n auto
    if ($LASTEXITCODE -eq 4) {
        Write-Warning "pytest-xdist unavailable; falling back to a serial gate (slower)."
        & $python -m pytest stage2/tests -q
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Offline correctness gate failed; refusing to package. Re-run with -SkipTests only for a deliberate spike."
    }
}

$outDir = Split-Path $OutPath -Parent
if ($outDir) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    Get-ChildItem -Force -Path $outDir | Remove-Item -Force -Recurse
}

# Write the submission with LF line endings instead of copying the CRLF source.
# This is worth ~10 KB of the 500 KB cap and costs nothing: the working tree is
# CRLF (Windows + git autocrlf), the file is ~10,400 lines, and every one of those
# carries a byte the judge does not need. Measured 2026-08-11: 490,503 bytes as a
# straight copy, 480,115 with LF — 2% of the cap recovered with no content change.
# Python is indifferent to line endings, and the 500 KB limit is on file bytes.
# UTF8Encoding($false) = no BOM; the file contains ◇ and a BOM would be junk the
# judge has to parse.
$text = [System.IO.File]::ReadAllText($sourcePath) -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($OutPath, $text, (New-Object System.Text.UTF8Encoding($false)))
$sizeBytes = (Get-Item $OutPath).Length

if ($sizeBytes -gt $limitBytes) {
    throw "Packaged solver is $sizeBytes bytes; limit is $limitBytes bytes."
}

if ($sizeBytes -gt $WarnBytes) {
    Write-Warning "Packaged solver is $sizeBytes bytes, above the $WarnBytes byte de-bloat target (hard limit $limitBytes)."
}

Write-Host "Packaged $OutPath ($sizeBytes bytes)."
