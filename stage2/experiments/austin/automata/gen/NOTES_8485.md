# NOTES 8485

> ## STOP — 2026-08-30 (session 9): **THE VARIANT-f MODEL IS FALSE.**
> `theorem law` in `gen/f8485.lean` / `f8485p.lean` / `f8485q.lean` / `f8485r.lean` is **not provable,
> because it is not true**. Lean's own `#eval` on the shipped `op` returns `false` on
>
> ```
> x = ((g0*(g0*g0))*(g0*(g0*(g0*g0))))                                                       sz 13
> y = g0                    (any y -- 1680/1680 sweep instances fail)
> z = ((g0*(g0*(g0*g0)))*(((g0*(g0*(g0*(g0*g0))))*(g0*(g0*(g0*g0))))*(g0*(g0*(g0*g0)))))     sz 33
> ```
>
> **Do not write Lean against this model.** Everything below the "SESSION 9" heading is the
> falsification; everything above it is session-8 material that is now known to describe a false
> model (its "six independent oracles" all missed this cell). See the section
> "SESSION 9 -- RE-FORCING: THE MODEL IS FALSE" at the end of this file.

## (session 8 material follows, superseded)

Law 8485 (catalog, L-form, not dualised): `x = y * (x * (((z*x)*y)*y))`
Row: `research_order5_hard_0096` (8485:4916).

Write `P = op z x`, `Q = op P y`, `R = op Q y`, `S = op x R`. The law is `op y S = x`.

---

## W3-3 track: TRACK B, confirmed

`python smallcheck.py 8485 9 1` → **12,167 assignments, 0 fails, 18.9 s.** The semantic free model is
clean, so this is an extractor hole and a rule set can fix it. (Contrast `gen/NOTES_6912.md`: 6912 and
39214 are Track C — they force all squares equal — and are **not** in this bucket despite
`SEMANTIC_TABLE.md` filing all three together as gate-cut/near-clean.)

## W3-1 harvest: no zero-sorry file, but **the model was already repaired and fully validated**

`gen/rec8485.lean` (4,787 B), `gen/x8485.lean` (5,124 B), `gen/cex8485.lean` (5,460 B),
`gen/rep8485_a/rec8485.lean` (5,124 B) — all 1 sorry (`theorem law`). Nothing to squeeze and ship.

The real inheritance is `gen/_x8485_min.py` + `gen/_x8485_val_f.out`: **variant `f` is a 4-rule model
that passed the complete wave-3 validator with 0 failures**, at a cost of 8,400 s of test time:

```
variant f : 4 rules
  R1 [free]     J?v & J?v.2 & J?v.2.1 & J?v.2.1.1 & v.1 = v.2.1.1.2 & u = v.2.1.2 & u = v.2.2  -> v.1
  R2 [zP@x22]   J?v & J?v.1 & J?v.1.2 & op(op(op(v.1.2.2, v.1), u), u) == v.2                  -> v.1
  R3 [zP@u22]   J?v & J?u & J?u.2 & J?u.2.2 & op(op(op(u.2.2.1, v.1), u), u) == v.2            -> v.1
  R4 [zP@u221]  J?v & J?u & J?u.2 & J?u.2.2 & J?u.2.2.1 & op(op(op(u.2.2.1.1, v.1), u), u) == v.2 -> v.1

exh9/1 12167/0   exh5/2 10648/0
deep/fuzz/clos/crit  seeds 3,4,5  ->  all 0        TOTAL value fails 0
```

`R2/R3/R4` all verify the **whole** chain `op(op(op(z, a1 v), u), u) = a2 v`; they differ only in where
`z` is read from (`a2(a2(a1 v))`, `a1(a2(a2 u))`, `a1(a1(a2(a2 u)))`).

**Still owed before the judge: the case tree (W3-6).** `rv.run_tests` + `deep_tests` are on record;
the `2^k` free/decoded cell enumeration by chained encoding (`gen/_x38565_dd.py`) is not.

## Measured DEAD — do not re-run

The one lever the wave-3 prompt named for this law ("express the guard structurally instead", the
softdrop `~` family) is **refuted for 8485**, by exhaustive test, in `gen/_y8485_soft.py`:

