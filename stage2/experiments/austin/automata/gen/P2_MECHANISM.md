# P2 — the existential decoder: what it is, and why 22591 is dead anyway

Wave-3 research agent, 2026-08-29 deep session 8.
Starting point: `gen/P2_EXISTENTIAL_DECODER.md` (R1–R4) and `gen/PLAYBOOK_QUOTIENT.md` §4.

Rows in scope (11): 22591 → 0017/0052/0069; 21865 → 0039/0057; 21866 → 0020/0028;
23357 → 0048; 23653 → 0080; 21864 → 0033; 24199 → 0086.

---

## VERDICT — two results, and they point opposite ways

**(A) The existential decoder is real, eliminable, and I built it.** The obstruction named "the
existential decoder" is an artefact of *where the guard is placed*, not of the mathematics. The
payload the two coincident readings destroy is still **determined** by the encoding-side equation
alone, and that equation has a **closed-form inverse**. The rule that R4 proposed does not fire —
not because it is wrong but because its guard is **always cut by the recursion gate**. Unfolding the
guard one level, into the structural preconditions of the decode rule that would have produced
`a2 u`, puts every remaining `op` call on a strict subterm and makes it an ordinary DSL rule.
Measured: 22591's baseline model `gen/q22591b.py` fails the recorded refutation family; with two
such rules added it is **0 failures over 72,600 exhaustive assignments, the whole constructed case
tree except one cell, and the identity probe**. Call the pair **ENC-INV / DEC-STRUCT** (§2).

**(B) It cannot save 22591, and no rule can, because 22591 is a Track-C identity law — proved.**
Chasing the last case-tree cell produced a *conflict* rather than a rule, and the conflict turned
out to be a purely equational consequence of the law. **22591 ⊢ `a = I3(a)`** where
`I1 = (a*a)*((a*a)*a)`, `I2 = a*(a*I1)`, `I3 = I1*(I1*I2)` — seven substitution instances, each
verified mechanically by `gen/_p2_ident22591.py`, **no freeness of any product assumed**. `a` and
`I3(a)` are distinct terms of the free magma, so **22591 has no model whose carrier is the free term
algebra**: no rule system, tag automaton, extractor repair or existential decoder can exist for it.
That closes rows **0017 / 0052 / 0069** to this whole approach and sends them to a quotient carrier.

So the mechanism exists and should be added to the extractor (it is general, and 21864's hand-built
`RA` rule is an independent discovery of it) — but 22591 was never the law it could save.

---

## 1. 22591 — the R4 experiment, done

`22591:  x = (y*(y*x)) * ((x*x)*z)`;  `P = op(y,x)`, `u = op(y,P)`, `S = op(x,x)`, `v = op(S,z)`,
top `= op(u,v)`. Baseline `gen/q22591b.py` rules (both read the payload out of a *free* side):

```
Ra   u = J a c,  c = J a b,      op(b,b) == a1 v        -> b     # payload from u, square checked on v
Rb   u = J a c,  a1 v = J b b,   op(a,b) == c           -> b     # payload from v, decoder checked on u
```

Files: `gen/_p2_q22591.py` (the model, MODE is a bitmask of the extra rules), `gen/_p2_tree22591.py`
(case tree + `run_tests` + deep20k + identity probe), `gen/_p2_tr.py` (per-instance trace),
`gen/_p2_conflict.py`, `gen/_p2_proof22591.py`, `gen/_p2_ident22591.py` (the proof).

### 1.1 R4's rule never fires — the gate cut is the whole obstruction. MEASURED.

R4's rule is `op(u,v) = invsq(a1 v)` guarded by `op(a1 u, invsq(a1 v)) == a2 u`, with
`invsq(s) := J T (J T s)`, `T = op(s,s)`. As MODE 1: **12 fails, identical to baseline; the rule
fires 0 times.** On the recorded refutation instance

```
x = ((g0*g0)*((g0*g0)*g0))   y = (g0*(g0*g0))   any z
u = J y g0  (sz 7)     v = J g0 z  (sz 3)     s = a1 v = g0
invsq(g0) = J (J g0 g0) (J (J g0 g0) g0) = x   (sz 9)      <- R4's closed form is CORRECT
msr(y, x) = max(5,9)^2 + 5 + 9 = 95      msr(u, v) = max(7,3)^2 + 7 + 3 = 59
```

`95 > 59`, so the gated call returns the free `J y x` and the guard fails. **This is not tunable.**
The reconstructed payload is always *bigger* than `u` and `v` — that is exactly why it was
destroyed — so any guard that applies `op` to the reconstructed payload is dead by construction.
R4's "termination is therefore NOT the obstacle" is right about `invsq` and wrong about the guard.

### 1.2 The fix: unfold the guard into structural conditions

`op(a1 u, x) == a2 u` with `x = invsq(s) = J T (J T s)` can only hold through one of the two decode
rules applied to the pair `(a1 u, x)`. Unfold both; branch Ra gives the rule that works, and every
`op` in it is on `a2 u` or `a1 v` — strict subterms, hence below the gate:

```
Rc   tg u = 2 ∧ tg v = 2                              # P dec, S dec, v FREE
   ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2
   ∧ a1 (a1 u) = a1 (a2 (a1 u))                       # a1 u = J p (J p b')  is a decoder for b'
   ∧ a2 (a2 (a1 u)) = a2 u                            # b' = a2 u
   ∧ op(a2 u, a2 u) = op(a1 v, a1 v)                  # the two readings agree on a1 x
  -> J T (J T (a1 v))          T = op(a1 v, a1 v)
```

