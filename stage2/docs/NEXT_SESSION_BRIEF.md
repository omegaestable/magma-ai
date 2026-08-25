# Final brief — upload and deep sweeps

Written 2026-08-24 at the end of the final working session. Deadline:
**2026-08-31 23:59 AoE**. Read `CLAUDE.md` first; this file is the plan for
what little remains, not the state.

**The repo is in its final submission state.** Solver, package, submission
note, licence, docs and rails are all current; every prior evidence item is
discharged (judge parity on Lean 4.32.2, Solo tier-ladder, unseen-Marathon,
fixture re-pin). What remains is the upload and, optionally, deep sweeps that
could still move a handful of rows.

---

## 1. Upload checklist

1. Build fresh if anything changed: `.\stage2\solver\package_solver.ps1`
   (refuses to package on a red gate; artifact must stay ≤ 500,000 B —
   currently 472,504 B).
2. `stage2/submissions/` must contain **only** `solver.py` (no `__pycache__` —
   never import the packaged file in place).
3. Submit **`stage2/solver/SUBMISSION_NOTE.md` alongside `solver.py`** — the
   2026-08-21 rules require the methodology note for generated data payloads
   (`DISTILLED_CERTS`).
4. Walk `stage2/docs/playground-preflight.md` (updated 2026-08-24).

## 2. Deep sweeps worth running (ranked)

1. **Deployed-tier audits** (rail 12 — measure at the tier you ship, with the
   bound deployment imposes):
   ```powershell
   .\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --effort standard --row-budget 540 --out stage2/results/audit-<date>-standard.json
   .\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --effort deep --row-budget 1980 --out stage2/results/audit-<date>-deep.json
   ```
   Diff by row id against `audit-2026-08-24-goalbridge.json`. Expected: no
   change; the value is confirming the tier ladder holds at deployment bounds
   on the current code.
2. **`etp_1661_3524` long constraint run** — the one FALSE miss in 20,000.
   Orders 5–9 at ≥ 1 h/order (the deployed 45 s/order is deadline-bound with
   > 99.8% of the node budget unused). If nothing lands, the structural note
   in `CLAUDE.md`'s open-frontier section points at a permutation-aware
   search (eq1 forces right-multiplication columns to pair into inverses) or
   a bespoke infinite construction (`hard2_0027` playbook).
3. **A larger order-5 generated sample** (say 10,000 rows) through a fast
   audit — order 5 is ¼ of the score and the 4,000-row sample is at 98.0%.
   Kernel-verified TRUE certs are sound without labels; FALSE witnesses are
   oracle-checked. New misses feed item 4.
4. **The remaining frontier shapes** — 2 order-4 TRUE rows + the order-5
   tail + the 3 distilled-only families (`e2923_e1623`, `e1517_e735`,
   `e3067_e3082`). The one untried idea: seed completion with instances of
   eq1 at *goal subterms* (egg_ladder's move, in completion's engine). The
   dev tool `stage2/experiments/completion/solve_row.py` prints derivations,
   but note its README's 2026-08-24 warning: it is now *weaker* than the
   shipped engine (no bridge) — confirm any MISS against `completion_prove`.

## 3. Standing constraints (unchanged)

- One `audit_corpus.py` sweep at a time (rail 5e); never race `lake env`
  against heavy CPU; check what else is on the box before quoting wall
  clocks.
- Diff by row id, never by total (rail 2).
- Judge work needs `~\.elan\bin` on PATH (a detached process does not inherit
  it) and the vendored cwd fix (UPSTREAM.md #9) — both bit on 2026-08-24.
- A Marathon launched from an agent/terminal session **dies with that
  session's console** (exit code `0x40010004`) — it happened to the 200-row
  order-5 run at 117/200 on 2026-08-24. `answers.jsonl` is append-only, so
  recover with `--score-only` on the run dir, then run the unanswered rows
  as a second manifest; report the union as two batches. For multi-hour runs
  launch from a console that outlives the session.
- A new certificate builder owes a real-judge run (rail 3c); nothing enters
  `DISTILLED_CERTS` without judge acceptance (rail 5h).
- The ~120 KB `DISTILLED_CERTS` recovery (50 of 65 entries live-solvable)
  stays deliberately untaken: judge-pinned bytes beat a good bet while no new
  engine needs the room.

## 4. Where the evidence lives

| What | Where |
| --- | --- |
| This session's full narrative | `stage2/results/2026-08-24-final-session-upstream-sync-and-goal-bridge.md` |
| Audits (official / HF / order-5) | `stage2/results/audit-2026-08-24-goalbridge*.json`, `audit-2026-08-24-order5-4000.json` |
| Judge parity sweep | `stage2/results/judge-rejudge-v4322-b{1,2,3}.json` |
| Bridge certs judged | `stage2/results/2026-08-24-bridge-certs-judged.jsonl` |
| Marathon manifests (fresh, seeded) | `stage2/results/etp-marathon-1000-2026-08-24.jsonl`, `order5-marathon-200-2026-08-24.jsonl` |