| candidate rule | exh9/1 | first counterexample |
| --- | --- | --- |
| `SOFT`  `v = J w (J (J p u) u) -> w` (R1 with the P-slot shape dropped) | **25 fails** (bail limit) | `y = J (J g0 g0) g0`, `x = g0`, `z = g0` |
| `rP`  `v = J w R, tg R = 2, op(op(a1 (a1 R), u), u) = R -> w` (P read structurally, rest verified) | **25 fails** | same |
| `rQ`  `v = J w R, op(a1 R, u) = R -> w` (Q read structurally) | **25 fails** | `y = J g0 g0`, `x = g0`, `z = g0` |
| `R1 + rP` | **25 fails** | same |

Why they all die on the same instance: with `y = J (J g0 g0) g0`, `x = z = g0`, every product is free,
so `R = J Q y` and the pair `(x, R)` accidentally matches the softdrop shape — `y` itself is
`J (J p u) u` with `u = g0 = x`. `S` then decodes when it must stay free. `rP` dies the same way and
worse: its guard `op(op(g0, g0), g0) = y` **holds by coincidence**. Only the full three-step chain from
`z` breaks the coincidence, because it adds the `op(z, a1 v)` level. R1 survives it because its
`J?v.2.1.1` conjunct fails there. **The nested chain guard is load-bearing; do not try to remove it.**

The other named lever, `closedform.GATE = 'lex'`, was not needed: variant f already validates.

## The skeleton — COMPILES, `gen/f8485p.lean`, 8,061 B, one `sorry` (`theorem law`)

`leangen.emit` on variant f is slow (its internal `deep_tests` + 12,000 fuzz on this model is ~15 min,
because a single `Closed.op` call costs 27 ms here). It is not needed: variant f differs from the
already-emitted variant `a` (`gen/x8485.lean`) in **two lines only**, and the edit is mechanical:

* `def P2` loses its last conjunct: `tg (a1 (a2 (a1 v))) = 2` — variant a's z-path
  `a2 (a1 (a2 (a1 v)))` is one accessor deeper than variant f's `a2 (a2 (a1 v))`;
* the z-path `a2 (a1 (a2 (a1 v)))` becomes `a2 (a2 (a1 v))` in all three places (the `p1` let, the
  `P2` branch gate, and nowhere else).

`gen/f8485.lean` is that file (5,081 B) and `gen/f8485p.lean` adds the proof block below.
Both compile clean:

```
python devrow.py 8485 4916
D=/c/.../vendor/stage2-official/.artifacts/dev_8485_4916 C=200000 bash devlean2.sh gen/f8485p.lean
  ->  exit=0 secs=3   only  "declaration uses `sorry`"
```

`theorem rhs` compiles as generated, so **the refutation of goal 4916 is already verified** for this
`op`; only `theorem law` is open. ~11.9 KB of the 20,000 B cap is free.

### The digest (W3-7) — compiled, and it collapses four rule lemmas into one

**All four rules return `a1 v`, and all four require `tg v = 2`.** So the entire rule set has one
characterisation and there are no per-rule lemmas at all:

```lean
theorem TR (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v) := by
  obtain ⟨p1, …, p9, -, …, -, hop⟩ := op_cases u v
  rw [hop]; split
  · rename_i h; exact Or.inr ⟨h.1, rfl⟩
  · split
    · rename_i h; exact Or.inr ⟨h.1.1, rfl⟩          -- P2/P3/P4 branches are `P_k u v ∧ gates`
    · split
      · rename_i h; exact Or.inr ⟨h.1.1, rfl⟩
      · split
        · rename_i h; exact Or.inr ⟨h.1.1, rfl⟩
        · exact Or.inl rfl

theorem Wfree {u v} (h : tg v ≠ 2)          : op u v = J u v      -- from TR
theorem Wsz   {u v} (h : op u v ≠ J u v)    : sz (op u v) < sz v  -- a1 v, sz_a1_lt
theorem Wpay  {u v} (h : op u v ≠ J u v)    : op u v = a1 v
```

`op_cases` is the generated 9-let packing (`python gen/_pb_gencases.py gen/f8485.lean`, saved as
`gen/_y8485_cases.txt`); it compiles in 3 s at 9 lets / 4 rules.

