# NOTES_9663 — the four-constructor carrier, and the separator that closed it

Laws 9663 / 36487 (its dual) / 12294. Rows `research_order5_hard_0018`, `_0051`, `_0098`, `_0093`.

* 9663  `x = y ◇ ((z ◇ y) ◇ (x ◇ (x ◇ y)))`   chain `P = x◇y ; Q = x◇P ; A = z◇y ; C = A◇Q ; root = y◇C`
* 36487 `x = (((y ◇ x) ◇ x) ◇ (y ◇ z)) ◇ y`   — **exactly the dual of 9663**, so it takes the dual magma
* 12294 `x = y ◇ (((z ◇ y) ◇ x) ◇ (x ◇ y))`   — a different chain (`B = A◇x`), same carrier candidate

Session-8 state carried in: `gen/_x9663_lab4.py`, four rules, unconditional gates, fast harness 0 —
but the **3.9M-chain exhaustive L1 (size ≤ 5, 2 generators) read 632 BAD**, and `deep seed=23` read 4.
Session 8's handover called this "two H3 cells, each a one-line reading". It was neither H3 nor a
reading: H3 was already 0 on lab4. See below.

---

## SESSION 9 RESULT: the residual is a POSITION problem and the separator is `a1 v ≠ u`

### 1. What the 632 failures actually were (`gen/_s9_9663_diag.py`)

All 632 come from **four (x, y) pairs**, and every one has the same shape:

```
x = g_b                       (a generator)
y = F(g_a, J(g_a, g_b))       (op-built: y = op(g_a, op(g_a, g_b)))
z = anything                  (all 158 pool terms; z is the junk slot)
```

Trace, x = g0, y = F(g0, J(g0,g0)), z = g0:

```
P = op(x,y) = F(x,y)     TAGF fires because  a1 y = x  and  op(x, a2 y) = y
Q = op(x,P) = g0         DEC fires because  a2 P = y is an F node with op(a1 y, x) = a2 y
                         --> Q collapses to a1 y instead of becoming the container F(x,P)
C = J(A, Q)              tg Q = 1 now, so C is a free product
root = E(y, C)           nothing can decode.  FAIL
```

**DEC misfired at the `Q` slot.** That is the position problem session 8 named for `R5` (LEMMA_LIBRARY,
"If changing the guard does not change the firing set, the problem is the POSITION") — reached from
the other side: this time it is the *decode* rule, not a witness rule, that is in the wrong place.

### 2. The separator — and it does NOT need an anchored carrier

`NOTES_ANCHORED_CARRIER.md` and the handover both concluded that the fix for this family is a
well-formedness invariant on a restricted carrier, because "`op` is a function of `(u,v)` alone and the
two positions present the same pair". **For 9663 that last clause is false, and the counter-example is
one comparison:**

| position | `v` is | `a1 v` |
| --- | --- | --- |
| the `Q` slot, `op(x, P)` | `P = op(x, y)`, i.e. **u's own product** | `= x = u` |
| the root, `op(y, C)` | `C = op(A, Q)`, built by **A**, not by `u` | `= A ≠ u` |

> **`a1 v ≠ u` is a root-vs-inner-position separator that a plain term algebra DOES supply.**
> It is a function of `(u, v)`, so it is legal in `op`; it says *"`v` is not a container I built myself"*.
> Every container the chain builds at an inner slot has `a1 = u`; the one the root reads does not.

Three features were measured (`gen/_s9_9663_lab5.py`, FEAT-parameterised so each is separately
switchable). All three are **necessary** — each was checked by deletion:

| feature | rule | condition added | deleting it costs |
| --- | --- | --- | --- |
| `nu`   | DEC | `a1 v ≠ u` | **632** L1 fails (the whole residual above) |
| `v34`  | DEC | `tg v ≠ 2` (the container must be `E`/`F`, never a free `J`) | 1 `deep seed=23` fail |
| `nur`  | R2  | `tg v ≠ 1 ∧ a1 v ≠ u` | 1 forced-firing (`TAGF2`) fail |

`v34r` (the same `tg v ≠ 2` on R2) was tried and is **wrong**: it costs 236 descent fails, because the
descent's root legitimately reads a `J` container (`profile D,D,E,.,R`). Three other separators were
tried and are worse than the baseline: `tg (a1 v) ≠ 1` and `tg(a1 v) ≠ 1 ∧ a2 (a1 v) = u` both break
H3 (136 and 445 on the fast battery), and `tg (a2 (a2 v)) ≠ 1` kills the base case (`P = J(x,y)` when
`y` is a generator — rail "a tag rule must fire on `J`-products too" one level up).

### 3. The rule set (session 9, `FEAT = {nu, v34, nur}`)

