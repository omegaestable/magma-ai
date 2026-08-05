# Latest Handoff

Updated: 2026-08-03 (real-judge broad runs — two Marathon-only bugs found, both fixed and real-judge confirmed campaign-wide: 2863/2894 rows, 0 rejected. Campaign complete).

This is the short team-memory note for the current Stage 2 solver state. Use the result files for detailed evidence and `tmp_stage2_smoke/` only for raw artifacts.

**Start at `CLAUDE.md`** for current numbers, commands and rails; this file is the
dated session log.

## 2026-08-01/03: real Solo/Marathon runs found two Marathon-only bugs — CAMPAIGN COMPLETE, 2863/2894 real-judge rows, 0 rejected anywhere (newest — read first)

Full detail: `stage2/results/2026-08-01-real-judge-broad-runs-and-marathon-memory-guard-bug.md`.

First-ever session running the packaged solver through the **real** official
harness at scale (real Lean judge, real proxy, real `openai/gpt-oss-120b` via
OpenRouter) instead of the offline oracle path every prior baseline in this
file used. It found something the offline path is structurally blind to.

- **Real Solo is clean.** `sample_20` 20/20, `hard1` full 69/69, 0 LLM calls
  needed for either, 0 judge rejections anywhere. Matches/exceeds offline
  expectations.
- **Real Marathon is not.** `normal.jsonl` scored **287/1000** (offline `fast`
  baseline: 989/1000); `hard1.jsonl` scored **31/69** against the *same rows*
  Solo had just solved 69/69. Both 0 rejected — pure coverage loss.