**`Wpay` is the lever.** On the law's top pair, if `S` is free then `S = J x R`, so `a1 S = x`, and the
goal `op y S = x` follows from **`op y S ≠ J y S` alone** — you never have to say which rule fired or
what it computes. The whole proof is therefore "show some guard holds", four times.

## The remaining goal, and the case tree for it

`theorem law (x y z : M) : op y (op x (op (op (op z x) y) y)) = x`

Cells, by which of `P, Q, R, S` is decoded (`d`) rather than free (`f`). `Wpay` + `op_free`'s
contrapositive (`op u v ≠ J u v → Pre u v`) are the only tools needed.

| cell | what fires at the top pair `(y, S)` | status |
| --- | --- | --- |
| `P f, Q f, R f, S f` | **R1 (`P1 y S`)**: `S = J x (J (J (J z x) y) y)`, so `tg (a2 S) = tg (a1 (a2 S)) = tg (a1 (a1 (a2 S))) = 2`, `a1 S = a2 (a1 (a1 (a2 S))) = x`, `y = a2 (a1 (a2 S)) = a2 (a2 S)` — all seven conjuncts are `rfl` after the three freeness rewrites | **easy, do this first** |
| `P d` (via R1 on `(z,x)`), `Q f, R f, S f` | **R2 (`P2 y S`)**. R1's own conjuncts on the pair `(z,x)` give `tg x = 2`, `tg (a2 x) = 2` **and `z = a2 (a2 x)`** — which is exactly R2's z-path `a2 (a2 (a1 v))` with `a1 v = x`. So the chain guard `op (op (op (a2 (a2 x)) x) y) y = a2 S` is `R = R` after `rw [← that]`, i.e. **`rfl`** | **the key insight; ~15 lines** |
| `P d` via R2/R3/R4 on `(z,x)` | those `P_k` carry no locator for `z`; needs either a proof that the cell is unreachable, or an `SND`-style shape invariant (`PLAYBOOK_PROOF.md` §4) | **open** |
| `Q d` (R1 fired on `(P,y)`) | R1's conjunct `u = a2 (a2 v)` gives `P = a2 (a2 y)`; if `P` is free then `z = a1 (a2 (a2 y))`, which is exactly **R3**'s z-path `a1 (a2 (a2 u))` with `u = y` | open, but the locator is already right |
| `R d` (R1 fired on `(Q,y)`) | same argument one level up: `Q = a2 (a2 y)`, `Q = J P y` free, `P = J z x` free ⇒ `z = a1 (a1 (a2 (a2 y)))` = **R4**'s z-path | open, same shape |
| `S d` | `S = a1 R` and `sz S < sz R` (`Wsz`); the goal becomes `op y (a1 R) = x` | open |

**The general invariant to state once (this is the W3-7 lemma for 8485):**

> `LOC {u v} (h : P1 u v) : u = a2 (a2 v) ∧ tg v = 2 ∧ tg (a2 v) = 2`

— i.e. *a product that fired R1 tells you where its left argument is inside its right argument*. R1's
conjuncts `u = a2 (a1 (a2 v))` and `u = a2 (a2 v)` are literally that, and every one of R2/R3/R4's
z-paths is `LOC` applied at a different depth of the chain. Prove `LOC` (it is `fun h => ⟨h.2.2.2.2.2.2, h.1, h.2.1⟩`
modulo the exact conjunct order) and the three decoded cells become the same 15-line argument.

## Progress on `theorem law` — the all-free cell is PROVED (`gen/f8485q.lean`, 8,611 B, compiles)

```lean
theorem op_R1 {u v : M} (h : P1 u v) : op u v = a1 v := by
  obtain ⟨p1, …, p9, -, …, -, hop⟩ := op_cases u v
  rw [hop, if_pos h]

theorem FREE (x y z : M)
    (hP : op z x = J z x) (hQ : op (J z x) y = J (J z x) y)
    (hR : op (J (J z x) y) y = J (J (J z x) y) y)
    (hS : op x (J (J (J z x) y) y) = J x (J (J (J z x) y) y)) :
    op y (op x (op (op (op z x) y) y)) = x := by
  rw [hP, hQ, hR, hS]
  have h1 : P1 y (J x (J (J (J z x) y) y)) := by unfold P1; simp
  rw [op_R1 h1]; simp
```

