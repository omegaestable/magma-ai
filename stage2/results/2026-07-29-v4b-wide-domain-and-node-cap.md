# 2026-07-29 (v4b) — wide-domain witnesses, and a node-cap bug found chasing them

Direct follow-up to the same day's v4 push. The user asked what to do about
`hard2_0051`, `hard2_0093`, `hard2_0123` — flagged as unreachable because their
smallest known countermodel exceeds the judge's order-10 rendering limit. This
session re-examined that claim, found it was half right, and along the way
found a real bug that fixed two of the three.

## The claim was imprecise, not wrong

`MemoFinOp.finOpTable`'s parser (`extractDigits`) keeps one value per digit
character and computes `(vals.getD idx 0) % n`. Since every extracted digit is
0-9 and `d % n == d` whenever `n > d`, **the actual invariant is single-digit
cell VALUES, not order**. Order ≤ 10 is only a corollary for a *complete* Cayley
table (entries spanning the full `0..n-1`) — which is what every existing FALSE
route produces, so the practical effect on this repo's rows was correct, just
not the deepest true statement.

**Confirmed against the real judge**: a `Fin 13` magma `op(i,j) = (i+j) mod 10`
— carrier size 13, every output restricted to < 10 — round-trips correctly and
was **`accepted`** in 78.1 s. So a table can exceed order 10 as long as its cell
values stay single-digit.

## Why it still can't rescue this frontier

Every currently-unsolved FALSE row has `eq1: x = F(...)` — a bare variable
alone on one side. That variable is universally quantified over the *full*
carrier `Fin n`. Once it exceeds 9, the equation demands `F(...) = x >= 10`,
impossible for an operation whose output is capped at 9 by construction. No
wide-domain table can ever satisfy this equation shape at order > 10 —
provably, not just empirically. `_eq1_has_bare_variable_side()` detects it for
free before spending any search.

Checked all five remaining unsolved FALSE rows: **all five** have this shape
(`hard1_0062`, `hard2_0027`, `hard2_0051`, `hard2_0093`, `hard2_0123`). So the
technique, while real, doesn't apply to today's frontier at all — it's shipped
as `constraint_countermodel_wide_domain` (orders up to 60, value-capped at 10)
for the *general* corpus (any FALSE row without a bare variable on either side
of eq1), end-to-end validated including a real-judge accept on a synthetic
commutative-law test.

## The node-cap bug

Empirical confirmation of the structural argument (searching order 13 for
`hard2_0051`) explored 74,787 nodes in 15 s without resolving — propagation
only discovers the fatal `x >= 10` contradiction once enough of the table
happens to be filled in, so the impossibility isn't obvious to the search even
though it's obvious on paper.

That led to a decisive push: a genuinely large per-order budget (120 s, vs. the
40 s used in the earlier sweep) on all five bare-variable rows, orders 2–10.
**Two found real witnesses**: `hard1_0062` and `hard2_0123`, both at order 8,
71–74 s each. The other three (`hard2_0027`, `hard2_0051`, `hard2_0093`) ran
the full budget across every order (671–737 s) and found nothing — much
stronger evidence of genuine non-existence than the earlier 40 s sweep.

Reproducing `hard1_0062` through the *shipped* solver (not the dev tool)
returned nothing in the same budget. The cause: `CONSTRAINT_MAX_NODES = 60000`
in `_cp_search` — a node budget the standalone dev tool (`mace_finder.py`)
never had — was cutting the search off before the time deadline that already
bounds it correctly. Direct test: raising the cap to 2,000,000 found the same
witness in 83.1 s / 138,225 nodes, independently re-verified.

**The node cap was always redundant with the time deadline** (checked every
node already) and, at 60,000, strictly more restrictive. Raised to
`3,000,000` — a pure safety net now, comfortably above what even a `deep`-tier
per-order budget (990 s at ~1,650 nodes/s measured) could reach.

## Result

Both new witnesses are order-8, 426-byte certificates, **real-judge accepted**
(4.7 s and 5.3 s). Verified at `standard` effort through the actual
`constraint_countermodel` call path the solver uses, not just the raw search
function.

| Row | Order | Judge | Time |
| --- | ---: | --- | ---: |
| `hard1_0062` | 8 | accepted | 4.7 s |
| `hard2_0123` | 8 | accepted | 5.3 s |

**Effort tier matters here and is easy to get wrong.** `egg_priority_bootstrap`
(three TRUE rows, from the same-day v4 session) already solves at `fast`
effort, so it counts toward the standard `fast`-tier audit headline. The two
node-cap rows do **not**: at `fast`, the wide constraint tier's per-order
budget is 45 s with no scaling, and both rows need ~75 s — they only finish at
`standard` effort (45 s × 7.5 = 337.5 s) or above. Confirmed by testing both at
`fast` (SKIP, matching a `fast`-tier audit) and `standard` (solved, 76.2 s /
71.4 s) through the actual `constraint_countermodel` call path. They are real
and real-judge-accepted, but belong to Solo/Marathon's effort-scaled budget or
a `--effort standard` sweep, not the `fast`-tier headline number.

## Confirmed: no regression, `fast`-tier headline unchanged at 1650

A first full-audit confirmation run showed 16 "lost" rows against the pre-fix
baseline — alarming, until traced to an unrelated diagnostic audit
(`--set hard1 --workers 4`, launched to investigate a suspicious hard1 TRUE
count) that overlapped a large chunk of it. Every "lost" row was a
budget-marginal `egg_*`/`lemma_chain`/wide-constraint-tier route — exactly the
routes the golden fixture excludes for being wall-clock nondeterministic under
load — and every one reproduced its original route on a clean, isolated rerun.

A genuinely clean, isolated `audit_corpus.py --all` (no concurrent jobs) came
back **row-for-row identical** to the pre-node-cap-fix baseline: **0 lost, 0
gained, 1650/1669 solved, TRUE 806, 0 oracle failures, 0 crashes.** The node
cap fix is confirmed to cause zero regression at the `fast` tier; it simply
doesn't reach the two rows it fixes at that tier (see above).

**New rail from this**: never run two `audit_corpus.py` sweeps concurrently —
16-worker pools sharing cores produce spurious double-digit "losses" on
timing-sensitive routes that are not real. See `CLAUDE.md` for the current
confirmed `fast`-tier total.

## Still open

Three FALSE rows remain genuinely hard, now with much stronger negative
evidence: `hard2_0027`, `hard2_0051`, `hard2_0093`. All share the bare-variable
shape, so no order > 10 witness can exist for them under the judge's rendering
constraints, and an extensive (671–737 s, uncapped-node) search found nothing
at order ≤ 10 either. Not proven unreachable with mathematical certainty — the
search, while sound and complete given enough budget, wasn't run to guaranteed
exhaustion — but the evidence is now much stronger than "we didn't look hard
enough."

## Lesson

The user's instinct to push back on "unreachable" was right, but not for the
reason initially suspected (the wide-domain technique doesn't apply here). The
value came from taking the investigation seriously enough to (a) validate the
theory against the real judge before trusting it, (b) work out the precise
mathematical boundary of when it applies, and (c) notice, while pushing a
decisive search, that a bug — not a genuine limit — was sitting in the way of
two solvable rows. Chasing a dead end thoroughly is what surfaced a live one.
