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
- **FALSE** — a magma satisfying `equation1` but not `equation2`. We ship finite
  ones (a Cayley table + `decideFin!`); the goal is `∃ (G : Type) (_ : Magma G),
  EquationLHS G ∧ ¬ EquationRHS G`, with no `Finite`/`Fintype` constraint.

`stage1/` is a finished archive. Do not start work there.

## Official rules, as clarified 2026-07-31

Three organizer answers on the forum, all checked against the vendored snapshot
(`vendor/stage2-official`, commit `6805e232` — the same commit under discussion):

1. **Marathon cannot call the judge.** `marathon_runner.py` spawns the solver
   with `stdin=subprocess.DEVNULL` and `marathon_proxy.py` serves only
   `/v1/chat/completions`. We already comply structurally — `main()` dispatches
   to `run_marathon` before any proxy traffic, every `judge_via_solo_proxy` call
   is inside `run_solo`, and a test now pins that. Solo keeps its judge channel.
2. **Budgets: Solo 60 min per problem, Marathon 5 min per problem on average.**
   `compression_ratio` has been withdrawn as misleading. The vendored
   `rules/evaluation.md` still says the global budget is `ratio × N × 3600 s`
   (180,000 s at N=100); `scripts/run_marathon.py` has always used a 600 s
   reference (30,000 s at N=100 = 300 s/problem), and the CLI is what the
   organizers confirmed. **Treat that vendored rules file as stale on this
   point.** The solver reads `JUDGE_MARATHON_BUDGET_SECONDS` and Solo's
   `budget.timeout_seconds` from the proxy, so nothing needed changing.
3. **Infinite countermodels are allowed.** The public judge never required
   finiteness and the organizers confirmed the rules text will follow. Unused so
   far, and correctly so: it only pays on a row with *no* finite countermodel,
   and proving `EquationLHS` over an infinite carrier means arithmetic lemmas
   instead of `decide`, under an allowlist with no `HAdd.hAdd`/`HMul.hMul`.
   Lifting the finite ceiling to 25 (rail 3b) was the cheaper reach. Revisit if a
   row resists every finite order.

## Current measured state (2026-08-12, session 2)

Every number below is from a **fresh isolated audit run this session** — the
1669/1669 that stood here had never actually been measured end to end (the
completion session re-measured only the 9 rows it closed, per instruction).

| Metric | Value |
| --- | --- |
| Official sets, `fast` tier (`normal`+`hard1`+`hard2`+`hard3`) | **1669 / 1669 (100%)** |
| Official TRUE / FALSE | **819 / 819** and **850 / 850** — both complete |
| HF mirror sets | **800 / 800 — complete** |
| `sample_200` (a 200-row **ETP** sample, disjoint from `normal`) | **200 / 200** — was 197/200; the last three local skips were closed this session |
| Remaining unsolved, anywhere local | **0** — combined offline **2689 / 2689** |
| Oracle failures / crashes / label mismatches | **0 / 0 / 0** |
| Audit wall clock, official (16 workers) | **980 s → 330 s (3.0x faster)** — a lower bound; see the caveat below |
| Audit wall clock, HF | **773 s → 344 s (2.2x)**; `hf_evaluation_order5` **611.5 s → 162.9 s** |
| Worst-case per-row latency, off the packaged artifact | `normal_0823` **252.7 s → 0.07 ms**, `hard1_0025` **217.3 s → 0.31 ms** |
| Real-judge evidence, individually verified | 99 certificates byte-pinned and **all 99 re-checked by the gate** (was 69 checked / 31 skipped). Includes **34/34 accepted this session** — 19 official + 12 HF distilled, plus 3 completion-derived |
| Real-runner evidence, this session | **Marathon `hard3.jsonl` 400/400 accepted, 0 rejected, 0 `not_attempted`, `llm_calls` 0 of a 200,000-token budget.** Was 396/400 with 4 `not_attempted` in the 08-01/03 campaign. 91 route kinds fired; 10 rows served by an exact `DISTILLED_CERTS` byte match, 5 of them distilled this session |
| Real-runner evidence, older routes | Marathon 38/38 accepted, Solo 12/12 solved, 0 rejected (2026-08-07). **Solo has no evidence for the new tier ladder yet** — it runs `deep`, so three passes, and nothing has exercised that end to end |
| Real-runner generalization | **Marathon on 200 fresh ETP rows (seed `20260812`, benchmark ids excluded): 200/200 accepted, 0 rejected, 0 `not_attempted`, 0 tokens.** Closing evidence totals **600/600 real-judge rows, 0 rejected, 0 LLM calls** |
| Spotcheck (standing loop) | **108 rows / 9 sources, 100% accuracy, 100% coverage, 0 mistakes** (seed `20260812`) |
| Offline gate | **252 passed, 2 skipped, ~24 s** (`-n auto`) |
| Packaged size | **445,233 bytes of 500,000 — 54,767 bytes (11.0%) headroom.** |
| Solver source | ~9,100 lines plus a 65-entry `DISTILLED_CERTS` block |

**2026-08-12 session 2** (`stage2/results/2026-08-12-tier-inversion-and-latency.md`)
— goal was efficiency without losing coverage, and both halves of that were met
by **row-id diff across three isolated audits: 0 lost, +3 gained**:

- **The tier inversion is fixed** (rail 12). We audit at `fast` and deploy at
  `standard`/`deep`, and more budget was making the solver *worse*: at `deep`
  with a 360 s row bound, `normal_0491` and `hard2_0162` were SKIP and now solve
  in 97.6 s / 173.9 s. `solve_problem` walks the tier ladder instead of jumping.