Three lines. `unfold P1; simp` discharges all seven conjuncts, and `op_R1` needs no `split` — it is
`rw [hop, if_pos h]` on the packed `op_cases`.

### What `op_R2` needs (the next 30 minutes of work)

```lean
theorem op_R2 {u v : M} (h2 : P2 u v)
    (g1 : msr (a2 (a2 (a1 v))) (a1 v) < msr u v)
    (g2 : msr (op (a2 (a2 (a1 v))) (a1 v)) u < msr u v)
    (g3 : msr (op (op (a2 (a2 (a1 v))) (a1 v)) (a1 v)) u < msr u v)   -- NB: second arg is u
    (hc : a2 v = op (op (op (a2 (a2 (a1 v))) (a1 v)) u) u) : op u v = a1 v := by
  by_cases h1 : P1 u v
  · exact op_R1 h1                                   -- P1 also returns a1 v, so no refutation needed
  · obtain ⟨p1, p2, p3, …, hp1, hp2, hp3, -, …, hop⟩ := op_cases u v
    rw [dif_pos g1] at hp1; subst hp1
    rw [dif_pos g2] at hp2; subst hp2
    rw [dif_pos g3] at hp3; subst hp3
    rw [hop, if_neg h1, if_pos ⟨h2, g1, g2, g3, hc⟩]
```

**Note the trick in the first branch**: because every rule returns `a1 v`, an earlier branch firing is
not an obstacle — `op_R1` closes it. That removes every "refute the earlier guard" obligation, which is
what usually makes these rule lemmas long.

The three gates are the only real work. With `u = y`, `v = J x R`, `n = sz`, `n v = n x + n R + 1`:

* `g1` — `z = a2 (a2 x)` so `n z < n x < n v`; `msr_lt_of_max_lt` closes it whenever `n x < max (n y) (n v)`,
  which holds because `n v > n x`.
* `g2`, `g3` — need `sz (op a b) ≤ sz a + sz b + 1` (i.e. a bound on a recursive result). `Wsz` gives
  `sz (op a b) < sz b` in the decoded case and `J a b` in the free case, so
  `SZOP : sz (op a b) ≤ sz a + sz b + 1` follows from `TR` **without induction** — prove it as a
  corollary of `TR` (`rcases TR a b`: free ⇒ `sz_J`; decoded ⇒ `sz (a1 b) ≤ sz b`).
  Then each gate is `msr_lt_of_max_lt` or `msr_lt_of_max_eq` after an `omega` on the sizes.

Then the P-decoded cell is: `P1 z x` (from `op_free`'s contrapositive plus a split on which `P_k`
holds) gives `z = a2 (a2 x)` — conjunct 7 of `P1` — and `hc` becomes `rfl` after `rw [← that]`.

## Budget note

Certificate cap 20,000 B; the compiling skeleton + digest is **8,061 B**, so the `law` proof has
~11.9 KB. `squeeze.py --rename` is not needed unless the case tree runs long — and remember to
recompile after any squeeze.

## Files written this session

| file | what |
| --- | --- |
| `gen/f8485.lean` | variant-f skeleton, 5,081 B, compiles, 1 sorry |
| `gen/f8485q.lean` | `f8485p.lean` + `op_R1` + `FREE` (the all-free cell of `law`); 8,611 B, compiles, 1 sorry |
| `gen/f8485p.lean` | the same + `op_cases`, `sz_pos/sz_a1_lt/sz_a2_lt`, `TR`, `Wfree`, `Wsz`, `Wpay`; 8,061 B, compiles, 1 sorry (`law`) |
| `gen/_y8485_cases.txt` | the generated `op_cases` statement |
| `gen/_y8485_soft.py` | the softdrop / structural-read refutations (variants `s`, `s2`, `P`, `Q`, `1P`, …) |
| `gen/_y8485_emit.py` | `leangen.emit` from variant f into `gen/rep8485_f/` (slow; the hand edit above is equivalent and instant) |

---

# SESSION 2 (same agent, after the coordinator's oracle request)

## W3-6 CASE TREE — done, three independent oracles, 0 failures

### (1) Cell census, `gen/_y8485_tree.py`
Exhaustive over all 22 one-/two-generator terms of size <= 5 in x, y, z (10,648 assignments) plus a
1,280-instance chained-encoding pool. Encoding used throughout (R1's own shape, built with `C.op` so
inner decodes fire): `enc(u,w,j) = op(w, op(op(op(j,w),u),u))`, for which `op(u, enc(u,w,j)) = w` **is**
the law.