Two corrections to R4, both load-bearing:

* R4 asserts `a2 (a2 (a1 u)) = s`. The correct condition is `= a2 u`. They coincide only because the
  recorded instance happens to have `a2 u = a1 v = g0`.
* R4 drops the square agreement. It is **necessary**: reading the payload out of `x = J q (J q s)`
  forces `a1 x = q = op(s,s)` from the `v` side and `a1 x = op(c,c)` from the `u` side.

A second rule is needed when the *v*-side product also decoded, so `v` is a payload rather than
`J S z` — and then `v` need not even be a `J`-node, so the rule must sit **outside** the `tg v = 2`
test that Ra/Rb/Rc share (missing this cost an hour):

```
Rd   u[0] = J                                          # P dec, S dec, v DEC
   ∧ a1 u = J p (J p (a2 u))
   ∧ op(a2 u, a2 u) = v
  -> J v (J v (J T (J T v)))    T = op(v,v)            # = invsq(invsq v), with op(S,S)=v substituted
```

`x = invsq(S)` and `S = invsq(v)`, so naively `x` needs `op(S,S)` — above the gate. But the guard
has already established `op(S,S) = v`, so **substituting the known value for the out-of-gate call**
leaves exactly one `op`, on `v`. That substitution is the second half of the technique.

### 1.3 Measured

| test | baseline (Ra,Rb) | +Rc | +Rc+Rd |
| --- | --- | --- | --- |
| sweep x ≤ 9, y ≤ 5, z ≤ 3 (72,600) | **12 fails** | **0** | **0** |
| case tree, 48 constructed instances, 6 reachable cells | 28 fails | 12 fails (all cell FTT) | 12 fails (all cell FTT) |
| identity probe (7,200–14,400 chained encodings) | fails | 2 fails | **0** |

The case tree is the useful instrument: `u = op(y, op(y,x))` **provably never decodes** (both decode
rules would force a term to equal a proper subterm of itself), so the tree is `2^3 = 8` cells, of
which `S` free ∧ `v` decoded is impossible for the same reason, leaving 6 — and all 6 are realised
by explicit chained-encoding constructions. Every failure after Rc/Rd sits in exactly one cell,
**FTT** (`P` free, `S` decoded, `v` decoded), which needs

```
Re   u = J a (J a b),  S := op(b,b),  S = J r (J r v)   -> b
```

Re closes FTT (12 → 0) and **breaks cell TTT-3** (4 new failures). That is not a tuning problem.

### 1.4 Why Re cannot be repaired — and the proof that follows from it

Re's guard is *exactly* the structural content of the FTT reading, and the pair it fires on is
*genuinely* forced to that value by an instance of the law. The trace (`gen/_p2_tr.py`) shows the
collision: with `I0 = g0`, `T = op(I0,I0)`, `I_{k+1} = invsq(I_k)` and `Y = J p (J p I2)`,

* FTT at `x := I2`, `y := p`, `z` a decoder for `I0` forces **`op(Y, I0) = I2`**;
* once that holds, `op(Y, op(Y, I0)) = op(Y, I2) = op(Y, op(Y, I3))`, so the instances
  `x := I0, y := Y` and `x := I3, y := Y` land on the **same pair** and demand `I0` and `I3`.

Chasing that to the bottom gives a derivation with no reference to the carrier at all:

> **Theorem.** In every magma satisfying 22591, with
> `I1 = (a*a)*((a*a)*a)`, `I2 = a*(a*I1)`, `I3 = I1*(I1*I2)`, and any `b`, `Y = b*(b*I2)`:
>
> | step | instance | conclusion |
> | --- | --- | --- |
> | 1 | `L[x:=a, y:=a*a, z:=(a*a)*a]` | `a = I1*I1` |
> | 2 | `L[x:=I1, y:=a, z:=a*I1]` | `I1 = I2*I2` |
> | 3 | `L[x:=I2, y:=I1, z:=I1*I2]` | `I2 = I3*I3` |
> | 4 | `L[x:=I2, y:=b, z:=I1]` | `I2 = Y*a` |
> | 5 | `L[x:=I2, y:=b, z:=I1*I2]` | `I2 = Y*I3` |
> | 6 | `L[x:=a, y:=Y, z:=(a*a)*a]` | `a = (Y*I2)*I1` |
> | 7 | `L[x:=I3, y:=Y, z:=I2]` | `I3 = (Y*I2)*I1` |
>
> hence **`a = I3`**, i.e. `x = ((x*x)*((x*x)*x)) * (((x*x)*((x*x)*x)) * (x*(x*((x*x)*((x*x)*x)))))`.

Steps 1–3 are the square-root tower: every element is a square of a *constructible* element
(R1 made non-constructive; this makes it explicit and iterable). Steps 4–5 say the same `Y` decodes
both `a` and `I3` to `I2`. Steps 6–7 then read the same product two ways.

`gen/_p2_ident22591.py` checks all seven steps mechanically: each is a literal substitution instance
of the law followed by replacement of a subterm by an already-derived equal, and every assertion
passes. **No product is assumed free**, so the identity holds in every 22591-magma.

