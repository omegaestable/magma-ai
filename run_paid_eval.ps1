param(
    [Parameter(Mandatory = $true)]
    [string]$Benchmark,

    [Parameter(Mandatory = $true)]
    [string]$Cheatsheet,

    [string]$Model = "meta-llama/llama-3.3-70b-instruct",

    [ValidateSet("wrapped", "complete")]
    [string]$PromptMode = "wrapped",

    [ValidateSet("strict", "lenient")]
    [string]$Parser = "strict",

    [int]$Repeats = 3
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

& $python sim_lab.py --data $benchmarkPath --cheatsheet $cheatsheetPath --openrouter --model $Model --prompt-mode $PromptMode --parser $Parser --repeats $Repeats --errors