### (2) Per-rule forcing / the 40037 warning, `gen/_y8485_fire.py`
For every rule k and every chain product, an instance was **constructed from that rule's own
precondition** so that rule k fires at that product — not sampled.
**97,000 constructed assignments, 0 failures.** Attempts actually realised:
`P<-R1 10000, Q<-R1 10000, R<-R1 10000, S-probe 40000, P<-R2 5000, Q<-R2 5000, R<-R2 5000,
P<-R3 3000, Q<-R3 5000, R<-R3 3000, Q<-R4 1000`.

### (3) Level-k descent, `gen/_y8485_deep3.py` (the 12087 construction, adapted)
The decoder of 8485 reads its payload out of the RIGHT argument, so "descend in the same argument"
means nesting encodings under one fixed left element `u0` and taking `z := u0`:
`p_0 = small ; p_{i+1} = enc(u0, p_i, junk) ; x = p_levels ; z = u0`, so `op z x`,
`op z (op z x)`, `op z (op z (op z x))` all decode.
Levels 0-3 x {small junk, large junk} x seeds {5,19}, 100 instances each:

```
levels=0  depth1                 BAD=0    (4 runs)
levels=1  depth2                 BAD=0    (4 runs)
levels=2  depth>=3  100/100 each BAD=0    (4 runs)
levels=3  depth4    100/100      BAD=0
cycles=0 on every fresh evaluator; large-junk pool = rand_term(5..8, 3 generators)
```

**The oracle passes.** With the earlier full validator (`gen/_x8485_val_f.out`) that is six independent
oracles: exhaustive small terms; `rv.run_tests` deep+fuzz+closure+critical on three seeds; the cell
census; per-rule forcing; large junk; and the level-4 descent.

### The reachable cells (this is the useful output)
Across all ~108,000 assignments only these `(P,Q,R,S,top)` cells occur:

| cell | count | reading |
| --- | --- | --- |
| `(free, free, free, free, R1)` | 57,980+ | the generic case |
| `(R1,   free, free, free, R2)` | 18,000 | P decoded by R1 -> `z = a2 (a2 x)` -> R2 at top |
| `(free, R1,   free, free, R3)` | 19,980 | Q decoded by R1 -> `P = a2 (a2 y)` -> R3 at top |
| `(free, R1,   free, free, R2)` | 1,000 | same, R2 happens to fire first |
| `(free, R1,   R1,   free, R3)` | 40 | Q and R both decoded |
| `(R2,   free, free, free, R2)` | ~5% of the descent runs | **P decoded by R2** — found ONLY by the level-k descent |

Two facts the Lean proof leans on, both measured and neither yet proved:
**S is free in every reachable cell**, and **R4 (`zP@u221`) never fires anywhere.**

## `theorem law` — where it actually stands, and the one case that blocks it

Compiled and shipped in `gen/f8485r.lean` (10,430 B, 1 sorry = `law`):

```lean
op_cases      the 9-let packing (generated)
TR   (u v) : op u v = J u v \/ (tg v = 2 /\ op u v = a1 v)       -- all 4 rules return a1 v
Wfree / Wsz / Wpay                                              -- corollaries of TR
mxl  {a b c d} (h1 : sz a < sz d) (h2 : sz b < sz d) : max (sz a) (sz b) < max (sz c) (sz d)
SZOP (a b) : sz (op a b) <= sz a + sz b + 1                     -- NO induction: TR gives it in 3 lines
QGE  (u v) : sz (a1 v) <= sz (op u v)                           -- likewise
op_R1 {u v} (h : P1 u v) : op u v = a1 v
op_R2 {u v} (P2 + three gates + the chain guard) : op u v = a1 v
op_R3 {u v} (P3 + three gates + the chain guard) : op u v = a1 v
FREE (x y z) (all four products free) : the law                 -- the all-free cell, 3 lines
```