**Consequence.** `a` (size 1) and `I3(a)` (size 33) are distinct elements of the free magma, so
**22591 has no model on the free term algebra.** The entire construction family — free carrier,
`op` defined by ordered structural rules with gated nested calls — is refuted for 22591, and
`gen/SEMANTIC_TABLE.md`'s "46 semantic failures / IDENTITY LAW (Track C)" is now a proof rather than
a measurement. Rows 0017 / 0052 / 0069 need a quotient carrier in which `I3(x) = x` holds
definitionally, and `PLAYBOOK_QUOTIENT.md` §4 plus `P2_EXISTENTIAL_DECODER.md` R1 already rule out
the two obvious ones (all-squares-equal is trivialising; recognisable invertible squares are
refuted by surjectivity of `S`).

---

## 2. The general mechanism — ENC-INV / DEC-STRUCT

State it once, because it is what the other laws need.

**Setting.** A law `x = A * B` whose free model reads the payload out of one side. The extractor
(`closedform.py`) emits, per reading of the pattern, a rule whose guard is a nested `op` on
determined subterms. It fails exactly when the same term is simultaneously a legal `A`-term and a
legal `B`-term, so both readings decode and the payload is gone from both — the cell
`PLAYBOOK_QUOTIENT.md` §4 calls the *existential decoder*.

**ENC-INV.** In that cell the payload is still determined, by the encoding-side equation alone,
which is one equation of the model in one unknown. Solve it in closed form by **inverting the decode
rule that produced it**: a rule's result is an accessor path into its own pattern, so inverting it is
rebuilding the pattern with the known value in the payload slot. For 22591, rule Ra applied to
`(x,x)` says `x = J q (J q r)` with `op(r,r) = q`, result `r`; setting `r := s` gives `q = op(s,s)`
and

```
Inv(s) = J (op(s,s)) (J (op(s,s)) s)          -- one op call, on a strict subterm of v
```

**DEC-STRUCT.** Never verify with `op` applied to `Inv(s)` — that call is **always** above the
recursion gate (§1.1). Instead emit the *symbolic precondition* of the decode rule that would have
produced `a2 u` from `(a1 u, Inv(s))`, with `Inv(s)`'s own accessors replaced by their definitions
(`a1 (Inv s) = op(s,s)`). Every surviving `op` is then on a strict subterm of `u` or `v`.

**Substitute known values for out-of-gate calls.** When the reconstruction nests (`Inv(Inv(v))`,
rule Rd), the inner `op` is above the gate — but the guard has just proved its value, so write the
value instead of the call. This is what keeps the nesting depth from costing recursion depth.

No new DSL construct is needed: the rules are `(conds, result_expr, tag)` over
`TG/EQ/OPEQ` and `A1/A2/OP/J`, exactly as `gen/EXTRACTOR_NOTES.md` describes. The extraction step
that emits them, for the cell where both readings decode: (i) invert the encoding-side rule's result
accessor to get `Inv` as a `J`/`OP` expression in `A1(V)` (or `V` itself when the `v`-side product
also decoded); (ii) emit the decoder-side rule's guard with each `A1(x)/A2(x)` replaced by the
corresponding component of `Inv`; (iii) result `Inv`. **Two rules per cell**, one for `v` free and
one for `v` decoded — and the second must sit outside the `tg v = 2` test.

**It was found once before, independently.** `gen/_x21864_rules.py`'s `RA` ("the RECURSIVE As
rule") eliminates `Acc(p,q,w) := ∃t. op(p, op(t,q)) = w` by the closed test
`op(w, J(q, J(q, p))) = q` — the same move for a different law, with the guard already below the
gate because its target is `U` rather than the reconstructed payload. Two independent derivations is
the argument that this is the mechanism and not a trick.

**Its limit, and this is the important half.** ENC-INV makes the rule *definable*; it does not make
the law *satisfiable*. When the reconstruction can be iterated — `Inv`, `Inv∘Inv`, … — the rule set
grows a level per iteration, and the tower `I_{k+1} = Inv(I_k)` is exactly the object that produces
the equational collision of §1.4. **So the right first move on any law in this cell is to build the
tower and look for the collision, before building the rules.** The tower is three instances
(steps 1–3 above); the collision is four more. That is minutes of work and it decides the row.

---

## 2.1 Why the 22591 proof does NOT transfer verbatim — the coset criterion

Worth stating, because it is the cheap test for "is this law killable the same way".

Steps 4–5 of §1.4 need **two distinct known elements that both encode the same `x`**, and they get
them for free because 22591's encoding side is

```
E(x, z) = (x*x) * z          z FREE and in the RIGHT slot of the OUTER product
```

so `E(x, M) = S_x * M` is a **full left-translate of one element** `S_x = x*x`. Both `a = I1*I1` and
`I3 = I1*(I1*I2)` are literally of the form `I1 * t`, hence both lie in `E(I2, M)` — and the A-side
`Y*(Y*·)` then maps them to the same thing. Classify the seven laws by that property (E = the right
factor of the RHS; "free" = the variable occurs nowhere else):

