# Gate comparison: v24j vs v23c
# 50T/50F normal + 50T/50F hard3, all 3 official models, raw mode
# Total: 2 cheatsheets × 2 subsets × 3 models × 100 problems = 1,200 API calls

$ErrorActionPreference = "Stop"

$cheatsheets = @("cheatsheets/v24j.txt", "cheatsheets/v23c.txt")
$gates = @("data/hf_cache/gate_normal_50_50.jsonl", "data/hf_cache/gate_hard3_50_50.jsonl")

foreach ($cs in $cheatsheets) {
    foreach ($gate in $gates) {
        Write-Host "`n`n========================================" -ForegroundColor Cyan
        Write-Host "  Cheatsheet: $cs" -ForegroundColor Cyan
        Write-Host "  Gate:       $gate" -ForegroundColor Cyan
        Write-Host "========================================`n" -ForegroundColor Cyan

        python sim_lab.py `
            --data $gate `
            --cheatsheet $cs `
            --all-models `
            --prompt-mode raw `
            --errors
    }
}

Write-Host "`n`nAll gate runs complete!" -ForegroundColor Green
