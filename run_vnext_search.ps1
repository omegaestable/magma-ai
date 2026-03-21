param(
    [string]$Config = "vnext_search_config.json",
    [ValidateSet("build-gates", "baseline", "cycle", "loop", "status")]
    [string]$Action = "status",
    [int]$Cycles = 0,
    [double]$BudgetUsd = 0,
    [switch]$Background
)

$python = "C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe"
$scriptPath = "vnext_search.py"

$args = @($scriptPath, $Action, "--config", $Config)
if ($Cycles -gt 0) {
    $args += @("--max-cycles", $Cycles)
}
if ($BudgetUsd -gt 0) {
    $args += @("--max-budget-usd", $BudgetUsd)
}

if ($Background -and $Action -eq "loop") {
    $job = Start-Job -Name "magma-vnext-search" -ScriptBlock {
        param($pythonExe, $cliArgs)
        & $pythonExe @cliArgs
    } -ArgumentList $python, $args
    "Started background job $($job.Id) with action '$Action'."
    "Check progress with: $python $scriptPath status --config $Config"
    return
}

& $python @args