**The `op_Rk` shape that works** (worth copying — it removes every "refute the earlier branch"
obligation): `obtain` the packing, `rw [dif_pos g_i] at hp_j; subst hp_j` for this rule's three lets,
`rw [hop]`, then `split` four times answering `rfl` each time (every branch returns `a1 v`, so an
earlier rule firing is not an obstacle), and in the final `else` contradict the branch's own negation:
`rename_i k4 k3 k2 k1; exact absurd (h, g1, g2, g3, hc) k3` for rule 2 (`k2` for rule 3).
**`rename_i` names in order of introduction**: `k4 = not-branch1, k3 = not-branch2,
k2 = not-branch3, k1 = not-branch4`.

### Why the top guard is usually `rfl`
At the top pair `(y, J x R)`, `a2 v = R` and `R = op (op (op z x) y) y` **by definition**, so

* R3's guard is `R = op (op (op (a1 (a2 (a2 y))) x) y) y` — **rfl as soon as `a1 (a2 (a2 y)) = z`**,
  which R1's own conjunct `u = a2 (a2 v)` gives when `Q = op P y` decoded by R1 (`P = a2 (a2 y)`) and
  `P` is free (`P = J z x`, so `a1 P = z`). It is `rfl` **whether or not R is free** — which is why
  cell `(free,R1,R1,free,R3)` costs nothing extra.
* R2's guard is `R = op (op (op (a2 (a2 x)) x) y) y` — **rfl as soon as `a2 (a2 x) = z`**, which
  `P1 z x`'s conjunct 7 gives when P decoded by R1.
* R1 fires when P, Q, R are all free.
* Gates: with the chain instantiated, every gate is `mxl` + `msr_lt_of_max_lt`, because
  `sz (J x R) > sz x`, `> sz R`, `> sz Q`, `> sz (a1 x)`. **Do not state them with abstract `v`**
  (the 17286 lesson) — instantiate `v = J x R` first.

### THE BLOCKER — one cell, and it is real

Cell `(R2, free, free, free, R2)`: **P decodes by rule R2, not R1.** Then `P1 z x` is false, so no
conjunct hands over `z = a2 (a2 x)`, and R2's top guard needs `op (a2 (a2 x)) x = op z x` for a reason
that is not syntactic. In the instances the descent constructs it is true because `x` is the *free*
encoding `J p (J (J (J j p) u0) u0)` and then `a2 (a2 x) = u0 = z` literally — but that is a property
of the construction, not a theorem.

An exhaustive scan over all 10,404 pairs of one-/two-generator terms of size <= 7 plus 21 constructed
pairs (`gen/_y8485_p2.py`) finds **zero** non-R1 decodes, so the cell is rare; the level-k descent is
the only oracle that produced it. Two ways out, in order:

1. **`TR2`, the strengthened digest** (not yet written):
   `op u v = J u v \/ (tg v = 2 /\ op u v = a1 v /\ (u = a2 (a2 v) \/ exists c, a2 v = op c u))`
   — provable by the same four-way `split`, because P1's conjunct 7 gives the left disjunct and
   R2/R3/R4's guard is literally `a2 v = op p2 u` after the gate rewrite. Combined with `TR` applied
   to `op c u` it becomes `u = a2 (a2 v) \/ (exists c, a2 v = J c u) \/ a2 v = a1 u` — three concrete
   shapes instead of an opaque guard. This is the tool that should also settle "S is always free" and
   "R decoded => Q decoded" (the latter is already *half* proved: if R decodes by P1 then
   `Q = a2 (a2 y)`, and `Q` free would give `sz Q > sz y > sz (a2 (a2 y)) = sz Q`, a contradiction).
2. If `TR2` is not enough, `PLAYBOOK_PROOF.md` section 4's `SND`/`CMP` shape invariant — but note
   `LEMMA_LIBRARY.md` section 3: 8485's recursive rules carry their own `msr` gates, so `mx` may bound
   the result and avoid the fuel induction.

**Byte budget is not the problem**: 10,430 B of 20,000 used, 9.5 KB free. `theorem rhs` compiles, so
the refutation of goal 4916 is already verified against this `op`.

## Files added in session 2

