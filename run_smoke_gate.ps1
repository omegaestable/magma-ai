#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Run the standard smoke test or full gate evaluation protocol.

.DESCRIPTION
  Smoke test: 20/20 normal + 20/20 hard3, all 3 models, 1 repeat.
  Full gate:  50/50 normal + 50/50 hard, all 3 models, 1 repeat.

  Generates fresh benchmark rotations first, then runs sim_lab.py.

.EXAMPLE
  .\run_smoke_gate.ps1 -Cheatsheet v24j -Mode smoke
  .\run_smoke_gate.ps1 -Cheatsheet v24j -Mode gate
  .\run_smoke_gate.ps1 -Cheatsheet v24j -Mode smoke -Model llama-3-3-70b-instruct
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Cheatsheet,

    [ValidateSet("smoke", "gate")]
    [string]$Mode = "smoke",

    [string]$Model = "",

    [switch]$AllModels,

    [int]$Repeats = 1,

    [switch]$SkipRotation,

    [switch]$Errors
)

$python = "C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe"
$csPath = "cheatsheets/$Cheatsheet.txt"

if (-not (Test-Path $csPath)) { throw "Cheatsheet not found: $csPath" }
if (-not (Test-Path Env:OPENROUTER_API_KEY)) { throw "OPENROUTER_API_KEY not set" }

# Determine sizes
if ($Mode -eq "smoke") {
    $normalTrue = 20; $normalFalse = 20
    $hardTrue   = 0;  $hardFalse   = 0
    $hard3True  = 20; $hard3False  = 20
    $subsets = @("normal", "hard3")
} else {
    $normalTrue = 50; $normalFalse = 50
    $hardTrue   = 50; $hardFalse   = 50
    $hard3True  = 0;  $hard3False  = 0
    $subsets = @("normal", "hard")
}

# Generate fresh rotation
if (-not $SkipRotation) {
    Write-Host "`n=== Generating fresh benchmark rotation ===" -ForegroundColor Cyan
    & $python make_unseen_30_30_sets.py `
        --normal-true $normalTrue --normal-false $normalFalse `
        --hard-true $hardTrue --hard-false $hardFalse `
        --hard3-true $hard3True --hard3-false $hard3False
    if ($LASTEXITCODE -ne 0) { throw "Benchmark generation failed" }
}

# Read latest manifest to get file paths
$latest = Get-Content "data/benchmark/rotating_official_latest.json" | ConvertFrom-Json

# Determine models
if ($AllModels -or ($Model -eq "")) {
    $models = @("gpt-oss-120b", "llama-3-3-70b-instruct", "gemma-4-31b-it")
} else {
    $models = @($Model)
}

# Run evaluations
foreach ($file in $latest.files) {
    $subset = $file.subset
    if ($subsets -notcontains $subset) { continue }

    $benchPath = $file.path
    Write-Host "`n=== Evaluating $subset ($benchPath) ===" -ForegroundColor Green

    foreach ($m in $models) {
        Write-Host "`n--- Model: $m ---" -ForegroundColor Yellow
        $simArgs = @(
            "sim_lab.py",
            "--data", $benchPath,
            "--cheatsheet", $csPath,
            "--model", $m,
            "--prompt-mode", "raw",
            "--repeats", $Repeats
        )
        if ($Errors) { $simArgs += "--errors" }
        & $python @simArgs
    }
}

Write-Host "`n=== $Mode complete for $Cheatsheet ===" -ForegroundColor Cyan
