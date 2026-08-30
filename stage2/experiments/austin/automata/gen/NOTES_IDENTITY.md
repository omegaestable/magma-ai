# NOTES_IDENTITY — the identity laws of wave 3 agent 2 (9663/36487, 10222/35836, 12294)

## SUMMARY (read this first)

**Two of my three groups are misfiled.** `gen/SEMANTIC_TABLE.md` lists 9663/36487 (3 rows) and 12294
(1 row) as Track C IDENTITY LAWS. They are not: a ground congruence-closure search that finds the
published 12073/27859 identity (`a*a = b*b`) at size 3 and the 10222 identity at size 9 finds **zero**
junk-forgetting identities for them, over 689,386 / 2,209,526 congruence nodes. The `smallcheck`
semantic failures that put them in Track C come from `freemodel.Free`'s *reading search* being
incomplete, not from a forced identity. **The inference "semantic free model fails ⟹ the carrier must
change" is invalid**; the congruence test is the one that decides it, and it is 5 seconds per law
(`python gen/_id_query.py <eq> 3 2 2 5`).

| group | rows | forced identity | carrier | state |
| --- | --- | --- | --- | --- |
| 9663 / 36487 | 0018, 0051, 0098 | **none** | plain free terms `g n \| J u v` | **model REFUTED** — see the CORRECTION at the end of this file. Passed nine oracles, killed by the tenth (forced firing, law 40037). Free-term models are dead. **E-carrier build started** (`gen/_x9663_lab.py`, best variant T2/D1+R2) — see the last section. |
| 12294 | 0093 | **none** | plain free terms | one branch short (`gen/q12294b.py`); same obstruction as 9663 — same queue |
| 10222 / 35836 | 0005, 0095 | **`(a*a)*((a*a)*a) = (a*a)*((b*a)*a)`** (proved) | `g n \| J u v \| K u`, **unary** K | identity proved, carrier designed, not built |

**No certificate shipped, and no model survives.** Every model, probe and negative result below is reproducible from this
directory; the new tools are `gen/_id_cong.py`, `gen/_id_query.py`, `gen/_id_ask.py`,
`gen/_id_ask2.py`, `gen/_idc_lib.py`.


Rows: 0018 (9663:22818), 0051 (36487:17522), 0098 (36487:22818), 0005 (10222:20034),
0095 (35836:25964), 0093 (12294:41082).

## W3-1 harvest (2026-08-29) — nothing shippable

| file | bytes | sorries |
| --- | --- | --- |
| `gen/rec9663.lean`  | 31805 | 1 (`theorem law`) |
| `gen/rec36487.lean` | 31920 | 1 |
| `gen/rec10222.lean` | 83296 | 1 |
| `gen/rec35836.lean` | 12148 | 1 |
| `gen/rec12294.lean` | 15655 | 1 |

**No zero-sorry file, and none of them is worth finishing**: every one is generated from the *extracted
rule system* over the free `g/J` carrier, and all five laws fail SEMANTICALLY (`gen/SEMANTIC_TABLE.md`:
23/23/45/45/22 failures on one-generator terms of size <= 9). A `theorem law` for a false model cannot be
proved. Confirmed the classification rather than assuming it (below).

Also harvested: `gen/_x10222_identity.py` (a previous agent's **hand derivation of the forced identity for
10222**, all structural claims machine-checked) and `gen/_x10222_quot.py` (a first-draft carrier built on
it). The draft carrier **fails at size 2**: `x=K(g0) y=K(g0) z=g0 -> (K(g0)*((K(g0)*K(g0))*g0))`
(rule R1 `op(a, K a) = a` never fires because `v = K u` is checked, not `u = v`; and squares of `K` are
not handled). It is a sketch, not a model.

## The forced identities, found mechanically (`gen/_id_cong.py`, `gen/_id_query.py`)

New tool, written this session. Ground congruence closure over hash-consed free terms: assert
`RHS(x,y,z) ~ x` for every assignment from a growing pool, close under congruence, then report
**classes whose two smallest members are distinct free terms of the same size** — i.e. the law has
genuinely forgotten something. Every merge is a sound consequence of the law (a congruence
consequence of ground instances), so a hit is a proof; a miss is evidence, not a proof.

Validated on the two laws whose answer is already known (`PLAYBOOK_QUOTIENT.md` §2): it finds
`(a*a) == (b*b)` at size 3 for **12073** and **27859**, in round 2, unprompted. That is exactly the
published theorem ("all squares are equal"), so the tool is sensitive to the phenomenon.

Run `python gen/_id_query.py <eq> 3 2 2 5` (base pool size <= 3, 2 generators, 2 rounds).

| law | minimal junk-forgetting identity | count |
| --- | --- | --- |
| 12073 (control) | `(a*a) == (b*b)` | 5191 |
| 27859 (control) | `(a*a) == (b*b)` | 2801 |
| **10222** | **`(a*a)*((a*a)*a) == (a*a)*((b*a)*a)`** | 194 |
| **35836** (dual) | **`(a*(a*a))*(a*a) == (a*(a*b))*(a*a)`** | 194 |
| **9663** | **none** | **0** |
| **36487** (dual) | **none** | **0** |
| **12294** | **none** | **0** |

### Group 2 — 10222 / 35836: the forced identity, with the hand proof

`gen/_x10222_identity.py` (previous agent, structurally machine-checked; re-run and confirmed):

* **F1. `R_y` is injective.** `x = y ◇ ((x◇y) ◇ ((z◇y)◇y))` — the right-hand side mentions `x` only
  inside `x◇y`, so `x1◇y = x2◇y ⟹ x1 = x2`.
