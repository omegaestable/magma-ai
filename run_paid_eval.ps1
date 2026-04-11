param(
    [Parameter(Mandatory = $true)]
    [string]$Benchmark,

    [Parameter(Mandatory = $true)]
    [string]$Cheatsheet,

    [ValidateSet(
        "gpt-oss-120b", "llama-3-3-70b-instruct", "gemma-4-31b-it",
        "meta-llama/llama-3.3-70b-instruct",
        "openai/gpt-oss-120b",
        "google/gemma-4-31b-it"
    )]
    [string]$Model = "llama-3-3-70b-instruct",

    [switch]$AllModels,

    [ValidateSet("raw", "wrapped")]
    [string]$PromptMode = "raw",

    [int]$Repeats = 3,

    [switch]$Errors
)

$python = "C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe"
$benchmarkPath = "data/benchmark/$Benchmark.jsonl"
$cheatsheetPath = "cheatsheets/$Cheatsheet.txt"

if (-not (Test-Path $benchmarkPath)) {
    throw "Benchmark not found: $benchmarkPath"
}

if (-not (Test-Path $cheatsheetPath)) {
    throw "Cheatsheet not found: $cheatsheetPath"
}

if (-not (Test-Path Env:OPENROUTER_API_KEY)) {
    throw "OPENROUTER_API_KEY is not set in the environment."
}

$baseArgs = @(
    "sim_lab.py",
    "--data", $benchmarkPath,
    "--cheatsheet", $cheatsheetPath,
    "--prompt-mode", $PromptMode,
    "--repeats", $Repeats
)

if ($Errors) {
    $baseArgs += "--errors"
}

if ($AllModels) {
    Write-Host "`n=== Running all 3 official models ===" -ForegroundColor Cyan
    foreach ($m in @("gpt-oss-120b", "llama-3-3-70b-instruct", "gemma-4-31b-it")) {
        Write-Host "`n--- $m ---" -ForegroundColor Yellow
        & $python @baseArgs --model $m
    }
} else {
    & $python @baseArgs --model $Model
}