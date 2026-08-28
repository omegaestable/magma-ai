# Deep session 5 — the Austin problem session (handover)

Written 2026-08-28 at the end of the perf/bytes/assessment day. Read
`CLAUDE.md` first (rails 34–37 are from this day), then this file, then
`stage2/experiments/austin/README.md`. Evidence for every number:
`stage2/results/2026-08-28-assessment-deterministic-austin-tidy.md` §2 and
`stage2/results/2026-08-27-austin-order5-hard-research-set.md`.

## The goal

**All 100 rows of `data/hf_cache/research_order5_hard.jsonl` solved,
deterministically, by routes that live in `stage2/solver/solver.py`, every
certificate accepted by the real Lean judge.** Not "as many as possible":
100/100. The session ends when the row-id ledger reads 100 accepted, or when
the remaining rows each carry a written proof of *why* the specific approach
below cannot close them — a measured reason, not a budget.

The set: 100 rows, **69 distinct hypotheses** (`eq1`), **10 distinct goals**
(`eq2`, the confirmed Austin laws). Ground truth is null everywhere and the
organizers exclude the set from scoring; the point is that private Order-5
rows with no finite models look exactly like these, and today the solver
returns nothing on that shape. Solving a hypothesis solves every row that
shares it: `11116`, `22591`, `32281`, `34889`, `36713` cover 3 rows each,
15 hypotheses cover 2, and the goal `22818` appears in 20 rows.

Current state: **0 / 100 — 100 left.** 0 at every tier, 0 from every
automated construction tried on 2026-08-28 (table below).

## What settles a row

`eq2` is a confirmed Austin law: no nontrivial finite model exists. So:

- **TRUE** = an equational proof `eq1 ⇒ eq2`. Vampire (teorth, time-limited)
  found none; our completion/egg engines and z3 (169/169 `unknown`) found
  none. Tracked in Track C; not where the rows are.
- **FALSE** = an **infinite** model of `eq1` that violates `eq2`, as a Lean
  certificate. Finite search is provably useless (Table-2 hypotheses have no
  nontrivial finite models; a field-linear model reduces mod p to a finite
  one — Lefschetz). This is where all 100 rows are. The blueprint's own
  words: "no effort was made to build infinite models for these equations."
  So the rows are open because nobody tried, not because someone failed.

## What was measured on 2026-08-28 (do not redo)

All tooling in `stage2/experiments/austin/` (README has the per-script table).

| Tried | Result |
| --- | --- |
| z3 proving, 120 s/row, 100 rows + 69 collapse goals | 169/169 `unknown` |
| z3 finite models for the 14 Table-3 hypotheses | stopped by decision; cannot work for Table 2 |
| affine `a·x + b·y + c` over ℚ | 0/69 (controls pass) |
| ℤ piecewise-linear `if COND then L₁ else L₂` (omega-provable) | 0/69, control 40/40 |
| root-reduce term model | passes random tests on 23/69, **broken by the critical-pair assignment** (`v_x` `T`-shaped with `y`-part `= v_y`) |
| normal-form / free model | 0/69 — non-confluent one-rule systems |
| junk-truncated repair models, repairs at the *innermost* derailed node | repairs regress over deeper shapes |
| **tag automaton** (Kisielewicz-style) | reproduces **28770 at depth 2 with 0 repairs**; 0/69 on the research laws; **wrong at depth 4** (2,629/20,000 deep random violations; 205/20,000 with square-first priority) |
| Lean renderer for tag automata (`tag_lean.py`) | compiles through the definitions and the no-fixpoint lemmas; the bounded `cases` main proof does not close |

## Why the automated attempts stopped at 0, precisely

Two defects, both mine, both fixable — this is the reason to expect the
number to move:

1. **The checker was blind.** The "exhaustive" universe was depth 2; the
   28770 counterexample needs depth 4. Every "model" reported today was
   checked by a test that cannot see the failures that matter (rail 37).
2. **Repairs were applied at the wrong node.** `repair()` fixed the
   *innermost* derailed spine node. At that node the intended value
   (`s2(v_y, v_x)`) contradicts the root rule (the same pair is also a
   genuine root instance and must return `x'`) — in the free model those two
   are *the same element* by a derived identity, so no rule at that node can
   satisfy both readings. The derived identity is satisfiable one level up:
   at the **outermost** derailed node the lost payload is still present as a
   sub-element of the right argument (`X` inside `(x' ◇ X)`), and the repair
   `y ◇ ((x' ◇ X) ◇ (z ◇ z)) → X` is a plain projection. That is precisely
   Kisielewicz's `2^{3^y} ◇ z = 3^y` clause: keyed on the *outer* colliding
   shape, returning a projection. `_projection` reported "not recoverable"
   only because it was asked at the inner node.

So the construction that fits the literature is the tag automaton with
outermost-first repairs and a checker that can see depth. Nothing measured
today rules it out for any of the 69; the 0/69 is an artefact of (1) and (2).

## The plan — four tracks, run in this order, each with a stop condition

### Track A — tag automata done right (the main line; target: the majority of the 69)

1. **Checker (half a day).** Deep random assignments (payload depth ≥ 5,
   20,000 per candidate) + critical-pair-derived assignments (every unifier
   of a proper subterm of `T` with every rule LHS, free variables filled at
   random, compositions to depth 2). "Checked" means 0/20,000 on all of it.
   Stop: the depth-4 28770 counterexample is found automatically.
2. **Repairs outermost-first (one day).** Walk the spine from the root down,
   repair at the first node where the intended value is projectable from the
   pair, key the rule on the *pattern* (variables, not concrete shapes) so one
   rule covers the whole family, keep the realisability filter. Search
   priority orders (specificity, square-first) per hypothesis. Stop: 28770 at
   0/60,000 with his one repair reproduced, then the count of research
   hypotheses at 0/20,000 — write that count down before touching Lean.
