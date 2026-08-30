# LEMMA_LIBRARY — the reusable Lean invariants, from the laws that shipped

**Read this file before `DEEP_SESSION_8_AUSTIN_HANDOVER.md`.** It grew from four Lean lemmas to the whole
method of the session; the handover has the score and the per-law state, this has how to do the work.

## Where to start, by what you are doing

| you are… | read |
| --- | --- |
| **about to trust a model** | "THE ORACLE LADDER" below — twelve rungs, and **seven models this session passed ~10^6 chains and were false** |
| **building a carrier** | "THE RECURSIVE-DECODER CARRIER", then the E-carrier rails (§ 12087, 12234, 11081), then "H3" |
| **writing Lean** | §§ 1-4 (`FD`, `ND1`, `mx`, the `TR` digest), then `mxl`, `Y`, and "the gate mechanic that folds every previous one together" |
| **fighting the byte cap** | "the digest compresses a rule SET; only a different CARRIER compresses a DEFINITION BLOCK", then `Z`/`Y` |
| **deciding a law's track** | "why 'add another rule' does not converge", "ruling out a quotient needs a POSITIVE CONTROL", and the banner on `gen/SEMANTIC_TABLE.md` |

## THE ORACLE LADDER — every rung was forced by a model that passed the previous one

1. `rv.run_tests(law, rules, [3,4,5], 3000, 12000)`
2. `cf.deep_tests` at 20,000 on >= 3 seeds
3. the case tree — each chain product decodes once (`gen/_x38565_dd.py`)
4. the both-decoded census — two decode at once
5. `qz_lib.identity_probe`
6. **the level-k descent, both tower variants, with the cell census printed** (`gen/_w3_12087_deep3.py`)
7. **vary the junk variable** — a large term over fresh generators in whichever slot no rule constrains
8. **forced firing** — construct each rule firing at every *other* chain product (`gen/_x9663_force.py`)
9. **H3** — build `y = enc(j, w, x)` so `y` is a genuine encoding *by x*. ~1,100x the kill power per chain
10. **per-branch, per-construction firing counts** — a branch at ~0 firings is untested, not unneeded
11. **the forcing suite's own positive control** — the census must show rule k fired, or nothing about k was tested
12. **every construction ported from the previous carrier's oracle** — a new carrier inherits the old one's adversary

And two things that are **not** evidence: `_orch_minim.py`'s `status: "ok"` (its keep-set is "fires under the
fuzz battery", so its bulk drop is unsound), and any count printed by a counter placed before the loop that
fills it.

---

Written 2026-08-29 (deep session 8) by the orchestrator, from the agents that finished. Every lemma below
is in a **judge-accepted** certificate. `PLAYBOOK_PROOF.md` §4.1 lists six partial proofs stuck on "one
shape"; these four lemmas are that shape, and three of them avoid the fuel induction §4 tells you to write.

**Read this before writing any case analysis** (W3-7). Three of the four laws that shipped today did so by
proving one general invariant instead of a chain of special cases.

---

## 1. `FD` — freeness bounded by `a1`, not by the whole term  (law 34889, 3 rows)

```lean
FD (n) : ∀ u a, sz a ≤ n → sz a < sz (a1 u) → op u a = J u a
```

Fuel induction on `n`, twelve lines, used four times in its certificate.

**The point is the hypothesis.** It is `sz a < sz (a1 u)`, *not* `sz a < sz u`, and that is what makes it
strong enough to kill two different decode branches at once:

* it kills a SELF-shaped rule for free, because that rule needs `a1 u = a1 a` while `sz (a1 a) < sz a < sz (a1 u)`;
* the induction hypothesis kills a DEC-shaped rule, because the rule's witness `b' = J u a'` is *bigger*
  than `u` and yet has to sit inside `a`.

If you have a decode branch whose result lives **inside** one of the arguments, this is the lemma.
Source: `gen/NOTES_34889.md`, certificate `gen/q34889_a.lean`.

## 2. `ND1` — the size analogue of freeness  (law 12073, 2 rows)

```lean
ND (n) : ∀ u v, sz v ≤ n → sz u ≤ sz (op u v) + sz v        -- ND1 = the unbounded corollary
```

Its agent: *"discharges the R1 blocker at the top product in one line for every case"*, and it is what
refutes every "y equals a term containing `op y x`" coincidence. Where `FD` says a product is free, `ND1`
says a product cannot have shrunk too far — which is the form you want when the coincidence to refute is an
equation rather than a rule firing. Source: `gen/NOTES_12073.md`.

## 3. `mx` — read the gate, do not induct  (law 32281)

```lean
mx {a b u v} (h : msr a b < msr u v) : max (sz a) (sz b) ≤ max (sz u) (sz v)
```

Proved as the converse of `msr_lt_of_max_lt` by `apply Classical.byContradiction; intro h` (`by_contra` is
Mathlib and banned).

**Why it matters, and it is the most transferable idea here: a recursive rule's own gate bounds its result.**
32281's `RS (u v) : op u v = J u v ∨ sz (op u v) < sz v` was expected to need `PLAYBOOK_PROOF.md` §4's
`CMP`/fuel induction, because the rule's result is `op u q` rather than a subterm of `v`. It does not. The
rule's disjunct carries a *second* gate `msr u X < msr u v`; `mx` turns that gate into a size fact, and two
`by_cases` on freeness close it.

**Before you reach for §4's fuel induction, check whether the rule you are fighting carries its own gate.**
Every msr-gated nested call in these models does.

## 4. `TR` / `SND` — one digest lemma for the whole `if`-chain  (laws 27859, 34889, 17286, 32281)

```lean
TR (u v) : op u v = J u v ∨ <rule 1 fired, with its guards and its result> ∨ <rule 2 ...> ∨ ...
```

Every law that shipped today states the **entire** `op` unfolding as one disjunction and proves it with one
`split` per branch (or none — see below). Nothing else in the file touches `op.eq_1`.

Consequences worth copying:

* **Law 27859 has no induction anywhere in its file** — its two recursion gates follow from `tg u = 2 ∧ v = K`
  alone and neither mentions a recursive result, so `TR` is the whole story. 9,108 B, first compile, two
  judge calls. If your gates are unconditional, check for this before writing anything harder.
* **State a recursive rule existentially.** 32281 writes its recursive branch as
  `∨ (tg v = 2 ∧ ∃ q, msr u q < msr u v ∧ op u v = op u q ∧ …)`; the `∃ q` form makes the rule statable in
  four lines instead of unfolding the whole `p4..p11` chain.
* **Factor the shared conjunct.** When several rules share a precondition, one lemma covers everything that
  fails it: 34889's `WF : ¬(tg v = 2 ∧ a2 v = E) → u ≠ v → op u v = J u v` frees every product whose right
  argument is not of the form `(_ * E)`, because both of its rules need that conjunct. `gen/_pb_common.py`
  computes the near-common split mechanically — `PLAYBOOK_PROOF.md` §3.2 says compute it, do not eyeball it.
* **Avoid `split` entirely with the `Z` combinator** from `certs/research_order5_hard_0001.lean`:
  `Z (R) (h1 : c → R a) (h2 : ¬c → R b) : R (if c then a else b)`. `split` dies with "maximum number of
  steps exceeded" past about ten rules and there is **no option to raise it**.

---

## The E-quotient carrier is wider than the handover says

Law 34889 was filed as a "pure extractor hole" with 2 semantic failures. It is a **Track C identity law**,
and three literal instantiations derive `(g*g)*(g*g) = g*g` — **every square is idempotent**. That is
strictly weaker than 12073's and 27859's *all squares equal and idempotent*, and collapsing every square to
one 0-ary constant `E` is nevertheless consistent with it. Three rows, about two hours, once the question
was asked.

**So for every law still marked "near-clean, 1-2 instances" — 6912 (1), 21864 (5), 39214 (1), 40037 (1) —
derive the forced idempotence or square identity before any further extractor work.**

Not universal, and the counterexample is proved: `PLAYBOOK_QUOTIENT.md` §4 shows square collapse forces the
trivial magma for 22591, and `gen/P2_EXISTENTIAL_DECODER.md` R1 shows 22591 makes *every* element a square,
which rules the carrier out there. Derive the forced identity first; do not assume either way.

## Two operational warnings from today

* **`squeeze.py` is NOT idempotent.** Squeezing an already-squeezed file yields a smaller file that does
  **not** compile (measured on an accepted 33020 certificate: 19,877 → 18,952 B, 18 errors), and the
  breakage reads as a name collision. It now warns. Squeeze the readable source once, and **compile
  whatever you judge**.
* **Lean 4 term-level application needs whitespace before `(` or `⟨`.** `foo(u)`, `foo (u)(v)` and
  `Or.inl⟨a,b⟩` all fail to parse; only tactics with their own bracketed grammar (`rw[`, `simp[`,
  `obtain⟨`, `exact⟨`, `refine⟨`, `rintro⟨`) tolerate the tight form. This caps whitespace-squeezing.

---

## Later additions (2026-08-29, from the agents that did not finish)

### `mxl` — `omega` cannot do max-vs-max goals  (law 32281)

```lean
mxl {a b c d} (h1 : sz a < sz d) (h2 : sz b < sz d) : max (sz a) (sz b) < max (sz c) (sz d)
  := by rw [Nat.max_def, Nat.max_def]; split <;> split <;> omega
```

`omega` collapses a whole `max` to one opaque `if` atom and **drops the `sz (J ..) = ...` equation in
context**, so a gate stated with `max` on both sides fails for a reason that looks like a missing
hypothesis. Routing every gate through `mxl` fixed three failing gates at once. If a `msr` gate will not
close and the goal has `max` on both sides, this is why.

### A size lemma is only as good as the pool that tested it — vary the junk variable

Law 17286's agent measured `RS : op u v = J u v ∨ sz (op u v) < sz v` at **0 violations over 420
constructed decoded pairs**, planned six proof leaves on it, and then **refuted it**: R2's gate is
`msr (a2 u) (a1 v) < msr u v`, so `mx` yields only `sz (a2 u) ≤ max (sz u) (sz v)` — nothing relative to
`sz v` — and the gap is **unbounded**, because `a1 (a2 u)` is the law's *junk variable* `y`, which no rule
constrains. Its own words: *"the pool had no big-junk `a1 (a2 u)`, the one shape that matters. When I hand
you a measured claim, treat the pool's construction as part of the claim."*

Two things follow.

* **Before believing a size bound, ask which argument the law leaves unconstrained, and put a large term
  there.** Every one of these laws has a junk variable; a pool built out of encodings never contains one.
* **`mx` bounds a result by `max (sz u) (sz v)`, not by `sz v`.** 32281's `RS` is true and 17286's is
  false for exactly this reason — 32281's recursive rule carries a *second* gate that pins the result to
  the `v` side, and 17286's R2 does not. So "a recursive rule's own gate bounds its result" (§3 above) is
  a real lever but bounds the result by the **max**; check which side the gate constrains before stating
  the lemma. The safe general form is 17286's

  ```lean
  RSZ (u v) : op u v = J u v ∨ sz (op u v) ≤ max (sz u) (sz v)
  ```

  which is proved, where the `< sz v` form is false.

### Do not state a top-product lemma with abstract `v` and abstract gates  (law 17286)

