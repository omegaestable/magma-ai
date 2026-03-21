param(
    [Parameter(Mandatory = $true)]
    [string]$ChampionPath,

    [Parameter(Mandatory = $true)]
    [string]$CandidatePath,

    [Parameter(Mandatory = $true)]
    [string]$FailureSummaryPath,

    [Parameter(Mandatory = $true)]
    [string]$MutationFocus,

    [string]$CopilotCommand = "copilot",

    [string]$CopilotModel = ""
)

$python = "C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe"
& $python invoke_copilot_candidate.py `
    --champion-path $ChampionPath `
    --candidate-path $CandidatePath `
    --failure-summary-path $FailureSummaryPath `
    --mutation-focus $MutationFocus `
    --copilot-command $CopilotCommand `
    --copilot-model $CopilotModel
if ($LASTEXITCODE -ne 0) {
    throw "Python Copilot adapter failed."
}