- **Marathon now bounds each row** (rail 13) — it previously bounded only the sum.
- **The single-rule egg engine never got the deadline fix its twin got**
  (rail 5f-v). Its 6 s probe budget was running **40 s at 11 GB RSS with zero
  polls**, straight through an armed memory guard. `normal_0823`: **252.7 s →
  1.09 s**, and a dozen `normal` rows moved from `derived_cp_closure` to the
  cheaper `egg_collapse` the probe was built to find.
- **34 certificates distilled**, all judge-accepted, taking the slow tail to O(1).
- **The last three open rows closed** by reusing the ordered-completion pipeline
  from the final nine — unchanged, no tuning, each joining in under 0.2 s.

**Timing caveat, stated so nobody over-reads the wall-clock rows.** Part of this
session's later measurement ran against heavy unrelated CPU load on the same
machine (another project's search jobs, several at 1,000+ CPU-seconds, box at
90%). The **coverage** numbers are unaffected — 0 mismatches over thousands of
rows does not come and go with load, which is rail 5e's own lesson — but the
speedup figures are **lower bounds on the improvement, not precise
measurements**. The trustworthy timing evidence is the isolated single-row
before/after probes (`normal_0491`, `hard2_0162`, `normal_0823`) and the
packaged-artifact latency row above. **Check what else is on the machine before
quoting a wall clock.**

**2026-08-11 session** (`stage2/results/2026-08-11-lemma-ladder-and-starved-search-fixes.md`):
`1658 → 1666`, TRUE `810 → 816`, FALSE `848 → 850`, diffed by row id across two
isolated audits: **+9 gained, 0 lost**, 0 oracle failures, 0 crashes.

- `true:egg_ladder` (new engine, multi-rule saturation with `have`-bound derived
  laws) closed `normal_0090`, `normal_0491`, `hard2_0162`, `hard3_0135`,
  `hard3_0204`, `hard3_0266`.
- `hard2_0092` was a named witness two guards had been hiding.
- `hard1_0062` and `hard2_0123` are **distilled**: both solve at `standard`
  (315 s / 405 s, judge-accepted), and content-keying them makes that result cost
  a dict probe at every tier. `hard2_0123`'s 405 s was more than a whole
  problem's average Marathon budget.
- **FALSE is complete at 850/850**, and `normal` and `hard1` are both complete.

**2026-08-12 session** (`stage2/results/2026-08-12-final-nine-completion.md`):
the last nine rows closed — official `1666 → 1669`, HF `795 → 800`. All nine
were derived by **ordered completion (Knuth-Bendix) with proof recording**, run
by hand per row, then judge-accepted and shipped as distilled certificates.
Equality saturation could not reach any of them at any budget; completion found
`hard2_0073`'s collapse in 0.0 s. The "no self-critical-pairs" claim that made
this family look structurally hopeless was **wrong** — see the open-frontier
section.

**2026-08-07 session** (`stage2/results/2026-08-07-distilled-library-and-egg-probe.md`):
+11 official rows from a 16-agent discovery pass over the 31 real-judge misses
of the 08-01/03 campaign. Three shipped mechanisms, all content-keyed:

- **`DISTILLED_CERTS`** — 20 judge-accepted certificates keyed by *canonical
  equation text* (`canonical_eq_text`), looked up O(1) after the singleton
  recogniser. Certificates are complete Lean files and alpha-invariant, so a
  key hit transfers across notation and set: verified emitting the same cert
  for the HF `*` spelling of an official `◇` row. Never keyed by row id
  (rail 9). Most entries came from **ETP's own implication chains** — the
  frontier is overwhelmingly collapse-shaped (`eq1 ⇒ x = y`, goal downstream),
  the rest are projection/rotation ladders transcribed from teorth Vampire
  proofs.
- **`egg_probe_route`** — a small *unscaled* early egg probe (collapse 6 s,
  row/column-constancy 2 s) placed first among the general engines. The
  campaign's dominant miss mode was scheduling, not math: egg lands these rows
  in 0.07–10 s but ran last, after the tier-scaled closure engines had eaten
  the per-row clock at `standard`/`deep`. Free gates keep it ~free elsewhere.
- **First infinite countermodel** (`hard2_0027`): carrier `Nat`,
  `op a b = if b % 2 = a % 2 then b + 1 else b - 1`, eq1 by parity (`omega`
  passes the allowlist), eq2 false at (0,1,0). Judge-accepted, 1268 bytes.
  `hard2_0093` got an order-6 *finite* witness (`S6B`) from ETP's FinitePoly
  refutation database — both FALSE holdouts are closed.

**The 1650 that stood here from 2026-07-29 was never measured.** The last full
audit before this one read 1647; the doc then added +3 for `hard2_0082`,
`hard3_0131` and `hard3_0271`, each verified individually, and wrote the sum as
if it were a measurement. This run — the first full audit since — reads 1647
again, with `hard3_0131` and `hard3_0271` landing as predicted and `hard2_0082`
not. Per-set: `normal` 996, `hard1` 68, `hard2` 189, `hard3` 394.

Treat the per-set movement (`hard2` 191→189, `hard3` 392→394) as scheduling, not
coverage: both `hard2_0082` (74.1 s standalone, `true:egg_bootstrap`) and
`hard2_0001` (1.3 s standalone, `false:dual:...:witness:S5B`) solve fine on a
quiet machine and miss under 16-way parallelism, `hard2_0001` because the cheap
witness portfolio runs on a 2 s budget that contention alone can exhaust. This
audit was **not** run on an idle machine, so its timing-derived numbers carry
less weight than the soundness ones beside them; a genuinely isolated re-run is
still owed. Nothing above depends on timing: 0 mismatches over 1863 rows does
not come and go with load.

