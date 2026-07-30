# CLAUDE.md

Authoritative entry point for this repo. Read this file; go deeper only when the
task needs it. If another doc disagrees with this file, this file wins — and fix
the other doc.

## What this is

A lab for the **SAIR Mathematics Distillation Challenge, Equational Theories
Stage 2**. Deadline **2026-08-31 23:59 AoE**.

Deliverable: one file, `stage2/submissions/solver.py`, ≤ 500 KB, no network, no
secrets, no repo-local imports. It decides implications between magma equations
and must emit **Lean 4 certificates the official judge accepts**:

- **TRUE** — a Lean proof that `equation1 ⇒ equation2`.
- **FALSE** — a finite magma satisfying `equation1` but not `equation2`
  (`finOpTable` + `decideFin!`).

`stage1/` is a finished archive. Do not start work there.

## Current measured state (2026-07-29)

| Metric | Value |
| --- | --- |
| Official sets, `fast` tier (`normal`+`hard1`+`hard2`+`hard3`) | **1650 / 1669 (98.9%)** |
| Official TRUE | **806 / 819** |
| Official FALSE | **844 / 850** |
| Remaining unsolved at `fast` | **19** (14 TRUE, 5 FALSE) |
| Oracle failures / crashes / label mismatches | **0 / 0 / 0** |
| Real-judge evidence, individually verified | 34/34 block certs, 10/10 collapse certs, **19/19** constraint witnesses |
| Offline gate | **196 passed, 2 skipped, ~45-67 s** (`-n auto`) |
| Packaged size | 354,071 bytes of 500,000 (size is not binding) |

Confirmed by a clean, isolated full audit (no concurrent jobs): **row-for-row
identical** to the pre-node-cap-fix baseline — 0 lost, 0 gained, 0 oracle
failures. An earlier contaminated run (an unrelated diagnostic audit
accidentally overlapping this one) showed 16 spurious "losses", all
budget-marginal `egg_*`/`lemma_chain` routes; reproduced each in isolation and
confirmed they solve identically — pure CPU-contention noise from testing
methodology, not a code regression. **Lesson: never run two `audit_corpus.py`
sweeps concurrently on the same machine** — the `fast`-tier headline number
is only trustworthy from an isolated run.

**Effort tier matters and is easy to conflate.** `egg_priority_bootstrap`
solves three TRUE rows (`hard2_0082`, `hard3_0131`, `hard3_0271`) at `fast` —
counted in the 1650 above. Two more rows (`hard1_0062`, `hard2_0123`, ~75 s
each) are real, judge-accepted (4.7 s / 5.3 s) fixes from the node-cap bug
below, but need `standard` effort's scaled budget (45 s × 7.5 = 337.5 s) to
finish within the wide constraint tier — they do **not** appear in the
`fast`-tier 1650, only in Solo/Marathon or a `--effort standard` sweep.

Root cause of the constraint fix: `CONSTRAINT_MAX_NODES = 60000` was cutting
`_cp_search` off *before* the time deadline that already bounds it correctly —
both rows needed ~140K search nodes. Raised to 3,000,000 (a pure safety net
now; the wall-clock deadline is the real stopping criterion).

The ranges are not vagueness — they are the measured run-to-run noise band on
identical code. Solved totals swing by up to ±7 because the FALSE search and the
general closure engines race a wall clock. **Diff by row id, never by total.**

This is **offline** evidence (proof kernel + finite-model oracles) — an upper
bound on judge acceptance, except for the 34 certificates with real judge
evidence. A cloud judge sweep is still owed before promotion.

Regenerate everything with the four commands below.

## The four commands

```powershell
# 1. Correctness gate (~47 s). Run before AND after any solver change.
.\.venv\Scripts\python.exe -m pytest stage2/tests -q -n auto

# 2. Full corpus audit (official sets; add --hf for the HF mirrors).
#    Now 25-40 min, not the ~450 s it used to be: the last-resort engines
#    (egg_collapse 40 s, egg_bootstrap, the wide constraint tier at 45 s x 7
#    orders) all run on every unsolved row. Only unsolved rows pay, so the cost
#    scales with the frontier, not the corpus. Run it once per session, not per edit.
.\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --out stage2/results/audit-<date>.json

# 3. The standing accuracy loop. Run it every session; fix whatever it pins.
.\.venv\Scripts\python.exe stage2/experiments/spotcheck.py

# 4. Package (re-runs the gate and refuses to package on failure).
.\stage2\solver\package_solver.ps1
```

