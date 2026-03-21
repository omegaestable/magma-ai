param(
    [string]$Config = "vnext_search_config.json",
    [int]$IntervalSeconds = 30,
    [int]$MaxMinutes = 180,
    [switch]$StopWhenSearchJobDone = $true
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $repoRoot ".venv/Scripts/python.exe"
$scriptPath = Join-Path $repoRoot "vnext_search.py"
$configPath = if ([System.IO.Path]::IsPathRooted($Config)) { $Config } else { Join-Path $repoRoot $Config }
$heartbeatPath = Join-Path $repoRoot "results/vnext_search/status_heartbeat.log"

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $heartbeatPath) | Out-Null

if ($IntervalSeconds -lt 5) {
    $IntervalSeconds = 5
}

$deadline = (Get-Date).AddMinutes($MaxMinutes)

while ((Get-Date) -lt $deadline) {
    # Refresh status.md via controller command.
    & $python $scriptPath status --config $configPath | Out-Null

    $searchJob = Get-Job -Name "magma-vnext-search" -ErrorAction SilentlyContinue
    $jobState = if ($null -eq $searchJob) { "missing" } else { $searchJob.State }
    $timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    Add-Content -Path $heartbeatPath -Value "$timestamp | monitor=alive | search_job_state=$jobState"

    if ($StopWhenSearchJobDone -and $null -ne $searchJob -and $searchJob.State -ne "Running") {
        Add-Content -Path $heartbeatPath -Value "$timestamp | monitor=stopping | reason=search_job_finished"
        break
    }

    Start-Sleep -Seconds $IntervalSeconds
}
