# P2 — the existential decoder, framed by the orchestrator (deep session 8)

Blocks **21865 (2 rows), 21866 (2), 22591 (3), 23357/23653 (2), 21864/24199 (2)** = 11 rows.
`gen/PLAYBOOK_QUOTIENT.md` §4 states the obstruction. This file adds four results derived and checked this
session, which change what the mechanism has to be. Work law **22591** first — it is the one with a concrete
refutation instance on file, and it has 3 rows.

`22591:  x = (y * (y * x)) * ((x * x) * z)`

Write `S(x) = x*x`, `T(x) = {y*(y*x) : y in M}` (the DECODER set of x),
`E(x) = S(x)*M` (the ENCODING set of x). The law says exactly

    (*)   A * b = x   for every A in T(x) and every b in E(x).

---

## R1. Every element of a 22591-magma is a square. (checked)

Substitute `y := x*x` and `z := (x*x)*x` into the law. Then with `S = x*x`:
`A = y*(y*x) = S*(S*x)` and `B = (x*x)*z = S*(S*x)`. So `A = B` and the law reads

    x = W * W        with W = S*(S*x),  S = x*x.

So `S : M -> M` is **surjective**, and `im S = M`.

**Consequence — this kills the whole family of "recognizable square" carriers.** The construction that ships
12073 and 27859 works by making the square map `S` injective and recognizable (`S(x) = sigma(x)` for an
injective constructor `sigma`), so that the encode rule `op(sigma x, z) = eps x` can read `x` off its left
argument for every `z`. Here `im S = M`, so that encode rule fires on **every** left argument, and the decode
rule `op(A, eps x) = x` can then never fire. Any carrier in which squares are recognizable and invertible is
therefore refuted a priori. Do not build one. (This is the same conclusion `PLAYBOOK_QUOTIENT.md` §4 reaches
for square *collapse*; R1 extends it to square *recognition*, which is the weaker property the free-model
construction actually relies on.)

## R2. 22591 has NO linear and no affine model over any abelian group. (proved)

Let `a*b = p a + q b + c` with `p, q` endomorphisms of an abelian group (not assumed to commute), `c` constant.
Expanding the law and matching coefficients:

    z:   q^2 = 0
    y:   p^2 + p q p = 0
    x:   p q^2 + q p^2 + q p q = 1
    const: (pq + p + qp + q + 1) c = 0

From `q^2 = 0` the x-equation is `q p^2 + q p q = 1`; from the y-equation `p^2 = -p q p`, so
`-q p q p + q p q = 1`. Left-multiply by `q`: the left side is `-q^2 p q p + q^2 p q = 0`, the right side is
`q`. So **`q = 0`**, and then `q p^2 + q p q = 0 != 1`. Contradiction.

The linear part is what fails, so the affine case dies with it, and so does every **Z-grading**
`deg(a*b) = alpha deg a + beta deg b + gamma` (same equations with scalars). This closes, with a proof rather
than a timeout, the affine-over-Q / Z-piecewise-linear / graded families for 22591.

## R3. The payload must be read from the DECODER side, not the encoding side — and for 22591 it cannot be read from either. (checked against the recorded refutation)

The extractor (`closedform.py` docstring, and `gen/EXTRACTOR_NOTES.md` FIX-1) always reads the payload out of
the *encoding* side and puts the nested `op` guard on the other. For 22591 the payload occurs on both sides:
in `u = y*(y*x)` at `a2 a2 u`, and in `v = (x*x)*z` inside `x*x`.

Replay of the recorded refutation instance under the rule "read `x = a2(a2 u)`, guard `op(x,x) = a1 v`",
with `x = ((g0*g0)*((g0*g0)*g0))`, `y = (g0*(g0*g0))`:

| product | value | why |
| --- | --- | --- |
| `op(y,x)` | `g0` | `y = J g0 (J g0 g0)` is a legal decoder of `g0`; `a1 x = J g0 g0 = op(g0,g0)` |
| `op(y, g0)` | `J y g0` | free, `g0` is not a J-node |
| `op(x,x)` | `g0` | `x` is simultaneously a legal decoder AND a legal encoding of `g0` |
| `op(g0,z)` | `J g0 z` | free |
| law RHS | `J (J y g0) (J g0 z)` | free |

which is the instance in `PLAYBOOK_QUOTIENT.md` §4 exactly. **Both `op(y,x) = g0` and `op(x,x) = g0` are
genuinely forced by the law** — they are not modelling artefacts: `y in T(g0)`, `x in E(g0)`, `x in T(g0)`.
So the law then *forces* `op(J y g0, J g0 z) = x` for every `z`, and that pair carries the payload on
neither side: `a2 u = op(y,x)` decoded (so `x` is gone from `u`) and `a1 v = op(x,x)` decoded (so `x` is gone
from `v`). That is the existential decoder, stated precisely.

## R4. The witness is UNIQUE and CONSTRUCTIBLE — the quantifier is eliminable. (checked on the instance)

The missing rule needs an `x` with

    op(a1 u, x) = a2 u        and        op(x, x) = a1 v.

The second constraint alone determines `x`. Take the instance: `a1 v = g0`, so we need `op(x,x) = g0`, i.e.
`(x,x) in T(g0) x E(g0)`, i.e. `x in T(g0) ∩ E(g0)`. Unfolding both memberships structurally:

* `x in E(g0)` gives `x = J (op(g0,g0)) z' = J (J g0 g0) z'`;
* `x in T(g0)` gives `x = J w q` with `op(w, g0) = q`, hence `w = J g0 g0` and
  `q = op(J g0 g0, g0) = J (J g0 g0) g0` (free, since `g0` is not a J-node);

so `x = J (J g0 g0) (J (J g0 g0) g0)` — **exactly the refutation's `x`, and it is the only solution.**

So the mechanism to build is not an unbounded existential. It is an **inverse-decode function**

    invsq(s)  =  the unique x with op(x,x) = s

defined by structural recursion on `s`, mirroring the decode rules: for each rule whose result is `s`,
invert its reading to a term built from `s`, and take the branch whose guards hold. `op(x,x) = s` has a free
solution `x = a1 s` when `s = J x x`, and a decoded solution obtained by unfolding `T(s) ∩ E(s)` as above.
The new rule is then

    op(u, v) = invsq(a1 v)      guarded by   tg u = 2, tg v = 2, op(a1 u, invsq(a1 v)) = a2 u

which is an ordinary nested-`op`-guard rule of the existing DSL shape, plus one extra recursive function on
the carrier. In Lean that is one more `def` by well-founded recursion on `sz` alongside `op`, and one more
branch in `op_cases`.

**A rule of this shape is a function of `(u,v)` again**, so the "no rule can separate two forced readings"
argument of `PLAYBOOK_QUOTIENT.md` §4 does not apply to it: it does not try to separate the two readings, it
*computes with both of them*.

---

## What to do

1. Build `invsq` for 22591 in Python first, inside a private copy of the model, and check it is well defined
   (single-valued) and terminating on the pools `revalidate.py` already uses.
2. Re-validate to the wave-3 standard: `rv.run_tests(law, rules, [3,4,5], 3000, 12000)` empty, `cf.deep_tests`
   at 20,000 on >= 3 seeds, then the case tree (`gen/_x38565_dd.py` is the worked example) and
   `qz_lib.identity_probe`.
3. Only then Lean. The recursion needs its own measure lemma; `sz (invsq s)` is NOT bounded by `sz s`, so
   the termination argument for `op` has to be redone — check that first, it is the one thing that can kill
   this. If `invsq` cannot be shown terminating, the fallback is to make the *number of decode levels* the
   measure instead of term size.
4. If it works for 22591, the same rule form is what 21865, 21866, 23357/23653 and 21864/24199 need
   (`PLAYBOOK_QUOTIENT.md` §4 names them as the same mechanism). 21866 is the outlier (18,515 one-generator
   failures) — do it last.

## Stop condition

If the mechanism does not exist, the deliverable is the written argument for why, in the style of R1/R2
above — a proof, not a timeout.

---

## R4 verified, and one honest negative

**Verified by the orchestrator** (self-contained replay, free carrier `g n | J a b`, single DEC rule
"read `x = a2(a2 u)` from `u = J y (J y x)`, guard `tg v = 2` and `a1 v = op(x,x)`"):

* R3's table reproduces exactly: `op(y,x) = g0`, `op(x,x) = g0`, and the law's RHS evaluates free instead of
  to `x`.
* **The closed form is right.** `invsq(s) := J (op s s) (J (op s s) s)` satisfies `op(invsq s, invsq s) = s`
  on **8 / 8** targets tried (generators, `J g0 g0`, `J g0 g1`, `J (J g0 g0) g0`, `J g0 (J g0 g0)`,
  `J (J g0 g0) (J g0 g0)`, `J (J g0 (J g0 g0)) g0`), and `invsq(g0)` is *literally* the refutation's `x`.
  So **the existential quantifier is eliminable, and not merely bounded — it has a closed form with one
  recursive `op` call on a strict subterm `s = a1 v`.**
* The guard also needs no recursive call. With `s := a2 u = a1 v` and `x := invsq s`, the condition
  `op(a1 u, x) = a2 u` reduces (by DEC, whose `v`-guard `a1 x = op(s,s)` holds by construction of `invsq`) to
  the purely **structural** test "`a1 u` has decoder shape with payload `s`":
  `tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ a1 (a1 u) = a1 (a2 (a1 u)) ∧ a2 (a2 (a1 u)) = s`.
  So the new rule is an ordinary DSL rule: structural conditions plus `op` on a subterm. **Termination is
  therefore NOT the obstacle I feared** — `sz (invsq s)` grows, but `invsq` is not recursive and the only
  `op` call is on `a1 v`.

**The honest negative.** Bolting that rule onto the one-rule toy above makes the toy *worse*
(507 → 951 failures over the 197 one-generator terms of size ≤ 7, all `z` in the first three). That is a
statement about the toy, not about the mechanism: a single DEC rule is not 22591's model. **Do the experiment
against `gen/q22591b.py`** — the real model, which already survives 1,061,208 exhaustive assignments at
size ≤ 7 and 5,722,200 with `y ≤ 9` and fails only on the R3 instance family. Add the rule there, in rule
order, and measure. The lesson from the toy is that the new rule must be placed and guarded so it fires
**only** when both readings have genuinely destroyed the payload, i.e. after every rule that can still read it.