With abstract `v`, R3's second gate `msr (a1 v) (op w (a1 v)) < msr u v` is **unprovable** — nothing bounds
`sz (op w (a1 v))`. On the concrete chain term (`J z (J z Q)`) every gate is `msr_lt_of_max_lt` + `omega`.
Instantiate the chain first; that is why 17286's `TOPL` compiled first try after two failures.

### `gen/hole23357.lean` is a REFUTATION, not a proof

It has zero `sorry`s and 7,179 bytes, so the harvest scan (rail 47) flags it. It is a Lean-verified
refutation of the generated 23357 skeleton, with three explicit holes proved by `decide`. Do not try to
ship it. Zero sorries means "nothing is left to prove *in this file*", not "this file proves the law".


### A rule can fire at a DIFFERENT chain product than the one it was extracted for  (law 40037)

The strongest falsification of the session. 40037's 4-rule model passed `rv.run_tests`, `cf.deep_tests` at
20,000 on three seeds, **and a 1,560,896-assignment exhaustive sweep** — and is FALSE, verified in Lean
(`gen/_x40037_hole.lean`: the generated `op` plus
`simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]` reduces the goal to `⊢ False` in 4 s).

The mechanism, and it is generic:

> a generated rule whose precondition constrains **only `a1 v`** (or only `u`), with `v` pinned solely by a
> recomputation guard, can fire at a **different product of the law's chain** than the one it was extracted
> for.

No sweep of any size finds it, because the witness has to be *constructed* by chained encoding from the
rule's own precondition. **Add to the W3-6 case tree: for each rule, construct an instance that makes it
fire at every chain product, not only its own.** 36524's R13–R17 are the same shape (they constrain `u`
only, with `v` appearing solely inside a recomputation) and are flagged as at risk.

### `_orch_min<eq>.json` without a `status` key is UNVALIDATED  (law 10218)

`gen/_orch_min10218.json`'s 3-rule set is FALSE — `rv.run_tests(law, rules, [3,4,5], 3000, 12000)` gives
**73 fails in 15 s**. The file was written by an older `_orch_minim.py` that did not validate, and it has no
`status` / `fails` / `dualized` key. Treat the absence of `status` as "never validated", and re-run the
minimiser rather than emitting from it.


### THE LEVEL-k DESCENT — the sixth oracle, and it refutes sets the other five pass  (law 12087)

`gen/_w3_12087_deep3.py`. **Run this on every model in this family before writing any Lean.**

Build a chain of nested encodings so the decoder has to descend *three* levels in the same argument:
with `x = enc(y,·,·)`, `p2 = enc(x,·,·)`, `p = enc(x,p2,·)`, `z = enc(x,p,·)`, so `op x z`, `op x N3`
**and** `op x (op x N3)` all decode.

| model | levels 0 | levels 1 | levels 2 |
| --- | --- | --- | --- |
| S7 (7 rules) | 0/500 | 0/500 | **500/500 BAD** |
| full13 | — | 0/500 | **500/500 BAD** |
| `closedform2`'s 11 | — | — | **BAD** |

Four configurations, two seeds, both junk pools, `cycles = 0` on fresh evaluators. The **semantic** free
model returns `x` on the same instance, so the law stays Track B — but the rule set required is
**infinite**: each extra level of `x`-encoding nested inside `z` needs one more structural reading, and
nothing can read the payload at `(op x N3).1.1.1` because that is a *value*, not a position in `v`.

**Why no earlier oracle finds it.** `rv.run_tests` draws random and rule-shaped terms; `cf.deep_tests`
draws random deep terms; the 16-cell case tree forces each product to decode once; the both-decoded census
forces two. **Only this forces the same rule to fire at three successive depths of one argument.**

**What it means when a model fails it: you need a decoder that RECURSES, not more rules.** The recursion is
the left-inverse of `op` — given `(z, N3)` with `op x z = N3`, find `x` — and it is well-founded because a
decoded `op u w` satisfies `sz (op u w) < sz w`, so `(z,N3) → (N3, op x N3) → …` strictly decreases.
`WAVE2_PROMPT.md` §2 permits a rule whose result is a nested `op`, and `gen/rec18137b.lean` is the shipped
template. It cannot come from `closedform`/`closedform2` as they stand (`gen/EXTRACTOR_NOTES.md`, "What is
still missing", item 3: the DSL supports nested-`op` results but no mode emits one at a non-`vdec` node).

Corollary from the same law: **`FD` is not always a replacement for a fuel-induction freeness lemma** — in
12087 it is a three-line corollary of `SU` (`sz a < sz (a1 u) ≤ sz u` contradicts `sz u < sz a`), not a
strengthening. Check which one your model's gates actually give you.


### The digest compresses a rule SET; only a different CARRIER compresses a DEFINITION BLOCK  (law 13764, 3 rows)

The single most useful byte result of the session, and it overturns `PLAYBOOK_PROOF.md` §3's implicit
promise. 13764's extracted free model has **67 rules and a 54,402-byte definition block** — 2.7x the whole
20,000-byte cap *before any proof*. §3's digest cannot help: it compresses the *proof* over a rule set, not
the `def op` that declares it, and neither can minimisation (the rule count is 2^k by construction, one rule
per free/decoded combination of the chain).

What worked: **replace the extractor's free model with a hand-built term algebra carrying a second
constructor.** `M ::= g n | J a b | E a b`, the whole model expressed as **three decidable predicates**
(D with 4 disjuncts, Q, W) instead of 67 rules, `op` a 4-branch if-chain with one `let` and one recursive
call. **67 rules → 5; 54,402 B → ~2,300 B; certificate judged at 13,588 B with 6.4 KB spare.**

> **When the definition block alone is over the cap, stop minimising and change the carrier.**
> `gen/_x13764_lab.py` is the tool; `gen/NOTES_13764.md` is the worked example.

The same law also produced the fourth, fifth and sixth instances of rail 50 in one session: **three
successive models each validated clean at 1.7–2.3 million chains and each was FALSE**, all three found by
hand case-tree walking and none by any sampler. The shipped v14/v15 replaces a structural guard with a
**recursive re-run of the encoding** and is clean at 2,340,296 chains including all three regression
families.

Two Lean mechanics from the same agent:

* **If a rule lemma's guards include `rfl` for `a2 v = u`, finish the product with `exact`, never `rw`.**
  All six of its first-round errors were this: `rw` unifies against the pattern `op (a2 ?v) ?v`, which is
  defeq to the goal but not syntactically equal.
* **`CORE`-style parameterisation.** When two branches share a long tail and differ only in *why* two
  coincidences are impossible, pass those as hypotheses and prove the tail once.


### `Z` removes `op_cases` too, not only `split` — when the result set is a singleton  (law 38316)

`_pb_common.py` reports whether the whole `if`-chain has **one** result expression. When it does — e.g.
every rule of 38316's 12-rule model returns `a1 v` — **no branch condition ever needs inspecting**, so the
entire digest is

```lean
Z {c} [Decidable c] {a b u v} (h1 : a = J u v ∨ a = a1 v) (h2 : b = J u v ∨ b = a1 v) :
    (if c then a else b) = J u v ∨ (if c then a else b) = a1 v
Wdig (u v) : op u v = J u v ∨ op u v = a1 v      -- `rw [op.eq_1]` then a 12-deep `Z` cascade
```

**~1.1 KB, with no `op_cases` at all** — against the 5,250 B (18 `let`s) `_pb_gencases.py` emits for the
same skeleton. It holds at any rule count. **Check `_pb_common.py` for a singleton result set before
generating `op_cases`.**

### A freeness lemma can be unprovable with an abstract argument and provable on the chain term

Second instance, checked *before* the proof attempt rather than after (17286 found it the hard way).
38316's `Dfree` with an abstract `c` is **unprovable**: `P3` is literally `tg v = 2`, true for any free `c`,
and R3's guards then reduce to `op (a1 y) x = y` and two more, none size-refutable. On the instantiated
chain term the same statement goes through. **State freeness lemmas on the chain, not on abstract
arguments** — the abstract version can look safe and be false or unprovable.


---

## THE RECURSIVE-DECODER CARRIER — four laws need it, one has shipped it

By the end of deep session 8 this is the dominant structural finding, and it supersedes a lot of the
per-law advice above.

**The extractor's free model is the wrong carrier for the hard laws.** `closedform` emits one rule per
free/decoded combination of the chain — 2^k rules — and reads the payload off a **fixed accessor path**.
For several laws the required rule set is therefore **infinite**: each extra level of encoding nested in the
argument moves the payload one level deeper, and the rule that reads at depth d is refuted by the level-(k+1)
instance. Measured, independently, on four laws:

| law | how it was found | the depth argument |
| --- | --- | --- |
| 12087 | level-k descent, 500/500 bad at level 2 | nothing can read the payload at `(op x N3).1.1.1` — that is a *value*, not a position in `v` |
| 11081 | large-junk producer fuzz (7th oracle), 13/52,325 | the key sits at `y.11121`, depth 5; a 4th rule for that path is refuted by the next instance |
| 17286 | level-k descent, fails at level 1 | `x = a1(a2(a2(a2(a2 B))))`, depth 5, where R4 reads at depth 3; **level k needs depth 3k+2** |
| 13764 | hand case-tree walking, three models clean at 1.7–2.3 M chains and all false | 67 rules, 54,402 B definition block, 2.7x the cap |

**13764 is the one that got out, and its construction is the template.** Replace the extractor's free model
with a hand-built term algebra carrying a second constructor:

* `M ::= g n | J a b | E a b` — accessors total, `tg` 1/2/3;
* the whole model as **three decidable predicates** (D with 4 disjuncts, Q, W) rather than N rules;
* `op` a **4-branch if-chain with one `let` and one recursive call**, `termination_by sz u + sz v`;
* crucially, **the structural guard is replaced by a recursive re-run of the encoding** — that is what
  makes it independent of nesting depth.

**67 rules → 5. 54,402 B → ~2,300 B. Certificate judged at 13,588 B with 6.4 KB spare. Three rows.**
Tools: `gen/_x13764_lab.py` (the carrier lab), `gen/NOTES_13764.md` (the worked example).
Lean template for a nested-`op` result: `gen/rec18137b.lean`; `WAVE2_PROMPT.md` §2 permits it.

**One caution, from 17286, that must not be taken on trust: the recursion is well-founded only on the
v-side branch.** `sz (op a b) < sz b` is **FALSE in general** — that is exactly the `RS` refutation — so the
gate has to name the v-side family specifically, not appeal to a global size argument. 11081's
`KY : op y x ≠ J y x → sz y < sz x` is the sharper form where it holds.

**What survives a carrier change.** The size preamble (`sz_pos`, `sz_a1_lt`, `sz_a2_lt`, `tgJ2`, `Jinj`),
`op_cases`, `Z`, `mx`, `mxl`, and the `Enc`/`RF` scaffolding are all model-independent or one `TR` away —
`Enc w v` is exactly "v codes w", and a recursive decoder is Enc-directed. What does not survive is any
lemma tied to the current if-chain.


### Building an E-carrier: two rails that cost four of six iterations  (law 12087)

**(1) With two binary constructors and total accessors, every shape test must be `tg t ≠ 1`
(non-generator), NEVER `tg t = 2`.** Both constructors carry the same two components, so the accessor path
is already correct on either — and testing for `J` specifically fails the moment an inner product got
tagged. Relaxing that test at successive depths took 12087's L1 sweep (all 74 terms of size ≤ 5 over two
generators) from 110 → 303 → 935 → 14,066 → 230,365 → **405,224 chains clean**. Four of six iterations were
this one mistake.