3. **Lean proof, inductive (one to two days).** Core Lean only
   (`JudgeProblem` imports no Mathlib; `induction`, `simp`, `omega`, `split`,
   `decide`, derived `DecidableEq` all work — measured). Ingredients: a size
   function `sz : M → Nat`, the lemma "no term equals a term that properly
   contains it" by `omega` on `sz` (replaces the per-constructor no-fixpoint
   lemmas), and the law proved by **induction on the spine argument** with the
   rule equations as simp lemmas — not `cases` on every variable. Repairs are
   extra match arms. Prototype on `28770 ⇒ x = y` through
   `judge_cert_text.py`. Stop: `accepted`, then `28770 ⇒` each of the other
   nine Austin laws accepted.
4. **The 69.** Generate + judge every hypothesis that passed step 2. For the
   ones where step 2 still cannot project: (a) payloads carry *all* variables
   of every spine subterm, (b) different spine choice per goal, (c) rules
   keyed on the parameter's tag (28770's `y³`) rather than the stage's,
   (d) a level counter in the tag (the `2^y < 3^y < 3^y·5^x` growth trick in
   tag form) so elements of different levels cannot collide. Stop per
   hypothesis: checked → judged.

### Track B — free models by finite saturation (covers what Track A cannot repair)

If a hypothesis's ordered completion **saturates** (finite ground-convergent
system), its free model is decidable and is a model of `eq1` by
construction. Vampire saturated all ten Austin laws; nobody has reported
whether the 96 Table-2 laws saturate under a stronger ordering or a longer
run. Steps: (1) census — run `_KBCompletion` with the size cap removed and a
1-hour budget per hypothesis, record which saturate (the 2026-08-27 run was
capped at 240 s and 4,000 active); (2) for those, one generic Lean text —
normal forms as the carrier, `nf` by fuel-bounded rewriting, local confluence
of the finite rule set by `decide` over its critical pairs, Newman's lemma
proved once in the certificate (~200–300 lines, reused verbatim per
hypothesis, well inside 100 KB), `eq2` refuted by two distinct normal forms.
Stop: the census count, then the first accepted certificate.

### Track C — the TRUE side

Install Vampire and E on the development machine (offline use is fine; only
the sandbox has no network). Hours per goal on the 100 goals and the 69
collapse goals `eq1 ⇒ x = y`. Any proof found is replayed through the
completion engine's proof recording into a `lemma_chain` certificate. Stop:
every goal either proved or timed out at ≥ 4 h with the saturation log kept.

### Track D — stragglers by hand

Whatever survives A–C gets a Kisielewicz-style construction by hand, using the
Track A Lean template. The blueprint's two worked models
(`infinite_models.tex`: 374794 and 28770) are the pattern. Budget one day per
hypothesis; rows sharing a hypothesis come for free.

### Ship

`false:tag_model` (Track A/D) and `false:free_model` (Track B) in the FALSE
portfolio after the constraint tiers — they only apply to `x = T`-shaped
hypotheses with no finite model found, so no served row pays for them. Models
that need a hand repair ship content-keyed like `DISTILLED_CERTS` (that is
still deterministic and still in the solver). Every certificate is
`other`-shaped for the kernel oracle, so every one is judge-pinned (rail 5h)
with a golden entry and a fixture row.

## Bookkeeping that keeps the session honest

- Keep a row-id ledger `stage2/results/austin-ledger.jsonl`: `{id, eq1_id,
  eq2_id, track, status, checked_violations, judge_status, judge_seconds}`,
  updated after every judge call. The headline number is only ever read
  from it.
- Never trust a model that has not passed the Track A checker; never count a
  certificate the real judge has not accepted (rails 3c, 37).
- No LLM calls: nothing here is a language task.

## The extended evaluation battery, stated the Zulip way

The full combined set from every published file (11 HF data files + the
harness samples + the marathon example): **2,969 distinct (eq1, eq2) pairs**
— 2,869 labelled plus the 100 research rows. The "2130/2130" figure quoted
from Zulip matches no union of these files (official distinct = 1,869;
+ stress test = 2,069; + all `evaluation_*` = 2,869; everything = 2,969); the
competition Zulip is not in the public archive, so the poster's composition
could not be checked. Nothing published is missing from our battery:
`hard.jsonl` is `hard1` with duplicated rows, the upstream
`stage2_stress_test.jsonl` is byte-identical to ours, and the marathon example
set is inside `normal`.

```
Result (measured 2026-08-28, `audit_corpus.py --file combined_eval_2869.jsonl`, 16 workers, isolated, `fast` tier, no LLM):
2869/2869 solved — 0 failed
Total solver time: 105.5 s
Wall-clock: 1m46.0s
about 0.04 s/problem on average (solver time), 0.037 s/problem wall on 16 workers.
0 crashes, 0 oracle failures, 0 label mismatches; slowest row `evaluation_order5_0154` 60.4 s.
The 100 research rows are the remaining 100 of the 2,969: 0/100, ~460 s/row, this session's target.
```

## Files that matter

- `stage2/experiments/austin/` — every script above; `tag_automaton.py` and
  `tag_lean.py` are the starting points for Track A.
- `stage2/results/2026-08-28-assessment-deterministic-austin-tidy.md` — the
  construction map (linear / cohomology / translation-invariant / greedy /
  free model / piecewise-linear) and why each does or does not apply.
- `paper/blueprint_source/chapter/infinite_models.tex` (Kisielewicz's two
  models — read first), `order_5.tex`, `infinite_magma_constructions.tex`.
- `stage2/experiments/judge_cert_text.py` — judge any certificate text.