| file | what |
| --- | --- |
| `gen/f8485r.lean` | skeleton + `TR`/`Wfree`/`Wsz`/`Wpay`/`mxl`/`SZOP`/`QGE`/`op_R1`/`op_R2`/`op_R3`/`FREE`; 10,430 B, compiles, 1 sorry |
| `gen/_y8485_tree.py` | the cell census (exhaustive + chained encodings) |
| `gen/_y8485_fire.py` | per-rule forcing at every chain product (the 40037 check), 97,000 instances |
| `gen/_y8485_deep3.py` + `gen/_y8485_deep3.out` | the level-k descent oracle, levels 0-3, both junk pools, two seeds |
| `gen/_y8485_p2.py` | search for decodes via a rule other than R1 (none in 10,404 exhaustive pairs) |

---

# SESSION 9 (2026-08-30) — RE-FORCING: THE MODEL IS FALSE

The task was "re-force the minimised model, then prove `op_R2` and `SZOP`". The re-forcing kills the
model, so no Lean was written. Row `research_order5_hard_0096` (8485:4916) is **not** one Lean
session away; it needs a new carrier.

## The result in one line

`gen/f8485r.lean`'s `op` does **not** satisfy law 8485. Confirmed four independent ways:
an independent Python transcription of the Lean definition (`gen/_z8485_lean.py`), `closedform.Closed`
with variant f's rules, a hand derivation, and **Lean's own `#eval` on the shipped `def op`**
(`gen/_z8485_diag.lean`, `exit=0`):

```
#eval (op (g 0) X1d == cd)                                        -- true
#eval (op cd zd == cd)                                            -- true
#eval (op zd xd == X1d)                                           -- true   (P decodes, branch 2 = R2)
#eval (a2 (a2 xd) == zd)                                          -- FALSE  (the locator is destroyed)
#eval (op yd (op xd (op (op (op zd xd) yd) yd)) == xd)            -- FALSE  <-- THE LAW
```

(`by decide` cannot be used here: the kernel will not reduce `op`'s well-founded recursion. `#eval`
uses the compiler and agrees with two separate Python implementations and with the hand derivation.)

## The construction (`gen/_z8485_break.py`)

The rule that dies is **R2 = N4 `[zP@x22]`**, the one that reads `z` at `a2 (a2 (a1 v))`. It was added
to fire at the **top** pair `(y, J x R)`, where `a1 v = x` and `P1 z x`'s conjunct 7 guarantees
`z = a2 (a2 x)`. But a rule is a predicate of `(u, v)` alone, so it also fires at the **P** pair
`(z, x)` — and there nothing guarantees the locator. Build the instance that exploits that:

```
z0, A, Cc, zz   generators
X1 := J A (J Cc z0)              -- puts z0 on R2's accessor path inside a1 x
c  := J z0 X1                    -- = op z0 X1, a free product
z  := J c (J (J (J zz c) c) c)   -- P1 c z holds, so  op c z = c   (a FIXED POINT of the chain)
x  := J X1 c
```

At `(z, x)`: `P2 z x` holds, the three chain steps are `op z0 X1 = c`, `op c z = c`, `op c z = c`,
and the guard `a2 x = c` is satisfied — so **R2 fires and `P = op z x = X1`**. The fixed point is the
whole trick: it lets the chain terminate *without* leaving `z` inside `a2 x`. Consequently

* `sz x = 13 < 33 = sz z`, so **`z` does not occur in `x` at all**;
* `a2 (a2 x) = a2 c = X1 != z`;
* measured: of the 5 accessor-reachable terms from `{x, y}`, and of **615** terms of size <= 11
  (1 generator) / <= 9 (2 generators), **zero** satisfy `op w x = P`. The only `w` that work are the
  z-shaped `J c (J (J (J _ c) c) c)`, which no accessor path can reach.

So at the top pair `(y, J x R)`: `P1` fails (it would need `a2 X1 = x`, an occurs-check violation),
`P2`'s guard needs `op (a2 (a2 x)) x = P` which is false, and with `y` a generator `P3`/`P4` cannot
fire at all (`tg u = 2`). The top pair stays **free**, so `op y S = J y S != x`.

## How general is it

`gen/_z8485_break2.py` re-runs the construction with the shape of `X1` matched to each rule's own
accessor path. **Every rule set on file falls:**

