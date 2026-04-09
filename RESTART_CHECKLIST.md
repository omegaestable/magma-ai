# Restart Checklist

Use this file when returning to the repo after time away or when a new agent starts from scratch.

## 1. Orient

Read these files first:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `.github/copilot-instructions.md`
5. `EVAL_WORKFLOW.md`
6. `BENCHMARK_MANIFEST.md`

## 2. Confirm Current Artifacts

1. **Champion: `cheatsheets/v24j.txt`** (8,955 bytes, 87.4% of cap)
2. Previous champion: `cheatsheets/v21f_structural.txt` (historical)
3. Canonical evaluator: `sim_lab.py`
4. Canonical wrapper: `run_paid_eval.ps1`
5. Next design doc: `V25A_MASTER_PROMPT.md`

## 3. Confirm Environment

1. Activate `.venv`
2. Set `OPENROUTER_API_KEY`
3. Verify cheatsheet size if editing candidates

Example:

```powershell
$env:OPENROUTER_API_KEY = "<your_key>"
(Get-Item "cheatsheets\v24j.txt").Length
```

## 4. Run One Smoke Eval

Purpose: verify that the evaluator, OpenRouter access, and repo wiring work before you spend tokens on a full candidate gate.

Run the champion on one warmup benchmark:

```powershell
.\run_paid_eval.ps1 -Benchmark normal_balanced10_true5_false5_seed0 -Cheatsheet v24j
```

Expected result: about 90% on this smoke test. If this fails badly, fix environment or provider issues before testing candidates.

Or run directly with `sim_lab.py`:

```powershell
python sim_lab.py --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --cheatsheet cheatsheets/v24j.txt --openrouter --errors
```

## 5. If You Need To Iterate

Follow this order:

1. Evaluate
2. Read result JSON
3. Run `analyze_seed_failures.py`
4. Run `distill.py`
5. Patch conservatively
6. Re-run normal gates

## 6. Do Not Start Here

Avoid starting from these unless the user asks for them:

- `vnext_search_v2.py`
- `proof_atlas.py`
- `atlas_public_dev.py`
- historical planning files as the source of truth

## 7. Common Traps

1. Reintroducing Jinja2 logic into cheatsheets
2. Overfitting to one benchmark file
3. Treating a coverage gap like an execution bug, or the reverse
4. Promoting hard uplift with hidden normal regression