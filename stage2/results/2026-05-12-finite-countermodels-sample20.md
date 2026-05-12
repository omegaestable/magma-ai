# Finite Countermodels Sample 20

Date: 2026-05-12

Solver artifact: `stage2/submissions/solver.py`

Size: 8712 bytes

Command:

```powershell
$env:PYTHONUTF8='1'
$env:PATH="$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_20.json --output ..\..\tmp_stage2_impl_sample20.json
Pop-Location
```

Result:

- Solved: 10/20
- Verdicts accepted: 10 FALSE
- LLM calls: 0
- Judge calls: 10
- Total runner time: 34.7s

Accepted problem ids:

- `normal_0703`
- `normal_0775`
- `normal_0905`
- `normal_0570`
- `normal_0102`
- `normal_0618`
- `normal_0456`
- `normal_0030`
- `normal_0029`
- `normal_0108`

Notes:

- This run validates the first active finite-countermodel engine in `stage2/solver/solver.py`.
- Unresolved cases were skipped rather than answered speculatively.