* `L(a,a,a)`: `a = a ◇ T` with `T := (a◇a)◇((a◇a)◇a)`.
* `L(a,a,b)`: `a = a ◇ S` with `S := (a◇a)◇((b◇a)◇a)`.
* `L(a,T,a)`: `a = T ◇ ((a◇T)◇((a◇T)◇T))`, and `a◇T = a`, so `a = T ◇ (a◇a)`.
* `L(a,S,a)` likewise: `a = S ◇ (a◇a)`.
* F1 at `y := a◇a` on the last two: **`T = S`**.

**So 10222 forces `(a◇a) ◇ ((z◇a)◇a)` to be independent of `z`.** Write `K a` for that value.
It is a **unary** constant (one per `a`), not a nullary one: `K a ◇ (a◇a) = a` pins `a` from `K a`, so
`K a = K a'` forces `a◇a = a'◇a'` and then `a = a'`. `K` is injective — the 12073/27859 nullary
tag `E` is structurally unavailable here.  (The carrier (c) precedent `gen/qz_m24.py` already uses a
unary code constructor `C m`, so unary is not the measured `K y` cascade of PLAYBOOK_QUOTIENT §2.)

### Groups 1 and 3 — 9663 / 36487 and 12294: **there is no forced identity**

Zero junk-forgetting merges at base pool <= 3 over 2 generators, 2 rounds (295,704 / 701,784 ground
instances, 689,386 / 2,209,526 congruence nodes) — while the same search finds the 12073/27859
identity at size 3 and the 10222 identity at size 9.

**This contradicts `gen/SEMANTIC_TABLE.md`, which files 9663/36487 (3 rows) and 12294 (1 row) as
IDENTITY LAWS (Track C) on the strength of `smallcheck` semantic failures alone.** The inference
"semantic free model fails ⟹ the law derives an identity between distinct free terms" is **not
valid**: `freemodel.Free` resolves a decode by *searching* for an assignment that produces the
observed value, and that search is incomplete (`rbail` / `rcycles` / `cuts` — it gives up on
readings that are not well-founded). A failure can therefore mean "the reading search lost the
payload", which is a decoder problem, not a carrier problem.

## Group 1 — 9663 / 36487: NOT a carrier problem. A one-rule free-term model.

Since there is no forced identity, the carrier stays `M ::= g n | J u v` and the only question is the
decoder. Law `x = y ◇ ((z◇y) ◇ (x◇(x◇y)))`: the code of `x` relative to `u` is `J A (J x P)` with
`P = op(x,u)` and `A` **any element of `im(R_u)`** — the `z◇y` slot is junk.

```
op u v =
  v = J A (J x P),  op x u = P,  inimg A u      ->  x
  otherwise                                     ->  J u v

inimg A u  :=  (A = J _ u)                 -- A is a free product ?*u
            v  (u = J _ (J A _))           -- A is u's own payload slot a1 (a2 u)
```
The nested call is `op x u` with `sz x < sz v`, so `msr = sz u + sz v` strictly decreases and the gate
`sz x + sz u < sz u + sz v` **holds unconditionally** (the 27859 property that made that file
induction-free — `LEMMA_LIBRARY.md` §4).

**Guard sweep** (`gen/_x9663_guards.py`, all one-generator free terms of size <= 11, 65 terms):

