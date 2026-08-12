# 2026-08-11 — The lemma ladder, and three searches that were being starved

Session goal: close the remaining frontier. Entry state was 1658/1669 official at
`fast` tier with 11 open rows and 8 open HF rows, and a next-lever list whose top
item was "bytes-weighted egg extraction" for `normal_0491`.

That lever turned out to be aimed at the wrong thing, and measuring why produced
the session's main result.

## What the frontier actually was

A per-row probe over all 19 open rows (`stage2/experiments/pivot_probe.py`,
`egg_bytes_probe.py`, `frontier_dossier.py` — all kept) separated four failure
modes that had been reading as one "unsolved":

| Mode | Rows | Evidence |
| --- | --- | --- |
| Pivot proved, explanation too long to render | `normal_0491`, `hard2_0162` | collapse merges in 5.0 s, explanation **4510 steps** |
| Pivot proved, explanation recursion too deep | `hard2_0073` | both projections merge at ~42 s, then `explanation recursion too deep` |
| Saturation *terminates* short of the pivot | `hard3_0135`, `hard3_0204`, `hard3_0214`, `hard3_0266`, `hard3_0314`, `normal_0090`, `evaluation_hard_0116` | returns in 5–10 s having exhausted its rule applications |
| Not a proof problem at all | `hard2_0092` | a witness exists and two separate guards stopped the search reaching it |

The last two rows in the "too long" class also killed the bytes-weighted
extraction lever on its own terms. The chains are **not redundant**: shortening
cuts 4510 → 1548 steps, and then a full BFS over the replayed state sequence
finds *no* shortcut at all. A context-factoring renderer (nested `congrArg`,
prototyped and measured) buys a consistent **2.4–2.9x** — 194 KB → 80 KB,
400 KB → 152 KB — against a 46 KB cap. Not close.

What the same measurement did show is why: those 800–1500 step chains use only
**28–38 distinct eq1 instances**, at positions up to depth 16. That is the
signature of a proof re-deriving the same fact over and over, because a flat
`.trans` chain over a single hypothesis has no way to **name** an intermediate
law. Naming one is what makes the ETP's own Vampire proofs of these rows short.

## Shipped: multi-rule saturation and `true:egg_ladder`

`egg_saturate_prove_multi` saturates under a *set* of rules, each carrying the
Lean hypothesis name that justifies it. `egg_ladder_route` uses it to build a
ladder: derive a small law from eq1, bind it with `have`, saturate again with
that law in scope, repeat (up to 4 rungs).

The measurement that decided the design, on `hard3_0266`
(eq1 `x = (y ◇ ((x ◇ z) ◇ z)) ◇ x`, goal closed by right projection):

- single-rule egg cannot reach right projection in **60 s**;
- idempotence `a ◇ a = a` is derivable in **under 2 s**;
- with idempotence in scope, right projection follows in **0.01 s** with a
  **267-byte** proof.

Unreachable to instant. That gap is the whole route.

Three design points are worth keeping:

1. **Rung candidates cannot come from the e-graph.** The first implementation
   read laws off a saturated generic-term graph. On `hard3_0314` a 5 s
   saturation over every term in a, b, c produced 640 "laws" and **every one was
   a direct instance of eq1** (9-byte proofs, `(h a b c)`) — only 10 of 1431
   classes held more than one term. Nothing cross-merges, so there is nothing to
   read. Candidates come from the small-law library instead, in size order.
2. **A rung does not have to close the goal.** It only has to be derivable and
   useful downstream, so the goal-shaped gate that filters the *pivot* list is
   deliberately not applied to rungs. `lemma_survives_models` is applied, and it
   is free: ~10 ms for the whole library, rejecting 429 of 601 candidates on
   `hard3_0266`.
3. **Round 0 is a probe, not a full attempt.** With no rungs yet it *is*
   single-rule saturation, which `egg_collapse` and `egg_priority_bootstrap`
   have already run at full budget before this route is reached. Re-running it at
   8 s a pivot cost `hard2_0073` its entire 60 s clock on attempts that could not
   have worked.

No new oracle surface: certificates are the existing `lemma_chain` shape, so
`oracles.check_true_lemma_chain_certificate` verifies each rung independently
with the `ProofKernel` — every helper in the scope of `h` plus the helpers before
it, then the goal in the scope of all of them. The single-rule engine is left
untouched; 249 audited rows are served by it and a shared refactor would have
risked all of them to buy nothing (rail 1).

