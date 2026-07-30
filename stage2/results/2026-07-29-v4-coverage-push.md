# 2026-07-29 (v4) — coverage push: constraint witnesses, egg lemma targets, and the finOpTable ceiling

Triggered by 16 playground `TRUE INCORRECT` rows from the v3 solver. All 16 were
mapped, reproduced and root-caused; the fixes generalise into three new engines
and one hard rail nobody had written down.

## The 16 reported rows

Playground ids carry a label segment (`hard2_true_0073`); strip it to get the
local id. All 16 mapped, and the ETP outcome matrix agrees with the benchmark
label on every one.

Reproduced against the current solver at `fast` effort:

| Class | Count | Status |
| --- | ---: | --- |
| Already fixed since v3 | 3 | `hard3_0203`, `evaluation_normal_0094`, `hard2_0153` now solve |
| TRUE-labelled, still skipped | 7 | fell through to the Solo grind fallback |
| **FALSE-labelled, answered `true`** | 6 | **guaranteed misses** — a TRUE verdict on a FALSE row can never be accepted |

The six FALSE rows are the clearest loss: 363–847 s each, spent to submit
something unacceptable. `hypothesis_models_seen()` read 1050, 1272, 1349, 1352,
7698 and 2 on them — all above zero, so the existing
`fallback:skip_no_model_evidence` guard passed them straight through. **That guard
is not a TRUE signal**; it only catches the vacuous case.

## What was actually missing

### 1. A real countermodel search (`false:constraint_fin*`)

Every FALSE route was either a canned table (named witnesses, structured /
affine / quadratic families), bounded `Fin 2..3` enumeration, or a randomized
`Fin 4..6` hill-climb. All of them fail on the same family: laws
`x = F(x, ȳ)` with `x` once on the right. Those force **quasigroups** — a random
table essentially never satisfies one, and the smallest countermodel usually sits
at order 8.

Shipped a Mace4-style search: the n² Cayley cells are unknowns, every ground
instance of eq1 is a constraint, and partial evaluation gives unit propagation.
Two design points carry it:

- **Propagation must fire at the root only.** The first version assigned the
  *innermost* unknown cell the value of the other side — a different equation
  entirely — and reported "no countermodel" everywhere. Positive and negative
  controls (rows with known small witnesses; rows that are TRUE and therefore have
  none) caught it.
- **Order schedule, not smallest-first.** On `hard2_0009`, order 7 burned a 120 s
  budget and found nothing while **order 8 succeeded in 0.03 s / 40 nodes**.
  Difficulty tracks how well the order fits the algebra, not its size. Searching
  2,3,4,… wastes the whole budget on the worst orders.

Result on the 22 unsolved FALSE official rows: **17 countermodels, 17/17
independently verified sound**, 15 at order 8, one at 5, one at 6. Certificates
are 313–426 bytes. Four judge-verified `accepted` (11–16 s).

The same search also serves as *evidence*: `constraint_search_exhausted()` records
whether it finished every order or was cut off, so a log line can distinguish
"orders 8–10 hold no countermodel" from "we ran out of clock" — which is the
distinction `models_seen` never made.

### 2. Egg pointed at a lemma, not the goal (`true:egg_collapse`, `true:egg_bootstrap`)

ETP pivot mining over every unsolved official row found the dominant structure:
**14 of the 31 unsolved TRUE rows have `eq1 ⇒ (x = y)`** — eq1 forces a
one-element magma, so the goal is irrelevant and the whole problem is "prove eq1
collapses". `singleton_route` catches only the syntactic case; `lemma_bootstrap`'s
critical-pair closure derives none of them.

Egg does. Pointed at the collapse law: **10 of the 14, in 1.9–34.3 s**, every
proof kernel-verified. All 10 certificates **judge-accepted** (3.7–5.3 s),
1194–34207 bytes — including two above 33 KB, comfortably inside the 50 KB cap.

Generalised into two routes:

- `true:egg_collapse` — the collapse target, its own route and a 40 s budget
  because measured successes span 1.9–34.3 s and an 8 s cap drops most of them.
- `true:egg_bootstrap` — the same move over the whole 601-entry lemma library,
  with the free gates (`lemma_applies_to_goal`, `lemma_survives_models`) first so
  egg is only paid for on a law that would finish the proof.

Certificates use the existing kernel-checkable `lemma` shape, so
`check_true_lemma_certificate` replays both halves. No new oracle surface.

### 3. The LLM lane, and why it is not needed at inference time

`stage2/experiments/llm_lemma_egg.py`: the model names pivot laws, egg derives
them, the kernel checks them. On the 21 still-open TRUE rows — **4 solved, 0
kernel rejects, 34k tokens, ~200 s**. Reject reasons were
`does_not_close_goal` 50, `refuted_by_eq1_model` 18, `egg_cannot_derive` 13, so
the free gates absorb most of the model's output before egg spends anything.