Touching a certificate builder? Add a fifth: verify against the **real Lean
judge** (see below). It is the only thing that is not an upper bound.

## Rails that cost real points to relearn

1. **Never delete solver routes to "de-bloat".** Disproved with evidence
   2026-07-21: "subsumed" routes are cheap high-volume fast paths, and 29 routes
   look dead on the official sets but are live on the HF sets. File size is not
   binding. De-bloat means junk files and stale docs, never coverage.
2. **Compare TRUE counts, not solved counts, and diff by row id.** The FALSE
   search is wall-clock bounded, so solved totals carry a ±7 run-to-run noise
   band. A route change is judged by row-id diff.
3. **Local Lean acceptance of a tactic proof is not cloud evidence.** The cloud
   judge rejected a `grind` cert the local judge accepted. Broad grind scored 34
   accepted against **433 incorrect** before retirement. Certificates must be
   kernel-checkable, not tactic-backed.
3b. **A *complete* FALSE witness table is capped at order 10, but that is not the
   whole story.** The judge builds the magma with `MemoFinOp.finOpTable`, whose
   parser (`extractDigits`) keeps **one value per digit character** and computes
   `(vals.getD idx 0) % n` — so the real invariant is single-digit *cell values*,
   not order. A hand-verified `Fin 13` linear witness with entries spanning
   0..12 (`x ◇ y = 7x + 7y mod 13`) passed every offline oracle and came back
   `LEAN_REJECTED`, `decide` calling the conjunction *false* — that is what forces
   a **complete** table (entries spanning the full `0..n-1`) to order ≤ 10.
   Building the magma from a formula instead fails the proof policy
   (`HAdd.hAdd`/`HMul.hMul` not allowlisted), so `finOpTable` is the only
   sanctioned constructor. `MAX_WITNESS_ORDER = 10` covers every complete-table
   route, enforced via `table_is_renderable()` inside `table_is_counterexample`.
3b-ii. **A table with cell values deliberately restricted to 0..9 can exceed
   order 10** — confirmed against the real judge: `Fin 13`, `op(i,j)=(i+j)%10`,
   `accepted` in 78.1 s. `constraint_countermodel_wide_domain` searches this space
   (orders up to 60, `WIDE_DOMAIN_VALUE_CAP=10`). It provably **cannot** help any
   law shaped `eq1: x = F(...)` — a bare variable alone on one side is
   universally quantified over the *full* carrier, so once it exceeds 9 the
   equation demands `F(...) = x ≥ 10`, impossible for an output capped at 9.
   `_eq1_has_bare_variable_side()` detects this for free before spending any
   search. That shape is every currently-unsolved FALSE row (2026-07-29), so this
   engine ships for the *general* corpus, not today's frontier.
3c. **A sound witness is not automatically a shippable one.** Every local check
   reads the parsed Python table, so all of them are blind to rendering. When a
   witness route changes, verify against the real judge.
4. **Never gate a sound witness on an equation-pair shape.** That is a hardcoded
   benchmark id in disguise. `LARGE_WITNESS_SHAPE_KEYS` cost 30 rows to save
   0.021 ms/problem, and failed *closed* on a route that should fail open.
5. **A failed FALSE search is not evidence of TRUE**, and `models_seen > 0` is not
   the evidence you want. It must be non-zero before any speculative TRUE verdict
   (on central-groupoid rows the search inspects zero models and proves nothing),
   but it is far too weak alone: the six FALSE playground rows this fallback
   misfired on read 1050–7698 and were all genuinely FALSE.
   `constraint_search_exhausted()` is the real signal — whether the countermodel
   search finished its orders or was cut off.
5b. **Model-order difficulty is not monotonic.** On `hard2_0009` the countermodel
   search exhausted 120 s at order 7 and then found one at order 8 in 0.03 s.
   Order the search by fit to the algebra (8 and 9 first for the
   quasigroup-forcing `x = F(x, ȳ)` family), never smallest-first.
5c. **Validate any search with positive *and* negative controls before trusting a
   negative result.** A propagation bug made the constraint search confidently
   report "no countermodel ≤ 6" for every row. Rows with known witnesses (must
   find) plus TRUE rows (must find nothing) exposed it in one run.