| law | encoding side | free variable in the outer right slot? |
| --- | --- | --- |
| **22591** | `(x*x) * z` | **YES** — `E(x,M) = (x*x)*M`, a coset. This is what the proof uses. |
| 21865 | `x * (x*z)` | no — `z` is shared with the A-side, and it is nested |
| 21866 | `x * (x*w)` | `w` is free but **nested**: `E(x,M) = x*(x*M)`, not a coset |
| 21864 | `x * (x*y)` | no — `y` is shared with the A-side |
| 23357 | `x * (y*z)` | `z` free but nested; `y` shared |
| 23653 | `z * (x*z)` | no |
| 24199 | dual of 21864 | — |

So **22591 is the only one of the seven with the coset shape**, and the seven-step proof is
genuinely specific to it. The *method* still transfers — build the square-root tower (three
instances, identical for all seven: substituting every variable by `x` turns each law into
`x = W*W` with `W` an explicit term, so `I_{k+1} := W(I_k)`), then look for two elements the A-side
identifies. What is missing for the other six is the second half, and the coset table says where to
look: for a nested `E(x,M) = x*(x*M)` you need a lemma about `x*M` first.

## 3. Per-law status

| law | rows | semantic fails (1 gen) | status after this session |
| --- | --- | --- | --- |
| **22591** | 0017, 0052, 0069 | 46 | **PROVED Track C** — `22591 ⊢ a = I3(a)`, `gen/_p2_ident22591.py`, 7 mechanically checked steps. No free-carrier model exists. Needs a quotient in which `I3(x)=x`; all-squares-equal is trivialising (§4 of the playbook) and recognisable squares are refuted (R1). The ENC-INV model `gen/_p2_q22591.py` MODE 6 is nevertheless the best free-carrier approximation on record (0 fails on 72,600 assignments + identity probe; residue = one case-tree cell) and is the right starting point if a carrier is found. |
| 21865 | 0039, 0057 | 68 | Same signature. Every element is a square (playbook §4), so the tower of §1.4 exists verbatim with `I1 := a*(a*a)` (`L[x=a,y=a,z=a]` gives `a = I1*I1` literally). **Do the collision search before any rule work.** |
| 21866 | 0020, 0028 | 18,515 | Same, and the extreme case. `I1 := a*(a*a)` again (`L[x=a,y=a,z=a,w=a]`). |
| 24199 | 0086 | 230 | Dual of 21864 — work the 21864 side (`SEMANTIC_TABLE.md`), then `dualcert.py`. |
| 21864 | 0033 | 5 (2 at size ≤ 7) | **The one to ship.** `gen/_x21864_t8.out` records a **13-rule model with `rv.run_tests` = 0 fails and 3 × 20,000 deep tests = 0 fails** — i.e. it already meets wave-3 standards 1 and 2. Remaining: the case tree, `identity_probe`, then Lean (13 rules ⇒ `PLAYBOOK_PROOF.md` §3 digest is mandatory). Caveat: substituting every variable equal gives `x = W*W` with `W = x*(x*x)`, so **all-squares-equal is trivialising here too** and the 34889 E-quotient is *not* available; the free-carrier 13-rule model is the live path. |
| 23357 | 0048 | **still unmeasured** — `smallcheck.py 23357 9 1` and `... 7 1` were launched and had produced no output after 15 min (the semantic model's reading recursion is the cost, not the pool). Outputs will land in `gen/_p2_sem23357.out` / `gen/_p2_sem7.out`; re-launch with a smaller pool (`5 1`) if they are still empty | `gen/hole23357.lean` (7,179 B, 0 sorries) is **not** a proof — it is a Lean-verified *refutation* of the generated skeleton, with three explicit holes. `gen/_x23357_val12.out` records a minimised 6-rule set that survives 3 × 20,000 deep tests; `gen/_x23357_perm.out` records that dropping to 5 or 4 rules costs 112/146 failures. |
| 23653 | 0080 | **still unmeasured**, same reason (`gen/_p2_sem23653.out`) | dual partner of 23357. Note both laws' extracted rule sets already read `deep tests: 0/3000 fails` in `gen/rules23357.txt` / `gen/rules23653.txt` — the *only* two laws of the seven that do — so they are the best free-carrier prospects in this set and should be measured first next session. |

### 3.0 The one-line triage for the next agent

Substituting every variable by `x` turns each of the seven laws into `x = W(x)*W(x)`, so the
square-root tower `I_{k+1} := W(I_k)` exists for all of them and **all-squares-equal collapses every
one of them to the trivial magma** — the 12073/27859/34889 E-quotient is unavailable across the
board. Ranked by what is actually left: **21864 (a validated 13-rule free-carrier model already
exists, 2 rows with the dual)** > **23357/23653 (0/3000 deep failures, semantic status unmeasured,
2 rows)** > 21865/21866 (Track C by measurement, proof not yet written, 4 rows) >
**22591 (Track C by proof, 3 rows, closed to this approach)**.

### 3.1 The 21864 residue, for whoever picks it up

`gen/_x21864_t8.out` is the validated set (`GEN + [R4c,R5c,RA,R6d,R6e,RB,RB2,RD]` in
`gen/_x21864_rules.py`); `gen/_x21864_t7.out` is the same set minus `RB2` and fails 1/20,000 on seed
78, which is what `RB2` was added for. Its two size-≤7 semantic failures are

```
y = (g0*(g0*g0))      z = x = ((g0*(g0*g0))*g0)     ->  (g0*(x*(x*y)))
y = (g0*((g0*g0)*g0)) z = x = ((g0*(g0*g0))*g0)     ->  (g0*(x*(x*y)))
```

— in both, `op(y, op(z,x))` decodes to `g0` and the top product is then free. Both have `z = x`.

---

## 4. Dead ends, measured, do not repeat

| idea | result |
| --- | --- |
| R4's `op(a1 u, invsq(a1 v)) == a2 u` guard | fires **0 times**; `msr(a1 u, invsq(a1 v)) > msr(u,v)` always. Not tunable (§1.1) |
| adding the invsq rule to a one-rule toy | 507 → 951 failures (recorded in `P2_EXISTENTIAL_DECODER.md`); the toy is not the model — irrelevant, ignore it |
| rule Re (the FTT cell) at any position | closes 12 failures, opens 4 in cell TTT-3; the collision it creates is forced by the law (§1.4) |
| an e-graph congruence closure over law instances on free terms (`gen/_p2_ident.py`) | **invalid method** — it treats `J` as `op`, so it "derives" the law's own instances as identities. Kept only as a warning; use the substitution-plus-rewrite checker (`gen/_p2_ident22591.py`) instead |
| random / deep / closure / critical fuzz for the deep cells | reach 4 of 6 reachable cells; the FTT and TTT cells need explicit chained-encoding construction (rail 50 again) |

---

## 5. Coordinator tasks (second pass)

### 5.1 Do 22591 / 21865 / 21866 force the TRIVIAL magma?  — measured, and the answer is "no evidence"

If eq1 ⊢ `x = y` the rows would be **TRUE** for every eq2 and no FALSE certificate could exist. The
free algebra of the variety is the term algebra modulo the congruence generated by the law's
instances, so the test is an e-graph over a bounded pool asking whether two generators merge.
(My §4 dismissal of `gen/_p2_ident.py` was wrong in one direction: an e-graph over law instances
*is* the free algebra in the variety. What it cannot do is certify a *model*, which is what I was
using it for. `gen/_p2_trivial.py` is the corrected tool.) A merge is a **proof** — every union is
one law instance; the absence of one is only a bound.

`python gen/_p2_trivial.py <eq> 5 2 60 3`, pool = terms of size ≤ 5 over **two** generators:

| law | instances | terms | classes | generators merged? |
| --- | --- | --- | --- | --- |
| 22591 | 39,304 | 42,594 | 3,278 | **no** |
| 21865 | 39,304 | 98,239 | 48,387 | **no** |
| 21866 | 1,336,336 | 1,767,307 | 48,304 | **no** |

Congruence closed in every round. `g0`'s class has 1,157 members for 22591 and 50,674 for 21866 and
`g1` is in none of them. **So there is no evidence these laws collapse, and the rows should not be
attempted as TRUE.** Not a proof of non-triviality (the pool is bounded at size 5 / two generators);
raise `poolsize`/`maxsz` if it ever matters. The classes it does merge are the expected ones —
`g0 ~ (g0*(g0*g0))*(g0*(g0*g0))` for 21866 is exactly "every element is a square", visible as data.

### 5.2 21864 — a compiling skeleton, a validated model, and the exact remaining goal

Everything below is done; `theorem law` is the only `sorry`.

* `gen/_p2_emit21864.py` emits the package. **`gen/rep21864/` = 11 rules, 7,142–8,377 B**,
  `gen/rep21864_13/` = the full 13.
* **Both compile.** `D=<dev> bash devlean2.sh gen/rep21864/rec21864.lean` reports exactly one line:
  `warning: declaration uses 'sorry'` at `theorem law`. The definition, the `termination_by`/
  `decreasing_by`, `op_free`, `rhs` (which refutes eq2 **20034**, i.e. row 0033) and `submission`
  are all done and checked. `python devrow.py 21864 20034` builds the dev dir.
* Validation of the 13-rule set **reproduced this session**: `rv.run_tests(law, rules, [3,4,5],
  3000, 12000)` = **0 fails**, then deep20k on seeds 77 / 78 / 91 = **0 / 0 / 0**.
* **Minimisation, with a trap worth recording.** A firing census over the full validator's own load
  (`python gen/_p2_min21864.py census`, 48.7 s) says three rules never fire:
  `Bs` (idx 2), `As|E2a` (idx 8), `As|yEnc2` (idx 11). Dropping all three gives a 10-rule set that
  passes `run_tests` with **0 fails** — and then **fails deep20k seed 78, 1/20,000**. That is the
  single failure `RB2 = As|yEnc2` was added for. **`run_tests` at 3000/12000 cannot see it; only
  deep20k can.** So a validated removal for these laws must run deep20k on 3 seeds, not
  `run_tests`. Safe drop is `{Bs, As|E2a}` → **11 rules, and that set is now fully
  validated**: `run_tests` 0 fails plus deep20k seeds 77/78/91 = 0/0/0 (`gen/_p2_val21864c.out`).
  **`gen/rep21864/` holds the 11-rule package, 7,597 B, and it compiles** — use it.
  `gen/rep21864_13/` is the 13-rule fallback (8,377 B).
* **The E-quotient is NOT available for 21864** (I checked, because `LEMMA_LIBRARY.md` asks):
  substituting every variable by `x` turns the law into `x = W*W` with `W = x*(x*x)`, so
  all-squares-equal forces `x = E` for every `x`. **Same for all seven laws in this set** — the
  34889 route is closed across the board and the free-carrier rule model is the live path.

**The remaining goal, verbatim:**
```lean
theorem law (x y z : M) : op (op (y) (op (z) (x))) (op (x) (op (x) (y))) = x
```

**The lemma plan.** The generic chain is `P = op z x = J z x`, `u = op y P = J y (J z x)`,
`Q = op x y = J x y`, `v = op x Q = J x (J x y)`, and then the top pair fires **P1** (the free rule)
because `a2 (a2 u) = x = a1 v = a1 (a2 v)` and `a1 u = y = a2 (a2 v)` — so the top is one rule
lemma and everything else is freeness of the four inner products. Follow `LEMMA_LIBRARY.md`:

1. `op_cases` in the packed form (`AGENT_BRIEF.md`) — at 11 rules **do not use `split`**, use the
   `Z` combinator from `certs/research_order5_hard_0001.lean`
   (`Z (R) (h1 : c → R a) (h2 : ¬c → R b) : R (if c then a else b)`); `split` dies past ~10 rules
   and the step limit cannot be raised.
2. State the recursive branches **existentially** (`∨ (tg v = 2 ∧ ∃ q, msr u q < msr u v ∧ …)`) —
   `RA`/`RD`/`RB` are the recursive ones and this is what took 32281's rule from a full packed-chain
   unfold to four lines.
3. `mx {a b u v} (h : msr a b < msr u v) : max (sz a) (sz b) ≤ max (sz u) (sz v)` before reaching
   for fuel induction — every nested call here is msr-gated, so its own gate bounds its result.
4. Factor the shared conjunct: P3–P10 all require `tg v = 2 ∧ tg (a1 v) = 2`, so one `WF`-style
   lemma frees every product whose `v` is not of that shape.

Its two size-≤7 semantic failures (`smallcheck.py 21864 7 1` → 2 fails, 0 conflicts) are in §3.1;
both have `z = x`, so the `z := x` case of the chain is where the coincidence lemmas will be needed.

### 5.3 23357 / 23653 — still unmeasured, and the reason is now known

`smallcheck.py 23357` produced no output at `9 1`, `7 1` **or `5 1`** (60 s each, three separate
launches). The cost is `freemodel.Free`'s reading recursion on this law shape, not the pool size, so
shrinking the pool does not help — it needs `--closed` (which measures the extracted system, not the
semantic model) or a bounded-`max_rdepth` run. **They remain the best free-carrier prospects of the
seven** — `gen/rules23357.txt` and `gen/rules23653.txt` are the only two of the seven that read
`deep tests: 0/3000 fails` — and `gen/_x23357_val12.out` records a minimised 6-rule set surviving
3 × 20,000 deep tests. `gen/hole23357.lean` is a Lean-verified **refutation** of the *generated*
skeleton (three holes), not a proof; the 6-rule repaired set in `gen/rep23357b/` supersedes it.

---

## 6. STOP — 21864's rule sets are FALSE.  Do not write `theorem law`.

The coordinator's **level-k descent** oracle (`gen/_w3_12087_deep3.py`, sibling agent's, on law 12087)
adapted to 21864 as **`gen/_p2_deep321864.py`** refutes the model. `theorem law` was not attempted;
proving it would have been proving a false statement.