But every law it found (`a ◇ b = a`, `a ◇ b = b`, `a ◇ b = c ◇ d`) is already in
the enumerated library, and **`egg_bootstrap` finds all four deterministically**
(`product_constant`, `enum291`, `enum291`, `enum292`, 5–20 s). So the LLM earned
its keep as a *discovery* tool — it told us which library entries matter — and the
shipped solver needs no LLM for these rows.

## The rail nobody had written down: witness order ≤ 10

Chasing `hard2_0051` produced the most important finding of the session.

Its countermodel is a clean algebraic construction: the linear model
`x ◇ y = 7x + 7y (mod 13)` over `Z₁₃`. Verified by hand, by both offline oracles,
and by the solver's own `table_is_counterexample` gate. The judge rejected it —
`LEAN_REJECTED`, with `decide` reporting the conjunction **false**.

Cause, in `vendor/stage2-official/judge/JudgeFinOp/MemoFinOp.lean`:

```lean
private def extractDigits (s : String) : List Nat :=
  s.toList.filterMap fun c =>
    if c.isDigit then some (c.toNat - '0'.toNat) else none
```

The table parser keeps **one value per digit character**. A cell holding `10`
becomes two cells, `1` and `0`, and everything after it shifts. Lean was checking
a different magma than we sent. Orders 2–10 use only single-digit entries and
round-trip cleanly; **order 11+ is silently corrupted**.

Building the magma from a formula instead would bypass the parser, and does not
work either: `fun i j => 7 * i + 7 * j` fails the proof policy with
`DISALLOWED_DECLARATIONS` on `HAdd.hAdd` / `HMul.hMul`, which have no allowlisted
prefix. So **`finOpTable` is the only sanctioned magma constructor and 10 is a hard
ceiling on FALSE witness order.**

This mattered immediately: the first version of the constraint search used orders
`(8, 9, 6, 4, 12)` and a wide tier including 12 and 16. Those would have emitted
certificates that pass every local check and fail in the field — precisely the
class of error this repo exists to prevent. Now:

- `MAX_WITNESS_ORDER = 10`, and `table_is_renderable()` is enforced inside
  `table_is_counterexample`, the single gate every FALSE witness passes through.
- `oracles.check_false_certificate` rejects multi-digit tables, so the offline
  harness can finally see this class at all. Every other check in that file reads
  the parsed Python table and is blind to it.
- A test asserts `MAX_WITNESS_ORDER == 10` and that every witness-order constant
  and every named table respects it.

Consequence worth stating plainly: a FALSE row whose smallest countermodel exceeds
order 10 is **unreachable** with table certificates. `hard2_0051` is such a row
(nothing at ≤ 9 by exhaustive search; the Z₁₃ model is real but unshippable), as
are `hard2_0093` and `hard2_0123` (nothing at ≤ 16).

## Measured result

Official sets, `fast` tier, diffed by row id against the pre-v4 baseline:

| | before | after | Δ |
| --- | ---: | ---: | ---: |
| solved | 1616 | **1647** | **+31** |
| TRUE | 788 | **803** | +15 |
| FALSE | 828 | **844** | +16 |
| rows lost | — | **0** | — |
| oracle failures / crashes / label mismatches | 0 | **0 / 0 / 0** | — |

Per set: `hard1` 68/69, `hard2` 191/200, `hard3` 392/400, `normal` 996/1000 —
**1647/1669 = 98.7%**, with 22 rows open (14 TRUE, 8 FALSE).

`egg_priority_bootstrap_route` landed after that audit and solves three more of
the 22 (`hard2_0082`, `hard3_0131`, `hard3_0271`), each verified individually and
kernel-OK, so the next full run should read ~1650.

Attribution of the +30: `false:constraint_fin8` ×14, `true:egg_collapse` ×9,
`true:egg_bootstrap` ×5, `true:lemma_chain` ×2 (knock-on from timing).

HF evaluation sets: **782 → 788**, TRUE 382 → 388, all six gains
`true:egg_collapse`, 0 lost, 0 oracle failures.

A later per-order budget fix for the wide constraint tier picked up three more
rows that the dev sweep could reach but the solver could not
(`hard1_0025` order 5, `hard2_0092`, `hard2_0125` order 6).

### Real-judge verification

Everything new was checked against the local Lean judge, not just the oracles:

| Batch | Result |
| --- | --- |
| `egg_collapse` certificates | **10/10 accepted**, 3.7–5.3 s, 1194–34207 bytes |
| `constraint_fin*` witnesses | **17/17 accepted**, 4.7–51.8 s, 313–426 bytes |
| earlier `*_block` certificates | 34/34 accepted (unchanged) |

## Method notes worth keeping

- **Validate a search with controls before believing its negative results.** The
  propagation bug produced confident "no countermodel ≤ 6" answers. Rows with
  known small witnesses (must find) and TRUE rows (must find nothing) exposed it
  in one run.
- **A sound witness is not a shippable witness.** Three independent local checks
  agreed on the `Fin 13` table. The gap was the judge's *parser*, which nothing
  local modelled.
- **Difficulty is not monotonic in model order.** 0.03 s at order 8 versus 120 s
  exhausted at order 7, same row.