| rule set | rules | result |
| --- | --- | --- |
| `FULL(noexist)` (the extractor's own output) | 83 | **FAILS** every shape (24/24) |
| `FULL(exist)` | 102 | survives this construction, but **fails `smallcheck` exh9/1 with 25 fails in 301 assignments** |
| variants a, b, c, d, f, g, i | 3–6 | **FAIL** every shape (24/24) |
| variant e | 3 | **FAILS** on the `a2a1a2` shape (C4's path) |
| variant h | 2 | **FAILS** on `a2a2` and `a2a1a2` |

And the rule is not optional. With **R1 alone**, or with **R1+N1+N2 (N4 and C4 removed)**,
`smallcheck` exh9/1 fails in the first 4,000 assignments on `x = (g0*(((g0*g0)*g0)*g0)), z = g0` —
the cell where `P` decodes by R1 and the top pair must read `z = a2 (a2 x)`. **The rule that closes
that cell is exactly the rule that manufactures the bad decode at the P pair: necessary and fatal.**

## Why six oracles missed it (the methodological finding)

1. **Exhaustive small terms cannot reach it.** The witness needs `sz x = 13` *and* a `z` of `sz 33`
   that is a *function of x* (`z = J c (J (J (J _ c) c) c)` with `c = a2 x`). This session ran
   **exh9/1 12,167**, **exh7/2 1,061,208**, **exh5/3 287,496**, **exh5/2 10,648** assignments against
   the Lean transcription: **0 failures**. Rail 50 again — a sampler cannot find a cell of measure
   zero, and this cell is a one-dimensional fibre inside a two-parameter family.
2. **The session-8 "forced firing" suite had no positive control for this branch.** All 97,000 of its
   constructed instances build `x` through `enc(u,w,j) = op(w, op(op(op(j,w),u),u))`, whose last step
   is free, so `a2 x = J _ z` and `a2 (a2 x) = z` **by construction**. The suite could not express the
   case it needed to test. That is exactly `LEMMA_LIBRARY.md`'s "a forcing suite needs its own
   positive control", and session 2's own note already said the descent instances worked "because `x`
   is the free encoding … that is a property of the construction, not a theorem". It was right.
3. **R4 (`[zP@u221]`) fires 0 times** in every one of the 1.37M exhaustive assignments — session 2's
   observation confirmed. It is dead weight, and a branch that never fires is untested, not unneeded.

## What it would take (rail 58 territory)

This is not "one more rule". Any rule reads `z` off a fixed accessor path; the construction above
makes `op z x` decode while erasing every trace of `z` from `x`, so the path does not exist. The only
fix is to stop R2 from firing at the P pair, and `op` is a function of `(u, v)` alone — it cannot see
whether it is at the root of the law's chain or inside it. That is the **root-vs-inner position
separator** that CLAUDE.md already names as the single obstruction shared by ~25 rows: the free term
algebra is the wrong carrier. 8485 belongs on that track, not on the "just needs Lean" list.

## Files

| file | what |
| --- | --- |
| `gen/_z8485_lean.py` | independent transcription of the Lean `op` (agrees with `closedform.Closed` on 23,600 pairs, 0 disagreements) |
| `gen/_z8485_reforce.py` | the re-forcing battery (cross-check, exhaustive, junk-variable, forced firing, blocker cell, level-k descent, broad random) |
| `gen/_z8485_break.py` | **the counterexample**, and a 1,680-instance sweep: 1,680 law failures |
| `gen/_z8485_break2.py` | the same attack per accessor path against all 11 rule sets |
| `gen/_z8485_variants.py` | the single instance against all 11 rule sets |
| `gen/_z8485_diag.lean` | the Lean `#eval` confirmation (compiles, `exit=0`) |
| `gen/_z8485_diag2.lean` | shows `by decide` cannot reduce the WF recursion (kept so nobody retries it) |
| `gen/_z8485_s1.out` | the four exhaustive sweeps, all clean — the evidence that small-term search cannot see this |

## Addendum — the junk-variable oracle also passes, and shows why

Rail 52a says to blow up the variable no rule constrains (`z`, in R1's free cell). 3 seeds x 40,000
assignments with `z` drawn from `rand_term(4..7, 4 generators)`: **0 failures**, and the branch
histogram is `[~1.2M free, ~34k R1, 0 R2, 0 R3, 0 R4]` — random large `z` never produces a decode by
R2/R3/R4 **at all**. A junk-variable sweep therefore cannot reach this cell either: the witness needs
`z` to be a *specific function of x*, not a large random term.