### 6.1 The adaptation, and the first version of it that was WRONG

21864's decode is a *matched pair*, not a single encoding:
```
decoder side   AT(y,z,t) = op(y, op(z,t))        encoding side   BT(t,y) = op(t, op(t,y))
the law is exactly     op( AT(y,z,t), BT(t,y) ) = t
```
so `op(a,·)` decodes for **exactly one** `b` — a tower of encodings of one payload (my first attempt)
forces nothing. It returned `('F','F','F','F')` in 4,800/4,800 instances: **a vacuous pass**, which
would have read as a clean bill of health. The working construction iterates the *pair*:
```
(t_0, y_0) = (small, small)
(t_{k+1}, y_{k+1}) = ( AT(y_k, junk, t_k),  BT(t_k, y_k) )        so  op(t_{k+1}, y_{k+1}) = t_k
```
`y_{k+1}`'s own inner product `op(t_k, y_k)` is again a decode, so the rule descends k levels in one
argument. Two variants feed the tower into the law's chain:
* **A** `x := t_L` (deep decoder), `y := y_L`, `z := junk` → `Q = op(x,y)` descends;
* **B** `x := y_L` (deep **encoding**), `z := t_L` (its matched decoder), `y := small` → `P = op(z,x)`
  descends.

**Always check the cell census before believing a pass**: variant A is `('F','F','D','F')` in
100% of instances, variant B `('D','F','F','F')`. A run whose cells are all `F` proves nothing.

