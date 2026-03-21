param(
    [string]$Config = "vnext_search_config.json",
    [ValidateSet("build-gates", "baseline", "cycle", "loop", "status")]
    [string]$Action = "status",
    [int]$Cycles = 0,
    [double]$BudgetUsd = 0,
    [switch]$Background
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $repoRoot ".venv/Scripts/python.exe"
$scriptPath = Join-Path $repoRoot "vnext_search.py"
$configPath = if ([System.IO.Path]::IsPathRooted($Config)) { $Config } else { Join-Path $repoRoot $Config }

$args = @($scriptPath, $Action, "--config", $configPath)
if ($Cycles -gt 0) {
    $args += @("--max-cycles", $Cycles)
}
if ($BudgetUsd -gt 0) {
    $args += @("--max-budget-usd", $BudgetUsd)
}

if ($Background -and $Action -eq "loop") {
    $job = Start-Job -Name "magma-vnext-search" -ScriptBlock {
        param($pythonExe, $cliArgs, $workingDir)
        Set-Location $workingDir
        & $pythonExe @cliArgs
    } -ArgumentList $python, $args, $repoRoot
    "Started background job $($job.Id) with action '$Action'."
    "Check progress with: $python $scriptPath status --config $configPath"
    return
}

& $python @args