**(2) The tag must keep both arguments: `E u v`, not `E x y`.** A tag that discards structure fires at an
inner product with a different-but-valid instance. `E u v` is what 13764 actually does.

**And the payoff, which is the reason to prefer this carrier over the free model even before the byte
count: the Lean gate becomes unconditional.** 12087's recursive call takes `a2 (a1 u)` and `a2 u`, both
proper subterms of `u`, so `sz (a2 (a1 u)) + sz (a2 u) < sz u ≤ sz u + sz v` needs **no hypothesis**. The
measure is the linear `sz u + sz v` — no `msr`, no `msr_lt_of_max_*`, one `let`. That is the 27859 shape
(which shipped at 9,108 B on the first compile with no induction anywhere in the file) and the 13764 shape.
Definition block ≈2,500–3,000 B against 10,506 B for the same law's free-model skeleton.

`gen/_w3_12087_lab.py` is a self-contained lab that runs **every** validator — L1, deep, and the level-k
descent at levels 0–3 with the large-junk pool — **in 2 seconds**. Copy its shape when building a carrier;
a fast oracle loop is what makes six iterations affordable.


### A level-k descent can be VACUOUS, and a vacuous one looks like a clean bill of health  (law 21864)

**Read this before believing any level-k zero.** Law 21864's first adaptation returned
`('F','F','F','F')` in **4,800 / 4,800 instances with BAD = 0** — and it was measuring nothing. Its decode
is a *matched pair*, `op(AT(y,z,t), BT(t,y)) = t`, so `op(a,·)` decodes for exactly one `b`; a tower of
encodings of a single payload therefore forces no descent at all. The agent caught it only because it had
printed the **cell census** alongside the failure count.

> **Any level-k adaptation must be checked against its own cell counts before its zero is believed.**
> If the cells you meant to reach have count 0, the oracle is vacuous, not passing.

The working construction for a matched-pair decode iterates **the pair**:
`(t_{k+1}, y_{k+1}) = (AT(y_k, junk, t_k), BT(t_k, y_k))`, so `y_{k+1}`'s inner product is again a decode
and the rule descends k levels in one argument.

**Run both tower variants.** 21864 has two, and only one of them refutes:

| rule set | variant A (`x` = deep decoder, `Q = op(x,y)` descends) | variant B (`x` = deep encoding, `z` its matched decoder, `P = op(z,x)` descends) |
| --- | --- | --- |
| `gen9` (extractor output) | 0 | **9,606 / 12,800** |
| `ship11` (the shipped package) | 0 | **11** |
| `t8_13` | 0 | **7** |

Eight hand repairs took variant B from 75% broken to **0.09%** broken — real work, nearly right, and still
fatal for a proof. It also fails at **level 1** (6/6000), so it is a *cell the earlier oracles never built*,
not only a deep-descent effect.

### The oracle ladder, as it stands at the end of deep session 8

`rv.run_tests` → `cf.deep_tests` 20k x 3 seeds → the case tree (each chain product decodes once) → the
both-decoded census (two) → `qz_lib.identity_probe` → **the level-k descent, both variants, with cell
counts printed**.

21864's 11-rule set passed the first five and died on the sixth. **Eleven models were falsified in one
session and every escalation was forced by a model that passed the previous rung.** Do not treat any rung
as sufficient.


### The tenth rung: FORCED FIRING — construct, do not sample, a rule firing at the wrong chain product

The 40037 lesson, turned into a construction and then decisive on a second law. **Law 9663's `q9663d`
passed nine oracles and is false.** It had survived 2,522,585 + 1,061,208 exhaustive assignments, a 1.5 M
case tree, level-3 and level-4 constructions, and the whole level-k descent in both `inimg` flavours and
both junk pools.

What killed it: instrument *which rule fires where*. On 9663's level-3 instances the **root** product fires
`W3` 1536/1536, while `op z y` fires only `free`/`W1` — **zero** `W2`/`W3` firings at that product across
~932,000 sampled pairs. So the agent stopped sampling and **built** the instance: satisfy the rule's own
precondition and place that term at a product it was not extracted for.

| model | forced pairs | rule at `op z m` | `IMG` counterexamples | law failures |
| --- | --- | --- | --- | --- |
| `q9663c` (W1+W2+W3) | 120 | W2 120/120 | 96 | **384** |
| `q9663d` (W1+W3) | 1,260 | W3 1260/1260 | 1,008 | **4,032 / 5,040** |

> **For each rule, satisfy its own precondition and place that term at EVERY other product of the law's
> chain. Construct it; a sampler will report zero firings there and be believed.**

Probes: `gen/_x9663_force.py`, `gen/_x9663_force3.py`, `gen/_x9663_img.py`.

### Why "add another rule" does not converge — and what the fixed point is

Law 9663's agent found the structural reason, and it explains this whole family. `inimg A u` is a
structural **under-approximation** of `im(R_u)`, and the proof needs it closed under the operation
(`IMG (z u) : inimg (op z u) u`, because the root consumes `A = op z y`). But **every witness rule added
to make the root decode enlarges `im(R_u)`** — `W2` returns `a2 (a1 z)` and `W3` returns
`a2 (a2 (a2 z))`, *subterms of the first argument*, about which a predicate on `(A, u = second argument)`
has no structural handle. Each new rule breaks `IMG`; repairing `IMG` widens `inimg`, which widens the
decoder, which adds more values to `im(R_u)`.

> **The fixed point of that loop is the existential decoder.**

So the "infinite hierarchy" of rail 58 and the "existential decoder" of `gen/P2_EXISTENTIAL_DECODER.md`
are **the same obstruction reached from two sides** — one where the payload's *position* is unbounded, one
where the witness *set* is not structurally definable. As of the end of deep session 8 the following rows
all depend on solving it once: **12087 (2), 11081 (4), 17286 (4), 21864/24199 (2), 9663/36487 (3),
12294 (1), 21865 (2), 21866 (2), 22591 (3), 10222/35836 (2) — 25 rows.**

**And there is exactly one construction on record that gets out of it: 13764's hand-built E-carrier with a
recursive re-run of the encoding, three accepted rows.** Law 12087's version of it is one disjunct from
complete and has an *unconditional* Lean gate. That is the template; build it once and it is worth most of
the remaining set.

One simplification that survives 9663's refutation and is worth having: the congruence result stands, so
**9663, 36487 and 12294 force no identity — their carrier is plain free terms**, no quotient and no new
constructor, once the decoder exists.


### Three measured design facts for building an E-carrier  (law 12234, a 16-carrier ladder)

`gen/_x12234_carrier.py` holds sixteen rule sets in a registry with four oracles wired, and the total-fail
column is the whole design process made visible:

