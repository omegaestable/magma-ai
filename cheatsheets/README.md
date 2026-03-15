# Cheatsheet Set

The live submission artifact is always `../cheatsheet.txt`.

Files in this folder are archived candidates and ablations:

- `cheatsheet_2026-03-14_pre_robust_rules.txt`: early sparse rule list.
- `cheatsheet_2026-03-14_robust_rules_v1.txt`: stronger FALSE-side baseline, still underuses byte budget.
- `cheatsheet_e2e_2026_03_14_candidate_default.txt`: LLM-distilled ablation; keep for comparison, not as default.
- `cheatsheet_2026-03-14_full_budget_v2.txt`: current human-authored full-budget baseline mirrored from `../cheatsheet.txt`.
- `data_first.txt`: compact mined facts and magma coverage notes.

Recommended starting point for a fresh run:

1. Edit `../cheatsheet.txt` directly.
2. Keep any promoted snapshot here with a dated descriptive name.
3. Treat `distill.py` outputs as ablations unless they beat the human baseline on TRUE accuracy, hard-bucket accuracy, and dual-swap consistency.