### 6.2 Result

Full matrix, levels 1-4 x 2 junk pools x 4 seeds x 400 = **12,800 instances per cell**, every one of
them with at least one genuine decode:

| rule set | variant A | variant B |
| --- | --- | --- |
| `gen9` (the 9 rules the extractor generates) | **0** bad | **9,606** bad |
| **`ship11`** (the package in `gen/rep21864/`) | **0** bad | **11** bad |
| `t8_13` (13 rules) | **0** bad | **7** bad |

So the eight hand repairs in `gen/_x21864_rules.py` (`R4c, R5c, RA, R6d, R6e, RB, RB2, RD`) take the
variant-B cell from **75% broken to 0.09% broken** - they are doing real work and are close - but
they do not close it. That residue is what kills the proof.

Variant B failure rate, `ship11`, 4 seeds × 1,500 instances per level:
**level 1 → 6 bad, level 2 → 12, level 3 → 10, level 4 → 0, level 5 → 0.**
So this is **not** only a deep-descent cell — it already fails at level 1; the earlier oracles simply
never built this shape. `cycles = 0` throughout, and the instance reproduces on **fresh** evaluators
with no shared memo (`gen/_p2_bad21864.py`).

### 6.3 The instance, verbatim

```
x = (g0*g1)*(g1*(g1*g0))                                     size 9
y = ((g0*g1)*(g0*g1))*(g1*(g1*g0))                           size 13
z = ((g1*(g1*g0))*((g1*(g1*g0))*g0))*((g0*g1)*(g0*g1))       size 21

P = op(z,x) = (g0*g1)                                        DECODED
u = op(y,P) = J y (g0*g1)                                    free
Q = op(x,y) = J x y                                          free
v = op(x,Q) = J x (J x y)                                    free
top         = J u v                                          free   -> the law demands x
```
Identical under `gen9`, `ship11` and `t8_13`; on the top pair **no rule's guard holds at all**.