| guard for the A slot | failures |
| --- | --- |
| `wild` (no guard at all) | 3 — `op(g0, J g0 y)` decodes spuriously and corrupts the chain |
| `free`: `A = J _ u` only | 3 — dies when `op(z,y)` itself decodes |
| `freeprod`: `A = J _ u` and `op(A.1,u) = A` | 3 — same |
| **`pay`: `A = J _ u`  or  `A = a1 (a2 u)`** | **0 / 274,625** |
| `pay2` (`pay` plus a recompute of u's own code) | 0 / 274,625 |

`pay` is the weaker and cheaper of the two, and identical on the sweep: **use `pay`.**

Why `pay` is the right guard: `op(z,u)` is either free (`J z u`, the first disjunct) or it *decoded*, and
a decode of `op(z,u)` returns `a1 (a2 u)` — the payload slot of `u` — whatever `z` was. So `im(R_u)`
is exactly `{J z u} ∪ {a1 (a2 u)}`, and the second element is readable **off `u` alone**. This is the
existential decoder of `gen/P2_EXISTENTIAL_DECODER.md` **solved by projection**: the witness `z` is
forgotten but the *value* it produces is not, because every decode of a product with right argument `u`
returns the same subterm of `u`. That is the transferable idea.

### Validation of the 9663 `pay` model, and the hole the case tree found

| test | result |
| --- | --- |
| exhaustive, 1 generator, `x,y` size <= 13, `z` size <= 11 | **2,522,585 assignments, 0 failures** (32.9 s) |
| exhaustive, 2 generators, all of `x,y,z` size <= 7 | **1,061,208 assignments, 0 failures** |
| deep random (terms built with `op` itself), 5 seeds x 20,000, depth 5, 2 gens | 0 failures |
| **case tree** (`gen/_x9663_tree.py`, chained encoding, 183-term pool, 400,000 draws) | **cell `P1 Q1 A0 C0` fails 157/157** |

Rail 50 again, exactly: no sampler reaches that cell — it needs `y` to be the code of `w` w.r.t. `x`
**and** `w` to be the code of `Q` w.r.t. `x`, two chained encodings, and the smallest witness has size
23. The one-rule model is FALSE. Minimal witness, reconstructed by hand:

```
x  = g0
w2 = g1                       P2 = op(w2,x) = J g1 g0
w  = J (J g0 g0) (J g1 (J g1 g0))          -- w is the code of g1 w.r.t. g0
P1 = op(w,x) = J w g0
y  = J (J g0 g0) (J w (J w g0))            -- y is the code of w  w.r.t. g0
z  free
   op(x,y) = w (DEC),  op(x,w) = g1 (DEC),  so the chain needs  op(y, J A g1) = g0
```

A **strictly structural** variant (require `P = J x u`, so the rule has no recursive call at all,
`gen/_x9663_strict.py`) is strictly worse: it fails the size-13 one-generator sweep that `pay`
passes, and it fails cell `P1 Q0` entirely (2,057/2,057). Do not use it.

### The uniform statement of the decoder, and why the repair is a hierarchy

Both rules are instances of one existential:

> `op(u, J A Q) = x`   whenever   `inimg A u`   and   **`op x (op x u) = Q`**

which is just the law read backwards. The rules differ only in **where the witness `x` is read from**:
DEC reads it off `Q = J x P`; the level-2 rule reads it off `a2 (a1 u)` (the free junk slot of `u`'s own
code). When *that* slot is itself decoded, `x` is not readable and a level-3 witness source is needed.
This is the same "existential decoder" obstruction as `gen/P2_EXISTENTIAL_DECODER.md`, in its mildest
form: here the witness has *some* readable positions, so each level is repairable, but the hierarchy is
not obviously finite.

### The 9663 model that survives everything: THREE witness positions (`gen/q9663c.py`)

```
op u v =
  v = J A Q,  inimg A u,  and one of
     W1   Q = J x P                       and op x u = P                     -> x
     W2   x := a2 (a1 u)   and lvl2 u Q x                                    -> x
     W3   x := a2 (a2 (a2 u))  and lvl2 u Q x                                -> x
  otherwise                                                                  -> J u v

inimg A u  :=  (A = J _ u)  or  (u = J _ (J A _))

lvl2 u Q x :=  u = J _ (J w P1),  op w x = P1,          -- u is the code of w w.r.t. x
               w = J A2 (J Q P2), op Q x = P2, inimg A2 x   -- w is the code of Q w.r.t. x
```

W2 and W3 are the same rule with the witness read from the two positions where the payload `x` can
appear inside its own code `u = J A1 (J w P1)`: `A1 = J j x` (so `x = a2 (a1 u)`) or `P1 = J w x`
(so `x = a2 (a2 (a2 u))`).

**Termination is the 27859 property.** Every nested call has both arguments proper subterms of `u`
or of `v` (`op w x`, `op Q x`, `op x u` with `x = a1 Q`), so `sz(arg1) + sz(arg2) < sz u + sz v`
**unconditionally** — no gate ever has a side condition and no recursive result appears in a gate.
`msr u v = sz u + sz v`.

| test | q9663 (W1 only) | q9663b (W1+W2) | **q9663c (W1+W2+W3)** |
| --- | --- | --- | --- |
| exhaustive 1 gen, `x,y` <= 13, `z` <= 11 (2,522,585) | 0 | 0 | **0** |
| exhaustive 2 gens, all <= 7 (1,061,208) | 0 | 0 | **0** |
| deep random 5 x 20,000, depth 5, 2 gens | 0 | 0 | **0** |
| case tree, 400,000 draws, 5 reachable cells | 157 FAIL in `P1 Q1` | 0 | **0** |
| case tree, **1,500,000** draws, 6 reachable cells | — | — | **0** |
| level-3 constructed (junk slot of `x`'s own code decoded), 7,680 | — | **7,680 FAIL** | **0** |
| level-4 constructed (both witness positions decoded), 840 | — | — | **0** |

Level 4 is **not a hole**: the configuration is reachable (840 instances constructed) but only with
`Q` free, so W1 covers it. Probes: `gen/_x9663_tree.py`, `gen/_x9663_lvl3.py`, `gen/_x9663_lvl4.py`,
driver `gen/_x9663_run.py <model> exh|tree`.

### The general invariant for the Lean proof (W3-7)

`IMG (z u) : inimg (op z u) u` — **verified with 0 counterexamples over 49,213 pairs**
(`gen/_x9663_inv.py`; all one-generator terms of size <= 13, and all two-generator terms of size <= 7).
This is the analogue of 24200's `FREE` and 27859's `MAIN`: it discharges the `inimg A u` conjunct of the
root decode *unconditionally*, for whatever `A = op z y` turns out to be, so the law proof never has to
case-split on how `op z y` evaluated. Proof sketch: `op z u` is either `J z u` (disjunct 1 with the
witness `z`) or a decode, and every decode of a product whose right argument is `u` returns
`a1 (a2 u)` — disjunct 2 verbatim. One `TR`-style digest lemma plus that observation.

## Group 3 — 12294: same shape, one witness level short

`gen/q12294.py`, law `x = y ◇ (((z◇y)◇x) ◇ (x◇y))`. Code of `x` w.r.t. `u` is `C = J D P` with
`D = op (op z u) x` (the junk slot) and `P = op x u`; the decode reads the witness off `D = J A x`,
so `decoded_val u = a2 (a1 u)` and

```
inimg A u := (A = J _ u) or (A = a2 (a1 u))
op u v =
   v = J D P,  D = J A x,  inimg A u,  and
      W1  P = J x u  and op x u = P                                  -> x
      W2  u = J (J A1 w) (J w x),  op w x = a2 u,  inimg A1 x,
          and P = w                                                  -> x
   otherwise                                                         -> J u v
```

| test | W1 only | **W1 + W2** |
| --- | --- | --- |
| exhaustive 2 generators, all of `x,y,z` size <= 7 | 0 / 1,061,208 | **0 / 1,061,208** |
| exhaustive 1 generator, size <= 13 / z <= 11 | fails after 729 | fails after **217,884** |

The residual 1-generator failure is the *same* chain-decode cell and wants the **third witness
position**, exactly as 9663 did (`gen/q9663c.py`'s W3). Smallest witness:
`x = ((g0*g0)*g0)*(g0*g0)`, `y = (g0*g0)*g0`, any `z` — `op x y` decodes through W2 and the chain
loses the code. **This is the next 30 minutes of work on this law, and 9663's W3 is the template.**

## Group 2 — 10222 / 35836: the carrier, designed but not built

Unlike the other two, this one *does* need a new constructor, because `T = S` is proved. Carrier

```
M ::= g n | J u v | K u                        -- K u is the value of (u◇u) ◇ ((z◇u)◇u), all z
```

with the identities the derivation of §"Group 2" supplies as **rules**:

```
R1  op (J w w) (J A w) = K w        when inimg A w            -- the identified family, T and S both
R2  op w (K w) = w                                            -- from  a ◇ T = a
R3  op (K w) (J w w) = w                                      -- from  a = T ◇ (a◇a)
R4  op u (J P B) = x   when P = J x u, op x u = P, inimg2 B u -- the decoder
R5  otherwise J u v
inimg  A u := (A = J _ u) or (A = a1 (a1 u))          -- the 10222 decode returns a1 (a1 v)
inimg2 B u := (B = J A u and inimg A u) or (B = a1 (a1 u))     -- B = op (op z u) u, two R_u's
```

`K` must be **unary**: `op (K a) (J a a) = a` recovers `a` from `K a`, so `K` is injective and the
nullary `E` of 12073/27859/34889 is unavailable (proved in §"Group 2"). This is the `qz_m24.py`
shape (`C m`, a unary code constructor), not the measured `K y` cascade of `PLAYBOOK_QUOTIENT.md` §2.
The junk slot does **not** collapse in general — `gen/_id_ask2.py` shows the code is `z`-independent
only on the diagonal `x = y` (`DERIVED` for `((a*a)*((c*a)*a))`, not derived for `((a*b)*((c*b)*b))`) —
so R4's `inimg2` decoder is needed *on top of* the quotient. **Not built or validated. Highest
remaining risk of the three groups; do 12294's W3 first.**

## Status and what to do next

| rows | law | state |
| --- | --- | --- |
| 0018, 0051, 0098 | 9663 / 36487 | **model complete and validated to the wave-3 standard** (`gen/q9663c.py`). Next: Lean. |
| 0093 | 12294 | model one witness short (`gen/q12294.py`); add W3 by analogy, ~30 min |
| 0005, 0095 | 10222 / 35836 | identity proved, carrier designed (above), not built |

**Lean plan for 9663** (the file to write, following `gen/nf27859p.lean` and `LEMMA_LIBRARY.md`):
carrier `M ::= g Nat | J M M`, `sz`, `tg`, `a1`, `a2`; `op` with `termination_by sz u + sz v` and
`decreasing_by` discharged by `sz_a1`/`sz_a2`/`sz_pos` + `omega` — **every gate is unconditional**, so
there is no fuel induction and no `CMP` (the 27859 property, `LEMMA_LIBRARY.md` §4). Then
`op_cases` (`⟨_,_,rfl,rfl,op.eq_1 u v⟩`), one `TR` digest for the whole `if`-chain, `FR` from it,
`IMG (z u) : inimg (op z u) u` as the single general invariant, and `theorem law` as: the chain
products are free or decoded; in every case the root fires W1, W2 or W3 with `op x u = P` **`rfl`**
(P *is* the chain's first product) and `IMG` supplying `inimg A u`. Note `inimg` is purely structural
(no recursive call), so `TR` mentions it as data, not as a recursive obligation.
Use the `Z` combinator from `certs/research_order5_hard_0001.lean` rather than `split` (>10 rules
exceeds the tactic step limit). Dual rows: prove the L-form 9663, then `dualcert.py` to 36487's rows.

### 12294 update — the one-rule form (`gen/q12294b.py`) is the right shape

The witness for 12294 sits in the `D` slot (`D = J A x`), which is **independent of `P`**, so it stays
readable even when `P = op x u` decodes. Replacing W1's *structural* guard `P = J x u` with the
*semantic* guard `op x u = P` therefore collapses W1+W2 into ONE rule:

```
op u v =  a2 D    when  v = J D P,  D = J A x,  inimg A u,  op (a2 D) u = P
       =  J u v   otherwise
```
The nested call has `x = a2 (a1 v)`, a proper subterm of `v`, so the gate is again unconditional.

| model | exh 1 gen <= 9 | exh 1 gen <= 15 (z <= 11) | exh 2 gens <= 7 |
| --- | --- | --- | --- |
| `q12294.py` (W1+W2, structural) | fails at 9,066 | fails at 217,884 | 0 / 1,061,208 |
| **`q12294b.py` (one rule, semantic)** | **0 / 12,167** | fails at 694,204 (4 cases) | **0 / 1,061,208** |

Residual failure of `q12294b`, smallest: `x = y = ((g0*g0)*g0)*(g0*g0)`, `z = g0` (the diagonal
`x = y`), and `x = (g0*g0)*g0`, `y = (g0*(((g0*g0)*g0)*(g0*g0)))*g0`, `z = (g0*g0)*g0`. Four cases in
694,204 — a single missing branch, not a wrong carrier. **Try the same semantic-guard simplification
on 9663 before adding rules there** (9663's witness lives inside `Q`, the slot that decodes, so it is
not automatic — but if it works, 9663 drops from three rules to one).

---

# CORRECTION (same session, after the coordinator's oracle list): **q9663c IS FALSE**

I claimed above that `gen/q9663c.py` was "model complete and validated to the wave-3 standard".
**That claim is withdrawn.** Two further oracles from `gen/LEMMA_LIBRARY.md` were run afterwards; the
first passed and the second refuted the model.

## 1. The level-k descent (LEMMA_LIBRARY, law 12087) — PASSED

`gen/_x9663_deep3.py`: nested encodings `p_i = enc(x, p_{i+1}, j)`, `y = enc(x, p_1, j)`, so the same
rule descends k levels in the same argument; both `inimg` flavours for the junk slot `A` (free
`J j u`, and decoded `a1 (a2 u)`); junk drawn from a **large**-term pool as well as a small one
(the 17286 refutation shape).

| model | depths 0-3, 2 flavours, 2 junk pools, 2 seeds x 400 |
| --- | --- |
| `q9663c` (W1+W2+W3) | **TOTAL BAD 0** (12,800 constructed instances) |
| `q9663b` (W1+W2 with the semantic guard) | **1,558 BAD** — the oracle is sensitive |

## 2. The forced-firing oracle (LEMMA_LIBRARY, law 40037) — **REFUTES q9663c AND q9663d**

> *a generated rule whose precondition constrains only one argument can fire at a **different product
> of the law's chain** than the one it was extracted for.*

W2 and W3 were built for the **root** product `op y C`. I instrumented which rule fires where
(`gen/_x9663_img.py`): on the level-3 instances the root fires **W3 1536/1536**, and `op z y` fires
only `free`/`W1` — and across every pool tested (exhaustive, deep-encoding, level-3; ~932,000 pairs)
W2/W3 fire at `op z y` **zero** times. That is exactly the situation rail 40037 warns about, so I
constructed the instance instead of sampling for it.

`gen/_x9663_force.py` builds `z` with the `_lvl2` shape and `m = J (J j z) Q` with `a2 m = Q`, which
forces W2 at `op z m`; `gen/_x9663_force3.py` does the same for W3.

| model | forced pairs | rule at `op z m` | **IMG counterexamples** | **law failures** |
| --- | --- | --- | --- | --- |
| `q9663c` (W1+W2+W3) | 120 | W2 120/120 | **96** | **384** |
| `q9663d` (W1+W3, W2 dropped) | 1,260 | W3 1260/1260 | **1,008** | **4,032 of 5,040** |

Smallest law failure for `q9663d`:
```
x = g0
y = ((g0*(g0*(((g0*g0)*(g0*(g0*g0)))*(((g0*g0)*(g0*(g0*g0)))*g0))))*g0)
z =  (g0*(((g0*g0)*(g0*(g0*g0)))*(((g0*g0)*(g0*(g0*g0)))*g0)))
```
`q9663d` (W1+W3) passes *everything else* — 2,522,585 + 1,061,208 exhaustive, the case tree, level-3,
level-4 and the whole level-k descent — and is still false. **Nine oracles were not enough; the tenth
was.**

## 3. Why this is structural, not a missing rule — the real obstruction

The decoder guard is `inimg A u`, a **structural under-approximation of `im(R_u)`**, and the law proof
needs it to be closed under the operation:

```
IMG (z u) :  inimg (op z u) u
```

`IMG` is what the root decode consumes (`A = op z y`) and it is the only general invariant the proof
needs (W3-7). But **every witness rule added to make the root decode also enlarges `im(R_u)`**: W2
returns `a2 (a1 z)` and W3 returns `a2 (a2 (a2 z))` — *subterms of the **first** argument*, about which
`inimg A u` (a predicate on `A` and `u = the second argument`) has no structural handle at all. So each
new rule breaks `IMG`, and repairing `IMG` needs a wider `inimg`, which widens the decoder, which adds
more values to `im(R_u)`. **The fixed point of that loop is the existential decoder**
(`gen/P2_EXISTENTIAL_DECODER.md`) — 9663's junk slot `z◇y` ranges over `im(R_y)`, and no structural
predicate can name that set once the decoder is strong enough to decode the chain.

This is the same obstruction as 21865 / 21866 / 22591, reached from the other side: those laws fail
because two readings collide, 9663 fails because the *witness set* is not structurally definable.
**9663/36487 (3 rows) and 12294 (1 row) belong in the existential-decoder queue with them**, which
raises that piece of mathematics from 11 rows to **15**.

## 4. What is still solid, and what to do next

* The congruence result stands and is independent of all of this: **9663, 36487 and 12294 force no
  identity**, so when the existential decoder exists, their carrier is plain free terms — no quotient,
  no new constructor. That is a real simplification for whoever builds it.
* 10222/35836's forced identity `(a*a)*((a*a)*a) = (a*a)*((b*a)*a)` and the unary-`K` argument stand.
  10222 needs **both** the quotient and the decoder, so it is the hardest of my three, as reported.
* **Run `gen/_x9663_force.py`'s construction shape on every model in this family before Lean.** It is
  the only oracle here that refuted a model which had passed the other nine, and it is cheap: for each
  rule, take its own precondition, build a term satisfying it, and place that term at *every other*
  product of the law's chain — not only at the product the rule was extracted for.
* Do **not** write Lean for `q9663c` or `q9663d`.

---

# 9663 E-CARRIER (the 13764 move) — built, best variant measured, NOT yet correct

`gen/_x9663_lab.py` — a self-contained lab in the `gen/_w3_12087_lab.py` shape: **L1 exhaustive +
3 deep seeds + the level-k descent at levels 0-3 with both junk pools, with the cell census printed
beside every failure count** (the vacuity check), in ~10 s per variant. Parametrised on the command
line so a whole design can be swept in one loop:

```
python gen/_x9663_lab.py <T1|T2|T3> <D1|D2> [noR2]
```

Carrier `M ::= g n | J a b | E a b`, `tg` 1/2/3, `a1`/`a2` total. **Every shape test is `tg t ≠ 1`
or an explicit `= 3`, never `tg t = 2` where a `J` is meant** (coordinator rail 1).

## Why the tag is the right move here — it deletes the obstruction I reported

The refutation above was entirely about `inimg A u`, the guard on the **junk slot** `A = z◇y`. With a
tag the root does not guess membership of `im(R_y)` at all: the code is recognised by its
*constructor*, which only the model can produce, so **the junk slot needs no guard whatsoever**. The
`IMG` fixed-point loop simply does not arise. That is the structural payoff of the 13764 carrier and
it is why this is the right direction.

## The design

```
TAG  T1  tg v ≠ 1 ∧ a1 v = u ∧ op u (a2 v) = v        -- (u,v) is an (x,P) pair, re-run certified
     T2  tg v ≠ 1                                      -- tag every product-valued v
     T3  tg v ≠ 1 ∧ a1 v = u                           -- structural only
         ->  E u v
DEC  D1  tg v ≠ 1 ∧ tg (a2 v) = 3 ∧ op (a1 (a2 v)) u = a2 (a2 v)   ->  a1 (a2 v)
     D2  same with tg (a2 v) ≠ 1
R2       tg u ≠ 1 ∧ tg (a2 u) = 3 ∧ tg (a2 (a2 u)) = 3,  p := a1 (a2 u),  x := a2 (a2 (a2 u)),
         op p x = a2 (a2 u)  ∧  op x p = a2 v          ->  x     -- payload read out of u
else J u v
```
On the law's chain `P = x◇y ; Q = x◇P ; A = z◇y ; C = A◇Q ; R = y◇C`, the intended run is
`P` tagged, `Q = E x P`, `C = E A Q`, and the root fires DEC with its guard `op x y = P` **`rfl`**.
**Every recursive argument in DEC and R2 is a proper subterm of `u` or of `v`**, so the Lean gate on
`sz u + sz v` is unconditional — the 27859 shape, no `msr`, no fuel induction.

## Measured (all six TAG x DEC variants, with and without R2)

| variant | L1 exh 405,224 | deep 3x20,000 | descent lv 0/1/2/3 | TOTAL BAD |
| --- | --- | --- | --- | --- |
| T1 D1 | 296 | 2 | 286/300/300/300 | 2684 |
| T1 D2 | 592 | 4 | 0/299/300/300 | 2401 |
| T2 D1 (no R2) | 296 | 2 | 99/299/300/300 | 2302 |
| **T2 D1 + R2** | **296** | **2** | **30/103/89/120** | **990** |
| T2 D2 + R2 | 592 | 4 | 0/103/89/120 | 1227 |
| T3 D1/D2 | 296/592 | 2/4 | 282/300/… | 2670/2401 |

**R2 is right and load-bearing**: at descent level 1 the cells `D,D,T,T,R` (129) and `D,D,T,F,R` (65)
are **194 instances where R2 fires and the law holds** — 0 bad. The 103 failures are the cells where
R2's guard did not match and the root fell through to TAG (`…,T` profiles). That is the 13764
v11→v14 pattern: the payload-out-of-`u` rule needs its remaining reading positions.

## The two diagnosed cells (this is the next iteration's work)

**(a) L1, one cell only, `T,D,T,F,T`, 292 of 296** — `E` is overloaded. Smallest witness:
```
x = g0,  y = E g0 (J g0 g0),  z = g0
P = op x y = E g0 y            (TAG)
Q = op x P = g0                (DEC fires: a2 P = y is a tag and op (a1 y) x = a2 y  -- correct by the
                                law, but it destroys the chain)
C = J A g0 ;  root has tg (a2 C) = 1, nothing fires  ->  E y C   ≠ x
```
`E` marks both "this is the `(x,P)` pair marker" and "this is the code container", and DEC cannot tell
them apart. **The fix is a fourth constructor** (`M ::= g | J | E | F`, `F` for the code container) so
that DEC tests `tg (a2 v) = 4` and can never fire on a `P`-marker. 13764 needed exactly two
constructors because its law re-reads one product; 9663's chain re-reads two (`P` and `Q`), so it
needs three.

**(b) descent levels 1-3, cells `D,D,·,·,T`** — the payload has to be read out of `u` from a position
R2 does not cover. R2 reads `a2 (a2 (a2 u))`; the L1-adjacent case wants `a2 (a2 u)`. I added that as
`R3` with an unconditional-gate certification (`op p x = a2 u`, both arguments proper subterms of `u`)
and its guard `a2 v = a1 u` is too strong — it fires 4 times and never in the cell that needs it.
**Enumerate the positions from the cell census, do not guess them**: run
`gen/_x9663_min.py T2 D1` (prints every failing cell with the full chain `P,Q,A,C,R` for the smallest
witnesses) and read the required reading off each.

## Status

Not correct yet, and I am not writing Lean for it. What is in hand: the lab, the six-variant sweep,
the two cells with witnesses, and the confirmation that the tag removes the `inimg` obstruction
entirely (the junk slot is unguarded in every variant above and no failure involves it). Estimated
one to three more iterations of the 13764 kind. The same carrier then transfers to **12294** (0093),
whose chain has the same two-re-read shape.

---

# 9663 FOUR-CONSTRUCTOR CARRIER — `gen/_x9663_lab4.py` (current best, still not correct)

**Count the products the law re-reads.** 13764 re-reads one and needs two constructors. 9663's chain
re-reads **two** (`P` and `Q`), so a single tag is overloaded — it marks both the `(x,P)` pair marker
and the code container, and DEC cannot tell them apart. That was 292 of the 296 L1 failures of the
3-constructor lab (cell `T,D,T,F,T`).

```
M ::= g n | J a b | E a b | F a b        tg 1/2/3/4;  a1/a2 total.
E = the (x,P) pair marker ;  F = the CODE CONTAINER the root reads.

DEC   tg v ≠ 1, tg (a2 v) = 4, op (a1 (a2 v)) u = a2 (a2 v)   ->  a1 (a2 v)
DEC2  tg v ≠ 1, tg (a2 v) = 2, op (a1 (a2 v)) u = a2 (a2 v)   ->  a1 (a2 v)   -- untagged container
R2    tg u ≠ 1, tg (a2 u) ≥ 3, tg (a2 (a2 u)) ≥ 3,  p := a1 (a2 u), x := a2 (a2 (a2 u)),
      op p x = a2 (a2 u) ∧ op x p = a2 v                      ->  x           -- payload out of u
TAGF  tg v ≠ 1, a1 v = u, op u (a2 v) = v                     ->  F u v
TAGE  tg v ≠ 1                                                ->  E u v
else                                                           ->  J u v
```

**`TAGF` must fire on `J`-products too, not only on tagged ones** — with `tg v ≥ 3` the base case
`x = y = z = g0` fails, because `P = op g0 g0 = J g0 g0` is untagged and `Q` never becomes an `F`.
That single character was 50,560 → 632 L1 failures. It is also what un-overloads `E`: the
recomputation `op u (a2 v) = v` distinguishes an `E` node from an `F` node with no extra test,
because `op` only ever produces one of them for a given `(u, a2 v)`.

**Every recursive argument is a proper subterm of `v` (DEC/DEC2: `a1 (a2 v)`; TAGF: `a2 v`) or of `u`
(R2), so the gate `sz(arg1) + sz(arg2) < sz u + sz v` is UNCONDITIONAL** — the 27859 shape, measure
`sz u + sz v`, no `msr`, no fuel induction. That property has survived every iteration.

## Measured (`gen/_x9663_fast.py`, the ranking harness — H3 first, ~40 s)

| oracle | 3-constructor best (T2/D1+R2) | 4-ctor | 4-ctor **+DEC2** |
| --- | --- | --- | --- |
| L1 exhaustive size <= 3, 2 gens | 0 | 0 | **0** |
| L1 exhaustive size <= 5, 2 gens (3,944,312 chains) | 296/405,224 | 632 | (not re-run) |
| deep 2 x 8,000 | 2 | 1 | **1** |
| **H3 (`y = enc(j,w,x)`, y a genuine encoding BY x) 2 x 8,000** | — | 255 / 250 | **164 / 176** |
| descent lv 0 / 1 / 2 / 3 (300 each) | 30/103/89/120 | 110/122/122/127 | **57/122/122/127** |
| TOTAL (fast harness) | — | 1468 | **1197** |

**H3 is the ranking oracle, exactly as you said.** It fails 2.1% where `deep` fails 0.01% — a
170x separation on the same carrier — and it is what named the DEC2 cell. `deep` would have ranked
this carrier as essentially clean.

**`R4` was vacuous and is deleted.** A fourth rule reading `x := a1 u`, certified by re-running
`op x (op x u) = a2 v`, gave **identical fail counts on every oracle, with and without it** — your
rail: two versions with the same counts differ by a guard that certifies nothing. Removing it saves a
Lean case and ~900 B.

## The next reading, read off the census (do not infer it)

`gen/_x9663_h3.py` prints the H3 cells with the full chain. Dominant remaining cells are
`D,E,E,E,E` (213/358) and `D,.,E,E,E` (111/358) — `P = op x y` **decoded**, so the chain starts from
the payload rather than from `y`. Smallest witness:

```
x = g2 ,  y = E (J g2 g2) (F g2 (J g2 g2)) ,  z = g1
P = op x y = g2   (DEC: a2 y is an F-container and op (a1 (a2 y)) x = a2 (a2 y))
Q = op x P = J g2 g2 ;  C = E A Q ;  root: tg (a2 C) = 2 -> DEC2 now closes this one.
```
DEC2 was derived from exactly this cell and took H3 from 255 to 164. Repeat the loop on the
`D,E,E,E,E` cell — `run gen/_x9663_h3.py`, read where `x` sits in `u` and in `v` for the smallest
witness, and add that reading with a subterm-only certification so the gate stays unconditional.

## Status

Not correct; no Lean written. One to two more census-driven readings on the trajectory
1468 → 1197 → …, all of them one-line additions to `gen/_x9663_lab4.py`. When it reaches 0 on the
fast harness, re-run the full `_x9663_lab4.py` (3.9M-chain L1 + 3 deep seeds + H3 + the full descent
grid) before any Lean, and use `refine (if_pos ?_).trans rfl` for the gates (~912 B per cell).
The same carrier then transfers to **12294** (row 0093), whose chain has the same two-re-read shape.

---

# 9663 FOUR-CONSTRUCTOR CARRIER — driven to 0 on the fast harness. FOUR RULES.

`gen/_x9663_lab4.py`. Trajectory on `gen/_x9663_fast.py` (H3 first, ~40 s):
**1468 → 1197 → 743 → 1 → 0**, each step a one-line change read off the failing-cell census.

```
M ::= g n | J a b | E a b | F a b        tg 1/2/3/4 ;  a1/a2 total
op u v =
  DEC   tg v ≠ 1, tg (a2 v) = 4, op (a1 (a2 v)) u = a2 (a2 v)        ->  a1 (a2 v)
  R2    tg u ≠ 1, tg (a2 u) ≠ 1, tg (a2 (a2 u)) ≠ 1,
        p := a1 (a2 u),  x := a2 (a2 (a2 u)),
        op p x = a2 (a2 u)  ∧  op x p = a2 v                          ->  x
  TAGF  tg v ≠ 1, a1 v = u, op u (a2 v) = v                           ->  F u v
  TAGE  tg v ≠ 1                                                      ->  E u v
  else                                                                ->  J u v
```
`E` is the `(x,P)` pair marker; `F` is the code container the root reads. **Every recursive argument
is a proper subterm of `u` or of `v`** (`a1 (a2 v)`, `a2 v`, and R2's `p`,`x` inside `u`), so the gate
`sz(arg1) + sz(arg2) < sz u + sz v` is **unconditional** — the 27859 shape, measure `sz u + sz v`,
no `msr`, no fuel induction. That property survived all seven iterations.

## The three changes that did it, and the rail each one is

1. **`TAGF` on `tg v ≠ 1`, not `tg v ≥ 3`** — 50,560 → 632 L1 failures from one character.
   *A tag rule fires on whatever the chain actually produces at that position, and at the base case
   `x = y = z = g0` that is a plain `J`.* It also un-overloads the constructors for free: the
   recomputation `op u (a2 v) = v` already separates `E` from `F`, because `op` produces only one of
   them for a given `(u, a2 v)`.
2. **`R2` gated on `tg ≠ 1`, not `tg ≥ 3`** — the same rail one level down. This is what took
   descent levels 1–3 from 122/122/127 to 0, and H3 from 164 to 0.
3. **`DEC` keeps `tg (a2 v) = 4` as its ANCHOR.** I first unified DEC over the container's
   constructor (H3 255 → 164 → 0); that removed the anchor, a junk `F` node then forged a container
   by a *genuinely satisfied* relation (law 12087's finding exactly), and I patched it with a second
   anchor `op (a1 Q) (a2 Q) = Q`. With change 2 in place **both are vacuous** — identical counts with
   and without, on every oracle — so both were deleted. Net: one DEC branch, anchored by the tag.

## Two rules measured and DELETED for vacuity (your rail 2, twice)

* **R4** (`x := a1 u`, re-run certified): identical fail counts on every oracle, with and without.
* **R5** (`x := a2 v`, gated `a1 u = x ∧ op x x = a2 u`): tried unanchored and with the anchor
  `op (a1 u) (a2 u) = u`; the anchor is itself vacuous (identical counts), and R5 is **net negative** —
  it fixes 1 of the 2 open TAGF2 failures and creates **5 new ones** in the TAGF arm.

## Final measurements

| oracle | result |
| --- | --- |
| L1 exhaustive size <= 3, 2 gens | **0 / 2,744** |
| **H3** (`y = enc(j,w,x)`, a genuine encoding BY x), 2 seeds | **0 / 16,000** |
| deep random, depth 5, 3 gens, 2 seeds | **0 / 16,000** |
| descent lv 0/1/2/3 x {small,large} junk | **0 / 2,400** |
| deep random 30,000, seed 5 | **0** |
| **forcing suite** (`gen/_x9663_force4.py`) | DEC 0/4000, R2 0/6000, TAGF 0/4000, TAGE 0/2452, **TAGF2 2/4000** |

**The forcing suite is non-vacuous**: DEC fired in 4000/4000 of its arm, R2 in 6000/6000, TAGF and
TAGE likewise — a suite that never fires rule k tests nothing about it, and this one fires all four.
**Descent saturation checked**: profiles per level are 7/4/2/4/2 at lv 0–4, so lv 2 and 4 *are*
saturating (`D,D,E,E,R` at 379/400 and 374/400) — those levels measure little, and lv 0/1/3 are the
informative ones.

## The one open cell — this is the exact remaining goal

Found only by the **TAGF2 arm** of the forcing suite (2 in 4,000) and by deep random at 3 in 20,000;
the fast harness never reaches it.

```
x = g2 ,  y = F (g2) (J g2 g2) ,  z any
P = op x y = F x y            (TAGF)
Q = op x P = g2 = x           (DEC: a2 P = y is an F container with op (a1 y) x = a2 y)
C = op A Q = J A g2           (tg g2 = 1, so C is a plain J)
root: tg (a2 C) = 1  -> DEC cannot fire; R2's second level a2 (a2 u) = g2 is a generator -> no rule.
```
Family: `y = F p (J p x)` — a genuine `F` node whose payload makes `Q` decode back to `x` **itself**,
so the container in `v` is the bare payload. The reading is `x = a2 v` and `x = a1 u`, and the
certification `op x x = a2 u` is subterm-only, i.e. R5 — but R5 must be gated so it cannot fire at
the `Q = op x P` position, which is where its 5 TAGF regressions come from. **That gate is the whole
of the remaining work.** Reproduce with `python gen/_x9663_force4.py` (the `BAD[TAGF2]` line).

## Status

Four rules, unconditional gates, 0 on every oracle except one cell reachable only by construction.
No Lean written — the model is not yet correct and rail 50 applies. When the TAGF2 cell closes,
re-run `gen/_x9663_lab4.py` in full (3.9M-chain L1 + 3 deep seeds + 2 H3 seeds + the descent grid)
and `gen/_x9663_force4.py`, then Lean with `refine (if_pos ?_).trans rfl` for the gates. The carrier
then transfers to **12294** (row 0093), same two-re-read shape — four rows behind one build.

### R5 closing note — four forms, all with IDENTICAL counts

The open TAGF2 cell wants a rule reading `x := a2 v`. I tried it in four forms:

| form | fast | forcing TAGF | forcing TAGF2 |
| --- | --- | --- | --- |
| unanchored (`a1 u = x ∧ op x x = a2 u`) | 1 | 5 | 1 |
| + anchor `op (a1 u) (a2 u) = u` | 0 | 5 | 1 |
| + gate "`op x u` is the marker over `(x,u)`" | 1 | 5 | 1 |
| + the TRUE certification `op x (op x u) = a2 v` | 0 | 5 | 1 |
| **absent** | **0** | **0** | **2** |

**All four give identical forcing counts** — R5's firing set is invariant under every guard, so the
problem is its **position**, not its guard: it fires at the `Q = op x P` slot (cell `.,S,.,.,E`)
where the correct behaviour is TAGE, and there is no local conjunct separating the root from that
slot. Net negative in every form. **Do not re-try R5 without a root-vs-Q separator** — that separator
is the remaining piece of mathematics, and it is one cell wide.