## Shipped: `lemma_closes_goal` — the pivot gate was direction-blind

`lemma_applies_to_goal` searches `eq2.lhs -> eq2.rhs` only. Every remaining
frontier goal is shaped `x = <big term>`, so a pivot has to reduce the **big**
side and the search has to run the other way. Measured: right projection closes
`hard3_0314`'s goal in three reductions, the forward gate reports nothing — so
that row never got an egg attempt at the one law its eq1 is *equivalent* to.

## Shipped: two starved searches, one row each

**`hard2_0092`, guard 1 — the constraint search never looked.**
`constraint_countermodel` opened with `if len(eq1 vars) > 4 or len(eq2 vars) > 4:
return None`. That row has 5, and the search finds an order-5 countermodel in
**0.33 s / 126 nodes** once allowed to try (independently re-derived by hand
first: carrier `Fin 5`, `Im = {0,1,2}`, two non-image elements — order 5 is
minimal, since one non-image element forces a contradiction). Rail 5f, fourth
instance: the dev twin `mace_finder.py` has no such gate, which is why the
constant's own comment already recorded a witness for this row that the shipped
solver could not claim.

Replaced by a per-*order* instance bound (`n ** variables <= 20_000`), applied
only in the **wide** tier — reached solely by rows nothing else claimed. The
cheap tier keeps `max_variables = 4` deliberately: it runs before the TRUE
engines on every row, and 168 of the corpus's five- and six-variable rows are
TRUE, where no witness can exist. An order skipped for cost now leaves the
search **incomplete**, because `constraint_search_exhausted()` is what licenses a
speculative TRUE verdict (rail 5) and "skipped" must never read as "searched".

**`hard2_0092`, guard 2 — the row did not even need that.** With the gate lifted
the row solved in **1.75 s** via `false:dual:false:witness:S5B`, a named table
that has been in the solver for months. `find_counterexample` ran its whole
portfolio *and* the dual pass on one shared 2 s deadline, with the dual last on
the leftovers. `witness_check` costs `n ** variables`, so on a 5-variable row
every table test is ~n² dearer: the primary passes alone spent 1.6 s of the 2 s,
leaving the dual 0.4 s to find a witness it needs 0.1 s for. On an idle machine
it just fit; under the audit's 16-way parallelism it did not, and the row read as
a permanent skip for four sessions. The dual pass now gets its own slice
(`local_deadline` still clamps it to the global per-problem deadline).

## Results

Standalone at `fast` tier, every certificate verified by the independent offline
kernel (`ladder_probe.py`, which runs `oracles.check_true_lemma_chain_certificate`
on whatever the route emits):

| Row | Route | Bytes | Seconds | Kernel |
| --- | --- | ---: | ---: | --- |
| `normal_0090` | `true:egg_ladder:goal:h1` | 1301 | 10.7 | ok |
| `normal_0491` | `true:egg_ladder:collapse:h1` | 4755 | 2.1 | ok |
| `hard2_0162` | `true:egg_ladder:collapse:h1` | 9117 | 9.3 | ok |
| `hard3_0135` | `true:egg_ladder:left_projection:h1` | 5382 | 4.3 | ok |
| `hard3_0204` | `true:egg_ladder:right_sq_projection:h2` | 2644 | 24.4 | ok |
| `hard3_0266` | `true:egg_ladder:right_projection:h1` | 3887 | 4.3 | ok |
| `hard2_0092` | `false:dual:false:witness:S5B` | 313 | 1.8 | ok |

Note `hard3_0204` needs **two** rungs (`h2`), and `normal_0090` closes the goal
directly once a rung is in scope rather than through any pivot.

The three cost bugs found while building this are the reason the timings above
are seconds rather than minutes. Before they were fixed, `normal_0491` took
26.9 s (now 2.1 s), `hard3_0266` 16.2 s (now 4.3 s) and `hard3_0135` 16.2 s (now
4.3 s), and two rows stalled indefinitely:

1. **A deadline polled once per outer loop level is not a deadline.**
   `_egg_run_saturation` checked the clock once per e-class while *building* its
   application list; with several rules the orientation count doubles per rule
   and a free-variable product over the pool is hundreds of candidates per match,
   so a 2 s attempt ran for minutes.
