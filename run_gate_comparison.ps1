# Gate comparison: v24j vs v23c
# 50T/50F normal + 50T/50F hard3, all 3 official models, raw mode
# Total: 2 cheatsheets × 2 subsets × 3 models × 100 problems = 1,200 API calls
# Uses --allow-fallbacks to work around deepinfra rate limits in lab

$ErrorActionPreference = "Stop"

$cheatsheets = @("cheatsheets/v24j.txt", "cheatsheets/v23c.txt")
$gates = @("data/hf_cache/gate_normal_50_50.jsonl", "data/hf_cache/gate_hard3_50_50.jsonl")
$models = @("gpt-oss-120b", "llama-3-3-70b-instruct", "gemma-4-31b-it")

foreach ($cs in $cheatsheets) {
    foreach ($gate in $gates) {
        foreach ($model in $models) {
            Write-Host "`n========================================" -ForegroundColor Cyan
            Write-Host "  CS: $cs | Gate: $(Split-Path $gate -Leaf) | Model: $model" -ForegroundColor Cyan
            Write-Host "========================================`n" -ForegroundColor Cyan

            python sim_lab.py `
                --data $gate `
                --cheatsheet $cs `
                --model $model `
                --prompt-mode raw `
                --errors `
                --allow-fallbacks

            # Brief pause between models to avoid rate limits
            Start-Sleep -Seconds 5
        }
    }
}

Write-Host "`n`nAll gate runs complete!" -ForegroundColor Green