### 6.4 Diagnosis — which rule is missing, and why patching it does not obviously terminate

`u = J y P` is free, so `a1 u = y` and `a2 u = P`; `P` decoded, so `x` is gone from `u`. But
`v = J x (J x y)` is free, so **`x` is sitting at `a1 v`** and an A1s-shaped rule should read it.
P3 (`A1s`) requires `a2 u = a1 (a1 v) ∧ a2 u = a1 (a2 (a1 v))` — it expects the decode
`op(z,x) = w` to have forced `x = J w (J w y')`, i.e. `a1 x = a1 (a2 x) = w`. Here
`a1 x = (g0*g1) = P = w` ✓ but `a1 (a2 x) = g1 ≠ w` ✗, **because `x`'s own inner product
`op(w, y')` was itself decoded** — `x = op(w, op(w,y'))` with the inner product not free.

That is precisely the hole `R4c`/`R5c` (`A1s|l2`) close **on the other side** of the pattern. Adding
the mirror rule closes level 1; the tower says level 2 then needs `|l3`, and so on — the infinite
repair hierarchy `CLAUDE.md` describes for this family. **Inference, not proof**: the measured fact
is that 9, 11 and 13 rules all fail, and that each existing `|l2` rule closes exactly one level of
one side.

### 6.5 What to do instead

Per `WAVE2_PROMPT.md` §2 a rule may have a nested `op` **as its result**, and `gen/rec18137b.lean` is
the shipped template. The right object here is the **left inverse of `op`**: given `(z, N)` with
`op(z, x) = N`, recover `x`. It is well founded because a decoded `op u w` satisfies
`sz (op u w) < sz w`, so the recursion descends on the second argument — which is exactly what makes
the level-k tower terminate. That replaces the `|l1, |l2, |l3, …` family with one recursive rule.

**Row status is therefore unchanged: 0033 and 0086 are NOT shippable from this model.**
`gen/rep21864/` still compiles and its `op`, termination, `op_free`, `rhs` and `submission` are all
sound and reusable — only the *rule set* is wrong, so a repaired set can be dropped straight into
`gen/_p2_emit21864.py` and re-emitted.

### 6.6 The oracle ladder for this project, updated

`run_tests` (random + rule-shaped) → `deep_tests` 20k×3 (random deep) → the case tree (each product
decodes **once**) → the both-decoded census (**two**) → `identity_probe` → **the level-k descent
(the same rule at successive depths of one argument, in both variants)**. 21864's 11-rule set passed
the first five and dies on the sixth. Every escalation of this project's validation standard has been
forced by a model that passed the previous one; this is the seventh.

---

## 7. The recursive (search) decoder for 21864 — built, measured, NOT yet clean

`gen/_p2_21864_lab.py` — self-contained, free carrier `M ::= g n | J a b`, **0.2 s for the whole
oracle stack** (`python gen/_p2_21864_lab.py <v1|v2|v3|v4>`). Following `gen/NOTES_17286.md`: keep
the carrier, drop the rule list, search for the certificate.

### 7.1 The shape

```
op u v =
  if tg v = 1 then J u v else
  let t = a1 v, X = a2 v                       -- payload candidate; BT(t,y) = op(t, op(t,y))
  branch U  (u is the free A-term):  tg u ≠ 1 ∧ op(t, a1 u) = X ∧ okA(u, t)      -> t
  branch A  (the A-side product itself decoded to u; v must be the free B-term):
            tg X ≠ 1 ∧ a1 X = t ∧ <u is coded inside t>                          -> t
  else J u v

okA(u,t) :  (A0) tg (a2 u) ≠ 1 ∧ a2 (a2 u) = t            -- A-side inner product FREE
         ∨  (A1) <t codes a2 u>                            -- A-side inner product DECODED
         ∨  (A2) the same, k unwraps down
```
One recursive call, `op(a1 v, a1 u)` — **both arguments proper subterms**, so `sz u + sz v` decreases
unconditionally and linearly: no `msr`, no fuel induction, the 27859 shape the coordinator's rail 3
asks for. Termination is not the problem here.

