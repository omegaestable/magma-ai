Base prompt: cheatsheets/v18_evidence_hierarchy.txt
Objective: create a non-collapsing revision on mixed random 5 TRUE / 5 FALSE normal warmups.
Observed failure profile across 3 fresh random warmup seeds:
- Seed0: true_accuracy=0.6, false_accuracy=0.0
- Seed1: true_accuracy=1.0, false_accuracy=0.2
- Seed2: true_accuracy=0.8, false_accuracy=0.0
- Main failure mode is false positives, not true collapse.
- The prompt keeps the TRUE fallback but often stops too early before checking the right FALSE witnesses.
- Combined distillation says top witness families in missed false cases are C0, LP, AND, OR, and RP.
- Missed structures include: generic false positives without new vars, fresh-var traps, missed LP whole-side obstruction, and missed RP whole-side obstruction.
- Preserve the private-safe rule set and the strict output format.
- Preserve the good TRUE behavior; fix the false-side undersearch.