2. **Greedy bridging is O(states²) × rules.** A 1500-step chain with 5 rules is
   ~22M pattern matches. It is an optimisation, never a correctness requirement,
   so it now has a hard state cap *and* the caller's deadline.
3. **The explanation step budget is really a bound on proof-forest traversals.**
   Every congr edge spawns a fresh BFS over the whole forest, and 200_000 steps
   (the single-rule figure) is meaningless when no explanation above ~4600 steps
   can render inside the 46 KB cap. Now 20_000, plus a deadline.

## Isolated official audits

Two isolated `audit_corpus.py --all` runs at `fast` tier, machine otherwise idle:
`audit-2026-08-11.json` after the ladder, `audit-2026-08-11b.json` after the
gap-closing pass.

| Set | Solved | TRUE | FALSE | Skipped | Oracle failures | Crashes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `normal` | **1000 / 1000** | 500 | 500 | 0 | 0 | 0 |
| `hard1` | **69 / 69** | 24 | 45 | 0 | 0 | 0 |
| `hard2` | 199 / 200 | 99 | 100 | 1 | 0 | 0 |
| `hard3` | 398 / 400 | 193 | 205 | 2 | 0 | 0 |
| **Total** | **1666 / 1669 (99.82%)** | **816 / 819** | **850 / 850** | 3 | **0** | **0** |

**FALSE is complete**, and `normal` and `hard1` are complete. All three remaining
rows are TRUE.

Diffed by row id against `audit-2026-08-07.json` (rail 2 — never by total):

- after the ladder: **+7 gained** — `normal_0090`, `normal_0491`, `hard2_0162`,
  `hard3_0135`, `hard3_0204`, `hard3_0266` (all `true:egg_ladder`) and
  `hard2_0092`; **−1 lost**, `hard1_0062`.
- after the gap-closing pass: **+2 gained** — `hard1_0062` and `hard2_0123`,
  both by distillation; **0 lost**.
- net across the session: **+9 / −0**.

**On `hard1_0062`, which the first audit lost and the second regained** — the
regain is by distillation, not by the analysis below being wrong. Both remain
true: the row needs more than its `fast` slice, and it is now served from the
distilled library so the slice no longer matters.