The 2026-07-29 audit behind the previous baseline was itself confirmed clean and
isolated: **row-for-row identical** to the pre-node-cap-fix run — 0 lost, 0
gained, 0 oracle failures. An earlier contaminated run (an unrelated diagnostic
audit accidentally overlapping it) showed 16 spurious "losses", all
budget-marginal `egg_*`/`lemma_chain` routes; reproduced each in isolation and
confirmed they solve identically — pure CPU-contention noise from testing
methodology, not a code regression. **Lesson: never run two `audit_corpus.py`
sweeps concurrently on the same machine** — the `fast`-tier headline number
is only trustworthy from an isolated run, and killing a sweep does not
necessarily kill its worker pool.

**Effort tier matters and is easy to conflate.** `egg_priority_bootstrap`
solves three TRUE rows (`hard2_0082`, `hard3_0131`, `hard3_0271`) at `fast`
given the machine to itself — `hard2_0082` needs 74 s of it, which 16-way
parallelism does not give, so it is *not* in the 1647 above. Two more rows
(`hard1_0062`, `hard2_0123`, ~75 s each) are real, judge-accepted (4.7 s /
5.3 s) fixes from the node-cap bug below, but need `standard` effort's scaled
budget (45 s × 7.5 = 337.5 s) to finish within the wide constraint tier — they
do **not** appear in the `fast`-tier count either, only in Solo/Marathon or a
`--effort standard` sweep.

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

**2026-08-01/03: that cloud-judge sweep started, found two Marathon-only bugs,
and both are now real-judge confirmed fixed on all nine official + HF sets
plus a random ETP sample — the whole planned real-run campaign is complete.**
A real-judge, real-key Solo/Marathon run found the first bug this table cannot
see, because `audit_corpus.py` never arms the memory guard: `_mem_reclaims_left`
(a module-level global) was never reset per-problem inside `run_marathon()`,
so 3 memory-guard trips anywhere in a manifest permanently disabled every
general engine for every remaining problem. Real Marathon on `normal.jsonl`
scored 287/1000 against this table's 989/1000 before the fix; real Solo on the
same rows was clean throughout. A second bug surfaced fixing the first: the
Marathon deterministic loop called `solve_problem()` with zero exception
handling, so one bad row could silently kill the entire multi-hour process —
a `hard3.jsonl` rerun crashed at 283/400 with no traceback anywhere, and a
narrow fix (wrapping only the `solve_problem()` call) turned out incomplete —
`evaluation_extra_hard.jsonl` crashed the same way at 75/200 under it. Widened
to wrap the entire per-problem loop body (cache clear, memory-guard reset,
solve, answer append, bookkeeping); the rerun completed clean. **Real-judge
confirmed on all four official sets**: `hard1.jsonl` 69/69, `normal.jsonl`
988/1000 (12 not_attempted), `hard2.jsonl` 196/200 (4 not_attempted),
`hard3.jsonl` 396/400 (4 not_attempted) — **0 rejected across all 1669 rows**,
total 1649/1669 (98.8%), matching this table's offline ceiling for the first
time via the real judge. **And on all five HF mirror sets**: `hf_hard`
200/200, `evaluation_normal` 198/200, `evaluation_hard` 197/200,
`evaluation_extra_hard` 200/200, `evaluation_order5` 195/200 — total 990/1000
(99.0%), 0 rejected. **And on a 200-row random sample of the full ETP outcome
matrix** (never tuned against): Marathon 199/200, Solo 25/25, 0 rejected.
**Campaign grand total: 2863/2894 real-judge rows (98.9%), 0 rejected
anywhere.** Detail: rails 10-11 below and
`stage2/results/2026-08-01-real-judge-broad-runs-and-marathon-memory-guard-bug.md`.

Regenerate everything with the four commands below.

## The four commands