5d. **Proof-search cost scales with goal size — so aim at a smaller law.** ETP
   pivot mining found **14 of 31 unsolved TRUE rows have `eq1 ⇒ (x = y)`**: eq1
   collapses the magma and the goal is irrelevant. `true:egg_collapse` proves 10 of
   them; the critical-pair closure proves none. When a row resists, ask what the
   smallest sufficient law is, not how to push harder on the goal.
5e. **Never run two `audit_corpus.py` sweeps concurrently.** All engines below
   `equational_closure` are wall-clock-budgeted, so 16-worker pools competing
   for the same cores starve each other and produce spurious "losses" on
   budget-marginal rows (`egg_*`, `lemma_chain`, wide constraint tiers) — 16
   of them in one measured case, 0 of them real. Always confirm a surprising
   diff with a clean, isolated re-run before trusting it; reproduce any single
   "lost" row standalone (3 clean repeats, same route) before calling it a
   regression.
5f. **A node budget alongside a per-node time-deadline check is redundant when
   harmless and wrong when it fires first.** `_cp_search`'s `CONSTRAINT_MAX_NODES
   = 60000` cut two genuine, judge-accepted witnesses (`hard1_0062`,
   `hard2_0123`, ~140K nodes each) off before their own time budget was spent.
   The dev-tool twin (`mace_finder.py`) never had this cap and found both. If a
   search is time-bounded, that is the real stopping criterion; a node cap
   should be a safety net far above measured throughput, not a second binding
   constraint.
6. **Never mix LLM calls and certificate verification in one `ThreadPoolExecutor`.**
   Verification is CPU-bound and the GIL serialises it (~10x slowdown). Use the
   two-phase shape in `llm_balanced_eval.py`: threads for network, processes for
   verification.
7. **No `--budget-tokens 0` Marathon runs** as validation or promotion evidence.
8. **Judge answer JSON contains exactly `verdict` and `code`.** Route labels go
   to stderr, never into the payload.
9. **No benchmark ids in solver policy.** Generalise findings into proof or
   witness families; pasted row lists are diagnostics and regression fixtures.

## Environment gotchas that will bite you

- **UTF-8.** Printing `◇` crashes with `UnicodeEncodeError` on Windows cp1252.
  Prefix ad-hoc scripts with `PYTHONIOENCODING=utf-8`, or run them via the
  repo's own entrypoints which set it.
- **The repo working tree is ~7.4 GB / 154k files.** `vendor/stage2-official/.lake`
  alone is 7.06 GB / 117,609 files (Lean + Mathlib build cache — needed, keep it).
  `du`/`find` at the repo root will hang. Scope every search: use `Grep`/`Glob`
  (they respect `.gitignore`) or point `find` at a subdirectory.
- **The local Lean judge works on Windows** via `elan`, despite the docs saying
  WSL/Linux only. This is the strongest verification available locally — see
  below. Caveat: `lake env` times out (30 s) under heavy CPU load, so never run
  it concurrently with a full audit.

## Verifying against the real Lean judge

The offline oracles are an upper bound; the judge is ground truth. Use it
whenever you touch a certificate builder:

```powershell
.\.venv\Scripts\python.exe stage2/experiments/judge_rows.py --ids hard2_0080,normal_0747
```

Roughly 3–8 s per row warm, against the judge's own `LEAN_TIMEOUT_SECONDS = 120`.
Judge hard limits, mirrored in the solver as `JUDGE_MAX_CODE_LENGTH` /
`JUDGE_MAX_FALSE_CERT_BYTES`: **50,000 bytes** for any certificate, **10,000** for
a FALSE certificate. Over either and the row is rejected, which is strictly worse
than skipping.

## How the solver is organised

`stage2/solver/solver.py` (~8.4k lines, single file by contract):

- `solve_problem()` dispatches through `TRUE_ROUTES` / the general engines in a
  fixed order — cheap syntactic routes first, expensive search engines last.
  **Order is load-bearing**; it is what keeps solved rows from paying for the
  hungry engines.
- The general TRUE engines, in order: `equational_closure`,
  `deep_absorption_closure`, `derived_cp_closure`, `projection_bootstrap`,
  `lemma_bootstrap`, `lemma_chain_bootstrap`, `egg_closure`, **`egg_collapse`**,
  **`egg_bootstrap`**, then the demoted `narrow_grind`.
- FALSE: named compact witnesses → structured/affine/quadratic families →
  bounded `Fin 2..3` enumeration → **`constraint_countermodel` cheap tier
  (orders 8,9,6,4,10 — most successes land in ~0.5 s)** → [TRUE engines] →
  `local_model_counterexample` (randomized `Fin 4..6` repair search) →
  **`constraint_countermodel` wide tier (45 s per order)**. Everything after the
  cheap tier runs only on rows nothing else claimed, so solved rows pay nothing.
- The two newest levers, both from the same idea (aim at a smaller target):
  `egg_collapse` proves `eq1 ⇒ (x = y)` by equality saturation, and
  `constraint_countermodel` is a Mace4-style propagation search for quasigroup
  countermodels. Together +30 official rows, 0 lost.
- `_engine_gate()` must be checked before every engine: it enforces the global
  hard deadline and the memory guard (the 2048 MB sandbox OOM-killed deep-tier
  closures measured at 5–17 GB RSS).
- `EFFORT_TIERS` / `set_effort()` scale time *and* search caps together. Solo and
  Marathon pick a tier from their real budget; `fast` is the audit default.

The single most productive idea so far: **proof-search cost scales with goal
size, so a small law that implies the goal can be reachable when the goal is
not.** That is what `universal_identity`, `projection_bootstrap`,
`lemma_bootstrap` and the LLM lemma lane all exploit.

## How correctness is enforced offline (no Lean needed)

`stage2/tests/` — deliberately shares no code with `solver.py`, so a bug in a
solver primitive cannot hide itself in the oracle.

- `ProofKernel` evaluates the restricted Lean grammar the builders emit
  (`h t1..tk`, `.symm`, `.trans`, `congrArg`, `rfl`) to the equation it proves.
  A TRUE cert passes only if it proves *exactly* `eq2.lhs = eq2.rhs`.
- A **finite-model oracle** builds magmas satisfying eq1 and refutes any unsound
  TRUE verdict. Caveat worth knowing: the trivial magma satisfies every
  equation, so `nontrivial_model_count()` is the number that matters. Laws that
  force a one-element magma (every `*_singleton`/`*_collapse` route asserts
  exactly that) have **no** non-trivial finite model, so model-checking them is
  inherently vacuous — those rows can only be verified by proof-checking.
- `check_no_banned_tactics()` rejects `grind`/`simp`/`aesop` in any emitted
  certificate except the two documented grind routes.
- `test_golden.py` pins real rows to the route family that solved them, catching
  coverage loss, engine drift and soundness loss. Regenerate deliberately via
  `audit_corpus.py` + `make_golden.py`; never hand-edit.
- `spotcheck.py` draws randomized balanced batches across 8 benchmark sets plus
  the ETP matrix (~22M labelled pairs the solver was never tuned on) and
  auto-pins any mistake into the gate forever.

## Going deeper

| Need | Read |
| --- | --- |
| Latest session detail, ranked next levers | `stage2/docs/LATEST_HANDOFF.md` |
| Operational truth, effort tiers, open rows | `CURRENT_STATE.md` |
| Route inventory | `stage2/docs/solver-route-ledger.md`, `stage2/docs/motif-cards/` |
| Offline gate design | `stage2/tests/README.md` |
| Spot-check design | `stage2/docs/spotcheck.md` |
| Before any upload | `stage2/docs/playground-preflight.md` |
| Official harness / runners | `vendor/stage2-official/`, `EVAL_WORKFLOW.md` |
| Teorth theory mining | `theory/TEORTH_WORKFLOW.md`, `theory/README.md` |
| Agent role playbooks | `AGENTS.md` |

## Known open frontier

52 official skips. TRUE-heavy: 29 TRUE misses vs 23 FALSE. Ranked next levers
(evidence-backed, see `LATEST_HANDOFF.md`):

1. Run `egg_closure` at `standard` effort — it is budget-bound at `fast`; the
   prototype reached ~8 more official rows at 20 s/row.
2. Shrink egg proof extraction — some proofs still hit the byte cap and get
   dropped, so better cycle-cutting means more shippable rows.
3. Replace wall-clock with step-count budgets, making route selection
   deterministic and letting the golden gate return to strict equality.
4. Re-run the LLM lemma lane: egg raises its ceiling (model names a law, egg
   derives it, the kernel checks it).