**The loss is not attributable to this session's changes**, and establishing that
took a measurement rather than the obvious story. The obvious story was
attractive: two things now sit ahead of the wide constraint tier (the dual witness
pass, and `egg_ladder`'s 60 s), so of course a row that needs that tier lost its
clock. It is wrong. Timing the tier directly on `hard1_0062`:

- its order-8 search needs **71.5 s**; the `fast` slice is **45 s** (it does find
  the witness given 120 s);
- the wide tier's deadline is `local_deadline(_eff_time(45.0))` computed **fresh
  at each order**, so an engine ahead of it delays the *start* and not the
  *slice*;
- the new instance cap admits every wide order for this row — it has 3 variables,
  so order 8 is 8³ = 512 instances, nowhere near the 20,000 bound.

So the row needs more than its `fast` slice, solved on 08-07 inside 45 s, and does
not today: the ±7 run-to-run band of rail 2, on a row `CLAUDE.md` already records
as needing `standard` effort and which is judge-accepted there in 4.7 s. That is
the tier Solo and Marathon run.

Worth keeping as method: a mechanism change and a marginal row landing in the same
audit is exactly the setup where a plausible causal story gets written down as
fact. The check that settled it took two `constraint_countermodel` calls.

## HF mirror audit, gate, and package

`audit_corpus.py --hf`, isolated (`audit-2026-08-11b-hf.json`): **795/800**,
TRUE 395, **FALSE 400/400 complete**, 0 oracle failures, 0 crashes. `extra_hard`
200/200, `normal` 200/200, `hard` 198/200, `order5` 197/200. Across the session
**+3 gained, 0 lost** (`evaluation_hard_0178`, `evaluation_order5_0006`,
`evaluation_order5_0040`). Combined offline total **2461/2469**.

A process note worth recording against myself: the first HF run was started while
other CPU work was still going, which is precisely what rail 5e forbids. It was
killed and re-run clean rather than caveated — a contaminated audit is worth less
than no audit, because its losses cannot be distinguished from real ones.

Golden regenerated from both audits: 52 entries / 33 routes. Gate **201 passed,
2 skipped, 16.5 s**.

Regenerating the golden fixture first produced a **208 s** gate, up from 22 s, and
the cause is worth recording. `make_golden` excluded expensive rows only when the
route was `false:constraint_fin*`; that rule should never have been
route-specific. What makes a row unfit for the gate is its cost, and the routes
that run *after* the TRUE engines (`local_model`, the wide constraint tier) now pay
for `egg_ladder` too, so more of them crossed the line — one pinned row,
`evaluation_order5_0065`, cost **170 s** by itself. The audit's own `seconds`
predicts the gate almost exactly (170.3 audited vs 170.7 in the gate), so the
filter is now cost-based for every route: gate back to **15.7 s**, faster than
before this session.

Packaged **480,115 bytes of the 500,000 cap** and verified standalone from a
scratch *copy* — import, an id-less payload (the shape that exposed the rail-5g
`is_reflexive_problem` bug, still correctly refusing `true:reflexive`), and the
same row with ids — leaving `stage2/submissions/` containing only `solver.py`.

**Headroom is 19,885 bytes (4.0%)**, the tightest it has been. "File size is not
binding" has been true for the whole project and is no longer safely true; rail 1
is amended accordingly.

10 KB of that was recovered for free. `package_solver.ps1` used `Copy-Item` on a
CRLF working tree, so every one of ~10,400 lines shipped a carriage return the
judge does not need: **490,503 bytes as a straight copy, 480,115 written as LF**
(UTF-8, no BOM), 2% of the cap for no content change. Where the rest of the bytes
are, measured rather than guessed: `DISTILLED_CERTS` is **14.8% of the file**
(71 KB across 22 entries, the two largest 12.6 KB and 11.9 KB) and full-line
comments are 10.3%. So distilling a big egg proof costs 2–12 KB of the cap — which
is why 2026-08-07 left two oversized certs out, and a trade to make deliberately.

## Still open at `fast` tier, with a diagnosis each

The ladder was run over all 19 open rows (`ladder_probe.py --open`). It closed 6
and left these, each at its 60 s route budget:

| Row | Why |
| --- | --- |
| `hard2_0073` | An **extraction** problem, not a search one: both projections *merge* single-rule at ~42 s, then `explain` dies with "recursion too deep". No library law is provable inside the rung budget. |
| `hard3_0214` | `triple_left` (`((a ◇ b) ◇ c) ◇ d = a`, ETP's Eq269) closes the goal and survives models, but no rung is found at `fast`. |
| `hard3_0314` | eq1 is *equivalent* to right projection and `lemma_closes_goal` now admits that pivot — but neither it nor the documented unlock law `(a ◇ b) ◇ a = a` is reachable in 30 s single-rule (measured, three spellings). Needs a rung. |
| `hard2_0123` | Unchanged: needs the `standard`-effort constraint tier, which is what Solo and Marathon run. |
| `hard1_0062` | Same as `hard2_0123` — a wide-tier FALSE witness needing `standard`'s scaled budget, judge-accepted when it gets it. Measured: its order-8 search wants 71.5 s against a 45 s `fast` slice. Not caused by this session's changes (see above). |
| `evaluation_hard_0116`, `evaluation_hard_0196`, `evaluation_order5_0014/0042/0164` | Same shape as `hard3_0214`: a viable pivot, no reachable rung at `fast`. |

The common blocker is now precise and singular: **the rung candidate set.** All of
these rows have a pivot that would close the goal; none has a law in the 601-entry
small-law library that the current rule set can prove in the rung budget. Two
untried angles are in `CLAUDE.md`'s next-lever 1 — a larger rung budget at deep
effort, and **goal generalisation** (anti-unify eq2 to get a law that implies the
goal by instantiation, which is a free syntactic check). `hard3_0214`'s ETP pivot
is exactly such a generalisation of its own goal, which is encouraging.

## Real-judge verification, and the rendering bug it caught

All six ladder certificates were run through the real local Lean judge:
**6/6 accepted, 2.4–4.1 s each.** That is the mandatory check for a new
certificate builder, and it passed first time. Three FALSE rows were judged as
controls after the search fixes — `hard2_0092` (the row this session unblocked),
`hard2_0001` (the other row `CLAUDE.md` flagged as starved by the same shared 2 s
budget) and `hard2_0009` (a wide-tier control): **3/3 accepted**, `hard2_0001`
also now arriving via `false:dual:false:witness:S5B`. Session tally: **9/9
accepted, 0 rejected.** `hard1_0062` and `hard2_0123` skip at `fast` as
documented — a skip is safe, a rejection is not.

The same run caught something the offline oracles are structurally blind to.
Before the dual-pass fix landed, `hard2_0092` was being claimed by the newly
reachable wide constraint tier as `false:constraint_fin6`, and the judge returned
**`LEAN_REJECTED`** — on a table that `table_is_counterexample` confirms is a
genuine countermodel (independently re-verified by hand). Rail 3c exactly: every
local check reads the parsed Python table and none of them can see the rendering.

Bisected against the judge:

| Witness | decide applications | as shipped | + `maxRecDepth 20000` | `List.getD` shape |
| --- | ---: | --- | --- | --- |
| `Fin 6`, 5 vars | 7,776 | **LEAN_REJECTED** | accepted | accepted |
| `Fin 5`, 5 vars | 3,125 | accepted | accepted | accepted |

The renderer emitted `set_option maxRecDepth` only for `n >= 7`. The real driver
is `n ** variables`, so a `Fin 6` table against a 5-variable goal fell through the
gap — the same axis mistake as the retired order-10 ceiling (rail 3b-ii). Fixed
with `DECIDE_MAX_REC_DEPTH_APPLICATIONS = 4_096`, chosen inside the measured band
so that every previously-accepted certificate stays **byte-identical** (the whole
accepted corpus is orders ≤ 6 with ≤ 4 variables, or order ≥ 7 which the old rule
already covered). Pinned by two tests, one of them end-to-end through
`solve_problem` so a plumbing break in `make_false_answer` cannot hide.

Worth stating plainly, because it generalises: **a coverage fix can expose a
rendering bug.** Lifting the constraint search's variable gate did not create the
`maxRecDepth` hole; it walked the solver into territory where the hole was
reachable. Re-judge what a widened search newly reaches, not only the rows you
were aiming at.

With the dual pass repaired, `hard2_0092` no longer goes anywhere near that
tier — it is `false:dual:false:witness:S5B`, **judge-accepted**, 313 bytes.

## Closing the gap: what worked, and what is genuinely out of reach

A second pass went after the 11 rows the ladder left. Two closed, and the other
nine now have a hard measurement against them rather than a guess.

### Closed: both FALSE holdouts, by distillation

`hard1_0062` and `hard2_0123` were never mathematically open — they need the wide
constraint tier's `standard`-effort budget. Measured at `standard`: both solved,
`false:constraint_fin8`, 426 bytes, in **315 s** and **405 s**, and both
**judge-accepted** (26.1 s / 6.7 s).

That made them the right distillation candidates, for a reason that is not "we
could not solve them": 405 s is more than a whole problem's average Marathon
budget spent re-deriving a 426-byte table the solver has already found. Distilled
they cost a dict probe — measured **0.0 s at `fast`**, oracle-verified, byte
identical to the judge-accepted text, and pinned in
`judge_verified_certs.jsonl` (56 entries). **Official skips 5 → 3.**

### Built: goal generalisation, which found the right candidate and still lost

The ladder's remaining failure was the *rung and pivot candidate set*, so the new
`goal_generalization_pivots` derives candidates from the goal instead of a fixed
list: a law G plus a substitution s with `G[s]` syntactically equal to eq2, so G
closes the goal by instantiation alone (`hlem <args>`, no chain search).

It works exactly as designed, and the **partial** abstractions are the point. On
`hard3_0214` (goal `x = ((x ◇ y) ◇ (z ◇ w)) ◇ y`) it produces
`a = ((a ◇ b) ◇ c) ◇ b` — **ETP's Eq267**, a genuine pivot for that row, weaker
than the maximal generalisation `triple_left` (which is in the fixed list and
measured unprovable), and in no list the solver had. Every candidate is verified
by substituting back, and each returned pair is kernel-checked in the gate.

**And it is still not enough.** With the generalisation available as a target,
`hard3_0214` does not close at `fast`. Producing the right candidate turned out
not to be the binding constraint — *proving* it is.

Two supporting measurements make that concrete:

- `hard2_0073` fails at **`deep`** effort too — 1336 s, every curated pivot, every
  generalisation, the full rung scan. Its projections do merge single-rule at
  ~40 s, but raising the explanation depth limit from 400 to 20,000 only moves the
  failure from "recursion too deep" to "explanation too long": the explanation is
  **over 20,000 steps**, so it was never a depth problem.
- eq1 for these rows admits **no critical pairs with itself**. The pattern has 4
  operations and every proper subterm has at most 3, so nothing overlaps; any
  proof must go through *expansion* (using eq1 right-to-left, which introduces two
  fresh variables per step). That is the search space Vampire explores to find
  ETP's proofs, and it is not one an e-graph seeded from the goal reaches. It also
  retires the "self-overlap helpers" idea that stood in the next-lever list: for
  this family there are no self-overlaps to seed with.

Two smaller tunings shipped alongside, both from the same measured fact that egg
wins are bimodal — seconds or never:

- the rung budget is capped at 6 s rather than effort-scaled, so `deep` examines
  ~7x more *laws* for the same clock instead of spending 44 s per law;
- the rung scan limit went 120 → 200, because ~172 of the 601 library laws survive
  the model filter on a frontier row and the tail was never reached where there
  was budget to reach it.

The generalisations run **after** the ladder's rounds, not interleaved. That
ordering is deliberate and was verified: `hard3_0204` wins at two rungs, so
anything that spends the clock rung discovery needs would cost a row that works
today. All six rows the ladder already solved reproduce **byte-identically** after
the restructure, `hard3_0204` still at `h2`.

### The implication graph, used properly — and what it proved

None of the remaining rows are open problems: the ETP has proofs for all of them,
and this repo vendors the full 4694² outcome matrix. Two ways to use it were
tried, and the difference between them is the useful part.

**The wrong way: walk the eq1 → eq2 path.** `etp_chain.py --mode chain` finds it,
via ETP's explicit edges where they exist and the matrix otherwise —
`hard3_0214` has a four-hop explicit chain
(Eq2042 ⇒ Eq2893 ⇒ Eq2671 ⇒ Eq2661 ⇒ Eq2692), `hard3_0314` goes through Eq5
(right projection), `evaluation_hard_0196` through Eq2 (collapse). But a path *in
implication order* is not a ladder: each law on it is a **consequence** of the
previous, so the first hop (eq1 to the strongest intermediate) carries all the
difficulty and everything after it is trivial. It reorganises the problem without
making it easier.

One thing that did come out of building it: rejecting *equivalent* intermediates
as "zero-length steps" is wrong. That filter made `hard3_0214` report no
intermediates at all while ETP's explicit graph has four — a chain through
equivalent forms is a sequence of cheap rewrites, which is exactly what is wanted.
Loops are prevented with a visited set instead.

**The right way: the exact set of eq1's consequences.** What a ladder needs is
*side facts* — laws that follow from eq1 and help prove the target without
implying it. Idempotence is the measured example: it unlocked `hard3_0266` and
does not imply that goal at all. `lemma_survives_models`, the shipped filter, can
only say "not obviously refutable"; the matrix says **derivable**. So
`etp_chain.py --mode ladder` enumerates `{M : eq1 ⇒ M}`, smallest first, and every
candidate is one that a complete prover would get.

That turns a fuzzy question into a sharp one, and the answer is a clean negative:

| Row | Smallest graph-verified consequences | Result |
| --- | --- | --- |
| `hard3_0214` (346 consequences) | `a ◇ a = a ◇ b`, `a ◇ b = a ◇ c`, `a = ((a ◇ a) ◇ a) ◇ a` | none provable in 60 s each |
| `hard2_0073` (all 4693 — eq1 forces collapse) | `a = b`, `a = a ◇ b`, `a = b ◇ a` | none provable, `deep` included |
| `hard3_0314` (1213) | `a = a ◇ a`, `a = b ◇ a` | none provable at `fast` |

`hard2_0073` got a targeted attempt on top of that, because it has a hand-derived
argument behind it. Its eq1 is `x = ((y ◇ (x ◇ z)) ◇ x) ◇ y`, i.e. `W ◇ y = x`
where `W` depends on `x`; so if right-column constancy (`u ◇ y = v ◇ y`) holds, the
left side depends only on `y`, hence so does `x`, hence every element is equal —
collapse, which closes any goal. The matrix confirms eq1 implies every equation, so
both constancy laws are derivable. **All six constancy variants tried
(`a ◇ b = c ◇ b`, `a ◇ b = a ◇ c`, `a ◇ b = c ◇ d`, `a ◇ a = b ◇ b`,
`(a ◇ b) ◇ c = (d ◇ b) ◇ c`, `a ◇ (b ◇ c) = a ◇ (d ◇ c)`) are unreachable at
120 s each.**

So the candidate set was never the problem, and now that is measured rather than
argued: given candidates that are *guaranteed* derivable, equality saturation
still cannot derive them. The limit is the proof search. `etp_chain.py` stays as
the instrument — any future improvement in that search can be pointed straight at
a list of candidates known to be reachable in principle.

### What remains, and why

Three official TRUE rows (`hard2_0073`, `hard3_0214`, `hard3_0314`) and six HF
TRUE rows. **All are known-true — the ETP has proofs and this repo vendors the
matrix that confirms it.** What is missing is a proof *our search can find*, and
that is now measured rather than inferred: given candidate laws the matrix
guarantees are derivable from eq1, equality saturation still cannot derive them
(13 candidates across three rows, at 60–120 s each, plus `hard2_0073` at `deep`
for 1336 s). eq1 also has no critical pairs with itself for this family, so there
is nothing for a completion-style engine to chew on either.

Closing them needs a different proof search — ordered superposition with term
indexing, which is what found ETP's proofs — or hand-derived certificates fed
through `distill_certs.py`. It does **not** need more clock, a wider candidate
list, or a better pivot heuristic; each of those was tried and measured this
session.

## Rails learned

- **A "hard frontier" is a mix of failure modes until you separate them.** Four
  of the 19 open rows were not proof-search problems at all. The 11-row skip list
  had one row that solved in 1.75 s, one that needed a search gate lifted, and
  six that needed a mechanism nobody had tried — and they all looked identical
  from the audit output.
- **When a long proof cannot be shortened, look for one that does not need to
  be.** Two sessions of next-lever notes pointed at compressing a 4510-step
  chain. The chain was incompressible; naming one lemma made the whole chain
  unnecessary.
- **Measure the failure mode before building the fix.** "`normal_0491` renders at
  135 KB" was recorded as a byte problem. It is a byte *symptom*; the cause is
  that the certificate shape could not name a lemma.
- **A wall-clock bound is only a bound where it is polled.** Three of this
  session's bugs were the same bug in three places: the clock checked once per
  outer loop level while inner work was unbounded (saturation's application list),
  a superlinear post-process with no bound at all (proof bridging), and a step
  budget sized for a different regime (explanation extraction). Each looked
  exactly like "this row is hard". This is the strongest argument yet for the
  long-standing step-count-budget item.
- **A portfolio that shares one deadline has no budget for its last stage.**
  `find_counterexample` also *returned* from the whole function when a primary
  pass hit the deadline, so the dual pass was skipped rather than shortened. Two
  independent defects with the same symptom, in eight lines of code.
- **A coverage fix can expose a rendering bug.** Widening the constraint search
  did not create the `maxRecDepth` hole; it walked the solver into territory
  where the hole was reachable, and the result was a `LEAN_REJECTED` certificate
  built from a provably sound table. When a search is widened, judge what it
  *newly reaches*, not just the row that motivated the change.
- **When a frontier list stops moving, suspect the list.** `hard2_0092` sat on
  the open-rows list for four sessions with the answer already in
  `WITNESS_TABLES`. Two guards, neither of them about the mathematics, kept it
  there — and both were visible only by running the row standalone and reading
  which route claimed it.
- **Producing the right candidate is not the same as being able to prove it.**
  Goal generalisation was built on the theory that the candidate set was the
  binding constraint. It demonstrably *is* the missing candidate — it derives
  ETP's own Eq267 for `hard3_0214` from the goal's structure — and the row still
  does not close. Worth keeping the mechanism (it is cheap, sound, and general)
  and worth being precise that it did not close the gap it was built for.
- **"Needs more budget" is a claim to test, not a conclusion to record.** Three
  rows were carrying the note "solves standalone / needs `standard`". Two of them
  did, and are now closed at every tier by distillation. The third,
  `hard2_0073`, fails at **`deep`** with 1336 s and the full candidate set — the
  note was wrong about it, and only running it at `deep` said so.
- **Check for critical pairs before planning a critical-pair lever.** The
  "self-overlap helpers" idea sat in the next-lever list for two sessions. For
  this equation family there are no self-overlaps at all: the pattern has 4
  operations and every proper subterm has at most 3, so nothing can overlap. One
  minute of structural checking would have retired it.