Branch A is not optional: `P7..P11` of the rule model have **no `tg u` condition** at all, and v1
omitted the branch. Adding it took the small exhaustive sweep 60 → 44 bad.

### 7.2 The measurement — and the tension that is the whole result

`<...codes...>` is the one free choice. Two spellings, four versions:

* **weak** `a1 t = w` (bare head)
* **strong** `codesB(t,w) := tg t ≠ 1 ∧ a1 t = w ∧ tg (a2 t) ≠ 1 ∧ a1 (a2 t) = w`
  (the *free* B-term shape, which pins the key `y' = a2 (a2 t)`)

| version | okA | branch A | level-k descent | exh sz≤5/2gen (10,648) | exh sz≤7/1gen (729) | deep+coinc | forced |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v1 | weak | *absent* | **0** | 60 | 21 | 2 | 6 |
| v2 | weak | weak | **0** | 44 | 11 | 5 | 4 |
| v3 | strong | strong | **1002** | 8 | 15 | 2 | 2 |
| **v4** | strong | weak | **996** | **0** | 8 | 6 | **0** |

**The two failure modes are complementary and no choice of a *structural* certificate closes both.**
The strong certificate is right for shallow terms — v4 is the first model in this project to get
**0 bad on 10,648 exhaustive triples and 0 on forced firing** — and it is wrong for the tower, where
the B-term's inner product `op(w,y')` has itself decoded, so `a1 (a2 t) ≠ w` and the certificate
rejects a legitimate reading: 996 bad on the level-k descent, against 0 for the weak spelling.

### 7.3 What the fix has to be (concrete, and it is v5)

The predicate both spellings are approximating is
```
codes(t, w)  :=  a1 t = w  ∧  ∃ y'. op(w, y') = a2 t
```
— "t is `BT(w,y')` for some key". `codesB` is its free-inner special case (`y' = a2 (a2 t)`); the
bare head drops the second conjunct entirely. **It must be recursive, not structural**, exactly as
17286's `codes u c` re-runs `op u (a1 c) = a2 (a2 c)` instead of shape-matching.

The witness `y'` is not determined by the pair, so v5 must **search** it, and 17286 says where the
candidates come from: *proper subterms of the term being certified*. Concretely
```
codes(t, w) :=  a1 t = w  ∧  ∃ c ∈ [a2 (a2 t)] ++ unwraps(a2 t).  op(w, c) = a2 t
```
with `unwraps(P) : c := a1 (a2 (a2 c))` while the code shape holds. Two rails from
`gen/LEMMA_LIBRARY.md` apply verbatim and are cheap to get wrong: **no size cutoff on a candidate**
(17286 lost two iterations to a `sz c ≥ sz v` "sanity guard"; my own unbounded-junk fact is the same
statement), and every shape test is `tg t ≠ 1`, never `tg t = 2`. The extra recursive call is
`op(w, c)` with `w = a1 v` and `c` inside `a2 t ⊆ v` — still both arguments proper subterms of `v`,
so rail 3 is preserved and the measure stays `sz u + sz v`.

### 7.4 v5 BUILT AND MEASURED — it is exactly v3, and the reason is the point

I implemented the recursive `codes` above (`VER == 'v5'`, `gen/_p2_21864_lab.py`), searching `y'` over
`[a2 (a2 t)] ++ unwraps(a2 t)` with no size cutoff. Result, digit for digit identical to v3:
**descent 1002, exh sz≤5/2gen 8, exh sz≤7/1gen 15, deep 2, forced 2** — the `codes` branch fires 701
times and finds nothing `codesB` did not.

**Why, and this is the finding.** In the tower case `t = BT(w,y')` with the inner product `op(w,y')`
*decoded*, so `a2 t` is a payload — and `y'` is **not a subterm of `a2 t`, of `t`, or of the pair at
all**. It was destroyed by the very decode we are trying to certify. 17286's candidate rule
("projections and unwraps of the term being certified") therefore cannot reach it, and no search over
subterms can: this is `PLAYBOOK_QUOTIENT.md` §4's existential decoder reappearing one level down,
inside the certificate rather than inside the payload.

So the honest statement is: **the search decoder does not close 21864 by searching subterms.** The
witness has to come from somewhere else — the two candidate sources not yet tried are (a) the outer
pair's own key (`a1 u` in branch U, `a2 (a2 v)` in branch A), which is free to pass down and is the
only key the law guarantees is shared between the A- and B-sides; and (b) ENC-INV from §2 of this
document — inverting the encoding to a closed form instead of searching for it, which is what worked
for 22591's analogous cell. (a) is a two-line change to `codes`'s signature and should be tried first.

### 7.5 Status

**Rows 0033 and 0086 are still not shippable.** v4 is the best model this project has had for 21864
on the shallow oracles (0/10,648 exhaustive, 0 forced firing, against the 11-rule model's clean
sweeps but 11/12,800 descent failures) and it is refuted by the descent; v2 is the mirror image.
`gen/rep21864/`'s `op` scaffolding, `termination_by`/`decreasing_by`, `op_free`, `rhs` and
`submission` remain sound and reusable — but the *emitted* `op` is rule-list-shaped, so a search
decoder needs its `op` written by hand rather than through `leangen.emit`. That is the 17286 file
(`gen/_proof17286.lean`) to copy from, not `gen/rep21864/`.

**Do not judge anything for 21864.** No certificate exists yet.
