# V25A Master Prompt — Failure-Driven Strengthening from v24j

Date: 2026-04-07
Status: READY TO EXECUTE
Base candidate: cheatsheets/v24j.txt
Objective: Improve hard3 FALSE coverage while protecting normal safety and parse discipline.

## 0) Mandatory Read Order (do not skip)

Read these files in this exact order before any edit:

1. [README.md](README.md)
2. [CURRENT_STATE.md](CURRENT_STATE.md)
3. [AGENTS.md](AGENTS.md)
4. [.github/copilot-instructions.md](.github/copilot-instructions.md)
5. [RESTART_CHECKLIST.md](RESTART_CHECKLIST.md)
6. [EVAL_WORKFLOW.md](EVAL_WORKFLOW.md)
7. [BENCHMARK_MANIFEST.md](BENCHMARK_MANIFEST.md)
8. [RULESET.md](RULESET.md)
9. [V24I_MASTER_PROMPT.md](V24I_MASTER_PROMPT.md)

Then read current candidate + artifacts:

10. [cheatsheets/v24j.txt](cheatsheets/v24j.txt)
11. [results/v24j_failure_log.md](results/v24j_failure_log.md)
12. [results/scoreboard.md](results/scoreboard.md)
13. [results/scoreboard.csv](results/scoreboard.csv)

Then read tooling used for canonical loop:

14. [sim_lab.py](sim_lab.py)
15. [run_paid_eval.ps1](run_paid_eval.ps1)
16. [analyze_seed_failures.py](analyze_seed_failures.py)
17. [distill.py](distill.py)
18. [scoreboard.py](scoreboard.py)
19. [v21_verify_structural_rules.py](v21_verify_structural_rules.py)
20. [v22_coverage_analysis.py](v22_coverage_analysis.py)
21. [v22_mine_sound_rules.py](v22_mine_sound_rules.py)

## 1) Deep Evidence Summary from v24j

Consolidated failure ledger:
- [results/v24j_failure_log.md](results/v24j_failure_log.md)
- Total logged failures across all v24j runs: 79
- Files analyzed: 7 result payloads (4 normal + 3 hard3)

v24j runs analyzed:
- [results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_182607.json](results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_182607.json)
- [results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_192130.json](results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_192130.json)
- [results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_194143.json](results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_194143.json)
- [results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_202047.json](results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_202047.json)
- [results/sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_183950.json](results/sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_183950.json)
- [results/sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_195815.json](results/sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_195815.json)
- [results/sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_201938.json](results/sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_201938.json)

Observed spread (important):
- Normal-60 ranged from 66.7% to 93.3%.
- Hard3-40 ranged from 52.5% to 72.5%.
- Parse remained 100% in all listed runs.

Stable recurring normal FALSE misses:
- normal_0884, normal_0335, normal_0301, normal_0618

Stable recurring hard3 FALSE misses:
- hard3_0128, hard3_0151, hard3_0153, hard3_0163, hard3_0166, hard3_0218,
  hard3_0253, hard3_0254, hard3_0301, hard3_0328, hard3_0359

Additional hard3 misses in weaker runs:
- hard3_0074, hard3_0383

Hard3 TRUE fragility events (occasional):
- hard3_0028, hard3_0033, hard3_0127

## 2) Key Diagnosis

v24j fixed several execution faults in T3R by forcing rewrite-with-numbers-first and explicit E1 abort.
That produced the best observed hard3 run (72.5%).

However, failure log evidence shows the remaining dominant misses are mostly hard3 FALSE families outside T3R-only coverage.
Multiple recurring misses are known to be catchable by T3L or other 3-element separators in the v24 design notes.

Relevant grounding:
- [V24I_MASTER_PROMPT.md](V24I_MASTER_PROMPT.md)
- [results/v24j_failure_log.md](results/v24j_failure_log.md)

## 3) Proposed v25a Strengthening Method

Method name: Guarded T3L-Lite Reintroduction (Symmetric to fixed T3R)

Core idea:
1. Keep v24j structural core and T3R exactly as stability anchor.
2. Add a compact T3L-Lite rescue lane with strict guard and strict abort, mirroring the T3R discipline that worked.
3. Require full variable-to-number rewrite before any T3L evaluation step.
4. Force immediate TRUE abort if E1 does not hold under T3L assignment.
5. Evaluate E2 under T3L only when E1 holds.
6. Return FALSE only on E1 hold + E2 fail.

T3L-Lite operator definition:
- a * b = next(a)
- next(0)=1, next(1)=2, next(2)=0
- Right argument ignored.

Guard:
- Run T3L-Lite only if LP test gave E1=HOLD and no earlier structural separation occurred.

Why this is the best next move:
- It directly targets recurrent misses with matrix witnesses tied to left-translation behavior.
- It reuses the proven anti-error execution pattern from fixed T3R (rewrite numbers first + E1 abort).
- It avoids introducing hardcoded benchmark pair logic.
- It preserves canonical two-phase architecture and soundness-first policy.

## 4) Concrete v25a Editing Plan

Primary edit target:
- [cheatsheets/v25a.txt](cheatsheets/v25a.txt) (create from v24j as baseline copy)

Edit rules:
1. Keep examples A-D structure verbose (do not aggressive-golf these blocks).
2. Keep decision table unchanged.
3. Keep T3R section unchanged except tiny wording cleanup if needed.
4. Add T3L-Lite section after T3R with symmetric A/B/C/D steps.
5. Add one worked T3L-Lite example from recurrent misses (not pair-hardcoding policy text).
6. Keep byte budget under 10,240.

Do not do:
- No Jinja logic.
- No benchmark-pair lookup rules.
- No unguarded spot-check.
- No structural-test expansion beyond canonical set unless separately proven safe.

## 5) v25a Gate and Evidence Protocol

Required command path:
- [run_paid_eval.ps1](run_paid_eval.ps1)
- [sim_lab.py](sim_lab.py)

Run sequence:
1. normal_balanced60_true30_false30_rotation0002_20260403_185904
2. hard3_balanced40_true20_false20_rotation0002_20260403_185904
3. Repeat both at least twice to estimate variance

Then distill:
- [analyze_seed_failures.py](analyze_seed_failures.py)
- [distill.py](distill.py)

Promotion intent for v25a (initial target band):
- Normal mean across repeats >= 92.0%
- No catastrophic collapse run (< 88%)
- Hard3 mean across repeats > v24j mean
- Parse rate 100%

## 6) Required Deliverables for Next Agent

1. v25a cheatsheet file
2. New result json files for each run
3. Consolidated v25a failure log markdown
4. Short decision memo comparing v24j vs v25a with mean and variance

Store all outputs under:
- [results](results)

## 7) Fast Restart Checklist for Next Agent

Before coding:
1. Confirm current size of [cheatsheets/v24j.txt](cheatsheets/v24j.txt)
2. Confirm [results/v24j_failure_log.md](results/v24j_failure_log.md) exists
3. Re-read [V24I_MASTER_PROMPT.md](V24I_MASTER_PROMPT.md) theorem and guard rationale
4. Implement only minimal, reversible edits
5. Run normal gate first, then hard3

This prompt is failure-driven and evidence-anchored. Do not skip the read order.