```
M ::= g n | J a b | E a b | F a b            tg: g→1, J→2, E→3, F→4;  a1/a2 total (identity on g)

DEC   tg v ≥ 3,  a1 v ≠ u,  tg (a2 v) = 4,  op (a1 (a2 v)) u = a2 (a2 v)       →  a1 (a2 v)
R2    tg u ≠ 1,  tg v ≠ 1,  a1 v ≠ u,  tg (a2 u) ≠ 1,  tg (a2 (a2 u)) ≠ 1,
      op (a1 (a2 u)) (a2 (a2 (a2 u))) = a2 (a2 u),
      op (a2 (a2 (a2 u))) (a1 (a2 u)) = a2 v                                   →  a2 (a2 (a2 u))
TAGF  tg v ≠ 1,  a1 v = u,  op u (a2 v) = v                                    →  F u v
TAGE  tg v ≠ 1                                                                 →  E u v
else                                                                           →  J u v
```

Note the free structural bonus: **DEC/R2 require `a1 v ≠ u` and TAGF requires `a1 v = u`**, so `op`
splits at the top on `a1 v = u` — three of the five branches are decided by one comparison.
Every recursive argument is a proper subterm of `u` or of `v`, so all four gates are **unconditional**
(the 27859/13764 shape):
`DEC` uses `a1 (a2 v)`; `TAGF` uses `a2 v`; `R2` uses `a1 (a2 u)` and `a2 (a2 (a2 u))`, whose sizes sum
to `sz (a2 u) − 1 < sz u` under `tg u ≠ 1 ∧ tg (a2 u) ≠ 1`, both of which are in R2's own guard.

### 4. The ladder, rung by rung — what was actually run and what it returned

`gen/_s9_9663_lab5.py f:nu,v34,nur full` and `gen/_s9_9663_force.py f:nu,v34,nur`.

| rung | battery | chains | BAD |
| --- | --- | --- | --- |
| 1/2 | deep random, depth 5, 3 gens, seeds 5 / 19 / 23 | 60,000 | **0** |
| 3/4 | cell census + both-decoded census (printed per construction) | — | see below |
| 6 | level-k descent, levels 0-4, both tower variants, cell census | 4,000 | **0** |
| 7 | vary the junk variable: depth-6 terms over **fresh** generators (g100-g102) in the `z` slot | every construction re-run with `+bigjunk` | **0** |
| 8 | forced firing: `DEC`, `R2`, `TAGF`, `TAGF2`, `TAGE` each constructed inside its own guard | 4,000-6,000 each | **0** |
| 9 | H3 (`y = enc(j,w,x)`, a genuine encoding by `x`), seeds 5/19 | 40,000 | **0** |
| 9b | **H3z** (`y = enc(z,w,j)`, an encoding by the *junk* variable) — new this session | 8,000 | **0** |
| 9c | **H3xz** (`y` an encoding by `x` *and* `z` an encoding by `x`) — new this session | 8,000 | **0** |
| 10 | per-branch, per-construction firing counts | — | every rule fires ≥ 3,799 times in every construction |
| 11 | positive control | — | see the vacuity note below |
| 12 | every construction ported from lab4's oracle | — | done (`_s9_9663_force.py` is `_x9663_force4.py` + 4 new targets) |
| — | **exhaustive L1, size ≤ 5, 2 generators** | **3,944,312** | **0** (was 632) |

**Vacuity found and fixed (rung 11).** Session 8's `_x9663_force4.py` had a target `Adec` (force the
root's `A` slot to be a decode) that **sampled** for `rule(z,y) ∈ {D,R}` and got **1 trial** — it tested
nothing. Rebuilt as a *construction* (`y = enc(z, w, j)` makes `op z y = w` by definition): 4,000 trials,
`D` fires 8,004 times, 0 BAD. This is the rung-11 rail doing its job on a suite this session inherited.