- **Root cause, confirmed:** `_mem_reclaims_left` (module-level global,
  `solver.py` ~4752) only ever decrements and is never reset per-problem
  inside `run_marathon()`'s loop. After 3 memory-guard trips *anywhere in the
  whole manifest*, `_engine_gate()` (~7338) permanently fails closed for every
  remaining problem, silently disabling `equational_closure`,
  `derived_cp_closure`, every `egg_*` engine, `lemma_chain_bootstrap`, the
  FALSE `constraint_countermodel` tiers — everything except the cheap ungated
  syntactic routes checked before the first gate (`singleton` alone was
  243/287 of `normal.jsonl`'s solves). `try_reclaim_memory()` logs nothing, so
  this is completely invisible except via route-count skew.
- **Why the offline 1650/1669 baseline never caught it:** `audit_corpus.py`
  never arms the memory guard at all. **Why Solo never hits it:** one fresh
  subprocess per problem resets all module state, `_mem_reclaims_left`
  included, every single row. Only a real, long, single-process Marathon
  manifest exposes it.
- **Fix shipped:** new `reset_memory_reclaims()`, called alongside the
  existing per-problem `clear_term_caches()` in `run_marathon()`'s
  deterministic loop. `pytest stage2/tests`: 202 passed, 2 skipped, no
  regression. Repackaged, 364,728 bytes.
- **Real-judge revalidation: CONFIRMED.** Post-fix, run to completion:
  `hard1.jsonl` Marathon **69/69 accepted, 0 rejected** (full recovery,
  matches Solo on the identical rows); `normal.jsonl` Marathon **988/1000
  accepted, 0 rejected**, 12 `not_attempted` — a real, single, ~7.3-hour
  Marathon process, essentially matching the 989/1000 offline ceiling. Route
  mix fully restored (`derived_cp_closure`:142, `equational_closure`:27,
  `egg_closure`/`egg_collapse` firing, 30+ FALSE witness families) versus the
  pre-fix near-total collapse into `true:singleton` alone. One unrelated infra
  hiccup along the way: the first `normal.jsonl` scoring pass crashed on a
  `lake env` 30 s timeout (documented gotcha, triggered after 7.3 h of solver
  CPU load) — recovered with `scripts/run_marathon.py --score-only` against
  the already-written `answers.jsonl` instead of re-running the solve.
  **`hard2.jsonl` also confirmed: 196/200 accepted, 0 rejected, 4
  `not_attempted`.**
- **A second bug, found getting `hard3.jsonl` to a full run.** The first full
  rerun attempt crashed silently at 283/400 — no traceback anywhere (not the
  solver's own output, not the harness log, not the Windows event log).
  Root cause: `run_marathon()`'s deterministic loop called `solve_problem()`
  with **zero exception handling**, unlike the LLM lane a few lines below it
  in the same function (which already wraps each result in `try/except` +
  `continue`). One bad row could kill the entire multi-hour process, even
  though every row solved before it was already safely on disk. Fixed by
  adding the same `try/except` + `log_stderr({"route":"solve:crash",...})` +
  `continue` pattern — **but only around the `solve_problem()` call itself**.
  Rerun under that narrow fix completed clean (`hard3.jsonl` 396/400, 0
  `solve:crash` entries), which looked like confirmation but was
  incomplete: a later real run on HF `evaluation_extra_hard.jsonl` crashed
  the **identical** way at 75/200, faster, still zero `solve:crash` entries —
  proving the exception was somewhere else in the loop (`clear_term_caches()`,
  `reset_memory_reclaims()`, `append_answer()`, or the bookkeeping), not the
  `solve_problem()` call. **Widened** the `try/except` to wrap the entire
  per-problem loop body. Reruns of both crash sites then completed clean
  under the wide fix: `hard3.jsonl` 396/400, `evaluation_extra_hard` 200/200,
  both 0 rejected, 0 `solve:crash` entries.
- **All four official sets real-judge confirmed: 1649/1669 (98.8%), 0
  rejected across every single row.** First time the real Marathon track has
  matched the offline ceiling, not just the offline oracle.
- **All five HF mirror sets real-judge confirmed, 0 rejected anywhere:**
  `hf_hard` 200/200 (0 tokens — fully deterministic), `evaluation_normal`
  198/200, `evaluation_hard` 197/200, `evaluation_extra_hard` 200/200,
  `evaluation_order5` 195/200. Total 990/1000 (99.0%).
- **All nine official + HF sets: 2639/2669 (98.9%), 0 rejected anywhere.**
- **200-row random ETP sample (never tuned against this distribution), also
  confirmed, 0 rejected:** Marathon 199/200, Solo 25/25 — built from
  `data/exports/general_outcomes.json.gz`, seed `20260731`.
- **Campaign grand total: 2863/2894 real-judge rows (98.9%), 0 rejected
  anywhere.** Every planned real-run item is done — no fixed next real-run
  item is queued. Non-mandatory follow-ups (promotion housekeeping, a
  larger/differently-seeded ETP sample, minor infra hardening) are in the
  results doc's "Next session" section.
- **Zero soundness issues anywhere, before or after either fix.** Every real
  judge verdict across this whole campaign — pre-fix and post-fix, official
  and HF, both crash sites — was `accepted` whenever it reached the judge at
  all. The entire measured gap, throughout, was always coverage or crashes,
  never a wrong answer.
- Secondary: real Solo per-row latency is genuinely high at its `deep` effort
  tier (many rows 80-900+ s even when solved) — expected given the full
  60-minute budget, not a bug. `hard1_0062`/`hard1_0025` (previously flagged
  needing the node-cap fix) solved deterministically here with no further
  changes.

## 2026-07-31: official rules review, and the order-10 rail retired

Triggered by three organizer clarifications on the playground forum. Two were
no-ops for us; reviewing the third is what exposed a self-inflicted ceiling.

**The rule changes** (all checked against the vendored snapshot, same commit
`6805e232` the forum thread cites — see `CLAUDE.md` for the full statement):

- *Marathon cannot call the judge.* Already compliant; `stdin` is `DEVNULL` and
  the marathon proxy has no judge route. Now pinned by an AST-level test that
  keeps every proxy call inside `run_solo`.
- *Solo 60 min/problem, Marathon 5 min/problem average; `compression_ratio`
  withdrawn.* No code change — budgets are read from the environment, never
  assumed. The vendored `rules/evaluation.md` is **stale** here (it still says
  180,000 s at N=100 where the real figure is 30,000 s); noted in `UPSTREAM.md`.
- *Infinite countermodels are allowed.* Not used yet — see below for why the
  finite route was the cheaper reach.

**The real finding.** Chasing what "no finiteness constraint" opens up meant
re-reading the FALSE certificate policy, and the 2026-07-29 conclusion that
`finOpTable` is the only sanctioned magma constructor did not survive it. That
rested on one experiment — `fun i j => 7 * i + 7 * j`, rejected on
`HAdd.hAdd`/`HMul.hMul`. It was the *notation* that failed the allowlist.
Written with `Nat.add`/`Nat.mul`/`Fin.mk`/`List.getD`, all under allowed
prefixes, the real judge **accepts** the same construction:

| Shape | Order | Result |
| --- | --- | --- |
| `fun i j => 7 * i + 7 * j` | 13 | `DISALLOWED_DECLARATIONS` (reproduced) |
| `finOpTable` complete table | 13 | `LEAN_REJECTED` (reproduced) |
| `magmaFin` (judge's own List constructor) | 13 | `DISALLOWED_DECLARATIONS: magmaFin` |
| **inlined `List.getD` table** | **13** | **accepted, 5.8 s** |
| **inlined `List.getD` table** | **17 / 25** | **accepted, 11.2 s / 30.2 s** |
| **named-arithmetic formula** | **13** | **accepted, 6.0 s** |

Shipped from that: `false_certificate_list`, `MAX_WITNESS_ORDER` 10 → 25,
`witness_decide_is_affordable()` (cost is `n ** variables`, not order), and
`large_linear_family_tables()` for orders 11–25. `hard2_0051`, called
unreachable in the v4b note below, now solves as `false:linear:z13:7,7` and is
judge-accepted in 5.6 s end-to-end.

Orders ≤ 10 keep the `finOpTable` shape byte-for-byte, so no working row changed
shape — verified by test and by 4 judge-accepted legacy controls.

Why infinite countermodels stayed on the shelf: they only pay where *no* finite
model exists, and they trade `decide` for arithmetic lemmas under an allowlist
that excludes `HAdd.hAdd`/`HMul.hMul`. Lifting the finite ceiling was cheaper
and it was the actual blocker. Revisit if a row resists every finite order.

## 2026-07-29 v4b: wide-domain witnesses + a node-cap bug (newest — read first)

Direct follow-up to v4 below. Full detail:
`stage2/results/2026-07-29-v4b-wide-domain-and-node-cap.md`.

User pushed back on "unreachable" for `hard2_0051`/`hard2_0093`/`hard2_0123`.
The pushback was partly right:

- **The order-10 claim was imprecise.** `finOpTable`'s real invariant is
  single-digit *cell values*, not order — order ≤ 10 is only a corollary for a
  *complete* table. Confirmed against the real judge: `Fin 13`,
  `op(i,j)=(i+j) mod 10`, `accepted` in 78.1 s. Shipped as
  `constraint_countermodel_wide_domain` (orders up to 60, value-capped at 10),
  end-to-end validated.
- **But it provably cannot help this frontier.** Every unsolved FALSE row has
  `eq1: x = F(...)` — a bare variable alone on one side, universally quantified
  over the *full* carrier. Once it exceeds 9, `F(...) = x >= 10` is impossible
  for an output capped at 9. `_eq1_has_bare_variable_side()` detects this for
  free; all 5 remaining FALSE misses have this shape.
- **Chasing it anyway found a real bug.** A decisive 120 s/order search (vs the
  40 s used before) found genuine order-8 witnesses for `hard1_0062` and
  `hard2_0123` — but the *shipped* solver still missed them. Cause:
  `CONSTRAINT_MAX_NODES = 60000` cut the search off before the (already
  correct) wall-clock deadline. Raised to 3,000,000 — a pure safety net now.
  **Both now judge-accepted**, 4.7 s / 5.3 s.
- **The other 3** (`hard2_0027`, `hard2_0051`, `hard2_0093`) ran an uncapped,
  721–737 s search across every order and found nothing — much stronger
  negative evidence, though not a formal proof of non-existence.

## 2026-07-29 v4 coverage push

Triggered by 16 playground `TRUE INCORRECT` rows from v3. Full detail:
`stage2/results/2026-07-29-v4-coverage-push.md`.

**Official `1616 → 1650/1669` (98.9%), TRUE `788 → 806`, FALSE `828 → 844`,
0 rows lost, 0 oracle failures, 0 crashes, 0 label mismatches. HF `782 → 788`.**
19 official rows remain open at `fast` tier (14 TRUE, 5 FALSE).

- **The six FALSE-labelled reported rows were guaranteed misses**: the Solo grind
  fallback answered `true` on rows labelled FALSE, at 363–847 s each.
  `hypothesis_models_seen()` read 1050–7698 on them, so the existing
  `skip_no_model_evidence` guard passed them through. **`models_seen > 0` is not a
  TRUE signal**; `constraint_search_exhausted()` is the one that means something.
- **New: `false:constraint_fin*`** — Mace4-style propagation search. The whole
  FALSE portfolio was blind to `x = F(x, ȳ)` laws, which force *quasigroups*:
  random tables never satisfy them and the witness usually sits at order 8.
  **17 of 22 unsolved FALSE official rows solved, 17/17 judge-accepted**
  (313–426 bytes). Two design points carry it: propagate at the **root** only
  (the first version assigned the innermost cell and reported "no countermodel"
  everywhere), and use an **order schedule** — `hard2_0009` exhausted 120 s at
  order 7 and took 0.03 s at order 8.
- **New: `true:egg_collapse`** — ETP pivot mining found **14 of 31 unsolved TRUE
  rows have `eq1 ⇒ (x = y)`**: eq1 collapses the magma, so the goal is
  irrelevant. The CP closure derives none of them; egg derives **10**, all
  kernel-verified, **10/10 judge-accepted** (1.2–34 KB).
- **New: `true:egg_bootstrap`** — the same move over the 601-entry lemma library,
  free gates first so egg is only paid for on a law that closes the goal. +5 rows.
- **HARD RAIL FOUND: FALSE witness order ≤ 10.** `finOpTable`'s parser
  (`extractDigits`) keeps one value per *digit character*, so a cell holding `10`
  becomes two cells. A hand-verified `Fin 13` linear witness
  (`x ◇ y = 7x + 7y mod 13`) passed every offline oracle and came back
  `LEAN_REJECTED` with `decide` calling the conjunction *false*. Formula-based
  magmas fail the proof policy (`HAdd.hAdd`/`HMul.hMul` unlisted). Now enforced by
  `MAX_WITNESS_ORDER` + `table_is_renderable()` inside `table_is_counterexample`,
  mirrored in `oracles.check_false_certificate`, and pinned by a test. **My first
  version of the constraint search used orders 12 and 16** — it would have emitted
  certificates that pass every local check and fail in the field.
- **LLM lane works but is not needed at inference time.**
  `stage2/experiments/llm_lemma_egg.py` (model names the pivot, egg derives it,
  kernel checks it): 4/21 open TRUE rows, **0 kernel rejects**, 34k tokens. Every
  law it found is already a library entry and `egg_bootstrap` finds all four
  deterministically. Keep it as a discovery tool.
- **New dev tools**: `mace_finder.py` (countermodel search + controls),
  `etp_pivots.py` (decodes the ETP 4694² outcome matrix; agrees with benchmark
  labels 2269/2269), `llm_lemma_egg.py`, `judge_rows.py`.
- **Process rail:** do not edit `solver.py` while a pool-based audit is running —
  a worker imported a half-renamed module and produced a spurious crash row.

## 2026-07-29 QA pass

No new coverage attempted. The goal was to make existing coverage *provably*
correct and the repo cheap to improve. Full detail:
`stage2/results/2026-07-29-qa-pass-soundness-and-refactor.md`.

- **The documented baseline reproduced exactly** on a clean run: official
  `1617/1669`, TRUE `790`, FALSE `827`, **0 oracle failures, 0 crashes**, 430 s
  on 16 workers. `spotcheck.py` 72 rows / 9 sources: 100% accuracy. The evidence
  base in this repo is trustworthy.
- **`grind` was still inside a deterministic route** —
  `true:right_projection_collapse:left_pair_tail`, via
  `right_projection_from_2788_block()`, with a 5M `maxHeartbeats` bump. Replaced
  by a derivation from eq19/eq22/eq34 that were already in the certificate:
  with `P := X0 ◇ (X0 ◇ X0)`, eq19+eq34 give `∀t, t ◇ P = X0`, hence
  `P ◇ P = X0`, and eq22 P P rewritten by that gives `(P ◇ X0) ◇ P = P`, which
  the universal fact closes to `P = X0`. **Judge-verified: accepted,
  37.0 s → 4.8 s.**
- **New rail: the solver must obey its own banned-tactic rule.**
  `sanitize_lean_code` policed only *LLM* output; that asymmetry is what hid the
  above. `check_no_banned_tactics` now runs per row in the golden gate and the
  audit, plus a static scan of the solver source.
- **The model oracle was vacuous on 28% of rows** (536/1889) because
  `model_battery` pre-seeded the trivial magma, making its `Fin 3` escalation
  unreachable dead code — and every equation holds in `Fin 1`. Now keyed off
  `nontrivial_model_count()` with exhaustive `Fin 3` then a budgeted order-4/5
  hill-climb (finds a real order-4 central groupoid in ~0.1 s).
- **Know this limit:** for laws that force a one-element magma — what every
  `*_singleton`/`*_collapse` route asserts — **no non-trivial finite model exists
  at any order**, so model-checking them proves nothing by construction. Those
  rows are only verifiable by proof-checking. A green `model_checked` there is
  not evidence; the audit now says `model_check_vacuous`.
- **All 34 kernel-unverifiable certs are judge-verified and pinned.** 10 of them
  previously had *no* offline verification at all. **34/34 `accepted`** by the
  real judge, pinned byte-for-byte in
  `stage2/fixtures/judge_verified_certs.jsonl`, guarded by
  `test_judge_verified.py`. Regenerate with `stage2/experiments/judge_rows.py`.
- **The local Lean judge works on Windows** via `elan` (docs said WSL/Linux
  only). This was tribal knowledge and is the strongest local evidence source;
  `judge_rows.py` makes it one command. `lake env` times out under load — never
  race it against a full audit.
- **Size caps were 2x the judge's** (`MAX_LEAN_CODE_BYTES` 100_000 vs the judge's
  50_000; FALSE 20_000 vs 10_000). Now derived from `JUDGE_MAX_*` constants. No
  row was affected — latent hole closed, not rows recovered.
- **`solve_problem`: 510 → 104 lines**, routes in a `TRUE_ROUTES` table, order
  verified mechanically against `git show HEAD`. The old copy-paste shape is what
  hid two defects: `narrow_grind` ran with **no `_engine_gate()`** (so it fired
  after a memory trip or passed deadline), and a duplicate
  `sandwich_left_projection_route` call was unreachable. Adding a route is now
  one line.
- **Gate: 146 s → 47 s** (`-n auto`), 196 → 237 tests. **CI added** — nothing
  enforced the gate outside `package_solver.ps1` before. `ruff check .` clean.
- **`CLAUDE.md` is the new entry point.** The mandated cold-start read was ~36k
  tokens across 13 mutually contradictory files; `AGENTS.md` advertised
  `1201/1669` and a 138,939-byte package as current.
- **Next levers unchanged** (see "Recommended Next Steps"): egg at `standard`,
  shrink egg extraction, step-count budgets, LLM lemma lane.

## 2026-07-23 session 2

A real playground Solo run returned eight `TRUE INCORRECT` rows at 400–630 s
each, all submitting the `fallback:unsolved_grind` cert. Seven were labelled
FALSE, so that verdict could never be accepted. Full detail:
`stage2/results/2026-07-23-s9a-witness-gate-and-fallback-evidence.md`.

- **Root cause: `LARGE_WITNESS_SHAPE_KEYS` pinned the 9-element witness `S9A`
  to the exact `(eq1, eq2)` pair it was discovered on.** All seven rows share
  `eq1_id = 168` (central groupoid) with different goals, so the gate skipped
  the one witness the solver owned for them. `S9A` refutes all eight. The
  guard bought **0.021 ms/problem**. It is deleted; every named table is now
  tried on every problem. A full equation-pair shape key is a benchmark id in
  disguise — do not reintroduce one (Operational Note 2).
- **Result: HF `754 → 783` (+30 / −1 by row id), all 30 `false:witness:S9A`;
  official sets bit-identical (`1617`, TRUE `789`, +0/−0); 0 oracle failures.**
  `hf_evaluation_extra_hard` goes `170/200 → 200/200` and `185.3 s → 24.7 s`.
- **`Fin 9` `decideFin!` certs are judge-validated.** This shape had no prior
  real-judge evidence, so 5 were run through `judge.verify.verify_answer`:
  **5/5 `accepted`**, 14–16 s warm against the judge's 120 s Lean timeout,
  462-byte certs against the 10 KB FALSE cap. Kernel reduction transfers;
  see [[grind-local-accept-is-not-cloud-evidence]].
- **"No counterexample found" now has to mean something.**
  `hypothesis_models_seen()` counts models of `eq1` the FALSE search actually
  inspected. On an `Eq168` row it is **2** — orders ≤ 3 hold *zero* models and
  the structured/affine/quadratic families hold zero, so the search was
  vacuous. `run_solo` no longer submits a speculative `verdict: "true"` when
  the count is 0 (`fallback:skip_no_model_evidence`).
- **`evaluation_extra_hard_0190` is closed** — it was recorded on 2026-07-22 as
  an open playground FALSE miss with "no witness ≤ 4 exists". True, but the
  witness lives at order 9 and `S9A` is it; judge-accepted in 14.3 s.
- **Still open: `evaluation_hard_0116`** (TRUE, `models_seen = 3691`). Real
  frontier row, not a bug; the grind lottery ticket is kept there.
- **Noise amendment:** `evaluation_hard_0178` flipped solved→skip→solved across
  three runs of identical code (45.7 s / 17.2 s / 10.0 s). Budget-marginal TRUE
  routes like `projection_bootstrap` are *not* run-to-run stable, so diff row
  ids, not TRUE totals.

## 2026-07-23 session 1

**Shipped a new engine, `true:egg_closure`** — ground equality saturation
with kernel-checkable proof extraction, the mechanism four prior sessions were
missing. Full detail:
`stage2/results/2026-07-23-spotcheck-batches-and-egg-frontier-study.md`.

- **Result: official TRUE `773 → 789` (+16), HF TRUE `379 → 384` (+5), zero
  oracle failures across all 2,689 problems.** Attribution: `egg_closure`
  fired 13 official + 4 HF times; **15 of those are previously-`skip` rows
  (genuine new coverage)**, the rest of the +21 are lemma_chain/derived_cp
  flipping on the timing band. These are `fast`-tier (10 s/row) numbers; Solo
  runs egg at `standard`/`deep` (75–220 s), where the prototype reached 21–23
  of these rows, so the deployed Solo ceiling is higher.
- **Why this was the right lever (root cause).** The oracle-pivot experiment
  handed the CP closure the exact ETP-verified intermediate laws as
  lemma-chain helpers; it **failed every genuine explicit edge**. So candidate
  generation was never the constraint — closure *mechanism* was. Do NOT widen
  the enumerated lemma library; that is measured-dead. The ETP's own proofs of
  these edges are MagmaEgg (egg) proofs that instantiate eq1 at composite
  ground terms over the goal's variables — the move egg makes and CP
  unification cannot.
- **How the engine stays sound.** A ground e-graph + congruence closure over
  goal-variable terms; eq1 applied by e-matching. A proof forest records the
  `h`-instance behind each merge; when the goal sides merge, the explanation
  is extracted, cycle-cut + greedily bridged to a short chain, and **every step
  is replayed syntactically against the concrete term before a character is
  emitted** — a bug anywhere fails closed (route returns None). Certificate is
  a balanced `.trans` tree of `congrArg`-wrapped `h`-instances: plain
  `exact_expr`, checked by the existing `ProofKernel`, **no new oracle surface**.
- **Validated four ways:** offline kernel 21–23/67 frontier rows; **real local
  Lean judge 8/9** on a 700 B–48 KB size ladder (the 1 failure was oversized —
  the real judge caps code at 50 KB, not the solver's 100 KB; route now caps
  certs at 49.5 KB); **0/25** ETP-FALSE negative controls through the full
  extract+render path; and **real end-to-end rounds** (`real_rounds.py`,
  solve→`verify_answer` through Lean): **69/69 emitted certs accepted, 0
  rejected, 0 wrong verdicts** across a broad mixed round (50) and the egg
  frontier — **18/18 egg certs Lean-accepted**, 480 B–34.9 KB.
- **Placement & gate discipline.** Route is last among TRUE engines (pure
  addition, honors `local_deadline`/`memory_exceeded`). Excluded from the
  golden fixture like `narrow_grind` — it is wall-clock nondeterministic and
  last, so an egg-only row can time out under load and read as a false coverage
  regression; its certs are kernel-checked in every audit/spotcheck instead.
- **`make_golden` now groups by route family, not full label** (2026-07-23).
  The port's golden regen briefly captured a `lemma_chain:enum319` row that
  solved at its 10 s ceiling and then flaked the gate; full-label grouping had
  force-pinned that marginal singleton. Family grouping pins the fastest
  representative per engine instead. Fixture is now 136 entries / 52 families;
  all re-solve under 8-worker parallel stress.
- **Standing loop before the port: 4 spotcheck batches, 358 rows, 100%
  accuracy, 0 pinned.** Prototype + drivers kept at
  `stage2/experiments/egg_saturation.py` / `egg_prove.py` / `egg_real_rows.py`
  / `egg_false_controls.py`.
- **Next levers (ranked):** (1) egg is budget-bound at `fast` — a `standard`
  Solo sweep should land the remaining ~8 prototype-provable rows; (2) shrink
  extraction further (some proofs still hit the 46 KB cap and are dropped —
  smaller certs = more shippable rows); (3) re-run the LLM lemma lane, whose
  ceiling egg now raises (model names a law, egg derives it).

## 2026-07-22 session 4

A real playground Solo run exposed 13 `TRUE INCORRECT` + 1 `ERROR`; all 14
were root-caused and fixed or mitigated in one pass — full story in
`stage2/results/2026-07-22-playground-failure-fixes.md`. Highlights: the
ERROR was an **OOM kill** (2048 MB sandbox vs 5–17 GB deep-tier closures) —
Solo now runs a global hard deadline + armed memory guard + insurance judge
call + guaranteed grind fallback; `true:narrow_grind` was **judge-rejected in
the field** and is demoted behind kernel-verified engines; the new
**enumerated lemma library + multi-hop `lemma_chain` route** (free CP-rule
helpers, iterative harvest, direct-goal fallback) took official TRUE
**706 → 773** and HF TRUE **357 → 379** with zero lost rows and a
multi-hypothesis kernel check for every chain cert.

## Current status

- **Offline score** (`fast` tier, oracles; regenerate via `audit_corpus.py --all`/`--hf`):
  official **1617/1669** (TRUE **789-790/819**), HF **783/800** (TRUE **383**).
  (The `754` previously written here predated the same session's own S9A fix,
  documented two blocks above as `754 -> 783`.)
  **Zero oracle failures across all 2,689 problems.** Offline is an upper
  bound — a cloud judge sweep is still owed before promotion.
- **Packaged**: `stage2/submissions/solver.py` (repackaged 2026-07-23 with the
  egg engine; ~332 KB source, limit 500 KB).
  Gate: `pytest stage2/tests`, no Lean. `package_solver.ps1` runs it and
  refuses to package on failure.
- **The standing loop**: `python stage2/experiments/spotcheck.py` — randomized
  cross-source accuracy hunt; auto-pins any mistake into the gate. Run it, fix
  what it pins. See `stage2/docs/spotcheck.md`.
- **Levers that keep paying**: the "small law is a smaller search target"
  routes (`true:universal_identity`, `true:projection_bootstrap`,
  `true:lemma_bootstrap`) plus an LLM lemma lane, and now **`true:egg_closure`**
  — the equality-saturation engine that reaches the ETP's MagmaEgg proofs the
  CP closure structurally cannot. The lemma-derivability wall is solved by egg;
  see the session block above.
- **Never delete solver routes to "debloat"** — 2026-07-21 disproved that with
  evidence (subsumed routes are cheap fast paths; 29 look dead on official but
  live on HF). Debloat = junk files and stale docs only.

## 2026-07-22 session 3

Focus: a randomized cross-source **spot-check harness** to hunt solver mistakes
over many sessions, heading toward 100% accuracy. Full design:
`stage2/docs/spotcheck.md`.

- **`stage2/experiments/spotcheck.py`** draws balanced random batches (default
  5 TRUE + 5 FALSE per source) across the 8 distinct benchmark sets plus a new
  **`etp`** source: the Equational Theories Project matrix in `data/exports/`,
  ~22M validated labelled pairs the solver has never been sampled against.
- **Correction worth knowing:** the HF `normal/hard*` files are notational
  mirrors (`*` vs `◇`) of the official sets — zero new content. There are only
  2,669 distinct benchmark problems and the audit already covers them all. The
  ETP matrix is the genuinely new, essentially unlimited source (agrees with
  2,269/2,269 in-range benchmark rows).
- Every row runs through the existing `audit_corpus.audit_row` (solve + offline
  oracles + label cross-check). A caught mistake — wrong verdict, unsound
  certificate, or crash — is auto-pinned to the git-tracked
  `stage2/fixtures/spotcheck_failures.jsonl` and replayed forever by
  `test_spotcheck_regressions.py` inside the pre-package gate. A skip is safe
  (coverage, not accuracy).
- A gitignored coverage ledger steers each batch toward untested rows, so
  repeated runs fan out across the corpus; `--pure-random` disables it.
- **Put to work same session:** 13 batches + an ETP-only sweep + a
  `standard`-effort hard-set sweep = **1,189 distinct rows tested, 100% accuracy
  on every batch, 0 mistakes, nothing pinned** (216 of them from the novel `etp`
  source). Also swept the one model-check-only surface (`other`-shape TRUE
  certs) with a heavy exhaustive-Fin2/Fin3 + 4,000-sample-Fin4 battery. Detail:
  `stage2/results/2026-07-22-spotcheck-baseline-and-soundness-sweep.md`.
  `pytest stage2/tests`: 273 passed, 2 skipped (the spot-check fixture starts
  empty).
- Soundness surface is fully mapped: FALSE certs are exhaustively re-verified
  and TRUE `exact_expr`/`singleton`/`lemma` are proof-kernel exact (zero gap);
  only TRUE `other`-shape (`*_block` combinator proofs) is model-check-only, and
  that is what the heavy Fin4 sweep targets (0 unsound in 20 certs / 463 rows
  before it was stopped).
- **Shipped fix — audit/spotcheck term-cache leak.** The Fin4 sweep hit 16 GB
  RSS by calling `solve_problem` in a loop without clearing the unbounded term
  caches — the same leak session-2 fixed *only* inside `run_marathon()`. Added
  `clear_term_caches()` to `audit_corpus.audit_row` (the shared per-row entry
  for the corpus audit and the spot-check), so long sweeps and big batches stay
  flat. Pure memoisation clear; no behaviour change.
- **Next session:** just run `python stage2/experiments/spotcheck.py` a few
  times (optionally `--effort standard`, `--true 10 --false 10`, or `--sources
  etp`); fix anything it pins. This is the standing accuracy loop now.
- **Do NOT debloat solver routes.** The solver looks big but every route earns
  its place: the 2026-07-21 session proved with evidence that "subsumed" routes
  are cheap high-volume fast paths and that 29 routes look dead on the official
  sets yet are live on the HF `evaluation_*` sets. Deleting routes loses points.
  Debloat means junk files and stale docs, never solver coverage.

## 2026-07-22 session 2

Focus: executed starters 1 and 2 from the session below, plus a third route the
theory produced. All shipped. Full detail:
`stage2/results/2026-07-22-universal-identity-route-and-cache-bound.md`.

**Headline: official TRUE rows `659 → 706` (+47), official solved
`1480 → 1534`, HF solved `707 → 727`. Zero oracle failures across all 2,689
problems.**

One idea drives all three new routes: **proof-search cost scales with goal
size, so a small law that implies the goal can be reachable when the goal is
not.** A projection law (`a ◇ b = a`) is the extreme case — it collapses the
theory, closing any goal whose two sides share a boundary variable, while being
the smallest non-trivial equation there is.

- **`true:universal_identity` (starter 2, solved).** The missing algebra: from
  `x = x ◇ A(ȳ)` (`x ∉ A`), every `A(ā)` is a right identity; instantiating
  `A`'s *own* variables with an identity element `E` collapses `A` to a bare
  variable, which upgrades the hypothesis to the left projection law. Mirror
  shape gives right projection. **+14 official / +4 HF TRUE.** Certificates are
  in the kernel-checkable `exact_expr` shape.
- **`true:projection_bootstrap` (new).** When the algebra fails, point the
  existing critical-pair closure at the *projection lemma* as its goal instead
  of the real goal. It lands in **milliseconds** on rows where the same engine
  cannot prove the goal at any budget. 30 firings. Gated by a free syntactic
  check (`projection_from_lemma_goal_proof` returns `None` unless a projection
  law could close the goal), and placed **last** in `solve_problem`.
- **`true:lemma_bootstrap` (new).** Same move over a six-entry library of small
  laws. 16 firings, **all via `a = b`** — it generalises the syntactic
  `singleton_route` into "the closure *proves* eq1 forces a one-element magma".
  The other five entries earned nothing but cost nothing (the cheap gate
  rejects them), which is the design point.
- **LLM lemma lane.** `{"verdict":"true","lemma":"a ◇ b = a"}` (or `"lemmas"`)
  is now accepted and documented in `PROMPT`. The model supplies only *which
  law to aim at*; the solver proves the lemma from eq1, the goal from the
  lemma, and the kernel re-checks both. See the LLM findings below.
- **`oracles.py` strengthened, not bypassed.** The `have hlem : …` shape used
  to classify as `other` (model-check only). New `check_true_lemma_certificate`
  reads the lemma statement back out of the certificate and runs `ProofKernel`
  twice — lemma body against eq1, goal body against the stated lemma — so a
  builder that proves one law and applies another cannot pass. Wired into both
  `test_golden.py` and `audit_corpus.py`.
- **Control run: 16 of the 19 rows route 1 wins are unreachable at `standard`
  effort** (26-145 s/row on the pre-change solver); the other 3 cost 27-56 s and
  are now microseconds. New coverage, not re-labelled work.
- **Term caches bounded (starter 1, shipped).** `clear_term_caches()` clears all
  13 module-level `@lru_cache(maxsize=None)` term utilities once per problem in
  `run_marathon()`. Measured on `hard2`: without clearing 15.4 M cached entries
  after 50 problems, 25.8 M after 100, still climbing (the mechanism behind this
  morning's 11.2 GB RSS); with clearing the peak is flat at 4.18 M across all
  200 rows. Kept unbounded (not `maxsize=N`) so the hot path stays fast;
  clearing between problems is free because problems essentially never share
  `Term` tuples.
- **Real-LLM result — first accepted LLM TRUE proofs in this project, but the
  frontier still holds.** `llm_balanced_eval.py --per-class 20
  --unresolved-only`, real tokens, gpt-oss-120b: 5 accepted TRUE proofs, **all
  via `llm:true:lemma`**, 0 via chain/guided_chain, 0 wrong verdicts. Against
  0 LLM TRUE accepts in each of the three prior sessions. **But all 7 correct
  rows were rows the deterministic lane already solves; on the 17 genuinely
  unresolved rows the LLM scored 0.** The +47 headline is entirely
  deterministic work.
- **The LLM failure mode moved, usefully.** `guided_chain_unproved_or_bad_endpoints`
  is no longer dominant (7); `lemma_not_derivable_from_hypothesis` is (13). Of
  16 parsed proposals, 14 passed the "does this imply the goal" gate — the
  model proposes goal-relevant laws. Attribution of the 13: **6 were
  demonstrably FALSE** (an eq1-model refutes them) and **0 of the 7 survivors
  became derivable with 22x the budget**. So: do *not* raise the LLM lemma
  budget (measured dead), and filter before proving — `lemma_survives_models`
  now rejects refutable lemmas in milliseconds. That filter lost 0 rows, gained
  3, and cut audit wall-clock ~25%.
- All 5 rows in
  `stage2/fixtures/universal_one_sided_identity_misses_2026-07-22.jsonl` are now
  solved and double-verified. Golden regenerated (213 entries / 126 routes);
  `pytest stage2/tests`: **273 passed**. Packaged at 277,918 bytes.
- **The pre-package gate was flaky under CPU load and is now stable.** Two rows
  drifted between interchangeable general closure engines racing a wall-clock
  budget. `test_golden.py` now collapses `absorption_closure` /
  `equational_closure` / `derived_cp_closure` into one family and tolerates a
  bespoke route drifting *onto* a general engine; every other drift, coverage
  loss and soundness check still fails hard. Step-count budgets remain the real
  fix.
- **Read the TRUE column, not the solved column.** Official Δ solved is +53 but
  Δ TRUE is +47 — the difference is FALSE rows flipping on wall-clock timing
  (rail 4 below). Quote +47.

## 2026-07-22 session 1

Focus: hard1/hard2/evaluation_normal deep dive + a real Marathon LLM-lane
simulation (official proxy, positive tokens, gpt-oss-120b). No solver.py
changes shipped. Full detail:
`stage2/results/2026-07-22-hard1-hard2-evalnormal-marathon-session.md`.

- **Real Marathon LLM lane confirmed still near-zero on this frontier.** hard1
  (10 calls), hard2 (51 calls), and evaluation_normal (22 calls) all scored
  identically with and without the LLM lane — real tokens spent
  (129,806 / 791,519 / 263,165), zero accepts across 83 total LLM attempts.
  Dominant reject: `guided_chain_unproved_or_bad_endpoints`, matching the
  2026-05-30 session exactly. This is a solver-side bridging-search
  limitation, not a prompt problem.
- **Deep-tier budget alone (no code change) recovers 4/76 known misses** via
  the existing `derived_cp_closure` engine (`hard2_0120`, `hard2_0154`,
  `evaluation_normal_0096`, `evaluation_normal_0172`), oracle-verified sound.
  The other 72/76 do not yield to more budget — reconfirms the 2026-07-20
  finding that this frontier resists brute-force search scaling.
- **New scalability risk found, not yet fixed**: solver.py's module-level
  `@lru_cache(maxsize=None)` term-utility caches never clear across problems
  within one Marathon process. Observed 11.2 GB RSS / 1086+ CPU-seconds
  partway through a 200-row real run. Fix before any large-N real validation:
  bound the caches or clear them per-problem in `run_marathon()`.
- Found and fixed two session-blocking infra issues along the way: a
  self-inflicted token-budget miscalculation (402 errors), and a genuinely
  invalid/revoked OpenRouter key (401 "User not found") that needed the user
  to rotate — plus a stale-process-env gotcha where the rotated `.env` key was
  shadowed by an old value already set in the shell environment.
- **New TRUE-route lead, not shipped**: a "universal one-sided identity"
  equation family (`x = A(...) ◇ x`) appears in ~9% of TRUE misses; worked out
  by hand that the fact alone doesn't trivially close the goal, so it needs
  real proof derivation next session, not a quick pattern match.

## 2026-07-21 session

Focus: readiness audit across math / AI / software, then act on the biggest gaps.
Full detail: `stage2/results/2026-07-21-correctness-harness-and-budget-scaling.md`.

**Shipped**

- **Offline correctness gate** — `pytest stage2/tests` (262 tests at the time; 208 and ~160 s as of 2026-07-29 — the count fell when the golden fixture moved to route-family grouping, 213 entries -> 136), no Lean
  needed. An independent proof kernel evaluates the Lean grammar the closure/CP
  builders emit and checks each certificate proves exactly `eq2.lhs = eq2.rhs`;
  a finite-model oracle independently refutes unsound TRUE verdicts; mutation
  tests prove the oracles reject corrupted certificates. `package_solver.ps1`
  refuses to package on failure. See `stage2/tests/README.md`.
- **Local-search finite model finder** (`local_model_counterexample`), run after
  the TRUE routes so solved rows pay nothing; gated by `table_is_counterexample`
  so it cannot emit an unsound witness. **+7 rows**.
- **Effort scaling** (`EFFORT_TIERS`, `set_effort`, `effort_for_seconds`). The
  engines were using ~1% of the available clock: `marathon_per_problem_budget`
  was hard-capped at 4 s and the CP closure at 8 s while Marathon affords
  ~1800 s/problem. `fast` reproduces old behaviour exactly.
  `MARATHON_DETERMINISTIC_SHARE=0.6` stops the hungrier engines starving the LLM lane.
- **Prompt/parser fix** — `PROMPT` used to forbid counterexample tables while the
  parser verified them; the model answered "true" on 47/50 FALSE rows (0% FALSE).
  Now it states the search is non-exhaustive and invites a verified table.
- **Guided-chain edge prover** was fixed at 1.0 s; now effort-scaled.

**Measured**

- Zero oracle failures across **2,689 problems** (1,889 official + 800 HF).
- Official sets **1487/1669** (docs previously claimed `1201/1669` — stale by ~280).
  `standard` tier: hard1 60/69, hard2 154/200. This is offline evidence; a cloud
  judge sweep is still required before promotion.
- Frontier by label: TRUE 659/819 (160 missed), FALSE 821/850 (29 missed).
- Real-LLM balanced eval (gpt-oss-120b): baseline 14/100 (TRUE 28%, FALSE 0%),
  **0 wrong verdicts submitted**, 47 verdict errors caught pre-submission.
  After fixes on a 20-row check: TRUE 50%, FALSE 10%, overall 30%.

**Rails learned the hard way**

1. **HF evaluation sets are first-class evidence.** 29 routes look dead on the
   official sets but are live on HF. Never delete or refactor without them.
2. **Subsumption is not a deletion licence.** 35 routes are subsumed by the
   general engines, but several are cheap high-volume fast paths (`true:rewrite`,
   52 rows) whose removal would push rows onto the 8 s CP engine.
3. **File size is not binding** — 251 KB of 500 KB. De-bloat buys maintainability,
   not points. The aggressive-deletion plan was abandoned on evidence.
4. **Route selection is wall-clock nondeterministic**, so a slower eval machine
   can skip rows that solve locally. The golden gate compares engine *families*.
   Step-count budgets remain open.
5. **Never mix LLM calls and certificate verification in one `ThreadPoolExecutor`**
   — verification is CPU-bound and the GIL serialises it. Use the two-phase shape
   in `llm_balanced_eval.py` (threads for network, processes for verify): ~10x.

## 2026-07-20 session

Focus: a self-verifying LLM TRUE-proof loop with `openai/gpt-oss-120b` via OpenRouter.

- New durable tools: `stage2/experiments/dev_true_loop.py` (repair loop: gpt-oss →
  solver chain/parse → **local Lean judge verify** → feed the error back) and
  `stage2/experiments/analyze_true_loop.py`. Dev-only; the shipped solver still only
  reaches the organizer proxy. Secret-safe; prefers the fresh repo `.env` key.
- Solver changes (all shipped, packaged at 226 676 bytes): `PROMPT` rewritten
  chain-primary (stops FALSE-guessing, forbids `simp`/`aesop`/`grind`, warns ◇ is
  non-associative); `sanitize_lean_code` no longer requires literal `intro G _ h`
  (judge is the gate); guided-chain edge prover `LLM_GUIDED_CHAIN_MAX_DEPTH=8`/`1.0 s`;
  `LLM_MAX_ROUNDS=6`; `run_solo` feeds parse rejects back via `{solver.feedback}`.
- Findings: the loop works (A/B on a solvable set: **25% → 75%** accepted; chain
  renderer is reliable) but gpt-oss cannot yet crack the deterministic-skip frontier
  at low reasoning (`0/20` mixed, `0/18` normal); big-budget deterministic closure
  cracks only `1/20`. The model gets endpoints right but botches exact instantiation
  and assumes associativity.
- Next lever: hybrid — LLM proposes middle/instantiation terms that seed the
  deterministic closure pool. Full detail: `stage2/results/2026-07-20-llm-true-loop-and-prompt-v3.md`.

## Current Solver Snapshot

- Active source: `stage2/solver/solver.py`.
- **Before any solver change: run `pytest stage2/tests` (it is also the
  pre-package gate). After an intentional route change, regenerate the golden
  fixture with `stage2/experiments/audit_corpus.py` + `make_golden.py`.**
- Packaged artifact: `stage2/submissions/solver.py` (limit 500 KB; current size in `CLAUDE.md` — `277918` was the 2026-07-22 pass).
- Submission directory should contain only `solver.py`.
- Historical public no-LLM baseline: `1201/1669` from `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`, including `34` now-retired grind wins.
- Active validation policy now forbids `--budget-tokens 0` Marathon guardrails. Use positive-token official/proxy runs and record LLM calls, token usage, and rejection classes.
- Current durable May 21 summary: `stage2/results/2026-05-21-prune-refactor-and-fallback-reproduction.md`.
- Current durable May 23 route expansion summary: `stage2/results/2026-05-23-held-out-structural-route-expansion.md`.
- Current durable May 25 cleanup/smoke summary: `stage2/results/2026-05-25-cleanup-and-smoke.md`.
- Current durable May 30 positive-token mixed-lane summary: `stage2/results/2026-05-30-positive-token-mixed-lane-resume.md`.
- Full public validation after the grind rollback and May 21 refactor is still pending. Do not claim the current package preserves old grind-backed totals until a new full run exists.

## Current Boundary Rails

- Preferred TRUE LLM outputs remain solver-owned `rewrite_chain` or `guided_chain` JSON.
- Marathon LLM may also propose FALSE only as `{"verdict":"false","counterexample_table":[...]}`; the solver checks the table before any judge submission.
- Raw TRUE Lean is disabled in Marathon and remains only a Solo/debug parser rail as `{"verdict":"true","code":"<complete Lean file>"}`.
- The raw `code` field may contain helper theorems, defs, lemmas, namespaces, or notation above `def submission : Goal := ...`.
- Legacy body-only `proof` and `proof_body` payloads are retired from the active local boundary and now reject as `proof_body_unsupported`.
- The vendored official README still contains an older `{"verdict": "true", "proof": "<tactic body>"}` prompt snippet. Treat that as upstream doc drift; the canonical local and judge-facing contract is full Lean source in `code`.

## Historical Boundary Changes (2026-05-30 mixed-lane era)

Kept as durable context for the LLM contract; NOT this session's changes (see the
dated session blocks above for recent work).

- Retired the broad/raw TRUE Marathon behavior that produced playground errors; Marathon TRUE now accepts only solver-checked chains.
- Updated the LLM prompt for the mixed lane: TRUE proof-chain proposals are still checked locally, and FALSE is allowed only as a finite table that passes `table_is_counterexample`.
- Fixed the false-search deadline checks so a zero-second local profiling budget is honored instead of silently expanding into an unbounded search.
- Replaced the old tokenless sweep/analyzer helpers with positive-token Marathon helpers that fail closed on nonpositive budgets.
- Refreshed the no-network LLM smoke, package artifact, route ledger, LLM motif card, and durable result summaries to match the current rails.

## Historical Regression Evidence (2026-05 era — see "Current status" for live numbers)

- Python syntax checks passed for source, experiment helpers, and packaged solver.
- `stage2/experiments/smoke_llm_dsl.py` now accepts helper-bearing full-file TRUE `code` payloads and rejects `proof` / `proof_body` payloads.
- `theory/tools/smoke_problem_sets.py` passed and confirmed public/HF mirror counts.
- 2026-05-25 no-key Solo smoke: `sample_20 = 15/20`, `sample_200 = 169/200`.
- 2026-05-25 bounded proxy smoke: Solo `1/1` with `llm_calls=1`; Marathon `1/1` with `89/4096` tokens used.
- 2026-05-30 official `normal_100` positive-token Marathon guardrail with Lean on PATH: `75/100`, `25` not attempted, `47419` tokens used, no incorrect submissions.
- 2026-05-30 TRUE red-flag positive-token Marathon after raw/grind TRUE trim: `2/13`, `11` LLM calls, `22764` tokens, no incorrect submissions.
- 2026-05-30 official `hard1` positive-token mixed-lane Marathon: `39/69`, `30` not attempted, `30` LLM calls, `240164` tokens used, no incorrect submissions.
- Repo-side generated `__pycache__` directories were removed; `.venv/` bytecode was left alone as ignored local environment state.
- Submission directory cleanliness: only `solver.py`.
- Route profile on public `normal_100` after the May 23 route expansion: `74` deterministic candidates, `26` skips, `47.479s`.
- Held-out hard first 80 after the May 23 route expansion: `76` deterministic candidates, `4` skips, `7.854s`.
- Official Solo harness on `sample_20`: exit `0`, no failing categories.
- Current package has positive-token official guardrail evidence for `normal_100`; broader full-public positive-token validation is still pending.
- Current held-out hard80 TRUE skips after the May route pass: `evaluation_hard_0072`, `evaluation_hard_0074`, `evaluation_hard_0078`, and `evaluation_hard_0080`.

## Selected-Row Reproduction

User-provided labels were normalized by removing the true/false label segment, for example `hard1_true_0065` -> `hard1_0065`.

- Public rows came from `vendor/stage2-official/examples/problems/`.
- Evaluation rows came from `data/hf_cache/`.
- Direct certificate verification used `verify_answer(_to_judge_problem(problem), raw_answer)`, not raw `verify_answer(problem, ...)`.

Broad 27-row direct probe:

- `evaluation_extra_hard_0045`, `evaluation_extra_hard_0043`, and `evaluation_extra_hard_0041` are now solved as `FALSE ACCEPTED` by `false:witness:S4C` in about 4-6 seconds.
- The other 24 listed rows reproduce Solo-style fallback behavior: submitted `TRUE`, judge `incorrect`, error code `LEAN_REJECTED`.
- Direct local timings for fallback rows were about 1.3-3.2 seconds because the probe bypassed live proxy waiting and checked the final fallback directly.

Historical Marathon reproduction on the same manifest, archived before the current positive-token policy, accepted the three `evaluation_extra_hard_false_*` rows via `false:witness:S4C` and left the other `24` rows unresolved. Use it only as fallback-reproduction history.

Scratch artifacts:

- `tmp_stage2_smoke/2026-05-21-fallback-batch-27.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.py`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/summary.json`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/run.log`

## Best Public Evidence

Latest completed official public no-LLM Marathon refresh, before the final heartbeat/path-helper optimization patch and before grind retirement:

| Set | Solved | TRUE | FALSE | Notes |
| --- | ---: | ---: | ---: | --- |
| `normal` | `803/1000` | 305 | 498 | salvaged via isolated `--score-only` after a Lean artifact failure |
| `hard1` | `42/69` | 6 | 36 | clean full lane |
| `hard2` | `92/200` | 16 | 76 | clean full lane |
| `hard3` | `264/400` | 63 | 201 | clean full lane |
| **Total** | `1201/1669` | 390 | 811 | `0` solver tokens |

Answer-kind totals for that baseline:

- `false:finite`: `811` accepted.
- `true:certificate`: `356` accepted.
- `true:grind`: `34` accepted, `433` incorrect; historical discovery evidence only.
- Remaining public misses by labels: `429` TRUE and `39` FALSE.

## Key Lessons

1. Generalize proof and witness families; do not add solver policy keyed to public or evaluation row ids.
2. Selected-row reproduction is useful for diagnosis, but promotion claims need full lanes or focused route fixtures with judge-accepted certificates.
3. Solo fallback `TRUE INCORRECT` rows and positive-token Marathon local LLM rejects can be the same unresolved proof-quality gap viewed through different runner policies.
4. The three `evaluation_extra_hard_false_*` rows appear fixed in the current package. If they failed elsewhere, that evidence likely came from an older package or different upload.
5. `true:grind` was a discovery route, not a deployable strategy. It found `34` public TRUE wins but caused `433` incorrect attempts and is retired from active solver policy.
6. Do not run or cite `--budget-tokens 0` Marathon as active validation; positive-token official/proxy runs are the guardrail lane.
7. Positive-token local LLM evidence must prove official proxy usage: nonzero Solo LLM calls, nonzero Marathon `llm_calls`, nonzero `tokens_used`, and classified failure outcomes.
8. Do not reopen the legacy `proof` / `proof_body` TRUE rail locally. Raw TRUE now means full Lean source in `code`.
9. Full-file TRUE `code` may declare helper theorems, defs, lemmas, namespaces, or notation above `submission`; this is part of the supported local boundary.
10. Treat the stale vendored `proof` example as doc drift unless an upstream sync explicitly changes the judge contract.

## Recommended Next Steps

Updated 2026-07-23 (after shipping `true:egg_closure`). Ranked by evidence:

0. **Standing loop first**: run `python stage2/experiments/spotcheck.py` a few
   times; fix anything it pins.
1. **Give egg more budget where it pays.** The +21 is `fast` tier (10 s/row).
   The prototype reached 21–23 official frontier rows at 20 s; a `standard`
   Solo sweep (75 s) should land the ~8 currently timing out. Cheapest win.
2. **Shrink egg extraction further.** Some proofs still hit the 46 KB byte cap
   and get dropped (`hard3_0208`, `evaluation_order5_0022` were 126 KB / 186 KB
   pre-shortening). Better cycle-cutting / common-subproof sharing = more
   shippable rows at the same saturation power.
3. **Step-count budgets** instead of wall-clock, so route selection is
   deterministic and the golden gate can go back to strict equality (this is
   also what would let `egg_closure` back into the golden fixture).
4. **Re-run the LLM lemma lane** — egg raises its ceiling: the model names a
   law, egg derives it, the kernel checks it.

Older items (LLM rails discipline, no raw-TRUE Marathon Lean, no proof-body
rewrapping) remain true as ongoing constraints, not active TODOs — see
"Current Boundary Rails" above.

## Scratch Discipline

- `tmp_stage2_smoke/` is scratch. Promote only concise dated summaries under `stage2/results/`.
- Consult `stage2/docs/cleanup-manifest.md` before deleting or moving scratch artifacts.
- Do not hardcode public benchmark ids in solver policy. Pasted row lists are regression fixtures and diagnostics only.
- Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, ledgers, or summaries.