| carrier | rules | exhaustive | descent | deep | total |
| --- | --- | --- | --- | --- | --- |
| K1 (mark D, M checks A) | 2 | 8,112 | 5,425 | 1,999 | 15,536 |
| K4 (**M keeps both args, `E u v`**) | 2 | 1,494 | 6 | 377 | 1,877 |
| K7 (+ `tg (a1 (a1 v)) ≠ 1`) | 2 | **0** | 521 | 0 | 521 |
| K12 (+ M's own guard on `v`) | 2 | **0** | **0** | 81 | 81 |
| **K15** (+ recomputation on R) | **2** | **0** | **0** | 38 | **38** |
| K16 (a 4th constructor `G`) | 4 | 6,784 | 102 | 355 | 7,241 — regressed |

1. **No guard may depend on the junk variable's product.** 12234's `z` is junk and `A` marks or decodes
   freely; K1 checked `A` and paid 15,536 fails, and dropping that check took the level-k descent from
   5,425 to **0**. Law-specific — 13764 had no junk variable in that position — so ask which product is
   junk *before* writing guards.
2. **The mark must keep both arguments** (second independent confirmation). `E (a1 v) (a2 v)` → `E u v`
   is 22,808 → 1,494, and the reason is worth knowing: a mark that misfires at an inner product is then
   **transparent** — its `a2` is unchanged, so the outer rule still marks and the root still reads through
   it. Misfires become *tolerated* instead of fatal.
3. **The decode rule must certify that `v` came from the mark** — half by the mark's own guard on `v`, half
   by a recomputation.

**And the level-k descent earned its place again, on the same day:** K7 is exhaustive-clean at **405,224
chains** and the descent finds **521** fails. Without it K7 goes to Lean. That is the fourth model this
session to pass ~10^6 chains and be false.

**Byte outcome, which settles the earlier "12234 cannot fit" verdict:** free model 5,167 B definition block
and a certificate 6.3–9.3 KB *over* the cap; the K15 carrier projects to a ~2,100 B block and an
~11,000–14,000 B certificate, **~6 KB under**. Measured against 13764's shipped 2,891 B / 13,588 B. The
eight `Dfree` sorries disappear with the model that created them.


### A second escape shape: SEARCH for the payload, no second constructor  (law 17286)

13764/12234/12087 escape the infinite hierarchy with a **tag** (`E u v`) plus a recursive re-run. Law 17286
escapes it **without changing the carrier at all** — `M ::= g n | J a b` stays — by replacing the
fixed-depth read with a **bounded search over candidate payloads**:

```
op u v = if tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) then
            let w = a1 v, P = a2 (a2 v)
            first c in [a1 P] ++ [a2 u] ++ unwraps(P) with ok_u u c ∧ op c w = P
         else J u v

unwraps(P) : c := a1 (a2 (a2 P)) repeatedly -- proper subterms, so level k costs k unwraps
             instead of a depth-(3k+2) accessor
ok_u u c   : (tg u = 2 ∧ a2 u = c) ∨ codes u c
codes u c  : tg c = 2 ∧ tg (a2 c) = 2 ∧ a1 c = a1 (a2 c) ∧ op u (a1 c) = a2 (a2 c)
```

**That is the point: level k costs k unwraps instead of one more rule.** The 2^k rule family collapses into
one search. Validated at levels 0–3 of the descent in both junk pools (0 bad, cycles 0), exhaustive
`sz ≤ 7` / 2 generators (103,768 triples, 0 bad) and `sz ≤ 9` / 1 generator. The oracle is discriminating
on this law, not vacuous: the free model fails it at level 1, and so did the agent's own v1 and v2.

**Two design errors it caught, both generic:**

* **The u-side check is not optional.** With `op c w = P` alone, `a1 P` fires for any `u` and `op` stops
  depending on its left argument — 440/2,728 bad at level 0.
* **No size cutoff on the candidate.** A `sz c ≥ sz v` "sanity guard" discards the correct payload whenever
  junk is large (0 bad on small junk, 32–42 on big). That is the `RS` refutation returning as a *modelling*
  bug: `a1 u` is unbounded, so `sz (a2 u)` can exceed `sz v`.

**The cost of this shape is termination.** A search that mixes sides (`op c w`, `op u (a1 c)`) is
well-founded only through a short-circuit, which is exactly the subtle decreasing argument the tag carrier
is chosen to avoid. Prefer a search that descends in **one** argument, at the price of an extra disjunct.

**And build the lab first.** 17286's descent alone runs ~90 s because each triple builds a fresh memo,
against `gen/_w3_12087_lab.py`'s 2 s for the whole stack. Several iterations are normal here — 12234 took
sixteen carriers, 12087 six — so a slow oracle loop is the binding constraint on the whole approach.


### `Y` — the condition-side twin of `Z`, and the other half of the byte lever  (law 38316)

`Z` handles the **result** side of an `if`-chain. `Y` handles the **condition** side:

```lean
Y {c} [Decidable c] {a b u v} {Q} (h1 : c -> Q) (h2 : b != J u v -> Q) : (if c then a else b) != J u v -> Q
```

With both, a 12-rule chain needs **no `split` and no `op_cases` on either side**, at ~1.1 KB each.

**Find the uniform structure mechanically first.** `gen/_x38316_gendig.py` parses the chain and reports
whether the rules share a shape. For 38316 all twelve put their gate at conjunct 1 and their `a2 v = p_k`
equality at conjunct 4 (rules 1-7) or 6 (rules 8-12), with only **two** distinct nested calls. So *every*
rule needs `op W u = a2 v`, and `Wdig` then pins `a2 v` to `{J W u, a1 u}` -- one lemma (`Adig`), twelve
one-line `Y` branches. Check for that uniformity before writing anything per-rule.

**Mechanic:** to apply a rule positively without `op_cases`, `rw [op.eq_1]` then `rw [dif_pos g1, dif_pos
g2, ...]` **on the goal** -- that de-zetas the `p_k` `dite`s in place at zero byte cost -- before
`rw [if_pos hcond]`.

### An abstract lemma can be false through a coincidence between the law's OWN variables

Third instance, and the sharpest. 38316's planned first step was `Dfree`: "`d = op x c` is free". It is
**false**, and *no battery can see it*, because the batteries record which rule fires, not this
coincidence: when `tg x = 2`, `y = a1 x` and `z = a2 x`, the chain runs `a` free, `b` decoded, `c` free,
`d` **decoded** -- and the law still holds, because the *free* top product `J y d = J (a1 x) (a2 x)`
already **is** `x`.

> The invariant is not "`d` is free" but **`op y d = x`**, discharged either by the free branch (when `y`
> and `d` happen to be `x`'s own components) or by a rule firing with `a1 d = x`. The digest hands you
> exactly that dichotomy at the top pair, so `law` should case on it first.

**The general form: a freeness lemma stated over abstract arguments can be false because the law's
variables coincide, not because a pool was too small.** Empirical validation cannot reach it -- the witness
is an *identification* among `x`, `y`, `z`, not a term shape. State the invariant as the equation you
actually need at the top product, not as freeness of a chain product. (17286 hit this one level down;
38316's agent caught it before writing the proof rather than after.)


### Three qualifications to the E-carrier rails  (law 11081, five carriers)

**Rail 1 needs a qualification: shape tests must be `tg t != 1`, but TAG tests must stay `tg t = 3`.**
`tg (a2 v) = 3` is not a shape test — it means "`a2 v` is an op-output". Relaxing it to `!= 1` re-admits
raw `J`-nodes and restores the over-approximation that killed an earlier carrier. Ask of each test: am I
asking "does this have two components" (use `!= 1`) or "did this come out of `op`" (use `= 3`)?

**Rail 3 pays off cleanly, and is worth an extra unfold.** Unfolding "u is R1-decodable" one level makes
both recursive arguments proper subterms of `u`, so the gate is unconditional and the measure is the
linear `sz u + sz v` — **a shipped certificate for that law needs no `msr` machinery at all.**

**Lab hygiene, and it invalidates profile tables rather than counts.** A lab that memoises and breaks
recursion cycles by returning the tag makes a *recomputed* profile disagree with the value the chain
actually got — so the profile column reads as evidence when it is an artifact. 13764's lab avoided this by
being non-recursive. **A recursing lab must carry the same well-founded measure the Lean `op` will have,
and fail loudly rather than cycle-break.**

**And the storage theorem, which is the shape of the remaining obstruction on this law:** *a rule handling
"C decoded" must store its key at a fixed path of `v`, and no such rule can — its `a2 v` is `a1 (a1 u)`, a
proper subterm of `u`, so `a2 (a2 v)` cannot be `u`.* A recursive `key` extractor does not help: it
recovers the key of `u`, and the root needs the key of `a2 v`. **The next lever is to change which product
carries the key, not which rule reads it** — a fourth constructor reserved for the product the law
re-reads, which is the direct analogue of what 13764's `E` marks.


### One rule per reachable cell — the completeness check, and why the digest works  (law 10218)

A pattern across every model that has shipped or validated this session:

> **A correct model has exactly one rule per *reachable* free/decoded cell of the law's chain, and the
> surviving rule's guard is always `rfl`, because its nested product IS one of the law's own chain
> products.**

10218's validated model has **six** rules and exactly six reachable cells, with the census to match
(1,577,065 + 405 + 267 + 36 + 3 + one reachable only by targeted construction, over 1,577,776 assignments).
That is why its `ROOT` invariant is two `by_cases`, and why 27859 needed no induction anywhere.

**So it is a cheap completeness check on any candidate model: count the reachable cells, count the rules.**
A model with more rules than reachable cells has dead rules (delete them, ~650 B each); a model with fewer
has a hole, and the missing cell tells you which construction to build.

It also explains the digest: when each rule owns one cell, `TR`'s disjuncts are mutually exclusive on any
actual chain, so the case analysis in `law` is a decision, not a search.

**Two mechanics from the same law:**

* **State a gate in the UNREDUCED `op_cases` form**, or `rw [dif_pos g] at hp` fails with "Did not find an
  occurrence of the pattern" (`PLAYBOOK_PROOF.md` §7 pitfall 4, in the other direction). Prove it with
  `simp only [a1_J_eq, a2_J_eq]; exact msr_lt_of_max_lt (mxl _ _)` — plain `omega` cannot do the max-vs-max
  goal.
* **`Pdig` pinning `u` strictly INSIDE `v`** (`u = a2 (a1 v) ∨ u = a2 (a2 v)`) is what makes the size
  lemmas induction-free. When every rule locates its left argument inside its right one, `Wsz`, `Wne`,
  `Dsz` and `Dv` all follow without a fuel argument. It is the structural difference between 10218 (works)
  and 40037 (does not).

### Ruling out a quotient needs a POSITIVE CONTROL  (law 40037)

`gen/_x40037_derive3.py` — ground equality saturation with e-matching, argument pool = class reps of
bounded size **plus a BOOST list of the structured terms a hand derivation reaches for** (repeated squares
to size 31). The BOOST list is what makes it work.

* **Positive control, 6912:** `a*a = b*b` DERIVED, `a*a = (a*a)*(a*a)` DERIVED,
  `(a*a)*(a*a) = (b*b)*(b*b)` DERIVED, 29 merged classes of size ≤ 9 — exactly reproducing the hand
  derivation.
* **40037, at the same and at strictly stronger settings** (1 generator to size 9, 900k nodes; 2 generators
  to size 5 + BOOST, 1.5M nodes): every identity `no`, **0** merged classes.

So 40037 forces no identity at all and its single semantic failure is **not** a Track C symptom. A search
that finds nothing is only evidence once it has found something it should.


### An UNDER-FIRED branch in the census is a live warning  (law 17286, twice)

The eleventh rung, and it caught a carrier that had just passed the level-k descent, both exhaustive
sweeps and forced firing.

17286's v4 stack showed the unwrap branch — *the entire point of the carrier* — firing **twice in 130,000
chains**. That is not "the branch is unneeded"; it is "the branch is untested". A probe built to exercise
it deliberately at tower levels 0–4, **with a fresh model per level**, found **18/108 bad at level 1**.

> **Report per-branch firing counts beside every "0 bad on N chains". A branch that fires ~0 times has not
> been validated, however large N is.**

Two riders, both generic:

* **A candidate list of projections and unwraps is INCOMPLETE — some payloads are *reconstructions*.**
  17286's missing payload is not a subterm of the argument at all: it must be rebuilt as `J (a1 P) P`.
  Its free model's R7 had exactly this shape and the search carrier dropped it when the rule list was
  replaced by projections. When you convert a rule family into a search, check every rule's *result*
  expression, not only its reading positions.
* **A cumulative census with a shared memo gives non-independent per-level deltas** — levels 2 and 3 show
  no new firings because their pairs were memoised. Use a fresh model per level for the per-level counts.

**And the termination cost of the search shape is real.** `J (a1 P) P` is not a subterm of `v`
(`sz c = sz (a1 P) + sz P + 1`), so `termination_by sz u + sz v` does **not** cover that branch. The free
model's R7 solved it with its own `msr` gate, so 12087/27859's "no `msr` at all" outcome is probably not
available whenever the payload must be reconstructed rather than located. **Decide this before writing the
Lean file — it decides whether you need `op_cases`/`decreasing_by` machinery at all.**

Speed note: the same agent took its full stack from ~90 s to **6 s**. Do that before iterating; 12234
needed sixteen carriers and 12087 six.


## H3 — THE CHEAP DECISIVE ORACLE FOR TAG CARRIERS. RUN IT BEFORE THE DESCENT.

From law 12234's second carrier pass. **Build `y = enc(j, w, x)` so that `y` is a genuine encoding *by x*,
then run the law.** That is all it is.

It separates candidate carriers by **five orders of magnitude**:

| carrier | standard battery (470,424) | **hard battery (3,046,197)** | where it dies |
| --- | --- | --- | --- |
| K15 (2 rules) | 38 | **690,550** | H3 **689,976 / 689,976 = 100%** |
| K19 (6 rules) | **0** | **7,390** | H3 7,060 |
| **K18 (4 rules)** | 2 | **16** | H5 only; H1-H4, H6, H7 all **0** |

### The ranking lesson is worth more than the oracle

**The standard battery mis-ranked all three.** It ordered K19 < K18 < K15; the hard battery orders
K18 < K19 < K15. K19 was a repair aimed at K18's last two fails: its extra rules buy 2 and cost 7,060,
because one of them fires at `A = op z x` for any E-term `x` with a generator first component.

> **A carrier scoring 0 on a weak battery and 7,390 on a strong one is worse than one scoring 2 and 16.
> Rank carriers on the strongest oracle you have — never on the battery they were tuned against.**

Fifth model of the session to pass ~10^6 chains and be false. **470,424 chains is not enough.**

### Two more results from the same pass

**The `tg t = 2` mistake has a fail-count signature.** Audited across the ladder: K8/K10/K11 made it and
cost 5,336 / 68,974 / 68,672. Same signature and cause as law 12087's. **If a carrier's fail count is in
the tens of thousands, check every shape test for `= 2` before looking at anything else.**

**"Recompute with `y` twice" works, and design fact 2 applies to the SECOND mark as well.** K17 used `a2 u`
twice and closed the target cell, but its second mark `M2` then misfired at the B position (140 fails).
K18 fixes it by making `M2` emit `E u v` keeping the *real* `v`, so an `M2` misfire is transparent exactly
as an `M` misfire is, and recovers the payload at the root with a second reading through B.
**Both gates stay unconditional:** both recursive calls take proper subterms of one side, so with measure
`sz u + sz v`, `M2` gives `sz(a2(a1 u)) + sz(a2 u) <= sz u - 1` from `tg u != 1` and `R2` gives
`sz(a2(a1(a1 v))) + sz(a2(a1 v)) <= sz(a1 v) - 1` from `tg (a1 v) != 1`. K18 has four rules but only
**three distinct results**, so in Lean it is three predicates and a four-branch `if`-chain — byte-for-byte
13764's shipped shape (2,891 B definition block, 13,588 B judged).

### The gate mechanic that folds every previous one together  (law 38316)

```lean
refine (if_pos ?_).trans rfl
```

Because `if_pos`'s `?c` unifies **from the goal first**, the anonymous constructor gets the branch
condition as its expected type — so **every gate is an unannotated `?_`**. You never state a gate's type,
which is both what costs bytes and what triggers "Did not find an occurrence of the pattern". Then
`rw [dif_pos (GT ...)]` de-zetas each `p_k` in place at zero byte cost, with `GT`'s implicits coming from
the `dite`:

```lean
GT {A B u v} (h1 : sz A < sz v) (h2 : sz B < sz v) : msr A B < msr u v := msr_lt_of_max_lt (mxl h1 h2)
```

Measured on that law: one cell costs **912 B**, and `squeeze.py --rename` takes the file 15,757 -> 14,126 B
(-12.8%) **and the squeezed file still compiles** (verified, not assumed).

**And the honest cost model for a `law` case analysis:** it cases on the digest at each chain product, so
`k` products give `2^k` combinations. The batteries reach only the *reachable* ones — 6 of 16 for 38316 —
and **the other ~9 must be proved impossible, which is the expensive half, not the six exhibitions.**
Count that before promising a certificate in one sitting.


### A search decoder needs a `find` helper — the generated-skeleton encoding cannot express one  (law 17286)

The structural cost of the search shape, named precisely. **The unwrap candidate list has length k at tower
level k, i.e. it is unbounded** — and `leangen`'s encoding binds a **fixed** number of nested calls
(`let p_k := if hs_k : … then op … else J u v`), so it cannot express a search at all. Two ways out:

1. **`op u P` IS the unwrap** (branch V's `a1 P'` fires one level down), and it decreases since
   `sz P < sz v`. But the validity check `op c w = P` then has `c = op u P` of unbounded size, and it is
   not obviously inlinable.
2. **A `find u P w : Option M` helper, mutually recursive with `op`, by well-founded recursion on
   `sz P`.** Clean termination; the cost is mutual WF recursion and a second `eq_1`-style unfolding lemma.

**Try 1 briefly, then take 2 without regret.**

**Two positive results from the same law worth keeping.** *Rail 3 is satisfiable even for a search carrier
with a reconstruction*: the reconstruction's own check inlines when it coincides with another branch
(`op c w` for `c = J (a1 P) P` is exactly branch U at `(c,w)`), and then every call decreases
`sz u + sz v` unconditionally — **no `msr`, and `mx`/`mxl` are not needed for the definition at all**.
The per-call table is in `gen/NOTES_17286.md`. And *the unwraps are not redundant once the reconstruction
branch exists*: 143,347 chains through every oracle give 0 bad with unwraps and **30 bad without**
(`gen/_x17286_nounwrap.py`) — the two-level tower again.

**Lab hygiene, third instance:** keep numbered variants (`_x<eq>_v1..vN.py`) rather than editing one lab in
place. 13764 did and its eleven-variant progression is auditable; 17286 did not and six model versions are
unrecoverable.


### An identical fail count across two versions means the guard certifies NOTHING  (law 11081)

A recomputation guard is load-bearing in 13764 because its W6 rule reads its payload out of `u` — there is
something to certify. 11081's rules all return `a1 (a1 v)`, a subterm of `v`, so adding the same guard
changed nothing: v8 = v7 and v9 = v6, **identical fail counts**.

> **Two versions with identical fail counts differ by a guard that certifies nothing. Delete it.**

Cheap corollary: diff fail counts, not just totals, when adding a guard.

### The census can be vacuous with respect to the failure that kills the model  (law 11081)

Stronger than the earlier vacuity warning, and it nearly shipped a false model. v6's census showed
`Ddec = False` across **all 97,032 chains** — the entire sweep never reached the product whose decoding
kills the carrier. Without the census, v11's `0 / 96,792` reads as validated. A targeted probe
(`gen/_x11081_forceD.py`) then kills v11 at **19,140 / 28,800**.

> **Order the oracles by which one reaches the cell that matters, not by how many chains they run.**
> 28,800 targeted chains found what 96,792 general ones could not.

### The tag DELETES the `inimg` obstruction — evidence the E-carrier is the right answer to all 25 rows

From law 9663's carrier build, and it is the strongest structural confirmation of rail 58 so far. That
law's refutation was entirely about the guard on the **junk slot** `A = z◇y`. With a tag, the root never
guesses membership of `im(R_y)` — the code is recognised by its **constructor**, which only the model can
produce. **The junk slot is unguarded in every variant, and not one failure involves it. The `IMG`
fixed-point loop does not arise.**

That is independent evidence that 13764's carrier is the right answer to the 25-row obstruction, from a law
whose obstruction was diagnosed from the *other* side (an undefinable witness set rather than an unbounded
depth).

**How many constructors: count the products the law re-reads.** 13764 re-reads one and needs two
constructors; 9663's chain re-reads two (`P` and `Q`), so `E` is overloaded — it marks both "the `(x,P)`
pair marker" and "the code container", and the decode rule cannot tell them apart. It needs
`M ::= g | J | E | F`. **Read the positions off the failing cell census rather than guessing them**: 9663
lost an iteration to a linking guard (`a2 v = a1 u`) that was too strong and fired four times, never in the
cell that needed it.


### The existential decoder reappears INSIDE THE CERTIFICATE — and search cannot reach it  (law 21864)

The sharpest negative result of the session, and it closes a loop.

A search decoder certifies a candidate `t` with `<t codes w>`. Law 21864's agent built the recursive
`codes` exactly as 17286 specifies — `codes(t,w) := a1 t = w and exists c in [a2 (a2 t)] ++ unwraps (a2 t)
with op (w,c) = a2 t`, no size cutoff, `tg != 1` throughout. It fires 701 times and finds **nothing** the
non-recursive version did not: descent 1002, exhaustive 8/15, deep 2, forced 2 — **digit for digit
identical**.

**Why.** In the tower case `t = BT(w, y')` has its inner product **decoded**, so `a2 t` is a payload and
`y'` is not a subterm of `a2 t`, of `t`, or of the pair at all — **it was destroyed by the very decode
being certified**. Projections and unwraps of the term being certified cannot reach it, and no other
subterm search can.

> **A search decoder moves the existential decoder from the payload into the certificate. It does not
> remove it.** Rail 50 one level up: a search cannot find a witness that was destroyed; only *inversion*
> can.

**The complementarity is measured, and it is why no structural certificate works.** Four versions, varying
only the certificate strength:

| version | okA | branch A | descent | exh 5/2gen (10,648) | exh 7/1gen | deep | forced |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v1 | weak | absent | **0** | 60 | 21 | 2 | 6 |
| v2 | weak | weak | **0** | 44 | 11 | 5 | 4 |
| v3 | strong | strong | 1002 | 8 | 15 | 2 | 2 |
| **v4** | strong | weak | 996 | **0** | 8 | 6 | **0** |

v4 is the first model for that law to score 0 on exhaustive *and* 0 on forced firing — and the descent
destroys it. **The failure modes are exactly complementary: a weak certificate passes the descent and
fails exhaustive, a strong one does the reverse.**

**The two untried witness sources, and (b) is one this session already solved once:**

* **(a) the outer pair's own key** — `a1 u` in the U branch, `a2 (a2 v)` in the A branch. The only key the
  law guarantees is *shared* between the A- and B-sides; passing it down is a two-line signature change.
* **(b) ENC-INV: invert the encoding to a closed form instead of searching for it.** Exactly what worked on
  22591's analogous cell (`gen/P2_EXISTENTIAL_DECODER.md` R4: `invsq(s) = J (op s s) (J (op s s) s)`,
  correct on 8/8 targets, reproducing the recorded refutation's witness exactly). **The search framing
  skips this move.**

**Two riders.** Rail 3 was never the problem here — one recursive call `op (a1 v) (a1 u)`, both proper
subterms, `sz u + sz v` decreasing unconditionally and linearly. And a **search decoder cannot be emitted
through `leangen.emit`** (the generated `op` is rule-list-shaped), so `op` must be hand-written; a
`rep<eq>/` package's `termination_by`/`decreasing_by`, `op_free`, `rhs` and `submission` remain reusable.
Lab: `gen/_p2_21864_lab.py`, whole stack in **0.2 s**.

### Read a branch's firing count PER CONSTRUCTION, never in aggregate  (law 12087)

The refinement of the under-fired-branch rung, and it prevents a false alarm as well as a false pass.
12087's `P2` reads **0** on the H3 and deep families and fires **exactly once per hit on every descent
run** (400/400 at levels 0, 2 and 4, both junk pools, 0 fails) — because the descent *is* `P2`'s family:
it is the branch added for "payload read out of the tag `z` when `N3` decoded at the V product".

> **In aggregate `P2` looked dead. It is the busiest branch of the oracle that matters.** Tabulate firings
> by construction family, not by total.


## A FORCING SUITE NEEDS ITS OWN POSITIVE CONTROL — and `_orch_minim.py`'s bulk drop is UNSOUND

Two results from law 10218 that invalidate things several agents were relying on. Read both before
trusting any model.

### 1. A clean forcing run proves nothing unless the census says the rule fired

10218's **first** forced-firing suite reported **3,846 assignments, 0 failures**. It was **vacuous**, and
only the cell census caught it:

```
force-t1-R2   ('R1', 'F', 'F', 'F', 'R5')   768    <- R1 fired, not R2
force-t1-R3   ('R1', ...)                   256    <- R1 fired, not R3
force-t1-R6   ('R1', ...)                    64    <- R1 fired, not R6
```

**The reason is generic to this whole model family, and it is the recipe rather than an anecdote:**

> Rules beyond the first differ from the first only in that a product inside their guard is **decoded**
> rather than free. Build that product free and rule 1's precondition holds too; rule 1 is checked first;
> the "forced" firing never happens. **To force rule k, construct the product inside rule k's own guard as
> an encoding.**

Corrected, the same suite reads **135 law failures in 1,944 assignments**, and Lean confirms
(`gen/_x10218_hole.lean`: the generated `op` plus one instance, `simp (config := {decide := true})`
reduces the goal to `False` in 2 s).

> **The assertion "rule k fired" must appear in the census, or the suite has proved nothing about rule k.**
> Even corrected, 10218's suite never fires R4 or R6 — so it is still incomplete and the model may have
> holes beyond the 135. `gen/_x10218_force.py` is kept deliberately as the counterexample to trusting a
> clean forcing run.

### 2. `_orch_minim.py`'s `status: "ok"` is NOT a soundness certificate

Stronger than the earlier "no `status` key means unvalidated" rail. **A JSON *with* `status: "ok"` is also
not a soundness certificate.** The minimiser's keep-set is "rules that fire under the fuzz battery", and
constructed cells are exactly what the battery misses — so its bulk drop is **unsound**.

10218's 6-rule minimised model passed exhaustive (1,560,896 assignments), 16,880 targeted assignments,
6,113 hand-built risky cells and a one-rule-per-reachable-cell census — and is **false**. The mechanism was
even predicted analytically two passes earlier: `t2 = op z x` can decode by R5/R6, which put `z` at
`a2 (a2 x)`, while R2 — the only root rule for a decoded `t2` — recovers `z` at `a2 (a1 x)`.

**It is a minimisation artifact, not an extraction hole: the full 140-rule set evaluates the failing
instance correctly.** So a correct subset exists.

> **Minimise against the forcing suite, not the battery. Re-force any model that was minimised.**

### 3. "One rule per reachable cell" needs CONSTRUCTED cells, not observed ones

10218 had six rules for six cells and still had a hole, because the census counted only cells a *sampler*
reached. The completeness check is exactly as good as the cell enumeration behind it.


### The conservation law: a MARK is cheap, a READING is expensive  (law 12234, 20 carriers)

Three attempts at one remaining cell, all using a genuine recomputation guard:

| carrier | rules | design | hard battery | what broke |
| --- | --- | --- | --- | --- |
| **K18** (baseline) | 4 | cell open | **16** | H5 only |
| K19 | 6 | `M4` + relaxed reading `R3` | 7,390 | **R3 forges at A** (H3 7,060) |
| K20 | 5 | `M4` emits `E v v` so plain `R` reads it | 32,518 | **M4 eats the payload at C** (H6 21,323) |
| K21 | 6 | `M4` emits `E u v` + narrow reading `R4` gated `tg u != 1` | 52 | **R4 forges at B** (47) |

**All three regressions are READING rules; the mark `M4` is harmless in K19 and K21.**

> **Adding a mark is cheap; adding a reading is expensive.** A mark emitting `E u v` is transparent by
> construction (its `a2` is unchanged, so the outer rule still fires and the root still reads through it).
> A reading **commits to an answer** and is therefore forgeable at every inner position whose `(u,v)` can
> be made to match — H3 and H2 will find it.

So when a cell resists, prefer *not* a new reading: strengthen an existing one to admit the new shape, or
add a **mark that repairs the argument** so an existing reading applies. (12234's untried next candidate is
exactly that: a mark emitting `E <something whose a2 is a2 v> v` rather than K20's `E v v`.)

**And the recomputation principle is confirmed twice over.** K20 and K21 both score **H3 = 0 / 689,976** —
the family that destroys K15 at 100% and K19 at 7,060. **A guard that re-runs a product cannot be forged by
H3, because H3 forges *shape*, not *evaluation*.** K20 also confirms design fact 2 from the other side: it
is the only carrier here that discards an argument (`E v v`) and the only one whose *marks* misfire
destructively.

Useful per-law fact of a kind worth looking for: in 12234's open cell **`y` is provably not a generator** —
if it were, no rule could fire on `op _ y` at all (every rule needs `tg v = 3` or `tg v != 1`), so B and C
would both be free and the plain mark would fire. Necessary but not sufficient there, but that style of
argument is free and prunes cells.


### H3, quantified: ~1,100x the kill power per chain  (law 11081, v15)

On the best 11081 carrier, H3 is the **only** oracle that finds the residual: **96 fails in 160 chains**,
where 177,552 exhaustive chains and 20,736 targeted `forceD` chains both return **0**. Orthogonal to both
constructive oracles.

> **Recommended order for a tag carrier: the targeted killer for the law's own hard product first, then H3,
> and treat the exhaustive sweep as a regression net rather than a test.**

### An impossibility theorem for 11081, and the gap in it worth one attempt

> For `x = y◇((x◇(y◇x))◇(z◇y))` over a **free term algebra with total accessors**, **no rule set whose
> decode returns `a1 (a1 v)`** can be a model.

*Necessity* — without a conjunct pinning `a2 v` to `u`, `D = op(B,C)` decodes, because `z` is constrained
by nothing and can be set to `z := <free> q (op B q)`; witness size 9. *Incompletability* — with it, the
root must fire when `C` decoded, and then `a2 v = a1 (a1 u)` is a **proper subterm of `u`**, so
`a2 (a2 v)` can never be `u`; the key sits at unbounded accessor depth (measured at `y.11121`, depth 5,
canonical paths at 2 and 3, one level deeper per nesting); witnesses of size 59 and 15. Verified across
**six carriers and fifteen rule sets**.

**The gap: the theorem quantifies over decodes that return a PROJECTION.** Law 17286 established that
*some payloads are reconstructions* — its missing payload is not a subterm of the argument at all and must
be rebuilt as `J (a1 P) P`, and dropping that branch cost 30 fails in 143,347 chains. A decode returning a
reconstruction is not covered by "returns `a1 (a1 v)`", and it is exactly the shape that escapes an
unbounded accessor depth: you do not read the key, you rebuild it.

**Also note the mark-ordering trap**, which reproduced 12234's recorded regression exactly: a mark keyed
only on `tg u = 4` is **position-blind**, so when `x` is itself tagged it steals another mark's position
(51,432 fails on `x = F(g0,g0), y = z = g0`). Ordering the marks fixes it. **Mark tests must distinguish
the position, not just the tag.**


### When you change carrier, PORT EVERY CONSTRUCTION from the old oracle  (law 12087)

The seventh model of the session to pass ~10^6 chains and be false, and **the first where the gap was the
agent's rather than the oracle's.**

12087's free-model 16-cell tree had a mode 4 — `z = enc(op(y,x), ., .)`, forcing `N2 = op N1 z` to decode.
It was never ported into the E-carrier lab. So L1 (405,224), L1b, deep (120,000), the level-k descent and
H3 — **560,000+ clean chains** — all missed a cell that is **32% of a targeted draw**. Re-run with the
construction ported: `gen/_w3_12087_ce.py`, **3,000 chains, 3,000 fails**, smallest instance of total size 17.

> **A new carrier inherits the old carrier's adversary. Port every construction, not just the ones that
> were failing.**

**And a reporting bug worth guarding against:** `gen/_w3_12087_cells.py` printed its failure counter
*before* the random loop that generated the hits, so it read "0 fails" where the correct placement reads
1,290 of 4,000. **Print counters after the loop that fills them, and sanity-check that the hit count is
non-zero** — same class as a vacuous oracle, but caused by the harness rather than the construction.

The diagnosis was a **missing branch, not a wrong carrier**: when `N2` decodes, both readings out of
`u = N2` are unavailable, `V` stays free and the root's tag test fails, so nothing fires. The free model
covered that cell with a rule the E-carrier dropped, and the transplant is direct. **Check what the old
rule set covered that the new one does not, cell by cell, before declaring a carrier validated.**


### The conservation law, refined: a mark is cheap only if it keeps `E u v` VERBATIM  (law 12234, K22)

The design space is now closed symmetrically. Four levers, all with **H3 = 0/689,976** — so the
recomputation principle holds throughout, and what fails is always *where the new rule additionally fires*,
never its guard's forgeability by shape:

| variant | lever | hard battery | dies at |
| --- | --- | --- | --- |
| K19 `R3` | new reading | 7,390 | A |
| K21 `R4` | new reading | 52 | B |
| K20 `M4` -> `E v v` | mark, **discards** `u` | 32,518 | C |
| K22 `M5` -> `E (J u (a2 v)) v` | mark, **synthesises** `a1` | 32,484 | C |

> **A mark is cheap only if it keeps `E u v` verbatim.** A mark that synthesises or replaces its first
> component is as expensive as a reading — `a1 (a2 v)` is the slot the root reads, so any such mark firing
> at an inner position wraps it.

Both levers measured expensive is evidence the remaining cell is **not closable by another rule at this
level**, not merely that the next rule has not been found.

### THE VACUITY AUDIT — 54% of a 3M-chain battery tested nothing about half the rules

Run the per-rule firing census **per family**, not per battery. On law 12234's best carrier:

| family | chains | fails | `R2` fired | `M2` fired | |
| --- | --- | --- | --- | --- | --- |
| H1 exhaustive size<=5, 3 gens | 1,179,549 | 0 | **0** | **0** | **VACUOUS** |
| H2 y size<=7 | 422,688 | 0 | 256 | 256 | thin |
| **H3 y a genuine encoding by x** | 459,984 | 0 | **459,984** | **459,984** | the real test |
| H4 z an encoding / z = y | 459,984 | 0 | **0** | **0** | **VACUOUS** |
| H5 chain-value coincidence | 40,000 | 8 | 422 | 716 | finds the fails |
| H6 deep random | 100,000 | 0 | 26 | 33 | very thin |
| H7 descent k=1 | 5,400 | 4 | 4 | 152 | thin |
| H7 descent k>=2 | 5,400 | 0 | **0** | **0** | **VACUOUS** |

**1.65M of 3.05M chains — 54% — never fire the two deep rules at all.** The entire case for them rests on
H3 plus a few hundred scattered firings. **"All families clean" overstates coverage; report which families
fired which rules.**

**And the level-k descent has its own saturation, which nobody had noticed:** for this law it **saturates
at k=1**. Nesting deeper makes `x` a deeper encoding, which makes the **first** rule fire at every product
and leaves the deep rules unreachable — the same mechanism that makes a forcing suite vacuous, now in the
oracle that was supposed to be the strongest. **k = 2..5 add chains and no information.** Check the
descent's own per-rule census before running it deep.


## THE ANCHOR — why marks are cheap and readings are expensive, and what the escape is

Two agents reached this from opposite directions on the same evening. It is the deepest structural result
of the session and it supersedes the mark-vs-reading heuristic by explaining it.

### The mechanism (law 12087, v9/v10)

> **A recomputation guard resists forgery by *shape*, but not forgery by a genuinely-satisfied *relation*.**

12087's `B0` guard is a generic three-product relation (`op (op u x) z = a1 v`, with `x` and `z` read off
`a2 v`), so **any inner pair standing in that relation satisfies it honestly** — it is not a forgery at all,
which is why a *second* certificate changed nothing (945 fails before and after). Meanwhile the same
model's `Dec` survives the identical exposure, and the difference is one conjunct:

* `Dec` tests `tg v = 3` — **only a node this model itself tagged can match it.**
* `B0` tests `tg v = 2` — **any free product matches it.**

> **A rule needs an ANCHOR: a conjunct that only the model can produce.** Without one, its guard is
> satisfiable by honest accident at every inner position, and no amount of extra certification helps.

That is the mechanism behind "a mark is cheap, a reading is expensive": **a mark commits to nothing, so a
spurious firing is harmless; a reading commits to an answer, so a spurious firing is a wrong value.**

**The design consequence is not a better guard — it is to give the unanchored case an anchor.** For 12087:
make the V product tag even when `N2` decodes, so the root only ever needs the anchored `Dec`. Two untried
shapes recorded there: a third constructor marking "product of a decoded left argument", so `N2` carries
its provenance; or having `Dec` at the `N2` position emit a *mark* rather than a bare payload, so `N2` is
never opaque.

### The same conclusion from the impossibility side (law 11081, final)

**Theorem, seven carriers and nineteen rule sets:** no rule set can model
`x = y◇((x◇(y◇x))◇(z◇y))` over a **free term algebra** — *whether its decode returns a projection of `v`,
a term reconstructed from `u`, `a1 v` and `a2 v`, or is certified by recomputation.* Necessity witness of
size 9; incompletability witnesses of size 59 and 15.

Two separations that made the strengthening possible and are worth reusing:

* **Distinguish "the payload is missing" from "the certification is missing".** 17286 needs
  `J (a1 P) P` because its payload is not a subterm of the argument. 11081's payload is *always present*
  (`a1 (a1 v) = x`, confirmed by census in both residual cells) — what is missing is only the
  certification. **A reconstruction decode has nothing to reconstruct there**, which is why that gap in the
  theorem closed rather than opening a route.
* **A certification-by-recomputation branch was built (v17) and scores 0 fails / 198,528 including H3 —
  and is false**, because branch 2 never fires anywhere but the root. Same anchor problem: the
  recomputation stores no key, so it *is* the incompletability half.

**And the escape both agents point at is the same thing.** 11081: *a carrier with a well-formedness
invariant, so `z := <free> q (op B q)` is not in the carrier at all* — the free algebra is what hands the
attacker `z`. 12087: *an anchor is a conjunct only the model can produce.* **These are one idea: restrict
the carrier to terms the model builds, and every guard becomes anchored for free.** The only shipped Austin
constructions that are not term algebras are the infinite models of the `hard2_0027` / ℚ-PWL playbooks.

Note for 11081 specifically: **a quotient is the wrong pointer.** `smallcheck.py 11081 9 1` is 0 failures
over 12,167 assignments, so the law forces **no identity** and every design in `PLAYBOOK_QUOTIENT.md`
starts from one. What the theorem indicts is the *freeness*, not the equality.

### Vacuity, the table — three five-figure clean sweeps, three order-of-magnitude-smaller kills

| model | clean sweep | killed by |
| --- | --- | --- |
| `w123` | 136,000 | 13 / 52,325 (large-junk producer fuzz) |
| lab2 `v11` | 96,792 | 19,140 / 28,800 (`forceD`) |
| lab3 `v17` | 198,528 **including H3** | 2,400 / 9,600 (`forceB2`) |

> **Read the profile table before the fail count. If a branch never fires anywhere but the position it was
> designed for, the sweep has not tested it.**


### Mutual well-founded recursion in Lean: `op` / `opTail` / `find`  (law 17286, compiles at 4,259 B)

The `find` helper the search decoder needs, actually built. `gen/_x17286_mut.lean`, `exit=0`, **4,259 B**
of definitions (that law's free model was 6,107 B at 7 rules; 13764's was 54,402 B), leaving ~15.7 KB for
the proof before `--rename`.

```
termination_by  find (sz u + 2*sz w + sz T + 2, 0) | opTail (…, 1) | op (…, 2)
```

Three mechanics, each of which cost a compile:

* **Phases must be ordered `find 0 < opTail 1 < op 2`.**
* `op -> opTail` keeps the first component, so it needs `exact Prod.Lex.right _ (by omega)`.
* **`Prod.Lex.right` needs the first components SYNTACTICALLY equal.** For `opTail -> find` they agree only
  via a size lemma, and `rw [Cd_sz hc]` leaves a different association, so:
  `have h8 : sz u + sz v = sz u + 2*sz (a1 v) + sz (a2 (a2 v)) + 2 := by omega; rw [h8]; exact Prod.Lex.right _ (by omega)`.
* **Every recursive call must sit under `if h :`** — inside a `∧` condition there is no hypothesis and
  `omega` cannot discharge the decrease.

**And `rhs` needs care with well-founded recursion: `decide` cannot evaluate it.** The concrete refutation
goes through `simp [op.eq_1, opTail.eq_1, find.eq_1, …]` instead. There are now **three** unfolding lemmas
rather than one.

### Build the Lean-exact mirror; do not eyeball the transcription

The mirror caught two bugs in `find` that every Python oracle had passed:

* it carried one branch's check instead of the full certification;
* **it gated its candidate test behind a condition needed only for the RECURSION** — 353 bad, on instances
  as small as `x = (g0*(g0*(g0*g0))), y = (g0*g0), z = g0`. Fix: test the candidate under the weak shape
  condition alone; the stronger one gates only the recursive call.

**A model validated in Python is not the model the Lean file defines.** Mirror it and re-run the battery.

### Self-recursion is not a substitute for `find`  (law 17286 v7)

Measured: **30 bad, and the search branch never fires** — the self-call compares against the *unwrapped*
argument rather than the original, so the validity check is wrong. If you need a search, build the helper.


### A tag rule must fire on `J`-products too, not only on tagged inputs  (law 9663, one character)

Worth 50,560 → 632 L1 failures out of 3,944,312, in one test. Writing the tag rule as `tg v >= 3`
(tagged inputs only) means **the base case never gets tagged**: for `x = y = z = g0` the first product is
`J g0 g0`, untagged, so the container is never built and the root has nothing to read.

> **A tag rule fires on whatever the chain actually produces at that position, which at the base case is a
> plain `J`. Gate it on the reading, not on the tag.**

Free bonus from the same change: it **un-overloads the constructors**, because the recomputation
`op u (a2 v) = v` already distinguishes one tag from the other — `op` only ever produces one of them for a
given `(u, a2 v)`. No extra test needed.

**H3's separation, measured a second time on a different law: 170x.** It fails at 2.1% where `deep` fails
at 0.01% on the same carrier — `deep` would have called it clean. And H3 **named the next rule**: its
dominant failing cell was the container arriving untagged, which one additional reading closed, taking H3
from 255 to 164 and the descent's level 0 from 110 to 57.

**And the vacuous-guard rail fired on a rule that "looked obviously necessary":** a reading certified by
re-running a product gave **identical fail counts on every oracle, with and without it**. Deleted — one
fewer Lean case and ~900 B. Its agent: *"I would not have checked without the rail."*


## THREE LAWS, THREE INDEPENDENT PROOFS, ONE ESCAPE — the next session's single target

By the end of deep session 8, three laws had been closed by *argument* rather than by search, and all three
name the same way out.

| law | what was proved | route |
| --- | --- | --- |
| **22591** | no model on the free term algebra at all: `a = I3(a)` in **seven substitution instances**, no freeness assumed | hand derivation |
| **11081** | no rule set over a free term algebra, **whether its decode returns a projection, a reconstruction, or is certified by recomputation**; seven carriers, nineteen rule sets, witnesses of size 9, 15, 59 | exhaustive design-space search plus proof |
| **12234** | the one open cell is **not closable by another rule on this carrier**; four failure positions (A, B, C, and "fires at D but unreadable"), K19-K23 all at H3 = 0/689,976 | structural proof, below |

**12234's Step 2 is the cleanest of the three and is worth reading as a template.** The mark must fire with
`tg u = 1` (forced: `u = B` is a generator), and K23 shows such a rule exists and is side-effect-free —
177,898 firings, harmless in every family. But a *verbatim* mark at that cell gives `a1 D = B`, `a2 D = C`,
and the root requires `a2 (a1 v) = a2 (a2 v)`; with `a1 v = B` a generator and accessors total, that is
`B = y`. And `y` is provably not a generator in this cell (if it were, no rule could fire on `op _ y`, so
B and C would both be free and the plain mark would have fired), while `B` is. **So `B != y`, and the mark
is unreadable.** The two escapes from that are the two levers, both measured expensive.

### The escape, named three ways

* 22591: a carrier where `I3(x) = x` holds **definitionally**.
* 11081: *"a carrier with a well-formedness invariant, so `z := <free> q (op B q)` is not in the carrier at
  all — a term algebra is what hands the attacker `z`."*
* 12234: *"`B`'s value is junk for this law — the payload is read from C at the root — yet a decode at B can
  collapse it to a generator and destroy D's markability. **A carrier in which B cannot decode**, or in
  which D's mark does not depend on B, removes the cell by construction."*
* and 12087, from the mechanism side: *"a rule needs an **anchor** — a conjunct only the model can
  produce."*

> **These are one construction: restrict the carrier to the terms the model itself builds. Then every guard
> is anchored for free, and the universally quantified variables can no longer be instantiated at the
> adversarial terms that kill every free-carrier model.**
>
> **Build it once. It is the single highest-value piece of work left, and it is worth roughly 25 rows.**

The only shipped Austin constructions that are not term algebras are the infinite models of the
`hard2_0027` (ℕ parity) and ℚ-piecewise-linear playbooks — those are the precedents for a carrier that is
not freely generated.


### The two-horned obstruction, stated exactly  (law 12087, eleven model iterations)

The fourth law closed by argument, and the sharpest statement of *why* the anchor cannot be supplied on a
free carrier:

1. **The root must be a reading.** `op y V = x` for arbitrary `x`; a free product or a tag is larger.
2. **A reading must be anchored or it forges** — and **the only anchor a term model has is a constructor it
   produces itself**, because every other test is satisfiable by an attacker-built term. Measured: the
   unanchored rule's guard is a genuinely-satisfied *relation*, not a shape test, and it forged anyway
   (945/4,000), with a second certificate changing the count by **zero**.
3. So the anchor requires the V product to be tagged: `op N2 N3 = E N2 N3`.
4. **But the product below it is FORCED to decode.** Whenever `z` is itself a genuine encoding with decoder
   `N1` (`z = enc(N1,p,q)`), the law's own instance `(x := p, y := N1, z := q)` demands `op N1 z` decode —
   leaving `N2` an arbitrary element. The certificate that `(N2,N3)` is genuine is `N2 = op (op y x) z`,
   and **`y` occurs in neither `N2` nor `N3`: the pair does not contain the information.** So the mark must
   be shape-only.
5. **A shape-only mark is too broad** and breaks the cells that relied on those pairs being free
   (801/4,000).

> **Mark narrowly ⇒ the root reading is unanchored ⇒ it forges. Mark broadly ⇒ the free cells break.**

Not a formal theorem, and the agent says so: the one direction not ruled out is 11081's — **a carrier with
a well-formedness invariant, so the attacker's term is not in the carrier at all.** Which is exactly the
missing ingredient: *a way to make the opaque product carry its own provenance without introducing a shape
that fires broadly.*

**One correction worth keeping:** "have the decode at the inner position emit a mark" **cannot be taken
literally** — `op` is a function of `(u,v)`, and the root is anchored by the same test as the inner
position, so a mark-emitting decode returns a mark at the root too and the law fails there. Anchoring the
reading and adding a mark to supply the anchor is the faithful reading, and it was measured (414 and 801 on
the two gates).


### A shipped law's architecture transfers to a law that contains it — but its LEMMAS may not  (23354 -> 23357)

**`23354: x = ((y*x)*y)*(x*(x*z))` is the left half of `23357: x = ((y*x)*y)*(x*(y*z))`**, and 23354 shipped
today at 18,728 B. Noticing that produced a **new, fully validated 4-rule model** for 23357
(`gen/rep23357d/`, skeleton 4,552 B) after the inherited 6-rule set turned out to be false: rebuild the
model to match the shipped sibling's shape, replacing a whole generated rule family with **one rule that
certifies by recomputation instead of by shape**.

> **When a law resists, check whether a shipped law is a sub-law of it. Port the architecture.**

**But port the architecture, not the lemmas.** Two of 23354's, checked and refuted for 23357:

* **`ONESIDE`** (no term is both the left and the right argument of a decoding pair) is **false** here — 8
  both-sided terms in a 434-term pool, with the witness recorded.
* **`NOSELF`** (`op u v != v`) is false here too, because this law's size lemma has a
  `sz (op u v) + 3 <= sz u` disjunct that is consistent with it.

**And the reason the sibling is easier is provable, which is the useful part:** 23354's freeness lemma
holds only because `x` repeats in its chain; 23357's law *forces* `op x (op y z)` to decode
(take `x = J (J y' x') y'`, `op y z = J x' (J y' z')`). **A sub-law's freeness lemmas depend on its
repeated variables; the containing law will not have them.** The replacement lever is a recomputation that
is `rfl` at the top of the chain — where the rule recomputes `u` from `v`, and at the top that recomputation
*is* `u`.

**Also: a truncated log is not a validation.** The inherited "6-rule set survives 3 x 20,000 deep tests"
came from a file whose deep tests ran on the **12-rule** baseline and which ends at "minimised 12 -> 6"
because the minimiser was cut off before its own follow-up validation printed. **The 6-rule set had never
been validated by anything**, and it is false. Check what a log's numbers were actually measured on.


### The anchor works, measurably — and the fail count tells you which kind of guard you added  (law 11081, v17-v20)

12087's anchor mechanism, implemented on a second law. The concrete form: **give the decode two results** —
one returning the bare payload (the law's own reading) and one returning a node **carrying its own right
argument** — so that when the inner product fires the anchored variant, the root sees `a2 (a2 v) = u` and
the bare reading fires on *that*.

| version | forceB2 | forceD | exhaustive | total |
| --- | --- | --- | --- | --- |
| v17 (recomputation) | 2,400/9,600 | 0 | 0 | 0 / 198,528 **(vacuous)** |
| v18 (anchor, unguarded) | 400 | **20,736/20,736** | 220 | 21,032 / 432,352 |
| v19 (+ `tg u != 4`) | 400 | **0** | 220 | 296 / 431,792 |
| **v20 (+ Q-disjointness)** | **400** | **0** | **0** | **76 / 431,232** |

**The anchor cut the killer 6x** (2,400 -> 400) and v20 is the best model that law has had, across eight
carriers and twenty-two rule sets.

**And a refinement of the vacuous-guard rail worth having:** v19's single `tg u != 4` conjunct is the
difference between **total collapse (20,736/20,736) and a clean column** — the exact opposite of the earlier
pair where an identical fail count proved a guard certified nothing.

> **The fail count tells you *which* kind of guard you added; the census tells you *why*.** An unchanged
> count means the guard is vacuous; a collapsed count means it was load-bearing. Read both.

**Why it still does not close** — the incompletability half, for the seventh time: when the junk variable's
own slot happens to be the right shape, the inner product fires the *bare* variant, returns unanchored, and
the root is back in the open cell. Merging the two variants collapses them into one rule and the root stops
firing at all. **The two branches are distinguished only by the shape of `a2 v`, and the root and the inner
position are indistinguishable in that respect.**


### `<helper>.induct` is UNUSABLE inside a mutual block — use fuel induction and thread the result  (law 17286)

For a mutual `op` / `opTail` / `find`, Lean's generated `find.induct` is a **three-motive eliminator** and
fails with "Unexpected eliminator type". Two moves make the helper's lemmas go through:

* **Fuel induction on the helper's own decreasing argument** (`sz T`), not the generated induction principle.
* **Thread the result as a variable** — state the lemma as `find u T w P = r -> ...` rather than about
  `find u T w P` directly, so `rw [find.eq_1]` cannot rewrite the *conclusion* out from under you.

Both of that law's helper lemmas, and then `SND`, compiled first try afterwards.

**And the anchor argument is usable constructively, not only as a refutation.** That law's `SND` proves its
reproduce-component by unfolding `op` at the reconstructed pair: `Cd (a1 v)` comes from the branch's **own
guard**, and the other branch fires there and returns the needed component. *A guard that is an anchor is
also a hypothesis you can use.*

**A discipline worth copying**, from an agent that had three thin-pool claims refuted on the same law: it
found a size digest holding with 0 violations — on **168 decoded pairs** — and recorded it as an
**untested conjecture, not a lemma**, with the induction it would need spelled out. Report the pool size
next to the claim and let the reader decide.


### Refuting a `find` helper needs a CONVERSE to its correctness lemma  (law 17286)

`findOK` gives the forward direction — if `find` returns a candidate, it is good. To prove a product
**free**, you need the other direction: that `find` returns the sentinel, i.e. **no candidate anywhere in
the unwrap chain** satisfies the certification. The shape, in the fuel-and-thread pattern that works for
mutual blocks:

```lean
findNone (n) : forall u T w P, sz T <= n ->
  (forall c, <c reachable in T's chain> -> not (cds u c and op c w = P)) -> find u T w P = <sentinel>
```

Every pointwise attempt stalls identically, and the reason is worth knowing: `op r w = P` together with
`cds u r` is a **consistent-looking pair with no size contradiction available**. The refutation has to come
from the chain's structure, not from arithmetic.

> **Budget for it: a search decoder costs a correctness lemma AND its converse.** The converse is the
> larger of the two, and it is invisible until you try to prove a product free.

**A useful narrowing technique from the same round.** Rather than case-splitting a freeness lemma
abstractly, measure which of its guards are actually reachable: over 12,996 `(x,z)` pairs from a 114-term
pool including towers and junk, the outer guard held on **exactly the diagonal `x = z`** (118 pairs), which
collapsed the hypothesis space to two cases; the inner guard was reachable **off**-diagonal (134), so the
leaves are genuinely different. **Census the guard before writing the case tree.**

**And the anchor used constructively, a second time:** in the diagonal case one branch **self-contradicts**
— its two inner conditions both become statements about the same product, and the branch's **own guard**
supplies the tag fact that closes it by `sz_a2_lt`.


### `ZP` — the POSITIVE twin of `Z`, and it makes a cell ~900 B  (law 38316)

```lean
ZP (h1 : a = r) (h2 : b = r) : (if c then a else b) = r
```

`Z` handles the result side of a chain when you must *case* on it; `Y` handles the condition side. **`ZP`
handles the case where you do not need to case at all.** When every branch of the chain returns the same
expression (`a1 v`) and in the cell you are proving `a1 v = x`, **the earlier rules never need refuting**:

```lean
ZP rfl (ZP rfl (… (if_pos ⟨…⟩).trans rfl))
```

walks past them with `rfl`, and **only the intended rule's condition is ever stated**. Its agent's first
attempt refuted branches 1 and 2 by hand and did not even parse; with `ZP` a cell is **~900 B**.

Corollary for the dispatch: use the *size-carrying* digest rather than the bare one — it hands you
`tg v = 2` and the size bound together, and a `≠ J` lemma converts the bound into the disequality the
guard-dichotomy lemma consumes.

### The firing census found SEVEN of twelve rules dead — and a structural-hit table had looked healthy

Over 69,573 chains on law 38316's validated 12-rule model, five rules account for every firing
(64,877 / 1,715 / 1,416 / 6 / 583) and **the other seven fire zero times anywhere**. Dropping them took the
skeleton from **10,411 B to 6,392 B** and the top-rule cases from six to five, and the 5-rule set then
passed every battery again from scratch — including the level-3 descent and a fresh census reading
"NEVER FIRES ANYWHERE: none".

> **A structural-hit table (does this rule's precondition hold here?) is a different measurement from a
> firing census (does this rule actually fire?).** The first looked healthy while seven rules were dead.
> Run the firing census before writing any Lean: each dead rule is ~650 B and a case in every cell.

**And a warning about which single-clause consequences are useful.** A digest derived from the *shared*
precondition can be vacuous: on this law `P3` is literally `tg v = 2`, so the shared-conjunct lemma holds
for free and carries nothing. The cells that depend on which rule fired at an inner product need a full
per-rule `TR`-style digest — a `Y` cascade whose `Q` is the complete condition of each rule — not another
consequence of the common part.


### If changing the guard does not change the firing set, the problem is the POSITION  (law 9663)

A diagnostic that saves a design cycle. Law 9663's last cell wanted a reading `x = a2 v`, tried in **four**
forms — unanchored; anchored on `op (a1 u) (a2 u) = u`; gated on a marker over `(x,u)`; and with the true
certification `op x (op x u) = a2 v`. **All four give identical forcing counts.**

> **A rule's firing set is invariant under its guard ⇒ the problem is where it fires, not what it checks.**
> No guard will fix it; you need a separator between the position it should fire at and the position it
> does.

Here it fires at an inner slot where the correct behaviour is a different rule, and it is **net negative in
every form** (fixes 1, breaks 5). Recorded as a dead end: do not re-try it without a root-vs-inner
separator.

### FIVE laws now need the same thing: a root-vs-inner-position separator

This is the anchored-carrier problem, reached by a fifth independent route:

| law | how it states the need |
| --- | --- |
| 11081 | *"the root and the inner position are indistinguishable in the shape of `a2 v`"* |
| 12087 | *"mark narrowly ⇒ the root reading is unanchored; mark broadly ⇒ the free cells break"* |
| 12234 | *"a carrier in which B cannot decode, or in which D's mark does not depend on B"* |
| 21864 | the certificate's witness was destroyed by the decode being certified |
| **9663** | *"R5 fires at the `Q` slot where the correct behaviour is `TAGE`; the separator is the remaining mathematics, and it is one cell wide"* |

**A term algebra cannot supply it**, because `op` is a function of `(u,v)` alone and the two positions
present the same pair. That is the whole content of "restrict the carrier to the terms the model builds":
a well-formedness invariant *is* a position separator, because only the root's arguments satisfy it.

### And the two rails collided productively, which is how to read them together  (law 9663)

Its agent unified a rule over the container's constructor (H3 255 -> 164 -> 0), which **removed an anchor**;
a junk node then forged a container **by a genuinely satisfied relation** — law 12087's mechanism exactly —
and it patched that with a second anchor. Then a *different* fix (relaxing a tag test from `tg >= 3` to
`tg != 1`, the same rail one level down) took the descent from 122/122/127 to **0** and H3 from 164 to
**0** — and made **both the unification and its patch vacuous** (identical counts everywhere), so both were
deleted.

> **After any win, re-run the vacuity check on everything you added earlier.** A fix upstream can make a
> downstream patch dead, and a dead patch is a Lean case and ~650-900 B.

Final: four rules, unconditional gates, `1468 -> 1197 -> 743 -> 1 -> 0` on the fast harness, every step read
off a cell census. **Descent saturation confirmed on a third law**: profiles per level 7/4/2/4/2, so levels
2 and 4 saturate and levels 0/1/3 are the informative ones.


### The anchored carrier, first measurement — and the first obstacle  (session 8, cut short)

The dedicated agent measured the key quantity before it was stopped:

> **The image of `op` is 4.1% of the term algebra.**

So restricting the carrier to op-built terms is a *real* restriction — it removes 95.9% of the attacker's
term space. But the same measurement produced the obstacle:

> **Law 9663's open-cell witness is itself op-built.**

That is, the one residual cell of the cleanest model on the board survives the restriction. So
"restrict to the image of `op`" is necessary-looking but **not sufficient on its own** — the well-formedness
invariant has to be finer than "is an output of `op`", or the separator has to come from somewhere else
(the position at which a term was built, not merely that it was).

**The question it had just started, and which is the first thing to run next session:** *do rules that were
rejected on the free carrier become admissible on the image?* Every impossibility proved this session
(11081, 12234, 12087, 21864) quantifies over rule sets **on a free term algebra**; each proof's witness
must be re-checked against the image before the theorem is assumed to carry over. Two other laws' agents
were mid-measurement on related questions when the session ended:

* law 8485's forcing suite had just gone non-vacuous (R1/R2/R3 firing 120/120, 120/120, ~114/120, **0
  failures**) with a differential test against the full 83-rule extraction still to run;
* law 9663's agent had found a **genuine collision** in its next variant and was testing whether the
  collision survives on op-produced terms only — the same question from the other side.

Partial results, recorded as partial. The measurements above are real; the conclusions are not drawn.