**One target is still vacuous and is recorded as such**: `Aeqy` (chains with `op z y = y` exactly, the
one shape in which the root's own `a1 v ≠ u` guard could fail) produced **0 instances in 60,000 draws**.
It is not evidence of anything. It is a *proof obligation* instead — see §5.

### 5. The one open obligation, stated exactly

For the root to fire DEC we need `a1 C ≠ y`, and in that branch `C ∈ {E(A,Q), F(A,Q)}` so `a1 C = A`.
So the Lean proof owes **`op z y ≠ y`**. Case analysis on `op z y`:

* `J/E/F(z,y)` — size `sz z + sz y + 1 > sz y`. Done by `omega`.
* DEC at `(z,y)` — returns `a1 (a2 y)`, `sz ≤ sz (a2 y) < sz y`. Done.
* R2 at `(z,y)` — returns `a2 (a2 (a2 z))`, a subterm of `z`, with **no size relation to `y`**.
  This is the only branch that is not free. R2's own guard then forces `op (a2(a2(a2 z))) (a1 (a2 z)) = a2 y`,
  i.e. with `A = y` it forces `op y p = a2 y` for `p = a1 (a2 z)`; every container branch of `op y p` has
  size `> sz y > sz (a2 y)`, so `op y p` must itself be a decode, and R2 at `(y,p)` returns a term
  strictly smaller than `a2 y` (from `tg (a2 y) ≠ 1 ∧ tg (a2 (a2 y)) ≠ 1` in its guard) — so it must be
  **DEC at `(y,p)` with `a1 (a2 p) = a2 y`**. That is the exact residual cell to discharge in Lean; the
  fuzzers cannot reach it (0 instances in 60,000), which is rail 50 ("a sampler cannot find a cell whose
  measure is zero; only construction can") pointing at the proof rather than at another oracle.

Not "the model is clean". The measured statement is: **0 failures on every rung that fired, and one
branch of the root's guard that no battery has ever instantiated.**

---

# 2026-09-01: the explicit `A=y` family is a guard gap, not a pair collision

- **Batch and laws affected** — Batch 1, `9663`; `36487` by pair reversal.
  No transfer to `12294` is justified because its chain is different.
- **Statement** — In the explicit family from `REMAINING_40_PROMPT.md`, put
  `P=E(l,y)`, `Q=F(l,P)`, and `C=E(y,Q)`.  The intended root pair
  `r=(y,C)` differs from the bad R2 pair `i_R=(z,y)` and its supporting
  TAGE pair `i_E=(p,y)`.  The concrete pair predicate

  `S(u,v) :⇔ a2(a2(a2(u))) != v`

  is true at `r` and false at both bad pairs.
- **Derivation in short numbered steps**
  1. The constructed equalities are `op(g,y)=V`, `op(y,p)=g`,
     `op(p,y)=H`, and `op(z,y)=y`; the last two make R2 fire at `(z,y)`.
  2. With `x=l`, TAGE gives `P=E(l,y)`, TAGF gives `Q=F(l,P)`, and
     the `A=y` branch gives `C=E(y,Q)`.  The blocked root DEC call is
     therefore exactly `(y,C)`.
  3. The first coordinates show `r != i_R` (`E` versus `J`) and
     `r != i_E` (`y=E(c,g)` whereas `p=E(b,F(g,V))`, with `b!=c`).
  4. Total accessors are the identity on generators, so
     `a2^3(y)=g != C`, while the construction gives
     `a2^3(z)=y=a2^3(p)`.  Hence `S(r)` and not `S(i_R),S(i_E)`.
  5. In the opposite magma every pair reverses, giving the 36487 pairs
     `(C,y)`, `(y,z)`, `(y,p)` and the dual predicate `Sᵒᵖ(u,v)=S(v,u)`.
- **Whether it is proved, refuted, or conjectural** — Pair inequality and the
  displayed separation are proved for this symbolic family.  The current
  DEC/R2/TAGF/TAGE model and its 36487 dual remain refuted.  Adding `S` as a
  global guard is conjectural, not a repair.
- **The one next lemma needed** — Prove the chain-specific root-safety statement

  `IntendedRootDEC_9663(y,C) -> a2^3(y) != C`,

  while separately retaining a guard against the older Q-slot DEC misfire.
  Only then is a guarded model worth constructing; `12294` first needs its own
  ordered-pair map.

# 2026-09-02: the two-bit root separator is branch-proved

- **Batch and laws affected** — Batch 1, `9663`; `36487` by pair reversal.  No transfer to
  `12294` is justified.
- **Statement** — Let `N(u,v) :⇔ a1(v) != u` and `S(u,v) :⇔ a2^3(u) != v`.  Retain `N` on
  DEC/R2 and add `S` only to R2.  For every intended root with
  `P=op(x,y)`, `Q=F(x,P)`, and `C` equal to `E(A,Q)` or `F(A,Q)`, one has `S(y,C)`.
  The three relevant signatures are: root `N∧S`, old Q-slot `¬N∧S`, bad R2 `N∧¬S`.
- **Derivation in short numbered steps**
  1. Every operation output is a container `K(u,v)`, DEC's strict right subterm
     `a1(a2(v))`, or R2's strict left subterm `a2^3(u)`.
  2. Since `C` contains `Q=F(x,P)`, both `sz(x)<sz(C)` and `sz(P)<sz(C)`.
  3. If a container produces `P`, then `a2^3(y)≤sz(y)<sz(P)<sz(C)`.
  4. If DEC produces `P`, its guard gives `op(P,x)=a2^2(y)`.  Splitting this product puts
     `a2^3(y)` strictly below either `x` or `P`, hence below `C`.
  5. If R2 produces `P`, put `p=a1(a2(x))`; its guard gives `op(P,p)=a2(y)`.  Splitting this
     product puts `a2^3(y)` below `p<x` or below `P`, hence below `C`.
  6. With `S` on R2, `op(z,y)!=y`: containers are larger than `y`, DEC is smaller, and R2
     equality is excluded by `S`.  Thus the root's `N` bit also holds.
  7. `_s10_9663_rootsep.py` reaches the explicit `A=y` control and all existing constructed
     rule/descent controls with zero failures.  Deleting `S` restores the bad R2 cell; deleting
     `N` restores the older Q-slot DEC misfire.
- **Whether it is proved, refuted, or conjectural** — Intended-root safety is proved by the
  displayed producer split.  The guarded operation is positive-controlled but does not yet have
  a Lean certificate.
- **The one next lemma needed** — Prove the chain dichotomy
  `Q=F(x,P) ∧ C∈{E(A,Q),F(A,Q)}` or `R2Guard(y,C) ∧ a2^3(y)=x`.
  DEC closes the first branch and R2 closes the second.
