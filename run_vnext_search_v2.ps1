param(
    [string]$Config = "vnext_search_v2_config.json",
    [ValidateSet("build-gates", "freeze-legacy", "init", "cycle", "loop", "status", "replay-check")]
    [string]$Action = "status",
    [int]$Cycles = 0,
    [double]$BudgetUsd = 0,
    [string]$Cheatsheets = "",
    [switch]$Background
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $repoRoot ".venv/Scripts/python.exe"
$scriptPath = Join-Path $repoRoot "vnext_search_v2.py"
$configPath = if ([System.IO.Path]::IsPathRooted($Config)) { $Config } else { Join-Path $repoRoot $Config }

if ($Background -and $Action -eq "loop") {
    $job = Start-Job -Name "magma-vnext-search-v2" -ScriptBlock {
        param($pythonExe, $scriptArg, $actionArg, $configArg, $cyclesArg, $budgetArg, $workingDir)
        Set-Location $workingDir
        if ($cyclesArg -gt 0 -and $budgetArg -gt 0) {
            & $pythonExe $scriptArg $actionArg "--config" $configArg "--max-cycles" $cyclesArg "--max-budget-usd" $budgetArg
        }
        elseif ($cyclesArg -gt 0) {
            & $pythonExe $scriptArg $actionArg "--config" $configArg "--max-cycles" $cyclesArg
        }
        elseif ($budgetArg -gt 0) {
            & $pythonExe $scriptArg $actionArg "--config" $configArg "--max-budget-usd" $budgetArg
        }
        else {
            & $pythonExe $scriptArg $actionArg "--config" $configArg
        }
    } -ArgumentList $python, $scriptPath, $Action, $configPath, $Cycles, $BudgetUsd, $repoRoot
    "Started background job $($job.Id) with action '$Action'."
    "Check progress with: $python $scriptPath status --config $configPath"
    return
}

if ($Cycles -gt 0 -and $BudgetUsd -gt 0 -and $Cheatsheets) {
    & $python $scriptPath $Action "--config" $configPath "--max-cycles" $Cycles "--max-budget-usd" $BudgetUsd "--cheatsheets" $Cheatsheets
}
elseif ($Cycles -gt 0 -and $BudgetUsd -gt 0) {
    & $python $scriptPath $Action "--config" $configPath "--max-cycles" $Cycles "--max-budget-usd" $BudgetUsd
}
elseif ($Cycles -gt 0 -and $Cheatsheets) {
    & $python $scriptPath $Action "--config" $configPath "--max-cycles" $Cycles "--cheatsheets" $Cheatsheets
}
elseif ($BudgetUsd -gt 0 -and $Cheatsheets) {
    & $python $scriptPath $Action "--config" $configPath "--max-budget-usd" $BudgetUsd "--cheatsheets" $Cheatsheets
}
elseif ($Cycles -gt 0) {
    & $python $scriptPath $Action "--config" $configPath "--max-cycles" $Cycles
}
elseif ($BudgetUsd -gt 0) {
    & $python $scriptPath $Action "--config" $configPath "--max-budget-usd" $BudgetUsd
}
elseif ($Cheatsheets) {
    & $python $scriptPath $Action "--config" $configPath "--cheatsheets" $Cheatsheets
}
else {
    & $python $scriptPath $Action "--config" $configPath
}