```powershell
# 1. Correctness gate (~47 s). Run before AND after any solver change.
.\.venv\Scripts\python.exe -m pytest stage2/tests -q -n auto

# 2. Full corpus audit (official sets; add --hf for the HF mirrors).
#    ~17 min wall clock on 16 workers (measured 2026-08-12). Only unsolved and
#    late-solving rows pay for the last-resort engines, so the cost scales with
#    the frontier, not the corpus. Run it once per session, not per edit — and
#    never two at once (rail 5e).
#
#    ADD --row-budget WHEN MEASURING A DEPLOYED TIER. Solo and Marathon always
#    bound a row; the audit does not unless told to, so `--effort standard/deep`
#    without it measures a solver no runner will ever be. Real Marathon at the
#    default compression ratio is `standard` with ~180 s per row on average
#    (`--effort standard --row-budget 540` models the borrow ceiling); real Solo
#    is `deep` with 1980 s. See rail 12.
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
   look dead on the official sets but are live on the HF sets. De-bloat means
   junk files and stale docs, never coverage.
   **Size was briefly binding (4.0% headroom on 2026-08-11), then was not, and
   is now worth watching again.** The package is **445,233 of 500,000 bytes —
   54,767 left, 11.0%**, after 2026-08-12 session 2 spent ~60 KB distilling the
   slow tail. That was a deliberate trade of bytes for latency, not drift: it
   took the official audit's wall clock from 980 s to 330 s. Two earlier levers
   bought the room, in this order:
   - **Simplification, −51 KB.** 37 bespoke `*_source` pattern matchers became one
     `law_matcher` plus a table row each, and the route families that wrapped them
     became factories. Source: 10,388 → 9,043 lines. This is *not* de-bloat by
     deletion: every route survives, `TRUE_ROUTES` is identical entry for entry,
     and the emitted Lean is byte-identical (proved over all 5,090 equations of the
     real domain — see the session note).
   - **Submission-only stripping, −74 KB.** `package_solver.ps1` now calls
     `stage2/solver/minify_submission.py`, which removes comments and docstrings
     and writes LF/UTF-8 without BOM. Comments stay in the working tree, where most
     of them record a measurement that cost a session; they are worth nothing to
     the judge. The stripper proves the artifact parses to the same tree as the
     source before writing, and the whole offline gate was run against the stripped
     artifact itself (201 passed) — that is what rail 1 asked for, done.
   Where the bytes are, measured 2026-08-12: `DISTILLED_CERTS` is **65 entries**
   and the dominant cost in the file. A distilled row costs anywhere from 232 B
   to 14.6 KB, so **rank distillation candidates by seconds-saved per byte, not
   by seconds** — the best trade of that session was `normal_0823` at 232 bytes
   for 253 seconds and the worst rejected one was `hard3_0134` at 34.9 KB for
   46 s. `WarnBytes` in the packager is 450,000: a "within 10% of the cap"
   alarm, not a de-bloat target.
2. **Compare TRUE counts, not solved counts, and diff by row id.** The FALSE
   search is wall-clock bounded, so solved totals carry a ±7 run-to-run noise
   band. A route change is judged by row-id diff.
3. **Local Lean acceptance of a tactic proof is not cloud evidence.** The cloud
   judge rejected a `grind` cert the local judge accepted. Broad grind scored 34
   accepted against **433 incorrect** before retirement. Certificates must be
   kernel-checkable, not tactic-backed.
3b. **Check whether a "judge limit" is actually the judge's before building a
   rail on it.** From 2026-07-29 to 07-31 this file carried a hard rail —
   "complete FALSE witness tables are capped at order 10" — that was **ours**.
   The real constraint is narrow: `MemoFinOp.finOpTable`'s parser
   (`extractDigits`) keeps **one value per digit character**, so a complete
   table above order 10 corrupts *in that shape*. The leap was concluding no
   other shape exists, from a single experiment (`fun i j => 7 * i + 7 * j`,
   rejected on `HAdd.hAdd`/`HMul.hMul`). The **notation** failed the allowlist,
   not the construction: `Nat.add`, `Nat.mul`, `Nat.mod`, `Nat.mod_lt`,
   `List.getD`, `Fin.mk` and `Fin.val` all sit under allowed prefixes. An
   inlined `List.getD` lookup is judge-**accepted** at order 13 (5.8 s), 17
   (11.2 s) and 25 (30.2 s), and `hard2_0051` — documented as unreachable — now
   ships as `false:linear:z13:7,7`. Cost of the wrong rail: every FALSE row
   above order 10, for two days. When one experiment closes a door, vary it once
   before writing the rail. (The judge's own `magmaFin` is genuinely unusable —
   a bare top-level name matching no allowlisted prefix.)
3b-ii. **What actually bounds a FALSE witness is bytes and `decide` cost, not
   order.** `MAX_WITNESS_ORDER = 25` is where the two meet:
   `table_is_renderable()` measures the rendered cert against the judge's
   10,000-byte FALSE cap, and `witness_decide_is_affordable()` bounds
   `n ** variables` — exhaustive `decide` means order 25 with a 3-variable goal
   is 15,625 applications (30.2 s of the judge's 120 s) while order 13 with 5
   variables is 371,293. Orders ≤ 10 are exempt from the cost model: that
   envelope holds every accepted cert to date and a model invented for new
   territory has no business vetoing it. Separately, a table with cell values
   restricted to 0..9 can exceed all of this on carrier size alone (`Fin 13`,
   `op(i,j)=(i+j)%10`, accepted in 78.1 s); `constraint_countermodel_wide_domain`
   searches that space up to order 60. It provably **cannot** help any law
   shaped `eq1: x = F(...)` — a bare variable alone on one side is universally
   quantified over the *full* carrier, so once it exceeds 9 the equation demands
   `F(...) = x ≥ 10`, impossible for an output capped at 9.
   `_eq1_has_bare_variable_side()` detects this for free. Those rows are exactly
   what the complete-table orders 11–25 are now for.
3b-iii. **`maxRecDepth` is driven by `n ** variables`, not by order — same axis
   mistake as the retired order-10 ceiling.** The renderer emitted
   `set_option maxRecDepth 20000` only for `n >= 7`. Verified against the real
   judge 2026-08-11 on `hard2_0092` (a 5-variable row): a `Fin 6` table is
   6⁵ = 7,776 `decideFin!` applications and came back **`LEAN_REJECTED`**
   without the option and **`accepted`** with it, byte-identical table. The same
   table against a 4-variable goal (1,296) and a `Fin 5` table against the same
   5-variable goal (3,125) are accepted either way, so the trigger sits in
   (3,125, 7,776]; `DECIDE_MAX_REC_DEPTH_APPLICATIONS = 4_096`. It stayed latent
   because nothing shipped had reached order 6 with 5 variables until the
   constraint search was allowed to (rail 5f-ii) — **a coverage fix can expose a
   rendering bug, so re-judge the rows a widened search newly reaches**, not just
   the ones you were aiming at.
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
5d-iii. **The ETP matrix can source candidates that are *guaranteed* derivable —
    use it to isolate the prover, not to find a path.** `lemma_survives_models`
    only says "not obviously refutable"; `{M : eq1 ⇒ M}` from the outcome matrix
    says **derivable**. `etp_chain.py --mode ladder` enumerates it smallest-first,
    which turns "is the candidate set wrong or is the prover weak?" into a clean
    experiment. Answer, measured 2026-08-11 on the three remaining official rows:
    the prover. Even `a ◇ a = a ◇ b` and `a ◇ b = a ◇ c` — size-6 laws the matrix
    confirms follow from `hard3_0214`'s eq1 — are unreachable in 60 s each.
    Corollary worth keeping: **walking the eq1 → eq2 path is the wrong use of the
    graph.** Every law on that path is a *consequence* of the previous one, so the
    first hop carries all the difficulty; what a ladder needs is side facts that
    follow from eq1 without implying the goal (idempotence unlocked `hard3_0266`
    and does not imply its goal at all).
5d-ii. **When a proof cannot be shortened, change the shape so it needn't be.**
    Two sessions of next-lever notes pointed at compressing `normal_0491`'s
    collapse proof (4510 extracted steps, 400 KB rendered, 46 KB cap). It is
    genuinely incompressible: cycle-cutting gets 4510 → 1548 and a full BFS over
    the replayed state sequence then finds **no** shortcut, while a
    context-factoring renderer buys only 2.4–2.9x. The reason it is that long is
    that a flat `.trans` chain over one hypothesis cannot **name** an
    intermediate law, so it re-derives the same fact at every instance — those
    1548 steps use only 38 distinct eq1 instances. One `have` makes the whole
    chain unnecessary: `true:egg_ladder` ships the row at **4755 bytes**. Before
    optimising the rendering of a proof, ask whether the certificate shape is
    what is forcing its size.
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
   constraint. **This has now bitten three times.** The 3,000,000 replacement
   bound again on 2026-08-07: `hard2_0093`'s family runs at ~22,500 nodes/s, so
   the order-6 search burned 3M nodes in 133 s *with clock remaining* and
   reported "no countermodel" for a row whose minimal witness ETP already had on
   file. Now 100,000,000. When raising such a cap, compute deadline × throughput
   for the **fastest** family, not the slowest.
5f-ii. **Rail 5f, fourth instance — and this time the gate was on the whole
    row, not the search.** `constraint_countermodel` opened with
    `if len(eq1 vars) > 4 or len(eq2 vars) > 4: return None`. `hard2_0092` has
    5 variables and an order-5 countermodel the search finds in **0.33 s /
    126 nodes**; it never got to look, for four sessions. The blow-up the gate
    guarded against is real (`_cp_propagate` walks `n ** vars` instances per
    node) but it is **per order**, so bound the instance count and skip only the
    orders that exceed it. Replaced by `n ** variables <= 20_000`, applied only
    in the wide tier — the cheap tier keeps `max_variables = 4` on purpose,
    because it runs before the TRUE engines on every row and 168 corpus rows
    with ≥5 variables are TRUE, where no witness can exist. **An order skipped
    for cost must leave the search incomplete**: `constraint_search_exhausted()`
    licenses a speculative TRUE verdict (rail 5), so "skipped" reading as
    "searched" would turn a cost cap into a wrong answer. The dev twin
    `mace_finder.py` has never had this gate, which is why the constant's own
    comment already recorded a witness the shipped solver could not claim —
    when a dev tool outperforms the solver on a row, the gap is a bug, not a
    tuning difference.
5f-iii. **One shared deadline across a portfolio starves whatever runs last.**
    `find_counterexample` ran the named tables, the structured/affine/quadratic
    families, bounded enumeration **and** the dual of all of it on a single 2 s
    deadline, dual last. `witness_check` costs `n ** variables`, so on a
    5-variable row every table test is ~n² dearer: on `hard2_0092` the primary
    passes alone spent 1.6 s of the 2 s, leaving 0.4 s for a dual pass that
    needs 0.1 s. It just fit on an idle machine and never fit under the audit's
    16-way parallelism, so the row read as a permanent skip — while the witness
    (`false:dual:false:witness:S5B`) had been in the solver for months. The dual
    now gets its own slice. Look for this shape wherever a cheap-to-expensive
    portfolio shares one clock: the last stage's budget is whatever the earlier
    ones happen to leave, which is not a budget.
5f-iv. **A deadline checked once per outer iteration is not a deadline.**
    `_egg_run_saturation` polled the clock once per e-class while *building* its
    application list. With several rules the orientation count doubles per rule
    and a free-variable product over the pool is hundreds of candidates per
    match, so a 2 s rung attempt ran for minutes and stalled a whole probe.
    Poll per unit of work, not per loop level — and note the failure mode is
    silent overshoot, which looks exactly like a hard row.
5f-v. **When you fix a bug in one engine, fix its twin the same day.** The
    2026-08-11 fix above went into `_egg_run_saturation` (multi-rule) and *not*
    into `egg_saturate_prove` (single-rule) — which is the engine `egg_probe`,
    `egg_closure`, `egg_collapse`, `egg_priority_bootstrap` and `egg_bootstrap`
    all actually run. Same site, same three defects: the poll sat on
    `for cid in classes` while `_egg_ematch` is a **recursive generator with no
    bound on the substitutions one e-class yields** (and for an op-pattern
    `classes` is every class in the graph); the `break` exited only the class
    loop so the orientation loop restarted the phase; and `apps` was unbounded
    while `EGG_EXPAND_CAP` bounds only what gets *applied*. Measured 2026-08-12
    on `normal_0823` at **`fast`** — so never a deep-tier-only bug — the probe's
    unscaled 6.0 s budget ran **40 s (6.7x) at 11,346 MB RSS with zero polls**.
    It also **defeated an armed memory guard**, because `memory_exceeded()` is
    only consulted through `deadline_expired()` / `_engine_gate()` and this loop
    called neither: a loop with no deadline poll has no memory guard either.
    Fixed by mirroring the twin plus `EGG_MAX_APPS`; the row went 252.7 s → 1.09 s
    and changed to the route the probe was built to find. A structural test now
    pins the poll in **both** engines.
5f-vi. **Localize an overshoot by sampling the stack, not by arithmetic.** This
    one was first blamed on `derived_cp_closure`, from a clean-looking argument:
    its budget is `_eff_time(8.0)` = 8 s and the row took 253 s. Wrong function —
    with the probe bounded the same row solves through `derived_cp_closure` in
    **0.4 s**. `faulthandler.dump_traceback_later(N, repeat=True)` in a probe
    process names the real site in one run, and the fix landed only because the
    measurement overruled the inference.
5g. **A fast path keyed on `.get(a) == .get(b)` fires on two missing keys.**
   `is_reflexive_problem` read `problem.get("eq1_id") == problem.get("eq2_id")`,
   so a payload carrying only equation text made `None == None` true and the
   solver answered `exact h` — a guaranteed rejection — for *every* row. The
   official pipeline always supplies both ids (`verify.py` `PROBLEM_KEYS`;
   `_resolve_problems` maps custom equation text back to catalog ids), so this
   was latent, not live. Hardened 2026-08-07 to require both ids present, plus a
   regression test. Any equality-on-optional-fields gate deserves the same look:
   absence must not read as a match.
5h. **Distillation is content-keying, not id-keying — and that is what makes it
   legal under rail 9.** `DISTILLED_CERTS` maps *canonical equation text* (the
   renaming-invariant `canonical_eq_text` of both equations) to a judge-accepted
   certificate. The key is mathematical content, so one entry covers the
   official row, its HF `*`-notation mirror, and any future ETP sample of the
   same implication — verified by test. A pasted list of row ids would cover
   exactly the snapshot and nothing else. **Never** put a certificate in this
   table that the real judge has not accepted; every entry is byte-pinned in
   `stage2/fixtures/judge_verified_certs.jsonl`.
6. **Never mix LLM calls and certificate verification in one `ThreadPoolExecutor`.**
   Verification is CPU-bound and the GIL serialises it (~10x slowdown). Use the
   two-phase shape in `llm_balanced_eval.py`: threads for network, processes for
   verification.
7. **No `--budget-tokens 0` Marathon runs** as validation or promotion evidence.
8. **Judge answer JSON contains exactly `verdict` and `code`.** Route labels go
   to stderr, never into the payload.
9. **No benchmark ids in solver policy.** Generalise findings into proof or
   witness families; pasted row lists are diagnostics and regression fixtures.
10. **A per-row safety-net counter that only decrements is a process-lifetime
    counter in Marathon, not a per-row one.** `_mem_reclaims_left` (the memory
    guard's reclaim budget) was set once at import and never reset inside
    `run_marathon()`'s loop, unlike the `clear_term_caches()` call right next
    to it. 3 memory-guard trips anywhere in a manifest permanently failed
    `_engine_gate()` closed for every remaining problem — real Marathon on
    `normal.jsonl` scored 287/1000 against this table's 989/1000, with 0
    rejected (pure coverage loss, not soundness). Invisible in the offline
    audit (never arms the guard) and in Solo (fresh subprocess per problem
    resets everything for free) — only a real, long, single-process Marathon
    run exposes it. Fixed 2026-08-01 with a `reset_memory_reclaims()` call
    alongside `clear_term_caches()`; **real-judge confirmed same day** —
    post-fix real Marathon: `hard1.jsonl` 69/69, `normal.jsonl` 988/1000, both
    0 rejected — see
    `stage2/results/2026-08-01-real-judge-broad-runs-and-marathon-memory-guard-bug.md`.
    Any future per-row budget/counter that lives at module level needs the
    same check: does it get reset where `clear_term_caches()` is, or does it
    silently accumulate across an entire Marathon manifest?
11. **One bad row must never be able to kill a whole Marathon manifest — and
    the `try/except` has to wrap the whole per-row body, not just the one
    call that looks risky.** `run_marathon()`'s deterministic loop called
    `solve_problem()` with zero exception handling — unlike the LLM lane a
    few lines below it in the same function, which already wraps each result
    in `try/except` + `continue`. A real `hard3.jsonl` rerun crashed silently
    at 283/400 with no traceback anywhere (not in solver output, not in the
    harness log, not in the Windows event log). First fix (2026-08-02)
    wrapped only the `solve_problem()` call — `hard3.jsonl`'s rerun then
    completed clean, which looked like confirmation but wasn't: a later real
    run on `evaluation_extra_hard.jsonl` crashed with the identical
    signature at 75/200, faster and past the narrow fix, with zero
    `solve:crash` entries logged — proving the exception was in
    `clear_term_caches()`, `reset_memory_reclaims()`, `append_answer()`, or
    the bookkeeping after `solve_problem()`, not the call itself. Widened
    (2026-08-03) to wrap the **entire loop body** per problem. Real-judge
    confirmed on both crash sites: `hard3.jsonl` 396/400 and
    `evaluation_extra_hard.jsonl` 200/200, both 0 rejected, 0 `solve:crash`
    entries under the wide fix. Lesson: when hardening a loop against
    one-iteration failures, don't narrow the `try/except` to "the call that
    seems most likely to fail" — wrap the whole iteration, then narrow later
    only with evidence.
12. **More budget must never mean fewer rows — walk the tier ladder, don't jump
    to it.** `EFFORT_TIERS` scales *every* engine together (`standard` 7.5x,
    `deep` 22x), so on a row whose answer lives in a **late** engine the early
    engines eat the whole per-row clock and the late one is never reached. This
    is the **tier inversion**, and it was live at the tiers we actually deploy:
    measured 2026-08-12 at `deep` with a 360 s row budget, `normal_0491` and
    `hard2_0162` were **SKIP** (each burning the full 360 s) and solve in 97.6 s
    / 173.9 s once fixed; `sample_20` is 20/20 at `fast` in 32 s but 15/20 at
    `deep` under a 45 s row bound and needs **313 s (10x)** to reach the same
    20/20. `solve_problem` now runs one pass per tier of
    `effort_ladder_to(effort_tier())`, cheapest first, returning the first pass
    that certifies (`solve_problem_pass` is the single pass). At `fast` that is
    exactly one pass, so the audit default is unchanged. **The audit could not
    see any of this**, because `audit_corpus.py` set no per-row deadline while
    Solo and Marathon always do — hence `--row-budget`. Corollary: *measure at
    the tier you ship*, and give the measurement the bound deployment imposes.
13. **A per-row deadline is not optional in Marathon.** The deterministic loop
    bounded only the **sum** (`MARATHON_DETERMINISTIC_SHARE` of the run, then
    `break`), so one slow row could spend everything left and every row after it
    was never attempted — what `not_attempted` meant in the 08-01/03 campaign.
    `marathon_row_budget` recomputes each row's fair share from what is actually
    left, lets a hard row borrow `MARATHON_ROW_BORROW = 3` rows' worth, and
    reserves `MARATHON_ROW_MIN_SECONDS` for every row still queued — **borrowing
    alone is not enough**: if every row took its full allowance the remainder
    decays geometrically and the tail is starved anyway, just later. A test
    caught that; the borrow-only version failed it. Restore the global deadline
    in a `finally` afterwards: every engine the LLM lane invokes clamps to
    `_HARD_DEADLINE`, so a stale expired bound turns every LLM candidate into
    `lemma_not_derivable_from_hypothesis` — tokens spent, zero accepts, nothing
    logged.

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

`stage2/solver/solver.py` (~9.0k lines, single file by contract):

- `solve_problem()` dispatches through `TRUE_ROUTES` / the general engines in a
  fixed order — cheap syntactic routes first, expensive search engines last.
  **Order is load-bearing**; it is what keeps solved rows from paying for the
  hungry engines.
- **The hand-recognised law families are data, not code (2026-08-11).** A family
  is `law_matcher(pattern, args, distinct=, symm=, both_orientations=)`: eq1 must
  match `pattern` up to renaming with every pattern variable landing on a bare
  equation variable, and `args` says which Lean argument each becomes. It returns
  a `LawMatch` carrying the `h ...` call and the bindings. On top of it,
  `collapse_family_route` and `projection_collapse_route` turn a whole route into
  a table row, and `submission_certificate` / `law_have` render the one
  certificate skeleton they all share. Adding a family is now one row; the law
  text in the row is the same string the certificate emits, so the two cannot
  drift. The 37 bespoke matchers this replaced were proved equivalent over the
  entire real input domain (4,694 ETP equations plus every equation in every
  benchmark set) before being deleted.
- The general TRUE engines, in order: `egg_probe`, `equational_closure`,
  `deep_absorption_closure`, `derived_cp_closure`, `projection_bootstrap`,
  `lemma_bootstrap`, `lemma_chain_bootstrap`, `egg_closure`, **`egg_collapse`**,
  `egg_priority_bootstrap`, **`egg_bootstrap`**, **`egg_ladder`**, then the
  demoted `narrow_grind`.
- **`egg_ladder` (2026-08-11) is the only engine that reasons with more than one
  law at a time.** `egg_saturate_prove_multi` saturates under a *set* of rules,
  each carrying the Lean hypothesis name that justifies it; the route derives a
  small law from eq1, binds it with `have`, and saturates again with that law in
  scope (up to 4 rungs). It exists for rows where single-rule saturation
  *terminates* short of the pivot, which no extra clock can fix. Certificates
  are the existing `lemma_chain` shape, so `check_true_lemma_chain_certificate`
  verifies every rung independently — no new oracle surface. The measurement
  that justifies it, on `hard3_0266`: single-rule egg cannot reach right
  projection in 60 s, idempotence is derivable in under 2 s, and with idempotence
  in scope right projection follows in **0.01 s with a 267-byte proof**.
- FALSE: named compact witnesses → structured/affine/quadratic families →
  bounded `Fin 2..3` enumeration → **`constraint_countermodel` cheap tier
  (orders 8,9,6,4,10 — most successes land in ~0.5 s)** → [TRUE engines] →
  `local_model_counterexample` (randomized `Fin 4..6` repair search) →
  **`constraint_countermodel` wide tier (45 s per order)**. Everything after the
  cheap tier runs only on rows nothing else claimed, so solved rows pay nothing.
  The cheap tier is capped at 4 variables and the wide tier at 6 with a per-order
  instance bound (`n ** variables <= 20_000`) — see rail 5f-ii for why those two
  numbers differ. The named-table pass also runs its **dual** on its own time
  slice rather than on the leftovers (rail 5f-iii).
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
| **Next session plan (skips, latency, closing real Marathon)** | **`stage2/docs/NEXT_SESSION_BRIEF.md`** |
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

**None, anywhere local: official 1669/1669, HF 800/800, `sample_200` 200/200 —
2689/2689 (2026-08-12, session 2).**

`sample_200`'s three holdouts (`true_2860_3458`, `true_2135_2128`,
`true_2055_2656`) were the last ones, and they closed the same way the final
nine did — **ordered completion, reused unchanged**. That is the durable result
worth carrying forward: the pipeline in
`tmp_stage2_smoke/final-nine-2026-08-12/` is row-agnostic, needed no tuning, and
joined each row in under 0.2 s against 60-90 s budgets. **A new ETP row of this
family now costs about five seconds.** If a fresh corpus ever appears, run that
before anything else — and consider productising it as a route, since it is
strictly stronger than the e-graph on this problem class.

The nine rows that stood here — `hard2_0073`, `hard3_0214`, `hard3_0314`,
`evaluation_hard_0116`/`0196`, `evaluation_order5_0014`/`0040`/`0042`/`0164` —
all now ship as judge-accepted distilled certificates. They were closed by
**ordered completion (Knuth–Bendix) with proof recording**, hand-run per row,
not by any engine in the solver. See
`stage2/results/2026-08-12-final-nine-completion.md`.

**Two claims that stood in this file were wrong, and both cost real time:**

1. ~~"eq1 for this family has **no critical pairs with itself** (the pattern has
   4 operations; every proper subterm has at most 3)"~~ — **false, and the size
   argument behind it is invalid.** A critical pair does not need the subterm to
   be *larger* than the rule's pattern; it needs the subterm to **unify** with
   it, and unification may instantiate the subterm's own variables. Orienting
   `hard2_0073`'s eq1 as `((Y ◇ (X ◇ Z)) ◇ X) ◇ Y → X` and overlapping it with
   itself at the proper subterm `X ◇ Z` (non-variable, so a legal overlap
   position) gives the mgu `X ↦ (Y' ◇ (X' ◇ Z')) ◇ X'`, `Z ↦ Y'` — and that
   single overlap unlocks the whole row. The claim was also **self-refuting**:
   with no self-critical-pair the one-rule system would be terminating and
   trivially confluent, so `x = y` could not follow — contradicting the TRUE
   label the ETP matrix already gave. Same class of error as rail 3b: a
   structural impossibility inferred from one insufficient argument.
2. ~~"neither the pivot nor any rung is provable by equality saturation at any
   budget"~~ — true as stated, but it was read as "unreachable". It only meant
   *this* search cannot get there. Completion found `hard2_0073`'s collapse in
   **0.0 s / 23 critical pairs / 10 rules**, against 1336 s of `deep`-effort
   saturation that failed. Completion is strictly stronger here because it
   **derives new rules by superposition and then rewrites with them**, whereas
   an e-graph only propagates congruence over terms it has already built. When
   a search plateaus, ask what class of inference it structurally cannot make.

Ranked next levers, updated 2026-08-11 after the ladder. Two of the four levers
that stood here are now **closed or refuted**, so read the refutations too —
they are the more useful half:

- ~~Bytes-weighted egg extraction~~ — **refuted as a lever, and worth knowing
  why** (rail 5d-ii). `normal_0491`'s chain is incompressible: 4510 → 1548 steps
  by cycle-cutting, then a full BFS over the replayed states finds no shortcut,
  and a context-factoring renderer buys 2.4–2.9x against a ~9x shortfall. The
  size was a *symptom* of a certificate shape that cannot name a lemma. Closed by
  `egg_ladder` at 4755 bytes.
- ~~Multi-rule egg saturation~~ — **built** (`egg_saturate_prove_multi` +
  `egg_ladder`), 6 official rows. But note the seeding idea in the old note was
  wrong: rungs cannot be harvested from a saturated generic-term graph, because
  every merged pair there is a direct *instance* of eq1 (640 of them on
  `hard3_0314`, all 9-byte proofs). They come from the small-law library instead.

Also refuted in the second pass, so nobody spends a session on them again:

- ~~Rungs from a wider candidate set~~ — **built and measured insufficient.**
  `goal_generalization_pivots` derives candidates from eq2's own structure and
  demonstrably finds the right one (it produces ETP's Eq267 for `hard3_0214`), and
  the row still does not close. Candidate generation was not the binding
  constraint; *proving* the candidate is. Keep the mechanism — it is cheap, sound
  and general — but do not expect more rows from widening it further.
- ~~`hard2_0073` is an extraction problem~~ — **no.** Raising the explanation depth
  limit 400 → 20,000 only moves the failure from "recursion too deep" to
  "explanation too long": the explanation is over 20,000 steps. The row also fails
  at **`deep`** effort (1336 s) with every pivot, every generalisation and the full
  rung scan.
- ~~Self-overlap helper laws~~ — **structurally impossible for this family.** eq1's
  pattern has 4 operations and every proper subterm has at most 3, so eq1 has no
  critical pairs with itself. There is nothing to seed with.
- ~~`hard1_0062` / `hard2_0123` need a bigger wide-tier slice~~ — closed a better
  way. Both solve at `standard` (315 s / 405 s, judge-accepted) and are now
  **distilled**, so they cost a dict probe at every tier. No budget change needed.

1. **The nine remaining TRUE rows need a different proof search, not more of this
   one — and that is measured, not inferred.** Three official (`hard2_0073`,
   `hard3_0214`, `hard3_0314`) and six HF. All are known-true; the vendored matrix
   confirms it. `etp_chain.py --mode ladder` supplies candidate laws the matrix
   **guarantees** are derivable from eq1, and equality saturation still cannot
   derive them: 13 candidates across three rows at 60–120 s each, plus
   `hard2_0073` at `deep` for 1336 s. eq1 also has no self-critical-pairs for this
   family. So: ordered superposition with term indexing (what found ETP's proofs),
   or hand-derived certificates through `distill_certs.py`, which judges before it
   emits and refuses anything the judge did not accept. **Do not re-try more
   clock, a wider candidate list, or another pivot heuristic** — each was tried
   and measured this session.
2. Step-count instead of wall-clock budgets, making route selection
   deterministic and letting the golden gate return to strict equality. This is
   now the *most* valuable structural item: three separate cost bugs this session
   (rails 5f-iii, 5f-iv) were all "a wall-clock bound in the wrong place".
