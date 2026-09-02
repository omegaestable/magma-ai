# NOTES 6912 / 39214 — wave-3 gate-cut agent, 2026-08-29 (deep session 8)

Law 6912 (catalog, L-form): `x = y * (y * ((z*z) * (x*y)))`
Law 39214 (catalog): `x = (((y*x)*(z*z))*y)*y` — the **dual** of 6912 (`smallcheck` reports
`dualized: true`, and its semantic failure is byte-identical to 6912's).

Rows: `research_order5_hard_0049` (6912:28770), `_0091` (6912:15535), `_0026` (39214:41082).

---

## HEADLINE — the classification in `gen/SEMANTIC_TABLE.md` is WRONG for these two laws

`SEMANTIC_TABLE.md` files 6912 and 39214 as **"near-clean, 1-2 instances"**, i.e. a repairable
extractor/gate-cut hole (Track B). They are not.

> **THEOREM (mechanically verified, `gen/_x6912_derive2.py`, re-run this session — every step is a
> literal substitution instance of the law or a rewrite by an already-derived equation):**
>
> **6912 ⊢ (a\*a) = ((a\*a)\*(a\*a))** — every square is idempotent, **and**
> **6912 ⊢ (b\*b) = (a\*a)** — *all squares are equal.*
>
> So 6912 implies there is a constant `e` with `a*a = e` for every `a`, `e*e = e`, and the law reduces
> to the two-variable law `x = y * (y * (e * (x*y)))`.

That script was written by an earlier agent and left unused; its `assert`s all pass. The derivation
(`u = a*a`, `v = u*u`, `S = v*v`, `w = b*b`):

```
F1  x=u,y=u,z=u              u = u*(u*S)
F2a x=u,y=S,z=a  + rw F1     u = S*(S*u)
F3a x=S,y=u,z=v  + rw F2     S = u*v
F4a x=u,y=v,z=a  + rw F3     u = v*(v*(u*S))
F5  x=v,y=v,z=a              v = v*(v*(u*S))      => (I)  u = v,   a*a = (a*a)*(a*a)
G1a x=u,y=u,z=b  + rw (I)    u = u*(u*(w*u))
G2  x=w,y=u,z=a              w = u*(u*(u*(w*u)))
G3  rw by G1                 w = u*u = v
G4  rw by (I)                w = u                => (II) b*b = a*a
```

Consequences:

1. **The free term algebra is refuted as a carrier**, over two or more generators: it has two distinct
   squares `J g0 g0` and `J g1 g1`. This is Track C (`gen/PLAYBOOK_QUOTIENT.md`), the same
   reclassification 34889 got this session, and for the same reason.
2. `python smallcheck.py 6912 9 1` = **1 fail**, `6912 5 2` = **0 fails**: the two-generator witnesses
   of (II) need terms of size ≥ 9, so the cheap exhaustive sweeps do not see them. **A low semantic
   failure count is not evidence of Track B.** (34889 read 2, 21864 reads 5, 40037 reads 1 — all four
   deserve this derivation before any rule work.)

### The single semantic failure is a GATE CUT, and it is a symptom of (II), not the disease

`gen/_y6912_sem.py` traces it. Instance `y = ((g0*g0)*(g0*(g0*g0)))`, `z = g0`, `x = (g0*g0)`:

```
  op(g0, g0)                                       = (g0*g0)                       [FREE]     S = z*z = c
  op(c, y)                                         = (c*y)                         [FREE]     A = x*y
  op(c, (c*y))                                     = g0                            *** DECODE  S*(x*y)
  op(y, g0)                                        = (y*g0)                        [FREE]     C
  FINAL op(y, (y*g0))                              = (y*(y*g0))   expected (g0*g0)  *** FAIL
```

The DECODE is genuine (reading `y'=c, z'=g0, x'=g0` reads `op(c, J c (J c (J g0 c))) = g0` off the law),
and the FINAL pair **does** have a reading (`y''=y, z''=g0, x''=c`) — `freemodel.Free` cannot use it
because verifying it needs `op(c, op(c,y))` whose measure `(13,16)` is not below the bound `(11,20)`:
`Free.opb` cuts it (`cuts 26` in the trace). So the failure is a search cut, *and* the model it would
have produced is refuted anyway by (II) at two generators. Do not spend time repairing the cut.

---

## The E-quotient carrier (`M ::= g n | E | J a b`, `op u u = E`) is ALSO refuted — measured

Since (II) forces square collapse, the obvious Track-C carrier is the free magma plus a nullary `E`
(the 12073 / 27859 / 34889 carrier). It does not work for 6912.

`gen/_y6912_qfix.py` is the least-fixed-point prober (the `gen/qfix.py` method): base `op u v = E` if
`u = v`, else the forced-entry table, else `J u v`; every `(x,y)` pair forces one entry
`op(y, C) = x` with `A = op(x,y)`, `B = op(E,A)`, `C = op(y,B)`.

| pool | rounds | entries | **collisions** |
| --- | --- | --- | --- |
| size ≤ 5, 1 gen (22 terms) | 2 | 483 | **0** |
| size ≤ 9, 1 gen (550 terms) | 3 | 302,526 | **5 (2 distinct)** |
| size ≤ 7, 2 gens (471 terms) | 3 | 221,848 | **10 (4 distinct, 2 per generator)** |

The two distinct collisions, verbatim:

```
op(((E*(g0*E))*g0), (((E*(g0*E))*g0)*E)) = (E*(g0*E))   AND   ((E*(g0*E))*g0)
op((g0*(E*(E*g0))), ((g0*(E*(E*g0)))*E)) = (g0*(E*(E*g0)))  AND  g0
```

**Why it is irreparable (a rule is a function of `(u,v)`).** Two instances of the law demand different
values of the *same* pair:

* `op(t,t) = E` and `op(E,E) = E`, so for `x = y = t` the chain is `A = E`, `B = E`, `C = op(t,E)`, and
  the law forces `op(t, op(t,E)) = t`.
* if `op(q,t) = E` for some `q ≠ t`, the chain for `x = q`, `y = t` is the same three products, so the
  law forces `op(t, op(t,E)) = q`.

Hence **`op(q,t) = E ⟹ q = t`** is forced (`R_t` is injective — that also follows directly from the
law). The collisions are exactly witnesses of `op(q,t) = E` with `q ≠ t`, and each is forced:

```
q := (E*(g0*E)) = e*(g*e)              t := q*g
op(E, q)        free
op(E, (E*q))    = g0     -- FORCED: (E*(E*q)) is the code C(g0,E) of g0 under y=E
op(q, g0)       free = t
op(q, t)        = E      -- the law at x=E, y=q
```

The equational form of the obstruction, derived from the law + square collapse:

```
(III)   y = y * (e * (e * y))          for every y
```

(from `x := e`: `e = y*(y*(e*(e*y)))`, and `op(a,b) = e ⟹ a = b`.) (III) is fine as a *syntactic*
rule `op(u, J E (J E u)) = u` only while `e*(e*y)` is the free term `J E (J E y)`. It is not: for
`y = e*(e*(g*e))` the law already forces `e*(e*y) = e*g`, so (III) demands `y = y*(e*g)` — a further
identification, and the quotient **cascades** (this is the same cascade `PLAYBOOK_QUOTIENT.md` §2
records for argument-carrying tags). Expressing (III) with a semantic guard `op(E, op(E,u)) = v` puts
the inner pair above the recursion measure — GATE CUT again.

`gen/_y6912_e.py` is a hand-built candidate on that carrier (5 purely structural rules, no nested `op`
at all, so no gates and no recursion). It gets `op(z,z) = E` for all z and `op(a,b) = E ⟹ a = b` clean,
and **13 fails out of 10,404** at size ≤ 7 / 1 gen. The failures come in three shapes, and each needs
one more rule that inverts a *decoded* `A = op(x,y)`:

```
R6 : v = J u (J E w),  u = J E (J E w)          -> w      (A decoded by the (III) rule)
R7 : v = J u (J E w),  u = J p (J E (J w p))    -> p      (A decoded by the main decoder)
R? : v = J u (J E w),  u = J E (J E (J w E))    -> E      (A decoded, payload E)  <-- BREAKS
```

The third one has result `E` with `u ≠ v`, which violates `op(a,b) = E ⟹ a = b` and re-creates the
collision. That is the wall, and it is the same wall the fixed-point prober hits.

---

## Verdict and the next move

**Track C, and NOT the plain E-quotient.** Both the free carrier and the free+E carrier are refuted,
each with an explicit witness. What is left, in the order I would try it:

1. **A carrier in which `e*(e*y)` is a constructor, not a term.** (III) says `L_e²` composed with
   `R_?` is forced; a unary code constructor `C m` (the `gen/qz_m24.py` / `PLAYBOOK_QUOTIENT` §3(c)
   design, built *from the theorem* rather than from the extractor) is the natural shape:
   `op(y, C(y)) = e`, `op(e, ...)` folded into the constructor. Note §2's warning that an
   argument-carrying tag cascaded for 12073 — check the cascade with `gen/_y6912_qfix.py` (change
   `Fix.op`'s base; it takes about ten lines) **before** writing any Lean.
2. **Check whether 6912 forces the trivial magma.** It is close: `L_y² ∘ L_e ∘ R_y = id` for every `y`,
   all squares are one idempotent `e`, `R_y` is injective and `L_y` is surjective for every `y`.
   Two negative results measured here: no model of the form `x◇y = f(x) - f(y)` on an abelian group
   with `f` a homomorphism (the conditions `φ⁴ = -1` and `φ² = φ - 1` force `id = 0`), and none of the
   form `α(x)α(y)⁻¹` on a group (forces abelian, then the same). If it does trivialise, these three
   rows are **impossible for the whole free/quotient family** and should be reported as such — that is
   the 22591 outcome (`PLAYBOOK_QUOTIENT.md` §4) and it is a useful, decisive result.
3. Only if 1 and 2 both fail: the existential decoder (`gen/P2_MECHANISM.md`).

**Do not re-run** (measured this session): repairing the gate cut on the free carrier (refuted by (II)
at two generators, whatever the rules); the plain E-quotient (collisions above); `trace.py 6912`
(reports "no failure found" at `--n 400`, because the *extracted* 14-rule system happens to dodge the
sampled instances — it cannot be right, by (II)).

39214 needs no separate work: it is 6912's dual, `dualcert.py` transplants an accepted 6912
certificate to row 0026, and its semantic failure is the same instance dualised.

## Files written this session

| file | what |
| --- | --- |
| `gen/_y6912_qfix.py` | least-fixed-point prober for the E-carrier; prints collisions + entry-shape census |
| `gen/_y6912_e.py` | hand-built 5-rule E-carrier candidate (fully structural), exhaustive law test |
| `gen/_y6912_sem.py` | step-by-step trace of the single semantic free-model failure (the gate cut) |
| `gen/_x6912_derive2.py` | (pre-existing, re-run) the mechanical derivation of (I) and (II) |

## Addendum — no finite model at orders 2 or 3

`gen/_y6912_fin.py <n>` enumerates tables with the forced constant diagonal (`a*a = e` for one `e`,
which (II) makes mandatory) and tests the law: **order 2 → 0 models, order 3 → 0 models** (the constant
magma is not a model for `n ≥ 2`). Consistent with the research set's "no finite countermodel"; it
does not settle whether 6912 forces the trivial magma, which is open question 2 above. Order 4 was
not run (4^12 leaves with no pruning is too slow in Python; add early pruning if it is wanted).

---

# SESSION 2 — the triviality question (coordinator task 2). VERDICT: still OPEN, but four independent negative results

The question: does 6912 force `x = y`?  If it does, rows 0049 / 0091 / 0026 are **TRUE**, a collapse
proof is directly shippable with `judge1.py ... --true`, and no FALSE certificate exists for anyone.

## 1. Finite models must be UNIPOTENT QUASIGROUPS — and there are none up to order 6

With all squares collapsed to one `e` (session 1's theorem) the law is `x = y*(y*(e*(x*y)))`.
Writing `t[a][b] = a*b`, for each fixed `y` it reads

```
row_y ( row_y ( row_e ( col_y (x) ) ) ) = x        for every x
```

A composite of maps equal to the identity **on a finite set** forces every factor to be a bijection.
So in any finite model: every column is a permutation, every row is a permutation, and the diagonal is
constant. That is a **unipotent Latin square** satisfying `row_y ∘ row_y ∘ row_e = (col_y)⁻¹`.

`gen/_y6912_quasi.py <n>` is the DFS over exactly those. Measured:

| order | models | time |
| --- | --- | --- |
| 2 | 0 | 0.0 s |
| 3 | 0 | 0.0 s |
| 4 | 0 | 0.0 s |
| 5 | 0 | 0.0 s |
| 6 | 0 | 25.1 s |
| 7 | 0 found, **TIMEOUT at 540 s** (incomplete) | 540 s |

(The earlier `gen/_y6912_fin.py`, which only fixed the diagonal, agrees at orders 2–3.)

## 2. No affine model over any commutative ring — proved, not searched

Try `x ◇ y = a·x + b·y + c` over a commutative ring. `a ◇ a = e` for all `a` forces `b = -a`, `c = e`.
Substituting into the law and equating coefficients gives **`a⁴ = -1`** and **`a² = a - 1`**.
From the second, `a³ = a² - a = -1` and `a⁴ = -a`; the first then gives `-a = -1`, so `a = 1`, and
`a² = a - 1` becomes `1 = 0`. So only the trivial ring. The same computation with `a` an endomorphism
of an abelian group (`x◇y = α(x) - α(y)`) gives `α = id` and then `id = 0`. Also checked:
`x ◇ y = α(x)·α(y)⁻¹` on a group forces the group abelian (`α⁴(x) = x⁻¹` must be an automorphism) and
then reduces to the previous case.

## 3. Ordered completion does not derive the collapse — but this is WEAK evidence, and here is why

`stage2/experiments/completion/kb2.py` (the repo's own engine, the one that closed the 2026-08-12 rows):

| goal from 6912 alone | result |
| --- | --- |
| `(x*x)*(x*x) = x*x` (square idempotence) | **DERIVED in 0.1 s, 4 active** — an independent confirmation of session 1's derivation (I) |
| `x*x = y*y` (all squares equal) | **not derived in 120 s / 538 active** — although it IS a consequence (`gen/_x6912_derive2.py` proves it in 7 literal instantiations) |
| `x = y` (collapse) | not derived in 120 s / 552 active |

**The middle row is the point.** The engine misses a known consequence at this budget, so its failure
on the collapse carries little weight. Do not quote "completion did not derive it" as evidence without
that control.

### A trap worth recording: a "saturation" that fails on its own axiom

Adding the two derived facts as extra axioms (sound — they are consequences) makes the run
**"saturate in 4 steps with 7 active equations and `dropped_by_size = 0` at max_size 50, 90 and 140"**,
and `x = y` is not joinable. Read naively (CLAUDE.md's "free signal": saturation with no dropped pairs
⇒ a ≥2-element model exists ⇒ no collapse) that is a proof that 6912 is non-trivial.

**It is not.** `gen/../tmp` control run: in that same saturated system,
`x*x = y*y` — an **axiom of the run** — reports *does NOT join*, and so do `(III)` and `(IV)`, both
proved by hand. `joinable` normalises both sides with the orientable rules only, and `x*x = y*y` cannot
be oriented by KBO, so it is never applied. The passive queue emptying is not unfailing saturation.
**Always test a saturation claim against a known consequence and against an axiom of the run before
using it.** (Positive-control discipline, rail 5c, in a new place.)

## 4. Where this leaves the three rows

**Verdict: 6912 is not known to be trivial, and no non-trivial model is known either.** The evidence
leans against triviality (no affine model of any kind; the collapse is not derivable at the budgets
tried while a weaker identity is; the free and free+E carriers are refuted for *structural* reasons —
a cascading quotient — rather than by a collapse). But no finite model exists at orders ≤ 6, so if a
model exists it is infinite or large.

Ranked next moves:

1. **Settle the collapse with a real unfailing-completion tool**, not kb2 with a joinability test:
   the check must handle unorientable equations (ordered rewriting with instance orientation). The
   positive control is `x*x = y*y` — any tool that cannot derive that from 6912 is not strong enough
   to be trusted on `x = y`.
2. **Finish the order-7 unipotent-quasigroup search** (`gen/_y6912_quasi.py 7`, currently 540 s and
   incomplete). Better: build it from the derived identity instead of filtering — the constraint
   `row_x(y) = g⁻¹(row_y⁻²(x))` with `g = row_e` determines the whole table from the rows, and
   `row_y²(0) = y`, `row_x(0) = g⁻³(x)` are forced; that is a much smaller search and reaches orders
   8–10.
3. Only then the unary-code carrier of `PLAYBOOK_QUOTIENT.md` §3(c).

## Files added in session 2

| file | what |
| --- | --- |
| `gen/_y6912_quasi.py` | the unipotent-Latin-square DFS (orders 2–6 exhaustive: 0 models) |
| `gen/_y6912_fin.py` | the cruder constant-diagonal search (orders 2–3) |

---

# 2026-09-01: all finite models are trivial

- **Batch and laws affected** — Batch 3, `6912/39214` (the latter by duality).
- **Statement** — Every model of 6912 in which all left translations are
  injective is the one-element magma.  Since the law already makes every left
  translation surjective, every finite model is therefore trivial.  Thus a
  nontrivial countermodel, if one exists, must be infinite and must have a
  noninjective surjective left translation.
- **Derivation in short numbered steps**
  1. Let `e` be the common idempotent square and write `L_y(t)=y*t`,
     `R_y(t)=t*y`, and `g=L_e`.  The reduced law is the map identity

     `L_y^2 ∘ g ∘ R_y = id`.

     Hence every `L_y` is surjective and every `R_y` is injective.
  2. Right injectivity and the common square give `a*b=e -> a=b`.  The law at
     `x=e` therefore gives

     `L_y(g^2(y))=y`.

     The map identity at `x=y`, using `R_y(y)=e` and `g(e)=e`, also gives
     `L_y(L_y(e))=y`.  If `L_y` is injective, then

     `y*e=L_y(e)=g^2(y)`.
  3. For `y=e`, the map identity is `g^3 ∘ R_e=id`.  Since
     `R_e(y)=y*e=g^2(y)`, it follows that `g^5=id`.
  4. Put `a=g^2(y)`.  The three known values form the cycle

     `L_y(y)=e`, `L_y(e)=a`, `L_y(a)=y`.

     Solving the map identity gives `R_y=g^{-1}∘L_y^{-2}`, hence
     `a*y=g^{-1}(y)=g^4(y)`.  Step 2 applied to `a` also gives
     `a*e=g^2(a)=g^4(y)`.
  5. Injectivity of `L_a` now cancels the common left factor in
     `a*y=a*e`, yielding `y=e`.  Since `y` was arbitrary, the model is
     trivial.  On a finite carrier, the surjective maps `L_y` are automatically
     injective, so the conclusion applies at every finite order.
- **Whether it is proved, refuted, or conjectural** — Proved algebraically from
  the already established common-square and right-injectivity consequences.
  This replaces the incomplete order-7 search and explains the order-2–6
  failures uniformly.  It does not prove that every infinite model is trivial.
- **The one next lemma needed** — Decide whether the law forces any `L_y` to be
  injective.  Equivalently, in a proposed infinite countermodel explicitly
  realize the forced duplicate fiber

  `L_y(y*e)=L_y(e*(e*y))=y`

  with `y*e != e*(e*y)` while preserving injectivity of every `R_y`.
